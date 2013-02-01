import copy
import re

import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

# From Maya =============================================================
import maya.cmds as mc

# From Red9 =============================================================
from Red9.core import Red9_Meta as r9Meta
from Red9.core import Red9_General as r9General

# From cgm ==============================================================
from cgm.core import cgm_Meta as cgmMeta
from cgm.core import cgm_PuppetMeta as cgmPM
reload(cgmPM)
from cgm.lib.classes import NameFactory as nFactory
from cgm.lib import (curves,
                     deformers,
                     distance,
                     search,
                     lists,
                     modules,
                     constraints,
                     rigging,
                     attributes,
                     joints,
                     guiFactory)
reload(constraints)


#======================================================================
# Functions for a cgmMorpheusMakerNetwork
#======================================================================
def isCustomizable(self):
    """
    Checks if an asset is good to go or not
    """
    return True

#======================================================================
# Processing factory
#======================================================================
class go(object):
    @r9General.Timer
    def __init__(self,customizationNode = 'MorpheusCustomization'): 
        """
        To do:
        1) Gather info, make sure we have everything
        2) Mirror joints properly
        3) mirror controls 
        4) Shape parent controls to their joints
        5) Setup rig
        """
        # Get our base info
        #==================	        
        #>>> Customization network node
        log.info(">>> go.__init__")
        if mc.objExists(customizationNode):
            p = r9Meta.MetaClass(customizationNode)
        else:
            p = cgmPM.cgmMorpheusMakerNetwork(name = customizationNode)
        
        self.cls = "CustomizationFactory.go"
        self.p = p# Link for shortness
	
	log.info('All good')

	
