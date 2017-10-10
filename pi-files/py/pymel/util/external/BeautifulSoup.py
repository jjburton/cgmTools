import exceptions

"""
Beautiful Soup
Elixir and Tonic
"The Screen-Scraper's Friend"
http://www.crummy.com/software/BeautifulSoup/

Beautiful Soup parses a (possibly invalid) XML or HTML document into a
tree representation. It provides methods and Pythonic idioms that make
it easy to navigate, search, and modify the tree.

A well-formed XML/HTML document yields a well-formed data
structure. An ill-formed XML/HTML document yields a correspondingly
ill-formed data structure. If your document is only locally
well-formed, you can use this library to find and process the
well-formed part of it.

Beautiful Soup works with Python 2.2 and up. It has no external
dependencies, but you'll have more success at converting data to UTF-8
if you also install these three packages:

* chardet, for auto-detecting character encodings
  http://chardet.feedparser.org/
* cjkcodecs and iconv_codec, which add more encodings to the ones supported
  by stock Python.
  http://cjkpython.i18n.org/

Beautiful Soup defines classes for two main parsing strategies:

 * BeautifulStoneSoup, for parsing XML, SGML, or your domain-specific
   language that kind of looks like XML.

 * BeautifulSoup, for parsing run-of-the-mill HTML code, be it valid
   or invalid. This class has web browser-like heuristics for
   obtaining a sensible parse tree in the face of common HTML errors.

Beautiful Soup also defines a class (UnicodeDammit) for autodetecting
the encoding of an HTML or XML document, and converting it to
Unicode. Much of this code is taken from Mark Pilgrim's Universal Feed Parser.

For more than you ever wanted to know about Beautiful Soup, see the
documentation:
http://www.crummy.com/software/BeautifulSoup/documentation.html

Here, have some legalese:

Copyright (c) 2004-2008, Leonard Richardson

All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:

  * Redistributions of source code must retain the above copyright
    notice, this list of conditions and the following disclaimer.

  * Redistributions in binary form must reproduce the above
    copyright notice, this list of conditions and the following
    disclaimer in the documentation and/or other materials provided
    with the distribution.

  * Neither the name of the the Beautiful Soup Consortium and All
    Night Kosher Bakery nor the names of its contributors may be
    used to endorse or promote products derived from this software
    without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE, DAMMIT.
"""

from sgmllib import SGMLParser
from sgmllib import SGMLParseError

