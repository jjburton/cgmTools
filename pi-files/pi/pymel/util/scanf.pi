import exceptions

"""
Danny Yoo (dyoo@hkn.eecs.berkeley.edu)

The initial motivation for this module was based on a posting on
Python-tutor:

    http://mail.python.org/pipermail/tutor/2004-July/030480.html

I haven't been able to find a nice module to do scanf-style input.
Even the Library Reference recommends regular expressions as a
substitute:

    http://docs.python.org/lib/node109.html

But there appears to have been activity about this on python-list:

    http://aspn.activestate.com/ASPN/Mail/Message/python-list/785450


Still, let's see if we can get a close equivalent scanf() in place.
At the least, it'll be fun for me, and it might be useful for people
who are still recovering from C.  *grin*


Functions provided:

    scanf(formatString) -- formatted scanning across stdin

    sscanf(sourceString, formatString) -- formated scanning across strings

    fscanf(sourceFile, formatString) -- formated scanning across files


The behavior of this scanf() will be slightly different from that
defined in C, because, in truth, I'm a little lazy, and am not quite
sure if people will need all of scanf's features in typical Python
programming.


But let's first show what conversions this scanf() will support.
Format strings are of the following form:

    % [*] [width] [format]

where [*] and [width] are optional, and [format] is mandatory.  The
optional flags modify the format.

    *         suppresses variable capture.
    width     maximum character width.


We support the following scanf conversion formats (copied from K&R):

    d    decimal integer.

    i    integer.  The integer may be in octal (leading zero) or
         hexadecimal (leading 0x or 0X).  ## fixme

    o    octal integer (with or without leading zero).  ## fixme

    x    hexadecimal integer (with or without leading 0x or 0X)   ## fixme

    c    characters.  The next input characters (default 1) are
         placed at the indicated spot.  The normal skip over white space
         is suppressed; to read the next non-white space character, use
         %1s.

    s    character string (not quoted).

    f    floating-point number with optional sign and optional decimal point.

    %    literal %; no assignment is made.


Literal characters can appear in the scanf format string: they must
match the same characters in the input.

There is no guarantee of what happens if calls to scanf are mixed with
other input functions.  See the BUGS section below for details on this.


If the input doesn't conform to the format string, a FormatError is
raised.


Example format strings:

    "%d %d"         Two decimal integers.

    "%d.%d.%d.%d"   Four decimal integers, separated by literal periods.
                    The periods won't be captured.

    "hello %s"      Literally matches "hello" followed by any number of
                    spaces, followed by a captured word.


There's also an interface for calling the internal function bscanf()
that works on CharacterBuffer types, if in the future there is
something that supports getc() and ungetc() natively.  There's also an
undocumented compile() function that takes format strings and returns
a function that can scan through CharacterBuffers.  Ooops, I guess I
just documented it.  *grin*


######################################################################


BUGS and GOTCHAS:

One major problem that I'm running into is a lack of ungetc(); it
would be nice if there were such a function in Python, but I can't
find it.  I have to simulate it by using a CharacterBuffer object, but
it's not an ideal solution.

So at most, you may lose a single character to the internal buffers
maintained by this module if you use scanf().  The other two *scanf()
functions, thankfully, aren't effected by this problem, since I can
simulate ungetc() more accurately by using seek() in the other two
cases.

If you really need to get that buffered character back, you can grab
it through _STDIN.lastChar, though manually fiddling with this is not
recommended.

So use scanf() with the following caveat: unlike C's stdin(), this
version scanf() can't be interchanged with calls to other input
functions without some kind of weird side effect.  We keep a
one-character buffer into stdin, so at most you might lose one
character to the internal buffers.

fscanf() is only allowed to work on things that support both read(1)
and seek(1, -1), since then I can reliably do a ungetch-like thing.

scanf("%s") can be dangerous in a hostile environment, since it's very
possible for something to pass in a huge string without spaces.  So use
an explicit width instead if you can help it.
"""

class CompiledPattern:
    def __call__(self, buffer):
        pass
    
    
    def __init__(self, handlers, formatString):
        pass
    
    
    def __repr__(self):
        pass


class CharacterBuffer(object):
    """
    A CharacterBuffer allows us to get a character, and to "unget" a
    character.  Abstract class
    """
    
    
    
    def getch(self):
        """
        Returns the next character.  If there are no more characters
        left in the stream, returns the empty string.
        """
    
        pass
    
    
    def scanCharacterSet(self, characterSet, maxChars=0):
        """
        Support function that scans across a buffer till we hit
        something outside the allowable characterSet.
        """
    
        pass
    
    
    def scanPredicate(self, predicate, maxChars=0):
        """
        Support function that scans across a buffer till we hit
        something outside what's allowable by the predicate.
        """
    
        pass
    
    
    def ungetch(self, ch):
        """
        Tries to put back a character.  Can be called at most once
        between calls to getch().
        """
    
        pass
    
    
    __dict__ = None
    
    __weakref__ = None


