"""
Current Features
----------------

tab completion of depend nodes, dag nodes, and attributes
automatic import of pymel

Future Features
---------------

- tab completion of PyNode attributes
- color coding of tab complete options
    - to differentiate between methods and attributes
    - dag nodes vs depend nodes
    - shortNames vs longNames
- magic commands
- bookmarking of maya's recent project and files

To Use
------

place in your PYTHONPATH
add the following line to the 'main' function of $HOME/.ipython/ipy_user_conf.py::

    import ipymel

Author: Chad Dombrova
"""

from IPython.core.error import UsageError
from IPython.utils.coloransi import ColorSchemeTable
from IPython.utils.coloransi import TermColors as Colors
from optparse import OptionParser
from IPython.utils.coloransi import ColorScheme
from IPython.core.page import page

class TreePager(object):
    def __init__(self, colors, options):
        pass
    
    
    def do_level(self, obj, depth, isLast):
        """
        # print options.depth
        """
    
        pass
    
    
    def make_tree(self, roots):
        pass
    
    
    __dict__ = None
    
    __weakref__ = None


class DagTree(TreePager):
    def getChildren(self, obj):
        pass
    
    
    def getName(self, obj):
        pass


class DGHistoryTree(TreePager):
    def getChildren(self, obj):
        pass
    
    
    def getName(self, obj):
        pass
    
    
    def make_tree(self, root):
        pass



def ipymel_sigint_handler(signal, frame):
    """
    # maya sets a sigint / ctrl-c / KeyboardInterrupt handler that quits maya -
    # want to override this to get "normal" python interpreter behavior, where it
    # interrupts the current python command, but doesn't exit the interpreter
    """

    pass


def finalPipe(obj):
    """
    DAG nodes with children should end in a pipe (|), so that each successive pressing
    of TAB will take you further down the DAG hierarchy.  this is analagous to TAB
    completion of directories, which always places a final slash (/) after a directory.
    """

    pass


def complete_node_with_attr(node, attr):
    pass


def complete_node_with_no_path(node):
    pass


def magic_open(self, parameter_s=''):
    """
    Change the current working directory.
    
    This command automatically maintains an internal list of directories
    you visit during your IPython session, in the variable _sh. The
    command %dhist shows this history nicely formatted. You can also
    do 'cd -<tab>' to see directory history conveniently.
    
    Usage:
    
      openFile 'dir': changes to directory 'dir'.
    
      openFile -: changes to the last visited directory.
    
      openFile -<n>: changes to the n-th directory in the directory history.
    
      openFile --foo: change to directory that matches 'foo' in history
    
      openFile -b <bookmark_name>: jump to a bookmark set by %bookmark
         (note: cd <bookmark_name> is enough if there is no
          directory <bookmark_name>, but a bookmark with the name exists.)
          'cd -b <tab>' allows you to tab-complete bookmark names.
    
    Options:
    
    -q: quiet.  Do not print the working directory after the cd command is
    executed.  By default IPython's cd command does print this directory,
    since the default prompts do not display path information.
    
    Note that !cd doesn't work for this purpose because the shell where
    !command runs is immediately discarded after executing 'command'.
    """

    pass


def expand(obj):
    """
    allows for completion of objects that reside within a namespace. for example,
    ``tra*`` will match ``trak:camera`` and ``tram``
    
    for now, we will hardwire the search to a depth of three recursive namespaces.
    TODO:
    add some code to determine how deep we should go
    """

    pass


def splitDag(obj):
    pass


def buildRecentFileMenu():
    pass


def magic_dghist(self, parameter_s=''):
    pass


def open_completer(self, event):
    pass


def sigint_plugin_loaded_callback(*args):
    """
    # unfortunately, it seems maya overrides the SIGINT hook whenever a plugin is
    # loaded...
    """

    pass


def install_sigint_handler(force=False):
    pass


def magic_dag(self, parameter_s=''):
    pass


def main():
    pass


def setup(shell):
    pass


def pymel_name_completer(self, event):
    pass


def get_colors(obj):
    pass


def pymel_python_completer(self, event):
    """
    Match attributes or global python names
    """

    pass



LightBGColors = None

x = '1'

NoColor = None

ip = None

delim = ' \t\n`~!@#$%^&*()-=+[{]}\\;\'",<>/?'

ver11 = True

LinuxColors = None

dag_parser = None

ipy_ver = []

dg_parser = None

color_table = {}

_scheme_default = 'Linux'


