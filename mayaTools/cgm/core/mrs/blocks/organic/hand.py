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
import Red9.core.Red9_AnimationUtils as r9Anim

# From cgm ==============================================================
from cgm.core import cgm_Meta as cgmMeta
import cgm.core.cgm_General as cgmGEN

from cgm.core.lib import curve_Utils as CURVES
from cgm.core.lib import rigging_utils as CORERIG
import cgm.core.classes.NodeFactory as NODEFACTORY
from cgm.core.lib import snap_utils as SNAP
from cgm.core.lib import attribute_utils as ATTR
import cgm.core.lib.math_utils as MATH

import cgm.core.lib.distance_utils as DIST
import cgm.core.lib.shared_data as CORESHARE
import cgm.core.rig.create_utils as RIGCREATE
import cgm.core.rig.constraint_utils as RIGCONSTRAINT
import cgm.core.lib.transform_utils as TRANS
import cgm.core.cgmPy.validateArgs as VALID
import cgm.core.rig.joint_utils as JOINTS
import cgm.core.lib.list_utils as LISTS
import cgm.core.mrs.lib.shared_dat as BLOCKSHARE
import cgm.core.mrs.lib.ModuleControlFactory as MODULECONTROL
import cgm.core.mrs.lib.block_utils as BLOCKUTILS
import cgm.core.mrs.lib.builder_utils as BUILDERUTILS
import cgm.core.lib.locator_utils as LOC
#=============================================================================================================
#>> Block Settings
#=============================================================================================================
__version__ = 'alpha.02.202019'
__autoTemplate__ = False
__component__ = False
__menuVisible__ = True
__baseSize__ = 10,10,10
__l_rigBuildOrder__ = []

#>>>Profiles ===================================================================================================
d_build_profiles = {'unityLow':{'default':{}},
                    'unityMed':{'default':{}},
                    'unityHigh':{'default':{}},
                    'feature':{'default':{}}}
d_block_profiles = {}

#>>>Attrs ========================================================================================================
l_attrsStandard = ['side',
                   'position',
                   'attachPoint',
                   #'baseDat',
                   'blockProfile',
                   'visMeasure',
                   'moduleTarget']

d_attrsToMake = {
    'definePose':'wide:relax',
    'numFinger':'int',
    'numThumb':'int',}

d_defaultSettings = {'version':__version__,
                     'definePose':'wide',
                     'numFinger':4,
                     'numThumb':1,}
                     #'baseDat':{'lever':[0,0,-1],'aim':[0,0,1],'up':[0,1,0],'end':[0,0,1]},}

d_wiring_prerig = {'msgLinks':['prerigNull']}
d_wiring_template = {'msgLinks':['templateNull'],
                     }


#=============================================================================================================
#>> Define
#=============================================================================================================
def mirror_self(self,primeAxis = 'Left'):
    _str_func = 'mirror_self'
    _idx_state = self.getState(False)
    
    log.debug("|{0}| >> define...".format(_str_func)+ '-'*80)
    ml_mirrorHandles = self.msgList_get('defineSubHandles')
    r9Anim.MirrorHierarchy().makeSymmetrical([mObj.mNode for mObj in ml_mirrorHandles],
                                             mode = '',primeAxis = primeAxis.capitalize() )    
    """
    if _idx_state > 0:
        log.debug("|{0}| >> template...".format(_str_func)+ '-'*80)
        ml_mirrorHandles = self.msgList_get('templateHandles')
        r9Anim.MirrorHierarchy().makeSymmetrical([mObj.mNode for mObj in ml_mirrorHandles],
                                                     mode = '',primeAxis = primeAxis.capitalize() )
    
    if _idx_state > 1:
        log.debug("|{0}| >> prerig...".format(_str_func)+ '-'*80)        
        ml_mirrorHandles = self.msgList_get('prerigHandles') + self.msgList_get('jointHandles')
        r9Anim.MirrorHierarchy().makeSymmetrical([mObj.mNode for mObj in ml_mirrorHandles],
                                                 mode = '',primeAxis = primeAxis.capitalize() )
        """