class IncompleteCaptureError(exceptions.ValueError):
    """
    The *scanf() functions raise IncompleteCaptureError if a problem
    occurs doing scanning.
    """
    
    
    
    __weakref__ = None


class FormatError(exceptions.ValueError):
    """
    A FormatError is raised if we run into errors while scanning
    for input.
    """
    
    
    
    __weakref__ = None


class CappedBuffer(CharacterBuffer):
    """
    Implementation of a buffer that caps the number of bytes we can
    getch().  The cap may or may not include whitespace characters.
    """
    
    
    
    def __init__(self, buffer, width, ignoreWhitespace=False):
        pass
    
    
    def getch(self):
        pass
    
    
    def isIgnoredChar(self, ch):
        pass
    
    
    def ungetch(self, ch):
        pass


class CharacterBufferFromFile(CharacterBuffer):
    """
    Implementation of CharacterBuffers for files.  We use the native
    read(1) and seek() calls, so we don't have to do so much magic.
    """
    
    
    
    def __init__(self, myfile):
        pass
    
    
    def getch(self):
        pass
    
    
    def ungetch(self, ch):
        pass


class CharacterBufferFromIterable(CharacterBuffer):
    """
    Implementation of CharacterBuffers for iterable things.
    We keep a 'lastChar' attribute to simulate ungetc().
    """
    
    
    
    def __init__(self, iterable):
        pass
    
    
    def getch(self):
        pass
    
    
    def ungetch(self, ch):
        pass



def fscanf(inputFile, formatString):
    """
    fscanf(inputFile, formatString) -> tuple
    
    Scans inputFile for formats specified in the formatString.  See
    module's docs for list of supported format characters.
    """

    pass


def handleInt(buffer, base=0):
    pass


def handleHex(buffer):
    pass


def handleOct(buffer):
    pass


def _compileFormat(formatBuffer):
    pass


def handleChars(buffer, allowLeadingWhitespace=False, isBadCharacter='<function <lambda>>', optional=False):
    """
    Read as many characters are there are in the buffer.
    """

    pass


def makeCharBuffer(thing):
    """
    Try to coerse 'thing' into a CharacterBuffer.  'thing' can be
    an instance of:
    
        1.  CharacterBuffer
        2.  A file-like object,
        3.  An iterable.
    
    makeCharBuffer() will make guesses in that order.
    """

    pass


def isFileLike(thing):
    """
    Returns true if thing looks like a file.
    """

    pass


def handleFloat(buffer, allowLeadingWhitespace=True):
    pass


def makeFormattedHandler(suppression, width, formatCh):
    """
    Given suppression, width, and a formatType, returns a function
    that eats a buffer and returns that thing.
    """

    pass


def isWhitespaceChar(ch, _set=set(['\t', '\n', '\x0b', '\x0c', '\r', ' '])):
    """
    Returns true if the charcter looks like whitespace.
    We follow the definition of C's isspace() function.
    """

    pass


def bscanf(buffer, formatString):
    """
    fscanf(buffer, formatString) -> tuple
    
    Scans a CharacterBuffer 'buffer' for formats specified in the
    formatString.  See scanf module's docs for list of supported format
    characters.
    """

    pass


def readiter(inputFile, *args):
    """
    Returns an iterator that calls read(*args) on the inputFile.
    """

    pass


def handleDecimalInt(buffer, optional=False, allowLeadingWhitespace=True):
    """
    Tries to scan for an integer.  If 'optional' is set to False,
    returns None if an integer can't be successfully scanned.
    """

    pass


def makeIgnoredHandler(handler):
    pass


def handleWhitespace(buffer):
    """
    Scans for whitespace.  Returns all the whitespace it collects.
    """

    pass


def compile(formatString):
    """
    Given a format string, emits a new CompiledPattern that eats
    CharacterBuffers and returns captured values as a tuple.
    
    If there's a failure during scanning, raises IncompleteCaptureError,
    with args being a two-tuple of the FormatError, and the results that
    were captured before the error occurred.
    """

    pass


def handleChar(buffer):
    pass


def makeWidthLimitedHandler(handler, width, ignoreWhitespace=False):
    """
    Constructs a Handler that caps the number of bytes that can be read
    from the byte buffer.
    """

    pass


def sscanf(inputString, formatString):
    """
    sscanf(inputString, formatString) -> tuple
    
    Scans inputString for formats specified in the formatString.  See
    module's docs for list of supported format characters.
    """

    pass


def handleString(buffer, allowLeadingWhitespace=True):
    """
    Reading a string format is just an application of reading
    characters (skipping leading spaces, and reading up to space).
    """

    pass


def isIterable(thing):
    """
    Returns true if 'thing' looks iterable.
    """

    pass


def makeHandleLiteral(literal):
    pass



__version__ = '1.0'

WHITESPACE = '\t\n\x0b\x0c\r '

_PLUS_MINUS_SET = set()

_FORMAT_HANDLERS = {}

_HEX_SET = set()

DIGITS = '0123456789'

_OCT_SET = set()

_DIGIT_SET = set()


