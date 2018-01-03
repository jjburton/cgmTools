"""
------------------------------------------
cgm.core.mrs.blocks.simple.torso
Author: Josh Burton
email: jjburton@cgmonks.com

Website : http://www.cgmonks.com
------------------------------------------

================================================================
"""
# From Python =============================================================
import copy
import re
import pprint
import time
import os

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

# From Maya =============================================================
import maya.cmds as mc

# From Red9 =============================================================
from Red9.core import Red9_Meta as r9Meta
#r9Meta.cleanCache()#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< TEMP!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

import cgm.core.cgm_General as cgmGEN

from cgm.core.rigger import ModuleShapeCaster as mShapeCast

import cgm.core.cgmPy.os_Utils as cgmOS
import cgm.core.cgmPy.path_Utils as cgmPATH
import cgm.core.mrs.assets as MRSASSETS
path_assets = cgmPATH.Path(MRSASSETS.__file__).up().asFriendly()

import cgm.core.mrs.lib.ModuleControlFactory as MODULECONTROL
reload(MODULECONTROL)
import cgm.core.lib.math_utils as MATH
import cgm.core.lib.transform_utils as TRANS
import cgm.core.lib.distance_utils as DIST
import cgm.core.lib.attribute_utils as ATTR
import cgm.core.tools.lib.snap_calls as SNAPCALLS
import cgm.core.classes.NodeFactory as NODEFACTORY
from cgm.core import cgm_RigMeta as cgmRigMeta



#Prerig handle making. refactor to blockUtils
import cgm.core.lib.snap_utils as SNAP
import cgm.core.lib.rayCaster as RAYS
import cgm.core.lib.rigging_utils as CORERIG
import cgm.core.lib.curve_Utils as CURVES
import cgm.core.rig.constraint_utils as RIGCONSTRAINT
import cgm.core.lib.constraint_utils as CONSTRAINT
import cgm.core.lib.position_utils as POS
import cgm.core.rig.joint_utils as JOINT
import cgm.core.rig.ik_utils as IK
import cgm.core.mrs.lib.block_utils as BLOCKUTILS


#from cgm.core.lib import curve_Utils as CURVES
#import cgm.core.lib.rigging_utils as CORERIG
#from cgm.core.lib import snap_utils as SNAP
#import cgm.core.classes.NodeFactory as NODEFACTORY
#import cgm.core.lib.distance_utils as DIST
#import cgm.core.lib.position_utils as POS
#import cgm.core.rig.constraint_utils as RIGCONSTRAINT
#import cgm.core.lib.constraint_utils as CONSTRAINT
#import cgm.core.lib.locator_utils as LOC
#import cgm.core.lib.shape_utils as SHAPES
#import cgm.core.mrs.lib.block_utils as BLOCKUTILS
#import cgm.core.mrs.lib.builder_utils as BUILDERUTILS

#for m in DIST,POS,MATH,CONSTRAINT,LOC,BLOCKUTILS,BUILDERUTILS,CORERIG,RAYS,JOINT,RIGCONSTRAINT:
#    reload(m)
    
# From cgm ==============================================================
from cgm.core import cgm_Meta as cgmMeta

#=============================================================================================================
#>> Block Settings
#=============================================================================================================
__version__ = 'alpha.12222017'
__autoTemplate__ = False
__dimensions = [15.2, 23.2, 19.7]
__menuVisible__ = True
__baseSize__ = 1,1,10

#These are our base dimensions. In this case it is for human


#>>>Attrs ----------------------------------------------------------------------------------------------------
_l_coreNames = ['segment']

l_attrsStandard = ['side',
                   'baseUp',
                   'baseAim',
                   'position',
                   'hasRootJoint',
                   #'proxyShape',
                   'loftSides',
                   'loftDegree',
                   'loftSplit',
                   'buildIK',
                   #'customStartOrientation',
                   'moduleTarget',]

d_attrsToMake = {'proxyShape':'cube:sphere:cylinder',
                 #'proxyType':'base:geo',
                 'numControls':'int',
                 'numJoints':'int'}

d_defaultSettings = {'version':__version__,
                     'baseSize':MATH.get_space_value(__dimensions[1]),
                     'numControls': 3,
                     'loftSides': 10,
                     'loftSplit':1,
                     'loftDegree':'cubic',                     
                     'numJoints':5,
                     'attachPoint':'base',}
                     #'proxyShape':'cube',}
                     #'proxyType':'geo'}

d_wiring_prerig = {'msgLinks':['moduleTarget','prerigNull','prerigLoftMesh','noTransformNull'],
                   'msgLists':['prerigHandles']}
d_wiring_template = {'msgLinks':['templateNull','templateLoftMesh',],
                     'msgLists':['templateHandles']}

#Skeletal stuff ------------------------------------------------------------------------------------------------
d_skeletonSetup = {'mode':'curveCast',
                   'targetsMode':'prerigHandles',
                   'helperUp':'z-',
                   'countAttr':'neckJoints',
                   'targets':'jointHelper'}

#d_preferredAngles = {'head':[0,-10, 10]}#In terms of aim up out for orientation relative values, stored left, if right, it will invert
#d_rotationOrders = {'head':'yxz'}

#=============================================================================================================
#>> Define
#=============================================================================================================
def define(self):
    _short = self.mNode
    ATTR.set_min(_short, 'numControls', 1)
    ATTR.set_min(_short, 'loftSides', 3)
    ATTR.set_min(_short, 'loftSplit', 1)
    
    
#=============================================================================================================
#>> Template
#=============================================================================================================    

def template(self):
    _str_func = 'template'
    log.debug("|{0}| >>  {1}".format(_str_func,self)+ '-'*80)
    
    _short = self.p_nameShort
    
    _side = 'center'
    if self.getMayaAttr('side'):
        _side = self.getEnumValueString('side')
        
    _l_basePos = self.datList_get('basePos') or [(0,0,0)]
    _baseUp = self.baseUp
    _baseSize = self.baseSize
    _baseAim = self.baseAim
    _size_width = _baseSize[0]#...x width
    
    #Generate more posData if necessary...
    if not len(_l_basePos)>1:
        log.debug("|{0}| >> Generating more pos dat".format(_str_func))
        _end = DIST.get_pos_by_vec_dist(_l_basePos[0], _baseAim, max(_baseSize))
        _l_basePos.append(_end)
    
    #Create temple Null  ==================================================================================
    mTemplateNull = self.atUtils('templateNull_verify')
    
    #Our main rigBlock shape =================================================================================
    mHandleFactory = self.asHandleFactory()

    #Handles ==================================================================================================
    log.debug("|{0}| >> handles...".format(_str_func)) 
    md_handles = {}
    ml_handles = []
    md_loftHandles = {}
    ml_loftHandles = []
    
    for i,n in enumerate(['start','end']):
        log.debug("|{0}| >> {1}:{2}...".format(_str_func,i,n)) 
        mHandle = mHandleFactory.buildBaseShape('sphere', _size_width, shapeDirection = 'y+')
        
        mHandle.p_parent = mTemplateNull
        
        self.copyAttrTo('cgmName',mHandle.mNode,'cgmName',driven='target')
        mHandle.doStore('cgmType','blockHandle')
        mHandle.doStore('cgmNameModifier',n)
        mHandle.doName()
        
        #Convert to loft curve setup ----------------------------------------------------
        mHandleFactory.setHandle(mHandle.mNode)
        #mHandleFactory = self.asHandleFactory(mHandle.mNode)
        mLoftCurve = mHandleFactory.rebuildAsLoftTarget('circle', _size_width, shapeDirection = 'y+',rebuildHandle = False)
        
        mc.makeIdentity(mHandle.mNode,a=True, s = True)#...must freeze scale once we're back parented and positioned
        
        #mHandle.setAttrFlags(['rotate','tx'])
        #mc.transformLimits(mHandle.mNode,  tz = [-.25,.25], etz = [1,1], ty = [.1,1], ety = [1,0])
        #mTopLoftCurve = mHandle.loftCurve
        
        mHandleFactory.color(mHandle.mNode)
        #CORERIG.colorControl(mHandle.mNode,_side,'main',transparent = True)
        
        mHandle.p_position = _l_basePos[i]
        
        md_handles[n] = mHandle
        ml_handles.append(mHandle)
        
        md_loftHandles[n] = mLoftCurve                
        ml_loftHandles.append(mLoftCurve)
        
        mBaseAttachGroup = mHandle.doGroup(True, asMeta=True,typeModifier = 'attach')
        
    #>>> Aim loft curves ==========================================================================================        
    mStartLoft = md_loftHandles['start']
    mEndLoft = md_loftHandles['end']
    
    mStartAimGroup = mStartLoft.doGroup(True,asMeta=True,typeModifier = 'aim')
    mEndAimGroup = mEndLoft.doGroup(True,asMeta=True,typeModifier = 'aim')        
    
    mc.aimConstraint(ml_handles[1].mNode, mStartAimGroup.mNode, maintainOffset = False,
                     aimVector = [0,1,0], upVector = [1,0,0], worldUpObject = ml_handles[0].mNode, #skip = 'z',
                     worldUpType = 'objectrotation', worldUpVector = [1,0,0])        
    mc.aimConstraint(ml_handles[0].mNode, mEndAimGroup.mNode, maintainOffset = False,
                     aimVector = [0,-1,0], upVector = [1,0,0], worldUpObject = ml_handles[-1].mNode,
                     worldUpType = 'objectrotation', worldUpVector = [1,0,0])             
    
    
    #>>> Connections ==========================================================================================
    self.msgList_connect('templateHandles',[mObj.mNode for mObj in ml_handles])

    
    #>>Loft Mesh ==================================================================================================
    targets = [mObj.mNode for mObj in ml_loftHandles]
    
    self.atUtils('create_templateLoftMesh',targets,self,
                 mTemplateNull,'numControls',
                 baseName = self.cgmName)
    
    
    """
    BLOCKUTILS.create_templateLoftMesh(self,targets,mBaseLoftCurve,
                                       mTemplateNull,'numControls',
                                       baseName = _l_baseNames[1])"""
    
   
    

    

    #>> Base Orient Helper ==================================================================================================
    mHandleFactory = self.asHandleFactory(md_handles['start'].mNode)

    mBaseOrientCurve = mHandleFactory.addOrientHelper(baseSize = _size_width,
                                                      shapeDirection = 'z-',
                                                      setAttrs = {#'rz':90,
                                                                  'ty':_size_width * .25,
                                                                  'tz':- _size_width})

    self.copyAttrTo('cgmName',mBaseOrientCurve.mNode,'cgmName',driven='target')
    mBaseOrientCurve.doName()    
    mBaseOrientCurve.p_parent = mStartAimGroup
    #mBaseOrientCurve.resetAttrs()
    mBaseOrientCurve.setAttrFlags(['rz','rx','translate','scale','v'])
    mHandleFactory.color(mBaseOrientCurve.mNode,controlType='sub')
    #CORERIG.colorControl(mBaseOrientCurve.mNode,_side,'sub')          
    mc.select(cl=True)    


    return True


