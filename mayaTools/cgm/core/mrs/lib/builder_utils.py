"""
------------------------------------------
builder_utils: cgm.core.mrs.lib
Author: Josh Burton
email: jjburton@cgmonks.com

Website : http://www.cgmonks.com
------------------------------------------

================================================================
"""
import random
import re
import copy
import time
import os
import pprint

# From Red9 =============================================================
from Red9.core import Red9_Meta as r9Meta
from Red9.core import Red9_AnimationUtils as r9Anim

#========================================================================
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
#========================================================================

import maya.cmds as mc

# From cgm ==============================================================
from cgm.core import cgm_General as cgmGEN
from cgm.core import cgm_Meta as cgmMeta
from cgm.core import cgm_PuppetMeta as PUPPETMETA

from cgm.core.lib import curve_Utils as CURVES
from cgm.core.lib import attribute_utils as ATTR
from cgm.core.lib import position_utils as POS
from cgm.core.lib import math_utils as MATH
from cgm.core.lib import distance_utils as DIST
from cgm.core.lib import snap_utils as SNAP
from cgm.core.lib import rigging_utils as RIGGING
from cgm.core.rigger.lib import joint_Utils as JOINTS
from cgm.core.lib import search_utils as SEARCH
from cgm.core.lib import rayCaster as RAYS
from cgm.core.cgmPy import validateArgs as VALID
from cgm.core.cgmPy import path_Utils as PATH
import cgm.core.rig.joint_utils as COREJOINTS
import cgm.core.classes.NodeFactory as NODEFACTORY
import cgm.core.lib.locator_utils as LOC
import cgm.core.mrs.lib.shared_dat as BLOCKSHARE
import cgm.core.tools.lib.snap_calls as SNAPCALLS

for m in BLOCKSHARE,MATH,DIST,RAYS:
    reload(m)

from cgm.core.cgmPy import os_Utils as cgmOS

def gather_rigBlocks():
    mGroup = get_blockGroup()
    
    for mObj in r9Meta.getMetaNodes(mTypes = 'cgmRigBlock'):
        if not mObj.parent:
            mObj.parent = mGroup

def get_blockGroup():
    if not mc.objExists('cgmRigBlocksGroup'):
        mGroup = cgmMeta.cgmObject(name = 'cgmRigBlocksGroup')
    else: 
        mGroup = cgmMeta.validateObjArg('cgmRigBlocksGroup','cgmObject')
    mGroup.setAttrFlags(attrs=['t','r','s'])
        
    return mGroup

def get_scene_blocks():
    """
    """
    _str_func = 'get_scene_blocks'
    
    _l_rigBlocks = r9Meta.getMetaNodes(mTypes = 'cgmRigBlock')
    
    return _l_rigBlocks

def get_block_lib_dict():
    return get_block_lib_dat()[0]

def get_block_lib_dat():
    """
    Data gather for available blocks.

    :parameters:

    :returns
        _d_modules, _d_categories, _l_unbuildable
        _d_modules(dict) - keys to modules
        _d_categories(dict) - categories to list of entries
        _l_unbuildable(list) - list of unbuildable modules
    """
    _str_func = 'get_block_lib_dict'    
    
    _b_debug = log.isEnabledFor(logging.DEBUG)
    
    import cgm.core.mrs.blocks as blocks
    _path = PATH.Path(blocks.__path__[0])
    _l_duplicates = []
    _l_unbuildable = []
    _base = _path.split()[-1]
    _d_files =  {}
    _d_modules = {}
    _d_import = {}
    _d_categories = {}
    
    log.debug("|{0}| >> Checking base: {1} | path: {2}".format(_str_func,_base,_path))   
    _i = 0
    for root, dirs, files in os.walk(_path, True, None):
        # Parse all the files of given path and reload python modules
        _mRoot = PATH.Path(root)
        _split = _mRoot.split()
        _subRoot = _split[-1]
        _splitUp = _split[_split.index(_base):]
        
        log.debug("|{0}| >> On subroot: {1} | path: {2}".format(_str_func,_subRoot,root))   
        log.debug("|{0}| >> On split: {1}".format(_str_func,_splitUp))   
        
        if len(_split) == 1:
            _cat = 'base'
        else:_cat = _split[-1]
        _l_cat = []
        _d_categories[_cat]=_l_cat
        
        for f in files:
            key = False
            
            if f.endswith('.py'):
                    
                if f == '__init__.py':
                    continue
                else:
                    name = f[:-3]    
            else:
                continue
                    
            if _i == 'cat':
                key = '.'.join([_base,name])                            
            else:
                key = '.'.join(_splitUp + [name])    
                if key:
                    log.debug("|{0}| >> ... {1}".format(_str_func,key))                      
                    if name not in _d_modules.keys():
                        _d_files[key] = os.path.join(root,f)
                        _d_import[name] = key
                        _l_cat.append(name)
                        try:
                            module = __import__(key, globals(), locals(), ['*'], -1)
                            reload(module) 
                            _d_modules[name] = module
                            if not is_buildable(module):
                                _l_unbuildable.append(name)
                        except Exception, e:
                            for arg in e.args:
                                log.error(arg)
                            raise RuntimeError,"Stop"  
                                          
                    else:
                        _l_duplicates.append("{0} >> {1} ".format(key, os.path.join(root,f)))
            _i+=1
            
    if _b_debug:
        cgmGEN.log_info_dict(_d_modules,"Modules")        
        cgmGEN.log_info_dict(_d_files,"Files")
        cgmGEN.log_info_dict(_d_import,"Imports")
        cgmGEN.log_info_dict(_d_categories,"Categories")
    
    if _l_duplicates:
        log.info(cgmGEN._str_subLine)
        log.info("|{0}| >> DUPLICATE MODULES....".format(_str_func))
        for m in _l_duplicates:
            print(m)
        raise Exception,"Must resolve"
    log.debug("|{0}| >> Found {1} modules under: {2}".format(_str_func,len(_d_files.keys()),_path))     
    if _l_unbuildable:
        log.info(cgmGEN._str_subLine)
        log.error("|{0}| >> ({1}) Unbuildable modules....".format(_str_func,len(_l_unbuildable)))
        for m in _l_unbuildable:
            print(">>>    " + m) 
    return _d_modules, _d_categories, _l_unbuildable

def get_posList_fromStartEnd(start=[0,0,0],end=[0,1,0],split = 1):
    _str_func = 'get_posList_fromStartEnd'
    _base = 'joint_base_placer'
    _top = 'joint_top_placer'  

    #>>Get positions ==================================================================================    
    _l_pos = []

    if split == 1:
        _l_pos = [DIST.get_average_position([start,end])]
    elif split == 2:
        _l_pos = [start,end]
    else:
        _vec = MATH.get_vector_of_two_points(start, end)
        _max = DIST.get_distance_between_points(start,end)

        log.debug("|{0}| >> start: {1} | end: {2} | vector: {3}".format(_str_func,start,end,_vec))   

        _split = _max/(split-1)
        for i in range(split-1):
            _p = DIST.get_pos_by_vec_dist(start, _vec, _split * i)
            _l_pos.append( _p)
        _l_pos.append(end)
        _radius = _split/4    
    return _l_pos


