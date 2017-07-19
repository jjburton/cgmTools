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
import cgm.core.rig.ik_utils as IK
reload(IK)
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
        connectBy(string - trans) | How the joint will scale
        advancedTwistSetup(bool - False) | Whether to do the cgm advnaced twist setup
        addMidTwist(bool - True) | Whether to setup a mid twist on the segment
        moduleInstance(cgmModule - None) | cgmModule to use for connecting on build
        extendTwistToEnd(bool - False) | Whether to extned the twist to the end by default

    :returns:
        Dict ------------------------------------------------------------------
        'mi_segmentCurve'(cgmObject) | segment curve
        'segmentCurve'(str) | segment curve string
        'mi_ikHandle'(cgmObject) | spline ik Handle
        'mi_segmentGroup'(cgmObject) | segment group containing most of the guts
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

    #>>> Verify =============================================================================================
    ml_joints = cgmMeta.validateObjListArg(jointList,mType = 'cgmObject', mayaType=['joint'], noneValid = False)
    l_joints = [mJnt.p_nameShort for mJnt in ml_joints]
    int_lenJoints = len(ml_joints)#because it's called repeatedly
    mi_useCurve = cgmMeta.validateObjArg(useCurve,mayaType=['nurbsCurve'],noneValid = True)

    mi_mayaOrientation = VALID.simpleOrientation(orientation)
    str_orientation = mi_mayaOrientation.p_string
    str_secondaryAxis = VALID.stringArg(secondaryAxis,noneValid=True)
    str_baseName = VALID.stringArg(baseName,noneValid=True)
    if kws.get('connectBy'):
        stretchBy = kws.get('connectBy')
        
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
    
    #>> Setup ========================================================================================    
    if b_addMidTwist:#We are gonna do two splineIK chains ---------------------------------------------------------------------
        log.debug("|{0}| >> Midtwist mode...".format(_str_func))                                            
        ml_midTwistJoints = [] #exteded list of before and after joints
        int_mid = False       
        
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
            _res = IK.spline(chain,mi_useCurve,str_orientation,str_secondaryAxis,baseName,str_stretchBy,parentGutsTo=mi_grp)
            ml_splineRes.append(_res)
            mi_ikHandle = _res['mIKHandle']
            mi_segmentCurve = _res['mIKCurve']
            
        #SplineIK Twist -----------------------------------------------------------------------------------------------
        mi_ikHandleFirst = ml_splineRes[0]['mIKHandle']
        mi_ikHandleMid = ml_splineRes[1]['mIKHandle']
        mi_ikHandleMid.rename('midIKHandle')
        d_twistReturn = IK.addSplineTwist(mi_ikHandleFirst.mNode, mi_ikHandleMid.mNode, b_advancedTwistSetup)

    else:
        _res = IK.spline(ml_joints,mi_useCurve,str_orientation,str_secondaryAxis,baseName,str_stretchBy,parentGutsTo=mi_grp)
        ml_splineRes.append(_res)
        mi_ikHandle = _res['mIKHandle']
        mi_segmentCurve = _res['mIKCurve']
        mi_segmentCurve.connectChildNode(mi_grp,'segmentGroup','owner')   
        
        #SplineIK Twist -----------------------------------------------------------------------------------------------
        d_twistReturn = IK.addSplineTwist(mi_ikHandle.mNode, None, b_advancedTwistSetup)
        mPlug_twistStart = d_twistReturn['mPlug_start']
        mPlug_twistEnd = d_twistReturn['mPlug_end']
    
    return


