"""
------------------------------------------
dragger: cgm.tools
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

class Dragger(PostBake.PostBake):
    def __init__(self, obj = None, aimFwd = 'z+', aimUp = 'y+', damp = 7.0, angularDamp=7.0, angularUpDamp=7.0,objectScale=100, rotate=True, translate=True,  cycleState = False, cycleBlend = 5, cycleMode = 'reverseBlend', 
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

        self.aimFwd = VALID.simpleAxis(aimFwd)
        self.aimUp = VALID.simpleAxis(aimUp)

        self.debug = debug
        self._debugLoc = None

        self.damp = damp
        self.angularDamp = angularDamp
        self.angularUpDamp = angularUpDamp
        
        self.translate = translate
        self.rotate = rotate
        
        self.objectScale = objectScale

        self.dir = self.obj.getTransformDirection(self.aimFwd.p_vector)*self.objectScale
        self.aimTargetPos = self.obj.p_position + self.dir

        self.keyableAttrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz']

        self.lastFwd = MATH.Vector3.forward()
        self.lastUp = MATH.Vector3.up()
        
        self.cycleBlend = cycleBlend
        self.cycleState = cycleState
        self.cycleMode = cycleMode
        
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
        

    def update(self, deltaTime=.04):
        #dir = self.obj.getTransformDirection(self.aimFwd.p_vector)

        self.dir = self._bakedLoc.getTransformDirection(self.aimFwd.p_vector)*self.objectScale
        
        if self.translate:
            self.obj.p_position = MATH.Vector3.Lerp(VALID.euclidVector3Arg(self.previousPosition), VALID.euclidVector3Arg(self._bakedLoc.p_position), deltaTime*self.damp)
            
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
                                    self.obj.setMayaAttr(_attr, _value, force=False)
                            else:
                                if self.obj.getMayaAttr(_attr) > _value:
                                    self.obj.setMayaAttr(_attr, _value,force=False)                                 
                        
                       
        if self.rotate:
            wantedTargetPos = ((VALID.euclidVector3Arg(self.obj.p_position) + self.dir) - self.obj.p_position).normalized()*self.objectScale + self.obj.p_position
            
            self.lastUp = MATH.Vector3.Lerp( self.lastUp, self._bakedLoc.getTransformDirection(self.aimUp.p_vector), min(deltaTime * self.angularUpDamp, 1.0) ).normalized()
    
            self.aimTargetPos = (MATH.Vector3.Lerp(self.aimTargetPos, wantedTargetPos, deltaTime*self.angularDamp) - self.obj.p_position).normalized()*self.objectScale + self.obj.p_position
    
            self.lastFwd = MATH.Vector3.Lerp( self.lastFwd, self._bakedLoc.getTransformDirection(self.aimFwd.p_vector), min(deltaTime * self.angularDamp, 1.0) ).normalized()
            
            SNAP.aim_atPoint(obj=self.obj.mNode, mode='local', position=self.aimTargetPos, aimAxis=self.aimFwd.p_string, upAxis=self.aimUp.p_string, vectorUp=self.lastUp )
            
            
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
    
    def preBake(self):
        if not self.bakeTempLocator():
            self.cancelBake()

        self.lastFwd = self._bakedLoc.getTransformDirection(self.aimFwd.p_vector)
        self.lastUp = self._bakedLoc.getTransformDirection(self.aimUp.p_vector)
        
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
        
        self.dir = self.obj.getTransformDirection(self.aimFwd.p_vector)*self.objectScale
        self.aimTargetPos = self.obj.p_position + self.dir



            