def build_skeleton(positionList = [], joints = 1, axisAim = 'z+', axisUp = 'y+', worldUpAxis = [0,1,0],asMeta = True):
    _str_func = 'build_skeleton'
    _axisAim = axisAim
    _axisUp = axisUp
    _axisWorldUp = worldUpAxis
    _l_pos = positionList
    _radius = 1    
    mc.select(cl=True)
    pprint.pprint(vars())
    
    #>>Get positions ================================================================================
    _len = len(_l_pos)
    if _len > 1:    
        _baseDist = DIST.get_distance_between_points(_l_pos[0],_l_pos[1])   
        _radius = _baseDist/4

    #>>Create joints =================================================================================
    _ml_joints = []

    log.debug("|{0}| >> pos list...".format(_str_func)) 
    for i,p in enumerate(_l_pos):
        log.debug("|{0}| >> {1}:{2}".format(_str_func,i,p)) 

        _mJnt = cgmMeta.cgmObject(mc.joint (p=(p[0],p[1],p[2])))
        _mJnt.displayLocalAxis = 1
        _mJnt.radius = _radius

        _ml_joints.append ( _mJnt )
        """if i > 0:
            _mJnt.parent = _ml_joints[i-1]    
        else:
            _mJnt.parent = False"""

    #>>Orient chain...
    if _len == 1:
        log.debug("|{0}| >> Only one joint. Can't orient chain".format(_str_func,_axisWorldUp)) 
    else:
        COREJOINTS.orientChain(_ml_joints,axisAim,axisUp,worldUpAxis)
    """
    for i,mJnt in enumerate(_ml_joints[:-1]):
        if i > 0:
            mJnt.parent = _ml_joints[i-1]
            #...after our first object, we use our last object's up axis to be our new up vector.
            #...this keeps joint chains that twist around from flipping. Ideally...
            _axisWorldUp = MATH.get_obj_vector(_ml_joints[i-1].mNode,_axisUp)
            log.debug("|{0}| >> {1} worldUp: {2}".format(_str_func,i,_axisWorldUp)) 
        mDup = mJnt.doDuplicate(parentOnly = True)
        mc.makeIdentity(mDup.mNode, apply = 1, jo = 1)#Freeze

        SNAP.aim(mDup.mNode,_ml_joints[i+1].mNode,_axisAim,_axisUp,'vector',_axisWorldUp)


        #_rot = mJnt.rotate
        mJnt.rotate = 0,0,0
        mJnt.jointOrient = mDup.rotate
        #mJnt.rotate = 0,0,0
        mDup.delete()

    #>>Last joint....        
    if _len > 1:
        _ml_joints[-1].parent = _ml_joints[-2]
        _ml_joints[-1].jointOrient = 0,0,0
    #_ml_joints[-1].rotate = _ml_joints[-2].rotate
    #_ml_joints[-1].rotateAxis = _ml_joints[-2].rotateAxis
    """
    #JOINTS.metaFreezeJointOrientation(_ml_joints)
    if asMeta:
        return _ml_joints
    return [mJnt.mNode for mJnt in _ml_joints]

    #>>Wiring and naming =================================================================================
    """
    ml_handles = []
    ml_handleJoints = []
    for i_obj in mi_go._ml_controlObjects:
        if i_obj.hasAttr('handleJoint'):
            #d_buffer = i_obj.handleJoint.d_jointFlags
            #d_buffer['isHandle'] = True
            #i_obj.handleJoint.d_jointFlags = d_buffer
            ml_handleJoints.append(i_obj.handleJoint)

    mi_go._mi_rigNull.msgList_connect(ml_handleJoints,'handleJoints','rigNull')
    mi_go._mi_rigNull.msgList_connect(ml_moduleJoints,'skinJoints')     
    """

    _ml_joints[0].addAttr('cgmName','box')

    for i,mJnt in enumerate(_ml_joints):
        mJnt.addAttr('cgmIterator',i)
        mJnt.doName()


    #>>HelperJoint setup???

 
def build_loftMesh(root, jointCount = 3, degree = 3, cap = True, merge = True):
    """
    Core rig block factory. Runs processes for rig blocks.

    :parameters:
        root(str) | root object to check for wiring

    :returns
        factory instance
    """
    _str_func = 'build_loftMesh'
    
    _l_targets = ATTR.msgList_get(root,'loftTargets')
    
    
    mc.select(cl=True)
    log.debug("|{0}| >> loftTargets: {1}".format(_str_func,_l_targets))
    
    #tess method - general, uType 1, vType 2+ joint count
    
    #>>Body -----------------------------------------------------------------
    _res_body = mc.loft(_l_targets, o = True, d = degree, po = 1 )

    _inputs = mc.listHistory(_res_body[0],pruneDagObjects=True)
    _tessellate = _inputs[0]
    
    _d = {'format':2,#General
          'polygonType':1,#'quads',
          'uNumber': 1 + jointCount}
    for a,v in _d.iteritems():
        ATTR.set(_tessellate,a,v)

    
    #>>Top/Bottom bottom -----------------------------------------------------------------
    if cap:
        _l_combine = [_res_body[0]]        
        for crv in _l_targets[0],_l_targets[-1]:
            _res = mc.planarSrf(crv,po=1)
            _inputs = mc.listHistory(_res[0],pruneDagObjects=True)
            _tessellate = _inputs[0]        
            _d = {'format':2,#General
                  'polygonType':1,#'quads',
                  'vNumber':1,
                  'uNumber':1}
            for a,v in _d.iteritems():
                ATTR.set(_tessellate,a,v)
            _l_combine.append(_res[0])
            
        _res = mc.polyUnite(_l_combine,ch=False,mergeUVSets=1,n = "{0}_proxy_geo".format(root))
        if merge:
            mc.polyMergeVertex(_res[0], d= .01, ch = 0, am = 1 )
            #polyMergeVertex  -d 0.01 -am 1 -ch 1 box_3_proxy_geo;
        mc.polySetToFaceNormal(_res[0],setUserNormal = True) 
    else:
        _res = _res_body
    return _res[0]

