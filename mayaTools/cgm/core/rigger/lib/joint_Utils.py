"""
cgmLimb
Josh Burton (under the supervision of David Bokser:)
www.cgmonks.com
1/12/2011

Key:
1) Class - Limb
    Creates our rig objects
2)  


"""
# From Python =============================================================
import copy
import re
import time

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

# From Maya =============================================================
import maya.cmds as mc

# From Red9 =============================================================
from Red9.core import Red9_Meta as r9Meta

# From cgm ==============================================================
from cgm.core import cgm_Meta as cgmMeta
from cgm.core import cgm_General as cgmGeneral
from cgm.core.classes import SnapFactory as Snap
from cgm.core.cgmPy import validateArgs as cgmValid

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

#>>> Utilities
#===================================================================
def duplicateJointInPlace(joint, asMeta = True):
    """
    :parameters:
        joint | str/instance
            Joint to duplicate
        asMeta | bool
            What to return as

    :returns:
        str or instance of new joint

    :raises:
        TypeError | if 'arg' is not a joint
    """ 
    _str_func_ = 'duplicateJointInPlace'
    try:
        mJoint = cgmMeta.validateObjArg(joint, mayaType = 'joint', mType = 'cgmObject')    

        #dup = mc.joint()
        mDup = mJoint.doDuplicate(parentOnly=True)

        #mDup.parent = mJoint.parent 
        #mc.delete(mc.parentConstraint(mJoint.mNode,mDup.mNode))
        '''
	('rotateOrder','rotateAxisX','rotateAxisY','rotateAxisZ',
	'inheritsTransform','drawStyle','radius',
	'jointTypeX','jointTypeY','jointTypeZ',
	'stiffnessX','stiffnessY','stiffnessZ',
	'preferredAngleX','preferredAngleY','preferredAngleZ',
	'jointOrientX','jointOrientY','jointOrientZ','segmentScaleCompensate','showManipDefault',
	'displayHandle','displayLocalAxis','selectHandleX','selectHandleY','selectHandleZ'),
	'''
        mDup.rotateOrder = mJoint.rotateOrder
        mDup.jointOrient = mJoint.jointOrient
        mDup.rotateAxis = mJoint.rotateAxis
        mDup.inheritsTransform = mJoint.inheritsTransform
        mDup.radius = mJoint.radius
        mDup.stiffness = mJoint.stiffness
        mDup.preferredAngle = mJoint.preferredAngle
        mDup.segmentScaleCompensate = mJoint.segmentScaleCompensate
        #mDup.displayHandle = mJoint.displayHandle
        #mDup.selectHandle = mJoint.selectHandle


        #Inverse scale...
        mAttr_inverseScale = cgmMeta.cgmAttr(mJoint,'inverseScale')
        _driver = mAttr_inverseScale.getDriver()
        if mAttr_inverseScale.getDriver():
            cgmMeta.cgmAttr(mDup,"inverseScale").doConnectIn(_driver)

        mAttr_inverseScale.getDriver(mJoint)

        for attr in mJoint.getUserAttrs():
            try:cgmMeta.cgmAttr(mJoint,attr).doCopyTo(mDup.mNode)
            except Exception,err:log.error("duplicateJointInPlace({0}) .{1} failed << {2} >>".format(mJoint.p_nameShort,attr,err))
        if asMeta:
            return mDup
        return mDup.mNode
    except Exception,error:
        raise Exception,"{0} | {1}".format(_str_func_,error)

def mirrorJointOrientation(*args,**kws):
    """
    Function to mirror a joint orientation in place
    @kws
    baseCurve -- curve on check
    """
    class fncWrap(cgmGeneral.cgmFuncCls):
        def __init__(self,*args,**kws):
            """
            """	
            super(fncWrap, self).__init__(curve = None)
            self._str_funcName = 'mirrorJointOrientation'
            self._b_WIP = True
            self._l_ARGS_KWS_DEFAULTS = [{'kw':'l_joints',"default":None},
                                         {'kw':'orientation',"default":'zyx'}]	    
            self.__dataBind__(*args,**kws)
            #=================================================================
            #log.info(">"*3 + " Log Level: %s "%log.getEffectiveLevel())	

        def __func__(self):
            """
            """
            self.ml_joints = cgmMeta.validateObjListArg(self.d_kws['l_joints'],cgmMeta.cgmObject,mayaType='joint',noneValid=False)
            self.mi_orientation = cgmValid.simpleOrientation(self.d_kws['orientation'],self._str_funcCombined)
            ml_chain = self.ml_joints

            for mJoint in ml_chain:
                mJoint.__setattr__("r%s"%self.mi_orientation.p_string[2],180)

            metaFreezeJointOrientation(ml_chain)

    return fncWrap(*args,**kws).go()

