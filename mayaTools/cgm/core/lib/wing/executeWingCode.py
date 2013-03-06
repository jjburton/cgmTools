"""
executeWingCode.py
Eric Pavey - 2011-03-23
Module that Maya calls to when Wing pings it through a socket, telling Maya
to execute the commands in the temp file as either Python or mel code.
"""
import __main__
import os

import maya.OpenMaya as om

def main(codeType):
    """
    Evaluate the temp file on disk, made by Wing, in Maya.

    codeType : string : Supports either 'python' or 'mel'
    """
    tempFile = os.path.join(os.environ['TEMP'], 'wingData.txt').replace("\\", "/")
    if os.access(tempFile , os.F_OK):
        # Print the lines from the file in Maya:
        with open(tempFile, "r") as f:
            for line in f.readlines():
                print line.rstrip()
        print "\n",

        if codeType == "python":
            # execute the file contents in Maya:
            with open(tempFile , "r") as f:
                exec(f, __main__.__dict__, __main__.__dict__)
        elif codeType == "mel":
            melCmd = 'source "%s"'%tempFile
            # This causes the "// Result: " line to show up in the Script Editor:
            om.MGlobal.executeCommand(melCmd, True, True)
    else:
        print "No Wing-generated temp file exists: " + tempFile