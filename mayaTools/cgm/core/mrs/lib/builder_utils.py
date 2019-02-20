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
import cgm.core.cgm_RigMeta as cgmRIGMETA

from cgm.core.lib import curve_Utils as CURVES
from cgm.core.lib import attribute_utils as ATTR
from cgm.core.lib import position_utils as POS
from cgm.core.lib import math_utils as MATH
from cgm.core.lib import distance_utils as DIST
from cgm.core.lib import snap_utils as SNAP
from cgm.core.lib import rigging_utils as CORERIG
import cgm.core.lib.rigging_utils as CORERIG
from cgm.core.rigger.lib import joint_Utils as JOINTS
from cgm.core.lib import search_utils as SEARCH
from cgm.core.lib import rayCaster as RAYS
from cgm.core.cgmPy import validateArgs as VALID
from cgm.core.cgmPy import path_Utils as PATH
import cgm.core.lib.node_utils as NODES
import cgm.core.rig.joint_utils as COREJOINTS
import cgm.core.classes.NodeFactory as NODEFACTORY
import cgm.core.lib.locator_utils as LOC
import cgm.core.mrs.lib.shared_dat as BLOCKSHARE
import cgm.core.tools.lib.snap_calls as SNAPCALLS
import cgm.core.rig.general_utils as RIGGEN
import cgm.core.lib.surface_Utils as SURF
import cgm.core.lib.transform_utils as TRANS
import cgm.core.lib.list_utils as LISTS
import cgm.core.classes.NodeFactory as NodeF
import cgm.core.mrs.lib.ModuleControlFactory as MODULECONTROL
from cgm.core.classes import GuiFactory as cgmUI
for m in BLOCKSHARE,MATH,DIST,RAYS,RIGGEN,SNAPCALLS:
    reload(m)

from cgm.core.cgmPy import os_Utils as cgmOS


def eyeLook_get(self,autoBuild=False):
    _str_func = 'eyeLook_get'
    
    log.debug("|{0}| >>  ".format(_str_func)+ '-'*80)
    log.debug("{0}".format(self))
    mBlock = self.mBlock
    
    mModule = self.mModule
    mRigNull = self.mRigNull
    mPuppet = self.mPuppet

    try:return mModule.eyeLook
    except:pass
    try:return mi_module.moduleParent.eyeLook
    except:pass
    
    ml_puppetEyelooks = mPuppet.msgList_get('eyeLook')
    if ml_puppetEyelooks:
        if len(ml_puppetEyelooks) == 1 and ml_puppetEyelooks[0]:
            return ml_puppetEyelooks[0]
        else:
            raise StandardError,"More than one puppet eye look"
        
    if autoBuild:
        return eyeLook_verify(self)
    return False

@cgmGEN.Timer
def eyeLook_verify(self):
    _str_func = 'eyeLook_verify'
    try:
        log.debug("|{0}| >>  ".format(_str_func)+ '-'*80)
        log.debug("{0}".format(self))
        mBlock = self.mBlock
        
        mModule = self.mModule
        mRigNull = self.mRigNull
        mPuppet = self.mPuppet
        mHandleFactory = mBlock.asHandleFactory()
        
        _eyeLook = eyeLook_get(self)
        if _eyeLook:
            log.debug("|{0}| >> Found existing eyeLook...".format(_str_func))                      
            return _eyeLook
        
        if mBlock.blockType not in ['eye']:
            raise ValueError,"blocktype must be eye. Found {0} | {1}".format(mBlock.blockType,mBlock)
        
        #Data... -----------------------------------------------------------------------
        log.debug("|{0}| >> Get data...".format(_str_func))
        #_size = mHandleFactory.get_axisBox_size(mBlock.getMessage('bbHelper'))
        
        try:
            _size = self.v_baseSize
            _sizeAvg = self.f_sizeAvg             
        except:
            _size = [mBlock.blockScale * v for v in mBlock.baseSize]
            _sizeAvg = MATH.average(_size)
        
        #Create shape... -----------------------------------------------------------------------        
        log.debug("|{0}| >> Creating shape...".format(_str_func))
        mCrv = cgmMeta.asMeta( CURVES.create_fromName('arrow4Fat',
                                                      direction = 'z+',
                                                      size = _sizeAvg ,
                                                      absoluteSize=False),'cgmObject',setClass=True)
        mCrv.doSnapTo(mBlock.mNode)
        pos = mBlock.getPositionByAxisDistance('z+',
                                               _sizeAvg * 4)
        
        mCrv.p_position = 0,pos[1],pos[2]
        
        
        mBlockParent = mBlock.p_blockParent
        if mBlockParent:
            mCrv.doStore('cgmName',mBlockParent.cgmName + '_eyeLook')
            mBlockParent.asHandleFactory().color(mCrv.mNode)
        else:
            mCrv.doStore('cgmName','eyeLook')
            mHandleFactory.color(mCrv.mNode)
        
        mCrv.doName()
        

        #Register control... -----------------------------------------------------------------------        
        log.debug("|{0}| >> Registering Control... ".format(_str_func))
        d_buffer = MODULECONTROL.register(mCrv,
                                          mirrorSide= 'center',
                                          mirrorAxis="translateX,rotateY,rotateZ",
                                          addSpacePivots = 2)
        
        mCrv = d_buffer['mObj']        
        
        
        #Dynparent... -----------------------------------------------------------------------        
        log.debug("|{0}| >> Dynparent setup.. ".format(_str_func))
        ml_dynParents = copy.copy(self.ml_dynParentsAbove)
        mHead = False
        for mParent in ml_dynParents:
            log.debug("|{0}| >> mParent: {1}".format(_str_func,mParent))
            
            if mParent.getMayaAttr('cgmName') == 'head':
                log.debug("|{0}| >> found head_direct...".format(_str_func))
                mHead = mParent
                break
        if mHead:
            ml_dynParents.insert(0,mHead)
        #if mBlock.attachPoint == 'end':
        #ml_dynParents.reverse()
        
        ml_dynParents.extend(mCrv.msgList_get('spacePivots'))
        ml_dynParents.extend(copy.copy(self.ml_dynEndParents))
        
        ml_dynParents = LISTS.get_noDuplicates(ml_dynParents)
        mDynParent = cgmRIGMETA.cgmDynParentGroup(dynChild=mCrv,dynMode=0)
        
        for o in ml_dynParents:
            mDynParent.addDynParent(o)
        mDynParent.rebuild()
        
        #Connections... -----------------------------------------------------------------------        
        log.debug("|{0}| >> Connections... ".format(_str_func))
        mModule.connectChildNode(mCrv,'eyeLook')
        mPuppet.msgList_append('eyeLook',mCrv,'puppet')
        
        if mBlockParent:
            log.debug("|{0}| >> Adding to blockParent...".format(_str_func))
            mModuleParent = mBlockParent.moduleTarget
            mModuleParent.connectChildNode(mCrv,'eyeLook')
            if mModuleParent.mClass == 'cgmRigModule':
                mBlockParentRigNull = mModuleParent.rigNull
                mBlockParentRigNull.msgList_append('controlsAll',mCrv)
                mBlockParentRigNull.moduleSet.append(mCrv)
                mRigNull.faceSet.append(mCrv)
                
                mCrv.connectParentNode(mBlockParentRigNull,'rigNull')
                
            else:
                mModuleParent.puppetSet.append(mCrv)
                mModuleParent.msgList_append('controlsAll',mCrv)
                mModuleParent.faceSet.append(mCrv)
                

        #Connections... -----------------------------------------------------------------------        
        log.debug("|{0}| >> Heirarchy... ".format(_str_func))
        mCrv.masterGroup.p_parent = self.mDeformNull
        
        for link in 'masterGroup','dynParentGroup':
            if mCrv.getMessage(link):
                mCrv.getMessageAsMeta(link).dagLock(True)
                
        mCrv.addAttr('cgmControlDat','','string')
        mCrv.cgmControlDat = {'tags':['ik']}                
        
        return mCrv
    
    except Exception,error:
        cgmGEN.cgmExceptCB(Exception,error,msg=vars())

   


    try:#moduleParent Stuff =======================================================
        if mi_moduleParent:
            try:
                for mCtrl in self.ml_controlsAll:
                    mi_parentRigNull.msgList_append('controlsAll',mCtrl)
            except Exception,error: raise Exception,"!Controls all connect!| %s"%error	    
            try:mi_parentRigNull.moduleSet.extend(self.ml_controlsAll)
            except Exception,error: raise Exception,"!Failed to set module objectSet! | %s"%error
    except Exception,error:raise Exception,"!Module Parent registration! | %s"%(error)	    



