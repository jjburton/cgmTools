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
log.setLevel(logging.INFO)

# From Maya =============================================================
import maya.cmds as mc
from maya import mel
# From Red9 =============================================================

# From cgm ==============================================================
import cgm.core.cgm_Meta as cgmMeta

from cgm.core import cgm_General as cgmGEN
from cgm.core.cgmPy import validateArgs as VALID
from cgm.core.lib import shared_data as SHARED
from cgm.core.lib import search_utils as SEARCH
from cgm.core.lib import math_utils as MATH
from cgm.core.lib import distance_utils as DIST
#reload(DIST)
from cgm.core.lib import position_utils as POS
from cgm.core.lib import euclid as EUCLID
from cgm.core.lib import attribute_utils as ATTR
from cgm.core.lib import name_utils as NAMES
import cgm.core.lib.snap_utils as SNAP
import cgm.core.lib.transform_utils as TRANS
import cgm.core.lib.curve_Utils as CURVES
import cgm.core.lib.list_utils as LISTS
import cgm.core.classes.GuiFactory as cgmUI

#!!!! No rigging_utils!!!!!!!!!!!!!!!!!!!!!!!!!

#>>> Utilities
#===================================================================  
def tweakOrient(joints = None, tweak = [0,0,0]):
    """
    Pythonification fo Michael Comet's function. Full acknoledgement.
    
    """
    ml_joints = cgmMeta.validateObjListArg(joints,mayaType=['joint'],noneValid=False)

    for mJnt in ml_joints:
        _short = mJnt.mNode
        mc.xform(_short, r=True, os=True, ra= tweak)
        
        mc.joint(_short, e=True, zso=True)
        mc.makeIdentity(_short, apply=True)
        """   
       // Now tweak each joint
       for ($i=0; $i < $nJnt; ++$i)
           {
               // Adjust the rotation axis
               xform -r -os -ra $rot[0] $rot[1] $rot[2] $joints[$i] ;
   
               // And now finish clearing out joint axis...
               joint -e -zso $joints[$i] ;
               makeIdentity -apply true $joints[$i] ;    """
        
def orientByPlane(joints = None, axisAim = 'z+', axisUp = 'y+',
                worldUpAxis = [0,1,0], planarMode = 'up', relativeOrient = True,
                progressBar=None,
                baseName = None, cleanUp = True, asMeta = True):
                
    """
    Given a chain of joints, setup 

    :parameters:
        planarMode - up/out - What plane to use
        
    :returns
        created(list)
    """    
    _str_func = 'orientPlane'
    
    ml_joints = cgmMeta.validateObjListArg(joints,mayaType=['joint'],noneValid=False)
    ml_joints = LISTS.get_noDuplicates(ml_joints)
    
    mAxis_aim = VALID.simpleAxis(axisAim)
    mAxis_up = VALID.simpleAxis(axisUp)
    str_aim = mAxis_aim.p_string
    str_up = mAxis_up.p_string
    ml_delete = []
    
    if str_aim == str_up:
        raise ValueError,"axisAim and axisUp cannot be the same"
    if len(ml_joints) < 3:
        raise ValueError,"{0} > Need more than 3 joints".format(_str_func)
    
    #First setup a dup chain of first and end, orient those ----------------------------------------------------------------
    log.debug("|{0}| >> Setup tmp chain...".format(_str_func))                     
    
    mStart = ml_joints[0].doDuplicate(parentOnly = True)
    mEnd = ml_joints[-1].doDuplicate(parentOnly = True)
    mEnd.parent = mStart
    
    orientChain([mStart,mEnd], axisAim, axisUp, worldUpAxis, relativeOrient)

    #Setup Loft curves and plane ----------------------------------------------------------------
    log.debug("|{0}| >> Setup curves...".format(_str_func))                     
    
    if planarMode == 'up':
        crvUp = mAxis_up.p_string
        crvDn = mAxis_up.inverse.p_string
    else:
        for a in 'xyz':
            if a not in str_aim and a not in str_up:
                mAxisCrv_tmp = VALID.simpleAxis(a+'+')
                crvUp = mAxisCrv_tmp.p_string
                crvDn = mAxisCrv_tmp.inverse.p_string
        
    d_distance = DIST.get_distance_between_targets([mStart.mNode,mEnd.mNode])
    
    l_crvs = []
    for mObj in [mStart,mEnd]:
        crv =   mc.curve (d=1, ep = [DIST.get_pos_by_axis_dist(mObj.mNode, crvUp, d_distance),
                                     DIST.get_pos_by_axis_dist(mObj.mNode, crvDn, d_distance)],
                               os=True)
        log.debug("|{0}| >> Created: {1}".format(_str_func,crv))
        l_crvs.append(crv)
        
    _res_body = mc.loft(l_crvs, o = True, d = 1, po = 1 )
    _inputs = mc.listHistory(_res_body[0],pruneDagObjects=True)
    _tessellate = _inputs[0]
    
    _d = {'format':2,#General
          'polygonType':1,#'quads'
          }
          
    for a,v in _d.iteritems():
        ATTR.set(_tessellate,a,v)    
            
    #Snap our joints ---------------------------------------------------------------------------------
    for mJnt in ml_joints[1:-1]:
        ml_children = mJnt.getChildren(asMeta=True)
        for mChild in ml_children:
            mChild.parent = False
            
        SNAP.go(mJnt, _res_body[0], rotation=False, pivot='closestPoint')

        for mChild in ml_children:
            mChild.parent = mJnt
            
    #Cleanup --------------------------------------------------------------------------------------------
    if cleanUp:
        mc.delete(_res_body + l_crvs)
        mStart.delete()
        
    orientChain(ml_joints, axisAim, axisUp, worldUpAxis, relativeOrient,progressBar)

    return

    l_start = []
    l_end = []
    
    mStartCrv = mc.curve()
    mc.curve (d=1, ep = posList, os=True)
    #Snap interior joints to plane ----------------------------------------------------------------
    