#@cgmGeneral.Timer
def metaFreezeJointOrientation(targetJoints):
    """
    Freeze joint orientations in place. 
    """
    try:
        _str_funcName = "metaFreezeJointOrientation"		
        #t1 = time.time()

        if type(targetJoints) not in [list,tuple]:targetJoints=[targetJoints]

        ml_targetJoints = cgmMeta.validateObjListArg(targetJoints,'cgmObject',mayaType='joint')

        #log.info("{0}>> meta'd: {1}".format(_str_funcName, "%0.3f seconds"%(time.time() - t1)))
        #t1 = time.time()				
        '''
		for i_jnt in ml_targetJoints:
			if i_jnt.getConstraintsTo():
			log.warning("freezeJointOrientation>> target joint has constraints. Can't change orientation. Culling from targets: '%s'"%i_jnt.getShortName())
			return False
			'''
        #buffer parents and children of 
        d_children = {}
        d_parent = {}
        mi_parent = cgmMeta.validateObjArg(ml_targetJoints[0].parent,noneValid=True)
        #log.info('validate')
        for i,i_jnt in enumerate(ml_targetJoints):
            _relatives = mc.listRelatives(i_jnt.mNode, path=True, c=True)
            log.debug("{0} relatives: {1}".format(i,_relatives))
            d_children[i_jnt] = cgmMeta.validateObjListArg( _relatives ,'cgmObject',True) or []
            d_parent[i_jnt] = cgmMeta.validateObjArg(i_jnt.parent,noneValid=True)
        for i_jnt in ml_targetJoints:
            for i,i_c in enumerate(d_children[i_jnt]):
            #log.debug(i_c.getShortName())
            #log.debug("freezeJointOrientation>> parented '%s' to world to orient parent"%i_c.mNode)
                i_c.parent = False
        if mi_parent:
            ml_targetJoints[0].parent = False
        #log.info('gather data')
        #log.info("{0}>> parent data: {1}".format(_str_funcName, "%0.3f seconds"%(time.time() - t1)))
        #t1 = time.time()	

        #Orient
        t_loop = time.time()
        for i,i_jnt in enumerate(ml_targetJoints):
            """
			So....jointOrient is always in xyz rotate order
			dup,rotate order
			Unparent, add rotate & joint rotate, push value, zero rotate, parent back, done
			"""    
            log.debug("parent...")
            if i != 0 and d_parent.get(i_jnt):
                i_jnt.parent = d_parent.get(i_jnt)#parent back first before duping
            #log.info('{0} parent'.format(i))
            #log.info("{0}>> {2} parent: {1}".format(_str_funcName, "%0.3f seconds"%(time.time() - t1), i_jnt.p_nameShort))
            #t1 = time.time()	

            log.debug("dup...")
            #i_dup = duplicateJointInPlace(i_jnt)
            i_dup = i_jnt.doDuplicate(parentOnly = True)
            #log.debug("{0} | UUID: {1}".format(i_jnt.mNode,i_jnt.getMayaAttr('UUID')))
            #log.debug("{0} | UUID: {1}".format(i_dup.mNode,i_dup.getMayaAttr('UUID')))
            i_dup.parent = i_jnt.parent
            i_dup.rotateOrder = 0

            #log.info("{0}>> {2} dup: {1}".format(_str_funcName, "%0.3f seconds"%(time.time() - t1), i_jnt.p_nameShort))
            #t1 = time.time()	

            #New method  ----
            log.debug("loc...")

            mi_zLoc = i_jnt.doLoc(fastMode = True)#Make some locs
            #mi_yLoc = mi_zLoc.doDuplicate()

            """mi_zLoc = cgmMeta.cgmObject(mc.spaceLocator()[0])
			objTrans = mc.xform(i_jnt.mNode, q=True, ws=True, sp=True)
			objRot = mc.xform(i_jnt.mNode, q=True, ws=True, ro=True)

			mc.move (objTrans[0],objTrans[1],objTrans[2], mi_zLoc.mNode)			
			mc.rotate (objRot[0], objRot[1], objRot[2], mi_zLoc.mNode, ws=True)
			mi_zLoc.rotateOrder = i_jnt.rotateOrder"""
            mi_yLoc = mi_zLoc.doDuplicate()

            #log.info('{0} loc'.format(i))

            #log.info("{0}>> {2} loc: {1}".format(_str_funcName, "%0.3f seconds"%(time.time() - t1), i_jnt.p_nameShort))
            #t1 = time.time()			

            log.debug("group...")
            str_group = mi_zLoc.doGroup(asMeta = False) #group for easy move
            mi_yLoc.parent = str_group
            #log.info('{0} group'.format(i))

            #log.info("{0}>> {2} group: {1}".format(_str_funcName, "%0.3f seconds"%(time.time() - t1), i_jnt.p_nameShort))
            #t1 = time.time()	

            mi_zLoc.tz = 1#Move
            mi_yLoc.ty = 1

            mc.makeIdentity(i_dup.mNode, apply = 1, jo = 1)#Freeze

            #Aim
            log.debug("constrain...")

            str_const = mc.aimConstraint(mi_zLoc.mNode,i_dup.mNode,maintainOffset = False, weight = 1, aimVector = [0,0,1], upVector = [0,1,0], worldUpVector = [0,1,0], worldUpObject = mi_yLoc.mNode, worldUpType = 'object' )[0]
            #log.info('{0} constrain'.format(i))
            #log.info("{0}>> {2} constraint: {1}".format(_str_funcName, "%0.3f seconds"%(time.time() - t1), i_jnt.p_nameShort))
            #t1 = time.time()				
            i_jnt.rotate = [0,0,0] #Move to joint
            i_jnt.jointOrient = i_dup.rotate
            #log.info('{0} delete'.format(i))

            log.debug("delete...")	    
            mc.delete([str_const,str_group])#Delete extra stuff str_group
            i_dup.delete()
            #log.info("{0}>> {2} clean: {1}".format(_str_funcName, "%0.3f seconds"%(time.time() - t1), i_jnt.p_nameShort))
            #t1 = time.time()							
        #log.info("{0}>> orienting: {1}".format(_str_funcName, "%0.3f seconds"%(time.time() - t_loop)))
        #t1 = time.time()				
        #reparent
        if mi_parent:
            try:ml_targetJoints[0].parent = mi_parent
            except Exception,error: raise StandardError,"Failed to parent back %s"%error
        for i,i_jnt in enumerate(ml_targetJoints):
            for ii,i_c in enumerate(d_children[i_jnt]):
                #log.info("{0} | {1}".format(i,ii))
                #log.info(i_c)
                log.debug("freezeJointOrientation>> parented '%s' back"%i_c.getShortName())
                i_c.parent = i_jnt.mNode 
                cgmMeta.cgmAttr(i_c,"inverseScale").doConnectIn("%s.scale"%i_jnt.mNode )
        #log.info('reparent')
        #log.info("{0}>> reparent: {1}".format(_str_funcName, "%0.3f seconds"%(time.time() - t1)))
        #t1 = time.time()				
        return True
    except Exception,error:raise Exception,"metaFreezeJointOrientation | {0} ".format(error)