class PageElement:
    """
    Contains the navigational information for some part of the page
    (either a tag or a piece of text)
    """
    
    
    
    def append(self, tag):
        """
        Appends the given tag to the contents of this tag.
        """
    
        pass
    
    
    def extract(self):
        """
        Destructively rips this element out of the tree.
        """
    
        pass
    
    
    def fetchNextSiblings(self, name=None, attrs={}, text=None, limit=None, **kwargs):
        """
        Returns the siblings of this Tag that match the given
        criteria and appear after this Tag in the document.
        """
    
        pass
    
    
    def fetchParents(self, name=None, attrs={}, limit=None, **kwargs):
        """
        Returns the parents of this Tag that match the given
        criteria.
        """
    
        pass
    
    
    def fetchPrevious(self, name=None, attrs={}, text=None, limit=None, **kwargs):
        """
        Returns all items that match the given criteria and appear
        before this Tag in the document.
        """
    
        pass
    
    
    def fetchPreviousSiblings(self, name=None, attrs={}, text=None, limit=None, **kwargs):
        """
        Returns the siblings of this Tag that match the given
        criteria and appear before this Tag in the document.
        """
    
        pass
    
    
    def findAllNext(self, name=None, attrs={}, text=None, limit=None, **kwargs):
        """
        Returns all items that match the given criteria and appear
        after this Tag in the document.
        """
    
        pass
    
    
    def findAllPrevious(self, name=None, attrs={}, text=None, limit=None, **kwargs):
        """
        Returns all items that match the given criteria and appear
        before this Tag in the document.
        """
    
        pass
    
    
    def findNext(self, name=None, attrs={}, text=None, **kwargs):
        """
        Returns the first item that matches the given criteria and
        appears after this Tag in the document.
        """
    
        pass
    
    
    def findNextSibling(self, name=None, attrs={}, text=None, **kwargs):
        """
        Returns the closest sibling to this Tag that matches the
        given criteria and appears after this Tag in the document.
        """
    
        pass
    
    
    def findNextSiblings(self, name=None, attrs={}, text=None, limit=None, **kwargs):
        """
        Returns the siblings of this Tag that match the given
        criteria and appear after this Tag in the document.
        """
    
        pass
    
    
    def findParent(self, name=None, attrs={}, **kwargs):
        """
        Returns the closest parent of this Tag that matches the given
        criteria.
        """
    
        pass
    
    
    def findParents(self, name=None, attrs={}, limit=None, **kwargs):
        """
        Returns the parents of this Tag that match the given
        criteria.
        """
    
        pass
    
    
    def findPrevious(self, name=None, attrs={}, text=None, **kwargs):
        """
        Returns the first item that matches the given criteria and
        appears before this Tag in the document.
        """
    
        pass
    
    
    def findPreviousSibling(self, name=None, attrs={}, text=None, **kwargs):
        """
        Returns the closest sibling to this Tag that matches the
        given criteria and appears before this Tag in the document.
        """
    
        pass
    
    
    def findPreviousSiblings(self, name=None, attrs={}, text=None, limit=None, **kwargs):
        """
        Returns the siblings of this Tag that match the given
        criteria and appear before this Tag in the document.
        """
    
        pass
    
    
    def insert(self, position, newChild):
        pass
    
    
    def nextGenerator(self):
        """
        #These Generators can be used to navigate starting from both
        #NavigableStrings and Tags.
        """
    
        pass
    
    
    def nextSiblingGenerator(self):
        pass
    
    
    def parentGenerator(self):
        pass
    
    
    def previousGenerator(self):
        pass
    
    
    def previousSiblingGenerator(self):
        pass
    
    
    def replaceWith(self, replaceWith):
        pass
    
    
    def setup(self, parent=None, previous=None):
        """
        Sets up the initial relations between this element and
        other elements.
        """
    
        pass
    
    
    def substituteEncoding(self, str, encoding=None):
        """
        # Utility methods
        """
    
        pass
    
    
    def toEncoding(self, s, encoding=None):
        """
        Encodes an object to a string in some encoding, or to Unicode.
        .
        """
    
        pass


class StopParsing(exceptions.Exception):
    __weakref__ = None


class SoupStrainer:
    """
    Encapsulates a number of ways of matching a markup element (tag or
    text).
    """
    
    
    
    def __init__(self, name=None, attrs={}, text=None, **kwargs):
        pass
    
    
    def __str__(self):
        pass
    
    
    def search(self, markup):
        pass
    
    
    def searchTag(self, markupName=None, markupAttrs={}):
        pass


class ResultSet(list):
    """
    A ResultSet is just a list that keeps track of the SoupStrainer
    that created it.
    """
    
    
    
    def __init__(self, source):
        pass
    
    
    __dict__ = None
    
    __weakref__ = None


class UnicodeDammit:
    """
    A class for detecting the encoding of a *ML document and
    converting it to a Unicode string. If the source encoding is
    windows-1252, can replace MS smart quotes with their HTML or XML
    equivalents.
    """
    
    
    
    def __init__(self, markup, overrideEncodings=[], smartQuotesTo='xml', isHTML=False):
        pass
    
    
    def find_codec(self, charset):
        pass
    
    
    CHARSET_ALIASES = {}
    
    
    EBCDIC_TO_ASCII_MAP = None
    
    
    MS_CHARS = {}


