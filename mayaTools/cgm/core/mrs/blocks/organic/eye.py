"""
------------------------------------------
cgm.core.mrs.blocks.organic.eye
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
from cgm.core.lib import curve_Utils as CURVES
import cgm.core.lib.rigging_utils as CORERIG
from cgm.core.lib import snap_utils as SNAP
import cgm.core.lib.attribute_utils as ATTR
import cgm.core.rig.joint_utils as JOINT
import cgm.core.classes.NodeFactory as NODEFACTORY
import cgm.core.lib.transform_utils as TRANS
import cgm.core.lib.distance_utils as DIST
import cgm.core.lib.position_utils as POS
import cgm.core.lib.math_utils as MATH
import cgm.core.rig.constraint_utils as RIGCONSTRAINT
import cgm.core.lib.constraint_utils as CONSTRAINT
import cgm.core.lib.locator_utils as LOC
import cgm.core.lib.rayCaster as RAYS
import cgm.core.lib.shape_utils as SHAPES
import cgm.core.mrs.lib.block_utils as BLOCKUTILS
import cgm.core.mrs.lib.builder_utils as BUILDERUTILS
import cgm.core.mrs.lib.shared_dat as BLOCKSHARE
import cgm.core.tools.lib.snap_calls as SNAPCALLS
import cgm.core.rig.ik_utils as IK
import cgm.core.cgm_RigMeta as cgmRIGMETA
import cgm.core.lib.nameTools as NAMETOOLS

for m in DIST,POS,MATH,IK,CONSTRAINT,LOC,BLOCKUTILS,BUILDERUTILS,CORERIG,RAYS,JOINT,RIGCONSTRAINT:
    reload(m)
    
# From cgm ==============================================================
from cgm.core import cgm_Meta as cgmMeta

#=============================================================================================================
#>> Block Settings
#=============================================================================================================
__version__ = 'alpha.1.06.27.2018'
__autoTemplate__ = False
__menuVisible__ = True

#These are our base dimensions. In this case it is for human
__dimensions_by_type = {'box':[22,22,22],
                        'human':[15.2, 23.2, 19.7]}

__l_rigBuildOrder__ = ['rig_dataBuffer',
                       'rig_skeleton',
                       'rig_shapes',
                       'rig_controls',
                       'rig_segments',
                       'rig_frame',
                       'rig_cleanUp']

d_wiring_skeleton = {'msgLinks':[],
                     'msgLists':['moduleJoints','skinJoints']}
d_wiring_prerig = {'msgLinks':['moduleTarget']}
d_wiring_template = {'msgLinks':['templateNull','eyeOrientHelper','rootHelper'],
                     }

#>>>Profiles =====================================================================================================
d_build_profiles = {}


d_block_profiles = {}



#>>>Attrs =====================================================================================================
l_attrsStandard = ['side',
                   'position',
                   'baseUp',
                   'baseAim',
                   'attachPoint',
                   'nameList',
                   'loftSides',
                   'loftDegree',
                   'loftSplit',
                   'loftShape',
                   'scaleSetup',                   
                   'numSpacePivots',
                   'scaleSetup',
                   'offsetMode',
                   'proxyDirect',
                   'settingsDirection',
                   'moduleTarget',]

d_attrsToMake = {'eyeType':'sphere:nonsphere',
                 'eyeOrb':'bool',
                 'fkSetup':'bool',
                 'setupPupil':'none:joint:blendshape',
                 'setupIris':'none:joint:blendshape',
                 'setupLid':'none:clam:full',
                 'lidJointsUpr':'int',
                 'lidJointsLwr':'int',
                 
                 
}

d_defaultSettings = {'version':__version__,
                     'nameList':['eye','eyeOrb','pupil','iris','cornea'],
                     #'baseSize':MATH.get_space_value(__dimensions[1]),
                     }

#=============================================================================================================
#>> Define
#=============================================================================================================
@cgmGEN.Timer
def define(self):
    _str_func = 'define'    
    log.debug("|{0}| >>  ".format(_str_func)+ '-'*80)
    log.debug("{0}".format(self))
    
    _short = self.mNode
    
    ATTR.set_alias(_short,'sy','blockScale')    
    self.setAttrFlags(attrs=['sx','sz','sz'])
    self.doConnectOut('sy',['sx','sz'])    
    
    ATTR.set_min(_short, 'loftSides', 3)
    ATTR.set_min(_short, 'loftSplit', 1)
    
    _shapes = self.getShapes()
    if _shapes:
        log.debug("|{0}| >>  Removing old shapes...".format(_str_func))        
        mc.delete(_shapes)
        defineNull = self.getMessage('defineNull')
        if defineNull:
            log.debug("|{0}| >>  Removing old defineNull...".format(_str_func))
            mc.delete(defineNull)
    
    _size = MATH.average(self.baseSize[1:])
    _crv = CURVES.create_fromName(name='axis3d',#'arrowsAxis', 
                                  direction = 'z+', size = _size/4)
    SNAP.go(_crv,self.mNode,)    
    CORERIG.shapeParent_in_place(self.mNode,_crv,False)
    
    mHandleFactory = self.asHandleFactory()
    self.addAttr('cgmColorLock',True,lock=True, hidden=True)
    mDefineNull = self.atUtils('stateNull_verify','define')
    
    
    #Rotate Group ==================================================================
    mRotateGroup = cgmMeta.validateObjArg(mDefineNull.doGroup(True,False,asMeta=True,typeModifier = 'rotate'),
                                          'cgmObject',setClass=True)
    mRotateGroup.p_parent = mDefineNull
    mRotateGroup.doConnectIn('rotate',"{0}.baseAim".format(_short))
    mRotateGroup.setAttrFlags()
    
    #Bounding box ==================================================================
    _bb_shape = CURVES.create_controlCurve(self.mNode,'sphere', size = 1.0, sizeMode='fixed')
    mBBShape = cgmMeta.validateObjArg(_bb_shape, 'cgmObject',setClass=True)
    mBBShape.p_parent = mDefineNull    
    mBBShape.tz = -.5
    
    CORERIG.copy_pivot(mBBShape.mNode,self.mNode)
    self.doConnectOut('baseSize', "{0}.scale".format(mBBShape.mNode))
    mHandleFactory.color(mBBShape.mNode,controlType='sub')
    mBBShape.setAttrFlags()
    
    mBBShape.doStore('cgmName', self.mNode)
    mBBShape.doStore('cgmType','bbVisualize')
    mBBShape.doName()    
    
    self.connectChildNode(mBBShape.mNode,'bbHelper')
    
    return
 
    
#=============================================================================================================
#>> Template
#=============================================================================================================

@cgmGEN.Timer
def template(self):
    _str_func = 'template'
    log.debug("|{0}| >>  ".format(_str_func)+ '-'*80)
    log.debug("{0}".format(self))
    
    _short = self.p_nameShort
    _baseNameAttrs = ATTR.datList_getAttrs(self.mNode,'nameList')
    
    #Initial checks ===============================================================================
    _side = self.UTILS.get_side(self)
    _eyeType = self.getEnumValueString('eyeType')
            
    if _eyeType not in ['sphere']:
        return log.error("|{0}| >> loft setup mode not done: {1}".format(_str_func,_loftSetup))
    
    #Get base dat =============================================================================    
    _mVectorAim = MATH.get_obj_vector(self.mNode,asEuclid=True)
    mBBHelper = self.bbHelper
    _v_range = max(TRANS.bbSize_get(self.mNode)) *2
    _bb_axisBox = SNAPCALLS.get_axisBox_size(mBBHelper.mNode, _v_range, mark=False)
    _size_width = _bb_axisBox[0]#...x width
    _pos_bbCenter = POS.get_bb_center(mBBHelper.mNode)
    
    log.debug("{0} >> axisBox size: {1}".format(_str_func,_bb_axisBox))
    log.debug("{0} >> Center: {1}".format(_str_func,_pos_bbCenter))

    #for i,p in enumerate(_l_basePos):
        #LOC.create(position=p,name="{0}_loc".format(i))
    
    mHandleFactory = self.asHandleFactory()
    
    #Create temple Null  ==================================================================================
    mTemplateNull = BLOCKUTILS.templateNull_verify(self)
    #mNoTransformNull = BLOCKUTILS.noTransformNull_verify(self,'template') 
    
    
    #Create Pivot =====================================================================================
    #loc = LOC.create(position=_pos_bbCenter,name="bbCenter_loc")
    #TRANS.parent_set(loc,mTemplateNull)
    
    crv = CURVES.create_fromName('jack', size = _size_width * .25)
    mHandleRoot = cgmMeta.validateObjArg(crv, 'cgmObject', setClass=True)
    mHandleFactory.color(mHandleRoot.mNode)
    
    #_shortHandle = mHandleRoot.mNode

    #ATTR.copy_to(self.mNode,_baseNameAttrs[i],_short, 'cgmName', driven='target')
    mHandleRoot.doStore('cgmName','eyeRoot')    
    mHandleRoot.doStore('cgmType','templateHandle')
    mHandleRoot.doName()
    
    mHandleRoot.p_position = _pos_bbCenter
    mHandleRoot.p_parent = mTemplateNull
    mHandleRoot.doGroup(True,True,asMeta=True,typeModifier = 'center')
    
    self.connectChildNode(mHandleRoot.mNode,'rootHelper','module')
    
    #Orient helper =====================================================================================
    _orientHelper = CURVES.create_fromName('arrowSingle', size = _size_width * .25)
    mShape = cgmMeta.validateObjArg(_orientHelper, mType = 'cgmObject',setClass=True)
    

    mShape.doSnapTo(self.mNode)
    mShape.p_parent = mHandleRoot
    
    mShape.tz = self.baseSizeZ / 2
    mShape.rz = 90
    
    mOrientHelper = mHandleRoot.doCreateAt()
    
    CORERIG.shapeParent_in_place(mOrientHelper.mNode, mShape.mNode,False)
    mOrientHelper.p_parent = mHandleRoot
    
    mOrientHelper.doStore('cgmName','eyeOrient')
    mOrientHelper.doStore('cgmType','templateHandle')
    mOrientHelper.doName()    
    
    self.connectChildNode(mOrientHelper.mNode,'eyeOrientHelper','module')
    mHandleFactory.color(mOrientHelper.mNode)
    
    
    if self.eyeOrb:
        pass
        """
        log.debug("|{0}| >> Eye orb setup...".format(_str_func))
        
        crv = CURVES.create_fromName('circle', size = [self.baseSizeX, self.baseSizeY, None])
        mHandleOrb = cgmMeta.validateObjArg(crv, 'cgmObject', setClass=True)
        mHandleFactory.color(mHandleOrb.mNode)
        
        #_shortHandle = mHandleRoot.mNode
        mHandleOrb.doSnapTo(self.mNode)
        mHandleOrb.p_parent = mTemplateNull
    
        #ATTR.copy_to(self.mNode,_baseNameAttrs[i],_short, 'cgmName', driven='target')
        mHandleOrb.doStore('cgmName','eyeOrb')    
        mHandleOrb.doStore('cgmType','templateHandle')
        mHandleOrb.doName()
        
        self.connectChildNode(mHandleOrb.mNode,'eyeOrbHelper','module')"""
    
    self.blockState = 'template'
    return


#=============================================================================================================
#>> Prerig
#=============================================================================================================
def prerig(self):
    _str_func = 'prerig'
    log.debug("|{0}| >>  {1}".format(_str_func,self)+ '-'*80)
    self.blockState = 'prerig'
    
    self.atUtils('module_verify')
    return

#=============================================================================================================
#>> Skeleton
#=============================================================================================================
def skeleton_check(self):
    return True

def skeleton_build(self, forceNew = True):
    _short = self.mNode
    _str_func = '[{0}] > skeleton_build'.format(_short)
    log.debug("|{0}| >> ...".format(_str_func)) 
    
    _radius = 1
    ml_joints = []
    mModule = self.moduleTarget
    
    if not mModule:
        raise ValueError,"No moduleTarget connected"
    mRigNull = mModule.rigNull
    if not mRigNull:
        raise ValueError,"No rigNull connected"
    
    mPrerigNull = self.preRigNull
    if not mPrerigNull:
        raise ValueError,"No prerig null"
    
    #>> If skeletons there, delete -------------------------------------------------------------------------- 
    _bfr = mRigNull.msgList_get('moduleJoints',asMeta=True)
    if _bfr:
        log.debug("|{0}| >> Joints detected...".format(_str_func))            
        if forceNew:
            log.debug("|{0}| >> force new...".format(_str_func))                            
            mc.delete([mObj.mNode for mObj in _bfr])
        else:
            return _bfr
        
    _baseNameAttrs = ATTR.datList_getAttrs(self.mNode,'nameList')
    _l_baseNames = ATTR.datList_get(self.mNode, 'nameList')
    
    mEyeOrb = False
    
    _d_base = self.atBlockUtils('skeleton_getNameDictBase')
    _d_base['cgmType'] = 'skinJoint'    
    pprint.pprint( _d_base )
    
    #..name --------------------------------------
    def name(mJnt,d):
        #mJnt.rename(NAMETOOLS.returnCombinedNameFromDict(d))
        for t,v in d.iteritems():
            mJnt.doStore(t,v)
        mJnt.doName()
        
    #>> Eye ===================================================================================
    log.debug("|{0}| >> Eye...".format(_str_func))
    mRootHelper = self.getMessageAsMeta('rootHelper')
    mOrientHelper = self.getMessageAsMeta('eyeOrientHelper')
    
    p = mRootHelper.p_position
    
    #...create ---------------------------------------------------------------------------
    mEyeJoint = cgmMeta.cgmObject(mc.joint (p=(p[0],p[1],p[2])))
    mEyeJoint.parent = False
    self.copyAttrTo(_baseNameAttrs[0],mEyeJoint.mNode,'cgmName',driven='target')
    
    #...orient ----------------------------------------------------------------------------
    #cgmMeta.cgmObject().getAxisVector
    CORERIG.match_orientation(mEyeJoint.mNode, mOrientHelper.mNode)
    JOINT.freezeOrientation(mEyeJoint.mNode)
    
    name(mEyeJoint,_d_base)
    ml_joints.append(mEyeJoint)
    
    mPrerigNull.connectChildNode(mEyeJoint.mNode,'eyeJoint')
    
    
    #>> Eye =================================================================================== 
    if self.eyeOrb:
        mEyeOrbJoint = mEyeJoint.doDuplicate()
        self.copyAttrTo(_baseNameAttrs[1],mEyeOrbJoint.mNode,'cgmName',driven='target')
        name(mEyeOrbJoint,_d_base)
        
        mEyeJoint.p_parent = mEyeOrbJoint
        ml_joints.append(mEyeOrbJoint)
        mPrerigNull.connectChildNode(mEyeOrbJoint.mNode,'eyeOrbJoint')
        
    mRigNull.msgList_connect('moduleJoints', ml_joints)
    
    
    return
    

    
    
    
    #>> Head ===================================================================================
    log.debug("|{0}| >> Head...".format(_str_func))
    p = POS.get( ml_prerigHandles[-1].jointHelper.mNode )
    mHeadHelper = ml_templateHandles[0].orientHelper
    
    #...create ---------------------------------------------------------------------------
    mHead_jnt = cgmMeta.cgmObject(mc.joint (p=(p[0],p[1],p[2])))
    mHead_jnt.parent = False
    #self.copyAttrTo(_baseNameAttrs[-1],mHead_jnt.mNode,'cgmName',driven='target')
    
    #...orient ----------------------------------------------------------------------------
    #cgmMeta.cgmObject().getAxisVector
    CORERIG.match_orientation(mHead_jnt.mNode, mHeadHelper.mNode)
    JOINT.freezeOrientation(mHead_jnt.mNode)
    
    #...name ----------------------------------------------------------------------------
    #mHead_jnt.doName()
    #mHead_jnt.rename(_l_namesToUse[-1])
    for k,v in _l_namesToUse[-1].iteritems():
        mHead_jnt.doStore(k,v)
    mHead_jnt.doName()
    
    if self.neckBuild:#...Neck =====================================================================
        log.debug("|{0}| >> neckBuild...".format(_str_func))
        if len(ml_prerigHandles) == 2 and self.neckJoints == 1:
            log.debug("|{0}| >> Single neck joint...".format(_str_func))
            p = POS.get( ml_prerigHandles[0].jointHelper.mNode )
            
            mBaseHelper = ml_prerigHandles[0].orientHelper
            
            #...create ---------------------------------------------------------------------------
            mNeck_jnt = cgmMeta.cgmObject(mc.joint (p=(p[0],p[1],p[2])))
            
            #self.copyAttrTo(_baseNameAttrs[0],mNeck_jnt.mNode,'cgmName',driven='target')
            
            #...orient ----------------------------------------------------------------------------
            #cgmMeta.cgmObject().getAxisVector
            TRANS.aim_atPoint(mNeck_jnt.mNode,
                              mHead_jnt.p_position,
                              'z+', 'y+', 'vector',
                              vectorUp=mHeadHelper.getAxisVector('z-'))
            JOINT.freezeOrientation(mNeck_jnt.mNode)
            
            #mNeck_jnt.doName()
            
            mHead_jnt.p_parent = mNeck_jnt
            ml_joints.append(mNeck_jnt)
            
            #mNeck_jnt.rename(_l_namesToUse[0])
            for k,v in _l_namesToUse[0].iteritems():
                mNeck_jnt.doStore(k,v)
            mNeck_jnt.doName()
        else:
            log.debug("|{0}| >> Multiple neck joint...".format(_str_func))
            
            _d = self.atBlockUtils('skeleton_getCreateDict', self.neckJoints +1)
            
            mOrientHelper = ml_prerigHandles[0].orientHelper
            
            ml_joints = JOINT.build_chain(_d['positions'][:-1], parent=True, worldUpAxis= mOrientHelper.getAxisVector('z-'))
            
            for i,mJnt in enumerate(ml_joints):
                #mJnt.rename(_l_namesToUse[i])
                for k,v in _l_namesToUse[i].iteritems():
                    mJnt.doStore(k,v)
                mJnt.doName()                
            
            #self.copyAttrTo(_baseNameAttrs[0],ml_joints[0].mNode,'cgmName',driven='target')
            
        mHead_jnt.p_parent = ml_joints[-1]
        ml_joints[0].parent = False
    else:
        mHead_jnt.parent = False
        #mHead_jnt.rename(_l_namesToUse[-1])
        
    ml_joints.append(mHead_jnt)
    
    for mJnt in ml_joints:
        mJnt.displayLocalAxis = 1
        mJnt.radius = _radius
    if len(ml_joints) > 1:
        mHead_jnt.radius = ml_joints[-1].radius * 5

    mRigNull.msgList_connect('moduleJoints', ml_joints)
    self.msgList_connect('moduleJoints', ml_joints)
    self.atBlockUtils('skeleton_connectToParent')
    
    return ml_joints


#=============================================================================================================
#>> rig
#=============================================================================================================
#NOTE - self here is a rig Factory....

d_preferredAngles = {'head':[0,-10, 10]}#In terms of aim up out for orientation relative values, stored left, if right, it will invert
d_rotateOrders = {'head':'yxz'}

#Rig build stuff goes through the rig build factory ------------------------------------------------------
@cgmGEN.Timer
def rig_prechecks(self):
    _short = self.d_block['shortName']
    _str_func = 'rig_prechecks'
    log.debug("|{0}| >>  ".format(_str_func)+ '-'*80)
    log.debug("{0}".format(self))
    
    mBlock = self.mBlock
    
    if mBlock.neckControls > 1:
        self.l_precheckErrors.append("Don't have support for more than one neckControl yet. Found: {0}".format(mBlock.neckControls))
    
    if mBlock.segmentMidIKControl and mBlock.neckJoints < 2:
        self.l_precheckErrors.append("Must have more than one neck joint with segmentMidIKControl")    
        
    if mBlock.getEnumValueString('squashMeasure') == 'pointDist':
        self.l_precheckErrors.append('pointDist squashMeasure mode not recommended')
        
    if mBlock.neckIK not in [0,3]:
        self.l_precheckErrors.append("Haven't setup neck IK: {0}".format(ATTR.get_enumValueString(mBlock.mNode,'neckIK')))

@cgmGEN.Timer
def rig_dataBuffer(self):
    _short = self.d_block['shortName']
    _str_func = 'rig_dataBuffer'
    log.debug("|{0}| >>  ".format(_str_func)+ '-'*80)
    log.debug("{0}".format(self))
    
    mBlock = self.mBlock
    mModule = self.mModule
    mRigNull = self.mRigNull
    mPrerigNull = mBlock.prerigNull
    ml_templateHandles = mBlock.msgList_get('templateHandles')
    ml_handleJoints = mPrerigNull.msgList_get('handleJoints')
    mMasterNull = self.d_module['mMasterNull']
    
    self.mRootTemplateHandle = ml_templateHandles[0]
    
    
    #Offset ============================================================================    
    str_offsetMode = ATTR.get_enumValueString(mBlock.mNode,'offsetMode')
    if not mBlock.offsetMode:
        log.debug("|{0}| >> default offsetMode...".format(_str_func))
        self.v_offset = self.mPuppet.atUtils('get_shapeOffset')
    else:
        str_offsetMode = ATTR.get_enumValueString(mBlock.mNode,'offsetMode')
        log.debug("|{0}| >> offsetMode: {1}".format(_str_func,str_offsetMode))
        
        l_sizes = []
        for mHandle in ml_templateHandles:
            #_size_sub = SNAPCALLS.get_axisBox_size(mHandle)
            #l_sizes.append( MATH.average(_size_sub[1],_size_sub[2]) * .1 )
            _size_sub = POS.get_bb_size(mHandle,True)
            l_sizes.append( MATH.average(_size_sub) * .1 )            
        self.v_offset = MATH.average(l_sizes)
        #_size_midHandle = SNAPCALLS.get_axisBox_size(ml_templateHandles[self.int_handleMidIdx])
        #self.v_offset = MATH.average(_size_midHandle[1],_size_midHandle[2]) * .1        
    log.debug("|{0}| >> self.v_offset: {1}".format(_str_func,self.v_offset))    
    log.debug(cgmGEN._str_subLine)
    
    #Squash stretch logic  =================================================================================
    log.debug("|{0}| >> Squash stretch..".format(_str_func))
    self.b_scaleSetup = mBlock.scaleSetup
    
    self.b_squashSetup = False
    
    self.d_squashStretch = {}
    self.d_squashStretchIK = {}
    
    _squashStretch = None
    if mBlock.squash:
        _squashStretch =  mBlock.getEnumValueString('squash')
        self.b_squashSetup = True
    self.d_squashStretch['squashStretch'] = _squashStretch
    
    _squashMeasure = None
    if mBlock.squashMeasure:
        _squashMeasure =  mBlock.getEnumValueString('squashMeasure')    
    self.d_squashStretch['squashStretchMain'] = _squashMeasure    

    _driverSetup = None
    if mBlock.ribbonAim:
        _driverSetup =  mBlock.getEnumValueString('ribbonAim')
    self.d_squashStretch['driverSetup'] = _driverSetup

    self.d_squashStretch['additiveScaleEnds'] = mBlock.scaleSetup
    self.d_squashStretch['extraSquashControl'] = mBlock.squashExtraControl
    self.d_squashStretch['squashFactorMax'] = mBlock.squashFactorMax
    self.d_squashStretch['squashFactorMin'] = mBlock.squashFactorMin
    
    log.debug("|{0}| >> self.d_squashStretch..".format(_str_func))    
    pprint.pprint(self.d_squashStretch)
    
    #Check for mid control and even handle count to see if w need an extra curve
    if mBlock.segmentMidIKControl:
        if MATH.is_even(mBlock.neckControls):
            self.d_squashStretchIK['sectionSpans'] = 2
            
    if self.d_squashStretchIK:
        log.debug("|{0}| >> self.d_squashStretchIK..".format(_str_func))    
        pprint.pprint(self.d_squashStretchIK)
    
    
    if not self.b_scaleSetup:
        pass
    
    log.debug("|{0}| >> self.b_scaleSetup: {1}".format(_str_func,self.b_scaleSetup))
    log.debug("|{0}| >> self.b_squashSetup: {1}".format(_str_func,self.b_squashSetup))
    
    log.debug(cgmGEN._str_subLine)
    
    #segintbaseindex =============================================================================
    str_ikBase = ATTR.get_enumValueString(mBlock.mNode,'ikBase')
    log.debug("|{0}| >> IK Base: {1}".format(_str_func,str_ikBase))    
    self.int_segBaseIdx = 0
    if str_ikBase in ['hips']:
        self.int_segBaseIdx = 1
    log.debug("|{0}| >> self.int_segBaseIdx: {1}".format(_str_func,self.int_segBaseIdx))
    
    log.debug(cgmGEN._str_subLine)

    #DynParents =============================================================================
    self.UTILS.get_dynParentTargetsDat(self)
    
    #rotateOrder =============================================================================
    _str_orientation = self.d_orientation['str']
    _l_orient = [_str_orientation[0],_str_orientation[1],_str_orientation[2]]
    self.ro_base = "{0}{1}{2}".format(_str_orientation[1],_str_orientation[2],_str_orientation[0])
    self.ro_head = "{2}{0}{1}".format(_str_orientation[0],_str_orientation[1],_str_orientation[2])
    self.ro_headLookAt = "{0}{2}{1}".format(_str_orientation[0],_str_orientation[1],_str_orientation[2])
    log.debug("|{0}| >> rotateOrder | self.ro_base: {1}".format(_str_func,self.ro_base))
    log.debug("|{0}| >> rotateOrder | self.ro_head: {1}".format(_str_func,self.ro_head))
    log.debug("|{0}| >> rotateOrder | self.ro_headLookAt: {1}".format(_str_func,self.ro_headLookAt))

    log.debug(cgmGEN._str_subLine)

    return True


@cgmGEN.Timer
def rig_skeleton(self):
    _short = self.d_block['shortName']
    
    _str_func = 'rig_skeleton'
    log.debug("|{0}| >>  ".format(_str_func)+ '-'*80)
    log.debug("{0}".format(self))
        
    mBlock = self.mBlock
    mRigNull = self.mRigNull
    ml_jointsToConnect = []
    ml_jointsToHide = []
    ml_joints = mRigNull.msgList_get('moduleJoints')
    self.d_joints['ml_moduleJoints'] = ml_joints
    ml_templateHandles = mBlock.msgList_get('templateHandles')
    
    BLOCKUTILS.skeleton_pushSettings(ml_joints, self.d_orientation['str'], self.d_module['mirrorDirection'])
                                     #d_rotateOrders, d_preferredAngles)
    
    log.info("|{0}| >> Head...".format(_str_func))  
    
    ml_rigJoints = BLOCKUTILS.skeleton_buildDuplicateChain(mBlock, ml_joints, 'rig', self.mRigNull,'rigJoints',blockNames=False)
    
    if self.mBlock.headAim:
        log.info("|{0}| >> Head IK...".format(_str_func))              
        ml_fkHeadJoints = BLOCKUTILS.skeleton_buildDuplicateChain(mBlock,ml_rigJoints[-1], 'fk', self.mRigNull, 'fkHeadJoint', singleMode = True)
        
        ml_blendHeadJoints = BLOCKUTILS.skeleton_buildDuplicateChain(mBlock,ml_rigJoints[-1], 'blend', self.mRigNull, 'blendHeadJoint', singleMode = True)
        ml_aimHeadJoints = BLOCKUTILS.skeleton_buildDuplicateChain(mBlock,ml_rigJoints[-1], 'aim', self.mRigNull, 'aimHeadJoint', singleMode = True)
        ml_jointsToConnect.extend(ml_fkHeadJoints + ml_aimHeadJoints)
        ml_jointsToHide.extend(ml_blendHeadJoints)
    
    #...Neck ---------------------------------------------------------------------------------------
    if self.mBlock.neckBuild:
        log.info("|{0}| >> Neck Build".format(_str_func))
        #return mOrientHelper.getAxisVector('y+')
        ml_fkJoints = BLOCKUTILS.skeleton_buildHandleChain(mBlock,'fk','fkJoints',mOrientHelper=ml_templateHandles[1].orientHelper)
        ml_jointsToHide.extend(ml_fkJoints)
        mOrientHelper = ml_templateHandles[1].orientHelper
        #Because
        vec_chainUp =mOrientHelper.getAxisVector('y+')

        if self.mBlock.neckIK:
            log.info("|{0}| >> buildIK on. Building blend and IK chains...".format(_str_func))  
            ml_blendJoints = BLOCKUTILS.skeleton_buildHandleChain(mBlock,'blend','blendJoints')
            ml_ikJoints = BLOCKUTILS.skeleton_buildHandleChain(mBlock,'ik','ikJoints')
            ml_jointsToConnect.extend(ml_ikJoints)
            ml_jointsToHide.extend(ml_blendJoints)
            
            for i,mJnt in enumerate(ml_ikJoints):
                if mJnt not in [ml_ikJoints[0],ml_ikJoints[-1]]:
                    mJnt.preferredAngle = mJnt.jointOrient
                    
            
            if mBlock.segmentMidIKControl:
                log.debug("|{0}| >> Creating ik mid control...".format(_str_func))  
                #Lever...
                mMidIK = ml_rigJoints[0].doDuplicate(po=True)
                mMidIK.cgmName = 'neck_segMid'
                mMidIK.p_parent = False
                mMidIK.doName()
            
                mMidIK.p_position = DIST.get_average_position([ml_rigJoints[self.int_segBaseIdx].p_position,
                                                               ml_rigJoints[-1].p_position])
            
                SNAP.aim(mMidIK.mNode, ml_rigJoints[-1].mNode, 'z+','y+','vector',
                         vec_chainUp)
                         #mBlock.rootUpHelper.getAxisVector('y+'))
                reload(JOINT)
                JOINT.freezeOrientation(mMidIK.mNode)
                mRigNull.connectChildNode(mMidIK,'controlSegMidIK','rigNull')            
    
        
        if mBlock.neckControls > 2:
            log.info("|{0}| >> IK Drivers...".format(_str_func))            
            ml_baseIKDrivers = BLOCKUTILS.skeleton_buildDuplicateChain(ml_segmentHandles,
                                                                       None, mRigNull,
                                                                       'baseIKDrivers',
                                                                       cgmType = 'baseIKDriver', indices=[0,-1])
            for mJnt in ml_baseIKDrivers:
                mJnt.parent = False
            ml_jointsToConnect.extend(ml_baseIKDrivers)
            
        if mBlock.neckJoints > mBlock.neckControls:
            log.info("|{0}| >> Handles...".format(_str_func))            
            ml_segmentHandles = BLOCKUTILS.skeleton_buildHandleChain(mBlock,'handle',
                                                                     'handleJoints',
                                                                     clearType=True)
            
            for i,mJnt in enumerate(ml_segmentHandles):
                mJnt.parent = ml_blendJoints[i]
            
            log.info("|{0}| >> segment necessary...".format(_str_func))
                
            ml_segmentChain = BLOCKUTILS.skeleton_buildDuplicateChain(mBlock,
                                                                      ml_joints,
                                                                      None, mRigNull,
                                                                      'segmentJoints',
                                                                      cgmType = 'segJnt')
            JOINT.orientChain(ml_segmentChain,
                              worldUpAxis=vec_chainUp)
            
            
            for i,mJnt in enumerate(ml_rigJoints):
                if mJnt != ml_rigJoints[-1]:
                    mJnt.parent = ml_segmentChain[i]
                    mJnt.connectChildNode(ml_segmentChain[i],'driverJoint','sourceJoint')#Connect
                else:
                    mJnt.p_parent = False
                    
            ml_jointsToHide.extend(ml_segmentChain)
            
    #...joint hide -----------------------------------------------------------------------------------
    for mJnt in ml_jointsToHide:
        try:
            mJnt.drawStyle =2
        except:
            mJnt.radius = .00001
            
    #...connect... 
    self.fnc_connect_toRigGutsVis( ml_jointsToConnect )        
    
    return

#@cgmGEN.Timer
def rig_shapes(self):
    _short = self.d_block['shortName']
    _str_func = 'rig_shapes'
    log.debug("|{0}| >>  ".format(_str_func)+ '-'*80)
    log.debug("{0}".format(self))
    
    ml_prerigHandles = self.mBlock.atBlockUtils('prerig_getHandleTargets')
    ml_fkJoints = self.mRigNull.msgList_get('fkJoints')
    ml_rigJoints = self.mRigNull.msgList_get('rigJoints')
    mHeadHelper = ml_prerigHandles[-1]
    mBlock = self.mBlock
    _baseNameAttrs = ATTR.datList_getAttrs(mBlock.mNode,'nameList')    
    ml_templateHandles = mBlock.msgList_get('templateHandles')
    mHandleFactory = mBlock.asHandleFactory()
    mRigNull = self.mRigNull
    
    #l_toBuild = ['segmentFK_Loli','segmentIK']
    #mShapeCast.go(self._mi_module,l_toBuild, storageInstance=self)#This will store controls to a dict called    
    
    #Get our base size from the block
    _jointOrientation = self.d_orientation['str']
    
    _size = DIST.get_bb_size(ml_templateHandles[0].mNode,True,True)
    _side = BLOCKUTILS.get_side(self.mBlock)
    _short_module = self.mModule.mNode
    ml_joints = self.d_joints['ml_moduleJoints']
    _offset = self.v_offset
    
    #Logic ====================================================================================

    
    #Head=============================================================================================
    if mBlock.headAim:
        log.info("|{0}| >> Head aim...".format(_str_func))  
        
        _ikPos =DIST.get_pos_by_vec_dist(ml_prerigHandles[-1].p_position,
                                       MATH.get_obj_vector(ml_templateHandles[0].orientHelper.mNode,'z+'),
                                       _size * 1.5)
        
        ikCurve = CURVES.create_fromName('sphere2',_size/3)
        textCrv = CURVES.create_text('head',_size/4)
        CORERIG.shapeParent_in_place(ikCurve,textCrv,False)
        
        mLookAt = cgmMeta.validateObjArg(ikCurve,'cgmObject',setClass=True)
        mLookAt.p_position = _ikPos
        
        ATTR.copy_to(_short_module,'cgmName',mLookAt.mNode,driven='target')
        #mIK.doStore('cgmName','head')
        mLookAt.doStore('cgmTypeModifier','lookAt')
        mLookAt.doName()
        
        CORERIG.colorControl(mLookAt.mNode,_side,'main')
        
        self.mRigNull.connectChildNode(mLookAt,'lookAt','rigNull')#Connect
    
    
    #Head control....-------------------------------------------------------------------------------
    if not mBlock.neckBuild:
        b_FKIKhead = False
        if mBlock.neckControls > 1 and mBlock.neckBuild: 
            log.info("|{0}| >> FK/IK head necessary...".format(_str_func))          
            b_FKIKhead = True            
        
        #IK ----------------------------------------------------------------------------------
        mIK = ml_rigJoints[-1].doCreateAt()
        #CORERIG.shapeParent_in_place(mIK,l_lolis,False)
        CORERIG.shapeParent_in_place(mIK,ml_templateHandles[0].mNode,True)
        mIK = cgmMeta.validateObjArg(mIK,'cgmObject',setClass=True)
        
        mBlock.copyAttrTo(_baseNameAttrs[-1],mIK.mNode,'cgmName',driven='target')
        
        #ATTR.copy_to(_short_module,'cgmName',mIK.mNode,driven='target')
        #mIK.doStore('cgmName','head')
        if b_FKIKhead:mIK.doStore('cgmTypeModifier','ik')
        mIK.doName()    
        
        CORERIG.colorControl(mIK.mNode,_side,'main')
        
        self.mRigNull.connectChildNode(mIK,'headIK','rigNull')#Connect
        
        if b_FKIKhead:
            l_lolis = []
            l_starts = []
            for axis in ['x+','z-','x-']:
                pos = mHeadHelper.getPositionByAxisDistance(axis, _size * .75)
                ball = CURVES.create_fromName('sphere',_size/10)
                mBall = cgmMeta.cgmObject(ball)
                mBall.p_position = pos
                mc.select(cl=True)
                p_end = DIST.get_closest_point(mHeadHelper.mNode, ball)[0]
                p_start = mHeadHelper.getPositionByAxisDistance(axis, _size * .25)
                l_starts.append(p_start)
                line = mc.curve (d=1, ep = [p_start,p_end], os=True)
                l_lolis.extend([ball,line])
                
            mFK = ml_fkJoints[-1]
            CORERIG.shapeParent_in_place(mFK,l_lolis,False)
            mFK.doStore('cgmTypeModifier','fk')
            mFK.doName()
            
            CORERIG.colorControl(mFK.mNode,_side,'main')
            
            self.mRigNull.connectChildNode(mFK,'headFK','rigNull')#Connect
            
            if b_FKIKhead:#Settings ==================================================================================
                pos = mHeadHelper.getPositionByAxisDistance('z+', _size * .75)
                vector = mHeadHelper.getAxisVector('y+')
                newPos = DIST.get_pos_by_vec_dist(pos,vector,_size * .5)
            
                settings = CURVES.create_fromName('gear',_size/5,'z+')
                mSettings = cgmMeta.validateObjArg(settings,'cgmObject',setClass=True)
                mSettings.p_position = newPos
            
                ATTR.copy_to(_short_module,'cgmName',mSettings.mNode,driven='target')
                #mSettings.doStore('cgmName','head')
                mSettings.doStore('cgmTypeModifier','settings')
                mSettings.doName()
            
                CORERIG.colorControl(mSettings.mNode,_side,'sub')
            
                self.mRigNull.connectChildNode(mSettings,'settings','rigNull')#Connect    
            else:
                self.mRigNull.connectChildNode(mIK,'settings','rigNull')#Connect            
    else:
        mHeadTar = ml_rigJoints[-1]
        mFKHead = ml_rigJoints[-1].doCreateAt()
        
        CORERIG.shapeParent_in_place(mFKHead,ml_templateHandles[0].mNode,True)
        mFKHead = cgmMeta.validateObjArg(mFKHead,'cgmObject',setClass=True)
        mFKHead.doCopyNameTagsFromObject(mHeadTar.mNode,
                                        ignore=['cgmType','cgmTypeModifier'])        
        mFKHead.doStore('cgmTypeModifier','fk')
        mFKHead.doName()
        
        mHandleFactory.color(mFKHead.mNode,controlType='main')
        
        
        if mBlock.neckIK:
            ml_blendJoints = mRigNull.msgList_get('blendJoints')
            
            mIKHead = mFKHead.doDuplicate(po=False)
            mIKHead.doStore('cgmTypeModifier','ik')
            mIKHead.doName()            
            self.mRigNull.connectChildNode(mIKHead,'controlIK','rigNull')#Connect
            self.mRigNull.connectChildNode(mIKHead,'headIK','rigNull')#Connect
            
            #Fix fk.... ---------------------------------------------------------------------------
            CORERIG.shapeParent_in_place(ml_fkJoints[-1].mNode, mFKHead.mNode,False)            
            mFKHead = ml_fkJoints[-1]
            
            #Base IK...---------------------------------------------------------------------------------
            log.debug("|{0}| >> baseIK...".format(_str_func))
            ml_ikJoints = mRigNull.msgList_get('ikJoints')
            #mIK_templateHandle = self.mRootTemplateHandle
            #bb_ik = mHandleFactory.get_axisBox_size(mIK_templateHandle.mNode)
            #_ik_shape = CURVES.create_fromName('sphere', size = bb_ik)
        
            _ik_shape = self.atBuilderUtils('shapes_fromCast',
                                            targets = [ mObj for mObj in ml_rigJoints[:1]],
                                            offset = _offset,
                                            mode = 'castHandle')[0].mNode
        
            mIKBaseShape = cgmMeta.validateObjArg(_ik_shape, 'cgmObject',setClass=True)
        
            mIKBaseCrv = ml_ikJoints[0].doCreateAt()
            mIKBaseCrv.doCopyNameTagsFromObject(ml_fkJoints[0].mNode,ignore=['cgmType'])
            CORERIG.shapeParent_in_place(mIKBaseCrv.mNode, mIKBaseShape.mNode, False)                            
        
            mIKBaseCrv.doStore('cgmTypeModifier','ikBase')
            mIKBaseCrv.doName()
        
            mHandleFactory.color(mIKBaseCrv.mNode, controlType = 'main',transparent=True)
        
            mHandleFactory.color(mIKBaseCrv.mNode, controlType = 'main')        
            self.mRigNull.connectChildNode(mIKBaseCrv,'controlIKBase','rigNull')#Connect                    

        self.mRigNull.connectChildNode(mFKHead,'headFK','rigNull')#Connect
        
                
        
        """
        if b_FKIKhead:
            l_lolis = []
            l_starts = []
            for axis in ['x+','z-','x-']:
                pos = mHeadHelper.getPositionByAxisDistance(axis, _size * .75)
                ball = CURVES.create_fromName('sphere',_size/10)
                mBall = cgmMeta.cgmObject(ball)
                mBall.p_position = pos
                mc.select(cl=True)
                p_end = DIST.get_closest_point(mHeadHelper.mNode, ball)[0]
                p_start = mHeadHelper.getPositionByAxisDistance(axis, _size * .25)
                l_starts.append(p_start)
                line = mc.curve (d=1, ep = [p_start,p_end], os=True)
                l_lolis.extend([ball,line])
                
            mFK = ml_fkJoints[-1]
            CORERIG.shapeParent_in_place(mFK,l_lolis,False)
            mFK.doStore('cgmTypeModifier','fk')
            mFK.doName()
            
            CORERIG.colorControl(mFK.mNode,_side,'main')
            
            self.mRigNull.connectChildNode(mFK,'headFK','rigNull')#Connect        
             """
        
        #Settings =================================================================================
        pos = mHeadHelper.getPositionByAxisDistance('z+', _size * .75)
        
        mTar = ml_rigJoints[-1]
        
        vector = mHeadHelper.getAxisVector('y+')
        newPos = DIST.get_pos_by_vec_dist(pos,vector,_size * .5)
    
        settings = CURVES.create_fromName('gear',_size/5,'x+')
        mSettingsShape = cgmMeta.validateObjArg(settings,'cgmObject')
        mSettings = cgmMeta.validateObjArg(mTar.doCreateAt(),'cgmObject',setClass=True)
        
        mSettings.p_position = newPos
        mSettingsShape.p_position = newPos
    
        ATTR.copy_to(_short_module,'cgmName',mSettings.mNode,driven='target')
        #mSettings.doStore('cgmName','head')
        mSettings.doStore('cgmTypeModifier','settings')
        mSettings.doName()
        #CORERIG.colorControl(mSettings.mNode,_side,'sub')
        
        SNAP.aim_atPoint(mSettingsShape.mNode,
                         mTar.p_position,
                         aimAxis=_jointOrientation[0]+'+',
                         mode = 'vector',
                         vectorUp= mTar.getAxisVector(_jointOrientation[0]+'-'))
        
        CORERIG.shapeParent_in_place(mSettings.mNode, mSettingsShape.mNode,False)
        mHandleFactory.color(mSettings.mNode,controlType='sub')
        
        self.mRigNull.connectChildNode(mSettings,'settings','rigNull')#Connect
        
        #Neck ================================================================================
        log.debug("|{0}| >> Neck...".format(_str_func))
        #Root -------------------------------------------------------------------------------------------
        #Grab template handle root - use for sizing, make ball
        mNeckBaseHandle = self.mBlock.msgList_get('templateHandles')[1]
        size_neck = DIST.get_bb_size(mNeckBaseHandle.mNode,True,True) /2

        mRoot = ml_joints[0].doCreateAt()
        mRootCrv = cgmMeta.validateObjArg(CURVES.create_fromName('locatorForm', size_neck),
                                          'cgmObject',setClass=True)
        mRootCrv.doSnapTo(ml_joints[0])

        #SNAP.go(mRootCrv.mNode, ml_joints[0].mNode,position=False)

        CORERIG.shapeParent_in_place(mRoot.mNode,mRootCrv.mNode, False)

        ATTR.copy_to(_short_module,'cgmName',mRoot.mNode,driven='target')
        mRoot.doStore('cgmTypeModifier','root')
        mRoot.doName()

        CORERIG.colorControl(mRoot.mNode,_side,'sub')
        self.mRigNull.connectChildNode(mRoot,'rigRoot','rigNull')#Connect

        #controlSegMidIK =============================================================================
        if mRigNull.getMessage('controlSegMidIK'):
            log.debug("|{0}| >> controlSegMidIK...".format(_str_func))            
            mControlSegMidIK = mRigNull.getMessage('controlSegMidIK',asMeta=1)[0]
            
            ml_shapes = self.atBuilderUtils('shapes_fromCast',
                                            targets = mControlSegMidIK,
                                            offset = _offset,
                                            mode = 'limbSegmentHandleBack')#'simpleCast  limbSegmentHandle
            
            CORERIG.shapeParent_in_place(mControlSegMidIK.mNode, ml_shapes[0].mNode,False)
            
            mControlSegMidIK.doStore('cgmTypeModifier','ik')
            mControlSegMidIK.doStore('cgmType','handle')
            mControlSegMidIK.doName()            
    
            mHandleFactory.color(mControlSegMidIK.mNode, controlType = 'sub')
        

        #FK/Ik =======================================================================================    
        ml_fkShapes = self.atBuilderUtils('shapes_fromCast', mode = 'frameHandle')#frameHandle

        mHandleFactory.color(ml_fkShapes[0].mNode, controlType = 'main')        
        CORERIG.shapeParent_in_place(ml_fkJoints[0].mNode, ml_fkShapes[0].mNode, True, replaceShapes=True)

        for i,mShape in enumerate(ml_fkJoints[:-1]):
            mShape = ml_fkShapes[i]
            mHandleFactory.color(mShape.mNode, controlType = 'main')        
            CORERIG.shapeParent_in_place(ml_fkJoints[i].mNode, mShape.mNode, True, replaceShapes=True)
            
            mShape.delete()

    
    
    #Direct Controls =============================================================================
    ml_rigJoints = self.mRigNull.msgList_get('rigJoints')
    
    _size_direct = DIST.get_bb_size(ml_templateHandles[-1].mNode,True,True)
    
    d_direct = {'size':_size_direct/2}
        
    ml_directShapes = self.atBuilderUtils('shapes_fromCast',
                                          ml_rigJoints,
                                          mode ='direct',**d_direct)
    
    for i,mCrv in enumerate(ml_directShapes):
        CORERIG.colorControl(mCrv.mNode,_side,'sub')
        CORERIG.shapeParent_in_place(ml_rigJoints[i].mNode,mCrv.mNode, False, replaceShapes=True)
        for mShape in ml_rigJoints[i].getShapes(asMeta=True):
            mShape.doName()

    for mJnt in ml_rigJoints:
        try:
            mJnt.drawStyle =2
        except:
            mJnt.radius = .00001    
    

    #Handles ===========================================================================================
    ml_handleJoints = self.mRigNull.msgList_get('handleJoints')

    if ml_handleJoints:
        log.debug("|{0}| >> Found Handle joints...".format(_str_func))
        #l_uValues = MATH.get_splitValueList(.01,.99, len(ml_handleJoints))
        ml_handleShapes = self.atBuilderUtils('shapes_fromCast',
                                              targets = ml_handleJoints,
                                              offset = _offset,
                                              mode = 'limbSegmentHandleBack')#'segmentHandle') limbSegmentHandle


        for i,mCrv in enumerate(ml_handleShapes):
            log.debug("|{0}| >> Shape: {1} | Handle: {2}".format(_str_func,mCrv.mNode,ml_handleJoints[i].mNode ))                
            mHandleFactory.color(mCrv.mNode, controlType = 'sub')            
            CORERIG.shapeParent_in_place(ml_handleJoints[i].mNode, 
                                         mCrv.mNode, False,
                                         replaceShapes=True)




@cgmGEN.Timer
def rig_controls(self):
    _short = self.d_block['shortName']
    _str_func = 'rig_controls'
    log.debug("|{0}| >>  ".format(_str_func)+ '-'*80)
    log.debug("{0}".format(self))
  
    mRigNull = self.mRigNull
    mBlock = self.mBlock
    ml_controlsAll = []#we'll append to this list and connect them all at the end
    mRootParent = self.mDeformNull
    mSettings = mRigNull.settings
    
    mHeadFK = mRigNull.getMessageAsMeta('headFK')
    mHeadIK = mRigNull.getMessageAsMeta('headIK')
    
    d_controlSpaces = self.atBuilderUtils('get_controlSpaceSetupDict')    
    
    # Drivers ==========================================================================================    
    if self.mBlock.neckBuild:
        if self.mBlock.neckIK:
            mPlug_FKIK = cgmMeta.cgmAttr(mSettings.mNode,'FKIK',attrType='float',minValue=0,maxValue=1,lock=False,keyable=True)
    
        #>> vis Drivers ==============================================================================	
        mPlug_visSub = self.atBuilderUtils('build_visSub')
        mPlug_visRoot = cgmMeta.cgmAttr(mSettings,'visRoot', value = True, attrType='bool', defaultValue = False,keyable = False,hidden = False)
        
    mPlug_visDirect = cgmMeta.cgmAttr(mSettings,'visDirect', value = True,
                                      attrType='bool', defaultValue = False,
                                      keyable = False,hidden = False)
    
    if self.mBlock.headAim:        
        mPlug_aim = cgmMeta.cgmAttr(mSettings.mNode,'blend_aim',attrType='float',
                                    minValue=0,maxValue=1,
                                    lock=False,keyable=True)
        
        
    #>> Neck build ======================================================================================
    if self.mBlock.neckBuild:
        log.debug("|{0}| >> Neck...".format(_str_func))
        
        #Root -------------------------------------------------------------------------------------------
        if not mRigNull.getMessage('rigRoot'):
            raise ValueError,"No rigRoot found"
        
        mRoot = mRigNull.rigRoot
        log.info("|{0}| >> Found rigRoot : {1}".format(_str_func, mRoot))
        
        
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
            
        
        #FK controls -------------------------------------------------------------------------------------
        log.debug("|{0}| >> FK Controls...".format(_str_func))
        ml_fkJoints = self.mRigNull.msgList_get('fkJoints')
        
        ml_fkJoints[0].parent = mRoot
        ml_controlsAll.extend(ml_fkJoints)
        
        for i,mObj in enumerate(ml_fkJoints):
            d_buffer = MODULECONTROL.register(mObj,
                                              mirrorSide= self.d_module['mirrorDirection'],
                                              mirrorAxis="translateX,rotateY,rotateZ",
                                              makeAimable = True)
    
            mObj = d_buffer['mObj']
            #mObj.axisAim = "%s+"%self._go._jointOrientation[0]
            #mObj.axisUp= "%s+"%self._go._jointOrientation[1]	
            #mObj.axisOut= "%s+"%self._go._jointOrientation[2]
            #try:i_obj.drawStyle = 2#Stick joint draw style	    
            #except:self.log_error("{0} Failed to set drawStyle".format(i_obj.p_nameShort))
            ATTR.set_hidden(mObj.mNode,'radius',True)
            
            
        ml_blend = mRigNull.msgList_get('blendJoints')
        
        mControlBaseIK = mRigNull.getMessageAsMeta('controlIKBase')
        if mControlBaseIK:
            mControlBaseIK = mRigNull.controlIKBase
            log.debug("|{0}| >> Found controlBaseIK : {1}".format(_str_func, mControlBaseIK))
            
            _d = MODULECONTROL.register(mControlBaseIK,
                                        addDynParentGroup = True, 
                                        mirrorSide= self.d_module['mirrorDirection'],
                                        mirrorAxis="translateX,rotateY,rotateZ",
                                        makeAimable = True,
                                        **d_controlSpaces)
                                        
            
            mControlBaseIK = _d['mObj']
            mControlBaseIK.masterGroup.parent = mRootParent
            ml_controlsAll.append(mControlBaseIK)
            
            #Register our snapToTarget -------------------------------------------------------------
            self.atUtils('get_switchTarget', mControlBaseIK,ml_blend[0])

            
            
        mControlSegMidIK = False
        #controlSegMidIK =============================================================================
        if mRigNull.getMessage('controlSegMidIK'):
            mControlSegMidIK = mRigNull.controlSegMidIK
            log.debug("|{0}| >> found controlSegMidIK: {1}".format(_str_func,mControlSegMidIK))
            
            _d = MODULECONTROL.register(mControlSegMidIK,
                                        addDynParentGroup = True, 
                                        mirrorSide= self.d_module['mirrorDirection'],
                                        mirrorAxis="translateX,rotateY,rotateZ",
                                        makeAimable = True,
                                        **d_controlSpaces)
            
            
            mControlSegMidIK = _d['mObj']
            mControlSegMidIK.masterGroup.parent = mRootParent
            ml_controlsAll.append(mControlSegMidIK)
        
            #Register our snapToTarget -------------------------------------------------------------
            self.atUtils('get_switchTarget', mControlSegMidIK,ml_blend[ MATH.get_midIndex(len(ml_blend))])        


    #ikHead ========================================================================================
    log.info("|{0}| >> Found headIK : {1}".format(_str_func, mHeadIK))
    ml_blendJoints = mRigNull.msgList_get('blendJoints')
    
    _d = MODULECONTROL.register(mHeadIK,
                                addDynParentGroup = True,
                                mirrorSide= self.d_module['mirrorDirection'],
                                mirrorAxis="translateX,rotateY,rotateZ",
                                makeAimable = True,
                                **d_controlSpaces)
    
    mHeadIK = _d['mObj']
    mHeadIK.masterGroup.parent = mRootParent
    ml_controlsAll.append(mHeadIK)
    
    self.atUtils('get_switchTarget', mHeadIK, ml_blendJoints[-1])
    
    
    #>> headLookAt ========================================================================================
    mHeadLookAt = False
    if mRigNull.getMessage('lookAt'):
        mHeadLookAt = mRigNull.lookAt
        log.info("|{0}| >> Found lookAt : {1}".format(_str_func, mHeadLookAt))
        MODULECONTROL.register(mHeadLookAt,
                               typeModifier='lookAt',
                               addDynParentGroup = True, 
                               mirrorSide= self.d_module['mirrorDirection'],
                               mirrorAxis="translateX,rotateY,rotateZ",
                               makeAimable = False,
                               **d_controlSpaces)
        mHeadLookAt.masterGroup.parent = mRootParent
        ml_controlsAll.append(mHeadLookAt)
        
        if mHeadIK:
            mHeadLookAt.doStore('controlIK', mHeadIK.mNode)
        if mHeadFK:
            mHeadLookAt.doStore('controlFK', mHeadFK.mNode)
            
        #int_mid = MATH.get_midIndex(len(ml_blend))

        
    
    #>> settings ========================================================================================
    if mHeadFK:
        mSettings = mRigNull.settings
        log.info("|{0}| >> Found settings : {1}".format(_str_func, mSettings))
        
        MODULECONTROL.register(mSettings,
                               mirrorSide= self.d_module['mirrorDirection'],
                               )
        
        ml_blendJoints = self.mRigNull.msgList_get('blendJoints')
        mSettings.masterGroup.parent = ml_blendJoints[-1]
        ml_controlsAll.append(mSettings)
    
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
    
            mObj = d_buffer['mObj']
            ATTR.set_hidden(mObj.mNode,'radius',True)
            
            for mShape in mObj.getShapes(asMeta=True):
                ATTR.connect(mPlug_visSub.p_combinedShortName, "{0}.overrideVisibility".format(mShape.mNode))
        
            
    #>> Direct Controls ========================================================================================
    ml_rigJoints = self.mRigNull.msgList_get('rigJoints')
    ml_controlsAll.extend(ml_rigJoints)
    
    for i,mObj in enumerate(ml_rigJoints):
        d_buffer = MODULECONTROL.register(mObj,
                                          typeModifier='direct',
                                          mirrorSide= self.d_module['mirrorDirection'],
                                          mirrorAxis="translateX,rotateY,rotateZ",
                                          makeAimable = False)
        mObj = d_buffer['mObj']
        ATTR.set_hidden(mObj.mNode,'radius',True)        
        if mObj.hasAttr('cgmIterator'):
            ATTR.set_hidden(mObj.mNode,'cgmIterator',True)        
            
        for mShape in mObj.getShapes(asMeta=True):
            ATTR.connect(mPlug_visDirect.p_combinedShortName, "{0}.overrideVisibility".format(mShape.mNode))
                
            
    #ml_controlsAll = self.atBuilderUtils('register_mirrorIndices', ml_controlsAll)
    #self.atBuilderUtils('check_nameMatches', ml_controlsAll)
    
    mHandleFactory = mBlock.asHandleFactory()
    for mCtrl in ml_controlsAll:
        ATTR.set(mCtrl.mNode,'rotateOrder',self.ro_base)
        
        if mCtrl.hasAttr('radius'):
            ATTR.set(mCtrl.mNode,'radius',0)        
        
        ml_pivots = mCtrl.msgList_get('spacePivots')
        if ml_pivots:
            log.debug("|{0}| >> Coloring spacePivots for: {1}".format(_str_func,mCtrl))
            for mPivot in ml_pivots:
                mHandleFactory.color(mPivot.mNode, controlType = 'sub')            
    
    if mHeadIK:
        ATTR.set(mHeadIK.mNode,'rotateOrder',self.ro_head)
    if mHeadLookAt:
        ATTR.set(mHeadLookAt.mNode,'rotateOrder',self.ro_headLookAt)
        
    
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
    log.debug("|{0}| >>  ".format(_str_func)+ '-'*80)
    log.debug("{0}".format(self))    
    
    if not self.mBlock.neckBuild:
        log.info("|{0}| >> No neck build optioned".format(_str_func))                      
        return True
    
    log.info("|{0}| >> ...".format(_str_func))  
    
    mBlock = self.mBlock
    mRigNull = self.mRigNull
    mRootParent = self.mDeformNull
    mModule = self.mModule
    mRoot = mRigNull.rigRoot
    
    mHeadIK = mRigNull.headIK
    log.info("|{0}| >> Found headIK : {1}".format(_str_func, mHeadIK))
    
    ml_segJoints = mRigNull.msgList_get('segmentJoints')
    ml_blendJoints = mRigNull.msgList_get('blendJoints')
    #ml_rigJoints[0].parent = ml_blendJoints[0]
    #ml_rigJoints[-1].parent = mHeadFK
    ml_handleJoints = mRigNull.msgList_get('handleJoints')
    
    
    if not ml_segJoints:
        log.info("|{0}| >> No segment joints. No segment setup necessary.".format(_str_func))
        return True    
    
    for mJnt in ml_segJoints:
        mJnt.drawStyle = 2
        ATTR.set(mJnt.mNode,'radius',0)    
    
    #>> Ribbon setup ========================================================================================
    log.debug("|{0}| >> Ribbon setup...".format(_str_func))    
    
    ml_influences = copy.copy(ml_handleJoints)
    
    _settingsControl = None
    if mBlock.squashExtraControl:
        _settingsControl = mRigNull.settings.mNode
    
    _extraSquashControl = mBlock.squashExtraControl
           
    res_segScale = self.UTILS.get_blockScale(self,'segMeasure')
    mPlug_masterScale = res_segScale[0]
    mMasterCurve = res_segScale[1]
    
    mSegMidIK = mRigNull.getMessageAsMeta('controlSegMidIK')
    if mSegMidIK and mBlock.neckControls == 1:
        log.info("|{0}| >> seg mid IK control found...".format(_str_func))
        ml_influences.append(mSegMidIK)
    
    _d = {'jointList':[mObj.mNode for mObj in ml_segJoints],
          'baseName':'{0}_rigRibbon'.format(self.d_module['partName']),
          'connectBy':'constraint',
          'extendEnds':True,
          'masterScalePlug':mPlug_masterScale,
          'influences':ml_influences,
          'settingsControl':_settingsControl,
          'attachEndsToInfluences':True,
          'moduleInstance':mModule}
    
    if mSegMidIK:
        _d['sectionSpans'] = 2
        
    _d.update(self.d_squashStretch)
    res_ribbon = IK.ribbon(**_d)
    
    ml_surfaces = res_ribbon['mlSurfaces']
    
    mMasterCurve.p_parent = mRoot    
    
    ml_segJoints[0].parent = mRoot
    
    if self.b_squashSetup:
        for mJnt in ml_segJoints:
            mJnt.segmentScaleCompensate = False
            if mJnt == ml_segJoints[0]:
                continue
            mJnt.p_parent = ml_segJoints[0].p_parent    
    
    return
    #>> Ribbon setup ========================================================================================
    log.debug("|{0}| >> Ribbon setup...".format(_str_func))
    reload(IK)
    #mSurf = IK.ribbon([mObj.mNode for mObj in ml_rigJoints], baseName = mBlock.cgmName, connectBy='constraint', msgDriver='masterGroup', moduleInstance = mModule)
    mSurf = IK.ribbon([mObj.mNode for mObj in ml_segJoints],
                      baseName = mBlock.cgmName,
                      driverSetup='stable',
                      connectBy='constraint',
                      moduleInstance = mModule)

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
    
    
    """
    #>> Neck build ======================================================================================
    if mBlock.neckJoints > 1:
        
        if mBlock.neckControls == 1:
            log.debug("|{0}| >> Simple neck segment...".format(_str_func))
            ml_segmentJoints[0].parent = ml_blendJoints[0] #ml_handleJoints[0]
            ml_segmentJoints[-1].parent = mHeadIK # ml_handleJoints[-1]
            RIGCONSTRAINT.setup_linearSegment(ml_segmentJoints)
            
        else:
            log.debug("|{0}| >> Neck segment...".format(_str_func))    """
            



@cgmGEN.Timer
def rig_frame(self):
    _short = self.d_block['shortName']
    _str_func = ' rig_rigFrame'
    
    log.debug("|{0}| >>  ".format(_str_func)+ '-'*80)
    log.debug("{0}".format(self))    

    mBlock = self.mBlock
    mRigNull = self.mRigNull
    mRootParent = self.mDeformNull
    mModule = self.mModule
    mHeadIK = mRigNull.headIK
    log.info("|{0}| >> Found headIK : {1}".format(_str_func, mHeadIK))
    
    ml_rigJoints = mRigNull.msgList_get('rigJoints')
    ml_fkJoints = mRigNull.msgList_get('fkJoints')
    ml_handleJoints = self.mRigNull.msgList_get('handleJoints')
    ml_baseIKDrivers = self.mRigNull.msgList_get('baseIKDrivers')
    ml_blendJoints = mRigNull.msgList_get('blendJoints')
    ml_segBlendTargets = copy.copy(ml_blendJoints)
    
    mTopHandleDriver = mHeadIK
    
    mHeadFK = False
    mAimParent = ml_blendJoints[-1]
    
    mHeadFK = mRigNull.getMessageAsMeta('headFK')
    mHeadIK = mRigNull.getMessageAsMeta('headIK')
        
    if ml_blendJoints:
        mHeadStuffParent = ml_blendJoints[-1]
    else:
        mHeadStuffParent = mHeadFK

    #>> headFK ========================================================================================
    """We use the ik head sometimes."""
    
    if self.mBlock.headAim:
        log.info("|{0}| >> HeadAim setup...".format(_str_func))
        mSettings = mRigNull.settings
        
        mPlug_aim = cgmMeta.cgmAttr(mSettings.mNode,'blend_aim',attrType='float',lock=False,keyable=True)
        
        mHeadFKJoint = mRigNull.getMessage('fkHeadJoint', asMeta=True)[0]
        mHeadAimJoint = mRigNull.getMessage('aimHeadJoint', asMeta=True)[0]
        mHeadBlendJoint = mRigNull.getMessage('blendHeadJoint', asMeta=True)[0]
        mTopHandleDriver = mHeadBlendJoint
        mHeadLookAt = mRigNull.lookAt
        
        if ml_handleJoints:
            mTopDriver = ml_handleJoints[-1].doCreateAt()
        else:
            mTopDriver = ml_fkJoints[-1].doCreateAt()
            
        mTopDriver.p_parent = mHeadBlendJoint
        ml_segBlendTargets[-1] = mTopDriver#...insert into here our new twist driver
        
        mHeadLookAt.doStore('drivenBlend', mHeadBlendJoint.mNode)
        mHeadLookAt.doStore('drivenAim', mHeadAimJoint.mNode)
        
        self.atUtils('get_switchTarget', mHeadLookAt, mHeadBlendJoint)
        
        mHeadLookAt.doStore('fkMatch', mTopDriver.mNode)
        mHeadLookAt.doStore('ikMatch', mHeadBlendJoint.mNode)
        
        if mBlock.scaleSetup:
            for mJnt in mHeadFKJoint,mHeadAimJoint,mHeadBlendJoint:
                mJnt.segmentScaleCompensate = False
        
        
        ATTR.connect(mPlug_aim.p_combinedShortName, "{0}.v".format(mHeadLookAt.mNode))
        
        #Setup Aim Main -------------------------------------------------------------------------------------
        mc.aimConstraint(mHeadLookAt.mNode,
                         mHeadAimJoint.mNode,
                         maintainOffset = False, weight = 1,
                         aimVector = self.d_orientation['vectorAim'],
                         upVector = self.d_orientation['vectorUp'],
                         worldUpVector = self.d_orientation['vectorUp'],
                         worldUpObject = mHeadLookAt.mNode,#mHeadIK.mNode,#mHeadIK.masterGroup.mNode
                         worldUpType = 'objectRotation' )
        
        #Setup Aim back on head -------------------------------------------------------------------------------------
        _str_orientation = self.d_orientation['str']
        mc.aimConstraint(mHeadStuffParent.mNode,
                         mHeadLookAt.mNode,
                         maintainOffset = False, weight = 1,
                         aimVector = self.d_orientation['vectorAimNeg'],
                         upVector = self.d_orientation['vectorUp'],
                         worldUpVector = self.d_orientation['vectorUp'],
                         skip = _str_orientation[0],
                         worldUpObject = mHeadStuffParent.mNode,#mHeadIK.masterGroup.mNode,#mHeadIK.mNode,#mHeadIK.masterGroup.mNode
                         worldUpType = 'objectRotation' )
        
        ATTR.set_alias(mHeadLookAt.mNode,'r{0}'.format(_str_orientation[0]),'tilt')
        mHeadLookAt.setAttrFlags(attrs=['r{0}'.format(v) for v in _str_orientation[1:]])
        
        #Setup blend ----------------------------------------------------------------------------------
        RIGCONSTRAINT.blendChainsBy(mHeadFKJoint,mHeadAimJoint,mHeadBlendJoint,
                                    driver = mPlug_aim.p_combinedName,l_constraints=['orient'])
        
        #Parent pass ---------------------------------------------------------------------------------
        mHeadLookAt.masterGroup.parent = mHeadStuffParent#mHeadIK.masterGroup
        #mSettings.masterGroup.parent = mHeadIK
        
        for mObj in mHeadFKJoint,mHeadAimJoint,mHeadBlendJoint:
            mObj.p_parent = mHeadStuffParent
        
        #mHeadIK.parent = mHeadBlendJoint.mNode
        """
        mHeadFK_aimFollowGroup = mHeadFK.doGroup(True,True,True,'aimFollow')
        mc.orientConstraint(mHeadBlendJoint.mNode,
                            mHeadFK_aimFollowGroup.mNode,
                            maintainOffset = False)"""
        
        #Trace crv ---------------------------------------------------------------------------------
        log.debug("|{0}| >> head look at track Crv".format(_str_func))
        trackcrv,clusters = CORERIG.create_at([mHeadLookAt.mNode,
                                               mHeadAimJoint.mNode],#ml_handleJoints[1]],
                                              'linearTrack',
                                              baseName = '{0}_headAimTrack'.format(self.d_module['partName']))
    
        mTrackCrv = cgmMeta.asMeta(trackcrv)
        mTrackCrv.p_parent = self.mModule
        mHandleFactory = mBlock.asHandleFactory()
        mHandleFactory.color(mTrackCrv.mNode, controlType = 'sub')
    
        for s in mTrackCrv.getShapes(asMeta=True):
            s.overrideEnabled = 1
            s.overrideDisplayType = 2
        mTrackCrv.doConnectIn('visibility',mPlug_aim.p_combinedShortName)        
    else:
        log.info("|{0}| >> NO Head IK setup...".format(_str_func))    
    
    #Parent the direct control to the 
    if ml_rigJoints[-1].getMessage('masterGroup'):
        ml_rigJoints[-1].masterGroup.parent = mTopHandleDriver
    else:
        ml_rigJoints[-1].parent = mTopHandleDriver
        
    #>> Neck build ======================================================================================
    if mBlock.neckBuild:
        log.debug("|{0}| >> Neck...".format(_str_func))
        
        if not mRigNull.getMessage('rigRoot'):
            raise ValueError,"No rigRoot found"
        
        mRoot = mRigNull.rigRoot
        mSettings = mRigNull.settings
        
        if self.mBlock.neckIK:
            log.debug("|{0}| >> Neck IK...".format(_str_func))
            ml_ikJoints = mRigNull.msgList_get('ikJoints')
            ml_blendJoints = mRigNull.msgList_get('blendJoints')
            
            mPlug_FKIK = cgmMeta.cgmAttr(mSettings.mNode,'FKIK',attrType='float',lock=False,keyable=True)
            
            #>>> Setup a vis blend result
            mPlug_FKon = cgmMeta.cgmAttr(mSettings,'result_FKon',attrType='float',defaultValue = 0,keyable = False,lock=True,hidden=True)	
            mPlug_IKon = cgmMeta.cgmAttr(mSettings,'result_IKon',attrType='float',defaultValue = 0,keyable = False,lock=True,hidden=True)	
        
            NODEFACTORY.createSingleBlendNetwork(mPlug_FKIK.p_combinedName,
                                                 mPlug_IKon.p_combinedName,
                                                 mPlug_FKon.p_combinedName)
              
            mPlug_FKon.doConnectOut("{0}.visibility".format(ml_fkJoints[0].masterGroup.mNode))
            
            
            mIKGroup = mRoot.doCreateAt()
            mIKGroup.doStore('cgmTypeModifier','ik')
            mIKGroup.doName()
    
            mPlug_IKon.doConnectOut("{0}.visibility".format(mIKGroup.mNode))
    
            mIKGroup.parent = mRoot
            #mIKControl.masterGroup.parent = mIKGroup            
            mIKGroup.dagLock(True)
            
            mHeadIK.masterGroup.p_parent = mIKGroup
            
            """
            # Create head position driver ------------------------------------------------
            mHeadDriver = mHeadIK.doCreateAt()
            mHeadDriver.rename('headBlendDriver')
            mHeadDriver.parent = mRoot
            
            mHeadIKDriver = mHeadIK.doCreateAt()
            mHeadIKDriver.rename('headIKDriver')
            mHeadIKDriver.parent = mRoot
            
            mHeadFKDriver = mHeadIK.doCreateAt()
            mHeadFKDriver.rename('headFKDriver')
            mHeadFKDriver.parent = ml_fkJoints[-1]
            
            mHeadIK.connectChildNode(mHeadDriver.mNode, 'blendDriver')
            
            RIGCONSTRAINT.blendChainsBy(mHeadFKDriver.mNode,
                                        mHeadIKDriver.mNode,
                                        mHeadDriver.mNode,
                                        driver = mPlug_FKIK.p_combinedName,l_constraints=['point','orient'])            
            
            """
            
            mIKBaseControl = mRigNull.controlIKBase
            # Neck controls --------------------------------------------------------------
            if mBlock.neckControls == 1:
                log.debug("|{0}| >> Single joint IK...".format(_str_func))
                mc.aimConstraint(mHeadIK.mNode,
                                 ml_ikJoints[0].mNode,
                                 maintainOffset = True, weight = 1,
                                 aimVector = self.d_orientation['vectorAim'],
                                 upVector = self.d_orientation['vectorUp'],
                                 worldUpVector = self.d_orientation['vectorOut'],
                                 worldUpObject = mIKBaseControl.mNode,
                                 worldUpType = 'objectRotation' )
                mc.pointConstraint(mHeadIK.mNode,
                                   ml_ikJoints[-1].mNode,
                                   maintainOffset = True)
            else:
                raise ValueError,"Don't have ability for more than one neck control yet"
            
            mIKBaseControl.masterGroup.p_parent = mIKGroup


            mc.pointConstraint(mHeadIK.mNode,ml_ikJoints[-1].mNode, maintainOffset = True)
            mc.orientConstraint(mHeadIK.mNode,ml_ikJoints[-1].mNode, maintainOffset = True)
            
            
            #>> handleJoints ========================================================================================
            if ml_handleJoints:
                log.debug("|{0}| >> Found Handles...".format(_str_func))
                #ml_handleJoints[-1].masterGroup.parent = mHeadIK
                #ml_handleJoints[0].masterGroup.parent = ml_blendJoints[0]
                
                if mBlock.neckControls == 1:
                    reload(RIGCONSTRAINT)
                    RIGCONSTRAINT.build_aimSequence(ml_handleJoints,
                                                    ml_handleJoints,
                                                    ml_blendJoints, #ml_segBlendTargets,#ml_handleParents,
                                                    ml_segBlendTargets,
                                                    mode = 'sequence',
                                                    mRoot=mRoot,
                                                    rootTargetEnd=ml_segBlendTargets[-1],
                                                    upParent=[1,0,0],
                                                    interpType = 2,
                                                    upMode = 'objectRotation')
                    
                    """
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
                                     worldUpType = 'objectRotation' )"""
            
            if ml_handleJoints:            
                ml_handleJoints[-1].masterGroup.p_parent = mHeadBlendJoint
            #>> midSegcontrol ========================================================================================
            mSegMidIK = mRigNull.getMessageAsMeta('controlSegMidIK')
            if mSegMidIK:
                log.debug("|{0}| >> seg mid IK control found...".format(_str_func))
    
                #mSegMidIK = mRigNull.controlSegMidIK
                
                if mBlock.neckControls > 1:
                    mSegMidIK.masterGroup.parent = mIKGroup
    
                ml_midTrackJoints = copy.copy(ml_handleJoints)
                ml_midTrackJoints.insert(1,mSegMidIK)
    
                d_mid = {'jointList':[mJnt.mNode for mJnt in ml_midTrackJoints],
                         'baseName' :self.d_module['partName'] + '_midRibbon',
                         'driverSetup':'stableBlend',
                         'squashStretch':None,
                         'msgDriver':'masterGroup',
                         'specialMode':'noStartEnd',
                         'connectBy':'constraint',
                         'influences':ml_handleJoints,
                         'moduleInstance' : mModule}
    
                l_midSurfReturn = IK.ribbon(**d_mid)            
            
            #>> baseIK Drivers ========================================================================================
            if ml_baseIKDrivers:
                log.debug("|{0}| >> Found baseIK drivers...".format(_str_func))
                
                ml_baseIKDrivers[-1].parent = mHeadIK
                ml_baseIKDrivers[0].parent = mRoot
                
                #Aim top to bottom ----------------------------
                mc.aimConstraint(mRoot.mNode,
                                 ml_baseIKDrivers[-1].mNode,
                                 maintainOffset = True, weight = 1,
                                 aimVector = self.d_orientation['vectorAimNeg'],
                                 upVector = self.d_orientation['vectorUp'],
                                 worldUpVector = self.d_orientation['vectorUp'],
                                 worldUpObject = ml_baseIKDrivers[0].mNode,
                                 worldUpType = 'objectRotation' )
                
                #Aim bottom to top ----------------------------
                mc.aimConstraint(ml_baseIKDrivers[-1].mNode,
                                 ml_baseIKDrivers[0].mNode,
                                 maintainOffset = True, weight = 1,
                                 aimVector = self.d_orientation['vectorAim'],
                                 upVector = self.d_orientation['vectorUp'],
                                 worldUpVector = self.d_orientation['vectorOut'],
                                 worldUpObject = ml_blendJoints[0].mNode,
                                 worldUpType = 'objectRotation' )                
                
                
            if mBlock.neckJoints == 1:
                log.debug("|{0}| >> Single neckJoint setup...".format(_str_func))                
                ml_rigJoints[0].masterGroup.parent = ml_blendJoints[0]
                
                """
                mc.aimConstraint(mHeadIK.mNode,
                                 ml_rigJoints[0].masterGroup.mNode,
                                 maintainOffset = True, weight = 1,
                                 aimVector = self.d_orientation['vectorAim'],
                                 upVector = self.d_orientation['vectorUp'],
                                 worldUpVector = self.d_orientation['vectorOut'],
                                 worldUpObject = ml_blendJoints[0].mNode,
                                 worldUpType = 'objectRotation' )"""
                
            else:
                log.debug("|{0}| >> Not implemented multi yet".format(_str_func))
                
            
            #Parent --------------------------------------------------            
            ml_blendJoints[0].parent = mRoot
            ml_ikJoints[0].parent = mRigNull.controlIKBase
            
            
            #Setup blend ----------------------------------------------------------------------------------
            log.debug("|{0}| >> blend setup...".format(_str_func))                
            
            if self.b_scaleSetup:
                log.debug("|{0}| >> scale blend chain setup...".format(_str_func))                
                RIGCONSTRAINT.blendChainsBy(ml_fkJoints,ml_ikJoints,ml_blendJoints,
                                            driver = mPlug_FKIK.p_combinedName,
                                            l_constraints=['point','orient','scale'])
        
        
                #Scale setup for ik joints                
                ml_ikScaleTargets = [mHeadIK]
        
                if mIKBaseControl:
                    mc.scaleConstraint(mIKBaseControl.mNode, ml_ikJoints[0].mNode,maintainOffset=True)
                    ml_ikScaleTargets.append(mIKBaseControl)
                else:
                    mc.scaleConstraint(mRoot.mNode, ml_ikJoints[0].mNode,maintainOffset=True)
                    ml_ikScaleTargets.append(mRoot)
        
                mc.scaleConstraint(mHeadIK.mNode, ml_ikJoints[-1].mNode,maintainOffset=True)
        
                _targets = [mHandle.mNode for mHandle in ml_ikScaleTargets]
        
                #Scale setup for mid set IK
                if mSegMidIK:
                    mMasterGroup = mSegMidIK.masterGroup
                    _vList = DIST.get_normalizedWeightsByDistance(mMasterGroup.mNode,_targets)
                    _scale = mc.scaleConstraint(_targets,mMasterGroup.mNode,maintainOffset = True)#Point contraint loc to the object
                    CONSTRAINT.set_weightsByDistance(_scale[0],_vList)                
                    ml_ikScaleTargets.append(mSegMidIK)
                    _targets = [mHandle.mNode for mHandle in ml_ikScaleTargets]
        
                for mJnt in ml_ikJoints[1:-1]:
                    _vList = DIST.get_normalizedWeightsByDistance(mJnt.mNode,_targets)
                    _scale = mc.scaleConstraint(_targets,mJnt.mNode,maintainOffset = True)#Point contraint loc to the object
                    CONSTRAINT.set_weightsByDistance(_scale[0],_vList)
        
                for mJnt in ml_ikJoints[1:]:
                    mJnt.p_parent = mIKGroup
                    mJnt.segmentScaleCompensate = False
        
                for mJnt in ml_blendJoints:
                    mJnt.segmentScaleCompensate = False
                    if mJnt == ml_blendJoints[0]:
                        continue
                    mJnt.p_parent = ml_blendJoints[0].p_parent
                    
            else:
                RIGCONSTRAINT.blendChainsBy(ml_fkJoints,ml_ikJoints,ml_blendJoints,
                                            driver = mPlug_FKIK.p_combinedName,
                                            l_constraints=['point','orient'])                

    
def rig_cleanUp(self):
    _short = self.d_block['shortName']
    _str_func = 'rig_cleanUp'
    log.debug("|{0}| >>  ".format(_str_func)+ '-'*80)
    log.debug("{0}".format(self))
    
    mBlock = self.mBlock
    mRigNull = self.mRigNull
    mHeadIK = mRigNull.headIK
    mSettings = mRigNull.settings
    
    mRoot = mRigNull.rigRoot
    if not mRoot.hasAttr('cgmAlias'):
        mRoot.addAttr('cgmAlias','root')    
    
    mMasterControl= self.d_module['mMasterControl']
    mMasterDeformGroup= self.d_module['mMasterDeformGroup']    
    mMasterNull = self.d_module['mMasterNull']
    mModuleParent = self.d_module['mModuleParent']
    mPlug_globalScale = self.d_module['mPlug_globalScale']
    ml_blendjoints = mRigNull.msgList_get('blendJoints')
    
    
    mAttachDriver = mRigNull.getMessageAsMeta('attachDriver')
    mAttachDriver.doStore('cgmAlias', '{0}_partDriver'.format(self.d_module['partName']))
    
    #if not self.mConstrainNull.hasAttr('cgmAlias'):
        #self.mConstrainNull.addAttr('cgmAlias','{0}_rootNull'.format(self.d_module['partName']))    
    
    #>>  Parent and constraining joints and rig parts =======================================================
    #if mSettings != mHeadIK:
        #mSettings.masterGroup.parent = mHeadIK
    
    #>>  DynParentGroups - Register parents for various controls ============================================
    ml_baseDynParents = []
    ml_endDynParents = self.ml_dynParentsAbove + self.ml_dynEndParents# + [mRoot]
    ml_ikDynParents = []    
    """
    #...head -----------------------------------------------------------------------------------
    ml_baseHeadDynParents = []
    
    #ml_headDynParents = [ml_controlsFK[0]]
    if mModuleParent:
        mi_parentRigNull = mModuleParent.rigNull
        if mi_parentRigNull.getMessage('controlIK'):
            ml_baseHeadDynParents.append( mi_parentRigNull.controlIK )	    
        if mi_parentRigNull.getMessage('controlIKBase'):
            ml_baseHeadDynParents.append( mi_parentRigNull.controlIKBase )
        if mi_parentRigNull.getMessage('rigRoot'):
            ml_baseHeadDynParents.append( mi_parentRigNull.rigRoot )
        ml_parentRigJoints =  mi_parentRigNull.msgList_get('rigJoints')
        if ml_parentRigJoints:
            ml_used = []
            for mJnt in ml_parentRigJoints:
                if mJnt in ml_used:continue
                if mJnt in [ml_parentRigJoints[0],ml_parentRigJoints[-1]]:
                    ml_baseHeadDynParents.append( mJnt.masterGroup)
                    ml_used.append(mJnt)
                    
    ml_baseHeadDynParents.append(mMasterNull.puppetSpaceObjectsGroup)"""
    
    #...Root controls ================================================================================
    log.debug("|{0}| >>  Root: {1}".format(_str_func,mRoot))                
    #mParent = mRoot.getParent(asMeta=True)
    ml_targetDynParents = [self.md_dynTargetsParent['attachDriver']]

    if not mRoot.hasAttr('cgmAlias'):
        mRoot.addAttr('cgmAlias','{0}_root'.format(self.d_module['partName']))

    #if not mParent.hasAttr('cgmAlias'):
    #    mParent.addAttr('cgmAlias',self.d_module['partName'] + 'base')
    #ml_targetDynParents.append(mParent)    
    
    ml_targetDynParents.extend(ml_endDynParents)

    mDynGroup = mRoot.dynParentGroup
    #mDynGroup.dynMode = 2

    for mTar in ml_targetDynParents:
        mDynGroup.addDynParent(mTar)
    mDynGroup.rebuild()
    #mDynGroup.dynFollow.p_parent = self.mDeformNull    
    
    
    #...ik controls ==================================================================================
    log.debug("|{0}| >>  IK Handles ... ".format(_str_func))                
    
    ml_ikControls = []
    mControlIK = mRigNull.getMessage('controlIK')
    
    if mControlIK:
        ml_ikControls.append(mRigNull.controlIK)
    if mRigNull.getMessage('controlIKBase'):
        ml_ikControls.append(mRigNull.controlIKBase)
        
    for mHandle in ml_ikControls:
        log.debug("|{0}| >>  IK Handle: {1}".format(_str_func,mHandle))
        
        ml_targetDynParents = ml_baseDynParents + [self.md_dynTargetsParent['attachDriver']] + ml_endDynParents
        
        ml_targetDynParents.append(self.md_dynTargetsParent['world'])
        ml_targetDynParents.extend(mHandle.msgList_get('spacePivots',asMeta = True))
    
        mDynGroup = cgmRIGMETA.cgmDynParentGroup(dynChild=mHandle,dynMode=0)
        #mDynGroup.dynMode = 2
    
        for mTar in ml_targetDynParents:
            mDynGroup.addDynParent(mTar)
        mDynGroup.rebuild()
        #mDynGroup.dynFollow.p_parent = self.mConstrainNull
        
    log.debug("|{0}| >>  IK targets...".format(_str_func))
    pprint.pprint(ml_targetDynParents)        
    
    log.debug(cgmGEN._str_subLine)
              
    
    if mRigNull.getMessage('controlIKMid'):
        log.debug("|{0}| >>  IK Mid Handle ... ".format(_str_func))                
        mHandle = mRigNull.controlIKMid
        
        mParent = mHandle.masterGroup.getParent(asMeta=True)
        ml_targetDynParents = []
    
        if not mParent.hasAttr('cgmAlias'):
            mParent.addAttr('cgmAlias','midIKBase')
        
        mPivotResultDriver = mRigNull.getMessage('pivotResultDriver',asMeta=True)
        if mPivotResultDriver:
            mPivotResultDriver = mPivotResultDriver[0]
        ml_targetDynParents = [mPivotResultDriver,mControlIK,mParent]
        
        ml_targetDynParents.extend(ml_baseDynParents + ml_endDynParents)
        #ml_targetDynParents.extend(mHandle.msgList_get('spacePivots',asMeta = True))
    
        mDynGroup = cgmRIGMETA.cgmDynParentGroup(dynChild=mHandle,dynMode=0)
        #mDynGroup.dynMode = 2
    
        for mTar in ml_targetDynParents:
            mDynGroup.addDynParent(mTar)
        mDynGroup.rebuild()
        #mDynGroup.dynFollow.p_parent = self.mConstrainNull
        
        log.debug("|{0}| >>  IK Mid targets...".format(_str_func,mRoot))
        pprint.pprint(ml_targetDynParents)                
        log.debug(cgmGEN._str_subLine)        
    
    
    """
    #Head -------------------------------------------------------------------------------------------
    ml_headDynParents = []
  
    ml_headDynParents.extend(mHeadIK.msgList_get('spacePivots',asMeta = True))
    ml_headDynParents.extend(ml_endDynParents)
    
    mBlendDriver =  mHeadIK.getMessage('blendDriver',asMeta=True)
    if mBlendDriver:
        mBlendDriver = mBlendDriver[0]
        ml_headDynParents.insert(0, mBlendDriver)  
        mBlendDriver.addAttr('cgmAlias','neckDriver')
    #pprint.pprint(ml_headDynParents)

    #Add our parents
    mDynGroup = mHeadIK.dynParentGroup
    log.info("|{0}| >> dynParentSetup : {1}".format(_str_func,mDynGroup))  
    mDynGroup.dynMode = 2

    for o in ml_headDynParents:
        mDynGroup.addDynParent(o)
    mDynGroup.rebuild()

    mDynGroup.dynFollow.parent = mMasterDeformGroup
    """
    
    #...headLookat ---------------------------------------------------------------------------------------
    if mBlock.headAim:
        log.info("|{0}| >> HeadAim setup...".format(_str_func))
        
        mPlug_aim = cgmMeta.cgmAttr(mSettings.mNode,'blend_aim',attrType='float',lock=False,keyable=True)
        
        #mHeadFKJoint = mRigNull.getMessage('fkHeadJoint', asMeta=True)[0]
        #mHeadAimJoint = mRigNull.getMessage('aimHeadJoint', asMeta=True)[0]
        #mHeadBlendJoint = mRigNull.getMessage('blendHeadJoint', asMeta=True)[0]
        #mHeadFKDynParentGroup = mHeadIK.dynParentGroup
        
        mHeadLookAt = mRigNull.lookAt        
        mHeadLookAt.setAttrFlags(attrs='v')
        
        #...dynParentGroup...
        ml_headLookAtDynParents = []
        ml_headLookAtDynParents.extend(mHeadLookAt.msgList_get('spacePivots',asMeta = True))
        ml_headLookAtDynParents.extend(ml_endDynParents)    
        
        ml_headLookAtDynParents.insert(0, ml_blendjoints[-1])
        if not ml_blendjoints[-1].hasAttr('cgmAlias'):
            ml_blendjoints[-1].addAttr('cgmAlias','blendHead')        
        #mHeadIK.masterGroup.addAttr('cgmAlias','headRoot')
        
        #Add our parents...
        mDynGroup = mHeadLookAt.dynParentGroup
        log.info("|{0}| >> dynParentSetup : {1}".format(_str_func,mDynGroup))  
    
        for o in ml_headLookAtDynParents:
            mDynGroup.addDynParent(o)
        mDynGroup.rebuild()
        
    #...rigJoints =================================================================================
    """
    if mBlock.spaceSwitch_direct:
        log.debug("|{0}| >>  Direct...".format(_str_func))                
        for i,mObj in enumerate(mRigNull.msgList_get('rigJoints')):
            log.debug("|{0}| >>  Direct: {1}".format(_str_func,mObj))                        
            ml_targetDynParents = copy.copy(ml_baseDynParents)
            ml_targetDynParents.extend(mObj.msgList_get('spacePivots',asMeta=True) or [])
    
            mParent = mObj.masterGroup.getParent(asMeta=True)
            if not mParent.hasAttr('cgmAlias'):
                mParent.addAttr('cgmAlias','{0}_rig{1}_base'.format(mObj.cgmName,i))
            ml_targetDynParents.insert(0,mParent)
    
            ml_targetDynParents.extend(ml_endDynParents)
    
            mDynGroup = cgmRIGMETA.cgmDynParentGroup(dynChild=mObj.mNode)
            mDynGroup.dynMode = 2
    
            for mTar in ml_targetDynParents:
                mDynGroup.addDynParent(mTar)
    
            mDynGroup.rebuild()
    
            mDynGroup.dynFollow.p_parent = mRoot """
            
    #...fk controls ============================================================================================
    log.debug("|{0}| >>  FK...".format(_str_func)+'-'*80)                
    ml_fkJoints = self.mRigNull.msgList_get('fkJoints')
    
    for i,mObj in enumerate([ml_fkJoints[0],ml_fkJoints[-1]]):
        if not mObj.getMessage('masterGroup'):
            log.debug("|{0}| >>  Lacks masterGroup: {1}".format(_str_func,mObj))            
            continue
        log.debug("|{0}| >>  FK: {1}".format(_str_func,mObj))
        ml_targetDynParents = copy.copy(ml_baseDynParents)
        ml_targetDynParents.append(self.md_dynTargetsParent['attachDriver'])
        
        mParent = mObj.masterGroup.getParent(asMeta=True)
        if not mParent.hasAttr('cgmAlias'):
            mParent.addAttr('cgmAlias','{0}_base'.format(mObj.p_nameBase))
        _mode = 2
        if i == 0:
            ml_targetDynParents.append(mParent)
            #_mode = 2            
        else:
            ml_targetDynParents.insert(0,mParent)
            #_mode = 1
        
        ml_targetDynParents.extend(ml_endDynParents)
        ml_targetDynParents.extend(mObj.msgList_get('spacePivots',asMeta = True))
    
        mDynGroup = cgmRIGMETA.cgmDynParentGroup(dynChild=mObj.mNode, dynMode=_mode)# dynParents=ml_targetDynParents)
        #mDynGroup.dynMode = 2
    
        for mTar in ml_targetDynParents:
            mDynGroup.addDynParent(mTar)
        mDynGroup.rebuild()

        if _mode == 2:
            mDynGroup.dynFollow.p_parent = mRoot    
        
        log.debug("|{0}| >>  FK targets: {1}...".format(_str_func,mObj))
        pprint.pprint(ml_targetDynParents)                
        log.debug(cgmGEN._str_subLine)    
        
    #Settings =================================================================================
    log.debug("|{0}| >> Settings...".format(_str_func))
    mSettings.visRoot = 0
    mSettings.visDirect = 0
    
    ml_handleJoints = mRigNull.msgList_get('handleJoints')
    if ml_handleJoints:
        ATTR.set_default(ml_handleJoints[0].mNode, 'followRoot', 1.0)
        ml_handleJoints[0].followRoot = 1.0    
        
        
    #Lock and hide =================================================================================
    ml_blendJoints = mRigNull.msgList_get('blendJoints',asMeta=True)
    for mJnt in ml_blendJoints:
        mJnt.dagLock(True)
        
        
    ml_controls = mRigNull.msgList_get('controlsAll')
    
    for mCtrl in ml_controls:
        if mCtrl.hasAttr('radius'):
            ATTR.set_hidden(mCtrl.mNode,'radius',True)
        
        for link in 'masterGroup','dynParentGroup','aimGroup':
            if mCtrl.getMessage(link):
                mCtrl.getMessageAsMeta(link).dagLock(True)
    
    if not mBlock.scaleSetup:
        log.debug("|{0}| >> No scale".format(_str_func))
        ml_controlsToLock = copy.copy(ml_controls)
        if self.b_squashSetup:
            ml_handles = self.mRigNull.msgList_get('handleJoints')
            for mHandle in ml_handles:
                ml_controlsToLock.remove(mHandle)
            for i in self.md_roll.keys():
                mControlMid = mRigNull.getMessageAsMeta('controlSegMidIK_{0}'.format(i))
                if mControlMid:
                    ml_controlsToLock.remove(mControlMid)
    
    
        for mCtrl in ml_controlsToLock:
            ATTR.set_standardFlags(mCtrl.mNode, ['scale'])
    else:
        log.debug("|{0}| >>  scale setup...".format(_str_func))
        
        
    self.mDeformNull.dagLock(True)
    
        
    
    
    #>>  Attribute defaults =================================================================================
    
    mRigNull.version = self.d_block['buildVersion']
    mBlock.blockState = 'rig'

    #>>  Parent and constraining joints and rig parts =======================================================

    #>>  DynParentGroups - Register parents for various controls ============================================
    #>>  Lock and hide ======================================================================================
    #>>  Attribute defaults =================================================================================
    
"""def rig(self):    
    if self.hasRootJoint:
        mJoint = self.doCreateAt('joint')
        mJoint.parent = self.moduleTarget.masterNull.skeletonGroup
        mJoint.connectParentNode(self,'module','rootJoint')
    raise NotImplementedError,"Not done."