def get_controlSpaceSetupDict(self):
    _str_func = 'get_controlSpaceSetupDict'
    
    #SpacePivots ============================================================================
    log.debug("|{0}| >>  ".format(_str_func)+ '-'*80)
    log.debug("{0}".format(self))
    mBlock = self.mBlock
    
    if not mBlock.hasAttr('numSpacePivots'):
        return False
    
    _spacePivots = mBlock.numSpacePivots
    if _spacePivots:
        d_controlSpaces = {'addSpacePivots':_spacePivots}
    else:
        d_controlSpaces = {'addConstrainGroup':True}
    log.debug("|{0}| >> d_controlSpaces {1}".format(_str_func,d_controlSpaces))
    
    return d_controlSpaces

def gather_rigBlocks(progressBar=False):
    _str_func = 'gather_rigBlocks'
    try:
        mGroup = get_blockGroup()
        ml_gathered = []
        ml_blocks = r9Meta.getMetaNodes(mTypes = 'cgmRigBlock',nTypes=['transform','network'])
        if progressBar:
            int_len = len(ml_blocks)
            
        for i,mObj in enumerate(ml_blocks):
            log.debug("|{0}| >> Checking: {1}".format(_str_func,mObj))
            if progressBar:
                cgmUI.progressBar_set(progressBar,
                                      maxValue = int_len,
                                      progress=i, vis=True)                        
            if not mObj.parent:
                mObj.parent = mGroup
                ml_gathered.append(mObj)
                
            for link in ['noTransTemplateNull','noTransDefineNull','noTransPrerigNull']:
                try:
                    mLink = mObj.getMessageAsMeta(link)
                    if mLink and not mLink.parent:
                        log.info("|{0}| >> {1} | {2}".format(_str_func,link,mLink))            
                        mLink.parent = mGroup
                        ml_gathered.append(mLink)
                except Exception,err:
                    log.error("{0} | {1}".format(link,err))
                    
        
        return log.info("|{0}| >> Gathered {1} dags".format(_str_func,len(ml_gathered)))
    except Exception,err:
        raise Exception,err
    finally:
        if progressBar:cgmUI.progressBar_end(progressBar)


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
    
    _l_rigBlocks = r9Meta.getMetaNodes(mTypes = 'cgmRigBlock',nTypes=['transform','network'])
    
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
        log.debug(cgmGEN._str_subLine)
        log.debug("|{0}| >> DUPLICATE MODULES....".format(_str_func))
        for m in _l_duplicates:
            print(m)
        raise Exception,"Must resolve"
    log.debug("|{0}| >> Found {1} modules under: {2}".format(_str_func,len(_d_files.keys()),_path))     
    if _l_unbuildable:
        log.debug(cgmGEN._str_subLine)
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

def get_midIK_basePosOrient(self,ml_handles = [], markPos = False, forceMidToHandle=False):
    """
    
    """
    raise DeprecationWarning,"Change to BLOCKUTILS.prerig_get_rpBasePos"
    try:
        _str_func = 'get_midIK_basePosOrient'
        log.debug("|{0}| >>  {1}".format(_str_func,self)+ '-'*80)
        
        if ml_handles:
            ml_use = ml_handles
        else:
            ml_prerigHandles = self.mBlock.msgList_get('prerigHandles')
            ml_templateHandles = self.mBlock.msgList_get('templateHandles')
            
            int_count = self.mBlock.numControls
            ml_use = ml_prerigHandles[:int_count]
            
        log.debug("|{0}| >> Using: {1}".format(_str_func,[mObj.p_nameBase for mObj in ml_use]))
        
        #Mid dat... ----------------------------------------------------------------------
        _len_handles = len(ml_use)
        if _len_handles == 1:
            mid=0
            mMidHandle = ml_use[0]
        else:
            
            mid = int(_len_handles)/2
            mMidHandle = ml_use[mid]
            
        log.debug("|{0}| >> mid: {1}".format(_str_func,mid))
        
        b_absMid = False
        if MATH.is_even(_len_handles) and not forceMidToHandle:
            log.debug("|{0}| >> absolute mid mode...".format(_str_func,mid))
            b_absMid = True
            
        
        
        #...Main vector -----------------------------------------------------------------------
        mOrientHelper = self.mBlock.orientHelper
        vec_base = MATH.get_obj_vector(mOrientHelper, 'y+')
        log.debug("|{0}| >> Block up: {1}".format(_str_func,vec_base))
        
        #...Get vector -----------------------------------------------------------------------
        if b_absMid:
            crvCubic = CORERIG.create_at(ml_use, create= 'curve')
            pos_mid = CURVES.getMidPoint(crvCubic)
            mc.delete(crvCubic)
        else:
            pos_mid = mMidHandle.p_position
            
        crv = CORERIG.create_at([ml_use[0].mNode,ml_use[-1].mNode], create= 'curveLinear')
        pos_close = DIST.get_closest_point(pos_mid, crv, markPos)[0]
        log.debug("|{0}| >> Pos close: {1} | Pos mid: {2}".format(_str_func,pos_close,pos_mid))
        
        if MATH.is_vector_equivalent(pos_mid,pos_close,3):
            log.debug("|{0}| >> Mid on linear line, using base vector".format(_str_func))
            vec_use = vec_base
        else:
            vec_use = MATH.get_vector_of_two_points(pos_close,pos_mid)
            mc.delete(crv)
        
        #...Get length -----------------------------------------------------------------------
        #dist_helper = 0
        #if ml_use[-1].getMessage('pivotHelper'):
            #log.debug("|{0}| >> pivotHelper found!".format(_str_func))
            #dist_helper = max(POS.get_bb_size(ml_use[-1].getMessage('pivotHelper')))
            
        dist_min = DIST.get_distance_between_points(ml_use[0].p_position, pos_mid)/2.0
        dist_base = DIST.get_distance_between_points(pos_mid, pos_close)
        
        #...get new pos
        dist_use = MATH.Clamp(dist_base, dist_min, None)
        log.debug("|{0}| >> Dist min: {1} | dist base: {2} | use: {3}".format(_str_func,
                                                                              dist_min,
                                                                              dist_base,
                                                                              dist_use))
        
        pos_use = DIST.get_pos_by_vec_dist(pos_mid,vec_use,dist_use*2)
        pos_use2 = DIST.get_pos_by_vec_dist(pos_mid,vec_base,dist_use*2)
        
        reload(LOC)
        if markPos:
            LOC.create(position=pos_use,name='pos1')
            LOC.create(position=pos_use2,name='pos2')
        
        return pos_use
        
        pos_mid = ml_templateHandles[mid].p_position
    
    
        #Get our point for knee...
        vec_mid = MATH.get_obj_vector(ml_blendJoints[1], 'y+')
        pos_mid = mKnee.p_position
        pos_knee = DIST.get_pos_by_vec_dist(pos_knee,
                                            vec_knee,
                                            DIST.get_distance_between_points(ml_blendJoints[0].p_position, pos_knee)/2)
    
        mKnee.p_position = pos_knee
    
        CORERIG.match_orientation(mKnee.mNode, mIKCrv.mNode)    
    
    
        return True
    except Exception,err:
        cgmGEN.cgmExceptCB(Exception,err)

