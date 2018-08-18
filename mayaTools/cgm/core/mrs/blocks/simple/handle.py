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
import time
import pprint

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
import cgm.core.cgm_General as cgmGEN

from cgm.core.lib import curve_Utils as CURVES
from cgm.core.lib import rigging_utils as CORERIG
import cgm.core.classes.NodeFactory as NODEFACTORY
from cgm.core.lib import snap_utils as SNAP
from cgm.core.lib import attribute_utils as ATTR
import cgm.core.lib.distance_utils as DIST
import cgm.core.lib.shared_data as CORESHARE
import cgm.core.rig.constraint_utils as RIGCONSTRAINT
import cgm.core.lib.transform_utils as TRANS
import cgm.core.cgmPy.validateArgs as VALID
import cgm.core.rig.joint_utils as JOINTS
import cgm.core.lib.list_utils as LISTS
import cgm.core.mrs.lib.ModuleControlFactory as MODULECONTROL
reload(MODULECONTROL)
import cgm.core.mrs.lib.block_utils as BLOCKUTILS
import cgm.core.mrs.lib.builder_utils as BUILDERUTILS
#=============================================================================================================
#>> Block Settings
#=============================================================================================================
__version__ = 'alpha.12192017'
__autoTemplate__ = True
__component__ = True
__menuVisible__ = True
__baseSize__ = 10,10,10
__l_rigBuildOrder__ = ['rig_skeleton',
                       'rig_shapes',
                       'rig_controls',
                       'rig_frame',
                       'rig_cleanUp']

#>>>Profiles =====================================================================================================
d_build_profiles = {'unityLow':{},
                    'unityMed':{},
                    'feature':{}}

#>>>Attrs ========================================================================================================
l_attrsStandard = ['side',
                   'position',
                   'hasJoint',
                   'basicShape',
                   'attachPoint',
                   'addAim',
                   'proxyShape',
                   'addPivot',
                   'addCog',
                   'addScalePivot',
                   'proxy',
                   #'buildProfile',
                   'moduleTarget']

d_attrsToMake = {'shapeDirection':":".join(CORESHARE._l_axis_by_string),
                 'axisAim':":".join(CORESHARE._l_axis_by_string),
                 'axisUp':":".join(CORESHARE._l_axis_by_string),                 
                 'targetJoint':'messageSimple',
                 'rootJoint':'messageSimple'}

d_defaultSettings = {'version':__version__,
                     'hasJoint':True,
                     'basicShape':5,
                     'addAim':True,
                     'shapeDirection':2,
                     'axisAim':2,
                     'axisUp':4,
                     'attachPoint':'end',
                     'proxy':1,
                     'proxyType':1}

d_wiring_prerig = {'msgLinks':['moduleTarget','prerigNull'],
                   'msgLists':['prerigHandles']}
d_wiring_template = {'msgLinks':['templateNull'],
                     }

#=============================================================================================================
#>> Define
#=============================================================================================================
def define(self):
    _short = self.mNode
    #self.translate = 0,0,0
    #self.rotate = 0,0,0
    

    #self.setAttrFlags(attrs=['translate','rotate','sx','sz'])
    #self.doConnectOut('sy',['sx','sz'])
    #ATTR.set_alias(_short,'sy','blockScale')
    
