"""
In particular, the system module contains the functionality of maya.cmds.file. The file command should not be imported into
the default namespace because it conflicts with python's builtin file class. Since the file command has so many flags,
we decided to kill two birds with one stone: by breaking the file command down into multiple functions -- one for each
primary flag -- the resulting functions are more readable and allow the file command's functionality to be used directly
within the pymel namespace.

for example, instead of this:

    >>> res = cmds.file( 'test.ma', exportAll=1, preserveReferences=1, type='mayaAscii', force=1 ) # doctest: +SKIP

you can do this:

    >>> expFile = exportAll( 'test.ma', preserveReferences=1, force=1)

some of the new commands were changed slightly from their flag name to avoid name clashes and to add to readability:

    >>> importFile( expFile )  # flag was called import, but that's a python keyword
    >>> ref = createReference( expFile )
    >>> ref # doctest: +ELLIPSIS
    FileReference(u'...test.ma', refnode=u'testRN')

Notice that the 'type' flag is set automatically for you when your path includes a '.mb' or '.ma' extension.

Paths returned by these commands are either a `Path` or a `FileReference`, so you can use object-oriented path methods with
the results::

    >>> expFile.exists()
    True
    >>> expFile.remove() # doctest: +ELLIPSIS
    Path('...test.ma')
"""

from pymel.util.path import path as pathClass
from pymel.util.decoration import decorator
from pymel.util.scanf import fscanf

class Namespace(unicode):
    """
    #===============================================================================
    # Namespace
    #===============================================================================
    """
    
    
    
    def __add__(self, other):
        pass
    
    
    def __cmp__(self, other):
        pass
    
    
    def __eq__(self, other):
        pass
    
    
    def __ge__(self, other):
        pass
    
    
    def __gt__(self, other):
        pass
    
    
    def __le__(self, other):
        pass
    
    
    def __lt__(self, other):
        pass
    
    
    def __ne__(self, other):
        pass
    
    
    def __repr__(self):
        pass
    
    
    def clean(self, haltOnError=True, reparentOtherChildren=True):
        """
        Deletes all nodes in this namespace
        
        Parameters
        ----------
        haltOnError : bool
            If true, and reparentOtherChildren is set, and there is an error in
            reparenting, then raise an Exception (no rollback is performed);
            otherwise, ignore the failed reparent, and continue
        reparentOtherChildren : bool
            If True, then if any transforms in this namespace have children NOT
            in this namespace, then will attempt to reparent these children
            under world (errors during these reparenting attempts is controlled
            by haltOnError)
        """
    
        pass
    
    
    def getNode(self, nodeName, verify=True):
        pass
    
    
    def getParent(self):
        pass
    
    
    def listNamespaces(self, recursive=False, internal=False):
        """
        List the namespaces contained within this namespace.
        
        :parameters:
        recursive : `bool`
            Set to True to enable recursive search of sub (and sub-sub, etc)
            namespaces
        internal : `bool`
            By default, this command filters out certain automatically created
            maya namespaces (ie, :UI, :shared); set to True to show these
            internal namespaces as well
        """
    
        pass
    
    
    def listNodes(self, recursive=False, internal=False):
        """
        List the nodes contained within this namespace.
        
        :parameters:
        recursive : `bool`
            Set to True to enable recursive search of sub (and sub-sub, etc)
            namespaces
        internal : `bool`
            By default, this command filters out nodes in certain automatically
            created maya namespaces (ie, :UI, :shared); set to True to show
            these internal namespaces as well
        """
    
        pass
    
    
    def ls(self, pattern='*', **kwargs):
        pass
    
    
    def move(self, other, force=False):
        pass
    
    
    def remove(self, haltOnError=True, reparentOtherChildren=True):
        """
        Removes this namespace
        
        Recursively deletes any nodes and sub-namespaces
        
        Parameters
        ----------
        haltOnError : bool
            If true, and reparentOtherChildren is set, and there is an error in
            reparenting, then raise an Exception (no rollback is performed);
            otherwise, ignore the failed reparent, and continue
        reparentOtherChildren : bool
            If True, then if any transforms in this namespace have children NOT
            in this namespace, then will attempt to reparent these children
            under world (errors during these reparenting attempts is controlled
            by haltOnError)
        """
    
        pass
    
    
    def setCurrent(self):
        pass
    
    
    def shortName(self):
        pass
    
    
    def splitAll(self):
        pass
    
    
    def create(cls, name):
        pass
    
    
    def getCurrent(cls):
        pass
    
    
    def __new__(cls, namespace, create=False):
        pass
    
    
    __dict__ = None
    
    __weakref__ = None


class Workspace(object):
    """
    This class is designed to lend more readability to the often confusing workspace command.
    The four types of workspace entries (objectType, fileRule, renderType, and variable) each
    have a corresponding dictiony for setting and accessing these mappings.
    
        >>> from pymel.all import *
        >>> workspace.fileRules['mayaAscii']
        u'scenes'
        >>> workspace.fileRules.keys() # doctest: +ELLIPSIS
        [...u'mayaAscii', u'mayaBinary',...]
        >>> 'mayaBinary' in workspace.fileRules
        True
        >>> workspace.fileRules['super'] = 'data'
        >>> workspace.fileRules.get( 'foo', 'some_default' )
        'some_default'
    
    the workspace dir can be confusing because it works by maintaining a current working directory that is persistent
    between calls to the command.  In other words, it works much like the unix 'cd' command, or python's 'os.chdir'.
    In order to clarify this distinction, the names of these flags have been changed in their class method counterparts
    to resemble similar commands from the os module.
    
    old way (still exists for backward compatibility)
        >>> proj = workspace(query=1, dir=1)
        >>> proj  # doctest: +ELLIPSIS
        u'...'
        >>> workspace(create='mydir')
        >>> workspace(dir='mydir') # move into new dir
        >>> workspace(dir=proj) # change back to original dir
    
    new way
        >>> proj = workspace.getcwd()
        >>> proj  # doctest: +ELLIPSIS
        Path('...')
        >>> workspace.mkdir('mydir')
        >>> workspace.chdir('mydir')
        >>> workspace.chdir(proj)
    
    All paths are returned as an pymel.core.system.Path class, which makes it easy to alter or join them on the fly.
        >>> workspace.path / workspace.fileRules['mayaAscii']  # doctest: +ELLIPSIS
        Path('...')
    """
    
    
    
    def __call__(self, *args, **kwargs):
        """
        provides backward compatibility with cmds.workspace by allowing an instance
        of this class to be called as if it were a function
        """
    
        pass
    
    
    def __init__(self, *p, **k):
        pass
    
    
    def expandName(self, path):
        pass
    
    
    def chdir(self, newdir):
        pass
    
    
    def getName(self):
        pass
    
    
    def getPath(self):
        pass
    
    
    def getcwd(self):
        pass
    
    
    def mkdir(self, newdir):
        pass
    
    
    def new(self, workspace):
        pass
    
    
    def open(self, workspace):
        pass
    
    
    def save(self):
        pass
    
    
    def update(self):
        pass
    
    
    def __new__(cls, *p, **k):
        """
        # redefine __new__
        """
    
        pass
    
    
    __dict__ = None
    
    __weakref__ = None
    
    name = None
    
    path = None
    
    
    
    fileRules = {}
    
    
    objectTypes = {}
    
    
    renderTypes = {}
    
    
    variables = {}


class Path(pathClass):
    """
    A basic Maya file class. it gets most of its power from the path class written by Jason Orendorff.
    see path.py for more documentation.
    """
    
    
    
    def __repr__(self):
        pass
    
    
    def getTypeName(self, **kwargs):
        """
        Set the type of this file.  By default this can be any one of: mayaAscii, mayaBinary, mel,  OBJ, directory, plug-in, audio, move, EPS, Adobe(R) Illustrator(R), imageplug-ins may define their own types as well.Return a string array of file types that match this file.                  
        
        
        Derived from mel command `maya.cmds.file`
        """
    
        pass
    
    
    def setSubType(self, **kwargs):
        pass


class ReferenceEdit(str):
    """
    Parses a reference edit command string into various components based on the edit type.
    This is the class returned by pymel's version of the 'referenceQuery' command.
    """
    
    
    
    def remove(self, force=False):
        """
        Remove the reference edit. if 'force=True' then the reference will be unloaded from the scene (if it is not already unloaded)
        """
    
        pass
    
    
    def __new__(cls, editStr, fileReference=None, successful=None):
        pass
    
    
    __dict__ = None
    
    editData = None
    
    fullNamespace = None
    
    namespace = None
    
    rawEditData = None


class _Iterable(object):
    def __iter__(self):
        pass
    
    
    def __subclasshook__(cls, C):
        pass
    
    
    __dict__ = None
    
    __weakref__ = None
    
    __abstractmethods__ = frozenset()


class WorkspaceEntryDict(object):
    def __contains__(self, key):
        pass
    
    
    def __getitem__(self, item):
        pass
    
    
    def __init__(self, entryType):
        pass
    
    
    def __iter__(self):
        pass
    
    
    def __repr__(self):
        pass
    
    
    def __setitem__(self, item, value):
        pass
    
    
    def get(self, item, default=None):
        pass
    
    
    def has_key(self, key):
        pass
    
    
    def items(self):
        pass
    
    
    def keys(self):
        pass
    
    
    def values(self):
        pass
    
    
    __dict__ = None
    
    __weakref__ = None


class _Container(object):
    def __contains__(self, x):
        pass
    
    
    def __subclasshook__(cls, C):
        pass
    
    
    __dict__ = None
    
    __weakref__ = None
    
    __abstractmethods__ = frozenset()


class Translator(object):
    """
    Provides information about a Maya translator, which is used for reading
    and/or writing file formats.
    
    >>> ascii = Translator('mayaAscii')
    >>> ascii.ext
    u'ma'
    >>> bin = Translator.fromExtension( 'mb' )
    >>> bin
    Translator(u'mayaBinary')
    >>> bin.name
    u'mayaBinary'
    >>> bin.hasReadSupport()
    True
    """
    
    
    
    def __init__(self, name):
        pass
    
    
    def __repr__(self):
        pass
    
    
    def __str__(self):
        pass
    
    
    def extension(self):
        pass
    
    
    def filter(self):
        pass
    
    
    def getDefaultOptions(self):
        pass
    
    
    def getFileCompression(self):
        pass
    
    
    def hasReadSupport(self):
        pass
    
    
    def hasWriteSupport(self):
        pass
    
    
    def optionsScript(self):
        pass
    
    
    def setDefaultOptions(self, options):
        pass
    
    
    def setFileCompression(self, compression):
        pass
    
    
    def fromExtension(ext, mode=None, caseSensitive=False):
        pass
    
    
    def listRegistered():
        pass
    
    
    __dict__ = None
    
    __weakref__ = None
    
    ext = None
    
    name = None


class UndoChunk(object):
    """
    Context manager for encapsulating code in a single undo.
    
    Use in a with statement
    Wrapper for cmds.undoInfo(openChunk=1)/cmds.undoInfo(closeChunk=1)
    
    >>> import pymel.core as pm
    >>> pm.ls("MyNode*", type='transform')
    []
    >>> with pm.UndoChunk():
    ...     res = pm.createNode('transform', name="MyNode1")
    ...     res = pm.createNode('transform', name="MyNode2")
    ...     res = pm.createNode('transform', name="MyNode3")
    >>> pm.ls("MyNode*", type='transform')
    [nt.Transform(u'MyNode1'), nt.Transform(u'MyNode2'), nt.Transform(u'MyNode3')]
    >>> pm.undo() # Due to the undo chunk, all three are undone at once
    >>> pm.ls("MyNode*", type='transform')
    []
    """
    
    
    
    def __enter__(self):
        pass
    
    
    def __exit__(*args, **kwargs):
        pass
    
    
    __dict__ = None
    
    __weakref__ = None


class _Sized(object):
    def __len__(self):
        pass
    
    
    def __subclasshook__(cls, C):
        pass
    
    
    __dict__ = None
    
    __weakref__ = None
    
    __abstractmethods__ = frozenset()


class FileReference(object):
    """
    A class for manipulating references which inherits Path and path.  you can create an
    instance by supplying the path to a reference file, its namespace, or its reference node to the
    appropriate keyword. The namespace and reference node of the reference can be retreived via
    the namespace and refNode properties. The namespace property can also be used to change the namespace
    of the reference.
    
    Use listReferences command to return a list of references as instances of the FileReference class.
    
    It is important to note that instances of this class will have their copy number stripped off
    and stored in an internal variable upon creation.  This is to maintain compatibility with the numerous methods
    inherited from the path class which requires a real file path. When calling built-in methods of FileReference,
    the path will automatically be suffixed with the copy number before being passed to maya commands, thus ensuring
    the proper results in maya as well.
    """
    
    
    
    def __eq__(self, other):
        pass
    
    
    def __ge__(self, other):
        pass
    
    
    def __gt__(self, other):
        pass
    
    
    def __hash__(self):
        pass
    
    
    def __init__(self, pathOrRefNode=None, namespace=None, refnode=None):
        pass
    
    
    def __le__(self, other):
        pass
    
    
    def __lt__(self, other):
        pass
    
    
    def __melobject__(self):
        pass
    
    
    def __ne__(self, other):
        pass
    
    
    def __repr__(self):
        pass
    
    
    def __str__(self):
        pass
    
    
    def clean(self, **kwargs):
        """
        Remove edits from the passed in reference node. The reference must be in an unloaded state. To remove a particular type of edit, use the editCommand flag. If no flag is specified, all edits will be removed.                  
        
        Flags:
          - editCommand:
              For use with cleanReference. Remove only this type of edit. Supported edits are: setAttr addAttr deleteAttr connectAttr
              disconnectAttr and parent
        
        Derived from mel command `maya.cmds.file`
        """
    
        pass
    
    
    def copyNumberList(self):
        """
        When queried, this flag returns a string array containing a number that uniquely identifies each instance the file is used.                  
        
        
        Derived from mel command `maya.cmds.file`
        """
    
        pass
    
    
    def exportAnim(self, exportPath, **kwargs):
        """
        Export the main scene animation nodes and animation helper nodes from all referenced objects. This flag, when used in conjunction with the -rfn/referenceNode flag, can be constrained to only export animation nodes from the specified reference file. See -ean/exportAnim flag description for details on usage of animation files.                  
        
        Flags:
          - force:
              Force an action to take place. (new, open, save, remove reference, unload reference) Used with removeReference to force
              remove reference namespace even if it has contents. Cannot be used with removeReference if the reference resides in the
              root namespace. Used with unloadReference to force unload reference even if the reference node is locked, without
              prompting a dialog that warns user about the lost of edits.
          - referenceNode:
              This flag is only used during queries. In MEL, if it appears before -query then it must be followed by the name of one
              of the scene's reference nodes. That will determine the reference to be queried by whatever flags appear after -query.
              If the named reference node does not exist within the scene the command will fail with an error. In Python the
              equivalent behavior is obtained by passing the name of the reference node as the flag's value. In MEL, if this flag
              appears after -query then it takes no argument and will cause the command to return the name of the reference node
              associated with the file given as the command's argument. If the file is not a reference or for some reason does not
              have a reference node (e.g., the user deleted it) then an empty string will be returned. If the file is not part of the
              current scene then the command will fail with an error. In Python the equivalent behavior is obtained by passing True as
              the flag's value.       In query mode, this flag can accept a value.
          - type:
              Set the type of this file.  By default this can be any one of: mayaAscii, mayaBinary, mel,  OBJ, directory, plug-in,
              audio, move, EPS, Adobe(R) Illustrator(R), imageplug-ins may define their own types as well.Return a string array of
              file types that match this file.
        
        Derived from mel command `maya.cmds.file`
        """
    
        pass
    
    
    def exportSelectedAnim(self, exportPath, **kwargs):
        """
        Export the main scene animation nodes and animation helper nodes from the selected referenced objects. This flag, when used in conjunction with the -rfn/referenceNode flag, can be constrained to only export animation nodes from the selected nodes of a specified reference file. See -ean/exportAnim flag description for details on usage of animation files.                  
        
        Flags:
          - force:
              Force an action to take place. (new, open, save, remove reference, unload reference) Used with removeReference to force
              remove reference namespace even if it has contents. Cannot be used with removeReference if the reference resides in the
              root namespace. Used with unloadReference to force unload reference even if the reference node is locked, without
              prompting a dialog that warns user about the lost of edits.
          - referenceNode:
              This flag is only used during queries. In MEL, if it appears before -query then it must be followed by the name of one
              of the scene's reference nodes. That will determine the reference to be queried by whatever flags appear after -query.
              If the named reference node does not exist within the scene the command will fail with an error. In Python the
              equivalent behavior is obtained by passing the name of the reference node as the flag's value. In MEL, if this flag
              appears after -query then it takes no argument and will cause the command to return the name of the reference node
              associated with the file given as the command's argument. If the file is not a reference or for some reason does not
              have a reference node (e.g., the user deleted it) then an empty string will be returned. If the file is not part of the
              current scene then the command will fail with an error. In Python the equivalent behavior is obtained by passing True as
              the flag's value.       In query mode, this flag can accept a value.
          - type:
              Set the type of this file.  By default this can be any one of: mayaAscii, mayaBinary, mel,  OBJ, directory, plug-in,
              audio, move, EPS, Adobe(R) Illustrator(R), imageplug-ins may define their own types as well.Return a string array of
              file types that match this file.
        
        Derived from mel command `maya.cmds.file`
        """
    
        pass
    
    
    def getReferenceEdits(self, **kwargs):
        """
        Get a list of ReferenceEdit objects for this node
        
        Adapted from:
        referenceQuery -editString -onReferenceNode <self.refNode>
        
        Notes
        -----
        By default, removes all edits. If neither of successfulEdits or
        failedEdits is given, they both default to True. If only one is given,
        the other defaults to the opposite value.
        """
    
        pass
    
    
    def importContents(self, removeNamespace=False):
        """
        Remove the encapsulation of the reference around the data within the specified file.    This makes the contents of the specified file part of the current scene and all references to the original file are lost. Returns the name of the reference that was imported.                  
        
        
        Derived from mel command `maya.cmds.file`
        """
    
        pass
    
    
    def isDeferred(self):
        """
        When used in conjunction with the -reference flag, this flag determines if the reference is loaded, or if loading is deferred.C: The default is false.Q: When queried, this flag returns true if the reference is deferred, or false if the reference is not deferred. If this is used with -rfn/referenceNode, the -rfn flag must come before -q.                  
        
        
        Derived from mel command `maya.cmds.file`
        """
    
        pass
    
    
    def isLoaded(self):
        """
        When used in conjunction with the -reference flag, this flag determines if the reference is loaded, or if loading is deferred.C: The default is false.Q: When queried, this flag returns true if the reference is deferred, or false if the reference is not deferred. If this is used with -rfn/referenceNode, the -rfn flag must come before -q.                  
        
        
        Derived from mel command `maya.cmds.file`
        """
    
        pass
    
    
    def isUsingNamespaces(self):
        """
        Returns boolean. Queries whether the specified reference file uses namespaces or renaming prefixes.                  
        
        
        Derived from mel command `maya.cmds.file`
        """
    
        pass
    
    
    def load(self, newFile=None, **kwargs):
        """
        This flag loads a file and associates it with the passed reference node. If the reference node does not exist, the command will fail. If the file is already loaded, then this flag will reload the same file.If a file is not given, the command will load (or reload) the last used reference file. 
        
        Flags:
          - loadNoReferences:
              This flag is obsolete and has been replaced witht the loadReferenceDepth flag. When used with the -open flag, no
              references will be loaded. When used with -i/import, -r/reference or -lr/loadReference flags, will load the top-most
              reference only.
          - loadReferenceDepth:
              Used to specify which references should be loaded. Valid types are all, noneand topOnly, which will load all references,
              no references and top-level references only, respectively. May only be used with the -o/open, -i/import, -r/reference or
              -lr/loadReference flags. When noneis used with -lr/loadReference, only path validation is performed. This can be used to
              replace a reference without triggering reload. Not using loadReferenceDepth will load references in the same loaded or
              unloaded state that they were in when the file was saved. Additionally, the -lr/loadReference flag supports a fourth
              type, asPrefs. This will force any nested references to be loaded according to the state (if any) stored in the current
              scene file, rather than according to the state saved in the reference file itself.
          - returnNewNodes:
              Used to control the return value in open, import, loadReference, and reference operations. It will force the file
              command to return a list of new nodes added to the current scene.
        
        Derived from mel command `maya.cmds.file`
        """
    
        pass
    
    
    def lock(self):
        """
        Locks attributes and nodes from the referenced file.                  
        
        
        Derived from mel command `maya.cmds.file`
        """
    
        pass
    
    
    def namespaceExists(self):
        """
        Returns true if the specified namespace exists, false if not.                  
        
        
        Derived from mel command `maya.cmds.namespace`
        """
    
        pass
    
    
    def nodes(self):
        """
        Returns string array. A main flag used to query the contents of the target reference.                              
        
        
        Derived from mel command `maya.cmds.referenceQuery`
        """
    
        pass
    
    
    def parent(self):
        """
        Returns the parent FileReference object, or None
        """
    
        pass
    
    
    def remove(self):
        """
        Remove the given file reference from its parent. This will also Remove everything this file references. Returns the name of the file removed. If the reference is alone in its namespace, remove the namespace. If there are objects remaining in the namespace after the file reference is removed, by default, keep the remaining objects in the namespace. To merge the objects remaining in the namespace to the parent or root namespace, use flags mergeNamespaceWithParent or mergeNamespaceWithRoot. The empty file reference namespace is then removed. To forcibly delete all objects, use flag force. The empty file reference namespace is then removed.                  
        
        
        Derived from mel command `maya.cmds.file`
        """
    
        pass
    
    
    def removeReferenceEdits(self, editCommand=None, force=False, **kwargs):
        """
        Remove edits from the reference.
        
        Parameters
        ----------
        editCommand : str
            If specified, remove only edits of a particular type: addAttr,
            setAttr, connectAttr, disconnectAttr or parent
        force : bool
            Unload the reference if it is not unloaded already
        successfulEdits : bool
            Whether to remove successful edits
        failedEdits : bool
            Whether to remove failed edits
        
        Notes
        -----
        By default, removes all edits. If neither of successfulEdits or
        failedEdits is given, they both default to True. If only one is given,
        the other defaults to the opposite value. This will only succeed on
        unapplied edits (ie, on unloaded nodes, or failed edits)... However,
        like maya.cmds.file/maya.cmds.referenceEdit, no error will be raised
        if there are no unapplied edits to work on. This may change in the
        future, however...
        """
    
        pass
    
    
    def replaceWith(self, newFile, **kwargs):
        """
        This flag loads a file and associates it with the passed reference node. If the reference node does not exist, the command will fail. If the file is already loaded, then this flag will reload the same file.If a file is not given, the command will load (or reload) the last used reference file. 
        
        Flags:
          - loadNoReferences:
              This flag is obsolete and has been replaced witht the loadReferenceDepth flag. When used with the -open flag, no
              references will be loaded. When used with -i/import, -r/reference or -lr/loadReference flags, will load the top-most
              reference only.
          - loadReferenceDepth:
              Used to specify which references should be loaded. Valid types are all, noneand topOnly, which will load all references,
              no references and top-level references only, respectively. May only be used with the -o/open, -i/import, -r/reference or
              -lr/loadReference flags. When noneis used with -lr/loadReference, only path validation is performed. This can be used to
              replace a reference without triggering reload. Not using loadReferenceDepth will load references in the same loaded or
              unloaded state that they were in when the file was saved. Additionally, the -lr/loadReference flag supports a fourth
              type, asPrefs. This will force any nested references to be loaded according to the state (if any) stored in the current
              scene file, rather than according to the state saved in the reference file itself.
          - returnNewNodes:
              Used to control the return value in open, import, loadReference, and reference operations. It will force the file
              command to return a list of new nodes added to the current scene.
        
        Derived from mel command `maya.cmds.file`
        """
    
        pass
    
    
    def selectAll(self):
        """
        Select all the components of this file as well as its child files.  Note that the file specified must be one that is already opened in this Maya session. The default behavior is to replace the existing selection. Use with the addflag to keep the active selection list.                  
        
        
        Derived from mel command `maya.cmds.file`
        """
    
        pass
    
    
    def subReferences(self):
        pass
    
    
    def unload(self):
        """
        This flag will unload the reference file associated with the passed reference node.                  
        
        
        Derived from mel command `maya.cmds.file`
        """
    
        pass
    
    
    def unlock(self):
        """
        Locks attributes and nodes from the referenced file.                  
        
        
        Derived from mel command `maya.cmds.file`
        """
    
        pass
    
    
    def unresolvedPath(self):
        pass
    
    
    def withCopyNumber(self):
        """
        return the path with the copy number at the end
        """
    
        pass
    
    
    __dict__ = None
    
    __weakref__ = None
    
    fullNamespace = None
    
    namespace = None
    
    path = None
    
    refNode = None


class _Mapping(_Sized, _Iterable, _Container):
    """
    A Mapping is a generic container for associating key/value
    pairs.
    
    This class provides concrete generic implementations of all
    methods except for __getitem__, __iter__, and __len__.
    """
    
    
    
    def __contains__(self, key):
        pass
    
    
    def __eq__(self, other):
        pass
    
    
    def __getitem__(self, key):
        pass
    
    
    def __ne__(self, other):
        pass
    
    
    def get(self, key, default=None):
        """
        D.get(k[,d]) -> D[k] if k in D, else d.  d defaults to None.
        """
    
        pass
    
    
    def items(self):
        """
        D.items() -> list of D's (key, value) pairs, as 2-tuples
        """
    
        pass
    
    
    def iteritems(self):
        """
        D.iteritems() -> an iterator over the (key, value) items of D
        """
    
        pass
    
    
    def iterkeys(self):
        """
        D.iterkeys() -> an iterator over the keys of D
        """
    
        pass
    
    
    def itervalues(self):
        """
        D.itervalues() -> an iterator over the values of D
        """
    
        pass
    
    
    def keys(self):
        """
        D.keys() -> list of D's keys
        """
    
        pass
    
    
    def values(self):
        """
        D.values() -> list of D's values
        """
    
        pass
    
    
    __abstractmethods__ = frozenset()
    
    
    __hash__ = None


class _MutableMapping(_Mapping):
    """
    A MutableMapping is a generic container for associating
    key/value pairs.
    
    This class provides concrete generic implementations of all
    methods except for __getitem__, __setitem__, __delitem__,
    __iter__, and __len__.
    """
    
    
    
    def __delitem__(self, key):
        pass
    
    
    def __setitem__(self, key, value):
        pass
    
    
    def clear(self):
        """
        D.clear() -> None.  Remove all items from D.
        """
    
        pass
    
    
    def pop(self, key, default='<object object>'):
        """
        D.pop(k[,d]) -> v, remove specified key and return the corresponding value.
        If key is not found, d is returned if given, otherwise KeyError is raised.
        """
    
        pass
    
    
    def popitem(self):
        """
        D.popitem() -> (k, v), remove and return some (key, value) pair
        as a 2-tuple; but raise KeyError if D is empty.
        """
    
        pass
    
    
    def setdefault(self, key, default=None):
        """
        D.setdefault(k[,d]) -> D.get(k,d), also set D[k]=d if k not in D
        """
    
        pass
    
    
    def update(*args, **kwds):
        """
        D.update([E, ]**F) -> None.  Update D from mapping/iterable E and F.
        If E present and has a .keys() method, does:     for k in E: D[k] = E[k]
        If E present and lacks .keys() method, does:     for (k, v) in E: D[k] = v
        In either case, this is followed by: for k, v in F.items(): D[k] = v
        """
    
        pass
    
    
    __abstractmethods__ = frozenset()


class FileInfo(_MutableMapping):
    """
    store and get custom data specific to this file:
    
        >>> from pymel.all import *
        >>> fileInfo['lastUser'] = env.user()
    
    if the python structures have valid __repr__ functions, you can
    store them and reuse them later:
    
        >>> fileInfo['cameras'] = str( ls( cameras=1) )
        >>> camList = eval(fileInfo['cameras'])
        >>> camList[0]
        nt.Camera(u'frontShape')
    
    for backward compatibility it retains it's original syntax as well:
    
        >>> fileInfo( 'myKey', 'myData' )
    
    Updated to have a fully functional dictiony interface.
    """
    
    
    
    def __call__(self, *args, **kwargs):
        pass
    
    
    def __delitem__(self, item):
        pass
    
    
    def __getitem__(self, item):
        pass
    
    
    def __init__(self, *p, **k):
        pass
    
    
    def __iter__(self):
        pass
    
    
    def __len__(self):
        pass
    
    
    def __setitem__(self, item, value):
        pass
    
    
    def has_key(self, key):
        pass
    
    
    def items(self):
        pass
    
    
    def keys(self):
        pass
    
    
    def __new__(cls, *p, **k):
        """
        # redefine __new__
        """
    
        pass
    
    
    __abstractmethods__ = frozenset()



def loadReference(filepath, **kwargs):
    """
    This flag loads a file and associates it with the passed reference node. If the reference node does not exist, the command will fail. If the file is already loaded, then this flag will reload the same file.If a file is not given, the command will load (or reload) the last used reference file. 
    
    Flags:
      - loadNoReferences:
          This flag is obsolete and has been replaced witht the loadReferenceDepth flag. When used with the -open flag, no
          references will be loaded. When used with -i/import, -r/reference or -lr/loadReference flags, will load the top-most
          reference only.
      - loadReferenceDepth:
          Used to specify which references should be loaded. Valid types are all, noneand topOnly, which will load all references,
          no references and top-level references only, respectively. May only be used with the -o/open, -i/import, -r/reference or
          -lr/loadReference flags. When noneis used with -lr/loadReference, only path validation is performed. This can be used to
          replace a reference without triggering reload. Not using loadReferenceDepth will load references in the same loaded or
          unloaded state that they were in when the file was saved. Additionally, the -lr/loadReference flag supports a fourth
          type, asPrefs. This will force any nested references to be loaded according to the state (if any) stored in the current
          scene file, rather than according to the state saved in the reference file itself.
      - returnNewNodes:
          Used to control the return value in open, import, loadReference, and reference operations. It will force the file
          command to return a list of new nodes added to the current scene.
    
    Derived from mel command `maya.cmds.file`
    """

    pass


def renameFile(newname, *args, **kwargs):
    """
    Rename the scene. Used mostly during save to set the saveAs name. Returns the new name of the scene.                  
    
    
    Derived from mel command `maya.cmds.file`
    """

    pass


def openGLExtension(*args, **kwargs):
    """
    Command returns the extension name depending on whether a given OpenGL extension is supported or not. The input is the
    extension string to the -extension flag. If the -extension flag is not used, or if the string argument to this flag is
    an empty string than all extension names are returned in a single string. If the extension exists it is not necessary
    true that the extension is supported. This command can only be used when a modeling view has been created. Otherwise no
    extensions will have been initialized and the resulting string will always be the empty string.
    
    Flags:
      - extension : ext                (unicode)       [create]
          Specifies the OpenGL extension to query.
    
      - renderer : rnd                 (bool)          [create]
          Specifies to query the OpenGL renderer.
    
      - vendor : vnd                   (bool)          [create]
          Specifies to query the company responsible for the OpenGL implementation.
    
      - version : ver                  (bool)          [create]
          Specifies to query the OpenGL version.                             Flag can have multiple arguments, passed either as a
          tuple or a list.
    
    
    Derived from mel command `maya.cmds.openGLExtension`
    """

    pass


