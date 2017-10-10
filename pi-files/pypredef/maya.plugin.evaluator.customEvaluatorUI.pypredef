"""
Prototype platform to view the currently available custom evaluators and their
states.

Import via:

        from maya.plugin.evaluator.customEvaluatorUI import customEvaluatorUI, customEvaluatorDisplay
        
and then create the window with:

        evaluatorUI = customEvaluatorUI()

or visualize the custom evaluator clusters using display layers with:

        customEvaluatorDisplay('theEvaluatorName')
"""

def customEvaluatorUI():
    """
    Create a simple window showing the current status of the custom evaluators
    and providing a callback so that they can update the status when it changes.
    Layout is a row per evaluator with the following information:
    
            EvaluatorName   Ready []   Active []   <Evaluator-specific information>
    """

    pass


def customEvaluatorReadyStateChange(evaluatorName, newValue):
    """
    Callback when a checkbox is ticked to alter the ready state of a custom
    evaluator.
    """

    pass


def customEvaluatorDisplay(customEvaluatorName):
    """
    Take the named custom evaluator and put each of its evaluation clusters
    into a different display layer with a rotating colouring. (It's rotating
    because the display layers only have a small number of colours available
    whereas there could be a large number of clusters in the scene.)
    
    Although it only works for DAG nodes this provides a simple visual cue
    of how the custom evaluator has created its clusters.
    """

    pass


def customEvaluatorActiveStateChange(evaluatorName, newValue):
    """
    Callback when a checkbox is ticked to alter the active state of a custom
    evaluator.
    """

    pass



customEvaluatorScriptJob = None