@r9General.Timer
def doMirrorTemplate(self):
    """ 
    Segement orienter. Must have a JointFactory Instance
    """ 
    log.info(">>> doRigBody")
    # Get our base info
    #==================	        
    assert self.cls == 'CustomizationFactory.go',"Not a CustomizationFactory.go instance!"
    assert mc.objExists(self.p.mNode),"Customization node no longer exists"
    log.info(">>> go.doSkinIt")      
    p = self.p
    
    #Get skin joints
    #>>> Split out the left joints
    self.l_leftJoints = []
    self.l_leftRoots = []
    cntrCnt = 1
    for i_jnt in self.p.jointList:
	if i_jnt.hasAttr('cgmDirection') and i_jnt.cgmDirection == 'left':
	   self.l_leftJoints.append(i_jnt.mNode)
	   if i_jnt.parent:#if it has a panent
	       i_parent = cgmMeta.cgmObject(i_jnt.parent)
	       log.debug("'%s' child of '%s'"%(i_jnt.getShortName(),i_parent.getShortName()))
	       if not i_parent.hasAttr('cgmDirection'):
		   self.l_leftRoots.append(i_jnt.mNode)
	else:
	    #>>> tag our centre joints for mirroring later
	    i_jnt.addAttr('mirrorSide',attrType = 'enum', enumName = 'Centre:Left:Right', value = 0,keyable = False, hidden = True)
	    i_jnt.addAttr('mirrorIndex',attrType = 'int', value = cntrCnt,keyable = False, hidden = True)
	    #i_jnt.addAttr('mirrorAxis',value = 'translateX,translateY,translateZ')
	    cntrCnt+=1
	    
    self.l_leftJoints = lists.returnListNoDuplicates(self.l_leftJoints)
    self.l_leftRoots = lists.returnListNoDuplicates(self.l_leftRoots)
    p.leftJoints = self.l_leftJoints
    p.leftRoots = self.l_leftRoots
	       
    #>>> Customization network node
    log.info("ShaperJoints: %s"%self.p.getMessage('jointList',False))
    log.info("leftJoints: %s"%self.p.getMessage('leftJoints',False))
    log.info("leftRoots: %s"%self.p.getMessage('leftRoots',False))
	    
    #Mirror our joints, make mirror controls and store them appropriately
    #====================================================================
    self.l_leftJoints = self.p.getMessage('leftJoints',False)
    self.l_rightJoints = []
    self.l_rightRoots = []
    
    for r,i_root in enumerate(self.p.leftRoots):
	l_mirrored = mc.mirrorJoint(i_root.mNode,mirrorBehavior = True, mirrorYZ = True)
	mc.select(cl=True)
	mc.select(i_root.mNode,hi=True)
	l_base = mc.ls( sl=True )
	segmentBuffer = []
	d_constraintParentTargets = {}
	d_constraintAimTargets = {}
	d_constraintPointTargets = {}
	
	segName = i_root.getShortName()
	
	mayaMainProgressBar = guiFactory.doStartMayaProgressBar(len(l_mirrored))
	
	for i,jnt in enumerate(l_mirrored):
	    if mc.progressBar(mayaMainProgressBar, query=True, isCancelled=True ) :
		break
	    mc.progressBar(mayaMainProgressBar, edit=True, status = "On segment '%s':'%s'..."%(segName,jnt), step=1)
	    i_jnt = cgmMeta.cgmObject(jnt)
	    i_jnt.cgmDirection = 'right'
	    i_jnt.doName()
	    i_jnt.doStore('cgmMirrorMatch',l_base[i])
	    
	    attributes.storeInfo(l_base[i],'cgmMirrorMatch',i_jnt.mNode)
	    
	    #>>> Make curve
	    index = self.l_leftJoints.index(l_base[i]) #Find our main index
	    i_mirror = self.p.leftJoints[index] #store that mirror instance so we're not calling it every line
	    
	    buffer = mc.duplicate(i_mirror.controlCurve.mNode) #Duplicate curve
	    i_crv = cgmMeta.cgmObject( buffer[0] )
	    i_crv.cgmDirection = 'right'#Change direction
	    i_jnt.doStore('controlCurve',i_crv.mNode)#Store new curve to new joint
	    i_crv.doStore('cgmSource',i_jnt.mNode)
	    i_crv.doName()#name it
	    
	    #>>> Mirror the curve
	    s_prntBuffer = i_crv.parent#Shouldn't be necessary later
	    grp = mc.group(em=True)#Group world center
	    i_crv.parent = grp
	    attributes.doSetAttr(grp,'sx',-1)#Set an attr
	    i_crv.parent = s_prntBuffer
	    mc.delete(grp)
	    
	    #color it
	    l_colorRight = modules.returnSettingsData('colorRight',True)
	    if i_crv.hasAttr('cgmTypeModifier') and i_crv.cgmTypeModifier == 'secondary':
		colorIndex = 1
	    else:
		colorIndex = 0
	    curves.setCurveColorByName(i_crv.mNode,l_colorRight[colorIndex])#Color it, need to get secodary indexes
	    self.l_rightJoints.append(i_jnt.mNode)
	    segmentBuffer.append(i_jnt.mNode)#store to our segment buffer
	    
	    #>>> Tag for mirroring
	    i_jnt.addAttr('mirrorSide',attrType = 'enum', enumName = 'Centre:Left:Right', value = 2,keyable = False, hidden = True)
	    i_jnt.addAttr('mirrorIndex',attrType = 'int', value = i+1,keyable = False, hidden = True)
	    i_jnt.addAttr('mirrorAxis',value = 'translateX,translateY,translateZ')
	    
	    i_mirror.addAttr('mirrorSide',attrType = 'enum', enumName = 'Centre:Left:Right', value = 1,keyable = False, hidden = True)
	    i_mirror.addAttr('mirrorIndex',attrType = 'int', value = i+1,keyable = False, hidden = True)
	    i_mirror.addAttr('mirrorAxis',value = 'translateX,translateY,translateZ')
	    
	    #>>> See if we need to grab contraintTargets attr
	    if i_mirror.hasAttr('constraintParentTargets') and i_mirror.constraintParentTargets:
		log.info("constraintParentTargets detected, searching to transfer!")
		targets = []
		for t in i_mirror.constraintParentTargets:
		    d_search = nFactory.returnObjectGeneratedNameDict(t.mNode)
		    d_search['cgmDirection'] = 'right'
		    testName = nFactory.returnCombinedNameFromDict(d_search)
		    targets.append(testName)
		d_constraintParentTargets[i] = targets
		
	    if i_mirror.hasAttr('constraintAimTargets') and i_mirror.constraintAimTargets:
		log.info("constraintAimTargets detected, searching to transfer!")
		targets = []
		for t in i_mirror.constraintAimTargets:
		    d_search = nFactory.returnObjectGeneratedNameDict(t.mNode)
		    d_search['cgmDirection'] = 'right'
		    testName = nFactory.returnCombinedNameFromDict(d_search)
		    targets.append(testName)
		d_constraintAimTargets[i] = targets	
		
	    if i_mirror.hasAttr('constraintPointTargets') and i_mirror.constraintAimTargets:
		log.info("constraintPointTargets detected, searching to transfer!")
		targets = []
		for t in i_mirror.constraintPointTargets:
		    d_search = nFactory.returnObjectGeneratedNameDict(t.mNode)
		    d_search['cgmDirection'] = 'right'
		    testName = nFactory.returnCombinedNameFromDict(d_search)
		    targets.append(testName)
		d_constraintPointTargets[i] = targets	
		
	#Connect constraintParent/Point/AimTargets when everything is done
	if d_constraintParentTargets:
	    for k in d_constraintParentTargets.keys():
		i_k = r9Meta.MetaClass(segmentBuffer[k])
		i_k.addAttr('constraintParentTargets',attrType='message',value = d_constraintParentTargets[k])
	if d_constraintAimTargets:
	    for k in d_constraintAimTargets.keys():
		i_k = r9Meta.MetaClass(segmentBuffer[k])
		i_k.addAttr('constraintAimTargets',attrType='message',value = d_constraintAimTargets[k])
	if d_constraintPointTargets:
	    for k in d_constraintPointTargets.keys():
		i_k = r9Meta.MetaClass(segmentBuffer[k])
		i_k.addAttr('constraintPointTargets',attrType='message',value = d_constraintPointTargets[k])
		 
	self.l_rightRoots.append(segmentBuffer[0])#Store the root
	guiFactory.doEndMayaProgressBar(mayaMainProgressBar)#Close out this progress bar
	
    p.rightRoots = self.l_rightRoots#store the roots to our network	
	    
    #p.addAttr('rightJoints',attrType = 'message',value = self.l_rightJoints,lock=True)
    p.rightJoints = self.l_rightJoints
	
    #Rig it
    #==================     
    #doRigBody(self)
    #doSkinBody(self)

