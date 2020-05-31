"""
------------------------------------------
controllerPuppet: cgm.core.tools
Author: David Bokser
email: dbokser@cgmonks.com

Website : http://www.cgmonks.com
------------------------------------------
UI for controller puppet
================================================================
"""
# From Python =============================================================
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

import maya.cmds as mc
import maya.mel as mel
import time

from cgm.core.classes import GamePad
import cgm.core.lib.math_utils as MATH
import cgm.core.lib.camera_utils as CAM
from cgm.core import cgm_General as cgmGen

class ControllerPuppet(object):
    def __init__(self, connectionDict, onEnded = None, onActivate = None, onDeactivate = None):
        self.gamePad = GamePad.GamePad(updateVisual=False)
        self.gamePad.start_listening()

        self.gamePad.on_press_subscribe(self.onPress)

        self._isActive = False
        self._isRecording = False

        self.connectionDict = connectionDict
        self._parentCamera = None

        self.attachControllerToCurrentCam()

        fps = mel.eval('currentTimeUnitToFPS')
        self.fixedDeltaTime = 1.0/fps

        self.onEnded = []
        if onEnded != None:
            self.onEnded.append(onEnded)

        self.onActivate = []
        if onActivate != None:
            self.onActivate.append(onActivate)

        self.onDeactivate = []
        if onDeactivate != None:
            self.onDeactivate.append(onDeactivate)

        self._startFrame = mc.currentTime(q=True)
        self._startTime = time.time()

        self._recordingPressed = False

    def onPress(self, btn):
        _str_func = 'ControllerPuppet.onPress'

        #log.info('{0} >> Button pressed: {1}'.format(_str_func, btn))

        if btn == 'Start':
            if not self._isActive:
                self.start()
        elif btn == 'A':
            #log.info('{0} >> Pressed A'.format(_str_func))
            self._recordingPressed = True
        #mc.refresh()

    def start(self):
        _str_func = 'ControllerPuppet.start'

        self._isActive = True
        try:
            log.info('{0} >> Activating'.format(_str_func))
            if len(self.onActivate) > 0:
                for func in self.onActivate:
                    func()

            while self._isActive and self.gamePad:
                time.sleep(self.fixedDeltaTime)
                
                self.updatePuppet(setKey=self._isRecording)

                if self._recordingPressed:
                    self._recordingPressed = False

                    if not self._isRecording:
                       self._startFrame = int(mc.currentTime(q=True))
                       self._startTime = time.time()
                       log.info('{0} >> Setting start values for recording'.format(_str_func))
                    self._isRecording = not self._isRecording

                if self._isRecording:
                    wantedFrame = self._startFrame + int( (time.time() - self._startTime) / self.fixedDeltaTime )
                    #log.info('{0} >> Wanted frame : {1}'.format(_str_func, wantedFrame))
                    if wantedFrame != int(mc.currentTime(q=True)):
                        #log.info('{0} >> Changing frame : {1}'.format(_str_func, wantedFrame))
                        mc.currentTime( wantedFrame )
                    if wantedFrame >= mc.playbackOptions(q=True, max=True):
                        self._isRecording = False
                        #self._isActive = False

                if self.gamePad:
                    self.gamePad.update_controller_model()

                mc.refresh()
                if self.gamePad.button_start:
                    self._isActive = False
                    break

                if self.gamePad.button_select:
                    self.stop()

            log.info('{0} >> Deactivating'.format(_str_func))
            if len(self.onDeactivate) > 0:
                for func in self.onDeactivate:
                    func()
        except Exception,err:
            log.error("|{0}| >> function failed: | err: {1}".format(_str_func, err))
            cgmGen.cgmException(Exception,err)
            self.stop()
        finally:
            log.info("|{0}| >> Ending start".format(_str_func))

    def updatePuppet(self, setKey=False):
        _str_func = 'ControllerPuppet.updatePuppet'

        if not self.gamePad:
            log.warning("{0} >> No GamePad found. Can't update puppet".format(_str_func))
            return

        connectionList = [  ['LStickVertical', self.gamePad.left_stick_y, -1, 1],
                            ['LStickHorizontal', self.gamePad.left_stick_x, -1, 1],
                            ['RStickVertical', self.gamePad.right_stick_y, -1, 1],
                            ['RStickHorizontal', self.gamePad.right_stick_x, -1, 1],
                            ['RTrigger', self.gamePad.right_trigger, 0,1],
                            ['LTrigger', self.gamePad.left_trigger, 0, 1] ]

        for con in connectionList:
            for key in self.connectionDict[con[0]]:
                p = (con[1] - con[2]) / (con[3]-con[2])
                d = self.connectionDict[con[0]][key]
                v = MATH.Lerp(d['min'], d['max'], p)
                v = MATH.Lerp(mc.getAttr(key), v, self.fixedDeltaTime * d['damp'])
                mc.setAttr(key, v)
                if setKey:
                    mc.setKeyframe(key)

    def stop(self):
        _str_func = 'ControllerPuppet.stop'

        if self.gamePad:
            log.info("{0} >> Stopping Listening to GamePad".format(_str_func))
            self.gamePad.stop_listening()
            self.gamePad = None
            self._parentCamera = None

        if len(self.onEnded) > 0:
            for func in self.onEnded:
                func()

    def attachControllerToCurrentCam(self):
        currentCam = CAM.getCurrentCamera()
        if self._parentCamera != currentCam:
            self._parentCamera = currentCam
            mc.delete(mc.listRelatives(self.gamePad.controller_model, type='constraint'))
            mc.parentConstraint(currentCam, self.gamePad.controller_model, mo=False)
