import exceptions

"""
# -----------------------------------------------------------------------------
# ply: yacc.py
#
# Copyright (C) 2001-2009,
# David M. Beazley (Dabeaz LLC)
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
# 
# * Redistributions of source code must retain the above copyright notice,
#   this list of conditions and the following disclaimer.  
# * Redistributions in binary form must reproduce the above copyright notice, 
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.  
# * Neither the name of the David Beazley or Dabeaz LLC may be used to
#   endorse or promote products derived from this software without
#  specific prior written permission. 
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# -----------------------------------------------------------------------------
#
# This implements an LR parser that is constructed from grammar rules defined
# as Python functions. The grammer is specified by supplying the BNF inside
# Python documentation strings.  The inspiration for this technique was borrowed
# from John Aycock's Spark parsing system.  PLY might be viewed as cross between
# Spark and the GNU bison utility.
#
# The current implementation is only somewhat object-oriented. The
# LR parser itself is defined in terms of an object (which allows multiple
# parsers to co-exist).  However, most of the variables used during table
# construction are defined in terms of global variables.  Users shouldn't
# notice unless they are trying to define multiple parsers at the same
# time using threads (in which case they should have their head examined).
#
# This implementation supports both SLR and LALR(1) parsing.  LALR(1)
# support was originally implemented by Elias Ioup (ezioup@alumni.uchicago.edu),
# using the algorithm found in Aho, Sethi, and Ullman "Compilers: Principles,
# Techniques, and Tools" (The Dragon Book).  LALR(1) has since been replaced
# by the more efficient DeRemer and Pennello algorithm.
#
# :::::::: WARNING :::::::
#
# Construction of LR parsing tables is fairly complicated and expensive.
# To make this module run fast, a *LOT* of work has been put into
# optimization---often at the expensive of readability and what might
# consider to be good Python "coding style."   Modify the code at your
# own risk!
# ----------------------------------------------------------------------------
"""

class LRParser:
    def __init__(self, lrtab, errorf):
        pass
    
    
    def errok(self):
        pass
    
    
    def parse(self, input=None, lexer=None, debug=0, tracking=0, tokenfunc=None):
        pass
    
    
    def parsedebug(self, input=None, lexer=None, debug=None, tracking=0, tokenfunc=None):
        pass
    
    
    def parseopt(self, input=None, lexer=None, debug=0, tracking=0, tokenfunc=None):
        pass
    
    
    def parseopt_notrack(self, input=None, lexer=None, debug=0, tracking=0, tokenfunc=None):
        pass
    
    
    def restart(self):
        pass


class NullLogger(object):
    """
    # Null logger is used when no output is generated. Does nothing.
    """
    
    
    
    def __call__(self, *args, **kwargs):
        pass
    
    
    def __getattribute__(self, name):
        pass
    
    
    __dict__ = None
    
    __weakref__ = None


class Grammar(object):
    def __getitem__(self, index):
        pass
    
    
    def __init__(self, terminals):
        pass
    
    
    def __len__(self):
        pass
    
    
    def add_production(self, prodname, syms, func=None, file='', line=0):
        pass
    
    
    def build_lritems(self):
        pass
    
    
    def compute_first(self):
        """
        # -------------------------------------------------------------------------
        # compute_first()
        #
        # Compute the value of FIRST1(X) for all symbols
        # -------------------------------------------------------------------------
        """
    
        pass
    
    
    def compute_follow(self, start=None):
        """
        # ---------------------------------------------------------------------
        # compute_follow()
        #
        # Computes all of the follow sets for every non-terminal symbol.  The
        # follow set is the set of all symbols that might follow a given
        # non-terminal.  See the Dragon book, 2nd Ed. p. 189.
        # ---------------------------------------------------------------------
        """
    
        pass
    
    
    def find_unreachable(self):
        pass
    
    
    def infinite_cycles(self):
        pass
    
    
    def set_precedence(self, term, assoc, level):
        pass
    
    
    def set_start(self, start=None):
        pass
    
    
    def undefined_symbols(self):
        """
        # -----------------------------------------------------------------------------
        # undefined_symbols()
        #
        # Find all symbols that were used the grammar, but not defined as tokens or
        # grammar rules.  Returns a list of tuples (sym, prod) where sym in the symbol
        # and prod is the production where the symbol was used. 
        # -----------------------------------------------------------------------------
        """
    
        pass
    
    
    def unused_precedence(self):
        pass
    
    
    def unused_rules(self):
        pass
    
    
    def unused_terminals(self):
        """
        # -----------------------------------------------------------------------------
        # unused_terminals()
        #
        # Find all terminals that were defined, but not used by the grammar.  Returns
        # a list of all symbols.
        # -----------------------------------------------------------------------------
        """
    
        pass
    
    
    __dict__ = None
    
    __weakref__ = None


