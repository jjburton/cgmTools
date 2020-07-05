"""
------------------------------------------
ik_utils: cgm.core.rig
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
from cgm.core.classes import NodeFactory as NODEFAC
import cgm.core.rig.joint_utils as JOINTS
import cgm.core.lib.attribute_utils as ATTR
import cgm.core.lib.transform_utils as TRANS
import cgm.core.lib.distance_utils as DIST
import cgm.core.rig.constraint_utils as RIGCONSTRAINTS
import cgm.core.rig.create_utils as RIGCREATE
import cgm.core.rig.general_utils as RIGGEN
import cgm.core.lib.list_utils as LISTS
import cgm.core.lib.rigging_utils as CORERIG
import cgm.core.lib.locator_utils as LOC
import cgm.core.lib.node_utils as NODES
import cgm.core.lib.math_utils as MATH
import cgm.core.rig.skin_utils as RIGSKIN
import cgm.core.lib.position_utils as POS

#for m in CURVES,RIGCREATE,RIGGEN,LISTS,RIGCONSTRAINTS,MATH,NODES,NODEFAC:
#    reload(m)

def spline(jointList = None,
           useCurve = None,
           orientation = 'zyx',
           secondaryAxis = 'y+',
           baseName = None,
           stretchBy = 'translate',
           advancedTwistSetup = False,
           extendTwistToEnd = False,
           reorient = False,
           moduleInstance = None,
           parentGutsTo = None):
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
        stretchBy(string - trans/scale/None) | How the joint will scale
        advancedTwistSetup(bool - False) | Whether to do the cgm advnaced twist setup
        addMidTwist(bool - True) | Whether to setup a mid twist on the segment
        moduleInstance(cgmModule - None) | cgmModule to use for connecting on build
        extendTwistToEnd(bool - False) | Whether to extned the twist to the end by default

    :returns:
        mIKHandle, mIKEffector, mIKSolver, mi_splineCurve
        

    :raises:
        Exception | if reached

    """ 
    _str_func = 'splineIK'
    #try:
    #>>> Verify =============================================================================================
    ml_joints = cgmMeta.validateObjListArg(jointList,mType = 'cgmObject', mayaType=['joint'], noneValid = False)
    l_joints = [mJnt.p_nameShort for mJnt in ml_joints]
    int_lenJoints = len(ml_joints)#because it's called repeatedly
    mi_useCurve = cgmMeta.validateObjArg(useCurve,mayaType=['nurbsCurve'],noneValid = True)

    mi_mayaOrientation = VALID.simpleOrientation(orientation)
    str_orientation = mi_mayaOrientation.p_string
    str_secondaryAxis = VALID.stringArg(secondaryAxis,noneValid=True)
    str_baseName = VALID.stringArg(baseName,noneValid=True)
    
    
    #module -----------------------------------------------------------------------------------------------
    mModule = cgmMeta.validateObjArg(moduleInstance,'cgmRigModule',noneValid = True)
    ml_toConnect=[]

    mi_rigNull = False	
    if mModule:
        log.debug("|{0}| >> Module found. mModule: {1}...".format(_str_func,mModule))                                    
        mi_rigNull = mModule.rigNull	
        if str_baseName is None:
            str_baseName = mModule.getPartNameBase()#Get part base name	    
    if not str_baseName:str_baseName = 'testSplineIK' 
    #...
    
    str_stretchBy = VALID.stringArg(stretchBy,noneValid=True)		
    b_advancedTwistSetup = VALID.boolArg(advancedTwistSetup)
    b_extendTwistToEnd= VALID.boolArg(extendTwistToEnd)

    if int_lenJoints<3:
        pprint.pprint(vars())
        raise ValueError,"needs at least three joints"
    
    if parentGutsTo is None:
        mGroup = cgmMeta.cgmObject(name = 'newgroup')
        mGroup.addAttr('cgmName', str(str_baseName), lock=True)
        mGroup.addAttr('cgmTypeModifier','segmentStuff', lock=True)
        mGroup.doName()
    else:
        mGroup = cgmMeta.validateObjArg(parentGutsTo,'cgmObject',False)
        
        
    if mi_rigNull:
        mGroup.p_parent = mi_rigNull

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
    l_param = []  
    
    #>>> SplineIK ===========================================================================================
    if mi_useCurve:
        log.debug("|{0}| >> useCurve. SplineIk...".format(_str_func))    
        f_MatchPosOffset = CURVES.getUParamOnCurve(ml_joints[0].mNode, mi_useCurve.mNode)
        log.debug("|{0}| >> Use curve mode. uPos: {1}...".format(_str_func,f_MatchPosOffset))                            
        
        
        for mJnt in ml_joints:
            param = CURVES.getUParamOnCurveFromObj(mJnt.mNode, mi_useCurve.mNode) 
            log.debug("|{0}| >> {1}...".format(_str_func,param))                
            l_param.append(param)
        
        #Because maya is stupid, when doing an existing curve splineIK setup in 2011, you need to select the objects
        #Rather than use the flags
        mc.select(cl=1)
        mc.select([ml_joints[0].mNode,ml_joints[-1].mNode,mi_useCurve.mNode])
        buffer = mc.ikHandle( simplifyCurve=False, eh = 1,curve = mi_useCurve.mNode,
                              rootOnCurve=True, forceSolver = True, snapHandleFlagToggle=True,
                              parentCurve = False, solver = 'ikSplineSolver',createCurve = False,)  
        log.info(buffer)
        mSegmentCurve = mi_useCurve#Link
        mSegmentCurve.addAttr('cgmType','splineIKCurve',attrType='string',lock=True)
        mSegmentCurve.doName()		
             
    else:
        log.debug("|{0}| >> createCurve. SplineIk...".format(_str_func))                                    

        buffer = mc.ikHandle( sj=ml_joints[0].mNode, ee=ml_joints[-1].mNode,simplifyCurve=False,
                              solver = 'ikSplineSolver', ns = 4, rootOnCurve=True,forceSolver = True,
                              createCurve = True,snapHandleFlagToggle=True )  

        mSegmentCurve = cgmMeta.asMeta( buffer[2],'cgmObject',setClass=True )
        mSegmentCurve.addAttr('cgmName',str_baseName,attrType='string',lock=True)    
        mSegmentCurve.addAttr('cgmType','splineIKCurve',attrType='string',lock=True)
        mSegmentCurve.doName()



    mIKSolver = cgmMeta.cgmNode(name = 'ikSplineSolver')
    
    #>> Handle/Effector --------------------------------------------------------------------------------------
    mIKHandle = cgmMeta.validateObjArg( buffer[0],'cgmObject',setClass=True )
    mIKHandle.addAttr('cgmName',str_baseName,attrType='string',lock=True)    		
    mIKHandle.doName()
    mIKHandle = mIKHandle

    mIKEffector = cgmMeta.validateObjArg( buffer[1],'cgmObject',setClass=True )
    mIKEffector.addAttr('cgmName',str_baseName,attrType='string',lock=True)  
    mIKEffector.doName()
    mIKHandle.parent = mGroup
    
    mSegmentCurve.connectChildNode(mGroup,'segmentGroup','owner')
    
    if mi_useCurve:
        log.debug("|{0}| >> useCurve fix. setIk handle offset to: {1}".format(_str_func,f_MatchPosOffset))                                            
        mIKHandle.offset = f_MatchPosOffset           
        
    _res = {'mIKHandle':mIKHandle, 
            'mIKEffector':mIKEffector,
            'mIKSolver':mIKSolver,
            'mSplineCurve':mSegmentCurve}
    
    #>>> Stretch ============================================================================================
    if str_stretchBy:
        log.debug("|{0}| >> Stretchy. by: {1}...".format(_str_func,str_stretchBy))
        ml_pointOnCurveInfos = []
        
        #First thing we're going to do is create our 'follicles'
        str_shape = mSegmentCurve.getShapes(asMeta=False)[0]
    
        for i,mJnt in enumerate(ml_joints):   
            #import cgm.lib.distance as distance
            #l_closestInfo = distance.returnNearestPointOnCurveInfo(mJnt.mNode,mSegmentCurve.mNode)
            #param = CURVES.getUParamOnCurve(mJnt.mNode, mSegmentCurve.mNode)
            if not l_param:
                param = CURVES.getUParamOnCurveFromObj(mJnt.mNode, mSegmentCurve.mNode)  
            else:
                param = l_param[i]
            #param = DIST.get_closest_point(mJnt.mNode,mSegmentCurve.mNode)[1]
            log.debug("|{0}| >> {1} param: {2}...".format(_str_func,mJnt.p_nameShort,param))
            
            #>>> POCI ----------------------------------------------------------------
            mi_closestPointNode = cgmMeta.cgmNode(nodeType = 'pointOnCurveInfo')
            ATTR.connect(str_shape+'.worldSpace',mi_closestPointNode.mNode+'.inputCurve')	
    
            #> Name
            mi_closestPointNode.doStore('cgmName',mJnt)
            mi_closestPointNode.doName()
            #>Set follicle value
            mi_closestPointNode.parameter = param
            ml_pointOnCurveInfos.append(mi_closestPointNode)
            
        ml_distanceObjects = []
        ml_distanceShapes = []  
        mSegmentCurve.addAttr('masterScale',value = 1.0, minValue = 0.0001, attrType='float')
        
        for i,mJnt in enumerate(ml_joints[:-1]):
            #>> Distance nodes
            mDistanceShape = cgmMeta.cgmNode( mc.createNode ('distanceDimShape') )        
            mDistanceDag = mDistanceShape.getTransform(asMeta=True) 
            mDistanceDag.doStore('cgmName',mJnt)
            mDistanceDag.addAttr('cgmType','measureNode',lock=True)
            mDistanceDag.doName(nameShapes = True)
            mDistanceDag.parent = mGroup.mNode#parent it
            mDistanceDag.overrideEnabled = 1
            mDistanceDag.overrideVisibility = 1

            #Connect things
            ATTR.connect(ml_pointOnCurveInfos[i].mNode+'.position',mDistanceShape.mNode+'.startPoint')
            ATTR.connect(ml_pointOnCurveInfos[i+1].mNode+'.position',mDistanceShape.mNode+'.endPoint')

            ml_distanceObjects.append(mDistanceDag)
            ml_distanceShapes.append(mDistanceShape)

            ml_toConnect.append(mDistanceDag)



        #>>>Hook up stretch/scale #========================================================================= 
        ml_distanceAttrs = []
        ml_resultAttrs = []

        #mi_jntScaleBufferNode.connectParentNode(mSegmentCurve.mNode,'segmentCurve','scaleBuffer')
        ml_mainMDs = []
        
        for i,mJnt in enumerate(ml_joints[:-1]):
            #progressBar_set(status = "node setup | '%s'"%l_joints[i], progress = i, maxValue = int_lenJoints)		    

            #Make some attrs
            mPlug_attrDist= cgmMeta.cgmAttr(mIKHandle.mNode,
                                            "distance_%s"%i,attrType = 'float',initialValue=0,lock=True,minValue = 0)
            mPlug_attrNormalBaseDist = cgmMeta.cgmAttr(mIKHandle.mNode,
                                                       "normalizedBaseDistance_%s"%i,attrType = 'float',
                                                       initialValue=0,lock=True,minValue = 0)			
            mPlug_attrNormalDist = cgmMeta.cgmAttr(mIKHandle.mNode,
                                                   "normalizedDistance_%s"%i,attrType = 'float',initialValue=0,lock=True,minValue = 0)		
            mPlug_attrResult = cgmMeta.cgmAttr(mIKHandle.mNode,
                                               "scaleResult_%s"%i,attrType = 'float',initialValue=0,lock=True,minValue = 0)	
            mPlug_attrTransformedResult = cgmMeta.cgmAttr(mIKHandle.mNode,
                                                          "scaledScaleResult_%s"%i,attrType = 'float',initialValue=0,lock=True,minValue = 0)	
            
            ATTR.datList_append(mIKHandle.mNode,'baseDist',ml_distanceShapes[i].distance)
            ATTR.set_hidden(mIKHandle.mNode,'baseDist_{0}'.format(i),True)
            
            if str_stretchBy.lower() in ['translate','trans','t']:
                #Let's build our args
                l_argBuild = []
                #distance by master
                l_argBuild.append("{0} = {1} / {2}".format(mPlug_attrNormalBaseDist.p_combinedName,
                                                           '{0}.baseDist_{1}'.format(mIKHandle.mNode,i),
                                                           "{0}.masterScale".format(mSegmentCurve.mNode)))
                l_argBuild.append("{0} = {1} / {2}".format(mPlug_attrNormalDist.p_combinedName,
                                                           mPlug_attrDist.p_combinedName,
                                                           "{0}.masterScale".format(mSegmentCurve.mNode)))			
                for arg in l_argBuild:
                    log.debug("|{0}| >> Building arg: {1}".format(_str_func,arg))
                    NODEFAC.argsToNodes(arg).doBuild()
                    
                #Still not liking the way this works with translate scale. looks fine till you add squash and stretch
                try:
                    mPlug_attrDist.doConnectIn('%s.%s'%(ml_distanceShapes[i].mNode,'distance'))		        
                    mPlug_attrNormalDist.doConnectOut('%s.t%s'%(ml_joints[i+1].mNode,str_orientation[0]))
                    #mPlug_attrNormalDist.doConnectOut('%s.t%s'%(ml_driverJoints[i+1].mNode,str_orientation[0]))    	    
                except Exception,error:
                    raise Exception,"[Failed to connect joint attrs by scale: {0} | error: {1}]".format(mJnt.mNode,error)		
                
            else:
                mi_mdNormalBaseDist = cgmMeta.cgmNode(nodeType='multiplyDivide')
                mi_mdNormalBaseDist.operation = 1
                mi_mdNormalBaseDist.doStore('cgmName',mJnt)
                mi_mdNormalBaseDist.addAttr('cgmTypeModifier','normalizedBaseDist')
                mi_mdNormalBaseDist.doName()

                ATTR.connect('%s.masterScale'%(mSegmentCurve.mNode),#>>
                             '%s.%s'%(mi_mdNormalBaseDist.mNode,'input1X'))
                ATTR.connect('{0}.baseDist_{1}'.format(mIKHandle.mNode,i),#>>
                             '%s.%s'%(mi_mdNormalBaseDist.mNode,'input2X'))	
                mPlug_attrNormalBaseDist.doConnectIn('%s.%s'%(mi_mdNormalBaseDist.mNode,'output.outputX'))

                #Create the normalized distance
                mi_mdNormalDist = cgmMeta.cgmNode(nodeType='multiplyDivide')
                mi_mdNormalDist.operation = 1
                mi_mdNormalDist.doStore('cgmName',mJnt)
                mi_mdNormalDist.addAttr('cgmTypeModifier','normalizedDist')
                mi_mdNormalDist.doName()

                ATTR.connect('%s.masterScale'%(mSegmentCurve.mNode),#>>
                             '%s.%s'%(mi_mdNormalDist.mNode,'input1X'))
                mPlug_attrDist.doConnectOut('%s.%s'%(mi_mdNormalDist.mNode,'input2X'))	
                mPlug_attrNormalDist.doConnectIn('%s.%s'%(mi_mdNormalDist.mNode,'output.outputX'))

                #Create the mdNode
                mi_mdSegmentScale = cgmMeta.cgmNode(nodeType='multiplyDivide')
                mi_mdSegmentScale.operation = 2
                mi_mdSegmentScale.doStore('cgmName',mJnt)
                mi_mdSegmentScale.addAttr('cgmTypeModifier','segmentScale')
                mi_mdSegmentScale.doName()
                mPlug_attrDist.doConnectOut('%s.%s'%(mi_mdSegmentScale.mNode,'input1X'))	
                mPlug_attrNormalBaseDist.doConnectOut('%s.%s'%(mi_mdSegmentScale.mNode,'input2X'))
                mPlug_attrResult.doConnectIn('%s.%s'%(mi_mdSegmentScale.mNode,'output.outputX'))	

                try:#Connect
                    mPlug_attrDist.doConnectIn('%s.%s'%(ml_distanceShapes[i].mNode,'distance'))		        
                    mPlug_attrResult.doConnectOut('%s.s%s'%(mJnt.mNode,str_orientation[0]))
                    #mPlug_attrResult.doConnectOut('%s.s%s'%(ml_driverJoints[i].mNode,str_orientation[0]))
                except Exception,error:raise Exception,"[Failed to connect joint attrs by scale: {0} | error: {1}]".format(mJnt.mNode,error)		    

                ml_mainMDs.append(mi_mdSegmentScale)#store the md



            #Append our data
            ml_distanceAttrs.append(mPlug_attrDist)
            ml_resultAttrs.append(mPlug_attrResult)

            """
                for axis in [str_orientation[1],str_orientation[2]]:
                    attributes.doConnectAttr('%s.s%s'%(mJnt.mNode,axis),#>>
                                             '%s.s%s'%(ml_driverJoints[i].mNode,axis))"""	 	


        
    #Connect last joint scale to second to last
    for axis in ['scaleX','scaleY','scaleZ']:
        ATTR.connect('%s.%s'%(ml_joints[-2].mNode,axis),#>>
                     '%s.%s'%(ml_joints[-1].mNode,axis))	 

    #mc.pointConstraint(ml_driverJoints[0].mNode,ml_joints[0].mNode,maintainOffset = False)
    
    #>> Connect and close =============================================================================
    #mSegmentCurve.connectChildNode(mi_jntScaleBufferNode,'scaleBuffer','segmentCurve')
    #mSegmentCurve.connectChildNode(mIKHandle,'ikHandle','segmentCurve')
    mSegmentCurve.msgList_append('ikHandles',mIKHandle,'segmentCurve')
    #mSegmentCurve.msgList_connect('drivenJoints',ml_joints,'segmentCurve')       
    mIKHandle.msgList_connect('drivenJoints',ml_joints,'ikHandle')       
    
    #mSegmentCurve.msgList_connect(ml_driverJoints,'driverJoints','segmentCurve')  
        
    """        
    except Exception,err:
        print(cgmGEN._str_hardLine)
        log.error("|{0}| >> Failure: {1}".format(_str_func, err.__class__))
        print("Local data>>>" + cgmGEN._str_subLine)        
        pprint.pprint(vars())  
        print("Local data<<<" + cgmGEN._str_subLine)                
        print("Errors...")
        for a in err.args:
            print(a)
        print(cgmGEN._str_subLine)        
        raise Exception,err"""

    #SplineIK Twist =======================================================================================
    d_twistReturn = rig_Utils.IKHandle_addSplineIKTwist(mIKHandle.mNode,b_advancedTwistSetup)
    mPlug_twistStart = d_twistReturn['mi_plug_start']
    mPlug_twistEnd = d_twistReturn['mi_plug_end']
    _res['mPlug_twistStart'] = mPlug_twistStart
    _res['mPlug_twistEnd'] = mPlug_twistEnd
    
    ml_toConnect.append(mSegmentCurve)
    if mi_rigNull:
        mRigNull = mi_rigNull
        mSegmentCurve.p_parent = mi_rigNull
        _str_rigNull = mi_rigNull.mNode
        for mObj in ml_toConnect:
            mObj.overrideEnabled = 1
            cgmMeta.cgmAttr(_str_rigNull,'gutsVis',lock=False).doConnectOut("%s.%s"%(mObj.mNode,'overrideVisibility'))
            cgmMeta.cgmAttr(_str_rigNull,'gutsLock',lock=False).doConnectOut("%s.%s"%(mObj.mNode,'overrideDisplayType'))    
            mObj.parent = mRigNull            
    return _res




