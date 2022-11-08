"""
------------------------------------------
constraint_utils: cgm.core.rig
Author: Josh Burton
email: cgmonks.info@gmail.com
Website : https://github.com/jjburton/cgmTools/wiki
------------------------------------------


================================================================
"""

__MAYALOCAL = 'RIGCONSTRAINTS'

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

# From cgm ==============================================================
from cgm.core import cgm_Meta as cgmMeta
from cgm.core import cgm_General as cgmGEN
import cgm.core.lib.snap_utils as SNAP
from cgm.core.lib import curve_Utils as CURVES
from cgm.core.cgmPy import validateArgs as VALID
#from cgm.core.classes import SnapFactory as Snap
from cgm.core.lib import nameTools
from cgm.core.rigger.lib import rig_Utils
from cgm.core.classes import NodeFactory as NODEFACTORY
import cgm.core.rig.joint_utils as JOINTS
import cgm.core.lib.attribute_utils as ATTR
import cgm.core.lib.distance_utils as DIST
import cgm.core.lib.constraint_utils as CONSTRAINT
import cgm.core.lib.shape_utils as SHAPES
import cgm.core.lib.node_utils as NODES
import cgm.core.lib.transform_utils as TRANS
import cgm.core.lib.list_utils as LISTS
from cgm.core.lib import rigging_utils as CORERIG
from cgm.core.lib import math_utils as MATHUTILS

