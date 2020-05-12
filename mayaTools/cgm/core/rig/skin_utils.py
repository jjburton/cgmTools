"""
------------------------------------------
skin_utils: cgm.core.rig.skin_utils
Author: Josh Burton
email: jjburton@cgmonks.com
Website : http://www.cgmonks.com
------------------------------------------

"""
# From Python =============================================================
import copy
import re
import time
import pprint

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

# From Maya =============================================================
import maya.cmds as mc
from maya import mel
# From Red9 =============================================================

# From cgm ==============================================================
import cgm.core.cgm_Meta as cgmMeta
import cgm.core.lib.skin_utils as CORESKIN
#reload(CORESKIN)

import cgm.core.lib.list_utils as LISTS
import cgm.core.lib.math_utils as MATH
import cgm.core.lib.distance_utils as DIST
import cgm.core.lib.position_utils as POS

"""
from cgm.core import cgm_General as cgmGEN
from cgm.core.cgmPy import validateArgs as VALID
from cgm.core.lib import shared_data as SHARED
from cgm.core.lib import search_utils as SEARCH
from cgm.core.lib import math_utils as MATH
#reload(DIST)
from cgm.core.lib import position_utils as POS
from cgm.core.lib import euclid as EUCLID
from cgm.core.lib import attribute_utils as ATTR
from cgm.core.lib import name_utils as NAMES
import cgm.core.lib.snap_utils as SNAP
import cgm.core.lib.transform_utils as TRANS
import cgm.core.lib.curve_Utils as CURVES
import cgm.core.lib.list_utils as LISTS
import cgm.core.classes.GuiFactory as cgmUI
"""

#>>> Utilities
#===================================================================  
def surface_copyWeights(sourceSurface, targetSurface):
    """
    First pass on call. Must be same cv lengths for now. Created for ribbon work
    
    """
    _str_func = 'surface_tightenEnds'
    
    def getDat(obj):
        mObj = cgmMeta.asMeta(obj)
        l_cvs = mObj.getComponents('cv')
        ml_skin = mObj.getDeformers(deformerTypes = 'skinCluster',asMeta=True)
        
        return mObj, l_cvs, ml_skin
    
    #Source ---------------------------------------------------------------------------------
    mSource, l_cvsSource, ml_skinSource = getDat(sourceSurface)
    mTarget, l_cvsTarget, ml_skinTarget = getDat(targetSurface)
    

    if len(ml_skinSource) > 1:
        raise ValueError,"Only know how to deal with one skin cluster. Found: {0}".format(ml_skinClusters)
    mSkinSource = ml_skinSource[0]
    mSkinTarget = ml_skinTarget[0]
    
    int_sourceCVs = len(l_cvsSource)
    int_targetCVs = len(l_cvsTarget)
    if int_sourceCVs != int_targetCVs:
        #pprint.pprint(vars)
        raise ValueError, "|{0}| >> cvLens must match".format(_str_func,)
        
    l_influenceSource = CORESKIN.get_influences_fromMatrix(ml_skinSource[0].mNode)
    l_influenceTargets = CORESKIN.get_influences_fromMatrix(ml_skinTarget[0].mNode)
    
    if l_influenceSource != l_influenceTargets:
        pprint.pprint(vars())
        raise ValueError, "|{0}| >> Influence targets don't match".format(_str_func,)    
    
    for i,cv in enumerate(l_cvsSource):
        v = mc.skinPercent(mSkinSource.mNode,cv, q=True, v = True)
        l_v = []
        for ii,o in enumerate(l_influenceTargets):
            l_v.append([o,v[ii]])
            
        mc.skinPercent(mSkinTarget.mNode,
                       l_cvsTarget[i],
                       tv = l_v)
        