@r9General.Timer
def doBody_bsNode(self):
    """ 
    Sets up body blendshape node
    """ 
    # Get our base info
    #==================	        
    assert self.cls == 'CustomizationFactory.go',"Not a CustomizationFactory.go instance!"
    assert mc.objExists(self.p.mNode),"Customization node no longer exists"
    log.info(">>> go.doBody_bsNode")      
    p = self.p
    
    #Gather geo
    targetGeoGroup = p.masterNull.getMessage('bodyTargetsGroup')[0]
    if not targetGeoGroup:
	log.warning("No base body target group found")
	return False
    bsTargetObjects = search.returnAllChildrenObjects(targetGeoGroup,True)
    if not bsTargetObjects:
	log.error("No geo found")
	return False
    
    baseGeo = p.getMessage('baseBodyGeo')[0]
    bsNode = deformers.buildBlendShapeNode(baseGeo,bsTargetObjects,'tmp')
    
    i_bsNode = cgmMeta.cgmNode(bsNode)
    i_bsNode.addAttr('cgmName','body',attrType='string',lock=True)    
    i_bsNode.addAttr('mClass','cgmNode',attrType='string',lock=True)
    i_bsNode.addAttr('targetsGroup',targetGeoGroup,attrType='messageSimple',lock=True)
    
    i_bsNode.doName()
    p.bodyBlendshapeNodes = i_bsNode.mNode

