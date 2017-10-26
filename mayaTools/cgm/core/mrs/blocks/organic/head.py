"""
------------------------------------------
cgm.core.mrs.blocks.simple.torso
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

from cgm.core.rigger import ModuleShapeCaster as mShapeCast

import cgm.core.cgmPy.os_Utils as cgmOS
import cgm.core.cgmPy.path_Utils as cgmPATH
import cgm.core.mrs.assets as MRSASSETS
path_assets = cgmPATH.Path(MRSASSETS.__file__).up().asFriendly()

import cgm.core.mrs.lib.ModuleControlFactory as MODULECONTROL
reload(MODULECONTROL)
from cgm.core.lib import curve_Utils as CURVES
from cgm.core.lib import rigging_utils as CORERIG
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

for m in DIST,POS,MATH,CONSTRAINT,LOC,BLOCKUTILS,BUILDERUTILS,CORERIG,RAYS,JOINT,RIGCONSTRAINT:
    reload(m)
    
# From cgm ==============================================================
from cgm.core import cgm_Meta as cgmMeta

#=============================================================================================================
#>> Block Settings
#=============================================================================================================
__version__ = 'alpha.08072017'
__autoTemplate__ = False

__dimensions = [15.2, 23.2, 19.7]

#These are our base dimensions. In this case it is for human
__dimensions_by_type = {'box':[22,22,22],
                        'human':[15.2, 23.2, 19.7]}

#>>>Attrs ----------------------------------------------------------------------------------------------------
_l_coreNames = ['head']

l_attrsStandard = ['side',
                   'position',
                   #'proxyType',
                   'hasRootJoint',
                   #'buildIK',
                   'baseNames',
                   'proxyShape',
                   'loftSides',
                   'loftDegree',
                   'loftSplit',
                   #'customStartOrientation',
                   'moduleTarget',]

d_attrsToMake = {'proxyShape':'cube:sphere:cylinder',
                 'proxyType':'base:geo',
                 'headType':'box:human:beast',
                 'headAim':'bool',
                 'headRotate':'double3',
                 'neckBuild':'bool',
                 'neckControls':'int',
                 'neckJoints':'int',
                 'neckIK':'bool'}

d_defaultSettings = {'version':__version__,
                     'baseSize':MATH.get_space_value(__dimensions[1]),
                     'headAim':True,
                     'headType':'human',
                     'neckBuild':True,
                     'neckControls': 1,
                     'loftSides': 10,
                     'loftSplit':4,
                     'loftDegree':'cubic',                     
                     'neckJoints':3,
                     'attachPoint':'base',
                     'neckIK':True,
                     'proxyShape':'cube',
                     'baseNames':['head','neck'],#...our datList values
                     'proxyType':'geo'}

#Skeletal stuff ------------------------------------------------------------------------------------------------
d_skeletonSetup = {'mode':'curveCast',
                   'targetsMode':'prerigHandles',
                   'helperUp':'z-',
                   'countAttr':'neckJoints',
                   'targets':'jointHelper'}

d_preferredAngles = {'head':[0,-10, 10]}#In terms of aim up out for orientation relative values, stored left, if right, it will invert
d_rotationOrders = {'head':'yxz'}

#=============================================================================================================
#>> Define
#=============================================================================================================
def define(self):
    _short = self.mNode
    
    ATTR.set_min(_short, 'neckControls', 1)
    ATTR.set_min(_short, 'loftSides', 3)
    ATTR.set_min(_short, 'loftSplit', 1)
    
    
#=============================================================================================================
#>> Template
#=============================================================================================================    
def templateDelete(self):
    return BLOCKUTILS.templateDelete(self,['orientHelper'])

is_template = BLOCKUTILS.is_template

  
def template(self):
    _str_func = 'template'
    
    _short = self.p_nameShort
    _baseNameAttrs = ATTR.datList_getAttrs(self.mNode,'baseNames')
    _l_baseNames = ATTR.datList_get(self.mNode, 'baseNames')
    _headType = self.getEnumValueString('headType')
    _dimensions = __dimensions_by_type.get(_headType,'human')
    
    _side = 'center'
    if self.getMayaAttr('side'):
        _side = self.getEnumValueString('side')
        
    self.scale = 1,1,1
    
    _size = self.baseSize
    _size_width = (_dimensions[1]/_size) * _dimensions[2]
    
    log.info("|{0}| >> [{1}] | headType: {2} |baseSize: {3} | side: {4} | dimensions: {5}".format(_str_func,_short,_headType,_size, _side, _dimensions))            

    #Create temple Null  ==================================================================================
    mTemplateNull = BLOCKUTILS.templateNull_verify(self)
    
    #Our main rigBlock shape =================================================================================
    mHandleFactory = self.asHandleFactory(self.mNode)
    
    _proxyType = self.proxyType
    
    #if _proxyType <= 1:
    mHandleFactory.rebuildSimple('cube', _size, shapeDirection = 'y+')
    
    #Size our base proxy shape ----------------------------------------------------------------
    mProxyBase = cgmMeta.validateObjArg( CORERIG.duplicate_shape( self.getShapes()[0] )[0] , 'cgmObject' )
    _factor = _dimensions[1]/_size
    _scale = [d * _factor for d in _dimensions]
    TRANS.scale_to_boundingBox(mProxyBase.mNode, _scale)
    CORERIG.shapeParent_in_place(self.mNode, mProxyBase.mNode, False, True)
    
    CORERIG.colorControl(self.mNode,_side,'main',transparent = True) 
    
    #Orient Helper ----------------------------------------------------------------------------------
    mOrientCurve = mHandleFactory.addOrientHelper(baseSize = _scale[0] * .7,
                                                  shapeDirection = 'z+',
                                                  setAttrs = {'rz':90,
                                                              'tz': _size * .8})
    self.copyAttrTo(_baseNameAttrs[1],mOrientCurve.mNode,'cgmName',driven='target')
    mOrientCurve.doName()    
    mOrientCurve.setAttrFlags(['rz','rx','translate','scale','v'])
    mOrientCurve.p_parent = mTemplateNull
    CORERIG.colorControl(mOrientCurve.mNode,_side,'sub')    
      
    #Proxies ==============================================================================
    ml_proxies = []        
    log.info("|{0}| >> Geo proxyType...".format(_str_func,))     
    
    
    if _proxyType == 0:
        _res = build_prerigMesh(self)
        mProxy = cgmMeta.validateObjArg(_res[0],'cgmObject',setClass=True)
        mProxy.doSnapTo(self.mNode)       
        TRANS.scale_to_boundingBox(mProxy.mNode, _scale)
        
        ml_proxies.append(mProxy)
        
        #mProxy.scale = self.getScaleLossy() 
        CORERIG.colorControl(mProxy.mNode,_side,'main',transparent = True)  
        
        for mShape in mProxy.getShapes(asMeta=1):
            mShape.overrideEnabled = 1
            mShape.overrideDisplayType = 2  
            
        mProxy.parent = mTemplateNull
        mGroup = mProxy.doGroup(True, asMeta = True, typeModifier = 'rotateGroup')
        ATTR.connect(self.mNode + '.headRotate', mGroup.mNode + '.rotate')
        
    elif _proxyType == 1:
        log.info("|{0}| >> Geo proxyType. Pushing dimensions...".format(_str_func,_short,_size, _side))     
        #self.scaleX = __dimensions[0] / __dimensions[1]
        #self.scaleZ = __dimensions[2] / __dimensions[1]        
        
        mFile = os.path.join(path_assets, 'headSimple_01.obj')
        _res = cgmOS.import_file(mFile,'HEADIMPORT')
        
        mGeoProxies = self.doCreateAt()
        mGeoProxies.rename("proxyGeo")
        mGeoProxies.parent = mTemplateNull
        _bb = DIST.get_size_byShapes(self.mNode,'bb')
        
        ATTR.connect(self.mNode + '.headRotate', mGeoProxies.mNode + '.rotate')
        
        for i,o in enumerate(_res):
            mProxy = cgmMeta.validateObjArg(o,'cgmObject',setClass=True)
            ml_proxies.append(mProxy)
            mProxy.doSnapTo(self.mNode)                
            #TRANS.scale_to_boundingBox(mProxy.mNode,_bb)
            CORERIG.colorControl(mProxy.mNode,_side,'main',transparent = True)                
            mProxy.parent = mGeoProxies
            mProxy.rename('head_{0}'.format(i))
            
            for mShape in mProxy.getShapes(asMeta=1):
                mShape.overrideEnabled = 1
                mShape.overrideDisplayType = 2                  
            
        NODEFACTORY.build_conditionNetworkFromGroup(mGeoProxies.mNode,'headGeo',self.mNode)
        ATTR.set_keyable(self.mNode,'headGeo',False)    
        
    else:
        raise NotImplementedError,"|{0}| >> Unknown proxyType: [{1}:{2}]".format(_str_func,_proxyType,ATTR.get_enumValueString(self.mNode,'proxyType'))
    
    self.msgList_connect('headMeshProxy',ml_proxies,'block')#Connect
    self.msgList_connect('templateHandles',[self.mNode])
        
    #Neck ==================================================================================================
    if self.neckBuild:
        log.info("|{0}| >> Building neck...".format(_str_func,_short,_size_width, _side)) 
        _size_width = _size_width * .5
        
        
        #>>> Top curve ==========================================================================================
        mTopCurve = mHandleFactory.buildBaseShape('sphere', _size_width, shapeDirection = 'y+')
        mTopCurve.p_parent = mTemplateNull
        
        self.copyAttrTo(_baseNameAttrs[1],mTopCurve.mNode,'cgmName',driven='target')
        mTopCurve.doStore('cgmType','blockHandle')
        mTopCurve.doStore('cgmNameModifier','top')
        mTopCurve.doName()
        
        #Convert to loft curve setup ----------------------------------------------------
        mHandleFactory = self.asHandleFactory(mTopCurve.mNode)
        mHandleFactory.rebuildAsLoftTarget('circle', _size_width, shapeDirection = 'y+',rebuildHandle = False)
        
        mc.makeIdentity(mTopCurve.mNode,a=True, s = True)#...must freeze scale once we're back parented and positioned
    
        mTopCurve.setAttrFlags(['rotate','tx'])
        #mc.transformLimits(mTopCurve.mNode,  tz = [-.25,.25], etz = [1,1], ty = [.1,1], ety = [1,0])
        mTopLoftCurve = mTopCurve.loftCurve
        
        
        CORERIG.colorControl(mTopCurve.mNode,_side,'main',transparent = True)        
        

        #>>> Base curve ==========================================================================================
        mBaseCurve = mHandleFactory.buildBaseShape('sphere', _size_width, shapeDirection = 'y+')
        
        self.copyAttrTo(_baseNameAttrs[1],mBaseCurve.mNode,'cgmName',driven='target')
        mBaseCurve.doStore('cgmType','blockHandle')
        mBaseCurve.doStore('cgmNameModifier','base')
        mBaseCurve.doName()       
        
        mBaseCurve.p_parent = mTemplateNull
        
        mBaseAttachGroup = mBaseCurve.doGroup(True, asMeta=True,typeModifier = 'attach')                
        mBaseCurve.translate = 0,-_size,0        
        
        self.copyAttrTo(_baseNameAttrs[1],mBaseCurve.mNode,'cgmName',driven='target')
        mBaseCurve.doStore('cgmType','blockHandle')
        mBaseCurve.doStore('cgmNameModifier','base')
        mBaseCurve.doName()
        
        #Convert to loft curve setup ----------------------------------------------------
        mHandleFactory = self.asHandleFactory(mBaseCurve.mNode)
        mHandleFactory.rebuildAsLoftTarget('circle', _size_width, shapeDirection = 'y+', rebuildHandle = False)
        
        mc.makeIdentity(mBaseCurve.mNode,a=True, s = True)#...must freeze scale once we're back parented and positioned
    
        mBaseCurve.setAttrFlags(['rotate','tx'])
        #mc.transformLimits(mBaseCurve.mNode,  tz = [-.25,.25], etz = [1,1], ty = [.1,1], ety = [1,0])
        mBaseLoftCurve = mBaseCurve.loftCurve
        
        CORERIG.colorControl(mBaseCurve.mNode,_side,'main',transparent = True)        
        
        #>>> Aim loft curves ==========================================================================================        
        mTopMasterGroup = mTopLoftCurve.doGroup(True,asMeta=True,typeModifier = 'master')
        mTopAimGroup = mTopLoftCurve.doGroup(True,asMeta=True,typeModifier = 'aim')
        
        mBaseMasterGroup = mBaseLoftCurve.doGroup(True,asMeta=True,typeModifier = 'master')
        mBaseAimGroup = mBaseLoftCurve.doGroup(True,asMeta=True,typeModifier = 'aim')        

        mc.aimConstraint(mTopCurve.mNode, mBaseAimGroup.mNode, maintainOffset = False,
                         aimVector = [0,1,0], upVector = [1,0,0], worldUpObject = mBaseCurve.mNode, #skip = 'z',
                         worldUpType = 'objectrotation', worldUpVector = [1,0,0])        
        mc.aimConstraint(mBaseCurve.mNode, mTopAimGroup.mNode, maintainOffset = False, #skip = 'z',
                         aimVector = [0,-1,0], upVector = [1,0,0], worldUpObject = mBaseCurve.mNode,
                         worldUpType = 'objectrotation', worldUpVector = [1,0,0])         
        
        
        #...
        self.msgList_connect('templateHandles',[mBaseCurve.mNode, mTopCurve.mNode])
        
        
        #>>Loft Mesh ==================================================================================================
        targets = [mBaseLoftCurve.mNode, mTopLoftCurve.mNode]        
        BLOCKUTILS.create_templateLoftMesh(self,targets,mBaseLoftCurve,
                                           mTemplateNull,'neckControls',
                                           baseName = _l_baseNames[1])
        
        """targets = [mBaseLoftCurve.mNode, mTopLoftCurve.mNode]
        _res_body = mc.loft(targets, o = True, d = 3, po = 1, name = _l_baseNames[1] )
        mLoft = cgmMeta.validateObjArg(_res_body[0],'cgmObject',setClass= True)
        
        _inputs = mc.listHistory(mLoft.mNode,pruneDagObjects=True)
        _tessellate = _inputs[0]
        _loftNode = _inputs[1]
        
        
        _d = {'format':2,#General
              'polygonType':1,#'quads',
              'uNumber': 1 + self.neckControls}
        
        for a,v in _d.iteritems():
            ATTR.set(_tessellate,a,v)    
            
        mLoft.overrideEnabled = 1
        mLoft.overrideDisplayType = 2
        _arg = "{0}.numberOfControlsOut = {1} + 1".format(mBaseLoftCurve.p_nameShort,
                                                          self.getMayaAttrString('neckControls','short'))
                                                          
        NODEFACTORY.argsToNodes(_arg).doBuild()
        
        ATTR.connect("{0}.numberOfControlsOut".format(mBaseLoftCurve.mNode), "{0}.uNumber".format(_tessellate))
        ATTR.connect("{0}.loftSides".format(self.mNode), "{0}.vNumber".format(_tessellate))
        
        mLoft.p_parent = mTemplateNull
        mLoft.resetAttrs()
        
        mLoft.doStore('cgmName',self.mNode)
        mLoft.doStore('cgmType','controlsApprox')
        mLoft.doName()
        
        for n in _tessellate,_loftNode:
            mObj = cgmMeta.validateObjArg(n)
            mObj.doStore('cgmName',self.mNode)
            mObj.doStore('cgmTypeModifier','controlsApprox')
            mObj.doName()            
        
        
        #mc.polySetToFaceNormal(mLoft.mNode,setUserNormal = True)
        #polyNormal -normalMode 0 -userNormalMode 1 -ch 1 spine_block_controlsApproxShape;
    
        mc.polyNormal(mLoft.mNode, normalMode = 0, userNormalMode = 1, ch=1)
        
        #Color our stuff...
        CORERIG.colorControl(mLoft.mNode,_side,'main',transparent = True)
        
        mLoft.inheritsTransform = 0
        for s in mLoft.getShapes(asMeta=True):
            s.overrideDisplayType = 2   
            
        self.connectChildNode(mLoft.mNode, 'templateLoftMesh', 'block')
        """
        
    
        #Base Orient Helper ----------------------------------------------------------------------------------
        mHandleFactory = self.asHandleFactory(mBaseCurve.mNode)
    
        mBaseOrientCurve = mHandleFactory.addOrientHelper(baseSize = _size_width,
                                                          shapeDirection = 'z-',
                                                          setAttrs = {#'rz':90,
                                                                      'ty':_size_width * .25,
                                                                      'tz':- _size_width})
    
        self.copyAttrTo(_baseNameAttrs[1],mOrientCurve.mNode,'cgmName',driven='target')
        mBaseOrientCurve.doName()    
        mBaseOrientCurve.p_parent = mBaseLoftCurve.parent
        #mBaseOrientCurve.resetAttrs()
        mBaseOrientCurve.setAttrFlags(['rz','rx','translate','scale','v'])
    
        CORERIG.colorControl(mBaseOrientCurve.mNode,_side,'sub')          
        mc.select(cl=True)    
    
    return True
    #Push our dimensions if we're gonna do go mesh...
    if self.proxyType ==2:
        log.info("|{0}| >> Geo proxyType. Pushing dimensions...".format(_str_func,_short,_size, _side))     
        self.scaleX = __dimensions[0] / __dimensions[1]
        self.scaleZ = __dimensions[2] / __dimensions[1]
        


#=============================================================================================================
#>> Prerig
#=============================================================================================================
def build_prerigMesh(self):
    _str_func = 'build_prerigMesh'    
    _shape = self.getEnumValueString('proxyShape')
    _size = self.baseSize
    
    if _shape == 'cube':
        _res = mc.polyCube(width=_size, height = _size, depth = _size)
    elif _shape == 'sphere':
        _res = mc.polySphere(radius = _size * .5)
    elif _shape == 'cylinder':
        _res = mc.polyCylinder(height = _size, radius = _size * .5)
    else:
        raise ValueError,"|{0}| >> Unknown shape: [{1}]".format(_str_func,_shape)
    return _res

def prerig(self):
    #Buffer some data
    _str_func = 'prerig'
    _short = self.p_nameShort
    _baseNameAttrs = ATTR.datList_getAttrs(self.mNode,'baseNames')
    _l_baseNames = ATTR.datList_get(self.mNode, 'baseNames')
    
    
    _side = 'center'
    if self.getMayaAttr('side'):
        _side = self.getEnumValueString('side')
    
    #log.info("|{0}| >> [{1}] | baseSize: {2} | side: {3}".format(_str_func,_short,_size, _side))     
        
    self._factory.module_verify()  
    ml_templateHandles = self.msgList_get('templateHandles')
    
    #Create preRig Null  ==================================================================================
    mPrerigNull = BLOCKUTILS.prerigNull_verify(self)   
    

    #>>New handles ==================================================================================================
    mHandleFactory = self.asHandleFactory(self.mNode)   
    _vec_root_up = self.getAxisVector('z-')
    
    #Get positions
    #DIST.get_pos_by_axis_dist(obj, axis)
    

    if not self.neckBuild:
        _size = DIST.get_size_byShapes(self.mNode)
        _sizeSub = _size * .2   
        
        log.info("|{0}| >> [{1}]  NO NECK | baseSize: {2} | side: {3}".format(_str_func,_short,_size, _side))     

        #Joint Helper ==========================================================================================
        mJointHelper = self.asHandleFactory(self.mNode).addJointHelper(baseSize = _sizeSub)
        ATTR.set_standardFlags(mJointHelper.mNode, attrs=['sx', 'sy', 'sz'], 
                              lock=False, visible=True,keyable=False)
        
        self.msgList_connect('jointHelpers',[mJointHelper.mNode])
        self.msgList_connect('prerigHandles',[self.mNode])

    else:#NECK build ==========================================================================================
        mNoTransformNull = BLOCKUTILS.noTransformNull_verify(self)
        
        mTemplateMesh = self.getMessage('templateLoftMesh',asMeta=True)[0]
        
        mStartHandle = ml_templateHandles[0]    
        mEndHandle = ml_templateHandles[-1]
        
        _size = DIST.get_size_byShapes(mStartHandle.loftCurve.mNode)
        _sizeSub = _size * .2    
        
        ml_handles = [mStartHandle]
        ml_jointHandles = []

        _pos_me = mStartHandle.p_position
        _pos_end = mEndHandle.p_position 
        _vec = MATH.get_vector_of_two_points(_pos_me, _pos_end)
        _offsetDist = DIST.get_distance_between_points(_pos_me,_pos_end) / (self.neckControls)
        _l_pos = [ DIST.get_pos_by_vec_dist(_pos_me, _vec, (_offsetDist * i)) for i in range(self.neckControls)] + [_pos_end]
        
        #Linear track curve ----------------------------------------------------------------------
        _linearCurve = mc.curve(d=1,p=[_pos_me,_pos_end])
        mLinearCurve = cgmMeta.validateObjArg(_linearCurve,'cgmObject')
    
        l_clusters = []
        _l_clusterParents = [mStartHandle,mEndHandle]
        for i,cv in enumerate(mLinearCurve.getComponents('cv')):
            _res = mc.cluster(cv, n = 'test_{0}_cluster'.format(_l_clusterParents[i].p_nameShort))
            TRANS.parent_set( _res[1], _l_clusterParents[i].getMessage('loftCurve')[0])
            l_clusters.append(_res)
        pprint.pprint(l_clusters)
        
        mLinearCurve.parent = mNoTransformNull
        #mLinearCurve.inheritsTransform = False      
        
        #Tmp loft mesh -------------------------------------------------------------------
        _l_targets = [mObj.loftCurve.mNode for mObj in [mStartHandle,mEndHandle]]

        _res_body = mc.loft(_l_targets, o = True, d = 3, po = 0 )
        _str_tmpMesh =_res_body[0]
        
        l_scales = []
        
        for mHandle in mStartHandle, mEndHandle:
            ml_jointHandles.append(self.asHandleFactory(mHandle.mNode).addJointHelper(baseSize = _sizeSub))
            l_scales.append(mHandle.scale)
            mHandle.scale = 1,1,1
        
        
        #Sub handles... ------------------------------------------------------------------------------------
        for i,p in enumerate(_l_pos[1:-1]):
            #mHandle = mHandleFactory.buildBaseShape('circle', _size, shapeDirection = 'y+')
            mHandle = cgmMeta.cgmObject(name = 'handle_{0}'.format(i))
            _short = mHandle.mNode
            ml_handles.append(mHandle)
            mHandle.p_position = p
            SNAP.aim_atPoint(_short,_l_pos[i+2],'y+', 'z-', mode='vector', vectorUp = _vec_root_up)
            
            #...Make our curve
            _d = RAYS.cast(_str_tmpMesh, _short, 'z+')
            pprint.pprint(_d)
            log.debug("|{0}| >> Casting {1} ...".format(_str_func,_short))
            #cgmGEN.log_info_dict(_d,j)
            _v = _d['uvs'][_str_tmpMesh][0][0]
            log.debug("|{0}| >> v: {1} ...".format(_str_func,_v))
        
            #>>For each v value, make a new curve -----------------------------------------------------------------        
            #duplicateCurve -ch 1 -rn 0 -local 0  "loftedSurface2.u[0.724977270271534]"
            _crv = mc.duplicateCurve("{0}.u[{1}]".format(_str_tmpMesh,_v), ch = 0, rn = 0, local = 0)
            log.debug("|{0}| >> created: {1} ...".format(_str_func,_crv))  
            
            CORERIG.shapeParent_in_place(_short, _crv, False)
            
            self.copyAttrTo(_baseNameAttrs[1],mHandle.mNode,'cgmName',driven='target')
            mHandle.doStore('cgmType','blockHandle')
            mHandle.doStore('cgmIterator',i)
            mHandle.doName()
            
            mHandle.p_parent = mPrerigNull
            
            mGroup = mHandle.doGroup(True,True,asMeta=True,typeModifier = 'master')
            _vList = DIST.get_normalizedWeightsByDistance(mGroup.mNode,[mStartHandle.mNode,mEndHandle.mNode])
            #_point = mc.pointConstraint([mStartHandle.mNode,mEndHandle.mNode],mGroup.mNode,maintainOffset = True)#Point contraint loc to the object
            _scale = mc.scaleConstraint([mStartHandle.mNode,mEndHandle.mNode],mGroup.mNode,maintainOffset = False)#Point contraint loc to the object
            reload(CURVES)
            mLoc = mGroup.doLoc()
            mLoc.parent = mNoTransformNull
            #mLoc.inheritsTransform = False
    
            CURVES.attachObjToCurve(mLoc.mNode, mLinearCurve.mNode)
            _point = mc.pointConstraint([mLoc.mNode],mGroup.mNode,maintainOffset = True)#Point contraint loc to the object
            
            for c in [_scale]:
                CONSTRAINT.set_weightsByDistance(c[0],_vList)
            
            #Convert to loft curve setup ----------------------------------------------------
            mHandleFactory = self.asHandleFactory(mHandle.mNode)
            
            #mc.makeIdentity(mHandle.mNode,a=True, s = True)#...must freeze scale once we're back parented and positioned
            
            mHandleFactory.rebuildAsLoftTarget('self', _size, shapeDirection = 'y+')
            ml_jointHandles.append(mHandleFactory.addJointHelper(baseSize = _sizeSub))
            #mTopCurve.setAttrFlags(['rotate','tx','tz'])
            #mc.transformLimits(mTopCurve.mNode,  tz = [-.25,.25], etz = [1,1], ty = [.1,1], ety = [1,0])
            #mTopLoftCurve = mTopCurve.loftCurve
            
            CORERIG.colorControl(mHandle.mNode,_side,'sub',transparent = True)        
            #LOC.create(position = p)
        
        ml_handles.append(mEndHandle)
        self.msgList_connect('prerigHandles', ml_handles,)
        mc.delete(_res_body)
        
        #Push scale back...
        for i,mHandle in enumerate([mStartHandle, mEndHandle]):
            mHandle.scale = l_scales[i]
        
         
        #Template Loft Mesh -------------------------------------
        mTemplateLoft = self.getMessage('templateLoftMesh',asMeta=True)[0]        
        for s in mTemplateLoft.getShapes(asMeta=True):
            s.overrideDisplayType = 1       
            
        
        #Aim the segment
        for i,mHandle in enumerate(ml_handles):
            if i > 0 and i < len(ml_handles) - 1:
                mMasterGroup = mHandle.getMessage('masterGroup',asMeta = True)[0]
                mAimForward = mHandle.doCreateAt()
                mAimForward.parent = mMasterGroup            
                mAimForward.doStore('cgmTypeModifier','forward')
                mAimForward.doStore('cgmType','aimer')
                mAimForward.doName()
                
                mAimBack = mHandle.doCreateAt()
                mAimBack.parent = mMasterGroup                        
                mAimBack.doStore('cgmTypeModifier','back')
                mAimBack.doStore('cgmType','aimer')
                mAimBack.doName()
                
                mAimGroup = mHandle.doGroup(True,asMeta=True,typeModifier = 'aim')
                
                if i == 1:
                    s_targetForward = ml_handles[i+1].getMessage('masterGroup')[0]
                    s_targetBack = mStartHandle.mNode
                elif i == len(ml_handles) -1:
                    s_targetForward = ml_handles[i+1].getMessage('masterGroup')[0]
                    s_targetBack = ml_handles[i-1].getMessage('masterGroup')[0]
                else:
                    s_targetForward = mEndHandle.mNode
                    s_targetBack = ml_handles[i-1].getMessage('masterGroup')[0]
                    
                mc.aimConstraint(s_targetForward, mAimForward.mNode, maintainOffset = False, #skip = 'z',
                                 aimVector = [0,1,0], upVector = [1,0,0], worldUpObject = self.mNode,
                                 worldUpType = 'objectrotation', worldUpVector = [1,0,0])            
                mc.aimConstraint(s_targetBack, mAimBack.mNode, maintainOffset = False, #skip = 'z',
                                 aimVector = [0,-1,0], upVector = [1,0,0], worldUpObject = self.mNode,
                                 worldUpType = 'objectrotation', worldUpVector = [1,0,0])  
                
                mc.orientConstraint([mAimForward.mNode, mAimBack.mNode], mAimGroup.mNode, maintainOffset = True)
                
                #mc.aimConstraint(ml_handles[i+1].mNode, mAimGroup.mNode, maintainOffset = False, #skip = 'z',
                #                 aimVector = [0,1,0], upVector = [1,0,0], worldUpObject = self.mNode,
                #                 worldUpType = 'objectrotation', worldUpVector = [1,0,0])             
                
            
            mLoftCurve = mHandle.loftCurve
                    
            
                
            """
            mLoftCurve = mHandle.loftCurve
            
            if not mLoftCurve.getMessage('aimGroup'):
                mLoftCurve.doGroup(True,asMeta=True,typeModifier = 'aim')
                 
            mAimGroup = mLoftCurve.getMessage('aimGroup',asMeta=True)[0]
            _l_constraints = mAimGroup.getConstraintsTo()
            if _l_constraints:
                mc.delete(_l_constraints)
        
            if mHandle == ml_handles[-1]:
                mc.aimConstraint(ml_handles[-2].mNode, mAimGroup.mNode, maintainOffset = False,
                                 aimVector = [0,-1,0], upVector = [1,0,0], worldUpObject = mHandle.mNode, #skip = 'z',
                                 worldUpType = 'objectrotation', worldUpVector = [1,0,0])        
            else:
                mc.aimConstraint(ml_handles[i+1].mNode, mAimGroup.mNode, maintainOffset = False, #skip = 'z',
                                 aimVector = [0,1,0], upVector = [1,0,0], worldUpObject = mHandle.mNode,
                                 worldUpType = 'objectrotation', worldUpVector = [1,0,0])   """      
        
        
        #>>Loft Mesh ==================================================================================================
        targets = [mObj.loftCurve.mNode for mObj in ml_handles]        
        BLOCKUTILS.create_prerigLoftMesh(self,targets,
                                         mPrerigNull,
                                         'loftSplit',
                                         'neckControls',
                                         baseName = _l_baseNames[1] )        
        for t in targets:
            ATTR.set(t,'v',0)        
        
        """
        _res_body = mc.loft(targets, o = True, d = 3, po = 1 )
        mLoft = cgmMeta.validateObjArg(_res_body[0],'cgmObject',setClass= True)
        _inputs = mc.listHistory(mLoft.mNode,pruneDagObjects=True)
        
        _tessellate = _inputs[0]
        _loft = _inputs[1]
        
        log.info("|{0}| loft inputs: {1}".format(_str_func,_inputs)) 
        _d = {'format':2,#General
              'polygonType':1,#'quads',
              'uNumber': 1 + len(ml_handles)}
        
        for a,v in _d.iteritems():
            ATTR.set(_tessellate,a,v)    
            
        mLoft.overrideEnabled = 1
        mLoft.overrideDisplayType = 2
        
        mLoft.p_parent = mPrerigNull
        mLoft.resetAttrs()
        
        mLoft.doStore('cgmName',self.mNode)
        mLoft.doStore('cgmType','shapeApprox')
        mLoft.doName()
        
        #mc.polySetToFaceNormal(mLoft.mNode,setUserNormal = True)
        #polyNormal -normalMode 0 -userNormalMode 1 -ch 1 spine_block_controlsApproxShape;
    
        mc.polyNormal(mLoft.mNode, normalMode = 0, userNormalMode = 1, ch=1)
        
        #Color our stuff...
        CORERIG.colorControl(mLoft.mNode,_side,'main',transparent = False)
        
        mLoft.inheritsTransform = 0
        for s in mLoft.getShapes(asMeta=True):
            s.overrideDisplayType = 2    
            
        #...wire some controls
        _arg = "{0}.out_vSplit = {1} + {2} + 1".format(targets[0],
                                                      self.getMayaAttrString('neckControls','short'),
                                                      self.getMayaAttrString('loftSplit'))
    
        NODEFACTORY.argsToNodes(_arg).doBuild()
        #rg = "%s.condResult = if %s.ty == 3:5 else 1"%(str_obj,str_obj)
        _arg = "{0}.out_degree = if {1} == 0:1 else 3".format(targets[0],
                                                              self.getMayaAttrString('loftDegree','short'))
      
        NODEFACTORY.argsToNodes(_arg).doBuild()    
    
        ATTR.connect("{0}.out_vSplit".format(targets[0]), "{0}.uNumber".format(_tessellate))
        ATTR.connect("{0}.loftSides".format(self.mNode), "{0}.vNumber".format(_tessellate)) 
        
        ATTR.connect("{0}.out_degree".format(targets[0]), "{0}.degree".format(_loft))    
        #ATTR.copy_to(_loft,'degree',self.mNode,'loftDegree',driven = 'source')"""
        
        
        
        #>>Joint placers ==================================================================================================    
        #Joint placer aim....
        for i,mHandle in enumerate(ml_handles):
            mJointHelper = mHandle.jointHelper
            mLoftCurve = mJointHelper.loftCurve
            
            if not mLoftCurve.getMessage('aimGroup'):
                mLoftCurve.doGroup(True,asMeta=True,typeModifier = 'aim')
                 
            mAimGroup = mLoftCurve.getMessage('aimGroup',asMeta=True)[0]
        
            if mHandle == ml_handles[-1]:
                mc.aimConstraint(ml_handles[-2].mNode, mAimGroup.mNode, maintainOffset = False,
                                 aimVector = [0,-1,0], upVector = [1,0,0], worldUpObject = mHandle.mNode, #skip = 'z',
                                 worldUpType = 'objectrotation', worldUpVector = [1,0,0])        
            else:
                mc.aimConstraint(ml_handles[i+1].mNode, mAimGroup.mNode, maintainOffset = False, #skip = 'z',
                                 aimVector = [0,1,0], upVector = [1,0,0], worldUpObject = mHandle.mNode,
                                 worldUpType = 'objectrotation', worldUpVector = [1,0,0])            
    
        #Joint placer loft....
        targets = [mObj.jointHelper.loftCurve.mNode for mObj in ml_handles]
        
        
        self.msgList_connect('jointHelpers',targets)
        
        BLOCKUTILS.create_jointLoft(self,targets,
                                    mPrerigNull,'neckJoints',
                                    baseName = _l_baseNames[1] )
        
        for t in targets:
            ATTR.set(t,'v',0)
            #ATTR.set_standardFlags(t,[v])
        
        
        """      

        _res_body = mc.loft(targets, o = True, d = 3, po =3 )
        
        mLoft = cgmMeta.validateObjArg(_res_body[0],'cgmObject',setClass= True)
        _inputs = mc.listHistory(mLoft.mNode,pruneDagObjects=True)
        _tessellate = _inputs[0]
        _loft = _inputs[1]
        
        log.info("|{0}| loft inputs: {1}".format(_str_func,_inputs)) 
            
        mLoft.overrideEnabled = 1
        mLoft.overrideDisplayType = 2
        
        mLoft.p_parent = mPrerigNull
        mLoft.resetAttrs()
        
        mLoft.doStore('cgmName',self.mNode)
        mLoft.doStore('cgmType','jointApprox')
        mLoft.doName()
        
        #mc.polySetToFaceNormal(mLoft.mNode,setUserNormal = True)
        #polyNormal -normalMode 0 -userNormalMode 1 -ch 1 spine_block_controlsApproxShape;
    
        #mc.polyNormal(mLoft.mNode, normalMode = 0, userNormalMode = 1, ch=1)
        
        #Color our stuff...
        CORERIG.colorControl(mLoft.mNode,_side,'main',transparent = False)
        
        mLoft.inheritsTransform = 0
        for s in mLoft.getShapes(asMeta=True):
            s.overrideDisplayType = 2    
            
        #...wire some controls
        _arg = "{0}.out_vSplit = {1} + {2} + 1".format(targets[0],
                                                      self.getMayaAttrString('neckJoints','short'),
                                                      self.getMayaAttrString('loftSplit'))
    
        NODEFACTORY.argsToNodes(_arg).doBuild()
        #rg = "%s.condResult = if %s.ty == 3:5 else 1"%(str_obj,str_obj)
      
        NODEFACTORY.argsToNodes(_arg).doBuild()    
    
        ATTR.connect("{0}.out_vSplit".format(targets[0]), "{0}.uNumber".format(_tessellate))    
        """
        
        #Neck ==================================================================================================
        
        self.noTransformNull.v = False
        
    return True