def dbtrace(*args, **kwargs):
    """
    The dbtracecommand is used to manipulate trace objects.           The keyword is the only mandatory argument, indicating
    which trace           object is to be altered.           Trace Objects to affect (keywordKEY)Optional filtering criteria
    (filterFILTER)Function (off, outputFILE, mark, titleTITLE, timed: default operation is to enable traces)You can use the
    query mode to find out which keywords are currently           active (query with no arguments) or inactive (query with
    the offargument).           You can enhance that query with or without a keyword argument to find           out where
    their output is going (query with the outputargument), out what filters are currently applied (query with the
    filterargument), or if their output will be           timestamped (query with the timedargument).                 In
    query mode, return type is based on queried flag.
    
    Flags:
      - filter : f                     (unicode)       [create,query]
          Set the filter object for these trace objects (see 'dgfilter')
    
      - info : i                       (bool)          [query]
          In query mode return a brief description of the trace object.
    
      - keyword : k                    (unicode)       [create,query]
          Keyword of the trace objects to affect In query mode, this flag can accept a value.
    
      - mark : m                       (bool)          [create]
          Display a mark for all outputs of defined trace objects
    
      - off : boolean                  (Toggle the traces off.  If omitted it will turn them on.) [create]
    
      - output : o                     (unicode)       [create,query]
          Destination file of the affected trace objects.  Use the special names stdoutand stderrto redirect to your command
          window. The special name msdevis available on Windows to direct your output to the debug tab in the output window of
          Visual Studio.
    
      - timed : tm                     (bool)          [create,query]
          Turn on/off timing information in the output of the specified trace objects.
    
      - title : t                      (unicode)       [create]
          Display a title mark for all outputs of defined trace objects
    
      - verbose : v                    (bool)          [create]
          Include all traces in output and filter queries, not just those turned on.                                 Flag can have
          multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.dbtrace`
    """

    pass


def devicePanel(*args, **kwargs):
    """
    This command is now obsolete. It is included only for the purpose of file compatibility. It creates a blank panel.
    
    
    Derived from mel command `maya.cmds.devicePanel`
    """

    pass


def saveFile(**kwargs):
    """
    Save the specified file. Returns the name of the saved file.                  
    
    Flags:
      - force:
          Force an action to take place. (new, open, save, remove reference, unload reference) Used with removeReference to force
          remove reference namespace even if it has contents. Cannot be used with removeReference if the reference resides in the
          root namespace. Used with unloadReference to force unload reference even if the reference node is locked, without
          prompting a dialog that warns user about the lost of edits.
      - preSaveScript:
          When used with the save flag, the specified script will be executed before the file is saved.
      - postSaveScript:
          When used with the save flag, the specified script will be executed after the file is saved.
      - type:
          Set the type of this file.  By default this can be any one of: mayaAscii, mayaBinary, mel,  OBJ, directory, plug-in,
          audio, move, EPS, Adobe(R) Illustrator(R), imageplug-ins may define their own types as well.Return a string array of
          file types that match this file.
    
    Derived from mel command `maya.cmds.file`
    """

    pass


def openMayaPref(*args, **kwargs):
    """
    Set or query API preferences.
    
    Flags:
      - errlog : el                    (bool)          [create,query,edit]
          toggles whether or not an error log of failed API method calls will be created.  When set to true, a file called
          OpenMayaErrorLogwill be created in Maya's current working directory.  Each time an API method fails, a detailed
          description of the error will be written to the file along with a mini-stack trace that indicates the routine that
          called the failing method. Defaults to false(off).
    
      - lazyLoad : lz                  (bool)          [create,query,edit]
          toggles whether or not plugins will be loaded with the RTLD_NOW flag or the RTLD_LAZY flag of dlopen(3C).  If set to
          true, RTLD_LAZY will be used.  In this mode references to functions that cannot be resolved at load time will not be
          considered an error.  However, if one of these symbols is actually dereferenced by the plug-in at run time, Maya will
          crash. Defaults to false(off).
    
      - oldPluginWarning : ow          (bool)          [create,query,edit]
          toggles whether or not loadPlugin will generate a warning when plug-ins are loaded that were compiled against an older,
          and possibly incompatible Maya release. Defaults to true(on).                  Flag can have multiple arguments, passed
          either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.openMayaPref`
    """

    pass


def cacheFile(*args, **kwargs):
    """
    Creates one or more cache files on disk to store attribute data for a span of frames. The caches can be created for
    points/normals on a geometry (using the pts/points or pan/pointsAndNormals flag), for vectorArray output data (using the
    oa/outAttr flag), or for additional node specific data (using the cnd/cacheableNode flag for those nodes that support
    it). When the ia/inAttr flag is used, connects a cacheFile node that associates the data file on disk with the
    attribute. Frames can be replaced/appended to an existing cache with the rcf/replaceCachedFrame and apf/appendFrame
    flag.  Replaced frames are never deleted. They are stored in the same directory as the original cache files with the
    name provided by the f/fileName flag. If no file name is provided, the cacheFile name is prefixed with backupfollowed by
    a unique number. Single file caches are backed up in their entirety. To revert to an older version, simply attach to
    this cache. One file per frame caches only backup the description file and the frames that were replaced. To recover
    these types of caches, the user must rename these files to the original name.
    
    Flags:
      - appendFrame : apf              (bool)          [create]
          Appends data to the cache for the times specified by the startTime and endTime flags. If no time is provided, appends
          the current time. Must be used in conjunction with the pts/points or cnd/cacheableNode flag. Any overwritten frames will
          not be deleted, but renamed as specified by the f/fileName flag.
    
      - attachFile : af                (bool)          [create]
          Used to indicate that rather than creating a cache file, that an existing cache file on disk should be attached to an
          attribute in the scene. The inAttr flag is used to specify the attribute.
    
      - cacheFileNode : cfn            (unicode)       [create]
          Specifies the name of the cache file node(s) we are appending/replacing to if more than one cache is attached to the
          specified geometries.
    
      - cacheFormat : cf               (unicode)       [create,query]
          Cache file format, default is Maya's .mcx format, but others available via plugin
    
      - cacheInfo : ci                 (unicode)       [create,query]
          In create mode, used to specify a mel script returning a string array. When creating the cache, this mel script will be
          executed and the returned strings will be written to the .xml description file of the cache. In query mode, returns
          descriptive info stored in the cacheFile such as the user name, Maya scene name and maya version number.
    
      - cacheableAttrs : cat           (unicode)       [query]
          Returns the list of cacheable attributes defined on the accompanying cache node. This argument requires the use of the
          cacheableNode flag.
    
      - cacheableNode : cnd            (unicode)       [create]
          Specifies the name of a cacheable node whose contents will be cached. A cacheable node is a node that is specially
          designed to work with the caching mechanism.  An example of a cacheable node is a nCloth node.
    
      - channelIndex : chi             (bool)          [create,query]
          A query-only flag which returns the channel index for the selected geometry for the cacheFile node specified using the
          cacheFileNode flag.
    
      - channelName : cnm              (unicode)       [create,query]
          When attachFile is used, used to indicate the channel in the file that should be attached to inAttr.  If not specified,
          the first channel in the file is used. In query mode, allows user to query the channels associated with a description
          file.
    
      - convertPc2 : pc2               (bool)          [create]
          Convert a PC2 file to the Maya cache format (true), or convert Maya cache to pc2 format (false)
    
      - createCacheNode : ccn          (bool)          [create]
          Used to indicate that rather than creating a cache file, that a cacheFile node should be created related to an existing
          cache file on disk.
    
      - creationChannelName : cch      (unicode)       [create]
          When creating a new cache, this multi-use flag specifies the channels to be cached. The names come from the cacheable
          channel names defined by the object being cached. If this flag is not used when creating a cache, then all cacheable
          channels are cached.
    
      - dataSize : dsz                 (bool)          [query]
          This is a query-only flag that returns the size of the data being cached per frame. This flag is to be used in
          conjunction with the cacheableNode, points, pointsAndNormals and outAttr flags.
    
      - deleteCachedFrame : dcf        (bool)          [create]
          Deletes cached data for the times specified by the startTime/endTime flags. If no time is provided, deletes the current
          frame. Must be used in conjunction with the pts/points or cnd/cacheableNode flag. Deleted frames will not be removed
          from disk, but renamed as specified by the f/fileName flag.
    
      - descriptionFileName : dfn      (bool)          [query]
          This is a query-only flag that returns the name of the description file for an existing cacheFile node. Or if no
          cacheFile node is specified, it returns the description file name that would be created based on the other flags
          specified.
    
      - directory : dir                (unicode)       [create,query]
          Specifies the directory where the cache files will be located. If the directory flag is not specified, the cache files
          will be placed in the project data directory.
    
      - doubleToFloat : dtf            (bool)          [create]
          During cache creation, double data is stored in the file as floats.  This helps cut down file size.
    
      - endTime : et                   (time)          [create]
          Specifies the end frame of the cache range.
    
      - fileName : f                   (unicode)       [create,query]
          Specifies the base file name for the cache files. If more than one object is being cached and the format is
          OneFilePerFrame, each cache file will be prefixed with this base file name. In query mode, returns the files associated
          with the specified cacheFile node. When used with rpf/replaceCachedFrame or apf/appendFrame specifies the name of the
          backup files. If not specified, replaced frames will be stored with a default name. In query mode, this flag can accept
          a value.
    
      - format : fm                    (unicode)       [create]
          Specifies the distribution format of the cache.  Valid values are OneFileand OneFilePerFrame
    
      - geometry : gm                  (bool)          [query]
          A query flag which returns the geometry controlled by the specified cache node
    
      - inAttr : ia                    (unicode)       [create]
          Specifies the name of the attribute that the cache file will drive. This file is optional when creating cache files. If
          this flag is not used during create mode, the cache files will be created on disk, but will not be driving anything in
          the scene. This flag is required when the attachFile flag is used.
    
      - inTangent : it                 (unicode)       [create]
          Specifies the in-tangent type when interpolating frames before the replaced frame(s). Must be used with the
          ist/interpStartTime and iet/interpEndTime flags. Valid values are linear, smoothand step.
    
      - interpEndTime : iet            (time)          [create]
          Specifies the frame until which there will be linear interpolation, beginning at endTime. Must be used with the
          rpf/replaceCachedFrame or apf/appendFrame flag. Interpolation is achieved by removing frames between endTime and
          interpEndTime from the cache. Removed frames will be renamed as specified by the f/fileName flag.
    
      - interpStartTime : ist          (time)          [create]
          Specifies the frame from which to begin linear interpolation, ending at startTime. Must be used with the
          rpf/replaceCachedFrame or apf/appendFrame flags. Interpolation is achieved by removing  frames between interpStartTime
          and startTime from the cache. These removed frames will will be renamed as specified by the f/fileName flag.
    
      - noBackup : nb                  (bool)          [create]
          Specifies that backup files should not be created for any files that may be over-written during append, replace or
          delete cache frames. Can only be used with the apf/appendFrame, rpf/replaceCachedFrame or dcf/deleteCachedFrame flags.
    
      - outAttr : oa                   (unicode)       [create]
          Specifies the name of the attribute that will be cached to disk.
    
      - outTangent : ot                (unicode)       [create]
          Specifies the out-tangent type when interpolating frames after the replaced frame(s). Must be used with the
          ist/interpStartTime and iet/interpEndTime flags. Valid values are linear, smoothand step.
    
      - pc2File : pcf                  (unicode)       [create]
          Specifies the full path to the pc2 file.  Must be used in conjunction with the pc2 flag.
    
      - pointCount : pc                (bool)          [query]
          A query flag which returns the number of points stored in the cache file. The channelName flag should be used to specify
          the channel to be queried.
    
      - points : pts                   (unicode)       [create]
          Specifies the name of a geometry whose points will be cached.
    
      - pointsAndNormals : pan         (unicode)       [create]
          Specifies the name of a geometry whose points and normals will be cached. The normals is per-vertex per-polygon. The
          normals cache cannot be imported back to geometry. This flag can only be used to export cache file. It cannot be used
          with the apf/appendFrame, dcf/deleteCachedFrame and rpf/replaceCachedFrame flags.
    
      - prefix : p                     (bool)          [create]
          Indicates that the specified fileName should be used as a prefix for the cacheName.
    
      - refresh : r                    (bool)          [create]
          When used during cache creation, forces a screen refresh during caching. This causes the cache creation to be slower but
          allows you to see how the simulation is progressing during the cache.
    
      - replaceCachedFrame : rcf       (bool)          [create]
          Replaces cached data for the times specified by the startTime/endTime flags. If no time is provided, replaces cache file
          for the current time. Must be used in conjunction with the pts/points or cnd/cacheableNode flag. Replaced frames will
          not be deleted, but renamed as specified by the f/fileName flag.
    
      - replaceWithoutSimulating : rws (bool)          [edit]
          When replacing cached frames, this flag specifies whether the replacement should come from the cached node without
          simulating or from advancing time and letting the simulation run.  This flag is valid only when neither the startTime
          nor endTime flags are used or when both the startTime and endTime flags specify the same time value.
    
      - runupFrames : rf               (int)           [create,query,edit]
          Specifies the number of frames of runup to simulate ahead of the starting frame. The value must be greater than or equal
          to 0.  The default is 2.
    
      - sampleMultiplier : spm         (int)           [create,query,edit]
          Specifies the sample rate when caches are being created as a multiple of simulation Rate. If the value is 1, then a
          sample will be cached everytime the time is advanced.  If the value is 2, then every other sample will be cached, and so
          on.  The default is 1.
    
      - simulationRate : smr           (time)          [create,query,edit]
          Specifies the simulation rate when caches are being created.  During cache creation, the time will be advanced by the
          simulation rate, until the end time of the cache is reached or surpassed.  The value is given in frames. The default
          value is 1 frame.
    
      - singleCache : sch              (bool)          [create]
          When used in conjunction with the points, pointsAndNormal or cacheableNode flag, specifies whether multiple geometries
          should be put into a single cache or to create one cache per geometry (default).
    
      - startTime : st                 (time)          [create]
          Specifies the start frame of the cache range.
    
      - staticCache : sc               (bool)          [create,query]
          If false, during cache creation, do not save a cache for the object if it appears to have no animation or deformation.
          If true, save a cache even if the object appears to have no animation or deformation. Default is true. In query mode,
          when supplied a shape, the flag returns true if the shape appears to have no animation or deformation.
    
      - worldSpace : ws                (bool)          [create]
          If the points flag is used, turning on this flag will result in the world space positions of the points being written.
          The expected use of this flag is for cache export.                                  Flag can have multiple arguments,
          passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.cacheFile`
    """

    pass


def listInputDeviceButtons(*args, **kwargs):
    """
    This command lists all of the buttons of the specified input device specified as an argument.
    
    
    Derived from mel command `maya.cmds.listInputDeviceButtons`
    """

    pass


def loadModule(*args, **kwargs):
    """
    Maya plug-ins may be installed individually within one of Maya's standard plug-in directories, or they may be packaged
    up with other resources in a module. Each module resides in its own directory and provides a module definition file to
    make Maya aware of the plug-ins it provides. When Maya starts up it loads all of the module files it finds, making the
    module's plug-ins, scripts and other resources available for use. Note that the plug-ins themselves are not loaded at
    this time, Maya is simply made aware of them so that they can be loaded if needed. The loadModule command provides the
    ability to list and load any new modules which have been added since Maya started up, thereby avoiding the need to
    restart Maya before being able to use them.
    
    Flags:
      - allModules : a                 (bool)          [create]
          Load all new modules not yet loaded in Maya. New modules are the one returned by the -scan option.
    
      - load : ld                      (unicode)       [create]
          Load the module specified by the module definition file.
    
      - scan : sc                      (bool)          [create]
          Rescan module presence. Returns the list of module definition files found and not yet loaded into Maya. Does not load
          any of these newly found modules, nor change the Maya state.                                 Flag can have multiple
          arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.loadModule`
    """

    pass


def showHelp(*args, **kwargs):
    """
    Invokes a web browser to open the on-line documentation and help files. It will open the help page for a given topic, or
    open a browser to a specific URL.               In query mode, return type is based on queried flag.
    
    Flags:
      - absolute : a                   (bool)          [create]
          The specified URLis an absolute URL that should be passed directly to the web browser.
    
      - docs : d                       (bool)          [create,query]
          Use this flag to directly specify a help file relative to the on-line documentation root.
    
      - helpTable : ht                 (bool)          [create,query]
          Use this flag to specify which file will be used to search for help topics when the -d/docs and -a/absolute flags are
          not used. If only a file name is specified and not a path, then the file is assumed to be in the maya application
          directory.If this flag does not accept an argument if it is queried.The default value is helpTable.
    
      - version : v                    (bool)          [query]
          Use this flag to get the Maya version that the showHelp command uses.                              Flag can have
          multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.showHelp`
    """

    pass


def fileDialog(*args, **kwargs):
    """
    The fileBrowserDialog and fileDialog commands have now been deprecated. Both commands are still callable, but it is
    recommended that the fileDialog2 command be used instead.  To maintain some backwards compatibility, both
    fileBrowserDialog and fileDialog will convert the flags/values passed to them into the appropriate flags/values that the
    fileDialog2 command uses and will call that command internally.  It is not guaranteed that this compatibility will be
    able to be maintained in future versions so any new scripts that are written should use fileDialog2. See below for an
    example of how to change a script to use fileDialog2.
    
    Flags:
      - application : app              (bool)          [create]
          This is a Maconly flag. This brings up the dialog which selects only the application bundle.
    
      - defaultFileName : dfn          (unicode)       [create]
          Set default file name. This flag is available under writemode
    
      - directoryMask : dm             (unicode)       [create]
          This can be used to specify what directory and file names will be displayed in the dialog.  If not specified, the
          current directory will be used, with all files displayed. The string may contain a path name, and must contain a wild-
          carded file specifier. (eg \*.ccor /usr/u/\*) If just a path is specified, then the last directory in the path is taken
          to be a file specifier, and this will not produce the desired results.
    
      - mode : m                       (int)           [create]
          Defines the mode in which to run the file dialog: 0 for read1 for writeWrite mode can not be used in conjunction with
          the -application flag.
    
      - title : t                      (unicode)       [create]
          Set title text. The default value under writemode is Save As. The default value under readmode is Open.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.fileDialog`
    """

    pass


def listNamespaces(root=None, recursive=False, internal=False):
    """
    Returns a list of the namespaces in the scene
    """

    pass


def displayError(*args, **kwargs):
    pass


def listInputDevices(*args, **kwargs):
    """
    This command lists all input devices that maya knows about.
    
    
    Derived from mel command `maya.cmds.listInputDevices`
    """

    pass


def redo(*args, **kwargs):
    """
    Takes the most recently undone command from the undo list and redoes it.
    
    
    Derived from mel command `maya.cmds.redo`
    """

    pass


def hitTest(*args, **kwargs):
    """
    The hitTestcommand hit-tests a point in the named control and returns a list of items underneath the point. The point is
    specified in pixels with the origin (0,0) at the top-left corner. This position is compatible with the coordinates
    provided by a drop-callback. The types of items that may be returned depends upon the specific control; not all controls
    currently support hit-testing.
    
    
    Derived from mel command `maya.cmds.hitTest`
    """

    pass


def exportAsReference(exportPath, **kwargs):
    """
    Export the selected objects into a reference file with the given name. The file is saved on disk during the process. Returns the name of the reference created.                  
    
    Flags:
      - namespace:
          The namespace name to use that will group all objects during importing and referencing. Change the namespace used to
          group all the objects from the specified referenced file. The reference must have been created with the Using
          Namespacesoption, and must be loaded. Non-referenced nodes contained in the existing namespace will also be moved to the
          new namespace. The new namespace will be created by this command and can not already exist. The old namespace will be
          removed.
      - renamingPrefix:
          The string to use as a prefix for all objects from this file. This flag has been replaced by -ns/namespace.
    
    Derived from mel command `maya.cmds.file`
    """

    pass


def unknownPlugin(*args, **kwargs):
    """
    Allows querying of the unknown plug-ins used by the scene, and provides a means to remove them.
    
    Flags:
      - dataTypes : dt                 (bool)          [query]
          Returns the data types associated with the given unknown plug-in. This will always be empty for pre-Maya 2014 files.
    
      - list : l                       (bool)          [query]
          Lists the unknown plug-ins in the scene.
    
      - nodeTypes : nt                 (bool)          [query]
          Returns the node types associated with the given unknown plug-in. This will always be empty for pre-Maya 2014 files.
    
      - remove : r                     (bool)          [create]
          Removes the given unknown plug-in from the scene. For Maya 2014 files and onwards, this will fail if node or data types
          defined by the plug-in are still in use.
    
      - version : v                    (bool)          [query]
          Returns the version string of the given unknown plug-in.                  Flag can have multiple arguments, passed
          either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.unknownPlugin`
    """

    pass


def autoSave(*args, **kwargs):
    """
    Provides an interface to the auto-save mechanism.                In query mode, return type is based on queried flag.
    
    Flags:
      - destination : dst              (int)           [create,query]
          Sets the option for where auto-save files go. 0 - auto-saves go into the workspace autosave folder 1 - auto-saves go
          into the named folder (set with the -folder flag) 2 - auto-saves go into a folder set by an environment variable
          (MAYA_AUTOSAVE_FOLDER)
    
      - destinationFolder : df         (bool)          [query]
          Queries the actual destination folder for auto-saves, based on the current setting of the -destination flag, workspace
          rules and environment variables. Resolves environment variables etc. and makes any relative path absolute (resolved
          relative to the workspace root). The returned string will end with a trailing separator ('/').
    
      - enable : en                    (bool)          [create,query]
          Enables or disables auto-saves.
    
      - folder : fol                   (unicode)       [create,query]
          Sets the folder for auto-saves used if the destination option is 1.
    
      - interval : int                 (float)         [create,query]
          Sets the interval between auto-saves (in seconds). The default interval is 600 seconds (10 minutes).
    
      - limitBackups : lim             (bool)          [create,query]
          Sets whether the number of auto-save files is limited.
    
      - maxBackups : max               (int)           [create,query]
          Sets the maximum number of auto-save files, if limiting is in effect.
    
      - perform : p                    (bool)          [create]
          Invokes the auto-save process.
    
      - prompt : prm                   (bool)          [create,query]
          Sets whether the auto-save prompts the user before auto-saving.                  Flag can have multiple arguments,
          passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.autoSave`
    """

    pass


def sysFile(*args, **kwargs):
    """
    This command provides a system independent way to create a directory or to rename or delete a file.
    
    Flags:
      - copy : cp                      (unicode)       [create]
          Copy the file to the name given by the newFileName paramter.
    
      - delete : delete                (bool)          [create]
          Deletes the file.
    
      - makeDir : md                   (bool)          [create]
          Create the directory path given in the parameter. This will create the entire path if more than one directory needs to
          be created.
    
      - move : mov                     (unicode)       [create]
          Behaves identically to the -rename flag and remains for compatibility with old scripts
    
      - removeEmptyDir : red           (bool)          [create]
          Delete the directory path given in the parameter if the directory is empty. The command will not delete a directory
          which is not empty.
    
      - rename : ren                   (unicode)       [create]
          Rename the file to the name given by the newFileName parameter.                  Flag can have multiple arguments,
          passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.sysFile`
    """

    pass


def sceneName():
    """
    return the name of the current scene.                  
    
    
    Derived from mel command `maya.cmds.file`
    """

    pass


def date(*args, **kwargs):
    """
    Returns information about current time and date. Use the predefined formats, or the -formatflag to specify the output
    format.
    
    Flags:
      - date : d                       (bool)          [create]
          Returns the current date. Format is YYYY/MM/DD
    
      - format : f                     (unicode)       [create]
          Specifies a string defining how the date and time should be represented. All occurences of the keywords below will be
          replaced with the corresponding values: KeywordBecomesYYYYCurrent year, using 4 digitsYYLast two digits of the current
          yearMMCurrent month, with leading 0 if necessaryDDCurrent day, with leading 0 if necessaryhhCurrent hour, with leading 0
          if necessarymmCurrent minute, with leading 0 if necessaryssCurrent second, with leading 0 if necessary
    
      - shortDate : sd                 (bool)          [create]
          Returns the current date. Format is MM/DD
    
      - shortTime : st                 (bool)          [create]
          Returns the current time. Format is hh:mm
    
      - time : t                       (bool)          [create]
          Returns the current time. Format is hh:mm:ss                               Flag can have multiple arguments, passed
          either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.date`
    """

    pass


def unknownNode(*args, **kwargs):
    """
    Allows querying of the data stored for unknown nodes (nodes that are defined by a plug-in that Maya could not load when
    loading a scene file).
    
    Flags:
      - plugin : p                     (bool)          [query]
          In query mode return the name of the plug-in from which the unknown node originated. If no plug-in then the empty string
          is returned.
    
      - realClassName : rcn            (bool)          [query]
          Return the real class name of the node.
    
      - realClassTag : rct             (bool)          [query]
          Return the real class IFF tag of the node.                  Flag can have multiple arguments, passed either as a tuple
          or a list.
    
    
    Derived from mel command `maya.cmds.unknownNode`
    """

    pass


def pluginDisplayFilter(*args, **kwargs):
    """
    Register, deregister or query a plugin display filter. Plug-ins can use this command to register their own display
    filters which will appear in the 'Show' menus on Maya's model panels.
    
    Flags:
      - classification : cls           (unicode)       [create,query]
          The classification used to filter objects in Viewport 2.0. This classification is the same as MFnPlugin::registerNode().
          If the node was registered with multiple classifications, use the one beginning with drawdb. The default value of this
          flag is an empty string (). It will not filter any objects in Viewport 2.0.
    
      - deregister : dr                (bool)          [create]
          Deregister a plugin display filter.
    
      - exists : ex                    (unicode)       [create]
          Returns true if the specified filter exists, false otherwise. Other flags are ignored.
    
      - label : l                      (unicode)       [create,query]
          The string to be displayed for this filter in the UI. E.g. in the 'Show' menu of a model panel. The default value of
          this flag is the same as the plugin display filter name.
    
      - listFilters : lf               (bool)          [query]
          Returns an array of all plugin display filters.
    
      - register : r                   (bool)          [create]
          Register a plugin display filter. The -register is implied if both -register and -deregister flags are missing in create
          mode. You are responsible for deregistering any filters which you register. Filters are reference counted, meaning that
          if you register the same filter twice then you will have to deregister it twice as well.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.pluginDisplayFilter`
    """

    pass


def getFileList(*args, **kwargs):
    """
    Returns a list of files matching an optional wildcard pattern. Note that this command works directly on raw system files
    and does not go through standard Maya file path resolution.
    
    Flags:
      - filespec : fs                  (unicode)       [create]
          wildcard specifier for search.
    
      - folder : fld                   (unicode)       [create]
          return a directory listing                  Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.getFileList`
    """

    pass


def attachDeviceAttr(*args, **kwargs):
    """
    This command associates a device/axis pair with a node/attribute pair. When the device axis moves, the value of the
    attribute is set to the value of the axis. This value can be scaled and offset using the setAttrScale command. In query
    mode, return type is based on queried flag.
    
    Flags:
      - attribute : at                 (unicode)       [create]
          specify the attribute to attach to
    
      - axis : ax                      (unicode)       [create]
          specify the axis to attach from.
    
      - camera : cam                   (bool)          [create]
          This flag attaches the device/axis to the current camera. The mapping between device axes and camera controls is uses a
          heuristic based on the device descripton. The interaction is a copy of the mouse camera navigation controls.
    
      - cameraRotate : cr              (bool)          [create]
          This flag attaches the device/axis to the current cameras rotation controls.
    
      - cameraTranslate : ct           (bool)          [create]
          This flag attaches the device/axis to the current cameras translate controls.
    
      - clutch : c                     (unicode)       [create]
          specify a clutch button.  This button must be down for the command string to be executed. If no clutch is specified the
          command string is executed everytime the device state changes
    
      - device : d                     (unicode)       [create]
          specify which device to assign the command string.
    
      - selection : sl                 (bool)          [create]
          This flag attaches to the nodes in the selection list. This is different from the default arguments of the command since
          changing the selection will change the attachments.                  Flag can have multiple arguments, passed either as
          a tuple or a list.
    
    
    Derived from mel command `maya.cmds.attachDeviceAttr`
    """

    pass


def dgfilter(*args, **kwargs):
    """
    The dgfiltercommand is used to define Dependency Graph filters that select DG objects based on certain criteria.  The
    command itself can be used to filter objects or it can be attached to a dbtraceobject to selectively filter what output
    is traced. If objects are specified then apply the filter to those objects and return a boolean indicating whether they
    passed or not, otherwise return then name of the filter.  An invalid filter will pass all objects.  For multiple objects
    the return value is the logical ANDof all object's return values.
    
    Dynamic library stub function
    
    Flags:
      - attribute : atr                (unicode)       [create]
          Select objects whose attribute names match the pattern.
    
      - list : l                       (bool)          [create]
          List the available filters.  If used in conjunction with the -nameflag it will show a description of what the filter is.
    
      - logicalAnd : logicalAnd        (unicode, unicode) [create]
          Logical AND of two filters.
    
      - logicalNot : logicalNot        (unicode)       [create]
          Logical inverse of filter.
    
      - logicalOr : logicalOr          (unicode, unicode) [create]
          Logical OR of two filters.
    
      - name : n                       (unicode)       [create]
          Use filter named FILTER (or create new filter with that name). If no objects are specified then the name given to the
          filter will be returned.
    
      - node : nd                      (unicode)       [create]
          Select objects whose node names match the pattern.
    
      - nodeType : nt                  (unicode)       [create]
          Select objects whose node type names match the pattern.
    
      - plug : p                       (unicode)       [create]
          Select objects whose plug names match the pattern.                                 Flag can have multiple arguments,
          passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.dgfilter`
    """

    pass


def displayString(*args, **kwargs):
    """
    Assign a string value to a string identifier. Allows you define a string in one location and then refer to it by its
    identifier in many other locations. Formatted strings are also supported (NOTE however, this functionality is now
    provided in a more general fashion by the format command, use of format is recommended). You may embed up to 3 special
    character sequences ^1s, ^2s, and ^3s to perform automatic string replacement. The embedded characters will be replaced
    with the extra command arguments. See example section for more detail. Note the extra command arguments do not need to
    be display string identifiers.              In query mode, return type is based on queried flag.
    
    Flags:
      - delete : d                     (bool)          [create]
          This flag is used to remove an identifer string. The command will fail if the identifier does not exist.
    
      - exists : ex                    (bool)          [create]
          Returns true or false depending upon whether the specified identifier exists.
    
      - keys : k                       (bool)          [create,query]
          List all displayString keys that match the identifier string. The identifier string may be a whole or partial key
          string. The command will return a list of all identifier keys that contain this identifier string as a substring.
    
      - replace : r                    (bool)          [create,query]
          Since a displayString command will fail if it tries to assign a new value to an existing identifer, this flag is
          required to allow updates to the value of an already-existing identifier.  If the identifier does not already exist, a
          new identifier is added as if the -replace flag were not present.
    
      - value : v                      (unicode)       [create,query]
          The display string\'s value. If you do not specify this flag when creating a display string then the value will be the
          same as the identifier.                             Flag can have multiple arguments, passed either as a tuple or a
          list.
    
    
    Derived from mel command `maya.cmds.displayString`
    """

    pass


def findType(*args, **kwargs):
    """
    The findTypecommand is used to search through a dependency subgraph on a certain node to find all nodes of the given
    type. The search can go either upstream (input connections) or downstream (output connections). The plug/attribute
    dependencies are not taken into account when searching for matching nodes, only the connections.
    
    Flags:
      - deep : d                       (bool)          [create]
          Find all nodes of the given type instead of just the first.
    
      - exact : e                      (bool)          [create]
          Match node types exactly instead of any in a node hierarchy.
    
      - forward : f                    (bool)          [create]
          Look forwards (downstream) through the graph rather than backwards (upstream) for matching nodes.
    
      - type : t                       (unicode)       [create]
          Type of node to look for (e.g. transform). This flag is mandatory.                                 Flag can have
          multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.findType`
    """

    pass


