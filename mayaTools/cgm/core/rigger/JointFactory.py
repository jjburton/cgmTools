# From Python =============================================================
import copy
import re

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

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
from cgm.lib import (cgmMath,
                     joints,
                     rigging,
                     attributes,
                     locators,
                     distance,
                     autoname,
                     search,
                     curves,
                     dictionary,
                     lists,
                     settings,
                     modules)
reload(joints)
reload(cgmMath)
from cgm.core.lib import nameTools

#>>> Register rig functions
#=====================================================================
from cgm.core.rigger.lib.Limb import (spine)
d_moduleTypeToBuildModule = {'torso':spine,
                            } 
for module in d_moduleTypeToBuildModule.keys():
    reload(d_moduleTypeToBuildModule[module])

typesDictionary = dictionary.initializeDictionary(settings.getTypesDictionaryFile())
namesDictionary = dictionary.initializeDictionary( settings.getNamesDictionaryFile())
settingsDictionary = dictionary.initializeDictionary( settings.getSettingsDictionaryFile())
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Modules
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
class go(object):
    @r9General.Timer
    def __init__(self,moduleInstance,forceNew = True,saveTemplatePose = True,**kws): 
        """
        To do:
        Add rotation order settting
        Add module parent check to make sure parent is templated to be able to move forward, or to constrain
        Add any other piece meal data necessary
        Add a cleaner to force a rebuild
        """
        # Get our base info
        #==============	        
        #>>> module null data 
        assert moduleInstance.mClass in ['cgmModule','cgmLimb'],"Not a module"
        assert moduleInstance.isTemplated(),"Module is not templated"
        #assert object is templated
        #assert ...
        log.debug(">>> JointFactory.go.__init__")
        self.cls = "JointFactory.go"
	self._cgmClass = "JointFactory.go"
        self._i_module = moduleInstance# Link for shortness
        
        if moduleInstance.isSkeletonized():
            if forceNew:
                deleteSkeleton(moduleInstance)
            else:
                log.warning("'%s' has already been skeletonized"%moduleInstance.getShortName())
                return        
        
        #>>> store template settings
        if saveTemplatePose:
            log.debug("Saving template pose in JointFactory.go")
            self._i_module.storeTemplatePose()
        
        self.rigNull = self._i_module.getMessage('rigNull')[0] or False
        self.i_rigNull = self._i_module.rigNull
        self.moduleColors = self._i_module.getModuleColors()
        self.l_coreNames = self._i_module.i_coreNames.value
        self.foundDirections = False #Placeholder to see if we have it
                
        #>>> part name 
        self._partName = self._i_module.getPartNameBase()
        self._partType = self._i_module.moduleType.lower() or False
        self._strShortName = self._i_module.getShortName() or False
	
        self.direction = None
        if self._i_module.hasAttr('cgmDirection'):
            self.direction = self._i_module.cgmDirection or None
        
        #>>> template null 
        self.i_templateNull = self._i_module.templateNull
        self.curveDegree = self.i_templateNull.curveDegree
	
        #>>> Gather info
        #=========================================================	
        self._l_coreNames = self._i_module.coreNames.value        
        #>>> Instances and joint stuff
        self.jointOrientation = modules.returnSettingsData('jointOrientation')
        self.i_root = self.i_templateNull.root
        self.i_orientRootHelper = self.i_templateNull.orientRootHelper
        self.i_curve = self.i_templateNull.curve
        self.i_controlObjects = self.i_templateNull.controlObjects
        
        log.debug("Module: %s"%self._i_module.getShortName())
        log.debug("partType: %s"%self._partType)
        log.debug("direction: %s"%self.direction) 
        log.debug("colors: %s"%self.moduleColors)
        log.debug("coreNames: %s"%self.l_coreNames)
        log.debug("root: %s"%self.i_root.getShortName())
        log.debug("curve: %s"%self.i_curve.getShortName())
        log.debug("orientRootHelper: %s"%self.i_orientRootHelper.getShortName())
        log.debug("rollJoints: %s"%self.i_templateNull.rollJoints)
        log.debug("jointOrientation: %s"%self.jointOrientation)
        log.info("hasJointSetup: %s"%hasJointSetup(self))
	
        if self._i_module.mClass == 'cgmLimb':
            log.debug("mode: cgmLimb Skeletonize")
            doSkeletonize(self)
	    self.build(self)    
        else:
            raise NotImplementedError,"haven't implemented '%s' templatizing yet"%self._i_module.mClass