def prerigDelete(self):
    if self.getMessage('templateLoftMesh'):
        mTemplateLoft = self.getMessage('templateLoftMesh',asMeta=True)[0]
        for s in mTemplateLoft.getShapes(asMeta=True):
            s.overrideDisplayType = 2     
    if self.getMessage('noTransformNull'):
        mc.delete(self.getMessage('noTransformNull'))
    return BLOCKUTILS.prerig_delete(self,templateHandles=True)

def is_prerig(self):
    return BLOCKUTILS.is_prerig(self,msgLinks=['moduleTarget','prerigNull'])


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

    
    _baseNameAttrs = ATTR.datList_getAttrs(self.mNode,'baseNames')    

    #>> Head ===================================================================================
    log.debug("|{0}| >> Head...".format(_str_func))
    p = POS.get( ml_prerigHandles[-1].jointHelper.mNode )
    mHeadHelper = self.orientHelper
    
    #...create ---------------------------------------------------------------------------
    mHead_jnt = cgmMeta.cgmObject(mc.joint (p=(p[0],p[1],p[2])))
    mHead_jnt.displayLocalAxis = 1
    mHead_jnt.radius = _radius
    
    self.copyAttrTo(_baseNameAttrs[0],mHead_jnt.mNode,'cgmName',driven='target')
    
    #...orient ----------------------------------------------------------------------------
    #cgmMeta.cgmObject().getAxisVector
    TRANS.aim_atPoint(mHead_jnt.mNode,
                      self.getPositionByAxisDistance('y+', 100),
                      'y+', 'z+', 'vector',
                      vectorUp=mHeadHelper.getAxisVector('z+'))
    #JOINT.orientChain(mHead_jnt, 'z+', 'y+', mHeadHelper.getAxisVector('z+'))
    mHead_jnt.rx = 0
    mHead_jnt.rz = 0
    JOINT.freezeOrientation(mHead_jnt.mNode)
    
    #...name ----------------------------------------------------------------------------
    mHead_jnt.doName()
    
    
    if self.neckBuild:#...Neck =====================================================================
        log.debug("|{0}| >> neckBuild...".format(_str_func))        
        _d = self.atBlockUtils('skeleton_getCreateDict')
        
        mOrientHelper = ml_prerigHandles[0].orientHelper
        
        log.debug("|{0}| >> Neck build....".format(_str_func))  
        ml_joints = JOINT.build_chain(_d['positions'][:-1], worldUpAxis= mOrientHelper.getAxisVector('z-'))
        
        self.copyAttrTo(_baseNameAttrs[1],ml_joints[0].mNode,'cgmName',driven='target')
        
        for i,mJnt in enumerate(ml_joints):
            mJnt.addAttr('cgmIterator',i)
            mJnt.doName()        
        
        mHead_jnt.p_parent = ml_joints[-1]
        mHead_jnt.radius = ml_joints[-1].radius * 5
        #mHead_jnt.parent = False
         
    ml_joints.append(mHead_jnt)
    mRigNull.msgList_connect('moduleJoints', ml_joints)
    
    return ml_joints


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
        
    ml_jointsToConnect = []
    ml_joints = self.d_joints['ml_moduleJoints']
    
    BLOCKUTILS.skeleton_pushSettings(ml_joints, self.d_orientation['str'], self.d_module['mirrorDirection'],
                                     d_rotateOrders, d_preferredAngles)
    
    if not self.mBlock.neckBuild:
        log.info("|{0}| >> Head only...".format(_str_func))  
        
        ml_rigJoints = BLOCKUTILS.skeleton_buildDuplicateChain(ml_joints, 'rig', self.mRigNull,'rigJoints')
        #self.fnc_connect_toRigGutsVis( ml_rigJoints )
        
        if self.mBlock.headAim:
            log.info("|{0}| >> Head IK...".format(_str_func))              
            ml_fkJoints = BLOCKUTILS.skeleton_buildDuplicateChain(ml_joints, 'fk', self.mRigNull, 'fkHeadJoint', singleMode = True )
            ml_blendJoints = BLOCKUTILS.skeleton_buildDuplicateChain(ml_joints, 'blend', self.mRigNull, 'blendHeadJoint', singleMode = True)
            ml_aimJoints = BLOCKUTILS.skeleton_buildDuplicateChain(ml_joints, 'aim', self.mRigNull, 'aimHeadJoint', singleMode = True)
            self.fnc_connect_toRigGutsVis( ml_fkJoints + ml_aimJoints )        
            
    else:
        log.info("|{0}| >> Head/Neck...".format(_str_func))          
        ml_rigJoints = BLOCKUTILS.skeleton_buildRigChain(self.mBlock)
        ml_fkJoints = BLOCKUTILS.skeleton_buildHandleChain(self.mBlock,'fk','fkJoints')    
        
        if self.mBlock.buildIK:
            log.info("|{0}| >> buildIK on. Building blend and IK chains...".format(_str_func))  
            ml_blendJoints = BLOCKUTILS.skeleton_buildHandleChain(self.mBlock,'blend','blendJoints')
            ml_ikJoints = BLOCKUTILS.skeleton_buildHandleChain(self.mBlock,'ik','ikJoints')

    #...connect... 
    #ml_jointsToConnect.extend(ml_rigJoints)
    #ml_jointsToConnect.extend(ml_ikJoints)    
    #ml_jointsToConnect.extend(ml_blendJoints)

    self.fnc_connect_toRigGutsVis( ml_jointsToConnect )        
    log.info("|{0}| >> Time >> = {1} seconds".format(_str_func, "%0.3f"%(time.clock()-_start)))                

    return

