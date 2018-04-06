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
#r9Meta.cleanCache()#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< TEMP!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


import cgm.core.cgm_General as cgmGEN
from cgm.core.rigger import ModuleShapeCaster as mShapeCast

import cgm.core.cgmPy.os_Utils as cgmOS
import cgm.core.cgmPy.path_Utils as cgmPATH
import cgm.core.mrs.assets as MRSASSETS
path_assets = cgmPATH.Path(MRSASSETS.__file__).up().asFriendly()

import cgm.core.mrs.lib.ModuleControlFactory as MODULECONTROL
reload(MODULECONTROL)
from cgm.core.lib import curve_Utils as CURVES
import cgm.core.lib.rigging_utils as CORERIG
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
import cgm.core.mrs.lib.shared_dat as BLOCKSHARE
import cgm.core.tools.lib.snap_calls as SNAPCALLS
import cgm.core.rig.ik_utils as IK

for m in DIST,POS,MATH,IK,CONSTRAINT,LOC,BLOCKUTILS,BUILDERUTILS,CORERIG,RAYS,JOINT,RIGCONSTRAINT:
    reload(m)
    
# From cgm ==============================================================
from cgm.core import cgm_Meta as cgmMeta

#=============================================================================================================
#>> Block Settings
#=============================================================================================================
__version__ = 'alpha.04022018'
__autoTemplate__ = False
__dimensions = [15.2, 23.2, 19.7]
__menuVisible__ = True

#These are our base dimensions. In this case it is for human
__dimensions_by_type = {'box':[22,22,22],
                        'human':[15.2, 23.2, 19.7]}

__l_rigBuildOrder__ = ['rig_prechecks',
                       'rig_skeleton',
                       'rig_shapes',
                       'rig_controls',
                       'rig_segments',
                       'rig_frame',
                       'rig_cleanUp']

d_wiring_skeleton = {'msgLinks':[],
                     'msgLists':['moduleJoints','skinJoints']}
d_wiring_prerig = {'msgLinks':['moduleTarget','prerigNull'],
                   'msgLists':['prerigHandles']}
d_wiring_template = {'msgLinks':['templateNull'],
                     'msgLists':['templateHandles']}

#>>>Profiles =====================================================================================================
d_build_profiles = {
    'unityMobile':{'default':{'neckJoints':1,
                              'neckControls':1,
                              'neckBuild':True},
                   'human':{'neckJoints':1,
                            'neckControls':1}
                   },
    'unityPC':{'default':{'neckJoints':2,
                          'neckControls':1},
               },
    'feature':{'default':{'numJoints':9,
                          'numControls':5}
               }
}

d_block_profiles = {
    'box':{'neckShapers':2,
           'neckBuild':False,
           'baseAim':[0,-1,0],
           'baseUp':[0,0,-1],
           'baseSize':[22,22,22],
           'loftShape':'square',           
           },
    'head':{'neckShapers':3,
            'neckBuild':True,
            'baseAim':[0,-1,0],
            'baseUp':[0,0,-1],
            'baseSize':[15.2, 23.2, 19.7],
            'loftShape':'wideUp',
            'proxyType':'geo'
             }
}



#>>>Attrs =====================================================================================================
#_l_coreNames = ['head']

l_attrsStandard = ['side',
                   'position',
                   'baseUp',
                   'baseAim',
                   #'hasRootJoint',
                   'attachPoint',
                   'nameList',
                   'loftSides',
                   'loftDegree',
                   'loftSplit',
                   'loftShape',
                   'ikSetup',
                   'ikBase',
                   'buildProfile',
                   'numSpacePivots',
                   'scaleSetup',
                   'offsetMode',
                   'proxyDirect',
                   'settingsDirection',
                   'moduleTarget',]

d_attrsToMake = {'proxyShape':'cube:sphere:cylinder',
                 'proxyType':'base:geo',
                 'headAim':'bool',
                 'headRotate':'double3',
                 'neckBuild':'bool',
                 'neckControls':'int',
                 'neckShapers':'int',
                 'neckJoints':'int',
                 'loftSetup':'default:neck',
                 'blockProfile':':'.join(d_block_profiles.keys()),
                 'neckIK':BLOCKSHARE._d_attrsTo_make.get('ikSetup')#we wanna match this one
                 }