def rigDelete(self):
    try:self.moduleTarget.masterControl.delete()
    except Exception,err:
        for a in err:
            print a
    return True

def is_rig(self):
    _str_func = 'is_rig'
    _l_missing = []

    _d_links = {'moduleTarget' : ['masterControl']}

    for plug,l_links in _d_links.iteritems():
        _mPlug = self.getMessage(plug,asMeta=True)
        if not _mPlug:
            _l_missing.append("{0} : {1}".format(plug,l_links))
            continue
        for l in l_links:
            if not _mPlug[0].getMessage(l):
                _l_missing.append(_mPlug[0].p_nameBase + '.' + l)


    if _l_missing:
        log.info("|{0}| >> Missing...".format(_str_func))  
        for l in _l_missing:
            log.info("|{0}| >> {1}".format(_str_func,l))  
        return False
    return True"""

def create_simpleMesh(self,  deleteHistory = True, cap=True):
    _str_func = 'create_simpleMesh'
    log.debug("|{0}| >>  ".format(_str_func)+ '-'*80)
    log.debug("{0}".format(self))
    
    #>> Head ===================================================================================
    log.debug("|{0}| >> Head...".format(_str_func))
    
    mGroup = self.msgList_get('headMeshProxy')[0].getParent(asMeta=True)
    l_headGeo = mGroup.getChildren(asMeta=False)
    ml_headStuff = []
    for i,o in enumerate(l_headGeo):
        log.debug("|{0}| >> geo: {1}...".format(_str_func,o))                    
        if ATTR.get(o,'v'):
            log.debug("|{0}| >> visible head: {1}...".format(_str_func,o))            
            mObj = cgmMeta.validateObjArg(mc.duplicate(o, po=False, ic = False)[0])
            ml_headStuff.append(  mObj )
            mObj.p_parent = False
        

    if self.neckBuild:#...Neck =====================================================================
        log.debug("|{0}| >> neckBuild...".format(_str_func))    
        ml_neckMesh = self.UTILS.create_simpleLoftMesh(self,deleteHistory,cap)
        ml_headStuff.extend(ml_neckMesh)
        
    _mesh = mc.polyUnite([mObj.mNode for mObj in ml_headStuff],ch=False)
    _mesh = mc.rename(_mesh,'{0}_0_geo'.format(self.p_nameBase))
    
    return cgmMeta.validateObjListArg(_mesh)

def asdfasdfasdf(self, forceNew = True, skin = False):
    """
    Build our proxyMesh
    """
    _short = self.d_block['shortName']
    _str_func = 'build_proxyMesh'
    log.debug("|{0}| >>  ".format(_str_func)+ '-'*80)
    log.debug("{0}".format(self))
    
    mBlock = self.mBlock
    mRigNull = self.mRigNull
    mHeadIK = mRigNull.headIK
    mSettings = mRigNull.settings
    mPuppetSettings = self.d_module['mMasterControl'].controlSettings
    
    ml_rigJoints = mRigNull.msgList_get('rigJoints',asMeta = True)
    if not ml_rigJoints:
        raise ValueError,"No rigJoints connected"

    #>> If proxyMesh there, delete --------------------------------------------------------------------------- 
    _bfr = mRigNull.msgList_get('proxyMesh',asMeta=True)
    if _bfr:
        log.debug("|{0}| >> proxyMesh detected...".format(_str_func))            
        if forceNew:
            log.debug("|{0}| >> force new...".format(_str_func))                            
            mc.delete([mObj.mNode for mObj in _bfr])
        else:
            return _bfr
        
    #>> Head ===================================================================================
    log.debug("|{0}| >> Head...".format(_str_func))
    if directProxy:
        log.debug("|{0}| >> directProxy... ".format(_str_func))
        _settings = self.mRigNull.settings.mNode
        
    
    mGroup = mBlock.msgList_get('headMeshProxy')[0].getParent(asMeta=True)
    l_headGeo = mGroup.getChildren(asMeta=False)
    l_vis = mc.ls(l_headGeo, visible = True)
    ml_headStuff = []
    
    for i,o in enumerate(l_vis):
        log.debug("|{0}| >> visible head: {1}...".format(_str_func,o))
        
        mObj = cgmMeta.validateObjArg(mc.duplicate(o, po=False, ic = False)[0])
        ml_headStuff.append(  mObj )
        mObj.parent = ml_rigJoints[-1]
        
        ATTR.copy_to(ml_rigJoints[-1].mNode,'cgmName',mObj.mNode,driven = 'target')
        mObj.addAttr('cgmIterator',i)
        mObj.addAttr('cgmType','proxyGeo')
        mObj.doName()
        
        if directProxy:
            CORERIG.shapeParent_in_place(ml_rigJoints[-1].mNode,mObj.mNode,True,False)
            CORERIG.colorControl(ml_rigJoints[-1].mNode,_side,'main',directProxy=True)        
        
    if mBlock.neckBuild:#...Neck =====================================================================
        log.debug("|{0}| >> neckBuild...".format(_str_func))


def build_proxyMesh(self, forceNew = True, puppetMeshMode = False):
    """
    Build our proxyMesh
    """
    _short = self.d_block['shortName']
    _str_func = 'build_proxyMesh'
    log.debug("|{0}| >>  ".format(_str_func)+ '-'*80)
    log.debug("{0}".format(self))
    
    mBlock = self.mBlock
    mRigNull = self.mRigNull
    mHeadIK = mRigNull.headIK
    mSettings = mRigNull.settings
    mPuppetSettings = self.d_module['mMasterControl'].controlSettings
    
    directProxy = mBlock.proxyDirect
    
    _side = BLOCKUTILS.get_side(self.mBlock)
    ml_neckProxy = []
    
    ml_rigJoints = mRigNull.msgList_get('rigJoints',asMeta = True)
    if not ml_rigJoints:
        raise ValueError,"No rigJoints connected"
    
    #>> If proxyMesh there, delete --------------------------------------------------------------------------- 
    if puppetMeshMode:
        _bfr = mRigNull.msgList_get('puppetProxyMesh',asMeta=True)
        if _bfr:
            log.debug("|{0}| >> puppetProxyMesh detected...".format(_str_func))            
            if forceNew:
                log.debug("|{0}| >> force new...".format(_str_func))                            
                mc.delete([mObj.mNode for mObj in _bfr])
            else:
                return _bfr        
    else:
        _bfr = mRigNull.msgList_get('proxyMesh',asMeta=True)
        if _bfr:
            log.debug("|{0}| >> proxyMesh detected...".format(_str_func))            
            if forceNew:
                log.debug("|{0}| >> force new...".format(_str_func))                            
                mc.delete([mObj.mNode for mObj in _bfr])
            else:
                return _bfr
        
    #>> Head ===================================================================================
    log.debug("|{0}| >> Head...".format(_str_func))
    if directProxy:
        log.debug("|{0}| >> directProxy... ".format(_str_func))
        _settings = self.mRigNull.settings.mNode
        
    if directProxy:
        for mJnt in ml_rigJoints:
            for shape in mJnt.getShapes():
                mc.delete(shape)
    mGroup = mBlock.msgList_get('headMeshProxy')[0].getParent(asMeta=True)
    
    l_headGeo = mGroup.getChildren(asMeta=False)
    #l_vis = mc.ls(l_headGeo, visible = True)
    ml_segProxy = []
    ml_headStuff = []
    if puppetMeshMode:
        log.debug("|{0}| >> puppetMesh setup... ".format(_str_func))
        ml_moduleJoints = mRigNull.msgList_get('moduleJoints')
        
        if mBlock.neckBuild:
            if mBlock.neckJoints == 1:
                mProxy = ml_moduleJoints[0].doCreateAt(setClass=True)
                mPrerigProxy = mBlock.getMessage('prerigLoftMesh',asMeta=True)[0]
                CORERIG.shapeParent_in_place(mProxy.mNode, mPrerigProxy.mNode)
                
                ATTR.copy_to(ml_moduleJoints[0].mNode,'cgmName',mProxy.mNode,driven = 'target')
                mProxy.addAttr('cgmType','proxyPuppetGeo')
                mProxy.doName()
                mProxy.parent = ml_moduleJoints[0]
                ml_segProxy = [mProxy]

                
            else:
                ml_segProxy = cgmMeta.validateObjListArg(self.atBuilderUtils('mesh_proxyCreate', ml_moduleJoints),'cgmObject')
                log.debug("|{0}| >> created: {1}".format(_str_func,ml_neckProxy))
                
                for i,mGeo in enumerate(ml_neckProxy):
                    mGeo.parent = ml_moduleJoints[i]
                    mGeo.doStore('cgmName',self.d_module['partName'])
                    mGeo.addAttr('cgmIterator',i+1)
                    mGeo.addAttr('cgmType','proxyPuppetGeo')
                    mGeo.doName()
                    ml_segProxy.append(mGeo)
        
        for i,o in enumerate(l_headGeo):
            log.debug("|{0}| >> geo: {1}...".format(_str_func,o))                    
            if ATTR.get(o,'v'):
                log.debug("|{0}| >> visible head: {1}...".format(_str_func,o))            
                mGeo = cgmMeta.validateObjArg(mc.duplicate(o, po=False, ic = False)[0])
                mGeo.parent = ml_moduleJoints[-1]
                mGeo.doStore('cgmName',self.d_module['partName'])
                mGeo.addAttr('cgmTypeModifier','end')
                mGeo.addAttr('cgmType','proxyPuppetGeo')
                mGeo.doName()
                
                ml_segProxy.append( mGeo )
            

                    
        
        mRigNull.msgList_connect('puppetProxyMesh', ml_segProxy)
        return ml_segProxy    
    
    
    
    
    for i,o in enumerate(l_headGeo):
        log.debug("|{0}| >> geo: {1}...".format(_str_func,o))                    
        if ATTR.get(o,'v'):
            log.debug("|{0}| >> visible head: {1}...".format(_str_func,o))            
            mObj = cgmMeta.validateObjArg(mc.duplicate(o, po=False, ic = False)[0])
            ml_headStuff.append(  mObj )
            mObj.p_parent = False
            mObj.parent = ml_rigJoints[-1]
            
            ATTR.copy_to(ml_rigJoints[-1].mNode,'cgmName',mObj.mNode,driven = 'target')
            mObj.addAttr('cgmIterator',i)
            mObj.addAttr('cgmType','proxyGeo')
            mObj.doName()
            
            if directProxy:
                CORERIG.shapeParent_in_place(ml_rigJoints[-1].mNode,mObj.mNode,True,False)
                CORERIG.colorControl(ml_rigJoints[-1].mNode,_side,'main',directProxy=True)        
        
    if mBlock.neckBuild:#...Neck =====================================================
        log.debug("|{0}| >> neckBuild...".format(_str_func))
        
        # Create ---------------------------------------------------------------------------
        if mBlock.neckJoints == 1:
            mProxy = ml_rigJoints[0].doCreateAt(setClass=True)
            mPrerigProxy = mBlock.getMessage('prerigLoftMesh',asMeta=True)[0]
            CORERIG.shapeParent_in_place(mProxy.mNode, mPrerigProxy.mNode)
            
            ATTR.copy_to(ml_rigJoints[0].mNode,'cgmName',mProxy.mNode,driven = 'target')
            mProxy.addAttr('cgmType','proxyGeo')
            mProxy.doName()
            mProxy.parent = ml_rigJoints[0]
            ml_neckProxy = [mProxy]
            
            if directProxy:
                CORERIG.shapeParent_in_place(ml_rigJoints[0].mNode,mProxy.mNode,True,False)
                CORERIG.colorControl(ml_rigJoints[0].mNode,_side,'main',directProxy=True)            
            
        else:
            ml_neckProxy = cgmMeta.validateObjListArg(self.atBuilderUtils('mesh_proxyCreate', ml_rigJoints),'cgmObject')
            log.debug("|{0}| >> created: {1}".format(_str_func,ml_neckProxy))
            
            for i,mGeo in enumerate(ml_neckProxy):
                mGeo.parent = ml_rigJoints[i]
                ATTR.copy_to(ml_rigJoints[0].mNode,'cgmName',mGeo.mNode,driven = 'target')
                mGeo.addAttr('cgmIterator',i+1)
                mGeo.addAttr('cgmType','proxyGeo')
                mGeo.doName()
                
                if directProxy:
                    CORERIG.shapeParent_in_place(ml_rigJoints[i].mNode,mGeo.mNode,True,False)
                    CORERIG.colorControl(ml_rigJoints[i].mNode,_side,'main',directProxy=True)                
    
    for mProxy in ml_neckProxy + ml_headStuff:
        CORERIG.colorControl(mProxy.mNode,_side,'main',transparent=False,proxy=True)
        mc.makeIdentity(mProxy.mNode, apply = True, t=1, r=1,s=1,n=0,pn=1)

        #Vis connect -----------------------------------------------------------------------
        mProxy.overrideEnabled = 1
        ATTR.connect("{0}.proxyVis".format(mPuppetSettings.mNode),"{0}.visibility".format(mProxy.mNode) )
        ATTR.connect("{0}.proxyLock".format(mPuppetSettings.mNode),"{0}.overrideDisplayType".format(mProxy.mNode) )
        for mShape in mProxy.getShapes(asMeta=1):
            str_shape = mShape.mNode
            mShape.overrideEnabled = 0
            #ATTR.connect("{0}.proxyVis".format(mPuppetSettings.mNode),"{0}.visibility".format(str_shape) )
            ATTR.connect("{0}.proxyLock".format(mPuppetSettings.mNode),"{0}.overrideDisplayTypes".format(str_shape) )
            
    if directProxy:
        for mObj in ml_rigJoints:
            for mShape in mObj.getShapes(asMeta=True):
                #mShape.overrideEnabled = 0
                mShape.overrideDisplayType = 0
                ATTR.connect("{0}.visDirect".format(_settings), "{0}.overrideVisibility".format(mShape.mNode))
        
    mRigNull.msgList_connect('proxyMesh', ml_neckProxy + ml_headStuff)




















