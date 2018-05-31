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
import cgm.core.cgm_General as cgmGEN
from cgm.core.lib import curve_Utils as CURVES
from cgm.core.lib import rigging_utils as RIG
from cgm.core.lib import snap_utils as SNAP
from cgm.core.lib import attribute_utils as ATTR
import cgm.core.lib.transform_utils as TRANS
import cgm.core.tools.lib.snap_calls as SNAPCALLS
reload(ATTR)
import cgm.core.mrs.lib.ModuleControlFactory as MODULECONTROL
import cgm.core.classes.NodeFactory as NODEFACTORY

import cgm.core.lib.distance_utils as DIST
import cgm.core.lib.rigging_utils as CORERIG
import cgm.core.lib.math_utils as MATH

# From cgm ==============================================================
from cgm.core import cgm_Meta as cgmMeta

#=============================================================================================================
#>> Block Settings
#=============================================================================================================
__version__ = 'alpha.1.03212018'
__autoTemplate__ = True
__menuVisible__ = True
__baseSize__ = 10,10,10

#>>>Profiles =====================================================================================================
d_build_profiles = {'unityMobile':{'addMotionJoint':True},
                    'unityPC':{'addMotionJoint':True,},
                    'feature':{'addMotionJoint':False}}

#>>>Attrs =======================================================================================================
l_attrsStandard = ['addMotionJoint',
                   'moduleTarget',
                   'baseSize',
                   'controlOffset',
                   'numSpacePivots',
                   'buildProfile']

d_attrsToMake = {'rootJoint':'messageSimple',
                 }

d_defaultSettings = {'version':__version__,
                     'baseName':'MasterBlock',
                     'addMotionJoint':True,
                     'controlOffset':1,
                     'numSpacePivots':1,
                     'attachPoint':'end'}

d_wiring_prerig = {'msgLinks':['moduleTarget'],
                   'msgLists':['prerigHandles']}
d_wiring_template = {'msgLinks':['templateNull']}


#MRP - Morpheus Rig Platform
#MRF - Morpheus Rig Format
#cgmRigamathig

def uiBuilderMenu(self,parent = None):
    uiMenu = mc.menuItem( parent = parent, l='Master:', subMenu=True)
    _short = self.p_nameShort
    
    mc.menuItem(uiMenu,
                ann = '[{0}] Recreate the base shape and push values to baseSize attr'.format(_short),                                                    
                c = cgmGEN.Callback(resize_masterShape,self),
                label = "Resize")            
    
#=============================================================================================================
#>> Define
#=============================================================================================================
def define(self):
    _short = self.mNode
    #self.translate = 0,0,0
    #self.rotate = 0,0,0
    ATTR.set_alias(_short,'sy','blockScale')    
    self.setAttrFlags(attrs=['sx','sz','sz'])
    self.doConnectOut('sy',['sx','sz'])
    
    try:mc.delete(self.getShapes())
    except:pass
    
    
