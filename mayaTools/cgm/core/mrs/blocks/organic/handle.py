"""
------------------------------------------
cgm.core.mrs.blocks.simple.handle
Author: Josh Burton
email: jjburton@cgmonks.com

Website : http://www.cgmonks.com
------------------------------------------

================================================================
"""
# From Python =============================================================
import copy
import re

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

# From Maya =============================================================
import maya.cmds as mc

# From Red9 =============================================================
from Red9.core import Red9_Meta as r9Meta
r9Meta.cleanCache()#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< TEMP!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


# From cgm ==============================================================
from cgm.core import cgm_Meta as cgmMeta

from cgm.core.lib import curve_Utils as CURVES
from cgm.core.lib import rigging_utils as CORERIG
from cgm.core.lib import snap_utils as SNAP
from cgm.core.lib import attribute_utils as ATTR
import cgm.core.lib.distance_utils as DIST
import cgm.core.lib.shared_data as CORESHARE
import cgm.core.cgmPy.validateArgs as VALID
import cgm.core.rig.joint_utils as JOINTS

import cgm.core.mrs.lib.block_utils as BLOCKUTILS
import cgm.core.mrs.lib.builder_utils as BUILDERUTILS
#=============================================================================================================
#>> Block Settings
#=============================================================================================================
__version__ = 'alpha.11062017'
__autoTemplate__ = True
__component__ = True
__menuVisible__ = True

#>>>Attrs ----------------------------------------------------------------------------------------------------
l_attrsStandard = ['side',
                   'position',
                   'hasRootJoint',
                   'hasJoint',
                   'basicShape',
                   'addAim',
                   'addPivotLeft',
                   'addPivotRight',
                   'addPivotCenter',
                   'addPivotFront',
                   'addPivotBack',
                   'moduleTarget']

d_attrsToMake = {'shapeDirection':":".join(CORESHARE._l_axis_by_string),
                 'axisAim':":".join(CORESHARE._l_axis_by_string),
                 'axisUp':":".join(CORESHARE._l_axis_by_string),                 
                 'targetJoint':'messageSimple',
                 'rootJoint':'messageSimple'}

d_defaultSettings = {'version':__version__,
                     'hasRootJoint':False,
                     'hasJoint':True,
                     'baseSize':10,#cm
                     'basicShape':5,
                     'addAim':True,
                     'addPivotLeft':True,
                     'addPivotRight':True,
                     'addPivotCenter':True,
                     'addPivotFront':True,
                     'addPivotBack':True,
                     'shapeDirection':2,
                     'axisAim':2,
                     'axisUp':4,
                     
                     'attachPoint':'end',
                     'proxyType':1}


#=============================================================================================================
#>> Define
#=============================================================================================================
def define(self):
    _short = self.mNode
    self.translate = 0,0,0
    self.rotate = 0,0,0
    #self.setAttrFlags(attrs=['translate','rotate','sx','sz'])
    #self.doConnectOut('sy',['sx','sz'])
    #ATTR.set_alias(_short,'sy','blockScale')
    
#=============================================================================================================
#>> Template
#=============================================================================================================
def template(self):
    _crv = CURVES.create_controlCurve(self.mNode, shape=self.getEnumValueString('basicShape'),
                                      direction = self.getEnumValueString('shapeDirection'),
                                      sizeMode = 'fixed', size = self.baseSize)
    CORERIG.shapeParent_in_place(self.mNode,_crv,False)
    
    _side = 'center'
    if self.getMayaAttr('side'):
        _side = self.getEnumValueString('side')
        
    CORERIG.colorControl(self.mNode,_side,'main',transparent = False) 
    
    self.msgList_connect('templateHandles',[self.mNode])

    return True

def templateDelete(self):
    return BLOCKUTILS.templateDelete(self)

def is_template(self):
    if self.getShapes():
        return True
    return False