d_defaultSettings = {'version':__version__,
                     'baseSize':MATH.get_space_value(__dimensions[1]),
                     'headAim':True,
                     'neckBuild':True,
                     'neckControls': 1,
                     'attachPoint':'end',
                     'loftSides': 10,
                     'loftSplit':4,
                     'loftDegree':'cubic',
                     'neckJoints':3,
                     'proxyDirect':True,
                     'attachPoint':'base',
                     'neckIK':'ribbon',
                     'proxyShape':'cube',
                     'nameList':['neck','head'],#...our datList values
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
    _str_func = 'define'    
    log.debug("|{0}| >>  ".format(_str_func)+ '-'*80)
    log.debug("{0}".format(self))
    
    _short = self.mNode
    
    ATTR.set_min(_short, 'neckControls', 1)
    ATTR.set_min(_short, 'loftSides', 3)
    ATTR.set_min(_short, 'loftSplit', 1)
    
    
    _shapes = self.getShapes()
    if _shapes:
        log.debug("|{0}| >>  Removing old shapes...".format(_str_func))        
        mc.delete(_shapes)
        defineNull = self.getMessage('defineNull')
        if defineNull:
            log.debug("|{0}| >>  Removing old defineNull...".format(_str_func))
            mc.delete(defineNull)
    
    _size = MATH.average(self.baseSize[1:])
    _crv = CURVES.create_controlCurve(self.mNode, shape='locatorForm',#'arrowsAxis', 
                                      direction = 'z+', sizeMode = 'fixed', size = _size/6)
    CORERIG.shapeParent_in_place(self.mNode,_crv,False)
    
    mHandleFactory = self.asHandleFactory()
    mHandleFactory.color(self.mNode,controlType='main')
    mDefineNull = self.atUtils('stateNull_verify','define')
    
    #Rotate Group ==================================================================
    mRotateGroup = cgmMeta.validateObjArg(mDefineNull.doGroup(True,False,asMeta=True,typeModifier = 'rotate'),
                                          'cgmObject',setClass=True)
    mRotateGroup.p_parent = mDefineNull
    mRotateGroup.doConnectIn('rotate',"{0}.baseAim".format(_short))
    mRotateGroup.setAttrFlags()
    
    #Bounding box ==================================================================
    _bb_shape = CURVES.create_controlCurve(self.mNode,'cubeOpen', size = 1.0, sizeMode='fixed')
    mBBShape = cgmMeta.validateObjArg(_bb_shape, 'cgmObject',setClass=True)
    mBBShape.p_parent = mDefineNull    
    #mBBShape.ty = .5
    
    #CORERIG.copy_pivot(mBBShape.mNode,self.mNode)
    self.doConnectOut('baseSize', "{0}.scale".format(mBBShape.mNode))
    mHandleFactory.color(mBBShape.mNode,controlType='sub')
    mBBShape.setAttrFlags()
    
    mBBShape.doStore('cgmName', self.mNode)
    mBBShape.doStore('cgmType','bbVisualize')
    mBBShape.doName()    
    
    self.connectChildNode(mBBShape.mNode,'bbHelper')

    #Aim Helper ==========================================================================
    _dist = _size / 3
    _crv = CORERIG.create_at(create='curveLinear',l_pos = [mRotateGroup.p_position,
                                                           DIST.get_pos_by_axis_dist(mRotateGroup.mNode,'z+',
                                                                                     distance = _dist * 2)])
    
    _crv = TRANS.parent_set(_crv,mRotateGroup.mNode)
    
    mTarget = self.doCreateAt()
    mTarget = cgmMeta.validateObjArg(mTarget.mNode, 'cgmObject',setClass=True)
    
    mTarget.rename('aimTarget')
    mTarget.p_parent = mRotateGroup
    mTarget.resetAttrs()
    
    mTarget.tz =  _dist    
    
    CORERIG.shapeParent_in_place(mTarget.mNode,_crv,False,False)    

    mTarget.setAttrFlags()
    mHandleFactory.color(mTarget.mNode,controlType='sub')
    self.connectChildNode(mTarget.mNode,'aimHelper')
    
    #neck Up helper ==========================================================================
    _arrowUp = CURVES.create_fromName('pyramid', _size/5, direction= 'y+')
    mArrow = cgmMeta.validateObjArg(_arrowUp, 'cgmObject',setClass=True)
    mArrow.p_parent = mRotateGroup    
    mArrow.resetAttrs()
    mHandleFactory.color(mArrow.mNode,controlType='sub')
    
    mArrow.doStore('cgmName', self.mNode)
    mArrow.doStore('cgmType','neckUpVector')
    mArrow.doName()
    mArrow.setAttrFlags()
    
    
    self.doConnectOut('baseSizeY', "{0}.ty".format(mArrow.mNode))
    #NODEFACTORY.argsToNodes("{0}.ty = {1}.baseSizeY + {2}".format(mArrow.mNode,
    #                                                              self.mNode,
    #                                                              self.baseSize[0])).doBuild()
    
    mAimGroup = cgmMeta.validateObjArg(mArrow.doGroup(True,
                                                      True,
                                                      asMeta=True,typeModifier = 'aim'),'cgmObject',setClass=True)
    mAimGroup.resetAttrs()
    
    _const = mc.aimConstraint(mTarget.mNode, mAimGroup.mNode, maintainOffset = False,
                              aimVector = [0,0,1], upVector = [0,1,0], 
                              worldUpObject = self.mNode,
                              worldUpType = 'objectrotation',#'objectrotation', 
                              worldUpVector = [0,1,0])
    cgmMeta.cgmNode(_const[0]).doConnectIn('worldUpVector','{0}.baseUp'.format(self.mNode))    
    mAimGroup.setAttrFlags()
    
    self.connectChildNode(mAimGroup.mNode,'neckUpHelper')
    
    return
    #Plane helper ==================================================================
    plane = mc.nurbsPlane(axis = [1,0,0],#axis =  MATH.get_obj_vector(self.mNode, 'x+'),
                          width = 1, #height = 1,
                          #subdivisionsX=1,subdivisionsY=1,
                          ch=0)
    mPlane = cgmMeta.validateObjArg(plane[0])
    mPlane.doSnapTo(self.mNode)
    mPlane.p_parent = mDefineNull
    #mPlane.tz = .5
    CORERIG.copy_pivot(mPlane.mNode,self.mNode)

    self.doConnectOut('baseSize', "{0}.scale".format(mPlane.mNode))

    mHandleFactory.color(mPlane.mNode,controlType='sub')

    mPlane.doStore('cgmName', self.mNode)
    mPlane.doStore('cgmType','planeVisualize')
    mPlane.doName() 
    
    mPlane.setAttrFlags()
    
    
    """mAimGroup = mPlane.doGroup(True,True,asMeta=True,typeModifier = 'aim')
    mAimGroup.resetAttrs()
    
    mc.aimConstraint(mTarget.mNode, mAimGroup.mNode, maintainOffset = False,
                     aimVector = [0,0,1], upVector = [0,1,0], 
                     worldUpObject = self.rootUpHelper.mNode,
                     worldUpType = 'objectrotation', 
                     worldUpVector = [0,1,0])    """

 
    return    
    
    
    
#=============================================================================================================
#>> Template
#=============================================================================================================    
#def templateDelete(self):
#    return BLOCKUTILS.templateDelete(self,['orientHelper'])

#is_template = BLOCKUTILS.is_template

  
def template(self):
    _str_func = 'template'
    log.debug("|{0}| >>  ".format(_str_func)+ '-'*80)
    log.debug("{0}".format(self))
    
    _short = self.p_nameShort
    _baseNameAttrs = ATTR.datList_getAttrs(self.mNode,'nameList')
    _proxyType = self.proxyType
    
    """
    _l_baseNames = ATTR.datList_get(self.mNode, 'nameList')
    _headType = self.getEnumValueString('blockProfile')
    _baseSize = self.baseSize
    #_dimensions = __dimensions_by_type.get(_headType,'human')
    
    _side = 'center'
    if self.getMayaAttr('side'):
        _side = self.getEnumValueString('side')
        
    self.scale = 1,1,1
    self.baseSize
    _size = MATH.average(self.scale)
    _size_width = (_baseSize[1]) * _baseSize[2]
    _proxyType = self.proxyType
    
    _worldUpVector = MATH.EUCLID.Vector3(self.baseUp[0],self.baseUp[1],self.baseUp[2])    
    
    log.info("|{0}| >> [{1}] | headType: {2} |baseSize: {3} | side: {4}".format(_str_func,
                                                                                _short,
                                                                                _headType,
                                                                                _baseSize, _side))
    """
    #Initial checks ===============================================================================
    _short = self.p_nameShort
    _side = self.UTILS.get_side(self)
        
    _l_basePosRaw = self.datList_get('basePos') or [(0,0,0)]
    _l_basePos = [self.p_position]
    _baseUp = self.baseUp
    _baseSize = self.baseSize
    _baseAim = self.baseAim
    
    _ikSetup = self.getEnumValueString('ikSetup')
    
    if MATH.is_vector_equivalent(_baseAim,_baseUp):
        raise ValueError,"baseAim and baseUp cannot be the same. baseAim: {0} | baseUp: {1}".format(self.baseAim,self.baseUp)
    
    _loftSetup = self.getEnumValueString('loftSetup')
            
    if _loftSetup not in ['default']:
        return log.error("|{0}| >> loft setup mode not done: {1}".format(_str_func,_loftSetup))
    
    #Get base dat =============================================================================    
    _mVectorAim = MATH.get_obj_vector(self.aimHelper.mNode,asEuclid=True)
    mNeckUpHelper = self.neckUpHelper
    _mVectorUp = MATH.get_obj_vector(mNeckUpHelper.mNode,'y+',asEuclid=True)
    
    mBBHelper = self.bbHelper
    _v_range = max(TRANS.bbSize_get(self.mNode)) *2
    _bb_axisBox = SNAPCALLS.get_axisBox_size(mBBHelper.mNode, _v_range, mark=False)
    _size_width = _bb_axisBox[0]#...x width
    log.debug("{0} >> axisBox size: {1}".format(_str_func,_bb_axisBox))
    log.debug("|{0}| >> Generating more pos dat | bbHelper: {1} | range: {2}".format(_str_func,
                                                                                     mBBHelper.p_nameShort,
                                                                                     _v_range))
    _end = DIST.get_pos_by_vec_dist(_l_basePos[0], _mVectorAim, _bb_axisBox[2] * .75)
    _l_basePos.append(_end)
    
    #for i,p in enumerate(_l_basePos):
        #LOC.create(position=p,name="{0}_loc".format(i))
    
    
    
    #Create temple Null  ==================================================================================
    mTemplateNull = BLOCKUTILS.templateNull_verify(self)
    mNoTransformNull = BLOCKUTILS.noTransformNull_verify(self,'template')
    
    
    #Our main head handle =================================================================================
    mHeadHandle = self.doCreateAt(setClass=True)
    self.copyAttrTo(_baseNameAttrs[-1],mHeadHandle.mNode,'cgmName',driven='target')    
    mHeadHandle.doStore('cgmType','blockHelper')
    mHeadHandle.doName()
    
    mHeadHandle.p_parent = mTemplateNull
    mHandleFactory = self.asHandleFactory(mHeadHandle.mNode, rigBlock = self.mNode)
    
    
    CORERIG.shapeParent_in_place(mHeadHandle.mNode, mBBHelper.mNode, True, True)
    
    CORERIG.colorControl(mHeadHandle.mNode,_side,'main',transparent = True) 
    mBBHelper.v = False
    self.defineNull.template=True
    
    #Orient Helper ==============================================================================
    mOrientCurve = mHandleFactory.addOrientHelper(baseSize = _bb_axisBox[0] * .7,
                                                  shapeDirection = 'z+',
                                                  setAttrs = {'rz':90,
                                                              'tz': _bb_axisBox[2] * .8})
    self.copyAttrTo(_baseNameAttrs[-1],mOrientCurve.mNode,'cgmName',driven='target')
    mOrientCurve.doName()    
    mOrientCurve.setAttrFlags(['rz','translate','scale','v'])
    #mOrientCurve.p_parent = mHeadHandle
    CORERIG.colorControl(mOrientCurve.mNode,_side,'sub')    
    
    
    
    #Proxies ==============================================================================
    ml_proxies = []        
    log.info("|{0}| >> Geo proxyType...".format(_str_func,))     
    
    if _proxyType == 0:
        _res = build_prerigMesh(self)
        mProxy = cgmMeta.validateObjArg(_res[0],'cgmObject',setClass=True)
        mProxy.doSnapTo(self.mNode)       
        TRANS.scale_to_boundingBox(mProxy.mNode, _bb_axisBox)
        
        ml_proxies.append(mProxy)
        
        #mProxy.scale = self.getScaleLossy() 
        CORERIG.colorControl(mProxy.mNode,_side,'main',transparent = True)  
        
        for mShape in mProxy.getShapes(asMeta=1):
            mShape.overrideEnabled = 1
            mShape.overrideDisplayType = 2  
            
        mProxy.parent = mHeadHandle
        mGroup = mProxy.doGroup(True, asMeta = True, typeModifier = 'rotateGroup')
        ATTR.connect(self.mNode + '.headRotate', mGroup.mNode + '.rotate')
        
    elif _proxyType == 1:
        log.info("|{0}| >> Geo proxyType. Pushing dimensions...".format(_str_func))     
        #self.scaleX = __dimensions[0] / __dimensions[1]
        #self.scaleZ = __dimensions[2] / __dimensions[1]        
        
        mFile = os.path.join(path_assets, 'headSimple_01.obj')
        _res = cgmOS.import_file(mFile,'HEADIMPORT')
        
        mGeoProxies = self.doCreateAt()
        mGeoProxies.rename("proxyGeo")
        mGeoProxies.parent = mHeadHandle
        #mGeoProxies.parent = mTemplateNull
        
        #_bb = DIST.get_bb_size(self.mNode,True)
        
        ATTR.connect(self.mNode + '.headRotate', mGeoProxies.mNode + '.rotate')
        
        for i,o in enumerate(_res):
            mProxy = cgmMeta.validateObjArg(o,'cgmObject',setClass=True)
            ml_proxies.append(mProxy)
            mProxy.doSnapTo(self.mNode)                
            #TRANS.scale_to_boundingBox(mProxy.mNode,_bb_axisBox)
            TRANS.scale_to_boundingBox(mProxy.mNode,[1,1,1])            
            CORERIG.colorControl(mProxy.mNode,_side,'main',transparent = True)                
            mProxy.parent = mGeoProxies
            mProxy.rename('head_{0}'.format(i))
            
            for mShape in mProxy.getShapes(asMeta=1):
                mShape.overrideEnabled = 1
                mShape.overrideDisplayType = 2                  
            
        NODEFACTORY.build_conditionNetworkFromGroup(mGeoProxies.mNode,'headGeo',self.mNode)
        ATTR.set_keyable(self.mNode,'headGeo',False)
        self.doConnectOut('baseSize', "{0}.scale".format(mGeoProxies.mNode))
        #mc.parentConstraint([mHeadHandle.mNode],mGeoProxies.mNode,maintainOffset = True)
        
    else:
        raise NotImplementedError,"|{0}| >> Unknown proxyType: [{1}:{2}]".format(_str_func,
                                                                                 _proxyType,
                                                                                 ATTR.get_enumValueString(self.mNode,'proxyType'))
    
    self.msgList_connect('headMeshProxy',ml_proxies,'block')#Connect
    
    
    #Neck ==================================================================================================
    if not self.neckBuild:
        self.msgList_connect('templateHandles',[mHeadHandle.mNode])
        #...just so we have something here. Replaced if we have a neck        
    else:
        log.debug("|{0}| >> Building neck...".format(_str_func,_short,_size_width, _side)) 
        #_size_width = _size_width * .5
        _size_width = _bb_axisBox[0] * .5
        
        md_handles = {}
        ml_handles = []
        md_loftHandles = {}
        ml_loftHandles = []
        
        _loftShapeBase = self.getEnumValueString('loftShape')
        _loftShape = 'loft' + _loftShapeBase[0].capitalize() + ''.join(_loftShapeBase[1:])
        _loftSetup = self.getEnumValueString('loftSetup')
        
        cgmGEN.func_snapShot(vars())
        
        #_l_basePos = [DIST.get_pos_by_vec_dist(self.p_position, self.baseAim, MATH.average(_bb_axisBox)),
        #              self.p_position,
        #              ]
        _l_basePos.reverse()
        _l_mainParents = [mTemplateNull, mHeadHandle]
        
        if _loftSetup not in ['default']:
            return log.error("|{0}| >> loft setup mode not done: {1}".format(_str_func,_loftSetup))
        
        else:
            log.debug("|{0}| >> Default loft setup...".format(_str_func))         
            for i,n in enumerate(['start','end']):
                log.debug("|{0}| >> {1}:{2}...".format(_str_func,i,n)) 
                mHandle = mHandleFactory.buildBaseShape('sphere', _size_width, shapeDirection = 'y+')
                
                mHandle.p_parent = mTemplateNull
                
                self.copyAttrTo(_baseNameAttrs[0],mHandle.mNode,'cgmName',driven='target')                
                mHandle.doStore('cgmType','blockHandle')
                mHandle.doStore('cgmNameModifier',n)
                mHandle.doName()
                
                #Convert to loft curve setup ----------------------------------------------------
                mHandleFactory.setHandle(mHandle.mNode)
                mLoftCurve = mHandleFactory.rebuildAsLoftTarget(_loftShape, _size_width, shapeDirection = 'z+',rebuildHandle = False)
                
                mc.makeIdentity(mHandle.mNode,a=True, s = True)#...must freeze scale once we're back parented and positioned
                
                mHandleFactory.color(mHandle.mNode)
                
                mHandle.p_position = _l_basePos[i]
                
                if _l_mainParents:
                    mHandle.p_parent = _l_mainParents[i]
                    
                md_handles[n] = mHandle
                ml_handles.append(mHandle)
                
                md_loftHandles[n] = mLoftCurve                
                ml_loftHandles.append(mLoftCurve)
                
                mBaseAttachGroup = mHandle.doGroup(True, asMeta=True,typeModifier = 'attach')
                
            
            #>> Base Orient Helper ===========================================================================
            mHandleFactory = self.asHandleFactory(md_handles['start'].mNode)
        
            mBaseOrientCurve = mHandleFactory.addOrientHelper(baseSize = _size_width,
                                                              shapeDirection = 'y+',
                                                              setAttrs = {'ty':_size_width})
            #'tz':- _size_width})
        
            self.copyAttrTo('cgmName',mBaseOrientCurve.mNode,'cgmName',driven='target')
            mBaseOrientCurve.doName()
            
            mBaseOrientCurve.p_parent =  ml_handles[0]
            mOrientHelperAimGroup = mBaseOrientCurve.doGroup(True,asMeta=True,typeModifier = 'aim')        
        
            _const = mc.aimConstraint(ml_handles[1].mNode, mOrientHelperAimGroup.mNode, maintainOffset = False,
                                      aimVector = [0,0,1], upVector = [0,1,0],
                                      worldUpObject = mNeckUpHelper.mNode, #skip = 'z',
                                      worldUpType = 'objectrotation', worldUpVector = [0,1,0])    
            
            self.connectChildNode(mHandle.mNode,'orientHelper')
            #cgmMeta.cgmNode(_const[0]).doConnectIn('worldUpVector','{0}.baseUp'.format(self.mNode))
            #mBaseOrientCurve.p_parent = mStartAimGroup
            
            mBaseOrientCurve.setAttrFlags(['ry','rx','translate','scale','v'])
            mHandleFactory.color(mBaseOrientCurve.mNode,controlType='sub')
            #CORERIG.colorControl(mBaseOrientCurve.mNode,_side,'sub')          
            mc.select(cl=True)    
            
            
            #>>> Aim loft curves =====================================================================
            mStartLoft = md_loftHandles['start']
            mEndLoft = md_loftHandles['end']
            
            mStartAimGroup = mStartLoft.doGroup(True,asMeta=True,typeModifier = 'aim')
            mEndAimGroup = mEndLoft.doGroup(True,asMeta=True,typeModifier = 'aim')        
            
            mc.aimConstraint(md_handles['end'].mNode, mStartAimGroup.mNode, maintainOffset = False,
                             aimVector = [0,0,1], upVector = [0,1,0], worldUpObject = mBaseOrientCurve.mNode,
                             worldUpType = 'objectrotation', worldUpVector = [0,1,0])             
            mc.aimConstraint(md_handles['start'].mNode, mEndAimGroup.mNode, maintainOffset = False,
                             aimVector = [0,0,-1], upVector = [0,1,0], worldUpObject = mBaseOrientCurve.mNode,
                             worldUpType = 'objectrotation', worldUpVector = [0,1,0])             
            
            
            #Sub handles=============================================================================
            if self.neckShapers > 2:
                log.debug("|{0}| >> Sub handles..".format(_str_func))
                
                mNoTransformNull = self.atUtils('noTransformNull_verify')
                
                mStartHandle = md_handles['start']    
                mEndHandle = md_handles['end']    
                mOrientHelper = mStartHandle.orientHelper
            
                ml_handles = [mStartHandle]
                #ml_jointHandles = []        
            
                _size = MATH.average(mHandleFactory.get_axisBox_size(mStartHandle.mNode))
                #DIST.get_bb_size(mStartHandle.loftCurve.mNode,True)[0]
                _sizeSub = _size * .5    
                _vec_root_up = ml_handles[0].orientHelper.getAxisVector('y+')        
        
    
                _pos_start = mStartHandle.p_position
                _pos_end = mEndHandle.p_position 
                _vec = MATH.get_vector_of_two_points(_pos_start, _pos_end)
                _offsetDist = DIST.get_distance_between_points(_pos_start,_pos_end) / (self.neckShapers - 1)
                _l_pos = [ DIST.get_pos_by_vec_dist(_pos_start, _vec, (_offsetDist * i)) for i in range(self.neckShapers-1)] + [_pos_end]
            
                _mVectorAim = MATH.get_vector_of_two_points(_pos_start, _pos_end,asEuclid=True)
                _mVectorUp = _mVectorAim.up()
                #_worldUpVector = [_mVectorUp.x,_mVectorUp.y,_mVectorUp.z]        
            
            
                #Linear track curve ----------------------------------------------------------------------
                _linearCurve = mc.curve(d=1,p=[_pos_start,_pos_end])
                mLinearCurve = cgmMeta.validateObjArg(_linearCurve,'cgmObject')
            
                l_clusters = []
                _l_clusterParents = [mStartHandle,mEndHandle]
                for i,cv in enumerate(mLinearCurve.getComponents('cv')):
                    _res = mc.cluster(cv, n = 'test_{0}_{1}_cluster'.format(_l_clusterParents[i].p_nameBase,i))
                    #_res = mc.cluster(cv)            
                    #TRANS.parent_set( _res[1], _l_clusterParents[i].getMessage('loftCurve')[0])
                    TRANS.parent_set(_res[1], mTemplateNull)
                    mc.pointConstraint(_l_clusterParents[i].getMessage('loftCurve')[0],
                                       _res[1],maintainOffset=True)
                    ATTR.set(_res[1],'v',False)
                    l_clusters.append(_res)
            
                pprint.pprint(l_clusters)
                
                mLinearCurve.parent = mNoTransformNull
                mLinearCurve.rename('template_trackCrv')
                
                #mLinearCurve.inheritsTransform = False      
            
            
                #Tmp loft mesh -------------------------------------------------------------------
                _l_targets = [mObj.loftCurve.mNode for mObj in [mStartHandle,mEndHandle]]
            
                _res_body = mc.loft(_l_targets, o = True, d = 3, po = 0 )
                _str_tmpMesh =_res_body[0]
            
                l_scales = []
            
                for mHandle in mStartHandle, mEndHandle:
                    #ml_jointHandles.append(self.asHandleFactory(mHandle.mNode).addJointHelper(baseSize = _sizeSub,shapeDirection='z+'))
                    l_scales.append(mHandle.scale)
                    mHandle.scale = 1,1,1

                #Sub handles... -------------------------------------------------------------------------------
                for i,p in enumerate(_l_pos[1:-1]):
                    #mHandle = mHandleFactory.buildBaseShape('circle', _size, shapeDirection = 'y+')
                    mHandle = cgmMeta.cgmObject(name = 'handle_{0}'.format(i))
                    _short = mHandle.mNode
                    ml_handles.append(mHandle)
                    mHandle.p_position = p
                    SNAP.aim_atPoint(_short,_l_pos[i+2],'z+', 'y+', mode='vector', vectorUp = _vec_root_up)
            
                    #...Make our curve
                    _d = RAYS.cast(_str_tmpMesh, _short, 'y+')
                    pprint.pprint(_d)
                    log.debug("|{0}| >> Casting {1} ...".format(_str_func,_short))
                    #cgmGEN.log_info_dict(_d,j)
                    _v = _d['uvs'][_str_tmpMesh][0][0]
                    log.debug("|{0}| >> v: {1} ...".format(_str_func,_v))
            
                    #>>For each v value, make a new curve --------------------------------------------
                    #duplicateCurve -ch 1 -rn 0 -local 0  "loftedSurface2.u[0.724977270271534]"
                    _crv = mc.duplicateCurve("{0}.u[{1}]".format(_str_tmpMesh,_v), ch = 0, rn = 0, local = 0)
                    log.debug("|{0}| >> created: {1} ...".format(_str_func,_crv))  
            
                    CORERIG.shapeParent_in_place(_short, _crv, False)
            
                    #self.copyAttrTo(_baseNameAttrs[1],mHandle.mNode,'cgmName',driven='target')
                    #self.copyAttrTo('cgmName',mHandle.mNode,'cgmName',driven='target')
                    self.copyAttrTo(_baseNameAttrs[0],mHandle.mNode,'cgmName',driven='target')                
            
                    mHandle.doStore('cgmType','blockHandle')
                    mHandle.doStore('cgmIterator',i+1)
                    mHandle.doName()
            
                    mHandle.p_parent = mTemplateNull
            
                    mGroup = mHandle.doGroup(True,True,asMeta=True,typeModifier = 'master')
                    _vList = DIST.get_normalizedWeightsByDistance(mGroup.mNode,[mStartHandle.mNode,mEndHandle.mNode])
                    #_point = mc.pointConstraint([mStartHandle.mNode,mEndHandle.mNode],mGroup.mNode,maintainOffset = True)#Point contraint loc to the object
                    _scale = mc.scaleConstraint([mStartHandle.mNode,mEndHandle.mNode],mGroup.mNode,maintainOffset = False)#Point contraint loc to the object
                    reload(CURVES)
                    
                    #mLoc = mGroup.doLoc()
                    #mLoc.parent = mNoTransformNull
                    #mLoc.inheritsTransform = False
                    
                    _res = RIGCONSTRAINT.attach_toShape(mGroup.mNode,mLinearCurve.mNode,'conPoint')
                    _res = TRANS.parent_set(_res[0], mNoTransformNull.mNode)
                    #CURVES.attachObjToCurve(mLoc.mNode, mLinearCurve.mNode)
                    _point = mc.pointConstraint([_res],mGroup.mNode,maintainOffset = True)#Point contraint loc to the object
            
                    for c in [_scale]:
                        CONSTRAINT.set_weightsByDistance(c[0],_vList)
            
                    #Convert to loft curve setup ----------------------------------------------------
                    mHandleFactory = self.asHandleFactory(mHandle.mNode)
            
                    #mc.makeIdentity(mHandle.mNode,a=True, s = True)#...must freeze scale once we're back parented and positioned
            
                    mHandleFactory.rebuildAsLoftTarget('self', _size, shapeDirection = 'z+')
                    #ml_jointHandles.append(mHandleFactory.addJointHelper(baseSize = _sizeSub))
                    #mRootCurve.setAttrFlags(['rotate','tx','tz'])
                    #mc.transformLimits(mRootCurve.mNode,  tz = [-.25,.25], etz = [1,1], ty = [.1,1], ety = [1,0])
                    #mTopLoftCurve = mRootCurve.loftCurve
            
                    CORERIG.colorControl(mHandle.mNode,_side,'sub',transparent = True)        
                    #LOC.create(position = p)
            
                ml_handles.append(mEndHandle)
                mc.delete(_res_body)
            
                #Push scale back...
                for i,mHandle in enumerate([mStartHandle, mEndHandle]):
                    mHandle.scale = l_scales[i]
            
                #Template Loft Mesh -------------------------------------
                #mTemplateLoft = self.getMessage('templateLoftMesh',asMeta=True)[0]        
                #for s in mTemplateLoft.getShapes(asMeta=True):
                    #s.overrideDisplayType = 1       
                
                
                #Aim the segment
                for i,mHandle in enumerate(ml_handles):
                    if mHandle != ml_handles[0] and mHandle != ml_handles[-1]:
                    #if i > 0 and i < len(ml_handles) - 1:
                        mAimGroup = mHandle.doGroup(True,asMeta=True,typeModifier = 'aim')
    
                        mc.aimConstraint(ml_handles[-1].mNode, mAimGroup.mNode, maintainOffset = True, #skip = 'z',
                                         aimVector = [0,0,1], upVector = [0,1,0], worldUpObject = mBaseOrientCurve.mNode,
                                         worldUpType = 'objectrotation', worldUpVector = [0,1,0])             
            
                                         
                mLoftCurve = mHandle.loftCurve
        
        
            #>>Loft Mesh =================================================================================
            targets = [mObj.loftCurve.mNode for mObj in ml_handles]        
            
            self.atUtils('create_prerigLoftMesh',
                         targets,
                         mTemplateNull,
                         'neckControls',
                         'loftSplit',
                         polyType='bezier',
                         baseName = self.cgmName )
            
            
            mNoTransformNull.v = False
            
            self.msgList_connect('templateHandles',[mHeadHandle.mNode] + ml_handles)#...just so we have something here. Replaced if we have a neck        
            
        """
        BLOCKUTILS.create_templateLoftMesh(self,targets,mBaseLoftCurve,
                                           mTemplateNull,'neckControls',
                                           baseName = _l_baseNames[1])"""
        
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
        mc.select(cl=True)    """
    self.blockState = 'template'#...buffer
    
    return True



#=============================================================================================================
#>> Prerig
#=============================================================================================================
def build_prerigMesh(self):
    _str_func = 'build_prerigMesh'    
    _shape = self.getEnumValueString('proxyShape')
    _size = self.baseSize
    
    if _shape == 'cube':
        _res = mc.polyCube(width=_size[0], height = _size[1], depth = _size[2])
    elif _shape == 'sphere':
        _res = mc.polySphere(radius = MATH.average(_size) * .5)
    elif _shape == 'cylinder':
        _res = mc.polyCylinder(height = MATH.average(_size), radius = MATH.average(_size) * .5)
    else:
        raise ValueError,"|{0}| >> Unknown shape: [{1}]".format(_str_func,_shape)
    return _res

def prerig(self):
    #Buffer some data
    _str_func = 'prerig'
    _short = self.p_nameShort
    _side = self.atUtils('get_side')
    log.debug("|{0}| >>  {1}".format(_str_func,self)+ '-'*80)
    
    _baseNameAttrs = ATTR.datList_getAttrs(self.mNode,'nameList')
    _l_baseNames = ATTR.datList_get(self.mNode, 'nameList')
    
    #Initial validation ================================================================================
    self.atUtils('module_verify')
    mPrerigNull = BLOCKUTILS.prerigNull_verify(self)   
    #mNoTransformNull = self.atUtils('noTransformNull_verify')
    mNoTransformNull = self.UTILS.noTransformNull_verify(self,'prerig')
    ml_templateHandles = self.msgList_get('templateHandles')
    
    
    #>>New handles ==================================================================================================
    mHandleFactory = self.asHandleFactory(self.mNode)   
    
    if not self.neckBuild:
        _size = DIST.get_bb_size(self.mNode,True,True)
        _sizeSub = _size * .2   
        
        log.info("|{0}| >> [{1}]  NO NECK | baseSize: {2} | side: {3}".format(_str_func,_short,_size, _side))     

        #Joint Helper ==========================================================================================
        mJointHelper = self.asHandleFactory(self.mNode).addJointHelper(baseSize = _sizeSub)
        ATTR.set_standardFlags(mJointHelper.mNode, attrs=['sx', 'sy', 'sz'], 
                              lock=False, visible=True,keyable=False)
        
        self.msgList_connect('jointHelpers',[mJointHelper.mNode])
        self.msgList_connect('prerigHandles',[self.mNode])

    else:#NECK build ==========================================================================================
        #..marking stuff with changed for refactor purposes
        int_numControls = self.neckControls + 1
        ml_templateHandles_neck = ml_templateHandles[1:]
        
        mStartHandle = ml_templateHandles_neck[0]#...changed
        mEndHandle = ml_templateHandles_neck[-1]    
        mOrientHelper = mStartHandle.orientHelper
    
        ml_handles = []
        # ml_handles = [mStartHandle]        
        ml_jointHandles = []        
    
        _size = MATH.average(mHandleFactory.get_axisBox_size(mStartHandle.mNode))
        _sizeSub = _size * .33    
        _vec_root_up = ml_templateHandles_neck[0].orientHelper.getAxisVector('y+')
    

    
        #Initial logic=========================================================================================
        log.debug("|{0}| >> Initial Logic...".format(_str_func)) 
    
        _pos_start = mStartHandle.p_position
        pprint.pprint(vars())

        _pos_end = mEndHandle.p_position 
        pprint.pprint(vars())

        _vec = MATH.get_vector_of_two_points(_pos_start, _pos_end)

        _offsetDist = DIST.get_distance_between_points(_pos_start,_pos_end) / int_numControls#(int_numControls - 1.0)
    
        _mVectorAim = MATH.get_vector_of_two_points(_pos_start, _pos_end,asEuclid=True)
        _mVectorUp = _mVectorAim.up()
        _worldUpVector = [_mVectorUp.x,_mVectorUp.y,_mVectorUp.z]        
    
    
        #Track curve ============================================================================
        log.debug("|{0}| >> TrackCrv...".format(_str_func)) 
    
        _trackCurve = mc.curve(d=1,p=[mObj.p_position for mObj in ml_templateHandles_neck])
        mTrackCurve = cgmMeta.validateObjArg(_trackCurve,'cgmObject')
        mTrackCurve.rename(self.cgmName + 'prerigTrack_crv')
        mTrackCurve.parent = mNoTransformNull
    
        #mPrerigNull.connectChildNode('prerigTrackCurve',mTrackCurve.mNode,)
    
        l_clusters = []
        #_l_clusterParents = [mStartHandle,mEndHandle]
        for i,cv in enumerate(mTrackCurve.getComponents('cv')):
            _res = mc.cluster(cv, n = 'test_{0}_{1}_cluster'.format(ml_templateHandles_neck[i].p_nameBase,i))
            #_res = mc.cluster(cv)            
            #TRANS.parent_set( _res[1], ml_templateHandles_neck[i].getMessage('loftCurve')[0])
            TRANS.parent_set(_res[1], mPrerigNull)
            mc.pointConstraint(ml_templateHandles_neck[i].getMessage('loftCurve')[0],
                               _res[1],maintainOffset=True)            
            ATTR.set(_res[1],'v',False)                            
            l_clusters.append(_res)
    
    
    
        """
            mTrackCurve.parent = mNoTransformNull
            #mLinearCurve.inheritsTransform = False
            ml_trackSkinJoints = []
            for mObj in ml_templateHandles:
                mJnt = mObj.loftCurve.doCreateAt('joint')
                mJnt.parent = mObj.loftCurve
                ml_trackSkinJoints.append(mJnt)
    
            mTrackCluster = cgmMeta.validateObjArg(mc.skinCluster ([mJnt.mNode for mJnt in ml_trackSkinJoints],
                                                                   mTrackCurve.mNode,
                                                                   tsb=True,
                                                                   maximumInfluences = 1,
                                                                   normalizeWeights = 1,dropoffRate=2.5),
                                                  'cgmNode',
                                                  setClass=True)
    
            mTrackCluster.doStore('cgmName', mTrackCurve.mNode)
            mTrackCluster.doName()    
    
                """
        l_scales = []
        for mHandle in ml_templateHandles_neck:
            l_scales.append(mHandle.scale)
            mHandle.scale = 1,1,1
    
        _l_pos = CURVES.returnSplitCurveList(mTrackCurve.mNode,int_numControls,markPoints = False)
        #_l_pos = [ DIST.get_pos_by_vec_dist(_pos_start, _vec, (_offsetDist * i)) for i in range(int_numControls-1)] + [_pos_end]
    
    
        #Sub handles... ------------------------------------------------------------------------------------
        log.debug("|{0}| >> PreRig Handle creation...".format(_str_func))
    
        for i,p in enumerate(_l_pos):
            log.debug("|{0}| >> handle cnt: {1} | p: {2}".format(_str_func,i,p))
            crv = CURVES.create_fromName('cubeOpen', size = _sizeSub)
            mHandle = cgmMeta.validateObjArg(crv, 'cgmObject', setClass=True)
            #mHandle = cgmMeta.cgmObject(crv, name = 'handle_{0}'.format(i))
            _short = mHandle.mNode
            ml_handles.append(mHandle)
            mHandle.p_position = p
            
            if len(_l_pos) == 1:
                SNAP.aim_atPoint(_short,_pos_end,'z+', 'y+', mode='vector', vectorUp = _vec_root_up)
                
            elif p == _l_pos[-1]:
                SNAP.aim_atPoint(_short,_l_pos[-2],'z-', 'y+', mode='vector', vectorUp = _vec_root_up)                
            else:
                SNAP.aim_atPoint(_short,_l_pos[i+1],'z+', 'y+', mode='vector', vectorUp = _vec_root_up)
    
            mHandle.p_parent = mPrerigNull
    
            mGroup = mHandle.doGroup(True,True,asMeta=True,typeModifier = 'master')
            _vList = DIST.get_normalizedWeightsByDistance(mGroup.mNode,[mStartHandle.mNode,mEndHandle.mNode])
            #_point = mc.pointConstraint([mStartHandle.mNode,mEndHandle.mNode],mGroup.mNode,maintainOffset = True)#Point contraint loc to the object
            #_scale = mc.scaleConstraint([mStartHandle.mNode,mEndHandle.mNode],mGroup.mNode,maintainOffset = False)#Point contraint loc to the object
            mLoc = mGroup.doLoc()
            mLoc.parent = mNoTransformNull
            #mLoc.inheritsTransform = False
    
            CURVES.attachObjToCurve(mLoc.mNode, mTrackCurve.mNode)
            _point = mc.pointConstraint([mLoc.mNode],mGroup.mNode,maintainOffset = True)#Point contraint loc to the object
    
            #for c in [_scale]:
                #CONSTRAINT.set_weightsByDistance(c[0],_vList)
    
            mHandleFactory = self.asHandleFactory(mHandle.mNode)
    
            #Convert to loft curve setup ----------------------------------------------------
            ml_jointHandles.append(mHandleFactory.addJointHelper(baseSize = _sizeSub))
            #mRootCurve.setAttrFlags(['rotate','tx','tz'])
            #mc.transformLimits(mRootCurve.mNode,  tz = [-.25,.25], etz = [1,1], ty = [.1,1], ety = [1,0])
            #mTopLoftCurve = mRootCurve.loftCurve
    
            CORERIG.colorControl(mHandle.mNode,_side,'sub',transparent = True)        
            #LOC.create(position = p)
    
        #ml_handles.append(mEndHandle)
        self.msgList_connect('prerigHandles', ml_handles)
    
        ml_handles[0].connectChildNode(mOrientHelper.mNode,'orientHelper')      
    
        #mc.delete(_res_body)
        self.atUtils('prerigHandles_getNameDat',True, int_numControls)
    
        #Push scale back...
        for i,mHandle in enumerate(ml_templateHandles_neck):
            mHandle.scale = l_scales[i]
    

    
    
        #>>Joint placers ==================================================================================================    
        #Joint placer aim....
    
        for i,mHandle in enumerate(ml_handles):
            mJointHelper = mHandle.jointHelper
            mLoftCurve = mJointHelper.loftCurve
    
            if not mLoftCurve.getMessage('aimGroup'):
                mLoftCurve.doGroup(True,asMeta=True,typeModifier = 'aim')
    
    
            mAimGroup = mLoftCurve.getMessage('aimGroup',asMeta=True)[0]
            
            if len(ml_handles) == 1:
                mc.aimConstraint(mEndHandle.mNode, mAimGroup.mNode, maintainOffset = False, #skip = 'z',
                                 aimVector = [0,0,1], upVector = [0,1,0], worldUpObject = mOrientHelper.mNode,
                                 worldUpType = 'objectrotation', worldUpVector = [0,1,0])
            elif mHandle == ml_handles[-1]:
                mc.aimConstraint(ml_handles[-2].mNode, mAimGroup.mNode, maintainOffset = False,
                                 aimVector = [0,0,-1], upVector = [0,1,0], worldUpObject = mOrientHelper.mNode, #skip = 'z',
                                 worldUpType = 'objectrotation', worldUpVector = [0,1,0])            
            else:
                mc.aimConstraint(ml_handles[i+1].mNode, mAimGroup.mNode, maintainOffset = False, #skip = 'z',
                                 aimVector = [0,0,1], upVector = [0,1,0], worldUpObject = mOrientHelper.mNode,
                                 worldUpType = 'objectrotation', worldUpVector = [0,1,0])
    
        
        #Joint placer loft....
        targets = [mObj.jointHelper.loftCurve.mNode for mObj in ml_handles]
        pprint.pprint(targets)
        self.msgList_connect('jointHelpers',targets)
    
        self.atUtils('create_jointLoft',
                     targets,
                     mPrerigNull,
                     'neckJoints',
                     baseCount = 2,
                     baseName = self.cgmName )        
    
        """
            BLOCKUTILS.create_jointLoft(self,targets,
                                        mPrerigNull,'neckJoints',
                                        baseName = _l_baseNames[1] )
            """

        
        for t in targets:
            ATTR.set(t,'v',0)
        
        cgmGEN.func_snapShot(vars())
        #Neck ==================================================================================================
        mNoTransformNull.v = False
    
    self.blockState = 'prerig'#...buffer
    return True

def prerigDelete(self):
    if self.getMessage('templateLoftMesh'):
        mTemplateLoft = self.getMessage('templateLoftMesh',asMeta=True)[0]
        for s in mTemplateLoft.getShapes(asMeta=True):
            s.overrideDisplayType = 2     
    if self.getMessage('noTransformNull'):
        mc.delete(self.getMessage('noTransformNull'))
    return BLOCKUTILS.prerig_delete(self,templateHandles=True)

#def is_prerig(self):
#    return BLOCKUTILS.is_prerig(self,msgLinks=['moduleTarget','prerigNull'])
#def is_prerig(self):return True
    
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
    
    ml_templateHandles = self.msgList_get('templateHandles',asMeta = True)
    if not ml_templateHandles:
        raise ValueError,"No templateHandles connected"    
    
    ml_prerigHandles = self.msgList_get('prerigHandles',asMeta = True)
    if not ml_prerigHandles:
        raise ValueError,"No prerigHandles connected"
    
    #>> If skeletons there, delete -------------------------------------------------------------------------- 
    _bfr = mRigNull.msgList_get('moduleJoints',asMeta=True)
    if _bfr:
        log.debug("|{0}| >> Joints detected...".format(_str_func))            
        if forceNew:
            log.debug("|{0}| >> force new...".format(_str_func))                            
            mc.delete([mObj.mNode for mObj in _bfr])
        else:
            return _bfr

    _baseNameAttrs = ATTR.datList_getAttrs(self.mNode,'nameList')
    _l_baseNames = ATTR.datList_get(self.mNode, 'nameList')
    _l_namesToUse = self.atUtils('skeleton_getNameDicts',False, self.neckJoints +1,
                                 iterName = _l_baseNames[0])        
    #>> Head ===================================================================================
    log.debug("|{0}| >> Head...".format(_str_func))
    p = POS.get( ml_prerigHandles[-1].jointHelper.mNode )
    mHeadHelper = ml_templateHandles[0].orientHelper
    
    #...create ---------------------------------------------------------------------------
    mHead_jnt = cgmMeta.cgmObject(mc.joint (p=(p[0],p[1],p[2])))
    mHead_jnt.parent = False
    #self.copyAttrTo(_baseNameAttrs[-1],mHead_jnt.mNode,'cgmName',driven='target')
    
    #...orient ----------------------------------------------------------------------------
    #cgmMeta.cgmObject().getAxisVector
    CORERIG.match_orientation(mHead_jnt.mNode, mHeadHelper.mNode)
    """
    p_orientAxis = mHeadHelper.getPositionByAxisDistance('z+', 100)
    TRANS.aim_atPoint(mHead_jnt.mNode,
                      p_orientAxis,
                      'z+', 'y+', 'vector',
                      vectorUp=mHeadHelper.getAxisVector('y+'))
    LOC.create(position=p_orientAxis)
    """
    #JOINT.orientChain(mHead_jnt, 'z+', 'y+', mHeadHelper.getAxisVector('z+'))
    #mHead_jnt.rx = 0
    #mHead_jnt.rz = 0
    JOINT.freezeOrientation(mHead_jnt.mNode)
    
    #...name ----------------------------------------------------------------------------
    #mHead_jnt.doName()
    #mHead_jnt.rename(_l_namesToUse[-1])
    for k,v in _l_namesToUse[-1].iteritems():
        mHead_jnt.doStore(k,v)
    mHead_jnt.doName()
    
    if self.neckBuild:#...Neck =====================================================================
        log.debug("|{0}| >> neckBuild...".format(_str_func))
        if len(ml_prerigHandles) == 2 and self.neckJoints == 1:
            log.debug("|{0}| >> Single neck joint...".format(_str_func))
            p = POS.get( ml_prerigHandles[0].jointHelper.mNode )
            
            mBaseHelper = ml_prerigHandles[0].orientHelper
            
            #...create ---------------------------------------------------------------------------
            mNeck_jnt = cgmMeta.cgmObject(mc.joint (p=(p[0],p[1],p[2])))
            
            #self.copyAttrTo(_baseNameAttrs[0],mNeck_jnt.mNode,'cgmName',driven='target')
            
            #...orient ----------------------------------------------------------------------------
            #cgmMeta.cgmObject().getAxisVector
            TRANS.aim_atPoint(mNeck_jnt.mNode,
                              mHead_jnt.p_position,
                              'z+', 'y+', 'vector',
                              vectorUp=mHeadHelper.getAxisVector('z-'))
            JOINT.freezeOrientation(mNeck_jnt.mNode)
            
            #mNeck_jnt.doName()
            
            mHead_jnt.p_parent = mNeck_jnt
            ml_joints.append(mNeck_jnt)
            
            #mNeck_jnt.rename(_l_namesToUse[0])
            for k,v in _l_namesToUse[0].iteritems():
                mNeck_jnt.doStore(k,v)
            mNeck_jnt.doName()
        else:
            log.debug("|{0}| >> Multiple neck joint...".format(_str_func))
            
            _d = self.atBlockUtils('skeleton_getCreateDict', self.neckJoints +1)
            
            mOrientHelper = ml_prerigHandles[0].orientHelper
            
            ml_joints = JOINT.build_chain(_d['positions'][:-1], parent=True, worldUpAxis= mOrientHelper.getAxisVector('z-'))
            
            for i,mJnt in enumerate(ml_joints):
                #mJnt.rename(_l_namesToUse[i])
                for k,v in _l_namesToUse[i].iteritems():
                    mJnt.doStore(k,v)
                mJnt.doName()                
            
            #self.copyAttrTo(_baseNameAttrs[0],ml_joints[0].mNode,'cgmName',driven='target')
            
        mHead_jnt.p_parent = ml_joints[-1]
        ml_joints[0].parent = False
    else:
        mHead_jnt.parent = False
        #mHead_jnt.rename(_l_namesToUse[-1])
        
    ml_joints.append(mHead_jnt)
    
    for mJnt in ml_joints:
        mJnt.displayLocalAxis = 1
        mJnt.radius = _radius
    if len(ml_joints) > 1:
        mHead_jnt.radius = ml_joints[-1].radius * 5

    mRigNull.msgList_connect('moduleJoints', ml_joints)
    self.msgList_connect('moduleJoints', ml_joints)
    self.atBlockUtils('skeleton_connectToParent')
    
    return ml_joints


#=============================================================================================================
#>> rig
#=============================================================================================================
#NOTE - self here is a rig Factory....

d_preferredAngles = {'head':[0,-10, 10]}#In terms of aim up out for orientation relative values, stored left, if right, it will invert
d_rotateOrders = {'head':'yxz'}

#Rig build stuff goes through the rig build factory ------------------------------------------------------
@cgmGEN.Timer
def rig_prechecks(self):
    _short = self.d_block['shortName']
    _str_func = 'rig_prechecks'
    log.debug("|{0}| >>  ".format(_str_func)+ '-'*80)
    log.debug("{0}".format(self))
    
    mBlock = self.mBlock
    mModule = self.mModule
    mRigNull = self.mRigNull
    mPrerigNull = mBlock.prerigNull
    ml_templateHandles = mBlock.msgList_get('templateHandles')
    ml_handleJoints = mPrerigNull.msgList_get('handleJoints')
    mMasterNull = self.d_module['mMasterNull']
    
    self.mRootTemplateHandle = ml_templateHandles[0]
    
    #Initial option checks ============================================================================    
    if mBlock.scaleSetup:
        raise NotImplementedError,"Haven't setup scale yet."
    if mBlock.neckIK not in [0,3]:
        raise NotImplementedError,"Haven't setup neck IK: {0}".format(ATTR.get_enumValueString(mBlock.mNode,'neckIK'))
    #if mBlock.ikSetup > 1:
        #raise NotImplementedError,"Haven't setup ik mode: {0}".format(ATTR.get_enumValueString(mBlock.mNode,'ikSetup'))
        

    
    #Offset ============================================================================    
    str_offsetMode = ATTR.get_enumValueString(mBlock.mNode,'offsetMode')
    if not mBlock.offsetMode:
        log.debug("|{0}| >> default offsetMode...".format(_str_func))
        self.v_offset = self.mPuppet.atUtils('get_shapeOffset')
    else:
        str_offsetMode = ATTR.get_enumValueString(mBlock.mNode,'offsetMode')
        log.debug("|{0}| >> offsetMode: {1}".format(_str_func,str_offsetMode))
        
        l_sizes = []
        for mHandle in ml_templateHandles:
            #_size_sub = SNAPCALLS.get_axisBox_size(mHandle)
            #l_sizes.append( MATH.average(_size_sub[1],_size_sub[2]) * .1 )
            _size_sub = POS.get_bb_size(mHandle,True)
            l_sizes.append( MATH.average(_size_sub) * .1 )            
        self.v_offset = MATH.average(l_sizes)
        #_size_midHandle = SNAPCALLS.get_axisBox_size(ml_templateHandles[self.int_handleMidIdx])
        #self.v_offset = MATH.average(_size_midHandle[1],_size_midHandle[2]) * .1        
    log.debug("|{0}| >> self.v_offset: {1}".format(_str_func,self.v_offset))    
    
    
    #DynParents =============================================================================
    self.UTILS.get_dynParentTargetsDat(self)
    
    """
    log.debug("|{0}| >> Resolve moduleParent dynTargets".format(_str_func))
    
    mModuleParent = self.d_module['mModuleParent']
    self.md_dynTargetsParent = {}
    self.ml_dynEndParents = [mMasterNull.puppetSpaceObjectsGroup, mMasterNull.worldSpaceObjectsGroup]
    self.ml_dynParentsAbove = []
    self.md_dynTargetsParent['world'] = mMasterNull.worldSpaceObjectsGroup
    self.md_dynTargetsParent['puppet'] = mMasterNull.puppetSpaceObjectsGroup
    
    self.md_dynTargetsParent['driverPoint'] = mModule.atUtils('get_driverPoint',
                                                             ATTR.get_enumValueString(mBlock.mNode,'attachPoint'))
    
    
    if mModuleParent:
        mi_parentRigNull = mModuleParent.rigNull
        if mi_parentRigNull.getMessage('rigRoot'):
            mParentRoot = mi_parentRigNull.rigRoot
            self.md_dynTargetsParent['root'] = mParentRoot
            #self.ml_dynEndParents.insert(0,mParentRoot)
            self.ml_dynParentsAbove.append(mParentRoot)
        else:
            self.md_dynTargetsParent['root'] = False
            
        _mBase = mModule.atUtils('get_driverPoint','base')
        _mEnd = mModule.atUtils('get_driverPoint','end')
        
        if _mBase:
            self.md_dynTargetsParent['base'] = _mBase
            self.ml_dynParentsAbove.append(_mBase)
        if _mEnd:
            self.md_dynTargetsParent['end'] = _mEnd
            self.ml_dynParentsAbove.append(_mEnd)
            

            
    log.debug(cgmGEN._str_subLine)
    log.debug("|{0}| >> dynTargets | self.md_dynTargetsParent ...".format(_str_func))            
    pprint.pprint(self.md_dynTargetsParent)
    log.debug(cgmGEN._str_subLine)    
    log.debug("|{0}| >> dynEndTargets | self.ml_dynEndParents ...".format(_str_func))                
    pprint.pprint(self.ml_dynEndParents)
    log.debug(cgmGEN._str_subLine)
    log.debug("|{0}| >> dynTargets from above | self.ml_dynParentsAbove ...".format(_str_func))                
    pprint.pprint(self.ml_dynParentsAbove)    
    log.debug(cgmGEN._str_subLine)
    """
    #rotateOrder =============================================================================
    _str_orientation = self.d_orientation['str']
    self.rotateOrder = "{0}{1}{2}".format(_str_orientation[1],_str_orientation[2],_str_orientation[0])
    self.rotateOrderHead = "{2}{0}{1}".format(_str_orientation[0],_str_orientation[1],_str_orientation[2])
    
    log.debug("|{0}| >> rotateOrder | self.rotateOrder: {1}".format(_str_func,self.rotateOrder))
    log.debug("|{0}| >> rotateOrder | self.rotateOrderHead: {1}".format(_str_func,self.rotateOrderHead))

    log.debug(cgmGEN._str_subLine)

    return True


@cgmGEN.Timer
def rig_skeleton(self):
    _short = self.d_block['shortName']
    
    _str_func = 'rig_skeleton'
    log.debug("|{0}| >>  ".format(_str_func)+ '-'*80)
    log.debug("{0}".format(self))
        
    mBlock = self.mBlock
    mRigNull = self.mRigNull
    ml_jointsToConnect = []
    ml_jointsToHide = []
    ml_joints = mRigNull.msgList_get('moduleJoints')
    self.d_joints['ml_moduleJoints'] = ml_joints
    
    BLOCKUTILS.skeleton_pushSettings(ml_joints, self.d_orientation['str'], self.d_module['mirrorDirection'])
                                     #d_rotateOrders, d_preferredAngles)
    
    log.info("|{0}| >> Head...".format(_str_func))  
    
    ml_rigJoints = BLOCKUTILS.skeleton_buildDuplicateChain(mBlock, ml_joints, 'rig', self.mRigNull,'rigJoints',blockNames=True)
    
    if self.mBlock.headAim:
        log.info("|{0}| >> Head IK...".format(_str_func))              
        ml_fkHeadJoints = BLOCKUTILS.skeleton_buildDuplicateChain(mBlock,ml_rigJoints[-1], 'fk', self.mRigNull, 'fkHeadJoint', singleMode = True)
        
        ml_blendHeadJoints = BLOCKUTILS.skeleton_buildDuplicateChain(mBlock,ml_rigJoints[-1], 'blend', self.mRigNull, 'blendHeadJoint', singleMode = True)
        ml_aimHeadJoints = BLOCKUTILS.skeleton_buildDuplicateChain(mBlock,ml_rigJoints[-1], 'aim', self.mRigNull, 'aimHeadJoint', singleMode = True)
        ml_jointsToConnect.extend(ml_fkHeadJoints + ml_aimHeadJoints)
        ml_jointsToHide.extend(ml_blendHeadJoints)
    
    #...Neck ---------------------------------------------------------------------------------------
    if self.mBlock.neckBuild:
        log.info("|{0}| >> Neck Build".format(_str_func))          
        ml_fkJoints = BLOCKUTILS.skeleton_buildHandleChain(mBlock,'fk','fkJoints')
        l_baseNameAttrs = ATTR.datList_getAttrs(mBlock.mNode,'baseNames')
        """
        #We then need to name our core joints to pass forward:
        mBlock.copyAttrTo(l_baseNameAttrs[-1],ml_fkJoints[-1].mNode,'cgmName',driven='target')
        mBlock.copyAttrTo(l_baseNameAttrs[0],ml_fkJoints[0].mNode,'cgmName',driven='target')
        
        if len(ml_fkJoints) > 2:
            for i,mJnt in enumerate(ml_fkJoints[1:-1]):
                mJnt.doStore('cgmIterator',i+1)
            ml_fkJoints[0].doStore('cgmNameModifier','base')
        
        for mJnt in ml_fkJoints:
            mJnt.doName()
            """
        ml_jointsToHide.extend(ml_fkJoints)

        if self.mBlock.neckIK:
            log.info("|{0}| >> buildIK on. Building blend and IK chains...".format(_str_func))  
            ml_blendJoints = BLOCKUTILS.skeleton_buildHandleChain(mBlock,'blend','blendJoints')
            ml_ikJoints = BLOCKUTILS.skeleton_buildHandleChain(mBlock,'ik','ikJoints')
            ml_jointsToConnect.extend(ml_ikJoints)
            ml_jointsToHide.extend(ml_blendJoints)
            
            for i,mJnt in enumerate(ml_ikJoints):
                if mJnt not in [ml_ikJoints[0],ml_ikJoints[-1]]:
                    mJnt.preferredAngle = mJnt.jointOrient                    
            
        
        if mBlock.neckControls > 2:
            log.info("|{0}| >> IK Drivers...".format(_str_func))            
            ml_baseIKDrivers = BLOCKUTILS.skeleton_buildDuplicateChain(ml_segmentHandles,
                                                                       None, mRigNull,
                                                                       'baseIKDrivers',
                                                                       cgmType = 'baseIKDriver', indices=[0,-1])
            for mJnt in ml_baseIKDrivers:
                mJnt.parent = False
            ml_jointsToConnect.extend(ml_baseIKDrivers)
            
        if mBlock.neckJoints > mBlock.neckControls:
            log.info("|{0}| >> Handles...".format(_str_func))            
            ml_segmentHandles = BLOCKUTILS.skeleton_buildHandleChain(mBlock,'handle',
                                                                     'handleJoints',
                                                                     clearType=True)
            for i,mJnt in enumerate(ml_segmentHandles):
                mJnt.parent = ml_blendJoints[i]
            
            log.info("|{0}| >> segment necessary...".format(_str_func))
                
            ml_segmentChain = BLOCKUTILS.skeleton_buildDuplicateChain(mBlock, ml_joints,
                                                                      None, mRigNull,
                                                                      'segmentJoints', cgmType = 'segJnt')
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
    self.fnc_connect_toRigGutsVis( ml_jointsToConnect )        
    
    return

@cgmGEN.Timer
def rig_shapes(self):
    _short = self.d_block['shortName']
    _str_func = 'rig_shapes'
    log.debug("|{0}| >>  ".format(_str_func)+ '-'*80)
    log.debug("{0}".format(self))
    
    ml_prerigHandles = self.mBlock.atBlockUtils('prerig_getHandleTargets')
    ml_fkJoints = self.mRigNull.msgList_get('fkJoints')
    ml_rigJoints = self.mRigNull.msgList_get('rigJoints')
    mHeadHelper = ml_prerigHandles[-1]
    mBlock = self.mBlock
    _baseNameAttrs = ATTR.datList_getAttrs(mBlock.mNode,'nameList')    
    ml_templateHandles = mBlock.msgList_get('templateHandles')
    mHandleFactory = mBlock.asHandleFactory()
    
    #l_toBuild = ['segmentFK_Loli','segmentIK']
    #mShapeCast.go(self._mi_module,l_toBuild, storageInstance=self)#This will store controls to a dict called    
    
    #Get our base size from the block
    _size = DIST.get_bb_size(ml_templateHandles[0].mNode,True,True)
    _side = BLOCKUTILS.get_side(self.mBlock)
    _short_module = self.mModule.mNode
    ml_joints = self.d_joints['ml_moduleJoints']
    _offset = self.v_offset
    
    #Logic ====================================================================================
    b_FKIKhead = False
    if mBlock.neckControls > 1 and mBlock.neckBuild: 
        log.info("|{0}| >> FK/IK head necessary...".format(_str_func))          
        b_FKIKhead = True    
    
    #Head=============================================================================================
    if mBlock.headAim:
        log.info("|{0}| >> Head aim...".format(_str_func))  
        
        _ikPos =DIST.get_pos_by_vec_dist(ml_prerigHandles[-1].p_position,
                                       MATH.get_obj_vector(ml_templateHandles[0].orientHelper.mNode,'z+'),
                                       _size * 1.5)
        
        ikCurve = CURVES.create_fromName('sphere2',_size/3)
        textCrv = CURVES.create_text('head',_size/4)
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
    mIK = ml_rigJoints[-1].doCreateAt()
    #CORERIG.shapeParent_in_place(mIK,l_lolis,False)
    CORERIG.shapeParent_in_place(mIK,ml_templateHandles[0].mNode,True)
    mIK = cgmMeta.validateObjArg(mIK,'cgmObject',setClass=True)
    
    mBlock.copyAttrTo(_baseNameAttrs[-1],mIK.mNode,'cgmName',driven='target')
    
    #ATTR.copy_to(_short_module,'cgmName',mIK.mNode,driven='target')
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
    
    _size_direct = DIST.get_bb_size(ml_templateHandles[-1].mNode,True,True)
    
    d_direct = {'size':_size_direct/2}
        
    ml_directShapes = self.atBuilderUtils('shapes_fromCast',
                                          ml_rigJoints,
                                          mode ='direct',**d_direct)
    
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
        self.mRigNull.connectChildNode(mIK,'settings','rigNull')#Connect    
        
    #Handles ===========================================================================================
    ml_handleJoints = self.mRigNull.msgList_get('handleJoints')

    if ml_handleJoints:
        log.debug("|{0}| >> Found Handle joints...".format(_str_func))
        #l_uValues = MATH.get_splitValueList(.01,.99, len(ml_handleJoints))
        ml_handleShapes = self.atBuilderUtils('shapes_fromCast',
                                              targets = ml_handleJoints,
                                              offset = _offset,
                                              mode = 'limbSegmentHandle')#'segmentHandle') limbSegmentHandle


        for i,mCrv in enumerate(ml_handleShapes):
            log.debug("|{0}| >> Shape: {1} | Handle: {2}".format(_str_func,mCrv.mNode,ml_handleJoints[i].mNode ))                
            mHandleFactory.color(mCrv.mNode, controlType = 'sub')            
            CORERIG.shapeParent_in_place(ml_handleJoints[i].mNode, 
                                         mCrv.mNode, False,
                                         replaceShapes=True)

    
    #Neck=============================================================================================    
    if self.mBlock.neckBuild:
        log.debug("|{0}| >> Neck...".format(_str_func))
        """
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
                    mShape.doName()"""
        
        
        #Root -------------------------------------------------------------------------------------------
        #Grab template handle root - use for sizing, make ball
        mNeckBaseHandle = self.mBlock.msgList_get('templateHandles')[1]
        size_neck = DIST.get_bb_size(mNeckBaseHandle.mNode,True,True) /2
        
        mRoot = ml_joints[0].doCreateAt()
        mRootCrv = cgmMeta.validateObjArg(CURVES.create_fromName('locatorForm', size_neck),
                                          'cgmObject',setClass=True)
        mRootCrv.doSnapTo(mNeckBaseHandle)
        
        #SNAP.go(mRootCrv.mNode, ml_joints[0].mNode,position=False)
        
        CORERIG.shapeParent_in_place(mRoot.mNode,mRootCrv.mNode, False)
        
        ATTR.copy_to(_short_module,'cgmName',mRoot.mNode,driven='target')
        mRoot.doStore('cgmTypeModifier','root')
        mRoot.doName()
        
        CORERIG.colorControl(mRoot.mNode,_side,'sub')
        self.mRigNull.connectChildNode(mRoot,'rigRoot','rigNull')#Connect
        
        
        
        #FK/Ik =======================================================================================    
        ml_fkShapes = self.atBuilderUtils('shapes_fromCast', mode = 'frameHandle')#frameHandle
        
        mHandleFactory.color(ml_fkShapes[0].mNode, controlType = 'main')        
        CORERIG.shapeParent_in_place(ml_fkJoints[0].mNode, ml_fkShapes[0].mNode, True, replaceShapes=True)
        
        for mShape in ml_fkShapes:
            mShape.delete()
        
        """
        for i,mCrv in enumerate(ml_fkShapes):
            CORERIG.colorControl(mCrv.mNode,_side,'main')
            CORERIG.shapeParent_in_place(ml_fkJoints[i].mNode,mCrv.mNode, False, replaceShapes=True)
            for mShape in ml_fkJoints[i].getShapes(asMeta=True):
                mShape.doName()"""

@cgmGEN.Timer
def rig_controls(self):
    _short = self.d_block['shortName']
    _str_func = 'rig_controls'
    log.debug("|{0}| >>  ".format(_str_func)+ '-'*80)
    log.debug("{0}".format(self))
  
    mRigNull = self.mRigNull
    mBlock = self.mBlock
    ml_controlsAll = []#we'll append to this list and connect them all at the end
    mRootParent = self.mDeformNull
    mSettings = mRigNull.settings
    
    mHeadFK = False
    if mRigNull.getMessage('headFK'):
        mHeadFK = mRigNull.headFK    
        
    mHeadIK = mRigNull.headIK
    
    d_controlSpaces = self.atBuilderUtils('get_controlSpaceSetupDict')    
    
    # Drivers ==========================================================================================    
    if self.mBlock.neckBuild:
        if self.mBlock.neckIK:
            mPlug_FKIK = cgmMeta.cgmAttr(mSettings.mNode,'FKIK',attrType='float',minValue=0,maxValue=1,lock=False,keyable=True)
    
        #>> vis Drivers ==============================================================================	
        mPlug_visSub = self.atBuilderUtils('build_visSub')
        mPlug_visRoot = cgmMeta.cgmAttr(mSettings,'visRoot', value = True, attrType='bool', defaultValue = False,keyable = False,hidden = False)
        
    mPlug_visDirect = cgmMeta.cgmAttr(mSettings,'visDirect', value = True,
                                      attrType='bool', defaultValue = False,
                                      keyable = False,hidden = False)
    
    if self.mBlock.headAim:        
        mPlug_aim = cgmMeta.cgmAttr(mSettings.mNode,'blend_aim',attrType='float',
                                    minValue=0,maxValue=1,
                                    lock=False,keyable=True)
        
        
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
                                addDynParentGroup = True,
                                mirrorSide= self.d_module['mirrorDirection'],
                                mirrorAxis="translateX,rotateY,rotateZ",
                                makeAimable = True,
                                **d_controlSpaces)
    
    mHeadIK = _d['mObj']
    mHeadIK.masterGroup.parent = mRootParent
    ml_controlsAll.append(mHeadIK)            
    
    
    #>> headLookAt ========================================================================================
    if mRigNull.getMessage('headLookAt'):
        mHeadLookAt = mRigNull.headLookAt
        log.info("|{0}| >> Found headLookAt : {1}".format(_str_func, mHeadLookAt))
        MODULECONTROL.register(mHeadLookAt,
                               typeModifier='lookAt',
                               addDynParentGroup = True, 
                               mirrorSide= self.d_module['mirrorDirection'],
                               mirrorAxis="translateX,rotateY,rotateZ",
                               makeAimable = False,
                               **d_controlSpaces)
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
    
    mHandleFactory = mBlock.asHandleFactory()
    for mCtrl in ml_controlsAll:
        ATTR.set(mCtrl.mNode,'rotateOrder',self.rotateOrder)
        
        if mCtrl.hasAttr('radius'):
            ATTR.set(mCtrl.mNode,'radius',0)        
        
        ml_pivots = mCtrl.msgList_get('spacePivots')
        if ml_pivots:
            log.debug("|{0}| >> Coloring spacePivots for: {1}".format(_str_func,mCtrl))
            for mPivot in ml_pivots:
                mHandleFactory.color(mPivot.mNode, controlType = 'sub')            
    
    if mHeadIK:
        ATTR.set(mHeadIK.mNode,'rotateOrder',self.rotateOrderHead)
        
    
    mRigNull.msgList_connect('controlsAll',ml_controlsAll)
    mRigNull.moduleSet.extend(ml_controlsAll)
    
    
    
    
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


@cgmGEN.Timer
def rig_segments(self):
    _short = self.d_block['shortName']
    _str_func = 'rig_neckSegment'
    log.debug("|{0}| >>  ".format(_str_func)+ '-'*80)
    log.debug("{0}".format(self))    
    
    if not self.mBlock.neckBuild:
        log.info("|{0}| >> No neck build optioned".format(_str_func))                      
        return True
    
    log.info("|{0}| >> ...".format(_str_func))  
    
    mBlock = self.mBlock
    mRigNull = self.mRigNull
    mRootParent = self.mDeformNull
    mModule = self.mModule
    mRoot = mRigNull.rigRoot
    
    mHeadIK = mRigNull.headIK
    log.info("|{0}| >> Found headIK : {1}".format(_str_func, mHeadIK))
    
    ml_segJoints = mRigNull.msgList_get('segmentJoints')
    ml_blendJoints = mRigNull.msgList_get('blendJoints')
    #ml_rigJoints[0].parent = ml_blendJoints[0]
    #ml_rigJoints[-1].parent = mHeadFK
    ml_handleJoints = mRigNull.msgList_get('handleJoints')
    
    
    if not ml_segJoints:
        log.info("|{0}| >> No segment joints. No segment setup necessary.".format(_str_func))
        return True    
    
    for mJnt in ml_segJoints:
        mJnt.drawStyle = 2
        ATTR.set(mJnt.mNode,'radius',0)    
    
    
    #>> Ribbon setup ========================================================================================
    log.debug("|{0}| >> Ribbon setup...".format(_str_func))
    reload(IK)
    #mSurf = IK.ribbon([mObj.mNode for mObj in ml_rigJoints], baseName = mBlock.cgmName, connectBy='constraint', msgDriver='masterGroup', moduleInstance = mModule)
    mSurf = IK.ribbon([mObj.mNode for mObj in ml_segJoints],
                      baseName = mBlock.cgmName,
                      driverSetup='stable',
                      connectBy='constraint',
                      moduleInstance = mModule)

    mSkinCluster = cgmMeta.validateObjArg(mc.skinCluster ([mHandle.mNode for mHandle in ml_handleJoints],
                                                          mSurf.mNode,
                                                          tsb=True,
                                                          maximumInfluences = 2,
                                                          normalizeWeights = 1,dropoffRate=2.5),
                                          'cgmNode',
                                          setClass=True)

    mSkinCluster.doStore('cgmName', mSurf.mNode)
    mSkinCluster.doName()    

    cgmGEN.func_snapShot(vars())
    ml_segJoints[0].parent = mRoot
    
    
    """
    #>> Neck build ======================================================================================
    if mBlock.neckJoints > 1:
        
        if mBlock.neckControls == 1:
            log.debug("|{0}| >> Simple neck segment...".format(_str_func))
            ml_segmentJoints[0].parent = ml_blendJoints[0] #ml_handleJoints[0]
            ml_segmentJoints[-1].parent = mHeadIK # ml_handleJoints[-1]
            RIGCONSTRAINT.setup_linearSegment(ml_segmentJoints)
            
        else:
            log.debug("|{0}| >> Neck segment...".format(_str_func))    """
            



@cgmGEN.Timer
def rig_frame(self):
    _short = self.d_block['shortName']
    _str_func = ' rig_rigFrame'
    
    log.debug("|{0}| >>  ".format(_str_func)+ '-'*80)
    log.debug("{0}".format(self))    

    mBlock = self.mBlock
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
    mAimParent = ml_blendJoints[-1]
    
    if mRigNull.getMessage('headFK'):
        mHeadFK = mRigNull.headFK

        
    
    #>> headFK ========================================================================================
    """We use the ik head sometimes."""
    
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
                         worldUpObject = mHeadIK.mNode,#mHeadIK.masterGroup.mNode
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
        
        #Trace crv ---------------------------------------------------------------------------------
        log.debug("|{0}| >> head look at track Crv".format(_str_func))
        trackcrv,clusters = CORERIG.create_at([mHeadLookAt.mNode,
                                               mHeadAimJoint.mNode],#ml_handleJoints[1]],
                                              'linearTrack',
                                              baseName = '{0}_headAimTrack'.format(self.d_module['partName']))
    
        mTrackCrv = cgmMeta.asMeta(trackcrv)
        mTrackCrv.p_parent = self.mModule
        mHandleFactory = mBlock.asHandleFactory()
        mHandleFactory.color(mTrackCrv.mNode, controlType = 'sub')
    
        for s in mTrackCrv.getShapes(asMeta=True):
            s.overrideEnabled = 1
            s.overrideDisplayType = 2
        mTrackCrv.doConnectIn('visibility',mPlug_aim.p_combinedShortName)        
        
        
    else:
        log.info("|{0}| >> NO Head IK setup...".format(_str_func))    
    
    #Parent the direct control to the 
    if ml_rigJoints[-1].getMessage('masterGroup'):
        ml_rigJoints[-1].masterGroup.parent = mTopHandleDriver
    else:
        ml_rigJoints[-1].parent = mTopHandleDriver
        
    
    #>> Neck build ======================================================================================
    if mBlock.neckBuild:
        log.debug("|{0}| >> Neck...".format(_str_func))
        
        if not mRigNull.getMessage('rigRoot'):
            raise ValueError,"No rigRoot found"
        
        mRoot = mRigNull.rigRoot
        mSettings = mRigNull.settings
        
        if self.mBlock.neckIK:
            log.debug("|{0}| >> Neck IK...".format(_str_func))
            ml_ikJoints = mRigNull.msgList_get('ikJoints')
            ml_blendJoints = mRigNull.msgList_get('blendJoints')
            
            mPlug_FKIK = cgmMeta.cgmAttr(mHeadIK.mNode,'FKIK',attrType='float',lock=False,keyable=True)
            
            #>>> Setup a vis blend result
            mPlug_FKon = cgmMeta.cgmAttr(mSettings,'result_FKon',attrType='float',defaultValue = 0,keyable = False,lock=True,hidden=True)	
            mPlug_IKon = cgmMeta.cgmAttr(mSettings,'result_IKon',attrType='float',defaultValue = 0,keyable = False,lock=True,hidden=True)	
        
            NODEFACTORY.createSingleBlendNetwork(mPlug_FKIK.p_combinedName,
                                                 mPlug_IKon.p_combinedName,
                                                 mPlug_FKon.p_combinedName)
              
            mPlug_FKon.doConnectOut("{0}.visibility".format(ml_fkJoints[0].masterGroup.mNode))
            #mPlug_IKon.doConnectOut("%s.visibility"%ikGroup)            
            
            
            # Create head position driver ------------------------------------------------
            mHeadDriver = mHeadIK.doCreateAt()
            mHeadDriver.rename('headBlendDriver')
            mHeadDriver.parent = mRoot
            
            mHeadIKDriver = mHeadIK.doCreateAt()
            mHeadIKDriver.rename('headIKDriver')
            mHeadIKDriver.parent = mRoot
            
            mHeadFKDriver = mHeadIK.doCreateAt()
            mHeadFKDriver.rename('headFKDriver')
            mHeadFKDriver.parent = ml_fkJoints[-1]
            
            mHeadIK.connectChildNode(mHeadDriver.mNode, 'blendDriver')
            
            RIGCONSTRAINT.blendChainsBy(mHeadFKDriver.mNode,
                                        mHeadIKDriver.mNode,
                                        mHeadDriver.mNode,
                                        driver = mPlug_FKIK.p_combinedName,l_constraints=['point','orient'])            
            
            
            # Neck controls --------------------------------------------------------------
            if mBlock.neckControls == 1:
                log.debug("|{0}| >> Single joint IK...".format(_str_func))
                mc.aimConstraint(mHeadIK.mNode,
                                 ml_ikJoints[0].mNode,
                                 maintainOffset = True, weight = 1,
                                 aimVector = self.d_orientation['vectorAim'],
                                 upVector = self.d_orientation['vectorUp'],
                                 worldUpVector = self.d_orientation['vectorOut'],
                                 worldUpObject = mRoot.mNode,
                                 worldUpType = 'objectRotation' )
                mc.pointConstraint(mHeadIK.mNode,
                                   ml_ikJoints[-1].mNode,
                                   maintainOffset = True)
                
                
            #>> handleJoints ========================================================================================
            if ml_handleJoints:
                log.debug("|{0}| >> Found Handles...".format(_str_func))
                ml_handleJoints[-1].masterGroup.parent = mHeadIK
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
                
                ml_baseIKDrivers[-1].parent = mHeadIK
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
                
                
            if mBlock.neckJoints == 1:
                log.debug("|{0}| >> Single neckJoint setup...".format(_str_func))                
                ml_rigJoints[0].masterGroup.parent = ml_blendJoints[0]
                
                mc.aimConstraint(mHeadIK.mNode,
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
            
    
def rig_cleanUp(self):
    _short = self.d_block['shortName']
    _str_func = 'rig_cleanUp'
    log.debug("|{0}| >>  ".format(_str_func)+ '-'*80)
    log.debug("{0}".format(self))
    
    mBlock = self.mBlock
    mRigNull = self.mRigNull
    mHeadIK = mRigNull.headIK
    mSettings = mRigNull.settings
    
    mRoot = mRigNull.rigRoot
    if not mRoot.hasAttr('cgmAlias'):
        mRoot.addAttr('cgmAlias','root')    
    
    mMasterControl= self.d_module['mMasterControl']
    mMasterDeformGroup= self.d_module['mMasterDeformGroup']    
    mMasterNull = self.d_module['mMasterNull']
    mModuleParent = self.d_module['mModuleParent']
    mPlug_globalScale = self.d_module['mPlug_globalScale']
    
    if not self.mConstrainNull.hasAttr('cgmAlias'):
        self.mConstrainNull.addAttr('cgmAlias','{0}_rootNull'.format(self.d_module['partName']))    
    
    #>>  Parent and constraining joints and rig parts =======================================================
    if mSettings != mHeadIK:
        mSettings.masterGroup.parent = mHeadIK
    
    #>>  DynParentGroups - Register parents for various controls ============================================
    ml_baseDynParents = []
    ml_endDynParents = self.ml_dynParentsAbove + self.ml_dynEndParents# + [mRoot]
    ml_ikDynParents = []    
    """
    #...head -----------------------------------------------------------------------------------
    ml_baseHeadDynParents = []
    
    #ml_headDynParents = [ml_controlsFK[0]]
    if mModuleParent:
        mi_parentRigNull = mModuleParent.rigNull
        if mi_parentRigNull.getMessage('controlIK'):
            ml_baseHeadDynParents.append( mi_parentRigNull.controlIK )	    
        if mi_parentRigNull.getMessage('controlIKBase'):
            ml_baseHeadDynParents.append( mi_parentRigNull.controlIKBase )
        if mi_parentRigNull.getMessage('rigRoot'):
            ml_baseHeadDynParents.append( mi_parentRigNull.rigRoot )
        ml_parentRigJoints =  mi_parentRigNull.msgList_get('rigJoints')
        if ml_parentRigJoints:
            ml_used = []
            for mJnt in ml_parentRigJoints:
                if mJnt in ml_used:continue
                if mJnt in [ml_parentRigJoints[0],ml_parentRigJoints[-1]]:
                    ml_baseHeadDynParents.append( mJnt.masterGroup)
                    ml_used.append(mJnt)
                    
    ml_baseHeadDynParents.append(mMasterNull.puppetSpaceObjectsGroup)"""
    
    #...Root controls ================================================================================
    log.debug("|{0}| >>  Root: {1}".format(_str_func,mRoot))                
    #mParent = mRoot.getParent(asMeta=True)
    ml_targetDynParents = [self.mConstrainNull]

    #if not mParent.hasAttr('cgmAlias'):
    #    mParent.addAttr('cgmAlias',self.d_module['partName'] + 'base')
    #ml_targetDynParents.append(mParent)    
    
    ml_targetDynParents.extend(ml_endDynParents)

    mDynGroup = mRoot.dynParentGroup
    mDynGroup.dynMode = 2

    for mTar in ml_targetDynParents:
        mDynGroup.addDynParent(mTar)
    mDynGroup.rebuild()
    mDynGroup.dynFollow.p_parent = self.mDeformNull    
    
    
    #Head -------------------------------------------------------------------------------------------
    ml_headDynParents = []
  
    ml_headDynParents.extend(mHeadIK.msgList_get('spacePivots',asMeta = True))
    ml_headDynParents.extend(ml_endDynParents)
    
    mBlendDriver =  mHeadIK.getMessage('blendDriver',asMeta=True)
    if mBlendDriver:
        mBlendDriver = mBlendDriver[0]
        ml_headDynParents.insert(0, mBlendDriver)  
        mBlendDriver.addAttr('cgmAlias','neckDriver')
    #pprint.pprint(ml_headDynParents)

    #Add our parents
    mDynGroup = mHeadIK.dynParentGroup
    log.info("|{0}| >> dynParentSetup : {1}".format(_str_func,mDynGroup))  
    mDynGroup.dynMode = 2

    for o in ml_headDynParents:
        mDynGroup.addDynParent(o)
    mDynGroup.rebuild()

    mDynGroup.dynFollow.parent = mMasterDeformGroup
    
    #...headLookat ---------------------------------------------------------------------------------------
    if mBlock.headAim:
        log.info("|{0}| >> HeadAim setup...".format(_str_func))
        
        mPlug_aim = cgmMeta.cgmAttr(mSettings.mNode,'blend_aim',attrType='float',lock=False,keyable=True)
        
        #mHeadFKJoint = mRigNull.getMessage('fkHeadJoint', asMeta=True)[0]
        #mHeadAimJoint = mRigNull.getMessage('aimHeadJoint', asMeta=True)[0]
        #mHeadBlendJoint = mRigNull.getMessage('blendHeadJoint', asMeta=True)[0]
        #mHeadFKDynParentGroup = mHeadIK.dynParentGroup
        
        mHeadLookAt = mRigNull.headLookAt        
        mHeadLookAt.setAttrFlags(attrs='v')
        
        #...dynParentGroup...
        ml_headLookAtDynParents = []
        ml_headLookAtDynParents.extend(mHeadLookAt.msgList_get('spacePivots',asMeta = True))
        ml_headLookAtDynParents.extend(ml_endDynParents)    
        
        ml_headDynParents.insert(0, mHeadIK)
        #mHeadIK.masterGroup.addAttr('cgmAlias','headRoot')
        
        #Add our parents...
        mDynGroup = mHeadLookAt.dynParentGroup
        log.info("|{0}| >> dynParentSetup : {1}".format(_str_func,mDynGroup))  
    
        for o in ml_headDynParents:
            mDynGroup.addDynParent(o)
        mDynGroup.rebuild()
        
    #Lock and hide =================================================================================
    ml_controls = mRigNull.msgList_get('controlsAll')
    
    for mCtrl in ml_controls:
        if mCtrl.hasAttr('radius'):
            ATTR.set_hidden(mCtrl.mNode,'radius',True)
        
        if mCtrl.getMessage('masterGroup'):
            mCtrl.masterGroup.setAttrFlags()
    
    if not mBlock.scaleSetup:
        log.debug("|{0}| >> No scale".format(_str_func))
        for mCtrl in ml_controls:
            ATTR.set_standardFlags(mCtrl.mNode, ['scale'])
    
        
    
    
    #>>  Attribute defaults =================================================================================
    
    mRigNull.version = self.d_block['buildVersion']
    mBlock.blockState = 'rig'

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
    _str_func = 'build_proxyMesh'
    log.debug("|{0}| >>  ".format(_str_func)+ '-'*80)
    log.debug("{0}".format(self))
    
    mBlock = self.mBlock
    mRigNull = self.mRigNull
    mHeadIK = mRigNull.headIK
    mSettings = mRigNull.settings
    mPuppetSettings = self.d_module['mMasterControl'].controlSettings
    
    directProxy = mBlock.proxyDirect
    
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
    if directProxy:
        log.debug("|{0}| >> directProxy... ".format(_str_func))
        _settings = self.mRigNull.settings.mNode
        
    
    mGroup = mBlock.msgList_get('headMeshProxy')[0].getParent(asMeta=True)
    l_headGeo = mGroup.getChildren(asMeta=False)
    l_vis = mc.ls(l_headGeo, visible = True)
    ml_headStuff = []
    
    for i,o in enumerate(l_vis):
        log.debug("|{0}| >> visible head: {1}...".format(_str_func,o))
        
        mObj = cgmMeta.validateObjArg(mc.duplicate(o, po=False, ic = False)[0])
        ml_headStuff.append(  mObj )
        mObj.parent = ml_rigJoints[-1]
        
        ATTR.copy_to(ml_rigJoints[-1].mNode,'cgmName',mObj.mNode,driven = 'target')
        mObj.addAttr('cgmIterator',i)
        mObj.addAttr('cgmType','proxyGeo')
        mObj.doName()
        
        if directProxy:
            CORERIG.shapeParent_in_place(ml_rigJoints[-1].mNode,mObj.mNode,True,True)
            CORERIG.colorControl(ml_rigJoints[-1].mNode,_side,'main',directProxy=True)        
        
    if mBlock.neckBuild:#...Neck =====================================================================
        log.debug("|{0}| >> neckBuild...".format(_str_func))
        
        # Create ---------------------------------------------------------------------------
        if mBlock.neckJoints == 1:
            mProxy = ml_rigJoints[0].doCreateAt(setClass=True)
            mPrerigProxy = mBlock.getMessage('prerigLoftMesh',asMeta=True)[0]
            CORERIG.shapeParent_in_place(mProxy.mNode, mPrerigProxy.mNode)
            
            ATTR.copy_to(ml_rigJoints[0].mNode,'cgmName',mProxy.mNode,driven = 'target')
            mProxy.addAttr('cgmType','proxyGeo')
            mProxy.doName()
            mProxy.parent = ml_rigJoints[0]
            ml_neckProxy = [mProxy]
            
            if directProxy:
                CORERIG.shapeParent_in_place(ml_rigJoints[0].mNode,mProxy.mNode,True,True)
                CORERIG.colorControl(ml_rigJoints[0].mNode,_side,'main',directProxy=True)            
            
        else:
            ml_neckProxy = cgmMeta.validateObjListArg(self.atBuilderUtils('mesh_proxyCreate', ml_rigJoints),'cgmObject')
            log.debug("|{0}| >> created: {1}".format(_str_func,ml_neckProxy))
            
            for i,mGeo in enumerate(ml_neckProxy):
                mGeo.parent = ml_rigJoints[i]
                ATTR.copy_to(ml_rigJoints[0].mNode,'cgmName',mGeo.mNode,driven = 'target')
                mGeo.addAttr('cgmIterator',i+1)
                mGeo.addAttr('cgmType','proxyGeo')
                mGeo.doName()
                
                if directProxy:
                    CORERIG.shapeParent_in_place(ml_rigJoints[i].mNode,mGeo.mNode,True,True)
                    CORERIG.colorControl(ml_rigJoints[i].mNode,_side,'main',directProxy=True)                
    
    for mProxy in ml_neckProxy + ml_headStuff:
        CORERIG.colorControl(mProxy.mNode,_side,'main',transparent=False,proxy=True)
        
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
            
    if directProxy:
        for mObj in ml_rigJoints:
            for mShape in mObj.getShapes(asMeta=True):
                #mShape.overrideEnabled = 0
                mShape.overrideDisplayType = 0
                ATTR.connect("{0}.visDirect".format(_settings), "{0}.overrideVisibility".format(mShape.mNode))
        
    mRigNull.msgList_connect('proxyMesh', ml_neckProxy + ml_headStuff)




















