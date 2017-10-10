from pymel.util.arguments import *
from pymel.util.utilitytypes import *

from pymel.util.objectParser import Token
from pymel.util.objectParser import TokenParser
from pymel.util.objectParser import autoparsed
from pymel.util.objectParser import process
from pymel.util.objectParser import verbose
from pymel.util.objectParser import NameParseError
from pymel.util.common import capitalize
from pymel.util.objectParser import isParsedClass
from pymel.util.objectParser import ProxyUni
from pymel.util.objectParser import Parser
from pymel.util.objectParser import Parsed
from pymel.util.objectParser import isParserClass
from pymel.util.objectParser import EmptyTokenParser
from pymel.util.common import uncapitalize
from pymel.util.objectParser import ParsingWarning
from pymel.util.objectParser import currentfn
from pymel.util.objectParser import EmptyParser

class Index(Token):
    """
    Token stub class
    """
    
    
    
    pass


class DotParser(TokenParser):
    """
    Token Parser stub class
    """
    
    
    
    pass


class Pipe(Token):
    """
    Token stub class
    """
    
    
    
    pass


class PipeParser(TokenParser):
    """
    Token Parser stub class
    """
    
    
    
    pass


class NumParser(TokenParser):
    """
    Token Parser stub class
    """
    
    
    
    pass


class AlphaParser(TokenParser):
    """
    Token Parser stub class
    """
    
    
    
    pass


class NameParsed(Parsed):
    def isAttributeName(self):
        """
        True if this object is specified including one or more dag parents
        """
    
        pass
    
    
    def isComponentName(self):
        """
        True if this object is specified as an absolute dag path (starting with '|')
        """
    
        pass
    
    
    def isNodeName(self):
        """
        True if this dag path name is absolute (starts with '|')
        """
    
        pass


class NameIndexParser(Parser):
    """
    A Parser for attribute or component name indexes, in the form [<int number>]
    """
    
    
    
    def p_index(self, p):
        """
        NameIndex : Index
        """
    
        pass
    
    
    precedence = ()
    
    
    start = 'NameIndex'
    
    
    t_Index = r'\[(?:[0-9]+|-1)\]'


class RangeIndex(Token):
    """
    Token stub class
    """
    
    
    
    pass


class ColonParser(TokenParser):
    """
    Token Parser stub class
    """
    
    
    
    pass


class Dot(Token):
    """
    Token stub class
    """
    
    
    
    pass


class IndexParser(TokenParser):
    """
    Token Parser stub class
    """
    
    
    
    pass


class Num(Token):
    """
    Token stub class
    """
    
    
    
    pass


class NameBaseParser(Parser):
    """
    Base for name parser with common tokens
    """
    
    
    
    start = None
    
    
    t_Alpha = '([a-z]+)|([A-Z]+[a-z]*)'
    
    
    t_Num = '[0-9]+'


class AttrSepParser(Parser):
    """
    A Parser for the MayaAttributePath separator
    """
    
    
    
    def p_attr_sep(self, p):
        """
        AttrSep : Dot
        """
    
        pass
    
    
    precedence = ()
    
    
    start = 'AttrSep'
    
    
    t_Dot = r'\.'


class Alpha(Token):
    """
    Token stub class
    """
    
    
    
    pass


class Colon(Token):
    """
    Token stub class
    """
    
    
    
    pass


class DagPathSepParser(Parser):
    """
    A Parser for the DagPathSep separator
    """
    
    
    
    def p_dpath_sep(self, p):
        """
        DagPathSep : Pipe
        """
    
        pass
    
    
    precedence = ()
    
    
    start = 'DagPathSep'
    
    
    t_Pipe = r'\|'


class Underscore(Token):
    """
    Token stub class
    """
    
    
    
    pass


class NamespaceSepParser(Parser):
    """
    A Parser for the Namespace separator
    """
    
    
    
    def p_nspace_sep(self, p):
        """
        NamespaceSep : Colon
        """
    
        pass
    
    
    precedence = ()
    
    
    start = 'NamespaceSep'
    
    
    t_Colon = ':'