#=============================================================================================================
#>> Prerig
#=============================================================================================================
def prerig(self):
    #self._factory.puppet_verify()
    _str_func = 'prerig'
    _short = self.p_nameShort
    _baseNameAttrs = ATTR.datList_getAttrs(self.mNode,'baseNames')
    _l_baseNames = ATTR.datList_get(self.mNode, 'baseNames')
    
    _side = 'center'
    if self.getMayaAttr('side'):
        _side = self.getEnumValueString('side')

    self._factory.module_verify()  
    ml_templateHandles = self.msgList_get('templateHandles')
    
    #Create preRig Null  ==================================================================================
    mPrerigNull = BLOCKUTILS.prerigNull_verify(self)       
    
    if self.hasJoint:
        _size = DIST.get_bb_size(self.mNode,True,True)
        _sizeSub = _size * .2   
    
        log.info("|{0}| >> [{1}]  Has joint| baseSize: {2} | side: {3}".format(_str_func,_short,_size, _side))     
    
        #Joint Helper ==========================================================================================
        mJointHelper = self.asHandleFactory(self.mNode).addJointHelper(baseSize = _sizeSub, loftHelper = False, lockChannels = ['scale'])
        ATTR.set_standardFlags(mJointHelper.mNode, attrs=['sx', 'sy', 'sz'], 
                               lock=False, visible=True,keyable=False)
    
        self.msgList_connect('jointHelpers',[mJointHelper.mNode])
        self.msgList_connect('prerigHandles',[self.mNode])
        
    #Pivot Helpers ==========================================================================================
    ml_pivots = []
    mPivotRootHandle = False
    self_pos = self.p_position
    self_upVector = self.getAxisVector('y+')
    for a in ['addPivotBack','addPivotFront','addPivotLeft','addPivotRight','addPivotCenter']:
        d_pivotDirections = {'back':'z-',
                             'front':'z+',
                             'left':'x+',
                             'right':'x-'}

        if self.getAttr(a):
            _strPivot = a.split('addPivot')[-1]
            _strPivot = _strPivot[0].lower() + _strPivot[1:]
            log.info("|{0}| >> Adding addPivot helper: {1}".format(_str_func,_strPivot))
            
            if _strPivot == 'center':
                pivot = CURVES.create_controlCurve(self.mNode, shape='circle',
                                                   direction = 'y+',
                                                   sizeMode = 'fixed',
                                                   size = _sizeSub)
                mPivot = cgmMeta.validateObjArg(pivot,'cgmObject',setClass=True)
                mPivot.addAttr('cgmName',_strPivot)
                ml_pivots.append(mPivot)
            else:
                mAxis = VALID.simpleAxis(d_pivotDirections[_strPivot])
                _inverse = mAxis.inverse.p_string
                pivot = CURVES.create_controlCurve(self.mNode, shape='hinge',
                                                   direction = _inverse,
                                                   sizeMode = 'fixed', size = _sizeSub)
                mPivot = cgmMeta.validateObjArg(pivot,'cgmObject',setClass=True)
                mPivot.addAttr('cgmName',_strPivot)
                
                mPivot.p_position = DIST.get_pos_by_axis_dist(_short,mAxis.p_string, _size/2)
                SNAP.aim_atPoint(mPivot.mNode,self_pos, _inverse, 'y+', mode='vector', vectorUp = self_upVector)
            
                ml_pivots.append(mPivot)
        
                if not mPivotRootHandle:
                    pivotHandle = CURVES.create_controlCurve(self.mNode, shape='squareOpen',
                                                             direction = 'y+',
                                                             sizeMode = 'fixed', size = _size * 1.25)
                    mPivotRootHandle = cgmMeta.validateObjArg(pivotHandle,'cgmObject',setClass=True)
                    mPivotRootHandle.addAttr('cgmName','base')
                    mPivotRootHandle.addAttr('cgmType','pivotHelper')            
                    mPivotRootHandle.doName()
                    
                    CORERIG.colorControl(mPivotRootHandle.mNode,_side,'sub',transparent = False) 
                    
                    mPivotRootHandle.parent = mPrerigNull
                    self.connectChildNode(mPivotRootHandle,'pivotHelper','block')#Connect    
                    
    for mPivot in ml_pivots:
        mPivot.addAttr('cgmType','pivotHelper')            
        mPivot.doName()
        
        CORERIG.colorControl(mPivot.mNode,_side,'sub',transparent = False) 
        mPivot.parent = mPivotRootHandle
        mPivotRootHandle.connectChildNode(mPivot,'pivot'+ mPivot.cgmName.capitalize(),'handle')#Connect    



def prerigDelete(self):
    #if self.getMessage('templateLoftMesh'):
    #    mTemplateLoft = self.getMessage('templateLoftMesh',asMeta=True)[0]
    #    for s in mTemplateLoft.getShapes(asMeta=True):
    #        s.overrideDisplayType = 2     
    
    if self.getMessage('noTransformNull'):
        mc.delete(self.getMessage('noTransformNull'))
    return BLOCKUTILS.prerig_delete(self,templateHandles=True)

def is_prerig(self):
    return BLOCKUTILS.is_prerig(self,msgLinks=['moduleTarget','prerigNull'])

"""
def is_prerig(self):
    _str_func = 'is_prerig'
    _l_missing = []
    
    _d_links = {self : ['moduleTarget']}
    
    for plug,l_links in _d_links.iteritems():
        for l in l_links:
            if not plug.getMessage(l):
                _l_missing.append(plug.p_nameBase + '.' + l)
                
    if _l_missing:
        log.info("|{0}| >> Missing...".format(_str_func))  
        for l in _l_missing:
            log.info("|{0}| >> {1}".format(_str_func,l))  
        return False
    return True"""

#=============================================================================================================
#>> rig
#=============================================================================================================
def rig(self):
    #
    self.moduleTarget._verifyMasterControl(size = DIST.get_bb_size(self,True,True))
    
    if self.hasRootJoint:
        if not is_skeletonized(self):
            skeletonize(self)
            
        mJoint = self.getMessage('rootJoint', asMeta = True)[0]
        log.info(mJoint)
        mJoint.p_parent = self.moduleTarget.masterNull.skeletonGroup  

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
                _l_missing.append(plug.p_nameBase + '.' + l)

    if _l_missing:
        log.info("|{0}| >> Missing...".format(_str_func))  
        for l in _l_missing:
            log.info("|{0}| >> {1}".format(_str_func,l))  
        return False
    return True

