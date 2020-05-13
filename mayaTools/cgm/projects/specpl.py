import cgm.core.cgm_Meta as cgmMeta
import cgm.core.cgm_RigMeta as RIGMETA
from cgm.core.cgmPy import validateArgs as VALID
import cgm.core.lib.attribute_utils as ATTR
from cgm.core.rigger.lib import rig_Utils as rUtils
###reload(rUtils)
from cgm.core.classes import NodeFactory as NodeF
import cgm.core.lib.distance_utils as DIST

import maya.cmds as mc
import pprint

import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
#-------------------------------------------------------------------


_d_l = {'fkJoints':[u'l_shoulder_fk', u'l_elbow_fk', u'l_wrist_fk'],
        'ikJoints':[u'l_shoulder_ik', u'l_elbow_ik', u'l_wrist_ik'],
        'blendJoints':[u'l_shoulder_blend', u'l_elbow_blend', u'l_wrist_blend'],
        'settings':'l_arm_root',
        'ikControl':'guardian_arm_l3_IK_anim_grp|guardian_arm_l3_IK_anim',
        'ikMid':'l_elbow_IK_anim'}

_d_r = {'fkJoints':[u'r_shoulder_fk', u'r_elbow_fk', u'r_wrist_fk'],
        'ikJoints':[u'r_shoulder_ik', u'r_elbow_ik', u'r_wrist_ik'],
        'blendJoints':[u'r_shoulder_blend', u'r_elbow_blend', u'r_wrist_blend'],
        'settings':'r_arm_root',
        'fkGroup':'r_arm_fk_grp',
        'ikGroup':'r_arm_ik_grp',
        'ikControl':'guardian_arm_r3_IK_anim_grp|guardian_arm_r3_IK_anim',
        'ikMid':'r_elbow_IK_anim'}



def buildFKIK(fkJoints = None,
              ikJoints = None,
              blendJoints = None,
              settings = None,
              orientation = 'zyx',
              ikControl = None,
              ikMid = None,
              mirrorDirection = 'Left',
              globalScalePlug = 'PLACER.scaleY',
              fkGroup = 'l_arm_fk_grp',
              ikGroup = 'l_arm_ik_grp',
              ikLen = 3):

    ml_blendJoints = cgmMeta.validateObjListArg(blendJoints,'cgmObject')
    ml_fkJoints = cgmMeta.validateObjListArg(fkJoints,'cgmObject')
    ml_ikJoints = cgmMeta.validateObjListArg(ikJoints,'cgmObject')

    mi_settings = cgmMeta.validateObjArg(settings,'cgmObject')

    aimVector = VALID.simpleAxis("%s+"%orientation[0]).p_vector#dictionary.stringToVectorDict.get("%s+"%self._go._jointOrientation[0])
    upVector = VALID.simpleAxis("%s+"%orientation[1]).p_vector#dictionary.stringToVectorDict.get("%s+"%self._go._jointOrientation[1])
    outVector = VALID.simpleAxis("%s+"%orientation[2]).p_vector#dictionary.stringToVectorDict.get("%s+"%self._go._jointOrientation[2])


    mi_controlIK = cgmMeta.validateObjArg(ikControl,'cgmObject')
    mi_controlMidIK = cgmMeta.validateObjArg(ikMid,'cgmObject')
    mPlug_lockMid = cgmMeta.cgmAttr(mi_controlMidIK,'lockMid',attrType='float',defaultValue = 0,keyable = True,minValue=0,maxValue=1.0)


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
                                           rpHandle=True, controlObject=mi_controlIK, addLengthMulti=True,
                                           globalScaleAttr=mPlug_globalScale.p_combinedName, stretch='translate',
                                           )	

    mi_armIKHandlePV = d_armPVReturn['mi_handle']
    ml_distHandlesPV = d_armPVReturn['ml_distHandles']
    mi_rpHandlePV = d_armPVReturn['mi_rpHandle']
    mPlug_lockMid = d_armPVReturn['mPlug_lockMid']
    
  

    mi_armIKHandlePV.parent = mi_controlIK.mNode#armIK to ball		
    ml_distHandlesPV[-1].parent = mi_controlIK.mNode#arm distance handle to ball	
    ml_distHandlesPV[0].parent = mi_settings#hip distance handle to deform group
    ml_distHandlesPV[1].parent = mi_controlMidIK.mNode#elbow distance handle to midIK
    mi_rpHandlePV.parent = mi_controlMidIK
    

    #RP handle	
    #mi_rpHandlePV.doCopyNameTagsFromObject(self._go._mi_module.mNode, ignore = ['cgmName','cgmType'])
    mi_rpHandlePV.addAttr('cgmName','elbowPoleVector',attrType = 'string')
    mi_rpHandlePV.doName()
    
    #Mid fix
    #=========================================================================================			
    mc.move(0,0,-25,mi_controlMidIK.mNode,r=True, rpr = True, ws = True, wd = True)#move out the midControl to fix the twist from

    #>>> Fix our ik_handle twist at the end of all of the parenting
    #rUtils.IKHandle_fixTwist(mi_armIKHandlePV)#Fix the twist
    
    log.info("rUtils.IKHandle_fixTwist('%s')"%mi_armIKHandlePV.getShortName())
    #Register our snap to point before we move it back
    i_ikMidMatch = RIGMETA.cgmDynamicMatch(dynObject=mi_controlMidIK,
                                           dynPrefix = "FKtoIK",
                                           dynMatchTargets=ml_blendJoints[1]) 	
    #>>> Reset the translations
    mi_controlMidIK.translate = [0,0,0]

    #Move the lock mid and add the toggle so it only works with show elbow on
    #mPlug_lockMid.doTransferTo(mi_controlMidIK.mNode)#move the lock mid	

    #Parent constain the ik wrist joint to the ik wrist
    #=========================================================================================				
    mc.orientConstraint(mi_controlIK.mNode,ml_ikJoints[ikLen-1].mNode, maintainOffset = True)	
    


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


#====================================================================================================
#>>> Twist
#====================================================================================================
_dTwistNodes_l = {'blendJoints':[u'l_shoulder_blend', u'l_elbow_blend', u'l_wrist_blend'],
                  'fkControls':[u'l_shoulder_fk', u'l_elbow_fk', u'l_wrist_fk'],
                  'ikControl':'guardian_arm_l3_IK_anim',
                  'settings':'l_arm_root',
                  'segmentHandles':[u'l_shoulder_blend|guardian_arm_l1_IK_grp|guardian_arm_l1_IK_anim',
                                    u'l_elbow_blend|guardian_arm_l2_IK_grp|guardian_arm_l2_IK_anim',
                                    u'guardian_arm_l3_IK_sub_anim'],
                  'rootGroup':'l_arm_root_grp',
                  'curve':'l_arm_crv_splineIKCurve',
                  'baseName':'l_arm'}