#=============================================================================================================
#>> Prerig
#=============================================================================================================
def prerig(self):
    try:
        _str_func = 'prerig'
        _short = self.p_nameShort
        _side = self.atUtils('get_side')
        log.debug("|{0}| >>  {1}".format(_str_func,self)+ '-'*80)
        
        self.atUtils('module_verify')
        
        log.info("|{0}| >> [{1}] | side: {2}".format(_str_func,_short, _side))   
        
        #Create some nulls Null  ==================================================================================
        mPrerigNull = self.atUtils('prerigNull_verify')
        mNoTransformNull = self.atUtils('noTransformNull_verify')
        
        #mNoTransformNull = BLOCKUTILS.noTransformNull_verify(self)
    
        #> Get our stored dat ==================================================================================================
        mHandleFactory = self.asHandleFactory()   
        mTemplateMesh = self.getMessage('templateLoftMesh',asMeta=True)[0]
        
        #Get positions
        #DIST.get_pos_by_axis_dist(obj, axis)
        
        
        ml_templateHandles = self.msgList_get('templateHandles')        
        mStartHandle = ml_templateHandles[0]    
        mEndHandle = ml_templateHandles[-1]    
        mOrientHelper = mStartHandle.orientHelper
        
        ml_handles = [mStartHandle]
        ml_jointHandles = []        
    
        _size = MATH.average(mHandleFactory.get_axisBox_size(mStartHandle.mNode))
        #DIST.get_bb_size(mStartHandle.loftCurve.mNode,True)[0]
        _sizeSub = _size * .5    
        _vec_root_up = ml_templateHandles[0].orientHelper.getAxisVector('z-')
        
        
        #NECK build =========================================================================================
        _pos_start = mStartHandle.p_position
        _pos_end = mEndHandle.p_position 
        _vec = MATH.get_vector_of_two_points(_pos_start, _pos_end)
        _offsetDist = DIST.get_distance_between_points(_pos_start,_pos_end) / (self.numControls - 1)
        _l_pos = [ DIST.get_pos_by_vec_dist(_pos_start, _vec, (_offsetDist * i)) for i in range(self.numControls-1)] + [_pos_end]
        
        
        
        
        #Linear track curve ----------------------------------------------------------------------
        _linearCurve = mc.curve(d=1,p=[_pos_start,_pos_end])
        mLinearCurve = cgmMeta.validateObjArg(_linearCurve,'cgmObject')
    
        l_clusters = []
        _l_clusterParents = [mStartHandle,mEndHandle]
        for i,cv in enumerate(mLinearCurve.getComponents('cv')):
            _res = mc.cluster(cv, n = 'test_{0}_cluster'.format(_l_clusterParents[i].p_nameShort))
            TRANS.parent_set( _res[1], _l_clusterParents[i].getMessage('loftCurve')[0])
            l_clusters.append(_res)
        
        pprint.pprint(l_clusters)
        
        mLinearCurve.parent = mNoTransformNull
        #mLinearCurve.inheritsTransform = False      
        
        
        #Tmp loft mesh -------------------------------------------------------------------
        _l_targets = [mObj.loftCurve.mNode for mObj in [mStartHandle,mEndHandle]]
    
        _res_body = mc.loft(_l_targets, o = True, d = 3, po = 0 )
        _str_tmpMesh =_res_body[0]
        
        l_scales = []
        
        for mHandle in mStartHandle, mEndHandle:
            ml_jointHandles.append(self.asHandleFactory(mHandle.mNode).addJointHelper(baseSize = _sizeSub))
            l_scales.append(mHandle.scale)
            mHandle.scale = 1,1,1
            

        
        #Sub handles... ------------------------------------------------------------------------------------
        for i,p in enumerate(_l_pos[1:-1]):
            #mHandle = mHandleFactory.buildBaseShape('circle', _size, shapeDirection = 'y+')
            mHandle = cgmMeta.cgmObject(name = 'handle_{0}'.format(i))
            _short = mHandle.mNode
            ml_handles.append(mHandle)
            mHandle.p_position = p
            SNAP.aim_atPoint(_short,_l_pos[i+2],'y+', 'z-', mode='vector', vectorUp = _vec_root_up)
            
            #...Make our curve
            _d = RAYS.cast(_str_tmpMesh, _short, 'z+')
            pprint.pprint(_d)
            log.debug("|{0}| >> Casting {1} ...".format(_str_func,_short))
            #cgmGEN.log_info_dict(_d,j)
            _v = _d['uvs'][_str_tmpMesh][0][0]
            log.debug("|{0}| >> v: {1} ...".format(_str_func,_v))
        
            #>>For each v value, make a new curve -----------------------------------------------------------------        
            #duplicateCurve -ch 1 -rn 0 -local 0  "loftedSurface2.u[0.724977270271534]"
            _crv = mc.duplicateCurve("{0}.u[{1}]".format(_str_tmpMesh,_v), ch = 0, rn = 0, local = 0)
            log.debug("|{0}| >> created: {1} ...".format(_str_func,_crv))  
            
            CORERIG.shapeParent_in_place(_short, _crv, False)
            
            #self.copyAttrTo(_baseNameAttrs[1],mHandle.mNode,'cgmName',driven='target')
            self.copyAttrTo('cgmName',mHandle.mNode,'cgmName',driven='target')
            
            mHandle.doStore('cgmType','blockHandle')
            mHandle.doStore('cgmIterator',i)
            mHandle.doName()
            
            mHandle.p_parent = mPrerigNull
            
            mGroup = mHandle.doGroup(True,True,asMeta=True,typeModifier = 'master')
            _vList = DIST.get_normalizedWeightsByDistance(mGroup.mNode,[mStartHandle.mNode,mEndHandle.mNode])
            #_point = mc.pointConstraint([mStartHandle.mNode,mEndHandle.mNode],mGroup.mNode,maintainOffset = True)#Point contraint loc to the object
            _scale = mc.scaleConstraint([mStartHandle.mNode,mEndHandle.mNode],mGroup.mNode,maintainOffset = False)#Point contraint loc to the object
            reload(CURVES)
            mLoc = mGroup.doLoc()
            mLoc.parent = mNoTransformNull
            #mLoc.inheritsTransform = False
    
            CURVES.attachObjToCurve(mLoc.mNode, mLinearCurve.mNode)
            _point = mc.pointConstraint([mLoc.mNode],mGroup.mNode,maintainOffset = True)#Point contraint loc to the object
            
            for c in [_scale]:
                CONSTRAINT.set_weightsByDistance(c[0],_vList)
            
            #Convert to loft curve setup ----------------------------------------------------
            mHandleFactory = self.asHandleFactory(mHandle.mNode)
            
            #mc.makeIdentity(mHandle.mNode,a=True, s = True)#...must freeze scale once we're back parented and positioned
            
            mHandleFactory.rebuildAsLoftTarget('self', _size, shapeDirection = 'y+')
            ml_jointHandles.append(mHandleFactory.addJointHelper(baseSize = _sizeSub))
            #mRootCurve.setAttrFlags(['rotate','tx','tz'])
            #mc.transformLimits(mRootCurve.mNode,  tz = [-.25,.25], etz = [1,1], ty = [.1,1], ety = [1,0])
            #mTopLoftCurve = mRootCurve.loftCurve
            
            CORERIG.colorControl(mHandle.mNode,_side,'sub',transparent = True)        
            #LOC.create(position = p)
        
        ml_handles.append(mEndHandle)
        self.msgList_connect('prerigHandles', ml_handles,)
        mc.delete(_res_body)
        
        #Push scale back...
        for i,mHandle in enumerate([mStartHandle, mEndHandle]):
            mHandle.scale = l_scales[i]
        
        #Template Loft Mesh -------------------------------------
        mTemplateLoft = self.getMessage('templateLoftMesh',asMeta=True)[0]        
        for s in mTemplateLoft.getShapes(asMeta=True):
            s.overrideDisplayType = 1       
            
        
        #Aim the segment
        for i,mHandle in enumerate(ml_handles):
            if i > 0 and i < len(ml_handles) - 1:
                mMasterGroup = mHandle.getMessage('masterGroup',asMeta = True)[0]
                mAimForward = mHandle.doCreateAt()
                mAimForward.parent = mMasterGroup            
                mAimForward.doStore('cgmTypeModifier','forward')
                mAimForward.doStore('cgmType','aimer')
                mAimForward.doName()
                
                mAimBack = mHandle.doCreateAt()
                mAimBack.parent = mMasterGroup                        
                mAimBack.doStore('cgmTypeModifier','back')
                mAimBack.doStore('cgmType','aimer')
                mAimBack.doName()
                
                mAimGroup = mHandle.doGroup(True,asMeta=True,typeModifier = 'aim')
                
                if i == 1:
                    if len(ml_handles) <=3:
                        s_targetForward = mEndHandle.mNode
                    else:
                        s_targetForward = ml_handles[i+1].getMessage('masterGroup')[0]
                    s_targetBack = mStartHandle.mNode
                elif i == len(ml_handles) -1:
                    s_targetForward = ml_handles[i+1].getMessage('masterGroup')[0]
                    s_targetBack = ml_handles[i-1].getMessage('masterGroup')[0]
                else:
                    s_targetForward = mEndHandle.mNode
                    s_targetBack = ml_handles[i-1].getMessage('masterGroup')[0]
                    
                mc.aimConstraint(s_targetForward, mAimForward.mNode, maintainOffset = False, #skip = 'z',
                                 aimVector = [0,1,0], upVector = [1,0,0], worldUpObject = mOrientHelper.mNode,
                                 worldUpType = 'objectrotation', worldUpVector = [0,0,-1])            
                mc.aimConstraint(s_targetBack, mAimBack.mNode, maintainOffset = False, #skip = 'z',
                                 aimVector = [0,-1,0], upVector = [1,0,0], worldUpObject = mOrientHelper.mNode,
                                 worldUpType = 'objectrotation', worldUpVector = [0,0,-1])  
                
                mc.orientConstraint([mAimForward.mNode, mAimBack.mNode], mAimGroup.mNode, maintainOffset = True)
                
                #mc.aimConstraint(ml_handles[i+1].mNode, mAimGroup.mNode, maintainOffset = False, #skip = 'z',
                #                 aimVector = [0,1,0], upVector = [1,0,0], worldUpObject = self.mNode,
                #                 worldUpType = 'objectrotation', worldUpVector = [1,0,0])             
                
            
            mLoftCurve = mHandle.loftCurve
                    

        
        #>>Loft Mesh ==================================================================================================
        targets = [mObj.loftCurve.mNode for mObj in ml_handles]        
        
        self.atUtils('create_prerigLoftMesh',
                     targets,
                     mPrerigNull,
                     'numControls',                     
                     'loftSplit',
                     polyType='nurbs',
                     baseName = self.cgmName )
        
        """
        BLOCKUTILS.create_prerigLoftMesh(self,targets,
                                         mPrerigNull,
                                         'loftSplit',
                                         'neckControls',
                                         polyType='nurbs',
                                         baseName = _l_baseNames[1] )     
        """
        for t in targets:
            ATTR.set(t,'v',0)        
        
        
        #>>Joint placers ==================================================================================================    
        #Joint placer aim....
        for i,mHandle in enumerate(ml_handles):
            mJointHelper = mHandle.jointHelper
            mLoftCurve = mJointHelper.loftCurve
            
            if not mLoftCurve.getMessage('aimGroup'):
                mLoftCurve.doGroup(True,asMeta=True,typeModifier = 'aim')
                 
            mAimGroup = mLoftCurve.getMessage('aimGroup',asMeta=True)[0]
        
            if mHandle == ml_handles[-1]:
                mc.aimConstraint(ml_handles[-2].mNode, mAimGroup.mNode, maintainOffset = False,
                                 aimVector = [0,-1,0], upVector = [1,0,0], worldUpObject = mHandle.mNode, #skip = 'z',
                                 worldUpType = 'objectrotation', worldUpVector = [1,0,0])        
            else:
                mc.aimConstraint(ml_handles[i+1].mNode, mAimGroup.mNode, maintainOffset = False, #skip = 'z',
                                 aimVector = [0,1,0], upVector = [1,0,0], worldUpObject = mHandle.mNode,
                                 worldUpType = 'objectrotation', worldUpVector = [1,0,0])            
    
        #Joint placer loft....
        targets = [mObj.jointHelper.loftCurve.mNode for mObj in ml_handles]
        
        
        self.msgList_connect('jointHelpers',targets)
        
        self.atUtils('create_jointLoft',
                     targets,
                     mPrerigNull,
                     'numJoints',
                     baseName = self.cgmName )        
        
        """
        BLOCKUTILS.create_jointLoft(self,targets,
                                    mPrerigNull,'neckJoints',
                                    baseName = _l_baseNames[1] )
        """
        for t in targets:
            ATTR.set(t,'v',0)
            #ATTR.set_standardFlags(t,[v])
        
        #Close out ==================================================================================================
        self.noTransformNull.v = False
        cgmGEN.func_snapShot(vars())    
        return True
    
    except Exception,err:cgmGEN.cgmException(Exception,err)
    
