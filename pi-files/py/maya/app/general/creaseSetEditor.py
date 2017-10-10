from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import *

class MayaSkipUndoChunk:
    """
    Safe way to using the 'with' command to create a block of commands that are not added to the undo queue.
    It will close the chunk automatically on exit from the block and
    restore the existing undo state.
    
    :Example:
        cmds.polyCube()
        with MayaSkipUndoChunk():
            cmds.polyCube()
            cmds.polyCube()
        cmds.polyCube()
    """
    
    
    
    def __enter__(self):
        pass
    
    
    def __exit__(self, type, value, traceback):
        pass


class PushValueOntoStack:
    """
    Safe way to push/pop of items onto a list (stack) using the "with" command
    It will push the value onto the list on entering the block and
    remove it on exit from the block.
    
    :Example:
        disableActionStack = []
        print disableActionStack
        with PushValueOntoStack(disableActionStack, 'outerLoop'):
            print disableActionStack
            with PushValueOntoStack(disableActionStack, 'innerLoop'):
                print disableActionStack
            print disableActionStack
        print disableActionStack
    """
    
    
    
    def __enter__(self):
        pass
    
    
    def __exit__(self, type, value, traceback):
        pass
    
    
    def __init__(self, stackItem, value):
        pass


class CreaseSetEditor(QWidget):
    """
    CreaseSetEditor widget
    
    :Contains:
        * row of buttons at the top for actions
        * the main column/tree view widget with popup menu for managing/selecting the creaseSets
    """
    
    
    
    def __init__(self, parent=None, name=None, title=None):
        """
        Init for the CreaseSetEditor
        Initializes its child widgets and sets up the button actions.
        
        :Parameters:
            parent (QWidget)
                parent Qt widget for this object.  Passed into the QWidget init function
            name (string)
                the objectName for this widget instance
            title (string)
                the windowTitle for this widget instance.  Defaults to 'CreaseSetEditor'.
        """
    
        pass
    
    
    def closeEvent(self, evt):
        pass
    
    
    staticMetaObject = None


_DefaultCreaseSetEditor = CreaseSetEditor
class CreaseSetTreeWidgetItem(QTreeWidgetItem):
    """
    QTreeWidgetItem tailored for the CreaseSetTreeWidget
    """
    
    
    
    def __init__(self, *args, **kwargs):
        pass
    
    
    def __lt__(self, other):
        """
        Properly handle numeric sorting for the columns that have numeric values
        """
    
        pass
    
    
    NUMERIC_COLUMNS = set()