def freezeJointOrientation(targetJoints):
    return metaFreezeJointOrientation(targetJoints)

def get_orientChild(targetJoint):
    mi_targetJoint = cgmMeta.validateObjArg(targetJoint,cgmMeta.cgmObject,mayaType='joint')
    ml_childrenJoints = cgmMeta.validateObjListArg(mi_targetJoint.getChildren(),cgmMeta.cgmObject,mayaType='joint')
    if not ml_childrenJoints:
        log.warning("%s.get_orientChild >> failed to find children joints to check"%(mi_targetJoint.p_nameShort))
        return False

    for i_j in ml_childrenJoints:
        """
	Measure dist
	"""
        pass


#>>> Helper joints
#===================================================================
__l_helperTypes__ = 'halfHold','childRootHold','halfPush'

def add_defHelpJoint(targetJoint,childJoint = None, helperType = 'halfPush',
                     orientation = 'zyx',doSetup = True, forceNew = False):
    """
    Add helper joints to other joints

    @KWS
    targetJoint(string/inst)
    helperType(str) --
         'halfHold' -- like a regular bend joint that needs a holder at it's root, like a finger
    'childRootHold' -- holds form on a hard rotate, like a finger root
    jointUp(str) --
    orientation(str)
    forceNew(bool) -- delete if exists

    """
    mi_posLoc = False
    if orientation != 'zyx':
        raise NotImplementedError, "add_defHelpJoints >> only currently can do orienation of 'zyx'"
    #Validate base info
    mi_targetJoint = cgmMeta.validateObjArg(targetJoint,cgmMeta.cgmObject,mayaType='joint')
    log.debug(">>> %s.add_defHelpJoint >> "%mi_targetJoint.p_nameShort + "="*75)            

    #>>Child joint
    #TODO -- implement child guessing
    mi_childJoint = cgmMeta.validateObjArg(childJoint,cgmMeta.cgmObject,mayaType='joint',noneValid=True)
    log.debug("%s.add_defHelpJoints >> Child joint : '%s'"%(mi_targetJoint.p_nameShort,mi_childJoint))

    str_plugHook = 'defHelp_joints'

    #Validate some data
    d_typeChecks = {'halfHold':[mi_childJoint],'childRootHold':[mi_childJoint],'halfPush':[mi_childJoint]}
    if helperType in d_typeChecks.keys():
        for k in d_typeChecks[helperType]:
            if not k:
                log.warning("%s.add_defHelpJoints >> must have valid %s for helperType: '%s'"%(mi_targetJoint.p_nameShort,k,helperType))	    
                return False    

    #>Register
    #----------------------------------------------------------------
    #First see if we have one
    ml_dynDefHelpJoints = cgmMeta.validateObjListArg(mi_targetJoint.msgList_get(str_plugHook),cgmMeta.cgmObject,noneValid=True)
    i_matchJnt = False
    for i_jnt in ml_dynDefHelpJoints:
        log.debug(i_jnt.p_nameShort)
        if i_jnt.getAttr('defHelpType') == helperType and i_jnt.getMessage('defHelp_target') == [mi_targetJoint.p_nameLong]:
            i_matchJnt = i_jnt
            log.debug("%s.add_defHelpJoints >> Found match: '%s'"%(mi_targetJoint.p_nameShort,i_matchJnt.p_nameShort))	    	    
            break

    if i_matchJnt:#if we have a match
        if forceNew:
            log.debug("%s.add_defHelpJoints >> helper exists, no force new : '%s'"%(mi_targetJoint.p_nameShort,i_matchJnt.p_nameShort))	    	    
            ml_dynDefHelpJoints.remove(i_matchJnt)	    
            mc.delete(i_matchJnt.mNode)
        else:
            log.debug("%s.add_defHelpJoints >> helper exists, no force new : '%s'"%(mi_targetJoint.p_nameShort,i_matchJnt.p_nameShort))	    

    if not i_matchJnt:
        log.debug("No match joint")
        i_dupJnt = mi_targetJoint.doDuplicate(inputConnections = False)#Duplicate
        #i_dupJnt= duplicateJointInPlace(mi_targetJoint)

        i_dupJnt.addAttr('cgmTypeModifier',helperType)#Tag
        i_dupJnt.addAttr('defHelpType',helperType,lock=True)#Tag    
        i_dupJnt.doName()#Rename
        i_dupJnt.parent = mi_targetJoint#Parent
        ml_dynDefHelpJoints.append(i_dupJnt)#append to help joint list

        i_dupJnt.connectChildNode(mi_childJoint,"defHelp_childTarget")#Connect Child target
        mi_targetJoint.msgList_append(str_plugHook,i_dupJnt,'defHelp_target')#Connect
    else:
        i_dupJnt = i_matchJnt
        #------------------------------------------------------------
        log.debug("%s.add_defHelpJoints >> Created helper joint : '%s'"%(mi_targetJoint.p_nameShort,i_dupJnt.p_nameShort))

    if doSetup:
        try:setup_defHelpJoint(i_dupJnt,orientation)
        except Exception,error:
            log.warning("%s.add_defHelpJoints >> Failed to setup | %s"%(i_dupJnt.p_nameShort,error))	                
            for arg in error.args:
                log.warning(arg)

    return i_dupJnt