def build_skeleton(positionList = [], joints = 1, axisAim = 'z+', axisUp = 'y+', worldUpAxis = [0,1,0],asMeta = True):
    _str_func = 'build_skeleton'
    _axisAim = axisAim
    _axisUp = axisUp
    _axisWorldUp = worldUpAxis
    _l_pos = positionList
    _radius = 1    
    mc.select(cl=True)
    #pprint.pprint(vars())
    
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

def controls_lockDown(ml_controls):
    _str_func = 'controls_lockDown'
    log.debug("|{0}| >> ...".format(_str_func))
    
    for mCtrl in ml_controls:
        _str = mCtrl.mNode
        if mCtrl.hasAttr('radius'):
            ATTR.set_hidden(_str,'radius',True)
        
        for link in 'masterGroup','dynParentGroup','aimGroup','worldOrientGroup':
            if mCtrl.getMessage(link):
                mCtrl.getMessageAsMeta(link).dagLock(True)
                
        try:
            if ATTR.has_attr(_str,'visibility'):
                ATTR.set_hidden(_str,'visibility',True)
                ATTR.set_keyable(_str,'visibility',False)
        except:pass
        
        
        

def control_convertToWorldIK(mCtrl=None):
    """
    """
    _str_func = 'control_convertToWorldIK'
    rot = mCtrl.p_orient
    mGrp_zero = mCtrl.doGroup(True,True,asMeta=True,typeModifier = 'worldOrient')
    

    xDot = mCtrl.getTransformDirection(MATH.Vector3.right()).dot(MATH.Vector3.forward())
    yDot = mCtrl.getTransformDirection(MATH.Vector3.up()).dot(MATH.Vector3.forward())
    zDot = mCtrl.getTransformDirection(MATH.Vector3.forward()).dot(MATH.Vector3.forward())
    
    xUpDot = mCtrl.getTransformDirection(MATH.Vector3.right()).dot(MATH.Vector3.up())
    yUpDot = mCtrl.getTransformDirection(MATH.Vector3.up()).dot(MATH.Vector3.up())
    zUpDot = mCtrl.getTransformDirection(MATH.Vector3.forward()).dot(MATH.Vector3.up())
    
    #Get our up and vector
    closestForward = "x"
    closestUp = "x"
    highestDot = xDot
    highestUpDot = xUpDot
    
    if(abs(yDot) > abs(highestDot)):
        closestForward = "y"
        highestDot = yDot
    
    if(abs(zDot) > abs(highestDot)):
        closestForward = "z"
        highestDot = zDot
    
    if(abs(yUpDot) > abs(highestUpDot)):
        closestUp = "y"
        highestUpDot = yUpDot
    
    if(abs(zUpDot) > abs(highestUpDot)):
        closestUp = "z"
        highestUpDot = zUpDot
    
    if(highestDot < 0):
        closestForward = "{0}-".format(closestForward)
    if(highestUpDot < 0):
        closestUp = "{0}-".format(closestUp)
        
    log.debug('closest forward axis is "%s" and closest up axis is "%s"' % (closestForward, closestUp))    
    pos_aim = DIST.get_pos_by_vec_dist(mCtrl.p_position, [0,0,1], 10.0)
    
    SNAP.aim_atPoint(mGrp_zero.mNode, pos_aim, closestForward, mode='world', vectorUp=[0,1,0] )
    
    mCtrl.p_orient = rot
    d = {'rotateX':mCtrl.rotateX,'rotateY':mCtrl.rotateY,'rotateZ':mCtrl.rotateZ}
    mCtrl.addAttr('defaultValues',d)
    return
    
 
def build_loftMesh(root, jointCount = 3, degree = 3, cap = True, merge = True,reverseSurfaceNormals=True):
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
    _res_body = mc.loft(_l_targets, o = True, d = degree, po = 1,reverseSurfaceNormals=reverseSurfaceNormals )

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
        CORERIG.match_transform(_mesh,_l_joints[i])
        _l_new.append(_mesh)
    
    #...clean up 
    mc.delete(_l_newCurves + _res_body)
    #>>Parent to the joints ----------------------------------------------------------------- 
    return _l_new

def create_loftMesh(targets = None, name = 'test', degree = 2, uSplit = 0,vSplit=0, divisions = None,
                    cap = True, merge = True,form = 1,planar=False,reverseSurfaceNormals=True,deleteHistory =True ):
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
        raise ValueError, "|{0}| >> No targets provided".format(_str_func)
    
    mc.select(cl=True)
    log.debug("|{0}| >> targets: {1}".format(_str_func,targets))
    
    #tess method - general, uType 1, vType 2+ joint count
    
    int_count = len(targets)
    
    #>>Body -----------------------------------------------------------------
    _ss = 1
    if degree == 1:
        _loftDegree = 1
        _ss = vSplit
    else:
        _loftDegree = 3
        
    _res_body = mc.loft(targets, o = True, d = _loftDegree, po = 1, ss=_ss,
                        autoReverse=True,
                        reverseSurfaceNormals=False )
    mTarget1 = cgmMeta.cgmObject(targets[0])
    l_cvs = mc.ls("{0}.cv[*]".format(mTarget1.getShapes()[0]),flatten=True)
    points = len(l_cvs)

    _inputs = mc.listHistory(_res_body[0],pruneDagObjects=True)
    _tessellate = _inputs[0]
    

    if degree == 1:
        if form == 2:
            _d = {'format':2,#General
                  'polygonType':1,#'quads',
                  'vNumber':1,
                  'uNumber': int_count+(int_count*uSplit) }            
        else:
            _d = {'format':3,#General
                  'polygonType':1,#'quads',
                  'vNumber':1,
                  'uNumber': int_count+(uSplit) }
    else:
        _d = {'format':form,#Fit              
              'polygonType':1,#'quads',
              'vNumber':1+vSplit,
              'uNumber': points+(uSplit*points)}
        
    for a,v in _d.iteritems():
        ATTR.set(_tessellate,a,v)
        
    #mc.polySoftEdge(_res_body[0], a = 30, ch = 1)
    
    #if degree ==1:
        ##mc.polyNormal(_res_body[0],nm=0)
        #mc.polySetToFaceNormal(_res_body[0],setUserNormal = True)
        #mc.polyNormal(_res_body[0], normalMode = 0, userNormalMode=1,ch=0)

    if form == 2:
        mc.polyNormal(_res_body[0],nm=0)           
    
    if not deleteHistory:
        return _res_body[0]
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
            log.debug(_res)
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
    
    #if degree == 1:
        #mc.polyNormal(_res_body[0],nm=0)
    
    if planar:
        mc.polySetToFaceNormal(_res_body[0],setUserNormal = True)#THIS WILL MAKE GEO SMOOTH
        #mc.polyNormal(_res_body[0], normalMode = 0, userNormalMode=1,ch=0)
       # mc.polySetToFaceNormal(_res_body[0],setUserNormal = True)
        
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
    
    
    return mPlug_result_moduleSubDriver