class CreaseSetTreeWidget(QTreeWidget):
    """
    Derives off of standard QTreeWidget. The QTreeWidget embeds the data for
    the tree inside the class. If wanting a "view" widget that accesses data
    external to the widget, then use QTreeView.
    """
    
    
    
    def __init__(self, parent=None, name=None):
        """
        Init for the CreaseSetTreeWidget
        
        :Parameters:
            parent (QWidget)
                parent Qt widget for this object.  Passed into the QtTreeWidget init function
            name (string)
                the objectName and windowTitle for this widget instance
        """
    
        pass
    
    
    def addMembersCB(self):
        """
        Add selected Maya edge and vertex components to the highlighed tree item
        """
    
        pass
    
    
    def addPerNodeMayaCallbacks(self, nodeObj):
        """
        Add the Maya per-node callbacks for the specified item
        and register them with the widget (so they can be cleaned up).
        
        :Parameters:
            nodeObj (MObject)
                MObject depend node to add per-node callbacks to
        
        :Return: None
        """
    
        pass
    
    
    def bakeOutCreaseSetValuesCB(self):
        """
        Bake out the CreaseSet values from the selected meshes directly onto
        the meshes and remove the components from the CreaseSet.
        """
    
        pass
    
    
    def beforeSceneUpdatedCB(self, clientData):
        """
        Freeze the callbacks before the entire scene is being reloaded or cleared.
        Unfreezing the callbacks is handled in the sceneUpdatedCB below.
        
        :Parameters:
            clientData
                container of the Maya client data for the event
        
        :Return: None
        """
    
        pass
    
    
    def calcCreaseValueColorSetCB(self):
        """
        Calculate a color-per-vertex colorSet representation for crease values
        on the selected meshes.
        """
    
        pass
    
    
    def cleanup(self):
        """
        Cleanup environment by removing the Maya callbacks, etc.
        """
    
        pass
    
    
    def commitData(self, *args):
        """
        Override the virtual function commitData() to retrieve the old and
        new values, revert the item value to its original value, then pass them
        along to commitDataCB().
        
        The commitDataCB() will update the Maya scene,
        that will then in turn update the widget. Therefore updating the item
        data directly is not desired, but retrieving the values are necessary. 
        
        :Dataflow:
            Maya Scene -> QCreaseSetTree (data)
            QCreaseSetTree (uncomitted edited values) -> Maya Scene
        
        :Note:
            Using commitData() is better than connecting a function to
            itemChanged signal as it will be triggered whenever an
            item value changes, not just when an editor changes the value
            by the user.  We can also get the old and new values
        """
    
        pass
    
    
    def commitDataCB(self, item, column, oldValue, newValue):
        """
        Update Maya scene with the new values.  It is called by the commitData()
        function above when column data is edited from the UI.
        
        :Parameters:
            item (QtTreeWidgetItem)
                the QtTreeWidgetItem acted upon
            column (int)
                the column index where the double-click action occurred
            oldValue
                original value of the attribute or name.
            newValue
                new value of the attribute or name
        """
    
        pass
    
    
    def contextMenuEvent(self, event):
        """
        Dynamically driven contextMenu for popup menu. Easily edited dict of labels and actions.
        """
    
        pass
    
    
    def deleteCreaseSetCB(self):
        """
        Delete the creaseSet(s) corresponding to the highlighted tree item(s)
        """
    
        pass
    
    
    def getCurrentSetNames(self):
        """
        Get the Maya nodenames for the widget's selected items
        """
    
        pass
    
    
    def getSelectedMeshes(self):
        """
        Get selected meshes. If there are no selected meshes then
        get the meshes associated with selected crease sets.
        """
    
        pass
    
    
    def hardenCreaseEdgesCB(self):
        """
        Set the cage hard/soft edge value for the selected meshes based on whether
        the edges are creased.  Creasing is assumed if creaseLevel > 0.
        """
    
        pass
    
    
    def hideCreaseValueColorSetCB(self):
        pass
    
    
    def hideEvent(self, *args):
        """
        When widget is hidden, remove the Maya callbacks and clean up.
        """
    
        pass
    
    
    def itemDoubleClickedCB(self, item, column):
        """
        Double-click behavior on a per-column basis.
        Used to edit values if double-clicked on the item's name or crease value.
        
        :Parameters:
            item (QtTreeWidgetItem)
                the QtTreeWidgetItem acted upon
            column (int)
                the column index where the double-click action occurred
        """
    
        pass
    
    
    def mayaSelectionChangedCB(self, clientData):
        """
        The selection has changed.  Update the background coloring of the items
        using the secondary highlight color (used by the Maya Outliner) to reflect member-set relationships.
        
        :Parameters:
            clientData
                container of the Maya client data for the event
        
        :Return: None
        """
    
        pass
    
    
    def mergeCreaseSetsCB(self):
        """
        Merge and combine two or more highlighted creaseSets into the last highlighted item.
        
        :Note: Order of highlighting the creaseSet items matters.  The last one selected is the target
        creaseSet.  This follows the same paradigm used in Maya parenting.
        """
    
        pass
    
    
    def minimumSizeHint(self):
        """
        The minimum size for the Qt window
        """
    
        pass
    
    
    def mouseMoveEvent(self, event):
        """
        Interactively adjust creaseLevel attr values when middle mouse button
        pressed and mouse moved.
        """
    
        pass
    
    
    def mousePressEvent(self, event):
        """
        Store off initial value of mouse for the middle-mouse button move event.
        """
    
        pass
    
    
    def mouseReleaseEvent(self, event):
        """
        Store off initial value of mouse for the mouse move event
        """
    
        pass
    
    
    def newCreaseSetCB(self):
        """
        Create a new creaseSet and populate it with the selected Maya edge and vertex components.
        """
    
        pass
    
    
    def objectSetAttrChangedCB(self, msg, plg, otherPlg, clientData):
        """
        Selectively update the widget tree for the specified item when
        the attributes of a creaseSet are modified
        
        :Parameters:
            msg (maya.OpenMaya.MNodeMessage)
                om.MNodeMessage enum for the action upon the attr.  Use '&' to check the value.
                Example use: msg&om.MNodeMessage.kAttributeSet
            plug (MPlug)
                MPlug for the attribute
            otherPlg (MPlug)
                MPlug for other connected attribute that may be contributing to this action
            clientData
                container of the Maya client data for the event
        
        :Return: None
        """
    
        pass
    
    
    def objectSetMembersChangedCB(self, nodeObj, clientData):
        """
        Selectively update the widget tree for the specified item when
        members are added/removed.  This updated column values for counts as well
        as updating the sub-items for the creaseSet.
        
        :Parameters:
            nodeObj (MObject)
                MObject depend node for the node added
            clientData
                container of the Maya client data for the event
        
        :Return: None
        """
    
        pass
    
    
    def objectSetNodeAddedCB(self, nodeObj, clientData):
        """
        Selectively update the widget tree for the specified item when a
        creaseSet is added to the Maya scene
        
        :Parameters:
            nodeObj (MObject)
                MObject depend node for the node added
            clientData
                container of the Maya client data for the event
        
        :Return: None
        """
    
        pass
    
    
    def objectSetNodeNameChangedCB(self, nodeObj, prevName, clientData):
        """
        Selectively update the widget items when a Maya CreaseSet node name changes
        
        :Parameters:
            nodeObj (MObject)
                MObject depend node for the node added
            prevName (string)
                previous name of the node
            clientData
                container of the Maya client data for the event
        
        :Return: None
        """
    
        pass
    
    
    def objectSetNodeRemovedCB(self, nodeObj, clientData):
        """
        Selectively update the widget tree for the specified item when
        a creaseSet is removed from the Maya scene
        
        :Parameters:
            nodeObj (MObject)
                MObject depend node for the node added
            clientData
                container of the Maya client data for the event
        
        :Return: None
        """
    
        pass
    
    
    def optimizeSubdLevelCB(self):
        """
        Set the subd smoothLevel attr to be +1 above the truncated max crease value.
        This is useful to see the most efficient representation of the creasing effects
        on the mesh.
        """
    
        pass
    
    
    def removeMembersCB(self):
        """
        Remove selected Maya edge and vertex components from the highlighed tree item
        """
    
        pass
    
    
    def removePerNodeMayaCallbacks(self, nodeObjs):
        """
        Remove per-node Maya callbacks.
        
        :Parameters:
            nodeObjs ([MObject])
                List of MObject dependency nodes on which to remove the Maya per-node callbacks
        """
    
        pass
    
    
    def repopulate(self):
        """
        Clear and populate the table with data retrieved from the Maya scene.
        Add Maya callbacks for creaseSet changes to trigger UI updates.
        """
    
        pass
    
    
    def requestUpdateHighlightedItems(self):
        """
        Request deferred update of the highlighted items to when Maya is idle.
        This improves performance when doing large operations like duplicating
        hundreds of objectSets.
        """
    
        pass
    
    
    def sceneUpdatedCB(self, clientData):
        """
        The entire scene is being reloaded or cleared. Repopulate the entire widget.
        
        :Parameters:
            clientData
                container of the Maya client data for the event
        
        :Return: None
        """
    
        pass
    
    
    def selectMembersCB(self):
        """
        Select the Maya creaseSet members for the highlighed tree item(s)
        If there are existing meshes or components selected, then select the intersection
        of the members in the creaseSet with the current selected items.
        """
    
        pass
    
    
    def selectSelectedSetNodesCB(self):
        """
        Select the CreaseSets in Maya that are highlighted in the CreaseSetEditor
        """
    
        pass
    
    
    def selectSetsWithSelectedMembersCB(self):
        """
        Select the CreaseSet tree items in the CreaseSetEditor that have members
        that are currently selected in Maya.
        """
    
        pass
    
    
    def setComponentColor(self, colorIndex):
        """
        Set the creaseSet component memberWireframeColor color colorIndex.
        
        :Parameters:
            colorIndex
                index value for the color (0-7).
                If set to -1, then color the override is disabled
        """
    
        pass
    
    
    def setCreaseLevelIncrementCB(self):
        """
        # ------------
        # Preferences
        # ------------
        """
    
        pass
    
    
    def setCurrentItemsFromSetNames(self, setNames):
        """
        Adjust the selection highlighting of the QtTreeWidgetItems based on the creaseSet
        node names passed in.
        
        :Parameters:
            setNames ([string])
                node names of the creaseSet nodes to highlight in the tree
        
        :Note: This "selection" is not the same as Maya's currentSelected items, but
        instead the selected items for the widget.
        """
    
        pass
    
    
    def setDefaultCreaseSetNameCB(self):
        pass
    
    
    def setItemValues(self, item=None, name=None, colorIndex=None, creaseLevel=None, members=None, numSelectedMembers=None, showSetMembers=False):
        """
        This helper function sets the column values for an item.
        It will set all values that are specified so can do partial or full setting of the item values.
        
        :Parameters:
            item (QTreeWidgetItem)
                QTreeWidgetItem to act upon.  If 'None', then create a new QTreeWidgetItem.
            name (string)
                new text for the 'Name Column'
            colorIndex (int)
                new colorIndex for the 'Color Column' swatch (range=0-7)
            creaseLevel (float)
                new creaseLevel for the 'CreaseLevel Column'
            members ([string])
                new list of members to add as sub-items to this tree item
            numSelectedMembers (int)
                number of members that are currently selected
            showSetMembers (bool)
                Add tree items under the CreaseSet item for each member in the CreasSet
                Disabled by default for performance reasons.
                (default=False) 
        
        :Return: QTreeWidgetItem created or acted upon (QTreeWidgetItem)
        """
    
        pass
    
    
    def showCreaseValueColorSetCB(self):
        pass
    
    
    def showEvent(self, *args):
        """
        Show the widget, add the callbacks, and repopulate the data.
        """
    
        pass
    
    
    def sizeHint(self):
        """
        The window sizeHint used by Qt
        """
    
        pass
    
    
    def splitCreaseSetCB(self):
        """
        Split the edges/vertices in selected meshes or components in CreaseSets into separate CreaseSets.
        """
    
        pass
    
    
    def subdivideBaseMeshCB(self):
        """
        Subdivide selected meshes by 1 level and decrement the creasing values to add resolution into the base mesh.
        """
    
        pass
    
    
    def toggleCreaseValueColorSetCB(self):
        pass
    
    
    def unbakeValuesIntoCreaseSetsCB(self):
        """
        Un-bake edges/verts with similar crease values into new CreaseSets
        """
    
        pass
    
    
    def unoptimizeSubdLevelCB(self):
        """
        Restore the displayed subd smoothLevel attr to the default value of 2.
        """
    
        pass
    
    
    def updateHighlightedItems_execute(self):
        """
        Update the highlighted items (visualized by changing the background
        color of the item) to indicate the items that the Maya selected items
        are members of.
        """
    
        pass
    
    
    def updateUI_objectSetMembersChanged(self):
        """
        Selectively update the widget tree for the specified creaseSet.
        This function is called by the objectSetMembersChangedCB callback when
        membership changes.  This updated column values for counts as well
        as updating the sub-items for the creaseSet.
        
        It processes self._requested_objectSetMembersChanged.
        
        :Return: None
        
        :Note: It should be called 'deferred' from a MCallback so as not to mess with the DG state by performing queries.
        """
    
        pass
    
    
    COLUMN_COUNT = 5
    
    
    COLUMN_CREASEVALUE = 2
    
    
    COLUMN_NUMMEMBERS = 3
    
    
    COLUMN_SELMEMBERS = 4
    
    
    COLUMN_SETCOLOR = 0
    
    
    COLUMN_SETNAME = 1
    
    
    staticMetaObject = None