def twist_drivers(settings = None,
                  orientation = 'zyx',
                  blendJoints = None,
                  ikControl = None,
                  fkControls = None,
                  segmentHandles = None,                                    
                  mirrorDirection = 'left',
                  rootGroup = 'l_arm_root_grp',
                  curve = None,
                  baseName = 'l_arm'):   
    
    mi_settings = cgmMeta.validateObjArg(settings,'cgmObject')
    mi_ikControl = cgmMeta.validateObjArg(ikControl,'cgmObject')
    mi_curve = cgmMeta.validateObjArg(curve,'cgmObject')
    mPlug_stableIKStartIn = cgmMeta.cgmAttr(mi_settings,"in_stableIKStart" , attrType='float' , lock = True)
    mPlug_worldIKEndIn = cgmMeta.cgmAttr(mi_settings,"in_worldIKEnd" , attrType='float' , lock = True)
    
    outVector = VALID.simpleAxis(orientation[2]).p_vector
    upVector = VALID.simpleAxis(orientation[1]).p_vector
    ml_blendJoints = cgmMeta.validateObjListArg(blendJoints,'cgmObject')
    ml_fkControls = cgmMeta.validateObjListArg(fkControls,'cgmObject')
    ml_segmentHandles = cgmMeta.validateObjListArg(segmentHandles,'cgmObject')
    
    mi_rootGroup = cgmMeta.validateObjArg(rootGroup,'cgmObject')
    str_twistOrientation = "r{0}".format(orientation[0])
    str_twistOrientationSeg = "rx"
    
        
    #>>>Collect our drivers ======================================================================================
    #...setup initial attributes
    mPlug_FKon = cgmMeta.cgmAttr(mi_settings,'result_FKon')	
    mPlug_IKon = cgmMeta.cgmAttr(mi_settings,'result_IKon')	                    
    mPlug_TwistStartResult = cgmMeta.cgmAttr(mi_settings,'result_twistStart' , attrType='float' , defaultValue = 1 , lock = True)
    mPlug_TwistEndResult = cgmMeta.cgmAttr(mi_settings,'result_twistEnd' , attrType='float' , defaultValue = 1 , lock = True)

    mPlug_TwistStartFKResult = cgmMeta.cgmAttr(mi_settings,'result_twistStartFK', attrType='float' , defaultValue = 1 , lock = True)
    mPlug_TwistEndFKResult = cgmMeta.cgmAttr(mi_settings,'result_twistEndFK' , attrType='float' , defaultValue = 1 , lock = True)
    mPlug_TwistStartFKSum = cgmMeta.cgmAttr(mi_settings,'sum_twistStartFK' , attrType='float' , defaultValue = 1 , lock = True)
    mPlug_TwistEndFKSum = cgmMeta.cgmAttr(mi_settings,'sum_twistEndFK' , attrType='float' , defaultValue = 1 , lock = True)

    mPlug_TwistStartIKResult = cgmMeta.cgmAttr(mi_settings,'result_twistStartIK' ,hidden=True, attrType='float' , defaultValue = 1 , lock = True)
    mPlug_TwistEndIKResult = cgmMeta.cgmAttr(mi_settings,'result_twistEndIK' ,hidden=True, attrType='float' , defaultValue = 1 , lock = True)
    mPlug_TwistStartIKSum = cgmMeta.cgmAttr(mi_settings,'sum_twistStartIK' , attrType='float' , defaultValue = 1 , lock = True)
    mPlug_TwistEndIKSum = cgmMeta.cgmAttr(mi_settings,'sum_twistEndIK' , attrType='float' , defaultValue = 1 , lock = True)

    #start twist driver
    l_startDrivers = ["%s.%s"%(ml_segmentHandles[0].getShortName(),str_twistOrientationSeg)]
    l_startDrivers.append("%s"%mPlug_TwistStartFKResult.p_combinedShortName )
    l_startDrivers.append("%s"%mPlug_TwistStartIKResult.p_combinedShortName )	    
    l_fkStartDrivers = []
    l_ikStartDrivers = []

    #end twist driver
    l_endDrivers = ["%s.%s"%(ml_segmentHandles[-1].getShortName(),str_twistOrientationSeg)]	    
    l_endDrivers.append("%s"%mPlug_TwistEndFKResult.p_combinedShortName )
    l_endDrivers.append("%s"%mPlug_TwistEndIKResult.p_combinedShortName )	    
    l_fkEndDrivers = []
    l_ikEndDrivers = []
    
    
    #Fk end
    for mDriver in ml_fkControls[1:]:
        l_fkEndDrivers.append("%s.%s"%(mDriver.getShortName(),str_twistOrientation))     
    
    #IK end:
    l_ikStartDrivers.append(mPlug_stableIKStartIn.p_combinedShortName)
    l_fkStartDrivers.append(mPlug_stableIKStartIn.p_combinedShortName)
    l_ikEndDrivers.append(mPlug_worldIKEndIn.p_combinedShortName)    
    
    
    #...collect drivers
    pprint.pprint(vars())
    
    #...args
    str_ArgStartDrivers_Result = "%s = %s"%(mPlug_TwistStartResult.p_combinedShortName," + ".join(l_startDrivers))
    log.info("start sum arg: '%s'"%(str_ArgStartDrivers_Result))
    NodeF.argsToNodes(str_ArgStartDrivers_Result).doBuild()		

    if l_ikStartDrivers:
        str_ArgIKStart_Sum = "%s = %s"%(mPlug_TwistStartIKSum.p_combinedShortName," + ".join(l_ikStartDrivers))
        log.info("start IK sum arg: '%s'"%(str_ArgIKStart_Sum))
        NodeF.argsToNodes(str_ArgIKStart_Sum).doBuild()		
        str_ArgIKStart_Result = "%s = %s * %s"%(mPlug_TwistStartIKResult.p_combinedShortName,mPlug_TwistStartIKSum.p_combinedShortName,mPlug_IKon.p_combinedShortName)
        log.info("start IK result arg: '%s'"%(str_ArgIKStart_Result))
        NodeF.argsToNodes(str_ArgIKStart_Result).doBuild()		

    if l_fkStartDrivers:
        str_ArgFKStart_Sum = "%s = %s"%(mPlug_TwistStartFKSum.p_combinedShortName," + ".join(l_fkStartDrivers))
        log.info("start FK sum arg: '%s'"%(str_ArgFKStart_Sum))
        NodeF.argsToNodes(str_ArgFKStart_Sum).doBuild()		
        str_ArgFKStart_Result = "%s = %s * %s"%(mPlug_TwistStartFKResult.p_combinedShortName,mPlug_TwistStartFKSum.p_combinedShortName,mPlug_FKon.p_combinedShortName)
        log.info("start FK result arg: '%s'"%(str_ArgFKStart_Result))
        NodeF.argsToNodes(str_ArgFKStart_Result).doBuild()		
    #><
    log.info("#"+"-"*70)
    str_ArgEndDrivers = "%s = %s"%(mPlug_TwistEndResult.p_combinedShortName," + ".join(l_endDrivers))
    log.info("end sum arg: '%s'"%(str_ArgEndDrivers))	    
    NodeF.argsToNodes(str_ArgEndDrivers).doBuild()		

    if l_ikEndDrivers:
        str_ArgIKEnd_Sum = "%s = %s"%(mPlug_TwistEndIKSum.p_combinedShortName," + ".join(l_ikEndDrivers))
        log.info("end IK sum arg: '%s'"%(str_ArgIKEnd_Sum))
        NodeF.argsToNodes(str_ArgIKEnd_Sum).doBuild()				
        str_ArgIKEnd_Result = "%s = %s * %s"%(mPlug_TwistEndIKResult.p_combinedShortName,mPlug_TwistEndIKSum.p_combinedShortName,mPlug_IKon.p_combinedShortName)
        log.info("end IK result arg: '%s'"%(str_ArgIKEnd_Result))
        NodeF.argsToNodes(str_ArgIKEnd_Result).doBuild()				
        
    if l_fkEndDrivers:
        str_ArgFKEnd_Sum = "%s = %s"%(mPlug_TwistEndFKSum.p_combinedShortName," + ".join(l_fkEndDrivers))
        log.info("end FK sum arg: '%s'"%(str_ArgFKEnd_Sum))
        NodeF.argsToNodes(str_ArgFKEnd_Sum).doBuild()				
        str_ArgFKEnd_Result = "%s = %s * %s"%(mPlug_TwistEndFKResult.p_combinedShortName,mPlug_TwistEndFKSum.p_combinedShortName,mPlug_FKon.p_combinedShortName)
        log.info("end FK result arg: '%s'"%(str_ArgFKEnd_Result))
        NodeF.argsToNodes(str_ArgFKEnd_Result).doBuild()				

    log.info("#"+"="*70)
    mPlug_TwistStartResult.doConnectOut("%s.twistStart"%mi_curve.mNode)
    mPlug_TwistEndResult.doConnectOut("%s.twistEnd"%mi_curve.mNode)    
    
    return




_dshoulderTwist_l = {'blendJoints':[u'l_shoulder_blend', u'l_elbow_blend', u'l_wrist_blend'],
                     'settings':'l_arm_root',
                     'segmentHandle':'l_elbow_seg_anim',
                     'rootGroup':'l_arm_root_grp',
                     'baseName':'l_arm'}

def shoulderTwist(settings = None,
                  orientation = 'xyz',
                  blendJoints = None,
                  mirrorDirection = 'Left',
                  rootGroup = 'l_arm_root_grp',
                  segmentHandle = 'l_elbow_seg_anim',
                  baseName = 'l_arm'):   
    
    mi_settings = cgmMeta.validateObjArg(settings,'cgmObject')
    #mPlug_worldIKStartIn = cgmMeta.cgmAttr(mi_settings,"in_worldIKStart" , attrType='float' , lock = True)
    outVector = VALID.simpleAxis(orientation[2]).p_vector
    upVector = VALID.simpleAxis(orientation[1]).p_vector
    ml_blendJoints = cgmMeta.validateObjListArg(blendJoints,'cgmObject')
    mi_mainSegmentHandle = cgmMeta.validateObjArg(segmentHandle,'cgmObject')
    mi_rootGroup = cgmMeta.validateObjArg(rootGroup,'cgmObject')
    
    i_target = mi_settings
    pprint.pprint(vars())
    
    """
    try:
        mi_parentRigNull = self._go._mi_module.moduleParent.rigNull
        i_target = mi_parentRigNull.msgList_get('moduleJoints')[0]	
    except Exception,error:
        raise Exception,"failed to find target | %s"%(error)"""	  
    
    #ml_handleJoints = self._go._mi_module.rig_getHandleJoints()
    fl_baseDist = DIST.get_distance_between_points(ml_blendJoints[0].p_position, ml_blendJoints[-1].p_position)

    #Create joints -------------------------------------------------------------------
    i_startRoot = ml_blendJoints[0].doDuplicate(inputConnections = False)
    i_startRoot.addAttr('cgmName',baseName)	
    i_startRoot.addAttr('cgmTypeModifier','twistDriver')
    i_startRoot.doName()
    i_startRoot.parent = mi_rootGroup

    i_startEnd = ml_blendJoints[0].doDuplicate(inputConnections = False)
    i_startEnd.addAttr('cgmTypeModifier','twistDriverEnd')
    i_startEnd.doName() 
    i_startEnd.parent = i_startRoot.mNode

    i_driver = ml_blendJoints[0].doDuplicate(inputConnections = False)
    i_driver.addAttr('cgmName',baseName)	
    i_driver.addAttr('cgmTypeModifier','twistDriverResult')
    i_driver.doName()
    i_driver.parent = ml_blendJoints[0]#parent to the root blend to get it in the same space

    #Loc -------------------------------------------------------------------
    i_upLoc = i_startRoot.doLoc()
    i_upLoc.parent = mi_rootGroup
    #i_upLoc.parent = self._go._i_constrainNull.mNode#parent
    #self._go.connect_toRigGutsVis(i_upLoc)

    ml_twistObjects = [i_startRoot,i_startEnd,i_upLoc,i_driver]
    #i_upLoc.__setattr__('t%s'%self._go._jointOrientation[1],fl_baseDist)	
    ATTR.set(i_upLoc.mNode,'t%s'%orientation[1],fl_baseDist)
    #Move aim joint out
    #i_startEnd.__setattr__('t%s'%self._go._jointOrientation[0],fl_baseDist)
    ATTR.set(i_startEnd.mNode,'t%s'%orientation[0],fl_baseDist)

    #=============================================================================
    #setup stable shoulder rotate group  
    i_rotGroup = mi_rootGroup.doCreateAt()
    i_rotGroup.addAttr('cgmType','stableShoulderTwistRotGroup')
    i_rotGroup.doName()
    ml_twistObjects.append(i_rotGroup)
    i_upLoc.parent = i_rotGroup.mNode

    i_rotGroup.parent = mi_rootGroup
    mc.parentConstraint(i_target.mNode,i_upLoc.mNode,maintainOffset = True)

    #=============================================================================
    #Create IK handle
    pos = i_startRoot.getPosition()
    mc.move (0,pos[1],pos[2], i_startRoot.mNode, ws = True)#zero out aim joint's x pos

    buffer = mc.ikHandle( sj=i_startRoot.mNode, ee=i_startEnd.mNode,
                          solver = 'ikRPsolver', forceSolver = True,
                          snapHandleFlagToggle=True )  

    #>>> Name
    str_baseName = baseName + "_startTwistDriver"
    i_ik_handle = cgmMeta.cgmObject(buffer[0],setClass=True)
    i_ik_handle.addAttr('cgmName',str_baseName ,attrType='string',lock=True)    
    i_ik_handle.doName()
    i_ik_handle.parent = mi_rootGroup
    mc.pointConstraint(mi_mainSegmentHandle.mNode,i_ik_handle.mNode,maintainOffset = False)

    ml_twistObjects.append(i_ik_handle)

    i_ik_effector = cgmMeta.asMeta(buffer[1],'cgmNode',setClass=True)
    i_ik_effector.addAttr('cgmName',str_baseName,attrType='string',lock=True)    
    i_ik_effector.doName()

    cBuffer = mc.poleVectorConstraint(i_upLoc.mNode,i_ik_handle.mNode)#Polevector	
    rUtils.IKHandle_fixTwist(i_ik_handle.mNode)#Fix the wist

    mc.orientConstraint(i_startRoot.mNode,i_driver.mNode,maintainOffset = True, skip = [orientation[1],orientation[2]])
    cgmMeta.cgmAttr(mi_settings,'in_stableIKStart').doConnectIn("%s.r%s"%(i_driver.mNode,orientation[0]))
    
    #self._go.connect_toRigGutsVis(ml_twistObjects)#connect to guts vis switches
    return i_driver

