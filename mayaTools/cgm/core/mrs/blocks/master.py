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
log.setLevel(logging.INFO)

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
#reload(ATTR)
import cgm.core.mrs.lib.ModuleControlFactory as MODULECONTROL
import cgm.core.classes.NodeFactory as NODEFACTORY
import cgm.core.mrs.lib.blockShapes_utils as BLOCKSHAPES
#reload(BLOCKSHAPES)
import cgm.core.lib.distance_utils as DIST
import cgm.core.lib.rigging_utils as CORERIG
import cgm.core.lib.math_utils as MATH

# From cgm ==============================================================
from cgm.core import cgm_Meta as cgmMeta

#=============================================================================================================
#>> Block Settings
#=============================================================================================================
__version__ = '1.04302019'
__MAYALOCAL = 'MASTER'


__autoForm__ = True
__menuVisible__ = True
__baseSize__ = 170,170,170

#>>>Profiles =====================================================================================================
d_build_profiles = {'unityLow':{'addMotionJoint':True},
                    'unityMed':{'addMotionJoint':True,},
                    'feature':{'addMotionJoint':False}}

#>>>Attrs =======================================================================================================
l_attrsStandard = ['addMotionJoint',
                   'moduleTarget',
                   'baseSize',
                   'controlOffset',
                   'numSpacePivots']

d_attrsToMake = {'rootJoint':'messageSimple',
                 }

d_defaultSettings = {'version':__version__,
                     'baseName':'MasterBlock',
                     'addMotionJoint':True,
                     'controlOffset':.9999,
                     'numSpacePivots':1,
                     'attachPoint':'end'}

d_wiring_prerig = {'msgLinks':['moduleTarget']}
d_wiring_form = {'msgLinks':['formNull','noTransFormNull']}

_d_attrStateMasks = {0:[],
                     1:[],
                     2:[],
                     3:['addMotionJoint'],
                     4:[]}

_d_attrStateOn = {0:[],
                  1:['hasJoint'],
                  2:['rotPivotPlace','basicShape'],
                  3:[],
                  4:[]}
_d_attrStateOff = {0:[],
                  1:[],
                  2:['baseSize','scaleY'],
                  3:['addMotionJoint'],
                  4:[]}

#MRP - Morpheus Rig Platform
#MRF - Morpheus Rig Format
#cgmRigamathig

def uiBuilderMenu(self,parent = None):
    _short = self.p_nameShort
    
    mc.menuItem(en=False,
                label = "Master")        
    
    mc.menuItem(ann = '[{0}] Recreate the base shape and push values to baseSize attr'.format(_short),
                c = cgmGEN.Callback(resize_masterShape,self,**{'resize':1}),
                label = "Resize")            
    
#=============================================================================================================
#>> Define
#=============================================================================================================
def define(self):
    try:
        _short = self.mNode
        ATTR.set_alias(_short,'sy','blockScale')    
        self.setAttrFlags(attrs=['sx','sz','sz'])
        self.doConnectOut('sy',['sx','sz'])
        ATTR.set_min(_short,'controlOffset',.001)
        
        try:mc.delete(self.getShapes())
        except:pass
    except Exception,err:
        cgmGEN.cgmExceptCB(Exception,err,localDat=vars())    
    
