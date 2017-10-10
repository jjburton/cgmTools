from pymel.util.common import unescape

def p_element(t):
    """
    element : declaration_specifiers
    | BREAK
    | CASE
    | CONTINUE
    | DEFAULT
    | DO
    | ELSE
    | FALSE
    | FOR
    | IF
    | IN
    | NO
    | ON
    | OFF
    | RETURN
    | SWITCH
    | TRUE
    | WHILE
    | YES
    | ID
    | VAR
    | ICONST
    | FCONST
    | SCONST
    | PLUS
    | MINUS
    | TIMES
    | DIVIDE
    | MOD
    | NOT
    | CROSS
    | LOR
    | LAND
    | LT
    | LE
    | GT
    | GE
    | EQ
    | NE
    | EQUALS
    | TIMESEQUAL
    | DIVEQUAL
    | MODEQUAL
    | PLUSEQUAL
    | MINUSEQUAL
    | CROSSEQUAL
    | COMPONENT
    | PLUSPLUS
    | MINUSMINUS
    | CONDOP
    | LPAREN
    | RPAREN
    | LBRACKET
    | RBRACKET
    | COMMA
    | SEMI
    | COLON
    | CAPTURE
    | LVEC
    | RVEC
    | COMMENT
    | COMMENT_BLOCK
    | ELLIPSIS
    """

    pass


def p_group_list(t):
    """
    group_list : group_list group
    | group
    """

    pass


def p_group_list_opt(t):
    """
    group_list_opt : group_list
    | empty
    """

    pass


def p_declaration_specifiers(t):
    """
    declaration_specifiers : type_specifier
    | GLOBAL type_specifier
    """

    pass


def p_function_arg_list_opt(t):
    """
    function_arg_list_opt : function_arg_list
    |  empty
    """

    pass


def p_function_arg_list(t):
    """
    function_arg_list : function_arg
    | function_arg_list COMMA function_arg
    """

    pass


def p_group(t):
    """
    group : element
    | LBRACE group_list_opt RBRACE
    """

    pass


def p_function_arg(t):
    """
    function_arg : type_specifier VAR
    | type_specifier VAR LBRACKET RBRACKET
    """

    pass


def p_function_specifiers_opt(t):
    """
    function_specifiers_opt : type_specifier
    | type_specifier LBRACKET RBRACKET
    | empty
    """

    pass


def p_translation_unit(t):
    """
    translation_unit : external_declaration
    | translation_unit external_declaration
    """

    pass


def p_function_declarator(t):
    """
    function_declarator : GLOBAL PROC
    | PROC
    """

    pass


def p_external_declaration(t):
    """
    external_declaration : function_definition
    | group
    """

    pass


def p_function_definition(t):
    """
    function_definition :  function_declarator function_specifiers_opt ID LPAREN function_arg_list_opt RPAREN group
    """

    pass


def p_empty(t):
    """
    empty :
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



tokens = ()