@r9General.Timer
def doFace_bsNode(self):
    """ 
    Sets up face blendshape node
    """ 
    # Get our base info
    #==================	        
    assert self.cls == 'CustomizationFactory.go',"Not a CustomizationFactory.go instance!"
    assert mc.objExists(self.p.mNode),"Customization node no longer exists"
    log.info(">>> go.doFace_bsNode")      
    p = self.p
    
    #Gather geo
    targetGeoGroup = p.masterNull.getMessage('faceTargetsGroup')[0]
    if not targetGeoGroup:
	log.warning("No base face target group found")
	return False
    bsTargetObjects = search.returnAllChildrenObjects(targetGeoGroup,True)
    if not bsTargetObjects:
	log.error("No geo found")
	return False
    
    baseGeo = p.getMessage('baseBodyGeo')[0]
    bsNode = deformers.buildBlendShapeNode(baseGeo,bsTargetObjects,'tmp')
    
    i_bsNode = cgmMeta.cgmNode(bsNode)
    i_bsNode.addAttr('cgmName','face',attrType='string',lock=True)    
    i_bsNode.addAttr('mClass','cgmNode',attrType='string',lock=True)
    i_bsNode.addAttr('targetsGroup',targetGeoGroup,attrType='messageSimple',lock=True)
    
    i_bsNode.doName()
    p.faceBlendshapeNodes = i_bsNode.mNode
    
@r9General.Timer
def doSkinBody(self):
    """ 
    Segement orienter. Must have a JointFactory Instance
    """ 
    log.info(">>> doRigBody")
    # Get our base info
    #==================	        
    assert self.cls == 'CustomizationFactory.go',"Not a CustomizationFactory.go instance!"
    assert mc.objExists(self.p.mNode),"Customization node no longer exists"
    log.info(">>> go.doSkinIt")      
    p = self.p
    #Get skin joints
    
    if not self.l_skinJoints:
	return False	
	#if not returnSkinJoints(self):
	    #log.error("No skinJoints found")
    l_skinJoints = []
    for i_jnt in self.l_skinJoints:
	l_skinJoints.append(i_jnt.mNode)
    #Gather geo and skin
    baseGeo = p.masterNull.getMessage('baseGeoGroup')[0]
    if not baseGeo:
	log.warning("No base geo group found")
	return False
    geoGroupObjects = search.returnAllChildrenObjects(baseGeo,True)
    if not geoGroupObjects:
	log.error("No geo found")
	return False	
    toSkin = []
    for o in geoGroupObjects:
	if search.returnObjectType(o) in ['mesh','nurbsSurface']:
	    toSkin.append(o) 
    if toSkin:
	for geo in toSkin:
	    toBind = l_skinJoints + [geo]
	cluster = mc.skinCluster(toBind, tsb = True, normalizeWeights = True, mi = 4, dr = 5)
	i_cluster = cgmMeta.cgmNode(cluster[0])
	i_cluster.doCopyNameTagsFromObject(p.mNode,ignore=['cgmType'])
	i_cluster.addAttr('mClass','cgmNode',attrType='string',lock=True)
	i_cluster.doName()
	p.skinCluster = i_cluster.mNode
	self.bodyGeo = toSkin[0]
    else:
	log.info("Nothing found to skin")
	
@r9General.Timer
def returnSkinJoints(self):
    assert self.cls == 'CustomizationFactory.go',"Not a CustomizationFactory.go instance!"
    assert mc.objExists(self.p.mNode),"Customization node no longer exists"
    log.info(">>> go.returnSkinJoints")  
    l_skinJoints  = ['pelvis_body_shaper']
    l_skinJoints.extend( search.returnChildrenJoints(l_skinJoints[0]) )
    log.info (l_skinJoints)
    self.l_skinJoints = l_skinJoints
    return l_skinJoints  
	    
