"""
------------------------------------------
post_bake: cgm.tools
Author: David Bokser
email: dbokser@cgmonks.com
Website : http://www.cgmonks.com
------------------------------------------

================================================================
"""

from cgm.core import cgm_Meta as cgmMeta
from cgm.core.lib import math_utils as MATH
from cgm.core.cgmPy import validateArgs as VALID
from cgm.core.lib import snap_utils as SNAP
from cgm.core.lib import locator_utils as LOC
from cgm.core import cgm_General as cgmGeneral

import maya.cmds as mc
import maya.mel as mel

class PostBake(object):
    velocity = MATH.Vector3.zero()
    previousPosition = MATH.Vector3.zero()
    startPosition = MATH.Vector3.zero()

    def __init__(self, obj = None, velocityDamp = 30.0, showBake=False):
        self.obj = None
        self.velocityDamp = velocityDamp
        self.showBake = showBake

        if obj is None:
            self.obj = cgmMeta.asMeta( mc.ls(sl=True)[0] )
        else:
            self.obj = cgmMeta.asMeta(obj)

        self.aimFwd = VALID.simpleAxis('z+')
        self.aimUp = VALID.simpleAxis('y+')

        self.velocity = MATH.Vector3.zero()
        self.startPosition = VALID.euclidVector3Arg(self.obj.p_position)

        self.previousPosition = self.startPosition

        self.keyableAttrs = ['translate', 'rotate', 'scale']
        self._bakedLoc = None

        self.startTime = int(mc.playbackOptions(q=True, min=True))
        self.endTime = int(mc.playbackOptions(q=True, max=True))

    def bake(self, startTime=None, endTime=None):
        self.startTime = int(mc.playbackOptions(q=True, min=True)) if startTime is None else startTime
        self.endTime = int(mc.playbackOptions(q=True, max=True)) if endTime is None else endTime

        mc.currentTime(self.startTime)

        self.preBake()

        self.setAim(aimFwd = self.aimFwd, aimUp = self.aimUp)

        fps = mel.eval('currentTimeUnitToFPS')
        
        fixedDeltaTime = 1.0/fps

        self.velocity = MATH.Vector3.zero()

        mc.refresh(su=not self.showBake)
        for i in range(self.startTime, self.endTime+1):
            mc.currentTime(i)

            self.update(fixedDeltaTime)
            mc.setKeyframe(self.obj.mNode, at=self.keyableAttrs)
            self.velocity = MATH.Vector3.Lerp(self.velocity, VALID.euclidVector3Arg(self.obj.p_position) - self.previousPosition, min(fixedDeltaTime * self.velocityDamp, 1.0))
            self.previousPosition = VALID.euclidVector3Arg(self.obj.p_position)

        mc.refresh(su=False)

        self.finishBake()
        #self.previousPos = self.startPosition
        #self.velocity = MATH.Vector3.zero()

        mc.select(self.obj.mNode)

    def preBake(self):
        pass

    def update(self, deltaTime = .04):
        pass

    def finishBake(self):
        pass

    def setAim(self, aimFwd = None, aimUp = None):
        if aimFwd:
            self.aimFwd = VALID.simpleAxis(aimFwd)

        if aimUp:
            self.aimUp = VALID.simpleAxis(aimUp)

    @cgmGeneral.Timer
    def bakeTempLocator(self, startTime = None, endTime = None):
        if startTime is None:
            startTime = mc.playbackOptions(q=True, min=True)
        if endTime is None:
            endTime = mc.playbackOptions(q=True, max=True)
        
        ct = mc.currentTime(q=True)

        self._bakedLoc = cgmMeta.asMeta(LOC.create(name='bakeLoc'))
        SNAP.matchTarget_set(self._bakedLoc.mNode, self.obj.mNode)
      
        SNAP.matchTarget_snap(self._bakedLoc.mNode)

        mc.refresh(su=True)
        for i in range(int(ct), int(mc.playbackOptions(q=True, max=True))+1):
            mc.currentTime(i)
            SNAP.matchTarget_snap(self._bakedLoc.mNode)
            mc.setKeyframe(self._bakedLoc.mNode, at=['translate', 'rotate'])
        mc.refresh(su=False)

        mc.currentTime(ct)