_dwristTwist_l = {'blendJoints':[u'l_shoulder_blend', u'l_elbow_blend', u'l_wrist_blend'],
                  'settings':'l_arm_root',
                  'mirrorDirection':'left',
                  'ikControl':'guardian_arm_l3_IK_anim',
                  'segmentHandle':'l_elbow_seg_anim',
                  'rootGroup':'l_arm_root_grp',
                  'baseName':'l_arm'}

def wristTwist(settings = None,
               orientation = 'zyx',
               blendJoints = None,
               mirrorDirection = 'left',
               ikControl = None,
               rootGroup = 'l_arm_root_grp',
               segmentHandle = 'l_elbow_seg_anim',
               baseName = 'l_arm'):   
    
    mi_settings = cgmMeta.validateObjArg(settings,'cgmObject')
    mi_ikControl = cgmMeta.validateObjArg(ikControl,'cgmObject')
    mPlug_worldIKStartIn = cgmMeta.cgmAttr(mi_settings,"in_worldIKStart" , attrType='float' , lock = True)
    outVector = VALID.simpleAxis(orientation[2]).p_vector
    upVector = VALID.simpleAxis(orientation[1]).p_vector
    ml_blendJoints = cgmMeta.validateObjListArg(blendJoints,'cgmObject')
    mi_mainSegmentHandle = cgmMeta.validateObjArg(segmentHandle,'cgmObject')
    mi_rootGroup = cgmMeta.validateObjArg(rootGroup,'cgmObject')
    fl_baseDist = DIST.get_distance_between_points(ml_blendJoints[0].p_position, ml_blendJoints[-1].p_position)
    
    i_target = mi_settings
    
    pprint.pprint(vars())
    
    #ml_rigHandleJoints = self._go._get_handleJoints()	
    
    #i_targetJoint = ml_rigHandleJoints[2]#This should be the wrist
    i_targetJoint = ml_blendJoints[2]#This should be the wrist
    
    i_blendWrist = ml_blendJoints[2]


    #Create joints
    i_startRoot = i_targetJoint.doDuplicate(inputConnections = False)
    i_startRoot.addAttr('cgmName',baseName)	
    i_startRoot.addAttr('cgmTypeModifier','endtwistDriver')
    i_startRoot.doName()
    i_startEnd = i_targetJoint.doDuplicate(inputConnections = False)
    i_startEnd.addAttr('cgmTypeModifier','endtwistDriverEnd')
    i_startEnd.doName()    

    i_upLoc = i_startRoot.doLoc()	
    i_upLoc.parent = mi_rootGroup#parent

    #Restore out lists

    i_startEnd.parent = i_startRoot.mNode
    ml_twistObjects = [i_startRoot,i_startEnd,i_upLoc]

    if mirrorDirection == 'left':#if right, rotate the pivots
        #i_upLoc.__setattr__('t%s'%self._go._jointOrientation[2],fl_baseDist)
        ATTR.set(i_upLoc.mNode,'t%s'%orientation[2],fl_baseDist)

    else:
        #i_upLoc.__setattr__('t%s'%self._go._jointOrientation[2],-fl_baseDist)
        ATTR.set(i_upLoc.mNode,'t%s'%orientation[2],-fl_baseDist)


    #i_startEnd.__setattr__('t%s'%self._go._jointOrientation[0],-(fl_baseDist))
    ATTR.set(i_startEnd.mNode,'t%s'%orientation[0],-fl_baseDist)

    #i_startRoot.parent = ml_ikJoints[1].mNode
    i_startRoot.parent = ml_blendJoints[1].mNode
    i_startRoot.rotateOrder = 0 #xyz
    mc.pointConstraint(i_blendWrist.mNode,i_startRoot.mNode,mo=True)#constrain

   
    #=============================================================================
    #setup stable wrist rotate group  
    i_rotGroup = mi_ikControl.doCreateAt()
    i_rotGroup.addAttr('cgmType','stableShoulderTwistRotGroup')
    i_rotGroup.doName()
    ml_twistObjects.append(i_rotGroup)
    i_upLoc.parent = i_rotGroup.mNode

    """
    NodeF.argsToNodes("%s.ry = -%s.ry"%(i_rotGroup.p_nameShort,
                        mi_controlIK.p_nameShort)).doBuild()	
    NodeF.argsToNodes("%s.rx = -%s.rx"%(i_rotGroup.p_nameShort,
                        mi_controlIK.p_nameShort)).doBuild()	"""
    i_rotGroup.parent = i_blendWrist.mNode
    #mc.orientConstraint(mi_ikControl.mNode,i_rotGroup.mNode,skip = ["%s"%r for r in orientation[1:]])
    mc.orientConstraint(ml_blendJoints[2].mNode,i_rotGroup.mNode,skip = ["y","z"])

    #=============================================================================
    #Create IK handle
    buffer = mc.ikHandle( sj=i_startRoot.mNode, ee=i_startEnd.mNode,
                          solver = 'ikRPsolver', forceSolver = True,
                          snapHandleFlagToggle=True )  

    #>>> Name
    str_baseName = baseName + "_endTwistDriver"
    i_ik_handle = cgmMeta.asMeta(buffer[0],'cgmObject',setClass=True)
    i_ik_handle.addAttr('cgmName',str_baseName ,attrType='string',lock=True)    
    i_ik_handle.doName()
    #i_ik_handle.parent = self._go._i_rigNull.mNode
    i_ik_handle.parent = mi_rootGroup
    mc.pointConstraint(ml_blendJoints[1].mNode,i_ik_handle.mNode)

    ml_twistObjects.append(i_ik_handle)

    i_ik_effector = cgmMeta.asMeta(buffer[1],'cgmNode',setClass=True)
    i_ik_effector.addAttr('cgmName',str_baseName,attrType='string',lock=True)    
    i_ik_effector.doName()

    cBuffer = mc.poleVectorConstraint(i_upLoc.mNode,i_ik_handle.mNode)#Polevector	
    rUtils.IKHandle_fixTwist(i_ik_handle.mNode)#Fix the wist

    cgmMeta.cgmAttr(mi_settings,'in_worldIKEnd').doConnectIn("%s.r%s"%(i_startRoot.mNode,orientation[0]))


_dmatrixTwist_l = {'startCon':'l_shoulder_blend|guardian_arm_l1_IK_grp|guardian_arm_l1_IK_anim',
                  'endCon':'guardian_arm_l3_IK_sub_anim',
                  'splineIK':'l_arm_crv_splineIKCurve',
                  'baseName':'l_arm'}

def matrixTwist(startCon = None,
                endCon = None,
                splineIK = None,
                baseName = None):   
    
    mult1 = mc.createNode( 'multMatrix' )
    mult2 = mc.createNode( 'multMatrix' ) 
    
    decomp1 = mc.createNode( 'decomposeMatrix' )
    decomp2 = mc.createNode( 'decomposeMatrix' )
    
    startConParent = mc.listRelatives(startCon, parent=True, fullPath=True)[0]
    
    mc.connectAttr( '%s.worldMatrix[0]' % startCon, '%s.matrixIn[0]' % mult1 )
    mc.connectAttr( '%s.worldInverseMatrix[0]' % startConParent, '%s.matrixIn[1]' % mult1 )
    
    mc.connectAttr( '%s.matrixSum' % mult1, '%s.inputMatrix' % decomp1 ) 
    mc.connectAttr( '%s.outputRotate.outputRotateX' % decomp1, '%s.twistStart' % splineIK ) 
    
    mc.connectAttr( '%s.worldMatrix[0]' % endCon, '%s.matrixIn[0]' % mult2 )
    mc.connectAttr( '%s.worldInverseMatrix[0]' % startConParent, '%s.matrixIn[1]' % mult2 )
    
    mc.connectAttr( '%s.matrixSum' % mult2, '%s.inputMatrix' % decomp2 ) 
    mc.connectAttr( '%s.outputRotate.outputRotateX' % decomp2, '%s.twistEnd' % splineIK )
    
