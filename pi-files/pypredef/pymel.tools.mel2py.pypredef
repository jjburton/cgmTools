"""
==========================
Mel To Python Translator
==========================


Known Limitations
=================

array index assignment
----------------------

In mel, you can directly assign the value of any element in an array, and all intermediate elements will be
automatically filled. This is not the case in python: if the list index is out of range an IndexError will be
raised. I've added fixes for several common array assignment conventions:

append new element
~~~~~~~~~~~~~~~~~~

MEL::

    string $strArray[];
    $strArray[`size $strArray`] = "foo";

Python::

    strArray = []
    strArray.append("foo")

assignment relative to end of array
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

MEL::

    strArray[`size $strArray`-3] = "foo";

Python::

    strArray[-3] = "foo"

However, since the translator does not track values of variables, it does not know if any given index is out of
range or not. so, the following would raise a 'list assignment index out of range' error when converted to
python and would need to be manually fixed::

    string $strArray[];
    for ($i=0; $i<5; $i++)
        $strArray[$i] = "foo"


for(init; condition; update)
----------------------------

    the closest equivalent to this in python is something akin to::

        for i in range(start, end):
            ...

    in order for this type of for loop to be translated into a python for loop it must meet several requirements:

    1. the initialization, condition, and update expressions must not be empty.

        not translatable::

              for(; ; $i++) print $i;

    2. there can be only one conditional expression.

        not translatable::

              for($i=0; $i<10, $j<20; $i++) print $i;

    3. the variable which is being updated and tested in the condition (aka, the iterator) must exist alone on one
        side of the    conditional expression. this one is easy enough to fix, just do some algebra:

        not translatable::

              for($i=0; ($i-2)<10, $i++) print $i;

        translatable::

              for($i=0; $i<(10+2), $i++) print $i;

    4. the iterator can appear only once in the update expression:

        not translatable::

              for($i=0; $i<10; $i++, $i+=2) print $i;

    if these conditions are not met, the for loop will be converted into a while loop::

        i=0
        while 1:
            if not ( (i - 2)<10 ):
                break
            print i
            i+=1


Inconveniences
==============

Switch Statements
-----------------
Alas, switch statements are not supported by python. the translator will convert them into an if/elif/else statement.


Global Variables
----------------

Global variables are not shared between mel and python.  two functions have been added to pymel for this purpose:
`pymel.core.langauage.getMelGlobal` and `pymel.core.langauage.setMelGlobal`. by default, the translator will convert mel global variables into python global
variables AND intialize them to the value of their corresponding mel global variable using `getMelGlobal()`. if your
python global variable does not need to be shared with other mel scripts, you can remove the get- and
setMelGlobals lines (for how to filter global variables, see below). however, if it does need to be shared, it is very
important that you manually add `setMelGlobal()` to update the variable in the mel environment before calling any mel
procedures that will use the global variable.

In order to hone the accuracy of the translation of global variables, you will find two dictionary parameters below --
`global_var_include_regex` and `global_var_exclude_regex` -- which you can use to set a regular expression string
to tell the translator which global variables to share with the mel environment (i.e. which will use the get and set
methods described above) and which to not.  for instance, in my case, it is desirable for all of maya's global
variables to be initialized from their mel value but for our in-house variables not to be, since the latter are often
used to pass values within a single script. see below for the actual regular expressions used to accomplish this.


Comments
--------
Rules on where comments may be placed is more strict in python, so expect your comments to be shifted around a bit
after translation.


Formatting
----------

Much of the formatting of your original script will be lost. I apologize for this, but python is much more strict
about formatting than mel, so the conversion is infinitely simpler when the formatting is largely discarded
and reconstructed based on pythonic rules.


Solutions and Caveats
=====================

catch and catchQuiet
--------------------

There is no direct equivalent in python to the catch and catchQuiet command and it does not exist in maya.cmds so i wrote two
python commands of the same name and put them into pymel. these are provided primarily for compatibility with
automatically translated scripts. try/except statements should be used instead of catch or catchQuiet if coding
from scratch.

for( $elem in $list )
---------------------

This variety of for loop has a direct syntactical equivalent in python.  the only catch here is that maya.cmds
functions which are supposed to return lists, return None when there are no matches. life would be much simpler
if they returned empty lists instead.  the solution currently lies in pymel, where i have begun
correcting all of these command to return proper results.  i've started with the obvious ones, but there
are many more that i need to fix.  you'll know you hit the problem when you get this error: 'TypeError: iteration
over non-sequence'. just email me with commands that are giving you problems and i'll fix them as
quickly as i can.
"""

