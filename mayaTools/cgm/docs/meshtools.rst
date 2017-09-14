.. toctree::

********************
Mesh Tools
********************

Status: 1.0 Release - Fall 2016

Last update: 08.17.2017



Overview
==========
MeshTools are a collection of tools to work with geo (poly or nurbs(for some)). You can find a detailed breakdown on the sections in the links provided.

**Core Modules**

Main modules this tool is using for those wanting to dig in.

* ``cgm.core.lib.geo_Utils``
* ``cgm.core.classes.DraggerContextFactory``
* ``cgm.core.lib.shapeCaster``
* ``cgm.core.lib.rayCaster``

Accessing
==============
#. Top cgm menu - ``CGM > TD > Mesh > cgmMeshTools``
#. Toolbox - ``TD Tab> Rigging > Mesh > MeshTools``
#. Python
    
.. code-block:: guess

    import cgm.core.tools.meshTools as MESHTOOLS
    MESHTOOLS.go()
 
If you open the ui, you should see something like this:

.. image:: _static/img/meshtools/meshtools_base.png
    :align: center

It's divided into three modes: Math, Cast, Utils

.. tip::
    * Previous selections are remembered for subsequent processes if possible
    * From/to selection is typical.

Menu
========
The top menu is where we set our options and get help

Options
-----------

.. image:: _static/img/meshtools/meshtools_options.png
    :align: center
    
* ``Space`` - xform space for mesh math functions
* ``Create`` - click Mesh create options
* ``Sym Axis`` - axis to measure symetry from
* ``Lathe Axis`` - curve casting lathe axis
* ``Aim Axis`` - object aim axis for shooting rays
* ``Obj Up Axis`` - object up axis for casting curves (lolipop for example)
* ``Extend Mode`` - extend mode for how curves are wrapped
    
Math
========
The math section is about using the positional data to do math functions similar to other deformers like blendshapes.

.. image:: _static/img/meshtools/meshtools_vid_math.png
    :align: center
    
Until we get embeded video sorted. Please use this link: https://player.vimeo.com/video/183549761 


.. tip::
    * Most math functions now work with soft selection evaluation
    * The `space section of the options menu <meshtools.html#Options>`_ affects math functions.

.. image:: _static/img/meshtools/meshtools_base.png
    :align: center

Base Object
-------------

.. image:: _static/img/meshtools/meshtools_baseobject.png
    :align: center
    
* ``Base [              ]`` - Text field that displays the base object when loaded
* ``<<`` - Loads a selected mesh as a base. It is then processed for it's symmetry dict
* ``Reprocess`` - Recheck the symmetry of a base object to see if you've resolved it
* ``Report`` - Tells how many asymetrical verts there are
* ``symMode`` - specify which point to base symmetry calculation from
* ``Tolerance`` - How close of a tolerance symmetry should be calculated to
* ``x`` - Value to multiply calculations from on the various buttons
* ``sym`` - Sym axis to measure symetry from
* ``result`` - Specify how the result should be used

    * ``New`` - Create a new mesh
    * ``Modify`` - modify the target
    * ``Values`` - report values
    
Base Select
-------------
Various methods of selecting helpful bits on the base..

.. image:: _static/img/meshtools/meshtools_baseselect.png
    :align: center
    
* ``Center`` - select the base center verts
* ``Pos`` - select the base positive verts
* ``Neg`` - select the base negative verts
* ``Asym`` - select the asymetrical verts (if there are some)

Target Select
--------------
Same as before but on selected target geo.

.. image:: _static/img/meshtools/meshtools_targetselect.png
    :align: center
    
* ``Center`` - select a target's center verts
* ``Pos`` - select the target's positive verts
* ``Neg`` - select the targets negative verts
* ``Check Sym``- select the target's asymetrical verts (if there are any)
* ``Select Mirror`` - selected the mirrored verts of those selected
* ``Select Moved`` - selected the moved verts of the selected objects relative to the base

Targets To Base
------------------
Functions cast in relation to the base on selected objects. Cumulative effect.

.. image:: _static/img/meshtools/meshtools_targettobase.png
    :align: center

.. note::
    ``*`` marks math functions that don't work with soft selection yet
   
* ``Add`` - base + target * multiplier
* ``Subtract`` - base - target * multiplier
* ``Average`` - average(base,target) * multiplier
* ``Reset`` - Reset to base
* ``Diff`` - delta of base - target
* ``+Diff`` - base + (delta * multiplier)
* ``-Diff`` - base - (delta * multiplier). This is what you'd use for 'adding' deltas
* ``xDiff`` - x delta
* ``yDiff`` - y delta
* ``zDiff`` - z delta
* ``Blend`` - acts like a blendshape with multiplier being the weight value
* ``xBlend`` - x only blendshape
* ``yBlend`` - y only blendshape
* ``zBlend`` - z only blendshape

Blend Slider - slider creation of blend

* ``Flip`` * - Flip the shape across the axis
* ``SymPos`` * - Mirror the positive side
* ``SymNeg`` * - Mirror the negative side

Target Math
----------------
.. image:: _static/img/meshtools/meshtools_targetmath.png
    :align: center
    
Functions cast on selected objects. Cumulative effect. Last object is treated as the base (except for ``copyTo``). See previous section for more details.

    