def define(self):
    try:
        _str_func = 'define'
        _short = self.mNode
        log.debug(cgmGEN.logString_start(_str_func))
        
        #Attributes =========================================================
        log.debug(cgmGEN.logString_sub(_str_func,'attributes'))
        
        ATTR.set_alias(_short,'sy','blockScale')    
        self.setAttrFlags(attrs=['sx','sz','sz'])
        self.doConnectOut('sy',['sx','sz'])
    
        _str_pose = self.getEnumValueString('definePose')
        #ATTR.set_min(_short, 'loftSplit', 1)
        #ATTR.set_min(_short, 'paramUprStart', 0.0)
        #ATTR.set_min(_short, 'paramLwrStart', 0.0)
        
        
        #Buffer our values...
        #_str_faceType = self.getEnumValueString('faceType')
        #_str_muzzleSetup = self.getEnumValueString('muzzleSetup')
        #_str_noseSetup = self.getEnumValueString('noseSetup')
        #_str_uprJawSetup = self.getEnumValueString('uprJawSetup')    
        #_str_lipsSetup = self.getEnumValueString('lipsSetup')
        #_str_teethSetup = self.getEnumValueString('teethSetup')
        #_str_cheekSetup = self.getEnumValueString('cheekSetup')
        #_str_tongueSetup = self.getEnumValueString('tongueSetup')
        
    
        #Cleaning =========================================================        
        _shapes = self.getShapes()
        if _shapes:
            log.debug(cgmGEN.logString_msg(_str_func,'Removing old shapes'))
            mc.delete(_shapes)
            defineNull = self.getMessage('defineNull')
            if defineNull:
                log.debug(cgmGEN.logString_msg(_str_func,'Removing old defineNull'))
                mc.delete(defineNull)
        ml_handles = []

        mNoTransformNull = self.getMessageAsMeta('noTransDefineNull')
        if mNoTransformNull:
            mNoTransformNull.delete()
        
        #rigBlock Handle ===========================================================
        log.debug(cgmGEN.logString_sub(_str_func,'RigBlock Handle'))
        
        _size = MATH.average(self.baseSize[1:])
        _crv = CURVES.create_fromName(name='locatorForm',#'axis3d',#'arrowsAxis', 
                                      direction = 'z+', size = _size/4)
        SNAP.go(_crv,self.mNode,)
        CORERIG.override_color(_crv, 'white')        
        CORERIG.shapeParent_in_place(self.mNode,_crv,False)
        mHandleFactory = self.asHandleFactory()
        self.addAttr('cgmColorLock',True,lock=True, hidden=True)
        mDefineNull = self.atUtils('stateNull_verify','define')
        mNoTransformNull = self.atUtils('noTransformNull_verify','define')
        
        #Bounding sphere ==================================================================
        log.debug(cgmGEN.logString_sub(_str_func,'bbVisualize'))        
        _bb_shape = CURVES.create_controlCurve(self.mNode,'cubeOpen', size = 1.0, sizeMode='fixed')
        mBBShape = cgmMeta.validateObjArg(_bb_shape, 'cgmObject',setClass=True)
        mBBShape.p_parent = mDefineNull    
        mBBShape.tz = .5
        #mBBShape.ty = .5
        
        CORERIG.copy_pivot(mBBShape.mNode,self.mNode)
        mHandleFactory.color(mBBShape.mNode,controlType='sub')
        mBBShape.setAttrFlags()
        
        mBBShape.doStore('cgmName', self)
        mBBShape.doStore('cgmType','bbVisualize')
        mBBShape.doName()    
        
        self.connectChildNode(mBBShape.mNode,'bbHelper')
        self.doConnectOut('baseSize', "{0}.scale".format(mBBShape.mNode))
        
        
        #Make our handles creation data =======================================================
        d_pairs = {}
        d_creation = {}
        l_order = []
        d_curves = {}
        d_curveCreation = {}
        d_toParent = {}
        
        log.debug(cgmGEN.logString_sub(_str_func,'handle data'))        
        
        
        _d_pairs = {'tipInner':'tipOuter',
                    #'thumbTipInner':'thumbTipOuter',
                    'thumbBaseInner':'thumbBaseOuter',
                    'thumbMidInner':'thumbMidOuter',
                    'thumbTipInner':'thumbTipOuter',
                    'midInner':'midOuter',
                    'baseInner':'baseOuter'
                    }
        
        d_pairs.update(_d_pairs)
        
        _d_scaleSpace = {
            'wide':{'tipInner':[.6,0,.8],
                    'tipOuter':[-.6,0,.8],
                    'tipMid':[0,.2,1],
                    'baseInner':[.4,0,-.95],
                    'baseOuter':[-.4,0,-.95],
                    'baseMid':[0,.2,-.95],
                    'midInner':[.5,0,0],
                    'midOuter':[-.5,0,0],
                    'midMid':[0,.2,0],
                    'thumbTipInner':[1,-.25,0],
                    'thumbBaseInner':[.5,-.1,-.95],
                    'thumbTipOuter':[-1,-.25,0],
                    'thumbBaseOuter':[-.5,-.1,-.95],                    
                    #'rollInner':[.4,0,.5],
                    #'rollOuter':[-.4,0,.5],
                    #'rollMid':[0,.2,.5],
                    },
            }
    
        _d = {#'thumbTipInner':{'color':'blueBright','tagOnly':1,'arrow':0,'jointLabel':1,'vectorLine':0},
              #'thumbBaseInner':{'color':'blueBright','tagOnly':1,'arrow':0,'jointLabel':1,'vectorLine':0},
              }
        
        for k in ['tip','base','roll','mid']:
            _d['{0}Inner'.format(k)] = {'color':'blueBright','tagOnly':1,'arrow':0,'jointLabel':1,'vectorLine':0}
            _d['{0}Outer'.format(k)] = {'color':'redBright','tagOnly':1,'arrow':0,'jointLabel':1,'vectorLine':0}
            _d['{0}Mid'.format(k)] = {'color':'yellow','tagOnly':1,'arrow':0,'jointLabel':1,'vectorLine':0}
            
        for k in ['thumbBase','thumbMid','thumbTip']:
            _d['{0}Inner'.format(k)] = {'color':'blueBright','tagOnly':1,'arrow':0,'jointLabel':1,'vectorLine':0}
            _d['{0}Outer'.format(k)] = {'color':'redBright','tagOnly':1,'arrow':0,'jointLabel':1,'vectorLine':0}
            
        
        for k,d in _d.iteritems():
            _v = _d_scaleSpace[_str_pose].get(k)
            if _v is not None:
                d['scaleSpace'] = _v
        
        d_creation.update(_d)
        l_order.extend(_d.keys())
        """
        l_order.extend(['tipInner','tipOuter','tipMid',
                        'baseInner','baseOuter','baseMid',
                        'midInner','midOuter','midMid',
                        'rollInner','rollOuter','rollMid',                        
                        'thumbTipInner','thumbBaseInner',
                        ])"""
        
        _d_curveCreation = {
            'tipLine':{'keys':['tipInner','tipMid','tipOuter'],'rebuild':1},
            'baseLine':{'keys':['baseInner','baseMid','baseOuter'],'rebuild':1},
            'midLine':{'keys':['midInner','midMid','midOuter'],'rebuild':1},
            'rollLine':{'keys':['rollInner','rollMid','rollOuter'],'rebuild':1},
            'outerLine':{'keys':['baseOuter','midOuter','rollOuter','tipOuter'],'rebuild':0},
            'innerLine':{'keys':['baseInner','midInner','rollInner','tipInner'],'rebuild':0},
            'innerThumbLine':{'keys':['thumbBaseInner','thumbMidInner','thumbTipInner'],'rebuild':0},
            'outerThumbLine':{'keys':['thumbBaseOuter','thumbMidOuter','thumbTipOuter'],'rebuild':0},
            
            
        }
        
        d_curveCreation.update(_d_curveCreation)
        
        #pprint.pprint(vars())
        
        
        #make em...============================================================
        log.debug(cgmGEN.logString_sub(_str_func,'Make handles'))        
        
        #self,l_order,d_definitions,baseSize,mParentNull = None, mScaleSpace = None, rotVecControl = False,blockUpVector = [0,1,0]
        md_res = self.UTILS.create_defineHandles(self, l_order, d_creation, _size / 10, mDefineNull, mBBShape)
    
        md_handles = md_res['md_handles']
        ml_handles = md_res['ml_handles']
        
        
        for k,p in d_toParent.iteritems():
            md_handles[k].p_parent = md_handles[p]
            
        log.debug(cgmGEN.logString_sub(_str_func,'curves'))        
        md_resCurves = self.UTILS.create_defineCurve(self, d_curveCreation, md_handles, mNoTransformNull)
        
        
        #Setup our mid 
        log.debug(cgmGEN.logString_sub(_str_func,'Position rolls'))                
        for t in ['Inner','Outer','Mid']:
            #Initial pos
            k = 'roll'+t
            mHandle = md_handles['roll'+t]
            #log.debug(mHandle)                
            
            mStart = md_handles['tip'+t]
            mEnd = md_handles['mid'+t]
            pos=  DIST.get_average_position([mStart.p_position,
                                             mEnd.p_position])
            mHandle.p_position = pos
            mGroup = mHandle.doGroup(True,True, asMeta=True,typeModifier = 'driver')
            mc.parentConstraint([mStart.mNode,mEnd.mNode],mGroup.mNode,maintainOffset=True)
            
        log.debug(cgmGEN.logString_sub(_str_func,'thumbMids'))                
        for t in ['Inner','Outer']:
            #Initial pos
            mHandle = md_handles['thumbMid'+t]
            #log.debug(mHandle)                
            
            mStart = md_handles['thumbBase'+t]
            mEnd = md_handles['thumbTip'+t]
            pos=  DIST.get_average_position([mStart.p_position,
                                             mEnd.p_position])
            mHandle.p_position = pos
            mGroup = mHandle.doGroup(True,True, asMeta=True,typeModifier = 'driver')
            mc.parentConstraint([mStart.mNode,mEnd.mNode],mGroup.mNode,maintainOffset=True)

        #mirror============================================================
        log.debug(cgmGEN.logString_sub(_str_func,'Mirror'))        
        
        idx_ctr = 0
        idx_side = 0
        d = {}
        
        for tag,mHandle in md_handles.iteritems():
            mHandle._verifyMirrorable()
            _center = True
            for p1,p2 in d_pairs.iteritems():
                if p1 == tag or p2 == tag:
                    _center = False
                    break
            if _center:
                log.debug("|{0}| >>  Center: {1}".format(_str_func,tag))    
                mHandle.mirrorSide = 0
                mHandle.mirrorIndex = idx_ctr
                idx_ctr +=1
            mHandle.mirrorAxis = "translateX,rotateY,rotateZ"
    
        #Self mirror wiring -------------------------------------------------------
        for k,m in d_pairs.iteritems():
            md_handles[k].mirrorSide = 1
            md_handles[m].mirrorSide = 2
            md_handles[k].mirrorIndex = idx_side
            md_handles[m].mirrorIndex = idx_side
            md_handles[k].doStore('mirrorHandle',md_handles[m])
            md_handles[m].doStore('mirrorHandle',md_handles[k])
            idx_side +=1
    
        #Curves -------------------------------------------------------------------------
        self.msgList_connect('defineHandles',ml_handles)#Connect    
        self.msgList_connect('defineSubHandles',ml_handles)#Connect
        self.msgList_connect('defineCurves',md_resCurves['ml_curves'])#Connect
        return        
        
 
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err,localDat=vars())        