class Tag(PageElement):
    """
    Represents a found HTML tag with its attributes and contents.
    """
    
    
    
    def __call__(self, *args, **kwargs):
        """
        Calling a tag like a function is the same as calling its
        findAll() method. Eg. tag('a') returns a list of all the A tags
        found within this tag.
        """
    
        pass
    
    
    def __contains__(self, x):
        pass
    
    
    def __delitem__(self, key):
        """
        Deleting tag[key] deletes all 'key' attributes for the tag.
        """
    
        pass
    
    
    def __eq__(self, other):
        """
        Returns true iff this tag has the same name, the same attributes,
        and the same contents (recursively) as the given tag.
        
        NOTE: right now this will return false if two tags have the
        same attributes in a different order. Should this be fixed?
        """
    
        pass
    
    
    def __getattr__(self, tag):
        pass
    
    
    def __getitem__(self, key):
        """
        tag[key] returns the value of the 'key' attribute for the tag,
        and throws an exception if it's not there.
        """
    
        pass
    
    
    def __init__(self, parser, name, attrs=None, parent=None, previous=None):
        """
        Basic constructor.
        """
    
        pass
    
    
    def __iter__(self):
        """
        Iterating over a tag iterates over its contents.
        """
    
        pass
    
    
    def __len__(self):
        """
        The length of a tag is the length of its list of contents.
        """
    
        pass
    
    
    def __ne__(self, other):
        """
        Returns true iff this tag is not identical to the other tag,
        as defined in __eq__.
        """
    
        pass
    
    
    def __nonzero__(self):
        """
        A tag is non-None even if it has no contents.
        """
    
        pass
    
    
    def __repr__(self, encoding='utf-8'):
        """
        Renders this tag as a string.
        """
    
        pass
    
    
    def __setitem__(self, key, value):
        """
        Setting tag[key] sets the value of the 'key' attribute for the
        tag.
        """
    
        pass
    
    
    def __str__(self, encoding='utf-8', prettyPrint=False, indentLevel=0):
        """
        Returns a string or Unicode representation of this tag and
        its contents. To get Unicode, pass None for encoding.
        
        NOTE: since Python's HTML parser consumes whitespace, this
        method is not certain to reproduce the whitespace present in
        the original string.
        """
    
        pass
    
    
    def __unicode__(self):
        pass
    
    
    def childGenerator(self):
        """
        #Generator methods
        """
    
        pass
    
    
    def decompose(self):
        """
        Recursively destroys the contents of this tree.
        """
    
        pass
    
    
    def fetch(self, name=None, attrs={}, recursive=True, text=None, limit=None, **kwargs):
        """
        Extracts a list of Tag objects that match the given
        criteria.  You can specify the name of the Tag and any
        attributes you want the Tag to have.
        
        The value of a key-value pair in the 'attrs' map can be a
        string, a list of strings, a regular expression object, or a
        callable that takes a string and returns whether or not the
        string matches for some custom definition of 'matches'. The
        same is true of the tag name.
        """
    
        pass
    
    
    def fetchText(self, text=None, recursive=True, limit=None):
        pass
    
    
    def find(self, name=None, attrs={}, recursive=True, text=None, **kwargs):
        """
        Return only the first child of this Tag matching the given
        criteria.
        """
    
        pass
    
    
    def findAll(self, name=None, attrs={}, recursive=True, text=None, limit=None, **kwargs):
        """
        Extracts a list of Tag objects that match the given
        criteria.  You can specify the name of the Tag and any
        attributes you want the Tag to have.
        
        The value of a key-value pair in the 'attrs' map can be a
        string, a list of strings, a regular expression object, or a
        callable that takes a string and returns whether or not the
        string matches for some custom definition of 'matches'. The
        same is true of the tag name.
        """
    
        pass
    
    
    def findChild(self, name=None, attrs={}, recursive=True, text=None, **kwargs):
        """
        Return only the first child of this Tag matching the given
        criteria.
        """
    
        pass
    
    
    def findChildren(self, name=None, attrs={}, recursive=True, text=None, limit=None, **kwargs):
        """
        Extracts a list of Tag objects that match the given
        criteria.  You can specify the name of the Tag and any
        attributes you want the Tag to have.
        
        The value of a key-value pair in the 'attrs' map can be a
        string, a list of strings, a regular expression object, or a
        callable that takes a string and returns whether or not the
        string matches for some custom definition of 'matches'. The
        same is true of the tag name.
        """
    
        pass
    
    
    def first(self, name=None, attrs={}, recursive=True, text=None, **kwargs):
        """
        Return only the first child of this Tag matching the given
        criteria.
        """
    
        pass
    
    
    def firstText(self, text=None, recursive=True):
        pass
    
    
    def get(self, key, default=None):
        """
        Returns the value of the 'key' attribute for the tag, or
        the value given for 'default' if it doesn't have that
        attribute.
        """
    
        pass
    
    
    def has_key(self, key):
        pass
    
    
    def prettify(self, encoding='utf-8'):
        pass
    
    
    def recursiveChildGenerator(self):
        pass
    
    
    def renderContents(self, encoding='utf-8', prettyPrint=False, indentLevel=0):
        """
        Renders the contents of this tag as a string in the given
        encoding. If encoding is None, returns a Unicode string..
        """
    
        pass
    
    
    BARE_AMPERSAND_OR_BRACKET = None
    
    
    XML_ENTITIES_TO_SPECIAL_CHARS = {}
    
    
    XML_SPECIAL_CHARS_TO_ENTITIES = {}