def build_jointProxyMeshOLD(root,degree = 3, jointUp = 'y+'):
    _str_func = 'build_jointProxyMesh'
    
    _l_targets = ATTR.msgList_get(root,'loftTargets')
    #_l_joints = [u'box_0_jnt', u'box_1_jnt', u'box_2_jnt', u'box_3_jnt', u'box_4_jnt']
    
    _mi_root = cgmMeta.cgmObject(root)
    _mi_module = _mi_root.moduleTarget
    _mi_rigNull = _mi_module.rigNull
    
    _l_joints = _mi_rigNull.msgList_get('skinJoints',asMeta = False)
    _castMesh = 'box_root_crv_grp_box_root_crv_proxy_geo'
    _name = ATTR.get(root,'blockType')
    
    #>>Make a nurbs body -----------------------------------------------------------------
    _res_body = mc.loft(_l_targets, o = True, d = degree, po = 0 )
    
    #>>Cast intersections to get v values -----------------------------------------------------------------
    #...get our initial range for casting
    #_l_dist = DIST.get_distance_between_points([POS.get(j) for j in _l_joints])
    #log.debug("|{0}| >> average dist: {1}".format(_str_func,_average))   
    
    _l_newCurves = []
    for j in _l_joints:
        _d = RAYS.cast(_res_body[0],j,jointUp)
        log.debug("|{0}| >> Casting {1} ...".format(_str_func,j))
        #cgmGEN.log_info_dict(_d,j)
        _v = _d['uvs'][_res_body[0]][0][0]
        log.debug("|{0}| >> v: {1} ...".format(_str_func,_v))
        
        #>>For each v value, make a new curve -----------------------------------------------------------------        
        #duplicateCurve -ch 1 -rn 0 -local 0  "loftedSurface2.u[0.724977270271534]"
        _crv = mc.duplicateCurve("{0}.u[{1}]".format(_res_body[0],_v), ch = 0, rn = 0, local = 0)
        log.debug("|{0}| >> created: {1} ...".format(_str_func,_crv))        
        _l_newCurves.append(_crv[0])
    
    
    #>>Reloft those sets of curves and cap them -----------------------------------------------------------------
    log.debug("|{0}| >> Create new mesh objs. Curves: {1} ...".format(_str_func,_l_newCurves))        
    _l_new = []
    for i,c in enumerate(_l_newCurves[:-1]):
        _pair = [c,_l_newCurves[i+1]]
        _mesh = create_loftMesh(_pair, name="{0}_{1}".format(_name,i))
        RIGGING.match_transform(_mesh,_l_joints[i])
        _l_new.append(_mesh)
    
    #...clean up 
    mc.delete(_l_newCurves + _res_body)
    #>>Parent to the joints ----------------------------------------------------------------- 
    return _l_new

def create_loftMesh(targets = None, name = 'test', degree = 3, divisions = 1, cap = True, merge = True ):
    """
    Create lofted mesh from target curves.

    :parameters:
        targets(list) | List of curves to loft
        name(str) | Base name for created objects
        degree(int) | degree of surface
        divisions(int) | how many splits in the created mesh
        cap(bool) | whether to cap the top and bottom
        merge(bool) | whether to merge the caps to the base mesh

    :returns
        created(list)
    """    
    _str_func = 'create_loftMesh'
    
    if targets == None:
        targets = mc.ls(sl=True)
    if not targets:
        raise ValueError, "|{0}| >> Failed to get attr dict".format(_str_func,blockType)
    
    mc.select(cl=True)
    log.debug("|{0}| >> targets: {1}".format(_str_func,targets))
    
    #tess method - general, uType 1, vType 2+ joint count
    
    #>>Body -----------------------------------------------------------------
    _res_body = mc.loft(targets, o = True, d = degree, po = 1 )
    mTarget1 = cgmMeta.cgmObject(targets[0])
    l_cvs = mc.ls("{0}.cv[*]".format(mTarget1.getShapes()[0]),flatten=True)
    points = len(l_cvs)
    

    _inputs = mc.listHistory(_res_body[0],pruneDagObjects=True)
    _tessellate = _inputs[0]
    
    _d = {'format':1,#Fit
          'polygonType':1,#'quads',
          'vNumber':points,
          'uNumber': 1 + divisions}
    for a,v in _d.iteritems():
        ATTR.set(_tessellate,a,v)
        
    #mc.polySoftEdge(_res_body[0], a = 30, ch = 1)
        
    #mc.polySetToFaceNormal(_res_body[0],setUserNormal = True)
    
    if merge:
        #Get our merge distance
        l_cvPoints = []
        for p in l_cvs:
            l_cvPoints.append(POS.get(p))
        l_dist = []    
        for i,p in enumerate(l_cvPoints[:-1]):
            l_dist.append(DIST.get_distance_between_points(p,l_cvPoints[i+1]))
    
        f_mergeDist = (sum(l_dist)/ float(len(l_dist))) * .001        
        
        mc.polyMergeVertex(_res_body[0], d= f_mergeDist, ch = 0, am = 1 )    
        
    if cap:
        mc.polyCloseBorder(_res_body[0] )
        """
        _l_combine = [_res_body[0]]
        
        #>>Top bottom -----------------------------------------------------------------
        for i,crv in enumerate([targets[0],targets[-1]]):
            _res = mc.planarSrf(crv,po=1,ch=True,d=3,ko=0, tol=.01,rn=0)
            log.info(_res)
            _inputs = mc.listHistory(_res[0],pruneDagObjects=True)
            _tessellate = _inputs[0]        
            _d = {'format':1,#Fit
                  'polygonType':1,#'quads',
                  #'vNumber':1,
                  #'uNumber':1
                  }
            for a,v in _d.iteritems():
                ATTR.set(_tessellate,a,v)
            _l_combine.append(_res[0])
        
        #_res = mc.polyUnite(_l_combine,ch=False,mergeUVSets=1,n = "{0}_proxy_geo".format(name))
        """
        
        if merge:
            mc.polyMergeVertex(_res_body[0], d= f_mergeDist, ch = 0, am = 1 )
            #polyMergeVertex  -d 0.01 -am 1 -ch 1 box_3_proxy_geo;
        _res = _res_body
    else:
        _res = _res_body
    
    return _res[0]    

def create_remesh(mesh = None, joints = None, curve=None, positions = None,
                  name = 'test', vector = None, 
                  degree = 3, divisions = 1, cap = True, merge = True ):
    """
    Given a series of positions, or objects, or a curve and a mesh - loft retopology it

    :parameters:
        targets(list) | List of curves to loft
        name(str) | Base name for created objects
        degree(int) | degree of surface
        divisions(int) | how many splits in the created mesh
        cap(bool) | whether to cap the top and bottom
        merge(bool) | whether to merge the caps to the base mesh

    :returns
        created(list)
    """    
    _str_func = 'create_remesh'
    _l_pos = False
    
    #Validate
    if positions:
        _len_passed = len(positions)
        log.debug("|{0}| >> Positions passed... len:{1} | {2}".format(_str_func,_len_passed,positions))        
        _mode = 'positions'
        
        if _len_passed > divisions:
            log.warning("|{0}| >> More positions passed than divisions... positions:{1} | divisions:{2}".format(_str_func,_len_passed,divisions))                    
            return False
        else:
            log.debug("|{0}| >> Splitting Positions")
            _p_start = POS.get(_l_targets[0])
            _p_top = POS.get(_l_targets[1])    
            _l_pos = get_posList_fromStartEnd(_p_start,_p_top,_joints)          
        
        
    else:
        if joints:
            log.debug("|{0}| >> joints passed... len:{1} | {2}".format(_str_func,len(joints),joints))                    
            _mode = 'joint'
            _objs = joints
        elif curve:
            log.debug("|{0}| >> curve passed... len:{1} | {2}".format(_str_func,len(curve),curve))                                
            _mode = 'curve'
        
    #>>Get our positions
    if not _l_pos:
        log.warning("|{0}| >> Must have _l_pos by now.".format(_str_func))                    
        return False       
    
    #>If we have a curve, split it
    #>If we have a series of joints, get pos
    
    #>>Get our vectors
    _vec = [0,1,0]
    
    
    #>>Cast our Loft curves
    