_d_attach_l = {'joints' : [u'arm1_l2_seg',
                  u'arm2_l_seg',
                  u'arm3_l_seg',
                  u'arm4_l_seg',
                  u'arm5_l_seg',
                  u'joint1_seg'],
      'useCurve' : 'l_arm_crv',
      'baseName' : 'l_armSegment'}
_d_attach_r = {'joints' : [u'arm1_r1_seg',
                           u'arm2_r_seg',
                           u'arm3_r_seg',
                           u'arm4_r_seg',
                           u'arm5_r_seg',
                           u'joint2_seg'],
               'useCurve' : 'r_arm_crv',
               'baseName' : 'r_armSegment'}
import cgm.core.lib.curve_Utils as CURVES
import cgm.core.cgm_Meta as cgmMeta
import cgm.core.lib.attribute_utils as ATTR
def attachToCurve(joints = None,
                  useCurve = None,
                  baseName = None):
    _str_func = 'attachToCurve'
    mi_curve = cgmMeta.validateObjArg(useCurve,'cgmObject')
    ml_joints = cgmMeta.validateObjListArg(joints,'cgmObject')
    l_param = []
    
    for mJnt in ml_joints:
        param = CURVES.getUParamOnCurveFromObj(mJnt.mNode, mi_curve.mNode) 
        log.debug("|{0}| >> {1}...".format(_str_func,param))                
        l_param.append(param) 
    
    
    ml_pointOnCurveInfos = []
    
    str_shape = mi_curve.getShapes(asMeta=False)[0]
    for i,mJnt in enumerate(ml_joints):   
        if not l_param:
            param = CURVES.getUParamOnCurveFromObj(mJnt.mNode, mi_curve.mNode)  
        else:
            param = l_param[i]
            
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
        
        mi_loc = mJnt.doLoc()
        
        #Connect things
        ATTR.connect(ml_pointOnCurveInfos[i].mNode+'.position',mi_loc.mNode+'.translate')
        mc.pointConstraint(mi_loc.mNode, mJnt.mNode,maintainOffset = True)
        
        
#===================================================================================================
# >> SegmentDirect
#===================================================================================================

_d_segmentDirect_l = {'joints':[u'arm1_l',
                                u'arm1_l|arm2_l',
                                u'arm1_l|arm2_l|arm3_l',
                                u'arm1_l|arm2_l|arm3_l|arm4_l',
                                u'arm1_l|arm2_l|arm3_l|arm4_l|arm5_l',
                                u'arm1_l|arm2_l|arm3_l|arm4_l|arm5_l|joint1',
                                u'arm1_l|arm2_l|arm3_l|arm4_l|arm5_l|joint1|wrist1_l']}
_d_segmentDirect_r = {'joints':[u'arm1_r', u'arm2_r', u'arm3_r', u'arm4_r', u'joint2', u'wrist1_r']}

import cgm.core.lib.rigging_utils as RIG
def setupDirectOrbs(joints=None):
    ml_joints = cgmMeta.validateObjListArg(joints, 'cgmObject')

    for mJnt in ml_joints:
        _trans = RIG.create_at(mJnt.mNode)
        mTrans = cgmMeta.validateObjArg(_trans,'cgmObject')
        #ATTR.set_message(mJnt.mNode, 'cgmSource',mTrans.mNode)
        mJnt.doStore('cgmSource',mTrans)
        mTrans.rename("{0}_anim".format(mJnt.p_nameBase))

        mTrans.doGroup(True)
        
        
_d_connectJointsToHandles = {'joints':[u'arm1_l',
                                       u'arm1_l|arm2_l',
                                       u'arm1_l|arm2_l|arm3_l',
                                       u'arm1_l|arm2_l|arm3_l|arm4_l',
                                       u'arm1_l|arm2_l|arm3_l|arm4_l|arm5_l',
                                       u'arm1_l|arm2_l|arm3_l|arm4_l|arm5_l|joint1',
                                       u'arm1_r',
                                       u'arm2_r',
                                       u'arm3_r',
                                       u'arm4_r',
                                       u'arm5_r',
                                       u'joint2'] }

def connectJointsToDirect(joints=None):
    ml_joints = cgmMeta.validateObjListArg(joints, 'cgmObject')
    
    for mJnt in ml_joints:
        _source = ATTR.get_message(mJnt.mNode,'cgmSource')
        mc.parentConstraint(_source, mJnt.mNode, maintainOffset = True)
        
_d_handlesDynP = {'controls':[u'arm1_l_anim',
                              u'arm2_l_anim',
                              u'arm3_l_anim',
                              u'arm4_l_anim',
                              u'arm5_l_anim',
                              u'joint1_anim',
                              
                              u'arm1_r_anim',
                              u'arm2_r_anim',
                              u'arm3_r_anim',
                              u'arm4_r_anim',
                              u'arm5_r_anim',
                              u'joint2_anim'],
                    'segmentJoints':[u'arm1_l2_seg',
                                     u'arm2_l_seg',
                                     u'arm3_l_seg',
                                     u'arm4_l_seg',
                                     u'arm5_l_seg',
                                     u'joint1_seg',
                                     
                                     u'arm1_r1_seg',
                                         u'arm2_r_seg',
                                         u'arm3_r_seg',
                                         u'arm4_r_seg',
                                         u'arm5_r_seg',
                                         u'joint2_seg'],
                    'sharedTargets':['PLACER']
                      } 
        
def connectDirectToSegment(controls = None,
                           segmentJoints = None,
                           sharedTargets = None):
    ml_controls = cgmMeta.validateObjListArg(controls,'cgmObject')
    ml_segmentJoints = cgmMeta.validateObjListArg(segmentJoints,'cgmObject')
    
    if len(ml_controls) != len(ml_segmentJoints):
        raise ValueError,'Differing lengths'
    
    for i,mCon in enumerate(ml_controls):
        l_targets = [ml_segmentJoints[i].mNode, 'PLACER']
        dynGroup = RIGMETA.cgmDynParentGroup(dynChild = mCon.mNode)
        for t in l_targets:
            dynGroup.addDynParent(t)
        dynGroup.rebuild()
        
        
def createAndContrainRigFromSkinJoints(joints = []):
    pprint.pprint(vars())    
    
    ml_joints = cgmMeta.validateObjListArg(joints,'cgmObject')
    ml_new = []
    for i,mObj in enumerate(ml_joints):
        mDup = mObj.doDuplicate(po=True)
        mDup.rename( mObj.p_nameBase.replace('sknj','rig') )
        mDup.connectChildNode(mObj,'skinJoin','rigJoint')
        ml_new.append(mObj)
        if i > 0:
            if ml_joints[i].parent:
                _buffer = ml_joints[i].getParent(asMeta=True).getMessage('rigJoint')
                if _buffer:
                    mDup.parent =_buffer[0]
        
        mc.pointConstraint([mDup.mNode], mObj.mNode, maintainOffset = True)
        mc.orientConstraint([mDup.mNode], mObj.mNode, maintainOffset = True)
    return ml_new

def create_lengthSetup(joints = [],
                       lengthAxis = 'x+',
                       lengthAttr = 'stretch',
                       zeroGroup = True,
                       mode = 'children'):
    """
    Should be a joint chain to work properly
    """
    ml_joints = cgmMeta.validateObjListArg(joints,'cgmObject')
    ml_new = []
    
    if mode == 'children':
        """Do  this for each child"""
        
        for mObj in ml_joints:
            
            ml_children = mObj.getChildren(asMeta = True)
            if not ml_children:
                log.info("no children on : {0}".format(mObj.mNode))
                continue
            
            mObj.addAttr(lengthAttr,value = 1.0)
            for mChild in ml_children:
                if zeroGroup:
                    mMover = mChild.doGroup(True,asMeta=True)
                else:
                    mMover = mChild
                    
                mMover.addAttr('baseLength',value = mMover.tx)
                
                arg_md = "{0}.tx = {1}.{2} * {0}.baseLength".format(mMover.p_nameShort, mObj.p_nameShort, lengthAttr)
                NodeF.argsToNodes(arg_md).doBuild()                
    else:
        """heirarchy mode"""
        for i,mObj in enumerate(ml_joints[:-1]):
            mChild = ml_joints[i+1]
            
            if zeroGroup:
                mMover = mChild.doGroup(True,asMeta=True)
            else:
                mMover = mChild
                
            mObj.addAttr(lengthAttr,value = 1.0)
            mMover.addAttr('baseLength',value = mMover.tx)
            
            arg_md = "{0}.tx = {1}.{2} * {0}.baseLength".format(mMover.mNode, mObj.mNode, lengthAttr)
            NodeF.argsToNodes(arg_md).doBuild()
            
def setup_fingers(curves=[]):
    """Works of created control curves to setup fingers"""
    ml_curves = cgmMeta.validateObjListArg(curves,'cgmObject')
    ml_joints = []
    for mObj in ml_curves:
        _source = ATTR.get_message(mObj.mNode,'cgmSource')
        if not _source:
            log.info("no cgmSource dat on : {0}".format(mObj.mNode))
            continue
        
        mSource = cgmMeta.validateObjArg(_source)
        mGroup = mSource.doGroup(True,True,asMeta=True,typeModifier = 'zero')
        log.info(mSource)
        ml_joints.append(mSource)
        RIG.shapeParent_in_place(mSource.mNode, mObj.mNode)
        
        create_lengthSetup(mSource.mNode)
        mSource.radius = 0
        #cgmMeta.cgmNode().setAttrFlags
        mSource.setAttrFlags(['radius','scale','v'],lock=True, visible=False)
        mObj.v = False
        
    return ml_joints

import cgm.core.lib.distance_utils as DIST
import cgm.core.lib.constraint_utils as CONSTRAINT

