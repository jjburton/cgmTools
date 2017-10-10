import exceptions

"""
# -----------------------------------------------------------------------------
# ply: lex.py
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
"""

class Lexer:
    def __init__(self):
        pass
    
    
    def __iter__(self):
        """
        # Iterator interface
        """
    
        pass
    
    
    def __next__(self):
        pass
    
    
    def begin(self, state):
        """
        # ------------------------------------------------------------
        # begin() - Changes the lexing state
        # ------------------------------------------------------------
        """
    
        pass
    
    
    def clone(self, object=None):
        pass
    
    
    def current_state(self):
        """
        # ------------------------------------------------------------
        # current_state() - Returns the current lexing state
        # ------------------------------------------------------------
        """
    
        pass
    
    
    def input(self, s):
        """
        # ------------------------------------------------------------
        # input() - Push a new string into the lexer
        # ------------------------------------------------------------
        """
    
        pass
    
    
    def next(self):
        pass
    
    
    def pop_state(self):
        """
        # ------------------------------------------------------------
        # pop_state() - Restores the previous state
        # ------------------------------------------------------------
        """
    
        pass
    
    
    def push_state(self, state):
        """
        # ------------------------------------------------------------
        # push_state() - Changes the lexing state and saves old on stack
        # ------------------------------------------------------------
        """
    
        pass
    
    
    def readtab(self, tabfile, fdict):
        """
        # ------------------------------------------------------------
        # readtab() - Read lexer information from a tab file
        # ------------------------------------------------------------
        """
    
        pass
    
    
    def skip(self, n):
        """
        # ------------------------------------------------------------
        # skip() - Skip ahead n characters
        # ------------------------------------------------------------
        """
    
        pass
    
    
    def token(self):
        """
        # ------------------------------------------------------------
        # opttoken() - Return the next token from the Lexer
        #
        # Note: This function has been carefully implemented to be as fast
        # as possible.  Don't make changes unless you really know what
        # you are doing
        # ------------------------------------------------------------
        """
    
        pass
    
    
    def writetab(self, tabfile, outputdir=''):
        """
        # ------------------------------------------------------------
        # writetab() - Write lexer information to a table file
        # ------------------------------------------------------------
        """
    
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


class LexError(exceptions.Exception):
    def __init__(self, message, s):
        pass
    
    
    __weakref__ = None


class LexerReflect(object):
    """
    # -----------------------------------------------------------------------------
    # LexerReflect()
    #
    # This class represents information needed to build a lexer as extracted from a
    # user's input file.
    # -----------------------------------------------------------------------------
    """
    
    
    
    def __init__(self, ldict, log=None, reflags=0):
        pass
    
    
    def get_all(self):
        """
        # Get all of the basic information
        """
    
        pass
    
    
    def get_literals(self):
        """
        # Get the literals specifier
        """
    
        pass
    
    
    def get_rules(self):
        pass
    
    
    def get_states(self):
        pass
    
    
    def get_tokens(self):
        """
        # Get the tokens map
        """
    
        pass
    
    
    def validate_all(self):
        """
        # Validate all of the information
        """
    
        pass
    
    
    def validate_file(self, filename):
        pass
    
    
    def validate_literals(self):
        """
        # Validate literals
        """
    
        pass
    
    
    def validate_rules(self):
        """
        # Validate all of the t_rules collected
        """
    
        pass
    
    
    def validate_tokens(self):
        """
        # Validate the tokens
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


class LexToken(object):
    """
    # Token class.  This class is used to represent the tokens produced.
    """
    
    
    
    def __repr__(self):
        pass
    
    
    def __str__(self):
        pass
    
    
    __dict__ = None
    
    __weakref__ = None



def get_caller_module_dict(levels):
    pass


def func_code(f):
    pass


def runmain(lexer=None, data=None):
    pass


def token(self):
    """
    # ------------------------------------------------------------
    # opttoken() - Return the next token from the Lexer
    #
    # Note: This function has been carefully implemented to be as fast
    # as possible.  Don't make changes unless you really know what
    # you are doing
    # ------------------------------------------------------------
    """

    pass


def input(self, s):
    """
    # ------------------------------------------------------------
    # input() - Push a new string into the lexer
    # ------------------------------------------------------------
    """

    pass


def TOKEN(r):
    pass


def lex(module=None, object=None, debug=0, optimize=0, lextab='lextab', reflags=0, nowarn=0, outputdir='', debuglog=None, errorlog=None):
    """
    # -----------------------------------------------------------------------------
    # lex(module)
    #
    # Build all of the regular expression rules from definitions in the supplied module
    # -----------------------------------------------------------------------------
    """

    pass


def _statetoken(s, names):
    pass


def _form_master_re(relist, reflags, ldict, toknames):
    pass


def _funcs_to_names(funclist, namelist):
    pass


def _names_to_funcs(namelist, fdict):
    pass



_is_identifier = None

StringTypes = ()

lexer = Lexer()

__version__ = '3.3'


