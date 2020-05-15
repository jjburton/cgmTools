from cgm.core.classes import DraggerContextFactory as cgmDrag
from cgm.core.lib import locator_utils as LOC
from cgm.core.lib import math_utils as MATHUTILS
from cgm.core import cgm_General as cgmGEN
from cgm.core.lib import camera_utils as CAM
from cgm.core.lib import euclid as EUCLID
from cgm.core.cgmPy import validateArgs as VALID
import cgm.core.lib.distance_utils as DIST
from cgm.core import cgm_Meta as cgmMeta
import time
import maya.mel as mel
from ctypes import windll, Structure, c_long, byref

import maya.cmds as mc

class LiveRecord(object):
    def __init__(self, clickDict, plane='screen'):
        self.offset = CAM.POINT()
        mp = CAM.getMousePosition()
        self.offset.x = int(clickDict['anchorPoint'][0]) - mp['x']
        self.offset.y = int(clickDict['anchorPoint'][1]) - mp['y']

        self.obj = cgmMeta.asMeta(mc.ls(sl=True)[0])
        self.cam = cgmMeta.asMeta(CAM.getCurrentCamera())

        self.planePoint = VALID.euclidVector3Arg(self.obj.p_position)
        self.planeNormal = None
        self.keyableAttrs = []

        if plane == 'x':
            self.planeNormal = MATHUTILS.Vector3.right()
            self.keyableAttrs = ['ty', 'tz']
        elif plane == 'y':
            self.planeNormal = MATHUTILS.Vector3.up()
            self.keyableAttrs = ['tx', 'tz']
        elif plane == 'z':
            self.planeNormal = MATHUTILS.Vector3.forward()
            self.keyableAttrs = ['tx', 'ty']
        else:
            self.planeNormal = VALID.euclidVector3Arg(self.cam.getTransformDirection(MATHUTILS.Vector3.forward()))
            self.keyableAttrs = ['tx', 'ty', 'tz']

        self.start()

    def start(self):
        print "Starting record"
        fps = mel.eval('currentTimeUnitToFPS')
        
        timeIncrement = 1.0/fps
        
        startTime = time.time()
        prevTime = startTime
        
        for i in range( int(mc.playbackOptions(q=True, min=True)), int(mc.playbackOptions(q=True, max=True)) ):
            deltaTime = time.time() - prevTime
            waitTime = timeIncrement - deltaTime
            time.sleep( max(waitTime, 0.0) )
            prevTime = time.time()
            mc.currentTime(i)
            self.update()

        mc.refresh()        
        print "Duration: %f" % (time.time() - startTime)

    def update(self):
        mp = CAM.getMousePosition()
        pos, vec = cgmDrag.screenToWorld( mp['x']+self.offset.x, mp['y']+self.offset.y )
        self.moveObjOnPlane({'vector':vec})

    def moveObjOnPlane(self,dict=None):        
        camPos = VALID.euclidVector3Arg(self.cam.p_position)

        self.planePoint = VALID.euclidVector3Arg(self.obj.p_position)       
        rayPoint = VALID.euclidVector3Arg(self.cam.p_position)
        rayDirection = VALID.euclidVector3Arg(dict['vector'])

        plane = EUCLID.Plane( EUCLID.Point3(self.planePoint.x, self.planePoint.y, self.planePoint.z), EUCLID.Point3(self.planeNormal.x, self.planeNormal.y, self.planeNormal.z) )
        pos = plane.intersect( EUCLID.Line3( EUCLID.Point3(rayPoint.x, rayPoint.y, rayPoint.z), EUCLID.Vector3(rayDirection.x, rayDirection.y, rayDirection.z) ) )

        self.obj.p_position = pos

        mc.setKeyframe(self.obj.mNode, at=self.keyableAttrs)