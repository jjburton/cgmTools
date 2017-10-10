from pymel.core.general import *
from pymel.core.system import *
from pymel.core.rendering import *
from pymel.core.windows import *
from pymel.core.modeling import *
from pymel.core.other import *
from pymel.core.context import *
from pymel.core.effects import *
from pymel.core.animation import *

from pymel.core.language import MelConversionError
from pymel.core.language import pythonToMel
from pymel.core.language import stackTrace
from pymel.core.language import setMelGlobal
from pymel.core.language import Mel
from pymel.core.language import MelUnknownProcedureError
from pymel.core.language import getLastError
from pymel.core.language import scriptJob
from pymel.core.language import MelGlobals
from pymel.core.language import Catch
from pymel.core.language import Env
from pymel.core.language import MelCallable
from pymel.core.language import MelArgumentError
from pymel.core.language import evalEcho
from pymel.core.language import OptionVarDict
from pymel.core.language import MelError
from pymel.core.language import pythonToMelCmd
from pymel.core.language import melOptions
from pymel.core.language import MelSyntaxError
from pymel.core.language import isValidMelType
from pymel.core.language import conditionExists
from pymel.core.language import getMelGlobal
from pymel.core.language import waitCursor
from pymel.core.language import OptionVarList
from pymel.core.language import callbacks
from pymel.core.language import sortCaseInsensitive
from pymel.util.common import unescape
from pymel.util.utilitytypes import TwoWayDict
from pymel.core.language import evalNoSelectNotify
from pymel.core.language import resourceManager
from pymel.core.language import python
from pymel.core.language import getProcArguments
from pymel.core.language import getMelType

class MelScanner(object):
    """
    Basic mel parser which only tries to get information about procs
    """
    
    
    
    def build(self):
        pass
    
    
    def parse(self, data):
        pass
    
    
    __dict__ = None
    
    __weakref__ = None


class Comment(object):
    def __init__(self, token):
        pass
    
    
    def format(self):
        pass
    
    
    def leadingSpace(self):
        pass
    
    
    def withLeadingSpace(self):
        pass
    
    
    def join(cls, comments, stripCommonSpace=False):
        pass
    
    
    __dict__ = None
    
    __weakref__ = None


class MelParser(object):
    """
    The MelParser class around which all other mel2py functions are based.
    """
    
    
    
    def build(self, rootModule=None, pymelNamespace='', verbosity=0, addPymelImport=True, expressionsOnly=False, forceCompatibility=True, parentData=None):
        pass
    
    
    def parse(self, data):
        pass
    
    
    __dict__ = None
    
    __weakref__ = None


class BatchData(object):
    def __init__(self, **kwargs):
        pass
    
    
    def __new__(cls, *p, **k):
        """
        # redefine __new__
        """
    
        pass
    
    
    __dict__ = None
    
    __weakref__ = None


import __builtin__ as builtin_module

class MelParseError(builtin_module.Exception):
    def __init__(self, *args, **kwargs):
        pass
    
    
    def __str__(self):
        pass
    
    
    __weakref__ = None


class Token(str):
    def __add__(self, other):
        pass
    
    
    def __getslice__(self, start, end):
        pass
    
    
    def __new__(cls, val, type, lineno=None, **kwargs):
        pass
    
    
    __dict__ = None


class ArrayToken(Token):
    def __new__(cls, val, type, size, lineno=None, **kwargs):
        pass


class ExpressionParseError(MelParseError, builtin_module.TypeError):
    """
    Error when mel code cannot be parsed into a python expression
    """
    
    
    
    pass



def p_equality_expression_1(t):
    """
    equality_expression : relational_expression
    | equality_expression EQ relational_expression
    | equality_expression NE relational_expression
    """

    pass


def p_declarator_2(t):
    """
    declarator :  declarator LBRACKET constant_expression_opt RBRACKET
    """

    pass


def format_held_comments(t, funcname=''):
    pass


def p_constant_expression(t):
    """
    constant_expression : conditional_expression
    """

    pass


def p_expression_list(t):
    """
    expression_list : expression
    | expression_list COMMA expression
    """

    pass


def p_iteration_statement_1(t):
    """
    iteration_statement : WHILE LPAREN expression RPAREN hold_comments statement_required
    """

    pass


