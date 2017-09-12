.. toctree::

********************
What's new?
********************
We'll keep this page update with the most important bits of what's new and getting started with the tools.

Last update: 09.12.2017

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

Bugs
--------

   * `2017`
      * General ui slow down - This seems to be an issue with 2017. Rebooting the computer resolves and sometimes force stopping Python. Continuing to investigate.
   * dynParentTool crash - ``Patch testing`` - Potential fix in bugs branch we're testing. Close to final testing on this.

Features/Updates
--------------------
* **Toolbox** - Continuing to flesh out the tools as we work through gigs.
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
* MeshTools - Initial Release