#=============================================================================================================
#>> Form
#=============================================================================================================
@cgmGEN.Timer
def resize_masterShape(self,sizeBy=None,resize=False):
    try:
        
        _short = self.p_nameShort        
        _str_func = '[{0}] resize_masterShape'.format(_short)
        log.debug("|{0}| >> ".format(_str_func)+ '-'*80)
        _sel = mc.ls(sl=True)
        _bb = False
        _bb = self.baseSize
        
        if resize:
            if _sel:
                _bb = TRANS.bbSize_get(_sel,False)
            #elif self.getBlockChildren():
            #    sizeBy = mc.ls(self.getBlockChildren(asMeta=False))
            #    _bb = TRANS.bbSize_get(sizeBy,False)
            self.baseSize = _bb

        log.debug("|{0}| >> _bb: {1}".format(_str_func,_bb))

        mHandleFactory = self.asHandleFactory(_short)
        mc.delete(self.getShapes())
        
        _average = MATH.average([_bb[0],_bb[2]])
        _size = _average * 1.5
        _offsetSize = _average * .01    
        _blockScale = self.blockScale
        mFormNull = self.atUtils('stateNull_verify','form')
        mNoTransformNull = self.atUtils('noTransformNull_verify','form')
        
        if resize or self.controlOffset == .9999:
            self.controlOffset = _offsetSize
            
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
        mBBShape.p_parent = mFormNull
        
        mBBShape.inheritsTransform = False
        mc.parentConstraint(self.mNode,mBBShape.mNode,maintainOffset=False)
        
        SNAPCALLS.snap( mBBShape.mNode,self.mNode,objPivot='axisBox',objMode='y-')
        
        CORERIG.copy_pivot(mBBShape.mNode,self.mNode)
        self.doConnectOut('baseSize', "{0}.scale".format(mBBShape.mNode))
        #mHandleFactory.color(mBBShape.mNode,controlType='sub')
        mBBShape.setAttrFlags()
        
        mBBShape.doStore('cgmName', self)
        mBBShape.doStore('cgmType','bbVisualize')
        mBBShape.doName()
        mBBShape.template = True
        self.connectChildNode(mBBShape.mNode,'bbHelper')
        
        #Offset visualize ==================================================================
        if self.getMessage('offsetHelper'):
            self.offsetHelper.delete()
            
        #Need to guess our offset size based on bounding box volume
        
        mShape = self.getShapes(asMeta=True)[0]
        l_return = mc.offsetCurve(mShape.mNode, distance = 1, ch=True )
        #pprint.pprint(l_return)
        mHandleFactory.color(l_return[0],'center','sub',transparent = False)
        
        mOffsetShape = cgmMeta.validateObjArg(l_return[0], 'cgmObject',setClass=True)
        mOffsetShape.p_parent = mNoTransformNull
        #mOffsetShape.doSnapTo(self)
        #mc.pointConstraint(self.mNode,mOffsetShape.mNode,maintainOffset=True)        
        #mc.orientConstraint(self.mNode,mOffsetShape.mNode,maintainOffset=True)        
        mOffsetShape.inheritsTransform = False
        
        mOffsetShape.dagLock()
        
        _arg = '{0}.distance = -{1}.controlOffset'.format(l_return[1],
                                                          self.mNode)
        NODEFACTORY.argsToNodes(_arg).doBuild()
        #self.doConnectOut('controlOffset',"{0}.distance".format(l_return[1]))
        
        mOffsetShape.doStore('cgmName', self)
        mOffsetShape.doStore('cgmType','offsetVisualize')
        mOffsetShape.doName()        
        
        self.connectChildNode(mOffsetShape.mNode,'offsetHelper')                
        
        
        
        
        return
        #Offset visualize ==================================================================
        if self.getMessage('offsetHelper'):
            self.offsetHelper.delete()
        
        mShape = self.getShapes(asMeta=True)[0]
        l_return = mc.offsetCurve(mShape.mNode, distance = 1, ch=True )
        #pprint.pprint(l_return)
        mHandleFactory.color(l_return[0],'center','sub',transparent = False)
        
        mOffsetShape = cgmMeta.validateObjArg(l_return[0], 'cgmObject',setClass=True)
        mOffsetShape.p_parent = mFormNull
        
        mOffsetShape.inheritsTransform = False
        mc.parentConstraint(self.mNode,mOffsetShape.mNode,maintainOffset=False)        
        
        #mOffsetShape.setAttrFlags()
        
        _arg = '{0}.distance = -{1}.controlOffset * {1}.blockScale'.format(l_return[1],
                                                                           self.mNode)
        NODEFACTORY.argsToNodes(_arg).doBuild()
        #self.doConnectOut('controlOffset',"{0}.distance".format(l_return[1]))
        
        mOffsetShape.doStore('cgmName', self)
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
        mBBShape.p_parent = mFormNull
        
        SNAPCALLS.snap( mBBShape.mNode,self.mNode,objPivot='axisBox',objMode='y-')
        
        
        CORERIG.copy_pivot(mBBShape.mNode,self.mNode)
        self.doConnectOut('baseSize', "{0}.scale".format(mBBShape.mNode))
        mHandleFactory.color(mBBShape.mNode,controlType='sub')
        mBBShape.setAttrFlags()
        
        mBBShape.doStore('cgmName', self)
        mBBShape.doStore('cgmType','bbVisualize')
        mBBShape.doName()    
        
        self.connectChildNode(mBBShape.mNode,'bbHelper')
        
        
        return True
    
    except Exception,err:
        cgmGEN.cgmExceptCB(Exception,err,localDat=vars())    
    
    