def create(jointList, influenceJoints = None, addSquashStretch = True, addTwist = True,
           startControl = None, endControl = None, segmentType = 'curve',
           rotateGroupAxis = 'rotateZ',secondaryAxis = None,
           baseName = None, advancedTwistSetup = False, additiveScaleSetup = False,
           connectAdditiveScale = False,
           orientation = 'zyx', controlOrientation = None, moduleInstance = None):
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
    'mi_anchorStart'
    'mi_anchorStart'
    'mi_anchorEnd'
    'mPlug_extendTwist'
    'mi_constraintStartAim'
    'mi_constraintEndAim'
    'mi_endAimConstraint'
    'mi_segmentCurve'(cgmObject) | segment curve
    'segmentCurve'(str) | segment curve string
    'mi_ikHandle'(cgmObject) | spline ik Handle
    'mi_segmentGroup'(cgmObject) | segment group containing most of the guts
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
    _str_func = 'createCGMSegment'
    log.info(">>> %s >> "%_str_func + "="*75)   

    if segmentType != 'curve':
        raise NotImplementedError,"createCGMSegment>>>Haven't implemented segmentType: %s"%segmentType
    try:#Gather data =====================================================================================
        #> start/end control -------------------------------------------------------------        
        i_startControl = cgmMeta.validateObjArg(startControl,cgmMeta.cgmObject,noneValid=True)
        i_endControl = cgmMeta.validateObjArg(endControl,cgmMeta.cgmObject,noneValid=True)

        #> joints -------------------------------------------------------------
        if type(jointList) not in [list,tuple]:jointList = [jointList]
        if len(jointList)<3:
            raise StandardError,"createCGMSegment>>> needs at least three joints"

        ml_influenceJoints = cgmMeta.validateObjListArg(influenceJoints,cgmMeta.cgmObject,noneValid=False,mayaType=['nurbsCurve','joint'])

        try:ml_jointList = cgmMeta.validateObjListArg(jointList,cgmMeta.cgmObject,noneValid=False,mayaType=['nurbsCurve','joint'])
        except Exception,error:
            raise StandardError,"%s >>Joint metaclassing | error : %s"%(_str_func,error)

        #> module -------------------------------------------------------------
        i_module = False
        if i_module:
            if baseName is None: baseName = i_module.getPartNameBase()#Get part base name	    
        if baseName is None:baseName = 'testSegment'

        log.debug('i_startControl: %s'%i_startControl)
        log.debug('i_endControl: %s'%i_endControl)
        log.debug('ml_influenceJoints: %s'%ml_influenceJoints)
        log.debug('i_module: %s'%i_module)
        log.debug("baseName: %s"%baseName)  

        #Good way to verify an instance list? #validate orientation
        #Gather info
        if controlOrientation is None:
            controlOrientation = orientation   

        #> axis -------------------------------------------------------------
        axis_aim = cgmValid.simpleAxis("%s+"%orientation[0])
        axis_aimNeg = cgmValid.simpleAxis("%s-"%orientation[0])
        axis_up = cgmValid.simpleAxis("%s+"%orientation[0])

        aimVector = axis_aim.p_vector
        aimVectorNegative = axis_aimNeg.p_vector
        upVector = axis_up.p_vector   

        outChannel = orientation[2]
        upChannel = '%sup'%orientation[1]

        #> baseDistance -------------------------------------------------------------
        baseDist = distance.returnDistanceBetweenObjects(ml_jointList[0].mNode,ml_jointList[-1].mNode)/2        

    except Exception,error:
        raise StandardError,"%s >> data gather | error: %s"%(_str_func,error)  

    try:#>>> Module instance =====================================================================================
        i_module = False
        try:
            if moduleInstance is not None:
                if moduleInstance.isModule():
                    i_module = moduleInstance    
                    log.info("%s >> module instance found: %s"%(_str_func,i_module.p_nameShort))		
        except:pass
    except Exception,error:
        raise StandardError,"%s >> Module check fail! | error: %s"%(_str_func,error)    

    try:#Build Transforms =====================================================================================
        #Start Anchor
        i_anchorStart = ml_jointList[0].doCreateAt()
        i_anchorStart.addAttr('cgmType','anchor',attrType='string',lock=True)
        i_anchorStart.doName()
        i_anchorStart.parent = False  


        #End Anchor
        i_anchorEnd = ml_jointList[-1].doCreateAt()
        i_anchorEnd.addAttr('cgmType','anchor',attrType='string',lock=True)
        i_anchorEnd.doName()    
        i_anchorEnd.parent = False

        #if not i_startControl:i_startControl = i_anchorStart
        #if not i_endControl:i_endControl = i_anchorEnd

        #Build locs
        #=======================================================================================    
        ml_rigObjects = []
        #>>>Aims
        #Start Aim
        i_aimStartNull = ml_jointList[0].doCreateAt()
        i_aimStartNull.addAttr('cgmType','aim',attrType='string',lock=True)
        i_aimStartNull.doName()
        i_aimStartNull.parent = i_anchorStart.mNode   
        i_aimStartNull.rotateOrder = 0

        #End Aim
        i_aimEndNull = ml_jointList[-1].doCreateAt()
        i_aimEndNull.addAttr('cgmType','aim',attrType='string',lock=True)
        i_aimEndNull.doName()
        i_aimEndNull.parent = i_anchorEnd.mNode 
        i_aimEndNull.rotateOrder = 0

        #=====================================
        """
	if addTwist:
	    #>>>Twist loc
	    #Start Aim
	    i_twistStartNull = ml_jointList[0].doCreateAt()
	    i_twistStartNull.addAttr('cgmType','twist',attrType='string',lock=True)
	    i_twistStartNull.doName()
	    i_twistStartNull.parent = i_anchorStart.mNode     
	    ml_rigObjects.append(i_twistStartNull)

	    #End Aim
	    i_twistEndNull = ml_jointList[-1].doCreateAt()
	    i_twistEndNull.addAttr('cgmType','twist',attrType='string',lock=True)
	    i_twistEndNull.doName()
	    i_twistEndNull.parent = i_anchorEnd.mNode  
	    ml_rigObjects.append(i_twistEndNull)"""

        #=====================================	
        #>>>Attach
        #Start Attach
        i_attachStartNull = ml_jointList[0].doCreateAt()
        i_attachStartNull.addAttr('cgmType','attach',attrType='string',lock=True)
        i_attachStartNull.doName()
        i_attachStartNull.parent = i_anchorStart.mNode     

        #End Attach
        i_attachEndNull = ml_jointList[-1].doCreateAt()
        i_attachEndNull.addAttr('cgmType','attach',attrType='string',lock=True)
        i_attachEndNull.doName()
        i_attachEndNull.parent = i_anchorEnd.mNode  

        #=====================================	
        #>>>Up locs
        i_startUpNull = ml_jointList[0].doCreateAt()
        i_startUpNull.parent = i_anchorStart.mNode  
        i_startUpNull.addAttr('cgmType','up',attrType='string',lock=True)
        i_startUpNull.doName()
        ml_rigObjects.append(i_startUpNull)
        attributes.doSetAttr(i_startUpNull.mNode,'t%s'%orientation[2],baseDist)#We're gonna push these out

        #End
        i_endUpNull = ml_jointList[-1].doCreateAt()
        i_endUpNull.parent = i_anchorEnd.mNode     	
        i_endUpNull.addAttr('cgmType','up',attrType='string',lock=True)
        i_endUpNull.doName()
        ml_rigObjects.append(i_endUpNull)
        attributes.doSetAttr(i_endUpNull.mNode,'t%s'%orientation[2],baseDist)#We're gonna push these out

        """"
	#Make our endorient fix
	i_endUpOrientNull = i_anchorEnd.doDuplicateTransform(True)
	i_endUpOrientNull.parent = i_anchorEnd.mNode
	i_endUpOrientNull.addAttr('cgmType','upOrient',attrType='string',lock=True)
	i_endUpOrientNull.doName()
	i_endUpNull.parent = i_endUpOrientNull.mNode   
	mc.orientConstraint(i_anchorStart.mNode,i_endUpOrientNull.mNode,maintainOffset = True, skip = [axis for axis in orientation[:-1]])
	"""
        #Parent the influenceJoints
        ml_influenceJoints[0].parent = i_attachStartNull.mNode
        ml_influenceJoints[-1].parent = i_attachEndNull.mNode


        #Start Aim Target
        i_aimStartTargetNull = ml_jointList[-1].doCreateAt()
        i_aimStartTargetNull.addAttr('cgmType','aimTargetStart',attrType='string',lock=True)
        i_aimStartTargetNull.doName()
        i_aimStartTargetNull.parent = ml_influenceJoints[-1].mNode     
        ml_rigObjects.append(i_aimStartTargetNull)

        #End AimTarget
        i_aimEndTargetNull = ml_jointList[0].doCreateAt()
        i_aimEndTargetNull.addAttr('cgmType','aimTargetEnd',attrType='string',lock=True)
        i_aimEndTargetNull.doName()
        i_aimEndTargetNull.parent = ml_influenceJoints[0].mNode  
        ml_rigObjects.append(i_aimEndTargetNull)

        if i_startControl and not i_startControl.parent:
            i_startControl.parent = i_attachStartNull.mNode
            i_startControl.doGroup(True)
            mc.makeIdentity(i_startControl.mNode, apply=True,t=1,r=0,s=1,n=0)

            ml_influenceJoints[0].parent = i_startControl.mNode

        if i_endControl and not i_endControl.parent:
            i_endControl.parent = i_attachEndNull.mNode
            i_endControl.doGroup(True)
            mc.makeIdentity(i_endControl.mNode, apply=True,t=1,r=0,s=1,n=0)	    
            ml_influenceJoints[-1].parent = i_endControl.mNode

        """
	if i_module:#if we have a module, connect vis
	    for i_obj in ml_rigObjects:
		i_obj.overrideEnabled = 1		
		cgmMeta.cgmAttr(i_module.rigNull.mNode,'gutsVis',lock=False).doConnectOut("%s.%s"%(i_obj.mNode,'overrideVisibility'))
		cgmMeta.cgmAttr(i_module.rigNull.mNode,'gutsLock',lock=False).doConnectOut("%s.%s"%(i_obj.mNode,'overrideDisplayType'))    
		"""
    except Exception,error:
        log.error("createCGMSegment>>Joint anchor and loc build fail! | start joint: %s"%ml_jointList[0].getShortName())
        raise StandardError,error 

    try:#Constrain Nulls =====================================================================================
        cBuffer = mc.orientConstraint([i_anchorStart.mNode,i_aimStartNull.mNode],
                                      i_attachStartNull.mNode,
                                      maintainOffset = True, weight = 1)[0]
        i_startOrientConstraint = cgmMeta.asMeta(cBuffer,'cgmNode',setClass=True)
        i_startOrientConstraint.interpType = 0

        cBuffer = mc.orientConstraint([i_anchorEnd.mNode,i_aimEndNull.mNode],
                                      i_attachEndNull.mNode,
                                      maintainOffset = True, weight = 1)[0]
        i_endOrientConstraint = cgmMeta.asMeta(cBuffer,'cgmNode',setClass=True)
        i_endOrientConstraint.interpType = 0


    except Exception,error:
        log.error("createCGMSegment>>Constrain locs build fail! | start joint: %s"%ml_jointList[0].getShortName())
        raise StandardError,error 

    try:#Build constraint blend =====================================================================================
        #If we don't have our controls by this point, we'll use the joints
        if not i_startControl:
            i_startControl = ml_influenceJoints[0]
        if not i_endControl:
            i_endControl = ml_influenceJoints[-1]

        #start blend
        d_startFollowBlendReturn = NodeF.createSingleBlendNetwork([i_startControl.mNode,'followRoot'],
                                                                  [i_startControl.mNode,'resultRootFollow'],
                                                                  [i_startControl.mNode,'resultAimFollow'],
                                                                  keyable=True)
        targetWeights = mc.orientConstraint(i_startOrientConstraint.mNode,q=True, weightAliasList=True)
        #Connect                                  
        d_startFollowBlendReturn['d_result1']['mi_plug'].doConnectOut('%s.%s' % (i_startOrientConstraint.mNode,targetWeights[0]))
        d_startFollowBlendReturn['d_result2']['mi_plug'].doConnectOut('%s.%s' % (i_startOrientConstraint.mNode,targetWeights[1]))
        d_startFollowBlendReturn['d_result1']['mi_plug'].p_hidden = True
        d_startFollowBlendReturn['d_result2']['mi_plug'].p_hidden = True

        #EndBlend
        d_endFollowBlendReturn = NodeF.createSingleBlendNetwork([i_endControl.mNode,'followRoot'],
                                                                [i_endControl.mNode,'resultRootFollow'],
                                                                [i_endControl.mNode,'resultAimFollow'],
                                                                keyable=True)
        targetWeights = mc.orientConstraint(i_endOrientConstraint.mNode,q=True, weightAliasList=True)
        #Connect                                  
        d_endFollowBlendReturn['d_result1']['mi_plug'].doConnectOut('%s.%s' % (i_endOrientConstraint.mNode,targetWeights[0]))
        d_endFollowBlendReturn['d_result2']['mi_plug'].doConnectOut('%s.%s' % (i_endOrientConstraint.mNode,targetWeights[1]))
        d_endFollowBlendReturn['d_result1']['mi_plug'].p_hidden = True
        d_endFollowBlendReturn['d_result2']['mi_plug'].p_hidden = True

    except Exception,error:
        log.error("createCGMSegment>>Constrain locs build fail! | start joint: %s"%ml_jointList[0].getShortName())
        raise StandardError,error 

    try:#Build segment =====================================================================================
        try:
            d_segmentBuild = createSegmentCurve(jointList, orientation = orientation,secondaryAxis = secondaryAxis, baseName = baseName,connectBy = 'scale',
                                                addMidTwist=True, advancedTwistSetup = advancedTwistSetup, moduleInstance = moduleInstance)

            mi_segmentCurve = d_segmentBuild['mi_segmentCurve']
            ml_drivenJoints = d_segmentBuild['ml_drivenJoints']
            mi_scaleBuffer = d_segmentBuild['mi_scaleBuffer']
            mi_segmentGroup = d_segmentBuild['mi_segmentGroup']
            mPlug_extendTwist = d_segmentBuild['mPlug_extendTwist']
        except Exception,error:raise Exception,"[Initial Segment build]{%s}"%error

        log.info("addSquashStretch: %s"%addSquashStretch)
        try:#Add squash
            if addSquashStretch:
                log.info("ADD SQUASH")
                addSquashAndStretchToSegmentCurveSetup(mi_scaleBuffer.mNode,
                                                       [i_jnt.mNode for i_jnt in ml_jointList],
                                                       moduleInstance=moduleInstance)
        except Exception,error:raise Exception,"[Add squash]{%s}"%error

        try:#Additive Scale 
            if additiveScaleSetup:
                log.info('additiveScaleSetup...')
                addAdditiveScaleToSegmentCurveSetup(mi_segmentCurve.mNode,orientation=orientation)
                log.info('additiveScaleSetup done...')

                if connectAdditiveScale:
                    l_plugs = ['scaleStartUp','scaleStartOut','scaleEndUp','scaleEndOut']
                    for attr in l_plugs: 
                        log.info(attr)
                        if not mi_segmentCurve.hasAttr(attr):
                            mi_segmentCurve.select()
                            raise StandardError, "Segment curve missing attr: %s"%attr

                    l_attrPrefix = ['Start','End']
                    int_runningTally = 0
                    for i,i_ctrl in enumerate([i_startControl,i_endControl]):
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

                        mPlug_out_scaleUp.doConnectOut("%s.%s"%(mi_segmentCurve.mNode,l_plugs[int_runningTally]))
                        int_runningTally+=1
                        mPlug_out_scaleOut.doConnectOut("%s.%s"%(mi_segmentCurve.mNode,l_plugs[int_runningTally]))	    
                        int_runningTally+=1
        except Exception,error:
            raise Exception,"[Additive scale]{%s}"%error

        try:#Twist
            if addTwist:
                i_twistStartPlug = cgmMeta.cgmAttr(mi_segmentCurve.mNode,'twistStart',attrType='float',keyable=True) 
                i_twistEndPlug = cgmMeta.cgmAttr(mi_segmentCurve.mNode,'twistEnd',attrType='float',keyable=True)
                capAim = orientation[0].capitalize()
                """
		log.debug("capAim: %s"%capAim)
		d_twistReturn = addRibbonTwistToControlSetup([i_jnt.mNode for i_jnt in ml_jointList],
							     [i_twistStartPlug.obj.mNode,i_twistStartPlug.attr],
							     [i_twistEndPlug.obj.mNode,i_twistEndPlug.attr],moduleInstance=moduleInstance) 

		#Connect resulting full sum to our last spline IK joint to get it's twist
		attributes.doConnectAttr(i_twistEndPlug.p_combinedName,"%s.rotate%s"%(ml_drivenJoints[-1].mNode,capAim))
		"""	    
                if i_startControl:
                    if controlOrientation is None:
                        i_twistStartPlug.doConnectIn("%s.rotate%s"%(i_startControl.mNode,capAim))
                    else:
                        i_twistStartPlug.doConnectIn("%s.r%s"%(i_startControl.mNode,controlOrientation[0]))
                if i_endControl:
                    if controlOrientation is None:		
                        i_twistEndPlug.doConnectIn("%s.rotate%s"%(i_endControl.mNode,capAim))
                    else:
                        i_twistEndPlug.doConnectIn("%s.r%s"%(i_endControl.mNode,controlOrientation[0]))
        except Exception,error:raise Exception,"[Twist]{%s}"%error


    except Exception,error:
        log.error("createCGMSegment>>Build segment fail! | start joint: %s"%ml_jointList[0].getShortName())
        raise StandardError,error     

    try:#Skin curve =====================================================================================    
        if ml_influenceJoints:#if we have influence joints, we're gonna skin our curve
            #Surface influence joints cluster#
            i_controlSurfaceCluster = cgmMeta.cgmNode(mc.skinCluster ([i_jnt.mNode for i_jnt in ml_influenceJoints],
                                                                      mi_segmentCurve.mNode,
                                                                      tsb=True,
                                                                      maximumInfluences = 3,
                                                                      normalizeWeights = 1,dropoffRate=2.5)[0])

            i_controlSurfaceCluster.addAttr('cgmName', baseName, lock=True)
            i_controlSurfaceCluster.addAttr('cgmTypeModifier','segmentCurve', lock=True)
            i_controlSurfaceCluster.doName()
            """
	    if len(ml_influenceJoints) == 2:
		controlCurveSkinningTwoJointBlend(mi_segmentCurve.mNode,start = ml_influenceJoints[0].mNode,
		                                  end = ml_influenceJoints[-1].mNode,tightLength=1,
		                                  blendLength = int(len(jointList)/2))"""

    except Exception,error:
        log.error("createCGMSegment>>Build segment fail! | start joint: %s"%ml_jointList[0].getShortName())
        raise StandardError,error 

    try:#Mid influence objects =====================================================================================   
        ml_midObjects = ml_influenceJoints[1:-1] or []
        if len(ml_midObjects)>1:
            raise NotImplementedError,"createCGMSegment>>Haven't implemented having more than one mid influence object in a single chain yet!"
        if ml_midObjects:
            #Create a dup constraint curve
            i_constraintCurve = mi_segmentCurve.doDuplicate(po = True)
            i_constraintCurve.addAttr('cgmTypeModifier','constraint')

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

    try:#Aim constraints =====================================================================================
        #startAimTarget = i_aimStartTargetNull.mNode
        #endAimTarget = i_aimEndTargetNull.mNode
        startAimTarget = i_anchorEnd.mNode
        endAimTarget = i_anchorStart.mNode	
        cBuffer = mc.aimConstraint(startAimTarget,
                                   i_aimStartNull.mNode,
                                   maintainOffset = True, weight = 1,
                                   aimVector = aimVector,
                                   upVector = upVector,
                                   worldUpObject = i_startUpNull.mNode,
                                   worldUpType = 'object' ) 
        i_startAimConstraint = cgmMeta.asMeta(cBuffer[0],'cgmNode',setClass=True)

        cBuffer = mc.aimConstraint(endAimTarget,
                                   i_aimEndNull.mNode,
                                   maintainOffset = True, weight = 1,
                                   aimVector = aimVectorNegative,
                                   upVector = upVector,
                                   worldUpObject = i_endUpNull.mNode,
                                   worldUpType = 'object' ) 
        i_endAimConstraint = cgmMeta.asMeta(cBuffer[0],'cgmNode',setClass=True)  

    except Exception,error:
        log.error("createCGMSegment>>Build aim constraints! | start joint: %s"%ml_jointList[0].getShortName())
        raise StandardError,error   

    try:#Store some necessary info to the segment curve =====================================================================================
        mi_segmentCurve.connectChildNode(i_anchorStart,'anchorStart','segmentCurve')
        mi_segmentCurve.connectChildNode(i_anchorEnd,'anchorEnd','segmentCurve')
        mi_segmentCurve.connectChildNode(i_attachStartNull,'attachStart','segmentCurve')
        mi_segmentCurve.connectChildNode(i_attachEndNull,'attachEnd','segmentCurve')

    except Exception,error:
        log.error("createCGMSegment>>Info storage fail! |  error: {0}".format(error))

    try:#Return ========================================================================================
        md_return = {'mi_segmentCurve':mi_segmentCurve,'mi_anchorStart':i_anchorStart,'mi_anchorEnd':i_anchorEnd,'mPlug_extendTwist':mPlug_extendTwist,
                     'mi_constraintStartAim':i_startAimConstraint,'mi_constraintEndAim':i_endAimConstraint}
        for k in d_segmentBuild.keys():
            if k not in md_return.keys():
                md_return[k] = d_segmentBuild[k]#...push to the return dict
        return md_return
    except Exception,error:
        log.error("createCGMSegment>>return fail| error: {0}".format(error))





