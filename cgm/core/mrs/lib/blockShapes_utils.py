"""
------------------------------------------
cgm.core.mrs.blocks.organic.limb
Author: Josh Burton
email: cgmonks.info@gmail.com

Website : https://github.com/jjburton/cgmTools/wiki
------------------------------------------

================================================================
"""
__MAYALOCAL = 'BLOCKSHAPES'

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
log.setLevel(logging.INFO)

# From Maya =============================================================
import maya.cmds as mc
import maya.mel as mel    

# From Red9 =============================================================
#from Red9.core import Red9_Meta as r9Meta
import cgm.core.cgm_General as cgmGEN
#from cgm.core.rigger import ModuleShapeCaster as mShapeCast
#import cgm.core.cgmPy.os_Utils as cgmOS
#import cgm.core.cgmPy.path_Utils as cgmPATH
#import cgm.core.mrs.lib.ModuleControlFactory as MODULECONTROL
#import cgm.core.rig.general_utils as CORERIGGEN
import cgm.core.lib.math_utils as MATH
import cgm.core.lib.transform_utils as TRANS
import cgm.core.lib.distance_utils as DIST
import cgm.core.lib.attribute_utils as ATTR
import cgm.core.tools.lib.snap_calls as SNAPCALLS
#import cgm.core.classes.NodeFactory as NODEFACTORY
#from cgm.core import cgm_RigMeta as cgmRigMeta
#import cgm.core.lib.list_utils as LISTS
#import cgm.core.lib.nameTools as NAMETOOLS
#import cgm.core.lib.locator_utils as LOC
#import cgm.core.rig.create_utils as RIGCREATE
import cgm.core.lib.snap_utils as SNAP
import cgm.core.lib.rayCaster as RAYS
import cgm.core.lib.rigging_utils as CORERIG
import cgm.core.lib.curve_Utils as CURVES
import cgm.core.rig.constraint_utils as RIGCONSTRAINT
#import cgm.core.lib.constraint_utils as CONSTRAINT
import cgm.core.lib.position_utils as POS
#import cgm.core.rig.joint_utils as JOINT
#import cgm.core.rig.ik_utils as IK
#import cgm.core.mrs.lib.block_utils as BLOCKUTILS
#import cgm.core.mrs.lib.shared_dat as BLOCKSHARE
#import cgm.core.mrs.lib.builder_utils as BUILDUTILS
#import cgm.core.lib.shapeCaster as SHAPECASTER
import cgm.core.rig.general_utils as RIGGEN
import cgm.core.lib.string_utils as STR

#reload(SHAPECASTER)
from cgm.core.cgmPy import validateArgs as VALID
#import cgm.core.cgm_RigMeta as cgmRIGMETA


# From cgm ==============================================================
from cgm.core import cgm_Meta as cgmMeta

#=============================================================================================================
#>> Block Settings
#=============================================================================================================
__version__ = 'alpha.1.09122018'
def log_start(str_func):
    log.debug("|{0}| >> ...".format(str_func)+'/'*60)

#@cgmGEN.Timer
def color(self, target = None, side = None, controlType = None, transparent = None,shaderOnly =True):
    _str_func = 'color'
    log.debug("|{0}| >> ".format(_str_func)+ '-'*80)
    _targets = VALID.mNodeStringList(target)
    log.debug("|{0}| >> target: [{1}]".format(_str_func, _targets))
    
    if side is None:
        _side = self.atUtils('get_side')
    else:
        log.debug("|{0}| >> arg side: {1}".format(_str_func, side))            
        _side = side
        
    if transparent is None:
        _transparent = True
    else:
        log.debug("|{0}| >> arg transparent: {1}".format(_str_func, transparent))            
        _transparent = transparent
            
    if controlType is None:
        _controlType = 'main'        
    else:
        log.debug("|{0}| >> arg controlType: {1}".format(_str_func, controlType))                        
        _controlType = controlType
    
    for t in _targets:
        if t is None:
            t = self.mNode
            
        if ATTR.get(t,'cgmColorLock'):
            log.info("|{0}| >> No recolor flag! {1}".format(_str_func,t))                        
            continue
        
        if VALID.get_mayaType(t) == 'joint':
            CORERIG.colorControl(t,_side,_controlType,transparent = _transparent)
            
        else:
            if VALID.is_shape(t):
                log.debug("|{0}| >> is shape: {1}".format(_str_func, t))                
                _shapes = [t]
            else:
                _shapes = TRANS.shapes_get(t,True)
            
            for s in _shapes:
                log.debug("|{0}| >> s: {1}".format(_str_func, s))
                _useType = _controlType
                _type = VALID.get_mayaType(s)
                if controlType is not None:
                    log.debug("|{0}| >> Setting controlType: {1}".format(_str_func, controlType))                                            
                    ATTR.store_info(s,'cgmControlType',controlType)
                    
                if transparent is not None and _type in ['mesh','nurbsSurface']:
                    log.debug("|{0}| >> Setting transparent: {1}".format(_str_func, transparent))                                                                
                    ATTR.store_info(s,'cgmControlTransparent',transparent)
                    
                if ATTR.has_attr(s,'cgmControlType'):
                    _useType = ATTR.get(s,'cgmControlType')
                    log.debug("|{0}| >> Shape has cgmControlType tag: {1}".format(_str_func,_useType))                
                log.debug("|{0}| >> s: {1} | side: {2} | controlType: {3}".format(_str_func, s, _side, _useType))            
                    
                if _type in ['mesh','nurbsSurface']:
                    CORERIG.colorControl(s,_side,_useType,transparent = _transparent, shaderOnly = shaderOnly)
                else:
                    CORERIG.colorControl(s,_side,_useType,transparent = _transparent,shaderOnly=False)
                    
    

