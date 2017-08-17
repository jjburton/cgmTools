.. toctree::

********************
Toolbox WIP
********************

The cgmToolbox can be accessed in a couple of different ways:

* **Top menu** - We'll be talking about using this method in the next sections
* **Marking menu** - We'll get to this later or you can LATER

The new top menu was initially released in February 2017. It shares tool libraries with the
marking menu so most items available in one are in the other. Menu sections may be torn off for easy access.

Tool Window
====================
This is quick access to some legacy tools and some settings for the toolbox as as whole. 

.. image:: _static/img/topmenu/toolbox.png
    :align: center
    
Access
-------------
* ``Open Tool Win`` - You should see what something like the above image


Setup
----------------

* ``Create cgmToolboxMenu`` - adds the top menu to maya
* ``Autoload on maya start`` - Yup.

Until we get embeded video sorted. Please use this link: https://player.vimeo.com/video/206286478 

.. tip::
    Most functions in the top menu are also in the marking menu.
    
Tabs
-----------------
For now just take a look around.


Snap
===============
Functions for snapping items around. In general, they function on a selection basis with all targeting the last.

.. image:: _static/img/topmenu/snap.png
    :align: center
    
Basic
---------

* ``Point Closest`` - To the closest point on the last surface,curve,shape
* ``Parent`` - Position and orientation
* ``Orient`` - rotation only
* ``Aim`` - Currently uses object defaults from Menu. Will take into account object tagging in future.
* ``Aim Special`` - In the cgmMarkingMenu, if three or more objects are selected splits to subMenu:

    * ``All to last`` - All items aim at the last
    * ``Selection Order`` - Each object aims to the next
    * ``First to Midpoint`` - First object aims at the midpoint of the rest of the selection
    
Casting
-----------
Casting utilizes rayCasting to help position things. Our rayCasting by default casts at all eligible surfaces.

* ``RayCast`` - Uses the rayCast options to detect a point in space
* ``AimCast`` - Uses rayCasting to aim selected objects in real time at a point of intersection

Matching
--------------
If an object is tagged to a cgmMatchTarget, will match the object to the match target. For example, if it is an updatable object ([Locinator](locinator.md) loc), it will update.

* ``Self`` - Update the selected object to their respective match targets
* ``Target`` - Updates the selected's match targets to the selected
* ``Buffer`` - Update utilizing the match buffer

Arrange 
--------------
* ``Arrange`` - 
    * ``Along Line (Even)`` - Arrange selected along line from frist to last evenly
    * ``Along Line (Spaced)`` - Arrange selected along a line snapping middle objects to their nearest point on the line 

Options
--------
See `Options Window`

TD
=====
Collection of tools for rigging and td work. It will eventually cover all that our legacy tool did and much more.

.. image:: _static/img/topmenu/td.png
    :align: center

Select
----------

A contextual selection tool. For each option provided you can select objects of the given type. This is a WIP tool,
we're unsure how useful it is. Simply an easy call from some other stuff we were doing.

* ``Selection`` - Work from our current selection
* ``Children`` - Check all children of all selected objects
* ``Heirarchy`` - Check heirarchies of all selected objects
* ``Scene`` - Check entire scene

.. image:: _static/img/topmenu/select_context.png
    :align: center

The options which are pretty self evident. If you clicked ``TD/Create/Select*/scene/Joints`` all joints in the scene would be selected.

* ``Joints``  
* ``Curves``  
* ``Mesh``  
* ``Surface`` 

Rigging Utils
----------------
Create from selected
^^^^^^^^^^^^^^^^^^^^^
Series of options to create new objects matching the given selection. 

* ``Transform`` - 
* ``Joint`` - 
* ``Locator`` - Locators are special. They work based off component selection and are updateable. More on that later or [here](locinator.md)
* ``Curve`` - Instead of per object, creates a curve through selection. Points may be components.

Copy
^^^^^^
Series or functions for copying this and that in a from>to fashion.

* ``Transform`` - Copy the position and orientation.
* ``Orientation`` - Only the orientation.
* ``Shapes`` - Any shapes are appended.
* ``Pivot`` - You can specify which pivot ou want to copy.

    * ``rotatePivot`` - 
    * ``scalePivot`` - 

Group
^^^^^^
Series or functions for grouping selected per selected objects. Groups are created matching the transform of their targets so objects can be zeroed for example. They are also named.

* ``Just Group`` - Just the group
* ``Group Me`` - Group created, objected paretned to said group. Group is in world.
* ``In Place`` - Group created, and inserts itself between target and target's original parent

Control Curves
^^^^^^^^^^^^^^^^
Options for creating control curves from selected objects. 

* ``Create Control Curve`` - Creates a control curve at each selected object utilizing stored create options. See [Toolbox Options](toolboxoptions.md) for more details.
* ``One of each`` - Just a way to create one of every curve type in our library
* ``Make resizeObj`` - Create a matching transform and shape from your selected objects so you can cleanly resize and shape without worrying about the rig. When you're done...
* ``Push resizeObj changes`` - Replace the shapes of the original object and delete our resizeObj
* ``Mirror World Space To Target`` - Currently only works across world x
* ``{Options}`` - Opens the `Option Window`


Attributes
----------------

* ``[cgmAttrTools](attrtools)`` 
* ``Add`` - Creates a ui prompt to add a number of attributes of the selected type. Separate by ``,`` 

    * ``enum``
    * ``string``
    * ``int``
    * ``float``
    * ``vector``
    * ``bool``
    * ``message``
* ``Compare Attrs`` - Compares the prime node to other selected nodes. That comparison comprising seeing what attributes on the given objects match and which do not. Here's example output:
    
.. code-block:: guess

    # cgm.core.lib.attribute_utils : Comparing nurbsSphere2 to nurbsSphere1... # 
    # cgm.core.lib.attribute_utils : Matching attrs: 199 | Unmatching: 29 # 
    # cgm.core.lib.attribute_utils : -------------------------------------------------------------------------- # 
    # cgm.core.lib.attribute_utils : attr: boundingBoxMin... # 
    # cgm.core.lib.attribute_utils : source: [-4.348416510705419, -1.543820107219151, 0.38805085162276876] # 
    # cgm.core.lib.attribute_utils : target: [-1.2264094625656805, -1.0, -1.2264094625656803] # 
    # cgm.core.lib.attribute_utils : attr: boundingBoxMinX... # 
    # cgm.core.lib.attribute_utils : source: -4.34841651071 # 
    # cgm.core.lib.attribute_utils : target: -1.22640946257 # 
    # cgm.core.lib.attribute_utils : attr: boundingBoxMinY... # 
    # cgm.core.lib.attribute_utils : source: -1.54382010722 # 
    # cgm.core.lib.attribute_utils : target: -1.0 # 
    # cgm.core.lib.attribute_utils : attr: boundingBoxMinZ... # 
    # cgm.core.lib.attribute_utils : source: 0.388050851623 # 
    # cgm.core.lib.attribute_utils : target: -1.22640946257 # 


Raycasting
----------------
WIP

Distance
----------------
WIP

Joints
----------------
WIP

SDK
----------------
WIP

Shape
----------------
WIP

Curve
----------------
WIP

Mesh
----------------
WIP

Skin
----------------
WIP


Nodes
----------------
WIP






Anim
=====
WIP

Layout
=======
WIP

Hotkeys
========
WIP

Dev
=====
WIP

Help
=====
WIP

Option Window
===============
.. image:: _static/img/toolboxoptions/optionVar_ui.png
    :align: center


