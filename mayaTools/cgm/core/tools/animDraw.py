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

from cgm.core.tools.liveRecord import LiveRecord

import time

import maya.mel as mel
import maya.cmds as mc

#========================================================================
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
#========================================================================

class RecordableObj(object):
    def __init__(self, obj = None):
        self.obj = cgmMeta.asMeta(obj)
        self.dataDict = {}

        self._bakedLoc = None
        self._animStoreLoc = None
        self.hasSavedKeys = False
        self._prevDataDict = {}

    @cgmGeneral.Timer
    def bakeLoc(self, obj = None):
        if obj is None:
            obj = self.obj

        self._bakedLoc = cgmMeta.asMeta(LOC.create(name='{0}_bakeLoc'.format(self.obj.mNode)))
        SNAP.matchTarget_set(self._bakedLoc.mNode, obj.mNode)

        ct = mc.currentTime(q=True)
        
        SNAP.matchTarget_snap(self._bakedLoc.mNode)

        mc.currentTime(ct)

    def clearBakedLoc(self):
        if self._bakedLoc:
            mc.delete(self._bakedLoc.mNode)
            self._bakedLoc = None

    @cgmGeneral.Timer
    def storeTransformData(self, obj = None):
        if obj is None:
            obj = self.obj

        ct = mc.currentTime(q=True)
        
        self._prevDataDict = {}

        mc.refresh(su=True)
        for i in range(int(ct), int(mc.playbackOptions(q=True, max=True))+1):
            mc.currentTime(i)
            self._prevDataDict[i] = {'p':obj.p_position, 'f':obj.getTransformDirection(EUCLID.Vector3(0,0,1)), 'u':obj.getTransformDirection(EUCLID.Vector3(0,1,0))}
        mc.refresh(su=False)

        mc.currentTime(ct)

    def saveKeys(self, attrs, replaceStored = True, removeOld = True):
        if self.hasSavedKeys and replaceStored:
            mc.delete(self._animStoreLoc)

        func = mc.copyKey
        if removeOld:
            func = mc.cutKey
        self.hasSavedKeys = func(self.obj.mNode, at=attrs, time=(mc.currentTime(q=True),mc.findKeyframe(self.obj.mNode, which='last')+1))
        if self.hasSavedKeys:
            self._animStoreLoc = LOC.create(name='animStoreLoc')
            mc.pasteKey(self._animStoreLoc, at=attrs, o='replaceCompletely')

    def clearSaved(self):
        if self._animStoreLoc:
            mc.delete(self._animStoreLoc)
        self.hasSavedKeys = False
        self._animStoreLoc = None

    def restoreKeys(self, attrs, startTime = None):
        _str_func = 'RecordableObj.restoreKeys'

        if self.hasSavedKeys:
            if startTime is None:
                startTime = mc.currentTime(q=True)+1
            hasKey = mc.cutKey(self._animStoreLoc, at=attrs, time=(startTime,mc.findKeyframe(self._animStoreLoc, which='last')+1))
            if hasKey:
                mc.pasteKey(self.obj.mNode, at=attrs, o='replace')
            else:
                log.warning("|{0}| >> {1} >> No keys found on storage locator. None pasted".format(_str_func, self.obj.mNode))
            self.clearSaved()

    def restoreBakedLocFromData(self, frame=None):
        if frame is None:
            frame = int(mc.currentTime(q=True))
        
        if self._bakedLoc and frame in self._prevDataDict:
            self._bakedLoc.p_position = self._prevDataDict[frame]['p']
            SNAP.aim_atPoint(obj=self._bakedLoc.mNode, mode='matrix', position=self._prevDataDict[frame]['p'] + self._prevDataDict[frame]['f'], aimAxis='z+', upAxis='y+', vectorUp=self._prevDataDict[frame]['u'] )
            return True
        
        return False

