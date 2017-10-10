.. toctree::

********************
Knowledege
********************

Hopefully you find some of this helpful. It's a collection of places we've beat our heads in the wall.

Last update: 08.17.2017

Maya Known Things
====================

2017
------

Reloading a ui from a menu crashes maya
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Props to `Charles Wardlaw <http://sugarandcyanide.com/blog/>`_ for help on this. This stems from maya changing the way things work and what worked from 2011-2016 broke. However there's a pretty simple fix.
    
    * Changing my previous ``c = lambda *a:self.reload()`` to ``c = lambda *a:mc.evalDeferred(self.reload,lp=True)`` resolved it.

Python update broke zoo.path and other things
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

2017 brought in a new version of Python which broke how strings were handled. Rewrote zoo.path and some other modules as Hamish isn"t developing currently.

2016
-------

Raycasting issues with OpenMaya 2.0 vs 1.0
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Calls on OpenMaya 1 and 2 variations after some bugs were discovered with 2016 casting. Sepcifically 2.0: 

* when casting at poly edge, fails
* nurbsSurface UV returns a different rawUV than 1. 1 Normalizes as expected, 2"s does not.
* nurbsSurface normal returns junk and broken

Hotkey system changed
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Any previous hotkey setup tools probably broke. We"d been using zoo"s but wrote our own to address. You may find it ``cgm.core.classes.HotkeyFactory``. The biggest add was the addition of workspace which need to be dealt with.



Lessons learned
====================
Animation
----------------
* If you see ``// Warning: Non object-space scale baked onto components.`` check your scale settings and put it in object mode.



Attributes
--------------------------------

* MultiMessage attributes - In the end, not a fan of multi message nodes for things that we need to track specifically. When an item connected via mult message attr is duplicated. The multiMsg connections are duplicated. While this can be handy for certain things, when you need specific lists of items, it's not so hot. We developed our msgList setup for this reason.

Joints
-----------

* When doing chained segments, parenting the root of the roll segment to it"s root and leaving the handle joints clean works best.
* Joints doing funky scale things? Check that the ``inverseScale`` is conected to the joint parent.
* ``segmentScale`` is a very cool attribute when you wanna do fun scale stuff. Took way to many years of working in maya before discovering it.

Logging
-------------

* Log.debugs still take a hit on processing time. Watch em
* Logger is much faster that print
* pprint rules all.

Blendshapes
---------------

Breakdown
^^^^^^^^^^^^^^

* Index -- this is it's index in the blendshape node. Note - not necessarily sequential.
* Weight -- this is the value at which this shape is "on'. Usually it is 1.0. Inbetween shapes are between 0 and 1.0.
* Shape -- this is the shape that drives the blendshape channel
* Dag -- the dag node for the shape
* Alias -- the attribute corresponding to its index in the weight list. Typically it is the name of the dag node. 
* Plug -- the actual raw attribute of the shape on the node. ``BSNODE.w[index]``
* Weight Index -- follows a maya formula of index = wt * 1000 + 5000. So a 1.0 weight is a weight index of 6000.

Storage
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* Blendshape data is stored in these arrays in real time so that if you query the data and your base mesh isn't zeroed out, the transformation happening is baked into that
* The caveat to that is that targets that have their base geo deleted are "locked" in to their respective data channels at the point they were when deleted. Their delta information is frozen.
* ``BlendshapeNode.inputTarget[0].inputTargetGroup[index].inputTargetItem[weightIndex]``
    * ``inputTarget`` -- this is most often 0.
    * ``inputTargetGroup`` -- information for a particular shape index
    * ``inputTargetItem`` -- information for a particular weight index
* Sub items at that index
    * ``inputPointsTarget`` -- the is the differential data of the point positions being transformed by a given shape target. It is indexed to the inputComponentsTarget array
    * ``inputComponentsTarget`` -- these are the compents that are being affected by a given shape 
    * ``inputGeomTarget`` -- this is the geo affecting a particular target shape
