import exceptions

"""
This module provides functions for upgrading scripts from pymel 0.9 to 1.0.  It
fixes two types non-compatible code:
    - pymel.all is now the main entry-point for loading all pymel modules
        - import pymel         --> import pymel.all as pymel
        - import pymel as pm   --> import pymel.all as pm
        - from pymel import *  --> from pymel.all import *
    - pymel.mayahook.versions.Version is now pymel.versions

To use, run this in a script editor tab::

    import pymel.tools.upgradeScripts
    pymel.tools.upgradeScripts.upgrade()

This will print out all the modules that will be upgraded.  If everything looks good
run the following to perform the upgrade::

    pymel.tools.upgradeScripts.upgrade(test=False)

Once you're sure that the upgrade went smoothly, run::

    pymel.tools.upgradeScripts.cleanup()

This will delete the backup files.

If you need to undo the changes, run::

    pymel.tools.upgradeScripts.undo()

Keep in mind that this will restore files to their state at the time that you ran
``upgrade``.  If you made edits to the files after running ``upgrade`` they will
be lost.
"""

from collections import defaultdict

class LogError(exceptions.ValueError):
    __weakref__ = None



def upgradeFile(filepath, test=True):
    """
    upgrade a single file
    """

    pass


def cleanup(logfile=None, force=False):
    """
    remove backed-up files.  run this when you are certain that the upgrade went
    smoothly and you no longer need the original backups.
    
    :param logfile:
    the logfile containing the list of files to restore.  if None, the logfile
    will be determined in this order:
        1. last used logfile (module must have remained loaded since running upgrade)
        2. MAYA_APP_DIR
        3. current working directory
    :param force:
        if you've lost the original logfile, setting force to True will cause the function
        to recurse sys.path looking for backup files to cleanup instead of using the log.
        if your sys.path is setup exactly as it was during upgrade, all files should
        be restored, but without the log it is impossible to be certain.
    """

    pass


def _findbackups():
    pass


def upgrade(logdir=None, test=True, excludeFolderRegex=None, excludeFileRegex=None, verbose=False, force=False):
    """
    search PYTHONPATH (aka. sys.path) and MAYA_SCRIPT_PATH for python files using
    pymel that should be upgraded
    
    Keywords
    --------
    
    :param logdir:
        directory to which to write the log of modified files
    :param test:
        when run in test mode (default) no files are changed
    :param excludeFolderRegex:
        a regex string which should match against a directory's basename, without parent path
    :param excludeFileRegex:
        a regex string which should match against a file's basename, without parent path or extension
    :param verbose:
        print more information during conversion
    :param force:
        by default, `upgrade` will skip files which already have already been processed,
        as determined by the existence of a backup file with a .pmbak extension. setting
        force to True will ignore this precaution
    """

    pass


def _getMayaAppDir():
    pass


def undo(logfile=None, force=False):
    """
    undo converted files to their original state and remove backups
    
    :param logfile:
        the logfile containing the list of files to restore.  if None, the logfile
        will be determined in this order:
            1. last used logfile (module must have remained loaded since running upgrade)
            2. MAYA_APP_DIR
            3. current working directory
    :param force:
        if you've lost the original logfile, setting force to True will cause the function
        to recurse sys.path looking for backup files to restore instead of using the log.
        if your sys.path is setup exactly as it was during upgrade, all files should
        be restored, but without the log it is impossible to be certain.
    """

    pass


def _getbackups(logfile, force):
    pass


def _getLogfile(logfile, read=True):
    pass


def undoFile(filepath):
    """
    undo a single file
    """

    pass



last_logfile = None

SUFFIX = 3

objects = []

BACKUPEXT = '.pmbak'

IMPORT_RE = None

LOGNAME = 'pymel_upgrade.log'

FROM_RE = None

OBJECT = 2

PREFIX = 1


