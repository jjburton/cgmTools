import os
#from cgm.lib.zoo.zooPy.path import Path
""" From http://stackoverflow.com/questions/1057431/loading-all-modules-in-a-folder-in-python"""

#Need to setup our cgm paths ===========================================================
#from cgm.lib.zoo.zooPy.path import Path, findFirstInEnv, findInPyPath
from cgm.core.cgmPy import path_Utils as cgmPath
import sys

def setupContributorPaths():
        try:
                thisFile = cgmPath.Path( __file__ )
                thisPath = thisFile.up().osPath()
        
                mayaSysPaths = sys.path
                #'lib/zoo/zooMel','lib/zoo/zooPy','lib/zoo/zooPyMaya','lib/bo','lib/ml':
                _l = ['mel','images','lib',os.path.join('lib','zoo'),
                      os.path.join('lib','zoo','zooPy'),
                      os.path.join('lib','zoo','zooPyMaya'),
                      os.path.join('lib','bo'),
                      os.path.join('lib','ml')]
                for folder in _l:
                        bufferFolderPath = os.path.join(thisPath,folder)
                        if bufferFolderPath not in mayaSysPaths:
                                try:
                                        sys.path.append("%s" %bufferFolderPath)
                                except:
                                        print ('%s Failed to append' %bufferFolderPath)
        except Exception,err:
                raise Exception,"setupContributorPaths FAILURE || {0}".format(err)
setupContributorPaths()
#=======================================================================================