def prerigDelete(self):
    if self.getMessage('templateLoftMesh'):
        mTemplateLoft = self.getMessage('templateLoftMesh',asMeta=True)[0]
        for s in mTemplateLoft.getShapes(asMeta=True):
            s.overrideDisplayType = 2

def build_skeleton(self, forceNew = True):
    _short = self.mNode
    _str_func = 'build_skeleton'
    log.debug("|{0}| >>  {1}".format(_str_func,self)+ '-'*80)
    
    _radius = .25
    ml_joints = []
    
    mModule = self.moduleTarget
    if not mModule:
        raise ValueError,"No moduleTarget connected"
    mRigNull = mModule.rigNull
    if not mRigNull:
        raise ValueError,"No rigNull connected"
    
    ml_prerigHandles = self.msgList_get('prerigHandles',asMeta = True)
    if not ml_prerigHandles:
        raise ValueError,"No prerigHandles connected"
    
    #>> If skeletons there, delete ----------------------------------------------------------------------------------- 
    _bfr = mRigNull.msgList_get('moduleJoints',asMeta=True)
    if _bfr:
        log.debug("|{0}| >> Joints detected...".format(_str_func))            
        if forceNew:
            log.debug("|{0}| >> force new...".format(_str_func))                            
            mc.delete([mObj.mNode for mObj in _bfr])
        else:
            return _bfr
    
    #_baseNameAttrs = ATTR.datList_getAttrs(self.mNode,'baseNames')    

    log.debug("|{0}| >> creating...".format(_str_func))
    
    _d = self.atBlockUtils('skeleton_getCreateDict', self.numJoints)

    mOrientHelper = ml_prerigHandles[0].orientHelper
    
    ml_joints = JOINT.build_chain(_d['positions'], parent=True, worldUpAxis= mOrientHelper.getAxisVector('z-'))
    
    self.copyAttrTo('cgmName',ml_joints[0].mNode,'cgmName',driven='target')
    

    for i,mJnt in enumerate(ml_joints):
        mJnt.addAttr('cgmIterator',i + 1)
        mJnt.doName()        
    
    ml_joints[0].parent = False
    
    for mJnt in ml_joints:
        mJnt.displayLocalAxis = 1
        mJnt.radius = _radius

    mRigNull.msgList_connect('moduleJoints', ml_joints)
    #cgmGEN.func_snapShot(vars())    
    self.atBlockUtils('skeleton_connectToParent')
    
    return ml_joints


#=============================================================================================================
#>> rig
#=============================================================================================================
#NOTE - self here is a rig Factory....

#d_preferredAngles = {'default':[0,-10, 10]}#In terms of aim up out for orientation relative values, stored left, if right, it will invert
d_preferredAngles = {'out':10}
d_rotateOrders = {'default':'yxz'}

