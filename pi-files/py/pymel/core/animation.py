from pymel.internal.pmcmds import tangentConstraint as cmd

def ikHandleDisplayScale(*args, **kwargs):
    """
    This action modifies and queries the current display size of ikHandle. The default display scale is 1.0. In query mode,
    return type is based on queried flag.
    
    
    Derived from mel command `maya.cmds.ikHandleDisplayScale`
    """

    pass


def pathAnimation(*args, **kwargs):
    """
    The pathAnimation command constructs the necessary graph nodes and their interconnections for a motion path animation.
    Motion path animation requires a curve and one or more other objects. During the animation, the objects will be moved
    along the 3D curve or the curveOnSurface.There are two ways to specify the moving objects: by explicitly specifying
    their names in the command line, orby making the objects selected (interactively, or through a MEL command).Likewise,
    there are two ways to specify a motion curve: by explicitly specifying the name of the motion curve in the command line
    (i.e. using the -c curve_name option), orby selecting the moving objects first before selecting the motion curve. I.e.
    if the name of the motion curve is not provided in the command line, the curve will be taken to be the last selected
    object in the selection list.When the end time is not specified: only one keyframe will be created either at the current
    time, or at the specified start time.
    
    Flags:
      - bank : b                       (bool)          [query]
          If on, enable alignment of the up axis of the moving object(s) to the curvature of the path geometry.Default is
          false.When queried, this flag returns a boolean.
    
      - bankScale : bs                 (float)         [query]
          This flag specifies a factor to scale the amount of bank angle.Default is 1.0When queried, this flag returns a float.
    
      - bankThreshold : bt             (float)         [query]
          This flag specifies the limit of the bank angle.Default is 90 degreesWhen queried, this flag returns an angle.
    
      - curve : c                      (unicode)       [query]
          This flag specifies the name of the curve for the path.Default is NONEWhen queried, this flag returns a string.
    
      - endTimeU : etu                 (time)          [query]
          This flag specifies the ending time of the animation for the u parameter.Default is NONE.When queried, this flag returns
          a time.
    
      - endU : eu                      (float)         [query]
          This flag specifies the ending value of the u parameterization for the animation.Default is the end parameterization
          value of the curve.When queried, this flag returns a linear.
    
      - follow : f                     (bool)          [query]
          If on, enable alignment of the front axis of the moving object(s).Default is false.When queried, this flag returns a
          boolean.
    
      - followAxis : fa                (unicode)       [query]
          This flag specifies which object local axis to be aligned to the tangent of the path curve.Default is yWhen queried,
          this flag returns a string.
    
      - fractionMode : fm              (bool)          [query]
          If on, evaluation on the path is based on the fraction of length of the path curve.Default is false.When queried, this
          flag returns a boolean.
    
      - inverseFront : inverseFront    (bool)          [query]
          This flag specifies whether or not to align the front axis of the moving object(s) to the opposite direction of the
          tangent vector of the path geometry.Default is false.When queried, this flag returns a boolean.
    
      - inverseUp : iu                 (bool)          [query]
          This flag specifies whether or not to align the up axis of the moving object(s) to the opposite direction of the normal
          vector of the path geometry.Default is false.When queried, this flag returns a boolean.
    
      - name : n                       (unicode)       [query]
          This flag specifies the name for the new motion path node. (instead of the default name)When queried, this flag returns
          a string.
    
      - startTimeU : stu               (time)          [query]
          This flag specifies the starting time of the animation for the u parameter.Default is the the current time.When queried,
          this flag returns a time.
    
      - startU : su                    (float)         [query]
          This flag specifies the starting value of the u parameterization for the animation.Default is the start parameterization
          value of the curve.When queried, this flag returns a linear.
    
      - upAxis : ua                    (unicode)       [query]
          This flag specifies which object local axis to be aligned a computed up direction.Default is zWhen queried, this flag
          returns a string.
    
      - useNormal : un                 (bool)          [create,query,edit]
          This flag is now obsolete. Use -wut/worldUpType instead.
    
      - worldUpObject : wuo            (PyNode)        [create,query,edit]
          Set the DAG object to use for worldUpType objectand objectrotation. See -wut/worldUpType for greater detail. The default
          value is no up object, which is interpreted as world space.
    
      - worldUpType : wut              (unicode)       [create,query,edit]
          Set the type of the world up vector computation. The worldUpType can have one of 5 values: scene, object,
          objectrotation, vector, or normal. If the value is scene, the upVector is aligned with the up axis of the scene and
          worldUpVector and worldUpObject are ignored. If the value is object, the upVector is aimed as closely as possible to the
          origin of the space of the worldUpObject and the worldUpVector is ignored. If the value is objectrotationthen the
          worldUpVector is interpreted as being in the coordinate space of the worldUpObject, transformed into world space and the
          upVector is aligned as closely as possible to the result. If the value is vector, the upVector is aligned with
          worldUpVector as closely as possible and worldUpObject is ignored. Finally, if the value is normalthe upVector is
          aligned to the path geometry. The default worldUpType is vector.
    
      - worldUpVector : wu             (float, float, float) [create,query,edit]
          Set world up vector.  This is the vector in world coordinates that up vector should align with. See -wut/worldUpType for
          greater detail. If not given at creation time, the default value of (0.0, 1.0, 0.0) is used.                  Flag can
          have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.pathAnimation`
    """

    pass


def poleVectorConstraint(*args, **kwargs):
    """
    Constrains the poleVector of an ikRPsolve handle to point at a target object or at the average position of a number of
    targets. An poleVectorConstraint takes as input one or more targetDAG transform nodes at which to aim pole vector for an
    IK handle using the rotate plane solver.  The pole vector is adjust such that the in weighted average of the world space
    position target objects lies is the rotate planeof the handle.
    
    Maya Bug Fix:
      - when queried, angle offsets would be returned in radians, not current angle unit
    
    Modifications:
      - added new syntax for querying the weight of a target object, by passing the constraint first::
    
            aimConstraint( 'pCube1_aimConstraint1', q=1, weight ='pSphere1' )
            aimConstraint( 'pCube1_aimConstraint1', q=1, weight =['pSphere1', 'pCylinder1'] )
            aimConstraint( 'pCube1_aimConstraint1', q=1, weight =[] )
    
    Flags:
      - layer : l                      (unicode)       [create,edit]
          Specify the name of the animation layer where the constraint should be added.
    
      - name : n                       (unicode)       [create,query,edit]
          Sets the name of the constraint node to the specified name.  Default name is constrainedObjectName_constraintType
    
      - remove : rm                    (bool)          [edit]
          removes the listed target(s) from the constraint.
    
      - targetList : tl                (bool)          [query]
          Return the list of target objects.
    
      - weight : w                     (float)         [create,query,edit]
          Sets the weight value for the specified target(s). If not given at creation time, the default value of 1.0 is used.
    
      - weightAliasList : wal          (bool)          [query]
          Returns the names of the attributes that control the weight of the target objects. Aliases are returned in the same
          order as the targets are returned by the targetList flag                  Flag can have multiple arguments, passed
          either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.poleVectorConstraint`
    """

    pass


def dopeSheetEditor(*args, **kwargs):
    """
    Edit a characteristic of a dope sheet editor
    
    Flags:
      - autoFit : af                   (unicode)       [query,edit]
          on | off | tgl Auto fit-to-view.
    
      - control : ctl                  (bool)          [query]
          Query only. Returns the top level control for this editor. Usually used for getting a parent to attach popup menus.
          Caution: It is possible for an editor to exist without a control. The query will return NONEif no control is present.
    
      - defineTemplate : dt            (unicode)       [create]
          Puts the command in a mode where any other flags and args are parsed and added to the command template specified in the
          argument. They will be used as default arguments in any subsequent invocations of the command when templateName is set
          as the current template.
    
      - displayActiveKeyTangents : dat (unicode)       [edit]
          on | off | tgl Display active key tangents in the editor.
    
      - displayActiveKeys : dak        (unicode)       [edit]
          on | off | tgl Display active keys in the editor.
    
      - displayInfinities : di         (unicode)       [edit]
          on | off | tgl Display infinities in the editor.
    
      - displayKeys : dk               (unicode)       [edit]
          on | off | tgl Display keyframes in the editor.
    
      - displayTangents : dtn          (unicode)       [edit]
          on | off | tgl Display tangents in the editor.
    
      - displayValues : dv             (unicode)       [edit]
          on | off | tgl Display active keys and tangents values in the editor.
    
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
    
      - hierarchyBelow : hb            (bool)          [query,edit]
          display animation for objects hierarchically
    
      - highlightConnection : hlc      (unicode)       [create,query,edit]
          Specifies the name of a selectionConnection object that the editor will synchronize with its highlight list. Not all
          editors have a highlight list. For those that do, it is a secondary selection list.
    
      - lockMainConnection : lck       (bool)          [create,edit]
          Locks the current list of objects within the mainConnection, so that only those objects are displayed within the editor.
          Further changes to the original mainConnection are ignored.
    
      - lookAt : la                    (unicode)       [edit]
          all | selected | currentTime FitView helpers.
    
      - mainListConnection : mlc       (unicode)       [create,query,edit]
          Specifies the name of a selectionConnection object that the editor will use as its source of content. The editor will
          only display items contained in the selectionConnection object.
    
      - outliner : o                   (unicode)       [query,edit]
          the name of the outliner which is associated with the dope sheet
    
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
    
      - selectionWindow : sel          (float, float, float, float) [query,edit]
          The selection area specified as left, right, bottom, top respectively.
    
      - showScene : sc                 (bool)          [query,edit]
          display the scene summary object
    
      - showSummary : ss               (bool)          [query,edit]
          display the summary object
    
      - showTicks : stk                (bool)          [query,edit]
          display per animation tick divider in channel
    
      - snapTime : st                  (unicode)       [query,edit]
          none | integer | keyframe Keyframe move snap in time.
    
      - snapValue : sv                 (unicode)       [query,edit]
          none | integer | keyframe Keyframe move snap in values.
    
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
          Forces the command to use a command template other than the current one.                  Flag can have multiple
          arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.dopeSheetEditor`
    """

    pass


def clip(*args, **kwargs):
    """
    This command is used to create, edit and query character clips.
    
    Flags:
      - absolute : abs                 (bool)          [create]
          This flag is now deprecated.  Use aa/allAbsolute, ar/allRelative, ra/rotationsAbsolute, or da/defaultAbsolute instead.
          This flag controls whether the clip follows its keyframe values or whether they are offset by a value to maintain a
          smooth path. Default is true.
    
      - absoluteRotations : abr        (bool)          [create]
          This flag is now deprecated.  Use aa/allAbsolute, ar/allRelative, ra/rotationsAbsolute, or da/defaultAbsolute instead.
          If true, this overrides the -absolute flag so that rotation channels are always calculated with absolute offsets. This
          allows you to have absolute offsets on rotations and relative offsets on all other channels.
    
      - active : a                     (unicode)       [query,edit]
          Query or edit the active clip. This flag is not valid in create mode. Making a clip active causes its animCurves to be
          hooked directly to the character attributes in addition to being attached to the clip library node. This makes it easier
          to access the animCurves if you want to edit, delete or add additional animCruves to the clip.
    
      - addTrack : at                  (bool)          []
          This flag is now obsolete. Use the insertTrack flag on the clipSchedule command instead.
    
      - allAbsolute : aa               (bool)          [create]
          Set all channels to be calculated with absolute offsets.  This flag cannot be used in conjunction with the
          ar/allRelative, ra/rotationsAbsolute or da/defaultAbsolute flags.
    
      - allClips : ac                  (bool)          [query]
          This flag is used to query all the clips in the scene. Nodes of type animClipthat are storing poses, are not returned by
          this command.
    
      - allRelative : ar               (bool)          [create]
          Set all channels to be calculated with relative offsets.  This flag cannot be used in conjunction with the
          aa/allAbsolute, ra/rotationsAbsolute or da/defaultAbsolute flags.
    
      - allSourceClips : asc           (bool)          [query]
          This flag is used to query all the source clips in the scene. Nodes of type animClipthat are storing poses or clip
          instances, are not returned by this command.
    
      - animCurveRange : acr           (bool)          [create]
          This flag can be used at the time you create the clip instead of the startTime and endTime flags. It specifies that you
          want the range of the clip to span the range of keys in the clips associated animCurves.
    
      - character : ch                 (bool)          [query]
          This is a query only flag which operates on the specified clip. It returns the names of any characters that a clip is
          associated with.
    
      - constraint : cn                (bool)          [create]
          This creates a clip out of any constraints on the character. The constraint will be moved off of the character and into
          the clip, so that it is only active for the duration of the clip, and its value can be scaled/offset/cycled according to
          the clip attributes.
    
      - copy : c                       (bool)          [create,query]
          This flag is used to copy a clip or clips to the clipboard. It should be used in conjunction with the name flag to copy
          the named clips on the specified character and its subcharacters. In query mode, this flag allows you to query what, if
          anything, has been copied into the clip clipboard.
    
      - defaultAbsolute : da           (bool)          [create]
          Sets all top-level channels except rotations in the clip to relative, and the remaining channels to absolute. This is
          the default during clip creation if no offset flag is specified.  This flag cannot be used in conjunction with the
          aa/allAbsolute, ar/allRelative, or ra/rotationsAbsolute flags.
    
      - duplicate : d                  (bool)          [query]
          Duplicate the clip specified by the name flag. The start time of the new clip should be specified with the startTime
          flag.
    
      - endTime : end                  (time)          [create,query,edit]
          Specify the clip end
    
      - expression : ex                (bool)          [create]
          This creates a clip out of any expressions on the character. The expression will be moved off of the character and into
          the clip, so that it is only active for the duration of the clip, and its value can be scaled/offset/cycled according to
          the clip attributes.
    
      - ignoreSubcharacters : ignoreSubcharacters (bool)          [create]
          During clip creation, duplication and isolation, subcharacters are included by default. If you want to create a clip on
          the top level character only, or you want to duplicate the clip on the top level character without including
          subCharacters, use the ignoreSubcharacters flag.
    
      - isolate : i                    (bool)          [create]
          This flag should be used in conjunction with the name flag to specify that a clip or clips should be copied to a new
          clip library. The most common use of this flag is for export, when you want to only export certain clips from the
          character, without exporting all of the clips.
    
      - leaveOriginal : lo             (bool)          [create]
          This flag is used when creating a clip to specify that the animation curves should be copied to the clip library, and
          left on the character.
    
      - mapMethod : mm                 (unicode)       [create]
          This is is valid with the paste and pasteInstance flags only. It specifies how the mapping should be done. Valid options
          are: byNodeName, byAttrName, byCharacterMap, byAttrOrder, byMapOrAttrNameand byMapOrNodeName. byAttrNameis the default.
          The flags mean the following: byAttrOrdermaps using the order that the character stores the attributes internally,
          byAttrNameuses the attribute name to find a correspondence, byNodeNameuses the node name \*and\* the attribute name to
          find a correspondence, byCharacterMapuses the existing characterMap node to do the mapping. byMapOrAttrNameuses a
          character map if one exists, otherwise uses the attribute name. byMapOrNodeNameuses a character map if one exists,
          otherwise uses the attribute name.
    
      - name : n                       (unicode)       [create,query]
          In create mode, specify the clip name. In query mode, return a list of all the clips. In duplicate mode, specify the
          clip to be duplicated. In copy mode, specify the clip to be copied. This flag is multi-use, but multiple use is only
          supported with the copy flag. For use during create and with all other flags, only the first instance of the name flag
          will be utilized. In query mode, this flag can accept a value.
    
      - newName : nn                   (unicode)       [create]
          Rename a clip. Must be used in conjunction with the clip name flag, which is used to specify the clip to be renamed.
    
      - paste : p                      (bool)          [create]
          This flag is used to paste a clip or clips from the clipboard to a character. Clips are added to the clipboard using the
          c/copy flag.
    
      - pasteInstance : pi             (bool)          [create]
          This flag is used to paste an instance of a clip or clips from the clipboard to a character. Unlike the p/paste flag,
          which duplicates the animCurves from the original source clip, the pi/pasteInstance flag shares the animCurves from the
          source clip.
    
      - remove : rm                    (bool)          [query]
          Remove the clip specified by the name flag. The clip will be permanently removed from the library and deleted from any
          times where it has been scheduled.
    
      - removeTrack : rt               (bool)          [create]
          This flag is now obsolete. Use removeTrack flag on the clipSchedule command instead.
    
      - rotationOffset : rof           (float, float, float) [create,query]
          Return the channel offsets used to modify the clip's rotation.
    
      - rotationsAbsolute : ra         (bool)          [create]
          Set all channels except rotations to be calculated with relative offsets.  Rotation channels will be calculated with
          absolute offsets.  This flag cannot be used in conjunction with the aa/allAbsolute, ar/allRelative or da/defaultAbsolute
          flags.
    
      - scheduleClip : sc              (bool)          [create]
          This flag is used when creating a clip to specify whether or not the clip should immediately be scheduled at the current
          time. If the clip is not scheduled, the clip will be placed in the library for future use, but will not be placed on the
          timeline. This flag is for use only when creating a new clip or duplicating an existing. The default is true.
    
      - sourceClipName : scn           (bool)          [query]
          This flag is for query only. It returns the name of the source clip that controls an instanced clip.
    
      - split : sp                     (time)          [create,edit]
          Split an existing clip into two clips. The split occurs around the specified time.
    
      - startTime : s                  (time)          [create,query,edit]
          Specify the clip start
    
      - translationOffset : tof        (float, float, float) [create,query]
          Return the channel offsets used to modify the clip's translation.
    
      - useChannel : uc                (unicode)       [create]
          Specify which channels should be acted on. This flag is valid only in conjunction with clip creation, and the isolate
          flag. The specified channels must be members of the character.                               Flag can have multiple
          arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.clip`
    """

    pass


def timeEditorClipLayer(*args, **kwargs):
    """
    Time Editor clip layers commands
    
    Flags:
      - addAttribute : aa              (unicode)       [edit]
          Add given plug to a layer with a supplied layerId.
    
      - addLayer : al                  (unicode)       [edit]
          Add a new layer with a given name.
    
      - addObject : ao                 (unicode)       [edit]
          Add given object with all its attributes in the clip to a layer with a supplied layerId.
    
      - allLayers : all                (bool)          [query]
          Return all layers given clip ID.
    
      - attribute : a                  (unicode)       [edit]
          The attribute path to key.
    
      - attributeKeyable : ak          (unicode)       [query]
          Return whether specified attribute is keyable.
    
      - clipId : cid                   (int)           [edit]
          ID of the clip this layer command operates on. In query mode, this flag can accept a value.
    
      - index : idx                    (int)           [edit]
          Layer index, used when adding new layer at specific location in the stack.
    
      - keySiblings : ks               (bool)          [edit]
          If set to true, additional attributes might be keyed while keying to achieve desired result.
    
      - layerId : lid                  (int)           [edit]
          Layer ID used in conjunction with other edit flags. In query mode, this flag can accept a value.
    
      - layerName : ln                 (unicode)       [query,edit]
          Edit layer name. In query mode, return the layer name given its layer ID and clip ID.
    
      - mode : m                       (int)           [edit]
          To control the playback speed of the clip by animation curve: 0 : additive1 : additive override2 : override3 : override
          passthrough
    
      - mute : mu                      (bool)          [edit]
          Mute/unmute a layer given its layer ID and clip ID.
    
      - name : n                       (bool)          [query]
          Query the attribute name of a layer given its layer ID and clip ID.
    
      - path : pt                      (unicode)       [edit]
          Full path of a layer or a clip to operates on. For example: composition1|track1|clip1|layer1;
          composition1|track1|group|track1|clip1. In query mode, this flag can accept a value.
    
      - removeAttribute : ra           (unicode)       [edit]
          Remove given plug from a layer with a supplied layerId.
    
      - removeLayer : rl               (bool)          [edit]
          Remove layer with an ID.
    
      - removeObject : ro              (unicode)       [edit]
          Remove given object with all its attributes in the clip to a layer with a supplied layerId.
    
      - resetSolo : rs                 (bool)          [edit]
          Unsolo all soloed layers in a given clip ID.
    
      - setKeyframe : k                (bool)          [edit]
          Set keyframe on specified attributes on specified layer of a clip. Use -clipId to indicate the specified clip. Use
          -layerId to indicate the specified layer of the clip. Use -attribute to indicate the specified attributes (if no
          attribute flag is used, all attribute will be keyed). Use -zeroKeying to indicate that zero offset from original
          animation should be keyed.
    
      - solo : sl                      (bool)          [edit]
          Solo/unsolo a layer given its layers ID and clip ID.
    
      - zeroKeying : zk                (bool)          [edit]
          Indicate if the key to set should be zero offset from original animation.                                  Flag can have
          multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.timeEditorClipLayer`
    """

    pass


def character(*args, **kwargs):
    """
    This command is used to manage the membership of a character.  Characters are a type of set that gathers together the
    attributes of a node or nodes that a user wishes to animate as a single entity.
    
    Flags:
      - addElement : add               (PyNode)        [edit]
          Adds the list of items to the given character.  If some of the items cannot be added to the character because they are
          in another character, the command will fail.  When another character is passed to to -addElement, is is added as a sub
          character.  When a node is passed in, it is expanded into its keyable attributes, which are then added to the character.
    
      - addOffsetObject : aoo          (unicode)       [query,edit]
          Indicates that the selected character member objects should be used when calculating and applying offsets. The flag
          argument is used to specify the character.
    
      - characterPlug : cp             (bool)          [query]
          Returns the plug on the character that corresponds to the specified character member.
    
      - clear : cl                     (PyNode)        [edit]
          An operation which removes all items from the given character.
    
      - empty : em                     (bool)          [create]
          Indicates that the character to be created should be empty. (i.e. it ignores any arguments identifying objects to be
          added to the character.
    
      - excludeDynamic : ed            (bool)          [create]
          When creating the character, exclude dynamic attributes.
    
      - excludeRotate : er             (bool)          [create]
          When creating the character, exclude rotate attributes from transform-type nodes.
    
      - excludeScale : es              (bool)          [create]
          When creating the character, exclude scale attributes from transform-type nodes.
    
      - excludeTranslate : et          (bool)          [create]
          When creating the character, exclude translate attributes from transform-type nodes. For example, if your character
          contains joints only, perhaps you only want to include rotations in the character.
    
      - excludeVisibility : ev         (bool)          [create]
          When creating the character, exclude visibility attribute from transform-type nodes.
    
      - flatten : fl                   (PyNode)        [edit]
          An operation that flattens the structure of the given character. That is, any characters contained by the given
          character will be replaced by its members so that the character no longer contains other characters but contains the
          other characters' members.
    
      - forceElement : fe              (PyNode)        [edit]
          For use in edit mode only. Forces addition of the items to the character. If the items are in another character which is
          in the character partition, the items will be removed from the other character in order to keep the characters in the
          character partition mutually exclusive with respect to membership.
    
      - include : include              (PyNode)        [edit]
          Adds the list of items to the given character.  If some of the items cannot be added to the character, a warning will be
          issued. This is a less strict version of the -add/addElement operation.
    
      - intersection : int             (PyNode)        [query]
          An operation that returns a list of items which are members of all the character in the list.  In general, characters
          should be mutually exclusive.
    
      - isIntersecting : ii            (PyNode)        [query]
          An operation which tests whether or not the characters in the list have common members.  In general, characters should
          be mutually exclusive, so this should always return false.
    
      - isMember : im                  (PyNode)        [query]
          An operation which tests whether or not all the given items are members of the given character.
    
      - library : lib                  (bool)          [query]
          Returns the clip library associated with this character, if there is one. A clip library will only exist if you have
          created clips on your character.
    
      - memberIndex : mi               (int)           [query]
          Returns the memberIndex of the specified character member if used after the query flag. Or if used before the query
          flag, returns the member that corresponds to the specified index.
    
      - name : n                       (unicode)       [create]
          Assigns string as the name for a new character. Valid for operations that create a new character.
    
      - noWarnings : nw                (bool)          [create]
          Indicates that warning messages should not be reported such as when trying to add an invalid item to a character. (used
          by UI)
    
      - nodesOnly : no                 (bool)          [query]
          This flag modifies the results of character membership queries. When listing the attributes (e.g. sphere1.tx) contained
          in the character, list only the nodes.  Each node will only be listed once, even if more than one attribute or component
          of the node exists in the character.
    
      - offsetNode : ofs               (bool)          [query]
          Returns the name of the characterOffset node used to add offsets to the root of the character.
    
      - remove : rm                    (PyNode)        [edit]
          Removes the list of items from the given character.
    
      - removeOffsetObject : roo       (unicode)       [edit]
          Indicates that the selected character offset objects should be removed as offsets. The flag argument is used to specify
          the character.
    
      - root : rt                      (unicode)       [create]
          Specifies the transform node which will act as the root of the character being created. This creates a characterOffset
          node in addition to the character node, which can be used to add offsets to the character to change the direction of the
          character's animtion without inserting additional nodes in its hierarchy.
    
      - scheduler : sc                 (bool)          [query]
          Returns the scheduler associated with this character, if there is one. A scheduler will only exist if you have created
          clips on your character.
    
      - split : sp                     (PyNode)        [create]
          Produces a new set with the list of items and removes each item in the list of items from the given set.
    
      - subtract : sub                 (PyNode)        [query]
          An operation between two characters which returns the members of the first character that are not in the second
          character. In general, characters should be mutually exclusive.
    
      - text : t                       (unicode)       [create,query,edit]
          Defines an annotation string to be stored with the character.
    
      - union : un                     (PyNode)        [query]
          An operation that returns a list of all the members of all characters listed.
    
      - userAlias : ua                 (PyNode)        [query]
          Returns the user defined alias for the given attribute on the character or and empty string if there is not one.
          Characters automatically alias the attributes where character animation data is stored.  A user alias will exist when
          the automatic aliases are overridden using the aliasAttr command.                  Flag can have multiple arguments,
          passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.character`
    """

    pass


def deltaMush(*args, **kwargs):
    """
    This command is used to create, edit and query deltaMush nodes.
    
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
    
      - deformerTools : dt             (bool)          [query]
          Returns the name of the deformer tool objects (if any) as string string ...
    
      - envelope : en                  (float)         [create,query,edit]
          Envelope of the delta mush node. The envelope determines the percent of deformation. Value is clamped between to [0, 1]
          range. Defaults to 1.
    
      - exclusive : ex                 (unicode)       [create,query]
          Puts the deformation set in a deform partition.
    
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
    
      - name : n                       (unicode)       [create]
          Used to specify the name of the node being created.
    
      - parallel : par                 (bool)          [create,edit]
          Inserts the new deformer in a parallel chain to any existing deformers in the history of the object. A blendShape is
          inserted to blend the parallel results together. Works in create mode (and edit mode if the deformer has no geometry
          added yet).
    
      - pinBorderVertices : pbv        (bool)          [create,query,edit]
          If enabled, vertices on mesh borders will be pinned to their current position during smoothing. Defaults to true.
    
      - prune : pr                     (bool)          [edit]
          Removes any points not being deformed by the deformer in its current configuration from the deformer set.
    
      - remove : rm                    (bool)          [edit]
          Specifies that objects listed after the -g flag should be removed from this deformer.
    
      - smoothingIterations : si       (int)           [create,query,edit]
          Number of smoothing iterations performed by the delta mush node. Defaults to 10.
    
      - smoothingStep : ss             (float)         [create,query,edit]
          Step amount used per smoothing iteration. Value is clamped between [0, 1] range. A higher value may lead to
          instabilities but converges faster compared to a lower value. Defaults to 0.5.
    
      - split : sp                     (bool)          [create,edit]
          Branches off a new chain in the dependency graph instead of inserting/appending the deformer into/onto an existing
          chain. Works in create mode (and edit mode if the deformer has no geometry added yet).                  Flag can have
          multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.deltaMush`
    """

    pass


def recordDevice(*args, **kwargs):
    """
    Starts and stops server side device recording. The data is recorded at the device rate. Once recorded, the data may be
    brought into Maya with the applyTake command. See also: enableDevice, applyTake, readTake, writeTake In query mode,
    return type is based on queried flag.
    
    Flags:
      - cleanup : c                    (bool)          [create]
          Removes the recorded data from the device.
    
      - data : da                      (bool)          [query]
          Specifies if the device has recorded data. If the device is recording at the time of query, the flag will return false.
          Q: When queried, this flag returns an int.
    
      - device : d                     (unicode)       [create]
          Specifies which device(s) to start record recording. The listed device(s) will start recording regardless of their
          record enable state. C: The default is to start recording all devices that are record enabled.
    
      - duration : dr                  (int)           [create,query]
          Duration (in seconds) of the recording. When the duration expires, the device will still be in a recording state and
          must be told to stop recording. C: The default is 60. Q: When queried, this flag returns an int.
    
      - playback : p                   (bool)          [create,query]
          If any attribute is connected to an animation curve, the animation curve will play back while recording the device(s)
          including any animation curves attached to attributes being recorded. C: The default is false. Q: When queried, this
          flag returns an int.
    
      - state : st                     (bool)          [create,query]
          Start or stop device recording. C: The default is true. Q: When queried, this flag returns an int.
    
      - wait : w                       (bool)          [create]
          If -p/playback specified, wait until playback completion before returning control to the user. This flag is ignored if
          -p is not used.                  Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.recordDevice`
    """

    pass


def timeEditor(*args, **kwargs):
    """
    General Time Editor commands
    
    Flags:
      - clipId : id                    (int)           [create]
          ID of the clip to be edited.
    
      - commonParentTrack : cpt        (bool)          [create]
          Locate the common parent track node and track index of the given clip IDs. Requires a list of clip IDs to be specified
          using the clipId flag. The format of the returned string is track_node:track_index. If the clips specified are on the
          same track node but in different track indexes, only the track node will be returned.
    
      - composition : cp               (unicode)       [create]
          A flag to use in conjunction with -dca/drivingClipsForObjto indicate the name of composition to use. By default if this
          flag is not provided, current active composition will be used.
    
      - drivingClipsForAttr : dca      (unicode)       [create]
          Return a list of clips driving the specified attribute(s). If the composition is not specified, current active
          composition will be used.
    
      - drivingClipsForObj : dco       (unicode, int)  [create]
          Return a list of clips driving the specified object(s) with an integer value indicating the matching mode. If no object
          is specified explicitly, the selected object(s) will be used. Objects that cannot be driven by clips are ignored. If the
          composition is not specified, current active composition will be used. Default match mode is 0. 0: Include only the clip
          that has an exact match1: Include any clip that contains all of the specified objects2: Include any clip that contains
          any of the specified objects3: Include all clips that do not include any of the specified objects
    
      - includeParent : ip             (bool)          [create]
          A toggle flag to use in conjunction with -dca/drivingClipsForObj. When toggled, parent clip is included in selection
          (the entire hierarchy will be selected).
    
      - mute : m                       (bool)          [create,query]
          Mute/unmute Time Editor.
    
      - selectedClips : sc             (unicode)       [create]
          Return a list of clip IDs of currently selected Time Editor clips. Arguments may be used to filter the returning result.
          An empty string will return clip IDs for all clip types: roster container group Flag can have multiple arguments, passed
          either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.timeEditor`
    """

    pass


def setKeyframe(*args, **kwargs):
    """
    This command creates keyframes for the specified objects, or the active objects if none are specified on the command
    line. The default time for the new keyframes is the current time. Override this behavior with the -tflag on the command
    line. The default value for the keyframe is the current value of the attribute for which a keyframe is set.  Override
    this behavior with the -vflag on the command line. When setting keyframes on animation curves that do not have timeas an
    input attribute (ie, they are unitless animation curves), use -f/-floatto specify the unitless value at which to set a
    keyframe. The -time and -float flags may be combined in one command. This command sets up Dependency Graph relationships
    for proper evaluation of a given attribute at a given time.
    
    Flags:
      - animLayer : al                 (unicode)       [create]
          Specifies that the new key should be placed in the specified animation layer. Note that if the objects being keyframed
          are not already part of the layer, this flag will be ignored.
    
      - animated : an                  (bool)          [create]
          Add the keyframe only to the attribute(s) that have already a keyframe on. Default: false
    
      - attribute : at                 (unicode)       [create]
          Attribute name to set keyframes on.
    
      - breakdown : bd                 (bool)          [create,query,edit]
          Sets the breakdown state for the key.  Default is false
    
      - clip : c                       (unicode)       [create]
          Specifies that the new key should be placed in the specified clip. Note that if the objects being keyframed are not
          already part of the clip, this flag will be ignored.
    
      - controlPoints : cp             (bool)          [create]
          Explicitly specify whether or not to include the control points of a shape (see -sflag) in the list of attributes.
          Default: false.
    
      - dirtyDG : dd                   (bool)          [create]
          Allow dirty messages to be sent out when a keyframe is set.
    
      - float : f                      (float)         [create]
          Float time at which to set a keyframe on float-based animation curves.
    
      - hierarchy : hi                 (unicode)       [create]
          Controls the objects this command acts on, relative to the specified (or active) target objects. Valid values are
          above,below,both,and none.Default is hierarchy -query
    
      - identity : id                  (bool)          [create]
          Sets an identity key on an animation layer.  An identity key is one that nullifies the effect of the anim layer.  This
          flag has effect only when the attribute being keyed is being driven by animation layers.
    
      - inTangentType : itt            (unicode)       [create]
          The in tangent type for keyframes set by this command. Valid values are: auto, clamped, fast, flat, linear, plateau,
          slow, spline, and stepnextDefault is keyTangent -q -g -inTangentType
    
      - insert : i                     (bool)          [create]
          Insert keys at the given time(s) and preserve the shape of the animation curve(s). Note: the tangent type on inserted
          keys will be fixed so that the curve shape can be preserved.
    
      - insertBlend : ib               (bool)          [create]
          If true, a pairBlend node will be inserted for channels that have nodes other than animCurves driving them, so that such
          channels can have blended animation. If false, these channels will not have keys inserted. If the flag is not specified,
          the blend will be inserted based on the global preference for blending animation.
    
      - minimizeRotation : mr          (bool)          [create]
          For rotations, ensures that the key that is set is a minimum distance away from the previous key.  Default is false
    
      - noResolve : nr                 (bool)          [create]
          When used with the -value flag, causes the specified value to be set directly onto the animation curve, without
          attempting to resolve the value across animation layers.
    
      - outTangentType : ott           (unicode)       [create]
          The out tangent type for keyframes set by this command. Valid values are: auto, clamped, fast, flat, linear, plateau,
          slow, spline, step, and stepnext. Default is keyTangent -q -g -outTangentType
    
      - respectKeyable : rk            (bool)          [create]
          When used with the -attribute flag, prevents the keying of the non keyable attributes.
    
      - shape : s                      (bool)          [create]
          Consider attributes of shapes below transforms as well, except controlPoints.  Default: true
    
      - time : t                       (time)          [create]
          Time at which to set a keyframe on time-based animation curves.
    
      - useCurrentLockedWeights : lw   (bool)          [create]
          If we are setting a key over an existing key, use that key tangent's locked weight value for the new locked weight
          value.  Default is false
    
      - value : v                      (float)         [create]
          Value at which to set the keyframe. Using the value flag will not cause the keyed attribute to change to the specified
          value until the scene re-evaluates. Therefore, if you want the attribute to update to the new value immediately, use the
          setAttr command in addition to setting the key.                  Flag can have multiple arguments, passed either as a
          tuple or a list.
    
    
    Derived from mel command `maya.cmds.setKeyframe`
    """

    pass


def disconnectJoint(*args, **kwargs):
    """
    This command will break a skeleton at the selected joint and delete any associated handles.
    
    Flags:
      - attachHandleMode : ahm         (bool)          [create]
          This flag is obsolete and no longer supported.
    
      - deleteHandleMode : dhm         (bool)          [create]
          Delete the handle on the associated joint.                  Flag can have multiple arguments, passed either as a tuple
          or a list.
    
    
    Derived from mel command `maya.cmds.disconnectJoint`
    """

    pass


def reroot(*args, **kwargs):
    """
    This command will reroot a skeleton. The selected joint or the given joint at the command line will be the new    root
    of the skeleton. All ikHandles passing through the selected joint or above it will be deleted. The given(or selected)
    joint should not have skin attached. The    command works on the given or selected joint. No options or flags are
    necessary.
    
    
    Derived from mel command `maya.cmds.reroot`
    """

    pass


def play(*args, **kwargs):
    """
    This command starts and stops playback. In order to change the frame range of playback, see the playbackOptions command.
    In query mode, return type is based on queried flag.
    
    Flags:
      - forward : f                    (bool)          [create,query]
          When true, play back the animation from the currentTime to the maximum of the playback range. When false, play back from
          the currentTime to the minimum of the playback range.  When queried, returns an int.
    
      - playSound : ps                 (bool)          [create,query]
          Specify whether or not sound should be used during playback
    
      - record : rec                   (bool)          [create,query]
          enable the recording system and start one playback loop
    
      - sound : s                      (unicode)       [create,query]
          Specify the sound node to be used during playback
    
      - state : st                     (bool)          [create,query]
          start or stop playing back
    
      - wait : w                       (bool)          [create]
          Wait till completion before returning control to command Window.                  Flag can have multiple arguments,
          passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.play`
    """

    pass


def filterCurve(*args, **kwargs):
    """
    The filterCurve command takes a list of anim curve and filters         them. Currently only a Euler filter is supported.
    The Euler filter         demangles discontinous rotation anim curves into smooth curves.
    
    Flags:
      - endTime : e                    (time)          [create]
          Specify the end time of the section to filter. If not specified, the last key of the animation curve is used to define
          the end time.
    
      - filter : f                     (unicode)       [create]
          Specifies the filter type to use. The avalible filters are euler, simplify, and resample. By default euler is used.
    
      - kernel : ker                   (unicode)       [create]
          The resample kernel is a decimation resampling filter used to resample dense data. It works on the keyframes and may not
          produce the desired results when used with sparse data. The resample filter converts from either uniform or non-uniform
          timestep input data samples to the specified uniform timeStep. Various time domain filters are available and are
          specified with the kernel flag which selects the resampling kernel applied to the keyframes on the animation curves.
          Kernel ValuesclosestClosest sample to output timestamplirpLinear interpolation between closest samplesboxBox filter:
          moving averagetriangleTriangle filter: (1 - |x|)  weighted moving averagegaussian2Gaussian2 Filter: (2^(-2x\*x))
          weighted moving averagegaussian4Gaussian4 Filter: (2^(-4x\*x))  weighted moving averageThis filter is onlytargeted at
          decimation resampling -- interpolation resampling is basically unsupported.  If your output framerate is much higher
          than your input frame rate (approximate, as the input timestep is not assumed to be regular) the lirp and triangle will
          interpolate (usually) and the rest will either average, or use the closest sample (depending on the phase and frequency
          of the input).  However this mode of operation may not give the expected result.
    
      - maxTimeStep : mxs              (float)         [create]
          Simplify filter.
    
      - minTimeStep : mns              (float)         [create]
          Simplify filter.
    
      - period : per                   (float)         [create]
          Resample filter
    
      - startTime : s                  (time)          [create]
          Specify the start time to filter. If not specified, then the first key in the animation curve is used to get the start
          time.
    
      - timeTolerance : tto            (float)         [create]
          Simplify filter.
    
      - tolerance : tol                (float)         [create]
          Simplify filter.                                   Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.filterCurve`
    """

    pass


def blendShapeEditor(*args, **kwargs):
    """
    This command creates an editor that derives from the base editor class that has controls for blendShape, control nodes.
    
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
    
      - targetControlList : tcl        (bool)          [query]
    
      - targetList : tl                (bool)          [query]
    
      - unParent : up                  (bool)          [create,edit]
          Specifies that the editor should be removed from its layout. This cannot be used in query mode.
    
      - unlockMainConnection : ulk     (bool)          [create,edit]
          Unlocks the mainConnection, effectively restoring the original mainConnection (if it is still available), and dynamic
          updates.
    
      - updateMainConnection : upd     (bool)          [create,edit]
          Causes a locked mainConnection to be updated from the orginal mainConnection, but preserves the lock state.
    
      - useTemplate : ut               (unicode)       [create]
          Forces the command to use a command template other than the current one.
    
      - verticalSliders : vs           (bool)          [create,query,edit]
          Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.blendShapeEditor`
    """

    pass


def flow(*args, **kwargs):
    """
    The flow command creates a deformation lattice to `bend' the object that is animated along a curve of a motion path
    animation. The motion path animation has to have the follow option set to be on.
    
    Flags:
      - divisions : dv                 (int, int, int) [query]
          This flag specifies the number of lattice slices in x,y,z.The default values are 2 5 2.When queried, it returns the
          TuInt32 TuInt32 TuInt32
    
      - localCompute : lc              (bool)          [query]
          This flag specifies whether or not to have local control over the object deformation.Default value: is on when the
          lattice is around the curve, and is off when the lattice is around the object. When queried, it returns a boolean
    
      - localDivisions : ld            (int, int, int) [query]
          This flag specifies the extent of the region of effect.Default values are 2 2 2.When queried, it returns the TuInt32
          TuInt32 TuInt32
    
      - objectCentered : oc            (bool)          [query]
          This flag specifies whether to create the lattice around the selected object at its center, or to create the lattice
          around the curve.Default value is true.When queried, it returns a booleanFlag can have multiple arguments, passed either
          as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.flow`
    """

    pass


def keyTangent(*args, **kwargs):
    """
    This command operates on a keyset.  A keyset is defined as a group of keys within a specified time range on one or more
    animation curves. The animation curves comprising a keyset depend on the value of the -animationflag: keysOrObjects: Any
    active keys, when no target objects or -attribute flags appear on the command line, orAll animation curves connected to
    all keyframable attributes of objects specified as the command line's targetList, when there are no active keys.keys:
    Only act on active keys or tangents. If there are no active keys or tangents, don't do anything. objects: Only act on
    specified objects.  If there are no objects specified, don't do anything. Note that the -animationflag can be used to
    override the curves uniquely identified by the multi-use -attributeflag, which takes an argument of the form
    attributeName, such as translateX. Keys on animation curves are identified by either their time values or their indices.
    Times and indices can be given individually or as part of a list or range. -time 10palmeans the key at frame 10 (PAL
    format).-time 1.0sec -time 15ntsc -time 20means the keys at time 1.0 second, frame 15 (in NTSC format), and time 20 (in
    the currently defined global time unit).-time 10:20means all keys in the range from 10 to 20, inclusive, in the current
    time unit.Omitting one end of a range means go to infinity, as in the following examples: -time 10:means all keys from
    time 10 (in the current time unit) onwards.-time :10means all keys up to (and including) time 10 (in the current time
    unit).-time :is a short form to specify all keys.-index 0means the first key of each animation curve. (Indices are
    0-based.)-index 2 -index 5 -index 7means the 3rd, 6th, and 8th keys.-index 1:5means the 2nd, 3rd, 4th, 5th, and 6th keys
    of each animation curve.This command edits or queries tangent properties of keyframes in a keyset.  It is also used to
    edit or query the default tangent type of newly created keyframes (see the setKeyframe command for more information on
    how to override this default). Tangents help manage the shape of the animation curve and affect the interpolation
    between keys.  The tangent angle specifies the direction the curve will take as it leaves (or enters) a key. The tangent
    weight specifies how much influence the tangent angle has on the curve before the curve starts towards the next key.
    Maya internally represents tangents as x and y values.  Refer to the API documentation for MFnAnimCurve for a
    description of the relationship between tangent angle and weight and the internal x and y values.
    
    Flags:
      - absolute : a                   (bool)          [create,edit]
          Changes to tangent positions are NOT relative to the current position.
    
      - animation : an                 (unicode)       [create]
          Where this command should get the animation to act on.  Valid values are objects,keys,and keysOrObjectsDefault:
          keysOrObjects.(See Description for details.)
    
      - attribute : at                 (unicode)       [create]
          List of attributes to select
    
      - controlPoints : cp             (bool)          [create]
          This flag explicitly specifies whether or not to include the control points of a shape (see -sflag) in the list of
          attributes. Default: false.  (Not valid for pasteKeycmd.)
    
      - float : f                      (floatrange)    [create]
          value uniquely representing a non-time-based key (or key range) on a time-based animCurve.  Valid floatRange include
          single values (-f 10) or a string with a lower and upper bound, separated by a colon (-f 10:20
    
      - g : g                          (bool)          [create]
          Required for all operations on the global tangent type. The global tangent type is used by the setKeyframe command when
          tangent types have not been specifically applied, except in combination with flags such as 'i/insert' which preserve the
          shape of the curve.  It is also used when keys are set from the menu. The only flags that can appear on a keyTangent
          command with the 'g/global' flag are 'itt/inTangentType', 'ott/outTangentType' and 'wt/weightedTangents'.
    
      - hierarchy : hi                 (unicode)       [create]
          Hierarchy expansion options.  Valid values are above,below,both,and none.(Not valid for pasteKeycmd.)
    
      - inAngle : ia                   (float)         [create,query,edit]
          New value for the angle of the in-tangent. Returns a float[] when queried.
    
      - inTangentType : itt            (unicode)       [create,query,edit]
          Specify the in-tangent type.  Valid values are spline,linear,fast,slow,flat,step,stepnext,fixed,clamped,plateauand auto.
          Returns a string[] when queried.
    
      - inWeight : iw                  (float)         [create,query,edit]
          New value for the weight of the in-tangent. Returns a float[] when queried.
    
      - includeUpperBound : iub        (bool)          [create]
          When the -t/time or -f/float flags represent a range of keys, this flag determines whether the keys at the upper bound
          of the range are included in the keyset. Default value: true.  This flag is only valid when the argument to the -t/time
          flag is a time range with a lower and upper bound.  (When used with the pasteKeycommand, this flag refers only to the
          time range of the target curve that is replaced, when using options such as replace,fitReplace,or scaleReplace.This flag
          has no effect on the curve pasted from the clipboard.)
    
      - index : index                  (int)           [create]
          index of a key on an animCurve
    
      - ix : ix                        (float)         [create,query,edit]
          New value for the x-component of the in-tangent. This is a unit independent representation of the tangent component.
          Returns a float[] when queried.
    
      - iy : iy                        (float)         [create,query,edit]
          New value for the y-component of the in-tangent. This is a unit independent representation of the tangent component.
          Returns a float[] when queried.
    
      - lock : l                       (bool)          [create,query,edit]
          Lock a tangent so in and out tangents move together. Returns an int[] when queried.
    
      - outAngle : oa                  (float)         [create,query,edit]
          New value for the angle of the out-tangent. Returns a float[] when queried.
    
      - outTangentType : ott           (unicode)       [create,query,edit]
          Specify the out-tangent type.  Valid values are spline,linear,fast,slow,flat,step,stepnext,fixed,clamped,plateauand
          auto. Returns a string[] when queried.
    
      - outWeight : ow                 (float)         [create,query,edit]
          New value for the weight of the out-tangent. Returns a float[] when queried.
    
      - ox : ox                        (float)         [create,query,edit]
          New value for the x-component of the out-tangent. This is a unit independent representation of the tangent component.
          Returns a float[] when queried.
    
      - oy : oy                        (float)         [create,query,edit]
          New value for the y-component of the out-tangent. This is a unit independent representation of the tangent component.
          Returns a float[] when queried.
    
      - pluginTangentTypes : ptt       (unicode)       [query]
          Returns a list of the plug-in tangent types that have been loaded. Return type is a string array.
    
      - relative : r                   (bool)          [create,edit]
          Changes to tangent positions are relative to the current position.
    
      - shape : s                      (bool)          [create]
          Consider attributes of shapes below transforms as well, except controlPoints.  Default: true.  (Not valid for
          pasteKeycmd.)
    
      - stepAttributes : sa            (bool)          [create,edit]
          The setKeyframe command will automatically set tangents for boolean and enumerated attributes to step.  This flag
          mirrors this behavior for the keyTangent command.  When set to false, tangents for these attributes will not be edited.
          When set to true (the default) tangents for these attributes will be edited.
    
      - time : t                       (timerange)     [create]
          time uniquely representing a key (or key range) on a time-based animCurve.  Valid timeRanges include single values (-t
          10) or a string with a lower and upper bound, separated by a colon (-t 10:20
    
      - unify : uni                    (bool)          [create,edit]
          Unify a tangent so in and out tangents are equal and move together.
    
      - weightLock : wl                (bool)          [create,query,edit]
          Lock the weight of a tangent so it is fixed. Returns an int[] when queried. Note: weightLock is only obeyed within the
          graph editor.  It is not obeyed when -inWeight/-outWeight are issued from a command.
    
      - weightedTangents : wt          (bool)          [create,query,edit]
          Specify whether or not the tangents on the animCurve are weighted Note: switching a curve from weightedTangents true to
          false and back to true again will not preserve fixed tangents properly. Use undo instead.                  Flag can have
          multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.keyTangent`
    """

    pass


def ubercam(*args, **kwargs):
    """
    Use this command to create a ubercamwith equivalent behavior to all cameras used by shots in the sequencer.
    
    
    Derived from mel command `maya.cmds.ubercam`
    """

    pass


def posePanel(*args, **kwargs):
    """
    This command creates a panel that derives from the base panel class that houses a poseEditor.
    
    Flags:
      - control : ctl                  (bool)          [query]
          Returns the top level control for this panel. Usually used for getting a parent to attach popup menus. CAUTION: panels
          may not have controls at times.  This flag can return if no control is present.
    
      - copy : cp                      (unicode)       [edit]
          Makes this panel a copy of the specified panel.  Both panels must be of the same type.
    
      - createString : cs              (bool)          [edit]
          Command string used to create a panel
    
      - defineTemplate : dt            (unicode)       [create]
          Puts the command in a mode where any other flags and args are parsed and added to the command template specified in the
          argument. They will be used as default arguments in any subsequent invocations of the command when templateName is set
          as the current template.
    
      - docTag : dtg                   (unicode)       [create,query,edit]
          Attaches a tag to the Maya panel.
    
      - editString : es                (bool)          [edit]
          Command string used to edit a panel
    
      - exists : ex                    (bool)          [create]
          Returns whether the specified object exists or not. Other flags are ignored.
    
      - init : init                    (bool)          [create,edit]
          Initializes the panel's default state.  This is usually done automatically on file -new and file -open.
    
      - isUnique : iu                  (bool)          [query]
          Returns true if only one instance of this panel type is allowed.
    
      - label : l                      (unicode)       [query,edit]
          Specifies the user readable label for the panel.
    
      - menuBarVisible : mbv           (bool)          [create,query,edit]
          Controls whether the menu bar for the panel is displayed.
    
      - needsInit : ni                 (bool)          [query,edit]
          (Internal) On Edit will mark the panel as requiring initialization. Query will return whether the panel is marked for
          initialization.  Used during file -new and file -open.
    
      - parent : p                     (unicode)       [create]
          Specifies the parent layout for this panel.
    
      - popupMenuProcedure : pmp       (script)        [query,edit]
          Specifies the procedure called for building the panel's popup menu(s). The default value is buildPanelPopupMenu.  The
          procedure should take one string argument which is the panel's name.
    
      - poseEditor : pe                (bool)          [query]
          Query only flag that returns the name of an editor to be associated with the panel.
    
      - replacePanel : rp              (unicode)       [edit]
          Will replace the specified panel with this panel.  If the target panel is within the same layout it will perform a swap.
    
      - tearOff : to                   (bool)          [query,edit]
          Will tear off this panel into a separate window with a paneLayout as the parent of the panel. When queried this flag
          will return if the panel has been torn off into its own window.
    
      - tearOffCopy : toc              (unicode)       [create]
          Will create this panel as a torn of copy of the specified source panel.
    
      - unParent : up                  (bool)          [edit]
          Specifies that the panel should be removed from its layout. This (obviously) cannot be used with query.
    
      - useTemplate : ut               (unicode)       [create]
          Forces the command to use a command template other than the current one.                  Flag can have multiple
          arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.posePanel`
    """

    pass


def textureDeformer(*args, **kwargs):
    """
    This command creates a texture deformer for the object. The selected objects are the input geometry objects. The
    deformer node name will be returned.
    
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
    
      - deformerTools : dt             (bool)          [query]
          Returns the name of the deformer tool objects (if any) as string string ...
    
      - direction : d                  (unicode)       [create]
          Set the deformation direction of texture deformer It can only handle three types: Normal, Handleand Vector. Normaleach
          vertices use its own normal vector. Handleall vertices use Up vector of the handle. Vectoreach vertices use RGB color
          vector strings.
    
      - envelope : en                  (float)         [create]
          Set the envelope of texture deformer. Envelope determines the percent of deformation. The final result is (color \*
          normal \* strength + offset) \* envelope
    
      - exclusive : ex                 (unicode)       [create,query]
          Puts the deformation set in a deform partition.
    
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
    
      - name : n                       (unicode)       [create]
          Used to specify the name of the node being created.
    
      - offset : o                     (float)         [create]
          Set the offset of texture deformer. Offset plus a translation on the final deformed vertices.
    
      - parallel : par                 (bool)          [create,edit]
          Inserts the new deformer in a parallel chain to any existing deformers in the history of the object. A blendShape is
          inserted to blend the parallel results together. Works in create mode (and edit mode if the deformer has no geometry
          added yet).
    
      - pointSpace : ps                (unicode)       [create]
          Set the point space of texture deformer. It can only handle three strings: World, Localand UV. Worldmap world space to
          color space. Localmap local space to color space. UVmap UV space to color space. strings.
    
      - prune : pr                     (bool)          [edit]
          Removes any points not being deformed by the deformer in its current configuration from the deformer set.
    
      - remove : rm                    (bool)          [edit]
          Specifies that objects listed after the -g flag should be removed from this deformer.
    
      - split : sp                     (bool)          [create,edit]
          Branches off a new chain in the dependency graph instead of inserting/appending the deformer into/onto an existing
          chain. Works in create mode (and edit mode if the deformer has no geometry added yet).
    
      - strength : s                   (float)         [create]
          Set the strength of texture deformer. Strength determines how strong the object is deformed.
    
      - vectorOffset : vo              (float, float, float) [create]
          Set the vector offset of texture deformer. Vector offset indicates the offset of the deformation on the vector mode.
    
      - vectorSpace : vsp              (unicode)       [create]
          Set the vector space of texture deformer. It can only handle three strings: Object, Worldand Tangent. Objectuse color
          vector in object space Worlduse color vector in world space Tangentuse color vector in tangent space strings.
    
      - vectorStrength : vs            (float, float, float) [create]
          Set the vector strength of texture deformer. Vector strength determines how strong the object is deformed on the vector
          mode.                  Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.textureDeformer`
    """

    pass


def animCurveEditor(*args, **kwargs):
    """
    Edit a characteristic of a graph editor
    
    Flags:
      - acs : acs                      (areCurvesSelected) []
    
      - areCurvesSelected : acs        (bool)          [query]
          Returns a boolean to know if at least one curve is selected in the graph editor.
    
      - autoFit : af                   (unicode)       [query,edit]
          on | off | tgl Auto fit-to-view.
    
      - classicMode : cm               (bool)          [query,edit]
          When on, the graph editor is displayed in Classic Mode, otherwise Suites Modeis used.
    
      - clipTime : ct                  (unicode)       [query,edit]
          Valid values: onoffDisplay the clips with their offset and scale applied to the anim curves in the clip.
    
      - constrainDrag : cd             (int)           [create,query,edit]
          Constrains all Graph Editor animation curve drag operations to either the X-axis, the Y-axis, or to neither of those
          axes. Values to supply are: 0 for not constraining any axis, 1 for constraing the X-axis, or 2 for constraining the
          Y-axis. When used in queries, this flag returns the latter values and these values have the same interpretation as
          above. Note: when the shift key is pressed before dragging the animation curve, the first mouse movement will instead
          determine (and override) any prior set constrained axis.
    
      - control : ctl                  (bool)          [query]
          Query only. Returns the top level control for this editor. Usually used for getting a parent to attach popup menus.
          Caution: It is possible for an editor to exist without a control. The query will return NONEif no control is present.
    
      - curvesShown : cs               (bool)          [query]
          Returns a string array containing the names of the animCurve nodes currently displayed in the graph editor.
    
      - curvesShownForceUpdate : csf   (bool)          [query]
          Returns a string array containing the names of the animCurve nodes currently displayed in the graph editor. Unlike the
          curvesShown flag, this will force an update of the graph editor for the case where the mainListConnection has been
          modified since the last refresh.
    
      - defineTemplate : dt            (unicode)       [create]
          Puts the command in a mode where any other flags and args are parsed and added to the command template specified in the
          argument. They will be used as default arguments in any subsequent invocations of the command when templateName is set
          as the current template.
    
      - denormalizeCurvesCommand : dcc (unicode)       [create,edit]
          Sets the script that is run to denormalize curves in the graph editor. This is intended for internal use only.
    
      - displayActiveKeyTangents : dat (unicode)       [edit]
          on | off | tgl Display active key tangents in the editor.
    
      - displayActiveKeys : dak        (unicode)       [edit]
          on | off | tgl Display active keys in the editor.
    
      - displayInfinities : di         (unicode)       [edit]
          on | off | tgl Display infinities in the editor.
    
      - displayKeys : dk               (unicode)       [edit]
          on | off | tgl Display keyframes in the editor.
    
      - displayNormalized : dn         (bool)          [query,edit]
          When on, display all curves normalized to the range -1 to +1.
    
      - displayTangents : dtn          (unicode)       [edit]
          on | off | tgl Display tangents in the editor.
    
      - displayValues : dv             (unicode)       [edit]
          on | off | tgl Display active keys and tangents values in the editor.
    
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
    
      - keyingTime : kt                (unicode)       [query]
          The current time in the given curve to be keyed in the graph editor.
    
      - lockMainConnection : lck       (bool)          [create,edit]
          Locks the current list of objects within the mainConnection, so that only those objects are displayed within the editor.
          Further changes to the original mainConnection are ignored.
    
      - lookAt : la                    (unicode)       [edit]
          all | selected | currentTime FitView helpers.
    
      - mainListConnection : mlc       (unicode)       [create,query,edit]
          Specifies the name of a selectionConnection object that the editor will use as its source of content. The editor will
          only display items contained in the selectionConnection object.
    
      - menu : m                       (script)        [create]
          Specify a script to be run when the editor is created.  The function will be passed one string argument which is the new
          editor's name.
    
      - normalizeCurvesCommand : ncc   (unicode)       [create,edit]
          Sets the script that is run to normalize curves in the graph editor. This is intended for internal use only.
    
      - outliner : o                   (unicode)       [query,edit]
          The name of the outliner that is associated with the graph editor.
    
      - panel : pnl                    (unicode)       [create,query]
          Specifies the panel for this editor. By default if an editor is created in the create callback of a scripted panel it
          will belong to that panel. If an editor does not belong to a panel it will be deleted when the window that it is in is
          deleted.
    
      - parent : p                     (unicode)       [create,query,edit]
          Specifies the parent layout for this editor. This flag will only have an effect if the editor is currently un-parented.
    
      - preSelectionHighlight : psh    (bool)          [query,edit]
          When on, the curve/key/tangent under the mouse pointer is highlighted to ease selection.
    
      - renormalizeCurves : rnc        (bool)          [edit]
          This flag causes the curve normalization factors to be recalculated.
    
      - resultSamples : rs             (time)          [query,edit]
          Specify the sampling for result curves Note: the smaller this number is, the longer it will take to update the display.
    
      - resultScreenSamples : rss      (int)           [query,edit]
          Specify the screen base result sampling for result curves. If 0, then results are sampled in time.
    
      - resultUpdate : ru              (unicode)       [query,edit]
          Valid values: interactivedelayedControls how changes to animCurves are reflected in the result curves (if results are
          being shown).  If resultUpdate is interactive, then as interactive changes are being made to the animCurve, the result
          curves will be updated.  If modelUpdate is delayed (which is the default setting), then result curves are updated once
          the final change to an animCurve has been made.
    
      - selectionConnection : slc      (unicode)       [create,query,edit]
          Specifies the name of a selectionConnection object that the editor will synchronize with its own selection list. As the
          user selects things in this editor, they will be selected in the selectionConnection object. If the object undergoes
          changes, the editor updates to show the changes.
    
      - showActiveCurveNames : acn     (bool)          [query,edit]
          Display the active curve(s)'s name.
    
      - showBufferCurves : sb          (unicode)       [query,edit]
          Valid values: onofftglDisplay buffer curves.
    
      - showCurveNames : scn           (bool)          [query,edit]
          Display the curves's name.
    
      - showResults : sr               (unicode)       [query,edit]
          Valid values: onofftglDisplay result curves from expression or other non-keyed action.
    
      - showUpstreamCurves : suc       (bool)          [query,edit]
          If true, the dependency graph is searched upstream for all curves that drive the selected plugs (showing multiple curves
          for example in a typical driven key setup, where first the driven key curve is encountered, followed by the actual
          animation curve that drives the source object). If false, only the first curves encountered will be shown. Note that,
          even if false, multiple curves can be shown if e.g. a blendWeighted node is being used to combine multiple curves.
    
      - smoothness : s                 (unicode)       [query,edit]
          Valid values: coarseroughmediumfineSpecify the display smoothness of animation curves.
    
      - snapTime : st                  (unicode)       [query,edit]
          none | integer | keyframe Keyframe move snap in time.
    
      - snapValue : sv                 (unicode)       [query,edit]
          none | integer | keyframe Keyframe move snap in values.
    
      - stackedCurves : sc             (bool)          [query,edit]
          Switches the display mode between normal (all curves sharing one set of axes) to stacked (each curve on its own value
          axis, stacked vertically).
    
      - stackedCurvesMax : scx         (float)         [query,edit]
          Sets the maximum value on the per-curve value axis when in stacked mode.
    
      - stackedCurvesMin : scm         (float)         [query,edit]
          Sets the minimum value on the per-curve value axis when in stacked mode.
    
      - stackedCurvesSpace : scs       (float)         [query,edit]
          Sets the spacing between curves when in stacked mode.
    
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
    
      - valueLinesToggle : vlt         (unicode)       [edit]
          on | off | tgl Display the value lines for high/low/zero of selected curves in the editor                  Flag can have
          multiple arguments, passed either as a tuple or a list.
    
      - viewLeft : vl                  (float)         []
    
      - viewRight : vr                 (float)         []
    
    
    Derived from mel command `maya.cmds.animCurveEditor`
    """

    pass


def percent(*args, **kwargs):
    """
    This command sets percent values on members of a weighted node such as a cluster or a jointCluster. With no flags
    specified the command sets the percent value for selected components of the specified node to the specified percent
    value. A dropoff from the specified percent value to 0 can be specified from a point, plane or curve using a dropoff
    distance around that shape. The percent value can also be added or multiplied with existing percent values of the node
    components. In query mode, return type is based on queried flag.
    
    Flags:
      - addPercent : ap                (bool)          [create]
          Add the percent value specified with the -v flag to the existing percent values
    
      - dropoffAxis : dax              (float, float, float) [create]
          Specifies the axis along which to dropoff the percent value, starting from the dropoffPosition.
    
      - dropoffCurve : dc              (unicode)       [create]
          Specifies the curve around which to dropoff the percent value.
    
      - dropoffDistance : dds          (float)         [create]
          Specifies the dropoff distance from the point, plane or curve that was specified using the -dp -dax or -dc flags.
    
      - dropoffPosition : dp           (float, float, float) [create]
          Specifies the point around which to dropoff the percent value.
    
      - dropoffType : dt               (unicode)       [create]
          Specifies the type of dropoff. Used in conjunction with the -dp, -dax or -dc flags. Default is linear. Valid values are:
          linear, sine, exponential, linearSquared, none.
    
      - multiplyPercent : mp           (bool)          [create]
          Multiply the percent value specified with the -v flag with existing percent values
    
      - value : v                      (float)         [create,query]
          The percent value to be applied. The default is 1. In query mode, returns an array of doubles corresponding to the
          weights of the selected object components.                  Flag can have multiple arguments, passed either as a tuple
          or a list.
    
    
    Derived from mel command `maya.cmds.percent`
    """

    pass


def cutKey(*args, **kwargs):
    """
    This command operates on a keyset.  A keyset is defined as a group of keys within a specified time range on one or more
    animation curves. The animation curves comprising a keyset depend on the value of the -animationflag: keysOrObjects: Any
    active keys, when no target objects or -attribute flags appear on the command line, orAll animation curves connected to
    all keyframable attributes of objects specified as the command line's targetList, when there are no active keys.keys:
    Only act on active keys or tangents. If there are no active keys or tangents, don't do anything. objects: Only act on
    specified objects.  If there are no objects specified, don't do anything. Note that the -animationflag can be used to
    override the curves uniquely identified by the multi-use -attributeflag, which takes an argument of the form
    attributeName, such as translateX. Keys on animation curves are identified by either their time values or their indices.
    Times and indices can be given individually or as part of a list or range. -time 10palmeans the key at frame 10 (PAL
    format).-time 1.0sec -time 15ntsc -time 20means the keys at time 1.0 second, frame 15 (in NTSC format), and time 20 (in
    the currently defined global time unit).-time 10:20means all keys in the range from 10 to 20, inclusive, in the current
    time unit.Omitting one end of a range means go to infinity, as in the following examples: -time 10:means all keys from
    time 10 (in the current time unit) onwards.-time :10means all keys up to (and including) time 10 (in the current time
    unit).-time :is a short form to specify all keys.-index 0means the first key of each animation curve. (Indices are
    0-based.)-index 2 -index 5 -index 7means the 3rd, 6th, and 8th keys.-index 1:5means the 2nd, 3rd, 4th, 5th, and 6th keys
    of each animation curve.The cutKey command cuts curve segment hierarchies from specified targets and puts them in the
    clipboard.  The pasteKey command applies these curves to other objects.The shape of the cut curve placed in the
    clipboard, and the effect of the cutKey command on the source animation curve depends on the cutKey -optionspecified.
    Each of these options below will be explained using an example.  For all the explanations, let us assume that the source
    animation curve (from which keys will be cut) has 5 keyframes at times 10, 15, 20, 25, and 30.TbaseKeySetCmd.h cutKey -t
    12:22-option keysKeyframes at times 15 and 20 are removed. All other keys are unchanged.A 5-frame animation curve is
    placed into the keyset clipboard.cutKey -t 12:22-option keysCollapseKeyframes at times 15 and 20 are removed.  Shift all
    keys after time 20 to the left by 5 frames, preserving all their values.A 5-frame animation curve is placed into the
    keyset clipboard.cutKey -t 12:22-option keysConnectKeyframes at times 15 and 20 are removed.  Shift all keys after time
    20 to the left by 5 frames, and place the key that used to be at time 25 at the value of the key that used to be at time
    15.A 5-frame animation curve is placed into the keyset clipboard.cutKey -t 12:22-option curveKeyframes at times 15 and
    20 are removed.  Keys are inserted at times 12 and 22.A 10-frame animation curve is placed into the keyset
    clipboard.cutKey -t 12:22-option curveCollapseKeyframes at times 15 and 20 are removed.  Keys are inserted at times 12
    and 22.  Shift all keys from time 22 to the left by 10 frames, preserving their values.A 10-frame animation curve is
    placed into the keyset clipboard.cutKey -t 12:22-option curveConnectKeyframes at times 15 and 20 are removed.  Keys are
    inserted at times 12 and 22.  Shift all keys from time 22 to the left by 10 frames, and replace the key inserted at time
    12 with the newly inserted key at time 22.A 10-frame animation curve is placed into the keyset clipboard.cutKey -t
    12:22-option areaCollapseKeyframes at times 15 and 20 are removed. Shift all keys from time 22 to the left by 10 frames,
    preserving their values.A 10-frame animation curve is placed into the keyset clipboard.
    
    Flags:
      - animation : an                 (unicode)       [create]
          Where this command should get the animation to act on.  Valid values are objects,keys,and keysOrObjectsDefault:
          keysOrObjects.(See Description for details.)
    
      - attribute : at                 (unicode)       [create]
          List of attributes to select
    
      - clear : cl                     (bool)          [create]
          Just remove the keyframes (i.e. do not overwrite the clipboard)
    
      - controlPoints : cp             (bool)          [create]
          This flag explicitly specifies whether or not to include the control points of a shape (see -sflag) in the list of
          attributes. Default: false.  (Not valid for pasteKeycmd.)
    
      - float : f                      (floatrange)    [create]
          value uniquely representing a non-time-based key (or key range) on a time-based animCurve.  Valid floatRange include
          single values (-f 10) or a string with a lower and upper bound, separated by a colon (-f 10:20
    
      - hierarchy : hi                 (unicode)       [create]
          Hierarchy expansion options.  Valid values are above,below,both,and none.(Not valid for pasteKeycmd.)
    
      - includeUpperBound : iub        (bool)          [create]
          When the -t/time or -f/float flags represent a range of keys, this flag determines whether the keys at the upper bound
          of the range are included in the keyset. Default value: true.  This flag is only valid when the argument to the -t/time
          flag is a time range with a lower and upper bound.  (When used with the pasteKeycommand, this flag refers only to the
          time range of the target curve that is replaced, when using options such as replace,fitReplace,or scaleReplace.This flag
          has no effect on the curve pasted from the clipboard.)
    
      - index : index                  (int)           [create]
          index of a key on an animCurve
    
      - option : o                     (unicode)       [create]
          Option for how to perform the cutKey operation.  Valid values for this flag are keys, curve, curveCollapse,
          curveConnect, areaCollapse.  The default cut option is: keys
    
      - selectKey : sl                 (bool)          [create]
          Select the keyframes of curves which have had keys removed
    
      - shape : s                      (bool)          [create]
          Consider attributes of shapes below transforms as well, except controlPoints.  Default: true.  (Not valid for
          pasteKeycmd.)
    
      - time : t                       (timerange)     [create]
          time uniquely representing a key (or key range) on a time-based animCurve.  Valid timeRanges include single values (-t
          10) or a string with a lower and upper bound, separated by a colon (-t 10:20Flag can have multiple arguments, passed
          either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.cutKey`
    """

    pass


def freezeOptions(*args, **kwargs):
    """
    This command provides access to the options used by the evaluation manager to handle propagation and recognition of when
    a node is in a frozen state. See the individual flags for the different options available. These values are all stored
    as user preferences and persist across sessions.
    
    Flags:
      - displayLayers : dl             (bool)          [create,query]
          If this option is enabled then any nodes that are in an enabled, invisible display layer will be considered to be
          frozen, and the frozen state will propagate accordingly.
    
      - downstream : dn                (unicode)       [create,query]
          Controls how frozen state is propagated downstream from currently frozen nodes. Valid values are nonefor no propagation,
          safefor propagation downstream only when all upstream nodes are frozen, and forcefor propagation downstream when any
          upstream node is frozen.
    
      - explicitPropagation : ep       (bool)          [create,query]
          When turned on this will perform an extra pass when the evaluation graph is constructed to perform intelligent
          propagation of the frozen state to related nodes as specified by the currently enabled options of the evaluation graph.
          See also runtimePropagation. This option performs more thorough propagation of the frozen state, but requires extra time
          for recalculating the evaluation graph.
    
      - invisible : inv                (bool)          [create,query]
          If this option is enabled then any nodes that are invisible, either directly or via an invisible parent node, will be
          considered to be frozen, and the frozen state will propagate accordingly.
    
      - referencedNodes : rn           (bool)          [create,query]
          If this option is enabled then any nodes that are referenced in from a frozen referenced node will also be considered to
          be frozen, and the frozen state will propagate accordingly.
    
      - runtimePropagation : rt        (bool)          [create,query]
          When turned on this will allow the frozen state to propagate during execution of the evaluation graph. See also
          explicitPropagation. This option allows frozen nodes to be scheduled for evaluation, but once it discovers a node that
          is frozen it will prune the evaluation based on the current set of enabled options. It only works in the downstream
          direction.
    
      - upstream : up                  (unicode)       [create,query]
          Controls how frozen state is propagated upstream from currently frozen nodes. Valid values are nonefor no propagation,
          safefor propagation upstream only when all downstream nodes are frozen, and forcefor propagation upstream when any
          downstream node is frozen.                               Flag can have multiple arguments, passed either as a tuple or a
          list.
    
    
    Derived from mel command `maya.cmds.freezeOptions`
    """

    pass


def bakeResults(*args, **kwargs):
    """
    This command allows the user to replace a chain of dependency nodes which define the value for an attribute with a
    single animation curve. Command allows the user to specify the range and frequency of sampling. This command operates on
    a keyset. A keyset is defined as a group of keys within a specified time range on one or more animation curves. The
    animation curves comprising a keyset depend on the value of the -animationflag: keysOrObjects: Any active keys, when no
    target objects or -attribute flags appear on the command line, orAll animation curves connected to all keyframable
    attributes of objects specified as the command line's targetList, when there are no active keys.keys: Only act on active
    keys or tangents. If there are no active keys or tangents, do not do anything. objects: Only act on specified objects.
    If there are no objects specified, do not do anything. Note that the -animationflag can be used to override the curves
    uniquely identified by the multi-use -attributeflag, which takes an argument of the form attributeName, such as
    translateX. Keys on animation curves are identified by either their time values or their indices. Times and indices
    should be specified as a range, as shown below. -time 10:20means all keys in the range from 10 to 20, inclusive, in the
    current time unit.-index 1:5means the 2nd, 3rd, 4th, 5th, and 6th keys of each animation curve.
    
    Flags:
      - animation : an                 (unicode)       [create]
          Where this command should get the animation to act on. Valid values are objects,keys,and keysOrObjectsDefault:
          keysOrObjects.See command description for details.
    
      - attribute : at                 (unicode)       [create]
          List of attributes to select
    
      - bakeOnOverrideLayer : bol      (bool)          [create]
          If true, all layered and baked attribute will be added as a top override layer.
    
      - controlPoints : cp             (bool)          [create]
          This flag explicitly specifies whether or not to include the control points of a shape (see -sflag) in the list of
          attributes. Default: false.  (Not valid for pasteKeycmd.)
    
      - destinationLayer : dl          (unicode)       [create]
          This flag can be used to specify an existing layer where the baked results should be stored. Use this flag with caution.
          If the destination layer already has animation on it that contributes to the final result, it will be replaced by the
          output of the bake. As a result, it is possible that the combined animation visible in the scene is different before /
          after the baking process.
    
      - disableImplicitControl : dic   (bool)          [create]
          Whether to disable implicit control after the anim curves are obtained as the result of this command. An implicit
          control to an attribute is some function that affects the attribute without using an explicit dependency graph
          connection. The control of IK, via ik handles, is an example.
    
      - float : f                      (floatrange)    [create]
          value uniquely representing a non-time-based key (or key range) on a time-based animCurve. Valid floatRange include
          single values (-f 10) or a string with a lower and upper bound, separated by a colon (-f 10:20
    
      - hierarchy : hi                 (unicode)       [create]
          Hierarchy expansion options.  Valid values are above,below,both,and none.(Not valid for pasteKeycmd.)
    
      - includeUpperBound : iub        (bool)          [create]
          When the -t/time or -f/float flags represent a range of keys, this flag determines whether the keys at the upper bound
          of the range are included in the keyset. Default value: true. This flag is only valid when the argument to the -t/time
          flag is a time range with a lower and upper bound. Note: when used with the pasteKeycommand, this flag refers only to
          the time range of the target curve that is replaced, when using options such as replace,fitReplace,or scaleReplace.This
          flag has no effect on the curve pasted from the clipboard.
    
      - index : index                  (int)           [create]
          index of a key on an animCurve
    
      - minimizeRotation : mr          (bool)          [create]
          Specify whether to minimize the local Euler component from key to key during baking of rotation channels.
    
      - oversamplingRate : osr         (int)           [create]
          Amount of samples per sampleBy period. Default is 1.
    
      - preserveOutsideKeys : pok      (bool)          [create]
          Whether to preserve keys that are outside the bake range when there are directly connected animation curves or a
          pairBlend node which has an animation curve as its direct input. The default (false) is to remove frames outside the
          bake range. If the channel that you are baking is not controlled by a single animation curve, then a new animation curve
          will be created with keys only in the bake range. In the case of pairBlend-driven channels, setting pok to true will
          retain both the pairBlend and its input animCurve. The blended values will be baked onto the animCurve and the weight of
          the pairBlend weight will be keyed to the animCurve during the baked range.
    
      - removeBakedAnimFromLayer : rba (bool)          []
    
      - removeBakedAttributeFromLayer : ral (bool)          [create]
          If true, all baked attribute will be removed from the layer. Otherwise all layer associated with the baked attribute
          will be muted.
    
      - resolveWithoutLayer : rwl      (unicode)       [create]
          This flag can be used to specify a list of layers to be merged together during the bake process. This is a multi-use
          flag. Its name refers to the fact that when solving for the value to key, it determines the proper value to key on the
          destination layer to achieve the same result as the merged layers.
    
      - sampleBy : sb                  (time)          [create]
          Amount to sample by. Default is 1.0 in current timeUnit.
    
      - shape : s                      (bool)          [create]
          Consider attributes of shapes below transforms as well, except controlPoints.  Default: true.  (Not valid for
          pasteKeycmd.)
    
      - simulation : sm                (bool)          [create]
          Using this flag instructs the command to preform a simulation instead of just evaluating each attribute separately over
          the range of time. The simulation flag is required to bake animation that that depends on the whole scene being
          evaluated at each time step such as dynamics. The default is false.
    
      - smart : sr                     (bool, float)   [create]
          Specify whether to enable smart bake and the optional smart bake tolerance.
    
      - sparseAnimCurveBake : sac      (bool)          [create]
          When this is true and anim curves are being baked, do not insert any keys into areas of the curve where animation is
          defined. And, use as few keys as possible to bake the pre and post infinity behavior. When this is false, one key will
          be inserted at each time step. The default is false.
    
      - time : t                       (timerange)     [create]
          time uniquely representing a key (or key range) on a time-based animCurve. Valid timeRanges include single values (-t
          10) or a string with a lower and upper bound, separated by a colon (-t 10:20Flag can have multiple arguments, passed
          either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.bakeResults`
    """

    pass


def controller(*args, **kwargs):
    """
    Commands for managing animation sources
    
    Flags:
      - allControllers : ac            (bool)          [create,query,edit]
          When this flag is queried, returns all dependNode attached to a controller in the scene.
    
      - children : cld                 (bool)          [query,edit]
          Return true if the specified dependNode is a controller.
    
      - group : g                      (bool)          [create,query,edit]
          Create a controller that is not associated with any object. This new controller will be the parent of all the selected
          objects.
    
      - index : idx                    (int)           [query,edit]
          In query mode, returns the index of the controller in the parent controller's list of children. In edit mode, reorder
          the parent controller's children connections so that the current controller is assigned the given index.
    
      - isController : ic              (unicode)       [create,query,edit]
          Returns true if the specified dependNode is a controller.
    
      - parent : p                     (bool)          [create,query,edit]
          Set or query the parent controller of the selected controller node.
    
      - pickWalkDown : pwd             (bool)          [query,edit]
          Return the first child.
    
      - pickWalkLeft : pwl             (bool)          [query,edit]
          Return the previous sibling.
    
      - pickWalkRight : pwr            (bool)          [query,edit]
          Return the next sibling.
    
      - pickWalkUp : pwu               (bool)          [query,edit]
          Return the parent.
    
      - unparent : unp                 (bool)          [query,edit]
          Unparent all selected controller objects from their respective parent.                             Flag can have
          multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.controller`
    """

    pass


def snapKey(*args, **kwargs):
    """
    This command operates on a keyset.  A keyset is defined as a group of keys within a specified time range on one or more
    animation curves. The animation curves comprising a keyset depend on the value of the -animationflag: keysOrObjects: Any
    active keys, when no target objects or -attribute flags appear on the command line, orAll animation curves connected to
    all keyframable attributes of objects specified as the command line's targetList, when there are no active keys.keys:
    Only act on active keys or tangents. If there are no active keys or tangents, don't do anything. objects: Only act on
    specified objects.  If there are no objects specified, don't do anything. Note that the -animationflag can be used to
    override the curves uniquely identified by the multi-use -attributeflag, which takes an argument of the form
    attributeName, such as translateX. Keys on animation curves are identified by either their time values or their indices.
    Times and indices can be given individually or as part of a list or range. -time 10palmeans the key at frame 10 (PAL
    format).-time 1.0sec -time 15ntsc -time 20means the keys at time 1.0 second, frame 15 (in NTSC format), and time 20 (in
    the currently defined global time unit).-time 10:20means all keys in the range from 10 to 20, inclusive, in the current
    time unit.Omitting one end of a range means go to infinity, as in the following examples: -time 10:means all keys from
    time 10 (in the current time unit) onwards.-time :10means all keys up to (and including) time 10 (in the current time
    unit).-time :is a short form to specify all keys.-index 0means the first key of each animation curve. (Indices are
    0-based.)-index 2 -index 5 -index 7means the 3rd, 6th, and 8th keys.-index 1:5means the 2nd, 3rd, 4th, 5th, and 6th keys
    of each animation curve.This command snapsall target key times and/or values so that they have times and/or values that
    are multiples of the specified flag arguments.  If neither multiple is specified, default is time snapping with a
    multiple of 1.0. Note that this command will fail to move keys over other neighboring keys: a key's index will not
    change as a result of a snapKey operation.TbaseKeySetCmd.h
    
    Flags:
      - animation : an                 (unicode)       [create]
          Where this command should get the animation to act on.  Valid values are objects,keys,and keysOrObjectsDefault:
          keysOrObjects.(See Description for details.)
    
      - attribute : at                 (unicode)       [create]
          List of attributes to select
    
      - controlPoints : cp             (bool)          [create]
          This flag explicitly specifies whether or not to include the control points of a shape (see -sflag) in the list of
          attributes. Default: false.  (Not valid for pasteKeycmd.)
    
      - float : f                      (floatrange)    [create]
          value uniquely representing a non-time-based key (or key range) on a time-based animCurve.  Valid floatRange include
          single values (-f 10) or a string with a lower and upper bound, separated by a colon (-f 10:20
    
      - hierarchy : hi                 (unicode)       [create]
          Hierarchy expansion options.  Valid values are above,below,both,and none.(Not valid for pasteKeycmd.)
    
      - includeUpperBound : iub        (bool)          [create]
          When the -t/time or -f/float flags represent a range of keys, this flag determines whether the keys at the upper bound
          of the range are included in the keyset. Default value: true.  This flag is only valid when the argument to the -t/time
          flag is a time range with a lower and upper bound.  (When used with the pasteKeycommand, this flag refers only to the
          time range of the target curve that is replaced, when using options such as replace,fitReplace,or scaleReplace.This flag
          has no effect on the curve pasted from the clipboard.)
    
      - index : index                  (int)           [create]
          index of a key on an animCurve
    
      - shape : s                      (bool)          [create]
          Consider attributes of shapes below transforms as well, except controlPoints.  Default: true.  (Not valid for
          pasteKeycmd.)
    
      - time : t                       (timerange)     [create]
          time uniquely representing a key (or key range) on a time-based animCurve.  Valid timeRanges include single values (-t
          10) or a string with a lower and upper bound, separated by a colon (-t 10:20
    
      - timeMultiple : tm              (float)         [create]
          If this flag is present, key times will be snapped to a multiple of the specified float value.
    
      - valueMultiple : vm             (float)         [create]
          If this flag is present, key values will be snapped to a multiple of the specified float value.                  Flag
          can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.snapKey`
    """

    pass


def setInfinity(*args, **kwargs):
    """
    Set the infinity type before (after) a paramCurve's first (last) keyframe. In query mode, return type is based on
    queried flag.
    
    Flags:
      - attribute : at                 (unicode)       [create]
          List of attributes to select
    
      - controlPoints : cp             (bool)          [create]
          This flag explicitly specifies whether or not to include the control points of a shape (see -sflag) in the list of
          attributes. Default: false.  (Not valid for pasteKeycmd.)
    
      - hierarchy : hi                 (unicode)       [create]
          Hierarchy expansion options.  Valid values are above,below,both,and none.(Not valid for pasteKeycmd.)
    
      - postInfinite : poi             (unicode)       [create,query]
          Set the infinity type after a paramCurve's last keyframe. Valid values are constant, linear, cycle, cycleRelative,
          oscillate.
    
      - preInfinite : pri              (unicode)       [create,query]
          Set the infinity type before a paramCurve's first keyframe. Valid values are constant, linear, cycle, cycleRelative,
          oscillate.
    
      - shape : s                      (bool)          [create]
          Consider attributes of shapes below transforms as well, except controlPoints.  Default: true.  (Not valid for
          pasteKeycmd.)Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.setInfinity`
    """

    pass


def timeEditorPanel(*args, **kwargs):
    """
    Time Editor - non-linear animation editor
    
    Flags:
      - activeClipEditMode : ace       (int)           [query,edit]
          Set the appropriate clip edit mode for the editor. 0: Default Mode1: Trim Mode2: Scale Mode3: Loop Mode4: Hold Mode
    
      - activeTabRootClipId : atr      (bool)          [query]
          Get the clip id for which current active tab has been opened. In case of main tab, this will return -1 meaning there is
          no root clip.
    
      - activeTabTime : att            (bool)          [query]
          Get current time displayed inside the active tab. This will be global time in case of the main tab and local time for
          others.
    
      - activeTabView : atv            (int)           [query,edit]
          Get/set the index of the tab widget's (active) visible tab. Note: the index is zero-based.
    
      - autoFit : af                   (unicode)       [query,edit]
          on | off | tgl Auto fit-to-view.
    
      - contextMenu : cm               (bool)          []
    
      - control : ctl                  (bool)          [query]
          Query only. Returns the top level control for this editor. Usually used for getting a parent to attach popup menus.
          Caution: It is possible for an editor to exist without a control. The query will return NONEif no control is present.
    
      - defineTemplate : dt            (unicode)       [create]
          Puts the command in a mode where any other flags and args are parsed and added to the command template specified in the
          argument. They will be used as default arguments in any subsequent invocations of the command when templateName is set
          as the current template.
    
      - displayActiveKeyTangents : dat (unicode)       [edit]
          on | off | tgl Display active key tangents in the editor.
    
      - displayActiveKeys : dak        (unicode)       [edit]
          on | off | tgl Display active keys in the editor.
    
      - displayInfinities : di         (unicode)       [edit]
          on | off | tgl Display infinities in the editor.
    
      - displayKeys : dk               (unicode)       [edit]
          on | off | tgl Display keyframes in the editor.
    
      - displayTangents : dtn          (unicode)       [edit]
          on | off | tgl Display tangents in the editor.
    
      - displayValues : dv             (unicode)       [edit]
          on | off | tgl Display active keys and tangents values in the editor.
    
      - docTag : dtg                   (unicode)       [create,query,edit]
          Attaches a tag to the editor.
    
      - exists : ex                    (bool)          [create]
          Returns whether the specified object exists or not. Other flags are ignored.
    
      - filter : f                     (unicode)       [create,query,edit]
          Specifies the name of an itemFilter object to be used with this editor. This filters the information coming onto the
          main list of the editor.
    
      - focusTrack : ft                (unicode)       []
    
      - forceMainConnection : fmc      (unicode)       [create,query,edit]
          Specifies the name of a selectionConnection object that the editor will use as its source of content. The editor will
          only display items contained in the selectionConnection object. This is a variant of the -mainListConnection flag in
          that it will force a change even when the connection is locked. This flag is used to reduce the overhead when using the
          -unlockMainConnection , -mainListConnection, -lockMainConnection flags in immediate succession.
    
      - groupIdForTabView : gtv        (int)           [query]
          Get the group clip id for the given tab view index. To specify the tab index, this flag must appear before the -query
          flag.
    
      - highlightConnection : hlc      (unicode)       [create,query,edit]
          Specifies the name of a selectionConnection object that the editor will synchronize with its highlight list. Not all
          editors have a highlight list. For those that do, it is a secondary selection list.
    
      - keyingTarget : kt              (int)           [query,edit]
          Set keying target to specified clip ID. If keying into layer, '-layer' flag must be used. In query mode, the clip id is
          omitted, and the name of the keying target will be returned.
    
      - layerId : l                    (int)           [edit]
          Indicate layer ID of keying target.
    
      - lockMainConnection : lck       (bool)          [create,edit]
          Locks the current list of objects within the mainConnection, so that only those objects are displayed within the editor.
          Further changes to the original mainConnection are ignored.
    
      - lookAt : la                    (unicode)       [edit]
          all | selected | currentTime FitView helpers.
    
      - mainListConnection : mlc       (unicode)       [create,query,edit]
          Specifies the name of a selectionConnection object that the editor will use as its source of content. The editor will
          only display items contained in the selectionConnection object.
    
      - menu : m                       (script)        [create]
          Specify a script to be run when the editor is created.  The function will be passed one string argument which is the new
          editor's name.
    
      - minClipWidth : mcw             (int)           []
    
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
    
      - setToPrevClipEditMode : spe    (bool)          [edit]
          Revert to previous clip edit mode.
    
      - snapTime : st                  (unicode)       [query,edit]
          none | integer | keyframe Keyframe move snap in time.
    
      - snapToClip : stc               (bool)          [query,edit]
          Enable/Disable snap-to-clip option in Time Editor while manipulating and drag-and-drop clips.
    
      - snapToFrame : stf              (bool)          [query,edit]
          Enable/Disable snap-to-frame option in Time Editor while manipulating and drag-and-drop clips.
    
      - snapTolerance : sto            (int)           [query,edit]
          Set the tolerance value for snapping.
    
      - snapValue : sv                 (unicode)       [query,edit]
          none | integer | keyframe Keyframe move snap in values.
    
      - stateString : sts              (bool)          [query]
          Query only flag. Returns the MEL command that will create an editor to match the current editor state. The returned
          command string uses the string variable $editorName in place of a specific name.
    
      - tabView : tv                   (int)           [edit]
          Create a tab view for the given group clip ID.
    
      - timeCursor : tc                (bool)          [query,edit]
          Activate the time cursor in Time Editor for scrubbing.
    
      - togglekeyview : tkv            (bool)          []
    
      - unParent : up                  (bool)          [create,edit]
          Specifies that the editor should be removed from its layout. This cannot be used in query mode.
    
      - unlockMainConnection : ulk     (bool)          [create,edit]
          Unlocks the mainConnection, effectively restoring the original mainConnection (if it is still available), and dynamic
          updates.
    
      - updateMainConnection : upd     (bool)          [create,edit]
          Causes a locked mainConnection to be updated from the orginal mainConnection, but preserves the lock state.
    
      - useTemplate : ut               (unicode)       [create]
          Forces the command to use a command template other than the current one.                  Flag can have multiple
          arguments, passed either as a tuple or a list.
    
      - viewLeft : vl                  (bool)          []
    
      - viewRight : vr                 (bool)          []
    
    
    Derived from mel command `maya.cmds.timeEditorPanel`
    """

    pass


def ikHandle(*args, **kwargs):
    """
    The handle command is used to create, edit, and query a handle within Maya.  The standard edit (-e) and query (-q) flags
    are used for edit and query functions. If there are 2 joints selected and neither -startJoint nor -endEffector flags are
    not specified, then the handle will be created from the selected joints. If a single joint is selected and neither
    -startJoint nor -endEffector flags are specified, then the handle will be created with the selected joint as the end-
    effector and the start joint will be the top of the joint chain containing the end effector. The default values of the
    flags are: -name ikHandle#-priority 1-weight 1.0-positionWeight 1.0-solver ikRPsolver-forceSolver on-
    snapHandleFlagToggle on-sticky off-createCurve true-simplifyCurve true-rootOnCurve true-twistType linear-createRootAxis
    false-parentCurve true-snapCurve false-numSpans 1-rootTwistMode false.These attributes can be specified in creation
    mode, edited in edit mode (-e) or queried in query mode (-q).
    
    Modifications:
      - returns a PyNode object for flags: (query and endEffector)
      - returns a list of PyNode objects for flags: (query and jointList)
    
    Flags:
      - autoPriority : ap              (bool)          [edit]
          Specifies that this handle's priority is assigned automatically.  The assigned priority will be based on the hierarchy
          distance from the root of the skeletal chain to the start joint of the handle.
    
      - connectEffector : ce           (bool)          [create,edit]
          This option is set to true as default, meaning that end-effector translate is connected with the endJoint translate.
    
      - createCurve : ccv              (bool)          [create]
          Specifies if a curve should automatically be created for the ikSplineHandle.
    
      - createRootAxis : cra           (bool)          [create]
          Specifies if a root transform should automatically be created above the joints affected by the ikSplineHandle. This
          option is used to prevent the root flipping singularity on a motion path.
    
      - curve : c                      (PyNode)        [create,query,edit]
          Specifies the curve to be used by the ikSplineHandle. Joints will be moved to align with this curve. This flag is
          mandatory if you use the -freezeJoints option.
    
      - disableHandles : dh            (bool)          [edit]
          set given handles to full fk (ikBlend attribute = 0.0)
    
      - enableHandles : eh             (bool)          [edit]
          set given handles to full ik (ikBlend attribute = 1.0)
    
      - endEffector : ee               (unicode)       [create,query,edit]
          Specifies the end-effector of the handle's joint chain. The end effector may be specified with a joint or an end-
          effector.  If a joint is specified, an end-effector will be created at the same position as the joint and this new end-
          effector will be used as the end-effector.
    
      - exists : ex                    (unicode)       [edit]
          Indicates if the specified handle exists or not.
    
      - forceSolver : fs               (bool)          [create,query,edit]
          Forces the solver to be used everytime. It could also be known as animSticky. So, after you set the first key the handle
          is sticky.
    
      - freezeJoints : fj              (bool)          [create,edit]
          Forces the curve, specfied by -curve option, to align itself along the existing joint chain. When false, or unspecified,
          the joints will be moved to positions along the specified curve.
    
      - jointList : jl                 (bool)          [query]
          Returns the list of joints that the handle is manipulating.
    
      - name : n                       (unicode)       [create,query,edit]
          Specifies the name of the handle.
    
      - numSpans : ns                  (int)           [create]
          Specifies the number of spans in the automatically generated curve of the ikSplineHandle.
    
      - parentCurve : pcv              (bool)          [create]
          Specifies if the curve should automatically be parented to the parent of the first joint affected by the ikSplineHandle.
    
      - positionWeight : pw            (float)         [create,query,edit]
          Specifies the position/orientation weight of a handle. This is used to compute the distancebetween the goal position and
          the end-effector position.  A positionWeight of 1.0 computes the distance as the distance between positions only and
          ignores the orientations.  A positionWeight of 0.0 computes the distance as the distance between the orientations only
          and ignores the positions.  A positionWeight of 0.5 attempts to weight the distances equally but cannot actually compute
          this due to unit differences. Because there is no way to add linear units and angular units.
    
      - priority : p                   (int)           [create,query,edit]
          Sets the priority of the handle.  Logically, all handles with a lower number priority are solved before any handles with
          a higher numbered priority.  (All handles of priority 1 are solved before any handles of priority 2 and so on.)  Handle
          priorities must be ] 0.
    
      - rootOnCurve : roc              (bool)          [create,query,edit]
          Specifies if the root is locked onto the curve of the ikSplineHandle.
    
      - rootTwistMode : rtm            (bool)          [create,query,edit]
          Specifies whether the start joint is allowed to twist or not. If not, then the required twist is distributed over the
          remaining joints. This applies to all the twist types.
    
      - setupForRPsolver : srp         (bool)          [edit]
          If the flag is set and ikSolver is ikRPsolver, call RPRotateSetup for the new ikHandle. It is for ikRPsolver only.
    
      - simplifyCurve : scv            (bool)          [create]
          Specifies if the ikSplineHandle curve should be simplified.
    
      - snapCurve : snc                (bool)          [create]
          Specifies if the curve should automatically snap to the first joint affected by the ikSplineHandle.
    
      - snapHandleFlagToggle : shf     (bool)          [create,query,edit]
          Specifies that the handle position should be snapped to the end-effector position if the end-effector is moved by the
          user.  Setting this flag on allows you to use forward kinematics to pose or adjust your skeleton and then to animate it
          with inverse kinematics.
    
      - snapHandleToEffector : see     (bool)          [edit]
          All handles are immediately moved so that the handle position and orientation matches the end-effector position and
          orientation.
    
      - solver : sol                   (unicode)       [create,query,edit]
          Specifies the solver.  The complete list of available solvers may not be known until run-time because some of the
          solvers may be implemented as plug-ins.  Currently the only valid solver are ikRPsolver, ikSCsolver and ikSplineSolver.
    
      - startJoint : sj                (unicode)       [create,query,edit]
          Specifies the start joint of the handle's joint chain.
    
      - sticky : s                     (unicode)       [create,query,edit]
          Specifies that this handle is sticky. Valid values are off, sticky, superSticky. Sticky handles are solved when the
          skeleton is being manipulated interactively.  If a character has sticky feet, the solver will attempt to keep them in
          the same position as the user moves the character's root.  If they were not sticky, they would move along with the root.
    
      - twistType : tws                (unicode)       [create,query,edit]
          Specifies the type of interpolation to be used by the ikSplineHandle.  The interpolation options are linear, easeIn,
          easeOut, and easeInOut.
    
      - weight : w                     (float)         [create,query,edit]
          Specifies the handles weight in error calculations.  The weight only applies when handle goals are in conflict and
          cannot be solved simultaneously.  When this happens, a solution is computed that weights the distancefrom each goal to
          the solution by the handle's weight and attempts to minimize this value.  The weight must be ]= 0.                  Flag
          can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.ikHandle`
    """

    pass


def bufferCurve(*args, **kwargs):
    """
    This command operates on a keyset.  A keyset is defined as a group of keys within a specified time range on one or more
    animation curves. The animation curves comprising a keyset depend on the value of the -animationflag: keysOrObjects: Any
    active keys, when no target objects or -attribute flags appear on the command line, orAll animation curves connected to
    all keyframable attributes of objects specified as the command line's targetList, when there are no active keys.keys:
    Only act on active keys or tangents. If there are no active keys or tangents, don't do anything. objects: Only act on
    specified objects.  If there are no objects specified, don't do anything. Note that the -animationflag can be used to
    override the curves uniquely identified by the multi-use -attributeflag, which takes an argument of the form
    attributeName, such as translateX. Keys on animation curves are identified by either their time values or their indices.
    Times and indices can be given individually or as part of a list or range. -time 10palmeans the key at frame 10 (PAL
    format).-time 1.0sec -time 15ntsc -time 20means the keys at time 1.0 second, frame 15 (in NTSC format), and time 20 (in
    the currently defined global time unit).-time 10:20means all keys in the range from 10 to 20, inclusive, in the current
    time unit.Omitting one end of a range means go to infinity, as in the following examples: -time 10:means all keys from
    time 10 (in the current time unit) onwards.-time :10means all keys up to (and including) time 10 (in the current time
    unit).-time :is a short form to specify all keys.-index 0means the first key of each animation curve. (Indices are
    0-based.)-index 2 -index 5 -index 7means the 3rd, 6th, and 8th keys.-index 1:5means the 2nd, 3rd, 4th, 5th, and 6th keys
    of each animation curve.This command helps manage buffer curve for animated objects
    
    Flags:
      - animation : an                 (unicode)       [create]
          Where this command should get the animation to act on.  Valid values are objects,keys,and keysOrObjectsDefault:
          keysOrObjects.(See Description for details.)
    
      - attribute : at                 (unicode)       [create]
          List of attributes to select
    
      - controlPoints : cp             (bool)          [create]
          This flag explicitly specifies whether or not to include the control points of a shape (see -sflag) in the list of
          attributes. Default: false.  (Not valid for pasteKeycmd.)
    
      - exists : ex                    (bool)          [query]
          Returns true if a buffer curve currently exists on the specified attribute; false otherwise.
    
      - float : f                      (floatrange)    [create]
          value uniquely representing a non-time-based key (or key range) on a time-based animCurve.  Valid floatRange include
          single values (-f 10) or a string with a lower and upper bound, separated by a colon (-f 10:20
    
      - hierarchy : hi                 (unicode)       [create]
          Hierarchy expansion options.  Valid values are above,below,both,and none.(Not valid for pasteKeycmd.)
    
      - includeUpperBound : iub        (bool)          [create]
          When the -t/time or -f/float flags represent a range of keys, this flag determines whether the keys at the upper bound
          of the range are included in the keyset. Default value: true.  This flag is only valid when the argument to the -t/time
          flag is a time range with a lower and upper bound.  (When used with the pasteKeycommand, this flag refers only to the
          time range of the target curve that is replaced, when using options such as replace,fitReplace,or scaleReplace.This flag
          has no effect on the curve pasted from the clipboard.)
    
      - index : index                  (int)           [create]
          index of a key on an animCurve
    
      - overwrite : ov                 (bool)          [create]
          Create a buffer curve.  truemeans create a buffer curve whether or not one already existed.  falsemeans if a buffer
          curve exists already then leave it alone.  If no flag is specified, then the command defaults to -overwrite false
    
      - shape : s                      (bool)          [create]
          Consider attributes of shapes below transforms as well, except controlPoints.  Default: true.  (Not valid for
          pasteKeycmd.)
    
      - swap : sw                      (bool)          [create]
          For animated attributes which have buffer curves, swap the buffer curve with the current animation curve
    
      - time : t                       (timerange)     [create]
          time uniquely representing a key (or key range) on a time-based animCurve.  Valid timeRanges include single values (-t
          10) or a string with a lower and upper bound, separated by a colon (-t 10:20
    
      - useReferencedCurve : urc       (bool)          [create,query]
          In create mode, sets the buffer curve to the referenced curve. Curves which are not from file references will ignore
          this flag. In query mode, returns true if the selected keys are displaying their referenced curve as the buffer curve,
          and false if they are not.                  Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.bufferCurve`
    """

    pass


def playblast(*args, **kwargs):
    """
    This command playblasts the current playback range. Sound is optional. Note that the playblast command registers a
    condition called playblastingso that users can monitor whether playblasting is occurring. You may monitor the condition
    using the API (MConditionMessage) or a script (scriptJob and condition commands).
    
    Flags:
      - activeEditor : ae              (bool)          [create]
          This flag will return the current model editor that would be used for playblast. It does not invoke playblast itself.
    
      - cameraSetup : cs               (unicode, unicode) [create]
          Information about camera setup. The first string defines a camera setup MEL procedure. The camera setup procedure will
          be invoked before executing a playblast. The second string argument which is used as a camera identifier and is appended
          to the root file name to specify the final output file name(s). The command will fail there is not a pair of strings
          supplied to the argument.
    
      - clearCache : cc                (bool)          [create]
          When true, all previous temporary playblast files will be deleted before the new playblast files are created and the
          remaining temporary playblast files will be deleted when the application quits. Any playblast files that were explicitly
          given a name by the user will not be deleted.
    
      - codecOptions : co              (bool)          [create]
          Brings up the OS specific dialog for setting playblast codec options, and does not run the playblast.
    
      - combineSound : csd             (bool)          [create]
          Combine the trax sounds into a single track. This might force a resampling of the sound if the sound paramters don't
          match up.
    
      - completeFilename : cf          (unicode)       [create]
          When set, this string specifies the exact name of the output image. In contrast with the -f/filename flag,
          -cf/completeFilename does not append any frame number or extension string at the end of the filename. Additionally,
          playblast will not delete the image from disk after it is displayed. This flag should not be used in conjunction with
          -f/filename.
    
      - compression : c                (unicode)       [create]
          Specify the compression to use for the movie file.  To determine which settings are available on your system, use the
          `playblast -options` command. This will display a system-specific dialog with supported compression formats. When the
          'format' flag is 'image', this flag is used to pass in the desired image format. If the format is 'image' and the
          compression flag is ommitted, the output format specified via the Render Globals preference (see -format) will be used.
          If compression is set to 'none', the iff image format will be used.
    
      - editorPanelName : epn          (unicode)       [create]
          This optional flag specifies the name of the model editor or panel, which is to be used for playblast. The current model
          editor or panel won't be used for playblast unless its name is specified. Flag usage is specific to invoking playblast.
    
      - endTime : et                   (time)          [create]
          Specify the end time of the playblast.  Default is the end time of the playback range displayed in the Time Slider.
          Overridden by -frame.
    
      - filename : f                   (unicode)       [create]
          The filename to use for the output of this playblast. If the file already exists, a confirmation box will be displayed
          if playblast is performed interactively.  If playblast is executed from the command line and the file already exists, it
          will abort.
    
      - forceOverwrite : fo            (bool)          [create]
          Overwrite existing playblast files which may have the the same name as the one specified with the -fflag
    
      - format : fmt                   (unicode)       [create]
          The format for the playblast output. ValueDescriptionmovieThis option selects a platform-specific default movie
          format.On Linux and Mac OSX the default movie format is Quicktime.On Windows the default movie format is Audio Video
          Interleave. aviSet the format to Audio Video Interleave (Windows only)qtSet the format to QuickTime (all
          platforms).avfoundationWrite movie by AVFoundation (Mac only).imageOutputs a sequence of image files.The image format
          will be the Output Format specified using Window RenderEditors RenderSettings CommonTab. The resulting files use the
          value of the -fflag as a prefix, with an appended frame number, as in myFile.0007.iffiffSame as imageThe default value
          of the -fmt/format flag is movie. Depending on the selected format, a platform-specific default application will be used
          to view results. For image sequences, the default application is fcheck. For movies, the default application is Windows
          Media Player (on Windows), Quicktime Player (on Mac OSX), and Lqtplay (on Linux). Users can specify different
          applications via Maya's application preferences.
    
      - frame : fr                     (time)          [create]
          List of frames to blast. One frame specified per flag. The frames can be specified in any order but will be output in an
          ordered sequence. When specified this flag will override any start/end range
    
      - framePadding : fp              (int)           [create]
          Number of zeros used to pad file name. Typically set to 4 to support fcheck.
    
      - height : h                     (int)           [create]
          Height of the final image. This value will be clamped if larger than the width of the active window.Windows: If not
          using fcheck, the width and height must each be divisible by 4.
    
      - indexFromZero : ifz            (bool)          [create]
          Output frames starting with file.0000.ext and incrementing by one. Typically frames use the Maya time as their frame
          number. This option can only be used for frame based output formats.
    
      - offScreen : os                 (bool)          [create]
          When set, this toggle allow playblast to use an offscreen buffer to render the view. This allows playblast to work when
          the application is iconified, or obscured.
    
      - options : o                    (bool)          [create]
          Brings up a dialog for setting playblast options, and does not run the playblast.
    
      - percent : p                    (int)           [create]
          Percentage of current view size  to use during blasting. Accepted values are integers between 10 and 100.  All other
          values are clamped to be within this range.  A value of 25 means 1/4 of the  current view size; a  value of 50  means
          half the current view size; a value of 100 means full size.  (Default is 50.)
    
      - quality : qlt                  (int)           [create]
          Specify the compression quality factor to use for the movie file. Value should be in the 0-100 range
    
      - rawFrameNumbers : rfn          (bool)          [create]
          Playblast typically numbers its frames sequentially, starting at zero. This flag will override the default action and
          frames will be numbered using the actual frames specified by the -frame or -startFrame/-endFrame flags.
    
      - replaceAudioOnly : rao         (bool)          [create]
          When set, this string dictates that only the audio will be replaced when the scene is re-playblasted.
    
      - replaceEndTime : ret           (time)          [create]
          Specify the end time of a replayblast of an existing playblast.  Default is the start time of the playback range
          displayed in the Time Slider. Overridden by -frame.
    
      - replaceFilename : rf           (bool)          [create]
          When set, this string specifies the name of an input playblast file which will have frames replaced according to the
          replace start and end times.
    
      - replaceStartTime : rst         (time)          [create]
          Specify the start time of a replayblast of an existing playblast.  Default is the start time of the playback range
          displayed in the Time Slider. Overridden by -frame.
    
      - sequenceTime : sqt             (bool)          [create]
          Use sequence time
    
      - showOrnaments : orn            (bool)          [create]
          Sets whether or not model view ornaments (e.g. the axis icon) should be displayed
    
      - sound : s                      (unicode)       [create]
          Specify the sound node to be used during playblast
    
      - startTime : st                 (time)          [create]
          Specify the start time of the playblast.  Default is the start time of the playback range displayed in the Time Slider.
          Overridden by -frame.
    
      - useTraxSounds : uts            (bool)          []
    
      - viewer : v                     (bool)          [create]
          Specify whether a viewer should be launched for the playblast.  Default is true.  Runs fcheckwhen -fmt is image. The
          player for movie files depends on the OS: Windows uses Microsoft Media Player, Irix uses movieplayer, OSX uses
          QuickTime.
    
      - width : w                      (int)           [create]
          Width of the final image. This value will be clamped if larger than the width of the active window.Windows: If not using
          fcheck, the width and height must each be divisible by 4.
    
      - widthHeight : wh               (int, int)      [create]
          Final image's width and height. Values larger than the dimensions of the active window are clamped. A width and height
          of 0 means to use the window's current size.Windows: If not using fcheck, the width and height must each be divisible by
          4.                  Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.playblast`
    """

    pass


def listAnimatable(*args, **kwargs):
    """
    This command list the animatable attributes of a node.  Command flags allow filtering by the current manipulator, or
    node type.
    
    Modifications:
        - returns an empty list when the result is None
        - returns wrapped classes
    
    Flags:
      - active : act                   (bool)          [create]
          This flag is obsolete and no longer supported.
    
      - manip : m                      (bool)          [create]
          Return only those attributes affected by the current manip. If there is no manip active and any other flags are
          specified, output is the same as if the -manipflag were not present.
    
      - manipHandle : mh               (bool)          [create]
          Return only those attributes affected by the current manip handle. If there is no manip handle active and any other
          flags are specified, output is the same as if the -manipHandleflag were not present.
    
      - shape : s                      (bool)          [create]
          This flag is obsolete and no longer supported.
    
      - type : typ                     (bool)          [create]
          Instead of returning attributes, Return the types of nodes that are currently animatable.                  Flag can have
          multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.listAnimatable`
    """

    pass


def clipSchedulerOutliner(*args, **kwargs):
    """
    This command creates/edits/queries a clip scheduler outliner control.
    
    Flags:
      - annotation : ann               (unicode)       [create,query,edit]
          Annotate the control with an extra string value.
    
      - backgroundColor : bgc          (float, float, float) [create,query,edit]
          The background color of the control. The arguments correspond to the red, green, and blue color components. Each
          component ranges in value from 0.0 to 1.0. When setting backgroundColor, the background is automatically enabled, unless
          enableBackground is also specified with a false value.
    
      - clipScheduler : cs             (unicode)       [edit]
          Name of the clip scheduler for which to display information.
    
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
    
    
    Derived from mel command `maya.cmds.clipSchedulerOutliner`
    """

    pass


def copySkinWeights(*args, **kwargs):
    """
    Command to copy or mirror the skinCluster weights accross one  of the three major axes.  The command can be used to
    mirror  weights either from one surface to another or within the  same surface.              In query mode, return type
    is based on queried flag.
    
    Flags:
      - destinationSkin : ds           (unicode)       [create,query,edit]
          Specify the destination skin shape
    
      - influenceAssociation : ia      (unicode)       [create,query,edit]
          The influenceAssociation flag controls how the influences on the source and target skins are matched up. The flag can be
          included multiple times to specify multiple association schemes that will be invoked one after the other until all
          influences have been matched up. Supported values are closestJoint, closestBone, label, name, oneToOne. The default is
          closestJoint.
    
      - mirrorInverse : mi             (bool)          [create,query,edit]
          Values are mirrored from the positive side to the negative.  If this flag is used then the direction is inverted.
    
      - mirrorMode : mm                (unicode)       [create,query,edit]
          The mirrorMode flag defines the plane of mirroring (XY, YZ, or XZ) when the mirror flag is used. The default plane is
          XY.
    
      - noBlendWeight : nbw            (bool)          [create,query,edit]
          When the no blend flag is used, the blend weights on the skin cluster will not be copied across to the destination.
    
      - noMirror : nm                  (bool)          [create,query,edit]
          When the no mirror flag is used, the weights are copied instead of mirrored.
    
      - normalize : nr                 (bool)          [create,query,edit]
          Normalize the skin weights.
    
      - sampleSpace : spa              (int)           [create,query,edit]
          Selects which space the attribute transfer is performed in. 0 is world space, 1 is model space. The default is world
          space.
    
      - smooth : sm                    (bool)          [create,query,edit]
          When the smooth flag is used, the weights are smoothly interpolated between the closest vertices, instead of assigned
          from the single closest.
    
      - sourceSkin : ss                (unicode)       [create,query,edit]
          Specify the source skin shape
    
      - surfaceAssociation : sa        (unicode)       [create,query,edit]
          The surfaceAssociation flag controls how the weights are transferred between the surfaces: closestPoint, rayCast, or
          closestComponent. The default is closestComponent.
    
      - uvSpace : uv                   (unicode, unicode) [create,query,edit]
          The uvSpace flag indicates that the weight transfer should occur in UV space, based on the source and destination UV
          sets specified.                               Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.copySkinWeights`
    """

    pass


def sound(*args, **kwargs):
    """
    Creates an audio node which can be used with UI commands such as soundControl or timeControl which support sound
    scrubbing and sound during playback.
    
    Flags:
      - endTime : et                   (time)          [create,query,edit]
          Time at which to end the sound.
    
      - file : f                       (unicode)       [create,query,edit]
          Name of sound file.
    
      - length : l                     (bool)          [query]
          Query the length (in the current time unit) of the sound.
    
      - mute : m                       (bool)          [create,query,edit]
          Mute the audio clip.
    
      - name : n                       (unicode)       [create,query,edit]
          Name to give the resulting audio node.
    
      - offset : o                     (time)          [create,query,edit]
          Time at which to start the sound.
    
      - sourceEnd : se                 (time)          [create,query,edit]
          Time offset from the start of the sound file at which to end the sound.
    
      - sourceStart : ss               (time)          [create,query,edit]
          Time offset from the start of the sound file at which to start the sound.                  Flag can have multiple
          arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.sound`
    """

    pass


def timeEditorClipOffset(*args, **kwargs):
    """
    This command is used to compute an offset to apply on a source clip in order to automatically align it to a destination
    clip at a specified match element. For this command to work, offset objects must be specified for the character.
    In query mode, return type is based on queried flag.
    
    Flags:
      - applyToAllRoots : atr          (bool)          [create]
          Apply root offsets to all roots in the population. However, if the root objects are specified by rootObj flag, this flag
          will be ignored.
    
      - clipId : id                    (int)           [create,edit]
          ID of a clip to be edited.
    
      - matchClipId : mci              (int)           [create]
          Specify the ID of a clip to match.
    
      - matchDstTime : mdt             (time)          [create]
          Specify the time on target clip.
    
      - matchObj : mob                 (PyNode)        [create]
          Specify the object to match.
    
      - matchOffsetRot : mor           (bool)          [query]
          Get the rotation of the match offset matrix.
    
      - matchOffsetTrans : mot         (bool)          [query]
          Get the translation of the match offset matrix.
    
      - matchPath : mpt                (unicode)       [create]
          Full path of the clip a clip to match. For example: composition1|track1|Group|track2|clip1
    
      - matchRotOp : mro               (int)           [create]
          Specify the option for matching rotation. 0 : full - All rotation components are matched1 : Y    - Y component is
          matched2 : none - No rotation matching
    
      - matchSrcTime : mst             (time)          [create]
          Specify the time on source clip.
    
      - matchTransOp : mto             (int)           [create]
          Specify the option for matching translation. 0 : full - All translation components are matched1 : XZ   - X and Z
          components are matched2 : none - No translation matching
    
      - offsetTransform : oft          (bool)          [create,query]
          Create/get an offset for the specified clip.
    
      - path : pt                      (unicode)       [create,edit]
          Full path of a clip to be edited. For example: composition1|track1|group; composition1|track1|group|track2|clip1. In
          query mode, this flag can accept a value.
    
      - resetMatch : rsm               (int)           [create]
          Specifiy clip ID to remove offset.
    
      - resetMatchPath : rmp           (unicode)       [create]
          Full path of a clip to remove offset. For example: composition1|track1|Group|track2|clip1
    
      - rootObj : rob                  (PyNode)        [create]
          Specify the root objects. If specified, this flag will take precedence over applyToAllRoots flag.
    
      - upVectorX : upx                (float)         [create]
          Specify the X coordinate of the up vector.
    
      - upVectorY : upy                (float)         [create]
          Specify the Y coordinate of the up vector.
    
      - upVectorZ : upz                (float)         [create]
          Specify the Z coordinate of the up vector.                                 Flag can have multiple arguments, passed
          either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.timeEditorClipOffset`
    """

    pass


def autoKeyframe(*args, **kwargs):
    """
    With no flags, this command will set keyframes on all attributes that have been modified since an autoKeyframe -state
    oncommand was issued.  To stop keeping track of modified attributes, use autoKeyframe -state offautoKeyframe does not
    create new animation curves.  An attribute must have already been keyframed (with the setKeyframe command) for
    autoKeyframe to  add new keyframes for modified attributes. You can also query the current state of autoKeyframing with
    autoKeyframe -query -state.
    
    Flags:
      - characterOption : co           (unicode)       [create,query,edit]
          Valid options are: standard, all. Dictates whether when auto-keying characters the auto-key works as usual or whether it
          keys all of the character attributes. Default is standard.
    
      - noReset : nr                   (bool)          [create,edit]
          Must be used in conjunction with the state/st flag. When noReset/nr is specified, the list of plugs to be autokeyed is
          not cleared when the state changes
    
      - state : st                     (bool)          [create,query,edit]
          turns on/off remembering of modified attributes                  Flag can have multiple arguments, passed either as a
          tuple or a list.
    
    
    Derived from mel command `maya.cmds.autoKeyframe`
    """

    pass


def defineDataServer(*args, **kwargs):
    """
    Connects to the specified data servername, creating a named device which then can be attached to device handlers. When
    the device is defined, it queries queries the server for data axis information.  The CapChannelspresent are represented
    as axis in form channelName.usagefor scalar channels and channelName.componentfor compound channels. See
    listInputDeviceAxesto list axis names. Note that undoing defineDataServer -d myDevice-s myServerdoes not break the
    connection with the data server until it cannot be redone.  Executing any other command (sphere for example) will cause
    this to occur.  Similarly, the command defineDataServer -d myDevice-u does not break the connection with the data server
    until it cannot be undone.  Either flushUndo, or the 'defineDataServer' command fallingoff the end of the undo queue
    causes this to occur, and the connection. to be broken. No return value.
    
    Flags:
      - device : d                     (unicode)       [create]
          specified the device name to be given to the server connection. device name must be unique or the command fails.
    
      - server : s                     (unicode)       [create]
          specifies the name of the server with which the define device connects, and can be specifiied in two ways  name-- the
          name of the server socketServer names of the form nameconnect to the server socket on the localhost corresponding to
          name.  If namedoes not begin with /, then /tmp/nameis used. This is the default behavior of most servers. If namebegins
          with /, namedenotes the full path to the socket. host:service- a udp service on the specified host.The servicecan be any
          one of a udp service name,a port number,or a named service of tcpmux,and they are found in that order. If hostis
          omitted, the localhost is used. In any case, if the server cannot be found, the device is not defined (created) and the
          command fails.
    
      - undefine : u                   (bool)          [create]
          undefines (destroys) the dataServer device, closing the connection with the server.                  Flag can have
          multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.defineDataServer`
    """

    pass


def geomBind(*args, **kwargs):
    """
    This command is used to compute weights using the GeomBind lib.                  In query mode, return type is based on
    queried flag.
    
    Flags:
      - bindMethod : bm                (int)           [create]
          Specifies which bind algorithm to use. By default, Geodesic Voxel will be used. Available algorithms are: 3 - Geodesic
          Voxel
    
      - falloff : fo                   (float)         [create,query,edit]
          Falloff controlling the bind stiffness. Valid values range from [0..1].
    
      - geodesicVoxelParams : gvp      (int, bool)     [create,query,edit]
          Specifies the geodesic voxel binding parameters. This flag is composed of three parameters: 0 - Maximum voxel grid
          resolution which must be a power of two. (ie. 64, 128, 256, etc. ) 1 - Performs a post voxel state validation when
          enabled. Default values are 256 true.
    
      - maxInfluences : mi             (int)           [create,query,edit]
          Specifies the maximum influences a vertex can have. By default, all influences are used (-1).
          Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.geomBind`
    """

    pass


def clipMatching(*args, **kwargs):
    """
    This command is used to compute an offset to apply on a source clip in order to automatically align it to a destination
    clip at a specified match element. For this command to work, offset objects must be specified for the character.
    
    Flags:
      - clipDst : cd                   (unicode, float) [create]
          The clip to match so that the source clip can be offsetted correctly.  This flag takes in a clip name and the percentage
          value ranging from 0.0 to 1.0 in order to have the source clip match at a certain time in the destination clip.
    
      - clipSrc : cs                   (unicode, float) [create]
          The clip to offset so that it aligns with the destination clip.  This flag takes in a clip name and the percentage value
          ranging from 0.0 to 1.0 in order to have it match at a certain time in the clip.
    
      - matchRotation : mr             (int)           [create]
          This flag sets the rotation match type. By default, it is set to not match the rotation. 0 - None 1 - Match full
          rotation 2 - Match projected rotation on ground plane
    
      - matchTranslation : mt          (int)           [create]
          This flag sets the translation match type. By default, it is set to not match the translation. 0 - None 1 - Match full
          translation 2 - Match projected translation on ground plane                                 Flag can have multiple
          arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.clipMatching`
    """

    pass


def scaleConstraint(*args, **kwargs):
    """
    Constrain an object's scale to the scale of the target object or to the average scale of a number of targets. A
    scaleConstraint takes as input one or more targetDAG transform nodes to which to scale the single constraint objectDAG
    transform node.  The scaleConstraint scales the constrained object at the weighted geometric mean of the world space
    target scale factors.
    
    Maya Bug Fix:
      - when queried, angle offsets would be returned in radians, not current angle unit
    
    Modifications:
      - added new syntax for querying the weight of a target object, by passing the constraint first::
    
            aimConstraint( 'pCube1_aimConstraint1', q=1, weight ='pSphere1' )
            aimConstraint( 'pCube1_aimConstraint1', q=1, weight =['pSphere1', 'pCylinder1'] )
            aimConstraint( 'pCube1_aimConstraint1', q=1, weight =[] )
    
    Flags:
      - layer : l                      (unicode)       [create,edit]
          Specify the name of the animation layer where the constraint should be added.
    
      - maintainOffset : mo            (bool)          [create]
          The offset necessary to preserve the constrained object's initial scale will be calculated and used as the offset.
    
      - name : n                       (unicode)       [create,query,edit]
          Sets the name of the constraint node to the specified name.  Default name is constrainedObjectName_constraintType
    
      - offset : o                     (float, float, float) [create,query,edit]
          Sets or queries the value of the offset. Default is 1,1,1.
    
      - remove : rm                    (bool)          [edit]
          removes the listed target(s) from the constraint.
    
      - scaleCompensate : sc           (bool)          [create,edit]
          Used only when constraining a joint. It specify if a scaleCompensate will be applied on constrained joint. If true it
          will connect Tjoint.aCompensateForParentScale to scaleContraint.aConstraintScaleCompensate.
    
      - skip : sk                      (unicode)       [create,edit]
          Specify the axis to be skipped. Valid values are x, y, zand none. During creation, noneis the default. This flag is
          multi-use.
    
      - targetList : tl                (bool)          [query]
          Return the list of target objects.
    
      - weight : w                     (float)         [create,query,edit]
          Sets the weight value for the specified target(s). If not given at creation time, the default value of 1.0 is used.
    
      - weightAliasList : wal          (bool)          [query]
          Returns the names of the attributes that control the weight of the target objects. Aliases are returned in the same
          order as the targets are returned by the targetList flag                  Flag can have multiple arguments, passed
          either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.scaleConstraint`
    """

    pass


def timeWarp(*args, **kwargs):
    """
    This command is used to create a time warp input to a set of animation curves.
    
    Flags:
      - deleteFrame : df               (int)           [edit]
          The flag value indicates the 0-based index of the warp frame to delete. This flag can only be used in edit mode.
    
      - frame : f                      (float)         [create,query,edit]
          In create and edit mode, this flag can be used to specify warp frames added to the warp operation. In query mode, this
          flag returns a list of the frame values where warping occurs. The moveFrame flag command can be used to query the
          associated warped values.
    
      - g : g                          (bool)          [create,query,edit]
          In create mode, creates a global time warp node which impacts every animated object in the scene. In query mode, returns
          the global time warp node. Note: only one global time warp can exist in the scene.
    
      - interpType : it                (int, unicode)  [create,query,edit]
          This flag can be used to set the interpolation type for a given span. Valid interpolation types are linear, easeIn and
          easeOut. When queried, it returns a string array of the interpolation types for the specified time warp.
    
      - moveFrame : mf                 (int, float)    [query,edit]
          This flag can be used to move a singular warp frame. The first value specified indicates the 0-based index of the warp
          frame to move. The second value indicates the new warp frame value. This flag can only be used in edit and query mode.
          When queried, it returns an array of the warped frame values.                                Flag can have multiple
          arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.timeWarp`
    """

    pass


def defineVirtualDevice(*args, **kwargs):
    """
    This command defines a virtual device. Virtual devices act like real devices and are useful to manipulate/playback data
    when an command device is not connected to the computer. In query mode, return type is based on queried flag.
    
    Flags:
      - axis : ax                      (int)           [create]
          Specifies the axis number of the channel. All children have their axis number determined by their parent's axis number
          and the width of the parent channel. If this flag is not used, the order of the channel determines the axis number.
    
      - channel : c                    (unicode)       [create]
          After a -create is started, channels may be added to the device definition. The channel string wil be the name of the
          channel being added to the device. The -channel flag must also be accompanied by the -usage flag and optionally by the
          -axis flag.
    
      - clear : cl                     (bool)          [create]
          The -clear option will end a device definition and throw away any defined channels.
    
      - create : cr                    (bool)          [create]
          Start defining a virtual device. If a device is currently being defined, the -create flag will produce an error.
    
      - device : d                     (unicode)       [create]
          The -device flag ends the device definition. All of the channels between the -create flag and the -device flag are added
          to the specified device. If that device already exists, the command will fail and the device should be redefined with
          another device name. To see the currently defined devices, use the listInputDevices command. The -device flag is also
          used with -undefine to undefine a virtual device.
    
      - parent : p                     (unicode)       [create]
          Specified the parent channel of the channel being defined. If the channel does not exist, or is an incompatible type,
          the command will fail.
    
      - undefine : u                   (bool)          [create]
          Undefines the device specified with the -device flag.
    
      - usage : use                    (unicode)       [create]
          The -usage option is required for every -channel flag. It describes what usage type the defined channel is. The usage
          types are: unknownscalarposrotposRotquaternionposQuaternionrotXYZrotYZXrotZXYrotXZYrotYXZrotZYXposRotXYZposRotYZXposRotZ
          XYposRotXZYposRotXZYposRotZYXposXposYposZrotXrotYrotZFlag can have multiple arguments, passed either as a tuple or a
          list.
    
    
    Derived from mel command `maya.cmds.defineVirtualDevice`
    """

    pass


def setKeyPath(*args, **kwargs):
    """
    The setKeyPath command either creates or edits the path (a nurbs curve) based on the current position of the selected
    object at the current time.
    
    
    Derived from mel command `maya.cmds.setKeyPath`
    """

    pass


def characterMap(*args, **kwargs):
    """
    This command is used to create a correlation between the attributes of 2 or more characters.
    
    Flags:
      - mapAttr : ma                   (unicode, unicode) [create,query,edit]
          In query mode, this flag can be used to query the mapping stored by the specified map node. It returns an array of
          strings. In non-query mode, this flag can be used to create a mapping between the specified character members. Any
          previous mapping on the attributes is removed in favor of the newly specified mapping.
    
      - mapMethod : mm                 (unicode)       [create]
          This is is valid in create mode only. It specifies how the mapping should be done. Valid options are: byNodeName,
          byAttrName, and byAttrOrder. byAttrOrderis the default. The flags mean the following: byAttrOrdermaps using the order
          that the character stores the attributes internally, byAttrNameuses the attribute name to find a correspondence,
          byNodeNameuses the node name \*and\* the attribute name to find a correspondence.
    
      - mapNode : mn                   (unicode, unicode) [create,query]
          This flag can be used to map all the attributes on the source node to their matching attributes on the destination node.
    
      - mapping : m                    (unicode)       [query]
          This flag is valid in query mode only. It must be used before the query flag with a string argument. It is used for
          querying the mapping for a particular attribute.  A string array is returned.
    
      - proposedMapping : pm           (bool)          [query]
          This flag is valid in query mode only. It is used to get an array of the mapping that the character map would prvide if
          called with the specified characters and the (optional) specified mappingMethod. If a character map exists on the
          characters, the map is not affected by the query operation.  A string array is returned.
    
      - unmapAttr : ua                 (unicode, unicode) [create,edit]
          This flag can be used to unmap the mapping stored by the specified map node.
    
      - unmapNode : umn                (unicode, unicode) [create]
          This flag can be used to unmap all the attributes on the source node to their matching attributes on the destination
          node. Note that mapped attributes which do not have matching names, will not be unmapped.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.characterMap`
    """

    pass


def mirrorJoint(*args, **kwargs):
    """
    This command will duplicate a branch of the skeleton from the selected joint symmetrically about a plane in world space.
    There are three mirroring modes(xy-, yz-, xz-plane).
    
    Flags:
      - mirrorBehavior : mb            (bool)          [create]
          The mirrorBehavior flag is used to specify that when performing the mirror, the joint orientation axes should be
          mirrored such that equal rotations on the original and mirrored joints will place the skeleton in a mirrored position
          (symmetric across the mirroring plane). Thus, animation curves from the original joints can be copied to the mirrored
          side to produce a similar (but symmetric) behavior. When mirrorBehavior is not specified, the joint orientation on the
          mirrored side will be identical to the source side.
    
      - mirrorXY : mxy                 (bool)          [create]
          mirror skeleton from the selected joint about xy-plane in world space.
    
      - mirrorXZ : mxz                 (bool)          [create]
          mirror skeleton from the selected joint about xz-plane in world space.
    
      - mirrorYZ : myz                 (bool)          [create]
          mirror skeleton from the selected joint about yz-plane in world space.
    
      - searchReplace : sr             (unicode, unicode) [create]
          After performing the mirror, rename the new joints by searching the name for the first specified string and replacing it
          with the second specified string.                  Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.mirrorJoint`
    """

    pass


def copyDeformerWeights(*args, **kwargs):
    """
    Command to copy or mirror the deformer weights accross one  of the three major axes.  The command can be used to mirror
    weights either from one surface to another or within the  same surface.                 In query mode, return type is
    based on queried flag.
    
    Flags:
      - destinationDeformer : dd       (unicode)       [create,query,edit]
          Specify the deformer used by the destination shape
    
      - destinationShape : ds          (unicode)       [create,query,edit]
          Specify the destination deformed shape
    
      - mirrorInverse : mi             (bool)          [create,query,edit]
          Values are mirrored from the positive side to the negative.  If this flag is used then the direction is inverted.
    
      - mirrorMode : mm                (unicode)       [create,query,edit]
          The mirrorMode flag defines the plane of mirroring (XY, YZ, or XZ) when the mirror flag is used. The default plane is
          XY.
    
      - noMirror : nm                  (bool)          [create,query,edit]
          When the no mirror flag is used, the weights are copied instead of mirrored.
    
      - smooth : sm                    (bool)          [create,query,edit]
          When the smooth flag is used, the weights are smoothly interpolated between the closest vertices, instead of assigned
          from the single closest.
    
      - sourceDeformer : sd            (unicode)       [create,query,edit]
          Specify the deformer whose weights should be mirrored.  When queried, returns the deformers used by the source shapes.
    
      - sourceShape : ss               (unicode)       [create,query,edit]
          Specify the source deformed shape
    
      - surfaceAssociation : sa        (unicode)       [create,query,edit]
          The surfaceAssociation flag controls how the weights are transferred between the surfaces: closestPoint, rayCast, or
          closestComponent. The default is closestComponent.
    
      - uvSpace : uv                   (unicode, unicode) [create,query,edit]
          The uvSpace flag indicates that the weight transfer should occur in UV space, based on the source and destination UV
          sets specified.                               Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.copyDeformerWeights`
    """

    pass


def polyUniteSkinned(*args, **kwargs):
    """
    Command to combine poly mesh objects (as polyUnite) while retaining the smooth skinning setup on the combined object.
    In query mode, return type is based on queried flag.
    
    Flags:
      - centerPivot : cp               (bool)          [create,query,edit]
          Set the resulting object's pivot to the center of the selected objects bounding box.
    
      - constructionHistory : ch       (bool)          [create,query,edit]
          Turn the construction history on or off.
    
      - mergeUVSets : muv              (int)           [create,query,edit]
          Specify how UV sets will be merged on the output mesh. The choices are 0 | 1 | 2. 0 = Do not merge. Each UV set on each
          mesh will become a new UV set in the output. 1 = Merge by name. UV sets with the same name will be merged. 2 = Merge by
          UV links. UV sets will be merged so that UV linking on the input meshes continues to work. The default is 1 (merge by
          name).
    
      - objectPivot : op               (bool)          [create,query,edit]
          Set the resulting object's pivot to last selected object's pivot.                                  Flag can have
          multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.polyUniteSkinned`
    """

    pass


def jointDisplayScale(*args, **kwargs):
    """
    This action modifies and queries the current display size of skelton joints. The joint display size is controlled by a
    scale factor; scale factor 1 puts the display size to its default, which is 1 in diameter. With the plain format, the
    float argument is the factor with respect to the default size. When -a/absolute is used, the float argument refers to
    the actual diameter of the joint display size. In query mode, return type is based on queried flag.
    
    Flags:
      - absolute : a                   (bool)          [create,query]
          Interpret the float argument as the actual display size as opposed to the scale factor.
    
      - ikfk : ik                      (bool)          [create,query]
          Set the display size of ik/fk skeleton joints.                  Flag can have multiple arguments, passed either as a
          tuple or a list.
    
    
    Derived from mel command `maya.cmds.jointDisplayScale`
    """

    pass


def aimConstraint(*args, **kwargs):
    """
    Constrain an object's orientation to point at a target object or at the average position of a number of targets. An
    aimConstraint takes as input one or more targetDAG transform nodes at which to aim the single constraint objectDAG
    transform node.  The aimConstraint orients the constrained object such that the aimVector (in the object's local
    coordinate system) points to the in weighted average of the world space position target objects.  The upVector (again
    the the object's local coordinate system) is aligned in world space with the worldUpVector.
    
    Maya Bug Fix:
      - when queried, angle offsets would be returned in radians, not current angle unit
    
    Modifications:
      - added new syntax for querying the weight of a target object, by passing the constraint first::
    
            aimConstraint( 'pCube1_aimConstraint1', q=1, weight ='pSphere1' )
            aimConstraint( 'pCube1_aimConstraint1', q=1, weight =['pSphere1', 'pCylinder1'] )
            aimConstraint( 'pCube1_aimConstraint1', q=1, weight =[] )
    
    Flags:
      - aimVector : aim                (float, float, float) [create,query,edit]
          Set the aim vector.  This is the vector in local coordinates that points at the target.  If not given at creation time,
          the default value of (1.0, 0.0, 0.0) is used.
    
      - layer : l                      (unicode)       [create,edit]
          Specify the name of the animation layer where the constraint should be added.
    
      - maintainOffset : mo            (bool)          [create]
          The offset necessary to preserve the constrained object's initial rotation will be calculated and used as the offset.
    
      - name : n                       (unicode)       [create,query,edit]
          Sets the name of the constraint node to the specified name.  Default name is constrainedObjectName_constraintType
    
      - offset : o                     (float, float, float) [create,query,edit]
          Sets or queries the value of the offset. Default is 0,0,0.
    
      - remove : rm                    (bool)          [edit]
          removes the listed target(s) from the constraint.
    
      - skip : sk                      (unicode)       [create,edit]
          Specify the axis to be skipped. Valid values are x, y, zand none. During creation, noneis the default.
    
      - targetList : tl                (bool)          [query]
          Return the list of target objects.
    
      - upVector : u                   (float, float, float) [create,query,edit]
          Set local up vector.  This is the vector in local coordinates that aligns with the world up vector.  If not given at
          creation time, the default value of (0.0, 1.0, 0.0) is used.
    
      - weight : w                     (float)         [create,query,edit]
          Sets the weight value for the specified target(s). If not given at creation time, the default value of 1.0 is used.
    
      - weightAliasList : wal          (bool)          [query]
          Returns the names of the attributes that control the weight of the target objects. Aliases are returned in the same
          order as the targets are returned by the targetList flag
    
      - worldUpObject : wuo            (PyNode)        [create,query,edit]
          Set the DAG object use for worldUpType objectand objectrotation. See worldUpType for greater detail. The default value
          is no up object, which is interpreted as world space.
    
      - worldUpType : wut              (unicode)       [create,query,edit]
          Set the type of the world up vector computation. The worldUpType can have one of 5 values: scene, object,
          objectrotation, vector, or none. If the value is scene, the upVector is aligned with the up axis of the scene and
          worldUpVector and worldUpObject are ignored. If the value is object, the upVector is aimed as closely as possible to the
          origin of the space of the worldUpObject and the worldUpVector is ignored. If the value is objectrotationthen the
          worldUpVector is interpreted as being in the coordinate space of the worldUpObject, transformed into world space and the
          upVector is aligned as closely as possible to the result. If the value is vector, the upVector is aligned with
          worldUpVector as closely as possible and worldUpMatrix is ignored. Finally, if the value is noneno twist calculation is
          performed by the constraint, with the resulting upVectororientation based previous orientation of the constrained
          object, and the great circlerotation needed to align the aim vector with its constraint. The default worldUpType is
          vector.
    
      - worldUpVector : wu             (float, float, float) [create,query,edit]
          Set world up vector.  This is the vector in world coordinates that up vector should align with. See -wut/worldUpType
          (below)for greater detail. If not given at creation time, the default value of (0.0, 1.0, 0.0) is used.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.aimConstraint`
    """

    pass


def copyKey(*args, **kwargs):
    """
    This command operates on a keyset.  A keyset is defined as a group of keys within a specified time range on one or more
    animation curves. The animation curves comprising a keyset depend on the value of the -animationflag: keysOrObjects: Any
    active keys, when no target objects or -attribute flags appear on the command line, orAll animation curves connected to
    all keyframable attributes of objects specified as the command line's targetList, when there are no active keys.keys:
    Only act on active keys or tangents. If there are no active keys or tangents, don't do anything. objects: Only act on
    specified objects.  If there are no objects specified, don't do anything. Note that the -animationflag can be used to
    override the curves uniquely identified by the multi-use -attributeflag, which takes an argument of the form
    attributeName, such as translateX. Keys on animation curves are identified by either their time values or their indices.
    Times and indices can be given individually or as part of a list or range. -time 10palmeans the key at frame 10 (PAL
    format).-time 1.0sec -time 15ntsc -time 20means the keys at time 1.0 second, frame 15 (in NTSC format), and time 20 (in
    the currently defined global time unit).-time 10:20means all keys in the range from 10 to 20, inclusive, in the current
    time unit.Omitting one end of a range means go to infinity, as in the following examples: -time 10:means all keys from
    time 10 (in the current time unit) onwards.-time :10means all keys up to (and including) time 10 (in the current time
    unit).-time :is a short form to specify all keys.-index 0means the first key of each animation curve. (Indices are
    0-based.)-index 2 -index 5 -index 7means the 3rd, 6th, and 8th keys.-index 1:5means the 2nd, 3rd, 4th, 5th, and 6th keys
    of each animation curve.This command copies curve segments's hierarchies from specified targets and puts them in the
    clipboard.  Source curves are unchanged.  The pasteKey command applies these curves to other objects.The shape of the
    copied curve placed in the clipboard depends on the copyKey -optionspecified.  Each of these options below will be
    explained using an example.  For all the explanations, let us assume that the source animation curve (from which keys
    will be copied) has 5 keyframes at times 10, 15, 20, 25, and 30. copyKey -t 12:22-option keysA 5-frame animation curve
    with one key at 15 and another key at 20 is placed into the keyset clipboard.copyKey -t 12:22-option curveA 10-frame
    animation is placed into the clipboard. The curve contains the original source-curve keys at times 15 and 20, as well as
    new keys inserted at times 12 and 22 to preserve the shape of the curve at the given time segment.TbaseKeySetCmd.h
    
    Flags:
      - animLayer : al                 (unicode)       [create]
          Specifies that the keys getting copied should come from this specified animation layer. If no keys on the object exist
          on this layer, then no keys are copied.
    
      - animation : an                 (unicode)       [create]
          Where this command should get the animation to act on.  Valid values are objects,keys,and keysOrObjectsDefault:
          keysOrObjects.(See Description for details.)
    
      - attribute : at                 (unicode)       [create]
          List of attributes to select
    
      - clipboard : cb                 (unicode)       [create]
          Specifies the clipboard to which animation is copied. Valid clipboards are apiand anim.  The default clipboard is: anim
    
      - controlPoints : cp             (bool)          [create]
          This flag explicitly specifies whether or not to include the control points of a shape (see -sflag) in the list of
          attributes. Default: false.  (Not valid for pasteKeycmd.)
    
      - float : f                      (floatrange)    [create]
          value uniquely representing a non-time-based key (or key range) on a time-based animCurve.  Valid floatRange include
          single values (-f 10) or a string with a lower and upper bound, separated by a colon (-f 10:20
    
      - forceIndependentEulerAngles : fea (bool)          [create]
          Specifies that the rotation curves should always be placed on the clipboard as independent Euler Angles. The default
          value is false.
    
      - hierarchy : hi                 (unicode)       [create]
          Hierarchy expansion options.  Valid values are above,below,both,and none.(Not valid for pasteKeycmd.)
    
      - includeUpperBound : iub        (bool)          [create]
          When the -t/time or -f/float flags represent a range of keys, this flag determines whether the keys at the upper bound
          of the range are included in the keyset. Default value: true.  This flag is only valid when the argument to the -t/time
          flag is a time range with a lower and upper bound.  (When used with the pasteKeycommand, this flag refers only to the
          time range of the target curve that is replaced, when using options such as replace,fitReplace,or scaleReplace.This flag
          has no effect on the curve pasted from the clipboard.)
    
      - index : index                  (int)           [create]
          index of a key on an animCurve
    
      - option : o                     (unicode)       [create]
          The option to use when performing the copyKey operation. Valid options are keys,and curve.The default copy option is:
          keys
    
      - shape : s                      (bool)          [create]
          Consider attributes of shapes below transforms as well, except controlPoints.  Default: true.  (Not valid for
          pasteKeycmd.)
    
      - time : t                       (timerange)     [create]
          time uniquely representing a key (or key range) on a time-based animCurve.  Valid timeRanges include single values (-t
          10) or a string with a lower and upper bound, separated by a colon (-t 10:20Flag can have multiple arguments, passed
          either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.copyKey`
    """

    pass


def rotationInterpolation(*args, **kwargs):
    """
    The rotationInterpolation command converts the rotation curves to the         desired rotation interpolation
    representation. For example, an         Euler-angled representation can be converted to Quaternion.                 In
    query mode, return type is based on queried flag.
    
    Flags:
      - convert : c                    (unicode)       [create,query]
          Specifies the rotation interpolation mode for the curves after converting. Possible choices are none(unsynchronized
          Euler-angled curves which are compatible with pre-4.0 Maya curves), euler(Euler-angled curves with keyframes kept
          synchronized), quaternion(quaternion curves with keyframes kept synchronized, but the exact interpolation depends on
          individual tangents),  quaternionSlerp(applies quaternion slerp interpolation to the curve, ignoring tangent settings),
          quaternionSquad(applied cubic interpolation to the curve in quaternion space, ignoring tangent settings)
          Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.rotationInterpolation`
    """

    pass


def keyframe(*args, **kwargs):
    """
    This command operates on a keyset.  A keyset is defined as a group of keys within a specified time range on one or more
    animation curves. The animation curves comprising a keyset depend on the value of the -animationflag: keysOrObjects: Any
    active keys, when no target objects or -attribute flags appear on the command line, orAll animation curves connected to
    all keyframable attributes of objects specified as the command line's targetList, when there are no active keys.keys:
    Only act on active keys or tangents. If there are no active keys or tangents, don't do anything. objects: Only act on
    specified objects.  If there are no objects specified, don't do anything. Note that the -animationflag can be used to
    override the curves uniquely identified by the multi-use -attributeflag, which takes an argument of the form
    attributeName, such as translateX. Keys on animation curves are identified by either their time values or their indices.
    Times and indices can be given individually or as part of a list or range. -time 10palmeans the key at frame 10 (PAL
    format).-time 1.0sec -time 15ntsc -time 20means the keys at time 1.0 second, frame 15 (in NTSC format), and time 20 (in
    the currently defined global time unit).-time 10:20means all keys in the range from 10 to 20, inclusive, in the current
    time unit.Omitting one end of a range means go to infinity, as in the following examples: -time 10:means all keys from
    time 10 (in the current time unit) onwards.-time :10means all keys up to (and including) time 10 (in the current time
    unit).-time :is a short form to specify all keys.-index 0means the first key of each animation curve. (Indices are
    0-based.)-index 2 -index 5 -index 7means the 3rd, 6th, and 8th keys.-index 1:5means the 2nd, 3rd, 4th, 5th, and 6th keys
    of each animation curve.This command edits the time and/or value of keys of specified objects and/or parameter curves
    Unless otherwise specified by the -query flag, the command defaults to editing keyframes.
    
    Modifications:
        - returns an empty list when the result is None
        - if both valueChange and timeChange are queried, the result will be a list of (time,value) pairs
    
    Flags:
      - absolute : a                   (bool)          [create]
          Move amounts are absolute.
    
      - adjustBreakdown : abd          (bool)          [create]
          When false, moving keys will not preserve breakdown timing, when true (the default) breakdowns will be adjusted to
          preserve their timing relationship.
    
      - animation : an                 (unicode)       [create]
          Where this command should get the animation to act on.  Valid values are objects,keys,and keysOrObjectsDefault:
          keysOrObjects.(See Description for details.)
    
      - attribute : at                 (unicode)       [create]
          List of attributes to select
    
      - breakdown : bd                 (bool)          [create,query,edit]
          Sets the breakdown state for the key.  Returns an integer.  Default is false.  The breakdown state of a key cannot be
          set in the same command as it is moved (i.e., via the -tc or -fc flags).
    
      - clipTime : ct                  (time, time, <type 'float'>) [create]
          Modifies the final time where a key is inserted using an offset, pivot, and scale.
    
      - controlPoints : cp             (bool)          [create]
          This flag explicitly specifies whether or not to include the control points of a shape (see -sflag) in the list of
          attributes. Default: false.  (Not valid for pasteKeycmd.)
    
      - eval : ev                      (bool)          [create,query]
          Returns the value(s) of the animCurves when evaluated (without regard to input connections) at the times given by the
          -t/time or -f/float flags.  Cannot be used in combination with other query flags, and cannot be used with time ranges
          (-t 5:10). When no -t or -f flags appear on the command line, the evals are queried at the current time.  Query returns
          a float[].
    
      - float : f                      (floatrange)    [create]
          value uniquely representing a non-time-based key (or key range) on a time-based animCurve.  Valid floatRange include
          single values (-f 10) or a string with a lower and upper bound, separated by a colon (-f 10:20
    
      - floatChange : fc               (float)         [create,query,edit]
          How much (with -relative) or where (with -absolute) to move keys (on non-time-input animation curves) along the x
          (float) axis. Returns float[] when queried.
    
      - hierarchy : hi                 (unicode)       [create]
          Hierarchy expansion options.  Valid values are above,below,both,and none.(Not valid for pasteKeycmd.)
    
      - includeUpperBound : iub        (bool)          [create]
          When the -t/time or -f/float flags represent a range of keys, this flag determines whether the keys at the upper bound
          of the range are included in the keyset. Default value: true.  This flag is only valid when the argument to the -t/time
          flag is a time range with a lower and upper bound.  (When used with the pasteKeycommand, this flag refers only to the
          time range of the target curve that is replaced, when using options such as replace,fitReplace,or scaleReplace.This flag
          has no effect on the curve pasted from the clipboard.)
    
      - index : index                  (timeRange)     [create]
          index of a key on an animCurve
    
      - indexValue : iv                (bool)          [create,query]
          Query-only flag that returns an int for the key's index.
    
      - keyframeCount : kc             (bool)          [create,query]
          Returns an int for the number of keys found for the targets.
    
      - lastSelected : lsl             (bool)          [create,query]
          When used in queries, this flag returns requested values for the last selected key.
    
      - name : n                       (bool)          [create,query]
          Returns the names of animCurves of specified nodes, attributes or keys.
    
      - option : o                     (unicode)       [create,edit]
          Valid values are move,insert,over,and segmentOver.When you movea key, the key will not cross over (in time) any keys
          before or after it. When you inserta key, all keys before or after (depending upon the -timeChange value) will be moved
          an equivalent amount. When you overa key, the key is allowed to move to any time (as long as a key is not there
          already). When you segmentOvera set of keys (this option only has a noticeable effect when more than one key is being
          moved) the first key (in time) and last key define a segment (unless you specify a time range). That segment is then
          allowed to move over other keys, and keys will be moved to make room for the segment.
    
      - relative : r                   (bool)          [create]
          Move amounts are relative to a key's current position.
    
      - selected : sl                  (bool)          [create,query]
          When used in queries, this flag returns requested values for any active keys.
    
      - shape : s                      (bool)          [create]
          Consider attributes of shapes below transforms as well, except controlPoints.  Default: true.  (Not valid for
          pasteKeycmd.)
    
      - tickDrawSpecial : tds          (bool)          [create,edit]
          Sets the special drawing state for this key when it is drawn as a tick in the timeline.
    
      - time : t                       (timerange)     [create]
          time uniquely representing a key (or key range) on a time-based animCurve.  Valid timeRanges include single values (-t
          10) or a string with a lower and upper bound, separated by a colon (-t 10:20
    
      - timeChange : tc                (time)          [create,query,edit]
          How much (with -relative) or where (with -absolute) to move keys (on time-input animation curves) along the x (time)
          axis.  Returns float[] when queried.
    
      - valueChange : vc               (float)         [create,query,edit]
          How much (with -relative) or where (with -absolute) to move keys along the y (value) axis. Returns float[] when queried.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.keyframe`
    """

    pass


def ikfkDisplayMethod(*args, **kwargs):
    """
    The ikfkDisplayMethodcommand is used to specify how ik/fk       blending should be shown                 In query mode,
    return type is based on queried flag.
    
    Flags:
      - display : d                    (unicode)       [create,query]
          Specify how ik/fk blending should be shown when the handle is selected. Possible choices are none(do not display any
          blending), ik(only show ik),fk(only show fk), and ikfk(show both ik and fk).                                  Flag can
          have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.ikfkDisplayMethod`
    """

    pass


def keyingGroup(*args, **kwargs):
    """
    This command is used to manage the membership of a keying group.  Keying groups allow users to effectively manage
    related keyframe data, allowing keys on attributes in the keying group to be set and edited as a single entity.
    
    Flags:
      - activator : act                (unicode)       [query,edit]
          Sets the selected node(s) as activators for the given keying group. In query mode, returns list of objects that activate
          the given keying group
    
      - addElement : add               (PyNode)        [edit]
          Adds the list of items to the given set.  If some of the items cannot be added to the set because they are in another
          set which is in the same partition as the set to edit, the command will fail.
    
      - afterFilters : af              (bool)          [edit]
          Default state is false. This flag is valid in edit mode only. This flag is for use on sets that are acted on by
          deformers such as sculpt, lattice, blendShape. The default edit mode is to edit the membership of the group acted on by
          the deformer. If you want to edit the group but not change the membership of the deformer, set the flag to true.
    
      - category : cat                 (unicode)       [create,query,edit]
          Sets the keying group's category. This is what the global, active keying group filter will use to match.
    
      - clear : cl                     (PyNode)        [edit]
          An operation which removes all items from the given set making the set empty.
    
      - color : co                     (int)           [create,query,edit]
          Defines the hilite color of the set. Must be a value in range [-1, 7] (one of the user defined colors).  -1 marks the
          color has being undefined and therefore not having any affect. Only the vertices of a vertex set will be displayed in
          this color.
    
      - copy : cp                      (PyNode)        [create]
          Copies the members of the given set to a new set. This flag is for use in creation mode only.
    
      - edges : eg                     (bool)          [create,query]
          Indicates the new set can contain edges only. This flag is for use in creation or query mode only. The default value is
          false.
    
      - editPoints : ep                (bool)          [create,query]
          Indicates the new set can contain editPoints only. This flag is for use in creation or query mode only. The default
          value is false.
    
      - empty : em                     (bool)          [create]
          Indicates that the set to be created should be empty. That is, it ignores any arguments identifying objects to be added
          to the set. This flag is only valid for operations that create a new set.
    
      - excludeDynamic : ed            (bool)          [create]
          When creating the keying group, exclude dynamic attributes.
    
      - excludeRotate : er             (bool)          [create]
          When creating the keying group, exclude rotate attributes from transform-type nodes.
    
      - excludeScale : es              (bool)          [create]
          When creating the keying group, exclude scale attributes from transform-type nodes.
    
      - excludeTranslate : et          (bool)          [create]
          When creating the keying group, exclude translate attributes from transform-type nodes. For example, if your keying
          group contains joints only, perhaps you only want to include rotations in the keying group.
    
      - excludeVisibility : ev         (bool)          [create]
          When creating the keying group, exclude visibility attribute from transform-type nodes.
    
      - facets : fc                    (bool)          [create,query]
          Indicates the new set can contain facets only. This flag is for use in creation or query mode only. The default value is
          false.
    
      - flatten : fl                   (PyNode)        [edit]
          An operation that flattens the structure of the given set. That is, any sets contained by the given set will be replaced
          by its members so that the set no longer contains other sets but contains the other sets' members.
    
      - forceElement : fe              (PyNode)        [edit]
          For use in edit mode only. Forces addition of the items to the set. If the items are in another set which is in the same
          partition as the given set, the items will be removed from the other set in order to keep the sets in the partition
          mutually exclusive with respect to membership.
    
      - include : include              (PyNode)        [edit]
          Adds the list of items to the given set.  If some of the items cannot be added to the set, a warning will be issued.
          This is a less strict version of the -add/addElement operation.
    
      - intersection : int             (PyNode)        [create]
          An operation that returns a list of items which are members of all the sets in the list.
    
      - isIntersecting : ii            (PyNode)        [create]
          An operation which tests whether the sets in the list have common members.
    
      - isMember : im                  (PyNode)        [create]
          An operation which tests whether all the given items are members of the given set.
    
      - layer : l                      (bool)          [create]
          OBSOLETE. DO NOT USE.
    
      - minimizeRotation : mr          (bool)          [create,query,edit]
          This flag only affects the attribute contained in the immediate keyingGroup. It does not affect attributes in sub-
          keyingGroups. Those will need to set minimizeRotation on their respective keyingGroups
    
      - name : n                       (unicode)       [create]
          Assigns string as the name for a new set. This flag is only valid for operations that create a new set.
    
      - noSurfaceShader : nss          (bool)          [create]
          If set is renderable, do not connect it to the default surface shader.  Flag has no meaning or effect for non renderable
          sets. This flag is for use in creation mode only. The default value is false.
    
      - noWarnings : nw                (bool)          [create]
          Indicates that warning messages should not be reported such as when trying to add an invalid item to a set. (used by UI)
    
      - nodesOnly : no                 (bool)          [query]
          This flag is usable with the -q/query flag but is ignored if used with another queryable flags. This flag modifies the
          results of the set membership query such that when there are attributes (e.g. sphere1.tx) or components of nodes
          included in the set, only the nodes will be listed. Each node will only be listed once, even if more than one attribute
          or component of the node exists in the set.
    
      - remove : rm                    (PyNode)        [edit]
          Removes the list of items from the given set.
    
      - removeActivator : rac          (unicode)       [edit]
          Removes the selected node(s) as activators for the given keying group.
    
      - renderable : r                 (bool)          [create,query]
          This flag indicates that a special type of set should be created. This type of set (shadingEngine as opposed to
          objectSet) has certain restrictions on its membership in that it can only contain renderable elements such as lights and
          geometry. These sets are referred to as shading groups and are automatically connected to the renderPartitionnode when
          created (to ensure mutual exclusivity of the set's members with the other sets in the partition). This flag is for use
          in creation or query mode only. The default value is false which means a normal set is created.
    
      - setActiveFilter : fil          (unicode)       [create,query,edit]
          Sets the global, active keying group filter, which will affect activation of keying groups. Only keying groups with
          categories that match the filter will be activated. If the setActiveFilter is set to NoKeyingGroups, keying groups will
          not be activated at all. If the setActiveFilter is set to AllKeyingGroups, we will activate any keying group rather than
          just those with matching categories.
    
      - size : s                       (bool)          [query]
          Use the size flag to query the length of the set.
    
      - split : sp                     (PyNode)        [create]
          Produces a new set with the list of items and removes each item in the list of items from the given set.
    
      - subtract : sub                 (PyNode)        [create]
          An operation between two sets which returns the members of the first set that are not in the second set.
    
      - text : t                       (unicode)       [create,query,edit]
          Defines an annotation string to be stored with the set.
    
      - union : un                     (PyNode)        [create]
          An operation that returns a list of all the members of all sets listed.
    
      - vertices : v                   (bool)          [create,query]
          Indicates the new set can contain vertices only. This flag is for use in creation or query mode only. The default value
          is false.                  Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.keyingGroup`
    """

    pass


def bakeSimulation(*args, **kwargs):
    """
    This command operates on a keyset.  A keyset is defined as a group of keys within a specified time range on one or more
    animation curves. The animation curves comprising a keyset depend on the value of the -animationflag: keysOrObjects: Any
    active keys, when no target objects or -attribute flags appear on the command line, orAll animation curves connected to
    all keyframable attributes of objects specified as the command line's targetList, when there are no active keys.keys:
    Only act on active keys or tangents. If there are no active keys or tangents, don't do anything. objects: Only act on
    specified objects.  If there are no objects specified, don't do anything. Note that the -animationflag can be used to
    override the curves uniquely identified by the multi-use -attributeflag, which takes an argument of the form
    attributeName, such as translateX. Keys on animation curves are identified by either their time values or their indices.
    Times and indices can be given individually or as part of a list or range. -time 10palmeans the key at frame 10 (PAL
    format).-time 1.0sec -time 15ntsc -time 20means the keys at time 1.0 second, frame 15 (in NTSC format), and time 20 (in
    the currently defined global time unit).-time 10:20means all keys in the range from 10 to 20, inclusive, in the current
    time unit.Omitting one end of a range means go to infinity, as in the following examples: -time 10:means all keys from
    time 10 (in the current time unit) onwards.-time :10means all keys up to (and including) time 10 (in the current time
    unit).-time :is a short form to specify all keys.-index 0means the first key of each animation curve. (Indices are
    0-based.)-index 2 -index 5 -index 7means the 3rd, 6th, and 8th keys.-index 1:5means the 2nd, 3rd, 4th, 5th, and 6th keys
    of each animation curve.The bakeSimulation command is obsolete.  Instead, bakeResults -simulation trueshould be used.
    The bakeSimulation command has retained for backwards compatibility. This command allows the user to replace a chain of
    dependency nodes, or implicit relationship, such as those between joints and IK handles, which define the value of an
    attribute, with a single animation curve. Command allows the user to specify the range and frequency of sampling. Unlike
    the bakeResults command, this command will actually set the time of the current scene to all the times, in sequence,
    inside the given time interval before it sets the time back to when it is started. As a result, it may modify the scene.
    In query mode, return type is based on queried flag.
    
    Flags:
      - animation : an                 (unicode)       [create]
          Where this command should get the animation to act on.  Valid values are objects,keys,and keysOrObjectsDefault:
          keysOrObjects.(See Description for details.)
    
      - attribute : at                 (unicode)       [create]
          List of attributes to select
    
      - bakeOnOverrideLayer : bol      (bool)          [create]
          If true, all layered and baked attributes will be added as a top override layer.
    
      - controlPoints : cp             (bool)          [create]
          This flag explicitly specifies whether or not to include the control points of a shape (see -sflag) in the list of
          attributes. Default: false.  (Not valid for pasteKeycmd.)
    
      - destinationLayer : dl          (unicode)       [create]
          This flag can be used to specify an existing layer where the baked results should be stored.
    
      - disableImplicitControl : dic   (bool)          [create]
          Whether to disable implicit control after the anim curves are obtained as the result of this command. An implicit
          control to an attribute is some function that affects the attribute without using an explicit dependency graph
          connection. The control of IK, via ik handles, is an example.
    
      - float : f                      (floatrange)    [create]
          value uniquely representing a non-time-based key (or key range) on a time-based animCurve.  Valid floatRange include
          single values (-f 10) or a string with a lower and upper bound, separated by a colon (-f 10:20
    
      - hierarchy : hi                 (unicode)       [create]
          Hierarchy expansion options.  Valid values are above,below,both,and none.(Not valid for pasteKeycmd.)
    
      - includeUpperBound : iub        (bool)          [create]
          When the -t/time or -f/float flags represent a range of keys, this flag determines whether the keys at the upper bound
          of the range are included in the keyset. Default value: true.  This flag is only valid when the argument to the -t/time
          flag is a time range with a lower and upper bound.  (When used with the pasteKeycommand, this flag refers only to the
          time range of the target curve that is replaced, when using options such as replace,fitReplace,or scaleReplace.This flag
          has no effect on the curve pasted from the clipboard.)
    
      - index : index                  (int)           [create]
          index of a key on an animCurve
    
      - minimizeRotation : mr          (bool)          [create]
          Specify whether to minimize the local euler component from key to key during baking of rotation channels.
    
      - oversamplingRate : osr         (int)           []
    
      - preserveOutsideKeys : pok      (bool)          [create]
          Whether to preserve keys that are outside the bake range when there are directly connected animation curves.  The
          default (false) is to remove frames outside the bake range.  If the channel that you are baking is not controlled by a
          single animation curve, then a new animation curve will be created with keys only in the bake range.
    
      - removeBakedAnimFromLayer : rba (bool)          [create]
          If true, all baked animation will be removed from the layer.
    
      - removeBakedAttributeFromLayer : ral (bool)          [create]
          If true, all baked attributes will be removed from the layer.
    
      - resolveWithoutLayer : rwl      (unicode)       [create]
          This flag can be used to specify a list of layers to be merged together during the bake process. This is a multi-use
          flag. Its name refers to the fact that when solving for the value to key, it determines the proper value to key on the
          destination layer to achieve the same result as the merged layers.
    
      - sampleBy : sb                  (time)          [create]
          Amount to sample by. Default is 1.0 in current timeUnit
    
      - shape : s                      (bool)          [create]
          Consider attributes of shapes below transforms as well, except controlPoints.  Default: true.  (Not valid for
          pasteKeycmd.)
    
      - simulation : sm                (bool)          [create]
          Using this flag instructs the command to preform a simulation instead of just evaluating each attribute separately over
          the range of time. The simulation flag is required to bake animation that that depends on the whole scene being
          evaluated at each time step such as dynamics. The default is true.
    
      - smart : sr                     (bool, float)   [create]
          Specify whether to enable smart bake and the optional smart bake tolerance.
    
      - sparseAnimCurveBake : sac      (bool)          [create]
          When baking anim curves, do not insert any keys into areas of the curve where animation is defined.  And, use as few
          keys as possible to bake the pre and post infinity behaviors.  When this is false, one key will be inserted at each time
          step.  The default is false.
    
      - time : t                       (timerange)     [create]
          time uniquely representing a key (or key range) on a time-based animCurve.  Valid timeRanges include single values (-t
          10) or a string with a lower and upper bound, separated by a colon (-t 10:20Flag can have multiple arguments, passed
          either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.bakeSimulation`
    """

    pass


def snapshot(*args, **kwargs):
    """
    This command can be used to create either a series of surfaces evaluated at the times specified by the command flags, or
    a motion trail displaying the trajectory of the object's pivot point at the times specified.If the constructionHistory
    flag is true, the output shapes or motion trail will re-update when modifications are made to the animation or
    construction history of the original shape. When construction history is used, the forceUpdate flag can be set to false
    to control when the snapshot recomputes, which will typically improve performance.
    
    Flags:
      - anchorTransform : at           (unicode)       []
    
      - constructionHistory : ch       (bool)          [create,query]
          update with changes to original geometry
    
      - endTime : et                   (time)          [create,query,edit]
          time to stop copying target geometry Default: 10.0
    
      - increment : i                  (time)          [create,query,edit]
          time increment between copies Default: 1.0
    
      - motionTrail : mt               (bool)          [create]
          Rather than create a series of surfaces, create a motion trail displaying the location of the object's pivot point at
          the specified time steps. Default is false.
    
      - motionTrailName : mtn          (unicode)       []
    
      - name : n                       (unicode)       [create,query,edit]
          the name of the snapshot node. Query returns string.
    
      - removeAnchorTransform : rat    (unicode)       []
    
      - startTime : st                 (time)          [create,query,edit]
          time to begin copying target geometry Default: 1.0
    
      - update : u                     (unicode)       [create,query,edit]
          This flag can only be used if the snapshot has constructionHistory. It sets the snapshot node's update value. The update
          value controls whether the snapshot updates on demand (most efficient), when keyframes change (efficient), or whenever
          any history changes (least efficient). Valid values are demand, animCurve, always. Default: alwaysFlag can have multiple
          arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.snapshot`
    """

    pass


def characterize(*args, **kwargs):
    """
    This command is used to scan a joint hierarchy for predefined joint names or labels. If the required joints are found,
    human IK effectors will be created to control the skeleton using full-body IK. Alternatively, you can manually create
    all of the components required for fullbody IK, and use this command to hook them up. Fullbody IK needs 3 major
    components: the user input skeleton (sk), the fk skeleton on which keys are set (fk) and the hik effectors (ik).
    Together fk and ik provide parameters to the fullbody IK engine, which solves for the output and plots it onto sk. This
    command usage is used internally by Maya when importing data from fbx files, but is not generally recommended. Note that
    a minimum set of required joint names or joint labels  must be found in order for the characterize command to succeed.
    Please refer to the Maya documentation for details on properly naming or labeling your skeleton. The skeleton should
    also be z-facing, with its y-axis up, its left hand parallel to positive x-axis and right hand parallel to negative
    x-axis. END_COMMENT
    
    Flags:
      - activatePivot : apv            (bool)          [edit]
          Activates a pivot that has been properly placed.  After activating this new pivot, you will now be able to rotate and
          translate about this pivot. A pivot behaves in all ways the same as an effector (it IS an effector, except that it is
          offset from the normal position of the effector to allow one to rotate about a different point.
    
      - addAuxEffector : aae           (bool)          [edit]
          Adds an auxilliary (secondary) effector to an existing effector.
    
      - addFloorContactPlane : afp     (bool)          [edit]
          Adds a floor contact plane to one of the hands or feet.  With this plane, you will be able to adjust the floor contact
          height.  Select a hand or foot effector and then issue the characterize command with this flag.
    
      - addMissingEffectors : ame      (bool)          [edit]
          This flag tells the characterize command to look for any effectors that can be added to the skeleton. For example, if
          the user has deleted some effectors or added fingers to an existing skeleton, characterize -e -addMissingEffectorscan be
          used to restore them.
    
      - attributeFromHIKProperty : ahk (unicode)       [query]
          Query for the attribute name associated with a MotionBuilder property.
    
      - attributeFromHIKPropertyMode : mhk (unicode)       [query]
          Query for the attribute name associated with a MotionBuilder property mode.
    
      - autoActivateBodyPart : aab     (bool)          [query,edit]
          Query or change whether auto activation of character nodes representing body parts should be enabled.
    
      - changePivotPlacement : cpp     (bool)          [edit]
          Reverts a pivot back into pivot placement mode.  A pivot that is in placement mode will not participate in full body
          manipulation until it has been activated with the -activatePivot flag.
    
      - effectors : ef                 (unicode)       [create]
          Specify the effectors to be used by human IK by providing 2 pieces of information for each effector:  1) the partial
          path of the effector and 2) the name of the full body effector this represents.  1) and 2) are to be separated by white
          space, and multiple entries separated by ,. Normally, the effectors are automatically created.  This flag is for
          advanced users only.
    
      - fkSkeleton : fk                (unicode)       [create,edit]
          Specify the fk skeleton to be used by human IK by providing 2 pieces of information for each joint of the FK skeleton:
          1) the partial path of the joint and 2) the name of the full body joint this represents.  1) and 2) are to be separated
          by white space, and multiple entries separated by ,. Normally, the fk control skeleton is automatically created.  This
          flag is for advanced users only.
    
      - name : nm                      (unicode)       [create]
          At characterization (FBIK creation) time, use this flag to name your FBIK character. This will affect the name of the
          hikHandle node and the control rig will be put into a namespace that matches the name of your character.  If you do not
          specify the character name, a default one will be used. At the moment edit and query of the character name is not
          supported.
    
      - pinHandFeet : phf              (bool)          [create]
          When the character is first being characterized, pin the hands and feet by default.
    
      - placeNewPivot : pnp            (bool)          [edit]
          Creates a new pivot and puts it into placement mode.  Note that you will not be able to do full body manipulation about
          this pivot until you have activated it with the -activatePivot flag. A pivot behaves in all ways the same as an effector
          (it IS an effector, except that it is offset from the normal position of the effector to allow one to rotate about a
          different point). A new pivot created with this flag allow you to adjust the offset interactively before activating it.
    
      - posture : pos                  (unicode)       [create]
          Specifies the posture of the character. Valid options are bipedand quadruped. The default is biped.
    
      - sourceSkeleton : sk            (unicode)       [create,edit]
          This flag can be used to characterize a skeleton that has not been named or labelled according to the FBIK guidelines.
          It specifies the association between the actual joint names and the expected FBIK joint names. The format of the string
          is as follows: For each joint that the user wants to involve in the solve:  1) the partial path of the joint and 2) the
          name of the full body joint this represents.  1) and 2) are to be separated by white space, and multiple entries
          separated by ,.
    
      - stancePose : sp                (unicode)       [create,query]
          Specify the default stance pose to be used by human IK.  The stance pose is specified by providing 2 pieces of
          information for each joint involved in the solve: 1) the partial path to the joint and 2) 9 numbers representing
          translation rotation and scale. 1) and 2) are to be separated by white space, and multiple entries separated by ,.
          Normally, the stance pose is taken from the selected skeleton.  This flag is for advanced users only.
    
      - type : typ                     (unicode)       [create]
          Specifies the technique used by the characterization to identify the joint type. Valid options are labeland name. When
          labelis used, the joints must be labelled using the guidelines described in the Maya documentation. When name is used,
          the joint names must follow the naming conventions described in the Maya documentation. The default is name. This flag
          cannot be used in conjunction with the sourceSkeleton flag.                                   Flag can have multiple
          arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.characterize`
    """

    pass


def setKeyframeBlendshapeTargetWts(*args, **kwargs):
    """
    This command can be used to keyframe per-point blendshape target weights. It operates on the currently selected objects
    as follows. When the base object is selected, then the target weights are keyed for all targets. When only target shapes
    are selected, then the weights for thoses targets are keyframed.
    
    
    Derived from mel command `maya.cmds.setKeyframeBlendshapeTargetWts`
    """

    pass


def bakeClip(*args, **kwargs):
    """
    This command is used to bake clips and blends into a single clip.
    
    Flags:
      - blend : b                      (int, int)      [create]
          Specify the indices of the clips being blended.
    
      - clipIndex : ci                 (int)           [create]
          Specify the index of the clip to bake.
    
      - keepOriginals : k              (bool)          [create]
          Keep original clips in the trax editor and place the merged clip into the visor. The default is to schedule the merged
          clip, and to keep the original clips in the visor.
    
      - name : n                       (unicode)       [create]
          Specify the name of the new clip to create.                                Flag can have multiple arguments, passed
          either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.bakeClip`
    """

    pass


def lattice(*args, **kwargs):
    """
    This command creates a lattice deformer that will deform the selected objects. If the object centered flag is used, the
    initial lattice will fit around the selected objects. The lattice will be selected when the command is completed. The
    lattice deformer has an associated base lattice. Only objects which are contained by the base lattice will be deformed
    by the lattice.
    
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
    
      - commonParent : cp              (bool)          [create]
          Group the base lattice and the deformed lattice under a common transform. This means that you can resize the lattice
          without affecting the deformation by resizing the common transform.
    
      - deformerTools : dt             (bool)          [query]
          Returns the name of the deformer tool objects (if any) as string string ...
    
      - divisions : dv                 (int, int, int) [create,query,edit]
          Set the number of lattice slices in x, y, z. Default is 2, 5, 2. When queried, this flag returns float float float. When
          you change the number of divisions, any tweaking or animation of lattice points must be redone.
    
      - dualBase : db                  (bool)          [create]
          Create a special purpose ffd deformer node which accepts 2 base lattices. The default is off which results in the
          creation of a normal ffd deformer node. Intended for internal usage only.
    
      - exclusive : ex                 (unicode)       [create,query]
          Puts the deformation set in a deform partition.
    
      - freezeMapping : fm             (bool)          [create,query,edit]
          The base position of the geometries points is fixed at the time this flag is set.  When mapping is frozen, moving the
          geometry with respect to the lattice will not cause the deformation to be recomputed.
    
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
    
      - latticeReset : lr              (bool)          [edit]
          Reset the lattice to match its base position. This will undo any deformations that the lattice is causing. The lattice
          will only deform points that are enclosed within the lattice's reset (base) position.
    
      - ldivisions : ldv               (int, int, int) [create,query,edit]
          Set the number of local lattice slices in x, y, z.
    
      - name : n                       (unicode)       [create]
          Used to specify the name of the node being created.
    
      - objectCentered : oc            (bool)          [create]
          Centers the lattice around the selected object(s) or components. Default is off which centers the lattice at the origin.
    
      - outsideFalloffDistance : ofd   (float)         [create]
          Set the falloff distance used when the setting for transforming points outside of the base lattice is set to 2. The
          distance value is a positive number which specifies the size of the falloff distance as a multiple of the base lattice
          size, thus a value of 1.0 specifies that only points up to the base lattice width/height/depth away are transformed. A
          value of 0.0 is equivalent to an outsideLattice value of 0 (i.e. no points outside the base lattice are transformed). A
          huge value is equivalent to transforming an outsideLattice value of 1 (i.e. all points are transformed).
    
      - outsideLattice : ol            (int)           [create]
          Set the mode describing how points outside the base lattice are transformed. 0 (the default) specifies that no outside
          points are transformed. 1 specifies that all outside points are transformed, and 2 specifies that only those outside
          points which fall within the falloff distance(see the -ofd/outsideFalloffDistance flag) are transformed. When querying,
          the current setting for the lattice is returned.
    
      - parallel : par                 (bool)          [create,edit]
          Inserts the new deformer in a parallel chain to any existing deformers in the history of the object. A blendShape is
          inserted to blend the parallel results together. Works in create mode (and edit mode if the deformer has no geometry
          added yet).
    
      - position : pos                 (float, float, float) [create]
          Used to specify the position of the newly created lattice.
    
      - prune : pr                     (bool)          [edit]
          Removes any points not being deformed by the deformer in its current configuration from the deformer set.
    
      - remove : rm                    (bool)          [edit]
          Specifies that objects listed after the -g flag should be removed from this deformer.
    
      - removeTweaks : rt              (bool)          [edit]
          Remove any lattice deformations caused by moving lattice points. Translations/rotations and scales on the lattice itself
          are not removed.
    
      - rotation : ro                  (float, float, float) [create]
          Used to specify the initial rotation of the newly created lattice.
    
      - scale : s                      (float, float, float) [create]
          Used to specify the initial scale of the newly created lattice.
    
      - split : sp                     (bool)          [create,edit]
          Branches off a new chain in the dependency graph instead of inserting/appending the deformer into/onto an existing
          chain. Works in create mode (and edit mode if the deformer has no geometry added yet).                  Flag can have
          multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.lattice`
    """

    pass


def applyTake(*args, **kwargs):
    """
    This command takes data in a device (refered to as a take) and converts it into a form that may be played back and
    reviewed. The take can either be imported through the readTake action, or recorded by the recordDevice action. The take
    is either converted into animation curves or if the -preview flag is used, into blendDevice nodes. The command looks for
    animation curves attached to the target attributes of a device attachment. If animation curves exist, the take is pasted
    over the existing curves. If the curves do not exist, new animation curves are created. If devices are not specified,
    all of the devices with take data and that are enabled for applyTake, will have their data applied. See also:
    recordDevice, enableDevice, readTake, writeTake
    
    Flags:
      - channel : c                    (unicode)       [create]
          This flag overrides the set channel enable value. If a channel is specified, it will be enabled. C: The default is all
          applyTake enabled channels for the device(s).
    
      - device : d                     (unicode)       [create]
          Specifies which device contains the take. C: The default is all applyTake enabled devices.
    
      - filter : f                     (unicode)       [create]
          This flag specifies the filters to use during the applyTake. If this flag is used multiple times, the ordering of the
          filters is from left to right. C: The default is no filters.
    
      - preview : p                    (bool)          [create]
          Applies the take to blendDevice nodes attached to the target attributes connected to the device attachments. Animation
          curves attached to the attributes will not be altered, but for the time that preview data is defined, the preview data
          will be the data used during playback. C: The default is to not preview.
    
      - recurseChannel : rc            (bool)          [create]
          When this flag is used, the children of the channel(s) specified by -c/channel are also applied. C: The default is all
          of the enabled channels.
    
      - reset : r                      (bool)          [create]
          Resets the blendDevice nodes affected by -preview. The preview data is removed and if animation curves exist, they are
          used during playback.
    
      - specifyChannel : sc            (bool)          [create]
          This flag is used with -c/channel flag. When used, applyTake will only work on the channels listed with the -c/channel
          flag. C: The default is all of the enabled channels.
    
      - startTime : st                 (time)          [create]
          The default start time for a take is determined at record time. The startTime option sets the starting time of the take
          in the current animation units. C: The default is the first time stamp of the take. If a time stamp does not exist for
          the take, 0 is used.                  Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.applyTake`
    """

    pass


def deformerWeights(*args, **kwargs):
    """
    Command to import and export deformer weights to and from a simple XML  file. The weight data is stored in a per-vertex
    fashion along with a  point cloudcorresponding to the vertices from the geometry input to  the deformer.  For example a
    cluster deformer would have the following information:  On import the weights are then mapped back to a specified
    deformer  based on the specified mapping method. Note that the geometry used to  perform the mapping association is not
    the visible shape but rather  the incoming geometry to the deformer. For example, in the case of a  skin cluster this
    would be the bind pose geometry.
    
    Flags:
      - attribute : at                 (unicode)       [create,query,edit]
          Specify the long name of deformer attribute that should be imported/exported along with the deformerWeights. i.e. -at
          envelope-at skinningMethodetc.. No warning or error is given if a specified attribute does not exist on a particular
          deformer, making it possible to use this command with multiple deformers without aborting or slowing down the
          import/export process.  Currently supports numeric attributes and matrix attributes
    
      - defaultValue : dv              (float)         [create,query,edit]
          Manually set the default value. Default values are values that are not written to file. For example, for blendShapes the
          default value is automatically set to 1.0 and these values are not written to disk. For skinClusters the value is 0.0.
          If all weights should be forced to be written to disk, set a defaultValue = -1.0.
    
      - deformer : df                  (unicode)       [create,query,edit]
          Specify the deformer whose weights should be exported or imported. If a pattern is supplied for the deformer name (i.e:
          cluster\*), only the first deformer that matches the pattern will be imported/exported unless used in conjunction with
          the -skip option
    
      - export : ex                    (bool)          [create,query,edit]
          Export the given deformer
    
      - ignoreName : ig                (bool)          [create,query,edit]
          Ignore the names of the layers on import, just use the order of the layers instead. This can be used when joint names
          have been changed. Leaving it on only name that match on import will be write to the deformer.
    
      - im : im                        (bool)          [create,query,edit]
          Import weights to the specified deformer. See the method flag for details on how the weights will be mapped to the
          destination deformer.
    
      - method : m                     (unicode)       [create,query,edit]
          Specify the method used to map the weight during import. Valid values are: index, nearest, barycentric, bilinearand
          over. The indexmethod uses the vertex index to map the weights onto the object. This is most useful when the destination
          object shares the same topology as the exported data. The nearestmethod finds the nearest vertex in the imported data
          set and sets the weight value to that value. This is best used when mapping a higher resolution mesh to a lower
          resolution. The barycentricand bilinearmethods are only supported with polygon mesh exported with -vc/vertexConnections
          flag. The barycentricmethod finds the nearest triangle of the input geometry and rescales the weights at the triangle
          vertices according to the barycentric weights to each vertex of the nearest triangle. The bilinearmethod finds the
          nearest convex quad of the input geometry and rescales the weights at the quad vertices according to the bilinear
          weights to each vertex of the nearest convex quad. For non-quad polygon, the bilinearmethod will fall back to
          barycentricmethod. The overmethod is similar to the indexmethod but the weights on the destination mesh are not cleared
          prior to mapping, so that unmatched indices keep their weights intact.
    
      - path : p                       (unicode)       [create,query,edit]
          The path to the given file. Default to the current project.
    
      - positionTolerance : pt         (float)         [create,query,edit]
          The position tolerance is used to determine the radius of search for the nearest method. This flag is only used with
          import. Defaults to a huge number.
    
      - remap : r                      (unicode)       [create,query,edit]
          Remap maps source regular expression to destination format. It maps any name that matches the regular expression (before
          the semi-colon) to the expression format (after the semi-colon). For example, -remap test:(.\*);$1will rename all items
          in the test namespace to the global namespace. Accepts $1, $2, .., $9 as pattern holders in the expression format. Remap
          flag must be used together with import or export. When working with import, the name of the object from the xml file
          matching the regular expression is remapped to object in scene. When working with export, the name of the object from
          the scene matching the regular expression is remapped to object in xml file.
    
      - shape : sh                     (unicode)       [create,query,edit]
          Specify the source shape. Export will write out all the deformers on the shape node into one file. If a pattern is
          supplied for the shape name (i.e: pCylinder\*), only the first shape that matches the pattern will be imported/exported
          unless used in conjunction with the -skip option.
    
      - skip : sk                      (unicode)       [create,query,edit]
          Skip any deformer, shape, or layer that whose name matches the given regular expression string
    
      - vertexConnections : vc         (bool)          [create,query,edit]
          Export vertex connection information, which is required for -m/-method barycentricand bilinear. The flag is only used
          with -ex/-export flag. The vertex connection information is automatically loaded during import if available in xml file.
    
      - weightPrecision : wp           (int)           [create,query,edit]
          Sets the output decimal precision for exported weights. The default value is 3.
    
      - weightTolerance : wt           (float)         [create,query,edit]
          The weight tolerance is used to decide if a given weight value is close enough to the default value that it does not
          need to be included. This flag is only used with export. The default value is .001.
    
      - worldSpace : ws                (bool)          [create,query,edit]
          For spatially based association methods (nearest), the position should be based on the world space position rather then
          the local object space.                                    Flag can have multiple arguments, passed either as a tuple or
          a list.
    
    
    Derived from mel command `maya.cmds.deformerWeights`
    """

    pass


def choice(*args, **kwargs):
    """
    The choice command provides a mechanism for changing the inputs to an attribute based on some (usually time-based)
    criteria. For example, an object could be animated from frames 1 to 30 by a motion path, then from frames 30 to 50 it
    follows keyframe animation, and after frame 50 it returns to the motion path. Or, a revolve surface could change its
    input curve depending on some transform's rotation value.The choice command creates a choice node (if one does not
    already exist) on all specified attributes of the selected objects. If the attribute was already connected to something,
    that something is now reconnected to the i'th index of the choice node's input (or the next available input if the
    -in/index flag is not specified). If a source attribute is specified, then that attribute is connected to the choice
    node's i'th input instead.The choice node operates by using the value of its selector attribute to determine which of
    its input attributes to pass through to its output. The input attributes can be of any type. For example, if the
    selector attribute was connected by an animation curve with keyframes at (1,1), (30,2) and (50,1), then that would mean
    that the choice node would pass on the data from input[1] from time 1 to 30, and after time 50, and the data from
    input[2] between times 30 and 50.This command returns the names of the created or modified choice nodes, and if a
    keyframe was added to the animation curve, it specifies the index (or value on the animation curve).
    
    Flags:
      - attribute : at                 (unicode)       [create]
          specifies the attributes onto which choice node(s) should be created. The default is all keyable attributes of the given
          objects. Note that although this flag is not queryable, it can be used to qualify which attributes of the given objects
          to query.
    
      - controlPoints : cp             (bool)          [create]
          Explicitly specify whether or not to include the control points of a shape (see -sflag) in the list of attributes.
          Default: false.
    
      - index : index                  (int)           [create,query]
          specifies the multi-input index of the choice node to connect the source attribute to. When queried, returns a list of
          integers one per specified -t/time that indicates the multi-index of the choice node to use at that time.
    
      - name : n                       (unicode)       [create,query]
          the name to give to any newly created choice node(s). When queried, returns a list of strings.
    
      - selector : sl                  (PyNode)        [create,query]
          specifies the attribute to be used as the choice node's selector. The value of the selector at a given time determines
          which of the choice node's multi-indices should be used as the output of the choice node at that time. This flag is only
          editable (it cannot be specified at creation time). When queried, returns a list of strings.
    
      - shape : s                      (bool)          [create]
          Consider all attributes of shapes below transforms as well, except controlPoints. Default: true
    
      - sourceAttribute : sa           (PyNode)        [create]
          specifies the attribute to connect to the choice node that will be selected at the given time(s) specified by -t/time.
    
      - time : t                       (time)          [create]
          specifies the time at which the choice should use the given source attribute, or the currently connected attribute if
          source attribute is not specified. The default is the curren time. Note that although this flag is not queryable, it can
          be used to qualify the times at which to query the other attributes.       Flag can have multiple arguments, passed
          either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.choice`
    """

    pass


def timeEditorClip(*args, **kwargs):
    """
    This command edits/queries Time Editor clips.
    
    Flags:
      - absolute : abs                 (bool)          [query]
          This flag is used in conjunction with other timing flags like -s/start, -d/duration, -ed/end, etc. to query (global)
          absolute time.
    
      - addAttribute : aa              (unicode)       [edit]
          Add new attribute to the clip (and anim  Animation Source)
    
      - addObjects : ao                (unicode)       [create,query,edit]
          Populate the given object(s) and their attributes to anim source to Time Editor. For multiple object, pass each name
          separated by semicolon. In query mode, return the number of attributes that will be populated given the flags, along
          with the animation's first and last frames for the given object(s). Similar to -addSelectedObjectsflag but acts on given
          object(s) instead. This flag will override the flag -addSelectedObjects.
    
      - addRelatedKG : akg             (bool)          [create,query,edit]
          During population, determine if associated keying groups should be populated or not. Normally used for populating HIK.
          By default the value is false.
    
      - addSelectedObjects : aso       (bool)          [create,query,edit]
          Populate the currently selected objects and their attributes to anim source or Time Editor. In query mode, return the
          number of attributes that will be populated given the flags, along with the animation's first and last frames.
    
      - allowShrinking : eas           (bool)          [edit]
          When extending clip, allow shrinking.
    
      - animSource : asr               (unicode)       [create,query,edit]
          Populate based on animation source.
    
      - attribute : at                 (unicode)       [create,edit]
          Populate a specific attribute on a object.
    
      - audio : au                     (unicode)       [create]
          Create a clip with audio inside.
    
      - children : chl                 (int)           [query]
          Get children clip IDs.
    
      - clipAfter : ca                 (bool)          [query]
          Get the clip ID of the next clip.
    
      - clipBefore : cb                (bool)          [query]
          Get the clip ID of the previous clip.
    
      - clipDataType : cdt             (bool)          [query]
          Query the type of data being driven by the given clip ID. Return values are: 0 : Animation       - Clip drives animation
          curves1 : Audio           - Clip drives audio3 : Group           - Clip is a group
    
      - clipId : id                    (int)           [create,edit]
          ID of the clip to be edited.
    
      - clipIdFromNodeName : idn       (int)           [query]
          Get clip ID from clip node name.
    
      - clipIdFromPath : idp           (unicode)       [query]
          Flag for querying the clip ID given the path. Clip path is a period-delimited string to indicate a hierarchical
          structure of a clip. Please refer to the hierarchical path in outliner to see how it is represented. For example:
          composition1|track1|clip1 Note: To specify the path, this flag must appear before -query flag.
    
      - clipNode : cln                 (bool)          [query]
          Flag for querying the name of the clip node.
    
      - clipPath : clp                 (bool)          [query]
          Flag for querying the path given the clip ID. Clip path is a period-delimited string to indicate a hierarchical
          structure of a clip. Please refer to the hierarchical path in outliner to see how it is represented. For example:
          composition1|track1|clip1. Note: If the clip is not connected to any track, it will return empty string.
    
      - copyClip : ccl                 (bool)          [edit]
          Get the selected clip IDs and store them in a list that could be used for pasting.
    
      - crossfadeMode : cfm            (int)           [query,edit]
          Set the crossfading mode between two clips that lie on the same track, and that are specified with the clipId flags: 0 :
          linear          - Two clips are blended with a constant ratio1 : step            - Left clip keeps its value until the
          middle of the crossfading region and then right clip's value is used2 : hold left       - Use only left clip's value3 :
          hold right      - Use only right clip's value4 : custom          - User defined crossfade curve5 : custom (spline) -
          User defined crossfade curve with spline preset
    
      - crossfadePlug : cfp            (bool)          [query]
          Get plug path for a custom crossfade curve between 2 clips.
    
      - curveTime : cvt                (time)          [query]
          Query the curve local time in relation to the given clip.
    
      - defaultGhostRoot : dgr         (bool)          [query,edit]
          Edit or query default ghost root variable. Determine whether to use the default ghost root (object driven by clip).
    
      - drivenAttributes : dat         (bool)          [query]
          Return a list of attributes driven by a clip.
    
      - drivenClipsBySource : dcs      (unicode)       [query]
          Returns the clips driven by the given source. Can filter the return result by the specified type, like animCurve,
          expression, constraint, etc. This flag must come before the -query flag.
    
      - drivenObjects : dos            (bool)          [query]
          Return an array of strings consisting of the names of all objects driven by the current clip and its children clips.
    
      - drivingSources : dsc           (unicode)       [query]
          Return all sources driving the given clip. Can filter the return result by the specified type, like animCurve,
          expression, constraint, etc. If used after the -query flag (without an argument), the command returns all sources
          driving the given clip. To specify the type, this flag must appear before the -query flag. In query mode, this flag can
          accept a value.
    
      - duplicateClip : dcl            (bool)          [edit]
          Duplicate clip into two clips with the same timing info.
    
      - duration : d                   (time)          [create,query]
          Relative duration of the new clip.
    
      - endTime : et                   (time)          [query]
          Query the relative end time of the clip.
    
      - exclusive : exc                (bool)          [create,edit]
          Populate all types of animation sources which are not listed by typeFlag.
    
      - exists : exs                   (bool)          [query]
          Return true if the specified clip exists.
    
      - explode : epl                  (int)           [edit]
          Reparent all tracks and their clips within a group out to its parent track node and remove the group.
    
      - exportAllClips : eac           (bool)          [edit]
          When used with the ef/exportFbxflag, export all clips.
    
      - exportFbx : ef                 (unicode)       [edit]
          Export currently selected clips to FBX files.
    
      - extend : ex                    (bool)          [edit]
          Extend the clip to encompass all children.
    
      - extendParent : exp             (bool)          [edit]
          Extend parent to fit this clip.
    
      - extendParents : xcp            (bool)          [edit]
          Extend the parent clip start and duration.
    
      - ghost : gh                     (bool)          [query,edit]
          Enable/disable ghosting for the specified clip.
    
      - ghostRootAdd : gra             (unicode)       [edit]
          Add path to specified node as a custom ghost root.
    
      - ghostRootRemove : grr          (unicode)       [edit]
          Remove path to specified node as a custom ghost root.
    
      - group : grp                    (bool)          [create]
          Specify if the new container should be created as a group, containing other specified clips.
    
      - holdEnd : he                   (time)          [query,edit]
          Hold clip's end to time
    
      - holdStart : hs                 (time)          [query,edit]
          Hold clip's start to time.
    
      - importAllFbxTakes : aft        (bool)          [create]
          Import all FBX takes into the new anim sources (for timeEditorAnimSource command) or new containers (for timeEditorClip
          command).
    
      - importFbx : fbx                (unicode)       [create]
          Import an animation from FBX file into the new anim source (for timeEditorAnimSource command) or new container (for
          timeEditorClip command).
    
      - importFbxTakes : ft            (unicode)       [create]
          Import multiple FBX takes (separated by semicolons) into the new anim sources (for timeEditorAnimSource command) or new
          containers (for timeEditorClip command).
    
      - importMayaFile : mf            (unicode)       [create]
          Import an animation from Maya file into the new anim sources (for timeEditorAnimSource command) or new containers (for
          timeEditorClip command).
    
      - importOption : io              (unicode)       [edit]
          Option for importing animation source. Specify either 'connect' or 'generate'. connect:  Only connect with nodes already
          existing in the scene.                   Importing an animation source which does not match with any element
          of the current scene will not create any clip.                   (connect is the default mode). generate: Import
          everything and generate new nodes for items not existing in the scene.
    
      - importPopulateOption : ipo     (unicode)       [edit]
          Option for population when importing.
    
      - importTakeDestination : itd    (int)           [create]
          Specify how to organize imported FBX takes: 0 - Import takes into a group (default) 1 - Import takes into multiple
          compositions 2 - Import takes as a sequence of clips
    
      - importedContainerNames : icn   (unicode)       [create]
          Internal use only. To be used along with populateImportedAnimSourcesto specify names for the created containers.
    
      - includeRoot : irt              (bool)          [create,edit]
          Populate TRS of hierarchy root nodes.
    
      - isContainer : ict              (bool)          [query]
          Indicate if given clip ID is a container.
    
      - listUserGhostRoot : lug        (bool)          [query]
          Get user defined ghost root object for indicated clips.
    
      - loopEnd : le                   (time)          [query,edit]
          Loop clip's end to time.
    
      - loopStart : ls                 (time)          [query,edit]
          Loop clip's start to time.
    
      - minClipDuration : mcd          (bool)          [query]
          Returns the minimum allowed clip duration
    
      - modifyAnimSource : mas         (bool)          [create,edit]
          When populating, automatically modify anim source without asking the user.
    
      - moveClip : mcl                 (time)          [edit]
          Move clip by adding delta to its start time.
    
      - mute : m                       (bool)          [query,edit]
          Mute/Unmute the clip given a clip ID. In query mode, return the muted state of the clip. Clips muted by soloing are not
          affected by this flag.
    
      - name : n                       (unicode)       [query,edit]
          Name of the clip. A clip will never have an empty name. If an empty string is provided, it will be replaced with _.
    
      - parent : p                     (int)           [edit]
          Specify group/object parent ID.
    
      - parentClipId : pid             (int)           [create,query]
          Specify the parent clip ID of a clip to be created.
    
      - parentGroupId : pgd            (bool)          [query]
          Return the parent group ID of the given clip.
    
      - pasteClip : pcl                (time)          [edit]
          Paste clip to the given time and track. Destination track is required to be specified through the track flag in the
          format tracksNode:trackIndex. A trackIndex of -1 indicates that a new track will be created.
    
      - path : pt                      (unicode)       [edit]
          Full path of the clip to be edited. For example: composition1|track1|clip1. In query mode, this flag can accept a value.
    
      - populateImportedAnimSources : pia (unicode)       [create]
          Internal use only. Populate the Time Editor with clips using the Animation Sources specified (use ; as a delimiter for
          multiple anim sources).
    
      - poseClip : poc                 (bool)          [create]
          Populate as pose clip with current attribute values.
    
      - preserveAnimationTiming : pat  (bool)          [create]
          When used with the population command, it ensures the animation is offset within a clip in such way that it matches its
          original scene timing, regardless of the new clip's position.
    
      - razorClip : rcl                (time)          [edit]
          Razor clip into two clips at the specified time.
    
      - recursively : rec              (bool)          [create,edit]
          Populate selection recursively, adding all the children.
    
      - remap : rmp                    (unicode, unicode) [edit]
          Change animation source for a given clip item to a new one, specified by the target path. This removes all clips for the
          roster item and creates new clips from the anim source for the new target path.
    
      - remapSource : rs               (unicode, unicode) [edit]
          Set animation source to be remapped for a given clip item to new one, specified by the target path.
    
      - remappedSourceAttrs : rms      (bool)          [query]
          Return an array of attribute indices and names of the source attributes of a remapped clip.
    
      - remappedTargetAttrs : rmt      (bool)          [query]
          Return an array of attribute indices and names of the target attributes of a remapped clip.
    
      - removeAttribute : ra           (unicode)       [edit]
          ARemove attribute to the clip
    
      - removeClip : rmc               (bool)          [edit]
          Remove clip of specified ID.
    
      - removeCrossfade : rcf          (bool)          [edit]
          Remove custom crossfade between two clips specified by clipId flags.
    
      - removeSceneAnimation : rsa     (bool)          [create,edit]
          If true, remove animation from scene when creating clips or anim sources. Only Time Editor will drive the removed scene
          animation.
    
      - removeWeightCurve : rwc        (bool)          [create,query,edit]
          Remove the weight curve connected to the clip.
    
      - resetTiming : rt               (bool)          [edit]
          Reset start and duration of a clip with the given clip ID to the values stored in its Anim Source.
    
      - resetTransition : rtr          (bool)          [edit]
          Reset transition intervals between specified clips.
    
      - ripple : rpl                   (bool)          [edit]
          Apply rippling to a clip operation.
    
      - rootClipId : rti               (int)           [edit]
          ID of the root clip. It is used together with various clip editing flags. When used, the effect of clip editing and its
          parameters will be affected by the given root clip. For example, moving a clip under the group root (usually in group
          tab view) will be performed in the local time space of the group root.
    
      - rootPath : rpt                 (unicode)       [edit]
          Path of the root clip. It is used together with various clip editing flags. When used, the effect of clip editing and
          its parameters will be affected by the given root clip. For example, moving a clip under the group root (usually in
          group tab view) will be performed in the local time space of the group root.
    
      - scaleEnd : sce                 (time)          [edit]
          Scale the end time of the clip to the given time.
    
      - scalePivot : scp               (time)          [edit]
          Scale the time of the clip based on the pivot. This should be used together with -scs/scaleStartor -sce/scaleEnd.
    
      - scaleStart : scs               (time)          [edit]
          Scale the start time of the clip to the given time.
    
      - setKeyframe : k                (unicode)       [edit]
          Set keyframe on a specific clip for a specified attribute.
    
      - showAnimSourceRemapping : sar  (bool)          [create]
          Show a remapping dialog when the imported anim source attributes do not match the scene attributes.
    
      - speedRamping : src             (int)           [query,edit]
          To control the playback speed of the clip by animation curve: 1 : create - Attach a speed curve and a time warp curve to
          the clip to control the playback speed2 : edit - Open the Graph editor to edit the speed curve3 : enable - Create a time
          warp curve from current speed curve and attach to clip4 : disable - Remove the time warp curve from clip5 : delete -
          Delete the attached speed curve and time warp curve6 : reset - Reset the speed curve back to the default7 : convert to
          speed curve from time warp8 : convert to time warp from speed curveIn query mode, return true if a speed curve is
          attached to the clip.
    
      - startTime : s                  (time)          [create,query]
          Relative start time of the new clip.
    
      - takeList : tl                  (unicode)       [create]
          Internal use only. To be used along with populateImportedAnimSourcesto specify the imported take names.
    
      - takesToImport : toi            (unicode)       [create]
          Internal use only. To be used along with populateImportedAnimSourcesto specify the imported take indices.
    
      - timeWarp : tw                  (bool)          [query]
          Return true if the clip is being warped by the speed curve. If no speed curve is attached to the clip, it will always
          return false.
    
      - timeWarpCurve : twc            (bool)          [query]
          Returns the name of the time warp curve connected to the clip.
    
      - timeWarpType : twt             (int)           [query,edit]
          Time warp mode: 0: remapping - Connected time warp curve performs frame by frame remapping1: speed curve - Connected
          time warp curve acts as a speed curveIn query mode, return time warp mode of a clip.
    
      - track : trk                    (unicode)       [create,query,edit]
          Track new container will be created on in the format trackNode:trackNumberor track path. For example:
          composition1|track1In query mode, return a string containing the track number and tracks node of the given clip ID. In
          create mode, if track number is passed in with a '-1' or not given in path a new track would be created. For example:
          trackNode:-1; composition1|
    
      - tracksNode : trn               (bool)          [query]
          Get tracks node if specified clip is a group clip.
    
      - transition : tra               (bool)          [edit]
          Create transition intervals between specified clips.
    
      - trimEnd : tre                  (time)          [edit]
          Trim the end time of the clip to the given time.
    
      - trimStart : trs                (time)          [edit]
          Trim the start time of the clip to the given time.
    
      - truncated : trc                (bool)          [query]
          This flag is used in conjunction with other timing flags like -s/start, -d/duration, -ed/end, etc. to query (global)
          truncated time.
    
      - type : typ                     (unicode)       [create,query,edit]
          Only populate the specified type of animation source.                              Flag can have multiple arguments,
          passed either as a tuple or a list.
    
      - uniqueAnimSource : uas         (bool)          [edit]
          If a given clip is sharing its anim source node with another clip, make the anim source of this clip unique.
    
      - userGhostRoot : ugr            (bool)          [query,edit]
          Edit or query custom ghost root variable. Determine whether to use user defined ghost root.
    
      - weightCurve : wc               (bool)          [create,query,edit]
          In edit mode, create a weight curve and connect it to the clip. In query mode, return the name of the weight curve
          connected to the clip.
    
      - zeroKeying : zk                (bool)          [edit]
          A toggle flag to use in conjunction with k/setKeyframe, set the value of the key frame(s) to be keyed to zero.
    
    
    Derived from mel command `maya.cmds.timeEditorClip`
    """

    pass


def timeEditorComposition(*args, **kwargs):
    """
    Commands related to composition management inside Time Editor.
    
    Flags:
      - active : act                   (bool)          [query,edit]
          Query or edit the active composition.
    
      - allCompositions : acp          (bool)          [query]
          Return all compositions inside Time Editor.
    
      - createTrack : ct               (bool)          [create]
          Create a default track when creating a new composition.
    
      - delete : delete                (bool)          [query,edit]
          Delete the composition.
    
      - duplicateFrom : df             (unicode)       [create]
          Duplicate the composition.
    
      - rename : ren                   (unicode, unicode) [edit]
          Rename the composition of the first name to the second name.
    
      - tracksNode : tn                (bool)          [query]
          Query the tracks node of a composition.                                    Flag can have multiple arguments, passed
          either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.timeEditorComposition`
    """

    pass


def ikSolver(*args, **kwargs):
    """
    The ikSolver command is used to set the attributes for an IK Solver or create a new one. The standard edit (-e) and
    query (-q) flags are used for edit and query functions.
    
    Flags:
      - epsilon : ep                   (float)         [create,query,edit]
          max error
    
      - maxIterations : mxi            (int)           [create,query,edit]
          Sets the max iterations for a solution
    
      - name : n                       (unicode)       [create,query,edit]
          Name of solver
    
      - solverType : st                (unicode)       [create,query,edit]
          valid solverType (only ikSystem knows what is valid) for creation of a new solver (required)                  Flag can
          have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.ikSolver`
    """

    pass


def shapeEditor(*args, **kwargs):
    """
    This command creates an editor that derives from the base editor class that has controls for deformer, control nodes.
    
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
    
      - targetControlList : tcl        (bool)          [query]
    
      - targetList : tl                (bool)          [query]
    
      - unParent : up                  (bool)          [create,edit]
          Specifies that the editor should be removed from its layout. This cannot be used in query mode.
    
      - unlockMainConnection : ulk     (bool)          [create,edit]
          Unlocks the mainConnection, effectively restoring the original mainConnection (if it is still available), and dynamic
          updates.
    
      - updateMainConnection : upd     (bool)          [create,edit]
          Causes a locked mainConnection to be updated from the orginal mainConnection, but preserves the lock state.
    
      - useTemplate : ut               (unicode)       [create]
          Forces the command to use a command template other than the current one.
    
      - verticalSliders : vs           (bool)          [create,query,edit]
          Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.shapeEditor`
    """

    pass


def readTake(*args, **kwargs):
    """
    This action reads a take (.mov) file to a defined device. See also: writeTake, applyTake
    
    Flags:
      - angle : a                      (unicode)       [create]
          Sets the angular unit used in the take. Valid strings are deg, degree, rad, and radian. C: The default is the current
          user angular unit.
    
      - device : d                     (unicode)       [create]
          Specifies the device into which the take data is read. This is a required argument.
    
      - frequency : f                  (float)         [create]
          The timestamp is ignored and the specified frequency is used. If timeStamp data is not in the .mov file, the
          -noTimestamp flag should also be used. This flag resample, instead the data is assumed to be at the specified frequency.
          C: If the take file does not use time stamps, the default frequency is 60Hz.
    
      - linear : l                     (unicode)       [create]
          Sets the linear unit used in the take. Valid strings are mm, millimeter, cm, centimeter, m, meter, km, kilometer, in,
          inch, ft, foot, yd, yard, mi, and mile. C: The default is the current user linear unit.
    
      - noTime : nt                    (bool)          [create]
          Specifies if the take (.mov) file contains time stamps. C: The default is to assume time stamps are part of the take
          file.
    
      - take : t                       (unicode)       [create]
          Reads the specified take file. It is safest to pass the full path to the flag.                  Flag can have multiple
          arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.readTake`
    """

    pass


def buildKeyframeMenu(*args, **kwargs):
    """
    This command handles building the dynamicKeyframe menu, to show attributes of currently selected objects, filtered by
    the current manipulator. menuName is the string returned by the menucommand. The target menu will entries appended to it
    (and deleted from it) to always show what's currently keyframable.
    
    
    Derived from mel command `maya.cmds.buildKeyframeMenu`
    """

    pass


def _constraint(func):
    pass


def scaleKey(*args, **kwargs):
    """
    This command operates on a keyset.  A keyset is defined as a group of keys within a specified time range on one or more
    animation curves. The animation curves comprising a keyset depend on the value of the -animationflag: keysOrObjects: Any
    active keys, when no target objects or -attribute flags appear on the command line, orAll animation curves connected to
    all keyframable attributes of objects specified as the command line's targetList, when there are no active keys.keys:
    Only act on active keys or tangents. If there are no active keys or tangents, don't do anything. objects: Only act on
    specified objects.  If there are no objects specified, don't do anything. Note that the -animationflag can be used to
    override the curves uniquely identified by the multi-use -attributeflag, which takes an argument of the form
    attributeName, such as translateX. Keys on animation curves are identified by either their time values or their indices.
    Times and indices can be given individually or as part of a list or range. -time 10palmeans the key at frame 10 (PAL
    format).-time 1.0sec -time 15ntsc -time 20means the keys at time 1.0 second, frame 15 (in NTSC format), and time 20 (in
    the currently defined global time unit).-time 10:20means all keys in the range from 10 to 20, inclusive, in the current
    time unit.Omitting one end of a range means go to infinity, as in the following examples: -time 10:means all keys from
    time 10 (in the current time unit) onwards.-time :10means all keys up to (and including) time 10 (in the current time
    unit).-time :is a short form to specify all keys.-index 0means the first key of each animation curve. (Indices are
    0-based.)-index 2 -index 5 -index 7means the 3rd, 6th, and 8th keys.-index 1:5means the 2nd, 3rd, 4th, 5th, and 6th keys
    of each animation curve.This command takes keyframes at (or within) the specified times (or time ranges) and scales
    them.  If no times are specified, the scale is applied to active keyframes or (if no keys are active) all keys of active
    objects.
    
    Flags:
      - animation : an                 (unicode)       [create]
          Where this command should get the animation to act on.  Valid values are objects,keys,and keysOrObjectsDefault:
          keysOrObjects.(See Description for details.)
    
      - attribute : at                 (unicode)       [create]
          List of attributes to select
    
      - controlPoints : cp             (bool)          [create]
          This flag explicitly specifies whether or not to include the control points of a shape (see -sflag) in the list of
          attributes. Default: false.  (Not valid for pasteKeycmd.)
    
      - float : f                      (floatrange)    [create]
          value uniquely representing a non-time-based key (or key range) on a time-based animCurve.  Valid floatRange include
          single values (-f 10) or a string with a lower and upper bound, separated by a colon (-f 10:20
    
      - floatPivot : fp                (float)         [create]
          Scale pivot along the x-axis for float-input animCurves
    
      - floatScale : fs                (float)         [create]
          Amount of scale along the x-axis for float-input animCurves
    
      - hierarchy : hi                 (unicode)       [create]
          Hierarchy expansion options.  Valid values are above,below,both,and none.(Not valid for pasteKeycmd.)
    
      - includeUpperBound : iub        (bool)          [create]
          When the -t/time or -f/float flags represent a range of keys, this flag determines whether the keys at the upper bound
          of the range are included in the keyset. Default value: true.  This flag is only valid when the argument to the -t/time
          flag is a time range with a lower and upper bound.  (When used with the pasteKeycommand, this flag refers only to the
          time range of the target curve that is replaced, when using options such as replace,fitReplace,or scaleReplace.This flag
          has no effect on the curve pasted from the clipboard.)
    
      - index : index                  (int)           [create]
          index of a key on an animCurve
    
      - newEndFloat : nef              (float)         [create]
          The end of the float range to which the float-input targets should be scaled.
    
      - newEndTime : net               (time)          [create]
          The end of the time range to which the targets should be scaled.
    
      - newStartFloat : nsf            (float)         [create]
          The start of the float range to which the float-input targets should be scaled.
    
      - newStartTime : nst             (time)          [create]
          The start of the time range to which the time-input targets should be scaled.
    
      - scaleSpecifiedKeys : ssk       (bool)          [create]
          Determines if only the specified keys are affected by the scale. If false, other keys may be adjusted with the scale.
          The default is true.
    
      - shape : s                      (bool)          [create]
          Consider attributes of shapes below transforms as well, except controlPoints.  Default: true.  (Not valid for
          pasteKeycmd.)
    
      - time : t                       (timerange)     [create]
          time uniquely representing a key (or key range) on a time-based animCurve.  Valid timeRanges include single values (-t
          10) or a string with a lower and upper bound, separated by a colon (-t 10:20
    
      - timePivot : tp                 (time)          [create]
          Scale pivot along the time-axis for time-input animCurves
    
      - timeScale : ts                 (float)         [create]
          Amount of scale along the time-axis for time-input animCurves
    
      - valuePivot : vp                (float)         [create]
          Scale pivot along the value-axis
    
      - valueScale : vs                (float)         [create]
          Amount of scale along the value-axis                  Flag can have multiple arguments, passed either as a tuple or a
          list.
    
    
    Derived from mel command `maya.cmds.scaleKey`
    """

    pass


def mute(*args, **kwargs):
    """
    The mute command is used to disable and enable playback on a channel. When a channel is muted, it retains the value that
    it was at prior to being muted.
    
    Flags:
      - disable : d                    (bool)          [create]
          Disable muting on the channels
    
      - force : f                      (bool)          [create]
          Forceable disable of muting on the channels. If there are keys on the mute channel, the animation and mute node will
          both be removed.  If this flag is not set, then mute nodes with animation will only be disabled.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.mute`
    """

    pass


def dropoffLocator(*args, **kwargs):
    """
    This command adds one or more dropoff locators to a wire curve, one for each selected curve point. The dropoff locators
    can be used to provide localized tuning of the wire deformation about the curve point. The arguments are two floats, the
    envelope and percentage, followed by the wire node name and then by the curve point(s).
    
    
    Derived from mel command `maya.cmds.dropoffLocator`
    """

    pass


def wire(*args, **kwargs):
    """
    This command creates a wire deformer. In the create mode the selection list is treated as the object(s) to be deformed,
    Wires are specified with the -w flag. Each wire can optionally have a holder which helps define the the regon of the
    object that is affected by the deformer.
    
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
    
      - crossingEffect : ce            (float)         [create,query,edit]
          Set the amount of convolution effect. Varies from fully convolved at 0 to a simple additive effect at 1 (which is what
          you get with the filter off). Default is 0. This filter should make its way into all blend nodes that deal with
          combining effects from multiple sources.
    
      - deformerTools : dt             (bool)          [query]
          Returns the name of the deformer tool objects (if any) as string string ...
    
      - dropoffDistance : dds          (int, float)    [create,query,edit]
          Set the dropoff distance (second parameter) for the wire at index (first parameter).
    
      - envelope : en                  (float)         [create,query,edit]
          Set the envelope value for the deformer. Default is 1.0
    
      - exclusive : ex                 (unicode)       [create,query]
          Puts the deformation set in a deform partition.
    
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
    
      - groupWithBase : gw             (bool)          [create]
          Groups the wire with the base wire so that they can easily be moved together to create a ripple effect. Default is
          false.
    
      - holder : ho                    (int, unicode)  [create,query,edit]
          Set the specified curve or surface (second parameter  as a holder for the wire at index (first parameter).
    
      - ignoreSelected : ignoreSelected (bool)          [create]
          Tells the command to not deform objects on the current selection list
    
      - includeHiddenSelections : ihs  (bool)          [create]
          Apply the deformer to any visible and hidden objects in the selection list. Default is false.
    
      - localInfluence : li            (float)         [create,query,edit]
          Set the local control a wire has with respect to other wires irrespective of whether it is deforming the surface. Varies
          from no local effect at 0 to full local control at 1. Default is 0.
    
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
    
      - split : sp                     (bool)          [create,edit]
          Branches off a new chain in the dependency graph instead of inserting/appending the deformer into/onto an existing
          chain. Works in create mode (and edit mode if the deformer has no geometry added yet).
    
      - wire : w                       (unicode)       [create,query,edit]
          Specify or query the wire curve name.
    
      - wireCount : wc                 (int)           [create,query,edit]
          Set the number of wires.                  Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.wire`
    """

    pass


def marker(*args, **kwargs):
    """
    The marker command creates one or two markers, on a motion path curve, at the specified time and location. The optionnal
    string argument is the parent object name.One can specify -pm -omoption to create both, a position marker and an
    orientation marker.Since there is only one keyframe for each marker of the same type, no more than one marker of the
    same type with the same time value can exist.The default marker type is the position marker. The default time is the
    current time.
    
    Flags:
      - attach : a                     (bool)          [create]
          This flag specifies to attach the selected 3D position markers to their parent geometry.
    
      - detach : d                     (bool)          [create]
          This flag specifies to detach the selected position markers from their parent geometry to the 3D space.
    
      - frontTwist : ft                (float)         [query]
          This flag specifies the amount of twist angle about the front vector for the marker.Default is 0.When queried, this flag
          returns a angle.
    
      - orientationMarker : om         (bool)          [query]
          This flag specifies creation of an orientation marker.Default is not set..When queried, this flag returns a boolean.
    
      - positionMarker : pm            (bool)          [query]
          This flag specifies creation of a position marker.Default is set.When queried, this flag returns a boolean.
    
      - sideTwist : st                 (float)         [query]
          This flag specifies  the amount of twist angle about the side vector for the marker.Default is 0.When queried, this flag
          returns a angle.
    
      - time : t                       (time)          [query]
          This flag specifies the time for the marker.Default is the current time.When queried, this flag returns a time.
    
      - upTwist : ut                   (float)         [query]
          This flag specifies the amount of twist angle about the up vector for the marker.Default is 0.When queried, this flag
          returns a angle.
    
      - valueU : u                     (float)         [query]
          This flag specifies the location of the position marker w.r.t. the parent geometry u parameterization.Default is the
          value at current time.When queried, this flag returns a linear.                  Flag can have multiple arguments,
          passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.marker`
    """

    pass


def substituteGeometry(*args, **kwargs):
    """
    This command can be used to replace the geometry which is already connected to deformers with a new geometry. The
    weights on the old geometry will be retargeted to the new geometry.
    
    Flags:
      - disableNonSkinDeformers : dnd  (bool)          [create]
          This flag controls the state of deformers other than skin deformers after the substitution has taken place. If the flag
          is true then non-skin deformer nodes are left in a disabled state at the completion of the command. Default value is
          false.
    
      - newGeometryToLayer : ngl       (bool)          [create]
          Create a new layer for the new geometry.
    
      - oldGeometryToLayer : ogl       (bool)          [create]
          Create a new layer and move the old geometry to this layer
    
      - reWeightDistTolerance : wdt    (float)         [create]
          Specify the distance tolerance value to be used for retargeting weights. While transferring weights the command tries to
          find the corresponding vertices by overlapping the geometries with all deformers disabled. Sometimes this results in
          selection of unrelated vertices. (Example when a hole in the old geometry has been filled with new vertices in the new
          geometry.) This distance tolerance value is used to detect this kind of faults and either ignore these cases or to vary
          algorithm to find more corresponding vertices.
    
      - retainOldGeometry : rog        (bool)          [create]
          A copy of the old geometry should be retained                              Flag can have multiple arguments, passed
          either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.substituteGeometry`
    """

    pass


def sculpt(*args, **kwargs):
    """
    This command creates/edits/queries a sculpt object deformer. By default for creation mode an implicit sphere will be
    used as the sculpting object if no sculpt tool is specified. The name of the created/edited object is returned.
    
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
    
      - deformerTools : dt             (bool)          [query]
          Returns the name of the deformer tool objects (if any) as string string ...
    
      - dropoffDistance : dds          (float)         [create,query,edit]
          Specifies the distance from the surface of the sculpt object at which the sculpt object produces no deformation effect.
          Default is 1.0. When queried, this flag returns a float.
    
      - dropoffType : drt              (unicode)       [create,query,edit]
          Specifies how the deformation effect drops off from maximum effect at the surface of the sculpt object to no effect at
          dropoff distance limit. Valid values are: linear | none. Default is linear. When queried, this flag returns a string.
    
      - exclusive : ex                 (unicode)       [create,query]
          Puts the deformation set in a deform partition.
    
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
    
      - groupWithLocator : gwl         (bool)          [create]
          Groups the sculptor and its locator together under a single transform. Default is off.
    
      - ignoreSelected : ignoreSelected (bool)          [create]
          Tells the command to not deform objects on the current selection list
    
      - includeHiddenSelections : ihs  (bool)          [create]
          Apply the deformer to any visible and hidden objects in the selection list. Default is false.
    
      - insideMode : im                (unicode)       [create,query,edit]
          Specifies how the deformation algorithm deals with points that are inside the sculpting primitve. The choices are: ring
          | even. The default is even. When queried, this flag returns a string. Ring mode will tend to produce a contour like
          ring of points around the sculpt object as it passes through an object while even mode will try to spread the points out
          as evenly as possible across the surface of the sculpt object.
    
      - maxDisplacement : mxd          (float)         [create,query,edit]
          Defines the maximum amount the sculpt object may move a point on an object which it is deforming. Default is 1.0. When
          queried, this flag returns a float.
    
      - mode : m                       (unicode)       [create,query,edit]
          Specifies which deformation algorithm the sculpt object should use. The choices are: flip | project | stretch. The
          default is stretch. When queried, this flag returns a string.
    
      - name : n                       (unicode)       [create]
          Used to specify the name of the node being created.
    
      - objectCentered : oc            (bool)          [create]
          Places the sculpt and locator in the center of the bounding box of the selected object(s) or components. Default is off
          which centers the sculptor and locator at the origin.
    
      - parallel : par                 (bool)          [create,edit]
          Inserts the new deformer in a parallel chain to any existing deformers in the history of the object. A blendShape is
          inserted to blend the parallel results together. Works in create mode (and edit mode if the deformer has no geometry
          added yet).
    
      - prune : pr                     (bool)          [edit]
          Removes any points not being deformed by the deformer in its current configuration from the deformer set.
    
      - remove : rm                    (bool)          [edit]
          Specifies that objects listed after the -g flag should be removed from this deformer.
    
      - sculptTool : st                (unicode)       [create]
          Use the specified NURBS object as the sculpt tool instead of the default implicit sphere.
    
      - split : sp                     (bool)          [create,edit]
          Branches off a new chain in the dependency graph instead of inserting/appending the deformer into/onto an existing
          chain. Works in create mode (and edit mode if the deformer has no geometry added yet).                  Flag can have
          multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.sculpt`
    """

    pass


def nonLinear(*args, **kwargs):
    """
    This command creates a functional deformer of the specified type that will deform the selected objects.  The deformer
    consists of three nodes: The deformer driver that gets connected to the history of the selected objects, the deformer
    handle transform that controls position and orientation of the axis of the deformation and the deformer handle that
    maintains the deformation parameters. The type of the deformer handle shape created depends on the specified type of the
    deformer.  The deformer handle will be positioned at the center of the selected objects' bounding box and oriented to
    match the orientation of the leading object in the selection list.  The deformer handle transform will be selected when
    the command is completed. The nonLinear command has some flags which are specific to the nonLinear type specified with
    the -type flag. The flags correspond to the primary keyable attributes related to the specific type of nonLinear node.
    For example, if the type is bend, then the flags -curvature, -lowBoundand -highBoundmay be used to initialize, edit or
    query those attribute values on the bend node. Examples of this are covered in the example section below.
    
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
    
      - autoParent : ap                (bool)          [create]
          Parents the deformer handle under the selected object's transform. This flag is valid only when a single object is
          selected.
    
      - before : bf                    (bool)          [create,edit]
          If the default behavior for insertion/appending into/onto the existing chain is not the desired behavior then this flag
          can be used to force the command to place the deformer node before the selected node in the chain even if a new geometry
          shape has to be created in order to do so. Works in create mode (and edit mode if the deformer has no geometry added
          yet).
    
      - commonParent : cp              (bool)          [create]
          Creates a new transform and parents the selected object and the deformer handle under it.  This flag is valid only when
          a single object is selected.
    
      - defaultScale : ds              (bool)          [create]
          Sets the scale of the deformation handle to 1.  By default the deformation handle is scaled to the match the largest
          dimension of the selected objects' bounding box. [deformerFlags] The attributes of the deformer handle shape can be set
          upon creation, edited and queried as normal flags using either the long or the short attribute name.  e.g.
    
      - deformerTools : dt             (bool)          [query]
          Returns the name of the deformer tool objects (if any) as string string ...
    
      - exclusive : ex                 (unicode)       [create,query]
          Puts the deformation set in a deform partition.
    
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
    
      - split : sp                     (bool)          [create,edit]
          Branches off a new chain in the dependency graph instead of inserting/appending the deformer into/onto an existing
          chain. Works in create mode (and edit mode if the deformer has no geometry added yet).
    
      - type : typ                     (unicode)       [create]
          Specifies the type of deformation. The current valid deformation types are:  bend, twist, squash, flare, sine and wave
          Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.nonLinear`
    """

    pass


def copyFlexor(*args, **kwargs):
    """
    This command copies an existing bone or joint flexor from one bone (joint) to another.  The attributes of the flexor and
    their connections as well as any tweaks in on the latticeFfd are copied from the original to the new flexor.  If the
    selected bone (joint) appears to be a mirror reflection of the bone (joint) of the existing flexor then the transform of
    the ffd lattice group gets reflected to the new bone (joint).  The arguments for the command are the name of the ffd
    Lattice and the name of the destination joint. If they are not specified at the command line, they will be picked up
    from the current selection list.
    
    
    Derived from mel command `maya.cmds.copyFlexor`
    """

    pass


def pointOnPolyConstraint(*args, **kwargs):
    """
    Constrain an object's position to the position of the target object or to the average position of a number of targets. A
    pointOnPolyConstraint takes as input one or more targetDAG transform nodes at which to position the single constraint
    objectDAG transform node.  The pointOnPolyConstraint positions the constrained object at the weighted average of the
    world space position target objects.
    
    Maya Bug Fix:
      - when queried, angle offsets would be returned in radians, not current angle unit
    
    Modifications:
      - added new syntax for querying the weight of a target object, by passing the constraint first::
    
            aimConstraint( 'pCube1_aimConstraint1', q=1, weight ='pSphere1' )
            aimConstraint( 'pCube1_aimConstraint1', q=1, weight =['pSphere1', 'pCylinder1'] )
            aimConstraint( 'pCube1_aimConstraint1', q=1, weight =[] )
    
    Flags:
      - layer : l                      (unicode)       [create,edit]
          Specify the name of the animation layer where the constraint should be added.
    
      - maintainOffset : mo            (bool)          [create]
          The offset necessary to preserve the constrained object's initial position will be calculated and used as the offset.
    
      - name : n                       (unicode)       [create,query,edit]
          Sets the name of the constraint node to the specified name.  Default name is constrainedObjectName_constraintType
    
      - offset : o                     (float, float, float) [create,query,edit]
          Sets or queries the value of the offset. Default is 0,0,0.
    
      - remove : rm                    (bool)          [edit]
          removes the listed target(s) from the constraint.
    
      - skip : sk                      (unicode)       [create,edit]
          Specify the axis to be skipped. Valid values are x, y, zand none. During creation, noneis the default. This flag is
          multi-use.
    
      - targetList : tl                (bool)          [query]
          Return the list of target objects.
    
      - weight : w                     (float)         [create,query,edit]
          Sets the weight value for the specified target(s). If not given at creation time, the default value of 1.0 is used.
    
      - weightAliasList : wal          (bool)          [query]
          Returns the names of the attributes that control the weight of the target objects. Aliases are returned in the same
          order as the targets are returned by the targetList flag                  Flag can have multiple arguments, passed
          either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.pointOnPolyConstraint`
    """

    pass


def wrinkle(*args, **kwargs):
    """
    The wrinkle command is used to create a network of wrinkles on a surface. It automatically creates a network of wrinkle
    curves that control a wire deformer. The wrinkle curves are attached to a cluster deformer.
    
    Flags:
      - axis : ax                      (float, float, float) [create]
          Specifies the plane of the wrinkle.
    
      - branchCount : brc              (int)           [create]
          Specifies the number of branches per wrinkle. Default is 2.
    
      - branchDepth : bd               (int)           [create]
          Specifies the depth of the branching. Default is 0.
    
      - center : ct                    (float, float, float) [create]
          Specifies the center of the wrinkle.
    
      - crease : cr                    (unicode)       [create]
          Specifies an existing curve to serve as the wrinkle.
    
      - dropoffDistance : dds          (float)         [create]
          Specifies the dropoff distance around the center.
    
      - envelope : en                  (float)         [create]
          The envelope globally attenuates the amount of deformation. Default is 1.0.
    
      - randomness : rnd               (float)         [create]
          Amount of randomness. Default is 0.2.
    
      - style : st                     (unicode)       [create]
          Specifies the wrinkle style. Valid values are radialor tangential
    
      - thickness : th                 (float)         [create]
          Wrinkle thickness. Default is 1.0.
    
      - uvSpace : uv                   (float, float, float, float, float) [create]
          1/2 length, 1/2 breadth, rotation angle, center u, v definition of a patch in uv space where the wrinkle is to be
          constructed.
    
      - wrinkleCount : wc              (int)           [create]
          Specifies the number of wrinkle lines to be generated. Default is 3.
    
      - wrinkleIntensity : wi          (float)         [create]
          Increasing the intensity makes it more wrinkly. Default is 0.5.                  Flag can have multiple arguments,
          passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.wrinkle`
    """

    pass


def movIn(*args, **kwargs):
    """
    Imports a .mov file into animation curves connected to  the listed attributes. The attribute must be writable, since an
    animation curve will be created and connected to the attribute. If an animation curve already is connected to the
    attribute, the imported data is pasted onto that curve. The starting time used for the .mov file importation is the
    current time when the command is executed. Valid attribute types are numeric attributes; time attributes; linear
    attributes; angular attributes; compound attributes made of the types listed previously; and multi attributes composed
    of the types listed previously. If an unsuppoted attribute type is requested, the command will fail and no data will be
    imported. It is important that your user units are set to the same units used in the .mov file, otherwise linear and
    angular values will be incorrect. To export a .mov file, use the movOut command.
    
    Flags:
      - file : f                       (unicode)       [create]
          The name of the .mov file. If no extension is used, a .mov will be added.
    
      - startTime : st                 (time)          [create]
          The default start time for importing the .mov file is the current time. The startTime option sets the starting time for
          the .mov data in the current time unit.                  Flag can have multiple arguments, passed either as a tuple or a
          list.
    
    
    Derived from mel command `maya.cmds.movIn`
    """

    pass


def removeJoint(*args, **kwargs):
    """
    This command will remove the selected joint or the joint given at the command line from the skeleton. The given (or
    selected) joint should not be the root joint of the skeleton, and not have skin attached. The command works on the given
    (or selected) joint. No options or flags are necessary.
    
    
    Derived from mel command `maya.cmds.removeJoint`
    """

    pass


def pose(*args, **kwargs):
    """
    This command is used to create character poses.
    
    Flags:
      - allPoses : ap                  (bool)          [query]
          This flag is used to query all the poses in the scene.
    
      - apply : a                      (bool)          [create]
          This flag is used in conjunction with the name flag to specify a pose should be applied to the character.
    
      - name : n                       (unicode)       [create,query]
          In create mode, specify the pose name. In query mode, return a list of all the poses for the character. In apply mode,
          specify the pose to be applied.                             Flag can have multiple arguments, passed either as a tuple
          or a list.
    
    
    Derived from mel command `maya.cmds.pose`
    """

    pass


def softMod(*args, **kwargs):
    """
    The softMod command creates a softMod or edits the membership of an existing softMod. The command returns the name of
    the softMod node upon creation of a new softMod.
    
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
    
      - bindState : bs                 (bool)          [create]
          Specifying this flag adds in a compensation to ensure the softModed objects preserve their spatial position when
          softModed. This is required to prevent the geometry from jumping at the time the softMod is created in situations when
          the softMod transforms at softMod time are not identity.
    
      - curveInterpolation : ci        (int)           [create]
          Ramp interpolation corresponding to the specified curvePoint position. Integer values of 0-3 are valid, corresponding to
          none, linear, smoothand splinerespectively. This flag may only be used in conjunction with the curvePoint and curveValue
          flag.
    
      - curvePoint : cp                (float)         [create]
          Position of ramp value on normalized 0-1 scale. This flag may only be used in conjunction with the curveInterpolation
          and curveValue flags.
    
      - curveValue : cv                (float)         [create]
          Ramp value corresponding to the specified curvePoint position. This flag may only be used in conjunction with the
          curveInterpolation and curvePoint flags.
    
      - deformerTools : dt             (bool)          [query]
          Returns the name of the deformer tool objects (if any) as string string ...
    
      - envelope : en                  (float)         [create,query,edit]
          Set the envelope value for the deformer. Default is 1.0
    
      - exclusive : ex                 (unicode)       [create,query]
          Puts the deformation set in a deform partition.
    
      - falloffAroundSelection : fas   (bool)          [create]
          Falloff will be calculated around any selected components
    
      - falloffBasedOnX : fbx          (bool)          [create]
          Falloff will be calculated using the X component.
    
      - falloffBasedOnY : fby          (bool)          [create]
          Falloff will be calculated using the Y component.
    
      - falloffBasedOnZ : fbz          (bool)          [create]
          Falloff will be calculated using the Z component.
    
      - falloffCenter : fc             (float, float, float) [create]
          Set the falloff center point of the softMod.
    
      - falloffMasking : fm            (bool)          [create]
          Deformation will be restricted to selected components
    
      - falloffMode : fom              (int)           [create]
          Set the falloff method used for the softMod.
    
      - falloffRadius : fr             (float)         [create]
          Set the falloff radius of the softMod.
    
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
    
      - name : n                       (unicode)       [create]
          Used to specify the name of the node being created.
    
      - parallel : par                 (bool)          [create,edit]
          Inserts the new deformer in a parallel chain to any existing deformers in the history of the object. A blendShape is
          inserted to blend the parallel results together. Works in create mode (and edit mode if the deformer has no geometry
          added yet).
    
      - prune : pr                     (bool)          [edit]
          Removes any points not being deformed by the deformer in its current configuration from the deformer set.
    
      - relative : rel                 (bool)          [create]
          Enable relative mode for the softMod. In relative mode, Only the transformations directly above the softMod are used by
          the softMod. Default is off.
    
      - remove : rm                    (bool)          [edit]
          Specifies that objects listed after the -g flag should be removed from this deformer.
    
      - resetGeometry : rg             (bool)          [edit]
          Reset the geometry matrices for the objects being deformed by the softMod. This flag is used to get rid of undesirable
          effects that happen if you scale an object that is deformed by a softMod.
    
      - split : sp                     (bool)          [create,edit]
          Branches off a new chain in the dependency graph instead of inserting/appending the deformer into/onto an existing
          chain. Works in create mode (and edit mode if the deformer has no geometry added yet).
    
      - weightedNode : wn              (unicode, unicode) [create,query,edit]
          Transform node in the DAG above the softMod to which all percents are applied. The second node specifies the descendent
          of the first node from where the transformation matrix is evaluated. Default is the softMod handle.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.softMod`
    """

    pass


def connectJoint(*args, **kwargs):
    """
    This command will connect two skeletons based on the two selected joints. The first selected joint can be made a child
    of the parent of the second selected joint or a child of the second selected joint, depending on the flags used. Note1:
    The first selected joint must be the root of a skeleton. The second selected joint must have a parent. Note2: If a joint
    name is specified in the command line, it is used as the child and the first selected joint will be the parent. If no
    joint name is given at the command line, two joints must be selected.
    
    Flags:
      - connectMode : cm               (bool)          [create]
          The first selected joint will be parented under the parent of the second selected joint.
    
      - parentMode : pm                (bool)          [create]
          The first selected joint will be parented under the second selected joint. Both joints will be in the active
          list(selection list).                  Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.connectJoint`
    """

    pass


def reorderDeformers(*args, **kwargs):
    """
    This command changes the order in which 2 deformation nodes affect the output geometry. The first string argument is the
    name of deformer1, the second is deformer2, followed by the list of objects they deform. It inserts deformer2 before
    deformer1. Currently supported deformer nodes include: sculpt, cluster, jointCluster, lattice, wire, jointLattice,
    boneLattice, blendShape.
    
    Flags:
      - name : n                       (unicode)       [create]
          This flag is obsolete and is not used.                  Flag can have multiple arguments, passed either as a tuple or a
          list.
    
    
    Derived from mel command `maya.cmds.reorderDeformers`
    """

    pass


def blendTwoAttr(*args, **kwargs):
    """
    A blendTwoAttr nodes takes two inputs, and blends the values of the inputs from one to the other, into an output value.
    The blending of the two inputs uses a blending function, and the following formula: (1 - blendFunction) \* input[0]  +
    blendFunction \* input[1] The blendTwoAttr command can be used to blend the animation of an object to transition
    smoothly between the animation of two other objects. When the blendTwoAttr command is issued, it creates a blendTwoAttr
    node on the specified attributes, and reconnects whatever was previously connected to the attributes to the new blend
    nodes. You may also specify which two attributes should be used to blend together. The driver is used when you want to
    keyframe an object after it is being animated by a blend node. The current driver index specifies which of the two
    blended attributes should be keyframed.
    
    Flags:
      - attribute : at                 (unicode)       [create]
          A list of attributes for the selected nodes for which a blendTwoAttr node will be created.
    
      - attribute0 : at0               (PyNode)        [create,query,edit]
          The attribute that should be connected to the first input of the new blendTwoAttr node. When queried, it returns a
          string.
    
      - attribute1 : at1               (PyNode)        [create,query,edit]
          The attribute that should be connected to the second input of the new blendTwoAttr node. When queried, it returns a
          string.
    
      - blender : bl                   (PyNode)        [create,query,edit]
          The blender attribute. This is the attribute that will be connected to the newly created blendTwoAttr node(s) blender
          attribute. This attribute controls how much of each of the two attributes to use in the blend. If this flag is not
          specified, a new animation curve is created whose value goes from 1 to 0 throughout the time range specified by the -t
          flag. If -t is not specified, an abrupt change from the value of the first to the value of the second attribute will
          occur at the current time when this command is issued.
    
      - controlPoints : cp             (bool)          [create]
          Explicitly specify whether or not to include the control points of a shape (see -sflag) in the list of attributes.
          Default: false.
    
      - driver : d                     (int)           [create,query,edit]
          The index of the driver attribute for this blend node (0 or 1) When queried, it returns an integer.
    
      - name : n                       (unicode)       [create,query]
          name for the new blend node(s)
    
      - shape : s                      (bool)          [create]
          Consider all attributes of shapes below transforms as well, except controlPoints. Default: true
    
      - time : t                       (timerange)     [create]
          The time range between which the blending between the 2 attributes should occur. If a single time is specified, then the
          blend will cause an abrupt change from the first to the second attribute at that time.  If a range is specified, a
          smooth blending will occur over that time range. The default is to make a sudden transition at the current time.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.blendTwoAttr`
    """

    pass


def blendShapePanel(*args, **kwargs):
    """
    This command creates a panel that derives from the base panel class that houses a blendShapeEditor.
    
    Flags:
      - blendShapeEditor : be          (bool)          [query]
          Query only flag that returns the name of an editor to be associated with the panel.
    
      - control : ctl                  (bool)          [query]
          Returns the top level control for this panel. Usually used for getting a parent to attach popup menus. CAUTION: panels
          may not have controls at times.  This flag can return if no control is present.
    
      - copy : cp                      (unicode)       [edit]
          Makes this panel a copy of the specified panel.  Both panels must be of the same type.
    
      - createString : cs              (bool)          [edit]
          Command string used to create a panel
    
      - defineTemplate : dt            (unicode)       [create]
          Puts the command in a mode where any other flags and args are parsed and added to the command template specified in the
          argument. They will be used as default arguments in any subsequent invocations of the command when templateName is set
          as the current template.
    
      - docTag : dtg                   (unicode)       [create,query,edit]
          Attaches a tag to the Maya panel.
    
      - editString : es                (bool)          [edit]
          Command string used to edit a panel
    
      - exists : ex                    (bool)          [create]
          Returns whether the specified object exists or not. Other flags are ignored.
    
      - init : init                    (bool)          [create,edit]
          Initializes the panel's default state.  This is usually done automatically on file -new and file -open.
    
      - isUnique : iu                  (bool)          [query]
          Returns true if only one instance of this panel type is allowed.
    
      - label : l                      (unicode)       [query,edit]
          Specifies the user readable label for the panel.
    
      - menuBarVisible : mbv           (bool)          [create,query,edit]
          Controls whether the menu bar for the panel is displayed.
    
      - needsInit : ni                 (bool)          [query,edit]
          (Internal) On Edit will mark the panel as requiring initialization. Query will return whether the panel is marked for
          initialization.  Used during file -new and file -open.
    
      - parent : p                     (unicode)       [create]
          Specifies the parent layout for this panel.
    
      - popupMenuProcedure : pmp       (script)        [query,edit]
          Specifies the procedure called for building the panel's popup menu(s). The default value is buildPanelPopupMenu.  The
          procedure should take one string argument which is the panel's name.
    
      - replacePanel : rp              (unicode)       [edit]
          Will replace the specified panel with this panel.  If the target panel is within the same layout it will perform a swap.
    
      - tearOff : to                   (bool)          [query,edit]
          Will tear off this panel into a separate window with a paneLayout as the parent of the panel. When queried this flag
          will return if the panel has been torn off into its own window.
    
      - tearOffCopy : toc              (unicode)       [create]
          Will create this panel as a torn of copy of the specified source panel.
    
      - unParent : up                  (bool)          [edit]
          Specifies that the panel should be removed from its layout. This (obviously) cannot be used with query.
    
      - useTemplate : ut               (unicode)       [create]
          Forces the command to use a command template other than the current one.                  Flag can have multiple
          arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.blendShapePanel`
    """

    pass


def normalConstraint(*args, **kwargs):
    """
    Constrain an object's orientation based on the normal of the target surface(s) at the closest point(s) to the object. A
    normalConstraint takes as input one or more surface shapes (the targets) and a DAG transform node (the object).  The
    normalConstraint orients the constrained object such that the aimVector (in the object's local coordinate system) aligns
    in world space to combined normal vector.  The upVector (again the the object's local coordinate system) is aligned in
    world space with the worldUpVector.  The combined normal vector is a weighted average of the normal vector for each
    target surface at the point closest to the constrained object.
    
    Maya Bug Fix:
      - when queried, angle offsets would be returned in radians, not current angle unit
    
    Modifications:
      - added new syntax for querying the weight of a target object, by passing the constraint first::
    
            aimConstraint( 'pCube1_aimConstraint1', q=1, weight ='pSphere1' )
            aimConstraint( 'pCube1_aimConstraint1', q=1, weight =['pSphere1', 'pCylinder1'] )
            aimConstraint( 'pCube1_aimConstraint1', q=1, weight =[] )
    
    Flags:
      - aimVector : aim                (float, float, float) [create,query,edit]
          Set the aim vector.  This is the vector in local coordinates that points at the target.  If not given at creation time,
          the default value of (1.0, 0.0, 0.0) is used.
    
      - layer : l                      (unicode)       [create,edit]
          Specify the name of the animation layer where the constraint should be added.
    
      - name : n                       (unicode)       [create,query,edit]
          Sets the name of the constraint node to the specified name.  Default name is constrainedObjectName_constraintType
    
      - remove : rm                    (bool)          [edit]
          removes the listed target(s) from the constraint.
    
      - targetList : tl                (bool)          [query]
          Return the list of target objects.
    
      - upVector : u                   (float, float, float) [create,query,edit]
          Set local up vector.  This is the vector in local coordinates that aligns with the world up vector.  If not given at
          creation time, the default value of (0.0, 1.0, 0.0) is used.
    
      - weight : w                     (float)         [create,query,edit]
          Sets the weight value for the specified target(s). If not given at creation time, the default value of 1.0 is used.
    
      - weightAliasList : wal          (bool)          [query]
          Returns the names of the attributes that control the weight of the target objects. Aliases are returned in the same
          order as the targets are returned by the targetList flag
    
      - worldUpObject : wuo            (PyNode)        [create,query,edit]
          Set the DAG object use for worldUpType objectand objectrotation. See worldUpType for greater detail. The default value
          is no up object, which is interpreted as world space.
    
      - worldUpType : wut              (unicode)       [create,query,edit]
          Set the type of the world up vector computation. The worldUpType can have one of 5 values: scene, object,
          objectrotation, vector, or none. If the value is scene, the upVector is aligned with the up axis of the scene and
          worldUpVector and worldUpObject are ignored. If the value is object, the upVector is aimed as closely as possible to the
          origin of the space of the worldUpObject and the worldUpVector is ignored. If the value is objectrotationthen the
          worldUpVector is interpreted as being in the coordinate space of the worldUpObject, transformed into world space and the
          upVector is aligned as closely as possible to the result. If the value is vector, the upVector is aligned with
          worldUpVector as closely as possible and worldUpMatrix is ignored. Finally, if the value is noneno twist calculation is
          performed by the constraint, with the resulting upVectororientation based previous orientation of the constrained
          object, and the great circlerotation needed to align the aim vector with its constraint. The default worldUpType is
          vector.
    
      - worldUpVector : wu             (float, float, float) [create,query,edit]
          Set world up vector.  This is the vector in world coordinates that up vector should align with. See -wut/worldUpType
          (below)for greater detail. If not given at creation time, the default value of (0.0, 1.0, 0.0) is used.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.normalConstraint`
    """

    pass


def shotRipple(*args, **kwargs):
    """
    When Ripple Edit Mode is enabled, neighboring shots to the shot that gets manipulated are moved in sequence time to
    either make way or close up gaps corresponding to that node's editing. Given some parameters about the shot edit that
    just took place, this command will choose which other shots to move, and move them the appropriate amounts If no shot
    name is provided, the command will attempt to use the first selected shot.               In query mode, return type is
    based on queried flag.
    
    Flags:
      - deleted : d                    (bool)          [create,query,edit]
          Specify whether this ripple edit is due to a shot deletion
    
      - endDelta : ed                  (time)          [create,query,edit]
          Specify the change in the end time in frames
    
      - endTime : et                   (time)          [create,query,edit]
          Specify the initial shot end time in the sequence timeline.
    
      - startDelta : sd                (time)          [create,query,edit]
          Specify the change in the start time in frames
    
      - startTime : st                 (time)          [create,query,edit]
          Specify the initial shot start time in the sequence timeline.                              Flag can have multiple
          arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.shotRipple`
    """

    pass


def keyframeStats(*args, **kwargs):
    """
    All of the group commands position their individual controls in columns starting at column 1.  The layout of each
    control (ie. column) can be customized using the -cw/columnWidth, -co/columnOffset, -cat/columnAttach, -cal/columnAlign,
    and -adj/adjustableColumnflags.  By default, columns are left aligned with no offset and are 100 pixels wide.  Only one
    column in any group can be adjustable. This command creates, edits, queries a keyframe stats control.
    
    Flags:
      - adjustableColumn : adj         (int)           [create,edit]
          Specifies which column has an adjustable size that changes with the sizing of the layout.  The column value is a 1-based
          index.  You may also specify 0 to turn off the previous adjustable column.
    
      - adjustableColumn2 : ad2        (int)           [create,edit]
          Specifies which column has an adjustable size that changes with the size of the parent layout. Ignored if there are not
          exactly two columns.
    
      - adjustableColumn3 : ad3        (int)           [create,edit]
          Specifies that the column has an adjustable size that changes with the size of the parent layout. Ignored if there are
          not exactly three columns.
    
      - adjustableColumn4 : ad4        (int)           [create,edit]
          Specifies which column has an adjustable size that changes with the size of the parent layout. Ignored if there are not
          exactly four columns.
    
      - adjustableColumn5 : ad5        (int)           [create,edit]
          Specifies which column has an adjustable size that changes with the size of the parent layout. Ignored if there are not
          exactly five columns.
    
      - adjustableColumn6 : ad6        (int)           [create,edit]
          Specifies which column has an adjustable size that changes with the size of the parent layout. Ignored if there are not
          exactly six columns.
    
      - animEditor : ae                (unicode)       [query,edit]
          The name of the animation editor which is associated with the control
    
      - annotation : ann               (unicode)       [create,query,edit]
          Annotate the control with an extra string value.
    
      - backgroundColor : bgc          (float, float, float) [create,query,edit]
          The background color of the control. The arguments correspond to the red, green, and blue color components. Each
          component ranges in value from 0.0 to 1.0. When setting backgroundColor, the background is automatically enabled, unless
          enableBackground is also specified with a false value.
    
      - classicMode : cm               (bool)          []
    
      - columnAlign : cal              (int, unicode)  [create,edit]
          Arguments are : column number, alignment type. Possible alignments are: left | right | center. Specifies alignment type
          for the specified column.
    
      - columnAlign2 : cl2             (unicode, unicode) [create,edit]
          Sets the text alignment of both columns.  Ignored if there are not exactly two columns. Valid values are left, right,
          and center.
    
      - columnAlign3 : cl3             (unicode, unicode, unicode) [create,edit]
          Sets the text alignment for all 3 columns.  Ignored if there are not exactly 3 columns. Valid values are left, right,
          and center.
    
      - columnAlign4 : cl4             (unicode, unicode, unicode, unicode) [create,edit]
          Sets the text alignment for all 4 columns.  Ignored if there are not exactly 4 columns. Valid values are left, right,
          and center.
    
      - columnAlign5 : cl5             (unicode, unicode, unicode, unicode, unicode) [create,edit]
          Sets the text alignment for all 5 columns.  Ignored if there are not exactly 5 columns. Valid values are left, right,
          and center.
    
      - columnAlign6 : cl6             (unicode, unicode, unicode, unicode, unicode, unicode) [create,edit]
          Sets the text alignment for all 6 columns.  Ignored if there are not exactly 6 columns. Valid values are left, right,
          and center.
    
      - columnAttach : cat             (int, unicode, int) [create,edit]
          Arguments are : column number, attachment type, and offset. Possible attachments are: left | right | both. Specifies
          column attachment types and offets.
    
      - columnAttach2 : ct2            (unicode, unicode) [create,edit]
          Sets the attachment type of both columns. Ignored if there are not exactly two columns. Valid values are left, right,
          and both.
    
      - columnAttach3 : ct3            (unicode, unicode, unicode) [create,edit]
          Sets the attachment type for all 3 columns. Ignored if there are not exactly 3 columns. Valid values are left, right,
          and both.
    
      - columnAttach4 : ct4            (unicode, unicode, unicode, unicode) [create,edit]
          Sets the attachment type for all 4 columns. Ignored if there are not exactly 4 columns. Valid values are left, right,
          and both.
    
      - columnAttach5 : ct5            (unicode, unicode, unicode, unicode, unicode) [create,edit]
          Sets the attachment type for all 5 columns. Ignored if there are not exactly 5 columns. Valid values are left, right,
          and both.
    
      - columnAttach6 : ct6            (unicode, unicode, unicode, unicode, unicode, unicode) [create,edit]
          Sets the attachment type for all 6 columns. Ignored if there are not exactly 6 columns. Valid values are left, right,
          and both.
    
      - columnOffset2 : co2            (int, int)      [create,edit]
          This flag is used in conjunction with the -columnAttach2 flag.  If that flag is not used then this flag will be ignored.
          It sets the offset for the two columns.  The offsets applied are based on the attachments specified with the
          -columnAttach2 flag.  Ignored if there are not exactly two columns.
    
      - columnOffset3 : co3            (int, int, int) [create,edit]
          This flag is used in conjunction with the -columnAttach3 flag.  If that flag is not used then this flag will be ignored.
          It sets the offset for the three columns.  The offsets applied are based on the attachments specified with the
          -columnAttach3 flag.  Ignored if there are not exactly three columns.
    
      - columnOffset4 : co4            (int, int, int, int) [create,edit]
          This flag is used in conjunction with the -columnAttach4 flag.  If that flag is not used then this flag will be ignored.
          It sets the offset for the four columns.  The offsets applied are based on the attachments specified with the
          -columnAttach4 flag.  Ignored if there are not exactly four columns.
    
      - columnOffset5 : co5            (int, int, int, int, int) [create,edit]
          This flag is used in conjunction with the -columnAttach5 flag.  If that flag is not used then this flag will be ignored.
          It sets the offset for the five columns.  The offsets applied are based on the attachments specified with the
          -columnAttach5 flag.  Ignored if there are not exactly five columns.
    
      - columnOffset6 : co6            (int, int, int, int, int, int) [create,edit]
          This flag is used in conjunction with the -columnAttach6 flag.  If that flag is not used then this flag will be ignored.
          It sets the offset for the six columns.  The offsets applied are based on the attachments specified with the
          -columnAttach6 flag.  Ignored if there are not exactly six columns.
    
      - columnWidth : cw               (int, int)      [create,edit]
          Arguments are : column number, column width. Sets the width of the specified column where the first parameter specifies
          the column (1 based index) and the second parameter specifies the width.
    
      - columnWidth1 : cw1             (int)           [create,edit]
          Sets the width of the first column. Ignored if there is not exactly one column.
    
      - columnWidth2 : cw2             (int, int)      [create,edit]
          Sets the column widths of both columns. Ignored if there are not exactly two columns.
    
      - columnWidth3 : cw3             (int, int, int) [create,edit]
          Sets the column widths for all 3 columns. Ignored if there are not exactly 3 columns.
    
      - columnWidth4 : cw4             (int, int, int, int) [create,edit]
          Sets the column widths for all 4 columns. Ignored if there are not exactly 4 columns.
    
      - columnWidth5 : cw5             (int, int, int, int, int) [create,edit]
          Sets the column widths for all 5 columns. Ignored if there are not exactly 5 columns.
    
      - columnWidth6 : cw6             (int, int, int, int, int, int) [create,edit]
          Sets the column widths for all 6 columns. Ignored if there are not exactly 6 columns.
    
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
    
      - precision : pre                (int)           [query,edit]
          Controls the number of digits to the right of the decimal point that will be displayed for float-valued channels.
          Default is 3.  Queried, returns an int.
    
      - preventOverride : po           (bool)          [create,query,edit]
          If true, this flag disallows overriding the control's attribute via the control's right mouse button menu.
    
      - rowAttach : rat                (int, unicode, int) [create,edit]
          Arguments are : column, attachment type, offset. Possible attachments are: top | bottom | both. Specifies attachment
          types and offsets for the entire row.
    
      - timeAnnotation : tan           (unicode)       [create,query,edit]
          Annotate the time field with an extra string value.
    
      - useTemplate : ut               (unicode)       [create]
          Forces the command to use a command template other than the current one.
    
      - valueAnnotation : van          (unicode)       [create,query,edit]
          Annotate the value field with an extra string value.
    
      - visible : vis                  (bool)          [create,query,edit]
          The visible state of the control.  A control is created visible by default.  Note that a control's actual appearance is
          also dependent on the visible state of its parent layout(s).
    
      - visibleChangeCommand : vcc     (script)        [create,query,edit]
          Command that gets executed when visible state of the control changes.
    
      - width : w                      (int)           [create,query,edit]
          The width of the control.  The control will attempt to be this size if it is not overruled by parent layout conditions.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.keyframeStats`
    """

    pass


def shapePanel(*args, **kwargs):
    """
    This command creates a panel that derives from the base panel class that houses a shapeEditor.
    
    Flags:
      - control : ctl                  (bool)          [query]
          Returns the top level control for this panel. Usually used for getting a parent to attach popup menus. CAUTION: panels
          may not have controls at times.  This flag can return if no control is present.
    
      - copy : cp                      (unicode)       [edit]
          Makes this panel a copy of the specified panel.  Both panels must be of the same type.
    
      - createString : cs              (bool)          [edit]
          Command string used to create a panel
    
      - defineTemplate : dt            (unicode)       [create]
          Puts the command in a mode where any other flags and args are parsed and added to the command template specified in the
          argument. They will be used as default arguments in any subsequent invocations of the command when templateName is set
          as the current template.
    
      - docTag : dtg                   (unicode)       [create,query,edit]
          Attaches a tag to the Maya panel.
    
      - editString : es                (bool)          [edit]
          Command string used to edit a panel
    
      - exists : ex                    (bool)          [create]
          Returns whether the specified object exists or not. Other flags are ignored.
    
      - init : init                    (bool)          [create,edit]
          Initializes the panel's default state.  This is usually done automatically on file -new and file -open.
    
      - isUnique : iu                  (bool)          [query]
          Returns true if only one instance of this panel type is allowed.
    
      - label : l                      (unicode)       [query,edit]
          Specifies the user readable label for the panel.
    
      - menuBarVisible : mbv           (bool)          [create,query,edit]
          Controls whether the menu bar for the panel is displayed.
    
      - needsInit : ni                 (bool)          [query,edit]
          (Internal) On Edit will mark the panel as requiring initialization. Query will return whether the panel is marked for
          initialization.  Used during file -new and file -open.
    
      - parent : p                     (unicode)       [create]
          Specifies the parent layout for this panel.
    
      - popupMenuProcedure : pmp       (script)        [query,edit]
          Specifies the procedure called for building the panel's popup menu(s). The default value is buildPanelPopupMenu.  The
          procedure should take one string argument which is the panel's name.
    
      - replacePanel : rp              (unicode)       [edit]
          Will replace the specified panel with this panel.  If the target panel is within the same layout it will perform a swap.
    
      - shapeEditor : se               (bool)          [query]
          Query only flag that returns the name of an editor to be associated with the panel.
    
      - tearOff : to                   (bool)          [query,edit]
          Will tear off this panel into a separate window with a paneLayout as the parent of the panel. When queried this flag
          will return if the panel has been torn off into its own window.
    
      - tearOffCopy : toc              (unicode)       [create]
          Will create this panel as a torn of copy of the specified source panel.
    
      - unParent : up                  (bool)          [edit]
          Specifies that the panel should be removed from its layout. This (obviously) cannot be used with query.
    
      - useTemplate : ut               (unicode)       [create]
          Forces the command to use a command template other than the current one.                  Flag can have multiple
          arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.shapePanel`
    """

    pass


def clipSchedule(*args, **kwargs):
    """
    This command is used to create, edit and query clips and blends in the Trax editor. It operates on the clipScheduler
    node attached to the character. In query mode, if no flags are specified, returns an array of strings in this form:
    (clipName,clipIndex,clipStart,clipSourceStart,clipSourceEnd,clipScale,clipPreCycle,clipPostCycle,clipHold)
    
    Flags:
      - allAbsolute : aa               (bool)          [query,edit]
          Set all channels to be calculated with absolute offsets.  This flag cannot be used in conjunction with the
          ar/allRelative, ra/rotationsAbsolute or da/defaultAbsolute flags.
    
      - allRelative : ar               (bool)          [query,edit]
          Set all channels to be calculated with relative offsets.  This flag cannot be used in conjunction with the
          aa/allAbsolute, ra/rotationsAbsolute or da/defaultAbsolute flags.
    
      - blend : b                      (int, int)      [create,query]
          This flag is used to blend two clips, whose indices are provided as flag arguments.
    
      - blendNode : bn                 (int, int)      [query]
          This query only flag list all of the blend nodes associated with the blend defined by the two clip indices. This flag
          returns a string array. In query mode, this flag can accept a value.
    
      - blendUsingNode : bun           (unicode)       [create]
          This flag is used to blend using an existing blend node. It is used in conjunction with the blend flag. The blend flag
          specifies the clip indices for the blend. The name of an existing animBlend node should be supplied supplied as an
          argument for the blendUsingNode flag.
    
      - character : ch                 (bool)          [query]
          This flag is used to query which characters this scheduler controls. It returns an array of strings.
    
      - clipIndex : ci                 (int)           [create,query]
          Specify the index of the clip to schedule. In query mode, returns an array of strings in this form:
          (clipName,index,start,sourceStart,sourceEnd,scale,preCycle,postCycle) In query mode, this flag can accept a value.
    
      - cycle : c                      (float)         [create,query]
          This flag is now obsolete. Use the postCycle flag instead.
    
      - defaultAbsolute : da           (bool)          [query,edit]
          Sets all top-level channels except rotations in the clip to relative, and the remaining channels to absolute. This is
          the default during clip creation if no offset flag is specified.  This flag cannot be used in conjunction with the
          aa/allAbsolute, ar/allRelative, or ra/rotationsAbsolute flags.
    
      - enable : en                    (bool)          [create,query]
          This flag is used to enable or disable a clip. It must be used in conjunction with the ci/clipIndex flag. The specified
          clip will be enabled or disabled.
    
      - group : grp                    (bool)          [create]
          This flag is used to add (true) or remove (false) a list of clips (specified with groupIndex) into a group.
    
      - groupIndex : gri               (int)           [create]
          This flag specifies a multiple number of clips to be added or removed from a group.
    
      - groupName : gn                 (unicode)       [create,query]
          This flag is used to specify the group that should be added to.  If no group by that name exists and new group is
          created with that name.  By default if this is not specified a new group will be created.
    
      - hold : ph                      (time)          [create,query]
          Specify how long to hold the last value of the clip after its normal or cycled end.
    
      - insertTrack : it               (int)           [create]
          This flag is used to insert a new empty track at the track index specified.
    
      - instance : instance            (unicode)       [create]
          Create an instanced copy of the named clip. An instanced clip is one that is linked to an original clip. Thus, changes
          to the animation curve of the original curve will also modify all instanced clips. The name of the instanced clip is
          returned as a string.
    
      - listCurves : lc                (bool)          [create,query]
          This flag is used to list the animation curves associated with a clip. It should be used in conjunction with the
          clipIndex flag, which specifies the clip of interest.
    
      - listPairs : lp                 (bool)          [query]
          This query only flag returns a string array containing the channels in a character that are used by a clip and the names
          of the animation curves that drive the channels. Each string in the string array consists of the name of a channel, a
          space, and the name of the animation curve animating that channel. This flag must be used with the ci/clipIndex flag.
    
      - lock : l                       (bool)          [query,edit]
          This flag specifies whether clips on a track are to be locked or not. Must be used in conjuction with the track flag.
    
      - mute : m                       (bool)          [query,edit]
          This flag specifies whether clips on a track are to be muted or not. Must be used in conjuction with the track flag.
    
      - name : n                       (unicode)       [create,query]
          This flag is used to query the name of the clip node associated with the specified clip index, or to specify the name of
          the instanced clip during instancing. In query mode, this flag can accept a value.
    
      - postCycle : poc                (float)         [create,query]
          Specify the number of times to repeat the clip after its normal end.
    
      - preCycle : prc                 (float)         [create,query]
          Specify the number of times to repeat the clip before its normal start.
    
      - remove : rm                    (bool)          [create]
          This flag is used to remove a clip from the timeline. It must be used in conjunction with the ci/clipIndex flag. The
          specified clip will be removed from the timeline, but will still exist in the library and any instanced clips will
          remain in the timeline. To permanently remove a clip from the scene, the clip command should be used instead.
    
      - removeBlend : rb               (int, int)      [create]
          This flag is used to remove an existing blend between two clips, whose indices are provided as flag arguments.
    
      - removeEmptyTracks : ret        (bool)          [create]
          This flag is used to remove all tracks that have no clips.
    
      - removeTrack : rt               (int)           [create]
          This flag is used to remove the track with the specified index.  The track must have no clips on it before it can be
          removed.
    
      - rotationsAbsolute : ra         (bool)          [query,edit]
          Set all channels except rotations to be calculated with relative offsets.  Rotation channels will be calculated with
          absolute offsets.  This flag cannot be used in conjunction with the aa/allAbsolute, ar/allRelative or da/defaultAbsolute
          flags.
    
      - scale : sc                     (float)         [create,query]
          Specify the amount to scale the clip. Values must be greater than 0.
    
      - shift : sh                     (int)           [create]
          This flag allows multiple clips to be shifted by a certain number of tracks and works in conjunction with the shiftIndex
          flag.  The flag specifies the number of tracks to shift the associated clips.  Positive values shift the clips down an
          negative values shift the clips up.
    
      - shiftIndex : shi               (int)           [create]
          This flag allows multiple clips to be shifted by a certain number of tracks and works in conjunction with the
          shiftAmount flag.  The flag specifies the index of the clip to shift.  This flag can be used multiple times on the
          command line to specify a number of clips to shift.
    
      - solo : so                      (bool)          [query,edit]
          This flag specifies whether clips on a track are to be soloed or not. Must be used in conjuction with the track flag.
    
      - sourceClipName : scn           (bool)          [create,query]
          This flag is used to query the name of the source clip node associated with the specified clip index.
    
      - sourceEnd : se                 (time)          [create,query]
          Specify where to end in the source clip's animation curves
    
      - sourceStart : ss               (time)          [create,query]
          Specify where to start in the source clip's animation curves
    
      - start : s                      (time)          [create,query]
          Specify the placement of the start of the clip
    
      - track : t                      (int)           [create,query]
          Specify the track to operate on. For example, which track to place a clip on, which track to mute/lock/solo.  In query
          mode, it may be used in conjuction with the clipIndex flag to return the track number of a clip, where track 1 is the
          first track of the character. In query mode, this flag can accept a value.
    
      - weight : w                     (float)         [create,query]
          This flag is used in to set or query the weight of the clip associated with the specified clip index.
    
      - weightStyle : ws               (int)           [create,query]
          This flag is used to set or query the weightStyle attribute of the clip associated with the specified clip index.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.clipSchedule`
    """

    pass


def sequenceManager(*args, **kwargs):
    """
    The sequenceManager command manages sequences, shots, and their related scenes.                  In query mode, return
    type is based on queried flag.
    
    Flags:
      - addSequencerAudio : asa        (unicode)       [create]
          Add an audio clip to the sequencer by specifying a filename
    
      - attachSequencerAudio : ata     (unicode)       [create]
          Add an audio clip to the sequencer by specifying an audio node
    
      - currentShot : cs               (unicode)       [query]
          Returns the shot that is being used at the current sequence time.
    
      - currentTime : ct               (time)          [create,query]
          Set the current sequence time
    
      - listSequencerAudio : lsa       (unicode)       [create]
          List the audio clips added to the sequencer
    
      - listShots : lsh                (bool)          [create]
          List all the currently defined shots across all scene segments
    
      - modelPanel : mp                (unicode)       [create,query]
          Sets a dedicated modelPanel to be used as the panel that the sequencer will control.
    
      - node : nd                      (unicode)       [query]
          Returns the SequenceManager node, of which there is only ever one.
    
      - writableSequencer : ws         (unicode)       [query]
          Get the writable sequencer node.  Create it if it doesn't exist.                                   Flag can have
          multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.sequenceManager`
    """

    pass


def jointCluster(*args, **kwargs):
    """
    The joint cluster command adds high-level controls to manage the cluster percentage values on a bound skin around a
    joint. JointClusters are one way to create smooth bending behaviour on skin when joints rotate. .                a ----
    aboveBound .    ____________a_________ .                a         \ .     Joint1     a       Joint2 .
    _____________a_______    \ .                a       \    \     b  --- belowBound .                a        \    \  b .
    \    b .                           \ b  \ .                           b\    \ .                         b   \ Joint3
    CVs/vertices between Joint1 and aaaaa (aboveBound) receive only translation/rotation/scale from Joint1. CVs vertices
    between aaaa and bbbb transition between translation/rotatation/scale from Joint1 and Joint2. CV2 beyand bbbbb (below
    bound) receive only translation/ rotation scale from Joint3.
    
    Flags:
      - aboveBound : ab                (float)         [create,query,edit]
          Specifies the where the drop-off begins in the direction of the bone above the joint. A value of 100 indicates the
          entire length of the bone. The default value is 10.
    
      - aboveCluster : ac              (bool)          [query]
          Returns the name of the cluster associated with the bone above this joint.
    
      - aboveDropoffType : adt         (unicode)       [create,query,edit]
          Specifies the type of percentage drop-off in the direction of the bone above this joint. Valid values are linear,
          exponential, sineand none. Default is linear.
    
      - aboveValue : av                (float)         [create,query,edit]
          Specifies the drop-off percentage of the joint cluster in the direction of the bone above the cluster. A value of 100
          indicates the entire length of the bone. The default value is 50.
    
      - belowBound : bb                (float)         [create,query,edit]
          Specifies where the drop-off ends in the direction of the bone below the joint. A value of 100 indicates the entire
          length of the bone. The default value is 10.
    
      - belowCluster : bc              (bool)          [query]
          Returns the name of the cluster associated with this joint.
    
      - belowDropoffType : bdt         (unicode)       [create,query,edit]
          Specifies the type of type of percentage drop-off in the direction of the bone below this joint. Valid values are
          linear, exponential, sineand none. Default is linear.
    
      - belowValue : bv                (float)         [create,query,edit]
          Specifies the drop-off percentage of the joint cluster in the direction of the joint below the cluster. A value of 100
          indicates the entire length of the bone. The default value is 50.
    
      - deformerTools : dt             (bool)          [query]
          Used to query for the helper nodes associated with the jointCluster.
    
      - joint : j                      (unicode)       [create]
          Specifies the joint that the cluster should act about.
    
      - name : n                       (unicode)       [create]
          This flag is obsolete.                  Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.jointCluster`
    """

    pass


def ikSystemInfo(*args, **kwargs):
    """
    This action modifies and queries the current ikSystem controls.                  In query mode, return type is based on
    queried flag.
    
    Flags:
      - globalSnapHandle : gsh         (bool)          [create,query]
          If this flag is off, all ikHandles will not be snapped.                  Flag can have multiple arguments, passed either
          as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.ikSystemInfo`
    """

    pass


def effector(*args, **kwargs):
    """
    The effector command is used to set the name or hidden flag for the effector.  The standard edit (-e) and query (-q)
    flags are used for edit and query functions.
    
    Flags:
      - hide : hi                      (bool)          [create,query,edit]
          Specifies whether to hide drawing of effector if attached to a handle.
    
      - name : n                       (unicode)       [create,query,edit]
          Specifies the name of the effector.                  Flag can have multiple arguments, passed either as a tuple or a
          list.
    
    
    Derived from mel command `maya.cmds.effector`
    """

    pass


def timeEditorBakeClips(*args, **kwargs):
    """
    This command is used to bake Time Editor clips and to blend them into a single clip.
    
    Flags:
      - bakeToAnimSource : bas         (unicode)       []
    
      - bakeToClip : btc               (unicode)       [create]
          Bake/merge the selected clips into a clip.
    
      - clipId : id                    (int)           [create]
          Clip IDs of the clips to bake.
    
      - combineLayers : cl             (bool)          [create]
          Combine the layers of the input clip.
    
      - forceSampling : fs             (bool)          [create]
          Force sampling on the whole time range when baking.
    
      - keepOriginalClip : koc         (bool)          [create]
          Keep the source clips after baking.
    
      - path : pt                      (unicode)       [create]
          Full path of clips to operates on. For example: composition1|track1|group; composition1|track1|group|track2|clip1.
    
      - sampleBy : sb                  (time)          [create]
          Sampling interval when baking crossfades and timewarps.
    
      - targetTrackIndex : tti         (int)           [create]
          Specify the target track when baking containers. If targetTrackIndex is specified, the track index within the specified
          node is used. If targetTrackIndex is not specified or is the default value (-1), the track index within the current node
          is used. If targetTrackIndex is -2, a new track will be created.
    
      - targetTracksNode : ttn         (unicode)       [create]
          Target tracks node when baking containers.                  Flag can have multiple arguments, passed either as a tuple
          or a list.
    
    
    Derived from mel command `maya.cmds.timeEditorBakeClips`
    """

    pass


def orientConstraint(*args, **kwargs):
    """
    Constrain an object's orientation to match the orientation of the target or the average of a number of targets. An
    orientConstraint takes as input one or more targetDAG transform nodes to control the orientation of the single
    constraint objectDAG transform  The orientConstraint orients the constrained object to match the weighted average of the
    target world space orientations.
    
    Maya Bug Fix:
      - when queried, angle offsets would be returned in radians, not current angle unit
    
    Modifications:
      - added new syntax for querying the weight of a target object, by passing the constraint first::
    
            aimConstraint( 'pCube1_aimConstraint1', q=1, weight ='pSphere1' )
            aimConstraint( 'pCube1_aimConstraint1', q=1, weight =['pSphere1', 'pCylinder1'] )
            aimConstraint( 'pCube1_aimConstraint1', q=1, weight =[] )
    
    Flags:
      - createCache : cc               (float, float)  [edit]
          This flag is used to generate an animation curve that serves as a cache for the constraint. The two arguments define the
          start and end frames.  The cache is useful if the constraint has multiple targets and the constraint's interpolation
          type is set to no flip. The no flipmode prevents flipping during playback, but the result is dependent on the previous
          frame.  Therefore in order to consistently get the same result on a specific frame, a cache must be generated. This flag
          creates the cache and sets the constraint's interpolation type to cache. If a cache exists already, it will be deleted
          and replaced with a new cache.
    
      - deleteCache : dc               (bool)          [edit]
          Delete an existing interpolation cache.
    
      - layer : l                      (unicode)       [create,edit]
          Specify the name of the animation layer where the constraint should be added.
    
      - maintainOffset : mo            (bool)          [create]
          The offset necessary to preserve the constrained object's initial orientation will be calculated and used as the offset.
    
      - name : n                       (unicode)       [create,query,edit]
          Sets the name of the constraint node to the specified name.  Default name is constrainedObjectName_constraintType
    
      - offset : o                     (float, float, float) [create,query,edit]
          Sets or queries the value of the offset. Default is 0,0,0.
    
      - remove : rm                    (bool)          [edit]
          removes the listed target(s) from the constraint.
    
      - skip : sk                      (unicode)       [create,edit]
          Specify the axis to be skipped. Valid values are x, y, zand none. The default value in create mode is none. This flag is
          multi-use.
    
      - targetList : tl                (bool)          [query]
          Return the list of target objects.
    
      - weight : w                     (float)         [create,query,edit]
          Sets the weight value for the specified target(s). If not given at creation time, the default value of 1.0 is used.
    
      - weightAliasList : wal          (bool)          [query]
          Returns the names of the attributes that control the weight of the target objects. Aliases are returned in the same
          order as the targets are returned by the targetList flag                  Flag can have multiple arguments, passed
          either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.orientConstraint`
    """

    pass


def animLayer(*args, **kwargs):
    """
    This command creates and edits animation layers.
    
    Modifications:
      - returns a PyNode object for flags: (query and (root or bestLayer or parent))
      - returns a list of PyNode objects for flags: (query and (children or attribute or bestAnimLayer or animCurves or baseAnimCurves or blendNodes or affectedLayers or parent))
    
    Flags:
      - addRelatedKG : akg             (bool)          [create,query,edit]
          Used adding attributes to a layer. Determines if associated keying groups should be added or not to the layer.
    
      - addSelectedObjects : aso       (bool)          [create,query,edit]
          Adds selected object(s) to the layer.
    
      - affectedLayers : afl           (bool)          [query]
          Return the layers that the currently selected object(s) are members of
    
      - animCurves : anc               (bool)          [create,query,edit]
          In query mode returns the anim curves associated with this layer
    
      - attribute : at                 (unicode)       [create,query,edit]
          Adds a specific attribute on a object to the layer.
    
      - baseAnimCurves : bac           (bool)          [create,query,edit]
          In query mode returns the base layer anim curves associated with this layer, if any.
    
      - bestAnimLayer : blr            (bool)          [create,query,edit]
          In query mode returns the best anim layers for keying for the selected objects. If used in conjunction with -at, will
          return the best anim layers for keying for the specific plugs (attributes) specified.
    
      - bestLayer : bl                 (bool)          [query]
          Return the layer that will be keyed for specified attribute.
    
      - blendNodes : bld               (bool)          [create,query,edit]
          In query mode returns the blend nodes associated with this layer
    
      - children : c                   (unicode)       [query]
          Get the list of children layers. Return value is a string array.
    
      - collapse : col                 (bool)          [create,query,edit]
          Determine if a layer is collapse in the layer editor.
    
      - copy : cp                      (unicode)       [edit]
          Copy from layer.
    
      - copyAnimation : ca             (unicode)       [create,edit]
          Copy animation from specified layer to destination layer, only animation that are on attribute layered by both layer
          that are concerned.
    
      - copyNoAnimation : cna          (unicode)       [edit]
          Copy from layer without the animation curves.
    
      - excludeBoolean : ebl           (bool)          [create,query,edit]
          When adding selected object(s) to the layer, excludes any boolean attributes.
    
      - excludeDynamic : edn           (bool)          [create,query,edit]
          When adding selected object(s) to the layer, excludes any dynamic attributes.
    
      - excludeEnum : een              (bool)          [create,query,edit]
          When adding selected object(s) to the layer, excludes any enum attributes.
    
      - excludeRotate : ert            (bool)          [create,query,edit]
          When adding selected object(s) to the layer, exclude the rotate attribute.
    
      - excludeScale : esc             (bool)          [create,query,edit]
          When adding selected object(s) to the layer, exclude the scale attribute.
    
      - excludeTranslate : etr         (bool)          [create,query,edit]
          When adding selected object(s) to the layer, excludes the translate attribute.
    
      - excludeVisibility : evs        (bool)          [create,query,edit]
          When adding selected object(s) to the layer, exclude the visibility attribute.
    
      - exists : ex                    (bool)          [query]
          Determine if an layer exists.
    
      - extractAnimation : ea          (unicode)       [create,edit]
          Transfer animation from specified layer to destination layer, only animation that are on attribute layered by both layer
          that are concerned.
    
      - findCurveForPlug : fcv         (unicode)       [query,edit]
          Finds the parameter curve containing the animation data for the specified plug on the given layer.
    
      - forceUIRebuild : fur           (bool)          [create]
          Rebuilds the animation layers user interface.
    
      - forceUIRefresh : uir           (bool)          [create]
          Refreshes the animation layers user interface.
    
      - layeredPlug : lp               (unicode)       [query]
          Returns the plug on the blend node corresponding to the specified layer
    
      - lock : l                       (bool)          [create,query,edit]
          Set the lock state of the specified layer. A locked layer cannot receive key. Default is false.
    
      - maxLayers : ml                 (bool)          [query]
          Returns the maximum number of anim layers supported by this product.
    
      - moveLayerAfter : mva           (unicode)       [edit]
          Move layer after the specified layer
    
      - moveLayerBefore : mvb          (unicode)       [edit]
          Move layer before the specified layer
    
      - mute : m                       (bool)          [create,query,edit]
          Set the mute state of the specified layer. Default is false.
    
      - override : o                   (bool)          [create,query,edit]
          Set the overide state of the specified layer. Default is false.
    
      - parent : p                     (unicode)       [create,query,edit]
          Set the parent of the specified layer. Default is the animation layer root.
    
      - passthrough : pth              (bool)          [create,query,edit]
          Set the passthrough state of the specified layer. Default is true.
    
      - preferred : prf                (bool)          [create,query,edit]
          Determine if a layer is a preferred layer, the best layer algorithm will try to set keyframe in preferred layer first.
    
      - removeAllAttributes : raa      (bool)          [edit]
          Remove all objects from layer.
    
      - removeAttribute : ra           (unicode)       [edit]
          Remove object from layer.
    
      - root : r                       (unicode)       [query]
          Return the base layer if it exist
    
      - selected : sel                 (bool)          [create,query,edit]
          Determine if a layer is selected, a selected layer will be show in the timecontrol, graph editor.
    
      - solo : s                       (bool)          [create,query,edit]
          Set the solo state of the specified layer. Default is false.
    
      - weight : w                     (float)         [create,query,edit]
          Set the weight of the specified layer between 0.0 and 1.0. Default is 1.
    
      - writeBlendnodeDestinations : wbd (bool)          [edit]
          In edit mode writes the destination plugs of the blend nodes that belong to the layer into the blend node. This is used
          for layer import/export purposes and is not for general use.                               Flag can have multiple
          arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.animLayer`
    """

    pass


def pairBlend(*args, **kwargs):
    """
    The pairBlend node allows a weighted combinations of 2 inputs to be blended together. It is created automatically when
    keying or constraining an attribute which is already connected.Alternatively, the pairBlend command can be used to
    connect a pairBlend node to connected attributes of a node. The previously existing connections are rewired to input1 of
    the pairBlend node. Additional connections can then be made manually to input2 of the pairBlend node. The pairBlend
    command can also be used to query the inputs to an existing pairBlend node.
    
    Flags:
      - attribute : at                 (unicode)       [create]
          The name of the attribute(s) which the blend will drive. This flag is required when creating the blend.
    
      - input1 : i1                    (bool)          [query]
          Returns a string array of the node(s) connected to input 1.
    
      - input2 : i2                    (bool)          [query]
          Returns a string array of the node(s) connected to input 2.
    
      - node : nd                      (unicode)       [create]
          The name of the node which the blend will drive. This flag is required when creating the blend.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.pairBlend`
    """

    pass


def deviceManager(*args, **kwargs):
    """
    This command queriers the internal device manager for information on attached devices.           In query mode, return
    type is based on queried flag.
    
    Flags:
      - attachment : att               (bool)          [query]
          Returns the plugs that a device and axis are attached to.  Expects the -deviceIndex and axisIndex to be used in
          conjunction.
    
      - axisCoordChanges : acc         (bool)          [query]
          Returns whether the axis coordinate changes.  Expects the -deviceIndex and -axisIndex flags to be used in conjunction.
    
      - axisIndex : axi                (int)           [create,query,edit]
          Used usually in conjunction with other flags, to indicate the index of the axis.
    
      - axisName : axn                 (bool)          [query]
          Returns the name of the axis.  Expects the -deviceIndex and -axisIndex flags to be used in conjunction.
    
      - axisOffset : axo               (bool)          [query]
          Returns the offset of the axis.  Expects the -deviceIndex and -axisIndex flags to be used in conjunction.
    
      - axisScale : axs                (bool)          [query]
          Returns the scale of the axis.  Expects the -deviceIndex and -axisIndex flags to be used in conjunction.
    
      - deviceIndex : dvi              (int)           [create,query,edit]
          Used usually in conjunction with other flags, to indicate the index of the device.
    
      - deviceNameFromIndex : dni      (int)           [query]
          Returns the name of the device with the given index.
    
      - numAxis : nax                  (bool)          [query]
          Returns the number of axis this device has.  Expects the -deviceIndex flag to be used.
    
      - numDevices : ndv               (bool)          [query]
          Returns the number of devices currently attached.                                  Flag can have multiple arguments,
          passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.deviceManager`
    """

    pass


def hikGlobals(*args, **kwargs):
    """
    Sets global HumanIK flags for the application.
    
    Flags:
      - releaseAllPinning : rap        (bool)          [query,edit]
          Sets the global release all pinning hik flag. When this flag is set, all pinning states are ignored.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.hikGlobals`
    """

    pass


def parentConstraint(*args, **kwargs):
    """
    Constrain an object's position and rotation so that it behaves as if it were a child of the target object(s). In the
    case of multiple targets, the overall position and rotation of the constrained object is the weighted average of each
    target's contribution to the position and rotation of the object. A parentConstraint takes as input one or more
    targetDAG transform nodes at which to position and rotate the single constraint objectDAG transform node.  The
    parentConstraint positions and rotates the constrained object at the weighted average of the world space position,
    rotation and scale target objects.
    
    Maya Bug Fix:
      - when queried, angle offsets would be returned in radians, not current angle unit
    
    Modifications:
      - added new syntax for querying the weight of a target object, by passing the constraint first::
    
            aimConstraint( 'pCube1_aimConstraint1', q=1, weight ='pSphere1' )
            aimConstraint( 'pCube1_aimConstraint1', q=1, weight =['pSphere1', 'pCylinder1'] )
            aimConstraint( 'pCube1_aimConstraint1', q=1, weight =[] )
    
    Flags:
      - createCache : cc               (float, float)  [edit]
          This flag is used to generate an animation curve that serves as a cache for the constraint. The two arguments define the
          start and end frames.  The cache is useful if the constraint has multiple targets and the constraint's interpolation
          type is set to no flip. The no flipmode prevents flipping during playback, but the result is dependent on the previous
          frame. Therefore in order to consistently get the same result on a specific frame, a cache must be generated. This flag
          creates the cache and sets the constraint's interpolation type to cache. If a cache exists already, it will be deleted
          and replaced with a new cache.
    
      - decompRotationToChild : dr     (bool)          [create]
          During constraint creation, if the rotation offset between the constrained object and the target object is maintained,
          this flag indicates close to which object the offset rotation is decomposed. Setting this flag will make the rotation
          decomposition close to the constrained object instead of the target object, which is the default setting.
    
      - deleteCache : dc               (bool)          [edit]
          Delete an existing interpolation cache.
    
      - layer : l                      (unicode)       [create,edit]
          Specify the name of the animation layer where the constraint should be added.
    
      - maintainOffset : mo            (bool)          [create]
          If this flag is specified the position and rotation of the constrained object will be maintained.
    
      - name : n                       (unicode)       [create,query,edit]
          Sets the name of the constraint node to the specified name.  Default name is constrainedObjectName_constraintType
    
      - remove : rm                    (bool)          [edit]
          removes the listed target(s) from the constraint.
    
      - skipRotate : sr                (unicode)       [create]
          Causes the axis specified not to be considered when constraining rotation.  Valid arguments are x, y, zand none.
    
      - skipTranslate : st             (unicode)       [create]
          Causes the axis specified not to be considered when constraining translation.  Valid arguments are x, y, zand none.
    
      - targetList : tl                (bool)          [query]
          Return the list of target objects.
    
      - weight : w                     (float)         [create,query,edit]
          Sets the weight value for the specified target(s). If not given at creation time, the default value of 1.0 is used.
    
      - weightAliasList : wal          (bool)          [query]
          Returns the names of the attributes that control the weight of the target objects. Aliases are returned in the same
          order as the targets are returned by the targetList flag                  Flag can have multiple arguments, passed
          either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.parentConstraint`
    """

    pass


def simplify(*args, **kwargs):
    """
    This command operates on a keyset.  A keyset is defined as a group of keys within a specified time range on one or more
    animation curves. The animation curves comprising a keyset depend on the value of the -animationflag: keysOrObjects: Any
    active keys, when no target objects or -attribute flags appear on the command line, orAll animation curves connected to
    all keyframable attributes of objects specified as the command line's targetList, when there are no active keys.keys:
    Only act on active keys or tangents. If there are no active keys or tangents, don't do anything. objects: Only act on
    specified objects.  If there are no objects specified, don't do anything. Note that the -animationflag can be used to
    override the curves uniquely identified by the multi-use -attributeflag, which takes an argument of the form
    attributeName, such as translateX. Keys on animation curves are identified by either their time values or their indices.
    Times and indices can be given individually or as part of a list or range. -time 10palmeans the key at frame 10 (PAL
    format).-time 1.0sec -time 15ntsc -time 20means the keys at time 1.0 second, frame 15 (in NTSC format), and time 20 (in
    the currently defined global time unit).-time 10:20means all keys in the range from 10 to 20, inclusive, in the current
    time unit.Omitting one end of a range means go to infinity, as in the following examples: -time 10:means all keys from
    time 10 (in the current time unit) onwards.-time :10means all keys up to (and including) time 10 (in the current time
    unit).-time :is a short form to specify all keys.-index 0means the first key of each animation curve. (Indices are
    0-based.)-index 2 -index 5 -index 7means the 3rd, 6th, and 8th keys.-index 1:5means the 2nd, 3rd, 4th, 5th, and 6th keys
    of each animation curve.This command will simplify (reduce the number of keyframes) an animation curve.
    
    Flags:
      - animation : an                 (unicode)       [create]
          Where this command should get the animation to act on.  Valid values are objects,keys,and keysOrObjectsDefault:
          keysOrObjects.(See Description for details.)
    
      - attribute : at                 (unicode)       [create]
          List of attributes to select
    
      - controlPoints : cp             (bool)          [create]
          This flag explicitly specifies whether or not to include the control points of a shape (see -sflag) in the list of
          attributes. Default: false.  (Not valid for pasteKeycmd.)
    
      - float : f                      (floatrange)    [create]
          value uniquely representing a non-time-based key (or key range) on a time-based animCurve.  Valid floatRange include
          single values (-f 10) or a string with a lower and upper bound, separated by a colon (-f 10:20
    
      - floatTolerance : ft            (float)         [create]
          Specify the x-axis tolerance (defaults to 0.05) for float-input animCurves such as those created by Set Driven Keyframe.
          This flag is ignored on animCurves driven by time. Higher floatTolerance values will result in sparser keys which may
          less accurately represent the initial curve.
    
      - hierarchy : hi                 (unicode)       [create]
          Hierarchy expansion options.  Valid values are above,below,both,and none.(Not valid for pasteKeycmd.)
    
      - includeUpperBound : iub        (bool)          [create]
          When the -t/time or -f/float flags represent a range of keys, this flag determines whether the keys at the upper bound
          of the range are included in the keyset. Default value: true.  This flag is only valid when the argument to the -t/time
          flag is a time range with a lower and upper bound.  (When used with the pasteKeycommand, this flag refers only to the
          time range of the target curve that is replaced, when using options such as replace,fitReplace,or scaleReplace.This flag
          has no effect on the curve pasted from the clipboard.)
    
      - index : index                  (int)           [create]
          index of a key on an animCurve
    
      - shape : s                      (bool)          [create]
          Consider attributes of shapes below transforms as well, except controlPoints.  Default: true.  (Not valid for
          pasteKeycmd.)
    
      - time : t                       (timerange)     [create]
          time uniquely representing a key (or key range) on a time-based animCurve.  Valid timeRanges include single values (-t
          10) or a string with a lower and upper bound, separated by a colon (-t 10:20
    
      - timeTolerance : tt             (time)          [create]
          Specify the x-axis tolerance (defaults to 0.05 seconds) for time-input animCurves. This flag is ignored on animCurves
          driven by floats. Higher time tolerance values will result in sparser keys which may less accurately represent the
          initial curve.
    
      - valueTolerance : vt            (float)         [create]
          Specify the value tolerance (defaults to 0.01)                  Flag can have multiple arguments, passed either as a
          tuple or a list.
    
    
    Derived from mel command `maya.cmds.simplify`
    """

    pass


def volumeBind(*args, **kwargs):
    """
    Command for creating and editing volume binding nodes. The node is use for storing volume data to define skin weighting
    data.
    
    Flags:
      - influence : inf                (unicode)       [query,edit]
          Edit or Query the list of influences connected to the skin cluster.
    
      - name : n                       (unicode)       [create]
          Used to specify the name of the node being created.                  Flag can have multiple arguments, passed either as
          a tuple or a list.
    
    
    Derived from mel command `maya.cmds.volumeBind`
    """

    pass


def flexor(*args, **kwargs):
    """
    This command creates a flexor. A flexor a deformer plus a set of driving    attributes. For example, a flexor might be a
    sculpt object that is driven by a joint's x rotation and a cube's y position.
    
    Flags:
      - atBones : ab                   (bool)          [create]
          Add a flexor at bones. Flexor will be added at each of the selected bones, or at all bones in the selected skeleton if
          the -ts flag is also specified.
    
      - atJoints : aj                  (bool)          [create]
          Add a flexor at joints. Flexor will be added at each of the selected joints, or at all joints in the selected skeleton
          if the -ts flag is specified.
    
      - deformerCommand : dc           (unicode)       [create]
          String representing underlying deformer command string.
    
      - list : l                       (bool)          [query]
          List all possible types of flexors. Query mode only.
    
      - name : n                       (unicode)       [create]
          This flag is obsolete.
    
      - noScale : ns                   (bool)          [create]
          Do not auto-scale the flexor to the size of the nearby geometry.
    
      - toSkeleton : ts                (bool)          [create]
          Specifies that flexors will be added to the entire skeleton rather than just to the selected joints/bones. This flag is
          used in conjunction with the -ab and -aj flags.
    
      - type : typ                     (unicode)       [create]
          Specifies which type of flexor. To see list of valid types, use the flexor -query -listcommand.                  Flag
          can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.flexor`
    """

    pass


def buildBookmarkMenu(*args, **kwargs):
    """
    This command handles building the dynamicBookmark menu, to show all bookmarks (sets) of a specified type (sets -text)
    menuName is the string returned by the menucommand.
    
    Flags:
      - editor : ed                    (unicode)       [create]
          Name of the editor which this menu belongs to
    
      - type : typ                     (unicode)       [create]
          Type of bookmark (sets -text) to display                  Flag can have multiple arguments, passed either as a tuple or
          a list.
    
    
    Derived from mel command `maya.cmds.buildBookmarkMenu`
    """

    pass


def skeletonEmbed(*args, **kwargs):
    """
    This command is used to embed a skeleton inside meshes.                  In query mode, return type is based on queried
    flag.
    
    Flags:
      - mergedMesh : mm                (bool)          [query]
          When specified, the query command merges selected meshes together and returns a Python object representing the merged
          mesh.
    
      - segmentationMethod : sm        (int)           [create]
          Specifies which segmentation algorithm to use to determine what is inside the mesh and what is outside the mesh.  By
          default, boundary-and-fill-and-grow voxelization will be used. Available algorithms are: 0  : Perfect mesh (no
          voxelization). This method works for perfect meshes, i.e. meshes that are closed, watertight, 2-manifold and without
          self-intersection or interior/hidden geometry.  It segments the interior region of the mesh from the exterior using a
          pseudo-normal test. It does not use voxelization.  If mesh conditions are not respected, the segmentation is likely to
          be wrong.  This can make the segmentation process significantly longer and prevent successful skeleton embedding. 1 :
          Watertight mesh (flood fill). This method works for watertight meshes, i.e. meshes for which faces completely separate
          the interior region of the mesh from the exterior.  The mesh can have degenerated faces, wrong face orientation, self-
          intersection, etc.  The method uses surface voxelization to classify as part of the interior region all voxels
          intersecting with a mesh face.  It then performs flood-filling from the outside, marking all reached voxels as part of
          the exterior region of the model.  Finally, all unreached voxels are marked as part of the interior region.  This method
          works so long as the mesh is watertight, i.e. without holes up to the voxelization resolution. Otherwise, flood-filling
          reaches the interior region and creates inaccurate segmentation. 2 : Imperfect mesh (flood fill + growing). This method
          works for meshes where holes could make the flood-filling step reach the interior region of the mesh, but that have face
          orientation consistent enough so filling them is possible.  First, it uses surface voxelization to classify as part of
          the interior region all voxels intersecting with a mesh face.  It then alternates flood-filling and growing steps.  The
          flood-filling tries to reach all voxels from the outside so that unreached voxels are marked as part of the interior
          region.  The growing step uses a relatively computation-intensive process to check for interior voxels in all neighbors
          to those already identified.  Any voxel identified as interior is likely to fill holes, allowing subsequent flood-
          filling steps to identify more interior voxels. 3 : Polygon soup (repair). This method has no manifold or face
          orientation requirements.  It reconstructs a mesh that wraps the input mesh with a given offset (3 times the voxel size)
          and uses this perfect 2-manifold mesh to segment the interior region from the exterior region of the model. Because of
          the offset, it might lose some of the details and merge parts that are proximal. However, this usually is not an issue
          with common models where body parts are not too close to one another. 99 : Direct skeleton (no embedding). This method
          does not try to perform embedding.  It simply returns the skeleton in its initial pose without any attempt at embedding
          inside the meshes, other than placing it in the meshes bounding box.
    
      - segmentationResolution : sr    (int)           [create]
          Specifies which segmentation resolution to use for the voxel grid.  By default, 256x256x256 voxels will be used.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.skeletonEmbed`
    """

    pass


def playbackOptions(*args, **kwargs):
    """
    This command sets/queries certain values associated with playback: looping style, start/end times, etc. Only commands
    modifying the -minTime/maxTime, the -animationStartTime/animationEndTime, or the -by value are undoable.
    
    Flags:
      - animationEndTime : aet         (time)          [create,query,edit]
          Sets the end time of the animation.  Query returns a float.
    
      - animationStartTime : ast       (time)          [create,query,edit]
          Sets the start time of the animation.  Query returns a float.
    
      - blockingAnim : ba              (bool)          [create,query]
          All tangents playback as stepped so that animation can be viewed in pure pose-to-pose form
    
      - by : by                        (float)         [create,query,edit]
          Increment between times viewed during playback. (Default 1.0)
    
      - framesPerSecond : fps          (bool)          [create,query]
          Queries the actual playback rate.  Query returns a float.
    
      - loop : l                       (unicode)       [create,query,edit]
          Controls if and how playback repeats.  Valid values are once,continuous,and oscillate.Query returns string.
    
      - maxPlaybackSpeed : mps         (float)         [create,query,edit]
          Sets the desired maximum playback speed.  Query returns a float. The maxPlaybackSpeed is only used by Maya when your
          playbackSpeed is 0 (play every frame). The maxPlaybackSpeed will clamp the maximum playback rate to prevent it from
          going more than a certain amount. A maxPlaybackSpeed of 0 will give free (unclamped) playback.
    
      - maxTime : max                  (time)          [create,query,edit]
          Sets the end of the playback time range.  Query returns a float.
    
      - minTime : min                  (time)          [create,query,edit]
          Sets the start of the playback time range.  Query returns a float.
    
      - playbackSpeed : ps             (float)         [create,query,edit]
          Sets the desired playback speed.  Query returns a float.
    
      - view : v                       (unicode)       [create,query,edit]
          Controls how many modelling views update during playback. Valid values are alland active.  Query returns a string.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.playbackOptions`
    """

    pass


def geometryConstraint(*args, **kwargs):
    """
    Constrain an object's position based on the shape of the target surface(s) at the closest point(s) to the object. A
    geometryConstraint takes as input one or more surface shapes (the targets) and a DAG transform node (the object).  The
    geometryConstraint position constrained object such object lies on the surface of the target with the greatest weight
    value.  If two targets have the same weight value then the one with the lowest index is chosen.
    
    Maya Bug Fix:
      - when queried, angle offsets would be returned in radians, not current angle unit
    
    Modifications:
      - added new syntax for querying the weight of a target object, by passing the constraint first::
    
            aimConstraint( 'pCube1_aimConstraint1', q=1, weight ='pSphere1' )
            aimConstraint( 'pCube1_aimConstraint1', q=1, weight =['pSphere1', 'pCylinder1'] )
            aimConstraint( 'pCube1_aimConstraint1', q=1, weight =[] )
    
    Flags:
      - layer : l                      (unicode)       [create,edit]
          Specify the name of the animation layer where the constraint should be added.
    
      - name : n                       (unicode)       [create,query,edit]
          Sets the name of the constraint node to the specified name.  Default name is constrainedObjectName_constraintType
    
      - remove : rm                    (bool)          [edit]
          removes the listed target(s) from the constraint.
    
      - targetList : tl                (bool)          [query]
          Return the list of target objects.
    
      - weight : w                     (float)         [create,query,edit]
          Sets the weight value for the specified target(s). If not given at creation time, the default value of 1.0 is used.
    
      - weightAliasList : wal          (bool)          [query]
          Returns the names of the attributes that control the weight of the target objects. Aliases are returned in the same
          order as the targets are returned by the targetList flag                  Flag can have multiple arguments, passed
          either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.geometryConstraint`
    """

    pass


def poseEditor(*args, **kwargs):
    """
    This command creates an editor that derives from the base editor class that has controls for deformer and control nodes.
    
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
    
      - targetControlList : tcl        (bool)          []
    
      - targetList : tl                (bool)          []
    
      - unParent : up                  (bool)          [create,edit]
          Specifies that the editor should be removed from its layout. This cannot be used in query mode.
    
      - unlockMainConnection : ulk     (bool)          [create,edit]
          Unlocks the mainConnection, effectively restoring the original mainConnection (if it is still available), and dynamic
          updates.
    
      - updateMainConnection : upd     (bool)          [create,edit]
          Causes a locked mainConnection to be updated from the orginal mainConnection, but preserves the lock state.
    
      - useTemplate : ut               (unicode)       [create]
          Forces the command to use a command template other than the current one.                  Flag can have multiple
          arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.poseEditor`
    """

    pass


def writeTake(*args, **kwargs):
    """
    This action writes a take from a device with recorded data to a take (.mov) file. The writeTake action can also write
    the virtual definition of a device. See also: recordDevice, readTake, defineVirtualDevice
    
    Flags:
      - angle : a                      (unicode)       [create]
          Sets the angular unit used in the take. Valid strings are [deg|degree|rad|radian]. C: The default is the current user
          angular unit.
    
      - device : d                     (unicode)       [create]
          Specifies the device that contains the take. This is a required argument. If the device does not contain a take, the
          action will fail.
    
      - linear : l                     (unicode)       [create]
          Sets the linear unit used in the take. Valid strings are
          [mm|millimeter|cm|centimeter|m|meter|km|kilometer|in|inch|ft|foot|yd|yard|mi|mile] C: The default is the current user
          linear unit.
    
      - noTime : nt                    (bool)          [create]
          The take (.mov) file will not contain time stamps. C: The default is to put time stamps in the take file.
    
      - precision : pre                (int)           [create]
          Sets the number of digits to the right of the decimal place in the take file.C: The default is 6.
    
      - take : t                       (unicode)       [create]
          Write out the take to a file with the specified name.
    
      - virtualDevice : vd             (unicode)       [create]
          Writes out the virtual device definition to a mel script with the specified file name.                  Flag can have
          multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.writeTake`
    """

    pass


def timeEditorTracks(*args, **kwargs):
    """
    Time Editor tracks commands
    
    Flags:
      - activeClipWeight : acw         (time)          [query]
          Get the clip weight at the specified time.
    
      - activeClipWeightId : aci       (time)          [query]
          Get the clip ID carrying the active clip weight at the specified time.
    
      - addTrack : at                  (int)           [edit]
          Add new track at the track index specified. Indices are 0-based. Specify -1 to add the track at the end.
    
      - allClips : ac                  (bool)          [query]
          Return a list of clip IDs under the specified track.
    
      - allTracks : atc                (bool)          [query]
          Return a list of strings for all the immediate tracks for the given tracks node in the format tracksNode:trackIndex.
    
      - allTracksRecursive : atr       (bool)          [query]
          Return a list of strings for all the tracks for the given tracks node, or return a list of strings for all tracks of all
          tracks nodes in the format tracksNode:trackIndex. If the given root tracks node is from a composition, this command
          returns the tracks under that composition, including the tracks within groups that is under the same composition.
    
      - composition : cp               (bool)          [query]
          Return the composition the specified track belongs to.
    
      - path : pt                      (unicode)       [edit]
          Full path of a track node or a track to operates on. For example: composition1|track1|group; composition1|track1. In
          query mode, this flag can accept a value.
    
      - plugIndex : pi                 (int)           [query,edit]
          Get the plug index of the specified track.
    
      - removeTrack : rt               (int)           [edit]
          Remove track at given index. It is a multi-use flag. For example: composition1|track1|group|track1;
    
      - removeTrackByPath : rtp        (unicode)       [edit]
          Remove track at given path. It is a multi-use flag.
    
      - reorderTrack : rot             (int, int)      [edit]
          Move the track relative to other tracks. The first argument is the track index (0-based). The second argument can be a
          positive or negative number to indicate the steps to move. Positive numbers move forward and negative numbers move
          backward.
    
      - resetMute : rm                 (bool)          [create]
          Reset all the muted tracks in the active composition.
    
      - resetSolo : rs                 (bool)          [create]
          Reset the soloing of all tracks on the active composition.
    
      - selectedTracks : st            (bool)          [query]
          Return a list of the indices for all the selected tracks for the given tracks node, or return a list of strings for all
          selected tracks of all tracks nodes in the format tracksNode:trackIndex.
    
      - trackGhost : tgh               (bool)          [query,edit]
          Ghost all clips under track.
    
      - trackIndex : ti                (int)           [query,edit]
          Specify the track index. This flag is used in conjunction with the other flags. In query mode, this flag can accept a
          value.
    
      - trackMuted : tm                (bool)          [query,edit]
          Return whether the track is muted.
    
      - trackName : tn                 (unicode)       [query,edit]
          Display name of the track.
    
      - trackSolo : ts                 (bool)          [query,edit]
          Return whether the track is soloed.
    
      - trackType : tt                 (int)           [query,edit]
          Specify the track type. Can only be used together with -at/addTrack. Does not work by itself. In query mode, return the
          integer corresponding to the track type. 0: Animation Track (Default)1: Audio Track Flag can have multiple arguments,
          passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.timeEditorTracks`
    """

    pass


def getCurrentTime():
    """
    get the current time as a float
    """

    pass


def movieInfo(*args, **kwargs):
    """
    movieInfo provides a mechanism for querying information about movie files.
    
    Flags:
      - counter : cn                   (bool)          [create]
          Query the 'counter' flag of the movie's timecode format. If this is true, the timecode returned by the -timeCode flag
          will be a simple counter. If false, the returned timecode will be an array of integers (hours, minutes, seconds,
          frames).
    
      - dropFrame : df                 (bool)          [create]
          Query the 'drop frame' flag of the movie's timecode format.
    
      - frameCount : f                 (bool)          [create]
          Query the number of frames in the movie file
    
      - frameDuration : fd             (bool)          [create]
          Query the frame duration of the movie's timecode format.
    
      - height : h                     (bool)          [create]
          Query the height of the movie
    
      - movieTexture : mt              (bool)          [create]
          If set, the string argument is interpreted as the name of a movie texture node, and the command then operates on the
          movie loaded by that node.
    
      - negTimesOK : nt                (bool)          [create]
          Query the 'neg times OK' flag of the movie's timecode format.
    
      - numFrames : nf                 (bool)          [create]
          Query the whole number of frames per second of the movie's timecode format.
    
      - quickTime : qt                 (bool)          [create]
          Query whether the movie is a QuickTime movie.
    
      - timeCode : tc                  (bool)          [create]
          Query the timecode of the current movie frame.
    
      - timeCodeTrack : tt             (bool)          [create]
          Query whether the movie has a timecode track.
    
      - timeScale : ts                 (bool)          [create]
          Query the timescale of the movie's timecode format.
    
      - twentyFourHourMax : tf         (bool)          [create]
          Query the '24 hour max' flag of the movie's timecode format.
    
      - width : w                      (bool)          [create]
          Query the width of the movie                               Flag can have multiple arguments, passed either as a tuple or
          a list.
    
    
    Derived from mel command `maya.cmds.movieInfo`
    """

    pass


def dagPose(*args, **kwargs):
    """
    This command is used to save and restore the matrix information for a dag hierarchy. Specifically, the data stored will
    restore the translate, rotate, scale, scale pivot, rotate pivot, rotation order, and (for joints) joint order for all
    the objects on the hierarchy. Data for other attributes is not stored by this command. This command can also be used to
    store a bindPose for an object. When you skin an object, a dagPose is automatically created for the skin.
    
    Flags:
      - addToPose : a                  (bool)          [create]
          Allows adding the selected items to the dagPose.
    
      - atPose : ap                    (bool)          [query]
          Query whether the hierarchy is at same position as the pose. Names of hierarchy members that are not at the pose
          position will be returned. An empty return list indicates that the hierarchy is at the pose.
    
      - bindPose : bp                  (bool)          [create,query]
          Used to specify the bindPose for the selected hierarchy. Each hierarchy can have only a single bindPose, which is saved
          automatically at the time of a skin bind. The bindPose is used when adding influence objects, binding new skins, or
          adding flexors. Take care when modifying the bindPose with the -rs/-reset or -rm/-remove flags, since if the bindPose is
          ill-defined it can cause problems with subsequent skinning operations.
    
      - g : g                          (bool)          [create]
          This flag can be used in conjunction with the restore flag to signal that the members of the pose should be restored to
          the global pose. The global pose means not only is each object locally oriented with respect to its parents, it is also
          in the same global position that it was at when the pose was saved. If a hierarchy's parenting has been changed since
          the time that the pose was saved, you may have trouble reaching the global pose.
    
      - members : m                    (bool)          [query]
          Query the members of the specified pose. The pose should be specified using the selection list, the -bp/-bindPose or the
          -n/-name flag.
    
      - name : n                       (unicode)       [create,query]
          Specify the name of the pose. This can be used during create, restore, reset, remove, and query operations to specify
          the pose to be created or acted upon.
    
      - remove : rm                    (bool)          [create]
          Remove the selected joints from the specified pose.
    
      - reset : rs                     (bool)          [create]
          Reset the pose on the selected joints. If you are resetting pose data for a bindPose, take care. It is appropriate to
          use the -rs/-reset flag if a joint has been reparented and/or appears to be exactly at the bindPose. However, a bindPose
          that is much different from the exact bindPose can cause problems with subsequent skinning operations.
    
      - restore : r                    (bool)          [create]
          Restore the hierarchy to a saved pose. To specify the pose, select the pose node, or use the -bp/-bindPose or -n/-name
          flag.
    
      - save : s                       (bool)          [create]
          Save a dagPose for the selected dag hierarchy. The name of the new pose will be returned.
    
      - selection : sl                 (bool)          [create,query]
          Whether or not to store a pose for all items in the hierarchy, or for only the selected items.
    
      - worldParent : wp               (bool)          [create]
          Indicates that the selected pose member should be recalculated as if it is parented to the world. This is typically used
          when you plan to reparent the object to world as the next operation.                  Flag can have multiple arguments,
          passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.dagPose`
    """

    pass


def blendShape(*args, **kwargs):
    """
    This command creates a blendShape deformer, which blends in specified amounts of each target shape to the initial base
    shape. Each base shape is deformed by its own set of target shapes. Every target shape has an index that associates it
    with one of the shape weight values.In the create mode the first item on the selection list is treated as the base and
    the remaining inputs as targets. If the first item on the list has multiple shapes grouped beneath it, the targets must
    have an identical shape hierarchy. Additional base shapes can be added in edit mode using the deformers -g flag.
    
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
    
      - copyDelta : cd                 (int, int, int) []
    
      - deformerTools : dt             (bool)          [query]
          Returns the name of the deformer tool objects (if any) as string string ...
    
      - envelope : en                  (float)         [create,query,edit]
          Set the envelope value for the deformer, controlling how much of the total deformation gets applied. Default is 1.0.
    
      - exclusive : ex                 (unicode)       [create,query]
          Puts the deformation set in a deform partition.
    
      - export : ep                    (unicode)       []
    
      - exportTarget : et              (int, int)      []
    
      - flipTarget : ft                (int, int)      []
    
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
    
      - inBetween : ib                 (bool)          [create,edit]
          Indicate that the specified target should serve as an inbetween. An inbetween target is one that serves as an
          intermediate target between the base shape and another target.
    
      - inBetweenIndex : ibi           (int)           [edit]
          Only used with the -rtd/-resetTargetDelta flag to remove delta values for points in the inbetween target geometry
          defined by this index.
    
      - inBetweenType : ibt            (unicode)       [create,edit]
          Specify if the in-between target to be created is relative to the hero target or if it is absolute. If it is relative to
          hero targets, the in-between target will get any changes made to the hero target. Valid values are relativeand absolute.
          This flag should always be used with the -ib/-inBetween and -t/-target flags.
    
      - includeHiddenSelections : ihs  (bool)          [create]
          Apply the deformer to any visible and hidden objects in the selection list. Default is false.
    
      - ip : ip                        (unicode)       []
    
      - mergeSource : mgs              (int)           []
    
      - mergeTarget : mgt              (int)           []
    
      - mirrorDirection : md           (int)           []
    
      - mirrorTarget : mt              (int, int)      []
    
      - name : n                       (unicode)       [create]
          Used to specify the name of the node being created.
    
      - normalizationGroups : ng       (bool)          [query]
          Returns a list of the used normalization group IDs.
    
      - origin : o                     (unicode)       [create]
          blendShape will be performed with respect to the world by default. Valid values are worldand local. The local flag will
          cause the blend shape to be performed with respect to the shape's local origin.
    
      - parallel : par                 (bool)          [create,edit]
          Inserts the new deformer in a parallel chain to any existing deformers in the history of the object. A blendShape is
          inserted to blend the parallel results together. Works in create mode (and edit mode if the deformer has no geometry
          added yet).
    
      - prune : pr                     (bool)          [edit]
          Removes any points not being deformed by the deformer in its current configuration from the deformer set.
    
      - remove : rm                    (bool)          [edit]
          Specifies that objects listed after the -g flag should be removed from this deformer.
    
      - resetTargetDelta : rtd         (int, int)      [edit]
          Remove all delta values for points in the target geometry, including all sequential targets defined by target index.
          Parameter list: uint: the base object indexuint: the target index
    
      - split : sp                     (bool)          [create,edit]
          Branches off a new chain in the dependency graph instead of inserting/appending the deformer into/onto an existing
          chain. Works in create mode (and edit mode if the deformer has no geometry added yet).
    
      - symmetryAxis : sa              (unicode)       []
    
      - symmetryEdge : se              (unicode)       []
    
      - symmetrySpace : ss             (int)           []
    
      - tangentSpace : ts              (bool)          [create,edit]
          Indicate that the delta of the specified target should be relative to the tangent space of the surface.
    
      - target : t                     (unicode, int, unicode, float) [create,query,edit]
          Set target object as the index target shape for the base shape base object. The full influence of target shape takes
          effect when its shape weight is targetValue. Parameter list: string: the base objectint: indexstring: the target
          objectdouble: target value
    
      - topologyCheck : tc             (bool)          [create]
          Set the state of checking for a topology match between the shapes being blended. Default is on.
    
      - transform : tr                 (unicode)       [query,edit]
          Set transform for target, then the deltas will become relative to a post transform. Typically the best workflow for this
          option is to choose a joint that is related to the fix you have introduced. This flag should be used only if the
          Deformation orderof blendShape node is Before.
    
      - weight : w                     (int, float)    [create,query,edit]
          Set the weight value (second parameter) at index (first parameter).
    
      - weightCount : wc               (int)           [create,query,edit]
          Set the number of shape weight values.                  Flag can have multiple arguments, passed either as a tuple or a
          list.
    
    
    Derived from mel command `maya.cmds.blendShape`
    """

    pass


def evaluator(*args, **kwargs):
    """
    Handles turning on and off custom evaluation overrides used by the evaluation manager. Query no flag to see all
    available custom evaluators. Query the 'enable' flag to check if an evaluator is currently enabled. If the 'name' flag
    isn't used then return all modes and their current active state.
    
    Flags:
      - clusters : cl                  (bool)          [query]
          This flag queries the list of clusters currently assigned to the named custom evaluator. The return value will be an
          array of strings where the array consists of a set of (number, string[]) groups. e.g. If an evaluator has 2 clusters
          with 2 and 3 nodes in them respectively the output would be something like: (2, 'transform2', 'transform3', 3, 'joint1',
          'joint2', 'joint3')
    
      - configuration : c              (unicode)       [create,query]
          Sends configuration information to a custom evaluator. It's up to the evaluator to understand what they mean. Multiple
          configuration messages can be sent in a single command. Query this flag for a given evaluator to find out what
          configuration messages it accepts.
    
      - enable : en                    (bool)          [create,query]
          Enables or disables a specific graph evaluation runtime, depending on the state of the flag.  In order to use this flag
          you must also specify the name in the 'name' argument. When the 'enable' flag is used in conjunction with the 'nodeType'
          flag then it is used to selectively turn on or off the ability of the given evaluator to handle nodes of the given type
          (i.e. it no longer toggles the evaluator enabled state). When the 'enable' flag is used in conjunction with the
          'configuration' flag then it is passed along with the configuration message interpreted by the custom evaluator.
    
      - info : i                       (bool)          [query]
          Queries the evaluator information. Only valid in query mode since the information is generated by the evaluator's
          internal state and cannot be changed. In order to use this flag, the 'name' argument must also be specified.
    
      - name : n                       (unicode)       [create,query]
          Names a particular DG evaluation override evaluator. Evaluators are registered automatically by name. Query this flag to
          get a list of available runtimes. When a runtime is registered it is enabled by default. Use the 'enable' flag to change
          its enabled state. In query mode, this flag can accept a value.
    
      - nodeType : nt                  (unicode)       [create,query]
          Names a particular node type to be passed to the evaluator request. Evaluators can either use or ignore the node type
          information as passed.
    
      - nodeTypeChildren : ntc         (bool)          [create,query]
          If enabled when using the 'nodeType' flag then handle all of the node types derived from the given one as well. Default
          is to only handle the named node type.
    
      - priority : p                   (bool)          [query]
          Gets the evaluator priority. Custom evaluator with highest priority order will get the chance to claim the nodes first.
          In order to use this flag you must also specify the name in the 'name' argument.
    
      - valueName : vn                 (unicode)       [query]
          Queries a value from a given evaluator.  Evaluators can define a set of values for which they answer.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.evaluator`
    """

    pass


def sculptTarget(*args, **kwargs):
    """
    This command is used to specify the blend shape target to be modified by the sculpting tools and transform manipulators.
    
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
    
      - deformerTools : dt             (bool)          []
          Returns the name of the deformer tool objects (if any) as string string ...
    
      - exclusive : ex                 (unicode)       [create]
          Puts the deformation set in a deform partition.
    
      - frontOfChain : foc             (bool)          [create,edit]
          This command is used to specify that the new deformer node should be placed ahead (upstream) of existing deformer and
          skin nodes in the shape's history (but not ahead of existing tweak nodes). The input to the deformer will be the
          upstream shape rather than the visible downstream shape, so the behavior of this flag is the most intuitive if the
          downstream deformers are in their reset (hasNoEffect) position when the new deformer is added. Works in create mode (and
          edit mode if the deformer has no geometry added yet).
    
      - geometry : g                   (unicode)       [edit]
          The specified object will be added to the list of objects being deformed by this deformer object, unless the -rm flag is
          also specified. When queried, this flag returns string string string ...
    
      - geometryIndices : gi           (bool)          []
          Complements the -geometry flag in query mode. Returns the multi index of each geometry.
    
      - ignoreSelected : ignoreSelected (bool)          [create]
          Tells the command to not deform objects on the current selection list
    
      - inbetweenWeight : ibw          (float)         [edit]
          Specifies the in between target weight of the blend shape node that will be made editable by the sculpting and transform
          tools.
    
      - includeHiddenSelections : ihs  (bool)          [create]
          Apply the deformer to any visible and hidden objects in the selection list. Default is false.
    
      - name : n                       (unicode)       [create]
          Used to specify the name of the node being created.
    
      - parallel : par                 (bool)          [create,edit]
          Inserts the new deformer in a parallel chain to any existing deformers in the history of the object. A blendShape is
          inserted to blend the parallel results together. Works in create mode (and edit mode if the deformer has no geometry
          added yet).
    
      - prune : pr                     (bool)          [edit]
          Removes any points not being deformed by the deformer in its current configuration from the deformer set.
    
      - regenerate : r                 (bool)          [edit]
          When this flag is specified a new shape is created for the specified blend shape target, if the shape does not already
          exist. The name of the new shape is returned.
    
      - remove : rm                    (bool)          [edit]
          Specifies that objects listed after the -g flag should be removed from this deformer.
    
      - snapshot : s                   (int)           [edit]
          This flag should only be used internally to add in-between target. When this flag is specified a snapshot of the shape
          will be taken for the specified in-between target when it does not exist yet. This flag specifies the base shape index
          and must be used with the -target and -inbetweenWeight flags, which specify the in-between target.
    
      - split : sp                     (bool)          [create,edit]
          Branches off a new chain in the dependency graph instead of inserting/appending the deformer into/onto an existing
          chain. Works in create mode (and edit mode if the deformer has no geometry added yet).
    
      - target : t                     (int)           [edit]
          Specifies the target index of the blend shape node that will be made editable by the sculpting and transform tools.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.sculptTarget`
    """

    pass


def insertJoint(*args, **kwargs):
    """
    This command will insert a new joint under the given or selected joint. If the given joint has child joints, they will
    be reparented under the new inserted joint. The given joint(or selected joint) should not have skin attached. The
    command works on the selected joint. No options or flags are necessary.
    
    
    Derived from mel command `maya.cmds.insertJoint`
    """

    pass


def keyframeOutliner(*args, **kwargs):
    """
    This command creates/edits/queries a keyframe outliner control.
    
    Flags:
      - animCurve : ac                 (unicode)       [edit]
          Name of the animation curve for which to display keyframes.
    
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
    
      - display : dsp                  (unicode)       [query,edit]
          narrow | wide What columns to display.  When narrow, time and value will be displayed, when widetangent information will
          be displayed as well
    
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
    
    
    Derived from mel command `maya.cmds.keyframeOutliner`
    """

    pass


def boneLattice(*args, **kwargs):
    """
    This command creates/edits/queries a boneLattice deformer. The name of the created/edited object is returned. Usually
    you would make use of this functionality through the higher level flexor command.
    
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
    
      - bicep : bi                     (float)         [create,query,edit]
          Affects the bulging of lattice points on the inside of the bend. Positive/negative values cause the points to bulge
          outwards/inwards. Default value is 0.0. When queried, this flag returns a float.
    
      - deformerTools : dt             (bool)          [query]
          Returns the name of the deformer tool objects (if any) as string string ...
    
      - exclusive : ex                 (unicode)       [create,query]
          Puts the deformation set in a deform partition.
    
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
    
      - joint : j                      (unicode)       [create,query,edit]
          Specifies which joint will be used to drive the bulging behaviors.
    
      - lengthIn : li                  (float)         [create,query,edit]
          Affects the location of lattice points along the upper half of the bone. Positive/negative values cause the points to
          move away/towards the center of the bone.  Changing this parameter also modifies the regions affected by the creasing,
          rounding and width parameters. Default value is 0.0. When queried, this flag returns a float.
    
      - lengthOut : lo                 (float)         [create,query,edit]
          Affects the location of lattice points along the lower half of the bone. Positive/negative values cause the points to
          move away/towards the center of the bone.  Changing this parameter also modifies the regions affected by the creasing,
          rounding and width parameters. Default value is 0.0. When queried, this flag returns a float.
    
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
    
      - split : sp                     (bool)          [create,edit]
          Branches off a new chain in the dependency graph instead of inserting/appending the deformer into/onto an existing
          chain. Works in create mode (and edit mode if the deformer has no geometry added yet).
    
      - transform : t                  (unicode)       [create]
          Specifies which dag node is being used to rigidly transform the lattice which this node is going to deform.  If this
          flag is not specified an identity matrix will be assumed.
    
      - tricep : tr                    (float)         [create,query,edit]
          Affects the bulging of lattice points on the outside of the bend. Positive/negative values cause the points to bulge
          outwards/inwards. Default value is 0.0. When queried, this flag returns a float.
    
      - widthLeft : wl                 (float)         [create,query,edit]
          Affects the bulging of lattice points on the left side of the bend. Positive/negative values cause the points to bulge
          outwards/inwards. Default value is 0.0. When queried, this flag returns a float.
    
      - widthRight : wr                (float)         [create,query,edit]
          Affects the bulging of lattice points on the right side of the bend. Positive/negative values cause the points to bulge
          outwards/inwards. Default value is 0.0. When queried, this flag returns a float.                  Flag can have multiple
          arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.boneLattice`
    """

    pass


def skinCluster(*args, **kwargs):
    """
    The skinCluster command is used for smooth skinning in maya. It binds the selected geometry to the selected joints or
    skeleton by means of a skinCluster node.  Each point of the bound geometry can be affected by any number of joints. The
    extent to which each joint affects the motion of each point is regulated by a corresponding weight factor.  Weight
    factors can be modified using the skinPercent command.  The command returns the name of the new skinCluster.The
    skinCluster binds only a single geometry at a time. Thus, to bind multiple geometries, multiple skinCluster commands
    must be issued.Upon creation of a new skinCluster, the command can be used to add and remove transforms (not necessarily
    joints) that influence the motion of the bound skin points.  The skinCluster command can also be used to adjust
    parameters such as the dropoff, nurbs samples, polygon smoothness on a particular influence object. Note: Any custom
    weights on a skin point that the influence object affects will be lost after adjusting these parameters.
    
    Modifications:
      - returns a list of PyNode objects for flags: (query and (geometry or deformerTools or influence or weightedInfluence))
    
    Flags:
      - addInfluence : ai              (unicode)       [edit]
          The specified transform or joint will be added to the list of transforms that influence the bound geometry. The maximum
          number of influences will be observed and only the weights of the cv's that the specified transform effects will change.
          This flag is multi-use.
    
      - addToSelection : ats           (bool)          [edit]
          When used in conjunction with the selectInfluenceVerts flag, causes the vertices afftected by the influence to be added
          to the current selection, without first de-selecting other vertices.
    
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
    
      - baseShape : bsh                (unicode)       [edit]
          This flag can be used in conjunction with the -addInfluence flag to specify the shape that will be used as the base
          shape when an influence object with geometry is added to the skinCluster.  If the flag is not used then the command will
          make a copy of the influence object's shape and use that as a base shape.
    
      - before : bf                    (bool)          [create,edit]
          If the default behavior for insertion/appending into/onto the existing chain is not the desired behavior then this flag
          can be used to force the command to place the deformer node before the selected node in the chain even if a new geometry
          shape has to be created in order to do so. Works in create mode (and edit mode if the deformer has no geometry added
          yet).
    
      - bindMethod : bm                (int)           [create,query]
          This flag sets the binding method. 0 - Closest distance between a joint and a point of the geometry. 1 - Closest
          distance between a joint, considering the skeleton hierarchy, and a point of the geometry. 2 - Surface heat map
          diffusion.
    
      - deformerTools : dt             (bool)          [query]
          Returns the name of the deformer tool objects (if any) as string string ...
    
      - dropoffRate : dr               (float)         [create,query,edit]
          Sets the rate at which the influence of a transform drops as the distance from that transform increases. The valid range
          is between 0.1 and 10.0.  In Create mode it sets the dropoff rate for all the bound joints.  In Edit mode the flag is
          used together with the inf/influence flag to set the dropoff rate of a particular influence.  Note: When the flag is
          used in Edit mode, any custom weights on the skin points the given transform influences will be lost.
    
      - exclusive : ex                 (unicode)       [create,query]
          Puts the deformation set in a deform partition.
    
      - forceNormalizeWeights : fnw    (bool)          [edit]
          If the normalization mode is none or post, it is possible (indeed likely) for the weights in the skin cluster to no
          longer add up to 1.  This flag forces all weights to add back to 1 again.
    
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
    
      - heatmapFalloff : hmf           (float)         [create]
          This flag sets the heatmap binding falloff. If set to 0.0 (default) the deformation will be smoother due to many small
          weights spread over the mesh surface per influence. However, if set to 1.0, corresponding to maximum falloff, the number
          of influences per point will be reduced and points will tend to be greatly influenced by their closest joint decreasing
          the overall spread of small weights. This flag only works when using heatmap binding.
    
      - ignoreBindPose : ibp           (bool)          [create,edit]
          This flag is deprecated and no longer used.  It will be ignored if used.
    
      - ignoreHierarchy : ih           (bool)          [create,query]
          Deprecated. Use bindMethod flag instead. Disregard the place of the joints in the skeleton hierarchy when computing the
          closest joints that influence a point of the geometry.
    
      - ignoreSelected : ignoreSelected (bool)          [create]
          Tells the command to not deform objects on the current selection list
    
      - includeHiddenSelections : ihs  (bool)          [create]
          Apply the deformer to any visible and hidden objects in the selection list. Default is false.
    
      - influence : inf                (unicode)       [query,edit]
          This flag specifies the influence object that will be used for the current edit operation. In query mode, returns a
          string array of the influence objects (joints and transform).       In query mode, this flag can accept a value.
    
      - lockWeights : lw               (bool)          [query,edit]
          Lock the weights of the specified influence object to their current value or to the value specified by the -weight flag.
    
      - maximumInfluences : mi         (int)           [create,query,edit]
          Sets the maximum number of transforms that can influence a point (have non-zero weight for the point) when the
          skinCluster is first created or a new influence is added.  Note: When this flag is used in Edit mode any custom weights
          will be lost and new weights will be reassigned to the whole skin.
    
      - moveJointsMode : mjm           (bool)          [edit]
          If set to true, puts the skin into a mode where joints can be moved without modifying the skinning. If set to false,
          takes the skin out of move joints mode.
    
      - name : n                       (unicode)       [create]
          Used to specify the name of the node being created.
    
      - normalizeWeights : nw          (int)           [create,query,edit]
          This flag sets the normalization mode. 0 - none, 1 - interactive, 2 - post (default) Interactive normalization makes
          sure the weights on the influences add up to 1.0, always. Everytime a weight is changed, the weights are automatically
          normalized.  This may make it difficult to perform weighting operations, as the normalization may interfere with the
          weights the user has set.  Post normalization leaves the weights the user has set as is, and only normalizes the weights
          at the moment it is needed (by dividing by the sum of the weights).  This makes it easier for users to weight their
          skins.
    
      - nurbsSamples : ns              (int)           [create,edit]
          Sets the number of sample points that will be used along an influence curve or in each direction on an influence NURBS
          surface to influence the bound skin. The more the sample points the more closely the skin follows the influence NURBS
          curve/surface.
    
      - obeyMaxInfluences : omi        (bool)          [create,query,edit]
          When true, the skinCluster will continue to enforce the maximum influences each time the user modifies the weight, so
          that any given point is only weighted by the number of influences in the skinCluster's maximumInfluences attribute.
    
      - parallel : par                 (bool)          [create,edit]
          Inserts the new deformer in a parallel chain to any existing deformers in the history of the object. A blendShape is
          inserted to blend the parallel results together. Works in create mode (and edit mode if the deformer has no geometry
          added yet).
    
      - polySmoothness : ps            (float)         [create,edit]
          This flag controls how accurately the skin control points follow a given polygon influence object. The higher the value
          of polySmoothnmess the more rounded the deformation resulting from a polygonal influence object will be.
    
      - prune : pr                     (bool)          [edit]
          Removes any points not being deformed by the deformer in its current configuration from the deformer set.
    
      - recacheBindMatrices : rbm      (bool)          [edit]
          Forces the skinCluster node to recache its bind matrices.
    
      - remove : rm                    (bool)          [edit]
          Specifies that objects listed after the -g flag should be removed from this deformer.
    
      - removeFromSelection : rfs      (bool)          [edit]
          When used in conjunction with the selectInfluenceVerts flag, causes the vertices afftected by the influence to be
          removed from the current selection.
    
      - removeInfluence : ri           (unicode)       [edit]
          Remove the specified transform or joint from the list of transforms that influence the bound geometry The weights for
          the affected points are renormalized. This flag is multi-use.
    
      - removeUnusedInfluence : rui    (bool)          [create]
          If this flag is set to true then transform or joint whose weights are all zero (they have no effect) will not be bound
          to the geometry.  Having this option set will help speed-up the playback of animation.
    
      - selectInfluenceVerts : siv     (unicode)       [edit]
          Given the name of a transform, this will select the verts or control points being influenced by this transform, so users
          may visualize which vertices are being influenced by the transform.
    
      - skinMethod : sm                (int)           [create,query,edit]
          This flag set the skinning method. 0 - classical linear skinning (default). 1 - dual quaternion (volume preserving), 2 -
          a weighted blend between the two.
    
      - smoothWeights : sw             (float)         [edit]
          This flag is used to detect sudden jumps in skin weight values, which often indicates bad weighting, and then smooth out
          those jaggies in skin weights. The argument is the error tolerance ranging from 0 to 1.  A value of 1 means that the
          algorithm will smooth a vertex only if there is a 100% change in weight values from its neighbors.  The recommended
          default to use is 0.5 (50% change in weight value from the neighbors).
    
      - smoothWeightsMaxIterations : swi (int)           [edit]
          This flag is valid only with the smooth weights flag.  It is possible that not all the vertices detected as needing
          smoothing can be smoothed in 1 iteration (because all of their neighbors also have bad weighting and need to be
          smoothed). With more iterations, more vertices can be smoothed.  This flag controls the maximum number of iterations the
          algorithm will attempt to smooth weights. The default is 2 for this flag.
    
      - split : sp                     (bool)          [create,edit]
          Branches off a new chain in the dependency graph instead of inserting/appending the deformer into/onto an existing
          chain. Works in create mode (and edit mode if the deformer has no geometry added yet).
    
      - toSelectedBones : tsb          (bool)          [create]
          geometry will be bound to the selected bones only.
    
      - toSkeletonAndTransforms : tst  (bool)          [create]
          geometry will be bound to the skeleton and any transforms in the hierarchy. If any of the transforms are also bindable
          objects, assume that only the last object passed to the command is the bindable object. The rest are treated as
          influences.
    
      - unbind : ub                    (bool)          [edit]
          Unbinds the geometry from the skinCluster and deletes the skinCluster node
    
      - unbindKeepHistory : ubk        (bool)          [edit]
          Unbinds the geometry from the skinCluster, but keeps the skinCluster node so that its weights can be used when the skin
          is rebound. To rebind, use the skinCluster command.
    
      - useGeometry : ug               (bool)          [edit]
          When adding an influence to a skinCluster, use the geometry parented under the influence transform to determine the
          weight dropoff of that influence.
    
      - volumeBind : vb                (float)         [create]
          Creates a volume bind node and attaches it to the new skin cluster node. This node holds hull geometry parameters for a
          volume based weighting system. This system is used in interactive skinning. The value passed will determine the minimum
          weight value when initializing the volume. The volume in be increase to enclose all the vertices that are above this
          value.
    
      - volumeType : vt                (int)           [create]
          Defines the initial shape of the binding volume (see volumeBind). 0 - Default (currently set to a capsule) 1 - Capsule,
          2 - Cylinder.
    
      - weight : wt                    (float)         [edit]
          This flag is only valid in conjunction with the -addInfluence flag. It sets the weight for the influence object that is
          being added.
    
      - weightDistribution : wd        (int)           [create,query,edit]
          This flag sets the weight distribution mode. 0 - distance (default), 1 - neighbors When normalizeWeights is in effect,
          and a weight has been reduced or removed altogether, the sum is usually brought back up to 1.0 by increasing the
          contributions of the other non-zero weights. However, if there are no other non-zero weights, the algorithm has to
          create some weights from thin air and distribute the residual weight between them. This attribute controls how that is
          done. Distance- the algorithm calculates weights from the world-space distances from the component to the transforms.
          Neighbors- the algorithm calculates weights from the weights on the neighboring components.
    
      - weightedInfluence : wi         (bool)          [query]
          This flag returns a string array of the influence objects (joints and transform) that have non-zero weighting.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.skinCluster`
    """

    pass


def pasteKey(*args, **kwargs):
    """
    The pasteKey command pastes curve segment hierarchies from the clipboard onto other objects or curves. If the object
    hierarchy from which the curve segments were copied or cut does not match the object hierarchy being pasted to, pasteKey
    will paste as much as it can match in the hierarchy.  If animation from only one object is on the clipboard, it will be
    pasted to each of the target objects. If animation from more than one object is on the clipboard, selection list order
    determines what animation is pasted to which object. Valid operations include: One attribute to one or more attributes
    (Clipboard animation is pasted onto all target attributes.One attribute to one or more objects (Clipboard animation
    pasted onto target object, when attribute names match.)Many attributes to one or more objectsClipboard animation pasted
    onto targets when attribute names match.TbaseKeySetCmd.h The way the keyset clipboard will be pasted to the specified
    object's attributes depends on the paste -optionspecified. Each of these options below will be explained using an
    example. For all the explanations, let us assume that there is a curve segment with 20 frames of animation on the keyset
    clipboard (you can put curve segments onto the clipboard using the cutKeyor copyKeycommands). We will call the animation
    curve that we are pasting to the target curve: pasteKey -time 5 -option insert1. Shift all keyframes on the target curve
    after time 5 to the right by 20 frames (to make room for the 20-frame clipboard segment). 2. Paste the 20-frame
    clipboard segment starting at time 5. pasteKey -time 5:25-option replace1. Remove all keys on the target curve from 5 to
    25. 2. Paste the 20-frame clipboard curve at time 5. pasteKey -option replaceCompletely1. Remove all keys on the target
    curve. 2. Paste the 20-frame clipboard curve, preserving the clipboard curve's original keyframe times. pasteKey -time 5
    -option merge1.The clipboard curve segment will be pasted starting at time 5 for its full 20-frame range until frame 25.
    2. If a keyframe on the target curve has the same time as a keyframe on the clipboard curve, it is overwritten.
    Otherwise, any keys that existed in the 5:25 range before the paste, will remain untouched pasteKey -time 3:10-option
    scaleInsert1. Shift all keyframes on the target curve after time 3 to the right by 7 frames (to clear the range 3:10 to
    paste in) 2. The clipboard curve segment will be scaled to fit the specified time range (i.e. the 20 frames on the
    clipboard will be scaled to fit into 7 frames), and then pasted into the range 3:10. pasteKey -time 3:10-option
    scaleReplace1. Any existing keyframes in the target curve in the range 3:10 are removed. 2. The clipboard curve segment
    will be scaled to fit the specified time range (i.e. the 20 frames on the clipboard will be scaled to fit into 7
    frames), and then pasted into the range 3:10. pasteKey -time 3:10-option scaleMerge1. The clipboard curve segment will
    be scaled to fit the specified time range (i.e. the 20 frames on the clipboard will be scaled to fit into 7 frames). 2.
    If there are keys on the target curve at the same time as keys on the clipboard curve, they are overwritten. Otherwise,
    keyframes on the target curve that existed in the 3:10 range before the paste, will remain untouched. pasteKey -time
    3:10-option fitInsert1. Shift all the keyframes on the target curve after time 3 to the right by 7 frames (to clear the
    range 3:10 to paste in) 2. The first 7 frames of the clipboard curve segment will be pasted into the range 3:10.
    pasteKey -time 3:10-option fitReplace1. Any existing frames in the target curve in the range 3:10 are removed. 2. The
    first 7 frames of the clipboard curve segment will be pasted into the range 3:10. pasteKey -time 3:10-option fitMerge1.
    The first 7 frames of the clipboard curve segment will be pasted into the range 3:10. 2. If there are keys on the target
    curve at the same time as keys on the clipboard curve, they are overwritten. Otherwise, keyframes on the target curve
    that existed in the 3:10 range before the paste, will remain untouched.
    
    Flags:
      - animLayer : al                 (unicode)       [create]
          Specifies that the keys getting pasted should be pasted onto curves on the specified animation layer.If that layer
          doesn't exist for the specified objects or attributes then the keys won't get pasted.
    
      - animation : an                 (unicode)       [create]
          Where this command should get the animation to act on.  Valid values are objects,keys,and keysOrObjectsDefault:
          keysOrObjects.(See Description for details.)
    
      - attribute : at                 (unicode)       [create]
          List of attributes to select
    
      - clipboard : cb                 (unicode)       [create]
          Specifies the clipboard from which animation is pasted. Valid clipboards are apiand anim.  The default clipboard is:
          anim
    
      - connect : c                    (bool)          [create]
          When true, connect the source curve with the destination curve's value at the paste time. (This has the effect of
          shifting the clipboard curve in value to connect with the destination curve.) False preserves the source curve's
          original keyframe values. Default is false.
    
      - copies : cp                    (int)           [create]
          The number of times to paste the source curve.
    
      - float : f                      (floatrange)    [create]
          value uniquely representing a non-time-based key (or key range) on a time-based animCurve.  Valid floatRange include
          single values (-f 10) or a string with a lower and upper bound, separated by a colon (-f 10:20
    
      - floatOffset : fo               (float)         [create]
          How much to offset the pasted keys in time (for non-time-input animation curves).
    
      - includeUpperBound : iub        (bool)          [create]
          When the -t/time or -f/float flags represent a range of keys, this flag determines whether the keys at the upper bound
          of the range are included in the keyset. Default value: true.  This flag is only valid when the argument to the -t/time
          flag is a time range with a lower and upper bound.  (When used with the pasteKeycommand, this flag refers only to the
          time range of the target curve that is replaced, when using options such as replace,fitReplace,or scaleReplace.This flag
          has no effect on the curve pasted from the clipboard.)
    
      - index : index                  (int)           [create]
          index of a key on an animCurve
    
      - matchByName : mn               (bool)          [create]
          When true, we will only paste onto items in the scene whose node and attribute names match up exactly with a
          corresponding item in the clipboard. No hierarchy information is used. Default is false, and in this case the usual
          matching by hierarchy occurs.
    
      - option : o                     (unicode)       [create]
          Valid values are insert, replace, replaceCompletely, merge, scaleInsert,scaleReplace, scaleMerge, fitInsert, fitReplace,
          and fitMerge. The default paste option is: insert.
    
      - time : t                       (timerange)     [create]
          time uniquely representing a key (or key range) on a time-based animCurve.  Valid timeRanges include single values (-t
          10) or a string with a lower and upper bound, separated by a colon (-t 10:20
    
      - timeOffset : to                (time)          [create]
          How much to offset the pasted keys in time (for time-input animation curves).
    
      - valueOffset : vo               (float)         [create]
          How much to offset the pasted keys in value.                  Flag can have multiple arguments, passed either as a tuple
          or a list.
    
    
    Derived from mel command `maya.cmds.pasteKey`
    """

    pass


def movOut(*args, **kwargs):
    """
    Exports a .mov file from the listed attributes. Valid attribute types are numeric attributes; time attributes; linear
    attributes; angular attributes; compound attributes made of the types listed previously; and multi attributes composed
    of the types listed previously. Length, angle, and time values will be written to the file in the user units. If an
    unsupported attribute type is requested, the action will fail. The .mov file may be read back into Maya using the movIn
    command.
    
    Flags:
      - comment : c                    (bool)          [create]
          If true, the attributes written to the .mov file will be listed in a commented section at the top of the .mov file. The
          default is false.
    
      - file : f                       (unicode)       [create]
          The name of the .mov file. If no extension is used, a .mov will be added.
    
      - precision : pre                (int)           [create]
          Sets the number of digits to the right of the decimal place in the .mov file.C: The default is 6.
    
      - time : t                       (timerange)     [create]
          The time range to save as a .mov file. The default is the current time range.                  Flag can have multiple
          arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.movOut`
    """

    pass


def currentTime(*args, **kwargs):
    """
    When given a time argument (with or without the -edit flag) this command sets the current global time.  The model
    updates and displays at the new time, unless -update offis present on the command line.
    
    Modifications:
        - if no args are provided, the command returns the current time
    
    Flags:
      - update : u                     (bool)          [create]
          change the current time, but do not update the world. Default value is true.                  Flag can have multiple
          arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.currentTime`
    """

    pass


def evaluationManager(*args, **kwargs):
    """
    Handles turning on and off the evaluation manager method of evaluating the DG. Query the 'mode' flag to see all
    available evaluation modes. The special mode 'off' disables the evaluation manager. The scheduling override flags
    'nodeTypeXXX' force certain node types to use specific scheduling types, even though the node descriptions might
    indicate otherwise. Use with caution; certain nodes may not react well to alternative scheduling types. Only one
    scheduling type override will be in force at a time, the most restrictive one. In order, they are untrusted, globally
    serialized, locally serialized, and parallel. The node types will however remember all overrides. For example, if you
    set a node type override to be untrusted, then to be parallel it will continue to use the untrusted override. If you
    then turn off the untrusted override, the scheduling will advance to the parallel one. The actual node scheduling type
    is always superceded by the overrides. For example, a serial node will still be considered as parallel if the node type
    has the parallel override set, even though 'serial' is a more restrictive scheduling type. See the 'dbpeek' command
    'graph' operation with arguments 'evaluationGraph' and 'scheduling' to see what scheduling type any particular node will
    end up using after the hierarchy of overrides and native scheduling types is applied.
    
    Flags:
      - cycleCluster : ccl             (unicode)       [create,query]
          Returns a list of nodes that are stored together with the given one in a cycle cluster. The list will be empty when the
          evaluation mode is not active or the node is not in a cycle.
    
      - downstreamFrom : dst           (unicode)       [create,query]
          Find the DG nodes that are immediately downstream of the named one in the evaluation graph. Note that the connectivity
          is via evaluation mode connections, not DG connections. In query mode the graph is walked and any nodes downstream of
          the named one are returned. The return type is alternating pairs of values that represent the graph level and the node
          name, e.g. if you walk downstream from A in the graph A -B -C then the return will be the array of strings
          (0,A,1,B,2,C). Scripts can deconstruct this information into something more visually recognizable. Note that cycles are
          likely to be present so any such scripts would have to handle them.
    
      - enabled : e                    (bool)          [query]
          Valid in query mode only. Checks to see if the evaluation manager is currently enabled. This is independent of the
          current mode.
    
      - idleBuild : ib                 (bool)          [create,query]
          This flag sets the rebuild option. If set to true then the evaluation graph will rebuild on an idle event as soon as it
          is able to do so. If false then it will only rebuild when required, for example at the start of playback. Note: This
          only applies to the graph attached to the normal context. All other graphs will be built according to their own rules.
          The disadvantage of building on an idle event is that for some workflows that are changing the graph frequently, or very
          large graphs, the graph build time may impact the workflow. The default is to have idleBuild turned on. If the build
          time is impacted, this flag can be turned off.
    
      - invalidate : inv               (bool)          [create,query]
          This flag invalidates the graph. Value is used to control auto rebuilding on idle (false) or forced (true). This command
          should be used as a last resort. In query mode it checks to see if the graph is valid.
    
      - manipulation : man             (bool)          [create,query]
          This flag is used to activate evaluation manager manipulation support.
    
      - mode : m                       (unicode)       [create,query]
          Changes the current evaluation mode in the evaluation manager. Supported values are off, serial, serialUncachedand
          parallel.
    
      - nodeTypeGloballySerialize : ntg (bool)          [create,query]
          This flag is used only when the evaluation manager is in parallelmode but can be set at anytime. It activates or
          deactivates the override to force global serial scheduling for the class name argument(s) in the evaluation manager.
          Legal object values are class type names: e.g. transform, skinCluster, mesh. When queried without specified nodes, it
          returns the list of nodes with the global serial scheduling override active. Scheduling overrides take precedence over
          all of the node and node type scheduling rules. Use with caution; certain nodes may not react well to alternative
          scheduling types.
    
      - nodeTypeParallel : ntp         (bool)          [create,query]
          This flag is used only when the evaluation manager is in parallelmode but can be set at anytime. It activates or
          deactivates the override to force parallel scheduling for the class name argument(s) in the evaluation manager. Legal
          object values are class type names: e.g. transform, skinCluster, mesh. When queried without specified nodes, it returns
          the list of nodes with the parallel scheduling override active. Scheduling overrides take precedence over all of the
          node and node type scheduling rules. Use with caution; certain nodes may not react well to alternative scheduling types.
    
      - nodeTypeSerialize : nts        (bool)          [create,query]
          This flag is used only when the evaluation manager is in parallelmode but can be set at anytime. It activates or
          deactivates the override to force local serial scheduling for the class name argument(s) in the evaluation manager.
          Legal object values are class type names: e.g. transform, skinCluster, mesh. When queried without specified nodes, it
          returns the list of nodes with the local serial scheduling override active. Scheduling overrides take precedence over
          all of the node and node type scheduling rules. Use with caution; certain nodes may not react well to alternative
          scheduling types.
    
      - nodeTypeUntrusted : ntu        (bool)          [create,query]
          This flag is used only when the evaluation manager is in parallelmode but can be set at anytime. It activates or
          deactivates the override to force untrusted scheduling for the class name argument(s) in the evaluation manager. Legal
          object values are class type names: e.g. transform, skinCluster, mesh. When queried without specified nodes, it returns
          the list of nodes with the untrusted scheduling override active. Scheduling overrides take precedence over all of the
          node and node type scheduling rules. Use with caution; certain nodes may not react well to alternative scheduling types.
          Untrusted scheduling will allow nodes to be evaluated in a critical section, separately from any other node evaluation.
          It should be used only as a last resort since the lost parallelism caused by untrusted nodes can greatly reduce
          performance.
    
      - safeMode : sfm                 (bool)          [create,query]
          This flag activates/deactivates parallel evaluation safe mode. When enabled, parallel execution will fall back to serial
          when evaluation graph is missing dependencies. Detection is happening on scheduling of parallel evaluation, which means
          potential fallback will happen at the next evaluation. WARNING: This mode should be disabled with extreme caution. It
          will prevent parallel mode from falling back to serial mode when an invalid evaluation is detected. Sometimes the
          evaluation will still work correctly in those situations and use of this flag will keep the peak parallel performance
          running. However since the safe mode is used to catch invalid evaluation disabling it may also cause problems with
          evaluation, anything from invalid values, missing evaluation, or even crashes.                                   Flag
          can have multiple arguments, passed either as a tuple or a list.
    
      - upstreamFrom : ust             (unicode)       [create,query]
          Find the DG nodes that are immediately upstream of the named one in the evaluation graph. Note that the connectivity is
          via evaluation mode connections, not DG connections. In query mode the graph is walked and any nodes upstream of the
          named one are returned. The return type is alternating pairs of values that represent the graph level and the node name,
          e.g. if you walk upstream from C in the graph A -B -C then the return will be the array of strings (0,C,1,B,2,A).
          Scripts can deconstruct this information into something more visually recognizable. Note that cycles are likely to be
          present so any such scripts would have to handle them.
    
    
    Derived from mel command `maya.cmds.evaluationManager`
    """

    pass


def timeEditorAnimSource(*args, **kwargs):
    """
    Commands for managing animation sources.
    
    Flags:
      - addObjects : ao                (unicode)       [create,query,edit]
          Populate the given object(s) and their attributes to anim source to Time Editor. For multiple object, pass each name
          separated by semicolon. In query mode, return the number of attributes that will be populated given the flags, along
          with the animation's first and last frames for the given object(s). Similar to -addSelectedObjectsflag but acts on given
          object(s) instead. This flag will override the flag -addSelectedObjects.
    
      - addRelatedKG : akg             (bool)          [create,query,edit]
          During population, determine if associated keying groups should be populated or not. Normally used for populating HIK.
          By default the value is false.
    
      - addSelectedObjects : aso       (bool)          [create,query,edit]
          Populate the currently selected objects and their attributes to anim source or Time Editor. In query mode, return the
          number of attributes that will be populated given the flags, along with the animation's first and last frames.
    
      - addSource : asc                (unicode)       [edit]
          Add single new target attribute with its animation.
    
      - apply : ap                     (bool)          [edit]
          Connect anim source's animation directly to the target objects. If the Time Editor is not muted, connect to scene
          storage instead.
    
      - attribute : at                 (unicode)       [create,edit]
          Populate a specific attribute on a object.
    
      - bakeToAnimSource : bas         (unicode)       [edit]
          Create a new anim source with the same animation as this anim source. All non-curve inputs will be baked down, whereas
          curve sources will be shared.
    
      - calculateTiming : ct           (bool)          [edit]
          Adjust start/duration when adding/removing sources.
    
      - copyAnimation : cp             (bool)          [edit]
          Copy animation when adding source.
    
      - drivenClips : dc               (bool)          [query]
          Return all clips driven by the given anim source.
    
      - exclusive : exc                (bool)          [create,edit]
          Populate all types of animation sources which are not listed by typeFlag.
    
      - export : ex                    (unicode)       [edit]
          Export given anim source and the animation curves to a specified Maya file.
    
      - importAllFbxTakes : aft        (bool)          [create]
          Import all FBX takes into the new anim sources (for timeEditorAnimSource command) or new containers (for timeEditorClip
          command).
    
      - importFbx : fbx                (unicode)       [create]
          Import an animation from FBX file into the new anim source (for timeEditorAnimSource command) or new container (for
          timeEditorClip command).
    
      - importFbxTakes : ft            (unicode)       [create]
          Import multiple FBX takes (separated by semicolons) into the new anim sources (for timeEditorAnimSource command) or new
          containers (for timeEditorClip command).
    
      - importMayaFile : mf            (unicode)       [create]
          Import an animation from Maya file into the new anim sources (for timeEditorAnimSource command) or new containers (for
          timeEditorClip command).
    
      - importOption : io              (unicode)       [edit]
          Option for importing animation source. Specify either 'connect' or 'generate'. connect:  Only connect with nodes already
          existing in the scene.                   Importing an animation source which does not match with any element
          of the current scene will not create any clip.                   (connect is the default mode). generate: Import
          everything and generate new nodes for items not existing in the scene.
    
      - importPopulateOption : ipo     (unicode)       [edit]
          Option for population when importing.
    
      - importedContainerNames : icn   (unicode)       [create]
          Internal use only. To be used along with populateImportedAnimSourcesto specify names for the created containers.
    
      - includeRoot : irt              (bool)          [create,edit]
          Populate TRS of hierarchy root nodes.
    
      - isUnique : iu                  (bool)          [query]
          Return true if the anim source node is only driving a single clip.
    
      - populateImportedAnimSources : pia (unicode)       [create]
          Internal use only. Populate the Time Editor with clips using the Animation Sources specified (use ; as a delimiter for
          multiple anim sources).
    
      - poseClip : poc                 (bool)          [create]
          Populate as pose clip with current attribute values.
    
      - recursively : rec              (bool)          [create,edit]
          Populate selection recursively, adding all the children.
    
      - removeSceneAnimation : rsa     (bool)          [create,edit]
          If true, remove animation from scene when creating clips or anim sources. Only Time Editor will drive the removed scene
          animation.
    
      - removeSource : rs              (unicode)       [edit]
          Remove single attribute.
    
      - showAnimSourceRemapping : sar  (bool)          [create]
          Show a remapping dialog when the imported anim source attributes do not match the scene attributes.
    
      - takeList : tl                  (unicode)       [create]
          Internal use only. To be used along with populateImportedAnimSourcesto specify the imported take names.
    
      - takesToImport : toi            (unicode)       [create]
          Internal use only. To be used along with populateImportedAnimSourcesto specify the imported take indices.
    
      - targetIndex : ti               (unicode)       [query]
          Get target index.
    
      - targets : trg                  (bool)          [query]
          Get a list of all targets in this anim source.
    
      - type : typ                     (unicode)       [create,query,edit]
          Only populate the specified type of animation source.                              Flag can have multiple arguments,
          passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.timeEditorAnimSource`
    """

    pass


def jointLattice(*args, **kwargs):
    """
    This command creates/edits/queries a jointLattice deformer. The name of the created/edited object is returned. Usually
    you would make use of this functionality through the higher level flexor command.
    
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
    
      - creasing : cr                  (float)         [create,query,edit]
          Affects the bulging of lattice points on the inside of the bend.  Positive/negative values cause the points to bulge
          outwards/inwards. Default value is 0.0. When queried, this flag returns a float.
    
      - deformerTools : dt             (bool)          [query]
          Returns the name of the deformer tool objects (if any) as string string ...
    
      - exclusive : ex                 (unicode)       [create,query]
          Puts the deformation set in a deform partition.
    
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
    
      - joint : j                      (unicode)       [create]
          Specifies the joint which will be used to drive the bulging behaviours.
    
      - lengthIn : li                  (float)         [create,query,edit]
          Affects the location of lattice points on the parent bone.  Positive/negative values cause the points to move
          away/towards the joint. Changing this parameter also modifies the regions affected by the creasing, rounding and width
          parameters. Default value is 0.0. When queried, this flag returns a float.
    
      - lengthOut : lo                 (float)         [create,query,edit]
          Affects the location of lattice points on the child bone. Positive/negative values cause the points to move away/towards
          the joint. Changing this parameter also modifies the regions affected by the creasing, rounding and width parameters.
          Default value is 0.0. When queried, this flag returns a float.
    
      - lowerBindSkin : lb             (unicode)       [create]
          Specifies the node which is performing the bind skin operation on the geometry associated with the lower bone.
    
      - lowerTransform : lt            (unicode)       [create]
          Specifies which dag node is being used to rigidly transform the lower part of the lattice which this node is going to
          deform. If this flag is not specified an identity matrix will be assumed.
    
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
    
      - rounding : ro                  (float)         [create,query,edit]
          Affects the bulging of lattice points on the outside of the bend. Positive/negative values cause the points to bulge
          outwards/inwards. Default value is 0.0. When queried, this flag returns a float.
    
      - split : sp                     (bool)          [create,edit]
          Branches off a new chain in the dependency graph instead of inserting/appending the deformer into/onto an existing
          chain. Works in create mode (and edit mode if the deformer has no geometry added yet).
    
      - upperBindSkin : ub             (unicode)       [create]
          Specifies the node which is performing the bind skin operation on the geometry associated with the upper bone.
    
      - upperTransform : ut            (unicode)       [create]
          Specifies which dag node is being used to rigidly transform the upper part of the lattice which this node is going to
          deform. If this flag is not specified an identity matrix will be assumed.
    
      - widthLeft : wl                 (float)         [create,query,edit]
          Affects the bulging of lattice points on the left side of the bend. Positive/negative values cause the points to bulge
          outwards/inwards. Default value is 0.0. When queried, this flag returns a float.
    
      - widthRight : wr                (float)         [create,query,edit]
          Affects the bulging of lattice points on the right side of the bend. Positive/negative values cause the points to bulge
          outwards/inwards. Default value is 0.0. When queried, this flag returns a float.                  Flag can have multiple
          arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.jointLattice`
    """

    pass


def deformer(*args, **kwargs):
    """
    This command creates a deformer of the specified type. The deformer will deform the selected objects.
    
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
    
      - deformerTools : dt             (bool)          [query]
          Returns the name of the deformer tool objects (if any) as string string ...
    
      - exclusive : ex                 (unicode)       [create,query]
          Puts the deformation set in a deform partition.
    
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
    
      - split : sp                     (bool)          [create,edit]
          Branches off a new chain in the dependency graph instead of inserting/appending the deformer into/onto an existing
          chain. Works in create mode (and edit mode if the deformer has no geometry added yet).
    
      - type : typ                     (unicode)       [create]
          Specify the type of deformer to create. This flag is required in create mode. Typically the type should specify a loaded
          plugin deformer. This command should typically not be used to create one of the standard deformers such as sculpt,
          lattice, blendShape, wire and cluster, since they have their own customized commands which perform useful specialized
          functionality.                  Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.deformer`
    """

    pass


def findKeyframe(*args, **kwargs):
    """
    This command operates on a keyset.  A keyset is defined as a group of keys within a specified time range on one or more
    animation curves. The animation curves comprising a keyset depend on the value of the -animationflag: keysOrObjects: Any
    active keys, when no target objects or -attribute flags appear on the command line, orAll animation curves connected to
    all keyframable attributes of objects specified as the command line's targetList, when there are no active keys.keys:
    Only act on active keys or tangents. If there are no active keys or tangents, don't do anything. objects: Only act on
    specified objects.  If there are no objects specified, don't do anything. Note that the -animationflag can be used to
    override the curves uniquely identified by the multi-use -attributeflag, which takes an argument of the form
    attributeName, such as translateX. Keys on animation curves are identified by either their time values or their indices.
    Times and indices can be given individually or as part of a list or range. -time 10palmeans the key at frame 10 (PAL
    format).-time 1.0sec -time 15ntsc -time 20means the keys at time 1.0 second, frame 15 (in NTSC format), and time 20 (in
    the currently defined global time unit).-time 10:20means all keys in the range from 10 to 20, inclusive, in the current
    time unit.Omitting one end of a range means go to infinity, as in the following examples: -time 10:means all keys from
    time 10 (in the current time unit) onwards.-time :10means all keys up to (and including) time 10 (in the current time
    unit).-time :is a short form to specify all keys.-index 0means the first key of each animation curve. (Indices are
    0-based.)-index 2 -index 5 -index 7means the 3rd, 6th, and 8th keys.-index 1:5means the 2nd, 3rd, 4th, 5th, and 6th keys
    of each animation curve.This command will return the time (in current units) of the requested key. For the relative
    direction methods (next, previous) if -time is NOT specified they will use current time. If the specified object is not
    animated the command will return the current time.
    
    Flags:
      - animation : an                 (unicode)       [create]
          Where this command should get the animation to act on.  Valid values are objects,keys,and keysOrObjectsDefault:
          keysOrObjects.(See Description for details.)
    
      - attribute : at                 (unicode)       [create]
          List of attributes to select
    
      - controlPoints : cp             (bool)          [create]
          This flag explicitly specifies whether or not to include the control points of a shape (see -sflag) in the list of
          attributes. Default: false.  (Not valid for pasteKeycmd.)
    
      - curve : c                      (bool)          [create]
          Return a list of the existing curves driving the selected object or attributes. The which, index, floatRange, timeRange,
          and includeUpperBound flags are ignored when this flag is used.
    
      - float : f                      (floatrange)    [create]
          value uniquely representing a non-time-based key (or key range) on a time-based animCurve.  Valid floatRange include
          single values (-f 10) or a string with a lower and upper bound, separated by a colon (-f 10:20
    
      - hierarchy : hi                 (unicode)       [create]
          Hierarchy expansion options.  Valid values are above,below,both,and none.(Not valid for pasteKeycmd.)
    
      - includeUpperBound : iub        (bool)          [create]
          When the -t/time or -f/float flags represent a range of keys, this flag determines whether the keys at the upper bound
          of the range are included in the keyset. Default value: true.  This flag is only valid when the argument to the -t/time
          flag is a time range with a lower and upper bound.  (When used with the pasteKeycommand, this flag refers only to the
          time range of the target curve that is replaced, when using options such as replace,fitReplace,or scaleReplace.This flag
          has no effect on the curve pasted from the clipboard.)
    
      - index : index                  (int)           [create]
          index of a key on an animCurve
    
      - shape : s                      (bool)          [create]
          Consider attributes of shapes below transforms as well, except controlPoints.  Default: true.  (Not valid for
          pasteKeycmd.)
    
      - time : t                       (timerange)     [create]
          time uniquely representing a key (or key range) on a time-based animCurve.  Valid timeRanges include single values (-t
          10) or a string with a lower and upper bound, separated by a colon (-t 10:20
    
      - timeSlider : ts                (bool)          [create]
          Get the next key time from the ticks displayed in the time slider. If this flag is set, then the -an/animation flag is
          ignored.
    
      - which : w                      (unicode)       [create]
          next | previous | first | last How to find the key                  Flag can have multiple arguments, passed either as a
          tuple or a list.
    
    
    Derived from mel command `maya.cmds.findKeyframe`
    """

    pass


def pointConstraint(*args, **kwargs):
    """
    Constrain an object's position to the position of the target object or to the average position of a number of targets. A
    pointConstraint takes as input one or more targetDAG transform nodes at which to position the single constraint
    objectDAG transform node.  The pointConstraint positions the constrained object at the weighted average of the world
    space position target objects.
    
    Maya Bug Fix:
      - when queried, angle offsets would be returned in radians, not current angle unit
    
    Modifications:
      - added new syntax for querying the weight of a target object, by passing the constraint first::
    
            aimConstraint( 'pCube1_aimConstraint1', q=1, weight ='pSphere1' )
            aimConstraint( 'pCube1_aimConstraint1', q=1, weight =['pSphere1', 'pCylinder1'] )
            aimConstraint( 'pCube1_aimConstraint1', q=1, weight =[] )
    
    Flags:
      - layer : l                      (unicode)       [create,edit]
          Specify the name of the animation layer where the constraint should be added.
    
      - maintainOffset : mo            (bool)          [create]
          The offset necessary to preserve the constrained object's initial position will be calculated and used as the offset.
    
      - name : n                       (unicode)       [create,query,edit]
          Sets the name of the constraint node to the specified name.  Default name is constrainedObjectName_constraintType
    
      - offset : o                     (float, float, float) [create,query,edit]
          Sets or queries the value of the offset. Default is 0,0,0.
    
      - remove : rm                    (bool)          [edit]
          removes the listed target(s) from the constraint.
    
      - skip : sk                      (unicode)       [create,edit]
          Specify the axis to be skipped. Valid values are x, y, zand none. During creation, noneis the default. This flag is
          multi-use.
    
      - targetList : tl                (bool)          [query]
          Return the list of target objects.
    
      - weight : w                     (float)         [create,query,edit]
          Sets the weight value for the specified target(s). If not given at creation time, the default value of 1.0 is used.
    
      - weightAliasList : wal          (bool)          [query]
          Returns the names of the attributes that control the weight of the target objects. Aliases are returned in the same
          order as the targets are returned by the targetList flag                  Flag can have multiple arguments, passed
          either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.pointConstraint`
    """

    pass


def skinPercent(*args, **kwargs):
    """
    This command edits and queries the weight values on members of a skinCluster node, given as the first argument. If no
    object components are explicitly mentioned in the command line, the current selection list is used. Note that setting
    multiple weights in a single invocation of this command is far more efficient than calling it once per weighted vertex.
    In query mode, return type is based on queried flag.
    
    Flags:
      - ignoreBelow : ib               (float)         [query]
          Limits the output of the -value and -transform queries to the entries whose weight values are over the specified limit.
          This flag has to be used before the -query flag.
    
      - normalize : nrm                (bool)          [create]
          If set, the weights not assigned by the -transformValue flag are normalized so that the sum of the all weights for the
          selected object component add up to 1. The default is on. NOTE: The skinCluster has a normalizeWeights attribute which
          when set to OFF overrides this attribute! If the skinCluster.normalizeWeights attribute is OFF, you must set it to
          Interactive in order to normalize weights using the skinPercent command.
    
      - pruneWeights : prw             (float)         [create]
          Sets to zero any weight smaller than the given value for all the selected components. To use this command to set all the
          weights to zero, you must turn the -normalize flag offor the skinCluster node will normalize the weights to sum to one
          after pruning them. Weights for influences with a true value on their Hold Weightsattribute will not be pruned.
    
      - relative : r                   (bool)          [create]
          Used with -transformValue to specify a relative setting of values. If -relative is true, the value passed to -tv is
          added to the previous value.  Otherwise, it replaces the previous value.
    
      - resetToDefault : rtd           (bool)          [create]
          Sets the weights of the selected components to their default values, overwriting any custom weights.
    
      - transform : t                  (unicode)       [query]
          If used after the -query flag (without an argument) the command returns an array of strings corresponding to the names
          of the transforms influencing the selected object components.  If used before the -query flag (with a transform name),
          the command returns the weight of the selected object component corresponding to the given transform. The command will
          return an average weight if several components have been selected.       In query mode, this flag can accept a value.
    
      - transformMoveWeights : tmw     (unicode)       [create]
          This flag is used to transfer weights from a source influence to one or more target influences. It acts on the selected
          vertices. The flag must be used at least twice to generate a valid command. The first flag usage indicates the source
          influence from which the weights will be copied. Subsequent flag usages indicate the target influences.
    
      - transformValue : tv            (unicode, float) [create]
          Accepts a pair consisting of a transform name and a value and assigns that value as the weight of the selected object
          components corresponding to the given transform.
    
      - value : v                      (bool)          [query]
          Returns an array of doubles corresponding to the joint weights for the selected object component.
    
      - zeroRemainingInfluences : zri  (bool)          [create]
          If set, the weights not assigned by the -transformValue flag are set to 0. The default is off.                  Flag can
          have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.skinPercent`
    """

    pass


def clipEditor(*args, **kwargs):
    """
    Create a clip editor with the given name.
    
    Flags:
      - allTrackHeights : th           (int)           []
          OBSOLETE flag. Use clipStyle instead.
    
      - autoFit : af                   (unicode)       [query,edit]
          on | off | tgl Auto fit-to-view.
    
      - characterOutline : co          (unicode)       []
    
      - clipDropCmd : cd               (unicode)       [edit]
          Command executed when clip node is dropped on the TraX editor
    
      - clipStyle : cs                 (int)           [query,edit]
          Set/return the clip track style in the specified editor. Default is 2. Valid values are 1-3.
    
      - control : ctl                  (bool)          [query]
          Query only. Returns the top level control for this editor. Usually used for getting a parent to attach popup menus.
          Caution: It is possible for an editor to exist without a control. The query will return NONEif no control is present.
    
      - defineTemplate : dt            (unicode)       [create]
          Puts the command in a mode where any other flags and args are parsed and added to the command template specified in the
          argument. They will be used as default arguments in any subsequent invocations of the command when templateName is set
          as the current template.
    
      - deleteCmd : dc                 (unicode)       [edit]
          Command executed when backspacekey is pressed
    
      - deselectAll : da               (bool)          [edit]
          Deselect all clips and blends in the editor.
    
      - displayActiveKeyTangents : dat (unicode)       [edit]
          on | off | tgl Display active key tangents in the editor.
    
      - displayActiveKeys : dak        (unicode)       [edit]
          on | off | tgl Display active keys in the editor.
    
      - displayInfinities : di         (unicode)       [edit]
          on | off | tgl Display infinities in the editor.
    
      - displayKeys : dk               (unicode)       [edit]
          on | off | tgl Display keyframes in the editor.
    
      - displayTangents : dtn          (unicode)       [edit]
          on | off | tgl Display tangents in the editor.
    
      - displayValues : dv             (unicode)       [edit]
          on | off | tgl Display active keys and tangents values in the editor.
    
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
    
      - frameAll : fa                  (bool)          [edit]
          Frame view around all clips in the editor.
    
      - frameRange : fr                (float, float)  [query,edit]
          The editor's current frame range.
    
      - highlightConnection : hlc      (unicode)       [create,query,edit]
          Specifies the name of a selectionConnection object that the editor will synchronize with its highlight list. Not all
          editors have a highlight list. For those that do, it is a secondary selection list.
    
      - highlightedBlend : hb          (unicode, unicode) [query]
          Returns the highlighted blend, listed as scheduler and index
    
      - highlightedClip : hc           (unicode, unicode) [query]
          Returns the highlighted clip, listed as scheduler and index
    
      - initialized : it               (bool)          [query]
          Returns whether the clip editor is fully initialized, and has a port to draw through. If not, the -frameRange and
          -frameAll flags will fail.
    
      - listAllCharacters : lac        (bool)          [edit]
          List all characters in the editor and outliner.
    
      - listCurrentCharacters : lc     (bool)          [edit]
          List only the characters in the editor and outliner.
    
      - lockMainConnection : lck       (bool)          [create,edit]
          Locks the current list of objects within the mainConnection, so that only those objects are displayed within the editor.
          Further changes to the original mainConnection are ignored.
    
      - lookAt : la                    (unicode)       [edit]
          all | selected | currentTime FitView helpers.
    
      - mainListConnection : mlc       (unicode)       [create,query,edit]
          Specifies the name of a selectionConnection object that the editor will use as its source of content. The editor will
          only display items contained in the selectionConnection object.
    
      - manageSequencer : ms           (bool)          [create,query,edit]
          Sets/returns whether the clip editor should manage sequencer nodes.  If so, animation clips and characters are not
          represented.
    
      - menuContext : mc               (unicode)       [query]
          Returns a string array denoting the type of data object the cursor is over.  Returned values are: timeSlider nothing
          track, track index, character node name, group name clip, clip node name
    
      - panel : pnl                    (unicode)       [create,query]
          Specifies the panel for this editor. By default if an editor is created in the create callback of a scripted panel it
          will belong to that panel. If an editor does not belong to a panel it will be deleted when the window that it is in is
          deleted.
    
      - parent : p                     (unicode)       [create,query,edit]
          Specifies the parent layout for this editor. This flag will only have an effect if the editor is currently un-parented.
    
      - selectBlend : sb               (unicode, unicode, unicode) [query,edit]
          Select the blends specified by the scheduler name and the indicies of the two clips used in the blend. When queried, a
          string containing the scheduler name and the two clip indicies for all of the selected blends is returned.
    
      - selectClip : sc                (unicode, unicode) [query,edit]
          Selects the clip specified by the scheduler name and the clip index. When queried, a string containing the scheduler and
          clip index of all of the selected clips is returned.
    
      - selectionConnection : slc      (unicode)       [create,query,edit]
          Specifies the name of a selectionConnection object that the editor will synchronize with its own selection list. As the
          user selects things in this editor, they will be selected in the selectionConnection object. If the object undergoes
          changes, the editor updates to show the changes.
    
      - snapTime : st                  (unicode)       [query,edit]
          none | integer | keyframe Keyframe move snap in time.
    
      - snapValue : sv                 (unicode)       [query,edit]
          none | integer | keyframe Keyframe move snap in values.
    
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
          Forces the command to use a command template other than the current one.                  Flag can have multiple
          arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.clipEditor`
    """

    pass


def animDisplay(*args, **kwargs):
    """
    This command changes certain display options used by animation windows. In query mode, return type is based on queried
    flag.
    
    Flags:
      - modelUpdate : upd              (unicode)       [create,query,edit]
          Controls how changes to animCurves are propagated through the dependency graph. Valid modes are none, interactiveor
          delayed. If modelUpdate is nonethen changing an animCurve will not cause the model to be updated (change currentTime in
          order to update the model).  If modelUpdate is interactive(which is the default setting), then as interactive changes
          are being made to the animCurve, the model will be updated.  If modelUpdate is delayed, then the model is updated once
          the final change to an animCurve has been made.  With modelUpdate set to either interactiveor delayed, changes to
          animCurves made via commands will also cause the model to be updated.
    
      - refAnimCurvesEditable : rae    (bool)          [create,query,edit]
          Specify if animation curves from referenced files are editable.
    
      - timeCode : tc                  (bool)          [create,query,edit]
          Controls whether the animation windows (time slider, graph editor and dope sheet) use time codes in their displays.
    
      - timeCodeOffset : tco           (unicode)       [create,query,edit]
          This flag has now been deprecated.  It still exists to not break legacy scripts, but it will now do nothing.  See the
          new timeCode command to set and query timeCodes.                  Flag can have multiple arguments, passed either as a
          tuple or a list.
    
    
    Derived from mel command `maya.cmds.animDisplay`
    """

    pass


def setCurrentTime(time):
    """
    set the current time
    """

    pass


def setDrivenKeyframe(*args, **kwargs):
    """
    This command sets a driven keyframe.  A driven keyframe is similar to a regular keyframe. However, while a standard
    keyframe always has an x-axis of time in the graph editor, for a drivenkeyframe the user may choose any attribute as the
    x-axis of the graph editor. For example, you can keyframe the emission of a faucet so that so that it emits whenever the
    faucet handle is rotated around y. The faucet emission in this example is called the driven attribute. The handle
    rotation is called the driver. Once you have used setDrivenKeyframe to set up the relationship between the emission and
    the rotation, you can go to the graph editor and modify the relationship between the attributes just as you would modify
    the animation curve on any keyframed object. In the case of an attribute driven by a single driver, the dependency graph
    is connected like this: driver attribute ---animCurve ---driven attribute You can set driven keyframes with more than a
    single driver. The effects of the multiple drivers are combined together by a blend node.
    
    Flags:
      - attribute : at                 (unicode)       [create]
          Attribute name to set keyframes on.
    
      - controlPoints : cp             (bool)          [create]
          Explicitly specify whether or not to include the control points of a shape (see -sflag) in the list of attributes.
          Default: false.
    
      - currentDriver : cd             (unicode)       [create,query]
          Set the driver to be used for the current driven keyframe to the attribute passed as an argument.
    
      - driven : dn                    (bool)          [query]
          Returns list of driven attributes for the selected item.
    
      - driver : dr                    (bool)          [query]
          Returns list of available drivers for the attribute.
    
      - driverValue : dv               (float)         [create]
          Value of the driver to use for this keyframe. Default value is the current value.
    
      - hierarchy : hi                 (unicode)       [create]
          Controls the objects this command acts on, relative to the specified (or active) target objects. Valid values are
          above,below,both,and none.Default is hierarchy -query
    
      - inTangentType : itt            (unicode)       [create]
          The in tangent type for keyframes set by this command. Valid values are: auto, clamped, fast, flat, linear, plateau,
          slow, spline, and stepnextDefault is keyTangent -q -g -inTangentType
    
      - insert : i                     (bool)          [create]
          Insert keys at the given time(s) and preserve the shape of the animation curve(s). Note: the tangent type on inserted
          keys will be fixed so that the curve shape can be preserved.
    
      - insertBlend : ib               (bool)          [create]
          If true, a pairBlend node will be inserted for channels that have nodes other than animCurves driving them, so that such
          channels can have blended animation. If false, these channels will not have keys inserted. If the flag is not specified,
          the blend will be inserted based on the global preference for blending animation.
    
      - outTangentType : ott           (unicode)       [create]
          The out tangent type for keyframes set by this command. Valid values are: auto, clamped, fast, flat, linear, plateau,
          slow, spline, step, and stepnext. Default is keyTangent -q -g -outTangentType
    
      - shape : s                      (bool)          [create]
          Consider attributes of shapes below transforms as well, except controlPoints.  Default: true
    
      - value : v                      (float)         [create]
          Value to set the keyframe at. Default is the current value.                  Flag can have multiple arguments, passed
          either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.setDrivenKeyframe`
    """

    pass


def ikSystem(*args, **kwargs):
    """
    The ikSystem command is used to set the global snapping flag for handles and set the global solve flag for solvers.  The
    standard edit (-e) and query (-q) flags are used for edit and query functions.
    
    Flags:
      - allowRotation : ar             (bool)          [query,edit]
          Set true to allow rotation of an ik handle with keys set on translation.
    
      - autoPriority : ap              (bool)          [edit]
          set autoPriority for all ikHandles
    
      - autoPriorityMC : apm           (bool)          [edit]
          set autoPriority for all multiChain handles
    
      - autoPrioritySC : aps           (bool)          [edit]
          set autoPriority for all singleChain handles
    
      - list : ls                      (int, int)      [query,edit]
          returns the solver execution order when in query mode(list of strings) changes execution order when in edit mode (int
          old position, int new position)
    
      - snap : sn                      (bool)          [query,edit]
          Set global snapping
    
      - solve : sol                    (bool)          [query,edit]
          Set global solve
    
      - solverTypes : st               (bool)          [query]
          returns a list of valid solverTypes ( query only )                  Flag can have multiple arguments, passed either as a
          tuple or a list.
    
    
    Derived from mel command `maya.cmds.ikSystem`
    """

    pass


def bindSkin(*args, **kwargs):
    """
    This command binds the currently selected objects to the currently selected skeletons.  Shapes which can be bound are:
    meshes, nurbs curves, nurbs surfaces, lattices, subdivision surfaces, and API shapes. Multiple shapes and multiple
    skeletons can be bound at once by selecting them or specifying them on the command line. Selection order is not
    important.The skin is bound using the so-called rigidbind, in which the components are rigidly attached to the closest
    bone in the skeleton. Flexors can later be added to the skeleton to smooth out the skinning around joints.The skin(s)
    can be bound either to the entire skeleton hierarchy of the selected joint(s), or to only the selected joints. The
    entire hierarchy is the default. The -tsb/-toSelectedBones flag allows binding to only the selected bones.This command
    can also be used to detach the skin from the skeleton. Detaching the skin is useful in a variety of situations, such as:
    inserting additional bones, deleting bones, changing the bind position of the skeleton or skin, or simply getting rid of
    the skinning nodes altogether. The options to use when detaching the skin depend on how much of the skinning info you
    want to get rid of. Namely: (1) -delete or -unbind: remove all skinning nodes, (2) -unbindKeepHistory: remove the
    skinning sets, but keep the weights, (3) -disable: disable the skinning but keep the skinning sets and the weights.
    
    Flags:
      - byClosestPoint : bcp           (bool)          [create]
          bind each point in the object to the segment closest to the point. The byClosestPoint and byPartition flags are mutually
          exclusive.  The byClosestPoint flag is the default.
    
      - byPartition : bp               (bool)          [create]
          bind each group in the partition to the segment closest to the group's centroid. A partition must be specified with the
          -p/-partition flag
    
      - colorJoints : cj               (bool)          [create]
          In bind mode, this flag assigns colors to the joints based on the colors assigned to the joint's skin set. In delete and
          unlock mode, this flag removes the colors from joints that are no longer bound as skin. In disable and unbindKeepHistory
          mode, this flag does nothing.
    
      - delete : d                     (bool)          [create]
          Detach the skin on the selected skeletons and remove all bind- related construction history.
    
      - doNotDescend : dnd             (bool)          [create]
          Do not descend to shapes that are parented below the selected object(s). Bind only the selected objects.
    
      - enable : en                    (bool)          [create]
          Enable or disable a bind that has been disabled on the selected skeletons. To enable the bind on selected bones only,
          select the bones and use the -tsb flag with the -en flag. This flag is used when you want to temporarily disable the
          bind without losing the set information or the weight information of the skinning, for example if you want to modify the
          bindPose.
    
      - name : n                       (unicode)       [create]
          This flag is obsolete.
    
      - partition : p                  (unicode)       [create]
          Specify a partition to bind by. This is only valid when used with the -bp/-byPartition flag.
    
      - toAll : ta                     (bool)          [create]
          objects will be bound to the entire selected skeletons. Even bones with zero influence will be bound, whereas the
          toSkeleton will only bind non-zero influences.
    
      - toSelectedBones : tsb          (bool)          [create]
          objects will be bound to the selected bones only.
    
      - toSkeleton : ts                (bool)          [create]
          objects will be bound to the selected skeletons. The toSkeleton, toAll and toSelectedBones flags are mutually exclusive.
          The toSkeleton flag is the default.
    
      - unbind : ub                    (bool)          [create]
          unbind the selected objects. They will no longer move with the skeleton. Any bindSkin history that is no longer used
          will be deleted.
    
      - unbindKeepHistory : ubk        (bool)          [create]
          unbind the selected objects. They will no longer move with the skeleton. However, existing weights on the skin will be
          kept for use the next time the skin is bound. This option is appropriate if you want to modify the skeleton without
          losing the weighting information on the skin.
    
      - unlock : ul                    (bool)          [create]
          unlock the selected objects. Since bindSkin will no longer give normal results if bound objects are moved away from the
          skeleton, bindSkin locks translate, rotate and scale. This command unlocks the selected objects translate, rotate and
          scale.                  Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.bindSkin`
    """

    pass


def animView(*args, **kwargs):
    """
    This command allows you to specify the current view range within an animation editor. In query mode, return type is
    based on queried flag.
    
    Flags:
      - endTime : et                   (time)          []
          End time to display within the editor
    
      - maxValue : max                 (float)         []
          Upper value to display within the editor
    
      - minValue : min                 (float)         []
          Lower value to display within the editor
    
      - nextView : nv                  (bool)          [edit]
          Switches to the next view.
    
      - previousView : pv              (bool)          [edit]
          Switches to the previous view.
    
      - startTime : st                 (time)          []
          Start time to display within the editor                  Flag can have multiple arguments, passed either as a tuple or a
          list.
    
    
    Derived from mel command `maya.cmds.animView`
    """

    pass


def enableDevice(*args, **kwargs):
    """
    Sets (or queries) the device enable state for actions involving the device. -monitoraffects all assignInputDevice and
    attachDeviceAttr actions for the named device-recordcontrols if the device is recorded (by default) by a recordDevice
    action-apply channelName [channelName ... ]controls if data from the  device channel is applied (by default) by
    applyTake to the param curves attached to the named channel.Disabling a channel for applyTake cause applyTake to ignore
    the enable state of all childchannels -- treating them as disabled. In query mode, return type is based on queried flag.
    
    Flags:
      - apply : a                      (bool)          [create,query]
          enable/disable applyTakefor the specified channel(s)
    
      - device : d                     (unicode)       [create,query]
          specifies the device to change
    
      - enable : en                    (bool)          [create,query]
          enable (or disable) monitor/record/apply
    
      - monitor : m                    (bool)          [create,query]
          enables/disables visible update for the device (default)
    
      - record : rec                   (bool)          [create,query]
          enable/disable recordDevicedevice recording                  Flag can have multiple arguments, passed either as a tuple
          or a list.
    
    
    Derived from mel command `maya.cmds.enableDevice`
    """

    pass


def shot(*args, **kwargs):
    """
    Use this command to create a shot node or manipulate that node.
    
    Flags:
      - audio : aud                    (unicode)       [create,query,edit]
          Specify the audio clip for this shot. Audio can be linked to a shot to allow playback of specific sounds when that shot
          is being displayed in the Sequencer. Refer to the shot node's documentation for details on how audio is used by shots
          and the Sequencer.
    
      - clip : cl                      (unicode)       [create,query,edit]
          The clip associated with this shot. This clip will be posted to the currentCamera's imagePlane. Refer to the shot node's
          documentation for details on how cameras are used by shots and the Sequencer.
    
      - clipDuration : cd              (time)          [create,query,edit]
          Length of clip. This is used for the display of the clip indicator bar in the Sequencer.
    
      - clipOpacity : co               (float)         [create,query,edit]
          Opacity for the shot's clip, this value is assigned to the currentCamera's imagePlane. Refer to the shot node's
          documentation for details on how cameras are used by shots and the Sequencer.
    
      - clipSyncState : css            (bool)          [create,query,edit]
          The viewport synchronization status of the clip associated with this shot. Return values are, 0 = no clip associated
          with this shot 1 = clip is fully in sync with viewport, and frames are 1:1 with sequencer 2 = clip is partially in sync
          with viewport, movie may be scaled to match sequencer 3 = clip not in sync with viewport (i.e. could have
          scale/time/camera differences)
    
      - clipZeroOffset : czo           (time)          [create,query,edit]
          Specify which time of the clip corresponds to the beginning of the shot. This is used to properly align splitted clips.
    
      - copy : c                       (bool)          [create,query,edit]
          This flag is used to copy a shot to the clipboard. In query mode, this flag allows you to query what, if anything, has
          been copied into the shot clipboard.
    
      - createCustomAnim : cca         (bool)          [edit]
          Creates an animation layer and links the shot node's customAnim attr to the weight attr of the animation layer
    
      - currentCamera : cc             (unicode)       [create,query,edit]
          The camera associated with this shot. Refer to the shot node's documentation for details on how cameras are used by
          shots and the Sequencer.
    
      - customAnim : ca                (bool)          [query]
          Returns the name of the animation layer node linked to this shot node's customAnim attr
    
      - deleteCustomAnim : dca         (bool)          [edit]
          Disconnects the animation layer from this shot's customAnim attr and deletes the animation layer node
    
      - determineTrack : dt            (bool)          [query,edit]
          Determines an available track for the shot. Returns a new track number or the existing track number if the current track
          is available.
    
      - endTime : et                   (time)          [create,query,edit]
          The shot end time in the Maya timeline. Changing the startTime will extend the duration of a shot.
    
      - favorite : fav                 (bool)          [create,query,edit]
          Make the shot a favorite. This is a UI indicator only to streamline navigation in the Sequencer panel
    
      - flag1 : f1                     (bool)          [create,query,edit]
          User specified state flag 1/12 for this shot
    
      - flag10 : f10                   (bool)          [create,query,edit]
          User specified state flag 10/12 for this shot
    
      - flag11 : f11                   (bool)          [create,query,edit]
          User specified state flag 11/12 for this shot
    
      - flag12 : f12                   (bool)          [create,query,edit]
          User specified state flag 12/12 for this shot
    
      - flag2 : f2                     (bool)          [create,query,edit]
          User specified state flag 2/12 for this shot
    
      - flag3 : f3                     (bool)          [create,query,edit]
          User specified state flag 3/12 for this shot
    
      - flag4 : f4                     (bool)          [create,query,edit]
          User specified state flag 4/12 for this shot
    
      - flag5 : f5                     (bool)          [create,query,edit]
          User specified state flag 5/12 for this shot
    
      - flag6 : f6                     (bool)          [create,query,edit]
          User specified state flag 6/12 for this shot
    
      - flag7 : f7                     (bool)          [create,query,edit]
          User specified state flag 7/12 for this shot
    
      - flag8 : f8                     (bool)          [create,query,edit]
          User specified state flag 8/12 for this shot
    
      - flag9 : f9                     (bool)          [create,query,edit]
          User specified state flag 9/12 for this shot
    
      - hasCameraSet : hcs             (bool)          [create,query,edit]
          Returns true if the camera associated with this shot is a camera set.
    
      - hasStereoCamera : hsc          (bool)          [create,query,edit]
          Returns true if the camera associated with this shot is a stereo camera.
    
      - linkAudio : la                 (unicode)       [create,query,edit]
          Specify an audio clip to link to this shot. Any currently linked audio will be unlinked.
    
      - lock : lck                     (bool)          [create,query,edit]
          Lock a specific shot. This is different than locking an entire track, which is done via the shotTrack command
    
      - mute : m                       (bool)          [create,query,edit]
          Mute a specific shot. This is different than muting an entire track, which is done via the shotTrack command. Querying
          this attribute will return true if the shot is muted due to its own mute, its shot being muted, or its shot being
          unsoloed. See flag selfmuteto query only the shot's own state.
    
      - paste : p                      (bool)          [create,query,edit]
          This flag is used to paste a shot or shots from the clipboard to the sequence timeline. Shots are added to the clipboard
          using the c/copy flag.
    
      - pasteInstance : pi             (bool)          [create,query,edit]
          This flag is used to paste an instance of a shot or shots from the clipboard to the sequence timeline. Unlike the
          p/paste flag, which duplicates the camera and image plane from the original source shot, the pi/pasteInstance flag
          shares the camera and image plane from the source shot. The audio node is duplicated.
    
      - postHoldTime : pst             (time)          [create,query,edit]
          Specify the time length to append to the shot in the sequence timeline. This repeats the last frame of the shot, in
          sequence time, over the specified duration.
    
      - preHoldTime : prt              (time)          [create,query,edit]
          Specify the time length to prepend to the shot in the sequence timeline. This repeats the first frame of the shot, in
          sequence time, over the specified duration.
    
      - scale : s                      (float)         [create,query,edit]
          Specify an amount to scale the Maya frame range of the shot. This will affect the sequenceEndFrame, leaving the
          sequenceStartFrame unchanged.
    
      - selfmute : sm                  (bool)          [create,query,edit]
          Query if this individual shot's own mute state is set. This is different from the flag mute, which will return true if
          this shot is muted due to the track being muted or another track being soloed. Editing this flag will set this shot's
          own mute status (identical behavior as the flag mute).
    
      - sequenceDuration : sqd         (time)          [query,edit]
          Return the sequence duration of the shot, which will include the holds and scale. This flag can only be queried.
    
      - sequenceEndTime : set          (time)          [create,query,edit]
          The shot end in the sequence timeline. Changing the endTime of a shot will scale it in sequence time.
    
      - sequenceStartTime : sst        (time)          [create,query,edit]
          The shot start in the sequence timeline. Changing the startTime of a shot will shift it in sequence time.
    
      - shotName : sn                  (unicode)       [create,query,edit]
          Specify a user-defined name for this shot. This allows the assignment of names that are not valid as node names within
          Maya. Whenever the shotName attribute is defined its value is used in the UI.
    
      - sourceDuration : sd            (time)          [query,edit]
          Return the number of source frames in the shot. This flag can only be queried.
    
      - startTime : st                 (time)          [create,query,edit]
          The shot start time in the Maya timeline. Changing the startTime will extend the duration of a shot.
    
      - track : trk                    (int)           [query,edit]
          Specify the track in which this shot resides.
    
      - transitionInLength : til       (time)          [create,query,edit]
          Length of the transtion into the shot.
    
      - transitionInType : tit         (int)           [query,edit]
          Specify the the type of transition for the transition into the shot. 0 = Fade 1 = Dissolve
    
      - transitionOutLength : tol      (time)          [create,query,edit]
          Length of the transtion out of the shot.
    
      - transitionOutType : tot        (int)           [query,edit]
          Specify the the type of transition for the transition out of the shot. 0 = Fade 1 = Dissolve
    
      - unlinkAudio : ula              (bool)          [query,edit]
          COMMENT Unlinks any currently linked audio.                                Flag can have multiple arguments, passed
          either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.shot`
    """

    pass


def cluster(*args, **kwargs):
    """
    The cluster command creates a cluster or edits the membership of an existing cluster. The command returns the name of
    the cluster node upon creation of a new cluster. After creating a cluster, the cluster's weights can be modified using
    the percent command or the set editor window.
    
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
    
      - bindState : bs                 (bool)          [create]
          When turned on, this flag adds in a compensation to ensure the clustered objects preserve their spatial position when
          clustered. This is required to prevent the geometry from jumping at the time the cluster is created in situations when
          the cluster transforms at cluster time are not identity.
    
      - deformerTools : dt             (bool)          [query]
          Returns the name of the deformer tool objects (if any) as string string ...
    
      - envelope : en                  (float)         [create,query,edit]
          Set the envelope value for the deformer. Default is 1.0
    
      - exclusive : ex                 (unicode)       [create,query]
          Puts the deformation set in a deform partition.
    
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
    
      - name : n                       (unicode)       [create]
          Used to specify the name of the node being created.
    
      - parallel : par                 (bool)          [create,edit]
          Inserts the new deformer in a parallel chain to any existing deformers in the history of the object. A blendShape is
          inserted to blend the parallel results together. Works in create mode (and edit mode if the deformer has no geometry
          added yet).
    
      - prune : pr                     (bool)          [edit]
          Removes any points not being deformed by the deformer in its current configuration from the deformer set.
    
      - relative : rel                 (bool)          [create]
          Enable relative mode for the cluster. In relative mode, Only the transformations directly above the cluster are used by
          the cluster. Default is off.
    
      - remove : rm                    (bool)          [edit]
          Specifies that objects listed after the -g flag should be removed from this deformer.
    
      - resetGeometry : rg             (bool)          [edit]
          Reset the geometry matrices for the objects being deformed by the cluster. This flag is used to get rid of undesirable
          effects that happen if you scale an object that is deformed by a cluster.
    
      - split : sp                     (bool)          [create,edit]
          Branches off a new chain in the dependency graph instead of inserting/appending the deformer into/onto an existing
          chain. Works in create mode (and edit mode if the deformer has no geometry added yet).
    
      - weightedNode : wn              (unicode, unicode) [create,query,edit]
          Transform node in the DAG above the cluster to which all percents are applied. The second DAGobject specifies the
          descendent of the first DAGobject from where the transformation matrix is evaluated. Default is the cluster handle.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.cluster`
    """

    pass


def joint(*args, **kwargs):
    """
    The joint command is used to create, edit, and query, joints within Maya. (The standard edit(-e) and query(-q) flags are
    used for edit and query functions). If the object is not specified, the currently selected object (dag object) will be
    used. Multiple objects are allowed only for the edit mode. The same edit flags will be applied on all the joints
    selected, except for -p without -r (set joint position in the world space). An ik handle in the object list is
    equivalent to the list of joints the ik handle commands. When -ch/children is present, all the child joints of the
    specified joints, including the joints implied by possible ik handles, will also be included. In the creation mode, a
    new joint will be created as a child of a selected transform or starts a hierarchy by itself if no transform is
    selected. An ik handle will be treated as a transform in the creation mode. The default values of the arguments are:
    -degreeOfFreedom xyz -name Joint#-position 0 0 0 -absolute -dof xyz-scale 1.0 1.0 1.0 -scaleCompensate true -orientation
    0.0 0.0 0.0 -scaleOrientation 0.0 0.0 0.0 -limitX -360 360 -limitY -360 360 -limitZ -360 360 -angleX 0.0 -angleY 0.0
    -angleZ 0.0 -stiffnessX 0.0 -stiffnessY 0.0 -stiffnessZ 0.0 -limitSwitchX no -limitSwitchY no -limitSwitchZ no
    -rotationOrder xyz Those arguments can be specified in the creation mode, editied in the edit mode (-e), or queried in
    the query mode (-q).
    
    Flags:
      - absolute : a                   (bool)          [create,query,edit]
          The joint center position is in absolute world coordinates. (This is the default.)
    
      - angleX : ax                    (float)         [create,query,edit]
          Set the x-axis angle. When queried, this flag returns a float.
    
      - angleY : ay                    (float)         [create,query,edit]
          Set the y-axis angle. When queried, this flag returns a float.
    
      - angleZ : az                    (float)         [create,query,edit]
          Set the z-axis angle. When queried, this flag returns a float.
    
      - assumePreferredAngles : apa    (bool)          [edit]
          Meaningful only in the edit mode. It sets the joint angles to the corresponding preferred angles.
    
      - automaticLimits : al           (bool)          [create]
          Meaningful only in edit mode. It sets the joint to appropriate hinge joint with joint limits. It modifies the joint only
          if (a) it connects exactly to two joints (one parent, one child), (b) it does not lie on the line drawn between the two
          connected joints, and the plane it forms with the two connected joints is perpendicular to one of its rotation axes.
    
      - children : ch                  (bool)          [edit]
          It tells the command to apply all the edit options not only to the selected joints, but also to their descendent joints
          in the DAG.
    
      - component : co                 (bool)          [create,edit]
          Use with the -position switch to position the joint relative to its parent (like -relative) but to compute new positions
          for all children joints so their world coordinate positions do not change.
    
      - degreeOfFreedom : dof          (unicode)       [create,query,edit]
          Specifies the degrees of freedom for the IK. Valid strings consist of non-duplicate letters from x, y, and z. The
          letters in the string indicate what rotations are to be used by IK. The order a letter appear in the string does not
          matter. Examples are x, yz, xyz. When queried, this flag returns a string. Modifying dof will change the locking state
          of the corresponding rotation attributes. The rule is: if an rotation is turned into a dof, it will be unlocked if it is
          currently locked. When it is turned into a non-dof, it will be locked if it is not currently locked.
    
      - exists : ex                    (unicode)       [query]
          Does the named joint exist? When queried, this flag returns a boolean.
    
      - limitSwitchX : lsx             (bool)          [create,query,edit]
          Use the limit the x-axis rotation? When queried, this flag returns a boolean.
    
      - limitSwitchY : lsy             (bool)          [create,query,edit]
          Use the limit the y-axis rotation? When queried, this flag returns a boolean.
    
      - limitSwitchZ : lsz             (bool)          [create,query,edit]
          Use the Limit the z-axis rotation? When queried, this flag returns a boolean.
    
      - limitX : lx                    (float, float)  [create,query,edit]
          Set lower and upper limits on the x-axis of rotation.  Also turns on the joint limit. When queried, this flag returns 2
          floats.
    
      - limitY : ly                    (float, float)  [create,query,edit]
          Set lower and upper limits on the y-axis of rotation.  Also turns on the joint limit. When queried, this flag returns 2
          floats.
    
      - limitZ : lz                    (float, float)  [create,query,edit]
          Set lower and upper limits on the z-axis of rotation.  Also turns on the joint limit. When queried, this flag returns 2
          floats.
    
      - name : n                       (unicode)       [create,query,edit]
          Specifies the name of the joint. When queried, this flag returns a string.
    
      - orientJoint : oj               (unicode)       [edit]
          The argument can be one of the following strings: xyz, yzx, zxy, zyx, yxz, xzy, none. It modifies the joint orientation
          and scale orientation so that the axis indicated by the first letter in the argument will be aligned with the vector
          from this joint to its first child joint. For example, if the argument is xyz, the x-axis will point towards the child
          joint. The alignment of the remaining two joint orient axes are dependent on whether or not the
          -sao/-secondaryAxisOrient flag is used. If the -sao flag is used, see the documentation for that flag for how the
          remaining axes are aligned. In the absence of a user specification for the secondary axis orientation, the rotation axis
          indicated by the last letter in the argument will be aligned with the vector perpendicular to first axis and the vector
          from this joint to its parent joint. The remaining axis is aligned according the right hand rule. If the argument is
          none, the joint orientation will be set to zero and its effect to the hierarchy below will be offset by modifying the
          scale orientation. The flag will be ignored if: A. the joint has non-zero rotations when the argument is not none. B.
          the joint does not have child joint, or the distance to the child joint is zero when the argument is not none. C. either
          flag -o or -so is set.
    
      - orientation : o                (float, float, float) [create,query,edit]
          The joint orientation. When queried, this flag returns 3 floats.
    
      - position : p                   (float, float, float) [create,query,edit]
          Specifies the position of the center of the joint. This position may be relative to the joint's parent or in absolute
          world coordinates (see -r and -a below). When queried, this flag returns 3 floats.
    
      - radius : rad                   (float)         [create,query,edit]
          Specifies the joint radius.
    
      - relative : r                   (bool)          [create,query,edit]
          The joint center position is relative to the joint's parent.
    
      - rotationOrder : roo            (unicode)       [create,query,edit]
          The rotation order of the joint. The argument can be one of the following strings: xyz, yzx, zxy, zyx, yxz, xzy.
    
      - scale : s                      (float, float, float) [create,query,edit]
          Scale of the joint. When queried, this flag returns 3 floats.
    
      - scaleCompensate : sc           (bool)          [create,query,edit]
          It sets the scaleCompenstate attribute of the joint to the given argument. When this is true, the scale of the parent
          joint will be compensated before any rotation of this joint is applied, so that the bone to the joint is scaled but not
          the bones to its child joints. When queried, this flag returns an boolean.
    
      - scaleOrientation : so          (float, float, float) [create,query,edit]
          Set the orientation of the coordinate axes for scaling. When queried, this flag returns 3 floats.
    
      - secondaryAxisOrient : sao      (unicode)       [edit]
          The argument can be one of the following strings: xup, xdown, yup, ydown, zup, zdown, none. This flag is used in
          conjunction with the -oj/orientJoint flag. It specifies the scene axis that the second axis should align with. For
          example, a flag combination of -oj yzx -sao yupwould result in the y-axis pointing down the bone, the z-axis oriented
          with the scene's positive y-axis, and the x-axis oriented according to the right hand rule.
    
      - setPreferredAngles : spa       (bool)          [edit]
          Meaningful only in the edit mode. It sets the preferred angles to the current joint angles.
    
      - stiffnessX : stx               (float)         [create,query,edit]
          Set the stiffness (from 0 to 100.0) for x-axis. When queried, this flag returns a float.
    
      - stiffnessY : sty               (float)         [create,query,edit]
          Set the stiffness (from 0 to 100.0) for y-axis. When queried, this flag returns a float.
    
      - stiffnessZ : stz               (float)         [create,query,edit]
          Set the stiffness (from 0 to 100.0) for z-axis. When queried, this flag returns a float.
    
      - symmetry : sym                 (bool)          [create,edit]
          Create a symmetric joint from the current joint.
    
      - symmetryAxis : sa              (unicode)       [create,edit]
          This flag specifies the axis used to mirror symmetric joints. Any combination of x, y, z can be used. This option is
          only used when the symmetry flag is set to True.
    
      - zeroScaleOrient : zso          (bool)          [edit]
          It sets the scale orientation to zero and compensate the change by modifing the translation and joint orientation for
          joint or rotation for general transform of all its child transformations. The flag will be ignored if the flag -so is
          set.                  Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.joint`
    """

    pass


def tangentConstraint(*args, **kwargs):
    """
    Constrain an object's orientation based on the tangent of the target curve[s] at the closest point[s] to the object. A
    tangentConstraint takes as input one or more NURBS curves (the targets) and a DAG transform node (the object).  The
    tangentConstraint orients the constrained object such that the aimVector (in the object's local coordinate system)
    aligns in world space to combined tangent vector.  The upVector (again the the object's local coordinate system) is
    aligned in world space with the worldUpVector.  The combined tangent vector is a weighted average of the tangent vector
    for each target curve at the point closest to the constrained object.
    
    Maya Bug Fix:
      - when queried, angle offsets would be returned in radians, not current angle unit
    
    Modifications:
      - added new syntax for querying the weight of a target object, by passing the constraint first::
    
            aimConstraint( 'pCube1_aimConstraint1', q=1, weight ='pSphere1' )
            aimConstraint( 'pCube1_aimConstraint1', q=1, weight =['pSphere1', 'pCylinder1'] )
            aimConstraint( 'pCube1_aimConstraint1', q=1, weight =[] )
    
    Flags:
      - aimVector : aim                (float, float, float) [create,query,edit]
          Set the aim vector.  This is the vector in local coordinates that points at the target.  If not given at creation time,
          the default value of (1.0, 0.0, 0.0) is used.
    
      - layer : l                      (unicode)       [create,edit]
          Specify the name of the animation layer where the constraint should be added.
    
      - name : n                       (unicode)       [create,query,edit]
          Sets the name of the constraint node to the specified name.  Default name is constrainedObjectName_constraintType
    
      - remove : rm                    (bool)          [edit]
          removes the listed target(s) from the constraint.
    
      - targetList : tl                (bool)          [query]
          Return the list of target objects.
    
      - upVector : u                   (float, float, float) [create,query,edit]
          Set local up vector.  This is the vector in local coordinates that aligns with the world up vector.  If not given at
          creation time, the default value of (0.0, 1.0, 0.0) is used.
    
      - weight : w                     (float)         [create,query,edit]
          Sets the weight value for the specified target(s). If not given at creation time, the default value of 1.0 is used.
    
      - weightAliasList : wal          (bool)          [query]
          Returns the names of the attributes that control the weight of the target objects. Aliases are returned in the same
          order as the targets are returned by the targetList flag
    
      - worldUpObject : wuo            (PyNode)        [create,query,edit]
          Set the DAG object use for worldUpType objectand objectrotation. See worldUpType for greater detail. The default value
          is no up object, which is interpreted as world space.
    
      - worldUpType : wut              (unicode)       [create,query,edit]
          Set the type of the world up vector computation. The worldUpType can have one of 5 values: scene, object,
          objectrotation, vector, or none. If the value is scene, the upVector is aligned with the up axis of the scene and
          worldUpVector and worldUpObject are ignored. If the value is object, the upVector is aimed as closely as possible to the
          origin of the space of the worldUpObject and the worldUpVector is ignored. If the value is objectrotationthen the
          worldUpVector is interpreted as being in the coordinate space of the worldUpObject, transformed into world space and the
          upVector is aligned as closely as possible to the result. If the value is vector, the upVector is aligned with
          worldUpVector as closely as possible and worldUpMatrix is ignored. Finally, if the value is noneno twist calculation is
          performed by the constraint, with the resulting upVectororientation based previous orientation of the constrained
          object, and the great circlerotation needed to align the aim vector with its constraint. The default worldUpType is
          vector.
    
      - worldUpVector : wu             (float, float, float) [create,query,edit]
          Set world up vector.  This is the vector in world coordinates that up vector should align with. See -wut/worldUpType
          (below)for greater detail. If not given at creation time, the default value of (0.0, 1.0, 0.0) is used.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.tangentConstraint`
    """

    pass



contstraintCmdName = 'tangentConstraint'