def setInputDeviceMapping(*args, **kwargs):
    """
    The command sets a scale and offset for all attachments made to a specified device axis. Any attachment made to a mapped
    device axis will have the scale and offset applied to its values. The value from the device is multiplied by the scale
    and the offset is added to this product. With an absolute mapping, the attached attribute gets the resulting value. If
    the mapping is relative, the final value is the offset added to the scaled difference between the current device value
    and the previous device value. This mapping will be applied to the device data before any mappings defined by the
    setAttrMapping command. A typical use would be to scale a device's input so that it is within a usable range. For
    example, the device mapping can be used to calibrate a spaceball to work in a specific section of a scene. As an
    example, if the space ball is setup with absolute device mappings, constantly pressing in one direction will cause the
    attached attribute to get a constant value. If a relative mapping is used, and the spaceball is pressed in one
    direction, the attached attribute will jump a constantly increasing (or constantly decreasing) value and will find a
    rest value equal to the offset. There are important differences between how the relative flag is handled by this command
    and the setAttrMapping command. (See the setAttrMapping documentation for specifics on how it calculates relative
    values). In general, both a relative device mapping (this command) and a relative attachment mapping (setAttrMapping)
    should not be used together on the same axis.
    
    Flags:
      - absolute : a                   (bool)          [create]
          report absolute axis values
    
      - axis : ax                      (unicode)       [create]
          specify the axis to map
    
      - device : d                     (unicode)       [create]
          specify which device to map
    
      - offset : o                     (float)         [create]
          specify the axis offset value
    
      - relative : r                   (bool)          [create]
          report the change in axis value since the last sample
    
      - scale : s                      (float)         [create]
          specify the axis scale value
    
      - view : v                       (bool)          [create]
          translate the device coordinates into the coordinates of the active camera
    
      - world : w                      (bool)          [create]
          translate the device coordinates into world space coordinates                  Flag can have multiple arguments, passed
          either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.setInputDeviceMapping`
    """

    pass


def openFile(*args, **kwargs):
    """
    Open the specified file. Returns the name of the opened file.                  
    
    Flags:
      - loadAllDeferred:
          This flag is obsolete, and has been replaced by the loadReferenceDepth flag. When used with the -open flag, determines
          if the -deferReference flag is respected when reading in the file. If true is passed, all of the references are loaded.
          If false is passed, the -deferReference flag is respected.
      - loadNoReferences:
          This flag is obsolete and has been replaced witht the loadReferenceDepth flag. When used with the -open flag, no
          references will be loaded. When used with -i/import, -r/reference or -lr/loadReference flags, will load the top-most
          reference only.
      - loadReferenceDepth:
          Used to specify which references should be loaded. Valid types are all, noneand topOnly, which will load all references,
          no references and top-level references only, respectively. May only be used with the -o/open, -i/import, -r/reference or
          -lr/loadReference flags. When noneis used with -lr/loadReference, only path validation is performed. This can be used to
          replace a reference without triggering reload. Not using loadReferenceDepth will load references in the same loaded or
          unloaded state that they were in when the file was saved. Additionally, the -lr/loadReference flag supports a fourth
          type, asPrefs. This will force any nested references to be loaded according to the state (if any) stored in the current
          scene file, rather than according to the state saved in the reference file itself.
      - force:
          Force an action to take place. (new, open, save, remove reference, unload reference) Used with removeReference to force
          remove reference namespace even if it has contents. Cannot be used with removeReference if the reference resides in the
          root namespace. Used with unloadReference to force unload reference even if the reference node is locked, without
          prompting a dialog that warns user about the lost of edits.
      - returnNewNodes:
          Used to control the return value in open, import, loadReference, and reference operations. It will force the file
          command to return a list of new nodes added to the current scene.
      - type:
          Set the type of this file.  By default this can be any one of: mayaAscii, mayaBinary, mel,  OBJ, directory, plug-in,
          audio, move, EPS, Adobe(R) Illustrator(R), imageplug-ins may define their own types as well.Return a string array of
          file types that match this file.
    
    Derived from mel command `maya.cmds.file`
    """

    pass


def fileBrowserDialog(*args, **kwargs):
    """
    The fileBrowserDialog and fileDialog commands have now been deprecated. Both commands are still callable, but it is
    recommended that the fileDialog2 command be used instead.  To maintain some backwards compatibility, both
    fileBrowserDialog and fileDialog will convert the flags/values passed to them into the appropriate flags/values that the
    fileDialog2 command uses and will call that command internally.  It is not guaranteed that this compatibility will be
    able to be maintained in future versions so any new scripts that are written should use fileDialog2. See below for an
    example of how to change a script to use fileDialog2.
    
    Flags:
      - actionName : an                (unicode)       [create]
          Script to be called when the file is validated.
    
      - dialogStyle : ds               (int)           [create]
          0 for old style dialog1 for Windows 2000 style Explorer style2 for Explorer style with Shortcuttip at bottom
    
      - fileCommand : fc               (script)        [create]
          The script to run on command action
    
      - fileType : ft                  (unicode)       [create]
          Set the type of file to filter.  By default this can be any one of: mayaAscii, mayaBinary, mel, OBJ, directory, plug-in,
          audio, move, EPS, Illustrator, image. plug-ins may define their own types as well.
    
      - filterList : fl                (unicode)       [create]
          Specify file filters. Used with dialog style 1 and 2. Each string should be a description followed by a comma followed
          by a semi-colon separated list of file extensions with wildcard.
    
      - includeName : includeName      (unicode)       [create]
          Include the given string after the actionName in parentheses. If the name is too long, it will be shortened to fit on
          the dialog (for example, /usr/alias/commands/scripts/fileBrowser.mel might be shortened to /usr/...pts/fileBrowser.mel)
    
      - mode : m                       (int)           [create]
          Defines the mode in which to run the file brower: 0 for read1 for write2 for write without paths (segmented files)4 for
          directories have meaning when used with the action+100 for returning short names
    
      - operationMode : om             (unicode)       [create]
          Enables the option dialog. Valid strings are: ImportReferenceSaveAsExportAllExportActive
    
      - tipMessage : tm                (unicode)       [create]
          Message to be displayed at the bottom of the style 2 dialog box.
    
      - windowTitle : wt               (unicode)       [create]
          Set the window title of a style 1 or 2 dialog box                  Flag can have multiple arguments, passed either as a
          tuple or a list.
    
    
    Derived from mel command `maya.cmds.fileBrowserDialog`
    """

    pass


def convertUnit(*args, **kwargs):
    """
    This command converts values between different units of measure.  The command takes a string, because a string can
    incorporate unit names as well as values (see examples).
    
    Flags:
      - fromUnit : f                   (unicode)       [create]
          The unit to convert from.  If not supplied, it is assumed to be the system default.  The from unit may also be supplied
          as part of the value e.g. 11.2m (11.2 meters).
    
      - toUnit : t                     (unicode)       [create]
          The unit to convert to.  If not supplied, it is assumed to be the system default                  Flag can have multiple
          arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.convertUnit`
    """

    pass


def unassignInputDevice(*args, **kwargs):
    """
    This command deletes all command strings associated with this device. In query mode, return type is based on queried
    flag.
    
    Flags:
      - clutch : c                     (unicode)       [create]
          Only delete command attachments with this clutch.
    
      - device : d                     (unicode)       [create]
          Specifies the device to work on.                  Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.unassignInputDevice`
    """

    pass


def selLoadSettings(*args, **kwargs):
    """
    This command is used to edit and query information about the implicit load settings. Currently this is primarily
    intended for internal use within the Preload Reference Editor. selLoadSettings acts on load setting IDs. When implict
    load settings are built for a target scene, there will be one load setting for each reference in the target scene. Each
    load setting has a numerical ID which is its index in a pre-order traversal of the target reference hierarchy (with the
    root scenefile being assigned an ID of 0). Although the IDs are numerical they must be passed to the command as string
    array. Example: Given the scene: a        / \       b   c          / \         d   e where: a references b and c c
    references d and e the IDs will be as follows: a = 0 b = 1 c = 2 d = 3 e = 4 selLoadSettings can be used to change the
    load state of a reference: whether it will be loaded or unloaded (deferred) when the target scene is opened. Note:
    selLoadSettings can accept multiple command parameters, but the order must be selected carefully such that no reference
    is set to the loaded state while its parent is in the unlaoded state. Given the scene: a | b [-] | c [-] where: a
    references b b references c a = 0 b = 1 c = 2 and b and c are currently in the unloaded state. The following command
    will succeed and change both b and c to the loaded state: selLoadSettings -e -deferReference 0 12; whereas the following
    command will fail and leave both b and c in the unloaded state: selLoadSettings -e -deferReference 0 21; Bear in mind
    that the following command will also change both b and c to the loaded state: selLoadSettings -e -deferReference 0 1;
    This is because setting a reference to the loaded state automatically sets all child references to the loaded state as
    well. And vice versa, setting a reference the the unloaded state automatically sets all child reference to the unloaded
    state.
    
    Flags:
      - activeProxy : ap               (unicode)       [create,query,edit]
          Change or query the active proxy of a proxy set. In query mode, returns the proxyTag of the active proxy; in edit mode,
          finds the proxy in the proxySet with the given tag and makes it the active proxy.
    
      - deferReference : dr            (bool)          [create,query,edit]
          Change or query the load state of a reference.
    
      - fileName : fn                  (unicode)       [create,query]
          Return the file name reference file(s) associated with the indicated load setting(s).
    
      - numSettings : ns               (int)           [create,query]
          Return the number of settings in the group of implicit load settings. This is equivalent to number of references in the
          scene plus 1.
    
      - proxyManager : pm              (unicode)       [create,query]
          Return the name(s) of the proxy manager(s) associated with the indicated load setting(s).
    
      - proxySetFiles : psf            (unicode)       [create,query]
          Return the name(s) of the proxy(ies) available in the proxy set associated with the indicated load setting(s).
    
      - proxySetTags : pst             (unicode)       [create,query]
          Return the name(s) of the proxy tag(s) available in the proxy set associated with the indicated load setting(s).
    
      - proxyTag : pt                  (unicode)       [create,query]
          Return the name(s) of the proxy tag(s) associated with the indicated load setting(s).
    
      - referenceNode : rfn            (unicode)       [create,query]
          Return the name(s) of the reference node(s) associated with the indicated load setting(s).
    
      - shortName : shn                (bool)          [create,query]
          Formats the return value of the 'fileName' query flag to only return the short name(s) of the reference file(s).
    
      - unresolvedName : un            (bool)          [create,query]
          Formats the return value of the 'fileName' query flag to return the unresolved name(s) of the reference file(s). The
          unresolved file name is the file name used when the reference was created, whether or not that file actually exists on
          disk. When Maya encounters a file name which does not exist on disk it attempts to resolve the name by looking for the
          file in a number of other locations. By default the 'fileName' flag will return this resolved value.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.selLoadSettings`
    """

    pass


def getReferences(parentReference=None, recursive=False):
    pass


def undo(*args, **kwargs):
    """
    Takes the most recent command from the undo list and undoes it.
    
    
    Derived from mel command `maya.cmds.undo`
    """

    pass


def dynamicLoad(*args, **kwargs):
    """
    Dynamically load the DLL passed as argument.             In query mode, return type is based on queried flag.
    
    
    Derived from mel command `maya.cmds.dynamicLoad`
    """

    pass


def cacheFileTrack(*args, **kwargs):
    """
    This command is used for inserting and removing tracks related to the caches displayed in the trax editor. It can also
    be used to modify the track state, for example, to lock or mute a track.                  In query mode, return type is
    based on queried flag.
    
    Flags:
      - insertTrack : it               (int)           [create]
          This flag is used to insert a new empty track at the track index specified.
    
      - lock : l                       (bool)          [create,query,edit]
          This flag specifies whether clips on a track are to be locked or not.
    
      - mute : m                       (bool)          [create,query,edit]
          This flag specifies whether clips on a track are to be muted or not.
    
      - removeEmptyTracks : ret        (bool)          [create]
          This flag is used to remove all tracks that have no clips.
    
      - removeTrack : rt               (int)           [create]
          This flag is used to remove the track with the specified index.  The track must have no clips on it before it can be
          removed.
    
      - solo : so                      (bool)          [create,query,edit]
          This flag specifies whether clips on a track are to be soloed or not.
    
      - track : t                      (int)           [create,query,edit]
          Used to specify a new track index for a cache to be displayed. Track-indices are 1-based.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.cacheFileTrack`
    """

    pass


def referenceEdit(*args, **kwargs):
    """
    Use this command to remove and change the modifications which have been applied to references. A valid commandTarget is
    either a reference node, a reference file, a node in a reference, or a plug from a reference. Only modifications that
    have been made from the currently open scene can be changed or removed. The 'referenceQuery -topReference' command can
    be used to determine what modifications have been made to a given commandTarget. Additionally only unapplied edits will
    be affected. Edits are unapplied when the node(s) which they affect are unloaded, or when they could not be successfully
    applied. By default this command only works on failed edits (this can be adjusted using the -failedEditsand
    -successfulEditsflags). Specifying a reference node as the command target is equivalent to specifying every node in the
    target reference file as a target. In this situation the results may differ depending on whether the target reference is
    loaded or unloaded. When it is unloaded, edits that affect both a node in the target reference and a node in one of its
    descendant references may be missed (e.g. those edits may not be removed). This is because when a reference is unloaded
    Maya no longer retains detailed information about which nodes belong to it. However, edits that only affect nodes in the
    target reference or in one of its ancestral references should be removed as expected. When the flags -removeEdits and
    -editCommand are used together, by default all connectAttr edits are removed from the specified source object. To remove
    only edits that connect to a specific target object, the target object can be passed as an additional argument to the
    command. This narrows the match criteria, so that only edits that connect the source object to the provided target in
    this additional argument are removed. See the example below. NOTE: When specifying a plug it is important to use the
    appropriate long attribute name.
    
    Flags:
      - applyFailedEdits : afe         (bool)          [create]
          Attempts to apply any unapplied edits. This flag is useful if previously failing edits have been fixed using the
          -changeEditTarget flag. This flag can only be used on loaded references. If the command target is a referenced node, the
          associated reference is used instead.
    
      - changeEditTarget : cet         (unicode, unicode) [create]
          Used to change a target of the specified edits. This flag takes two parameters: the old target of the edits, and the new
          target to change it to. The target can either be a node name (node), a node and attribute name (node.attr), or just an
          attribute name (.attr). If an edit currently affects the old target, it will be changed to affect the new target. Flag
          'referenceQuery' should be used to determine the format of the edit targets. As an example most edits store the long
          name of the attribute (e.g. translateX), so when specifying the old target, a long name must also be used. If the short
          name is specified (e.g. tx), chances are the edit won't be retargeted.
    
      - editCommand : ec               (unicode)       [create,query]
          This is a secondary flag used to indicate which type of reference edits should be considered by the command. If this
          flag is not specified all edit types will be included. This flag requires a string parameter. Valid values are: addAttr,
          connectAttr, deleteAttr, disconnectAttr, parent, setAttr, lockand unlock. In some contexts, this flag may be specified
          more than once to specify multiple edit types to consider.
    
      - failedEdits : fld              (bool)          [create]
          This is a secondary flag used to indicate whether or not failed edits should be acted on (e.g. queried, removed,
          etc...). A failed edit is an edit which could not be successfully applied the last time its reference was loaded. An
          edit can fail for a variety of reasons (e.g. the referenced node to which it applies was removed from the referenced
          file). By default failed edits will be acted on.
    
      - onReferenceNode : orn          (unicode)       [create,query]
          This is a secondary flag used to indicate that only those edits which are stored on the indicated reference node should
          be considered. This flag only supports multiple uses when specified with the exportEditscommand.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
      - removeEdits : r                (bool)          [create]
          Remove edits which affect the specified unloaded commandTarget.
    
      - successfulEdits : scs          (bool)          [create]
          This is a secondary flag used to indicate whether or not successful edits should be acted on (e.g. queried, removed,
          etc...). A successful edit is any edit which was successfully applied the last time its reference was loaded. This flag
          will have no affect if the commandTarget is loaded. By default successful edits will not be acted on.
    
    
    Derived from mel command `maya.cmds.referenceEdit`
    """

    pass


def launch(*args, **kwargs):
    """
    Launch the appropriate application to open the document, web page or directory specified.
    
    Flags:
      - directory : dir                (unicode)       [create]
          A directory.
    
      - movie : mov                    (unicode)       [create]
          A movie file. The only acceptable movie file formats are MPEG, Quicktime, and Windows Media file. The file's name must
          end with .mpg, .mpeg, .mp4, .wmv, .mov, or .qt.
    
      - pdfFile : pdf                  (unicode)       [create]
          A PDF (Portable Document Format) document. The file's name must end with .pdf.
    
      - webPage : web                  (unicode)       [create]
          A web page.                  Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.launch`
    """

    pass


def undoInfo(*args, **kwargs):
    """
    This command controls the undo/redo parameters. In query mode, if invoked without flags (other than the query flag),
    this command will return the number of items currently on the undo queue.
    
    Flags:
      - chunkName : cn                 (unicode)       [create,query]
          Sets the name used to identify a chunk for undo/redo purposes when opening a chunk.
    
      - closeChunk : cck               (bool)          [create]
          Closes the chunk that was opened earlier by openChunk. Once close chunk is called, all undoable operations in the chunk
          will undo as a single undo operation. Use with CAUTION!! Improper use of this command can leave the undo queue in a bad
          state.
    
      - infinity : infinity            (bool)          [create,query]
          Set the queue length to infinity.
    
      - length : l                     (int)           [create,query]
          Specifies the maximum number of items in the undo queue. The infinity flag overrides this one.
    
      - openChunk : ock                (bool)          [create]
          Opens a chunk so that all undoable operations after this call will fall into the newly opened chunk, until close chunk
          is called. Once close chunk is called, all undoable operations in the chunk will undo as a single undo operation. Use
          with CAUTION!! Improper use of this command can leave the undo queue in a bad state.
    
      - printQueue : pq                (bool)          [query]
          Prints to the Script Editor the contents of the undo queue.
    
      - redoName : rn                  (unicode)       [query]
          Returns what will be redone (if anything)
    
      - redoQueueEmpty : rqe           (bool)          [query]
          Return true if the redo queue is empty. Return false if there is at least one command in the queue to be redone.
    
      - state : st                     (bool)          [create,query]
          Turns undo/redo on or off.
    
      - stateWithoutFlush : swf        (bool)          [create,query]
          Turns undo/redo on or off without flushing the queue. Use with CAUTION!! Note that if you  perform destructive
          operations while stateWithoutFlush is disabled, and you then enable it again, subsequent undo operations that try to go
          past the  destructive operations may be unstable since undo will not be able to properly reconstruct the former state of
          the scene.
    
      - undoName : un                  (unicode)       [query]
          Returns what will be undone (if anything)
    
      - undoQueueEmpty : uqe           (bool)          [query]
          Return true if the undo queue is empty. Return false if there is at least one command in the queue to be undone.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.undoInfo`
    """

    pass


def diskCache(*args, **kwargs):
    """
    Command to create, clear, or close disk cache(s).                In query mode, return type is based on queried flag.
    
    Flags:
      - append : a                     (bool)          [create,query]
          Append at the end and not to flush the existing cache
    
      - cacheType : ct                 (unicode)       [create,query]
          Specifies the type of cache to overwrite.  mcfpfor particle playback cache, mcfifor particle initial cache. mcjfor
          jiggle cache. This option is only activated during the cache creation.
    
      - close : c                      (unicode)       [create,query]
          Close the cache given the disk cache node name.  If -eco/enabledCachesOnly is trueonly enabled disk cache nodes are
          affected.
    
      - closeAll : ca                  (bool)          [create,query]
          Close all disk cache files. If -eco/enabledCachesOnly is trueonly enabled disk cache nodes are affected.
    
      - delete : d                     (unicode)       [create,query]
          Delete the cache given the disk cache node name.  If -eco/enabledCachesOnly is trueonly enabled disk cache nodes are
          affected.
    
      - deleteAll : da                 (bool)          [create,query]
          Delete all disk cache files.  If -eco/enabledCachesOnly is trueonly enabled disk cache nodes are affected.
    
      - empty : e                      (unicode)       [create,query]
          Clear the content of the disk cache with the given disk cache node name.  If -eco/enabledCachesOnly is trueonly enabled
          disk cache nodes are affected.
    
      - emptyAll : ea                  (bool)          [create,query]
          Clear the content of all disk caches.  If -eco/enabledCachesOnly is trueonly enabled disk cache nodes are affected.
    
      - enabledCachesOnly : eco        (bool)          [create,query]
          When present, this flag restricts the -ea/emptyAll, so that only enableddisk caches (i.e., disk cache nodes with the
          .enableattribute set to true) are affected.
    
      - endTime : et                   (time)          [create,query]
          Specifies the end frame of the cache range.
    
      - frameRangeType : frt           (unicode)       [create,query]
          Specifies the type of frame range to use, namely Render Globals, Time Slider, and Start/End.  In the case of Time
          Slider, startFrame and endFrame need to be specified.  (This flag is now obsolete.  Please use the -startTime and
          -endTime flags to specify the frame range explicitly.)
    
      - overSample : os                (bool)          [create,query]
          Over sample if true. Otherwise, under sample.
    
      - samplingRate : sr              (int)           [create,query]
          Specifies how frequently to sample relative to each frame. When over-sampling (-overSample has been specified), this
          parameter determines how many times per frame the runup will be evaluated. When under-sampling (the default, when
          -overSample has not been specified), the runup will evaluate only once per srframes, where sris the value specified to
          this flag.
    
      - startTime : st                 (time)          [create,query]
          Specifies the start frame of the cache range.
    
      - tempDir : tmp                  (bool)          [create,query]
          Query-only flag for the location of temporary diskCache files.                             Flag can have multiple
          arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.diskCache`
    """

    pass


def _setTypeKwargFromExtension(path, kwargs, mode='write'):
    pass


def profiler(*args, **kwargs):
    """
    The profiler is used to record timing information from key events within Maya, as an aid in tuning the performance of
    scenes, scripts and plug-ins. User written plug-ins and Python scripts can also generate profiling information for their
    own code through the MProfilingScope and MProfiler classes in the API. This command provides the ability to control the
    collection of profiling data and to query information about the recorded events. The recorded information can also be
    viewed graphically in the Profiler window. The buffer size cannot be changed while sampling is active, it will return an
    error The reset flag cannot be called while sampling is active, it will return an error. Any changes to the buffer size
    will only be applied on start of the next recording. You can't save and load in the same command, save has priority,
    load would be ignored.                In query mode, return type is based on queried flag.
    
    Flags:
      - addCategory : a                (unicode)       [create]
          Add a new category for the profiler. Returns the index of the new category.
    
      - allCategories : ac             (bool)          [query]
          Query the names of all categories
    
      - bufferSize : b                 (int)           [create,query]
          Toggled : change the buffer size to fit the specified number of events (requires that sampling is off) Query : return
          the current buffer size The new buffer size will only take effect when next sampling starts. When the buffer is full,
          the recording stops.
    
      - categoryIndex : ci             (int)           [create,query]
          Used in conjunction with other flags, to indicate the index of the category.
    
      - categoryIndexToName : cin      (int)           [create,query]
          Returns the name of the category with a given index.
    
      - categoryName : cn              (unicode)       [query]
          Used in conjunction with other flags, to indicate the name of the category.
    
      - categoryNameToIndex : cni      (unicode)       [create,query]
          Returns the index of the category with a given name.
    
      - categoryRecording : cr         (bool)          [create,query]
          Toggled : Enable/disable the recording of the category. Query : return if the recording of the category is On. Requires
          the -categoryIndex or -categoryName flag to specify the category to be queried.
    
      - clearAllMelInstrumentation : cam (bool)          [create]
          Clear all MEL command or procedure instrumentation.
    
      - colorIndex : coi               (int)           [create]
          Used with -instrumentMel trueto specify the color index to show the profiling result.
    
      - eventCPUId : eci               (bool)          [query]
          Query the CPU ID of the event at the given index. Requires the -eventIndex flag to specify the event to be queried.
    
      - eventCategory : eca            (bool)          [query]
          Query the category index the event at the given index belongs to. Requires the -eventIndex flag to specify the event to
          be queried.
    
      - eventColor : eco               (bool)          [query]
          Query the color of the event at the given index. Requires the -eventIndex flag to specify the event to be queried.
    
      - eventCount : ec                (bool)          [query]
          Query the number of events in the buffer
    
      - eventDescription : ed          (bool)          [query]
          Query the description of the event at the given index. Requires the -eventIndex flag to specify the event to be queried.
    
      - eventDuration : edu            (bool)          [query]
          Query the duration of the event at the given index, the time unit is microsecond. Note that a signal event has a 0
          duration. Requires the -eventIndex flag to specify the event to be queried.
    
      - eventIndex : ei                (int)           [query]
          Used usually in conjunction with other flags, to indicate the index of the event.
    
      - eventName : en                 (bool)          [query]
          Query the name of the event at the given index. Requires the -eventIndex flag to specify the event to be queried.
    
      - eventStartTime : et            (bool)          [query]
          Query the time of the event at the given index, the time unit is microsecond. Requires the -eventIndex flag to specify
          the event to be queried.
    
      - eventThreadId : eti            (bool)          [query]
          Query the thread ID of the event at the given index. Requires the -eventIndex flag to specify the event to be queried.
    
      - instrumentMel : instrumentMel  (bool)          [create]
          Enable/Diable the instrumentation of a MEL command or procedure. When the instrumentation is enabled, the execution of
          MEL command or procedure can be profiled and shown in the Profiler window. To enable the instrumentation requires the
          -procedureName, -colorIndex and -categoryIndex flags. To disable the instrumentation requires the -procedureName flag.
    
      - load : l                       (unicode)       [create,query]
          Read the recorded events from the specified file
    
      - output : o                     (unicode)       [create,query]
          Output the recorded events to the specified file
    
      - procedureDescription : pd      (unicode)       [create]
          Used with -instrumentMel trueto provide a description of the MEL command or procedure being instrumented. This
          description can be viewed in the Profiler Tool window.
    
      - procedureName : pn             (unicode)       [create]
          Used with -instrumentMel to specify the name of the procedure to be enabled/disabled the instrumentation.
    
      - removeCategory : rc            (unicode)       [create]
          Remove an existing category for the profiler. Returns the index of the removed category.
    
      - reset : r                      (bool)          [create,query]
          reset the profiler's data (requires that sampling is off)
    
      - sampling : s                   (bool)          [create,query]
          Toggled : Enable/disable the recording of events Query : return if the recording of events is On.
    
      - signalEvent : sig              (bool)          [query]
          Query if the event at the given index is a signal event. Requires the -eventIndex flag to specify the event to be
          queried. A Signal Event only remembers the start moment and has no knowledge about duration. It can be used in cases
          when the user does not care about the duration but only cares if this event does happen.
    
      - signalMelEvent : sim           (bool)          [create]
          Used with -instrumentMel true, inform profiler that this instrumented MEL command or procedure will be taken as a signal
          event during profiling. A Signal Event only remembers the start moment and has no knowledge about duration. It can be
          used in cases when the user does not care about the duration but only cares if this event does happen.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.profiler`
    """

    pass


def ogs(*args, **kwargs):
    """
    OGS is one of the viewport renderers. As there is a lot of effort involved in migrating functionality it will evolve
    over several releases. As it evolves it is prudent to provide safeguards to get the database back to a known state. That
    is the function of this command, similar to how 'dgdirty' is used to restore state to the dependency graph.
    
    Flags:
      - deviceInformation : di         (bool)          [create]
          If used then output the current device information.
    
      - disposeReleasableTextures : drt (bool)          [create]
          Clear up all the releasable file textures that are not required for rendering.
    
      - dumpTexture : dt               (unicode)       [create]
          If used then dump texture memory usage info (in MB), must be used with FLAG gpuMemoryUsed. The final info detail is
          specified by the string parameter. Current available values are: full, total.
    
      - enableHardwareInstancing : hwi (bool)          [create]
          Enables/disables new gpu instancing of instanceable render items in OGS.
    
      - fragmentEditor : fe            (unicode)       [create]
          If used then launch the fragment editor UI.
    
      - fragmentXML : xml              (unicode)       [create]
          Get the fragment XML associated with a shading node.
    
      - gpuMemoryUsed : gpu            (bool)          [create]
          If used then output the estimated amount of GPU memory in use (in MB).
    
      - pause : p                      (bool)          [create,query]
          Toggle pausing VP2 display update
    
      - rebakeTextures : rbt           (bool)          [create]
          If used then re-bake all baked textures for OGS.
    
      - regenerateUVTilePreview : rup  (unicode)       [create]
          If used then regenerate all UV tiles preview textures for OGS.
    
      - reloadTextures : rlt           (bool)          [create]
          If used then reload all textures for OGS.
    
      - reset : r                      (bool)          [create,query]
          If used then reset the entire OGS database for all viewports using it. In query mode the number of viewports that would
          be affected is returned but the reset is not actually done.  If no viewport is using OGS then OGS will stop listening to
          DG changes.
    
      - shaderSource : ss              (unicode)       [query]
          Get the shader source for the specified material.
    
      - toggleTexturePaging : ttp      (bool)          [create]
          If used then toggle the default OGS Texture paging mechanism.
    
      - traceRenderPipeline : trp      (bool)          [create]
          Enable debug tracing of the renderer pipeline.                             Flag can have multiple arguments, passed
          either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.ogs`
    """

    pass


def fileDialog2(*args, **kwargs):
    """
    This command provides a dialog that allows users to select files or directories.
    
    Flags:
      - buttonBoxOrientation : bbo     (int)           []
    
      - cancelCaption : cc             (unicode)       [create]
          If the dialogStyle flag is set to 2 then this provides a caption for the Cancel button within the dialog.
    
      - caption : cap                  (unicode)       [create]
          Provide a title for the dialog.
    
      - dialogStyle : ds               (int)           [create]
          1 On Windows or Mac OS X will use a native style file dialog.2 Use a custom file dialog with a style that is consistent
          across platforms.
    
      - fileFilter : ff                (unicode)       [create]
          Provide a list of file type filters to the dialog.  Multiple filters should be separated by double semi-colons.  See the
          examples section.
    
      - fileMode : fm                  (int)           [create]
          Indicate what the dialog is to return. 0 Any file, whether it exists or not.1 A single existing file.2 The name of a
          directory.  Both directories and files are displayed in the dialog.3 The name of a directory.  Only directories are
          displayed in the dialog.4 Then names of one or more existing files.
    
      - fileTypeChanged : ftc          (unicode)       [create]
          MEL only.  The string is interpreted as a MEL callback, to be called when the user-selected file type changes.  The
          callback is of the form: global proc MyCustomFileTypeChanged(string $parent, string $newType) The parent argument is the
          parent layout into which controls have been added using the optionsUICreate flag.  The newType argument is the new file
          type.
    
      - hideFileExtensions : hfe       (bool)          []
    
      - hideNameEdit : hne             (bool)          []
    
      - okCaption : okc                (unicode)       [create]
          If the dialogStyle flag is set to 2 then this provides a caption for the OK, or Accept, button within the dialog.
    
      - optionsUICancel : oca          (unicode)       [create]
          MEL only.  The string is interpreted as a MEL callback, to be called when the dialog is cancelled (with Cancel button or
          close button to close window). The callback is of the form: global proc MyCustomOptionsUICancel()
    
      - optionsUICommit : ocm          (unicode)       [create]
          MEL only.  The string is interpreted as a MEL callback, to be called when the dialog is successfully dismissed.  It will
          not be called if the user cancels the dialog, or closes the window using window title bar controls or other window
          system means.  The callback is of the form: global proc MyCustomOptionsUICommit(string $parent) The parent argument is
          the parent layout into which controls have been added using the optionsUICreate flag.
    
      - optionsUICommit2 : oc2         (unicode)       [create]
          MEL only.  As optionsUICommit, the given string is interpreted as a MEL callback, to be called when the dialog is
          successfully dismissed. The difference is that this callback takes one additional argument which is the file name
          selected by the user before the dialog validation. It will not be called if the user cancels the dialog, or closes the
          window using window title bar controls or other window system means.  The callback is of the form: global proc
          MyCustomOptionsUICommit(string $parent, string $selectedFile) The parent argument is the parent layout into which
          controls have been added using the optionsUICreate flag.
    
      - optionsUICreate : ocr          (bool)          [create]
          MEL only.  The string is interpreted as a MEL callback, to be called on creation of the file dialog.  The callback is of
          the form: global proc MyCustomOptionsUISetup(string $parent) The parent argument is the parent layout into which
          controls can be added.  This parent is the right-hand pane of the file dialog.
    
      - optionsUIInit : oin            (unicode)       [create]
          MEL only.  The string is interpreted as a MEL callback, to be called just after file dialog creation, to initialize
          controls.  The callback is of the form: global proc MyCustomOptionsUIInitValues(string $parent, string $filterType) The
          parent argument is the parent layout into which controls have been added using the optionsUICreate flag.  The filterType
          argument is the initial file filter.
    
      - returnFilter : rf              (bool)          [create]
          If true, the selected filter will be returned as the last item in the string array along with the selected files.
    
      - selectFileFilter : sff         (unicode)       [create]
          Specify the initial file filter to select.  Specify just the begining text and not the full wildcard spec.
    
      - selectionChanged : sc          (unicode)       [create]
          MEL only.  The string is interpreted as a MEL callback, to be called when the user changes the file selection in the
          file dialog.  The callback is of the form: global proc MyCustomSelectionChanged(string $parent, string $selection) The
          parent argument is the parent layout into which controls have been added using the optionsUICreate flag.  The selection
          argument is the full path to the newly-selected file.
    
      - setProjectBtnEnabled : spe     (bool)          []
    
      - startingDirectory : dir        (unicode)       [create]
          Provide the starting directory for the dialog.                  Flag can have multiple arguments, passed either as a
          tuple or a list.
    
    
    Derived from mel command `maya.cmds.fileDialog2`
    """

    pass