def hasJointSetup(goInstance):
    if not issubclass(type(goInstance),go):
	log.error("Not a JointFactory.go instance: '%s'"%goInstance)
	raise StandardError
    self = goInstance#Link
    
    if self._partType not in d_moduleTypeToBuildModule.keys():
	log.info("%s.isBuildable>>> Not in d_moduleTypeToBuildModule"%(self._strShortName))	
	return False
    
    try:#Version
	self._buildVersion = d_moduleTypeToBuildModule[self._partType].__version__    
    except:
	log.error("%s.isBuildable>>> Missing version"%(self._strShortName))	
	return False
    
    try:#Joints list
	self.build = d_moduleTypeToBuildModule[self._partType].__bindSkeletonSetup__
	self.buildModule = d_moduleTypeToBuildModule[self._partType]
    except:
	log.error("%s.isBuildable>>> Missing Joint Setup Function"%(self._strShortName))	
	return False	
    
    return True    
	
#@r9General.Timer
def doSkeletonize(self):
    """ 
    DESCRIPTION:
    Basic limb skeletonizer
    
    ARGUMENTS:
    stiffIndex(int) - the index of the template objects you want to not have roll joints
                      For example, a value of -1 will let the chest portion of a spine 
                      segment be solid instead of having a roll segment. Default is the modules setting
    RETURNS:
    l_limbJoints(list)
    """
    log.debug(">>> doSkeletonize")
    # Get our base info
    #==================	        
    assert self.cls == 'JointFactory.go',"Not a JointFactory.go instance!"
    assert mc.objExists(self._i_module.mNode),"module no longer exists"
    curve = self.i_curve.mNode
    partName = self._partName
    l_limbJoints = []
    
    #>>> Check roll joint args
    rollJoints = self.i_templateNull.rollJoints
    d_rollJointOverride = self.i_templateNull.rollOverride
    if type(d_rollJointOverride) is not dict:
        d_rollJointOverride = False
    
    #>>> See if we have have a suitable parent joint to use
    # We'll know it is if the first template position shares an equivalent position with it's parentModule
    #======================================================
    i_parentJointToUse = False
    
    pos = distance.returnWorldSpacePosition( self.i_templateNull.getMessage('controlObjects')[0] )
    log.debug("pos: %s"%pos)
    #Get parent position, if we have one
    if self._i_module.getMessage('moduleParent'):
        log.debug("Found moduleParent, checking joints...")
        i_parentRigNull = self._i_module.moduleParent.rigNull
        parentJoints = i_parentRigNull.getMessage('skinJoints',False)
        log.debug(parentJoints)
        if parentJoints:
            parent_pos = distance.returnWorldSpacePosition( parentJoints[-1] )
            log.debug("parentPos: %s"%parent_pos)  
            
        log.debug("Equivalent: %s"%cgmMath.isVectorEquivalent(pos,parent_pos))
        if cgmMath.isVectorEquivalent(pos,parent_pos):#if they're equivalent
            i_parentJointToUse = cgmMeta.cgmObject(parentJoints[-1])
            
    #>>> Make if our segment only has one handle
    #==========================================	
    self.b_parentStole = False
    if len(self.i_controlObjects) == 1:
        if i_parentJointToUse:
            log.debug("Single joint: moduleParent mode")
            #Need to grab the last joint for this module
            l_limbJoints = [parentJoints[-1]]
            i_parentRigNull.connectChildrenNodes(parentJoints[:-1],'skinJoints','module')
	    self.b_parentStole = True	    
        else:
            log.debug("Single joint: no parent mode")
            l_limbJoints.append ( mc.joint (p=(pos[0],pos[1],pos[2]))) 
    else:
        if i_parentJointToUse:
            #We're going to reconnect all but the last joint back to the parent module and delete the last parent joint which we're replacing
            i_parentRigNull.connectChildrenNodes(parentJoints[:-1],'skinJoints','module')
            mc.delete(i_parentJointToUse.mNode)
	    self.b_parentStole = True
            
        #>>> Make the limb segment
        #==========================	 
        l_spanUPositions = []
        #>>> Divide stuff
        for i_obj in self.i_controlObjects:#These are our base span u positions on the curve
            l_spanUPositions.append(distance.returnNearestPointOnCurveInfo(i_obj.mNode,curve)['parameter'])
        l_spanSegmentUPositions = lists.parseListToPairs(l_spanUPositions)
        #>>>Get div per span
        l_spanDivs = []
        for segment in l_spanSegmentUPositions:
            l_spanDivs.append(rollJoints)
            
        if d_rollJointOverride:
            for k in d_rollJointOverride.keys():
                try:
                    l_spanDivs[int(k)]#If the arg passes
                    l_spanDivs[int(k)] = d_rollJointOverride.get(k)#Override the roll value
                except:log.warning("%s:%s rollOverride arg failed"%(k,d_rollJointOverride.get(k)))
        
        log.debug("l_spanSegmentUPositions: %s"%l_spanSegmentUPositions)
        log.debug("l_spanDivs: %s"%l_spanDivs)
        
        #>>>Get div per span 
        l_jointUPositions = []
        for i,segment in enumerate(l_spanSegmentUPositions):#Split stuff up
            #Get our span u value distance
            length = segment[1]-segment[0]
            div = length / (l_spanDivs[i] +1)
            tally = segment[0]
            l_jointUPositions.append(tally)
            for i in range(l_spanDivs[i] +1)[1:]:
                tally = segment[0]+(i*div)
                l_jointUPositions.append(tally)
        l_jointUPositions.append(l_spanUPositions[-1])
                
        l_jointPositions = []
        for u in l_jointUPositions:
            l_jointPositions.append(mc.pointPosition("%s.u[%f]"%(curve,u)))
            
        #>>> Remove the duplicate positions"""
        l_jointPositions = lists.returnPosListNoDuplicates(l_jointPositions)
        #>>> Actually making the joints
        for pos in l_jointPositions:
            l_limbJoints.append ( mc.joint (p=(pos[0],pos[1],pos[2]))) 
               
    #>>> Naming
    #=========== 
    """ 
    Copy naming information from template objects to the joints closest to them
    copy over a cgmNameModifier tag from the module first
    """
    #attributes.copyUserAttrs(moduleNull,l_limbJoints[0],attrsToCopy=['cgmNameModifier'])
    
    #>>>First we need to find our matches
    log.debug("Finding matches from module controlObjects")
    for i_obj in self.i_controlObjects:
        closestJoint = distance.returnClosestObject(i_obj.mNode,l_limbJoints)
        #transferObj = attributes.returnMessageObject(obj,'cgmName')
        """Then we copy it"""
        attributes.copyUserAttrs(i_obj.mNode,closestJoint,attrsToCopy=['cgmPosition','cgmNameModifier','cgmDirection','cgmName'])
	i_obj.connectChildNode(closestJoint,'handleJoint')
	
    #>>>If we stole our parents anchor joint, we need to to reconnect it
    log.debug("STOLEN>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> %s"%self.b_parentStole)
    if self.b_parentStole:
	i_parentControl = self._i_module.moduleParent.templateNull.controlObjects[-1]
	log.debug("parentControl: %s"%i_parentControl.getShortName())
        closestJoint = distance.returnClosestObject(i_parentControl.mNode,l_limbJoints)	
	i_parentControl.connectChildNode(closestJoint,'handleJoint')
    
    #>>>Store it
    #self.i_rigNull.connectChildren(l_limbJoints,'skinJoints','module')
    self.i_rigNull.connectChildrenNodes(l_limbJoints,'skinJoints','module')
    log.debug(self.i_rigNull.skinJoints)       

    #>>>Store these joints and rename the heirarchy
    log.debug("Metaclassing our objects") 
    for i,o in enumerate(l_limbJoints):
        i_o = cgmMeta.cgmObject(o)
        i_o.addAttr('mClass','cgmObject',lock=True) 
	
    self.i_rigNull.skinJoints[0].doName(nameChildren=True,fastIterate=False)
    
    #>>> Orientation    
    #=============== 
    try:
	if not doOrientSegment(self):
	    raise StandardError, "Orient failed"
    except StandardError,error:
        raise StandardError,"Segment orientation failed: %s"%error    
    
    #>>> Set its radius and toggle axis visbility on
    #averageDistance = distance.returnAverageDistanceBetweenObjects (l_limbJoints)
    l_limbJoints = self.i_rigNull.getMessage('skinJoints')
    jointSize = (distance.returnDistanceBetweenObjects (l_limbJoints[0],l_limbJoints[-1])/6)
    reload(attributes)
    #jointSize*.2
    attributes.doMultiSetAttr(l_limbJoints,'radi',3)
    
    return True 

