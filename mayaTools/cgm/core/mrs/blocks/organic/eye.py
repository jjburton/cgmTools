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
                       'rig_frame',
                       'rig_cleanUp']




d_wiring_skeleton = {'msgLinks':[],
                     'msgLists':['moduleJoints','skinJoints']}
d_wiring_prerig = {'msgLinks':['moduleTarget','prerigNull']}
d_wiring_template = {'msgLinks':['templateNull','eyeOrientHelper','rootHelper'],
                     }
d_wiring_extraDags = {'msgLinks':['bbHelper'],
                      'msgLists':[]}
#>>>Profiles ==============================================================================================
d_build_profiles = {}


d_block_profiles = {'default':{},
                    'eye':{'baseSize':[2.7,2.7,2.7],
                           'eyeType':'sphere',
                           'ikSetup':True,
                           'setupLid':'none',
                           },
                    'eyeClamLid':{
                        'baseSize':[2.7,2.7,2.7],
                        'eyeType':'sphere',
                        'ikSetup':True,
                        'setupLid':'clam',
                        'numLidUpr':1,
                        'numLidLwr':1,
                           }}



#>>>Attrs =================================================================================================
l_attrsStandard = ['side',
                   'position',
                   #'baseUp',
                   'baseAim',
                   'attachPoint',
                   'nameList',
                   #'loftSides',
                   #'loftDegree',
                   #'loftSplit',
                   #'loftShape',
                   'numSpacePivots',
                   'scaleSetup',
                   #'offsetMode',
                   'proxyDirect',
                   #'settingsDirection',
                   'moduleTarget',]

d_attrsToMake = {'eyeType':'sphere:nonsphere',
                 'hasEyeOrb':'bool',
                 'ikSetup':'bool',
                 'setupPupil':'none:joint:blendshape',
                 'setupIris':'none:joint:blendshape',
                 'setupLid':'none:clam:full',
                 'numLidUpr':'int',
                 'numLidLwr':'int',
                 
                 
}