class PlyLogger(object):
    def __init__(self, f):
        pass
    
    
    def critical(self, msg, *args, **kwargs):
        pass
    
    
    def debug(self, msg, *args, **kwargs):
        pass
    
    
    def error(self, msg, *args, **kwargs):
        pass
    
    
    def info(self, msg, *args, **kwargs):
        pass
    
    
    def warning(self, msg, *args, **kwargs):
        pass
    
    
    __dict__ = None
    
    __weakref__ = None


class LRTable(object):
    def __init__(self):
        pass
    
    
    def bind_callables(self, pdict):
        """
        # Bind all production function names to callable objects in pdict
        """
    
        pass
    
    
    def read_pickle(self, filename):
        pass
    
    
    def read_table(self, module):
        pass
    
    
    __dict__ = None
    
    __weakref__ = None


class Production(object):
    def __getitem__(self, index):
        pass
    
    
    def __init__(self, number, name, prod, precedence=('right', 0), func=None, file='', line=0):
        pass
    
    
    def __len__(self):
        pass
    
    
    def __nonzero__(self):
        pass
    
    
    def __repr__(self):
        pass
    
    
    def __str__(self):
        pass
    
    
    def bind(self, pdict):
        """
        # Bind the production function name to a callable
        """
    
        pass
    
    
    def lr_item(self, n):
        """
        # Return the nth lr_item from the production (or None if at the end)
        """
    
        pass
    
    
    __dict__ = None
    
    __weakref__ = None
    
    reduced = 0


class YaccSymbol:
    def __repr__(self):
        pass
    
    
    def __str__(self):
        pass


class LRItem(object):
    def __init__(self, p, n):
        pass
    
    
    def __repr__(self):
        pass
    
    
    def __str__(self):
        pass
    
    
    __dict__ = None
    
    __weakref__ = None


class YaccProduction:
    def __getitem__(self, n):
        pass
    
    
    def __getslice__(self, i, j):
        pass
    
    
    def __init__(self, s, stack=None):
        pass
    
    
    def __len__(self):
        pass
    
    
    def __setitem__(self, n, v):
        pass
    
    
    def error(self):
        pass
    
    
    def lexpos(self, n):
        pass
    
    
    def lexspan(self, n):
        pass
    
    
    def lineno(self, n):
        pass
    
    
    def linespan(self, n):
        pass
    
    
    def set_lineno(self, n, lineno):
        pass


class YaccError(exceptions.Exception):
    """
    # Exception raised for yacc-related errors
    """
    
    
    
    __weakref__ = None


class ParserReflect(object):
    """
    # -----------------------------------------------------------------------------
    # ParserReflect()
    #
    # This class represents information extracted for building a parser including
    # start symbol, error function, tokens, precedence list, action functions,
    # etc.
    # -----------------------------------------------------------------------------
    """
    
    
    
    def __init__(self, pdict, log=None):
        pass
    
    
    def get_all(self):
        """
        # Get all of the basic information
        """
    
        pass
    
    
    def get_error_func(self):
        """
        # Look for error handler
        """
    
        pass
    
    
    def get_pfunctions(self):
        """
        # Get all p_functions from the grammar
        """
    
        pass
    
    
    def get_precedence(self):
        """
        # Get the precedence map (if any)
        """
    
        pass
    
    
    def get_start(self):
        """
        # Get the start symbol
        """
    
        pass
    
    
    def get_tokens(self):
        """
        # Get the tokens map
        """
    
        pass
    
    
    def signature(self):
        """
        # Compute a signature over the grammar
        """
    
        pass
    
    
    def validate_all(self):
        """
        # Validate all of the information
        """
    
        pass
    
    
    def validate_error_func(self):
        """
        # Validate the error function
        """
    
        pass
    
    
    def validate_files(self):
        pass
    
    
    def validate_pfunctions(self):
        """
        # Validate all of the p_functions
        """
    
        pass
    
    
    def validate_precedence(self):
        """
        # Validate and parse the precedence map
        """
    
        pass
    
    
    def validate_start(self):
        """
        # Validate the start symbol
        """
    
        pass
    
    
    def validate_tokens(self):
        """
        # Validate the tokens
        """
    
        pass
    
    
    __dict__ = None
    
    __weakref__ = None


