"""
------------------------------------------
KeyframeToMotionCurve: cgm.tools
Author: David Bokser
email: dbokser@cgmonks.com
Website : http://www.cgmonks.com
------------------------------------------

================================================================
"""

from cgm.core import cgm_Meta as cgmMeta
from cgm.core.lib import math_utils as MATH
from cgm.core.lib import snap_utils as SNAP
from cgm.core.lib import distance_utils as DIST
from cgm.core.cgmPy import validateArgs as VALID
from cgm.core.classes import PostBake as PostBake
import maya.cmds as mc


class KeyframeToMotionCurve(PostBake.PostBake):
    def __init__(self, obj = None, showBake=False, debug=False):
        PostBake.PostBake.__init__(self, obj=obj, showBake=showBake)

        self.keyableAttrs = []

        self.motionCurve = None
        self.motionPath = None

        self.debug = debug

    def update(self, deltaTime=.04):
        d_closest = DIST.get_closest_point_data(self.motionCurve.mNode,self._bakedLoc.mNode)
        self.motionPath.uValue = d_closest['parameter']
        mc.setKeyframe(self.motionPath.mNode, at='uValue', v=d_closest['parameter'])

    def bake(self):
        startTime = int(mc.findKeyframe(self.obj.mNode, which='first'))
        endTime = int(mc.findKeyframe(self.obj.mNode, which='last'))

        PostBake.PostBake.bake(self, startTime, endTime)

    def preBake(self):
        self.bakeTempLocator()

        points = []
        ks = [0]
        k = -1

        mc.refresh(su=not self.showBake)
        for i in range(self.startTime, self.endTime+1):
            mc.currentTime(i)
            points.append(self._bakedLoc.p_position)
            ks.append( min(max(k,0),self.endTime-self.startTime-2) )
            k = k + 1
        mc.refresh(su=False)

        ks.append(ks[-1])

        self.motionCurve = cgmMeta.asMeta(mc.curve(name='motionCurve', d=3, p=points, k=ks))
        mc.rebuildCurve(self.motionCurve.mNode,
                        ch=False, 
                        rpo=True, 
                        rt=0, 
                        end=1, 
                        kr=0, 
                        kcp=1,
                        kep=1, 
                        kt=0, 
                        s=4, 
                        d=3,
                        tol=3.28084e-06)

        mc.cutKey(self.obj.mNode, at=['tx', 'ty', 'tz'], clear=True)

        self.motionPath = cgmMeta.asMeta(mc.pathAnimation(self.obj.mNode, self.motionCurve.mNode, fractionMode=False ,follow =False ,startTimeU=self.startTime, endTimeU=self.endTime))


    def finishBake(self):
        if self._bakedLoc and not self.debug:
            mc.delete(self._bakedLoc.mNode)
            self._bakedLoc = None

        mc.cutKey(self.obj.mNode, at=['tx', 'ty', 'tz'], clear=True)