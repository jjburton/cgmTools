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
from cgm.core.lib import snap_utils as SNAP
from cgm.core import cgm_General as cgmGeneral

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
    def __init__(self, plane='screen', mode='position', planeObject = None, recordMode='combine', aimFwd = 'z+', aimUp = 'y+', onStart=None, onUpdate=None, onComplete=None, onReposition=None, onExit=None, postBlendFrames=6, loopTime=False, debug=False):
        _str_func = 'LiveRecord._init_'

        try:
            self.obj = cgmMeta.asMeta(mc.ls(sl=True)[0])
        except:
            log.error("|{0}| >> No object selected".format(_str_func))
            return

        # Callbacks
        self.onStart = onStart
        self.onUpdate = onUpdate
        self.onComplete = onComplete
        self.onReposition = onReposition
        self.onExit = onExit

        self.plane = plane
        self.isPressed = False
        self.isRecording = False
        self.postBlendFrames = postBlendFrames
        self.loopTime = loopTime
        self.mode = mode
        self.planeObject = cgmMeta.asMeta(planeObject) if planeObject else None
        self.aimFwd = VALID.simpleAxis(aimFwd)
        self.aimUp = VALID.simpleAxis(aimUp)
        self.debug = debug
        self.recordMode = recordMode

        self._currentPlaneObject = self.planeObject

        self._debugPlane = None
        self._debugLoc = None
        self._bakedLoc = None
        self._animStoreLoc = None
        self._prevDataDict = {}
        self._useCache = False

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

        if self._bakedLoc and currentFrame in self._prevDataDict:
            self._bakedLoc.p_position = self._prevDataDict[currentFrame]['p']
            SNAP.aim_atPoint(obj=self._bakedLoc.mNode, mode='matrix', position=self._prevDataDict[currentFrame]['p'] + self._prevDataDict[currentFrame]['f'], aimAxis='z+', upAxis='y+', vectorUp=self._prevDataDict[currentFrame]['u'] )

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
                        self._hasSavedKeys = mc.cutKey(self.obj.mNode, at=self.keyableAttrs, time=(mc.currentTime(q=True),mc.findKeyframe(self.obj.mNode, which='last')+1))
                        if self._hasSavedKeys:
                            self._animStoreLoc = LOC.create(name='animStoreLoc')
                            mc.pasteKey(self._animStoreLoc, at=self.keyableAttrs, o='replaceCompletely')

                mc.currentTime(currentFrame)

                if self._bakedLoc:
                    if currentFrame in self._prevDataDict and self.recordMode == 'combine':
                        self._bakedLoc.p_position = self._prevDataDict[currentFrame]['p']
                        SNAP.aim_atPoint(obj=self._bakedLoc.mNode, mode='matrix', position=self._prevDataDict[currentFrame]['p'] + self._prevDataDict[currentFrame]['f'], aimAxis='z+', upAxis='y+', vectorUp=self._prevDataDict[currentFrame]['u'] )
                    else:
                        self._bakedLoc.p_position = self.obj.p_position

        if self.clickAction.modifier != 'ctrl':
            mc.currentTime(currentFrame-1)

        print "Duration: %f" % (time.time() - startTime)
        
        mc.refresh()        

    @cgmGeneral.Timer
    def bakeLoc(self):
        self._bakedLoc = cgmMeta.asMeta(LOC.create(name='bakeLoc'))
        SNAP.matchTarget_set(self._bakedLoc.mNode, self._currentPlaneObject.mNode)

        ct = mc.currentTime(q=True)
        
        SNAP.matchTarget_snap(self._bakedLoc.mNode)

        # mc.refresh(su=True)
        # for i in range(int(ct), int(mc.playbackOptions(q=True, max=True))+1):
        #     mc.currentTime(i)
        #     SNAP.matchTarget_snap(self._bakedLoc.mNode)
        #     mc.setKeyframe(self._bakedLoc.mNode, at=['translate', 'rotate'])
        # mc.refresh(su=False)

        mc.currentTime(ct)

    @cgmGeneral.Timer
    def storeTransformData(self):
        #self._bakedLoc = cgmMeta.asMeta(LOC.create(name='bakeLoc'))
        #SNAP.matchTarget_set(self._bakedLoc.mNode, self._currentPlaneObject.mNode)

        ct = mc.currentTime(q=True)
        
        #SNAP.matchTarget_snap(self._bakedLoc.mNode)
        self._prevDataDict = {}

        #if self.recordMode == 'combine':
        if self.recordMode == 'combine':
            mc.refresh(su=True)
            for i in range(int(ct), int(mc.playbackOptions(q=True, max=True))+1):
                mc.currentTime(i)
                self._prevDataDict[i] = {'p':self._currentPlaneObject.p_position, 'f':self._currentPlaneObject.getTransformDirection(EUCLID.Vector3(0,0,1)), 'u':self._currentPlaneObject.getTransformDirection(EUCLID.Vector3(0,1,0))}
            mc.refresh(su=False)

        mc.currentTime(ct)

    def quit(self):
        _str_func = 'LiveRecord.quit'

        self.clickAction.dropTool()
        self.clickAction = None

    def onPress(self, clickDict):
        _str_func = 'LiveRecord.onPress'

        mb = mc.draggerContext( self.clickAction.name, q=True, button=True )

        self.isPressed = True

        if mb == 1:
            self.isRecording = False

            self.offset = MOUSE.Point()
            mp = MOUSE.getMousePosition()
            self.offset.x = int(clickDict['anchorPoint'][0]) - mp['x']
            self.offset.y = int(clickDict['anchorPoint'][1]) - mp['y']

            self.startTime = mc.currentTime(q=True)
            
            self._velocity = MATHUTILS.Vector3.zero()

            self.validateData()

            if not self._useCache:
                self.cacheData()

            self._objOffset = MATHUTILS.Vector3.zero()
            if self.plane != 'custom':
                self._objOffset = VALID.euclidVector3Arg(self.obj.p_position) - self.projectOntoPlane(clickDict['vector'])

            if self.debug:
                self._debugLoc = cgmMeta.asMeta(LOC.create(name='Debug_Loc'))

            self._debugPlane = makePlaneCurve()
            
            if self.clickAction.modifier != 'ctrl':
                mc.cutKey(self.obj.mNode, at=self.keyableAttrs, time=(mc.currentTime(q=True),mc.findKeyframe(self.obj.mNode, which='last')+1))
            
            self.record()
        else:
            self.cacheData()

    @cgmGeneral.Timer
    def validateData(self):
        # Validate data in case it was manually changed
        self.obj = cgmMeta.asMeta(self.obj)

        self.aimFwd = VALID.simpleAxis(self.aimFwd)
        self.aimUp = VALID.simpleAxis(self.aimUp)

    @cgmGeneral.Timer
    def cacheData(self):
        self.cam = cgmMeta.asMeta(CAM.getCurrentCamera())

        self.planePoint = VALID.euclidVector3Arg(self.obj.p_position)
        self.planeNormal = None
        self.keyableAttrs = []

        fps = mel.eval('currentTimeUnitToFPS')
        self.fixedDeltaTime = 1.0/fps        

        #if self.mode == 'position':
        self.constructPlaneInfo()

        if self.clickAction.modifier != 'ctrl':
            if self._bakedLoc:
                mc.delete(self._bakedLoc.mNode)
                self._bakedLoc = None
            self.bakeLoc()
            self.storeTransformData()
            if self._bakedLoc:
                self._currentPlaneObject = self._bakedLoc

        if self.mode == 'aim':
            self.keyableAttrs = ['rx', 'ry', 'rz']

        if self.clickAction.modifier == 'ctrl':
            mc.cutKey(self.obj.mNode, at=self.keyableAttrs, time=(mc.currentTime(q=True),), clear=True)
            self._hasSavedKeys = False
        else:
            self._hasSavedKeys = mc.copyKey(self.obj.mNode, at=self.keyableAttrs, time=(mc.currentTime(q=True),mc.findKeyframe(self.obj.mNode, which='last')+1))
            if self._hasSavedKeys:
                self._animStoreLoc = LOC.create(name='animStoreLoc')
                mc.pasteKey(self._animStoreLoc, at=self.keyableAttrs, o='replaceCompletely')
                # if self._bakedLoc and self.planeObject == self.obj:
                #     self.planeObject = self._bakedLoc

        self._useCache = True

    def onRelease(self, clickDict):
        _str_func = 'LiveRecord.onRelease'

        if self.isRecording:
            self.isRecording = False
            if self.clickAction.modifier != 'ctrl':
                log.warning("Completing Recording - Frame {0}".format(mc.currentTime(q=True)))

                self.endTime = mc.currentTime(q=True)

                if self._hasSavedKeys:
                    hasKey = mc.cutKey(self._animStoreLoc, at=self.keyableAttrs, time=(mc.currentTime(q=True)+1,mc.findKeyframe(self._animStoreLoc, which='last')+1))
                    if hasKey:
                        mc.pasteKey(self.obj.mNode, at=self.keyableAttrs, o='replace')
                    else:
                        log.warning("|{0}| >> No keys found on storage locator. None pasted".format(_str_func))
                    mc.delete(self._animStoreLoc)

                self.postBlend()

                if self._bakedLoc:
                    if self.planeObject == self._bakedLoc:
                        self.planeObject = self.obj
                    if not self.debug:
                        mc.delete(self._bakedLoc.mNode)
                    self._bakedLoc = None

                if self.onComplete != None:
                    self.onComplete()
            else:
                log.warning("Completing Reposition - Frame {0}".format(mc.currentTime(q=True)))
                if self.onReposition != None:
                    self.onReposition()

            self._useCache = False

        mc.select(self.obj.mNode)

        if self._debugPlane:
            if not self.debug:
                mc.delete(self._debugPlane.mNode)
            self._debugPlane = None

        self.isPressed = False

    def onFinalize(self):
        if self.onExit:
            self.onExit()

    def postBlend(self):
        _str_func = 'LiveRecord.postBlend'

        log.warning("Starting Post Blend")
        startPosition = VALID.euclidVector3Arg(self.obj.p_position)
        
        currentFrame = mc.currentTime(q=True)
        for i in range(self.postBlendFrames+1):
            easeVal = EASE.easeInOutQuad( i / (self.postBlendFrames*1.0) )
            self._velocity = MATHUTILS.Vector3.Lerp(self._velocity, MATHUTILS.Vector3.zero(), easeVal )
            startPosition = startPosition + self._velocity
            self.obj.p_position = MATHUTILS.Vector3.Lerp(startPosition, VALID.euclidVector3Arg(self.obj.p_position), easeVal)
            mc.setKeyframe(self.obj.mNode, at=self.keyableAttrs)

            try:
                if self.onUpdate != None:
                    self.onUpdate(self.fixedDeltaTime)
            except Exception,err:
                log.error("|{0}| >> onUpdate function failed: | err: {1}".format(_str_func, err))

            currentFrame = currentFrame + 1
            mc.currentTime(currentFrame)

    def update(self, deltaTime = .04):
        _str_func = 'LiveRecord.update'

        mp = MOUSE.getMousePosition()
        pos, vec = cgmDrag.screenToWorld( mp['x']+self.offset.x, mp['y']+self.offset.y )
        
        if self.mode == 'position':
            self.moveObjOnPlane(vec)
        elif self.mode == 'aim':
            self.aimObjToPlane(vec)

        try:
            if self.onUpdate != None:
                self.onUpdate(deltaTime)
        except Exception,err:
            log.error("|{0}| >> onUpdate function failed: | err: {1}".format(_str_func, err))

    def constructPlaneInfo(self):
        self._currentPlaneObject = cgmMeta.asMeta(self.planeObject) if self.planeObject and self.plane == 'custom' else cgmMeta.asMeta(self.obj)

        if self.plane == 'planeX':
            self.planeNormal = MATHUTILS.Vector3.right()
            self.keyableAttrs = ['ty', 'tz']
        elif self.plane == 'planeY':
            self.planeNormal = MATHUTILS.Vector3.up()
            self.keyableAttrs = ['tx', 'tz']
        elif self.plane == 'planeZ':
            self.planeNormal = MATHUTILS.Vector3.forward()
            self.keyableAttrs = ['tx', 'ty']
        elif self.plane == 'axisX':
            self.planeNormal = VALID.euclidVector3Arg(self.cam.getTransformDirection(MATHUTILS.Vector3.forward()))
            self.keyableAttrs = ['tx']
        elif self.plane == 'axisY':
            self.planeNormal = VALID.euclidVector3Arg(self.cam.getTransformDirection(MATHUTILS.Vector3.forward()))
            self.keyableAttrs = ['ty']
        elif self.plane == 'axisZ':
            self.planeNormal = VALID.euclidVector3Arg(self.cam.getTransformDirection(MATHUTILS.Vector3.forward()))
            self.keyableAttrs = ['tz']
        elif self.plane == 'custom':
            if self.planeObject:
                self.planeNormal = VALID.euclidVector3Arg(self._currentPlaneObject.getTransformDirection(MATHUTILS.Vector3.up()))
                self.keyableAttrs = ['tx', 'ty', 'tz']
            else:
                log.error("|{0}| >> Custom plane not found. Please input and try again".format(_str_func))
                return
        elif self.plane == 'object':
            # Since we're using the object and are going to be removing keys
            # we need to bake the existing animation to a locator and use that
            # as the relevant plane
            #self._currentPlaneObject = self._bakedLoc if self._bakedLoc else self.obj
            self.planeNormal = VALID.euclidVector3Arg(self.aimUp.p_vector)
            self.keyableAttrs = ['tx', 'ty', 'tz']
        else:
            self.planeNormal = VALID.euclidVector3Arg(self.cam.getTransformDirection(MATHUTILS.Vector3.forward()))
            self.keyableAttrs = ['tx', 'ty', 'tz']

    def projectOntoPlane(self, vector):
        _str_func = 'LiveRecord.projectOntoPlane'

        camPos = VALID.euclidVector3Arg(self.cam.p_position)

        planeNormal = self.planeNormal
        if self.plane in ['custom', 'object']:
            planeNormal = VALID.euclidVector3Arg(self._currentPlaneObject.getTransformDirection(self.planeNormal))
        else:
            self.planePoint = VALID.euclidVector3Arg(self.obj.p_position)       
        
        self.planePoint = VALID.euclidVector3Arg(self._currentPlaneObject.p_position)

        rayPoint = VALID.euclidVector3Arg(self.cam.p_position)
        rayDirection = VALID.euclidVector3Arg(vector)

        plane = EUCLID.Plane( EUCLID.Point3(self.planePoint.x, self.planePoint.y, self.planePoint.z), EUCLID.Point3(planeNormal.x, planeNormal.y, planeNormal.z) )
        pos = plane.intersect( EUCLID.Line3( EUCLID.Point3(rayPoint.x, rayPoint.y, rayPoint.z), EUCLID.Vector3(rayDirection.x, rayDirection.y, rayDirection.z) ) )

        if self._debugPlane:
            self._debugPlane.p_position = self.planePoint
            SNAP.aim_atPoint(obj=self._debugPlane.mNode, mode='matrix', position=self.planePoint + planeNormal, aimAxis='y+', upAxis='z+', vectorUp=planeNormal.cross(EUCLID.Vector3(0,1,.01) ) )

        return pos

    def moveObjOnPlane(self,vector):
        _str_func = 'LiveRecord.moveObjOnPlane'

        projectedPosition = self.projectOntoPlane(vector)
        wantedPos = projectedPosition + self._objOffset
        currentPos = VALID.euclidVector3Arg(self.obj.p_position)
        if 'tx' not in self.keyableAttrs:
            wantedPos.x = currentPos.x
        if 'ty' not in self.keyableAttrs:
            wantedPos.y = currentPos.y
        if 'tz' not in self.keyableAttrs:
            wantedPos.z = currentPos.z
        self.obj.p_position = wantedPos

        if self._debugLoc:
            self._debugLoc.p_position = projectedPosition
            mc.setKeyframe(self._debugLoc.mNode, at='translate')
        mc.setKeyframe(self.obj.mNode, at=self.keyableAttrs)

    def aimObjToPlane(self, vector):
        _str_func = 'LiveRecord.aimObjToPlane'

        wantedPos = self.projectOntoPlane(vector)
        #vectorUp = None
        vectorUp = VALID.euclidVector3Arg(self._currentPlaneObject.getTransformDirection(self.aimUp.p_vector))
        SNAP.aim_atPoint(obj=self.obj, mode='matrix', position=wantedPos, aimAxis=self.aimFwd.p_string, upAxis=self.aimUp.p_string, vectorUp=vectorUp)
        mc.setKeyframe(self.obj.mNode, at=self.keyableAttrs)

        if self._debugLoc:
            self._debugLoc.p_position = wantedPos
            mc.setKeyframe(self._debugLoc.mNode, at='translate')

def makePlaneCurve(size = 10.0):
    p = [(-size, 0, size), (size, 0, size), (size, 0, -size), (-size, 0, -size), (-size, 0, size), (0, 0, size), (0, 0, -size), (-size, 0, -size), (-size, 0, 0), (size, 0, 0)]
    k = range(10)
    return cgmMeta.asMeta( mc.curve(name='planeCrv', d=1, p=p, k=k) )