#=============================================================================================================
#>> Skeleton
#=============================================================================================================
def build_skeleton(self, forceNew = True):
    _short = self.mNode
    _str_func = '[{0}] > build_skeleton'.format(_short)
    log.debug("|{0}| >> ...".format(_str_func)) 
    
    if not self.hasJoint:
        return True
    
    _radius = 1
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
        
    mJoint = self.jointHelper.doCreateAt('joint')
    JOINTS.freezeOrientation(mJoint)
    
    #mJoint.connectParentNode(self,'module','rootJoint')
    
    self.copyAttrTo('cgmName',mJoint.mNode,'cgmName',driven='target')
    #mJoint.doStore('cgmTypeModifier','root')
    mJoint.doName()
    
    mRigNull.msgList_connect('moduleJoints', [mJoint])
    return mJoint.mNode        
    

def skeletonize(self):
    #    
    if is_skeletonized(self):
        return True
    
    if self.hasRootJoint:
        mJoint = self.doCreateAt('joint')
        mJoint.connectParentNode(self,'module','rootJoint')
        self.copyAttrTo('puppetName',mJoint.mNode,'cgmName',driven='target')
        mJoint.doStore('cgmTypeModifier','root')
        mJoint.doName()
        return mJoint.mNode
        #self.msgList_connect('modul')
    return True
        
def is_skeletonized(self):
    if self.hasRootJoint:
        if not self.getMessage('rootJoint'):
            return False
    return True

def skeletonDelete(self):
    if is_skeletonized(self):
        log.warning("MUST ACCOUNT FOR CHILD JOINTS")
        mc.delete(self.getMessage('rootJoint'))
    return True
            

#=============================================================================================================
#>> rig
#=============================================================================================================
#NOTE - self here is a rig Factory....

d_preferredAngles = {'head':[0,-10, 10]}#In terms of aim up out for orientation relative values, stored left, if right, it will invert
d_rotateOrders = {'head':'yxz'}

#Rig build stuff goes through the rig build factory ------------------------------------------------------
def rig_skeleton(self):
    _short = self.d_block['shortName']
    
    _str_func = '[{0}] > rig_skeleton'.format(_short)
    log.info("|{0}| >> ...".format(_str_func))  
    _start = time.clock()
        
    mBlock = self.mBlock
    mRigNull = self.mRigNull
    ml_jointsToConnect = []
    ml_jointsToHide = []
    ml_joints = mRigNull.msgList_get('moduleJoints')
    self.d_joints['ml_moduleJoints'] = ml_joints
    
    BLOCKUTILS.skeleton_pushSettings(ml_joints, self.d_orientation['str'], self.d_module['mirrorDirection'],
                                     d_rotateOrders, d_preferredAngles)
    
    log.info("|{0}| >> Head...".format(_str_func))  
    
    ml_rigJoints = BLOCKUTILS.skeleton_buildDuplicateChain(ml_joints, 'rig', self.mRigNull,'rigJoints')
    
    if self.mBlock.headAim:
        log.info("|{0}| >> Head IK...".format(_str_func))              
        ml_fkHeadJoints = BLOCKUTILS.skeleton_buildDuplicateChain(ml_joints[-1], 'fk', self.mRigNull, 'fkHeadJoint', singleMode = True )
        ml_blendHeadJoints = BLOCKUTILS.skeleton_buildDuplicateChain(ml_joints[-1], 'blend', self.mRigNull, 'blendHeadJoint', singleMode = True)
        ml_aimHeadJoints = BLOCKUTILS.skeleton_buildDuplicateChain(ml_joints[-1], 'aim', self.mRigNull, 'aimHeadJoint', singleMode = True)
        ml_jointsToConnect.extend(ml_fkHeadJoints + ml_aimHeadJoints)
        ml_jointsToHide.extend(ml_blendHeadJoints)
    
    #...Neck ---------------------------------------------------------------------------------------
    if self.mBlock.neckBuild:
        log.info("|{0}| >> Neck Build".format(_str_func))          
        ml_fkJoints = BLOCKUTILS.skeleton_buildHandleChain(self.mBlock,'fk','fkJoints')
        l_baseNameAttrs = ATTR.datList_getAttrs(mBlock.mNode,'baseNames')
        
        #We then need to name our core joints to pass forward:
        mBlock.copyAttrTo(l_baseNameAttrs[0],ml_fkJoints[-1].mNode,'cgmName',driven='target')
        mBlock.copyAttrTo(l_baseNameAttrs[1],ml_fkJoints[0].mNode,'cgmName',driven='target')
        
        if len(ml_fkJoints) > 2:
            for i,mJnt in enumerate(ml_fkJoints[1:-1]):
                mJnt.doStore('cgmIterator',i+1)
            ml_fkJoints[0].doStore('cgmNameModifier','base')
        
        for mJnt in ml_fkJoints:
            mJnt.doName()
            
        ml_jointsToHide.extend(ml_fkJoints)

        if self.mBlock.neckIK:
            log.info("|{0}| >> buildIK on. Building blend and IK chains...".format(_str_func))  
            ml_blendJoints = BLOCKUTILS.skeleton_buildHandleChain(self.mBlock,'blend','blendJoints')
            ml_ikJoints = BLOCKUTILS.skeleton_buildHandleChain(self.mBlock,'ik','ikJoints')
            ml_jointsToConnect.extend(ml_ikJoints)
            ml_jointsToHide.extend(ml_blendJoints)
            
        
        if mBlock.neckControls > 1:
            log.info("|{0}| >> Handles...".format(_str_func))            
            ml_segmentHandles = BLOCKUTILS.skeleton_buildHandleChain(self.mBlock,'handle','handleJoints',clearType=True)
            for i,mJnt in enumerate(ml_segmentHandles):
                mJnt.parent = ml_blendJoints[i]
                
        if mBlock.neckControls > 2:
            log.info("|{0}| >> IK Drivers...".format(_str_func))            
            ml_baseIKDrivers = BLOCKUTILS.skeleton_buildDuplicateChain(ml_segmentHandles, None, mRigNull,'baseIKDrivers', cgmType = 'baseIKDriver', indices=[0,-1])
            for mJnt in ml_baseIKDrivers:
                mJnt.parent = False
            ml_jointsToConnect.extend(ml_baseIKDrivers)
            
        if mBlock.neckJoints > mBlock.neckControls:
            log.info("|{0}| >> segment necessary...".format(_str_func))
                
            ml_segmentChain = BLOCKUTILS.skeleton_buildDuplicateChain(ml_joints, None, mRigNull,'segmentJoints', cgmType = 'segJnt')
            for i,mJnt in enumerate(ml_rigJoints[:-1]):
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
    log.info("|{0}| >> Time >> = {1} seconds".format(_str_func, "%0.3f"%(time.clock()-_start)))
    self.fnc_connect_toRigGutsVis( ml_jointsToConnect )        
    
    return