def launchImageEditor(*args, **kwargs):
    """
    Launch the appropriate application to edit/view the image files specified. This command works only on the Macintosh and
    Windows platforms.
    
    Flags:
      - editImageFile : eif            (unicode)       [create]
          If the file is a PSD, then the specified verison of Photoshop is launched, and the file is opened in it. If file is any
          other image type, then the preferred image editor is launched, and the file is opened in it.
    
      - viewImageFile : vif            (unicode)       [create]
          Opens up an Image editor to view images.                  Flag can have multiple arguments, passed either as a tuple or
          a list.
    
    
    Derived from mel command `maya.cmds.launchImageEditor`
    """

    pass


def getModulePath(*args, **kwargs):
    """
    Returns the module path for a given module name.
    
    Flags:
      - moduleName : mn                (unicode)       [create]
          The name of the module whose path you want to retrieve.                                    Flag can have multiple
          arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.getModulePath`
    """

    pass


def fcheck(*args, **kwargs):
    """
    Invokes the fcheck program to display images in a separate window.
    
    
    Derived from mel command `maya.cmds.fcheck`
    """

    pass


def pluginInfo(*args, **kwargs):
    """
    This command provides access to the plug-in registry of the application. It is used mainly to query the characteristics
    of registered plug-ins. Plugins automatically become registered the first time that they are loaded. The argument is
    either the internal name of the plug-in or the path to access it.
    
    Flags:
      - activeFile : af                (bool)          [query]
          Restricts the command to the active file only, not the entire scene. This only affects the -dependNode/-dn and
          -pluginsInUse/-pu flags. For use during export selected.
    
      - animCurveInterp : aci          (unicode)       [query]
          Returns a string array containing the names of all of the animation curve interpolators registered by this plug-in.
    
      - apiVersion : av                (bool)          [query]
          Returns a string containing the version of the API that this plug-in was compiled with.  See the comments in MTypes.h
          for the details on how to interpret this value.
    
      - autoload : a                   (bool)          [create,query,edit]
          Sets whether or not this plug-in should be loaded every time the application starts up. Returns a boolean in query mode.
    
      - cacheFormat : cf               (bool)          [query]
          Returns a string array containing the names of all of the registered geometry cache formats
    
      - changedCommand : cc            (script)        [create]
          Adds a callback that will get executed every time the plug-in registry changes. Any other previously registered
          callbacks will also get called.
    
      - command : c                    (unicode)       [query]
          Returns a string array containing the names of all of the normal commands registered by this plug-in. Constraint,
          control, context and model editor commands are not included.
    
      - constraintCommand : cnc        (unicode)       [query]
          Returns a string array containing the names of all of the constraint commands registered by this plug-in.
    
      - controlCommand : ctc           (unicode)       [query]
          Returns a string array containing the names of all of the control commands registered by this plug-in.
    
      - data : d                       (unicode, unicode) [query]
          Returns a string array containing the names of all of the data types registered by this plug-in.
    
      - dependNode : dn                (bool)          [query]
          Returns a string array containing the names of all of the custom nodes types registered by this plug-in.
    
      - dependNodeByType : dnt         (unicode)       [query]
          Returns a string array of all registered node types within a specified class of nodes.  Each custom node type registered
          by a plug-in belongs to a more general class of node types as specified by its MPxNode::Type. The flag's argument is an
          MPxNode::Type as a string.  For example, if you want to list all registered Locator nodes, you should specify
          kLocatorNode as a argument to this flag.
    
      - dependNodeId : dni             (unicode)       [query]
          Returns an integer array containing the ids of all of the custom node types registered by this plug-in.
    
      - device : dv                    (bool)          [query]
          Returns a string array containing the names of all of the devices registered by this plug-in.
    
      - dragAndDropBehavior : ddb      (bool)          [query]
          Returns a string array containing the names of all of the drag and drop behaviors registered by this plug-in.
    
      - iksolver : ik                  (bool)          [query]
          Returns a string array containing the names of all of the ik solvers registered by this plug-in.
    
      - listPlugins : ls               (bool)          [query]
          Returns a string array containing all the plug-ins that are currently loaded.
    
      - listPluginsPath : lsp          (bool)          [query]
          Returns a string array containing the full paths of all the plug-ins that are currently loaded.
    
      - loadPluginPrefs : lpp          (bool)          [create]
          Loads the plug-in preferences (ie. autoload) from pluginPrefs.mel into Maya.
    
      - loaded : l                     (bool)          [query]
          Returns a boolean specifying whether or not the plug-in is loaded.
    
      - modelEditorCommand : mec       (unicode)       [query]
          Returns a string array containing the names of all of the model editor commands registered by this plug-in.
    
      - name : n                       (unicode)       [query]
          Returns a string containing the internal name by which the plug-in is registered.
    
      - path : p                       (unicode)       [query]
          Returns a string containing the absolute path name to the plug-in.
    
      - pluginsInUse : pu              (bool)          [query]
          Returns a string array containing all the plug-ins that are currently being used in the scene.
    
      - registered : r                 (bool)          [query]
          Returns a boolean specifying whether or not plug-in is currently registered with the system.
    
      - remove : rm                    (bool)          [edit]
          Removes the given plug-in's record from the registry. There is no return value.
    
      - renderer : rdr                 (bool)          [query]
          Returns a string array containing the names of all of the renderers registered by this plug-in.
    
      - savePluginPrefs : spp          (bool)          [create]
          Saves the plug-in preferences (ie. autoload) out to pluginPrefs.mel
    
      - serviceDescriptions : sd       (bool)          [query]
          If there are services in use, then this flag will return a string array containing short descriptions saying what those
          services are.
    
      - settings : set                 (bool)          [query]
          Returns an array of values with the loaded, autoload, registered flags
    
      - tool : t                       (unicode)       [query]
          Returns a string array containing the names of all of the tool contexts registered by this plug-in.
    
      - translator : tr                (bool)          [query]
          Returns a string array containing the names of all of the file translators registered by this plug-in.
    
      - unloadOk : uo                  (bool)          [query]
          Returns a boolean that specifies whether or not the plug-in can be safely unloaded.  It will return false if the plug-in
          is currently in use.  For example, if the plug-in adds a new dependency node type, and an instance of that node type is
          present in the scene, then this query will return false.
    
      - userNamed : u                  (bool)          [query]
          Returns a boolean specifying whether or not the plug-in has been assigned a name by the user.
    
      - vendor : vd                    (unicode)       [query]
          Returns a string containing the vendor of the plug-in.
    
      - version : v                    (bool)          [query]
          Returns a string containing the version the plug-in.
    
      - writeRequires : wr             (bool)          [create,query,edit]
          Sets whether or not this plug-in should write requirescommand into the saved file. requirescommand could autoload the
          plug-in when you open or import that saved file. This way, Maya will load the plug-in when a file is being loaded for
          some specified reason, such as to create a customized UI or to load some plug-in data that is not saved in any node or
          attributes. For example, stereoCamerais using this flag for its customized UI.                  Flag can have multiple
          arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.pluginInfo`
    """

    pass


def dgdirty(*args, **kwargs):
    """
    The dgdirtycommand is used to force a dependency graph dirty message on a node or plug.  Used for debugging to find
    evaluation problems.  If no nodes are specified then the current selection list is used. If the listflag is used it will
    return the list of things currently marked as dirty (or clean if the cleanflag was also used). The returned values will
    be the names of plugs either clean/dirty themselves, at both ends of a clean/dirty connection, or representing the
    location of clean/dirty data on the node. Be careful using this option in conjunction with the allflag, the list could
    be huge.
    
    Flags:
      - allPlugs : a                   (bool)          [create,query]
          Ignore the selected or specified objects and dirty (or clean) all plugs.
    
      - clean : c                      (bool)          [create,query]
          If this flag is set then the attributes are cleaned.  Otherwise they are set to dirty.
    
      - implicit : i                   (bool)          [create,query]
          If this flag is set then allow the implicit or default nodes to be processed as well. Otherwise they will be skipped for
          efficiency.
    
      - list : l                       (unicode)       [create,query]
          When this flag is specified then instead of sending out dirty/clean messages the list of currently dirty/clean objects
          will be returned. The allPlugsand cleanflags are respected to narrow guide the values to be returned. The value of the
          flag tells what will be reported. dataor d= show plugs that have dirty/clean dataplugor p= show plugs that have
          dirty/clean statesconnectionor c= show plugs with connections that have dirty/clean statesQuery this flag to find all
          legal values of the flag. Query this flag with its value already set to get a description of what that value means. Note
          that pand cmodes are restricted to plugs that have connections or non-standard state information. Other attributes will
          not have state information to check, though they will have data. In the case of array attributes only the children that
          have values currently set will be considered. No attempt will be made to evaluate them in order to update the available
          child lists. e.g. if you have a DAG with transform T1 and shape S1 the instanced attribute S1.wm[0] will be reported. If
          in a script you create a second instance T2-S1 and immediately list the plugs again before evaluation you will still
          only see S1.wm[0]. The new S1.wm[1] won't be reported until it is created through an evaluation, usually caused by
          refresh, a specific getAttr command, or an editor update. Note that the list is only for selected nodes. Unlike when
          dirty messages are sent this does not travel downstream.
    
      - propagation : p                (bool)          [create,query]
          If this flag is set then the ability of dirty messages to flow through the graph is left enabled.
    
      - showTiming : st                (bool)          [create,query]
          If this flag is used then show how long the dirty messages took to propagate.
    
      - verbose : v                    (bool)          [create,query]
          Prints out all of the plugs being set dirty on stdout.                             Flag can have multiple arguments,
          passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.dgdirty`
    """

    pass


def timer(*args, **kwargs):
    """
    Allow simple timing of scripts and commands. The resolution of this timer is at the level of your OS's
    gettimeofday()function.  Note:This command does not handle stacked calls. For example, this code below will give an
    incorrect answer on the second timer -ecall.timer -s; timer -s; timer -e; timer -e; To do this use named timers: timer
    -s; timer -s -name innerTimer; timer -e -name innerTimer; timer -e; I the -e flag or -lap flag return the time elapsed
    since the last 'timer -s' call.I the -s flag has no return value.
    
    Flags:
      - endTimer : e                   (bool)          [create]
          Stop the timer and return the time elapsed since the timer was started (in seconds). Once a timer is turned off it no
          longer exists, though it can be recreated with a new start
    
      - lapTime : lap                  (bool)          [create]
          Get the lap time of the timer (time elapsed since start in seconds). Unlike the endflag this keeps the timer running.
    
      - name : n                       (unicode)       [create]
          Use a named timer for the operation. If this is omitted then the default timer is assumed.
    
      - startTimer : s                 (bool)          [create]
          Start the timer.                                   Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.timer`
    """

    pass


def exportAnimFromReference(exportPath, **kwargs):
    """
    Export the main scene animation nodes and animation helper nodes from all referenced objects. This flag, when used in conjunction with the -rfn/referenceNode flag, can be constrained to only export animation nodes from the specified reference file. See -ean/exportAnim flag description for details on usage of animation files.                  
    
    Flags:
      - force:
          Force an action to take place. (new, open, save, remove reference, unload reference) Used with removeReference to force
          remove reference namespace even if it has contents. Cannot be used with removeReference if the reference resides in the
          root namespace. Used with unloadReference to force unload reference even if the reference node is locked, without
          prompting a dialog that warns user about the lost of edits.
      - referenceNode:
          This flag is only used during queries. In MEL, if it appears before -query then it must be followed by the name of one
          of the scene's reference nodes. That will determine the reference to be queried by whatever flags appear after -query.
          If the named reference node does not exist within the scene the command will fail with an error. In Python the
          equivalent behavior is obtained by passing the name of the reference node as the flag's value. In MEL, if this flag
          appears after -query then it takes no argument and will cause the command to return the name of the reference node
          associated with the file given as the command's argument. If the file is not a reference or for some reason does not
          have a reference node (e.g., the user deleted it) then an empty string will be returned. If the file is not part of the
          current scene then the command will fail with an error. In Python the equivalent behavior is obtained by passing True as
          the flag's value.       In query mode, this flag can accept a value.
      - type:
          Set the type of this file.  By default this can be any one of: mayaAscii, mayaBinary, mel,  OBJ, directory, plug-in,
          audio, move, EPS, Adobe(R) Illustrator(R), imageplug-ins may define their own types as well.Return a string array of
          file types that match this file.
    
    Derived from mel command `maya.cmds.file`
    """

    pass


def exportEdits(*args, **kwargs):
    """
    Use this command to export edits made in the scene to a file. The exported file can be subsequently imported to another
    scene. Edits may include: nodes, connections and reference edits such as value changes. The nodes that are included in
    the exported file will be based on the options used. At least one option flag that describes the set of target nodes to
    include in the exported file must be specified (e.g. 'selected', 'onReferenceNode'). Use the inclusion flags
    ('includeAnimation', 'includeShaders', 'includeNetwork') to specify which additional related nodes will be added to the
    export list. In export mode, when the command completes successfully, the name of the exported file will be returned. In
    query mode, this command will return information about the contents of the exported file. The query mode will return the
    list of nodes that will be considered for inclusion in the exported file based on the specified flags.
    
    Flags:
      - editCommand : ec               (unicode)       [create,query]
          This is a secondary flag used to indicate which type of reference edits should be considered by the command. If this
          flag is not specified all edit types will be included. This flag requires a string parameter. Valid values are: addAttr,
          connectAttr, deleteAttr, disconnectAttr, parent, setAttr, lockand unlock. In some contexts, this flag may be specified
          more than once to specify multiple edit types to consider.
    
      - excludeHierarchy : ehr         (bool)          [create,query]
          By default, all DAG parents and DAG history are written to the export file. To prevent any DAG relations not otherwise
          connected to the target nodes to be included, specify the -excludeHierarchy flag.
    
      - excludeNode : en               (unicode)       [create,query]
          Prevent the node from being included in the list of nodes being exported. This flag is useful to exclude specific scene
          nodes that might otherwise be exported. In the case where more than one Maya node has the same name, the DAG path can be
          specified to uniquely identify the node.
    
      - exportSelected : exs           (bool)          [create,query]
          The selected nodes and their connections to each other will be exported. Additionally, any dangling connections to non-
          exported nodes will be exported. Default nodes are ignored and never exported. Note that when using the exportSelected
          flag, only selected nodes are exported, and -include/-exclude flags such as -includeHierarchy are ignored.
    
      - force : f                      (bool)          [create,query]
          Force the export action to take place. This flag is required to overwrite an existing file.
    
      - includeAnimation : ian         (bool)          [create,query]
          Additionally include animation nodes and animation helper nodes associated with the target nodes being exported.
    
      - includeConstraints : ic        (bool)          [create,query]
          Additionally include constraint-related nodes associated with the target nodes being exported.
    
      - includeDeformers : idf         (bool)          [create,query]
          Additionally include deformer networks associated with the target nodes being exported.
    
      - includeNetwork : inw           (bool)          [create,query]
          Additionally include the network of nodes connected to the target nodes being exported.
    
      - includeNode : includeNode      (unicode)       [create,query]
          Additionally include the named node in the list of nodes being exported. In the case where more than one Maya node has
          the same name, the DAG path can be specified to uniquely identify the node.
    
      - includeSetAttrs : isa          (bool)          [create,query]
          When using the -selected/-sel flag, if any of the selected nodes are referenced, also include/exclude any setAttr edits
          on those nodes. If used with the -onReferenceNode/-orn flag, include/exclude any setAttr edits on the reference.
    
      - includeSetDrivenKeys : sdk     (bool)          [create,query]
          Additionally include setDrivenKey-related nodes associated with the target nodes being exported.
    
      - includeShaders : ish           (bool)          [create,query]
          Additionally include shaders associated with the target nodes being exported.
    
      - onReferenceNode : orn          (unicode)       [create,query]
          This is a secondary flag used to indicate that only those edits which are stored on the indicated reference node should
          be considered. This flag only supports multiple uses when specified with the exportEditscommand.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
      - selected : sel                 (bool)          [create,query]
          Export will operate on the list of nodes currently selected. This flag differs from the exportSelected flag in that the
          selected nodes are not exported, only the edits on them, and any nodes found via the include flags that are used (such
          as includeAnimation, includeNetwork and so on).
    
      - type : typ                     (unicode)       [create,query]
          Set the type of the exported file. Valid values are editMAor editMB. Note that this command respects the global
          defaultExtensionssetting for file naming that is controlled with the file command defaultExtensions option.  See the
          file command for more information.
    
    
    Derived from mel command `maya.cmds.exportEdits`
    """

    pass


def rehash(*args, **kwargs):
    """
    Derived from mel command `maya.cmds.rehash`
    """

    pass


def exportSelected(exportPath, **kwargs):
    """
    Export the selected items into the specified file. Returns the name of the exported file.                  
    
    Flags:
      - force:
          Force an action to take place. (new, open, save, remove reference, unload reference) Used with removeReference to force
          remove reference namespace even if it has contents. Cannot be used with removeReference if the reference resides in the
          root namespace. Used with unloadReference to force unload reference even if the reference node is locked, without
          prompting a dialog that warns user about the lost of edits.
      - constructionHistory:
          For use with exportSelected to specify whether attached construction history should be included in the export.
      - channels:
          For use with exportSelected to specify whether attached channels should be included in the export.
      - constraints:
          For use with exportSelected to specify whether attached constraints should be included in the export.
      - expressions:
          For use with exportSelected to specify whether attached expressions should be included in the export.
      - shader:
          For use with exportSelected to specify whether attached shaders should be included in the export.
      - preserveReferences:
          Modifies the various import/export flags such that references are imported/exported as actual references rather than
          copies of those references.
      - type:
          Set the type of this file.  By default this can be any one of: mayaAscii, mayaBinary, mel,  OBJ, directory, plug-in,
          audio, move, EPS, Adobe(R) Illustrator(R), imageplug-ins may define their own types as well.Return a string array of
          file types that match this file.
    
    Derived from mel command `maya.cmds.file`
    """

    pass


def audioTrack(*args, **kwargs):
    """
    This command is used for inserting and removing tracks related to the audio clips displayed in the sequencer. It can
    also be used to modify the track state, for example, to lock or mute a track.               In query mode, return type
    is based on queried flag.
    
    Flags:
      - insertTrack : it               (int)           [create]
          This flag is used to insert a new empty track at the track index specified. Indices are 1-based.
    
      - lock : l                       (bool)          [create,query,edit]
          This flag specifies whether all audio clips on the same track as the specified audio node are to be locked at their
          current location and track.
    
      - mute : m                       (bool)          [create,query,edit]
          This flag specifies whether all audio clips on the same track as the specified audio node are to be muted or not.
    
      - numTracks : nt                 (int)           [query]
          To query the number of audio tracks
    
      - removeEmptyTracks : ret        (bool)          [create]
          This flag is used to remove all tracks that have no clips.
    
      - removeTrack : rt               (int)           [create]
          This flag is used to remove the track with the specified index.  The track must have no clips on it before it can be
          removed.
    
      - solo : so                      (bool)          [create,query,edit]
          This flag specifies whether all audio clips on the same track as the specified audio node are to be soloed or not.
    
      - swapTracks : st                (int, int)      [create]
          This flag is used to swap the contents of two specified tracks. Indices are 1-based.
    
      - title : t                      (unicode)       [create,query,edit]
          This flag specifies the title for the track.
    
      - track : tr                     (int)           [create,query,edit]
          Specify the track on which to operate by using the track's trackNumber. Flag can have multiple arguments, passed either
          as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.audioTrack`
    """

    pass


def moduleInfo(*args, **kwargs):
    """
    Returns information on modules found by Maya.
    
    Flags:
      - definition : d                 (bool)          [create]
          Returns module definition file name for the module specified by the -moduleName parameter.
    
      - listModules : lm               (bool)          [create]
          Returns an array containing the names of all currently loaded modules.
    
      - moduleName : mn                (unicode)       [create]
          The name of the module whose information you want to retrieve. Has to be used with either -definition / -path / -version
          flags.
    
      - path : p                       (bool)          [create]
          Returns the module path for the module specified by the -moduleName parameter.
    
      - version : v                    (bool)          [create]
          Returns the module version for the module specified by the -moduleName parameter.                                  Flag
          can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.moduleInfo`
    """

    pass


def recordAttr(*args, **kwargs):
    """
    This command sets up an attribute to be recorded.  When the record command is executed, any changes to this attribute
    are recorded.  When recording stops these changes are turned into keyframes. If no attributes are specified all
    attributes of the node are recorded. When the query flag is used, a list of the attributes being recorded will be
    returned. In query mode, return type is based on queried flag.
    
    Flags:
      - attribute : at                 (unicode)       [create]
          specify the attribute to record
    
      - delete : d                     (bool)          [create]
          Do not record the specified attributes                  Flag can have multiple arguments, passed either as a tuple or a
          list.
    
    
    Derived from mel command `maya.cmds.recordAttr`
    """

    pass


def saveAs(newname, **kwargs):
    pass


def sceneEditor(*args, **kwargs):
    """
    This creates an editor for managing the files in a scene.
    
    Flags:
      - control : ctl                  (bool)          [query]
          Query only. Returns the top level control for this editor. Usually used for getting a parent to attach popup menus.
          Caution: It is possible for an editor to exist without a control. The query will return NONEif no control is present.
    
      - defineTemplate : dt            (unicode)       [create]
          Puts the command in a mode where any other flags and args are parsed and added to the command template specified in the
          argument. They will be used as default arguments in any subsequent invocations of the command when templateName is set
          as the current template.
    
      - docTag : dtg                   (unicode)       [create,query,edit]
          Attaches a tag to the editor.
    
      - exists : ex                    (bool)          [create]
          Returns whether the specified object exists or not. Other flags are ignored.
    
      - filter : f                     (unicode)       [create,query,edit]
          Specifies the name of an itemFilter object to be used with this editor. This filters the information coming onto the
          main list of the editor.
    
      - forceMainConnection : fmc      (unicode)       [create,query,edit]
          Specifies the name of a selectionConnection object that the editor will use as its source of content. The editor will
          only display items contained in the selectionConnection object. This is a variant of the -mainListConnection flag in
          that it will force a change even when the connection is locked. This flag is used to reduce the overhead when using the
          -unlockMainConnection , -mainListConnection, -lockMainConnection flags in immediate succession.
    
      - highlightConnection : hlc      (unicode)       [create,query,edit]
          Specifies the name of a selectionConnection object that the editor will synchronize with its highlight list. Not all
          editors have a highlight list. For those that do, it is a secondary selection list.
    
      - lockMainConnection : lck       (bool)          [create,edit]
          Locks the current list of objects within the mainConnection, so that only those objects are displayed within the editor.
          Further changes to the original mainConnection are ignored.
    
      - mainListConnection : mlc       (unicode)       [create,query,edit]
          Specifies the name of a selectionConnection object that the editor will use as its source of content. The editor will
          only display items contained in the selectionConnection object.
    
      - onlyParents : op               (bool)          [query]
          When used with the 'selectItem' or 'selectReference' queries it indicates that, if both a parent and a child file or
          reference are selected, only the parent will be returned.
    
      - panel : pnl                    (unicode)       [create,query]
          Specifies the panel for this editor. By default if an editor is created in the create callback of a scripted panel it
          will belong to that panel. If an editor does not belong to a panel it will be deleted when the window that it is in is
          deleted.
    
      - parent : p                     (unicode)       [create,query,edit]
          Specifies the parent layout for this editor. This flag will only have an effect if the editor is currently un-parented.
    
      - refreshReferences : rr         (bool)          [edit]
          Force refresh of references
    
      - selectCommand : sc             (script)        [create,query,edit]
          A script to be executed when an item is selected.
    
      - selectItem : si                (int)           [query,edit]
          Query or change the currently selected item. When queried, the currently selected file name will be return.
    
      - selectReference : sr           (unicode)       [query]
          Query the currently selected reference. Returns the name of the currently selected reference node.
    
      - selectionConnection : slc      (unicode)       [create,query,edit]
          Specifies the name of a selectionConnection object that the editor will synchronize with its own selection list. As the
          user selects things in this editor, they will be selected in the selectionConnection object. If the object undergoes
          changes, the editor updates to show the changes.
    
      - shortName : shn                (bool)          [query]
          When used with the 'selectItem' query it indicates that the file name returned will be the short name (i.e. just a file
          name without any directory paths). If this flag is not present, the full name and directory path will be returned.
    
      - stateString : sts              (bool)          [query]
          Query only flag. Returns the MEL command that will create an editor to match the current editor state. The returned
          command string uses the string variable $editorName in place of a specific name.
    
      - unParent : up                  (bool)          [create,edit]
          Specifies that the editor should be removed from its layout. This cannot be used in query mode.
    
      - unlockMainConnection : ulk     (bool)          [create,edit]
          Unlocks the mainConnection, effectively restoring the original mainConnection (if it is still available), and dynamic
          updates.
    
      - unresolvedName : un            (bool)          [query]
          When used with the 'selectItem' query it indicates that the file name returned will be unresolved (i.e. it will be the
          path originally specified when the file was loaded into Maya; this path may contain environment variables and may not
          exist on disk). If this flag is not present, the resolved name will    be returned.
    
      - updateMainConnection : upd     (bool)          [create,edit]
          Causes a locked mainConnection to be updated from the orginal mainConnection, but preserves the lock state.
    
      - useTemplate : ut               (unicode)       [create]
          Forces the command to use a command template other than the current one.
    
      - withoutCopyNumber : wcn        (bool)          [query]
          When used with the 'selectItem' query it indicates that the file name returned will not have a copy number appended to
          the end. If this flag is not present, the file name returned may have a copy number appended to the end.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.sceneEditor`
    """

    pass


def cacheFileCombine(*args, **kwargs):
    """
    Creates a cacheBlend node that can be used to combine, layer or blend multiple cacheFiles for a given object.
    
    Flags:
      - cacheIndex : ci                (bool)          [query]
          A query only flag that returns the index related to the cache specified with the connectCache flag.
    
      - channelName : cnm              (unicode)       [edit]
          Used in conjunction with the connectCache flag to indicate the channel(s) that should be connected.  If not specified,
          the first channel in the file is used.
    
      - connectCache : cc              (unicode)       [query,edit]
          An edit flag that specifies a cacheFile node that should be connected to the next available index on the specified
          cacheBlend node. As a query flag, it returns a string array containing the cacheFiles that feed into the specified
          cacheBlend node. In query mode, this flag can accept a value.
    
      - keepWeights : kw               (bool)          [edit]
          This is a flag for use in combination with the connectCache flag only. By default, the connectCache flag will set all
          weights other than the newly added cacheWeight to 0 so that the new cache gets complete control. This flag disables that
          behavior so that all existing blend weights are retained.
    
      - layerNode : ln                 (bool)          [query]
          A query flag that returns a string array of the existing cacheBlends on the selected object(s). Returns an empty string
          array if no cacheBlends are found.
    
      - nextAvailable : na             (bool)          [query]
          A query flag that returns the next available index on the selected cacheBlend node.
    
      - object : obj                   (unicode)       [query]
          This flag is used in combination with the objectIndex flag. It is used to specify the object whose index you wish to
          query.
    
      - objectIndex : oi               (int)           [query,edit]
          In edit mode, used in conjunction with the connectCache flag to indicate the objectIndex to be connected. In query mode,
          returns the index related to the object specified with the object flag.                                   Flag can have
          multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.cacheFileCombine`
    """

    pass


def dgeval(*args, **kwargs):
    """
    The dgevalcommand is used to force a dependency graph evaluate of a node or plug.  Used for debugging to find
    propagation problems. Normally the selection list is used to determine which objects to evaluate, but you can add to the
    selection list by specifying which objects you want on the command line.
    
    Flags:
      - src : src                      (bool)          [create]
          This flag is obsolete. Do not use.
    
      - verbose : v                    (bool)          [create]
          If this flag is used then the results of the evaluation(s) is/are printed on stdout.                  Flag can have
          multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.dgeval`
    """

    pass


def mouse(*args, **kwargs):
    """
    This command allows to configure mouse.
    
    Flags:
      - enableScrollWheel : esw        (bool)          [create]
          Enable or disable scroll wheel support.
    
      - mouseButtonTracking : mbt      (int)           [create]
          Set the number (1, 2 or 3) of mouse buttons to track.Note: this is only supported on Macintosh
    
      - mouseButtonTrackingStatus : mbs (bool)          [create]
          returns the current number of mouse buttons being tracked.
    
      - scrollWheelStatus : sws        (bool)          [create]
          returns the current status of scroll wheel support.                  Flag can have multiple arguments, passed either as
          a tuple or a list.
    
    
    Derived from mel command `maya.cmds.mouse`
    """

    pass