#@r9General.Timer
def doOrientSegment(self):
    """ 
    Segement orienter. Must have a JointFactory Instance
    """ 
    log.debug(">>> doOrientSegment")
    # Get our base info
    #==================	        
    assert self.cls == 'JointFactory.go',"Not a JointFactory.go instance!"
    assert mc.objExists(self._i_module.mNode),"module no longer exists"
    
    #self.i_rigNull = self._i_module.rigNull#refresh
        
    #>>> orientation vectors
    #=======================    
    orientationVectors = search.returnAimUpOutVectorsFromOrientation(self.jointOrientation)
    wantedAimVector = orientationVectors[0]
    wantedUpVector = orientationVectors[1]  
    log.debug("wantedAimVector: %s"%wantedAimVector)
    log.debug("wantedUpVector: %s"%wantedUpVector)
    
    #>>> Put objects in order of closeness to root
    #l_limbJoints = distance.returnDistanceSortedList(l_limbJoints[0],l_limbJoints)
    
    #>>> Segment our joint list by cgmName, prolly a better way to optimize this
    l_cull = copy.copy(self.i_rigNull.getMessage('skinJoints'))
    #joints.orientJointChain(l_cull,self.jointOrientation,'zup')
    if len(l_cull)==1:
        log.debug('Single joint orient mode')
        helper = self.i_templateNull.orientRootHelper.mNode
        if helper:
            log.debug("helper: %s"%helper)
            constBuffer = mc.orientConstraint( helper,l_cull[0],maintainOffset = False)
            mc.delete (constBuffer[0])  
	    #Push rotate to jointOrient
	    i_jnt = cgmMeta.cgmObject(l_cull[0])
	    ##i_jnt.jointOrient = i_jnt.rotate
	    ##i_jnt.rotate = [0,0,0]
	    
    else:#Normal mode
        log.debug('Normal orient mode')        
        self.l_jointSegmentIndexSets= []
        while l_cull:
            matchTerm = search.findRawTagInfo(l_cull[0],'cgmName')
            buffer = []
            objSet = search.returnMatchedTagsFromObjectList(l_cull,'cgmName',matchTerm)
            for o in objSet:
                buffer.append(self.i_rigNull.getMessage('skinJoints').index(o))
            self.l_jointSegmentIndexSets.append(buffer)
            for obj in objSet:
                l_cull.remove(obj)
            
        #>>> un parenting the chain
        for i,i_jnt in enumerate(self.i_rigNull.skinJoints):
	    if i != 0:
		i_jnt.parent = False
            i_jnt.displayLocalAxis = 1#tmp
	    #Reset the jointRotate before orientating
	    ##i_jnt.jointOrient = [0,0,0]	    
	    #Set rotateOrder
            try:
		#i_jnt.rotateOrder = 2
                i_jnt.rotateOrder = self.jointOrientation
	    except StandardError,error:
		log.error("doOrientSegment>>rotate order set fail: %s"%i_jnt.getShortName())
    
        #>>>per segment stuff
        assert len(self.l_jointSegmentIndexSets) == len(self._i_module.i_coreNames.value)#quick check to make sure we've got the stuff we need
        cnt = 0
	log.info("Segment Index sets: %s"%self.l_jointSegmentIndexSets)
        for cnt,segment in enumerate(self.l_jointSegmentIndexSets):#for each segment
	    log.info("On segment: %s"%segment)	    
	    lastCnt = len(self.l_jointSegmentIndexSets)-1
            segmentHelper = self.i_templateNull.controlObjects[cnt].getMessage('helper')[0]
            helperObjectCurvesShapes =  mc.listRelatives(segmentHelper,shapes=True)
            upLoc = locators.locMeCvFromCvIndex(helperObjectCurvesShapes[0],30)        
            if not mc.objExists(segmentHelper) and search.returnObjectType(segmentHelper) != 'nurbsCurve':
                raise StandardError,"doOrientSegment>>> No helper found"
	    ml_skinJoints = self.i_rigNull.skinJoints
	    
            if cnt != lastCnt:
		log.debug(cnt)
                #>>> Create our up object from from the helper object 
                #>>> make a pair list
                #pairList = lists.parseListToPairs(segment)
                """for pair in pairList:
                    constraintBuffer = mc.aimConstraint(self.i_rigNull.skinJoints[pair[1]].mNode,self.i_rigNull.skinJoints[pair[0]].mNode,maintainOffset = False, weight = 1, aimVector = wantedAimVector, upVector = wantedUpVector, worldUpVector = [0,1,0], worldUpObject = upLoc, worldUpType = 'object' )
                    mc.delete(constraintBuffer[0])"""
		for index in segment:
		    if index != 0:
			ml_skinJoints[index].parent = ml_skinJoints[index-1].mNode
		    ml_skinJoints[index].rotate  = [0,0,0]			
		    ml_skinJoints[index].jointOrient  = [0,0,0]	
		    
		    log.info("%s aim to %s"%(ml_skinJoints[index].mNode,ml_skinJoints[index+1].mNode))
		    constraintBuffer = mc.aimConstraint(ml_skinJoints[index+1].mNode,ml_skinJoints[index].mNode,maintainOffset = False, weight = 1, aimVector = wantedAimVector, upVector = wantedUpVector, worldUpVector = [0,1,0], worldUpObject = upLoc, worldUpType = 'object' )
		    mc.delete(constraintBuffer[0])
		    
		    #Push rotate to jointOrient
		    #ml_skinJoints[index].jointOrient = ml_skinJoints[index].rotate
		    #ml_skinJoints[index].rotate = [0,0,0]
		    
		mc.delete(upLoc)
                """for index in segment[-1:]:
		    log.debug("%s orient to %s"%(ml_skinJoints[index].mNode,ml_skinJoints[index-1].mNode))		    
                    constraintBuffer = mc.orientConstraint(ml_skinJoints[index-1].mNode,ml_skinJoints[index].mNode,maintainOffset = False, weight = 1)
                    mc.delete(constraintBuffer[0])"""
                #>>>  Increment and delete the up loc """
            else:
                #>>> Make an aim object and move it """
		i_jnt = self.i_rigNull.skinJoints[segment[-1]]
		log.info(i_jnt.getShortName())
		i_jnt.parent = self.i_rigNull.skinJoints[segment[-1]-1].mNode
		i_jnt.jointOrient  = [0,0,0]
		#ml_skinJoints[index].rotate  = [0,0,0]					

                aimLoc = locators.locMeObject(segmentHelper)
                aimLocGroup = rigging.groupMeObject(aimLoc)
                mc.move (0,0,10, aimLoc, localSpace=True)
                constraintBuffer = mc.aimConstraint(aimLoc,i_jnt.mNode,maintainOffset = False, weight = 1, aimVector = wantedAimVector, upVector = wantedUpVector, worldUpVector = [0,1,0], worldUpObject = upLoc, worldUpType = 'object' )
                mc.delete(constraintBuffer[0])
                mc.delete(aimLocGroup)
                mc.delete(upLoc)
		#>>>Push the first joints orient to 		
		#i_jnt.jointOrient = i_jnt.rotate
		i_jnt.rotate = [0,0,0]		
               	
        #>>>Reconnect the joints
        for cnt,i_jnt in enumerate(self.i_rigNull.skinJoints[1:]):#parent each to the one before it
            i_jnt.parent = self.i_rigNull.skinJoints[cnt].mNode
	    i_p = cgmMeta.cgmObject(i_jnt.parent)
	    #Verify inverse scale connection
	    cgmMeta.cgmAttr(i_jnt,"inverseScale").doConnectIn("%s.scale"%i_p.mNode)

    if self._i_module.moduleType in ['foot']:
        log.debug("Special case orient")
        if len(self.i_rigNull.getMessage('skinJoints')) > 1:
            helper = self.i_templateNull.orientRootHelper.mNode
            if helper:
                log.debug("Root joint fix...")                
                rootJoint = self.i_rigNull.getMessage('skinJoints')[0]
                self.i_rigNull.skinJoints[1].parent = False #unparent the first child
                constBuffer = mc.orientConstraint( helper,rootJoint,maintainOffset = False)
                mc.delete (constBuffer[0])   
                self.i_rigNull.skinJoints[1].parent = rootJoint
		self.i_rigNull.skinJoints[1].jointOrient = self.i_rigNull.skinJoints[1].rotate
		self.i_rigNull.skinJoints[1].rotate = [0,0,0]        
    
    #Copy 
    """ Freeze the rotations """
    metaFreezeJointOrientation(self.i_rigNull.skinJoints)   
    
    #Connect to parent
    if self._i_module.getMessage('moduleParent'):#If we have a moduleParent, constrain it
	connectToParentModule(self.m)    
	
    for i,i_jnt in enumerate(self.i_rigNull.skinJoints):
	log.info(i_jnt.getAttr('cgmName'))
	if i_jnt.getAttr('cgmName') in ['ankle']:
	    log.info("Copy orient from parent mode: %s"%i_jnt.getShortName())
	    joints.doCopyJointOrient(i_jnt.parent,i_jnt.mNode)    
    return True