@r9General.Timer
def doRigBody(self):
    """ 
    Segement orienter. Must have a JointFactory Instance
    """ 
    log.info(">>> doRigBody")
    # Get our base info
    #==================	        
    assert self.cls == 'CustomizationFactory.go',"Not a CustomizationFactory.go instance!"
    assert mc.objExists(self.p.mNode),"Customization node no longer exists"
    
    mayaMainProgressBar = guiFactory.doStartMayaProgressBar(len(self.p.jointList))
    self.l_skinJoints = []
    l_constraintParentTargetJoints = []
    l_constraintAimTargetJoints = []    
    l_constraintPointTargetJoints = [] 
    l_iControlsLeft = []
    l_iControlsRight = []
    l_iControlsCentre = []
    
    mc.select(cl=True)
    i_controlSet = cgmMeta.cgmObjectSet(setName = 'customControls',setType = 'tdSet',qssState=True)#Build us a simple quick select set
    i_controlSetLeft = cgmMeta.cgmObjectSet(setName = 'customControlsLeft',setType = 'tdSet',qssState=True)#Build us a simple quick select set
    i_controlSetRight = cgmMeta.cgmObjectSet(setName = 'customControlsRight',setType = 'tdSet',qssState=True)#Build us a simple quick select set
    
    for i,i_jnt in enumerate(self.p.jointList):#+ self.p.rightJoints
	if mc.progressBar(mayaMainProgressBar, query=True, isCancelled=True ) :
	    break
	mc.progressBar(mayaMainProgressBar, edit=True, status = "On: '%s'"%i_jnt.getShortName(), step=1)
	
        if i_jnt.cgmName == 'ankle':
	    buffer = updateTransform(i_jnt.controlCurve,i_jnt)	  
	    i_jnt.controlCurve = buffer
	    i_crv = i_jnt.controlCurve
	    i_crv.parent = False
	    mc.makeIdentity(i_crv.mNode, apply = True, t=True, r = True, s = True)
	    vBuffer = mc.xform(i_crv.mNode,q=True,sp=True,ws=True)	    
	    i_crv.scalePivotY = 0	    	    	    	    
	    i_crv.doName()
	    i_jnt.doGroup(True)
	    i_jnt.parent = i_crv.mNode
	    #mc.parentConstraint(i_crv.mNode,i_jnt.parent, maintainOffset=True)
	    #mc.scaleConstraint(i_crv.mNode,i_jnt.parent, maintainOffset=True)	    
	    i_controlSet.addObj(i_crv.mNode)#Add to our selection set
	    
	    if i_crv.cgmDirection == 'left':
		i_controlSetLeft.addObj(i_crv.mNode)
	    else:
		i_controlSetRight.addObj(i_crv.mNode)		
	    
	else:
	    i_crv = i_jnt.controlCurve
	    if i_crv:
		i_jnt.addAttr('cgmType','bodyShaper',attrType = 'string')
		curves.parentShapeInPlace(i_jnt.mNode,i_crv.mNode)
		i_jnt.doName()
		i_jnt.doGroup(True)	
		
		if i_jnt.cgmName in ['hip','neck','head','shoulders','shoulder']:
		    pBuffer = i_jnt.parent
		    i_prnt = cgmMeta.cgmObject(pBuffer)
		    parentPBuffer = i_prnt.parent
		    i_prnt.parent = False
		    if i_jnt.cgmName == 'shoulders':
			mc.pointConstraint(parentPBuffer,i_prnt.mNode, maintainOffset=True)					    	    
		    else:
			mc.parentConstraint(parentPBuffer,i_prnt.mNode, maintainOffset=True)
		    
		if i_jnt.hasAttr('constraintAimTargets'):
		    l_constraintAimTargetJoints.append(i_jnt)		    
		if i_jnt.hasAttr('constraintParentTargets'):
		    l_constraintParentTargetJoints.append(i_jnt)
		if i_jnt.hasAttr('constraintPointTargets'):
		    l_constraintPointTargetJoints.append(i_jnt)
	    i_controlSet.addObj(i_jnt.mNode)
	    
	    if i_jnt.hasAttr('cgmDirection'):
		if i_jnt.cgmDirection == 'left':
		    i_controlSetLeft.addObj(i_jnt.mNode)
		elif i_jnt.cgmDirection == 'right':
		    i_controlSetRight.addObj(i_jnt.mNode)		    
			    
	self.l_skinJoints.append(i_jnt)
    
    if l_constraintParentTargetJoints:
	log.info("Found contraintParentTargetJoints: %i"%len(l_constraintParentTargetJoints))
	for i_jnt in l_constraintParentTargetJoints:
	    pBuffer = i_jnt.parent
	    i_prnt = cgmMeta.cgmObject(pBuffer)
	    parentPBuffer = i_prnt.parent
	    i_prnt.parent = False
	    log.info(i_jnt.getMessage('constraintParentTargets',False))
	    log.info(i_prnt.mNode)
	    if i_jnt not in l_constraintAimTargetJoints:
		constraints.doParentConstraintObjectGroup(i_jnt.getMessage('constraintParentTargets',False),i_prnt.getShortName(),1)
		mc.scaleConstraint(i_jnt.getMessage('constraintParentTargets',False),i_prnt.getShortName(), maintainOffset=True)	    
	    else:
		constraints.doPointConstraintObjectGroup(i_jnt.getMessage('constraintParentTargets',False),i_prnt.getShortName(),0)
    
    if l_constraintPointTargetJoints:
	log.info("Found constraintPointTargets: %i"%len(l_constraintPointTargetJoints))
	for i_jnt in l_constraintPointTargetJoints:
	    pBuffer = i_jnt.parent
	    i_prnt = cgmMeta.cgmObject(pBuffer)
	    i_prnt.addAttr('cgmTypeModifier','point','string')	    
	    parentPBuffer = i_prnt.parent
	    i_prnt.parent = False
	    i_prnt.doName()	    
	    log.info(i_jnt.getMessage('constraintPointTargets',False))
	    log.info(i_prnt.mNode)
	    
	    constraints.doPointConstraintObjectGroup(i_jnt.getMessage('constraintPointTargets',False),i_prnt.getShortName(),0)

    if l_constraintAimTargetJoints:
	log.info("Found contraintAimTargetJoints: %i"%len(l_constraintAimTargetJoints))
	for i_jnt in l_constraintAimTargetJoints:
	    if i_jnt.cgmName == 'ankleMeat':
		if i_jnt.cgmDirection == 'left':
		    constBuffer = mc.aimConstraint(i_jnt.getMessage('constraintAimTargets',False),i_jnt.mNode,maintainOffset = True, weight = 1, aimVector = [0,1,0], upVector = [0,0,1], worldUpVector = [0,0,-1], worldUpType = 'vector' )    		
		elif i_jnt.cgmDirection == 'right':
		    constBuffer = mc.aimConstraint(i_jnt.getMessage('constraintAimTargets',False),i_jnt.mNode,maintainOffset = True, weight = 1, aimVector = [0,-1,0], upVector = [0,0,-1], worldUpVector = [0,0,-1], worldUpType = 'vector' )    			    
	    else:
		if i_jnt.cgmDirection == 'left':
		    constBuffer = mc.aimConstraint(i_jnt.getMessage('constraintAimTargets',False),i_jnt.mNode,maintainOffset = True, weight = 1, aimVector = [0,0,1], upVector = [0,1,0], worldUpVector = [0,0,1], worldUpType = 'vector' )    
		elif i_jnt.cgmDirection == 'right':
		    constBuffer = mc.aimConstraint(i_jnt.getMessage('constraintAimTargets',False),i_jnt.mNode,maintainOffset = True, weight = 1, aimVector = [0,0,-1], upVector = [0,-1,0], worldUpVector = [0,0,1], worldUpType = 'vector' )    
	    
	    attributes.doSetLockHideKeyableAttr(i_jnt.mNode,channels = ['rx','ry','rz'])
		    
	     
    guiFactory.doEndMayaProgressBar(mayaMainProgressBar)
    self.p.controlsLeft = i_controlSetLeft.value
    self.p.controlsRight = i_controlSetRight.value
		
            
    #mc.delete('controlCurves')

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Utilities
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
def autoTagControls(customizationNode = 'MorpheusCustomization',l_controls=None): 
    """
    For each joint:
    1) tag it mClass as cgmObject
    2) Find the closest curve
    3) Tag that curve as a cgmObject mClass
    """
    # Get our base info
    #==============	        
    #>>> module null data 
    assert mc.objExists(customizationNode),"'%s' doesn't exist"%customizationNode
    log.info(">>> autoTagControls")
    log.info("l_joints: %s"%customizationNode)
    log.info("l_controls: %s"%l_controls)
    p = r9Meta.MetaClass(customizationNode)
    buffer = p.getMessage('jointList')
    for o in buffer:
	i_o = cgmMeta.cgmObject(o)
	i_o.addAttr('mClass','cgmObject',attrType = 'string', lock = True)    
    if l_controls is None:#If we don't have any controls passed
	l_iControls = []
	if mc.objExists('controlCurves'):#Check the standard group
	    l_controls = search.returnAllChildrenObjects('controlCurves')
	for c in l_controls:
	    i_c = cgmMeta.cgmObject(c)
	    i_c.addAttr('mClass','cgmObject',attrType = 'string', lock = True)
	    l_iControls.append(i_c.mNode)
	#p.addAttr('controlCurves',attrType = 'message', value = l_iControls)
	p.controlCurves = l_iControls
    for i_o in p.jointList:
	closestObject = distance.returnClosestObject(i_o.mNode,p.getMessage('controlCurves'))
	if closestObject:
	    log.info("'%s' <<tagging>> '%s'"%(i_o.getShortName(),closestObject))            
	    i_closestObject = cgmMeta.cgmObject(closestObject)
	    i_closestObject.addAttr('mClass','cgmObject',attrType = 'string', lock = True)
	    i_o.addAttr('controlCurve',value = i_closestObject.mNode,attrType = 'messageSimple', lock = True)
	    i_closestObject.addAttr('cgmSource',value = i_o.mNode,attrType = 'messageSimple', lock = True)
	    i_closestObject.doCopyNameTagsFromObject(i_o.mNode,['cgmType','cgmTypeModifier'])
	    
	    i_o.addAttr('cgmType','shaper',attrType='string',lock = True)            
	    i_closestObject.addAttr('cgmType','bodyShaper',attrType='string',lock = True)
	    
	    i_o.doName()
	    i_closestObject.doName()
	    