def p_function_arg(t):
    """
    function_arg : type_specifier variable
    | type_specifier variable LBRACKET RBRACKET
    """

    pass


def _error(t):
    pass


def p_object_list(t):
    """
    object_list : object
    | object_list object
    """

    pass


def merge_assignment_spillover(t, curr_lineno, title=''):
    pass


def p_unary_expression_2(t):
    """
    unary_expression : PLUSPLUS unary_expression
    | MINUSMINUS unary_expression
    """

    pass


def strip_leading_space(text):
    """
    Given a text block consisting of multiple lines, strip out common
    whitespace that appears at the start of every non-empty line
    """

    pass


def p_relational_expression_1(t):
    """
    relational_expression : shift_expression
    | relational_expression LT shift_expression
    | relational_expression GT shift_expression
    | relational_expression LE shift_expression
    | relational_expression GE shift_expression
    """

    pass


def p_assignment_expression(t):
    """
    assignment_expression : equality_expression
    | postfix_expression assignment_operator assignment_expression
    """

    pass


def getModuleBasename(script):
    pass


def p_init_declarator(t):
    """
    init_declarator : declarator
    | declarator EQUALS expression
    """

    pass


def p_postfix_expression(t):
    """
    postfix_expression : primary_expression
    | postfix_expression PLUSPLUS
    | postfix_expression MINUSMINUS
    """

    pass


def p_selection_statement_2(t):
    """
    selection_statement : IF LPAREN expression RPAREN statement_required ELSE hold_comments statement_required
    """

    pass


def p_labeled_statement_list(t):
    """
    labeled_statement_list : labeled_statement
    | labeled_statement_list labeled_statement
    """

    pass


def p_constant_expression_opt_1(t):
    """
    constant_expression_opt : empty
    """

    pass


def format_command(command, args, t):
    pass


def hasNonCommentPyCode(pyCode):
    """
    Returns True if the given chunk of python code has any lines that contain
    something other than a comment or whitespace
    """

    pass


def p_statement_complex(t):
    """
    statement : selection_statement
    | iteration_statement
    | jump_statement
    | declaration_statement
    """

    pass


def p_function_declarator(t):
    """
    function_declarator : GLOBAL PROC
    | PROC
    """

    pass


def p_command(t):
    """
    command : ID
    | ID command_input_list
    """

    pass


def p_vector_element_list(t):
    """
    vector_element_list : expression
    | vector_element_list COMMA expression
    """

    pass


def p_logical_or_expression_1(t):
    """
    logical_or_expression : logical_and_expression
    | logical_or_expression LOR logical_and_expression
    """

    pass


def p_type_specifier(t):
    """
    type_specifier : INT
    | FLOAT
    | STRING
    | VECTOR
    | MATRIX
    """

    pass


def p_error(t):
    pass


def p_command_input_list(t):
    """
    command_input_list : command_input
    | command_input_list command_input
    """

    pass


def p_boolean_true(t):
    """
    boolean : ON
    | TRUE
    | YES
    """

    pass


def p_primary_expression1(t):
    """
    primary_expression :     SCONST
    """

    pass


def format_singleline_comments(comments):
    pass


def p_procedure_expression_list(t):
    """
    procedure_expression_list : constant_expression
    | procedure_expression_list COMMA constant_expression
    """

    pass


def p_object_2(t):
    """
    object    : ID LBRACKET expression RBRACKET
    """

    pass


def p_logical_and_expression_1(t):
    """
    logical_and_expression : assignment_expression
    | logical_and_expression LAND assignment_expression
    """

    pass


def format_fopen(x, t):
    pass


def p_additive_expression(t):
    """
    additive_expression : multiplicative_expression
    | additive_expression PLUS multiplicative_expression
    | additive_expression MINUS multiplicative_expression
    """

    pass


def vprint(t, *args):
    pass


def p_hold_comments(t):
    """
    hold_comments :
    """

    pass


def p_command_statement_input_2(t):
    """
    command_statement_input     : object_list
    """

    pass


def pythonizeName(name):
    pass


def p_matrix_row_list_1(t):
    """
    matrix_row_list : vector_element_list SEMI vector_element_list
    """

    pass


def p_conditional_expression_1(t):
    """
    conditional_expression : logical_or_expression
    """

    pass


def p_postfix_expression_3(t):
    """
    postfix_expression : LVEC vector_element_list RVEC
    """

    pass


