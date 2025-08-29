"""
------------------------------------------
spring: cgm.tools
Author: David Bokser
email: dbokser@cgmonks.com
Website : https://github.com/jjburton/cgmTools/wiki
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
    def __init__(self, obj = None, aimFwd = 'z+', aimUp = 'y+', damp = .1, angularDamp = .1, angularUpDamp = .1, spring = 1.0, maxDistance = 100.0, objectScale = 100, pushForce = 8.0, springForce = 5.0, angularSpringForce = 5.0, angularUpSpringForce = 5.0, collider = None, rotate=True, translate=True,
                 cycleState = False, cycleBlend = 5, cycleMode = 'reverseBlend',
                 minLimitUse = False,
                 minLimit = None,
                 maxLimitUse = False,
                 maxLimit = None,
                 translateMinXLimitUse = False,
                 translateMinXLimit = None,
                 translateMaxXLimitUse = False,
                 translateMaxXLimit = None,
                 
                 translateMinYLimitUse = False,
                 translateMinYLimit = None,
                 translateMaxYLimitUse = False,
                 translateMaxYLimit = None,
                 
                 translateMinZLimitUse = False,
                 translateMinZLimit = None,
                 translateMaxZLimitUse = False,
                 translateMaxZLimit = None,
                 
                 rotateMinXLimitUse = False,
                 rotateMinXLimit = None,
                 rotateMaxXLimitUse = False,
                 rotateMaxXLimit = None,
                 
                 rotateMinYLimitUse = False,
                 rotateMinYLimit = None,
                 rotateMaxYLimitUse = False,
                 rotateMaxYLimit = None,
                 
                 rotateMinZLimitUse = False,
                 rotateMinZLimit = None,
                 rotateMaxZLimitUse = False,
                 rotateMaxZLimit = None,
                 debug=False, showBake=False):
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
        # Initialize upTargetPos as a world position (will be properly set in preBake)
        self.upTargetPos = MATH.Vector3.zero()
        
        self.keyableAttrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz']


        self.cycleBlend = cycleBlend
        self.cycleState = cycleState
        self.cycleMode = cycleMode
        
        self.minLimitUse = minLimitUse
        self.minLimit = minLimit
        self.maxLimitUse = maxLimitUse
        self.maxLimit = maxLimit
        
        self.translateMinXLimitUse = translateMinXLimitUse
        self.translateMinXLimit = translateMinXLimit 
        self.translateMaxXLimitUse = translateMaxXLimitUse 
        self.translateMaxXLimit = translateMaxXLimit
        
        self.translateMinYLimitUse = translateMinYLimitUse
        self.translateMinYLimit = translateMinYLimit 
        self.translateMaxYLimitUse = translateMaxYLimitUse 
        self.translateMaxYLimit = translateMaxYLimit 
        
        self.translateMinZLimitUse = translateMinZLimitUse
        self.translateMinZLimit = translateMinZLimit 
        self.translateMaxZLimitUse = translateMaxZLimitUse
        self.translateMaxZLimit = translateMaxZLimit 
        
        self.rotateMinXLimitUse = rotateMinXLimitUse 
        self.rotateMinXLimit = rotateMinXLimit 
        self.rotateMaxXLimitUse = rotateMaxXLimitUse 
        self.rotateMaxXLimit = rotateMaxXLimit 
        
        self.rotateMinYLimitUse = rotateMinYLimitUse 
        self.rotateMinYLimit = rotateMinYLimit 
        self.rotateMaxYLimitUse = rotateMaxYLimitUse 
        self.rotateMaxYLimit = rotateMaxYLimit 
        
        self.rotateMinZLimitUse = rotateMinZLimitUse 
        self.rotateMinZLimit = rotateMinZLimit 
        self.rotateMaxZLimitUse = rotateMaxZLimitUse 
        self.rotateMaxZLimit = rotateMaxZLimit             
        
        #self.lastFwd = MATH.Vector3.forward()
        #self.lastUp = MATH.Vector3.up()

    def update(self, deltaTime=.04):
        #log.info("Updating")
        
        if self.translate:
            self.positionForce = self.positionForce + ((VALID.euclidVector3Arg(self._bakedLoc.p_position) - VALID.euclidVector3Arg(self.previousPosition)) * self.springForce)
            self.positionForce = self.positionForce * (1.0 - self.damp)
            
            self.obj.p_position = self.previousPosition + (self.positionForce * deltaTime)
            
            
            for a in 'XYZ':
                for a2 in ['Min','Max']:
                    _plugUse = 'translate{}{}LimitUse'.format(a2,a)
                    _plugValue = 'translate{}{}Limit'.format(a2,a)
                    _attr = 'translate{}'.format(a)
                    
                    if hasattr(self,_plugUse) and self.__dict__[_plugUse] and hasattr(self,_plugValue):
                        _value = self.__dict__.get(_plugValue)
                        if _value is not None:
                            if a2 == 'Min':
                                if self.obj.getMayaAttr(_attr) < _value:
                                    self.obj.setMayaAttr(_attr, _value,force=False)                                 
                            else:
                                if self.obj.getMayaAttr(_attr) > _value:
                                    self.obj.setMayaAttr(_attr, _value,force=False)                                 
            
        if self.rotate:
            self.dir = self._bakedLoc.getTransformDirection(self.aimFwd.p_vector) * self.objectScale
    
            wantedTargetPos = ((VALID.euclidVector3Arg(self.obj.p_position) + self.dir) - self.obj.p_position).normalized() * self.objectScale + self.obj.p_position
            # Calculate the world position where the up vector should point
            wantedUp = self._bakedLoc.p_position + (self._bakedLoc.getTransformDirection(self.aimUp.p_vector) * self.objectScale)
            
            self.angularForce = self.angularForce + ((wantedTargetPos - self.aimTargetPos) * self.angularSpringForce)
            self.angularForce = self.angularForce * (1.0 - self.angularDamp)
            
            self.angularUpForce = self.angularUpForce + ((wantedUp - self.upTargetPos) * self.angularUpSpringForce)
            self.angularUpForce = self.angularUpForce * (1.0 - self.upDamp)       
            
            self.aimTargetPos = self.aimTargetPos + (self.angularForce * deltaTime)
            self.upTargetPos = self.upTargetPos + (self.angularUpForce * deltaTime)
                    
            SNAP.aim_atPoint(obj=self.obj.mNode, mode='position', position=self.aimTargetPos, aimAxis=self.aimFwd.p_string, upAxis=self.aimUp.p_string, vectorUp= wantedUp  )
            
            
            for a in 'XYZ':
                for a2 in ['Min','Max']:
                    _plugUse = 'rotate{}{}LimitUse'.format(a2,a)
                    _plugValue = 'rotate{}{}Limit'.format(a2,a)
                    _attr = 'rotate{}'.format(a)
                    
                    if hasattr(self,_plugUse) and self.__dict__[_plugUse] and hasattr(self,_plugValue):
                        _value = self.__dict__.get(_plugValue)
                        if _value is not None:
                            if a2 == 'Min':
                                if self.obj.getMayaAttr(_attr) < _value:
                                    self.obj.setMayaAttr(_attr, _value,force=False)                                 
                            else:
                                if self.obj.getMayaAttr(_attr) > _value:
                                    self.obj.setMayaAttr(_attr, _value,force=False)                                 

        if self.debug and self.rotate:
            if not self._debugLoc:
                self._debugLoc = cgmMeta.asMeta(LOC.create(name='debug_loc'))
            self._debugLoc.p_position = self.aimTargetPos
            mc.setKeyframe(self._debugLoc.mNode, at='translate')

            if not self._wantedUpLoc:
                self._wantedUpLoc = cgmMeta.asMeta(LOC.create(name='wanted_up_loc'))
            self._wantedUpLoc.p_position = wantedUp
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
        
        # Calculate the world position where the up vector should point
        self.upTargetPos = self._bakedLoc.p_position + (self._bakedLoc.getTransformDirection(self.aimUp.p_vector) * self.objectScale)
        
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



            








