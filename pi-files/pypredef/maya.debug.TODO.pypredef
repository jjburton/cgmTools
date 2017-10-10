"""
ile ToDo.py
A utility to help identify areas of the code that need work.

This is just a syntactically similar interface of the TODO macro
in C++ code that uses the toDo command to register hits of
incomplete code and mark areas of Python source for extraction
to the code health summary.

The strings inside the TODO call should all be literals so that
they can be easily extracted to the code health web page. You
can use either single or double quotes. It's also acceptable to
use None for the jiraEntry argument.

This should only be called from tests as we obviously don't want
to pollute customer-visible files with this sort of thing. If you
must though you can use the #ifdef MAYA_DEV_BUILD to ensure that
it gets filtered out of the customer version


Example usage:

    from maya.debug.TODO import *
    def myIncompleteFunction(self, case):
        if case == 0:
            handleCase0()
        elif case == 1:
            handleCase1()
        else:
            TODO( 'Finish', 'Unhandled case value %s' % case, 'MAYA-99999' )
            # Currently only cases 0 and 1 are handled but there are
            # situations in which values of 2 or 3 can be passed in. Those
            # represent edge cases at the moment and they will be handled
            # once our customer feedback lets us know exactly what we
            # should be doing in those situations.

\sa ToDo.h
\sa TODO.mel
"""

def TODO(toDoType, description, jiraEntry):
    """
    Register a "TODO" with the system. This is used to track when running code
    hits an area that has work to be done. This can help track down bugs,
    inefficiencies, and just generally make incomplete work more visible.
    
        toDoType
            What type of ToDo is it. Entries are grouped by this
            value. There are some hardcoded values to choose from, or you can use
            your own.
                REFACTOR    : Code works but needs some sort of refactoring.
                HACK        : Ugly shortcuts were taken to get something working quickly.
                FINISH      : Code doesn't handle all cases yet.
                BUG         : There is a known problem with the code.
                PERFORMANCE : The code could be made faster or more scalable.
    
        description
            Short description of what work needs to be done to remedy the problem.
    
        jiraEntry
            Link to the name of a JIRA entry referencing this code. None if
            there is no associated JIRA entry, but there really should be.
    """

    pass