class handleFactory(object):
    _l_controlLinks = []
    _l_controlmsgLists = []	

    def __init__(self, node = None, rigBlock = None,baseShape = 'square',  baseSize = 1, side = None,
                 shapeDirection = 'z+', aimDirection = 'z+', upDirection = 'y+', *a,**kws):
        """
        :returns
            factory instance
        """
        _str_func = 'handleFactory._init_'

        if a:log.debug("|{0}| >> a: {1}".format(_str_func,a))
        if kws:
            self._call_kws = kws
            cgmGEN.walk_dat(kws,_str_func)
            #log.debug("|{0}| >> kws: {1}".format(_str_func,kws))
        
        self.mBlock = None
        self._mTransform = None
        self._baseShape = baseShape
        self._baseSize = baseSize
        self._side = side
        self._mTemp = None

        if node is not None:
            self.setHandle(node)
        if rigBlock is not None:
            self.setRigBlock(rigBlock)
            #self.setHandle(rigBlock)
            
    def __repr__(self):
        try:return "{0}(root: {1} | mBlock: {2})".format(self.__class__, self._mTransform, self.mBlock)
        except:return self
        
    def setHandle(self,arg = None):
        #if not VALID.is_transform(arg):
            #raise ValueError,"must be a transform"

        self._mTransform = cgmMeta.validateObjArg(arg,'cgmObject')
        #if not self._mTransform.hasAttr('baseSize'):
            #ATTR.add(self._mTransform.mNode,'baseSize','float3')
            #self._mTransform.baseSize = 1.0,1.0,1.0
            #ATTR.set_hidden(self._mTransform.mNode,'baseSize',False)
            
    def setRigBlock(self,arg = None):
        mBlock = cgmMeta.validateObjArg(arg)
        if mBlock.mClass != 'cgmRigBlock':
            raise ValueError("Not a rigBlock: {0}".format(arg))
        self.mBlock = mBlock

                #ATTR.set_hidden(self._mTransform.mNode,'baseSize',False)
    
    def rebuildSimple(self, baseShape = None, baseSize = None, shapeDirection = 'z+'):
        self.cleanShapes()

        if baseShape is None:
            baseShape = 'square'

        self._mTransform.addAttr('baseShape', baseShape,attrType='string')

        SNAP.verify_aimAttrs(self._mTransform.mNode, aim = 'z+', up = 'y+')

        if baseSize is not None:
            _baseSize = baseSize or 1.0
            #self._mTransform.baseSize = baseSize

        _baseSize = self.mBlock.baseSize

        _baseShape = self._mTransform.getMayaAttr('baseShape') 
        mCrv = self.buildBaseShape(_baseShape,_baseSize,shapeDirection)
        CORERIG.shapeParent_in_place(self._mTransform.mNode,mCrv.mNode,False)

        # CURVES.create_fromName('square', color = 'yellow', direction = 'y+', sizeMode = 'fixed', size = _size * .5)

        #self.color()

        #if not self._mTransform.hasAttr('cgmName'):
            #self._mTransform.doStore('cgmName',baseShape)

        self._mTransform.doStore('cgmType','blockHandle')
        self._mTransform.doName()
        return True

    def verify(self, baseShape = None, baseSize = None, shapeDirection = 'z+'):
        SNAP.verify_aimAttrs(self._mTransform.mNode, aim = 'z+', up = 'y+')
        return True

    def cleanShapes(self):
        if self._mTransform.getShapes():
            mc.delete(self._mTransform.getShapes())     

        for link in ['loftCurve']:
            _buffer = self._mTransform.getMessage(link)
            if _buffer:
                mc.delete(_buffer)


    def getBaseCreateSize(self):
        _maxLossy = max(self._mTransform.getScaleLossy())
        _baseSize = self.mBlock.baseSize * _maxLossy    
        return _baseSize

    def copyBlockNameTags(self, target = None, name = True, direction = True, position = True):
        _str_func = 'handleFactory.copyBlockNameTags'
        log.info("|{0}| >> ".format(_str_func)+ '-'*80)
        
        if not self.mBlock:
            raise ValueError("Must have rigBlock loaded")
        mBlock = self.mBlock
        
        #_targets = VALID.listArg(target)
        ml_targets = cgmMeta.validateObjListArg(target)
        log.info("|{0}| >> target: [{1}]".format(_str_func, ml_targets))
    
        for mTar in ml_targets:
            t = mTar.mNode
            if name and mBlock.getMayaAttr('cgmName') and not mTar.getMayaAttr('cgmName') :
                ATTR.copy_to(mBlock.mNode,'cgmName',t,driven='target')
            if position and mBlock.getMayaAttr('cgmPosition') and not mTar.getMayaAttr('cgmPosition'):
                ATTR.copy_to(mBlock.mNode,'cgmPosition',t,driven='target')
            if not mTar.getMayaAttr('cgmDirection'):
                if direction and mBlock.getMayaAttr('cgmDirection'):
                    ATTR.copy_to(mBlock.mNode,'cgmDirection',t,driven='target')
                elif mBlock.side:
                    mTar.doStore('cgmDirection',self.get_side())
            mTar.doName()
            
                
    def color(self, target = None, side = None, controlType = None, transparent = None,shaderOnly =True):
        _str_func = 'handleFactory.color'
        log.debug("|{0}| >> ".format(_str_func)+ '-'*80)
        _targets = VALID.listArg(target)
        log.debug("|{0}| >> target: [{1}]".format(_str_func, _targets))
        
        mTransform = self._mTransform
        if side is None:
            _side = self.get_side()
        else:
            log.debug("|{0}| >> arg side: {1}".format(_str_func, side))            
            _side = side
            
        if transparent is None:
            _transparent = True
        else:
            log.debug("|{0}| >> arg transparent: {1}".format(_str_func, transparent))            
            _transparent = transparent
                
        if controlType is None:
            _controlType = 'main'        
        else:
            log.debug("|{0}| >> arg controlType: {1}".format(_str_func, controlType))                        
            _controlType = controlType
        
        for t in _targets:
            if t is None:
                t = self._mTransform.mNode
                
            if ATTR.get(t,'cgmColorLock'):
                log.info("|{0}| >> No recolor flag! {1}".format(_str_func,t))                        
                continue
            
            if VALID.get_mayaType(t) == 'joint':
                CORERIG.colorControl(t,_side,_controlType,transparent = _transparent)
                
            else:
                if VALID.is_shape(t):
                    log.debug("|{0}| >> is shape: {1}".format(_str_func, t))                
                    _shapes = [t]
                else:
                    _shapes = TRANS.shapes_get(t,True)
                
                for s in _shapes:
                    log.debug("|{0}| >> s: {1}".format(_str_func, s))
                    _useType = _controlType
                    _type = VALID.get_mayaType(s)
                    if controlType is not None:
                        log.debug("|{0}| >> Setting controlType: {1}".format(_str_func, controlType))                                            
                        ATTR.store_info(s,'cgmControlType',controlType)
                        
                    if transparent is not None and _type in ['mesh','nurbsSurface']:
                        log.debug("|{0}| >> Setting transparent: {1}".format(_str_func, transparent))                                                                
                        ATTR.store_info(s,'cgmControlTransparent',transparent)
                        
                    if ATTR.has_attr(s,'cgmControlType'):
                        _useType = ATTR.get(s,'cgmControlType')
                        log.debug("|{0}| >> Shape has cgmControlType tag: {1}".format(_str_func,_useType))                
                    log.debug("|{0}| >> s: {1} | side: {2} | controlType: {3}".format(_str_func, s, _side, _useType))            
                        
                    if _type in ['mesh','nurbsSurface']:
                        CORERIG.colorControl(s,_side,_useType,transparent = _transparent, shaderOnly = shaderOnly)
                    else:
                        CORERIG.colorControl(s,_side,_useType,transparent = _transparent,shaderOnly=False)
                        


    def get_baseDat(self, baseShape = None, baseSize = None, shapeDirection = None):
        _str_func = 'get_baseDat'

        
        if not self._mTransform or self._mTransform.mNode is None:
            if baseShape:
                name=baseShape
            else:
                name='handleFactory_shape'
            self._mTransform = cgmMeta.createMetaNode('cgmObject', name = name, nodeType = 'transform')
            log.error("|{0}| >> Must have an handle loaded. One Generated".format(_str_func))
            self._mTemp = self._mTransform
        
        
        if baseShape:
            _baseShape = baseShape
        elif self._mTransform and self._mTransform.hasAttr('baseShape'):
            _baseShape = self._mTransform.baseShape
        else:
            _baseShape = 'square'
            
        if baseSize is not None:
            _baseSize = get_sizeVector(baseSize)
        elif self._mTransform.getShapes():
            _baseSize = POS.get_axisBox_size(self._mTransform.mNode,False)
        elif self.mBlock and self.mBlock.hasAttr('baseSize'):
            _baseSize = self.mBlock.baseSize
        elif self._mTransform and self._mTransform.hasAttr('baseSize'):
            _baseSize = self._mTransform.baseSize
        else:
            _baseSize = [1.0,1.0,1.0]

        return [_baseShape,_baseSize]

    def get_axisBox_size(self,targets = None, maxDistance = 10000000):
        """
        Putting this here till I can refactor it out of SNAPCALLS as I don't want it there permenantly
        """
        return SNAPCALLS.get_axisBox_size(targets,maxDistance)

    def buildBaseShape(self, baseShape = None, baseSize = None, shapeDirection = 'z+' ):
        _baseDat = self.get_baseDat(baseShape,baseSize)
        _baseShape = _baseDat[0]
        _baseSize = _baseDat[1]

        if baseSize is None and _baseShape not in ['sphere','sphere2','cube','locatorForm']:
            _baseSize = [_baseSize[0],_baseSize[1],None]

        if baseShape == 'self':
            _crv = mc.duplicate( self._mTransform.getShapes()[0])[0]
        else:
            _crv = CURVES.create_fromName(_baseShape, _baseSize, shapeDirection, baseSize=1.0)
            TRANS.snap(_crv, self._mTransform.mNode) 
            
        mCrv = cgmMeta.validateObjArg(_crv,'cgmObject',setClass=True)

        #...lossy
        _lossy = self._mTransform.getScaleLossy()
        mCrv.scaleX = mCrv.scaleX * _lossy[0]
        mCrv.scaleY = mCrv.scaleY * _lossy[1]
        mCrv.scaleZ = mCrv.scaleZ * _lossy[2]
        
        if self._mTemp:
            self._mTemp.delete()
            self._mTemp = None
        return mCrv

    def get_side(self):
        if self.mBlock:
            return self.mBlock.atUtils('get_side')
        if self._side:
            return self._side
        _side = 'center'
        mHandle = self._mTransform        
        if mHandle.getMayaAttr('side'):
            _side = mHandle.getEnumValueString('side')
        return _side

    def addPivotSetupHelper(self,baseShape=None, baseSize = None, upAxis = 'y+', setAttrs = {}):
        try:
            _str_func = 'addPivotSetupHelper'
            mHandle = self._mTransform
            _short = mHandle.mNode
            _side = self.get_side()

            _baseDat = self.get_baseDat(baseShape,baseSize)
            _baseShape = _baseDat[0]
            _baseSize = _baseDat[1]

            _bbsize = POS.get_axisBox_size(mHandle.mNode,False)
            _size = MATH.average(_bbsize)
            _sizeSub = _size * .2

            _bfr = mHandle.getMessage('scalePivotHelper')
            if _bfr:
                mc.delete(_bfr)


            ml_pivots = []
            mPivotRootHandle = False
            self_pos = mHandle.p_position
            self_upVector = mHandle.getAxisVector(upAxis)

            d_pivotDirections = {'back':'z-',
                                 'front':'z+',
                                 'left':'x+',
                                 'right':'x-'}        
            _axisBox = False
            
            _baseShape = 'loft' + _baseShape[0].capitalize() + ''.join(_baseShape[1:])

            for a in ['pivotBack','pivotFront','pivotLeft','pivotRight','pivotCenter']:
                _strPivot = a.split('pivot')[-1]
                _strPivot = _strPivot[0].lower() + _strPivot[1:]
                log.info("|{0}| >> Adding pivot helper: {1}".format(_str_func,_strPivot))
                if _strPivot == 'center':
                    pivot = CURVES.create_controlCurve(mHandle.mNode, shape='circle',
                                                       direction = upAxis,
                                                       sizeMode = 'fixed',
                                                       bakeScale = False,
                                                       size = _sizeSub)
                    mPivot = cgmMeta.validateObjArg(pivot,'cgmObject',setClass=True)
                    mPivot.addAttr('cgmName',_strPivot)
                    ml_pivots.append(mPivot)
                else:
                    if not _axisBox:
                        _axisBox = CORERIG.create_proxyGeo('cube',_baseSize,ch=False)[0]
                        SNAP.go(_axisBox,self._mTransform.mNode)

                    mAxis = VALID.simpleAxis(d_pivotDirections[_strPivot])
                    _inverse = mAxis.inverse.p_string
                    pivot = CURVES.create_controlCurve(mHandle.mNode, shape='hinge',
                                                       direction = _inverse,
                                                       bakeScale = False,
                                                       sizeMode = 'fixed', size = _sizeSub)
                    mPivot = cgmMeta.validateObjArg(pivot,'cgmObject',setClass=True)
                    mPivot.addAttr('cgmName',_strPivot)
                    
                    #mPivot.p_position = DIST.get_pos_by_axis_dist(_short,mAxis.p_string, _size/2)
                    SNAPCALLS.snap(mPivot.mNode,_axisBox,rotation=False,targetPivot='castNear',targetMode=mAxis.p_string)

                    SNAP.aim_atPoint(mPivot.mNode,self_pos, _inverse, upAxis, mode='vector', vectorUp = self_upVector)

                    ml_pivots.append(mPivot)

                    if not mPivotRootHandle:
                        pivotHandle = CURVES.create_controlCurve(mHandle.mNode, shape=_baseShape,
                                                                 direction = upAxis,
                                                                 bakeScale = False,
                                                                 sizeMode = 'fixed', size = _size * 1.1)
                        mPivotRootHandle = cgmMeta.validateObjArg(pivotHandle,'cgmObject',setClass=True)
                        mPivotRootHandle.addAttr('cgmName','base')
                        mPivotRootHandle.addAttr('cgmType','pivotHelper')            
                        mPivotRootHandle.doName()

                        #CORERIG.colorControl(mPivotRootHandle.mNode,_side,'sub') 
                        self.color(mPivotRootHandle.mNode,_side,'sub')

                        #mPivotRootHandle.parent = mPrerigNull
                        mHandle.connectChildNode(mPivotRootHandle,'pivotHelper','block')#Connect    

                        if mHandle.hasAttr('addPivot'):
                            mHandle.doConnectOut('addPivot',"{0}.v".format(mPivotRootHandle.mNode))
                        self.mBlock.msgList_append('prerigHandles',mPivotRootHandle)

            if _axisBox:
                mc.delete(_axisBox)
            for mPivot in ml_pivots:
                mPivot.addAttr('cgmType','pivotHelper')            
                mPivot.doName()

                #CORERIG.colorControl(mPivot.mNode,_side,'sub') 
                self.color(mPivot.mNode,_side,'sub')
                
                mPivot.parent = mPivotRootHandle
                mPivotRootHandle.connectChildNode(mPivot,'pivot'+ mPivot.cgmName.capitalize(),'handle')#Connect    
                self.mBlock.msgList_append('prerigHandles',mPivot)

            if self._mTransform.getShapes():
                SNAPCALLS.snap(mPivotRootHandle.mNode,self._mTransform.mNode,rotation=False,targetPivot='axisBox',targetMode='y-')

            return mPivotRootHandle
        except Exception as err:
            cgmGEN.cgmExceptCB(Exception,err,msg=vars())
            
    def addFootHelper(self,baseShape=None, baseSize = None, upAxis = 'y+', setAttrs = {}):
            try:
                _str_func = 'addPivotSetupHelper'
                mHandle = self._mTransform
                _short = mHandle.mNode
                _side = self.get_side()
    
                _baseDat = self.get_baseDat(baseShape,baseSize)
                _baseShape = _baseDat[0]
                _baseSize = _baseDat[1]
    
                _bbsize = POS.get_axisBox_size(mHandle.mNode,False)
                _size = MATH.average(_bbsize)
                _sizeSub = _size * .2
    
                _bfr = mHandle.getMessage('scalePivotHelper')
                if _bfr:
                    mc.delete(_bfr)
    
    
                ml_pivots = []
                mPivotRootHandle = False
                self_pos = mHandle.p_position
                self_upVector = mHandle.getAxisVector(upAxis)
    
                d_pivotDirections = {'back':'z-',
                                     'front':'z+',
                                     'left':'x+',
                                     'right':'x-'}
                _axisBox = False
                
                d_altName = {'back':'heel',
                             'front':'toe',
                             'center':'ball'}
    
                mAxis = VALID.simpleAxis(d_pivotDirections['front'])
                #p_ballPush = DIST.get_pos_by_vec_dist(self_pos, mAxis.p_vector,_size/8 )
                
                _baseShape = 'loft' + _baseShape[0].capitalize() + ''.join(_baseShape[1:])
                #Main Handle -----------------------------------------------------------------------------
                pivotHandle = CURVES.create_controlCurve(mHandle.mNode,
                                                         shape=_baseShape,
                                                         direction = 'y-',
                                                         bakeScale = False,
                                                         sizeMode = 'fixed',
                                                         size = _size)
                mPivotRootHandle = cgmMeta.validateObjArg(pivotHandle,'cgmObject',setClass=True)
                mPivotRootHandle.addAttr('cgmName','base')
                mPivotRootHandle.addAttr('cgmType','pivotHelper')            
                mPivotRootHandle.doName()
            
                mPivotRootHandle.p_position = self_pos
                #CORERIG.colorControl(mPivotRootHandle.mNode,_side,'sub') 
                self.color(mPivotRootHandle.mNode,_side,'sub')
            
                #mPivotRootHandle.parent = mPrerigNull
                mHandle.connectChildNode(mPivotRootHandle,'pivotHelper','block')#Connect    
            
                if mHandle.hasAttr('addPivot'):
                    mHandle.doConnectOut('addPivot',"{0}.v".format(mPivotRootHandle.mNode))
            
                self.mBlock.msgList_append('prerigHandles',mPivotRootHandle)
            
                #Top loft ----------------------------------------------------------------
                mTopLoft = mPivotRootHandle.doDuplicate(po=False)
                mTopLoft.addAttr('cgmName','topLoft')
                mTopLoft.addAttr('cgmType','pivotHelper')            
                mTopLoft.doName()
            
                mTopLoft.parent = mPivotRootHandle
            
                

                
                if not _axisBox:
                    _axisBox = CORERIG.create_proxyGeo('cube',_baseSize,ch=False)[0]
                    SNAP.go(_axisBox,self._mTransform.mNode)
                    #_axisBox = CORERIG.create_axisProxy(self._mTransform.mNode)
                    
                #Sub pivots =============================================================================
                for a in ['pivotBack','pivotFront','pivotLeft','pivotRight','pivotCenter']:
                    _strPivot = a.split('pivot')[-1]
                    _strPivot = _strPivot[0].lower() + _strPivot[1:]
                    _strName = d_altName.get(_strPivot,_strPivot)
                    log.info("|{0}| >> Adding pivot helper: {1}".format(_str_func,_strPivot))
                    if _strPivot == 'center':
                        pivot = CURVES.create_controlCurve(mHandle.mNode, shape='circle',
                                                           direction = upAxis,
                                                           bakeScale = False,
                                                           sizeMode = 'fixed',
                                                           size = _sizeSub)
                        mPivot = cgmMeta.validateObjArg(pivot,'cgmObject',setClass=True)
                        mPivot.addAttr('cgmName',_strName)
                        ml_pivots.append(mPivot)
                        mPivot.p_parent = mPivotRootHandle
                        
                        mPivotRootHandle.connectChildNode(mPivot, a ,'handle')#Connect    
                        
                        #mPivot.p_position = p_ballPush
                    else:

    
                        mAxis = VALID.simpleAxis(d_pivotDirections[_strPivot])
                        _inverse = mAxis.inverse.p_string
                        pivot = CURVES.create_controlCurve(mHandle.mNode, shape='hinge',
                                                           direction = _inverse,
                                                           bakeScale = False,
                                                           sizeMode = 'fixed', size = _sizeSub)
                        mPivot = cgmMeta.validateObjArg(pivot,'cgmObject',setClass=True)
                        mPivot.addAttr('cgmName',_strName)
                        mPivot.p_parent = mPivotRootHandle
                        
                        mPivotRootHandle.connectChildNode(mPivot, a ,'handle')#Connect    
    
                        #mPivot.p_position = DIST.get_pos_by_axis_dist(_short,mAxis.p_string, _size/2)
                        SNAPCALLS.snap(mPivot.mNode,_axisBox,rotation=False,targetPivot='castNear',targetMode=mAxis.p_string)
                        #SNAPCALLS.get_special_pos()
                        #mPivot.p_position = #SNAPCALLS.get_special_pos(mPivotRootHandle.p_nameLong,'axisBox',mAxis.p_string,True)
                        SNAP.aim_atPoint(mPivot.mNode,self_pos, _inverse, upAxis, mode='vector', vectorUp = self_upVector)
    
                        ml_pivots.append(mPivot)
                        
                        #if _strPivot in ['left','right']:
                            #mPivot.p_position = p_ballPush
                            #mPivot.tz = .75
                                
                #Clean up Pivot root after all else --------------------------------------------------
                #mAxis = VALID.simpleAxis(d_pivotDirections['back'])
                #p_Base = DIST.get_pos_by_axis_dist(mPivotRootHandle.mNode,
                #                                   d_pivotDirections['back'],
                #                                   _size/4 )
                
                #mc.xform (mPivotRootHandle.mNode,  ws=True, sp= p_Base, rp=p_Base, p=True)
                
                for mPivot in ml_pivots:#Unparent for loft
                    mPivot.p_parent = False
                    
                if self._mTransform.getMessage('loftCurve'):
                    log.info("|{0}| >> LoftSetup...".format(_str_func))
                    
                    #Fix the aim on the foot
                    mTopLoft.parent = False
                    
                    l_footTargets = [self._mTransform.loftCurve.mNode, mTopLoft.mNode,mPivotRootHandle.mNode]
                    
                    _res_body = mc.loft(l_footTargets, o = True, d = 3, po = 0,reverseSurfaceNormals=True)
                    
                    mTopLoft.parent = mPivotRootHandle
                    
                    _loftNode = _res_body[1]
                    mLoftSurface = cgmMeta.validateObjArg(_res_body[0],'cgmObject',setClass= True)        
                        
                        
                    mLoftSurface.overrideEnabled = 1
                    mLoftSurface.overrideDisplayType = 2
                    #...this used to be {1} + 1. may need to revisit for head/neck
                    
                    mLoftSurface.parent = self.mBlock.formNull

                    #mLoft.p_parent = mFormNull
                    mLoftSurface.resetAttrs()
                    
                    ATTR.set(_loftNode,'degree',1)    
                
                    mLoftSurface.doStore('cgmName',self.mBlock)
                    mLoftSurface.doStore('cgmType','footApprox')
                    mLoftSurface.doName()
                
                
                
                    #mc.polySetToFaceNormal(mLoft.mNode,setUserNormal = True)
                    #polyNormal -normalMode 0 -userNormalMode 1 -ch 1 spine_block_controlsApproxShape;
                
                    #mc.polyNormal(mLoft.mNode, normalMode = 0, userNormalMode = 1, ch=1)
                
                    #Color our stuff...
                    self.color(mLoftSurface.mNode,transparent=True)
                    #RIGGING.colorControl(mLoft.mNode,_side,'main',transparent = True)
                
                    mLoftSurface.inheritsTransform = 0
                    for s in mLoftSurface.getShapes(asMeta=True):
                        s.overrideDisplayType = 2   
                
                    self.mBlock.connectChildNode(mLoftSurface.mNode, 'formFootMesh', 'block')
                    
                for mPivot in ml_pivots:
                    mPivot.addAttr('cgmType','pivotHelper')            
                    mPivot.doName()
    
                    #CORERIG.colorControl(mPivot.mNode,_side,'sub') 
                    self.color(mPivot.mNode,_side,'sub')
                    
                    mPivot.parent = mPivotRootHandle
                    
                    #if mPivot.cgmName in ['ball','left','right']:
                        #mPivot.tz = .5
                        
                    #mPivotRootHandle.connectChildNode(mPivot,'pivot'+ mPivot.cgmName.capitalize(),'handle')#Connect    
                    self.mBlock.msgList_append('prerigHandles',mPivot)
                    
                    
    
                if self._mTransform.getShapes():
                    SNAPCALLS.snap(mPivotRootHandle.mNode,self._mTransform.mNode,rotation=False,targetPivot='axisBox',targetMode='y-')
                    mTopLoft.ty = 1
                    
                if _axisBox:
                    mc.delete(_axisBox)
                    
                log.info(_bbsize)
                #TRANS.scale_to_boundingBox(mPivotRootHandle.mNode,[_bbsize[0],None,_bbsize[2] * 2], False)
                #mPivotRootHandle.scale = [_bbsize[0],_bbsize[1],_bbsize[2] * 2]
                #mc.xform(mPivotRootHandle.mNode,
                         #scale = [_bbsize[0],_bbsize[1],_bbsize[2] * 2],
                         #worldSpace = True, absolute = True)
                
                return mPivotRootHandle,mTopLoft
            except Exception as err:
                cgmGEN.cgmExceptCB(Exception,err,msg=vars())
                
    def add_lidsHelper(self,upAxis = 'y+', setAttrs = {}):
        try:
            _str_func = 'add_lidsHelper'
            #mHandleMain = self._mTransform
            mBlock = self.mBlock
            _short = mBlock.mNode
            _side = self.get_side()
            
            if not mBlock.setupLid:
                raise ValueError("No setupLid option detected")
                return False
            
            _setup = mBlock.getEnumValueString('setupLid')
            
            log.info("|{0}| >> setupLid: {1}".format(_str_func,_setup))
            
            _v_size = [mBlock.blockScale * v for v in mBlock.baseSize]
            _bbsize = POS.get_axisBox_size(mBlock.mNode,False)
            _size = MATH.average(_bbsize)
            _sizeSub = _size * .2

            _bfr = mBlock.getMessage('lidsHelper')
            if _bfr:
                mc.delete(_bfr)
            
            

            ml_handles = []
            md_handles = {}
            mRootHandle = False
            self_pos = mBlock.p_position
            self_upVector = mBlock.getAxisVector(upAxis)
            self_aimVector = mBlock.getAxisVector('z+')

            d_handleDirections = {'upr':'y+',
                                 'lwr':'y-',
                                 'left':'x+',
                                 'right':'x-'}
            
            d_handleDirectionsDist = {'upr':_v_size[1],
                                      'lwr':_v_size[1],
                                      'left':_v_size[0],
                                      'right':_v_size[0]}
            _axisBox = False
            
            
            p_push = DIST.get_pos_by_vec_dist(self_pos, self_aimVector, _size * 3 )
            
            #Main Handle -----------------------------------------------------------------------------
            lidHandleShape = CURVES.create_controlCurve(mBlock.mNode,
                                                        'loftCircle',
                                                        direction = 'z+',
                                                        bakeScale = False,
                                                        size = _size)
            POS.set(lidHandleShape,p_push )
            if mBlock.getMessage('rootHelper'):
                mLidHandle = mBlock.rootHelper.doCreateAt(setClass=True)
                CORERIG.shapeParent_in_place(mLidHandle.mNode,lidHandleShape,False)
            else:
                mLidHandle = cgmMeta.validateObjArg(lidHandle,'cgmObject',setClass=True)

            mLidHandle.addAttr('cgmName','base')
            mLidHandle.addAttr('cgmType','lidsHelper')            
            mLidHandle.doName()
            #CORERIG.colorControl(mPivotRootHandle.mNode,_side,'sub') 
            self.color(mLidHandle.mNode,_side,'main')
        
            #mPivotRootHandle.parent = mPrerigNull
            mBlock.connectChildNode(mLidHandle,'lidsHelper','block')#Connect    
        
            if mBlock.hasAttr('setupLids'):
                mBlock.doConnectOut('addPivot',"{0}.v".format(mPivotRootHandle.mNode))
            
            mLidHandle.p_parent = mBlock.formNull
            
            mBlock.msgList_append('formHandles',mLidHandle)
            
            
            
            #if not _axisBox:
                #_axisBox = CORERIG.create_axisProxy(self._mTransform.mNode)
            l_handles = ['lidUpr','lidLwr']
                
            if _setup not in ['clam']:
                l_handles.extend(['lidLeft','lidRight'])
            
            #main handles =============================================================================
            for a in l_handles:
                _strHandle = a.split('lid')[-1]
                _strHandle = _strHandle[0].lower() + _strHandle[1:]
                _strName = _strHandle#d_altName.get(_strHandle,_strHandle)
                
                log.info("|{0}| >> Adding handle helper: {1}".format(_str_func,_strHandle))
                
                mAxis = VALID.simpleAxis(d_handleDirections[_strHandle])
                _inverse = mAxis.inverse.p_string
                
                handle = CURVES.create_fromName('cubeOpen',
                                                direction = 'z+',
                                                baseSize=1.0,
                                                size = _sizeSub*3)
                
                mHandle = cgmMeta.validateObjArg(handle,'cgmObject',setClass=True)
                mHandle.doSnapTo(_short)                
                mHandle.addAttr('cgmName',_strName)
                mHandle.p_parent = mLidHandle
                self.color(mHandle.mNode,_side,'main')
                mLidHandle.connectChildNode(mHandle, a ,'handle')#Connect    

                mHandle.p_position = DIST.get_pos_by_axis_dist(_short,mAxis.p_string,
                                                               d_handleDirectionsDist.get(_strName)/2)
                #SNAPCALLS.snap(mHandle.mNode,_axisBox,rotation=False,targetHandle='castNear',targetMode=mAxis.p_string)
                #SNAPCALLS.get_special_pos()
                #SNAP.aim_atPoint(mHandle.mNode,self_pos, _inverse, upAxis, mode='vector', vectorUp = self_upVector)

                ml_handles.append(mHandle)
                md_handles[_strName] = mHandle
                
                    #if _strHandle in ['left','right']:
                        #mHandle.p_position = p_ballPush
                        #mHandle.tz = .75
                        
            if _setup not in ['clam']:
                #Sub handles ==============================================================================
                d_handleDirections = {'uprLeft':['left','upr'],
                                      'uprRight':['right','upr'],
                                      'lwrLeft':['left','lwr'],
                                      'lwrRight':['right','lwr'],
                                      }
                
                for a,pair in list(d_handleDirections.items()):
                    log.info("|{0}| >> Adding sub handle helper: {1}".format(_str_func,a))
                                    
                    handle = CURVES.create_fromName('cube',
                                                    direction = 'z+',
                                                    size = _sizeSub * 2,
                                                    baseSize=1.0)
                    
                    mHandle = cgmMeta.validateObjArg(handle,'cgmObject',setClass=True)
                    mHandle.doSnapTo(_short)                
                    mHandle.addAttr('cgmName',a)
                    mHandle.p_parent = mLidHandle
                    
                    self.color(mHandle.mNode,_side,'sub')
                    mLidHandle.connectChildNode(mHandle, a ,'handle')#Connect
                    
                    mGroup = mHandle.doGroup(True,True,asMeta=True,typeModifier = 'constrain')
                    l_targets = []
                    for o in pair:
                        l_targets.append(md_handles[o].mNode)
                    mc.pointConstraint(l_targets, mGroup.mNode, maintainOffset = False)
                    
                    ml_handles.append(mHandle)
                md_handles[a] = mHandle

            
            for mHandle in ml_handles:
                mHandle.addAttr('cgmType','handleHelper')            
                mHandle.doName()

                #CORERIG.colorControl(mHandle.mNode,_side,'sub') 
                #self.color(mHandle.mNode,_side,'sub')
                self.mBlock.msgList_append('formHandles',mHandle)
                
                
            #Curves ============================================================
                
                

            return mLidHandle
        except Exception as err:
            cgmGEN.cgmExceptCB(Exception,err,msg=vars())

    def addScalePivotHelper(self,baseShape=None, baseSize = None, shapeDirection = 'z+', setAttrs = {}):
        _baseDat = self.get_baseDat(baseShape,baseSize)
        _baseShape = _baseDat[0]
        _baseSize = _baseDat[1]
        _side = self.get_side()

        mHandle = self._mTransform
        _bfr = mHandle.getMessage('scalePivotHelper')
        if _bfr:
            mc.delete(_bfr)

        _sizeSub = MATH.average(_baseSize) * .5


        #helper ======================================================================================
        _curve = CURVES.create_controlCurve(mHandle.mNode,'arrowsScaleOut',  direction= shapeDirection, sizeMode = 'fixed', bakeScale = False,size = _sizeSub)
        mCurve = cgmMeta.validateObjArg(_curve, mType = 'cgmObject',setClass=True)

        if mHandle.hasAttr('cgmName'):
            ATTR.copy_to(mHandle.mNode,'cgmName',mCurve.mNode,driven='target')
        mCurve.doStore('cgmType','scalePivotHelper')
        mCurve.doName()    

        mCurve.p_parent = mHandle

        for a,v in list(setAttrs.items()):
            ATTR.set(mCurve.mNode, a, v)

        CORERIG.match_transform(mCurve.mNode, mHandle)
        mCurve.connectParentNode(mHandle.mNode,'handle','scalePivotHelper')      
        self.color(mCurve.mNode,_side,'sub')

        if mHandle.hasAttr('addScalePivot'):
            mHandle.doConnectOut('addScalePivot',"{0}.v".format(mCurve.mNode))

        self.mBlock.msgList_append('prerigHandles',mCurve.mNode)
        return mCurve    

    def get_subSize(self,mult = .2):
        mHandle = self._mTransform        
        _absize = POS.get_axisBox_size(mHandle.mNode)
        _size = MATH.average(_absize)
        _sizeSub = _size * mult
        return _sizeSub, _size, _absize

    def addCogHelper(self,baseShape=None, baseSize = None, shapeDirection = 'z+', setAttrs = {}):
        try:
            _baseDat = self.get_baseDat(baseShape,baseSize)
            _baseShape = _baseDat[0]
            _baseSize = _baseDat[1]
            _plug = 'cogHelper'
            _side = self.get_side()
            
            _d_shapeDirectionOptions = {'z+':{'up':'y+',
                                       'directions':{'back':'z-',
                                                     'front':'z+',
                                                     'left':'x+',
                                                     'right':'x-'}},
                                        'z-':{'up':'y+',
                                              'directions':{'back':'z-',
                                                            'front':'z+',
                                                            'left':'x+',
                                                            'right':'x-'}},
                                        'y-':{'up':'z+',
                                              'directions':{'back':'y-',
                                                            'front':'y+',
                                                            'left':'x+',
                                                            'right':'x-'}},                                        
                                        'y+':{'up':'z+',
                                              'directions':{'back':'y-',
                                                            'front':'y+',
                                                            'left':'x+',
                                                            'right':'x-'}},
                                 }
            _d_shapeDirection = _d_shapeDirectionOptions.get(shapeDirection)
            if not _d_shapeDirection:
                raise ValueError("shapeDirection {0} not setup".format(shapeDirection))

            mHandle = self._mTransform
            mBlock = self.mBlock
            upAxis = _d_shapeDirection['up']
            _short = mHandle.mNode

            _bfr = mHandle.getMessage(_plug)
            if _bfr:
                mc.delete(_bfr)
                
            _sizeSub, _size, _absize = self.get_subSize(.25)
            #_sizeByBB = [_absize[0] * .5, _absize[1] * .15, _absize[2]*.5]
            _sizeByBB = [_absize[0] * .25, _absize[1] * .25, _absize[2]*.25]
            
            self_pos = mHandle.p_position
            self_upVector = mHandle.getAxisVector(upAxis)
            _sizeArrow = (MATH.average(_absize)) * .25
            mCurve = cgmMeta.validateObjArg(self._mTransform.doCreateAt(),'cgmObject',setClass=True)
            
            #helper ======================================================================================
            d_shapeDirections = _d_shapeDirection['directions']
            
            ml_shapes = []
            for d,axis in list(d_shapeDirections.items()):
                mAxis = VALID.simpleAxis(axis)
                _inverse = mAxis.inverse.p_string
                shape = CURVES.create_controlCurve(mHandle.mNode, shape='pyramid',
                                                   direction = axis,bakeScale = False,
                                                   sizeMode = 'fixed', size = [_sizeArrow,_sizeArrow,_sizeArrow])
                mShape = cgmMeta.validateObjArg(shape,'cgmObject',setClass=True)
                _pos = DIST.get_pos_by_axis_dist(_short,mAxis.p_string, _size)
                mShape.p_position = _pos
                #import cgm.core.lib.locator_utils as LOC
                #LOC.create(position=_pos)
                SNAP.aim_atPoint(mShape.mNode,self_pos, _inverse, upAxis, mode='vector',
                                 vectorUp = self_upVector)

                ml_shapes.append(mShape)

                #mCurve.scaleY = 2
                #mCurve.scaleZ = .75
                
                CORERIG.shapeParent_in_place(mCurve.mNode,mShape.mNode,False)
            
            """
            mCurve = cgmMeta.validateObjArg(CORERIG.combineShapes([mObj.mNode for mObj in ml_shapes],keepSource=False),
                                            'cgmObject',setClass=True)"""


            if mHandle.hasAttr('cgmName'):
                ATTR.copy_to(mHandle.mNode,'cgmName',mCurve.mNode,driven='target')
                
            mCurve.doStore('cgmType',_plug)
            mCurve.doStore('cgmTypeModifier','shape')            
            mCurve.doName()    

            mCurve.p_parent = mHandle

            for a,v in list(setAttrs.items()):
                ATTR.set(mCurve.mNode, a, v)


            #CORERIG.colorControl(mCurve.mNode,_side,'sub')
            self.color(mCurve.mNode,_side,'sub')
            
            #Transform ---------------------------------------------------------------------------
            #CURVES.create_text('COG',MATH.average(_sizeByBB))
            mTrans = cgmMeta.validateObjArg( CURVES.create_fromName('axis3d',
                                                                    MATH.average(_sizeByBB),bakeScale=1) ,
                                             'cgmObject',setClass=True)
            SNAP.go(mTrans.mNode, mCurve.mNode)
            #self.color(mTrans.mNode,_side,'main')
            
            if mHandle.hasAttr('cgmName'):
                ATTR.copy_to(mHandle.mNode,'cgmName',mTrans.mNode,driven='target')            
            
            mTrans.doStore('cgmType',_plug)
            mTrans.doStore('cgmTypeModifier','dag')            
            
            mTrans.doName()                
            
            mCurve.p_parent = mTrans
            
            mTrans.connectParentNode(mBlock.mNode,'rigBlock',_plug)            
            mCurve.connectParentNode(mTrans.mNode,'handle','shapeHelper')
            
            self.addJointLabel(mTrans,'cog')
            
            if mBlock.hasAttr('addCog'):
                mBlock.doConnectOut('addCog',"{0}.v".format(mCurve.mNode))
                mBlock.doConnectOut('addCog',"{0}.v".format(mTrans.mNode))
            
            #mBlock.msgList_append('prerigHandles',mTrans.mNode)
            #mBlock.msgList_append('prerigHandles',mCurve.mNode)
            
            return mTrans
        except Exception as err:
            cgmGEN.cgmExceptCB(Exception,err,msg=vars())

    def setAttrs_fromDict(self, setAttrs={}):
        try:
            mHandle = self._mTransform   
            _short = mHandle.mNode

            for a,v in list(setAttrs.items()):
                ATTR.set(_short, a, v)
        except Exception as err:
            cgmGEN.cgmExceptCB(Exception,err,msg=vars())

    def addOrientHelper(self,baseShape=None, baseSize = None, shapeDirection = 'z-', setAttrs = {}):
        try:
            _baseDat = self.get_baseDat(baseShape,baseSize)
            _baseShape = _baseDat[0]
            _baseSize = _baseDat[1]

            mHandle = self._mTransform
            _short = mHandle.mNode
            _bfr = mHandle.getMessage('orientHelper')
            if _bfr:
                mc.delete(_bfr)
            
            #if baseSize is None:
            _size = MATH.average(_baseSize[:1])
            #else:
            #    _size = baseSize
                
            #Orientation helper ======================================================================================
            _orientHelper = CURVES.create_controlCurve(mHandle.mNode,'arrowSingle',  direction= shapeDirection, sizeMode = 'fixed', bakeScale = True,size = _size * .75)
            mCurve = cgmMeta.validateObjArg(_orientHelper, mType = 'cgmObject',setClass=True)


            mCurve.p_position = DIST.get_pos_by_axis_dist(_short,shapeDirection, _size/1.75)

            if mHandle.hasAttr('cgmName'):
                ATTR.copy_to(mHandle.mNode,'cgmName',mCurve.mNode,driven='target')        
            mCurve.doStore('cgmType','orientHandle')
            mCurve.doName()    

            mCurve.p_parent = mHandle

            for a,v in list(setAttrs.items()):
                ATTR.set(mCurve.mNode, a, v)

            CORERIG.match_transform(mCurve.mNode, mHandle)
            mCurve.connectParentNode(mHandle.mNode,'handle','orientHelper')      
            self.color(mCurve.mNode)

            return mCurve
        except Exception as err:
            cgmGEN.cgmExceptCB(Exception,err,msg=vars())

    def addProxyHelper(self,baseShape=None, baseSize = None, shapeDirection = 'z+', setAttrs = {}):
        try:
            _baseDat = self.get_baseDat(baseShape,baseSize)
            _baseShape = _baseDat[0]
            _baseSize = _baseDat[1]
            _side = self.get_side()
            #cgmGEN.func_snapShot(vars())
            mHandle = self._mTransform
            _short = mHandle.mNode
            _bfr = mHandle.getMessage('proxyHelper')
            
            if _bfr:
                mc.delete(_bfr)

            _proxyShape = self.mBlock.getEnumValueString('proxyShape')

            #Orientation helper ======================================================================================
            _proxy = CORERIG.create_proxyGeo(_proxyShape, _baseSize, shapeDirection)
            mProxy = cgmMeta.validateObjArg(_proxy[0], mType = 'cgmObject',setClass=True)

            mProxy.doSnapTo(mHandle)
            SNAPCALLS.snap(mProxy.mNode,mHandle.mNode, objPivot='boundingBox',objMode='y-',targetPivot='boundingBox',targetMode='y-')

            if mHandle.hasAttr('cgmName'):
                ATTR.copy_to(mHandle.mNode,'cgmName',mProxy.mNode,driven='target')        
            mProxy.doStore('cgmType','proxyHelper')
            mProxy.doName()    

            mProxy.p_parent = mHandle

            self.setAttrs_fromDict(setAttrs)

            #CORERIG.colorControl(mProxy.mNode,_side,'sub',transparent=True)
            self.color(mProxy.mNode,_side,'sub',transparent=True)

            mProxy.connectParentNode(mHandle.mNode,'handle','proxyHelper')

            if mHandle.hasAttr('proxyVis'):
                mHandle.doConnectOut('proxyVis',"{0}.v".format(mProxy.mNode))

            return mProxy
        except Exception as err:
            cgmGEN.cgmExceptCB(Exception,err,msg=vars())

    def addRootMotionHelper(self,baseShape='pivotLocator', baseSize = None, shapeDirection = 'z+'):
        try:
            mHandle = self._mTransform
            _bfr = mHandle.getMessage('rootMotionHelper')
            if _bfr:
                mc.delete(_bfr)

            _size = baseSize or 1.0
            pprint.pprint(vars())
            #helper ======================================================================================
            _str_curve = CURVES.create_fromName(baseShape, 
                                                direction= shapeDirection, sizeMode = 'fixed',
                                                size = _size,
                                                baseSize = 1.0,
                                                bakeScale = False)

            mCurve = cgmMeta.validateObjArg(_str_curve, mType = 'cgmObject',setClass=True)
            
            mCurve.doSnapTo(mHandle.mNode)
            if mHandle.hasAttr('cgmName'):
                ATTR.copy_to(mHandle.mNode,'cgmName',mCurve.mNode,driven='target')
                
            mCurve.doStore('cgmType','rootMotionHelper')
            mCurve.doName()    

            mCurve.p_parent = mHandle

            CORERIG.match_transform(mCurve.mNode, mHandle)


            mCurve.connectParentNode(mHandle.mNode,'handle','rootMotionHelper')   
            if mHandle.hasAttr('addMotionJoint'):
                mHandle.doConnectOut('addMotionJoint',"{0}.v".format(mCurve.mNode))
                ATTR.set_standardFlags(mCurve.mNode,['v'])

            self.mBlock.msgList_append('prerigHandles',mCurve.mNode)
            return mCurve
        except Exception as err:
            cgmGEN.cgmExceptCB(Exception,err,msg=vars())

    def addJointLabel(self,mHandle = None, label = None):
        _bfr = mHandle.getMessage('jointLabel')
        if _bfr:
            mc.delete(_bfr)
        
        if label is None:
            label = mHandle.cgmName
            
        #Joint Label ---------------------------------------------------------------------------
        mJointLabel = cgmMeta.validateObjArg(mc.joint(),'cgmObject',setClass=True)
    
        mJointLabel.p_parent = mHandle
        mJointLabel.resetAttrs()
        
        mParent = mJointLabel.getParent(asMeta=1)
        if mParent.mNode != mHandle.mNode:
            mParent.rename("{0}_zeroGroup".format(mHandle.p_nameBase))
            mParent.p_parent = mHandle            
            #mParent.resetAttrs()
            #mParent.dagLock()
            mJointLabel.resetAttrs()
            
        mJointLabel.radius = 0
        mJointLabel.side = 0
        mJointLabel.type = 18
        mJointLabel.drawLabel = 1
        mJointLabel.otherType = label
    
        mJointLabel.doStore('cgmName',mHandle)
        mJointLabel.doStore('cgmType','jointLabel')
        mJointLabel.doName()
    
    
        mJointLabel.overrideEnabled = 1
        mJointLabel.overrideDisplayType = 2
        
        mJointLabel.connectParentNode(mHandle.mNode,'handle','jointLabel')
        
        try:
            ATTR.connect("{0}.visLabels".format(self.mBlock.mNode), "{0}.overrideVisibility".format(mJointLabel.mNode))
        except:pass
            
        mJointLabel.dagLock()
        
        return mJointLabel
        
    def addJointHelper(self,baseShape='sphere', baseSize = None,
                       shapeDirection = 'z+', loftHelper = True,
                       lockChannels = ['rotate','scale']):
        try:


            mHandle = self._mTransform
            _bfr = mHandle.getMessage('jointHelper')
            if _bfr:
                mc.delete(_bfr)

            _size_vector = get_sizeVector(baseSize)
            _size = MATH.average(_size_vector[:1]) #* .5
    
            #Joint helper ======================================================================================
            #jack
            _jointHelper = CURVES.create_fromName(baseShape,  direction= shapeDirection, size = _size,bakeScale = False,baseSize=1.0)
            mJointCurve = cgmMeta.validateObjArg(_jointHelper, mType = 'cgmObject',setClass=True)
            mJointCurve.doSnapTo(mHandle.mNode)
            
            if baseShape == 'axis3d':
                mJointCurve.addAttr('cgmColorLock',True,lock=True,hidden=True)
                


            if mHandle.hasAttr('cgmName'):
                ATTR.copy_to(mHandle.mNode,'cgmName',mJointCurve.mNode,driven='target')
            mJointCurve.doStore('cgmType','jointHandle')
            mJointCurve.doName()    

            mJointCurve.p_parent = mHandle

            self.color(mJointCurve.mNode)

            #CORERIG.match_transform(mJointCurve.mNode, mHandle)

            #mc.transformLimits(mJointCurve.mNode, tx = (-.5,.5), ty = (-.5,.5), tz = (-.5,.5),
            #                   etx = (True,True), ety = (True,True), etz = (True,True))        

            mJointCurve.connectParentNode(mHandle.mNode,'handle','jointHelper')   

            mJointCurve.setAttrFlags(lockChannels)

            if loftHelper:#...loft curve -------------------------------------------------------------------------------------
                #mLoft = self.buildBaseShape('square',_size*.5,'z+')
                _loft = CURVES.create_controlCurve(mHandle.mNode,'square',  direction= shapeDirection, sizeMode = 'fixed', size = _size * .5,bakeScale = False)
                mLoft = cgmMeta.validateObjArg(_loft,'cgmObject',setClass=True)
                mLoft.doStore('cgmName',mJointCurve)
                mLoft.doStore('cgmType','loftCurve')
                mLoft.doName()
                mLoft.p_parent = mJointCurve
                self.color(mLoft.mNode,controlType='sub')

                for s in mLoft.getShapes(asMeta=True):
                    s.overrideEnabled = 1
                    s.overrideDisplayType = 2
                mLoft.connectParentNode(mJointCurve,'handle','loftCurve')        

            return mJointCurve
        except Exception as err:
            cgmGEN.cgmExceptCB(Exception,err,msg=vars())

    def rebuildAsLoftTarget(self, baseShape = None, baseSize = None, shapeDirection = 'z+', rebuildHandle = True):
        _baseDat = self.get_baseDat(baseShape,baseSize)
        _baseShape = _baseDat[0]
        _baseSize = _baseDat[1]   


        if baseShape != 'self':
            if rebuildHandle:
                self.cleanShapes()      
                _offsetSize = _baseSize * 1.3
                _dist = _baseSize *.05
                _mShapeDirection = VALID.simpleAxis(shapeDirection)
                
                mCrv = self.buildBaseShape(_baseShape,_offsetSize,shapeDirection)
                CORERIG.shapeParent_in_place(self._mTransform.mNode,mCrv.mNode,False,True)
                self.color(self._mTransform.mNode)
                
                """
                for i,p in enumerate(['upper','lower']):
                    mCrv = self.buildBaseShape(_baseShape,_offsetSize,shapeDirection)
                    if i == 0:
                        _pos = self._mTransform.getPositionByAxisDistance(_mShapeDirection.p_string,_dist)
                    else:
                        _pos = self._mTransform.getPositionByAxisDistance(_mShapeDirection.p_string,-_dist)

                    mCrv.p_position = _pos
                    CORERIG.shapeParent_in_place(self._mTransform.mNode,mCrv.mNode,False)

                    self.color(self._mTransform.mNode)"""

            #>>>make our loft curve
            mCrv = self.buildBaseShape(_baseShape,_baseSize,shapeDirection)
            #mCrv.doStore('cgmName',self._mTransform)
            mCrv.doCopyNameTagsFromObject(self._mTransform.mNode,['cgmType'])
            mCrv.doStore('cgmType','shapeHandle')
            mCrv.doName()
            mCrv.p_parent = self._mTransform
            self.color(mCrv.mNode,controlType='sub')

            #for s in mCrv.getShapes(asMeta=True):
                #s.overrideEnabled = 1
                #s.overrideDisplayType = 2
            mCrv.connectParentNode(self._mTransform,'handle','loftCurve')            

            return mCrv

        else:
            _baseSize = DIST.get_createSize(self._mTransform.getShapes()[0])
            _baseShape = 'self'

            _offsetSize = _baseSize * 1.3
            _dist = _baseSize *.05
            _mShapeDirection = VALID.simpleAxis(shapeDirection)               

            mBaseCrv = self.buildBaseShape('self',_offsetSize,shapeDirection)
            
            mCrv = mBaseCrv.doDuplicate(po=False)
            mCrv.scale = [1.25,1.25,1.25]
            CORERIG.shapeParent_in_place(self._mTransform.mNode,mCrv.mNode,False,True)
            
            """
            #>>> make our offset shapes to control our handle
            for i,p in enumerate(['upper','lower']):
                mCrv = mBaseCrv.doDuplicate(po=False)
                if baseShape == 'self':
                    #mc.scale(_offsetSize,_offsetSize,_offsetSize, mCrv.mNode, absolute = True)
                    #mc.xform(mCrv.mNode, scale = [_baseSize,_baseSize,_baseSize], worldSpace = True, relative = True)
                    mCrv.scale = [1.25,1.25,1.25]
                if i == 0:
                    _pos = self._mTransform.getPositionByAxisDistance(_mShapeDirection.p_string,_dist)
                else:
                    _pos = self._mTransform.getPositionByAxisDistance(_mShapeDirection.p_string,-_dist)

                mCrv.p_position = _pos
                CORERIG.shapeParent_in_place(self._mTransform.mNode,mCrv.mNode,False)"""

            self.color(self._mTransform.mNode)

            #>>>make our loft curve
            mCrv = mBaseCrv
            #mCrv.doStore('cgmName',self._mTransform)
            mCrv.doCopyNameTagsFromObject(self._mTransform.mNode,['cgmType'])            
            mCrv.doStore('cgmType','shapeHandle')
            mCrv.doName()
            mCrv.p_parent = self._mTransform
            self.color(mCrv.mNode,controlType='sub')

            #for s in mCrv.getShapes(asMeta=True):
                #s.overrideEnabled = 1
                #s.overrideDisplayType = 2
            mCrv.connectParentNode(self._mTransform,'handle','loftCurve')

            return mCrv
    

