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
import cgm.core.rig.constraint_utils as RIGCONSTRAINTS
import cgm.core.rig.create_utils as RIGCREATE
import cgm.core.rig.general_utils as RIGGEN
import cgm.core.lib.list_utils as LISTS

import cgm.core.lib.math_utils as MATH

for m in CURVES,RIGCREATE,RIGGEN,LISTS,RIGCONSTRAINTS,MATH:
    reload(m)

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
    mModule = cgmMeta.validateObjArg(moduleInstance,noneValid = True)
    try:mModule.isModule()
    except:mModule = False

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
        mi_grp = cgmMeta.cgmObject(name = 'newgroup')
        mi_grp.addAttr('cgmName', str(str_baseName), lock=True)
        mi_grp.addAttr('cgmTypeModifier','segmentStuff', lock=True)
        mi_grp.doName()
    else:
        mi_grp = cgmMeta.validateObjArg(parentGutsTo,'cgmObject',False)

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

    #if mModule:#if we have a module, connect vis
        #mSegmentCurve.overrideEnabled = 1		
        #cgmMeta.cgmAttr(mi_rigNull.mNode,'gutsVis',lock=False).doConnectOut("%s.%s"%(mSegmentCurve.mNode,'overrideVisibility'))    
        #cgmMeta.cgmAttr(mi_rigNull.mNode,'gutsLock',lock=False).doConnectOut("%s.%s"%(mSegmentCurve.mNode,'overrideDisplayType'))    

    mIKSolver = cgmMeta.cgmNode(name = 'ikSplineSolver')
    
    #>> Handle/Effector --------------------------------------------------------------------------------------
    mIKHandle = cgmMeta.validateObjArg( buffer[0],'cgmObject',setClass=True )
    mIKHandle.addAttr('cgmName',str_baseName,attrType='string',lock=True)    		
    mIKHandle.doName()
    mIKHandle = mIKHandle

    mIKEffector = cgmMeta.validateObjArg( buffer[1],'cgmObject',setClass=True )
    mIKEffector.addAttr('cgmName',str_baseName,attrType='string',lock=True)  
    mIKEffector.doName()
    mIKHandle.parent = mi_grp
    
    mSegmentCurve.connectChildNode(mi_grp,'segmentGroup','owner')
    
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
            mi_closestPointNode.doStore('cgmName',mJnt.mNode)
            mi_closestPointNode.doName()
            #>Set follicle value
            mi_closestPointNode.parameter = param
            ml_pointOnCurveInfos.append(mi_closestPointNode)
            
        ml_distanceObjects = []
        ml_distanceShapes = []  
        mSegmentCurve.addAttr('masterScale',value = 1.0, minValue = 0.0001, attrType='float')
        
        for i,mJnt in enumerate(ml_joints[:-1]):
            #>> Distance nodes
            mi_distanceShape = cgmMeta.cgmNode( mc.createNode ('distanceDimShape') )        
            mi_distanceObject = mi_distanceShape.getTransform(asMeta=True) 
            mi_distanceObject.doStore('cgmName',mJnt.mNode)
            mi_distanceObject.addAttr('cgmType','measureNode',lock=True)
            mi_distanceObject.doName(nameShapes = True)
            mi_distanceObject.parent = mi_grp.mNode#parent it
            mi_distanceObject.overrideEnabled = 1
            mi_distanceObject.overrideVisibility = 1

            #Connect things
            ATTR.connect(ml_pointOnCurveInfos[i].mNode+'.position',mi_distanceShape.mNode+'.startPoint')
            ATTR.connect(ml_pointOnCurveInfos[i+1].mNode+'.position',mi_distanceShape.mNode+'.endPoint')

            ml_distanceObjects.append(mi_distanceObject)
            ml_distanceShapes.append(mi_distanceShape)

            if mModule:#Connect hides if we have a module instance:
                ATTR.connect("{0}.gutsVis".format(mModule.rigNull.mNode),"{0}.overrideVisibility".format(mi_distanceObject.mNode))
                ATTR.connect("{0}.gutsLock".format(mModule.rigNull.mNode),"{0}.overrideVisibility".format(overrideDisplayType.mNode))
                #cgmMeta.cgmAttr(mModule.rigNull.mNode,'gutsVis',lock=False).doConnectOut("%s.%s"%(mi_distanceObject.mNode,'overrideVisibility'))
                #cgmMeta.cgmAttr(mModule.rigNull.mNode,'gutsLock',lock=False).doConnectOut("%s.%s"%(mi_distanceObject.mNode,'overrideDisplayType'))    


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
                l_argBuild.append("{0} = {1} / {2}".format(mPlug_attrNormalBaseDist.p_combinedShortName,
                                                           '{0}.baseDist_{1}'.format(mIKHandle.mNode,i),
                                                           "{0}.masterScale".format(mSegmentCurve.mNode)))
                l_argBuild.append("{0} = {1} / {2}".format(mPlug_attrNormalDist.p_combinedShortName,
                                                           mPlug_attrDist.p_combinedShortName,
                                                           "{0}.masterScale".format(mSegmentCurve.mNode)))			
                for arg in l_argBuild:
                    log.debug("|{0}| >> Building arg: {1}".format(_str_func,arg))
                    NodeF.argsToNodes(arg).doBuild()
                    
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
                mi_mdNormalBaseDist.doStore('cgmName',mJnt.mNode)
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
                mi_mdNormalDist.doStore('cgmName',mJnt.mNode)
                mi_mdNormalDist.addAttr('cgmTypeModifier','normalizedDist')
                mi_mdNormalDist.doName()

                ATTR.connect('%s.masterScale'%(mSegmentCurve.mNode),#>>
                             '%s.%s'%(mi_mdNormalDist.mNode,'input1X'))
                mPlug_attrDist.doConnectOut('%s.%s'%(mi_mdNormalDist.mNode,'input2X'))	
                mPlug_attrNormalDist.doConnectIn('%s.%s'%(mi_mdNormalDist.mNode,'output.outputX'))

                #Create the mdNode
                mi_mdSegmentScale = cgmMeta.cgmNode(nodeType='multiplyDivide')
                mi_mdSegmentScale.operation = 2
                mi_mdSegmentScale.doStore('cgmName',mJnt.mNode)
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
    
    pprint.pprint(vars())

    mPlug_start = cgmMeta.cgmAttr(mi_crv.mNode,'twistStart',attrType='float',keyable=True, hidden=False)
    mPlug_end = cgmMeta.cgmAttr(mi_crv.mNode,'twistEnd',attrType='float',keyable=True, hidden=False)
    d_return = {"mPlug_start":mPlug_start,"mPlug_end":mPlug_end}    
    
    if not advancedTwistSetup:
        mPlug_twist = cgmMeta.cgmAttr(mIKHandle.mNode,'twist',attrType='float',keyable=True, hidden=False)
    else:
        mi_ramp = cgmMeta.cgmNode(nodeType= 'ramp')
        mi_ramp.doStore('cgmName',mIKHandle.mNode)
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
        
        arg1 = "{0} = {1} - {2}".format(mPlug_midDiff.p_combinedShortName,
                                        mPlug_end.p_combinedShortName,
                                        mPlug_start.p_combinedShortName)    
        arg2 = "{0} = {1} / 2".format(mPlug_midDiv.p_combinedShortName,
                                      mPlug_midDiff.p_combinedShortName)
        arg3 = "{0} = {1} + {2}".format(mPlug_midResult.p_combinedShortName,
                                        mPlug_midDiv.p_combinedShortName,
                                        mPlug_mid.p_combinedShortName)
        
        for a in arg1,arg2,arg3:
            NodeF.argsToNodes(a).doBuild()
        
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
        
        arg1 = "{0} = {1}".format(mPlug_midSum.p_combinedShortName,
                                  ' + '.join(["{0}.r{1}".format(mJnt.p_nameShort,orientation[0]) for mJnt in ml_joints]))
        log.debug(arg1)
        arg2 = "{0} = {1} - {2}".format(mPlug_midTwist.p_combinedShortName,
                                        mPlug_end.p_combinedShortName,
                                        mPlug_midSum.p_combinedShortName)
        for a in arg1,arg2:
            NodeF.argsToNodes(a).doBuild()
        
        """arg1 = "{0}.twist = if {1} > {2}: {3} else {4}".format(mMidHandle.p_nameShort,
                                                               mPlug_start.p_combinedName,
                                                               mPlug_end.p_combinedName,                                                               
                                                               mPlug_endMidDiffResult.p_combinedShortName,
                                                               mPlug_endMidDiffNegResult.p_combinedShortName)"""        
        
        #Second roll...
        
        
        """
        arg1 = "{0}.twist = {1} - {2}".format(mMidHandle.p_nameShort,
                                              mPlug_end.p_combinedShortName,
                                              mPlug_midNegResult.p_combinedShortName)
        """
        
        
    else:
        mPlug_start.doConnectOut("%s.roll"%mIKHandle.mNode)
        #ikHandle1.twist = (ikHandle1.roll *-.77) + curve4.twistEnd # to implement
        arg1 = "{0} = {1} - {2}".format(mPlug_twist.p_combinedShortName,
                                        mPlug_end.p_combinedShortName,
                                        mPlug_start.p_combinedShortName)
        NodeF.argsToNodes(arg1).doBuild()
        
        
    
    if advancedTwistSetup:
        mc.select(mi_ramp.mNode)
        for c in mc.ls("%s.colorEntryList[*]"%mi_ramp.mNode,flatten = True):
            log.debug( mc.removeMultiInstance( c, b = True) )
        mc.setAttr("%s.colorEntryList[0].color"%mi_ramp.mNode,0, 0, 0)
        mc.setAttr("%s.colorEntryList[1].color"%mi_ramp.mNode,1, 1, 1)
        mc.setAttr("%s.colorEntryList[1].position"%mi_ramp.mNode,1)

        mPlug_existingTwistType = cgmMeta.cgmAttr(mi_ramp,'interpolation')
        mPlug_twistType = cgmMeta.cgmAttr(mi_crv,'twistType', attrType = 'enum', enum = ":".join(mPlug_existingTwistType.p_enum))
        mPlug_twistType.doConnectOut(mPlug_existingTwistType.p_combinedShortName)	
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
        mi_ramp.doStore('cgmName',mIKHandle.mNode)
        mi_ramp.doName()

        #Fix Ramp
        ATTR.connect("%s.outColor"%mi_ramp.mNode,"%s.dTwistRamp"%mIKHandle.mNode)
        d_return['mi_ramp'] = mi_ramp

    mPlug_start.doConnectOut("%s.roll"%mIKHandle.mNode)
    d_return['mi_plug_twist']=mPlug_twist
    #ikHandle1.twist = (ikHandle1.roll *-.77) + curve4.twistEnd # to implement
    arg1 = "%s = %s - %s"%(mPlug_twist.p_combinedShortName,mPlug_end.p_combinedShortName,mPlug_start.p_combinedShortName)
    log.debug("arg1: '%s'"%arg1)    
    log.debug( NodeF.argsToNodes(arg1).doBuild() )       

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
        mPlug_twistType.doConnectOut(mPlug_existingTwistType.p_combinedShortName)	
    else:
        mPlug_existingTwistType = cgmMeta.cgmAttr(mIKHandle,'twistType')
        mPlug_twistType = cgmMeta.cgmAttr(mi_crv,'twistType', attrType = 'enum', enum = ":".join(mPlug_existingTwistType.p_enum))
        mPlug_twistType.twistType = 'linear'	
        mPlug_twistType.doConnectOut(mPlug_existingTwistType.p_combinedShortName)	
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
            NodeF.connectNegativeAttrs(ml_fkJoints[i].mNode, mJoint.mNode,
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

    NodeF.createSingleBlendNetwork(mPlug_FKIK.p_combinedName,
                                   mPlug_IKon.p_combinedName,
                                   mPlug_FKon.p_combinedName)

    mPlug_FKon.doConnectOut("%s.visibility"%fkGroup)
    mPlug_IKon.doConnectOut("%s.visibility"%ikGroup)	


    pprint.pprint(vars())
    return True


def ribbon_createSurface(jointList=[], outAxis = 'x'):
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
        mAxis_out = VALID.simpleAxis(outAxis)
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
            
        _res_body = mc.loft(l_crvs, reverseSurfaceNormals = True, ch = False, uniform = True, degree = 3)

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
    except Exception,err:cgmGEN.cgmException(Exception,err)
    
def ribbon(jointList = None,
           useSurface = None,
           orientation = 'zyx',
           secondaryAxis = 'y+',
           baseName = None,
           connectBy = 'constraint',
           stretchBy = 'translate',
           msgDriver = None,#...msgLink on joint to a driver group for constaint purposes
           #advancedTwistSetup = False,
           #extendTwistToEnd = False,
           #reorient = False,
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
    try:
        _str_func = 'ribbon'
        ml_rigObjectsToConnect = []
        ml_rigObjectsToParent = []
        
        #try:
        #>>> Verify =============================================================================================
        ml_joints = cgmMeta.validateObjListArg(jointList,mType = 'cgmObject', mayaType=['joint'], noneValid = False)
        l_joints = [mJnt.p_nameShort for mJnt in ml_joints]
        int_lenJoints = len(ml_joints)#because it's called repeatedly
        mi_useSurface = cgmMeta.validateObjArg(useSurface,mayaType=['nurbsSurface'],noneValid = True)
    
        mi_mayaOrientation = VALID.simpleOrientation(orientation)
        str_orientation = mi_mayaOrientation.p_string
        str_secondaryAxis = VALID.stringArg(secondaryAxis,noneValid=True)
        str_baseName = VALID.stringArg(baseName,noneValid=True)
        
        
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
        
        str_stretchBy = VALID.stringArg(stretchBy,noneValid=True)		
        #b_advancedTwistSetup = VALID.boolArg(advancedTwistSetup)
        #b_extendTwistToEnd= VALID.boolArg(extendTwistToEnd)
    
        if int_lenJoints<3:
            pprint.pprint(vars())
            raise ValueError,"needs at least three joints"
        
        if parentGutsTo is None:
            mi_grp = cgmMeta.cgmObject(name = 'newgroup')
            mi_grp.addAttr('cgmName', str(str_baseName), lock=True)
            mi_grp.addAttr('cgmTypeModifier','segmentStuff', lock=True)
            mi_grp.doName()
        else:
            mi_grp = cgmMeta.validateObjArg(parentGutsTo,'cgmObject',False)
        if mModule:
            mi_grp.parent = mModule.rigNull
    
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
        
        
        #>>> Ribbon Surface ===========================================================================================        
        if mi_useSurface:
            raise NotImplementedError,'Not done with passed surface'
        else:
            log.debug("|{0}| >> Creating surface...".format(_str_func))
            l_surfaceReturn = ribbon_createSurface(jointList,outChannel)
        
            mControlSurface = cgmMeta.validateObjArg( l_surfaceReturn[0],'cgmObject',setClass = True )
            mControlSurface.addAttr('cgmName',str(baseName),attrType='string',lock=True)    
            mControlSurface.addAttr('cgmType','controlSurface',attrType='string',lock=True)
            mControlSurface.doName()
        
        if mModule:#if we have a module, connect vis
            mControlSurface.overrideEnabled = 1		
            cgmMeta.cgmAttr(mModule.rigNull.mNode,'gutsVis',lock=False).doConnectOut("%s.%s"%(mControlSurface.mNode,'overrideVisibility'))
            cgmMeta.cgmAttr(mModule.rigNull.mNode,'gutsLock',lock=False).doConnectOut("%s.%s"%(mControlSurface.mNode,'overrideDisplayType'))    
            mControlSurface.parent = mModule.rigNull
        #>>> Follicles ===========================================================================================        
        ml_follicleTransforms = []
        ml_follicleShapes = []
        ml_upGroups = []
        
        import cgm.core.lib.node_utils as NODES
        
        for i,mJnt in enumerate(ml_joints):
            if msgDriver:
                mDriven = mJnt.getMessage(msgDriver,asMeta=True)
                if not mDriven:
                    raise ValueError,"Missing msgDriver: {0} | {1}".format(msgDriver,mJnt)
                mDriven = mDriven[0]
            else:
                mDriven = mJnt
                
            follicle,shape = RIGCONSTRAINTS.attach_toShape(mJnt.mNode, mControlSurface.mNode, None)
            mFollicle = cgmMeta.asMeta(follicle)
            mFollShape = cgmMeta.asMeta(shape)
            
            

            ml_follicleShapes.append(mFollicle)
            ml_follicleTransforms.append(mFollShape)
    
            mFollicle.parent = mi_grp.mNode
    
            if mModule:#if we have a module, connect vis
                mFollicle.overrideEnabled = 1
                cgmMeta.cgmAttr(mModule.rigNull.mNode,'gutsVis',lock=False).doConnectOut("%s.%s"%(mFollicle.mNode,'overrideVisibility'))
                cgmMeta.cgmAttr(mModule.rigNull.mNode,'gutsLock',lock=False).doConnectOut("%s.%s"%(mFollicle.mNode,'overrideDisplayType'))    
            
            #Simple contrain
            mc.parentConstraint([mFollicle.mNode], mDriven.mNode, maintainOffset=True)
            

            
            
            """
            if mJnt != ml_joints[-1]:
                mUpLoc = mJnt.doLoc()#Make up Loc
                mLocRotateGroup = mJnt.doCreateAt()#group in place
                mLocRotateGroup.parent = i_follicleTrans.mNode
                mLocRotateGroup.doStore('cgmName',mJnt.mNode)	    
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
    
        #>>> Connect our iModule vis stuff
        if mModule:#if we have a module, connect vis
            for mObj in ml_rigObjectsToConnect:
                mObj.overrideEnabled = 1		
                cgmMeta.cgmAttr(mModule.rigNull.mNode,'gutsVis',lock=False).doConnectOut("%s.%s"%(mObj.mNode,'overrideVisibility'))
                cgmMeta.cgmAttr(mModule.rigNull.mNode,'gutsLock',lock=False).doConnectOut("%s.%s"%(mObj.mNode,'overrideDisplayType'))    
            for mObj in ml_rigObjectsToParent:
                mObj.parent = mModule.rigNull.mNode

                
        return mControlSurface
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
    
        #if mModule:#if we have a module, connect vis
            #mSegmentCurve.overrideEnabled = 1		
            #cgmMeta.cgmAttr(mi_rigNull.mNode,'gutsVis',lock=False).doConnectOut("%s.%s"%(mSegmentCurve.mNode,'overrideVisibility'))    
            #cgmMeta.cgmAttr(mi_rigNull.mNode,'gutsLock',lock=False).doConnectOut("%s.%s"%(mSegmentCurve.mNode,'overrideDisplayType'))    
    
        mIKSolver = cgmMeta.cgmNode(name = 'ikSplineSolver')
        
        #>> Handle/Effector --------------------------------------------------------------------------------------
        mIKHandle = cgmMeta.validateObjArg( buffer[0],'cgmObject',setClass=True )
        mIKHandle.addAttr('cgmName',str_baseName,attrType='string',lock=True)    		
        mIKHandle.doName()
        mIKHandle = mIKHandle
    
        mIKEffector = cgmMeta.validateObjArg( buffer[1],'cgmObject',setClass=True )
        mIKEffector.addAttr('cgmName',str_baseName,attrType='string',lock=True)  
        mIKEffector.doName()
        mIKHandle.parent = mi_grp
        
        mSegmentCurve.connectChildNode(mi_grp,'segmentGroup','owner')
        
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
                mi_closestPointNode.doStore('cgmName',mJnt.mNode)
                mi_closestPointNode.doName()
                #>Set follicle value
                mi_closestPointNode.parameter = param
                ml_pointOnCurveInfos.append(mi_closestPointNode)
                
            ml_distanceObjects = []
            ml_distanceShapes = []  
            mSegmentCurve.addAttr('masterScale',value = 1.0, minValue = 0.0001, attrType='float')
            
            for i,mJnt in enumerate(ml_joints[:-1]):
                #>> Distance nodes
                mi_distanceShape = cgmMeta.cgmNode( mc.createNode ('distanceDimShape') )        
                mi_distanceObject = mi_distanceShape.getTransform(asMeta=True) 
                mi_distanceObject.doStore('cgmName',mJnt.mNode)
                mi_distanceObject.addAttr('cgmType','measureNode',lock=True)
                mi_distanceObject.doName(nameShapes = True)
                mi_distanceObject.parent = mi_grp.mNode#parent it
                mi_distanceObject.overrideEnabled = 1
                mi_distanceObject.overrideVisibility = 1
    
                #Connect things
                ATTR.connect(ml_pointOnCurveInfos[i].mNode+'.position',mi_distanceShape.mNode+'.startPoint')
                ATTR.connect(ml_pointOnCurveInfos[i+1].mNode+'.position',mi_distanceShape.mNode+'.endPoint')
    
                ml_distanceObjects.append(mi_distanceObject)
                ml_distanceShapes.append(mi_distanceShape)
    
                if mModule:#Connect hides if we have a module instance:
                    ATTR.connect("{0}.gutsVis".format(mModule.rigNull.mNode),"{0}.overrideVisibility".format(mi_distanceObject.mNode))
                    ATTR.connect("{0}.gutsLock".format(mModule.rigNull.mNode),"{0}.overrideVisibility".format(overrideDisplayType.mNode))
                    #cgmMeta.cgmAttr(mModule.rigNull.mNode,'gutsVis',lock=False).doConnectOut("%s.%s"%(mi_distanceObject.mNode,'overrideVisibility'))
                    #cgmMeta.cgmAttr(mModule.rigNull.mNode,'gutsLock',lock=False).doConnectOut("%s.%s"%(mi_distanceObject.mNode,'overrideDisplayType'))    
    
    
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
                    l_argBuild.append("{0} = {1} / {2}".format(mPlug_attrNormalBaseDist.p_combinedShortName,
                                                               '{0}.baseDist_{1}'.format(mIKHandle.mNode,i),
                                                               "{0}.masterScale".format(mSegmentCurve.mNode)))
                    l_argBuild.append("{0} = {1} / {2}".format(mPlug_attrNormalDist.p_combinedShortName,
                                                               mPlug_attrDist.p_combinedShortName,
                                                               "{0}.masterScale".format(mSegmentCurve.mNode)))			
                    for arg in l_argBuild:
                        log.debug("|{0}| >> Building arg: {1}".format(_str_func,arg))
                        NodeF.argsToNodes(arg).doBuild()
                        
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
                    mi_mdNormalBaseDist.doStore('cgmName',mJnt.mNode)
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
                    mi_mdNormalDist.doStore('cgmName',mJnt.mNode)
                    mi_mdNormalDist.addAttr('cgmTypeModifier','normalizedDist')
                    mi_mdNormalDist.doName()
    
                    ATTR.connect('%s.masterScale'%(mSegmentCurve.mNode),#>>
                                 '%s.%s'%(mi_mdNormalDist.mNode,'input1X'))
                    mPlug_attrDist.doConnectOut('%s.%s'%(mi_mdNormalDist.mNode,'input2X'))	
                    mPlug_attrNormalDist.doConnectIn('%s.%s'%(mi_mdNormalDist.mNode,'output.outputX'))
    
                    #Create the mdNode
                    mi_mdSegmentScale = cgmMeta.cgmNode(nodeType='multiplyDivide')
                    mi_mdSegmentScale.operation = 2
                    mi_mdSegmentScale.doStore('cgmName',mJnt.mNode)
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
        return _res
    
    
        #import pprint
        pprint.pprint(vars())
        #pprint.pformat(vars)
        return
    except Exception,err:cgmGEN.cgmException(Exception,err)


def handleHOLDER(jointList = None,
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
    mModule = cgmMeta.validateObjArg(moduleInstance,noneValid = True)
    try:mModule.isModule()
    except:mModule = False

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
        mi_grp = cgmMeta.cgmObject(name = 'newgroup')
        mi_grp.addAttr('cgmName', str(str_baseName), lock=True)
        mi_grp.addAttr('cgmTypeModifier','segmentStuff', lock=True)
        mi_grp.doName()
    else:
        mi_grp = cgmMeta.validateObjArg(parentGutsTo,'cgmObject',False)

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
        if not str_baseName:str_baseName = 'testIK'     
    
        #Joint chain ======================================================================================
        mStart = cgmMeta.validateObjArg(startJoint,'cgmObject',noneValid=False)
        mEnd = cgmMeta.validateObjArg(endJoint,'cgmObject',noneValid=False)
        if not mEnd.isChildOf(mStart):
            raise ValueError,"|{0}| >> {1} not a child of {2}".format(_str_func,endJoint,startJoint)
            
        
        ml_jointChain = mStart.getListPathTo(mEnd,asMeta=True)
        #ml_jointChain = cgmMeta.validateObjListArg(l_jointChain,'cgmObject',noneValid=False)
        l_jointChain = [mObj.mNode for mObj in ml_jointChain]
        if len(ml_jointChain)<3:
            raise ValueError,"|{0}| >> {1} len less than 3 joints.".format(_str_func,len(ml_jointChain))
            
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
        #v_localAim = distance.returnLocalAimDirection(ml_jointChain[0].mNode,ml_jointChain[1].mNode)
        #str_localAim = dictionary.returnVectorToString(v_localAim)
        #str_localAimSingle = str_localAim[0]
        str_localAimSingle = orientation[0]
        #log.debug("create_IKHandle>>> vector aim: %s | str aim: %s"%(v_localAim,str_localAim))
    
    

        #Create IK handle ==================================================================================
        buffer = mc.ikHandle( sj=mStart.mNode, ee=mEnd.mNode,
                              solver = solverType, forceSolver = True,
                              snapHandleFlagToggle=True )  	
    
    
        #>>> Name
        log.debug(buffer)
        mIKHandle = cgmMeta.asMeta(buffer[0],'cgmObject',setClass=True)
        mIKHandle.addAttr('cgmName',str_baseName,attrType='string',lock=True)
        #mIKHandle.doStore('cgmType','IKHand')
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
            
            mPlug_autoStretch = cgmMeta.cgmAttr(mControl,'autoStretch',initialValue = 1, defaultValue = 1, keyable = True, attrType = 'float', minValue = 0, maxValue = 1)
            
            if len(ml_jointChain) == 3 and lockMid:
                log.debug("|{0}| >> MidLock setup possible...".format(_str_func))
                
            
                if lockMid:mPlug_lockMid = cgmMeta.cgmAttr(mControl,'lockMid',initialValue = 0, attrType = 'float', keyable = True, minValue = 0, maxValue = 1)
        
        
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
            mPlug_globalScale = cgmMeta.cgmAttr(mIKHandle.mNode,'masterScale',value = 1.0, lock =True, hidden = True)
    
    
            md_baseDistReturn = RIGCREATE.distanceMeasure(ml_handles[0].mNode,ml_handles[-1].mNode,baseName=str_baseName)
            
            md_baseDistReturn['mEnd'].p_parent = mControl
            
            ml_rigObjectsToParent.append(md_baseDistReturn['mDag'])
            mPlug_baseDist = cgmMeta.cgmAttr(mIKHandle.mNode,'ikDistBase' , attrType = 'float', value = md_baseDistReturn['mShape'].distance , lock =True , hidden = True)	
            mPlug_baseDistRaw = cgmMeta.cgmAttr(mIKHandle.mNode,'ikDistRaw' , value = 1.0 , lock =True , hidden = True)
            mPlug_baseDistRaw.doConnectIn("%s.distance"%md_baseDistReturn['mShape'].mNode)
            mPlug_baseDistNormal = cgmMeta.cgmAttr(mIKHandle.mNode,'result_ikBaseNormal',value = 1.0, lock =True, hidden = True)
            mPlug_ikDistNormal = cgmMeta.cgmAttr(mIKHandle.mNode,'result_ikDistNormal',value = 1.0, lock =True, hidden = True)	
            mPlug_ikScale = cgmMeta.cgmAttr(mIKHandle.mNode,'result_ikScale',value = 1.0, lock =True, hidden = True)
            mPlug_ikClampScale = cgmMeta.cgmAttr(mIKHandle.mNode,'result_ikClampScale',value = 1.0, lock =True, hidden = True)
            mPlug_ikClampMax = cgmMeta.cgmAttr(mIKHandle.mNode,'result_ikClampMax',value = 1.0, lock =True, hidden = True)
    
            #Normal base
            arg = "%s = %s * %s"%(mPlug_baseDistNormal.p_combinedShortName,
                                  mPlug_baseDist.p_combinedShortName,
                                  mPlug_globalScale.p_combinedShortName)
            NodeF.argsToNodes(arg).doBuild()
    
            #Normal Length
            arg = "%s = %s / %s"%(mPlug_ikDistNormal.p_combinedShortName,
                                  mPlug_baseDistRaw.p_combinedShortName,
                                  mPlug_globalScale.p_combinedShortName)
            NodeF.argsToNodes(arg).doBuild()	
    
            #ik scale
            arg = "%s = %s / %s"%(mPlug_ikScale.p_combinedShortName,
                                  mPlug_baseDistRaw.p_combinedShortName,
                                  mPlug_baseDistNormal.p_combinedShortName)
            NodeF.argsToNodes(arg).doBuild()	
    
            #ik max clamp
            """ This is for maya 2013 (at least) which honors the max over the  min """
            arg = "%s = if %s >= 1: %s else 1"%(mPlug_ikClampMax.p_combinedShortName,
                                                mPlug_ikScale.p_combinedShortName,
                                                mPlug_ikScale.p_combinedShortName)
            NodeF.argsToNodes(arg).doBuild()
    
            #ik clamp scale
            arg = "%s = clamp(1,%s,%s)"%(mPlug_ikClampScale.p_combinedShortName,
                                         mPlug_ikClampMax.p_combinedShortName,
                                         mPlug_ikScale.p_combinedShortName)
            NodeF.argsToNodes(arg).doBuild()	
    
            #Create our blend to stretch or not - blend normal base and stretch base
            mi_stretchBlend = cgmMeta.cgmNode(nodeType= 'blendTwoAttr')
            mi_stretchBlend.addAttr('cgmName','%s_stretchBlend'%(baseName),lock=True)
            mi_stretchBlend.doName()
            ATTR.set(mi_stretchBlend.mNode,"input[0]",1)
            mPlug_ikClampScale.doConnectOut("%s.input[1]"%mi_stretchBlend.mNode)
            mPlug_autoStretch.doConnectOut("%s.attributesBlender"%mi_stretchBlend.mNode)
    
            
            #Make our distance objects per segment
            #=========================================================================
            l_segments = LISTS.get_listPairs(ml_handles)
            for i,seg in enumerate(l_segments):#Make our measure nodes
                buffer =  RIGCREATE.distanceMeasure(seg[0].mNode,seg[-1].mNode,baseName="{0}_{1}".format(str_baseName,i))
                ml_distanceShapes.append(buffer['mShape'])
                ml_distanceObjects.append(buffer['mDag'])
                #>>>TODO Add hide stuff
            ml_rigObjectsToParent.extend(ml_distanceObjects)
            ml_rigObjectsToConnect.extend(ml_handles)
            
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
                arg = "%s = %s * %s"%(mPlug_normalBaseDist.p_combinedShortName,
                                      mPlug_baseDist.p_combinedName,
                                      mPlug_globalScale.p_combinedShortName)
                NodeF.argsToNodes(arg).doBuild()
    
                #Normal distance
                arg = "%s = %s / %s"%(mPlug_normalDist.p_combinedShortName,
                                      mPlug_rawDist.p_combinedName,
                                      mPlug_globalScale.p_combinedShortName)
                NodeF.argsToNodes(arg).doBuild()
    
                #Stretch Distance
                arg = "%s = %s * %s.output"%(mPlug_stretchDist.p_combinedShortName,
                                             mPlug_normalBaseDist.p_combinedName,
                                             mi_stretchBlend.getShortName())
                NodeF.argsToNodes(arg).doBuild()
    
                #Then pull the global out of the stretchdistance 
                arg = "%s = %s / %s"%(mPlug_stretchNormalDist.p_combinedShortName,
                                      mPlug_stretchDist.p_combinedName,
                                      mPlug_globalScale.p_combinedName)
                NodeF.argsToNodes(arg).doBuild()	    
    
                #Segment scale
                arg = "%s = %s / %s"%(mPlug_resultSegmentScale.p_combinedShortName,
                                      mPlug_normalDist.p_combinedName,
                                      mPlug_baseDist.p_combinedShortName)
                NodeF.argsToNodes(arg).doBuild()
    
                #Create our blend to stretch or not - blend normal base and stretch base
                mi_blend = cgmMeta.cgmNode(nodeType= 'blendTwoAttr')
                mi_blend.addAttr('cgmName','%s_stretch_to_lockMid'%(i_jnt.getBaseName()),lock=True)
                mi_blend.doName()
                if lockMid:
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
        if lockMid:
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
    except Exception,err:cgmGEN.cgmException(Exception,err)



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
        log.debug("|{0}| >> drivenAttr='{1}',driverAttr='{2}.twist',minIn = -180, maxIn = 180, maxIterations = 75,matchValue=0.0001".format(_str_func,mPlug_rot.p_combinedShortName,mIKHandle.p_nameShort))        
        
        RIGGEN.matchValue_iterator(drivenAttr="%s.r%s"%(mStartJoint.mNode,aimAxis),
                                   driverAttr="%s.twist"%mIKHandle.mNode,
                                   minIn = -170, maxIn = 180,
                                   maxIterations = 30,
                                   matchValue=0)
        log.debug("|{0}| >> drivenAttr='{1}',driverAttr='{2}.twist',minIn = -180, maxIn = 180, maxIterations = 75,matchValue=0.0001".format(_str_func,mPlug_rot.p_combinedShortName,mIKHandle.p_nameShort))        
        
        #log.debug("rUtils.matchValue_iterator(drivenAttr='%s.r%s',driverAttr='%s.twist',minIn = -180, maxIn = 180, maxIterations = 75,matchValue=0.0001)"%(mStartJoint.getShortName(),str_localAimSingle,mIKHandle.getShortName()))
    return True