#Rig build stuff goes through the rig build factory ------------------------------------------------------
@cgmGEN.Timer
def rig_skeleton(self):
    _short = self.d_block['shortName']
    _str_func = 'rig_skeleton'
    log.debug("|{0}| >>  {1}".format(_str_func,self)+ '-'*80)
        
    mBlock = self.mBlock
    mRigNull = self.mRigNull
    ml_jointsToConnect = []
    ml_jointsToHide = []
    ml_joints = mRigNull.msgList_get('moduleJoints')
    self.d_joints['ml_moduleJoints'] = ml_joints
    
    reload(BLOCKUTILS)
    BLOCKUTILS.skeleton_pushSettings(ml_joints,self.d_orientation['str'],
                                     self.d_module['mirrorDirection'],
                                     d_rotateOrders, d_preferredAngles)
    
    
    log.info("|{0}| >> rig chain...".format(_str_func))              
    ml_rigJoints = BLOCKUTILS.skeleton_buildDuplicateChain(ml_joints, 'rig', self.mRigNull,'rigJoints')
    

    #...fk chain -----------------------------------------------------------------------------------------------
    log.info("|{0}| >> fk_chain".format(_str_func))
    ml_fkJoints = BLOCKUTILS.skeleton_buildHandleChain(self.mBlock,'fk','fkJoints')
    
    #l_baseNameAttrs = ATTR.datList_getAttrs(mBlock.mNode,'baseNames')
    #We then need to name our core joints to pass forward:
    #mBlock.copyAttrTo(l_baseNameAttrs[0],ml_fkJoints[-1].mNode,'cgmName',driven='target')
    #mBlock.copyAttrTo(l_baseNameAttrs[1],ml_fkJoints[0].mNode,'cgmName',driven='target')
    

    mBlock.copyAttrTo('cgmName',ml_fkJoints[0].mNode,'cgmName',driven='target')

    if len(ml_fkJoints) > 2:
        for i,mJnt in enumerate(ml_fkJoints):
            mJnt.doStore('cgmIterator',i+1)
        #ml_fkJoints[0].doStore('cgmIterator','base')
    
    for mJnt in ml_fkJoints:
        mJnt.doName()
        
    ml_jointsToHide.extend(ml_fkJoints)


    #...fk chain -----------------------------------------------------------------------------------------------
    if mBlock.buildIK:
        log.info("|{0}| >> buildIK on. Building blend and IK chains...".format(_str_func))  
        ml_blendJoints = BLOCKUTILS.skeleton_buildHandleChain(self.mBlock,'blend','blendJoints')
        ml_ikJoints = BLOCKUTILS.skeleton_buildHandleChain(self.mBlock,'ik','ikJoints')
        ml_jointsToConnect.extend(ml_ikJoints)
        ml_jointsToHide.extend(ml_blendJoints)
        
        BLOCKUTILS.skeleton_pushSettings(ml_ikJoints,self.d_orientation['str'],
                                         self.d_module['mirrorDirection'],
                                         d_rotateOrders, d_preferredAngles)        
        
    #cgmGEN.func_snapShot(vars())        
    
    if mBlock.numControls > 1:
        log.info("|{0}| >> Handles...".format(_str_func))            
        ml_segmentHandles = BLOCKUTILS.skeleton_buildHandleChain(self.mBlock,'handle','handleJoints',clearType=True)
        if mBlock.buildIK:
            for i,mJnt in enumerate(ml_segmentHandles):
                mJnt.parent = ml_blendJoints[i]
        else:
            for i,mJnt in enumerate(ml_segmentHandles):
                mJnt.parent = ml_fkJoints[i]
                
    """
    if mBlock.buildIK:
        log.info("|{0}| >> IK Drivers...".format(_str_func))            
        ml_baseIKDrivers = BLOCKUTILS.skeleton_buildDuplicateChain(ml_segmentHandles, None, mRigNull,'baseIKDrivers', cgmType = 'baseIKDriver', indices=[0,-1])
        for mJnt in ml_baseIKDrivers:
            mJnt.parent = False
        ml_jointsToConnect.extend(ml_baseIKDrivers)"""
        
    
    if mBlock.numJoints > mBlock.numControls:
        log.info("|{0}| >> segment necessary...".format(_str_func))
            
        ml_segmentChain = BLOCKUTILS.skeleton_buildDuplicateChain(ml_joints, None, mRigNull,'segmentJoints', cgmType = 'segJnt')
        for i,mJnt in enumerate(ml_rigJoints):
            mJnt.parent = ml_segmentChain[i]
            mJnt.connectChildNode(ml_segmentChain[i],'driverJoint','sourceJoint')#Connect
            
        ml_jointsToHide.extend(ml_segmentChain)
        
    #...joint hide -----------------------------------------------------------------------------------
    for mJnt in ml_jointsToHide:
        try:
            mJnt.drawStyle =2
        except:
            mJnt.radius = .00001
            
    #...connect... 
    self.fnc_connect_toRigGutsVis( ml_jointsToConnect )        
    
    cgmGEN.func_snapShot(vars())     
    return

@cgmGEN.Timer
def rig_shapes(self):
    _short = self.d_block['shortName']
    _str_func = 'rig_shapes'
    log.debug("|{0}| >>  {1}".format(_str_func,self)+ '-'*80)
    
    #_str_func = '[{0}] > rig_shapes'.format(_short)
    log.info("|{0}| >> ...".format(_str_func))  
    
    ml_prerigHandleTargets = self.mBlock.atBlockUtils('prerig_getHandleTargets')

    ml_fkJoints = self.mRigNull.msgList_get('fkJoints')    
    mIKEnd = ml_prerigHandleTargets[-1]
    
    mBlock = self.mBlock
    ml_prerigHandles = mBlock.msgList_get('prerigHandles')
    
    _side = mBlock.atUtils('get_side')
    _short_module = self.mModule.mNode
    
    mHandleFactory = mBlock.asHandleFactory()
    mOrientHelper = ml_prerigHandles[0].orientHelper
    #_size = 5
    _size = MATH.average(mHandleFactory.get_axisBox_size(ml_prerigHandles[0].mNode))
    
    ml_joints = self.d_joints['ml_moduleJoints']
    
    
    #Root =============================================================================
    log.debug("|{0}| >> settings...".format(_str_func))
    
    mRootHandle = ml_prerigHandles[0]
    mRoot = ml_joints[0].doCreateAt()
    mRootCrv = cgmMeta.validateObjArg(CURVES.create_fromName('sphere', _size),'cgmObject',setClass=True)
    mRootCrv.doSnapTo(mRootHandle)

    #SNAP.go(mRootCrv.mNode, ml_joints[0].mNode,position=False)

    CORERIG.shapeParent_in_place(mRoot.mNode,mRootCrv.mNode, False)

    ATTR.copy_to(_short_module,'cgmName',mRoot.mNode,driven='target')
    mRoot.doStore('cgmTypeModifier','root')
    mRoot.doName()
    
    mHandleFactory.color(mRoot.mNode, controlType = 'sub')
    
    self.mRigNull.connectChildNode(mRoot,'rigRoot','rigNull')#Connect
    

    #Settings =============================================================================
    log.debug("|{0}| >> settings...".format(_str_func))
    
    
    settings = CURVES.create_fromName('gear',_size * .75,'x+')
    mSettings = cgmMeta.validateObjArg(settings,'cgmObject',setClass=True)
    mSettings.p_position = mOrientHelper.getPositionByAxisDistance('z-', _size * 2)
    SNAP.aim_atPoint(mSettings,mOrientHelper.p_position,
                     mode = 'vector',
                     vectorUp= mOrientHelper.getAxisVector('z-'))
    ATTR.copy_to(_short_module,'cgmName',mSettings.mNode,driven='target')
    mSettings.doStore('cgmTypeModifier','settings')
    mSettings.doName()
    #CORERIG.colorControl(mSettings.mNode,_side,'sub')
    mHandleFactory.color(mSettings.mNode, controlType = 'sub')

    self.mRigNull.connectChildNode(mSettings,'settings','rigNull')#Connect        
    
    
    #Direct Controls =============================================================================
    log.debug("|{0}| >> direct...".format(_str_func))                
    ml_rigJoints = self.mRigNull.msgList_get('rigJoints')
    
    if len(ml_rigJoints) < 3:
        _size_direct = DIST.get_distance_between_targets([mObj.mNode for mObj in ml_rigJoints], average=True)        
        d_direct = {'size':_size_direct}
    else:
        d_direct = {'size':None}
        
    ml_directShapes = self.atBuilderUtils('shapes_fromCast',
                                          ml_rigJoints,
                                          mode ='direct',**d_direct)
                                                                                                                                                            #offset = 3

    for i,mCrv in enumerate(ml_directShapes):
        mHandleFactory.color(mCrv.mNode, controlType = 'sub')
        CORERIG.shapeParent_in_place(ml_rigJoints[i].mNode,mCrv.mNode, False, replaceShapes=True)
        for mShape in ml_rigJoints[i].getShapes(asMeta=True):
            mShape.doName()

    for mJnt in ml_rigJoints:
        try:
            mJnt.drawStyle =2
        except:
            mJnt.radius = .00001    
            
            
    #baseIKDrivers =============================================================================================    
    #ml_baseIKDrivers = self.mRigNull.msgList_get('baseIKDrivers')
    if mBlock.buildIK:
        log.debug("|{0}| >> ikHandle...".format(_str_func))

        crv = CURVES.create_fromName('cube',MATH.average(mHandleFactory.get_axisBox_size(ml_prerigHandles[-1].mNode)))
        mIKCrv = cgmMeta.validateObjArg(crv,'cgmObject',setClass=True)
        mIKCrv.doSnapTo(ml_joints[-1])
        mHandleFactory.color(mIKCrv.mNode, controlType = 'main')
        
        ATTR.copy_to(_short_module,'cgmName',mIKCrv.mNode,driven='target')
        mIKCrv.doStore('cgmTypeModifier','ik')
        mIKCrv.doName()
        
        self.mRigNull.connectChildNode(mIKCrv,'controlIK','rigNull')#Connect        
                
            
    #Handles =============================================================================================    
    ml_handleJoints = self.mRigNull.msgList_get('handleJoints')
    if ml_handleJoints:
        log.debug("|{0}| >> Found Handle joints...".format(_str_func))
        l_uValues = MATH.get_splitValueList(.1,.9, len(ml_handleJoints))
        ml_handleShapes = self.atBuilderUtils('shapes_fromCast',
                                              mode ='segmentHandle',
                                              uValues = l_uValues,)
                                                                                                                                                                #offset = 3
        for i,mCrv in enumerate(ml_handleShapes):
            mHandleFactory.color(mCrv.mNode, controlType = 'sub')            
            CORERIG.shapeParent_in_place(ml_handleJoints[i].mNode,mCrv.mNode, False, replaceShapes=True)
            for mShape in ml_handleJoints[i].getShapes(asMeta=True):
                mShape.doName()
    
    #FK =============================================================================================    
    log.debug("|{0}| >> FK...".format(_str_func))
    ml_fkShapes = self.atBuilderUtils('shapes_fromCast',  ml_prerigHandles)
    for i,mCrv in enumerate(ml_fkShapes):
        mJnt = ml_fkJoints[i]
        #CORERIG.match_orientation(mCrv.mNode,mJnt.mNode)
        
        mHandleFactory.color(mCrv.mNode, controlType = 'main')        
        CORERIG.shapeParent_in_place(mJnt.mNode,mCrv.mNode, False, replaceShapes=True)
        
        l_lolis = []
        l_starts = []
        text_crv = CURVES.create_text(mJnt.cgmIterator,_size /3)
        mText = cgmMeta.cgmObject(text_crv)
        log.debug("|{0}| >> Text Curve: {1}|{2}".format(_str_func,i,mText))
        
        for axis in ['x+','y+','x-','y-']:
            pos_jnt = mJnt.p_position
            pos_axis = SNAPCALLS.get_special_pos(mJnt.mNode,'axisBox',axis)
            pos_dist = DIST.get_distance_between_points(pos_axis,pos_jnt)
            pos = mJnt.getPositionByAxisDistance(axis, pos_dist * 1.5)
            mNewText = mText.doDuplicate(po=False)
            mNewText.p_position = pos
            mc.select(cl=True)
            
            SNAP.aim_atPoint(mNewText,pos_jnt,'y-',
                             mode = 'vector',
                             vectorUp= mJnt.getAxisVector('z+'))            
            #p_end = DIST.get_closest_point(mJnt.mNode, ball)[0]
            #p_start = mJnt.getPositionByAxisDistance(axis, _size * .25)
            #l_starts.append(p_start)
            #line = mc.curve (d=1, ep = [p_start,p_end], os=True)
            l_lolis.extend([mNewText.mNode])
            mHandleFactory.color(mNewText.mNode, controlType = 'sub')
        
        mText.delete()
        #mFK = ml_fkJoints[-1]
        CORERIG.shapeParent_in_place(mJnt,l_lolis,False)
        
        #CORERIG.shapeParent_in_place(ml_fkJoints[i].mNode,mCrv.mNode, False, replaceShapes=True)
        for mShape in ml_fkJoints[i].getShapes(asMeta=True):
            mShape.doName()
    
    return
    
    



