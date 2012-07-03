import maya.cmds as mc
from cgm.lib import joints, rigging, attributes, names, distance, nodes, search, batch, lists,curves
from cgm.lib import position

import copy as copy
from cgm.lib import skinning as cgmSkin

# ====================================================================================================================
#
# SIGNATURE:
#	finCtrlMaker(objectNull,spineChain,mirror,mode)
#
# DESCRIPTION:
#   makes a fin control rig
# 
# ARGUMENTS:
#	objectNull- null which houses our variables
#   bindJoint- start of the spine chain you wanna connect to
#   mirror - True/False (currently accross yz only)
#   worldScale - the world scale attribute to connect to the rigger
#   mode - 0/1 (0 for spingle main control pivot, 1 to connect each chain to the spine)
#   jointsPerChain - how many joints you want per chain
#   deformChains - number of spans you'd like on your deformation rig
#   cntrlChains - number of control chains you'd like (need at least 2)
#
# RETURNS:
#	List of the joints created
#
# ====================================================================================================================
def finRigger(objectNull,spineChain,worldScale,mirror,mode,jointsPerChain,deformChains,ctrlChains):
    attachSurfaceReturn = []
    attachSurfaceMirrorReturn = []
    """ Get variables"""
    nullBase = names.stripSuffixObj (objectNull)
    templateNull = (nullBase + '_templateNull')
    moverNull = (nullBase + '_mover')
    templateNullMessageData = []
    templateNullMessageData = attributes.returnMessageAttrs (templateNull)
    templateObjects = []
    coreNamesList = []
    spineJointNumber = int(mc.getAttr (objectNull+'.rollJoints'))
    spineChainList = search.returnChildrenJoints (spineChain)
    jointChains = []
    for set in templateNullMessageData:
        templateObjects.append (set[1])
        coreNamesList.append (set[0])
    #>>>>>>>>>>>>>>>>>>>>>Store skin joint data
    """ check for master skin info group """
    if mc.objExists ('master_skinJntList_grp'):
        masterSkinJointList = ('master_skinJntList_grp')
    else:
        masterSkinJointList = mc.group (n= ('master_skinJntList_grp'), w=True, empty=True)
        mc.parent(masterSkinJointList,'rigStuff_grp')
    """ check for segment skin info group """
    if mc.objExists (nullBase+'_skinJntList_grp'):
        skinJointListGrp = (nullBase+'_skinJntList_grp')
    else:
        skinJointListGrp = mc.group (n= (nullBase+'_skinJntList_grp'), w=True, empty=True)
    attributes.storeObjNameToMessage (skinJointListGrp,masterSkinJointList)
    mc.parent (skinJointListGrp,masterSkinJointList)
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """ Rebuild curve - with actual curve in it!"""
    mc.rebuildCurve ((templateObjects[3]), ch=0, rpo=1, rt=0, end=0, kr=0, kcp=0, kep=1, kt=0, s=jointsPerChain, d=1, tol=5)
    mc.rebuildCurve ((templateObjects[7]), ch=0, rpo=1, rt=0, end=0, kr=0, kcp=0, kep=1, kt=0, s=jointsPerChain, d=1, tol=5)
    """ Reverse the curve """
    mc.reverseCurve ((templateObjects[3]),ch=False,rpo=True)
    mc.reverseCurve ((templateObjects[7]),ch=False,rpo=True)
    """ loft our surface to figure out joint positions, then delete it"""
    controlSurface = mc.loft ([templateObjects[3],templateObjects[7]],name=(nullBase+'_surf'),ss=(ctrlChains-mode),ch=1,u=1,c=0,ar=1,d=3,rn=0,po=0,rsn=True)
    mc.select (cl=True)
    jointChains = joints.createJointChainsFromLoftSurface (nullBase,controlSurface[0],2,False)
    frontChain = jointChains[0]
    backChain = jointChains[-1]
    """ Chain - orienting, sizing """
    for chain in jointChains:
        joints.orientJointChain (chain, 'xyz', 'zup')
        joints.setGoodJointRadius(chain,.5)
    #IF we have mode 0, gotta make a main ctrl
    if mode == 0:
        midChain = []
        if (len(jointChains)) > 3:
            midChain = jointChains[int(len(jointChains)/2)]
        else:
            midChain = jointChains[1]
            jointChains.remove(midChain)
        if ctrlChains > 2:
            masterCtrlBuffer = mc.duplicate (midChain[0],parentOnly=True)
        else:
            masterCtrlBuffer = midChain[0]
            mc.delete (midChain[1])
        masterCtrl = mc.rename (masterCtrlBuffer,(nullBase+'_master_anim'))
        position.movePointSnap(masterCtrl,moverNull)
        """ temp parenting the master control for mirroring purposes """
        spineHookJoint = distance.returnClosestObject (masterCtrl, spineChainList)
        mc.parent (masterCtrl,spineHookJoint)
    mc.delete (controlSurface[0])
    #>>>>>>>>>>>>Parent time
    """ Get closest joint """
    if mode == 0:
        for chain in jointChains:
            mc.parent (chain[0],masterCtrl)
    else:
        for chain in jointChains:
            tailHookJoint = distance.returnClosestObject (chain[0], spineChainList)
            mc.parent (chain[0],tailHookJoint)
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>> Ctrl Joints to Ctrls
    cnt = 0
    for chain in jointChains:
        ctrlSize = (distance.returnAverageDistanceBetweenObjects (chain)/2)
        for jnt in chain[0:-1]:
            rigging.makeObjCtrl (jnt,ctrlSize)
        """ adds our Anim tag """
        chainBuffer = []
        chainBuffer = names.addSuffixList ('anim', chain)
        jointChains[cnt]= chainBuffer
        cnt +=1
    #>>>>>>>>>>>>>>>>>>>Mirroring while getting chain info
    """ If mirroring ...."""
    if mirror == True:
        # if we have a main control
        leftSkinChains = []
        rightSkinChains = []
        masterCtrls = []
        if mode == 0:
            leftChain = []
            rightChain = []
            finHeirarchy = []
            finHeirarchy.append (masterCtrl)
            children = search.returnChildrenJoints (masterCtrl)
            finHeirarchy += children
            leftChain = names.addPrefixList ('left',finHeirarchy)
            masterCtrl = leftChain [0]
            rightChainBuffer = mc.mirrorJoint (masterCtrl,mirrorYZ=True,mirrorBehavior=True, searchReplace =['left','right'])
            rightChainJointBuffer = mc.ls (rightChainBuffer,type='joint')
            rightChain = rightChainJointBuffer
            leftSkinChains.append(leftChain)
            rightSkinChains.append(rightChain)
            masterCtrls.append(leftChain[0])
            masterCtrls.append(rightChain[0])
        else:
            for chain in jointChains:
                leftChain =[]
                leftChain = names.addPrefixList ('left',chain)
                rightChainBuffer = (mc.mirrorJoint (leftChain[0],mirrorYZ=True,mirrorBehavior=True, searchReplace =['left','right']))
                rightChainJointBuffer = mc.ls (rightChainBuffer,type='joint')
                rightChain = rightChainJointBuffer
                rightSkinChains.append (rightChainJointBuffer)
                leftSkinChains.append (leftChain)
        """ complile our chains to lists of skin joints """
        leftSkinJointList=[]
        rightSkinJointList=[]
        for chain in leftSkinChains:
            for jnt in chain:
                leftSkinJointList.append (jnt)
        for chain in rightSkinChains:
            for jnt in chain:
                rightSkinJointList.append (jnt)
        """if we're not mirroring, let's return our skin joints for the deformation surface"""
    else:
        skinJointList = []
        skinChains = []
        for chain in jointChains:
            skinChains.append (chain)
            for jnt in chain:
                skinJointList.append (jnt)
                
    #>>>>>>>>>>>>>>>>>>>>>>>>>>Time to make the deformation surface stuff
    """ Rebuild curve - with actual curve in it!"""
    #mc.rebuildCurve ((templateObjects[3]), ch=0, rpo=1, rt=0, end=0, kr=0, kcp=0, kep=1, kt=0, s=(3), d=1, tol=5)
    #mc.rebuildCurve ((templateObjects[7]), ch=0, rpo=1, rt=0, end=0, kr=0, kcp=0, kep=1, kt=0, s=(3), d=1, tol=5)
    """ loft our surface to figure out joint positions, then delete it"""
    deformSurface = mc.loft ([templateObjects[3],templateObjects[7]],name=(nullBase+'_surf'),ss=(deformChains-1),ch=0,u=1,c=0,ar=1,d=3,rn=0,po=0,rsn=True)
    if mirror == True:
        deformSurfaceNameBuffer = deformSurface[0]
        """we have a surface to mirror..."""
        surfaceMirrorBuffer = mc.duplicate (deformSurface[0])
        mc.setAttr ((surfaceMirrorBuffer[0]+'.sx'),-1)
        leftBuffer = mc.rename (deformSurface[0],('left_'+deformSurfaceNameBuffer))
        rightBuffer = mc.rename (surfaceMirrorBuffer[0],('right_'+deformSurfaceNameBuffer))
        deformSurface[0]=leftBuffer
        deformSurface.append(rightBuffer)
        leftDeformJointChains = joints.createJointChainsFromLoftSurface (('left_'+nullBase),deformSurface[0],2,False)
        rightDeformJointChains = joints.createJointChainsFromLoftSurface (('right_'+nullBase),deformSurface[1],2,False)
        """ Connecting to surface """
        for chain in leftDeformJointChains:
            attachSurfaceReturn = joints.attachJointChainToSurface (chain,deformSurface[0],'xyz','zup')
            tailHookJoint = distance.returnClosestObject (chain[0], spineChainList)
            """ break the connection so we can parent it"""
            """first return the original thing to follow"""
            parentBuffer = attributes.returnDriverObject ((chain[0]+'.translate'))
            attributes.doBreakConnection (chain[0]+'.translate')
            mc.parent (chain[0],tailHookJoint)
            """ reconstrain it to the driver"""
            constraintBuffer = mc.pointConstraint (parentBuffer,chain[0], maintainOffset = True)
            mc.rename (constraintBuffer[0],(chain[0]+'_pointConst'))
            """ store the skin joint data """
            for jnt in chain:
                attributes.storeObjNameToMessage (jnt,skinJointListGrp)

        for chain in rightDeformJointChains:
            attachSurfaceMirrorReturn = joints.attachJointChainToSurface (chain,deformSurface[1],'xyz','zup')
            tailHookJoint = distance.returnClosestObject (chain[0], spineChainList)
            """ break the connection s we can parent it"""
            """first return the original thing to follow"""
            parentBuffer = attributes.returnDriverObject ((chain[0]+'.translate'))
            attributes.doBreakConnection (chain[0]+'.translate')
            mc.parent (chain[0],tailHookJoint)
            """ reconstrain it to the driver"""
            constraintBuffer = mc.pointConstraint (parentBuffer,chain[0], maintainOffset = True)
            mc.rename (constraintBuffer[0],(chain[0]+'_pointConst'))
            """ store the skin joint data """
            for jnt in chain:
                attributes.storeObjNameToMessage (jnt,skinJointListGrp)

        """ parent the scale stuff to rig stuff grp"""
        mc.select (cl=True)
        for item in attachSurfaceReturn[0]:
            mc.parent(item,'rigStuff_grp')
        for item in attachSurfaceMirrorReturn[0]:
            mc.parent(item,'rigStuff_grp')
        """ hook up world scale """
        mc.connectAttr (worldScale,attachSurfaceReturn[1])
        mc.connectAttr (worldScale,attachSurfaceMirrorReturn[1])
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>Skin in the control joints
        """ Time to set skin our surface to our control joints """
        mc.skinCluster (leftSkinJointList,deformSurface[0],tsb=True, n=(deformSurface[0]+'_skinCluster'),maximumInfluences = 8, normalizeWeights = 1, dropoffRate=1,smoothWeights=.5,obeyMaxInfluences=True, weight = 1)
        mc.skinCluster (rightSkinJointList,deformSurface[1],tsb=True, n=(deformSurface[1]+'_skinCluster'),maximumInfluences = 8, normalizeWeights = 1, dropoffRate=1,smoothWeights=.5,obeyMaxInfluences=True, weight = 1)
    #>>>>>If we,re not mirrored, let's make our deform setup
    else:
        deformJointChains = []
        deformJointChains = joints.createJointChainsFromLoftSurface (nullBase,deformSurface[0],2,False)
        """ Connecting to surface """
        for chain in deformJointChains:
            attachSurfaceReturn = joints.attachJointChainToSurface (chain,deformSurface[0],'xyz','zup')
            tailHookJoint = distance.returnClosestObject (chain[0], spineChainList)
            """ break the connection so we can parent it"""
            """first return the original thing to follow"""
            parentBuffer = attributes.returnDriverObject ((chain[0]+'.translate'))
            attributes.doBreakConnection (chain[0]+'.translate')
            mc.parent (chain[0],tailHookJoint)
            """ reconstrain it to the driver"""
            constraintBuffer = mc.pointConstraint (parentBuffer,chain[0], maintainOffset = True)
            mc.rename (constraintBuffer[0],(chain[0]+'_pointConst'))
            """ store the skin joint data """
            for jnt in chain:
                attributes.storeObjNameToMessage (jnt,skinJointListGrp)
        """ hook up world scale  """
        partScaleBuffer = attachSurfaceReturn[1]
        mc.connectAttr (worldScale, partScaleBuffer)
        """ parent the scale stuff to rig stuff grp"""
        mc.select (cl=True)
        for item in attachSurfaceReturn[0]:
            mc.parent(item,'rigStuff_grp')
        """ Time to set skin our surface to our control joints """
        mc.skinCluster (skinJointList,deformSurface[0],tsb=True, n=(deformSurface[0]+'_skinCluster'),maximumInfluences = 8, normalizeWeights = 1, dropoffRate=1,smoothWeights=.5,obeyMaxInfluences=True, weight = 1)
        
        
    """ Setting up the joint starts"""
    if mode == 0:
        if mirror == True:
            for ctrl in masterCtrls:
                rigging.makeObjCtrl (ctrl,(ctrlSize*4))
                masterCtrlGrp = rigging.groupMeObject (ctrl,True)
                """ Get closest joint and connect the Cntrl """
                spineHookJoint = distance.returnClosestObject (masterCtrlGrp, spineChainList)
                mc.parent(masterCtrlGrp,spineHookJoint)
        else:
            rigging.makeObjCtrl (masterCtrl,(ctrlSize*4))
            masterCtrlGrp = rigging.groupMeObject (masterCtrl,True)
            """ Get closest joint and connect the Cntrl """
            spineHookJoint = distance.returnClosestObject (masterCtrlGrp, spineChainList)
            mc.parent(masterCtrlGrp,spineHookJoint)
    #else we need to connect the individual chains to the spine
    else:
        if mirror == True:
            for chain in leftSkinChains:
                chainCtrlGrp = rigging.groupMeObject (chain[0],True)
                spineHookJoint = distance.returnClosestObject (chainCtrlGrp, spineChainList)
                mc.parent(chainCtrlGrp,spineHookJoint)
            for chain in rightSkinChains:
                chainCtrlGrp = rigging.groupMeObject (chain[0],True)
                spineHookJoint = distance.returnClosestObject (chainCtrlGrp, spineChainList)
                mc.parent(chainCtrlGrp,spineHookJoint)
        else:
            for chain in skinChains:
                chainCtrlGrp = rigging.groupMeObject (chain[0],True)
                spineHookJoint = distance.returnClosestObject (chainCtrlGrp, spineChainList)
                mc.parent(chainCtrlGrp,spineHookJoint)
    #>>>>>>>>>>>>>>>>>>>>>>>>>>> Cleanup
    #mc.parent (distCleanupGrp, 'rigStuff_grp')
    #mc.parent (cleanupGrp, 'rigStuff_grp')
    #mc.parent (scaleHolderGrp, 'rigStuff_grp')

