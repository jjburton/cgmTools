"""
# -----------------------------------------------------------------------------
# cpp.py
#
# Author:  David Beazley (http://www.dabeaz.com)
# Copyright (C) 2007
# All rights reserved
#
# This module implements an ANSI-C style lexical preprocessor for PLY. 
# -----------------------------------------------------------------------------
"""

class Preprocessor(object):
    def __init__(self, lexer=None):
        pass
    
    
    def add_path(self, path):
        pass
    
    
    def collect_args(self, tokenlist):
        pass
    
    
    def define(self, tokens):
        pass
    
    
    def error(self, file, line, msg):
        pass
    
    
    def evalexpr(self, tokens):
        pass
    
    
    def expand_macros(self, tokens, expanded=None):
        pass
    
    
    def group_lines(self, input):
        pass
    
    
    def include(self, tokens):
        pass
    
    
    def lexprobe(self):
        pass
    
    
    def macro_expand_args(self, macro, args):
        pass
    
    
    def macro_prescan(self, macro):
        pass
    
    
    def parse(self, input, source=None, ignore={}):
        """
        # ----------------------------------------------------------------------
        # parse()
        #
        # Parse input text.
        # ----------------------------------------------------------------------
        """
    
        pass
    
    
    def parsegen(self, input, source=None):
        """
        # ----------------------------------------------------------------------
        # parsegen()
        #
        # Parse an input string/
        # ----------------------------------------------------------------------
        """
    
        pass
    
    
    def token(self):
        """
        # ----------------------------------------------------------------------
        # token()
        #
        # Method to return individual tokens
        # ----------------------------------------------------------------------
        """
    
        pass
    
    
    def tokenize(self, text):
        pass
    
    
    def tokenstrip(self, tokens):
        pass
    
    
    def undef(self, tokens):
        pass
    
    
    __dict__ = None
    
    __weakref__ = None


class Macro(object):
    def __init__(self, name, value, arglist=None, variadic=False):
        pass
    
    
    __dict__ = None
    
    __weakref__ = None



def t_CPP_STRING(t):
    """
    \"([^\\\n]|(\\(.|\n)))*?\"
    """

    pass


def trigraph(input):
    pass


def t_error(t):
    pass


def t_CPP_COMMENT(t):
    """
    (/\*(.|\n)*?\*/)|(//.*?\n)
    """

    pass


def t_CPP_WS(t):
    """
    \s+
    """

    pass


def t_CPP_CHAR(t):
    """
    (L)?\'([^\\\n]|(\\(.|\n)))*?\'
    """

    pass


def CPP_INTEGER(t):
    """
    (((((0x)|(0X))[0-9a-fA-F]+)|(\d+))([uU]|[lL]|[uU][lL]|[lL][uU])?)
    """

    pass


t_CPP_INTEGER = CPP_INTEGER

t_CPP_FLOAT = r'((\d+)(\.\d+)(e(\+|-)?(\d+))? | (\d+)e(\+|-)?(\d+))([lL]|[fF])?'

t_CPP_POUND = r'\#'

generators = None

_trigraph_pat = None

t_CPP_DPOUND = r'\#\#'

tokens = ()

t_CPP_ID = r'[A-Za-z_][\w_]*'

literals = '+-*/%|&~^<>=!?()[]{}.,;:\\\'"'

_trigraph_rep = {}