class NavigableString(unicode, PageElement):
    def __getattr__(self, attr):
        """
        text.string gives you text. This is for backwards
        compatibility for Navigable*String, but for CData* it lets you
        get the string without the CData wrapper.
        """
    
        pass
    
    
    def __getnewargs__(self):
        pass
    
    
    def __str__(self, encoding='utf-8'):
        pass
    
    
    def __unicode__(self):
        pass
    
    
    def __new__(cls, value):
        """
        Create a new NavigableString.
        
        When unpickling a NavigableString, this method is called with
        the string in DEFAULT_OUTPUT_ENCODING. That encoding needs to be
        passed in to the superclass's __new__ or the superclass won't know
        how to handle non-ASCII characters.
        """
    
        pass
    
    
    __dict__ = None
    
    __weakref__ = None


class Declaration(NavigableString):
    def __str__(self, encoding='utf-8'):
        pass


class Comment(NavigableString):
    def __str__(self, encoding='utf-8'):
        pass


class BeautifulStoneSoup(Tag, SGMLParser):
    """
    This class contains the basic parser and search code. It defines
    a parser that knows nothing about tag behavior except for the
    following:
    
      You can't close a tag without closing all the tags it encloses.
      That is, "<foo><bar></foo>" actually means
      "<foo><bar></bar></foo>".
    
    [Another possible explanation is "<foo><bar /></foo>", but since
    this class defines no SELF_CLOSING_TAGS, it will never use that
    explanation.]
    
    This class is useful for parsing XML or made-up markup languages,
    or when BeautifulSoup makes an assumption counter to what you were
    expecting.
    """
    
    
    
    def __getattr__(self, methodName):
        """
        This method routes method call requests to either the SGMLParser
        superclass or the Tag superclass, depending on the method name.
        """
    
        pass
    
    
    def __init__(self, markup='', parseOnlyThese=None, fromEncoding=None, markupMassage=True, smartQuotesTo='xml', convertEntities=None, selfClosingTags=None, isHTML=False):
        """
        The Soup object is initialized as the 'root tag', and the
        provided markup (which can be a string or a file-like object)
        is fed into the underlying parser.
        
        sgmllib will process most bad HTML, and the BeautifulSoup
        class has some tricks for dealing with some HTML that kills
        sgmllib, but Beautiful Soup can nonetheless choke or lose data
        if your data uses self-closing tags or declarations
        incorrectly.
        
        By default, Beautiful Soup uses regexes to sanitize input,
        avoiding the vast majority of these problems. If the problems
        don't apply to you, pass in False for markupMassage, and
        you'll get better performance.
        
        The default parser massage techniques fix the two most common
        instances of invalid HTML that choke sgmllib:
        
         <br/> (No space between name of closing tag and tag close)
         <! --Comment--> (Extraneous whitespace in declaration)
        
        You can pass in a custom list of (RE object, replace method)
        tuples to get Beautiful Soup to scrub your input the way you
        want.
        """
    
        pass
    
    
    def convert_charref(self, name):
        """
        This method fixes a bug in Python's SGMLParser.
        """
    
        pass
    
    
    def endData(self, containerClass="<class 'pymel.util.external.BeautifulSoup.NavigableString'>"):
        pass
    
    
    def handle_charref(self, ref):
        """
        Handle character references as data.
        """
    
        pass
    
    
    def handle_comment(self, text):
        """
        Handle comments as Comment objects.
        """
    
        pass
    
    
    def handle_data(self, data):
        pass
    
    
    def handle_decl(self, data):
        """
        Handle DOCTYPEs and the like as Declaration objects.
        """
    
        pass
    
    
    def handle_entityref(self, ref):
        """
        Handle entity references as data, possibly converting known
        HTML and/or XML entity references to the corresponding Unicode
        characters.
        """
    
        pass
    
    
    def handle_pi(self, text):
        """
        Handle a processing instruction as a ProcessingInstruction
        object, possibly one with a %SOUP-ENCODING% slot into which an
        encoding will be plugged later.
        """
    
        pass
    
    
    def isSelfClosingTag(self, name):
        """
        Returns true iff the given string is the name of a
        self-closing tag according to this parser.
        """
    
        pass
    
    
    def parse_declaration(self, i):
        """
        Treat a bogus SGML declaration as raw data. Treat a CDATA
        declaration as a CData object.
        """
    
        pass
    
    
    def popTag(self):
        pass
    
    
    def pushTag(self, tag):
        pass
    
    
    def reset(self):
        pass
    
    
    def unknown_endtag(self, name):
        pass
    
    
    def unknown_starttag(self, name, attrs, selfClosing=0):
        pass
    
    
    ALL_ENTITIES = 'xhtml'
    
    
    HTML_ENTITIES = 'html'
    
    
    MARKUP_MASSAGE = []
    
    
    NESTABLE_TAGS = {}
    
    
    PRESERVE_WHITESPACE_TAGS = []
    
    
    QUOTE_TAGS = {}
    
    
    RESET_NESTING_TAGS = {}
    
    
    ROOT_TAG_NAME = []
    
    
    SELF_CLOSING_TAGS = {}
    
    
    STRIP_ASCII_SPACES = {}
    
    
    XHTML_ENTITIES = 'xhtml'
    
    
    XML_ENTITIES = 'xml'