#=============================================================================================================
#>> Template
#=============================================================================================================
def templateDelete(self):
    try:
        _str_func = 'templateDelete'
        log.debug("|{0}| >> ...".format(_str_func)+ '-'*80)
        log.debug("{0}".format(self))
        
        for k in ['end','rp','up','lever','aim']:
            mHandle = self.getMessageAsMeta("define{0}Helper".format(k.capitalize()))
            if mHandle:
                l_const = mHandle.getConstraintsTo()
                if l_const:
                    log.debug("currentConstraints...")
                    pos = mHandle.p_position
                    
                    for i,c in enumerate(l_const):
                        log.debug("{0} : {1}".format(i,c))
                        if not mc.ls(c,type='aimConstraint'):
                            mc.delete(c)
                    mHandle.p_position = pos
                if k == 'end':
                    self.baseSize = mHandle.width,mHandle.height,mHandle.length
                    
                        
                mHandle.v = True
                mHandle.template = False
                
            mHandle = self.getMessageAsMeta("vector{0}Helper".format(k.capitalize()))
            if mHandle:
                mHandle.template=False
            
        self.defineLoftMesh.v = True
        self.defineLoftMesh.template = False
        mNoTransformNull = self.getMessageAsMeta('noTransTemplateNull')
        if mNoTransformNull:
            mNoTransformNull.delete()
        
        
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err,localDat=vars())        