@cgmGEN.Timer
def rig_controls(self):
    _short = self.d_block['shortName']
    _str_func = 'rig_controls'
    log.debug("|{0}| >>  {1}".format(_str_func,self)+ '-'*80)
    
    mBlock = self.mBlock
    mRigNull = self.mRigNull
    ml_controlsAll = []#we'll append to this list and connect them all at the end
    mRootParent = self.mDeformNull
    mSettings = mRigNull.settings
    
    # Drivers ==============================================================================================
    log.debug("|{0}| >> Attr drivers...".format(_str_func))    
    if mBlock.buildIK:
        log.debug("|{0}| >> Build IK drivers...".format(_str_func))
        mPlug_FKIK = cgmMeta.cgmAttr(mSettings.mNode,'FKIK',attrType='float',minValue=0,maxValue=1,lock=False,keyable=True)
    
    #>> vis Drivers ================================================================================================	
    mPlug_visSub = self.atBuilderUtils('build_visSub')
    
    mPlug_visRoot = cgmMeta.cgmAttr(mSettings,'visRoot', value = True, attrType='bool', defaultValue = False,keyable = False,hidden = False)
    mPlug_visDirect = cgmMeta.cgmAttr(mSettings,'visDirect', value = True, attrType='bool', defaultValue = False,keyable = False,hidden = False)
    
    #if self.mBlock.headAim:        
        #mPlug_aim = cgmMeta.cgmAttr(mSettings.mNode,'blend_aim',attrType='float',minValue=0,maxValue=1,lock=False,keyable=True)
        
    
    #Root/Settings ==============================================================================================
    log.debug("|{0}| >> Root...".format(_str_func))
    
    if not mRigNull.getMessage('rigRoot'):
        raise ValueError,"No rigRoot found"
    
    mRoot = mRigNull.rigRoot
    log.debug("|{0}| >> Found rigRoot : {1}".format(_str_func, mRoot))
    
    
    _d = MODULECONTROL.register(mRoot,
                                addDynParentGroup = True,
                                mirrorSide= self.d_module['mirrorDirection'],
                                mirrorAxis="translateX,rotateY,rotateZ",
                                makeAimable = True)
    
    mRoot = _d['mObj']
    mRoot.masterGroup.parent = mRootParent
    mRootParent = mRoot#Change parent going forward...
    ml_controlsAll.append(mRoot)
    
    for mShape in mRoot.getShapes(asMeta=True):
        ATTR.connect(mPlug_visRoot.p_combinedShortName, "{0}.overrideVisibility".format(mShape.mNode))
            
    #FK controls ==============================================================================================
    log.debug("|{0}| >> FK Controls...".format(_str_func))
    ml_fkJoints = self.mRigNull.msgList_get('fkJoints')
    
    ml_fkJoints[0].parent = mRoot
    ml_controlsAll.extend(ml_fkJoints)
    
    for i,mObj in enumerate(ml_fkJoints):
        d_buffer = MODULECONTROL.register(mObj,
                                          mirrorSide= self.d_module['mirrorDirection'],
                                          mirrorAxis="translateX,rotateY,rotateZ",
                                          makeAimable = True)

        mObj = d_buffer['instance']
        ATTR.set_hidden(mObj.mNode,'radius',True)
            
    
    #ControlIK ========================================================================================
    mControlIK = False
    if mRigNull.getMessage('controlIK'):
        mControlIK = mRigNull.controlIK
        log.debug("|{0}| >> Found controlIK : {1}".format(_str_func, mControlIK))
        
        _d = MODULECONTROL.register(mControlIK,
                                    addSpacePivots = 2,
                                    addDynParentGroup = True, addConstraintGroup=False,
                                    mirrorSide= self.d_module['mirrorDirection'],
                                    mirrorAxis="translateX,rotateY,rotateZ",
                                    makeAimable = True)
        
        mControlIK = _d['mObj']
        mControlIK.masterGroup.parent = mRootParent
        ml_controlsAll.append(mControlIK)            
    

    #>> settings ========================================================================================
    log.info("|{0}| >> Settings : {1}".format(_str_func, mSettings))
    
    MODULECONTROL.register(mSettings)
    
    ml_blendJoints = self.mRigNull.msgList_get('blendJoints')
    if ml_blendJoints:
        mSettings.masterGroup.parent = ml_blendJoints[0]
    else:
        mSettings.masterGroup.parent = ml_fkJoints[0]
    
    #>> handleJoints ========================================================================================
    ml_handleJoints = self.mRigNull.msgList_get('handleJoints')
    if ml_handleJoints:
        log.debug("|{0}| >> Found Handle Joints...".format(_str_func))
        
        ml_controlsAll.extend(ml_handleJoints)
        
        for i,mObj in enumerate(ml_handleJoints):
            d_buffer = MODULECONTROL.register(mObj,
                                              mirrorSide= self.d_module['mirrorDirection'],
                                              mirrorAxis="translateX,rotateY,rotateZ",
                                              makeAimable = False)
    
            mObj = d_buffer['instance']
            ATTR.set_hidden(mObj.mNode,'radius',True)
            
            for mShape in mObj.getShapes(asMeta=True):
                ATTR.connect(mPlug_visSub.p_combinedShortName, "{0}.overrideVisibility".format(mShape.mNode))
        
            
    #>> Direct Controls ========================================================================================
    log.debug("|{0}| >> Direct controls...".format(_str_func))
    
    ml_rigJoints = self.mRigNull.msgList_get('rigJoints')
    ml_controlsAll.extend(ml_rigJoints)
    
    for i,mObj in enumerate(ml_rigJoints):
        d_buffer = MODULECONTROL.register(mObj,
                                          typeModifier='direct',
                                          mirrorSide= self.d_module['mirrorDirection'],
                                          mirrorAxis="translateX,rotateY,rotateZ",
                                          makeAimable = False)

        mObj = d_buffer['instance']
        ATTR.set_hidden(mObj.mNode,'radius',True)        
        if mObj.hasAttr('cgmIterator'):
            ATTR.set_hidden(mObj.mNode,'cgmIterator',True)        
            
        for mShape in mObj.getShapes(asMeta=True):
            ATTR.connect(mPlug_visDirect.p_combinedShortName, "{0}.overrideVisibility".format(mShape.mNode))
                

    ml_controlsAll = self.atBuilderUtils('register_mirrorIndices', ml_controlsAll)
    mRigNull.msgList_connect('controlsAll',ml_controlsAll)
    mRigNull.moduleSet.extend(ml_controlsAll)
    
    return 

    try:#>>>> IK Segments =============================================================================	 
        for i_obj in ml_shapes_segmentIK:
            d_buffer = mControlFactory.registerControl(i_obj,addExtraGroups=1,typeModifier='segIK',
                                                       mirrorSide=mi_go._str_mirrorDirection, mirrorAxis="translateX,rotateY,rotateZ",	                                               
                                                       setRotateOrder=2)       
            i_obj = d_buffer['instance']
            i_obj.masterGroup.parent = mi_go._i_deformNull.mNode
            mPlug_result_moduleSubDriver.doConnectOut("%s.visibility"%i_obj.mNode)	    

        mi_go._i_rigNull.msgList_connect('segmentHandles',ml_shapes_segmentIK,'rigNull')
        ml_controlsAll.extend(ml_shapes_segmentIK)	
    except Exception,error:raise Exception,"IK Segments! | error: {0}".format(error)