def p_declaration_statement(t):
    """
    declaration_statement : declaration_specifiers init_declarator_list SEMI
    """

    pass


def p_statement_list(t):
    """
    statement_list   : statement
    | statement_list statement
    """

    pass


def p_labeled_statement_2(t):
    """
    labeled_statement : CASE constant_expression COLON statement_list_opt
    """

    pass


def p_postfix_expression_4(t):
    """
    postfix_expression : LVEC matrix_row_list RVEC
    """

    pass


def p_translation_unit(t):
    """
    translation_unit : external_declaration
    | translation_unit external_declaration
    """

    pass


def p_constant_expression_opt_2(t):
    """
    constant_expression_opt : constant_expression
    """

    pass


def format_tokenize_size(tokenized, sizeVar):
    """
    tokenize fix:
    tokenize passes a buffer by reference, and returns a size.
    we must return a list, and compute the size as a second operation::
    
        int $size = `tokenize "foo bar", $buffer, " "`;
    
        buffer = "foo bar".split(' ')
        size = len(buffer)
    """

    pass


def p_expression_list_opt(t):
    """
    expression_list_opt : expression_list
    | empty
    """

    pass


def _melObj_to_pyModule(script):
    """
    Return the module name this mel script / procedure will be converted to / found in.
    
    If the mel script is not being translated, returns None.
    """

    pass


def p_command_input(t):
    """
    command_input : unary_expression
    | command_flag
    """

    pass


def p_command_statement_input(t):
    """
    command_statement_input : unary_expression
    | command_flag
      | command_expression
    """

    pass


def p_command_statement_input_list(t):
    """
    command_statement_input_list : command_statement_input
    | command_statement_input_list command_statement_input
    """

    pass


def format_held_comments_and_docstring(t, funcname=''):
    """
    Splits the held comments into the last comment block and the rest of the
    comments, formats the rest of the comments normally, and formats the last
    block as a multiline string.
    
    A comment block is either a group of mel-single-line-comments, or a single
    mel-comment-block
    
    This is useful for grabbing the "last" comment before something, and
    formatting it for use as a docstrign - for instance, if we have, in mel:
    
        // Some section
        // -----------------------
    
        /*
         * docProc: does stuff
         */
        global proc docProc() {};
    
    ...then we only want to grab the last comment block, and format it as
    a docstring... similarly, if the situation is something like this:
    
        /*
         * Some long notes here
         *    batman
         *    superman
         *    king kong
         *    the tick
         */
    
        // proctopus
        // does stuff
        global proc proctopus() {};
    """

    pass


def p_expression(t):
    """
    expression : conditional_expression
    """

    pass


def p_iteration_statement_2(t):
    """
    iteration_statement : FOR LPAREN expression_list_opt SEMI expression_list_opt SEMI expression_list_opt RPAREN hold_comments statement_required
    """

    pass


def p_function_arg_list(t):
    """
    function_arg_list : function_arg
    | function_arg_list COMMA function_arg
    """

    pass


def p_primary_expression2(t):
    """
    primary_expression :     variable
    """

    pass


def p_function_definition(t):
    """
    function_definition :  function_declarator function_specifiers_opt ID seen_func LPAREN function_arg_list_opt RPAREN hold_comments compound_statement
    """

    pass


def p_unary_command_expression(t):
    """
    unary_command_expression : procedure_expression
    | unary_operator procedure_expression
    """

    pass


def p_labeled_statement_3(t):
    """
    labeled_statement : DEFAULT COLON statement_list_opt
    """

    pass


def format_substring(x, t):
    """
    convert:
        substring( var, 2, (len(var)) )
    to:
        var[1:]
    
    or:
        substring( var, 2, var2 )
    to:
        var[1:var2]
    
    or:
        substring( var, 3, var2 )
    to:
        var[1:var2]
    """

    pass


def p_assignment_operator(t):
    """
    assignment_operator : EQUALS
                        | TIMESEQUAL
                        | DIVEQUAL
                        | MODEQUAL
                        | PLUSEQUAL
                        | MINUSEQUAL
                        | CROSSEQUAL
    """

    pass


def findModule(moduleName):
    pass


def p_statement_required(t):
    """
    statement_required : statement
    """

    pass