def doTagCurveFromJoint(curve = None, joint = None): 
    """
    """
    # Get our base info
    #==============	        
    #>>> module null data 
    if curve is None:
	curve = mc.ls(sl=True)[1] or False
    if joint is None:
	joint = mc.ls(sl=True)[0] or False
	
    assert mc.objExists(curve),"'%s' doesn't exist"%curve
    assert mc.objExists(joint),"'%s' doesn't exist"%joint
    
    log.info(">>> doTagCurveFromJoint")
    log.info("curve: %s"%curve)
    log.info("joint: %s"%joint)
    i_o = cgmMeta.cgmObject(joint)
    i_o.addAttr('mClass','cgmObject',attrType = 'string', lock = True)
    
    i_crv = cgmMeta.cgmObject(curve)
    i_crv.addAttr('mClass','cgmObject',attrType = 'string', lock = True)
    i_o.addAttr('controlCurve',value = i_crv.mNode,attrType = 'messageSimple', lock = True)
    i_crv.addAttr('cgmSource',value = i_o.mNode,attrType = 'messageSimple', lock = True)
    i_crv.doCopyNameTagsFromObject(i_o.mNode,['cgmType','cgmTypeModifier'])
    
    #i_o.addAttr('cgmTypeModifier','shaper',attrType='string',lock = True)            
    i_crv.addAttr('cgmType','shaper',attrType='string',lock = True)
    
    i_o.doName()
    i_crv.doName()
    return True
    
