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


class MAnimUtil(object):
    """
    Static class providing common animation helper methods.
    """
    
    
    
    def isAnimated(*args, **kwargs):
        """
        Return true if the target is animated.
        """
    
        pass


class MAnimCurveChange(object):
    """
    Anim curve change cache.
    """
    
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def redoIt(*args, **kwargs):
        """
        Redo all of the Anim Curve changes in this cache.
        """
    
        pass
    
    
    def undoIt(*args, **kwargs):
        """
        Undo all of the Anim Curve changes in this cache.
        """
    
        pass
    
    
    __new__ = None


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


class MAnimCurveClipboard(object):
    """
    Provides control over the animation clipboard.
    
    __init__()
    Initializes a new, empty MAnimCurveClipboard object.
    """
    
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def clear(*args, **kwargs):
        """
        clear() -> self
        
        Clears the clipboard.
        """
    
        pass
    
    
    def clipboardItems(*args, **kwargs):
        """
        clipboardItems() -> MAnimCurveClipboardItemArray
        
        Returns the clipboard items.
        """
    
        pass
    
    
    def set(*args, **kwargs):
        """
        set( clipboard ) -> self
        set( items ) -> self
        set( items, startTime, endTime, startUnitlessInput, endUnitlessInput, strictValidation=True ) -> self
        
        Sets the content of the clipboard.
        'items' may be either an MAnimClipboardItemArray or a sequence of MAnimClipboardItems.
        """
    
        pass
    
    
    endTime = None
    
    endUnitlessInput = None
    
    isEmpty = None
    
    startTime = None
    
    startUnitlessInput = None
    
    __new__ = None
    
    
    theAPIClipboard = None


class MAnimCurveClipboardItem(object):
    """
    This class provides a wrapper for a clipboard item.
    
    __init__()
    Initializes a new, empty MAnimCurveClipboardItem object.
    """
    
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def animCurveType(*args, **kwargs):
        """
        animCurveType() -> MFnAnimCurve.AnimCurveType
        
        Returns the type of the item's anim curve.
        """
    
        pass
    
    
    def getAddressingInfo(*args, **kwargs):
        """
        getAddressingInfo() -> (unsigned int, unsigned int, unsigned int)
        
        Returns the addressing information for this clipboard item
        as (rowCount, childCount, attributeCount).
        """
    
        pass
    
    
    def setAddressingInfo(*args, **kwargs):
        """
        setAddressingInfo(rowCount, childCount, attributeCount) -> self
        
        Sets the addressing information for this clipboard item.
        """
    
        pass
    
    
    def setAnimCurve(*args, **kwargs):
        """
        setAnimCurve(object) -> self
        
        Sets the anim curve MObject.
        """
    
        pass
    
    
    def setNameInfo(*args, **kwargs):
        """
        setNameInfo(nodeName, fullName, leafName) -> self
        
        Sets the name information for this clipboard item.
        """
    
        pass
    
    
    animCurve = None
    
    fullAttributeName = None
    
    leafAttributeName = None
    
    nodeName = None
    
    __new__ = None