def p_variable_vector_component(t):
    """
    variable :  VAR COMPONENT
    """

    pass


def append_comments(t, funcname=''):
    pass


def p_function_arg_list_opt(t):
    """
    function_arg_list_opt : function_arg_list
    |  empty
    """

    pass


def p_postfix_expression_2(t):
    """
    postfix_expression : LBRACE expression_list_opt RBRACE
    """

    pass


def store_assignment_spillover(token, t):
    pass


def p_unary_expression(t):
    """
    unary_expression : postfix_expression
    | unary_operator cast_expression
    """

    pass


def p_flag(t):
    """
    command_flag : MINUS ID
    | MINUS BREAK
    | MINUS CASE
    | MINUS CONTINUE
    | MINUS DEFAULT
    | MINUS DO
    | MINUS ELSE
    | MINUS FALSE
    | MINUS FLOAT
    | MINUS FOR
    | MINUS GLOBAL
    | MINUS IF
    | MINUS IN
    | MINUS INT
    | MINUS NO
    | MINUS ON
    | MINUS OFF
    | MINUS PROC
    | MINUS RETURN
    | MINUS STRING
    | MINUS SWITCH
    | MINUS TRUE
    | MINUS VECTOR
    | MINUS WHILE
    | MINUS YES
    """

    pass


def p_command_input_2(t):
    """
    command_input     : object_list
    """

    pass


def p_variable(t):
    """
    variable : VAR
    """

    pass


def p_primary_expression_paren(t):
    """
    primary_expression :    LPAREN expression RPAREN
    """

    pass


def format_comments(comments):
    pass


def p_jump_statement(t):
    """
    jump_statement : CONTINUE SEMI
    | BREAK SEMI
    | RETURN expression_opt SEMI
    """

    pass


def p_expression_opt(t):
    """
    expression_opt : empty
    | expression
    """

    pass


def p_init_declarator_list(t):
    """
    init_declarator_list : init_declarator
    | init_declarator_list COMMA init_declarator
    """

    pass


def p_unary_operator(t):
    """
    unary_operator : PLUS
    | MINUS
    | NOT
    """

    pass


def p_boolean_false(t):
    """
    boolean : OFF
    | FALSE
    | NO
    """

    pass


def format_multiline_string_comment(comments):
    pass


def format_fread(x, t):
    pass


def p_selection_statement_1(t):
    """
    selection_statement : IF LPAREN expression RPAREN statement_required
    """

    pass


def format_source(x, t):
    pass


def p_multiplicative_expression(t):
    """
    multiplicative_expression : cast_expression
    | multiplicative_expression TIMES cast_expression
    | multiplicative_expression DIVIDE cast_expression
    | multiplicative_expression MOD cast_expression
    | multiplicative_expression CROSS cast_expression
    """

    pass


def toList(t):
    pass


def p_statement_simple(t):
    """
    statement : expression_statement
    | command_statement
    | compound_statement
    """

    pass


def p_seen_FOR(t):
    """
    seen_FOR :
    """

    pass


def p_compound_statement(t):
    """
    compound_statement   : LBRACE statement_list RBRACE
    | LBRACE RBRACE
    """

    pass


def p_declarator_1(t):
    """
    declarator : variable
    """

    pass


def p_matrix_row_list_2(t):
    """
    matrix_row_list : matrix_row_list SEMI vector_element_list
    """

    pass


def p_conditional_expression_2(t):
    """
    conditional_expression : logical_or_expression CONDOP expression COLON conditional_expression
    """

    pass


def p_iteration_statement_4(t):
    """
    iteration_statement : DO statement_required WHILE LPAREN expression RPAREN SEMI
    """

    pass


def format_assignment_value(val, typ):
    """
    when assigning a value in mel, values will be auto-cast to the type of the variable, but in python, the variable
    will simply become the new type.  to ensure that the python operates as in mel, we need to cast when assigning
    a value to a variable of a different type
    """

    pass


def p_declaration_specifiers(t):
    """
    declaration_specifiers : type_specifier
    | GLOBAL type_specifier
    """

    pass


def p_float_constant(t):
    """
    float_constant :     FCONST
    """

    pass


def p_procedure(t):
    """
    procedure : ID LPAREN procedure_expression_list RPAREN
    | ID LPAREN RPAREN
    """

    pass


