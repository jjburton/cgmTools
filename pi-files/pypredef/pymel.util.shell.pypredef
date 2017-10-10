from pymel.util.arguments import isIterable as _isIterable

def executableOutput(exeAndArgs, convertNewlines=True, stripTrailingNewline=True, returnCode=False, input=None, **kwargs):
    """
    Will return the text output of running the given executable with the given arguments.
    
    This is just a convenience wrapper for subprocess.Popen, so the exeAndArgs argment
    should have the same format as the first argument to Popen: ie, either a single string
    giving the executable, or a list where the first element is the executable and the rest
    are arguments.
    
    :Parameters:
        convertNewlines : bool
            if True, will replace os-specific newlines (ie, \r\n on Windows) with
            the standard \n newline
    
        stripTrailingNewline : bool
            if True, and the output from the executable contains a final newline,
            it is removed from the return value
            Note: the newline that is stripped is the one given by os.linesep, not \n
    
        returnCode : bool
            if True, the return will be a tuple, (output, returnCode)
    
        input : string
            if non-none, a string that will be sent to the stdin of the executable
    
    kwargs are passed onto subprocess.Popen
    
    Note that if the keyword arg 'stdout' is supplied (and is something other than subprocess.PIPE),
    then the return will be empty - you must check the file object supplied as the stdout yourself.
    
    Also, 'stderr' is given the default value of subprocess.STDOUT, so that the return will be
    the combined output of stdout and stderr.
    
    Finally, since maya's python build doesn't support universal_newlines, this is always set to False -
    however, set convertNewlines to True for an equivalent result.
    """

    pass


def putEnv(env, value):
    """
    set the value of an environment variable.  overwrites any pre-existing value for this variable. If value is a non-string
    iterable (aka a list or tuple), it will be joined into a string with the separator appropriate for the current system.
    """

    pass


def appendEnv(env, value):
    """
    append the value to the environment variable list ( separated by ':' on osx and linux and ';' on windows).
    skips if it already exists in the list
    """

    pass


def getEnvs(env, default=None):
    """
    get the value of an environment variable split into a list.  returns default ([]) if the variable has not been previously set.
    
    :rtype: list
    """

    pass


def refreshEnviron():
    """
    copy the shell environment into python's environment, as stored in os.environ
    """

    pass


def getEnv(env, default=None):
    """
    get the value of an environment variable.  returns default (None) if the variable has not been previously set.
    """

    pass


def shellOutput(shellCommand, convertNewlines=True, stripTrailingNewline=True, returnCode=False, input=None, **kwargs):
    """
    Will return the text output of running a given shell command.
    
    :Parameters:
        convertNewlines : bool
            if True, will replace os-specific newlines (ie, \r\n on Windows) with
            the standard \n newline
    
        stripTrailingNewline : bool
            if True, and the output from the executable contains a final newline,
            it is removed from the return value
            Note: the newline that is stripped is the one given by os.linesep, not \n
    
        returnCode: bool
            if True, the return will be a tuple, (output, returnCode)
    
        input : string
            if non-none, a string that will be sent to the stdin of the executable
    
    With default arguments, behaves like commands.getoutput(shellCommand),
    except it works on windows as well.
    
    kwargs are passed onto subprocess.Popen
    
    Note that if the keyword arg 'stdout' is supplied (and is something other than subprocess.PIPE),
    then the return will be empty - you must check the file object supplied as the stdout yourself.
    
    Also, 'stderr' is given the default value of subprocess.STDOUT, so that the return will be
    the combined output of stdout and stderr.
    
    Finally, since maya's python build doesn't support universal_newlines, this is always set to False -
    however, set convertNewlines to True for an equivalent result.
    """

    pass


def prependEnv(env, value):
    """
    prepend the value to the environment variable list (separated by ':' on osx and linux and ';' on windows).
    skips if it already exists in the list
    """

    pass