#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Module tools
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
@r9General.Timer
def deleteSkeleton(i_module,*args,**kws):  
    if not i_module.isSkeletonized():
        log.warning("Not skeletonized. Cannot delete skeleton: '%s'"%i_module.getShortName())
        return False
    
    #We need to see if any of or skinJoints have children
    l_strayChildren = []
    l_moduleJoints = i_module.rigNull.getMessage('skinJoints',longNames = True)
    for i_jnt in i_module.rigNull.skinJoints:
        buffer = i_jnt.getChildren(True)
        for c in buffer:
            if c not in l_moduleJoints:
                try:
                    i_c = cgmMeta.cgmObject(c)
                    i_c.parent = False
                    l_strayChildren.append(i_c.mNode)
                except StandardError,error:
                    log.warning(error)     
    log.debug("l_strayChildren: %s"%l_strayChildren)
    mc.delete(i_module.rigNull.getMessage('skinJoints'))
    return True

@r9General.Timer
def connectToParentModule(self):
    """
    Pass a module class. Constrains template root to parent's closest template object
    """
    log.debug(">>> constrainToParentModule")
    if not self.isSkeletonized():
        log.error("Must be skeletonized to contrainToParentModule: '%s' "%self.getShortName())
        return False
    if not self.getMessage('moduleParent'):
        return False
    else:
        #>>> Get some info
        i_rigNull = self.rigNull #Link
        i_parent = self.moduleParent #Link
        parentState = i_parent.getState() 
        if i_parent.isSkeletonized():#>> If we have a module parent
            #>> If we have another anchor
            parentSkinJoints = i_parent.rigNull.getMessage('skinJoints')
            closestObj = distance.returnClosestObject(i_rigNull.getMessage('skinJoints')[0],parentSkinJoints)
            i_rigNull.skinJoints[0].parent = closestObj
            
        else:
            log.debug("Parent has not been skeletonized...")           
            return False  
    return True