def returnSkinJoints(masterSkinListGrp):
    segmentSkinGroups = []
    skinJoints = []
    """return the segments"""
    segmentSkinGroups = attributes.returnMessageObjs(masterSkinListGrp)
    for grp in segmentSkinGroups:
        listBuffer = attributes.returnMessageObjs(grp)
        for jnt in listBuffer:
            skinJoints.append (jnt)
    return skinJoints
    
                        
def surfRigger(objectNull,anchor,worldScale,mirror,mode,jointsPerChain,deformChains,ctrlChains):
    """ Get variables"""
    nullBase = names.stripSuffixObj (objectNull)
    templateNull = (nullBase + '_templateNull')
    moverNull = (nullBase + '_mover')
    templateNullMessageData = []
    templateNullMessageData = attributes.returnMessageAttrs (templateNull)
    templateObjects = []
    coreNamesList = []
    spineJointNumber = int(mc.getAttr (objectNull+'.rollJoints'))
    #spineChainList = search.returnChildrenJoints (spineChain)
    spineChainList = []
    spineChainList.append (anchor)
    jointChains = []
    for set in templateNullMessageData:
        templateObjects.append (set[1])
        coreNamesList.append (set[0])
    #>>>>>>>>>>>>>>>>>>>>>Store skin joint data
    """ check for master skin info group """
    if mc.objExists ('master_skinJntList_grp'):
        masterSkinJointList = ('master_skinJntList_grp')
    else:
        masterSkinJointList = mc.group (n= ('master_skinJntList_grp'), w=True, empty=True)
        mc.parent(masterSkinJointList,'rigStuff_grp')
    """ check for segment skin info group """
    if mc.objExists (nullBase+'_skinJntList_grp'):
        skinJointListGrp = (nullBase+'_skinJntList_grp')
    else:
        skinJointListGrp = mc.group (n= (nullBase+'_skinJntList_grp'), w=True, empty=True)
    attributes.storeObjNameToMessage (skinJointListGrp,masterSkinJointList)
    mc.parent (skinJointListGrp,masterSkinJointList)
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """ Rebuild curve - with actual curve in it!"""
    mc.rebuildCurve ((templateObjects[3]), ch=0, rpo=1, rt=0, end=0, kr=0, kcp=0, kep=1, kt=0, s=jointsPerChain, d=1, tol=5)
    mc.rebuildCurve ((templateObjects[7]), ch=0, rpo=1, rt=0, end=0, kr=0, kcp=0, kep=1, kt=0, s=jointsPerChain, d=1, tol=5)
    mc.rebuildCurve ((templateObjects[11]), ch=0, rpo=1, rt=0, end=0, kr=0, kcp=0, kep=1, kt=0, s=jointsPerChain, d=1, tol=5)
    """ Reverse the curve """
    mc.reverseCurve ((templateObjects[3]),ch=False,rpo=True)
    mc.reverseCurve ((templateObjects[7]),ch=False,rpo=True)
    mc.reverseCurve ((templateObjects[11]),ch=False,rpo=True)
    """ loft our surface to figure out joint positions, then delete it"""
    controlSurface = mc.loft ([templateObjects[3],templateObjects[7],templateObjects[11]],name=(nullBase+'_surf'),ss=(ctrlChains-mode),ch=1,u=1,c=0,ar=1,d=3,rn=0,po=0,rsn=True)
    mc.select (cl=True)
    jointChains = joints.createJointChainsFromLoftSurface (nullBase,controlSurface[0],2,False)
    frontChain = jointChains[0]
    backChain = jointChains[-1]
    """ Chain - orienting, sizing """
    for chain in jointChains:
        joints.orientJointChain (chain, 'xyz', 'zup')
        joints.setGoodJointRadius(chain,.5)
    #IF we have mode 0, gotta make a main ctrl
    if mode == 0:
        midChain = []
        if (len(jointChains)) > 3:
            midChain = jointChains[int(len(jointChains)/2)]
        else:
            midChain = jointChains[1]
            jointChains.remove(midChain)
        if ctrlChains > 2:
            masterCtrlBuffer = mc.duplicate (midChain[0],parentOnly=True)
        else:
            masterCtrlBuffer = midChain[0]
            mc.delete (midChain[1])
        masterCtrl = mc.rename (masterCtrlBuffer,(nullBase+'_master_anim'))
        position.movePointSnap(masterCtrl,moverNull)
        """ temp parenting the master control for mirroring purposes """
        spineHookJoint = distance.returnClosestObject (masterCtrl, spineChainList)
        mc.parent (masterCtrl,spineHookJoint)
    mc.delete (controlSurface[0])
    #>>>>>>>>>>>>Parent time
    """ Get closest joint """
    if mode == 0:
        for chain in jointChains:
            mc.parent (chain[0],masterCtrl)
    else:
        for chain in jointChains:
            tailHookJoint = distance.returnClosestObject (chain[0], spineChainList)
            mc.parent (chain[0],tailHookJoint)
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>> Ctrl Joints to Ctrls
    cnt = 0
    for chain in jointChains:
        ctrlSize = (distance.returnAverageDistanceBetweenObjects (chain)/2)
        for jnt in chain[0:-1]:
            rigging.makeObjCtrl (jnt,ctrlSize)
        """ adds our Anim tag """
        chainBuffer = []
        chainBuffer = names.addSuffixList ('anim', chain)
        jointChains[cnt]= chainBuffer
        cnt +=1
    #>>>>>>>>>>>>>>>>>>>Mirroring while getting chain info
    """ If mirroring ...."""
    if mirror == True:
        # if we have a main control
        leftSkinChains = []
        rightSkinChains = []
        masterCtrls = []
        if mode == 0:
            leftChain = []
            rightChain = []
            finHeirarchy = []
            finHeirarchy.append (masterCtrl)
            children = search.returnChildrenJoints (masterCtrl)
            finHeirarchy += children
            leftChain = names.addPrefixList ('left',finHeirarchy)
            masterCtrl = leftChain [0]
            rightChainBuffer = mc.mirrorJoint (masterCtrl,mirrorYZ=True,mirrorBehavior=True, searchReplace =['left','right'])
            rightChainJointBuffer = mc.ls (rightChainBuffer,type='joint')
            rightChain = rightChainJointBuffer
            leftSkinChains.append(leftChain)
            rightSkinChains.append(rightChain)
            masterCtrls.append(leftChain[0])
            masterCtrls.append(rightChain[0])
        else:
            for chain in jointChains:
                leftChain =[]
                leftChain = names.addPrefixList ('left',chain)
                rightChainBuffer = (mc.mirrorJoint (leftChain[0],mirrorYZ=True,mirrorBehavior=True, searchReplace =['left','right']))
                rightChainJointBuffer = mc.ls (rightChainBuffer,type='joint')
                rightChain = rightChainJointBuffer
                rightSkinChains.append (rightChainJointBuffer)
                leftSkinChains.append (leftChain)
        """ complile our chains to lists of skin joints """
        leftSkinJointList=[]
        rightSkinJointList=[]
        for chain in leftSkinChains:
            for jnt in chain:
                leftSkinJointList.append (jnt)
        for chain in rightSkinChains:
            for jnt in chain:
                rightSkinJointList.append (jnt)
        """if we're not mirroring, let's return our skin joints for the deformation surface"""
    else:
        skinJointList = []
        skinChains = []
        for chain in jointChains:
            skinChains.append (chain)
            for jnt in chain:
                skinJointList.append (jnt)
                
    #>>>>>>>>>>>>>>>>>>>>>>>>>>Time to make the deformation surface stuff
    """ Rebuild curve - with actual curve in it!"""
    #mc.rebuildCurve ((templateObjects[3]), ch=0, rpo=1, rt=0, end=0, kr=0, kcp=0, kep=1, kt=0, s=(3), d=1, tol=5)
    #mc.rebuildCurve ((templateObjects[7]), ch=0, rpo=1, rt=0, end=0, kr=0, kcp=0, kep=1, kt=0, s=(3), d=1, tol=5)
    """ loft our surface to figure out joint positions, then delete it"""
    deformSurface = mc.loft ([templateObjects[3],templateObjects[7],templateObjects[11]],name=(nullBase+'_surf'),ss=(deformChains-1),ch=0,u=1,c=0,ar=1,d=3,rn=0,po=0,rsn=True)
    if mirror == True:
        deformSurfaceNameBuffer = deformSurface[0]
        """we have a surface to mirror..."""
        surfaceMirrorBuffer = mc.duplicate (deformSurface[0])
        mc.setAttr ((surfaceMirrorBuffer[0]+'.sx'),-1)
        leftBuffer = mc.rename (deformSurface[0],('left_'+deformSurfaceNameBuffer))
        rightBuffer = mc.rename (surfaceMirrorBuffer[0],('right_'+deformSurfaceNameBuffer))
        deformSurface[0]=leftBuffer
        deformSurface.append(rightBuffer)
        leftDeformJointChains = joints.createJointChainsFromLoftSurface (('left_'+nullBase),deformSurface[0],2,False)
        rightDeformJointChains = joints.createJointChainsFromLoftSurface (('right_'+nullBase),deformSurface[1],2,False)
        """ Connecting to surface """
        for chain in leftDeformJointChains:
            attachSurfaceReturn = joints.attachJointChainToSurface (chain,deformSurface[0],'xyz','zup')
            tailHookJoint = distance.returnClosestObject (chain[0], spineChainList)
            """ break the connection so we can parent it"""
            """first return the original thing to follow"""
            parentBuffer = attributes.returnDriverObject ((chain[0]+'.translate'))
            attributes.doBreakConnection (chain[0]+'.translate')
            #mc.parent (chain[0],tailHookJoint)
            """ reconstrain it to the driver"""
            constraintBuffer = mc.pointConstraint (parentBuffer,chain[0], maintainOffset = True)
            mc.rename (constraintBuffer[0],(chain[0]+'_pointConst'))
            """ store the skin joint data """
            for jnt in chain:
                attributes.storeObjNameToMessage (jnt,skinJointListGrp)

        for chain in rightDeformJointChains:
            attachSurfaceMirrorReturn = joints.attachJointChainToSurface (chain,deformSurface[1],'xyz','zup')
            tailHookJoint = distance.returnClosestObject (chain[0], spineChainList)
            """ break the connection s we can parent it"""
            """first return the original thing to follow"""
            parentBuffer = attributes.returnDriverObject ((chain[0]+'.translate'))
            attributes.doBreakConnection (chain[0]+'.translate')
            #mc.parent (chain[0],tailHookJoint)
            """ reconstrain it to the driver"""
            constraintBuffer = mc.pointConstraint (parentBuffer,chain[0], maintainOffset = True)
            mc.rename (constraintBuffer[0],(chain[0]+'_pointConst'))
            """ store the skin joint data """
            for jnt in chain:
                attributes.storeObjNameToMessage (jnt,skinJointListGrp)

        """ parent the scale stuff to rig stuff grp"""
        mc.select (cl=True)
        for item in attachSurfaceReturn[0]:
            mc.parent(item,'rigStuff_grp')
        for item in attachSurfaceMirrorReturn[0]:
            mc.parent(item,'rigStuff_grp')
        """ hook up world scale """
        mc.connectAttr (worldScale,attachSurfaceReturn[1])
        mc.connectAttr (worldScale,attachSurfaceMirrorReturn[1])
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>Skin in the control joints
        """ Time to set skin our surface to our control joints """
        mc.skinCluster (leftSkinJointList,deformSurface[0],tsb=True, n=(deformSurface[0]+'_skinCluster'),maximumInfluences = 8, normalizeWeights = 1, dropoffRate=1,smoothWeights=.5,obeyMaxInfluences=True, weight = 1)
        mc.skinCluster (rightSkinJointList,deformSurface[1],tsb=True, n=(deformSurface[1]+'_skinCluster'),maximumInfluences = 8, normalizeWeights = 1, dropoffRate=1,smoothWeights=.5,obeyMaxInfluences=True, weight = 1)
    #>>>>>If we,re not mirrored, let's make our deform setup
    else:
        deformJointChains = []
        deformJointChains = joints.createJointChainsFromLoftSurface (nullBase,deformSurface[0],2,False)
        """ Connecting to surface """
        for chain in deformJointChains:
            attachSurfaceReturn = joints.attachJointChainToSurface (chain,deformSurface[0],'xyz','zup')
            tailHookJoint = distance.returnClosestObject (chain[0], spineChainList)
            """ break the connection so we can parent it"""
            """first return the original thing to follow"""
            parentBuffer = attributes.returnDriverObject ((chain[0]+'.translate'))
            attributes.doBreakConnection (chain[0]+'.translate')
            #mc.parent (chain[0],tailHookJoint)
            """ reconstrain it to the driver"""
            constraintBuffer = mc.pointConstraint (parentBuffer,chain[0], maintainOffset = True)
            mc.rename (constraintBuffer[0],(chain[0]+'_pointConst'))
            """ store the skin joint data """
            for jnt in chain:
                attributes.storeObjNameToMessage (jnt,skinJointListGrp)
        """ hook up world scale  """
        partScaleBuffer = attachSurfaceReturn[1]
        mc.connectAttr (worldScale, partScaleBuffer)
        """ parent the scale stuff to rig stuff grp"""
        mc.select (cl=True)
        for item in attachSurfaceReturn[0]:
            mc.parent(item,'rigStuff_grp')
        """ Time to set skin our surface to our control joints """
        mc.skinCluster (skinJointList,deformSurface[0],tsb=True, n=(deformSurface[0]+'_skinCluster'),maximumInfluences = 8, normalizeWeights = 1, dropoffRate=1,smoothWeights=.5,obeyMaxInfluences=True, weight = 1)
        
        
    """ Setting up the joint starts"""
    if mode == 0:
        if mirror == True:
            for ctrl in masterCtrls:
                rigging.makeObjCtrl (ctrl,(ctrlSize*4))
                masterCtrlGrp = rigging.groupMeObject (ctrl,True)
                """ Get closest joint and connect the Cntrl """
                spineHookJoint = distance.returnClosestObject (masterCtrlGrp, spineChainList)
                mc.parent(masterCtrlGrp,spineHookJoint)
        else:
            rigging.makeObjCtrl (masterCtrl,(ctrlSize*4))
            masterCtrlGrp = rigging.groupMeObject (masterCtrl,True)
            """ Get closest joint and connect the Cntrl """
            spineHookJoint = distance.returnClosestObject (masterCtrlGrp, spineChainList)
            mc.parent(masterCtrlGrp,spineHookJoint)
    #else we need to connect the individual chains to the spine
    else:
        if mirror == True:
            for chain in leftSkinChains:
                chainCtrlGrp = rigging.groupMeObject (chain[0],True)
                spineHookJoint = distance.returnClosestObject (chainCtrlGrp, spineChainList)
                mc.parent(chainCtrlGrp,spineHookJoint)
            for chain in rightSkinChains:
                chainCtrlGrp = rigging.groupMeObject (chain[0],True)
                spineHookJoint = distance.returnClosestObject (chainCtrlGrp, spineChainList)
                mc.parent(chainCtrlGrp,spineHookJoint)
        else:
            for chain in skinChains:
                chainCtrlGrp = rigging.groupMeObject (chain[0],True)
                spineHookJoint = distance.returnClosestObject (chainCtrlGrp, spineChainList)
                mc.parent(chainCtrlGrp,spineHookJoint)
    #>>>>>>>>>>>>>>>>>>>>>>>>>>> Cleanup
    #mc.parent (distCleanupGrp, 'rigStuff_grp')
    #mc.parent (cleanupGrp, 'rigStuff_grp')
    #mc.parent (scaleHolderGrp, 'rigStuff_grp')
             
                