#=============================================================================================================
#>> Template
#=============================================================================================================
@cgmGEN.Timer
def resize_masterShape(self,sizeBy=None):
    try:
        
        _short = self.p_nameShort        
        _str_func = '[{0}] resize_masterShape'.format(_short)
        log.debug("|{0}| >> ".format(_str_func)+ '-'*80)
        _sel = mc.ls(sl=True)
        _bb = False
        
        if _sel:
            _bb = TRANS.bbSize_get(_sel,False)
        elif self.getBlockChildren():
            sizeBy = mc.ls(self.getBlockChildren(asMeta=False))
            _bb = TRANS.bbSize_get(sizeBy,False)
        else:
            _bb = self.baseSize
            
        self.baseSize = _bb

        log.debug("|{0}| >> _bb: {1}".format(_str_func,_bb))

        mHandleFactory = self.asHandleFactory(_short)
        mc.delete(self.getShapes())
        
        _average = MATH.average([_bb[0],_bb[2]])
        _size = _average * 1.5
        _offsetSize = _average * .1    
        _blockScale = self.blockScale
        mTemplateNull = self.atUtils('stateNull_verify','template')
        
        #Main curve ===========================================================================
        _crv = CURVES.create_fromName(name='circle',direction = 'y+', size = 1)
        mCrv = cgmMeta.asMeta(_crv)
        SNAP.go(mCrv.mNode,self.mNode,rotation=False)
        TRANS.scale_to_boundingBox(mCrv.mNode, [_bb[0],None,_bb[2]])
        
        
        #mDup = mCrv.doDuplicate(po=False)
        #mDup.p_position = MATH.list_add(mDup.p_position, [0,_offsetSize,0])
        
        RIG.shapeParent_in_place(self.mNode,_crv,False)
        #RIG.shapeParent_in_place(self.mNode,mDup.mNode,False)
        
        mHandleFactory.color(self.mNode,'center','main',transparent = False)
        
        #Bounding box ==================================================================
        if self.getMessage('bbHelper'):
            self.bbHelper.delete()
            
        _bb_shape = CURVES.create_controlCurve(self.mNode,'cubeOpen', size = 1, sizeMode='fixed')
        _bb_newSize = MATH.list_mult(self.baseSize,[_blockScale,_blockScale,_blockScale])
        TRANS.scale_to_boundingBox(_bb_shape,_bb_newSize)
        mBBShape = cgmMeta.validateObjArg(_bb_shape, 'cgmObject',setClass=True)
        mBBShape.p_parent = mTemplateNull
        
        mBBShape.inheritsTransform = False
        mc.parentConstraint(self.mNode,mBBShape.mNode,maintainOffset=False)
        
        SNAPCALLS.snap( mBBShape.mNode,self.mNode,objPivot='axisBox',objMode='y-')
        
        CORERIG.copy_pivot(mBBShape.mNode,self.mNode)
        self.doConnectOut('baseSize', "{0}.scale".format(mBBShape.mNode))
        #mHandleFactory.color(mBBShape.mNode,controlType='sub')
        mBBShape.setAttrFlags()
        
        mBBShape.doStore('cgmName', self.mNode)
        mBBShape.doStore('cgmType','bbVisualize')
        mBBShape.doName()
        mBBShape.template = True
        self.connectChildNode(mBBShape.mNode,'bbHelper')        
        
        return
        #Offset visualize ==================================================================
        if self.getMessage('offsetHelper'):
            self.offsetHelper.delete()
        
        mShape = self.getShapes(asMeta=True)[0]
        l_return = mc.offsetCurve(mShape.mNode, distance = 1, ch=True )
        pprint.pprint(l_return)
        mHandleFactory.color(l_return[0],'center','sub',transparent = False)
        
        mOffsetShape = cgmMeta.validateObjArg(l_return[0], 'cgmObject',setClass=True)
        mOffsetShape.p_parent = mTemplateNull
        
        mOffsetShape.inheritsTransform = False
        mc.parentConstraint(self.mNode,mOffsetShape.mNode,maintainOffset=False)        
        
        #mOffsetShape.setAttrFlags()
        
        _arg = '{0}.distance = -{1}.controlOffset * {1}.blockScale'.format(l_return[1],
                                                                           self.mNode)
        NODEFACTORY.argsToNodes(_arg).doBuild()
        #self.doConnectOut('controlOffset',"{0}.distance".format(l_return[1]))
        
        mOffsetShape.doStore('cgmName', self.mNode)
        mOffsetShape.doStore('cgmType','offsetVisualize')
        mOffsetShape.doName()        
        
        self.connectChildNode(mOffsetShape.mNode,'offsetHelper')        
        
        return

        _crv = CURVES.create_fromName(name='squareOpen',direction = 'y+', size = 1)    
        TRANS.scale_to_boundingBox(_crv, [_bb[0],None,_bb[2]])
    
        mHandleFactory.color(_crv,'center','sub',transparent = False)
    
        mCrv = cgmMeta.validateObjArg(_crv,'cgmObject')
        l_offsetCrvs = []
        for shape in mCrv.getShapes():
            offsetShape = mc.offsetCurve(shape, distance = -_offsetSize, ch=True )[0]
            mHandleFactory.color(offsetShape,'center','main',transparent = False)
            l_offsetCrvs.append(offsetShape)
    
        RIG.combineShapes(l_offsetCrvs + [_crv], True)
        SNAP.go(_crv,self.mNode)    
    
        RIG.shapeParent_in_place(self.mNode,_crv,True)
    
        self.baseSize = _bb
        
        
        
        #Bounding box ==================================================================
        if self.getMessage('offsetVisualize'):
            self.bbVisualize.delete()
            
        _bb_shape = CURVES.create_controlCurve(self.mNode,'cubeOpen', size = 1.0, sizeMode='fixed')
        mBBShape = cgmMeta.validateObjArg(_bb_shape, 'cgmObject',setClass=True)
        mBBShape.p_parent = mTemplateNull
        
        SNAPCALLS.snap( mBBShape.mNode,self.mNode,objPivot='axisBox',objMode='y-')
        
        
        CORERIG.copy_pivot(mBBShape.mNode,self.mNode)
        self.doConnectOut('baseSize', "{0}.scale".format(mBBShape.mNode))
        mHandleFactory.color(mBBShape.mNode,controlType='sub')
        mBBShape.setAttrFlags()
        
        mBBShape.doStore('cgmName', self.mNode)
        mBBShape.doStore('cgmType','bbVisualize')
        mBBShape.doName()    
        
        self.connectChildNode(mBBShape.mNode,'bbHelper')
        
        
        return True
    
    except Exception,err:cgmGEN.cgmException(Exception,err)
    
    
    