class RangeIndexParser(TokenParser):
    """
    Token Parser stub class
    """
    
    
    
    pass


class UnderscoreParser(TokenParser):
    """
    Token Parser stub class
    """
    
    
    
    pass


class NameSepParser(Parser):
    """
    A Parser for the MayaName NameGroup separator : one or more underscores
    """
    
    
    
    def p_sep(self, p):
        """
        NameSep : Underscore
        """
    
        pass
    
    
    def p_sep_concat(self, p):
        """
        NameSep : NameSep Underscore
        """
    
        pass
    
    
    precedence = ()
    
    
    start = 'NameSep'
    
    
    t_Underscore = '_+'


class NameRangeIndexParser(Parser):
    """
    A Parser for an index specification for an attribute or a component index,
    in the form [<optional int number>:<optional int number>]
    Rule : NameIndex = r'\[[0-9]*:[0-9]*\]'
    """
    
    
    
    def p_rindex(self, p):
        """
        NameRangeIndex : RangeIndex
        """
    
        pass
    
    
    precedence = ()
    
    
    start = 'NameRangeIndex'
    
    
    t_RangeIndex = r'\[[0-9]*:[0-9]*\]'


class MayaShortName(NameParsed):
    """
    A short node name in Maya, a Maya name, possibly preceded by a Namespace
    
        Rule : MayaShortName = `Namespace` ? `MayaName`
    
        Composed Of: `Namespace`, `MayaName`
    
        Component Of: `MayaNodePath`
    """
    
    
    
    def addPrefix(self, prefix):
        """
        Add a prefix to the node name. This must produce a valid maya name (no separators allowed).
        """
    
        pass
    
    
    def addSuffix(self, suffix):
        """
        Add a suffix to the node name. This must produce a valid maya name (no separators allowed).
        """
    
        pass
    
    
    def getBaseName(self):
        """
        Get the short node name of the object
        """
    
        pass
    
    
    def getBaseNamespace(self):
        """
        Get the namespace for the current node
        """
    
        pass
    
    
    def isAbsoluteNamespace(self):
        """
        True if this object is specified in an absolute namespace
        """
    
        pass
    
    
    def setBaseName(self, name):
        """
        Set the name of the object.  Should not include namespace
        """
    
        pass
    
    
    def setNamespace(self, namespace):
        """
        Set the namespace. The provided namespace may be nested and should including a trailing colon unless it is empty.
        """
    
        pass
    
    
    basename = None
    
    first = None
    
    last = None
    
    namespace = None
    
    parts = None


class NameSep(NameParsed):
    """
    the MayaName NameGroup separator : one or more underscores
    
        Rule : NameSep = r'_+'
    
        Component Of: `MayaName`
    """
    
    
    
    def reduced(self):
        """
        Reduce multiple underscores to one
        """
    
        pass
    
    
    def default(cls):
        pass


class Attribute(NameParsed):
    """
    The name of a Maya attribute on a Maya node, a MayaName with an optional NameIndex
    
        Rule : Attribute = `MayaName` `NameIndex` ?
    
        Composed Of: `MayaName`, `NameIndex`
    
        Component Of: `AttributePath`
    """
    
    
    
    def isCompound(self):
        pass
    
    
    bracketedIndex = None
    
    index = None
    
    name = None
    
    parts = None


class NameAlphaPartParser(NameBaseParser):
    """
    Parser for a name part starting with a letter
    """
    
    
    
    def p_apart(self, p):
        """
        NameAlphaPart : Alpha
        """
    
        pass
    
    
    start = 'NameAlphaPart'


class NamespaceSep(NameParsed):
    """
    The Maya Namespace separator : the colon ':'
    
        Rule : NamespaceSep = r':'
    
        Component Of: `Namespace`
    """
    
    
    
    def default(cls):
        pass


class Component(NameParsed):
    """
    A Maya component name of any of the single, double or triple indexed kind
    
        Rule : Component = SingleComponentName | DoubleComponentName | TripleComponentName
    
        Component Of: `MayaObjectName`
    """
    
    
    
    pass