def rig_shapes(self):
    _short = self.d_block['shortName']
    _str_func = '[{0}] > rig_shapes'.format(_short)
    log.info("|{0}| >> ...".format(_str_func))  
    _start = time.clock()
    mHelper = self.mBlock.jointHelper
    
    #l_toBuild = ['segmentFK_Loli','segmentIK']
    #mShapeCast.go(self._mi_module,l_toBuild, storageInstance=self)#This will store controls to a dict called    
    
    #Get our base size from the block
    _size = DIST.get_size_byShapes(_short)
    _side = BLOCKUTILS.get_side(self.mBlock)
    _ikPos = mHelper.getPositionByAxisDistance('z+', _size *2)
    #mAttr_moduleName = cgmMeta.cgmAttr(self.mModule,'cgmName')
    _short_module = self.mModule.mNode
    
    if self.mBlock.headAim:
        #IK ----------------------------------------------------------------------------------
        ikCurve = CURVES.create_fromName('sphere',_size/2)
        mLookAt = cgmMeta.validateObjArg(ikCurve,'cgmObject',setClass=True)
        mLookAt.p_position = _ikPos
        
        ATTR.copy_to(_short_module,'cgmName',mLookAt.mNode,driven='target')
        #mIK.doStore('cgmName','head')
        mLookAt.doStore('cgmTypeModifier','lookAt')
        mLookAt.doName()
        
        CORERIG.colorControl(mLookAt.mNode,_side,'main')
        
        self.mRigNull.connectChildNode(mLookAt,'headLookAt','rigNull')#Connect
    
    #FK ----------------------------------------------------------------------------------
    l_lolis = []
    l_starts = []
    for axis in ['x+','z-','x-']:
        pos = mHelper.getPositionByAxisDistance(axis, _size * .75)
        ball = CURVES.create_fromName('sphere',_size/6)
        mBall = cgmMeta.cgmObject(ball)
        mBall.p_position = pos
        mc.select(cl=True)
        p_end = DIST.get_closest_point(mHelper.mNode, ball)[0]
        p_start = mHelper.getPositionByAxisDistance(axis, _size * .25)
        l_starts.append(p_start)
        line = mc.curve (d=1, ep = [p_start,p_end], os=True)
        l_lolis.extend([ball,line])
    
    #base = CURVES.create_fromList(posList=l_starts)
    #l_lolis.append(base)
    
    
    mFK = mHelper.doCreateAt()
    CORERIG.shapeParent_in_place(mFK,l_lolis,False)
    mFK = cgmMeta.validateObjArg(mFK,'cgmObject',setClass=True)
    ATTR.copy_to(_short_module,'cgmName',mFK.mNode,driven='target')
    #mFK.doStore('cgmName','head')
    mFK.doStore('cgmTypeModifier','fk')
    mFK.doName()    
    
    CORERIG.colorControl(mFK.mNode,_side,'main')
    
    self.mRigNull.connectChildNode(mFK,'headFK','rigNull')#Connect
    
    #Settings -------------------------------------------------------------
    pos = mHelper.getPositionByAxisDistance('z-', _size * .75)
    vector = mHelper.getAxisVector('y+')
    newPos = DIST.get_pos_by_vec_dist(pos,vector,_size * .5)
    
    settings = CURVES.create_fromName('gear',_size/3,'x+')
    mSettings = cgmMeta.validateObjArg(settings,'cgmObject',setClass=True)
    mSettings.p_position = newPos
    
    ATTR.copy_to(_short_module,'cgmName',mSettings.mNode,driven='target')
    #mSettings.doStore('cgmName','head')
    mSettings.doStore('cgmTypeModifier','settings')
    mSettings.doName()    
    
    CORERIG.colorControl(mSettings.mNode,_side,'main')    
    
    self.mRigNull.connectChildNode(mSettings,'settings','rigNull')#Connect
    
    if not self.mBlock.neckBuild:
        pass
    
    log.info("|{0}| >> Time >> = {1} seconds".format(_str_func, "%0.3f"%(time.clock()-_start)))
    