@cgmGEN.Timer
def rig_segments(self):
    _short = self.d_block['shortName']
    _str_func = 'rig_neckSegment'
    log.debug("|{0}| >>  {1}".format(_str_func,self)+ '-'*80)
    

    
    mBlock = self.mBlock
    mRigNull = self.mRigNull
    ml_rigJoints = mRigNull.msgList_get('rigJoints')
    ml_segJoints = mRigNull.msgList_get('segmentJoints')
    mModule = self.mModule
    mRoot = mRigNull.rigRoot
    
    if len(ml_rigJoints)<2:
        log.info("|{0}| >> Not enough rig joints for setup".format(_str_func))                      
        return True    
    
    mRootParent = self.mDeformNull
    ml_handleJoints = mRigNull.msgList_get('handleJoints')
    
    
    #>> Ribbon setup ========================================================================================
    log.debug("|{0}| >> Ribbon setup...".format(_str_func))
    reload(IK)
    #mSurf = IK.ribbon([mObj.mNode for mObj in ml_rigJoints], baseName = mBlock.cgmName, connectBy='constraint', msgDriver='masterGroup', moduleInstance = mModule)
    mSurf = IK.ribbon([mObj.mNode for mObj in ml_segJoints],
                      baseName = mBlock.cgmName,
                      connectBy='constraint',
                      moduleInstance = mModule)
    
    #Setup the aim along the chain -----------------------------------------------------------------------------
    for i,mJnt in enumerate(ml_rigJoints):
        mAimGroup = mJnt.doGroup(True,asMeta=True,typeModifier = 'aim')
        v_aim = [0,0,1]
        if mJnt == ml_rigJoints[-1]:
            s_aim = ml_rigJoints[-2].masterGroup.mNode
            v_aim = [0,0,-1]
        else:
            s_aim = ml_rigJoints[i+1].masterGroup.mNode
    
        mc.aimConstraint(s_aim, mAimGroup.mNode, maintainOffset = True, #skip = 'z',
                         aimVector = v_aim, upVector = [1,0,0], worldUpObject = mJnt.masterGroup.mNode,
                         worldUpType = 'objectrotation', worldUpVector = [1,0,0])    
    
    mSkinCluster = cgmMeta.validateObjArg(mc.skinCluster ([mHandle.mNode for mHandle in ml_handleJoints],
                                                          mSurf.mNode,
                                                          tsb=True,
                                                          maximumInfluences = 2,
                                                          normalizeWeights = 1,dropoffRate=2.5),
                                          'cgmNode',
                                          setClass=True)

    mSkinCluster.doStore('cgmName', mSurf.mNode)
    mSkinCluster.doName()    
    
    cgmGEN.func_snapShot(vars())

    ml_segJoints[0].parent = mRoot

    