class MAnimControl(object):
    """
    Control over animation playback and values
    """
    
    
    
    def animationEndTime(*args, **kwargs):
        """
        animationEndTime() -> MTime
        
        Return an MTime specifying the last frame of the animation, as specified by the Maya user in the Range Slider UI.
        """
    
        pass
    
    
    def animationStartTime(*args, **kwargs):
        """
        animationStartTime() -> MTime
        
        Return an MTime specifying the first frame of the animation, as specified by the Maya user in the Range Slider UI.
        """
    
        pass
    
    
    def autoKeyMode(*args, **kwargs):
        """
        autoKeyMode() -> bool
        
        Return the autoKeyMode.
        """
    
        pass
    
    
    def currentTime(*args, **kwargs):
        """
        currentTime() -> MTime
        
        Return an MTime instance containing the current animation frame.
        """
    
        pass
    
    
    def globalInTangentType(*args, **kwargs):
        """
        globalInTangentType() -> int
        
        Return the current global in tangent type.
        """
    
        pass
    
    
    def globalOutTangentType(*args, **kwargs):
        """
        globalOutTangentType() -> int
        
        Return the current global out tangent type.
        """
    
        pass
    
    
    def isPlaying(*args, **kwargs):
        """
        isPlaying() -> bool
        
        Return a value indicating whether Maya is currently playing the animation
        """
    
        pass
    
    
    def isScrubbing(*args, **kwargs):
        """
        isScrubbing() -> bool
        
        Return a value indicating whether interactive scrubbing is occuring while Maya is not currently playing an animation.
        """
    
        pass
    
    
    def maxTime(*args, **kwargs):
        """
        maxTime() -> MTime
        
        Return an MTime specifying the last frame of the current playback time range.
        """
    
        pass
    
    
    def minTime(*args, **kwargs):
        """
        minTime() -> MTime
        
        Return an MTime specifying the first frame of the current playback time range.
        """
    
        pass
    
    
    def playBackward(*args, **kwargs):
        """
        playBackward() -> None
        
        Start playing the current animation backwards.
        """
    
        pass
    
    
    def playForward(*args, **kwargs):
        """
        playForward() -> None
        
        Start playing the current animation forwards.
        """
    
        pass
    
    
    def playbackBy(*args, **kwargs):
        """
        playbackBy() -> float
        
        Return a float specifying the increment between times viewed during the playing of the animation.
        """
    
        pass
    
    
    def playbackMode(*args, **kwargs):
        """
        playbackMode() -> int
        
        Return the playback mode currently in effect:
          MAnimControl.kPlaybackOnce         Play once then stop.
          MAnimControl.kPlaybackLoop         Play continuously.
          MAnimControl.kPlaybackOscillate    Play forwards, then backwards continuously.
        """
    
        pass
    
    
    def playbackSpeed(*args, **kwargs):
        """
        playbackSpeed() -> float
        
        Return the speed with with to play the animation.
        """
    
        pass
    
    
    def setAnimationEndTime(*args, **kwargs):
        """
        setAnimationEndTime(MTime) -> None
        
        Set the value of the last frame in the animation.
        """
    
        pass
    
    
    def setAnimationStartEndTime(*args, **kwargs):
        """
        setAnimationStartEndTime(MTime, MTime) -> None
        
        Set the values of the first and last frames in the animation.
        """
    
        pass
    
    
    def setAnimationStartTime(*args, **kwargs):
        """
        setAnimationStartTime(MTime) -> None
        
        Set the value of the first frame in the animation.
        """
    
        pass
    
    
    def setAutoKeyMode(*args, **kwargs):
        """
        setAutoKeyMode(bool) -> None
        
        Set the autoKeyMode.
        """
    
        pass
    
    
    def setCurrentTime(*args, **kwargs):
        """
        setMinTime(MTime) -> None
        
        Set the current animation frame.
        """
    
        pass
    
    
    def setGlobalInTangentType(*args, **kwargs):
        """
        setGlobalInTangentType(int) -> None
        
        Set the current global in tangent type
        """
    
        pass
    
    
    def setGlobalOutTangentType(*args, **kwargs):
        """
        setGlobalOutTangentType(int) -> None
        
        Set the current global out tangent type.
        """
    
        pass
    
    
    def setMaxTime(*args, **kwargs):
        """
        setMaxTime(MTime) -> None
        
        Set the value of the last frame of the current playback time range.
        """
    
        pass
    
    
    def setMinMaxTime(*args, **kwargs):
        """
        setMinMaxTime(MTime, MTime) -> None
        
        Set the values of the first and last frames of the playback time range.
        """
    
        pass
    
    
    def setMinTime(*args, **kwargs):
        """
        setMinTime(MTime) -> None
        
        Set the value of the first frame of the current playback time range.
        """
    
        pass
    
    
    def setPlaybackBy(*args, **kwargs):
        """
        setPlaybackBy(float) -> None
        
        Specify the increment between times viewed during the playing of the animation.
        """
    
        pass
    
    
    def setPlaybackMode(*args, **kwargs):
        """
        setPlaybackMode(int) -> None
        
        Set the current playback mode.
        """
    
        pass
    
    
    def setPlaybackSpeed(*args, **kwargs):
        """
        setPlaybackSpeed(float) -> None
        
        Set the desired speed factor at which the animation will play back.
        """
    
        pass
    
    
    def setViewMode(*args, **kwargs):
        """
        setViewMode(int) -> None
        
        Set the current viewing mode.
        Controls whether the animation is run in only the active view, or simultaneously in all views.
        """
    
        pass
    
    
    def setWeightedTangents(*args, **kwargs):
        """
        setWeightedTangents(bool) -> None
        
        Sets whether or not the tangents on the Anim Curve are weighted.
        """
    
        pass
    
    
    def stop(*args, **kwargs):
        """
        stop() -> None
        
        Stop playing the current animation.
        """
    
        pass
    
    
    def viewMode(*args, **kwargs):
        """
        viewMode() -> int
        
        Return the viewing mode currently in effect:
          MAnimControl.kPlaybackViewAll      Playback in all views.
          MAnimControl.kPlaybackViewActive   Playback in only the active view.
        """
    
        pass
    
    
    def weightedTangents(*args, **kwargs):
        """
        weightedTangents() -> bool
        
        Determine whether or not the tangents on the Anim Curve are weighted.
        """
    
        pass
    
    
    kPlaybackLoop = 1
    
    
    kPlaybackOnce = 0
    
    
    kPlaybackOscillate = 2
    
    
    kPlaybackViewActive = 1
    
    
    kPlaybackViewAll = 0


