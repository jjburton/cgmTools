"""
------------------------------------------
trajectoryAim: cgm.tools
Author: David Bokser
email: dbokser@cgmonks.com
Website : http://www.cgmonks.com
------------------------------------------

================================================================
"""

from cgm.core.lib import math_utils as MATH
from cgm.core.lib import snap_utils as SNAP
from cgm.core.cgmPy import validateArgs as VALID
from cgm.core.classes import PostBake as PostBake

import maya.cmds as mc


class TrajectoryAim(PostBake.PostBake):
    def __init__(self, obj = None, aimFwd = 'z+', aimUp = 'y+', damp = 10, showBake=False):
        PostBake.PostBake.__init__(self, obj=obj, showBake=showBake)

        self.aimFwd = VALID.simpleAxis(aimFwd)
        self.aimUp = VALID.simpleAxis(aimUp)

        self.damp = damp
        self.keyableAttrs = ['rx', 'ry', 'rz']

        self.lastFwd = MATH.Vector3.forward()
        self.lastUp = MATH.Vector3.up()

    def update(self, deltaTime=.04):
        self.lastUp = MATH.Vector3.Lerp( self.lastUp, self._bakedLoc.getTransformDirection(self.aimUp.p_vector), min(deltaTime * self.damp, 1.0) ).normalized()
        self.lastFwd = MATH.Vector3.Lerp( self.lastFwd, self.velocity.normalized(), min(deltaTime * self.damp, 1.0) ).normalized()
        
        SNAP.aim_atPoint(obj=self.obj.mNode, mode='vector', position=self.obj.p_position + self.lastFwd, aimAxis=self.aimFwd.p_string, upAxis=self.aimUp.p_string, vectorUp=self.lastUp )

    def preBake(self):
        self.bakeTempLocator()

        self.lastFwd = self.obj.getTransformDirection(self.aimFwd.p_vector)
        self.lastUp = self.obj.getTransformDirection(self.aimUp.p_vector)

    def finishBake(self):
        if self._bakedLoc:
            mc.delete(self._bakedLoc.mNode)
            self._bakedLoc = None