def template(self):
    try:
        _str_func = 'template'        
        _short = self.mNode
        _shape = self.getEnumValueString('basicShape')
        mHandleFactory = self.asHandleFactory(self)
        _shapeDirection = self.getEnumValueString('shapeDirection')
        _proxyShape = self.getEnumValueString('proxyShape')
        _side = self.UTILS.get_side(self)
        
        #If we have a loftList setup, we need to validate those attributes
        _int_shapers = self.numShapers
        
        
        _loftSetup = self.getEnumValueString('loftSetup')
 
        if _loftSetup == 'loftList':
            log.debug("loftList | attr validation"+ '-'*60)            
            l_loftList = ATTR.datList_get(_short,'loftList',enum=True)
            if len(l_loftList) > _int_shapers:
                log.debug("loftList | cleaning")
                _d_attrs = ATTR.get_sequentialAttrDict(_short, 'loftList')
                for i in range(len(l_loftList) - _int_shapers):
                    ATTR.delete(_short,_d_attrs[i+_int_shapers] )

            v = self.loftShape
            _enum_loftShape = BLOCKSHARE._d_attrsTo_make['loftShape']
            for i in range(_int_shapers):
                str_attr = "loftList_{0}".format(i)
                if not ATTR.has_attr(_short,str_attr):
                    self.addAttr(str_attr, v, attrType = 'enum',
                                 enumName= _enum_loftShape,
                                 keyable = False)
                else:
                    strValue = ATTR.get_enumValueString(_short,str_attr)
                    self.addAttr(str_attr,initialValue = v, attrType = 'enum', enumName= _enum_loftShape, keyable = False)
                    if strValue:
                        ATTR.set(_short,str_attr,strValue)

        #Create temple Null  ==================================================================================
        mTemplateNull = BLOCKUTILS.templateNull_verify(self)
        
        
        mGeoGroup = self.doCreateAt(setClass='cgmObject')
        mGeoGroup.rename("proxyGeo")
        mGeoGroup.parent = mTemplateNull
        #mGeoProxies.parent = mTemplateNull
    
        #_bb = DIST.get_bb_size(self.mNode,True)
    
        mGeoGroup.connectParentNode(self, 'rigBlock','proxyGeoGroup') 
        

        #BaseDat ==================================================================================
        self.defineLoftMesh.v = 0
        mRootUpHelper = self.vectorUpHelper    
        _mVectorAim = MATH.get_obj_vector(self.vectorEndHelper.mNode,asEuclid=True)
        _mVectorUp = MATH.get_obj_vector(mRootUpHelper.mNode,asEuclid=True)    
        mDefineEndObj = self.defineEndHelper
        mDefineUpObj = self.defineUpHelper
        
        _l_basePos = [self.p_position]
        
        md_vectorHandles = {}
        md_defineHandles = {}
        #Template our vectors
        for k in ['end','rp','up','aim']:
            mHandle = self.getMessageAsMeta("vector{0}Helper".format(k.capitalize()))    
            if mHandle:
                log.debug("define vector: {0} | {1}".format(k,mHandle))            
                mHandle.template=True
                md_vectorHandles[k] = mHandle
                
            mHandle = self.getMessageAsMeta("define{0}Helper".format(k.capitalize()))    
            if mHandle:
                log.debug("define handle: {0} | {1}".format(k,mHandle))                        
                md_defineHandles[k] = mHandle
                if k in ['end']:
                    mHandle.template = True        
                #if k in ['up']:
                    #mHandle.v=False
    
        mDefineLoftMesh = self.defineLoftMesh
        _v_range = DIST.get_distance_between_points(self.p_position,
                                                    mDefineEndObj.p_position)
        #_bb_axisBox = SNAPCALLS.get_axisBox_size(mDefineLoftMesh.mNode, _v_range, mark=False)
        _size_width = mDefineEndObj.width#...x width
        _size_height = mDefineEndObj.height#
        log.debug("|{0}| >> Generating more pos dat | bbHelper: {1} | range: {2}".format(_str_func,
                                                                                         mDefineLoftMesh.p_nameShort,
                                                                                         _v_range))
        _end = DIST.get_pos_by_vec_dist(_l_basePos[0], _mVectorAim, _v_range)
        _size_length = mDefineEndObj.length#DIST.get_distance_between_points(self.p_position, _end)
        _size_handle = _size_width * 1.25
        self.baseSize = [_size_width,_size_height,_size_length]
        log.debug("|{0}| >> baseSize: {1}".format(_str_func, self.baseSize))        
        
        
        _size = self.baseSize
        _proxyShape = self.getEnumValueString('proxyShape')
        if _proxyShape == 'shapers':
            log.debug("|{0}| >> Shapers ...".format(_str_func)+ '-'*60)
            
            log.debug("vectorAim: {0}".format(_mVectorAim))
    
            pos_self = self.p_position
            pos_aim = DIST.get_pos_by_vec_dist(pos_self, _mVectorAim, 5)        
            mNoTransformNull = BLOCKUTILS.noTransformNull_verify(self,'template')
            
            _shaperAim = self.getEnumValueString('shaperAim')
            
            #Get base dat =======================================================================            
            self.defineLoftMesh.template = True
        
            log.debug("|{0}| >> neck Base dat...".format(_str_func)+ '-'*40)
            mRootUpHelper = self.vectorUpHelper    
            _mVectorAim = MATH.get_obj_vector(self.vectorEndHelper.mNode,asEuclid=True)
            _mVectorUp = MATH.get_obj_vector(mRootUpHelper.mNode,'y+',asEuclid=True)    
            mDefineEndObj = self.defineEndHelper
            mDefineUpObj = self.defineUpHelper
        
            _v_range = DIST.get_distance_between_points(self.p_position,
                                                        mDefineEndObj.p_position)
            #_bb_axisBox = SNAPCALLS.get_axisBox_size(mDefineLoftMesh.mNode, _v_range, mark=False)
            log.debug("|{0}| >> Generating more pos dat | bbHelper: {1} | range: {2}".format(_str_func,
                                                                                             mDefineLoftMesh.p_nameShort,
                                                                                             _v_range))
            _end = DIST.get_pos_by_vec_dist(_l_basePos[0], _mVectorAim, _v_range)
            _size_handle = _size_width * 1.25
            _size_loft = MATH.get_greatest(_size_width,_size_height)
        
            #self.baseSize = [_size_width,_size_height,_size_length]
            _l_basePos.append(_end)
            log.debug("|{0}| >> baseSize: {1}".format(_str_func, self.baseSize))
        
        
            #Get base dat =============================================================================        
            _b_lever = False
            md_handles = {}
            ml_handles = []
            md_loftHandles = {}
            ml_loftHandles = []
        
            _loftShapeBase = self.getEnumValueString('loftShape')
            _loftShape = 'loft' + _loftShapeBase[0].capitalize() + ''.join(_loftShapeBase[1:])
            _loftSetup = self.getEnumValueString('loftSetup')
        
            cgmGEN.func_snapShot(vars())
        
        
            #if _loftSetup == 'default':
            md_handles,ml_handles,ml_shapers,ml_handles_chain = self.UTILS.template_segment(
            self,
            aShapers = 'numShapers',aSubShapers = 'numSubShapers',
            loftShape=_loftShape,l_basePos = _l_basePos, baseSize=_size_handle,
            orientHelperPlug='orientHelper',templateAim =  self.getEnumValueString('shapersAim'),
            sizeWidth = _size_width, sizeLoft=_size_loft,side = _side,
            mTemplateNull = mTemplateNull,mNoTransformNull = mNoTransformNull,
            mDefineEndObj=mDefineEndObj)
            
            mOrientHelper = self.getMessageAsMeta('orientHelper')
            mUpTrans = md_defineHandles['up'].doCreateAt(setClass = True)
            mUpTrans.p_parent = mOrientHelper.mNode                  
            
            #>>> Connections ================================================================================
            self.msgList_connect('templateHandles',[mObj.mNode for mObj in ml_handles_chain])
        
            #>>Loft Mesh ==================================================================================
            if self.numShapers:
                targets = [mObj.loftCurve.mNode for mObj in ml_shapers]
                self.msgList_connect('shaperHandles',[mObj.mNode for mObj in ml_shapers])
            else:
                targets = [mObj.loftCurve.mNode for mObj in ml_handles_chain]
        
        
        
            mMesh = self.atUtils('create_prerigLoftMesh',
                                 targets,
                                 mTemplateNull,
                                 'numShapers',                     
                                 'loftSplit',
                                 polyType='bezier',
                                 baseName = self.cgmName )
            mMesh.connectParentNode(self.mNode,'handle','proxyHelper')
            self.msgList_connect('proxyMeshGeo',[mMesh])
            mHandleFactory.color(mMesh.mNode,_side,'sub',transparent=True)
        
            mNoTransformNull.v = False
            
            
            SNAP.aim_atPoint(md_handles['end'].mNode, position=_l_basePos[0], aimAxis="z-", mode='vector', vectorUp=_mVectorUp)
       
            SNAP.aim_atPoint(md_handles['start'].mNode, position=_l_basePos[-1], aimAxis="z+", mode='vector', vectorUp=_mVectorUp)
        
            #Constrain the define end to the end of the template handles
            #mc.pointConstraint(md_handles['start'].mNode,mDefineEndObj.mNode,maintainOffset=False)
            mc.scaleConstraint([md_handles['end'].mNode,md_handles['start'].mNode],mDefineEndObj.mNode,maintainOffset=True)            
            
            
            #mc.pointConstraint(mUpTrans.mNode,
            #                   md_defineHandles['up'].mNode,
            #                   maintainOffset = True)                    
            
        else:
            #Base shape ========================================================================================
            log.debug("|{0}| >> Shapers ...".format(_str_func)+ '-'*60)
            _l_basePos.append(_end)
            
            if _shape in ['cube']:
                _shapeDirection = 'z+'
            elif _shape in ['semiSphere']:
                _shapeDirection = 'y+'
            
            if _shape in ['circle','square']:
                _size = [v for v in self.baseSize[:-1]] + [None]
                _shapeDirection = 'y+'
            elif _shape in ['pyramid','semiSphere']:
                _size =  [_size_width,_size_height,_size_length]
            else:
                _size =  [_size_width,_size_length,_size_height]
        
            _crv = CURVES.create_controlCurve(self.mNode, shape=_shape,
                                              direction = _shapeDirection,
                                              sizeMode = 'fixed', size =_size)
        
            mHandle = cgmMeta.validateObjArg(_crv,'cgmObject',setClass=True)
            mHandle.p_parent = mTemplateNull
            _pos_mid = DIST.get_average_position(_l_basePos)
            if _shape in ['pyramid','semiSphere','circle','square']:
                mHandle.p_position = _l_basePos[0]
            else:
                mHandle.p_position = _pos_mid
                
            #if _shape in ['circle']:
            #    SNAP.aim_atPoint(mHandle.mNode, _l_basePos[-1], "z+",'y-','vector', _mVectorUp)
            #else:
            SNAP.aim_atPoint(mHandle.mNode, _l_basePos[-1], "y",'z-','vector', _mVectorUp)
        
            mHandle.doStore('cgmNameModifier','main')
            mHandle.doStore('cgmType','handle')
            mHandleFactory.copyBlockNameTags(mHandle)
        
        
            CORERIG.colorControl(mHandle.mNode,_side,'main',transparent = False) 
        
            mHandleFactory.setHandle(mHandle)
        
            #self.msgList_connect('templateHandles',[mHandle.mNode])
        
            #Proxy geo ==================================================================================
            _proxy = CORERIG.create_proxyGeo(_proxyShape, [_size_width,_size_length,_size_height], 'y+')
            mProxy = cgmMeta.validateObjArg(_proxy[0], mType = 'cgmObject',setClass=True)
            
            mProxy.doSnapTo(mHandle.mNode)
            if _shape in ['pyramid','semiSphere','circle','square']:
                mProxy.p_position = _pos_mid
            #mProxy.p_position = _pos_mid
            #NAP.aim_atPoint(mHandle.mNode, _l_basePos[-1], "y",'z-','vector', _mVectorUp)
            
            #SNAPCALLS.snap(mProxy.mNode,mHandle.mNode, objPivot='boundingBox',objMode='y-',targetPivot='boundingBox',targetMode='y-')
        
            if mHandle.hasAttr('cgmName'):
                ATTR.copy_to(mHandle.mNode,'cgmName',mProxy.mNode,driven='target')        
            mProxy.doStore('cgmType','proxyHelper')
            self.msgList_connect('proxyMeshGeo',[mProxy])
            
            mProxy.doName()    
        
            mProxy.p_parent = mGeoGroup
        
        
            #CORERIG.colorControl(mProxy.mNode,_side,'sub',transparent=True)
            mHandleFactory.color(mProxy.mNode,_side,'sub',transparent=True)
        
            mProxy.connectParentNode(mHandle.mNode,'handle','proxyHelper')        
            mProxy.connectParentNode(self.mNode,'proxyHelper')        
            mProxy.connectParentNode(self.mNode,'handle','proxyHelper')        
            
            self.msgList_connect('templateHandles',[mHandle.mNode,mProxy.mNode])
        
            attr = 'proxy'
            self.addAttr(attr,enumName = 'off:lock:on', defaultValue = 1, attrType = 'enum',keyable = False,hidden = False)
            NODEFACTORY.argsToNodes("%s.%sVis = if %s.%s > 0"%(_short,attr,_short,attr)).doBuild()
            NODEFACTORY.argsToNodes("%s.%sLock = if %s.%s == 2:0 else 2"%(_short,attr,_short,attr)).doBuild()
                    
            #mProxy.resetAttrs()
            
            mGeoGroup.overrideEnabled = 1
            ATTR.connect("{0}.proxyVis".format(_short),"{0}.visibility".format(mGeoGroup.mNode) )
            ATTR.connect("{0}.proxyLock".format(_short),"{0}.overrideDisplayType".format(mGeoGroup.mNode) )        
            for mShape in mProxy.getShapes(asMeta=1):
                str_shape = mShape.mNode
                mShape.overrideEnabled = 0
                ATTR.connect("{0}.proxyLock".format(_short),"{0}.overrideDisplayTypes".format(str_shape) )
                ATTR.connect("{0}.proxyLock".format(_short),"{0}.overrideDisplayType".format(str_shape) )        
            
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err,localDat=vars())        
        
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
        _shape = self.getEnumValueString('basicShape')
        
        _side = self.atUtils('get_side')
            
        self.atUtils('module_verify')
    
        ml_templateHandles = self.msgList_get('templateHandles')
        
        _proxyShape = self.getEnumValueString('proxyShape')
        b_shapers = False
        if _proxyShape == 'shapers':
            log.debug("|{0}| >> Shapers ...".format(_str_func)+ '-'*60)
            mMain = self
            b_shapers = True
            pos_shaperBase = ml_templateHandles[0].p_position
        else:
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
            if b_shapers:
                mJointHelper.p_parent = mPrerigNull
                mJointHelper.p_position = pos_shaperBase
            
        
        #Helpers=====================================================================================
        #self.msgList_connect('prerigHandles',[self.mNode])
        
        if self.addPivot:
            mPivot = mHandleFactory.addPivotSetupHelper()
            mPivot.p_parent = mPrerigNull
            ml_templateHandles[0].connectChildNode(mPivot,'pivotHelper')

            if _shape in ['pyramid','semiSphere','circle','square']:
                mPivot.p_position = self.p_position
            elif b_shapers:mPivot.p_position = pos_shaperBase
                
        
        if self.addScalePivot:
            mScalePivot = mHandleFactory.addScalePivotHelper()
            mScalePivot.p_parent = mPrerigNull
            if b_shapers:mScalePivot.p_position = pos_shaperBase
            
            
        if self.addCog:
            mCog = mHandleFactory.addCogHelper()
            mCog.p_parent = mPrerigNull
            if b_shapers:mCog.p_position = pos_shaperBase
            
        if b_shapers:
            mc.parentConstraint([ml_templateHandles[0].mNode],mPrerigNull.mNode, maintainOffset = True)
            mc.scaleConstraint([ml_templateHandles[0].mNode],mPrerigNull.mNode, maintainOffset = True)
        else:
            mc.parentConstraint([mMain.mNode],mPrerigNull.mNode, maintainOffset = True)
            mc.scaleConstraint([mMain.mNode],mPrerigNull.mNode, maintainOffset = True)
        
        return

    except Exception,err:cgmGEN.cgmExceptCB(Exception,err,localDat=vars())        