#=============================================================================================================
#>> Template
#=============================================================================================================
def template(self):
    try:
        _short = self.mNode
        _shape = self.getEnumValueString('basicShape')
        _size = self.baseSize
        mHandleFactory = self.asHandleFactory(self)
        _shapeDirection = self.getEnumValueString('shapeDirection')
        #Create temple Null  ==================================================================================
        mTemplateNull = BLOCKUTILS.templateNull_verify(self)        
        
        #Base shape ===========================================================================================
        if _shape in ['circle','square']:
            _size = [v for v in self.baseSize[:-1]] + [None]
            
        _crv = CURVES.create_controlCurve(self.mNode, shape=_shape,
                                          direction = _shapeDirection,
                                          sizeMode = 'fixed', size = _size)
        
        mHandle = cgmMeta.validateObjArg(_crv,'cgmObject',setClass=True)
        mHandle.p_parent = mTemplateNull
        
        mHandle.doStore('cgmNameModifier','main')
        mHandle.doStore('cgmType','handle')
        mHandleFactory.copyBlockNameTags(mHandle)
        
        _side = 'center'
        if self.getMayaAttr('side'):
            _side = self.getEnumValueString('side')
            
        CORERIG.colorControl(mHandle.mNode,_side,'main',transparent = False) 
        
        #Proxy geo ==================================================================================
        attr = 'proxy'
        #self.addAttr(attr,enumName = 'off:lock:on', defaultValue = 1, attrType = 'enum',keyable = False,hidden = False)
        NODEFACTORY.argsToNodes("%s.%sVis = if %s.%s > 0"%(_short,attr,_short,attr)).doBuild()
        NODEFACTORY.argsToNodes("%s.%sLock = if %s.%s == 2:0 else 2"%(_short,attr,_short,attr)).doBuild()
        
        mProxy = mHandleFactory.addProxyHelper(shapeDirection = _shapeDirection)
        mProxy.p_parent = mHandle
        
        mProxy.overrideEnabled = 1
        ATTR.connect("{0}.proxyVis".format(_short),"{0}.visibility".format(mProxy.mNode) )
        ATTR.connect("{0}.proxyLock".format(_short),"{0}.overrideDisplayType".format(mProxy.mNode) )        
        for mShape in mProxy.getShapes(asMeta=1):
            str_shape = mShape.mNode
            mShape.overrideEnabled = 0
            ATTR.connect("{0}.proxyLock".format(_short),"{0}.overrideDisplayTypes".format(str_shape) )
            ATTR.connect("{0}.proxyLock".format(_short),"{0}.overrideDisplayType".format(str_shape) )        
            
        self.msgList_connect('templateHandles',[mHandle.mNode])
    except Exception,err:
        cgmGEN.cgmException(Exception,err,msg=vars())
        
#def is_template(self):
#    if self.getMessage('templateNull'):
#        return True
#    return False

#=============================================================================================================
#>> Prerig
#=============================================================================================================
def prerig(self):
    #self._factory.puppet_verify()
    try:
        _str_func = 'prerig'
        _short = self.p_nameShort
        _baseNameAttrs = ATTR.datList_getAttrs(self.mNode,'baseNames')
        _l_baseNames = ATTR.datList_get(self.mNode, 'baseNames')
        
        _side = self.atUtils('get_side')
            
        self.atUtils('module_verify')
    
        ml_templateHandles = self.msgList_get('templateHandles')
        mMain = ml_templateHandles[0]
        mHandleFactory = self.asHandleFactory(mMain.mNode)
        
        #Create preRig Null  ==================================================================================
        mPrerigNull = BLOCKUTILS.prerigNull_verify(self)       
        
        if self.hasJoint:
            _size = DIST.get_bb_size(self.mNode,True,True)
            _sizeSub = _size * .2   
        
            log.info("|{0}| >> [{1}]  Has joint| baseSize: {2} | side: {3}".format(_str_func,_short,_size, _side))     
        
            #Joint Helper ==========================================================================================
            mJointHelper = self.asHandleFactory(mMain.mNode).addJointHelper(baseSize = _sizeSub, loftHelper = False, lockChannels = ['scale'])
            ATTR.set_standardFlags(mJointHelper.mNode, attrs=['sx', 'sy', 'sz'], 
                                   lock=False, visible=True,keyable=False)
        
            self.msgList_connect('jointHelpers',[mJointHelper.mNode])
            
        
        #Helpers=====================================================================================
        self.msgList_connect('prerigHandles',[self.mNode])
        
        if self.addPivot:
            mHandleFactory.addPivotSetupHelper().p_parent = mPrerigNull
        
        if self.addScalePivot:
            mHandleFactory.addScalePivotHelper().p_parent = mPrerigNull
        if self.addCog:
            mHandleFactory.addCogHelper().p_parent = mPrerigNull

        mc.parentConstraint([mMain.mNode],mPrerigNull.mNode, maintainOffset = True)
        mc.scaleConstraint([mMain.mNode],mPrerigNull.mNode, maintainOffset = True)
        
        return

    except Exception,err:
        cgmGEN.cgmException(Exception,err,msg=vars())


