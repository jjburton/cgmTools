.. toctree::

********************
What's new?
********************
We'll keep this page update with the most important bits of what's new and getting started with the tools.

Last update: 09.14.2017

Added Docs: 

* `Set Tools <settools.html>`_
* `Attr Tools <attrtools.html>`_
* `Mesh Tools <meshtools.html>`_
* `MarkingMenu <markingmenu.html>`_

New Tools:

* Set Tools 2.0
* Toolbox 2.0

Quick Start
=============== 

Requirments
--------------
* Maya 2010+
* OS - WIndows, Mac, Linux

Tutorial
-----------   
Let's do this

.. raw: html
    <div class="vimeo" align="left">
    <iframe width="420" height="315" src="https://player.vimeo.com/video/204937700" frameborder="0"></iframe>
    </div>

Until we get embeded video sorted. Please use this link: https://player.vimeo.com/video/204937700 

Stand Alone
--------------
1. Download the latest
2. Unzip it to your maya scripts folder

.. tip::
    1. Windows - ``c:\Users\<USERNAME>\My Documents\maya\<version>\scripts``
    2. Mac - ``/Users/<USERNAME>/Library/Preferences/Autodesk/maya/<version>/scripts``
    
3. In the mel command line, type: ``rehash``
4. Again in command line: ``cgmToolbox``
    

You should see a new window pop up.

If you're having issues, check .. `Support`


Active Development
=====================

Docs
---------

These help docs will be continued to be fleshed out. We currently only have about 30% coverage on tools

   * Toolbox/Toolbox up (09.05.2017) - Collecting Feedback
   * SetTools docs up (09.11.2017) - Collecting Feedback
   * AttrTools docs in que
   * Knowledge - Added 08.17.2017

Features/Updates
--------------------
* **MRS** - Morpheus Rig System
* **Build Pulls** - Working on a method to make getting update much easier

2017
^^^^^^^
* SetTools 2.0
* Transform Tools
* New Docs using Sphinx
* Toolbox 2.0
* MarkingMenu 2.0
* dynParentTool 
* AttrTools 2.0
* Locinator 2.0

2016
^^^^^^^
* MeshTools 1.0 - Initial Release


Release Notes
================

10.11.2017
----------------
Small sprint on getting the main menu working a bit faster and fixing a few bugs.

Toolbox
^^^^^^^^^
* Rework of cgmTop menu for speed. Previously, it was rebuilding everytime you moused over the menu. Now it does initially then on request via the ``Rebuild`` option.
* Moved module stuff around to clean things up and again try to get a bit more speed
* Create mid point mode - After doing some gig work, added the ability to create not just via object but by midpoint of objects or components

    * ``Toolbox> TD Tab > Rigging Section > Create row`` - null(mid), jnt(mid), loc(mid)

MarkingMenu
^^^^^^^^^^^^^^
For the sake of speed moving away from the all in one menu and instead providing access to important items and tools for more options. The marking menu option toggling was just too tedious.

* Added align options to snap marking menu. ``Marking Menu > Snap > Point > Along line (even/spaced)``
* Added ``TD Marking Menu > Create > Mid > Null/Joint/Locator`` 
* Rewored bottom menu to just be our most used tools rather than being contextual

SDK
^^^^^
This took some rework of some core stuff and refactoring from non core libraries. Prompted by the last project Josh worked.

* Started ``cgm.core.lib.sdk_utils`` for this endeavour.
* NEW Calls
    * ``cgm.core.lib.search.seek_upStream/seek_downStream``
* New section in cgmToolbox
* Ammended top menu with new functions
* seShapeTaper - Moved from joints
* NEW
    * Get Driven - Get objects driven by an sdk driver (usually an attribute) and select them
    * Get Driven Plugs - Get plugs driven by an sdk driver