def rig_controls(self):
    _short = self.d_block['shortName']
    _str_func = '[{0}] > rig_controls'.format(_short)
    log.info("|{0}| >> ...".format(_str_func))  
    _start = time.clock()
  
    #mHelper = self.mBlock.jointHelper
    mRigNull = self.mRigNull
    ml_controlsAll = []#we'll append to this list and connect them all at the end
    
    #>> visSub ================================================================================================	
    mPlug_result_moduleSubDriver = self.atBuilderUtils('build_visSub')
    
    #>> headFK ========================================================================================
    if not mRigNull.getMessage('headFK'):
        raise ValueError,"No headFK found"
    
    mHeadFK = mRigNull.headFK
    log.info("|{0}| >> Found headFK : {1}".format(_str_func, mHeadFK))
    
    
    _d = MODULECONTROL.register(mHeadFK,
                                addSpacePivots = 2,
                                addDynParentGroup = True, addConstraintGroup=False,
                                mirrorSide= self.d_module['mirrorDirection'],
                                mirrorAxis="translateX,rotateY,rotateZ",
                                makeAimable = True)
    
    mHeadFK = _d['mObj']
    mHeadFK.masterGroup.parent = self.mDeformNull
    ml_controlsAll.append(mHeadFK)    
    
    
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
        mHeadLookAt.masterGroup.parent = self.mDeformNull
        ml_controlsAll.append(mHeadLookAt)

    #>> settings ========================================================================================
    if not mRigNull.getMessage('settings'):
        raise ValueError,"No settings found"    
    mSettings = mRigNull.settings
    log.info("|{0}| >> Found settings : {1}".format(_str_func, mSettings))
    
    MODULECONTROL.register(mSettings)
    
    mSettings.masterGroup.parent = self.mDeformNull
    
    #>> Neck build ======================================================================================
    if self.mBlock.neckBuild:
        raise NotImplementedError,'neck not done'
    
        
        
        
    ml_controlsAll = self.atBuilderUtils('register_mirrorIndices', ml_controlsAll)
    mRigNull.msgList_connect('controlsAll',ml_controlsAll)
    mRigNull.moduleSet.extend(ml_controlsAll)
    
    log.info("|{0}| >> Time >> = {1} seconds".format(_str_func, "%0.3f"%(time.clock()-_start)))                
    
    return 
        
    
    mIK = mRigNull.handleIK
    mFK = mRigNull.handleFK
    mSettings = mRigNull.settings
    
    
    #>>>> IK Handle =============================================================================
    d_buffer = MODULECONTROL.register(mIK,
                                      typeModifier='ik',addSpacePivots = 2,
                                      addDynParentGroup = True, addConstraintGroup=True,
                                      mirrorSide= self.d_module['mirrorDirection'],
                                      mirrorAxis="translateX,rotateY,rotateZ",                                          
                                      makeAimable = False)
    
    #i_IKEnd = d_buffer['instance']	
    mIK.masterGroup.parent = self.mDeformNull
    ml_controlsAll.append(mIK)	
    return 


    try:#visSub ================================================================================================	
        mPlug_result_moduleSubDriver = mi_go.build_visSub()	
    except Exception,error:raise Exception,"visSub! | error: {0}".format(error)


    try:#>>>> FK Segments =============================================================================	
        if len( ml_shapes_segmentFKLoli )<2:
            raise Exception,"build_controls>> Must have at least two fk controls"

        ml_segmentsFK = ml_shapes_segmentFKLoli[:-1]

        i_loc = ml_segmentsFK[0].doLoc()
        mc.move (basePivotPos[0],basePivotPos[1],basePivotPos[2], i_loc.mNode)	

        for i,i_obj in enumerate(ml_shapes_segmentFKLoli[1:-1]):#parent
            i_obj.parent = ml_shapes_segmentFKLoli[i].mNode

        for i,i_obj in enumerate(ml_segmentsFK):
            if i == 0:
                copyPivot = i_loc.mNode
                copyTransform = ml_rigJoints[0].mNode
            else:
                copyPivot = None
                copyTransform = None
            try:
                d_buffer = mControlFactory.registerControl(i_obj,copyTransform = copyTransform,addExtraGroups=1,setRotateOrder=5,typeModifier='fk',copyPivot=copyPivot,
                                                           mirrorSide=mi_go._str_mirrorDirection, mirrorAxis="translateX,rotateY,rotateZ",
                                                           ) 
                log.info(d_buffer)
                i_obj = d_buffer['instance']
                try:
                    i_obj.drawStyle = 2#Stick joint draw style	    
                except:
                    self.log_error("{0} Failed to set drawStyle".format(i_obj.p_nameShort))
                ml_segmentsFK[i] = i_obj
            except Exception,error:
                raise Exception,"%s failed | error: %s"%(i_obj.mNode,error)

        i_loc.delete()
        mi_go._i_rigNull.msgList_connect('controlsFK',ml_segmentsFK,'rigNull')
        ml_controlsAll.extend(ml_segmentsFK)	
        ml_segmentsFK[0].masterGroup.parent = mi_go._i_deformNull.mNode

    except Exception,error:raise Exception,"FK Segments! | error: {0}".format(error)


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


    int_strt = mi_go._i_puppet.get_nextMirrorIndex( mi_go._str_mirrorDirection )
    ml_extraControls = []
    for i,mCtrl in enumerate(ml_controlsAll):
        try:
            for str_a in cgmRigsData.__l_moduleControlMsgListHooks__:
                buffer = mCtrl.msgList_get(str_a)
                if buffer:
                    ml_extraControls.extend(buffer)
                    log.info("Extra controls : {0}".format(buffer))
        except Exception,error:
            self.log_error("mCtrl failed to search for msgList : {0}".format(mCtrl))
            self.log_error("Fail error : {0}".format(error))
    ml_controlsAll.extend(ml_extraControls)			

    for i,mCtrl in enumerate(ml_controlsAll):
        try:
            mCtrl.addAttr('mirrorIndex', value = (int_strt + i))		
        except Exception,error: raise Exception,"Failed to register mirror index | mCtrl: %s | %s"%(mCtrl,error)

    mi_go._i_rigNull.msgList_connect('controlsAll',ml_controlsAll)
    mi_go._i_rigNull.moduleSet.extend(ml_controlsAll)
    return True