def get_blockScale(self,plug='blockScale',ml_joints = None):
    """
    Creates a curve for measuring a segment length. This should be parented under whatever root you setup for that segment
    """
    _str_func = 'get_blockScale'
    log.debug("|{0}| >> ".format(_str_func)+ '-'*80)
    mRigNull = self.mRigNull
    plug_curve = "{0}Curve".format(plug)
    
    if mRigNull.getMessage(plug_curve):
        return [cgmMeta.cgmAttr(mRigNull.mNode,plug), mRigNull.getMessage(plug_curve,asMeta=1)[0]]
        
    if ml_joints is None:
        ml_joints = self.d_joints['ml_moduleJoints']
    
    crv = CORERIG.create_at(None,'curveLinear',l_pos= [ml_joints[0].p_position, ml_joints[1].p_position])
    
    mCrv = ml_joints[0].doCreateAt()
    
    #mCrv = cgmMeta.validateObjArg(crv,'cgmObject',setClass=True)
    CORERIG.shapeParent_in_place(mCrv.mNode,crv,False)
    mCrv.rename('{0}_measureCrv'.format( plug ))
    
    
    mRigNull.connectChildNode(mCrv,plug_curve,'rigNull')
    
    #mCrv.p_parent = self.mConstrainNull
    log.debug("|{0}| >> created: {1}".format(_str_func,mCrv)) 
        
    
    infoNode = CURVES.create_infoNode(mCrv.mNode)
    
    mInfoNode = cgmMeta.validateObjArg(infoNode,'cgmNode',setClass=True)
    mInfoNode.addAttr('baseDist', mInfoNode.arcLength,attrType='float')
    mInfoNode.rename('{0}_{1}_measureCIN'.format( self.d_module['partName'],plug))
    
    log.debug("|{0}| >> baseDist: {1}".format(_str_func,mInfoNode.baseDist)) 
    
    mPlug_blockScale = cgmMeta.cgmAttr(mRigNull.mNode,plug,'float')

    l_argBuild=[]
    l_argBuild.append("{0} = {1} / {2}".format(mPlug_blockScale.p_combinedShortName,
                                               '{0}.arcLength'.format(mInfoNode.mNode),
                                               "{0}.baseDist".format(mInfoNode.mNode)))
    
    
    for arg in l_argBuild:
        log.debug("|{0}| >> Building arg: {1}".format(_str_func,arg))
        NodeF.argsToNodes(arg).doBuild()
        
        
    return [cgmMeta.cgmAttr(mRigNull.mNode,plug), mCrv, mInfoNode]

def get_switchTarget(self,mControl,parentTo=False):
    _str_func = 'switchMode'
    log.debug("|{0}| >> ".format(_str_func)+ '-'*80)
    log.debug("Control: {0} | parentTo: {1}".format(mControl,parentTo))
    
    if mControl.getMessage('switchTarget'):
        mSwitchTarget = mControl.getMessage('switchTarget',asMeta=True)[0]
        mSwitchTarget.setAttrFlags(lock=False)
    else:
        mSwitchTarget = mControl.doCreateAt(setClass=True)
        mControl.doStore('switchTarget',mSwitchTarget)
        mSwitchTarget.rename("{0}_switchTarget".format(mControl.p_nameBase))
        
    log.debug("|{0}| >> Controlsnap target : {1} | from: {2}".format(_str_func, mSwitchTarget, mControl))
    mSwitchTarget.p_parent = parentTo
    mSwitchTarget.setAttrFlags()
    


def register_mirrorIndices(self, ml_controls = []):
    raise ValueError,"Don't use this"
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
                    log.debug("Extra controls : {0}".format(buffer))
        except Exception,error:
            log.error("mCtrl failed to search for msgList : {0}".format(mCtrl))
            log.error(error)
            log.error(cgmGEN._str_subLine)
    
    ml_controls.extend(ml_extraControls)
    
    for i,mCtrl in enumerate(ml_controls):
        mCtrl.addAttr('mirrorIndex', value = (int_strt + i))

    log.debug("|{0}| >> Time >> = {1} seconds".format(_str_func, "%0.3f"%(time.clock()-_start))) 
    
    return ml_controls


def rigNodes_store(self):
    """
    :parameters:

    :returns:
        
    :raises:
        Exception | if reached

    """
    _str_func = 'rigNodes_store'
    log.debug("|{0}| >>  ".format(_str_func)+ '-'*80)
    log.debug("{0}".format(self))
    
    l_postNodes = SEARCH.get_nodeSnapShot()
    _res = []
    for o in l_postNodes:
        try:
            if mc.ls(o, uuid=True)[0] in self.l_preNodesUUIDs:
                log.debug("|{0}| >>  pre uuid match: {1}".format(_str_func,o))
                continue
        except:
            pass
        if o not in self.l_preNodesBuffer:
            _res.append(o)
            
    if self.__dict__.get('mRigNull'):
        _str_owner = self.mRigNull.module.mNode
        self.mRigNull.connectChildrenNodes(_res,'rigNodes')
        for o in _res:
            ATTR.set_message(o,'cgmOwner',_str_owner,simple=True)
    else:
        self.mPuppet.connectChildrenNodes(_res,'rigNodes','cgmOwner')
        
    print _res


@cgmGEN.Timer
def get_dynParentTargetsDat(self,allParents=True):
    """
    :parameters:

    :returns:
        
    :raises:
        Exception | if reached

    """
    _str_func = 'get_dynParentTargetsDat'
    log.debug("|{0}| >>  ".format(_str_func)+ '-'*80)
    log.debug("{0}".format(self))
    
    log.debug("|{0}| >> Resolve moduleParent dynTargets".format(_str_func))
    
    mBlock = self.mBlock
    mModule = self.mModule
    mMasterNull = self.d_module['mMasterNull']
    mModuleParent = self.d_module['mModuleParent']
    self.md_dynTargetsParent = {}
    self.ml_dynEndParents = [mMasterNull.puppetSpaceObjectsGroup, mMasterNull.worldSpaceObjectsGroup]
    self.ml_dynParentsAbove = []
    self.md_dynTargetsParent['world'] = mMasterNull.worldSpaceObjectsGroup
    self.md_dynTargetsParent['puppet'] = mMasterNull.puppetSpaceObjectsGroup
    
    #self.md_dynTargetsParent['driverPoint'] = mModule.atUtils('get_driverPoint',
    #                                                         ATTR.get_enumValueString(mBlock.mNode,'attachPoint'))
    #
    self.md_dynTargetsParent['attachDriver'] = mModule.rigNull.getMessageAsMeta('attachDriver')
    
    _mBase = mModule.atUtils('get_driverPoint','base')
    _mEnd = mModule.atUtils('get_driverPoint','end')
    
    if _mBase:
        self.md_dynTargetsParent['base'] = _mBase
        self.ml_dynParentsAbove.append(_mBase)
    if _mEnd:
        self.md_dynTargetsParent['end'] = _mEnd
        self.ml_dynParentsAbove.append(_mEnd)    
    
    
    if allParents:ml_moduleParents = mModule.atUtils('parentModules_get')
    else: ml_moduleParents = [mModuleParent]
    if ml_moduleParents:
        log.debug("|{0}| >> mParents: {1}".format(_str_func,len(ml_moduleParents)))        
        for mModuleParent in ml_moduleParents:
            mi_parentRigNull = mModuleParent.rigNull
            if not self.md_dynTargetsParent.get('root'):
                if mi_parentRigNull.getMessage('rigRoot'):
                    mParentRoot = mi_parentRigNull.rigRoot
                    self.md_dynTargetsParent['root'] = mParentRoot
                    #self.ml_dynEndParents.insert(0,mParentRoot)
                    self.ml_dynParentsAbove.append(mParentRoot)
                else:
                    self.md_dynTargetsParent['root'] = False            
            
            
            _mBase = mModuleParent.atUtils('get_driverPoint','base')
            _mEnd = mModuleParent.atUtils('get_driverPoint','end')
            
            if _mBase:
                self.md_dynTargetsParent['base'] = _mBase
                self.ml_dynParentsAbove.append(_mBase)
            if _mEnd:
                self.md_dynTargetsParent['end'] = _mEnd
                self.ml_dynParentsAbove.append(_mEnd)            
            
    self.ml_dynEndParents=LISTS.get_noDuplicates(self.ml_dynEndParents)
    self.ml_dynParentsAbove=LISTS.get_noDuplicates(self.ml_dynParentsAbove)
    
    mMasterAnim = self.d_module['mMasterControl']
    if mMasterAnim in self.ml_dynParentsAbove:
        self.ml_dynParentsAbove.remove(mMasterAnim)
    
    log.debug(cgmGEN._str_subLine)
    log.debug("dynTargets | self.md_dynTargetsParent ...".format(_str_func))            
    #pprint.pprint(self.md_dynTargetsParent)
    log.debug(cgmGEN._str_subLine)    
    log.debug("dynEndTargets | self.ml_dynEndParents ...".format(_str_func))                
    #pprint.pprint(self.ml_dynEndParents)
    log.debug(cgmGEN._str_subLine)
    log.debug("dynTargets from above | self.ml_dynParentsAbove ...".format(_str_func))                
    #pprint.pprint(self.ml_dynParentsAbove)    
    log.debug(cgmGEN._str_subLine)    