def rootMotionHelper(self,mHandle=None,
                     baseShape = 'axis3d',#'arrowSingleFat3d',
                     shapeDirection = 'z+',#'y-', 
                     size = 1.0,
                     snapToGround = True):
    try:
        if not mHandle:mHandle = self
            
        _bfr = mHandle.getMessage('rootMotionHelper')
        if _bfr:
            mc.delete(_bfr)

        #pprint.pprint(vars())
        
        """
         mHandleFactory.addRootMotionHelper(baseShape='arrowSingleFat3d',
                                                              baseSize = offset *5,
                                                              shapeDirection = 'y-')
            mShape = mMotionJoint.doDuplicate(po=False)
            SNAP.to_ground(mShape.mNode)
            CORERIG.shapeParent_in_place(mMotionJoint.mNode, mShape.mNode, False,True)
            mMotionJoint.p_parent = mPrerigNull
        """
        
        
        #helper ======================================================================================
        _str_curve = CURVES.create_fromName(baseShape, 
                                            direction= shapeDirection,
                                            size = size,
                                            baseSize = 1.0,
                                            bakeScale = False)

        mShape = cgmMeta.validateObjArg(_str_curve, mType = 'cgmObject',setClass=True)
        
        mShape.doSnapTo(mHandle.mNode)
        
        
        if snapToGround:
            mDag = self.doCreateAt(setClass=True)
            SNAP.to_ground(mShape.mNode)
            CORERIG.shapeParent_in_place(mDag.mNode,mShape.mNode,False)
        else:
            mDag = mShape
            CORERIG.match_transform(mCurve.mNode, mHandle)            
        
        if baseShape != 'axis3d':
            color(self,mDag)
        else:
            mDag.addAttr('cgmColorLock',True,lock=True,hidden=True)            
            
        
        if mHandle.hasAttr('cgmName'):
            ATTR.copy_to(mHandle.mNode,'cgmName',mDag.mNode,driven='target')
            
        mDag.doStore('cgmType','rootMotionHelper')
        mDag.doName()    

        mDag.connectParentNode(mHandle.mNode,'handle','rootMotionHelper')   
        if mHandle.hasAttr('addMotionJoint'):
            mHandle.doConnectOut('addMotionJoint',"{0}.v".format(mDag.mNode))
            ATTR.set_standardFlags(mDag.mNode,['v'])

        self.msgList_append('prerigHandles',mDag.mNode)
        return mDag
    except Exception as err:
        cgmGEN.cgmExceptCB(Exception,err,msg=vars())
        