def template(self):
    _short = self.mNode    
    _str_func = '[{0}] template'.format(_short)
    log.debug("|{0}| >> ".format(_str_func)+ '-'*80)


    #_average = MATH.average([self.baseSize[0],self.baseSize[2]])
    #_size = _average * 1.5
    #_offsetSize = _average * .1
    #log.info(_size)
    
    #mHandleFactory = self.asHandleFactory(_short)
    mc.select(cl=True)
    resize_masterShape(self)
    
    
    return True



    _crv = CURVES.create_controlCurve(self.mNode,shape='squareOpen',direction = 'y+', sizeMode = 'fixed', size = 1)    
    TRANS.scale_to_boundingBox(_crv, [self.baseSize[0],None,self.baseSize[2]])
    
    mHandleFactory.color(_crv,'center','sub',transparent = False)
    
    mCrv = cgmMeta.validateObjArg(_crv,'cgmObject')
    l_offsetCrvs = []
    for shape in mCrv.getShapes():
        offsetShape = mc.offsetCurve(shape, distance = -_offsetSize, ch=False )[0]
        mHandleFactory.color(offsetShape,'center','main',transparent = False)
        
        l_offsetCrvs.append(offsetShape)
        
    for s in [_crv] + l_offsetCrvs:
        RIG.shapeParent_in_place(self.mNode,s,False)
    return True

def templateDelete(self):
    self.setAttrFlags(attrs=['translate','rotate','sx','sz'], lock = False)

def is_template(self):
    if self.getShapes():
        return True
    return False

#=============================================================================================================
#>> Prerig
#=============================================================================================================
def prerig(self):
    self.atUtils('puppet_verify')
    
    
    #Create preRig Null  ==================================================================================
    mPrerigNull = self.atBlockUtils('prerigNull_verify')
    mHandleFactory = self.asHandleFactory(self.mNode)
    ml_handles = [self.mNode]
    
    #Helpers=====================================================================================
    self.msgList_connect('prerigHandles',[self.mNode])
    
    if self.addMotionJoint:
        mMotionJoint = mHandleFactory.addRootMotionHelper()
        mMotionJoint.p_parent = mPrerigNull
        

def prerigDelete(self):
    self.atBlockUtils('prerig_delete',templateHandles=True)
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
@cgmGEN.Timer
def rig_prechecks(self):
    #try:
    #_short = self.d_block['shortName']
    _str_func = 'rig_prechecks'
    log.debug("|{0}| >>  ".format(_str_func)+ '-'*80)
    log.debug("{0}".format(self))
    
    if not self.mBlock.buildProfile:
        self.l_errors.append('Must have build profile')
        return False
    
    return True