def rig_shapes(self):
    _short = self.d_block['shortName']
    _str_func = '[{0}] > rig_shapes'.format(_short)
    log.info("|{0}| >> ...".format(_str_func))  
    _start = time.clock()
    
    ml_prerigHandles = self.mBlock.atBlockUtils('prerig_getHandleTargets')
    ml_fkJoints = self.mRigNull.msgList_get('fkJoints')    
    mHeadHelper = ml_prerigHandles[-1]
    mBlock = self.mBlock
    #l_toBuild = ['segmentFK_Loli','segmentIK']
    #mShapeCast.go(self._mi_module,l_toBuild, storageInstance=self)#This will store controls to a dict called    
    
    #Get our base size from the block
    _size = DIST.get_bb_size(_short,True,True)
    _side = BLOCKUTILS.get_side(self.mBlock)
    _ikPos = mHeadHelper.getPositionByAxisDistance('z+', _size *2)
    _short_module = self.mModule.mNode
    ml_joints = self.d_joints['ml_moduleJoints']
    
    #Logic ====================================================================================
    b_FKIKhead = False
    if mBlock.neckControls > 1 and mBlock.neckBuild: 
        log.info("|{0}| >> FK/IK head necessary...".format(_str_func))          
        b_FKIKhead = True    
    
    #Head=============================================================================================
    if mBlock.headAim:
        log.info("|{0}| >> Head aim...".format(_str_func))  
        ikCurve = CURVES.create_fromName('sphere2',_size/2)
        textCrv = CURVES.create_text('head',_size/2)
        CORERIG.shapeParent_in_place(ikCurve,textCrv,False)
        
        mLookAt = cgmMeta.validateObjArg(ikCurve,'cgmObject',setClass=True)
        mLookAt.p_position = _ikPos
        
        ATTR.copy_to(_short_module,'cgmName',mLookAt.mNode,driven='target')
        #mIK.doStore('cgmName','head')
        mLookAt.doStore('cgmTypeModifier','lookAt')
        mLookAt.doName()
        
        CORERIG.colorControl(mLookAt.mNode,_side,'main')
        
        self.mRigNull.connectChildNode(mLookAt,'headLookAt','rigNull')#Connect
    
    #IK ----------------------------------------------------------------------------------
    mIK = mHeadHelper.doCreateAt()
    #CORERIG.shapeParent_in_place(mIK,l_lolis,False)
    CORERIG.shapeParent_in_place(mIK,self.mBlock.mNode,True)
    mIK = cgmMeta.validateObjArg(mIK,'cgmObject',setClass=True)
    ATTR.copy_to(_short_module,'cgmName',mIK.mNode,driven='target')
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
    
    #Direct Controls =============================================================================
    ml_rigJoints = self.mRigNull.msgList_get('rigJoints')
    
    if len(ml_rigJoints) < 3:
        d_direct = {'size':_size/3}
    else:
        d_direct = {'size':None}
        
    ml_directShapes = self.atBuilderUtils('shapes_fromCast',
                                          ml_rigJoints,
                                          mode ='direct',**d_direct)
                                                                                                                                                            #offset = 3

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
        self.mRigNull.connectChildNode(mFK,'settings','rigNull')#Connect    
        
    
    #Neck=============================================================================================    
    if self.mBlock.neckBuild:
        log.debug("|{0}| >> Neck...".format(_str_func))
        
        #Handle Joints ----------------------------------------------------------------------------------
        ml_handleJoints = self.mRigNull.msgList_get('handleJoints')
        if ml_handleJoints:
            log.debug("|{0}| >> Found Handle Joints...".format(_str_func))
            l_uValues = MATH.get_splitValueList(.1,.9, len(ml_handleJoints))
            ml_handleShapes = self.atBuilderUtils('shapes_fromCast',
                                                  mode ='segmentHandle',
                                                  uValues = l_uValues,)
                                                  #offset = 3
            for i,mCrv in enumerate(ml_handleShapes):
                CORERIG.colorControl(mCrv.mNode,_side,'sub')
                CORERIG.shapeParent_in_place(ml_handleJoints[i].mNode,mCrv.mNode, False, replaceShapes=True)
                for mShape in ml_handleJoints[i].getShapes(asMeta=True):
                    mShape.doName()
        
        #Root -------------------------------------------------------------------------------------------
        #Grab template handle root - use for sizing, make ball
        mNeckBaseHandle = self.mBlock.msgList_get('templateHandles')[0]
        size_neck = DIST.get_bb_size(mNeckBaseHandle.mNode,True,True) /2
        
        mRoot = ml_joints[0].doCreateAt()
        mRootCrv = cgmMeta.validateObjArg(CURVES.create_fromName('sphere', size_neck),'cgmObject',setClass=True)
        mRootCrv.doSnapTo(mNeckBaseHandle)
        
        #SNAP.go(mRootCrv.mNode, ml_joints[0].mNode,position=False)
        
        CORERIG.shapeParent_in_place(mRoot.mNode,mRootCrv.mNode, False)
        
        ATTR.copy_to(_short_module,'cgmName',mRoot.mNode,driven='target')
        mRoot.doStore('cgmTypeModifier','root')
        mRoot.doName()
        
        CORERIG.colorControl(mRoot.mNode,_side,'sub')
        self.mRigNull.connectChildNode(mRoot,'rigRoot','rigNull')#Connect
        
        #FK ---------------------------------------------------------------------------------------------
        ml_fkShapes = self.atBuilderUtils('shapes_fromCast',  ml_prerigHandles[:-1])
        for i,mCrv in enumerate(ml_fkShapes):
            CORERIG.colorControl(mCrv.mNode,_side,'main')
            CORERIG.shapeParent_in_place(ml_fkJoints[i].mNode,mCrv.mNode, False, replaceShapes=True)
            for mShape in ml_fkJoints[i].getShapes(asMeta=True):
                mShape.doName()

    log.info("|{0}| >> Time >> = {1} seconds".format(_str_func, "%0.3f"%(time.clock()-_start)))
    