#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Module tools
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>  

def skeletonizeCharacter(masterNull):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Skeletonizes a character
    
    ARGUMENTS:
    masterNull(string)
    
    RETURNS:
    nothin
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    modules = modules.returnModules(masterNull)
    orderedModules = modules.returnOrderedModules(modules)
    #>>> Do the spine first
    stateCheck = modules.moduleStateCheck(orderedModules[0],['template'])
    if stateCheck == 1:
        spineJoints = skeletonize(orderedModules[0])
    else:
        print ('%s%s' % (module,' has already been skeletonized. Moving on...'))
    
    #>>> Do the rest
    for module in orderedModules[1:]:
        stateCheck = modules.moduleStateCheck(module,['template'])
        if stateCheck == 1:
            templateNull = modules.returnTemplateNull(module)
            root =  modules.returnInfoNullObjects(module,'templatePosObjects',types='templateRoot')
            
            #>>> See if our item has a non default anchor
            anchored = storeTemplateRootParent(module) 
            if anchored == True:
                anchor =  attributes.returnMessageObject(root[0],'skeletonParent')
                closestJoint = distance.returnClosestObject(anchor,spineJoints)
            else:
                closestJoint = distance.returnClosestObject(root[0],spineJoints) 
        
            l_limbJoints = skeletonize(module)
            rootName = rigging.doParentReturnName(l_limbJoints[0],closestJoint)
            print rootName
        else:
            print ('%s%s' % (module,' has already been skeletonized. Moving on...'))

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def skeletonStoreCharacter(masterNull):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    stores a skeleton of a character
    
    ARGUMENTS:
    masterNull(string)
    
    RETURNS:
    nothin
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    modules = modules.returnModules(masterNull)
    orderedModules = modules.returnOrderedModules(modules)
    #>>> Do the spine first
    stateCheck = modules.moduleStateCheck(orderedModules[0],['template'])
    if stateCheck == 1:
        spineJoints = modules.saveTemplateToModule(orderedModules[0])
    else:
        print ('%s%s' % (module,' has already been skeletonized. Moving on...'))
    
    #>>> Do the rest
    for module in orderedModules[1:]:
        stateCheck = modules.moduleStateCheck(module,['template'])
        if stateCheck == 1:
            templateNull = modules.returnTemplateNull(module)        
            modules.saveTemplateToModule(module)
        else:
            print ('%s%s' % (module,' has already been skeletonized. Moving on...'))

       
         
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>            