def prerigDelete(self):
    #if self.getMessage('templateLoftMesh'):
    #    mTemplateLoft = self.getMessage('templateLoftMesh',asMeta=True)[0]
    #    for s in mTemplateLoft.getShapes(asMeta=True):
    #        s.overrideDisplayType = 2     
    
    #if self.getMessage('noTransformNull'):
    #    mc.delete(self.getMessage('noTransformNull'))
    #return BLOCKUTILS.prerig_delete(self,templateHandles=True)
    return True

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
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err,localDat=vars())        


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
    
    
    
    #>> If skeletons there, delete ------------------------------------------------------------------------ 
    _bfr = mRigNull.msgList_get('moduleJoints',asMeta=True)
    if _bfr:
        log.debug("|{0}| >> Joints detected...".format(_str_func))            
        if forceNew:
            log.debug("|{0}| >> force new...".format(_str_func))                            
            mc.delete([mObj.mNode for mObj in _bfr])
        else:
            return _bfr
        
    ml_templateHandles = self.msgList_get('templateHandles')
    
    ml_jointHelpers = self.msgList_get('jointHelpers')
    mJoint = ml_jointHelpers[0].doCreateAt('joint')
    JOINTS.freezeOrientation(mJoint)

    _l_namesToUse = self.atUtils('skeleton_getNameDicts',False, 1)
    for k,v in _l_namesToUse[0].iteritems():
        mJoint.doStore(k,v)
        mJoint.doName()
    mJoint.doName()
    
    #if self.getMayaAttr('cgmName'):
        #self.copyAttrTo('cgmName',mJoint.mNode,'cgmName',driven='target')
    #else:
        #self.copyAttrTo('blockType',mJoint.mNode,'cgmName',driven='target')
        
    if mModule.getMayaAttr('cgmDirection'):
        mModule.copyAttrTo('cgmDirection',mJoint.mNode,'cgmDirection',driven='target')
    if mModule.getMayaAttr('cgmPosition'):
        mModule.copyAttrTo('cgmPosition',mJoint.mNode,'cgmPosition',driven='target')
        
    mJoint.doName()

    mRigNull.msgList_connect('moduleJoints', [mJoint])
    
    self.atBlockUtils('skeleton_connectToParent')
    
    mJoint.rotateOrder = 5
    
    mJoint.displayLocalAxis = 1
    mJoint.radius = self.atUtils('get_shapeOffset') 
    
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
@cgmGEN.Timer
def rig_dataBuffer(self):
    try:
        _short = self.d_block['shortName']
        _str_func = 'rig_dataBuffer'
        log.debug("|{0}| >> ...".format(_str_func)+cgmGEN._str_hardBreak)
        log.debug(self)
        
        mBlock = self.mBlock
        mModule = self.mModule
        mRigNull = self.mRigNull
        mPrerigNull = mBlock.prerigNull
        ml_templateHandles = mBlock.msgList_get('templateHandles')
        self.ml_templateHandles=ml_templateHandles
        ml_prerigHandles = mBlock.msgList_get('prerigHandles')
        
        ml_handleJoints = mPrerigNull.msgList_get('handleJoints')
        mMasterNull = self.d_module['mMasterNull']
        
        self.mRootTemplateHandle = ml_templateHandles[0]
        log.debug(cgmGEN._str_subLine)
        
        #Offset ============================================================================    
        self.v_offset = self.mPuppet.atUtils('get_shapeOffset')

        log.debug("|{0}| >> self.v_offset: {1}".format(_str_func,self.v_offset))    
        
        
        #DynParents =============================================================================
        self.UTILS.get_dynParentTargetsDat(self)
        
        #rotateOrder =============================================================================
        _str_orientation = self.d_orientation['str']
        
        self.rotateOrder = "{0}{1}{2}".format(_str_orientation[1],_str_orientation[2],_str_orientation[0])
        self.rotateOrderIK = "{2}{0}{1}".format(_str_orientation[0],_str_orientation[1],_str_orientation[2])
        
        log.debug("|{0}| >> rotateOrder | self.rotateOrder: {1}".format(_str_func,self.rotateOrder))
        log.debug("|{0}| >> rotateOrder | self.rotateOrderIK: {1}".format(_str_func,self.rotateOrderIK))
    
        log.debug(cgmGEN._str_subLine)

        log.debug(cgmGEN._str_subLine)    
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err,localDat=vars())        


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
    ml_jointHelpers = mBlock.msgList_get('jointHelpers')
    mHelper = ml_jointHelpers[0]
    mRigNull = self.mRigNull
    
    #Get our base size from the block
    _size = DIST.get_bb_size(mMainHandle.mNode,True,True)
    _side = BLOCKUTILS.get_side(self.mBlock)
    #_ikPos = mHelper.getPositionByAxisDistance(mBlock.getEnumValueString('axisAim'), _size *2)
    _short_module = self.mModule.mNode
    ml_joints = self.d_joints['ml_moduleJoints']
    mBlock_upVector = mBlock.getAxisVector('y+')
    _offset = self.v_offset
    
    pprint.pprint(vars())
    

    #Control ----------------------------------------------------------------------------------
    log.info("|{0}| >> Main control shape...".format(_str_func))
    _str_rotPivot = mBlock.getEnumValueString('rotPivotPlace')
    
    if _str_rotPivot == 'cog' and mBlock.addCog and mMainHandle.getMessage('cogHelper'):
        log.info("|{0}| >> Cog pivot setup... ".format(_str_func))    
        mControl = mMainHandle.cogHelper.doCreateAt()
    elif _str_rotPivot == 'jointHelper':
        mControl = mHelper.doCreateAt()        
    else:
        mControl = mMainHandle.doCreateAt()
        
    if mBlock.addScalePivot and mMainHandle.getMessage('scalePivotHelper'):
        log.info("|{0}| >> Scale Pivot setup...".format(_str_func))
        TRANS.scalePivot_set(mControl.mNode, mMainHandle.scalePivotHelper.p_position)
        
    #Shape -------------------------------------------------------------------------------------
    if mBlock.getEnumValueString('proxyShape') == 'shapers':
        ml_fkShapes = self.atBuilderUtils('shapes_fromCast',
                                          offset = _offset,
                                          mode = 'singleCurve')#limbHandle
        CORERIG.shapeParent_in_place(mControl,ml_fkShapes[0].mNode,False)
        
        
    else:
        CORERIG.shapeParent_in_place(mControl,mMainHandle.mNode,True)
    mControl = cgmMeta.validateObjArg(mControl,'cgmObject',setClass=True)
    ATTR.copy_to(_short_module,'cgmName',mControl.mNode,driven='target')
    mControl.doName()    
    
    CORERIG.colorControl(mControl.mNode,_side,'main')
    
    mRigNull.connectChildNode(mControl,'handle','rigNull')#Connect
    mRigNull.connectChildNode(mControl,'settings','rigNull')#Connect    
    
    #Aim=============================================================================================
    if mBlock.addAim:
        log.info("|{0}| >> Aim setup...".format(_str_func))  
        _vec_aim = MATH.get_obj_vector(mBlock.vectorAimHelper.mNode,asEuclid=True)    
        #_ikPos = DIST.get_pos_by_vec_dist(mControl.p_position, _vec_aim, mBlock.baseSize[2])
        _ikPos = mControl.getPositionByAxisDistance(mBlock.getEnumValueString('axisAim'), _size *2)
        
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
        #ml_controlsAll = self.atBuilderUtils('register_mirrorIndices', ml_controlsAll)
        mRigNull.msgList_connect('controlsAll',ml_controlsAll)
        mRigNull.moduleSet.extend(ml_controlsAll)
        
        log.info("|{0}| >> Time >> = {1} seconds".format(_str_func, "%0.3f"%(time.clock()-_start)))                
        
        
        
        return 
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err)

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
        cgmGEN.cgmExceptCB(Exception,err,msg=vars())
    
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
    if mBlock.spaceSwitch_direct:
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
    mBlock.blockState = 'rig'
    mBlock.UTILS.set_blockNullTemplateState(mBlock)
    self.UTILS.rigNodes_store(self)