def setup_linearSegment(joints = [],
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
                                      skip = ['y','z'],
                                      maintainOffset = False)#Point contraint loc to the object
        
        for c in [_point,_orient]:
            CONSTRAINT.set_weightsByDistance(c[0],_vList)
            
        mObj.parent = mGroup
        
      
d_footTest = {'pivotToe' : 'l_front_toe_pivot',
              'pivotHeel' : 'l_front_heel_pivot',
              'pivotBall' : 'l_front_ball_pivot',
              'pivotInner' : 'l_front_inr_pivot',
              'pivotOutr' : 'l_front_outr_pivot',
              'pivotBall' : 'l_front_ball_pivot',
              #pivotBallWiggle : None,
              #jointBall : None,
              'direction':'left,',
              'orientation' : 'xyz',
              'controlIK' : 'l_front_foot_ik_anim',
              'ikHandle':'l_front_foot_ik_anim|ikChain_PV_ikH',
              'jointIKBall':'l_front_ball_ik',
              'jointIKHeel':'l_front_heel_ik',
              'baseName':'left_front'}   

def setup_footPivots(pivotToe = None,
                     pivotHeel = None,
                     pivotBall = None,
                     pivotInner = None,
                     pivotOutr = None,
                     #pivotBallWiggle = None,
                     #jointBall = None,
                     orientation = 'xyz',
                     controlIK = None,
                     direction = 'left',
                     ikHandle = None,
                     jointIKBall = None,#To build toe ik
                     jointIKHeel = None,
                     baseName = 'left_front',
                     ballRoll = False,
                     ):   
    _str_func = 'setup_footPivots'
          

    mi_pivotToe = cgmMeta.validateObjArg(pivotToe,'cgmObject')
    mi_pivotHeel  = cgmMeta.validateObjArg(pivotHeel,'cgmObject')
    mi_pivotBall  = cgmMeta.validateObjArg(pivotBall,'cgmObject')
    mi_pivotInner  = cgmMeta.validateObjArg(pivotInner,'cgmObject')
    mi_pivotOutr  = cgmMeta.validateObjArg(pivotOutr,'cgmObject')
    #mi_pivotBall  = cgmMeta.validateObjArg(pivotBall,'cgmObject')
    #mi_pivotBallWiggle  = cgmMeta.validateObjArg(pivotBallWiggle,'cgmObject')
    #mi_jointBall   = cgmMeta.validateObjArg(jointBall,'cgmObject')    
    #mi_jointBall  = cgmMeta.validateObjArg(jointBall,'cgmObject')

    
    mOrientation = VALID.simpleOrientation(orientation)
    
    mi_controlIK   = cgmMeta.validateObjArg(controlIK,'cgmObject')    
    mi_ikHandle = cgmMeta.validateObjArg(ikHandle,'cgmObject',noneValid=True)    
    
    ml_pivots = [mi_pivotToe,mi_pivotHeel ,mi_pivotBall,mi_pivotInner,mi_pivotOutr]
    
    pprint.pprint(vars())
    
    if ballRoll:
        mi_jointIKBall  = cgmMeta.validateObjArg(jointIKBall,'cgmObject')
        mi_jointIKHeel  = cgmMeta.validateObjArg(jointIKHeel,'cgmObject')        
        
        #Make Joints...--------------------------------------------------------------------------------------------
        #Ball Joint pivot
        log.info("|{0}| >> Make joints...".format(_str_func))        
        mi_jointBallPivot = mi_jointIKBall.doCreateAt(copyAttrs=True)#dup ball in place
        mi_jointBallPivot.rename(mi_jointIKBall.p_nameBase.replace('ik','pivot_jnt'))
        mi_jointBallPivot.parent = mi_pivotBall.mNode#ballJoint to ball        
        #mi_pivBallWiggle.parent = mi_pivInner.mNode    
    
        #Ball wiggle pivot
        #mi_ballWiggle = mi_jointIKBall.doDuplicate(po = True)#dup ball in place
        #i_ballWigglePivot.parent = False
        #i_ballWigglePivot.cgmName = 'ballWiggle'
        #i_ballWigglePivot.doName()
        #self._i_rigNull.connectChildNode(i_ballWigglePivot,"pivot_ballWiggle","rigNull")     
    
        #Do the toe
        mi_jointToe = mi_jointIKBall.doDuplicate()
        mi_jointToe.doSnapTo(mi_pivotToe.mNode,True,False)
        #SNAP.go(mi_jointToe, mi_pivotToe.mNode,True,False)
        import cgm.lib.joints as joints
        joints.doCopyJointOrient(mi_jointIKBall.mNode,mi_jointToe.mNode)
        #mi_jointToe.addAttr('cgmName','toe',attrType='string',lock=True)	
        #mi_jointToe.addAttr('cgmTypeModifier','ik',attrType='string',lock=True)
        #mi_jointToe.doName()
        mi_jointToe.rename(mi_jointIKBall.p_nameBase.replace('ik','toe_ikHelper_jnt'))
    
        mi_jointToe.parent = mi_jointIKBall.mNode
        #ml_ikJoints.append(mi_jointToe)
        #self._i_rigNull.msgList_append('ikJoints',mi_jointToe,'rigNull')   
        
        #Create foot IK -----------------------------------------------------------------------
        
        d_ballReturn = rUtils.IKHandle_create(mi_jointIKHeel.mNode,mi_jointIKBall.mNode,solverType='ikSCsolver',
                                              baseName=baseName + '_heel')
        mi_ballIKHandle = d_ballReturn['mi_handle']
        mi_ballIKHandle.parent = mi_pivotInner.mNode#ballIK to toe
        
        
        #Create toe IK
        d_toeReturn = rUtils.IKHandle_create(mi_jointIKBall.mNode,mi_jointToe.mNode,solverType='ikSCsolver',
                                             baseName=baseName + '_toe')
        mi_toeIKHandle = d_toeReturn['mi_handle']
    
        #return {'mi_handle':i_ik_handle,'mi_effector':i_ik_effector,'mi_solver':i_ikSolver}
    
        mi_toeIKHandle.parent = mi_pivotBall.mNode#toeIK to wiggle    
    

    #Parenting...--------------------------------------------------------------------------------------------
    log.info("|{0}| >> Parenting...".format(_str_func))    
    mi_pivotHeel.parent = mi_controlIK
    mi_pivotToe.parent = mi_pivotHeel
    mi_pivotBall.parent = mi_pivotToe
    mi_pivotOutr.parent = mi_pivotBall
    mi_pivotInner.parent = mi_pivotOutr
    
    if mi_ikHandle:
        mi_ikHandle.parent = mi_pivotInner
    #mi_jointBall
    #mi_pivotBallWiggle = mi_pivotBall
    
    for mPivot in ml_pivots:
        mPivot.rotateOrder = 0
        mPivot.doGroup(True,True,asMeta=True,typeModifier = 'zero')
    
    #Attributes ...---------------------------------------------------------------------------------------------
    log.info("|{0}| >> Attributes ...".format(_str_func))    
    mPlug_roll = cgmMeta.cgmAttr(mi_controlIK,'roll',attrType='float',defaultValue = 0,keyable = True)
    mPlug_bank = cgmMeta.cgmAttr(mi_controlIK,'bank',attrType='float',defaultValue = 0,keyable = True)
    
    #mPlug_toeWiggle= cgmMeta.cgmAttr(mi_controlIK,'toeWiggle',attrType='float',defaultValue = 0,keyable = True)
    mPlug_toeSpin = cgmMeta.cgmAttr(mi_controlIK,'toeSpin',attrType='float',defaultValue = 0,keyable = True)
    mPlug_heelSpin = cgmMeta.cgmAttr(mi_controlIK,'heelSpin',attrType='float',defaultValue = 0,keyable = True)
    mPlug_ballSpin = cgmMeta.cgmAttr(mi_controlIK,'ballSpin',attrType='float',defaultValue = 0,keyable = True)
    
    #mPlug_lean = cgmMeta.cgmAttr(mi_controlIK,'lean',attrType='float',defaultValue = 0,keyable = True)
    #mPlug_kneeSpin = cgmMeta.cgmAttr(mi_controlIK,'kneeSpin',attrType='float',defaultValue = 0,keyable = True)
    #mPlug_stretch = cgmMeta.cgmAttr(mi_controlIK,'autoStretch',attrType='float',defaultValue = 1,keyable = True)
    #mPlug_showKnee = cgmMeta.cgmAttr(mi_controlIK,'showKnee',attrType='int',defaultValue = 0,minValue=0,maxValue=1,keyable = True)
    #mPlug_lengthUpr= cgmMeta.cgmAttr(mi_controlIK,'lengthUpr',attrType='float',defaultValue = 1,minValue=0,keyable = True)
    #mPlug_lengthLwr = cgmMeta.cgmAttr(mi_controlIK,'lengthLwr',attrType='float',defaultValue = 1,minValue=0,keyable = True)
    
    if ballRoll:
        mPlug_toeLift = cgmMeta.cgmAttr(mi_controlIK,'toeLift',attrType='float',initialValue = 35, defaultValue = 35,keyable = True)
        mPlug_toeStaighten = cgmMeta.cgmAttr(mi_controlIK,'toeStaighten',attrType='float',initialValue = 65,defaultValue = 70,keyable = True)
        
        #Heel setup ----------------------------------------------------------------------------------------
        log.info("|{0}| >> Heel ...".format(_str_func))        
        mPlug_heelClampResult = cgmMeta.cgmAttr(mi_controlIK,'result_clamp_heel',attrType='float',keyable = False,hidden=True)
    
        #Setup the heel roll
        #Clamp
        
        _arg = "{0} = clamp({1},0,{2})".format(mPlug_heelClampResult.p_combinedShortName,
                                               mPlug_roll.p_combinedShortName,
                                               mPlug_roll.p_combinedShortName)
        
        log.info("|{0}| >> heel arg: {1}".format(_str_func,_arg))        
        NodeF.argsToNodes(_arg).doBuild()
        
        #Inversion
        mPlug_heelClampResult.doConnectOut("%s.rx"%(mi_pivotHeel.mNode))        
        
        #Ball setup ----------------------------------------------------------------------------------------------
        """
        Schleifer's
        ball_loc.rx = (linstep(0,$toeLift, $roll) * (1-(linstep( $toeLift, $toeStraight, $roll))) * $roll;
                ballToeLiftRoll        md   ( pma   toeToeStraightRoll                    md  
                    1               4       3             2                            5
        """
        log.info("|{0}| >> ball ...".format(_str_func))    
        
        
        mPlug_ballToeLiftRollResult = cgmMeta.cgmAttr(mi_controlIK,'result_range_ballToeLiftRoll',attrType='float',keyable = False,hidden=True)
        mPlug_toeStraightRollResult = cgmMeta.cgmAttr(mi_controlIK,'result_range_toeStraightRoll',attrType='float',keyable = False,hidden=True)
        mPlug_oneMinusToeResultResult = cgmMeta.cgmAttr(mi_controlIK,'result_pma_one_minus_toeStraitRollRange',attrType='float',keyable = False,hidden=True)
        mPlug_ball_x_toeResult = cgmMeta.cgmAttr(mi_controlIK,'result_md_roll_x_toeResult',attrType='float',keyable = False,hidden=True)
        mPlug_all_x_rollResult = cgmMeta.cgmAttr(mi_controlIK,'result_md_all_x_rollResult',attrType='float',keyable = False,hidden=True)
    
        arg1 = "%s = setRange(0,1,0,%s,%s)"%(mPlug_ballToeLiftRollResult.p_combinedShortName,
                                             mPlug_toeLift.p_combinedShortName,
                                             mPlug_roll.p_combinedShortName)
        arg2 = "%s = setRange(0,1,%s,%s,%s)"%(mPlug_toeStraightRollResult.p_combinedShortName,
                                              mPlug_toeLift.p_combinedShortName,
                                              mPlug_toeStaighten.p_combinedShortName,
                                              mPlug_roll.p_combinedShortName)
        arg3 = "%s = 1 - %s"%(mPlug_oneMinusToeResultResult.p_combinedShortName,
                              mPlug_toeStraightRollResult.p_combinedShortName)
    
        arg4 = "%s = %s * %s"%(mPlug_ball_x_toeResult.p_combinedShortName,
                               mPlug_oneMinusToeResultResult.p_combinedShortName,
                               mPlug_ballToeLiftRollResult.p_combinedShortName)
    
        arg5 = "%s = %s * %s"%(mPlug_all_x_rollResult.p_combinedShortName,
                               mPlug_ball_x_toeResult.p_combinedShortName,
                               mPlug_roll.p_combinedShortName)
    
        for arg in [arg1,arg2,arg3,arg4,arg5]:
            NodeF.argsToNodes(arg).doBuild()
    
        mPlug_all_x_rollResult.doConnectOut("%s.r%s"%(mi_jointBallPivot.mNode,orientation[2]))
    
    
        #Toe setup -----------------------------------------------------------------------------------------------
        """
        Schleifer's
        toe_loc.rotateX = linstep($toeLift, $toeStraight,$roll) * $roll;
                      setRange                           md
                     1                                2
        """
        log.info("|{0}| >> Toe ...".format(_str_func))        
        
        mPlug_toeRangeResult = cgmMeta.cgmAttr(mi_controlIK,'result_range_toeLiftStraightRoll',attrType='float',keyable = False,hidden=True)
        mPlug_toe_x_rollResult = cgmMeta.cgmAttr(mi_controlIK,'result_md_toeRange_x_roll',attrType='float',keyable = False,hidden=True)
    
        arg1 = "%s = setRange(0,1,%s,%s,%s)"%(mPlug_toeRangeResult.p_combinedShortName,
                                              mPlug_toeLift.p_combinedShortName,
                                              mPlug_toeStaighten.p_combinedShortName,                                         
                                              mPlug_roll.p_combinedShortName)
        arg2 = "%s = %s * %s"%(mPlug_toe_x_rollResult.p_combinedShortName,
                               mPlug_toeRangeResult.p_combinedShortName,
                               mPlug_roll.p_combinedShortName)
        for arg in [arg1,arg2]:
            NodeF.argsToNodes(arg).doBuild()    
    
        mPlug_toe_x_rollResult.doConnectOut("%s.rx"%(mi_pivotToe.mNode))    
    else:
        #Roll setup -----------------------------------------------------------------------------------------------
        """
        Schleifer's
        outside_loc.rotateZ = min($side,0);
        clamp1
        inside_loc.rotateZ = max(0,$side);
        clamp2
        """   
        log.info("|{0}| >> Bank ...".format(_str_func))        
        
        mPlug_toeRollResult = cgmMeta.cgmAttr(mi_controlIK,'result_clamp_toeRoll',attrType='float',keyable = False,hidden=True)
        mPlug_heelRollResult = cgmMeta.cgmAttr(mi_controlIK,'result_clamp_heelRoll',attrType='float',keyable = False,hidden=True)
    
        arg1 = "%s = clamp(-180,0,%s)"%(mPlug_heelRollResult.p_combinedShortName,                                  
                                        mPlug_roll.p_combinedShortName)
        arg2 = "%s = clamp(0,180,%s)"%(mPlug_toeRollResult.p_combinedShortName,
                                       mPlug_roll.p_combinedShortName)
        for arg in [arg1,arg2]:
            NodeF.argsToNodes(arg).doBuild()   
    
        mPlug_toeRollResult.doConnectOut("%s.rx"%(mi_pivotToe.mNode))
        mPlug_heelRollResult.doConnectOut("%s.rx"%(mi_pivotHeel.mNode))         
    

    #Bank setup -----------------------------------------------------------------------------------------------
    """
    Schleifer's
    outside_loc.rotateZ = min($side,0);
    clamp1
    inside_loc.rotateZ = max(0,$side);
    clamp2
    """   
    log.info("|{0}| >> Bank ...".format(_str_func))        
    
    mPlug_outerResult = cgmMeta.cgmAttr(mi_controlIK,'result_clamp_outerBank',attrType='float',keyable = False,hidden=True)
    mPlug_innerResult = cgmMeta.cgmAttr(mi_controlIK,'result_clamp_innerBank',attrType='float',keyable = False,hidden=True)

        
    if direction.lower() in ['right']:
        arg1 = "%s = clamp(-180,0,%s)"%(mPlug_innerResult.p_combinedShortName,                                  
                                        mPlug_bank.p_combinedShortName)
        arg2 = "%s = clamp(0,180,%s)"%(mPlug_outerResult.p_combinedShortName,
                                       mPlug_bank.p_combinedShortName)
        for arg in [arg1,arg2]:
            NodeF.argsToNodes(arg).doBuild()           
        
        str_bankDriverOutr = "%s.rz = -%s"%(mi_pivotOutr.mNode,
                                         mPlug_outerResult.p_combinedShortName)
        str_bankDriverInnr = "%s.rz = -%s"%(mi_pivotInner.mNode,
                                            mPlug_innerResult.p_combinedShortName)    
        for arg in [str_bankDriverInnr,str_bankDriverOutr]:
            NodeF.argsToNodes(arg).doBuild()
    else:     
        arg1 = "%s = clamp(-180,0,%s)"%(mPlug_outerResult.p_combinedShortName,                                  
                                        mPlug_bank.p_combinedShortName)
        arg2 = "%s = clamp(0,180,%s)"%(mPlug_innerResult.p_combinedShortName,
                                       mPlug_bank.p_combinedShortName)
        for arg in [arg1,arg2]:
            NodeF.argsToNodes(arg).doBuild()           
        
        mPlug_outerResult.doConnectOut("%s.rz"%(mi_pivotOutr.mNode))
        mPlug_innerResult.doConnectOut("%s.rz"%(mi_pivotInner.mNode))    
    
    #ball spin setup -----------------------------------------------------------------------------------------------    
    """
    Schleifer's
    ball_loc.rotateZ = $lean;
    """    
    log.info("|{0}| >> ball spin ...".format(_str_func))        
    
    if direction.lower() in ['right']:
        str_leanDriver = "%s.ry = -%s"%(mi_pivotBall.mNode,
                                         mPlug_ballSpin.p_combinedShortName)
        NodeF.argsToNodes(str_leanDriver).doBuild()
    else:
        mPlug_ballSpin.doConnectOut("%s.ry"%(mi_pivotBall.mNode))  
        
    #Toe spin --------------------------------------------------------------------------------------
    """
    Schleifer's
    toe_loc.rotateY = $spin;
    """  
    log.info("|{0}| >> toe spin ...".format(_str_func))        
    
    if direction.lower() in ['right']:
        str_leanDriver = "%s.ry = -%s"%(mi_pivotToe.mNode,
                                         mPlug_toeSpin.p_combinedShortName)
        NodeF.argsToNodes(str_leanDriver).doBuild()
    else:
        mPlug_toeSpin.doConnectOut("%s.ry"%(mi_pivotToe.mNode))    
        
    #heel spin --------------------------------------------------------------------------------------
    log.info("|{0}| >> heel spin ...".format(_str_func))        
    
    if direction.lower() in ['right']:
        str_leanDriver = "%s.ry = -%s"%(mi_pivotHeel.mNode,
                                         mPlug_heelSpin.p_combinedShortName)
        NodeF.argsToNodes(str_leanDriver).doBuild()
    else:
        mPlug_heelSpin.doConnectOut("%s.ry"%(mi_pivotHeel.mNode)) 
        
    return
    