def createReference(filepath, **kwargs):
    """
    Create a reference to the specified file. Returns the name of the file referenced.Query all file references from the specified file.                  
    
    Flags:
      - loadNoReferences:
          This flag is obsolete and has been replaced witht the loadReferenceDepth flag. When used with the -open flag, no
          references will be loaded. When used with -i/import, -r/reference or -lr/loadReference flags, will load the top-most
          reference only.
      - loadReferenceDepth:
          Used to specify which references should be loaded. Valid types are all, noneand topOnly, which will load all references,
          no references and top-level references only, respectively. May only be used with the -o/open, -i/import, -r/reference or
          -lr/loadReference flags. When noneis used with -lr/loadReference, only path validation is performed. This can be used to
          replace a reference without triggering reload. Not using loadReferenceDepth will load references in the same loaded or
          unloaded state that they were in when the file was saved. Additionally, the -lr/loadReference flag supports a fourth
          type, asPrefs. This will force any nested references to be loaded according to the state (if any) stored in the current
          scene file, rather than according to the state saved in the reference file itself.
      - defaultNamespace:
          Use the default name space for import and referencing.  This is an advanced option.  If set, then on import or
          reference, Maya will attempt to place all nodes from the imported or referenced file directly into the root (default)
          name space, without invoking any name clash resolution algorithms.  If the names of any of the new objects    already
          exist in the root namespace, then errors will result. The user of this flag is responsible for creating a name clash
          resolution mechanism outside of Maya to avoid such errors. Note:This flag    is intended only for use with custom file
          translators written through    the API. Use at your own risk.
      - deferReference:
          When used in conjunction with the -reference flag, this flag determines if the reference is loaded, or if loading is
          deferred.C: The default is false.Q: When queried, this flag returns true if the reference is deferred, or false if the
          reference is not deferred. If this is used with -rfn/referenceNode, the -rfn flag must come before -q.
      - groupReference:
          Used only with the -r or the -i flag. Used to group all the imported/referenced items under a single transform.
      - groupLocator:
          Used only with the -r and the -gr flag. Used to group the output of groupReference under a locator
      - groupName:
          Used only with the -gr flag. Optionally used to set the name of the transform node that the imported/referenced items
          will be grouped under.
      - namespace:
          The namespace name to use that will group all objects during importing and referencing. Change the namespace used to
          group all the objects from the specified referenced file. The reference must have been created with the Using
          Namespacesoption, and must be loaded. Non-referenced nodes contained in the existing namespace will also be moved to the
          new namespace. The new namespace will be created by this command and can not already exist. The old namespace will be
          removed.
      - referenceNode:
          This flag is only used during queries. In MEL, if it appears before -query then it must be followed by the name of one
          of the scene's reference nodes. That will determine the reference to be queried by whatever flags appear after -query.
          If the named reference node does not exist within the scene the command will fail with an error. In Python the
          equivalent behavior is obtained by passing the name of the reference node as the flag's value. In MEL, if this flag
          appears after -query then it takes no argument and will cause the command to return the name of the reference node
          associated with the file given as the command's argument. If the file is not a reference or for some reason does not
          have a reference node (e.g., the user deleted it) then an empty string will be returned. If the file is not part of the
          current scene then the command will fail with an error. In Python the equivalent behavior is obtained by passing True as
          the flag's value.       In query mode, this flag can accept a value.
      - renamingPrefix:
          The string to use as a prefix for all objects from this file. This flag has been replaced by -ns/namespace.
      - swapNamespace:
          Can only be used in conjunction with the -r/reference or -i/import flags. This flag will replace any occurrences of a
          given namespace to an alternate specified namespace. This namespace swapwill occur as the file is referenced in. It
          takes in two string arguments. The first argument specifies the namespace to replace. The second argument specifies the
          replacement namespace. Use of this flag, implicitly enables the use of namespaces and cannot be used with
          deferReference.
      - sharedReferenceFile:
          Can only be used in conjunction with the -r/reference flag and the -ns/namespace flag (there is no prefix support). This
          flag modifies the '-r/reference' flag to indicate that all nodes within that reference should be treated as shared
          nodes. New copies    of those nodes will not be created if a copy already exists. Instead, the shared node will be
          merged with the existing node. The specifics of what happens when two nodes are merged depends on the node type. This
          flag cannot be used in conjunction with -shd/sharedNodes.
      - sharedNodes:
          This flag modifies the '-r/reference' flag to indicate that certain    types of nodes within that reference should be
          treated as shared nodes. All shared nodes will be placed in the default namespace. New copies of those nodes will not be
          created if a copy already exists in the default namespace, instead the shared node will be merged with the    existing
          node. The specifics of what happens when two nodes are merged depends on the node type. In general attribute values will
          not be merged, meaning the values set on any existing shared nodes will be retained, and the values of the nodes being
          merged in will be ignored. The valid options are displayLayers, shadingNetworks, renderLayersByName, and
          renderLayersById. This flag is multi-use; it may be specified multiple times to for example, share both display layers
          and shading networks. Two shading networks will only be merged if    they are identical: the network    of nodes feeding
          into the shading group must be arranged identically with equivalent nodes have the same name and node type. Additionally
          if a network is animated or contains a DAG object or expression it will not be mergeable. This flag cannot be used in
          conjunction with -srf/sharedReferenceFile.
      - returnNewNodes:
          Used to control the return value in open, import, loadReference, and reference operations. It will force the file
          command to return a list of new nodes added to the current scene.
    
    Derived from mel command `maya.cmds.file`
    """

    pass


def error(*args, **kwargs):
    """
    The error command is provided so that the user can issue error messages from his/her scripts and control execution in
    the event of runtime errors.  The string argument is displayed in the command window (or stdout if running in batch
    mode) after being prefixed with an error message heading and surrounded by //.  The error command also causes execution
    to terminate with an error. Using error is like raising an exception because the error will propagate up through the
    call chain. You can use catch to handle the error from the caller side. If you don't want execution to end, then you
    probably want to use the warning command instead.
    
    Flags:
      - noContext : n                  (bool)          [create]
          Do not include the context information with the error message.
    
      - showLineNumber : sl            (bool)          [create]
          Obsolete. Will be deleted in the next version of Maya. Use the checkbox in the script editor that enables line number
          display instead.                             Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.error`
    """

    pass


def _safePyNode(n):
    pass


def assignInputDevice(*args, **kwargs):
    """
    This command associates a command string (i.e. a mel script) with the input device.  When the device moves or a button
    on the device is pressed, the command string is executed as if you typed it into the window.  If the command string
    contains the names of buttons or axes of the device, the current value of these buttons/axes are substituted in.
    Buttons are reported as booleans and axes as doubles. This command is most useful for associating buttons on a device
    with commands.  For using a device to capture continous movements it is much more efficient to attach the device
    directly into the dependency graph.
    
    Flags:
      - clutch : c                     (unicode)       [create]
          specify a clutch button.  This button must be down for the command string to be executed. If no clutch is specified the
          command string is executed everytime the device state changes
    
      - continuous : ct                (bool)          [create]
          if this flag is set the command string is continously (once for everytime the device changes state).  By default if a
          clutch button is specified the command string is only executed once when the button is pressed.
    
      - device : d                     (unicode)       [create]
          specify which device to assign the command string.
    
      - immediate : im                 (bool)          [create]
          Immediately executes the command, without using the queue.
    
      - multiple : m                   (bool)          [create]
          if this flag is set the other command strings associated with this device are not deleted. By default, when a new
          command string is attached to the device, all other command strings are deleted.                  Flag can have multiple
          arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.assignInputDevice`
    """

    pass


def reference(*args, **kwargs):
    """
    Flags:
      - connectionsBroken : cb         (bool)          []
    
      - connectionsMade : cm           (bool)          []
    
      - dagPath : dp                   (bool)          []
    
      - editCommand : ec               (unicode)       []
    
      - filename : f                   (unicode)       []
    
      - isNodeReferenced : inr         (bool)          []
    
      - longName : ln                  (bool)          []
    
      - node : n                       (unicode)       []
    
      - referenceNode : rfn            (unicode)       []
    
      - shortName : sn                 (bool)          []
    
    
    Derived from mel command `maya.cmds.reference`
    """

    pass


def deviceEditor(*args, **kwargs):
    """
    This creates an editor for creating/modifying attachments to input devices.
    
    Flags:
      - control : ctl                  (bool)          [query]
          Query only. Returns the top level control for this editor. Usually used for getting a parent to attach popup menus.
          Caution: It is possible for an editor to exist without a control. The query will return NONEif no control is present.
    
      - defineTemplate : dt            (unicode)       [create]
          Puts the command in a mode where any other flags and args are parsed and added to the command template specified in the
          argument. They will be used as default arguments in any subsequent invocations of the command when templateName is set
          as the current template.
    
      - docTag : dtg                   (unicode)       [create,query,edit]
          Attaches a tag to the editor.
    
      - exists : ex                    (bool)          [create]
          Returns whether the specified object exists or not. Other flags are ignored.
    
      - filter : f                     (unicode)       [create,query,edit]
          Specifies the name of an itemFilter object to be used with this editor. This filters the information coming onto the
          main list of the editor.
    
      - forceMainConnection : fmc      (unicode)       [create,query,edit]
          Specifies the name of a selectionConnection object that the editor will use as its source of content. The editor will
          only display items contained in the selectionConnection object. This is a variant of the -mainListConnection flag in
          that it will force a change even when the connection is locked. This flag is used to reduce the overhead when using the
          -unlockMainConnection , -mainListConnection, -lockMainConnection flags in immediate succession.
    
      - highlightConnection : hlc      (unicode)       [create,query,edit]
          Specifies the name of a selectionConnection object that the editor will synchronize with its highlight list. Not all
          editors have a highlight list. For those that do, it is a secondary selection list.
    
      - lockMainConnection : lck       (bool)          [create,edit]
          Locks the current list of objects within the mainConnection, so that only those objects are displayed within the editor.
          Further changes to the original mainConnection are ignored.
    
      - mainListConnection : mlc       (unicode)       [create,query,edit]
          Specifies the name of a selectionConnection object that the editor will use as its source of content. The editor will
          only display items contained in the selectionConnection object.
    
      - panel : pnl                    (unicode)       [create,query]
          Specifies the panel for this editor. By default if an editor is created in the create callback of a scripted panel it
          will belong to that panel. If an editor does not belong to a panel it will be deleted when the window that it is in is
          deleted.
    
      - parent : p                     (unicode)       [create,query,edit]
          Specifies the parent layout for this editor. This flag will only have an effect if the editor is currently un-parented.
    
      - selectionConnection : slc      (unicode)       [create,query,edit]
          Specifies the name of a selectionConnection object that the editor will synchronize with its own selection list. As the
          user selects things in this editor, they will be selected in the selectionConnection object. If the object undergoes
          changes, the editor updates to show the changes.
    
      - stateString : sts              (bool)          [query]
          Query only flag. Returns the MEL command that will create an editor to match the current editor state. The returned
          command string uses the string variable $editorName in place of a specific name.
    
      - takePath : tp                  (unicode)       [query,edit]
          The path used for writing/reading take data through the editor.
    
      - unParent : up                  (bool)          [create,edit]
          Specifies that the editor should be removed from its layout. This cannot be used in query mode.
    
      - unlockMainConnection : ulk     (bool)          [create,edit]
          Unlocks the mainConnection, effectively restoring the original mainConnection (if it is still available), and dynamic
          updates.
    
      - updateMainConnection : upd     (bool)          [create,edit]
          Causes a locked mainConnection to be updated from the orginal mainConnection, but preserves the lock state.
    
      - useTemplate : ut               (unicode)       [create]
          Forces the command to use a command template other than the current one.                  Flag can have multiple
          arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.deviceEditor`
    """

    pass


def whatsNewHighlight(*args, **kwargs):
    """
    This command is used to toggle the What's New highlighting feature, and the display of the settings dialog for the
    feature that appears on startup. In query mode, return type is based on queried flag.
    
    Flags:
      - highlightColor : hc            (float, float, float) [create,query]
          Set the color of the What's New highlight. The arguments correspond to the red, green, and blue color components. Each
          color component ranges in value from 0.0 to 1.0.
    
      - highlightOn : ho               (bool)          [create,query]
          Toggle the What's New highlighting feature. When turned on, menu items and buttons introduced in the latest version will
          be highlighted.
    
      - showStartupDialog : ssd        (bool)          [create,query]
          Set whether the settings dialog for this feature appears on startup.                  Flag can have multiple arguments,
          passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.whatsNewHighlight`
    """

    pass


def warning(*args, **kwargs):
    """
    The warning command is provided so that the user can issue warning messages from his/her scripts. The string argument is
    displayed in the command window (or stdout if running in batch mode) after being prefixed with a warning message heading
    and surrounded by the appropriate language separators (# for Python, // for Mel).
    
    Flags:
      - noContext : n                  (bool)          [create]
          Do not include the context information with the warning message.
    
      - showLineNumber : sl            (bool)          [create]
          Obsolete. Will be deleted in the next version of Maya. Use the checkbox in the script editor that enables line number
          display instead.                             Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.warning`
    """

    pass


def allNodeTypes(*args, **kwargs):
    """
    This command returns a list containing the type names of every kind of creatable node registered with the system. Note
    that some node types are abstract and cannot be created. These will not show up on this list. (e.g. transform and
    polyShape both inherit from dagObject, but dagObject  cannot be created directly so it will not appear on this list.)
    
    Flags:
      - includeAbstract : ia           (bool)          [create]
          Show every node type, even the abstract ones which cannot be created via the 'createNode' command. These will have the
          suffix (abstract)appended to them in the list.                              Flag can have multiple arguments, passed
          either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.allNodeTypes`
    """

    pass


def dbmessage(*args, **kwargs):
    """
    The dbmessagecommand is used to install monitors for certain message types, dumping debug information as they are sent
    so that the flow of messages can be examined.
    
    Flags:
      - file : f                       (unicode)       [create]
          Destination file of the message monitoring information.  Use the special names stdoutand stderrto redirect to your
          command window.  As well, the special name msdevis available on NT to direct your output to the debug tab in the output
          window of Developer Studio. Default value is stdout.
    
      - list : l                       (bool)          [create]
          List all available message types and their current enabled status.
    
      - monitor : m                    (bool)          [create]
          Set the monitoring state of the message type ('on' to enable, 'off' to disable). Returns the list of all message types
          being monitored after the change in state.
    
      - type : t                       (unicode)       [create]
          Monitor only the messages whose name matches this keyword (default is all).                                Flag can have
          multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.dbmessage`
    """

    pass


def profilerTool(*args, **kwargs):
    """
    This script is intended to be used by the profilerPanel to interact with the profiler tool's view (draw region). It can
    be used to control some behaviors about the profiler Tool.               In query mode, return type is based on queried
    flag.
    
    Flags:
      - categoryView : cat             (bool)          [edit]
          Change view mode to category view
    
      - cpuView : cpu                  (bool)          [edit]
          Change view mode to cpu view
    
      - destroy : dtr                  (bool)          [create]
          Destroy the profiler tool Internal flag. Should not be used by user.
    
      - exists : ex                    (bool)          [query]
          Query if the profiler tool view exists. Profiler tool can only exist after profilerTool -makeis called.
    
      - findNext : fn                  (bool)          [query]
          This flag is used along with flag -searchEvent.
    
      - findPrevious : fp              (bool)          [query]
          This flag is used along with flag -searchEvent.
    
      - frameAll : fa                  (bool)          [edit]
          Frame on all events in the profilerToolView
    
      - frameSelected : fs             (bool)          [edit]
          Frame on all selected events in the profilerToolView
    
      - isolateSegment : isolateSegment (int)           [edit]
          Isolate a specified segment. A segment is a set of events that happened in one animation frame. You can use flag
          -segmentCount to query the number of segments in the event buffer. The segment index starts from 0. If the specified
          segment does not exist, an error will be thrown.
    
      - make : mk                      (bool)          [create]
          Make the profiler tool and parent it to the most recent layout created Internal flag. Should not be used by user.
    
      - matchWholeWord : mww           (bool)          [edit]
          Tells profiler tool if it should match whole word when searching event(s). The default value is false.
    
      - searchEvent : se               (unicode)       [query]
          Search event(s). You can set -matchWholeWord before you use -searchEvent. If -matchWholeWord has been set to true, the
          profiler tool will search event(s) whose name exactly matches with the string. If -matchWholeWord has been set to false,
          the profiler tool will search event(s) whose name contains the string. If -findNext is also used along with this flag,
          the profiler tool will find the first event next to the current selected event. If -findPrevious is also used along with
          this flag, the profiler tool will find the first event previous to the current selected event. If currently don't have a
          selected event or there are multiple selected events, the search will start at the first event in profiler buffer. If
          -findNext and -findPrevious are not used along with this flag, the profiler tool will find all events.
    
      - segmentCount : sc              (bool)          [query]
          Returns the number of segments in the event buffer.
    
      - showAllEvent : sa              (bool)          [edit]
          Show all events (if events were hidden by filtering) (true) or Hide all events (false)
    
      - showSelectedEvents : ss        (bool)          [edit]
          Show only the selected events (true) or hide all selected events (false)
    
      - showSelectedEventsRepetition : ssr (bool)          [edit]
          Show only the selected events repetition based on their comment (true) or Hide all selected events repetition based on
          their comment (false)
    
      - threadView : thd               (bool)          [edit]
          Change view mode to thread view
    
      - unisolateSegment : uis         (bool)          [edit]
          Unisolate current isolated segment. If no segment is currently isolated, nothing will happen.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.profilerTool`
    """

    pass


def namespace(*args, **kwargs):
    """
    This command allows a namespace to be created, set or removed. A namespace is a simple grouping of objects under a given
    name. Namespaces are primarily used to resolve name-clash issues in Maya, where a new object has the same name as an
    existing object (from importing a file, for example).  Using namespaces, you can have two objects with the same name, as
    long as they are contained in differenct namespaces. Namespaces are reminiscent of hierarchical structures like file
    systems where namespaces are analogous to directories and objects are analogous to files. The colon (':') character is
    the separator used to separate the names of namespaces and nodes instead of the slash ('/') or backslash ('\')
    character.  Namespaces can contain other namespaces as well as objects.  Like objects, the names of namespaces must be
    unique within another namespace. Objects and namespaces can be in only one namespace. Namespace names and object names
    don't clash so a namespace and an object contained in another namespace can have the same name. There is an unnamed root
    namespace specified with a leading colon (':').  Any object not in a named namespace is in the root namespace. Normally,
    the leading colon is omitted from the name of an object as it's presence is implied. The presence of a leading colon is
    important when moving objects between namespaces using the 'rename' command.  For the 'rename' command, the new name is
    relative to the current namespace unless the new name is fully qualified with a leading colon. Namespaces are created
    using the 'add/addNamespace' flag. By default they are created under the current namespace. Changing the current
    namespace is done with the 'set/setNamespace' flag. To reset the current namespace to the root namespace, use 'namespace
    -set :;'. Whenever an object is created, it is added by default to the current namespace. When creating a new namespace
    using a qualified name, any intervening namespaces which do not yet exist will be automatically created. For example, if
    the name of the new namespace is specified as A:Band the current namespace already has a child namespace named Athen a
    new child namespace named Bwill be created under A. But if the current namespace does not yet have a child named Athen
    it will be created automatically. This applies regardless of the number of levels in the provided name (e.g. A:B:C:D).
    The 'p/parent' flag can be used to explicitly specify the parent namespace under which the new one should be created,
    rather than just defaulting to the current namespace. If the name given for the new namespace is absolute (i.e. it
    begins with a colon, as in :A:B) then both the current namespace and the 'parent' flag will be ignored and the new
    namespace will be created under the root namespace. The relativeNamespace flag can be used to change the way node names
    are displayed in the UI and returned by the 'ls' command. Here are some specific details on how the return from the 'ls'
    command works in relativeNamespace mode: List all mesh objects in the scene:ls -type mesh;The above command lists all
    mesh objects in the root and any child namespaces. In relative name lookup mode, all names will be displayed relative to
    the current namespace. When not in relative name lookup mode (the default behaviour in Maya), results are printed
    relative to the root namespace. Using a \*wildcard:namespace -set myNS;ls -type mesh \*;In relative name lookup mode,
    the \*will match to the current namespace and thus the ls command will list only those meshes defined within the current
    namespace (i.e. myNs). If relative name lookup is off (the default behaviour in Maya), names are root-relative and thus
    \*matches the root namespace, with the net result being that only thoses meshes defined in the root namespace will be
    listed. You can force the root namespace to be listed when in relative name lookup mode by specifying :\*as your search
    pattern (i.e. ls -type mesh :\*which lists those meshes defined in the root namespace only). Note that you can also use
    :\*when relative name lookup mode is off to match the root if you want a consistent way to list the root. Listing child
    namespace contents:ls -type mesh \*:\*;For an example to list all meshes in immediate child namespaces, use \*:\*. In
    relative name lookup mode \*:\*lists those meshes in immediate child namespaces of the current namespaces. When not in
    relative name lookup mode, \*:\*lists meshes in namespaces one level below the root. Recursive listing of namespace
    contents:Example: ls -type mesh -recurse on \*The 'recurse' flag is provided on the lscommand to recursively traverse
    any child namespaces. In relative name lookup mode, the above example command will list all meshes in the current and
    any child namespaces of current. When not in relative name lookup mode, the above example command works from the root
    downwards and is thus equivalent to ls -type mesh.
    
    Flags:
      - absoluteName : an              (bool)          [create,query]
          This is a general flag which can be used to specify the desired format for the namespace(s) returned by the command. The
          absolute name of the namespace is a full namespace path, starting from the root namespace :and including all parent
          namespaces.  For example :ns:ballis an absolute namespace name while ns:ballis not.
    
      - addNamespace : add             (unicode)       [create]
          Create a new namespace with the given name. Both qualified names (A:B) and unqualified names (A) are acceptable. If any
          of the higher-level namespaces in a qualified name do not yet exist, they will be created. If the supplied name contains
          invalid characters it will first be modified as per the validateName flag.
    
      - collapseAncestors : ch         (unicode)       [create]
          Delete all empty ancestors of the given namespace. An empty namespace is a a namespace that does not contain any objects
          or other nested namespaces
    
      - deleteNamespaceContent : dnc   (bool)          [create]
          Used with the 'rm/removeNamespace' flag to indicate that when removing a namespace the contents of the namespace will
          also be removed.
    
      - exists : ex                    (unicode)       [query]
          Returns true if the specified namespace exists, false if not.
    
      - force : f                      (bool)          [create]
          Used with 'mv/moveNamespace' to force the move operation to ignore name clashes.
    
      - isRootNamespace : ir           (unicode)       [query]
          Returns true if the specified namespace is root, false if not.
    
      - mergeNamespaceWithParent : mnp (bool)          [create]
          Used with the 'rm/removeNamespace' flag. When removing a namespace, move the rest of the namespace content to the parent
          namespace.
    
      - mergeNamespaceWithRoot : mnr   (bool)          [create]
          Used with the 'rm/removeNamespace' flag. When removing a namespace, move the rest of the namespace content to the root
          namespace.
    
      - moveNamespace : mv             (unicode, unicode) [create]
          Move the contents of the first namespace into the second namespace. Child namespaces will also be moved. Attempting to
          move a namespace containing referenced nodes will result in an error; use the 'file' command ('file -edit -namespace')
          to change a reference namespace. If there are objects in the source namespace with the same name as objects in the
          destination namespace, an error will be issued. Use the 'force' flag to override this error - name clashes will be
          resolved by renaming the objects to ensure uniqueness.
    
      - parent : p                     (unicode)       [create]
          Used with the 'addNamespace' or 'rename' flags to specifiy the parent of the new namespace. The full namespace parent
          path is required. When using 'addNamespace' with an absolute name, the 'parent' will be ignored and the command will
          display a warning
    
      - recurse : r                    (bool)          [query]
          Can be used with the 'exists' flag to recursively look for the specified namespace
    
      - relativeNames : rel            (bool)          [create,query]
          Turns on relative name lookup, which causes name lookups within Maya to be relative to the current namespace. By default
          this is off, meaning that name lookups are always relative to the root namespace. Be careful turning this feature on
          since commands such as setAttr will behave differently. It is wise to only turn this feature on while executing custom
          procedures that you have written to be namespace independent and turning relativeNames off when returning control from
          your custom procedures. Note that Maya will turn on relative naming during file I/O. Although it is not recommended to
          leave relativeNames turned on, if you try to toggle the value during file I/O you may notice that the value stays
          onbecause Maya has already temporarily enabled it internally. When relativeNames are enabled, the returns provided by
          the 'ls' command will be relative to the current namespace. See the main description of this command for more details.
    
      - removeNamespace : rm           (unicode)       [create]
          Deletes the given namespace.  The namespace must be empty for it to be deleted.
    
      - rename : ren                   (unicode, unicode) [create]
          Rename the first namespace to second namespace name. Child namespaces will also be renamed. Both names are relative to
          the current namespace. Use the 'parent' flag to specify a parent namespace for the renamed namespace. An error is issued
          if the second namespace name already exists. If the supplied name contains invalid characters it will first be modified
          as per the validateName flag.
    
      - setNamespace : set             (unicode)       [create]
          Sets the current namespace.
    
      - validateName : vn              (unicode)       [create]
          Convert the specified name to a valid name to make it contain no illegal characters. The leading illegal characters will
          be removed and other illegal characters will be converted to '_'. Specially, the leading numeric characters and trailing
          space characters will be also removed.  Full name path can be validated as well. However, if the namespace of the path
          does not exist, command will only return the base name. For example, :nonExistentNS:namewill be converted to name.  If
          the entire name consists solely of illegal characters, e.g. 123which contains only leading digits, then the returned
          string will be empty.                  Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.namespace`
    """

    pass


def timerX(*args, **kwargs):
    """
    Used to calculate elapsed time. This command returns sub-second accurate time values. It is useful from scripts for
    timing the length of operations. Call this command before and after the operation you wish to time. On the first call,
    do not use any flags. It will return the start time. Save this value. After the operation, call this command a second
    time, and pass the saved start time using the -st flag. The elapsed time will be returned.
    
    Flags:
      - startTime : st                 (float)         [create]
          When this flag is used, the command returns the elapsed time since the specified start time.                  Flag can
          have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.timerX`
    """

    pass


def dgmodified(*args, **kwargs):
    """
    The dgmodifiedcommand is used to find out which nodes in the           dependency graph have been modified.  This is
    mostly useful for fixing           instances where file new asks you to save when no changes have been           made to
    the scene.
    
    
    Derived from mel command `maya.cmds.dgmodified`
    """

    pass


def getInputDeviceRange(*args, **kwargs):
    """
    This command lists the minimum and maximum values the device axis can return.  This value is the raw device values
    before any mapping is applied.  If you don't specify an axis the values for all axes of the device are returned.
    
    Flags:
      - maxValue : max                 (bool)          [create]
          list only the maximum value of the axis
    
      - minValue : min                 (bool)          [create]
          list only the minimum value of the axis                  Flag can have multiple arguments, passed either as a tuple or a
          list.
    
    
    Derived from mel command `maya.cmds.getInputDeviceRange`
    """

    pass


def shotTrack(*args, **kwargs):
    """
    This command is used for inserting and removing tracks related to the shots displayed in the Sequencer. It can also be
    used to modify the track state, for example, to lock or mute a track.             In query mode, return type is based on
    queried flag.
    
    Flags:
      - insertTrack : it               (int)           [create]
          This flag is used to insert a new empty track at the track index specified.
    
      - lock : l                       (bool)          [create,query,edit]
          This flag specifies whether shots on a track are to be locked or not.
    
      - mute : m                       (bool)          [create,query,edit]
          This flag specifies whether shots on a track are to be muted or not.
    
      - numTracks : nt                 (int)           [query]
          To query the number of tracks
    
      - removeEmptyTracks : ret        (bool)          [create]
          This flag is used to remove all tracks that have no clips.
    
      - removeTrack : rt               (int)           [create]
          This flag is used to remove the track with the specified index.  The track must have no clips on it before it can be
          removed.
    
      - selfmute : sm                  (bool)          [create,query,edit]
          This flag specifies whether shots on a track are to be muted or not (unlike mute, this disregards soloing).
    
      - solo : so                      (bool)          [create,query,edit]
          This flag specifies whether shots on a track are to be soloed or not.
    
      - swapTracks : st                (int, int)      [create]
          This flag is used to swap the contents of two specified tracks.
    
      - title : t                      (unicode)       [create,query,edit]
          This flag specifies the title for the track.
    
      - track : tr                     (int)           [create,query,edit]
          Specify the track on which to operate by using the track's trackNumber.
    
      - unsolo : uso                   (bool)          [query]
          This flag specifies whether shots on a track are to be unsoloed or not.                                    Flag can have
          multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.shotTrack`
    """

    pass


def _translateEditFlags(kwargs, addKwargs=True):
    """
    Given the pymel values for successfulEdits/failedEdits (which may be
    True, False, or None), returns the corresponding maya.cmds values to use
    """

    pass


def exportSelectedAnimFromReference(exportPath, **kwargs):
    """
    Export the main scene animation nodes and animation helper nodes from the selected referenced objects. This flag, when used in conjunction with the -rfn/referenceNode flag, can be constrained to only export animation nodes from the selected nodes of a specified reference file. See -ean/exportAnim flag description for details on usage of animation files.                  
    
    Flags:
      - force:
          Force an action to take place. (new, open, save, remove reference, unload reference) Used with removeReference to force
          remove reference namespace even if it has contents. Cannot be used with removeReference if the reference resides in the
          root namespace. Used with unloadReference to force unload reference even if the reference node is locked, without
          prompting a dialog that warns user about the lost of edits.
      - referenceNode:
          This flag is only used during queries. In MEL, if it appears before -query then it must be followed by the name of one
          of the scene's reference nodes. That will determine the reference to be queried by whatever flags appear after -query.
          If the named reference node does not exist within the scene the command will fail with an error. In Python the
          equivalent behavior is obtained by passing the name of the reference node as the flag's value. In MEL, if this flag
          appears after -query then it takes no argument and will cause the command to return the name of the reference node
          associated with the file given as the command's argument. If the file is not a reference or for some reason does not
          have a reference node (e.g., the user deleted it) then an empty string will be returned. If the file is not part of the
          current scene then the command will fail with an error. In Python the equivalent behavior is obtained by passing True as
          the flag's value.       In query mode, this flag can accept a value.
      - type:
          Set the type of this file.  By default this can be any one of: mayaAscii, mayaBinary, mel,  OBJ, directory, plug-in,
          audio, move, EPS, Adobe(R) Illustrator(R), imageplug-ins may define their own types as well.Return a string array of
          file types that match this file.
    
    Derived from mel command `maya.cmds.file`
    """

    pass


def dagObjectCompare(*args, **kwargs):
    """
    dagObjectCompare can be used to compare to compare objects based on: type -  Currently supports transform nodes and
    shape nodesrelatives - Compares DAG objects' children and parentsconnections - Checks to make sure the two dags are
    connected to the same sources and destinationsattributes - Checks to make sure that the properties of active attributes
    are the same
    
    Flags:
      - attribute : a                  (bool)          [create]
          Compare dag object attributes
    
      - bail : b                       (unicode)       [create]
          Bail on first error or bail on category. Legal values are never, first, and category.
    
      - connection : c                 (bool)          [create]
          Compare dag connections
    
      - namespace : n                  (unicode)       [create]
          The baseline namespace
    
      - relative : r                   (bool)          [create]
          dag relatives
    
      - short : s                      (bool)          [create]
          Compress output to short form (not as verbose)
    
      - type : t                       (bool)          [create]
          Compare based on dag object type                                   Flag can have multiple arguments, passed either as a
          tuple or a list.
    
    
    Derived from mel command `maya.cmds.dagObjectCompare`
    """

    pass


def preloadRefEd(*args, **kwargs):
    """
    This creates an editor for managing which references will be read in (loaded) and which deferred (unloaded) upon opening
    a file.
    
    Flags:
      - control : ctl                  (bool)          [query]
          Query only. Returns the top level control for this editor. Usually used for getting a parent to attach popup menus.
          Caution: It is possible for an editor to exist without a control. The query will return NONEif no control is present.
    
      - defineTemplate : dt            (unicode)       [create]
          Puts the command in a mode where any other flags and args are parsed and added to the command template specified in the
          argument. They will be used as default arguments in any subsequent invocations of the command when templateName is set
          as the current template.
    
      - docTag : dtg                   (unicode)       [create,query,edit]
          Attaches a tag to the editor.
    
      - exists : ex                    (bool)          [create]
          Returns whether the specified object exists or not. Other flags are ignored.
    
      - filter : f                     (unicode)       [create,query,edit]
          Specifies the name of an itemFilter object to be used with this editor. This filters the information coming onto the
          main list of the editor.
    
      - forceMainConnection : fmc      (unicode)       [create,query,edit]
          Specifies the name of a selectionConnection object that the editor will use as its source of content. The editor will
          only display items contained in the selectionConnection object. This is a variant of the -mainListConnection flag in
          that it will force a change even when the connection is locked. This flag is used to reduce the overhead when using the
          -unlockMainConnection , -mainListConnection, -lockMainConnection flags in immediate succession.
    
      - highlightConnection : hlc      (unicode)       [create,query,edit]
          Specifies the name of a selectionConnection object that the editor will synchronize with its highlight list. Not all
          editors have a highlight list. For those that do, it is a secondary selection list.
    
      - lockMainConnection : lck       (bool)          [create,edit]
          Locks the current list of objects within the mainConnection, so that only those objects are displayed within the editor.
          Further changes to the original mainConnection are ignored.
    
      - mainListConnection : mlc       (unicode)       [create,query,edit]
          Specifies the name of a selectionConnection object that the editor will use as its source of content. The editor will
          only display items contained in the selectionConnection object.
    
      - panel : pnl                    (unicode)       [create,query]
          Specifies the panel for this editor. By default if an editor is created in the create callback of a scripted panel it
          will belong to that panel. If an editor does not belong to a panel it will be deleted when the window that it is in is
          deleted.
    
      - parent : p                     (unicode)       [create,query,edit]
          Specifies the parent layout for this editor. This flag will only have an effect if the editor is currently un-parented.
    
      - selectCommand : sc             (callable)      []
    
      - selectFileNode : sf            (bool)          [query]
          Query the currently selected load setting. Returns the id of the currently selected load setting. This id can be used as
          an argument to the selLoadSettings command.
    
      - selectionConnection : slc      (unicode)       [create,query,edit]
          Specifies the name of a selectionConnection object that the editor will synchronize with its own selection list. As the
          user selects things in this editor, they will be selected in the selectionConnection object. If the object undergoes
          changes, the editor updates to show the changes.
    
      - stateString : sts              (bool)          [query]
          Query only flag. Returns the MEL command that will create an editor to match the current editor state. The returned
          command string uses the string variable $editorName in place of a specific name.
    
      - unParent : up                  (bool)          [create,edit]
          Specifies that the editor should be removed from its layout. This cannot be used in query mode.
    
      - unlockMainConnection : ulk     (bool)          [create,edit]
          Unlocks the mainConnection, effectively restoring the original mainConnection (if it is still available), and dynamic
          updates.
    
      - updateMainConnection : upd     (bool)          [create,edit]
          Causes a locked mainConnection to be updated from the orginal mainConnection, but preserves the lock state.
    
      - useTemplate : ut               (unicode)       [create]
          Forces the command to use a command template other than the current one.                  Flag can have multiple
          arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.preloadRefEd`
    """

    pass