def form(self):
    try:
        _short = self.mNode    
        _str_func = '[{0}] form'.format(_short)
        log.debug("|{0}| >> ".format(_str_func)+ '-'*80)
    
    
        #_average = MATH.average([self.baseSize[0],self.baseSize[2]])
        #_size = _average * 1.5
        #_offsetSize = _average * .1
        #log.info(_size)
        
        #mHandleFactory = self.asHandleFactory(_short)
        mc.select(cl=True)
        resize_masterShape(self)
        
        
        return True
    except Exception,err:
        cgmGEN.cgmExceptCB(Exception,err,localDat=vars())


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

def formDelete(self):
    pass
    #self.setAttrFlags(attrs=['translate','rotate','sx','sz'], lock = False)

def is_form(self):
    if self.getShapes():
        return True
    return False

#=============================================================================================================
#>> Prerig
#=============================================================================================================
def prerig(self):
    try:
        #self.atUtils('puppet_verify')
        self.UTILS.puppet_verify(self)
        
        
        #Create preRig Null  ==================================================================================
        mPrerigNull = self.atBlockUtils('prerigNull_verify')
        mHandleFactory = self.asHandleFactory(self.mNode)
        ml_handles = [self.mNode]
        _offset = self.controlOffset 
        
        #Helpers=====================================================================================
        self.msgList_connect('prerigHandles',[self.mNode])
        
        if self.addMotionJoint:
            _baseSize = self.baseSize
            _sizeHandle = (MATH.average(_baseSize[0],_baseSize[1]) * .1) + _offset
            mMotionJoint = BLOCKSHAPES.rootMotionHelper(self,size=_sizeHandle)
            mMotionJoint.p_parent = mPrerigNull
            
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err,localDat=vars())        

def prerigDelete(self):
    self.atBlockUtils('prerig_delete',formHandles=True)
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
    log.debug(cgmGEN.logString_start(_str_func))

    """
    if not self.mBlock.buildProfile:
        self.l_precheckErrors.append('Must have build profile')
        return False"""
    
    return True