def prerigDelete(self):
    #if self.getMessage('templateLoftMesh'):
    #    mTemplateLoft = self.getMessage('templateLoftMesh',asMeta=True)[0]
    #    for s in mTemplateLoft.getShapes(asMeta=True):
    #        s.overrideDisplayType = 2     
    
    if self.getMessage('noTransformNull'):
        mc.delete(self.getMessage('noTransformNull'))
    return BLOCKUTILS.prerig_delete(self,templateHandles=True)

#def is_prerig(self):
#    return BLOCKUTILS.is_prerig(self,msgLinks=['moduleTarget','prerigNull'])

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
def rigDelete(self):
    
    return
    try:self.moduleTarget.masterControl.delete()
    except Exception,err:
        for a in err:
            print a
    return True
            
def is_rig(self):
    try:
        _str_func = 'is_rig'
        _l_missing = []
        
        _d_links = {'moduleTarget' : ['constrainNull']}
        
        for plug,l_links in _d_links.iteritems():
            _mPlug = self.getMessage(plug,asMeta=True)
            if not _mPlug:
                _l_missing.append("{0} : {1}".format(plug,l_links))
                continue
            for l in l_links:
                if not _mPlug[0].getMessage(l):
                    _l_missing.append(plug + '.' + l)
    
        if _l_missing:
            log.info("|{0}| >> Missing...".format(_str_func))  
            for l in _l_missing:
                log.info("|{0}| >> {1}".format(_str_func,l))  
            return False
        return True
    except Exception,err:
        cgmGEN.cgmException(Exception,err,msg=vars())

#=============================================================================================================
#>> Skeleton
#=============================================================================================================
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
        
    ml_templateHandles = self.msgList_get('templateHandles')
    
    mJoint = ml_templateHandles[0].jointHelper.doCreateAt('joint')
    JOINTS.freezeOrientation(mJoint)

    if self.getMayaAttr('cgmName'):
        self.copyAttrTo('cgmName',mJoint.mNode,'cgmName',driven='target')
    else:
        self.copyAttrTo('blockType',mJoint.mNode,'cgmName',driven='target')
        
    if mModule.getMayaAttr('cgmDirection'):
        mModule.copyAttrTo('cgmDirection',mJoint.mNode,'cgmDirection',driven='target')
    if mModule.getMayaAttr('cgmPosition'):
        mModule.copyAttrTo('cgmPosition',mJoint.mNode,'cgmPosition',driven='target')
        
    mJoint.doName()

    mRigNull.msgList_connect('moduleJoints', [mJoint])
    
    self.atBlockUtils('skeleton_connectToParent')
    
    return mJoint.mNode        

        
def skeleton_check(self):
    if self.getMessage('moduleTarget'):
        if self.moduleTarget.getMessage('rigNull'):
            if self.moduleTarget.rigNull.msgList_get('moduleJoints'):
                return True
    return False

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
    
    ml_rigJoints = BLOCKUTILS.skeleton_buildDuplicateChain(self,ml_joints, 'rig', self.mRigNull,'rigJoints')
    
    if self.mBlock.addAim:
        log.info("|{0}| >> Aim...".format(_str_func))              
        ml_aimFKJoints = BLOCKUTILS.skeleton_buildDuplicateChain(self,ml_joints[-1], 'fk', self.mRigNull, 'aimFKJoint', singleMode = True )
        ml_aimBlendJoints = BLOCKUTILS.skeleton_buildDuplicateChain(self,ml_joints[-1], 'blend', self.mRigNull, 'aimBlendJoint', singleMode = True)
        ml_aimIkJoints = BLOCKUTILS.skeleton_buildDuplicateChain(self,ml_joints[-1], 'aim', self.mRigNull, 'aimIKJoint', singleMode = True)
        ml_jointsToConnect.extend(ml_aimFKJoints + ml_aimIkJoints)
        ml_jointsToHide.extend(ml_aimBlendJoints)
    
    #...joint hide -----------------------------------------------------------------------------------
    for mJnt in ml_jointsToHide:
        try:
            mJnt.drawStyle =2
        except:
            mJnt.radius = .00001
            
    #...connect... 
    self.fnc_connect_toRigGutsVis( ml_jointsToConnect )
    
    BUILDERUTILS.joints_connectToParent(self)
    log.info("|{0}| >> Time >> = {1} seconds".format(_str_func, "%0.3f"%(time.clock()-_start)))
    return