def createCGMSegmentOLD(jointList, influenceJoints = None, addSquashStretch = True, addTwist = True,
                     startControl = None, endControl = None, segmentType = 'curve',
                     rotateGroupAxis = 'rotateZ',secondaryAxis = None,
                     baseName = None, advancedTwistSetup = False, additiveScaleSetup = False,connectAdditiveScale = False,
                     orientation = 'zyx',controlOrientation = None, moduleInstance = None):
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
    'mi_anchorStart'
    'mi_anchorStart'
    'mi_anchorEnd'
    'mPlug_extendTwist'
    'mi_constraintStartAim'
    'mi_constraintEndAim'
    'mi_endAimConstraint'
    'mi_segmentCurve'(cgmObject) | segment curve
    'segmentCurve'(str) | segment curve string
    'mi_ikHandle'(cgmObject) | spline ik Handle
    'mi_segmentGroup'(cgmObject) | segment group containing most of the guts
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
    _str_func = 'createCGMSegment'
    log.info(">>> %s >> "%_str_func + "="*75)   

    if segmentType != 'curve':
        raise NotImplementedError,"createCGMSegment>>>Haven't implemented segmentType: %s"%segmentType
    try:#Gather data =====================================================================================
        #> start/end control -------------------------------------------------------------        
        i_startControl = cgmMeta.validateObjArg(startControl,cgmMeta.cgmObject,noneValid=True)
        i_endControl = cgmMeta.validateObjArg(endControl,cgmMeta.cgmObject,noneValid=True)

        #> joints -------------------------------------------------------------
        if type(jointList) not in [list,tuple]:jointList = [jointList]
        if len(jointList)<3:
            raise StandardError,"createCGMSegment>>> needs at least three joints"

        ml_influenceJoints = cgmMeta.validateObjListArg(influenceJoints,cgmMeta.cgmObject,noneValid=False,mayaType=['nurbsCurve','joint'])

        try:ml_jointList = cgmMeta.validateObjListArg(jointList,cgmMeta.cgmObject,noneValid=False,mayaType=['nurbsCurve','joint'])
        except Exception,error:
            raise StandardError,"%s >>Joint metaclassing | error : %s"%(_str_func,error)

        #> module -------------------------------------------------------------
        i_module = False
        if i_module:
            if baseName is None: baseName = i_module.getPartNameBase()#Get part base name	    
        if baseName is None:baseName = 'testSegment'

        log.debug('i_startControl: %s'%i_startControl)
        log.debug('i_endControl: %s'%i_endControl)
        log.debug('ml_influenceJoints: %s'%ml_influenceJoints)
        log.debug('i_module: %s'%i_module)
        log.debug("baseName: %s"%baseName)  

        #Good way to verify an instance list? #validate orientation
        #Gather info
        if controlOrientation is None:
            controlOrientation = orientation   

        #> axis -------------------------------------------------------------
        axis_aim = cgmValid.simpleAxis("%s+"%orientation[0])
        axis_aimNeg = cgmValid.simpleAxis("%s-"%orientation[0])
        axis_up = cgmValid.simpleAxis("%s+"%orientation[0])

        aimVector = axis_aim.p_vector
        aimVectorNegative = axis_aimNeg.p_vector
        upVector = axis_up.p_vector   

        outChannel = orientation[2]
        upChannel = '%sup'%orientation[1]

        #> baseDistance -------------------------------------------------------------
        baseDist = distance.returnDistanceBetweenObjects(ml_jointList[0].mNode,ml_jointList[-1].mNode)/2        

    except Exception,error:
        raise StandardError,"%s >> data gather | error: %s"%(_str_func,error)  

    try:#>>> Module instance =====================================================================================
        i_module = False
        try:
            if moduleInstance is not None:
                if moduleInstance.isModule():
                    i_module = moduleInstance    
                    log.info("%s >> module instance found: %s"%(_str_func,i_module.p_nameShort))		
        except:pass
    except Exception,error:
        raise StandardError,"%s >> Module check fail! | error: %s"%(_str_func,error)    

    try:#Build Transforms =====================================================================================
        #Start Anchor
        i_anchorStart = ml_jointList[0].doCreateAt()
        i_anchorStart.addAttr('cgmType','anchor',attrType='string',lock=True)
        i_anchorStart.doName()
        i_anchorStart.parent = False  


        #End Anchor
        i_anchorEnd = ml_jointList[-1].doCreateAt()
        i_anchorEnd.addAttr('cgmType','anchor',attrType='string',lock=True)
        i_anchorEnd.doName()    
        i_anchorEnd.parent = False

        #if not i_startControl:i_startControl = i_anchorStart
        #if not i_endControl:i_endControl = i_anchorEnd

        #Build locs
        #=======================================================================================    
        ml_rigObjects = []
        #>>>Aims
        #Start Aim
        i_aimStartNull = ml_jointList[0].doCreateAt()
        i_aimStartNull.addAttr('cgmType','aim',attrType='string',lock=True)
        i_aimStartNull.doName()
        i_aimStartNull.parent = i_anchorStart.mNode   
        i_aimStartNull.rotateOrder = 0

        #End Aim
        i_aimEndNull = ml_jointList[-1].doCreateAt()
        i_aimEndNull.addAttr('cgmType','aim',attrType='string',lock=True)
        i_aimEndNull.doName()
        i_aimEndNull.parent = i_anchorEnd.mNode 
        i_aimEndNull.rotateOrder = 0

        #=====================================
        """
	if addTwist:
	    #>>>Twist loc
	    #Start Aim
	    i_twistStartNull = ml_jointList[0].doCreateAt()
	    i_twistStartNull.addAttr('cgmType','twist',attrType='string',lock=True)
	    i_twistStartNull.doName()
	    i_twistStartNull.parent = i_anchorStart.mNode     
	    ml_rigObjects.append(i_twistStartNull)

	    #End Aim
	    i_twistEndNull = ml_jointList[-1].doCreateAt()
	    i_twistEndNull.addAttr('cgmType','twist',attrType='string',lock=True)
	    i_twistEndNull.doName()
	    i_twistEndNull.parent = i_anchorEnd.mNode  
	    ml_rigObjects.append(i_twistEndNull)"""

        #=====================================	
        #>>>Attach
        #Start Attach
        i_attachStartNull = ml_jointList[0].doCreateAt()
        i_attachStartNull.addAttr('cgmType','attach',attrType='string',lock=True)
        i_attachStartNull.doName()
        i_attachStartNull.parent = i_anchorStart.mNode     

        #End Attach
        i_attachEndNull = ml_jointList[-1].doCreateAt()
        i_attachEndNull.addAttr('cgmType','attach',attrType='string',lock=True)
        i_attachEndNull.doName()
        i_attachEndNull.parent = i_anchorEnd.mNode  

        #=====================================	
        #>>>Up locs
        i_startUpNull = ml_jointList[0].doCreateAt()
        i_startUpNull.parent = i_anchorStart.mNode  
        i_startUpNull.addAttr('cgmType','up',attrType='string',lock=True)
        i_startUpNull.doName()
        ml_rigObjects.append(i_startUpNull)
        attributes.doSetAttr(i_startUpNull.mNode,'t%s'%orientation[2],baseDist)#We're gonna push these out

        #End
        i_endUpNull = ml_jointList[-1].doCreateAt()
        i_endUpNull.parent = i_anchorEnd.mNode     	
        i_endUpNull.addAttr('cgmType','up',attrType='string',lock=True)
        i_endUpNull.doName()
        ml_rigObjects.append(i_endUpNull)
        attributes.doSetAttr(i_endUpNull.mNode,'t%s'%orientation[2],baseDist)#We're gonna push these out

        """"
	#Make our endorient fix
	i_endUpOrientNull = i_anchorEnd.doDuplicateTransform(True)
	i_endUpOrientNull.parent = i_anchorEnd.mNode
	i_endUpOrientNull.addAttr('cgmType','upOrient',attrType='string',lock=True)
	i_endUpOrientNull.doName()
	i_endUpNull.parent = i_endUpOrientNull.mNode   
	mc.orientConstraint(i_anchorStart.mNode,i_endUpOrientNull.mNode,maintainOffset = True, skip = [axis for axis in orientation[:-1]])
	"""
        #Parent the influenceJoints
        ml_influenceJoints[0].parent = i_attachStartNull.mNode
        ml_influenceJoints[-1].parent = i_attachEndNull.mNode


        #Start Aim Target
        i_aimStartTargetNull = ml_jointList[-1].doCreateAt()
        i_aimStartTargetNull.addAttr('cgmType','aimTargetStart',attrType='string',lock=True)
        i_aimStartTargetNull.doName()
        i_aimStartTargetNull.parent = ml_influenceJoints[-1].mNode     
        ml_rigObjects.append(i_aimStartTargetNull)

        #End AimTarget
        i_aimEndTargetNull = ml_jointList[0].doCreateAt()
        i_aimEndTargetNull.addAttr('cgmType','aimTargetEnd',attrType='string',lock=True)
        i_aimEndTargetNull.doName()
        i_aimEndTargetNull.parent = ml_influenceJoints[0].mNode  
        ml_rigObjects.append(i_aimEndTargetNull)

        if i_startControl and not i_startControl.parent:
            i_startControl.parent = i_attachStartNull.mNode
            i_startControl.doGroup(True)
            mc.makeIdentity(i_startControl.mNode, apply=True,t=1,r=0,s=1,n=0)

            ml_influenceJoints[0].parent = i_startControl.mNode

        if i_endControl and not i_endControl.parent:
            i_endControl.parent = i_attachEndNull.mNode
            i_endControl.doGroup(True)
            mc.makeIdentity(i_endControl.mNode, apply=True,t=1,r=0,s=1,n=0)	    
            ml_influenceJoints[-1].parent = i_endControl.mNode

        """
	if i_module:#if we have a module, connect vis
	    for i_obj in ml_rigObjects:
		i_obj.overrideEnabled = 1		
		cgmMeta.cgmAttr(i_module.rigNull.mNode,'gutsVis',lock=False).doConnectOut("%s.%s"%(i_obj.mNode,'overrideVisibility'))
		cgmMeta.cgmAttr(i_module.rigNull.mNode,'gutsLock',lock=False).doConnectOut("%s.%s"%(i_obj.mNode,'overrideDisplayType'))    
		"""
    except Exception,error:
        log.error("createCGMSegment>>Joint anchor and loc build fail! | start joint: %s"%ml_jointList[0].getShortName())
        raise StandardError,error 

    try:#Constrain Nulls =====================================================================================
        cBuffer = mc.orientConstraint([i_anchorStart.mNode,i_aimStartNull.mNode],
                                      i_attachStartNull.mNode,
                                      maintainOffset = True, weight = 1)[0]
        i_startOrientConstraint = cgmMeta.asMeta(cBuffer,'cgmNode',setClass=True)
        i_startOrientConstraint.interpType = 0

        cBuffer = mc.orientConstraint([i_anchorEnd.mNode,i_aimEndNull.mNode],
                                      i_attachEndNull.mNode,
                                      maintainOffset = True, weight = 1)[0]
        i_endOrientConstraint = cgmMeta.asMeta(cBuffer,'cgmNode',setClass=True)
        i_endOrientConstraint.interpType = 0


    except Exception,error:
        log.error("createCGMSegment>>Constrain locs build fail! | start joint: %s"%ml_jointList[0].getShortName())
        raise StandardError,error 

    try:#Build constraint blend =====================================================================================
        #If we don't have our controls by this point, we'll use the joints
        if not i_startControl:
            i_startControl = ml_influenceJoints[0]
        if not i_endControl:
            i_endControl = ml_influenceJoints[-1]

        #start blend
        d_startFollowBlendReturn = NodeF.createSingleBlendNetwork([i_startControl.mNode,'followRoot'],
                                                                  [i_startControl.mNode,'resultRootFollow'],
                                                                  [i_startControl.mNode,'resultAimFollow'],
                                                                  keyable=True)
        targetWeights = mc.orientConstraint(i_startOrientConstraint.mNode,q=True, weightAliasList=True)
        #Connect                                  
        d_startFollowBlendReturn['d_result1']['mi_plug'].doConnectOut('%s.%s' % (i_startOrientConstraint.mNode,targetWeights[0]))
        d_startFollowBlendReturn['d_result2']['mi_plug'].doConnectOut('%s.%s' % (i_startOrientConstraint.mNode,targetWeights[1]))
        d_startFollowBlendReturn['d_result1']['mi_plug'].p_hidden = True
        d_startFollowBlendReturn['d_result2']['mi_plug'].p_hidden = True

        #EndBlend
        d_endFollowBlendReturn = NodeF.createSingleBlendNetwork([i_endControl.mNode,'followRoot'],
                                                                [i_endControl.mNode,'resultRootFollow'],
                                                                [i_endControl.mNode,'resultAimFollow'],
                                                                keyable=True)
        targetWeights = mc.orientConstraint(i_endOrientConstraint.mNode,q=True, weightAliasList=True)
        #Connect                                  
        d_endFollowBlendReturn['d_result1']['mi_plug'].doConnectOut('%s.%s' % (i_endOrientConstraint.mNode,targetWeights[0]))
        d_endFollowBlendReturn['d_result2']['mi_plug'].doConnectOut('%s.%s' % (i_endOrientConstraint.mNode,targetWeights[1]))
        d_endFollowBlendReturn['d_result1']['mi_plug'].p_hidden = True
        d_endFollowBlendReturn['d_result2']['mi_plug'].p_hidden = True

    except Exception,error:
        log.error("createCGMSegment>>Constrain locs build fail! | start joint: %s"%ml_jointList[0].getShortName())
        raise StandardError,error 

    try:#Build segment =====================================================================================
        try:
            d_segmentBuild = createSegmentCurve(jointList, orientation = orientation,secondaryAxis = secondaryAxis, baseName = baseName,connectBy = 'scale',
                                                addMidTwist=True, advancedTwistSetup = advancedTwistSetup, moduleInstance = moduleInstance)

            mi_segmentCurve = d_segmentBuild['mi_segmentCurve']
            ml_drivenJoints = d_segmentBuild['ml_drivenJoints']
            mi_scaleBuffer = d_segmentBuild['mi_scaleBuffer']
            mi_segmentGroup = d_segmentBuild['mi_segmentGroup']
            mPlug_extendTwist = d_segmentBuild['mPlug_extendTwist']
        except Exception,error:raise Exception,"[Initial Segment build]{%s}"%error

        log.info("addSquashStretch: %s"%addSquashStretch)
        try:#Add squash
            if addSquashStretch:
                log.info("ADD SQUASH")
                addSquashAndStretchToSegmentCurveSetup(mi_scaleBuffer.mNode,
                                                       [i_jnt.mNode for i_jnt in ml_jointList],
                                                       moduleInstance=moduleInstance)
        except Exception,error:raise Exception,"[Add squash]{%s}"%error

        try:#Additive Scale 
            if additiveScaleSetup:
                log.info('additiveScaleSetup...')
                addAdditiveScaleToSegmentCurveSetup(mi_segmentCurve.mNode,orientation=orientation)
                log.info('additiveScaleSetup done...')

                if connectAdditiveScale:
                    l_plugs = ['scaleStartUp','scaleStartOut','scaleEndUp','scaleEndOut']
                    for attr in l_plugs: 
                        log.info(attr)
                        if not mi_segmentCurve.hasAttr(attr):
                            mi_segmentCurve.select()
                            raise StandardError, "Segment curve missing attr: %s"%attr

                    l_attrPrefix = ['Start','End']
                    int_runningTally = 0
                    for i,i_ctrl in enumerate([i_startControl,i_endControl]):
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

                        mPlug_out_scaleUp.doConnectOut("%s.%s"%(mi_segmentCurve.mNode,l_plugs[int_runningTally]))
                        int_runningTally+=1
                        mPlug_out_scaleOut.doConnectOut("%s.%s"%(mi_segmentCurve.mNode,l_plugs[int_runningTally]))	    
                        int_runningTally+=1
        except Exception,error:
            raise Exception,"[Additive scale]{%s}"%error

        try:#Twist
            if addTwist:
                i_twistStartPlug = cgmMeta.cgmAttr(mi_segmentCurve.mNode,'twistStart',attrType='float',keyable=True) 
                i_twistEndPlug = cgmMeta.cgmAttr(mi_segmentCurve.mNode,'twistEnd',attrType='float',keyable=True)
                capAim = orientation[0].capitalize()
                """
		log.debug("capAim: %s"%capAim)
		d_twistReturn = addRibbonTwistToControlSetup([i_jnt.mNode for i_jnt in ml_jointList],
							     [i_twistStartPlug.obj.mNode,i_twistStartPlug.attr],
							     [i_twistEndPlug.obj.mNode,i_twistEndPlug.attr],moduleInstance=moduleInstance) 

		#Connect resulting full sum to our last spline IK joint to get it's twist
		attributes.doConnectAttr(i_twistEndPlug.p_combinedName,"%s.rotate%s"%(ml_drivenJoints[-1].mNode,capAim))
		"""	    
                if i_startControl:
                    if controlOrientation is None:
                        i_twistStartPlug.doConnectIn("%s.rotate%s"%(i_startControl.mNode,capAim))
                    else:
                        i_twistStartPlug.doConnectIn("%s.r%s"%(i_startControl.mNode,controlOrientation[0]))
                if i_endControl:
                    if controlOrientation is None:		
                        i_twistEndPlug.doConnectIn("%s.rotate%s"%(i_endControl.mNode,capAim))
                    else:
                        i_twistEndPlug.doConnectIn("%s.r%s"%(i_endControl.mNode,controlOrientation[0]))
        except Exception,error:raise Exception,"[Twist]{%s}"%error


    except Exception,error:
        log.error("createCGMSegment>>Build segment fail! | start joint: %s"%ml_jointList[0].getShortName())
        raise StandardError,error     

    try:#Skin curve =====================================================================================    
        if ml_influenceJoints:#if we have influence joints, we're gonna skin our curve
            #Surface influence joints cluster#
            i_controlSurfaceCluster = cgmMeta.cgmNode(mc.skinCluster ([i_jnt.mNode for i_jnt in ml_influenceJoints],
                                                                      mi_segmentCurve.mNode,
                                                                      tsb=True,
                                                                      maximumInfluences = 3,
                                                                      normalizeWeights = 1,dropoffRate=2.5)[0])

            i_controlSurfaceCluster.addAttr('cgmName', baseName, lock=True)
            i_controlSurfaceCluster.addAttr('cgmTypeModifier','segmentCurve', lock=True)
            i_controlSurfaceCluster.doName()
            """
	    if len(ml_influenceJoints) == 2:
		controlCurveSkinningTwoJointBlend(mi_segmentCurve.mNode,start = ml_influenceJoints[0].mNode,
		                                  end = ml_influenceJoints[-1].mNode,tightLength=1,
		                                  blendLength = int(len(jointList)/2))"""

    except Exception,error:
        log.error("createCGMSegment>>Build segment fail! | start joint: %s"%ml_jointList[0].getShortName())
        raise StandardError,error 

    try:#Mid influence objects =====================================================================================   
        ml_midObjects = ml_influenceJoints[1:-1] or []
        if len(ml_midObjects)>1:
            raise NotImplementedError,"createCGMSegment>>Haven't implemented having more than one mid influence object in a single chain yet!"
        if ml_midObjects:
            #Create a dup constraint curve
            i_constraintCurve = mi_segmentCurve.doDuplicate(po = True)
            i_constraintCurve.addAttr('cgmTypeModifier','constraint')

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

    try:#Aim constraints =====================================================================================
        #startAimTarget = i_aimStartTargetNull.mNode
        #endAimTarget = i_aimEndTargetNull.mNode
        startAimTarget = i_anchorEnd.mNode
        endAimTarget = i_anchorStart.mNode	
        cBuffer = mc.aimConstraint(startAimTarget,
                                   i_aimStartNull.mNode,
                                   maintainOffset = True, weight = 1,
                                   aimVector = aimVector,
                                   upVector = upVector,
                                   worldUpObject = i_startUpNull.mNode,
                                   worldUpType = 'object' ) 
        i_startAimConstraint = cgmMeta.asMeta(cBuffer[0],'cgmNode',setClass=True)

        cBuffer = mc.aimConstraint(endAimTarget,
                                   i_aimEndNull.mNode,
                                   maintainOffset = True, weight = 1,
                                   aimVector = aimVectorNegative,
                                   upVector = upVector,
                                   worldUpObject = i_endUpNull.mNode,
                                   worldUpType = 'object' ) 
        i_endAimConstraint = cgmMeta.asMeta(cBuffer[0],'cgmNode',setClass=True)  

    except Exception,error:
        log.error("createCGMSegment>>Build aim constraints! | start joint: %s"%ml_jointList[0].getShortName())
        raise StandardError,error   

    try:#Store some necessary info to the segment curve =====================================================================================
        mi_segmentCurve.connectChildNode(i_anchorStart,'anchorStart','segmentCurve')
        mi_segmentCurve.connectChildNode(i_anchorEnd,'anchorEnd','segmentCurve')
        mi_segmentCurve.connectChildNode(i_attachStartNull,'attachStart','segmentCurve')
        mi_segmentCurve.connectChildNode(i_attachEndNull,'attachEnd','segmentCurve')

    except Exception,error:
        log.error("createCGMSegment>>Info storage fail! |  error: {0}".format(error))

    try:#Return ========================================================================================
        md_return = {'mi_segmentCurve':mi_segmentCurve,'mi_anchorStart':i_anchorStart,'mi_anchorEnd':i_anchorEnd,'mPlug_extendTwist':mPlug_extendTwist,
                     'mi_constraintStartAim':i_startAimConstraint,'mi_constraintEndAim':i_endAimConstraint}
        for k in d_segmentBuild.keys():
            if k not in md_return.keys():
                md_return[k] = d_segmentBuild[k]#...push to the return dict
        return md_return
    except Exception,error:
        log.error("createCGMSegment>>return fail| error: {0}".format(error))