def create_simpleMesh(self, deleteHistory = True, cap=True, skin = False, parent=False):
    try:
        _str_func = 'create_simpleMesh'
        log.debug("|{0}| >>  ".format(_str_func)+ '-'*80)
        log.debug("{0}".format(self))
        
        if skin:
            mModuleTarget = self.getMessage('moduleTarget',asMeta=True)
            if not mModuleTarget:
                return log.error("|{0}| >> Must have moduleTarget for skining mode".format(_str_func))
            mModuleTarget = mModuleTarget[0]
            ml_moduleJoints = mModuleTarget.rigNull.msgList_get('moduleJoints')
            if not ml_moduleJoints:
                return log.error("|{0}| >> Must have moduleJoints for skining mode".format(_str_func))        
        
        
        
        ml_geo = self.msgList_get('proxyMeshGeo')
        ml_proxy = []
        if ml_geo:
            for i,mGeo in enumerate(ml_geo):
                log.debug("|{0}| >> proxyMesh creation from: {1}".format(_str_func,mGeo))                        
                if mGeo.getMayaType() == 'nurbsSurface':
                    mMesh = RIGCREATE.get_meshFromNurbs(self.proxyHelper,
                                                        mode = 'general',
                                                        uNumber = self.loftSplit, vNumber=self.loftSides)
                else:
                    mMesh = mGeo.doDuplicate(po=False)
                    #mMesh.p_parent = False
                    #mDup = mBlock.proxyHelper.doDuplicate(po=False)
                mMesh.rename("{0}_{1}_mesh".format(self.p_nameBase,i))
                #mDup.inheritsTransform = True
                ml_proxy.append(mMesh)        
        
        
            #mDup = self.proxyHelper.doDuplicate(po=False)
            str_setup = self.getEnumValueString('proxyShape')
            if str_setup == 'shapers':
                d_kws = {}
                mMesh = self.UTILS.create_simpleLoftMesh(self,divisions=5)[0]
                ml_proxy = [mMesh]
            else:
                for i,mGeo in enumerate(ml_geo):
                    log.debug("|{0}| >> proxyMesh creation from: {1}".format(_str_func,mGeo))
                    if mGeo.getMayaType() == 'nurbsSurface':
                        d_kws = {'mode':'general',
                                 'uNumber':self.loftSplit,
                                 'vNumber':self.loftSides,
                                 }
                        mMesh = RIGCREATE.get_meshFromNurbs(self.proxyHelper,**d_kws)
                    else:
                        mMesh = mGeo.doDuplicate(po=False)
                    ml_proxy.append(mMesh)
                    
            for i,mMesh in enumerate(ml_proxy):
                if parent and skin:
                    mMesh.p_parent=parent
                
                if skin:
                    mc.skinCluster ([mJnt.mNode for mJnt in ml_moduleJoints],
                                    mMesh.mNode,
                                    tsb=True,
                                    bm=1,
                                    maximumInfluences = 3,
                                    normalizeWeights = 1, dropoffRate=10)            
                mMesh.rename('{0}_{1}_puppetmesh_geo'.format(self.p_nameBase,i))
        return ml_proxy
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err,localDat=vars())        