def addSplineTwist(ikHandle = None, midHandle = None, advancedTwistSetup = False, orientation = 'zyx'):
    """
    ikHandle(arg)
    advancedTwistSetup(bool) -- Whether to setup ramp setup or not (False)
    """
    _str_func = 'addSplineTwist'
    
    #>>> Data gather and arg check
    mIKHandle = cgmMeta.validateObjArg(ikHandle,'cgmObject',noneValid=False)
    mMidHandle = cgmMeta.validateObjArg(midHandle,'cgmObject',noneValid=True)
    
    if mIKHandle.getMayaType() != 'ikHandle':
        raise ValueError,("|{0}| >> Not an ikHandle ({2}). Type: {1}".format(_str_func, mIKHandle.getMayaType(), mIKHandle.p_nameShort))                                                    
    if mMidHandle and mMidHandle.getMayaType() != 'ikHandle':
        raise ValueError,("|{0}| >> Mid ({2}) not an ikHandle. Type: {1}".format(_str_func, mMidHandle.getMayaType(),mMidHandle.p_nameShort))                                                    

    ml_handles = [mIKHandle]
    if mMidHandle:
        ml_handles.append(mMidHandle)
        
        if advancedTwistSetup:
            log.warning("|{0}| >> advancedTwistSetup not supported with midTwist setup currently. Using no advanced setup.".format(_str_func))                                                        
            advancedTwistSetup = False
        
    mi_crv = cgmMeta.validateObjArg(ATTR.get_driver("%s.inCurve"%mIKHandle.mNode,getNode=True),'cgmObject',noneValid=False)
    
    #pprint.pprint(vars())

    mPlug_start = cgmMeta.cgmAttr(mi_crv.mNode,'twistStart',attrType='float',keyable=True, hidden=False)
    mPlug_end = cgmMeta.cgmAttr(mi_crv.mNode,'twistEnd',attrType='float',keyable=True, hidden=False)
    d_return = {"mPlug_start":mPlug_start,"mPlug_end":mPlug_end}    
    
    if not advancedTwistSetup:
        mPlug_twist = cgmMeta.cgmAttr(mIKHandle.mNode,'twist',attrType='float',keyable=True, hidden=False)
    else:
        mi_ramp = cgmMeta.cgmNode(nodeType= 'ramp')
        mi_ramp.doStore('cgmName',mIKHandle)
        mi_ramp.doName()     
        mlPlugs_twist = []
        
        for mHandle in ml_handles:
            mHandle.dTwistControlEnable = True
            mHandle.dTwistValueType = 2
            mHandle.dWorldUpType = 7
            mPlug_twist = cgmMeta.cgmAttr(mHandle,'dTwistRampMult')
            mlPlugs_twist.append(mPlug_twist)
    
            #Fix Ramp
            ATTR.connect("{0}.outColor".format(mi_ramp.mNode),"{0}.dTwistRamp".format(mHandle.mNode))
            d_return['mRamp'] = mi_ramp    
        
    d_return['mPlug_twist']=mPlug_twist
    
    
    if midHandle:
        log.debug("|{0}| >> midHandle mode...".format(_str_func))    
        """
        $sumBase = chain_0.rotateZ + chain_1.rotateZ;
        test_mid_ikH.roll = $sumBase;
        test_mid_ikH.twist = resultCurve_splineIKCurve_splineIKCurve.twistEnd - $sumBase;        
        """

        mPlug_mid = cgmMeta.cgmAttr(mi_crv.mNode,'twistMid',attrType='float',keyable=True, hidden=False)
        mPlug_midResult = cgmMeta.cgmAttr(mi_crv.mNode,'twistMid_result',attrType='float',keyable=True, hidden=False)
        mPlug_midDiff = cgmMeta.cgmAttr(mi_crv.mNode,'twistMid_diff',attrType='float',keyable=True, hidden=False)
        mPlug_midDiv = cgmMeta.cgmAttr(mi_crv.mNode,'twistMid_div',attrType='float',keyable=True, hidden=False)
       
        #First Handle ----------------------------------------------------------------------------------------
        
        arg1 = "{0} = {1} - {2}".format(mPlug_midDiff.p_combinedName,
                                        mPlug_end.p_combinedName,
                                        mPlug_start.p_combinedName)    
        arg2 = "{0} = {1} / 2".format(mPlug_midDiv.p_combinedName,
                                      mPlug_midDiff.p_combinedName)
        arg3 = "{0} = {1} + {2}".format(mPlug_midResult.p_combinedName,
                                        mPlug_midDiv.p_combinedName,
                                        mPlug_mid.p_combinedName)
        
        for a in arg1,arg2,arg3:
            NODEFAC.argsToNodes(a).doBuild()
        
        d_return['mPlug_mid'] = mPlug_mid
        d_return['mPlug_midResult'] = mPlug_midResult
        
        mPlug_start.doConnectOut("{0}.roll".format(mIKHandle.mNode))     
        mPlug_midResult.doConnectOut("{0}.twist".format(mIKHandle.p_nameShort))
        

        #Second Handle --------------------------------------------------------------------------------
        mPlug_midSum = cgmMeta.cgmAttr(mi_crv.mNode,'twistMid_sum',attrType='float',keyable=True, hidden=False)
        mPlug_midTwist = cgmMeta.cgmAttr(mi_crv.mNode,'twistMid_twist',attrType='float',keyable=True, hidden=False)
        
        ml_joints = mIKHandle.msgList_get('drivenJoints',asMeta = True)
        mPlug_midSum.doConnectOut("{0}.roll".format(mMidHandle.p_nameShort))
        mPlug_midTwist.doConnectOut("{0}.twist".format(mMidHandle.p_nameShort))
        
        arg1 = "{0} = {1}".format(mPlug_midSum.p_combinedName,
                                  ' + '.join(["{0}.r{1}".format(mJnt.p_nameShort,orientation[0]) for mJnt in ml_joints]))
        log.debug(arg1)
        arg2 = "{0} = {1} - {2}".format(mPlug_midTwist.p_combinedName,
                                        mPlug_end.p_combinedName,
                                        mPlug_midSum.p_combinedName)
        for a in arg1,arg2:
            NODEFAC.argsToNodes(a).doBuild()
        
        """arg1 = "{0}.twist = if {1} > {2}: {3} else {4}".format(mMidHandle.p_nameShort,
                                                               mPlug_start.p_combinedName,
                                                               mPlug_end.p_combinedName,                                                               
                                                               mPlug_endMidDiffResult.p_combinedName,
                                                               mPlug_endMidDiffNegResult.p_combinedName)"""        
        
        #Second roll...
        
        
        """
        arg1 = "{0}.twist = {1} - {2}".format(mMidHandle.p_nameShort,
                                              mPlug_end.p_combinedName,
                                              mPlug_midNegResult.p_combinedName)
        """
        
        
    else:
        mPlug_start.doConnectOut("%s.roll"%mIKHandle.mNode)
        #ikHandle1.twist = (ikHandle1.roll *-.77) + curve4.twistEnd # to implement
        arg1 = "{0} = {1} - {2}".format(mPlug_twist.p_combinedName,
                                        mPlug_end.p_combinedName,
                                        mPlug_start.p_combinedName)
        NODEFAC.argsToNodes(arg1).doBuild()
        
        
    
    if advancedTwistSetup:
        mc.select(mi_ramp.mNode)
        for c in mc.ls("%s.colorEntryList[*]"%mi_ramp.mNode,flatten = True):
            log.debug( mc.removeMultiInstance( c, b = True) )
        mc.setAttr("%s.colorEntryList[0].color"%mi_ramp.mNode,0, 0, 0)
        mc.setAttr("%s.colorEntryList[1].color"%mi_ramp.mNode,1, 1, 1)
        mc.setAttr("%s.colorEntryList[1].position"%mi_ramp.mNode,1)

        mPlug_existingTwistType = cgmMeta.cgmAttr(mi_ramp,'interpolation')
        mPlug_twistType = cgmMeta.cgmAttr(mi_crv,'twistType', attrType = 'enum', enum = ":".join(mPlug_existingTwistType.p_enum))
        mPlug_twistType.doConnectOut(mPlug_existingTwistType.p_combinedName)	
    else:
        mPlug_existingTwistType = cgmMeta.cgmAttr(mIKHandle,'twistType')
        mPlug_twistType = cgmMeta.cgmAttr(mi_crv,'twistType', attrType = 'enum', enum = ":".join(mPlug_existingTwistType.p_enum))
        mPlug_twistType.twistType = 'linear'	
        
        for mHandle in ml_handles:
            mPlug_twistType.doConnectOut("{0}.twistType".format(mHandle.mNode))	
            
    return d_return






def addSplineTwistOLD(ikHandle, midHandle = None, advancedTwistSetup = False):
    """
    ikHandle(arg)
    advancedTwistSetup(bool) -- Whether to setup ramp setup or not (False)
    """
    #>>> Data gather and arg check
    mIKHandle = cgmMeta.validateObjArg(ikHandle,cgmMeta.cgmObject,noneValid=False)
    if mIKHandle.getMayaType() != 'ikHandle':
        raise StandardError,"IKHandle_fixTwist>>> '%s' object not 'ikHandle'. Found type: %s"%(mIKHandle.getShortName(),mIKHandle.getMayaType())

    mi_crv = cgmMeta.validateObjArg(ATTR.get_driver("%s.inCurve"%mIKHandle.mNode,getNode=True),cgmMeta.cgmObject,noneValid=False)
    log.debug(mi_crv.mNode)

    mPlug_start = cgmMeta.cgmAttr(mi_crv.mNode,'twistStart',attrType='float',keyable=True, hidden=False)
    mPlug_end = cgmMeta.cgmAttr(mi_crv.mNode,'twistEnd',attrType='float',keyable=True, hidden=False)
    #mPlug_equalizedRoll = cgmMeta.cgmAttr(mIKHandle.mNode,'result_twistEqualized',attrType='float',keyable=True, hidden=False)
    d_return = {"mi_plug_start":mPlug_start,"mi_plug_end":mPlug_end}    
    if not advancedTwistSetup:
        mPlug_twist = cgmMeta.cgmAttr(mIKHandle.mNode,'twist',attrType='float',keyable=True, hidden=False)	
    else:
        mIKHandle.dTwistControlEnable = True
        mIKHandle.dTwistValueType = 2
        mIKHandle.dWorldUpType = 7
        mPlug_twist = cgmMeta.cgmAttr(mIKHandle,'dTwistRampMult')
        mi_ramp = cgmMeta.cgmNode(nodeType= 'ramp')
        mi_ramp.doStore('cgmName',mIKHandle)
        mi_ramp.doName()

        #Fix Ramp
        ATTR.connect("%s.outColor"%mi_ramp.mNode,"%s.dTwistRamp"%mIKHandle.mNode)
        d_return['mi_ramp'] = mi_ramp

    mPlug_start.doConnectOut("%s.roll"%mIKHandle.mNode)
    d_return['mi_plug_twist']=mPlug_twist
    #ikHandle1.twist = (ikHandle1.roll *-.77) + curve4.twistEnd # to implement
    arg1 = "%s = %s - %s"%(mPlug_twist.p_combinedName,mPlug_end.p_combinedName,mPlug_start.p_combinedName)
    log.debug("arg1: '%s'"%arg1)    
    log.debug( NODEFAC.argsToNodes(arg1).doBuild() )       

    if advancedTwistSetup:
        mc.select(mi_ramp.mNode)
        log.debug( mc.attributeInfo("%s.colorEntryList"%mi_ramp.mNode) )
        for c in mc.ls("%s.colorEntryList[*]"%mi_ramp.mNode,flatten = True):
            log.debug(c)
            log.debug( mc.removeMultiInstance( c, b = True) )
        mc.setAttr("%s.colorEntryList[0].color"%mi_ramp.mNode,0, 0, 0)
        mc.setAttr("%s.colorEntryList[1].color"%mi_ramp.mNode,1, 1, 1)
        mc.setAttr("%s.colorEntryList[1].position"%mi_ramp.mNode,1)

        mPlug_existingTwistType = cgmMeta.cgmAttr(mi_ramp,'interpolation')
        mPlug_twistType = cgmMeta.cgmAttr(mi_crv,'twistType', attrType = 'enum', enum = ":".join(mPlug_existingTwistType.p_enum))
        mPlug_twistType.doConnectOut(mPlug_existingTwistType.p_combinedName)	
    else:
        mPlug_existingTwistType = cgmMeta.cgmAttr(mIKHandle,'twistType')
        mPlug_twistType = cgmMeta.cgmAttr(mi_crv,'twistType', attrType = 'enum', enum = ":".join(mPlug_existingTwistType.p_enum))
        mPlug_twistType.twistType = 'linear'	
        mPlug_twistType.doConnectOut(mPlug_existingTwistType.p_combinedName)	
    return d_return




def buildFKIK(fkJoints = None,
              ikJoints = None,
              blendJoints = None,
              settings = None,
              orientation = 'zyx',
              ikControl = None,
              ikMid = None,
              mirrorDirection = 'Left',
              globalScalePlug = 'PLACER.scaleY',
              fkGroup = None,
              ikGroup = None):

    ml_blendJoints = cgmMeta.validateObjListArg(blendJoints,'cgmObject')
    ml_fkJoints = cgmMeta.validateObjListArg(fkJoints,'cgmObject')
    ml_ikJoints = cgmMeta.validateObjListArg(ikJoints,'cgmObject')

    mi_settings = cgmMeta.validateObjArg(settings,'cgmObject')

    aimVector = VALID.simpleAxis("%s+"%orientation[0]).p_vector#dictionary.stringToVectorDict.get("%s+"%self._go._jointOrientation[0])
    upVector = VALID.simpleAxis("%s+"%orientation[1]).p_vector#dictionary.stringToVectorDict.get("%s+"%self._go._jointOrientation[1])
    outVector = VALID.simpleAxis("%s+"%orientation[2]).p_vector#dictionary.stringToVectorDict.get("%s+"%self._go._jointOrientation[2])


    mControlIK = cgmMeta.validateObjArg(ikControl,'cgmObject')
    mControlMidIK = cgmMeta.validateObjArg(ikMid,'cgmObject')
    mPlug_lockMid = cgmMeta.cgmAttr(mControlMidIK,'lockMid',attrType='float',defaultValue = 0,keyable = True,minValue=0,maxValue=1.0)


    #for more stable ik, we're gonna lock off the lower channels degrees of freedom
    for chain in [ml_ikJoints]:
        for axis in orientation[:2]:
            for i_j in chain[1:]:
                ATTR.set(i_j.mNode,"jointType%s"%axis.upper(),1)


    ml_toParentChains = []
    ml_fkAttachJoints = []   
    """
    self.ml_toParentChains = []
    self.ml_fkAttachJoints = []
    if self._go._str_mirrorDirection == 'Right':#mirror control setup
        self.ml_fkAttachJoints = self._go._i_rigNull.msgList_get('fkAttachJoints')
        self.ml_toParentChains.append(self.ml_fkAttachJoints)

    self.ml_toParentChains.extend([self.ml_ikJoints,self.ml_blendJoints])
    for chain in self.ml_toParentChains:
        chain[0].parent = self._go._i_constrainNull.mNode"""



    #def build_fkJointLength(self):      
    #for i,i_jnt in enumerate(self.ml_fkJoints[:-1]):
    #    rUtils.addJointLengthAttr(i_jnt,orientation=self._go._jointOrientation)

    #def build_pvIK(self):
    mPlug_globalScale = cgmMeta.validateAttrArg(globalScalePlug)['mi_plug']


    #Create no flip arm IK
    #We're gonna use the no flip stuff for the most part
    d_armPVReturn = rUtils.IKHandle_create(ml_ikJoints[0].mNode,ml_ikJoints[ikLen - 1].mNode,nameSuffix = 'PV',
                                           rpHandle=True, controlObject=mControlIK, addLengthMulti=True,
                                           globalScaleAttr=mPlug_globalScale.p_combinedName, stretch='translate',
                                           )

    mi_armIKHandlePV = d_armPVReturn['mi_handle']
    ml_distHandlesPV = d_armPVReturn['ml_distHandles']
    mRPHandlePV = d_armPVReturn['mRPHandle']
    mPlug_lockMid = d_armPVReturn['mPlug_lockMid']



    mi_armIKHandlePV.parent = mControlIK.mNode#armIK to ball		
    ml_distHandlesPV[-1].parent = mControlIK.mNode#arm distance handle to ball	
    ml_distHandlesPV[0].parent = mi_settings#hip distance handle to deform group
    ml_distHandlesPV[1].parent = mControlMidIK.mNode#elbow distance handle to midIK
    mRPHandlePV.parent = mControlMidIK


    #RP handle	
    #mRPHandlePV.doCopyNameTagsFromObject(self._go._mModule.mNode, ignore = ['cgmName','cgmType'])
    mRPHandlePV.addAttr('cgmName','elbowPoleVector',attrType = 'string')
    mRPHandlePV.doName()

    #Mid fix
    #=========================================================================================			
    mc.move(0,0,-25,mControlMidIK.mNode,r=True, rpr = True, ws = True, wd = True)#move out the midControl to fix the twist from

    #>>> Fix our ik_handle twist at the end of all of the parenting
    #rUtils.IKHandle_fixTwist(mi_armIKHandlePV)#Fix the twist

    log.info("rUtils.IKHandle_fixTwist('%s')"%mi_armIKHandlePV.getShortName())
    #Register our snap to point before we move it back
    i_ikMidMatch = RIGMETA.cgmDynamicMatch(dynObject=mControlMidIK,
                                           dynPrefix = "FKtoIK",
                                           dynMatchTargets=ml_blendJoints[1]) 	
    #>>> Reset the translations
    mControlMidIK.translate = [0,0,0]

    #Move the lock mid and add the toggle so it only works with show elbow on
    #mPlug_lockMid.doTransferTo(mControlMidIK.mNode)#move the lock mid	

    #Parent constain the ik wrist joint to the ik wrist
    #=========================================================================================				
    mc.orientConstraint(mControlIK.mNode,ml_ikJoints[ikLen-1].mNode, maintainOffset = True)	

    #Blend stuff
    #-------------------------------------------------------------------------------------
    mPlug_FKIK = cgmMeta.cgmAttr(mi_settings.mNode,'blend_FKIK',attrType='float',lock=False,keyable=True)

    if ml_fkAttachJoints:
        ml_fkUse = ml_fkAttachJoints
        for i,mJoint in enumerate(ml_fkAttachJoints):
            mc.pointConstraint(ml_fkJoints[i].mNode,mJoint.mNode,maintainOffset = False)
            #Connect inversed aim and up
            NODEFAC.connectNegativeAttrs(ml_fkJoints[i].mNode, mJoint.mNode,
                                       ["r%s"%orientation[0],"r%s"%orientation[1]]).go()
            cgmMeta.cgmAttr(ml_fkJoints[i].mNode,"r%s"%orientation[2]).doConnectOut("%s.r%s"%(mJoint.mNode,orientation[2]))
    else:
        ml_fkUse = ml_fkJoints

    rUtils.connectBlendChainByConstraint(ml_fkUse,ml_ikJoints,ml_blendJoints,
                                         driver = mPlug_FKIK.p_combinedName,l_constraints=['point','orient'])


    #>>> Settings - constrain
    #mc.parentConstraint(self.ml_blendJoints[0].mNode, self.mi_settings.masterGroup.mNode, maintainOffset = True)

    #>>> Setup a vis blend result
    mPlug_FKon = cgmMeta.cgmAttr(mi_settings,'result_FKon',attrType='float',defaultValue = 0,keyable = False,lock=True,hidden=True)	
    mPlug_IKon = cgmMeta.cgmAttr(mi_settings,'result_IKon',attrType='float',defaultValue = 0,keyable = False,lock=True,hidden=True)	

    NODEFAC.createSingleBlendNetwork(mPlug_FKIK.p_combinedName,
                                   mPlug_IKon.p_combinedName,
                                   mPlug_FKon.p_combinedName)

    mPlug_FKon.doConnectOut("%s.visibility"%fkGroup)
    mPlug_IKon.doConnectOut("%s.visibility"%ikGroup)	


    #pprint.pprint(vars())
    return True