def referenceQuery(*args, **kwargs):
    """
    Use this command to find out information about references and referenced nodes. A valid target is either a reference
    node, a reference file, or a referenced node. Some flags don't require a target, see flag descriptions for more
    information on what effect this has. When a scene contains multiple levels of file references, those edits which affect
    a nested reference may be stored on several different reference nodes. For example: A.ma has a reference to B.ma which
    has a reference to C.ma which contains a poly sphere (pSphere1). If you were to open B.ma and translate the sphere, an
    edit would be stored on CRN which refers to a node named C:pSphere1. If you were then to open A.ma and parent the
    sphere, an edit would be stored on BRN which refers to a node named B:C:pSphere1. It is important to note that when
    querying edits which affect a nested reference, the edits will be returned in the same format that they were applied. In
    the above example, opening A.ma and querying all edits which affect C.ma, would return two edits a parent edit affecting
    B:C:pSphere1, and a setAttr edit affecting C:pSphere1. Since there is currently no node named C:pSphere1 (only
    B:C:pSphere1) care will have to be taken when interpreting the returned information. The same care should be taken when
    referenced DAG nodes have been parented or instanced. Continuing with the previous example, let's say that you were to
    open A.ma and, instead of simply parenting pSphere1, you were to instance it. While A.ma is open, B:C:pSphere1may now be
    an amibiguous name, replaced by |B:C:pSphere1and group1|B:C:pSphere1. However querying the edits which affect C.ma would
    still return a setAttr edit affecting C:pSphere1since it was applied prior to B:C:pSphere1 being instanced. Some tips:
    1. Use the '-topReference' flag to query only those edits which were applied    from the currently open file. 2. Use the
    '-onReferenceNode' flag to limit the results to those edits where    are stored on a given reference node. You can then
    use various string    manipulation techniques to extrapolate the current name of any affected    nodes.
    
    Modifications:
        - When queried for 'es/editStrings', returned a list of ReferenceEdit objects
        - By default, returns all edits. If neither of successfulEdits or
          failedEdits is given, they both default to True. If only one is given,
          the other defaults to the opposite value.
    
    Flags:
      - child : ch                     (bool)          [create]
          This flag modifies the '-rfn/-referenceNode' and '-f/-filename' flags to indicate the the children of the target
          reference will be returned. Returns a string array.
    
      - dagPath : dp                   (bool)          [create]
          This flag modifies the '-n/-nodes' flag to indicate that the names of any dag objects returned will include as much of
          the dag path as is necessary to make the names unique. If this flag is not present, the names returned will not include
          any dag paths.
    
      - editAttrs : ea                 (bool)          [create]
          Returns string array. A main flag used to query the edits that have been applied to the target. Only the names of the
          attributes involved in the reference edit will be returned. If an edit involves multiple attributes (e.g.
          connectAttredits) the nodes will be returned as separate, consecutive entries in the string array. A valid target is
          either a reference node, a reference file, or a referenced node. If a referenced node is specified, only those edits
          which affect that node will be returned. If a reference file or reference node is specified any edit which affects a
          node in that reference will be returned. If no target is specified all edits are returned. This command can be used on
          both loaded and unloaded references. By default it will return all the edits, formatted as MEL commands, which apply to
          the target. This flag can be used in combination with the '-ea/-editAttrs' flag to indicate that the names of both the
          involved nodes and attributes will be returned in the format 'node.attribute'.
    
      - editCommand : ec               (unicode)       [create,query]
          This is a secondary flag used to indicate which type of reference edits should be considered by the command. If this
          flag is not specified all edit types will be included. This flag requires a string parameter. Valid values are: addAttr,
          connectAttr, deleteAttr, disconnectAttr, parent, setAttr, lockand unlock. In some contexts, this flag may be specified
          more than once to specify multiple edit types to consider.
    
      - editNodes : en                 (bool)          [create]
          Returns string array. A main flag used to query the edits that have been applied to the target. Only the names of the
          nodes involved in the reference edit will be returned. If an edit involves multiple nodes (e.g. connectAttredits) the
          nodes will be returned as separate, consecutive entries in the string array. A valid target is either a reference node,
          a reference file, or a referenced node. If a referenced node is specified, only those edits which affect that node will
          be returned. If a reference file or reference node is specified any edit which affects a node in that reference will be
          returned. If no target is specified all edits are returned. This command can be used on both loaded and unloaded
          references. By default it will return all the edits, formatted as MEL commands, which apply to the target. This flag can
          be used in combination with the '-ea/-editAttrs' flag to indicate that the names of both the involved nodes and
          attributes will be returned in the format 'node.attribute'.
    
      - editStrings : es               (bool)          [create]
          Returns string array. A main flag used to query the edits that have been applied to the target. The edit will be
          returned as a valid MEL command. A valid target is either a reference node, a reference file, or a referenced node. If a
          referenced node is specified, only those edits which affect that node will be returned. If a reference file or reference
          node is specified any edit which affects a node in that reference will be returned. If no target is specified all edits
          are returned. This command can be used on both loaded and unloaded references. By default it will return all the edits,
          formatted as MEL commands, which apply to the target. This flag cannot be used with either the '-en/-editNodes' or
          '-ea/-editAttrs' flags.
    
      - failedEdits : fld              (bool)          [create]
          This is a secondary flag used to indicate whether or not failed edits should be acted on (e.g. queried, removed,
          etc...). A failed edit is an edit which could not be successfully applied the last time its reference was loaded. An
          edit can fail for a variety of reasons (e.g. the referenced node to which it applies was removed from the referenced
          file). By default failed edits will not be acted on.
    
      - filename : f                   (bool)          [create]
          Returns string. A main flag used to query the filename associated with the target reference.
    
      - isExportEdits : iee            (bool)          [create]
          Returns a boolean indicating whether the specified reference node or file name is an edits file (created with the Export
          Edits feature)
    
      - isLoaded : il                  (bool)          [create]
          Returns a boolean indicating whether the specified reference node or file name refers to a loaded or unloaded reference.
    
      - isNodeReferenced : inr         (bool)          [create]
          Returns boolean. A main flag used to determine whether or not the target node comes from a referenced file. true if the
          target node comes from a referenced file, false if not.
    
      - isPreviewOnly : ipo            (bool)          [create]
          Returns boolean. This flag is used to determine whether or not the target reference node is only a preview reference
          node.
    
      - liveEdits : le                 (bool)          [create]
          Specifies that the edits should be returned based on the live edits database. Only valid when used in conjunction with
          the editStrings flag.
    
      - namespace : ns                 (bool)          [create]
          Returns string. This flag returns the full namespace path of the target reference, starting from the root namespace :.
          It can be combined with the shortName flag to return just the base name of the namespace.
    
      - nodes : n                      (bool)          [create]
          Returns string array. A main flag used to query the contents of the target reference.
    
      - onReferenceNode : orn          (unicode)       [create,query]
          This is a secondary flag used to indicate that only those edits which are stored on the indicated reference node should
          be considered. This flag only supports multiple uses when specified with the exportEditscommand.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
      - parent : p                     (bool)          [create]
          This flag modifies the '-rfn/-referenceNode' and '-f/-filename' flags to indicate the the parent of the target reference
          will be returned.
    
      - parentNamespace : pns          (bool)          [create]
          A main flag used to query and return the parent namespace of the target reference.
    
      - referenceNode : rfn            (bool)          [create]
          Returns string. A main flag used to query the reference node associated with the target reference.
    
      - shortName : shn                (bool)          [create]
          This flag modifies the '-f/-filename' and '-ns/-namespace' flags. Used with the '-f/-filename' flag indicates that the
          file name returned will be the short name (i.e. just a file name without any directory paths). If this flag is not
          present, the full name and directory path will be returned. Used with the '-ns/-namespace' flag indicates that the
          namespace returned will be the base name of the namespace. (i.e. the base name of the full namespace path :AAA:BBB:CCCis
          CCC
    
      - showDagPath : sdp              (bool)          [create]
          Shows/hides the full dag path for edits. If false only displays the node-name of reference edits. Must be used with the
          -editNodes, -editStrings or -editAttrs flag.
    
      - showNamespace : sns            (bool)          [create]
          Shows/hides the namespaces on nodes in the reference edits. Must be used with the -editNodes, -editStrings or -editAttrs
          flag
    
      - successfulEdits : scs          (bool)          [create]
          This is a secondary flag used to indicate whether or not successful edits should be acted on (e.g. queried, removed,
          etc...). A successful edit is any edit which was successfully applied the last time its reference was loaded. By default
          successful edits will be acted on.
    
      - topReference : tr              (bool)          [create]
          This flag modifies the '-rfn/-referenceNode' flag to indicate the top level ancestral reference of the target reference
          will be returned.
    
      - unresolvedName : un            (bool)          [create]
          This flag modifies the '-f/-filename' flag to indicate that the file name returned will be unresolved (i.e. it will be
          the path originally specified when the file was loaded into Maya; this path may contain environment variables and may
          not exist on disk). If this flag is not present, the resolved name will     be returned.
    
      - withoutCopyNumber : wcn        (bool)          [create]
          This flag modifies the '-f/-filename' flag to indicate that the file name returned will not have a copy number (e.g.
          '{1}') appended to the end. If this flag is not present, the file name returned may have a copy number appended to the
          end.
    
    
    Derived from mel command `maya.cmds.referenceQuery`
    """

    pass


def loadPlugin(*args, **kwargs):
    """
    Load plug-ins into Maya. The parameter(s) to this command are either the names or pathnames of plug-in files.  The
    convention for naming plug-ins is to use a .so extension on Linux, a .mll extension on Windows and .bundle extension on
    Mac OS X. If no extension is provided then the default extension for the platform will be used. To load a Python plugin
    you must explicitly supply the '.py' extension. If the plugin was specified with a pathname then that is where the
    plugin will be searched for. If no pathname was provided then the current working directory (i.e. the one returned by
    Maya's 'pwd' command) will be searched, followed by the directories in the MAYA_PLUG_IN_PATH environment variable. When
    the plug-in is loaded, the name used in Maya's internal plug-in registry for the plug-in information will be the file
    name with the extension removed.  For example, if you load the plug-in newNode.mllthe name used in the Maya's registry
    will be newNode.  This value as well as that value with either a .so, .mllor .bundleextension can be used as valid
    arguments to either the unloadPlugin or pluginInfo commands.
    
    Flags:
      - addCallback : ac               (script)        [create]
          Add a MEL or Python callback script to be called after a plug-in is loaded.  For MEL, the procedure should have the
          following signature: global proc procedureName(string $pluginName).  For Python, you may specify either a script as a
          string, or a Python callable object such as a function.  If you specify a string, then put the formatting specifier
          %swhere you want the name of the plug-in to be inserted.  If you specify a callable such as a function, then the name of
          the plug-in will be passed as an argument.
    
      - allPlugins : a                 (bool)          [create]
          Cause all plug-ins in the search path specified in MAYA_PLUG_IN_PATH to be loaded.
    
      - name : n                       (unicode)       [create]
          Set a user defined name for the plug-ins that are loaded.  If the name is already taken, then a number will be added to
          the end of the name to make it unique.
    
      - qObsolete : q                  (bool)          []
    
      - quiet : qt                     (bool)          [create]
          Don't print a warning if you attempt to load a plug-in that is already loaded.
    
      - removeCallback : rc            (script)        [create]
          Removes a procedure which was previously added with -addCallback.                  Flag can have multiple arguments,
          passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.loadPlugin`
    """

    pass


def translator(*args, **kwargs):
    """
    Set or query parameters associated with the file translators specified in as the argument.
    
    Flags:
      - defaultFileRule : dfr          (bool)          [query]
          Returns the default file rule value, can return as well
    
      - defaultOptions : do            (unicode)       [query]
          Return/set a string of default options used by this translator.
    
      - extension : ext                (bool)          [query]
          Returns the default file extension for this translator.
    
      - fileCompression : cmp          (unicode)       [query]
          Specifies the compression action to take when a file is saved. Possible values are compressed, uncompressedasCompressed.
    
      - filter : f                     (bool)          [query]
          Returns the filter string used for this translator.
    
      - list : l                       (bool)          [query]
          Return a string array of all the translators that are loaded.
    
      - loaded : ld                    (bool)          [query]
          Returns true if the given translator is currently loaded.
    
      - objectType : ot                (bool)          [query]
          This flag is obsolete. This will now return the same results as defaultFileRule going forward.
    
      - optionsScript : os             (bool)          [query]
          Query the name of the options script to use to post the user options UI. When this script is invoked it will expect the
          name of the parent layout in which the options will be displayed as well as the name of the callback to be invoked once
          the apply button has been depressed in the options area.
    
      - readSupport : rs               (bool)          [query]
          Returns true if this translator supports read operations.
    
      - writeSupport : ws              (bool)          [query]
          Returns true if this translator supports write operations.                  Flag can have multiple arguments, passed
          either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.translator`
    """

    pass


def exportAnim(exportPath, **kwargs):
    """
    Export all animation nodes and animation helper nodes from all objects in the scene. The resulting animation export file will contain connections to objects that are not included in the animation file. As a result, importing/referencing this file back in will require objects of the same name to be present, else errors will occur. The -sns/swapNamespace flag is available for swapping the namespaces of given objects to another namespace. This use of namespaces can be used to re-purpose the animation file to multiple targets using a consistent naming scheme.  The exportAnim flag will not export animation layers. For generalized file export of animLayers and other types of nodes, refer to the exportEdits command. Or use the Export Layers functionality.                  
    
    Flags:
      - force:
          Force an action to take place. (new, open, save, remove reference, unload reference) Used with removeReference to force
          remove reference namespace even if it has contents. Cannot be used with removeReference if the reference resides in the
          root namespace. Used with unloadReference to force unload reference even if the reference node is locked, without
          prompting a dialog that warns user about the lost of edits.
      - type:
          Set the type of this file.  By default this can be any one of: mayaAscii, mayaBinary, mel,  OBJ, directory, plug-in,
          audio, move, EPS, Adobe(R) Illustrator(R), imageplug-ins may define their own types as well.Return a string array of
          file types that match this file.
    
    Derived from mel command `maya.cmds.file`
    """

    pass


def memory(*args, **kwargs):
    """
    Used to query essential statistics on memory availability and usage. By default memory sizes are returned in bytes.
    Since Maya's command engine only supports 32-bit signed integers, any returned value which cannot fit into 31 bits will
    be truncated to 2,147,483,647 and a warning message displayed. To avoid having memory sizes truncated use one of the
    memory size flags to return the value in larger units (e.g. megabytes) or use the asFloat flag to return the value as a
    float.
    
    Flags:
      - asFloat : af                   (bool)          [create]
          Causes numeric values to be returned as floats rather than ints. This can be useful if you wish to retain some of the
          significant digits lost when using the unit size flags.
    
      - debug : dbg                    (bool)          []
    
      - freeMemory : fr                (bool)          [create]
          Returns size of free memory
    
      - gigaByte : gb                  (bool)          [create]
          Return memory sizes in gigabytes (1024\*1024\*1024 bytes)
    
      - heapMemory : he                (bool)          [create]
          Returns size of memory heap
    
      - kiloByte : kb                  (bool)          [create]
          Return memory sizes in kilobytes (1024 bytes)
    
      - megaByte : mb                  (bool)          [create]
          Return memory sizes in megabytes (1024\*1024 bytes)
    
      - pageFaults : pf                (bool)          [create]
          Returns number of page faults
    
      - pageReclaims : pr              (bool)          [create]
          Returns number of page reclaims
    
      - physicalMemory : phy           (bool)          [create]
          Returns size of physical memory
    
      - summary : sum                  (bool)          [create]
          Returns a summary of memory usage. The size flags are ignored and all memory sizes are given in megabytes.
    
      - swapFree : swf                 (bool)          [create]
          Returns size of free swap
    
      - swapLogical : swl              (bool)          [create]
          Returns size of logical swap
    
      - swapMax : swm                  (bool)          [create]
          Returns maximum swap size
    
      - swapPhysical : swp             (bool)          [create]
          Returns size of physical swap
    
      - swapReserved : swr             (bool)          []
    
      - swapVirtual : swv              (bool)          [create]
          Returns size of virtual swap
    
      - swaps : sw                     (bool)          [create]
          Returns number of swaps                  Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.memory`
    """

    pass


def iterReferences(parentReference=None, recursive=False, namespaces=False, refNodes=False, references=True, recurseType='depth', loaded=None, unloaded=None):
    """
    returns references in the scene as a list of value tuples.
    
    The values in the tuples can be namespaces, refNodes (as PyNodes), and/or
    references (as FileReferences), and are controlled by their respective
    keywords (and are returned in that order).  If only one of the three options
    is True, the result will not be a list of value tuples, but will simply be a
    list of values.
    
    Parameters
    ----------
    parentReference : string, `Path`, or `FileReference`
        a reference to get sub-references from. If None (default), the current
        scene is used.
    
    recursive : bool
        recursively determine all references and sub-references
    
    namespaces : bool
        controls whether namespaces are returned
    
    refNodes : bool
        controls whether reference PyNodes are returned
    
    refNodes : bool
        controls whether FileReferences returned
    
    recurseType : string
        if recursing, whether to do a 'breadth' or 'depth' first search;
        defaults to a 'depth' first
    
    loaded : bool or None
        whether to return loaded references in the return result; if both of
        loaded/unloaded are not given (or None), then both are assumed True;
        if only one is given, the other is assumed to have the opposite boolean
        value
    
    unloaded : bool or None
        whether to return unloaded references in the return result; if both of
        loaded/unloaded are not given (or None), then both are assumed True;
        if only one is given, the other is assumed to have the opposite boolean
        value
    """

    pass


def namespaceInfo(*args, **kwargs):
    """
    This command displays information about a namespace. The target namespace can optionally be specified on the command
    line. If no namespace is specified, the command will display information about the current namespace. A namespace is a
    simple grouping of objects under a given name. Each item in a namespace can then be identified by its own name, along
    with what namespace it belongs to.  Namespaces can contain other namespaces like sets, with the restriction that all
    namespaces are disjoint. Namespaces are primarily used to resolve name-clash issues in Maya, where a new object has the
    same name as an existing object (from importing a file, for example). Using namespaces, you can have two objects with
    the same name, as long as they are contained in different namespaces. Note that namespaces are a simple grouping of
    names, so they do not effect selection, the DAG, the Dependency Graph, or any other aspect of Maya.  All namespace names
    are colon-separated. The namespace format flags are: baseName(shortName), fullNameand absoluteName. The flags are used
    in conjunction with the main query flags to specify the desired namespace format of the returned result. They can also
    be used to return the different formats of a specified namespace. By default, when no format is specified, the result
    will be returned as a full name.
    
    Modifications:
        - returns an empty list when the result is None
        - returns wrapped classes for listOnlyDependencyNodes
    
    Flags:
      - absoluteName : an              (bool)          [create]
          This is a general flag which can be used to specify the desired format for the namespace(s) returned by the command. The
          absolute name of the namespace is a full namespace path, starting from the root namespace :and including all parent
          namespaces.  For example :ns:ballis an absolute namespace name while ns:ballis not. The absolute namespace name is
          invariant and is not affected by the current namespace or relative namespace modes. See also other format modifiers
          'baseName', 'fullName', etc
    
      - baseName : bn                  (bool)          [create]
          This is a general flag which can be used to specify the desired format for the namespace(s) returned by the command. The
          base name of the namespace contains only the leaf level name and does not contain its parent namespace(s). For example
          the base name of an object named ns:ballis ball. This mode will always return the base name in the same manner, and is
          not affected by the current namespace or relative namespace mode. See also other format modifiers 'absoluteName',
          'fullName', etc The flag 'shortName' is a synonym for 'baseName'.
    
      - currentNamespace : cur         (bool)          [create]
          Display the name of the current namespace.
    
      - dagPath : dp                   (bool)          [create]
          This flag modifies the 'listNamespace' and 'listOnlyDependencyNodes' flags to indicate that the names of any dag objects
          returned will include as much of the dag path as is necessary to make the names unique. If this flag is not present, the
          names returned will not include any dag paths.
    
      - fullName : fn                  (bool)          [create]
          This is a general flag which can be used to specify the desired format for the namespace(s) returned by the command. The
          full name of the namespace contains both the namespace path and the base name, but without the leading colon
          representing the root namespace. For example ns:ballis a full name, whereas :ns:ballis an absolute name. This mode is
          affected by the current namespace and relative namespace modes. See also other format modifiers 'baseName',
          'absoluteName', etc.
    
      - internal : int                 (bool)          [create]
          This flag is used together with the 'listOnlyDependencyNodes' flag. When this flag is set, the returned list will
          include internal nodes (for example itemFilters) that are not listed by default.
    
      - isRootNamespace : ir           (unicode)       [create]
          Returns true if the namespace is root(:), false if not.
    
      - listNamespace : ls             (bool)          [create]
          List the contents of the namespace.
    
      - listOnlyDependencyNodes : lod  (bool)          [create]
          List all dependency nodes in the namespace.
    
      - listOnlyNamespaces : lon       (bool)          [create]
          List all namespaces in the namespace.
    
      - parent : p                     (bool)          [create]
          Display the parent of the namespace. By default, the list returned will not include internal nodes (such as
          itemFilters). To include the internal nodes, use the 'internal' flag.
    
      - recurse : r                    (bool)          [create]
          Can be specified with 'listNamespace', 'listOnlyNamespaces' or 'listOnlyDependencyNode' to cause the listing to
          recursively include any child namespaces of the namespaces;
    
      - shortName : sn                 (bool)          [create]
          This flag is deprecated and may be removed in future releases of Maya. It is a synonym for the baseName flag. Please use
          the baseName flag instead.                  Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.namespaceInfo`
    """

    pass


def listInputDeviceAxes(*args, **kwargs):
    """
    This command lists all of the axes of the specified input device.
    
    
    Derived from mel command `maya.cmds.listInputDeviceAxes`
    """

    pass


def feof(fileid):
    """
    Reproduces the behavior of the mel command of the same name. if writing pymel scripts from scratch,
    you should use a more pythonic construct for looping through files:
    
    >>> f = open('myfile.txt') # doctest: +SKIP
    ... for line in f:
    ...     print line
    
    This command is provided for python scripts generated by mel2py
    """

    pass


def hardware(*args, **kwargs):
    """
    Return description of the hardware available in the machine.
    
    Flags:
      - brdType : brd                  (bool)          [create]
          Returns IP number identifying the CPU motherboard
    
      - cpuType : cpu                  (bool)          [create]
          Returns type of CPU
    
      - graphicsType : gfx             (bool)          [create]
          Returns string identifying graphics hardware type
    
      - megaHertz : mhz                (bool)          [create]
          Returns string identifying the speed of the CPU chip
    
      - numProcessors : npr            (bool)          [create]
          Returns string identifying the number of processors                  Flag can have multiple arguments, passed either as
          a tuple or a list.
    
    
    Derived from mel command `maya.cmds.hardware`
    """

    pass


def _correctPath(path):
    pass


def clearCache(*args, **kwargs):
    """
    Even though dependency graph values are computed or dirty they may still occupy space temporarily within the nodes.
    This command goes in to all of the data that can be regenerated if required and removes it from the caches (datablocks),
    thus clearing up space in memory.
    
    Flags:
      - allNodes : all                 (bool)          [create]
          If toggled then all nodes in the graph are cleared.  Otherwise only those nodes that are selected are cleared.
    
      - computed : c                   (bool)          [create]
          If toggled then remove all data that is computable.  (Warning: If the data is requested for redraw then the recompute
          will immediately fill the data back in.)
    
      - dirty : d                      (bool)          [create]
          If toggled then remove all heavy data that is dirty.                               Flag can have multiple arguments,
          passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.clearCache`
    """

    pass


def aaf2fcp(*args, **kwargs):
    """
    This command is used to convert an aff file to a Final Cut Pro (fcp) xml file The conversion process can take several
    seconds to complete and the command is meant to be run asynchronously
    
    Flags:
      - deleteFile : df                (bool)          [create]
          Delete temporary file. Can only be used with the terminate option
    
      - dstPath : dst                  (unicode)       [create]
          Specifiy a destination path
    
      - getFileName : gfn              (int)           [create]
          Query output file name
    
      - progress : pr                  (int)           [create]
          Request progress report
    
      - srcFile : src                  (unicode)       [create]
          Specifiy a source file
    
      - terminate : t                  (int)           [create]
          Complete the task
    
      - waitCompletion : wc            (int)           [create]
          Wait for the conversion process to complete                                Flag can have multiple arguments, passed
          either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.aaf2fcp`
    """

    pass


def saveImage(*args, **kwargs):
    """
    This command creates a static image for non-xpm files. Any image file format supported by the file texture node is
    supported by this command. This command creates a static image control for non-xpm files used to display a thumbnail
    image of the scene file.
    
    Flags:
      - annotation : ann               (unicode)       [create,query,edit]
          Annotate the control with an extra string value.
    
      - backgroundColor : bgc          (float, float, float) [create,query,edit]
          The background color of the control. The arguments correspond to the red, green, and blue color components. Each
          component ranges in value from 0.0 to 1.0. When setting backgroundColor, the background is automatically enabled, unless
          enableBackground is also specified with a false value.
    
      - currentView : cv               (bool)          [edit]
          Generate the image from the current view.
    
      - defineTemplate : dt            (unicode)       [create]
          Puts the command in a mode where any other flags and args are parsed and added to the command template specified in the
          argument. They will be used as default arguments in any subsequent invocations of the command when templateName is set
          as the current template.
    
      - docTag : dtg                   (unicode)       [create,query,edit]
          Add a documentation flag to the control.  The documentation flag has a directory structure like hierarchy. Eg. -dt
          render/multiLister/createNode/material
    
      - dragCallback : dgc             (script)        [create,edit]
          Adds a callback that is called when the middle mouse button is pressed.  The MEL version of the callback is of the form:
          global proc string[] callbackName(string $dragControl, int $x, int $y, int $mods) The proc returns a string array that
          is transferred to the drop site. By convention the first string in the array describes the user settable message type.
          Controls that are application defined drag sources may ignore the callback. $mods allows testing for the key modifiers
          CTL and SHIFT. Possible values are 0 == No modifiers, 1 == SHIFT, 2 == CTL, 3 == CTL + SHIFT. In Python, it is similar,
          but there are two ways to specify the callback.  The recommended way is to pass a Python function object as the
          argument.  In that case, the Python callback should have the form: def callbackName( dragControl, x, y, modifiers ): The
          values of these arguments are the same as those for the MEL version above. The other way to specify the callback in
          Python is to specify a string to be executed.  In that case, the string will have the values substituted into it via the
          standard Python format operator.  The format values are passed in a dictionary with the keys dragControl, x, y,
          modifiers.  The dragControlvalue is a string and the other values are integers (eg the callback string could be print
          '%(dragControl)s %(x)d %(y)d %(modifiers)d'
    
      - dropCallback : dpc             (script)        [create,edit]
          Adds a callback that is called when a drag and drop operation is released above the drop site.  The MEL version of the
          callback is of the form: global proc callbackName(string $dragControl, string $dropControl, string $msgs[], int $x, int
          $y, int $type) The proc receives a string array that is transferred from the drag source. The first string in the msgs
          array describes the user defined message type. Controls that are application defined drop sites may ignore the callback.
          $type can have values of 1 == Move, 2 == Copy, 3 == Link. In Python, it is similar, but there are two ways to specify
          the callback.  The recommended way is to pass a Python function object as the argument.  In that case, the Python
          callback should have the form: def pythonDropTest( dragControl, dropControl, messages, x, y, dragType ): The values of
          these arguments are the same as those for the MEL version above. The other way to specify the callback in Python is to
          specify a string to be executed.  In that case, the string will have the values substituted into it via the standard
          Python format operator.  The format values are passed in a dictionary with the keys dragControl, dropControl, messages,
          x, y, type.  The dragControlvalue is a string and the other values are integers (eg the callback string could be print
          '%(dragControl)s %(dropControl)s %(messages)r %(x)d %(y)d %(type)d'
    
      - enable : en                    (bool)          [create,query,edit]
          The enable state of the control.  By default, this flag is set to true and the control is enabled.  Specify false and
          the control will appear dimmed or greyed-out indicating it is disabled.
    
      - enableBackground : ebg         (bool)          [create,query,edit]
          Enables the background color of the control.
    
      - exists : ex                    (bool)          [create]
          Returns whether the specified object exists or not. Other flags are ignored.
    
      - fullPathName : fpn             (bool)          [query]
          Return the full path name of the widget, which includes all the parents
    
      - height : h                     (int)           [create,query,edit]
          The height of the control.  The control will attempt to be this size if it is not overruled by parent layout conditions.
    
      - highlightColor : hlc           (float, float, float) [create,query,edit]
          The highlight color of the control. The arguments correspond to the red, green, and blue color components. Each
          component ranges in value from 0.0 to 1.0.
    
      - image : i                      (unicode)       [create,query,edit]
          Sets the image given the file name.
    
      - isObscured : io                (bool)          [query]
          Return whether the control can actually be seen by the user. The control will be obscured if its state is invisible, if
          it is blocked (entirely or partially) by some other control, if it or a parent layout is unmanaged, or if the control's
          window is invisible or iconified.
    
      - manage : m                     (bool)          [create,query,edit]
          Manage state of the control.  An unmanaged control is not visible, nor does it take up any screen real estate.  All
          controls are created managed by default.
    
      - noBackground : nbg             (bool)          [create,edit]
          Clear/reset the control's background. Passing true means the background should not be drawn at all, false means the
          background should be drawn.  The state of this flag is inherited by children of this control.
    
      - numberOfPopupMenus : npm       (bool)          [query]
          Return the number of popup menus attached to this control.
    
      - objectThumbnail : ot           (unicode)       [edit]
          Use an image of the named object, if possible.
    
      - parent : p                     (unicode)       [create,query]
          The parent layout for this control.
    
      - popupMenuArray : pma           (bool)          [query]
          Return the names of all the popup menus attached to this control.
    
      - preventOverride : po           (bool)          [create,query,edit]
          If true, this flag disallows overriding the control's attribute via the control's right mouse button menu.
    
      - sceneFile : sf                 (unicode)       [edit]
          The name of the file that the icon is to be associated with.
    
      - useTemplate : ut               (unicode)       [create]
          Forces the command to use a command template other than the current one.
    
      - visible : vis                  (bool)          [create,query,edit]
          The visible state of the control.  A control is created visible by default.  Note that a control's actual appearance is
          also dependent on the visible state of its parent layout(s).
    
      - visibleChangeCommand : vcc     (script)        [create,query,edit]
          Command that gets executed when visible state of the control changes.
    
      - width : w                      (int)           [create,query,edit]
          The width of the control.  The control will attempt to be this size if it is not overruled by parent layout conditions.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.saveImage`
    """

    pass


def listNamespaces_old():
    """
    Deprecated
    Returns a list of the namespaces of referenced files.
    REMOVE In Favor of listReferences('dict') ?
    """

    pass


