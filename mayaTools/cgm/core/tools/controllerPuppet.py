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

from cgm.core.classes import GamePad
import cgm.core.lib.math_utils as MATH
import cgm.core.lib.camera_utils as CAM
from cgm.core import cgm_General as cgmGen

import time
import threading 
import ctypes
import copy
import pprint

class RecordingThread(threading.Thread): 
    def __init__(self, gamePad, startFrame = 0, deltaTime = .04): 
        threading.Thread.__init__(self)
        self.dataDict = {}
        self.gamePad = gamePad
        self.deltaTime = deltaTime

        self.currentFrame = startFrame
              
    def run(self): 
  
        # target function of the thread class 
        try: 
            while True:
                self.dataDict[self.currentFrame] = self.gamePad.get_state_dict()
                time.sleep(self.deltaTime)
                self.currentFrame = self.currentFrame + 1
        finally: 
            print('stopped recording')
           
    def get_id(self): 
  
        # returns id of the respective thread 
        if hasattr(self, '_thread_id'): 
            return self._thread_id 
        for id, thread in threading._active.items(): 
            if thread is self: 
                return id
   
    def raise_exception(self): 
        thread_id = self.get_id() 
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 
              ctypes.py_object(SystemExit)) 
        if res > 1: 
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0) 
            print('Exception raise failure')