class MCallbackIdWrapper(object):
    """
    Wrapper class to handle cleaning up of MCallbackIds from registered MMessage
    """
    
    
    
    def __del__(self):
        pass
    
    
    def __init__(self, callbackId):
        pass
    
    
    def __repr__(self):
        pass
    
    
    __dict__ = None
    
    __weakref__ = None


import maya.OpenMaya as om

class HashableMObjectHandle(om.MObjectHandle):
    """
    Hashable MObjectHandle referring to an MObject that can be used as a key in a dict.
    
    :See: MObjectHandle documentation for more information.
    """
    
    
    
    def __hash__(self):
        """
        Use the proper unique hash value unique to the MObject that the MObjectHandle points to so this class can be used as a key in a dict.
        
        :Return:
            MObjectHandle.hasCode() unique memory address for the MObject that is hashable
        
        :See: MObjectHandle.hashCode() documentation for more information.
        """
    
        pass


class MayaUndoChunk:
    """
    Safe way to manage group undo chunks using the 'with' command.
    It will close the chunk automatically on exit from the block
    
    :Example:
        maya.cmds.polyCube()
        with MayaUndoChunk():
            maya.cmds.polyCube()
            maya.cmds.polyCube()
        maya.cmds.undo()
    """
    
    
    
    def __enter__(self):
        pass
    
    
    def __exit__(self, type, value, traceback):
        pass
    
    
    def __init__(self, name='unnamedChunk'):
        pass



