"""
------------------------------------------
liveRecord: cgm.tools
Author: David Bokser
email: dbokser@cgmonks.com
Website : http://www.cgmonks.com
------------------------------------------

================================================================
"""

from cgm.core.classes import DraggerContextFactory as cgmDrag
from cgm.core.lib import mouse_utils as MOUSE

import time
import maya.mel as mel
#from ctypes import windll, Structure, c_long, byref

import maya.cmds as mc

#========================================================================
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
#========================================================================

class LiveRecord(object):
    def __init__(self, onStart=None, onUpdate=None, onComplete=None, onExit=None, loopTime=False, debug=False):
        _str_func = 'LiveRecord._init_'

        # Callbacks
        self.onStart = onStart
        self.onUpdate = onUpdate
        self.onComplete = onComplete
        self.onExit = onExit

        self.isPressed = False
        self.isRecording = False
        self.loopTime = loopTime
        self.debug = debug

        self._recordButtons = [1]

        fps = mel.eval('currentTimeUnitToFPS')
        self.fixedDeltaTime = 1.0/fps

    def activate(self):
        _str_func = 'LiveRecord.activate'

        self.clickAction = cgmDrag.ClickAction(onPress=self.onPress, onRelease=self.onRelease, onFinalize=self.onFinalize, dropOnPress=False, dropOnRelease=False)
        mc.draggerContext(self.clickAction.name, edit=True, cursor='hand')

    def record(self):
        _str_func = 'LiveRecord.record'

        log.warning("Starting Record")

        self.isRecording = True

        if self.onStart != None:
            self.onStart()
            mc.refresh(force=True)

        fps = mel.eval('currentTimeUnitToFPS')
               
        startTime = time.time()
        prevTime = startTime

        currentFrame = mc.currentTime(q=True)

        while any([MOUSE.getMouseDown(x) for x in self._recordButtons]) and currentFrame < mc.playbackOptions(q=True, max=True):
            deltaTime = time.time() - prevTime
            waitTime = self.fixedDeltaTime - deltaTime
            time.sleep( max(waitTime, 0.0) )
            prevTime = time.time()
            self.update(self.fixedDeltaTime)

        print "Duration: %f" % (time.time() - startTime)
        
        mc.refresh()        

    def completeRecording(self):
        if self.onComplete != None:
            self.onComplete()

    def quit(self):
        _str_func = 'LiveRecord.quit'

        self.clickAction.dropTool()
        self.clickAction = None

    def onPress(self, clickDict):
        _str_func = 'LiveRecord.onPress'

        self._mb = mc.draggerContext( self.clickAction.name, q=True, button=True )

        self.isPressed = True
        self.isRecording = False

        # if mb == 1:
        #     self.onLeftButtonPress(clickDict)
        # else:
        #     self.onRightButtonPress(clickDict)

    def onRelease(self, clickDict):
        _str_func = 'LiveRecord.onRelease'

        if self.isRecording:
            self.isRecording = False
            self.completeRecording()

        self.isPressed = False

    def onFinalize(self):
        if self.onExit:
            self.onExit()

    def update(self, deltaTime = .04):
        _str_func = 'LiveRecord.update'

        try:
            if self.onUpdate != None:
                self.onUpdate(deltaTime)
        except Exception,err:
            log.error("|{0}| >> onUpdate function failed: | err: {1}".format(_str_func, err))