def rig_controls(self):
    _short = self.d_block['shortName']
    _str_func = '[{0}] > rig_controls'.format(_short)
    log.info("|{0}| >> ...".format(_str_func))  
    _start = time.clock()
  
    mRigNull = self.mRigNull
    ml_controlsAll = []#we'll append to this list and connect them all at the end
    mRootParent = self.mDeformNull
    mSettings = mRigNull.settings
    
    mHeadFK = False
    if mRigNull.getMessage('headFK'):
        mHeadFK = mRigNull.headFK    
        
    mHeadIK = mRigNull.headIK
    
    # Drivers ==============================================================================================    
    if self.mBlock.neckBuild:
        if self.mBlock.neckIK:
            mPlug_FKIK = cgmMeta.cgmAttr(mSettings.mNode,'FKIK',attrType='float',minValue=0,maxValue=1,lock=False,keyable=True)
    
        #>> vis Drivers ================================================================================================	
        mPlug_visSub = self.atBuilderUtils('build_visSub')
        mPlug_visRoot = cgmMeta.cgmAttr(mSettings,'visRoot', value = True, attrType='bool', defaultValue = False,keyable = False,hidden = False)
    mPlug_visDirect = cgmMeta.cgmAttr(mSettings,'visDirect', value = True, attrType='bool', defaultValue = False,keyable = False,hidden = False)
    
    if self.mBlock.headAim:        
        mPlug_aim = cgmMeta.cgmAttr(mSettings.mNode,'blend_aim',attrType='float',minValue=0,maxValue=1,lock=False,keyable=True)
        
        
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
    
            mObj = d_buffer['instance']
            #mObj.axisAim = "%s+"%self._go._jointOrientation[0]
            #mObj.axisUp= "%s+"%self._go._jointOrientation[1]	
            #mObj.axisOut= "%s+"%self._go._jointOrientation[2]
            #try:i_obj.drawStyle = 2#Stick joint draw style	    
            #except:self.log_error("{0} Failed to set drawStyle".format(i_obj.p_nameShort))
            ATTR.set_hidden(mObj.mNode,'radius',True)
            
    
    #ikHead ========================================================================================
    log.info("|{0}| >> Found headIK : {1}".format(_str_func, mHeadIK))    
    _d = MODULECONTROL.register(mHeadIK,
                                addSpacePivots = 2,
                                addDynParentGroup = True, addConstraintGroup=False,
                                mirrorSide= self.d_module['mirrorDirection'],
                                mirrorAxis="translateX,rotateY,rotateZ",
                                makeAimable = True)
    
    mHeadIK = _d['mObj']
    mHeadIK.masterGroup.parent = mRootParent
    ml_controlsAll.append(mHeadIK)            
    
    
    #>> headLookAt ========================================================================================
    if mRigNull.getMessage('headLookAt'):
        mHeadLookAt = mRigNull.headLookAt
        log.info("|{0}| >> Found headLookAt : {1}".format(_str_func, mHeadLookAt))
        MODULECONTROL.register(mHeadLookAt,
                               typeModifier='lookAt',addSpacePivots = 2,
                               addDynParentGroup = True, addConstraintGroup=False,
                               mirrorSide= self.d_module['mirrorDirection'],
                               mirrorAxis="translateX,rotateY,rotateZ",
                               makeAimable = False)
        mHeadLookAt.masterGroup.parent = mRootParent
        ml_controlsAll.append(mHeadLookAt)
        
    
    #>> settings ========================================================================================
    if mHeadFK:
        mSettings = mRigNull.settings
        log.info("|{0}| >> Found settings : {1}".format(_str_func, mSettings))
        
        MODULECONTROL.register(mSettings)
        
        ml_blendJoints = self.mRigNull.msgList_get('blendJoints')
        mSettings.masterGroup.parent = ml_blendJoints[-1]
    
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
    
    log.info("|{0}| >> Time >> = {1} seconds".format(_str_func, "%0.3f"%(time.clock()-_start)))                
    
    
    
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