def getDefaultCreaseSetEditor():
    """
    Get the current CreaseSetEditor class used by default.
    
    :Return: class CreaseSetEditor or derived class
    """

    pass


def filterComponentsBySelectedItems(components):
    """
    Filters list of components against exact match of selected components or all the components for selected meshes.
    
    :Parameters:
        components ([string])
            component items to filter against the current selection
            
    :Return: list of items ([string])
    
    :Example:
        cmds.select('pCube1', 'pCube2.e[2:5]')
        filterComponentsBySelectedItems(['pCube1.e[2]', 'pCube1.e[4]', 'pCube2.e[1]', 'pCube2.e[2]', 'pCube3.e[1]'])
        # Result: ['pCube1.e[2]', 'pCube1.e[4]', 'pCube2.e[2]']
    """

    pass


def bakeOutCreaseSetValues(meshes):
    """
    Bake out the CreaseSet values from the specified meshes directly onto
    the meshes and remove the components from the CreaseSet.
    
    :Parameters:
        meshes ([string])
            The mesh shape nodes or mesh transforms to act upon
            
    :Return: None
    """

    pass


def setDefaultCreaseSetEditor(cls="<class 'maya.app.general.creaseSetEditor.CreaseSetEditor'>"):
    """
    Set the CreaseSetEditor class to use by default.
    This allows studios the ability to override the standard CreaseSetEditor
    and replace it with their own and still use the existing menu items
    for calling it
    
    :Parameters:
        cls (class)
            CreaseSetEditor or derived class. (default=CreaseSetEditor)
            
    :Example:
        import creaseSetEditor
        import myCreaseSetEditor
        creaseSetEditor.setDefaultCreaseSetEditor(myCreaseSetEditor.MyCreaseSetEditor)
        creaseSetEditor.showCreaseSetEditor()
    """

    pass