def surface_tightenEnds(controlSurface,start = None, end = None,blendLength=3, hardLength = 2,
                        mode = 'twoBlend'):
    """
    
    
    mode
        'twoBlend' - blend between a start and end joint typically. Created for ribbon work
    
    """
    _str_func = 'surface_tightenEnds'
    
    if blendLength<hardLength:
        blendLength=hardLength
    
    mSurface = cgmMeta.asMeta(controlSurface)
    
    l_cvs = mSurface.getComponents('cv')
    ml_skinClusters = mSurface.getDeformers(deformerTypes = 'skinCluster',asMeta=True)
    
    if len(ml_skinClusters) > 1:
        raise ValueError,"Only know how to deal with one skin cluster. Found: {0}".format(ml_skinClusters)
    
    mSkin = ml_skinClusters[0]
    
    #Get our influences --------------------------------------------------
    
    l_influenceObjects = CORESKIN.get_influences_fromCluster(mSkin.mNode)
    
    
    if not mSkin and l_influenceObjects:
        raise StandardError,"controlSurfaceSmoothWeights failed. Not enough info found"
    
    cvStarts = [int(cv.split('[')[-1].split(']')[0]) for cv in l_cvs]
    cvEnds = [int(cv.split('[')[-2].split(']')[0]) for cv in l_cvs]
    #pprint.pprint(vars())
    
    cvStarts = LISTS.get_noDuplicates(cvStarts)
    cvEnds = LISTS.get_noDuplicates(cvEnds)

    #if len{cvEnds)<4:
        #raise StandardError,"Must have enough cvEnds. cvEnds: %s"%(cvEnds)
    if max(cvStarts) > max(cvEnds):
        l_cvsUse = cvStarts
    else:
        l_cvsUse = cvEnds
    
    #if len(l_cvs)<(blendLength + 2):
     #   raise StandardError,"Must have enough cvEnds. blendLength: %s"%(blendLength)

    if mode == 'twoBlend':
        log.debug("|{0}| >> twoBlend mode".format(_str_func))        
        blendLength = len(l_cvsUse) - hardLength
        
    blendFactor = 1.0 / (blendLength+hardLength)
    log.debug("|{0}| >> BlendFactor: {1} | BlendLength: {2}".format(_str_func,blendFactor, blendLength))
        

    if start is None or end is None:
        log.debug("|{0}| >> No start or end. Figuring out one or another".format(_str_func))
        
        if start is None:
            pos_start = POS.get(l_cvs[0])
            start = DIST.get_closestTarget(pos_start,l_influenceObjects)
            log.debug("|{0}| >> No start arg, guessed: {1}".format(_str_func,start))
            
        if end is None:
            pos_end = POS.get(l_cvs[-1])
            end = DIST.get_closestTarget(pos_end,l_influenceObjects)
            log.debug("|{0}| >> No end arg, guessed: {1}".format(_str_func,end))
        

    #>>>Tie down start and ends
    #build our args....
    d_dat = {}
    for influence in [start,end]:
        if influence == start:
            cvBlendEnds = l_cvsUse[:blendLength]
                        
        if influence == end:
            cvBlendEnds = l_cvsUse[-(blendLength):]
            cvBlendEnds.reverse()
            
        log.debug("|{0}| >> Influence: {1} | blendEnds: {2}".format(_str_func,influence,cvBlendEnds))
        
        for i,endInt in enumerate(cvBlendEnds):
            for startInt in cvStarts:
                k = "{0}.cv[{1}][{2}]".format(mSurface.mNode, startInt,endInt)
                if not d_dat.get(k):
                    l = list()                    
                    d_dat[k] = l
                else:
                    l = d_dat[k]
                d = d_dat[k]
                
                if i < hardLength:
                    l.append([influence,1.0])
                else:
                    l.append([influence,MATH.Clamp(1 - ( (i)*blendFactor), 0,1.0,)])
                    #l.append([influence,MATH.Clamp(1 - ( (i-hardLength)*blendFactor), 0,1.0,)])

                    
    #pprint.pprint(vars())
    #pprint.pprint(d_dat)    
    #return        
    for k,dat in d_dat.iteritems():
        #log.debug("|{0}| >> key: {1} | dat: {2}".format(_str_func,k,dat))
        
        l_vs = []
        for i,dat2 in enumerate(dat):
            l_vs.append(dat2[1])
            
        if sum(l_vs)>1.0:
            #log.debug("|{0}| >> before: {1} ".format(_str_func,l_vs))            
            l_vs = MATH.normalizeListToSum(l_vs)
            #log.debug("|{0}| >> after: {1} ".format(_str_func,l_vs))
            
            for i,dat2 in enumerate(dat):
                dat2[1] = l_vs[i]
            
        mc.skinPercent(mSkin.mNode,(k), tv = dat, normalize = 1)
        
    
    """
    for i,endInt in enumerate(cvBlendEnds):
        if i in [0,1]:
            for startInt in cvStarts:
                mc.skinPercent(mSkin.mNode,("%s.cv[%s][%s]"%(mSurface.mNode,startInt,endInt)), tv = [influence,1])

        for startInt in cvStarts:
            mc.skinPercent(mSkin.mNode,("%s.cv[%s][%s]"%(mSurface.mNode,startInt,endInt)),
                           tv = [influence,1-(i*blendFactor)])"""
    
    
    """
    for influence in [start,end]:
        if influence == start:
            cvBlendEnds = cvEnds[:blendLength+2]
                        
        if influence == end:
            cvBlendEnds = cvEnds[-(blendLength+2):]
            cvBlendEnds.reverse()
            
        log.debug("|{0}| >> Influence: {1} | blendEnds: {2}".format(_str_func,influence,cvBlendEnds))
            
            
        for i,endInt in enumerate(cvBlendEnds):
            if i in [0,1]:
                for startInt in cvStarts:
                    mc.skinPercent(mSkin.mNode,("%s.cv[%s][%s]"%(mSurface.mNode,startInt,endInt)), tv = [influence,1])

            for startInt in cvStarts:
                mc.skinPercent(mSkin.mNode,("%s.cv[%s][%s]"%(mSurface.mNode,startInt,endInt)),
                               tv = [influence,1-(i*blendFactor)])"""