def rig_segments(self):
    _short = self.d_block['shortName']
    _str_func = '[{0}] > rig_neckSegment'.format(_short)
    
    if not self.mBlock.neckBuild:
        log.info("|{0}| >> No neck build optioned".format(_str_func))                      
        return True
    
    log.info("|{0}| >> ...".format(_str_func))  
    _start = time.clock()
    
    mBlock = self.mBlock
    mRigNull = self.mRigNull
    mRootParent = self.mDeformNull
    mHeadFK = mRigNull.headFK
    log.info("|{0}| >> Found headFK : {1}".format(_str_func, mHeadFK))
    
    ml_segmentJoints = mRigNull.msgList_get('segmentJoints')
    ml_blendJoints = mRigNull.msgList_get('blendJoints')
    #ml_rigJoints[0].parent = ml_blendJoints[0]
    #ml_rigJoints[-1].parent = mHeadFK
    ml_handleJoints = mRigNull.msgList_get('handleJoints')
    #>> Neck build ======================================================================================
    if mBlock.neckJoints > 1:
        
        if mBlock.neckControls == 1:
            
            log.debug("|{0}| >> Simple neck segment...".format(_str_func))
            RIGCONSTRAINT.setup_linearSegment(ml_segmentJoints)
            ml_segmentJoints[0].parent = ml_handleJoints[0]
            ml_segmentJoints[-1].parent = ml_handleJoints[-1]
        else:
            log.debug("|{0}| >> Neck segment...".format(_str_func))    
            


    log.info("|{0}| >> Time >> = {1} seconds".format(_str_func, "%0.3f"%(time.clock()-_start)))                
    
