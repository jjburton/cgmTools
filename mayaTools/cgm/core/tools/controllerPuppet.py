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
import cgm.core.lib.attribute_utils as ATTR
from cgm.core import cgm_General as cgmGen
from cgm.core.lib import locator_utils as LOC

import time
import threading 
import ctypes
import copy
import pprint

# Audio
import pyaudio
import wave

class RecordingThread(threading.Thread): 
    def __init__(self, gamePad, startFrame = 0, deltaTime = .04, audioFile=None, audioStartFrame = 0, audioSpeed = 1.0): 
        threading.Thread.__init__(self)
        self.dataDict = {}
        self.gamePad = gamePad
        self.deltaTime = deltaTime

        self.currentFrame = startFrame
        
        self.audioFile = audioFile
        self._audioActive = False
        self._audioStartFrame = audioStartFrame
        self._audioSpeed = audioSpeed
        self.__audioData = {}
        
    def run(self): 
  
        # target function of the thread class 
        try: 
            while True:
                self.dataDict[self.currentFrame] = self.gamePad.get_state_dict()
                time.sleep(self.deltaTime)
                self.currentFrame = self.currentFrame + 1
                
                if self._audioStartFrame >= self.currentFrame:
                    offset = (self.currentFrame - self._audioStartFrame)
                    self.__audioData = processAudio(self.audioFile, offset, self._audioSpeed, self.deltaTime)
        finally: 
            if self.__audioData.get('stream', False):
                stopAudio(self.__audioData)
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
        self._keyList = []

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
            for key in self.connectionDict:
                if isinstance(self.connectionDict[key], dict):
                    self._keyList = self._keyList + self.connectionDict[key].keys()

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
        
        self._playAudioPressed = False

        self._recordingThread = None
        self._recordedData = {}

        self._upPushed = False
        self._downPushed = False
        self._leftPushed = False
        self._rightPushed = False
        
        self.__audioData = {}

    def onPress(self, btn):
        _str_func = 'ControllerPuppet.onPress'

        #log.info('{0} >> Button pressed: {1}'.format(_str_func, btn))

        if btn == 'Start':
            self._startPressed = True
        elif btn == 'A':
            #log.info('{0} >> Pressed A'.format(_str_func))
            self._recordingPressed = True
        elif btn == 'B':
            self._playAudioPressed = True

    def start(self):
        _str_func = 'ControllerPuppet.start'

        self._isActive = True

        _ak = mc.autoKeyframe(q=True, state=True)

        try:
            log.info('{0} >> Activating'.format(_str_func))
            mc.autoKeyframe(state=False)

            if len(self.onActivate) > 0:
                for func in self.onActivate:
                    func()

            while self._isActive and self.gamePad:              
                time.sleep(self.fixedDeltaTime)

                self.gamePad.update_controller_model()
                
                if self._updatePuppet:
                    self.updatePuppet()

                if self._recordingPressed:
                    self._recordingPressed = False

                    if self._isRecording:
                        self.stopRecording()
                    else:
                        self.startRecording()

                if self._isRecording:
                    wantedFrame = self._startFrame + int( (time.time() - self._startTime) / (self.fixedDeltaTime / self.playbackMultiplier)  )
                    #log.info('{0} >> Wanted frame : {1}'.format(_str_func, wantedFrame))
                    if wantedFrame != int(mc.currentTime(q=True)):
                        #log.info('{0} >> Changing frame : {1}'.format(_str_func, wantedFrame))
                        mc.currentTime( wantedFrame )

                    if wantedFrame >= mc.playbackOptions(q=True, max=True):
                        self.stopRecording()
                        self.displayMessage('Stopping Recording')
                        #self._isActive = False
                else:
                    if self._startPressed:
                        self._startPressed = False
                        self._updatePuppet = not self._updatePuppet
                        self.displayMessage('Updating Puppet : {0}'.format(self._updatePuppet))
                    
                    if self._playAudioPressed:
                        self._playAudioPressed = False
                        
                        if self.__audioData.get('stream', False):
                            self.displayMessage('Stopping Audio')
                            stopAudio(self.__audioData)
                            self.__audioData = {}       
                        else:
                            self.displayMessage('Playing Audio')
                            
                            # figure out audio
                            audioNodes = mc.ls(type='audio')
                            audioFile = None
                            audioStartFrame = 0
                            offset = 0
                            currentFrame = mc.currentTime(q=True)
                            
                            if len(audioNodes) > 0:
                                audioFile = mc.getAttr( '{0}.filename'.format(audioNodes[0]))
                                audioStartFrame = mc.getAttr( '{0}.offset'.format(audioNodes[0]))
                            if currentFrame >= audioStartFrame:
                                offset = (currentFrame - audioStartFrame)                        
                            
                            if audioFile:
                                self.__audioData = processAudio(audioFile, offset, self.playbackMultiplier, self.fixedDeltaTime / self.playbackMultiplier)

                    
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
                        self.setMapping( (self.currentMapIdx + 1) % len(self.mappingList) )
                    self._upPushed = self.gamePad.thumbpad_y > 0.5

                    if self.gamePad.thumbpad_y < -0.5 and not self._downPushed and len(self.mappingList) > 0:
                        self.setMapping( (self.currentMapIdx - 1) if self.currentMapIdx > 0 else (len(self.mappingList)-1) )
                    self._downPushed = self.gamePad.thumbpad_y < -0.5

                    # Process Speed Change
                    if self.gamePad.thumbpad_x > 0.5 and not self._rightPushed:
                        self.setRecordSpeed( (self.playbackMultIdx + 1) % len(self.playbackMultiplierList) )
                    self._rightPushed = self.gamePad.thumbpad_x > 0.5

                    if self.gamePad.thumbpad_x < -0.5 and not self._leftPushed:
                        self.setRecordSpeed( (self.playbackMultIdx - 1) if self.playbackMultIdx > 0 else (len(self.playbackMultiplierList)-1) )
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
            mc.autoKeyframe(state=_ak)
            log.info("|{0}| >> Ending start".format(_str_func))

    def setMapping(self, idx):
        self._keyList = []
        self.currentMapIdx = idx
        self.connectionDict = self.mappingList[self.currentMapIdx]
        for key in self.connectionDict:
            if isinstance(self.connectionDict[key], dict):
                self._keyList = self._keyList + self.connectionDict[key].keys()
        log.info('Current Mapping : {0}'.format(self.connectionDict['name']))
        self.displayMessage('Current Mapping : {0}'.format(self.connectionDict['name']))

    def setRecordSpeed(self, idx):
        self.playbackMultIdx = idx
        self.playbackMultiplier = self.playbackMultiplierList[self.playbackMultIdx]
        log.info('Playback multiplier : {0}'.format(self.playbackMultiplier))
        self.displayMessage('Playback multiplier : {0}'.format(self.playbackMultiplier))

    def startRecording(self):
        _str_func = 'ControllerPuppet.startRecording'

        if self._isRecording:
            return

        if self.__audioData.get('stream', False):
            #self.displayMessage('Stopping Audio')
            stopAudio(self.__audioData)
            self.__audioData = {}

        self._keyHolderDict = {}

        for k in self._keyList:
            objName, attr = k.split('.')
            if not objName in self._keyHolderDict:
                self._keyHolderDict[objName] = LOC.create(name='keyHolder_{0}'.format(objName))

            ATTR.copy_to( objName, attr, self._keyHolderDict[objName], inConnection=True, keepSourceConnections=False)


        # figure out audio
        audioNodes = mc.ls(type='audio')
        audioFile = None
        audioStartFrame = 0
        if len(audioNodes) > 0:
            audioFile = mc.getAttr( '{0}.filename'.format(audioNodes[0]))
            audioStartFrame = mc.getAttr( '{0}.offset'.format(audioNodes[0]))

        self._startFrame = int(mc.currentTime(q=True))
        self._startTime = time.time()
        self._recordingThread = RecordingThread( self.gamePad, startFrame = self._startFrame, deltaTime = self.fixedDeltaTime / self.playbackMultiplier, audioFile = audioFile, audioStartFrame = audioStartFrame, audioSpeed=self.playbackMultiplier ) 
        self._recordingThread.start() 
        
        #self._hasSavedKeys = mc.cutKey(self._keyList, t=(self._startFrame,))
        log.info('{0} >> Setting start values for recording'.format(_str_func))
        self.displayMessage('Starting Recording')

        self._isRecording = True

    def stopRecording(self):
        _str_func = 'ControllerPuppet.stopRecording'
        
        if not self._isRecording:
            return

        self._endFrame = int(mc.currentTime(q=True))

        if self._recordingThread != None:
            self._recordedData = copy.copy(self._recordingThread.dataDict)
            self._recordingThread.raise_exception()
            self.keyFromData(self._recordedData)        

        for k in self._keyList:
            objName, attr = k.split('.')
            first = mc.findKeyframe( '{0}.{1}'.format( self._keyHolderDict[objName], attr ), which='first' )
            if first < self._startFrame: 
                if mc.cutKey('{0}.{1}'.format( self._keyHolderDict[objName],attr ), t=(first, self._startFrame) ):
                    mc.pasteKey( objName, o='replace' )
            
            last = mc.findKeyframe( '{0}.{1}'.format( self._keyHolderDict[objName], attr ), which='last' )
            if last > self._endFrame: 
                if mc.cutKey('{0}.{1}'.format( self._keyHolderDict[objName],attr), t=(self._endFrame, last) ):
                    mc.pasteKey( objName, o='replace' )

        mc.delete( [self._keyHolderDict[x] for x in self._keyHolderDict.keys() ] )
        self._keyHolderDict = {}

        self.displayMessage('Stopping Recording')

        self._isRecording = False

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
    
    def keyFromData(self, dataDict):
        #mc.refresh(su=True)

        keyList = dataDict.keys()
        keyList.sort()

        prevDataDict = {}

        for frame in keyList:
            connectionList = [  ['LStickVertical', dataDict[frame]['left_stick_y'], -1, 1],
                                ['LStickHorizontal', dataDict[frame]['left_stick_x'], -1, 1],
                                ['RStickVertical', dataDict[frame]['right_stick_y'], -1, 1],
                                ['RStickHorizontal', dataDict[frame]['right_stick_x'], -1, 1],
                                ['RTrigger', dataDict[frame]['right_trigger'], 0,1],
                                ['LTrigger', dataDict[frame]['left_trigger'], 0, 1] ]

            for con in connectionList:
                for key in self.connectionDict[con[0]]:
                    p = (con[1] - con[2]) / (con[3]-con[2])
                    d = self.connectionDict[con[0]][key]
                    v = MATH.Lerp(d['min'], d['max'], p)
                    v = MATH.Lerp(prevDataDict[key] if key in prevDataDict else v, v, self.fixedDeltaTime * d['damp'])
                    prevDataDict[key] = v
                    mc.setKeyframe(key, v=v, t=frame)

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