def rigSpine (crvName,tailCntrlJoints,waveControlObject,splitJoints):
    """ Rebuild curve - with actual curve in it!"""
    """ first have to make our reg spine""" 
    mc.rebuildCurve (crvName, ch=0, rpo=1, rt=0, end=0, kr=0, kcp=0, kep=1, kt=0, s=(splitJoints), d=1, tol=5)
    """ Make joint chains"""
    spineJoints = joints.createJointsFromCurve (crvName,'spine')
    """ set joint radius """
    joints.setGoodJointRadius (spineJoints,1)
    """ Orienting the joint chain """
    joints.orientJointChain (spineJoints, 'xyz', 'zup')
    
    """ Renaming the joint chain """
    spineJointsBuffer = names.renameJointChainList (spineJoints, 'tailStart', 'tail')
    spineJoints = spineJointsBuffer
    """ removing initial bind from the spine curve """
    mc.delete ('bindPose1')
    mc.delete ('skinCluster1')
    """ Makes our control surface """
    controlSurface = makeJointControlSurfaceFish(spineJoints[0],tailCntrlJoints,'y','tail')
    """ parenting the tail joints """
    rigging.parentListToHeirarchy (tailCntrlJoints)
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>auto swim stuff
    """ Creating our deformation surface """
    deformMeshBuffer = mc.duplicate (controlSurface)
    deformMesh = mc.rename (deformMeshBuffer[0],(controlSurface[0]+'_defmesh'))
    """ Creates  our wave deformer """
    deformerBuffer = mc.nonLinear (deformMesh, type = 'wave', name = 'swimWave')
    waveDeformer = mc.rename (deformerBuffer[0], 'waveDeformer')
    waveDeformerHandle = mc.rename (deformerBuffer[1], 'waveDeformerHandle')
    """ move the handle """
    position.movePointSnap (waveDeformerHandle,spineJoints[0])
    mc.setAttr ((waveDeformerHandle+'.rx'),90)
    mc.setAttr ((waveDeformerHandle+'.ry'),90)
    """ set some variables """
    mc.setAttr ((waveDeformer+'.dropoff'),1)
    mc.setAttr ((waveDeformer+'.dropoffPosition'),1)
    mc.setAttr ((waveDeformer+'.maxRadius'),2)
    """ make our blendshape node and reorder things"""
    blendshapeNode = mc.blendShape (deformMesh, controlSurface[0], name = 'swim_bsNode' )
    mc.reorderDeformers ("tweak2", blendshapeNode[0],controlSurface[0])
    """ add some attrs to our wave control object """
    attributes.addSectionBreakAttrToObj (waveControlObject, 'swim')
    attributes.addFloatAttributeToObject (waveControlObject, 'auto', min = 0, max = 1, dv =0)
    attributes.addFloatAttributeToObject (waveControlObject, 'speed', -100, 100, 0)
    attributes.addFloatAttributeToObject (waveControlObject, 'wavelength', 0, 10, 5)
    attributes.addFloatAttributeToObject (waveControlObject, 'amplitude', 0, 10, 0)
    attributes.addFloatAttributeToObject (waveControlObject, 'dropoff', 0, 1, 1)
    attributes.addFloatAttributeToObject (waveControlObject, 'dropoffPosition', 0, 1, 0)
    attributes.addFloatAttributeToObject (waveControlObject, 'minRadius', 0, 10, 0)
    attributes.addFloatAttributeToObject (waveControlObject, 'maxRadius', 0, 10, 10)
    """ connect a few attrs """
    mc.connectAttr ((waveControlObject+'.auto'),(blendshapeNode[0]+'.'+deformMesh))
    mc.connectAttr ((waveControlObject+'.wavelength'),(waveDeformer+'.wavelength'))
    mc.connectAttr ((waveControlObject+'.amplitude'),(waveDeformer+'.amplitude'))
    mc.connectAttr ((waveControlObject+'.dropoff'),(waveDeformer+'.dropoff'))
    mc.connectAttr ((waveControlObject+'.dropoffPosition'),(waveDeformer+'.dropoffPosition'))
    mc.connectAttr ((waveControlObject+'.minRadius'),(waveDeformer+'.minRadius'))
    mc.connectAttr ((waveControlObject+'.maxRadius'),(waveDeformer+'.maxRadius'))
    """ set some good base values """
    mc.setAttr ((waveControlObject+'.speed'),1)
    mc.setAttr ((waveControlObject+'.wavelength'),4)
    mc.setAttr ((waveControlObject+'.amplitude'),.3)
    mc.setAttr ((waveControlObject+'.dropoff'),1)
    mc.setAttr ((waveControlObject+'.dropoffPosition'),1)
    mc.setAttr ((waveControlObject+'.maxRadius'),2)
    """ sets up swim speed """
    nodes.offsetCycleSpeedControlNodeSetup (waveDeformer,(waveControlObject+'.speed'),90,-10)
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>> Head control and joint
    headJointBuffer = mc.duplicate ('head_anim')
    headJoint = mc.rename (headJointBuffer, 'head_jnt')
    headCtrlGrp = rigging.groupMeObject ('head_anim',True)
    #mc.parent (headJoint, spineJoints[0])
    mc.parent (headJoint, 'move_anim')
    contsBuffer = mc.parentConstraint (spineJoints[0], headCtrlGrp, maintainOffset = True)
    mc.rename (contsBuffer,(headCtrlGrp+'_prntConst'))
    contsBuffer = mc.parentConstraint ('head_anim', headJoint, maintainOffset = True)
    mc.rename (contsBuffer,(headJoint+'_prntConst'))
    mc.parent (headCtrlGrp,'move_anim')
    
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Clean stuff
    """ deform group """
    deformGrp = mc.group (n= 'swimDeform_grp', w=True, empty=True)
    mc.parent (waveDeformerHandle,deformGrp)
    mc.parent (deformMesh,deformGrp)
    mc.setAttr ((deformGrp+'.v'), 0)
    mc.setAttr ((controlSurface[0]+'.v'),0)
    """ delete placement stuff """
    mc.delete ('curvePlacementStuff')
    mc.parent (tailCntrlJoints[0],waveControlObject)
    mc.parent (deformGrp, 'rigStuff_grp')

    
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>> Ctrl Joints to Ctrls
    ctrlSize = (distance.returnAverageDistanceBetweenObjects (tailCntrlJoints))
    curves.parentShape ('head_anim', 'sampleCtrlZ')
    for ctrl in tailCntrlJoints:
        rigging.makeObjCtrl (ctrl,ctrlSize)
 
    #>>>>>>>>>>>>>>>>>>>>>Store skin joint data
    """ check for master skin info group """
    name = 'spine'
    if mc.objExists ('master_skinJntList_grp'):
        masterSkinJointList = ('master_skinJntList_grp')
    else:
        masterSkinJointList = mc.group (n= ('master_skinJntList_grp'), w=True, empty=True)
        mc.parent(masterSkinJointList,'rigStuff_grp')
    """ check for segment skin info group """
    if mc.objExists (name+'_skinJntList_grp'):
        skinJointList = (name+'_skinJntList_grp')
    else:
        skinJointList = mc.group (n= (name+'_skinJntList_grp'), w=True, empty=True)
    mc.parent (skinJointList,masterSkinJointList)
    attributes.storeObjNameToMessage (skinJointList,masterSkinJointList)
    """ store the skin joint data """
    for jnt in spineJoints:
        attributes.storeObjNameToMessage (jnt,skinJointList)
    attributes.storeObjNameToMessage (headJoint,skinJointList)
            
    