def setup_defHelpJoint(targetJoint,orientation = 'zyx'):
    """
    Setup a helper joint

    @KWS
    targetJoint(string/inst) -- must be helper joint
    orientation(str)
    forceNew(bool) -- delete if exists

    helperTypes --
     'halfHold' -- like a regular bend joint that needs a holder at it's root, like a finger
     'childRootHold' -- holds form on a hard rotate, like a finger root
     'halfPush' -- like a regular bend joint that needs a holder at it's root, like a finger
    """
    mi_posLoc = False
    if orientation != 'zyx':
        raise NotImplementedError, "add_defHelpJoints >> only currently can do orienation of 'zyx'"

    #Validate base info
    mi_helperJoint = cgmMeta.validateObjArg(targetJoint,cgmMeta.cgmObject,mayaType='joint')
    mi_targetJoint = cgmMeta.validateObjArg(mi_helperJoint.getMessage('defHelp_target'),cgmMeta.cgmObject,mayaType='joint')        
    mi_childJoint = cgmMeta.validateObjArg(mi_helperJoint.getMessage('defHelp_childTarget'),cgmMeta.cgmObject,mayaType='joint')    
    str_helperType = mi_helperJoint.getAttr('defHelpType')
    if not str_helperType in __l_helperTypes__:
        log.warning("%s.setup_defHelpJoint >> '%s' not a valid helperType: %s"%(mi_helperJoint.p_nameShort,str_helperType,__l_helperTypes__))	    
        return False

    log.debug(">>> %s.setup_defHelpJoint >> "%mi_helperJoint.p_nameShort + "="*75)            
    #>Setup
    #---------------------------------------------------------------- 
    if str_helperType == 'halfHold':
        mi_helperJoint.tx = mi_childJoint.tx *.5
        mi_helperJoint.ty = mi_childJoint.ty *.5
        mi_helperJoint.tz = mi_childJoint.tz *.5

        mi_helperJoint.__setattr__("t%s"%orientation[1],(-mi_childJoint.tz *.2))

        #Setup sd
        '''
	""" set our keyframes on our curve"""
	for channel in :
	    mc.setKeyframe (attributeHolder,sqshStrchAttribute, time = cnt, value = 1)
	    """ making the frame cache nodes """
	    frameCacheNodes.append(nodes.createNamedNode(jointChain[jnt],'frameCache'))
	    cnt+=1
	""" connect it """
	for cacheNode  in frameCacheNodes:
	    mc.connectAttr((sqshStrchAttribute),(cacheNode+'.stream'))
	cnt=1
	""" set the vary time """
	for cacheNode in frameCacheNodes:
	    mc.setAttr((cacheNode+'.varyTime'),cnt)
	    cnt+=1	
	'''
        #With half hold, our driver is the child joint
        str_driverRot = "%s.r%s"%(mi_childJoint.mNode,orientation[2])
        str_drivenTransAim = "%s.t%s"%(mi_helperJoint.mNode,orientation[0])
        f_baseTransValue = mi_helperJoint.getAttr("t%s"%(orientation[0]))
        f_sdkTransValue = f_baseTransValue + (f_baseTransValue * .3)	
        mc.setDrivenKeyframe(str_drivenTransAim,
                             currentDriver = str_driverRot,
                             driverValue = 0,value = f_baseTransValue)
        mc.setDrivenKeyframe(str_drivenTransAim,
                             currentDriver = str_driverRot,
                             driverValue = 110,value = f_sdkTransValue)	

    elif str_helperType == 'halfPush':
        mi_helperJoint.tx = mi_childJoint.tx *.5
        mi_helperJoint.ty = mi_childJoint.ty *.5
        mi_helperJoint.tz = mi_childJoint.tz *.5

        mi_helperJoint.__setattr__("t%s"%orientation[1],-(mi_childJoint.tz *.2))

        #With half push, our driver is the target joint
        str_driverRot = "%s.r%s"%(mi_targetJoint.mNode,orientation[2])
        str_drivenTransAim = "%s.t%s"%(mi_helperJoint.mNode,orientation[0])
        f_baseTransValue = mi_helperJoint.getAttr("t%s"%(orientation[0]))
        f_sdkTransValue = f_baseTransValue + (f_baseTransValue * .3)	
        mc.setDrivenKeyframe(str_drivenTransAim,
                             currentDriver = str_driverRot,
                             driverValue = 0,value = f_baseTransValue)
        mc.setDrivenKeyframe(str_drivenTransAim,
                             currentDriver = str_driverRot,
                             driverValue = 110,value = f_sdkTransValue)	

    elif str_helperType == 'childRootHold':
        '''mi_helperJoint.__setattr__("t%s"%orientation[1],(-mi_childJoint.getMayaAttr("t%s"%(orientation[0])) *.2))
	mi_helperJoint.parent = mi_targetJoint.parent
	if not mi_posLoc:mi_posLoc = mi_helperJoint.doLoc()#Make sure we have a loc
	mi_posLoc.parent = mi_helperJoint.mNode#Parent loc to i_dup to make sure we're in same space

	f_baseUpTransValue = mi_helperJoint.getAttr("t%s"%(orientation[1]))
	f_sdkUpTransValue = mi_childJoint.getAttr("t%s"%(orientation[0])) * -.25

	f_baseAimTransValue = mi_helperJoint.getAttr("t%s"%(orientation[0]))
	f_sdkAimTransValue = mi_childJoint.getAttr("t%s"%(orientation[0])) * -.5'''
        mi_helperJoint.__setattr__("t%s"%orientation[1],(-mi_childJoint.getMayaAttr("t%s"%(orientation[0])) *.2))
        mi_helperJoint.__setattr__("t%s"%orientation[0],(-mi_childJoint.getMayaAttr("t%s"%(orientation[0])) *.1))	
        mi_helperJoint.parent = mi_targetJoint.parent
        if not mi_posLoc:mi_posLoc = mi_helperJoint.doLoc()#Make sure we have a loc
        mi_posLoc.parent = mi_helperJoint.mNode#Parent loc to i_dup to make sure we're in same space

        f_baseUpTransValue = mi_helperJoint.getAttr("t%s"%(orientation[1]))
        f_sdkUpTransValue = mi_targetJoint.getAttr("t%s"%(orientation[0])) * -.05

        f_baseAimTransValue = mi_helperJoint.getAttr("t%s"%(orientation[0]))
        f_sdkAimTransValue = mi_targetJoint.getAttr("t%s"%(orientation[0])) * -.25	

        #Move the pos loc for our pose ----------------------------------
        mi_posLoc.__setattr__("t%s"%orientation[0],f_sdkAimTransValue)
        mi_posLoc.__setattr__("t%s"%orientation[1],f_sdkUpTransValue)
        mi_posLoc.parent = mi_helperJoint.parent

        #With childRootHold, our driver is the target joint --------------
        str_driverRot = "%s.r%s"%(mi_targetJoint.mNode,orientation[2])

        #Up ---------------------------------------------------------------
        str_drivenTransUp = "%s.t%s"%(mi_helperJoint.mNode,orientation[1])

        mc.setDrivenKeyframe(str_drivenTransUp,
                             currentDriver = str_driverRot,
                             driverValue = 0,value = f_baseUpTransValue)
        mc.setDrivenKeyframe(str_drivenTransUp,
                             currentDriver = str_driverRot,
                             driverValue = 120,value = mi_posLoc.getAttr("t%s"%orientation[1]))	

        #Aim ---------------------------------------------------------------
        str_drivenTransAim = "%s.t%s"%(mi_helperJoint.mNode,orientation[0])	

        mc.setDrivenKeyframe(str_drivenTransAim,
                             currentDriver = str_driverRot,
                             driverValue = 0,value = f_baseAimTransValue)
        mc.setDrivenKeyframe(str_drivenTransAim,
                             currentDriver = str_driverRot,
                             driverValue = 120,value = mi_posLoc.getAttr("t%s"%orientation[0]))	


    if mi_posLoc:mi_posLoc.delete()
    return