def dgInfo(*args, **kwargs):
    """
    This command prints information about the DG in plain text. The scope of the information printed is the entire graph if
    the allflag is used, the nodes/plugs on the command line if they were specified, and the selection list, in that order.
    Each plug on a connection will have two pieces of state information displayed together at the end of the line on which
    they are printed. There are two possible values for each of the two states displayed. The values are updated when the DG
    pulls data across them, usually through evaluation, or pushes a dirty message through them. There are some subtleties in
    how the data is pulled through the connection but for simplicity it will be referred to as evaluation. The values
    displayed will be CLEAN or DIRTY followed by PROP or BLOCK. The first keyword has these meanings: CLEANmeans that
    evaluation of the plug's connection succeeded and no dirty messages have come through it since then. It also implies
    that the destination end of the connection has received the value from the source end. DIRTYmeans that a dirty message
    has passed through the plug's connection since the last time an evaluation was made on the destination side of that
    connection. Note: the data on the node has its own dirty state that depends on other factors so having a clean
    connection doesn't necessarily mean the plug's data is clean, and vice versa. The second keyword has these meanings:
    PROPmeans that the connection will allow dirty messages to pass through and forwards them to all destinations.
    BLOCKmeans that a dirty message will stop at this connection and not continue on to any destinations. This is an
    optimization that prevents excessive dirty flag propagation when many values are changing, for example, a frame change
    in an animated sequece. The combination CLEAN BLOCKshould never be seen in a valid DG. This indicates that while the
    plug connection has been evaluated since the last dirty message it will not propagate any new dirty messages coming in
    to it. That in turn means downstream nodes will not be notified that the graph is changing and they will not evaluate
    properly. Recovering from this invalid state requires entering the command dgdirty -ato mark everything dirty and
    restart proper evaluation. Think of this command as the reset/reboot of the DG world. Both state types behave
    differently depending on your connection type. SimpleA -B: Plugs at both ends of the connection share the same state
    information. The state information updates when an evaluation request comes to A from B, or a dirty message is sent from
    A to B. Fan-OutA -B, A -C: Each of A, B, and C have their own unique state information. B and C behave as described
    above. A has its state information linked to B and C - it will have CLEANonly when both B and C have CLEAN, it will have
    BLOCKonly when both B and C have BLOCK. In-OutA -B, C -A: Each of A, B, and C have their own unique state information. B
    and C behave as described above. A has its state information linked to B and C. The CLEAN|DIRTYflag looks backwards,
    then forwards: if( C == CLEAN ) A = CLEAN else if( B == CLEAN ) A = CLEAN The BLOCKstate is set when a dirty message
    passes through A, and the PROPstate is set either when A is set clean or an evaluation passes through A. There are some
    other exceptions to these rules: All of this state change information only applies to dirty messages and evaluations
    that use the normal context. Any changes in other contexts, for example, through the getAttr -t TIMEcommand, does not
    affect the state in the connections. Param curves and other passive inputs, for example blend nodes coming from param
    curves, will not disable propagation. Doing so would make the keyframing workflow impossible. Certain messages can
    choose to completely ignore the connection state information. For example when a node's state attribute changes a
    connection may change to a blocking one so the message has to be propagated at least one step further to all of its
    destinations. This way they can update their information. Certain operations can globally disable the use of the
    propagaton state to reduce message flow.  The simplest example is when the evaluation manager is building its graph. It
    has to visit all nodes so the propagation cannot be blocked. The messaging system has safeguards against cyclic messages
    flowing through connections but sometimes a message bypasses the connection completely and goes directly to the node.
    DAG parents do this to send messages to their children. So despite connections into a node all having the BLOCKstate it
    could still receive dirty messages.
    
    Flags:
      - allNodes : all                 (bool)          [create]
          Use the entire graph as the context
    
      - connections : c                (bool)          [create]
          Print the connection information
    
      - dirty : d                      (bool)          [create]
          Only print dirty/clean nodes/plugs/connections.  Default is both
    
      - nodes : n                      (bool)          [create]
          Print the specified nodes (or the entire graph if -all is used)
    
      - nonDeletable : nd              (bool)          [create]
          Include non-deletable nodes as well (normally not of interest)
    
      - outputFile : of                (unicode)       [create]
          Send the output to the file FILE instead of STDERR
    
      - propagation : p                (bool)          [create]
          Only print propagating/not propagating nodes/plugs/connections. Default is both.
    
      - short : s                      (bool)          [create]
          Print using short format instead of long
    
      - size : sz                      (bool)          [create]
          Show datablock sizes for all specified nodes. Return value is tuple of all selected nodes (NumberOfNodes,
          NumberOfDatablocks, TotalDatablockMemory)
    
      - subgraph : sub                 (bool)          [create]
          Print the subgraph affected by the node or plugs (or all nodes in the graph grouped in subgraphs if -all is used)
    
      - type : nt                      (unicode)       [create]
          Filter output to only show nodes of type NODETYPE                                  Flag can have multiple arguments,
          passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.dgInfo`
    """

    pass


def scriptNode(*args, **kwargs):
    """
    scriptNodes contain scripts that are executed when a file is loaded or when the script node is deleted. If a script
    modifies a referenced node, the changes will be tracked as reference edits unless the scriptNode was created with the
    ignoreReferenceEdits flag. The scriptNode command is used to create, edit, query, and test scriptNodes. In query mode,
    return type is based on queried flag.
    
    Flags:
      - afterScript : afterScript      (unicode)       [create,query,edit]
          The script executed when the script node is deleted. C: The default is an empty string. Q: When queried, this flag
          returns a string.
    
      - beforeScript : bs              (unicode)       [create,query,edit]
          The script executed during file load. C: The default is an empty string. Q: When queried, this flag returns a string.
    
      - executeAfter : ea              (bool)          [create]
          Execute the script stored in the .after attribute of the scriptNode. This script is normally executed when the script
          node is deleted.
    
      - executeBefore : eb             (bool)          [create]
          Execute the script stored in the .before attribute of the scriptNode. This script is normally executed when the file is
          loaded.
    
      - ignoreReferenceEdits : ire     (bool)          [create]
          Sets whether changes made to referenced nodes during the execution of the script should be recorded as reference edits.
          This flag must be set when the scriptNode is created. If this flag is not set, changes to referenced nodes will be
          recorded as edits by default.
    
      - name : n                       (unicode)       [create]
          When creating a new scriptNode, this flag specifies the name of the node. If a non-unique name is used, the name will be
          modified to ensure uniqueness.
    
      - scriptType : st                (int)           [create,query,edit]
          Specifies when the script is executed. The following values may be used: 0Execute on demand.1Execute on file load or on
          node deletion.2Execute on file load or on node deletion when not in batch mode. 3Internal4Execute on software
          render5Execute on software frame render6Execute on scene configuration7Execute on time changedC: The default value is 0.
          Q: When queried, this flag returns an int.
    
      - sourceType : stp               (unicode)       [create,query,edit]
          Sets the language type for both the attached scripts. Valid values are mel(enabled by default), and python.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.scriptNode`
    """

    pass


def setAttrMapping(*args, **kwargs):
    """
    This command applies an offset and scale to a specified device attachment. This command is different than the
    setInputDeviceMapping command, which applies a mapping to a device axis. The value from the device is multiplied by the
    scale and the offset is added to this product. With an absolute mapping, the attached attribute gets the resulting
    value. If the mapping is relative, the resulting value is added to the previous calculated value. The calculated value
    will also take into account the setInputDeviceMapping, if it was defined. As an example, if the space ball is setup with
    absolute attachment mappings, pressing in one direction will cause the attached attribute to get a constant value. If a
    relative mapping is used, and the spaceball is pressed in one direction, the attached attribute will get a constantly
    increasing (or constantly decreasing) value. Note that the definition of relative is different than the definition used
    by the setInputDeviceMapping command. In general, both a relative attachment mapping (this command) and a relative
    device mapping (setInputDeviceMapping) should not be used together one the same axis. In query mode, return type is
    based on queried flag.
    
    Flags:
      - absolute : a                   (bool)          [create]
          Make the mapping absolute.
    
      - attribute : at                 (unicode)       [create]
          The attribute used in the attachment.
    
      - axis : ax                      (unicode)       [create]
          The axis on the device used in the attachment.
    
      - clutch : c                     (unicode)       [create]
          The clutch button used in the attachment.
    
      - device : d                     (unicode)       [create]
          The device used in the attachment.
    
      - offset : o                     (float)         [create]
          Specify the offset value.
    
      - relative : r                   (bool)          [create]
          Make the mapping relative.
    
      - scale : s                      (float)         [create]
          Specify the scale value.
    
      - selection : sl                 (bool)          [create]
          This flag specifies the mapping should be on the selected objects                  Flag can have multiple arguments,
          passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.setAttrMapping`
    """

    pass


def untitledFileName():
    """
    Obtain the base filename used for untitled scenes. In localized environments, this string will contain a translated value.
    """

    pass


def reloadImage(*args, **kwargs):
    """
    This command reloads an xpm image from disk. This can be used when the file has changed on disk and needs to be
    reloaded. The first string argument is the file name of the .xpm file. The second string argument is the name of a
    control using the specified pixmap.
    
    
    Derived from mel command `maya.cmds.reloadImage`
    """

    pass


def cmdFileOutput(*args, **kwargs):
    """
    This command will open a text file to receive all of the commands and results that normally get printed to the Script
    Editor window or console. The file will stay open until an explicit -close with the correct file descriptor or a
    -closeAll, so care should be taken not to leave a file open. To enable logging to commence as soon as Maya starts up,
    the environment variable MAYA_CMD_FILE_OUTPUT may be specified prior to launching Maya. Setting MAYA_CMD_FILE_OUTPUT to
    a filename will create and output to that given file. To access the descriptor after Maya has started, use the -query
    and -open flags together.
    
    Flags:
      - close : c                      (int)           [create]
          Closes the file corresponding to the given descriptor. If -3 is returned, the file did not exist. -1 is returned on
          error, 0 is returned on successful close.
    
      - closeAll : ca                  (bool)          [create]
          Closes all open files.
    
      - open : o                       (unicode)       [create,query]
          Opens the given file for writing (will overwrite if it exists and is writable). If successful, a value is returned to
          enable status queries and file close. -1 is returned if the file cannot be opened for writing. The -open flag can also
          be specified in -query mode. In query mode, if the named file is currently opened, the descriptor for the specified file
          is returned, otherwise -1 is returned. This is an easy way to check if a given file is currently open.
    
      - status : s                     (int)           [create,query]
          Queries the status of the given descriptor. -3 is returned if no such file exists, -2 indicates the file is not open, -1
          indicates an error condition, 0 indicates file is ready for writing.                  Flag can have multiple arguments,
          passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.cmdFileOutput`
    """

    pass


def dbpeek(*args, **kwargs):
    """
    The dbpeekcommand is used to analyze the Maya data for information of interest. See a description of the flags for
    details on what types of things can be analyzed.
    
    Flags:
      - allObjects : all               (bool)          [create,query]
          Ignore any specified or selected objects and peek into all applicable objects. The definition of allObjectswill vary
          based on the peek operation being performed - see the flag documentation for details on what it means for a given
          operation. By default if no objects are selected or specified then it will behave as though this flag were set.
    
      - argument : a                   (unicode)       [create,query]
          Specify one or more arguments to be passed to the operation. The acceptable values for the argument string are
          documented in the flag to which they will be applied. If the argument itself takes a value then the value will be of the
          form argname=argvalue.
    
      - count : c                      (int)           [create,query]
          Specify a count to be used by the test. Different tests make different use of the count, query the operation to find out
          how it interprets the value. For example a performance test might use it as the number of iterations to run in the test,
          an output operation might use it to limit the amount of output it produces.
    
      - evaluationGraph : eg           (bool)          [create,query]
          Ignore any nodes that are not explicitly part of the evaluation graph. Usually this means nodes that are affected either
          directly or indirectly by animation. May also tailor the operation to be EM-specific in the areas where the structure of
          the DG differs from the structure of the EM, for example, plug configurations. This is a filter on the currently
          selected nodes, including the use of the allObjectsflag.
    
      - operation : op                 (unicode)       [create,query]
          Specify the peeking operation to perform. The various operations are registered at run time and can be listed by
          querying this flag without a value. If you query it with a value then you get the detail values that peek operation
          accepts and a description of what it does. In query mode, this flag can accept a value.
    
      - outputFile : of                (unicode)       [create,query]
          Specify the location of a file to which the information is to be dumped. Default will return the value from the command.
          Use the special names stdoutand stderrto redirect to your command window. The special name msdevis available when
          debugging on Windows to direct your output to the debug tab in the output window of Visual Studio.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.dbpeek`
    """

    pass


def sceneUIReplacement(*args, **kwargs):
    """
    This command returns existing scene based UI that can be utilized by the scene that is being loaded. It can also delete
    any such UI that is not used by the loading scene.
    
    Flags:
      - clear : cl                     (bool)          [create]
          Frees any resources allocated by the command.
    
      - deleteRemaining : dr           (bool)          [create]
          Delete any UI that is scene dependent and has not been referenced by this command since the last update.
    
      - getNextFilter : gf             (unicode, unicode) [create]
          Returns the next filter of the specified type with the specified name.
    
      - getNextPanel : gp              (unicode, unicode) [create]
          Returns the next panel of the specified type, preferably with the specified label.
    
      - getNextScriptedPanel : gsp     (unicode, unicode) [create]
          Returns the next scripted panel of the specified scripted panel type, preferably with the specified label.
    
      - update : u                     (unicode)       [create]
          Updates the state of the command to reflect the current state of the application.  The string argument is the name of
          the main window pane layout holding the panels.                  Flag can have multiple arguments, passed either as a
          tuple or a list.
    
    
    Derived from mel command `maya.cmds.sceneUIReplacement`
    """

    pass


def _safeEval(s):
    pass


def dgtimer(*args, **kwargs):
    """
    This command measures dependency graph node performance by managing timers on a per-node basis. Logically, each DG node
    has a timer associated with it which records the amount of real time spent in various operations on its plugs. The time
    measurement includes the cost of copying data to the node on behalf of the operation, MEL commands executed by an
    expression contained in an expression invoked by the node, and includes any wait time such as when a fileTexture node
    loads an image file from disk. Most DG operations are reported including compute, draw, and dirty propagation. The
    various operations we measure are called metricsand the types of timers are called timer types. The various metrics are
    always measured when timing is on, but are only queried when specified via the -show and -hide flags. The metrics
    currently supported are listed in detail under the -show flag below. For each metric we support a standard set of timer
    types. There are three of these: selffor self time (the time specific to the node and not its children), inclusive(time
    including children of the node), and count(number of operations of the given metric on the node). The timing mechanism
    which is used by dgtimeris built into the DG itself, thus ALL depend nodes can be timed and there is no need for
    programmers writing plug-ins using the OpenMaya API to add any special code in order for their nodes to be timed -- its
    all handled transparently. The dgtimercommand allows node timers to be turned on, off, reset to zero, and have their
    current value displayed, and these operations can be performed globally on all nodes or on a specific set of nodes
    defined by name, type or parentage. Note that all timer measurements are computed in real time(the same time measurement
    you get from a wristwatch) as opposed to CPU time(which only measures time when the processor is executing your code).
    All times are displayed in seconds. Use the -query flag to display the current timer values on a node, use -on to turn
    on timing, use -off to turn off timing, and -reset to reset timers to zero. To display the values measured during
    timing, there are two approaches. The first method is to use the -query flag can be used to report the information which
    has been measured. The second method is to use the query methods available on the OpenMaya class MFnDependencyNode (see
    the OpenMaya documentation for details). What follows is a description of what is generated via -query. The output is
    broken out into several sections and these are described as follows: SECTION 1:Section 1 of the dgtimer output contains
    global information. This section can be disabled via the -hoHeader flag. These values are reset whenever a global timer
    reset occurs (i.e. dgtimer -reset;is specified). The global values which are reported are: Total real time:the total
    wall-clock time since the last global timer reset. This is the actual time which has been spent as you might measure it
    measure it with your watch. On a multi-processing system, this value will always remain true to to real time (unlike
    userand systime).Total user time:the total time the CPU(s) spent processing Maya not including any system time since the
    last global timer reset.Total sys time:the total time the CPU(s) spent in operating system calls on behalf of Maya since
    the last global timer reset. Summary of each metric for all nodes:a summary of self and count for each metric that we
    measure:Real time in callbacksreports the self time and count for the callbackmetric.Real time in computereports the
    self time and count for the computemetric.Real time in dirty propagationreports the self time and count for the
    dirtymetric.Real time in drawingreports the self time and count for the drawmetric.Real time fetching data from
    plugsreports the self time and count for the fetchmetric.Breakdown of select metrics in greater detail:a reporting of
    certain combinations of metrics that we measure:Real time in compute invoked from callbackreports the self time spent in
    compute when invoked either directly or indirectly by a callback.Real time in compute not invoked from callbackreports
    the self time spent in compute not invoked either directly or indirectly by a callback.SECTION 2:Section 2 of the
    dgtimer -query output contains per-node information. There is a header which describes the meaning of each column,
    followed by the actual per-node data, and this is ultimately followed by a footer which summarises the totals per
    column. Note that the data contained in the footer is the global total for each metric and will include any nodes that
    have been deleted since the last reset, so the value in the footer MAY exceed what you get when you total the individual
    values in the column. To prevent the header and footer from appearing, use the -noHeader flag to just display the per-
    node data. The columns which are displayed are as follows: Rank:The order of this node in the sorted list of all nodes,
    where the list is sorted by -sortMetric and -sortType flag values (if these are omitted the default is to sort by self
    compute time).ON:Tells you if the timer for that node is currently on or off. (With dgtimer, you have the ability to
    turn timing on and off on a per-node basis).Per-metric information:various columns are reported for each metric. The
    name of the metric is reported at in the header in capital letters (e.g. DRAW). The standard columns for each metric
    are:Self:The amount of real time (i.e. elapsed time as you might measure it with a stopwatch) spent performing the
    operation (thus if the metric is DRAW, then this will be time spent drawing the node).Inclusive:The amount of real time
    (i.e. elapsed time as you might measure it with a stopwatch) spent performing the operation including any child
    operations that were invoked on behalf of the operation (thus if the metric is DRAW, then this will be the total time
    taken to draw the node including any child operations).Count:The number of operations that occued on this node (thus if
    the metric is DRAW, then the number of draw operations on the node will be reported).Sort informationif a column is the
    one being used to sort all the per-node dgtimer information, then that column is followed by a Percentand
    Cumulativecolumn which describe a running total through the listing. Note that -sortType noneprevents these two columns
    from appearing and implicitely sorts on selftime.After the per-metric columns, the node name and type are
    reported:TypeThe node type.NameThe name of the node. If the node is file referenced and you are using namespaces, the
    namespace will be included. You can also force the dagpath to be displayed by specifying the -uniqueName flag.Plug-in
    nameIf the node was implemented in an OpenMaya plug-in, the name of that plug-in is reported.SECTION 3:Section 3 of the
    dgtimer -query output describes time spent in callbacks. Note that section 3 only appears when the CALLBACK metric is
    shown (see the -show flag). The first part is SECTION 3.1 lists the time per callback with each entry comprising: The
    name of the callback, such as attributeChangedMsg. These names are internal Maya names, and in the cases where the
    callback is available through the OpenMaya API, the API access to the callback is similarly named.The name is followed
    by a breakdown per callbackId. The callbackId is an identifying number which is unique to each client that is registered
    to a callback and can be deduced by the user, such as through the OpenMaya API. You can cross-reference by finding the
    same callbackId value listed in SECTIONs 3.1 and 3.3.Self time (i.e. real time spent within that callbackId type not
    including any child operations which occur while processing the callback).Percent (see the -sortType flag). Note that
    the percent values are listed to sum up to 100% for that callback. This is not a global percent.Cumulative (see the
    -sortType flag).Inclusive time (i.e. real time spent within that callbackId including any child operations).Count
    (number of times the callbackId was invoked).API lists Yif the callbackId was defined through the OpenMaya API, and Nif
    the callbackId was defined internally within Maya.Node lists the name of the node this callbackId was associated with.
    If the callbackId was associated with more than one node, the string \*multiple\*is printed. If there was no node
    associated with the callbackId (or its a callback type in which the node is hard to deduce), the entry is blank.After
    the callbackId entries are listed, a dashed line is printed followed by a single line listing the self, inclusive and
    count values for the callback. Note that the percent is relative to the global callback time.At the bottom of SECTION
    3.1 is the per-column total. The values printed match the summation at the bottom of the listing in section 2. Note that
    the values from SECTION 3.1 include any nodes that have been deleted since the last reset. The thresholding parameters
    (-threshold, -rangeLower, -rangeUpper and -maxDisplay) are honoured when generating the listing. The sorting of the rows
    and display of the Percent and Cumulative columns obeys the -sortType flag. As the listing can be long, zero entries are
    not displayed. The second part is SECTION 3.2 which lists the data per callbackId. As noted earlier, the callbackId is
    an identifying number which is unique to each client that is registered to a callback and can be deduced by the user,
    such as through the OpenMaya API. The entries in SECTION 3.2 appear as follows: CallbackId the numeric identifier for
    the callback. You can cross reference by finding the same callbackId value listed in SECTIONs 3.1 and 3.3.For each
    callbackId, the data is broken down per-callback:Callback the name of the callback, e.g. attributeChangedMsg.Percent,
    Cumulative, Inclusive, Count, API and Node entries as described in SECTION 3.1.After the callback entries are listed for
    the callbackId, a dashed followed by a summary line is printed. The summary line lists the self, inclusive and count
    values for the callback. Note that the percent is relative to the global callback time.The third part is SECTION 3.3
    which lists data per-callback per-node. The nodes are sorted based on the -sortType flag, and for each node, the
    callbacks are listed, also sorted based on the -sortType flag. As this listing can be long, zero entries are not
    displayed. An important note for SECTION 3.3 is that only nodes which still exist are displayed. If a node has been
    deleted, no infromation is listed.
    
    Flags:
      - combineType : ct               (bool)          [query]
          Causes all nodes of the same type (e.g. animCurveTA) to be combined in the output display.
    
      - hide : hi                      (unicode)       [create,query]
          This flag is the converse of -show. As with -show, it is a query-only flag which can be specified multiple times. If you
          do specify -hide, we display all columns except those listed by the -hide flags.
    
      - hierarchy : h                  (bool)          [create,query]
          Used to specify that a hierarchy of the dependency graph be affected, thus -reset -hierarchy -name ballwill reset the
          timers on the node named balland all of its descendents in the dependency graph.
    
      - maxDisplay : m                 (int)           [query]
          Truncates the display so that only the most expenive nentries are printed in the output display.
    
      - name : n                       (unicode)       [create,query]
          Used in conjunction with -reset or -query to specify the name of the node to reset or print timer values for. When
          querying a single timer, only a single line of output is generated (i.e. the global timers and header information is
          omitted). Note that one can force output to the script editor window via the -outputFile MELoption to make it easy to
          grab the values in a MEL script. Note: the -name and -type flag cannot be used together.
    
      - noHeader : nh                  (bool)          [create,query]
          Used in conjunction with -query to prevent any header or footer information from being printed. All that will be output
          is the per-node timing data. This option makes it easier to parse the output such as when you output the query to a file
          on disk using the -outputFileoption.
    
      - outputFile : o                 (unicode)       [query]
          Specifies where the output of timing or tracing is displayed. The flag takes a string argument which accepts three
          possible values: The name of a file on disk.Or the keyword stdout, which causes output to be displayed on the terminal
          window (Linux and Macintosh), and the status window on Windows.Or the keyword MEL, which causes output to be displayed
          in the Maya Script Editor (only supported with -query).The stdoutsetting is the default behaviour. This flag can be used
          with the -query flag as well as the -trace flag. When used with the -trace flag, any tracing output will be displayed on
          the destination specified by the -outputFile (or stdout if -outputFile is omitted). Tracing operations will continue to
          output to the destination until you specify the -trace and -outputFile flags again. When used with the -query flag,
          timing output will be displayed to the destination specified by the -outputFile (or stdoutif -outputFile is omitted).
          Here are some examples of how to use the -query, -trace and -outputFile flags: Example: output the timing information to
          a single file on disk:dgtimer -on;                                       // Turn on timing create some animated scene
          content; play -wait;                                        // Play the scene through dgtimer -query -outputFile
          /tmp/timing.txt// Output node timing information to a file on disk Example: output the tracing information to a single
          file on disk:dgtimer -on;                                       // Turn on timing create some animated scene content;
          dgtimer -trace on -outputFile /tmp/trace.txt// Turn on tracing and output the results to file play -wait;
          // Play the scene through; trace info goes to /tmp/trace.txt dgtimer -query;                                    // But
          the timing info goes to the terminal window play -wait;                                        // Play the scene again,
          trace info still goes to /tmp/trace.txt Example: two runs, outputting the trace information and timing information to
          separate files:dgtimer -on;                                       // Turn on timing create some animated scene content;
          dgtimer -trace on -outputFile /tmp/trace1.txt// Turn on tracing and output the results to file play -wait;
          // Play the scene through dgtimer -query -outputFile /tmp/query1.txt// Output node timing information to another file
          dgtimer -reset; dgtimer -trace on -outputFile /tmp/trace2.txt// Output tracing results to different file play -wait;
          // Play the scene through dgtimer -query -outputFile /tmp/query2.txt// Output node timing information to another file
          Tips and tricks:Outputting the timing results to the script editor makes it easy to use the results in MEL e.g. string
          $timing[] = `dgtimer -query -outputFile MEL`.It is important to note that the -outputFile you specify with -trace is
          totally independent from the one you specify with -query.If the file you specify already exists, Maya will empty the
          file first before outputting data to it (and if the file is not writable, an error is generated instead).
    
      - overhead : oh                  (bool)          [create,query]
          Turns on and off the measurement of timing overhead. Under ordinary circumstances the amount of timing overhead is
          minimal compared with the events being measured, but in complex scenes, one might find the overhead to be measurable. By
          default this option is turned off. To enable it, specify dgtimer -overhead trueprior to starting timing. When querying
          timing, the overhead is reported in SECTION 1.2 of the dgtimer output and is not factored out of each individual
          operation.
    
      - rangeLower : rgl               (float)         [create]
          This flag can be specified to limit the range of nodes which are displayed in a query, or the limits of the heat map
          with -updateHeatMap. The value is the lower percentage cutoff for the nodes which are processed. There is also a
          -rangeLower flag which sets the lower range limit. The default value is 0, meaning that all nodes with timing value
          below the upper range limit are considered.
    
      - rangeUpper : rgu               (float)         [create]
          This flag can be specified to limit the range of nodes which are displayed in a query, or the limits of the heat map
          with -updateHeatMap. The value is the upper percentage cutoff for the nodes which are processed. There is also a
          -rangeLower flag which sets the lower range limit. The default value is 100, meaning that all nodes with timing value
          above the lower range limit are considered.
    
      - reset : r                      (bool)          [create]
          Resets the node timers to zero. By default, the timers on all nodes as well as the global timers are reset, but if
          specified with the -name or -type flags, only the timers on specified nodes are reset.
    
      - returnCode : rc                (unicode)       [create,query]
          This flag has been replaced by the more general -returnType flag. The -returnCode flag was unfortunately specific to the
          compute metric only. It exists only for backwards compatability purposes. It will be removed altogether in a future
          release. Here are some handy equivalences: To get the total number of nodes:OLD WAY: dgtimer -rc nodecount -q;//
          Result:325//NEW WAY: dgtimer -returnType total -sortType none -q;// Result:325//OLD WAY: dgtimer -rc count -q;//
          Result:1270//To get the sum of the compute count column:NEW WAY: dgtimer -returnType total -sortMetric compute -sortType
          count -q;// Result:1270//OLD WAY: dgtimer -rc selftime -q;// Result:0.112898//To get the sum of the compute self
          column:NEW WAY: dgtimer -returnType total -sortMetric compute -sortType self -q;// Result:0.112898//
    
      - returnType : rt                (unicode)       [query]
          This flag specifies what the double value returned by the dgtimer command represents. By default, the value returned is
          the global total as displayed in SECTION 1 for the column we are sorting on in the per-node output (the sort column can
          be specified via the -sortMetric and -sortType flags). However, instead of the total being returned, the user can
          instead request the individual entries for the column. This flag is useful mainly for querying without forcing any
          output. The flag accepts the values total, to just display the column total, or allto display all entries individually.
          For example, if you want to get the total of draw self time without any other output simply specify the following:
          dgtimer -returnType total -sortMetric draw -sortType self -threshold 100 -noHeader -query;// Result: 7718.01 // To
          instead get each individual entry, change the above query to: dgtimer -returnType all -sortMetric draw -sortType self
          -threshold 100 -noHeader -query;// Result: 6576.01 21.91 11.17 1108.92 // To get the inclusive dirty time for a specific
          node, use -name as well as -returnType all: dgtimer -name virginia-returnType all -sortMetric dirty -sortType inclusive
          -threshold 100 -noHeader -query;Note: to get the total number of nodes, use -sortType none -returnType total.  To get
          the on/off status for each node, use -sortType none -returnType all.
    
      - show : sh                      (unicode)       [create,query]
          Used in conjunction with -query to specify which columns are to be displayed in the per-node section of the output.
          -show takes an argument, which can be all(to display all columns), callback(to display the time spent during any
          callback processing on the node not due to evaluation), compute(to display the time spent in the node's compute
          methods), dirty(to display time spent propagating dirtiness on behalf of the node), draw(to display time spent drawing
          the node), compcb(to display time spent during callback processing on node due to compute), and compncb(to display time
          spent during callback processing on node NOT due to compute). The -show flag can be used multiple times, but cannot be
          specified with -hide. By default, if neither -show, -hide, or -sort are given, the effective display mode is: dgtimer
          -show compute -query.
    
      - sortMetric : sm                (unicode)       [create,query]
          Used in conjunction with -query to specify which metric is to be sorted on when the per-node section of the output is
          generated, for example drawtime. Note that the -sortType flag can also be specified to define which timer is sorted on:
          for example dgtimer -sortMetric draw -sortType count -querywill sort the output by the number of times each node was
          drawn. Both -sortMetric and -sortType are optional and you can specify one without the other. The -sortMetric flag can
          only be specified at most once. The flag takes the following arguments: callback(to sort on time spent during any
          callback processing on the node), compute(to sort on the time spent in the node's compute methods), dirty(to sort on the
          time spent propagating dirtiness on behalf of the node), draw(to sort on time spent drawing the node), fetch(to sort on
          time spent copying data from the datablock), The default, if -sortMetric is omitted, is to sort on the first displayed
          column. Note that the sortMetric is independent of which columns are displayed via -show and -hide. Sort on a hidden
          column is allowed. The column selected by -sortMetric and -sortType specifies which total is returned by the dgtimer
          command on the MEL command line. This flag is also used with -updateHeatMap to specify which metric to build the heat
          map for.
    
      - sortType : st                  (unicode)       [create,query]
          Used in conjunction with -query to specify which timer is to be sorted on when the per-node section of the output is
          generated, for example selftime. Note that the -sortMetric flag can also be specified to define which metric is sorted
          on: for example dgtimer -sortMetric draw -sortType count -querywill sort the output by the number of times each node was
          drawn. Both -sortMetric and -sortType are optional and you can specify one without the other. The -sortType flag can be
          specified at most once. The flag takes the following arguments: self(to sort on self time, which is the time specific to
          the node and not its children), inclusive(to sort on the time including children of the node), count(to sort on the
          number of times the node was invoked). and none(to sort on self time, but do not display the Percent and Cumulative
          columns in the per-node display, as well as cause the total number of nodes in Maya to be returned on the command line).
          The default, if -sortType is omitted, is to sort on self time. The column selected by -sortMetric and -sortType
          specifies which total is returned by the dgtimer command on the MEL command line. The global total as displayed in
          SECTION 1 of the listing is returned. The special case of -sortType nonecauses the number of nodes in Maya to instead be
          returned. This flag is also used with -updateHeatMap to specify which metric to build the heat map for.
    
      - threshold : th                 (float)         [query]
          Truncates the display once the value falls below the threshold value. The threshold applies to whatever timer is being
          used for sorting. For example, if our sort key is self compute time (i.e. -sortMetric is computeand -sortType is self)
          and the threshold parameter is 20.0, then only nodes with a compute self-time of 20.0 or higher will be displayed. (Note
          that -threshold uses absolute time. There are the similar -rangeUpper and -rangeLower parameters which specify a range
          using percentage).
    
      - timerOff : off                 (bool)          [create,query]
          Turns off node timing. By default, the timers on all nodes are turned off, but if specified with the -name or -type
          flags, only the timers on specified nodes are turned off. If the timers on all nodes become turned off, then global
          timing is also turned off as well.
    
      - timerOn : on                   (bool)          [create,query]
          Turns on node timing. By default, the timers on all nodes are turned on, but if specified with the -name or -type flags,
          only the timers on specified nodes are turned on. The global timers are also turned on by this command. Note that
          turning on timing does NOT reset the timers to zero. Use the -reset flag to reset the timers. The idea for NOT resetting
          the timers is to allow the user to arbitrarily turn timing on and off and continue to add to the existing timer values.
    
      - trace : tr                     (bool)          [create]
          Turns on or off detailed execution tracing. By default, tracing is off. If enabled, each timeable operation is logged
          when it starts and again when it ends. This flag can be used in conjunction with -outputFile to specify where the output
          is generated to. The following example shows how the output is formatted:dgtimer:begin: compute 3 particleShape1Deformed
          particleShape1Deformed.lastPosition The above is an example of the output when -trace is true that marks the start of an
          operation. For specific details on each field: the dgtimer:begin:string is an identifying marker to flag that this is a
          begin operation record. The second argument, computein our example, is the operation metric. You can view the output of
          each given metric via dgtimer -qby specifying the -show flag. The integer which follows (3 in this case) is the depth in
          the operation stack, and the third argument is the name of the node (particleShape1Deformed). The fourth argument is
          specific to the metric. For compute, it gives the name of the plug being computed. For callback, its the internal Maya
          name of the callback. For dirty, its the name of the plug that dirtiness is being propagated from.dgtimer:end: compute 3
          particleShape1Deformed 0.000305685 0.000305685 The above is the end operation record. The compute, 3and
          particleShapeDeformedarguments were described in the dgtimer:beginoverview earlier. The two floating-point arguments are
          self time and inclusive time for the operation measured in seconds. The inclusive measure lists the total time since the
          matching dgtimer:begin:entry for this operation, while the self measure lists the inclusive time minus any time consumed
          by child operations which may have occurred during execution of the current operation. As noted elsewhere in this
          document, these two times are wall clock times, measuring elapsed time including any time in which Maya was idle or
          performing system calls. Since dgtimer can measure some non-node qualities in Maya, such as global message callbacks, a
          -is displayed where the node name would ordinarily be displayed. The -means not applicable.
    
      - type : t                       (unicode)       [create,query]
          Used in conjunction with -reset or -query to specify the type of the node(s) (e.g. animCurveTA) to reset or print timer
          values for. When querying, use of the -combineType flag will cause all nodes of the same type to be combined into one
          entry, and only one line of output is generated (i.e. the global timers and header information is omitted). Note: the
          -name and -type flag cannot be used together.
    
      - uniqueName : un                (bool)          [create,query]
          Used to specify that the DAG nodes listed in the output should be listed by their unique names.  The full DAG path to
          the object will be printed out instead of just the node name.
    
      - updateHeatMap : uhm            (int)           [create]
          Forces Maya's heat map to rebuild based on the specified parameters. The heat map is an internal dgtimer structure used
          in mapping intensity values to colourmap entries during display by the HyperGraph Editor. There is one heat map shared
          by all editors that are using heat map display mode. Updating the heat map causes the timer values on all nodes to be
          analysed to compose the distribution of entries in the heat map. The parameter is the integer number of divisions in the
          map and should equal the number of available colours for displaying the heat map. This flag can be specified with the
          -rangeLower and -rangeUpper flags to limit the range of displayable to lie between the percentile range. The dgtimer
          command returns the maximum timing value for all nodes in Maya for the specified metric and type. Note: when the display
          range includes 0, the special zeroth (exactly zero) slot in the heat map is avilable.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.dgtimer`
    """

    pass


