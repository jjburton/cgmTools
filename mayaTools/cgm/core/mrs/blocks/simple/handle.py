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

from cgm.core.lib import curve_Utils as CURVES
from cgm.core.lib import rigging_utils as CORERIG
from cgm.core.lib import snap_utils as SNAP
from cgm.core.lib import attribute_utils as ATTR
import cgm.core.lib.distance_utils as DIST
import cgm.core.lib.shared_data as CORESHARE
import cgm.core.rig.constraint_utils as RIGCONSTRAINT

import cgm.core.cgmPy.validateArgs as VALID
import cgm.core.rig.joint_utils as JOINTS
import cgm.core.mrs.lib.ModuleControlFactory as MODULECONTROL
reload(MODULECONTROL)
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

    self.copyAttrTo('cgmName',mJoint.mNode,'cgmName',driven='target')
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
    
    ml_rigJoints = BLOCKUTILS.skeleton_buildDuplicateChain(ml_joints, 'rig', self.mRigNull,'rigJoints')
    
    if self.mBlock.addAim:
        log.info("|{0}| >> Aim...".format(_str_func))              
        ml_aimFKJoints = BLOCKUTILS.skeleton_buildDuplicateChain(ml_joints[-1], 'fk', self.mRigNull, 'aimFKJoint', singleMode = True )
        ml_aimBlendJoints = BLOCKUTILS.skeleton_buildDuplicateChain(ml_joints[-1], 'blend', self.mRigNull, 'aimBlendJoint', singleMode = True)
        ml_aimIkJoints = BLOCKUTILS.skeleton_buildDuplicateChain(ml_joints[-1], 'aim', self.mRigNull, 'aimIKJoint', singleMode = True)
        ml_jointsToConnect.extend(ml_aimFKJoints + ml_aimIkJoints)
        ml_jointsToHide.extend(ml_aimBlendJoints)
        
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
    
    mBlock = self.mBlock
    mHelper = mBlock.jointHelper
    mRigNull = self.mRigNull
    
    #Get our base size from the block
    _size = DIST.get_bb_size(_short,True,True)
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
    mControl = mBlock.doCreateAt()
    CORERIG.shapeParent_in_place(mControl,self.mBlock.mNode,True)
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
    if mBlock.getMessage('pivotHelper'):
        mBlock.atBlockUtils('pivots_buildShapes', mBlock.pivotHelper, mRigNull)
        
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
    _short = self.d_block['shortName']
    _str_func = '[{0}] > rig_controls'.format(_short)
    log.info("|{0}| >> ...".format(_str_func))  
    _start = time.clock()
  
    mBlock = self.mBlock
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
    if mBlock.getMessage('pivotHelper'):
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


def rig_frame(self):
    _short = self.d_block['shortName']
    _str_func = '[{0}] > rig_rigFrame'.format(_short)
    log.info("|{0}| >> ...".format(_str_func))  
    _start = time.clock()
    
    mBlock = self.mBlock
    mRigNull = self.mRigNull
    mHandle = mRigNull.handle        
    log.info("|{0}| >> Found mHandle : {1}".format(_str_func, mHandle))
    
    #Changing targets - these change based on how the setup rolls through
    mDirectDriver = mHandle
    mAimDriver = mHandle
    mRootParent = self.mDeformNull
    
    #Pivot Setup ========================================================================================
    if mBlock.getMessage('pivotHelper'):
        log.info("|{0}| >> Pivot setup...".format(_str_func))
        
        mPivotResultDriver = mHandle.doCreateAt()
        mPivotResultDriver.addAttr('cgmName','pivotResult')
        mPivotResultDriver.addAttr('cgmType','driver')
        mPivotResultDriver.doName()
        
        mPivotResultDriver.addAttr('cgmAlias', 'PivotResult')
        
        mAimDriver = mPivotResultDriver
        mRigNull.connectChildNode(mPivotResultDriver,'pivotResultDriver','rigNull')#Connect    
 
        mBlock.atBlockUtils('pivots_setup', mControl = mHandle, mRigNull = mRigNull, pivotResult = mPivotResultDriver, rollSetup = 'default',
                            front = 'front', back = 'back')#front, back to clear the toe, heel defaults
        

    #Aim ========================================================================================
    if self.mBlock.addAim:
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
    
    #End parents....
    ml_baseDynParents_end.append(mMasterNull.puppetSpaceObjectsGroup)
    ml_baseDynParents_end.append(mMasterNull.worldSpaceObjectsGroup)
    
    
    #...Handle -----------------------------------------------------------------------------------
    ml_baseHandleDynParents = []

    #ml_baseDynParents = [ml_controlsFK[0]]

    ml_baseHandleDynParents = copy.copy(ml_baseDynParents_start)
    ml_baseHandleDynParents.extend(mHandle.msgList_get('spacePivots',asMeta = True))
    ml_baseHandleDynParents.extend(ml_baseDynParents_end)
    
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
    
    mRigNull.version = self.d_block['buildVersion']
    
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
    mHandle = mRigNull.headFK
    mSettings = mRigNull.settings
    mPuppetSettings = self.d_module['mMasterControl'].controlSettings
    _side = BLOCKUTILS.get_side(self.mBlock)
    
    
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
    
    
    #Connect to setup ------------------------------------------------------------------------------------
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
                       'rig_frame',
                       'rig_cleanUp']





 