def doTagParentContrainToTargets(obj = None, targets = None): 
    """
    """
    # Get our base info
    #==============	        
    #>>> module null data 
    if obj is None:
	obj = mc.ls(sl=True)[-1] or False
    if targets is None:
	targets = mc.ls(sl=True)[:-1] or False
	
    assert mc.objExists(obj),"'%s' doesn't exist"%obj
    assert targets,"No targets found"
    for t in targets:
	assert mc.objExists(t),"'%s' doesn't exist"%t
    
    log.info(">>> doTagContrainToTargets")
    log.info("obj: %s"%obj)
    log.info("targets: %s"%targets)
    i_o = cgmMeta.cgmObject(obj)
    i_o.addAttr('mClass','cgmObject',attrType = 'string', lock = True)
    
    i_o.addAttr('constraintParentTargets',attrType='message',value = targets)
    return True

def doTagAimContrainToTargets(obj = None, targets = None): 
    """
    """
    # Get our base info
    #==============	        
    #>>> module null data 
    if obj is None:
	obj = mc.ls(sl=True)[-1] or False
    if targets is None:
	targets = mc.ls(sl=True)[:-1] or False
	
    assert mc.objExists(obj),"'%s' doesn't exist"%obj
    assert targets,"No targets found"
    for t in targets:
	assert mc.objExists(t),"'%s' doesn't exist"%t
    
    log.info(">>> doTagContrainToTargets")
    log.info("obj: %s"%obj)
    log.info("targets: %s"%targets)
    i_o = cgmMeta.cgmObject(obj)
    i_o.addAttr('mClass','cgmObject',attrType = 'string', lock = True)
    
    i_o.addAttr('constraintAimTargets',attrType='message',value = targets)
    return True

