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
import cgm.core.cgm_RigMeta as cgmRIGMETA

for m in DIST,POS,MATH,IK,CONSTRAINT,LOC,BLOCKUTILS,BUILDERUTILS,CORERIG,RAYS,JOINT,RIGCONSTRAINT:
    reload(m)
    
# From cgm ==============================================================
from cgm.core import cgm_Meta as cgmMeta

#=============================================================================================================
#>> Block Settings
#=============================================================================================================
__version__ = 'alpha.1.05162018'
__autoTemplate__ = False
__dimensions = [15.2, 23.2, 19.7]
__menuVisible__ = True

#These are our base dimensions. In this case it is for human
__dimensions_by_type = {'box':[22,22,22],
                        'human':[15.2, 23.2, 19.7]}

__l_rigBuildOrder__ = ['rig_dataBuffer',
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
                   #'ikSetup',
                   #'ikBase',
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
                 
                 'squashMeasure' : 'none:arcLength:pointDist',
                 'squash' : 'none:simple:single:both',
                 'squashExtraControl' : 'bool',
                 'squashFactorMax':'float',
                 'squashFactorMin':'float',
             
                 'ribbonAim': 'none:stable:stableBlend',
                 'ribbonConnectBy': 'constraint:matrix',
                 'segmentMidIKControl':'bool',                 
                 
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
                     'attachPoint':'end',
                     'neckIK':'ribbon',
                     
                     'squashMeasure':'arcLength',
                     'squash':'simple',
                     'squashFactorMax':1.0,
                     'squashFactorMin':1.0,
                 
                     'segmentMidIKControl':True,
                     'squash':'both',
                     'squashExtraControl':True,
                     'ribbonAim':'stable',
                     
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
    _crv = CURVES.create_fromName(name='axis3d',#'arrowsAxis', 
                                  direction = 'z+', size = _size/4)
    SNAP.go(_crv,self.mNode,)    
    CORERIG.shapeParent_in_place(self.mNode,_crv,False)
    
    mHandleFactory = self.asHandleFactory()
    self.addAttr('cgmColorLock',True,lock=True,visible=False)
    #mHandleFactory.color(self.mNode,controlType='main')
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
    
    if mBlock.neckControls > 1:
        raise ValueError,"Don't have support for more than one neckControl yet. Found: {0}".format(mBlock.neckControls)
    
    if mBlock.segmentMidIKControl and mBlock.neckJoints < 2:
        raise ValueError,"Must have more than one neck joint with segmentMidIKControl"
        

@cgmGEN.Timer
def rig_dataBuffer(self):
    _short = self.d_block['shortName']
    _str_func = 'rig_dataBuffer'
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
        

    log.debug(cgmGEN._str_subLine)
    
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
    log.debug(cgmGEN._str_subLine)
    
    #Squash stretch logic  =================================================================================
    log.debug("|{0}| >> Squash stretch..".format(_str_func))
    self.b_scaleSetup = mBlock.scaleSetup
    
    self.b_squashSetup = False
    
    self.d_squashStretch = {}
    self.d_squashStretchIK = {}
    
    _squashStretch = None
    if mBlock.squash:
        _squashStretch =  mBlock.getEnumValueString('squash')
        self.b_squashSetup = True
    self.d_squashStretch['squashStretch'] = _squashStretch
    
    _squashMeasure = None
    if mBlock.squashMeasure:
        _squashMeasure =  mBlock.getEnumValueString('squashMeasure')    
    self.d_squashStretch['squashStretchMain'] = _squashMeasure    

    _driverSetup = None
    if mBlock.ribbonAim:
        _driverSetup =  mBlock.getEnumValueString('ribbonAim')
    self.d_squashStretch['driverSetup'] = _driverSetup

    
    self.d_squashStretch['extraSquashControl'] = mBlock.squashExtraControl
    self.d_squashStretch['squashFactorMax'] = mBlock.squashFactorMax
    self.d_squashStretch['squashFactorMin'] = mBlock.squashFactorMin
    
    log.debug("|{0}| >> self.d_squashStretch..".format(_str_func))    
    pprint.pprint(self.d_squashStretch)
    
    #Check for mid control and even handle count to see if w need an extra curve
    if mBlock.segmentMidIKControl:
        if MATH.is_even(mBlock.neckControls):
            self.d_squashStretchIK['sectionSpans'] = 2
            
    if self.d_squashStretchIK:
        log.debug("|{0}| >> self.d_squashStretchIK..".format(_str_func))    
        pprint.pprint(self.d_squashStretchIK)
    
    
    if not self.b_scaleSetup:
        pass
    
    log.debug("|{0}| >> self.b_scaleSetup: {1}".format(_str_func,self.b_scaleSetup))
    log.debug("|{0}| >> self.b_squashSetup: {1}".format(_str_func,self.b_squashSetup))
    
    log.debug(cgmGEN._str_subLine)
    
    #segintbaseindex =============================================================================
    str_ikBase = ATTR.get_enumValueString(mBlock.mNode,'ikBase')
    log.debug("|{0}| >> IK Base: {1}".format(_str_func,str_ikBase))    
    self.int_segBaseIdx = 0
    if str_ikBase in ['hips']:
        self.int_segBaseIdx = 1
    log.debug("|{0}| >> self.int_segBaseIdx: {1}".format(_str_func,self.int_segBaseIdx))
    
    log.debug(cgmGEN._str_subLine)

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
    _l_orient = [_str_orientation[0],_str_orientation[1],_str_orientation[2]]
    self.ro_base = "{0}{1}{2}".format(_str_orientation[1],_str_orientation[2],_str_orientation[0])
    self.ro_head = "{2}{0}{1}".format(_str_orientation[0],_str_orientation[1],_str_orientation[2])
    self.ro_headLookAt = "{0}{2}{1}".format(_str_orientation[0],_str_orientation[1],_str_orientation[2])
    log.debug("|{0}| >> rotateOrder | self.ro_base: {1}".format(_str_func,self.ro_base))
    log.debug("|{0}| >> rotateOrder | self.ro_head: {1}".format(_str_func,self.ro_head))
    log.debug("|{0}| >> rotateOrder | self.ro_headLookAt: {1}".format(_str_func,self.ro_headLookAt))

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
    ml_templateHandles = mBlock.msgList_get('templateHandles')
    
    BLOCKUTILS.skeleton_pushSettings(ml_joints, self.d_orientation['str'], self.d_module['mirrorDirection'])
                                     #d_rotateOrders, d_preferredAngles)
    
    log.info("|{0}| >> Head...".format(_str_func))  
    
    ml_rigJoints = BLOCKUTILS.skeleton_buildDuplicateChain(mBlock, ml_joints, 'rig', self.mRigNull,'rigJoints',blockNames=False)
    
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
        #return mOrientHelper.getAxisVector('y+')
        ml_fkJoints = BLOCKUTILS.skeleton_buildHandleChain(mBlock,'fk','fkJoints',mOrientHelper=ml_templateHandles[1].orientHelper)
        ml_jointsToHide.extend(ml_fkJoints)
        mOrientHelper = ml_templateHandles[1].orientHelper
        #Because
        vec_chainUp =mOrientHelper.getAxisVector('y+')

        if self.mBlock.neckIK:
            log.info("|{0}| >> buildIK on. Building blend and IK chains...".format(_str_func))  
            ml_blendJoints = BLOCKUTILS.skeleton_buildHandleChain(mBlock,'blend','blendJoints')
            ml_ikJoints = BLOCKUTILS.skeleton_buildHandleChain(mBlock,'ik','ikJoints')
            ml_jointsToConnect.extend(ml_ikJoints)
            ml_jointsToHide.extend(ml_blendJoints)
            
            for i,mJnt in enumerate(ml_ikJoints):
                if mJnt not in [ml_ikJoints[0],ml_ikJoints[-1]]:
                    mJnt.preferredAngle = mJnt.jointOrient
                    
            
            if mBlock.segmentMidIKControl:
                log.debug("|{0}| >> Creating ik mid control...".format(_str_func))  
                #Lever...
                mMidIK = ml_rigJoints[0].doDuplicate(po=True)
                mMidIK.cgmName = 'neck_segMid'
                mMidIK.p_parent = False
                mMidIK.doName()
            
                mMidIK.p_position = DIST.get_average_position([ml_rigJoints[self.int_segBaseIdx].p_position,
                                                               ml_rigJoints[-1].p_position])
            
                SNAP.aim(mMidIK.mNode, ml_rigJoints[-1].mNode, 'z+','y+','vector',
                         vec_chainUp)
                         #mBlock.rootUpHelper.getAxisVector('y+'))
                reload(JOINT)
                JOINT.freezeOrientation(mMidIK.mNode)
                mRigNull.connectChildNode(mMidIK,'controlSegMidIK','rigNull')            
    
        
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
                
            ml_segmentChain = BLOCKUTILS.skeleton_buildDuplicateChain(mBlock,
                                                                      ml_joints,
                                                                      None, mRigNull,
                                                                      'segmentJoints',
                                                                      cgmType = 'segJnt')
            JOINT.orientChain(ml_segmentChain,
                              worldUpAxis=vec_chainUp)
            
            
            for i,mJnt in enumerate(ml_rigJoints):
                if mJnt != ml_rigJoints[-1]:
                    mJnt.parent = ml_segmentChain[i]
                    mJnt.connectChildNode(ml_segmentChain[i],'driverJoint','sourceJoint')#Connect
                else:
                    mJnt.p_parent = False
                    
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

#@cgmGEN.Timer
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
    mRigNull = self.mRigNull
    
    #l_toBuild = ['segmentFK_Loli','segmentIK']
    #mShapeCast.go(self._mi_module,l_toBuild, storageInstance=self)#This will store controls to a dict called    
    
    #Get our base size from the block
    _jointOrientation = self.d_orientation['str']
    
    _size = DIST.get_bb_size(ml_templateHandles[0].mNode,True,True)
    _side = BLOCKUTILS.get_side(self.mBlock)
    _short_module = self.mModule.mNode
    ml_joints = self.d_joints['ml_moduleJoints']
    _offset = self.v_offset
    
    #Logic ====================================================================================

    
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
        
        self.mRigNull.connectChildNode(mLookAt,'lookAt','rigNull')#Connect
    
    
    #Head control....-------------------------------------------------------------------------------
    if not mBlock.neckBuild:
        b_FKIKhead = False
        if mBlock.neckControls > 1 and mBlock.neckBuild: 
            log.info("|{0}| >> FK/IK head necessary...".format(_str_func))          
            b_FKIKhead = True            
        
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
    else:
        mHeadTar = ml_rigJoints[-1]
        mFKHead = ml_rigJoints[-1].doCreateAt()
        
        CORERIG.shapeParent_in_place(mFKHead,ml_templateHandles[0].mNode,True)
        mFKHead = cgmMeta.validateObjArg(mFKHead,'cgmObject',setClass=True)
        mFKHead.doCopyNameTagsFromObject(mHeadTar.mNode,
                                        ignore=['cgmType','cgmTypeModifier'])        
        mFKHead.doStore('cgmTypeModifier','fk')
        mFKHead.doName()
        
        mHandleFactory.color(mFKHead.mNode,controlType='main')
        
        
        if mBlock.neckIK:
            ml_blendJoints = mRigNull.msgList_get('blendJoints')
            
            mIKHead = mFKHead.doDuplicate(po=False)
            mIKHead.doStore('cgmTypeModifier','ik')
            mIKHead.doName()            
            self.mRigNull.connectChildNode(mIKHead,'controlIK','rigNull')#Connect
            self.mRigNull.connectChildNode(mIKHead,'headIK','rigNull')#Connect
            
            #Fix fk.... ---------------------------------------------------------------------------
            CORERIG.shapeParent_in_place(ml_fkJoints[-1].mNode, mFKHead.mNode,False)            
            mFKHead = ml_fkJoints[-1]
            
            #Base IK...---------------------------------------------------------------------------------
            log.debug("|{0}| >> baseIK...".format(_str_func))
            ml_ikJoints = mRigNull.msgList_get('ikJoints')
            #mIK_templateHandle = self.mRootTemplateHandle
            #bb_ik = mHandleFactory.get_axisBox_size(mIK_templateHandle.mNode)
            #_ik_shape = CURVES.create_fromName('sphere', size = bb_ik)
        
            _ik_shape = self.atBuilderUtils('shapes_fromCast',
                                            targets = [ mObj for mObj in ml_rigJoints[:1]],
                                            offset = _offset,
                                            mode = 'castHandle')[0].mNode
        
            mIKBaseShape = cgmMeta.validateObjArg(_ik_shape, 'cgmObject',setClass=True)
        
            mIKBaseCrv = ml_ikJoints[0].doCreateAt()
            mIKBaseCrv.doCopyNameTagsFromObject(ml_fkJoints[0].mNode,ignore=['cgmType'])
            CORERIG.shapeParent_in_place(mIKBaseCrv.mNode, mIKBaseShape.mNode, False)                            
        
            mIKBaseCrv.doStore('cgmTypeModifier','ikBase')
            mIKBaseCrv.doName()
        
            mHandleFactory.color(mIKBaseCrv.mNode, controlType = 'main',transparent=True)
        
            mHandleFactory.color(mIKBaseCrv.mNode, controlType = 'main')        
            self.mRigNull.connectChildNode(mIKBaseCrv,'controlIKBase','rigNull')#Connect                    

        self.mRigNull.connectChildNode(mFKHead,'headFK','rigNull')#Connect
        
                
        
        """
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
             """
        
        #Settings =================================================================================
        pos = mHeadHelper.getPositionByAxisDistance('z+', _size * .75)
        
        mTar = ml_rigJoints[-1]
        
        vector = mHeadHelper.getAxisVector('y+')
        newPos = DIST.get_pos_by_vec_dist(pos,vector,_size * .5)
    
        settings = CURVES.create_fromName('gear',_size/5,'x+')
        mSettingsShape = cgmMeta.validateObjArg(settings,'cgmObject')
        mSettings = cgmMeta.validateObjArg(mTar.doCreateAt(),'cgmObject',setClass=True)
        
        mSettings.p_position = newPos
        mSettingsShape.p_position = newPos
    
        ATTR.copy_to(_short_module,'cgmName',mSettings.mNode,driven='target')
        #mSettings.doStore('cgmName','head')
        mSettings.doStore('cgmTypeModifier','settings')
        mSettings.doName()
        #CORERIG.colorControl(mSettings.mNode,_side,'sub')
        
        SNAP.aim_atPoint(mSettingsShape.mNode,
                         mTar.p_position,
                         aimAxis=_jointOrientation[0]+'+',
                         mode = 'vector',
                         vectorUp= mTar.getAxisVector(_jointOrientation[0]+'-'))
        
        CORERIG.shapeParent_in_place(mSettings.mNode, mSettingsShape.mNode,False)
        mHandleFactory.color(mSettings.mNode,controlType='sub')
        
        self.mRigNull.connectChildNode(mSettings,'settings','rigNull')#Connect
        
        #Neck ================================================================================
        log.debug("|{0}| >> Neck...".format(_str_func))
        #Root -------------------------------------------------------------------------------------------
        #Grab template handle root - use for sizing, make ball
        mNeckBaseHandle = self.mBlock.msgList_get('templateHandles')[1]
        size_neck = DIST.get_bb_size(mNeckBaseHandle.mNode,True,True) /2

        mRoot = ml_joints[0].doCreateAt()
        mRootCrv = cgmMeta.validateObjArg(CURVES.create_fromName('locatorForm', size_neck),
                                          'cgmObject',setClass=True)
        mRootCrv.doSnapTo(ml_joints[0])

        #SNAP.go(mRootCrv.mNode, ml_joints[0].mNode,position=False)

        CORERIG.shapeParent_in_place(mRoot.mNode,mRootCrv.mNode, False)

        ATTR.copy_to(_short_module,'cgmName',mRoot.mNode,driven='target')
        mRoot.doStore('cgmTypeModifier','root')
        mRoot.doName()

        CORERIG.colorControl(mRoot.mNode,_side,'sub')
        self.mRigNull.connectChildNode(mRoot,'rigRoot','rigNull')#Connect

        #controlSegMidIK =============================================================================
        if mRigNull.getMessage('controlSegMidIK'):
            log.debug("|{0}| >> controlSegMidIK...".format(_str_func))            
            mControlSegMidIK = mRigNull.getMessage('controlSegMidIK',asMeta=1)[0]
            
            ml_shapes = self.atBuilderUtils('shapes_fromCast',
                                            targets = mControlSegMidIK,
                                            offset = _offset,
                                            mode = 'limbSegmentHandleBack')#'simpleCast  limbSegmentHandle
            
            CORERIG.shapeParent_in_place(mControlSegMidIK.mNode, ml_shapes[0].mNode,False)
            
            mControlSegMidIK.doStore('cgmTypeModifier','ik')
            mControlSegMidIK.doStore('cgmType','handle')
            mControlSegMidIK.doName()            
    
            mHandleFactory.color(mControlSegMidIK.mNode, controlType = 'sub')
        

        #FK/Ik =======================================================================================    
        ml_fkShapes = self.atBuilderUtils('shapes_fromCast', mode = 'frameHandle')#frameHandle

        mHandleFactory.color(ml_fkShapes[0].mNode, controlType = 'main')        
        CORERIG.shapeParent_in_place(ml_fkJoints[0].mNode, ml_fkShapes[0].mNode, True, replaceShapes=True)

        for i,mShape in enumerate(ml_fkJoints[:-1]):
            mShape = ml_fkShapes[i]
            mHandleFactory.color(mShape.mNode, controlType = 'main')        
            CORERIG.shapeParent_in_place(ml_fkJoints[i].mNode, mShape.mNode, True, replaceShapes=True)
            
            mShape.delete()

    
    
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
    

    #Handles ===========================================================================================
    ml_handleJoints = self.mRigNull.msgList_get('handleJoints')

    if ml_handleJoints:
        log.debug("|{0}| >> Found Handle joints...".format(_str_func))
        #l_uValues = MATH.get_splitValueList(.01,.99, len(ml_handleJoints))
        ml_handleShapes = self.atBuilderUtils('shapes_fromCast',
                                              targets = ml_handleJoints,
                                              offset = _offset,
                                              mode = 'limbSegmentHandleBack')#'segmentHandle') limbSegmentHandle


        for i,mCrv in enumerate(ml_handleShapes):
            log.debug("|{0}| >> Shape: {1} | Handle: {2}".format(_str_func,mCrv.mNode,ml_handleJoints[i].mNode ))                
            mHandleFactory.color(mCrv.mNode, controlType = 'sub')            
            CORERIG.shapeParent_in_place(ml_handleJoints[i].mNode, 
                                         mCrv.mNode, False,
                                         replaceShapes=True)




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
    
    mHeadFK = mRigNull.getMessageAsMeta('headFK')
    mHeadIK = mRigNull.getMessageAsMeta('headIK')
    
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
    
            mObj = d_buffer['mObj']
            #mObj.axisAim = "%s+"%self._go._jointOrientation[0]
            #mObj.axisUp= "%s+"%self._go._jointOrientation[1]	
            #mObj.axisOut= "%s+"%self._go._jointOrientation[2]
            #try:i_obj.drawStyle = 2#Stick joint draw style	    
            #except:self.log_error("{0} Failed to set drawStyle".format(i_obj.p_nameShort))
            ATTR.set_hidden(mObj.mNode,'radius',True)
            
            
        ml_blend = mRigNull.msgList_get('blendJoints')
        
        mControlBaseIK = mRigNull.getMessageAsMeta('controlIKBase')
        if mControlBaseIK:
            mControlBaseIK = mRigNull.controlIKBase
            log.debug("|{0}| >> Found controlBaseIK : {1}".format(_str_func, mControlBaseIK))
            
            _d = MODULECONTROL.register(mControlBaseIK,
                                        addDynParentGroup = True, 
                                        mirrorSide= self.d_module['mirrorDirection'],
                                        mirrorAxis="translateX,rotateY,rotateZ",
                                        makeAimable = True,
                                        **d_controlSpaces)
                                        
            
            mControlBaseIK = _d['mObj']
            mControlBaseIK.masterGroup.parent = mRootParent
            ml_controlsAll.append(mControlBaseIK)
            
            #Register our snapToTarget -------------------------------------------------------------
            self.atUtils('get_switchTarget', mControlBaseIK,ml_blend[0])

            
            
        mControlSegMidIK = False
        #controlSegMidIK =============================================================================
        if mRigNull.getMessage('controlSegMidIK'):
            mControlSegMidIK = mRigNull.controlSegMidIK
            log.debug("|{0}| >> found controlSegMidIK: {1}".format(_str_func,mControlSegMidIK))
            
            _d = MODULECONTROL.register(mControlSegMidIK,
                                        addDynParentGroup = True, 
                                        mirrorSide= self.d_module['mirrorDirection'],
                                        mirrorAxis="translateX,rotateY,rotateZ",
                                        makeAimable = True,
                                        **d_controlSpaces)
            
            
            mControlSegMidIK = _d['mObj']
            mControlSegMidIK.masterGroup.parent = mRootParent
            ml_controlsAll.append(mControlSegMidIK)
        
            #Register our snapToTarget -------------------------------------------------------------
            self.atUtils('get_switchTarget', mControlSegMidIK,ml_blend[ MATH.get_midIndex(len(ml_blend))])        


    #ikHead ========================================================================================
    log.info("|{0}| >> Found headIK : {1}".format(_str_func, mHeadIK))
    ml_blendJoints = mRigNull.msgList_get('blendJoints')
    
    _d = MODULECONTROL.register(mHeadIK,
                                addDynParentGroup = True,
                                mirrorSide= self.d_module['mirrorDirection'],
                                mirrorAxis="translateX,rotateY,rotateZ",
                                makeAimable = True,
                                **d_controlSpaces)
    
    mHeadIK = _d['mObj']
    mHeadIK.masterGroup.parent = mRootParent
    ml_controlsAll.append(mHeadIK)
    
    self.atUtils('get_switchTarget', mHeadIK, ml_blendJoints[-1])
    
    
    #>> headLookAt ========================================================================================
    mHeadLookAt = False
    if mRigNull.getMessage('lookAt'):
        mHeadLookAt = mRigNull.lookAt
        log.info("|{0}| >> Found lookAt : {1}".format(_str_func, mHeadLookAt))
        MODULECONTROL.register(mHeadLookAt,
                               typeModifier='lookAt',
                               addDynParentGroup = True, 
                               mirrorSide= self.d_module['mirrorDirection'],
                               mirrorAxis="translateX,rotateY,rotateZ",
                               makeAimable = False,
                               **d_controlSpaces)
        mHeadLookAt.masterGroup.parent = mRootParent
        ml_controlsAll.append(mHeadLookAt)
        
        if mHeadIK:
            mHeadLookAt.doStore('controlIK', mHeadIK.mNode)
        if mHeadFK:
            mHeadLookAt.doStore('controlFK', mHeadFK.mNode)
            
        #int_mid = MATH.get_midIndex(len(ml_blend))

        
    
    #>> settings ========================================================================================
    if mHeadFK:
        mSettings = mRigNull.settings
        log.info("|{0}| >> Found settings : {1}".format(_str_func, mSettings))
        
        MODULECONTROL.register(mSettings,
                               mirrorSide= self.d_module['mirrorDirection'],
                               )
        
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
    
            mObj = d_buffer['mObj']
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
        mObj = d_buffer['mObj']
        ATTR.set_hidden(mObj.mNode,'radius',True)        
        if mObj.hasAttr('cgmIterator'):
            ATTR.set_hidden(mObj.mNode,'cgmIterator',True)        
            
        for mShape in mObj.getShapes(asMeta=True):
            ATTR.connect(mPlug_visDirect.p_combinedShortName, "{0}.overrideVisibility".format(mShape.mNode))
                
            
    #ml_controlsAll = self.atBuilderUtils('register_mirrorIndices', ml_controlsAll)
    #self.atBuilderUtils('check_nameMatches', ml_controlsAll)
    
    mHandleFactory = mBlock.asHandleFactory()
    for mCtrl in ml_controlsAll:
        ATTR.set(mCtrl.mNode,'rotateOrder',self.ro_base)
        
        if mCtrl.hasAttr('radius'):
            ATTR.set(mCtrl.mNode,'radius',0)        
        
        ml_pivots = mCtrl.msgList_get('spacePivots')
        if ml_pivots:
            log.debug("|{0}| >> Coloring spacePivots for: {1}".format(_str_func,mCtrl))
            for mPivot in ml_pivots:
                mHandleFactory.color(mPivot.mNode, controlType = 'sub')            
    
    if mHeadIK:
        ATTR.set(mHeadIK.mNode,'rotateOrder',self.ro_head)
    if mHeadLookAt:
        ATTR.set(mHeadLookAt.mNode,'rotateOrder',self.ro_headLookAt)
        
    
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
    
    ml_influences = copy.copy(ml_handleJoints)
    
    _settingsControl = None
    if mBlock.squashExtraControl:
        _settingsControl = mRigNull.settings.mNode
    
    _extraSquashControl = mBlock.squashExtraControl
           
    res_segScale = self.UTILS.get_blockScale(self,'segMeasure')
    mPlug_masterScale = res_segScale[0]
    mMasterCurve = res_segScale[1]
    
    mSegMidIK = mRigNull.getMessageAsMeta('controlSegMidIK')
    if mSegMidIK and mBlock.neckControls == 1:
        log.debug("|{0}| >> seg mid IK control found...".format(_str_func))
        ml_influences.append(mSegMidIK)
    
    _d = {'jointList':[mObj.mNode for mObj in ml_segJoints],
          'baseName':'{0}_rigRibbon'.format(self.d_module['partName']),
          'connectBy':'constraint',
          'extendEnds':True,
          'masterScalePlug':mPlug_masterScale,
          'influences':ml_influences,
          'settingsControl':_settingsControl,
          'attachEndsToInfluences':True,
          'moduleInstance':mModule}
    
    _d.update(self.d_squashStretch)
    res_ribbon = IK.ribbon(**_d)
    
    ml_surfaces = res_ribbon['mlSurfaces']
    
    mMasterCurve.p_parent = mRoot    
    
    ml_segJoints[0].parent = mRoot
    
    
    
    return
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
    mModule = self.mModule
    mHeadIK = mRigNull.headIK
    log.info("|{0}| >> Found headIK : {1}".format(_str_func, mHeadIK))
    
    ml_rigJoints = mRigNull.msgList_get('rigJoints')
    ml_fkJoints = mRigNull.msgList_get('fkJoints')
    ml_handleJoints = self.mRigNull.msgList_get('handleJoints')
    ml_baseIKDrivers = self.mRigNull.msgList_get('baseIKDrivers')
    ml_blendJoints = mRigNull.msgList_get('blendJoints')
    ml_segBlendTargets = copy.copy(ml_blendJoints)
    
    mTopHandleDriver = mHeadIK
    
    mHeadFK = False
    mAimParent = ml_blendJoints[-1]
    
    mHeadFK = mRigNull.getMessageAsMeta('headFK')
    mHeadIK = mRigNull.getMessageAsMeta('headIK')
        
    if ml_blendJoints:
        mHeadStuffParent = ml_blendJoints[-1]
    else:
        mHeadStuffParent = mHeadFK

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
        mHeadLookAt = mRigNull.lookAt
        
        if ml_handleJoints:
            mTopDriver = ml_handleJoints[-1].doCreateAt()
        else:
            mTopDriver = ml_fkJoints[-1].doCreateAt()
            
        mTopDriver.p_parent = mHeadBlendJoint
        ml_segBlendTargets[-1] = mTopDriver#...insert into here our new twist driver
        
        mHeadLookAt.doStore('drivenBlend', mHeadBlendJoint.mNode)
        mHeadLookAt.doStore('drivenAim', mHeadAimJoint.mNode)
        
        self.atUtils('get_switchTarget', mHeadLookAt, mHeadBlendJoint)
        
        mHeadLookAt.doStore('fkMatch', mTopDriver.mNode)
        mHeadLookAt.doStore('ikMatch', mHeadBlendJoint.mNode)
        
        
        ATTR.connect(mPlug_aim.p_combinedShortName, "{0}.v".format(mHeadLookAt.mNode))
        
        #Setup Aim Main -------------------------------------------------------------------------------------
        mc.aimConstraint(mHeadLookAt.mNode,
                         mHeadAimJoint.mNode,
                         maintainOffset = False, weight = 1,
                         aimVector = self.d_orientation['vectorAim'],
                         upVector = self.d_orientation['vectorUp'],
                         worldUpVector = self.d_orientation['vectorUp'],
                         worldUpObject = mHeadLookAt.mNode,#mHeadIK.mNode,#mHeadIK.masterGroup.mNode
                         worldUpType = 'objectRotation' )
        
        #Setup Aim back on head -------------------------------------------------------------------------------------
        _str_orientation = self.d_orientation['str']
        mc.aimConstraint(mHeadStuffParent.mNode,
                         mHeadLookAt.mNode,
                         maintainOffset = False, weight = 1,
                         aimVector = self.d_orientation['vectorAimNeg'],
                         upVector = self.d_orientation['vectorUp'],
                         worldUpVector = self.d_orientation['vectorUp'],
                         skip = _str_orientation[0],
                         worldUpObject = mHeadStuffParent.mNode,#mHeadIK.masterGroup.mNode,#mHeadIK.mNode,#mHeadIK.masterGroup.mNode
                         worldUpType = 'objectRotation' )
        
        ATTR.set_alias(mHeadLookAt.mNode,'r{0}'.format(_str_orientation[0]),'tilt')
        mHeadLookAt.setAttrFlags(attrs=['r{0}'.format(v) for v in _str_orientation[1:]])
        
        #Setup blend ----------------------------------------------------------------------------------
        RIGCONSTRAINT.blendChainsBy(mHeadFKJoint,mHeadAimJoint,mHeadBlendJoint,
                                    driver = mPlug_aim.p_combinedName,l_constraints=['orient'])
        
        #Parent pass ---------------------------------------------------------------------------------
        mHeadLookAt.masterGroup.parent = mHeadStuffParent#mHeadIK.masterGroup
        #mSettings.masterGroup.parent = mHeadIK
        
        for mObj in mHeadFKJoint,mHeadAimJoint,mHeadBlendJoint:
            mObj.p_parent = mHeadStuffParent
        
        #mHeadIK.parent = mHeadBlendJoint.mNode
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
            
            mPlug_FKIK = cgmMeta.cgmAttr(mSettings.mNode,'FKIK',attrType='float',lock=False,keyable=True)
            
            #>>> Setup a vis blend result
            mPlug_FKon = cgmMeta.cgmAttr(mSettings,'result_FKon',attrType='float',defaultValue = 0,keyable = False,lock=True,hidden=True)	
            mPlug_IKon = cgmMeta.cgmAttr(mSettings,'result_IKon',attrType='float',defaultValue = 0,keyable = False,lock=True,hidden=True)	
        
            NODEFACTORY.createSingleBlendNetwork(mPlug_FKIK.p_combinedName,
                                                 mPlug_IKon.p_combinedName,
                                                 mPlug_FKon.p_combinedName)
              
            mPlug_FKon.doConnectOut("{0}.visibility".format(ml_fkJoints[0].masterGroup.mNode))
            
            
            mIKGroup = mRoot.doCreateAt()
            mIKGroup.doStore('cgmTypeModifier','ik')
            mIKGroup.doName()
    
            mPlug_IKon.doConnectOut("{0}.visibility".format(mIKGroup.mNode))
    
            mIKGroup.parent = mRoot
            #mIKControl.masterGroup.parent = mIKGroup            
        
            mHeadIK.masterGroup.p_parent = mIKGroup
            
            """
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
            
            """
            
            mControlIKBase = mRigNull.controlIKBase
            # Neck controls --------------------------------------------------------------
            if mBlock.neckControls == 1:
                log.debug("|{0}| >> Single joint IK...".format(_str_func))
                mc.aimConstraint(mHeadIK.mNode,
                                 ml_ikJoints[0].mNode,
                                 maintainOffset = True, weight = 1,
                                 aimVector = self.d_orientation['vectorAim'],
                                 upVector = self.d_orientation['vectorUp'],
                                 worldUpVector = self.d_orientation['vectorOut'],
                                 worldUpObject = mControlIKBase.mNode,
                                 worldUpType = 'objectRotation' )
                mc.pointConstraint(mHeadIK.mNode,
                                   ml_ikJoints[-1].mNode,
                                   maintainOffset = True)
            else:
                raise ValueError,"Don't have ability for more than one neck control yet"
            
            mControlIKBase.p_parent = mIKGroup


            mc.pointConstraint(mHeadIK.mNode,ml_ikJoints[-1].mNode, maintainOffset = True)
            mc.orientConstraint(mHeadIK.mNode,ml_ikJoints[-1].mNode, maintainOffset = True)
            
            
            #>> handleJoints ========================================================================================
            if ml_handleJoints:
                log.debug("|{0}| >> Found Handles...".format(_str_func))
                #ml_handleJoints[-1].masterGroup.parent = mHeadIK
                #ml_handleJoints[0].masterGroup.parent = ml_blendJoints[0]
                
                if mBlock.neckControls == 1:
                    reload(RIGCONSTRAINT)
                    RIGCONSTRAINT.build_aimSequence(ml_handleJoints,
                                                    ml_handleJoints,
                                                    ml_blendJoints, #ml_segBlendTargets,#ml_handleParents,
                                                    ml_segBlendTargets,
                                                    mode = 'sequence',
                                                    mRoot=mRoot,
                                                    rootTargetEnd=ml_segBlendTargets[-1],
                                                    upParent=[1,0,0],
                                                    interpType = 2,
                                                    upMode = 'objectRotation')
                    
                    """
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
                                     worldUpType = 'objectRotation' )"""
            
            if ml_handleJoints:            
                ml_handleJoints[-1].masterGroup.p_parent = mHeadBlendJoint
            #>> midSegcontrol ========================================================================================
            mSegMidIK = mRigNull.getMessageAsMeta('controlSegMidIK')
            if mSegMidIK:
                log.debug("|{0}| >> seg mid IK control found...".format(_str_func))
    
                #mSegMidIK = mRigNull.controlSegMidIK
                
                if mBlock.neckControls > 1:
                    mSegMidIK.masterGroup.parent = mIKGroup
    
                ml_midTrackJoints = copy.copy(ml_handleJoints)
                ml_midTrackJoints.insert(1,mSegMidIK)
    
                d_mid = {'jointList':[mJnt.mNode for mJnt in ml_midTrackJoints],
                         'baseName' :self.d_module['partName'] + '_midRibbon',
                         'driverSetup':'stableBlend',
                         'squashStretch':None,
                         'msgDriver':'masterGroup',
                         'specialMode':'noStartEnd',
                         'connectBy':'constraint',
                         'influences':ml_handleJoints,
                         'moduleInstance' : mModule}
    
                l_midSurfReturn = IK.ribbon(**d_mid)            
            
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
                
                """
                mc.aimConstraint(mHeadIK.mNode,
                                 ml_rigJoints[0].masterGroup.mNode,
                                 maintainOffset = True, weight = 1,
                                 aimVector = self.d_orientation['vectorAim'],
                                 upVector = self.d_orientation['vectorUp'],
                                 worldUpVector = self.d_orientation['vectorOut'],
                                 worldUpObject = ml_blendJoints[0].mNode,
                                 worldUpType = 'objectRotation' )"""
                
            else:
                log.debug("|{0}| >> Not implemented multi yet".format(_str_func))
                
            
            #Parent --------------------------------------------------            
            ml_blendJoints[0].parent = mRoot
            ml_ikJoints[0].parent = mRigNull.controlIKBase

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
    ml_blendjoints = mRigNull.msgList_get('blendJoints')
    
    
    mAttachDriver = mRigNull.getMessageAsMeta('attachDriver')
    mAttachDriver.doStore('cgmAlias', '{0}_partDriver'.format(self.d_module['partName']))
    
    #if not self.mConstrainNull.hasAttr('cgmAlias'):
        #self.mConstrainNull.addAttr('cgmAlias','{0}_rootNull'.format(self.d_module['partName']))    
    
    #>>  Parent and constraining joints and rig parts =======================================================
    #if mSettings != mHeadIK:
        #mSettings.masterGroup.parent = mHeadIK
    
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
    ml_targetDynParents = [self.md_dynTargetsParent['attachDriver']]

    if not mRoot.hasAttr('cgmAlias'):
        mRoot.addAttr('cgmAlias','{0}_root'.format(self.d_module['partName']))

    #if not mParent.hasAttr('cgmAlias'):
    #    mParent.addAttr('cgmAlias',self.d_module['partName'] + 'base')
    #ml_targetDynParents.append(mParent)    
    
    ml_targetDynParents.extend(ml_endDynParents)

    mDynGroup = mRoot.dynParentGroup
    #mDynGroup.dynMode = 2

    for mTar in ml_targetDynParents:
        mDynGroup.addDynParent(mTar)
    mDynGroup.rebuild()
    #mDynGroup.dynFollow.p_parent = self.mDeformNull    
    
    
    #...ik controls ==================================================================================
    log.debug("|{0}| >>  IK Handles ... ".format(_str_func))                
    
    ml_ikControls = []
    mControlIK = mRigNull.getMessage('controlIK')
    
    if mControlIK:
        ml_ikControls.append(mRigNull.controlIK)
    if mRigNull.getMessage('controlIKBase'):
        ml_ikControls.append(mRigNull.controlIKBase)
        
    for mHandle in ml_ikControls:
        log.debug("|{0}| >>  IK Handle: {1}".format(_str_func,mHandle))
        
        ml_targetDynParents = ml_baseDynParents + [self.md_dynTargetsParent['attachDriver']] + ml_endDynParents
        
        ml_targetDynParents.append(self.md_dynTargetsParent['world'])
        ml_targetDynParents.extend(mHandle.msgList_get('spacePivots',asMeta = True))
    
        mDynGroup = cgmRIGMETA.cgmDynParentGroup(dynChild=mHandle,dynMode=0)
        #mDynGroup.dynMode = 2
    
        for mTar in ml_targetDynParents:
            mDynGroup.addDynParent(mTar)
        mDynGroup.rebuild()
        #mDynGroup.dynFollow.p_parent = self.mConstrainNull
        
    log.debug("|{0}| >>  IK targets...".format(_str_func))
    pprint.pprint(ml_targetDynParents)        
    
    log.debug(cgmGEN._str_subLine)
              
    
    if mRigNull.getMessage('controlIKMid'):
        log.debug("|{0}| >>  IK Mid Handle ... ".format(_str_func))                
        mHandle = mRigNull.controlIKMid
        
        mParent = mHandle.masterGroup.getParent(asMeta=True)
        ml_targetDynParents = []
    
        if not mParent.hasAttr('cgmAlias'):
            mParent.addAttr('cgmAlias','midIKBase')
        
        mPivotResultDriver = mRigNull.getMessage('pivotResultDriver',asMeta=True)
        if mPivotResultDriver:
            mPivotResultDriver = mPivotResultDriver[0]
        ml_targetDynParents = [mPivotResultDriver,mControlIK,mParent]
        
        ml_targetDynParents.extend(ml_baseDynParents + ml_endDynParents)
        #ml_targetDynParents.extend(mHandle.msgList_get('spacePivots',asMeta = True))
    
        mDynGroup = cgmRIGMETA.cgmDynParentGroup(dynChild=mHandle,dynMode=0)
        #mDynGroup.dynMode = 2
    
        for mTar in ml_targetDynParents:
            mDynGroup.addDynParent(mTar)
        mDynGroup.rebuild()
        #mDynGroup.dynFollow.p_parent = self.mConstrainNull
        
        log.debug("|{0}| >>  IK Mid targets...".format(_str_func,mRoot))
        pprint.pprint(ml_targetDynParents)                
        log.debug(cgmGEN._str_subLine)        
    
    
    """
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
    """
    
    #...headLookat ---------------------------------------------------------------------------------------
    if mBlock.headAim:
        log.info("|{0}| >> HeadAim setup...".format(_str_func))
        
        mPlug_aim = cgmMeta.cgmAttr(mSettings.mNode,'blend_aim',attrType='float',lock=False,keyable=True)
        
        #mHeadFKJoint = mRigNull.getMessage('fkHeadJoint', asMeta=True)[0]
        #mHeadAimJoint = mRigNull.getMessage('aimHeadJoint', asMeta=True)[0]
        #mHeadBlendJoint = mRigNull.getMessage('blendHeadJoint', asMeta=True)[0]
        #mHeadFKDynParentGroup = mHeadIK.dynParentGroup
        
        mHeadLookAt = mRigNull.lookAt        
        mHeadLookAt.setAttrFlags(attrs='v')
        
        #...dynParentGroup...
        ml_headLookAtDynParents = []
        ml_headLookAtDynParents.extend(mHeadLookAt.msgList_get('spacePivots',asMeta = True))
        ml_headLookAtDynParents.extend(ml_endDynParents)    
        
        ml_headLookAtDynParents.insert(0, ml_blendjoints[-1])
        if not ml_blendjoints[-1].hasAttr('cgmAlias'):
            ml_blendjoints[-1].addAttr('cgmAlias','blendHead')        
        #mHeadIK.masterGroup.addAttr('cgmAlias','headRoot')
        
        #Add our parents...
        mDynGroup = mHeadLookAt.dynParentGroup
        log.info("|{0}| >> dynParentSetup : {1}".format(_str_func,mDynGroup))  
    
        for o in ml_headLookAtDynParents:
            mDynGroup.addDynParent(o)
        mDynGroup.rebuild()
        
    #...rigJoints =================================================================================
    """
    if mBlock.spaceSwitch_direct:
        log.debug("|{0}| >>  Direct...".format(_str_func))                
        for i,mObj in enumerate(mRigNull.msgList_get('rigJoints')):
            log.debug("|{0}| >>  Direct: {1}".format(_str_func,mObj))                        
            ml_targetDynParents = copy.copy(ml_baseDynParents)
            ml_targetDynParents.extend(mObj.msgList_get('spacePivots',asMeta=True) or [])
    
            mParent = mObj.masterGroup.getParent(asMeta=True)
            if not mParent.hasAttr('cgmAlias'):
                mParent.addAttr('cgmAlias','{0}_rig{1}_base'.format(mObj.cgmName,i))
            ml_targetDynParents.insert(0,mParent)
    
            ml_targetDynParents.extend(ml_endDynParents)
    
            mDynGroup = cgmRIGMETA.cgmDynParentGroup(dynChild=mObj.mNode)
            mDynGroup.dynMode = 2
    
            for mTar in ml_targetDynParents:
                mDynGroup.addDynParent(mTar)
    
            mDynGroup.rebuild()
    
            mDynGroup.dynFollow.p_parent = mRoot """
            
    #...fk controls ============================================================================================
    log.debug("|{0}| >>  FK...".format(_str_func)+'-'*80)                
    ml_fkJoints = self.mRigNull.msgList_get('fkJoints')
    
    for i,mObj in enumerate([ml_fkJoints[0],ml_fkJoints[-1]]):
        if not mObj.getMessage('masterGroup'):
            log.debug("|{0}| >>  Lacks masterGroup: {1}".format(_str_func,mObj))            
            continue
        log.debug("|{0}| >>  FK: {1}".format(_str_func,mObj))
        ml_targetDynParents = copy.copy(ml_baseDynParents)
        ml_targetDynParents.append(self.md_dynTargetsParent['attachDriver'])
        
        mParent = mObj.masterGroup.getParent(asMeta=True)
        if not mParent.hasAttr('cgmAlias'):
            mParent.addAttr('cgmAlias','{0}_base'.format(mObj.p_nameBase))
        _mode = 2
        if i == 0:
            ml_targetDynParents.append(mParent)
            #_mode = 2            
        else:
            ml_targetDynParents.insert(0,mParent)
            #_mode = 1
        
        ml_targetDynParents.extend(ml_endDynParents)
        ml_targetDynParents.extend(mObj.msgList_get('spacePivots',asMeta = True))
    
        mDynGroup = cgmRIGMETA.cgmDynParentGroup(dynChild=mObj.mNode, dynMode=_mode)# dynParents=ml_targetDynParents)
        #mDynGroup.dynMode = 2
    
        for mTar in ml_targetDynParents:
            mDynGroup.addDynParent(mTar)
        mDynGroup.rebuild()

        if _mode == 2:
            mDynGroup.dynFollow.p_parent = mRoot    
        
        log.debug("|{0}| >>  FK targets: {1}...".format(_str_func,mObj))
        pprint.pprint(ml_targetDynParents)                
        log.debug(cgmGEN._str_subLine)    
        
    #Settings =================================================================================
    log.debug("|{0}| >> Settings...".format(_str_func))
    mSettings.visRoot = 0
    mSettings.visDirect = 0
    
    ml_handleJoints = mRigNull.msgList_get('handleJoints')
    if ml_handleJoints:
        ATTR.set_default(ml_handleJoints[0].mNode, 'followRoot', 1.0)
        ml_handleJoints[0].followRoot = 1.0    
        
        
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
    else:
        pass
    
        
    
    
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

def create_simpleMesh(self,  deleteHistory = True, cap=True):
    _str_func = 'create_simpleMesh'
    log.debug("|{0}| >>  ".format(_str_func)+ '-'*80)
    log.debug("{0}".format(self))
    
    #>> Head ===================================================================================
    log.debug("|{0}| >> Head...".format(_str_func))
    
    mGroup = self.msgList_get('headMeshProxy')[0].getParent(asMeta=True)
    l_headGeo = mGroup.getChildren(asMeta=False)
    ml_headStuff = []
    for i,o in enumerate(l_headGeo):
        log.debug("|{0}| >> geo: {1}...".format(_str_func,o))                    
        if ATTR.get(o,'v'):
            log.debug("|{0}| >> visible head: {1}...".format(_str_func,o))            
            mObj = cgmMeta.validateObjArg(mc.duplicate(o, po=False, ic = False)[0])
            ml_headStuff.append(  mObj )
            mObj.p_parent = False
        

    if self.neckBuild:#...Neck =====================================================================
        log.debug("|{0}| >> neckBuild...".format(_str_func))    
        ml_neckMesh = self.UTILS.create_simpleLoftMesh(self,deleteHistory,cap)
        ml_headStuff.extend(ml_neckMesh)
        
    _mesh = mc.polyUnite([mObj.mNode for mObj in ml_headStuff],ch=False)
    _mesh = mc.rename(_mesh,'{0}_0_geo'.format(self.p_nameBase))
    
    return cgmMeta.validateObjListArg(_mesh)

def asdfasdfasdf(self, forceNew = True, skin = False):
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
    
    ml_rigJoints = mRigNull.msgList_get('rigJoints',asMeta = True)
    if not ml_rigJoints:
        raise ValueError,"No rigJoints connected"

    #>> If proxyMesh there, delete --------------------------------------------------------------------------- 
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
            CORERIG.shapeParent_in_place(ml_rigJoints[-1].mNode,mObj.mNode,True,False)
            CORERIG.colorControl(ml_rigJoints[-1].mNode,_side,'main',directProxy=True)        
        
    if mBlock.neckBuild:#...Neck =====================================================================
        log.debug("|{0}| >> neckBuild...".format(_str_func))


def build_proxyMesh(self, forceNew = True, puppetMeshMode = False):
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
    
    #>> If proxyMesh there, delete --------------------------------------------------------------------------- 
    if puppetMeshMode:
        _bfr = mRigNull.msgList_get('puppetProxyMesh',asMeta=True)
        if _bfr:
            log.debug("|{0}| >> puppetProxyMesh detected...".format(_str_func))            
            if forceNew:
                log.debug("|{0}| >> force new...".format(_str_func))                            
                mc.delete([mObj.mNode for mObj in _bfr])
            else:
                return _bfr        
    else:
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
        
    if directProxy:
        for mJnt in ml_rigJoints:
            for shape in mJnt.getShapes():
                mc.delete(shape)
    mGroup = mBlock.msgList_get('headMeshProxy')[0].getParent(asMeta=True)
    
    l_headGeo = mGroup.getChildren(asMeta=False)
    #l_vis = mc.ls(l_headGeo, visible = True)
    ml_segProxy = []
    ml_headStuff = []
    if puppetMeshMode:
        log.debug("|{0}| >> puppetMesh setup... ".format(_str_func))
        ml_moduleJoints = mRigNull.msgList_get('moduleJoints')
        
        if mBlock.neckBuild:
            if mBlock.neckJoints == 1:
                mProxy = ml_moduleJoints[0].doCreateAt(setClass=True)
                mPrerigProxy = mBlock.getMessage('prerigLoftMesh',asMeta=True)[0]
                CORERIG.shapeParent_in_place(mProxy.mNode, mPrerigProxy.mNode)
                
                ATTR.copy_to(ml_moduleJoints[0].mNode,'cgmName',mProxy.mNode,driven = 'target')
                mProxy.addAttr('cgmType','proxyPuppetGeo')
                mProxy.doName()
                mProxy.parent = ml_moduleJoints[0]
                ml_segProxy = [mProxy]

                
            else:
                ml_segProxy = cgmMeta.validateObjListArg(self.atBuilderUtils('mesh_proxyCreate', ml_moduleJoints),'cgmObject')
                log.debug("|{0}| >> created: {1}".format(_str_func,ml_neckProxy))
                
                for i,mGeo in enumerate(ml_neckProxy):
                    mGeo.parent = ml_moduleJoints[i]
                    mGeo.doStore('cgmName',self.d_module['partName'])
                    mGeo.addAttr('cgmIterator',i+1)
                    mGeo.addAttr('cgmType','proxyPuppetGeo')
                    mGeo.doName()
                    ml_segProxy.append(mGeo)
        
        for i,o in enumerate(l_headGeo):
            log.debug("|{0}| >> geo: {1}...".format(_str_func,o))                    
            if ATTR.get(o,'v'):
                log.debug("|{0}| >> visible head: {1}...".format(_str_func,o))            
                mGeo = cgmMeta.validateObjArg(mc.duplicate(o, po=False, ic = False)[0])
                mGeo.parent = ml_moduleJoints[-1]
                mGeo.doStore('cgmName',self.d_module['partName'])
                mGeo.addAttr('cgmTypeModifier','end')
                mGeo.addAttr('cgmType','proxyPuppetGeo')
                mGeo.doName()
                
                ml_segProxy.append( mGeo )
            

                    
        
        mRigNull.msgList_connect('puppetProxyMesh', ml_segProxy)
        return ml_segProxy    
    
    
    
    
    for i,o in enumerate(l_headGeo):
        log.debug("|{0}| >> geo: {1}...".format(_str_func,o))                    
        if ATTR.get(o,'v'):
            log.debug("|{0}| >> visible head: {1}...".format(_str_func,o))            
            mObj = cgmMeta.validateObjArg(mc.duplicate(o, po=False, ic = False)[0])
            ml_headStuff.append(  mObj )
            mObj.p_parent = False
            mObj.parent = ml_rigJoints[-1]
            
            ATTR.copy_to(ml_rigJoints[-1].mNode,'cgmName',mObj.mNode,driven = 'target')
            mObj.addAttr('cgmIterator',i)
            mObj.addAttr('cgmType','proxyGeo')
            mObj.doName()
            
            if directProxy:
                CORERIG.shapeParent_in_place(ml_rigJoints[-1].mNode,mObj.mNode,True,False)
                CORERIG.colorControl(ml_rigJoints[-1].mNode,_side,'main',directProxy=True)        
        
    if mBlock.neckBuild:#...Neck =====================================================
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
                CORERIG.shapeParent_in_place(ml_rigJoints[0].mNode,mProxy.mNode,True,False)
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
                    CORERIG.shapeParent_in_place(ml_rigJoints[i].mNode,mGeo.mNode,True,False)
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




