class DagPathSep(NameParsed):
    """
    The Maya long names separator : the pipe '|'
    
        Rule : DagPathSep = r'\|'
    
        Component Of: `MayaNodePath`
    """
    
    
    
    def default(cls):
        pass


class MayaName(NameParsed):
    """
    The most basic Maya Name : several name groups separated by one or more underscores,
    starting with a NameHead or one or more underscore, followed by zero or more NameGroup
    
        Rule : MayaName = (`NameSep` * `NameAlphaGroup`) | (`NameSep` + `NameNumGroup`)  ( `NameSep` `NameGroup` ) * `NameSep` *
    
        Composed Of: `NameSep`, `NameAlphaGroup`, `NameNumGroup`, `NameGroup`
    
        Component Of: `Namespace`, `MayaShortName`, `Attribute`
    """
    
    
    
    def extractNum(self):
        """
        Return the trailing numbers of the node name. If no trailing numbers are found
        an error will be raised.
        """
    
        pass
    
    
    def nextName(self):
        """
        Increment the trailing number of the object by 1
        """
    
        pass
    
    
    def nextUniqueName(self):
        """
        Increment the trailing number of the object until a unique name is found
        """
    
        pass
    
    
    def prevName(self):
        """
        Decrement the trailing number of the object by 1
        """
    
        pass
    
    
    def reduced(self):
        """
        Reduces all separators in thet Maya Name to one underscore, eliminates head and tail separators if not needed
        """
    
        pass
    
    
    first = None
    
    groups = None
    
    last = None
    
    parts = None
    
    tail = None


class AttrSep(NameParsed):
    """
    The Maya attribute separator : the dot '.'
    
        Rule : AttrSep = r'\.'
    
        Component Of: `Component`, `AttributePath`, `NodeAttribute`
    """
    
    
    
    def default(cls):
        pass


class NameNumPartParser(NameBaseParser):
    """
    Parser for a name part starting with a number
    """
    
    
    
    def p_npart(self, p):
        """
        NameNumPart : Num
        """
    
        pass
    
    
    start = 'NameNumPart'


class NodeAttribute(NameParsed):
    """
    The name of a Maya node and attribute (plug): a MayaNodePath followed by a AttrSep and a AttributePath
    
        Rule : NodeAttribute = `MayaNodePath` `AttrSep` `AttributePath`
    
        Composed Of: `MayaNodePath`, `AttrSep`, `AttributePath`
    
        Component Of: `MayaObjectName`
    
    
        >>> nodeAttr = NodeAttribute( 'persp|perspShape.focalLength' )
        >>> nodeAttr.attributes
        (Attribute('focalLength', 17),)
        >>> nodeAttr.nodePath
        MayaNodePath('persp|perspShape', 0)
        >>> nodeAttr.shortName()
        NodeAttribute('perspShape.focalLength', 0)
        >>>
        >>> nodeAttr2 = NodeAttribute( 'persp.translate.tx' )
        >>> nodeAttr2.attributes
        (Attribute('translate', 6), Attribute('tx', 16))
    """
    
    
    
    def popNode(self):
        """
        Remove a node from the end of the path, preserving any attributes (Ex. pCube1|pCubeShape1.width --> pCube1.width).
        """
    
        pass
    
    
    def shortName(self):
        """
        Just the node and attribute without the full dag path. Returns a copy.
        """
    
        pass
    
    
    attribute = None
    
    attributes = None
    
    nodePath = None
    
    parts = None
    
    separator = None


class NamePart(NameParsed):
    """
    A name part of either the NameAlphaPart or NameNumPart kind
    
        Rule : NamePart = `NameAlphaPart` | `NameNumPart`
    
        Composed Of: `NameAlphaPart`, `NameNumPart`
    
        Component Of: `NameNumGroup`
    """
    
    
    
    def isAlpha(self):
        pass
    
    
    def isNum(self):
        pass