def rig_shapes(self):
    _short = self.d_block['shortName']
    _str_func = '[{0}] > rig_shapes'.format(_short)
    log.info("|{0}| >> ...".format(_str_func))  
    _start = time.clock()
    
    mBlock = self.mBlock
    ml_templateHandles = mBlock.msgList_get('templateHandles')
    mMainHandle = ml_templateHandles[0]
    mHelper = mMainHandle.jointHelper
    mRigNull = self.mRigNull
    
    #Get our base size from the block
    _size = DIST.get_bb_size(mMainHandle.mNode,True,True)
    _side = BLOCKUTILS.get_side(self.mBlock)
    _ikPos = mHelper.getPositionByAxisDistance(mBlock.getEnumValueString('axisAim'), _size *2)
    _short_module = self.mModule.mNode
    ml_joints = self.d_joints['ml_moduleJoints']
    mBlock_upVector = mBlock.getAxisVector('y+')
    
    pprint.pprint(vars())
    

    #Aim=============================================================================================
    if mBlock.addAim:
        log.info("|{0}| >> Aim setup...".format(_str_func))  
        ikCurve = CURVES.create_fromName('sphere2',_size/2)
        textCrv = CURVES.create_text(mBlock.getAttr('cgmName') or mBlock.blockType,_size/2)
        
        CORERIG.shapeParent_in_place(ikCurve,textCrv,False)
        
        mLookAt = cgmMeta.validateObjArg(ikCurve,'cgmObject',setClass=True)
        mLookAt.p_position = _ikPos
        
        SNAP.aim_atPoint(mLookAt.mNode, mHelper.p_position, 'z-', mode='vector', vectorUp = mBlock_upVector)
        
        ATTR.copy_to(_short_module,'cgmName',mLookAt.mNode,driven='target')
        #mIK.doStore('cgmName','head')
        mLookAt.doStore('cgmTypeModifier','lookAt')
        mLookAt.doName()
        
        CORERIG.colorControl(mLookAt.mNode,_side,'main')
        mRigNull.connectChildNode(mLookAt,'lookAtHandle','rigNull')#Connect
        

    #Control ----------------------------------------------------------------------------------
    log.info("|{0}| >> Main control shape...".format(_str_func))
    if mBlock.addCog and mMainHandle.getMessage('cogHelper'):
        log.info("|{0}| >> Cog pivot setup... ".format(_str_func))    
        mControl = mMainHandle.cogHelper.doCreateAt()
    else:
        mControl = mMainHandle.doCreateAt()
        
    if mBlock.addScalePivot and mMainHandle.getMessage('scalePivotHelper'):
        log.info("|{0}| >> Scale Pivot setup...".format(_str_func))
        TRANS.scalePivot_set(mControl.mNode, mMainHandle.scalePivotHelper.p_position)
        
    CORERIG.shapeParent_in_place(mControl,mMainHandle.mNode,True)
    mControl = cgmMeta.validateObjArg(mControl,'cgmObject',setClass=True)
    ATTR.copy_to(_short_module,'cgmName',mControl.mNode,driven='target')
    mControl.doName()    
    
    CORERIG.colorControl(mControl.mNode,_side,'main')
    
    mRigNull.connectChildNode(mControl,'handle','rigNull')#Connect
    mRigNull.connectChildNode(mControl,'settings','rigNull')#Connect    
    
    #Direct Controls =============================================================================
    log.info("|{0}| >> Direct controls...".format(_str_func))      
    ml_rigJoints = mRigNull.msgList_get('rigJoints')
    
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
            
    #Pivots =======================================================================================
    if mMainHandle.getMessage('pivotHelper'):
        mBlock.atBlockUtils('pivots_buildShapes', mMainHandle.pivotHelper, mRigNull)
        
        """
        log.info("|{0}| >> Pivot helper found".format(_str_func))
        mPivotHelper = mBlock.pivotHelper
        for a in 'center','front','back','left','right':
            str_a = 'pivot' + a.capitalize()
            if mPivotHelper.getMessage(str_a):
                log.info("|{0}| >> Found: {1}".format(_str_func,str_a))
                mPivot = mPivotHelper.getMessage(str_a,asMeta=True)[0].doDuplicate(po=False)
                mRigNull.connectChildNode(mPivot,str_a,'rigNull')#Connect    
                mPivot.parent = False"""

    log.info("|{0}| >> Time >> = {1} seconds".format(_str_func, "%0.3f"%(time.clock()-_start)))
    
