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
from cgm.core.lib import attribute_utils as ATTR
from cgm.core import cgm_General as cgmGEN

import cgm.core.classes.GuiFactory as cgmUI

import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

import maya.cmds as mc
import maya.mel as mel

class PostBake(object):
    def __init__(self, obj = None, velocityDamp = 30.0, showBake=False):
        self.obj = None
        self.velocityDamp = velocityDamp
        self.showBake = showBake

        self.velocity = MATH.Vector3.zero()
        self.previousPosition = MATH.Vector3.zero()
        self.startPosition = MATH.Vector3.zero()

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
        _str_func = 'PostBake.bake'

        self._cancelBake = False

        self.startTime = int(mc.playbackOptions(q=True, min=True)) if startTime is None else startTime
        self.endTime = int(mc.playbackOptions(q=True, max=True)) if endTime is None else endTime

        previousStart = mc.playbackOptions(q=True, min=True)
        previousEnd = mc.playbackOptions(q=True, max=True)
        previousCurrent = mc.currentTime(q=True)

        log.info('Baking from {0} to {1}'.format(self.startTime, self.endTime))

        mc.currentTime(self.startTime)

        self.preBake()

        self.setAim(aimFwd = self.aimFwd, aimUp = self.aimUp)

        fps = mel.eval('currentTimeUnitToFPS')
        
        fixedDeltaTime = 1.0/fps

        self.velocity = MATH.Vector3.zero()

        ak = mc.autoKeyframe(q=True, state=True)
        mc.autoKeyframe(state=False)
        mc.refresh(su=not self.showBake)

        _len = self.endTime - self.startTime
        _progressBar = cgmUI.doStartMayaProgressBar(_len,"Processing...")

        completed = True

        if self._cancelBake:
            mc.refresh(su=False)
            mc.autoKeyframe(state=ak)
            return

        for i in range(self.startTime, self.endTime+1):
            mc.currentTime(i)
            
            try:
                self.update(fixedDeltaTime)
            except Exception,err:
                mc.refresh(su=False)
                mc.autoKeyframe(state=ak)
                log.warning('Error on update | {0}'.format(err))   
                cgmGEN.cgmException(Exception,err)
                return

            mc.setKeyframe(self.obj.mNode, at=self.keyableAttrs)
            self.velocity = MATH.Vector3.Lerp(self.velocity, VALID.euclidVector3Arg(self.obj.p_position) - self.previousPosition, min(fixedDeltaTime * self.velocityDamp, 1.0))
            self.previousPosition = VALID.euclidVector3Arg(self.obj.p_position)

            if _progressBar:
                if mc.progressBar(_progressBar, query=True, isCancelled=True ):
                    log.warning('Bake cancelled!')
                    completed = False
                    break
                
                mc.progressBar(_progressBar, edit=True, status = ("{0} On frame {1}".format(_str_func,i)), step=1, maxValue = _len)                    


        mc.refresh(su=False)
        mc.autoKeyframe(state=ak)

        if completed:
            self.finishBake()
        #self.previousPos = self.startPosition
        #self.velocity = MATH.Vector3.zero()

        mc.playbackOptions(e=True, min=previousStart)
        mc.playbackOptions(e=True, max=previousEnd)
        mc.currentTime(previousCurrent)

        cgmUI.doEndMayaProgressBar(_progressBar)

        mc.select(self.obj.mNode)

        return completed

    def preBake(self):
        pass

    def cancelBake(self):
        self._cancelBake = True

    def update(self, deltaTime = .04):
        pass

    def finishBake(self):
        pass

    def setAim(self, aimFwd = None, aimUp = None):
        if aimFwd:
            self.aimFwd = VALID.simpleAxis(aimFwd)

        if aimUp:
            self.aimUp = VALID.simpleAxis(aimUp)

    def bakeTempLocator(self, startTime = None, endTime = None):
        _str_func = 'PostBake.bakeTempLocator'

        if startTime is None:
            startTime = self.startTime
        if endTime is None:
            endTime = self.endTime
        
        ct = mc.currentTime(q=True)

        self._bakedLoc = cgmMeta.asMeta(LOC.create(name='bakeLoc'))
        self._bakedLoc.rotateOrder = self.obj.rotateOrder

        SNAP.matchTarget_set(self._bakedLoc.mNode, self.obj.mNode)

        _len = endTime - startTime
        _progressBar = cgmUI.doStartMayaProgressBar(_len,"Processing...")

        _obj = VALID.objString(self._bakedLoc.mNode, noneValid=False)
        _target = VALID.objString(self.obj.mNode, noneValid=False)#ATTR.get_message(_obj, 'cgmMatchTarget','cgmMatchDat',0)

        ak = mc.autoKeyframe(q=True, state=True)
        mc.autoKeyframe(state=False)
        mc.refresh(su=True)

        completed = True

        for i in range(startTime, endTime+1):
            mc.currentTime(i)
            SNAP.go(_obj,_target,True,True,pivot='rp')
            mc.setKeyframe(_obj, at=['translate', 'rotate'])

            if _progressBar:
                if mc.progressBar(_progressBar, query=True, isCancelled=True ):
                    log.warning('Bake cancelled!')
                    completed = False
                    break
                
                mc.progressBar(_progressBar, edit=True, status = ("{0} On frame {1}".format(_str_func,i)), step=1, maxValue = _len)                    
        
        mc.refresh(su=False)
        mc.autoKeyframe(state=ak)

        cgmUI.doEndMayaProgressBar(_progressBar)

        mc.currentTime(ct)

        return completed