Cast
==========
This was our intial pass on rayCasting with geo in a ui form. 

.. image:: _static/img/meshtools/meshtools_vid_cast.png
    :align: center
    
Until we get embeded video sorted. Please use this link: https://player.vimeo.com/video/183556460 

.. image:: _static/img/meshtools/meshtools_cast.png
    :align: center

Cast Targets
----------------

.. image:: _static/img/meshtools/meshtools_casttargets.png
    :align: center

This is where we load our targets to cast if we want to be specific. If no targets are specified, all mesh and nurbs surface objects in scene will be used.

* Load Field - Multi select ability enabled. Displays loaded names and mesh types.

    * Popup - loads on right click on an item
    
        * ``Select`` - handy if you have a big scene and aren't sure where an item is
        * ``Remove Selected``
        * ``Remove Non-selected``
* ``Load Selected`` - Load selected objects
* ``Load all`` - Load all eligible targets (geo or nurbs)
* ``Clear all`` - Clear this. When clear, ALL eligible targets will be used.

Click Mesh
------------
For most things `toolbox <toolbox.html#id3>`_ section is probably more intutive except for shapeCasting which it doesn't do.

.. image:: _static/img/meshtools/meshtools_clickmesh.png
    :align: center

* Mode -

    * ``Surface`` - first hit
    * ``bisect`` - Piercing cast or all hits
    * ``midPoint`` - Mid point of hits
* ``[ ] Drag`` - When checked, rays are cast as long as you click 
* ``Clamp[ 0 ]`` - Clamp the number of hits
* ``Start`` - Start the tool
* ``Drop`` - Force the tool to drop and create non locator objects
* ``Snap`` - Snap selected objects to cast point based on setting provided

* ``Create`` - (Options Menu) - What to create for click mesh when tool is released. 

    * Options: locator,joint,jointChain,curve,follicle,group


Object Cast
----------------
This is a two part section. Most of the options in the slice section affect the wrap section as well. The general theory is that rays are cast from a given object in order to create curves. To my mind I think of the death blossom from the 80's flick the Last Starfighter spinning around around shooting rays.
Works off a given selection of objects and uses the cast targets specified or all if none are.

.. image:: _static/img/meshtools/meshtools_objectcast.png
    :align: center

Slice
^^^^^^^
A slice is a single curve lathe.

**Options** - Accessed via the `options menu <Options>`_

* ``Lathe Axis``  - curve casting lathe axis
* ``Aim Axis`` - object aim axis for shooting rays


* ``[] mark`` - Mark hits. Useful for troubleshooting and using data for other bits.
* ``[] closed`` - Create closed curve
* ``[] near`` - Use the nearest hit or use the farthest hit
* ``d [3]`` - The degree of the curve to create. 1 is linear.
* ``p [9]`` - Points - Number of rays to cast which translates to points of the curve
* ``[] < [0.0]`` - Min Range (with toggle) - Specify range of an angle to cast
* ``[] > [0.0]`` - Max Range (with toggle) - Specify range of an angle to cast
* ``dist`` - Distance - Range which to cast our rays
* ``Offset: [0.0] [0.0] [0.0]`` - Offset - Offset of a hit to further process. Use z to push out from the surface
* ``Slice`` - Make your mesh curve slice

Wrap
^^^^^^
A wrap is a more complicated lathe often with more than one cast point.

**Options** - Accessed via the `options menu <Options>`_

* ``Obj Up Axis `` - object up axis for casting curves (lolipop for example)
* ``Extend Mode`` - extend mode for how curves are wrapped

    * ``Segment`` - cylider between two points
    * ``radial`` - single radial cast like the rings of Saturn
    * ``disc`` -
    * ``cylinder`` -
    * ``loliwrap`` -
    * ``endCap`` - most often used for things like finger tips


* ``Root: [0.0] [0.0] [0.0]``  - Root Offset - Offset for our root cast object. May be pulling this from gui call.
* ``bank: [0.0]`` - Bank - Bake for cast object. May be pulling this from gui call.
* ``[] mid`` - Mid mesh cast. May be pulling this from gui call.
* ``[] join`` - Join cast curves. Only used in certain modes.
* ``[] Inset [ 0.2]`` - Inset multplier. Only used with certain modes.
* Wrap - Make your mesh wrap

    
Utils
=======

.. image:: _static/img/meshtools/meshtools_vid_utils.png
    :align: center
    
Until we get embeded video sorted. Please use this link: https://player.vimeo.com/video/183669485 

.. image:: _static/img/meshtools/meshtools_utilities.png
    :align: center

Proximity Query
----------------
Create proxi geometry based on a from to selection.
* ``Expand`` - Mode by which to expand the found selection.

    * ``None`` -
    * ``Grow`` - Grow selection by amount specified
    * ``Soft Select [0.0]`` - Use soft select to grow by amount specified
    
* ``Result``- What kind of data we want from our processing.

    * ``objs``
    * ``face``
    * ``edge``
    * ``vtx``
    * ``mesh`` - create a proximesh
    
* ``Mode`` -

    * ``Ray Cast`` - Use ray casting to check for precisness
    * ``Bounding Box`` - Use the much faster bounding box check
    
* ``Go`` - Process