import os
#from cgm.lib.zoo.zooPy.path import Path
""" From http://stackoverflow.com/questions/1057431/loading-all-modules-in-a-folder-in-python"""

#Need to setup our cgm paths ===========================================================
from cgm.lib.zoo.zooPy.path import Path, findFirstInEnv, findInPyPath
import sys

def setupContributorPaths():
        thisFile = Path( __file__ )
        thisPath = thisFile.up()

        mayaSysPaths = sys.path

        for folder in 'mel','images','lib/zoo','lib/zoo/zooMel','lib/zoo/zooPy','lib/zoo/zooPyMaya','lib/bo','lib/ml':
                bufferFolderPath = thisPath / folder
                if bufferFolderPath not in mayaSysPaths:
                        try:
                                sys.path.append("%s" %bufferFolderPath)
                        except:
                                print ('%s Failed to append' %bufferFolderPath)
setupContributorPaths()
#=======================================================================================

def returnPyFilesFromFolder():
        import os
        thisFile = Path( __file__ )
        thisPath = thisFile.up()


        bufferList = find_files(thisPath, '*.py')
        returnList = []
        
        for file in bufferList:
                if '__' not in file:
                        splitBuffer = file.split('.')
                        returnList.append(splitBuffer[0])               
        if returnList:
                return returnList
        else:
                return False
        
def find_files(base, pattern):
        import fnmatch
        import os
        
        '''Return list of files matching pattern in base folder.'''
        """ http://stackoverflow.com/questions/4296138/use-wildcard-with-os-path-isfile"""
        return [n for n in fnmatch.filter(os.listdir(base), pattern) if
                os.path.isfile(os.path.join(base, n))]
        
        
__all__ = returnPyFilesFromFolder()