* Replacing blendshapes - you can 1) use a copy geo function if the point count is exact to change the shape to what you want or 2) make a function to do it yourself. There's not a great way to replace a shape except to rebuild that whole index or the node itself. We made a function to do that
* Once a blendshape node is created with targets, the individual targets are no longer needed and just take up space. Especially when you have the easy ability to extract shapes.
* Getting a base for calculating delta information. As the blendshapes are stored as delta off of the base, the best way I could find to get that delta was to turn off all the deformers on the base object, query that and then return on/connect the envelopes. I'm sure there's more elegant solutions but I was unsuccessful in finding one.
    
    * Once you have that creating a new mesh from a an existing one is as simple as:
        * Taking base data
        * For components that are affected on a given index/weight: add the delta to base
        * duplicating the base and xform(t=vPos, absolute = True) each of the verts will give you a duplicate shape
* Aliasing weight attributes - mc.aliasAttr("NAME", "BSNODE.w[index]")


    
cmds/mc
-----------
* mc all the way. cmds eats toenails, Keith! 
* ``mc.listConnections``
    * To get plugs properly, you need both source and destination flags set - one True, one False to get expected results. Ran into a bug where the default value in maya changed between versions. Don"t assume.

Wing
----------------
Setting up wing auto completion with maya can be a bit tedious but as Josh got a new computer he had to go through it again recently and is putting it here so we don't forget.

https://wingware.com/doc/howtos/maya

Getting things setup can be a little tedious.
* Project Properties
    * Python executable - Point to maya mayapy.exe. Example: ``c:\Program Files\Autodesk\Maya2017\bin\mayapy.exe``
    * Python path - Set to custom
        * Add repo. Example ``d:\repos\cgmTools\mayaTools``
        * Add pi helper path. Example ``
* Preferences. edit>Preferences
    * Source Analysis - 
        * Add pi helper path. ``d:\[your path]\pi-files``

Sphinx
--------
We use sphinx, this is how we get rolling on new machines.

#. Install Python (2.76 I one we currently use for Maya reasons)
#. Open a command prompt
#. ``$ easy_install sphinx``
#. ``$ pip install sphinx_rtd_theme``
#. Walk to doc directory
#. Make changes to rsts
#. ``$ make html``

Python
------

Sys
^^^^^

* Pathing uses ``/`` on windows. - ``sys.path.append("d:/repos/cgmTools/mayaTools/")``

pprint
^^^^^^^^^
pprint is a fantastic tool for logging data while working. It breaks out dict data in a readable format. Pretty sure maya started using it in 2017 or as results in the script editor got the same readabilty around that time.

* ``pprint.pprint(vars())`` for example will print all active variables in the middle of a function without using some sort of editor to track it.



Concepts
====================
Not everyone does things the same way and use terms differently. Here's some help in following what we're talking about.

Locators
---------
See `locinator's section <locinator.html#concepts>`_

msgList
----------
This was our answer to the limiatations of MultiMessage attributes where we wanted specific defined lists of items. To do this we utilized single message attribute connections in an attribute sequence. More to come

Object Buffer
--------------
This is a way we store information to make things happen regardless of what you have selected or storing settings. In general we do this by optionVars As a couple of examples:

* The `match buffer <locinator.html#match-buffer>`_ stores objects to use with snapping regardless of selection
* The rayCast buffer defines cast targets for raycasting.

OptionVar
------------
Option variables are maya preference items that we use mainly for ui consistancy and saving settings between sessions and between tools. For example, changing the optionVar for rayCasting options will be used by the various tools that use it.

Raycasting
---------------
This is the function of using a point and vector in 3d space and shooting those rays at surfaces. We then can do all manner of things with that information. 

Some possiblities are:

* Snapping to a position in space
* Getting uv data for follicles
* On interactive aiming