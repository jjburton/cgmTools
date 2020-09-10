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

#>>>======================================================================
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
#=========================================================================

class Spring(PostBake.PostBake):
    def __init__(self, obj = None, aimFwd = 'z+', aimUp = 'y+', damp = .1, angularDamp = .1, angularUpDamp = .1, spring = 1.0, maxDistance = 100.0, objectScale = 100, pushForce = 8.0, springForce = 5.0, angularSpringForce = 5.0, angularUpSpringForce = 5.0, collider = None, rotate=True, translate=True, debug=False, showBake=False):
        PostBake.PostBake.__init__(self, obj=obj, showBake=showBake)

        self.translate = translate
        self.rotate = rotate
        
        self.aimFwd = VALID.simpleAxis(aimFwd)
        self.aimUp = VALID.simpleAxis(aimUp)

        self.pushForce = pushForce
        
        self.springForce = springForce
        self.angularSpringForce = angularSpringForce
        self.angularUpSpringForce = angularUpSpringForce
        
        self.maxDistance = maxDistance;
    
        self.positionForce = MATH.Vector3.zero()
        self.angularForce = MATH.Vector3.zero()
        self.angularUpForce = MATH.Vector3.zero()
        
        self.spring = spring

        self.debug = debug
        self._debugLoc = None
        self._wantedPosLoc = None
        self._wantedUpLoc = None
        
        self.collider = cgmMeta.asMeta(collider) if collider else None
        
        self.damp = damp
        self.angularDamp = angularDamp
        self.upDamp = angularUpDamp
        
        self.objectScale = objectScale

        self.dir = self.obj.getTransformDirection(self.aimFwd.p_vector)*self.objectScale
        self.aimTargetPos = self.obj.p_position + self.dir
        self.upTargetPos = self.obj.getTransformDirection(self.aimUp.p_vector)*self.objectScale
        
        self.keyableAttrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz']

        #self.lastFwd = MATH.Vector3.forward()
        #self.lastUp = MATH.Vector3.up()

    def update(self, deltaTime=.04):
        #log.info("Updating")
        
        if self.translate:
            self.positionForce = self.positionForce + ((VALID.euclidVector3Arg(self._bakedLoc.p_position) - VALID.euclidVector3Arg(self.previousPosition)) * self.springForce)
            self.positionForce = self.positionForce * (1.0 - self.damp)
            
            self.obj.p_position = self.obj.p_position + (self.positionForce * deltaTime)
            
        if self.rotate:
            self.dir = self._bakedLoc.getTransformDirection(self.aimFwd.p_vector) * self.objectScale
    
            wantedTargetPos = ((VALID.euclidVector3Arg(self.obj.p_position) + self.dir) - self.obj.p_position).normalized() * self.objectScale + self.obj.p_position
            wantedUp = self._bakedLoc.getTransformDirection(self.aimUp.p_vector) * self.objectScale
            
            self.angularForce = self.angularForce + ((wantedTargetPos - self.aimTargetPos) * self.angularSpringForce)
            self.angularForce = self.angularForce * (1.0 - self.angularDamp)
            
            self.angularUpForce = self.angularUpForce + ((wantedUp - self.upTargetPos) * self.angularUpSpringForce)
            self.angularUpForce = self.angularUpForce * (1.0 - self.upDamp)       
            
            self.aimTargetPos = self.aimTargetPos + (self.angularForce * deltaTime)
            self.upTargetPos = self.upTargetPos + (self.angularUpForce * deltaTime)
                    
            SNAP.aim_atPoint(obj=self.obj.mNode, mode='matrix', position=self.aimTargetPos, aimAxis=self.aimFwd.p_string, upAxis=self.aimUp.p_string, vectorUp=self.upTargetPos.normalized() )

        if self.debug:
            if not self._debugLoc:
                self._debugLoc = cgmMeta.asMeta(LOC.create(name='debug_loc'))
            self._debugLoc.p_position = self.aimTargetPos
            mc.setKeyframe(self._debugLoc.mNode, at='translate')

            if not self._wantedUpLoc:
                self._wantedUpLoc = cgmMeta.asMeta(LOC.create(name='wanted_up_loc'))
            self._wantedUpLoc.p_position = self.obj.p_position + self.upTargetPos
            mc.setKeyframe(self._wantedUpLoc.mNode, at='translate')

            if not self._wantedPosLoc:
                self._wantedPosLoc = cgmMeta.asMeta(LOC.create(name='wanted_pos_loc'))
            self._wantedPosLoc.p_position = wantedTargetPos
            mc.setKeyframe(self._wantedPosLoc.mNode, at='translate')
            
    def preBake(self):
        if not self.bakeTempLocator():
            self.cancelBake()
        
        self.dir = self._bakedLoc.getTransformDirection(self.aimFwd.p_vector) * self.objectScale
        self.aimTargetPos = self.obj.p_position + self.dir
        
        self.upTargetPos = self._bakedLoc.getTransformDirection(self.aimUp.p_vector) * self.objectScale
        
        self.positionForce = MATH.Vector3.zero()
        self.angularForce = MATH.Vector3.zero()
        self.angularUpForce = MATH.Vector3.zero()
        
        self.keyableAttrs = []
        if self.translate:
            self.keyableAttrs += ['tx', 'ty', 'tz']
        if self.rotate:
            self.keyableAttrs += ['rx', 'ry', 'rz']        
        
    def finishBake(self):
        self.aimTargetPos = self.startPosition + self.dir

        if self._bakedLoc and not self.debug:
            mc.delete(self._bakedLoc.mNode)
            self._bakedLoc = None

    def setAim(self, aimFwd = None, aimUp = None, objectScale = None):
        PostBake.PostBake.setAim(self, aimFwd, aimUp)

        if objectScale:
            self.objectScale = objectScale
        
        #self.dir = self.obj.getTransformDirection(self.aimFwd.p_vector)*self.objectScale
        #self.aimTargetPos = self.obj.p_position + self.dir



            