class ProcessingInstruction(NavigableString):
    def __str__(self, encoding='utf-8'):
        pass


class CData(NavigableString):
    def __str__(self, encoding='utf-8'):
        pass


class BeautifulSoup(BeautifulStoneSoup):
    """
    This parser knows the following facts about HTML:
    
    * Some tags have no closing tag and should be interpreted as being
      closed as soon as they are encountered.
    
    * The text inside some tags (ie. 'script') may contain tags which
      are not really part of the document and which should be parsed
      as text, not tags. If you want to parse the text as tags, you can
      always fetch it and parse it explicitly.
    
    * Tag nesting rules:
    
      Most tags can't be nested at all. For instance, the occurance of
      a <p> tag should implicitly close the previous <p> tag.
    
       <p>Para1<p>Para2
        should be transformed into:
       <p>Para1</p><p>Para2
    
      Some tags can be nested arbitrarily. For instance, the occurance
      of a <blockquote> tag should _not_ implicitly close the previous
      <blockquote> tag.
    
       Alice said: <blockquote>Bob said: <blockquote>Blah
        should NOT be transformed into:
       Alice said: <blockquote>Bob said: </blockquote><blockquote>Blah
    
      Some tags can be nested, but the nesting is reset by the
      interposition of other tags. For instance, a <tr> tag should
      implicitly close the previous <tr> tag within the same <table>,
      but not close a <tr> tag in another table.
    
       <table><tr>Blah<tr>Blah
        should be transformed into:
       <table><tr>Blah</tr><tr>Blah
        but,
       <tr>Blah<table><tr>Blah
        should NOT be transformed into
       <tr>Blah<table></tr><tr>Blah
    
    Differing assumptions about tag nesting rules are a major source
    of problems with the BeautifulSoup class. If BeautifulSoup is not
    treating as nestable a tag your page author treats as nestable,
    try ICantBelieveItsBeautifulSoup, MinimalSoup, or
    BeautifulStoneSoup before writing your own subclass.
    """
    
    
    
    def __init__(self, *args, **kwargs):
        pass
    
    
    def start_meta(self, attrs):
        """
        Beautiful Soup can detect a charset included in a META tag,
        try to convert the document to that charset, and re-parse the
        document from the beginning.
        """
    
        pass
    
    
    CHARSET_RE = None
    
    
    NESTABLE_BLOCK_TAGS = []
    
    
    NESTABLE_INLINE_TAGS = []
    
    
    NESTABLE_LIST_TAGS = {}
    
    
    NESTABLE_TABLE_TAGS = {}
    
    
    NESTABLE_TAGS = {}
    
    
    NON_NESTABLE_BLOCK_TAGS = []
    
    
    PRESERVE_WHITESPACE_TAGS = set()
    
    
    QUOTE_TAGS = {}
    
    
    RESET_NESTING_TAGS = {}
    
    
    SELF_CLOSING_TAGS = {}