def get_sizeVector(value):
    if VALID.isListArg(value):
        return value
    return [value,value,value]


def addJointLabel(self,mHandle = None, label = None):
    _bfr = mHandle.getMessage('jointLabel')
    if _bfr:
        mc.delete(_bfr)
    
    if label is None:
        label = mHandle.cgmName
        
    #Joint Label ---------------------------------------------------------------------------
    mJointLabel = cgmMeta.validateObjArg(mc.joint(),'cgmObject',setClass=True)

    mJointLabel.p_parent = mHandle
    mJointLabel.resetAttrs()
    
    mParent = mJointLabel.getParent(asMeta=1)
    if mParent.mNode != mHandle.mNode:
        mParent.rename("{0}_zeroGroup".format(mHandle.p_nameBase))
        mParent.p_parent = mHandle
        mJointLabel.resetAttrs()
        
        mParent.resetAttrs()
        mParent.dagLock()
        
    mJointLabel.radius = 0
    mJointLabel.side = 0
    mJointLabel.type = 18
    mJointLabel.drawLabel = 1
    mJointLabel.otherType = label

    mJointLabel.doStore('cgmName',mHandle)
    mJointLabel.doStore('cgmType','jointLabel')
    mJointLabel.doName()


    mJointLabel.overrideEnabled = 1
    mJointLabel.overrideDisplayType = 2
    
    mJointLabel.connectParentNode(mHandle.mNode,'handle','jointLabel')
    
    try:
        ATTR.connect("{0}.visLabels".format(self.mNode), "{0}.overrideVisibility".format(mJointLabel.mNode))
    except:pass
        
    mJointLabel.dagLock()
    
    return mJointLabel