def stopAudio(audioData = {}):
    # stop stream
    if audioData.get('stream', False):
        audioData['stream'].stop_stream()
        audioData['stream'].close()
    if audioData.get('wf', False):
        audioData['wf'].close()
    
    # close PyAudio
    if audioData.get('p', False):
        audioData['p'].terminate()
    
def processAudio(audioFile, offset, audioSpeed, deltaTime = .04):
    if not audioFile:
        return {}
    
    audioData = {}
    
    chunk = 1024
    
    audioData['wf'] = wave.open(audioFile, 'rb')
    
    # instantiate PyAudio
    audioData['p'] = pyaudio.PyAudio()
    
    params = audioData['wf'].getparams()
    
    audioLength = float(params[3]) / params[2]
    totalChunks = params[3] / 1024        
    frameChunk = deltaTime * params[2]
    
    # remove chunk if we're starting from somewhere in the middle of the clip
    audioData['wf'].readframes( int(frameChunk * offset) )
    
    # define callback
    def streamCallback(in_data, frame_count, time_info, status):
        data = audioData['wf'].readframes(frame_count)
        return (data, pyaudio.paContinue)        
    
    # open stream using callback
    audioData['stream'] = audioData['p'].open(format=audioData['p'].get_format_from_width(audioData['wf'].getsampwidth()),
                    channels=audioData['wf'].getnchannels(),
                    rate=int(audioData['wf'].getframerate() * audioSpeed),
                    output=True,
                    stream_callback=streamCallback)
       
    return audioData