class BeautifulSOAP(BeautifulStoneSoup):
    """
    This class will push a tag with only a single string child into
    the tag's parent as an attribute. The attribute's name is the tag
    name, and the value is the string child. An example should give
    the flavor of the change:
    
    <foo><bar>baz</bar></foo>
     =>
    <foo bar="baz"><bar>baz</bar></foo>
    
    You can then access fooTag['bar'] instead of fooTag.barTag.string.
    
    This is, of course, useful for scraping structures that tend to
    use subelements instead of attributes, such as SOAP messages. Note
    that it modifies its input, so don't print the modified version
    out.
    
    I'm not sure how many people really want to use this class; let me
    know if you do. Mainly I like the name.
    """
    
    
    
    def popTag(self):
        pass


class RobustXMLParser(BeautifulStoneSoup):
    """
    #Enterprise class names! It has come to our attention that some people
    #think the names of the Beautiful Soup parser classes are too silly
    #and "unprofessional" for use in enterprise screen-scraping. We feel
    #your pain! For such-minded folk, the Beautiful Soup Consortium And
    #All-Night Kosher Bakery recommends renaming this file to
    #"RobustParser.py" (or, in cases of extreme enterprisiness,
    #"RobustParserBeanInterface.class") and using the following
    #enterprise-friendly class aliases:
    """
    
    
    
    pass


class SimplifyingSOAPParser(BeautifulSOAP):
    pass


class ICantBelieveItsBeautifulSoup(BeautifulSoup):
    """
    The BeautifulSoup class is oriented towards skipping over
    common HTML errors like unclosed tags. However, sometimes it makes
    errors of its own. For instance, consider this fragment:
    
     <b>Foo<b>Bar</b></b>
    
    This is perfectly valid (if bizarre) HTML. However, the
    BeautifulSoup class will implicitly close the first b tag when it
    encounters the second 'b'. It will think the author wrote
    "<b>Foo<b>Bar", and didn't close the first 'b' tag, because
    there's no real-world reason to bold something that's already
    bold. When it encounters '</b></b>' it will close two more 'b'
    tags, for a grand total of three tags closed instead of two. This
    can throw off the rest of your document structure. The same is
    true of a number of other tags, listed below.
    
    It's much more common for someone to forget to close a 'b' tag
    than to actually use nested 'b' tags, and the BeautifulSoup class
    handles the common case. This class handles the not-co-common
    case: where you can't believe someone wrote what they did, but
    it's valid HTML and BeautifulSoup screwed up by assuming it
    wouldn't be.
    """
    
    
    
    I_CANT_BELIEVE_THEYRE_NESTABLE_BLOCK_TAGS = []
    
    
    I_CANT_BELIEVE_THEYRE_NESTABLE_INLINE_TAGS = []
    
    
    NESTABLE_TAGS = {}


class MinimalSoup(BeautifulSoup):
    """
    The MinimalSoup class is for parsing HTML that contains
    pathologically bad markup. It makes no assumptions about tag
    nesting, but it does know which tags are self-closing, that
    <script> tags contain Javascript and should not be parsed, that
    META tags may contain encoding information, and so on.
    
    This also makes it better for subclassing than BeautifulStoneSoup
    or BeautifulSoup.
    """
    
    
    
    NESTABLE_TAGS = {}
    
    
    RESET_NESTING_TAGS = {}


class RobustHTMLParser(BeautifulSoup):
    pass


class RobustWackAssHTMLParser(ICantBelieveItsBeautifulSoup):
    pass


class RobustInsanelyWackAssHTMLParser(MinimalSoup):
    pass



def buildTagMap(default, *args):
    """
    Turns a list of maps, lists, or scalars into a single map.
    Used to build the SELF_CLOSING_TAGS, NESTABLE_TAGS, and
    NESTING_RESET_TAGS maps out of lists and partial maps.
    """

    pass


def isList(l):
    """
    Convenience method that works with all 2.x versions of Python
    to determine whether or not something is listlike.
    """

    pass


def isString(s):
    """
    Convenience method that works with all 2.x versions of Python
    to determine whether or not something is stringlike.
    """

    pass



generators = None

__author__ = 'Leonard Richardson (leonardr@segfault.org)'

DEFAULT_OUTPUT_ENCODING = 'utf-8'

chardet = None

__version__ = '3.0.7a'

name2codepoint = {}