def build_visSub(self):
    _start = time.clock()    
    _str_func = 'build_visSub'
        
    mSettings = self.mRigNull.settings
    if not mSettings:
        raise ValueError,"Not settings found"
    mMasterControl = self.d_module['mMasterControl']

    #Add our attrs
    mPlug_moduleSubDriver = cgmMeta.cgmAttr(mSettings,'visSub', value = True, attrType='bool', defaultValue = False,keyable = False,hidden = False)
    #mPlug_moduleSubDriver = cgmMeta.cgmAttr(mSettings,'visSub', value = 1, defaultValue = 1, attrType = 'int', minValue=0,maxValue=1,keyable = False,hidden = False)
    mPlug_result_moduleSubDriver = cgmMeta.cgmAttr(mSettings,'visSub_out', defaultValue = 1, attrType = 'int', keyable = False,hidden = True,lock=True)

    #Get one of the drivers
    if self.mModule.getAttr('cgmDirection') and self.mModule.cgmDirection.lower() in ['left','right']:
        str_mainSubDriver = "%s.%sSubControls_out"%(mMasterControl.controlVis.getShortName(),
                                                    self.mModule.cgmDirection)
    else:
        str_mainSubDriver = "%s.subControls_out"%(mMasterControl.controlVis.getShortName())

    iVis = mMasterControl.controlVis
    visArg = [{'result':[mPlug_result_moduleSubDriver.obj.mNode,mPlug_result_moduleSubDriver.attr],
               'drivers':[[iVis,"subControls_out"],[mSettings,mPlug_moduleSubDriver.attr]]}]
    NODEFACTORY.build_mdNetwork(visArg)
    
    log.debug("|{0}| >> Time >> = {1} seconds".format(_str_func, "%0.3f"%(time.clock()-_start))) 
    
    return mPlug_result_moduleSubDriver

def register_mirrorIndices(self, ml_controls = []):
    _start = time.clock()    
    _str_func = 'register_mirrorIndices'
    
    mPuppet = self.mPuppet
    direction = self.d_module['mirrorDirection']
    
    int_strt = mPuppet.atUtils( 'mirror_getNextIndex', direction )
    ml_extraControls = []
    for i,mCtrl in enumerate(ml_controls):
        try:
            for str_a in BLOCKSHARE.__l_moduleControlMsgListHooks__:
                buffer = mCtrl.msgList_get(str_a)
                if buffer:
                    ml_extraControls.extend(buffer)
                    log.info("Extra controls : {0}".format(buffer))
        except Exception,error:
            log.error("mCtrl failed to search for msgList : {0}".format(mCtrl))
            log.error(error)
            log.error(cgmGEN._str_subLine)
    
    ml_controls.extend(ml_extraControls)
    
    for i,mCtrl in enumerate(ml_controls):
        mCtrl.addAttr('mirrorIndex', value = (int_strt + i))

    log.debug("|{0}| >> Time >> = {1} seconds".format(_str_func, "%0.3f"%(time.clock()-_start))) 
    
    return ml_controls