@cgmGEN.Timer
def rig_frame(self):
    try:
        _short = self.d_block['shortName']
        _str_func = 'rig_rigFrame'.format(_short)
        log.info("|{0}| >> ...".format(_str_func))  
        
        mBlock = self.mBlock
        mRigNull = self.mRigNull
        mRootParent = self.mDeformNull
        
        ml_rigJoints = mRigNull.msgList_get('rigJoints')
        ml_fkJoints = mRigNull.msgList_get('fkJoints')
        ml_handleJoints = self.mRigNull.msgList_get('handleJoints')
        ml_baseIKDrivers = self.mRigNull.msgList_get('baseIKDrivers')
        ml_blendJoints = mRigNull.msgList_get('blendJoints')
        mPlug_globalScale = self.d_module['mPlug_globalScale']
        mRoot = mRigNull.rigRoot
        
        #>> handleJoints ========================================================================================
        if ml_handleJoints:
            log.debug("|{0}| >> Handles setup...".format(_str_func))
            
            ml_handleParents = ml_fkJoints
            if ml_blendJoints:
                log.debug("|{0}| >> Handles parent: blend".format(_str_func))
                ml_handleParents = ml_blendJoints
                
            for i,mHandle in enumerate(ml_handleJoints):
                mHandle.masterGroup.parent = ml_handleParents[i]
                s_rootTarget = False
                s_targetForward = False
                s_targetBack = False
                mMasterGroup = mHandle.masterGroup
                b_first = False
                if mHandle == ml_handleJoints[0]:
                    log.debug("|{0}| >> First handle: {1}".format(_str_func,mHandle))
                    if len(ml_handleJoints) <=2:
                        s_targetForward = ml_handleParents[-1].mNode
                    else:
                        s_targetForward = ml_handleJoints[i+1].getMessage('masterGroup')[0]
                    s_rootTarget = mRoot.mNode
                    b_first = True
                    
                elif mHandle == ml_handleJoints[-1]:
                    log.debug("|{0}| >> Last handle: {1}".format(_str_func,mHandle))
                    s_rootTarget = ml_handleParents[i].mNode                
                    s_targetBack = ml_handleJoints[i-1].getMessage('masterGroup')[0]
                else:
                    log.debug("|{0}| >> Reg handle: {1}".format(_str_func,mHandle))            
                    s_targetForward = ml_handleJoints[i+1].getMessage('masterGroup')[0]
                    s_targetBack = ml_handleJoints[i-1].getMessage('masterGroup')[0]
                    
                #Decompose matrix for parent...
                mUpDecomp = cgmMeta.cgmNode(nodeType = 'decomposeMatrix')
                mUpDecomp.doStore('cgmName',ml_handleParents[i].mNode)                
                mUpDecomp.addAttr('cgmType','aimMatrix',attrType='string',lock=True)
                mUpDecomp.doName()
                
                ATTR.connect("%s.worldMatrix"%(ml_handleParents[i].mNode),"%s.%s"%(mUpDecomp.mNode,'inputMatrix'))
                
                if s_targetForward:
                    mAimForward = mHandle.doCreateAt()
                    mAimForward.parent = mMasterGroup            
                    mAimForward.doStore('cgmTypeModifier','forward')
                    mAimForward.doStore('cgmType','aimer')
                    mAimForward.doName()
                    
                    _const=mc.aimConstraint(s_targetForward, mAimForward.mNode, maintainOffset = True, #skip = 'z',
                                            aimVector = [0,0,1], upVector = [1,0,0], worldUpObject = ml_handleParents[i].mNode,
                                            worldUpType = 'vector', worldUpVector = [0,0,0])            
                    s_targetForward = mAimForward.mNode
                    ATTR.connect("%s.%s"%(mUpDecomp.mNode,"outputRotate"),"%s.%s"%(_const[0],"upVector"))                 
                    
                else:
                    s_targetForward = ml_handleParents[i].mNode
                    
                if s_targetBack:
                    mAimBack = mHandle.doCreateAt()
                    mAimBack.parent = mMasterGroup                        
                    mAimBack.doStore('cgmTypeModifier','back')
                    mAimBack.doStore('cgmType','aimer')
                    mAimBack.doName()
                    
                    _const = mc.aimConstraint(s_targetBack, mAimBack.mNode, maintainOffset = True, #skip = 'z',
                                              aimVector = [0,0,-1], upVector = [1,0,0], worldUpObject = ml_handleParents[i].mNode,
                                              worldUpType = 'vector', worldUpVector = [0,0,0])  
                    s_targetBack = mAimBack.mNode
                    ATTR.connect("%s.%s"%(mUpDecomp.mNode,"outputRotate"),"%s.%s"%(_const[0],"upVector"))                                     
                else:
                    s_targetBack = s_rootTarget
                    #ml_handleParents[i].mNode
                
                pprint.pprint([s_targetForward,s_targetBack])
                mAimGroup = mHandle.doGroup(True,asMeta=True,typeModifier = 'aim')
                
                mHandle.parent = False
                
                if b_first:
                    const = mc.orientConstraint([s_targetBack, s_targetForward], mAimGroup.mNode, maintainOffset = True)[0]
                else:
                    const = mc.orientConstraint([s_targetForward, s_targetBack], mAimGroup.mNode, maintainOffset = True)[0]
                    
    
                d_blendReturn = NODEFACTORY.createSingleBlendNetwork([mHandle.mNode,'followRoot'],
                                                                     [mHandle.mNode,'resultRootFollow'],
                                                                     [mHandle.mNode,'resultAimFollow'],
                                                                     keyable=True)
                targetWeights = mc.orientConstraint(const,q=True, weightAliasList=True,maintainOffset=True)
                #Connect                                  
                d_blendReturn['d_result1']['mi_plug'].doConnectOut('%s.%s' % (const,targetWeights[0]))
                d_blendReturn['d_result2']['mi_plug'].doConnectOut('%s.%s' % (const,targetWeights[1]))
                d_blendReturn['d_result1']['mi_plug'].p_hidden = True
                d_blendReturn['d_result2']['mi_plug'].p_hidden = True
                
                mHandle.parent = mAimGroup#...parent back
                
                if mHandle in [ml_handleJoints[0],ml_handleJoints[-1]]:
                    mHandle.followRoot = 1
                else:
                    mHandle.followRoot = .5
                    
                
                
            
            
            """
            ml_handleJoints[-1].masterGroup.parent = mHeadFK
            ml_handleJoints[0].masterGroup.parent = mRoot
            
            #Aim top to bottom ----------------------------
            mc.aimConstraint(ml_handleJoints[0].mNode,
                             ml_handleJoints[-1].masterGroup.mNode,
                             maintainOffset = True, weight = 1,
                             aimVector = self.d_orientation['vectorAimNeg'],
                             upVector = self.d_orientation['vectorUp'],
                             worldUpVector = self.d_orientation['vectorOut'],
                             worldUpObject = mTopHandleDriver.mNode,
                             worldUpType = 'objectRotation' )
            
            #Aim bottom to top ----------------------------
            mc.aimConstraint(ml_handleJoints[-1].mNode,
                             ml_handleJoints[0].masterGroup.mNode,
                             maintainOffset = True, weight = 1,
                             aimVector = self.d_orientation['vectorAim'],
                             upVector = self.d_orientation['vectorUp'],
                             worldUpVector = self.d_orientation['vectorOut'],
                             worldUpObject = ml_blendJoints[0].mNode,
                             worldUpType = 'objectRotation' )    
                             """
        
        #>> Build IK ======================================================================================
        if mBlock.buildIK:
            _ikType = mBlock.getEnumValueString('buildIK')
            log.debug("|{0}| >> IK Type: {1}".format(_str_func,_ikType))    
        
            if not mRigNull.getMessage('rigRoot'):
                raise ValueError,"No rigRoot found"
            if not mRigNull.getMessage('controlIK'):
                raise ValueError,"No controlIK found"            
            
            mIKControl = mRigNull.controlIK
            mSettings = mRigNull.settings
            ml_ikJoints = mRigNull.msgList_get('ikJoints')
            mPlug_FKIK = cgmMeta.cgmAttr(mSettings.mNode,'FKIK',attrType='float',lock=False,keyable=True)
            
            #>>> Setup a vis blend result
            mPlug_FKon = cgmMeta.cgmAttr(mSettings,'result_FKon',attrType='float',defaultValue = 0,keyable = False,lock=True,hidden=True)	
            mPlug_IKon = cgmMeta.cgmAttr(mSettings,'result_IKon',attrType='float',defaultValue = 0,keyable = False,lock=True,hidden=True)	
        
            NODEFACTORY.createSingleBlendNetwork(mPlug_FKIK.p_combinedName,
                                                 mPlug_IKon.p_combinedName,
                                                 mPlug_FKon.p_combinedName)
            #Fk...
            mPlug_FKon.doConnectOut("{0}.visibility".format(ml_fkJoints[0].masterGroup.mNode))
            
            #IK...
            mIKGroup = mRoot.doCreateAt()
            mIKGroup.doStore('cgmTypeModifier','ik')
            mIKGroup.doName()
            mIKGroup.parent = mRoot
            mIKControl.masterGroup.parent = mIKGroup
            
            mPlug_IKon.doConnectOut("{0}.visibility".format(mIKGroup.mNode))
            
            if mBlock.buildIK == 1:
                log.debug("|{0}| >> rp setup...".format(_str_func,_ikType))
                
                #Build the IK ---------------------------------------------------------------------
                _d_ik= {'globalScaleAttr':mPlug_globalScale.p_combinedName,
                        'stretch':'translate',
                        'lockMid':False,
                        'rpHandle':True,
                        'nameSuffix':'noFlip',
                        'controlObject':mIKControl.mNode,
                        'moduleInstance':self.mModule.mNode}
                mStart = ml_ikJoints[0]
                mEnd = ml_ikJoints[-1]
                _start = ml_ikJoints[0].mNode
                _end = ml_ikJoints[-1].mNode
                
                d_ikReturn = IK.handle(_start,_end,**_d_ik)
                
                #Get our no flip position-------------------------------------------------------------------------
                log.debug("|{0}| >> no flip dat...".format(_str_func))
                
                _side = mBlock.atUtils('get_side')
                _dist_ik_noFlip = DIST.get_distance_between_points(mStart.p_position,
                                                                   mEnd.p_position)
                _jointOrientation = self.d_orientation['str']
                if _side == 'left':#if right, rotate the pivots
                    pos_noFlipOffset = mStart.getPositionByAxisDistance(_jointOrientation[2]+'-',_dist_ik_noFlip)
                else:
                    pos_noFlipOffset = mStart.getPositionByAxisDistance(_jointOrientation[2]+'+',_dist_ik_noFlip)
                
                #No flip -------------------------------------------------------------------------
                log.debug("|{0}| >> no flip setup...".format(_str_func))
                
                mIKHandle = d_ikReturn['mHandle']
                ml_distHandlesNF = d_ikReturn['ml_distHandles']
                mRPHandleNF = d_ikReturn['mRPHandle']
            
                #No Flip RP handle
                mRPHandleNF.p_position = pos_noFlipOffset
            
                mRPHandleNF.doCopyNameTagsFromObject(self.mModule.mNode, ignore = ['cgmName','cgmType'])
                mRPHandleNF.addAttr('cgmName','{0}PoleVector'.format(self.d_module['partName']), attrType = 'string')
                mRPHandleNF.addAttr('cgmTypeModifier','noFlip')
                mRPHandleNF.doName()
            
                #spin
                #=========================================================================================
                log.debug("|{0}| >> spin setup...".format(_str_func))
                
                #Make a spin group
                mSpinGroup = mStart.doGroup(False,False,asMeta=True)
                mSpinGroup.doCopyNameTagsFromObject(self.mModule.mNode, ignore = ['cgmName','cgmType'])	
                mSpinGroup.addAttr('cgmName','{0}NoFlipSpin'.format(self.d_module['partName']))
                mSpinGroup.doName()
                
                mSpinGroup.parent = mRoot
            
                mSpinGroup.doGroup(True,True,typeModifier='zero')
                mRPHandleNF.parent = mSpinGroup.mNode
            
                #Setup arg
                mPlug_spin = cgmMeta.cgmAttr(mIKControl,'spin',attrType='float',keyable=True, defaultValue = 0, hidden = False)
                mPlug_spin.doConnectOut("%s.r%s"%(mSpinGroup.mNode,_jointOrientation[0]))
            
                #>>>Parent IK handles
                log.debug("|{0}| >> parent ik dat...".format(_str_func,_ikType))
                
                mIKHandle.parent = mIKControl.mNode#handle to control	
                for mObj in ml_distHandlesNF[:-1]:
                    mObj.parent = mRoot
                ml_distHandlesNF[-1].parent = mIKControl.mNode#handle to control
            
                #>>> Fix our ik_handle twist at the end of all of the parenting
                IK.handle_fixTwist(mIKHandle,_jointOrientation[0])#Fix the twist
                
                mc.orientConstraint([mIKControl.mNode], ml_ikJoints[-1].mNode, maintainOffset = True)

            elif mBlock.buildIK == 2:
                log.debug("|{0}| >> ribbon setup...".format(_str_func,_ikType))
                
            else:
                raise ValueError,"Not implemented {0} setup".format(_ikType)
            
            
            #Parent --------------------------------------------------            
            ml_blendJoints[0].parent = mRoot
            ml_ikJoints[0].parent = mIKGroup
            
            #Setup blend ----------------------------------------------------------------------------------
            RIGCONSTRAINT.blendChainsBy(ml_fkJoints,ml_ikJoints,ml_blendJoints,
                                        driver = mPlug_FKIK.p_combinedName,l_constraints=['point','orient'])            
            
        

        cgmGEN.func_snapShot(vars())
        return    
    except Exception,err:cgmGEN.cgmException(Exception,err)
    