def attach_toShape(obj = None, targetShape = None, connectBy = 'parent', driver = None, parentTo = None, floating = False):
    """
    :parameters:
        obj - transform to attach
        targetShape(str) - Curve, Nurbs, Mesh
        connectBy(str)
            parent - parent to track transform
            parentGroup - parent to group and have group follow
            conPoint - just point contraint
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
        mDriver = cgmMeta.validateObjArg(driver,'cgmObject',noneValid=True)
        
        targetShape = VALID.mNodeString(targetShape)
        log.debug("targetShape: {0}".format(targetShape))

        #Get our data...
        d_closest = DIST.get_closest_point_data(targetShape,
                                                mObj.mNode)

        log.debug("|{0}| >> jnt: {1} | {2}".format(_str_func,mObj.mNode, d_closest))
        #pprint.pprint(d_closest)
        md_res = {}
        
        if d_closest['type'] in ['mesh','nurbsSurface']:
            log.debug("|{0}| >> Follicle mode...".format(_str_func))
            _shape = SHAPES.get_nonintermediate(d_closest['shape'] )
            log.debug("_shape: {0}".format(_shape))

            l_follicleInfo = NODES.createFollicleOnMesh( _shape )

            i_follicleTrans = cgmMeta.asMeta(l_follicleInfo[1],'cgmObject',setClass=True)
            i_follicleShape = cgmMeta.asMeta(l_follicleInfo[0],'cgmNode')

            #> Name...
            i_follicleTrans.doStore('cgmName',mObj)
            i_follicleTrans.doStore('cgmTypeModifier','surfaceTrack')            
            i_follicleTrans.doName()

            #>Set follicle value...
            if d_closest['type'] == 'mesh':
                i_follicleShape.parameterU = d_closest['parameterU']
                i_follicleShape.parameterV = d_closest['parameterV']
            else:
                i_follicleShape.parameterU = d_closest['normalizedU']
                i_follicleShape.parameterV = d_closest['normalizedV']
                
            if parentTo:
                i_follicleTrans.p_parent = parentTo
                
            _res = [i_follicleTrans.mNode, i_follicleShape.mNode]
            _trackTransform = i_follicleTrans.mNode
            
            md_res['mFollicle'] = i_follicleTrans
            md_res['mFollicleShape'] = i_follicleShape
        else:
            log.debug("|{0}| >> Curve mode...".format(_str_func))
            #d_returnBuff = distance.returnNearestPointOnCurveInfo(obj,crv)
            _shape = SHAPES.get_nonintermediate(d_closest['shape'] )            
            mPOCI = cgmMeta.cgmNode(nodeType = 'pointOnCurveInfo')
            mc.connectAttr("%s.worldSpace"%_shape,"%s.inputCurve"%mPOCI.mNode)
            mPOCI.parameter = d_closest['parameter']
            
            if floating:
                _minU = ATTR.get(_shape,'minValue')
                _maxU = ATTR.get(_shape,'maxValue')
                _param = mPOCI.parameter
                pct = MATHUTILS.get_normalized_parameter(_minU,_maxU,_param)
                log.debug("|{0}| >>  min,max,param,pct | {1},{2},{3},{4} ".format(_str_func,
                                                                                  _minU,
                                                                                  _maxU,
                                                                                  _param,
                                                                                  pct))
                mPOCI.turnOnPercentage = True
                mPOCI.parameter = pct                

            mTrack = mObj.doCreateAt()
            mTrack.doStore('cgmName',mObj)
            mTrack.doStore('cgmType','surfaceTrack')
            mTrack.doName()
            
            
            if parentTo:
                mTrack.p_parent = parentTo
                
            _trackTransform = mTrack.mNode

            mc.connectAttr("%s.position"%mPOCI.mNode,"%s.t"%_trackTransform)
            mPOCI.doStore('cgmName',mObj)            
            mPOCI.doName()
            

                
            _res = [mTrack.mNode, mPOCI.mNode]
            #md_res['mTrack'] = mTrack
            #md_res['mPoci'] = mPOCI            


        if mDriver:
            if d_closest['type'] in ['nurbsSurface']:
                mFollicle = i_follicleTrans
                mFollShape = i_follicleShape
                
                minU = ATTR.get(_shape,'minValueU')
                maxU = ATTR.get(_shape,'maxValueU')
                minV = ATTR.get(_shape,'minValueV')
                maxV = ATTR.get(_shape,'maxValueV')        
        
                mDriverLoc = mDriver.doLoc()
                mc.pointConstraint(mDriver.mNode,mDriverLoc.mNode)
                #mLoc = mObj.doLoc()
                
                str_baseName = "{0}_to_{1}".format(mDriver.p_nameBase, mObj.p_nameBase)
                mPlug_normalizedU = cgmMeta.cgmAttr(mDriverLoc.mNode,
                                                   "{0}_normalizedU".format(str_baseName),
                                                   attrType = 'float',
                                                   hidden = False,
                                                   lock=False)
                mPlug_sumU = cgmMeta.cgmAttr(mDriverLoc.mNode,
                                            "{0}_sumU".format(str_baseName),
                                            attrType = 'float',
                                            hidden = False,
                                            lock=False)
                
                mPlug_normalizedV = cgmMeta.cgmAttr(mDriverLoc.mNode,
                                                   "{0}_normalizedV".format(str_baseName),
                                                   attrType = 'float',
                                                   hidden = False,
                                                   lock=False)
                mPlug_sumV = cgmMeta.cgmAttr(mDriverLoc.mNode,
                                            "{0}_sumV".format(str_baseName),
                                            attrType = 'float',
                                            hidden = False,
                                            lock=False)
                
                #res_closest = DIST.create_closest_point_node(mLoc.mNode, mCrv_reparam.mNode,True)
                log.debug("|{0}| >> Closest info {1}".format(_str_func,_res))
        
                srfNode = mc.createNode('closestPointOnSurface')
                mc.connectAttr("%s.worldSpace[0]" % _shape, "%s.inputSurface" % srfNode)
                mc.connectAttr("%s.translate" % mDriverLoc.mNode, "%s.inPosition" % srfNode)
                #mc.connectAttr("%s.position" % srfNode, "%s.translate" % mLoc.mNode, f=True)
                
                #mClosestPoint =  cgmMeta.validateObjArg(srfNode,setClass=True)
                #mClosestPoint.doStore('cgmName',mObj)
                #mClosestPoint.doName()
                
                log.debug("|{0}| >> paramU {1}.parameterU | {2}".format(_str_func,srfNode,
                                                                        ATTR.get(srfNode,'parameterU')))
                log.debug("|{0}| >> paramV {1}.parameterV | {2}".format(_str_func,srfNode,
                                                                        ATTR.get(srfNode,'parameterV')))
                
        
                l_argBuild = []
                mPlug_uSize = cgmMeta.cgmAttr(mDriverLoc.mNode,
                                              "{0}_uSize".format(str_baseName),
                                              attrType = 'float',
                                              hidden = False,
                                              lock=False)        
                mPlug_vSize = cgmMeta.cgmAttr(mDriverLoc.mNode,
                                              "{0}_vSize".format(str_baseName),
                                              attrType = 'float',
                                              hidden = False,
                                              lock=False)
                
                l_argBuild.append("{0} = {1} - {2}".format(mPlug_vSize.p_combinedName,
                                                           maxV,minV))
                l_argBuild.append("{0} = {1} - {2}".format(mPlug_uSize.p_combinedName,
                                                           maxU,minU))        
                
                l_argBuild.append("{0} = {1} + {2}.parameterU".format(mPlug_sumU.p_combinedName,
                                                                      minU,
                                                                      srfNode))
                
                l_argBuild.append("{0} = {1} / {2}".format(mPlug_normalizedU.p_combinedName,
                                                           mPlug_sumU.p_combinedName,
                                                           mPlug_uSize.p_combinedName))
                
                l_argBuild.append("{0} = {1} + {2}.parameterV".format(mPlug_sumV.p_combinedName,
                                                                      minV,
                                                                      srfNode))
                
                l_argBuild.append("{0} = {1} / {2}".format(mPlug_normalizedV.p_combinedName,
                                                           mPlug_sumV.p_combinedName,
                                                           mPlug_vSize.p_combinedName))        
                
                
                for arg in l_argBuild:
                    log.debug("|{0}| >> Building arg: {1}".format(_str_func,arg))
                    NODEFACTORY.argsToNodes(arg).doBuild()        
                
                ATTR.connect(mPlug_normalizedU.p_combinedShortName,
                             '{0}.parameterU'.format(mFollShape.mNode))
                ATTR.connect(mPlug_normalizedV.p_combinedShortName,
                             '{0}.parameterV'.format(mFollShape.mNode))
                
                
                md_res['mDriverLoc'] = mDriverLoc
                
            elif d_closest['type'] in ['curve','nurbsCurve']:
                mDriverLoc = mDriver.doLoc()
                mc.pointConstraint(mDriver.mNode,mDriverLoc.mNode)
                
                _resClosest = DIST.create_closest_point_node(mDriverLoc.mNode,
                                                             _shape,True) 
                _loc = _resClosest[0]
                

                md_res['mDriverLoc'] = mDriverLoc
                md_res['mDrivenLoc'] = cgmMeta.asMeta(_loc)
                md_res['mTrack'] = mTrack
                
            else:
                log.warning(cgmGEN.logString_msg(_str_func,"Shape type not currently supported for driver setup. Type: {0}".format(d_closest['type'])))
        
        #if connectBy is None:
            #return _res 
        if connectBy == 'parent':
            mObj.p_parent = _trackTransform
        elif connectBy == 'conPoint':
            mc.pointConstraint(_trackTransform, mObj.mNode,maintainOffset = True)
        elif connectBy == 'conParent':
            mc.parentConstraint(_trackTransform, mObj.mNode,maintainOffset = True)
        elif connectBy == 'parentGroup':
            mGroup = mObj.doGroup(asMeta=True)
            #_grp = TRANS.group_me(obj,True)
            #TRANS.parent_set(_grp,_trackTransform)
            mGroup.p_parent = _trackTransform
            _res = _res + [mGroup.mNode]        
        elif connectBy == 'conPointGroup':
            mLoc = mObj.doLoc()            
            mLoc.p_parent = _trackTransform
            mGroup = mObj.doGroup(asMeta=True)
            mc.pointConstraint(mLoc.mNode,mGroup.mNode)
            _res = _res + [mGroup.mNode]        

        elif connectBy == 'conPointOrientGroup':
            mLoc = mObj.doLoc()            
            mLoc.p_parent = _trackTransform
            mGroup = mObj.doGroup(asMeta=True)

            mc.pointConstraint(mLoc.mNode,mGroup.mNode)
            mc.orientConstraint(mLoc.mNode,mGroup.mNode)
            _res = _res + [mGroup.mNode]        

        elif connectBy == 'conParentGroup':
            mLoc = mObj.doLoc()            
            mLoc.p_parent = _trackTransform
            mGroup = mObj.doGroup(asMeta=True)
            mc.parentConstraint(mLoc.mNode,mGroup.mNode)
            _res = _res + [mGroup.mNode]        
        elif connectBy is None:
            pass
        else:
            raise NotImplementedError,"|{0}| >>invalid connectBy: {1}".format(_str_func,connectBy)        
        
        if md_res:
            return _res , md_res
        return _res

        #pprint.pprint(vars())
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err)


    


def driven_disconnect(driven = None, driver = None, mode = 'best'):
    """
    :parameters:
        l_jointChain1 - First set of objects

    :returns:

    :raises:
        Exception | if reached

    """
    _str_func = 'driven_disconnect'
    mDriven = cgmMeta.asMeta(driven)
    _short = mDriven.mNode
    l_drivers = []
    for a in ['tx','ty','tz','rx','ry','rz','sx','sy','sz']:
        l_drivers.append(ATTR.get_driver(_short,a,True))

    l_drivers = LISTS.get_noDuplicates(l_drivers)
    log.debug("|{0}| >> drivers: {1}".format(_str_func,l_drivers))
    mc.delete(l_drivers)

def driven_connect(driven = None, driver = None, mode = 'best'):
    """
    :parameters:
        l_jointChain1 - First set of objects

    :returns:

    :raises:
        Exception | if reached

    """
    _str_func = 'driven_connect'
    mDriven = cgmMeta.asMeta(driven)
    mDriver = cgmMeta.asMeta(driver)

    if mode == 'best':
        mode = 'rigDefault'

    if mode == 'rigDefault':
        mc.pointConstraint(mDriver.mNode,mDriven.mNode,maintainOffset=False,weight=1)
        mc.orientConstraint(mDriver.mNode,mDriven.mNode,maintainOffset=False,weight=1) 
        mc.scaleConstraint(mDriver.mNode,mDriven.mNode,maintainOffset=True,weight=1)#...we do this because sometimes very minor scale values sneak into a rig and this is just easier
    elif mode == 'noScale':
        mc.pointConstraint(mDriver.mNode,mDriven.mNode,maintainOffset=False,weight=1)
        mc.orientConstraint(mDriver.mNode,mDriven.mNode,maintainOffset=False,weight=1)         
    else:
        pprint.pprint(vars())
        raise ValueError,"Unknown mode: {0}".format(mode)



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
                  d_scale = {},
                  d_point = {},
                  d_parent = {},
                  d_orient = {},
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
               'parent':mc.parentConstraint}

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
    d_blendReturn = {}
    mi_driver = False
    if d_driver:
        mi_driver = d_driver.get('mi_plug') or False
    else:
        raise ValueError,"Invalid driver: {0}".format(driver)

    if not len(ml_jointChain1) >= len(ml_blendChain) or not len(ml_jointChain2) >= len(ml_blendChain):
        raise StandardError,"Joint chains aren't equal lengths: l_jointChain1: %s | l_jointChain2: %s | l_blendChain: %s"%(len(l_jointChain1),len(l_jointChain2),len(l_blendChain))

    ml_nodes = []

    #>>> Actual meat ===========================================================
    _creates = []
    for i,i_jnt in enumerate(ml_blendChain):
        log.debug(i_jnt)
        for constraint in l_constraints:
            _d = {}
            if constraint == 'scale':
                _d = d_scale
            """
            log.debug("connectBlendChainByConstraint>>> %s || %s = %s | %s"%(ml_jointChain1[i].mNode,
                                                                             ml_jointChain2[i].mNode,
                                                                             ml_blendChain[i].mNode,
                                                                             constraint))"""
            
            _buff = d_funcs[constraint]([ml_jointChain2[i].mNode,ml_jointChain1[i].mNode],
                                                          ml_blendChain[i].mNode,
                                                          maintainOffset = maintainOffset,**_d)
            
            #func = getattr(mc,'{0}Constraint'.format(constraint))
            #_buff = func([ml_jointChain2[i].mNode,ml_jointChain1[i].mNode],
            #             ml_blendChain[i].mNode,
            #             maintainOffset = maintainOffset,**_d)
            _creates.append(_buff)
            mConst = cgmMeta.cgmNode(_buff[0])

            if constraint in ['parent','orient']:
                mConst.interpType = 2
            
            targetWeights = d_funcs[constraint](mConst.mNode,q=True, weightAliasList=True)
            if len(targetWeights)>2:
                raise StandardError,"Too many weight targets: obj: %s | weights: %s"%(i_jnt.mNode,targetWeights)

            if mi_driver:
                d_blendReturn = NODEFACTORY.createSingleBlendNetwork(mi_driver,
                                                               [mConst.mNode,'result_%s_%s'%(constraint,ml_jointChain1[i].getBaseName())],
                                                               [mConst.mNode,'result_%s_%s'%(constraint,ml_jointChain2[i].getBaseName())],
                                                               keyable=True)

                #Connect                                  
                d_blendReturn['d_result1']['mi_plug'].doConnectOut('%s.%s' % (mConst.mNode,targetWeights[0]))
                d_blendReturn['d_result2']['mi_plug'].doConnectOut('%s.%s' % (mConst.mNode,targetWeights[1]))
            ml_nodes.append(mConst)

    d_blendReturn['ml_nodes'] = ml_nodes
    #pprint.pprint(vars())
    return d_blendReturn


def build_aimSequence(l_driven = None,
                      l_targets = None,
                      l_parents = None,
                      l_upTargets = None,
                      msgLink_masterGroup = 'masterGroup',
                      aim = [0,0,1],
                      up = [0,1,0],
                      mode = 'sequence',#sequence,singleBlend
                      upMode = 'objRotation',#objRotation,decomposeMatrix
                      upParent = [0,1,0],
                      rootTargetEnd = None,
                      rootTargetStart=None,#specify root targets by index and mObj
                      mRoot = None,#need for sequence
                      interpType = None,
                      maintainOffset = False):
    """
    This kind of setup is for setting up a blended constraint so  that obj2 in an obj1/obj2/obj3 sequence can aim forward or back as can obj3.

    :parameters:
        l_jointChain1 - First set of objects

    :returns:

    :raises:
        Exception | if reached

    """
    _str_func = 'build_aimSequence'

    ml_driven = cgmMeta.validateObjListArg(l_driven,'cgmObject')
    ml_targets = cgmMeta.validateObjListArg(l_targets,'cgmObject',noneValid=True)
    ml_parents = cgmMeta.validateObjListArg(l_parents,'cgmObject',noneValid=True)
    ml_upTargets = cgmMeta.validateObjListArg(l_upTargets,'cgmObject',noneValid=True)

    if not ml_upTargets:
        ml_upTargets = ml_parents

    axis_aim = VALID.simpleAxis(aim)
    axis_aimNeg = axis_aim.inverse
    axis_up = VALID.simpleAxis(up)

    v_aim = axis_aim.p_vector#aimVector
    v_aimNeg = axis_aimNeg.p_vector#aimVectorNegative
    v_up = axis_up.p_vector   #upVector

    #cgmGEN.func_snapShot(vars())

    if mode == 'singleBlend':
        if len(ml_targets) != 2:
            cgmGEN.func_snapShot(vars())            
            return log.error("|{0}| >> Single blend mode must have 2 targets.".format(_str_func))
        if len(ml_driven) != 1:
            cgmGEN.func_snapShot(vars())            
            return log.error("|{0}| >> Single blend mode must have 1 driven obj.".format(_str_func))
        if not ml_parents:
            cgmGEN.func_snapShot(vars())            
            return log.error("|{0}| >> Single blend mode must have handleParents.".format(_str_func))
        if len(ml_parents) != 1:
            cgmGEN.func_snapShot(vars())            
            return log.error("|{0}| >> Single blend mode must have 1 handleParent.".format(_str_func))

        mDriven = ml_driven[0]
        if not mDriven.getMessage(msgLink_masterGroup):
            log.debug("|{0}| >> No master group, creating...".format(_str_func))
            raise ValueError, log.error("|{0}| >> Add the create masterGroup setup, Josh".format(_str_func))

        mMasterGroup = mDriven.getMessage(msgLink_masterGroup,asMeta=True)[0]

        s_rootTarget = False
        s_targetForward = ml_targets[-1].mNode
        s_targetBack = ml_targets[0].mNode
        i = 0

        mMasterGroup.p_parent = ml_parents[i]
        mUpDecomp = None

        if upMode == 'decomposeMatrix':
            #Decompose matrix for parent...
            mUpDecomp = cgmMeta.cgmNode(nodeType = 'decomposeMatrix')
            mUpDecomp.rename("{0}_aimMatrix".format(ml_parents[i].p_nameBase))

            #mUpDecomp.doStore('cgmName',ml_parents[i])                
            #mUpDecomp.addAttr('cgmType','aimMatrix',attrType='string',lock=True)
            #mUpDecomp.doName()

            ATTR.connect("{0}.worldMatrix".format(ml_parents[i].mNode),"{0}.{1}".format(mUpDecomp.mNode,'inputMatrix'))
            d_worldUp = {'worldUpObject' : ml_parents[i].mNode,
                         'worldUpType' : 'vector', 'worldUpVector': [0,0,0]}
        elif upMode == 'objectRotation':
            d_worldUp = {'worldUpObject' : ml_parents[i].mNode,
                         'worldUpType' : 'objectRotation', 'worldUpVector': upParent}            
        else:
            raise ValueError, log.error("|{0}| >> Unknown upMode: {1}".format(_str_func,upMode))

        if s_targetForward:
            mAimForward = mDriven.doCreateAt()
            mAimForward.parent = mMasterGroup            
            mAimForward.doStore('cgmTypeModifier','forward')
            mAimForward.doStore('cgmType','aimer')
            mAimForward.doName()

            _const=mc.aimConstraint(s_targetForward, mAimForward.mNode, maintainOffset = True, #skip = 'z',
                                    aimVector = v_aim, upVector = v_up, **d_worldUp)            
            s_targetForward = mAimForward.mNode

            if mUpDecomp:
                ATTR.connect("%s.%s"%(mUpDecomp.mNode,"outputRotate"),"%s.%s"%(_const[0],"upVector"))                 

        else:
            s_targetForward = ml_parents[i].mNode

        if s_targetBack:
            mAimBack = mDriven.doCreateAt()
            mAimBack.parent = mMasterGroup                        
            mAimBack.doStore('cgmTypeModifier','back')
            mAimBack.doStore('cgmType','aimer')
            mAimBack.doName()

            _const = mc.aimConstraint(s_targetBack, mAimBack.mNode, maintainOffset = True, #skip = 'z',
                                      aimVector = v_aimNeg, upVector = v_up, **d_worldUp)  
            s_targetBack = mAimBack.mNode
            if mUpDecomp:
                ATTR.connect("%s.%s"%(mUpDecomp.mNode,"outputRotate"),"%s.%s"%(_const[0],"upVector"))                                     
        else:
            s_targetBack = s_rootTarget
            #ml_parents[i].mNode

        #pprint.pprint([s_targetForward,s_targetBack])
        mAimGroup = mDriven.doGroup(True,asMeta=True,typeModifier = 'aim')

        mDriven.parent = False


        const = mc.orientConstraint([s_targetForward, s_targetBack], mAimGroup.mNode, maintainOffset = True)[0]


        d_blendReturn = NODEFACTORY.createSingleBlendNetwork([mDriven.mNode,'followRoot'],
                                                             [mDriven.mNode,'resultRootFollow'],
                                                             [mDriven.mNode,'resultAimFollow'],
                                                             keyable=True)

        targetWeights = mc.orientConstraint(const,q=True, weightAliasList=True,maintainOffset=True)

        #Connect                                  
        d_blendReturn['d_result1']['mi_plug'].doConnectOut('%s.%s' % (const,targetWeights[0]))
        d_blendReturn['d_result2']['mi_plug'].doConnectOut('%s.%s' % (const,targetWeights[1]))
        d_blendReturn['d_result1']['mi_plug'].p_hidden = True
        d_blendReturn['d_result2']['mi_plug'].p_hidden = True

        mDriven.parent = mAimGroup#...parent back


        mDriven.followRoot = .5        
        return True

    elif mode == 'sequence':
        """
        if len(ml_targets) != 2:
            cgmGEN.func_snapShot(vars())            
            return log.error("|{0}| >> Single blend mode must have 2 targets.".format(_str_func))
        if len(ml_driven) != 1:
            cgmGEN.func_snapShot(vars())            
            return log.error("|{0}| >> Single blend mode must have 1 driven obj.".format(_str_func))
        if not ml_parents:
            cgmGEN.func_snapShot(vars())            
            return log.error("|{0}| >> Single blend mode must have handleParents.".format(_str_func))
        if len(ml_parents) != 1:
            cgmGEN.func_snapShot(vars())            
            return log.error("|{0}| >> Single blend mode must have 1 handleParent.".format(_str_func))
        """


        for i,mDriven in enumerate(ml_driven):
            log.debug("|{0}| >> on: {1} | {2}".format(_str_func,i,mDriven))
            mUpDecomp = False
            if not mDriven.getMessage(msgLink_masterGroup):
                log.debug("|{0}| >> No master group, creating...".format(_str_func))
                raise ValueError, log.error("|{0}| >> Add the create masterGroup setup, Josh".format(_str_func))

            mDriven.masterGroup.parent = ml_parents[i]


            if upMode == 'decomposeMatrix':
                #Decompose matrix for parent...
                mUpDecomp = cgmMeta.cgmNode(nodeType = 'decomposeMatrix')
                mUpDecomp.rename("{0}_aimMatrix".format(ml_parents[i].p_nameBase))

                #mUpDecomp.doStore('cgmName',ml_parents[i])                
                #mUpDecomp.addAttr('cgmType','aimMatrix',attrType='string',lock=True)
                #mUpDecomp.doName()

                ATTR.connect("{0}.worldMatrix".format(ml_upTargets[i].mNode),"{0}.{1}".format(mUpDecomp.mNode,'inputMatrix'))
                d_worldUp = {'worldUpObject' : ml_upTargets[i].mNode,
                             'worldUpType' : 'vector', 'worldUpVector': [0,0,0]}
            elif upMode == 'objectRotation':
                d_worldUp = {'worldUpObject' : ml_upTargets[i].mNode,
                             'worldUpType' : 'objectRotation', 'worldUpVector': upParent}            
            else:
                raise ValueError, log.error("|{0}| >> Unknown upMode: {1}".format(_str_func,upMode))            



            s_rootTarget = False
            s_targetForward = False
            s_targetBack = False
            mMasterGroup = mDriven.masterGroup
            b_first = False
            if mDriven == ml_driven[0]:
                log.debug("|{0}| >> First handle: {1}".format(_str_func,mDriven))
                if len(ml_driven) <=2:
                    s_targetForward = ml_parents[-1].mNode
                else:
                    s_targetForward = ml_driven[i+1].getMessage('masterGroup')[0]

                if rootTargetStart:
                    s_rootTarget = rootTargetStart.mNode
                else:
                    s_rootTarget = mRoot.mNode
                b_first = True

            elif mDriven == ml_driven[-1]:
                log.debug("|{0}| >> Last handle: {1}".format(_str_func,mDriven))
                if rootTargetEnd:
                    s_rootTarget = rootTargetEnd.mNode
                else:
                    s_rootTarget = ml_parents[i].mNode

                s_targetBack = ml_driven[i-1].getMessage('masterGroup')[0]
            else:
                log.debug("|{0}| >> Reg handle: {1}".format(_str_func,mDriven))            
                s_targetForward = ml_driven[i+1].getMessage('masterGroup')[0]
                s_targetBack = ml_driven[i-1].getMessage('masterGroup')[0]

            #Decompose matrix for parent...
            """
            mUpDecomp = cgmMeta.cgmNode(nodeType = 'decomposeMatrix')
            mUpDecomp.doStore('cgmName',ml_parents[i])                
            mUpDecomp.addAttr('cgmType','aimMatrix',attrType='string',lock=True)
            mUpDecomp.doName()

            ATTR.connect("%s.worldMatrix"%(ml_parents[i].mNode),"%s.%s"%(mUpDecomp.mNode,'inputMatrix'))
            """
            if s_targetForward:
                mAimForward = mDriven.doCreateAt()
                mAimForward.parent = mMasterGroup            
                mAimForward.doStore('cgmTypeModifier','forward')
                mAimForward.doStore('cgmType','aimer')
                mAimForward.doName()

                _const=mc.aimConstraint(s_targetForward, mAimForward.mNode, maintainOffset = True, #skip = 'z',
                                        aimVector = v_aim, upVector = v_up,**d_worldUp)            

                s_targetForward = mAimForward.mNode

                if mUpDecomp:
                    ATTR.connect("%s.%s"%(mUpDecomp.mNode,"outputRotate"),"%s.%s"%(_const[0],"upVector"))         
            elif s_rootTarget:
                s_targetForward = s_rootTarget
            else:
                s_targetForward = ml_parents[i].mNode

            if s_targetBack:
                mAimBack = mDriven.doCreateAt()
                mAimBack.parent = mMasterGroup                        
                mAimBack.doStore('cgmTypeModifier','back')
                mAimBack.doStore('cgmType','aimer')
                mAimBack.doName()

                _const = mc.aimConstraint(s_targetBack, mAimBack.mNode, maintainOffset = True, #skip = 'z',
                                          aimVector = v_aimNeg, upVector = v_up, **d_worldUp)  

                s_targetBack = mAimBack.mNode
                if mUpDecomp:
                    ATTR.connect("%s.%s"%(mUpDecomp.mNode,"outputRotate"),"%s.%s"%(_const[0],"upVector"))                         
            else:
                s_targetBack = s_rootTarget
                #ml_parents[i].mNode

            #pprint.pprint([s_targetForward,s_targetBack])
            mAimGroup = mDriven.doGroup(True,asMeta=True,typeModifier = 'aim')

            mDriven.parent = False

            log.debug("|{0}| >> obj: {1} | {2}".format(_str_func,i,mDriven))
            log.debug("|{0}| >> forward: {1}".format(_str_func,s_targetForward))
            log.debug("|{0}| >> back: {1}".format(_str_func,s_targetBack))
            log.debug(cgmGEN._str_subLine)

            if b_first:
                const = mc.orientConstraint([s_targetBack, s_targetForward], mAimGroup.mNode, maintainOffset = True)[0]
            else:
                const = mc.orientConstraint([s_targetForward, s_targetBack], mAimGroup.mNode, maintainOffset = True)[0]


            d_blendReturn = NODEFACTORY.createSingleBlendNetwork([mDriven.mNode,'followRoot'],
                                                                 [mDriven.mNode,'resultRootFollow'],
                                                                 [mDriven.mNode,'resultAimFollow'],
                                                                 keyable=True)
            targetWeights = mc.orientConstraint(const,q=True, weightAliasList=True,maintainOffset=True)

            #Connect                                  
            d_blendReturn['d_result1']['mi_plug'].doConnectOut('%s.%s' % (const,targetWeights[0]))
            d_blendReturn['d_result2']['mi_plug'].doConnectOut('%s.%s' % (const,targetWeights[1]))
            d_blendReturn['d_result1']['mi_plug'].p_hidden = True
            d_blendReturn['d_result2']['mi_plug'].p_hidden = True

            mDriven.parent = mAimGroup#...parent back

            if interpType:
                ATTR.set(const,'interpType',interpType)
            #if mDriven in [ml_driven[0],ml_driven[-1]]:
            #    mDriven.followRoot = 1
            #else:
            mDriven.followRoot = .5
        return True

    raise ValueError,"Not done..."
    return
    for i,mObj in enumerate(ml_driven):


        return


        mObj.masterGroup.parent = ml_parents[i]
        s_rootTarget = False
        s_targetForward = False
        s_targetBack = False
        mMasterGroup = mObj.masterGroup
        b_first = False
        if mObj == ml_driven[0]:
            log.debug("|{0}| >> First handle: {1}".format(_str_func,mObj))
            if len(ml_driven) <=2:
                s_targetForward = ml_parents[-1].mNode
            else:
                s_targetForward = ml_driven[i+1].getMessage('masterGroup')[0]
            s_rootTarget = mRoot.mNode
            b_first = True

        elif mObj == ml_driven[-1]:
            log.debug("|{0}| >> Last handle: {1}".format(_str_func,mObj))
            s_rootTarget = ml_parents[i].mNode                
            s_targetBack = ml_driven[i-1].getMessage('masterGroup')[0]
        else:
            log.debug("|{0}| >> Reg handle: {1}".format(_str_func,mObj))            
            s_targetForward = ml_driven[i+1].getMessage('masterGroup')[0]
            s_targetBack = ml_driven[i-1].getMessage('masterGroup')[0]

        #Decompose matrix for parent...
        mUpDecomp = cgmMeta.cgmNode(nodeType = 'decomposeMatrix')
        mUpDecomp.doStore('cgmName',ml_parents[i])                
        mUpDecomp.addAttr('cgmType','aimMatrix',attrType='string',lock=True)
        mUpDecomp.doName()

        ATTR.connect("%s.worldMatrix"%(ml_parents[i].mNode),"%s.%s"%(mUpDecomp.mNode,'inputMatrix'))

        if s_targetForward:
            mAimForward = mObj.doCreateAt()
            mAimForward.parent = mMasterGroup            
            mAimForward.doStore('cgmTypeModifier','forward')
            mAimForward.doStore('cgmType','aimer')
            mAimForward.doName()

            _const=mc.aimConstraint(s_targetForward, mAimForward.mNode, maintainOffset = True, #skip = 'z',
                                    aimVector = [0,0,1], upVector = [1,0,0], worldUpObject = ml_parents[i].mNode,
                                    worldUpType = 'vector', worldUpVector = [0,0,0])            
            s_targetForward = mAimForward.mNode
            ATTR.connect("%s.%s"%(mUpDecomp.mNode,"outputRotate"),"%s.%s"%(_const[0],"upVector"))                 

        else:
            s_targetForward = ml_parents[i].mNode

        if s_targetBack:
            mAimBack = mObj.doCreateAt()
            mAimBack.parent = mMasterGroup                        
            mAimBack.doStore('cgmTypeModifier','back')
            mAimBack.doStore('cgmType','aimer')
            mAimBack.doName()

            _const = mc.aimConstraint(s_targetBack, mAimBack.mNode, maintainOffset = True, #skip = 'z',
                                      aimVector = [0,0,-1], upVector = [1,0,0], worldUpObject = ml_parents[i].mNode,
                                      worldUpType = 'vector', worldUpVector = [0,0,0])  
            s_targetBack = mAimBack.mNode
            ATTR.connect("%s.%s"%(mUpDecomp.mNode,"outputRotate"),"%s.%s"%(_const[0],"upVector"))                                     
        else:
            s_targetBack = s_rootTarget
            #ml_parents[i].mNode

        #pprint.pprint([s_targetForward,s_targetBack])
        mAimGroup = mObj.doGroup(True,asMeta=True,typeModifier = 'aim')

        mObj.parent = False

        if b_first:
            const = mc.orientConstraint([s_targetBack, s_targetForward], mAimGroup.mNode, maintainOffset = True)[0]
        else:
            const = mc.orientConstraint([s_targetForward, s_targetBack], mAimGroup.mNode, maintainOffset = True)[0]


        d_blendReturn = NODEFACTORY.createSingleBlendNetwork([mObj.mNode,'followRoot'],
                                                             [mObj.mNode,'resultRootFollow'],
                                                             [mObj.mNode,'resultAimFollow'],
                                                             keyable=True)
        targetWeights = mc.orientConstraint(const,q=True, weightAliasList=True,maintainOffset=True)

        #Connect                                  
        d_blendReturn['d_result1']['mi_plug'].doConnectOut('%s.%s' % (const,targetWeights[0]))
        d_blendReturn['d_result2']['mi_plug'].doConnectOut('%s.%s' % (const,targetWeights[1]))
        d_blendReturn['d_result1']['mi_plug'].p_hidden = True
        d_blendReturn['d_result2']['mi_plug'].p_hidden = True

        mObj.parent = mAimGroup#...parent back

        if mObj in [ml_driven[0],ml_driven[-1]]:
            mObj.followRoot = 1
        else:
            mObj.followRoot = .5

d_wiring_l = {'modules':[u'L_feather1_limb', u'L_feather2_limb', u'L_feather3_limb',
                         u'L_feather4_limb', u'L_feather5_limb', u'L_index_limb'],
            'driven':{1:[0,3],
                      2:[0,3],
                      3:[0,5],
                      4:[3,5],
                      }}
d_wiring_r = {'modules':[u'R_feather1_limb', u'R_feather2_limb', u'R_feather3_limb',
                         u'R_feather4_limb', u'R_feather5_limb', u'R_index_limb'],
            'driven':{1:[0,3],
                      2:[0,3],
                      3:[0,5],
                      4:[3,5],
                      }}

d_wiring_r_hawk = {'modules':
                   ['R_feather1_limb_part',
                    'R_feather2_limb_part',
                    'R_feather3_limb_part',
                    'R_feather4_limb_part',
                    'R_feather5_limb_part',
                    'R_index_limb_part'],
                   'driven':{1:[0,3],
                             2:[0,3],
                             3:[0,5],
                             4:[3,5],
                             
                             }}
d_wiring_l_hawk = {'modules':
                   ['L_feather1_limb_part',
                    'L_feather2_limb_part',
                    'L_feather3_limb_part',
                    'L_feather4_limb_part',
                    'L_feather5_limb_part',
                    'L_index_limb_part'],
                   'driven':{1:[0,3],
                             2:[0,3],
                             3:[0,5],
                             4:[3,5],
                             
                             }}
#limbFrameCurve
d_wiring_r_owlWingFrame2 = {'mode':'limbFrameCurve',
                           'orientOnly':True,
                           'name':'wingFrame',
                           'modules':
                           ['R_wing_1_limb_part',
                            'R_wing_2_limb_part',],
'curveDrivers':['R_wingBase_limb_part','R_wingEnd_limb_part'],
'driven':{0:[0,1],
          1:[0,1],
          }}

#Griffon============================================================================================
d_wiring_r_griffonWingFrame = {'mode':'default',
                           'name':'R_feathersFrame',
                           'modules':
                           ['R_wingClav_limb_part',
                            'R_wingBase_limb_part',
                            'R_wing_1_limb_part',
                            'R_wing_2_limb_part'],
'driven':{1:[0,3],
          2:[0,3]
          }}

d_wiring_r_griffon = {'mode':'limbFrameSurface',#'mode':'limbFrameCurve',
                      'modules':
                      ['R_featherUpr_0_segment_part',
                       'R_featherUpr_1_segment_part',#0
                       'R_featherUpr_2_segment_part',#01
                       'R_featherUpr_3_segment_part',#02
                       'R_featherLwr_0_segment_part',#03
                       'R_featherLwr_1_segment_part',#04
                       'R_featherLwr_2_segment_part',#05
                       'R_featherLwr_3_segment_part',#06
                       'R_featherLwr_4_segment_part',#07                       
                       'R_feather_1_segment_part',#08
                       'R_feather_2_segment_part',#09
                       'R_feather_3_segment_part',#10
                       'R_feather_4_segment_part',#11
                       'R_feather_5_segment_part'], #12
'color':range(13),
'name':'R_feathersFrame',
'curveDrivers':['R_wingClav_limb_part',
                'R_wingBase_limb_part',
                'R_wing_1_limb_part', 'R_wing_2_limb_part', 'R_wingEnd_limb_part'],
'driven':{0:[],
          1:[0],
          2:[0,1],
          3:[0,1],
          4:[1],#[0,7],
          5:[1,2],
          6:[1,2],
          7:[1,2],
          8:[1,2],
          9:[2,3],
          10:[2,3],
          11:[2,3],
          12:[2,3],
          13:[3]
          }}

d_wiring_l_griffonWingFrame = {'mode':'default',
                           'name':'L_feathersFrame',
                           'modules':
                           ['L_wingClav_limb_part',
                            'L_wingBase_limb_part',
                            'L_wing_1_limb_part',
                            'L_wing_2_limb_part'],
'driven':{1:[0,3],
          2:[0,3]
          }}

d_wiring_l_griffon = {'mode':'limbFrameSurface',#'mode':'limbFrameCurve',
                      'modules':
                      ['L_featherUpr_0_segment_part',
                       'L_featherUpr_1_segment_part',#0
                       'L_featherUpr_2_segment_part',#01
                       'L_featherUpr_3_segment_part',#02
                       'L_featherLwr_0_segment_part',#03
                       'L_featherLwr_1_segment_part',#04
                       'L_featherLwr_2_segment_part',#05
                       'L_featherLwr_3_segment_part',#06
                       'L_featherLwr_4_segment_part',#07                       
                       'L_feather_1_segment_part',#08
                       'L_feather_2_segment_part',#09
                       'L_feather_3_segment_part',#10
                       'L_feather_4_segment_part',#11
                       'L_feather_5_segment_part'], #12
'color':range(13),
'name':'L_feathersFrame',
'curveDrivers':['L_wingClav_limb_part',
                'L_wingBase_limb_part',
                'L_wing_1_limb_part', 'L_wing_2_limb_part', 'L_wingEnd_limb_part'],
'driven':{0:[],
          1:[0],
          2:[0,1],
          3:[0,1],
          4:[1],#[0,7],
          5:[1,2],
          6:[1,2],
          7:[1,2],
          8:[1,2],
          9:[2,3],
          10:[2,3],
          11:[2,3],
          12:[2,3],
          13:[3]
          }}

#limbFrameCurve=====================================================================================
d_wiring_r_owlWingFrame = {'mode':'default',
                           'name':'R_feathersFrame',
                           'modules':
                           ['R_wingBase_limb_part',
                            'R_wing_1_limb_part',
                            'R_wing_2_limb_part'],
'driven':{1:[0,2],
          }}

d_wiring_r_owl = {'mode':'limbFrameSurface',#'mode':'limbFrameCurve',
                  'modules':
                  ['R_featherUpr_1_segment_part',#0
                   'R_featherUpr_2_segment_part',#01
                   'R_featherUpr_3_segment_part',#02
                   'R_feather_elbow_segment_part',#03
                   'R_featherLwr_1_segment_part',#04
                   'R_featherLwr_2_segment_part',#05
                   'R_featherLwr_3_segment_part',#06
                   'R_feather_1_segment_part',#07
                   'R_feather_2_segment_part',#08
                   'R_feather_3_segment_part',#09
                   'R_feather_4_segment_part',#10
                   'R_feather_5_segment_part'], #11
'color':range(12),
'name':'R_feathersFrame',
'curveDrivers':['R_wingBase_limb_part', 'R_wing_1_limb_part', 'R_wing_2_limb_part', 'R_wingEnd_limb_part'],
'driven':{0:[0],
          1:[0,1],
          2:[0,1],
          3:[1],#[0,7],
          4:[1,2],
          5:[1,2],
          6:[1,2],
          7:[2,3],
          8:[2,3],
          9:[2,3],
          10:[2,3],
          11:[3]
          }}

d_wiring_l_owlWingFrame = {'mode':'default',
                           'name':'L_wingFrame',
                           'modules':
                           ['L_wingBase_limb_part',
                            'L_wing_1_limb_part',
                            'L_wing_2_limb_part'],
                            #'L_wingEnd_limb_part'],
'driven':{1:[0,2],#[0,3]
          #2:[0,3],
          }}

d_wiring_l_owl = {'mode':'limbFrameCurve',
                  'modules':
                  ['L_featherUpr_1_segment_part',#0
                   'L_featherUpr_2_segment_part',#01
                   'L_featherUpr_3_segment_part',#02
                   'L_feather_elbow_segment_part',#03
                   'L_featherLwr_1_segment_part',#04
                   'L_featherLwr_2_segment_part',#05
                   'L_featherLwr_3_segment_part',#06
                   'L_feather_1_segment_part',#07
                   'L_feather_2_segment_part',#08
                   'L_feather_3_segment_part',#09
                   'L_feather_4_segment_part',#10
                   'L_feather_5_segment_part'], #11
'color':range(12),
'name':'L_feathersFrame',
'curveDrivers':['L_wingBase_limb_part', 'L_wing_1_limb_part', 'L_wing_2_limb_part', 'L_wingEnd_limb_part'],
'driven':{0:[0],
          1:[0,1],
          2:[0,1],
          3:[1],#[0,7],
          4:[1,2],
          5:[1,2],
          6:[1,2],
          7:[2,3],
          8:[2,3],
          9:[2,3],
          10:[2,3],
          11:[3]
          }}


#curveAttach
d_wiring_r_owlCurve1 = {'modules':
                  ['R_featherUpr_1_segment_part',#0
                   'R_featherUpr_2_segment_part',#01
                   'R_featherUpr_3_segment_part',#02
                   'R_feather_elbow_segment_part',#03
                   'R_featherLwr_1_segment_part',#04
                   'R_featherLwr_2_segment_part',#05
                   'R_featherLwr_3_segment_part',#06
                   'R_feather_1_segment_part',#07
                   'R_feather_2_segment_part',#08
                   'R_feather_3_segment_part',#09
                   'R_feather_4_segment_part',#10
                   'R_feather_5_segment_part'] #11
,
'color':[1,2,4,5,6,8,9,10],
'curveDrivers':['R_shoulder_seg_anim', 'R_shoulder_segMid_0_ik_anim', 'R_elbow_seg_anim', 'R_elbow_segMid_1_ik_anim', 'R_wrist_seg_anim', 'R_feather_5_root_anim|R_start_fk_anim_master_grp|R_start_fk_anim_dynParentGroup|R_start_fk_anim'],
'driven':{0:[],
          1:[0,3],
          2:[0,3],
          3:[],#[0,7],
          4:[3,7],
          5:[3,7],
          6:[3,7],
          7:[],
          8:[7,11],
          9:[7,11],
          10:[7,11],
          }}

#curveHandles
d_wiring_r_owl2 = {'modules':
                  ['R_featherUpr_1_segment_part',#0
                   'R_featherUpr_2_segment_part',#01
                   'R_featherUpr_3_segment_part',#02
                   'R_feather_elbow_segment_part',#03
                   'R_featherLwr_1_segment_part',#04
                   'R_featherLwr_2_segment_part',#05
                   'R_featherLwr_3_segment_part',#06
                   'R_feather_1_segment_part',#07
                   'R_feather_2_segment_part',#08
                   'R_feather_3_segment_part',#09
                   'R_feather_4_segment_part',#10
                   'R_feather_5_segment_part'] #11
,
'color':[1,2,4,5,6,8,9,10],
'curveDrivers':['joint1', 'joint2', 'joint3', 'joint4'],
'driven':{0:[0],
          1:[0,1],
          2:[0,1],
          3:[1],#[0,7],
          4:[1,2],
          5:[1,2],
          6:[1,2],
          7:[2,3],
          8:[2,3],
          9:[2,3],
          10:[2,3],
          11:[3]
          }}


d_wiring_owlTailFrame = {'mode':'default',
                           #'orientOnly':True,
                           'name':'tailFrame',
                           'modules':
                           ['L_tail_limb_part', 'CTR_tail_limb_part', 'R_tail_limb_part'],
'driven':{1:[0,2],
          }}

d_wiring_owlTail= {'modules':
                  ['L_tailFeather_3_segment_part',#0
                   'L_tailFeather_2_segment_part',#1
                   'L_tailFeather_1_segment_part',#2
                   'CTR_tailFeather_segment_part',#3
                   'R_tailFeather_1_segment_part',#4
                   'R_tailFeather_2_segment_part',#5
                   'R_tailFeather_3_segment_part',#6
                    ],
                   #'mode':'limbFrameCurve',
                   'mode':'limbFrameSurface',
                   'name':'tailFeathersFrame',
                   'color':[0,1,2,4,5,6],
                   'curveDrivers':['L_tail_limb_part', 'CTR_tail_limb_part', 'R_tail_limb_part'],
                   'driven':{0:[0],
                             1:[0,1],
                             2:[0,1],
                             3:[1],
                             4:[1,2],
                             5:[1,2],
                             6:[2],
                             }}


def byDistance(mDriven = None,
               mTargets = None,
               constraint = None,
               maxUse = 2,
               threshold = .001,
               **kws):
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
    _str_func = 'byDistance'
    log.debug(cgmGEN.logString_start(_str_func))
    
    mDriven = cgmMeta.asMeta(mDriven)
    mTargets = cgmMeta.asMeta(mTargets)
    
    l_dat = DIST.get_targetsOrderedByDist(mDriven.mNode,[mObj.mNode for mObj in mTargets])
    if maxUse != None and len(l_dat) > maxUse:
        l_dat = l_dat[:maxUse]
        
    l_dist = []
    l_objs = []
    for s in l_dat:
        l_objs.append(s[0])
        l_dist.append(s[1])
        if l_dist[-1] <= threshold:
            log.info(cgmGEN.logString_msg(_str_func,"Threshold hit: {0}".format(threshold)))
            break
        
    if len(l_objs) > 1:
        vList = MATHUTILS.normalizeListToSum(l_dist,1.0)
        log.info("|{0}| >> targets: {1} ".format(_str_func,l_objs))                     
        log.info("|{0}| >> raw: {1} ".format(_str_func,l_dist))             
        log.info("|{0}| >> normalize: {1} ".format(_str_func,vList))  
        vList = [1.0 - v for v in vList]
        log.info("|{0}| >> normal: {1} ".format(_str_func,vList))
        const = constraint(l_objs,mDriven.mNode, **kws)
        
        CONSTRAINT.set_weightsByDistance(const[0],vList)                
        return const
    else:
        return constraint(l_objs,mDriven.mNode, **kws)
    
    pprint.pprint(l_dist)
    
    
def wing_temp(d_wiring=d_wiring_r, mode = 'limbFrameCurve'):
    """
    mode
        default
        slidingPosition
        driverCurve
        frameCurve
        limbFrameCurve -- expects two joint limb drivers
    """
    try:
        _str_func = 'wing_temp'
        log.debug(cgmGEN.logString_start(_str_func))
        
        ml_roots = []
        ml_parts = []
        ml_rigNulls = []
        ml_blendDrivers = []
        ml_fkEnds = []
        ml_fkStarts = []
        md_toColor = {}
        l_toColor = d_wiring.get('color',[])
        
        name = d_wiring.get('name','NAMEME')
        mode = d_wiring.get('mode',mode)
        
        
        for i,part in enumerate(d_wiring['modules']):
            mPart = cgmMeta.asMeta(part)
            mRigNull = mPart.rigNull
            ml_parts.append(mPart)
            ml_rigNulls.append(mRigNull)
            ml_roots.append(mRigNull.rigRoot)
            ml_joints = mRigNull.msgList_get('blendJoints')
            if not ml_joints:
                for plug in 'fkAttachJoints','fkJoints':
                    ml_test = mRigNull.msgList_get(plug)
                    if ml_test:
                        ml_joints = ml_test
                        break
            ml_blendDrivers.append(ml_joints[0])
            ml_fkEnds.append(ml_joints[-1])
            ml_fkStarts.append(ml_joints[0])
            if i in l_toColor:
                print 'Color'
                mHandleFactory =  mPart.rigBlock.asHandleFactory()
                ml_fkJoints = mRigNull.msgList_get('fkJoints')
                for mJnt in ml_fkJoints:
                    mHandleFactory.color(mJnt.mNode, controlType = 'sub')                
                    
                    
        #Let's make our curve...
        _driverCurve = None
        mEndCrv = None
        
        if mode in ['driverCurve','frameCurve','limbFrameCurve','limbFrameSurface']:
            mGroup = cgmMeta.cgmObject(name="{0}_{1}_grp".format(name,mode))
            
            if mode in ['limbFrameCurve','limbFrameSurface']:
                ml_handles = []
                ml_endHandles = []
                for part in d_wiring['curveDrivers']:
                    mPart = cgmMeta.asMeta(part)
                    mRigNull = mPart.rigNull
                    ml_rigJoints = mRigNull.msgList_get('rigJoints')
                    ml_handles.append(ml_rigJoints[0])
                    ml_endHandles.append(ml_rigJoints[-1])
                    
                l_handles = [mObj.mNode for mObj in ml_handles]
                    
            else:
                l_handles = d_wiring['curveDrivers']
                ml_handles = cgmMeta.asMeta(l_handles)
            
            
            if mode in 'frameCurve':
                _trackCurve,l_clusters = CORERIG.create_at(l_handles, 'linearTrack',baseName = name)
                mCrv = cgmMeta.asMeta(_trackCurve)
                
                #crv = CORERIG.create_at([mObj.mNode for mObj in ml_blendDrivers],'curveLinear')
                #mCrv = cgmMeta.asMeta(crv)
                ml_blendDrivers = cgmMeta.asMeta(d_wiring['curveDrivers']) #suplant the drivers
                
                #End curve
                _trackCurve,l_clusters = CORERIG.create_at([mObj.getChildren()[0] for mObj in ml_handles], 'linearTrack',baseName = name)
                mEndCrv = cgmMeta.asMeta(_trackCurve)
                
                mCrv.p_parent = mGroup
                mEndCrv.p_parent = mGroup

                
            elif mode in ['limbFrameCurve','limbFrameSurface']:
                _trackCurve,l_clusters = CORERIG.create_at([mObj.mNode for mObj in ml_handles], 'linearTrack', baseName = name)
                mCrv = cgmMeta.asMeta(_trackCurve)
                
                _trackCurve,l_clusters = CORERIG.create_at([mObj.mNode for mObj in ml_endHandles], 'linearTrack',baseName = name)
                mEndCrv = cgmMeta.asMeta(_trackCurve)
                
                
                mCrv.p_parent = mGroup
                mEndCrv.p_parent = mGroup                
            else:
            
                _trackCurve,l_clusters = CORERIG.create_at(l_handles, 'linearTrack',baseName = name)
                mCrv = cgmMeta.asMeta(_trackCurve)
                
                
                _node = mc.rebuildCurve(mCrv.mNode, d=3, keepControlPoints=False,
                                        ch=1,s=len(l_handles),
                                        n="{0}_reparamRebuild".format(mCrv.p_nameBase))
                mc.rename(_node[1],"{0}_reparamRebuild".format(mCrv.p_nameBase))
                
                
                mCrv.p_parent = mGroup
                
            _driverCurve = mCrv.mNode
            
            """
            if mEndCrv:
                _node = mc.rebuildCurve(mEndCrv.mNode, d=2, keepControlPoints=False,
                                        ch=1,s=len(l_handles),
                                        n="{0}_end_reparamRebuild".format(name))"""
            
            if mode == 'limbFrameSurface':
                
                _res_body = mc.loft([mCrv.mNode, mEndCrv.mNode], o = True, d = 1, po = 3, c = False,autoReverse=False)
                mLoftSurface = cgmMeta.validateObjArg(_res_body[0],'cgmObject',setClass= True)                    
                _loftNode = _res_body[1]
                _inputs = mc.listHistory(mLoftSurface.mNode,pruneDagObjects=True)
                _rebuildNode = _inputs[0]            
                mLoftSurface = cgmMeta.validateObjArg(_res_body[0],'cgmObject',setClass= True)
                
                #_len = len(targets)*2
                _d = {'keepCorners':False,
                      'rebuildType':0,
                      'degreeU':1,
                      'degreeV':3,
                      'keepControlPoints':False}
                      #'spansU':_len,
                      #'spansV':_len}#General}
                for a,v in _d.iteritems():
                    ATTR.set(_rebuildNode,a,v)
                    
                mLoftSurface.rename("{0}_frameSurface".format(name))
                mLoftSurface.p_parent = mGroup
                
                
        
        #Generate driver locs...
        for d,s in d_wiring['driven'].iteritems():
            mPart = ml_parts[d]
            mRoot = ml_roots[d]
            mRigNull = ml_rigNulls[d]
            mAttach = mRigNull.getMessageAsMeta('attachDriver')
            
            log.info(cgmGEN.logString_sub(_str_func,"{0} | {1}".format(d,s)))
            
            #...loc -----------------------------------------------------------------------
            log.info(cgmGEN.logString_msg(_str_func,'loc...'))
            mLoc = mRoot.getMessageAsMeta('featherDriver')
            if mLoc:
                mLoc.delete()
                
            if mode  == 'frameCurve':
                mLoc = ml_fkStarts[d].doLoc()
            else:
                mLoc = ml_roots[d].doLoc()
            mLoc.rename("{0}_featherLoc".format(mPart.p_nameBase))
            mLoc.p_parent = mRoot.masterGroup.p_parent
            mLoc.v=False
            mLoc.doStore('cgmAlias','feather')
            
            mRoot.connectChildNode(mLoc.mNode,'featherDriver','mPart')
            
            #...drivers ------------------------------------------------------------
            
            if s:
                ml_drivers = [ml_blendDrivers[v] for v in s]
                l_drivers = [mObj.mNode for mObj in ml_drivers]
                _vList = DIST.get_normalizedWeightsByDistance(mLoc.mNode,
                                                              l_drivers)
                
                print ml_drivers
                print l_drivers
                
                if mode  in ['frameCurve','limbFrameCurve','limbFrameSurface']:
                    if not d_wiring.get('orientOnly'):
                        attach_toShape(mLoc.mNode, _driverCurve,'conPoint',parentTo=mGroup)
                    
                    #Aim at and end point
                    mEnd = ml_fkEnds[d]
                    mEndLoc = mEnd.doLoc()#mRigNull.settings.doLoc()
                    mEndLoc.rename("{0}_EndfeatherLoc".format(mPart.p_nameBase))
                    mEndLoc.p_parent = mRoot.masterGroup.p_parent
                    mEndLoc.v=False
                    mEndLoc.doStore('cgmAlias','featherEnd')
                    
                    mEndLoc.p_position = DIST.get_closest_point(mEndLoc.mNode, mEndCrv.mNode)[0]
                    
                    if mode == 'limbFrameSurface':
                        attach_toShape(mEndLoc.mNode, mLoftSurface.mNode,'parent',parentTo=mGroup)
                    else:
                        attach_toShape(mEndLoc.mNode, mEndCrv.mNode,'conPoint',parentTo=mGroup)
                    
                    #made a loc to blend our up
                    """
                    _closest = DIST.get_closestTarget(mLoc.mNode, l_handles)
                    mc.aimConstraint(mEndLoc.mNode, mLoc.mNode,maintainOffset = 0,
                                     aimVector = [0,0,1], upVector = [0,1,0], worldUpObject = _closest,
                                     worldUpType = 'objectrotation', worldUpVector = [0,1,0])"""
                    mStart = ml_fkStarts[d]
                    
                    mUpLoc = mRigNull.settings.doLoc()
                    mUpLoc.rename("{0}_featherAimUpLoc".format(mPart.p_nameBase))
                    mUpLoc.v=False
                    
                    if mode == 'limbFrameSurface':
                        attach_toShape(mUpLoc.mNode, mLoftSurface.mNode,'parent',parentTo=mGroup)
                    else:
                        mUpLoc.p_parent = mRoot.masterGroup.p_parent
                        byDistance(mUpLoc.mNode, l_handles, mc.orientConstraint, maxUse = 2, **{'maintainOffset':1})
                        
                    mc.aimConstraint(mEndLoc.mNode, mLoc.mNode,maintainOffset = 0,
                                     aimVector = [0,0,1], upVector = [0,1,0], worldUpObject = mUpLoc.mNode,
                                     worldUpType = 'objectrotation', worldUpVector = [0,1,0])                    
                    
                else:
                    #_orient = mc.orientConstraint(l_drivers, mLoc.mNode, maintainOffset = 0)
                    _orient = byDistance(mLoc.mNode, l_drivers, mc.orientConstraint, maxUse = 2, **{'maintainOffset':1})
                    
                    l_constraints = [_orient]
                    if mode == 'slidingPosition':
                        _point = mc.pointConstraint(l_drivers, mLoc.mNode, maintainOffset = 0)
                        l_constraints.append(_point)
                    elif _driverCurve:
                        attach_toShape(mLoc.mNode, _driverCurve,'conPoint',parentTo=mGroup)
                    else:
                        _point = mc.pointConstraint(mAttach.mNode, mLoc.mNode, maintainOffset = 1)
                    
                    if len(l_constraints) >1 :
                        for c in l_constraints:
                            CONSTRAINT.set_weightsByDistance(c[0],_vList)
                    
                    ATTR.set(_orient[0],'interpType',2)
            elif _driverCurve:
                attach_toShape(mLoc.mNode, _driverCurve,'conPoint',parentTo=mGroup)
                _closest = DIST.get_closestTarget(mLoc.mNode, l_handles)
                mc.orientConstraint(_closest, mLoc.mNode, maintainOffset=1)
            
            mLoc.dagLock()
            
            mDynGroup = mRoot.dynParentGroup
            mDynGroup.addDynParent(mLoc)
            mDynGroup.rebuild()
            
            _len = len(ATTR.get_enumList(mRoot.mNode,'space'))
            mRoot.space = _len -1
            
            ATTR.set_default(mRoot.mNode,'space', mRoot.space)
            
        #if mode == 'frameCurve':
        #    mc.rebuildCurve(mEndCrv.mNode, d=3, keepControlPoints=False,
        #                    ch=1,s=len(ml_blendDrivers),
        #                    n="{0}_reparamRebuild".format(mEndCrv.p_nameBase))                
        
        return True
    except Exception,err:cgmGEN.cgmException(Exception,err)
    

def baseTalon_tmp(mPart,indices = None):
    mPart = cgmMeta.asMeta(mPart)
    mBlock = mPart.rigBlock

    
    mRigNull = mPart.rigNull
    mRoot = mRigNull.rigRoot
    
    ml_joints = mRigNull.msgList_get('blendJoints')
    if not ml_joints:
        for plug in 'fkAttachJoints','fkJoints':
            ml_test = mRigNull.msgList_get(plug)
            if ml_test:
                ml_joints = ml_test
                break
    #ml_blendDrivers.append(ml_joints[0])
    #ml_fkEnds.append(ml_joints[-1])
    #ml_fkStarts.append(ml_joints[0])
    
    #Find our drivers = 
    mParent = mBlock.blockParent
    mParentModule = mParent.moduleTarget

    ml_targetJoints = mParentModule.rigNull.msgList_get('blendJoints',asMeta = True, cull = True)
    if not ml_targetJoints:
        raise ValueError,"mParentModule has no blend joints."
    
    if indices:
        mTargets = []
        for i in indices:
            mTargets.append(ml_targetJoints[i])
    else:
        _attachPoint = ATTR.get_enumValueString(mBlock.mNode,'attachPoint')
        if _attachPoint == 'end':
            mTargets = ml_targetJoints[-2:]
        elif _attachPoint in ['base','closest']:
            raise ValueError,"can't do base"
        #elif _attachPoint == 'closest':
        #    jnt = DIST.get_closestTarget(ml_targetJoints[0].mNode, [mObj.mNode for mObj in ml_targetJoints])
        #    mTargetJoint = cgmMeta.asMeta(jnt)
        elif _attachPoint == 'index':
            idx = mBlock.attachIndex
            mTargets = ml_targetJoints[idx-1:index]   
        
    #Make our loc ------------------------------------------------------------------
    mLoc = mRoot.doLoc()
    mLoc.rename("{0}_driverLoc".format(mPart.p_nameBase))
    mLoc.p_parent = mTargets[-1]
    mLoc.v=False
    mLoc.doStore('cgmAlias','blendDriver')
    mRoot.connectChildNode(mLoc.mNode,'blendDriver','mPart')
    
    mDriver1 = mLoc.doDuplicate(po=False)
    mDriver2 = mLoc.doDuplicate(po=False)
    
    mDriver1.p_parent = mTargets[0]
    mDriver2.p_parent = mTargets[1]
    
    
    #Constrain and wire --------------------------------------------------------------
    const = mc.orientConstraint([mDriver1.mNode, mDriver2.mNode],
                                mLoc.mNode,
                                maintainOffset=True)[0]
    mConst = cgmMeta.asMeta(const)
    mConst.interpType = 2
    
    mHandle = mRigNull.settings
    #Create Reverse Nodes
    d_blendReturn = NODEFACTORY.createSingleBlendNetwork([mHandle.mNode,
                                                          'blendTrack'],
                                                         [mLoc.mNode,'blendTrack_base'],
                                                         [mLoc.mNode,'blendTrack_end'],
                                                         keyable=True)

    targetWeights = mc.orientConstraint(const,q=True,
                                        weightAliasList=True,
                                        maintainOffset=True)

    #Connetct output of switch attribute to input of W1 of parentConstraint
    d_blendReturn['d_result1']['mi_plug'].doConnectOut('%s.%s' % (const,targetWeights[0]))
    d_blendReturn['d_result2']['mi_plug'].doConnectOut('%s.%s' % (const,targetWeights[1]))
    d_blendReturn['d_result1']['mi_plug'].p_hidden = True
    d_blendReturn['d_result2']['mi_plug'].p_hidden = True

    #Set a deafult value of 0.5 so that the corners are weighted evenly
    ATTR.set_default(mHandle.mNode, 'blendTrack', 0.5)
    mHandle.setMayaAttr('blendTrack', .5)    
    
    #Wire to dynParent Group ------------------------------------------------

    mDynGroup = mRoot.dynParentGroup
    mDynGroup.addDynParent(mLoc)
    mDynGroup.dynMode=2
    mDynGroup.rebuild()
    
    _len = len(ATTR.get_enumList(mRoot.mNode,'orientTo'))
    mRoot.orientTo = _len -1
    
    ATTR.set_default(mRoot.mNode,'orientTo', mRoot.orientTo)
        
    


d_wiring_r_dragonWingFrame = {'mode':'default',
                              'name':'R wingFrame',
                              'modules':
                              ['R_UPR_ring_limb_part',
                               'R_UPR_middle_limb_part',
                               'R_UPR_index_limb_part'],
'color':[1],

'driven':{1:[0,2],
          }}

d_wiring_l_dragonWingFrame = {'mode':'default',
                              'name':'L wingFrame',
                              'modules':
                              ['L_UPR_ring_limb_part',
                               'L_UPR_middle_limb_part',
                               'L_UPR_index_limb_part'],
'color':[1],

'driven':{1:[0,2],
          }}




d_wiring_r_bat= {'mode':'default',
                 'modules':
                   ['R_index_limb_part',
                    'R_middle_limb_part',
                     'R_pinky_limb_part',
                    ],
                 'color':[1],
                   'driven':{1:[0,2],
                             }}
d_wiring_l_bat= {'mode':'default',
                 'modules':
                   ['L_index_limb_part',
                    'L_middle_limb_part',
                    'L_pinky_limb_part',
                    ],
                 'color':[1],
                   'driven':{1:[0,2],
                             }}