def ribbon_createSurface(jointList=[], createAxis = 'x', sectionSpans=1, extendEnds=False):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    ACKNOWLEDMENT:
    This is a modification of the brilliant technique I got from Matt's blog - 
    http://td-matt.blogspot.com/2011/01/spine-control-rig.html?showComment=1297462382914#c3066380136039163369

    DESCRIPTION:
    Lofts a surface from a joint list

    ARGUMENTS:
    jointList(list) - list of the joints you want to loft from
    outChannel(string)['x','y','z - the the extrude out direction

    RETURNS:
    surface(string)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """

    """ return a good length for out loft curves """
    try:
        _str_func = 'ribbon_createSurface'
        mAxis_out = VALID.simpleAxis(createAxis)
        crvUp = mAxis_out.p_string
        crvDn = mAxis_out.inverse.p_string
        
        f_distance = (DIST.get_distance_between_targets([jointList[0],jointList[-1]])/ len(jointList))/2
        
        l_crvs = []
        for j in jointList:
            crv =   mc.curve (d=1, ep = [DIST.get_pos_by_axis_dist(j, crvUp, f_distance),
                                         DIST.get_pos_by_axis_dist(j, crvDn, f_distance)],
                                   os=True)
            log.debug("|{0}| >> Created: {1}".format(_str_func,crv))
            l_crvs.append(crv)
            
        if extendEnds:
            log.debug("|{0}| >> Extended ends.".format(_str_func))
            
            log.debug("|{0}| >> start...".format(_str_func))
            mJnt = cgmMeta.asMeta(jointList[0])
            mLoc = mJnt.doLoc(fastMode=True)
            pos_end = POS.get(jointList[0])
            vec_aim = MATH.get_vector_of_two_points(POS.get(jointList[1]), pos_end)
            mLoc.p_position = DIST.get_pos_by_vec_dist(pos_end, vec_aim, f_distance)
            crv =   mc.curve (d=1, ep = [DIST.get_pos_by_axis_dist(mLoc.mNode, crvUp, f_distance),
                                         DIST.get_pos_by_axis_dist(mLoc.mNode, crvDn, f_distance)],
                                   os=True)
            log.debug("|{0}| >> Created: {1}".format(_str_func,crv))
            l_crvs.insert(0,crv)
            mLoc.delete()
            
        
            log.debug("|{0}| >> end...".format(_str_func))
            mJnt = cgmMeta.asMeta(jointList[-1])
            mLoc = mJnt.doLoc(fastMode=True)
            pos_end = POS.get(jointList[-1])
            vec_aim = MATH.get_vector_of_two_points(POS.get(jointList[-2]), pos_end)
            mLoc.p_position = DIST.get_pos_by_vec_dist(pos_end, vec_aim, f_distance)
            crv =   mc.curve (d=1, ep = [DIST.get_pos_by_axis_dist(mLoc.mNode, crvUp, f_distance),
                                         DIST.get_pos_by_axis_dist(mLoc.mNode, crvDn, f_distance)],
                                   os=True)
            log.debug("|{0}| >> Created: {1}".format(_str_func,crv))
            l_crvs.append(crv)
            mLoc.delete()
            
        _res_body = mc.loft(l_crvs, reverseSurfaceNormals = True, ch = False, uniform = True, degree = 3, sectionSpans=sectionSpans)

        #_res_body = mc.loft(l_crvs, o = True, d = 1, po = 1 )
        #_inputs = mc.listHistory(_res_body[0],pruneDagObjects=True)
        #_tessellate = _inputs[0]
        
        #_d = {'format':2,#General
        #      'polygonType':1,#'quads'
        #      }
              
        #for a,v in _d.iteritems():
        #    ATTR.set(_tessellate,a,v)
        mc.delete(l_crvs)
        return _res_body
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err)
    
    
def ribbon(jointList = None,
           useSurface = None,
           extendEnds = False,
           orientation = 'zyx',
           secondaryAxis = 'y+',
           loftAxis = 'x',
           baseName = None,
           connectBy = 'constraint',
           stretchBy = 'translate',
           squashStretchMain = 'arcLength',
           squashStretch = None, 
           sectionSpans = 1, 
           driverSetup = None,#...aim.stable
           msgDriver = None,#...msgLink on joint to a driver group for constaint purposes
           settingsControl = None,
           additiveScaleEnds = False, 
           extraSquashControl = False,#...setup extra attributes
           specialMode = None,
           masterScalePlug = None,
           squashFactorMode = 'midPeak',
           squashFactorMin = 0.0,
           squashFactorMax = 1.0,
           paramaterization='blend',
           #advancedTwistSetup = False,
           #extendTwistToEnd = False,
           #reorient = False,
           skipAim = True,
           influences = None,
           tightenWeights=True,
           extraKeyable = True,
           ribbonJoints = None,
           attachEndsToInfluences = None,
           attachStartToInfluence = None,
           attachEndToInfluence = None,
           moduleInstance = None,
           parentGutsTo = None):

    """
    Root of the segment setup.
    Inspiriation from Jason Schleifer's work as well as

    http://faithofthefallen.wordpress.com/2008/10/08/awesome-spine-setup/
    on twist methods.

    Latest update - April 30, 2018

    :parameters:
        jointList(joints - None) | List or metalist of joints
        useCurve(nurbsCurve - None) | Which curve to use. If None. One Created
        extendEnd(bool) | extend the last curve loft to get meat to measure stretch with
        orientation(string - zyx) | What is the joints orientation
        secondaryAxis(maya axis arg(y+) | Only necessary when no module provide for orientating
        baseName(string - None) | baseName string
        connectBy(str)
        
        paramaterization(string)
            fixed - Hard value uv
            floating - Floating uv value from reparamterized curve
            blend - Blend of the two
        
        squashStretchMain(str)
            arcLength
            pointDist
            
        squashStretch(str)
            None
            simple - just base measure
            single - measure actual surface distance on the main axis
            both - add a second ribbon for the third axis
        
        stretchBy(string - trans/scale/None) | How the joint will scale
        
        sectionSpans(int) - default 2 - number of spans in the loft per section
        
        driverSetup(string) | Extra setup on driver
            None
            stable - two folicle stable setup
            stableBlend - two follicle with blend aim
            aim - aim along the chain
        
        squashFactorMode 
            see cgm.core.math_utils.get_blendList

        squashFactorMax
            1.0 - default
        squashFactorMin
            0.0- default
            
        specialMode
            None
            noStartEnd
            
        masterScalePlug - ONLY matters for squash and stetch setup
            None - setup a plug on the surface for it
            'create' - make a measure curve. It'll be connected to the main surface on a message attr called segScaleCurve
            attribute arg - use this plug
            
        additiveScaleEnds(bool - False) | Whether to setup end scaling to it works more as expected for ends
        advancedTwistSetup(bool - False) | Whether to do the cgm advnaced twist setup
        addMidTwist(bool - True) | Whether to setup a mid twist on the segment
        skipAim(bool - True) | Whether to setup the aim scale or not
        
        influences(joints - None) | List or metalist of joints to skin our objects to
        attachEndsToInfluences(bool) - Connect the first and last joint to the influence 0,-1. Still use scale setup.
        
        moduleInstance(cgmModule - None) | cgmModule to use for connecting on build
        extendTwistToEnd(bool - False) | Whether to extned the twist to the end by default

    :returns:
        mIKHandle, mIKEffector, mIKSolver, mi_splineCurve
        

    :raises:
        Exception | if reached

    """   	 
    #try:
    _str_func = 'ribbon'
    ml_rigObjectsToConnect = []
    ml_rigObjectsToParent = []
    
    #try:
    #>>> Verify =============================================================================================
    ml_joints = cgmMeta.validateObjListArg(jointList,mType = 'cgmObject', mayaType=['joint'], noneValid = False)
    l_joints = [mJnt.mNode for mJnt in ml_joints]
    int_lenJoints = len(ml_joints)#because it's called repeatedly
    
    if ribbonJoints is None:
        ml_ribbonJoints = ml_joints
        l_ribbonJoints = l_joints
    else:
        ml_ribbonJoints = cgmMeta.validateObjListArg(ribbonJoints,mType = 'cgmObject', mayaType=['joint'], noneValid = False)
        l_ribbonJoints = [mJnt.mNode for mJnt in ml_ribbonJoints]
    
    mi_useSurface = cgmMeta.validateObjArg(useSurface,mayaType=['nurbsSurface'],noneValid = True)
    mi_mayaOrientation = VALID.simpleOrientation(orientation)
    str_orientation = mi_mayaOrientation.p_string
    str_secondaryAxis = VALID.stringArg(secondaryAxis,noneValid=True)
    str_baseName = VALID.stringArg(baseName,noneValid=True)
    
    if specialMode and specialMode not in ['noStartEnd']:
        raise ValueError,"Unknown special mode: {0}".format(specialMode)
    
    
    ml_influences = cgmMeta.validateObjListArg(influences,mType = 'cgmObject', noneValid = True)
    if ml_influences:
        l_influences = [mObj.p_nameShort for mObj in ml_influences]
        int_lenInfluences = len(l_influences)#because it's called repeatedly    
    
    if attachEndsToInfluences:
        if attachStartToInfluence == None:
            attachStartToInfluence = True
        if attachEndToInfluence == None:
            attachStartToInfluence = True
    #module -----------------------------------------------------------------------------------------------
    mModule = cgmMeta.validateObjArg(moduleInstance,noneValid = True)
    #try:mModule.isModule()
    #except:mModule = False

    mi_rigNull = False	
    if mModule:
        log.debug("|{0}| >> Module found. mModule: {1}...".format(_str_func,mModule))                                    
        mi_rigNull = mModule.rigNull	
        if str_baseName is None:
            str_baseName = mModule.getPartNameBase()#Get part base name	    
    if not str_baseName:str_baseName = 'testRibbon' 
    #...
    
    #str_stretchBy = VALID.stringArg(stretchBy,noneValid=True)		
    #b_advancedTwistSetup = VALID.boolArg(advancedTwistSetup)
    #b_extendTwistToEnd= VALID.boolArg(extendTwistToEnd)

    #if int_lenJoints<3:
        #pprint.pprint(vars())
        #raise ValueError,"needs at least three joints"
    
    if parentGutsTo is None:
        mGroup = cgmMeta.cgmObject(name = 'newgroup')
        mGroup.addAttr('cgmName', str(str_baseName), lock=True)
        mGroup.addAttr('cgmTypeModifier','segmentStuff', lock=True)
        mGroup.doName()
    else:
        mGroup = cgmMeta.validateObjArg(parentGutsTo,'cgmObject',False)
        
        
    if mModule:
        mGroup.parent = mModule.rigNull

    if additiveScaleEnds and not extendEnds:
        extendEnds=True


    #Good way to verify an instance list? #validate orientation             
    #> axis -------------------------------------------------------------
    axis_aim = VALID.simpleAxis("{0}+".format(str_orientation[0]))
    axis_aimNeg = axis_aim.inverse
    axis_up = VALID.simpleAxis("{0}+".format(str_orientation [1]))
    axis_out = VALID.simpleAxis("{0}+".format(str_orientation [2]))

    v_aim = axis_aim.p_vector#aimVector
    v_aimNeg = axis_aimNeg.p_vector#aimVectorNegative
    v_up = axis_up.p_vector   #upVector
    v_out = axis_out.p_vector
    
    str_up = axis_up.p_string
    
    loftAxis2 = False
    #Figure out our loft axis stuff
    if loftAxis not in  orientation:
        _lower_loftAxis = loftAxis.lower()
        if _lower_loftAxis in ['out','up']:
            if _lower_loftAxis == 'out':
                loftAxis = str_orientation[2]
            else:
                loftAxis = str_orientation[1]
        else:
            raise ValueError,"Not sure what to do with loftAxis: {0}".format(loftAxis)
    
    #Ramp values -------------------------------------------------------------------------
    if extraSquashControl:
        l_scaleFactors = MATH.get_blendList(int_lenJoints,squashFactorMax,squashFactorMin,squashFactorMode)
    
    #Squash stretch -------------------------------------------------------------------------
    b_squashStretch = False
    if squashStretch is not None:
        b_squashStretch = True
        if squashStretch == 'both':
            loftAxis2 = str_orientation[1]
            
        """
        mTransGroup = cgmMeta.cgmObject(name = 'newgroup')
        mTransGroup.addAttr('cgmName', str(str_baseName), lock=True)
        mTransGroup.addAttr('cgmTypeModifier','segmentTransStuff', lock=True)
        mTransGroup.doName()"""
        
        
        
    outChannel = str_orientation[2]#outChannel
    upChannel = str_orientation[1]
    #upChannel = '{0}up'.format(str_orientation[1])#upChannel
    l_param = []  
    
    
    mControlSurface2 = False
    ml_surfaces = []
    
    #>>> Ribbon Surface ================================================================================        
    if mi_useSurface:
        raise NotImplementedError,'Not done with passed surface'
    else:
        log.debug("|{0}| >> Creating surface...".format(_str_func))
        l_surfaceReturn = ribbon_createSurface(l_ribbonJoints,loftAxis,sectionSpans,extendEnds)
    
        mControlSurface = cgmMeta.validateObjArg( l_surfaceReturn[0],'cgmObject',setClass = True )
        mControlSurface.addAttr('cgmName',str(baseName),attrType='string',lock=True)    
        mControlSurface.addAttr('cgmType','controlSurface',attrType='string',lock=True)
        mControlSurface.doName()
        
        ml_surfaces.append(mControlSurface)
        
        if loftAxis2:
            log.debug("|{0}| >> Creating surface...".format(_str_func))
            l_surfaceReturn2 = ribbon_createSurface(l_ribbonJoints,loftAxis2,sectionSpans,extendEnds)
        
            mControlSurface2 = cgmMeta.validateObjArg( l_surfaceReturn[0],'cgmObject',setClass = True )
            mControlSurface2.addAttr('cgmName',str(baseName),attrType='string',lock=True)
            mControlSurface2.addAttr('cgmTypeModifier','up',attrType='string',lock=True)
            mControlSurface2.addAttr('cgmType','controlSurface',attrType='string',lock=True)
            mControlSurface2.doName()
    
            ml_surfaces.append(mControlSurface2)
    
    log.debug("mControlSurface: {0}".format(mControlSurface))
    _surf_shape = mControlSurface.getShapes()[0]
    minU = ATTR.get(_surf_shape,'minValueU')
    maxU = ATTR.get(_surf_shape,'maxValueU')
    minV = ATTR.get(_surf_shape,'minValueV')
    maxV = ATTR.get(_surf_shape,'maxValueV')
    
    ml_toConnect = []
    ml_toConnect.extend(ml_surfaces)
    
    mArcLenCurve = None
    mArcLenDag = None
    
    if b_squashStretch and squashStretchMain == 'arcLength':
        log.debug("|{0}| >> Creating arc curve setup...".format(_str_func))
        
        minV = ATTR.get(_surf_shape,'minValueV')
        maxV = ATTR.get(_surf_shape,'maxValueV')
        
        plug = '{0}_segScale'.format(str_baseName)
        plug_dim = '{0}_arcLengthDim'.format(str_baseName)
        plug_inverse = '{0}_segInverseScale'.format(str_baseName)
        
        mArcLen = cgmMeta.validateObjArg(mc.createNode('arcLengthDimension'),setClass=True)
        mArcLenDag = mArcLen.getTransform(asMeta=True)
        
        mArcLen.uParamValue = MATH.average(minU,maxU)
        mArcLen.vParamValue = maxV
        mArcLenDag.rename('{0}_arcLengthNode'.format(str_baseName))
        
        mControlSurface.connectChildNode(mArcLen.mNode,plug_dim,'arcLenDim')

        log.debug("|{0}| >> created: {1}".format(_str_func,mArcLen)) 

        #infoNode = CURVES.create_infoNode(mCrv.mNode)
        
        ATTR.connect("{0}.worldSpace".format(mControlSurface.getShapes()[0]), "{0}.nurbsGeometry".format(mArcLen.mNode))

        mArcLen.addAttr('baseDist', mArcLen.arcLengthInV,attrType='float',lock=True)
        log.debug("|{0}| >> baseDist: {1}".format(_str_func,mArcLen.baseDist)) 

        mPlug_inverseScale = cgmMeta.cgmAttr(mArcLen.mNode,plug_inverse,'float')
        
        l_argBuild=[]
        
        """
        if not masterScalePlug or masterScalePlug == 'create':
            plug_master = '{0}_segMasterScale'.format(str_baseName)
            mPlug_masterScale = cgmMeta.cgmAttr(mArcLen.mNode,plug_master,'float')
            l_argBuild.append("{0} = {1} / {2}".format(mPlug_masterScale.p_combinedName,
                                                       '{0}.arcLengthInV'.format(mArcLen.mNode),
                                                       "{0}.baseDist".format(mArcLen.mNode)))
            masterScalePlug = mPlug_masterScale"""
            
        
        """
        l_argBuild.append("{0} = {1} / {2}".format(mPlug_masterScale.p_combinedName,
                                                   '{0}.arcLength'.format(mInfoNode.mNode),
                                                   "{0}.baseDist".format(mCrv.mNode)))"""
        
        #l_argBuild.append("{0} = {2} / {1}".format(mPlug_inverseScale.p_combinedName,

        l_argBuild.append("{0} = {2} / {1}".format(mPlug_inverseScale.p_combinedName,
                                                   '{0}.arcLengthInV'.format(mArcLen.mNode),
                                                   "{0}.baseDist".format(mArcLen.mNode)))        
        
        
        for arg in l_argBuild:
            log.debug("|{0}| >> Building arg: {1}".format(_str_func,arg))
            NODEFAC.argsToNodes(arg).doBuild()
            
    #Settings ... ----------------------------------------------------------------------------------------
    if settingsControl:
        mSettings = cgmMeta.validateObjArg(settingsControl,'cgmObject')
    else:
        mSettings = mControlSurface
    
    
    #Reparam ----------------------------------------------------------------------------------------
    mCrv_reparam = False
    str_paramaterization = str(paramaterization).lower()
    if str_paramaterization in ['blend','floating']:
        log.debug("|{0}| >> Reparameterization curve needed...".format(_str_func))
        #crv = CORERIG.create_at(None,'curve',l_pos= [mJnt.p_position for mJnt in ml_joints])
        _crv = mc.duplicateCurve("{0}.u[{1}]".format(_surf_shape,MATH.median(minU,maxU)),
                                 ch = 1,
                                 rn = 0,
                                 local = 0)
        

        mCrv_reparam = cgmMeta.validateObjArg(_crv[0],setClass=True)
        mCrv_reparam.doStore("cgmName","{0}_reparam".format(str_baseName))
        mCrv_reparam.doName()        
        cgmMeta.cgmNode(_crv[1]).doName()
        
        mc.rebuildCurve(mCrv_reparam.mNode, d=3, keepControlPoints=False,ch=1,n="reparamRebuild")
        #cubic keepC
        md_floatTrackGroups = {}
        md_floatTrackNodes = {}
        md_floatParameters = {}
        d_vParameters = {}
        
        mCrv_reparam.p_parent = mGroup
        
        l_argBuild = []
        mPlug_vSize = cgmMeta.cgmAttr(mControlSurface.mNode,
                                      "{0}_vSize".format(str_baseName),
                                      attrType = 'float',
                                      hidden = False,
                                      lock=False)
        
        l_argBuild.append("{0} = {1} - {2}".format(mPlug_vSize.p_combinedName,
                                                   maxV,minV))        
                
        if str_paramaterization == 'blend':
            if not mSettings.hasAttr('blendParam'):
                mPlug_paramBlend = cgmMeta.cgmAttr(mSettings.mNode,
                                                   "blendParam".format(str_baseName),
                                                   attrType = 'float',
                                                   minValue=0,
                                                   maxValue=1.0,
                                                   keyable=True,
                                                   value= 1.0,
                                                   defaultValue=1.0,
                                                   hidden = False,
                                                   lock=False)
            else:
                mPlug_paramBlend = cgmMeta.cgmAttr(mSettings.mNode,"blendParam".format(str_baseName))
            md_paramBlenders = {}
        
        #Set up per joint...
        for i,mObj in enumerate(ml_joints):
            mPlug_normalized = cgmMeta.cgmAttr(mControlSurface.mNode,
                                               "{0}_normalizedV_{1}".format(str_baseName,i),
                                               attrType = 'float',
                                               hidden = False,
                                               lock=False)
            mPlug_sum = cgmMeta.cgmAttr(mControlSurface.mNode,
                                        "{0}_sumV_{1}".format(str_baseName,i),
                                        attrType = 'float',
                                        hidden = False,
                                        lock=False)            
            mLoc = mObj.doLoc()
            
            _res = RIGCONSTRAINTS.attach_toShape(mObj,mCrv_reparam.mNode,None)
            md_floatTrackGroups[i]=_res[0]
            #res_closest = DIST.create_closest_point_node(mLoc.mNode, mCrv_reparam.mNode,True)
            log.debug("|{0}| >> Closest info {1} : {2}".format(_str_func,i,_res))
            mLoc.p_parent = mGroup

            srfNode = mc.createNode('closestPointOnSurface')
            mc.connectAttr("%s.worldSpace[0]" % _surf_shape, "%s.inputSurface" % srfNode)
            mc.connectAttr("%s.translate" % _res[0], "%s.inPosition" % srfNode)
            mc.connectAttr("%s.position" % srfNode, "%s.translate" % mLoc.mNode, f=True) 
            md_floatParameters[i] = mPlug_normalized            
            mClosestPoint =  cgmMeta.validateObjArg(srfNode,setClass=True)
            mClosestPoint.doStore('cgmName',mObj)
            mClosestPoint.doName()
            md_floatTrackNodes[i] = mClosestPoint
            srfNode = mClosestPoint.mNode
            
            TRANS.parent_set(_res[0],mGroup.mNode)
            
            log.debug("|{0}| >> paramU {1} : {2}.parameterU | {3}".format(_str_func,i,srfNode,
                                                                          ATTR.get(srfNode,'parameterU')))
            log.debug("|{0}| >> paramV {1} : {2}.parameterV | {3}".format(_str_func,i,srfNode,
                                                                          ATTR.get(srfNode,'parameterV')))
            

            
            l_argBuild.append("{0} = {1} + {2}.parameterV".format(mPlug_sum.p_combinedName,
                                                                  minV,
                                                                  srfNode))
            
            l_argBuild.append("{0} = {1} / {2}".format(mPlug_normalized.p_combinedName,
                                                       mPlug_sum.p_combinedName,
                                                       mPlug_vSize.p_combinedName))
            
            
            if str_paramaterization == 'blend':
                mPlug_baseV = cgmMeta.cgmAttr(mControlSurface.mNode,
                                               "{0}_baseV_{1}".format(str_baseName,i),
                                               attrType = 'float',
                                               hidden = False,
                                               lock=False)
                mPlug_blendV = cgmMeta.cgmAttr(mControlSurface.mNode,
                                               "{0}_blendV_{1}".format(str_baseName,i),
                                               attrType = 'float',
                                               hidden = False,
                                               lock=False)
                
                mBlendNode = cgmMeta.cgmNode(nodeType = 'blendTwoAttr')
                mBlendNode.doStore('cgmName',"{0}_blendV".format(mObj.mNode))
                mBlendNode.doName()
                
                md_paramBlenders[i] = mBlendNode
                ATTR.set(md_paramBlenders[i].mNode,"input[0]",1)
                mPlug_normalized.doConnectOut("%s.input[1]"%mBlendNode.mNode)
                mPlug_paramBlend.doConnectOut("%s.attributesBlender"%mBlendNode.mNode)
                d_vParameters[i] = "{0}.output".format(mBlendNode.mNode)
                
            else:
                d_vParameters[i] = mPlug_normalized.p_combinedName

        for arg in l_argBuild:
            log.debug("|{0}| >> Building arg: {1}".format(_str_func,arg))
            NODEFAC.argsToNodes(arg).doBuild()
            
    
    mPlug_masterScale = None
    if b_squashStretch and masterScalePlug is not None:
        log.debug("|{0}| >> Checking masterScalePlug: {1}".format(_str_func, masterScalePlug))        
        if masterScalePlug == 'create':
            log.debug("|{0}| >> Creating measure curve setup...".format(_str_func))
            
            plug = 'segMasterScale'
            plug_curve = 'segMasterMeasureCurve'
            crv = CORERIG.create_at(None,'curveLinear',l_pos= [ml_joints[0].p_position, ml_joints[1].p_position])
            mCrv = cgmMeta.validateObjArg(crv,'cgmObject',setClass=True)
            mCrv.rename('{0}_masterMeasureCrv'.format( baseName))
    
            mControlSurface.connectChildNode(mCrv,plug_curve,'rigNull')
    
            log.debug("|{0}| >> created: {1}".format(_str_func,mCrv)) 
    
            infoNode = CURVES.create_infoNode(mCrv.mNode)
    
            mInfoNode = cgmMeta.validateObjArg(infoNode,'cgmNode',setClass=True)
            mInfoNode.addAttr('baseDist', mInfoNode.arcLength,attrType='float')
            mInfoNode.rename('{0}_{1}_measureCIN'.format( baseName,plug))
    
            log.debug("|{0}| >> baseDist: {1}".format(_str_func,mInfoNode.baseDist)) 
    
            mPlug_masterScale = cgmMeta.cgmAttr(mControlSurface.mNode,plug,'float')
    
            l_argBuild=[]
            l_argBuild.append("{0} = {1} / {2}".format(mPlug_masterScale.p_combinedName,
                                                       '{0}.arcLength'.format(mInfoNode.mNode),
                                                       "{0}.baseDist".format(mInfoNode.mNode)))
            for arg in l_argBuild:
                log.debug("|{0}| >> Building arg: {1}".format(_str_func,arg))
                NODEFAC.argsToNodes(arg).doBuild()                
    
        else:
            if issubclass(type(masterScalePlug),cgmMeta.cgmAttr):
                mPlug_masterScale = masterScalePlug
            else:
                d_attr = cgmMeta.validateAttrArg(masterScalePlug)
                if not d_attr:
                    raise ValueError,"Ineligible masterScalePlug: {0}".format(masterScalePlug)
                mPlug_masterScale  = d_attr['mPlug']
                
        if not mPlug_masterScale:
            raise ValueError,"Should have a masterScale plug by now"        
    elif masterScalePlug is not None:
        if issubclass(type(masterScalePlug),cgmMeta.cgmAttr):
            mPlug_masterScale = masterScalePlug
        else:
            d_attr = cgmMeta.validateAttrArg(masterScalePlug)
            if not d_attr:
                raise ValueError,"Ineligible masterScalePlug: {0}".format(masterScalePlug)
            mPlug_masterScale  = d_attr['mPlug']        
            

    
        
    #b_attachToInfluences = False
    if attachEndsToInfluences:
        log.debug("|{0}| >> attachEndsToInfluences flag. Checking...".format(_str_func))
        if influences and len(influences) > 1:
            b_attachToInfluences = True
            if attachStartToInfluence:
                b_attachStart = True
            if attachEndToInfluence:
                b_attachEnd = True
        #log.debug("|{0}| >> b_attachToInfluences: {1}".format(_str_func,b_attachToInfluences))
        
    
    #>>> Follicles ======================================================================================        
    log.debug("|{0}| >> Follicles...".format(_str_func)+cgmGEN._str_subLine)
    
    ml_follicles = []
    ml_follicleShapes = []
    ml_upGroups = []
    ml_aimDrivers = []
    ml_upTargets = []
    ml_folliclesStable = []
    ml_folliclesStableShapes = []
    

    f_offset = DIST.get_distance_between_targets(l_joints,True)
    
    range_joints = range(len(ml_joints))
    l_firstLastIndices = [range_joints[0],range_joints[-1]]
    
    
    for i,mJnt in enumerate(ml_joints):
        log.debug("|{0}| >> On: {1}".format(_str_func,mJnt))        
        
        mDriven = mJnt
        if specialMode == 'noStartEnd' and mJnt in [ml_joints[0],ml_joints[-1]]:
            pass
        else:
            if msgDriver:
                log.debug("|{0}| >> Checking msgDriver: {1}".format(_str_func,msgDriver))                
                mDriven = mJnt.getMessage(msgDriver,asMeta=True)
                if not mDriven:
                    raise ValueError,"Missing msgDriver: {0} | {1}".format(msgDriver,mJnt)
                mDriven = mDriven[0]
                log.debug("|{0}| >> Found msgDriver: {1} | {2}".format(_str_func,msgDriver,mDriven))
                
        log.debug("|{0}| >> Attaching mDriven: {1}".format(_str_func,mDriven))
        
        _res = RIGCONSTRAINTS.attach_toShape(mDriven.mNode, mControlSurface.mNode, None)
        mFollicle = _res[-1]['mFollicle']#cgmMeta.asMeta(follicle)
        mFollShape = _res[-1]['mFollicleShape']#cgmMeta.asMeta(shape)
        
        if mCrv_reparam:
            if str_paramaterization == 'blend':
                ATTR.set(md_paramBlenders[i].mNode,"input[0]",mFollShape.parameterV)
            ATTR.connect(d_vParameters[i],
                         '{0}.parameterV'.format(mFollShape.mNode))
            

        
        ml_follicleShapes.append(mFollShape)
        ml_follicles.append(mFollicle)
        
        mFollicle.parent = mGroup.mNode

        if mModule:#if we have a module, connect vis
            mFollicle.overrideEnabled = 1
            cgmMeta.cgmAttr(mModule.rigNull.mNode,'gutsVis',lock=False).doConnectOut("%s.%s"%(mFollicle.mNode,'overrideVisibility'))
            cgmMeta.cgmAttr(mModule.rigNull.mNode,'gutsLock',lock=False).doConnectOut("%s.%s"%(mFollicle.mNode,'overrideDisplayType'))    
            
        mDriver = mFollicle
        
        if specialMode == 'noStartEnd' and mJnt in [ml_joints[0],ml_joints[-1]]:
            log.debug("|{0}| >> noStartEnd skip: {1}".format(_str_func,mJnt))
            ml_aimDrivers.append(mDriver)
            ml_upGroups.append(False)
            ml_upTargets.append(False)                        
            continue
        
        if driverSetup:
            mDriver = mJnt.doCreateAt(setClass=True)
            mDriver.rename("{0}_aimDriver".format(mFollicle.p_nameBase))
            mDriver.parent = mFollicle
            mUpGroup = mDriver.doGroup(True,asMeta=True,typeModifier = 'up')
            
            ml_aimDrivers.append(mDriver)
            ml_upGroups.append(mUpGroup)
            
            if driverSetup in ['stable','stableBlend']:
                mUpDriver = mJnt.doCreateAt(setClass=True)
                mDriver.rename("{0}_upTarget".format(mFollicle.p_nameBase))                    
                pos = DIST.get_pos_by_axis_dist(mJnt.mNode, str_up, f_offset)
                mUpDriver.p_position = pos
                mUpDriver.p_parent = mUpGroup
                
                ml_upTargets.append(mUpDriver)
                
        #Simple contrain
        mUse = mDriver
        if attachStartToInfluence and mJnt == ml_joints[0]:
            mUse = ml_influences[0]
            #mc.parentConstraint([mUse.mNode], mDriven.mNode, maintainOffset=True)            
            
        elif attachEndToInfluence and mJnt == ml_joints[-1]:
            mUse = ml_influences[-1]
            #mc.parentConstraint([mUse.mNode], mDriven.mNode, maintainOffset=True)            
            
        #if b_attachToInfluences and mJnt in [ml_joints[0],ml_joints[-1]]:
        #    if mJnt == ml_joints[0]:
        #        mUse = ml_influences[0]
        #    else:
        #        mUse = ml_influences[-1]
        #    mc.parentConstraint([mUse.mNode], mDriven.mNode, maintainOffset=True)            
        #else:
            #mc.parentConstraint([mDriver.mNode], mDriven.mNode, maintainOffset=True)
            
        mc.parentConstraint([mUse.mNode], mDriven.mNode, maintainOffset=True)            
        
        mDriven.doStore('ribbonDriver',mDriver.mNode,attrType='msg')
        
    if extendEnds or additiveScaleEnds:
        #End follicle...
        _surf_shape = mControlSurface.getShapes()[0]
        log.debug("|{0}| >> maxV follicle...".format(_str_func)+cgmGEN._str_subLine)                    
        maxV = ATTR.get(_surf_shape,'maxValueV')
        
        l_FollicleInfo = NODES.createFollicleOnMesh( mControlSurface.mNode )
                   
        mFollicle = cgmMeta.asMeta(l_FollicleInfo[1],'cgmObject',setClass=True)
        mFollicleShape = cgmMeta.asMeta(l_FollicleInfo[0],'cgmNode')
        
        mFollicle.parent = mGroup.mNode
        
        #> Name...
        mFollicle.rename('{0}_maxV'.format(ml_joints[-1].p_nameBase))
    
        mFollicleShape.parameterU = ml_follicleShapes[-1].parameterU
        mFollicleShape.parameterV = maxV
        
        ml_follicles.append(mFollicle)
        ml_follicleShapes.append(mFollicleShape)
        
        mFollicleMaxV = mFollicle
        mFollicleMaxVShape = mFollicleShape
        
        if additiveScaleEnds:
            log.debug("|{0}| >> minV Follicle...".format(_str_func)+cgmGEN._str_subLine)                    
            
            #Start follicle
            minV = ATTR.get(_surf_shape,'minValueV')
            
            l_FollicleInfo = NODES.createFollicleOnMesh( mControlSurface.mNode )
            mFollicle = cgmMeta.asMeta(l_FollicleInfo[1],'cgmObject',setClass=True)
            mFollicleShape = cgmMeta.asMeta(l_FollicleInfo[0],'cgmNode')
            
            mFollicle.parent = mGroup.mNode
            
            #> Name...
            mFollicle.rename('{0}_minV'.format(ml_joints[0].p_nameBase))
        
            mFollicleShape.parameterU = ml_follicleShapes[0].parameterU
            mFollicleShape.parameterV = minV
            
            ml_follicles.append(mFollicle)
            ml_follicleShapes.append(mFollicleShape)
            
            mFollicleMinV = mFollicle
            mFollicleMinVShape = mFollicleShape            
        
        
        
        
    
    if ml_aimDrivers:
        log.debug("|{0}| >> aimDrivers...".format(_str_func)+cgmGEN._str_subLine)            
        if driverSetup == 'aim':
            for i,mDriver in enumerate(ml_aimDrivers):
                if specialMode == 'noStartEnd' and i in l_firstLastIndices:
                    log.debug("|{0}| >> noStartEnd skip: {1}".format(_str_func,mDriver))                    
                    continue
                    
                v_aimUse = v_aim
                if mDriver == ml_aimDrivers[-1] and not extendEnds:
                    s_aim = ml_follicles[-2].mNode
                    v_aimUse = v_aimNeg
                else:
                    s_aim = ml_follicles[i+1].mNode
            
                mc.aimConstraint(s_aim, ml_aimDrivers[i].mNode, maintainOffset = True, #skip = 'z',
                                 aimVector = v_aimUse, upVector = v_up, worldUpObject = ml_upGroups[i].mNode,
                                 worldUpType = 'objectrotation', worldUpVector = v_up)            
        else:
            for i,mDriver in enumerate(ml_aimDrivers):
                if specialMode == 'noStartEnd' and i in l_firstLastIndices:
                    log.debug("|{0}| >> noStartEnd skip: {1}".format(_str_func,mDriver))                    
                    continue                
                #We need to make new follicles
                l_stableFollicleInfo = NODES.createFollicleOnMesh( mControlSurface.mNode )
            
                mStableFollicle = cgmMeta.asMeta(l_stableFollicleInfo[1],'cgmObject',setClass=True)
                mStableFollicleShape = cgmMeta.asMeta(l_stableFollicleInfo[0],'cgmNode')
                mStableFollicle.parent = mGroup.mNode
                
                ml_folliclesStable.append(mStableFollicle)
                ml_folliclesStableShapes.append(mStableFollicleShape)
                
                #> Name...
                #mStableFollicleTrans.doStore('cgmName',mObj.mNode)
                #mStableFollicleTrans.doStore('cgmTypeModifier','surfaceStable')            
                #mStableFollicleTrans.doName()
                mStableFollicle.rename('{0}_surfaceStable'.format(ml_joints[i].p_nameBase))
            
                mStableFollicleShape.parameterU = minU
                #mStableFollicleShape.parameterV = ml_follicleShapes[i].parameterV
                ATTR.connect('{0}.parameterV'.format(ml_follicleShapes[i].mNode),
                             '{0}.parameterV'.format(mStableFollicleShape.mNode))
                
                if driverSetup == 'stable':
                    if mDriver in [ml_aimDrivers[-1]]:
                        #...now aim it
                        mc.aimConstraint(mStableFollicle.mNode, mDriver.mNode, maintainOffset = True, #skip = 'z',
                                         aimVector = v_aim, upVector = v_up, worldUpObject = ml_upTargets[i].mNode,
                                         worldUpType = 'object', worldUpVector = v_up)                     
                    else:
                        #was aimint at follicles... ml_follicles
                        mc.aimConstraint(ml_follicles[i+1].mNode, ml_aimDrivers[i].mNode, maintainOffset = True, #skip = 'z',
                                         aimVector = v_aim, upVector = v_up, worldUpObject = ml_upTargets[i].mNode,
                                         worldUpType = 'object', worldUpVector = v_up)
                elif driverSetup == 'stableBlend': #stableBlend....
                    if mDriver in [ml_aimDrivers[0],ml_aimDrivers[-1]]:
                        #...now aim it
                        mc.aimConstraint(mStableFollicle.mNode, mDriver.mNode, maintainOffset = True, #skip = 'z',
                                         aimVector = v_aim,
                                         upVector = v_up,
                                         worldUpObject = ml_upTargets[i].mNode,
                                         worldUpType = 'object', worldUpVector = v_up)
                    else:
                        mAimForward = mDriver.doCreateAt()
                        mAimForward.parent = mDriver.p_parent
                        mAimForward.doStore('cgmTypeModifier','forward')
                        mAimForward.doStore('cgmType','aimer')
                        mAimForward.doName()
                    

                        mAimBack = mDriver.doCreateAt()
                        mAimBack.parent = mDriver.p_parent
                        mAimBack.doStore('cgmTypeModifier','back')
                        mAimBack.doStore('cgmType','aimer')
                        mAimBack.doName()
                        
                        mc.aimConstraint(ml_follicles[i+1].mNode, mAimForward.mNode, maintainOffset = True, #skip = 'z',
                                         aimVector = v_aim, upVector = v_up, worldUpObject = ml_upTargets[i].mNode,
                                         worldUpType = 'object', worldUpVector = v_up)
                        mc.aimConstraint(ml_follicles[i-1].mNode, mAimBack.mNode, maintainOffset = True, #skip = 'z',
                                         aimVector = v_aimNeg, upVector = v_up, worldUpObject = ml_upTargets[i].mNode,
                                         worldUpType = 'object', worldUpVector = v_up)                        

                        mc.orientConstraint([mAimForward.mNode,mAimBack.mNode], ml_aimDrivers[i].mNode, maintainOffset=True)
                        #mc.aimConstraint(ml_follicles[i+1].mNode, ml_aimDrivers[i].mNode, maintainOffset = True, #skip = 'z',
                        #                 aimVector = v_aim, upVector = v_up, worldUpObject = ml_upTargets[i].mNode,
                        #                 worldUpType = 'object', worldUpVector = v_up)
                else:
                    pass

                    
                
        """
        if mJnt != ml_joints[-1]:
            mUpLoc = mJnt.doLoc()#Make up Loc
            mLocRotateGroup = mJnt.doCreateAt()#group in place
            mLocRotateGroup.parent = i_follicleTrans.mNode
            mLocRotateGroup.doStore('cgmName',mJnt)	    
            mLocRotateGroup.addAttr('cgmTypeModifier','rotate',lock=True)
            mLocRotateGroup.doName()
        
            #Store the rotate group to the joint
            mJnt.connectChildNode(mLocRotateGroup,'rotateUpGroup','drivenJoint')
            mZeroGrp = cgmMeta.asMeta( mLocRotateGroup.doGroup(True),'cgmObject',setClass=True )
            mZeroGrp.addAttr('cgmTypeModifier','zero',lock=True)
            mZeroGrp.doName()
            #connect some other data
            mLocRotateGroup.connectChildNode(i_follicleTrans,'follicle','drivenGroup')
            mLocRotateGroup.connectChildNode(mLocRotateGroup.parent,'zeroGroup')
            mLocRotateGroup.connectChildNode(mUpLoc,'upLoc')
        
            mc.makeIdentity(mLocRotateGroup.mNode, apply=True,t=1,r=1,s=1,n=0)
        
            mUpLoc.parent = mLocRotateGroup.mNode
            mc.move(0,10,0,mUpLoc.mNode,os=True)	
            ml_upGroups.append(mUpLoc)
        
            if mModule:#if we have a module, connect vis
                mUpLoc.overrideEnabled = 1		
                cgmMeta.cgmAttr(mModule.rigNull.mNode,'gutsVis',lock=False).doConnectOut("%s.%s"%(mUpLoc.mNode,'overrideVisibility'))
                cgmMeta.cgmAttr(mModule.rigNull.mNode,'gutsLock',lock=False).doConnectOut("%s.%s"%(mUpLoc.mNode,'overrideDisplayType'))    
        
        else:#if last...
            pass"""
    def createDist(mJnt, typeModifier = None):
        mShape = cgmMeta.cgmNode( mc.createNode ('distanceDimShape') )        
        mObject = mShape.getTransform(asMeta=True) 
        mObject.doStore('cgmName',mJnt)
        if typeModifier:
            mObject.addAttr('cgmTypeModifier',typeModifier,lock=True)                
        mObject.addAttr('cgmType','measureNode',lock=True)
        mObject.doName(nameShapes = True)
        mObject.parent = mGroup.mNode#parent it
        mObject.overrideEnabled = 1
        mObject.overrideVisibility = 1
        
        if mModule:#Connect hides if we have a module instance:
            ATTR.connect("{0}.gutsVis".format(mModule.rigNull.mNode),"{0}.overrideVisibility".format(mObject.mNode))
            ATTR.connect("{0}.gutsLock".format(mModule.rigNull.mNode),"{0}.overrideDisplayType".format(mObject.mNode))
        
        return mObject,mShape

    if b_squashStretch:
        log.debug("|{0}| >> SquashStretch...".format(_str_func)+cgmGEN._str_subLine)
        
        if extraSquashControl:
            mPlug_segScale = cgmMeta.cgmAttr(mSettings.mNode,
                                             "{0}_segScale".format(str_baseName),
                                             attrType = 'float',
                                             hidden = False,                                                 
                                             initialValue=1.0,
                                             defaultValue=1.0,
                                             keyable = extraKeyable,
                                             lock=False,
                                             minValue = 0)
            
        if squashStretchMain == 'arcLength':
            mPlug_inverseNormalized = cgmMeta.cgmAttr(mControlSurface.mNode,
                                             "{0}_normalInverse".format(str_baseName),
                                             attrType = 'float',
                                             hidden = False,)
                
            arg = "{0} = {1} * {2}".format(mPlug_inverseNormalized.p_combinedName,
                                           mPlug_inverseScale.p_combinedName,
                                           mPlug_masterScale.p_combinedName)
            NODEFAC.argsToNodes(arg).doBuild()
            
        
        log.debug("|{0}| >> Making our base dist stuff".format(_str_func))
        
        ml_distanceObjectsBase = []
        ml_distanceShapesBase = []
        
        ml_distanceObjectsActive = []
        ml_distanceShapesActive = []
        
        md_distDat = {}
        for k in ['aim','up','out']:
            md_distDat[k] = {}
            for k2 in 'base','active':
                md_distDat[k][k2] = {'mTrans':[],
                                     'mDist':[]}

        #mSegmentCurve.addAttr('masterScale',value = 1.0, minValue = 0.0001, attrType='float')
        ml_outFollicles = []
        if ml_folliclesStable:
            log.debug("|{0}| >> Found out follicles via stable...".format(_str_func))                
            ml_outFollicles = ml_folliclesStable
        elif driverSetup:
            raise ValueError,"Must create out follicles"
        
        #Up follicles =================================================================================
        ml_upFollicles = []
        ml_upFollicleShapes = []
        
        if mControlSurface2:
            log.debug("|{0}| >> up follicle setup...".format(_str_func,)+cgmGEN._str_subLine)
            
            for i,mJnt in enumerate(ml_joints):
                #We need to make new follicles
                l_FollicleInfo = NODES.createFollicleOnMesh( mControlSurface2.mNode )
            
                mUpFollicle = cgmMeta.asMeta(l_FollicleInfo[1],'cgmObject',setClass=True)
                mUpFollicleShape = cgmMeta.asMeta(l_FollicleInfo[0],'cgmNode')
                
                mUpFollicle.parent = mGroup.mNode
                
                ml_upFollicles.append(mUpFollicle)
                ml_upFollicleShapes.append(mUpFollicleShape)
                
                #> Name...
                mUpFollicle.rename('{0}_surfaceUp'.format(ml_joints[i].p_nameBase))
            
                mUpFollicleShape.parameterU = minU
                #mUpFollicleShape.parameterV = ml_follicleShapes[i].parameterV
                ATTR.connect('{0}.parameterV'.format(ml_follicleShapes[i].mNode),
                             '{0}.parameterV'.format(mUpFollicleShape.mNode))
            

            
        if squashStretch != 'simple':
            for i,mJnt in enumerate(ml_joints):#Base measure ===================================================
                """
                log.debug("|{0}| >> Base measure for: {1}".format(_str_func,mJnt))
                
                mDistanceDag,mDistanceShape = createDist(mJnt, 'base')
                mDistanceDag.p_parent = mTransGroup
                
                #Connect things
                ATTR.connect(ml_follicles[i].mNode+'.translate',mDistanceShape.mNode+'.startPoint')
                ATTR.connect(ml_follicles[i+1].mNode+'.translate',mDistanceShape.mNode+'.endPoint')
                
                ATTR.break_connection(mDistanceShape.mNode+'.startPoint')
                ATTR.break_connection(mDistanceShape.mNode+'.endPoint')
                
                md_distDat['aim']['base']['mTrans'].append(mDistanceDag)
                md_distDat['aim']['base']['mDist'].append(mDistanceShape)
                """
                if mJnt == ml_joints[-1]:
                    #use the the last....
                    md_distDat['aim']['active']['mTrans'].append(mDistanceDag)
                    md_distDat['aim']['active']['mDist'].append(mDistanceShape)                
                else:
                    #Active measures ---------------------------------------------------------------------
                    log.debug("|{0}| >> Active measure for: {1}".format(_str_func,mJnt))
                    #>> Distance nodes
                    mDistanceDag,mDistanceShape = createDist(mJnt, 'active')
        
                    #Connect things
                    #.on loc = position
                    ATTR.connect(ml_follicles[i].mNode+'.translate',mDistanceShape.mNode+'.startPoint')
                    ATTR.connect(ml_follicles[i+1].mNode+'.translate',mDistanceShape.mNode+'.endPoint')
                    
                    #ml_distanceObjectsActive.append(mDistanceDag)
                    #ml_distanceShapesActive.append(mDistanceShape)
                    md_distDat['aim']['active']['mTrans'].append(mDistanceDag)
                    md_distDat['aim']['active']['mDist'].append(mDistanceShape)
    
            if ml_outFollicles or ml_upFollicles:
                for i,mJnt in enumerate(ml_joints):
                    if ml_outFollicles:
                        """
                        #Out Base ---------------------------------------------------------------------------------
                        log.debug("|{0}| >> Out base measure for: {1}".format(_str_func,mJnt))
                        
                        mDistanceDag,mDistanceShape = createDist(mJnt, 'baseOut')
                        mDistanceDag.p_parent = mTransGroup
    
                        #Connect things
                        ATTR.connect(ml_follicles[i].mNode+'.translate',mDistanceShape.mNode+'.startPoint')
                        ATTR.connect(ml_outFollicles[i].mNode+'.translate',mDistanceShape.mNode+'.endPoint')
                        
                        ATTR.break_connection(mDistanceShape.mNode+'.startPoint')
                        ATTR.break_connection(mDistanceShape.mNode+'.endPoint')
                        
                        md_distDat['out']['base']['mTrans'].append(mDistanceDag)
                        md_distDat['out']['base']['mDist'].append(mDistanceShape)
                        """
                        
                        #ml_distanceObjectsBase.append(mDistanceDag)
                        #ml_distanceShapesBase.append(mDistanceShape)
                        
                        #Out Active---------------------------------------------------------------------------------
                        log.debug("|{0}| >> Out active measure for: {1}".format(_str_func,mJnt))
                        
                        mDistanceDag,mDistanceShape = createDist(mJnt, 'activeOut')
                                        
                        #Connect things
                        ATTR.connect(ml_follicles[i].mNode+'.translate',mDistanceShape.mNode+'.startPoint')
                        ATTR.connect(ml_outFollicles[i].mNode+'.translate',mDistanceShape.mNode+'.endPoint')
                        
                        #ml_distanceObjectsBase.append(mDistanceDag)
                        #ml_distanceShapesBase.append(mDistanceShape)
                        md_distDat['out']['active']['mTrans'].append(mDistanceDag)
                        md_distDat['out']['active']['mDist'].append(mDistanceShape)
                    
                    if ml_upFollicles:
                        """
                        #Up Base ---------------------------------------------------------------------------------
                        log.debug("|{0}| >> Up base measure for: {1}".format(_str_func,mJnt))
                        
                        mDistanceDag,mDistanceShape = createDist(mJnt, 'baseUp')
                        mDistanceDag.p_parent = mTransGroup
    
                        #Connect things
                        ATTR.connect(ml_follicles[i].mNode+'.translate',mDistanceShape.mNode+'.startPoint')
                        ATTR.connect(ml_upFollicles[i].mNode+'.translate',mDistanceShape.mNode+'.endPoint')
                        
                        ATTR.break_connection(mDistanceShape.mNode+'.startPoint')
                        ATTR.break_connection(mDistanceShape.mNode+'.endPoint')
                        
                        md_distDat['up']['base']['mTrans'].append(mDistanceDag)
                        md_distDat['up']['base']['mDist'].append(mDistanceShape)
                        #ml_distanceObjectsBase.append(mDistanceDag)
                        #ml_distanceShapesBase.append(mDistanceShape)
                        """
                        
                        #Up Active---------------------------------------------------------------------------------
                        log.debug("|{0}| >> Up active measure for: {1}".format(_str_func,mJnt))
                        
                        mDistanceDag,mDistanceShape = createDist(mJnt, 'activeUp')
                                        
                        #Connect things
                        ATTR.connect(ml_follicles[i].mNode+'.translate',mDistanceShape.mNode+'.startPoint')
                        ATTR.connect(ml_upFollicles[i].mNode+'.translate',mDistanceShape.mNode+'.endPoint')
                        
                        #ml_distanceObjectsBase.append(mDistanceDag)
                        #ml_distanceShapesBase.append(mDistanceShape)
                        md_distDat['up']['active']['mTrans'].append(mDistanceDag)
                        md_distDat['up']['active']['mDist'].append(mDistanceShape)                


        
        
        #>>>Hook up stretch/scale #================================================================ 
        if squashStretchMain == 'arcLength':
            log.debug("|{0}| >> arcLength aim stretch setup ".format(_str_func)+cgmGEN._str_subLine)
            for i,mJnt in enumerate(ml_joints):#Nodes =======================================================
                
                
                if extraSquashControl:
                    try:
                        v_scaleFactor = l_scaleFactors[i]
                    except Exception,err:
                        log.error("scale factor idx fail ({0}). Using 1.0 | {1}".format(i,err))
                        v_scaleFactor = 1.0                    
                    
                    mPlug_aimResult = cgmMeta.cgmAttr(mControlSurface.mNode,
                                                      "{0}_aimScaleResult_{1}".format(str_baseName,i),
                                                      attrType = 'float',
                                                      initialValue=0,
                                                      lock=True,
                                                      minValue = 0)                    
                    """
                    mPlug_baseRes = cgmMeta.cgmAttr(mControlSurface.mNode,
                                                     "{0}_baseRes_{1}".format(str_baseName,i),
                                                     attrType = 'float')"""                    
                    mPlug_jointFactor = cgmMeta.cgmAttr(mSettings.mNode,
                                                        "{0}_factor_{1}".format(str_baseName,i),
                                                        attrType = 'float',
                                                        hidden = False,
                                                        initialValue=v_scaleFactor,
                                                        defaultValue=v_scaleFactor,
                                                        keyable = extraKeyable,
                                                        lock=False,
                                                        minValue = 0)
                    
                    mPlug_jointRes = cgmMeta.cgmAttr(mControlSurface.mNode,
                                                     "{0}_factorRes_{1}".format(str_baseName,i),
                                                     attrType = 'float')
                    
                    mPlug_jointDiff = cgmMeta.cgmAttr(mControlSurface.mNode,
                                                      "{0}_factorDiff_{1}".format(str_baseName,i),
                                                      attrType = 'float')
                    mPlug_jointMult = cgmMeta.cgmAttr(mControlSurface.mNode,
                                                      "{0}_factorMult_{1}".format(str_baseName,i),
                                                      attrType = 'float')                    
                    
                    #>> x + (y - x) * blend --------------------------------------------------------
                    mPlug_baseRes = mPlug_inverseNormalized
                    """
                    l_argBuild.append("{0} = {1} / {2}".format(mPlug_baseRes.p_combinedName,
                                                               mPlug_aimBaseNorm.p_combinedName,
                                                               "{0}.distance".format(mActive_aim.mNode)))"""
                    l_argBuild.append("{0} = 1 + {1}".format(mPlug_aimResult.p_combinedName,
                                                               mPlug_jointMult.p_combinedName))
                    l_argBuild.append("{0} = {1} - 1".format(mPlug_jointDiff.p_combinedName,
                                                             mPlug_baseRes.p_combinedName))
                    l_argBuild.append("{0} = {1} * {2}".format(mPlug_jointMult.p_combinedName,
                                                               mPlug_jointDiff.p_combinedName,
                                                               mPlug_jointRes.p_combinedName))
                    
                    
                    l_argBuild.append("{0} = {1} * {2}".format(mPlug_jointRes.p_combinedName,
                                                               mPlug_jointFactor.p_combinedName,
                                                               mPlug_segScale.p_combinedName))                    
    
                    
                else:
                    mPlug_aimResult = mPlug_inverseNormalized
                
                for arg in l_argBuild:
                    log.debug("|{0}| >> Building arg: {1}".format(_str_func,arg))
                    NODEFAC.argsToNodes(arg).doBuild()
                
            
                if squashStretch == 'simple':
                    for axis in ['scaleX','scaleY']:
                        mPlug_aimResult.doConnectOut('{0}.{1}'.format(mJnt.mNode,axis))
                        
                if not skipAim:
                    mPlug_aimResult.doConnectOut('{0}.{1}'.format(mJnt.mNode,'scaleZ'))                
        else:
            for i,mJnt in enumerate(ml_joints):#Nodes =======================================================
                mActive_aim =  md_distDat['aim']['active']['mDist'][i]
    
                mPlug_aimResult = cgmMeta.cgmAttr(mControlSurface.mNode,
                                                  "{0}_aimScaleResult_{1}".format(str_baseName,i),
                                                  attrType = 'float',
                                                  initialValue=0,
                                                  lock=True,
                                                  minValue = 0)
                
                mPlug_aimBase = cgmMeta.cgmAttr(mControlSurface.mNode,
                                               "{0}_aimBase_{1}".format(str_baseName,i),
                                               attrType = 'float',
                                               lock=True,
                                               value=ATTR.get('{0}.distance'.format(mActive_aim.mNode)))
    
                mPlug_aimBaseNorm = cgmMeta.cgmAttr(mControlSurface.mNode,
                                                  "{0}_aimBaseNorm_{1}".format(str_baseName,i),
                                                  attrType = 'float',
                                                  initialValue=0,
                                                  lock=True,
                                                  minValue = 0)
                
                l_argBuild = []
                l_argBuild.append("{0} = {1} * {2}".format(mPlug_aimBaseNorm.p_combinedName,
                                                           mPlug_aimBase.p_combinedName,
                                                           mPlug_masterScale.p_combinedName,))

                
                #baseSquashScale = distBase / distActual
                #out scale = baseSquashScale * (outBase / outActual)
                #mBase_aim =  md_distDat['aim']['base']['mDist'][i]
                
                
                try:
                    v_scaleFactor = l_scaleFactors[i]
                except Exception,err:
                    log.error("scale factor idx fail ({0}). Using 1.0 | {1}".format(i,err))
                    v_scaleFactor = 1.0
                    
                if extraSquashControl:
                    #mPlug_segScale
                    mPlug_baseRes = cgmMeta.cgmAttr(mControlSurface.mNode,
                                                     "{0}_baseRes_{1}".format(str_baseName,i),
                                                     attrType = 'float')                    
                    mPlug_jointFactor = cgmMeta.cgmAttr(mSettings.mNode,
                                                        "{0}_factor_{1}".format(str_baseName,i),
                                                        attrType = 'float',
                                                        hidden = False,
                                                        initialValue=v_scaleFactor,#l_scaleFactors[i],
                                                        defaultValue=v_scaleFactor,
                                                        lock=False,
                                                        minValue = 0)
                    mPlug_jointRes = cgmMeta.cgmAttr(mControlSurface.mNode,
                                                     "{0}_factorRes_{1}".format(str_baseName,i),
                                                     attrType = 'float')
                    
                    mPlug_jointDiff = cgmMeta.cgmAttr(mControlSurface.mNode,
                                                      "{0}_factorDiff_{1}".format(str_baseName,i),
                                                      attrType = 'float')
                    #mPlug_jointAdd = cgmMeta.cgmAttr(mControlSurface.mNode,
                    #                                  "{0}_factorAdd_{1}".format(str_baseName,i),
                    #                                  attrType = 'float')
                    mPlug_jointMult = cgmMeta.cgmAttr(mControlSurface.mNode,
                                                      "{0}_factorMult_{1}".format(str_baseName,i),
                                                      attrType = 'float')                    
                    
                    #>> x + (y - x) * blend --------------------------------------------------------
                    l_argBuild.append("{0} = {1} / {2}".format(mPlug_baseRes.p_combinedName,
                                                               mPlug_aimBaseNorm.p_combinedName,
                                                               "{0}.distance".format(mActive_aim.mNode),
                                                               ))
                    l_argBuild.append("{0} = 1 + {1}".format(mPlug_aimResult.p_combinedName,
                                                               mPlug_jointMult.p_combinedName))
                    l_argBuild.append("{0} = {1} - 1".format(mPlug_jointDiff.p_combinedName,
                                                             mPlug_baseRes.p_combinedName))
                    l_argBuild.append("{0} = {1} * {2}".format(mPlug_jointMult.p_combinedName,
                                                               mPlug_jointDiff.p_combinedName,
                                                               mPlug_jointRes.p_combinedName))
                    
                    
                    l_argBuild.append("{0} = {1} * {2}".format(mPlug_jointRes.p_combinedName,
                                                               mPlug_jointFactor.p_combinedName,
                                                               mPlug_segScale.p_combinedName))                    
    
                    
                else:
                    l_argBuild.append("{0} = {1} / {2}".format(mPlug_aimResult.p_combinedName,
                                                               mPlug_aimBaseNorm.p_combinedName,
                                                               "{0}.distance".format(mActive_aim.mNode),
                                                               ))
                
                
                for arg in l_argBuild:
                    log.debug("|{0}| >> Building arg: {1}".format(_str_func,arg))
                    NODEFAC.argsToNodes(arg).doBuild()
                            
                if not ml_outFollicles:
                    for axis in ['scaleX','scaleY']:
                        mPlug_aimResult.doConnectOut('{0}.{1}'.format(mJnt.mNode,axis))
                        
                if not skipAim:
                    mPlug_aimResult.doConnectOut('{0}.{1}'.format(mJnt.mNode,'scaleZ'))
            
        if squashStretch in ['single','both']:
            if ml_outFollicles or ml_upFollicles:
                for i,mJnt in enumerate(ml_joints):
                    #if mJnt == ml_joints[-1]:
                        #pass #...we'll pick up the last on the loop
                    #else:
                    mPlug_aimResult = cgmMeta.cgmAttr(mControlSurface.mNode,
                                                    "{0}_aimScaleResult_{1}".format(str_baseName,i))
                        #mActive_aim =  md_distDat['aim']['active']['mDist'][i]                        
                        
                    
                    if ml_outFollicles:
                        #mBase_out =  md_distDat['out']['base']['mDist'][i]
                        mActive_out =  md_distDat['out']['active']['mDist'][i]
                        
                        mPlug_outResult = cgmMeta.cgmAttr(mControlSurface.mNode,
                                                          "{0}_outScaleResult_{1}".format(str_baseName,i),
                                                          attrType = 'float',
                                                          lock=True,
                                                          minValue = 0)
                        
                        mPlug_outBase = cgmMeta.cgmAttr(mControlSurface.mNode,
                                                        "{0}_outBaseScaleResult_{1}".format(str_baseName,i),
                                                        attrType = 'float',
                                                        value=ATTR.get('{0}.distance'.format(mActive_out.mNode)))
             
                        mPlug_outBaseNorm = cgmMeta.cgmAttr(mControlSurface.mNode,
                                                          "{0}_outBaseNorm_{1}".format(str_baseName,i),
                                                          attrType = 'float',
                                                          lock=True,
                                                          minValue = 0)
                        
                        mPlug_outBaseRes = cgmMeta.cgmAttr(mControlSurface.mNode,
                                                            "{0}_outBaseRes_{1}".format(str_baseName,i),
                                                            attrType = 'float',
                                                            lock=True)                    
                         
                        l_argBuild = []
                        l_argBuild.append("{0} = {1} * {2}".format(mPlug_outBaseNorm.p_combinedName,
                                                                   mPlug_outBase.p_combinedName,
                                                                   mPlug_masterScale.p_combinedName,))
                        
                        #baseSquashScale = distBase / distActual
                        #out scale = baseSquashScale * (outBase / outActual)
    
     
                        
                        l_argBuild.append("{0} = {1} / {2}".format(mPlug_outBaseRes.p_combinedName,
                                                                   '{0}.distance'.format(mActive_out.mNode),
                                                                   mPlug_outBaseNorm.p_combinedName,))
                        
                        l_argBuild.append("{0} = {1} * {2}".format(mPlug_outResult.p_combinedName,
                                                                   mPlug_aimResult.p_combinedName,
                                                                   mPlug_outBaseRes.p_combinedName))
                        
                        
                        for arg in l_argBuild:
                            log.debug("|{0}| >> Building arg: {1}".format(_str_func,arg))
                            NODEFAC.argsToNodes(arg).doBuild()
                            
                            
                        #out scale ---------------------------------------------------------------
                        for axis in ['scaleX','scaleY']:
                            mPlug_outResult.doConnectOut('{0}.{1}'.format(mJnt.mNode,axis))
                            
                    if ml_upFollicles:
                        #mBase_up =  md_distDat['up']['base']['mDist'][i]
                        mActive_up =  md_distDat['up']['active']['mDist'][i]
                        
                        mPlug_upResult = cgmMeta.cgmAttr(mControlSurface.mNode,
                                                          "{0}_upScaleResult_{1}".format(str_baseName,i),
                                                          attrType = 'float',
                                                          lock=True,
                                                          minValue = 0)
                        
                        mPlug_upBase = cgmMeta.cgmAttr(mControlSurface.mNode,
                                                       "{0}_upBaseScaleResult_{1}".format(str_baseName,i),
                                                       attrType = 'float',
                                                       value=ATTR.get('{0}.distance'.format(mActive_up.mNode)))
                        
                        mPlug_upBaseRes = cgmMeta.cgmAttr(mControlSurface.mNode,
                                                          "{0}_upBaseRes_{1}".format(str_baseName,i),
                                                          attrType = 'float',
                                                          lock=True,
                                                          minValue = 0)
            
                        mPlug_upBaseNorm = cgmMeta.cgmAttr(mControlSurface.mNode,
                                                          "{0}_upBaseNorm_{1}".format(str_baseName,i),
                                                          attrType = 'float',
                                                          lock=True,
                                                          minValue = 0)
                        
                        l_argBuild = []
                        l_argBuild.append("{0} = {1} * {2}".format(mPlug_upBaseNorm.p_combinedName,
                                                                   mPlug_upBase.p_combinedName,
                                                                   mPlug_masterScale.p_combinedName,))                    
                        
                        #baseSquashScale = distBase / distActual
                        #up scale = baseSquashScale * (upBase / upActual)
    
                        
    
                        
                        l_argBuild.append("{0} = {1} / {2}".format(mPlug_upBaseRes.p_combinedName,
                                                                   '{0}.distance'.format(mActive_up.mNode),
                                                                   mPlug_upBaseNorm.p_combinedName,))
                        
                        l_argBuild.append("{0} = {1} * {2}".format(mPlug_upResult.p_combinedName,
                                                                   mPlug_aimResult.p_combinedName,
                                                                   mPlug_upBaseRes.p_combinedName))
                        
                        
                        for arg in l_argBuild:
                            log.debug("|{0}| >> Building arg: {1}".format(_str_func,arg))
                            NODEFAC.argsToNodes(arg).doBuild()
                            
                            
                        #up scale ---------------------------------------------------------------
                        for axis in ['scaleY']:
                            mPlug_upResult.doConnectOut('{0}.{1}'.format(mJnt.mNode,axis))                

    if additiveScaleEnds:
        log.debug("|{0}| >> Additive Scale Ends".format(_str_func)+cgmGEN._str_subLine)
        
        for i,mJnt in enumerate( [ml_joints[0],ml_joints[-1]] ):
            
            #Active measures ---------------------------------------------------------------------
            log.debug("|{0}| >> Additve Scale measure for: {1}".format(_str_func,mJnt))
            
            #>> Distance nodes
            mDistanceDag,mDistanceShape = createDist(mJnt, 'additiveEnd')
            log.debug("|{0}| >> Dist created...".format(_str_func))
            
            

            #Connect things
            #.on loc = position
            ATTR.connect(ml_follicles[ml_joints.index(mJnt)].mNode+'.translate',
                         mDistanceShape.mNode+'.startPoint')
            
            if not i:
                ATTR.connect(mFollicleMinV.mNode+'.translate',
                             mDistanceShape.mNode+'.endPoint')
                str_tag = 'min'
            else:
                ATTR.connect(mFollicleMaxV.mNode+'.translate',
                             mDistanceShape.mNode+'.endPoint')
                str_tag = 'max'
                
            log.debug("|{0}| >> follicle connected...".format(_str_func))
                
            #Normal Base -----------------------------------------------------------------
            #normalbase = base value * master
            #mult_normalBase = mc.createNode('multDoubleLinear')
            #ATTR.connect(mPlug_masterScale.p_combinedName, mult_normalBase + '.input1')
            #ATTR.set(mult_normalBase,'input2',mDistanceDag.mNode + '.distance')
            #ATTR.connect(mDistanceDag.mNode + '.distance', mult_normalBase + '.input2')
            
            # Base -----------------------------------------------------------------
            mPlug_aimResult = cgmMeta.cgmAttr(mControlSurface.mNode,
                                              "{0}_aimAdditiveResult_{1}".format(str_baseName,str_tag),
                                              attrType = 'float',
                                              initialValue=0,
                                              lock=True,
                                              minValue = 0)
        
            mPlug_aimBase = cgmMeta.cgmAttr(mControlSurface.mNode,
                                            "{0}_aimAdditiveBase_{1}".format(str_baseName,str_tag),
                                            attrType = 'float',
                                            lock=True,
                                            value=ATTR.get('{0}.distance'.format(mDistanceShape.mNode)))
    
            mPlug_aimBaseNorm = cgmMeta.cgmAttr(mControlSurface.mNode,
                                                "{0}_aimAdditveBaseNorm_{1}".format(str_baseName,str_tag),
                                                attrType = 'float',
                                                initialValue=0,
                                                lock=True,
                                                minValue = 0)
            log.debug("|{0}| >> Attrs registered...".format(_str_func))
            
            l_argBuild = []
            l_argBuild.append("{0} = {1} * {2}".format(mPlug_aimBaseNorm.p_combinedName,
                                                       mPlug_aimBase.p_combinedName,
                                                       mPlug_masterScale.p_combinedName,))
            l_argBuild.append("{0} = {2} / {1}".format(mPlug_aimResult.p_combinedName,
                                                       mPlug_aimBaseNorm.p_combinedName,
                                                       "{0}.distance".format(mDistanceShape.mNode),
                                                       ))
        
            for arg in l_argBuild:
                log.debug("|{0}| >> Building arg: {1}".format(_str_func,arg))
                NODEFAC.argsToNodes(arg).doBuild()
                
                
            if not skipAim:
                RIGGEN.plug_insertNewValues('{0}.scaleZ'.format(mJnt.mNode),
                                            [mPlug_aimResult.p_combinedName],replace=False)
            
    #>>> Connect our iModule vis stuff
    if mModule:#if we have a module, connect vis
        log.debug("|{0}| >> mModule wiring...".format(_str_func)+cgmGEN._str_subLine)            
        
        for mObj in ml_rigObjectsToConnect:
            mObj.overrideEnabled = 1		
            cgmMeta.cgmAttr(mModule.rigNull.mNode,'gutsVis',lock=False).doConnectOut("%s.%s"%(mObj.mNode,'overrideVisibility'))
            cgmMeta.cgmAttr(mModule.rigNull.mNode,'gutsLock',lock=False).doConnectOut("%s.%s"%(mObj.mNode,'overrideDisplayType'))    
        for mObj in ml_rigObjectsToParent:
            mObj.parent = mModule.rigNull.mNode

    if ml_influences:
        log.debug("|{0}| >> Influences found. Attempting to skin...".format(_str_func)+cgmGEN._str_subLine)            
        
        max_influences = 2
        mode_tighten = 'twoBlend'
        blendLength = int_lenJoints/2
        blendMin = 2
        _hardLength = 2
        
        if extendEnds:
            blendMin = 4
            _hardLength = 3
            mode_tighten = None
        
        
        if int_lenInfluences > 2:
            mode_tighten = None
            #blendLength = int(int_lenInfluences/2)
            max_influences = MATH.Clamp( blendLength, 2, 4)
            blendLength = MATH.Clamp( int(int_lenInfluences/1.5), 2, 6)
        
        if int_lenInfluences == int_lenJoints:
            _hardLength = 3
            
        #Tighten the weights...
        
       
            
        if mArcLenCurve:
            log.debug("|{0}| >> Skinning arcLen Curve: {1}".format(_str_func,mArcLenCurve))
            
            mSkinCluster = cgmMeta.validateObjArg(mc.skinCluster ([mObj.mNode for mObj in ml_influences],
                                                                  mArcLenCurve.mNode,
                                                                  tsb=True,
                                                                  maximumInfluences = max_influences,
                                                                  normalizeWeights = 1,dropoffRate=1.0),
                                                  'cgmNode',
                                                  setClass=True)
        
            mSkinCluster.doStore('cgmName', mArcLenCurve)
            mSkinCluster.doName()    
        
            
            if tightenWeights:
                RIGSKIN.curve_tightenEnds(mArcLenCurve.mNode,
                                           hardLength = _hardLength,
                                           blendLength=blendLength,
                                           mode=mode_tighten)
                
            
        for mSurf in ml_surfaces:
            log.debug("|{0}| >> Skinning surface: {1}".format(_str_func,mSurf))
            mSkinCluster = cgmMeta.validateObjArg(mc.skinCluster ([mObj.mNode for mObj in ml_influences],
                                                                  mSurf.mNode,
                                                                  tsb=True,
                                                                  maximumInfluences = max_influences,
                                                                  normalizeWeights = 1,dropoffRate=5.0),
                                                  'cgmNode',
                                                  setClass=True)
        
            mSkinCluster.doStore('cgmName', mSurf)
            mSkinCluster.doName()    
        
            #Tighten the weights...
            if tightenWeights:
                RIGSKIN.surface_tightenEnds(mSurf.mNode,
                                            hardLength = _hardLength,
                                            blendLength = blendLength,
                                            mode = mode_tighten)
        
    
    if mModule:#if we have a module, connect vis
        mRigNull = mModule.rigNull
        _str_rigNull = mRigNull.mNode
        for mObj in ml_toConnect:
            mObj.overrideEnabled = 1
            cgmMeta.cgmAttr(_str_rigNull,'gutsVis',lock=False).doConnectOut("%s.%s"%(mObj.mNode,'overrideVisibility'))
            cgmMeta.cgmAttr(_str_rigNull,'gutsLock',lock=False).doConnectOut("%s.%s"%(mObj.mNode,'overrideDisplayType'))    
            mObj.parent = mRigNull    
    
    if mArcLenDag:
        mArcLenDag.p_parent = mGroup

    
    _res = {'mlSurfaces':ml_surfaces}
    return _res




def handle(startJoint,
           endJoint,
           solverType = 'ikRPsolver',
           rpHandle = False,
           lockMid = True,
           addLengthMulti = False,
           stretch = False, globalScaleAttr = None,
           controlObject = None,
           baseName = None,
           orientation = 'zyx',
           nameSuffix = None,
           newSolver = False,#Create a new solver node for this?
           handles = [],#If one given, assumed to be mid, can't have more than length of joints
           moduleInstance = None):
    """
    @kws
    l_jointChain1(list) -- blend list 1
    l_jointChain2(list) -- blend list 2
    l_blendChain(list) -- result chain
    solverType -- 'ikRPsolver','ikSCsolver'
    baseName -- 
    nameSuffix -- add to nameBase
    rpHandle(bool/string) -- whether to have rphandle setup, object to use if string or MetaClass
    lockMid(bool) --
    driver(attr arg) -- driver attr
    globalScaleAttr(string/cgmAttr) -- global scale attr to connect in
    addLengthMulti(bool) -- whether to setup lengthMultipliers
    controlObject(None/string) -- whether to have control to put attrs on, object to use if string or MetaClass OR will use ikHandle
    channels(list) -- channels to blend
    stretch(bool/string) -- stretch options - translate/scale
    moduleInstance -- instance to connect stuff to

    """
    try:
        _str_func = 'handle'
        log.debug("|{0}| >> ...".format(_str_func))  
        
    
        ml_rigObjectsToConnect = []
        ml_rigObjectsToParent = []
    
        #>>> Data gather and arg check
        if solverType not in ['ikRPsolver','ikSCsolver']:
            raise ValueError,"|{0}| >> Invalid solverType: {1}".format(_str_func,solverType)
        
        
        mi_mayaOrientation = VALID.simpleOrientation(orientation)
        str_orientation = mi_mayaOrientation.p_string
        #str_secondaryAxis = VALID.stringArg(secondaryAxis,noneValid=True)
        str_baseName = VALID.stringArg(baseName,noneValid=True)
        
        #module ---------------------------------------------------------------------------------------
        mModule = cgmMeta.validateObjArg(moduleInstance,noneValid = True)
        #try:mModule.isModule()
        #except:mModule = False
    
        mi_rigNull = False	
        if mModule:
            log.debug("|{0}| >> Module found. mModule: {1}...".format(_str_func,mModule))
            mi_rigNull = mModule.rigNull	
            if str_baseName is None:
                str_baseName = mModule.getPartNameBase()#Get part base name	    
        if not str_baseName:str_baseName = 'testIK'     
    
        #Joint chain ======================================================================================
        mStart = cgmMeta.validateObjArg(startJoint,'cgmObject',noneValid=False)
        mEnd = cgmMeta.validateObjArg(endJoint,'cgmObject',noneValid=False)
        if not mEnd.isChildOf(mStart):
            raise ValueError,"|{0}| >> {1} not a child of {2}".format(_str_func,endJoint,startJoint)
            
        ml_jointChain = mStart.getListPathTo(mEnd,asMeta=True)
        #ml_jointChain = cgmMeta.validateObjListArg(l_jointChain,'cgmObject',noneValid=False)
        l_jointChain = [mObj.mNode for mObj in ml_jointChain]
        if len(ml_jointChain)<3 and solverType in ['rpSolver']:
            raise ValueError,"|{0}| >> {1} len less than 3 joints. solver: {2}".format(_str_func,len(ml_jointChain,solverType))
            
        _foundPrerred = False
        for mJnt in ml_jointChain:
            mc.joint(mJnt.mNode, e=True, spa=True, ch=1)            
            #for attr in ['preferredAngleX','preferredAngleY','preferredAngleZ']:
                #if mJnt.getAttr(attr):
                    #log.debug("|{0}| >> Found preferred...".format(_str_func))                  
                    #_foundPrerred = True
                    #break
        
        #Attributes =====================================================================================
        #Master global control
        d_MasterGlobalScale = cgmMeta.validateAttrArg(globalScaleAttr,noneValid=True)    
        
        #Stretch
        if stretch and stretch not in ['translate','scale']:
            log.debug("|{0}| >> Invalid stretch arg: {1}. Using 'translate'".format(_str_func,stretch))
            stretch = 'translate'
        if stretch == 'scale':
            raise NotImplementedError,"|{0}| >> Scale method not done".format(_str_func)
            
        #Handles =======================================================================================
        ml_handles = cgmMeta.validateObjListArg(handles,'cgmObject',noneValid=True)
        if len(ml_handles)>len(ml_jointChain):#Check handle length to joint list
            raise ValueError,"|{0}| >> More handles than joints. joints: {1}| handles: {2}.".format(_str_func,len(ml_jointChain),len(ml_handles))
            
    
        mRPHandle = cgmMeta.validateObjArg(rpHandle,'cgmObject',noneValid=True)
        if mRPHandle and mRPHandle in ml_handles:
            raise NotImplementedError,"|{0}| >> rpHandle can't be a measure handle".format(_str_func)
            
        #Control object
        mControl = cgmMeta.validateObjArg(controlObject,'cgmObject',noneValid=True)
        if mControl:
            log.debug("|{0}| >> mControl: {1}.".format(_str_func,mControl))                  
    
        #Figure out our aimaxis
        str_localAimSingle = orientation[0]
        
        
        
        if newSolver:
            _node = mc.createNode(solverType)
            mSolver = cgmMeta.asMeta(_node)
            mSolver.rename("{0}_{1}".format(str_baseName,solverType))
            _useSolver = mSolver.mNode
        else:
            _useSolver = solverType
    
        #Create IK handle ==================================================================================
        buffer = mc.ikHandle( sj=mStart.mNode, ee=mEnd.mNode,
                              solver = _useSolver, forceSolver = True,
                              snapHandleFlagToggle=True )  	
    
    
        #>>> Name
        log.debug(buffer)
        mIKHandle = cgmMeta.asMeta(buffer[0],'cgmObject',setClass=True)
        mIKHandle.addAttr('cgmName',str_baseName,attrType='string',lock=True)
        mIKHandle.doName()
    
        ml_rigObjectsToConnect.append(mIKHandle)
    
        mIKEffector = cgmMeta.asMeta(buffer[1],'cgmNode',setClass=True)
        mIKEffector.addAttr('cgmName',str_baseName,attrType='string',lock=True)    
        mIKEffector.doName()
    
        #>>> Control
        if not mControl:
            mControl = mIKHandle
        else:
            mIKHandle.parent = mControl
            
        #>>> Store our start and end
        mIKHandle.connectChildNode(mStart,'jointStart','ikOwner')
        mIKHandle.connectChildNode(mEnd,'jointEnd','ikOwner')
        
        #>>>Stetch #===============================================================================
        mPlug_lockMid = False  
        ml_distanceShapes = []
        ml_distanceObjects = []   
        mPlug_globalScale = False
        
        if stretch:
            log.debug("|{0}| >> Stretch setup...".format(_str_func))
            mPlug_globalScale = cgmMeta.cgmAttr(mIKHandle.mNode,'masterScale',value = 1.0, lock =True, hidden = True)
            
            
            #Attributes ----------------------------------------------------------
            d_baseAttrs = {}
            for a in ['distIKRaw','distBaseNormal','distActiveNormal',
                      'distFullLengthNormal','scaleFactorRaw','scaleFactor']:
                d_baseAttrs[a] = cgmMeta.cgmAttr(mIKHandle.mNode, a , attrType = 'float',
                                                 value = 1, lock =True , hidden = True)
            
            
            #Get our distance -----------------------------------------------------------------------
            f_baseDist = DIST.get_distance_between_targets(l_jointChain)

            #--------------------------------------------------------------------------------------
            mPlug_autoStretch = cgmMeta.cgmAttr(mControl,'autoStretch',initialValue = 1,
                                                defaultValue = 1, keyable = True,
                                                attrType = 'float', minValue = 0, maxValue = 1)
            
            if len(ml_jointChain) == 3 and lockMid:
                log.debug("|{0}| >> MidLock setup possible...".format(_str_func))
                
                if lockMid:mPlug_lockMid = cgmMeta.cgmAttr(mControl,'lockMid',
                                                           initialValue = 0, attrType = 'float',
                                                           keyable = True, minValue = 0, maxValue = 1)
        
                if addLengthMulti:
                    mPlug_lengthUpr= cgmMeta.cgmAttr(mControl,'lengthUpr',attrType='float',value = 1, defaultValue = 1,minValue=0,keyable = True)
                    mPlug_lengthLwr = cgmMeta.cgmAttr(mControl,'lengthLwr',attrType='float',value = 1, defaultValue = 1,minValue=0,keyable = True)	
                    ml_multiPlugs = [mPlug_lengthUpr,mPlug_lengthLwr]
        
            #Check our handles for stretching
            if len(ml_handles)!= len(ml_jointChain):#we need a handle per joint for measuring purposes
                log.debug("create_IKHandle>>> Making handles")
                ml_buffer = ml_handles
                ml_handles = []
                for j in ml_jointChain:
                    m_match = False
                    for h in ml_buffer:
                        if MATH.is_vector_equivalent(j.getPosition(),h.getPosition()):
                            log.debug("create_IKHandle>>> '%s' handle matches: '%s'"%(h.getShortName(),j.getShortName()))
                            m_match = h
                    if not m_match:#make one
                        m_match = j.doLoc(nameLink = True)
                        m_match.addAttr('cgmTypeModifier','stretchMeasure')
                        m_match.doName()
                    ml_handles.append(m_match)
                    ml_rigObjectsToConnect.append(m_match)
    
                #>>>TODO Add hide stuff
        
                #>>>Do Handles
                mMidHandle = False   
                if ml_handles:
                    if len(ml_handles) == 1:
                        mMidHandle = ml_handles[0]
                    else:
                        mid = int((len(ml_handles))/2)
                        mMidHandle = ml_handles[mid]
                    
                    log.debug("|{0}| >> mid handle: {1}".format(_str_func,mMidHandle))

            #Overall stretch ----------------------------------------------------------------------
            md_baseDistReturn = RIGCREATE.distanceMeasure(ml_handles[0].mNode,ml_handles[-1].mNode,baseName=str_baseName)
            md_baseDistReturn['mEnd'].p_parent = mControl
            ml_rigObjectsToParent.append(md_baseDistReturn['mDag'])
            
            mPlug_rawDistance = cgmMeta.cgmAttr(md_baseDistReturn['mShape'],'distance')
            
            # ['distIKStretch','stretchMultiplier','distIKNormal','distFullLengthNormal']
            d_baseAttrs['distIKRaw'].value = md_baseDistReturn['mShape'].distance

            
            #Normal base -----------------------------------------------------------------------
            _arg = "{0} = {1} * {2}".format(d_baseAttrs['distBaseNormal'].p_combinedName,
                                            mPlug_rawDistance.value,
                                            mPlug_globalScale.p_combinedName)
            NODEFAC.argsToNodes(_arg).doBuild()
            
            #Normal active -----------------------------------------------------------------------
            _arg = "{0} = {1} / {2}".format(d_baseAttrs['distActiveNormal'].p_combinedName,
                                          mPlug_rawDistance.p_combinedName,
                                          mPlug_globalScale.p_combinedName)
            NODEFAC.argsToNodes(_arg).doBuild()            
            

            #dist fullLenth normal -----------------------------------------------------------------            
            _arg = "{0} = {1} * {2}".format(d_baseAttrs['distFullLengthNormal'].p_combinedName,
                                            f_baseDist,
                                            mPlug_globalScale.p_combinedName)
            NODEFAC.argsToNodes(_arg).doBuild()            
            
            #scaleFactorRaw  -----------------------------------------------------------------------
            _arg = "{0} = {1} / {2}".format(d_baseAttrs['scaleFactorRaw'].p_combinedName,
                                            mPlug_rawDistance.p_combinedName,
                                            d_baseAttrs['distFullLengthNormal'].p_combinedName)
            NODEFAC.argsToNodes(_arg).doBuild()
            
            
            #scaleFactorReal ---------------------------------------------------------------
            _arg = "{0} = if {1} >= {2}: {3} else 1".format(d_baseAttrs['scaleFactor'].p_combinedName,
                                                            mPlug_rawDistance.p_combinedName,
                                                            d_baseAttrs['distFullLengthNormal'].p_combinedName,
                                                            d_baseAttrs['scaleFactorRaw'].p_combinedName)
            NODEFAC.argsToNodes(_arg).doBuild()            
            


            #Create our blend to stretch or not - blend normal base and stretch base
            mStretchBlend = cgmMeta.cgmNode(nodeType= 'blendTwoAttr')
            mStretchBlend.addAttr('cgmName','%s_stretchBlend'%(str_baseName),lock=True)
            mStretchBlend.doName()
            ATTR.set(mStretchBlend.mNode,"input[0]",1)
            d_baseAttrs['scaleFactor'].doConnectOut("%s.input[1]"%mStretchBlend.mNode)
            mPlug_autoStretch.doConnectOut("%s.attributesBlender"%mStretchBlend.mNode)
            
            
            #--------------------------------------------------------------------------------------------
            if lockMid:
                #Make our distance objects per segment ===========================================================
                l_segments = LISTS.get_listPairs(ml_handles)
                for i,seg in enumerate(l_segments):#Make our measure nodes
                    buffer =  RIGCREATE.distanceMeasure(seg[0].mNode,seg[-1].mNode,baseName="{0}_{1}".format(str_baseName,i))
                    ml_distanceShapes.append(buffer['mShape'])
                    ml_distanceObjects.append(buffer['mDag'])
                    #>>>TODO Add hide stuff
                ml_rigObjectsToParent.extend(ml_distanceObjects)
                ml_rigObjectsToConnect.extend(ml_handles)            
            
            

            #Per joint setup...
            #--------------------------------------------------------------------------------------------
            l_jntAttrs = ['distBase','distNormal','stretchReg']
            if lockMid:
                l_jntAttrs.extend(['stretchMid',
                                   'distMidBase','distMidBaseNormal',
                                   'distMidRaw','distMidNormal'])
                
            for i,mJnt in enumerate(ml_jointChain[:-1]):
                md_jntAttrs = {}

                for a in l_jntAttrs:
                    md_jntAttrs[a] = cgmMeta.cgmAttr(mIKHandle.mNode, "{0}_{1}".format(a,i) ,
                                                     attrType = 'float',
                                                     value = 1, lock =True , hidden = True)
                    
                md_jntAttrs['distBase'].value = ATTR.get(ml_jointChain[i+1].mNode,
                                                         "t{0}".format(str_localAimSingle))
                
                #Normal base -----------------------------------------------------------------------
                _arg = "{0} = {1} * {2}".format(md_jntAttrs['distNormal'].p_combinedName,
                                                md_jntAttrs['distBase'].p_combinedName,
                                                mPlug_globalScale.p_combinedName)
                NODEFAC.argsToNodes(_arg).doBuild()
                
                _arg = "{0} = {1} * {2}.output".format(md_jntAttrs['stretchReg'].p_combinedName,
                                                       md_jntAttrs['distBase'].p_combinedName,
                                                       mStretchBlend.mNode)
                NODEFAC.argsToNodes(_arg).doBuild()
                
                
                if lockMid:
                    md_jntAttrs['distBase'].value = ml_distanceShapes[i].distance
                    md_jntAttrs['distMidRaw'].doConnectIn("%s.distance"%ml_distanceShapes[i].mNode)	  
                    
                    #Normal base distance
                    arg = "%s = %s * %s"%(md_jntAttrs['distMidBaseNormal'].p_combinedName,
                                          md_jntAttrs['distBase'].p_combinedName,
                                          mPlug_globalScale.p_combinedName)
                    NODEFAC.argsToNodes(arg).doBuild()
                
                    #Normal distance
                    arg = "%s = %s / %s"%(md_jntAttrs['distMidNormal'].p_combinedName,
                                          md_jntAttrs['distMidRaw'].p_combinedName,
                                          mPlug_globalScale.p_combinedName)
                    NODEFAC.argsToNodes(arg).doBuild()

                
                #Blend --------------------------------------------------------------
                mBlend_jnt = cgmMeta.cgmNode(nodeType= 'blendTwoAttr')
                mBlend_jnt.addAttr('cgmName','%s_stretch_to_lockMid'%(mJnt.getBaseName()),lock=True)
                mBlend_jnt.doName()
                if mPlug_lockMid:
                    mPlug_lockMid.doConnectOut("%s.attributesBlender"%mBlend_jnt.mNode)                    
                    
    
                if stretch == 'translate':
                    if lockMid:
                        #Base Normal, Dist Normal
                        md_jntAttrs['stretchReg'].doConnectOut("%s.input[0]"%mBlend_jnt.mNode)
                        md_jntAttrs['distMidNormal'].doConnectOut("%s.input[1]"%mBlend_jnt.mNode)
                        ATTR.connect("%s.output"%mBlend_jnt.mNode,"%s.t%s"%(ml_jointChain[i+1].mNode,str_localAimSingle))
                    else:
                        md_jntAttrs['stretchReg'].doConnectOut("{0}.t{1}".format(ml_jointChain[i+1].mNode,str_localAimSingle))
    
        #>>> addLengthMulti
        if addLengthMulti:
            log.debug("|{0}| >> addLengthMulti...".format(_str_func))
            
            if len(ml_jointChain[:-1]) == 2:
                #grab the plug
    
                i_mdLengthMulti = cgmMeta.cgmNode(mc.createNode('multiplyDivide'))
                i_mdLengthMulti.operation = 1
                i_mdLengthMulti.doStore('cgmName',str_baseName)
                i_mdLengthMulti.addAttr('cgmTypeModifier','lengthMulti')
                i_mdLengthMulti.doName()
    
                l_mdAxis = ['X','Y','Z']
                for i,i_jnt in enumerate(ml_jointChain[:-1]):
                    #grab the plug
                    mPlug_driven = cgmMeta.cgmAttr(ml_jointChain[i+1],'t%s'%str_localAimSingle)
                    plug = ATTR.break_connection(mPlug_driven.p_combinedName)
                    if not plug:raise StandardError,"create_IKHandle>>> Should have found a plug on: %s.t%s"%(ml_jointChain[i+1].mNode,str_localAimSingle)
    
                    ATTR.connect(plug,#>>
                                 '%s.input1%s'%(i_mdLengthMulti.mNode,l_mdAxis[i]))#Connect the old plug data
                    ml_multiPlugs[i].doConnectOut('%s.input2%s'%(i_mdLengthMulti.mNode,l_mdAxis[i]))#Connect in the mutliDriver	
                    mPlug_driven.doConnectIn('%s.output.output%s'%(i_mdLengthMulti.mNode,l_mdAxis[i]))#Connect it back to our driven
    
            else:
                log.error("|{0}| >> addLengthMulti only currently supports 2 segments. Found: {1}".format(_str_func,len(ml_jointChain[:-1])))
                
    
        #>>> rpSetup
        if solverType == 'ikRPsolver' and rpHandle:
            log.debug("|{0}| >> RP Handle setup...".format(_str_func))
            
            if not mRPHandle:
                #Make one
                mRPHandle = mMidHandle.doLoc()
                mRPHandle.addAttr('cgmTypeModifier','poleVector')
                mRPHandle.doName()
                ml_rigObjectsToConnect.append(mRPHandle)
            cBuffer = mc.poleVectorConstraint(mRPHandle.mNode,mIKHandle.mNode)
    
            #Fix rp
            #rotValue = mStart.getAttr('r%s'%str_localAimSingle)    
            #if not cgmMath.isFloatEquivalent(rotValue,0):#if we have a value, we need to fix it
                #IKHandle_fixTwist(mIKHandle)	
    
    
        #>>> Plug in global scale
        if d_MasterGlobalScale and mPlug_globalScale:
            d_MasterGlobalScale['mi_plug'].doConnectOut(mPlug_globalScale.p_combinedName)
    
        #>>> Connect our iModule vis stuff
        if mModule:#if we have a module, connect vis
            for mObj in ml_rigObjectsToConnect:
                mObj.overrideEnabled = 1		
                cgmMeta.cgmAttr(mModule.rigNull.mNode,'gutsVis',lock=False).doConnectOut("%s.%s"%(mObj.mNode,'overrideVisibility'))
                cgmMeta.cgmAttr(mModule.rigNull.mNode,'gutsLock',lock=False).doConnectOut("%s.%s"%(mObj.mNode,'overrideDisplayType'))    
            for mObj in ml_rigObjectsToParent:
                mObj.parent = mModule.rigNull.mNode
    
        #>>> Return dict
        d_return = {'mHandle':mIKHandle,'mEffector':mIKEffector}
        if mPlug_lockMid:
            d_return['mPlug_lockMid'] = mPlug_lockMid	
            d_return['ml_measureObjects']=ml_distanceObjects	
        if stretch:
            d_return['mPlug_autoStretch'] = mPlug_autoStretch
            d_return['ml_distHandles']=ml_handles
        if mRPHandle:
            d_return['mRPHandle'] = mRPHandle
        if addLengthMulti:
            d_return['ml_lengthMultiPlugs'] = ml_multiPlugs
    
        #if not _foundPrerred:log.warning("create_IKHandle>>> No preferred angle values found. The chain probably won't work as expected: %s"%l_jointChain)
        
        return d_return   
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err)





def handleBAK(startJoint,
           endJoint,
           solverType = 'ikRPsolver',
           rpHandle = False,
           lockMid = True,
           addLengthMulti = False,
           stretch = False, globalScaleAttr = None,
           controlObject = None,
           baseName = None,
           orientation = 'zyx',
           nameSuffix = None,
           handles = [],#If one given, assumed to be mid, can't have more than length of joints
           moduleInstance = None):
    """
    @kws
    l_jointChain1(list) -- blend list 1
    l_jointChain2(list) -- blend list 2
    l_blendChain(list) -- result chain
    solverType -- 'ikRPsolver','ikSCsolver'
    baseName -- 
    nameSuffix -- add to nameBase
    rpHandle(bool/string) -- whether to have rphandle setup, object to use if string or MetaClass
    lockMid(bool) --
    driver(attr arg) -- driver attr
    globalScaleAttr(string/cgmAttr) -- global scale attr to connect in
    addLengthMulti(bool) -- whether to setup lengthMultipliers
    controlObject(None/string) -- whether to have control to put attrs on, object to use if string or MetaClass OR will use ikHandle
    channels(list) -- channels to blend
    stretch(bool/string) -- stretch options - translate/scale
    moduleInstance -- instance to connect stuff to

    """
    try:
        _str_func = 'handle'
        log.debug("|{0}| >> ...".format(_str_func))  
        
    
        ml_rigObjectsToConnect = []
        ml_rigObjectsToParent = []
    
        #>>> Data gather and arg check
        if solverType not in ['ikRPsolver','ikSCsolver']:
            raise ValueError,"|{0}| >> Invalid solverType: {1}".format(_str_func,solverType)
        
        
        mi_mayaOrientation = VALID.simpleOrientation(orientation)
        str_orientation = mi_mayaOrientation.p_string
        #str_secondaryAxis = VALID.stringArg(secondaryAxis,noneValid=True)
        str_baseName = VALID.stringArg(baseName,noneValid=True)
        
        #module ---------------------------------------------------------------------------------------
        mModule = cgmMeta.validateObjArg(moduleInstance,noneValid = True)
        #try:mModule.isModule()
        #except:mModule = False
    
        mi_rigNull = False	
        if mModule:
            log.debug("|{0}| >> Module found. mModule: {1}...".format(_str_func,mModule))
            mi_rigNull = mModule.rigNull	
            if str_baseName is None:
                str_baseName = mModule.getPartNameBase()#Get part base name	    
        if not str_baseName:str_baseName = 'testIK'     
    
        #Joint chain ======================================================================================
        mStart = cgmMeta.validateObjArg(startJoint,'cgmObject',noneValid=False)
        mEnd = cgmMeta.validateObjArg(endJoint,'cgmObject',noneValid=False)
        if not mEnd.isChildOf(mStart):
            raise ValueError,"|{0}| >> {1} not a child of {2}".format(_str_func,endJoint,startJoint)
            
        ml_jointChain = mStart.getListPathTo(mEnd,asMeta=True)
        #ml_jointChain = cgmMeta.validateObjListArg(l_jointChain,'cgmObject',noneValid=False)
        l_jointChain = [mObj.mNode for mObj in ml_jointChain]
        if len(ml_jointChain)<3 and solverType in ['rpSolver']:
            raise ValueError,"|{0}| >> {1} len less than 3 joints. solver: {2}".format(_str_func,len(ml_jointChain,solverType))
            
        _foundPrerred = False
        for mJnt in ml_jointChain:
            for attr in ['preferredAngleX','preferredAngleY','preferredAngleZ']:
                if mJnt.getAttr(attr):
                    log.debug("|{0}| >> Found preferred...".format(_str_func))                  
                    _foundPrerred = True
                    break
        
        #Attributes =====================================================================================
        #Master global control
        d_MasterGlobalScale = cgmMeta.validateAttrArg(globalScaleAttr,noneValid=True)    
        
        #Stretch
        if stretch and stretch not in ['translate','scale']:
            log.debug("|{0}| >> Invalid stretch arg: {1}. Using 'translate'".format(_str_func,stretch))
            stretch = 'translate'
        if stretch == 'scale':
            raise NotImplementedError,"|{0}| >> Scale method not done".format(_str_func)
            
        #Handles =======================================================================================
        ml_handles = cgmMeta.validateObjListArg(handles,'cgmObject',noneValid=True)
        if len(ml_handles)>len(ml_jointChain):#Check handle length to joint list
            raise ValueError,"|{0}| >> More handles than joints. joints: {1}| handles: {2}.".format(_str_func,len(ml_jointChain),len(ml_handles))
            
    
        mRPHandle = cgmMeta.validateObjArg(rpHandle,'cgmObject',noneValid=True)
        if mRPHandle and mRPHandle in ml_handles:
            raise NotImplementedError,"|{0}| >> rpHandle can't be a measure handle".format(_str_func)
            
        #Control object
        mControl = cgmMeta.validateObjArg(controlObject,'cgmObject',noneValid=True)
        if mControl:
            log.debug("|{0}| >> mControl: {1}.".format(_str_func,mControl))                  
    
        #Figure out our aimaxis
        str_localAimSingle = orientation[0]
    
    
        #Create IK handle ==================================================================================
        buffer = mc.ikHandle( sj=mStart.mNode, ee=mEnd.mNode,
                              solver = solverType, forceSolver = True,
                              snapHandleFlagToggle=True )  	
    
    
        #>>> Name
        log.debug(buffer)
        mIKHandle = cgmMeta.asMeta(buffer[0],'cgmObject',setClass=True)
        mIKHandle.addAttr('cgmName',str_baseName,attrType='string',lock=True)
        mIKHandle.doName()
    
        ml_rigObjectsToConnect.append(mIKHandle)
    
        mIKEffector = cgmMeta.asMeta(buffer[1],'cgmNode',setClass=True)
        mIKEffector.addAttr('cgmName',str_baseName,attrType='string',lock=True)    
        mIKEffector.doName()
    
        #>>> Control
        if not mControl:
            mControl = mIKHandle
        else:
            mIKHandle.parent = mControl
            
        #>>> Store our start and end
        mIKHandle.connectChildNode(mStart,'jointStart','ikOwner')
        mIKHandle.connectChildNode(mEnd,'jointEnd','ikOwner')
        
    
        #>>>Stetch #===============================================================================
        mPlug_lockMid = False  
        ml_distanceShapes = []
        ml_distanceObjects = []   
        mPlug_globalScale = False
        
        if stretch:
            log.debug("|{0}| >> Stretch setup...".format(_str_func))
            mPlug_globalScale = cgmMeta.cgmAttr(mIKHandle.mNode,'masterScale',value = 1.0, lock =True, hidden = True)
            
            #Get our distance -----------------------------------------------------------------------
            #mPlug_ikRegScale = cgmMeta.cgmAttr(mIKHandle.mNode,'result_ikRegScale',value = 1.0, lock =True, hidden = True)
            #mPlug_distSumRaw = cgmMeta.cgmAttr(mIKHandle.mNode,'distanceSumLive',value = 1.0, lock =True, hidden = True)
            #mPlug_distSumNormal = cgmMeta.cgmAttr(mIKHandle.mNode,'result_distSumLive',value = 1.0, lock =True, hidden = True)
            
            
            
            f_baseDist = DIST.get_distance_between_targets(l_jointChain)
            mPlug_lengthFullNormal = cgmMeta.cgmAttr(mIKHandle,'result_fullLengthNormal',keyable = False, hidden=True, attrType = 'float')
            _arg = "{0} = {1} * {2}".format(mPlug_lengthFullNormal.p_combinedName,
                                            f_baseDist,
                                            mPlug_globalScale.p_combinedName)
            NODEFAC.argsToNodes(_arg).doBuild()
            #--------------------------------------------------------------------------------------
            
            
            mPlug_autoStretch = cgmMeta.cgmAttr(mControl,'autoStretch',initialValue = 1, defaultValue = 1, keyable = True, attrType = 'float', minValue = 0, maxValue = 1)
            
            if len(ml_jointChain) == 3 and lockMid:
                log.debug("|{0}| >> MidLock setup possible...".format(_str_func))
                
                if lockMid:mPlug_lockMid = cgmMeta.cgmAttr(mControl,'lockMid',
                                                           initialValue = 0, attrType = 'float',
                                                           keyable = True, minValue = 0, maxValue = 1)
        
                if addLengthMulti:
                    mPlug_lengthUpr= cgmMeta.cgmAttr(mControl,'lengthUpr',attrType='float',value = 1, defaultValue = 1,minValue=0,keyable = True)
                    mPlug_lengthLwr = cgmMeta.cgmAttr(mControl,'lengthLwr',attrType='float',value = 1, defaultValue = 1,minValue=0,keyable = True)	
                    ml_multiPlugs = [mPlug_lengthUpr,mPlug_lengthLwr]
        
            #Check our handles for stretching
            if len(ml_handles)!= len(ml_jointChain):#we need a handle per joint for measuring purposes
                log.debug("create_IKHandle>>> Making handles")
                ml_buffer = ml_handles
                ml_handles = []
                for j in ml_jointChain:
                    m_match = False
                    for h in ml_buffer:
                        if MATH.is_vector_equivalent(j.getPosition(),h.getPosition()):
                            log.debug("create_IKHandle>>> '%s' handle matches: '%s'"%(h.getShortName(),j.getShortName()))
                            m_match = h
                    if not m_match:#make one
                        m_match = j.doLoc(nameLink = True)
                        m_match.addAttr('cgmTypeModifier','stretchMeasure')
                        m_match.doName()
                    ml_handles.append(m_match)
                    ml_rigObjectsToConnect.append(m_match)
    
                #>>>TODO Add hide stuff
        
                #>>>Do Handles
                mMidHandle = False   
                if ml_handles:
                    if len(ml_handles) == 1:
                        mMidHandle = ml_handles[0]
                    else:
                        mid = int((len(ml_handles))/2)
                        mMidHandle = ml_handles[mid]
                    
                    log.debug("|{0}| >> mid handle: {1}".format(_str_func,mMidHandle))

            #Overall stretch

            md_baseDistReturn = RIGCREATE.distanceMeasure(ml_handles[0].mNode,ml_handles[-1].mNode,baseName=str_baseName)
            
            md_baseDistReturn['mEnd'].p_parent = mControl
            
            ml_rigObjectsToParent.append(md_baseDistReturn['mDag'])
            mPlug_baseDist = cgmMeta.cgmAttr(mIKHandle.mNode,'ikDistBase' , attrType = 'float', value = md_baseDistReturn['mShape'].distance , lock =True , hidden = True)	
            mPlug_baseDistRaw = cgmMeta.cgmAttr(mIKHandle.mNode,'ikDistRaw' , value = 1.0 , lock =True , hidden = True)
            mPlug_baseDistRaw.doConnectIn("%s.distance"%md_baseDistReturn['mShape'].mNode)
            mPlug_baseDistNormal = cgmMeta.cgmAttr(mIKHandle.mNode,'result_ikBaseNormal',value = 1.0, lock =True, hidden = True)
            mPlug_ikDistNormal = cgmMeta.cgmAttr(mIKHandle.mNode,'result_ikDistNormal',value = 1.0, lock =True, hidden = True)	
            mPlug_ikScaleRaw = cgmMeta.cgmAttr(mIKHandle.mNode,'result_ikScaleRaw',value = 1.0, lock =True, hidden = True)
            mPlug_ikScale = cgmMeta.cgmAttr(mIKHandle.mNode,'result_ikScale',value = 1.0, lock =True, hidden = True)            
            mPlug_ikClampScale = cgmMeta.cgmAttr(mIKHandle.mNode,'result_ikClampScale',value = 1.0, lock =True, hidden = True)
            mPlug_ikClampMax = cgmMeta.cgmAttr(mIKHandle.mNode,'result_ikClampMax',value = 1.0, lock =True, hidden = True)
    
            #EVEN METHOD ==================================================================================================
            #Normal base -----------------------------------------------------------------------
            arg = "%s = %s * %s"%(mPlug_baseDistNormal.p_combinedName,
                                  mPlug_baseDist.p_combinedName,
                                  mPlug_globalScale.p_combinedName)
            NODEFAC.argsToNodes(arg).doBuild()
    
            #Normal Length-------------------------------------------------------------------
            arg = "%s = %s / %s"%(mPlug_ikDistNormal.p_combinedName,
                                  mPlug_baseDistRaw.p_combinedName,
                                  mPlug_globalScale.p_combinedName)
            NODEFAC.argsToNodes(arg).doBuild()	
    
            #ik scale raw---------------------------------------------------
            arg = "%s = %s / %s"%(mPlug_ikScaleRaw.p_combinedName,
                                  mPlug_baseDistRaw.p_combinedName,
                                  mPlug_baseDistNormal.p_combinedName)
            NODEFAC.argsToNodes(arg).doBuild()	
            
            
            #ik scale real ----------------------------------------
            _arg = "{0} = if {1} <= {2}: {3} else 1".format(mPlug_ikScale.p_combinedName,
                                                            mPlug_baseDistNormal.p_combinedName,
                                                            mPlug_lengthFullNormal.p_combinedName,
                                                            mPlug_ikScaleRaw.p_combinedName)
            NODEFAC.argsToNodes(_arg).doBuild()            
            

            #ik max clamp-------------------------------------------------------------
            """ This is for maya 2013 (at least) which honors the max over the  min """
            arg = "%s = if %s >= 1: %s else 1"%(mPlug_ikClampMax.p_combinedName,
                                                mPlug_ikScale.p_combinedName,
                                                mPlug_ikScale.p_combinedName)
            NODEFAC.argsToNodes(arg).doBuild()
    
            #ik clamp scale-----------------------------------------------
            arg = "%s = clamp(1,%s,%s)"%(mPlug_ikClampScale.p_combinedName,
                                         mPlug_ikClampMax.p_combinedName,
                                         mPlug_ikScale.p_combinedName)
            NODEFAC.argsToNodes(arg).doBuild()	
    
            #Create our blend to stretch or not - blend normal base and stretch base
            mi_stretchBlend = cgmMeta.cgmNode(nodeType= 'blendTwoAttr')
            mi_stretchBlend.addAttr('cgmName','%s_stretchBlend'%(baseName),lock=True)
            mi_stretchBlend.doName()
            ATTR.set(mi_stretchBlend.mNode,"input[0]",1)
            mPlug_ikClampScale.doConnectOut("%s.input[1]"%mi_stretchBlend.mNode)
            mPlug_autoStretch.doConnectOut("%s.attributesBlender"%mi_stretchBlend.mNode)
            #--------------------------------------------------------------------------------------------
            
            #Make our distance objects per segment ===========================================================
            l_segments = LISTS.get_listPairs(ml_handles)
            for i,seg in enumerate(l_segments):#Make our measure nodes
                buffer =  RIGCREATE.distanceMeasure(seg[0].mNode,seg[-1].mNode,baseName="{0}_{1}".format(str_baseName,i))
                ml_distanceShapes.append(buffer['mShape'])
                ml_distanceObjects.append(buffer['mDag'])
                #>>>TODO Add hide stuff
            ml_rigObjectsToParent.extend(ml_distanceObjects)
            ml_rigObjectsToConnect.extend(ml_handles)            
            
            
            #Reg method ===========================================================================================
            """
            arg = "{0} = {1} * {2}".format(mPlug_distSumNormal.p_combinedName,
                                           mPlug_distSumRaw.p_combinedName,
                                           mPlug_globalScale.p_combinedName)
            
            NODEFAC.argsToNodes(arg).doBuild()
            
            argSum = ' + '.join(["{0}.distance".format(mShape.mNode) for mShape in ml_distanceShapes])
            arg = "{0} = {1}".format(mPlug_distSumRaw.p_combinedName,
                                     argSum)"""
            
            #--------------------------------------------------------------------------------------------
    
            for i,i_jnt in enumerate(ml_jointChain[:-1]):
                #Make some attrs
                mPlug_baseDist= cgmMeta.cgmAttr(mIKHandle.mNode,"baseDist_%s"%i,attrType = 'float' , value = ml_distanceShapes[i].distance , lock=True,minValue = 0)
                mPlug_rawDist = cgmMeta.cgmAttr(mIKHandle.mNode,"baseRaw_%s"%i,attrType = 'float', initialValue=0 , lock=True , minValue = 0)				  	    
                mPlug_normalBaseDist = cgmMeta.cgmAttr(mIKHandle.mNode,"baseNormal_%s"%i,attrType = 'float', initialValue=0 , lock=True , minValue = 0)			
                mPlug_normalDist = cgmMeta.cgmAttr(mIKHandle.mNode,"distNormal_%s"%i,attrType = 'float',initialValue=0,lock=True,minValue = 0)		
                mPlug_stretchDist = cgmMeta.cgmAttr(mIKHandle.mNode,"result_stretchDist_%s"%i,attrType = 'float',initialValue=0,lock=True,minValue = 0)			    
                mPlug_stretchNormalDist = cgmMeta.cgmAttr(mIKHandle.mNode,"result_stretchNormalDist_%s"%i,attrType = 'float',initialValue=0,lock=True,minValue = 0)			    	    
                mPlug_resultSegmentScale = cgmMeta.cgmAttr(mIKHandle.mNode,"segmentScale_%s"%i,attrType = 'float',initialValue=0,lock=True,minValue = 0)	
    
                #Raw distance in
                mPlug_rawDist.doConnectIn("%s.distance"%ml_distanceShapes[i].mNode)	  
    
                #Normal base distance
                arg = "%s = %s * %s"%(mPlug_normalBaseDist.p_combinedName,
                                      mPlug_baseDist.p_combinedName,
                                      mPlug_globalScale.p_combinedName)
                NODEFAC.argsToNodes(arg).doBuild()
    
                #Normal distance
                arg = "%s = %s / %s"%(mPlug_normalDist.p_combinedName,
                                      mPlug_rawDist.p_combinedName,
                                      mPlug_globalScale.p_combinedName)
                NODEFAC.argsToNodes(arg).doBuild()
    
                #Stretch Distance
                arg = "%s = %s * %s.output"%(mPlug_stretchDist.p_combinedName,
                                             mPlug_normalBaseDist.p_combinedName,
                                             mi_stretchBlend.getShortName())
                NODEFAC.argsToNodes(arg).doBuild()
    
                #Then pull the global out of the stretchdistance 
                arg = "%s = %s / %s"%(mPlug_stretchNormalDist.p_combinedName,
                                      mPlug_stretchDist.p_combinedName,
                                      mPlug_globalScale.p_combinedName)
                NODEFAC.argsToNodes(arg).doBuild()	    
    
                #Segment scale
                arg = "%s = %s / %s"%(mPlug_resultSegmentScale.p_combinedName,
                                      mPlug_normalDist.p_combinedName,
                                      mPlug_baseDist.p_combinedName)
                NODEFAC.argsToNodes(arg).doBuild()
    
                #Create our blend to stretch or not - blend normal base and stretch base
                mi_blend = cgmMeta.cgmNode(nodeType= 'blendTwoAttr')
                mi_blend.addAttr('cgmName','%s_stretch_to_lockMid'%(i_jnt.getBaseName()),lock=True)
                mi_blend.doName()
                if mPlug_lockMid:
                    mPlug_lockMid.doConnectOut("%s.attributesBlender"%mi_blend.mNode)
    
                if stretch == 'translate':
                    #Base Normal, Dist Normal
                    mPlug_stretchNormalDist.doConnectOut("%s.input[0]"%mi_blend.mNode)
                    mPlug_normalDist.doConnectOut("%s.input[1]"%mi_blend.mNode)
                    ATTR.connect("%s.output"%mi_blend.mNode,"%s.t%s"%(ml_jointChain[i+1].mNode,str_localAimSingle))
    
        #>>> addLengthMulti
        if addLengthMulti:
            log.debug("|{0}| >> addLengthMulti...".format(_str_func))
            
            if len(ml_jointChain[:-1]) == 2:
                #grab the plug
    
                i_mdLengthMulti = cgmMeta.cgmNode(mc.createNode('multiplyDivide'))
                i_mdLengthMulti.operation = 1
                i_mdLengthMulti.doStore('cgmName',baseName)
                i_mdLengthMulti.addAttr('cgmTypeModifier','lengthMulti')
                i_mdLengthMulti.doName()
    
                l_mdAxis = ['X','Y','Z']
                for i,i_jnt in enumerate(ml_jointChain[:-1]):
                    #grab the plug
                    mPlug_driven = cgmMeta.cgmAttr(ml_jointChain[i+1],'t%s'%str_localAimSingle)
                    plug = ATTR.break_connection(mPlug_driven.p_combinedName)
                    if not plug:raise StandardError,"create_IKHandle>>> Should have found a plug on: %s.t%s"%(ml_jointChain[i+1].mNode,str_localAimSingle)
    
                    ATTR.connect(plug,#>>
                                 '%s.input1%s'%(i_mdLengthMulti.mNode,l_mdAxis[i]))#Connect the old plug data
                    ml_multiPlugs[i].doConnectOut('%s.input2%s'%(i_mdLengthMulti.mNode,l_mdAxis[i]))#Connect in the mutliDriver	
                    mPlug_driven.doConnectIn('%s.output.output%s'%(i_mdLengthMulti.mNode,l_mdAxis[i]))#Connect it back to our driven
    
            else:
                log.error("|{0}| >> addLengthMulti only currently supports 2 segments. Found: {1}".format(_str_func,len(ml_jointChain[:-1])))
                
    
        #>>> rpSetup
        if solverType == 'ikRPsolver' and rpHandle:
            log.debug("|{0}| >> RP Handle setup...".format(_str_func))
            
            if not mRPHandle:
                #Make one
                mRPHandle = mMidHandle.doLoc()
                mRPHandle.addAttr('cgmTypeModifier','poleVector')
                mRPHandle.doName()
                ml_rigObjectsToConnect.append(mRPHandle)
            cBuffer = mc.poleVectorConstraint(mRPHandle.mNode,mIKHandle.mNode)
    
            #Fix rp
            #rotValue = mStart.getAttr('r%s'%str_localAimSingle)    
            #if not cgmMath.isFloatEquivalent(rotValue,0):#if we have a value, we need to fix it
                #IKHandle_fixTwist(mIKHandle)	
    
    
        #>>> Plug in global scale
        if d_MasterGlobalScale and mPlug_globalScale:
            d_MasterGlobalScale['mi_plug'].doConnectOut(mPlug_globalScale.p_combinedName)
    
        #>>> Connect our iModule vis stuff
        if mModule:#if we have a module, connect vis
            for mObj in ml_rigObjectsToConnect:
                mObj.overrideEnabled = 1		
                cgmMeta.cgmAttr(mModule.rigNull.mNode,'gutsVis',lock=False).doConnectOut("%s.%s"%(mObj.mNode,'overrideVisibility'))
                cgmMeta.cgmAttr(mModule.rigNull.mNode,'gutsLock',lock=False).doConnectOut("%s.%s"%(mObj.mNode,'overrideDisplayType'))    
            for mObj in ml_rigObjectsToParent:
                mObj.parent = mModule.rigNull.mNode
    
        #>>> Return dict
        d_return = {'mHandle':mIKHandle,'mEffector':mIKEffector}
        if mPlug_lockMid:
            d_return['mPlug_lockMid'] = mPlug_lockMid	
            d_return['ml_measureObjects']=ml_distanceObjects	
        if stretch:
            d_return['mPlug_autoStretch'] = mPlug_autoStretch
            d_return['ml_distHandles']=ml_handles
        if mRPHandle:
            d_return['mRPHandle'] = mRPHandle
        if addLengthMulti:
            d_return['ml_lengthMultiPlugs'] = ml_multiPlugs
    
        if not _foundPrerred:log.warning("create_IKHandle>>> No preferred angle values found. The chain probably won't work as expected: %s"%l_jointChain)
    
        return d_return   
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err)





def handle_fixTwist(ikHandle, aimAxis = None):
    #>>> Data gather and arg check    
    _str_func = 'handle_fixTwist'
    log.debug("|{0}| >> ...".format(_str_func))
    
    mIKHandle = cgmMeta.validateObjArg(ikHandle,'cgmObject',noneValid=False)
    if mIKHandle.getMayaType() != 'ikHandle':
        raise ValueError,"|{0}| >> {1} not an 'ikHandle'. Type: ".format(_str_func,mIKHandle.mNode, mIKHandle.getMayaType())
        

    jointStart = mIKHandle.getMessage('jointStart')
    if not jointStart:
        raise ValueError,"|{0}| >> {1} | no jointStart dataFound".format(_str_func,mIKHandle.mNode, mIKHandle.getMayaType())

    mStartJoint = cgmMeta.validateObjArg(jointStart[0],'cgmObject',noneValid=False)

    #Find the aim axis
    if aimAxis == None:
        raise NotImplementedError,"Need aimAxis. Not done migrating solver"
        log.debug("|{0}| >> find aim axis...".format(_str_func))
        
        return 
        v_localAim = MATH.get_vector_of_two_points(mStartJoint.p_position, mStartJoint.getChildren(asMeta=True)[0].p_position)
        
        str_localAim = dictionary.returnVectorToString(v_localAim)
        str_localAimSingle = str_localAim[0]
        log.debug("IKHandle_fixTwist>>> vector aim: %s | str aim: %s"%(v_localAim,str_localAim))  

    #Check rotation:
    mPlug_rot = cgmMeta.cgmAttr(mStartJoint,'r'+aimAxis)
    #rotValue = mStartJoint.getAttr('r%s'%str_localAimSingle)
    #First we try our rotate value
    if not MATH.is_float_equivalent(mPlug_rot.value,0,2):
        log.debug("|{0}| >> Not zero...".format(_str_func))        
        mIKHandle.twist = 0
    if not MATH.is_float_equivalent(mPlug_rot.value,0,2):
        log.debug("|{0}| >> Trying inverse to start...".format(_str_func))                
        mIKHandle.twist = -mPlug_rot.value#try inversed driven joint rotate value first

    if not MATH.is_float_equivalent(mPlug_rot.value,0,2):#if we have a value, we need to fix it
        log.debug("|{0}| >> drivenAttr='{1}',driverAttr='{2}.twist',minIn = -180, maxIn = 180, maxIterations = 75,matchValue=0.0001".format(_str_func,mPlug_rot.p_combinedName,mIKHandle.p_nameShort))        
        
        RIGGEN.matchValue_iterator(drivenAttr="%s.r%s"%(mStartJoint.mNode,aimAxis),
                                   driverAttr="%s.twist"%mIKHandle.mNode,
                                   minIn = -170, maxIn = 179,
                                   maxIterations = 30,
                                   matchValue=0)
        log.debug("|{0}| >> drivenAttr='{1}',driverAttr='{2}.twist',minIn = -180, maxIn = 180, maxIterations = 75,matchValue=0.0001".format(_str_func,mPlug_rot.p_combinedName,mIKHandle.p_nameShort))        
        
        #log.debug("rUtils.matchValue_iterator(drivenAttr='%s.r%s',driverAttr='%s.twist',minIn = -180, maxIn = 180, maxIterations = 75,matchValue=0.0001)"%(mStartJoint.getShortName(),str_localAimSingle,mIKHandle.getShortName()))
    return True


def get_midIK_basePos(ml_handles = [], baseAxis = 'y+', markPos = False, forceMidToHandle=False):
    _str_func = 'get_midIK_basePos'
    log.debug("|{0}| >> ".format(_str_func)+ '-'*80)
    
    ml_handles = cgmMeta.validateObjListArg(ml_handles,'cgmObject')
    
    log.debug("|{0}| >> Using: {1}".format(_str_func,[mObj.p_nameBase for mObj in ml_handles]))
    
    #Mid dat... ----------------------------------------------------------------------
    _len_handles = len(ml_handles)
    if _len_handles == 1:
        mid=0
        mMidHandle = ml_handles[0]
    else:
        
        mid = int(_len_handles)/2
        mMidHandle = ml_handles[mid]
        
    log.debug("|{0}| >> mid: {1}".format(_str_func,mid))
    
    b_absMid = False
    if MATH.is_even(_len_handles) and not forceMidToHandle:
        log.debug("|{0}| >> absolute mid mode...".format(_str_func,mid))
        b_absMid = True
        
    
    #...Main vector -----------------------------------------------------------------------
    #mOrientHelper = self.mBlock.orientHelper
    vec_base = MATH.get_obj_vector(ml_handles[0], 'y+')
    log.debug("|{0}| >> Block up: {1}".format(_str_func,vec_base))
    
    #...Get vector -----------------------------------------------------------------------
    if b_absMid:
        crvCubic = CORERIG.create_at(ml_handles, create= 'curve')
        pos_mid = CURVES.getMidPoint(crvCubic)
        mc.delete(crvCubic)
    else:
        pos_mid = mMidHandle.p_position
        
    crv = CORERIG.create_at([ml_handles[0].mNode,ml_handles[-1].mNode], create= 'curveLinear')
    pos_close = DIST.get_closest_point(pos_mid, crv, markPos)[0]
    log.debug("|{0}| >> Pos close: {1} | Pos mid: {2}".format(_str_func,pos_close,pos_mid))
    
    if MATH.is_vector_equivalent(pos_mid,pos_close,3):
        log.debug("|{0}| >> Mid on linear line, using base vector".format(_str_func))
        vec_use = vec_base
    else:
        vec_use = MATH.get_vector_of_two_points(pos_close,pos_mid)
        mc.delete(crv)
    
    #...Get length -----------------------------------------------------------------------
    #dist_helper = 0
    #if ml_handles[-1].getMessage('pivotHelper'):
        #log.debug("|{0}| >> pivotHelper found!".format(_str_func))
        #dist_helper = max(POS.get_bb_size(ml_handles[-1].getMessage('pivotHelper')))
        
    dist_min = DIST.get_distance_between_points(ml_handles[0].p_position, pos_mid)/4.0
    dist_base = DIST.get_distance_between_points(pos_mid, pos_close)
    
    #...get new pos
    dist_use = MATH.Clamp(dist_base, dist_min, None)
    log.debug("|{0}| >> Dist min: {1} | dist base: {2} | use: {3}".format(_str_func,
                                                                          dist_min,
                                                                          dist_base,
                                                                          dist_use))
    
    pos_use = DIST.get_pos_by_vec_dist(pos_mid,vec_use,dist_use*2)
    pos_use2 = DIST.get_pos_by_vec_dist(pos_mid,vec_base,dist_use*2)
    
    #reload(LOC)
    if markPos:
        LOC.create(position=pos_use,name='pos1')
        LOC.create(position=pos_use2,name='pos2')
    
    return pos_use

def ribbon_seal(driven1 = None,
                driven2 = None,

                influences1 = None,
                influences2 = None,

                msgDriver = None,#...msgLink on joint to a driver group for constaint purposes


                extendEnds = False,


                loftAxis = 'z',

                orientation = 'zyx',
                secondaryAxis = 'y+',

                baseName = None,
                baseName1=None,
                baseName2=None,

                connectBy = 'constraint',

                sectionSpans = 1, 
                settingsControl = None,
                specialMode = None,

                sealSplit = False,
                sealDriver1 = None,
                sealDriver2 = None,
                sealDriverMid = None,
                sealName1 = 'left',
                sealName2 = 'right',
                sealNameMid = 'center',

                maxValue = 10.0,
                extend2LoftTo1Ends = True,

                moduleInstance = None,
                parentGutsTo = None):
    """
    Dual ribbon setup with seal
    """
    try:
        _str_func = 'ribbon_seal'

        ml_rigObjectsToConnect = []
        md_drivers = {}
        md_base = {}
        md_seal = {}
        md_blend = {}
        md_follicles = {}
        md_follicleShapes ={}
        str_baseName = baseName
        ml_toParent = []
        d_dat = {1:{},
                 2:{}}

        if msgDriver:
            ml_missingDrivers = []

        def check_msgDriver(mObj):
            mDriver = mObj.getMessageAsMeta(msgDriver)
            if mDriver:
                md_drivers[mObj] = mDriver
            else:
                log.error("|{0}| >> Missing driver: {1}".format(_str_func,mObj))
                ml_missingDrivers.append(mObj)
                return False

        #>>> Verify ===================================================================================
        log.debug("|{0}| >> driven1 [Check]...".format(_str_func))        
        d_dat[1]['driven'] = cgmMeta.validateObjListArg(driven1,
                                                        mType = 'cgmObject',
                                                        mayaType=['joint'], noneValid = False)
        log.debug("|{0}| >> driven2 [Check]...".format(_str_func))                
        d_dat[2]['driven'] = cgmMeta.validateObjListArg(driven2,
                                                        mType = 'cgmObject',
                                                        mayaType=['joint'], noneValid = False)
        
        
        d_dat[1]['LoftTargets']=d_dat[1]['driven']
        d_dat[2]['LoftTargets'] = d_dat[2]['driven']
        
        if extend2LoftTo1Ends:
            d_dat[2]['LoftTargets'] = [d_dat[1]['driven'][0]] + d_dat[2]['driven'] + [d_dat[1]['driven'][-1]]


        #Check our msgDrivers -----------------------------------------------------------
        if msgDriver:
            log.debug("|{0}| >> msgDriver [Check]...".format(_str_func))
            for mObj in d_dat[1]['driven'] + d_dat[2]['driven']:
                if mObj not in ml_missingDrivers:
                    check_msgDriver(mObj)
            if ml_missingDrivers:
                raise ValueError,"Missing drivers. See errors."
            log.debug("|{0}| >> msgDriver [Pass]...".format(_str_func))


        d_dat[1]['int_driven']  = len(d_dat[1]['driven'])
        d_dat[2]['int_driven']  = len(d_dat[2]['driven'])

        log.debug("|{0}| >> Driven lengths   {1} | {2}".format(_str_func,d_dat[1]['int_driven'] ,d_dat[2]['int_driven'] ))                


        log.debug("|{0}| >> influences1 [Check]...".format(_str_func))                
        d_dat[1]['mInfluences']  = cgmMeta.validateObjListArg(influences1,
                                                              mType = 'cgmObject',
                                                              mayaType=['joint'], noneValid = False)

        log.debug("|{0}| >> influences2 [Check]...".format(_str_func))                    
        d_dat[2]['mInfluences']  = cgmMeta.validateObjListArg(influences2,
                                                              mType = 'cgmObject',
                                                              mayaType=['joint'], noneValid = False)        


        d_dat[1]['int_influences'] = len(d_dat[1]['mInfluences'] )
        d_dat[2]['int_influences'] = len(d_dat[2]['mInfluences'] )

        log.debug("|{0}| >> Influence lengths   {1} | {2}".format(_str_func,
                                                                  d_dat[1]['int_influences'],
                                                                  d_dat[2]['mInfluences']))                        


        mi_mayaOrientation = VALID.simpleOrientation(orientation)
        str_orientation = mi_mayaOrientation.p_string
        str_secondaryAxis = VALID.stringArg(secondaryAxis,noneValid=True)        

        if specialMode and specialMode not in ['noStartEnd','endsToInfluences']:
            raise ValueError,"Unknown special mode: {0}".format(specialMode)


        #module -----------------------------------------------------------------------------------------------
        mModule = cgmMeta.validateObjArg(moduleInstance,noneValid = True)
        #try:mModule.isModule()
        #except:mModule = False

        mi_rigNull = False	
        if mModule:
            log.debug("|{0}| >> mModule [Check]...".format(_str_func))            
            mi_rigNull = mModule.rigNull	
            if str_baseName is None:
                str_baseName = mModule.getPartNameBase()#Get part base name	    
        if not baseName:baseName = 'testRibbonSeal' 
        if not baseName1:baseName1 = 'ribbon1'
        if not baseName2:baseName2 = 'ribbon2'

        d_check = {'driven1':d_dat[1]['int_driven'] ,
                   'driven2':d_dat[2]['int_driven'] }

        for k,i in d_check.iteritems():
            if i<3:
                raise ValueError,"needs at least three driven. Found : {0} | {1}".format(k,i)

        log.debug("|{0}| >> Group [Check]...".format(_str_func))                    
        if parentGutsTo is None:
            mGroup = cgmMeta.cgmObject(name = 'newgroup')
            mGroup.addAttr('cgmName', str(baseName), lock=True)
            mGroup.addAttr('cgmTypeModifier','segmentStuff', lock=True)
            mGroup.doName()
        else:
            mGroup = cgmMeta.validateObjArg(parentGutsTo,'cgmObject',False)

        if mModule:
            mGroup.parent = mModule.rigNull

        #Good way to verify an instance list? #validate orientation             
        #> axis -------------------------------------------------------------
        """
        axis_aim = VALID.simpleAxis("{0}+".format(str_orientation[0]))
        axis_aimNeg = axis_aim.inverse
        axis_up = VALID.simpleAxis("{0}+".format(str_orientation [1]))
        axis_out = VALID.simpleAxis("{0}+".format(str_orientation [2]))

        v_aim = axis_aim.p_vector#aimVector
        v_aimNeg = axis_aimNeg.p_vector#aimVectorNegative
        v_up = axis_up.p_vector   #upVector
        v_out = axis_out.p_vector

        str_up = axis_up.p_string

        loftAxis2 = False
        #Figure out our loft axis stuff
        if loftAxis not in  orientation:
            _lower_loftAxis = loftAxis.lower()
            if _lower_loftAxis in ['out','up']:
                if _lower_loftAxis == 'out':
                    loftAxis = str_orientation[2]
                else:
                    loftAxis = str_orientation[1]
            else:
                raise ValueError,"Not sure what to do with loftAxis: {0}".format(loftAxis)
        """

        outChannel = str_orientation[2]#outChannel
        upChannel = str_orientation[1]
        #upChannel = '{0}up'.format(str_orientation[1])#upChannel



        #>>> Ribbon Surface ============================================================================        
        log.debug("|{0}| >> Ribbons generating...".format(_str_func))

        l_surfaceReturn1 = ribbon_createSurface(d_dat[1]['LoftTargets'],loftAxis,sectionSpans,extendEnds)

        d_dat[1]['mSurf'] = cgmMeta.validateObjArg( l_surfaceReturn1[0],'cgmObject',setClass = True )
        d_dat[1]['mSurf'].addAttr('cgmName',str(baseName1),attrType='string',lock=True)    
        d_dat[1]['mSurf'].addAttr('cgmType','controlSurface',attrType='string',lock=True)
        d_dat[1]['mSurf'].doName()

        l_surfaceReturn2 = ribbon_createSurface(d_dat[2]['LoftTargets'],loftAxis,sectionSpans,extendEnds)        
        d_dat[2]['mSurf'] = cgmMeta.validateObjArg( l_surfaceReturn1[0],'cgmObject',setClass = True )
        d_dat[2]['mSurf'].addAttr('cgmName',str(baseName2),attrType='string',lock=True)    
        d_dat[2]['mSurf'].addAttr('cgmType','controlSurface',attrType='string',lock=True)
        d_dat[2]['mSurf'].doName()        


        log.debug("d_dat[1]['mSurf']: {0}".format(d_dat[1]['mSurf']))
        log.debug("d_dat[2]['mSurf']: {0}".format(d_dat[2]['mSurf']))



        ml_toConnect = []
        ml_toConnect.extend([d_dat[1]['mSurf'],d_dat[2]['mSurf']])
        
        #Special Mode =================================================================================
        if specialMode in ['noStartEnd','endsToInfluences']:
            log.debug("|{0}| >> Special Mode: {1}".format(_str_func,specialMode)+cgmGEN._str_subLine)

            if specialMode == 'endsToInfluences':
                d_special = {'1start':{'mObj':d_dat[1]['driven'][0],
                                       'mDriver':d_dat[1]['mInfluences'][0]},
                             '1end':{'mObj':d_dat[1]['driven'][-1],
                                     'mDriver':d_dat[1]['mInfluences'][-1]},}
                """
                             '2start':{'mObj':d_dat[2]['driven'][0],
                                       'mDriver':d_dat[2]['mInfluences'][0]},
                             '2end':{'mObj':d_dat[2]['driven'][-1],
                                     'mDriver':d_dat[2]['mInfluences'][-1]}}"""

                for n,dat in d_special.iteritems():
                    mObj = dat['mObj']
                    mDriven = md_drivers[mObj]
                    mDriver = dat['mDriver']
                    log.debug("|{0}| >> {1} | Driver: {2}".format(_str_func,i,mDriven))

                    _const = mc.parentConstraint([mDriver.mNode],mDriven.mNode,maintainOffset=True)[0]
                    ATTR.set(_const,'interpType',2)

            d_dat[1]['driven'] = d_dat[1]['driven'][1:-1]
            #d_dat[2]['driven'] = d_dat[2]['driven'][1:-1]            
            driven1 = driven1[1:-1]
            #driven2 = driven2[1:-1]

        #>>> Setup our Attributes ================================================================
        log.debug("|{0}| >> Settings...".format(_str_func))        
        if settingsControl:
            mSettings = cgmMeta.validateObjArg(settingsControl,'cgmObject')
        else:
            mSettings = d_dat[1]['mSurf']




        mPlug_sealHeight = cgmMeta.cgmAttr(mSettings.mNode,
                                           'sealHeight',
                                           attrType='float',
                                           lock=False,
                                           keyable=True)
        mPlug_sealHeight.doDefault(.5)
        mPlug_sealHeight.value = .5


        #>>> Setup blend results --------------------------------------------------------------------
        if sealSplit:
            d_split = RIGGEN.split_blends(driven1,#d_dat[1]['driven'],
                                          driven2,#d_dat[2]['driven'],
                                          sealDriver1,
                                          sealDriver2,
                                          sealDriverMid,
                                          nameSeal1=sealName1,
                                          nameSeal2=sealName2,
                                          nameSealMid=sealNameMid,
                                          settingsControl = mSettings,
                                          maxValue=maxValue)
            for k,d in d_split.iteritems():
                d_dat[k]['mPlugs'] = d['mPlugs']

        else:
            mPlug_seal = cgmMeta.cgmAttr(mSettings.mNode,
                                         'seal',
                                         attrType='float',
                                         lock=False,
                                         keyable=True)

            mPlug_sealOn = cgmMeta.cgmAttr(mSettings,'result_sealOn',attrType='float',
                                           defaultValue = 0,keyable = False,lock=True,
                                           hidden=False)

            mPlug_sealOff= cgmMeta.cgmAttr(mSettings,'result_sealOff',attrType='float',
                                           defaultValue = 0,keyable = False,lock=True,
                                           hidden=False)

            NODEFAC.createSingleBlendNetwork(mPlug_seal.p_combinedName,
                                                 mPlug_sealOn.p_combinedName,
                                                 mPlug_sealOff.p_combinedName)

            d_dat[1]['mPlug_sealOn'] = mPlug_sealOn
            d_dat[1]['mPlug_sealOff'] = mPlug_sealOff
            d_dat[2]['mPlug_sealOn'] = mPlug_sealOn
            d_dat[2]['mPlug_sealOff'] = mPlug_sealOff                    

        mPlug_FavorOneMe = cgmMeta.cgmAttr(mSettings,'result_sealOneMe',attrType='float',
                                           defaultValue = 0,keyable = False,lock=True,
                                           hidden=False)
        mPlug_FavorOneThee = cgmMeta.cgmAttr(mSettings,'result_sealOneThee',attrType='float',
                                             defaultValue = 0,keyable = False,lock=True,
                                             hidden=False)
        mPlug_FavorTwoMe = cgmMeta.cgmAttr(mSettings,'result_sealTwoMe',attrType='float',
                                           defaultValue = 0,keyable = False,lock=True,
                                           hidden=False)
        mPlug_FavorTwoThee = cgmMeta.cgmAttr(mSettings,'result_sealTwoThee',attrType='float',
                                             defaultValue = 0,keyable = False,lock=True,
                                             hidden=False)    

        NODEFAC.createSingleBlendNetwork(mPlug_sealHeight.p_combinedName,
                                             mPlug_FavorOneThee.p_combinedName,
                                             mPlug_FavorOneMe.p_combinedName)
        NODEFAC.createSingleBlendNetwork(mPlug_sealHeight.p_combinedName,
                                             mPlug_FavorTwoThee.p_combinedName,
                                             mPlug_FavorTwoMe.p_combinedName)        


        d_dat[1]['mPlug_me'] = mPlug_FavorOneMe
        d_dat[1]['mPlug_thee'] = mPlug_FavorOneThee
        d_dat[2]['mPlug_me'] = mPlug_FavorTwoMe
        d_dat[2]['mPlug_thee'] = mPlug_FavorTwoThee


        """
        b_attachToInfluences = False
        if attachEndsToInfluences:
            log.debug("|{0}| >> attachEndsToInfluences flag. Checking...".format(_str_func))
            if influences and len(influences) > 1:
                b_attachToInfluences = True
            log.debug("|{0}| >> b_attachToInfluences: {1}".format(_str_func,b_attachToInfluences))
            """


        #>>> Skinning ============================================================================
        log.debug("|{0}| >> Skinning Ribbons...".format(_str_func))

        for idx,dat in d_dat.iteritems():
            max_influences = 2
            mode_tighten = 'twoBlend'
            blendLength = int(dat['int_driven']/2)
            blendMin = 2
            _hardLength = 2

            if extendEnds:
                blendMin = 4
                _hardLength = 4


            if dat['int_influences'] > 2:
                mode_tighten = None
                #blendLength = int(int_lenInfluences/2)
                max_influences = MATH.Clamp( blendLength, 2, 4)
                blendLength = MATH.Clamp( int(dat['int_influences']/2), 2, 6)

            if dat['int_influences'] == dat['int_driven']:
                _hardLength = 3
            #Tighten the weights...


            mSkinCluster = cgmMeta.validateObjArg(mc.skinCluster ([mObj.mNode for mObj in dat['mInfluences']],
                                                                  dat['mSurf'].mNode,
                                                                  tsb=True,nurbsSamples=4,
                                                                  maximumInfluences = 3,#max_influences,
                                                                  normalizeWeights = 1,dropoffRate=5.0),
                                                  'cgmNode',
                                                  setClass=True)

            mSkinCluster.doStore('cgmName', dat['mSurf'])
            mSkinCluster.doName()    

            #Tighten the weights...
            """
            RIGSKIN.surface_tightenEnds(dat['mSurf'].mNode,
                                        hardLength = _hardLength,
                                        blendLength=blendLength,
                                        mode=mode_tighten)"""        

        #>>> Meat ============================================================================
        ml_processed = []
        for idx,dat in d_dat.iteritems():
            idx_seal = 1
            if idx == 1:
                idx_seal = 2
            dat_seal = d_dat[idx_seal]
            log.debug("|{0}| >> Building [{1}] | seal idx: {2} |".format(_str_func,
                                                                         idx,
                                                                         idx_seal)+cgmGEN._str_subLine)

            mSurfBase = dat['mSurf']
            mSurfSeal = dat_seal['mSurf']

            for i,mObj in enumerate(dat['driven']):
                if mObj in ml_processed:
                    log.debug("|{0}| >> Already completed: {1}".format(_str_func,mObj))                    
                    continue
                ml_processed.append(mObj)
                log.debug("|{0}| >> {1} | Driven: {2}".format(_str_func,i,mObj))
                mDriven = md_drivers[mObj]
                log.debug("|{0}| >> {1} | Driver: {2}".format(_str_func,i,mDriven))

                log.debug("|{0}| >> Create track drivers...".format(_str_func))                
                mTrackBase = mDriven.doCreateAt(setClass=True)
                mTrackBase.doStore('cgmName',mObj)
                mTrackSeal = mTrackBase.doDuplicate()
                mTrackBlend = mTrackBase.doDuplicate()
                
                mObj.connectChildNode(mTrackBase.mNode,'mTrackBase','cgmSource')
                mObj.connectChildNode(mTrackSeal.mNode,'mTrackSeal','cgmSource')
                mObj.connectChildNode(mTrackBlend.mNode,'mTrackBlend','cgmSource')


                mTrackSeal.doStore('cgmType','trackSeal')
                mTrackBase.doStore('cgmType','trackBase')
                mTrackBlend.doStore('cgmType','trackBlend')
                ml_toParent.append(mTrackBlend)
                for mTrack in mTrackBase,mTrackSeal,mTrackBlend:
                    mTrack.doName()

                log.debug("|{0}| >> Attach drivers...".format(_str_func))

                d_tmp = {'base':{'mSurf':mSurfBase,
                                 'mTrack':mTrackBase},
                         'seal':{'mSurf':mSurfSeal,
                                 'mTrack':mTrackSeal},
                         }

                for n,d in d_tmp.iteritems():
                    mTrack = d['mTrack']
                    mSurf = d['mSurf']

                    _res = RIGCONSTRAINTS.attach_toShape(mTrack.mNode, mSurf.mNode, 'parent')
                    mFollicle = _res[-1]['mFollicle']#cgmMeta.asMeta(follicle)
                    mFollShape = _res[-1]['mFollicleShape']#cgmMeta.asMeta(shape)                    
                    #mFollicle = cgmMeta.asMeta(follicle)
                    #mFollShape = cgmMeta.asMeta(shape)

                    md_follicleShapes[mObj] = mFollShape
                    md_follicles[mObj] = mFollicle

                    mFollicle.parent = mGroup.mNode

                    if mModule:#if we have a module, connect vis
                        mFollicle.overrideEnabled = 1
                        cgmMeta.cgmAttr(mModule.rigNull.mNode,'gutsVis',lock=False).doConnectOut("%s.%s"%(mFollicle.mNode,'overrideVisibility'))
                        cgmMeta.cgmAttr(mModule.rigNull.mNode,'gutsLock',lock=False).doConnectOut("%s.%s"%(mFollicle.mNode,'overrideDisplayType'))

                #Blend point --------------------------------------------------------------------
                _const = mc.parentConstraint([mTrackBase.mNode,mTrackSeal.mNode],mTrackBlend.mNode)[0]
                ATTR.set(_const,'interpType',2)

                targetWeights = mc.parentConstraint(_const,q=True, weightAliasList=True)

                #Connect                                  
                if idx==1:
                    dat['mPlug_thee'].doConnectOut('%s.%s' % (_const,targetWeights[0]))
                    dat['mPlug_me'].doConnectOut('%s.%s' % (_const,targetWeights[1]))
                else:
                    dat['mPlug_me'].doConnectOut('%s.%s' % (_const,targetWeights[0]))
                    dat['mPlug_thee'].doConnectOut('%s.%s' % (_const,targetWeights[1]))                

                #seal --------------------------------------------------------------------
                _const = mc.parentConstraint([mTrackBase.mNode,mTrackBlend.mNode],mDriven.mNode)[0]
                ATTR.set(_const,'interpType',2)                

                targetWeights = mc.parentConstraint(_const,q=True, weightAliasList=True)

                if sealSplit:
                    dat['mPlugs']['off'][i].doConnectOut('%s.%s' % (_const,targetWeights[0]))
                    dat['mPlugs']['on'][i].doConnectOut('%s.%s' % (_const,targetWeights[1]))                    
                else:
                    dat['mPlug_sealOff'].doConnectOut('%s.%s' % (_const,targetWeights[0]))
                    dat['mPlug_sealOn'].doConnectOut('%s.%s' % (_const,targetWeights[1]))

            log.debug("|{0}| >> Blend drivers...".format(_str_func))


        
        if mModule:#if we have a module, connect vis
            mRigNull = mModule.rigNull
            _str_rigNull = mRigNull.mNode
            for mObj in ml_toConnect:
                mObj.overrideEnabled = 1
                cgmMeta.cgmAttr(_str_rigNull,'gutsVis',lock=False).doConnectOut("%s.%s"%(mObj.mNode,'overrideVisibility'))
                cgmMeta.cgmAttr(_str_rigNull,'gutsLock',lock=False).doConnectOut("%s.%s"%(mObj.mNode,'overrideDisplayType'))    
                mObj.p_parent = mRigNull    
        
        for mObj in ml_toParent:
            mObj.p_parent = mGroup.mNode
            

        #pprint.pprint(d_dat)
        return




    except Exception,err:
        cgmGEN.cgmExceptCB(Exception,err,msg=vars())