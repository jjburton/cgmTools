"""
    compare_translate : Comparison for a DAG node's translation values
    compare_rotate    : Comparison for a DAG node's rotation values
    compare_scale     : Comparison for a DAG node's scale values
    compare_floats    : Generic comparison for float values

Each method returns a closeness measurement indicating how equal the values are.
The measurement is the log10 of the average  of the numbers divided by the
difference, with values near zero being treated as completely equal. Larger values
are a closer match.

    ALL_SIGNIFICANT_DIGITS_MATCH : Indicates the numbers are functionally identical
    NO_SIGNIFICANT_DIGITS_MATCH  : Indicates the numbers are complete different
    DEFAULT_SIGNIFICANT_DIGITS   : A good first guess at a reasonable closeness measure

The closeness of a list of values equals the closeness of the worst match in the list.
e.g. [0.0,0.0,1.0] will be completely unmatched by [0.0,0.0,0.5] even though two of the
     three values are the same.
"""

def compare_wm(node, expected):
    """
    Compare the world matrix values of the node against the expected values
    passed in. A TypeError exception is raised of the list passed in isn't
    of the correct length and type. Only the first instance is checked (wm[0])
    """

    pass


def closeness(first_num, second_num):
    """
    Returns measure of equality (for two floats), in unit
    of decimal significant figures.
    """

    pass


def compare_scale(node, expected):
    """
    Compare the scale values of the node against the expected values
    passed in. A TypeError exception is raised of the list passed in isn't
    of the correct length and type.
    """

    pass


def compare_rotate(node, expected):
    """
    Compare the rotation values of the node against the expected values
    passed in. A TypeError exception is raised of the list passed in isn't
    of the correct length and type.
    """

    pass


def compare_floats(float_list1, float_list2):
    """
    Compare two space-separated lists of floating point numbers.
    Return True if they are the same, False if they differ.
    
    float_list1: First list of floats
    float_list1: Second list of floats
    
    Arguments can be:
        simple values - compare_floats( 1.0, 1.0 )
        lists         - compare_floats( [1.0,2.0], [1.0,2.0] )
        strings       - compare_floats( "1.0 2.0", "1.0 2.0" )
    
    Returns the worst match, in significant digits (0 means no match at all).
    """

    pass


def compare_translate(node, expected):
    """
    Compare the translation values of the node against the expected values
    passed in. A TypeError exception is raised of the list passed in isn't
    of the correct length and type.
    """

    pass



ALL_SIGNIFICANT_DIGITS_MATCH = 999

DEFAULT_SIGNIFICANT_DIGITS = 3

NO_SIGNIFICANT_DIGITS_MATCH = 0


