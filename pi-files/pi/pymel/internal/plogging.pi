from logging import *

from maya.OpenMaya import MGlobal
from pymel.util.decoration import decorator
from maya.OpenMaya import MMessage
from maya.OpenMaya import MEventMessage

def _setupLevelPreferenceHook():
    """
    Sets up a callback so that the last used log-level is saved to the user preferences file
    """

    pass


def _fixMayaOutput():
    pass


def _addOldHandlers(logger, oldHandlers, secName, configParser):
    pass


def pymelLogFileConfig(fname, defaults=None, disable_existing_loggers=False):
    """
    Reads in a file to set up pymel's loggers.
    
    In most respects, this function behaves similarly to logging.config.fileConfig -
    consult it's help for details. In particular, the format of the config file
    must meet the same requirements - it must have the sections [loggers],
    [handlers], and [fomatters], and it must have an entry for [logger_root]...
    even if not options are set for it.
    
    It differs from logging.config.fileConfig in the following ways:
    
    1) It will not disable any pre-existing loggers which are not specified in
    the config file, unless disable_existing_loggers is set to True.
    
    2) Like logging.config.fileConfig, the default behavior for pre-existing
    handlers on any loggers whose settings are specified in the config file is
    to remove them; ie, ONLY the handlers explicitly given in the config will
    be on the configured logger.
    However, pymelLogFileConfig provides the ability to keep pre-exisiting
    handlers, by setting the 'remove_existing_handlers' option in the appropriate
    section to True.
    """

    pass


def environLogLevelOverride(logger):
    """
    If PYMEL_LOGLEVEL is set, make sure the logging level is at least that
    much for the given logger.
    """

    pass


def raiseLog(logger, level, message, errorClass="<type 'exceptions.RuntimeError'>"):
    """
    For use in situations in which you may wish to raise an error or simply
    print to a logger.
    
    Ie, if checking for things that "shouldn't" happen, may want to raise an
    error if a developer, but simply issue a warning and continue as gracefully
    as possible for normal end-users.
    
    So, if we make a call:
        raiseLog(_logger, _logger.INFO, "oh noes! something weird happened!")
    ...then what happens will depend on what the value of ERRORLEVEL (controlled
    by the environment var %s) is - if it was not set, or set to ERROR, or
    WARNING, then the call will result in issuing a _logger.info(...) call;
    if it was set to INFO or DEBUG, then an error would be raised.
    
    For convenience, raiseLog is installed onto logger instances created with
    the getLogger function in this module, so you can do:
        _logger.raiseLog(_logger.INFO, "oh noes! something weird happened!")
    """

    pass


def nameToLevel(name):
    pass


def getConfigFile():
    pass


def addErrorLog(logger):
    """
    Adds an 'raiseLog' method to the given logger instance
    """

    pass


def getLogger(name):
    """
    a convenience function that allows any module to setup a logger by simply
    calling `getLogger(__name__)`.  If the module is a package, "__init__" will
    be stripped from the logger name
    """

    pass


def levelToName(level):
    pass


def getLogConfigFile():
    pass


def timed(level=10):
    pass



ERRORLEVEL = None

ERRORLEVEL_DEFAULT = 40

n = 50

root = None

logLevels = {}

PYMEL_CONF_ENV_VAR = 'PYMEL_CONF'

pymelLogger = None

PYMEL_LOGLEVEL_ENV_VAR = 'PYMEL_LOGLEVEL'

PYMEL_ERRORLEVEL_ENV_VAR = 'PYMEL_ERRORLEVEL'


