import maya.cmds as mc
from cgm.lib import joints,rigging, names, attributes, distance


def rigArm (objectNull):
    """return variables"""
    nullBase = names.stripSuffixObj (objectNull)
    templateNull = (nullBase + '_templateNull')
    templateNullMessageData = []
    templateNullMessageData = attributes.returnMessageAttrs (templateNull)
    templateObjects = []
    coreNamesList = []
    for set in templateNullMessageData:
        templateObjects.append (set[1])
        coreNamesList.append (set[0])
    """ return rid of locators on our template objects so they don't screw up the distance locators"""
    templateObjects.remove(templateObjects[-1])
    coreNamesList.remove(coreNamesList[-1])
    for obj in templateObjects:
        if mc.objExists (obj+'_loc'):
            mc.delete (obj+'_loc')
    """make joint chains"""
    fkJoints = joints.createJointsFromObjPositions (templateObjects, 'fk')
    mc.select (cl=True)
    ikJoints = joints.createJointsFromObjPositions (templateObjects, 'ik')
    
    """orient joints"""
    joints.orientJointChain (fkJoints, 'xyz', 'yup')
    joints.orientJointChain (ikJoints, 'xyz', 'yup')
    
    """set rotation order - CHANGE to go for the names later and optional orientation schemes"""
    joints.setRotationOrderOnJoint (fkJoints[0], 'xyz')
    joints.setRotationOrderOnJoint (fkJoints[1], 'xzy')
    joints.setRotationOrderOnJoint (fkJoints[2], 'zyx')
    
    joints.setRotationOrderOnJoint (ikJoints[0], 'xyz')
    joints.setRotationOrderOnJoint (ikJoints[1], 'xzy')
    joints.setRotationOrderOnJoint (ikJoints[2], 'zyx')
    
    """ create hand_anim locs """
    hand_animRegBuffer = locators.locMeObject (ikJoints[2])
    hand_animPinnedBuffer = locators.locMeObject (ikJoints[2]) 
    
    hand_animReg = mc.rename (hand_animRegBuffer, (coreNamesList[2]+'_anim'))
    hand_animPinned = mc.rename (hand_animPinnedBuffer, (coreNamesList[2]+'_elbow_anim'))
    
    """ creating measure stuff """
    # Had to move this up here because distanceDimension doesn't let you specify which locator to use. Need to modify script to account for that
    uprArmMeasureLocBuffer = locators.locMeObject (ikJoints[0])
    handMeasureLocBuffer = locators.locMeObject (ikJoints[2])
    elbowMeasureLocBuffer = locators.locMeObject (ikJoints[1])
    
    uprArmMeasureLoc = mc.rename (uprArmMeasureLocBuffer, (coreNamesList[0]+'_dist_loc'))
    handMeasureLoc = mc.rename (handMeasureLocBuffer, (coreNamesList[2]+'_dist_loc'))
    elbowMeasureLoc = mc.rename (elbowMeasureLocBuffer, (coreNamesList[1]+'_dist_loc'))
    
    measureFullLength = [uprArmMeasureLoc,handMeasureLoc]
    fullLengthMeassureObj = distance.createDistanceObjectsBetweenObjectList (measureFullLength) 

    measureShoulderToElbow = [uprArmMeasureLoc,elbowMeasureLoc]
    uprLengthMeassureObj = distance.createDistanceObjectsBetweenObjectList (measureShoulderToElbow)
    
    measureElbowToHand = [elbowMeasureLoc,handMeasureLoc]
    lwrLengthMeassureObj = distance.createDistanceObjectsBetweenObjectList (measureElbowToHand)  
    
    """>>>Set up Rotation Isolation for FK Mode
    """             
    """creates our locator parent"""     
    UprArmRoot = locators.locMeObject (fkJoints[0])
    """ Create 4 target locators"""
    UprArmTorsoOrientBuffer = mc.duplicate (UprArmRoot)
    UprArmBodyOrientBuffer = mc.duplicate (UprArmRoot)
    UprArmTorsoOrientDriverBuffer = mc.duplicate (UprArmRoot)
    UprArmBodyOrientDriverBuffer = mc.duplicate (UprArmRoot)
    UprArmOrientBuffer = mc.duplicate (UprArmRoot)

    """names our loctators intelligently"""
    uprArmTorsoOrient = mc.rename (UprArmTorsoOrientBuffer[0], (coreNamesList[0]+'_torso_orient'))
    uprArmBodyOrient = mc.rename (UprArmBodyOrientBuffer[0], (coreNamesList[0]+'_body_orient'))
    uprArmTorsoOrientDriver = mc.rename (UprArmTorsoOrientDriverBuffer[0], (coreNamesList[0]+'_torso_orient_driver'))
    uprArmBodyOrientDriver = mc.rename (UprArmBodyOrientDriverBuffer[0], (coreNamesList[0]+'_body_orient_driver'))
    UprArmOrient = mc.rename (UprArmOrientBuffer[0], (coreNamesList[0]+'_orient_anim'))
    
    """orients the orient_anim control placeholder"""
    attributes.setRotationOrderObj (UprArmOrient, 'xzy')
    
    """parents orient control loc to top node"""
    mc.parent (UprArmOrient,UprArmRoot)    
    """parents arm to top loc"""
    mc.parent (fkJoints[0],UprArmOrient)
    """parents top loc and torso orient loc to torso diver"""
    mc.parent (UprArmRoot,uprArmTorsoOrientDriver)
    mc.parent (uprArmTorsoOrient,uprArmTorsoOrientDriver)
    mc.parent (uprArmBodyOrient,uprArmBodyOrientDriver)
    
    """ makes orient constraint for the fk arm"""
    orConstBuffer = mc.orientConstraint ([uprArmBodyOrient,uprArmTorsoOrient], UprArmRoot, mo=True, weight=1)
    orConst = mc.rename (orConstBuffer,(fkJoints[0]+'_orConst'))
    
    """ adds our constraint toggle """
    mc.addAttr (fkJoints[0],ln='orient', at='enum', en='torso:body:')
    mc.setAttr ((fkJoints[0]+'.orient'), keyable=True)
    
    """ return our orient constraint channels """
    orConstAttrs =  (mc.listAttr (orConst, userDefined= True))
    
    """ setups up toggle to change orientation """    
    mc.setDrivenKeyframe ((orConst+'.'+orConstAttrs[0]), currentDriver=(fkJoints[0]+'.orient'), driverValue = 0, value =0)
    mc.setDrivenKeyframe ((orConst+'.'+orConstAttrs[1]), currentDriver=(fkJoints[0]+'.orient'), driverValue = 0, value =1)
    mc.setDrivenKeyframe ((orConst+'.'+orConstAttrs[0]), currentDriver=(fkJoints[0]+'.orient'), driverValue = 1, value =1)
    mc.setDrivenKeyframe ((orConst+'.'+orConstAttrs[1]), currentDriver=(fkJoints[0]+'.orient'), driverValue = 1, value =0)   

    """ >>>Sets up fk arm scaling """
    """ adds our length attribute"""
    mc.addAttr (fkJoints[0],ln='length', at='float', minValue = 0, defaultValue = 1)
    mc.setAttr ((fkJoints[0]+'.length'), keyable=True)
    mc.addAttr (fkJoints[1],ln='length', at='float', minValue = 0, defaultValue = 1)
    mc.setAttr ((fkJoints[1]+'.length'), keyable=True)
    
    """ connects length to child joint length """
    currentLength = mc.getAttr (fkJoints[1]+'.translateX')
    mc.setDrivenKeyframe ((fkJoints[1]+'.translateX'), currentDriver=(fkJoints[0]+'.length'), driverValue = 1, value = currentLength, inTangentType = 'linear', outTangentType = 'linear')
    mc.setDrivenKeyframe ((fkJoints[1]+'.translateX'), currentDriver=(fkJoints[0]+'.length'), driverValue = 0, value = 0, inTangentType = 'linear', outTangentType = 'linear')    

    currentLength = mc.getAttr (fkJoints[2]+'.translateX')
    mc.setDrivenKeyframe ((fkJoints[2]+'.translateX'), currentDriver=(fkJoints[1]+'.length'), driverValue = 1, value = currentLength, inTangentType = 'linear', outTangentType = 'linear')
    mc.setDrivenKeyframe ((fkJoints[2]+'.translateX'), currentDriver=(fkJoints[1]+'.length'), driverValue = 0, value = 0, inTangentType = 'linear', outTangentType = 'linear')    

    """ set sdk curves to infinity """
    mc.setInfinity ((fkJoints[1]+'.translateX'),pri = 'constant', poi = 'linear')
    mc.setInfinity ((fkJoints[2]+'.translateX'),pri = 'constant', poi = 'linear')

    """ lockin stuff down on the fk end """
    for jnt in fkJoints:    
        attributes.doSetLockHideKeyableAttr (jnt,True,False,False,['ty','tz','sx','sy','sz','v'])
    attributes.doSetLockHideKeyableAttr (UprArmOrient,True,False,False,['tx','ty','tz','sx','sy','sz','v'])
    attributes.doSetLockHideKeyableAttr (fkJoints[1],False,False,False,['tx'])
    attributes.doSetLockHideKeyableAttr (fkJoints[2],False,False,False,['tx'])
    
    """ >>>IK arm time!"""
    """make elbow loc and a hand loc"""
    elbowIKLoc = locators.locMeObject (ikJoints[1])
    handIKLoc = locators.locMeObject (ikJoints[2])

    """set preferred rotation channel on elbow"""
    #---------------------->>>> Need to figure out how to generate this!
    mc.setAttr ((ikJoints[1]+'.ry'), -30)    
    mc.joint (ikJoints[1], edit=True, setPreferredAngles = True)
    mc.setAttr ((ikJoints[1]+'.ry'), 0)    
    
    """set up the ik handle"""
    ikHandleName = (nullBase +'_ikHandle')
    mc.ikHandle  (name = ikHandleName ,startJoint = ikJoints[0], endEffector = ikJoints[2], sol='ikRPsolver', snapHandleFlagToggle=True )
    
    """Polevector constraint"""
    mc.poleVectorConstraint (elbowIKLoc, ikHandleName, name= (nullBase+'.pvConst'),weight=1.0)
    mc.parent (ikHandleName,handIKLoc)
    
    """ >>> IK Stretch stuff"""
    """connecting measure stuff"""
    mc.parent (handMeasureLoc,handIKLoc)
    
    uprArmLength = mc.getAttr (ikJoints[1]+'.tx')
    lwrArmLength = mc.getAttr (ikJoints[2]+'.tx')
    fullLength = (uprArmLength + lwrArmLength)
    driver = (fullLengthMeassureObj[0]+'Shape.distance')

    """sets base sdk key for length"""
    mc.setDrivenKeyframe ((ikJoints[1]+'.tx'), currentDriver = driver, driverValue = fullLength, value = uprArmLength, inTangentType = 'linear', outTangentType = 'linear')
    mc.setDrivenKeyframe ((ikJoints[2]+'.tx'), currentDriver = driver, driverValue = fullLength, value = lwrArmLength, inTangentType = 'linear', outTangentType = 'linear')
    """sets stetch sdk key for length"""
    mc.setDrivenKeyframe ((ikJoints[1]+'.tx'), currentDriver = driver, driverValue = (fullLength * 2), value = (uprArmLength * 2), inTangentType = 'linear', outTangentType = 'linear')
    mc.setDrivenKeyframe ((ikJoints[2]+'.tx'), currentDriver = driver, driverValue = (fullLength * 2), value = (lwrArmLength * 2), inTangentType = 'linear', outTangentType = 'linear')
    
    mc.setInfinity ((ikJoints[1]+'.tx'),pri = 'constant', poi = 'linear')
    mc.setInfinity ((ikJoints[2]+'.tx'),pri = 'constant', poi = 'linear')
    
    """ >>> Set up pinning"""
    """ creates blend node """    
    """upr"""    
    uprBlendNode = mc.createNode ('blendTwoAttr', name = 'upr_Choice_blendTwoNode', skipSelect = True)
    uprSDKCurve = mc.listConnections ((ikJoints[1]+'.tx'),source=True)
    mc.connectAttr ( (uprSDKCurve[0]+'.output') , (uprBlendNode+'.input[0]'), force=True )
    mc.connectAttr ( (uprLengthMeassureObj[0]+'Shape.distance') , (uprBlendNode+'.input[1]') , force = True )
    
    mc.connectAttr ( (uprBlendNode+'.output') , (ikJoints[1]+'.tx'), force = True )
    """lwr"""
    lwrBlendNode = mc.createNode ('blendTwoAttr', name = 'lwr_Choice_blendTwoNode', skipSelect = True)
    lwrSDKCurve = mc.listConnections ((ikJoints[2]+'.tx'),source=True)
    mc.connectAttr ( (lwrSDKCurve[0]+'.output') , (lwrBlendNode+'.input[0]'), force=True )
    mc.connectAttr ( (lwrLengthMeassureObj[0]+'Shape.distance') , (lwrBlendNode+'.input[1]') , force = True )
    
    mc.connectAttr ( (lwrBlendNode+'.output') , (ikJoints[2]+'.tx'), force = True )
    
    """adds stetch attrs"""
    mc.addAttr (elbowIKLoc,ln='pin', at='float', minValue = 0, defaultValue = 1)
    mc.setAttr ((elbowIKLoc+'.pin'), keyable=True)
    
    mc.connectAttr ( (elbowIKLoc+'.pin') , (uprBlendNode+'.attributesBlender') )
    mc.connectAttr ( (elbowIKLoc+'.pin') , (lwrBlendNode+'.attributesBlender') )
    mc.setAttr ((elbowIKLoc+'.pin') , 0)    
    
    mc.parent (elbowMeasureLoc,elbowIKLoc)
    
    """ >>> FK lower limb control setup """
    """ creates our pinned lower limb fk joint """
    pinnedLwrLimcgmuffer = mc.duplicate (ikJoints[1], renameChildren = True)
    
    nonJointStuff = search.returnNonJointObjsInHeirarchy (pinnedLwrLimcgmuffer)
    for item in nonJointStuff:
        mc.delete (item)
    
    """ name the joint we'll be using """    
    pinnedLwrLimb = mc.rename (pinnedLwrLimcgmuffer[0], (coreNamesList[1]+'_pinned_fk_anim') )
    mc.parent (pinnedLwrLimb,elbowIKLoc)
    pinnedLwrLimbEndBuffer = mc.listRelatives (pinnedLwrLimb, children = True)
    mc.rename (pinnedLwrLimbEndBuffer[0], (coreNamesList[1]+'_pinned_fk_end') )
    
    """ make the hand anim loc """
    mc.parent (hand_animPinned, elbowIKLoc)
    ptConstBuffer = mc.pointConstraint ([hand_animReg,hand_animPinned], handIKLoc, mo=False, weight=1)
        
    """ make the attr to drive it """
    mc.addAttr (elbowIKLoc,ln='forearm', at='enum', en = 'fk:ik:')
    mc.setAttr ((elbowIKLoc+'.forearm'), keyable=True)
    mc.setAttr ((elbowIKLoc+'.forearm') , 1)    

    """ connect it """    
    mc.connectAttr ( (elbowIKLoc+'.forearm') , (ptConstBuffer[0]+'.'+hand_animReg+'W0') )
    revNodeBuffer = mc.createNode ('reverse', name = 'hand_revNode')
    
    mc.connectAttr ( (elbowIKLoc+'.forearm'),(revNodeBuffer+'.inputX'))
    mc.connectAttr ( (revNodeBuffer+'.outputX'),(ptConstBuffer[0]+'.'+hand_animPinned+'W1') )
    
    


    
    

    
    
    

    

    


 



    
    
#rigArm ('armLeft_null')