@cgmGEN.Timer
def rig_cleanUp(self):
    try:
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
        #reload(MODULECONTROL)
    
        
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
            
            ml_spacePivots = mMasterControl.msgList_get('spacePivots',asMeta = True)
            for mPivot in ml_spacePivots:
                mDup = mPivot.doDuplicate(po=False)
                mDup.scale = .25,.25,.25
                CORERIG.shapeParent_in_place(mPivot.mNode, mDup.mNode,False,True)
                
            
            ml_dynParents.extend(ml_spacePivots)    
        
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
            
            #ATTR.copy_to(mBlock.moduleTarget.mNode,'cgmName',mControl.mNode,driven='target')
            mControl.doStore('cgmName','rootMotion')
            mControl.doName()
            
            
            #Color ---------------------------------------------------------------
            log.debug("|{0}| >> Motion Joint | Color...".format(_str_func))            
            #_side = mBlock.atBlockUtils('get_side')
            #CORERIG.colorControl(mControl.mNode,_side,'main')        
            
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
            mMasterControl.connectChildNode(mControl,'rootMotionHandle','puppet')#Connect
            
        for mCtrl in ml_controlsAll:            
            if mCtrl.hasAttr('radius'):
                ATTR.set(mCtrl.mNode,'radius',0)        
            
            ml_pivots = mCtrl.msgList_get('spacePivots')
            if ml_pivots:
                log.debug("|{0}| >> Coloring spacePivots for: {1}".format(_str_func,mCtrl))
                for mPivot in ml_pivots:
                    mHandleFactory.color(mPivot.mNode, controlType = 'sub')            
                    ml_controlsAll.append(mPivot)
        
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
        mBlock.noTransFormNull.template=True
        self.UTILS.rigNodes_store(self)
        
        self.version = self.d_block['buildVersion']
        
        mMasterControl.doStore('version', self.d_block['buildVersion'])
        
        #log.info("|{0}| >> Time >> = {1} seconds".format(_str_func, "%0.3f"%(time.clock()-_start)))
        #except Exception,err:cgmGEN.cgmExceptCB(Exception,err)
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err,localDat=vars())        

@cgmGEN.Timer
def rigDelete(self):
    try:
        _str_func = 'rigDelete'
        log.debug("|{0}| >> ...".format(_str_func,)+'-'*80)
        log.debug(self)
        self.template = False
        self.noTransFormNull.template=True
        mPuppet = self.moduleTarget
        mRootMotion = self.moduleTarget.getMessageAsMeta('rootMotionHandle')
        if mRootMotion:
            if mRootMotion.getMessage('dynParentGroup'):mRootMotion.dynParentGroup.doPurge()
            mRootMotion.masterGroup.delete()
        
        
        if self.moduleTarget.masterControl.getMessage('dynParentGroup'):
            self.moduleTarget.masterControl.dynParentGroup.doPurge()
        
        ml_spacePivots = self.moduleTarget.masterControl.msgList_get('spacePivots')
        if ml_spacePivots:
            for mObj in ml_spacePivots:
                log.info("|{0}| >> SpacePivot: {1}".format(_str_func,mObj))  
                for link in ['constraintGroup','constrainGroup','masterGroup']:
                    mGroup = mObj.getMessageAsMeta(link)
                    if mGroup:
                        mGroup.delete()
                        break
                
        if self.moduleTarget.masterControl.getMessage('masterGroup'):
            self.moduleTarget.masterControl.masterGroup.delete()
        
        log.debug("|{0}| >> rigNodes...".format(_str_func,)+'-'*40)                             
        ml_rigNodes = mPuppet.getMessageAsMeta('rigNodes')
        for mNode in ml_rigNodes:
            try:
                log.debug("|{0}| >> deleting: {1}".format(_str_func,mNode))                     
                mNode.delete()
            except:
                log.debug("|{0}| >> failed...".format(_str_func,mNode))         
        
        
        
        return True
        self.v = 1
        try:self.moduleTarget.masterControl.masterGroup.delete()
        except Exception,err:
            cgmGEN.cgmExceptCB(Exception,err,msg=vars())
            raise Exception,err
        return True
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err,localDat=vars())        

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
            mJoint.doStore('cgmName','ignore')            
            #self.copyAttrTo('cgmName',mJoint.mNode,'cgmName',driven='target')
            mJoint.doStore('cgmTypeModifier','rootMotion')
            mJoint.doName()
            
            mJoint.radius = self.controlOffset
            
            
            #self.atBlockUtils('skeleton_connectToParent')
            if self.moduleTarget.masterNull.getMessage('skeletonGroup'):
                mJoint.p_parent = self.moduleTarget.masterNull.skeletonGroup
            return mJoint.mNode
        
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err,localDat=vars())        

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






 








