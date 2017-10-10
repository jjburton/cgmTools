"""
Render setup overrides and collections can be enabled and disabled.

Disabling an override removes its effect, but keeps the override itself.

Disabling a collection disables all the overrides in its list, as well
as disabling any child (nested) collection it may have.

To implement this behavior, overrides and collections have three
attributes:

1) An enabled attribute.  This attribute is readable only (output), and
   is (trivially) computed from the two following attributes.
2) A self enabled attribute.  This writable attribute determines whether
   the override or collection itself is enabled.
3) A parent enabled attribute.  This writable attribute is connected to
   its parent's enabled output attribute, unless it is a collection
   immediately under a render layer.

The enabled output boolean value is the logical and of the self enabled
attribute and the parent enabled attribute.
"""

def addChangeCallbacks(node):
    """
    Add callbacks to indicate the argument node's enabled attribute changed.
    
    A list of callback IDs is returned.
    """

    pass


def createIntAttribute(longName, shortName, defaultValue):
    """
    Helper method to create an input (writable) int attribute
    """

    pass


def computeWithIsolateSelected(node, plug, dataBlock):
    pass


def initializeAttributes(cls):
    pass


def compute(node, plug, dataBlock):
    pass


def createBoolAttribute(longName, shortName, defaultValue):
    """
    Helper method to create an input (writable) boolean attribute
    """

    pass


def createBoolOutputAttribute(longName, shortName, defaultValue):
    """
    Helper method to create an output (readable) boolean attribute
    """

    pass


def _compute(node, plug, dataBlock):
    pass



