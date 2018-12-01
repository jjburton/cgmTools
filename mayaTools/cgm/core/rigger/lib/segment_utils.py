"""
------------------------------------------
segment_utils: cgm.core.rigger.lib
Author: Josh Burton
email: jjburton@cgmonks.com
Website : http://www.cgmonks.com
------------------------------------------

Part of a segment rewrite began November 2016 from rig_Utils
================================================================
"""
# From Python =============================================================
import copy
import re
import time
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

# From Maya =============================================================
import maya.cmds as mc

# From cgm ==============================================================
from cgm.core import cgm_Meta as cgmMeta
from cgm.core import cgm_General as cgmGeneral
from cgm.core.lib import curve_Utils as crvUtils
from cgm.core.cgmPy import validateArgs as cgmValid
from cgm.core.classes import SnapFactory as Snap
from cgm.core.lib import nameTools
from cgm.core.rigger.lib import rig_Utils
from cgm.core.classes import NodeFactory as NodeF
from cgm.lib import (distance,
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
                     cgmMath)


def create_segment_curve(*args,**kws):
    class fncWrap(cgmGeneral.cgmFuncCls):
        """
        Root of the segment setup.
        Inspiriation from Jason Schleifer's work as well as http://faithofthefallen.wordpress.com/2008/10/08/awesome-spine-setup/
        on twist methods.

        :parameters:
            0 - 'jointList'(joints - None) | List or metalist of joints
            1 - 'useCurve'(nurbsCurve - None) | Which curve to use. If None. One Created
            2 - 'orientation'(string - zyx) | What is the joints orientation
            3 - 'secondaryAxis'(maya axis arg(ex:'yup') - yup) | Only necessary when no module provide for orientating
            4 - 'baseName'(string - None) | baseName string
            5 - 'connectBy'(string - trans) | How the joint will scale
            6 - 'advancedTwistSetup'(bool - False) | Whether to do the cgm advnaced twist setup
            7 - 'addMidTwist'(bool - True) | Whether to setup a mid twist on the segment
            8 - 'moduleInstance'(cgmModule - None) | cgmModule to use for connecting on build
            9 - 'extendTwistToEnd'(bool - False) | Whether to extned the twist to the end by default

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
        def __init__(self,*args,**kws):
            """
            """
            super(fncWrap, self).__init__(*args, **kws)
            self._str_funcName= "create_segment_curve"
            self._b_reportTimes = True
            self._b_autoProgressBar = 1
            self._l_ARGS_KWS_DEFAULTS = [{'kw':'jointList',"default":None,'help':"List or metalist of joints","argType":"joints"},
                                         {'kw':'useCurve',"default":None,'help':"Which curve to use. If None. One Created","argType":"nurbsCurve"},
                                         {'kw':'orientation',"default":'zyx','help':"What is the joints orientation","argType":"string"},
                                         {'kw':'secondaryAxis',"default":'yup','help':"Only necessary when no module provide for orientating","argType":"maya axis arg(ex:'yup')"},
                                         {'kw':'baseName',"default":None,'help':"baseName string","argType":"string"},
                                         {'kw':'connectBy',"default":'trans','help':"How the joint will scale","argType":"string"},
                                         {'kw':'advancedTwistSetup',"default":False,'help':"Whether to do the cgm advnaced twist setup","argType":"bool"},
                                         {'kw':'addMidTwist',"default":True,'help':"Whether to setup a mid twist on the segment","argType":"bool"},
                                         {'kw':'moduleInstance',"default":None,'help':"cgmModule to use for connecting on build","argType":"cgmModule"},	                                 
                                         {'kw':'extendTwistToEnd',"default":False,'help':"Whether to extned the twist to the end by default","argType":"bool"}]			    

            self.__dataBind__(*args,**kws)
            self.l_funcSteps = [{'step':'Verify','call':self._verify_},
                                {'step':'Curve Check','call':self._curveCheck_},
                                {'step':'Joint Setup','call':self._jointSetup_},
                                {'step':'Build Spline IK','call':self._splineIK_},
                                {'step':'Twist setup','call':self._twistSetup_},
                                {'step':'Attach','call':self._attachJoints_},
                                {'step':'Stretch setup','call':self._stretchSetup_},
                                ]
            #=================================================================
        def _verify_(self):
            try:#Query ===========================================================================================
                self.ml_joints = cgmMeta.validateObjListArg(self.d_kws['jointList'],mType = cgmMeta.cgmObject, mayaType=['joint'], noneValid = False)
                self.l_joints = [mJnt.p_nameShort for mJnt in self.ml_joints]
                self.int_lenJoints = len(self.ml_joints)#because it's called repeatedly
                self.mi_useCurve = cgmMeta.validateObjArg(self.d_kws['useCurve'],mayaType=['nurbsCurve'],noneValid = True)
                self.mi_module = cgmMeta.validateObjArg(self.d_kws['moduleInstance'],noneValid = True)
                try:self.mi_module.isModule()
                except:self.mi_module = False
                self.mi_mayaOrientation = cgmValid.simpleOrientation(self.d_kws['orientation'])
                self.str_orientation = self.mi_mayaOrientation.p_string
                self.str_secondaryAxis = cgmValid.stringArg(self.d_kws['secondaryAxis'],noneValid=True)
                self.str_baseName = cgmValid.stringArg(self.d_kws['baseName'],noneValid=True)
                self.str_connectBy = cgmValid.stringArg(self.d_kws['connectBy'],noneValid=True)		
                self.b_addMidTwist = cgmValid.boolArg(self.d_kws['addMidTwist'])
                self.b_advancedTwistSetup = cgmValid.boolArg(self.d_kws['advancedTwistSetup'])
                self.b_extendTwistToEnd= cgmValid.boolArg(self.d_kws['extendTwistToEnd'])
            except Exception,error:raise Exception,"[Query | error: {0}".format(error)  

            try:#Validate =====================================================================================
                if self.b_addMidTwist and self.int_lenJoints <4:
                    raise ValueError,"must have at least 3 joints for a mid twist setup"
                if self.int_lenJoints<3:
                    raise ValueError,"needs at least three joints"

                #Good way to verify an instance list? #validate orientation             
                #> axis -------------------------------------------------------------
                self.axis_aim = cgmValid.simpleAxis("%s+"%self.str_orientation [0])
                self.axis_aimNeg = cgmValid.simpleAxis("%s-"%self.str_orientation [0])
                self.axis_up = cgmValid.simpleAxis("%s+"%self.str_orientation [1])

                self.v_aim = self.axis_aim.p_vector#aimVector
                self.v_aimNeg = self.axis_aimNeg.p_vector#aimVectorNegative
                self.v_up = self.axis_up.p_vector   #upVector

                self.outChannel = self.str_orientation [2]#outChannel
                self.upChannel = '%sup'%self.str_orientation [1]#upChannel

            except Exception,error:
                raise Exception,"[data validation | error: {0}".format(error)  

            try:#>>> Module instance =====================================================================================
                self.mi_rigNull = False	
                if self.mi_module:
                    self.mi_rigNull = self.mi_module.rigNull	

                    if self.str_baseName is None:
                        self.str_baseName = self.mi_module.getPartNameBase()#Get part base name	    
                        log.debug('baseName set to module: %s'%self.str_baseName)	    	    
                if self.str_baseName is None:self.str_baseName = 'testSegmentCurve'    

            except Exception,error:raise Exception,"[Module checks | error: {0}".format(error) 	    

        def _curveCheck_(self):
            try:#Query ===========================================================================================
                if self.mi_useCurve:
                    #must get a offset u position
                    self.f_MatchPosOffset = crvUtils.getUParamOnCurve(self.ml_joints[0].mNode, self.mi_useCurve.mNode)
            except Exception,error:raise Exception,"[Query | error: {0}".format(error)  

        def _jointSetup_(self):
            try:#Pull local =======================================================================================
                ml_joints = self.ml_joints
                b_addMidTwist = self.b_addMidTwist
            except Exception,error:raise Exception,"[Pull local | error: {0}".format(error)  
            
            try:#>> Group ========================================================================================
                self.mi_grp = cgmMeta.cgmObject(name = 'newgroup')
                self.mi_grp.addAttr('cgmName', str(self.str_baseName), lock=True)
                self.mi_grp.addAttr('cgmTypeModifier','segmentStuff', lock=True)
                self.mi_grp.doName()
            except Exception,error:raise Exception,"[Group Creation | error: {0}".format(error) 	    

            try:#>> Orient ========================================================================================
                if not self.mi_module:#if it is, we can assume it's right
                    if self.str_secondaryAxis is None:
                        raise Exception,"Must have secondaryAxis arg if no moduleInstance is passed"
                    for mJnt in self.ml_joints:
                        """
                        Cannot iterate how important this step is. Lost a day trying to trouble shoot why one joint chain worked and another didn't.
                        WILL NOT connect right without this.
                        """
                        try:
                            joints.orientJoint(mJnt.mNode,self.str_orientation,self.str_secondaryAxis)
                        except Exception,error:raise Exception,"['%s' orient failed]{%s}"%(mJnt.p_nameShort,error)  
            except Exception,error:raise Exception,"[Orient | error: {0}".format(error) 
            
            try:#>> midtwist ========================================================================================
                ml_midTwistJoints = [] #exteded list of before and after joints
                int_mid = False
                
                if b_addMidTwist:#We need to get our factors
                    #>> Let's do the blend ===============================================================
                    int_mid = int(len(ml_joints)/2)
                    #ml_beforeJoints.reverse()
                    #Need to check for even value for this
                    if int_mid%2 == 0:#even
                        ml_beforeJoints = ml_joints[:int_mid]
                        ml_afterJoints = ml_joints[int_mid:]                          
                    else:
                        ml_beforeJoints = ml_joints[:int_mid+1]
                        ml_afterJoints = ml_joints[int_mid+1:]
                    self.log_info("beforeJoints: %s"%[i_jnt.getShortName() for i_jnt in ml_beforeJoints])
                    self.log_info("afterJoints: %s"%[i_jnt.getShortName() for i_jnt in ml_afterJoints])           
            except Exception,error:raise Exception,"[Midtwist logic | error: {0}".format(error) 

        def _splineIK_(self):
            self.ml_driverJoints = self.ml_joints
            if self.mi_useCurve:
                try:
                    #Because maya is stupid, when doing an existing curve splineIK setup in 2011, you need to select the objects
                    #Rather than use the flags
                    mc.select(cl=1)
                    mc.select([self.ml_driverJoints[0].mNode,self.ml_driverJoints[-1].mNode,self.mi_useCurve.mNode])
                    buffer = mc.ikHandle( simplifyCurve=False, eh = 1,curve = self.mi_useCurve.mNode,
                                          rootOnCurve=True, forceSolver = True, snapHandleFlagToggle=True,
                                          parentCurve = False, solver = 'ikSplineSolver',createCurve = False,)  
                except Exception,error:raise Exception,"[Spline IK | use curve mode | error: {0}".format(error) 	
                self.log_info(buffer)
                mi_segmentCurve = self.mi_useCurve#Link
                mi_segmentCurve.addAttr('cgmType','splineIKCurve',attrType='string',lock=True)
                mi_segmentCurve.doName()		
            else:
                try:#Create Curve =======================================================================================
                    buffer = mc.ikHandle( sj=self.ml_driverJoints[0].mNode, ee=self.ml_driverJoints[-1].mNode,simplifyCurve=False,
                                          solver = 'ikSplineSolver', ns = 4, rootOnCurve=True,forceSolver = True,
                                          createCurve = True,snapHandleFlagToggle=True )  
                except Exception,error:raise Exception,"[Spline IK | build curve | error: {0}".format(error) 	

                mi_segmentCurve = cgmMeta.asMeta( buffer[2],'cgmObject',setClass=True )
                mi_segmentCurve.addAttr('cgmName',self.str_baseName,attrType='string',lock=True)    
                mi_segmentCurve.addAttr('cgmType','splineIKCurve',attrType='string',lock=True)
                mi_segmentCurve.doName()

                try:#>> Module Link =======================================================================================
                    if self.mi_module:#if we have a module, connect vis
                        mi_segmentCurve.overrideEnabled = 1		
                        cgmMeta.cgmAttr(self.mi_rigNull.mNode,'gutsVis',lock=False).doConnectOut("%s.%s"%(mi_segmentCurve.mNode,'overrideVisibility'))    
                        cgmMeta.cgmAttr(self.mi_rigNull.mNode,'gutsLock',lock=False).doConnectOut("%s.%s"%(mi_segmentCurve.mNode,'overrideDisplayType'))    
                except Exception,error:raise Exception,"[Connect To Module | error: {0}".format(error) 

            self.mi_splineSolver = cgmMeta.cgmNode(name = 'ikSplineSolver')
            
            try:#>> Update func name strings ==============================================================================
                self._str_funcName = "%s(%s)"%(self._str_funcName,mi_segmentCurve.p_nameShort)
                self.__updateFuncStrings__()
            except Exception,error:self.log_error("Updating names strings | %s"%(error))	


            try:#>> Handle/Effector =======================================================================================
                mi_ikHandle = cgmMeta.asMeta( buffer[0],'cgmObject',setClass=True )
                mi_ikHandle.addAttr('cgmName',self.str_baseName,attrType='string',lock=True)    		
                mi_ikHandle.doName()
                mi_ikHandle.parent = self.mi_grp
                self.mi_ikHandle = mi_ikHandle

                mi_ikEffector = cgmMeta.asMeta( buffer[1],'cgmObject',setClass=True )
                mi_ikEffector.addAttr('cgmName',self.str_baseName,attrType='string',lock=True)  
                mi_ikEffector.doName()

                self.mi_ikEffector = mi_ikEffector
                if self.mi_useCurve:
                    self.log_info("useCurve mode > set ikHandle offset to %s"%self.f_MatchPosOffset)
                    mi_ikHandle.offset = self.f_MatchPosOffset
                mi_segmentCurve.connectChildNode(self.mi_grp,'segmentGroup','owner')
                self.mi_segmentCurve = mi_segmentCurve		
            except Exception,error:raise Exception,"[Handle/Effector | error: {0}".format(error) 	

        def _twistSetup_(self):
            try:#Pull local =======================================================================================
                ml_driverJoints = self.ml_driverJoints
                mi_ikHandle = self.mi_ikHandle
                b_addMidTwist = self.b_addMidTwist
                str_orientation = self.str_orientation

            except Exception,error:
                raise StandardError,"[Pull local | error: {0}".format(error)  

            try:#SplineIK Twist =======================================================================================
                d_twistReturn = rig_Utils.IKHandle_addSplineIKTwist(mi_ikHandle.mNode,self.b_advancedTwistSetup)
                mPlug_twistStart = d_twistReturn['mi_plug_start']
                mPlug_twistEnd = d_twistReturn['mi_plug_end']
            except Exception,error:raise Exception,"[Initial SplineIK Twist | error: {0}".format(error)  

            try:#>>> Twist stuff
                #=========================================================================
                #mPlug_factorInfluenceIn = cgmMeta.cgmAttr(self.mi_segmentCurve.mNode,"twistExtendToEnd",attrType = 'float',lock=False,keyable=True,hidden=False,minValue=0,maxValue=1)               
                #self.mPlug_factorInfluenceIn = mPlug_factorInfluenceIn#Link
                d_midTwistOutPlugs = {} # dictionary of out plugs to index of joint in the before or after list
                ml_midTwistJoints = [] #exteded list of before and after joints
                int_mid = False

                if b_addMidTwist:#We need to get our factors
                    try:#>> MidTwist =====================================================================================
                        #>> Let's do the blend ===============================================================
                        try:#First split it out ------------------------------------------------------------------
                            int_mid = int(len(ml_driverJoints)/2)
                            ml_beforeJoints = ml_driverJoints[1:int_mid]
                            ml_beforeJoints.reverse()
                            ml_afterJoints = ml_driverJoints[int_mid+1:-1]
                            self.log_debug("beforeJoints: %s"%[i_jnt.getShortName() for i_jnt in ml_beforeJoints])
                            self.log_debug("afterJoints: %s"%[i_jnt.getShortName() for i_jnt in ml_afterJoints])
                        except Exception,error:raise Exception,"[Split fail! | error: {0}".format(error)  

                        mPlug_midTwist = cgmMeta.cgmAttr(self.mi_segmentCurve,"twistMid",attrType='float',keyable=True,hidden=False)	    
                        ml_midTwistJoints.extend(ml_beforeJoints)
                        ml_midTwistJoints.extend(ml_afterJoints)
                        ml_midTwistJoints.append(ml_driverJoints[int_mid])
                        #Get our factors ------------------------------------------------------------------
                        mPlugs_factors = []
                        maxInt = (max([len(ml_beforeJoints),len(ml_afterJoints)])) +1#This is our max blend factors we need
                        fl_fac = 1.0/maxInt#get our factor
                        log.debug("maxInt: %s"%maxInt)
                        l_factors = [ (1-(i*fl_fac)) for i in range(maxInt) ]#fill our factor list
                        int_maxLen = len(l_factors)
                        for i,fac in enumerate(l_factors):
                            #self.progressBar_set(status = "Setting up midTwist factor nodes... ", progress = i, maxValue = int_maxLen)		    				    		    		    			    
                            mPlug_midFactorIn = cgmMeta.cgmAttr(self.mi_segmentCurve,"midFactor_%s"%(i),attrType='float',value=fac,hidden=False)	    
                            mPlug_midFactorOut = cgmMeta.cgmAttr(self.mi_segmentCurve,"out_midFactor_%s"%(i),attrType='float',lock=True)
                            arg = "%s = %s * %s"%(mPlug_midFactorOut.p_combinedShortName,mPlug_midTwist.p_combinedShortName,mPlug_midFactorIn.p_combinedShortName)
                            log.debug("%s arg: %s"%(i,arg))
                            NodeF.argsToNodes(arg).doBuild()
                            #Store it
                            d_midTwistOutPlugs[i] = mPlug_midFactorOut    
                    except Exception,error:raise Exception,"[MidTwist setup fail! | error: {0}".format(error)  
                """
                mPlugs_rollSumDrivers = []#Advanced Twist
                mPlugs_rollDrivers = []
                d_mPlugs_rotateGroupDrivers = {}
                self.md_mPlugs_rotateGroupDrivers = d_mPlugs_rotateGroupDrivers
                for i,mJnt in enumerate(ml_driverJoints):
                    #self.progressBar_set(status = "Setting up twist setup | '%s'"%self.l_driverJoints[i], progress = i, maxValue = self.int_lenJoints)		    				    		    		    			    		    
                    mPlugs_twistSumOffset = []
                    if mJnt not in [ml_driverJoints[0],ml_driverJoints[-1]]:
                        if b_addMidTwist and mJnt in ml_midTwistJoints:
                            if mJnt in ml_afterJoints:int_index = ml_afterJoints.index(mJnt)+1
                            elif mJnt in ml_beforeJoints:int_index = ml_beforeJoints.index(mJnt)+1
                            elif mJnt == ml_driverJoints[int_mid]:int_index = 0
                            else:raise StandardError,"Found no mid twist index for: '%s'"%mJnt.getShortName()

                            try:mPlug_midTwistFactor = d_midTwistOutPlugs[int_index]
                            except:raise StandardError,"Found no mid twist plug for: '%s' | %s"%(mJnt.getShortName(),d_midTwistOutPlugs.keys())
                            mPlugs_twistSumOffset.append(mPlug_midTwistFactor)

                        mPlug_baseRoll = cgmMeta.cgmAttr(mJnt,'r%s'%str_orientation[0])
                        mPlug_extendTwistFactor = cgmMeta.cgmAttr(self.mi_segmentCurve.mNode,"out_extendTwistFactor_%s"%i,attrType = 'float',lock=True)		    
                        mPlug_extendTwist = cgmMeta.cgmAttr(self.mi_segmentCurve.mNode,"out_extendTwist_%s"%i,attrType = 'float',lock=True)	
                        mPlug_twistSum = cgmMeta.cgmAttr(self.mi_segmentCurve.mNode,"out_twistSum_%s"%i,attrType = 'float',lock=True)	

                        #twistFactor = baseRoll / 2
                        arg_extendInfluenceFactor = " %s = %s / 2"%(mPlug_extendTwistFactor.p_combinedShortName,mPlug_baseRoll.p_combinedShortName)
                        #extendTwist = factorIn * factor
                        arg_extendInfluence = " %s = %s * -%s"%(mPlug_extendTwist.p_combinedShortName,mPlug_factorInfluenceIn.p_combinedShortName,mPlug_extendTwistFactor.p_combinedShortName)
                        mPlugs_twistSumOffset.append(mPlug_extendTwist)
                        arg_twistSum = " %s = %s"%(mPlug_twistSum.p_combinedShortName,' + '.join([mPlug.p_combinedShortName for mPlug in mPlugs_twistSumOffset]))

                        for arg in [arg_extendInfluenceFactor,arg_extendInfluence,arg_twistSum]:
                            self.log_debug(arg)
                            NodeF.argsToNodes(arg).doBuild() 
                        d_mPlugs_rotateGroupDrivers[i] = mPlug_twistSum
                """

            except Exception,error:
                raise StandardError,"[Segment Twist setup | error: {0}".format(error) 

        def _attachJoints_(self):
            try:#Pull local =======================================================================================
                #ml_driverJoints = self.ml_driverJoints
                ml_joints = self.ml_joints
                mi_ikHandle = self.mi_ikHandle
                b_addMidTwist = self.b_addMidTwist
                str_orientation = self.str_orientation
                mi_segmentCurve = self.mi_segmentCurve
                mi_module = self.mi_module
                mi_rigNull = self.mi_rigNull
                #md_mPlugs_rotateGroupDrivers = self.md_mPlugs_rotateGroupDrivers
            except Exception,error:
                raise StandardError,"[Pull local | error: {0}".format(error)  

            try:#>>> Create up locs, follicles -------------------------------------------------------------
                ml_pointOnCurveInfos = []
                #ml_upGroups = []

                #Link up
                self.ml_pointOnCurveInfos = ml_pointOnCurveInfos
                #self.ml_upGroups = ml_upGroups

                #First thing we're going to do is create our 'follicles'
                l_shapes = mc.listRelatives(mi_segmentCurve.mNode,shapes=True)
                str_shape = l_shapes[0]

                for i,mJnt in enumerate(ml_joints):   
                    #self.progressBar_set(status = "Attaching| '%s'"%self.l_joints[i], progress = i, maxValue = self.int_lenJoints)		    				    		    		    			    		    		    
                    l_closestInfo = distance.returnNearestPointOnCurveInfo(mJnt.mNode,mi_segmentCurve.mNode)
                    log.debug("'%s' closest info: %s"%(mJnt.mNode,l_closestInfo))
                    #>>> POCI ----------------------------------------------------------------
                    mi_closestPointNode = cgmMeta.cgmNode(nodeType = 'pointOnCurveInfo')
                    mc.connectAttr ((str_shape+'.worldSpace'),(mi_closestPointNode.mNode+'.inputCurve'))	

                    #> Name
                    mi_closestPointNode.doStore('cgmName',mJnt)
                    mi_closestPointNode.doName()
                    #>Set follicle value
                    mi_closestPointNode.parameter = l_closestInfo['parameter']
                    ml_pointOnCurveInfos.append(mi_closestPointNode)
                    """
                    #>>> loc ----------------------------------------------------------------
                    mi_upLoc = mJnt.doLoc()#Make up Loc
                    mi_locRotateGroup = mJnt.duplicateTransform(False)#group in place
                    mi_locRotateGroup.parent = ml_driverJoints[i].mNode
                    mi_locRotateGroup.doStore('cgmName',mJnt)	    
                    mi_locRotateGroup.addAttr('cgmTypeModifier','rotate',lock=True)
                    mi_locRotateGroup.doName()

                    #Store the rotate group to the joint
                    mJnt.connectChildNode(mi_locRotateGroup,'rotateUpGroup','drivenJoint')
                    mi_zeroGrp = cgmMeta.asMeta( mi_locRotateGroup.doGroup(True),'cgmObject',setClass=True )
                    mi_zeroGrp.addAttr('cgmTypeModifier','zero',lock=True)
                    mi_zeroGrp.doName()

                    #connect some other data
                    mi_locRotateGroup.connectChildNode(mi_locRotateGroup.parent,'zeroGroup')
                    mi_locRotateGroup.connectChildNode(mi_upLoc,'upLoc')
                    mJnt.connectChildNode(mi_upLoc,'upLoc')
                    mc.makeIdentity(mi_locRotateGroup.mNode, apply=True,t=1,r=1,s=1,n=0)

                    mi_upLoc.parent = mi_locRotateGroup.mNode
                    mc.move(0,10,0,mi_upLoc.mNode,os=True)#TODO - make dependent on orientation	
                    ml_upGroups.append(mi_upLoc)

                    #Connect the rotate
                    #if extendTwistToEnd:#Need at least x joints
                    mPlug_rotateDriver = md_mPlugs_rotateGroupDrivers.get(i) or False
                    if mPlug_rotateDriver:
                        mPlug_rotateDriver.doConnectOut("%s.r%s"%(mi_locRotateGroup.mNode,str_orientation[0]))
                        #ml_twistDrivers.append(mPlug_factorInfluenceOut)
                    
                    try:
                        if mi_module:#if we have a module, connect vis
                            mi_upLoc.overrideEnabled = 1		
                            cgmMeta.cgmAttr(mi_rigNull,'gutsVis',lock=False).doConnectOut("%s.%s"%(mi_upLoc.mNode,'overrideVisibility'))
                            cgmMeta.cgmAttr(mi_rigNull,'gutsLock',lock=False).doConnectOut("%s.%s"%(mi_upLoc.mNode,'overrideDisplayType'))    
                    except Exception,error:raise Exception,"[module connect | error: {0}".format(error) 
                    """

                #Orient constrain our last joint to our splineIK Joint
                #constBuffer = mc.orientConstraint(ml_driverJoints[-1].mNode,ml_joints[-1].mNode,maintainOffset = True)
                #attributes.doSetAttr(constBuffer[0],'interpType',0)

            except Exception,error:raise Exception,"[attach and connect | error: {0}".format(error) 

        def _stretchSetup_(self):
            try:#Pull local =======================================================================================
                #ml_driverJoints = self.ml_driverJoints
                mi_ikHandle = self.mi_ikHandle                
                ml_joints = self.ml_joints
                str_orientation = self.str_orientation
                mi_segmentCurve = self.mi_segmentCurve
                mi_grp = self.mi_grp
                mi_module = self.mi_module
                mi_rigNull = self.mi_rigNull
                ml_pointOnCurveInfos = self.ml_pointOnCurveInfos
                #ml_upGroups = self.ml_upGroups		
                #md_mPlugs_rotateGroupDrivers = self.md_mPlugs_rotateGroupDrivers
            except Exception,error:raise Exception,"[Pull local | error: {0}".format(error)  

            try:#>>> Scale stuff =============================================================================
                #> Create IK effectors,Create distance nodes
                #ml_IKeffectors = []
                #ml_IKhandles = []  
                ml_distanceObjects = []
                ml_distanceShapes = []  
                for i,mJnt in enumerate(ml_joints[:-1]):
                    try:
                        #self.progressBar_set(status = "scale guts | '%s'"%self.l_joints[i], progress = i, maxValue = self.int_lenJoints)
                        """
                        ik_buffer = mc.ikHandle (startJoint=mJnt.mNode,
                                                 endEffector = ml_joints[i+1].mNode,
                                                 setupForRPsolver = True, solver = 'ikRPsolver',
                                                 enableHandles=True )
                        #Handle
                        mi_IK_Handle = cgmMeta.asMeta(ik_buffer[0],'cgmObject',setClass=True)
                        mi_IK_Handle.parent = ml_driverJoints[i+1].mNode
                        mi_IK_Handle.doStore('cgmName',mJnt)    
                        mi_IK_Handle.doName()

                        #Effector
                        mi_IK_Effector = cgmMeta.cgmObject(ik_buffer[1])        
                        mi_IK_Effector.doStore('cgmName',mJnt)    
                        mi_IK_Effector.doName()

                        ml_IKhandles.append(mi_IK_Handle)
                        ml_IKeffectors.append(mi_IK_Effector)

                        if mi_module:#if we have a module, connect vis
                            mi_IK_Handle.overrideEnabled = 1		
                            cgmMeta.cgmAttr(mi_module.rigNull.mNode,'gutsVis',lock=False).doConnectOut("%s.%s"%(mi_IK_Handle.mNode,'overrideVisibility'))
                            cgmMeta.cgmAttr(mi_module.rigNull.mNode,'gutsLock',lock=False).doConnectOut("%s.%s"%(mi_IK_Handle.mNode,'overrideDisplayType'))    
                        """
                        #>> Distance nodes
                        mi_distanceShape = cgmMeta.cgmNode( mc.createNode ('distanceDimShape') )        
                        mi_distanceObject = cgmMeta.cgmObject( mi_distanceShape.getTransform() )
                        mi_distanceObject.doStore('cgmName',mJnt)
                        mi_distanceObject.addAttr('cgmType','measureNode',lock=True)
                        mi_distanceObject.doName(nameShapes = True)
                        mi_distanceObject.parent = mi_grp.mNode#parent it
                        mi_distanceObject.overrideEnabled = 1
                        mi_distanceObject.overrideVisibility = 1

                        #Connect things
                        mc.connectAttr ((ml_pointOnCurveInfos[i].mNode+'.position'),(mi_distanceShape.mNode+'.startPoint'))
                        mc.connectAttr ((ml_pointOnCurveInfos[i+1].mNode+'.position'),(mi_distanceShape.mNode+'.endPoint'))

                        ml_distanceObjects.append(mi_distanceObject)
                        ml_distanceShapes.append(mi_distanceShape)


                        if mi_module:#Connect hides if we have a module instance:
                            cgmMeta.cgmAttr(mi_module.rigNull.mNode,'gutsVis',lock=False).doConnectOut("%s.%s"%(mi_distanceObject.mNode,'overrideVisibility'))
                            cgmMeta.cgmAttr(mi_module.rigNull.mNode,'gutsLock',lock=False).doConnectOut("%s.%s"%(mi_distanceObject.mNode,'overrideDisplayType'))    
                    except Exception,error:raise Exception,"[Pull local | error: {0}".format(error)  
            except Exception,error:
                raise Exception,"[scale stuff setup | error: {0}".format(error) 
            """
            try:#fix twists ==========================================================================================
                #>> Second part for the full twist setup
                aimChannel = str_orientation[0]  

                for i,mJnt in enumerate(ml_joints[:-1]):
                    #self.progressBar_set(status = "fixing twist | '%s'"%self.l_driverJoints[i], progress = i, maxValue = self.int_lenJoints)		    
                    rotBuffer = mc.xform (mJnt.mNode, q=True, ws=True, ro=True)
                    log.debug("rotBuffer: %s"%rotBuffer)
                    #Create the poleVector
                    poleVector = mc.poleVectorConstraint (ml_upGroups[i].mNode,ml_IKhandles[i].mNode)  	
                    IKHandle_fixTwist(ml_IKhandles[i])

                    if mc.xform (mJnt.mNode, q=True, ws=True, ro=True) != rotBuffer:
                        self.log_info("Found the following on '%s': %s"%(mJnt.getShortName(),mc.xform (mJnt.mNode, q=True, ws=True, ro=True)))
            except Exception,error:
                raise Exception,"[fix twists | error: {0}".format(error) """

            try:#>>>Hook up stretch/scale #==========================================================================
                #Buffer
                mi_jntScaleBufferNode = cgmMeta.cgmBufferNode(name = self.str_baseName,overideMessageCheck=True)
                mi_jntScaleBufferNode.addAttr('cgmType','distanceBuffer')
                mi_jntScaleBufferNode.addAttr('masterScale',value = 1.0, minValue = 0.0001, attrType='float')    
                #mi_jntScaleBufferNode.addAttr('segmentScale',value = 1.0, attrType='float',minValue = 0.0) 

                mi_jntScaleBufferNode.doName()
                ml_distanceAttrs = []
                ml_resultAttrs = []

                mi_jntScaleBufferNode.connectParentNode(mi_segmentCurve.mNode,'segmentCurve','scaleBuffer')
                ml_mainMDs = []
                for i,mJnt in enumerate(ml_joints[:-1]):
                    #self.progressBar_set(status = "node setup | '%s'"%self.l_joints[i], progress = i, maxValue = self.int_lenJoints)		    

                    #Make some attrs
                    mPlug_attrDist= cgmMeta.cgmAttr(mi_jntScaleBufferNode.mNode,
                                                    "distance_%s"%i,attrType = 'float',initialValue=0,lock=True,minValue = 0)
                    mPlug_attrNormalBaseDist = cgmMeta.cgmAttr(mi_jntScaleBufferNode.mNode,
                                                               "normalizedBaseDistance_%s"%i,attrType = 'float',
                                                               initialValue=0,lock=True,minValue = 0)			
                    mPlug_attrNormalDist = cgmMeta.cgmAttr(mi_jntScaleBufferNode.mNode,
                                                           "normalizedDistance_%s"%i,attrType = 'float',initialValue=0,lock=True,minValue = 0)		
                    mPlug_attrResult = cgmMeta.cgmAttr(mi_jntScaleBufferNode.mNode,
                                                       "scaleResult_%s"%i,attrType = 'float',initialValue=0,lock=True,minValue = 0)	
                    mPlug_attrTransformedResult = cgmMeta.cgmAttr(mi_jntScaleBufferNode.mNode,
                                                                  "scaledScaleResult_%s"%i,attrType = 'float',initialValue=0,lock=True,minValue = 0)	

                    #Store our distance base to our buffer
                    try:mi_jntScaleBufferNode.store(ml_distanceShapes[i].distance)#Store to our buffer
                    except Exception,error:raise Exception,"[Failed to store joint distance: %s]{%s}"%(ml_distanceShapes[i].mNode,error)


                    if self.str_connectBy.lower() in ['translate','trans']:
                        #Let's build our args
                        l_argBuild = []
                        #distance by master
                        l_argBuild.append("{0} = {1} / {2}".format(mPlug_attrNormalBaseDist.p_combinedShortName,
                                                                   '{0}.{1}'.format(mi_jntScaleBufferNode.mNode,mi_jntScaleBufferNode.d_indexToAttr[i]),
                                                                   "{0}.masterScale".format(mi_jntScaleBufferNode.mNode)))
                        l_argBuild.append("{0} = {1} / {2}".format(mPlug_attrNormalDist.p_combinedShortName,
                                                                   mPlug_attrDist.p_combinedShortName,
                                                                   "{0}.masterScale".format(mi_jntScaleBufferNode.mNode)))			
                        for arg in l_argBuild:
                            self.log_info("Building: {0}".format(arg))
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
                        mi_mdNormalBaseDist.doStore('cgmName',mJnt)
                        mi_mdNormalBaseDist.addAttr('cgmTypeModifier','normalizedBaseDist')
                        mi_mdNormalBaseDist.doName()

                        attributes.doConnectAttr('%s.masterScale'%(mi_jntScaleBufferNode.mNode),#>>
                                                 '%s.%s'%(mi_mdNormalBaseDist.mNode,'input1X'))
                        attributes.doConnectAttr('%s.%s'%(mi_jntScaleBufferNode.mNode,mi_jntScaleBufferNode.d_indexToAttr[i]),#>>
                                                 '%s.%s'%(mi_mdNormalBaseDist.mNode,'input2X'))	
                        mPlug_attrNormalBaseDist.doConnectIn('%s.%s'%(mi_mdNormalBaseDist.mNode,'output.outputX'))

                        #Create the normalized distance
                        mi_mdNormalDist = cgmMeta.cgmNode(nodeType='multiplyDivide')
                        mi_mdNormalDist.operation = 1
                        mi_mdNormalDist.doStore('cgmName',mJnt)
                        mi_mdNormalDist.addAttr('cgmTypeModifier','normalizedDist')
                        mi_mdNormalDist.doName()

                        attributes.doConnectAttr('%s.masterScale'%(mi_jntScaleBufferNode.mNode),#>>
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

                    #Create the normalized base distance


                    #Append our data
                    ml_distanceAttrs.append(mPlug_attrDist)
                    ml_resultAttrs.append(mPlug_attrResult)

                    """
                for axis in [str_orientation[1],str_orientation[2]]:
                    attributes.doConnectAttr('%s.s%s'%(mJnt.mNode,axis),#>>
                                             '%s.s%s'%(ml_driverJoints[i].mNode,axis))"""	 	
            except Exception,error:raise Exception,"[Stretch wiring | error: {0}".format(error) 

            try:#Connect last joint scale to second to last
                for axis in ['scaleX','scaleY','scaleZ']:
                    attributes.doConnectAttr('%s.%s'%(ml_joints[-2].mNode,axis),#>>
                                             '%s.%s'%(ml_joints[-1].mNode,axis))	 

                #mc.pointConstraint(ml_driverJoints[0].mNode,ml_joints[0].mNode,maintainOffset = False)
            except Exception,error:raise Exception,"[constrain last end end bits | error: {0}".format(error) 

            try:#>> Connect and close =============================================================================
                mi_segmentCurve.connectChildNode(mi_jntScaleBufferNode,'scaleBuffer','segmentCurve')
                mi_segmentCurve.connectChildNode(mi_ikHandle,'ikHandle','segmentCurve')
                mi_segmentCurve.msgList_connect(ml_joints,'drivenJoints','segmentCurve')       
                #mi_segmentCurve.msgList_connect(ml_driverJoints,'driverJoints','segmentCurve')   
            except Exception,error:raise Exception,"[Final Connections | error: {0}".format(error) 

            try:#Return Prep ====================================================================================
                d_return = {'mi_segmentCurve':mi_segmentCurve,'segmentCurve':mi_segmentCurve.mNode,'mi_ikHandle':mi_ikHandle,'mi_segmentGroup':mi_grp,
                            'scaleBuffer':mi_jntScaleBufferNode.mNode,'mi_scaleBuffer':mi_jntScaleBufferNode,#'mPlug_extendTwist':self.mPlug_factorInfluenceIn,
                            'l_drivenJoints':self.l_joints,'ml_drivenJoints':ml_joints}
            except Exception,error:raise Exception,"[Return prep | error: {0}".format(error) 
            return d_return	   		
    return fncWrap(*args,**kws).go()

_d_KWARG_segementJoints = {'kw':'segmentJoints',"default":[], 'help':"List of segment joints", "argType":"list"}
_d_KWARG_influenceJoints = {'kw':'influenceJoints',"default":[], 'help':"List of influence joints", "argType":"list"}
_d_KWARG_useCurve = {'kw':'useCurve',"default":None,'help':"Which curve to use. If None. One Created","argType":"nurbsCurve"}
_d_KWARG_orienation = {'kw':'orientation',"default":'zyx','help':"What is the joints orientation","argType":"string"}
_d_KWARG_secondaryAxis = {'kw':'secondaryAxis',"default":'yup','help':"Only necessary when no module provide for orientating","argType":"maya axis arg(ex:'yup')"}

_d_KWARG_extendTwistToEnd = {'kw':'extendTwistToEnd',"default":False,'help':"Whether to extned the twist to the end by default","argType":"bool"}
_d_KWARG_addTwist = {'kw':'addTwist',"default":False,'help':"whether to add extra twist in the segment","argType":"bool"}
_d_KWARG_addMidTwist = {'kw':'addMidTwist',"default":False,'help':"Whether to setup a mid twist on the segment","argType":"bool"}
_d_KWARG_advancedTwistSetup = {'kw':'advancedTwistSetup',"default":False,'help':"Whether to do the cgm advnaced twist setup","argType":"bool"}

_d_KWARG_addSquashStretch = {'kw':'addSquashStretch',"default":False,'help':"whether to setup squash and stretch in the segment","argType":"bool"}
_d_KWARG_additiveScaleSetup = {'kw':'additiveScaleSetup',"default":False,'help':"whether to setup additive scale","argType":"bool"}
_d_KWARG_additiveScaleConnect = {'kw':'additiveScaleConnect',"default":False,'help':"whether to connect additive scale","argType":"bool"}
_d_KWARG_connectBy = {'kw':'connectBy',"default":'scale','help':"How the joint will scale","argType":"string"}


_d_KWARG_startControl = {'kw':'startControl',"default":None,'help':"Start control for the segment","argType":"string"}
_d_KWARG_endControl = {'kw':'endControl',"default":None,'help':"End control for the segment","argType":"string"}
_d_KWARG_controlOrienation = {'kw':'controlOrientation',"default":'zyx',
                              'help':"What is the control orientation. Important as it sets which channels will drive twist and additive scale",
                              "argType":"string"}

_d_KWARG_baseName = {'kw':'baseName',"default":None,'help':"baseName string","argType":"string"}
_d_KWARG_moduleInstance = {'kw':'moduleInstance',"default":None,'help':"cgmModule to use for connecting on build","argType":"cgmModule"}                                

def create_basic(*args,**kws):
    """
        :parameters:
            0 - 'segmentJoints'(list - []) | List of segment joints
            1 - 'influenceJoints'(list - []) | List of influence joints
            2 - 'startControl'(string - None) | Start control for the segment
            3 - 'endControl'(string - None) | End control for the segment
            4 - 'orientation'(string - zyx) | What is the joints orientation
            5 - 'secondaryAxis'(maya axis arg(ex:'yup') - yup) | Only necessary when no module provide for orientating
            6 - 'controlOrientation'(string - zyx) | What is the control orientation. Important as it sets which channels will drive twist and additive scale
            7 - 'useCurve'(nurbsCurve - None) | Which curve to use. If None. One Created
            8 - 'rootSetup'(string - torso) | Type of root setup
            9 - 'segmentType'(string - curve) | Type of segment setup
            10 - 'addSquashStretch'(bool - False) | whether to setup squash and stretch in the segment
            11 - 'connectBy'(string - trans) | How the joint will scale
            12 - 'addTwist'(bool - False) | whether to add extra twist in the segment
            13 - 'addMidTwist'(bool - False) | Whether to setup a mid twist on the segment
            14 - 'advancedTwistSetup'(bool - False) | Whether to do the cgm advnaced twist setup
            15 - 'additiveScaleSetup'(bool - False) | whether to setup additive scale
            16 - 'additiveScaleConnect'(bool - False) | whether to connect additive scale
            17 - 'rotateGroupAxis'(string - y) | the rotate axis of the rotate group for a twist setup
            18 - 'baseName'(string - None) | baseName string
            19 - 'moduleInstance'(cgmModule - None) | cgmModule to use for connecting on build

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
    class fncWrap(cgmGeneral.cgmFuncCls):
        def __init__(self,*args,**kws):            
            super(fncWrap, self).__init__(*args, **kws)
            self._str_funcName= "create_basic"
            self._b_reportTimes = True
            self._b_autoProgressBar = 1
            self._l_ARGS_KWS_DEFAULTS = [_d_KWARG_segementJoints,
                                         _d_KWARG_influenceJoints,
                                         _d_KWARG_startControl,
                                         _d_KWARG_endControl,
                                         _d_KWARG_orienation,
                                         _d_KWARG_secondaryAxis,
                                         _d_KWARG_controlOrienation,
                                         _d_KWARG_useCurve,
                                         {'kw':'rootSetup',"default":'torso','help':"Type of root setup","argType":"string"},                                         
                                         {'kw':'segmentType',"default":'curve','help':"Type of segment setup","argType":"string"},
                                         _d_KWARG_addSquashStretch,
                                         _d_KWARG_connectBy,
                                         _d_KWARG_addTwist,
                                         _d_KWARG_addMidTwist,
                                         _d_KWARG_advancedTwistSetup,
                                         _d_KWARG_additiveScaleSetup,
                                         _d_KWARG_additiveScaleConnect,
                                         {'kw':'rotateGroupAxis',"default":'y','help':"the rotate axis of the rotate group for a twist setup","argType":"string"},
                                         _d_KWARG_baseName,
                                         _d_KWARG_moduleInstance,
                                         ]			    

            self.__dataBind__(*args,**kws)
            self.l_funcSteps = [{'step':'Verify','call':self._func_verify_},
                                {'step':'Build Transforms','call':self._func_transforms_},
                                {'step':'Constraints','call':self._func_constraints_},
                                {'step':'Build Segment','call':self._func_segment_},
                                {'step':'Skin segment','call':self._func_skin_},
                                {'step':'Aim setup','call':self._func_aim_},
                                {'step':'Finalize','call':self._func_finalize_},
                                ]
        def _func_verify_(self):
            try:#Query ===========================================================================================
                _joints = self.d_kws['segmentJoints']
                self.int_lenJoints = len(_joints)#because it's called repeatedly       
                
                self.ml_joints = cgmMeta.validateObjListArg(self.d_kws['segmentJoints'],mType = 'cgmObject', mayaType=['joint'], noneValid = False)
                self.l_joints = [mJnt.p_nameShort for mJnt in self.ml_joints]
                self.int_lenJoints = len(self.ml_joints)#because it's called repeatedly
                
                self.ml_influenceJoints = cgmMeta.validateObjListArg(self.d_kws['influenceJoints'],'cgmObject',noneValid=False,mayaType=['nurbsCurve','joint'])
                
                self.mi_useCurve = cgmMeta.validateObjArg(self.d_kws['useCurve'],mayaType=['nurbsCurve'],noneValid = True)
                
                self.mi_module = cgmMeta.validateObjArg(self.d_kws['moduleInstance'],noneValid = True)
                try:self.mi_module.isModule()
                except:self.mi_module = False
                
                self.mi_startControl = cgmMeta.validateObjArg(self.d_kws['startControl'],'cgmObject',noneValid=True)
                self.mi_endControl = cgmMeta.validateObjArg(self.d_kws['endControl'],'cgmObject',noneValid=True)

                self.mi_mayaOrientation = cgmValid.simpleOrientation(self.d_kws['orientation'])
                self.str_orientation = self.mi_mayaOrientation.p_string

                #Good way to verify an instance list? #validate orientation
                #Gather info
                _controlOrientation = self.d_kws['controlOrientation']
                if _controlOrientation is None:
                    self.str_controlOrientation = self.str_orientation   
                    self.mi_mayaControlOrientation = self.mi_mayaOrientation
                else:
                    self.mi_mayaControlOrientation = cgmValid.simpleOrientation(self.d_kws['controlOrientation'])
                    self.str_controlOrientation = self.mi_mayaControlOrientation.p_string
        
                #> baseDistance -------------------------------------------------------------
                self._f_baseDist = distance.returnDistanceBetweenObjects(self.ml_joints[0].mNode,self.ml_joints[-1].mNode)/2                  
                
                self.str_secondaryAxis = cgmValid.stringArg(self.d_kws['secondaryAxis'],noneValid=True)
                self.str_baseName = cgmValid.stringArg(self.d_kws['baseName'],noneValid=True)
                self.str_connectBy = cgmValid.stringArg(self.d_kws['connectBy'],noneValid=True)	
                self.b_addTwist = cgmValid.boolArg(self.d_kws['addTwist'])                
                self.b_addMidTwist = cgmValid.boolArg(self.d_kws['addMidTwist'])
                self.b_advancedTwistSetup = cgmValid.boolArg(self.d_kws['advancedTwistSetup'])
                self.b_addSquashStretch = cgmValid.boolArg(self.d_kws['addSquashStretch'])
                self.b_additiveScaleSetup = cgmValid.boolArg(self.d_kws['additiveScaleSetup'])
                self.b_additiveScaleConnect = cgmValid.boolArg(self.d_kws['additiveScaleConnect'])
                
                #self.b_extendTwistToEnd= cgmValid.boolArg(self.d_kws['extendTwistToEnd'])
                
                self.str_rootSetup = self.d_kws['rootSetup']
                self.str_segmentType = self.d_kws['segmentType']
                
            except Exception,error:raise Exception,"[Query | error: {0}".format(error)  

            try:#Validate =====================================================================================
                if self.b_addMidTwist and self.int_lenJoints <4:
                    raise ValueError,"must have at least 3 joints for a mid twist setup"
                if self.int_lenJoints<3:
                    raise ValueError,"needs at least three joints"

                #Good way to verify an instance list? #validate orientation             
                #> axis -------------------------------------------------------------
                self.axis_aim = cgmValid.simpleAxis("%s+"%self.str_orientation [0])
                self.axis_aimNeg = cgmValid.simpleAxis("%s-"%self.str_orientation [0])
                self.axis_up = cgmValid.simpleAxis("%s+"%self.str_orientation [1])

                self.v_aim = self.axis_aim.p_vector#aimVector
                self.v_aimNeg = self.axis_aimNeg.p_vector#aimVectorNegative
                self.v_up = self.axis_up.p_vector   #upVector

                self.outChannel = self.str_orientation [2]#outChannel
                self.upChannel = '%sup'%self.str_orientation[1]#upChannel

            except Exception,error:
                raise Exception,"[data validation | error: {0}".format(error)  

            try:#>>> Module instance =====================================================================================
                self.mi_rigNull = False	
                if self.mi_module:
                    self.mi_rigNull = self.mi_module.rigNull	

                    if self.str_baseName is None:
                        self.str_baseName = self.mi_module.getPartNameBase()#Get part base name	    
                        log.debug('baseName set to module: %s'%self.str_baseName)	    	    
                if self.str_baseName is None:self.str_baseName = 'testSegmentCurve'    

            except Exception,error:raise Exception,"[Module checks | error: {0}".format(error) 
            #self.report_selfStored()
        
        def _func_transforms_(self):
            try:#Query ===========================================================================================
                ml_jointList = self.ml_joints
                ml_influenceJoints = self.ml_influenceJoints
                
                ml_rigObjects = []
                self.ml_rigObjects = ml_rigObjects
                
                i_startControl = self.mi_startControl
                i_endControl = self.mi_endControl
                
                orientation = self.str_orientation
            except Exception,err:raise Exception,"[Bring local | error: {0}".format(err)
            
            try:#Anchor transforms ===============================================================================
                #Start Anchor                
                i_anchorStart = ml_jointList[0].duplicateTransform()
                i_anchorStart.addAttr('cgmType','anchor',attrType='string',lock=True)
                i_anchorStart.doName()
                i_anchorStart.parent = False      
                
                self.mi_anchorStart = i_anchorStart
                
                #End Anchor
                i_anchorEnd = ml_jointList[-1].duplicateTransform()
                i_anchorEnd.addAttr('cgmType','anchor',attrType='string',lock=True)
                i_anchorEnd.doName()    
                i_anchorEnd.parent = False                
                
                self.mi_anchorEnd = i_anchorEnd
                
                #>>>Attach -----------------------------------------------------------------
                #Start Attach
                i_attachStartNull = ml_jointList[0].duplicateTransform()
                i_attachStartNull.addAttr('cgmType','attach',attrType='string',lock=True)
                i_attachStartNull.doName()
                i_attachStartNull.parent = i_anchorStart.mNode  
                
                self.mi_attachStartNull = i_attachStartNull
            
                #End Attach
                i_attachEndNull = ml_jointList[-1].duplicateTransform()
                i_attachEndNull.addAttr('cgmType','attach',attrType='string',lock=True)
                i_attachEndNull.doName()
                i_attachEndNull.parent = i_anchorEnd.mNode      
                
                self.mi_attachEndNull = i_attachEndNull
                
                
                ml_influenceJoints[0].parent = i_attachStartNull.mNode
                ml_influenceJoints[-1].parent = i_attachEndNull.mNode                
                
            except Exception,err:raise Exception,"[Anchor transforms | error: {0}".format(err)
            
            try:#Aim Null creation ===============================================================================
                #Start Aim
                i_aimStartNull = ml_jointList[0].duplicateTransform()
                i_aimStartNull.addAttr('cgmType','aim',attrType='string',lock=True)
                i_aimStartNull.doName()
                i_aimStartNull.parent = i_anchorStart.mNode   
                i_aimStartNull.rotateOrder = 0
                
                self.mi_aimStartNull = i_aimStartNull
            
                #End Aim
                i_aimEndNull = ml_jointList[-1].duplicateTransform()
                i_aimEndNull.addAttr('cgmType','aim',attrType='string',lock=True)
                i_aimEndNull.doName()
                i_aimEndNull.parent = i_anchorEnd.mNode 
                i_aimEndNull.rotateOrder = 0
                
                self.mi_aimEndNull = i_aimEndNull
                
            except Exception,err:raise Exception,"[Aim null creation | error: {0}".format(err)            
            
            try:#Up Null creation ===============================================================================
                #>>>Up locs
                i_startUpNull = ml_jointList[0].duplicateTransform()
                i_startUpNull.parent = i_anchorStart.mNode  
                i_startUpNull.addAttr('cgmType','up',attrType='string',lock=True)
                i_startUpNull.doName()
                ml_rigObjects.append(i_startUpNull)
                attributes.doSetAttr(i_startUpNull.mNode,'t%s'%orientation[2],self._f_baseDist)#We're gonna push these out
                
                self.mi_startUpNull = i_startUpNull
                
                #End
                i_endUpNull = ml_jointList[-1].duplicateTransform()
                i_endUpNull.parent = i_anchorEnd.mNode     	
                i_endUpNull.addAttr('cgmType','up',attrType='string',lock=True)
                i_endUpNull.doName()
                ml_rigObjects.append(i_endUpNull)
                attributes.doSetAttr(i_endUpNull.mNode,'t%s'%orientation[2],self._f_baseDist)#We're gonna push these out
                
                self.mi_endUpNull = i_endUpNull
                
            except Exception,err:raise Exception,"[Up null creation | error: {0}".format(err)   
            
            
            try:#Aim Target creation ===============================================================================
                #Start Aim Target
                i_aimStartTargetNull = ml_jointList[-1].duplicateTransform()
                i_aimStartTargetNull.addAttr('cgmType','aimTargetStart',attrType='string',lock=True)
                i_aimStartTargetNull.doName()
                i_aimStartTargetNull.parent = ml_influenceJoints[-1].mNode     
                ml_rigObjects.append(i_aimStartTargetNull)
                
                self.mi_aimStartTargetNull = i_aimStartTargetNull
        
                #End AimTarget
                i_aimEndTargetNull = ml_jointList[0].duplicateTransform()
                i_aimEndTargetNull.addAttr('cgmType','aimTargetEnd',attrType='string',lock=True)
                i_aimEndTargetNull.doName()
                i_aimEndTargetNull.parent = ml_influenceJoints[0].mNode  
                ml_rigObjects.append(i_aimEndTargetNull)
                
                self.mi_aimEndTargetNull = i_aimEndTargetNull
                
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
                
            except Exception,err:raise Exception,"[Aim Target creation | error: {0}".format(err)             
            
                
            #if not i_startControl:i_startControl = i_anchorStart
            #if not i_endControl:i_endControl = i_anchorEnd
        def _func_constraints_(self):
            try:#Query ===========================================================================================
                i_anchorStart = self.mi_anchorStart
                i_aimStartNull = self.mi_aimStartNull
                i_attachStartNull = self.mi_attachStartNull
                
                i_anchorEnd = self.mi_anchorEnd
                i_aimEndNull = self.mi_aimEndNull
                i_attachEndNull = self.mi_attachEndNull
                
                i_startControl = self.mi_startControl
                i_endControl = self.mi_endControl
                
                ml_influenceJoints = self.ml_influenceJoints
            except Exception,err:raise Exception,"[Bring local | error: {0}".format(err)  
            
            try:#Create ===========================================================================================
                cBuffer = mc.orientConstraint([i_anchorStart.mNode,i_aimStartNull.mNode],
                                              i_attachStartNull.mNode,
                                              maintainOffset = True, weight = 1)[0]
                i_startOrientConstraint = cgmMeta.asMeta(cBuffer,'cgmNode',setClass=True)
                i_startOrientConstraint.interpType = 0
                
                self.mi_startOrientConstraint = i_startOrientConstraint
                
                cBuffer = mc.orientConstraint([i_anchorEnd.mNode,i_aimEndNull.mNode],
                                              i_attachEndNull.mNode,
                                              maintainOffset = True, weight = 1)[0]
                i_endOrientConstraint = cgmMeta.asMeta(cBuffer,'cgmNode',setClass=True)
                i_endOrientConstraint.interpType = 0 
                
                self.mi_endOrientConstraint = i_endOrientConstraint
            except Exception,err:raise Exception,"[Create | error: {0}".format(err)             
            
            try:#Blend ===========================================================================================
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
            except Exception,err:raise Exception,"[Blend setup | error: {0}".format(err)
                           
        def _func_segment_(self):
            try:#Query ===========================================================================================
                i_anchorStart = self.mi_anchorStart
                i_aimStartNull = self.mi_aimStartNull
                i_attachStartNull = self.mi_attachStartNull
                
                i_anchorEnd = self.mi_anchorEnd
                i_aimEndNull = self.mi_aimEndNull
                i_attachEndNull = self.mi_attachEndNull
                
                i_startControl = self.mi_startControl
                i_endControl = self.mi_endControl
                
                ml_influenceJoints = self.ml_influenceJoints
                l_segmentJoints = self.l_joints
            except Exception,err:raise Exception,"[Bring local | error: {0}".format(err)    
            
            try:#Segment ===========================================================================================
                d_segmentBuild = create_segment_curve(l_segmentJoints, useCurve = self.mi_useCurve, orientation = self.str_orientation,secondaryAxis = self.str_secondaryAxis,
                                                      baseName = self.str_baseName,connectBy = self.str_connectBy,
                                                      addMidTwist=self.b_addMidTwist, advancedTwistSetup = self.b_advancedTwistSetup, moduleInstance = self.mi_module)

                mi_segmentCurve = d_segmentBuild['mi_segmentCurve']
                #ml_drivenJoints = d_segmentBuild['ml_drivenJoints']
                mi_scaleBuffer = d_segmentBuild['mi_scaleBuffer']
                mi_segmentGroup = d_segmentBuild['mi_segmentGroup']
                #mPlug_extendTwist = d_segmentBuild['mPlug_extendTwist']
                
                self.d_segmentBuild = d_segmentBuild
                self.mi_segmentCurve = mi_segmentCurve
                self.mi_scaleBuffer = mi_scaleBuffer
                self.mi_segmentGroup = mi_segmentGroup
            except Exception,err:raise Exception,"[Segment curve| error: {0}".format(err)   
                        
            try:#SquashStretch ===========================================================================================
                if self.b_addSquashStretch:
                    self.log_info("adding squashStretch...")
                    rig_Utils.addSquashAndStretchToSegmentCurveSetup(mi_scaleBuffer.mNode,
                                                                     self.ml_joints,
                                                                     moduleInstance=self.mi_module)
            except Exception,err:raise Exception,"[SquashStretch setup | error: {0}".format(err) 
            
            try:#AdditiveScale ===========================================================================================
                if self.b_additiveScaleSetup:
                    self.log_info("additveScale setup ...")
                    rig_Utils.addAdditiveScaleToSegmentCurveSetup(mi_segmentCurve.mNode,orientation=self.str_orientation)
    
                    if self.b_additiveScaleConnect:
                        self.log_info("additveScale connect ...")                        
                        l_plugs = ['scaleStartUp','scaleStartOut','scaleEndUp','scaleEndOut']
                        for attr in l_plugs: 
                            log.info(attr)
                            if not mi_segmentCurve.hasAttr(attr):
                                mi_segmentCurve.select()
                                raise ValueError, "Segment curve missing attr: %s"%attr
    
                        l_attrPrefix = ['Start','End']
                        int_runningTally = 0
                        for i,i_ctrl in enumerate([i_startControl,i_endControl]):
                            log.info("{0} | {1}".format(i,i_ctrl.p_nameShort))
                            mPlug_outDriver = cgmMeta.cgmAttr(i_ctrl,"s%s"%self.str_controlOrientation[2])
                            mPlug_upDriver = cgmMeta.cgmAttr(i_ctrl,"s%s"%self.str_controlOrientation[1])
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
            except Exception,err:raise Exception,"[AdditiveScale setup | error: {0}".format(err) 
            
            try:#Twist ===========================================================================================
                if self.b_addTwist:
                    i_twistStartPlug = cgmMeta.cgmAttr(mi_segmentCurve.mNode,'twistStart',attrType='float',keyable=True) 
                    i_twistEndPlug = cgmMeta.cgmAttr(mi_segmentCurve.mNode,'twistEnd',attrType='float',keyable=True)
                    capAim = self.str_orientation[0].capitalize()
                    controlOrientation = self.str_controlOrientation
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
            except Exception,err:raise Exception,"[Connect Twist | error: {0}".format(err) 
            
            try:#Twist ===========================================================================================
                pass
            except Exception,err:raise Exception,"[Twist setup | error: {0}".format(err)             
        def _func_skin_(self):
            try:#Query ===========================================================================================
                if self.ml_influenceJoints:#if we have influence joints, we're gonna skin our curve
                    if deformers.isSkinned(self.mi_segmentCurve.mNode):
                        self.log_warning("Curve already skinned. Skipping...")
                    else:
                        i_skinCluster = cgmMeta.cgmNode(mc.skinCluster ([i_jnt.mNode for i_jnt in self.ml_influenceJoints],
                                                                    self.mi_segmentCurve.mNode,
                                                                    tsb=True,
                                                                    maximumInfluences = 3,
                                                                    normalizeWeights = 1,dropoffRate=2.5)[0])
        
                        i_skinCluster.addAttr('cgmName', self.str_baseName, lock=True)
                        i_skinCluster.addAttr('cgmTypeModifier','segmentCurve', lock=True)
                        i_skinCluster.doName()
            except Exception,err:raise Exception,"[Bring local | error: {0}".format(err)
            
        def _func_aim_(self):
            try:#Query ===========================================================================================
                i_anchorStart = self.mi_anchorStart
                i_aimStartNull = self.mi_aimStartNull
                i_attachStartNull = self.mi_attachStartNull
                
                i_anchorEnd = self.mi_anchorEnd
                i_aimEndNull = self.mi_aimEndNull
                i_attachEndNull = self.mi_attachEndNull
                
                i_startControl = self.mi_startControl
                i_endControl = self.mi_endControl
                
                ml_influenceJoints = self.ml_influenceJoints
                l_segmentJoints = self.l_joints
            except Exception,err:raise Exception,"[Bring local | error: {0}".format(err)  
            
            try:
                startAimTarget = self.mi_anchorEnd.mNode# i_anchorEnd.mNode
                endAimTarget = self.mi_anchorStart.mNode#i_anchorStart.mNode	
                cBuffer = mc.aimConstraint(startAimTarget,
                                           i_aimStartNull.mNode,
                                           maintainOffset = True, weight = 1,
                                           aimVector = self.v_aim,#aimVector,
                                           upVector = self.v_up,#upVector,
                                           worldUpObject = self.mi_startUpNull.mNode,#i_startUpNull.mNode,
                                           worldUpType = 'object' ) 
                self.mi_startAimConstraint = cgmMeta.asMeta(cBuffer[0],'cgmNode',setClass=True)
        
                cBuffer = mc.aimConstraint(endAimTarget,
                                           i_aimEndNull.mNode,
                                           maintainOffset = True, weight = 1,
                                           aimVector = self.v_aimNeg,#aimVectorNegative,
                                           upVector = self.v_up,#upVector,
                                           worldUpObject = self.mi_endUpNull.mNode,#i_endUpNull.mNode,
                                           worldUpType = 'object' ) 
                self.mi_endAimConstraint = cgmMeta.asMeta(cBuffer[0],'cgmNode',setClass=True)
            except Exception,err:raise Exception,"[constraints | error: {0}".format(err)
                
            
        def _func_finalize_(self):  
            try:#Store some necessary info to the segment curve =====================================================================================
                self.mi_segmentCurve.connectChildNode(self.mi_anchorStart,'anchorStart','segmentCurve')
                self.mi_segmentCurve.connectChildNode(self.mi_anchorEnd,'anchorEnd','segmentCurve')
                self.mi_segmentCurve.connectChildNode(self.mi_attachStartNull,'attachStart','segmentCurve')
                self.mi_segmentCurve.connectChildNode(self.mi_attachEndNull,'attachEnd','segmentCurve')
        
            except Exception,err:raise Exception,"[Data Store | error: {0}".format(err)

        
            try:#Return ========================================================================================
                md_return = {'mi_segmentCurve':self.mi_segmentCurve,'mi_anchorStart':self.mi_anchorStart,'mi_anchorEnd':self.mi_anchorEnd,#'mPlug_extendTwist':mPlug_extendTwist,
                             'mi_constraintStartAim':self.mi_startAimConstraint,'mi_constraintEndAim':self.mi_endAimConstraint}
                for k in self.d_segmentBuild.keys():
                    if k not in md_return.keys():
                        md_return[k] = self.d_segmentBuild[k]#...push to the return dict
                return md_return
            except Exception,err:raise Exception,"[data return | error: {0}".format(err)
        
        
    return fncWrap(*args,**kws).go()

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
    _str_funcName = 'createCGMSegment'
    log.info(">>> %s >> "%_str_funcName + "="*75)   

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
            raise StandardError,"%s >>Joint metaclassing | error : %s"%(_str_funcName,error)

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
        raise StandardError,"%s >> data gather | error: %s"%(_str_funcName,error)  

    try:#>>> Module instance =====================================================================================
        i_module = False
        try:
            if moduleInstance is not None:
                if moduleInstance.isModule():
                    i_module = moduleInstance    
                    log.info("%s >> module instance found: %s"%(_str_funcName,i_module.p_nameShort))		
        except:pass
    except Exception,error:
        raise StandardError,"%s >> Module check fail! | error: %s"%(_str_funcName,error)    

    try:#Build Transforms =====================================================================================
        #Start Anchor
        i_anchorStart = ml_jointList[0].duplicateTransform()
        i_anchorStart.addAttr('cgmType','anchor',attrType='string',lock=True)
        i_anchorStart.doName()
        i_anchorStart.parent = False  


        #End Anchor
        i_anchorEnd = ml_jointList[-1].duplicateTransform()
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
        i_aimStartNull = ml_jointList[0].duplicateTransform()
        i_aimStartNull.addAttr('cgmType','aim',attrType='string',lock=True)
        i_aimStartNull.doName()
        i_aimStartNull.parent = i_anchorStart.mNode   
        i_aimStartNull.rotateOrder = 0

        #End Aim
        i_aimEndNull = ml_jointList[-1].duplicateTransform()
        i_aimEndNull.addAttr('cgmType','aim',attrType='string',lock=True)
        i_aimEndNull.doName()
        i_aimEndNull.parent = i_anchorEnd.mNode 
        i_aimEndNull.rotateOrder = 0

        #=====================================
        """
	if addTwist:
	    #>>>Twist loc
	    #Start Aim
	    i_twistStartNull = ml_jointList[0].duplicateTransform()
	    i_twistStartNull.addAttr('cgmType','twist',attrType='string',lock=True)
	    i_twistStartNull.doName()
	    i_twistStartNull.parent = i_anchorStart.mNode     
	    ml_rigObjects.append(i_twistStartNull)

	    #End Aim
	    i_twistEndNull = ml_jointList[-1].duplicateTransform()
	    i_twistEndNull.addAttr('cgmType','twist',attrType='string',lock=True)
	    i_twistEndNull.doName()
	    i_twistEndNull.parent = i_anchorEnd.mNode  
	    ml_rigObjects.append(i_twistEndNull)"""

        #=====================================	
        #>>>Attach
        #Start Attach
        i_attachStartNull = ml_jointList[0].duplicateTransform()
        i_attachStartNull.addAttr('cgmType','attach',attrType='string',lock=True)
        i_attachStartNull.doName()
        i_attachStartNull.parent = i_anchorStart.mNode     

        #End Attach
        i_attachEndNull = ml_jointList[-1].duplicateTransform()
        i_attachEndNull.addAttr('cgmType','attach',attrType='string',lock=True)
        i_attachEndNull.doName()
        i_attachEndNull.parent = i_anchorEnd.mNode  

        #=====================================	
        #>>>Up locs
        i_startUpNull = ml_jointList[0].duplicateTransform()
        i_startUpNull.parent = i_anchorStart.mNode  
        i_startUpNull.addAttr('cgmType','up',attrType='string',lock=True)
        i_startUpNull.doName()
        ml_rigObjects.append(i_startUpNull)
        attributes.doSetAttr(i_startUpNull.mNode,'t%s'%orientation[2],baseDist)#We're gonna push these out

        #End
        i_endUpNull = ml_jointList[-1].duplicateTransform()
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
        i_aimStartTargetNull = ml_jointList[-1].duplicateTransform()
        i_aimStartTargetNull.addAttr('cgmType','aimTargetStart',attrType='string',lock=True)
        i_aimStartTargetNull.doName()
        i_aimStartTargetNull.parent = ml_influenceJoints[-1].mNode     
        ml_rigObjects.append(i_aimStartTargetNull)

        #End AimTarget
        i_aimEndTargetNull = ml_jointList[0].duplicateTransform()
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