class MayaNodePath(NameParsed):
    """
    A node name in Maya, one or more MayaShortName separated by DagPathSep, with an optional leading DagPathSep
    
        Rule : MayaNodePath = `DagPathSep` ? `MayaShortName` (`DagPathSep` `MayaShortName`) *
    
        Composed Of: `DagPathSep`, `MayaShortName`
    
        Component Of: `Component`, `NodeAttribute`
    
    Example
        >>> import pymel.util.nameparse as nameparse
        >>> obj = nameparse.parse( 'group1|pCube1|pCubeShape1' )
        >>> obj.setNamespace( 'foo:' )
        >>> print obj
        foo:group1|foo:pCube1|foo:pCubeShape1
        >>> print obj.parent
        foo:group1|foo:pCube1
        >>> print obj.node
        foo:pCubeShape1
        >>> print obj.node.basename
        pCubeShape1
        >>> print obj.node.namespace
        foo:
    """
    
    
    
    def addNamespace(self, namespace):
        """
        Append the namespace for all nodes in this path.
        """
    
        pass
    
    
    def addNode(self, node):
        """
        Add a node to the end of the path
        """
    
        pass
    
    
    def addPrefix(self, prefix):
        """
        Add a prefix to all nodes in the path. This must produce a valid maya name (no separators allowed).
        """
    
        pass
    
    
    def addSuffix(self, suffix):
        """
        Add a suffix to all nodes in the path. This must produce a valid maya name (no separators allowed).
        """
    
        pass
    
    
    def isAbsolute(self):
        """
        True if this object is specified as an absolute dag path (starting with '|')
        """
    
        pass
    
    
    def isDagName(self):
        """
        True if this object is specified including one or more dag parents
        """
    
        pass
    
    
    def isLongName(self):
        """
        True if this object is specified as an absolute dag path (starting with '|')
        """
    
        pass
    
    
    def isShortName(self):
        """
        True if this object node is specified as a short name (without a path)
        """
    
        pass
    
    
    def popNamespace(self, index=0):
        """
        Remove an individual namespace (no separator) from all nodes in this path. An index of 0 (default) is the shallowest (leftmost) in the list.
        Returns a tuple containing the namespace popped from each node in the path or None if the node had no namespaces.
        """
    
        pass
    
    
    def popNode(self, index=-1):
        """
        Remove a node from the end of the path
        """
    
        pass
    
    
    def setNamespace(self, namespace):
        """
        Set the namespace for all nodes in this path. The provided namespace may be nested and should including a trailing colon unless it is empty.
        """
    
        pass
    
    
    def shortName(self):
        """
        The last short name of the path
        """
    
        pass
    
    
    first = None
    
    last = None
    
    node = None
    
    nodePaths = None
    
    nodes = None
    
    parent = None
    
    parents = None
    
    parts = None
    
    root = None
    
    separator = None


class Empty(NameParsed):
    """
    # Empty special NameParsed class
    """
    
    
    
    def default(cls):
        pass


class NameRangeIndex(NameParsed):
    """
    An index specification for an attribute or a component index, in the form::
        [<optional int number>:<optional int number>]
    
        Rule : NameIndex = r'\[[0-9]*:[0-9]*\]'
    """
    
    
    
    def default(cls):
        pass
    
    
    def __new__(cls, *args, **kwargs):
        pass
    
    
    bounds = None
    
    end = None
    
    range = None
    
    start = None


class AttributePath(NameParsed):
    """
    The full path of a Maya attribute on a Maya node, as one or more AttrSep ('.') separated Attribute
    
        Rule : AttributePath = ( `Attribute` `AttrSep` ) * `Attribute`
    
        Composed Of: `Attribute`, `AttrSep`
    
        Component Of: `NodeAttribute`
    """
    
    
    
    def isCompound(self):
        pass
    
    
    attributes = None
    
    first = None
    
    last = None
    
    parent = None
    
    parents = None
    
    parts = None
    
    path = None
    
    separator = None