@cgmGEN.Timer
def shapes_fromCast(self, targets = None, mode = 'default', aimVector = None, upVector = None, uValues = [], offset = None, size = None,f_factor = None,connectionPoints=6):
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
        
        
        _dir = self.d_module.get('direction')
        if aimVector is None:
            if _dir and _dir.lower() == 'left':
                str_aim = self.d_orientation['mOrientation'].p_outNegative.p_string
            else:
                str_aim = self.d_orientation['mOrientation'].p_out.p_string        
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
        if mode not in ['singleCurve']:
            if targets is None:
                ml_targets = self.mBlock.msgList_get('prerigHandles',asMeta = True)
                if not ml_targets:
                    raise ValueError,"No prerigHandles connected. NO targets offered"
            else:
                ml_targets = cgmMeta.validateObjListArg(targets,'cgmObject')
        
        if offset is None:
            offset = self.mPuppet.atUtils('get_shapeOffset')
            #offset = self.d_module.get('f_shapeOffset',1.0)

        if mode in ['singleCurve']:
            mMesh_tmp =  self.mBlock.atUtils('get_castMesh')
            str_meshShape = mMesh_tmp.getShapes()[0]
            
            minU = ATTR.get(str_meshShape,'minValueU')
            maxU = ATTR.get(str_meshShape,'maxValueU')
            
            if f_factor is None:
                f_factor = (maxU-minU)/(20)                
            
            if mode == 'singleCurve':
                ml_shapes = []
                _add = f_factor/2
                
                l_curves = SURF.get_splitValues(str_meshShape,
                                                [minU,maxU],
                                                mode='u',
                                                insertMax=True,
                                                preInset = f_factor*.25,
                                                postInset = -f_factor*.25,
                                                curvesCreate=True,
                                                curvesConnect=True,
                                                connectionPoints=connectionPoints,
                                                offset=offset)
                ml_shapes = cgmMeta.validateObjListArg(l_curves)            
            
        elif mode in ['default',
                    'segmentHandle',
                    'ikHandle',
                    'ikEnd',
                    'ikBase',
                    'frameHandle',
                    'loftHandle',
                    'limbHandle',
                    'castHandle',
                    'limbSegmentHandle',
                    'limbSegmentHandleBack',
                    'simpleCast',
                    'singleCast']:
            #Get our cast mesh        
            ml_handles = self.mBlock.msgList_get('prerigHandles',asMeta = True)

            mMesh_tmp =  self.mBlock.atUtils('get_castMesh')
            str_meshShape = mMesh_tmp.getShapes()[0]
            
            minU = ATTR.get(str_meshShape,'minValueU')
            maxU = ATTR.get(str_meshShape,'maxValueU')
            if f_factor is None:
                f_factor = (maxU-minU)/(20)                            
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
                    log.debug("|{0}| >> v: {1} ...".format(_str_func,v))
                
                    #>>For each v value, make a new curve -----------------------------------------------------------------        
                    baseCrv = mc.duplicateCurve("{0}.u[{1}]".format(str_meshShape,v), ch = 0, rn = 0, local = 0)[0]
                    DIST.offsetShape_byVector(baseCrv,offset)
                    ml_shapes.append(cgmMeta.validateObjArg(baseCrv))
                    
            elif mode in ['segmentHandle','ikHandle','frameHandle','castHandle','limbHandle','limbSegmentHandleBack','limbSegmentHandle','simpleCast','singleCast',
                          'ikEnd','ikBase']:
                
               
                if targets:
                    ml_fkJoints = ml_targets
                else:
                    ml_fkJoints = mRigNull.msgList_get('fkJoints',asMeta=True)
                    
                #if len(ml_fkJoints)<2:
                    #return log.error("|{0}| >> Need at least two joints. Mode: {1}".format(_str_func,mode))
                
                
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
                            CORERIG.shapeParent_in_place(l_mainCurves[0], crv, False)
                            
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
                        CORERIG.shapeParent_in_place(l_mainCurves[0], crv, False)
                        
                    ml_shapes.append(cgmMeta.validateObjArg(l_mainCurves[0]))
                    
                    #ml_shapes = mc.loft(l_loftShapes, o = True, d = 3, po = 0,ch=False)
                    #mc.delete(l_loftShapes)
                    
                elif mode == 'frameHandle':#================================================================
                    #if not mRigNull.msgList_get('fkJoints'):
                        #return log.error("|{0}| >> No fk joints found".format(_str_func))
                    
                    #...Get our vectors...
                    """
                    l_vectors = []
                    for i,mObj in enumerate(ml_fkJoints[:-1]):
                        l_vectors.append(  MATH.get_vector_of_two_points(mObj.p_position, ml_fkJoints[i+1].p_position) )
                    l_vectors.append(  MATH.get_vector_of_two_points(ml_fkJoints[-2].p_position, ml_fkJoints[-1].p_position) )
                    l_vectors.append( l_vectors[-1])#...add it again
                    """
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
                    
                    reload(SURF)
                    l_curves = SURF.get_splitValues(str_meshShape,
                                                    l_uValues,
                                                    mode='u',
                                                    insertMax=True,
                                                    preInset = f_factor*.25,
                                                    postInset = -f_factor*.25,
                                                    curvesCreate=True,
                                                    curvesConnect=True,
                                                    connectionPoints=connectionPoints,
                                                    offset=offset)
                    ml_shapes = cgmMeta.validateObjListArg(l_curves)
                     
                elif mode == 'castHandle':#================================================================
                    #if not mRigNull.msgList_get('fkJoints'):
                        #return log.error("|{0}| >> No fk joints found".format(_str_func))
                    
                    #...Get our vectors...
                    """
                    l_vectors = []
                    for i,mObj in enumerate(ml_fkJoints[:-1]):
                        l_vectors.append(  MATH.get_vector_of_two_points(mObj.p_position, ml_fkJoints[i+1].p_position) )
                    l_vectors.append(  MATH.get_vector_of_two_points(ml_fkJoints[-2].p_position, ml_fkJoints[-1].p_position) )
                    l_vectors.append( l_vectors[-1])#...add it again
                    """
                    
                    l_failSafes = MATH.get_splitValueList(minU,maxU,
                                                          len(ml_fkJoints))                    
                    
                    #...Get our uValues...
                    l_uValues = []
                    #l_sets = []
                    
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
                    
                    l_curves = SURF.get_splitValues(str_meshShape,
                                                    l_uValues,
                                                    mode='u',
                                                    insertMax=False,
                                                    preInset = f_factor,
                                                    postInset = -f_factor,
                                                    curvesCreate=True,
                                                    curvesConnect=True,
                                                    connectionPoints=connectionPoints,
                                                    offset=offset)
                    ml_shapes = cgmMeta.validateObjListArg(l_curves)
                    
                elif mode == 'limbHandle':#================================================================
                    if targets:
                        ml_fkJoints = ml_targets
                    else:
                        ml_fkJoints = mRigNull.msgList_get('fkJoints',asMeta=True)
                        
                    if len(ml_fkJoints)<2:
                        return log.error("|{0}| >> Need at least two targets".format(_str_func))                
                    
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
                            CORERIG.shapeParent_in_place(l_mainCurves[0], crv, False)
                            
                        ml_shapes.append(cgmMeta.validateObjArg(l_mainCurves[0]))                    
                elif mode == 'simpleCast':#================================================================
                    if targets:
                        ml_fkJoints = ml_targets
                    else:
                        ml_fkJoints = mRigNull.msgList_get('fkJoints',asMeta=True)
                        
                    #if len(ml_fkJoints)<2:
                        #return log.error("|{0}| >> Need at least two targets".format(_str_func))                
                    
                    #...Get our vectors...
                    """
                    l_vectors = []
                    for i,mObj in enumerate(ml_fkJoints[:-1]):
                        l_vectors.append(  MATH.get_vector_of_two_points(mObj.p_position, ml_fkJoints[i+1].p_position) )
                    l_vectors.append(  MATH.get_vector_of_two_points(ml_fkJoints[-2].p_position, ml_fkJoints[-1].p_position) )
                    l_vectors.append( l_vectors[-1])#...add it again"""
                    
                    
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
                            log.warning("|{0}| >> frameHandle. Hit fail {1} | {2}".format(_str_func,i,l_failSafes[i]))                                            
                            _v = l_failSafes[i]
                        l_uValues.append( _v )
                        

                
                    
                    ml_shapes = []
                    _add = f_factor/2
                    
                    for i,v in enumerate(l_uValues):
                        l_mainCurves = []
                        log.debug("|{0}| >> {1} | {2} ...".format(_str_func,i,v))
                        
                        #if v == l_uValues[-2]:
                            #log.debug("|{0}| >> {1} | Last one...".format(_str_func,i))
                            #_add = - _add
                        pos_jnt = ml_fkJoints[i].p_position
                        baseCrv = mc.duplicateCurve("{0}.u[{1}]".format(str_meshShape,v), ch = 0, rn = 0, local = 0)[0]
                        DIST.offsetShape_byVector(baseCrv,offset,pos_jnt,component='cv')
                        l_mainCurves.append(baseCrv)
                        
                        endCrv = mc.duplicateCurve("{0}.u[{1}]".format(str_meshShape,v+(_add *2)), ch = 0, rn = 0, local = 0)[0]
                        #endCrv = mc.duplicateCurve("{0}.u[{1}]".format(str_meshShape,l_uValues[i+1]-_add), ch = 0, rn = 0, local = 0)[0]
                        DIST.offsetShape_byVector(endCrv,offset,pos_jnt,component='cv')
                        
                        l_mainCurves.append(endCrv)
                        
                        
                        log.debug("|{0}| >> {1} | Making connectors".format(_str_func,i))
                        d_epPos = {}
                    
                        for i,crv in enumerate(l_mainCurves):
                            _l = CURVES.getUSplitList(crv,connectionPoints,rebuild=True,rebuildSpans=30)[:-1]
                    
                            for ii,p in enumerate(_l):
                                if not d_epPos.get(ii):
                                    d_epPos[ii] = []
                                _l = d_epPos[ii]
                                _l.append(p)
                    
                        for k,points in d_epPos.iteritems():
                            try:
                                crv_connect = CURVES.create_fromList(posList=points)
                                l_mainCurves.append(crv_connect)
                            except Exception,err:
                                print err

                        for crv in l_mainCurves[1:]:
                            CORERIG.shapeParent_in_place(l_mainCurves[0], crv, False)
                            
                        ml_shapes.append(cgmMeta.validateObjArg(l_mainCurves[0]))
                        
                elif mode == 'singleCast':#================================================================
                    if targets:
                        ml_fkJoints = ml_targets
                    else:
                        ml_fkJoints = mRigNull.msgList_get('fkJoints',asMeta=True)
                        
                    #if len(ml_fkJoints)<2:
                        #return log.error("|{0}| >> Need at least two targets".format(_str_func))                
                    
                    #...Get our vectors...
                    """
                    l_vectors = []
                    for i,mObj in enumerate(ml_fkJoints[:-1]):
                        l_vectors.append(  MATH.get_vector_of_two_points(mObj.p_position, ml_fkJoints[i+1].p_position) )
                    l_vectors.append(  MATH.get_vector_of_two_points(ml_fkJoints[-2].p_position, ml_fkJoints[-1].p_position) )
                    l_vectors.append( l_vectors[-1])#...add it again"""
                    
                    
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
                            log.warning("|{0}| >> frameHandle. Hit fail {1} | {2}".format(_str_func,i,l_failSafes[i]))                                            
                            _v = l_failSafes[i]
                        l_uValues.append( _v )

                    ml_shapes = []
                    _add = f_factor/2
                    
                    for i,v in enumerate(l_uValues):
                        l_mainCurves = []
                        log.debug("|{0}| >> {1} | {2} ...".format(_str_func,i,v))
                        
                        #if v == l_uValues[-2]:
                            #log.debug("|{0}| >> {1} | Last one...".format(_str_func,i))
                            #_add = - _add
                        pos_jnt = ml_fkJoints[i].p_position
                        baseCrv = mc.duplicateCurve("{0}.u[{1}]".format(str_meshShape,v), ch = 0, rn = 0, local = 0)[0]
                        DIST.offsetShape_byVector(baseCrv,offset,pos_jnt,component='cv')
                        l_mainCurves.append(baseCrv)
                            
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
                            CORERIG.shapeParent_in_place(l_mainCurves[0], crv, False)
                            
                        mCrv = cgmMeta.validateObjArg(l_mainCurves[0])
                        mCrv.rename('shapeCast_{0}'.format(i))
                        ml_shapes.append(mCrv)                   

                elif mode in ['limbSegmentHandle','limbSegmentHandleBack']:#=============================================================
                    if targets:
                        ml_fkJoints = ml_targets
                    else:
                        ml_fkJoints = mRigNull.msgList_get('fkJoints',asMeta=True)

                    #if len(ml_fkJoints)<2:
                        #return log.error("|{0}| >> Need at least two ik joints".format(_str_func))
                    
                    for mObj in ml_targets:
                        str_orientation = self.d_orientation['str']
                        l_shapes = []
                        
                        dist = offset * 5
                        pos_obj = mObj.p_position
                        for i,axis in enumerate([str_orientation[1], str_orientation[2]]):
                            for ii,d in enumerate(['+','-']):
                                
                                if 'limbSegmentHandleBack' and i == 0 and ii == 1:
                                    continue
                                p = SNAPCALLS.get_special_pos([mObj.mNode,
                                                               str_meshShape],
                                                              'cast',axis+d)

                                crv = CURVES.create_fromName(name='semiSphere',
                                                             direction = 'z+',
                                                             size = offset)
                                l_shapes.append(crv)
                                mCrv = cgmMeta.validateObjArg(crv,'cgmObject')
                                
                                if not p:
                                    p = DIST.get_pos_by_axis_dist(mObj.mNode, axis+d, dist)
                                    
                                dist = DIST.get_distance_between_points(p, pos_obj)
                                
                                vec_tmp = MATH.get_vector_of_two_points(pos_obj,p)
                                p_use = DIST.get_pos_by_vec_dist(pos_obj,vec_tmp, dist+offset)
                                
                                mCrv.p_position = p_use
                                
                                SNAP.aim_atPoint(mCrv.mNode, pos_obj, 'z-')
                                
                                

                        for crv in l_shapes[1:]:
                            log.debug("|{0}| >> combining: {1}".format(_str_func,crv))
                            CORERIG.shapeParent_in_place(l_shapes[0], crv, False)
                            
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
                        CORERIG.shapeParent_in_place(l_mainCurves[0], crv, False)
                        
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
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err,msg=vars())