def verify_visFormMesh(self):
    mLoftMesh = self.getMessageAsMeta('prerigLoftMesh')
    if not mLoftMesh:
        return False
    
    if not self.hasAttr('visFormMesh'):
        self.addAttr('visFormMesh',attrType='bool',defaultValue=True)
        
    self.doConnectOut('visFormMesh',"{0}.template".format(mLoftMesh.mNode))    

    return True


def addJointRadiusVisualizer(self,mParent = False):
    
    if not self.hasAttr('jointRadius'):
        return log.warning("No jointRadius attr: {0}".format(self))
    
    _crv = CURVES.create_fromName(name='sphere',#'arrowsAxis', 
                                  bakeScale = 1,                                              
                                  direction = 'z+', size = 1.0)

    mJointRadius = cgmMeta.validateObjArg(_crv,'cgmControl',setClass = True)
    mJointRadius.p_parent = mParent
    mJointRadius.doSnapTo(self.mNode)
    CORERIG.override_color(mJointRadius.mNode, 'black')
    
    mJointRadius.template = 1
    
    mJointRadius.rename("jointRadiusVis")
    _base = self.atUtils('get_shapeOffset')*2
    if self.jointRadius < .3:
        self.jointRadius = self.atUtils('get_shapeOffset')
        
    self.doConnectOut('jointRadius',"{0}.scale".format(mJointRadius.mNode),pushToChildren=1)    
    mJointRadius.connectParentNode(self, 'rigBlock','jointRadiusVisualize')
    
    if mParent:
        mc.parentConstraint(self.mNode, mJointRadius.mNode, maintainOffset = True)
        
    mJointRadius.dagLock()
    
    return mJointRadius

def addJointHelper(self,mHandle=None,
                   baseShape='sphere',#'locatorForm',
                   size = 1.0,
                   shapeDirection = 'z+',
                   loftHelper = True,
                   d_nameTags = {},
                   lockChannels = ['scale']):
    
    if mHandle:
    
        _bfr = mHandle.getMessage('jointHelper')
        if _bfr:mc.delete(_bfr)
    
    _size_vector = get_sizeVector(size)
    _size = MATH.average(_size_vector[:1]) #* .5


    #Joint helper ======================================================================================
    #jack
    _jointHelper = CURVES.create_fromName(baseShape,  direction= shapeDirection, size = _size,bakeScale = False,baseSize=1.0)
    mJointCurve = cgmMeta.validateObjArg(_jointHelper, mType = 'cgmObject',setClass=True)
    color(self,mJointCurve.mNode)
    
    
    if mHandle:
        mJointCurve.doSnapTo(mHandle.mNode)

        if mHandle.hasAttr('cgmName'):
            ATTR.copy_to(mHandle.mNode,'cgmName',mJointCurve.mNode,driven='target')
    
        mJointCurve.doStore('cgmType','jointHandle')
        mJointCurve.doName()    

        mJointCurve.p_parent = mHandle
        mJointCurve.connectParentNode(mHandle.mNode,'handle','jointHelper')
    else:
        if d_nameTags:
            for t,tag in list(d_nameTags.items()):
                if tag not in [None,False]:
                    mJointCurve.doStore(t,tag)
            mJointCurve.doName()                                

    mJointCurve.setAttrFlags(lockChannels)

    if loftHelper:#...loft curve -------------------------------------------------------------------------------------
        #mLoft = self.buildBaseShape('square',_size*.5,'z+')
        _loft = CURVES.create_controlCurve(mJointCurve.mNode,'square',  direction= shapeDirection, sizeMode = 'fixed', size = _size * .25, bakeScale = True)
        mLoft = cgmMeta.validateObjArg(_loft,'cgmObject',setClass=True)
        mLoft.doStore('cgmName',mJointCurve)
        mLoft.doStore('cgmType','loftCurve')
        mLoft.doName()
        mLoft.p_parent = mJointCurve
        color(self,mLoft.mNode,controlType='sub')

        for s in mLoft.getShapes(asMeta=True):
            s.overrideEnabled = 1
            s.overrideDisplayType = 2
        mLoft.connectParentNode(mJointCurve,'handle','loftCurve')        

    return mJointCurve