class Namespace(NameParsed):
    """
    A Maya namespace name, one or more MayaName separated by ':'
    
        Rule : Namespace = `NamespaceSep` ? (`MayaName` `NamespaceSep`) +
    
        Composed Of: `NamespaceSep`, `MayaName`
    
        Component Of: `MayaShortName`
    """
    
    
    
    def append(self, namespace):
        """
        Append a namespace. Can include separator and multiple namespaces. The new namespace will be the shallowest (leftmost) namespace.
        """
    
        pass
    
    
    def isAbsolute(self):
        """
        True if this namespace is an absolute namespace path (starts with ':')
        """
    
        pass
    
    
    def pop(self, index=0):
        """
        Remove an individual namespace (no separator). An index of 0 (default) is the shallowest (leftmost) in the list
        """
    
        pass
    
    
    def setSpace(self, index, space):
        """
        Set the namespace at the given index
        """
    
        pass
    
    
    def default(cls):
        pass
    
    
    first = None
    
    last = None
    
    parent = None
    
    parents = None
    
    parts = None
    
    path = None
    
    separator = None
    
    space = None
    
    spaces = None


class MayaObjectName(NameParsed):
    """
    An object name in Maya, can be a dag object name, a node name,
    an plug name, a component name or a ui name
    
        Rule : MayaObjectName = `MayaNodePath` | `NodeAttribute` | `Component`
    
        Composed Of: `MayaNodePath`, `NodeAttribute`, `Component`
    """
    
    
    
    def isAttributeName(self):
        """
        True if this object is specified including one or more dag parents
        """
    
        pass
    
    
    def isComponentName(self):
        """
        True if this object is specified as an absolute dag path (starting with '|')
        """
    
        pass
    
    
    def isNodeName(self):
        """
        True if this dag path name is absolute (starts with '|')
        """
    
        pass
    
    
    attribute = None
    
    attributes = None
    
    component = None
    
    node = None
    
    nodes = None
    
    object = None
    
    parts = None
    
    type = None


class NameIndex(NameParsed):
    """
    An index specification for an attribute or a component index, in the form [<int number>]
    
        Rule : NameIndex = r'\[[0-9]+\]'
    
        Component Of: `Attribute`
    """
    
    
    
    def __new__(cls, *args, **kwargs):
        """
        # to allow initialization from a single int
        """
    
        pass
    
    
    value = None


class NameGroup(NameParsed):
    """
    A name group of either the NameAlphaGroup or NameNumGroup kind
    
        Rule : NameGroup = `NameAlphaGroup` | `NameNumGroup`
    
        Composed Of: `NameAlphaGroup`, `NameNumGroup`
    
        Component Of: `MayaName`
    """
    
    
    
    def isAlpha(self):
        pass
    
    
    def isNum(self):
        pass
    
    
    def nextName(self):
        pass
    
    
    def prevName(self):
        pass
    
    
    first = None
    
    last = None
    
    parts = None
    
    tail = None


class NamePartParser(NameAlphaPartParser, NameNumPartParser):
    """
    Parser for a name part of either the NameAlphaPart or NameNumPart kind
    """
    
    
    
    def p_part(self, p):
        """
        NamePart : NameAlphaPart
        | NameNumPart
        """
    
        pass
    
    
    start = 'NamePart'


class NameNumPart(NamePart):
    """
    A name part made of numbers
    
        Rule : NameNumPart = r'[0-9]+'
    """
    
    
    
    def isAlpha(self):
        pass
    
    
    def isNum(self):
        pass
    
    
    def __new__(cls, *args, **kwargs):
        """
        # to allow initialization from a single int
        """
    
        pass
    
    
    value = None


class NameAlphaPart(NamePart):
    """
    A name part made of alphabetic letters
    
        Rule : NameAlphaPart = r'([a-z]+)|([A-Z]+[a-z]*)'
    
        Component Of: `NameNumGroup`, `NameAlphaGroup`
    """
    
    
    
    def isAlpha(self):
        pass
    
    
    def isNum(self):
        pass