def holder():
    try:#initialize...
        mi_settings = cgmMeta.validateObjArg(settings,'cgmObject')
        mi_ikControl = cgmMeta.validateObjArg(ikControl,'cgmObject')
        mPlug_worldIKStartIn = cgmMeta.cgmAttr(mi_settings,"in_worldIKStart" , attrType='float' , lock = True)
        outVector = VALID.simpleAxis(orientation[2]).p_vector
        upVector = VALID.simpleAxis(orientation[1]).p_vector
        ml_blendJoints = cgmMeta.validateObjListArg(blendJoints,'cgmObject')
        mi_mainSegmentHandle = cgmMeta.validateObjArg(segmentHandle,'cgmObject')
        mi_rootGroup = cgmMeta.validateObjArg(rootGroup,'cgmObject')
        fl_baseDist = DIST.get_distance_between_points(ml_blendJoints[0].p_position, ml_blendJoints[-1].p_position)
    except:pass    
    try:#msgLists....
        ml_controlsFK =  mi_go._i_rigNull.msgList_get('controlsFK')    
        ml_rigJoints = mi_go._i_rigNull.msgList_get('rigJoints')
        ml_blendJoints = mi_go._i_rigNull.msgList_get('blendJoints')
        ml_fkJoints = mi_go._i_rigNull.msgList_get('fkJoints')
        ml_ikJoints = mi_go._i_rigNull.msgList_get('ikJoints')
        ml_ikPVJoints = mi_go._i_rigNull.msgList_get('ikPVJoints')
        ml_ikNoFlipJoints = mi_go._i_rigNull.msgList_get('ikNoFlipJoints')
    except:pass    
    #=============================================================    
    try:#>>>Attr setup
        mi_pivHeel.parent = mi_controlIK.mNode#heel to foot
        mi_pivToe.parent = mi_pivHeel.mNode#toe to heel    
        mi_pivOuter.parent = mi_pivToe.mNode#outer to heel
        mi_pivInner.parent = mi_pivOuter.mNode#inner to outer
        mi_pivBall.parent = mi_pivInner.mNode#pivBall to toe
        mi_pivBallJoint.parent = mi_pivBall.mNode#ballJoint to ball        
        mi_pivBallWiggle.parent = mi_pivInner.mNode

        #for each of our pivots, we're going to zero group them
        for pivot in [mi_pivToe,mi_pivHeel,mi_pivBall,mi_pivInner,mi_pivOuter,mi_pivBallJoint,mi_pivBallWiggle]:
            pivot.rotateOrder = 0
            pivot.doGroup(True,True)
            log.info("pivot: %s"%pivot.getShortName())    

        #Add driving attrs
        mPlug_roll = cgmMeta.cgmAttr(mi_controlIK,'roll',attrType='float',defaultValue = 0,keyable = True)
        mPlug_toeLift = cgmMeta.cgmAttr(mi_controlIK,'toeLift',attrType='float',initialValue = 35, defaultValue = 35,keyable = True)
        mPlug_toeStaighten = cgmMeta.cgmAttr(mi_controlIK,'toeStaighten',attrType='float',initialValue = 65,defaultValue = 70,keyable = True)
        mPlug_toeWiggle= cgmMeta.cgmAttr(mi_controlIK,'toeWiggle',attrType='float',defaultValue = 0,keyable = True)
        mPlug_toeSpin = cgmMeta.cgmAttr(mi_controlIK,'toeSpin',attrType='float',defaultValue = 0,keyable = True)
        mPlug_lean = cgmMeta.cgmAttr(mi_controlIK,'lean',attrType='float',defaultValue = 0,keyable = True)
        mPlug_side = cgmMeta.cgmAttr(mi_controlIK,'bank',attrType='float',defaultValue = 0,keyable = True)
        mPlug_kneeSpin = cgmMeta.cgmAttr(mi_controlIK,'kneeSpin',attrType='float',defaultValue = 0,keyable = True)
        mPlug_stretch = cgmMeta.cgmAttr(mi_controlIK,'autoStretch',attrType='float',defaultValue = 1,keyable = True)
        mPlug_showKnee = cgmMeta.cgmAttr(mi_controlIK,'showKnee',attrType='int',defaultValue = 0,minValue=0,maxValue=1,keyable = True)
        mPlug_lengthUpr= cgmMeta.cgmAttr(mi_controlIK,'lengthUpr',attrType='float',defaultValue = 1,minValue=0,keyable = True)
        mPlug_lengthLwr = cgmMeta.cgmAttr(mi_controlIK,'lengthLwr',attrType='float',defaultValue = 1,minValue=0,keyable = True)

    except Exception,error:raise Exception,"Attr setup fail! | error: {0}".format(error)

    try:#heel setup
        #Add driven attrs
        mPlug_heelClampResult = cgmMeta.cgmAttr(mi_controlIK,'result_clamp_heel',attrType='float',keyable = False,hidden=True)
        #mPlug_heelResult = cgmMeta.cgmAttr(mi_controlIK,'result_heel',attrType='float',keyable = False,hidden=True)

        #Setup the heel roll
        #Clamp
        NodeF.argsToNodes("%s = clamp(%s,0,%s)"%(mPlug_heelClampResult.p_combinedShortName,
                                                 mPlug_roll.p_combinedShortName,
                                                 mPlug_roll.p_combinedShortName)).doBuild()
        #Inversion
        #NodeF.argsToNodes("%s = -%s"%(mPlug_heelResult.p_combinedShortName,mPlug_heelClampResult.p_combinedShortName)).doBuild()
        mPlug_heelClampResult.doConnectOut("%s.r%s"%(mi_pivHeel.mNode,mi_go._jointOrientation[2].lower()))

    except Exception,error:raise Exception,"Heel setup fail! | error: {0}".format(error)


    try:#ball setup
        """
		Schleifer's
		ball_loc.rx = (linstep(0,$toeLift, $roll) * (1-(linstep( $toeLift, $toeStraight, $roll))) * $roll;
				ballToeLiftRoll        md   ( pma   toeToeStraightRoll                    md  
					1               4       3             2                            5
		"""
        mPlug_ballToeLiftRollResult = cgmMeta.cgmAttr(mi_controlIK,'result_range_ballToeLiftRoll',attrType='float',keyable = False,hidden=True)
        mPlug_toeStraightRollResult = cgmMeta.cgmAttr(mi_controlIK,'result_range_toeStraightRoll',attrType='float',keyable = False,hidden=True)
        mPlug_oneMinusToeResultResult = cgmMeta.cgmAttr(mi_controlIK,'result_pma_one_minus_toeStraitRollRange',attrType='float',keyable = False,hidden=True)
        mPlug_ball_x_toeResult = cgmMeta.cgmAttr(mi_controlIK,'result_md_roll_x_toeResult',attrType='float',keyable = False,hidden=True)
        mPlug_all_x_rollResult = cgmMeta.cgmAttr(mi_controlIK,'result_md_all_x_rollResult',attrType='float',keyable = False,hidden=True)

        arg1 = "%s = setRange(0,1,0,%s,%s)"%(mPlug_ballToeLiftRollResult.p_combinedShortName,
                                             mPlug_toeLift.p_combinedShortName,
                                             mPlug_roll.p_combinedShortName)
        arg2 = "%s = setRange(0,1,%s,%s,%s)"%(mPlug_toeStraightRollResult.p_combinedShortName,
                                              mPlug_toeLift.p_combinedShortName,
                                              mPlug_toeStaighten.p_combinedShortName,
                                              mPlug_roll.p_combinedShortName)
        arg3 = "%s = 1 - %s"%(mPlug_oneMinusToeResultResult.p_combinedShortName,
                              mPlug_toeStraightRollResult.p_combinedShortName)

        arg4 = "%s = %s * %s"%(mPlug_ball_x_toeResult.p_combinedShortName,
                               mPlug_oneMinusToeResultResult.p_combinedShortName,
                               mPlug_ballToeLiftRollResult.p_combinedShortName)

        arg5 = "%s = %s * %s"%(mPlug_all_x_rollResult.p_combinedShortName,
                               mPlug_ball_x_toeResult.p_combinedShortName,
                               mPlug_roll.p_combinedShortName)

        for arg in [arg1,arg2,arg3,arg4,arg5]:
            NodeF.argsToNodes(arg).doBuild()

        mPlug_all_x_rollResult.doConnectOut("%s.r%s"%(mi_pivBallJoint.mNode,mi_go._jointOrientation[2].lower()))

    except Exception,error:raise Exception,"Ball setup fail! | error: {0}".format(error)

    try:#toe setup    
        """
		Schleifer's
		toe_loc.rotateX = linstep($toeLift, $toeStraight,$roll) * $roll;
				      setRange                           md
					 1                                2
		"""
        mPlug_toeRangeResult = cgmMeta.cgmAttr(mi_controlIK,'result_range_toeLiftStraightRoll',attrType='float',keyable = False,hidden=True)
        mPlug_toe_x_rollResult = cgmMeta.cgmAttr(mi_controlIK,'result_md_toeRange_x_roll',attrType='float',keyable = False,hidden=True)

        arg1 = "%s = setRange(0,1,%s,%s,%s)"%(mPlug_toeRangeResult.p_combinedShortName,
                                              mPlug_toeLift.p_combinedShortName,
                                              mPlug_toeStaighten.p_combinedShortName,                                         
                                              mPlug_roll.p_combinedShortName)
        arg2 = "%s = %s * %s"%(mPlug_toe_x_rollResult.p_combinedShortName,
                               mPlug_toeRangeResult.p_combinedShortName,
                               mPlug_roll.p_combinedShortName)
        for arg in [arg1,arg2]:
            NodeF.argsToNodes(arg).doBuild()    

        mPlug_toe_x_rollResult.doConnectOut("%s.r%s"%(mi_pivToe.mNode,mi_go._jointOrientation[2].lower()))

    except Exception,error:raise Exception,"Toe Setup fail! | error: {0}".format(error)


    try:#bank setup 
        """
		Schleifer's
		outside_loc.rotateZ = min($side,0);
		clamp1
		inside_loc.rotateZ = max(0,$side);
		clamp2
		"""    
        mPlug_outerResult = cgmMeta.cgmAttr(mi_controlIK,'result_clamp_outerBank',attrType='float',keyable = False,hidden=True)
        mPlug_innerResult = cgmMeta.cgmAttr(mi_controlIK,'result_clamp_innerBank',attrType='float',keyable = False,hidden=True)

        arg1 = "%s = clamp(-180,0,%s)"%(mPlug_outerResult.p_combinedShortName,                                  
                                        mPlug_side.p_combinedShortName)
        arg2 = "%s = clamp(0,180,%s)"%(mPlug_innerResult.p_combinedShortName,
                                       mPlug_side.p_combinedShortName)
        for arg in [arg1,arg2]:
            NodeF.argsToNodes(arg).doBuild()   

        mPlug_outerResult.doConnectOut("%s.r%s"%(mi_pivOuter.mNode,mi_go._jointOrientation[0].lower()))
        mPlug_innerResult.doConnectOut("%s.r%s"%(mi_pivInner.mNode,mi_go._jointOrientation[0].lower()))

    except Exception,error:raise Exception,"Bank setup fail! | error: {0}".format(error)


    try:#lean setup 
        """
		Schleifer's
		ball_loc.rotateZ = $lean;
		"""    
        if mi_go._mi_module.getAttr('cgmDirection') and mi_go._mi_module.cgmDirection.lower() in ['right']:
            str_leanDriver = "%s.r%s = -%s"%(mi_pivBallJoint.mNode,mi_go._jointOrientation[0].lower(),
                                             mPlug_lean.p_combinedShortName)
            NodeF.argsToNodes(str_leanDriver).doBuild()
        else:
            mPlug_lean.doConnectOut("%s.r%s"%(mi_pivBallJoint.mNode,mi_go._jointOrientation[0].lower()))

    except Exception,error:raise Exception,"lean setup fail! | error: {0}".format(error)


    try:#toe spin setup 
        """
		Schleifer's
		toe_loc.rotateY = $spin;
		"""  
        if mi_go._mi_module.getAttr('cgmDirection') and mi_go._mi_module.cgmDirection.lower() in ['right']:
            str_leanDriver = "%s.r%s = -%s"%(mi_pivToe.mNode,mi_go._jointOrientation[1].lower(),
                                             mPlug_toeSpin.p_combinedShortName)
            NodeF.argsToNodes(str_leanDriver).doBuild()
        else:
            mPlug_toeSpin.doConnectOut("%s.r%s"%(mi_pivToe.mNode,mi_go._jointOrientation[1].lower()))

    except Exception,error:raise Exception,"Toe spin fail! | error: {0}".format(error)


    try:#toe wiggle setup 
        """
		Schleifer's
		toeWiggle_loc.rx = $wiggle;
		""" 
        mPlug_toeWiggle.doConnectOut("%s.r%s"%(mi_pivBallWiggle.mNode,mi_go._jointOrientation[2].lower()))

    except Exception,error:raise Exception,"Toe wiggle fail! | error: {0}".format(error)

    return True	        
              