l_pivotShapes = ['pivotBack','pivotFront','pivotLeft','pivotRight','pivotCenter']
def pivotHelper(self,mHandle=None, 
                baseShape=None,
                baseSize = None,
                upAxis = 'y+',
                setAttrs = {},
                side = None,
                loft = True,
                l_pivots = l_pivotShapes,
                mParent = False,
                forceNew=False):
    try:
        _str_func = 'addPivotSetupHelper'
        mBuffer = mHandle.getMessageAsMeta('pivotHelper')
        if mBuffer:
            if forceNew:
                mBuffer.delete()
            else:
                return mBuffer
            
        #_bbsize = POS.get_axisBox_size(mHandle.mNode,False)
        #_size = MATH.average(_bbsize)
        _size = baseSize
        if self.hasAttr('jointRadius'):
            _sizeSub = self.jointRadius
        else:
            _sizeSub = _size * .2        
            
        
        mHandleFactory = self.asHandleFactory()
        
        if side == None:
            _side = self.UTILS.get_side(self)
        else:
            _side = side

        ml_pivots = []
        mPivotRootHandle = mParent
        self_pos = mHandle.p_position
        self_upVector = mHandle.getAxisVector(upAxis)

        d_pivotDirections = {'back':'z-',
                             'front':'z+',
                             'left':'x+',
                             'right':'x-'}

        d_altName = {'back':'heel',
                     'front':'toe',
                     'center':'ball'}

        mAxis = VALID.simpleAxis(d_pivotDirections['front'])
        
        if baseShape not in ['xxx']:#circle
            _baseShape = 'loft' + baseShape[0].capitalize() + ''.join(baseShape[1:])
        else:
            _baseShape = baseShape
        _baseSize = baseSize
        #Main Handle -----------------------------------------------------------------------------
        pivotHandle = CURVES.create_controlCurve(mHandle.mNode,
                                                 shape=_baseShape,
                                                 direction = 'y-',
                                                 sizeMode = 'fixed',
                                                 bakeScale = False,
                                                 size = _size)
        mPivotRootHandle = cgmMeta.validateObjArg(pivotHandle,'cgmObject',setClass=True)
        mPivotRootHandle.addAttr('cgmName','base')
        mPivotRootHandle.addAttr('cgmType','pivotHelper')            
        mPivotRootHandle.doName()

        mPivotRootHandle.p_position = self_pos
        mHandleFactory.color(mPivotRootHandle.mNode,_side,'main')

        mHandle.connectChildNode(mPivotRootHandle,'pivotHelper','block')#Connect    

        if mHandle.hasAttr('addPivot'):
            mHandle.doConnectOut('addPivot',"{0}.v".format(mPivotRootHandle.mNode))

        self.msgList_append('prerigHandles',mPivotRootHandle)

        #Top loft ----------------------------------------------------------------
        mTopLoft = False
        if loft:
            mTopLoft = mPivotRootHandle.doDuplicate(po=False)
            mTopLoft.addAttr('cgmName','topLoft')
            mTopLoft.addAttr('cgmType','pivotHelper')            
            mTopLoft.doName()
                
            mTopLoft.parent = mParent
            mTrack = mTopLoft.doCreateAt(setClass='cgmObject')
            mTrack.p_parent = mPivotRootHandle
            mGroup = mTopLoft.doGroup(True,True,asMeta=True,typeModifier = 'track',setClass='cgmObject')
            mc.parentConstraint(mTrack.mNode, mGroup.mNode, maintainOffset =True)
            mc.scaleConstraint(mTrack.mNode, mGroup.mNode, maintainOffset =True)
            
            mPivotRootHandle.connectChildNode(mTopLoft, 'topLoft' ,'handle')#Connect
            
            mHandleFactory.color(mTopLoft.mNode,_side,'sub')
            


        #_axisBox = CORERIG.create_proxyGeo('cube',_baseSize,ch=False)[0]
        #SNAP.go(_axisBox,mHandle.mNode)
            #_axisBox = CORERIG.create_axisProxy(self._mTransform.mNode)

        #Sub pivots =============================================================================
        for a in l_pivots:
            _strPivot = a.split('pivot')[-1]
            _strPivot = _strPivot[0].lower() + _strPivot[1:]
            _strName = d_altName.get(_strPivot,_strPivot)
            log.debug("|{0}| >> Adding pivot helper: {1}".format(_str_func,_strPivot))
            if _strPivot == 'center':
                pivot = CURVES.create_controlCurve(mHandle.mNode, shape='circle',
                                                   direction = upAxis,
                                                   sizeMode = 'fixed',
                                                   bakeScale = 0,
                                                   size = _sizeSub)
                mPivot = cgmMeta.validateObjArg(pivot,'cgmObject',setClass=True)
                mPivot.addAttr('cgmName',_strName)
                ml_pivots.append(mPivot)
                mPivot.p_parent = mParent
                
                mTrack = mPivot.doCreateAt(setClass='cgmObject')
                mTrack.p_parent = mPivotRootHandle
                mGroup = mPivot.doGroup(True,True,asMeta=True,typeModifier = 'track',setClass='cgmObject')
                mc.parentConstraint(mTrack.mNode, mGroup.mNode, maintainOffset =True)                

                mPivotRootHandle.connectChildNode(mPivot, a ,'handle')#Connect    

                #mPivot.p_position = p_ballPush
            else:
                mAxis = VALID.simpleAxis(d_pivotDirections[_strPivot])
                _inverse = mAxis.inverse.p_string
                pivot = CURVES.create_controlCurve(mHandle.mNode, shape='hinge',
                                                   direction = _inverse,
                                                   bakeScale = 1,
                                                   sizeMode = 'fixed', size = _sizeSub)
                mPivot = cgmMeta.validateObjArg(pivot,'cgmObject',setClass=True)
                mPivot.addAttr('cgmName',_strName)
                


                #mPivot.p_position = DIST.get_pos_by_axis_dist(mHandle.mNode,mAxis.p_string, _size)
                mPivot.p_position = DIST.get_closest_point(DIST.get_pos_by_axis_dist(mHandle.mNode,mAxis.p_string, _size),
                                                           mPivotRootHandle.mNode)[0]
                #SNAPCALLS.snap(mPivot.mNode,_axisBox,rotation=False,targetPivot='castNear',targetMode=mAxis.p_string)
                #SNAPCALLS.get_special_pos()
                #mPivot.p_position = #SNAPCALLS.get_special_pos(mPivotRootHandle.p_nameLong,'axisBox',mAxis.p_string,True)
                #SNAP.aim_atPoint(mPivot.mNode,self_pos, _inverse, upAxis, mode='vector', vectorUp = self_upVector)
                
                mPivot.p_parent = mParent
            
                mTrack = mPivot.doCreateAt(setClass='cgmObject')
                mTrack.p_parent = mPivotRootHandle
                mGroup = mPivot.doGroup(True,True,asMeta=True,typeModifier = 'track',setClass='cgmObject')
                mc.parentConstraint(mTrack.mNode, mGroup.mNode, maintainOffset =True)
                
                mPivotRootHandle.connectChildNode(mPivot, a ,'handle')#Connect                    

                ml_pivots.append(mPivot)

                #if _strPivot in ['left','right']:
                    #mPivot.p_position = p_ballPush
                    #mPivot.tz = .75

        #Clean up Pivot root after all else --------------------------------------------------
        #mAxis = VALID.simpleAxis(d_pivotDirections['back'])
        #p_Base = DIST.get_pos_by_axis_dist(mPivotRootHandle.mNode,
        #                                   d_pivotDirections['back'],
        #                                   _size/4 )

        #mc.xform (mPivotRootHandle.mNode,  ws=True, sp= p_Base, rp=p_Base, p=True)

        #for mPivot in ml_pivots:#Unparent for loft
            #mPivot.p_parent = False
            
        if loft:
            if mHandle.getMessage('loftCurve'):
                log.debug("|{0}| >> LoftSetup...".format(_str_func))
    
                #Fix the aim on the foot
                #mTopLoft.parent = False
    
                l_footTargets = [mHandle.loftCurve.mNode, mTopLoft.mNode,mPivotRootHandle.mNode]
    
                _res_body = mc.loft(l_footTargets, o = True, d = 3, po = 0,reverseSurfaceNormals=True)
    
                #mTopLoft.parent = mPivotRootHandle
    
                _loftNode = _res_body[1]
                mLoftSurface = cgmMeta.validateObjArg(_res_body[0],'cgmObject',setClass= True)        
    
    
                mLoftSurface.overrideEnabled = 1
                mLoftSurface.overrideDisplayType = 2
                #...this used to be {1} + 1. may need to revisit for head/neck
    
                mLoftSurface.parent = self.formNull
    
                #mLoft.p_parent = mFormNull
                mLoftSurface.resetAttrs()
    
                ATTR.set(_loftNode,'degree',1)    
    
                mLoftSurface.doStore('cgmName',self)
                mLoftSurface.doStore('cgmType','footApprox')
                mLoftSurface.doName()
    
    
                #mc.polySetToFaceNormal(mLoft.mNode,setUserNormal = True)
                #polyNormal -normalMode 0 -userNormalMode 1 -ch 1 spine_block_controlsApproxShape;
    
                #mc.polyNormal(mLoft.mNode, normalMode = 0, userNormalMode = 1, ch=1)
    
                #Color our stuff...
                mHandleFactory.color(mLoftSurface.mNode,_side,'sub',transparent=True)
                #RIGGING.colorControl(mLoft.mNode,_side,'main',transparent = True)
                mLoftSurface.inheritsTransform = 0
                for s in mLoftSurface.getShapes(asMeta=True):
                    s.overrideDisplayType = 2   
    
                self.connectChildNode(mLoftSurface.mNode, 'formFootMesh', 'block')

        for mPivot in ml_pivots:
            mPivot.addAttr('cgmType','pivotHelper')            
            mPivot.doName()

            #CORERIG.colorControl(mPivot.mNode,_side,'sub') 
            mHandleFactory.color(mPivot.mNode,_side,'sub')

            #mPivot.parent = mPivotRootHandle

            #if mPivot.cgmName in ['ball','left','right']:
                #mPivot.tz = .5

            #mPivotRootHandle.connectChildNode(mPivot,'pivot'+ mPivot.cgmName.capitalize(),'handle')#Connect    
            self.msgList_append('prerigHandles',mPivot)



        #if mHandle.getShapes():
        #    SNAPCALLS.snap(mPivotRootHandle.mNode,mHandle.mNode,rotation=False,targetPivot='axisBox',targetMode='y-')
        #    mTopLoft.ty = 1

        #if _axisBox:
        #    mc.delete(_axisBox)

        #log.debug(_bbsize)
        #TRANS.scale_to_boundingBox(mPivotRootHandle.mNode,[_bbsize[0],None,_bbsize[2] * 2], False)
        #mPivotRootHandle.scale = [_bbsize[0],_bbsize[1],_bbsize[2] * 2]
        #mc.xform(mPivotRootHandle.mNode,
            #scale = [_bbsize[0],_bbsize[1],_bbsize[2] * 2],
            #worldSpace = True, absolute = True)
        
        if mTopLoft:
            mTopLoft.p_position = DIST.get_pos_by_axis_dist(mPivotRootHandle.mNode,'y+', MATH.average(_size)*.1)
            
            return mPivotRootHandle,mTopLoft
        return mPivotRootHandle
        
    except Exception as err:
        cgmGEN.cgmExceptCB(Exception,err,msg=vars())


def backup(self,ml_handles = None):
    try:
        _str_func = 'segment_handles'
        log_start(_str_func)
        
        mBlock = self.mBlock
        mRigNull = self.mRigNull
        _offset = self.v_offset
        _jointOrientation = self.d_orientation['str']
        
        if not ml_handles:
            raise ValueError("{0} | ml_handles required".format(_str_func))
    except Exception as err:cgmGEN.cgmExceptCB(Exception,err,localDat=vars())


def create_face_anchor(self, pos, mSurface,tag,k,side=None,controlType = 'main',orientToSurf = False,
                       nameDict=None, size = 1.0,mParent=None):
    mHandle = cgmMeta.validateObjArg(self.doCreateAt(),'cgmControl',setClass=1)
    
    #Position 
    datClose = DIST.get_closest_point_data(mSurface.mNode, targetPoint=pos)
    pClose = datClose['position']
    
    mHandle.p_position = pClose
    
    if orientToSurf:
        mc.delete(mc.normalConstraint(mSurface.mNode, mHandle.mNode,
                            aimVector = [0,0,1], upVector = [0,1,0],
                            worldUpObject = self.mNode,
                            worldUpType = 'objectrotation', 
                            worldUpVector = [0,1,0]))
    
    pBall = DIST.get_pos_by_axis_dist(mHandle.mNode,'z+',(size) * 3)
    
    mBall = cgmMeta.validateObjArg( CURVES.create_fromName('circle', size = size), 
                                      'cgmControl',setClass=1)
    mBall.doSnapTo(mHandle)
    mBall.p_position = pBall
    
    _crvLinear = CORERIG.create_at(create='curveLinear',
                                   l_pos=[pClose,pBall])
    
    CORERIG.shapeParent_in_place(mHandle.mNode, mBall.mNode,False)
    CORERIG.shapeParent_in_place(mHandle.mNode, _crvLinear,False)            

    mHandle._verifyMirrorable()
    
    if mParent:mHandle.p_parent = mParent
    
    if nameDict:
        RIGGEN.store_and_name(mHandle,nameDict)
    else:
        mHandle.doStore('cgmName',tag)
        mHandle.doStore('cgmType','anchor')
        mHandle.doName()
        
    _key = tag
    if k:
        _key = _key+k.capitalize()
        
    color(self,mHandle.mNode, side = side, controlType=controlType)

    return mHandle

