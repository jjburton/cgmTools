.. toctree::

********************
SetTools
********************
Status: Alpha release

Overview
==========
cgmSetTools is a tool for working with selection sets in maya. The 2.0 rewrite was completed in September 2017.


**What can I do with it?**

* Filter certain types of selection sets to work with
* Mutiset functionality. Key,reset,delete key on muliple sets as once


Accessing
==============
1. UI

    * Top cgm menu - ``CGM> animation> cgmSetTools``

2. Toolbox>TD>Rigging
3. Toolbox>Anim
4. Python
    
.. code-block:: guess

    import cgm.core.tools.setTools as setTools
    setTools.ui()
 
If you open the ui, you should see something like this:

.. image:: _static/img/settools/settools_base.png
    :align: center

The UI has to main parts. The top menu and body.


Menu
========
The top menu is where we set our options.

.. image:: _static/img/settools/settools_options.png
    :align: center
    
Force Update
--------------

Necessary when reloading the scene or if you made changes outside the tool and want to see those changes represented.
    
Modes
-------
The tool allows for the user to specify want options they want displayed during use.

Anim
^^^^^^
When active new options will show up in the ui. Both the muliset function bar and the left options on the row per objectSet.

.. image:: _static/img/settools/settools_anim.png
    :align: center
    
* ``s`` - Always visible. Select the items of the objectSet.

* ``k`` - Key the items of the objectSet
* ``d`` - Delete any curent keys of items in the objectSet
* ``r`` - Reset the items of the objectSet


Setup
^^^^^^^

.. image:: _static/img/settools/settools_setup.png
    :align: center
    
    
* ``+`` - Add selected items to this objectSet
* ``-`` - Remove selected items from this objectSet
* ``e`` - Edit mode. When toggled, an additional scrollList is generated below the row's objectSet which offers options on a per item level.
    
.. image:: _static/img/settools/settools_edit.png
    :align: center
    
* Currently left clicking any item in the list will select it. Looking into more options. Open to suggestions


Autohide
------------

.. image:: _static/img/settools/settools_autohide.png
    :align: center
    
* ``[] Anim Layersets`` - Hide anim layerset sets
* ``[] non Qss`` - Hide non qss sets
* ``[] Maya Sets`` - Hide default maya sets

    
Load Refs
------------

.. image:: _static/img/settools/settools_ref.png
    :align: center
    
You have the ability to only load the referenced sets you want. By default they aren't loaded. This is most handy with animation sets and multiple assets. The menu is split by:

* ``All`` - This will activate all reference prefixes
* ``[] Prefix`` - You can toggle individual prefixes
* ``Clear`` - If you want to clear all of the reference prefixes

    
Dock
------------

.. image:: _static/img/settools/settools_options.png
    :align: center

You can dock the tool with the ``dock`` button. Pressing when docked will undock it. Docked it looks something like this...

.. image:: _static/img/settools/settools_dock.png
    :align: center

Body
========

MultiSet Row
-------------
Only available with `anim mode <settools.html#anim>`_

.. image:: _static/img/settools/settools_multiset.png
    :align: center
    
* ``[]`` - When checked or unchecked all of the checkboxes on all loaded objectSet rows will toggle to match
* ``[<<< Active Sets>>>]`` - Toggle for two different multimodes.

    * Active sets - Only objectSets with their rows checked will be affected
    * All Loaded Sets - ALL loaded sets will be affected
* ``K`` - Key the items of the objectSets
* ``D`` - Delete any curent keys of items in the objectSets
* ``R`` - Reset the items of the objectSets


ObjectSet Row
---------------

.. image:: _static/img/settools/settools_setrow.png
    :align: center

* As previously discussed, certain modes have more options: 

    * `Anim <settools.html#anim>`_
    * `Setup <settools.html#setup>`_
    
* ``s`` - Always visible. Select the items of the objectSet.
* ``+`` - Add selected items to this objectSet
* ``-`` - Remove selected items from this objectSet
* ``e`` - Edit mode. When toggled, an additional scrollList is generated below the row's objectSet which offers options on a per item level.
    
    * Currently left clicking any item in the list will select it. Looking into more options. Open to suggestions
* ``[ nameOfASet ]`` - Textfield that displays the name of the set's base name. Each has an annotation with the set's full name. Additionally, each has a `right click menu <settools.html#Popup>`_.
* ``k`` - Key the items of the objectSet
* ``d`` - Delete any curent keys of items in the objectSet
* ``r`` - Reset the items of the objectSet

Popup
------------

Right click menu on the objectSet row textfield. 

.. image:: _static/img/settools/settools_setpopup.png
    :align: center
    
* ``[] Qss`` - Qss state. Check to change.
* ``Make Type:`` - Tag as a specific type. Unsure if we're keeping this. It's intended as an additional way to flag sets for filtering.
* ``Select set`` - Select the set itself.
* ``Purge`` - Clear the set but leave the set
* ``Rename`` - Bring up a uiPrompt to rename the set
* ``Copy`` - Create a new set with all of this set's items
* ``Log`` - Print a breakdown of what's in the set in the script editor
* ``Delete`` - Delete the set