def importFile(filepath, **kwargs):
    """
    Import the specified file. Returns the name of the imported file.                  
    
    Flags:
      - loadNoReferences:
          This flag is obsolete and has been replaced witht the loadReferenceDepth flag. When used with the -open flag, no
          references will be loaded. When used with -i/import, -r/reference or -lr/loadReference flags, will load the top-most
          reference only.
      - loadReferenceDepth:
          Used to specify which references should be loaded. Valid types are all, noneand topOnly, which will load all references,
          no references and top-level references only, respectively. May only be used with the -o/open, -i/import, -r/reference or
          -lr/loadReference flags. When noneis used with -lr/loadReference, only path validation is performed. This can be used to
          replace a reference without triggering reload. Not using loadReferenceDepth will load references in the same loaded or
          unloaded state that they were in when the file was saved. Additionally, the -lr/loadReference flag supports a fourth
          type, asPrefs. This will force any nested references to be loaded according to the state (if any) stored in the current
          scene file, rather than according to the state saved in the reference file itself.
      - defaultNamespace:
          Use the default name space for import and referencing.  This is an advanced option.  If set, then on import or
          reference, Maya will attempt to place all nodes from the imported or referenced file directly into the root (default)
          name space, without invoking any name clash resolution algorithms.  If the names of any of the new objects    already
          exist in the root namespace, then errors will result. The user of this flag is responsible for creating a name clash
          resolution mechanism outside of Maya to avoid such errors. Note:This flag    is intended only for use with custom file
          translators written through    the API. Use at your own risk.
      - deferReference:
          When used in conjunction with the -reference flag, this flag determines if the reference is loaded, or if loading is
          deferred.C: The default is false.Q: When queried, this flag returns true if the reference is deferred, or false if the
          reference is not deferred. If this is used with -rfn/referenceNode, the -rfn flag must come before -q.
      - groupReference:
          Used only with the -r or the -i flag. Used to group all the imported/referenced items under a single transform.
      - groupName:
          Used only with the -gr flag. Optionally used to set the name of the transform node that the imported/referenced items
          will be grouped under.
      - renameAll:
          If true, rename all newly-created nodes, not just those whose names clash with existing nodes. Only available with
          -i/import.
      - renamingPrefix:
          The string to use as a prefix for all objects from this file. This flag has been replaced by -ns/namespace.
      - swapNamespace:
          Can only be used in conjunction with the -r/reference or -i/import flags. This flag will replace any occurrences of a
          given namespace to an alternate specified namespace. This namespace swapwill occur as the file is referenced in. It
          takes in two string arguments. The first argument specifies the namespace to replace. The second argument specifies the
          replacement namespace. Use of this flag, implicitly enables the use of namespaces and cannot be used with
          deferReference.
      - returnNewNodes:
          Used to control the return value in open, import, loadReference, and reference operations. It will force the file
          command to return a list of new nodes added to the current scene.
      - preserveReferences:
          Modifies the various import/export flags such that references are imported/exported as actual references rather than
          copies of those references.
    
    Derived from mel command `maya.cmds.file`
    """

    pass


def detachDeviceAttr(*args, **kwargs):
    """
    This command detaches connections between device axes and node attributes.  The command line arguments are the same as
    for the corresponding attachDeviceAttr except for the clutch argument which can not be used in this command. In query
    mode, return type is based on queried flag.
    
    Flags:
      - all : all                      (bool)          [create]
          Delete all attachments on every device.
    
      - attribute : at                 (unicode)       [create]
          The attribute to detach. This flag must be used with the -d/device flag.
    
      - axis : ax                      (unicode)       [create]
          The axis to detach. This flag must be used with the -d/device flag.
    
      - device : d                     (unicode)       [create]
          Delete the attachment for this device. If the -ax/axis flag is not used, all of the attachments connected to this device
          are detached.
    
      - selection : sl                 (bool)          [create]
          Detaches selection attachments.                  Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.detachDeviceAttr`
    """

    pass


def flushUndo(*args, **kwargs):
    """
    Removes everything from the undo queue, freeing up memory.
    
    
    Derived from mel command `maya.cmds.flushUndo`
    """

    pass


def displayInfo(*args, **kwargs):
    pass


def dirmap(*args, **kwargs):
    """
    Use this command to map a directory to another directory. The first argument is the directory to map, and the second is
    the destination directory to map to. Directories must both be absolute paths, and should be separated with forward
    slashes ('/'). The mapping is case-sensitive on all platforms. This command can be useful when moving projects to
    another machine where some textures may not be contained in the Maya project, or when a texture archive moves to a new
    location. This command is not necessary when moving a (self-contained) project from one machine to another - instead
    copy the entire project over and set the Maya project to the new location. For one-time directory moves, if the command
    is enabled and the mapping configured correctly, when a scene is opened and saved the mapped locations will be reflected
    in the filenames saved with the file. To set up a permanent mapping the command should be enabled and the mappings set
    up in a script which is executed every time you launch Maya (userSetup.mel is sourced on startup). The directory
    mappings and enabled state are not preserved between Maya sessions. This command requires one mainflag that specifies
    the action to take. Flags are:-[m|um|gmd|gam|cd|en]
    
    Flags:
      - convertDirectory : cd          (unicode)       [create]
          Convert a file or directory. Returns the name of the mapped file or directory, if the command is enabled. If the given
          string contains one of the mapped directories, the return value will have that substring replaced with the mapped one.
          Otherwise the given argument string will be returned. If the command is disabled the given argument is always returned.
          Checks are not made for whether the file or directory exists. If the given string is a directory it should have a
          trailing '/'.
    
      - enable : en                    (bool)          [create,query]
          Enable directory mapping. Directory mapping is off when you start Maya. If enabled, when opening Maya scenes, file
          texture paths (and other file paths) will be converted when the scene is opened. The -cd flag only returns mapped
          directories when -enable is true. Query returns whether mapping has been enabled.
    
      - getAllMappings : gam           (bool)          [create]
          Get all current mappings. Returns string array of current mappings in format: [redirect1, replacement1, ... redirectN,
          replacementN]
    
      - getMappedDirectory : gmd       (unicode)       [create]
          Get the mapped redirected directory. The given argument must exactly match the first string used with the -mapDirectory
          flag.
    
      - mapDirectory : m               (unicode, unicode) [create]
          Map a directory - the first argument is mapped to the second. Neither directory needs to exist on the local machine at
          the time of invocation.
    
      - unmapDirectory : um            (unicode)       [create]
          Unmap a directory. The given argument must exactly match the argument used with the -mapDirectory flag.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.dirmap`
    """

    pass


def internalVar(*args, **kwargs):
    """
    This command returns the values of internal variables.  No modification of these variables is supported.
    
    Flags:
      - userAppDir : uad               (bool)          [create]
          Return the user application directory.
    
      - userBitmapsDir : ubd           (bool)          [create]
          Return the user bitmaps prefs directory.
    
      - userHotkeyDir : uhk            (bool)          [create]
          Return the user hotkey directory.
    
      - userMarkingMenuDir : umm       (bool)          [create]
          Return the user marking menu directory.
    
      - userPrefDir : upd              (bool)          [create]
          Return the user preference directory.
    
      - userPresetsDir : ups           (bool)          [create]
          Return the user presets directory.
    
      - userScriptDir : usd            (bool)          [create]
          Return the user script directory.
    
      - userShelfDir : ush             (bool)          [create]
          Return the user shelves directory.
    
      - userTmpDir : utd               (bool)          [create]
          Return a temp directory.  Will check for TMPDIR environment variable, otherwise will return the current directory.
    
      - userWorkspaceDir : uwd         (bool)          [create]
          Return the user workspace directory (also known as the projects directory).                  Flag can have multiple
          arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.internalVar`
    """

    pass


def attrCompatibility(*args, **kwargs):
    """
    This command is used by Maya to handle compatibility issues between file format versions by providing a mechanism to
    describe differences between two versions.  Plug-in writers can make use of this command to handle attribute
    compatibility changes to files.The first optional command argument argument is a node type name and the second optional
    command argument is the short name of an attribute.Warning:Only use this command to describe changes in names or
    attributes of nodes that youhave written as plugins.  Do notuse this command to change information about builtin
    dependency graph nodes. Removing attributes on a plug-in node is a special case. Use a separate attrCompatibility call
    with pluginNode flag and name so that these attributes can be tracked even though the plug-in may not be loaded. Only
    one flag may be used per invocation of the command. If multiple flags are provided one will arbitrarily be chosen as the
    action to perform and the others will be silently ignored.
    
    Flags:
      - addAttr : a                    (bool)          [create]
          Add the given attribute to the named node.
    
      - clear : clr                    (bool)          [create]
          Clear out the compatibility table. This is only used internally for debugging purposes.
    
      - dumpTable : dmp                (bool)          [create]
          Dump the current contents of the compatibility table. This is only used internally for debugging purposes.
    
      - enable : e                     (bool)          [create]
          Enable or disable the compatibility table. This is only used internally for debugging purposes.
    
      - nodeRename : nr                (unicode)       [create]
          Replace all uses of the node type 'nodeName' with given string.
    
      - pluginNode : pn                (unicode)       [create]
          Registers the string argument as a plug-in node type. This is necessary for subsequent attrCompatibility calls that
          reference node attributes of unloaded plug-ins. Specifically, this works in the case when attributes are being removed.
    
      - removeAttr : rm                (bool)          [create]
          Remove the given attribute from the named node.
    
      - renameAttr : r                 (unicode)       [create]
          Change the short name of the attribute specified in the command's arguments to the new short name provided as a
          parameter to this flag. Once the mapping between short names has been established, Maya will handle the long names
          automatically.
    
      - type : typ                     (unicode)       [create]
          Change the type of the given attribute to the given type.
    
      - version : v                    (unicode)       [create]
          Set the version target for subsequent commands to the given string.                  Flag can have multiple arguments,
          passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.attrCompatibility`
    """

    pass


def cacheFileMerge(*args, **kwargs):
    """
    If selected/specified caches can be successfully merged, will return the start/end frames of the new cache followed by
    the start/end frames of any gaps in the merged cache for which no data should be written to file. In query mode, will
    return the names of geometry associated with the specified cache file nodes.
    
    Flags:
      - endTime : et                   (time)          [create]
          Specifies the end frame of the merge range. If not specified, will figure out range from times of caches being merged.
    
      - geometry : g                   (bool)          [query]
          Query-only flag used to find the geometry nodes associated with the specified cache files.
    
      - startTime : st                 (time)          [create]
          Specifies the start frame of the merge range. If not specified, will figure out range from the times of the caches being
          merged.                                   Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.cacheFileMerge`
    """

    pass


def listReferences(parentReference=None, recursive=False, namespaces=False, refNodes=False, references=True, loaded=None, unloaded=None):
    """
    Like iterReferences, except returns a list instead of an iterator.
    
    
    returns references in the scene as a list of value tuples.
    
    The values in the tuples can be namespaces, refNodes (as PyNodes), and/or
    references (as FileReferences), and are controlled by their respective
    keywords (and are returned in that order).  If only one of the three options
    is True, the result will not be a list of value tuples, but will simply be a
    list of values.
    
    Parameters
    ----------
    parentReference : string, `Path`, or `FileReference`
        a reference to get sub-references from. If None (default), the current
        scene is used.
    
    recursive : bool
        recursively determine all references and sub-references
    
    namespaces : bool
        controls whether namespaces are returned
    
    refNodes : bool
        controls whether reference PyNodes are returned
    
    refNodes : bool
        controls whether FileReferences returned
    
    recurseType : string
        if recursing, whether to do a 'breadth' or 'depth' first search;
        defaults to a 'depth' first
    
    loaded : bool or None
        whether to return loaded references in the return result; if both of
        loaded/unloaded are not given (or None), then both are assumed True;
        if only one is given, the other is assumed to have the opposite boolean
        value
    
    unloaded : bool or None
        whether to return unloaded references in the return result; if both of
        loaded/unloaded are not given (or None), then both are assumed True;
        if only one is given, the other is assumed to have the opposite boolean
        value
    """

    pass


def requires(*args, **kwargs):
    """
    This command is used during file I/O to specify the requirements needed to load the given file.  It defines what file
    format version was used to write the file, or what plug-ins are required to load the scene. The first string names a
    product (either maya, or a plug-in name) The second string gives the version. This command is only useful during file
    I/O, so users should not have any need to use this command themselves. The flags -nodeTypeand -dataTypespecify the node
    types and data types defined by the plug-in. When Maya open a scene file, it runs requirescommand in the file and load
    required plug-ins. But some plug-ins may be not loaded because they are missing. The flags -nodeTypeand -dataTypeare
    used by the missing plug-ins. If one plug-in is missing, nodes and data created by this plug-in are created as unknown
    nodes and unknown data. Maya records their original types for these unknown nodes and data. When these nodes and data
    are saved back to file, it will be possible to determine the associated missing plug-ins. And when export selected
    nodes, Maya can write out the exact required plug-ins. The flags -nodeTypeand -dataTypeis optional. In this command, if
    these flags are not given for one plug-in and the plug-in is missing, the requirescommand of this plug-in will always be
    saved back.
    
    Flags:
      - dataType : dt                  (unicode)       [create]
          Specify a data type defined by this plug-in. The data type is specified by MFnPlugin::registerData() when register the
          plug-in.
    
      - nodeType : nt                  (unicode)       [create]
          Specify a node type defined by this plug-in. The node type is specified by MFnPlugin::registerNode() when register the
          plug-in.                  Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.requires`
    """

    pass


def newFile(*args, **kwargs):
    """
    Initialize the scene. Returns untitled scene with default location.                  
    
    Flags:
      - force:
          Force an action to take place. (new, open, save, remove reference, unload reference) Used with removeReference to force
          remove reference namespace even if it has contents. Cannot be used with removeReference if the reference resides in the
          root namespace. Used with unloadReference to force unload reference even if the reference node is locked, without
          prompting a dialog that warns user about the lost of edits.
      - type:
          Set the type of this file.  By default this can be any one of: mayaAscii, mayaBinary, mel,  OBJ, directory, plug-in,
          audio, move, EPS, Adobe(R) Illustrator(R), imageplug-ins may define their own types as well.Return a string array of
          file types that match this file.
    
    Derived from mel command `maya.cmds.file`
    """

    pass


def melInfo(*args, **kwargs):
    """
    This command returns the names of all global MEL procedures that are currently defined as a string array. The user can
    query the definition of each MEL procedure using the whatIscommand.
    
    
    Derived from mel command `maya.cmds.melInfo`
    """

    pass


def _getTypeFromExtension(path, mode='write'):
    """
    Parameters
    ----------
    path : str
        path from with to pull the extension from - note that it may NOT be
        ONLY the extension - ie, "obj" and ".obj", will not work, but
        "foo.obj" will
    mode : {'write', 'read'}
        the type is basically a string name of a file translator, which can
        have different ones registered for reading or writing; this specifies
        whether you're looking for the read or write translator
    """

    pass


def exportSelectedAnim(exportPath, **kwargs):
    """
    Export all animation nodes and animation helper nodes from the selected objects in the scene. See -ean/exportAnim flag description for details on usage of animation files.                  
    
    Flags:
      - force:
          Force an action to take place. (new, open, save, remove reference, unload reference) Used with removeReference to force
          remove reference namespace even if it has contents. Cannot be used with removeReference if the reference resides in the
          root namespace. Used with unloadReference to force unload reference even if the reference node is locked, without
          prompting a dialog that warns user about the lost of edits.
      - type:
          Set the type of this file.  By default this can be any one of: mayaAscii, mayaBinary, mel,  OBJ, directory, plug-in,
          audio, move, EPS, Adobe(R) Illustrator(R), imageplug-ins may define their own types as well.Return a string array of
          file types that match this file.
    
    Derived from mel command `maya.cmds.file`
    """

    pass


def unloadPlugin(*args, **kwargs):
    """
    Unload plug-ins from Maya. After the successful execution of this command, plug-in services will no longer be available.
    
    Flags:
      - addCallback : ac               (script)        [create]
          Add a procedure to be called just before a plugin is unloaded. The procedure should have one string argument, which will
          be the plugin's name.
    
      - force : f                      (bool)          [create]
          Unload the plugin even if it is providing services.  This is not recommended.  If you unload a plug-in that implements a
          node or data type in the scene, those instances will be converted to unknown nodes or data and the scene will no longer
          behave properly. Maya may become unstable or even crash. If you use this flag you are advised to save your scene in
          MayaAscii format and restart Maya as soon as possible.
    
      - removeCallback : rc            (script)        [create]
          Remove a procedure which was previously added with -addCallback.                  Flag can have multiple arguments,
          passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.unloadPlugin`
    """

    pass


def exportAll(exportPath, **kwargs):
    """
    Export everything into a single file. Returns the name of the exported file.                  
    
    Flags:
      - force:
          Force an action to take place. (new, open, save, remove reference, unload reference) Used with removeReference to force
          remove reference namespace even if it has contents. Cannot be used with removeReference if the reference resides in the
          root namespace. Used with unloadReference to force unload reference even if the reference node is locked, without
          prompting a dialog that warns user about the lost of edits.
      - preserveReferences:
          Modifies the various import/export flags such that references are imported/exported as actual references rather than
          copies of those references.
      - type:
          Set the type of this file.  By default this can be any one of: mayaAscii, mayaBinary, mel,  OBJ, directory, plug-in,
          audio, move, EPS, Adobe(R) Illustrator(R), imageplug-ins may define their own types as well.Return a string array of
          file types that match this file.
    
    Derived from mel command `maya.cmds.file`
    """

    pass


def listDeviceAttachments(*args, **kwargs):
    """
    This command lists the current set of device attachments. The listing is in the form of the commands required to
    recreate them.  This includes both attachments and device mappings.
    
    Flags:
      - attribute : at                 (unicode)       [create]
          specify the attribute attachments to list
    
      - axis : ax                      (unicode)       [create]
          specify the axis attachments to list
    
      - clutch : c                     (unicode)       [create]
          List only attachment clutched with this button
    
      - device : d                     (unicode)       [create]
          specify which device attachments to list
    
      - file : f                       (unicode)       [create]
          Specify the name of the file to write out device attachments.
    
      - selection : sl                 (bool)          [create]
          This flag list only attachments on selection
    
      - write : w                      (bool)          [create]
          Write out device attachments to a file specified by the -f flag, is set.  If -f is not set, it'll write out to a file
          named for the device.                  Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.listDeviceAttachments`
    """

    pass


def getModifiers(*args, **kwargs):
    """
    This command returns the current state of the modifier keys. The state of each modifier can be obtained by testing for
    the modifier's corresponding bit value in the return value. Shift is bit 1, Ctrl is bit 3, Alt is bit 4, and bit 5 is
    the 'Windows' key on Windows keyboards and the Command key on Mac keyboards.  See the provided example for more details
    on testing for each modifier's bit value.
    
    
    Derived from mel command `maya.cmds.getModifiers`
    """

    pass


def dbcount(*args, **kwargs):
    """
    The dbcountcommand is used to print and manage a list of statistics collected for counting operations.  These statistics
    are displayed as a list of hits on a particular location in code, with added reference information for
    pointers/strings/whatever. If -reset is not specified then statistics are printed.
    
    Flags:
      - enabled : e                    (bool)          [create]
          Set the enabled state of the counters ('on' to enable, 'off' to disable). Returns the list of all counters affected.
    
      - file : f                       (unicode)       [create]
          Destination file of the enabled count objects.  Use the special names stdoutand stderrto redirect to your command
          window.  As well, the special name msdevis available on NT to direct your output to the debug tab in the output window
          of Developer Studio.
    
      - keyword : k                    (unicode)       [create]
          Print only the counters whose name matches this keyword (default is all).
    
      - list : l                       (bool)          [create]
          List all available counters and their current enabled status. (The only thing you can do when counters are disabled.)
    
      - maxdepth : md                  (int)           [create]
          Maximum number of levels down to traverse and report. 0 is the default and it means continue recursing as many times as
          are requested.
    
      - quick : q                      (bool)          [create]
          Display only a summary for each counter type instead of the full details.
    
      - reset : r                      (bool)          [create]
          Reset all counters back to 0 and remove all but the top level counters. Returns the list of all counters affected.
    
      - spreadsheet : s                (bool)          [create]
          Display in spreadsheet format instead of the usual nested braces. This will include a header row that contains 'Count
          Level1 Level2 Level3...', making the data suitable for opening directly in a spreadsheet table.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.dbcount`
    """

    pass


def filePathEditor(*args, **kwargs):
    """
    Maya can reference and use external files, such as textures or other Maya scenes. This command is used to get the
    information about those file paths and modify them in bulk. By default, only the most frequently used types of files are
    presented to the user:  TextureScene referenceAudioImage planeFor the command to manage more file types, those must be
    explicitly requested by the caller using the registerTypeflag. This flag tells the command about attributes or nodes
    that are to reveal their paths when the command is used.  Currently, the attributes specified through this flag must
    have the usedAsFileNameproperty. Supported nodes are referenceand plug-in nodes. For example: brush.flowerImageor
    referencecan be used as value for this flag.  Conversely, the deregisterTypeflag can be used to tell the command to stop
    handling certain attributes or nodes.  Once the set of attributes and nodes to be searched for external files is
    selected, the command can be used to obtain a list of plugs that contain file names. Additional information can be
    obtained, such as each file's name, directory, and report whether the file exists. Additional information about the
    associated node or plug can also be obtained, such as its name, type and label.  Finally, the command can be used to
    perform various manipulations such as editing the paths, remapping the files or verifying the presence of identically-
    named files in target directories. See the repath, copyAndRepathand replaceFieldflags for more information.  The results
    of these manipulations can be previewed before they are applied using the previewflag.                In query mode,
    return type is based on queried flag.
    
    Flags:
      - attributeOnly : ao             (bool)          [query]
          Used with listFilesto return the node and attribute name that are using the files.
    
      - attributeType : at             (unicode)       [query]
          Query the attribute type for the specified plug.
    
      - byType : bt                    (unicode)       [query]
          Used with listFilesto query files that are used by the specified node type or attribute type.
    
      - copyAndRepath : cr             (unicode, unicode) [create]
          Copy a source file to the destination path and repath the plug data to the new file. The source file must have the same
          name as the one in the plug. The command will look for the file at the specified location first. If not found, the
          command will try to use the original file in the plug. If the file is still not found, nothing is done.
    
      - deregisterType : dt            (unicode)       [create]
          Deregister a file type from the list of registered types so the command stops handling it. Unless the temporaryflag is
          used, the type will be removed from the preferences will not reappear on application restart. When the temporaryflag is
          specified, the deregistration is only effective for the current session. The deregistration will be rejected if the type
          has already been unregistered. However, it is valid to deregister permanently (without the temporaryflag) a type after
          it has been temporarily deregistered.
    
      - force : f                      (bool)          [create]
          Used with flag repathto repath all files to the new location, including the resolved files. Otherwise, repathwill only
          deal with the missing files. Used with flag copyAndRepathto overwrite any colliding file at the destination. Otherwise,
          copyAndRepathwill use the existing file at the destination instead of overwriting it. The default value is off.
    
      - listDirectories : ld           (unicode)       [query]
          List all sub directories of the specified directory.  Only directories containing at least one file whose type is
          registered (see registerType) will be listed. If no directory is provided, all directories applicable to the scene will
          be returned.
    
      - listFiles : lf                 (unicode)       [query]
          List files in the specified directory. No recursion in subdirectories will be performed.
    
      - listRegisteredTypes : lrt      (bool)          [query]
          Query the list of registered attribute types. The registered types include the auto-loaded types from the preference
          file and the types explicitly registered by the user, both with and without the temporaryflag.
    
      - preview : p                    (bool)          [create]
          Used with repath, replaceStringor copyAndRepathto preview the result of the operation instead of excuting it. When it is
          used with repathor replaceString, the command returns the new file path and a status flag indicating whether the new
          file exists (1) or not (0). The path name and the file status are listed in pairs. When it is used with copyAndRepath,
          the command returns the files that need copying.
    
      - recursive : rc                 (bool)          [create]
          Used with flag repathto search the files in the target directory and its subdirectories recursively. If the flag is on,
          the command will repath the plug to a file that has the same name in the target directory or sub directories. If the
          flag is off, the command will apply the directory change without verifying that the resulting file exists.
    
      - refresh : rf                   (bool)          [create]
          Clear and re-collect the file information in the scene. The command does not automatically track file path modifications
          in the scene. So it is the users responsibility to cause refreshes in order to get up-to-date information.
    
      - registerType : rt              (unicode)       [create]
          Register a new file type that the command will handle and recognize from now on. Unless the temporaryflag is used, the
          registered type is saved in the preferences and reappears on application restart. The new type will be rejected if it
          collides with an existing type or label. One exception to this is when registering a type without the temporaryflag
          after the type has been registered with it. This is considered as modifying the persistent/temporary property of the
          existing type, rather than registering a new type.
    
      - relativeNames : rel            (bool)          [query]
          Used with listDirectoriesor listFilesto return the relative path of each directory or file.  Paths are relative to the
          current project folder. If a file or the directory is not under the current project folder, the returned path will still
          be a full path.
    
      - repath : r                     (unicode)       [create]
          Replace the directory part of a file path with a specified location. The file name will be preserved.
    
      - replaceAll : ra                (bool)          [create]
          Used with flag replaceString, specifies how many times the matched string will be replaced. When the flag is false, only
          the first matched string will be replaced. Otherwise, all matched strings will be replaced. The default value is false.
    
      - replaceField : rfd             (unicode)       [create]
          Used with the replaceStringflag to control the scope of the replacement. Possible values are: pathOnly- only replace
          strings in the directory part. nameOnly- only replace strings in the file name, without the directory. fullPath- replace
          strings anywhere in the full name. The default argument is fullPath.
    
      - replaceString : rs             (unicode, unicode) [create]
          Replace the target string with the new string in the file paths. The flag needs two arguments: the first one is the
          target string and the second one is the new string. See the replaceFieldand replaceAllflags to control how the
          replacement is performed.
    
      - status : s                     (bool)          [query]
          Used with listFiles, this will cause the returned list of files to include one status flag per file: 0 if it cannot be
          resolved and 1 if it can. Used with listDirectories, this will cause the returned list of directories to include one
          status flag per directory: 0 if it cannot be resolved, 1 if it can and 2 if the resolution is partial. The status will
          be interleaved with the file/directory names, with the name appearing first. See the example for listFiles.  See the
          withAttributeflag for another way of getting per-file information.  When multiple per-entry items appear in the list
          (e.g.: plug name), the status is always last.
    
      - temporary : tmp                (bool)          [create]
          Make the effect of the register/deregisterflag only applicable in the current session. Normally, a type
          registration/deregistration is permanent and is made persistent via a preference file. When the temporaryflag is
          specified, the changes will not be saved to the preference file. When the application restarts, any type that has been
          previously temporarily registered will not appear and any type that was temporarily deregistered will re-appear.
    
      - typeLabel : tl                 (unicode)       [create,query]
          Used with registerTypeto set the label name for the new file type. Used with queryto return the type label for the
          specified attribute type. For default types, the type label is the localized string. For other types, the type label is
          supplied by user.
    
      - unresolved : u                 (bool)          [query]
          Used with listFilesto query the unresolved files that are being used in the scene.
    
      - withAttribute : wa             (bool)          [query]
          Used with listFilesto return the name of the plug using a given file. For example, if file.jpgis used by the plug
          node1.fileTextureName, then the returned string will become the pair file.jpg node1.fileTextureName.  See the statusflag
          for another way to get per-file information.                                    Flag can have multiple arguments, passed
          either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.filePathEditor`
    """

    pass


def imfPlugins(*args, **kwargs):
    """
    This command queries all the available imf plugins for its name, keyword or image file extension. Only one of the
    attributes (name, keyword or extension) can be queried at a time. If no flags are specified, this command returns a list
    of all available plugin names.
    
    Flags:
      - extension : ext                (unicode)       [create,query]
          image file extension
    
      - keyword : key                  (unicode)       [create,query]
          imf keyword
    
      - multiFrameSupport : mfs        (unicode)       [create,query]
          multi frame IO is supported
    
      - pluginName : pn                (unicode)       [create,query]
          imf plugin name
    
      - readSupport : rs               (unicode)       [create,query]
          read operation is supported
    
      - writeSupport : ws              (unicode)       [create,query]
          write operation is supported                               Flag can have multiple arguments, passed either as a tuple or
          a list.
    
    
    Derived from mel command `maya.cmds.imfPlugins`
    """

    pass


def displayWarning(*args, **kwargs):
    pass



_pymel_options = {}

fileInfo = FileInfo()

workspace = Workspace()

_logger = None