def create_face_handle(self, pos, tag, k, side,
                       controlType = 'main',
                       mainShape = 'squareRounded',
                       mHandleShape = None,
                       mSurface = None,
                       jointShape = 'axis3d',
                       jointSize = None,
                       size = 1.0,
                       offset = 1,
                       mStateNull = None,
                       mNoTransformNull = None,
                       depthAttr = 'jointDepth',
                       offsetAttr = 'controlOffset',
                       mDriver = None,
                       mAttachCrv = None,
                       mode = None,
                       plugShape = 'shapeHelper',
                       plugDag = 'dagHelper',
                       attachToSurf = False,
                       shapeToSurf = False,
                       orientToDriver = False,
                       orientToNormal = False,
                       aimGroup = 0,nameDict = None):
    _str_func = 'create_face_handle'
    #Main handle ==================================================================================
    #Create...
    _mainSize = size
    if controlType == 'sub':
        _mainSize = size*.7
        
    if mHandleShape:
        mHandle = mHandleShape
    else:
        mHandle = cgmMeta.validateObjArg( CURVES.create_fromName(mainShape, size = _mainSize), 
                                      'cgmControl',setClass=1)
        mHandle._verifyMirrorable()
        mHandle.doSnapTo(self)
        if pos:mHandle.p_position = pos
    
    mHandle.p_parent = mStateNull
    
    #Name...
    if nameDict:
        dUse = copy.copy(nameDict)
        dUse['cgmType'] = plugShape
        
        RIGGEN.store_and_name(mHandle,dUse)
    else:
        mHandle.doStore('cgmName',tag)
        mHandle.doStore('cgmType', plugShape)
        mHandle.doName()
        
        
    _key = tag
    if k:
        _key = _key+k.capitalize()
    """
    mMasterGroup = mHandle.doGroup(True,True,
                                   asMeta=True,
                                   typeModifier = 'master',
                                   setClass='cgmObject')"""


    color(self, mHandle.mNode,side = side, controlType=controlType)
    mStateNull.connectChildNode(mHandle, _key+STR.capFirst(plugShape),'block')
    
    if mSurface and orientToNormal: #and not orientToDriver
        mc.delete(mc.normalConstraint(mSurface.mNode, mHandle.mNode,
                                aimVector = [0,0,1], upVector = [0,1,0],
                                worldUpObject = self.mNode,
                                worldUpType = 'objectrotation', 
                                worldUpVector = [0,1,0]))
    
    #Main handle ==================================================================================
    #Create...
    if jointSize is None:
        jointSize = size/2.0
        
    mDagHelper = cgmMeta.validateObjArg( CURVES.create_fromName(jointShape, size = jointSize,
                                                                bakeScale=1), 
                                      'cgmControl',setClass=1)
    
    if jointShape in ['axis3d']:
        mDagHelper.addAttr('cgmColorLock',True,lock=True,hidden=True)            
    else:
        color(self, mDagHelper.mNode,side = side, controlType='sub')
        
    mDagHelper._verifyMirrorable()
    mDagHelper.doSnapTo(self)
    
    if not mHandleShape:
        mDagHelper.p_orient = mHandle.p_orient
        mDagHelper.p_parent = mStateNull
    
    if pos:mDagHelper.p_position = pos
    
    #Name...
    if nameDict:
        dUse = copy.copy(nameDict)
        dUse['cgmType'] = plugDag               
        RIGGEN.store_and_name(mDagHelper,dUse)
    else:
        mDagHelper.doStore('cgmName',tag)
        mDagHelper.doStore('cgmType',plugDag)
        mDagHelper.doName()
        
        

    """
    mMasterGroup = mDagHelper.doGroup(True,True,
                                   asMeta=True,
                                   typeModifier = 'master',
                                   setClass='cgmObject')"""


    mStateNull.connectChildNode(mDagHelper, _key+STR.capFirst(plugDag),'block')
    
        
    if mSurface or mAttachCrv:
        if attachToSurf:
            #Attach group... -------------------------------------------------------------------------------
            mTrack = mHandle.doCreateAt()
            mTrack.p_parent = mNoTransformNull
            
            if mAttachCrv:
                mTrack.rename("{0}_curveDriver".format(mHandle.p_nameBase))
                
                _res = RIGCONSTRAINT.attach_toShape(mTrack.mNode,mAttachCrv.mNode,None,driver= mDriver)
                
                md = _res[-1]
                mFollicle = md['mDrivenLoc']
                for k in ['mDriverLoc','mDrivenLoc','mTrack']:
                    md[k].p_parent = mNoTransformNull
                    md[k].v = False
                
                mTrack.p_position = md['mDrivenLoc'].p_position
                mc.pointConstraint( md['mDrivenLoc'].mNode,mTrack.mNode,maintainOffset=0)
                
                if mSurface:
                    log.debug(cgmGEN.logString_msg(_str_func,'Attach curve'))
                    #We need a second driver point on the surface
                    mSurfaceTrack = mHandle.doCreateAt()
                    mSurfaceTrack.p_parent = mNoTransformNull                    
                    mSurfaceTrack.rename("{0}_surfaceDriver".format(mHandle.p_nameBase))
                    
                    _res = RIGCONSTRAINT.attach_toShape(mSurfaceTrack.mNode,mSurface.mNode,None,
                                                        driver= mDagHelper)
                    
                    md = _res[-1]
                    mFollicle = md['mFollicle']
                    for k in ['mDriverLoc','mFollicle']:
                        md[k].p_parent = mNoTransformNull
                        md[k].v = False
                    
                    mSurfaceTrack.p_position = md['mFollicle'].p_position
                    mc.pointConstraint(mFollicle.mNode,mSurfaceTrack.mNode,maintainOffset=0)
                    

                
            else:
                mTrack.rename("{0}_surfaceDriver".format(mHandle.p_nameBase))
                _res = RIGCONSTRAINT.attach_toShape(mTrack.mNode,mSurface.mNode,None,driver= mDriver)
                
                md = _res[-1]
                mFollicle = md['mFollicle']
                for k in ['mDriverLoc','mFollicle']:
                    md[k].p_parent = mNoTransformNull
                    md[k].v = False
                
                mTrack.p_position = md['mFollicle'].p_position
                mc.pointConstraint(mFollicle.mNode,mTrack.mNode,maintainOffset=0)
                if not orientToDriver:
                    mc.orientConstraint(mFollicle.mNode, mTrack.mNode,maintainOffset = True)                
                
            mDepth = mTrack.doCreateAt(setClass=1)
            mDepth.rename("{0}_depthDriver".format(mHandle.p_nameBase))
            mDepth.p_parent = mTrack
            
            mDagHelper.p_parent = mDepth
            
            if mode == 'handle':
                mPush = mTrack.doCreateAt(setClass=1)
                mPush.rename("{0}_pushDriver".format(mHandle.p_nameBase))
                
                mPush.p_parent = mTrack
                mHandle.p_parent = mPush
                ATTR.connect('{0}.{1}'.format(self.mNode,offsetAttr), "{0}.tz".format(mPush.mNode))
            
            else:
                mHandle.p_parent = mTrack

                if mAttachCrv:
                    mCrvTrack = mHandle.doCreateAt()
                    mCrvTrack.rename("{0}_crvDriver".format(mHandle.p_nameBase))
                    mCrvTrack.p_parent = mNoTransformNull
                    
                    _res = RIGCONSTRAINT.attach_toShape(mCrvTrack.mNode,mAttachCrv.mNode,'conPoint')
                    TRANS.parent_set(_res[0], mNoTransformNull.mNode)                    
                    
                    log.debug(cgmGEN.logString_msg('attachCrv'))
                    mDagHelper.p_parent = mCrvTrack
                    mDagHelper.resetAttrs()
                    
                    if orientToDriver:
                        mc.orientConstraint(mDriver.mNode, mCrvTrack.mNode,maintainOffset = False)
                    
                    if mSurface:
                        log.debug(cgmGEN.logString_msg(_str_func,'Attach curve'))
                        mPush = mSurfaceTrack.doCreateAt(setClass=1)
                        mPush.rename("{0}_pushDriver".format(mHandle.p_nameBase))
                        
                        mPush.p_parent = mSurfaceTrack
                        mHandle.p_parent = mPush
                        ATTR.connect('{0}.{1}'.format(self.mNode,offsetAttr), "{0}.tz".format(mPush.mNode))
                        
                        if orientToDriver:
                            mc.orientConstraint(mDriver.mNode, mSurfaceTrack.mNode,maintainOffset = False)
                            
                    mHandle.resetAttrs('translate')
                        
                else:
                    mHandle.p_position = mTrack.p_position
                    mDagHelper.resetAttrs()
                    
                    if mSurface:
                        mPush = mHandle.doCreateAt(setClass=1)
                        mPush.rename("{0}_pushDirect".format(mHandle.p_nameBase))
                        
                        mPush.p_parent = mTrack
                        mHandle.p_parent = mPush
                        ATTR.connect('{0}.{1}'.format(self.mNode,offsetAttr), "{0}.tz".format(mPush.mNode))
                        mPush.rotate = 0,0,0
                    
                    
            ATTR.connect('{0}.{1}'.format(self.mNode,depthAttr), "{0}.tz".format(mDepth.mNode))
            
            if shapeToSurf:
                mHandle.p_parent = mTrack
                
            if orientToDriver:
                mc.orientConstraint(mDriver.mNode, mTrack.mNode,maintainOffset = False)

        else:
            _dat = DIST.get_closest_point_data(mSurface.mNode, targetObj=mHandle)
            mHandle.p_position = DIST.get_pos_by_vec_dist(_dat['position'],_dat['normal'], self.controlOffset)
            mDagHelper.p_position = DIST.get_pos_by_vec_dist(_dat['position'],_dat['normal'], self.getMayaAttr(depthAttr))

    if aimGroup:
        mHandle.doGroup(True,True,
                        asMeta=True,
                        typeModifier = 'aim',
                        setClass='cgmObject')

    mDagHelper.doStore('shapeHelper',mHandle)
    mHandle.doStore('dagHelper',mDagHelper)
    
    return mHandle,mDagHelper

def create_face_anchorHandleCombo(self, pos, tag, k, side,
                                controlType = 'main',
                                mHandleShape = None,
                                mSurface = None,
                                jointShape = 'axis3d',
                                jointSize = None,
                                handleSize = 1.0,
                                handleShape = 'squareRounded',
                                size = 1.0,
                                offset = 1,
                                mParent = None,
                                mNoTransformNull = None,
                                mDriver = None,
                                mAttachCrv = None,
                                mode = None,
                                depthAttr = 'jointDepth',
                                offsetAttr = 'controlOffset',
                                
                                plugShape = 'shapeHelper',
                                plugDag = 'dagHelper',
                                attachToSurf = False,
                                orientToDriver = False,
                                aimGroup = 0,nameDict = None,
                                anchorSize = 1.0,
                                orientToSurf = False,**kws):
                                    
    d_anchor = copy.copy(nameDict)
    d_anchor['cgmType'] = 'preAnchor'
    
    mAnchor = create_face_anchor(self, pos, mSurface,tag,k,side,controlType,orientToSurf,
                                 d_anchor, anchorSize,mParent)
    
    d_use = mAnchor.getNameDict(ignore=['cgmType'])
    
    mShape, mDag = create_face_handle(self,mAnchor.p_position,
                                      tag,
                                      None,
                                      side,
                                      size = size,
                                      mDriver=mAnchor,
                                      mSurface=mSurface,
                                      mHandleShape = mHandleShape,
                                      mainShape = handleShape,
                                      jointShape=jointShape,
                                      jointSize = jointSize,
                                      controlType=controlType,
                                      mode=mode,
                                      plugDag= plugDag,
                                      plugShape= plugShape,
                                      depthAttr = depthAttr,
                                      offsetAttr = offsetAttr,
                                      attachToSurf=attachToSurf,
                                      orientToDriver = orientToDriver,
                                      nameDict= d_use,
                                      mParent = mParent,
                                      mNoTransformNull=mNoTransformNull)
    
    try:kws.get('ml_handles').extend([mAnchor,mShape,mDag])
    except:pass
    
    try:kws.get('md_handles')[tag] = mShape
    except:pass
    
    try:kws.get('md_handles')[tag+'Joint'] = mDag
    except:pass
    
    try:kws.get('ml_jointHandles').append(mDag)
    except:pass
    
    try:kws.get('md_mirrorDat')[side].extend([mAnchor,mShape,mDag])    
    except:pass
    
    
    return mAnchor,mShape,mDag
    

def create_visualTrack(self,mHandle, mTarget,tag='track',mParent = None):
    _str_func = 'create_visualTrack'
    log.debug("|{0}| >> visualConnection ".format(_str_func, tag))
    trackcrv,clusters = CORERIG.create_at([mHandle.mNode,
                                           mTarget.mNode],#ml_handleJoints[1]],
                                          'linearTrack',
                                          baseName = '{0}_midTrack'.format(tag))

    mTrackCrv = cgmMeta.asMeta(trackcrv)
    if mParent:mTrackCrv.p_parent = mParent
    color(self, trackcrv, controlType = 'sub')

    for s in mTrackCrv.getShapes(asMeta=True):
        s.overrideEnabled = 1
        s.overrideDisplayType = 2    
    
def backup(self,ml_handles = None):
    try:
        _str_func = 'segment_handles'
        log_start(_str_func)
        
        mBlock = self.mBlock
        mRigNull = self.mRigNull
        _offset = self.v_offset
        _jointOrientation = self.d_orientation['str']
        
        if not ml_handles:
            raise ValueError("{0} | ml_handles required".format(_str_func))
    except Exception as err:cgmGEN.cgmExceptCB(Exception,err,localDat=vars())
    
    
def settings(self,settingsPlace = None,ml_targets = None, mPrerigNull = None):
    try:
        _str_func = 'rp'
        log_start(_str_func)
        log.debug("|{0}| >> settings: {1}...".format(_str_func,settingsPlace))
        
        if not ml_targets:
            ml_targets = self.msgList_get('prerigHandles')
        
        mBlock = self
        
        if self.hasAttr('jointRadius'):
            v_offset = self.jointRadius
            
        else:
            v_offset = self.atUtils('get_shapeOffset')
        
        if self.getEnumValueString('rigSetup') == 'digit':
            v_offset = v_offset * .5

        _jointOrientation = self.atUtils('get_baseJointOrientation')
        
        if settingsPlace == None:
            settingsPlace = self.getEnumValueString('settingsPlace')
        
        if settingsPlace == 'cog':
            return

        if settingsPlace in ['start','end']:
            mMesh_tmp =  self.atUtils('get_castMesh')
            str_meshShape = mMesh_tmp.getShapes()[0]
            
            idx_start, idx_end = self.atUtils('get_handleIndices')
            
            if settingsPlace == 'start':
                _mTar = ml_targets[idx_start]
            else:
                _mTar = ml_targets[idx_end]#self.msgList_get('formHandles')[-1]
                """
                mIKOrientHandle = self.getMessageAsMeta('ikOrientHandle')
                if mIKOrientHandle:
                    _mTar = mIKOrientHandle
                else:
                    _mTar = ml_targets[-1]"""            
            
            d_directions = {'up':'y+','down':'y-','in':'x+','out':'x-'}
            
            str_settingsDirections = d_directions.get(self.getEnumValueString('settingsDirection'),'y+')
            
            pos = RAYS.get_cast_pos(_mTar.mNode,str_settingsDirections,shapes = str_meshShape)
            if not pos:
                log.warning(cgmGEN.logString_msg(_str_func, 'miscast | standard IK end'))
                pos = _mTar.getPositionByAxisDistance(str_settingsDirections,v_offset * 3)
                
            vec = MATH.get_vector_of_two_points(_mTar.p_position, pos)
            newPos = DIST.get_pos_by_vec_dist(pos,vec,v_offset * 3)
            
            _settingsSize = v_offset * 2.0
            
            mSettings = cgmMeta.validateObjArg(CURVES.create_fromName('gear',_settingsSize,
                                                                      '{0}+'.format(_jointOrientation[2]),
                                                                      baseSize=1.0),'cgmObject',setClass=True)

            #mSettings = _mTar.doCreateAt(setClass= 'cgmObject')
            
            mSettings.doSnapTo(_mTar.mNode)
            
            
            #mSettingsShape.p_position = newPos
            mSettings.p_position = newPos
            
            mMesh_tmp.delete()
            
            SNAP.aim_atPoint(mSettings.mNode,
                             _mTar.p_position,
                             aimAxis=_jointOrientation[0]+'+',
                             mode = 'vector',
                             vectorUp= _mTar.getAxisVector(_jointOrientation[0]+'-'))
            
            #mSettingsShape.parent = _mTar
            #CORERIG.match_orientation(mSettings.mNode, _mTar.mNode)
            
            #CORERIG.shapeParent_in_place(mSettings.mNode, mSettingsShape.mNode, False)
            
            mSettings.doStore('cgmName',self.p_nameBase)
            mSettings.doStore('cgmTypeModifier','settings')            
            mSettings.doStore('cgmType','shapeHelper')
            mSettings.doName()
            
            color(self, mSettings.mNode, controlType = 'sub')
            
            self.connectChildNode(mSettings,'settingsHelper','block')#Connect
            
            mSettings.doStore('handleTag','settings')            
            
            if mPrerigNull:
                mSettings.p_parent = mPrerigNull

        else:
            raise ValueError("Unknown settingsPlace: {1}".format(settingsPlace))
        
        return mSettings
    except Exception as err:cgmGEN.cgmExceptCB(Exception,err,localDat=vars())
    

