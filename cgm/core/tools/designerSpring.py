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
from cgm.core.lib import math_utils as COREMATH

import maya.cmds as mc
import maya.mel as mel
import pprint
#>>>======================================================================
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
#=========================================================================

'''
def animate_object_position(obj, target, springiness, damp):
    start_frame = mc.playbackOptions(q=True, min=True)
    end_frame = mc.playbackOptions(q=True, max=True)
3
    x = obj.getPosition(asEuclid=1)
    v = euclid.Vector3()

    for frame in range(int(start_frame+1), int(end_frame)+1):
        mc.currentTime(frame, edit=True)
        x,v = spring(x,v,target.getPosition(asEuclid=1),springiness,damp, 1/24.0)

        mc.xform(obj.mNode, t=(x.x,x.y,x.z), ws=True)

obj = cgmMeta.asMeta("pSphere1")
pos = cgmMeta.asMeta("locator1")

animate_object_position(obj, pos, .2, 3*math.pi)
'''
import math
from cgm.core.lib import euclid

class DesignerSpring(PostBake.PostBake):
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
    
        self.springVelocity = MATH.Vector3.zero()
        self.springAimVelocity = MATH.Vector3.zero()
        self.springUpVelocity = MATH.Vector3.zero()
        
        
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
        
        self.previousUpPosition = MATH.Vector3.zero()
        self.previousAimPosition = MATH.Vector3.zero()
        
        
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
        pprint.pprint(vars())
    def update(self, deltaTime=.04):
        #log.info("Updating")
        
        if self.translate:
            x = self.previousPosition#obj.getPosition(asEuclid=1)
            v = self.springVelocity#euclid.Vector3()
            if self.debug:
                print("Before: {},{},{} | {},{},{}".format(x.x,x.y,x.z,v.x,v.y,v.z))
                print("*"*50)            
                print(x)
                print(v)
                print(self._bakedLoc.getPosition(asEuclid=1))
                print(self.springForce)
                print(self.damp*math.pi)    
            
            x,self.springVelocity = COREMATH.spring(x,v,self._bakedLoc.getPosition(asEuclid=1), self.springForce, self.damp*math.pi, deltaTime)#1/24.0)
            if self.debug:print("After: {},{},{} | {},{},{}".format(x.x,x.y,x.z,v.x,v.y,v.z))

            self.obj.p_position = x.x,x.y,x.z

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
            
            
            #Aim -----------------------------------------------------------------------------------
            wantedTargetPos = ((VALID.euclidVector3Arg(self.obj.p_position) + self.dir) - self.obj.p_position).normalized() * self.objectScale + self.obj.p_position
            
            if self.firstFrame :# If our first frame, our wantedTargetPos is good as is...
                x = wantedTargetPos
            else:
                x = self.previousAimPosition#obj.getPosition(asEuclid=1)
                v = self.springAimVelocity#euclid.Vector3()
                
                if self.debug:
                    print("Before: {},{},{} | {},{},{}".format(x.x,x.y,x.z,v.x,v.y,v.z))
                    print("*"*50)            
                    print(x)
                    print(v)
                    print(wantedTargetPos)
                    print(self.angularSpringForce)
                    print(self.angularDamp*math.pi)
                x,self.springAimVelocity = COREMATH.spring(x,v,wantedTargetPos, self.angularSpringForce, self.angularDamp*math.pi, deltaTime)#1/24.0)
                if self.debug:print("After: {},{},{} | {},{},{}".format(x.x,x.y,x.z,v.x,v.y,v.z))            
            self.previousAimPosition = x                
            self.aimTargetPos  = x
            
            
            #Up ------------------------------------------------------------------------------------
            wantedUp = self._bakedLoc.getTransformDirection(self.aimUp.p_vector) * self.objectScale
            
            if self.firstFrame:# If our first frame, our wantedTargetPos is good as is...

                x =wantedUp
            else:
                x = self.previousUpPosition#obj.getPosition(asEuclid=1)
                v = self.springUpVelocity#euclid.Vector3()
                
                if self.debug:
                    print("Before: {},{},{} | {},{},{}".format(x.x,x.y,x.z,v.x,v.y,v.z))
                
                    print("*"*50)            
                    print(x)
                    print(v)
                    print(wantedUp)
                    print(self.angularUpSpringForce)
                    print(self.upDamp*math.pi)            
                
                x,self.springUpVelocity = COREMATH.spring(x,v,wantedUp, self.angularUpSpringForce, self.upDamp*math.pi, deltaTime)#1/24.0)
                if self.debug:print("After: {},{},{} | {},{},{}".format(x.x,x.y,x.z,v.x,v.y,v.z))            
                            
                self.previousUpPosition = x            
                self.upTargetPos  = x
            
            SNAP.aim_atPoint(obj=self.obj.mNode, mode='local', position=self.aimTargetPos, aimAxis=self.aimFwd.p_string, upAxis=self.aimUp.p_string, vectorUp=self.upTargetPos.normalized() )
            
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

            if self.debug:
                if not self._debugLoc:
                    self._debugLoc = cgmMeta.asMeta(LOC.create(name='debug_loc'))
                self._debugLoc.p_position = self.aimTargetPos
                mc.setKeyframe(self._debugLoc.mNode, at='translate')
    
                if not self._wantedUpLoc:
                    self._wantedUpLoc = cgmMeta.asMeta(LOC.create(name='wanted_up_loc'))
                self._wantedUpLoc.p_position = self.obj.p_position + self.upTargetPos
                mc.setKeyframe(self._wantedUpLoc.mNode, at='translate')

            
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



            








