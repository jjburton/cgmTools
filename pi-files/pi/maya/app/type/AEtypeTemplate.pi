import pymel.core.uitypes

from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2.QtGui import *

from collections import defaultdict
from sets import Set

class AEtypeTemplate(pm.uitypes.AETemplate):
    def EscapedToUni(self, str):
        pass
    
    
    def HexToByte(self, hexStr):
        """
        Convert a string hex byte values into a byte string. The Hex Byte values may
        or may not be space separated.
        """
    
        pass
    
    
    def HexToUni(self, hexStr):
        pass
    
    
    def UniToEscaped(self, str):
        pass
    
    
    def __init__(self, nodeName):
        pass
    
    
    def addWidgets(self, atr):
        """
        #add the wigets to the interface using the qControl to link a Maya layout to a widget.
        """
    
        pass
    
    
    def add_tabs(self, atr):
        pass
    
    
    def add_tabs_replace(self, atr):
        pass
    
    
    def build_ui(self, nodeName):
        pass
    
    
    def create_connections(self):
        pass
    
    
    def fontChanged(self):
        """
        #get the new font and set the attributes accordingly
        #also loads all the styles for this font into the family menu.
        """
    
        pass
    
    
    def loadStyleList(self):
        pass
    
    
    def on_text_change(self, nodeName):
        """
        #update the textInput attribute whenever we type something
        """
    
        pass
    
    
    def on_text_change_deferred(self):
        pass
    
    
    def setUpWritingSystems(self):
        pass
    
    
    def styleChanged(self):
        """
        #triggered when the style changes, it tries to load the style into the rich text edit
        """
    
        pass
    
    
    def systemChanged(self):
        """
        #triggered when the writing system changes, it refilters the fonts.
        """
    
        pass
    
    
    def typeContextMenu(self):
        """
        #this function exists to override the font in the QTextEdit contextual menu, by default it matches what ever font is set in the QTextEdit.
        """
    
        pass
    
    
    def uiDeleted(self):
        pass
    
    
    def updateUI(self, widget=None):
        """
        #loads values from the node attributes into the widget
        """
    
        pass
    
    
    def widget_replace(self, atr):
        """
        #connect the widgets to the node
        """
    
        pass


class qWidgetWrapper:
    """
    class to wrap Qt widgets to listen for delete
    
    Attributes:
        widget         pointer      Qt widget
        isValid        bool         widget token
    """
    
    
    
    def __init__(self, widget):
        """
        qWidgetWrapper constructor
        
        Arguments:
            widget         pointer      Qt widget
        """
    
        pass
    
    
    def destroyed(self):
        """
        destroyed callback
        """
    
        pass


class attrWatcher:
    """
    class to wrap custom widgets with attribute support
    
    Attributes:
        node           string       node name
        attribute      string       attribute name
        updateUI       function     widget update function
        widgetChanged  function     widget changed function
        attributeChangeScriptJob
                       int          attributeChange scriptJob ID
        nodeDeletedScriptJob
                       int          nodeDeleted scriptJob ID
        deleteAllScriptJob
                       int          deleteAll scriptJob ID
        plug           string       node.attribute
        inAttrChanged  bool         attrChanged token
        inSetAttr      bool         setAttr token
        inUpdateUI     bool         updateUI token
        linkedWatcher  attrWatcher  watcher to update
    """
    
    
    
    def __init__(self, node, attribute, updateUI, widgetChanged):
        """
        attrWatcher constructor
        
        Arguments:
            node           string    node name
            attribute      string    attribute name
            updateUI       function  widget update function
            widgetChanged  function  widget changed function
        """
    
        pass
    
    
    def attrChanged(self):
        """
        handle attrChanged
        """
    
        pass
    
    
    def getAttr(self):
        """
        return the attribute value
        """
    
        pass
    
    
    def nodeDeleted(self):
        """
        handle nodeDeleted
        """
    
        pass
    
    
    def setAttr(self, value):
        """
        set the attribute value
        """
    
        pass
    
    
    def setLinkedWatcher(self, linkedWatcher):
        """
        set a linked watcher
        """
    
        pass
    
    
    def setNode(self, node):
        """
        set the node
        
        Arguments:
            node           string    node name
        """
    
        pass
    
    
    def widgetWatcher(self):
        """
        listen for widget changes
        """
    
        pass



def changeCommandUpdateAE(nodeName):
    """
    #force the AE to update when we enable/ disable checkboxes
    """

    pass


def animationPivotMenusChance(animationNode, channel):
    pass


def typeUITemplate():
    """
    #UITemplate, very simple, just allows me to adjust the width of the controls all together.
    """

    pass


def _loadUIString(strId):
    """
    # Based on nodeEditorMenus.py
    #
    # This method is meant to be used when a particular string Id is needed more
    # than once in this file.  The Maya Python pre-parser will report a warning
    # when a duplicate string Id is detected.
    """

    pass


def wrp(*args, **kwargs):
    pass


def deformableTypeChangeCommand(polyRemeshNode, changeCommand):
    pass


def typeBevelStyleUpdate(extrudeNode, bevelStyle):
    """
    #hide and show the correct bevel interface
    """

    pass


def textAlignmentChange(nodeName):
    """
    #setting alignment modes
    """

    pass


def qControl(mayaName, qobj=None):
    """
    #get pointer to the Maya interface object, used for adding widgets to a Maya layout
    """

    pass


def ByteToHex(byteStr):
    """
    Convert a byte string to it's hex string representation e.g. for output.
    """

    pass


def checkAnimationPivotMenuBoxes(animationNode):
    pass