def rig_controls(self):
    try:
        _short = self.d_block['shortName']
        _str_func = '[{0}] > rig_controls'.format(_short)
        log.info("|{0}| >> ...".format(_str_func))  
        _start = time.clock()
      
        mBlock = self.mBlock
        ml_templateHandles = mBlock.msgList_get('templateHandles')
        mMainHandle = ml_templateHandles[0]    
        mRigNull = self.mRigNull
        ml_controlsAll = []#we'll append to this list and connect them all at the end
        mRootParent = self.mDeformNull
        mSettings = mRigNull.settings
        
            
        mHandle = mRigNull.handle
        
        # Drivers ==============================================================================================    
        #>> vis Drivers ================================================================================================	
        mPlug_visSub = self.atBuilderUtils('build_visSub')
        #mPlug_visRoot = cgmMeta.cgmAttr(mSettings,'visRoot', value = True, attrType='bool', defaultValue = False,keyable = False,hidden = False)
        mPlug_visDirect = cgmMeta.cgmAttr(mSettings,'visDirect', value = True, attrType='bool', defaultValue = False,keyable = False,hidden = False)
        
        if self.mBlock.addAim:        
            mPlug_aim = cgmMeta.cgmAttr(mSettings.mNode,'blend_aim',attrType='float',minValue=0,maxValue=1,lock=False,keyable=True)
        
        #mHandle ========================================================================================
        log.info("|{0}| >> Found handle : {1}".format(_str_func, mHandle))    
        _d = MODULECONTROL.register(mHandle,
                                    addSpacePivots = 1,
                                    addDynParentGroup = True,
                                    addConstraintGroup=False,
                                    mirrorSide= self.d_module['mirrorDirection'],
                                    mirrorAxis="translateX,rotateY,rotateZ",
                                    makeAimable = True)
        
        mHandle = _d['mObj']
        mHandle.masterGroup.parent = mRootParent
        ml_controlsAll.append(mHandle)            
        
        #>> settings ========================================================================================
        if mSettings != mHandle:
            log.info("|{0}| >> Settings setup : {1}".format(_str_func, mSettings))        
            MODULECONTROL.register(mSettings)
            mSettings.masterGroup.parent = mHandle
            ml_controlsAll.append(mSettings)
    
        #>> Direct Controls ========================================================================================
        ml_rigJoints = self.mRigNull.msgList_get('rigJoints')
        ml_controlsAll.extend(ml_rigJoints)
        
        for i,mObj in enumerate(ml_rigJoints):
            d_buffer = MODULECONTROL.register(mObj,
                                              typeModifier='direct',
                                              addDynParentGroup = True,                                          
                                              mirrorSide= self.d_module['mirrorDirection'],
                                              mirrorAxis="translateX,rotateY,rotateZ",
                                              makeAimable = False)
    
            mObj = d_buffer['instance']
            ATTR.set_hidden(mObj.mNode,'radius',True)        
            if mObj.hasAttr('cgmIterator'):
                ATTR.set_hidden(mObj.mNode,'cgmIterator',True)        
                
            for mShape in mObj.getShapes(asMeta=True):
                ATTR.connect(mPlug_visDirect.p_combinedShortName, "{0}.overrideVisibility".format(mShape.mNode))
    
        # Pivots =================================================================================================
        if mMainHandle.getMessage('pivotHelper'):
            log.info("|{0}| >> Pivot helper found".format(_str_func))
            for a in 'center','front','back','left','right':#This order matters
                str_a = 'pivot' + a.capitalize()
                if mRigNull.getMessage(str_a):
                    log.info("|{0}| >> Found: {1}".format(_str_func,str_a))
                    
                    mPivot = mRigNull.getMessage(str_a,asMeta=True)[0]
                    
                    d_buffer = MODULECONTROL.register(mPivot,
                                                      typeModifier='pivot',
                                                      mirrorSide= self.d_module['mirrorDirection'],
                                                      mirrorAxis="translateX,rotateY,rotateZ",
                                                      makeAimable = False)
                    
                    mPivot = d_buffer['instance']
                    for mShape in mPivot.getShapes(asMeta=True):
                        ATTR.connect(mPlug_visSub.p_combinedShortName, "{0}.overrideVisibility".format(mShape.mNode))                
                    
                    
                    ml_controlsAll.append(mPivot)
            
        
        #>> headLookAt ========================================================================================
        if mRigNull.getMessage('lookAtHandle'):
            mLookAtHandle = mRigNull.lookAtHandle
            log.info("|{0}| >> Found lookAtHandle : {1}".format(_str_func, mLookAtHandle))
            MODULECONTROL.register(mLookAtHandle,
                                   typeModifier='lookAt',
                                   addSpacePivots = 1,
                                   addDynParentGroup = True,
                                   addConstraintGroup=False,
                                   mirrorSide= self.d_module['mirrorDirection'],
                                   mirrorAxis="translateX,rotateY,rotateZ",
                                   makeAimable = False)
            mLookAtHandle.masterGroup.parent = mRootParent
            ml_controlsAll.append(mLookAtHandle)
    
    
        #Connections =======================================================================================
        ml_controlsAll = self.atBuilderUtils('register_mirrorIndices', ml_controlsAll)
        mRigNull.msgList_connect('controlsAll',ml_controlsAll)
        mRigNull.moduleSet.extend(ml_controlsAll)
        
        log.info("|{0}| >> Time >> = {1} seconds".format(_str_func, "%0.3f"%(time.clock()-_start)))                
        
        
        
        return 
    except Exception,err:cgmGEN.cgmException(Exception,err)

