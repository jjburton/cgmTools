"""
Test the comparitive performance between regular Maya transforms and the
leanTransformTest node to see what overhead the API brings.
"""

from maya.debug.playbackModeManager import playbackModeManager
from maya.debug.emModeManager import emModeManager

def create_nodes(node_count, node_type):
    """
    Create a given number of nodes of the given type and return the
    list of nodes created.
    """

    pass


def measureMPxTransformPerformance():
    """
    Run two performance tests with 1000 transforms keyed randomly over 1000 frames
    for both the native Ttransform and the API leanTransformTest. Report the timing
    for playback of the two, and dump profile files for both for manual inspection.
    """

    pass


def animate(node_list, keyframe_count):
    """
    Animate the TRS attributes of every node in the list with random
    values for each frame from 1 to "keyframe_count"
    """

    pass



PLUGIN_PROFILE = 'MPxTransform_profile.txt'

KEY_COUNT = 500

NATIVE_PROFILE = 'Ttransform_profile.txt'

NODE_NAME = 'leanTransformTest'

PLUGIN = NODE_NAME