class NameAlphaGroupParser(NameAlphaPartParser, NameNumPartParser):
    """
    A Parser for suitable groups for a name head : one or more name parts, the first part starting with a letter
    NameAlphaGroup = NameAlphaPart NamePart *
    """
    
    
    
    def p_agroup(self, p):
        """
        NameAlphaGroup : NameAlphaPart
        """
    
        pass
    
    
    def p_agroup_concat(self, p):
        """
        NameAlphaGroup : NameAlphaGroup NameAlphaPart
        |  NameAlphaGroup NameNumPart
        """
    
        pass
    
    
    start = 'NameAlphaGroup'


class NameNumGroup(NameGroup):
    """
    A name group starting with an alphabetic part
    
        Rule : NameAlphaGroup  = `NameAlphaPart` `NamePart` *
    
        Composed Of: `NameAlphaPart`, `NamePart`
    
        Component Of: `MayaName`
    """
    
    
    
    def isAlpha(self):
        pass
    
    
    def isNum(self):
        pass


class NameAlphaGroup(NameGroup):
    """
    A name group starting with an alphabetic part
    
        Rule : NameAlphaGroup  = `NameAlphaPart` `NamePart` *
    
        Composed Of: `NameAlphaPart`, `NamePart`
    
        Component Of: `NameNumGroup`
    """
    
    
    
    def isAlpha(self):
        pass
    
    
    def isNum(self):
        pass


class NameNumGroupParser(NameAlphaPartParser, NameNumPartParser):
    """
    A Parser for suitable groups for a name body : one or more name parts, the first part starting with a number
    NameNumGroup = NameNumPart NamePart *
    """
    
    
    
    def p_ngroup(self, p):
        """
        NameNumGroup : NameNumPart
        """
    
        pass
    
    
    def p_ngroup_concat(self, p):
        """
        NameNumGroup : NameNumGroup NameAlphaPart
        | NameNumGroup NameNumPart
        """
    
        pass
    
    
    start = 'NameNumGroup'


class NameGroupParser(NameAlphaGroupParser, NameNumGroupParser):
    """
    A Parser for a name group of either the NameAlphaGroup or NameNumGroup kind
    """
    
    
    
    def p_group(self, p):
        """
        NameGroup : NameAlphaGroup
        | NameNumGroup
        """
    
        pass
    
    
    start = 'NameGroup'


class MayaNameParser(NameSepParser, NameGroupParser):
    """
    A Parser for the most basic Maya Name : several name groups separated by one or more underscores,
    starting with an alphabetic part or one or more underscore, followed by zero or more NameGroup(s)
    separated by underscores
    """
    
    
    
    def p_name(self, p):
        """
        MayaName : NameSep NameGroup
        | NameAlphaGroup
        """
    
        pass
    
    
    def p_name_concat(self, p):
        """
        MayaName : MayaName NameSep NameGroup
        | MayaName NameSep
        """
    
        pass
    
    
    def p_name_error(self, p):
        """
        MayaName : error
        """
    
        pass
    
    
    start = 'MayaName'


class DoubleComponentNameParser(NameRangeIndexParser, NameIndexParser, MayaNameParser):
    pass


class NamespaceParser(NamespaceSepParser, MayaNameParser, EmptyParser):
    """
    A Parser for Namespace, Maya namespaces names
    """
    
    
    
    def p_nspace(self, p):
        """
        Namespace : MayaName NamespaceSep
        | NamespaceSep
        | Empty
        """
    
        pass
    
    
    def p_nspace_concat(self, p):
        """
        Namespace : Namespace MayaName NamespaceSep
        """
    
        pass
    
    
    start = 'Namespace'


class NodeAttributeNameParser(NameIndexParser, MayaNameParser):
    """
    Parser for a Attribute, the name of a Maya attribute on a Maya node, a MayaName with an optional NameIndex
    """
    
    
    
    def p_nodeattr(self, p):
        """
        Attribute : MayaName NameIndex
        | MayaName
        """
    
        pass
    
    
    def p_nodeattr_error(self, p):
        """
        Attribute : error
        """
    
        pass
    
    
    start = 'Attribute'