class MAnimCurveClipboardItemArray(object):
    """
    Array of MAnimCurveClipboardItem values.
    """
    
    
    
    def __add__(*args, **kwargs):
        """
        x.__add__(y) <==> x+y
        """
    
        pass
    
    
    def __contains__(*args, **kwargs):
        """
        x.__contains__(y) <==> y in x
        """
    
        pass
    
    
    def __delitem__(*args, **kwargs):
        """
        x.__delitem__(y) <==> del x[y]
        """
    
        pass
    
    
    def __delslice__(*args, **kwargs):
        """
        x.__delslice__(i, j) <==> del x[i:j]
        
        Use of negative indices is not supported.
        """
    
        pass
    
    
    def __getitem__(*args, **kwargs):
        """
        x.__getitem__(y) <==> x[y]
        """
    
        pass
    
    
    def __getslice__(*args, **kwargs):
        """
        x.__getslice__(i, j) <==> x[i:j]
        
        Use of negative indices is not supported.
        """
    
        pass
    
    
    def __iadd__(*args, **kwargs):
        """
        x.__iadd__(y) <==> x+=y
        """
    
        pass
    
    
    def __imul__(*args, **kwargs):
        """
        x.__imul__(y) <==> x*=y
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
    
    
    def __mul__(*args, **kwargs):
        """
        x.__mul__(n) <==> x*n
        """
    
        pass
    
    
    def __repr__(*args, **kwargs):
        """
        x.__repr__() <==> repr(x)
        """
    
        pass
    
    
    def __rmul__(*args, **kwargs):
        """
        x.__rmul__(n) <==> n*x
        """
    
        pass
    
    
    def __setitem__(*args, **kwargs):
        """
        x.__setitem__(i, y) <==> x[i]=y
        """
    
        pass
    
    
    def __setslice__(*args, **kwargs):
        """
        x.__setslice__(i, j, y) <==> x[i:j]=y
        
        Use  of negative indices is not supported.
        """
    
        pass
    
    
    def __str__(*args, **kwargs):
        """
        x.__str__() <==> str(x)
        """
    
        pass
    
    
    def append(*args, **kwargs):
        """
        Add a value to the end of the array.
        """
    
        pass
    
    
    def clear(*args, **kwargs):
        """
        Remove all elements from the array.
        """
    
        pass
    
    
    def copy(*args, **kwargs):
        """
        Replace the array contents with that of another or of a compatible Python sequence.
        """
    
        pass
    
    
    def insert(*args, **kwargs):
        """
        Insert a new value into the array at the given index.
        """
    
        pass
    
    
    def remove(*args, **kwargs):
        """
        Remove an element from the array.
        """
    
        pass
    
    
    def setLength(*args, **kwargs):
        """
        Grow or shrink the array to contain a specific number of elements.
        """
    
        pass
    
    
    sizeIncrement = None
    
    __new__ = None


class MAnimMessage(_MMessage):
    """
    Class used to register callbacks for anim related messages.
    """
    
    
    
    def addAnimCurveEditedCallback(*args, **kwargs):
        """
        addAnimCurveEditedCallback(function, clientData=None) -> id
        
        This method registers a callback that is called whenever an
        AnimCurve is edited.
        
         * function - callable which will be passed a MObjectArray object containing
           an array of AnimCurves which have been edited, and the clientData object
         * clientData - User defined data passed to the callback function
        
         * return: Identifier used for removing the callback.
        """
    
        pass
    
    
    def addAnimKeyframeEditCheckCallback(*args, **kwargs):
        """
        addAnimKeyframeEditCheckCallback(function, clientData=None) -> id
        
        This method registers a callback that is used by the setKeyframe command
        to allow a user to consider the set keyframe request and cancel it if
        needed. The callback method should return False to abort the keyframe
        setting.
        
         * function - callable which will be passed a MPlug indicating the
           plug being keyframed and the clientData object.
           Return False to abort the keyframe action, otherwise return True
         * clientData - User defined data passed to the callback function
        
         * return: Identifier used for removing the callback.
        """
    
        pass
    
    
    def addAnimKeyframeEditedCallback(*args, **kwargs):
        """
        addAnimKeyframeEditedCallback(function, clientData=None) -> id
        
        This method registers a callback that is called whenever an
        a group of keys are modified.  The callback is invoked once per
        atomic change to single or group of keyframes. For example, if
        a user selects a group 5 of keys and moves them 5 units in the value
        axis, then a single callback event will be invoked with a MObject
        for each of the 5 keyframes.  The MObjects can then be used in the
        MFnKeyframeDelta function set. Refer to MFnKeyframeDelta function set
        documentation for more info.
        
         * function - callable which will be passed a MObjectArray object containing
           an array of keyframes that were edited, and the clientData object
         * clientData - User defined data passed to the callback function
        
         * return: Identifier used for removing the callback.
        """
    
        pass
    
    
    def addDisableImplicitControlCallback(*args, **kwargs):
        """
        addDisableImplicitControlCallback(function, clientData=None) -> id
        
        This method registers a callback that is called from bakeResults
        command after baking operation is completed, if disableImplicitControl
        is enabled. One example usage of this callback is to create the anim curve
        that is used to drive Maya rigidbody's bakeSimulationIndex, which defines
        if the rigid body should take its input from anim curve or rigid body 
        simulation.
        
         * function - callable which will be passed a MPlugArray containing the baked plugs
           (they can be replaced but must have the same number of plugs), a MDGModifier used
           if bakeResults command is undone or redone and the clientData object.
         * clientData - User defined data passed to the callback function
        
         * return: Identifier used for removing the callback.
        """
    
        pass
    
    
    def addNodeAnimKeyframeEditedCallback(*args, **kwargs):
        """
        addNodeAnimKeyframeEditedCallback(animNode, function, clientData=None) -> id
        
        This method registers a callback that is called whenever an a
        group of keys are modified.  The callback is invoked once per
        atomic change to single or group of keyframes on the specified
        animation curve node. For example, if a user selects a group 5
        of keys and moves them 5 units in the value axis, then a single
        callback event will be invoked with a MObject for each of the 5
        keyframes.  The MObjects can then be used in the MFnKeyframeDelta
        function set. Refer to MFnKeyframeDelta function set documentation
        for more info.
        
         * animNode (MObject) - the param curve node you want to watch.
         * function - callable which will be passed a MObject indicating the
           edited animation node, a MObjectArray containing an array of keyframes
           that were edited and the clientData object.
         * clientData - User defined data passed to the callback function
        
         * return: Identifier used for removing the callback.
        """
    
        pass
    
    
    def addPostBakeResultsCallback(*args, **kwargs):
        """
        addPostBakeResultsCallback(function, clientData=None) -> id
        
        This method registers a callback that is called from bakeResults
        command after the simulation. If the plugArray is replaced, then
        the anim curves created from baking will be connected to the new
        plugs.
        
         * function - callable which will be passed a MPlugArray containing the baked
           plugs to which the resulting anim curves will be connected (they can be
           replaced but must have the same number of plugs),a MDGModifier used if
           bakeResults command is undone or redone and the clientData object.
         * clientData - User defined data passed to the callback function
        
         * return: Identifier used for removing the callback.
        """
    
        pass
    
    
    def addPreBakeResultsCallback(*args, **kwargs):
        """
        addPreBakeResultsCallback(function, clientData=None) -> id
        
        This method registers a callback that is called from bakeResults
        command before the simulation. One example usage is handle the runup to
        the first frame in a dynamic system. If plugArray is set to zero
        length in the callback, the baking will be aborted.
        
         * function - callable which will be passed a MPlugArray containing the plugs
           to be baked (they can be replaced but must have the same number of plugs)
           ,a MDGModifier used if bakeResults command is undone or redone and the
           clientData object.
         * clientData - User defined data passed to the callback function
        
         * return: Identifier used for removing the callback.
        """
    
        pass
    
    
    def flushAnimKeyframeEditedCallbacks(*args, **kwargs):
        """
        flushAnimKeyframeEditedCallbacks() -> None
        
        Animation keyframe edited callbacks are queued to only be issued on an
        idle event. There may be times when it is desired to issue the callback
        at a specific time. This method provides this functionality. It will
        flush all animation keyframe edited callbacks and force them to issue
        their callbacks with the data contained within.
        """
    
        pass


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


class MFnGeometryFilter(_MFnDependencyNode):
    """
    Function set for operating on geometryFilter nodes.
    geometryFilter is the abstract node type from which all
    deformer node types derive.
    
    __init__()
    Initializes a new, empty MFnGeometryFilter functionset.
    
    __init__(MObject)
    Initializes a new MFnGeometryFilter functionset and attaches it
    to a geometryFilter node.
    """
    
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def getInputGeometry(*args, **kwargs):
        """
        getInputGeometry() -> MObjectArray
        
        Returns the DAG nodes which provide input geometry to the deformer.
        These are found by traversing the graph to find upstream shape nodes.
        It is possible for there to be nodes in between the shape and the
        deformer so that the returned shape may have a different topology or
        tweaks then the input data to the deformer. If the actual input
        geometry data for the deformer is required, this information can be
        accessed by using MPlug::getValue() to query the inputGeometry
        attribute on the deformer.
        """
    
        pass
    
    
    def getOutputGeometry(*args, **kwargs):
        """
        getOutputGeometry() -> MObjectArray
        
        Returns the DAG nodes which receive output geometry from the deformer.
        """
    
        pass
    
    
    def getPathAtIndex(*args, **kwargs):
        """
        getPathAtIndex(plugIndex) -> MDagPath
        
        Returns the DAG path of the specified output geometry.
        
        * plugIndex (unsigned int) - Plug index of the desired geometry.
        """
    
        pass
    
    
    def groupIdAtIndex(*args, **kwargs):
        """
        groupIdAtIndex(plugIndex) -> long
        
        Returns the groupId associated with the specified geometry.
        
        * plugIndex (unsigned int) - Plug index of the desired geometry.
        """
    
        pass
    
    
    def indexForGroupId(*args, **kwargs):
        """
        indexForGroupId(groupId) -> plugIndex
        
        Returns the plug index of the geometry associated with the specified groupId.
        
        * groupId (unsigned int) - groupId of the desired geometry.
        """
    
        pass
    
    
    def indexForOutputConnection(*args, **kwargs):
        """
        indexForOutputConnection(connIndex) -> plugIndex
        
        Returns the plug index corresponding to a connection index. The
        connection index is the contiguous (physical) index of the output
        connection, ranging from 0 to numOutputConnections()-1. The plug
        index is the sparse (logical) index of the connection.
        
        * connIndex (unsigned int) - Connection index of the desired geometry.
        """
    
        pass
    
    
    def indexForOutputShape(*args, **kwargs):
        """
        indexForOutputShape(shape) -> plugIndex
        
        Returns the plug index for the specified output shape.
        
        * shape (MObject) - Shape for which the plug index is requested.
        """
    
        pass
    
    
    def inputShapeAtIndex(*args, **kwargs):
        """
        inputShapeAtIndex(plugIndex) -> MObject
        
        Returns the input shape corresponding to the plug index.
        
        * plugIndex (unsigned int) - Plug index of the desired shape.
        """
    
        pass
    
    
    def numOutputConnections(*args, **kwargs):
        """
        numOutputConnections() -> long
        
        Returns the number of output geometries connected to this node. This
        is typically equal to the number of input geometries unless an input
        or output geometry has been deleted, or a connection to an input or
        output geometry has been broken.
        
        This method is useful in conjunction with indexForOutputConnection()
        to iterate through the affected objects.
        """
    
        pass
    
    
    def outputShapeAtIndex(*args, **kwargs):
        """
        outputShapeAtIndex(index) -> MObject
        
        Returns the DAG path to which this function set is attached, or the first path to the node if the function set is attached to an MObject.
        """
    
        pass
    
    
    deformerSet = None
    
    envelope = None
    
    __new__ = None


class MFnAnimCurve(_MFnDependencyNode):
    """
    Function set for operations on anim curves.
    
    __init__()
    Initializes a new, empty MFnAnimCurve object.
    
    __init__(MObject object)
    Initializes a new MFnAnimCurve and attaches it
    to an animCurve object.
    
    __init__(MPlug plug)
    Initializes a new MFnAnimCurve and attaches it
    to the single animCurve node connected to the given MPlug.
    """
    
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def addKey(*args, **kwargs):
        """
        addKey(at, value, tangentInType=kTangentGlobal, tangentOutType=kTangentGlobal, change=None) -> unsigned int
        
        Adds a new key with the given value at the specified time.
        at and value can both be either MTime or double,depending on what is appropriate for the animCurve type.
        change is an optional MAnimCurveChange.
        """
    
        pass
    
    
    def addKeys(*args, **kwargs):
        """
        addKeys(times, values, tangentInType=kTangentGlobal, tangentOutType=kTangentGlobal, keepExistingKeys=False, change=None) -> self
        
        Add a set of new keys with the given corresponding values and tangent typesat the specified times.  This method only works for animCurves of typekAnimCurveTA, kAnimCurveTL and kAnimCurveTU.
        """
    
        pass
    
    
    def create(*args, **kwargs):
        """
        create(node, attribute, animCurveType=kAnimCurveUnknown [, modifier] ) -> MObject
        create(plug, animCurveType=kAnimCurveUnknown [, modifier] ) -> MObject
        create(animCurveType [, modifier] ) -> MObject
        
        Creates a new animCurve node.
        If node and attribute (MObject) are supplied, the animCurvewill be connected to the given attribute on the given node.
        If plug (MPlug) is supplied, the animCurvewill be connected to the given plug.
        modifier is an optional MDGModifier which can be used to later undo the operation.
        animCurveType specifies the type of animCurve to create. Valid values are:
        kAnimCurveTA            Time to Angular
        kAnimCurveTL            Time to Linear
        kAnimCurveTT            Time to Time
        kAnimCurveTU            Time to Unitless
        kAnimCurveUA            Unitless to Angular
        kAnimCurveUL            Unitless to Linear
        kAnimCurveUT            Unitless to Time
        kAnimCurveUU            Unitless to Unitless
        kAnimCurveUnknown       Unknown type
        """
    
        pass
    
    
    def evaluate(*args, **kwargs):
        """
        evaluate(at) -> value
        
        Evalutes the curve.
        For curves of type kAnimCurveTA, kAnimCurveTL and kAnimCurveTU,the at parameter is an MTime, otherwise it is a double.
        For curves of type kAnimCurveTT and kAnimCurveUT,the value is an MTime, otherwise it is a double.
        """
    
        pass
    
    
    def find(*args, **kwargs):
        """
        find(at) -> unsigned int
        
        Determines the index of the key which is set at the specifiedMTime (time-input curves) or double (unitless-input curves).
        Returns None if the key is not found.
        """
    
        pass
    
    
    def findClosest(*args, **kwargs):
        """
        findClosest(at) -> unsigned int
        
        Determines the index of the key which is set at theMTime (time-input curves) or double (unitless-input curves)closest to the specified time.
        """
    
        pass
    
    
    def getTangentAngleWeight(*args, **kwargs):
        """
        getTangentAngleWeight(index, isInTangent) -> (MAngle,double)
        
        Determines the angle and weight of the in- or out-tangent to the curvefor the key at the specified index
        """
    
        pass
    
    
    def getTangentXY(*args, **kwargs):
        """
        getTangentXY(index, isInTangent) -> (x,y)
        
        Determines the x,y value representing the vector of the in- orout-tangent (depending on the value of the isInTangent parameter) tothe curve for the key at the specified index.  The values returnedwill be in Maya's internal units (seconds for time, centimeters forlinear, radians for angles).
        """
    
        pass
    
    
    def inTangentType(*args, **kwargs):
        """
        inTangentType(index) -> TangentType
        
        Determines the type of the tangent to the curve entering the current key.
        """
    
        pass
    
    
    def input(*args, **kwargs):
        """
        input(index) -> MTime or double
        
        Determines the input (MTime for T* curves or double for U* curves) of the key at the specified index.
        """
    
        pass
    
    
    def isBreakdown(*args, **kwargs):
        """
        isBreakdown(index) -> bool
        
        Determines whether or not a key is a breakdown.
        """
    
        pass
    
    
    def outTangentType(*args, **kwargs):
        """
        outTangentType(index) -> TangentType
        
        Determines the type of the tangent to the curve leaving the current key.
        """
    
        pass
    
    
    def remove(*args, **kwargs):
        """
        remove(index, change=None) -> self
        
        Removes the key at the specified index.
        change is an optional MAnimCurveChange.
        """
    
        pass
    
    
    def setAngle(*args, **kwargs):
        """
        setAngle(index, setAngle, isInTangent, change=None) -> self
        
        Sets the in- or out-angle of the tangent for the key at the given index.
        isInTangent is True to modify the inTangent or False to modify the outTangent.
        """
    
        pass
    
    
    def setInTangentType(*args, **kwargs):
        """
        setInTangentType(index, tangentType, change=None) -> self
        
        Sets the type of the tangent to the curve entering the key at thespecified index.
        Valid values for tangentType are:
        kTangentGlobal          Global
        kTangentFixed           Fixed
        kTangentLinear          Linear
        kTangentFlat            Flag
        kTangentSmooth          Smooth
        kTangentStep            Step
        kTangentSlow            OBSOLETE kTangentSlow should not be used. Using this tangent type may produce unwanted and unexpected results.
        kTangentFast            OBSOLETE kTangentFast should not be used. Using this tangent type may produce unwanted and unexpected results.
        kTangentClamped Clamped
        kTangentPlateau Plateau
        kTangentStepNext        StepNext
        kTangentAuto            Auto
        """
    
        pass
    
    
    def setInput(*args, **kwargs):
        """
        setInput(index, at, change=None) -> self
        
        Sets the input (MTime for T* curves or double for U* curves) of the key at the specified index.  This will fail ifsetting the input would require re-ordering of the keys.
        """
    
        pass
    
    
    def setIsBreakdown(*args, **kwargs):
        """
        setIsBreakdown(index, isBreakdown, change=None) -> self
        
        Sets the breakdown state of a key at a given index.
        """
    
        pass
    
    
    def setIsWeighted(*args, **kwargs):
        """
        setIsWeighted(isWeighted, change=None) -> self
        
        Sets whether or not the curve has weighted tangents.
        """
    
        pass
    
    
    def setOutTangentType(*args, **kwargs):
        """
        setOutTangentType(index, tangentType, change=None) -> self
        
        Sets the type of the tangent to the curve leaving the key at thespecified index.
        """
    
        pass
    
    
    def setPostInfinityType(*args, **kwargs):
        """
        setPostInfinityType(infinityType, change=None) -> self
        
        Sets the behaviour of the curve for the range occurring after the last key.
        """
    
        pass
    
    
    def setPreInfinityType(*args, **kwargs):
        """
        setPreInfinityType(infinityType, change=None) -> self
        
        Sets the behaviour of the curve for the range occurring before the first key.
        Valid values for infinityType are:
        kConstant                       Constant
        kLinear                 Linear
        kCycle                          Cycle
        kCycleRelative          Cycle relative
        kOscillate                      Oscillate
        """
    
        pass
    
    
    def setTangent(*args, **kwargs):
        """
        setTangent(index, xOrAngle, yOrWeight, isInTangent, change=None, convertUnits=True) -> self
        
        Sets the tangent for the key at the specified index.
        The tangent can be specified as an x/y pair, oras an MAngle and a weight.
        isInTangent is True to modify the inTangent or False to modify the outTangent.
        """
    
        pass
    
    
    def setTangentTypes(*args, **kwargs):
        """
        setTangentTypes(indexArray, tangentInType=kTangentGlobal, tangentOutType=kTangentGlobal, change=None) -> self
        
        Sets the tangent types for multiple keys.
        """
    
        pass
    
    
    def setTangentsLocked(*args, **kwargs):
        """
        setTangentsLocked(index, locked, change=None) -> self
        
        Lock or unlock the tangents at the given key.
        """
    
        pass
    
    
    def setValue(*args, **kwargs):
        """
        setValue(index, value, change=None) -> self
        
        Sets the value of the key at the specified index.  This methodshould only be used on Anim Curves of type kAnimCurve*A, kAnimCurve*Lor kAnimCurve*U.
        """
    
        pass
    
    
    def setWeight(*args, **kwargs):
        """
        setWeight(index, weight, isInTangent, change=None) -> self
        
        Sets the in- or out-weight of the tangent for the key at the given index.
        isInTangent is True to modify the inTangent or False to modify the outTangent.
        """
    
        pass
    
    
    def setWeightsLocked(*args, **kwargs):
        """
        setWeightsLocked(index, locked, change=None) -> self
        
        Lock or unlock the weights at the given key.
        """
    
        pass
    
    
    def tangentsLocked(*args, **kwargs):
        """
        tangentsLocked(index) -> bool
        
        Determines whether the tangents are locked at the given key.
        """
    
        pass
    
    
    def timedAnimCurveTypeForPlug(*args, **kwargs):
        """
        timedAnimCurveTypeForPlug(plug) -> AnimCurveType
        
        Returns the timed animCurve type appropriate for the specified plug.
        """
    
        pass
    
    
    def unitlessAnimCurveTypeForPlug(*args, **kwargs):
        """
        unitlessAnimCurveTypeForPlug(plug) -> AnimCurveType
        
        Returns the unitless animCurve type appropriate for the specified plug.
        """
    
        pass
    
    
    def value(*args, **kwargs):
        """
        value(index) -> double
        
        Determines the value of the key at the specified index.  This methodshould only be used on Anim Curves of type kAnimCurve*A, kAnimCurve*Lor kAnimCurve*U.
        """
    
        pass
    
    
    def weightsLocked(*args, **kwargs):
        """
        weightsLocked(index) -> bool
        
        Determines whether the weights are locked at the given key.
        """
    
        pass
    
    
    animCurveType = None
    
    isStatic = None
    
    isTimeInput = None
    
    isUnitlessInput = None
    
    isWeighted = None
    
    numKeys = None
    
    postInfinityType = None
    
    preInfinityType = None
    
    __new__ = None
    
    
    kAnimCurveTA = 0
    
    
    kAnimCurveTL = 1
    
    
    kAnimCurveTT = 2
    
    
    kAnimCurveTU = 3
    
    
    kAnimCurveUA = 4
    
    
    kAnimCurveUL = 5
    
    
    kAnimCurveUT = 6
    
    
    kAnimCurveUU = 7
    
    
    kAnimCurveUnknown = 8
    
    
    kConstant = 0
    
    
    kCycle = 3
    
    
    kCycleRelative = 4
    
    
    kLinear = 1
    
    
    kOscillate = 5
    
    
    kTangentAuto = 11
    
    
    kTangentClamped = 8
    
    
    kTangentCustomEnd = 32767
    
    
    kTangentCustomStart = 64
    
    
    kTangentFast = 7
    
    
    kTangentFixed = 1
    
    
    kTangentFlat = 3
    
    
    kTangentGlobal = 0
    
    
    kTangentLinear = 2
    
    
    kTangentPlateau = 9
    
    
    kTangentShared1 = 19
    
    
    kTangentShared2 = 20
    
    
    kTangentShared3 = 21
    
    
    kTangentShared4 = 22
    
    
    kTangentShared5 = 23
    
    
    kTangentShared6 = 24
    
    
    kTangentShared7 = 25
    
    
    kTangentShared8 = 26
    
    
    kTangentSlow = 6
    
    
    kTangentSmooth = 4
    
    
    kTangentStep = 5
    
    
    kTangentStepNext = 10
    
    
    kTangentTypeCount = 32768


class MFnSkinCluster(MFnGeometryFilter):
    """
    Function set for operating on skinCluster nodes.
    SkinCluster nodes are created during a smooth bindSkin. They
    store a weight per influence object for each component of the
    geometry that is deformed. Influence objects can be joints or
    any transform.
    
    Unlike most deformers, a skinCluster node can deform only a
    single geometry. Therefore, if additional geometries are added
    to the skinCluster set, they will be ignored.
    
    __init__()
    Initializes a new, empty MFnSkinCluster functionset.
    
    __init__(MObject)
    Initializes a new MFnSkinCluster functionset and attaches it to
    a skinCluster node.
    """
    
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def getBlendWeights(*args, **kwargs):
        """
        getBlendWeights(shape, components) -> MDoubleArray
        
        Returns blend weights for the specified components of the deformed
        shape. Blend weights are used to determine the blending between
        classical linear skinning and dual quaternion bases skinning on a
        per vertex basis. The returned array contains one weight per component
        in the order given by 'components'.
        
        * shape     (MDagPath) - the object being deformed by the skinCluster
        * components (MObject) - components for which weights should be returned
        """
    
        pass
    
    
    def getPointsAffectedByInfluence(*args, **kwargs):
        """
        getPointsAffectedByInfluence(influence) -> (MSelectionList, MDoubleArray)
        
        During deformation, the skinCluster algorithm is applied for a given
        influence object on all points in the deformer's set whose weights
        are non-zero. This returns the non-zero weights for a particular
        influence object.
        
        The return value is a tuple consisting of a selection list, which
        contains the dag path and components that are affected by the
        specified influence object, and the corresponding weights for the
        components. If no components are weighted for a specified influence
        the selection list will be empty.
        
        * influence (MDagPath) - the influence object of interest
        """
    
        pass
    
    
    def getWeights(*args, **kwargs):
        """
        getWeights(shape, components) -> (MDoubleArray, int)
        getWeights(shape, components, influence) -> MDoubleArray
        getWeights(shape, components, influences) -> MDoubleArray
        
        Returns the skinCluster weights of the given influence objects on
        the specified components of the deformed shape.
        
        
        If no influence index is provided then a tuple containing the weights
        and the number of influence objects will be returned.
        
        If a single influence index is provided the an array of weights will
        be returned, one per component in the same order as in 'components'.
        
        If an array of influence indices is provided an array of weights will
        be returned containing as many weights for each component as there
        are influences in the 'influenceIndices' array. The weights will be
        in component order: i.e. all of the weight values for the first
        component, followed by all the weight values for the second component,
        and so on.
        
        * shape       (MDagPath) - the object being deformed by the skinCluster
        * components   (MObject) - components to return weights for
        * influence        (int) - index of the single influence to return weights for
        * influences (MIntArray) - indices of multiple influences to return weights for
        """
    
        pass
    
    
    def indexForInfluenceObject(*args, **kwargs):
        """
        indexForInfluenceObject(influenceObj) -> long
        
        Returns the logical index of the matrix array attribute where the
        specified influence object is attached.
        
        * influenceObj (MObject) - influence object for which the index is requested.
        """
    
        pass
    
    
    def influenceObjects(*args, **kwargs):
        """
        influenceObjects() -> MDagPathArray
        
        Returns an array of paths to the influence objects for the skinCluster.
        """
    
        pass
    
    
    def setBlendWeights(*args, **kwargs):
        """
        setBlendWeights(shape, components, weights) -> self
        
        Sets blend weights for the specified components of the shape being
        deformed by the skinCluster. Blend weights are used to determine the
        blending between classical linear skinning and dual quaternion bases
        skinning on a per vertex basis.
        
        * shape       (MDagPath) - object being deformed by the skinCluster
        * components   (MObject) - components of 'shape' to set blend weights for
        * weights (MDoubleArray) - weights to set, one per component. If the
                                   length of this array does match the number
                                   of components provided then the lesser of
                                   the two will be used.
        """
    
        pass
    
    
    def setWeights(*args, **kwargs):
        """
        setWeights(shape, components, influence, weight, normalize=True, returnOldWeights=False) -> None or MDoubleArray
        setWeights(shape, components, influences, weights, normalize=True, returnOldWeights=False) -> None or MDoubleArray
        
        Sets the skinCluster weights for one or more influence objects on
        the specified components of the given shape. If 'returnOldWeights'
        is True then the old weights will be returned, otherwise None will
        be returned
        
        If only a single influence index and weight are specified then that
        weight is applied to all of the specified components. The returned
        array of old weights, if requested, will contain weights for ALL of
        the skinCluster's influence objects, not just the one specified by
        the 'influence' parameter.
        
        If arrays of influence indices and weights are provided then the
        behaviour depends upon the number of elements in the 'weights' array.
        If it's equal to the number of influences specified then each weight
        will be used for all of components for the corresponding influence
        object. If it's equal to the number of influences times the number of
        components provided, then a separate weight will be used for each
        component, with all of the weights for the first component coming
        first in the 'weights' array, followed by all of the weights for the
        second component, and so on. Within each component the weights will
        will correspond with the ordering of influence indices in the
        'influences' array. The returned old weights, if requested, will
        consist of a separate weight for
        
        The returned old weights will be ordered by influence within
        component, i.e. all of the influence weights for the first component
        will come first in the array, followed by all the weights for the
        second component, and so on.
        
        * shape       (MDagPath) - object being deformed by the skinCluster
        * components   (MObject) - the components to set weights on
        * influence        (int) - physical index of a single influence object
        * weight         (float) - single weight to be applied to all components.
        * influences (MIntArray) - physical indices of several influence objects.
        * weights (MDoubleArray) - weights to be used with several influence objects.
        * normalize       (bool) - if True, normalize weights on other influence objects
        * returnOldWeights(bool) - if True, return the old weights, otherwise return None
        """
    
        pass
    
    
    __new__ = None