def convertCreasesToVertValues(meshT):
    """
    Convert edge and vertex crease values to a per-vertex dict of the max crease value
    connected to each vertex.
    
    :Parameters:
        meshT (string)
            The transform mesh node name to act upon
    
    Return: dict(vertexId, float)
    """

    pass


def _findPixmapResource(filename):
    """
    Resolve filenames using the XBMLANGPATH icon searchpath or look
    through the embedded Qt resources (if the path starts with a ':').
    
    :Parameters:
        filename (string)
            filename path or resource path (uses embedded Qt resources if starts with a ':'
    
    :Return: (QPixmap)
        QPixmap created from image found for absolute path string.
        Use .isNull() to check if the returned QPixmap is valid.
    """

    pass


def getCreaseSetPartition():
    """
    Returns a singleton 'creasePartition' shared node.  It creates one if it does not already exist.
    
    :Return: nodeName string to the creasePartition (string)
    """

    pass


def showCreaseSetEditor(dockControl=False, creaseSetEditorCls=None):
    """
    Create the CreaseSetEditor (optionally in a dockControl) and make it visible.
    This is the main way to launch the CreaseSetEditor.
    
    :Parameters:
        dockControl (bool)
            display the widget by a dock control. Otherwise use a standard standalone window
            (default=True)
        creaseSetEditorCls (class)
            explicitly specify the CreaseSetEditor class (or derived class) to show.  If unspecified, then
            it defaults to the value from getDefaultCreaseSetEditor()
            (default=None, which means the standard CreaseSetEditor)
    
    :Note:
        Handle internals to remove any existing CreaseSetEditor so it does not conflict
        with this new one.
        
    :Return: Tuple of CreaseSetEditor and dock control string identifier if specified (QWidget, string)
    """

    pass


def getCreaseSetsContainingItems(items=None, asDict=False):
    """
    Return list of sets that have edge/vertex members with the specified items
    
    :Parameters:
        items ([string])
            The edge and vertex items to look for in the creaseSet nodes.
            If mesh shapes are included, it will return all creaseSet nodes
            used by the mesh shapes as well.  If "None", then operate on the
            selected items.
        asDict (bool)
            if true, return a dict
            if false, return a set
            (default=False)
            
    :Limitation:
        If both a mesh and some of its components are selected/specified, then this function
        will return an artificially elevated count of selected members for the asDict=True option.
        It will add the total number of member components for the mesh and then additionally add
        the number of member components for the selected/specified components.
            
    :Return: Set of creaseSet names or dict in the format {creaseSet: numItems}
    """

    pass