@cgmGEN.Timer
def shapes_fromCast(self, targets = None, mode = 'default', aimVector = None, upVector = None, uValues = [], offset = None, size = None):
    """
    :parameters:
        self(RigBlocks.rigFactory)
        targets(list) - targets for most modes. If none provided. Looks for prerig handles
        mode - 
            default
            segmentHandle
            ikHandle
        upVector - If none provided, uses from rigFactory 
        uValues - percent based values to generate curves on nurbs loft
        offset(float) - If none, uses internal data to guess
        size(float) - Used for various modes. Most will guess if none provided
    :returns:
        
    :raises:
        Exception | if reached

    """
    try:
        _short = self.mBlock.mNode
        _str_func = 'shapes_build ( {0} )'.format(_short)
        
        if aimVector is None:
            str_aim = self.d_orientation['str'][1] + '-'
        else:
            str_aim = VALID.simpleAxis(aimVector).p_string
            
        
        mRigNull = self.mRigNull
        ml_shapes = []
        mMesh_tmp = None
        mRebuildNode = None
        _rebuildState = None
        
        if upVector is None:
            upVector = self.d_orientation['vectorUp']
        if aimVector is None:
            aimVector = self.d_orientation['vectorAim']
                
        #Get our prerig handles if none provided
        if targets is None:
            ml_targets = self.mBlock.msgList_get('prerigHandles',asMeta = True)
            if not ml_targets:
                raise ValueError,"No prerigHandles connected. NO targets offered"
        else:
            ml_targets = cgmMeta.validateObjListArg(targets,'cgmObject')
        
        if offset is None:
            offset = self.mPuppet.atUtils('get_shapeOffset')
            #offset = self.d_module.get('f_shapeOffset',1.0)
            
        if mode in ['default','segmentHandle','ikHandle','frameHandle','loftHandle','limbHandle','limbSegmentHandle']:
            #Get our cast mesh        
            
            ml_handles = self.mBlock.msgList_get('prerigHandles',asMeta = True)

            mMesh_tmp =  self.mBlock.atUtils('get_castMesh')
            str_meshShape = mMesh_tmp.getShapes()[0]
            
            minU = ATTR.get(str_meshShape,'minValueU')
            maxU = ATTR.get(str_meshShape,'maxValueU')
            
            l_failSafes = MATH.get_splitValueList(minU,maxU,
                                                  len(ml_targets))
    
            if mode == 'default':
                log.debug("|{0}| >> Default cast...".format(_str_func))                        
                _average = DIST.get_distance_between_targets([mObj.mNode for mObj in ml_targets],average=True)/4
                
                
                for i,mTar in enumerate(ml_targets):
                    log.debug("|{0}| >> Casting {1} ...".format(_str_func,_short))                
                    _d = RAYS.cast(str_meshShape, mTar.mNode, axis = str_aim)
                    
                    if mTar == ml_targets[-1]:
                        _normal = MATH.get_vector_of_two_points(ml_targets[-2].p_position, ml_targets[-1].p_position)
                    else:
                        _normal = MATH.get_vector_of_two_points(mTar.p_position, ml_targets[i+1].p_position)
                    
                    if not _d:
                        log.debug("|{0}| >> Using failsafe value for: {1}".format(_str_func,mTar))            
                        v = l_failSafes[i]
                    else:
                        v = _d['uvsRaw'][str_meshShape][0][0]
                    
                    
                            
                    #cgmGEN.log_info_dict(_d,j)
                    log.info("|{0}| >> v: {1} ...".format(_str_func,v))
                
                    #>>For each v value, make a new curve -----------------------------------------------------------------        
                    baseCrv = mc.duplicateCurve("{0}.u[{1}]".format(str_meshShape,v), ch = 0, rn = 0, local = 0)[0]
                    DIST.offsetShape_byVector(baseCrv,offset)
                    #offsetCrv = mc.offsetCurve(baseCrv, distance = -offset, ch=False, normal = _normal )[0]
                    #log.debug("|{0}| >> created: {1} ...".format(_str_func,offsetCrv))
                    #mc.delete(baseCrv)
                    #mTrans = mTar.doCreateAt()
                    #RIGGING.shapeParent_in_place(mTrans.mNode, crv, False)
                    ml_shapes.append(cgmMeta.validateObjArg(baseCrv))
                    
            elif mode in ['segmentHandle','ikHandle','frameHandle','limbHandle','limbSegmentHandle']:
                f_factor = (maxU-minU)/(30)
    
                if mode == 'segmentHandleBAK':
                    log.debug("|{0}| >> segmentHandle cast...".format(_str_func))                        
                    
                    if not uValues: raise ValueError,"Must have uValues with segmentHandle mode"
                    
                    l_vectors = []
                    for i,mObj in enumerate(ml_targets[:-1]):
                        l_vectors.append(  MATH.get_vector_of_two_points(mObj.p_position, ml_targets[i+1].p_position) )
                    l_vectors.append(  MATH.get_vector_of_two_points(ml_targets[-2].p_position, ml_targets[-1].p_position) )
                    
                    for i,u in enumerate(uValues):
                        uValue = MATH.Lerp(minU,maxU,u)
                        if u < minU or u > maxU:
                            raise ValueError, "uValue not in range. {0}. min: {1} | max: {2}".format(uValue,minU,maxU)
                        
                        l_mainCurves = []
                        for ii,v in enumerate([uValue+f_factor, uValue, uValue-f_factor]):
                            baseCrv = mc.duplicateCurve("{0}.u[{1}]".format(str_meshShape,v), ch = 0, rn = 0, local = 0)
                            mc.rebuildCurve(baseCrv, replaceOriginal = True, rt = 1, spans = 12, kr = 2)
                            
                            
                            if ii == 1:
                                offsetCrv = mc.offsetCurve(baseCrv, distance = -offset, normal = l_vectors[i], ch=False )[0]                        
                            else:
                                offsetCrv = mc.offsetCurve(baseCrv, distance = -(offset * .9), normal = l_vectors[i], ch=False )[0]
                            
                            l_mainCurves.append(offsetCrv)
                            mc.delete(baseCrv)
                        
                        l_crvPos = []
                        points = 7
                        d_crvPos = {}
                        for crv in l_mainCurves:
                            mCrv = cgmMeta.cgmObject(crv,'cgmObject')
                            mShape = mCrv.getShapes(asMeta=True)[0]
                            
                            minU_shape = mShape.minValue
                            maxU_shape = mShape.maxValue# - 1# not sure on this
                            l_v = MATH.get_splitValueList(minU_shape,maxU_shape, points)
                            #pprint.pprint(l_v)
                            log.debug("|{0}| >> crv {1} splitList {2} ...".format(_str_func,crv,l_v))
                            for ii,v in enumerate(l_v):
                                if not d_crvPos.get(ii):
                                    d_crvPos[ii] = []
                                #print "{0}.u[{1}]".format(mCrv.mNode, v)
                                pos = POS.get("{0}.u[{1}]".format(mCrv.mNode, v))
                                #if pos not in d_crvPos[i]:
                                d_crvPos[ii].append( pos )
        
                                
                        for ii in range(points):
                            crv_connect = CURVES.create_fromList(posList=d_crvPos[ii])
                            l_mainCurves.append(crv_connect)
                            
                        for crv in l_mainCurves[1:]:
                            RIGGING.shapeParent_in_place(l_mainCurves[0], crv, False)
                            
                        ml_shapes.append(cgmMeta.validateObjArg(l_mainCurves[0]))
                            
                ##mc.delete(str_tmpMesh)
                elif mode == 'ikHandle':
                    if not mRigNull.msgList_get('ikJoints'):
                        return log.error("|{0}| >> No ik joints found".format(_str_func))
        
                    ml_ikJoints = mRigNull.msgList_get('ikJoints',asMeta=True)
                    if len(ml_ikJoints)<2:
                        return log.error("|{0}| >> Need at least two ik joints".format(_str_func))
                    
                    str_aim = self.d_orientation['str'][1] + '-'
                    vec_normal = MATH.get_vector_of_two_points(ml_ikJoints[-2].p_position,
                                                               ml_ikJoints[-1].p_position)
                    l_mainCurves = []
                    for mJnt in ml_ikJoints[-2:]:
                        #...Make our curve
                        _short = mJnt.mNode
                        _d = RAYS.cast(str_meshShape, _short, str_aim)
                        
                        log.debug("|{0}| >> Casting {1} ...".format(_str_func,_short))
                        #cgmGEN.log_info_dict(_d,j)
                        _v = _d['uvsRaw'][str_meshShape][0][0]                
                        log.debug("|{0}| >> v: {1} ...".format(_str_func,_v))
                
                        #>>For each v value, make a new curve -----------------------------------------------------------------        
                        #duplicateCurve -ch 1 -rn 0 -local 0  "loftedSurface2.u[0.724977270271534]"
                        baseCrv = mc.duplicateCurve("{0}.u[{1}]".format(str_meshShape,_v), ch = 0, rn = 0, local = 0)[0]
                        DIST.offsetShape_byVector(baseCrv,offset,component='cv')
                        #offsetCrv = mc.offsetCurve(baseCrv, distance = -(offset * .9),
                        ##                           normal = vec_normal,
                        #                           ch=False )[0]
                        l_mainCurves.append(baseCrv)
                        #mc.delete(baseCrv)                        
                        log.debug("|{0}| >> created: {1} ...".format(_str_func,baseCrv))
                    
                    log.debug("|{0}| >> Making connectors".format(_str_func))
                    d_epPos = {}
                    for i,crv in enumerate(l_mainCurves):
                        mCrv = cgmMeta.cgmObject(crv,'cgmObject')
                        for ii,ep in enumerate(mCrv.getComponents('ep',True)):
                            if not d_epPos.get(ii):
                                d_epPos[ii] = []
                                
                            _l = d_epPos[ii]
                            _l.append(POS.get(ep))
                            
                    for k,points in d_epPos.iteritems():
                        crv_connect = CURVES.create_fromList(posList=points)
                        l_mainCurves.append(crv_connect)
                        
                    for crv in l_mainCurves[1:]:
                        RIGGING.shapeParent_in_place(l_mainCurves[0], crv, False)
                        
                    ml_shapes.append(cgmMeta.validateObjArg(l_mainCurves[0]))
                    
                    #ml_shapes = mc.loft(l_loftShapes, o = True, d = 3, po = 0,ch=False)
                    #mc.delete(l_loftShapes)
                    
                elif mode == 'frameHandle':#================================================================
                    if not mRigNull.msgList_get('fkJoints'):
                        return log.error("|{0}| >> No fk joints found".format(_str_func))
                    
                    if targets:
                        ml_fkJoints = ml_targets
                    else:
                        ml_fkJoints = mRigNull.msgList_get('fkJoints',asMeta=True)
                    if len(ml_fkJoints)<2:
                        return log.error("|{0}| >> Need at least two ik joints".format(_str_func))                
                    
                    #...Get our vectors...
                    l_vectors = []
                    for i,mObj in enumerate(ml_fkJoints[:-1]):
                        l_vectors.append(  MATH.get_vector_of_two_points(mObj.p_position, ml_fkJoints[i+1].p_position) )
                    l_vectors.append(  MATH.get_vector_of_two_points(ml_fkJoints[-2].p_position, ml_fkJoints[-1].p_position) )
                    l_vectors.append( l_vectors[-1])#...add it again
                    
                    
                    l_failSafes = MATH.get_splitValueList(minU,maxU,
                                                          len(ml_fkJoints))                    
                    
                    #...Get our uValues...
                    l_uValues = []
                    for i,mObj in enumerate(ml_fkJoints):
                        _short = mObj.mNode
                        _d = RAYS.cast(str_meshShape, _short, str_aim)
                        log.debug("|{0}| >> Casting {1} ...".format(_str_func,_short))
                        #cgmGEN.log_info_dict(_d,j)
                        try:_v = _d['uvsRaw'][str_meshShape][0][0]                                    
                        except:
                            log.debug("|{0}| >> frameHandle. Hit fail {1} | {2}".format(_str_func,i,l_failSafes[i]))                                            
                            _v = l_failSafes[i]
                        l_uValues.append( _v )
                        
                    #l_uValues.append( l_uValues[-1] + (maxU - l_uValues[-1])/2 )
                    l_uValues.append(maxU)
                
                    ml_shapes = []
                    _add = f_factor
                    
                    for i,v in enumerate(l_uValues[:-1]):
                        l_mainCurves = []
                        log.debug("|{0}| >> {1} | {2} ...".format(_str_func,i,v))
                        
                        if v == l_uValues[-2]:
                            log.debug("|{0}| >> {1} | Last one...".format(_str_func,i))
                            _add = 0

                        baseCrv = mc.duplicateCurve("{0}.u[{1}]".format(str_meshShape,v+_add), ch = 0, rn = 0, local = 0)[0]
                        DIST.offsetShape_byVector(baseCrv,offset,component='cv')
                        l_mainCurves.append(baseCrv)
                        
                        endCrv = mc.duplicateCurve("{0}.u[{1}]".format(str_meshShape,l_uValues[i+1]-_add), ch = 0, rn = 0, local = 0)[0]
                        DIST.offsetShape_byVector(endCrv,offset,component='cv')
                        
                        l_mainCurves.append(endCrv)
                        
                        
                        log.debug("|{0}| >> {1} | Making connectors".format(_str_func,i))
                        d_epPos = {}
                        for i,crv in enumerate(l_mainCurves):
                            mCrv = cgmMeta.cgmObject(crv,'cgmObject')
                            for ii,ep in enumerate(mCrv.getComponents('ep',True)):
                                if not d_epPos.get(ii):
                                    d_epPos[ii] = []
                                    
                                _l = d_epPos[ii]
                                _l.append(POS.get(ep))
                                
                        for k,points in d_epPos.iteritems():
                            crv_connect = CURVES.create_fromList(posList=points)
                            l_mainCurves.append(crv_connect)
                            
                        for crv in l_mainCurves[1:]:
                            RIGGING.shapeParent_in_place(l_mainCurves[0], crv, False)
                            
                        ml_shapes.append(cgmMeta.validateObjArg(l_mainCurves[0]))                    
                                        
                elif mode == 'limbHandle':#================================================================
                    if targets:
                        ml_fkJoints = ml_targets
                    else:
                        ml_fkJoints = mRigNull.msgList_get('fkJoints',asMeta=True)
                    if len(ml_fkJoints)<2:
                        return log.error("|{0}| >> Need at least two ik joints".format(_str_func))                
                    
                    #...Get our vectors...
                    l_vectors = []
                    for i,mObj in enumerate(ml_fkJoints[:-1]):
                        l_vectors.append(  MATH.get_vector_of_two_points(mObj.p_position, ml_fkJoints[i+1].p_position) )
                    l_vectors.append(  MATH.get_vector_of_two_points(ml_fkJoints[-2].p_position, ml_fkJoints[-1].p_position) )
                    l_vectors.append( l_vectors[-1])#...add it again
                    
                    
                    l_failSafes = MATH.get_splitValueList(minU,maxU,
                                                          len(ml_fkJoints))                    
                    
                    #...Get our uValues...
                    l_uValues = []
                    for i,mObj in enumerate(ml_fkJoints):
                        _short = mObj.mNode
                        _d = RAYS.cast(str_meshShape, _short, str_aim)
                        log.debug("|{0}| >> Casting {1} ...".format(_str_func,_short))
                        #cgmGEN.log_info_dict(_d,j)
                        try:_v = _d['uvsRaw'][str_meshShape][0][0]                                    
                        except:
                            log.debug("|{0}| >> frameHandle. Hit fail {1} | {2}".format(_str_func,i,l_failSafes[i]))                                            
                            _v = l_failSafes[i]
                        l_uValues.append( _v )
                        
                    #l_uValues.append( l_uValues[-1] + (maxU - l_uValues[-1])/2 )
                    l_uValues.append(maxU)
                
                    ml_shapes = []
                    _add = f_factor
                    
                    for i,v in enumerate(l_uValues[:-1]):
                        l_mainCurves = []
                        log.debug("|{0}| >> {1} | {2} ...".format(_str_func,i,v))
                        
                        if v == l_uValues[-2]:
                            log.debug("|{0}| >> {1} | Last one...".format(_str_func,i))
                            _add = - _add

                        baseCrv = mc.duplicateCurve("{0}.u[{1}]".format(str_meshShape,v+_add), ch = 0, rn = 0, local = 0)[0]
                        DIST.offsetShape_byVector(baseCrv,offset,component='cv')
                        l_mainCurves.append(baseCrv)
                        
                        endCrv = mc.duplicateCurve("{0}.u[{1}]".format(str_meshShape,v+(_add *2)), ch = 0, rn = 0, local = 0)[0]
                        #endCrv = mc.duplicateCurve("{0}.u[{1}]".format(str_meshShape,l_uValues[i+1]-_add), ch = 0, rn = 0, local = 0)[0]
                        DIST.offsetShape_byVector(endCrv,offset,component='cv')
                        
                        l_mainCurves.append(endCrv)
                        
                        
                        log.debug("|{0}| >> {1} | Making connectors".format(_str_func,i))
                        d_epPos = {}
                        for i,crv in enumerate(l_mainCurves):
                            mCrv = cgmMeta.cgmObject(crv,'cgmObject')
                            for ii,ep in enumerate(mCrv.getComponents('ep',True)):
                                if not d_epPos.get(ii):
                                    d_epPos[ii] = []
                                    
                                _l = d_epPos[ii]
                                _l.append(POS.get(ep))
                                
                        for k,points in d_epPos.iteritems():
                            crv_connect = CURVES.create_fromList(posList=points)
                            l_mainCurves.append(crv_connect)
                            
                        for crv in l_mainCurves[1:]:
                            RIGGING.shapeParent_in_place(l_mainCurves[0], crv, False)
                            
                        ml_shapes.append(cgmMeta.validateObjArg(l_mainCurves[0]))                    

                elif mode == 'segmentHandle':#=============================================================
                    if targets:
                        ml_fkJoints = ml_targets
                    else:
                        ml_fkJoints = mRigNull.msgList_get('fkJoints',asMeta=True)

                    if len(ml_fkJoints)<2:
                        return log.error("|{0}| >> Need at least two ik joints".format(_str_func))                
                    
                    l_failSafes = MATH.get_splitValueList(minU,maxU,
                                                          len(ml_fkJoints))
                    #...Get our vectors...
                    l_vectors = []
                    for i,mObj in enumerate(ml_fkJoints[:-1]):
                        l_vectors.append(  MATH.get_vector_of_two_points(mObj.p_position, ml_fkJoints[i+1].p_position) )
                    l_vectors.append(  MATH.get_vector_of_two_points(ml_fkJoints[-2].p_position, ml_fkJoints[-1].p_position) )
                    
                    #...Get our uValues...
                    #l_uValues = [minU]
                    l_uValues = []
                    for i,mObj in enumerate(ml_fkJoints):
                        _short = mObj.mNode
                        _d = RAYS.cast(str_meshShape, _short, str_aim)
                        log.debug("|{0}| >> Casting {1} ...".format(_str_func,_short))
                        #cgmGEN.log_info_dict(_d,j)
                        try:_v = _d['uvsRaw'][str_meshShape][0][0]                                    
                        except:
                            log.debug("|{0}| >> segmentHandle. Hit fail {1} | {2}".format(_str_func,i,l_failSafes[i]))                                            
                            _v = l_failSafes[i]
                        l_uValues.append( _v )
                    #l_uValues.append(maxU)
                    
                    ml_shapes = []
                    _add = f_factor
                    
                    ml_shapes = []
                    _add = f_factor
                    _offset_seg = offset * 4
                    for i,v in enumerate(l_uValues):
                        l_mainCurves = []
                        
                        if v == l_uValues[-1]:
                            log.debug("|{0}| >> {1} | Last one...".format(_str_func,i))
                            upV = MATH.Clamp(v, minU, maxU)
                            dnV = MATH.Clamp(v - f_factor/4 * 2, minU, maxU)                        
                        else:
                            upV = MATH.Clamp(v + f_factor/4, minU, maxU)
                            dnV = MATH.Clamp(v - f_factor/4, minU, maxU)
                        
                        baseCrv = mc.duplicateCurve("{0}.u[{1}]".format(str_meshShape,dnV), ch = 0, rn = 0, local = 0)[0]
                        DIST.offsetShape_byVector(baseCrv,offset * 2,component='cv')
                        
                        #baseOffsetCrv = mc.offsetCurve(baseCrv, distance = - _offset_seg,
                        #                           normal = l_vectors[i],
                        #                           ch=False )[0]
                        #mc.rebuildCurve(baseCrv, replaceOriginal = True, rt = 3, spans = 12, d=3)
                        
                        l_mainCurves.append(baseCrv)
                        #mc.delete(baseCrv)
                        
                        topCrv = mc.duplicateCurve("{0}.u[{1}]".format(str_meshShape,upV), ch = 0, rn = 0, local = 0)[0]
                        DIST.offsetShape_byVector(topCrv,offset * 2,component='cv')
                        
                        #topOffsetCrv = mc.offsetCurve(topCrv, distance = - _offset_seg,
                        #                           normal = l_vectors[i],
                        #                           ch=False )[0]
                        #mc.rebuildCurve(topCrv, replaceOriginal = True, rt = 3, spans = 12,d=3)                    
                        l_mainCurves.append(topCrv)
                        #mc.delete(topCrv)                    
                        
                        """
                        log.debug("|{0}| >> {1} | Making connectors".format(_str_func,i))
                        d_epPos = {}
                        for i,crv in enumerate(l_mainCurves):
                            #mc.ls(['%s.%s[*]'%(crv,'ep')],flatten=True)
                            mCrv = cgmMeta.cgmObject(crv,'cgmObject')
                            mCrv.getComponents('ep',True)
                            #continue
                            for ii,ep in enumerate(mCrv.getComponents('ep',True)):
                                if not d_epPos.get(ii):
                                    d_epPos[ii] = []
                                _l = d_epPos[ii]
                                _l.append(POS.get(ep))
                        
                        for k,points in d_epPos.iteritems():
                            crv_connect = CURVES.create_fromList(posList=points)
                            l_mainCurves.append(crv_connect)"""
                            
                        
                        for crv in l_mainCurves[1:]:
                            log.debug("|{0}| >> combining: {1}".format(_str_func,crv))
                            RIGGING.shapeParent_in_place(l_mainCurves[0], crv, False)
                            
                        mCrv = cgmMeta.validateObjArg(l_mainCurves[0])
                        mCrv.rename('shapeCast_{0}'.format(i))
                        ml_shapes.append(mCrv)                   

                elif mode == 'limbSegmentHandle':#=============================================================
                    if targets:
                        ml_fkJoints = ml_targets
                    else:
                        ml_fkJoints = mRigNull.msgList_get('fkJoints',asMeta=True)

                    if len(ml_fkJoints)<2:
                        return log.error("|{0}| >> Need at least two ik joints".format(_str_func))
                    
                    for mObj in ml_targets:
                        str_orientation = self.d_orientation['str']
                        l_shapes = []
                        
                        dist = offset * 5
                        pos_obj = mObj.p_position
                        for axis in [str_orientation[1], str_orientation[2]]:
                            for d in ['+','-']:
                                p = SNAPCALLS.get_special_pos([mObj.mNode,
                                                               str_meshShape],
                                                              'cast',axis+d)
                                crv = CURVES.create_fromName(name='semiSphere',
                                                             direction = 'z+',
                                                             size = offset*2)
                                l_shapes.append(crv)
                                mCrv = cgmMeta.validateObjArg(crv,'cgmObject')
                                
                                if not p:
                                    p = DIST.get_pos_by_axis_dist(mObj.mNode, axis+d, dist)
                                    
                                mCrv.p_position = p
                                
                                SNAP.aim_atPoint(mCrv.mNode, pos_obj, 'z-')
                                
                                
                                dist = DIST.get_distance_between_points(p, pos_obj)

                                    
                        for crv in l_shapes[1:]:
                            log.debug("|{0}| >> combining: {1}".format(_str_func,crv))
                            RIGGING.shapeParent_in_place(l_shapes[0], crv, False)
                            
                        ml_shapes.append(cgmMeta.validateObjArg(l_shapes[0],'cgmObject'))
    
                            

                
                elif mode == 'ikHandle':#==================================================================================
                    if not mRigNull.msgList_get('ikJoints'):
                        return log.error("|{0}| >> No ik joints found".format(_str_func))
        
                    ml_ikJoints = mRigNull.msgList_get('ikJoints',asMeta=True)
                    if len(ml_ikJoints)<2:
                        return log.error("|{0}| >> Need at least two ik joints".format(_str_func))
                    
                    vec_normal = MATH.get_vector_of_two_points(ml_ikJoints[-2].p_position,
                                                               ml_ikJoints[-1].p_position)
                    l_mainCurves = []
                    for mJnt in ml_ikJoints[-2:]:
                        #...Make our curve
                        _short = mJnt.mNode
                        _d = RAYS.cast(str_meshShape, _short, str_aim)
                        
                        log.debug("|{0}| >> Casting {1} ...".format(_str_func,_short))
                        #cgmGEN.log_info_dict(_d,j)
                        _v = _d['uvsRaw'][str_meshShape][0][0]                
                        log.debug("|{0}| >> v: {1} ...".format(_str_func,_v))
                
                        #>>For each v value, make a new curve -----------------------------------------------------------------        
                        #duplicateCurve -ch 1 -rn 0 -local 0  "loftedSurface2.u[0.724977270271534]"
                        baseCrv = mc.duplicateCurve("{0}.u[{1}]".format(str_meshShape,_v), ch = 0, rn = 0, local = 0)[0]
                        DIST.offsetShape_byVector(baseCrv,offset,component='cv')
                        #offsetCrv = mc.offsetCurve(baseCrv, distance = -(offset * .9),
                        #                           normal = vec_normal,
                        #                           ch=False )[0]
                        l_mainCurves.append(baseCrv)
                        #mc.delete(baseCrv)                        
                        
                        log.debug("|{0}| >> created: {1} ...".format(_str_func,baseCrv))
                    
                    log.debug("|{0}| >> Making connectors".format(_str_func))
                    d_epPos = {}
                    for i,crv in enumerate(l_mainCurves):
                        mCrv = cgmMeta.cgmObject(crv,'cgmObject')
                        for ii,ep in enumerate(mCrv.getComponents('ep',True)):
                            if not d_epPos.get(ii):
                                d_epPos[ii] = []
                                
                            _l = d_epPos[ii]
                            _l.append(POS.get(ep))
                            
                    for k,points in d_epPos.iteritems():
                        crv_connect = CURVES.create_fromList(posList=points)
                        l_mainCurves.append(crv_connect)
                        
                    for crv in l_mainCurves[1:]:
                        RIGGING.shapeParent_in_place(l_mainCurves[0], crv, False)
                        
                    ml_shapes.append(cgmMeta.validateObjArg(l_mainCurves[0]))                        
                    
                    #ml_shapes = mc.loft(l_loftShapes, o = True, d = 3, po = 0,ch=False)
                    #mc.delete(l_loftShapes)
                    
        elif mode == 'direct':
            if size == None:
                log.debug("|{0}| >> Guessing size".format(_str_func))
                size = DIST.get_distance_between_targets([mObj.mNode for mObj in ml_targets],average=True) * .75
    
            for mTar in ml_targets:
                crv = CURVES.create_controlCurve(mTar.mNode, 'cube',
                                                 sizeMode= 'fixed',
                                                 size = size)
    
                ml_shapes.append(cgmMeta.validateObjArg(crv))
            
        else:
            raise ValueError,"unknown mode: {0}".format(mode)
        #Process
        
        
        if mMesh_tmp:mMesh_tmp.delete()
        return ml_shapes
    except Exception,err:cgmGEN.cgmException(Exception,err)
    