def curve_tightenEnds(curve,start = None, end = None,blendLength=3, hardLength = 2, mode = 'twoBlend'):
    """
    
    
    mode
        'twoBlend' - blend between a start and end joint typically. Created for ribbon work
    
    """
    _str_func = 'curve_tightenEnds'
    
    mCurve = cgmMeta.asMeta(curve)
    
    l_cvs = mCurve.getComponents('cv')
    ml_skinClusters = mCurve.getDeformers(deformerTypes = 'skinCluster',asMeta=True)
    
    if len(ml_skinClusters) > 1:
        raise ValueError,"Only know how to deal with one skin cluster. Found: {0}".format(ml_skinClusters)
    
    mSkin = ml_skinClusters[0]
    
    #Get our influences --------------------------------------------------
    
    l_influenceObjects = CORESKIN.get_influences_fromCluster(mSkin.mNode)

    
    if not mSkin and l_influenceObjects:
        raise StandardError,"controlSurfaceSmoothWeights failed. Not enough info found"
    
    l_cvsUse = [int(cv.split('[')[-1].split(']')[0]) for cv in l_cvs]
    #cvEnds = [int(cv.split('[')[-2].split(']')[0]) for cv in l_cvs]
    #pprint.pprint(vars())
    
    l_cvsUse = LISTS.get_noDuplicates(l_cvsUse)
    #cvEnds = LISTS.get_noDuplicates(cvEnds)



    if mode == 'twoBlend':
        log.debug("|{0}| >> twoBlend mode".format(_str_func))        
        blendLength = len(l_cvsUse) - hardLength
        
    blendFactor = 1.0 / (blendLength+hardLength)
    log.debug("|{0}| >> BlendFactor: {1}".format(_str_func,blendFactor))
        
        

    if start is None or end is None:
        log.debug("|{0}| >> No start or end. Figuring out one or another".format(_str_func))
        
        if start is None:
            pos_start = POS.get(l_cvs[0])
            start = DIST.get_closestTarget(pos_start,l_influenceObjects)
            log.warning("|{0}| >> No start arg, guessed: {1}".format(_str_func,start))
            
        if end is None:
            pos_end = POS.get(l_cvs[-1])
            end = DIST.get_closestTarget(pos_end,l_influenceObjects)
            log.warning("|{0}| >> No end arg, guessed: {1}".format(_str_func,end))
        

    #>>>Tie down start and ends
    #build our args....
    d_dat = {}
    for influence in [start,end]:
        if influence == start:
            cvBlendEnds = l_cvsUse[:blendLength]
                        
        if influence == end:
            cvBlendEnds = l_cvsUse[-(blendLength):]
            cvBlendEnds.reverse()
            
        log.debug("|{0}| >> Influence: {1} | blendEnds: {2}".format(_str_func,influence,cvBlendEnds))
        
        for i,cv in enumerate(cvBlendEnds):
            k = "{0}.cv[{1}]".format(mCurve.mNode, cv)
            if not d_dat.get(k):
                l = list()                    
                d_dat[k] = l
            else:
                l = d_dat[k]
                
            d = d_dat[k]
            
            if i < hardLength:
                l.append([influence,1.0])
            else:
                l.append([influence,MATH.Clamp(1 - ( (i)*blendFactor), 0,1.0,)])
                    #l.append([influence,MATH.Clamp(1 - ( (i-hardLength)*blendFactor), 0,1.0,)])

                    
    #pprint.pprint(vars())
    #pprint.pprint(d_dat)    
    #return
    
    for k,dat in d_dat.iteritems():
        #log.debug("|{0}| >> key: {1} | dat: {2}".format(_str_func,k,dat))
        
        l_vs = []
        for i,dat2 in enumerate(dat):
            l_vs.append(dat2[1])
            
        if sum(l_vs)>1.0:
            #log.debug("|{0}| >> before: {1} ".format(_str_func,l_vs))            
            l_vs = MATH.normalizeListToSum(l_vs)
            #log.debug("|{0}| >> after: {1} ".format(_str_func,l_vs))
            
            for i,dat2 in enumerate(dat):
                dat2[1] = l_vs[i]
            
        mc.skinPercent(mSkin.mNode,(k), tv = dat, normalize = 1)