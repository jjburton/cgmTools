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
import time

from cgm.core.classes import GamePad
import cgm.core.lib.math_utils as MATH
import cgm.core.lib.camera_utils as CAM

class ControllerPuppet(object):
    def __init__(self, connectionDict):
        self.gamePad = GamePad.GamePad()
        self.gamePad.start_listening()

        self.gamePad.on_press_subscribe(self.onPress)

        self._isActive = False
        try:
            self.connectionDict = connectionDict
            self._parentCamera = None

            self.attachControllerToCurrentCam()

            self.fixedDeltaTime = .04

            self.start()
        finally:
            self.gamePad.stop_listening()

    def onPress(self, btn):
        if btn == 'Start':
            self._isActive = False

    def start(self):
        self._isActive = True
        while self._isActive:
            time.sleep(self.fixedDeltaTime)
            self.updatePuppet()
            mc.refresh()

    def updatePuppet(self):
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

    def stop(self):
        if self.gamePad:
            log.info("Stopping Listening to GamePad")
            self.gamePad.stop_listening()
            self.gamePad = None
            self._parentCamera = None

    def attachControllerToCurrentCam(self):
        currentCam = CAM.getCurrentCamera()
        if self._parentCamera != currentCam:
            self._parentCamera = currentCam
            mc.delete(mc.listRelatives(self.gamePad.controller_model, type='constraint'))
            mc.parentConstraint(currentCam, self.gamePad.controller_model, mo=False)