def setup_driverGroups(objs=[]):
    ml_objs = cgmMeta.validateObjListArg(objs,'cgmObject')
    ml_groups = []
    for mObj in ml_objs:
        mGroup = mObj.getMessage('driverGroup',asMeta =True)
        if not mGroup:
            mGroup = mObj.doGroup(True,True,asMeta=True,typeModifier = 'driver')
        ml_groups.append(mGroup)
    return ml_groups

def setup_mirrorDrivenAttrs(objs = [], attrs = []):
    ml_objs = cgmMeta.validateObjListArg(objs,'cgmObject')
    ml_groups = []
    for mObj in ml_objs:
        mGroup = mObj.getMessage('driverGroup',asMeta =True)
        if not mGroup:        
            log.info("no driverGroup dat on : {0}".format(mObj.mNode))
            continue
        mGroup = mGroup[0]
        for a in attrs:
            if ATTR.is_connected(mGroup.mNode, a):
                plug = ATTR.get_driver(mGroup.mNode,a,False,True,False)
                
                ATTR.break_connection(mGroup.mNode, a)
                
                _arg = "{0}.{1} = -{2}".format(mGroup.p_nameShort,
                                               a,
                                               plug)
                log.info("{0}.{1} >> {2}".format(mGroup.mNode,a, _arg))
                NodeF.argsToNodes(_arg).doBuild()
            else:
                log.info("No driver on: {0}.{1}".format(mGroup.mNode,a))
                continue    
            