class ControllerPuppet(object):
    def __init__(self, mappingList, onEnded = None, onActivate = None, onDeactivate = None):
        self.gamePad = GamePad.GamePad(updateVisual=False)
        self.gamePad.start_listening()

        self.gamePad.on_press_subscribe(self.onPress)

        self._isActive = False
        self._isRecording = False

        self.mappingList = mappingList
        self.currentMapIdx = 0
        self.connectionDict = { 'name':'Default',
                                'RStickHorizontal':{},
                                'RStickVertical':{},
                                'LStickHorizontal':{},
                                'LStickVertical':{},
                                'RTrigger':{},
                                'LTrigger':{} }
        if len(self.mappingList) > 0:
            self.connectionDict = self.mappingList[self.currentMapIdx]


        self.playbackMultiplierList = [.1, .25, .5, .75, 1.0, 1.5, 2.0]
        self.playbackMultIdx = 4
        self.playbackMultiplier = self.playbackMultiplierList[self.playbackMultIdx]

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

        self._updatePuppet = True

        self._recordingPressed = False
        self._startPressed = False

        self._recordingThread = None
        self._recordedData = {}

        self._upPushed = False
        self._downPushed = False
        self._leftPushed = False
        self._rightPushed = False

    def onPress(self, btn):
        _str_func = 'ControllerPuppet.onPress'

        #log.info('{0} >> Button pressed: {1}'.format(_str_func, btn))

        if btn == 'Start':
            self._startPressed = True
        elif btn == 'A':
            #log.info('{0} >> Pressed A'.format(_str_func))
            self._recordingPressed = True

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

                self.gamePad.update_controller_model()
                
                if self._updatePuppet:
                    self.updatePuppet(setKey=self._isRecording)

                if self._recordingPressed:
                    self._recordingPressed = False

                    if not self._isRecording:
                        self._startFrame = int(mc.currentTime(q=True))
                        self._startTime = time.time()
                        self._recordingThread = RecordingThread( self.gamePad, startFrame = self._startFrame, deltaTime = self.fixedDeltaTime ) 
                        self._recordingThread.start() 
                        log.info('{0} >> Setting start values for recording'.format(_str_func))
                        self.displayMessage('Starting Recording')
                    else:
                        self.stopRecordingThread()
                        self.displayMessage('Stopping Recording')

                    self._isRecording = not self._isRecording

                if self._isRecording:
                    wantedFrame = self._startFrame + int( (time.time() - self._startTime) / self.fixedDeltaTime )
                    #log.info('{0} >> Wanted frame : {1}'.format(_str_func, wantedFrame))
                    if wantedFrame != int(mc.currentTime(q=True)):
                        #log.info('{0} >> Changing frame : {1}'.format(_str_func, wantedFrame))
                        mc.currentTime( wantedFrame )

                    if wantedFrame >= mc.playbackOptions(q=True, max=True):
                        self._isRecording = False
                        self.stopRecordingThread()
                        self.displayMessage('Stopping Recording')
                        #self._isActive = False

                if self._startPressed:
                    self._startPressed = False
                    self._updatePuppet = not self._updatePuppet
                    self.displayMessage('Updating Puppet : {0}'.format(self._updatePuppet))

                if self.gamePad.right_bumper:
                    nextFrame = int(mc.currentTime(q=True)+1)
                    if nextFrame > mc.playbackOptions(q=True, max=True):
                        nextFrame = mc.playbackOptions(q=True, min=True)

                    mc.currentTime( nextFrame )

                if self.gamePad.left_bumper:
                    nextFrame = int(mc.currentTime(q=True)-1)
                    if nextFrame < mc.playbackOptions(q=True, min=True):
                        nextFrame = mc.playbackOptions(q=True, max=True)
                    mc.currentTime( nextFrame )

                # Process Mapping Change
                if self.gamePad.thumbpad_y > 0.5 and not self._upPushed and len(self.mappingList) > 0:
                    self.currentMapIdx = (self.currentMapIdx + 1) % len(self.mappingList)
                    self.connectionDict = self.mappingList[self.currentMapIdx]
                    log.info('Current Mapping : {0}'.format(self.connectionDict['name']))
                    self.displayMessage('Current Mapping : {0}'.format(self.connectionDict['name']))
                self._upPushed = self.gamePad.thumbpad_y > 0.5

                if self.gamePad.thumbpad_y < -0.5 and not self._downPushed and len(self.mappingList) > 0:
                    self.currentMapIdx = (self.currentMapIdx - 1) if self.currentMapIdx > 0 else (len(self.mappingList)-1)
                    self.connectionDict = self.mappingList[self.currentMapIdx]
                    log.info('Current Mapping : {0}'.format(self.connectionDict['name']))
                    self.displayMessage('Current Mapping : {0}'.format(self.connectionDict['name']))
                self._downPushed = self.gamePad.thumbpad_y < -0.5

                # Process Speed Change
                if self.gamePad.thumbpad_x > 0.5 and not self._rightPushed:
                    self.playbackMultIdx = (self.playbackMultIdx + 1) % len(self.playbackMultiplierList)
                    self.playbackMultiplier = self.playbackMultiplierList[self.playbackMultIdx]
                    log.info('Playback multiplier : {0}'.format(self.playbackMultiplier))
                    self.displayMessage('Playback multiplier : {0}'.format(self.playbackMultiplier))
                self._rightPushed = self.gamePad.thumbpad_x > 0.5

                if self.gamePad.thumbpad_x < -0.5 and not self._leftPushed:
                    self.playbackMultIdx = (self.playbackMultIdx - 1) if self.playbackMultIdx > 0 else (len(self.playbackMultiplierList)-1)
                    self.playbackMultiplier = self.playbackMultiplierList[self.playbackMultIdx]
                    log.info('Playback multiplier : {0}'.format(self.playbackMultiplier))
                    self.displayMessage('Playback multiplier : {0}'.format(self.playbackMultiplier))
                self._leftPushed = self.gamePad.thumbpad_x < -0.5

                if self.gamePad.button_select:
                    self.stop()
                
                mc.refresh()

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

    def stopRecordingThread(self):
        if self._recordingThread != None:
            self._recordedData = copy.copy(self._recordingThread.dataDict)
            self._recordingThread.raise_exception()
            pprint.pprint(self._recordedData)

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

    def displayMessage(self, msg):
        if self.gamePad:
            mc.select(self.gamePad.controller_model + "|PositionNode")
            mc.headsUpMessage( msg, verticalOffset=-250, selection=True, t=2 )
            mc.select(cl=True)

    def getMapping(self):
        return self.connectionDict['name']

    def attachControllerToCurrentCam(self):
        currentCam = CAM.getCurrentCamera()
        if self._parentCamera != currentCam:
            self._parentCamera = currentCam
            mc.delete(mc.listRelatives(self.gamePad.controller_model, type='constraint'))
            mc.parentConstraint(currentCam, self.gamePad.controller_model, mo=False)
