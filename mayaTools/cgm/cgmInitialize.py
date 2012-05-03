import os
import re
import sys

"""	
else:
	print ('You need to get the zooPy directory in one of your scripts paths')
"""

from cgm.lib.zoo.zooPy.path import Path, findFirstInEnv, findInPyPath


def setupContributorPaths():
        thisFile = Path( __file__ )
        thisPath = thisFile.up()

        mayaSysPaths = sys.path

        for folder in 'lib/zoo','lib/zoo/zooMel','lib/zoo/zooPy','lib/zoo/zooPyMaya','lib/bo','lib/ml':
                bufferFolderPath = thisPath / folder

                if bufferFolderPath not in mayaSysPaths:
                        try:
                                sys.path.append("%s" %bufferFolderPath)
                        except:
                                print ('%s Failed to append' %bufferFolderPath)


def devPaths():
        mayaSysPaths = sys.path

        devPaths = ['D:/repos/cgmTools/mayaTools']

        for dirPath in devPaths:
                if dirPath not in mayaSysPaths:
                        try:
                                sys.path.insert(0,dirPath)
                        except:
                                print ('%s Failed to append' %dirPath)


def returnPyFilesFromFolder():
        import os
        thisFile = Path( __file__ )
        thisPath = thisFile.up()


        bufferList = find_files(thisPath, '*.py')
        returnList = []
        
        for file in bufferList:
                print file
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