def joints_flipChainForBehavior(self,ml_chain=None):
    d_children = {}
    for mJoint in ml_chain:
        ml_end_children = mJoint.getChildren(asMeta=True)
        if ml_end_children:
            d_children[mJoint] = ml_end_children
            for mChild in ml_end_children:
                mChild.parent = False        
        mJoint.parent = False
        
    
    for mJoint in ml_chain:
        ATTR.set(mJoint.mNode,"r{0}".format(self.d_orientation['str'][2]),180)
    
    for i,mJoint in enumerate(ml_chain[1:]):
        mJoint.parent = ml_chain[i]

    JOINTS.freezeJointOrientation(ml_chain)
    
    for i,mJoint in enumerate(ml_chain):
        if d_children.get(mJoint):
            for mChild in d_children[mJoint]:
                mChild.parent = mJoint
                
def joints_mirrorChainAndConnect(self,ml_chain=None):
    _str_func = 'joints_mirrorChainAndConnect'
    mBlock = self.mBlock
    mRigNull = self.mRigNull
    ml_fkAttachJoints = mBlock.UTILS.skeleton_buildDuplicateChain(mBlock, ml_chain,
                                                                  'fkAttach',mRigNull,'fkAttachJoints',
                                                                  blockNames=False,cgmType = 'frame')

    joints_flipChainForBehavior(self, ml_chain)
    for i,mJoint in enumerate(ml_fkAttachJoints):
        log.debug("|{0}| >> Mirror connect: {1} | {2} ...".format(_str_func,i,mJoint))        
        ml_chain[i].connectChildNode(ml_fkAttachJoints[i],"fkAttach","rootJoint")
        #attributes.doConnectAttr(("%s.rotateOrder"%mJoint.mNode),("%s.rotateOrder"%ml_fkDriverJoints[i].mNode))
        cgmMeta.cgmAttr(ml_chain[i].mNode,"rotateOrder").doConnectOut("%s.rotateOrder"%ml_fkAttachJoints[i].mNode)
        mJoint.p_parent = ml_chain[i]
        
    return ml_fkAttachJoints