def rig_cleanUp(self):
    _short = self.d_block['shortName']
    _str_func = 'rig_neckSegment'
    log.debug("|{0}| >>  {1}".format(_str_func,self)+ '-'*80)
    
    
    mRigNull = self.mRigNull
    mSettings = mRigNull.settings
    mRoot = mRigNull.rigRoot
    if not mRoot.hasAttr('cgmAlias'):
        mRoot.addAttr('cgmAlias','root')
        
    mRootParent = self.mDeformNull
    mMasterControl= self.d_module['mMasterControl']
    mMasterDeformGroup= self.d_module['mMasterDeformGroup']    
    mMasterNull = self.d_module['mMasterNull']
    mModuleParent = self.d_module['mModuleParent']
    mPlug_globalScale = self.d_module['mPlug_globalScale']
    
    
    ml_controlsToSetup = []
    for msgLink in ['rigJoints','controlIK']:
        ml_buffer = mRigNull.msgList_get(msgLink)
        if ml_buffer:
            log.debug("|{0}| >>  Found: {1}".format(_str_func,msgLink))            
            ml_controlsToSetup.extend(ml_buffer)
    
    #>>  DynParentGroups - Register parents for various controls ============================================
    ml_baseDynParents = []
    ml_endDynParents = [mRoot,mMasterNull.puppetSpaceObjectsGroup, mMasterNull.worldSpaceObjectsGroup]
    
    if mModuleParent:
        mi_parentRigNull = mModuleParent.rigNull
        if mi_parentRigNull.getMessage('handleIK'):
            ml_baseDynParents.append( mi_parentRigNull.handleIK )	    
        if mi_parentRigNull.getMessage('cog'):
            ml_baseDynParents.append( mi_parentRigNull.cog )
    
    #...rigjoints ----------------------------------------------------------------------------------------------
    log.debug("|{0}| >>  Direct...".format(_str_func))                
    for mObj in mRigNull.msgList_get('rigJoints'):
        log.debug("|{0}| >>  Direct: {1}".format(_str_func,mObj))                        
        ml_targetDynParents = copy.copy(ml_baseDynParents)
        ml_targetDynParents.extend(mObj.msgList_get('spacePivots',asMeta=True) or [])
        
        mParent = mObj.getParent(asMeta=True)
        if not mParent.hasAttr('cgmAlias'):
            mParent.addAttr('cgmAlias','base')
        ml_targetDynParents.append(mParent)
        
        ml_targetDynParents.extend(ml_endDynParents)
        
        mDynGroup = cgmRigMeta.cgmDynParentGroup(dynChild=mObj.mNode)
        mDynGroup.dynMode = 2
        
        for mTar in ml_targetDynParents:
            if mTar != mObj:
                mDynGroup.addDynParent(mTar)
        mDynGroup.rebuild()
        
        mDynGroup.dynFollow.p_parent = mRoot
            
    #...fk controls ----------------------------------------------------------------------------------------------
    log.debug("|{0}| >>  FK...".format(_str_func))                
    ml_fkJoints = self.mRigNull.msgList_get('fkJoints')
    ml_targetDynParents = copy.copy(ml_baseDynParents)
    
    for mObj in ml_fkJoints[:1]:
        log.debug("|{0}| >>  Direct: {1}".format(_str_func,mObj))                        
        
        mParent = mObj.getParent(asMeta=True)
        if not mParent.hasAttr('cgmAlias'):
            mParent.addAttr('cgmAlias','base')
        ml_targetDynParents.append(mParent)    
        
        ml_targetDynParents.extend(ml_endDynParents)
    
        mDynGroup = cgmRigMeta.cgmDynParentGroup(dynChild=mObj.mNode)
        mDynGroup.dynMode = 2
    
        for mTar in ml_targetDynParents:
            if mTar != mObj:
                mDynGroup.addDynParent(mTar)
        mDynGroup.rebuild()
        mDynGroup.dynFollow.p_parent = mRoot    
    
    #...fk controls ----------------------------------------------------------------------------------------------
    log.debug("|{0}| >>  Root: {1}".format(_str_func,mRoot))                
    mParent = mRoot.getParent(asMeta=True)
    ml_targetDynParents = []

    if not mParent.hasAttr('cgmAlias'):
        mParent.addAttr('cgmAlias','base')
    ml_targetDynParents.append(mParent)    
    
    ml_targetDynParents.extend(ml_baseDynParents + ml_endDynParents)

    mDynGroup = cgmRigMeta.cgmDynParentGroup(dynChild=mObj.mNode)
    mDynGroup.dynMode = 2

    for mTar in ml_targetDynParents:
        if mTar != mObj:
            mDynGroup.addDynParent(mTar)
    mDynGroup.rebuild()
    mDynGroup.dynFollow.p_parent = mRoot        
    
    
    #Close out ====================================================================================================
    mRigNull.version = self.d_block['buildVersion']
    cgmGEN.func_snapShot(vars())
    return


    #Add our parents
    mDynGroup = mHeadFK.dynParentGroup
    log.info("|{0}| >> dynParentSetup : {1}".format(_str_func,mDynGroup))  
    mDynGroup.dynMode = 2

    for o in ml_headDynParents:
        mDynGroup.addDynParent(o)
    mDynGroup.rebuild()

    mDynGroup.dynFollow.parent = mMasterDeformGroup
    
    #...headLookat ---------------------------------------------------------------------------------------
    if self.mBlock.headAim:
        log.info("|{0}| >> HeadAim setup...".format(_str_func))
        
        mPlug_aim = cgmMeta.cgmAttr(mSettings.mNode,'blend_aim',attrType='float',lock=False,keyable=True)
        
        #mHeadFKJoint = mRigNull.getMessage('fkHeadJoint', asMeta=True)[0]
        #mHeadAimJoint = mRigNull.getMessage('aimHeadJoint', asMeta=True)[0]
        #mHeadBlendJoint = mRigNull.getMessage('blendHeadJoint', asMeta=True)[0]
        #mHeadFKDynParentGroup = mHeadFK.dynParentGroup
        
        mHeadLookAt = mRigNull.headLookAt        
        mHeadLookAt.setAttrFlags(attrs='v')
        
        #...dynParentGroup...
        ml_headLookAtDynParents = copy.copy(ml_baseHeadDynParents)
        ml_headLookAtDynParents.extend(mHeadLookAt.msgList_get('spacePivots',asMeta = True))
        ml_headLookAtDynParents.append(mMasterNull.worldSpaceObjectsGroup)    
        
        ml_headDynParents.insert(0, mHeadFK)
        #mHeadFK.masterGroup.addAttr('cgmAlias','headRoot')
        
        #Add our parents...
        mDynGroup = mHeadLookAt.dynParentGroup
        log.info("|{0}| >> dynParentSetup : {1}".format(_str_func,mDynGroup))  
    
        for o in ml_headDynParents:
            mDynGroup.addDynParent(o)
        mDynGroup.rebuild()
        
    
        
    #>>  Lock and hide ======================================================================================
    
    
    #>>  Attribute defaults =================================================================================
    
    mRigNull.version = self.d_block['buildVersion']
    
    

def build_proxyMesh(self, forceNew = True):
    """
    Build our proxyMesh
    """
    _short = self.d_block['shortName']
    _str_func = '[{0}] > build_proxyMesh'.format(_short)
    log.debug("|{0}| >> ...".format(_str_func))  
    _start = time.clock()
    mBlock = self.mBlock
    mRigNull = self.mRigNull
    mSettings = mRigNull.settings
    mPuppetSettings = self.d_module['mMasterControl'].controlSettings
    
    _side = BLOCKUTILS.get_side(self.mBlock)
    ml_proxy = []
    
    ml_rigJoints = mRigNull.msgList_get('rigJoints',asMeta = True)
    if not ml_rigJoints:
        raise ValueError,"No rigJoints connected"
    
    #>> If proxyMesh there, delete ----------------------------------------------------------------------------------- 
    _bfr = mRigNull.msgList_get('proxyMesh',asMeta=True)
    if _bfr:
        log.debug("|{0}| >> proxyMesh detected...".format(_str_func))            
        if forceNew:
            log.debug("|{0}| >> force new...".format(_str_func))                            
            mc.delete([mObj.mNode for mObj in _bfr])
        else:
            return _bfr
        

    # Create ---------------------------------------------------------------------------
    ml_segProxy = cgmMeta.validateObjListArg(self.atBuilderUtils('mesh_proxyCreate', ml_rigJoints),'cgmObject')
    
    for i,mGeo in enumerate(ml_segProxy):
        mGeo.parent = ml_rigJoints[i]
        ATTR.copy_to(ml_rigJoints[0].mNode,'cgmName',mGeo.mNode,driven = 'target')
        mGeo.addAttr('cgmIterator',i+1)
        mGeo.addAttr('cgmType','proxyGeo')
        mGeo.doName()            
    
    for mProxy in ml_segProxy:
        CORERIG.colorControl(mProxy.mNode,_side,'main',transparent=False)
        
        mc.makeIdentity(mProxy.mNode, apply = True, t=1, r=1,s=1,n=0,pn=1)

        #Vis connect -----------------------------------------------------------------------
        mProxy.overrideEnabled = 1
        ATTR.connect("{0}.proxyVis".format(mPuppetSettings.mNode),"{0}.visibility".format(mProxy.mNode) )
        ATTR.connect("{0}.proxyLock".format(mPuppetSettings.mNode),"{0}.overrideDisplayType".format(mProxy.mNode) )        
        for mShape in mProxy.getShapes(asMeta=1):
            str_shape = mShape.mNode
            mShape.overrideEnabled = 0
            ATTR.connect("{0}.proxyLock".format(mPuppetSettings.mNode),"{0}.overrideDisplayTypes".format(str_shape) )
        
    mRigNull.msgList_connect('proxyMesh', ml_segProxy)

__l_rigBuildOrder__ = ['rig_skeleton',
                       'rig_shapes',
                       'rig_controls',
                       'rig_frame',
                       'rig_segments',                       
                       'rig_cleanUp']



