def rig_frame(self):
    try:
        _short = self.d_block['shortName']
        _str_func = '[{0}] > rig_rigFrame'.format(_short)
        log.info("|{0}| >> ...".format(_str_func))  
        _start = time.clock()
        
        mBlock = self.mBlock
        ml_templateHandles = mBlock.msgList_get('templateHandles')
        mMainHandle = ml_templateHandles[0]            
        mRigNull = self.mRigNull
        mHandle = mRigNull.handle        
        log.info("|{0}| >> Found mHandle : {1}".format(_str_func, mHandle))
        
        #Changing targets - these change based on how the setup rolls through
        mDirectDriver = mHandle
        mAimDriver = mHandle
        mRootParent = self.mDeformNull
        
        #Pivot Setup ========================================================================================
        if mMainHandle.getMessage('pivotHelper'):
            log.info("|{0}| >> Pivot setup...".format(_str_func))
            
            mPivotResultDriver = mHandle.doCreateAt()
            mPivotResultDriver.addAttr('cgmName','pivotResult')
            mPivotResultDriver.addAttr('cgmType','driver')
            mPivotResultDriver.doName()
            
            mPivotResultDriver.addAttr('cgmAlias', 'PivotResult')
            
            mDirectDriver = mPivotResultDriver
            mAimDriver = mPivotResultDriver
            mRigNull.connectChildNode(mPivotResultDriver,'pivotResultDriver','rigNull')#Connect    
     
            mBlock.atBlockUtils('pivots_setup', mControl = mHandle, mRigNull = mRigNull, pivotResult = mPivotResultDriver, rollSetup = 'default',
                                front = 'front', back = 'back')#front, back to clear the toe, heel defaults
            
    
        #Aim ========================================================================================
        if mBlock.addAim:
            log.info("|{0}| >> Aim setup...".format(_str_func))
            mSettings = mRigNull.settings
            
            mPlug_aim = cgmMeta.cgmAttr(mSettings.mNode,'blend_aim',attrType='float',lock=False,keyable=True)
            
            mAimFKJoint = mRigNull.getMessage('aimFKJoint', asMeta=True)[0]
            mAimIKJoint = mRigNull.getMessage('aimIKJoint', asMeta=True)[0]
            mAimBlendJoint = mRigNull.getMessage('aimBlendJoint', asMeta=True)[0]
            
            mDirectDriver = mAimBlendJoint
            mAimLookAt = mRigNull.lookAtHandle
            
            ATTR.connect(mPlug_aim.p_combinedShortName, "{0}.v".format(mAimLookAt.mNode))
            
            #Setup Aim -------------------------------------------------------------------------------------
            mc.aimConstraint(mAimLookAt.mNode,
                             mAimIKJoint.mNode,
                             maintainOffset = False, weight = 1,
                             aimVector = self.d_orientation['vectorAim'],
                             upVector = self.d_orientation['vectorUp'],
                             worldUpVector = self.d_orientation['vectorUp'],
                             worldUpObject = mAimDriver.mNode,
                             worldUpType = 'objectRotation' )
    
            #Setup blend ----------------------------------------------------------------------------------
            RIGCONSTRAINT.blendChainsBy(mAimFKJoint,mAimIKJoint,mAimBlendJoint,
                                        driver = mPlug_aim.p_combinedName,l_constraints=['orient'])
            
            #Parent pass ---------------------------------------------------------------------------------
            mAimLookAt.masterGroup.parent = mAimDriver
            
            for mObj in mAimFKJoint,mAimIKJoint,mAimBlendJoint:
                mObj.parent = mAimDriver
    
        else:
            log.info("|{0}| >> NO Head IK setup...".format(_str_func))    
        
    
        #Direct  ===================================================================================
        ml_rigJoints = mRigNull.msgList_get('rigJoints')
        
        #Parent the direct control to the 
        if ml_rigJoints[0].getMessage('masterGroup'):
            ml_rigJoints[0].masterGroup.parent = mDirectDriver
        else:
            ml_rigJoints[0].parent = mDirectDriver
            
        log.info("|{0}| >> Time >> = {1} seconds".format(_str_func, "%0.3f"%(time.clock()-_start)))
    except Exception,err:
        cgmGEN.cgmException(Exception,err,msg=vars())
    
