'''
------------------------------------------
Red9 Studio Pack: Maya Pipeline Solutions
Author: Mark Jackson
email: rednineinfo@gmail.com

Red9 blog : http://red9-consultancy.blogspot.co.uk/
MarkJ blog: http://markj3d.blogspot.co.uk
------------------------------------------

This is the Audio library of utils used throughout the modules

================================================================

'''
import maya.cmds as cmds
import maya.mel as mel
import os

import Red9.startup.setup as r9Setup
import Red9_General as r9General

import wave
import contextlib
from ..packages.pydub.pydub import audio_segment

import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


def combineAudio():
    '''
    this is a logic wrapper over the main compile call in the AudioHandler
    I wanted to keep things simple in the base class
    '''
    prompt=False
    filepath = None
    audioHandler = AudioHandler()
    
    if not len(audioHandler.audioNodes)>1:
        raise ValueError('We need more than 1 audio node in order to compile')
        
    for audio in cmds.ls(type='audio'):
        audioNode = AudioNode(audio)
        if audioNode.isCompiled:
            result = cmds.confirmDialog(
                title='Compiled Audio',
                message='Compiled Audio Track already exists, over-right this instance?\n\nSoundNode : %s' % audioNode.audioNode,
                button=['OK', 'Generate New', 'Cancel'],
                defaultButton='OK',
                cancelButton='Cancel',
                dismissString='Cancel')
            if result == 'OK':
                filepath = audioNode.path
            elif result == 'Cancel':
                return
            else:
                prompt=True
            break
        
    scenepath = cmds.file(q=True, sn=True)
    if not filepath:
        if not scenepath or prompt:
            filepath = cmds.fileDialog2(fileFilter="Wav Files (*.wav *.wav);;", okc='Save')[0]
        else:
            filepath = '%s_combined.wav' % os.path.splitext(scenepath)[0]
            
    audioHandler.combineAudio(filepath)
              

## Audio Hanlders  -----------------------------------------------------
    
class AudioHandler(object):
    '''
    process on multiple audio nodes
    '''
    def __init__(self, audio=None):
        self._audioNodes = None
        if audio:
            self.audioNodes = audio
        else:
            if cmds.ls(sl=True,type='audio'):
                self.audioNodes = cmds.ls(sl=True,type='audio')
            else:
                self.audioNodes = cmds.ls(type='audio')

    @property
    def audioNodes(self):
        if not self._audioNodes:
            raise StandardError('No AudioNodes selected or given to process')
        return self._audioNodes
    
    @audioNodes.setter
    def audioNodes(self, val):
        print val, type(val)
        if not val:
            raise StandardError('No AudioNodes selected or given to process')
        if not type(val)==list:
            val = [val]
        self._audioNodes = [AudioNode(audio) for audio in val]
    
    @property
    def mayaNodes(self):
        return [audio.audioNode for audio in self.audioNodes]
    
    def getOverallRange(self, ms=False):
        '''
        return the overall frame range of the given audioNodes (min/max)
        '''
        maxV = self.audioNodes[0].startFrame  # initialize backwards
        minV = self.audioNodes[0].endFrame  # initialize backwards
        for a in self.audioNodes:
            audioOffset=a.startFrame
            audioEnd=a.endFrame  # why the hell does this always come back 1 frame over??
            if audioOffset<minV:
                minV=audioOffset
            if audioEnd>maxV:
                maxV=audioEnd
        #print 'min : ', minV
        #print 'max : ', maxV
        return (minV, maxV)
        
    def setTimelineToAudio(self, audioNodes=None):
        '''
        set the current TimeSlider to the extent of the given audioNodes
        '''
        frmrange=self.getOverallRange()
        cmds.playbackOptions(min=int(frmrange[0]), max=int(frmrange[1]))
        
    def muteSelected(self, state=True):
        for a in self.audioNodes:
            a.mute(state)
            
    def deleteSelected(self):
        for a in self.audioNodes:
            a.delete()
    
#     def delCombined(self):
#         audioNodes=cmds.ls(type='audio')
#         if not audioNodes:
#             return
#         for audio in audioNodes:
#             audioNode=AudioNode(audio)
#             if audioNode.path==filepath:
#                 if audioNode.isCompiled:
#                     log.info('Deleting currently compiled Audio Track')
#                     if audioNode in self.audioNodes:
#                         self.audioNodes.remove(audioNode)
#                     audioNode.delete()
#                     break
#                 else:
#                     raise IOError('Combined Audio path is already imported into Maya')
               
    def combineAudio(self, filepath):
        '''
        Combine audio tracks into a single wav file. This by-passes
        the issues with Maya not playblasting multip audio tracks.
        @param filepath: filepath to store the combined audioTrack
        TODO: Deal with offset start and end data + silence
        '''
        if not len(self.audioNodes)>1:
            raise ValueError('We need more than 1 audio node in order to compile')

        for audio in cmds.ls(type='audio'):
            audioNode=AudioNode(audio)
            if audioNode.path==filepath:
                if audioNode.isCompiled:
                    log.info('Deleting currently compiled Audio Track : %s' % audioNode.path)
                    if audioNode in self.audioNodes:
                        self.audioNodes.remove(audioNode)
                    audioNode.delete()
                    break
                else:
                    raise IOError('Combined Audio path is already imported into Maya')
            
        frmrange = self.getOverallRange()
        neg_adjustment=0
        if frmrange[0] < 0:
            neg_adjustment=frmrange[0]
            
        duration = ((frmrange[1] + abs(neg_adjustment)) / r9General.getCurrentFPS()) * 1000
        log.info('Audio BaseTrack duration = %f' % duration)
        baseTrack = audio_segment.AudioSegment.silent(duration)

        for audio in self.audioNodes:
            sound = audio_segment.AudioSegment.from_wav(audio.path)
            insertFrame = (audio.startFrame + abs(neg_adjustment))
            log.info('inserting sound : %s at %f adjusted to %f' % \
                     (audio.audioNode, audio.startFrame, insertFrame))
            baseTrack = baseTrack.overlay(sound, position=(insertFrame / r9General.getCurrentFPS()) * 1000)

        baseTrack.export(filepath, format="wav")
        compiled=AudioNode.importAndActivate(filepath)
        compiled.stampCompiled(self.mayaNodes)
        compiled.startFrame=neg_adjustment

        
        