@cgmGEN.Timer
def rig_cleanUp(self):
    #try:
    _short = self.d_block['shortName']
    _str_func = 'rig_cleanUp'.format(_short)
    log.debug("|{0}| >>  ".format(_str_func)+ '-'*80)
    log.debug("{0}".format(self))
    
    #_start = time.clock()

    mBlock = self.mBlock
    mMasterControl= self.d_module['mMasterControl']
    mMasterDeformGroup= self.d_module['mMasterDeformGroup']    
    mMasterNull = self.d_module['mMasterNull']
    mPlug_globalScale = self.d_module['mPlug_globalScale']
    _spacePivots = mBlock.numSpacePivots
    
    ml_controlsAll = []
    
    #MasterControl =======================================================================
    log.debug("|{0}| >> MasterConrol | dynParent setup...".format(_str_func))
    reload(MODULECONTROL)

    
    if not _spacePivots:
        mConstrainGroup = mMasterControl.doGroup(True,True,asMeta=True,typeModifier = 'constrain')
        mConstrainGroup.addAttr('cgmAlias','{0}_constrain'.format(mMasterNull.puppet.cgmName))
    else:
        MODULECONTROL.register(mMasterControl,
                               addDynParentGroup = True,
                               addSpacePivots=_spacePivots,
                               mirrorSide= 'Centre',
                               mirrorAxis="translateX,rotateY,rotateZ",
                               noFreeze = True)
        mMasterControl.masterGroup.setAttrFlags()
        ml_dynParents = [mMasterNull]
        
        ml_dynParents.extend(mMasterControl.msgList_get('spacePivots',asMeta = True))    
    
        mDynGroup = mMasterControl.dynParentGroup
        mDynGroup.dynMode = 0

        for o in ml_dynParents:
            mDynGroup.addDynParent(o)
        mDynGroup.rebuild()
    #mMasterGroup = mMasterControl.masterGroup
    #ml_dynParents.append(mMasterGroup)

    #Add our parents
    mPuppet = mBlock.moduleTarget
 
    
    
    #Motion Joint ==========================================================================
    if mBlock.addMotionJoint:
        if not skeleton_check(mBlock):
            skeleton_build(mBlock)
        
        mRootMotionHelper = mBlock.rootMotionHelper
        mMasterNull = mPuppet.masterNull
        
        #Make joint =================================================================
        mJoint = mBlock.moduleTarget.getMessage('rootJoint', asMeta = True)[0]
        mJoint.p_parent = mBlock.moduleTarget.masterNull.skeletonGroup
        
        #Make the handle ===========================================================
        log.debug("|{0}| >> Motion Joint | Main control shape...".format(_str_func))
        mControl = mRootMotionHelper.doCreateAt()
            
            
        CORERIG.shapeParent_in_place(mControl,mRootMotionHelper.mNode,True)
        mControl = cgmMeta.validateObjArg(mControl,'cgmObject',setClass=True)
        mControl.parent = False
        
        ATTR.copy_to(mBlock.moduleTarget.mNode,'cgmName',mControl.mNode,driven='target')
        mControl.addAttr('cgmTypeModifier','rootMotion')
        mControl.doName()
        
        
        #Color ---------------------------------------------------------------
        log.debug("|{0}| >> Motion Joint | Color...".format(_str_func))            
        _side = mBlock.atBlockUtils('get_side')
        CORERIG.colorControl(mControl.mNode,_side,'main')        
        
        #Register ------------------------------------------------------------
        log.debug("|{0}| >> Motion Joint | Register...".format(_str_func))
        
        MODULECONTROL.register(mControl,
                               addDynParentGroup = True,
                               mirrorSide= 'Centre',
                               mirrorAxis="translateX,rotateY,rotateZ")
        
        mControl.masterGroup.parent = mPuppet.masterNull.deformGroup
        
        mMasterControl.controlVis.addAttr('rootMotionControl',value = True, keyable=False)
        mMasterControl.rootMotionControl = 0
        
        mControl.doConnectIn('v',"{0}.rootMotionControl".format( mMasterControl.controlVis.mNode))
        ATTR.set_standardFlags(mControl.mNode,['v'])
        
        #DynParent group ====================================================================
        ml_dynParents = [mMasterNull.puppetSpaceObjectsGroup,
                         mMasterNull.worldSpaceObjectsGroup]
                         
        #mMasterGroup = mMasterControl.masterGroup
        #ml_dynParents.append(mMasterGroup)

        #Add our parents
        mDynGroup = mControl.dynParentGroup
        log.debug("|{0}| >> Motion Joint | dynParentSetup : {1}".format(_str_func,mDynGroup))  
        mDynGroup.dynMode = 0
    
        for o in ml_dynParents:
            mDynGroup.addDynParent(o)
        mDynGroup.rebuild()
        
        #>>>>> INDEX CONTROLS
        #>>>>> Setup VIS
        mJoint.connectChildNode(mControl.mNode,'rigJoint','sourceJoint')
        
        """
        mc.parentConstraint(mControl.mNode,
                            mJoint.mNode,
                            maintainOffset = True)
        mc.scaleConstraint(mControl.mNode,
                           mJoint.mNode,
                           maintainOffset = True)            
        """
        ml_controlsAll.append(mControl)
        mPuppet.connectChildNode(mControl,'rootMotionHandle','puppet')#Connect
        
    #Connect -------------------------------------------------------------
    mPuppet.msgList_connect('controlsAll', ml_controlsAll)
    mPuppet.puppetSet.extend( ml_controlsAll)
    #self.atBuilderUtils('register_mirrorIndices', ml_controlsAll)
    self.atBuilderUtils('check_nameMatches', ml_controlsAll)
    

    #Connections =======================================================================================
    #ml_controlsAll = mBlock.atBuilderUtils('register_mirrorIndices', ml_controlsAll)
    #mRigNull.msgList_connect('controlsAll',ml_controlsAll)
    #mRigNull.moduleSet.extend(ml_controlsAll)        
    
    self.v = 0
    
    #mRigNull.version = self.d_block['buildVersion']
    #mRigNull.version = __version__
    mBlock.blockState = 'rig'
    mBlock.template = True
    self.version = self.d_block['buildVersion']
    
    #log.info("|{0}| >> Time >> = {1} seconds".format(_str_func, "%0.3f"%(time.clock()-_start)))
    #except Exception,err:cgmGEN.cgmException(Exception,err)