def makeJointControlSurfaceFish(startJoint,controlJointList,outChannel,name):
    """ Makes a ricgmon surface for ricgmon rigging """
    heirarchyJoints = []
    heirarchyJoints.append (startJoint)
    childrenBuffer = []
    controlJointGroups = []
    """ Makes some transform groups for our groups"""
    """ Get joint list """
    for jnt in (mc.listRelatives (startJoint, ad = True, type = 'joint')):
        childrenBuffer.append (jnt)
    childrenBuffer.reverse ()
    heirarchyJoints += childrenBuffer
    """ return a good length for out loft curves """
    length = (distance.returnDistanceBetweenObjects (heirarchyJoints[0], heirarchyJoints[-1])/2)
    loftCurveList = []
    crvPosBuffer = []
    crvPosBuffer.append ([0,0,0])
    if outChannel == 'x':
        crvPosBuffer.append ([length,0,0])
    elif outChannel == 'y':
        crvPosBuffer.append ([0,length,0])
    elif outChannel == 'z':
        crvPosBuffer.append ([0,0,length])
    crvPosBuffer.reverse ()
    """ for each joint, make a loft curve and snap it to the joint it goes with """
    for jnt in heirarchyJoints:
        crvBuffer = mc.curve (d=1, p = crvPosBuffer , os=True, n=(jnt+'_tmpCrv'))
        mc.xform (crvBuffer, cp = True)
        posBuffer = distance.returnWorldSpacePosition (jnt)
        cnstBuffer = mc.parentConstraint ([jnt], [crvBuffer], maintainOffset = False)
        mc.delete (cnstBuffer)
        loftCurveList.append (crvBuffer)
    controlSurface = mc.loft (loftCurveList, reverseSurfaceNormals = True, ch = False, uniform = True, degree = 3, n = (name+'_surf') )
    """ deletes our loft curve list"""
    for crv in loftCurveList:
        mc.delete (crv)
    cvList = (mc.ls ([controlSurface[0]+'.cv[*]'],flatten=True))
    """ Time to set skin our surface to our control joints """
    surfaceSkinCluster = mc.skinCluster (controlJointList,controlSurface[0],tsb=True, n=(controlSurface[0]+'_skinCluster'),maximumInfluences = 3, normalizeWeights = 1, dropoffRate=2,smoothWeights=.5,obeyMaxInfluences=True, weight = 1)
    #surfaceSkinCluster = mc.skinCluster (controlJointList,controlSurface,tsb=True, n=(controlSurface[0]+'_skinCluster'),maximumInfluences = 5, normalizeWeights = 2, dropoffRate=4,smoothWeights=.5,forceNormalizeWeights=True)
    """ Make our groups to follow the surface and drive out """
    posGroups = []
    upGroups = []
    cnt = 0
    for jnt in heirarchyJoints:
        posGroups.append (mc.group (n= ('%s%s' % (jnt,'_Pos_grp')), w=True, empty=True))
        upGroups.append (mc.group (n= ('%s%s' % (jnt,'_Up_grp')), w=True, empty=True))
        mc.parent (upGroups[cnt],posGroups[cnt])
        cnt +=1
    """ Make our v values for our position info groups"""
    vValues = []
    vValues.append (.5)
    cnt = 0
    for item in heirarchyJoints:
        vValues.append (cnt + 1)
        cnt += 1
    """ Make our position info nodes"""
    posInfoNodes = []
    cnt = 0
    for grp in posGroups:
        node = mc.createNode ('pointOnSurfaceInfo',name= (grp+'_posInfoNode'))
        print node
        posInfoNodes.append (node)
        """ Connect the info node to the surface """                  
        mc.connectAttr ((controlSurface[0]+'Shape.worldSpace'),(posInfoNodes[cnt]+'.inputSurface'))
        """ Contect the pos group to the info node"""
        mc.connectAttr ((posInfoNodes[cnt]+'.position'),(grp+'.translate'))
        """ Connect the U tangent attribute to the child of our first group """
        mc.connectAttr ((posInfoNodes[cnt]+'.tangentU'),(upGroups[cnt]+'.translate'))
        mc.setAttr ((posInfoNodes[cnt]+'.parameterU'),.5)
        mc.setAttr ((posInfoNodes[cnt]+'.parameterV'),(vValues[cnt]))
        cnt += 1
        
        
    """ Make our measure nodes to keep joint position """    
    posPairsList = lists.parseListToPairs (posInfoNodes)
    posDistConnections = []
    poseDistNameList = []
    for pair in posPairsList:
        distanceInfoBuffer = distance.createDistanceNodeBetweenPosInfoNodes (pair[0],pair[1])
        posDistConnections.append(distanceInfoBuffer[2])
        poseDistNameList.append(distanceInfoBuffer[0])
        """ connect the distances to our stretch translation channels on our joints """
    """ connect the distances to our stretch translation channels on our joints """
    #find it
    directionCap = 'X'
    cnt = 0
    jointLengths = []
    mdNodes = []
    """ need to make our master scale connector"""
    scaleHolderGrp= (controlSurface[0]+'_scaleHolder_grp')
    masterScaleAttrBuffer = (scaleHolderGrp+'.worldScale')
    if mc.objExists (scaleHolderGrp):
        pass
    else:
        mc.group (n= scaleHolderGrp, w=True, empty=True)
        mc.addAttr (scaleHolderGrp, ln = 'worldScale',  at = 'float', hidden=False )
        mc.setAttr(masterScaleAttrBuffer,1)
    """ return our default lengths and store them,then run them through an md node to return our scale values """
    for jnt in heirarchyJoints[0:-1]:
        lengthBuffer = mc.getAttr (posDistConnections[cnt])
        jointLengths.append (lengthBuffer)
        #mc.addAttr (jnt, ln = 'baseLength',  at = 'float')
        mc.addAttr (scaleHolderGrp, ln = (jnt+'_baseLength'),  at = 'float')
        jntAttrBuffer = (scaleHolderGrp+'.'+jnt+'_baseLength')
        mc.setAttr (jntAttrBuffer,jointLengths[cnt])
        mdNodeBuffer = nodes.createNamedNode ((jnt+'_jntScale'), 'multiplyDivide')
        mdNodes.append(mdNodeBuffer)
        mc.setAttr ((mdNodeBuffer+'.operation'),2)
        mc.connectAttr((posDistConnections[cnt]),(mdNodeBuffer+'.input1X'))
        mc.connectAttr((jntAttrBuffer),(mdNodeBuffer+'.input2X'))
        mc.connectAttr(masterScaleAttrBuffer,(jnt+'.scaleY'))
        mc.connectAttr(masterScaleAttrBuffer,(jnt+'.scaleZ'))
        mc.connectAttr((mdNodeBuffer+'.output.outputX'),(jnt+'.scale'+directionCap))
        cnt+=1
    """ """
    #mc.connectAttr (
    
    """ SET SPECIAL CONDITION FOR FIRST POS GROUP """
    #mc.setAttr ((posInfoNodes[0]+'.parameterV'),0)
    """Clean up stuff """
    cleanupGrp = mc.group (n= 'surfacePosFollowStuff_grp', w=True, empty=True)
    for grp in posGroups:
        mc.parent (grp, cleanupGrp)
    """ make some IK effectors and connect everything up"""
    effectorList = []
    cnt = (len(heirarchyJoints) - 1)
    firstTermCount = 0
    secondTermCount = 1
    while cnt > 0:
        effector = mc.ikHandle (name = (heirarchyJoints[firstTermCount]+'_ikHandle') , startJoint=heirarchyJoints[firstTermCount], endEffector = heirarchyJoints[secondTermCount], setupForRPsolver = True, solver = 'ikRPsolver', enableHandles=True )
        """ if it's the not the last effector, do this """
        if cnt > 1:
            mc.parent (effector[0],posGroups[secondTermCount])
        """ if it is, parent it to the last controlJoint """
        if cnt == 1:
            mc.parent (effector[0],posGroups[secondTermCount])
        effectorList.append (effector[0])
        cnt-=1
        firstTermCount += 1
        secondTermCount += 1
        if cnt == 0:
            break
    """ let's make some  pole vector constraints"""
    #----------->>>>> Need to find a good way of "discovering" correct twist for the effectors
    cnt = 0
    """ Connect first joint to surface """
    mc.connectAttr ((posGroups[0]+'.translate'),(heirarchyJoints[0]+'.translate'))
    for effector in effectorList:
            #print ('Constrain '+effector+' to '+ upGroups[cnt])
            poleVector = mc.poleVectorConstraint (upGroups[cnt],effector,name = (effector+'_pvConst'))
            """ fix the twist"""
            if (len(effectorList) - cnt) == 0:
                mc.setAttr ((effector+'.twist'),-180)
            elif cnt == 0:
                mc.setAttr ((effector+'.twist'),0)            
            else:
                mc.setAttr ((effector+'.twist'),-90)
            cnt+=1
    #
    """return all our data together to return"""
    """ clean up measure stuff """
    if mc.objExists (name+'_measureStuff_grp'):
        distCleanupGrp = (name+'_measureStuff_grp')
    else:
        distCleanupGrp = mc.group (n= (name+'_measureStuff_grp'), w=True, empty=True)
    for dist in poseDistNameList:
        mc.parent (dist, distCleanupGrp)
        mc.setAttr ((dist+'.v'),0)
    mc.parent (distCleanupGrp, 'rigStuff_grp')
    mc.parent (cleanupGrp, 'rigStuff_grp')
    mc.parent (scaleHolderGrp, 'rigStuff_grp')

    """ connect master scale to the master  """
    mc.connectAttr(('placement_anim.sy'),masterScaleAttrBuffer)
    return controlSurface
    