def test(*args,**kws):
    """
    Root of the segment setup.
    Inspiriation from Jason Schleifer's work as well as http://faithofthefallen.wordpress.com/2008/10/08/awesome-spine-setup/
    on twist methods.

    :parameters:
        0 - 'jointList'(joints - None) | List or metalist of joints
        1 - 'useCurve'(nurbsCurve - None) | Which curve to use. If None. One Created
        2 - 'orientation'(string - zyx) | What is the joints orientation
        3 - 'secondaryAxis'(maya axis arg(ex:'yup') - yup) | Only necessary when no module provide for orientating
        4 - 'baseName'(string - None) | baseName string
        5 - 'connectBy'(string - trans) | How the joint will scale
        6 - 'advancedTwistSetup'(bool - False) | Whether to do the cgm advnaced twist setup
        7 - 'addMidTwist'(bool - True) | Whether to setup a mid twist on the segment
        8 - 'moduleInstance'(cgmModule - None) | cgmModule to use for connecting on build
        9 - 'extendTwistToEnd'(bool - False) | Whether to extned the twist to the end by default

    """   	    
    class fncWrap(cgmGeneral.cgmFuncCls):
        
        def __init__(self,*args,**kws):
            """
            """
            super(fncWrap, self).__init__(*args, **kws)
            self._str_funcName= "create_segment_curve"
            self._b_reportTimes = True
            self._b_autoProgressBar = 1
            self.__dataBind__(*args,**kws)
            self.report()
    return fncWrap(*args,**kws).go()
            