class AudioNode(object):
    '''
    Single AudioNode handler for simple audio management object
    '''

    def __init__(self, audioNode=None):
        self.audioNode = audioNode
        if not self.audioNode:
            self.audioNode=self.audioSelected()
    
    def __repr__(self):
        if self.audioNode:
            return "%s(AudioNode InternalAudioNodes: '%s')" % (self.__class__, self.audioNode)
        else:
            return "%s(AudioNode NO AudioNodes: )" % self.__class__
    
    def __eq__(self, val):
        if isinstance(val, AudioNode):
            if self.audioNode==val.audioNode:
                return True
        elif cmds.nodeType(val)=='audio':
            if self.audioNode==val:
                return True
            
    def __ne__(self, val):
        return not self.__eq__(val)
    
    def audioSelected(self):
        selected = cmds.ls(sl=True,type='audio')
        if selected:
            return selected[0]
    
    @property
    def path(self):
        return cmds.getAttr('%s.filename' % self.audioNode)
    
    @property
    def sampleRate(self):
        '''
        sample rate in milliseconds
        '''
        return audio_segment.AudioSegment.from_wav(self.path).frame_rate
    
    @property
    def startFrame(self):
        return cmds.getAttr('%s.offset' % self.audioNode)
    
    @startFrame.setter
    def startFrame(self, val):
        cmds.setAttr('%s.offset' % self.audioNode, val)
        
    @property
    def endFrame(self):
        '''
        Note in batch mode we calculate via the Wav duration
        NOT the Maya audioNode length as it's invalid under batch mode!
        '''
        if not cmds.about(batch=True):
            return cmds.getAttr('%s.endFrame' % self.audioNode)  # why the hell does this always come back 1 frame over??
        else:
            return self.getLengthFromWav() + self.startFrame
        
    @property
    def startTime(self):
        '''
        this is in milliseconds
        '''
        return (self.startFrame / r9General.getCurrentFPS()) * 1000
    
    @property
    def endTime(self):
        '''
        this is in milliseconds
        '''
        return (self.endFrame / r9General.getCurrentFPS()) * 1000
           
    def delete(self):
        cmds.delete(self.audioNode)
            
    def offsetTime(self, offset):
        if r9Setup.mayaVersion() == 2011:
            #Autodesk fucked up in 2011 and we need to manage both these attrs
            cmds.setAttr('%s.offset' % self.audioNode, self.startFrame + offset)
            cmds.setAttr('%s.endFrame' % self.audioNode, self.length + offset)
        else:
            cmds.setAttr('%s.offset' % self.audioNode, self.startFrame + offset)
    
    @staticmethod
    def importAndActivate(path):
        a=cmds.ls(type='audio')
        cmds.file(path, i=True, type='audio', options='o=0')
        b=cmds.ls(type='audio')
        if not a == b:
            audio = AudioNode(list(set(a) ^ set(b))[0])
        else:
            matchingnode = [audio for audio in a if cmds.getAttr('%s.filename' % audio) == path]
            if matchingnode:
                audio = AudioNode(matchingnode[0])
            else:
                return
        audio.setActive()
        return audio
        
    def setActive(self):
        '''
        Set sound node as active on the timeSlider
        '''
        gPlayBackSlider = mel.eval("string $temp=$gPlayBackSlider")
        cmds.timeControl(gPlayBackSlider, e=True, ds=1, sound=self.audioNode)

    def getLengthFromWav(self):
        '''
        This uses the wav itself bypassing the Maya handling, why?
        In maya.standalone the audio isn't loaded correctly and always is of length 1!
        '''
        with contextlib.closing(wave.open(self.path,'r')) as f:
            frames=f.getnframes()
            rate=f.getframerate()
            duration=frames/float(rate)
            return (duration) * r9General.getCurrentFPS()
                    
    def setTimeline(self):
        cmds.playbackOptions(min=int(self.startFrame), max=int(self.endFrame))

    def mute(self, state=True):
        cmds.setAttr('%s.mute' % self.audioNode, state)

    def openAudioPath(self):
        path=self.path
        if path and os.path.exists(path):
            r9General.os_OpenFileDirectory(path)
            
    @property
    def isCompiled(self):
        '''
        return if the audioNode in Maya was generated via the compileAudio
        call in the AudioHandler.
        '''
        if cmds.attributeQuery('compiledAudio', exists=True, node=self.audioNode):
            return True

    def stampCompiled(self, audioNodes):
        '''
        Used by the compiler - stamp the audioNodes from which this audio
        track was compiled from
        '''
        cmds.addAttr(self.audioNode, longName='compiledAudio', dt='string')
        cmds.setAttr('%s.compiledAudio' % self.audioNode, ','.join(audioNodes), type="string")
                
