from pymel.util.arguments import isIterable
from pymel.core.language import getMelType
from pymel.core.language import isValidMelType
from pymel.util.arguments import isMapping

import pymel.api.plugins as plugins

class WrapperCommand(plugins.Command):
    def parseCommandArgs(self, argData):
        pass
    
    
    def parseFlagArgs(self, argData):
        """
        cycle through known flags looking for any that have been set.
        
        :rtype: a list of (flagLongName, flagArgList) tuples
        """
    
        pass
    
    
    def setResult(self, result):
        """
        convert to a valid result type
        """
    
        pass
    
    
    def createSyntax(cls):
        pass



def _shortnameByUnderscores(name):
    """
    for python methods that use underscores instead of camelCaps, with a maximum of 3 letters
    """

    pass


def _nonUniqueName(longname, shortname, shortNames, operation):
    pass


def _shortnameByCaps(name):
    """
    uses hungarian notation (aka camelCaps) to generate a shortname, with a maximum of 3 letters
        ex.
    
            myProc --> mp
            fooBar --> fb
            superCrazyLongProc --> scl
    """

    pass


def _getArgInfo(obj, allowExtraKwargs=True, maxVarArgs=10, filter=None):
    """
    Returns a dict giving info about the arugments for the function/property
    
    If obj is None, will return the 'defaults'.
    """

    pass


def _getShortNames(objects, nonUniqueName):
    """
    uses several different methods to generate a shortname flag from the long name
    """

    pass


def _getFunction(function):
    pass


def _invalidName(commandName, longname, operation):
    pass


def py2melCmd(pyObj, commandName=None, register=True, includeFlags=None, excludeFlags=[], includeFlagArgs=None, excludeFlagArgs={}, nonUniqueName='warn', invalidName='warn'):
    """
    Create a MEL command from a python function or class.
    
    A MEL command has two types of arguments: command arguments and flag arguments.  In the case of passing a function, the function's
    non-keyword arguments become the command arguments and the function's keyword arguments become the flag arguments.
    for example::
    
        def makeName( first, last, middle=''):
            if middle:
                return first + ' ' + middle + ' ' + last
            return first + ' ' + last
    
        import pymel as pm
        from pymel.tools.py2mel import py2melCmd
        cmd = py2melCmd( makeName, 'makeNameCmd' )
        pm.makeNameCmd( 'Homer', 'Simpson')
        # Result: Homer Simpson #
        pm.makeNameCmd( 'Homer', 'Simpson', middle='J.')
        # Result: Homer J. Simpson #
    
    Of course, the real advantage of this tool is that now your python function is available from within MEL as a command::
    
        makeNameCmd "Homer" "Simpson";
        // Result: Homer Simpson //
        makeNameCmd "Homer" "Simpson" -middle "J.";
        // Result: Homer J. Simpson //
    
    To remove the command, call the deregister method of the class returned by py2melCmd::
    
        cmd.deregister()
    
    This function attempts to automatically create short names (3 character max) based on the long names of the methods or arguments of the pass python object.
    It does this by looping through long names in alphabetical order and trying the following techniques until a unique short name is found:
    
            1. by docstring (methods only): check the method docstring looking for something of the form ``shortname: xyz``::
                class Foo():
                    def bar():
                        'shortname: b'
                        # do some things
                        return
            2. by convention:  if the name uses under_scores or camelCase, use the first letter of each "word" to generate a short name up to 3 letters long
            3. first letter
            4. first two letters
            5. first three letters
            6. first two letters plus a unique digit
    
    .. warning:: if you edit the python object that is passed to this function it may result in short names changing!  for example, if you have a class like the following::
    
                class Foo():
                    def bar():
                        pass
    
            ``Foo.bar`` will be assigned the short flag name 'b'. but if you later add the method ``Foo.baa``, it will be assigned the short flag name 'b' and 'bar' will be given 'ba'.
            **The only way to be completely sure which short name is assigned is to use the docstring method described above.**
    
    Parameters
    ----------
    commandName : str
        name given to the generated MEL command
    register : bool
        whether or not to automatically register the generated command.  If
        False, you will have to manually call the `register` method of the
        returned `WrapperCommand` instance
    includeFlags : list of str
        list of flags to include. if given, other flags will be ignored
    exludeFlags : list of str
        list of flags to exclude
    includeFlagArgs : dict from str to list of str
        for each flag, a list of arg names to include; if given, other args will
        be ignored
    excludeFlagArgs : dict from str to list of str
        for each flag, a list of arg names to exclude
    nonUniqueName : 'force', 'warn', 'skip', or 'error'
        what to do if a flag name is not unique
    invalidName: 'force', 'warn', 'skip', or 'error'
        what to do if a flag name is invalid
    """

    pass


def _shortnameByDoc(method):
    """
    a shortname can be explicitly set by adding the keyword shortname followed by a colon followed by the shortname
    
            ex.
    
            class foo():
                def bar():
                    'shortname: b'
                    # do some things
                    return
    """

    pass


def _shortnameByConvention(name):
    """
    chooses between byUnderscores and ByCaps
    """

    pass


def getMelArgs(function, exactMelType=True):
    """
    Inspect the arguments of a python function and return the cloesst
    compatible MEL arguments.
    
    Returns
    -------
    ``((argName, melType ), {argName : default}, {argName : description})``
    
    Parameters
    ----------
    function : callable or str
        This can be a callable python object or the full, dotted path to the
        callable object as a string.
    """

    pass


def py2melProc(function, returnType=None, procName=None, evaluateInputs=True, argTypes=None):
    """
    This is a work in progress.  It generates and sources a mel procedure which wraps the passed
    python function.  Theoretically useful for calling your python scripts in scenarios where Maya
    does not yet support python callbacks.
    
    The function is inspected in order to generate a MEL procedure which relays its
    arguments on to the python function.  However, Python features a very versatile argument structure whereas
    MEL does not.
    
        - python args with default values (keyword args) will be set to their MEL analogue, if it exists.
        - normal python args without default values default to strings. If 'evaluteInputs' is True, string arguments passed to the
            MEL wrapper proc will be evaluated as python code before being passed to your wrapped python
            function. This allows you to include a typecast in the string representing your arg::
    
                myWrapperProc( "Transform('persp')" );
    
        - *args : not yet implemented
        - **kwargs : not likely to be implemented
    
    
    function
        This can be a callable python object or the full, dotted path to the callable object as a string.
    
        If passed as a python object, the object's __name__ and __module__ attribute must point to a valid module
        where __name__ can be found.
    
        If a string representing the python object is passed, it should include all packages and sub-modules, along
        with the function's name:  'path.to.myFunc'
    
    procName
        Optional name of the mel procedure to be created.  If None, the name of the function will be used.
    
    evaluateInputs
        If True (default), string arguments passed to the generated mel procedure will be evaluated as python code, allowing
        you to pass a more complex python objects as an argument. For example:
    
        In python:
            >>> import pymel.tools.py2mel as py2mel
            >>> def myFunc( arg ):
            ...    for x in arg:
            ...       print x
            >>> py2mel.py2melProc( myFunc, procName='myFuncWrapper', evaluateInputs=True )
    
        Then, in mel::
            // execute the mel-to-python wrapper procedure
            myFuncWrapper("[ 1, 2, 3]");
    
        the string "[1,2,3]" will be converted to a python list [1,2,3] before it is executed by the python function myFunc
    """

    pass



MAX_FLAG_ARGS = 6

MAX_VAR_ARGS = 10

_functionStore = {}

MELTYPES = []