def doTagPointContrainToTargets(obj = None, targets = None): 
    """
    """
    # Get our base info
    #==============	        
    #>>> module null data 
    if obj is None:
	obj = mc.ls(sl=True)[-1] or False
    if targets is None:
	targets = mc.ls(sl=True)[:-1] or False
	
    assert mc.objExists(obj),"'%s' doesn't exist"%obj
    assert targets,"No targets found"
    for t in targets:
	assert mc.objExists(t),"'%s' doesn't exist"%t
    
    log.info(">>> doTagContrainToTargets")
    log.info("obj: %s"%obj)
    log.info("targets: %s"%targets)
    i_o = cgmMeta.cgmObject(obj)
    i_o.addAttr('mClass','cgmObject',attrType = 'string', lock = True)
    
    i_o.addAttr('constraintPointTargets',attrType='message',value = targets)
    return True
    
@r9General.Timer
def updateTransform(i_curve,i_sourceObject):
    log.info(">>> updateTransform: '%s'"%i_curve.getShortName())    
    childrenToWorld = []	
    children = mc.listRelatives(i_curve.mNode,children=True,type = 'transform')
    if children:
	for c in children:
	    childrenToWorld.append(rigging.doParentToWorld(c))
    transform = rigging.groupMeObject(i_sourceObject.mNode,False,False)
    i_transform = cgmMeta.cgmObject(transform)
    for attr in i_curve.getUserAttrs():
	attributes.doCopyAttr(i_curve.mNode,attr,transform)
    for attr in i_sourceObject.getUserAttrs():
	attributes.doCopyAttr(i_sourceObject.mNode,attr,transform)
    buffer = curves.parentShapeInPlace(transform,i_curve.mNode)
    mc.delete(i_curve.mNode)
    if childrenToWorld:
	for c in childrenToWorld:
	    rigging.doParentReturnName(c,transform)
    return i_transform.mNode