def getSelectedMeshComponents(items=None, verts=False, edges=False, meshShapes=False, expand=False):
    """
    Return a list of the selected mesh components
    
    :Parameters:
        items ([string])
            items to filter.  If unspecified, then the function will act on the selected items.
        verts (bool)
            include mesh vertices in the list (default=False)
        edges (bool)
            include mesh edges in the list (default=False)
        meshShapes (bool)
            include mesh shapes (default=False)
        expand (bool)
            list each individual component as a separate item.  If false, compress the component list. (default=False)
    
    :Limitation:
        The returned component list will have dupliate components if both the meshShape and components are specified (or selected)
        in the list of items and meshShapes=True and at the verts/edges components equal True.
    
    :Return: list of component items ([string])
    """

    pass


def wrapInstance(*args, **kwargs):
    pass


def newCreaseSet(name='creaseSet#', elements=None, creaseLevel=2):
    """
    Create a crease set
    
    :Parameters:
        name (string)
            Name of the creaseSet node
        elements ([string])
            List of edges and vertices to add to the creaseSet
        creaseLevel (float)
            Initial creasing for the creaseSet creaseLevel attribute
            
    :Return: None
    """

    pass


def subdivideBaseMesh(meshes, level=1, adjustSmoothLevelDisplay=False):
    """
    Subdivide selected meshes by the specified level and decrement the creasing values in order to add resolution into the base mesh.
    The creaseSets used by the mesh must be exclusive to the meshes subdivided as the subdivide and creaseLevel adjustment must be done
    in tandem.
    
    :Parameters:
        meshes ([string])
            The mesh shape (of type 'mesh') or transform nodes (parent transform of mesh shapes)  to act upon
        level (int)
            level of subdivision to add to the base mesh
        adjustSmoothLevelDisplay (bool)
            specify if the mesh 'preview division levels' smoothLevel should be decremented to preserve
            the topology of the displayed mesh.  Setting this to True will preserve the same displayed vertex positions for
            the before/after smoothed meshes.
            
    :Return: list of meshes modified ([string])
    """

    pass


def lookupColorValue(v, minvalue=0.0, maxvalue=1.0, colors=None):
    """
    Linearly convert the value within the min/max range to a color with the specified colormap
    
    :Parameters:
        v (float)
            The value to convert
        minvalue (float)
            The minimum clamp value for the color scale
        maxvalue (float)
            The maximum clamp vaule for the color scale
        colors ([(r,g,b),...])
            A list of rgb colors to represent the colors to map 
            
    :Return: rgb tuple representing a color (r,g,b)
    """

    pass


def calcCreaseValueColorSet(meshTs=None, minvalue=0.0, maxvalue=4.0, colorSetName='creaseValues'):
    """
    Create a per-vertex "creaseValue" colorSet map from mesh crease values.
    Combines the crease values (max edge and vertex crease value per vertex) for each vertex and represent
    them by a color.
    
    :Parameters:
        meshTs ([string])
            List of transform mesh node names to act upon
        minvalue (float)
            The minimum clamp value for the color scale
        maxvalue (float)
            The maximum clamp vaule for the color scale
        colorSetName (string)
            The name of the colorSet to use, and create if it does not exist
    
    Return: None
    """

    pass


def unbakeValuesIntoCreaseSets(meshes, name='creaseSet#'):
    """
    Un-bake edges/verts with similar crease values into new CreaseSets
    
    :Parameters:
        meshes ([string])
            The mesh shape nodes (of type mesh) to act upon
        name (string)
            The name template to use for the new creaseSets.
            The "#" if used at the end of the string will be replaced with
            a number to make the name unique.
            
    :Return: None
    """

    pass


def getDependNode(nodeName):
    """
    Get an MObject (depend node) for the associated node name
    
    :Parameters:
        nodeName
            String representing the node
    
    :Return: depend node (MObject)
    """

    pass


def _loadUIString(strId):
    """
    # This method is meant to be used when a particular string Id is needed more than
    # once in this file.  The Maya Python pre-parser will report a warning when a
    # duplicate string Id is detected.
    """

    pass



_edgeSetColorSupported = False

formatter = None

ch = None

logger = None

_qtImported = 'PySide2'


