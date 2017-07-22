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
from cgm.core.classes import NodeFactory as NodeF
import cgm.core.rig.joint_utils as JOINTS
import cgm.core.lib.attribute_utils as ATTR

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
    mi_module = cgmMeta.validateObjArg(moduleInstance,noneValid = True)
    try:mi_module.isModule()
    except:mi_module = False

    mi_rigNull = False	
    if mi_module:
        log.debug("|{0}| >> Module found. mi_module: {1}...".format(_str_func,mi_module))                                    
        mi_rigNull = mi_module.rigNull	
        if str_baseName is None:
            str_baseName = mi_module.getPartNameBase()#Get part base name	    
    if not str_baseName:str_baseName = 'testSplineIK' 
    #...
    
    str_stretchBy = VALID.stringArg(stretchBy,noneValid=True)		
    b_advancedTwistSetup = VALID.boolArg(advancedTwistSetup)
    b_extendTwistToEnd= VALID.boolArg(extendTwistToEnd)

    if int_lenJoints<3:
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
            
    #>>> SplineIK ===========================================================================================
    if mi_useCurve:
        log.debug("|{0}| >> useCurve. SplineIk...".format(_str_func))    
        f_MatchPosOffset = CURVES.getUParamOnCurve(ml_joints[0].mNode, mi_useCurve.mNode)
        log.debug("|{0}| >> Use curve mode. uPos: {1}...".format(_str_func,f_MatchPosOffset))                            
        
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

    #if mi_module:#if we have a module, connect vis
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
            param = CURVES.getUParamOnCurve(mJnt.mNode, mSegmentCurve.mNode)
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

            if mi_module:#Connect hides if we have a module instance:
                ATTR.connect("{0}.gutsVis".format(mi_module.rigNull.mNode),"{0}.overrideVisibility".format(mi_distanceObject.mNode))
                ATTR.connect("{0}.gutsLock".format(mi_module.rigNull.mNode),"{0}.overrideVisibility".format(overrideDisplayType.mNode))
                #cgmMeta.cgmAttr(mi_module.rigNull.mNode,'gutsVis',lock=False).doConnectOut("%s.%s"%(mi_distanceObject.mNode,'overrideVisibility'))
                #cgmMeta.cgmAttr(mi_module.rigNull.mNode,'gutsLock',lock=False).doConnectOut("%s.%s"%(mi_distanceObject.mNode,'overrideDisplayType'))    


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
    #d_twistReturn = rig_Utils.IKHandle_addSplineIKTwist(mIKHandle.mNode,b_advancedTwistSetup)
    #mPlug_twistStart = d_twistReturn['mi_plug_start']
    #mPlug_twistEnd = d_twistReturn['mi_plug_end']
    #_res['mPlug_twistStart'] = mPlug_twistStart
    #_res['mPlug_twistEnd'] = mPlug_twistEnd
    return _res


    #import pprint
    pprint.pprint(vars())
    #pprint.pformat(vars)
    return


def addSplineTwist(ikHandle = None, midHandle = None, advancedTwistSetup = False, orientation = 'zyx'):
    """
    ikHandle(arg)
    advancedTwistSetup(bool) -- Whether to setup ramp setup or not (False)
    """
    _str_func = 'addSplineTwist'
    
    #>>> Data gather and arg check
    mIKHandle = cgmMeta.validateObjArg(ikHandle,'cgmObject',noneValid=False)
    mi_midHandle = cgmMeta.validateObjArg(midHandle,'cgmObject',noneValid=True)
    
    if mIKHandle.getMayaType() != 'ikHandle':
        raise ValueError,("|{0}| >> Not an ikHandle ({2}). Type: {1}".format(_str_func, mIKHandle.getMayaType(), mIKHandle.p_nameShort))                                                    
    if mi_midHandle and mi_midHandle.getMayaType() != 'ikHandle':
        raise ValueError,("|{0}| >> Mid ({2}) not an ikHandle. Type: {1}".format(_str_func, mi_midHandle.getMayaType(),mi_midHandle.p_nameShort))                                                    

    ml_handles = [mIKHandle]
    if mi_midHandle:
        ml_handles.append(mi_midHandle)
        
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
        mPlug_midSum.doConnectOut("{0}.roll".format(mi_midHandle.p_nameShort))
        mPlug_midTwist.doConnectOut("{0}.twist".format(mi_midHandle.p_nameShort))
        
        arg1 = "{0} = {1}".format(mPlug_midSum.p_combinedShortName,
                                  ' + '.join(["{0}.r{1}".format(mJnt.p_nameShort,orientation[0]) for mJnt in ml_joints]))
        log.debug(arg1)
        arg2 = "{0} = {1} - {2}".format(mPlug_midTwist.p_combinedShortName,
                                        mPlug_end.p_combinedShortName,
                                        mPlug_midSum.p_combinedShortName)
        for a in arg1,arg2:
            NodeF.argsToNodes(a).doBuild()
        
        """arg1 = "{0}.twist = if {1} > {2}: {3} else {4}".format(mi_midHandle.p_nameShort,
                                                               mPlug_start.p_combinedName,
                                                               mPlug_end.p_combinedName,                                                               
                                                               mPlug_endMidDiffResult.p_combinedShortName,
                                                               mPlug_endMidDiffNegResult.p_combinedShortName)"""        
        
        #Second roll...
        
        
        """
        arg1 = "{0}.twist = {1} - {2}".format(mi_midHandle.p_nameShort,
                                              mPlug_end.p_combinedShortName,
                                              mPlug_midNegResult.p_combinedShortName)
        """
        
        
    else:
        mPlug_start.doConnectOut("%s.roll"%mIKHandle.mNode)
        #ikHandle1.twist = (ikHandle1.roll *-.77) + curve4.twistEnd # to implement
        arg1 = "{0} = {1} - {2}".format(mlPlugs_twist[0].p_combinedShortName,
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