def rig_neckSegment(self):
    _short = self.d_block['shortName']
    _str_func = '[{0}] > rig_neckSegment'.format(_short)
    
    if not self.mBlock.neckBuild:
        log.info("|{0}| >> No neck build optioned".format(_str_func))                      
        return True
    
    log.info("|{0}| >> Neck build. Not done".format(_str_func))              
    return False
    

    log.info("|{0}| >> ...".format(_str_func))  
    _start = time.clock()
  
    #mHelper = self.mBlock.jointHelper
    mRigNull = self.mRigNull

    log.info("|{0}| >> Time >> = {1} seconds".format(_str_func, "%0.3f"%(time.clock()-_start)))                
    
def rig_frame(self):
    _short = self.d_block['shortName']
    _str_func = '[{0}] > rig_rigFrame'.format(_short)
    log.info("|{0}| >> ...".format(_str_func))  
    _start = time.clock()
    mRigNull = self.mRigNull
    
    #>> headFK ========================================================================================
    if not mRigNull.getMessage('headFK'):
        raise ValueError,"No headFK found"
    
    mHeadFK = mRigNull.headFK
    log.info("|{0}| >> Found headFK : {1}".format(_str_func, mHeadFK))
    
    
    
    if self.mBlock.headAim:
        log.info("|{0}| >> HeadAim setup...".format(_str_func))
        mSettings = mRigNull.settings
        
        mPlug_aim = cgmMeta.cgmAttr(mSettings.mNode,'blend_aim',attrType='float',lock=False,keyable=True)
        
        mHeadFKJoint = mRigNull.getMessage('fkHeadJoint', asMeta=True)[0]
        mHeadAimJoint = mRigNull.getMessage('aimHeadJoint', asMeta=True)[0]
        mHeadBlendJoint = mRigNull.getMessage('blendHeadJoint', asMeta=True)[0]
        mHeadFKDynParentGroup = mHeadFK.dynParentGroup
        
        mHeadLookAt = mRigNull.headLookAt
        
        ATTR.connect(mPlug_aim.p_combinedShortName, "{0}.v".format(mHeadLookAt.mNode))
        
        #Setup Aim -------------------------------------------------------------------------------------
        mc.aimConstraint(mHeadLookAt.mNode,
                         mHeadAimJoint.mNode,
                         maintainOffset = False, weight = 1,
                         aimVector = self.d_orientation['vectorAim'],
                         upVector = self.d_orientation['vectorUp'],
                         worldUpVector = self.d_orientation['vectorUp'],
                         worldUpObject = mHeadFK.masterGroup.mNode,
                         worldUpType = 'objectRotation' )

        #Setup blend ----------------------------------------------------------------------------------
        RIGCONSTRAINT.blendChainsBy(mHeadFKJoint,mHeadAimJoint,mHeadBlendJoint,
                                    driver = mPlug_aim.p_combinedName,l_constraints=['orient'])
        
        #Parent pass ---------------------------------------------------------------------------------
        mHeadLookAt.masterGroup.parent = mHeadFK.masterGroup
        mSettings.masterGroup.parent = mHeadFK
        
        for mObj in mHeadFKJoint,mHeadAimJoint,mHeadBlendJoint:
            mObj.parent = mHeadFKDynParentGroup
        
        mHeadFK.parent = mHeadBlendJoint.mNode
        """
        mHeadFK_aimFollowGroup = mHeadFK.doGroup(True,True,True,'aimFollow')
        mc.orientConstraint(mHeadBlendJoint.mNode,
                            mHeadFK_aimFollowGroup.mNode,
                            maintainOffset = False)"""
        
        
    else:
        log.info("|{0}| >> NO Head IK setup...".format(_str_func))
        
    ml_rigJoints = mRigNull.msgList_get('rigJoints')
    ml_rigJoints[0].parent = mHeadFK
        
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
    
    
    pprint.pprint(ml_headDynParents)

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
        
        ml_headDynParents.insert(0, mHeadFK.masterGroup)
        mHeadFK.masterGroup.addAttr('cgmAlias','headRoot')
        
        #Add our parents...
        mDynGroup = mHeadLookAt.dynParentGroup
        log.info("|{0}| >> dynParentSetup : {1}".format(_str_func,mDynGroup))  
    
        for o in ml_headDynParents:
            mDynGroup.addDynParent(o)
        mDynGroup.rebuild()
    
        
    #>>  Lock and hide ======================================================================================
    mSettings.setAttrFlags()
    
    
    
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


__l_rigBuildOrder__ = []



















