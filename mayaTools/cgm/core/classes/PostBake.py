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
from cgm.core.lib import transform_utils as TRANS
from cgm.core.lib import math_utils as MATH
from cgm.core.cgmPy import validateArgs as VALID
from cgm.core.lib import snap_utils as SNAP
from cgm.core.lib import locator_utils as LOC

import maya.cmds as mc
import maya.mel as mel

class PostBake(object):
    velocity = MATH.Vector3.zero()
    previousPosition = MATH.Vector3.zero()
    startPosition = MATH.Vector3.zero()

    def __init__(self, obj = None, velocityDamp = 30.0):
        self.obj = None

        if obj is None:
            self.obj = cgmMeta.asMeta( mc.ls(sl=True)[0] )
        else:
            self.obj = cgmMeta.asMeta(obj)


        self.velocity = MATH.Vector3.zero()
        self.startPosition = VALID.euclidVector3Arg(self.obj.p_position)

        self.previousPosition = self.startPosition

        self.keyableAttrs = ['translate', 'rotate', 'scale']

    def bake(self, startTime=None, endTime=None):
        startTime = int(mc.playbackOptions(q=True, min=True))
        endTime = int(mc.playbackOptions(q=True, max=True))

        self.setAim(aimFwd = self.aimFwd, aimUp = self.aimUp)

        fps = mel.eval('currentTimeUnitToFPS')
        
        fixedDeltaTime = 1.0/fps

        self.velocity = MATH.Vector3.zero()

        for i in range(startTime, endTime+1):
            mc.currentTime(i)

            self.previousPosition = VALID.euclidVector3Arg(self.obj.p_position)
            self.update(fixedDeltaTime)
            mc.setKeyframe(self.obj.mNode, at=self.keyableAttrs)
            self.velocity = MATH.Vector3.Lerp(self.velocity, VALID.euclidVector3Arg(self.obj.p_position) - self.previousPosition, fixedDeltaTime * self.velocityDamp)

        self.finishBake()
        #self.previousPos = self.startPosition
        #self.velocity = MATH.Vector3.zero()

        mc.select(self.obj.mNode)

    def update(self, deltaTime = .04):
        pass

    def finishBake(self):
        pass