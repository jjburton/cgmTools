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
log.setLevel(logging.DEBUG)

# From Maya =============================================================
import maya.cmds as mc
from maya import mel
# From Red9 =============================================================

# From cgm ==============================================================
import cgm.core.cgm_Meta as cgmMeta
import cgm.core.lib.skin_utils as CORESKIN
reload(CORESKIN)

import cgm.core.lib.list_utils as LISTS
import cgm.core.lib.math_utils as MATH

"""
from cgm.core import cgm_General as cgmGEN
from cgm.core.cgmPy import validateArgs as VALID
from cgm.core.lib import shared_data as SHARED
from cgm.core.lib import search_utils as SEARCH
from cgm.core.lib import math_utils as MATH
from cgm.core.lib import distance_utils as DIST
reload(DIST)
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
def surface_tightenEnds(controlSurface,start = None, end = None,blendLength=3, hardLength = 2, mode = None):
    _str_func = 'surface_tightenEnds'
    
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

    cvStarts = [int(cv[-5]) for cv in l_cvs]
    cvEnds = [int(cv[-2]) for cv in l_cvs]

    cvStarts = LISTS.get_noDuplicates(cvStarts)
    cvEnds = LISTS.get_noDuplicates(cvEnds)

    #if len{cvEnds)<4:
        #raise StandardError,"Must have enough cvEnds. cvEnds: %s"%(cvEnds)
        
    if len(cvEnds)<(blendLength + 2):
        raise StandardError,"Must have enough cvEnds. blendLength: %s"%(blendLength)	

    blendFactor = 1.0 / (len(cvEnds)-blendLength)
    log.debug("|{0}| >> BlendFactor: {1}".format(_str_func,blendFactor))

    if start is None:
        log.debug("|{0}| >> No start arg, guessing...".format(_str_func,blendFactor))
        start = l_influenceObjects[0]
    if end is None:
        log.debug("|{0}| >> No end arg, guessing...".format(_str_func,blendFactor))
        end = l_influenceObjects[-1]
        

    #>>>Tie down start and ends
    #build our args....
    d_dat = {}
    for influence in [start,end]:
        if influence == start:
            cvBlendEnds = cvEnds[:blendLength+2]
                        
        if influence == end:
            cvBlendEnds = cvEnds[-(blendLength+2):]
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
                    l.append([influence,MATH.Clamp(1 - ( (i-hardLength)*blendFactor), 0,1.0,)])
                    
                    
    #pprint.pprint(vars())
    #pprint.pprint(d_dat)
    
    
            
    for k,dat in d_dat.iteritems():
        log.debug("|{0}| >> key: {1} | dat: {2}".format(_str_func,k,dat))
        
        l_vs = []
        for i,dat2 in enumerate(dat):
            l_vs.append(dat2[1])
            
        if sum(l_vs)>1.0:
            log.debug("|{0}| >> before: {1} ".format(_str_func,l_vs))            
            l_vs = MATH.normalizeListToSum(l_vs)
            log.debug("|{0}| >> after: {1} ".format(_str_func,l_vs))
            
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