from pymel.util.external.ply.lex import LexError

def _makePackages():
    pass


def fileOnMelPath(file):
    """
    Return True if this file is on the mel path.
    """

    pass


def mel2pyStr(data, currentModule=None, pymelNamespace='', forceCompatibility=False, verbosity=0, basePackage=None):
    """
    convert a string representing mel code into a string representing python code
    
        >>> import pymel.tools.mel2py as mel2py
        >>> print mel2py.mel2pyStr('paneLayout -e -configuration "top3" test;')
        from pymel.all import *
        paneLayout('test',configuration="top3",e=1)
        <BLANKLINE>
    
    Note that when converting single lines, the lines must end in a semi-colon, otherwise it is technically
    invalid syntax.
    
    Parameters
    ----------
    data : `str`
        string representing coe to convert
    
    currentModule : `str`
        the name of the module that the hypothetical code is executing in. In most cases you will
        leave it at its default, the __main__ namespace.
    
    pymelNamespace : `str`
        the namespace into which pymel will be imported.  the default is '', which means ``from pymel.all import *``
    
    forceCompatibility : `bool`
        If True, the translator will attempt to use non-standard python types in order to produce
        python code which more exactly reproduces the behavior of the original mel file, but which
        will produce "uglier" code.  Use this option if you wish to produce the most reliable code
        without any manual cleanup.
    
    verbosity : `int`
        Set to non-zero for a *lot* of feedback
    """

    pass


def resolvePath(melobj, recurse=False, exclude=(), melPathOnly=False, basePackage=''):
    """
    if passed a directory, get all mel files in the directory
    if passed a file, ensure it is a mel file
    if passed a procedure name, find its file
    
    Returns tuples of the form (moduleName, melfile).
    """

    pass


def _updateCurrentModules(newResults):
    pass


def findMelOnlyCommands():
    """
    Using maya's documentation, find commands which were not ported to python.
    """

    pass


def melInfo(input):
    """
    Get information about procedures in a mel file.
    
        >>> import pymel.tools.mel2py as mel2py
        >>> mel2py.melInfo('attributeExists')
        (['attributeExists'], {'attributeExists': {'returnType': 'int', 'args': [('string', '$attr'), ('string', '$node')]}}, {})
    
    Parameters
    ----------
    input
        can be a mel file or a sourced mel procedure
    
    Returns
    -------
    allProcs : list of str
        The list of procedures in the order the are defined
    globalProcs : dict
        A dictionary of global procedures, with the following entries:
            - returnType: mel type to be returned
            - args: a list of (type, variable_name) pairs
    localProcs : dict
        A dictionary of local procedures, formatted the same as with globals
    """

    pass


def _getInputFiles(input, recurse=False, exclude=(), melPathOnly=False, basePackage=''):
    """
    Returns tuples of the form (packageName, melfile)
    """

    pass


def mel2py(input, outputDir=None, pymelNamespace='', forceCompatibility=False, verbosity=0, test=False, recurse=False, exclude=(), melPathOnly=False, basePackage=None):
    """
    Batch convert an entire directory
    
    Parameters
    ----------
    input
        May be a directory, a list of directories, the name of a mel file, a list of mel files, or the name of a sourced procedure.
        If only the name of the mel file is passed, mel2py will attempt to determine the location
        of the file using the 'whatIs' mel command, which relies on the script already being sourced by maya.
    
    outputDir : `str`
        Directory where resulting python files will be written to
    
    pymelNamespace : `str`
        the namespace into which pymel will be imported.  the default is '', which means ``from pymel.all import *``
    
    forceCompatibility : `bool`
        If True, the translator will attempt to use non-standard python types in order to produce
        python code which more exactly reproduces the behavior of the original mel file, but which
        will produce "uglier" code.  Use this option if you wish to produce the most reliable code
        without any manual cleanup.
    
    verbosity : `int`
        Set to non-zero for a *lot* of feedback
    
    test : `bool`
        After translation, attempt to import the modules to test for errors
    
    recurse : `bool`
        If the input is a directory, whether or not to recursively search subdirectories as well.
        Subdirectories will be converted into packages, and any mel files within those subdirectories
        will be submodules of that package.
    
    exclude : `str`
        A comma-separated list of files/directories to exclude from processing, if input is a directory.
    
    melPathOnly : `bool`
        If true, will only translate mel files found on the mel script path.
    
    basePackage : `str`
        Gives the package that all translated modules will be a part of; if None or an empty string, all
        translated modules are assumed to have no base package.
    """

    pass



custom_proc_remap = {}

log = None