def storeTemplateRootParent(moduleNull):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Stores the template root parent to the root control if there is a new one
    
    ARGUMENTS:
    moduleNull(string)
    
    RETURNS:
    success(bool)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    templateNull = modules.returnTemplateNull(moduleNull)
    root =   modules.returnInfoNullObjects(moduleNull,'templatePosObjects',types='templateRoot')
    parent = search.returnParentObject(root, False)
    if parent != templateNull:
        if parent != False:
            attributes.storeObjectToMessage(parent,root,'skeletonParent')
            return True
    return False



#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>    
#>>> Tools    
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def metaFreezeJointOrientation(targetJoints):
    """
    Copies joint orietnations from one joint to others
    """
    if type(targetJoints) not in [list,tuple]:targetJoints=[targetJoints]

    ml_targetJoints = cgmMeta.validateObjListArg(targetJoints,cgmMeta.cgmObject)
    for i_jnt in ml_targetJoints:
	if i_jnt.getConstraintsTo():
            log.warning("freezeJointOrientation>> target joint has constraints. Can't change orientation. Culling from targets: '%s'"%i_jnt.getShortName())
	    return False
	if i_jnt.getMayaType() != 'joint':
            log.warning("freezeJointOrientation>> target joint is not a joint. Can't change orientation. Culling from targets: '%s'"%i_jnt.getShortName())
	    return False
	
    #buffer parents and children of 
    d_children = {}
    d_parent = {}
    for i_jnt in ml_targetJoints:
        d_children[i_jnt] = cgmMeta.validateObjListArg( mc.listRelatives(i_jnt.mNode, path=True, c=True),cgmMeta.cgmObject,True) or []
	d_parent[i_jnt] = i_jnt.parent
    for i_jnt in ml_targetJoints:
	for i,i_c in enumerate(d_children[i_jnt]):
	    log.info(i_c.getShortName())
	    log.info("freezeJointOrientation>> parented '%s' to world to orient parent"%i_c.mNode)
	    i_c.parent = False
	
    #Orient
    for i,i_jnt in enumerate(ml_targetJoints):
	"""
	So....jointOrient is always in xyz rotate order
	dup,rotate order
	Unparent, add rotate & joint rotate, push value, zero rotate, parent back, done
	"""
	i_jnt.parent = d_parent.get(i_jnt)#parent back first before duping
	buffer = mc.duplicate(i_jnt.mNode,po=True,ic=False)[0]#Duplicate the joint
	i_dup = cgmMeta.cgmObject(buffer)
	i_dup.rotateOrder = 0
        mc.delete(mc.orientConstraint(i_jnt.mNode, i_dup.mNode, w=1, maintainOffset = False))
	
	#i_dup.parent = False
	
	l_rValue = i_dup.rotate
	l_joValue = i_dup.jointOrient
	l_added = cgmMath.list_add(l_rValue,l_joValue)	
	
	i_dup.jointOrientX = l_added[0]
	i_dup.jointOrientY = l_added[1]
	i_dup.jointOrientZ = l_added[2]	
	i_dup.rotate = [0,0,0]
	
	i_dup.parent = i_jnt.parent
	
	i_jnt.rotate = [0,0,0]
	i_jnt.jointOrient = i_dup.jointOrient	
	
        i_dup.delete()
	
    #reparent
    for i_jnt in ml_targetJoints:
        for i_c in d_children[i_jnt]:
            log.info("freezeJointOrientation>> parented '%s' back"%i_c.getShortName())
            i_c.parent = i_jnt.mNode 
	    cgmMeta.cgmAttr(i_c,"inverseScale").doConnectIn("%s.scale"%i_jnt.mNode )
	    
    return True