def eelFinSwimmer (controlSurface,waveControlObject):
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>auto swim stuff
    """ Creating our deformation surface """
    deformMeshBuffer = mc.duplicate (controlSurface)
    deformMesh = mc.rename (deformMeshBuffer[0],(controlSurface+'_defmesh'))
    """ Creates  our wave deformer """
    deformerBuffer = mc.nonLinear (deformMesh, type = 'wave', name = 'swimWave')
    waveDeformer = mc.rename (deformerBuffer[0], 'waveDeformer')
    waveDeformerHandle = mc.rename (deformerBuffer[1], 'waveDeformerHandle')
    """ move the handle """
    mc.setAttr ((waveDeformerHandle+'.rx'),90)
    mc.setAttr ((waveDeformerHandle+'.ry'),90)
    """ set some variables """
    mc.setAttr ((waveDeformer+'.dropoff'),1)
    mc.setAttr ((waveDeformer+'.dropoffPosition'),1)
    mc.setAttr ((waveDeformer+'.maxRadius'),2)
    """ make our blendshape node and reorder things"""
    blendshapeNode = mc.blendShape (deformMesh, controlSurface, name = 'swim_bsNode' )
    mc.reorderDeformers ("tweak5", blendshapeNode[0],controlSurface)
    """ add some attrs to our wave control object """
    attributes.addSectionBreakAttrToObj (waveControlObject, 'swim')
    attributes.addFloatAttributeToObject (waveControlObject, 'auto', 0, 1, 0)
    attributes.addFloatAttributeToObject (waveControlObject, 'speed', -100, 100, 0)
    attributes.addFloatAttributeToObject (waveControlObject, 'wavelength', 0, 10, 5)
    attributes.addFloatAttributeToObject (waveControlObject, 'amplitude', 0, 10, 0)
    attributes.addFloatAttributeToObject (waveControlObject, 'dropoff', 0, 1, 1)
    attributes.addFloatAttributeToObject (waveControlObject, 'dropoffPosition', 0, 1, 0)
    attributes.addFloatAttributeToObject (waveControlObject, 'minRadius', 0, 10, 0)
    attributes.addFloatAttributeToObject (waveControlObject, 'maxRadius', 0, 10, 10)
    """ connect a few attrs """
    mc.connectAttr ((waveControlObject+'.auto'),(blendshapeNode[0]+'.'+deformMesh))
    mc.connectAttr ((waveControlObject+'.wavelength'),(waveDeformer+'.wavelength'))
    mc.connectAttr ((waveControlObject+'.amplitude'),(waveDeformer+'.amplitude'))
    mc.connectAttr ((waveControlObject+'.dropoff'),(waveDeformer+'.dropoff'))
    mc.connectAttr ((waveControlObject+'.dropoffPosition'),(waveDeformer+'.dropoffPosition'))
    mc.connectAttr ((waveControlObject+'.minRadius'),(waveDeformer+'.minRadius'))
    mc.connectAttr ((waveControlObject+'.maxRadius'),(waveDeformer+'.maxRadius'))
    """ set some good base values """
    mc.setAttr ((waveControlObject+'.speed'),1)
    mc.setAttr ((waveControlObject+'.wavelength'),4)
    mc.setAttr ((waveControlObject+'.amplitude'),.3)
    mc.setAttr ((waveControlObject+'.dropoff'),1)
    mc.setAttr ((waveControlObject+'.dropoffPosition'),1)
    mc.setAttr ((waveControlObject+'.maxRadius'),2)
    """ sets up swim speed """
    nodes.offsetCycleSpeedControlNodeSetup (waveDeformer,(waveControlObject+'.speed'),90,-10)
    
def fixPoleVectorsCauseJoshIsAMoron ():
    groupsToProcess = (mc.ls (sl=True))
    for group in groupsToProcess:
        groupPair = mc.listRelatives (group, children=True)
        if len(groupPair) == 2:
            if (mc.listRelatives (groupPair[1], children=True)) > 0:
                print (groupPair[1]+' has constraint')
            else:
                poleVector = mc.poleVectorConstraint (groupPair[0],groupPair[1],name = ('joshIsAGoob_pvConst')) 
        else:
            print 'not needed'
    

    
    