d_defaultSettings = {'version':__version__,
                     'proxyDirect':True,
                     'attachPoint':'end',
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
    
    
    if self.hasEyeOrb:
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
        
    if self.setupLid:
        log.debug("|{0}| >> EyeLid setup...".format(_str_func))
        mHandleFactory.add_lidsHelper()
        
    self.blockState = 'template'
    return


#=============================================================================================================
#>> Prerig
#=============================================================================================================
def prerigDelete(self):
    try:self.moduleEyelid.delete()
    except:pass
    
def prerig(self):
    _str_func = 'prerig'
    log.debug("|{0}| >>  {1}".format(_str_func,self)+ '-'*80)
    self.blockState = 'prerig'
    _side = self.UTILS.get_side(self)
    
    self.atUtils('module_verify')
    mStateNull = self.UTILS.stateNull_verify(self,'prerig')
    
    mRoot = self.getMessageAsMeta('rootHelper')
    mHandleFactory = self.asHandleFactory()
    
    ml_handles = []
    #Settings shape --------------------
    if self.ikSetup or self.hasEyeOrb:
        log.debug("|{0}| >> Settings/Orb setup ... ".format(_str_func)) 
        
        _size_bb = mHandleFactory.get_axisBox_size(self.getMessage('bbHelper'))
        _size = MATH.average(_size_bb)
        
        mSettingsShape = cgmMeta.validateObjArg(CURVES.create_fromName('gear',_size * .25,
                                                                       'z+'),'cgmObject',setClass=True)
        
        mSettingsShape.doSnapTo(mRoot.mNode)
        
        d_directions = {'left':'x+','right':'x-','center':'z+'}
        str_settingsDirections = d_directions.get(_side,'z+')
        
        mSettingsShape.p_position = self.getPositionByAxisDistance(str_settingsDirections,
                                                                    _size_bb[1] * .7)
        
        mSettingsShape.p_parent = mStateNull
        
        mSettingsShape.doStore('cgmName','settingsShape')
        mSettingsShape.doStore('cgmType','prerigHandle')
        mSettingsShape.doName()
        
        self.connectChildNode(mSettingsShape.mNode,'settingsHelper','module')
        mHandleFactory.color(mSettingsShape.mNode,controlType='sub')
        
        ml_handles.append(mSettingsShape)
        """
        d_directions = {'up':'y+','down':'y-','in':'x+','out':'x-'}
        str_settingsDirections = d_directions.get(mBlock.getEnumValueString('settingsDirection'),'y+')
        mSettingsShape.p_position = _mTar.getPositionByAxisDistance(str_settingsDirections,
                                                                    _settingsSize)
    
        SNAP.aim_atPoint(mSettingsShape.mNode,
                         _mTar.p_position,
                         aimAxis=_jointOrientation[0]+'+',
                         mode = 'vector',
                         vectorUp= _mTar.getAxisVector(_jointOrientation[0]+'-'))
    
        mSettingsShape.parent = _mTar
        mSettings = mSettingsShape
        CORERIG.match_orientation(mSettings.mNode, _mTar.mNode)
    
        ATTR.copy_to(_short_module,'cgmName',mSettings.mNode,driven='target')
    
        mSettings.doStore('cgmTypeModifier','settings')
        mSettings.doName()
        mHandleFactory.color(mSettings.mNode, controlType = 'sub')
    
        mRigNull.connectChildNode(mSettings,'settings','rigNull')#Connect        
        """
    
    if self.setupLid:
        _setupLid = self.getEnumValueString('setupLid')
        log.debug("|{0}| >> EyeLid setup: {1}.".format(_str_func,_setupLid))
        
        mModule_lids = self.atUtils('module_verify','eyelid','moduleEyelid')
        
        if _setupLid == 'clam':
            pass
        
    
    
    self.msgList_connect('prerigHandles', ml_handles)
    
    #Close out ===============================================================================================
    #mNoTransformNull.v = False
    #cgmGEN.func_snapShot(vars())
    self.blockState = 'prerig'
    
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
    
    _radius = self.atUtils('get_shapeOffset')# or 1
    ml_joints = []
    
    mModule = self.atUtils('module_verify')
    
    mRigNull = mModule.rigNull
    if not mRigNull:
        raise ValueError,"No rigNull connected"
    
    mPrerigNull = self.prerigNull
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
            log.debug("|{0}| >> {1} | {2}.".format(_str_func,t,v))            
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
    
    mRoot = mEyeJoint
    #>> Eye =================================================================================== 
    if self.hasEyeOrb:
        mEyeOrbJoint = mEyeJoint.doDuplicate()
        self.copyAttrTo(_baseNameAttrs[1],mEyeOrbJoint.mNode,'cgmName',driven='target')
        name(mEyeOrbJoint,_d_base)
        
        mEyeJoint.p_parent = mEyeOrbJoint
        ml_joints.insert(0,mEyeOrbJoint)
        mPrerigNull.connectChildNode(mEyeOrbJoint.mNode,'eyeOrbJoint')
        mRoot = mEyeOrbJoint
        
    
    

            
    mRigNull.msgList_connect('moduleJoints', ml_joints)
    self.msgList_connect('moduleJoints', ml_joints)
    self.atBlockUtils('skeleton_connectToParent')
    
    if len(ml_joints) > 1:
        ml_joints[0].getParent(asMeta=1).radius = ml_joints[-1].radius * 5
        
    if self.setupLid:#=====================================================
        _setupLid = self.getEnumValueString('setupLid')
        log.debug("|{0}| >> EyeLid setup: {1}.".format(_str_func,_setupLid))
        mLidsHelper = self.getMessageAsMeta('lidsHelper')
        _d_lids = copy.copy(_d_base)
        
        _d_lids['cgmNameModifier'] = 'lid'
        
        if _setupLid == 'clam':
            for a in ['upr','lwr']:
                log.debug("|{0}| >> Creating lid joint: {1}.".format(_str_func,a))
                _a = 'lid{0}'.format(a.capitalize())
                mHandle = mLidsHelper.getMessageAsMeta(_a)
                mJoint = mHandle.doCreateAt('joint')
                mJoint.parent = mRoot
                
                mJoint.doStore('cgmName',a)
                name(mJoint,_d_lids)
                
                log.debug("|{0}| >> joint: {1} | {2}.".format(_str_func,mJoint,mJoint.parent))                
                

        else:
            log.error("Don't have setup for eyelidType: {0}".format(_setupLid))
    

    for mJnt in ml_joints:
        mJnt.displayLocalAxis = 1
        mJnt.radius = _radius
        
    return ml_joints    

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
    ml_handleJoints = mPrerigNull.msgList_get('handleJoints')
    mMasterNull = self.d_module['mMasterNull']
    
    mEyeTemplateHandle = mBlock.bbHelper
    
    self.mRootTemplateHandle = mEyeTemplateHandle
    ml_templateHandles = [mEyeTemplateHandle]
    
    
    self.b_scaleSetup = mBlock.scaleSetup
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
    
    #Size =======================================================================================
    self.v_baseSize = [mBlock.blockScale * v for v in mBlock.baseSize]
    self.f_sizeAvg = MATH.average(self.v_baseSize)
    
    log.debug("|{0}| >> size | self.v_baseSize: {1} | self.f_sizeAvg: {2}".format(_str_func,self.v_baseSize, self.f_sizeAvg ))
    
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
    
    
    #eyeLook =============================================================================
    self.mEyeLook = self.atUtils('eyeLook_get',True)#autobuild...

    return True


@cgmGEN.Timer
def rig_skeleton(self):
    _short = self.d_block['shortName']
    
    _str_func = 'rig_skeleton'
    log.debug("|{0}| >>  ".format(_str_func)+ '-'*80)
    log.debug("{0}".format(self))
        
    mBlock = self.mBlock
    mRigNull = self.mRigNull
    mPrerigNull = mBlock.prerigNull
    
    ml_jointsToConnect = []
    ml_jointsToHide = []
    ml_joints = mRigNull.msgList_get('moduleJoints')
    self.d_joints['ml_moduleJoints'] = ml_joints
    
    log.info("|{0}| >> Eye...".format(_str_func))
    
    BLOCKUTILS.skeleton_pushSettings(ml_joints, self.d_orientation['str'], self.d_module['mirrorDirection'])
                                     #d_rotateOrders, d_preferredAngles)
    
    ml_rigJoints = BLOCKUTILS.skeleton_buildDuplicateChain(mBlock,
                                                           ml_joints, 'rig',
                                                           self.mRigNull,
                                                           'rigJoints',
                                                           'rig',
                                                           blockNames=False)
    
    mEyeJoint = mPrerigNull.getMessageAsMeta('eyeJoint')
    mEyeRigJoint = mEyeJoint.getMessageAsMeta('rigJoint')
    log.info(mEyeJoint)
    log.info(mEyeRigJoint)
    
    mRigNull.connectChildNode(mEyeRigJoint,'directEye')
    
    if mBlock.ikSetup:
        log.info("|{0}| >> Eye IK...".format(_str_func))              
        mEyeFK = BLOCKUTILS.skeleton_buildDuplicateChain(mBlock,[mEyeJoint],
                                                         'fk', mRigNull,
                                                         'fkEye',
                                                         singleMode = True)[0]
        
        mEyeIK = BLOCKUTILS.skeleton_buildDuplicateChain(mBlock,[mEyeJoint],
                                                         'ik', mRigNull,
                                                         'ikEye',
                                                         singleMode = True)[0]
        
        mEyeBlend = BLOCKUTILS.skeleton_buildDuplicateChain(mBlock,[mEyeJoint],
                                                            'blend', mRigNull,
                                                            'blendEye',
                                                            singleMode = True)[0]        
        for mJnt in mEyeFK,mEyeIK,mEyeBlend:
            mJnt.p_parent = mEyeRigJoint.p_parent
        
        mEyeRigJoint.p_parent = mEyeBlend
        
        ml_jointsToConnect.extend([mEyeIK])
        ml_jointsToHide.append(mEyeBlend)    
    
            
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
    try:
        _short = self.d_block['shortName']
        _str_func = 'rig_shapes'
        log.debug("|{0}| >>  ".format(_str_func)+ '-'*80)
        log.debug("{0}".format(self))
        
    
        mBlock = self.mBlock
        _baseNameAttrs = ATTR.datList_getAttrs(mBlock.mNode,'nameList')    
        mHandleFactory = mBlock.asHandleFactory()
        mRigNull = self.mRigNull
        mPrerigNull = mBlock.prerigNull
        
        ml_rigJoints = mRigNull.msgList_get('rigJoints')
        
        if mBlock.hasEyeOrb or mBlock.ikSetup:
            log.debug("|{0}| >> Settings needed...".format(_str_func))
            mSettingsHelper = mBlock.getMessageAsMeta('settingsHelper')
            if not mSettingsHelper:
                raise ValueError,"Settings helper should have been generated during prerig phase. Please go back"
            log.debug(mSettingsHelper)
            
            if mBlock.hasEyeOrb:
                log.debug("|{0}| >> EyeOrb Settings...".format(_str_func))
                mEyeOrbJoint = mPrerigNull.getMessageAsMeta('eyeOrbJoint')
                mEyeOrbRigJoint = mEyeOrbJoint.getMessageAsMeta('rigJoint')
                CORERIG.shapeParent_in_place(mEyeOrbRigJoint.mNode,mSettingsHelper.mNode,False)
                mSettings = mEyeOrbRigJoint
            else:
                mSettings = mSettingsHelper.doCreateAt()
                CORERIG.shapeParent_in_place(mSettings.mNode,mSettings.mNode,True)
                
            mSettings.doStore('mClass','cgmObject')
            mSettings.doStore('cgmName','eyeRoot')
            mSettings.doName()
                
            mRigNull.connectChildNode(mSettings,'settings','rigNull')#Connect
            
        #Logic ====================================================================================
        mFKEye = mRigNull.getMessageAsMeta('fkEye')
        if mFKEye:
            log.debug("|{0}| >> FK eye...".format(_str_func))  
            log.debug(mFKEye)
            
            _shape_fk = CURVES.create_fromName('sphere', size = [v*1.1 for v in self.v_baseSize])
            SNAP.go(_shape_fk,mFKEye.mNode)
            mHandleFactory.color(_shape_fk, controlType = 'main')
            CORERIG.shapeParent_in_place(mFKEye.mNode,_shape_fk,False)
            
            #mShape = mBlock.getMessageAsMeta('bbHelper').doDuplicate()
            
        
        mIKEye = mRigNull.getMessageAsMeta('ikEye')
        if mIKEye:
            log.debug("|{0}| >> IK eye...".format(_str_func))  
            log.debug(mIKEye)
            
            #Create shape... -----------------------------------------------------------------------        
            log.debug("|{0}| >> Creating shape...".format(_str_func))
            mIKControl = cgmMeta.asMeta( CURVES.create_fromName('eye',
                                                                direction = 'z+',
                                                                size = self.f_sizeAvg * .5 ,
                                                                absoluteSize=False),'cgmObject',setClass=True)
            mIKControl.doSnapTo(mBlock.mNode)
            pos = mBlock.getPositionByAxisDistance('z+',
                                                   self.f_sizeAvg * 4)
        
            mIKControl.p_position = pos
        
            
            if mIKEye.hasAttr('cgmDirection'):
                mIKControl.doStore('cgmDirection',mIKEye.cgmDirection)
            mIKControl.doStore('cgmName',mIKEye.cgmName)
            
            mHandleFactory.color(mIKControl.mNode)
    
            mIKControl.doName()
            
            mIKControl.p_parent = self.mEyeLook
            
            mRigNull.connectChildNode(mIKControl,'controlIK','rigNull')#Connect
            
        mDirectEye = mRigNull.getMessageAsMeta('directEye')
        if mDirectEye:#Direct Eye =======================================================================
            log.debug("|{0}| >> direct eye...".format(_str_func))  
            log.debug(mDirectEye)
            
            trackcrv= CORERIG.create_at(l_pos=[mDirectEye.p_position,
                                               mBlock.getPositionByAxisDistance('z+',
                                               self.f_sizeAvg * 1.5)],#ml_handleJoints[1]],
                                        create='curveLinear',
                                        baseName = '{0}_eyeTrack'.format(self.d_module['partName']))
        
            
            CORERIG.shapeParent_in_place(mDirectEye,trackcrv,False)
            mHandleFactory = mBlock.asHandleFactory()
            mHandleFactory.color(mDirectEye.mNode, controlType = 'sub')
            
            #for s in mDirectEye.getShapes(asMeta=True):
                #s.overrideEnabled = 1
                #s.overrideDisplayType = 2
            
            
        for mJnt in ml_rigJoints:
            try:
                mJnt.drawStyle =2
            except:
                mJnt.radius = .00001                
        return
    except Exception,error:
        cgmGEN.cgmException(Exception,error,msg=vars())


@cgmGEN.Timer
def rig_controls(self):
    try:
        _short = self.d_block['shortName']
        _str_func = 'rig_controls'
        log.debug("|{0}| >>  ".format(_str_func)+ '-'*80)
        log.debug("{0}".format(self))
      
        mRigNull = self.mRigNull
        mBlock = self.mBlock
        ml_controlsAll = []#we'll append to this list and connect them all at the end
        mRootParent = self.mDeformNull
        
        d_controlSpaces = self.atBuilderUtils('get_controlSpaceSetupDict')
        
        mControlFK = mRigNull.getMessageAsMeta('fkEye')
        mControlIK = mRigNull.getMessageAsMeta('controlIK')
        mSettings = mRigNull.getMessageAsMeta('settings')
        mBlendJoint = mRigNull.getMessageAsMeta('blendEye')
        mDirect = mRigNull.getMessageAsMeta('directEye')
        
        # Drivers ==========================================================================================    
        if mBlock.ikSetup:
            mPlug_FKIK = cgmMeta.cgmAttr(mSettings.mNode,'FKIK',attrType='float',minValue=0,maxValue=1,lock=False,keyable=True)
            
    
        #>> vis Drivers ==============================================================================	
        mPlug_visSub = self.atBuilderUtils('build_visSub')
        mPlug_visDirect = cgmMeta.cgmAttr(mSettings,'visDirect', value = True,
                                          attrType='bool', defaultValue = False,
                                          keyable = False,hidden = False)
        
        #Settings ========================================================================================
        if mSettings:
            log.info("|{0}| >> Found settings : {1}".format(_str_func, mSettings))
            
            _d = MODULECONTROL.register(mSettings,
                                        addDynParentGroup = False,
                                        mirrorSide= self.d_module['mirrorDirection'],
                                        mirrorAxis="translateX,rotateY,rotateZ")
            
            mSettings = _d['mObj']
            ml_controlsAll.append(mSettings)
            
        
        
        #FK ========================================================================================    
        log.info("|{0}| >> Found fk : {1}".format(_str_func, mControlFK))
        
        _d = MODULECONTROL.register(mControlFK,
                                    mirrorSide= self.d_module['mirrorDirection'],
                                    mirrorAxis="translateX,rotateY,rotateZ",
                                    makeAimable = True)
        
        mControlFK = _d['mObj']
        ml_controlsAll.append(mControlFK)
        if mBlendJoint:
            self.atUtils('get_switchTarget', mControlFK, mBlendJoint)
                
        #ik ========================================================================================
        if mControlIK:
            log.info("|{0}| >> Found ik : {1}".format(_str_func, mControlIK))
            
            _d = MODULECONTROL.register(mControlIK,
                                        addDynParentGroup = True,
                                        mirrorSide= self.d_module['mirrorDirection'],
                                        mirrorAxis="translateX,rotateY,rotateZ",
                                        makeAimable = True,
                                        **d_controlSpaces)
            
            mControlIK = _d['mObj']
            ml_controlsAll.append(mControlIK)
            self.atUtils('get_switchTarget', mControlIK, mBlendJoint)
        
        #>> Direct Controls ==================================================================================
        log.debug("|{0}| >> Direct controls...".format(_str_func))
        
        #ml_rigJoints = self.mRigNull.msgList_get('rigJoints')
        ml_controlsAll.extend([mDirect])
        
        for i,mObj in enumerate([mDirect]):
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
        log.debug(cgmGEN._str_subLine)        

            
            
        #Close out...
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
        """
        if mHeadIK:
            ATTR.set(mHeadIK.mNode,'rotateOrder',self.ro_head)
        if mHeadLookAt:
            ATTR.set(mHeadLookAt.mNode,'rotateOrder',self.ro_headLookAt)
            """
        
        mRigNull.msgList_connect('controlsAll',ml_controlsAll)
        mRigNull.moduleSet.extend(ml_controlsAll)
        
    except Exception,error:
        cgmGEN.cgmException(Exception,error,msg=vars())


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
    
    mControlFK = mRigNull.getMessageAsMeta('fkEye')
    mJointFK = mControlFK
    mJointIK = mRigNull.getMessageAsMeta('ikEye')
    mControlIK = mRigNull.getMessageAsMeta('controlIK')
    mSettings = mRigNull.getMessageAsMeta('settings')
    mBlendJoint = mRigNull.getMessageAsMeta('blendEye')
    mDirect = mRigNull.getMessageAsMeta('directEye')
    
    ml_joints = [mJointFK,mJointIK,mBlendJoint,mSettings,mDirect]
    
    pprint.pprint(vars())
    
    log.debug("|{0}| >> Adding to attach driver...".format(_str_func))
    self.mDeformNull.p_parent = self.md_dynTargetsParent['attachDriver'].mNode    
    if mSettings:
        mSettings.masterGroup.p_parent = self.mDeformNull
        
    """
    #Mid IK trace ------------------------------------------------------
    log.debug("|{0}| >> eye track Crv".format(_str_func))
    trackcrv= CORERIG.create_at(l_pos=[mDirect.p_position,
                                       mBlock.getPositionByAxisDistance('z+',
                                       self.f_sizeAvg * 2)],#ml_handleJoints[1]],
                                create='curveLinear',
                                baseName = '{0}_eyeTrack'.format(self.d_module['partName']))

    
    mTrackCrv = mDirect.doCreateAt(setClass=True)
    CORERIG.shapeParent_in_place(mTrackCrv,trackcrv,False)
    mTrackCrv.p_parent = mSettings
    mHandleFactory = mBlock.asHandleFactory()
    mHandleFactory.color(mTrackCrv.mNode, controlType = 'sub')
    
    for s in mTrackCrv.getShapes(asMeta=True):
        s.overrideEnabled = 1
        s.overrideDisplayType = 2
    #mTrackCrv.doConnectIn('visibility',"{0}.v".format(mIKGroup.mNode))    
    mc.orientConstraint(mDirect.mNode,mTrackCrv.mNode)
    """


    if mBlock.ikSetup:
        mPlug_FKIK = cgmMeta.cgmAttr(mSettings.mNode,'FKIK'
                                     )    
        #Aim setup ---------------------------------------------------------------
        log.info("|{0}| >> Aim setup...".format(_str_func, mControlIK))    
        mc.aimConstraint(mControlIK.mNode,
                         mJointIK.mNode,
                         maintainOffset = False, weight = 1,
                         aimVector = self.d_orientation['vectorAim'],
                         upVector = self.d_orientation['vectorUp'],
                         worldUpVector = self.d_orientation['vectorUp'],
                         worldUpObject = mSettings.mNode,
                         worldUpType = 'objectRotation' )
        
        
        #>>> Setup a vis blend result
        mPlug_FKon = cgmMeta.cgmAttr(mSettings,'result_FKon',attrType='float',defaultValue = 0,keyable = False,lock=True,hidden=True)	
        mPlug_IKon = cgmMeta.cgmAttr(mSettings,'result_IKon',attrType='float',defaultValue = 0,keyable = False,lock=True,hidden=True)	
    
        NODEFACTORY.createSingleBlendNetwork(mPlug_FKIK.p_combinedName,
                                             mPlug_IKon.p_combinedName,
                                             mPlug_FKon.p_combinedName)
    
        #IK...
        mIKGroup = mSettings.doCreateAt()
        mIKGroup.doStore('cgmName',self.d_module['partName'])
        mIKGroup.doStore('cgmTypeModifier','ik')
        mIKGroup.doName()
        mPlug_IKon.doConnectOut("{0}.visibility".format(mIKGroup.mNode))
    
        mIKGroup.parent = mSettings
        mControlIK.masterGroup.parent = mIKGroup
        mJointIK.p_parent = mIKGroup
        
        #FK...
        FKGroup = mSettings.doCreateAt()
        FKGroup.doStore('cgmName',self.d_module['partName'])        
        FKGroup.doStore('cgmTypeModifier','FK')
        FKGroup.doName()
        mPlug_FKon.doConnectOut("{0}.visibility".format(FKGroup.mNode))
    
        FKGroup.parent = mSettings
        mControlFK.masterGroup.parent = FKGroup        
        
        
    #Setup blend ----------------------------------------------------------------------------------
    log.debug("|{0}| >> blend setup...".format(_str_func))
      
    if self.b_scaleSetup :
        log.debug("|{0}| >> scale blend chain setup...".format(_str_func))    
        
        if mBlock.ikSetup:
            RIGCONSTRAINT.blendChainsBy(mJointFK,mJointIK,mBlendJoint,
                                        driver = mPlug_FKIK.p_combinedName,
                                        l_constraints=['point','orient','scale'])
            
        for mJnt in ml_joints:
            mJnt.segmentScaleCompensate = False
            
            
    else:
        #Setup blend ----------------------------------------------------------------------------------
        RIGCONSTRAINT.blendChainsBy(mJointFK,mJointIK,mBlendJoint,
                                    driver = mPlug_FKIK.p_combinedName,l_constraints=['point','orient'])
    
    


    
    return
            
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
    
    mMasterControl= self.d_module['mMasterControl']
    mMasterDeformGroup= self.d_module['mMasterDeformGroup']    
    mMasterNull = self.d_module['mMasterNull']
    mModuleParent = self.d_module['mModuleParent']
    mPlug_globalScale = self.d_module['mPlug_globalScale']
    
    mControlFK = mRigNull.getMessageAsMeta('fkEye')
    mJointFK = mControlFK
    mJointIK = mRigNull.getMessageAsMeta('ikEye')
    mControlIK = mRigNull.getMessageAsMeta('controlIK')
    mSettings = mRigNull.getMessageAsMeta('settings')
    mBlendJoint = mRigNull.getMessageAsMeta('blendEye')
    mDirect = mRigNull.getMessageAsMeta('directEye')    
    
    
    mAttachDriver = mRigNull.getMessageAsMeta('attachDriver')
    mAttachDriver.doStore('cgmAlias', '{0}_partDriver'.format(self.d_module['partName']))
    
    #if not self.mConstrainNull.hasAttr('cgmAlias'):
        #self.mConstrainNull.addAttr('cgmAlias','{0}_rootNull'.format(self.d_module['partName']))    
    
    
    #>>  DynParentGroups - Register parents for various controls ============================================
    ml_baseDynParents = []
    ml_endDynParents = self.ml_dynParentsAbove + self.ml_dynEndParents# + [mRoot]
    ml_ikDynParents = []    
    

    #...ik controls ==================================================================================
    if mControlIK:
        log.debug("|{0}| >>  IK Handle ... ".format(_str_func))                
    
        ml_targetDynParents = [self.mEyeLook] + self.ml_dynParentsAbove + self.ml_dynEndParents
        
        ml_targetDynParents.append(self.md_dynTargetsParent['world'])
        ml_targetDynParents.extend(mControlIK.msgList_get('spacePivots',asMeta = True))
    
        mDynGroup = cgmRIGMETA.cgmDynParentGroup(dynChild=mControlIK,dynMode=0)
    
        for mTar in ml_targetDynParents:
            mDynGroup.addDynParent(mTar)
        mDynGroup.rebuild()
            
        log.debug("|{0}| >>  IK targets...".format(_str_func))
        pprint.pprint(ml_targetDynParents)        
        
        log.debug(cgmGEN._str_subLine)



    #Settings =================================================================================
    log.debug("|{0}| >> Settings...".format(_str_func))
    mSettings.visDirect = 0
    
    mPlug_FKIK = cgmMeta.cgmAttr(mSettings,'FKIK')
    mPlug_FKIK.p_defaultValue = 1
    mPlug_FKIK.value = 1
        
    #Lock and hide =================================================================================
    mBlendJoint.dagLock(True)
        
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
        for mCtrl in ml_controlsToLock:
            ATTR.set_standardFlags(mCtrl.mNode, ['scale'])
    else:
        log.debug("|{0}| >>  scale setup...".format(_str_func))
        
        
    self.mDeformNull.dagLock(True)
    

    
    #>>  Attribute defaults =================================================================================
    mRigNull.version = self.d_block['buildVersion']
    mBlock.blockState = 'rig'


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
    mSettings = mRigNull.settings
    mPuppetSettings = self.d_module['mMasterControl'].controlSettings
    
    directProxy = mBlock.proxyDirect
    
    _side = BLOCKUTILS.get_side(self.mBlock)
    ml_neckProxy = []
    
    ml_rigJoints = mRigNull.msgList_get('rigJoints',asMeta = True)
    if not ml_rigJoints:
        raise ValueError,"No rigJoints connected"
    self.v_baseSize = [mBlock.blockScale * v for v in mBlock.baseSize]
    
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
        
    #>> Eye ===================================================================================
    log.debug("|{0}| >> Eye...".format(_str_func))
    
    if directProxy:
        log.debug("|{0}| >> directProxy... ".format(_str_func))
        _settings = self.mRigNull.settings.mNode
        
    mDirect = mRigNull.getMessageAsMeta('directEye')
    
    mProxyEye = cgmMeta.validateObjArg(CORERIG.create_proxyGeo('sphere',
                                                               self.v_baseSize,ch=False)[0],
                                       'cgmObject',setClass=True)
    
    mProxyEye.doSnapTo(mDirect)
    mProxyEye.p_parent = mDirect
    
    ml_proxy = [mProxyEye]

    for mProxy in ml_proxy:
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
        
    mRigNull.msgList_connect('proxyMesh', ml_proxy)




