def rig_frame(self):
    _short = self.d_block['shortName']
    _str_func = '[{0}] > rig_rigFrame'.format(_short)
    log.info("|{0}| >> ...".format(_str_func))  
    _start = time.clock()
    
    mRigNull = self.mRigNull
    mRootParent = self.mDeformNull
    mHeadIK = mRigNull.headIK
    log.info("|{0}| >> Found headIK : {1}".format(_str_func, mHeadIK))
    
    ml_rigJoints = mRigNull.msgList_get('rigJoints')
    ml_fkJoints = mRigNull.msgList_get('fkJoints')
    ml_handleJoints = self.mRigNull.msgList_get('handleJoints')
    ml_baseIKDrivers = self.mRigNull.msgList_get('baseIKDrivers')
    ml_blendJoints = mRigNull.msgList_get('blendJoints')
    
    mTopHandleDriver = mHeadIK
    
    mHeadFK = False
    
    if mRigNull.getMessage('headFK'):
        mHeadFK = mRigNull.headFK
        mAimParent = ml_blendJoints[-1]
    else:
        pass
        
    
    #>> headFK ========================================================================================
    if not mRigNull.getMessage('headFK'):
        raise ValueError,"No headFK found"
    
    if self.mBlock.headAim:
        log.info("|{0}| >> HeadAim setup...".format(_str_func))
        mSettings = mRigNull.settings
        
        mPlug_aim = cgmMeta.cgmAttr(mSettings.mNode,'blend_aim',attrType='float',lock=False,keyable=True)
        
        mHeadFKJoint = mRigNull.getMessage('fkHeadJoint', asMeta=True)[0]
        mHeadAimJoint = mRigNull.getMessage('aimHeadJoint', asMeta=True)[0]
        mHeadBlendJoint = mRigNull.getMessage('blendHeadJoint', asMeta=True)[0]
        mTopHandleDriver = mHeadBlendJoint
        mHeadLookAt = mRigNull.headLookAt
        
        ATTR.connect(mPlug_aim.p_combinedShortName, "{0}.v".format(mHeadLookAt.mNode))
        
        #Setup Aim -------------------------------------------------------------------------------------
        mc.aimConstraint(mHeadLookAt.mNode,
                         mHeadAimJoint.mNode,
                         maintainOffset = False, weight = 1,
                         aimVector = self.d_orientation['vectorAim'],
                         upVector = self.d_orientation['vectorUp'],
                         worldUpVector = self.d_orientation['vectorUp'],
                         worldUpObject = mHeadIK.masterGroup.mNode,
                         worldUpType = 'objectRotation' )

        #Setup blend ----------------------------------------------------------------------------------
        RIGCONSTRAINT.blendChainsBy(mHeadFKJoint,mHeadAimJoint,mHeadBlendJoint,
                                    driver = mPlug_aim.p_combinedName,l_constraints=['orient'])
        
        #Parent pass ---------------------------------------------------------------------------------
        mHeadLookAt.masterGroup.parent = mHeadIK.masterGroup
        #mSettings.masterGroup.parent = mHeadIK
        
        for mObj in mHeadFKJoint,mHeadAimJoint,mHeadBlendJoint:
            mObj.parent = mHeadIK
        
        mHeadIK.parent = mHeadBlendJoint.mNode
        """
        mHeadFK_aimFollowGroup = mHeadFK.doGroup(True,True,True,'aimFollow')
        mc.orientConstraint(mHeadBlendJoint.mNode,
                            mHeadFK_aimFollowGroup.mNode,
                            maintainOffset = False)"""
        
        
    else:
        log.info("|{0}| >> NO Head IK setup...".format(_str_func))    
    
    #Parent the direct control to the 
    if ml_rigJoints[-1].getMessage('masterGroup'):
        ml_rigJoints[-1].masterGroup.parent = mTopHandleDriver
    else:
        ml_rigJoints[-1].parent = mTopHandleDriver
        
    return
    #>> Neck build ======================================================================================
    if self.mBlock.neckBuild:
        log.debug("|{0}| >> Neck...".format(_str_func))
        
        if not mRigNull.getMessage('rigRoot'):
            raise ValueError,"No rigRoot found"
        
        mRoot = mRigNull.rigRoot
        mSettings = mRigNull.settings
        
        if self.mBlock.neckIK:
            
            log.debug("|{0}| >> Neck IK...".format(_str_func))
            ml_ikJoints = mRigNull.msgList_get('ikJoints')
            ml_blendJoints = mRigNull.msgList_get('blendJoints')
            
            mPlug_FKIK = cgmMeta.cgmAttr(mHeadFK.mNode,'FKIK',attrType='float',lock=False,keyable=True)
            
            
            #>>> Setup a vis blend result
            mPlug_FKon = cgmMeta.cgmAttr(mSettings,'result_FKon',attrType='float',defaultValue = 0,keyable = False,lock=True,hidden=True)	
            mPlug_IKon = cgmMeta.cgmAttr(mSettings,'result_IKon',attrType='float',defaultValue = 0,keyable = False,lock=True,hidden=True)	
        
            NODEFACTORY.createSingleBlendNetwork(mPlug_FKIK.p_combinedName,
                                                 mPlug_IKon.p_combinedName,
                                                 mPlug_FKon.p_combinedName)
              
            mPlug_FKon.doConnectOut("{0}.visibility".format(ml_fkJoints[0].masterGroup.mNode))
            #mPlug_IKon.doConnectOut("%s.visibility"%ikGroup)            
            
            
            # Create head position driver ------------------------------------------------
            mHeadDriver = mHeadFK.doCreateAt()
            mHeadDriver.rename('headBlendDriver')
            mHeadDriver.parent = mRoot
            
            mHeadIKDriver = mHeadFK.doCreateAt()
            mHeadIKDriver.rename('headIKDriver')
            mHeadIKDriver.parent = mRoot
            
            mHeadFKDriver = mHeadFK.doCreateAt()
            mHeadFKDriver.rename('headFKDriver')
            mHeadFKDriver.parent = ml_fkJoints[-1]
            
            mHeadFK.connectChildNode(mHeadDriver.mNode, 'blendDriver')
            
            RIGCONSTRAINT.blendChainsBy(mHeadFKDriver.mNode,
                                        mHeadIKDriver.mNode,
                                        mHeadDriver.mNode,
                                        driver = mPlug_FKIK.p_combinedName,l_constraints=['point','orient'])            
            
            
            # Neck controls --------------------------------------------------------------
            if self.mBlock.neckControls == 1:
                log.debug("|{0}| >> Single joint IK...".format(_str_func))
                mc.aimConstraint(mHeadFK.mNode,
                                 ml_ikJoints[0].mNode,
                                 maintainOffset = True, weight = 1,
                                 aimVector = self.d_orientation['vectorAim'],
                                 upVector = self.d_orientation['vectorUp'],
                                 worldUpVector = self.d_orientation['vectorOut'],
                                 worldUpObject = mRoot.mNode,
                                 worldUpType = 'objectRotation' )
                mc.pointConstraint(mHeadFK.mNode,
                                   ml_ikJoints[-1].mNode,
                                   maintainOffset = True)
                
                
            #>> handleJoints ========================================================================================
            if ml_handleJoints:
                log.debug("|{0}| >> Found Handles...".format(_str_func))
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
                
            #>> baseIK Drivers ========================================================================================
            if ml_baseIKDrivers:
                log.debug("|{0}| >> Found baseIK drivers...".format(_str_func))
                
                ml_baseIKDrivers[-1].parent = mHeadFK
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
                
                
            if self.mBlock.neckJoints == 1:
                log.debug("|{0}| >> Single neckJoint setup...".format(_str_func))                
                ml_rigJoints[0].masterGroup.parent = ml_blendJoints[0]
                
                mc.aimConstraint(mHeadFK.mNode,
                                 ml_rigJoints[0].masterGroup.mNode,
                                 maintainOffset = True, weight = 1,
                                 aimVector = self.d_orientation['vectorAim'],
                                 upVector = self.d_orientation['vectorUp'],
                                 worldUpVector = self.d_orientation['vectorOut'],
                                 worldUpObject = ml_blendJoints[0].mNode,
                                 worldUpType = 'objectRotation' )                    
                
            else:
                log.debug("|{0}| >> Not implemented multi yet".format(_str_func))
                
                #raise ValueError,"Not implemented"
            
            #Parent --------------------------------------------------            
            ml_blendJoints[0].parent = mRoot
            ml_ikJoints[0].parent = mRoot

            #Setup blend ----------------------------------------------------------------------------------
            RIGCONSTRAINT.blendChainsBy(ml_fkJoints,ml_ikJoints,ml_blendJoints,
                                        driver = mPlug_FKIK.p_combinedName,l_constraints=['point','orient'])            
            
    
    
        
    ##ml_rigJoints = mRigNull.msgList_get('rigJoints')
    ##ml_rigJoints[-1].parent = mHeadFK
    ##ml_rigJoints[0].parent = ml_blendJoints[0]
    
    log.info("|{0}| >> Time >> = {1} seconds".format(_str_func, "%0.3f"%(time.clock()-_start)))
    