class TripleComponentNameParser(NameRangeIndexParser, NameIndexParser, MayaNameParser):
    pass


class SingleComponentNameParser(NameRangeIndexParser, NameIndexParser, MayaNameParser):
    """
    A NameParsed for the reserved single indexed components names:
    vtx,
    Rule : NameIndex = r'\[[0-9]*:[0-9]*\]'
    """
    
    
    
    pass


class ComponentNameParser(SingleComponentNameParser, DoubleComponentNameParser, TripleComponentNameParser):
    pass


class MayaShortNameParser(NamespaceParser, MayaNameParser):
    """
    A parser for MayaShortName, a short object name (without preceding path) with a possible preceding namespace
    """
    
    
    
    def p_sname(self, p):
        """
        MayaShortName : Namespace MayaName
        | MayaName
        """
    
        pass
    
    
    start = 'MayaShortName'


class NodeAttributePathParser(AttrSepParser, NodeAttributeNameParser):
    """
    Parser for a full path of a Maya attribute on a Maya node, as one or more AttrSep ('.') separated Attribute
    """
    
    
    
    def p_nodeattrpath(self, p):
        """
        AttributePath : Attribute
        """
    
        pass
    
    
    def p_nodeattrpath_concat(self, p):
        """
        AttributePath : AttributePath AttrSep Attribute
        """
    
        pass
    
    
    start = 'AttributePath'


class MayaNodePathParser(DagPathSepParser, MayaShortNameParser):
    """
    a Parser for Maya node name, an optional leading DagPathSep followed by one or more
    MayaShortName separated by DagPathSep
    """
    
    
    
    def p_node(self, p):
        """
        MayaNodePath : DagPathSep MayaShortName
        | MayaShortName
        """
    
        pass
    
    
    def p_node_concat(self, p):
        """
        MayaNodePath : MayaNodePath DagPathSep MayaShortName
        """
    
        pass
    
    
    start = 'MayaNodePath'


class AttributeNameParser(NodeAttributePathParser, MayaNodePathParser):
    """
    Parser for the name of a Maya attribute, a MayaNodePath followed by a AttrSep and a AttributePath
    """
    
    
    
    def p_attribute(self, p):
        """
        NodeAttribute : MayaNodePath AttrSep AttributePath
        """
    
        pass
    
    
    start = 'NodeAttribute'


class MayaObjectNameParser(AttributeNameParser):
    """
    A Parser for an unspecified object name in Maya, can be a dag object name, a node name,
    an plug name, or a component name.
    """
    
    
    
    def p_mobject(self, p):
        """
        MayaObjectName : MayaNodePath
        | NodeAttribute
        """
    
        pass
    
    
    start = 'MayaObjectName'



def _test(expr):
    """
    Tests the name parsing of the string argument expr and displays results
    """

    pass


def _decomposeNodeAttributeName(name, ident=0):
    pass


def _decomposeName(name, ident=0):
    pass


def _decomposeGroup(name, ident=0):
    pass


def _decomposeNamespace(name, ident=0):
    pass


def _decomposeNodeName(name, ident=0):
    pass


def _decomposeAttributeName(name, ident=0):
    pass


def _decomposeNodeAttributePathName(name, ident=0):
    pass


def _decomposeShortName(name, ident=0):
    pass


def _decomposeObjectName(name, ident=0):
    pass


def parse(name):
    """
    main entry point for parsing a maya node name
    """

    pass


def _itest():
    """
    Inerractive name parsing test, enter a name and see result decomposition
    """

    pass


def getBasicPartList(name):
    """
    convenience function for breaking apart a maya object to the appropriate level for pymel name parsing
    
        >>> getBasicPartList('thing|foo:bar.attr[0].child')
        [MayaNodePath('thing|foo:bar', 0), MayaName('attr', 14), NameIndex('[0]', 18), MayaName('child', 22)]
    """

    pass



