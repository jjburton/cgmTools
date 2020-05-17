from cgm.core.classes import DraggerContextFactory as cgmDrag
from cgm.core.lib import locator_utils as LOC
from cgm.core.lib import math_utils as MATHUTILS
from cgm.core import cgm_General as cgmGEN
from cgm.core.lib import camera_utils as CAM
from cgm.core.lib import mouse_utils as MOUSE
from cgm.core.lib import euclid as EUCLID
from cgm.core.cgmPy import validateArgs as VALID
import cgm.core.lib.distance_utils as DIST
from cgm.core import cgm_Meta as cgmMeta
from cgm.core import cgm_General as cgmGEN
from cgm.core.classes import DraggerContextFactory as cgmDrag
from cgm.core.lib import ease_utils as EASE
import time
import maya.mel as mel
from ctypes import windll, Structure, c_long, byref

import maya.cmds as mc

#========================================================================
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
#========================================================================


class LiveRecord(object):
    def __init__(self, plane='screen', onUpdate=None, postBlendFrames=6, loopTime=False):
        _str_func = 'LiveRecord._init_'

        try:
            self.obj = cgmMeta.asMeta(mc.ls(sl=True)[0])
        except:
            log.error("|{0}| >> No object selected".format(_str_func))
            return

        self.plane = plane
        self.onUpdate = onUpdate
        self.isPressed = False
        self.postBlendFrames = postBlendFrames
        self.loopTime = loopTime

    def activate(self):
        self.clickAction = cgmDrag.ClickAction(onPress=self.onPress, onRelease=self.onRelease, dropOnPress=False, dropOnRelease=False)
        mc.draggerContext(self.clickAction.name, edit=True, cursor='hand')

    def record(self):
        log.warning("Starting Record")

        fps = mel.eval('currentTimeUnitToFPS')
               
        startTime = time.time()
        prevTime = startTime

        currentFrame = mc.currentTime(q=True)

        while MOUSE.getMouseDown(1) and currentFrame < mc.playbackOptions(q=True, max=True):
            deltaTime = time.time() - prevTime
            waitTime = self.fixedDeltaTime - deltaTime
            time.sleep( max(waitTime, 0.0) )
            prevTime = time.time()
            startPos = VALID.euclidVector3Arg(self.obj.p_position)
            self.update(self.fixedDeltaTime)
            self._velocity = VALID.euclidVector3Arg(self.obj.p_position) - startPos
            if self.clickAction.modifier == 'ctrl':
                mc.refresh()
            else:
                currentFrame = currentFrame+1
                if self.loopTime:
                    currentFrame = int(currentFrame % mc.playbackOptions(q=True, max=True))
                    if currentFrame == int(mc.playbackOptions(q=True, min=True)):
                        if self._hasSavedKeys:
                            mc.delete(self._animStoreLoc)
                        self._hasSavedKeys = mc.cutKey(self.obj.mNode, at=self.keyableAttrs + ['rx', 'ry', 'rz'], time=(mc.currentTime(q=True),mc.findKeyframe(self.obj.mNode, which='last')+1))
                        if self._hasSavedKeys:
                            self._animStoreLoc = LOC.create()
                            mc.pasteKey(self._animStoreLoc, at=self.keyableAttrs + ['rx', 'ry', 'rz'], o='replaceCompletely')

                mc.currentTime(currentFrame)


        if self.clickAction.modifier != 'ctrl':
            mc.currentTime(currentFrame-1)

        print "Duration: %f" % (time.time() - startTime)
        
        mc.refresh()        


    def quit(self):
        self.clickAction.dropTool()
        self.clickAction = None

    def onPress(self, clickDict):
        self.isPressed = True

        self.offset = MOUSE.Point()
        mp = MOUSE.getMousePosition()
        self.offset.x = int(clickDict['anchorPoint'][0]) - mp['x']
        self.offset.y = int(clickDict['anchorPoint'][1]) - mp['y']

        self.cam = cgmMeta.asMeta(CAM.getCurrentCamera())

        self.planePoint = VALID.euclidVector3Arg(self.obj.p_position)
        self.planeNormal = None
        self.keyableAttrs = []

        self.startTime = mc.currentTime(q=True)

        fps = mel.eval('currentTimeUnitToFPS')
        self.fixedDeltaTime = 1.0/fps        

        if self.plane == 'planeX':
            self.planeNormal = MATHUTILS.Vector3.right()
            self.keyableAttrs = ['ty', 'tz']
        elif self.plane == 'planeY':
            self.planeNormal = MATHUTILS.Vector3.up()
            self.keyableAttrs = ['tx', 'tz']
        elif self.plane == 'planeZ':
            self.planeNormal = MATHUTILS.Vector3.forward()
            self.keyableAttrs = ['tx', 'ty']
        if self.plane == 'x':
            self.planeNormal = VALID.euclidVector3Arg(self.cam.getTransformDirection(MATHUTILS.Vector3.forward()))
            self.keyableAttrs = ['tx']
        elif self.plane == 'y':
            self.planeNormal = VALID.euclidVector3Arg(self.cam.getTransformDirection(MATHUTILS.Vector3.forward()))
            self.keyableAttrs = ['ty']
        elif self.plane == 'z':
            self.planeNormal = VALID.euclidVector3Arg(self.cam.getTransformDirection(MATHUTILS.Vector3.forward()))
            self.keyableAttrs = ['tz']
        else:
            self.planeNormal = VALID.euclidVector3Arg(self.cam.getTransformDirection(MATHUTILS.Vector3.forward()))
            self.keyableAttrs = ['tx', 'ty', 'tz']

        self._objOffset = VALID.euclidVector3Arg(self.obj.p_position) - self.projectOntoPlane(clickDict['vector'])

        if self.clickAction.modifier == 'ctrl':
            mc.cutKey(self.obj.mNode, at=self.keyableAttrs + ['rx', 'ry', 'rz'], time=(mc.currentTime(q=True),), clear=True)
            self._hasSavedKeys = False
        else:
            self._hasSavedKeys = mc.cutKey(self.obj.mNode, at=self.keyableAttrs + ['rx', 'ry', 'rz'], time=(mc.currentTime(q=True),mc.findKeyframe(self.obj.mNode, which='last')+1))
            if self._hasSavedKeys:
                self._animStoreLoc = LOC.create()
                mc.pasteKey(self._animStoreLoc, at=self.keyableAttrs + ['rx', 'ry', 'rz'], o='replaceCompletely')

        self.record()

    def onRelease(self, clickDict):
        _str_func = 'LiveRecord.onRelease'

        if self.clickAction.modifier != 'ctrl':
            log.warning("Completing Recording - Frame {0}".format(mc.currentTime(q=True)))

            self.endTime = mc.currentTime(q=True)

            if self._hasSavedKeys:
                hasKey = mc.cutKey(self._animStoreLoc, at=self.keyableAttrs + ['rx', 'ry', 'rz'], time=(mc.currentTime(q=True)+1,mc.findKeyframe(self._animStoreLoc, which='last')+1))
                if hasKey:
                    mc.pasteKey(self.obj.mNode, at=self.keyableAttrs + ['rx', 'ry', 'rz'], o='replace')
                else:
                    log.warning("|{0}| >> No keys found on storage locator. None pasted".format(_str_func))
                mc.delete(self._animStoreLoc)

            self.postBlend()
        else:
            log.warning("Completing Reposition - Frame {0}".format(mc.currentTime(q=True)))
        
        mc.select(self.obj.mNode)

        self.isPressed = False

    def postBlend(self):
        log.warning("Starting Post Blend")
        startPosition = VALID.euclidVector3Arg(self.obj.p_position)
        
        currentFrame = mc.currentTime(q=True)
        for i in range(self.postBlendFrames+1):
            easeVal = EASE.easeInOutQuad( i / (self.postBlendFrames*1.0) )
            self._velocity = MATHUTILS.Vector3.Lerp(self._velocity, MATHUTILS.Vector3.zero(), easeVal )
            startPosition = startPosition + self._velocity
            self.obj.p_position = MATHUTILS.Vector3.Lerp(startPosition, VALID.euclidVector3Arg(self.obj.p_position), easeVal)
            mc.setKeyframe(self.obj.mNode, at=self.keyableAttrs)

            if self.onUpdate != None:
                self.onUpdate(self.fixedDeltaTime)

            currentFrame = currentFrame + 1
            mc.currentTime(currentFrame)

    def update(self, deltaTime = .04):
        mp = MOUSE.getMousePosition()
        pos, vec = cgmDrag.screenToWorld( mp['x']+self.offset.x, mp['y']+self.offset.y )
        self.moveObjOnPlane(vec)

        if self.onUpdate != None:
            self.onUpdate(deltaTime)

    def projectOntoPlane(self, vector):
        camPos = VALID.euclidVector3Arg(self.cam.p_position)

        self.planePoint = VALID.euclidVector3Arg(self.obj.p_position)       
        rayPoint = VALID.euclidVector3Arg(self.cam.p_position)
        rayDirection = VALID.euclidVector3Arg(vector)

        plane = EUCLID.Plane( EUCLID.Point3(self.planePoint.x, self.planePoint.y, self.planePoint.z), EUCLID.Point3(self.planeNormal.x, self.planeNormal.y, self.planeNormal.z) )
        pos = plane.intersect( EUCLID.Line3( EUCLID.Point3(rayPoint.x, rayPoint.y, rayPoint.z), EUCLID.Vector3(rayDirection.x, rayDirection.y, rayDirection.z) ) )

        return pos

    def moveObjOnPlane(self,vector):
        wantedPos = self.projectOntoPlane(vector) + self._objOffset
        currentPos = VALID.euclidVector3Arg(self.obj.p_position)
        if 'tx' not in self.keyableAttrs:
            wantedPos.x = currentPos.x
        if 'ty' not in self.keyableAttrs:
            wantedPos.y = currentPos.y
        if 'tz' not in self.keyableAttrs:
            wantedPos.z = currentPos.z
        self.obj.p_position = wantedPos
        mc.setKeyframe(self.obj.mNode, at=self.keyableAttrs)