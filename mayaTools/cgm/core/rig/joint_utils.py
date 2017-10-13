"""
------------------------------------------
snap_utils: cgm.core.lib.joint_utils
Author: Josh Burton
email: jjburton@cgmonks.com
Website : http://www.cgmonks.com
------------------------------------------

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
from maya import mel
# From Red9 =============================================================

# From cgm ==============================================================
import cgm.core.cgm_Meta as cgmMeta

from cgm.core import cgm_General as cgmGeneral
from cgm.core.cgmPy import validateArgs as VALID
from cgm.core.lib import shared_data as SHARED
from cgm.core.lib import search_utils as SEARCH
from cgm.core.lib import math_utils as MATH
from cgm.core.lib import distance_utils as DIST
from cgm.core.lib import position_utils as POS
from cgm.core.lib import euclid as EUCLID
from cgm.core.lib import attribute_utils as ATTR
from cgm.core.lib import name_utils as NAMES
import cgm.core.lib.snap_utils as SNAP
import cgm.core.lib.transform_utils as TRANS
import cgm.core.lib.curve_Utils as CURVES

#!!!! No rigging_utils!!!!!!!!!!!!!!!!!!!!!!!!!

#>>> Utilities
#===================================================================  

def orientChain(joints = None, axisAim = 'z+', axisUp = 'y+',
                worldUpAxis = [0,1,0], relativeOrient = True,
                baseName = None, asMeta = True):
                
    """
    Given a series of positions, or objects, or a curve and a mesh - loft retopology it

    :parameters:
        targets(list) | List of curves to loft
        name(str) | Base name for created objects

    :returns
        created(list)
    """    
    _str_func = 'build_skeleton'
    
    _ml_joints = cgmMeta.validateObjListArg(joints,mayaType=['joint'],noneValid=False)
    _axisAim = axisAim
    _axisUp = axisUp
    _axisWorldUp = worldUpAxis
    _len = len(_ml_joints)
    
    for mJnt in _ml_joints:
        mJnt.parent = False
    if baseName:
        _ml_joints[0].doStore('cgmName',baseName)
        
    #>>Orient chain...
    for i,mJnt in enumerate(_ml_joints[:-1]):
        if i > 0:
            mJnt.parent = _ml_joints[i-1]
            #...after our first object, we use our last object's up axis to be our new up vector.
            #...this keeps joint chains that twist around from flipping. Ideally...
            if relativeOrient:
                _axisWorldUp = MATH.get_obj_vector(_ml_joints[i-1].mNode,'y+')
        
        mDup = mJnt.doDuplicate(parentOnly = True)
        mc.makeIdentity(mDup.mNode, apply = 1, jo = 1)#Freeze

        SNAP.aim(mDup.mNode,_ml_joints[i+1].mNode,_axisAim,_axisUp,'vector',_axisWorldUp)
        if baseName:
            mJnt.doStore('cgmIterator',i)
            mJnt.doName()

        mJnt.rotate = 0,0,0
        mJnt.jointOrient = mDup.rotate
        mDup.delete()

    #>>Last joint....        
    if _len > 1:
        _ml_joints[-1].parent = _ml_joints[-2]
        _ml_joints[-1].jointOrient = 0,0,0    
        if baseName:
            _ml_joints[-1].doStore('cgmIterator',_len-1)
            _ml_joints[-1].doName()   
            
def freezeOrientation(targetJoints):
    """
    Freeze joint orientations in place. 
    """
    _str_funcName = "metaFreezeJointOrientation"		
    #t1 = time.time()

    if type(targetJoints) not in [list,tuple]:targetJoints=[targetJoints]

    ml_targetJoints = cgmMeta.validateObjListArg(targetJoints,'cgmObject')

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
        _relatives = TRANS.children_get(i_jnt.mNode)
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

def build_chain(posList = [],
                targetList = [],
                curve = None,
                axisAim = 'z+',
                axisUp = 'y+',
                worldUpAxis = [0,1,0],
                count = None,
                splitMode = 'curve',
                parent = False,
                orient = True,
                relativeOrient=True,
                asMeta = True):
    """
    General build oriented skeleton from a position list, targets or curve
    
    :parameters:
        posList(list) | List of positions to build from
        targetList(list) | List of targets to build from
        curve(str) | Curve to split 
        worldUpAxis(vector) | World up direction for orientation
        count(int) | number of joints for splitting (None) is default which doesn't resplit
        splitMode(str)
            linear - Resplit along a vector from the first to last posList point
            curve - Resplit along a curve going through all of our points

    :returns
        created(list)
    """
    
    _str_func = 'build_chain'
    _axisAim = axisAim
    _axisUp = axisUp
    _axisWorldUp = worldUpAxis
    _radius = 1    
    mc.select(cl=True)
    pprint.pprint(vars())
    
    #>>Get positions ================================================================================
    if not posList and targetList:
        log.debug("|{0}| >> No posList provided, using targets...".format(_str_func))            
        posList = []
        for t in targetList:
            posList.append(POS.get(t))
            
    if curve and not posList:
        log.debug("|{0}| >> Generating posList from curve arg...".format(_str_func))                    
        splitMode == 'curve'
        posList = CURVES.returnSplitCurveList(curve,count)
        
    if count is not None:
        log.debug("|{0}| >> Resplit...".format(_str_func))    
        if count != len(posList):
            if splitMode == 'linear':
                #_p_start = POS.get(_l_targets[0])
                #_p_top = POS.get(_l_targets[1])    
                #posList = get_posList_fromStartEnd(posList[0],posList[-1],count)
                _crv = CURVES.create_fromList(posList= posList, linear=True)
                posList = CURVES.returnSplitCurveList(_crv,count)
                mc.delete(_crv)                
            elif splitMode == 'curve':
                if not curve:
                    log.debug("|{0}| >> Making curve...".format(_str_func))                        
                    _crv = CURVES.create_fromList(posList= posList)
                    posList = CURVES.returnSplitCurveList(_crv,count)
                    mc.delete(_crv)
                else:
                    posList = CURVES.returnSplitCurveList(curve,count)
                    
            else:
                raise ValueError, "Unknown splitMode: {0}".format(splitMode)
    
    #>>Radius =======================================================================================
    _len = len(posList)
    if _len > 1:    
        _baseDist = DIST.get_distance_between_points(posList[0],posList[1])   
        _radius = _baseDist/4

    #>>Create joints =================================================================================
    ml_joints = []

    log.debug("|{0}| >> pos list...".format(_str_func)) 
    for i,p in enumerate(posList):
        log.debug("|{0}| >> {1}:{2}".format(_str_func,i,p)) 

        mJnt = cgmMeta.cgmObject(mc.joint (p=(p[0],p[1],p[2])))
        mJnt.displayLocalAxis = 1
        mJnt.radius = _radius

        ml_joints.append ( mJnt )
        if not parent:
            mJnt.parent=False
        """if i > 0:
            _mJnt.parent = _ml_joints[i-1]    
        else:
            _mJnt.parent = False"""
        
    #>>Orient chain...
    if orient:
        if _len == 1:
            log.debug("|{0}| >> Only one joint. Can't orient chain".format(_str_func,_axisWorldUp)) 
        else:
            orientChain(ml_joints,axisAim,axisUp,worldUpAxis,relativeOrient)

    if asMeta:
        return ml_joints
    return [mJnt.mNode for mJnt in ml_joints]