@cgmGEN.Timer
def orientChain(joints = None, axisAim = 'z+', axisUp = 'y+',
                worldUpAxis = [0,1,0], relativeOrient = True,
                progressBar = None,axisBackup = 'x+',
                baseName = None, asMeta = True):
                
    """
    Given a series of positions, or objects, or a curve and a mesh - loft retopology it

    :parameters:


    :returns
        created(list)
    """    
    try:
        _str_func = 'orientChain'
        if baseName:raise NotImplementedError,"Remove these calls"
        
        def orientJoint(mJnt):
            try:
                if mJnt not in ml_cull:
                    log.debug("|{0}| >> Aready done: {1}".format(_str_func,mJnt.mNode))                     
                    return 
                
                log.debug("|{0}| >> Orienting: {1}".format(_str_func,mJnt.mNode))
                mParent = _d_parents[mJnt]
                if mParent and mParent in ml_cull:
                    return
                    log.debug("|{0}| >> Orienting parent: {1}".format(_str_func,mParent.mNode))         
                    orientJoint(mParent)
                    
                if mJnt in ml_world:
                    log.debug("|{0}| >> World joint: {1}".format(_str_func,mJnt.mNode))
                    try:
                        axisWorldOrient = SHARED._d_axisToJointOrient[str_aim][str_up]
                    except Exception,err:
                        log.error("{0}>> World axis query. {1} | {2}".format(_str_func, str_aim, str_up))
                        raise Exception,err
                    
                    log.debug("|{0}| >> World joint: {1} | {2}".format(_str_func,mJnt.mNode, axisWorldOrient))
                    mJnt.rotate = 0,0,0
                    mJnt.jointOrient = axisWorldOrient[0],axisWorldOrient[1],axisWorldOrient[2]
                    
                elif mJnt not in ml_ends:
                    log.debug("|{0}| >> Reg joint: {1}".format(_str_func,mJnt.mNode))            
                    mDup = mJnt.doDuplicate(parentOnly = True)
                    mc.makeIdentity(mDup.mNode, apply = 1, jo = 1)#Freeze
                    b_rotFix = False
                    
                    if relativeOrient and mParent:
                        p_child = _d_children[mJnt][0].p_position
                        p_me = mJnt.p_position
                        p_parent = mParent.p_position                                    
                        
                        _axisWorldUp = MATH.get_obj_vector(mParent.mNode, axisUp)
                        _vecToChild = MATH.get_vector_of_two_points(p_child, p_me)
                        _vecToParent = MATH.get_vector_of_two_points(p_me, p_parent)
                        _vecFromParent = MATH.get_vector_of_two_points(p_parent, p_me)
                        
                        _angleVec = MATH.angleBetweenVectors(_axisWorldUp,_vecToChild)
                        #_angle = MATH.angleBetweenVectors(_vecFromParent,_vecToChild)
                        _angle = MATH.angleBetween(p_child,p_me,p_parent)
                        #except:_angle = 0
                        _cross = MATH.dotproduct(_vecToChild,_vecToParent)
                        
                        #pprint.pprint(vars())
                        
                        log.debug(cgmGEN.logString_msg(_str_func,"{0} | vec: {1} | angle: {2} | cross: {3}".format(mJnt.mNode,_angleVec,_angle,_cross)))
                        
                        if _angle > 70:
                            log.warning(cgmGEN.logString_msg(_str_func,"{0} | dangerous angles vec: {1} | angle: {2} ".format(mJnt.mNode,_angleVec,_angle)))
                            #log.info(cgmGEN.logString_msg(_str_func,"dangerous cross: {0} ".format(_cross)))
                            
                            #_axisWorldUp = MATH.get_obj_vector(mParent.mNode, axisBackup)
                            
                            if _cross < 0:
                                _axisWorldUp = [-1*v for v in _vecToParent]
                            else:
                                pass
                                #_axisWorldUp = _vecToParent
                                #_axisWorldUp = _lastVecUp
                            #v = MATH.transform_direction(
            
                            b_rotFix = True
                            """
                            if _angleVec < 1.0:
                                _axisWorldUp = MATH.averageVectors(_axisWorldUp,_vecToChild)
                                _axisWorldUp = MATH.averageVectors(_axisWorldUp,worldUpAxis)#.average in the world value
                                log.warning(cgmGEN.logString_msg(_str_func,"To child | postfix: {0} ".format(_axisWorldUp)))
                                
                            else:
                                _vecToParent = MATH.get_vector_of_two_points(p_me, p_parent)                        
                                _axisWorldUp = MATH.averageVectors(_axisWorldUp,_vecToParent)
                                _axisWorldUp = MATH.averageVectors(_axisWorldUp,worldUpAxis)#.average in the world value
                                log.warning(cgmGEN.logString_msg(_str_func,"To parent | postfix: {0} ".format(_axisWorldUp)))"""
                    else:
                        _axisWorldUp = worldUpAxis
                        
                    mDup.rotateOrder = 0
                    SNAP.aim(mDup.mNode,_d_children[mJnt][0].mNode,
                             mAxis_aim.p_vector,mAxis_up.p_vector,
                             'vector',_axisWorldUp)
                    
                    if b_rotFix:
                        pass
                        """
                        a = 'r{0}'.format(axisAim[0])
                        v = ATTR.get(mDup.mNode,a)                
                        log.warning(cgmGEN.logString_msg(_str_func,"{0} | rotFix | a: {1} | v: {2}".format(mJnt.mNode,a,v)))
            
                        ATTR.set(mDup.mNode,a,90)"""
                        
                    mJnt.rotate = 0,0,0
                    mJnt.jointOrient = mDup.p_orient
                    mDup.delete()
                    
                if mJnt in ml_cull:ml_cull.remove(mJnt)
                return
            except Exception,err:
                cgmGEN.cgmException(Exception,err)
                
        def reparent(progressBar=None):
            log.debug("|{0}| >> reparent...".format(_str_func))
            
            #progressBar = cgmUI.progressBar_start(progressBar, stepMaxValue=_len)
            
            #log.info("|{0}| >> reparent progressBar:{1}".format(_str_func,format(progressBar)))
            for mJnt in ml_joints:
                #log.debug("|{0}| >> reparenting: {1} | {2}".format(_str_func,mJnt.mNode, _d_parents[mJnt]))         
                #cgmUI.progressBar_iter(progressBar,status='Reparenting: {0}'.format(mJnt.mNode))
                
                mJnt.parent = _d_parents[mJnt]
                
                for mChild in _d_children[mJnt]:
                    #if mChild not in ml_joints:
                        #log.debug("|{0}| >> reparenting child: {1}".format(_str_func,mChild.mNode))                             
                    mChild.parent = mJnt
                
                if mJnt in ml_ends and mJnt not in ml_world:
                    log.debug("|{0}| >> End joint. No world: {1}".format(_str_func,mJnt))                                             
                    mJnt.jointOrient = 0,0,0                
                            
        ml_joints = cgmMeta.validateObjListArg(joints,mayaType=['joint'],noneValid=False)
        ml_joints = LISTS.get_noDuplicates(ml_joints)
        
        mAxis_aim = VALID.simpleAxis(axisAim)
        mAxis_up = VALID.simpleAxis(axisUp)
        _axisWorldUp = worldUpAxis
        str_aim = mAxis_aim.p_string
        str_up = mAxis_up.p_string
        
        if str_aim == str_up:
            raise ValueError,"axisAim and axisUp cannot be the same"
        
        _len = len(ml_joints)
        _d_parents = {}
        _d_children = {}
        ml_roots = []
        ml_ends = []
        ml_world =[]
        ml_done = []
        ml_cull = copy.copy(ml_joints)
        
        #First loop is logic check ---------------------------------------------------------
        for mJnt in ml_joints:
            _d_parents[mJnt] = mJnt.getParent(asMeta=True)
            _d_children[mJnt] = mJnt.getChildren(asMeta=True)
            if not _d_parents[mJnt]:
                log.debug("|{0}| >> Root joint: {1}".format(_str_func,mJnt.mNode)) 
                ml_roots.append(mJnt)
                
            if not _d_children[mJnt]:
                log.debug("|{0}| >> End joint: {1}".format(_str_func,mJnt.mNode)) 
                ml_ends.append(mJnt)
                if not _d_parents[mJnt]:
                    log.debug("|{0}| >> World joint: {1}".format(_str_func,mJnt.mNode)) 
                    ml_world.append(mJnt)
        
                    
        for mJnt in ml_joints:
            mJnt.parent = False
            for mChild in _d_children[mJnt]:
                if mChild not in ml_joints:
                    mChild.parent = False            
                
        #pprint.pprint(vars())
        _go = True
        _cnt = 0
        while ml_cull and _go and _cnt <= _len+1:
            _cnt+=1
            #progressBar = cgmUI.progressBar_start(progressBar,stepMaxValue=_len)        
            for mJnt in ml_cull:
                try:            
                    #cgmUI.progressBar_iter(progressBar,status='Orienting: {0}'.format(mJnt.mNode))
                    orientJoint(mJnt)
                except Exception,err:
                    log.error("{0}>> Error fail. Last joint: {1} | {2}".format(_str_func, mJnt.mNode, err))
                    _go = False
                    #cgmUI.progressBar_end(progressBar)
                    reparent()                
                    #return False
                    cgmGEN.cgmException(Exception,err)
                
        reparent(progressBar)
        return
    except Exception,err:
        cgmGEN.cgmException(Exception,err)
        
            
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

        #New method  ----
        log.debug("loc...")
    
        #mi_rootLoc = i_jnt.doLoc(fastMode = True)#Make some locs
        mi_zLoc = i_jnt.doLoc(fastMode = True)#Make some locs
        mi_yLoc = mi_zLoc.doDuplicate()

        log.debug("dup...")
        i_dup = i_jnt.doDuplicate(parentOnly = True)

        i_dup.parent = i_jnt.parent
        i_dup.rotate = 0,0,0
        i_dup.rotateOrder = 0
        i_dup.jointOrient = 0,0,0

        log.debug("group...")
        str_group = TRANS.group_me(i_jnt,False,True) #group for easy move
        
        mi_yLoc.parent = str_group
        mi_zLoc.parent = str_group

        mi_zLoc.tz = 1#Move
        mi_yLoc.ty = 1

        mc.makeIdentity(i_dup.mNode, apply = 1, jo = 1)#Freeze

        #Aim
        log.debug("constrain...")

        str_const = mc.aimConstraint(mi_zLoc.mNode,
                                     i_dup.mNode,
                                     maintainOffset = False,
                                     weight = 1,
                                     aimVector = [0,0,1],
                                     upVector = [0,1,0],
                                     worldUpVector = [0,1,0],
                                     worldUpObject = mi_yLoc.mNode,
                                     worldUpType = 'object' )[0]
        

        
        i_jnt.rotate = [0,0,0] #Move to joint
        i_jnt.jointOrient = i_dup.rotate
        
        #log.info('{0} delete'.format(i))

        log.debug("delete...")	    
        mc.delete([str_const,str_group])#Delete extra stuff str_group
        i_dup.delete()
        
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
                progressBar = None,                
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
            sub - Resplit adding the number of joints between our points

    :returns
        created(list)
    """
    
    _str_func = 'build_chain'
    _axisAim = axisAim
    _axisUp = axisUp
    _axisWorldUp = worldUpAxis
    _radius = 1    
    mc.select(cl=True)
    #pprint.pprint(vars())
    
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
        if splitMode == 'sub':
            l_new = []
            for i,p in enumerate(posList[:-1]):
                #l_new.append(p)
                l_new.extend(DIST.get_posList_fromStartEnd(p,posList[i+1], count +2) [:-1])
            l_new.append(posList[-1])
            posList = l_new        
            
        elif count != len(posList):
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
    
    #progressBar = cgmUI.progressBar_start(progressBar, stepMaxValue=_len)
    
    for i,p in enumerate(posList):
        log.debug("|{0}| >> {1}:{2}".format(_str_func,i,p)) 
        #cgmUI.progressBar_iter(progressBar,status='Creating: {0}'.format(p))

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
    
    #cgmUI.progressBar_end(progressBar)
    #>>Orient chain...
    if orient:
        if _len == 1:
            log.debug("|{0}| >> Only one joint. Can't orient chain".format(_str_func,_axisWorldUp)) 
        else:
            orientChain(ml_joints,axisAim,axisUp,worldUpAxis,relativeOrient)

    if asMeta:
        return ml_joints
    return [mJnt.mNode for mJnt in ml_joints]