def mesh_proxyCreate(self, targets = None, upVector = None, degree = 1):
    _short = self.mBlock.mNode
    _str_func = 'mesh_proxyCreate ( {0} )'.format(_short)
    _start = time.clock()	
    mRigNull = self.mRigNull
    ml_shapes = []
    
    if upVector is None:
        upVector = self.d_orientation['mOrientation'].p_up.p_string
    
    #Get our prerig handles if none provided
    if targets is None:
        ml_targets = self.mRigNull.msgList_get('rigJoints',asMeta = True)
        if not ml_targets:
            raise ValueError,"No rigJoints connected. NO targets offered"
    else:
        ml_targets = cgmMeta.validateObjListArg(targets,'cgmObject')
    

    ml_handles = self.mBlock.msgList_get('templateHandles',asMeta = True)
    l_targets = [mObj.loftCurve.mNode for mObj in ml_handles]
    #res_body = mc.loft(l_targets, o = True, d = 3, po = 0 )
    #mMesh_tmp = cgmMeta.validateObjArg(res_body[0],'cgmObject')
    #str_tmpMesh = mMesh_tmp.mNode
    
    mMesh_tmp =  self.mBlock.atUtils('get_castMesh')
    str_meshShape = mMesh_tmp.getShapes()[0]    

    
    #Process -----------------------------------------------------------------------------------
    l_newCurves = []
    str_meshShape = mMesh_tmp.getShapes()[0]
    log.debug("|{0}| >> Shape: {1}".format(_str_func,str_meshShape))
    
    minU = ATTR.get(str_meshShape,'minValueU')
    maxU = ATTR.get(str_meshShape,'maxValueU')
    
    l_failSafes = MATH.get_splitValueList(minU,maxU,
                                          len(ml_targets))
    log.debug("|{0}| >> Failsafes: {1}".format(_str_func,l_failSafes))
    
    l_uValues = []
    for i,mTar in enumerate(ml_targets):
        j = mTar.mNode
        _d = RAYS.cast(str_meshShape,j,upVector)
        log.debug("|{0}| >> Casting {1} ...".format(_str_func,j))
        #cgmGEN.log_info_dict(_d,j)
        if not _d:
            log.debug("|{0}| >> Using failsafe value for: {1}".format(_str_func,j))            
            _v = l_failSafes[i]
        else:
            _v = _d['uvsRaw'][str_meshShape][0][0]
        log.debug("|{0}| >> v: {1} ...".format(_str_func,_v))
        
        #>>For each v value, make a new curve -----------------------------------------------------------------        
        #duplicateCurve -ch 1 -rn 0 -local 0  "loftedSurface2.u[0.724977270271534]"
        #l_uValues.append(_v)
        crv = mc.duplicateCurve("{0}.u[{1}]".format(str_meshShape,_v), ch = 0, rn = 0, local = 0)
        log.debug("|{0}| >> created: {1} ...".format(_str_func,crv))        
        l_newCurves.append(crv[0])
        if mTar == ml_targets[-1]:
            crv = mc.duplicateCurve("{0}.u[{1}]".format(str_meshShape,maxU), ch = 0, rn = 0, local = 0)
            l_newCurves.append(crv[0])

    #>>Reloft those sets of curves and cap them -----------------------------------------------------------------
    log.debug("|{0}| >> Create new mesh objs. Curves: {1} ...".format(_str_func,l_newCurves))        
    l_new = []
    for i,c in enumerate(l_newCurves[:-1]):
        _pair = [c,l_newCurves[i+1]]
        _mesh = create_loftMesh(_pair, name="{0}_{1}".format('test',i), divisions=1)
        RIGGING.match_transform(_mesh,ml_targets[i])
        l_new.append(_mesh)
    
    #...clean up 
    mc.delete(l_newCurves)# + [str_tmpMesh]
    mMesh_tmp.delete()
    #>>Parent to the joints ----------------------------------------------------------------- 
    return l_new
    
    
    
    log.info("%s >> Time >> = %0.3f seconds " % (_str_func,(time.clock()-_start)) + "-"*75)	
    
    return ml_shapes


def joints_connectToParent(self):
    try:
        _start = time.clock()    
        _str_func = 'joints_connectToParent'
            
        mRigNull = self.mRigNull
        mMasterControl = self.d_module.get('mMasterControl',False)
        mMasterNull = self.d_module.get('mMasterNull',False)
        mSkeletonGroup = mMasterNull.skeletonGroup
        mModuleParent = self.d_module.get('mModuleParent',False)
    
        ml_joints = mRigNull.msgList_get('moduleJoints')
        if not ml_joints:
            raise ValueError,"|{0}| >> No moduleJoints found".format(_str_func)
        
        if mModuleParent:
            log.debug("|{0}| >> ModuleParent setup...".format(_str_func))
            
        else:
            log.debug("|{0}| >> Root Mode...".format(_str_func))        
            ml_joints[0].p_parent = mSkeletonGroup
            
        
        log.debug("|{0}| >> Time >> = {1} seconds".format(_str_func, "%0.3f"%(time.clock()-_start))) 
    except Exception,err:cgmGEN.cgmException(Exception,err)






    