class AnimDraw(LiveRecord):
    def __init__(self, plane='screen', mode='position', planeObject = None, recordMode='combine', aimFwd = 'z+', aimUp = 'y+', onStart=None, onUpdate=None, onComplete=None, onReposition=None, onExit=None, postBlendFrames=6, loopTime=False, debug=False):
        _str_func = 'AnimDraw._init_'

        try:
            self.recordableObjs = [RecordableObj(x) for x in mc.ls(sl=True)]
        except:
            log.error("|{0}| >> No objects selected".format(_str_func))
            return

        LiveRecord.__init__(self, onStart=onStart, onUpdate=onUpdate, onComplete=onComplete, onExit=onExit, loopTime=loopTime, debug=debug)

        self.onReposition = onReposition

        self.plane = plane
        self.postBlendFrames = postBlendFrames
        self.mode = mode
        self.planeObject = cgmMeta.asMeta(planeObject) if planeObject else None
        self.aimFwd = VALID.simpleAxis(aimFwd)
        self.aimUp = VALID.simpleAxis(aimUp)
        self.recordMode = recordMode

        self._currentPlaneObject = self.planeObject

        self._debugPlane = None
        self._debugLoc = None
        self._prevDataDict = {}
        self._useCache = False

        self._recordButtons = [1]

    def update(self, deltaTime = .04):
        mp = MOUSE.getMousePosition()
        pos, vec = cgmDrag.screenToWorld( mp['x']+self.offset.x, mp['y']+self.offset.y )
        
        startPos = VALID.euclidVector3Arg(self.recordableObjs[0].obj.p_position)
        currentFrame = int(mc.currentTime(q=True))

        if self.mode == 'position':
            self.moveObjOnPlane(vec)
        elif self.mode == 'aim':
            self.aimObjToPlane(vec)

        self._velocity = VALID.euclidVector3Arg(self.recordableObjs[0].obj.p_position) - startPos
        if self.clickAction.modifier == 'ctrl':
            mc.refresh()
        else:
            currentFrame = currentFrame+1
            if self.loopTime:
                currentFrame = int(currentFrame % mc.playbackOptions(q=True, max=True))
                if currentFrame == int(mc.playbackOptions(q=True, min=True)):
                    self.recordableObjs[0].saveKeys(self.keyableAttrs, replace=True)

            mc.currentTime(currentFrame)

            if self.recordableObjs[0]._bakedLoc:
                if not self.recordableObjs[0].restoreBakedLocFromData(currentFrame):
                    self.recordableObjs[0]._bakedLoc.p_position = self._currentPlaneObject.p_position

        LiveRecord.update(self, deltaTime)

    def completeRecording(self):
        if self.clickAction.modifier != 'ctrl':
            mc.currentTime(currentFrame-1)

    def onPress(self, clickDict):
        LiveRecord.onPress(self, clickDict)
        
        self.validateData()

        if self._mb == 1:
            self.offset = MOUSE.Point()
            mp = MOUSE.getMousePosition()
            self.offset.x = int(clickDict['anchorPoint'][0]) - mp['x']
            self.offset.y = int(clickDict['anchorPoint'][1]) - mp['y']
            
            self._velocity = MATHUTILS.Vector3.zero()

            

            if not self._useCache:
                self.cacheData()

            if self.plane != 'custom':
                projectedPlanePos = self.projectOntoPlane(clickDict['vector'])
                for recordable in self.recordableObjs:
                    recordable.dataDict['objOffset'] = VALID.euclidVector3Arg(recordable.obj.p_position) - projectedPlanePos
            else:
                for recordable in self.recordableObjs:
                    recordable.dataDict['objOffset'] = MATHUTILS.Vector3.zero()

            if self.debug:
                self._debugLoc = cgmMeta.asMeta(LOC.create(name='Debug_Loc'))

            self._debugPlane = makePlaneCurve()
            
            if self.clickAction.modifier != 'ctrl':
                ct = mc.currentTime(q=True)
                for recordable in self.recordableObjs:
                    mc.cutKey(recordable.obj.mNode, at=self.keyableAttrs, time=(ct,mc.findKeyframe(recordable.obj.mNode, which='last')+1))
            
            self.recordableObjs[0].restoreBakedLocFromData(mc.currentTime(q=True))

            self.record()

        else:
            self.cacheData()

    def onRelease(self, clickDict):
        LiveRecord.onRelease(self, clickDict)

        if self._mb == 1:
            self._currentPlaneObject = None

        mc.select([x.obj.mNode for x in self.recordableObjs])

        if self._debugPlane:
            if not self.debug:
                mc.delete(self._debugPlane.mNode)
            self._debugPlane = None

    def completeRecording(self):
        if self.clickAction.modifier != 'ctrl':
            log.warning("Completing Recording - Frame {0}".format(mc.currentTime(q=True)))

            self.endTime = mc.currentTime(q=True)

            for recordable in self.recordableObjs:
                recordable.restoreKeys(attrs=self.keyableAttrs)

            self.postBlend()

            if not self.debug:
                for recordable in self.recordableObjs:
                    recordable.clearBakedLoc()
        else:
            log.warning("Completing Reposition - Frame {0}".format(mc.currentTime(q=True)))
            if self.onReposition != None:
                self.onReposition()

        self._useCache = False

        LiveRecord.completeRecording(self)

    @cgmGeneral.Timer
    def validateData(self):
        # Validate data in case it was manually changed
        #self.obj = cgmMeta.asMeta(self.obj)

        self.aimFwd = VALID.simpleAxis(self.aimFwd)
        self.aimUp = VALID.simpleAxis(self.aimUp)

    @cgmGeneral.Timer
    def cacheData(self):
        self.cam = cgmMeta.asMeta(CAM.getCurrentCamera())

        self.planePoint = VALID.euclidVector3Arg(self.recordableObjs[0].obj.p_position)
        self.planeNormal = None
        self.keyableAttrs = []

        fps = mel.eval('currentTimeUnitToFPS')
        self.fixedDeltaTime = 1.0/fps        

        #if self.mode == 'position':
        self.constructPlaneInfo()

        if self.clickAction.modifier != 'ctrl':
            for i, recordable in enumerate(self.recordableObjs):
                recordable.clearBakedLoc()
                recordable.bakeLoc()
                if self.recordMode == 'combine':
                    if i == 0:
                        recordable.storeTransformData(self._currentPlaneObject)
                    else:
                        recordable.storeTransformData()

            if self.recordableObjs[0]._bakedLoc and self.plane != 'custom':
                self._currentPlaneObject = self.recordableObjs[0]._bakedLoc

        if self.mode == 'aim':
            self.keyableAttrs = ['rx', 'ry', 'rz']

        if self.clickAction.modifier == 'ctrl':
            for recordable in self.recordableObjs:
                mc.cutKey(recordable.obj.mNode, at=self.keyableAttrs, time=(mc.currentTime(q=True),), clear=True)
                recordable.clearSaved()
        else:
            for recordable in self.recordableObjs:
                recordable.saveKeys(self.keyableAttrs, removeOld = False)

        self._useCache = True

    def postBlend(self):
        _str_func = 'LiveRecord.postBlend'

        log.warning("Starting Post Blend")
        for recordable in self.recordableObjs:
            recordable.dataDict['startPosition'] = VALID.euclidVector3Arg(recordable.obj.p_position)
            
        currentFrame = mc.currentTime(q=True)
        if self.postBlendFrames > 0:
            for i in range(self.postBlendFrames+1):
                easeVal = EASE.easeInOutQuad( i / (self.postBlendFrames*1.0) )
                self._velocity = MATHUTILS.Vector3.Lerp(self._velocity, MATHUTILS.Vector3.zero(), easeVal )
                for recordable in self.recordableObjs:
                    recordable.dataDict['startPosition'] = recordable.dataDict['startPosition'] + self._velocity
                    recordable.obj.p_position = MATHUTILS.Vector3.Lerp(recordable.dataDict['startPosition'], VALID.euclidVector3Arg(recordable.obj.p_position), easeVal)
                    mc.setKeyframe(recordable.obj.mNode, at=self.keyableAttrs)

                try:
                    if self.onUpdate != None:
                        self.onUpdate(self.fixedDeltaTime)
                except Exception,err:
                    log.error("|{0}| >> onUpdate function failed: | err: {1}".format(_str_func, err))

                currentFrame = currentFrame + 1
                mc.currentTime(currentFrame)

    def constructPlaneInfo(self):
        self._currentPlaneObject = cgmMeta.asMeta(self.planeObject) if (self.planeObject and self.plane == 'custom') else cgmMeta.asMeta(self.recordableObjs[0].obj)
        
        self._offsetUpVector = self.aimUp.p_vector

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
                self.planeNormal = MATHUTILS.Vector3.up()
                self._offsetUpVector = self.planeObject.getTransformInverseDirection( self.recordableObjs[0].obj.getTransformDirection(self.aimUp.p_vector) )
                self.keyableAttrs = ['tx', 'ty', 'tz']
            else:
                log.error("|{0}| >> Custom plane not found. Please input and try again".format(_str_func))
                return
        elif self.plane == 'object':
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

        log.info('Current plane object : {0}'.format(self._currentPlaneObject))
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
        for recordable in self.recordableObjs:
            wantedPos = projectedPosition + recordable.dataDict['objOffset']
            currentPos = VALID.euclidVector3Arg(recordable.obj.p_position)
            if 'tx' not in self.keyableAttrs:
                wantedPos.x = currentPos.x
            if 'ty' not in self.keyableAttrs:
                wantedPos.y = currentPos.y
            if 'tz' not in self.keyableAttrs:
                wantedPos.z = currentPos.z
            recordable.obj.p_position = wantedPos
            #log.info('{0} wantedPos : {1}, projectedPos : {2}, objOffset : {3}'.format(recordable.obj.mNode, wantedPos, projectedPosition, recordable.dataDict['objOffset']))

        mc.setKeyframe([x.obj.mNode for x in self.recordableObjs], at=self.keyableAttrs)

        if self._debugLoc:
            self._debugLoc.p_position = projectedPosition
            mc.setKeyframe(self._debugLoc.mNode, at='translate')

    def aimObjToPlane(self, vector):
        _str_func = 'LiveRecord.aimObjToPlane'

        wantedPos = self.projectOntoPlane(vector)

        vectorUp = VALID.euclidVector3Arg(self._currentPlaneObject.getTransformDirection(self._offsetUpVector))
        
        for recordable in self.recordableObjs:
            SNAP.aim_atPoint(obj=recordable.obj, mode='matrix', position=wantedPos, aimAxis=self.aimFwd.p_string, upAxis=self.aimUp.p_string, vectorUp=vectorUp)
        
        mc.setKeyframe([x.obj.mNode for x in self.recordableObjs], at=self.keyableAttrs)

        if self._debugLoc:
            self._debugLoc.p_position = wantedPos
            mc.setKeyframe(self._debugLoc.mNode, at='translate')

def makePlaneCurve(size = 10.0):
    p = [(-size, 0, size), (size, 0, size), (size, 0, -size), (-size, 0, -size), (-size, 0, size), (0, 0, size), (0, 0, -size), (-size, 0, -size), (-size, 0, 0), (size, 0, 0)]
    k = range(10)
    return cgmMeta.asMeta( mc.curve(name='planeCrv', d=1, p=p, k=k) )