def orientSegment(l_limbJoints,posTemplateObjects,orientation):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Basic limb skeletonizer
    
    ARGUMENTS:
    l_limbJoints(list)
    templeateObjects(list)
    orientation(string) - ['xyz','yzx','zxy','xzy','yxz','zyx']
    
    RETURNS:
    l_limbJoints(list)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """  
    """ orientation vectors"""
    orientationVectors = search.returnAimUpOutVectorsFromOrientation(orientation)
    wantedAimVector = orientationVectors[0]
    wantedUpVector = orientationVectors[1]    
    
    """put objects in order of closeness to root"""
    l_limbJoints = distance.returnDistanceSortedList(l_limbJoints[0],l_limbJoints)
    
    #>>> Segment our joint list by names
    jointSegmentsList = []
    cullList = []
    """ gonna be culling items from the list so need to rebuild it, just doing a list1 = list2 
    somehow keeps the relationship....odd """
    for obj in l_limbJoints:
        cullList.append(obj)
    
    while len(cullList) > 0:
        matchTerm = search.returnTagInfo(cullList[0],'cgmName')
        objSet = search.returnMatchedTagsFromObjectList(cullList,'cgmName',matchTerm)
        jointSegmentsList.append(objSet)
        for obj in objSet:
            cullList.remove(obj)
            
    #>>> get our orientation helpers
    helperObjects = []
    for obj in posTemplateObjects:
        templateObj = attributes.returnMessageObject(obj,'cgmName')
        helperObjects.append(attributes.returnMessageObject(templateObj,'orientHelper'))
    
    #>>> un parenting the chain
    for joint in l_limbJoints[1:]:
        mc.parent(joint,world=True)
    
    #>>>per segment stuff
    cnt = 0
    for segment in jointSegmentsList:
	log.info("On segment: %s"%segment)
        if len(segment) > 1:
            """ creat our up object from from the helper object """
            helperObjectCurvesShapes =  mc.listRelatives(helperObjects[cnt],shapes=True)
            upLoc = locators.locMeCvFromCvIndex(helperObjectCurvesShapes[0],30)
            """ make a pair list"""
            pairList = lists.parseListToPairs(segment)
            for pair in pairList:
                """ set up constraints """
                constraintBuffer = mc.aimConstraint(pair[1],pair[0],maintainOffset = False, weight = 1, aimVector = wantedAimVector, upVector = wantedUpVector, worldUpVector = [0,1,0], worldUpObject = upLoc, worldUpType = 'object' )
                mc.delete(constraintBuffer[0])
            for obj in segment[-1:]:
                constraintBuffer = mc.orientConstraint(segment[-2],obj,maintainOffset = False, weight = 1)
                mc.delete(constraintBuffer[0])
            """ increment and delete the up loc """
            cnt+=1
            mc.delete(upLoc)
        else:
            helperObjectCurvesShapes =  mc.listRelatives(helperObjects[cnt],shapes=True)
            upLoc = locators.locMeCvFromCvIndex(helperObjectCurvesShapes[0],30)
            """ make an aim object """
            aimLoc = locators.locMeObject(helperObjects[cnt])
            aimLocGroup = rigging.groupMeObject(aimLoc)
            mc.move (10,0,0, aimLoc, localSpace=True)
            constraintBuffer = mc.aimConstraint(aimLoc,segment[0],maintainOffset = False, weight = 1, aimVector = wantedAimVector, upVector = wantedUpVector, worldUpVector = [0,1,0], worldUpObject = upLoc, worldUpType = 'object' )
            mc.delete(constraintBuffer[0])
            mc.delete(aimLocGroup)
            mc.delete(upLoc)
            cnt+=1
    #>>>reconnect the joints
    pairList = lists.parseListToPairs(l_limbJoints)
    for pair in pairList:
        mc.parent(pair[1],pair[0])
        
    """ Freeze the rotations """
    mc.makeIdentity(l_limbJoints[0],apply=True,r=True)
    return l_limbJoints