#...for tracking to a curve
def attachHandleToCurve(mHandle,mCrv,mShape = None,parentTo=None,pct = None, blend = True):
    if not mHandle.getMessage('trackGroup'):
        mHandle.doGroup(True,True,asMeta=True,typeModifier = 'track',setClass='cgmObject')
        
    mTrackGroup = mHandle.trackGroup
    for mConst in mTrackGroup.getConstraintsTo(asMeta=1):
        mConst.delete()

    if not pct:
        
        param = CURVES.getUParamOnCurve(mHandle.mNode, mCrv.mNode)
        
        if not mShape:
            mShape = mCrv.getShapes(asMeta=1)[0]
        _minU = mShape.minValue
        _maxU = mShape.maxValue
        pct = MATH.get_normalized_parameter(_minU,_maxU,param)        

    mPointOnCurve = cgmMeta.asMeta(CURVES.create_pointOnInfoNode(mCrv.mNode,turnOnPercentage=1))
    
    
    if blend:
        mPlug = cgmMeta.cgmAttr(mHandle.mNode, 'param', attrType = 'float',
                                minValue = 0.0, maxValue = 1.0,#len(ml_jointHelpers)-1, 
                                #defaultValue = .5, initialValue = .5,
                                keyable = True, hidden = False)
        mPlug.value = pct
        mPlug.p_defaultValue = pct
                
        mPointOnCurve.doConnectIn('parameter',mPlug.p_combinedName)
    else:
        mPointOnCurve.parameter = pct
        
    mTrackLoc = mHandle.doLoc()
    mPointOnCurve.doConnectOut('position',"{0}.translate".format(mTrackLoc.mNode))

    mTrackLoc.p_parent = parentTo
    mTrackLoc.v=False
    mc.pointConstraint(mTrackLoc.mNode,mHandle.trackGroup.mNode,maintainOffset = False)           
    
    
def eyeOrb(self, mTarget, mStateNull, side='left', attr= 'eyeSize'):
    _str_func = 'eyeOrb'
    mNoTransformNull = self.noTransDefineNull
    _res = []
    
    #Bounding sphere ==================================================================
    log.debug(cgmGEN.logString_msg(_str_func,'blockVolume...'))
    mBlockVolume = mTarget.doCreateAt(setClass=1)

    mBlockVolume.doSnapTo(mTarget)
    mBlockVolume.p_parent = mStateNull        
    #mBlockVolume.tz = -.5
    #mBlockVolume.p_parent = False
    mBlockVolume.rename(side + 'BlockVolume')
    
    """
    #Mid driver ....
    log.debug(cgmGEN.logString_msg(_str_func,'midDriver...'))
    
    mMidDriver = mBlockVolume.doCreateAt(setClass=1)
    mMidDriver.rename('midDriver')
    mMidDriver.p_parent = mBlockVolume
    mMidDriver.dagLock()
    
    #Mid Group...
    log.debug(cgmGEN.logString_msg(_str_func,'midGroup...'))    
    mMidGroup = mMidDriver.doCreateAt(setClass=1)
    mMidGroup.rename(side + 'midGoup')
    mMidGroup.p_parent = mStateNull
    mc.parentConstraint(mMidDriver.mNode, mMidGroup.mNode)
    mMidGroup.dagLock()
    self.connectChildNode(mMidGroup.mNode,side+'MidDrivenDag','module')    
    """
    
    CORERIG.copy_pivot(mBlockVolume.mNode,mTarget.mNode)
    
    
    """
    #Create Pivot =====================================================================================
    log.debug(cgmGEN.logString_msg(_str_func,'pivot...'))
    _irisPosHelper = CURVES.create_fromName('sphere', size = _size_base/3)
    mShape = cgmMeta.validateObjArg(_irisPosHelper)

    mShape.doSnapTo(self.mNode)
    mShape.p_parent = mMidGroup

    mShape.tz = self.baseSizeZ
    mShape.rz = 90    
    

    mIrisPosHelper = self.doCreateAt(setClass=True)
    mIrisPosHelper.p_position = mShape.p_position
    
    CORERIG.shapeParent_in_place(mIrisPosHelper.mNode, mShape.mNode,False)

    
    mPupilTrackDriver = mIrisPosHelper.doCreateAt(setClass=1)
    mPupilTrackDriver.rename('eyeTrackDriver')
    
    mIrisPosHelper.p_parent = mStateNull
    mIrisPosHelper.rename('irisPos_defineHandle')

    self.connectChildNode(mIrisPosHelper.mNode,'irisPosHelper','module')
    mHandleFactory.color(mIrisPosHelper.mNode,controlType='sub')
    
    ml_handles.append(mIrisPosHelper)    
    mPupilTrackDriver.p_parent = mIrisPosHelper#...parent our tracker to the orient handle    
    """

    #Bounding sphere ==================================================================
    _bb_shape = mc.sphere(axis=[0,0,1],ch=0,radius=.5,sections=6,spans=8)#[0]
    mBBShape = cgmMeta.validateObjArg(_bb_shape, 'cgmObject',setClass=True)
    for mShape in mBBShape.getShapes(asMeta=1):
        mShape.overrideEnabled = 1
        mShape.overrideDisplayType = 2
        
    mBBShape.doSnapTo(mTarget)
    mBBShape.p_parent = mBlockVolume#mDefineNull    
    
    mBBShape.tz = -.5
    
    CORERIG.colorControl(mBBShape.mNode,side,controlType='sub',transparent = True)
    
    #mBBShape.setAttrFlags()
    
    mBBShape.doStore('cgmName', mTarget)
    mBBShape.doStore('cgmType','bbVisualize')
    mBBShape.doName()    
    
    mTarget.connectChildNode(mBBShape.mNode,'bbHelper')
    

    #EyeControl -----------------------------------------------------
    mEyeDag = mBBShape.doCreateAt()
    mEyeDag = cgmMeta.validateObjArg(mEyeDag,'cgmControl',setClass=True)
    mEyeDag.doStore('cgmName', mTarget)
    mEyeDag.doStore('cgmType','eyeHelper')
    mEyeDag.doName()
    
    _str_capFirst = side[0].capitalize()
    mEyeDag.doStore('handleTag',"{0}_eyeHelper".format(_str_capFirst))
    
    _res.append(mEyeDag)
    
    mEndLoc = mTarget.doCreateAt()
    mEndLoc.rename('{0}_endLoc'.format(mTarget.mNode))
    mEndLoc.p_parent = mEyeDag
    
    mEyeDag.p_parent = mBlockVolume#mDefineNull    
    mBBShape.p_parent = mEyeDag
    
    mTarget.connectChildNode(mEyeDag.mNode,side + 'EyeHelper')        
        
            
    str_meshShape = mBBShape.getShapes()[0]
    ml_curves = []
    for i,k in enumerate([6.5,6]):
        _crv = mc.duplicateCurve("{0}.{2}[{1}]".format(str_meshShape,k,'u'), ch = 1, rn = 0, local = 0)[0]
        #mCrv = cgmMeta.validateObjArg(_crv, 'cgmObject',setClass=True)
        #mCrv.p_parent = mNoTransformNull
        color(self,_crv,side)
        CORERIG.shapeParent_in_place(mEyeDag.mNode,_crv,False )
        
        #mCrv.rename("eye_knot_{0}_approx".format(i))
        #for mShape in mCrv.getShapes(asMeta=1):
            #mShape.overrideEnabled = 1
            #mShape.overrideDisplayType = 2
        #mCrv.dagLock()
        
    """
    #SurfaceTrackSphere ==========================================================
    log.debug(cgmGEN.logString_msg(_str_func,'surface...'))
    mSurface = mBBShape.doDuplicate(po=False)
    mSurface.rename('TrackSurface')
    mSurface.v=0
    
    self.connectChildNode(mSurface.mNode,'trackSurface')
        
    """
    #Pupil/Iris =====================================================================
    log.debug(cgmGEN.logString_msg(_str_func,'Iris/pupil...'))

    _size_width = self.getMayaAttr(attr)[0][0]
    for k in ['pupil','iris']:
        _shape = CURVES.create_fromName('circle', 1.0, baseSize=1.0)
        mHelper = cgmMeta.validateObjArg(_shape, 'cgmControl',setClass=True)
        mHelper.doSnapTo(mTarget)
        color(self,mHelper.mNode,side, controlType='sub')
        #ml_handles.append(mHelper)
        mHelper.rename("{0}_visualize".format(k))
        mHelper.p_parent = mEndLoc
        mHelper.doStore('handleTag',"{0}_{1}Helper".format(_str_capFirst, k))
        
        _res.append(mHelper)
        
        
        if k == 'pupil':
            _sizeUse = _size_width * .03
            self.doConnectOut('pupilDepth', "{0}.tz".format(mHelper.mNode))
            
            #mHelper.p_position = mTarget.getPositionByAxisDistance('z-', _size_width * .01)        
            
        else:
            _sizeUse = _size_width * .05
            self.doConnectOut('irisDepth', "{0}.tz".format(mHelper.mNode))
        
        mHelper.setAttrFlags(['rotate','translate','sz'])
            
        mHelper.sx = _sizeUse        
        mHelper.sy = _sizeUse        

        self.connectChildNode(mHelper.mNode,'{0}Helper'.format(k))

        if k == 'pupil':
            _surf = mc.planarSrf(mHelper.mNode,ch=1, d=3, ko=0, tol = .01, rn = 0, po = 0,
                                 name = "{0}_approx".format(k))
            mc.reverseSurface(_surf[0])
            mSurf = cgmMeta.validateObjArg(_surf[0], 'cgmObject',setClass=True)

        else:
            _surf =  mc.loft([mHelper.mNode,_res[-2].mNode], o = True, d = 3, po = 0,ch=1,
                             name = "{0}_approx".format(k))            
            mSurf = cgmMeta.validateObjArg(_surf[0], 'cgmObject',setClass=True)
        
        if k == 'iris':
            CORERIG.colorControl(mSurf.mNode,side,'sub',transparent = True)
        else:
            CORERIG.colorControl(mSurf.mNode,side,'main',transparent=True)
            
        mSurf.p_parent = mNoTransformNull
        mSurf.dagLock()
        mSurf.overrideEnabled = 1
        mSurf.overrideDisplayType = 2
        for mShape in mSurf.getShapes(asMeta=1):
            mShape.overrideEnabled = 1
            mShape.overrideDisplayType = 2
    self.doConnectOut(attr, "{0}.scale".format(mBlockVolume.mNode))
    
    return _res


def attachToCurve(mHandle,mCrv,mShape = None,parentTo=None,pct = None, blend = True, trackLink = 'trackGroup'):
    if not mHandle.getMessage(trackLink):
        mHandle.doGroup(True,True,asMeta=True,typeModifier = 'track',setClass='cgmObject')
        
    mTrackGroup = mHandle.getMessageAsMeta(trackLink)
    for mConst in mTrackGroup.getConstraintsTo(asMeta=1):
        mConst.delete()
    
    if not pct:
        
        param = CURVES.getUParamOnCurve(mHandle.mNode, mCrv.mNode)
        
        if not mShape:
            mShape = mCrv.getShapes(asMeta=1)[0]
        _minU = mShape.minValue
        _maxU = mShape.maxValue
        pct = MATH.get_normalized_parameter(_minU,_maxU,param)        

    mPointOnCurve = cgmMeta.asMeta(CURVES.create_pointOnInfoNode(mCrv.mNode,turnOnPercentage=1))
    
    
    if blend:
        mPlug = cgmMeta.cgmAttr(mHandle.mNode, 'param', attrType = 'float',
                                minValue = 0.0, maxValue = 1.0,#len(ml_jointHelpers)-1, 
                                #defaultValue = .5, initialValue = .5,
                                keyable = True, hidden = False)
        mPlug.value = pct
        mPlug.p_defaultValue = pct
                
        mPointOnCurve.doConnectIn('parameter',mPlug.p_combinedName)
    else:
        mPointOnCurve.parameter = pct
        
    mTrackLoc = mHandle.doLoc()
    mPointOnCurve.doConnectOut('position',"{0}.translate".format(mTrackLoc.mNode))
    
    mHandle.doStore('trackCurve', mCrv)

    mTrackLoc.p_parent = parentTo
    mTrackLoc.v=False
    mc.pointConstraint(mTrackLoc.mNode,mTrackGroup .mNode,maintainOffset = False)     