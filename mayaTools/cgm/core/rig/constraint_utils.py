"""
------------------------------------------
constraint_utils: cgm.core.rig
Author: Josh Burton
email: jjburton@cgmonks.com
Website : http://www.cgmonks.com
------------------------------------------


================================================================
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

# From cgm ==============================================================
from cgm.core import cgm_Meta as cgmMeta
from cgm.core import cgm_General as cgmGEN
import cgm.core.lib.snap_utils as SNAP
from cgm.core.lib import curve_Utils as CURVES
from cgm.core.cgmPy import validateArgs as VALID
#from cgm.core.classes import SnapFactory as Snap
from cgm.core.lib import nameTools
from cgm.core.rigger.lib import rig_Utils
from cgm.core.classes import NodeFactory as NodeF
import cgm.core.rig.joint_utils as JOINTS
import cgm.core.lib.attribute_utils as ATTR
import cgm.core.lib.distance_utils as DIST
import cgm.core.lib.constraint_utils as CONSTRAINT
import cgm.core.lib.shape_utils as SHAPES
import cgm.core.lib.node_utils as NODES
import cgm.core.lib.transform_utils as TRANS

def attach_toShape(obj = None, targetShape = None, connectBy = 'parent'):
    """
    :parameters:
        obj - transform to attach
        targetShape(str) - Curve, Nurbs, Mesh
        connectBy(str)
            parent - parent to track transform
            parentGroup - parent to group and have group follow
            conPointGroup - pointConstrain group
            conPointOrientGroup - point/orient constrain group
            conParentGroup - parent Constrain group
            None - just the tracker nodes
    :returns:
        resulting dat

    """   
    try:
        _str_func = 'attach_toShape'
        mObj = cgmMeta.validateObjArg(obj,'cgmObject')
        targetShape = VALID.mNodeString(targetShape)
        
        #Get our data...
        d_closest = DIST.get_closest_point_data(targetShape,
                                                mObj.mNode)
    
        log.debug("|{0}| >> jnt: {1} | {2}".format(_str_func,mObj.mNode, d_closest))
        pprint.pprint(d_closest)
        
        if d_closest['type'] in ['mesh','nurbsSurface']:
            log.debug("|{0}| >> Follicle mode...".format(_str_func))
            _shape = SHAPES.get_nonintermediate(d_closest['shape'] )
            l_follicleInfo = NODES.createFollicleOnMesh( _shape )
            
            i_follicleTrans = cgmMeta.asMeta(l_follicleInfo[1],'cgmObject',setClass=True)
            i_follicleShape = cgmMeta.asMeta(l_follicleInfo[0],'cgmNode')
        
            #> Name...
            i_follicleTrans.doStore('cgmName',mObj.mNode)
            i_follicleTrans.doStore('cgmTypeModifier','surfaceTrack')            
            i_follicleTrans.doName()
            _trackTransform = i_follicleTrans.mNode
            
            #>Set follicle value...
            if d_closest['type'] == 'mesh':
                i_follicleShape.parameterU = d_closest['parameterU']
                i_follicleShape.parameterV = d_closest['parameterV']
            else:
                i_follicleShape.parameterU = d_closest['normalizedU']
                i_follicleShape.parameterV = d_closest['normalizedV']
            _res = [i_follicleTrans.mNode, i_follicleShape.mNode]
        else:
            log.debug("|{0}| >> Curve mode...".format(_str_func))
            #d_returnBuff = distance.returnNearestPointOnCurveInfo(obj,crv)
            _shape = SHAPES.get_nonintermediate(d_closest['shape'] )            
            mPOCI = cgmMeta.cgmNode(nodeType = 'pointOnCurveInfo')
            mc.connectAttr("%s.worldSpace"%_shape,"%s.inputCurve"%mPOCI.mNode)
            mPOCI.parameter = d_closest['parameter']
            
            mTrack = mObj.doCreateAt()
            mTrack.doStore('cgmName',mObj.mNode)
            mTrack.doStore('cgmType','surfaceTrack')
            mTrack.doName()
            
            _trackTransform = mTrack.mNode
            
            mc.connectAttr("%s.position"%mPOCI.mNode,"%s.t"%_trackTransform)
            mPOCI.doStore('cgmName',mObj.mNode)            
            mPOCI.doName()            
            _res = [mTrack.mNode, mPOCI.mNode]
            
        if connectBy is None:
            return _res 
            
        elif connectBy == 'parent':
            mObj.p_parent = _trackTransform
            return _res
        
        elif connectBy == 'parentGroup':
            mGroup = mObj.doGroup(asMeta=True)
            #_grp = TRANS.group_me(obj,True)
            #TRANS.parent_set(_grp,_trackTransform)
            mGroup.p_parent = _trackTransform
            return _res + [mGroup.mNode]        
        elif connectBy == 'conPointGroup':
            mLoc = mObj.doLoc()            
            mLoc.p_parent = _trackTransform
            mGroup = mObj.doGroup(asMeta=True)
            mc.pointConstraint(mLoc.mNode,mGroup.mNode)
            return _res + [mGroup.mNode]        
            
        elif connectBy == 'conPointOrientGroup':
            mLoc = mObj.doLoc()            
            mLoc.p_parent = _trackTransform
            mGroup = mObj.doGroup(asMeta=True)
            
            mc.pointConstraint(mLoc.mNode,mGroup.mNode)
            mc.orientConstraint(mLoc.mNode,mGroup.mNode)
            return _res + [mGroup.mNode]        
            
        elif connectBy == 'conParentGroup':
            mLoc = mObj.doLoc()            
            mLoc.p_parent = _trackTransform
            mGroup = mObj.doGroup(asMeta=True)
            mc.parentConstraint(mLoc.mNode,mGroup.mNode)
            return _res + [mGroup.mNode]        
            
        else:
            raise NotImplementedError,"|{0}| >>invalid connectBy: {1}".format(_str_func,connectBy)  
        
        #pprint.pprint(vars())
    except Exception,err:cgmGEN.cgmException(Exception,err)


def setup_linearSegment(joints = [], skip = ['y','x'],
                        ):
    """
    Should be a joint chain to work properly
    """
    ml_joints = cgmMeta.validateObjListArg(joints,'cgmObject')
    ml_new = []
    mStartHandle = ml_joints[0]
    mEndHandle = ml_joints[-1]

    for mObj in ml_joints[1:-1]:
        mGroup = mObj.doGroup(True,True,asMeta=True,typeModifier = 'twist')
        mObj.parent = False

        _vList = DIST.get_normalizedWeightsByDistance(mGroup.mNode,[mStartHandle.mNode,mEndHandle.mNode])
        _point = mc.pointConstraint([mStartHandle.mNode,mEndHandle.mNode],mGroup.mNode,maintainOffset = False)#Point contraint loc to the object
        _orient = mc.orientConstraint([mStartHandle.mNode,mEndHandle.mNode],mGroup.mNode,
                                      skip = skip,
                                      maintainOffset = False)#Point contraint loc to the object

        for c in [_point,_orient]:
            CONSTRAINT.set_weightsByDistance(c[0],_vList)

        mObj.parent = mGroup

def blendChainsBy(l_jointChain1 = None,
                  l_jointChain2 = None,
                  l_blendChain = None,
                  driver = None,
                  l_constraints = ['point','orient'],
                  maintainOffset = False):
    """
    :parameters:
        l_jointChain1 - First set of objects
        l_jointChain2 - Second set of objects
        
        l_blendChain - blend set 
        driver - Attribute to drive our blend
        l_constraints - constraints to be driven by the setup. Default is ['point','orient']

    :returns:
        
    :raises:
        Exception | if reached

    """
    _str_func = 'blendChainsBy'
    
    d_funcs = {'point':mc.pointConstraint,
               'orient':mc.orientConstraint,
               'scale':mc.scaleConstraint,
               'parent':mc.scaleConstraint}
    
    for c in l_constraints:
        if c not in ['point','orient','scale','parent']:
            log.warning("|{0}| >> Bad constraint arg. Removing: {1}".format(_str_func, c))
            l_constraints.remove(c)
            
    if not l_constraints:
        raise StandardError,"Need valid constraints"
    
    
    ml_jointChain1 = cgmMeta.validateObjListArg(l_jointChain1,'cgmObject',noneValid=False)
    ml_jointChain2 = cgmMeta.validateObjListArg(l_jointChain2,'cgmObject',noneValid=False)
    ml_blendChain = cgmMeta.validateObjListArg(l_blendChain,'cgmObject',noneValid=False)
    d_driver = cgmMeta.validateAttrArg(driver,noneValid=True)
    mi_driver = False
    if d_driver:
        mi_driver = d_driver.get('mi_plug') or False
    else:
        raise ValueError,"Invalid driver: {0}".format(driver)

    if not len(ml_jointChain1) >= len(ml_blendChain) or not len(ml_jointChain2) >= len(ml_blendChain):
        raise StandardError,"Joint chains aren't equal lengths: l_jointChain1: %s | l_jointChain2: %s | l_blendChain: %s"%(len(l_jointChain1),len(l_jointChain2),len(l_blendChain))
    
    pprint.pprint(vars())

    ml_nodes = []

    #>>> Actual meat
    #===========================================================
    for i,i_jnt in enumerate(ml_blendChain):
        for constraint in l_constraints:
            log.debug("connectBlendChainByConstraint>>> %s || %s = %s | %s"%(ml_jointChain1[i].getShortName(),
                                                                             ml_jointChain2[i].getShortName(),
                                                                             ml_blendChain[i].getShortName(),
                                                                             constraint))	    
            i_c = cgmMeta.cgmNode( d_funcs[constraint]([ml_jointChain2[i].getShortName(),ml_jointChain1[i].getShortName()],
                                                       ml_blendChain[i].getShortName(),maintainOffset = maintainOffset)[0])


            targetWeights = d_funcs[constraint](i_c.mNode,q=True, weightAliasList=True)
            if len(targetWeights)>2:
                raise StandardError,"Too many weight targets: obj: %s | weights: %s"%(i_obj.mNode,targetWeights)

            if mi_driver:
                d_blendReturn = NodeF.createSingleBlendNetwork(mi_driver,
                                                               [i_c.mNode,'result_%s_%s'%(constraint,ml_jointChain1[i].getBaseName())],
                                                               [i_c.mNode,'result_%s_%s'%(constraint,ml_jointChain2[i].getBaseName())],
                                                               keyable=True)

                #Connect                                  
                d_blendReturn['d_result1']['mi_plug'].doConnectOut('%s.%s' % (i_c.mNode,targetWeights[0]))
                d_blendReturn['d_result2']['mi_plug'].doConnectOut('%s.%s' % (i_c.mNode,targetWeights[1]))

            ml_nodes.append(i_c)

    d_blendReturn['ml_nodes'] = ml_nodes

    return d_blendReturn