class MiniProduction(object):
    """
    # This class serves as a minimal standin for Production objects when
    # reading table data from files.   It only contains information
    # actually used by the LR parsing engine, plus some additional
    # debugging information.
    """
    
    
    
    def __init__(self, str, name, len, func, file, line):
        pass
    
    
    def __repr__(self):
        pass
    
    
    def __str__(self):
        pass
    
    
    def bind(self, pdict):
        """
        # Bind the production function name to a callable
        """
    
        pass
    
    
    __dict__ = None
    
    __weakref__ = None


class VersionError(YaccError):
    pass


class LRGeneratedTable(LRTable):
    def __init__(self, grammar, method='LALR', log=None):
        pass
    
    
    def add_lalr_lookaheads(self, C):
        pass
    
    
    def add_lookaheads(self, lookbacks, followset):
        pass
    
    
    def compute_follow_sets(self, ntrans, readsets, inclsets):
        pass
    
    
    def compute_lookback_includes(self, C, trans, nullable):
        pass
    
    
    def compute_nullable_nonterminals(self):
        pass
    
    
    def compute_read_sets(self, C, ntrans, nullable):
        pass
    
    
    def dr_relation(self, C, trans, nullable):
        pass
    
    
    def find_nonterminal_transitions(self, C):
        pass
    
    
    def lr0_closure(self, I):
        pass
    
    
    def lr0_goto(self, I, x):
        pass
    
    
    def lr0_items(self):
        """
        # Compute the LR(0) sets of item function
        """
    
        pass
    
    
    def lr_parse_table(self):
        """
        # -----------------------------------------------------------------------------
        # lr_parse_table()
        #
        # This function constructs the parse tables for SLR or LALR
        # -----------------------------------------------------------------------------
        """
    
        pass
    
    
    def pickle_table(self, filename, signature=''):
        pass
    
    
    def reads_relation(self, C, trans, empty):
        pass
    
    
    def write_table(self, modulename, outputdir='', signature=''):
        pass


class LALRError(YaccError):
    pass


class GrammarError(YaccError):
    pass



def func_code(f):
    pass


def rightmost_terminal(symbols, terminals):
    """
    # -----------------------------------------------------------------------------
    # rightmost_terminal()
    #
    # Return the rightmost terminal from a list of symbols.  Used in add_production()
    # -----------------------------------------------------------------------------
    """

    pass


def digraph(X, R, FP):
    pass


def format_stack_entry(r):
    """
    # Format stack entries when the parser is running in debug mode
    """

    pass


def parse(self, input=None, lexer=None, debug=0, tracking=0, tokenfunc=None):
    pass


def traverse(x, N, stack, F, X, R, FP):
    pass


def get_caller_module_dict(levels):
    pass


def yacc(method='LALR', debug=1, module=None, tabmodule='parsetab', start=None, check_recursion=1, optimize=0, write_tables=1, debugfile='parser.out', outputdir='', debuglog=None, errorlog=None, picklefile=None):
    pass


def load_ply_lex():
    """
    # Python 2.x/3.0 compatibility.
    """

    pass


def parse_grammar(doc, file, line):
    """
    # -----------------------------------------------------------------------------
    # parse_grammar()
    #
    # This takes a raw grammar rule string and parses it into production data
    # -----------------------------------------------------------------------------
    """

    pass


def format_result(r):
    """
    # Format the result message that the parser produces when running in debug mode.
    """

    pass



default_lr = 'LALR'

pickle_protocol = 0

debug_file = 'parser.out'

resultlimit = 40

error_count = 3

__version__ = '3.3'

MAXINT = 9223372036854775807

_is_identifier = None

tab_module = 'parsetab'

yaccdebug = 1