def setup_fingerDrivers(objs = [], baseName = 'index',
                        d_fingerAttrs = {'curl':'z','side':'y','twist':'x'},
                        attrHolder = 'l_hand_attrs'):
    
    ml_objs = cgmMeta.validateObjListArg(objs,'cgmObject')
    ml_groups = []
    mHolder = cgmMeta.validateObjArg(attrHolder,'cgmObject')
    
    for a in ['curl','side','twist']:
        for i,mObj in enumerate(ml_objs):
            mGroup = mObj.getMessage('driverGroup',asMeta =True)
            if not mGroup:        
                log.info("no driverGroup dat on : {0}".format(mObj.mNode))
                continue
            mGroup = mGroup[0]
            
            _str_attr = "{0}_{1}_{2}".format(baseName,i,a)
            
            mHolder.addAttr(_str_attr,attrType = 'float')
            
            ATTR.connect("{0}.{1}".format(attrHolder,_str_attr),
                         "{0}.r{1}".format(mGroup.mNode, d_fingerAttrs[a]))
            
def setup_toeIKGroups(objs = [],settings = 'l_front_leg_root'):
    ml_objs = cgmMeta.validateObjListArg(objs,'cgmObject')
    ml_groups = []
    for mObj in ml_objs:
        mFKGroup =  mObj.doGroup(True,False,asMeta=True,typeModifier = 'fk')
        mIKGroup =  mObj.doGroup(True,False,asMeta=True,typeModifier = 'ik')
        mGroup = mObj.doGroup(True,True,asMeta=True,typeModifier = 'blendFKIK')
        
        _const = mc.parentConstraint([mFKGroup.mNode, mIKGroup.mNode], mGroup.mNode)
        _l_attrs = CONSTRAINT.get_targetWeightsAttrs(_const[0])
        
        ATTR.connect("{0}.result_FKon".format(settings), "{0}.{1}".format(_const[0],_l_attrs[0]))
        ATTR.connect("{0}.result_IKon".format(settings), "{0}.{1}".format(_const[0],_l_attrs[1]))

def resetCurveTransformsToSource():
    
    ml_objs = cgmMeta.validateObjListArg(mc.ls(sl=True),'cgmObject')
    
    for mObj in ml_objs:
        mSource = mObj.getMessage('cgmSource',asMeta=True)
        
        RIG.match_transform(mObj.mNode, mSource[0].mNode)
        

l_fingerJoints = [u'index_l_base_sknj',
                  u'index_l_mid_sknj',
                  u'index_l_tip_sknj',
                  u'index_l_end_sknj',
                  u'middle_l_base_sknj',
                  u'middle_l_mid_sknj',
                  u'middle_l_tip_sknj',
                  u'middle_l_end_sknj',
                  u'ring_l_base_sknj',
                  u'ring_l_mid_sknj',
                  u'ring_l_tip_sknj',
                  u'ring_l_end_sknj',
                  u'thumb_l_base_sknj',
                  u'thumb_l_mid_sknj',
                  u'thumb_l_tip_sknj',
                  u'thumb_l_end_sknj',
                  u'pinky_l_base_sknj',
                  u'pinky_l_mid_sknj',
                  u'pinky_l_tip_sknj',
                  u'pinky_l_end_sknj',
                  u'index_r_base_sknj',
                  u'index_r_mid_sknj',
                  u'index_r_tip_sknj',
                  u'index_r_end_sknj',
                  u'middle_r_base_sknj',
                  u'middle_r_mid_sknj',
                  u'middle_r_tip_sknj',
                  u'middle_r_end_sknj',
                  u'ring_r_base_sknj',
                  u'ring_r_mid_sknj',
                  u'ring_r_tip_sknj',
                  u'ring_r_end_sknj',
                  u'thumb_r_base_sknj',
                  u'thumb_r_mid_sknj',
                  u'thumb_r_tip_sknj',
                  u'thumb_r_end_sknj',
                  u'pinky_r_base_sknj',
                  u'pinky_r_mid_sknj',
                  u'pinky_r_tip_sknj',
                  u'pinky_r_end_sknj'] 
import cgm.core.lib.constraint_utils as CONSTRAINTS
#reload(CONSTRAINTS)
#CONSTRAINTS.copy_constraint('ring_r_base_rigj|OrientConstraint',None,'pointConstraint')

def fixFingerConstraints(l_joints = l_fingerJoints):
    ml_joints = cgmMeta.validateObjListArg(l_joints)
    
    for mObj in ml_joints:
        targets = CONSTRAINTS.get_targets( mObj.mNode)
        target = targets[0]
        constraint = CONSTRAINTS.get_constraintsTo(target)[0]
        CONSTRAINTS.copy_constraint(constraint,None,'pointConstraint',maintainOffset=False)
        

def skin_pushComponentToConnected(copyCurrent=True):
    _sel = mc.ls(sl=True)
    import maya.mel as mel
    if copyCurrent:mel.eval('artAttrSkinWeightCopy;')
    
    #_comp = VALID.get_component(_sel[0])
    #mc.select(mc.ls("{0}.{1}[*]".format(_comp[1],_comp[2])))
    for i in range(250):
        mel.eval('GrowPolygonSelectionRegion;')
    
    mel.eval('artAttrSkinWeightPaste;')
    
    