def rig_cleanUp(self):
    _short = self.d_block['shortName']
    _str_func = '[{0}] > rig_cleanUp'.format(_short)
    log.info("|{0}| >> ...".format(_str_func))  
    _start = time.clock()
    
    mRigNull = self.mRigNull
    mHeadFK = mRigNull.headFK
    mSettings = mRigNull.settings
    
    
    mMasterControl= self.d_module['mMasterControl']
    mMasterDeformGroup= self.d_module['mMasterDeformGroup']    
    mMasterNull = self.d_module['mMasterNull']
    mModuleParent = self.d_module['mModuleParent']
    mPlug_globalScale = self.d_module['mPlug_globalScale']
    
    #>>  Parent and constraining joints and rig parts =======================================================
    mSettings.masterGroup.parent = mHeadFK
    
    #>>  DynParentGroups - Register parents for various controls ============================================

    #...head -----------------------------------------------------------------------------------
    ml_headDynParents = []
    ml_baseHeadDynParents = []
    
    #ml_headDynParents = [ml_controlsFK[0]]
    if mModuleParent:
        mi_parentRigNull = mModuleParent.rigNull
        if mi_parentRigNull.getMessage('handleIK'):
            ml_baseHeadDynParents.append( mi_parentRigNull.handleIK )	    
        if mi_parentRigNull.getMessage('cog'):
            ml_baseHeadDynParents.append( mi_parentRigNull.cog )
    ml_baseHeadDynParents.append(mMasterNull.puppetSpaceObjectsGroup)
    
  
    
    ml_headDynParents = copy.copy(ml_baseHeadDynParents)
    ml_headDynParents.extend(mHeadFK.msgList_get('spacePivots',asMeta = True))
    ml_headDynParents.append(mMasterNull.worldSpaceObjectsGroup)
    
    mBlendDriver =  mHeadFK.getMessage('blendDriver',asMeta=True)
    if mBlendDriver:
        mBlendDriver = mBlendDriver[0]
        ml_headDynParents.insert(0, mBlendDriver)  
        mBlendDriver.addAttr('cgmAlias','neckDriver')
    #pprint.pprint(ml_headDynParents)

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
    
    log.info("|{0}| >> Time >> = {1} seconds".format(_str_func, "%0.3f"%(time.clock()-_start)))
    

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
    mHeadFK = mRigNull.headFK
    mSettings = mRigNull.settings
    mPuppetSettings = self.d_module['mMasterControl'].controlSettings
    
    _side = BLOCKUTILS.get_side(self.mBlock)
    ml_neckProxy = []
    
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
        
    #>> Head ===================================================================================
    log.debug("|{0}| >> Head...".format(_str_func))
    
    mGroup = mBlock.msgList_get('headMeshProxy')[mBlock.headGeo + 1].getParent(asMeta=True)
    l_headGeo = mGroup.getChildren(asMeta=False)
    l_vis = mc.ls(l_headGeo, visible = True)
    ml_headStuff = []
    for i,o in enumerate(l_vis):
        mObj = cgmMeta.validateObjArg(mc.duplicate(o, po=False, ic = False)[0])
        ml_headStuff.append(  mObj )
        mObj.parent = ml_rigJoints[-1]
        
        ATTR.copy_to(ml_rigJoints[-1].mNode,'cgmName',mObj.mNode,driven = 'target')
        mObj.addAttr('cgmIterator',i)
        mObj.addAttr('cgmType','proxyGeo')
        mObj.doName()
        
        
    if mBlock.neckBuild:#...Neck =====================================================================
        log.debug("|{0}| >> neckBuild...".format(_str_func))
        
        # Create ---------------------------------------------------------------------------
        ml_neckProxy = cgmMeta.validateObjListArg(self.atBuilderUtils('mesh_proxyCreate', ml_rigJoints),'cgmObject')
        
        for i,mGeo in enumerate(ml_neckProxy):
            mGeo.parent = ml_rigJoints[i]
            ATTR.copy_to(ml_rigJoints[0].mNode,'cgmName',mGeo.mNode,driven = 'target')
            mGeo.addAttr('cgmIterator',i+1)
            mGeo.addAttr('cgmType','proxyGeo')
            mGeo.doName()            
    
    for mProxy in ml_neckProxy + ml_headStuff:
        CORERIG.colorControl(mProxy.mNode,_side,'main',transparent=False)
        
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
        
    mRigNull.msgList_connect('proxyMesh', ml_neckProxy + ml_headStuff)

__l_rigBuildOrder__ = ['rig_skeleton',
                       'rig_shapes',
                       'rig_controls',
                       'rig_segments',
                       'rig_frame',
                       'rig_cleanUp ']





 








