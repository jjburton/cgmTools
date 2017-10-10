"""
Collection of general utilities for use with Maya analytics. See the help
string for each method for more details.

    list_analytics              : List all of the available analytics
"""

def bootstrap_analytics():
    """
    Bootstrap loading of the analytics in the same directory as this script.
    It only looks for files with the prefix "analytic" but you can add any
    analytics at other locations by using the @makeAnalytic decorator for
    per-file analytics or the @make_static_analytic decorator for analytics
    that are independent of scene content, and importing them before calling
    list_analytics.
    """

    pass


def analytic_by_name(analyticName):
    """
    Get an analytic class object by name. If no anaytic of that name exists
    then a KeyError exception is raised.
    """

    pass


def add_analytic(name, cls):
    """
    Add a new analytic to the global list. Used by the decorator
    'makeAnalytic' to mark a class as being an analytic.
    """

    pass


def list_analytics():
    """
    List all of the objects in this packages that perform analysis of the
    Maya scene for output. They were gleaned from the list collected by
    the use of the @makeAnalytic decorator.
    
    The actual module names are returned. If you imported the module with a
    shorter alias use that instead.
    """

    pass



ALL_ANALYTICS = {}

ANALYTIC_DEBUGGING = False