def mesh_proxyCreate(self, targets = None, aimVector = None, degree = 1,firstToStart=False, 
                     ballBase = True,
                     ballMode = 'asdf',
                     ballPosition = 'joint',
                     reverseNormal=False,
                     extendToStart = True,method = 'u'):
    try:
        _short = self.mBlock.mNode
        _str_func = 'mesh_proxyCreate'
        log.debug("|{0}| >>  ".format(_str_func)+ '-'*80)
        log.debug("{0}".format(self))
        
        mRigNull = self.mRigNull
        ml_shapes = []
        
        _offset = self.mBlock.atUtils('get_shapeOffset') or .25
        _dir = self.d_module.get('direction')
        if aimVector is None:
            if _dir and _dir.lower() == 'left':
                aimVector = self.d_orientation['mOrientation'].p_outNegative.p_string
            else:
                aimVector = self.d_orientation['mOrientation'].p_out.p_string
                
            
        #Get our prerig handles if none provided
        if targets is None:
            ml_targets = self.mRigNull.msgList_get('rigJoints',asMeta = True)
            if not ml_targets:
                raise ValueError,"No rigJoints connected. NO targets offered"
        else:
            ml_targets = cgmMeta.validateObjListArg(targets,'cgmObject')
        
    
        ml_handles = self.mBlock.msgList_get('templateHandles',asMeta = True)
        #l_targets = [mObj.loftCurve.mNode for mObj in ml_handles]
        #res_body = mc.loft(l_targets, o = True, d = 3, po = 0 )
        #mMesh_tmp = cgmMeta.validateObjArg(res_body[0],'cgmObject')
        #str_tmpMesh = mMesh_tmp.mNode
        
        mMesh_tmp =  self.mBlock.atUtils('get_castMesh')
        str_meshShape = mMesh_tmp.getShapes()[0]
        
        """
        if len(ml_targets)==1:
            log.debug("|{0}| >> Single mode!".format(_str_func))
            _res = mc.nurbsToPoly(mMesh_tmp.mNode, mnd=1, ch =0, f =1, pt= 1, pc= 200, chr= 0.9, ft= 0.01, mel= 0.001, d= 0.1, ut= 1, un= 3, vt= 1, vn= 3, uch= 0, ucr= 0, cht= 0.01, es= 0, ntr= 0, mrt= 0, uss= 1)

            return _res[0]"""
            
    
        
        #Process ----------------------------------------------------------------------------------
        l_newCurves = []
        l_pos = []
        str_meshShape = mMesh_tmp.getShapes()[0]
        log.debug("|{0}| >> Shape: {1}".format(_str_func,str_meshShape))
        """
        minU = ATTR.get(str_meshShape,'minValueU')
        maxU = ATTR.get(str_meshShape,'maxValueU')
        
        l_failSafes = MATH.get_splitValueList(minU,maxU,
                                              len(ml_targets))
        log.debug("|{0}| >> Failsafes: {1}".format(_str_func,l_failSafes))
        
        l_uIsos = SURF.get_dat(str_meshShape, uKnots=True)['uKnots']
        log.debug("|{0}| >> Isoparms U: {1}".format(_str_func,l_uIsos))
        """
        _cap = method.capitalize()
        minU = ATTR.get(str_meshShape,'minValue{0}'.format(_cap))
        maxU = ATTR.get(str_meshShape,'maxValue{0}'.format(_cap))
        
        l_failSafes = MATH.get_splitValueList(minU,maxU,
                                              len(ml_targets))
        log.debug("|{0}| >> Failsafes: {1}".format(_str_func,l_failSafes))
        
        if method == 'u':
            l_uIsos = SURF.get_dat(str_meshShape, uKnots=True)['uKnots']
        else:
            l_uIsos = SURF.get_dat(str_meshShape, vKnots=True)['vKnots']
            
        log.debug("|{0}| >> Isoparms {2}: {1}".format(_str_func,l_uIsos,_cap))        
        
        l_uValues = []
        str_start = False
        l_sets = []
        #First loop through and get our base U Values for each point
        for i,mTar in enumerate(ml_targets):
            j = mTar.mNode
            _d = RAYS.cast(str_meshShape,j,aimVector)
            l_pos.append(mTar.p_position)
            log.debug("|{0}| >> Casting {1} ...".format(_str_func,j))
            #cgmGEN.log_info_dict(_d,j)
            if not _d:
                log.debug("|{0}| >> Using failsafe value for: {1}".format(_str_func,j))
                _v = l_failSafes[i]
            else:
                if method == 'v':
                    _v = _d['uvsRaw'][str_meshShape][0][1]
                else:
                    _v = _d['uvsRaw'][str_meshShape][0][0]
                    
                
            log.debug("|{0}| >> v: {1} ...".format(_str_func,_v))
            
            l_uValues.append(_v)
            
        _b_singleMode =False
        if len(l_uValues) < 2:
            l_uValues.append(maxU)
            _b_singleMode = True
            
        for i,v in enumerate(l_uValues):
            _l = [v]
            
            for uKnot in l_uIsos:
                if uKnot > v:
                    if v == l_uValues[-1]:
                        if uKnot < maxU:
                            _l.append(uKnot)
                    elif uKnot < l_uValues[i+1]:
                        _l.append(uKnot)
                    
            if v == l_uValues[-1]:
                _l.append(maxU)
            else:
                _l.append(l_uValues[i+1])
                
            if i == 0 and extendToStart:
                _l.insert(0,minU)
                
            l_sets.append(_l)
    
            
            #>>For each v value, make a new curve ---------------------------------------------------------
            #duplicateCurve -ch 1 -rn 0 -local 0  "loftedSurface2.u[0.724977270271534]"
            #l_uValues.append(_v)
            #crv = mc.duplicateCurve("{0}.u[{1}]".format(str_meshShape,_v), ch = 0, rn = 0, local = 0)
            #log.debug("|{0}| >> created: {1} ...".format(_str_func,crv))        
            #l_newCurves.append(crv[0])
            #if mTar == ml_targets[-1]:
            #    crv = mc.duplicateCurve("{0}.u[{1}]".format(str_meshShape,maxU), ch = 0, rn = 0, local = 0)
            #    l_newCurves.append(crv[0])
                
            #str_start = crv = mc.duplicateCurve("{0}.u[{1}]".format(str_meshShape,0),
            #                                    ch = 0, rn = 0, local = 0)[0]
    
        l_newCurves = []
        d_curves = {}
        def getCurve(uValue,l_curves):
            _crv = d_curves.get(uValue)
            if _crv:return _crv
            _crv = mc.duplicateCurve("{0}.{2}[{1}]".format(str_meshShape,uValue,method), ch = 0, rn = 0, local = 0)[0]
            d_curves[uValue] = _crv
            log.debug("|{0}| >> created: {1} ...".format(_str_func,_crv))        
            l_curves.append(_crv)
            return _crv
        
        _degree = 1
        if self.mBlock.loftDegree:
            _degree = 3
            
        #>>Reloft those sets of curves and cap them ------------------------------------------------------------
        log.debug("|{0}| >> Create new mesh objs.".format(_str_func))
        l_new = []
        _len_targets = len(ml_targets)
        for i,uSet in enumerate(l_sets):
            if i  and _b_singleMode:
                log.debug("|{0}| >> SINGLE MODE".format(_str_func))                
                break
            
            log.debug("|{0}| >> {1} | u's: {2}".format(_str_func,i,uSet))
            """
            if i == 0 and str_start:
                _pair = [str_start,c,l_newCurves[i+1]]
            else:
                _pair = [c,l_newCurves[i+1]]"""
            
            _loftCurves = [getCurve(uValue, l_newCurves) for uValue in uSet]
            
            _mesh = create_loftMesh(_loftCurves, name="{0}_{1}".format('test',i), degree=_degree,divisions=1)
            log.debug("|{0}| >> mesh created...".format(_str_func))                            
            CORERIG.match_transform(_mesh,ml_targets[i])
            if reverseNormal:
                mc.polyNormal(_mesh, normalMode = 0, userNormalMode=1,ch=0)
            
            if ballBase and i != 0:
                log.debug("|{0}| >> ball started...".format(_str_func))
                CORERIG.match_transform(_loftCurves[0],ml_targets[i])
                TRANS.pivots_recenter(_loftCurves[0])
                
                
                if ballMode == 'loft':
                    root = mc.duplicate(_loftCurves[0])[0]
                    try:
                        _planar = mc.planarSrf(_loftCurves[0],ch=0,d=3,ko=0,rn=0,po=0)[0]
                        vecRaw = SURF.get_uvNormal(_planar,.5,.5)
                        vec = [-v for v in vecRaw]
                        log.debug("|{0}| >> vector: {1}".format(_str_func,vec))                                        
                        p1 = mc.pointOnSurface(_planar,parameterU=.5,parameterV=.5,position=True)#l_pos[i]                    
                    except Exception,err:
                        log.debug(err)
                        try:
                            vec
                            log.debug("|{0}| >> surf fail. Using last vector: {1}".format(_str_func,vec))
                        except:
                            if i:
                                vec = MATH.get_vector_of_two_points(l_pos[i],l_pos[i-1])
                            else:
                                vec =MATH.get_vector_of_two_points(l_pos[i+1],l_pos[i])
                                
                            log.debug("|{0}| >> Using last vector: {1}".format(_str_func,vec))
                        p1 = l_pos[i]                    
                        
                    p2 = l_pos[i-1]
                    pClose = DIST.get_closest_point(ml_targets[i].mNode, _loftCurves[0])[0]
                    dClose = DIST.get_distance_between_points(p1,pClose)
                    d2 = DIST.get_distance_between_points(p1,p2)
                    
                    #planarSrf -ch 1 -d 3 -ko 0 -tol 0.01 -rn 0 -po 0 "duplicatedCurve40";
                    #vecRaw = mc.pointOnSurface(_planar,parameterU=.5,parameterV=.5,normalizedNormal=True)
    
                    
                    #vec = _resClosest['normal']
                    
                    """
                    if uSet == l_sets[-1]:
                        vec = MATH.get_vector_of_two_points(p1,p2)                    
                    else:
                        vec = MATH.get_vector_of_two_points(p1,l_pos[i-1])"""                
                        #vec = MATH.get_vector_of_two_points(l_pos[i+1],p1)
                        
                    #dMax = min([dClose,_offset*10])
                    dMax = (mc.arclen(root)/3.14)/3
                    
                    #dMax = dClose * .5#_offset *10
                    pSet1 = DIST.get_pos_by_vec_dist(p1,vec,dMax * .5)                
                    pSet2 = DIST.get_pos_by_vec_dist(p1,vec,dMax * .85)
                    pSet3 = DIST.get_pos_by_vec_dist(p1,vec,dMax)
                    
                    
                    #DIST.offsetShape_byVector(root,-_offset)
                    ATTR.set(root,'scale',.9)                                        
                    mid1 = mc.duplicate(root)[0]
                    ATTR.set(mid1,'scale',.7)
                    mid2 = mc.duplicate(root)[0]
                    ATTR.set(mid2,'scale',.5)                
                    end = mc.duplicate(root)[0]
                    ATTR.set(end,'scale',.1)
                    
                    #DIST.offsetShape_byVector(end,-_offset)
                    
                    TRANS.position_set(mid1,pSet1)
                    TRANS.position_set(mid2,pSet2)
                    TRANS.position_set(end,pSet3)
                    
                    #now loft new mesh...
                    _loftTargets = [end,mid2,mid1,root]
                    #if cgmGEN.__mayaVersion__ in [2018]:
                        #_loftTargets.reverse()
                        
                    _meshEnd = create_loftMesh(_loftTargets, name="{0}_{1}".format('test',i),
                                               degree=1,divisions=1)
                    
                    mc.polyNormal(_meshEnd, normalMode = 0, userNormalMode=1,ch=0)
                    
                    _mesh = mc.polyUnite([_mesh,_meshEnd], ch=False )[0]
                    mc.delete([end,mid1,mid2,root])
                    try:mc.delete(_planar)
                    except:pass
                else:
                
                    #TRANS.orient_set(_sphere[0], ml_targets[i].p_orient)
                    if ballPosition == 'joint':
                        p2 = DIST.get_closest_point(ml_targets[i].mNode, _loftCurves[0])[0]
                        p1 = ml_targets[i].p_position
                        d1 = DIST.get_distance_between_points(p1,p2)
                        
                        try:p1_2 = ml_targets[i+1].p_position
                        except:p1_2 = ml_targets[i-1].p_position
                        
                        d2 = DIST.get_distance_between_points(p1,p1_2)
                        d2 = min([d1,d2])
                        
                        #d_offset = d1 - _offset
                        #log.debug("{0} : {1}".format(d1,d_offset))
                        _sphere = mc.polySphere(axis = [0,0,1],
                                                radius = d1*.5,
                                                subdivisionsX = 10,
                                                subdivisionsY = 10)
                        #_sphere = mc.polyCylinder(axis = [0,0,1],
                        #                          radius = d1,
                        #                          height = d2,
                        #                          subdivisionsX = 1,
                        #                          subdivisionsY = 1)                    
                        #TRANS.scale_to_boundingBox(_sphere[0], [d1*1.75,d1*1.75,d2])
                        
                        SNAP.go(_sphere[0],ml_targets[i].mNode,True,True)
                        
                    else:
                        _sphere = mc.polySphere(axis = [1,0,0], radius = 1, subdivisionsX = 10, subdivisionsY = 10)                    
                        _bb_size = SNAPCALLS.get_axisBox_size(_loftCurves[0])
                        _size = [_bb_size[0],_bb_size[1],MATH.average(_bb_size)]
                        _size = [v*.8 for v in _size]
                        SNAP.go(_sphere[0],_loftCurves[0],pivot='bb')
                        TRANS.scale_to_boundingBox(_sphere[0], _size)
                        SNAP.go(_sphere[0],ml_targets[i].mNode,False,True)
                    
                    _mesh = mc.polyUnite([_mesh,_sphere[0]], ch=False )[0]
                    
            #_mesh = mc.polyUnite([_mesh,_sphere[0]], ch=False )[0]
            #mc.polyNormal(_mesh,setUserNormal = True)
                
            CORERIG.match_transform(_mesh,ml_targets[i])
            l_new.append(_mesh)
            log.debug("|{0}| >> ball done...".format(_str_func))                
        
        #...clean up 
        mc.delete(l_newCurves)# + [str_tmpMesh]
        mMesh_tmp.delete()
        
        if str_start:
            mc.delete(str_start)
        #>>Parent to the joints ----------------------------------------------------------------- 
        return l_new
    except Exception,err:
        cgmGEN.cgmExceptCB(Exception,err,msg=vars())









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
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err)


check_nameMatches = RIGGEN.check_nameMatches
#...just linking for now because I want to only check against asset names in future and not scene wide


    