def p_function_specifiers_opt(t):
    """
    function_specifiers_opt : type_specifier
    | type_specifier LBRACKET RBRACKET
    | empty
    """

    pass


def p_statement_list_opt(t):
    """
    statement_list_opt : statement_list
    | empty
    """

    pass


def p_empty(t):
    """
    empty :
    """

    pass


def p_command_input_3(t):
    """
    command_input     : ELLIPSIS
    """

    pass


def p_command_statement_input_3(t):
    """
    command_statement_input     : ELLIPSIS
    """

    pass


def p_primary_expression(t):
    """
    primary_expression :    boolean
    |    numerical_constant
    """

    pass


def p_object_1(t):
    """
    object    : ID
    """

    pass


def p_int_constant(t):
    """
    int_constant :     ICONST
    """

    pass


def p_shift_expression(t):
    """
    shift_expression : additive_expression
    """

    pass


def p_command_statement(t):
    """
    command_statement : ID SEMI
    | ID command_statement_input_list SEMI
    """

    pass


def find_num_leading_space(text):
    """
    Given a text block consisting of multiple lines, find the number of
    characters in the longest common whitespace that appears at the start of
    every non-empty line
    """

    pass


def _melProc_to_pyModule(t, procedure):
    """
    determine if this procedure has been or will be converted into python, and if so, what module it belongs to
    """

    pass


def p_external_declaration(t):
    """
    external_declaration : statement
    | function_definition
    """

    pass


def p_procedure_expression(t):
    """
    procedure_expression : command_expression
    | procedure
    """

    pass


def p_seen_func(t):
    """
    seen_func :
    """

    pass


def p_cast_expression(t):
    """
    cast_expression : unary_expression
    | unary_command_expression
    | type_specifier LPAREN expression RPAREN
    | LPAREN type_specifier RPAREN cast_expression
    """

    pass


def p_postfix_expression_5(t):
    """
    postfix_expression : postfix_expression LBRACKET expression RBRACKET
    """

    pass


def p_iteration_statement_3(t):
    """
    iteration_statement : FOR LPAREN variable IN expression seen_FOR RPAREN hold_comments statement_required
    """

    pass


def entabLines(line):
    pass


def p_numerical_constant(t):
    """
    numerical_constant : int_constant
    | float_constant
    """

    pass


def assemble(t, funcname, separator='', tokens=None, matchFormatting=False):
    pass


def p_expression_statement(t):
    """
    expression_statement : expression_opt SEMI
    """

    pass


def p_selection_statement_3(t):
    """
    selection_statement : SWITCH LPAREN expression RPAREN hold_comments LBRACE labeled_statement_list RBRACE
    """

    pass


def fileInlist(file, fileList):
    """
    # def _script_to_module( t, script ):
    #    global batchData.currentFiles
    #    global script_to_module
    #
    #    path, name = os.path.split(script)
    #    if name.endswith('.mel'):
    #        name += '.mel'
    #
    #    try:
    #        return script_to_module[name]
    #
    #    except KeyError:
    #
    #        if not path:
    #            result = mel.whatIs( name )
    #            buf = result.split( ':' )
    #            if buf[0] == 'Script found in':
    #                fullpath = buf[1]
    #            else:
    #                return
    #        else:
    #            fullpath = os.path.join(path, name )
    #
    #
    #        moduleName = getModuleBasename(fullpath)
    #
    #
    #        # the mel file in which this proc is defined is being converted with this batch
    #        if fullpath in batchData.currentFiles:
    #            script_to_module[name] = moduleName
    #            return moduleName
    """

    pass


def p_command_expression(t):
    """
    command_expression : CAPTURE command CAPTURE
    """

    pass


def format_tokenize(x, t):
    pass



melCmdFlagList = {}

pythonReservedWords = []

proc_remap = {}

tag = '# script created by pymel.tools.mel2py'

_outputdir = '/var/folders/8l/_gxk_gxx4xxdrfc27y0fjj0r0000zg/T'

x = 'whatIs'

catch = None

filteredCmds = []

optionVar = {}

default_values = {}

parser = None

NON_COMMENT_LINE_RE = None

batchData = BatchData()

FLAG_RE = None

scanner = None

mel_type_to_python_type = {}

tokens = ()

reserved = set()

MELTYPES = []

env = None

melCmdList = []

lexer = None


