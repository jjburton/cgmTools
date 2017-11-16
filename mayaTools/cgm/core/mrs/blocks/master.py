"""
------------------------------------------
cgm.core.mrs.blocks.simple.master
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

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

# From Maya =============================================================
import maya.cmds as mc

# From Red9 =============================================================
from Red9.core import Red9_Meta as r9Meta
import cgm.core.cgm_General as cgmGEN
from cgm.core.lib import curve_Utils as CURVES
from cgm.core.lib import rigging_utils as RIG
from cgm.core.lib import snap_utils as SNAP
from cgm.core.lib import attribute_utils as ATTR
reload(ATTR)
import cgm.core.mrs.lib.ModuleControlFactory as MODULECONTROL

import cgm.core.lib.distance_utils as DIST
import cgm.core.lib.rigging_utils as CORERIG
import cgm.core.lib.math_utils as MATH
# From cgm ==============================================================
from cgm.core import cgm_Meta as cgmMeta

#=============================================================================================================
#>> Block Settings
#=============================================================================================================
__version__ = 'alpha.11152017'
__autoTemplate__ = True
__menuVisible__ = True
__baseSize__ = 10,10,10

#>>>Attrs ----------------------------------------------------------------------------------------------------
l_attrsStandard = ['addMotionJoint','moduleTarget','baseSize']

d_attrsToMake = {'puppetName':'string',
                 'rootJoint':'messageSimple'}

d_defaultSettings = {'version':__version__,
                     'puppetName':'NotBatman',
                     'addMotionJoint':True, 
                     'attachPoint':'end'}

#MRP - Morpheus Rig Platform
#MRF - Morpheus Rig Format
#cgmRigamathig
#=============================================================================================================
#>> Define
#=============================================================================================================
def define(self):
    _short = self.mNode
    self.translate = 0,0,0
    self.rotate = 0,0,0
    self.setAttrFlags(attrs=['translate','rotate','sx','sz'])
    self.doConnectOut('sy',['sx','sz'])
    ATTR.set_alias(_short,'sy','blockScale')
    
#=============================================================================================================
#>> Template
#=============================================================================================================
def template(self):
    _average = MATH.average(self.baseSize)
    _size = _average * 1.5
    _offsetSize = _average * .1
    log.info(_size)
    _crv = CURVES.create_controlCurve(self.mNode,shape='squareOpen',direction = 'y+', sizeMode = 'fixed', size = _size)
    CORERIG.colorControl(_crv,'center','main',transparent = False) 
    
    mCrv = cgmMeta.validateObjArg(_crv,'cgmObject')
    l_offsetCrvs = []
    for shape in mCrv.getShapes():
        offsetShape = mc.offsetCurve(shape, distance = _offsetSize, ch=False )[0]
        CORERIG.colorControl(offsetShape,'center','sub',transparent = False) 
        l_offsetCrvs.append(offsetShape)
        
    for s in [_crv] + l_offsetCrvs:
        RIG.shapeParent_in_place(self.mNode,s,False)
        
    #RIG.shapeParent_in_place(self.mNode,_crv,False)
    
    
    return True

def templateDelete(self):
    self.setAttrFlags(attrs=['translate','rotate','sx','sz'], lock = False)
    
    pass#...handled in generic callmc.delete(self.getShapes())

def is_template(self):
    if self.getShapes():
        return True
    return False
#=============================================================================================================
#>> Prerig
#=============================================================================================================
def prerig(self):
    self._factory.puppet_verify()    
    
    #Create preRig Null  ==================================================================================
    mPrerigNull = self.atBlockUtils('prerigNull_verify')
    mHandleFactory = self.asHandleFactory(self.mNode)
    
    #Helpers=====================================================================================
    if self.addMotionJoint:
        mHandleFactory.addRootMotionHelper().p_parent = mPrerigNull

def prerigDelete(self):
    try:self.moduleTarget.masterNull.delete()
    except Exception,err:
        for a in err:
            print a
    return True   

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
    return True
#=============================================================================================================
#>> rig
#=============================================================================================================
def rig_cleanUp(self):
    _short = self.d_block['shortName']
    _str_func = '[{0}] > rig_cleanUp'.format(_short)
    log.info("|{0}| >> ...".format(_str_func))
    _start = time.clock()

    mBlock = self.mBlock
    mMasterControl= self.d_module['mMasterControl']
    mMasterDeformGroup= self.d_module['mMasterDeformGroup']    
    mMasterNull = self.d_module['mMasterNull']
    mPlug_globalScale = self.d_module['mPlug_globalScale']
    
    
    if mBlock.addMotionJoint:
        if not is_skeletonized(mBlock):
            build_skeleton(mBlock)
        
        mRootMotionHelper = mBlock.rootMotionHelper
        mPuppet = mBlock.moduleTarget
        mMasterNull = mPuppet.masterNull
        
        #Make joint =================================================================
        mJoint = mBlock.moduleTarget.getMessage('rootJoint', asMeta = True)[0]
        mJoint.p_parent = mBlock.moduleTarget.masterNull.skeletonGroup
        
        #Make the handle ===========================================================
        log.info("|{0}| >> Main control shape...".format(_str_func))
        mControl = mRootMotionHelper.doCreateAt()
            
            
        CORERIG.shapeParent_in_place(mControl,mRootMotionHelper.mNode,True)
        mControl = cgmMeta.validateObjArg(mControl,'cgmObject',setClass=True)
        mControl.parent = False
        
        ATTR.copy_to(mBlock.moduleTarget.mNode,'cgmName',mControl.mNode,driven='target')
        mControl.addAttr('cgmTypeModifier','rootMotion')
        mControl.doName()
        
        
        #Color ---------------------------------------------------------------
        _side = mBlock.atBlockUtils('get_side')
        CORERIG.colorControl(mControl.mNode,_side,'main')        
        
        #Register ------------------------------------------------------------
        MODULECONTROL.register(mControl,
                               addDynParentGroup = True,
                               mirrorSide= 'Centre',
                               mirrorAxis="translateX,rotateY,rotateZ")
        
        mControl.masterGroup.parent = mPuppet.masterNull.deformGroup
        
        mMasterControl.controlVis.addAttr('rootMotionControl',value = True, keyable=False)
        mControl.doConnectIn('v',"{0}.rootMotionControl".format( mMasterControl.controlVis.mNode))
        ATTR.set_standardFlags(mControl.mNode,['v'])
        
        #DynParent group ====================================================================
        ml_dynParents = [mMasterNull.puppetSpaceObjectsGroup,
                         mMasterNull.worldSpaceObjectsGroup]

        #Add our parents
        mDynGroup = mControl.dynParentGroup
        log.info("|{0}| >> dynParentSetup : {1}".format(_str_func,mDynGroup))  
        mDynGroup.dynMode = 0
    
        for o in ml_dynParents:
            mDynGroup.addDynParent(o)
        mDynGroup.rebuild()        
        
        #Connect -------------------------------------------------------------
        ml_controlsAll = [mControl]
        mPuppet.connectChildNode(mControl,'rootMotionHandle','puppet')#Connect
        mPuppet.msgList_connect('controlsAll', ml_controlsAll)
        mPuppet.puppetSet.extend( ml_controlsAll)
        self.atBuilderUtils('register_mirrorIndices', ml_controlsAll)
        #>>>>> INDEX CONTROLS
        #>>>>> Setup VIS
        
        mc.parentConstraint(mControl.mNode,
                            mJoint.mNode,
                            maintainOffset = True)
        mc.scaleConstraint(mControl.mNode,
                           mJoint.mNode,
                           maintainOffset = True)
        #Connections =======================================================================================
        #ml_controlsAll = mBlock.atBuilderUtils('register_mirrorIndices', ml_controlsAll)
        #mRigNull.msgList_connect('controlsAll',ml_controlsAll)
        #mRigNull.moduleSet.extend(ml_controlsAll)        
    mBlock.template = 1    
    
    
    
    #mRigNull.version = self.d_block['buildVersion']
    
    log.info("|{0}| >> Time >> = {1} seconds".format(_str_func, "%0.3f"%(time.clock()-_start)))
    

def rig(self):
    #
    _str_func = 'rig'
    
    self.moduleTarget._verifyMasterControl(size = DIST.get_bb_size(self.mNode,True,'max') * 1.5)
    
    if self.addMotionJoint:
        if not is_skeletonized(self):
            build_skeleton(self)
        
        mRootMotionHelper = self.rootMotionHelper
        mPuppet = self.moduleTarget
        mMasterNull = mPuppet.masterNull
        
        #Make joint =================================================================
        mJoint = self.moduleTarget.getMessage('rootJoint', asMeta = True)[0]
        mJoint.p_parent = self.moduleTarget.masterNull.skeletonGroup
        
        #Make the handle ===========================================================
        log.info("|{0}| >> Main control shape...".format(_str_func))
        mControl = mRootMotionHelper.doCreateAt()
            
            
        CORERIG.shapeParent_in_place(mControl,mRootMotionHelper.mNode,True)
        mControl = cgmMeta.validateObjArg(mControl,'cgmObject',setClass=True)
        mControl.parent = False
        
        ATTR.copy_to(self.moduleTarget.mNode,'cgmName',mControl.mNode,driven='target')
        mControl.addAttr('cgmTypeModifier','rootMotion')
        mControl.doName()
        
        print mControl.mNode
        
        #Color ---------------------------------------------------------------
        _side = self.atBlockUtils('get_side')
        CORERIG.colorControl(mControl.mNode,_side,'main')        
        
        #Register ------------------------------------------------------------
        MODULECONTROL.register(mControl,
                               addDynParentGroup = True,
                               mirrorSide= 'Centre',
                               mirrorAxis="translateX,rotateY,rotateZ")
        
        mControl.masterGroup.parent = mPuppet.masterNull.deformGroup
        
        #DynParent group ====================================================================
        ml_dynParents = [mMasterNull.puppetSpaceObjectsGroup,
                         mMasterNull.worldSpaceObjectsGroup]

        #Add our parents
        mDynGroup = mControl.dynParentGroup
        log.info("|{0}| >> dynParentSetup : {1}".format(_str_func,mDynGroup))  
        mDynGroup.dynMode = 0
    
        for o in ml_dynParents:
            mDynGroup.addDynParent(o)
        mDynGroup.rebuild()        
        
        #Connect -------------------------------------------------------------
        mPuppet.connectChildNode(mControl,'rootMotionHandle','puppet')#Connect
        mPuppet.msgList_connect('controlsAll', [mControl])
        
        #add to object set
        
        #Connections =======================================================================================
        #ml_controlsAll = self.atBuilderUtils('register_mirrorIndices', ml_controlsAll)
        #mRigNull.msgList_connect('controlsAll',ml_controlsAll)
        #mRigNull.moduleSet.extend(ml_controlsAll)        
    self.template = 1

def rigDelete(self):
    self.template = 0
    try:self.moduleTarget.masterControl.delete()
    except Exception,err:
        cgmGEN.cgmExceptCB(Exception,err)
        raise Exception,err
    return True
            
def is_rig(self):
    _str_func = 'is_rig'
    _l_missing = []
    
    _d_links = {'moduleTarget' : ['masterControl']}
    
    for plug,l_links in _d_links.iteritems():
        _mPlug = self.getMessage(plug,asMeta=True)[0]
        if not _mPlug:
            _l_missing.append("{0} : {1}".format(plug,l_links))
            continue
        for l in l_links:
            if not _mPlug.getMessage(l):
                _l_missing.append(_mPlug.p_nameBase + '.' + l)

    if _l_missing:
        log.info("|{0}| >> Missing...".format(_str_func))  
        for l in _l_missing:
            log.info("|{0}| >> {1}".format(_str_func,l))  
        return False
    return True

#=============================================================================================================
#>> Skeleton
#=============================================================================================================
def build_skeleton(self):
    #    
    if is_skeletonized(self):
        return True
    
    if self.addMotionJoint:
        mPuppet = self.moduleTarget
        if not mPuppet:
            raise ValueError,"No moduleTarget connected"
        
        mJoint = self.rootMotionHelper.doCreateAt('joint')
        mPuppet.connectChildNode(mJoint,'rootJoint','module')
        mJoint.connectParentNode(self,'module','rootJoint')
        self.copyAttrTo('puppetName',mJoint.mNode,'cgmName',driven='target')
        mJoint.doStore('cgmTypeModifier','rootMotion')
        mJoint.doName()
        return mJoint.mNode
        
def is_skeletonized(self):
    if self.addMotionJoint:
        if not self.getMessage('rootJoint'):
            return False
    return True

def skeletonDelete(self):
    if is_skeletonized(self):
        log.warning("MUST ACCOUNT FOR CHILD JOINTS")
        mc.delete(self.getMessage('rootJoint'))
    return True
            






 








