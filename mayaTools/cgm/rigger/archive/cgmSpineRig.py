import maya.cmds as mc

from cgm.lib.classes import NameFactory

from cgm.lib import (joints,
                     rigging,
                     attributes,
                     names,
                     distance,
                     search,
                     dictionary,
                     settings,
                     lists,
                     modules,
                     skinning,
                     constraints,
                     curves)

import copy



typesDictionary = dictionary.initializeDictionary(settings.getTypesDictionaryFile())
namesDictionary = dictionary.initializeDictionary( settings.getNamesDictionaryFile())
settingsDictionary = dictionary.initializeDictionary( settings.getSettingsDictionaryFile())


def rigSpine(moduleNull):
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    #>>>Get our info
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    partName = NameFactory.returnUniqueGeneratedName(moduleNull, ignore = 'cgmType')
    
    """ template null """
    templateNull = modules.returnTemplateNull(moduleNull)
    templateNullData = attributes.returnUserAttrsToDict (templateNull)
    jointOrientation = modules.returnSettingsData('jointOrientation')
    templateRoot =  modules.returnInfoNullObjects(moduleNull,'templatePosObjects',types='templateRoot')
    

    """ AutonameStuff """
    divider = NameFactory.returnCGMDivider()
    
    """ control helper objects """
    controlTemplateObjects = modules.returnInfoNullObjects(moduleNull,'templateControlObjects',types='all')
    controlTemplateObjects = distance.returnDistanceSortedList(templateRoot,controlTemplateObjects)
        
    print 'controlTemplateObjects...'
    print controlTemplateObjects 
    
    """size list of template control objects """
    controlTemplateObjectsSizes = []
    for obj in controlTemplateObjects:
        controlTemplateObjectsSizes.append(distance.returnAbsoluteSizeCurve(obj))
    print 'sizes...'
    print controlTemplateObjectsSizes
    
    """ Skin Joints """
    skinJoints = modules.returnInfoNullObjects(moduleNull,'skinJoints',types='all')
    skinJoints = distance.returnDistanceSortedList(templateRoot,skinJoints)
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    #>>> Make Controls
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>    
    """ control options """
    fk = templateNullData.get('fk')
    ik = templateNullData.get('ik')
    stretch = templateNullData.get('stretch')
    bend = templateNullData.get('bend')
    
    """controls to make """
    controlsToMake =[]
    controlsToMake.append('cog')
    
    if fk == True:
        controlsToMake.append('segmentControls')
        controlsToMake.append('hips')
        
    if ik == True:
        controlsToMake.append('vectorHandles')
        controlsToMake.append('spineIKHandle')  
        
    controlsDict = modules.limbControlMaker(moduleNull,controlsToMake)
    
    print controlsDict
    #>>> Organize em
    segmentControls = controlsDict.get('segmentControls')
    spineIKHandle = controlsDict.get('spineIKHandle')
    cog = controlsDict.get('cog')
    hips = controlsDict.get('hips')
    vectorHandles = controlsDict.get('vectorHandles')
    
    for handle in vectorHandles[-1:]:
        mc.delete(handle)
        vectorHandles.remove(handle)
    
    #>>> Parent em
    rigging.parentListToHeirarchy(segmentControls)
    mc.parent(spineIKHandle,segmentControls[-1])
    mc.parent(segmentControls[0],cog)
    mc.parent(hips,cog)
    
    for obj in segmentControls:
        rigging.zeroTransformMeObject(obj)
        mc.makeIdentity(obj,apply=True,translate =True)
        
    for obj in vectorHandles:
        mc.makeIdentity(obj,apply=True,translate =True)

    """ hips anchor locator """
    locBuffer = locators.locMeObject(hips)
    attributes.storeInfo(locBuffer,'cgmName',hips)
    attributes.storeInfo(locBuffer,'cgmTypeModifier','anchor')
    hipsAnchor = NameFactory.doNameObject(locBuffer)
    
    mc.setAttr((hipsAnchor+'.rotateOrder'),5)
    
    pointConstraintBuffer = mc.pointConstraint(hips,hipsAnchor, maintainOffset=False,weight =1)
    orientConstraintBuffer = mc.orientConstraint(hips,hipsAnchor, maintainOffset=False, skip =['x','y'],weight =1)
    
    """ hips anchor group constraint """
    groupBuffer =  rigging.groupMeObject(hipsAnchor)
    attributes.storeInfo(groupBuffer,'cgmName',hipsAnchor)
    attributes.storeInfo(groupBuffer,'cgmTypeModifier','orient')
    hipsAnchorOrGroup = NameFactory.doNameObject(groupBuffer)
    orientConstraintBuffer = mc.orientConstraint(segmentControls[0],hipsAnchorOrGroup, maintainOffset=False,weight =1)

    """ end anchor locator """
    locBuffer = locators.locMeObject(segmentControls[-1])
    attributes.storeInfo(locBuffer,'cgmName',segmentControls[-1])
    attributes.storeInfo(locBuffer,'cgmTypeModifier','anchor')
    endAnchor = NameFactory.doNameObject(locBuffer)
    
    mc.setAttr((endAnchor+'.rotateOrder'),5)
    
    mc.parent(endAnchor,spineIKHandle)

    #>>> set up follow chains
    constraintChain = []
    constraintChain.append(hipsAnchor)
    constraintChain = constraintChain + vectorHandles
    constraintChain.append(endAnchor)
    
    constraintChainReturn = constraints.doSegmentAimPointConstraint(constraintChain)
    print constraintChainReturn
    vectorHandlesZeroGroups = []
    for obj in vectorHandles:
        vectorHandlesZeroGroups.append(rigging.zeroTransformMeObject(obj))
        
    """ parent the last group to our IK handle """
    #mc.parent(vectorHandlesZeroGroups[-1],spineIKHandle)
    
    
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    #>>> Joint Chains
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>    
    """ surface chain """
    dupJointsBuffer = mc.duplicate(skinJoints[:-1],po=True,rc=True)
    surfaceJoints = []
    for joint in dupJointsBuffer:
        attributes.storeInfo(joint,'cgmType','surfaceJoint')
        surfaceJoints.append(NameFactory.doNameObject(joint))
    
    """ firm start """
    startJointsBuffer = mc.duplicate(skinJoints[0],po=True,rc=True)
    startJoints = []
    for joint in startJointsBuffer:
        attributes.storeInfo(joint,'cgmType','deformationJoint')
        startJoints.append(NameFactory.doNameObject(joint))
    
    """ firm end """
    endJointsBuffer = mc.duplicate(skinJoints[-2:],po=True,rc=True)
    endJoints = []
    for joint in endJointsBuffer:
        attributes.storeInfo(joint,'cgmType','deformationJoint')
        endJoints.append(NameFactory.doNameObject(joint))
    mc.parent(endJoints[0],world=True)

    #>>> Influence chain
    """
    get the root joints from our main chain searching by "cgmName" tags...maybe not the best way
    Maybe should change to search to closest joints
    """
    influenceJointsBuffer = []
    for obj in surfaceJoints:
        if (search.returnTagInfo(obj,'cgmName')) != False:
            influenceJointsBuffer.append(obj)
    
    """ make our influence joints """
    influenceJoints=[]
    for joint in influenceJointsBuffer:
        buffer = mc.duplicate(joint,po=True)
        closestObject = distance.returnClosestObject(buffer[0], surfaceJoints)
        attributes.storeInfo(buffer[0],'cgmName',closestObject)
        attributes.storeInfo(buffer[0],'cgmType','influenceJoint')
        rigging.doParentToWorld(buffer[0])
        influenceJoints.append(NameFactory.doNameObject(buffer[0]))
    
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    #>>> Put our deformation joints in the rig
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    ############### need better way of doing this for iterative
    mc.parent(endJoints[0],spineIKHandle)
    mc.parent(startJoints[0],hips)
    mc.parent(influenceJoints[0],hipsAnchor)
    mc.parent(influenceJoints[1],vectorHandles[0])
    mc.parent(influenceJoints[2],spineIKHandle)
    #mc.parent(influenceJoints[3],spineIKHandle)
    
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    #>>> Control Surface
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """ create """
    orientationBuffer = list(jointOrientation)
    outChannel = orientationBuffer[2]
    upChannel = (orientationBuffer[1]+'up')
    print upChannel
    
    surfaceBuffer = joints.loftSurfaceFromJointList(surfaceJoints,outChannel)
    controlSurface = surfaceBuffer[0]
    attributes.copyUserAttrs(moduleNull,controlSurface,attrsToCopy=['cgmName'])
    attributes.storeInfo(controlSurface,'cgmType','controlSurface',True)
    controlSurface = NameFactory.doNameObject(controlSurface)
    
    """ connect joints to surface"""
    surfaceConnectReturn = joints.attachJointChainToSurface(surfaceJoints,controlSurface,jointOrientation,upChannel,'animCrv')
    print surfaceConnectReturn
    """ surface influence joints skinning"""
    surfaceSkinCluster = mc.skinCluster (influenceJoints,controlSurface,tsb=True, n=(controlSurface+'_skinCluster'),maximumInfluences = 3, normalizeWeights = 1,dropoffRate=1)
    #surfaceSkinCluster = mc.skinCluster (influenceJoints,controlSurface,tsb=True, n=(controlSurface+'_skinCluster'),maximumInfluences = 3, normalizeWeights = 1, dropoffRate=1,smoothWeights=.5,obeyMaxInfluences=True, weight = 1)
    controlSurfaceSkinCluster = surfaceSkinCluster[0]
    
    """ smooth skin weights """
    skinning.simpleControlSurfaceSmoothWeights(controlSurface)




    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    #>>> Connect skin joints to surface joints
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    deformationJoints = []
    deformationJoints.append(startJoints[0])
    deformationJoints = deformationJoints + surfaceJoints[1:-2]
    deformationJoints = deformationJoints + endJoints
    for joint in skinJoints:
        attachJoint = distance.returnClosestObject(joint,deformationJoints)
        pntConstBuffer = mc.pointConstraint(attachJoint,joint,maintainOffset=False,weight=1)
        orConstBuffer = mc.orientConstraint(attachJoint,joint,maintainOffset=False,weight=1)
        #mc.connectAttr((attachJoint+'.t'),(joint+'.t'))
        #mc.connectAttr((attachJoint+'.r'),(joint+'.r'))
        mc.connectAttr((attachJoint+'.s'),(joint+'.s'))
        pntConstBuffer = mc.pointConstraint(attachJoint,joint,maintainOffset=False,weight=1)
        orConstBuffer = mc.orientConstraint(attachJoint,joint,maintainOffset=False,weight=1)
        #scaleConstBuffer = mc.scaleConstraint(attachJoint,joint,maintainOffset=False,weight=1)

    
def HOLDER(moduleNull):

    
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    #>>> Connect skin joints to surface joints
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    for joint in skinJoints:
        attachJoint = distance.returnClosestObject(joint,surfaceJoints)
        pntConstBuffer = mc.pointConstraint(attachJoint,joint,maintainOffset=True,weight=1)
        orConstBuffer = mc.orientConstraint(attachJoint,joint,maintainOffset=True,weight=1)
        #scaleConstBuffer = mc.scaleConstraint(attachJoint,joint,maintainOffset=True,weight=1)
    
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    #>>> Template Save and Removal
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """ get rid of the template """
    #modules.saveTemplateToModule(moduleNull)  
    
    #>>> creating our skin joint null and store the info
    #skinJointNullBuffer = modules.createInfoNull('skinJointNull')
    #mc.parent(skinJointNullBuffer,partNull)
    #skinJointNull = NameFactory.doNameObject(skinJointNullBuffer)
    #attributes.storeObjListNameToMessage(spineJoints,skinJointNull)
    #attributes.storeObjectToMessage(skinJointNull,partNull,'skinJointNull')
    
    #>>> Rig Maker
    #joints.loftSurfaceFromJointList (spineJoints,outDirection)




