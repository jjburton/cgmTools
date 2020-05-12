"""
------------------------------------------
segment_utils: cgm.core.rig
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
from cgm.core.classes import NodeFactory as NodeF
import cgm.core.rig.joint_utils as JOINTS
import cgm.core.rig.ik_utils as IK
import cgm.core.lib.distance_utils as DIST
import cgm.core.lib.attribute_utils as ATTR
import cgm.core.lib.name_utils as NAMES
import cgm.core.lib.list_utils as LISTS
import cgm.lib.skinning as OLDSKINNING
#reload(IK)
"""from cgm.lib import (distance,
                     attributes,
                     curves,
                     deformers,
                     lists,
                     rigging,
                     skinning,
                     dictionary,
                     search,
                     nodes,
                     joints,
                     cgmMath)"""   

def create_curveSetup(jointList = None,
                      useCurve = None,
                      orientation = 'zyx',
                      secondaryAxis = 'y+',
                      baseName = None,
                      stretchBy = 'translate',
                      advancedTwistSetup = False,
                      addMidTwist = False,
                      midIndex = None,
                      extendTwistToEnd = False,
                      reorient = False,                      
                      moduleInstance = None,**kws):

    """
    Root of the segment setup.
    Inspiriation from Jason Schleifer's work as well as

    http://faithofthefallen.wordpress.com/2008/10/08/awesome-spine-setup/
    on twist methods.

    Latest rewrite - July 2017

    :parameters:
        jointList(joints - None) | List or metalist of joints
        useCurve(nurbsCurve - None) | Which curve to use. If None. One Created
        orientation(string - zyx) | What is the joints orientation
        secondaryAxis(maya axis arg(y+) | Only necessary when no module provide for orientating
        baseName(string - None) | baseName string
        stretchBy(string - trans) | How the joint will scale
        advancedTwistSetup(bool - False) | Whether to do the cgm advnaced twist setup
        addMidTwist(bool - True) | Whether to setup a mid twist on the segment
        moduleInstance(cgmModule - None) | cgmModule to use for connecting on build
        extendTwistToEnd(bool - False) | Whether to extned the twist to the end by default

    :returns:
        Dict ------------------------------------------------------------------
        'mSegmentCurve'(cgmObject) | segment curve
        'segmentCurve'(str) | segment curve string
        'mIKHandle'(cgmObject) | spline ik Handle
        'mSegmentGroup'(cgmObject) | segment group containing most of the guts
        'l_driverJoints'(list) | list of string driver joint names
        'ml_driverJoints'(metalist) | cgmObject instances of driver joints
        'scaleBuffer'(str) | scale buffer node
        'mi_scaleBuffer'(cgmBufferNode) | scale buffer node for the setup
        'mPlug_extendTwist'(cgmAttr) | extend twist attribute instance
        'l_drivenJoints'(list) | list of string driven joint names
        'ml_drivenJoints'(metalist) | cgmObject instances of driven joints

    :raises:
        Exception | if reached

    """   	 

    _str_func = 'create'
    _res = {}
    
    #>>> Verify =============================================================================================
    log.debug("|{0}| >> Verify...".format(_str_func))                                    
    
    ml_joints = cgmMeta.validateObjListArg(jointList,mType = 'cgmObject', mayaType=['joint'], noneValid = False)
    l_joints = [mJnt.p_nameShort for mJnt in ml_joints]
    int_lenJoints = len(ml_joints)#because it's called repeatedly
    mi_useCurve = cgmMeta.validateObjArg(useCurve,mayaType=['nurbsCurve'],noneValid = True)

    mi_mayaOrientation = VALID.simpleOrientation(orientation)
    str_orientation = mi_mayaOrientation.p_string
    str_secondaryAxis = VALID.stringArg(secondaryAxis,noneValid=True)
    str_baseName = VALID.stringArg(baseName,noneValid=True)
    if kws.get('stretchBy'):
        stretchBy = kws.get('stretchBy')

    str_stretchBy = VALID.stringArg(stretchBy,noneValid=True)		
    b_addMidTwist = VALID.boolArg(addMidTwist)
    b_advancedTwistSetup = VALID.boolArg(advancedTwistSetup)
    b_extendTwistToEnd= VALID.boolArg(extendTwistToEnd)

    if b_addMidTwist and int_lenJoints <4:
        raise ValueError,"must have at least 3 joints for a mid twist setup"
    if int_lenJoints<3:
        raise ValueError,"needs at least three joints"


    #Good way to verify an instance list? #validate orientation             
    #> axis -------------------------------------------------------------
    axis_aim = VALID.simpleAxis("{0}+".format(str_orientation[0]))
    axis_aimNeg = axis_aim.inverse
    axis_up = VALID.simpleAxis("{0}+".format(str_orientation [1]))

    v_aim = axis_aim.p_vector#aimVector
    v_aimNeg = axis_aimNeg.p_vector#aimVectorNegative
    v_up = axis_up.p_vector   #upVector

    outChannel = str_orientation[2]#outChannel
    upChannel = '{0}up'.format(str_orientation[1])#upChannel

    #module -----------------------------------------------------------------------------------------------
    mi_module = cgmMeta.validateObjArg(moduleInstance,noneValid = True)
    try:mi_module.isModule()
    except:mi_module = False

    mi_rigNull = False	
    if mi_module:
        log.debug("|{0}| >> Module found. mi_module: {1}...".format(_str_func,mi_module))                                    
        mi_rigNull = mi_module.rigNull	

        if not str_baseName:
            str_baseName = mi_module.getPartNameBase()#Get part base name	    
            log.debug('baseName set to module: %s'%str_baseName)	    	    
    if not str_baseName:str_baseName = 'testSegmentCurve' 

    #>>> Curve Check ========================================================================================
    if mi_useCurve:#must get a offset u position
        f_MatchPosOffset = CURVES.getUParamOnCurve(ml_joints[0].mNode, mi_useCurve.mNode)
        log.debug("|{0}| >> Use curve mode. uPos: {1}...".format(_str_func,f_MatchPosOffset))                            

    #>> Group ========================================================================================
    mi_grp = cgmMeta.cgmObject(name = 'newgroup')
    mi_grp.addAttr('cgmName', str(str_baseName), lock=True)
    mi_grp.addAttr('cgmTypeModifier','segmentStuff', lock=True)
    mi_grp.doName()

    #>> Orient ========================================================================================
    if reorient:#if it is, we can assume it's right
        log.debug("|{0}| >> reorient mode...".format(_str_func))                                    
        raise NotImplementedError,'Nope'
        JOINTS.orientChain(ml_joints,str_orientation[0]+'+', )
        if str_secondaryAxis is None:
            raise Exception,"Must have secondaryAxis arg if no moduleInstance is passed"
        for mJnt in ml_joints:
            """
            Cannot iterate how important this step is. Lost a day trying to trouble shoot why one joint chain worked and another didn't.
            WILL NOT connect right without this.
            """
            joints.orientJoint(mJnt.mNode,str_orientation,str_secondaryAxis)

    ml_splineRes = []

    #Setup>>> ========================================================================================    
    if b_addMidTwist:#We are gonna do two splineIK chains ---------------------------------------------------------------------
        log.debug("|{0}| >> Midtwist mode...".format(_str_func))                                            

        if not mi_useCurve:
            log.debug("|{0}| >> Creating use curve for midTwist mode...".format(_str_func))                                            
            mi_useCurve = cgmMeta.validateObjArg(CURVES.create_fromList([mJnt.mNode for mJnt in ml_joints]))


        ml_midTwistJoints = [] #exteded list of before and after joints
        
        if midIndex is not None:
            int_mid = midIndex

        else:
            int_mid = int(len(ml_joints)/2)
        #Need to check for even value for this
        if len(ml_joints)%2 == 0:#even
            log.debug("|{0}| >> even...".format(_str_func))                                                
            ml_beforeJoints = ml_joints[:int_mid]
            ml_afterJoints = ml_joints[int_mid:]                          
        else:
            log.debug("|{0}| >> odd...".format(_str_func))                                                
            ml_beforeJoints = ml_joints[:int_mid]
            ml_afterJoints = ml_joints[int_mid:]   

            #Make a duplicate------------------------
            mDup = ml_afterJoints[0].doDuplicate()
            #mDup.parent = ml_joints[int_mid].parent
            mDup.parent = ml_beforeJoints[-1]
            ml_beforeJoints.append(mDup)   

            ml_afterJoints[0].parent = ml_joints[0].parent

        for chain in ml_beforeJoints,ml_afterJoints:            
            _resInline = IK.spline(chain,mi_useCurve,str_orientation,str_secondaryAxis,baseName,str_stretchBy,parentGutsTo=mi_grp)
            ml_splineRes.append(_resInline)
            mIKHandle = _resInline['mIKHandle']
            mSegmentCurve = _resInline['mSplineCurve']

        #SplineIK Twist -----------------------------------------------------------------------------------------------
        mIKHandleFirst = ml_splineRes[0]['mIKHandle']
        mIKHandleMid = ml_splineRes[1]['mIKHandle']
        mIKHandleMid.doStore('cgmTypeModifier','mid')
        mIKHandleMid.doName()
        d_twistReturn = IK.addSplineTwist(mIKHandleFirst.mNode, mIKHandleMid.mNode, b_advancedTwistSetup)

    else:
        log.debug("|{0}| >> single chain...".format(_str_func))                                                        
        _resInline = IK.spline(ml_joints,mi_useCurve,str_orientation,str_secondaryAxis,baseName,str_stretchBy,parentGutsTo=mi_grp)
        ml_splineRes.append(_resInline)
        mIKHandle = _resInline['mIKHandle']
        mSegmentCurve = _resInline['mSplineCurve']
        mSegmentCurve.connectChildNode(mi_grp,'segmentGroup','owner')   

        #SplineIK Twist -----------------------------------------------------------------------------------------------
        d_twistReturn = IK.addSplineTwist(mIKHandle.mNode, None, b_advancedTwistSetup)
        mPlug_twistStart = d_twistReturn['mPlug_start']
        mPlug_twistEnd = d_twistReturn['mPlug_end']
    #Setup<<< ========================================================================================    
    
    
    #Res prep>>> ========================================================================================    
    log.debug("|{0}| >> Result prep...".format(_str_func))                                            
    _res = {'mSegmentCurve':ml_splineRes[0]['mSplineCurve'],
            'ml_joints':ml_joints,
            'mSegmentGroup':mi_grp,
            'mPlug_extendTwist': None,
            'ml_ikHandles':[d['mIKHandle'] for d in ml_splineRes]}
    if b_addMidTwist:
        _res['mIKHandleMid'] = mIKHandleMid
        _res['mIKHandle'] = mIKHandleFirst
    else:
        _res['mIKHandle'] = mIKHandle
               
    return _res


def create(jointList, segmentType = 'curve', 
           influenceJoints = None, startControl = None, endControl = None,
           addSquashStretch = True, addTwist = True,
           useCurve = None,
           stretchBy = 'scale',
           advancedTwistSetup = False,
           additiveScaleSetup = False,
           connectAdditiveScale = False,
           rotateGroupAxis = 'rotateZ',           
           orientation = 'zyx', secondaryAxis = None, controlOrientation = None, baseName = None, moduleInstance = None):
    """
    CGM Joint Segment setup.
    Inspiriation from Jason Schleifer's work as well as http://faithofthefallen.wordpress.com/2008/10/08/awesome-spine-setup/
    on twist methods.

    The general idea is a joint chain with a start control and and end control. Full twist, squash and stretch, additive scale ability

    :parameters:
        jointList(list) | jointList of joints to setup
        influenceJoints(list) | influence joints for setup segment
        addSquashStretch(bool) | whether to setup squash and stretch in the segment
        addTwist(bool)| whether tto setup extra twist control
        startControl(inst/str) | start control object
        startControl(inst/str) | end control object
        segmentType(str) | currently only support 'curve' type.
        rotateGroupAxis(str) | the rotate axis of the rotate group for a twist setup
        secondaryAxis(arg) | pass through command for other functions
        baseName(str) | basename for various naming
        advancedTwistSetup(bool) | pass through command to createCurveSegment
        additiveScaleSetup(bool) | whether to setup additive scale
        connectAdditiveScale(bool) |whether to connect additive scale
        orientation(str) | joint orientation
        controlOrientation(str) |control orientation. Important as it sets which channels will drive twist and additive scale
        moduleInstance(arg) | 

    :returns:
        Dict ------------------------------------------------------------------
    'mAnchorStart'
    'mAnchorStart'
    'mAnchorEnd'
    'mPlug_extendTwist'
    'mmConstraintStartAim'
    'mmConstraintEndAim'
    'mmAimConstraintEnd'
    'mSegmentCurve'(cgmObject) | segment curve
    'segmentCurve'(str) | segment curve string
    'mIKHandle'(cgmObject) | spline ik Handle
    'mSegmentGroup'(cgmObject) | segment group containing most of the guts
    'l_driverJoints'(list) | list of string driver joint names
    'ml_driverJoints'(metalist) | cgmObject instances of driver joints
    'scaleBuffer'(str) | scale buffer node
    'mi_scaleBuffer'(cgmBufferNode) | scale buffer node for the setup
    'mPlug_extendTwist'(cgmAttr) | extend twist attribute instance
    'l_drivenJoints'(list) | list of string driven joint names
    'ml_drivenJoints'(metalist) | cgmObject instances of driven joints

    :raises:
    Exception | if reached

    """      
    _str_func = 'create'

    if segmentType != 'curve':
        raise NotImplementedError,"|{0}| >> Haven't implemented segmentType: {1}".format(_str_func,segmentType)

    #Gather data>>> =====================================================================================
    log.debug("|{0}| >> Data gather...".format(_str_func))                                                        
    #> start/end control -------------------------------------------------------------        
    mStartControl = cgmMeta.validateObjArg(startControl,'cgmObject',noneValid=True)
    mEndControl = cgmMeta.validateObjArg(endControl,'cgmObject',noneValid=True)
    str_baseName = VALID.stringArg(baseName,noneValid=True)

    #> joints -------------------------------------------------------------
    if type(jointList) not in [list,tuple]:jointList = [jointList]
    if len(jointList)<3:
        raise StandardError,"createCGMSegment>>> needs at least three joints"

    ml_influenceJoints = cgmMeta.validateObjListArg(influenceJoints,'cgmObject',noneValid=False,mayaType=['nurbsCurve','joint'])

    try:ml_jointList = cgmMeta.validateObjListArg(jointList,'cgmObject',noneValid=False,mayaType=['nurbsCurve','joint'])
    except Exception,error:
        raise StandardError,"%s >>Joint metaclassing | error : %s"%(_str_func,error)

    #module -----------------------------------------------------------------------------------------------
    mi_module = cgmMeta.validateObjArg(moduleInstance,noneValid = True)
    try:mi_module.isModule()
    except:mi_module = False

    mi_rigNull = False	
    if mi_module:
        log.debug("|{0}| >> Module found. mi_module: {1}...".format(_str_func,mi_module))                                    
        mi_rigNull = mi_module.rigNull	

        if not str_baseName:
            str_baseName = mi_module.getPartNameBase()#Get part base name	    
            log.debug('baseName set to module: %s'%str_baseName)	    	    
    if not str_baseName:str_baseName = 'testSegment' 


    #Good way to verify an instance list? #validate orientation
    #Gather info
    if controlOrientation is None:
        controlOrientation = orientation   

    #> axis -------------------------------------------------------------
    axis_aim = VALID.simpleAxis("%s+"%orientation[0])
    axis_aimNeg = VALID.simpleAxis("%s-"%orientation[0])
    axis_up = VALID.simpleAxis("%s+"%orientation[1])

    aimVector = axis_aim.p_vector
    aimVectorNegative = axis_aimNeg.p_vector
    upVector = axis_up.p_vector   

    outChannel = orientation[2]
    upChannel = '%sup'%orientation[1]

    #> baseDistance -------------------------------------------------------------
    baseDist = DIST.get_distance_between_points(ml_jointList[0].p_position, ml_jointList[-1].p_position)/2
    
    #pprint.pprint(vars())

    #<<<Gather data DONE=====================================================================================


    #Build Transforms>>> =====================================================================================
    log.debug("|{0}| >> Build transforms...".format(_str_func))                                                    
    
    #Start Anchor
    mAnchorStart = ml_jointList[0].doCreateAt()
    mAnchorStart.addAttr('cgmType','anchor',attrType='string',lock=True)
    mAnchorStart.doName()
    mAnchorStart.parent = False  


    #End Anchor
    mAnchorEnd = ml_jointList[-1].doCreateAt()
    mAnchorEnd.addAttr('cgmType','anchor',attrType='string',lock=True)
    mAnchorEnd.doName()    
    mAnchorEnd.parent = False

    #if not mStartControl:mStartControl = mAnchorStart
    #if not mEndControl:mEndControl = mAnchorEnd

    #Build locs --------------------------------------------------------------------------------------
    ml_rigObjects = []
    
    #>>>Aims
    #Start Aim
    mAimStartNull = ml_jointList[0].doCreateAt()
    mAimStartNull.addAttr('cgmType','aim',attrType='string',lock=True)
    mAimStartNull.doName()
    mAimStartNull.parent = mAnchorStart.mNode   
    mAimStartNull.rotateOrder = 0

    #End Aim
    mAimEndNull = ml_jointList[-1].doCreateAt()
    mAimEndNull.addAttr('cgmType','aim',attrType='string',lock=True)
    mAimEndNull.doName()
    mAimEndNull.parent = mAnchorEnd.mNode 
    mAimEndNull.rotateOrder = 0

    #=====================================
    """
    if addTwist:
    #>>>Twist loc
    #Start Aim
    i_twistStartNull = ml_jointList[0].doCreateAt()
    i_twistStartNull.addAttr('cgmType','twist',attrType='string',lock=True)
    i_twistStartNull.doName()
    i_twistStartNull.parent = mAnchorStart.mNode     
    ml_rigObjects.append(i_twistStartNull)

    #End Aim
    i_twistEndNull = ml_jointList[-1].doCreateAt()
    i_twistEndNull.addAttr('cgmType','twist',attrType='string',lock=True)
    i_twistEndNull.doName()
    i_twistEndNull.parent = mAnchorEnd.mNode  
    ml_rigObjects.append(i_twistEndNull)"""

    #>>>Attach ---------------------------------------------------------------------------------------
    #Start Attach
    mAttachStartNull = ml_jointList[0].doCreateAt()
    mAttachStartNull.addAttr('cgmType','attach',attrType='string',lock=True)
    mAttachStartNull.doName()
    mAttachStartNull.parent = mAnchorStart.mNode     

    #End Attach
    mAttachEndtNull = ml_jointList[-1].doCreateAt()
    mAttachEndtNull.addAttr('cgmType','attach',attrType='string',lock=True)
    mAttachEndtNull.doName()
    mAttachEndtNull.parent = mAnchorEnd.mNode  

    #>>>Up locs-----------------------------------------------------------------------------------
    mStartUpNull = ml_jointList[0].doCreateAt()
    mStartUpNull.parent = mAnchorStart.mNode  
    mStartUpNull.addAttr('cgmType','up',attrType='string',lock=True)
    mStartUpNull.doName()
    ml_rigObjects.append(mStartUpNull)
    ATTR.set(mStartUpNull.mNode,'t%s'%orientation[2],baseDist)#We're gonna push these out

    #End
    mEndUpNull = ml_jointList[-1].doCreateAt()
    mEndUpNull.parent = mAnchorEnd.mNode     	
    mEndUpNull.addAttr('cgmType','up',attrType='string',lock=True)
    mEndUpNull.doName()
    ml_rigObjects.append(mEndUpNull)
    ATTR.set(mEndUpNull.mNode,'t%s'%orientation[2],baseDist)#We're gonna push these out

    """"
	#Make our endorient fix
	i_endUpOrientNull = mAnchorEnd.doDuplicateTransform(True)
	i_endUpOrientNull.parent = mAnchorEnd.mNode
	i_endUpOrientNull.addAttr('cgmType','upOrient',attrType='string',lock=True)
	i_endUpOrientNull.doName()
	mEndUpNull.parent = i_endUpOrientNull.mNode   
	mc.orientConstraint(mAnchorStart.mNode,i_endUpOrientNull.mNode,maintainOffset = True, skip = [axis for axis in orientation[:-1]])
	"""
    #Parent the influenceJoints
    ml_influenceJoints[0].parent = mAttachStartNull.mNode
    ml_influenceJoints[-1].parent = mAttachEndtNull.mNode

    #>>>Aim Targets -----------------------------------------------------------------------------
    #Start Aim Target
    mAimStartTargetNull = ml_jointList[-1].doCreateAt()#cgmMeta.cgmObject('uprArm|uprDirect')
    mAimStartTargetNull.addAttr('cgmType','aimTargetStart',attrType='string',lock=True)
    mAimStartTargetNull.doName()
    mAimStartTargetNull.parent = ml_influenceJoints[-1].mNode     
    ml_rigObjects.append(mAimStartTargetNull)

    #End AimTarget
    mAimEndTargetNull = ml_jointList[0].doCreateAt()
    mAimEndTargetNull.addAttr('cgmType','aimTargetEnd',attrType='string',lock=True)
    mAimEndTargetNull.doName()
    mAimEndTargetNull.parent = ml_influenceJoints[0].mNode  
    ml_rigObjects.append(mAimEndTargetNull)

    if mStartControl and not mStartControl.parent:
        log.debug("|{0}| >> Start control and no parent...".format(_str_func))                                                    
        mStartControl.parent = mAttachStartNull.mNode
        mStartControl.doGroup(True)
        mc.makeIdentity(mStartControl.mNode, apply=True,t=1,r=0,s=1,n=0)

        ml_influenceJoints[0].parent = mStartControl.mNode

    if mEndControl and not mEndControl.parent:
        log.debug("|{0}| >> end control and no parent...".format(_str_func))                                                            
        mEndControl.parent = mAttachEndtNull.mNode
        mEndControl.doGroup(True)
        mc.makeIdentity(mEndControl.mNode, apply=True,t=1,r=0,s=1,n=0)	    
        ml_influenceJoints[-1].parent = mEndControl.mNode

    """
	if mModule:#if we have a module, connect vis
	    for i_obj in ml_rigObjects:
		i_obj.overrideEnabled = 1		
		cgmMeta.cgmAttr(mModule.rigNull.mNode,'gutsVis',lock=False).doConnectOut("%s.%s"%(i_obj.mNode,'overrideVisibility'))
		cgmMeta.cgmAttr(mModule.rigNull.mNode,'gutsLock',lock=False).doConnectOut("%s.%s"%(i_obj.mNode,'overrideDisplayType'))    
		"""
    #<<<<Build Transforms DONE=====================================================================================

    #Constrain Nulls>>> =====================================================================================
    log.debug("|{0}| >> Constrain null...".format(_str_func))                                                    
    
    cBuffer = mc.orientConstraint([mAnchorStart.mNode,mAimStartNull.mNode],
                                  mAttachStartNull.mNode,
                                  maintainOffset = True, weight = 1)[0]
    mOrientConstraintStart = cgmMeta.validateObjArg(cBuffer,'cgmNode',setClass=True)
    mOrientConstraintStart.interpType = 0

    cBuffer = mc.orientConstraint([mAnchorEnd.mNode,mAimEndNull.mNode],
                                  mAttachEndtNull.mNode,
                                  maintainOffset = True, weight = 1)[0]
    mOrientConstraintEnd = cgmMeta.validateObjArg(cBuffer,'cgmNode',setClass=True)
    mOrientConstraintEnd.interpType = 0
    #<<< Constrain Nulls DONE =====================================================================================

    #Build constraint blend>>> =====================================================================================
    log.debug("|{0}| >> Constraint blend setup...".format(_str_func))                                                            
    
    #If we don't have our controls by this point, we'll use the joints
    if not mStartControl:
        log.debug("|{0}| >> No startControl. Using joint...".format(_str_func))                                                            
        mStartControl = ml_influenceJoints[0]
    if not mEndControl:
        log.debug("|{0}| >> No end. Using joint...".format(_str_func))                                                            
        mEndControl = ml_influenceJoints[-1]

    #start blend
    d_startFollowBlendReturn = NodeF.createSingleBlendNetwork([mStartControl.mNode,'followRoot'],
                                                              [mStartControl.mNode,'resultRootFollow'],
                                                              [mStartControl.mNode,'resultAimFollow'],
                                                              keyable=True)
    targetWeights = mc.orientConstraint(mOrientConstraintStart.mNode,q=True, weightAliasList=True)
    d_startFollowBlendReturn['d_result1']['mi_plug'].doConnectOut('%s.%s' % (mOrientConstraintStart.mNode,targetWeights[0]))
    d_startFollowBlendReturn['d_result2']['mi_plug'].doConnectOut('%s.%s' % (mOrientConstraintStart.mNode,targetWeights[1]))
    d_startFollowBlendReturn['d_result1']['mi_plug'].p_hidden = True
    d_startFollowBlendReturn['d_result2']['mi_plug'].p_hidden = True

    #EndBlend
    d_endFollowBlendReturn = NodeF.createSingleBlendNetwork([mEndControl.mNode,'followRoot'],
                                                            [mEndControl.mNode,'resultRootFollow'],
                                                            [mEndControl.mNode,'resultAimFollow'],
                                                            keyable=True)
    targetWeights = mc.orientConstraint(mOrientConstraintEnd.mNode,q=True, weightAliasList=True)
    d_endFollowBlendReturn['d_result1']['mi_plug'].doConnectOut('%s.%s' % (mOrientConstraintEnd.mNode,targetWeights[0]))
    d_endFollowBlendReturn['d_result2']['mi_plug'].doConnectOut('%s.%s' % (mOrientConstraintEnd.mNode,targetWeights[1]))
    d_endFollowBlendReturn['d_result1']['mi_plug'].p_hidden = True
    d_endFollowBlendReturn['d_result2']['mi_plug'].p_hidden = True
    #<<<Build constraint blend DONE =====================================================================================

    

    #Build segment>>> =====================================================================================
    log.debug("|{0}| >> Build segment...".format(_str_func))                                                        
    d_segmentBuild = create_curveSetup(jointList, useCurve, orientation,secondaryAxis,
                                       baseName,'scale',advancedTwistSetup, addMidTwist=True,
                                       moduleInstance = mi_module)

    """
    _res = {'mSegmentCurve':ml_splineRes[0]['mSplineCurve'],
            'ml_joints':ml_joints,
            'mSegmentGroup':mi_grp,
            'mPlug_extendTwist': None,
            'ml_ikHandles':[d['mIKHandle'] for d in ml_splineRes]}
    if b_addMidTwist:
        _res['mIKHandleMid'] = mIKHandleMid
        _res['mIKHandle'] = mIKHandleFirst
    else:
        _res['mIKHandle'] = mIKHandle    
    
    """

    mSegmentCurve = d_segmentBuild['mSegmentCurve']
    mSegmentGroup = d_segmentBuild['mSegmentGroup']
    mPlug_extendTwist = d_segmentBuild['mPlug_extendTwist']
    
    
    #Squash stretch ---------------------------------------------------------------------------------------
    if addSquashStretch:
        log.debug("|{0}| >> Squash stretch setup...".format(_str_func))                                                    
        addSquashAndStretch_toCurve(ml_jointList,
                                    stretchBy,
                                    orientation)        
    
    
    if additiveScaleSetup:
        log.debug("|{0}| >> Additive scale setup...".format(_str_func))   
        addAdditveScale_toCurve(ml_jointList,'scale',orientation=orientation)
        log.debug("|{0}| >> Additive scale setup <<<DONE".format(_str_func))   
       
        if connectAdditiveScale:
            l_plugs = ['scaleStartUp','scaleStartOut','scaleEndUp','scaleEndOut']
            for attr in l_plugs: 
                log.info(attr)
                if not mSegmentCurve.hasAttr(attr):
                    mSegmentCurve.select()
                    raise StandardError, "Segment curve missing attr: %s"%attr

            l_attrPrefix = ['Start','End']
            int_runningTally = 0
            for i,i_ctrl in enumerate([mStartControl,mEndControl]):
                log.info("{0} | {1}".format(i,i_ctrl.p_nameShort))
                mPlug_outDriver = cgmMeta.cgmAttr(i_ctrl,"s%s"%controlOrientation[2])
                mPlug_upDriver = cgmMeta.cgmAttr(i_ctrl,"s%s"%controlOrientation[1])
                mPlug_scaleOutDriver = cgmMeta.cgmAttr(i_ctrl,"out_scale%sOutNormal"%l_attrPrefix[i],attrType='float')
                mPlug_scaleUpDriver = cgmMeta.cgmAttr(i_ctrl,"out_scale%sUpNormal"%l_attrPrefix[i],attrType='float')
                mPlug_out_scaleUp = cgmMeta.cgmAttr(i_ctrl,"out_scale%sOutInv"%l_attrPrefix[i],attrType='float')
                mPlug_out_scaleOut = cgmMeta.cgmAttr(i_ctrl,"out_scale%sUpInv"%l_attrPrefix[i],attrType='float')	
                # -1 * (1 - driver)
                arg_up1 = "%s = 1 - %s"%(mPlug_scaleUpDriver.p_combinedShortName,mPlug_upDriver.p_combinedShortName)
                arg_out1 = "%s = 1 - %s"%(mPlug_scaleOutDriver.p_combinedShortName,mPlug_outDriver.p_combinedShortName)
                arg_up2 = "%s = -1 * %s"%(mPlug_out_scaleUp.p_combinedShortName,mPlug_scaleUpDriver.p_combinedShortName)
                arg_out2 = "%s = -1 * %s"%(mPlug_out_scaleOut.p_combinedShortName,mPlug_scaleOutDriver.p_combinedShortName)
                for arg in [arg_up1,arg_out1,arg_up2,arg_out2]:
                    try:
                        NodeF.argsToNodes(arg).doBuild()
                    except Exception,err:
                        raise Exception,"arg fail {0} | error: {1}".format(arg,err)

                mPlug_out_scaleUp.doConnectOut("%s.%s"%(mSegmentCurve.mNode,l_plugs[int_runningTally]))
                int_runningTally+=1
                mPlug_out_scaleOut.doConnectOut("%s.%s"%(mSegmentCurve.mNode,l_plugs[int_runningTally]))	    
                int_runningTally+=1
       
       
    mPlug_twistStart = cgmMeta.cgmAttr(mSegmentCurve.mNode,'twistStart',attrType='float',keyable=True) 
    mPlug_twistEnd = cgmMeta.cgmAttr(mSegmentCurve.mNode,'twistEnd',attrType='float',keyable=True)
    capAim = orientation[0].capitalize()        
 
    if mStartControl:
        if controlOrientation is None:
            mPlug_twistStart.doConnectIn("%s.rotate%s"%(mStartControl.mNode,capAim))
        else:
            mPlug_twistStart.doConnectIn("%s.r%s"%(mStartControl.mNode,controlOrientation[0]))
    if mEndControl:
        if controlOrientation is None:		
            mPlug_twistEnd.doConnectIn("%s.rotate%s"%(mEndControl.mNode,capAim))
        else:
            mPlug_twistEnd.doConnectIn("%s.r%s"%(mEndControl.mNode,controlOrientation[0]))

    #<<<Build segment DONE =====================================================================================
    

    #Skin curve =====================================================================================    
    if mSegmentCurve.getDeformers('skinCluster'):
        log.debug("|{0}| >> Segment curve already skinned...".format(_str_func))                                                    
    elif ml_influenceJoints:#if we have influence joints, we're gonna skin our curve
        log.debug("|{0}| >> Skinning segment curve...".format(_str_func))                                                    
        
        #Surface influence joints cluster#
        mControlSurfaceCluster = cgmMeta.cgmNode(mc.skinCluster ([mJnt.mNode for mJnt in ml_influenceJoints],
                                                                  mSegmentCurve.mNode,
                                                                  tsb=True,
                                                                  maximumInfluences = 3,
                                                                  normalizeWeights = 1,dropoffRate=2.5)[0])

        mControlSurfaceCluster.addAttr('cgmName', baseName, lock=True)
        mControlSurfaceCluster.addAttr('cgmTypeModifier','segmentCurve', lock=True)
        mControlSurfaceCluster.doName()
        """
        if len(ml_influenceJoints) == 2:
        controlCurveSkinningTwoJointBlend(mSegmentCurve.mNode,start = ml_influenceJoints[0].mNode,
                                          end = ml_influenceJoints[-1].mNode,tightLength=1,
                                      blendLength = int(len(jointList)/2))"""
    else:
        log.warning("|{0}| >> Segment Curve not skinned...".format(_str_func))                                                    
    #<<< Skin curve DONE =====================================================================================    


    #Aim constraints >>> =====================================================================================
    log.debug("|{0}| >> aim constraints...".format(_str_func)) 
    
    startAimTarget = mAnchorEnd.mNode
    endAimTarget = mAnchorStart.mNode	
    
    cBuffer = mc.aimConstraint(startAimTarget,
                               mAimStartNull.mNode,
                               maintainOffset = True, weight = 1,
                               aimVector = aimVector,
                               upVector = upVector,
                               worldUpObject = mStartUpNull.mNode,
                               worldUpType = 'object' ) 
    mAimConstraintStart = cgmMeta.asMeta(cBuffer[0],'cgmNode',setClass=True)

    cBuffer = mc.aimConstraint(endAimTarget,
                               mAimEndNull.mNode,
                               maintainOffset = True, weight = 1,
                               aimVector = aimVectorNegative,
                               upVector = upVector,
                               worldUpObject = mEndUpNull.mNode,
                               worldUpType = 'object' ) 
    mAimConstraintEnd = cgmMeta.asMeta(cBuffer[0],'cgmNode',setClass=True)      
    #<<< Aim Constraints DONE =====================================================================================    



    #Store >>> =====================================================================================
    log.debug("|{0}| >> Data connection...".format(_str_func))    
    mSegmentCurve.connectChildNode(mAnchorStart,'anchorStart','segmentCurve')
    mSegmentCurve.connectChildNode(mAnchorEnd,'anchorEnd','segmentCurve')
    mSegmentCurve.connectChildNode(mAttachStartNull,'attachStart','segmentCurve')
    mSegmentCurve.connectChildNode(mAttachEndtNull,'attachEnd','segmentCurve')    
    #<<< Store DONE =====================================================================================    


    #Return >>> =====================================================================================
    log.debug("|{0}| >> Return prep...".format(_str_func)) 
    md_return = {'mSegmentCurve':mSegmentCurve,'mAnchorStart':mAnchorStart,'mAnchorEnd':mAnchorEnd,'mPlug_extendTwist':mPlug_extendTwist,
                 'mmConstraintStartAim':mAimConstraintStart,'mmConstraintEndAim':mAimConstraintEnd}
    for k in d_segmentBuild.keys():
        if k not in md_return.keys():
            md_return[k] = d_segmentBuild[k]#...push to the return dict
    return md_return    
    #<<< Return DONE =====================================================================================    


    #Aim >>> =====================================================================================
    #log.debug("|{0}| >> aim constraints...".format(_str_func))     
    #<<< Aim DONE =====================================================================================    

    return



    try:#Mid influence objects =====================================================================================   
        ml_midObjects = ml_influenceJoints[1:-1] or []
        if len(ml_midObjects)>1:
            raise NotImplementedError,"createCGMSegment>>Haven't implemented having more than one mid influence object in a single chain yet!"
        if ml_midObjects:
            #Create a dup constraint curve
            mConstraintCurve = mSegmentCurve.doDuplicate(po = True)
            mConstraintCurve.addAttr('cgmTypeModifier','constraint')

            #Skin it

            for i_obj in ml_midObjects:
                pass
                #Create group
                #i_midInfluenceGroup = 
                #Attach
                #Make aim groups since one will be aiming backwards
                #Aim
                #AimBlend

    except Exception,error:
        log.error("createCGMSegment>>Extra Influence Object Setup Fail! %s"%[i_obj.getShortName() for i_obj in ml_influenceJoints])
        raise StandardError,error  


def addSquashAndStretch_toCurve(jointList,#attrHolder,#Should be an ikHandle normally, should have attributes and a joint List stored
                                stretchBy = 'scale',
                                orientation = 'zyx'):
    """
    Joint list must have connections to their attr holder ikHandle in this case
    """
    _str_func = 'addSquashAndStretch_toCurve'
     
     #>>> Verify =============================================================================================
    log.debug("|{0}| >> Verify...".format(_str_func))                                    
    
    outChannel = orientation[2].capitalize()
    upChannel = orientation[1].capitalize()
    aimChannel = orientation[0].capitalize()
    
    ml_jointList = cgmMeta.validateObjListArg(jointList,'cgmObject',mayaType= 'joint')
    md_jointToHandle = {}
    mSegmentCurve = None
    for mJnt in ml_jointList:
        if mJnt.getMessage('ikHandle'):
            md_jointToHandle[mJnt] = mJnt.ikHandle
            mSegmentCurve = cgmMeta.validateObjArg( md_jointToHandle[mJnt].segmentCurve )
        else:
            raise ValueError,"|{0}| >> No attr holder data found on joint : {1}...".format(_str_func,mJnt.p_nameShort)
    
    #mAttrHolder = cgmMeta.validateObjArg(attrHolder,'cgmNode',noneValid=False) 
    
    #ml_jointList = mAttrHolder.msgList_get('drivenJoints',asMeta = True)
    #if not ml_jointList:
        #raise ValueError,"|{0}| >> No joint list data found on : {1}...".format(_str_func,mAttrHolder.p_nameShort)
    
    ml_scaleNodes = []
    ml_sqrtNodes = []
    ml_attrs = []
    
    for i,mJnt in enumerate(ml_jointList[:-1]):
        #make sure attr exists
        mAttrHolder = md_jointToHandle[mJnt]
        _attrHolder_short = mAttrHolder.p_nameShort
        mPlug_segmentScale = cgmMeta.cgmAttr(mSegmentCurve,"segmentScaleMult",attrType = 'float',
                                             initialValue=1.0,hidden=False,defaultValue=1.0,keyable=True)	        
        _short = mJnt.p_nameShort
        log.debug("|{0}| >> On: {1}...".format(_str_func,_short))                                    
        
        mAttr = cgmMeta.cgmAttr(mSegmentCurve,"scaleMult_{0}".format(i),attrType = 'float',initialValue=1)
        mPlug_resultScaleMult = cgmMeta.cgmAttr(_attrHolder_short,
                                                "result_scaleMultByFactor_{0}".format(i),
                                                attrType = 'float',hidden=True)

        arg_blendSegFactor = "{0} = {1} * {2}".format(mPlug_resultScaleMult.p_combinedShortName,
                                                      mAttr.p_combinedShortName,
                                                      mPlug_segmentScale.p_combinedShortName)	
        NodeF.argsToNodes(arg_blendSegFactor).doBuild()

        #outScalePlug = attributes.doBreakConnection(_short,"scale%s"%outChannel)
        #upScalePlug = attributes.doBreakConnection(_short,"scale%s"%upChannel)

        if stretchBy == 'translate':
            mainDriver = '{0}.scaleResult_{1}'.format(_attrHolder_short.mNode,(i))
        else:
            mainDriver = '{0}.scale{1}'.format(_short,aimChannel)	
        log.debug("|{0}| >> Main driver: {1}...".format(_str_func,_short))                                    

        #Create the sqrtNode
        mSqrtScale = cgmMeta.cgmNode(nodeType= 'multiplyDivide')
        mSqrtScale.operation = 3#set to power
        mSqrtScale.doStore('cgmName',_short,attrType = 'msg')
        mSqrtScale.addAttr('cgmTypeModifier','sqrtScale')
        mSqrtScale.doName()
        for channel in [outChannel,upChannel]:
            ATTR.connect(mainDriver,#>>
                         '%s.input1%s'%(mSqrtScale.mNode,channel))	    
            mc.setAttr("%s.input2"%(mSqrtScale.mNode)+channel,.5)

        #Create the invScale
        mInvScale = cgmMeta.cgmNode(nodeType= 'multiplyDivide')
        mInvScale.operation = 2
        mInvScale.doStore('cgmName',_short,attrType = 'msg')
        mInvScale.addAttr('cgmTypeModifier','invScale')
        mInvScale.doName()
        for channel in [outChannel,upChannel]:
            mc.setAttr("%s.input1"%(mInvScale.mNode)+channel,1)	    
            ATTR.connect('%s.output%s'%(mSqrtScale.mNode,channel),#>>
                         '%s.input2%s'%(mInvScale.mNode,channel))

        #Create the powScale
        mPowScale = cgmMeta.cgmNode(nodeType= 'multiplyDivide')
        mPowScale.operation = 3
        mPowScale.doStore('cgmName',_short,attrType = 'msg')
        mPowScale.addAttr('cgmTypeModifier','powScale')
        mPowScale.doName()
        for channel in [outChannel,upChannel]:
            ATTR.connect('%s.output%s'%(mInvScale.mNode,channel),#>>
                         '%s.input1%s'%(mPowScale.mNode,channel))
            ATTR.connect('%s'%(mPlug_resultScaleMult.p_combinedName),#>> was mAttr
                                     '%s.input2%s'%(mPowScale.mNode,channel))


        #Connect to joint
        ATTR.connect('%s.output%s'%(mPowScale.mNode,outChannel),#>>
                                 '%s.scale%s'%(_short,outChannel))  
        ATTR.connect('%s.output%s'%(mPowScale.mNode,upChannel),#>>
                                 '%s.scale%s'%(_short,upChannel)) 	

        ml_attrs.append(mAttr)



def addAdditveScale_toCurve(jointList,#attrHolder,#Should be an ikHandle normally, should have attributes and a joint List stored
                            stretchBy = 'scale',
                            orientation = 'zyx'):
    """
    Method for additive scale setup to a cgmSegment. Drivers for out/up should be setup as:
    -1 * ((1-driver1) + (1-driver2)) and connected back to the out/up in's
    """
    _str_func = 'addAdditveScale_toCurve'
     
     #>>> Verify =============================================================================================
    log.debug("|{0}| >> Verify...".format(_str_func))                                    
    
    outChannel = orientation[2].capitalize()
    upChannel = orientation[1].capitalize()
    aimChannel = orientation[0].capitalize()
    
    ml_jointList = cgmMeta.validateObjListArg(jointList,'cgmObject',mayaType= 'joint')
    md_jointToHandle = {}
    segmentCurve = None
    for i,mJnt in enumerate(ml_jointList):
        if mJnt.getMessage('ikHandle'):
            md_jointToHandle[i] = mJnt.ikHandle
            if not segmentCurve:
                segmentCurve = md_jointToHandle[i].getMessage('segmentCurve')
        else:
            raise ValueError,"|{0}| >> No attr holder data found on joint : {1}...".format(_str_func,mJnt.p_nameShort)

    #pprint.pprint(vars())
    mSegmentCurve = cgmMeta.validateObjArg(segmentCurve)
    _short_curve = NAMES.short(mSegmentCurve.mNode)
    
    #Split it out ------------------------------------------------------------------
    log.debug("|{0}| >> Split...".format(_str_func))                                        
    ml_startBlendJoints = ml_jointList[:-1]
    ml_endBlendJoints = ml_jointList[1:]
    ml_endBlendJoints.reverse()#Reverse it
    ml_midBlendJoints = ml_jointList[1:-1]
    
    #=====================================================================================================
    #Declare our attrs
    log.debug("|{0}| >> declare out main attrs...".format(_str_func))                                            
    mPlug_in_startUp = cgmMeta.cgmAttr(_short_curve,"scaleStartUp",attrType = 'float',lock=False,keyable=True,hidden=False)
    mPlug_in_startOut = cgmMeta.cgmAttr(_short_curve,"scaleStartOut",attrType = 'float',lock=False,keyable=True,hidden=False)               
    mPlug_in_endUp = cgmMeta.cgmAttr(_short_curve,"scaleEndUp",attrType = 'float',lock=False,keyable=True,hidden=False)
    mPlug_in_endOut = cgmMeta.cgmAttr(_short_curve,"scaleEndOut",attrType = 'float',lock=False,keyable=True,hidden=False)               
    mPlug_in_midUp = cgmMeta.cgmAttr(_short_curve,"scaleMidUp",attrType = 'float',lock=False,keyable=True,hidden=False)
    mPlug_in_midOut = cgmMeta.cgmAttr(_short_curve,"scaleMidOut",attrType = 'float',lock=False,keyable=True,hidden=False)               
    
    #>> Let's do the blend ===============================================================
    #Get our factors ------------------------------------------------------------------
    fl_factor = 1.0/len(ml_startBlendJoints)
    log.debug("|{0}| >> factoring ({1})...".format(_str_func, fl_factor))                                                
    
    dPlugs_startUps = {}
    dPlugs_startOuts = {}
    dPlugs_endUps = {}
    dPlugs_endOuts = {}
    dPlugs_midUps = {}
    dPlugs_midOuts = {}

    for i,mJnt in enumerate(ml_startBlendJoints):#We need out factors for start and end up and outs, let's get em
        mAttrHolder = md_jointToHandle[i]
        attrHolder_short = mAttrHolder.p_nameShort        
        log.debug("|{0}| >> On: {1} | attrHolder: {2}...".format(_str_func,mJnt.p_nameShort, attrHolder_short))                                    
        
        
        mPlug_addFactorIn = cgmMeta.cgmAttr(mSegmentCurve,
                                            "scaleFactor_%s"%(i),attrType='float',value=(1-(fl_factor * (i))),hidden=False)	    
        mPlug_out_startFactorUp = cgmMeta.cgmAttr(attrHolder_short,
                                                  "out_addStartUpScaleFactor_%s"%(i),attrType='float',lock=True)
        mPlug_out_startFactorOut = cgmMeta.cgmAttr(attrHolder_short,
                                                   "out_addStartOutScaleFactor_%s"%(i),attrType='float',lock=True)

        mPlug_out_endFactorUp = cgmMeta.cgmAttr(attrHolder_short,
                                                "out_addEndUpScaleFactor_%s"%(i),attrType='float',lock=True)		
        mPlug_out_endFactorOut = cgmMeta.cgmAttr(attrHolder_short,
                                                 "out_addEndOutScaleFactor_%s"%(i),attrType='float',lock=True)

        startUpArg = "%s = %s * %s"%(mPlug_out_startFactorUp.p_combinedShortName,
                                     mPlug_in_startUp.p_combinedShortName,
                                     mPlug_addFactorIn.p_combinedShortName )
        startOutArg = "%s = %s * %s"%(mPlug_out_startFactorOut.p_combinedShortName,
                                      mPlug_in_startOut.p_combinedShortName,
                                      mPlug_addFactorIn.p_combinedShortName )
        endUpArg = "%s = %s * %s"%(mPlug_out_endFactorUp.p_combinedShortName,
                                   mPlug_in_endUp.p_combinedShortName,
                                   mPlug_addFactorIn.p_combinedShortName )
        endOutArg = "%s = %s * %s"%(mPlug_out_endFactorOut.p_combinedShortName,
                                    mPlug_in_endOut.p_combinedShortName, mPlug_addFactorIn.p_combinedShortName )

        for arg in [startUpArg,startOutArg,endUpArg,endOutArg]:
            log.debug("|{0}| >> arg: {1}".format(_str_func,arg))                                                
            NodeF.argsToNodes(arg).doBuild()

        #Store indexed to 
        dPlugs_startUps[i] = mPlug_out_startFactorUp
        dPlugs_startOuts[i] = mPlug_out_startFactorOut
        dPlugs_endUps[i] = mPlug_out_endFactorUp
        dPlugs_endOuts[i] = mPlug_out_endFactorOut
        
    
    #Mid factors ---------------------------------------------------------------------------
    log.debug("|{0}| >> mid factors...".format(_str_func))                                                    
    int_mid = int(len(ml_jointList)/2)
    #ml_beforeJoints = ml_jointList[1:int_mid]
    ml_beforeJoints = ml_jointList[:int_mid]
    ml_beforeJoints.reverse()
    ml_afterJoints = ml_jointList[int_mid+1:-1]
    maxInt = (max([len(ml_beforeJoints),len(ml_afterJoints)])) +1#This is our max blend factors we need    
    
    for i in range(maxInt):
        #mAttrHolder = md_jointToHandle[i]
        #attrHolder_short = mAttrHolder.p_nameShort  
        
        mPlug_addFactorIn = cgmMeta.cgmAttr(mSegmentCurve,"midFactor_%s"%(i),attrType='float',hidden=False)	    
        mPlug_out_midFactorUp = cgmMeta.cgmAttr(mSegmentCurve,"out_addMidUpScaleFactor_%s"%(i),attrType='float',lock=True)		
        mPlug_out_midFactorOut = cgmMeta.cgmAttr(mSegmentCurve,"out_addMidOutScaleFactor_%s"%(i),attrType='float',lock=True)	

        midUpArg = "%s = %s * %s"%(mPlug_out_midFactorUp.p_combinedShortName, mPlug_in_midUp.p_combinedShortName, mPlug_addFactorIn.p_combinedShortName )
        midOutArg = "%s = %s * %s"%(mPlug_out_midFactorOut.p_combinedShortName, mPlug_in_midOut.p_combinedShortName, mPlug_addFactorIn.p_combinedShortName )
        for arg in [midUpArg,midOutArg]:
            log.debug("mid arg %s: %s"%(i,arg))
            NodeF.argsToNodes(arg).doBuild()

        dPlugs_midUps[i] = mPlug_out_midFactorUp
        dPlugs_midOuts[i] = mPlug_out_midFactorOut	

    
    #Now we need to build our drivens for each joint ----------------------------------------------------------------------
    log.debug("|{0}| >> Drivers per joint...".format(_str_func))                                                        
    d_jointDrivers = {}
    for i,mJnt in enumerate(ml_jointList):
        outScalePlug = ATTR.break_connection(mJnt.mNode,"scale%s"%outChannel)
        upScalePlug = ATTR.break_connection(mJnt.mNode,"scale%s"%upChannel)	
        d_jointDrivers[mJnt] = {'up':[upScalePlug],'out':[outScalePlug]}#build a dict of lists for each joint indexed to joint instance
        log.debug("|{0}| >> Drivers for {1} : {2}...".format(_str_func,i, d_jointDrivers[mJnt]))                                                        
        
    #Because the last joint uses the joint before it's scale, we want the raw scale not the additive scale (the mdNode is what we want), so we need to grab that
    #d_jointDrivers[ml_drivenJoints[-1]] = {'up':[upScalePlug],'out':[outScalePlug]}
    #log.debug("startUps: %s"%[dPlugs_startUps[k].p_combinedShortName for k in dPlugs_startUps.keys()])
    #log.debug("endUps: %s"%[dPlugs_endUps[k].p_combinedShortName for k in dPlugs_endUps.keys()])
    
    #build a dict of lists for each joint indexed to joint instance
    log.debug("|{0}| >> Dict building...".format(_str_func))                                                            
    for i,mJnt in enumerate(ml_startBlendJoints):#start blends
        log.debug("|{0}| >>  startBlend {1} | {2} | ups: {3} | outs: {4}".format(_str_func,i,mJnt.getShortName(),dPlugs_startUps[i].p_combinedShortName,dPlugs_startOuts[i].p_combinedShortName))                                                       
        
        d_jointDrivers[mJnt]['up'].append(dPlugs_startUps[i].p_combinedShortName)
        d_jointDrivers[mJnt]['out'].append(dPlugs_startOuts[i].p_combinedShortName)

    for i,mJnt in enumerate(ml_endBlendJoints):#end blends
        log.debug("|{0}| >>  startBlend {1} | {2} | ups: {3} | outs: {4}".format(_str_func,i,mJnt.getShortName(),dPlugs_endUps[i].p_combinedShortName,dPlugs_endOuts[i].p_combinedShortName))                                                               
        d_jointDrivers[mJnt]['up'].append(dPlugs_endUps[i].p_combinedShortName)
        d_jointDrivers[mJnt]['out'].append(dPlugs_endOuts[i].p_combinedShortName)    

    for i,mJnt in enumerate(ml_beforeJoints):#before blends
        d_jointDrivers[mJnt]['up'].append(dPlugs_midUps[i+1].p_combinedShortName)
        d_jointDrivers[mJnt]['out'].append(dPlugs_midOuts[i+1].p_combinedShortName)

    for i,mJnt in enumerate(ml_afterJoints):#after blends
        d_jointDrivers[mJnt]['up'].append(dPlugs_midUps[i+1].p_combinedShortName)
        d_jointDrivers[mJnt]['out'].append(dPlugs_midOuts[i+1].p_combinedShortName)

    mi_midJoint = ml_jointList[int_mid]
    d_jointDrivers[mi_midJoint]['up'].append(dPlugs_midUps[0].p_combinedShortName)
    d_jointDrivers[mi_midJoint]['out'].append(dPlugs_midOuts[0].p_combinedShortName)    

    #log.debug("last - %s | %s"%(ml_drivenJoints[-1].getShortName(),d_jointDrivers[ml_drivenJoints[-1]]))
    
    
    for mJnt in d_jointDrivers.keys():#Build our 
        log.debug("%s driven >> up: %s | out: %s"%(mJnt.getShortName(),[plug for plug in d_jointDrivers[mJnt]['up']],[plug for plug in d_jointDrivers[mJnt]['out']]))
        arg_up = "%s.scale%s = %s"%(mJnt.mNode,upChannel,' + '.join(d_jointDrivers[mJnt]['up']))
        arg_out = "%s.scale%s = %s"%(mJnt.mNode,outChannel,' + '.join(d_jointDrivers[mJnt]['out']))
        log.debug("arg_up: %s"%arg_up)
        log.debug("arg_out: %s"%arg_out)
        for arg in [arg_up,arg_out]:
            NodeF.argsToNodes(arg).doBuild()

    return {"mi_plug_startUp":mPlug_in_startUp,"mi_plug_startOut":mPlug_in_startOut,
            "plug_startUp":mPlug_in_startUp.p_combinedName,"plug_startOut":mPlug_in_startOut.p_combinedName,
            "mi_plug_endUp":mPlug_in_endUp,"mi_plug_endOut":mPlug_in_endOut,
            "plug_endUp":mPlug_in_endUp.p_combinedName,"plug_endOut":mPlug_in_endOut.p_combinedName,            
            "mi_plug_midUp":mPlug_in_midUp,"mi_plug_midOut":mPlug_in_midOut,
            "plug_midUp":mPlug_in_midUp.p_combinedName,"plug_midOut":mPlug_in_midOut.p_combinedName}    




def add_subControl_toCurve(joints=None, segmentCurve = None, baseParent = None, endParent = None,
                           midControls = None, orientation = 'zyx',controlOrientation = None,
                           controlTwistAxis = 'rotateY',
                           addTwist = True, baseName = None,
                           rotateGroupAxis = 'rotateZ', blendLength = None,
                           connectMidScale = True,
                           moduleInstance = None):
    """

    """
    _str_func = 'add_subControl_toCurve'
    
    #>>> Verify =============================================================================================
    log.debug("|{0}| >> Gather data...".format(_str_func)) 

    ml_newJoints = cgmMeta.validateObjListArg(joints,'cgmObject',noneValid=False, mayaType='joint')
    ml_midControls = cgmMeta.validateObjListArg(midControls,'cgmObject',noneValid=True)

    if ml_midControls and len(ml_midControls) != len(ml_newJoints):
        raise StandardError," Enough controls for joints provided! joints: %s | controls: %s"%(len(ml_midControls),len(ml_newJoints))


    mBaseParent = cgmMeta.validateObjArg(baseParent,cgmMeta.cgmObject,noneValid=False)
    mEndParent = cgmMeta.validateObjArg(endParent,cgmMeta.cgmObject,noneValid=False)
    mSegmentCurve = cgmMeta.validateObjArg(segmentCurve,cgmMeta.cgmObject,noneValid=False)
    mSegmentCurveSkinCluster = cgmMeta.validateObjArg(mSegmentCurve.getDeformers('skinCluster')[0],
                                                       noneValid=False)
    mSegmentGroup = mSegmentCurve.segmentGroup      

    #> Orientation ------------------------------------------------------------
    if controlOrientation is None:
        controlOrientation = orientation        

    aimVector = VALID.simpleAxis("%s+"%orientation[0]).p_vector
    aimVectorNegative = VALID.simpleAxis("%s-"%orientation[0]).p_vector
    upVector = VALID.simpleAxis("%s+"%orientation[1]).p_vector 
    outChannel = orientation[2]
    upChannel = '%sup'%orientation[1]   
    
    
    str_baseName = VALID.stringArg(baseName,noneValid=True)
    if not str_baseName:
        str_baseName = 'subControl'
    #< Verify <<<<DONE =============================================================================================



    #>>> Create Constraint Curve >>> =============================================================================
    log.debug("|{0}| >> Create Constraint Curve...".format(_str_func)) 
    
    #Spline -----------------------------------------------------------------
    if mSegmentCurve:#If we have a curve, duplicate it
        mConstraintSplineCurve = mSegmentCurve.doDuplicate(po = False, ic = False)
    else:
        l_pos = [mBaseParent.getPosition()]
        l_pos.expand([i_obj.getPosition() for i_obj in ml_newJoints])
        l_pos.append(mEndParent.getPosition())
        mConstraintSplineCurve = cgmMeta.cgmObject( mc.curve (d=3, ep = l_pos, os=True))
    mConstraintSplineCurve.addAttr('cgmName',baseName)
    mConstraintSplineCurve.addAttr('cgmTypeModifier','constraintSpline')
    mConstraintSplineCurve.doName()

    #Skin it ---------------------------------------------------------------------
    mConstraintSplineCurveCluster = cgmMeta.cgmNode(mc.skinCluster ([mBaseParent.mNode,mEndParent.mNode],
                                                                     mConstraintSplineCurve.mNode,
                                                                     tsb=True,
                                                                     maximumInfluences = 3,
                                                                     normalizeWeights = 1,dropoffRate=2.5)[0])

    mConstraintSplineCurveCluster.addAttr('cgmName', str_baseName)
    mConstraintSplineCurveCluster.addAttr('cgmTypeModifier','constraint', lock=True)
    mConstraintSplineCurveCluster.doName()

    #Linear
    #====================================================================	
    mConstraintLinearCurve = cgmMeta.cgmObject( mc.curve (d=1, ep = [mBaseParent.getPosition(),mEndParent.getPosition()], os=True))
    mConstraintLinearCurve.addAttr('cgmName',str_baseName)
    mConstraintLinearCurve.addAttr('cgmTypeModifier','constraintLinear')
    mConstraintLinearCurve.doName()

    #Skin it ---------------------------------------------------------------------------
    mConstraintLinearCurveCluster = cgmMeta.cgmNode(mc.skinCluster ([mBaseParent.mNode,mEndParent.mNode],
                                                                     mConstraintLinearCurve.mNode,
                                                                     tsb=True,
                                                                     maximumInfluences = 1,
                                                                     normalizeWeights = 1,dropoffRate=10.0)[0])

    mConstraintLinearCurveCluster.addAttr('cgmName', str_baseName)
    mConstraintLinearCurveCluster.addAttr('cgmTypeModifier','constraint', lock=True)
    mConstraintLinearCurveCluster.doName()	
    #<<< Create Constraint Curve <<<<DONE =============================================================================================


    #>>> Attach to curves >>> =============================================================================
    log.debug("|{0}| >> Attach to curves..".format(_str_func)) 
    
    ml_pointOnCurveInfos = []
    splineShape = mc.listRelatives(mConstraintSplineCurve.mNode,shapes=True)[0]
    linearShape = mc.listRelatives(mConstraintLinearCurve.mNode,shapes=True)[0] 


    for i,mJnt in enumerate(ml_newJoints):

        if ml_midControls and ml_midControls[i]:#if we have a control curve, use it
            mControl = ml_midControls[i]
        else:#else, connect 
            mControl = mJnt
            
        _str_jnt_short = mJnt.p_nameShort
        _str_control_short = mControl.p_nameShort
    
        log.debug("|{0}| >> On: {1} | control: {2}..".format(_str_func, _str_jnt_short, _str_control_short)) 
        
        #>>>Transforms ----------------------------------------------------------------------------------     
        #Create group
        grp = mJnt.doGroup()
        mFollow = cgmMeta.validateObjArg(grp,'cgmObject',setClass=True)
        mFollow.addAttr('cgmTypeModifier','follow',lock=True)
        mFollow.doName()

        grp = mJnt.doGroup(True)	
        mOrientGroup = cgmMeta.validateObjArg(grp,'cgmObject',setClass=True)
        mOrientGroup.addAttr('cgmTypeModifier','orient',lock=True)
        mOrientGroup.doName()
        

        mJnt.parent = False#since stuff is gonna move, we'll parent back at end

        #=============================================================	
        #>>>PointTargets
        #linear follow
        mLinearFollowNull = mJnt.doCreateAt()
        mLinearFollowNull.addAttr('cgmType','linearFollow',attrType='string',lock=True)
        mLinearFollowNull.doName()
        #mLinearFollowNull.parent = i_anchorStart.mNode     
        mLinearPosNull = mJnt.doCreateAt()
        mLinearPosNull.addAttr('cgmType','linearPos',attrType='string',lock=True)
        mLinearPosNull.doName()

        #splineFollow
        mSplineFollowNull = mJnt.doCreateAt()
        mSplineFollowNull.addAttr('cgmType','splineFollow',attrType='string',lock=True)
        mSplineFollowNull.doName()	

        #>>>Orient Targets
        #aimstart
        mAimStartNull = mJnt.doCreateAt()
        mAimStartNull.addAttr('cgmType','aimStart',attrType='string',lock=True)
        mAimStartNull.doName()
        mAimStartNull.parent = mFollow.mNode    

        #aimEnd
        mAimEndNull = mJnt.doCreateAt()
        mAimEndNull.addAttr('cgmType','aimEnd',attrType='string',lock=True)
        mAimEndNull.doName()
        mAimEndNull.parent = mFollow.mNode   


        #>>>Attach 
        #=============================================================
        #>>>Spline
        #l_closestInfo = distance.returnNearestPointOnCurveInfo(mJnt.mNode,mConstraintSplineCurve.mNode)
        param =  CURVES.getUParamOnCurve(mJnt.mNode, mConstraintSplineCurve.mNode)
        mClosestSplinePointNode = cgmMeta.cgmNode(nodeType = 'pointOnCurveInfo')
        mc.connectAttr ((splineShape+'.worldSpace'),(mClosestSplinePointNode.mNode+'.inputCurve'))	

        #> Name
        mClosestSplinePointNode.doStore('cgmName',mJnt)
        mClosestSplinePointNode.addAttr('cgmTypeModifier','spline',attrType='string',lock=True)	    
        mClosestSplinePointNode.doName()
        #>Set attachpoint value
        mClosestSplinePointNode.parameter = param
        mc.connectAttr ((mClosestSplinePointNode.mNode+'.position'),(mSplineFollowNull.mNode+'.translate'))
        ml_pointOnCurveInfos.append(mClosestSplinePointNode) 

        #>>>Linear
        param =  CURVES.getUParamOnCurve(mJnt.mNode, mConstraintLinearCurve.mNode)        
        #l_closestInfo = distance.returnNearestPointOnCurveInfo(mJnt.mNode,mConstraintLinearCurve.mNode)
        mClosestLinearPointNode = cgmMeta.cgmNode(nodeType = 'pointOnCurveInfo')
        mc.connectAttr ((linearShape+'.worldSpace'),(mClosestLinearPointNode.mNode+'.inputCurve'))	

        #> Name
        mClosestLinearPointNode.doStore('cgmName',mJnt)
        mClosestLinearPointNode.addAttr('cgmTypeModifier','linear',attrType='string',lock=True)	    	    
        mClosestLinearPointNode.doName()
        #>Set attachpoint value
        mClosestLinearPointNode.parameter = param
        mc.connectAttr ((mClosestLinearPointNode.mNode+'.position'),(mLinearFollowNull.mNode+'.translate'))
        ml_pointOnCurveInfos.append(mClosestLinearPointNode) 	    
        mLinearPosNull.parent = mLinearFollowNull.mNode#paren the pos obj

        
   

        #>>> point Constrain--------------------------------------------------------------------------------------
        log.debug("|{0}| >> Point constraint setup..".format(_str_func))         
        cBuffer = mc.pointConstraint([mSplineFollowNull.mNode,mLinearPosNull.mNode],
                                     mFollow.mNode,
                                     maintainOffset = True, weight = 1)[0]
        mPointConstraint = cgmMeta.asMeta(cBuffer,'cgmNode',setClass=True)	

        #Blendsetup

        targetWeights = mc.pointConstraint(mPointConstraint.mNode,q=True, weightAliasList=True)
        if len(targetWeights)>2:
            raise StandardError,"addCGMSegmentSubControl>>Too many weight targets: obj: %s | weights: %s"%(mJnt.mNode,targetWeights)

        d_midPointBlendReturn = NodeF.createSingleBlendNetwork([mControl.mNode,'linearSplineFollow'],
                                                               [mControl.mNode,'resultSplineFollow'],
                                                               [mControl.mNode,'resultLinearFollow'],
                                                               keyable=True)

        #Connect                                  
        d_midPointBlendReturn['d_result1']['mi_plug'].doConnectOut('%s.%s' % (mPointConstraint.mNode,targetWeights[0]))
        d_midPointBlendReturn['d_result2']['mi_plug'].doConnectOut('%s.%s' % (mPointConstraint.mNode,targetWeights[1]))
        d_midPointBlendReturn['d_result1']['mi_plug'].p_hidden = True
        d_midPointBlendReturn['d_result2']['mi_plug'].p_hidden = True



        #>>>Aim constraint and blend --------------------------------------------------------------------
        log.debug("|{0}| >> Orient constraint setup..".format(_str_func)) 
        #Create our decomposeMatrix attrs
        #Start up
        mUpStartDecomp = cgmMeta.cgmNode(nodeType = 'decomposeMatrix')
        mUpStartDecomp.addAttr('cgmName',str_baseName,attrType='string',lock=True)                
        mUpStartDecomp.addAttr('cgmType','midStartAimUp',attrType='string',lock=True)
        mUpStartDecomp.doName()

        #Start up
        mUpEndDecomp = cgmMeta.cgmNode(nodeType = 'decomposeMatrix')
        mUpEndDecomp.addAttr('cgmName',str_baseName,attrType='string',lock=True)                
        mUpEndDecomp.addAttr('cgmType','midEndAimUp',attrType='string',lock=True)
        mUpEndDecomp.doName()                
                 

        cBuffer = mc.aimConstraint(mBaseParent.mNode,
                                   mAimStartNull.mNode,
                                   maintainOffset = 0, weight = 1,
                                   aimVector = aimVectorNegative,
                                   upVector = upVector,
                                   worldUpType = 'vector' )[0]


        mStartAimConst = cgmMeta.asMeta(cBuffer,'cgmNode', setClass=True)
        #attributes.doConnectAttr(mUpStartDecomp.mNode,'inputMatrix')


        cBuffer = mc.aimConstraint(mEndParent.mNode,
                                   mAimEndNull.mNode,
                                   maintainOffset = 0, weight = 1,
                                   aimVector = aimVector,
                                   upVector = upVector,
                                   worldUpType = 'vector' )[0]

        mEndAimConst = cgmMeta.asMeta(cBuffer,'cgmNode', setClass=True)            
        cBuffer = mc.orientConstraint([mAimEndNull.mNode,mAimStartNull.mNode],
                                      mOrientGroup.mNode,
                                      maintainOffset = False, weight = 1)[0]
        mOrientConstraint = cgmMeta.asMeta(cBuffer,'cgmNode', setClass=True)	
        mOrientConstraint.interpType = 2

        #Blendsetup
        #log.debug("mOrientConstraint: %s"%mOrientConstraint)
        #log.debug("mControl: %s"%mControl)

        targetWeights = mc.orientConstraint(mOrientConstraint.mNode,q=True, weightAliasList=True)
        if len(targetWeights)>2:
            raise StandardError,"Too many weight targets: obj: %s | weights: %s"%(mJnt.mNode,targetWeights)

        d_midOrientBlendReturn = NodeF.createSingleBlendNetwork([mControl.mNode,'startEndAim'],
                                                                [mControl.mNode,'resultEndAim'],
                                                                [mControl.mNode,'resultStartAim'],
                                                                keyable=True)

        #Connect                                  
        d_midOrientBlendReturn['d_result1']['mi_plug'].doConnectOut('%s.%s' % (mOrientConstraint.mNode,targetWeights[0]))
        d_midOrientBlendReturn['d_result2']['mi_plug'].doConnectOut('%s.%s' % (mOrientConstraint.mNode,targetWeights[1]))
        d_midOrientBlendReturn['d_result1']['mi_plug'].p_hidden = True
        d_midOrientBlendReturn['d_result2']['mi_plug'].p_hidden = True




        #Skincluster work ---------------------------------------------------------------------------------------
        if mSegmentCurveSkinCluster:
            log.debug("|{0}| >> SKin cluster work..".format(_str_func)) 
            
            mc.skinCluster(mSegmentCurveSkinCluster.mNode,edit=True,ai=mJnt.mNode,dropoffRate = 2.5)
            #Smooth the weights
            curve_tightenEndWeights(mSegmentCurve,mBaseParent.mNode,mEndParent.mNode,2)	
   

        #>>>Add Twist -------------------------------------------------------------------------------------------
        mPlug_controlDriver = cgmMeta.cgmAttr(mControl.mNode,controlTwistAxis)	    
        mPlug_midTwist = cgmMeta.cgmAttr(mSegmentCurve,'twistMid')
        #mPlug_midTwist.doConnectIn(mPlug_controlDriver.p_combinedShortName)
        mSegmentCurve.doConnectIn('twistMid',mPlug_controlDriver.p_combinedShortName)
        
        if addTwist == 'asdasdfasdfasdfasdfasdf':
            if not mSegmentCurve:
                raise StandardError,"addCGMSegmentSubControl>>Cannot add twist without a segmentCurve"
            if not mSegmentCurve.getMessage('drivenJoints'):
                raise StandardError,"addCGMSegmentSubControl>>Cannot add twist stored bind joint info on segmentCurve: %s"%mSegmentCurve.getShortName()		    

            ml_drivenJoints = mSegmentCurve.msgList_get('drivenJoints',asMeta = True)

            closestJoint = distance.returnClosestObject(mJnt.mNode,[i_jnt.mNode for i_jnt in ml_drivenJoints])
            closestIndex = [i_jnt.mNode for i_jnt in ml_drivenJoints].index(closestJoint)
            upLoc = cgmMeta.cgmObject(closestJoint).rotateUpGroup.upLoc.mNode
            i_rotateUpGroup = cgmMeta.cgmObject(closestJoint).rotateUpGroup
            plug_rotateGroup = "%s.%s"%(i_rotateUpGroup.mNode,rotateGroupAxis)
            #Twist setup start
            #grab driver
            driverNodeAttr = attributes.returnDriverAttribute(plug_rotateGroup,True) 

            #get driven
            #rotDriven = attributes.returnDrivenAttribute(driverNodeAttr,True)

            rotPlug = attributes.doBreakConnection(i_rotateUpGroup.mNode,
                                                   rotateGroupAxis)
            #Create the add node
            mPlug_controlDriver = cgmMeta.cgmAttr(mControl.mNode,controlTwistAxis)
            l_driverPlugs = [driverNodeAttr,mPlug_controlDriver.p_combinedShortName]

            #Get the driven so that we can bridge to them 
            log.debug("midFollow "+ "="*50)
            log.debug("closestIndex: %s"%closestIndex)		
            log.debug("rotPlug: %s"%rotPlug)
            log.debug("rotateGroup: %s"%plug_rotateGroup)
            log.debug("originalDriverNode: %s"%driverNodeAttr)		
            log.debug("aimVector: '%s'"%aimVector)
            log.debug("upVector: '%s'"%upVector)    
            log.debug("upLoc: '%s'"%upLoc)
            #log.debug("rotDriven: '%s'"%rotDriven)
            log.debug("driverPlugs: '%s'"%l_driverPlugs)
            log.debug("="*50)

            #>>>Twist setup 
            #Connect To follow group
            #attributes.doConnectAttr(rotPlug,"%s.r%s"%(i_midFollowGrp.mNode,
                #                                          self._jointOrientation[0]))

            #>> Setup up the main twist add
            arg_add = "%s = %s"
            i_pmaAdd = NodeF.createAverageNode(l_driverPlugs,
                                               operation=1)

            attributes.doConnectAttr("%s.output1D"%i_pmaAdd.mNode,plug_rotateGroup)

            #>> Let's do the blend ===============================================================
            #First split it out ------------------------------------------------------------------
            ml_beforeJoints = ml_drivenJoints[1:closestIndex]
            ml_beforeJoints.reverse()
            ml_afterJoints = ml_drivenJoints[closestIndex+1:-1]
            log.debug("beforeJoints: %s"%[i_jnt.getShortName() for i_jnt in ml_beforeJoints])
            log.debug("afterJoints: %s"%[i_jnt.getShortName() for i_jnt in ml_afterJoints])

            #Get our factors ------------------------------------------------------------------
            mPlugs_factors = []
            for i,fac in enumerate([0.75,0.5,0.25]):
                mPlug_factor = cgmMeta.cgmAttr(mSegmentCurve,"out_%s_blendFactor_%s"%(closestIndex,i+1),attrType='float',lock=True)
                #str_factor = str(1.0/(i+2))
                str_factor = str(fac)
                log.debug(str_factor)
                log.debug(mPlug_factor.p_combinedShortName)
                log.debug(mPlug_controlDriver.p_combinedShortName)
                arg = "%s = %s * %s"%(mPlug_factor.p_combinedShortName,mPlug_controlDriver.p_combinedShortName,str_factor)
                log.debug("%s arg: %s"%(i,arg))
                NodeF.argsToNodes(arg).doBuild()
                mPlugs_factors.append(mPlug_factor)

            #Connect Them ----------------------------------------------------------------------
            def addFactorToJoint(i,i_jnt):
                try:
                    log.debug("On '%s'"%i_jnt.getShortName())

                    upLoc = i_jnt.rotateUpGroup.upLoc.mNode
                    i_rotateUpGroup = i_jnt.rotateUpGroup
                    plug_rotateGroup = "%s.%s"%(i_rotateUpGroup.mNode,rotateGroupAxis)

                    #Twist setup start
                    driverNodeAttr = attributes.returnDriverAttribute(plug_rotateGroup,True) 

                    rotPlug = attributes.doBreakConnection(i_rotateUpGroup.mNode,
                                                           rotateGroupAxis)
                    #Create the add node
                    l_driverPlugs = [driverNodeAttr,mPlugs_factors[i].p_combinedShortName]		    
                    i_pmaAdd = NodeF.createAverageNode(l_driverPlugs,
                                                       operation=1)

                    attributes.doConnectAttr("%s.output1D"%i_pmaAdd.mNode,plug_rotateGroup)
                except Exception,error:
                    log.error("'%s' Failed | %s"%(i_jnt.getShortName(),error))

            for i,i_jnt in enumerate(ml_beforeJoints):
                addFactorToJoint(i,i_jnt)

            for i,i_jnt in enumerate(ml_afterJoints):
                addFactorToJoint(i,i_jnt)

        

    
        #>>> Connect mid scale work ---------------------------------------------------------------------------------------
        
        if connectMidScale:
            log.debug("|{0}| >> connectMidScale..".format(_str_func)) 
            
            if not mSegmentCurve.hasAttr('scaleMidUp') or not mSegmentCurve.hasAttr('scaleMidOut'):
                mSegmentCurve.select()
                raise ValueError, "Segment curve missing scaleMidUp or scaleMideOut"
            
            mPlug_outDriver = cgmMeta.cgmAttr(mControl,"s%s"%controlOrientation[2])
            mPlug_upDriver = cgmMeta.cgmAttr(mControl,"s%s"%controlOrientation[1])
            mPlug_scaleOutDriver = cgmMeta.cgmAttr(mControl,"out_scaleOutNormal",attrType='float')
            mPlug_scaleUpDriver = cgmMeta.cgmAttr(mControl,"out_scaleUpNormal",attrType='float')
            mPlug_out_scaleUp = cgmMeta.cgmAttr(mControl,"out_scaleOutInv",attrType='float')
            mPlug_out_scaleOut = cgmMeta.cgmAttr(mControl,"out_scaleUpInv",attrType='float')	
            # -1 * (1 - driver)
            arg_up1 = "%s = 1 - %s"%(mPlug_scaleUpDriver.p_combinedShortName,mPlug_upDriver.p_combinedShortName)
            arg_out1 = "%s = 1 - %s"%(mPlug_scaleOutDriver.p_combinedShortName,mPlug_outDriver.p_combinedShortName)
            arg_up2 = "%s = -1 * %s"%(mPlug_out_scaleUp.p_combinedShortName,mPlug_scaleUpDriver.p_combinedShortName)
            arg_out2 = "%s = -1 * %s"%(mPlug_out_scaleOut.p_combinedShortName,mPlug_scaleOutDriver.p_combinedShortName)
            for arg in [arg_up1,arg_out1,arg_up2,arg_out2]:
                NodeF.argsToNodes(arg).doBuild()

            mPlug_out_scaleUp.doConnectOut("%s.scaleMidUp"%mSegmentCurve.mNode)
            mPlug_out_scaleOut.doConnectOut("%s.scaleMidOut"%mSegmentCurve.mNode)

            #Now let's connect scale of the start and end controls to a group so it's visually consistenent
            mc.scaleConstraint([mBaseParent.mNode,mEndParent.mNode],mOrientGroup.mNode)




    
        #Parent at very end to keep the joint from moving
        log.debug("|{0}| >> Final hook up..".format(_str_func)) 
        
        ATTR.connect("%s.worldMatrix"%(mBaseParent.mNode),"%s.%s"%(mUpStartDecomp.mNode,'inputMatrix'))
        ATTR.connect("%s.%s"%(mUpStartDecomp.mNode,"outputRotate"),"%s.%s"%(mStartAimConst.mNode,"upVector"))            
        ATTR.connect("%s.worldMatrix"%(mEndParent.mNode),"%s.%s"%(mUpEndDecomp.mNode,'inputMatrix'))
        ATTR.connect("%s.%s"%(mUpEndDecomp.mNode,"outputRotate"),"%s.%s"%(mEndAimConst.mNode,"upVector"))  

        for mi_const in [mStartAimConst,mEndAimConst]:
            mi_const.worldUpVector = [0,0,0]            



        if mControl != mJnt:#Parent our control if we have one
            if mControl.getMessage('masterGroup'):
                mControl.masterGroup.parent = mOrientGroup
            else:
                mControl.parent = mOrientGroup.mNode
                mControl.doGroup(True)
                mc.makeIdentity(mControl.mNode, apply=True,t=1,r=0,s=1,n=0)
            mJnt.parent = mControl.mNode
        else:
            mJnt.parent = mOrientGroup.mNode

        #Parent pieces
        mSegmentCurve.parent = mSegmentGroup.mNode	
        mConstraintLinearCurve.parent = mSegmentGroup.mNode
        mConstraintSplineCurve.parent = mSegmentGroup.mNode
        mLinearFollowNull.parent = mSegmentGroup.mNode	
        mSplineFollowNull.parent = mSegmentGroup.mNode
 

        return {'ml_followGroups':[mFollow]}


def curve_tightenEndWeights(curve,start = None, end = None, blendLength = 2):
    """Weight fixer for curves"""
    i_curve = cgmMeta.validateObjArg(curve,'cgmObject')


    l_cvs = i_curve.getComponents('cv')
    l_skinClusters = i_curve.getDeformers('skinCluster')
    i_skinCluster = cgmMeta.cgmNode(l_skinClusters[0])
    l_influenceObjects = OLDSKINNING.queryInfluences(i_skinCluster.mNode) or []

    log.debug("l_skinClusters: '%s'"%l_skinClusters)
    log.debug("i_skinCluster: '%s'"%i_skinCluster)
    log.debug("l_influenceObjects: '%s'"%l_influenceObjects)

    if not i_skinCluster and l_influenceObjects:
        raise StandardError,"curveSmoothWeights failed. Not enough info found"

    l_cvInts = [int(cv[-2]) for cv in l_cvs]

    l_cvInts = LISTS.get_noDuplicates(l_cvInts)

    #if len{cvEnds)<4:
        #raise StandardError,"Must have enough cvEnds. cvEnds: %s"%(cvEnds)
    if len(l_cvInts)<(blendLength + 2):
        raise StandardError,"Must have enough cvEnds. blendLength: %s"%(blendLength)	

    blendFactor = 1 * ((blendLength+1)*.1)
    log.debug("blendFactor: %s"%blendFactor)

    #>>>Tie down start and ends
    for influence in [start,end]:
        log.debug("Influence: %s"%influence)
        if influence == start:
            cvBlendRange = l_cvInts[:blendLength+2]
            log.debug("%s: %s"%(influence,cvBlendRange))
        if influence == end:
            cvBlendRange = l_cvInts[-(blendLength+2):]
            cvBlendRange.reverse()
            log.debug("%s: %s"%(influence,cvBlendRange))
        for i,cv in enumerate(cvBlendRange):
            if i in [0,1]:
                mc.skinPercent(i_skinCluster.mNode,("%s.cv[%s]"%(i_curve.mNode,cv)), tv = [influence,1])

            else:
                mc.skinPercent(i_skinCluster.mNode,("%s.cv[%s]"%(i_curve.mNode,cv)),
                               tv = [influence,1-(i*blendFactor)])