def rig_cleanUp(self):
    _short = self.d_block['shortName']
    _str_func = '[{0}] > rig_cleanUp'.format(_short)
    log.info("|{0}| >> ...".format(_str_func))  
    _start = time.clock()
    
    mBlock = self.mBlock
    mRigNull = self.mRigNull
    mHandle = mRigNull.handle            
    mSettings = mRigNull.settings
    
    
    mMasterControl= self.d_module['mMasterControl']
    mMasterDeformGroup= self.d_module['mMasterDeformGroup']    
    mMasterNull = self.d_module['mMasterNull']
    mModuleParent = self.d_module['mModuleParent']
    mPlug_globalScale = self.d_module['mPlug_globalScale']
    
    
    #>>  Parent and constraining joints and rig parts =======================================================
    #>>>> mSettings.masterGroup.parent = mHandle
    
    #>>  DynParentGroups - Register parents for various controls ============================================
    ml_baseDynParents_start = []
    ml_baseDynParents_end = []
    
    #Start parents....
    if mModuleParent:
        mi_parentRigNull = mModuleParent.rigNull
        if mi_parentRigNull.getMessage('cog'):
            ml_baseDynParents_start.append( mi_parentRigNull.cog )
        else:
            ml_baseDynParents_start.append( mi_parentRigNull.msgList_get('rigJoints')[-1] )
    
    #End parents....
    ml_baseDynParents_end.append(mMasterNull.puppetSpaceObjectsGroup)
    ml_baseDynParents_end.append(mMasterNull.worldSpaceObjectsGroup)
    
    
    #...Handle -----------------------------------------------------------------------------------
    ml_baseHandleDynParents = []

    #ml_baseDynParents = [ml_controlsFK[0]]
    _moveStart = False
    if not ml_baseDynParents_start:
        _moveStart = True
        
    ml_baseHandleDynParents = copy.copy(ml_baseDynParents_start)
    ml_baseHandleDynParents.extend(mHandle.msgList_get('spacePivots',asMeta = True))
    ml_baseHandleDynParents.extend(ml_baseDynParents_end)
    
    if _moveStart:
        mPuppetSpace = ml_baseHandleDynParents.pop(-2)
        ml_baseHandleDynParents.insert(0,mPuppetSpace)
    """
    mBlendDriver =  mHandle.getMessage('blendDriver',asMeta=True)
    if mBlendDriver:
        mBlendDriver = mBlendDriver[0]
        ml_baseDynParents.insert(0, mBlendDriver)  
        mBlendDriver.addAttr('cgmAlias','neckDriver')
    """
    
    #Add our parents
    mDynGroup = mHandle.dynParentGroup
    log.info("|{0}| >> dynParentSetup : {1}".format(_str_func,mDynGroup))  
    mDynGroup.dynMode = 0

    for o in ml_baseHandleDynParents:
        mDynGroup.addDynParent(o)
    mDynGroup.rebuild()

    #mDynGroup.dynFollow.parent = mMasterDeformGroup
    
    #Direct ---------------------------------------------------------------------------------------------
    for mControl in mRigNull.msgList_get('rigJoints'):
        _short_direct = mControl.p_nameBase
        if mControl.getMessage('dynParentGroup'):
            log.info("|{0}| >> Direct control: {1}".format(_str_func,_short_direct))
            ml_directHandleDynParents = copy.copy(ml_baseDynParents_start)
            ml_directHandleDynParents.extend(ml_baseDynParents_end)
            
            mDriver = mControl.masterGroup.getParent(asMeta=True)
            if mDriver:
                ml_directHandleDynParents.insert(0, mDriver)
                if not mDriver.hasAttr('cgmAlias'):
                    mDriver.addAttr('cgmAlias',_short_direct + '_driver')
                
            mDynGroup = mControl.dynParentGroup
            log.info("|{0}| >> dynParentSetup : {1}".format(_str_func,mDynGroup))  
            mDynGroup.dynMode = 0
        
            for o in ml_directHandleDynParents:
                mDynGroup.addDynParent(o)
            mDynGroup.rebuild()        

    
    #...look at ------------------------------------------------------------------------------------------
    if mRigNull.getMessage('lookAtHandle'):
        log.info("|{0}| >> LookAt setup...".format(_str_func))
        
        mPlug_aim = cgmMeta.cgmAttr(mSettings.mNode,'blend_aim',attrType='float',lock=False,keyable=True)
        

        mHeadLookAt = mRigNull.lookAtHandle        
        mHeadLookAt.setAttrFlags(attrs='v')
        
        #...dynParentGroup...
        ml_headLookAtDynParents = copy.copy(ml_baseDynParents_start)
        ml_headLookAtDynParents.extend(mHeadLookAt.msgList_get('spacePivots',asMeta = True))
        ml_headLookAtDynParents.extend(ml_baseDynParents_end)
        
        ml_headLookAtDynParents.insert(0, mHandle)
        
        
        mPivotResultDriver = mRigNull.getMessage('pivotResultDriver',asMeta=True)
        if mPivotResultDriver:
            ml_headLookAtDynParents.insert(0, mPivotResultDriver)

            
        #mHandle.masterGroup.addAttr('cgmAlias','headRoot')
        
        #Add our parents...
        mDynGroup = mHeadLookAt.dynParentGroup
        log.info("|{0}| >> dynParentSetup : {1}".format(_str_func,mDynGroup))  
    
        for o in ml_headLookAtDynParents:
            mDynGroup.addDynParent(o)
        mDynGroup.rebuild()
        

    #>>  Lock and hide ======================================================================================

    #>>  Attribute defaults =================================================================================
    
    #Final close out stuff....move to 
    mRigNull.version = __version__
    mBlock.blockState = 'rig'
    log.info("|{0}| >> Time >> = {1} seconds".format(_str_func, "%0.3f"%(time.clock()-_start)))
    



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
    mHandle = mRigNull.handle
    mSettings = mRigNull.settings
    
    
    #>> If proxyMesh there, delete ----------------------------------------------------------------------------------- 
    _bfr = mRigNull.msgList_get('proxyMesh',asMeta=True)
    if _bfr:
        log.debug("|{0}| >> proxyMesh detected...".format(_str_func))            
        if forceNew:
            log.debug("|{0}| >> force new...".format(_str_func))                            
            mc.delete([mObj.mNode for mObj in _bfr])
        else:
            return _bfr
    
    #>> Build bbProxy -----------------------------------------------------------------------------
    if mBlock.getMessage('proxyHelper'):
        mDup = mBlock.proxyHelper.doDuplicate(po=False)
        mDup.p_parent = mRigNull.msgList_get('rigJoints')[0]
        
        ml_proxy = [mDup]
    #Connect to setup ------------------------------------------------------------------------------------
    mPuppetSettings = self.d_module['mMasterControl'].controlSettings
    _side = BLOCKUTILS.get_side(self.mBlock)
    
    for mProxy in ml_proxy:
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
        
    mRigNull.msgList_connect('proxyMesh', ml_proxy)







 








