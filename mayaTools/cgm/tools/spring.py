"""
------------------------------------------
spring: cgm.tools
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
from cgm.core.classes import PostBake as PostBake
from cgm.core.lib import locator_utils as LOC
import maya.cmds as mc
import maya.mel as mel

class Spring(PostBake.PostBake):
    def __init__(self, obj = None, aimFwd = 'z+', aimUp = 'y+', damp = .1, spring = 1.0, maxDistance = 100.0, objectScale = 100, pushForce = 8.0, springForce = 5.0, debug=False, showBake=False):
        PostBake.PostBake.__init__(self, obj=obj, showBake=showBake)

        self.aimFwd = VALID.simpleAxis(aimFwd)
        self.aimUp = VALID.simpleAxis(aimUp)

        self.pushForce = pushForce
        self.springForce = springForce
    
        self.maxDistance = maxDistance;
    
        self.force = MATH.Vector3.zero()
        self.spring = spring

        self.debug = debug
        self._debugLoc = None
        self._wantedPosLoc = None
        
        self.damp = damp
        self.objectScale = objectScale

        self.dir = self.obj.getTransformDirection(self.aimFwd.p_vector)*self.objectScale
        self.aimTargetPos = self.obj.p_position + self.dir

        self.keyableAttrs = ['rx', 'ry', 'rz']

        self.lastFwd = MATH.Vector3.forward()
        self.lastUp = MATH.Vector3.up()

    def update(self, deltaTime=.04):

        self.dir = self._bakedLoc.getTransformDirection(self.aimFwd.p_vector)*self.objectScale

        wantedTargetPos = ((VALID.euclidVector3Arg(self.obj.p_position) + self.dir) - self.obj.p_position).normalized()*self.objectScale + self.obj.p_position
        
        self.lastUp = MATH.Vector3.Lerp( self.lastUp, self._bakedLoc.getTransformDirection(self.aimUp.p_vector), min(deltaTime * self.damp, 1.0) ).normalized()

        #self.aimTargetPos = (MATH.Vector3.Lerp(self.aimTargetPos, wantedTargetPos, deltaTime*self.damp) - self.obj.p_position).normalized()*self.objectScale + self.obj.p_position
        
        self.force = self.force + ((1.0 - (min((self.aimTargetPos - wantedTargetPos).magnitude(), self.maxDistance) / self.maxDistance)) * (self.aimTargetPos - wantedTargetPos).normalized() * self.pushForce)
        self.force = self.force + ((self.startPosition - self.aimTargetPos) * self.springForce)
        self.force = self.force * (1.0 - self.damp)
    
        self.aimTargetPos = self.aimTargetPos + (self.force * deltaTime)
        
        self.upTargetPos = (MATH.Vector3.Lerp(self.aimTargetPos, wantedTargetPos, deltaTime*self.damp) - self.obj.p_position).normalized()*self.objectScale + self.obj.p_position

        self.lastFwd = MATH.Vector3.Lerp( self.lastFwd, self._bakedLoc.getTransformDirection(self.aimFwd.p_vector), min(deltaTime * self.damp, 1.0) ).normalized()
        
        SNAP.aim_atPoint(obj=self.obj.mNode, mode='matrix', position=self.aimTargetPos, aimAxis=self.aimFwd.p_string, upAxis=self.aimUp.p_string, vectorUp=self.lastUp )

        if self.debug:
            if not self._debugLoc:
                self._debugLoc = cgmMeta.asMeta(LOC.create(name='debug_loc'))
            self._debugLoc.p_position = self.aimTargetPos
            mc.setKeyframe(self._debugLoc.mNode, at='translate')

            if not self._wantedPosLoc:
                self._wantedPosLoc = cgmMeta.asMeta(LOC.create(name='wanted_pos_loc'))
            self._wantedPosLoc.p_position = wantedTargetPos
            mc.setKeyframe(self._wantedPosLoc.mNode, at='translate')
            
    def preBake(self):
        if not self.bakeTempLocator():
            self.cancelBake()

        self.lastFwd = self._bakedLoc.getTransformDirection(self.aimFwd.p_vector)
        self.lastUp = self._bakedLoc.getTransformDirection(self.aimUp.p_vector)
        
        

    def finishBake(self):
        self.aimTargetPos = self.startPosition + self.dir

        if self._bakedLoc and not self.debug:
            mc.delete(self._bakedLoc.mNode)
            self._bakedLoc = None

    def setAim(self, aimFwd = None, aimUp = None, objectScale = None):
        PostBake.PostBake.setAim(self, aimFwd, aimUp)

        if objectScale:
            self.objectScale = objectScale
        
        self.dir = self.obj.getTransformDirection(self.aimFwd.p_vector)*self.objectScale
        self.aimTargetPos = self.obj.p_position + self.dir



            