def rigDelete(self):
    self.template = False    
    
    return True
    self.v = 1
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
#>> Bind
#=============================================================================================================
def skeleton_build(self):
    #    
    try:
        if skeleton_check(self):
            return True
        if self.addMotionJoint:
            mPuppet = self.moduleTarget
            if not mPuppet:
                raise ValueError,"No moduleTarget connected"
            
            mJoint = self.rootMotionHelper.doCreateAt('joint')
            mPuppet.connectChildNode(mJoint,'rootJoint','module')
            mJoint.connectParentNode(self,'module','rootJoint')
            self.copyAttrTo('cgmName',mJoint.mNode,'cgmName',driven='target')
            mJoint.doStore('cgmTypeModifier','rootMotion')
            mJoint.doName()
            
            #self.atBlockUtils('skeleton_connectToParent')
            mJoint.p_parent = self.moduleTarget.masterNull.skeletonGroup
            return mJoint.mNode
        
    except Exception,err:cgmGEN.cgmException(Exception,err
                                             )
def skeleton_check(self):
    if self.addMotionJoint:
        if not self.getMessage('rootJoint'):
            return False
    return True

def skeleton_delete(self):
    if skeleton_check(self):
        log.warning("MUST ACCOUNT FOR CHILD JOINTS")
        mc.delete(self.getMessage('rootJoint'))
    return True

__l_rigBuildOrder__ = ['rig_cleanUp']






 