def build_proxyMesh(self, forceNew = True, puppetMeshMode = False,**kws):
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
    if puppetMeshMode:
        _bfr = mRigNull.msgList_get('puppetProxyMesh',asMeta=True)
        if _bfr:
            log.debug("|{0}| >> puppetProxyMesh detected...".format(_str_func))            
            if forceNew:
                log.debug("|{0}| >> force new...".format(_str_func))                            
                mc.delete([mObj.mNode for mObj in _bfr])
            else:
                return _bfr        
            
    _bfr = mRigNull.msgList_get('proxyMesh',asMeta=True)
    if _bfr:
        log.debug("|{0}| >> proxyMesh detected...".format(_str_func))            
        if forceNew:
            log.debug("|{0}| >> force new...".format(_str_func))                            
            mc.delete([mObj.mNode for mObj in _bfr])
        else:
            return _bfr
      
    #>> Build bbProxy -----------------------------------------------------------------------------
    ml_geo = mBlock.msgList_get('proxyMeshGeo')
    ml_proxy = []
    if ml_geo:
        reload(RIGCREATE)
        for i,mGeo in enumerate(ml_geo):
            log.debug("|{0}| >> proxyMesh creation from: {1}".format(_str_func,mGeo))                        
            if mGeo.getMayaType() == 'nurbsSurface':
                mMesh = RIGCREATE.get_meshFromNurbs(mBlock.proxyHelper,
                                                    mode = 'general',
                                                    uNumber = mBlock.loftSplit, vNumber=mBlock.loftSides)
            else:
                mMesh = mGeo.doDuplicate(po=False)
                #mMesh.p_parent = False
                #mDup = mBlock.proxyHelper.doDuplicate(po=False)
            mMesh.p_parent = mRigNull.msgList_get('rigJoints')[0]
            mMesh.rename("{0}_{1}_mesh".format(mBlock.p_nameBase,i))
            #mDup.inheritsTransform = True
            ml_proxy.append(mMesh)
    
    
    #Connect to setup ------------------------------------------------------------------------------------
    mPuppetSettings = self.d_module['mMasterControl'].controlSettings
    _side = BLOCKUTILS.get_side(self.mBlock)
    
    if puppetMeshMode:
        log.debug("|{0}| >> puppetMesh setup... ".format(_str_func))
        ml_moduleJoints = mRigNull.msgList_get('moduleJoints')
    
        for i,mGeo in enumerate(ml_proxy):
            log.debug("|{0}| >> geo: {1}...".format(_str_func,mGeo))
            CORERIG.color_mesh(mGeo.mNode,'puppetmesh')
            
            mc.makeIdentity(mGeo.mNode, apply = True, t=1, r=1,s=1,n=0,pn=1)
            
            mGeo.p_parent = ml_moduleJoints[0]

        mRigNull.msgList_connect('puppetProxyMesh', ml_proxy)
        return ml_proxy    
    
    
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







 








