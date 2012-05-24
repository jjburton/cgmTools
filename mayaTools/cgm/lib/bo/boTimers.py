# Bo Timing Charts and other scripts uses some procedures that need to be timed, or automatic...

# This python script contains a timer function to enable threaded timing
# It also uses the executeDeferred procedure to make sure the mel doesn't return anything before the python script is done

# The timer also needs to be interruptable, so we use a boTimerActive variable
# to find out if the command should still be run once the timer ends


import maya.mel as mel
import maya.utils as utils
import maya.cmds as cmds
import sys
import string
import time
import threading

def boCmdEncode(cmd):
    return cmds.encodeString(cmd).replace("\\\"","\"")

def boTimerStart(dur, cmd):
    newBoTimer = boTimer(dur, cmd)
    newBoTimer.start()
    return newBoTimer
    
class boTimer(threading.Thread):
    def __init__(self, dur, cmd):
        self.dur = dur
        self.cmd = cmd
        self.cancel = 0
        threading.Thread.__init__(self)
    def run(self):
        time.sleep(self.dur)
        if self.cancel == 0:
            utils.executeDeferred(mel.eval, boCmdEncode(self.cmd))
    def kill(self):
        self.cancel = 1