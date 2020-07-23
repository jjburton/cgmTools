"""
------------------------------------------
cgm.core.mrs.blocks.simple.e
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
import cgm.core.mrs.lib.ModuleControlFactory as MODULECONTROL
import cgm.core.classes.NodeFactory as NODEFACTORY
import cgm.core.mrs.lib.blockShapes_utils as BLOCKSHAPES
import cgm.core.lib.distance_utils as DIST
import cgm.core.lib.rigging_utils as CORERIG
import cgm.core.lib.math_utils as MATH
import cgm.core.lib.list_utils as LISTS
import cgm.core.cgm_RigMeta as cgmRIGMETA
from cgm.core.cgmPy import validateArgs as VALID
from cgm.core.lib import euclid as EUCLID
from cgm.core.lib import locator_utils as LOC

# From cgm ==============================================================
from cgm.core import cgm_Meta as cgmMeta

#=============================================================================================================
#>> Block Settings
#=============================================================================================================
__version__ = '1.04302019'
__MAYALOCAL = 'EYEMAIN'

__autoForm__ = True
__menuVisible__ = True
__baseSize__ = 10,10,10


#>>>Profiles =====================================================================================================
d_build_profiles = {'unityLow':{},
                    'unityMed':{},
                    'feature':{}}

#>>>Attrs =======================================================================================================
l_attrsStandard = ['side',
                   'position',
                   'attachPoint',
                   'attachIndex',
                   'buildSDK',
                   'buildSDK',
                   'numSpacePivots',
                   'blockProfile',
                   'visLabels',
                   'visMeasure',
                   'visProximityMode',
                   'moduleTarget']

d_attrsToMake = {}

d_defaultSettings = {'version':__version__,
                     'baseName':'eyeMain',
                     'numSpacePivots':0,
                     'attachPoint':'end'}

d_wiring_prerig = {'msgLinks':['moduleTarget']}
d_wiring_form = {'msgLinks':[]}

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

    
    #mc.menuItem(ann = '[{0}] Recreate the base shape and push values to baseSize attr'.format(_short),
    #            c = cgmGEN.Callback(resize_masterShape,self,**{'resize':1}),
    #            label = "Resize")            
    
#=============================================================================================================
#>> Define
#=============================================================================================================
def define(self):
    _short = self.mNode
    _str_func = '[{0}] define'.format(_short)
    
    ATTR.set_alias(_short,'sy','blockScale')    
    self.setAttrFlags(attrs=['sx','sz','sz'])
    self.doConnectOut('sy',['sx','sz'])
    ATTR.set_hidden(_short, 'baseSize', True)
    
    _shapes = self.getShapes()
    if _shapes:
        log.debug("|{0}| >>  Removing old shapes...".format(_str_func))        
        mc.delete(_shapes)

    _size = self.atUtils('defineSize_get')

    #_sizeSub = _size / 2.0
    log.debug("|{0}| >>  Size: {1}".format(_str_func,_size))        
    _crv = CURVES.create_fromName(name='locatorForm',
                                  direction = 'z+', size = _size * 2.0)

    SNAP.go(_crv,self.mNode)
    CORERIG.override_color(_crv, 'white')
    CORERIG.shapeParent_in_place(self.mNode,_crv,False)
    mHandleFactory = self.asHandleFactory()
    self.addAttr('cgmColorLock',True,lock=True,hidden=True)    
    
    if self.cgmName == 'default':
        self.cgmName = 'eyeLook'
        self.doName()
    #try:mc.delete(self.getShapes())
    #except:pass

    
#=============================================================================================================
#>> Form
#=============================================================================================================
def rebuild_controlShape(self):
    _short = self.mNode
    _str_func = '[{0}] rebuild_controlShape'.format(_short)
    
    if not self.atUtils('is_rigged'):
        log.warning(cgmGEN.logString_msg(_str_func,"Must be rigged"))
        return False
    
    bb_sizeBase = TRANS.bbSize_get(self.mNode,True)
    pprint.pprint(bb_sizeBase)
    


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
    pass

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
    #Create preRig Null  ==================================================================================
    mPrerigNull = self.atBlockUtils('prerigNull_verify')
    mHandleFactory = self.asHandleFactory(self.mNode)
    
    self.atBlockUtils('module_verify')

            

def prerigDelete(self):
    #self.atBlockUtils('prerig_delete',formHandles=True)
    #try:self.moduleTarget.masterNull.delete()
    #except Exception,err:
    #    for a in err:
    #        print a
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
        
        #DynParents =============================================================================
        self.UTILS.get_dynParentTargetsDat(self)
        log.debug(cgmGEN._str_subLine)
            
        mModule = self.mModule
        mRigNull = self.mRigNull
        mPuppet = self.mPuppet
        mHandleFactory = mBlock.asHandleFactory()
        
        """
        _eyeLook = eyeLook_get(self)
        
        if _eyeLook:
            log.debug("|{0}| >> Found existing eyeLook...".format(_str_func))                      
            return _eyeLook
        
        if mBlock.blockType not in ['eye']:
            raise ValueError,"blocktype must be eye. Found {0} | {1}".format(mBlock.blockType,mBlock)
        """
        
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
        mCrv.doSnapTo(mBlock.mNode,rotation=False)
        pos = mBlock.p_position
        
        mCrv.p_position = pos
        
        
        mBlockParent = mBlock.p_blockParent
        if mBlockParent:
            _parentName = mBlockParent.getMayaAttr('cgmName') or mBlockParent.p_nameShort
            mCrv.doStore('cgmName',_parentName + '_eyeLook')
            mBlockParent.asHandleFactory().color(mCrv.mNode)
        else:
            mCrv.doStore('cgmName','eyeLook')
            mHandleFactory.color(mCrv.mNode)
        
        mCrv.doName()
        

        #Register control... -----------------------------------------------------------------------        
        log.debug("|{0}| >> Registering Control... ".format(_str_func))
        d_controlSpaces = self.atBuilderUtils('get_controlSpaceSetupDict')
        
        d_buffer = MODULECONTROL.register(mCrv,
                                          mirrorSide= 'center',
                                          mirrorAxis="translateX,rotateY,rotateZ",
                                          **d_controlSpaces)
        
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
                #mRigNull.faceSet.append(mCrv)
                
                #mCrv.connectParentNode(mBlockParentRigNull,'rigNull')
                
            else:
                mModuleParent.puppetSet.append(mCrv)
                mModuleParent.msgList_append('controlsAll',mCrv)
                #mModuleParent.faceSet.append(mCrv)
                

        #Connections... -----------------------------------------------------------------------        
        log.debug("|{0}| >> Heirarchy... ".format(_str_func))
        mCrv.masterGroup.p_parent = self.mDeformNull
        
        for link in 'masterGroup','dynParentGroup':
            if mCrv.getMessage(link):
                mCrv.getMessageAsMeta(link).dagLock(True)
                
        mCrv.addAttr('cgmControlDat','','string')
        mCrv.cgmControlDat = {'tags':['ik']}                
        
        
        
        
        mBlock.template = True
        return True
    

    
       
    
    
        try:#moduleParent Stuff =======================================================
            if mi_moduleParent:
                try:
                    for mCtrl in self.ml_controlsAll:
                        mi_parentRigNull.msgList_append('controlsAll',mCtrl)
                except Exception,error: raise Exception,"!Controls all connect!| %s"%error	    
                try:mi_parentRigNull.moduleSet.extend(self.ml_controlsAll)
                except Exception,error: raise Exception,"!Failed to set module objectSet! | %s"%error
        except Exception,error:raise Exception,"!Module Parent registration! | %s"%(error)	            
        
        return
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
         
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
        
        self.moduleTarget.eyeLook.masterGroup.delete()
        
        return True
    
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
    return True
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
    return True
def skeleton_delete(self):
    #    
    return True

def skeleton_check(self):
    return True


__l_rigBuildOrder__ = ['rig_cleanUp']


def get_planeIntersect(self, target = None, planeAxis = 'z+', objAxis = 'z+', mark = True):
    _short = self.mNode
    _str_func = '[{0}] get_planeIntersect'.format(_short)
    
    if target:
        mTarget = cgmMeta.asMeta(target)
    else:
        mTarget = cgmMeta.asMeta(mc.ls(sl=1))
        if not mTarget:
            return log.error(cgmGEN.logString_msg( _str_func, 'No Target'))
        mTarget = mTarget[0]
    
    if not self.atUtils('is_rigged'):
        mObj = self
    else:
        mObj = self.moduleTarget.eyeLook
        
    planePoint = VALID.euclidVector3Arg(mObj.p_position)
    planeNormal = VALID.euclidVector3Arg(mObj.getAxisVector(planeAxis))

    
    rayPoint = VALID.euclidVector3Arg(mTarget.p_position)
    rayDirection = VALID.euclidVector3Arg(mTarget.getAxisVector(objAxis))
    
    plane = EUCLID.Plane( EUCLID.Point3(planePoint.x, planePoint.y, planePoint.z),
                          EUCLID.Point3(planeNormal.x, planeNormal.y, planeNormal.z) )
    pos = plane.intersect( EUCLID.Line3( EUCLID.Point3(rayPoint.x, rayPoint.y, rayPoint.z), EUCLID.Vector3(rayDirection.x, rayDirection.y, rayDirection.z) ) )
    
    if mark:
        LOC.create(position = pos, name = 'pewpew')
        
    return pos
    







 








