"""
------------------------------------------
cgm.core.mrs.blocks.organic.limb
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
import maya.mel as mel    

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
import cgm.core.lib.math_utils as MATH
import cgm.core.lib.transform_utils as TRANS
import cgm.core.lib.distance_utils as DIST
import cgm.core.lib.attribute_utils as ATTR
import cgm.core.tools.lib.snap_calls as SNAPCALLS
import cgm.core.classes.NodeFactory as NODEFACTORY
from cgm.core import cgm_RigMeta as cgmRigMeta
import cgm.core.lib.list_utils as LISTS
import cgm.core.lib.nameTools as NAMETOOLS
import cgm.core.lib.locator_utils as LOC
reload(NAMETOOLS)
#Prerig handle making. refactor to blockUtils
import cgm.core.lib.snap_utils as SNAP
import cgm.core.lib.rayCaster as RAYS
import cgm.core.lib.rigging_utils as CORERIG
import cgm.core.lib.curve_Utils as CURVES
import cgm.core.rig.constraint_utils as RIGCONSTRAINT
import cgm.core.lib.constraint_utils as CONSTRAINT
import cgm.core.lib.position_utils as POS
import cgm.core.rig.joint_utils as JOINT
import cgm.core.rig.ik_utils as IK
import cgm.core.mrs.lib.block_utils as BLOCKUTILS
import cgm.core.mrs.lib.builder_utils as BUILDUTILS
import cgm.core.lib.shapeCaster as SHAPECASTER
from cgm.core.cgmPy import validateArgs as VALID

import cgm.core.cgm_RigMeta as cgmRIGMETA
reload(CURVES)

# From cgm ==============================================================
from cgm.core import cgm_Meta as cgmMeta

#=============================================================================================================
#>> Block Settings
#=============================================================================================================
__version__ = 'alpha.1.03222018'
__autoTemplate__ = False
__dimensions = [15.2, 23.2, 19.7]#...cm
__menuVisible__ = True
__sizeMode__ = 'castNames'

#__baseSize__ = 1,1,10

__l_rigBuildOrder__ = ['rig_prechecks',
                       'rig_skeleton',
                       'rig_shapes',
                       'rig_controls',
                       'rig_frame',
                       'rig_pivotSetup',                       
                       'rig_segments',
                       'rig_cleanUp']

d_wiring_skeleton = {'msgLists':['moduleJoints','skinJoints']}
d_wiring_prerig = {'msgLinks':['moduleTarget','prerigNull','noTransPrerigNull'],
                   'msgLists':['prerigHandles']}
d_wiring_template = {'msgLinks':['templateNull','noTransTemplateNull','prerigLoftMesh','orientHelper'],
                     'msgLists':['templateHandles']}
d_wiring_define = {'msgLinks':['defineNull']}

#>>>Profiles =====================================================================================================
d_build_profiles = {
    'unityMobile':{'default':{'numRoll':1,
                              },
                   },
    'unityPC':{'default':{'numRoll':3,
                          },
               'spine':{'numRoll':4,
                       }},
    'feature':{'default':{'numRoll':5,
                          }}}

d_block_profiles = {
    'leg_bi':{'numShapers':2,
               'addCog':False,
               'cgmName':'leg',
               'loftShape':'square',
               'loftSetup':'default',
               'settingsPlace':'end',
               'settingsDirection':'down',
               'ikSetup':'rp',
               'ikEnd':'foot',
               'numControls':3,
               'mainRotAxis':'out',               
               'buildBaseLever':False,
               'hasLeverJoint':False,
               'nameList':['hip','knee','ankle','ball','toe'],
               'baseAim':[0,-1,0],
               'baseUp':[0,0,1],
               'baseSize':[2,8,2]},
    
    'arm':{'numShapers':2,
           'addCog':False,
           'attachPoint':'end',
           'cgmName':'arm',
           'loftShape':'square',
           'loftSetup':'default',
           'settingsPlace':'end',
           'ikSetup':'rp',
           'ikEnd':'hand',
           'mainRotAxis':'up',
           'numControls':3,
           'buildLeverBase':True,
           'hasLeverJoint':True,
           'nameList':['clav','shoulder','elbow','wrist'],
           'baseAim':[-1,0,0],
           'baseUp':[0,1,0],
           'baseSize':[2,8,2]},
    
    'finger':{'numShapers':2,
              'addCog':False,
              'attachPoint':'end',
              'cgmName':'finger',
              'loftShape':'wideUp',
              'loftSetup':'default',
              'settingsPlace':'end',
              'ikSetup':'rp',
              'ikEnd':'tipEnd',
              'numControls':4,
              'numRoll':0,
              'rigSetup':'digit',
              'offsetMode':'proxyAverage',
              'buildLeverBase':True,
              'hasLeverJoint':True,
              'hasEndJoint':False,
              'nameList':['index'],
              'scaleSetup':False,
              #'baseAim':[1,0,0],
              'baseUp':[0,1,0],
              'baseSize':[1.4,1,6.4]},
    
    'thumb':{'numShapers':1,
             'addCog':False,
             'attachPoint':'end',
             'cgmName':'thumb',
             'loftShape':'wideUp',
             'loftSetup':'default',
             'settingsPlace':'end',
             'ikSetup':'rp',
             'ikEnd':'tipEnd',
             'numControls':4,
             'numRoll':0,
             'rigSetup':'digit',
             'offsetMode':'proxyAverage',
             'buildLeverBase':False,
             'hasLeverJoint':False,
             'hasEndJoint':False,
             'nameList':['thumb'],
             'scaleSetup':False,
             #'baseAim':[1,0,0],
             'baseUp':[0,1,0],
             'baseSize':[1.4,1,6.4]},
   }

#>>>Attrs =====================================================================================================
l_attrsStandard = ['side',
                   'position',
                   'baseUp',
                   'baseAim',
                   'addCog',
                   'nameList',
                   #'namesHandles',
                   #'namesJoints',
                   'attachPoint',
                   'loftSides',
                   'loftDegree',
                   'loftSplit',
                   'loftShape',
                   'ikSetup',
                   'scaleSetup',
                   'numControls',
                   'offsetMode',
                   'settingsDirection',
                   'numSpacePivots',
                   'proxyDirect',
                   'numShapers',#...with limb this is the sub shaper count as you must have one per handle
                   'buildProfile',
                   'moduleTarget']

d_attrsToMake = {'proxyShape':'cube:sphere:cylinder',
                 'loftSetup':'default:morpheus',
                 'mainRotAxis':'up:out',
                 'settingsPlace':'start:end',
                 'blockProfile':':'.join(d_block_profiles.keys()),
                 'rigSetup':'default:digit',#...this is to account for some different kinds of setup
                 'ikEnd':'none:bank:foot:hand:tipBase:tipEnd:proxy',
                 'numRoll':'int',
                 #'ikBase':'none:fkRoot',
                 'hasLeverJoint':'bool',
                 'buildLeverBase':'bool',#...fkRoot is our clav like setup
                 'hasEndJoint':'bool',
                 'hasBallJoint':'bool',
                 #'buildSpacePivots':'bool',
                 #'nameIter':'string',
                 #'numControls':'int',
                 #'numShapers':'int',
                 #'numJoints':'int'
                 }

d_defaultSettings = {'version':__version__,
                     'baseSize':MATH.get_space_value(__dimensions[1]),
                     'numControls': 3,
                     'loftSetup':0,
                     'loftShape':0,
                     'numShapers':3,
                     'settingsDirection':'up',
                     'numSpacePivots':2,
                     'settingsPlace':1,
                     'loftSides': 10,
                     'loftSplit':1,
                     'loftDegree':'linear',
                     'numRoll':1,
                     'proxyDirect':True,
                     'nameList':['',''],
                     'blockProfile':'leg_bi',
                     'attachPoint':'base',}


#d_preferredAngles = {'head':[0,-10, 10]}#In terms of aim up out for orientation relative values, stored left, if right, it will invert
#d_rotationOrders = {'head':'yxz'}


#=============================================================================================================
#>> Define
#=============================================================================================================
def define(self):
    _str_func = 'define'    
    log.debug("|{0}| >> ...".format(_str_func)+ '-'*80)
    log.debug(self)
    
    _short = self.mNode
    ATTR.set_min(_short, 'numControls', 2)
    ATTR.set_min(_short, 'numRoll', 0)
    ATTR.set_min(_short, 'loftSides', 3)
    ATTR.set_min(_short, 'loftSplit', 1)
    ATTR.set_min(_short, 'numShapers', 1)
    

    _shapes = self.getShapes()
    if _shapes:
        log.debug("|{0}| >>  Removing old shapes...".format(_str_func))        
        mc.delete(_shapes)
        defineNull = self.getMessage('defineNull')
        if defineNull:
            log.debug("|{0}| >>  Removing old defineNull...".format(_str_func))
            mc.delete(defineNull)
    
    _size = MATH.average(self.baseSize[1:])
    _crv = CURVES.create_controlCurve(self.mNode, shape='arrowsAxis',#'arrowsAxis', 
                                      direction = 'z+', sizeMode = 'fixed', size = _size/2)
    CORERIG.shapeParent_in_place(self.mNode,_crv,False)
    
    mHandleFactory = self.asHandleFactory()
    mHandleFactory.color(self.mNode,controlType='main')
    #CORERIG.colorControl(self.mNode,_side,'main',transparent = True)
    
    mDefineNull = self.atUtils('stateNull_verify','define')
    
    #Rotate Group ==================================================================
    mRotateGroup = cgmMeta.validateObjArg(mDefineNull.doGroup(True,False,asMeta=True,typeModifier = 'rotate'),
                                          'cgmObject',setClass=True)
    mRotateGroup.p_parent = mDefineNull
    mRotateGroup.setAttrFlags()    
    
    #Bounding box ==================================================================
    _bb_shape = CURVES.create_controlCurve(self.mNode,'cubeOpen', size = 1.0, sizeMode='fixed')
    mBBShape = cgmMeta.validateObjArg(_bb_shape, 'cgmObject',setClass=True)
    mBBShape.p_parent = mRotateGroup    
    mBBShape.tz = .5
    CORERIG.copy_pivot(mBBShape.mNode,self.mNode)    
    
    self.doConnectOut('baseSize', "{0}.scale".format(mBBShape.mNode))
    mHandleFactory.color(mBBShape.mNode,controlType='sub')
    mBBShape.setAttrFlags()
    
    mBBShape.doStore('cgmName', self.mNode)
    mBBShape.doStore('cgmType','bbVisualize')
    mBBShape.doName()    
    
    self.connectChildNode(mBBShape.mNode,'bbHelper')
    
    #Up helper ==================================================================
    mTarget = self.doCreateAt()
    mTarget.p_parent = mRotateGroup
    mTarget.rename('aimTarget')
    self.doConnectOut('baseSizeZ', "{0}.tz".format(mTarget.mNode))
    mTarget.setAttrFlags()
    
    _arrowUp = CURVES.create_fromName('pyramid', _size/5, direction= 'y+')
    mArrow = cgmMeta.validateObjArg(_arrowUp, 'cgmObject',setClass=True)
    mArrow.p_parent = mRotateGroup    
    mArrow.resetAttrs()
    mHandleFactory.color(mArrow.mNode,controlType='sub')
    
    mArrow.doStore('cgmName', self.mNode)
    mArrow.doStore('cgmType','upVector')
    mArrow.doName()
    mArrow.setAttrFlags()
    
    
    #self.doConnectOut('baseSizeY', "{0}.ty".format(mArrow.mNode))
    NODEFACTORY.argsToNodes("{0}.ty = {1}.baseSizeY + {2}".format(mArrow.mNode,
                                                                self.mNode,
                                                                self.baseSize[1])).doBuild()
    
    mAimGroup = cgmMeta.validateObjArg(mArrow.doGroup(True,True,
                                                      asMeta=True,
                                                      typeModifier = 'aim'),
                                       'cgmObject',setClass=True)
    mAimGroup.resetAttrs()
    
    _const = mc.aimConstraint(mTarget.mNode, mAimGroup.mNode, maintainOffset = False,
                              aimVector = [0,0,1], upVector = [0,1,0], 
                              worldUpObject = self.mNode,
                              worldUpType = 'objectrotation', 
                              worldUpVector = [0,1,0])
    cgmMeta.cgmNode(_const[0]).doConnectIn('worldUpVector','{0}.baseUp'.format(self.mNode))    
    mAimGroup.setAttrFlags()
    
    self.connectChildNode(mAimGroup.mNode,'rootUpHelper')
    
 
    #Plane helper ==================================================================
    plane = mc.nurbsPlane(axis = [1,0,0],#axis =  MATH.get_obj_vector(self.mNode, 'x+'),
                          width = 1, #height = 1,
                          #subdivisionsX=1,subdivisionsY=1,
                          ch=0)
    mPlane = cgmMeta.validateObjArg(plane[0])
    mPlane.doSnapTo(self.mNode)
    mPlane.p_parent = mRotateGroup
    mPlane.tz = .5
    CORERIG.copy_pivot(mPlane.mNode,self.mNode)

    self.doConnectOut('baseSize', "{0}.scale".format(mPlane.mNode))

    mHandleFactory.color(mPlane.mNode,controlType='sub',transparent=False)

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

    mRotateGroup.doConnectIn('rotate',"{0}.baseAim".format(_short))
 
    return

    
#=============================================================================================================
#>> Template
#=============================================================================================================    
#def templateDelete(self):
    #self.atUtils('delete_msgDat',msgLinks = ['noTemplateNull','templateLoftMesh'])
        
def template(self):
    _str_func = 'template'
    log.debug("|{0}| >> ...".format(_str_func)+ '-'*80)
    log.debug("{0}".format(self))
    
    self.defineNull.template = True
    
    ATTR.datList_connect(self.mNode, 'rollCount', [self.numRoll for i in range(self.numControls - 1)])
    l_rollattrs = ATTR.datList_getAttrs(self.mNode,'rollCount')
    for a in l_rollattrs:
        ATTR.set_standardFlags(self.mNode, l_rollattrs, lock=False,visible=True,keyable=True)
    
    #Initial checks =====================================================================================
    _short = self.p_nameShort
    _side = self.UTILS.get_side(self)
        
    _l_basePosRaw = self.datList_get('basePos') or [(0,0,0)]
    _l_basePos = [self.p_position]
    _baseUp = self.baseUp
    _baseSize = self.baseSize
    _baseAim = self.baseAim
    
    _ikSetup = self.getEnumValueString('ikSetup')
    _ikEnd = self.getEnumValueString('ikEnd')
    
    if MATH.is_vector_equivalent(_baseAim,_baseUp):
        raise ValueError,"baseAim and baseUp cannot be the same. baseAim: {0} | baseUp: {1}".format(self.baseAim,self.baseUp)
    
    _loftSetup = self.getEnumValueString('loftSetup')
            
    if _loftSetup not in ['default']:
        return log.error("|{0}| >> loft setup mode not done: {1}".format(_str_func,_loftSetup))    
    
    #Get base dat =====================================================================================    
    #Old method...
    """
    _mVectorAim = MATH.get_vector_of_two_points(_l_basePos[0],_l_basePos[-1],asEuclid=True)
    _mVectorUp = _mVectorAim.up()
    _worldUpVector = MATH.EUCLID.Vector3(self.baseUp[0],self.baseUp[1],self.baseUp[2])
    """
    _mVectorAim = MATH.get_obj_vector(self.rootUpHelper.mNode,asEuclid=True)
    mRootUpHelper = self.rootUpHelper
    _mVectorUp = MATH.get_obj_vector(mRootUpHelper.mNode,'y+',asEuclid=True)
    
    mBBHelper = self.bbHelper
    _v_range = max(TRANS.bbSize_get(self.mNode)) *2
    _bb_axisBox = SNAPCALLS.get_axisBox_size(mBBHelper.mNode, _v_range, mark=False)
    _size_width = _bb_axisBox[0]#...x width
    log.debug("|{0}| >> Generating more pos dat | bbHelper: {1} | range: {2}".format(_str_func,
                                                                                     mBBHelper.p_nameShort,
                                                                                     _v_range))
    _end = DIST.get_pos_by_vec_dist(_l_basePos[0], _mVectorAim, _bb_axisBox[2])
    _l_basePos.append(_end)
    
    #for i,p in enumerate(_l_basePos):
    #    LOC.create(position=p,name="{0}_loc".format(i))
    
    mBBHelper.v = False
    
    cgmGEN.func_snapShot(vars())
    
    
    #Create temple Null ==================================================================================
    #mTemplateNull = self.atUtils('templateNull_verify')
    mTemplateNull = self.UTILS.stateNull_verify(self,'template')
    mNoTransformNull = self.atUtils('noTransformNull_verify','template')
    
    #Our main rigBlock shape ...
    mHandleFactory = self.asHandleFactory()
    

    
    #Lever ==================================================================================================
    _b_lever = False
    if self.buildLeverBase:
        _b_lever = True
        log.debug("|{0}| >> Lever base, generating base value".format(_str_func))
        _mBlockParent = self.p_blockParent
        
        if _mBlockParent:
            log.debug("|{0}| >> blockParent...".format(_str_func))
            #_attachPoint = ATTR.get_enumValueString(self.mNode,'attachPoint')
            #attachPoint = self.mModule.atUtils('get_driverPoint',_attachPoint )
            if _mBlockParent.p_blockState < 1:
                raise ValueError,"BlockParent must at least be templated"
            ml_parentHandles = _mBlockParent.msgList_get('templateHandles')
            _attachPoint = ATTR.get_enumValueString(self.mNode,'attachPoint')
            log.debug("|{0}| >> attachPoint: {1}".format(_str_func, _attachPoint))
            
            if _attachPoint == 'base':
                pos_attach = ml_parentHandles[0].p_position
            elif _attachPoint == 'end':
                pos_attach = ml_parentHandles[-1].p_position
            else:
                raise ValueError,"Not implemented attachPoint: {0}".format(_attachPoint)
            
            _vec_toAttach = MATH.get_vector_of_two_points(_l_basePos[0], pos_attach)
            log.debug("|{0}| >> _vec_toAttach: {1} ".format(_str_func,_vec_toAttach))
            
            _dist_toAttach = DIST.get_distance_between_points(_l_basePos[0], pos_attach)
            log.debug("|{0}| >> _dist_toAttach: {1} ".format(_str_func,_dist_toAttach))
            
            pos_lever = DIST.get_pos_by_vec_dist(_l_basePos[0],_vec_toAttach, _dist_toAttach * .7 )
            
        else:
            log.debug("|{0}| >> no blockParent...".format(_str_func))
            #_mVectorAimNeg = _mVectorAim.reflect(MATH.Vector3(0,0,1))
            #_vec_AimNeg = MATH.list_mult(_baseAim,[-1,-1,-1])
            _vec_AimNeg = MATH.get_obj_vector(self.mNode,'z-')
            
            log.debug("|{0}| >> VecAimNeg: {1} ".format(_str_func,_vec_AimNeg))
            pos_lever = DIST.get_pos_by_vec_dist(_l_basePos[0],_vec_AimNeg, _bb_axisBox[2]*.3)
            
        log.debug("|{0}| >> pos_lever: {1} ".format(_str_func,pos_lever))
        #LOC.create(position=pos_lever, name='lever_pos_loc')
    
    
    
    #Root handles ===========================================================================================
    log.debug("|{0}| >> root handles...".format(_str_func)) 
    md_handles = {'lever':None}
    ml_handles = []
    md_loftHandles = {}
    ml_loftHandles = []
    
    _loftShapeBase = self.getEnumValueString('loftShape')
    _loftShape = 'loft' + _loftShapeBase[0].capitalize() + ''.join(_loftShapeBase[1:])
    
    if _loftSetup == 'default':
        log.debug("|{0}| >> Default loft setup...".format(_str_func))
        
        for i,n in enumerate(['start','end']):
            log.debug("|{0}| >> {1}:{2}...".format(_str_func,i,n)) 
            mHandle = mHandleFactory.buildBaseShape('sphere', _size_width, shapeDirection = 'y+')
            mHandle.p_parent = mTemplateNull
            
            mHandle.resetAttrs()
            
            self.copyAttrTo('cgmName',mHandle.mNode,'cgmName',driven='target')
            mHandle.doStore('cgmType','blockHandle')
            mHandle.doStore('cgmNameModifier',n)
            mHandle.doName()
            
            #Convert to loft curve setup ----------------------------------------------------
            mHandleFactory.setHandle(mHandle.mNode)
            #mHandleFactory = self.asHandleFactory(mHandle.mNode)
            
            mLoftCurve = mHandleFactory.rebuildAsLoftTarget(_loftShape, _size_width, shapeDirection = 'z+',rebuildHandle = False)
            mc.makeIdentity(mHandle.mNode,a=True, s = True)#...must freeze scale once we're back parented and positioned
            
            
            mHandleFactory.color(mHandle.mNode)            
            mHandle.p_position = _l_basePos[i]
            
            md_handles[n] = mHandle
            ml_handles.append(mHandle)
            
            md_loftHandles[n] = mLoftCurve                
            ml_loftHandles.append(mLoftCurve)
            
            mBaseAttachGroup = mHandle.doGroup(True,True, asMeta=True,typeModifier = 'attach')
            

        
        #>> Base Orient Helper ==================================================================================================
        mHandleFactory = self.asHandleFactory(md_handles['start'].mNode)
        mBaseOrientCurve = mHandleFactory.addOrientHelper(baseSize = _size_width,
                                                          shapeDirection = 'y+',
                                                          setAttrs = {'ty':_size_width})
        #'tz':- _size_width})
    
        self.copyAttrTo('cgmName',mBaseOrientCurve.mNode,'cgmName',driven='target')
        mBaseOrientCurve.doName()
        
        mBaseOrientCurve.p_parent =  mTemplateNull
        mOrientHelperAimGroup = mBaseOrientCurve.doGroup(True,asMeta=True,typeModifier = 'aim')
        mc.pointConstraint(md_handles['start'].mNode, mOrientHelperAimGroup.mNode )
        _const = mc.aimConstraint(ml_handles[1].mNode, mOrientHelperAimGroup.mNode, maintainOffset = False,
                                  aimVector = [0,0,1], upVector = [0,1,0], 
                                  worldUpObject = mRootUpHelper.mNode,
                                  worldUpType = 'objectrotation', 
                                  worldUpVector = [0,1,0])
                                  #worldUpType = 'vector',
                                  #worldUpVector = [_worldUpVector.x,_worldUpVector.y,_worldUpVector.z])    
        
        self.connectChildNode(mBaseOrientCurve.mNode,'orientHelper')
        #cgmMeta.cgmNode(_const[0]).doConnectIn('worldUpVector','{0}.baseUp'.format(self.mNode))
        #mBaseOrientCurve.p_parent = mStartAimGroup
        
        mBaseOrientCurve.setAttrFlags(['ry','rx','translate','scale','v'])
        mHandleFactory.color(mBaseOrientCurve.mNode,controlType='sub')
        #CORERIG.colorControl(mBaseOrientCurve.mNode,_side,'sub')          
        mc.select(cl=True)
        
        if self.numControls > 2:
            log.debug("|{0}| >> more handles necessary...".format(_str_func)) 
            #Mid Track curve ============================================================================
            log.debug("|{0}| >> TrackCrv...".format(_str_func)) 
            _midTrackResult = CORERIG.create_at([mObj.mNode for mObj in ml_handles],'linearTrack',
                                                baseName='midTrack')
            
            _midTrackCurve = _midTrackResult[0]
            mMidTrackCurve = cgmMeta.validateObjArg(_midTrackCurve,'cgmObject')
            mMidTrackCurve.rename(self.cgmName + 'midHandlesTrack_crv')
            mMidTrackCurve.parent = mNoTransformNull
        
            #>>> mid main handles =====================================================================
            l_scales = []
            for mHandle in ml_handles:
                l_scales.append(mHandle.scale)
                mHandle.scale = 1,1,1
        
            _l_posMid = CURVES.returnSplitCurveList(mMidTrackCurve.mNode,self.numControls,markPoints = False)
            #_l_pos = [ DIST.get_pos_by_vec_dist(_pos_start, _vec, (_offsetDist * i)) for i in range(self.numControls-1)] + [_pos_end]
        
        
            #Sub handles... ------------------------------------------------------------------------------------
            log.debug("|{0}| >> Mid Handle creation...".format(_str_func))
            ml_aimGroups = []
            ml_midHandles = []
            ml_midLoftHandles = []
            for i,p in enumerate(_l_posMid[1:-1]):
                log.debug("|{0}| >> mid handle cnt: {1} | p: {2}".format(_str_func,i,p))
                crv = CURVES.create_fromName('sphere', _size_width * .75, direction = 'y+')
                mHandle = cgmMeta.validateObjArg(crv, 'cgmObject', setClass=True)
                
                self.copyAttrTo('cgmName',mHandle.mNode,'cgmName',driven='target')
                mHandle.doStore('cgmType','blockHandle')
                mHandle.doStore('cgmNameModifier',"mid_{0}".format(i+1))
                mHandle.doName()                
                
                _short = mHandle.mNode
                ml_midHandles.append(mHandle)
                mHandle.p_position = p

                mHandle.p_parent = mTemplateNull
                #mHandle.resetAttrs()
                
                mHandleFactory.setHandle(mHandle.mNode)
                mLoftCurve = mHandleFactory.rebuildAsLoftTarget(_loftShape,
                                                                _size_width,
                                                                shapeDirection = 'z+',rebuildHandle = False)
                mc.makeIdentity(mHandle.mNode,a=True, s = True)#...must freeze scale once we're back parented and positioned
                ml_midLoftHandles.append(mLoftCurve)
                
                mGroup = mHandle.doGroup(True,True,asMeta=True,typeModifier = 'master')
                mAimGroup = mHandle.doGroup(True,True,asMeta=True,typeModifier = 'aim')
                
                
                _vList = DIST.get_normalizedWeightsByDistance(mGroup.mNode,
                                                              [ml_handles[0].mNode,ml_handles[-1].mNode])

                _scale = mc.scaleConstraint([ml_handles[0].mNode,ml_handles[-1].mNode],
                                            mAimGroup.mNode,maintainOffset = False)
        
                _res_attach = RIGCONSTRAINT.attach_toShape(mGroup.mNode, mMidTrackCurve.mNode, 'conPoint')
                TRANS.parent_set(_res_attach[0], mNoTransformNull.mNode)
                
                mGroup.resetAttrs('rotate')
                
                
                for c in [_scale]:
                    CONSTRAINT.set_weightsByDistance(c[0],_vList)
        
                mHandleFactory = self.asHandleFactory(mHandle.mNode)
        
                CORERIG.colorControl(mHandle.mNode,_side,'main',transparent = True)
                
            #Push scale back...
            for i,mHandle in enumerate(ml_handles):
                mHandle.scale = l_scales[i]
                
                
                
            
            #Lever Handle ===============================================================================
            if _b_lever:
                crv = CURVES.create_fromName('sphere', _size_width * .75, direction = 'y+')
                mHandle = cgmMeta.validateObjArg(crv, 'cgmObject', setClass=True)
                md_handles['lever'] = mHandle
                self.copyAttrTo('cgmName',mHandle.mNode,'cgmName',driven='target')
                mHandle.doStore('cgmType','blockHandle')
                mHandle.doStore('cgmNameModifier',"lever".format(i+1))
                mHandle.doName()                
                
                _short = mHandle.mNode
                mHandle.p_parent = mTemplateNull
                mHandle.resetAttrs()
                
                mHandle.p_position = pos_lever
                
                mHandleFactory.setHandle(mHandle.mNode)
                mLeverLoftCurve = mHandleFactory.rebuildAsLoftTarget('loftWideDown',#_loftShape,
                                                                     _size_width,
                                                                     shapeDirection = 'z+',rebuildHandle = False)
                #mc.makeIdentity(mHandle.mNode,a=True, s = True)#...must freeze scale once we're back parented and positioned
            
                mGroup = mHandle.doGroup(True,True,asMeta=True,typeModifier = 'master')
                mHandleFactory = self.asHandleFactory(mHandle.mNode)
            
                CORERIG.colorControl(mHandle.mNode,_side,'sub',transparent = True)
                
                
                SNAP.aim(mGroup.mNode, self.mNode,vectorUp=_mVectorUp)
                """
                mc.aimConstraint(md_handles['start'].mNode, mHandle.mNode, maintainOffset = False,
                                 aimVector = [0,0,1], upVector = [0,1,0], 
                                 worldUpObject = mRootUpHelper.mNode,
                                 worldUpType = 'objectrotation', 
                                 worldUpVector = [0,1,0])"""
                
            #AimEndHandle ============================================================================
            #mAimGroup = md_handles['end'].doGroup(True, asMeta=True,typeModifier = 'aim')
            #...not doing this now...
            SNAP.go(md_handles['end'].mNode, self.mNode, position=False)
            
            """
            _const = mc.aimConstraint(self.mNode, md_handles['end'].mNode, maintainOffset = False,
                                      aimVector = [0,0,-1], upVector = [0,1,0], 
                                      worldUpObject = mBaseOrientCurve.mNode,
                                      worldUpType = 'objectrotation', 
                                      worldUpVector = [0,1,0])"""
            
            #cgmMeta.cgmNode(_const[0]).doConnectIn('worldUpVector','{0}.baseUp'.format(self.mNode))
            
            
            #AimStartHandle ============================================================================
            log.debug("|{0}| >> Aim main handles...".format(_str_func)) 
            
            _const = mc.aimConstraint(md_handles['end'].mNode, md_handles['start'].mNode,
                                      maintainOffset = False,
                                      aimVector = [0,0,1],
                                      upVector = [0,1,0], 
                                      worldUpObject = mRootUpHelper.mNode,
                                      worldUpType = 'objectrotation', 
                                      worldUpVector = [0,1,0])
            

            
            #Main Track curve ============================================================================
            ml_handles_chain = [ml_handles[0]] + ml_midHandles + [ml_handles[-1]]
            
            log.debug("|{0}| >> Main TrackCrv...".format(_str_func)) 
            _mainTrackResult = CORERIG.create_at([mObj.mNode for mObj in ml_handles_chain],'linearTrack',
                                                baseName='mainTrack')
        
            mMainTrackCurve = cgmMeta.validateObjArg(_mainTrackResult[0],'cgmObject')
            mMainTrackCurve.rename(self.cgmName + 'mainHandlesTrack_crv')
            mMainTrackCurve.parent = mNoTransformNull
            
            
        #>>> Aim Main loft curves ================================================================== 
        log.debug("|{0}| >> Aim main loft curves...".format(_str_func)) 
        
        if _b_lever:
            ml_handles_chain.insert(0,md_handles['lever'])
            
        for i,mHandle in enumerate(ml_handles_chain):
            if mHandle in [md_handles['lever']]:#,md_handles['end']
                continue
            
            mLoft = mHandle.loftCurve
            _str_handle = mHandle.mNode
            
            mLoftAimGroup = mLoft.doGroup(True,asMeta=True,typeModifier = 'aim')
            mLoft.visibility = 1
            mLoft.setAttrFlags(['translate'])
            
            for mShape in mLoft.getShapes(asMeta=True):
                mShape.overrideDisplayType = 0
            
            _worldUpType = 'objectrotation'
            _worldUpBack = 'objectrotation'
            
            if mHandle == md_handles['lever']:
                _worldUpType = 'vector'
            elif mHandle == md_handles['start'] and _b_lever:
                _worldUpBack = 'vector'
                
            _aimBack = None
            _aimForward = None
            
            if mHandle == ml_handles_chain[0]:
                _aimForward = ml_handles_chain[i+1].mNode
            elif mHandle == ml_handles_chain[-1]:
                _aimBack = md_handles['start'].mNode#ml_handles_chain[].mNode
            else:
                _aimForward =  ml_handles_chain[i+1].mNode
                _aimBack  =  ml_handles_chain[i-1].mNode
                
            if _aimForward and _aimBack is None:
                mc.aimConstraint(_aimForward, mLoftAimGroup.mNode, maintainOffset = False,
                                 aimVector = [0,0,1], upVector = [0,1,0], 
                                 worldUpObject = mBaseOrientCurve.mNode,
                                 worldUpType = _worldUpType, 
                                 worldUpVector = [0,1,0])
            elif _aimBack and _aimForward is None:
                mc.aimConstraint(_aimBack, mLoftAimGroup.mNode, maintainOffset = False,
                                 aimVector = [0,0,-1], upVector = [0,1,0], 
                                 worldUpObject = mBaseOrientCurve.mNode,
                                 worldUpType = _worldUpBack, 
                                 worldUpVector = [0,1,0])
            else:
                mAimForward = mLoft.doCreateAt()
                mAimForward.p_parent = mLoft.p_parent
                mAimForward.doStore('cgmName',mHandle.mNode)                
                mAimForward.doStore('cgmTypeModifier','forward')
                mAimForward.doStore('cgmType','aimer')
                mAimForward.doName()
                
                mAimBack = mLoft.doCreateAt()
                mAimBack.p_parent = mLoft.p_parent
                mAimBack.doStore('cgmName',mHandle.mNode)                                
                mAimBack.doStore('cgmTypeModifier','back')
                mAimBack.doStore('cgmType','aimer')
                mAimBack.doName()
                
                mc.aimConstraint(_aimForward, mAimForward.mNode, maintainOffset = False,
                                 aimVector = [0,0,1], upVector = [0,1,0], 
                                 worldUpObject = mBaseOrientCurve.mNode,
                                 worldUpType = _worldUpType, 
                                 worldUpVector = [0,1,0])
                mc.aimConstraint(_aimBack, mAimBack.mNode, maintainOffset = False,
                                 aimVector = [0,0,-1], upVector = [0,1,0], 
                                 worldUpObject = mBaseOrientCurve.mNode,
                                 worldUpType = _worldUpBack, 
                                 worldUpVector = [0,1,0])                
                
                const = mc.orientConstraint([mAimForward.mNode, mAimBack.mNode],
                                            mLoftAimGroup.mNode, maintainOffset = False)[0]
                
                ATTR.set(const,'interpType',2)#.shortest...
                
                #...also aim our main handles...
                if mHandle not in [md_handles['end'],md_handles['start']]:
                    if not mHandle.getMessage('aimGroup'):
                        mHandleAimGroup = mHandle.doGroup(True,asMeta=True,typeModifier = 'aim')
                    else:
                        mHandleAimGroup = mHandle.getMessageAsMeta('aimGroup')
                        
                    mc.aimConstraint(_aimForward, mHandleAimGroup.mNode, maintainOffset = False,
                                     aimVector = [0,0,1], upVector = [0,1,0], 
                                     worldUpObject = mBaseOrientCurve.mNode,
                                     worldUpType = 'objectrotation', 
                                     worldUpVector = [0,1,0])

            if mHandle == md_handles['lever']:
                pass
                #ATTR.set_standardFlags( mHandle.mNode, ['rotate'])
            elif mHandle not in [md_handles['end']]:
                ATTR.set_standardFlags( mHandle.mNode, ['rotate','sz'])
                ATTR.connect('{0}.sy'.format(mHandle.mNode), '{0}.sz'.format(mHandle.mNode))
                
        
        #ml_shapers = copy.copy(ml_handles_chain)
        #>>> shaper handles =======================================================================
        if self.numShapers:
            _numShapers = self.numShapers
            ml_shapers = []
            log.debug("|{0}| >> Sub shaper handles: {1}".format(_str_func,_numShapers))
            
            mOrientHelper = mBaseOrientCurve
            
            log.debug("|{0}| >> pairs...".format(_str_func))
            

            ml_handlesToShaper = ml_handles_chain
            ml_shapers = [ml_handlesToShaper[0]]
                
            ml_pairs = LISTS.get_listPairs(ml_handlesToShaper)
            pprint.pprint(ml_pairs)
            
            
            for i,mPair in enumerate(ml_pairs):
                log.debug(cgmGEN._str_subLine)
                ml_shapersTmp = []
                
                _mStart = mPair[0]
                _mEnd = mPair[1]
                _end = _mEnd.mNode
                log.debug("|{0}| >> pairs: {1} | end: {2}".format(_str_func,i,_end))
                
                _pos_start = _mStart.p_position
                _pos_end = _mEnd.p_position 
                
                if i == 0 and self.buildLeverBase:
                    _numShapers = 1
                else:
                    _numShapers = self.numShapers

                
                _vec = MATH.get_vector_of_two_points(_pos_start, _pos_end)
                _offsetDist = DIST.get_distance_between_points(_pos_start,_pos_end) / (_numShapers+1)
                _l_pos_seg = [ DIST.get_pos_by_vec_dist(_pos_start,
                                                        _vec,
                                                        (_offsetDist * ii)) for ii in range(_numShapers+1)] + [_pos_end]
            
                _mVectorAim = MATH.get_vector_of_two_points(_pos_start, _pos_end,asEuclid=True)
                _mVectorUp = _mVectorAim.up()
                _worldUpVector = [_mVectorUp.x,_mVectorUp.y,_mVectorUp.z]        
            
            
                #Linear track curve ----------------------------------------------------------------------
                _linearCurve = mc.curve(d=1,p=[_pos_start,_pos_end])
                mLinearCurve = cgmMeta.validateObjArg(_linearCurve,'cgmObject')
                
            
                l_clusters = []
                #_l_clusterParents = [mStartHandle,mEndHandle]
                for ii,cv in enumerate(mLinearCurve.getComponents('cv')):
                    _res = mc.cluster(cv, n = 'seg_{0}_{1}_cluster'.format(mPair[0].p_nameBase,ii))
                    TRANS.parent_set(_res[1], mTemplateNull)
                    mc.pointConstraint(mPair[ii].getMessage('loftCurve')[0],
                                       _res[1],maintainOffset=True)
                    ATTR.set(_res[1],'v',False)                
                    l_clusters.append(_res)
            
            
                mLinearCurve.parent = mNoTransformNull
                mLinearCurve.rename('seg_{0}_trackCrv'.format(i))
            
                #mLinearCurve.inheritsTransform = False      
            
            
                #Tmp loft mesh -------------------------------------------------------------------
                _l_targets = [mObj.loftCurve.mNode for mObj in mPair]
            
                _res_body = mc.loft(_l_targets, o = True, d = 3, po = 0 )
                _str_tmpMesh =_res_body[0]
            
                l_scales_seg = []
            
                #for mHandle in mPair:
                    #l_scales_seg.append(mHandle.scale)
                    #mHandle.scale = 1,1,1
                
                #Sub handles... ------------------------------------------------------------------------------------
                for ii,p in enumerate(_l_pos_seg[1:-1]):
                    #mHandle = mHandleFactory.buildBaseShape('circle', _size, shapeDirection = 'y+')
                    mHandle = cgmMeta.cgmObject(name = 'subHandle_{0}_{1}'.format(i,ii))
                    _short = mHandle.mNode
                    ml_handles.append(mHandle)
                    mHandle.p_position = p
                    SNAP.aim_atPoint(_short,_l_pos_seg[ii+2],'z+', 'y+', mode='vector', vectorUp = _mVectorUp)
            
                    #...Make our curve
                    _d = RAYS.cast(_str_tmpMesh, _short, 'y+')
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
            
                    #self.copyAttrTo(_baseNameAttrs[1],mHandle.mNode,'cgmName',driven='target')
                    self.copyAttrTo('cgmName',mHandle.mNode,'cgmName',driven='target')
            
                    mHandle.doStore('cgmName','subHandle_{0}_{1}'.format(i,ii))
                    mHandle.doStore('cgmType','blockHandle')
                    mHandle.doName()
            
                    mHandle.p_parent = mTemplateNull
            
                    mGroup = mHandle.doGroup(True,True,asMeta=True,typeModifier = 'master')
                    mGroup.p_parent = mTemplateNull
            
                    _vList = DIST.get_normalizedWeightsByDistance(mGroup.mNode,[mPair[0].mNode,mPair[1].mNode])
            
                    _scale = mc.scaleConstraint([mPair[0].mNode,mPair[1].mNode],mGroup.mNode,maintainOffset = False)#Point contraint loc to the object
            
                    _res_attach = RIGCONSTRAINT.attach_toShape(mGroup.mNode, 
                                                               mLinearCurve.mNode,
                                                               'conPoint')
                    TRANS.parent_set(_res_attach[0], mNoTransformNull.mNode)
            
                    for c in [_scale]:
                        CONSTRAINT.set_weightsByDistance(c[0],_vList)
            
                    #Convert to loft curve setup ----------------------------------------------------
                    mHandleFactory = self.asHandleFactory(mHandle.mNode)
                    mHandleFactory.rebuildAsLoftTarget('self', None, shapeDirection = 'z+')
            
            
                    CORERIG.colorControl(mHandle.mNode,_side,'sub',transparent = True)        
                    #LOC.create(position = p)
                    ml_shapers.append(mHandle)
                    ml_shapersTmp.append(mHandle)
                    
                ml_shapers.append(mPair[1])
                mc.delete(_res_body)
                
                _mStart.msgList_connect('subShapers',[mObj.mNode for mObj in ml_shapersTmp])                    
            
                #Push scale back...
                #for mHandle in mPair:
                    #mHandle.scale = l_scales_seg[i]
            
                #Template Loft Mesh -------------------------------------
                #mTemplateLoft = self.getMessage('templateLoftMesh',asMeta=True)[0]        
                #for s in mTemplateLoft.getShapes(asMeta=True):
                    #s.overrideDisplayType = 1       
            
            
                #Aim the segment
                
                for ii,mHandle in enumerate(ml_shapersTmp):
                    mAimGroup = mHandle.doGroup(True,asMeta=True,typeModifier = 'aim')
                    log.debug("|{0}| >> seg constrain: {1} {2} | end: {3}".format(_str_func,i,ii,_end))
                    
                    mc.aimConstraint([_end], mAimGroup.mNode, maintainOffset = True, #skip = 'z',
                                     aimVector = [0,0,1], upVector = [0,1,0],
                                     worldUpObject = mBaseOrientCurve.mNode,
                                     worldUpType = 'objectrotation', worldUpVector = [0,1,0])
                
                
        #>>> Connections =======================================================================================
        self.msgList_connect('templateHandles',[mObj.mNode for mObj in ml_handles_chain])
        
        #if ml_shapers:
        #    self.msgList_connect('templateHandles',[mObj.mNode for mObj in ml_shapers])
        #else:
        #    self.msgList_connect('templateHandles',[mObj.mNode for mObj in ml_handles_chain])
            
        #>>Loft Mesh =========================================================================================
        if self.numShapers:
            targets = [mObj.loftCurve.mNode for mObj in ml_shapers]
            self.msgList_connect('shaperHandles',[mObj.mNode for mObj in ml_shapers])
            
        else:
            targets = [mObj.loftCurve.mNode for mObj in ml_handles_chain]        
        
        """
            return {'targets':targets,
                    'mPrerigNull' : mTemplateNull,
                    'uAttr':'numControls',
                    'uAttr2':'loftSplit',
                    'polyType':'bezier',
                    'baseName':self.cgmName}"""
    
        self.atUtils('create_prerigLoftMesh',
                     targets,
                     mTemplateNull,
                     'numControls',                     
                     'loftSplit',
                     polyType='bezier',
                     baseName = self.cgmName )
        #for t in targets:
            #ATTR.set(t,'v',0)
        mNoTransformNull.v = False
        
        #End setup======================================================================================
        if _ikSetup != 'none':
            mEndHandle = ml_handles_chain[-1]
            log.debug("|{0}| >> ikSetup. End: {1}".format(_str_func,mEndHandle))
            mHandleFactory.setHandle(mEndHandle.mNode)
            
            if _ikEnd == 'bank':
                log.debug("|{0}| >> Bank setup".format(_str_func)) 
                mHandleFactory.addPivotSetupHelper().p_parent = mTemplateNull
            elif _ikEnd == 'foot':
                log.debug("|{0}| >> foot setup".format(_str_func)) 
                mFoot,mFootLoftTop = mHandleFactory.addFootHelper()
                mFoot.p_parent = mTemplateNull
            elif _ikEnd == 'proxy':
                log.debug("|{0}| >> proxy setup".format(_str_func)) 
                mProxy = mHandleFactory.addProxyHelper(shapeDirection = 'z+')
                mProxy.p_parent = mEndHandle
                
                pos_proxy = SNAPCALLS.get_special_pos(mEndHandle.p_nameLong,
                                                     'axisBox','z+',False)
                
                log.debug("|{0}| >> posProxy: {1}".format(_str_func,pos_proxy))
                mProxy.p_position = pos_proxy
                CORERIG.copy_pivot(mProxy.mNode,mEndHandle.mNode)
                
        #Aim end handle -----------------------------------------------------------------------------------
        SNAP.aim_atPoint(md_handles['end'].mNode, position=_l_basePos[0], 
                         aimAxis="z-", mode='vector', vectorUp=_mVectorUp)
        
        self.blockState = 'template'#...buffer


    return True


#=============================================================================================================
#>> Prerig
#=============================================================================================================
def prerig(self):
    try:
        _str_func = 'prerig'

        log.debug("|{0}| >> ...".format(_str_func)+ '-'*80)
        log.debug("{0}".format(self))
        #log.debug("|{0}| >> [{1}] | side: {2}".format(_str_func,_short, _side))   
        
        _short = self.p_nameShort
        _side = self.atUtils('get_side')        
    
        #> Get our stored dat ==================================================================================================
        mHandleFactory = self.asHandleFactory()
        
        _ikSetup = self.getEnumValueString('ikSetup')
        _ikEnd = self.getEnumValueString('ikEnd')

        ml_templateHandles = self.msgList_get('templateHandles')
        
        #Names dat.... -----------------------------------------------------------------
        _l_baseNames = ATTR.datList_get(self.mNode, 'nameList')        
        #b_iterNames = False
        if len(_l_baseNames) < len(ml_templateHandles):
            log.debug("|{0}| >>  Not enough nameList attrs, need to generate".format(_str_func))
            #b_iterNames = True
            baseName = _l_baseNames[0]
            _l_baseNamesNEW = []
            for i in range(len(ml_templateHandles)):
                _l_baseNamesNEW.append("{0}_{1}".format(baseName,i))
            ATTR.datList_connect(self.mNode,'nameList',_l_baseNamesNEW)
            _l_baseNames = ATTR.datList_get(self.mNode, 'nameList')#...get em back
            
        _baseNameAttrs = ATTR.datList_getAttrs(self.mNode,'nameList')
        
        #pprint.pprint(vars())
        
        #Create some nulls Null  =========================================================================
        self.atUtils('module_verify')
        
        
        mPrerigNull = self.atUtils('stateNull_verify','prerig')
        mNoTransformNull = self.atUtils('noTransformNull_verify','prerig')
    
        #mNoTransformNull = BLOCKUTILS.noTransformNull_verify(self)
        
        #...cog -----------------------------------------------------------------------------
        if self.addCog:
            self.asHandleFactory(ml_templateHandles[0]).addCogHelper().p_parent = mPrerigNull
        
        mStartHandle = ml_templateHandles[0]    
        mEndHandle = ml_templateHandles[-1]    
        mOrientHelper = self.orientHelper
        #Because Maya doesn't eval correctly all the time...
        #_orient = mOrientHelper.rotate
        #mOrientHelper.rotate = [1+v for v in _orient]
        #mOrientHelper.rotate = _orient
        
        ml_handles = []
        ml_jointHandles = []        
        
        _size = MATH.average(mHandleFactory.get_axisBox_size(mStartHandle.mNode))
        #DIST.get_bb_size(mStartHandle.loftCurve.mNode,True)[0]
        _sizeSub = _size * .33    
        _vec_root_up = mOrientHelper.getAxisVector('y+')
        
        
        #Initial logic=========================================================================================
        log.debug("|{0}| >> Initial Logic...".format(_str_func)) 
        
        _pos_start = mStartHandle.p_position
        _pos_end = mEndHandle.p_position 
        _vec = MATH.get_vector_of_two_points(_pos_start, _pos_end)
        
        _mVectorAim = MATH.get_vector_of_two_points(_pos_start, _pos_end,asEuclid=True)
        _mVectorUp = _mVectorAim.up()
        _worldUpVector = [_mVectorUp.x,_mVectorUp.y,_mVectorUp.z]
        
        #Foot helper ============================================================================
        mFootHelper = False
        if ml_templateHandles[-1].getMessage('pivotHelper'):
            log.debug("|{0}| >> footHelper".format(_str_func))
            mFootHelper = ml_templateHandles[-1].pivotHelper
    
        if self.hasBallJoint and mFootHelper:
            ml_templateHandles.append(mFootHelper.pivotCenter)
        if self.hasEndJoint and mFootHelper:
            ml_templateHandles.append(mFootHelper.pivotFront)
            
        #Finger Tip ============================================================================
        if _ikSetup != 'none' and _ikEnd == 'catInTheHat':#bankTip
            log.debug("|{0}| >> bankTip setup...".format(_str_func))
            mEndHandle = ml_templateHandles[-1]
            
            """
            #Make a tip last mesh segment to build our pivot setup from...
            l_curves = []
            mTrans = mEndHandle.doCreateAt()
            mTrans.p_parent = False
            for mObj in ml_templateHandles[-2:]:
                #CORERIG.shapeParent_in_place(mTrans.mNode,mObj.loftCurve.mNode)
                l_curves.append(mObj.loftCurve.mNode)
            BUILDUTILS.create_loftMesh(l_curves)"""
            
            
            log.debug("|{0}| >> ikSetup. End: {1}".format(_str_func,mEndHandle))
            mHandleFactory.setHandle(mEndHandle.mNode)
            mHandleFactory.addPivotSetupHelper().p_parent = mPrerigNull
                
        #return 
        #Sub handles... ------------------------------------------------------------------------------------
        log.debug("|{0}| >> PreRig Handle creation...".format(_str_func))
        ml_aimGroups = []
        for i,mTemplateHandle in enumerate(ml_templateHandles):
            log.debug("|{0}| >> prerig handle cnt: {1}".format(_str_func,i))
            _sizeUse = MATH.average(mHandleFactory.get_axisBox_size(mTemplateHandle.mNode)) * .33
            
            try: _HandleSnapTo = mTemplateHandle.loftCurve.mNode
            except: _HandleSnapTo = mTemplateHandle.mNode
            
            crv = CURVES.create_fromName('cubeOpen', size = _sizeUse)
            mHandle = cgmMeta.validateObjArg(crv, 'cgmObject', setClass=True)
            _short = mHandle.mNode
            
            #if b_iterNames:
                #ATTR.copy_to(self.mNode,_baseNameAttrs[0],_short, 'cgmName', driven='target')
                #mHandle.doStore('cgmIterator',i)
            #    mHandle.doStore('cgmName',"{0}_{1}".format(_l_baseNames[0],i))
            #else:
            ATTR.copy_to(self.mNode,_baseNameAttrs[i],_short, 'cgmName', driven='target')
            mHandle.doStore('cgmType','preHandle')
            mHandle.doName()
            ml_handles.append(mHandle)
            
            mHandle.doSnapTo(_HandleSnapTo)
            mHandle.p_parent = mPrerigNull
            mGroup = mHandle.doGroup(True,True,asMeta=True,typeModifier = 'master')
            ml_aimGroups.append(mGroup)
            
            mc.parentConstraint(_HandleSnapTo, mGroup.mNode, maintainOffset=True)
            
            mHandleFactory = self.asHandleFactory(mHandle.mNode)
            
            #Convert to loft curve setup ----------------------------------------------------
            ml_jointHandles.append(mHandleFactory.addJointHelper(baseSize = _sizeSub))
            CORERIG.colorControl(mHandle.mNode,_side,'sub',transparent = True)
        
        
        
        self.msgList_connect('prerigHandles', ml_handles)
        
        #ml_handles[0].connectChildNode(mOrientHelper.mNode,'orientHelper')      
        
        self.atUtils('prerigHandles_getNameDat',True)
        
                                 
        #Joint placer loft....
        targets = [mObj.jointHelper.loftCurve.mNode for mObj in ml_handles]
        
        
        self.msgList_connect('jointHelpers',targets)
        
        self.atUtils('create_jointLoft',
                     targets,
                     mPrerigNull,
                     baseCount = self.numRoll * self.numControls,
                     baseName = self.cgmName,
                     simpleMode = True)        
        
        """
        BLOCKUTILS.create_jointLoft(self,targets,
                                    mPrerigNull,'neckJoints',
                                    baseName = _l_baseNames[1] )
        """
        for t in targets:
            ATTR.set(t,'v',0)
            #ATTR.set_standardFlags(t,[v])
            
            
    
        
        #if self.addScalePivot:
            #mHandleFactory.addScalePivotHelper().p_parent = mPrerigNull        
        
        
        #Close out ==================================================================================================
        mNoTransformNull.v = False
        #cgmGEN.func_snapShot(vars())
        
        self.blockState = 'prerig'
            
        return True
    
    except Exception,err:cgmGEN.cgmException(Exception,err)
    
def prerigDelete(self):
    if self.getMessage('templateLoftMesh'):
        mTemplateLoft = self.getMessage('templateLoftMesh',asMeta=True)[0]
        for s in mTemplateLoft.getShapes(asMeta=True):
            s.overrideDisplayType = 2
        mTemplateLoft.v = True
        
def skeleton_build(self, forceNew = True):
    _short = self.mNode
    _str_func = 'skeleton_build'
    log.debug("|{0}| >>  {1}".format(_str_func,self)+ '-'*80)
    
    ml_joints = []
    
    mPrerigNull = self.prerigNull
    
    mModule = self.moduleTarget
    if not mModule:
        raise ValueError,"No moduleTarget connected"
    mRigNull = mModule.rigNull
    if not mRigNull:
        raise ValueError,"No rigNull connected"
    
    ml_templateHandles = self.msgList_get('templateHandles',asMeta = True)
    if not ml_templateHandles:
        raise ValueError,"No templateHandles connected"
    
    ml_jointHelpers = self.msgList_get('jointHelpers',asMeta = True)
    if not ml_jointHelpers:
        raise ValueError,"No jointHelpers connected"
    
    #>> If skeletons there, delete ------------------------------------------------------------------- 
    _bfr = mRigNull.msgList_get('moduleJoints',asMeta=True)
    if _bfr:
        log.debug("|{0}| >> Joints detected...".format(_str_func))            
        if forceNew:
            log.debug("|{0}| >> force new...".format(_str_func))                            
            mc.delete([mObj.mNode for mObj in _bfr])
        else:
            return _bfr
    
    #_baseNameAttrs = ATTR.datList_getAttrs(self.mNode,'baseNames')
    
    _d_base = self.atBlockUtils('skeleton_getNameDictBase')
    _l_names = ATTR.datList_get(self.mNode,'nameList')
    
    #Deal with Lever joint or not --------------------------------------------------
    _b_lever = False
    if self.buildLeverBase:
        if not self.hasLeverJoint:
            _l_names = _l_names[1:]
            ml_jointHelpers = ml_jointHelpers[1:]
        else:
            _b_lever = True
    
    
    _rollCounts = ATTR.datList_get(self.mNode,'rollCount')
    log.debug("|{0}| >> rollCount: {1}".format(_str_func,_rollCounts))
    _int_rollStart = 0
    if self.hasLeverJoint:
        _int_rollStart = 1
    _d_rollCounts = {i+_int_rollStart:v for i,v in enumerate(_rollCounts)}
    
    
    if len(_l_names) != len(ml_jointHelpers):
        return log.error("Namelist lengths and handle lengths doesn't match | len {0} != {1}".format(_l_names,len(ml_jointHelpers)))
    

    _d_base['cgmType'] = 'skinJoint'
    
    #Build our handle chain ======================================================
    l_pos = []
    
    if not self.hasEndJoint:
        log.debug("|{0}| >> No end joint, culling...".format(_str_func,_rollCounts))
        ml_jointHelpers = ml_jointHelpers[:-1]
    
    for mObj in ml_jointHelpers:
        l_pos.append(mObj.p_position)
            
    mOrientHelper = self.orientHelper
    ml_handleJoints = JOINT.build_chain(l_pos, parent=True,
                                        worldUpAxis= mOrientHelper.getAxisVector('y+'), orient= False)
    
    if _b_lever:
        ml_handleJoints[1].p_parent = False
        #Lever...
        mLever = ml_handleJoints[0]
        #_const = mc.aimConstraint(ml_handleJoints[1].mNode, mLever.mNode, maintainOffset = False,
        #                          aimVector = [0,0,1], upVector = [0,1,0], 
        #                          worldUpType = 'Vector', 
        #                          worldUpVector = self.baseUp)
        #mc.delete()
        SNAP.aim(mLever.mNode, ml_handleJoints[1].mNode, 'z+','y+','vector',
                 self.rootUpHelper.getAxisVector('y+'))
        JOINT.freezeOrientation(mLever.mNode)
        
        #Rest...
        JOINT.orientChain(ml_handleJoints[1:],
                          worldUpAxis= mOrientHelper.getAxisVector('y+'))
        ml_handleJoints[1].p_parent = ml_handleJoints[0]
        
    else:
        JOINT.orientChain(ml_handleJoints,
                          worldUpAxis= mOrientHelper.getAxisVector('y+'))        
    

    ml_joints = []
    d_rolls = {}
    
    for i,mJnt in enumerate(ml_handleJoints):
        d=copy.copy(_d_base)
        d['cgmName'] = _l_names[i]
        mJnt.rename(NAMETOOLS.returnCombinedNameFromDict(d))
        for t,v in d.iteritems():
            mJnt.doStore(t,v)
        ml_joints.append(mJnt)
        if mJnt != ml_handleJoints[-1]:
            if _d_rollCounts.get(i):
                log.debug("|{0}| >> {1} Rolljoints: {2}".format(_str_func,mJnt.mNode,_d_rollCounts.get(i)))
                _roll = _d_rollCounts.get(i)
                _p_start = l_pos[i]
                _p_end = l_pos[i+1]
                
                if _roll != 1:
                    _l_pos = BUILDUTILS.get_posList_fromStartEnd(_p_start,_p_end,_roll+2)[1:-1]
                else:
                    _l_pos = BUILDUTILS.get_posList_fromStartEnd(_p_start,_p_end,_roll)
                    
                log.debug("|{0}| >> {1}".format(_str_func,_l_pos))
                ml_rolls = []
                
                ml_handleJoints[i].select()
                
                for ii,p in enumerate(_l_pos):
                    mRoll = cgmMeta.validateObjArg( mc.joint (p=(p[0],p[1],p[2])))
                    dRoll=copy.copy(d)
                    
                    dRoll['cgmNameModifier'] = 'roll'
                    dRoll['cgmIterator'] = ii
                    
                    mRoll.rename(NAMETOOLS.returnCombinedNameFromDict(dRoll))
                    for t,v in dRoll.iteritems():
                        mRoll.doStore(t,v)                    
                    #mRoll.jointOrient = mJnt.jointOrient
                    mRoll.rotate = mJnt.rotate
                    ml_rolls.append(mRoll)
                    ml_joints.append(mRoll)
                d_rolls[i] = ml_rolls

    ml_joints[0].parent = False
    
    _radius = DIST.get_distance_between_points(ml_joints[0].p_position, ml_joints[-1].p_position)/ 20
    #MATH.get_space_value(5)
    
    for mJoint in ml_joints:
        mJoint.displayLocalAxis = 1
        mJoint.radius = _radius

    mRigNull.msgList_connect('moduleJoints', ml_joints)
    
    mPrerigNull.msgList_connect('handleJoints', ml_handleJoints)
    #mPrerigNull.msgList_connect('moduleJoints', ml_joints)
    
    for i,l in d_rolls.iteritems():
        mPrerigNull.msgList_connect('rollJoints_{0}'.format(i), l)
        for mJnt in l:
            mJnt.radius = _radius / 2
    self.atBlockUtils('skeleton_connectToParent')
    

        
    
    #PivotHelper -------------------------------------------------------------------------------------
    if ml_templateHandles[-1].getMessage('pivotHelper'):
        log.debug("|{0}| >> Pivot helper found".format(_str_func))
        if len(ml_joints) < len(ml_templateHandles):
            log.debug("|{0}| >> No extra ball/toe joints detected...".format(_str_func))
        else:
            mEnd = ml_handleJoints[int(self.hasLeverJoint) + self.numControls - 1]
            ml_children = mEnd.getChildren(asMeta=True)
            for mChild in ml_children:
                mChild.parent = False
                JOINT.orientChain(ml_handleJoints[self.numControls - 1:],
                                  worldUpAxis= ml_templateHandles[-1].pivotHelper.getAxisVector('y+') )
        
            mEnd.jointOrient = 0,0,0
        
            for mChild in ml_children:
                mChild.parent = mEnd    
    """
    if len(ml_handleJoints) > self.numControls:
        log.debug("|{0}| >> Extra joints, checking last handle".format(_str_func))
        mEnd = ml_handleJoints[self.numControls - 1]
        ml_children = mEnd.getChildren(asMeta=True)
        for mChild in ml_children:
            mChild.parent = False
            
            JOINT.orientChain(ml_handleJoints[self.numControls - 1:],
                              worldUpAxis= ml_templateHandles[-1].pivotHelper.getAxisVector('y+') )
            
        mEnd.jointOrient = 0,0,0
        
        for mChild in ml_children:
            mChild.parent = mEnd"""
    
    #End joint fix when not end joint is there...
    if not self.hasEndJoint:
        mEnd = ml_joints[-1]        
        log.debug("|{0}| >> Fixing end: {1}".format(_str_func,mEnd))
        SNAP.aim(mEnd.mNode,
                 ml_templateHandles[-1].mNode,
                 'z+','y+','vector',
                 ml_joints[-2].getAxisVector('y+'))
        JOINT.freezeOrientation(mEnd.mNode)
        
    self.blockState = 'skeleton'#...buffer
    
    return ml_joints

#=============================================================================================================
#>> rig
#=============================================================================================================
#NOTE - self here is a rig Factory....

#d_preferredAngles = {'default':[0,-10, 10]}#In terms of aim up out for orientation relative values, stored left, if right, it will invert
#d_preferredAngles = {'out':10}
d_preferredAngles = {}
d_rotateOrders = {'default':'yxz'}

#Rig build stuff goes through the rig build factory ------------------------------------------------------
@cgmGEN.Timer
def rig_prechecks(self):
    _short = self.d_block['shortName']
    _str_func = 'rig_prechecks'
    log.debug("|{0}| >>  {1}".format(_str_func,self)+ '-'*80)
        
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
    #if mBlock.ikSetup >=1:
        #raise NotImplementedError,"Haven't setup ik mode: {0}".format(ATTR.get_enumValueString(mBlock.mNode,'ikSetup'))
        
    #Lever ============================================================================    
    _b_lever = False
    self.b_leverJoint = False
    if mBlock.buildLeverBase:
        _b_lever = True        
        if mBlock.hasLeverJoint:
            self.b_leverJoint = True
        else:
            log.debug("|{0}| >> Need leverJoint | self.b_leverJoint ".format(_str_func))
        self.mRootTemplateHandle = ml_templateHandles[1]
        
    self.b_lever = _b_lever
    log.debug("|{0}| >> Lever: {1}".format(_str_func,self.b_lever))    
    log.debug("|{0}| >> self.mRootTemplateHandle : {1}".format(_str_func,self.mRootTemplateHandle))    
    
    #Pivot checks ============================================================================
    mPivotHolderHandle = ml_templateHandles[-1]
    self.b_pivotSetup = False
    self.mPivotHelper = False
    if mPivotHolderHandle.getMessage('pivotHelper'):
        log.debug("|{0}| >> Pivot setup needed".format(_str_func))
        self.b_pivotSetup = True
        self.mPivotHelper = mPivotHolderHandle.getMessage('pivotHelper',asMeta=True)[0]
        log.debug(cgmGEN._str_subLine)
        
    #Roll joints =============================================================================
    #Look for roll chains...
    log.debug("|{0}| >> Looking for rollChains...".format(_str_func))    
    _check = 0
    
    self.md_roll = {}
    self.md_rollMulti = {}
    self.ml_segHandles = []
    self.md_segHandleIndices = {}
    #self.b_segmentSetup = False
    #self.b_rollSetup = False
    
    while _check <= len(ml_handleJoints):
        mBuffer = mPrerigNull.msgList_get('rollJoints_{0}'.format(_check))
        _len = len(mBuffer)
        self.md_rollMulti[_check] = False
        
        if mBuffer:
            mStart = ml_handleJoints[_check]
            mEnd = ml_handleJoints[_check+1]            
            
            ml_roll = [mStart] + mBuffer + [mEnd]
            self.ml_segHandles
            if mStart not in self.ml_segHandles:
                self.ml_segHandles.append(mStart)
                self.md_segHandleIndices[mStart] = _check
            if mEnd not in self.ml_segHandles:
                self.ml_segHandles.append(mEnd)
                self.md_segHandleIndices[mEnd] = _check+1
            
            self.md_roll[_check] = ml_roll            
            if _len > 1:
                self.md_rollMulti[_check] = True
            log.debug("|{0}| >> Roll joints found on seg: {1} | len: {2} | multi: {3}".format(_str_func,
                                                                                      _check,
                                                                                      _len,
                                                                                      self.md_rollMulti[_check]))
        _check +=1
        
    #log.debug("|{0}| >> Segment setup: {1}".format(_str_func,self.b_segmentSetup))            
    #log.debug("|{0}| >> Roll setup: {1}".format(_str_func,self.b_rollSetup))
    
    if self.b_leverJoint:
        log.debug("|{0}| >> lever roll remap...".format(_str_func))
        md_rollRemap = {}
        for i,v in self.md_roll.iteritems():
            md_rollRemap[i-1] = v
        self.md_roll = md_rollRemap
        
        ml_indiceRemap = {}
        for v,i in self.md_segHandleIndices.iteritems():
            ml_indiceRemap[v] = i-1
        self.md_segHandleIndices = ml_indiceRemap
        
    
    log.debug("|{0}| >> self.md_roll...".format(_str_func))    
    pprint.pprint(self.md_roll)
    log.debug(cgmGEN._str_subLine)
    
    log.debug("|{0}| >> self.ml_segHandles...".format(_str_func))        
    pprint.pprint(self.ml_segHandles)
    log.debug(cgmGEN._str_subLine)
    
    #Frame Handles =============================================================================
    self.ml_handleTargets = mPrerigNull.msgList_get('handleJoints')
    if self.b_leverJoint:
        log.debug("|{0}| >> handleJoint lever cull...".format(_str_func))        
        self.ml_handleTargets = self.ml_handleTargets[1:]
        ml_handleJoints = ml_handleJoints[1:]
        
    self.mToe = False
    self.mBall = False
    self.int_handleEndIdx = -1
    self.b_ikNeedEnd = False
    l= []
    
    str_ikEnd = ATTR.get_enumValueString(mBlock.mNode,'ikEnd')
    log.debug("|{0}| >> IK End: {1}".format(_str_func,format(str_ikEnd)))
    
    if str_ikEnd in ['foot']:
        if mBlock.hasEndJoint:
            self.mToe = self.ml_handleTargets.pop(-1)
            log.debug("|{0}| >> mToe: {1}".format(_str_func,self.mToe))
            self.int_handleEndIdx -=1
        if mBlock.hasBallJoint:
            self.mBall = self.ml_handleTargets.pop(-1)
            log.debug("|{0}| >> mBall: {1}".format(_str_func,self.mBall))        
            self.int_handleEndIdx -=1
    elif str_ikEnd in ['tipEnd','tipBase']:
        log.debug("|{0}| >> tip setup...".format(_str_func))        
        if not mBlock.hasEndJoint:
            self.b_ikNeedEnd = True
            log.debug("|{0}| >> Need IK end joint".format(_str_func))
        else:
            self.int_handleEndIdx -=1
            
    
    ml_use = ml_handleJoints[:self.int_handleEndIdx]
    if len(ml_use) == 1:
        mid=0
        mMidHandle = ml_use[0]
    else:
        mid = int((len(ml_use))/2)
        mMidHandle = ml_use[mid]
    self.int_handleMidIdx = mid
    
    self.int_templateHandleMidIdx = mid
    
    #if self.b_lever:
        #log.debug("|{0}| >> lever pop...".format(_str_func))        
        #self.int_templateHandleMidIdx +=1
    
    
    log.debug("|{0}| >> self.ml_handleTargets: {1} | {2}".format(_str_func,
                                                                 len(self.ml_handleTargets),
                                                                 self.ml_handleTargets))
    log.debug("|{0}| >> Mid self.int_handleMidIdx idx: {1} | {2}".format(_str_func,self.int_handleMidIdx,
                                                                         ml_handleJoints[self.int_handleMidIdx]))    
    log.debug("|{0}| >> End self.int_handleEndIdx idx: {1} | {2}".format(_str_func,self.int_handleEndIdx,
                                                                         ml_handleJoints[self.int_handleEndIdx]))
    log.debug("|{0}| >> Mid self.int_templateHandleMidIdx idx: {1} | {2}".format(_str_func,self.int_templateHandleMidIdx,
                                                                         ml_templateHandles[self.int_templateHandleMidIdx]))
        

    
    if self.int_handleEndIdx ==  -1:
        self.ml_handleTargetsCulled = copy.copy(ml_handleJoints)
    else:
        self.ml_handleTargetsCulled = ml_handleJoints[:self.int_handleEndIdx+1]
    self.mIKEndSkinJnt = ml_handleJoints[self.int_handleEndIdx]
    
    log.debug("|{0}| >> self.ml_handleTargetsCulled: {1} | {2}".format(_str_func,
                                                                 len(self.ml_handleTargetsCulled),
                                                                 self.ml_handleTargetsCulled))
    log.debug("|{0}| >> self.mIKEndSkinJnt: {1}".format(_str_func,
                                                        self.mIKEndSkinJnt))    
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
    
    
    #DynParents =============================================================================
    self.UTILS.get_dynParentTargetsDat(self)
    
    #rotateOrder =============================================================================
    _str_orientation = self.d_orientation['str']
    
    self.rotateOrder = "{0}{1}{2}".format(_str_orientation[1],_str_orientation[2],_str_orientation[0])
    self.rotateOrderIK = "{2}{0}{1}".format(_str_orientation[0],_str_orientation[1],_str_orientation[2])
    
    log.debug("|{0}| >> rotateOrder | self.rotateOrder: {1}".format(_str_func,self.rotateOrder))
    log.debug("|{0}| >> rotateOrder | self.rotateOrderIK: {1}".format(_str_func,self.rotateOrderIK))

    log.debug(cgmGEN._str_subLine)
    
    #mainRot axis =============================================================================
    """For twist stuff"""
    _mainAxis = ATTR.get_enumValueString(mBlock.mNode,'mainRotAxis')
    _axis = ['aim','up','out']
    if _mainAxis == 'up':
        _upAxis = 'out'
    else:
        _upAxis = 'up'
    
    self.v_twistUp = self.d_orientation.get('vector{0}'.format(_mainAxis.capitalize()))
    log.debug("|{0}| >> twistUp | self.v_twistUp: {1}".format(_str_func,self.v_twistUp))

    log.debug(cgmGEN._str_subLine)    
    

@cgmGEN.Timer
def rig_skeleton(self):
    _short = self.d_block['shortName']
    _str_func = 'rig_skeleton'
    log.debug("|{0}| >>  {1}".format(_str_func,self)+ '-'*80)
        
    mBlock = self.mBlock
    mRigNull = self.mRigNull
    mPrerigNull = mBlock.prerigNull
    ml_jointsToConnect = []
    ml_jointsToHide = []
    ml_blendJoints = []
    ml_joints = mRigNull.msgList_get('moduleJoints')
    ml_handleJoints = mPrerigNull.msgList_get('handleJoints')
    self.d_joints['ml_moduleJoints'] = ml_joints
    str_ikBase = ATTR.get_enumValueString(mBlock.mNode,'ikBase')        
    
    reload(BLOCKUTILS)
    BLOCKUTILS.skeleton_pushSettings(ml_joints,self.d_orientation['str'],
                                     self.d_module['mirrorDirection'],
                                     d_rotateOrders)#d_preferredAngles)
    
    
    log.info("|{0}| >> rig chain...".format(_str_func))              
    ml_rigJoints = BLOCKUTILS.skeleton_buildDuplicateChain(mBlock,
                                                           ml_joints, None ,
                                                           mRigNull,'rigJoints',
                                                           blockNames=False,
                                                           cgmType = 'rigJoint',
                                                           connectToSource = 'rig')
    #pprint.pprint(ml_rigJoints)
    
    
    #...fk chain ----------------------------------------------------------------------------------------------
    log.info("|{0}| >> fk_chain".format(_str_func))
    #ml_fkJoints = BLOCKUTILS.skeleton_buildHandleChain(mBlock,'fk','fkJoints')
    
    
    ml_fkJoints = BLOCKUTILS.skeleton_buildDuplicateChain(mBlock, ml_handleJoints,
                                                          'fk',mRigNull,'fkJoints',
                                                          blockNames=False,cgmType = 'frame')
    ml_jointsToHide.extend(ml_fkJoints)
    
    ml_handleJointsToUse = ml_handleJoints
    ml_fkJointsToUse = ml_fkJoints
    
    #...lever -------------------------------------------------------------------------------------------------
    if self.b_lever:
        if self.b_leverJoint:
            log.debug("|{0}| >> Lever handle joint remap...".format(_str_func))  
            
            ml_fkJointsToUse = ml_fkJoints[1:]
            ml_fkJoints[1].parent = False
            ml_rigJoints[1].parent = False
        
            mRigNull.connectChildNode(ml_rigJoints[0],'leverDirect','rigNull')
            mRigNull.connectChildNode(ml_fkJoints[0],'leverFK','rigNull')
            ml_rigJoints[0].p_parent = ml_fkJoints[0]
            
            mRigNull.msgList_connect('fkJoints', ml_fkJointsToUse,'rigNull')#connect	        
            ml_parentJoints = ml_fkJointsToUse
            
        else:
            log.debug("|{0}| >> Creating lever joint for rig setup...".format(_str_func))  
            #Lever...
            mLever = ml_fkJoints[0].doDuplicate(po=True)
            mLever.cgmName = '{0}_lever'.format(mBlock.cgmName)
            mLever.p_parent = False
            mLever.doName()
            
            ml_jointHelpers = mBlock.msgList_get('jointHelpers',asMeta = True)
            if not ml_jointHelpers:
                raise ValueError,"No jointHelpers connected"            
            
            mLever.p_position = ml_jointHelpers[0].p_position
            
            SNAP.aim(mLever.mNode, ml_fkJoints[0].mNode, 'z+','y+','vector',
                     mBlock.rootUpHelper.getAxisVector('y+'))
            reload(JOINT)
            JOINT.freezeOrientation(mLever.mNode)
            mRigNull.connectChildNode(mLever,'leverFK','rigNull')
        
    
    #...fk chain -----------------------------------------------------------------------------------------------
    if mBlock.ikSetup:
        log.info("|{0}| >> ikSetup on. Building blend and IK chains...".format(_str_func))  
        ml_blendJoints = BLOCKUTILS.skeleton_buildHandleChain(self.mBlock,'blend','blendJoints')
        ml_ikJoints = BLOCKUTILS.skeleton_buildHandleChain(self.mBlock,'ik','ikJoints')
        
        for i,mJnt in enumerate(ml_ikJoints):
            if mJnt not in [ml_ikJoints[0],ml_ikJoints[-1]]:
                mJnt.preferredAngle = mJnt.jointOrient
        
        """
        ml_blendJoints = BLOCKUTILS.skeleton_buildDuplicateChain(mBlock,
                                                                 ml_fkJointsToUse, None, 
                                                                 mRigNull,
                                                                 'blendJoints',
                                                                 connectToSource = 'blendJoint',
                                                                 cgmType = 'handle')
        ml_ikJoints = BLOCKUTILS.skeleton_buildDuplicateChain(mBlock,
                                                              ml_fkJointsToUse, None, 
                                                              mRigNull,
                                                              'ikJoints',
                                                              connectToSource = 'ikJoint',
                                                              cgmType = 'handle')"""
     
        ml_jointsToConnect.extend(ml_ikJoints)
        ml_jointsToHide.extend(ml_blendJoints)
        ml_parentJoints = ml_blendJoints
        
        BLOCKUTILS.skeleton_pushSettings(ml_ikJoints,self.d_orientation['str'],
                                         self.d_module['mirrorDirection'],
                                         d_rotateOrders, d_preferredAngles)        
        
    #cgmGEN.func_snapShot(vars())        
    """
    if mBlock.numControls > 1:
        log.info("|{0}| >> Handles...".format(_str_func))            
        ml_segmentHandles = BLOCKUTILS.skeleton_buildHandleChain(self.mBlock,'handle','handleJoints',clearType=True)
        if mBlock.ikSetup:
            for i,mJnt in enumerate(ml_segmentHandles):
                mJnt.parent = ml_blendJoints[i]
        else:
            for i,mJnt in enumerate(ml_segmentHandles):
                mJnt.parent = ml_fkJoints[i]
                """
    """
    if mBlock.ikSetup in [2,3]:#...ribbon/spline
        log.info("|{0}| >> IK Drivers...".format(_str_func))            
        ml_ribbonIKDrivers = BLOCKUTILS.skeleton_buildDuplicateChain(mBlock,ml_ikJoints, None, mRigNull,'ribbonIKDrivers', cgmType = 'ribbonIKDriver', indices=[0,-1])
        for i,mJnt in enumerate(ml_ribbonIKDrivers):
            mJnt.parent = False
            
            mTar = ml_blendJoints[0]
            if i == 0:
                mTar = ml_blendJoints[0]
            else:
                mTar = ml_blendJoints[-1]
                
            mJnt.doCopyNameTagsFromObject(mTar.mNode,ignore=['cgmType'])
            mJnt.doName()
        
        ml_jointsToConnect.extend(ml_ribbonIKDrivers)"""
        
    
    #Segment/Parenting -----------------------------------------------------------------------------
    self.md_roll
    self.md_rollMulti
    ml_processed = []
    self.md_segHandleIndices
    self.ml_segHandles
    
    md_rigTargets = {}
    self.md_segHandles = {}
    ml_handles = []
    if self.md_roll:#Segment stuff ===================================================================
        log.debug("|{0}| >> Segment...".format(_str_func))
        
        log.debug("|{0}| >> Handle Joints...".format(_str_func))
        log.debug("|{0}| >> Targets: {1} | {2} ".format(_str_func, self.int_handleEndIdx, ml_parentJoints))
        
        ml_handleJoints = BLOCKUTILS.skeleton_buildDuplicateChain(mBlock,
                                                                  self.ml_handleTargetsCulled,#ml_parentJoints,#ml_parentJoints[:self.int_handleEndIdx+1],
                                                                  None, 
                                                                  mRigNull,
                                                                  'handleJoints',
                                                                  connectToSource = 'handleJoint',
                                                                  cgmType = 'handle')
        for i,mJnt in enumerate(ml_handleJoints):
            #if mJnt.hasAttr('cgmTypeModifier'):
                #ATTR.delete(mJnt.mNode,'cgmTypeModifier')
            mJnt.doStore('cgmTypeModifier','seg')
            mJnt.doName()
            mJnt.parent = ml_parentJoints[i]
            
        
        for i,ml_set in self.md_roll.iteritems():
            log.debug("|{0}| >> Segment Handles {1} ...".format(_str_func, i))#----------------------------
        
            ml_segmentHandles = BLOCKUTILS.skeleton_buildDuplicateChain(mBlock,
                                                                        [ml_set[0],ml_set[-1]], None, 
                                                                        mRigNull,
                                                                        'segmentHandles_{0}'.format(i),
                                                                        connectToSource = 'segHandle_{0}_'.format(i),
                                                                        cgmType = 'segHandle')
            ml_jointsToConnect.extend(ml_segmentHandles)
            
            self.md_segHandles[i] = ml_segmentHandles
            
            for mJnt in ml_segmentHandles:
                mJnt.doStore('cgmTypeModifier',"seg_{0}".format(i))
                mJnt.doName()
                
            if mBlock.ikSetup:
                for ii,mJnt in enumerate(ml_segmentHandles):
                    mJnt.parent = ml_blendJoints[ self.md_segHandleIndices[self.ml_segHandles[ii]]]
            else:
                for ii,mJnt in enumerate(ml_segmentHandles):
                    mJnt.parent = ml_fkJointsToUse[ self.md_segHandleIndices[self.ml_segHandles[ii]]]
                    
            
            #Seg chain -------------------------------------------------------------------------------------
            log.debug("|{0}| >> SegChain {1} ...".format(_str_func, i))
            ml_segmentChain = BLOCKUTILS.skeleton_buildDuplicateChain(mBlock,
                                                                      ml_set, None, 
                                                                      mRigNull,'segJoints_{0}'.format(i),
                                                                      connectToSource = 'seg_{0}_'.format(i),
                                                                      cgmType = 'segJnt')
            
            for mJnt in ml_segmentChain:
                mJnt.doStore('cgmTypeModifier',"seg_{0}".format(i))
                mJnt.doName()
                
            #ml_jointsToConnect.extend(ml_segmentChain)
            
            log.debug("|{0}| >> map drivers {1} ...".format(_str_func, i))            
            for ii,mJnt in enumerate(ml_set):
                mRigJoint = mJnt.getMessage('rigJoint',asMeta=True)[0]
                
                log.debug("|{0}| >> mJnt: {1} | rigJoint: {2} | segJoint: {3}".format(_str_func,
                                                                                      mJnt.p_nameShort,
                                                                                      mRigJoint.p_nameShort,
                                                                                      ml_segmentChain[ii].p_nameShort))

                
                mRigJoint.msgList_append('driverJoints',ml_segmentChain[ii].mNode, connectBack = 'drivenJoint')

            
            
            for ii,mJnt in enumerate(ml_segmentChain):
                if ii == 0:
                    continue
                mJnt.parent = ml_segmentChain[ii-1]
        
            ml_segmentChain[0].parent = ml_parentJoints[i]
                
    
    """
    if self.b_segmentSetup:
        log.info("|{0}| >> segment necessary...".format(_str_func))
            
        ml_segmentChain = BLOCKUTILS.skeleton_buildDuplicateChain(mBlock,
                                                                  ml_joints, None, 
                                                                  mRigNull,'segmentJoints',
                                                                  connectToSource = 'seg',
                                                                  cgmType = 'segJnt')
        for i,mJnt in enumerate(ml_rigJoints):
            mJnt.parent = ml_segmentChain[i]
            mJnt.connectChildNode(ml_segmentChain[i],'driverJoint','sourceJoint')#Connect
            
        ml_jointsToHide.extend(ml_segmentChain)
        
    else:
        log.info("|{0}| >> rollSetup joints...".format(_str_func))
        
         
        for i,mBlend in enumerate(ml_blendJoints):
            ml_rolls = self.md_roll.get(i)
            
            if ml_rolls:
                ml_segmentChain = BLOCKUTILS.skeleton_buildDuplicateChain(mBlock,
                                                                          ml_rolls,
                                                                          None, 
                                                                          False,
                                                                          connectToSource = 'seg',
                                                                          cgmType = 'segJnt')
            
                ml_jointsToHide.extend(ml_segmentChain)
                ml_segmentChain[0].p_parent = mBlend"""
        
    
    #Parenting rigJoints ======================================================================
    log.debug("|{0}| >> Connecting rigJoints to drivers...".format(_str_func))
    ml_rigParents = ml_fkJoints
    if ml_blendJoints:
        ml_rigParents = ml_blendJoints
    
    for i,mJnt in enumerate(ml_rigJoints):
        log.debug("|{0}| >> RigJoint: {1} ...".format(_str_func,mJnt))
        ml_drivers = mJnt.msgList_get('driverJoints')
        
        _l = False
        _done = False
        if ml_drivers:
            log.debug("|{0}| >> ... Found special drivers: {1}".format(_str_func,ml_drivers))
            #if len(ml_drivers) == 1:
            
            if ml_joints[i] == self.mIKEndSkinJnt:#last joint
                log.debug("|{0}| >> End joint: {1} ".format(_str_func,mJnt))
                mJnt.p_parent = ml_blendJoints[self.int_handleEndIdx]
            else:
                mJnt.p_parent = ml_drivers[-1]
            _done = True
            #else:
                #_l = [mObj.mNode for mObj in ml_drivers]

        if not _done:
            for mParent in ml_rigParents:
                if MATH.is_vector_equivalent(mParent.p_position,mJnt.p_position):
                    log.debug("|{0}| >> ... Position match: {1}".format(_str_func,mParent))
                    mJnt.parent = mParent
                    
                    #if _l:
                        #mc.pointConstraint(_l, mJnt.mNode, maintainOffset =False)
                        #mc.orientConstraint(_l, mJnt.mNode, maintainOffset = False)
                        #mc.scaleConstraint(_l, mJnt.mNode, maintainOffset = False)
                        
                    continue

    
    if self.b_pivotSetup:
        log.info("|{0}| >> Pivot joints...".format(_str_func))        
        if self.mBall:
            log.info("|{0}| >> Ball joints...".format(_str_func))
            
            mBallJointPivot = self.mBall.doCreateAt('joint',copyAttrs=True)#dup ball in place
            mBallJointPivot.parent = False
            mBallJointPivot.cgmName = 'ball'
            mBallJointPivot.addAttr('cgmType','pivotJoint')
            mBallJointPivot.doName()
            mRigNull.connectChildNode(mBallJointPivot,"pivot_ballJoint","rigNull")
    
            #Ball wiggle pivot
            mBallWiggleJointPivot = mBallJointPivot.doDuplicate(po = True)#dup ball in place
            mBallWiggleJointPivot.parent = False
            mBallWiggleJointPivot.cgmName = 'ballWiggle'
            mBallWiggleJointPivot.addAttr('cgmType','pivotJoint')            
            mBallWiggleJointPivot.doName()
            mRigNull.connectChildNode(mBallWiggleJointPivot,"pivot_ballWiggle","rigNull") 
            
            if not self.mToe:
                log.info("|{0}| >> Making toe joint...".format(_str_func))
                raise NotImplementedError,"Haven't done make toe joint yet"
                """
                i_toeJoint = ml_ikJoints[-1].doDuplicate()
                log.info("i_toeJoint: {0}".format(i_toeJoint))
                log.info("mi_toePivot: {0}".format(mi_toePivot))                
                SNAP.go(i_toeJoint, mi_toePivot.mNode,True,False)
                joints.doCopyJointOrient(ml_ikJoints[-1].mNode,i_toeJoint.mNode)
                i_toeJoint.addAttr('cgmName','toe',attrType='string',lock=True)	
                i_toeJoint.addAttr('cgmTypeModifier','ik',attrType='string',lock=True)
                i_toeJoint.doName()
            
                i_toeJoint.parent = ml_ikJoints[-1].mNode
                ml_ikJoints.append(i_toeJoint)
                self._i_rigNull.msgList_append('ikJoints',i_toeJoint,'rigNull')            
                """
    
        
    #...joint hide -----------------------------------------------------------------------------------
    for mJnt in ml_jointsToHide:
        try:
            mJnt.drawStyle =2
        except:
            mJnt.radius = .00001
            
    #...connect... 
    self.fnc_connect_toRigGutsVis( ml_jointsToConnect )        
    
    cgmGEN.func_snapShot(vars())     
    return

@cgmGEN.Timer
def rig_digitShapes(self):
    try:
        _short = self.d_block['shortName']
        _str_func = 'rig_shapes'
        log.debug("|{0}| >>  {1}".format(_str_func,self)+ '-'*80)
        
        #_str_func = '[{0}] > rig_shapes'.format(_short)
        log.info("|{0}| >> ...".format(_str_func))  
        
        mBlock = self.mBlock
        
        str_rigSetup = ATTR.get_enumValueString(mBlock.mNode,'rigSetup')
        
        
        mRigNull = self.mRigNull
        
        ml_templateHandles = mBlock.msgList_get('templateHandles')
        ml_prerigHandleTargets = self.mBlock.atBlockUtils('prerig_getHandleTargets')
        ml_fkJoints = self.mRigNull.msgList_get('fkJoints')
        ml_ikJoints = mRigNull.msgList_get('ikJoints',asMeta=True)
        ml_blendJoints = self.mRigNull.msgList_get('blendJoints')
        
        mIKEnd = ml_prerigHandleTargets[-1]
        ml_prerigHandles = mBlock.msgList_get('prerigHandles')
        
        _side = mBlock.atUtils('get_side')
        _short_module = self.mModule.mNode
        str_ikBase = ATTR.get_enumValueString(mBlock.mNode,'ikBase')
        str_ikEnd = ATTR.get_enumValueString(mBlock.mNode,'ikEnd')        
        str_rigSetup = ATTR.get_enumValueString(mBlock.mNode,'rigSetup')
        
        mHandleFactory = mBlock.asHandleFactory()
        mOrientHelper = mBlock.orientHelper
        
        #_size = 5
        #_size = MATH.average(mHandleFactory.get_axisBox_size(ml_prerigHandles[0].mNode))
        _jointOrientation = self.d_orientation['str']
        
        ml_joints = self.d_joints['ml_moduleJoints']
        
        #Our base size will be the average of the bounding box sans the largest
        #_bbSize = TRANS.bbSize_get(mBlock.getMessage('prerigLoftMesh')[0],shapes=True)
        #_bbSize.remove(max(_bbSize))
        #_size = MATH.average(_bbSize)
        
        _bbSize = TRANS.bbSize_get(self.mRootTemplateHandle.mNode,shapes=True)
        _size = MATH.average(_bbSize[1:])
        
        
        _offset = self.v_offset
        
        
        d_directions = {'up':'y+','down':'y-','in':'x+','out':'x-'}
        str_settingsDirections = d_directions.get(mBlock.getEnumValueString('settingsDirection'),'y+')        

        #Pivots ==================================================================================
        mPivotHolderHandle = ml_templateHandles[-1]
        mPivotHelper = False
        if mPivotHolderHandle.getMessage('pivotHelper'):
            mPivotHelper = mPivotHolderHandle.pivotHelper
            log.debug("|{0}| >> Pivot shapes...".format(_str_func))            
            mBlock.atBlockUtils('pivots_buildShapes', mPivotHolderHandle.pivotHelper, mRigNull)

        #IK End ================================================================================
        if mBlock.ikSetup:
            log.debug("|{0}| >> ikHandle...".format(_str_func))
            """
            if mPivotHelper:
                mIKCrv = mPivotHelper.doDuplicate(po=False)
                mIKCrv.parent = False
                mShape2 = False
                for mChild in mIKCrv.getChildren(asMeta=True):
                    if mChild.cgmName == 'topLoft':
                        mShape2 = mChild.doDuplicate(po=False)
                        DIST.offsetShape_byVector(mShape2.mNode,_offset,component='cv')
    
                    mChild.delete()
    
                DIST.offsetShape_byVector(mIKCrv.mNode,_offset,component='cv')
    
                if mShape2:
                    CORERIG.shapeParent_in_place(mIKCrv.mNode, mShape2.mNode, False)
    
    
                TRANS.rotatePivot_set(mIKCrv.mNode,
                                      ml_fkJoints[self.int_handleEndIdx].p_position )"""
                
            if ml_templateHandles[-1].getMessage('proxyHelper'):
                log.debug("|{0}| >> proxyHelper IK shape...".format(_str_func))
                mProxyHelper = ml_templateHandles[-1].getMessage('proxyHelper',asMeta=True)[0]
                bb_ik = mHandleFactory.get_axisBox_size(mProxyHelper.mNode)
    
                _ik_shape = CURVES.create_fromName('cube', size = bb_ik)
                ATTR.set(_ik_shape,'scale', 1.5)
                mIKShape = cgmMeta.validateObjArg(_ik_shape, 'cgmObject',setClass=True)
                #DIST.offsetShape_byVector(_ik_shape,_offset, mIKCrv.p_position,component='cv')
    
                mIKShape.doSnapTo(mProxyHelper)
                pos_ik = POS.get_bb_center(mProxyHelper.mNode)
                #SNAPCALLS.get_special_pos(mEndHandle.p_nameLong,
                #                                   'axisBox','z+',False)                
    
                mIKShape.p_position = pos_ik
                mIKCrv = self.ml_handleTargets[self.int_handleEndIdx].doCreateAt()
    
                CORERIG.shapeParent_in_place(mIKCrv.mNode, mIKShape.mNode, False)
    
                #CORERIG.match_transform(mIKShape.mNode, self.ml_handleTargets[self.int_handleEndIdx].mNode)
    
            else:
                log.debug("|{0}| >> default IK shape...".format(_str_func))
                """
                mIKTemplateHandle = ml_templateHandles[-1]
                bb_ik = mHandleFactory.get_axisBox_size(mIKTemplateHandle.mNode)
                _ik_shape = CURVES.create_fromName('cube', size = bb_ik)
                ATTR.set(_ik_shape,'scale', 1.5)
    
                mIKCrv = cgmMeta.validateObjArg(_ik_shape, 'cgmObject',setClass=True)
                mIKCrv.doSnapTo(self.ml_handleTargets[self.int_handleEndIdx].mNode)
                """
                ml_curves = []
                
                if str_ikEnd == 'tipBase':
                    mIKCrv = self.ml_handleTargets[self.int_handleEndIdx].doCreateAt()
                else:
                    mIKCrv = self.ml_handleTargets[-1].doCreateAt()
                    if self.b_ikNeedEnd:
                        SNAP.go(mIKCrv.mNode,
                                ml_prerigHandles[-1].jointHelper,
                                rotation = False)

                for mObj in ml_templateHandles[-2:]:
                    mCrv = mObj.loftCurve.doDuplicate(po=False,ic=False)
                    DIST.offsetShape_byVector(mCrv.mNode,_offset, mCrv.p_position,component='cv')
                    mCrv.p_parent=False
                    for mShape in mCrv.getShapes(asMeta=True):
                        mShape.overrideDisplayType = False
                    CORERIG.shapeParent_in_place(mIKCrv.mNode, mCrv.mNode, True)
                    ml_curves.append(mCrv)
                    
                #mCrv = ml_templateHandles[-1].loftCurve.doDuplicate(po=False,ic=False)
                #DIST.offsetShape_byVector(mCrv.mNode,_offset, mCrv.p_position,component='cv')
                #mCrv.p_parent=False
                #for mShape in mCrv.getShapes(asMeta=True):
                #    mShape.overrideDisplayType = False
                    
                """
                d_endPos = {}
                _str_endHandle = ml_templateHandles[-1].mNode
                _str_loftCurve = mCrv.mNode
                
                pos_handle = ml_templateHandles[-1].p_position
                vec_handle = MATH.get_obj_vector(_str_endHandle,'z+')
                
                for k in ['x+','x-','y+','y-','z+']:
                    pos = SNAPCALLS.get_special_pos(_str_endHandle,
                                                    'axisBox',k)
                    if k == 'z+':
                        d_endPos[k] = DIST.get_pos_by_vec_dist(pos,
                                                               vec_handle,
                                                               _offset)                        
                    else:
                        p_close = DIST.get_closest_point(pos, _str_loftCurve)[0]
                        d_endPos[k] = p_close
                
                l_crvs = []
                for k in ['x','y']:
                    p1 = d_endPos['{0}+'.format(k)]
                    p2 = d_endPos['z+']
                    pos_average = DIST.get_average_position([p1,p2])
                    vec_start = MATH.get_vector_of_two_points(pos_handle,pos_average)
                    dist_start = DIST.get_distance_between_points(pos_handle,pos_average)
                    mid_start = DIST.get_pos_by_vec_dist(pos_handle,
                                                         vec_start,
                                                         dist_start * 1.5)
                    
                    
                    p1 = d_endPos['{0}-'.format(k)]
                    pos_average = DIST.get_average_position([p1,p2])
                    vec_start = MATH.get_vector_of_two_points(pos_handle,pos_average)
                    dist_start = DIST.get_distance_between_points(pos_handle,pos_average)
                    mid_end = DIST.get_pos_by_vec_dist(pos_handle,
                                                       vec_start,
                                                       dist_start * 1.5)                    
                
                    crv = CURVES.create_fromList(posList = [d_endPos['{0}+'.format(k)],
                                                            mid_start,
                                                            d_endPos['z+'],
                                                            mid_end,
                                                            d_endPos['{0}-'.format(k)],]
                                                            )
                    l_crvs.append(crv)
                    CORERIG.shapeParent_in_place(mIKCrv.mNode, crv, False)"""
                    

                #pprint.pprint(d_endPos)
                for mCrv in ml_curves:
                    mCrv.delete()                
                    
                #CORERIG.shapeParent_in_place(mIKCrv.mNode, mCrv.mNode, False)
                
                
            
            mHandleFactory.color(mIKCrv.mNode, controlType = 'main',transparent=True)
            mIKCrv.doCopyNameTagsFromObject(ml_fkJoints[self.int_handleEndIdx].mNode,
                                            ignore=['cgmType','cgmTypeModifier'])
            mIKCrv.doStore('cgmTypeModifier','ik')
            mIKCrv.doStore('cgmType','handle')
            mIKCrv.doName()
            
            
            #mc.makeIdentity(mIKCrv.mNode, apply = True, t=0, r=0,s=1,n=0,pn=1)
            
            mHandleFactory.color(mIKCrv.mNode, controlType = 'main')        
            self.mRigNull.connectChildNode(mIKCrv,'controlIK','rigNull')#Connect            
    
    
            #Mid IK...----------------------------------------------------------------------------
            log.debug("|{0}| >> midIK...".format(_str_func))
            mKnee = ml_fkJoints[self.int_templateHandleMidIdx].doCreateAt(setClass=True)
            #size_knee =  POS.get_bb_size(ml_templateHandles[self.int_templateHandleMidIdx].mNode)
            
            crv = CURVES.create_controlCurve(mKnee, shape='sphere',
                                             direction = _jointOrientation[0]+'+',
                                             sizeMode = 'fixed',
                                             size = _size/2)            
            
            
            CORERIG.shapeParent_in_place(mKnee.mNode, crv, False)
            
            mKnee.doSnapTo(ml_ikJoints[1].mNode)
    
            #Get our point for knee...
            mKnee.p_position = self.atBuilderUtils('get_midIK_basePosOrient',
                                                   self.ml_handleTargetsCulled,False)
    
            
            CORERIG.match_orientation(mKnee.mNode, mIKCrv.mNode)
            #mc.makeIdentity(mKnee.mNode, apply = True, t=0, r=0,s=1,n=0,pn=1)
            mHandleFactory.color(mKnee.mNode, controlType = 'sub')
    
            mKnee.doCopyNameTagsFromObject(ml_fkJoints[1].mNode,ignore=['cgmType','cgmTypeModifier'])
            mKnee.doStore('cgmAlias','midIK')            
            mKnee.doName()
    
            self.mRigNull.connectChildNode(mKnee,'controlIKMid','rigNull')#Connect
        
        #Cog =============================================================================
        if mBlock.getMessage('cogHelper') and mBlock.getMayaAttr('addCog'):
            log.debug("|{0}| >> Cog...".format(_str_func))
            mCogHelper = mBlock.cogHelper
    
            mCog = mCogHelper.doCreateAt(setClass=True)
            CORERIG.shapeParent_in_place(mCog.mNode, mCogHelper.shapeHelper.mNode)
    
            mCog.doStore('cgmName','cog')
            mCog.doStore('cgmAlias','cog')            
            mCog.doName()
    
            self.mRigNull.connectChildNode(mCog,'rigRoot','rigNull')#Connect
            self.mRigNull.connectChildNode(mCog,'settings','rigNull')#Connect        
    
    
        else:#Root =============================================================================
            log.debug("|{0}| >> Root...".format(_str_func))
    
            #if self.b_lever:
            #    mRootHandle = ml_prerigHandles[1]
            #else:
            mRootHandle = ml_prerigHandles[0]
                
            #mRoot = ml_joints[0].doCreateAt()
    
            mRoot = ml_joints[0].doCreateAt()
    
            _size_root =  MATH.average(POS.get_bb_size(self.mRootTemplateHandle.mNode)) * .75
            mRootCrv = cgmMeta.validateObjArg(CURVES.create_fromName('locatorForm', _size_root),'cgmObject',setClass=True)
            mRootCrv.doSnapTo(mRootHandle)
    
            #SNAP.go(mRootCrv.mNode, ml_joints[0].mNode,position=False)
    
            CORERIG.shapeParent_in_place(mRoot.mNode,mRootCrv.mNode, False)
            
            for a in 'cgmName','cgmDirection','cgmModifier':
                if ATTR.get(_short_module,a):
                    ATTR.copy_to(_short_module,a,mRoot.mNode,driven='target')
            mRoot.doStore('cgmTypeModifier','root')
            mRoot.doName()
    
            mHandleFactory.color(mRoot.mNode, controlType = 'sub')
    
            self.mRigNull.connectChildNode(mRoot,'rigRoot','rigNull')#Connect
        
        #Lever =============================================================================
        if self.b_lever:            
            log.debug("|{0}| >> Lever...".format(_str_func))
            
            mLeverRigJnt = mRigNull.getMessage('leverDirect',asMeta=True)
            if mLeverRigJnt:
                mLeverRigJnt = mLeverRigJnt[0]
            mLeverFKJnt = mRigNull.getMessage('leverFK',asMeta=True)[0]
            log.debug("|{0}| >> mLeverRigJnt: {1}".format(_str_func,mLeverRigJnt))            
            log.debug("|{0}| >> mLeverFKJnt: {1}".format(_str_func,mLeverFKJnt))            
    
            dist_lever = DIST.get_distance_between_points(ml_prerigHandles[0].p_position,
                                                          ml_prerigHandles[1].p_position)
            log.debug("|{0}| >> Lever dist: {1}".format(_str_func,dist_lever))
    
            #Dup our rig joint and move it 
            mDup = mLeverFKJnt.doDuplicate(po=True)
            mDup.p_parent = mLeverFKJnt
            mDup.resetAttrs()
            ATTR.set(mDup.mNode, 't{0}'.format(_jointOrientation[0]), dist_lever * .5)
    
            l_lolis = []
            l_starts = []
            
            size_loli = _size * .3
            offset_loli = _bbSize[1] + (_offset * 2)
            _mTar = mDup
            for axis in [str_settingsDirections]:
                pos = _mTar.getPositionByAxisDistance(axis, offset_loli)
                ball = CURVES.create_fromName('sphere',size_loli)
                mBall = cgmMeta.cgmObject(ball)
                mBall.p_position = pos
                
                SNAP.aim_atPoint(mBall.mNode,
                                 _mTar.p_position,
                                 aimAxis=_jointOrientation[0]+'+',
                                 mode = 'vector',
                                 vectorUp= _mTar.getAxisVector(_jointOrientation[0]+'-'))                
                
                mc.select(cl=True)
                p_end = DIST.get_closest_point(mDup.mNode, ball)[0]
                p_start = mDup.getPositionByAxisDistance(axis, offset_loli * .25)
                l_starts.append(p_start)
                line = mc.curve (d=1, ep = [p_start,p_end], os=True)
                l_lolis.extend([ball,line])
        
            CORERIG.shapeParent_in_place(mLeverFKJnt.mNode,l_lolis,False)
            mHandleFactory.color(mLeverFKJnt.mNode, controlType = 'main')
            mDup.delete()
            
            #limbRoot ------------------------------------------------------------------------------
            log.debug("|{0}| >> Lever -- limbRoot".format(_str_func))
            mLimbRootHandle = ml_prerigHandles[1]
            mLimbRoot = ml_fkJoints[0].doCreateAt()
        
            _size_root =  MATH.average(POS.get_bb_size(self.mRootTemplateHandle.mNode)) * .75
            mRootCrv = cgmMeta.validateObjArg(CURVES.create_fromName('locatorForm', _size_root),'cgmObject',setClass=True)
            mRootCrv.doSnapTo(mLimbRootHandle)
        
            #SNAP.go(mRootCrv.mNode, ml_joints[0].mNode,position=False)
        
            CORERIG.shapeParent_in_place(mLimbRoot.mNode,mRootCrv.mNode, False)
        
            for a in 'cgmName','cgmDirection','cgmModifier':
                if ATTR.get(_short_module,a):
                    ATTR.copy_to(_short_module,a,mLimbRoot.mNode,driven='target')
                    
            mLimbRoot.doStore('cgmTypeModifier','limbRoot')
            mLimbRoot.doName()
        
            mHandleFactory.color(mLimbRoot.mNode, controlType = 'sub')
        
            self.mRigNull.connectChildNode(mLimbRoot,'limbRoot','rigNull')#Connect
        
        #Settings =============================================================================
        if ml_blendJoints:
            ml_targets = ml_blendJoints
        else:
            ml_targets = ml_fkJoints
            
        #if self.b_lever:
            """
            log.debug("|{0}| >> Lever...".format(_str_func))
            mLeverRigJnt = mRigNull.getMessage('leverDirect',asMeta=True)[0]
            mLeverFKJnt = mRigNull.getMessage('leverFK',asMeta=True)[0]
            log.debug("|{0}| >> mLeverRigJnt: {1}".format(_str_func,mLeverRigJnt))            
            log.debug("|{0}| >> mLeverFKJnt: {1}".format(_str_func,mLeverFKJnt))            
        

            _mTar = ml_targets[0]
            _settingsSize = MATH.average(TRANS.bbSize_get(ml_templateHandles[1].mNode,shapes=True))
            
            mSettingsShape = cgmMeta.validateObjArg(CURVES.create_fromName('gear',_settingsSize * .5,
                                                                           '{0}+'.format(_jointOrientation[2])),'cgmObject',setClass=True)
            
            mSettingsShape.doSnapTo(_mTar.mNode)
            d_directions = {'up':'y+','down':'y-','in':'x+','out':'x-'}
            str_settingsDirections = d_directions.get(mBlock.getEnumValueString('settingsDirection'),'y+')
            mSettingsShape.p_position = _mTar.getPositionByAxisDistance(str_settingsDirections,
                                                                        _settingsSize)
        
            SNAP.aim_atPoint(mSettingsShape.mNode,
                             _mTar.p_position,
                             aimAxis=_jointOrientation[0]+'+',
                             mode = 'vector',
                             vectorUp= _mTar.getAxisVector(_jointOrientation[0]+'-'))
        
            #mSettings = _mTar.doCreateAt(setClass=True)
        
            #mSettingsShape.parent = _mTar
            mSettings = mSettingsShape
            #CORERIG.match_orientation(mSettings.mNode, ml_targets[0].mNode)
            #CORERIG.shapeParent_in_place(mSettings.mNode,mSettingsShape.mNode,False)            
        
            #ATTR.copy_to(_short_module,'cgmName',mSettings.mNode,driven='target')
        
            #mSettings.doStore('cgmTypeModifier','settings')
            #mSettings.doName()
            #CORERIG.colorControl(mSettings.mNode,_side,'sub')
            
            CORERIG.shapeParent_in_place(mLeverFKJnt.mNode,mSettings.mNode, False, replaceShapes=True)
            mHandleFactory.color(mLeverFKJnt.mNode, controlType = 'sub')"""
            
            
        _settingsPlace = mBlock.getEnumValueString('settingsPlace')
        
        if _settingsPlace == 'cog':
            log.warning("|{0}| >> Settings. Cog option but no cog found...".format(_str_func))
            _settingsPlace = 'start'

        else:
            log.debug("|{0}| >> settings: {1}...".format(_str_func,_settingsPlace))

            if _settingsPlace == 'start':
                _mTar = ml_targets[0]
                bbSize_handle = TRANS.bbSize_get(self.mRootTemplateHandle.mNode,shapes=True)
            else:
                _mTar = ml_targets[self.int_handleEndIdx]
                bbSize_handle = TRANS.bbSize_get(ml_templateHandles[-1].mNode,shapes=True)
            
            _settingsSize = MATH.average(bbSize_handle[1:])
            mSettingsShape = cgmMeta.validateObjArg(CURVES.create_fromName('gear',_settingsSize * .5,
                                                                           '{0}+'.format(_jointOrientation[2])),'cgmObject',setClass=True)

            mSettingsShape.doSnapTo(_mTar.mNode)
            mSettingsShape.p_position = _mTar.getPositionByAxisDistance(str_settingsDirections,
                                                                        _settingsSize)

            SNAP.aim_atPoint(mSettingsShape.mNode,
                             _mTar.p_position,
                             aimAxis=_jointOrientation[0]+'+',
                             mode = 'vector',
                             vectorUp= _mTar.getAxisVector(_jointOrientation[0]+'-'))

            #mSettings = _mTar.doCreateAt(setClass=True)
            mSettingsShape.parent = _mTar
            mSettings = mSettingsShape
            CORERIG.match_orientation(mSettings.mNode, _mTar.mNode)
            #CORERIG.shapeParent_in_place(mSettings.mNode,mSettingsShape.mNode,False)            

            ATTR.copy_to(_short_module,'cgmName',mSettings.mNode,driven='target')

            mSettings.doStore('cgmTypeModifier','settings')
            mSettings.doName()
            #CORERIG.colorControl(mSettings.mNode,_side,'sub')                
            mHandleFactory.color(mSettings.mNode, controlType = 'sub')

        self.mRigNull.connectChildNode(mSettings,'settings','rigNull')#Connect
        
        
        #FK/Ik ==========================================================================================    
        log.debug("|{0}| >> Frame shape cast...".format(_str_func))
        ml_targets = [mObj.mNode for mObj in self.ml_handleTargets]
        if mBlock.hasEndJoint:
            ml_targets.pop(-1)
            
        ml_fkShapes = self.atBuilderUtils('shapes_fromCast',
                                          offset = _offset,
                                          targets = ml_targets,
                                          mode = 'simpleCast')
        """
        if self.mPivotHelper:
            size_pivotHelper = POS.get_bb_size(self.mPivotHelper.mNode)
        else:
            size_pivotHelper = POS.get_bb_size(ml_templateHandles[-1].mNode)
    
        
        if self.mBall:
            #_size_ball = DIST.get_distance_between_targets([self.mBall.mNode,
                        #self.mBall.p_parent])
            crv = CURVES.create_controlCurve(self.mBall.mNode, shape='circle',
                                             direction = _jointOrientation[0]+'+',
                                             sizeMode = 'fixed',
                                             size = size_pivotHelper[0])
            ml_fkShapes.append(cgmMeta.validateObjArg(crv,'cgmObject'))
    
        if self.mToe:
            #_size_ball = DIST.get_distance_between_targets([self.mToe.mNode,
            #                                                self.mToe.p_parent])
    
            crv = CURVES.create_controlCurve(self.mToe.mNode, shape='circle',
                                             direction = _jointOrientation[0]+'+',
                                             sizeMode = 'fixed',
                                             size = size_pivotHelper[0])        
            ml_fkShapes.append(cgmMeta.validateObjArg(crv,'cgmObject'))"""
    
    
        log.debug("|{0}| >> FK...".format(_str_func))    
        for i,mCrv in enumerate(ml_fkShapes):
            mJnt = ml_fkJoints[i]    
            mHandleFactory.color(mCrv.mNode, controlType = 'main')
            CORERIG.shapeParent_in_place(mJnt.mNode,mCrv.mNode, False, replaceShapes=True)

        #Direct Controls =============================================================================
        log.debug("|{0}| >> direct...".format(_str_func))                
        ml_rigJoints = self.mRigNull.msgList_get('rigJoints')
        #_size_direct = DIST.get_distance_between_targets([mObj.mNode for mObj in ml_rigJoints], average=True)        

        d_direct = {'size':_size/4}
            
        ml_directShapes = self.atBuilderUtils('shapes_fromCast',
                                              ml_rigJoints,
                                              mode ='direct',**d_direct)
                                                                                                                                                                #offset = 3
    
        for i,mCrv in enumerate(ml_directShapes):
            mHandleFactory.color(mCrv.mNode, controlType = 'sub')
            CORERIG.shapeParent_in_place(ml_rigJoints[i].mNode,mCrv.mNode, False, replaceShapes=True)
    
        for mJnt in ml_rigJoints:
            try:
                mJnt.drawStyle =2
            except:
                mJnt.radius = .00001

        
        #Handles =============================================================================================    
        ml_handleJoints = self.mRigNull.msgList_get('handleJoints')
        if ml_handleJoints:
            log.debug("|{0}| >> Found Handle joints...".format(_str_func))
            
            ml_handleShapes = self.atBuilderUtils('shapes_fromCast',
                                                  targets = [mObj.mNode for mObj in ml_handleJoints],
                                                  mode = 'limbSegmentHandle')
            
            for i,mCrv in enumerate(ml_handleShapes):
                log.debug("|{0}| >> Shape: {1} | Handle: {2}".format(_str_func,mCrv.mNode,ml_handleJoints[i].mNode ))                
                mHandleFactory.color(mCrv.mNode, controlType = 'sub')            
                CORERIG.shapeParent_in_place(ml_handleJoints[i].mNode, 
                                             mCrv.mNode, False,
                                             replaceShapes=True)            
            
            
            """
            #l_uValues = MATH.get_splitValueList(.01,.99, len(ml_handleJoints))
            ml_handleShapes = self.atBuilderUtils('shapes_fromCast',
                                                  targets = [mObj.mNode for mObj in self.ml_handleTargets],
                                                  mode ='segmentHandle')
            
            #offset = 3
            if str_ikBase == 'hips':
                mHandleFactory.color(ml_handleShapes[1].mNode, controlType = 'sub')            
                CORERIG.shapeParent_in_place(ml_handleJoints[0].mNode, 
                                             ml_handleShapes[1].mNode, False,
                                             replaceShapes=True)
                for mObj in ml_handleShapes:
                    try:mObj.delete()
                    except:pass
            else:
                for i,mCrv in enumerate(ml_handleShapes):
                    log.debug("|{0}| >> Shape: {1} | Handle: {2}".format(_str_func,mCrv.mNode,ml_handleJoints[i].mNode ))                
                    mHandleFactory.color(mCrv.mNode, controlType = 'sub')            
                    CORERIG.shapeParent_in_place(ml_handleJoints[i].mNode, 
                                                 mCrv.mNode, False,
                                                 replaceShapes=True)
                #for mShape in ml_handleJoints[i].getShapes(asMeta=True):
                    #mShape.doName()"""

        return
    except Exception,err:cgmGEN.cgmException(Exception,err)

@cgmGEN.Timer
def rig_shapes(self):
    try:
        _short = self.d_block['shortName']
        _str_func = 'rig_shapes'
        log.debug("|{0}| >>  {1}".format(_str_func,self)+ '-'*80)
        
        #_str_func = '[{0}] > rig_shapes'.format(_short)
        log.info("|{0}| >> ...".format(_str_func))  
        
        mBlock = self.mBlock
        
        str_rigSetup = ATTR.get_enumValueString(mBlock.mNode,'rigSetup')
        
        if str_rigSetup == 'digit':
            return rig_digitShapes(self)
        
        mRigNull = self.mRigNull
        
        ml_templateHandles = mBlock.msgList_get('templateHandles')
        ml_prerigHandleTargets = self.mBlock.atBlockUtils('prerig_getHandleTargets')
        ml_fkJoints = self.mRigNull.msgList_get('fkJoints')
        ml_ikJoints = mRigNull.msgList_get('ikJoints',asMeta=True)
        ml_blendJoints = self.mRigNull.msgList_get('blendJoints')
        
        mIKEnd = ml_prerigHandleTargets[-1]
        ml_prerigHandles = mBlock.msgList_get('prerigHandles')
        
        _side = mBlock.atUtils('get_side')
        _short_module = self.mModule.mNode
        str_ikBase = ATTR.get_enumValueString(mBlock.mNode,'ikBase')
        str_rigSetup = ATTR.get_enumValueString(mBlock.mNode,'rigSetup')
        
        mHandleFactory = mBlock.asHandleFactory()
        mOrientHelper = mBlock.orientHelper
        
        #_size = 5
        #_size = MATH.average(mHandleFactory.get_axisBox_size(ml_prerigHandles[0].mNode))
        _jointOrientation = self.d_orientation['str']
        
        ml_joints = self.d_joints['ml_moduleJoints']
        
        #Our base size will be the average of the bounding box sans the largest
        _bbSize = TRANS.bbSize_get(mBlock.getMessage('prerigLoftMesh')[0],shapes=True)
        _bbSize.remove(max(_bbSize))
        _size = MATH.average(_bbSize)
        _offset = self.v_offset

        #Pivots =======================================================================================
        mPivotHolderHandle = ml_templateHandles[-1]
        mPivotHelper = False
        if mPivotHolderHandle.getMessage('pivotHelper'):
            mPivotHelper = mPivotHolderHandle.pivotHelper
            log.debug("|{0}| >> Pivot shapes...".format(_str_func))            
            mBlock.atBlockUtils('pivots_buildShapes', mPivotHolderHandle.pivotHelper, mRigNull)

        #IK End ================================================================================
        if mBlock.ikSetup:
            log.debug("|{0}| >> ikHandle...".format(_str_func))
            
            if mPivotHelper:
                mIKCrv = mPivotHelper.doDuplicate(po=False)
                mIKCrv.parent = False
                mShape2 = False
                for mChild in mIKCrv.getChildren(asMeta=True):
                    if mChild.cgmName == 'topLoft':
                        mShape2 = mChild.doDuplicate(po=False)
                        DIST.offsetShape_byVector(mShape2.mNode,_offset,component='cv')
    
                    mChild.delete()
    
                DIST.offsetShape_byVector(mIKCrv.mNode,_offset,component='cv')
    
                if mShape2:
                    CORERIG.shapeParent_in_place(mIKCrv.mNode, mShape2.mNode, False)
    
    
                TRANS.rotatePivot_set(mIKCrv.mNode,
                                      ml_fkJoints[self.int_handleEndIdx].p_position )                
            elif ml_templateHandles[-1].getMessage('proxyHelper'):
                log.debug("|{0}| >> proxyHelper IK shape...".format(_str_func))
                mProxyHelper = ml_templateHandles[-1].getMessage('proxyHelper',asMeta=True)[0]
                bb_ik = mHandleFactory.get_axisBox_size(mProxyHelper.mNode)
                
                _ik_shape = CURVES.create_fromName('cube', size = bb_ik)
                ATTR.set(_ik_shape,'scale', 1.5)
                mIKShape = cgmMeta.validateObjArg(_ik_shape, 'cgmObject',setClass=True)
                #DIST.offsetShape_byVector(_ik_shape,_offset, mIKCrv.p_position,component='cv')
                                
                mIKShape.doSnapTo(mProxyHelper)
                pos_ik = POS.get_bb_center(mProxyHelper.mNode)
                #SNAPCALLS.get_special_pos(mEndHandle.p_nameLong,
                #                                   'axisBox','z+',False)                
                
                mIKShape.p_position = pos_ik
                mIKCrv = self.ml_handleTargets[self.int_handleEndIdx].doCreateAt()
                
                CORERIG.shapeParent_in_place(mIKCrv.mNode, mIKShape.mNode, False)
                
                #CORERIG.match_transform(mIKShape.mNode, self.ml_handleTargets[self.int_handleEndIdx].mNode)
                
            else:
                log.debug("|{0}| >> default IK shape...".format(_str_func))                
                mIKTemplateHandle = ml_templateHandles[self.int_handleEndIdx]
                bb_ik = mHandleFactory.get_axisBox_size(mIKTemplateHandle.mNode)
                _ik_shape = CURVES.create_fromName('cube', size = bb_ik)
                ATTR.set(_ik_shape,'scale', 1.5)
                
                mIKCrv = cgmMeta.validateObjArg(_ik_shape, 'cgmObject',setClass=True)
                mIKCrv.doSnapTo(self.ml_handleTargets[self.int_handleEndIdx].mNode)
    
            mHandleFactory.color(mIKCrv.mNode, controlType = 'main',transparent=True)
            mIKCrv.doCopyNameTagsFromObject(ml_fkJoints[self.int_handleEndIdx].mNode,
                                            ignore=['cgmType','cgmTypeModifier'])
            mIKCrv.doStore('cgmTypeModifier','ik')
            mIKCrv.doStore('cgmType','handle')
            mIKCrv.doName()
    
            mc.makeIdentity(mIKCrv.mNode, apply = True, t=0, r=0,s=1,n=0,pn=1)
            
    
            #CORERIG.match_transform(mIKCrv.mNode,ml_ikJoints[-1].mNode)
            mHandleFactory.color(mIKCrv.mNode, controlType = 'main')        
    
            self.mRigNull.connectChildNode(mIKCrv,'controlIK','rigNull')#Connect            
    
            """
               #mIKCrvShape = ml_fkShapes[-1].doDuplicate(po=False)
                mIKCrv = ml_ikJoints[-1].doCreateAt(setClass=True)
    
                CORERIG.shapeParent_in_place(mIKCrv.mNode,ml_fkShapes[-1].mNode,False)
    
                mHandleFactory.color(mIKCrv.mNode, controlType = 'main',transparent=True)
                mIKCrv.doCopyNameTagsFromObject(ml_fkJoints[-1].mNode,ignore=['cgmType','cgmTypeModifier'])
                mIKCrv.doStore('cgmTypeModifier','ik')
                mIKCrv.doName()
    
                #CORERIG.match_transform(mIKCrv.mNode,ml_ikJoints[-1].mNode)
                mHandleFactory.color(mIKCrv.mNode, controlType = 'main')        
    
                self.mRigNull.connectChildNode(mIKCrv,'controlIK','rigNull')#Connect
                """
            
            #Mid IK...---------------------------------------------------------------------------------
            log.debug("|{0}| >> midIK...".format(_str_func))
            mKnee = ml_templateHandles[self.int_templateHandleMidIdx].doCreateAt(setClass=True)
            size_knee =  POS.get_bb_size(ml_templateHandles[self.int_templateHandleMidIdx].mNode)
    
            crv = CURVES.create_controlCurve(mKnee, shape='sphere',
                                             direction = _jointOrientation[0]+'+',
                                             sizeMode = 'fixed',
                                             size = max(size_knee))            
    
            CORERIG.shapeParent_in_place(mKnee.mNode, crv, False)
            mKnee.doSnapTo(ml_ikJoints[1].mNode)
    
            #Get our point for knee...
            mKnee.p_position = self.atBuilderUtils('get_midIK_basePosOrient',self.ml_handleTargets,False)
    
            CORERIG.match_orientation(mKnee.mNode, mIKCrv.mNode)
            #mc.makeIdentity(mKnee.mNode, apply = True, t=0, r=0,s=1,n=0,pn=1)
            mHandleFactory.color(mKnee.mNode, controlType = 'sub')
    
            mKnee.doCopyNameTagsFromObject(ml_fkJoints[1].mNode,ignore=['cgmType','cgmTypeModifier'])
            mKnee.doStore('cgmAlias','midIK')            
            mKnee.doName()
    
            self.mRigNull.connectChildNode(mKnee,'controlIKMid','rigNull')#Connect

        
        #Lever =============================================================================
        if self.b_lever:
            log.debug("|{0}| >> Lever...".format(_str_func))
            mLeverRigJnt = mRigNull.getMessage('leverDirect',asMeta=True)[0]
            mLeverFKJnt = mRigNull.getMessage('leverFK',asMeta=True)[0]
            log.debug("|{0}| >> mLeverRigJnt: {1}".format(_str_func,mLeverRigJnt))            
            log.debug("|{0}| >> mLeverFKJnt: {1}".format(_str_func,mLeverFKJnt))            
            
            dist_lever = DIST.get_distance_between_points(ml_prerigHandles[0].p_position,
                                                          ml_prerigHandles[1].p_position)
            log.debug("|{0}| >> Lever dist: {1}".format(_str_func,dist_lever))
            
            #Dup our rig joint and move it 
            mDup = mLeverRigJnt.doDuplicate()
            mDup.resetAttrs()
            ATTR.set(mDup.mNode, 't{0}'.format(_jointOrientation[0]), dist_lever)
            
            ml_clavShapes = BUILDUTILS.shapes_fromCast(self, targets= [mLeverFKJnt.mNode,
                                                                       #ml_fkJoints[0].mNode],
                                                                        mDup.mNode],
                                                             offset=_offset,
                                                             mode = 'frameHandle')
            
            mHandleFactory.color(ml_clavShapes[0].mNode, controlType = 'main')        
            CORERIG.shapeParent_in_place(mLeverFKJnt.mNode,ml_clavShapes[0].mNode, False, replaceShapes=True)
            
            mc.delete([mShape.mNode for mShape in ml_clavShapes] + [mDup.mNode])
            
            #limbRoot ------------------------------------------------------------------------------
            log.debug("|{0}| >> Lever -- limbRoot".format(_str_func))
            mLimbRootHandle = ml_prerigHandles[1]
            mLimbRoot = ml_fkJoints[0].doCreateAt()
        
            _size_root =  MATH.average(POS.get_bb_size(self.mRootTemplateHandle.mNode)) * .75
            mRootCrv = cgmMeta.validateObjArg(CURVES.create_fromName('locatorForm', _size_root),'cgmObject',setClass=True)
            mRootCrv.doSnapTo(mLimbRootHandle)
        
            #SNAP.go(mRootCrv.mNode, ml_joints[0].mNode,position=False)
        
            CORERIG.shapeParent_in_place(mLimbRoot.mNode,mRootCrv.mNode, False)
        
            for a in 'cgmName','cgmDirection','cgmModifier':
                if ATTR.get(_short_module,a):
                    ATTR.copy_to(_short_module,a,mLimbRoot.mNode,driven='target')
        
            mLimbRoot.doStore('cgmTypeModifier','limbRoot')
            mLimbRoot.doName()
        
            mHandleFactory.color(mLimbRoot.mNode, controlType = 'sub')
        
            self.mRigNull.connectChildNode(mLimbRoot,'limbRoot','rigNull')#Connect            
            
            
        
        #Cog =============================================================================
        if mBlock.getMessage('cogHelper') and mBlock.getMayaAttr('addCog'):
            log.debug("|{0}| >> Cog...".format(_str_func))
            mCogHelper = mBlock.cogHelper
            
            mCog = mCogHelper.doCreateAt(setClass=True)
            CORERIG.shapeParent_in_place(mCog.mNode, mCogHelper.shapeHelper.mNode)
            
            mCog.doStore('cgmName','cog')
            mCog.doStore('cgmAlias','cog')            
            mCog.doName()
            
            self.mRigNull.connectChildNode(mCog,'rigRoot','rigNull')#Connect
            self.mRigNull.connectChildNode(mCog,'settings','rigNull')#Connect        
            

        else:#Root =============================================================================
            log.debug("|{0}| >> Root...".format(_str_func))
            
            if self.b_lever:
                mRootHandle = ml_prerigHandles[1]
            else:
                mRootHandle = ml_prerigHandles[0]
            #mRoot = ml_joints[0].doCreateAt()
            
            mRoot = ml_fkJoints[0].doCreateAt()
            
            _size_root =  MATH.average(mHandleFactory.get_axisBox_size(self.mRootTemplateHandle.mNode))
            mRootCrv = cgmMeta.validateObjArg(CURVES.create_fromName('cube', _size_root),'cgmObject',setClass=True)
            mRootCrv.doSnapTo(mRootHandle)
        
            #SNAP.go(mRootCrv.mNode, ml_joints[0].mNode,position=False)
        
            CORERIG.shapeParent_in_place(mRoot.mNode,mRootCrv.mNode, False)
        
            ATTR.copy_to(_short_module,'cgmName',mRoot.mNode,driven='target')
            mRoot.doStore('cgmTypeModifier','root')
            mRoot.doName()
            
            mHandleFactory.color(mRoot.mNode, controlType = 'sub')
            
            self.mRigNull.connectChildNode(mRoot,'rigRoot','rigNull')#Connect
        
            
            #Settings =============================================================================
            _settingsPlace = mBlock.getEnumValueString('settingsPlace')
            if _settingsPlace == 'cog':
                log.warning("|{0}| >> Settings. Cog option but no cog found...".format(_str_func))
                _settingsPlace = 'start'
            
            if _settingsPlace is not 'cog':
                log.debug("|{0}| >> settings: {1}...".format(_str_func,_settingsPlace))
                
                
                if ml_blendJoints:
                    ml_targets = ml_blendJoints
                else:
                    ml_targets = ml_fkJoints
                    
                if _settingsPlace == 'start':
                    _mTar = ml_targets[0]
                    _settingsSize = MATH.average(TRANS.bbSize_get(self.mRootTemplateHandle.mNode,shapes=True))
                else:
                    _mTar = ml_targets[self.int_handleEndIdx]
                    _settingsSize = MATH.average(TRANS.bbSize_get(ml_templateHandles[-1].mNode,shapes=True))
                    
                mSettingsShape = cgmMeta.validateObjArg(CURVES.create_fromName('gear',_settingsSize * .5,
                                                                               '{0}+'.format(_jointOrientation[2])),'cgmObject',setClass=True)
    
                mSettingsShape.doSnapTo(_mTar.mNode)
                d_directions = {'up':'y+','down':'y-','in':'x+','out':'x-'}
                str_settingsDirections = d_directions.get(mBlock.getEnumValueString('settingsDirection'),'y+')
                mSettingsShape.p_position = _mTar.getPositionByAxisDistance(str_settingsDirections,
                                                                            _settingsSize)
                
                SNAP.aim_atPoint(mSettingsShape.mNode,
                                 _mTar.p_position,
                                 aimAxis=_jointOrientation[0]+'+',
                                 mode = 'vector',
                                 vectorUp= _mTar.getAxisVector(_jointOrientation[0]+'-'))
                                
                mSettingsShape.parent = _mTar
                mSettings = mSettingsShape
                CORERIG.match_orientation(mSettings.mNode, _mTar.mNode)
                
                ATTR.copy_to(_short_module,'cgmName',mSettings.mNode,driven='target')
    
                mSettings.doStore('cgmTypeModifier','settings')
                mSettings.doName()
                mHandleFactory.color(mSettings.mNode, controlType = 'sub')
            
                mRigNull.connectChildNode(mSettings,'settings','rigNull')#Connect        
            
        
         
    
        #Direct Controls =============================================================================
        log.debug("|{0}| >> direct...".format(_str_func))                
        ml_rigJoints = self.mRigNull.msgList_get('rigJoints')
        _size_direct = DIST.get_distance_between_targets([mObj.mNode for mObj in ml_rigJoints], average=True)        

        d_direct = {'size':_size_direct/4}
            
        ml_directShapes = self.atBuilderUtils('shapes_fromCast',
                                              ml_rigJoints,
                                              mode ='direct',**d_direct)
                                                                                                                                                                #offset = 3
    
        for i,mCrv in enumerate(ml_directShapes):
            mHandleFactory.color(mCrv.mNode, controlType = 'sub')
            CORERIG.shapeParent_in_place(ml_rigJoints[i].mNode,mCrv.mNode, False, replaceShapes=True)
    
        for mJnt in ml_rigJoints:
            try:
                mJnt.drawStyle =2
            except:
                mJnt.radius = .00001

        
        #Handles ============================================================================================    
        ml_handleJoints = self.mRigNull.msgList_get('handleJoints')
        if ml_handleJoints:
            log.debug("|{0}| >> Found Handle joints...".format(_str_func))
            
            ml_handleShapes = self.atBuilderUtils('shapes_fromCast',
                                                  targets = [mObj.mNode for mObj in ml_handleJoints],
                                                  mode = 'limbSegmentHandle')
            
            for i,mCrv in enumerate(ml_handleShapes):
                log.debug("|{0}| >> Shape: {1} | Handle: {2}".format(_str_func,
                                                                     mCrv.mNode,
                                                                     ml_handleJoints[i].mNode ))                
                mHandleFactory.color(mCrv.mNode, controlType = 'sub')            
                CORERIG.shapeParent_in_place(ml_handleJoints[i].mNode, 
                                             mCrv.mNode, False,
                                             replaceShapes=True)            
            
            
            """
            #l_uValues = MATH.get_splitValueList(.01,.99, len(ml_handleJoints))
            ml_handleShapes = self.atBuilderUtils('shapes_fromCast',
                                                  targets = [mObj.mNode for mObj in self.ml_handleTargets],
                                                  mode ='segmentHandle')
            
            #offset = 3
            if str_ikBase == 'hips':
                mHandleFactory.color(ml_handleShapes[1].mNode, controlType = 'sub')            
                CORERIG.shapeParent_in_place(ml_handleJoints[0].mNode, 
                                             ml_handleShapes[1].mNode, False,
                                             replaceShapes=True)
                for mObj in ml_handleShapes:
                    try:mObj.delete()
                    except:pass
            else:
                for i,mCrv in enumerate(ml_handleShapes):
                    log.debug("|{0}| >> Shape: {1} | Handle: {2}".format(_str_func,mCrv.mNode,ml_handleJoints[i].mNode ))                
                    mHandleFactory.color(mCrv.mNode, controlType = 'sub')            
                    CORERIG.shapeParent_in_place(ml_handleJoints[i].mNode, 
                                                 mCrv.mNode, False,
                                                 replaceShapes=True)
                #for mShape in ml_handleJoints[i].getShapes(asMeta=True):
                    #mShape.doName()"""
        
        #FK/Ik ==========================================================================================    
        log.debug("|{0}| >> Frame shape cast...".format(_str_func))        
        ml_fkShapes = self.atBuilderUtils('shapes_fromCast',
                                          targets = [mObj.mNode for mObj in self.ml_handleTargets],
                                          mode = 'frameHandle')#limbHandle
        
        if self.mPivotHelper:
            size_pivotHelper = POS.get_bb_size(self.mPivotHelper.mNode)
        else:
            size_pivotHelper = POS.get_bb_size(ml_templateHandles[-1].mNode)
        
        if self.mBall:
            #_size_ball = DIST.get_distance_between_targets([self.mBall.mNode,
                                                            #self.mBall.p_parent])
        
            crv = CURVES.create_controlCurve(self.mBall.mNode, shape='circle',
                                             direction = _jointOrientation[0]+'+',
                                             sizeMode = 'fixed',
                                             size = size_pivotHelper[0])
            ml_fkShapes.append(cgmMeta.validateObjArg(crv,'cgmObject'))
            
        if self.mToe:
            #_size_ball = DIST.get_distance_between_targets([self.mToe.mNode,
            #                                                self.mToe.p_parent])
    
            crv = CURVES.create_controlCurve(self.mToe.mNode, shape='circle',
                                             direction = _jointOrientation[0]+'+',
                                             sizeMode = 'fixed',
                                             size = size_pivotHelper[0])        
            ml_fkShapes.append(cgmMeta.validateObjArg(crv,'cgmObject'))
        
        

        log.debug("|{0}| >> FK...".format(_str_func))    
        for i,mShape in enumerate(ml_fkShapes):
            mJnt = ml_fkJoints[i]
            
            if mJnt == ml_fkJoints[self.int_handleEndIdx]:
                log.debug("|{0}| >> Last fk handle before toes/ball...".format(_str_func))                
                mIKTemplateHandle = ml_templateHandles[-1]
                
                mShape1 = mIKTemplateHandle.loftCurve.doDuplicate(po = False)
                mShape2 = mIKTemplateHandle.loftCurve.doDuplicate(po = False)
                
                for mShp in mShape1,mShape2:
                    ATTR.set_standardFlags(mShp.mNode,lock=False,keyable=True)
                    mShp.p_parent = False
                    SNAP.go(mShp.mNode,mJnt.mNode)
                
                _p = mJnt.p_position
                DIST.offsetShape_byVector(mShape1.mNode,_offset,_p)
                DIST.offsetShape_byVector(mShape2.mNode,_offset * 2,_p)
                
                CORERIG.combineShapes([mShape2.mNode,mShape1.mNode])
                _fk_shape = mShape1.mNode
                #bb_ik = mHandleFactory.get_axisBox_size(mIKTemplateHandle.mNode)
                #_fk_shape = CURVES.create_fromName('sphere', size = bb_ik)
                #ATTR.set(_fk_shape,'scale', 2)
                #SNAP.go(_fk_shape,mJnt.mNode)
                mHandleFactory.color(_fk_shape, controlType = 'main')        
                CORERIG.shapeParent_in_place(mJnt.mNode,_fk_shape, False, replaceShapes=True)            
                mShape.delete()
            else:
                mHandleFactory.color(mShape.mNode, controlType = 'main')        
                CORERIG.shapeParent_in_place(mJnt.mNode,mShape.mNode, False, replaceShapes=True)

        return
    except Exception,err:cgmGEN.cgmException(Exception,err)
    
@cgmGEN.Timer
def rig_controls(self):
    _short = self.d_block['shortName']
    _str_func = 'rig_controls'
    log.debug("|{0}| >>  {1}".format(_str_func,self)+ '-'*80)
    
    mBlock = self.mBlock
    mRigNull = self.mRigNull
    ml_controlsAll = []#we'll append to this list and connect them all at the end
    mRootParent = self.mConstrainNull
    mSettings = mRigNull.settings
    ml_handleJoints = mRigNull.msgList_get('handleJoints')
    
    b_cog = False
    if mBlock.getMessage('cogHelper'):
        b_cog = True
    str_ikBase = ATTR.get_enumValueString(mBlock.mNode,'ikBase')
    d_controlSpaces = self.atBuilderUtils('get_controlSpaceSetupDict')    
    ml_controlsIKRO = []
        
    # Drivers ==============================================================================================
    log.debug("|{0}| >> Attr drivers...".format(_str_func))    
    if mBlock.ikSetup:
        log.debug("|{0}| >> Build IK drivers...".format(_str_func))
        mPlug_FKIK = cgmMeta.cgmAttr(mSettings.mNode,'FKIK',attrType='float',minValue=0,maxValue=1,lock=False,keyable=True)
    
    #>> vis Drivers ==========================================================================================	
    mPlug_visSub = self.atBuilderUtils('build_visSub')
    
    if not b_cog:
        mPlug_visRoot = cgmMeta.cgmAttr(mSettings,'visRoot', value = True, attrType='bool', defaultValue = False,keyable = False,hidden = False)
    mPlug_visDirect = cgmMeta.cgmAttr(mSettings,'visDirect', value = True, attrType='bool', defaultValue = False,keyable = False,hidden = False)
    
    #Root ==============================================================================================
    log.debug("|{0}| >> Root...".format(_str_func))
    
    if not mRigNull.getMessage('rigRoot'):
        raise ValueError,"No rigRoot found"
    
    mRoot = mRigNull.rigRoot
    log.debug("|{0}| >> Found rigRoot : {1}".format(_str_func, mRoot))
    
    _d = MODULECONTROL.register(mRoot,
                                addDynParentGroup = True,
                                mirrorSide= self.d_module['mirrorDirection'],
                                mirrorAxis="translateX,rotateY,rotateZ",
                                makeAimable = True)
    
    mRoot = _d['mObj']
    mRoot.masterGroup.parent = mRootParent
    ml_controlsAll.append(mRoot)
    mRootParent = mRoot#Change parent going forward...
    
        
    #Settings overall =========================================================================================
    if not b_cog:
        for mShape in mRoot.getShapes(asMeta=True):
            ATTR.connect(mPlug_visRoot.p_combinedShortName, "{0}.overrideVisibility".format(mShape.mNode))
            
        #>> settings -------------------------------------------------------------------------------------
        log.info("|{0}| >> Settings : {1}".format(_str_func, mSettings))
        MODULECONTROL.register(mSettings)
        ml_controlsAll.append(mSettings)
        #ml_blendJoints = self.mRigNull.msgList_get('blendJoints')
        #if ml_blendJoints:
        #    mSettings.masterGroup.parent = ml_blendJoints[-1]
        #else:
        #    mSettings.masterGroup.parent = ml_fkJoints[-1]


    #Lever =================================================================================================
    if self.b_lever:
        #LimbRoot -----------------------------------------------------------------------------------------
        log.debug("|{0}| >> limbRoot...".format(_str_func))
        
        if not mRigNull.getMessage('limbRoot'):
            raise ValueError,"No limbRoot found"
    
        mLimbRoot = mRigNull.limbRoot
        log.debug("|{0}| >> Found rigRoot : {1}".format(_str_func, mLimbRoot))
    
        _d = MODULECONTROL.register(mLimbRoot,
                                    addDynParentGroup = True,
                                    mirrorSide= self.d_module['mirrorDirection'],
                                    mirrorAxis="translateX,rotateY,rotateZ",
                                    makeAimable = True)
    
        mLimbRoot = _d['mObj']
        mLimbRoot.masterGroup.parent = mRootParent
        mRootParent = mLimbRoot#Change parent going forward...
        ml_controlsAll.append(mLimbRoot)
        
        
        for mShape in mLimbRoot.getShapes(asMeta=True):
            ATTR.connect(mPlug_visRoot.p_combinedShortName, "{0}.overrideVisibility".format(mShape.mNode))        
        
        #Lever ---------------------------------------------------------------------------------------        
        log.debug("|{0}| >> Lever...".format(_str_func))
        #mLeverRigJnt = mRigNull.getMessage('leverRig',asMeta=True)[0]
        mLeverFK = mRigNull.getMessage('leverFK',asMeta=True)[0]
        d_buffer = MODULECONTROL.register(mLeverFK,
                                          typeModifier='FK',
                                          mirrorSide = self.d_module['mirrorDirection'],
                                          mirrorAxis ="translateX,rotateY,rotateZ",
                                          makeAimable = False)        
        ml_controlsAll.append(mLeverFK)
        
        

    
    # Pivots ================================================================================================
    #if mMainHandle.getMessage('pivotHelper'):
        #log.info("|{0}| >> Pivot helper found".format(_str_func))
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

    #FK controls ==============================================================================================
    log.debug("|{0}| >> FK Controls...".format(_str_func))
    ml_fkJoints = self.mRigNull.msgList_get('fkJoints')
    
    if str_ikBase == 'hips':
        ml_fkJoints = ml_fkJoints[1:]
    
    ml_fkJoints[0].parent = mRoot
    ml_controlsAll.extend(ml_fkJoints)
    
    for i,mObj in enumerate(ml_fkJoints):
        d_buffer = MODULECONTROL.register(mObj,
                                          mirrorSide= self.d_module['mirrorDirection'],
                                          mirrorAxis="translateX,rotateY,rotateZ",
                                          makeAimable = True)

        mObj = d_buffer['instance']
            
    
    #ControlIK ========================================================================================
    mControlIK = False
    if mRigNull.getMessage('controlIK'):
        mControlIK = mRigNull.controlIK
        log.debug("|{0}| >> Found controlIK : {1}".format(_str_func, mControlIK))
        

        _d = MODULECONTROL.register(mControlIK,
                                    addDynParentGroup = True,
                                    mirrorSide= self.d_module['mirrorDirection'],
                                    mirrorAxis="translateX,rotateY,rotateZ",
                                    makeAimable = True,
                                    **d_controlSpaces)
        
        mControlIK = _d['mObj']
        mControlIK.masterGroup.parent = mRootParent
        ml_controlsAll.append(mControlIK)
        ml_controlsIKRO.append(mControlIK)
        
    mControlBaseIK = False
    if mRigNull.getMessage('controlIKBase'):
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
        ml_controlsIKRO.append(mControlBaseIK)
        
        
    mControlMidIK = False
    if mRigNull.getMessage('controlIKMid'):
        mControlMidIK = mRigNull.controlIKMid
        log.debug("|{0}| >> Found controlIKMid : {1}".format(_str_func, mControlMidIK))
        

                
        _d = MODULECONTROL.register(mControlMidIK,
                                    addDynParentGroup = True,
                                    mirrorSide= self.d_module['mirrorDirection'],
                                    mirrorAxis="translateX,rotateY,rotateZ",
                                    makeAimable = True,
                                    **d_controlSpaces)
        
        mControlMidIK = _d['mObj']
        mControlMidIK.masterGroup.parent = mRootParent
        ml_controlsAll.append(mControlMidIK)
        ml_controlsIKRO.append(mControlMidIK)
        

    
    #>> handleJoints ========================================================================================
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
    log.debug("|{0}| >> Direct controls...".format(_str_func))
    
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

    #self.atBuilderUtils('check_nameMatches', ml_controlsAll)

    mHandleFactory = mBlock.asHandleFactory()
    for mCtrl in ml_controlsAll:
        ATTR.set(mCtrl.mNode,'rotateOrder',self.rotateOrder)
        
        ml_pivots = mCtrl.msgList_get('spacePivots')
        if ml_pivots:
            log.debug("|{0}| >> Coloring spacePivots for: {1}".format(_str_func,mCtrl))
            for mPivot in ml_pivots:
                mHandleFactory.color(mPivot.mNode, controlType = 'sub')
                
        if mCtrl.hasAttr('radius'):
            ATTR.set(mCtrl.mNode,'radius',0)

    for mCtrl in ml_controlsIKRO:
        ATTR.set(mCtrl.mNode,'rotateOrder',self.rotateOrderIK)
    

    
    ml_controlsAll = self.atBuilderUtils('register_mirrorIndices', ml_controlsAll)
    mRigNull.msgList_connect('controlsAll',ml_controlsAll)
    mRigNull.moduleSet.extend(ml_controlsAll)
    
    return 


@cgmGEN.Timer
def rig_segments(self):
    _short = self.d_block['shortName']
    _str_func = 'rig_segments'
    log.debug("|{0}| >>  {1}".format(_str_func,self)+ '-'*80)
    

    mBlock = self.mBlock
    mRigNull = self.mRigNull
    ml_rigJoints = mRigNull.msgList_get('rigJoints')
    #ml_segJoints = mRigNull.msgList_get('segmentJoints')
    mModule = self.mModule
    mRoot = mRigNull.rigRoot
    mPrerigNull = mBlock.prerigNull

    mRootParent = self.mConstrainNull
    ml_handleJoints = mRigNull.msgList_get('handleJoints')
    ml_prerigHandleJoints = mPrerigNull.msgList_get('handleJoints')
    _jointOrientation = self.d_orientation['str']
    
    if not ml_handleJoints and not self.md_roll:
        log.info("|{0}| >> No segment setup...".format(_str_func))
        return True    
    
    if ml_handleJoints:
        log.debug("|{0}| >> Handle Joints...".format(_str_func))
        
        for i,mHandle in enumerate(ml_handleJoints):
            log.debug("|{0}| >> {1}...".format(_str_func,mHandle))
            
        
    if self.md_roll:
        log.debug("|{0}| >> Segments...".format(_str_func))
        
        for i in self.md_roll.keys():
            log.debug("|{0}| >> Segment {1}".format(_str_func,i))
            
            ml_segHandles = mRigNull.msgList_get('segmentHandles_{0}'.format(i))
            log.debug("|{0}| >> Segment handles...".format(_str_func,i))
            pprint.pprint(ml_segHandles)
            
            #Parent these to their handles ------------------------------------------------
            ml_segHandles[0].parent = ml_handleJoints[i]
            ml_segHandles[-1].parent = ml_handleJoints[i+1]
            
            #Setup the aim blends ---------------------------------------------------------
            log.debug("|{0}| >> Aim segmentHandles: {1}".format(_str_func,i))            
            for ii,mSegHandle in enumerate(ml_segHandles):
                log.debug("|{0}| >> Handle: {1} | {2}".format(_str_func,mSegHandle.p_nameShort, ii))            
                mParent = mSegHandle.getParent(asMeta=1)
                idx_parent = ml_handleJoints.index(mParent)
                mBlendParent = mParent.masterGroup.getParent(asMeta=True)
                
                if mParent == ml_handleJoints[0]:
                    #First handle ================================================================
                    log.debug("|{0}| >> First handle...".format(_str_func))
                    _aimForward = ml_handleJoints[idx_parent+1].p_nameShort
                    
                    """
                    mc.aimConstraint(_aimForward, mSegHandle.mNode, maintainOffset = True,
                                     aimVector = [0,0,1], upVector = [0,1,0], 
                                     worldUpObject = mParent.mNode,
                                     worldUpType = 'objectrotation', 
                                     worldUpVector = [1,0,0])"""
                    
                    #Stable aim ---------------------------------------------------------------
                    log.debug("|{0}| >> Stable/Aim...".format(_str_func))                    
                    log.debug("|{0}| >> blendParent: {1} ".format(_str_func,mBlendParent))
                    
                    log.debug("|{0}| >> Stable up...".format(_str_func))
                    mStableUp = mBlendParent.doCreateAt()
                    mStableUp.p_parent = mRoot
                    mStableUp.doStore('cgmName',mSegHandle.mNode)                
                    mStableUp.doStore('cgmTypeModifier','stable')
                    mStableUp.doStore('cgmType','upObj')
                    mStableUp.doName()
                    
                    #orient contrain one channel
                    mc.orientConstraint(mBlendParent.mNode, mStableUp.mNode,
                                        maintainOffset = True,
                                        skip = [_jointOrientation[0], _jointOrientation[1]])
                    
                    
                    mAimStable = mSegHandle.doCreateAt()
                    mAimStable.p_parent = mBlendParent
                    mAimStable.doStore('cgmName',mSegHandle.mNode)                
                    mAimStable.doStore('cgmTypeModifier','stableStart')
                    mAimStable.doStore('cgmType','aimer')
                    mAimStable.doName()
                    
                    mAimFollow = mSegHandle.doCreateAt()
                    mAimFollow.p_parent = mBlendParent
                    mAimFollow.doStore('cgmName',mSegHandle.mNode)                
                    mAimFollow.doStore('cgmTypeModifier','follow')
                    mAimFollow.doStore('cgmType','aimer')
                    mAimFollow.doName()                    
                    
                    mc.aimConstraint(_aimForward, mAimFollow.mNode, maintainOffset = True,
                                     aimVector = [0,0,1], upVector = [0,1,0], 
                                     worldUpObject = mBlendParent.mNode,
                                     worldUpType = 'objectrotation', 
                                     worldUpVector = [0,1,0])
                    
                    mc.aimConstraint(_aimForward, mAimStable.mNode, maintainOffset = True,
                                     aimVector = [0,0,1], upVector = [0,1,0], 
                                     worldUpObject = mStableUp.mNode,
                                     worldUpType = 'objectrotation', 
                                     worldUpVector = [0,1,0])                    
                    
                    
                    const = mc.orientConstraint([mAimStable.mNode,mAimFollow.mNode],
                                                mParent.masterGroup.mNode, maintainOffset = False)[0]
                
                    d_blendReturn = NODEFACTORY.createSingleBlendNetwork([mParent.mNode,
                                                                          'stable_{0}'.format(i)],
                                                                         [mParent.mNode,'resRootFollow_{0}'.format(i)],
                                                                         [mParent.mNode,'resAimFollow_{0}'.format(i)],
                                                                         keyable=True)
                
                    targetWeights = mc.orientConstraint(const,q=True,
                                                        weightAliasList=True,
                                                        maintainOffset=True)
                
                    #Connect                                  
                    d_blendReturn['d_result1']['mi_plug'].doConnectOut('%s.%s' % (const,targetWeights[0]))
                    d_blendReturn['d_result2']['mi_plug'].doConnectOut('%s.%s' % (const,targetWeights[1]))
                    d_blendReturn['d_result1']['mi_plug'].p_hidden = True
                    d_blendReturn['d_result2']['mi_plug'].p_hidden = True
                    
                    
                    
                    
                    
                elif mParent == ml_handleJoints[-1]:
                    log.debug("|{0}| >> Last handles...".format(_str_func))
                    _aimBack = ml_handleJoints[idx_parent-1].p_nameShort
                    
                    mFollow = mSegHandle.doCreateAt()
                    mFollow.p_parent = mBlendParent
                    mFollow.doStore('cgmName',mSegHandle.mNode)                
                    mFollow.doStore('cgmTypeModifier','follow')
                    mFollow.doStore('cgmType','driver')
                    mFollow.doName()
                
                    mAimBack = mSegHandle.doCreateAt()
                    mAimBack.p_parent = mBlendParent
                    mAimBack.doStore('cgmName',mSegHandle.mNode)                                
                    mAimBack.doStore('cgmTypeModifier','back')
                    mAimBack.doStore('cgmType','aimer')
                    mAimBack.doName()
                    
                    log.debug("|{0}| >> Stable up...".format(_str_func))
                    mStableUp = mBlendParent.doCreateAt()
                    mStableUp.p_parent = mBlendParent.p_parent
                    mStableUp.doStore('cgmName',mSegHandle.mNode)                
                    mStableUp.doStore('cgmTypeModifier','stableEnd')
                    mStableUp.doStore('cgmType','upObj')
                    mStableUp.rotateOrder = 0#...thing we have to have this to xyz to work right
                    mStableUp.doName()
                    
                    mc.orientConstraint(mBlendParent.mNode, mStableUp.mNode,
                                        maintainOffset = True,
                                        skip = [_jointOrientation[2], _jointOrientation[1]])                    
                
                    mc.aimConstraint(_aimBack, mAimBack.mNode, maintainOffset = False,
                                     aimVector = [0,0,-1], upVector = self.v_twistUp,#[-1,0,0], 
                                     worldUpObject = mStableUp.mNode,
                                     worldUpType = 'objectrotation', 
                                     worldUpVector = self.v_twistUp)#[-1,0,0])
                
                

                    const = mc.orientConstraint([mFollow.mNode,mAimBack.mNode],
                                                mParent.masterGroup.mNode,
                                                maintainOffset = False)[0]
                
                    d_blendReturn = NODEFACTORY.createSingleBlendNetwork([mParent.mNode,
                                                                          'followRoot_{0}'.format(i)],
                                                                         [mParent.mNode,'resRootFollow_{0}'.format(i)],
                                                                         [mParent.mNode,'resAimFollow_{0}'.format(i)],
                                                                         keyable=True)
                
                    targetWeights = mc.orientConstraint(const,q=True,
                                                        weightAliasList=True,
                                                        maintainOffset=True)
                
                    #Connect                                  
                    d_blendReturn['d_result1']['mi_plug'].doConnectOut('%s.%s' % (const,targetWeights[0]))
                    d_blendReturn['d_result2']['mi_plug'].doConnectOut('%s.%s' % (const,targetWeights[1]))
                    d_blendReturn['d_result1']['mi_plug'].p_hidden = True
                    d_blendReturn['d_result2']['mi_plug'].p_hidden = True
                    
                    
                else:
                    _aimForward = ml_handleJoints[idx_parent+1].p_nameShort
                    _aimBack = ml_handleJoints[idx_parent-1].p_nameShort
                    
                    log.debug("|{0}| >> Blend handles | forward: {1} | back: {2}".format(_str_func,_aimForward,_aimBack))
                    
                    mAimForward = mSegHandle.doCreateAt()
                    mAimForward.p_parent = mSegHandle.p_parent
                    mAimForward.doStore('cgmName',mSegHandle.mNode)                
                    mAimForward.doStore('cgmTypeModifier','forward')
                    mAimForward.doStore('cgmType','aimer')
                    mAimForward.doName()
                
                    mAimBack = mSegHandle.doCreateAt()
                    mAimBack.p_parent = mSegHandle.p_parent
                    mAimBack.doStore('cgmName',mSegHandle.mNode)                                
                    mAimBack.doStore('cgmTypeModifier','back')
                    mAimBack.doStore('cgmType','aimer')
                    mAimBack.doName()
                
                    mc.aimConstraint(_aimForward, mAimForward.mNode, maintainOffset = False,
                                     aimVector = [0,0,1], upVector = [0,1,0], 
                                     worldUpObject = mParent.mNode,
                                     worldUpType = 'objectrotation', 
                                     worldUpVector = self.v_twistUp)
                    
                    mc.aimConstraint(_aimBack, mAimBack.mNode, maintainOffset = False,
                                     aimVector = [0,0,-1], upVector = [0,1,0], 
                                     worldUpObject = mParent.mNode,
                                     worldUpType = 'objectrotation', 
                                     worldUpVector = self.v_twistUp)                
                    
                    if ii == 0:
                        const = mc.orientConstraint([mAimBack.mNode,mAimForward.mNode], mSegHandle.mNode, maintainOffset = False)[0]
                    else:
                        const = mc.orientConstraint([mAimForward.mNode, mAimBack.mNode], mSegHandle.mNode, maintainOffset = False)[0]
                    
                    d_blendReturn = NODEFACTORY.createSingleBlendNetwork([mParent.mNode,
                                                                          'curveSeg_{0}'.format(i)],
                                                                         [mParent.mNode,'resRootFollow_{0}'.format(i)],
                                                                         [mParent.mNode,'resAimFollow_{0}'.format(i)],
                                                                         keyable=True)
                    
                    targetWeights = mc.orientConstraint(const,q=True,
                                                        weightAliasList=True,
                                                        maintainOffset=True)
                
                    #Connect                                  
                    d_blendReturn['d_result1']['mi_plug'].doConnectOut('%s.%s' % (const,targetWeights[0]))
                    d_blendReturn['d_result2']['mi_plug'].doConnectOut('%s.%s' % (const,targetWeights[1]))
                    d_blendReturn['d_result1']['mi_plug'].p_hidden = True
                    d_blendReturn['d_result2']['mi_plug'].p_hidden = True
                
                    #mHandle.parent = mAimGroup#...parent back
                
                    #if mHandle in [ml_handleJoints[0],ml_handleJoints[-1]]:
                    #    mHandle.followRoot = 1
                    #else:
                    #    mHandle.followRoot = .5                    
        
            
            
            
            #Seg handles -------------------------------------------------------------------
            ml_segJoints = mRigNull.msgList_get('segJoints_{0}'.format(i))
            log.debug("|{0}| >> Segment joints...".format(_str_func,i))
            pprint.pprint(ml_segJoints)
            
            for mJnt in ml_segJoints:
                mJnt.drawStyle = 2
                ATTR.set(mJnt.mNode,'radius',0)
            
            #Ribbon...
            log.debug("|{0}| >> Ribbon {1} setup...".format(_str_func,i))
            reload(IK)
            #mSurf = IK.ribbon([mObj.mNode for mObj in ml_rigJoints], baseName = mBlock.cgmName, connectBy='constraint', msgDriver='masterGroup', moduleInstance = mModule)
            mSurf = IK.ribbon([mObj.mNode for mObj in ml_segJoints],
                              #baseName = "{0}_seg_{1}".format(mBlock.cgmName,i),
                              baseName = "{0}_seg_{1}".format(self.d_module['partName'],i),                              
                              driverSetup='stable',
                              connectBy='constraint',
                              moduleInstance = mModule)
            
            #Skin ribbon...
            log.debug("|{0}| >> Skin Ribbon {1} setup...".format(_str_func,i))            
            mSkinCluster = cgmMeta.validateObjArg(mc.skinCluster ([mHandle.mNode for mHandle in ml_segHandles],
                                                                  mSurf.mNode,
                                                                  tsb=True,
                                                                  maximumInfluences = 2,
                                                                  normalizeWeights = 1,dropoffRate=2.5),
                                                  'cgmNode',
                                                  setClass=True)
            
            mSkinCluster.doStore('cgmName', mSurf.mNode)
            mSkinCluster.doName()    
            
            #cgmGEN.func_snapShot(vars())
        
            #ml_segJoints[0].parent = mRoot            
            
            
        #segmentHandles_{0}
    
    return
    
    
    
    if self.b_segmentSetup:
        raise NotImplementedError,'Not done here Josh'
    
    else:#Roll setup
        log.debug("|{0}| >> Roll setup".format(_str_func))
        
        for i,mHandle in enumerate(ml_prerigHandleJoints):
            mHandle.rigJoint.masterGroup.parent = ml_handleJoints[i]
            
            ml_rolls = self.md_roll.get(i)
            if ml_rolls:
                mSeg = ml_rolls[0].getMessageAsMeta('segJoint')
                
                mc.pointConstraint([ml_handleJoints[i].mNode,ml_handleJoints[i+1].mNode], mSeg.mNode)
                mc.orientConstraint([ml_handleJoints[i].mNode,ml_handleJoints[i+1].mNode], 
                                    mSeg.mNode, skip = [_jointOrientation[1],_jointOrientation[2]])
                mc.scaleConstraint([ml_handleJoints[i].mNode,ml_handleJoints[i+1].mNode], mSeg.mNode)
                
                
                ml_rolls[0].rigJoint.masterGroup.parent = mSeg.mNode
    return
                
        
    
    
    
    
    
    if not ml_segJoints:
        log.info("|{0}| >> No segment joints. No segment setup necessary.".format(_str_func))
        return True
    
    
    #>> Ribbon setup ========================================================================================
    log.debug("|{0}| >> Ribbon setup...".format(_str_func))
    reload(IK)
    #mSurf = IK.ribbon([mObj.mNode for mObj in ml_rigJoints], baseName = mBlock.cgmName, connectBy='constraint', msgDriver='masterGroup', moduleInstance = mModule)
    mSurf = IK.ribbon([mObj.mNode for mObj in ml_segJoints],
                      baseName = mBlock.cgmName,
                      driverSetup='stable',
                      connectBy='constraint',
                      moduleInstance = mModule)
    """
    #Setup the aim along the chain -----------------------------------------------------------------------------
    for i,mJnt in enumerate(ml_rigJoints):
        mAimGroup = mJnt.doGroup(True,asMeta=True,typeModifier = 'aim')
        v_aim = [0,0,1]
        if mJnt == ml_rigJoints[-1]:
            s_aim = ml_rigJoints[-2].masterGroup.mNode
            v_aim = [0,0,-1]
        else:
            s_aim = ml_rigJoints[i+1].masterGroup.mNode
    
        mc.aimConstraint(s_aim, mAimGroup.mNode, maintainOffset = True, #skip = 'z',
                         aimVector = v_aim, upVector = [1,0,0], worldUpObject = mJnt.masterGroup.mNode,
                         worldUpType = 'objectrotation', worldUpVector = [1,0,0])    
    """
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

    
@cgmGEN.Timer
def rig_frame(self):
    try:
        _short = self.d_block['shortName']
        _str_func = 'rig_rigFrame'.format(_short)
        log.debug("|{0}| >> ...".format(_str_func))  
        
        mBlock = self.mBlock
        mRigNull = self.mRigNull
        mRootParent = self.mConstrainNull
        
        ml_rigJoints = mRigNull.msgList_get('rigJoints')
        ml_fkJoints = mRigNull.msgList_get('fkJoints')
        ml_handleJoints = mRigNull.msgList_get('handleJoints')
        ml_baseIKDrivers = mRigNull.msgList_get('baseIKDrivers')
        ml_blendJoints = mRigNull.msgList_get('blendJoints')
        ml_templateHandles = mBlock.msgList_get('templateHandles')
        mPlug_globalScale = self.d_module['mPlug_globalScale']
        mRoot = mRigNull.rigRoot
        
        
        b_cog = False
        if mBlock.getMessage('cogHelper'):
            b_cog = True
        str_ikBase = ATTR.get_enumValueString(mBlock.mNode,'ikBase')
        str_rigSetup = mBlock.getEnumValueString('rigSetup')

        #Changing targets - these change based on how the setup rolls through
        #mIKHandleDriver = mIKControl#...this will change with pivot
        mIKControl = mRigNull.controlIK                
        mIKHandleDriver = mIKControl
        
        #Pivot Driver ========================================================================================
        mPivotHolderHandle = ml_templateHandles[-1]
        if mPivotHolderHandle.getMessage('pivotHelper'):
            log.debug("|{0}| >> Pivot setup initial".format(_str_func))
            
            if str_rigSetup == 'digit':
                mPivotDriverHandle = ml_templateHandles[-2]
            else:
                mPivotDriverHandle = mPivotHolderHandle
            
            mPivotResultDriver = mPivotDriverHandle.doCreateAt()
            mPivotResultDriver.addAttr('cgmName','pivotResult')
            mPivotResultDriver.addAttr('cgmType','driver')
            mPivotResultDriver.doName()
            
            mPivotResultDriver.addAttr('cgmAlias', 'PivotResult')
            mIKHandleDriver = mPivotResultDriver
            
            mRigNull.connectChildNode(mPivotResultDriver,'pivotResultDriver','rigNull')#Connect
            
            
        #Lever ===============================================================================================
        if self.b_lever:
            log.debug("|{0}| >> Lever setup | main".format(_str_func))            
            #mLeverRigJnt = mRigNull.getMessage('leverRig',asMeta=True)[0]
            mLeverFK = mRigNull.leverFK
            mLeverFK.masterGroup.p_parent = mRoot#mRootParent
            #mLeverDirect = mRigNull.leverDirect
            """
            log.debug("|{0}| >> Lever rig aim".format(_str_func))

            mAimGroup = mLeverDirect.doGroup(True,asMeta=True,typeModifier = 'aim')
            mc.aimConstraint(ml_handleJoints[0].mNode,
                             mAimGroup.mNode,
                             maintainOffset = True, weight = 1,
                             aimVector = self.d_orientation['vectorAim'],
                             upVector = self.d_orientation['vectorUp'],
                             worldUpVector = self.d_orientation['vectorOut'],
                             worldUpObject = mLeverFK.mNode,
                             worldUpType = 'objectRotation' )"""
        
        
            log.debug("|{0}| >> Lever setup | LimbRoot".format(_str_func))            
            if not mRigNull.getMessage('limbRoot'):
                raise ValueError,"No limbRoot found"
        
            mLimbRoot = mRigNull.limbRoot
            log.debug("|{0}| >> Found limbRoot : {1}".format(_str_func, mLimbRoot))
            mRoot = mLimbRoot

        
        """
        #>> handleJoints ========================================================================================
        if ml_handleJoints:
            log.debug("|{0}| >> Handles setup...".format(_str_func))
            
            ml_handleParents = ml_fkJoints
            if ml_blendJoints:
                log.debug("|{0}| >> Handles parent: blend".format(_str_func))
                ml_handleParents = ml_blendJoints            
            
            if str_ikBase == 'hips':
                log.debug("|{0}| >> hips setup...".format(_str_func))
                
                ml_ribbonIkHandles = mRigNull.msgList_get('ribbonIKDrivers')
                if not ml_ribbonIkHandles:
                    raise ValueError,"No ribbon IKDriversFound"
                
                reload(RIGCONSTRAINT)
                RIGCONSTRAINT.build_aimSequence(ml_handleJoints,
                                                ml_ribbonIkHandles,
                                                [mRigNull.controlIKBase.mNode],#ml_handleParents,
                                                mode = 'singleBlend',
                                                upMode = 'objectRotation')
                
                mHipHandle = ml_handleJoints[0]
                mHipHandle.masterGroup.p_parent = mRoot
                mc.pointConstraint(mRigNull.controlIKBase.mNode,
                                   mHipHandle.masterGroup.mNode,
                                   maintainOffset = True)
                
            else:

                for i,mHandle in enumerate(ml_handleJoints):
                    mHandle.masterGroup.parent = ml_handleParents[i]
                    s_rootTarget = False
                    s_targetForward = False
                    s_targetBack = False
                    mMasterGroup = mHandle.masterGroup
                    b_first = False
                    if mHandle == ml_handleJoints[0]:
                        log.debug("|{0}| >> First handle: {1}".format(_str_func,mHandle))
                        if len(ml_handleJoints) <=2:
                            s_targetForward = ml_handleParents[-1].mNode
                        else:
                            s_targetForward = ml_handleJoints[i+1].getMessage('masterGroup')[0]
                        s_rootTarget = mRoot.mNode
                        b_first = True
                        
                    elif mHandle == ml_handleJoints[-1]:
                        log.debug("|{0}| >> Last handle: {1}".format(_str_func,mHandle))
                        s_rootTarget = ml_handleParents[i].mNode                
                        s_targetBack = ml_handleJoints[i-1].getMessage('masterGroup')[0]
                    else:
                        log.debug("|{0}| >> Reg handle: {1}".format(_str_func,mHandle))            
                        s_targetForward = ml_handleJoints[i+1].getMessage('masterGroup')[0]
                        s_targetBack = ml_handleJoints[i-1].getMessage('masterGroup')[0]
                        
                    #Decompose matrix for parent...
                    mUpDecomp = cgmMeta.cgmNode(nodeType = 'decomposeMatrix')
                    mUpDecomp.doStore('cgmName',ml_handleParents[i].mNode)                
                    mUpDecomp.addAttr('cgmType','aimMatrix',attrType='string',lock=True)
                    mUpDecomp.doName()
                    
                    ATTR.connect("%s.worldMatrix"%(ml_handleParents[i].mNode),"%s.%s"%(mUpDecomp.mNode,'inputMatrix'))
                    
                    if s_targetForward:
                        mAimForward = mHandle.doCreateAt()
                        mAimForward.parent = mMasterGroup            
                        mAimForward.doStore('cgmTypeModifier','forward')
                        mAimForward.doStore('cgmType','aimer')
                        mAimForward.doName()
                        
                        _const=mc.aimConstraint(s_targetForward, mAimForward.mNode, maintainOffset = True, #skip = 'z',
                                                aimVector = [0,0,1], upVector = [1,0,0], worldUpObject = ml_handleParents[i].mNode,
                                                worldUpType = 'vector', worldUpVector = [0,0,0])            
                        s_targetForward = mAimForward.mNode
                        ATTR.connect("%s.%s"%(mUpDecomp.mNode,"outputRotate"),"%s.%s"%(_const[0],"upVector"))                 
                        
                    else:
                        s_targetForward = ml_handleParents[i].mNode
                        
                    if s_targetBack:
                        mAimBack = mHandle.doCreateAt()
                        mAimBack.parent = mMasterGroup                        
                        mAimBack.doStore('cgmTypeModifier','back')
                        mAimBack.doStore('cgmType','aimer')
                        mAimBack.doName()
                        
                        _const = mc.aimConstraint(s_targetBack, mAimBack.mNode, maintainOffset = True, #skip = 'z',
                                                  aimVector = [0,0,-1], upVector = [1,0,0], worldUpObject = ml_handleParents[i].mNode,
                                                  worldUpType = 'vector', worldUpVector = [0,0,0])  
                        s_targetBack = mAimBack.mNode
                        ATTR.connect("%s.%s"%(mUpDecomp.mNode,"outputRotate"),"%s.%s"%(_const[0],"upVector"))                                     
                    else:
                        s_targetBack = s_rootTarget
                        #ml_handleParents[i].mNode
                    
                    pprint.pprint([s_targetForward,s_targetBack])
                    mAimGroup = mHandle.doGroup(True,asMeta=True,typeModifier = 'aim')
                    
                    mHandle.parent = False
                    
                    if b_first:
                        const = mc.orientConstraint([s_targetBack, s_targetForward], mAimGroup.mNode, maintainOffset = True)[0]
                    else:
                        const = mc.orientConstraint([s_targetForward, s_targetBack], mAimGroup.mNode, maintainOffset = True)[0]
                        
        
                    d_blendReturn = NODEFACTORY.createSingleBlendNetwork([mHandle.mNode,'followRoot'],
                                                                         [mHandle.mNode,'resultRootFollow'],
                                                                         [mHandle.mNode,'resultAimFollow'],
                                                                         keyable=True)
                    targetWeights = mc.orientConstraint(const,q=True, weightAliasList=True,maintainOffset=True)
                    
                    #Connect                                  
                    d_blendReturn['d_result1']['mi_plug'].doConnectOut('%s.%s' % (const,targetWeights[0]))
                    d_blendReturn['d_result2']['mi_plug'].doConnectOut('%s.%s' % (const,targetWeights[1]))
                    d_blendReturn['d_result1']['mi_plug'].p_hidden = True
                    d_blendReturn['d_result2']['mi_plug'].p_hidden = True
                    
                    mHandle.parent = mAimGroup#...parent back
                    
                    if mHandle in [ml_handleJoints[0],ml_handleJoints[-1]]:
                        mHandle.followRoot = 1
                    else:
                        mHandle.followRoot = .5"""
                        
        
        #>> Build IK ======================================================================================
        if mBlock.ikSetup:
            _ikSetup = mBlock.getEnumValueString('ikSetup')
            log.debug("|{0}| >> IK Type: {1}".format(_str_func,_ikSetup))    
        
            if not mRigNull.getMessage('rigRoot'):
                raise ValueError,"No rigRoot found"
            if not mRigNull.getMessage('controlIK'):
                raise ValueError,"No controlIK found"            
            
            mIKControl = mRigNull.controlIK
            mSettings = mRigNull.settings
            ml_ikJoints = mRigNull.msgList_get('ikJoints')
            mPlug_FKIK = cgmMeta.cgmAttr(mSettings.mNode,'FKIK',attrType='float',lock=False,keyable=True)
            _jointOrientation = self.d_orientation['str']
            
            mStart = ml_ikJoints[0]
            mEnd = ml_ikJoints[self.int_handleEndIdx]
            _start = ml_ikJoints[0].mNode
            _end = ml_ikJoints[self.int_handleEndIdx].mNode
            
            
            #>>> Setup a vis blend result
            mPlug_FKon = cgmMeta.cgmAttr(mSettings,'result_FKon',attrType='float',defaultValue = 0,keyable = False,lock=True,hidden=True)	
            mPlug_IKon = cgmMeta.cgmAttr(mSettings,'result_IKon',attrType='float',defaultValue = 0,keyable = False,lock=True,hidden=True)	
        
            NODEFACTORY.createSingleBlendNetwork(mPlug_FKIK.p_combinedName,
                                                 mPlug_IKon.p_combinedName,
                                                 mPlug_FKon.p_combinedName)
            
            #IK...
            mIKGroup = mRoot.doCreateAt()
            mIKGroup.doStore('cgmTypeModifier','ik')
            mIKGroup.doName()
            
            mPlug_IKon.doConnectOut("{0}.visibility".format(mIKGroup.mNode))
            
            mIKGroup.parent = mRoot
            mIKControl.masterGroup.parent = mIKGroup
            
            """
            mIKBaseControl = False
            if mRigNull.getMessage('controlIKBase'):
                mIKBaseControl = mRigNull.controlIKBase
                
                if str_ikBase == 'hips':
                    mIKBaseControl.masterGroup.parent = mRoot
                else:
                    mIKBaseControl.masterGroup.parent = mIKGroup
                    
            else:#Spin Group
                #=========================================================================================
                log.debug("|{0}| >> spin setup...".format(_str_func))
            
                #Make a spin group
                mSpinGroup = mStart.doGroup(False,False,asMeta=True)
                mSpinGroup.doCopyNameTagsFromObject(self.mModule.mNode, ignore = ['cgmName','cgmType'])	
                mSpinGroup.addAttr('cgmName','{0}NoFlipSpin'.format(self.d_module['partName']))
                mSpinGroup.doName()
            
                mSpinGroup.parent = mRoot
            
                mSpinGroup.doGroup(True,True,typeModifier='zero')
            
                #Setup arg
                mPlug_spin = cgmMeta.cgmAttr(mIKControl,'spin',attrType='float',keyable=True, defaultValue = 0, hidden = False)
                mPlug_spin.doConnectOut("%s.r%s"%(mSpinGroup.mNode,_jointOrientation[0]))
                """
            
            if _ikSetup == 'rp':
                log.debug("|{0}| >> rp setup...".format(_str_func,_ikSetup))
                mIKMid = mRigNull.controlIKMid
                
                ml_end_children = mEnd.getChildren(asMeta=True)
                if ml_end_children:
                    for mChild in ml_end_children:
                        mChild.parent = False
                
                #Build the IK ---------------------------------------------------------------------
                reload(IK)
                _d_ik= {'globalScaleAttr':mPlug_globalScale.p_combinedName,
                        'stretch':'translate',
                        'lockMid':True,
                        'rpHandle':mIKMid.mNode,
                        'nameSuffix':'ik',
                        'controlObject':mIKControl.mNode,
                        'moduleInstance':self.mModule.mNode}
                
                d_ikReturn = IK.handle(_start,_end,**_d_ik)
                mIKHandle = d_ikReturn['mHandle']
                ml_distHandlesNF = d_ikReturn['ml_distHandles']
                mRPHandleNF = d_ikReturn['mRPHandle']
                
                """
                #Get our no flip position-------------------------------------------------------------------------
                log.debug("|{0}| >> no flip dat...".format(_str_func))
                
                _side = mBlock.atUtils('get_side')
                _dist_ik_noFlip = DIST.get_distance_between_points(mStart.p_position,
                                                                   mEnd.p_position)
                if _side == 'left':#if right, rotate the pivots
                    pos_noFlipOffset = mStart.getPositionByAxisDistance(_jointOrientation[2]+'-',_dist_ik_noFlip)
                else:
                    pos_noFlipOffset = mStart.getPositionByAxisDistance(_jointOrientation[2]+'+',_dist_ik_noFlip)
                
                #No flip -------------------------------------------------------------------------
                log.debug("|{0}| >> no flip setup...".format(_str_func))
                
                mIKHandle = d_ikReturn['mHandle']
                ml_distHandlesNF = d_ikReturn['ml_distHandles']
                mRPHandleNF = d_ikReturn['mRPHandle']
            
                #No Flip RP handle -------------------------------------------------------------------
                mRPHandleNF.p_position = pos_noFlipOffset
            
                mRPHandleNF.doCopyNameTagsFromObject(self.mModule.mNode, ignore = ['cgmName','cgmType'])
                mRPHandleNF.addAttr('cgmName','{0}PoleVector'.format(self.d_module['partName']), attrType = 'string')
                mRPHandleNF.addAttr('cgmTypeModifier','noFlip')
                mRPHandleNF.doName()
            
                if mIKBaseControl:
                    mRPHandleNF.parent = mIKBaseControl.mNode
                else:
                    mRPHandleNF.parent = mSpinGroup.mNode
                    """

                #>>>Parent IK handles -----------------------------------------------------------------
                log.debug("|{0}| >> parent ik dat...".format(_str_func,_ikSetup))
                
                mIKHandle.parent = mIKHandleDriver.mNode#handle to control	
                for mObj in ml_distHandlesNF[:-1]:
                    mObj.parent = mRoot
                ml_distHandlesNF[-1].parent = mIKHandleDriver.mNode#handle to control
                ml_distHandlesNF[1].parent = mIKMid
                ml_distHandlesNF[1].t = 0,0,0
                ml_distHandlesNF[1].r = 0,0,0
                
                #>>> Fix our ik_handle twist at the end of all of the parenting
                IK.handle_fixTwist(mIKHandle,_jointOrientation[0])#Fix the twist
                
                mc.orientConstraint([mIKControl.mNode],
                                    ml_ikJoints[self.int_handleEndIdx].mNode,
                                    maintainOffset = True)
                
                
                if ml_end_children:
                    for mChild in ml_end_children:
                        mChild.parent = mEnd                
                
                #mc.scaleConstraint([mIKControl.mNode],
                #                    ml_ikJoints[self.int_handleEndIdx].mNode,
                #                    maintainOffset = True)                
                #if mIKBaseControl:
                    #ml_ikJoints[0].parent = mRigNull.controlIKBase
                
                #if mIKBaseControl:
                    #mc.pointConstraint(mIKBaseControl.mNode, ml_ikJoints[0].mNode,maintainOffset=True)
                    
                    
                #Mid IK driver -----------------------------------------------------------------------
                log.info("|{0}| >> mid IK driver.".format(_str_func))
                mMidControlDriver = mIKMid.doCreateAt()
                mMidControlDriver.addAttr('cgmName','midIK')
                mMidControlDriver.addAttr('cgmType','driver')
                mMidControlDriver.doName()
                mMidControlDriver.addAttr('cgmAlias', 'midDriver')
                
                mc.pointConstraint([mRoot.mNode, mIKHandleDriver.mNode], mMidControlDriver.mNode)
                mMidControlDriver.parent = mIKGroup
                mIKMid.masterGroup.parent = mMidControlDriver
                
                #Mid IK trace
                log.debug("|{0}| >> midIK track Crv".format(_str_func, mIKMid))
                trackcrv,clusters = CORERIG.create_at([mIKMid.mNode,
                                                       ml_ikJoints[1].mNode],#ml_handleJoints[1]],
                                                      'linearTrack',
                                                      baseName = '{0}_midTrack'.format(self.d_module['partName']))
            
                mTrackCrv = cgmMeta.asMeta(trackcrv)
                mTrackCrv.p_parent = self.mModule
                mHandleFactory = mBlock.asHandleFactory()
                mHandleFactory.color(mTrackCrv.mNode, controlType = 'sub')
            
                for s in mTrackCrv.getShapes(asMeta=True):
                    s.overrideEnabled = 1
                    s.overrideDisplayType = 2
                mTrackCrv.doConnectIn('visibility',"{0}.v".format(mIKGroup.mNode))
                
                    
            elif _ikSetup == 'spline':
                log.debug("|{0}| >> spline setup...".format(_str_func))
                ml_ribbonIkHandles = mRigNull.msgList_get('ribbonIKDrivers')
                if not ml_ribbonIkHandles:
                    raise ValueError,"No ribbon IKDriversFound"
            
                log.debug("|{0}| >> ribbon ik handles...".format(_str_func))
                
                if mIKBaseControl:
                    ml_ribbonIkHandles[0].parent = mIKBaseControl
                else:
                    ml_ribbonIkHandles[0].parent = mSpinGroup
                    
                ml_ribbonIkHandles[-1].parent = mIKControl
            
                mc.aimConstraint(mIKControl.mNode,
                                 ml_ribbonIkHandles[0].mNode,
                                 maintainOffset = True, weight = 1,
                                 aimVector = self.d_orientation['vectorAim'],
                                 upVector = self.d_orientation['vectorUp'],
                                 worldUpVector = self.d_orientation['vectorOut'],
                                 worldUpObject = mSpinGroup.mNode,
                                 worldUpType = 'objectRotation' )
            
                
                res_spline = IK.spline([mObj.mNode for mObj in ml_ikJoints],
                                       orientation = _jointOrientation,
                                       moduleInstance = self.mModule)
                mSplineCurve = res_spline['mSplineCurve']
                log.debug("|{0}| >> spline curve...".format(_str_func))
                

                #...ribbon skinCluster ---------------------------------------------------------------------
                log.debug("|{0}| >> ribbon skinCluster...".format(_str_func))                
                mSkinCluster = cgmMeta.validateObjArg(mc.skinCluster ([mHandle.mNode for mHandle in ml_ribbonIkHandles],
                                                                      mSplineCurve.mNode,
                                                                      tsb=True,
                                                                      maximumInfluences = 2,
                                                                      normalizeWeights = 1,dropoffRate=2.5),
                                                      'cgmNode',
                                                      setClass=True)
            
                mSkinCluster.doStore('cgmName', mSplineCurve.mNode)
                mSkinCluster.doName()    
                cgmGEN.func_snapShot(vars())
                
            elif _ikSetup == 'ribbon':
                log.debug("|{0}| >> ribbon setup...".format(_str_func))
                ml_ribbonIkHandles = mRigNull.msgList_get('ribbonIKDrivers')
                if not ml_ribbonIkHandles:
                    raise ValueError,"No ribbon IKDriversFound"
                
                
                
                log.debug("|{0}| >> ribbon ik handles...".format(_str_func))
                if mIKBaseControl:
                    ml_ribbonIkHandles[0].parent = mIKBaseControl
                else:
                    ml_ribbonIkHandles[0].parent = mSpinGroup
                    mc.aimConstraint(mIKControl.mNode,
                                     ml_ribbonIkHandles[0].mNode,
                                     maintainOffset = True, weight = 1,
                                     aimVector = self.d_orientation['vectorAim'],
                                     upVector = self.d_orientation['vectorUp'],
                                     worldUpVector = self.d_orientation['vectorOut'],
                                     worldUpObject = mSpinGroup.mNode,
                                     worldUpType = 'objectRotation' )                    
                
                ml_ribbonIkHandles[-1].parent = mIKControl
                
                reload(IK)
                mSurf = IK.ribbon([mObj.mNode for mObj in ml_ikJoints],
                                  baseName = self.d_module['partName'] + '_ikRibbon',
                                  driverSetup='stable',
                                  connectBy='constraint',
                                  moduleInstance = self.mModule)
                
                log.debug("|{0}| >> ribbon surface...".format(_str_func))
                """
                #Setup the aim along the chain -----------------------------------------------------------------------------
                for i,mJnt in enumerate(ml_ikJoints):
                    mAimGroup = mJnt.doGroup(True,asMeta=True,typeModifier = 'aim')
                    v_aim = [0,0,1]
                    if mJnt == ml_ikJoints[-1]:
                        s_aim = ml_ikJoints[-2].masterGroup.mNode
                        v_aim = [0,0,-1]
                    else:
                        s_aim = ml_ikJoints[i+1].masterGroup.mNode
            
                    mc.aimConstraint(s_aim, mAimGroup.mNode, maintainOffset = True, #skip = 'z',
                                     aimVector = v_aim, upVector = [1,0,0], worldUpObject = mJnt.masterGroup.mNode,
                                     worldUpType = 'objectrotation', worldUpVector = [1,0,0])    
                """
                #...ribbon skinCluster ---------------------------------------------------------------------
                log.debug("|{0}| >> ribbon skinCluster...".format(_str_func))
                ml_skinDrivers = ml_ribbonIkHandles
                max_influences = 2
                if str_ikBase == 'hips':
                    ml_skinDrivers.append(mHipHandle)
                    max_influences = 3
                mSkinCluster = cgmMeta.validateObjArg(mc.skinCluster ([mHandle.mNode for mHandle in ml_skinDrivers],
                                                                      mSurf.mNode,
                                                                      tsb=True,
                                                                      maximumInfluences = max_influences,
                                                                      normalizeWeights = 1,dropoffRate=10),
                                                      'cgmNode',
                                                      setClass=True)
            
                mSkinCluster.doStore('cgmName', mSurf.mNode)
                mSkinCluster.doName()    
                cgmGEN.func_snapShot(vars())
                
                
                
            else:
                raise ValueError,"Not implemented {0} ik setup".format(_ikSetup)
            
            
            
            #Parent --------------------------------------------------
            #Fk...
            #if str_ikBase == 'hips':
            #    mPlug_FKon.doConnectOut("{0}.visibility".format(ml_fkJoints[1].masterGroup.mNode))
            #    ml_fkJoints[0].p_parent = mIKBaseControl
            #else:
            mPlug_FKon.doConnectOut("{0}.visibility".format(ml_fkJoints[0].masterGroup.mNode))            
            ml_blendJoints[0].parent = mRoot
            ml_ikJoints[0].parent = mIKGroup

            #Setup blend ----------------------------------------------------------------------------------
            RIGCONSTRAINT.blendChainsBy(ml_fkJoints,ml_ikJoints,ml_blendJoints,
                                        driver = mPlug_FKIK.p_combinedName,
                                        l_constraints=['point','orient'])
            
        
        
        
        #cgmGEN.func_snapShot(vars())
        return    
    except Exception,err:cgmGEN.cgmException(Exception,err)

@cgmGEN.Timer
def rig_pivotSetup(self):
    _short = self.d_block['shortName']
    _str_func = 'rig_pivotSetup'.format(_short)
    log.debug("|{0}| >>  {1}".format(_str_func,self)+ '-'*80)
    
    if not self.b_pivotSetup:
        log.info("|{0}| >> No pivot setup...".format(_str_func))
        return True
    
    mBlock = self.mBlock
    mRigNull = self.mRigNull
    mRootParent = self.mConstrainNull
    mModule = self.mModule
    _jointOrientation = self.d_orientation['str']
    _side = mBlock.atUtils('get_side')
    
    #ml_rigJoints = mRigNull.msgList_get('rigJoints')
    #ml_fkJoints = mRigNull.msgList_get('fkJoints')
    #ml_handleJoints = mRigNull.msgList_get('handleJoints')
    #ml_baseIKDrivers = mRigNull.msgList_get('baseIKDrivers')
    #ml_blendJoints = mRigNull.msgList_get('blendJoints')
    #ml_templateHandles = mBlock.msgList_get('templateHandles')
    #mPlug_globalScale = self.d_module['mPlug_globalScale']
    #mRoot = mRigNull.rigRoot

    #str_ikBase = ATTR.get_enumValueString(mBlock.mNode,'ikBase')
    
    
    
    #Changing targets - these change based on how the setup rolls through
    #mIKHandleDriver = mIKControl#...this will change with pivot
    mIKControl = mRigNull.controlIK                
    mIKHandleDriver = mIKControl
    
    #Pivot Driver ========================================================================================
    mBallPivotJoint = None
    mBallWiggleJoint = None
    
    if self.b_pivotSetup:
        mPivotResultDriver = mRigNull.getMessage('pivotResultDriver',asMeta=True)[0]
        
        _pivotSetup = ATTR.get_enumValueString(self.mBlock.mNode,'ikEnd')
        mToeIK = False
        mBallIK = False
        
        if _pivotSetup == 'foot':
            _mode = 'foot'
            

    
            ml_ikJoints = mRigNull.msgList_get('ikJoints')
            if self.mToe:
                mToeIK = ml_ikJoints.pop(-1)
                
            if self.mBall:
                mBallIK = ml_ikJoints.pop(-1)
            
            mAnkleIK = ml_ikJoints[-1]
            mBallPivotJoint = mRigNull.getMessage('pivot_ballJoint',asMeta=True)[0]
            mBallWiggleJoint = mRigNull.getMessage('pivot_ballWiggle',asMeta=True)[0]
            for mObj in mBallPivotJoint,mBallWiggleJoint:
                if mObj:
                    mObj.radius = 0
            pprint.pprint(vars())

        else:
            _mode = 'default'
            
        
        
       
        
        pprint.pprint(vars())
         
        mBlock.atBlockUtils('pivots_setup',
                            mControl = mIKControl, 
                            mRigNull = mRigNull, 
                            pivotResult = mPivotResultDriver,
                            mBallJoint= mBallPivotJoint,
                            mBallWiggleJoint = mBallWiggleJoint,
                            mToeJoint = mToeIK,
                            rollSetup = _mode,
                            front = 'front', back = 'back')#front, back to clear the toe, heel defaults
        
        if _mode == 'foot':
            log.info("|{0}| >> foot ik".format(_str_func))
            
            #Create foot IK -----------------------------------------------------------------------------
            reload(IK)
            d_ballReturn = IK.handle(mAnkleIK.mNode,mBallIK.mNode,solverType='ikSCsolver',
                                     baseName=mAnkleIK.cgmName,moduleInstance=mModule)
            mi_ballIKHandle = d_ballReturn['mHandle']
            mi_ballIKHandle.parent = mBallPivotJoint.mNode#ballIK to toe
            #mi_ballIKHandle.doSnapTo(self.mBall.mNode)
        
            #Create toe IK -------------------------------------------------------------------------------
            d_toeReturn = IK.handle(mBallIK.mNode,mToeIK.mNode,solverType='ikSCsolver',
                                    baseName=mBallIK.cgmName,moduleInstance=mModule)
            mi_toeIKHandle = d_toeReturn['mHandle']
            mi_toeIKHandle.parent = mBallWiggleJoint.mNode#toeIK to wiggle        
            #mi_toeIKHandle.doSnapTo(self.mToe.mNode)
            
            
            if mToeIK:
                mPlug_toeUpDn = cgmMeta.cgmAttr(mIKControl,'toeLift',attrType='float',defaultValue = 0,keyable = True)
                mPlug_toeTwist= cgmMeta.cgmAttr(mIKControl,'toeTwist',attrType='float',defaultValue = 0,keyable = True)                
                mPlug_toeWiggle= cgmMeta.cgmAttr(mIKControl,'toeSide',attrType='float',defaultValue = 0,keyable = True)                
                
                mPlug_toeUpDn.doConnectOut("%s.r%s"%(mToeIK.mNode,_jointOrientation[2].lower()))
                
                if _side in ['right']:
                    str_arg = "{0}.r{1} = -{2}".format(mToeIK.mNode,
                                                       _jointOrientation[0].lower(),
                                                       mPlug_toeTwist.p_combinedShortName)
                    log.debug("|{0}| >> Toe Right arg: {1}".format(_str_func,str_arg))        
                    NODEFACTORY.argsToNodes(str_arg).doBuild()
                    
                    str_arg = "{0}.r{1} = -{2}".format(mToeIK.mNode,
                                                       _jointOrientation[1].lower(),
                                                       mPlug_toeWiggle.p_combinedShortName)
                    log.debug("|{0}| >> Toe Right arg: {1}".format(_str_func,str_arg))        
                    NODEFACTORY.argsToNodes(str_arg).doBuild()                    
                else:
                    mPlug_toeTwist.doConnectOut("%s.r%s"%(mToeIK.mNode,_jointOrientation[0].lower()))
                    mPlug_toeWiggle.doConnectOut("%s.r%s"%(mToeIK.mNode,_jointOrientation[1].lower()))                

#@cgmGEN.Timer
def rig_matchSetup(self):
    try:
        _short = self.d_block['shortName']
        _str_func = 'rig_matchSetup'.format(_short)
        log.debug("|{0}| >> ...".format(_str_func))  
        
        mBlock = self.mBlock
        mRigNull = self.mRigNull
        mRootParent = self.mDeformNull
        mControlIK = mRigNull.controlIK
        mSettings = mRigNull.settings
        
        ml_rigJoints = mRigNull.msgList_get('rigJoints')
        ml_fkJoints = mRigNull.msgList_get('fkJoints')
        ml_blendJoints = mRigNull.msgList_get('blendJoints')
        ml_ikJoints = mRigNull.msgList_get('ikJoints')
        
        if not ml_ikJoints:
            return log.warning("|{0}| >> No Ik joints. Can't setup match".format(_str_func))
        
        len_fk = len(ml_fkJoints)
        len_ik = len(ml_ikJoints)
        len_blend = len(ml_blendJoints)
        
        if len_blend != len_ik and len_blend != len_fk:
            raise ValueError,"|{0}| >> All chains must equal length. fk:{1} | ik:{2} | blend:{2}".format(_str_func,len_fk,len_ik,len_blend)
        
        cgmGEN.func_snapShot(vars())
        
        mDynSwitch = mBlock.atRigModule('get_dynSwitch')
        _jointOrientation = self.d_orientation['str']
        
        
        
        #>>> FK to IK ==================================================================
        log.debug("|{0}| >> fk to ik...".format(_str_func))
        mMatch_FKtoIK = cgmRIGMETA.cgmDynamicMatch(dynObject=mControlIK,
                                                   dynPrefix = "FKtoIK",
                                                   dynMatchTargets = ml_blendJoints[-1])
        mMatch_FKtoIK.addPrematchData({'spin':0})
        
        
        
        
        
        #>>> IK to FK ==================================================================
        log.debug("|{0}| >> ik to fk...".format(_str_func))
        ml_fkMatchers = []
        for i,mObj in enumerate(ml_fkJoints):
            mMatcher = cgmRIGMETA.cgmDynamicMatch(dynObject=mObj,
                                                 dynPrefix = "IKtoFK",
                                                 dynMatchTargets = ml_blendJoints[i])        
            ml_fkMatchers.append(mMatcher)
            
        #>>> IK to FK ==================================================================
        log.debug("|{0}| >> Registration...".format(_str_func))
        
        mDynSwitch.addSwitch('snapToFK',"{0}.FKIK".format(mSettings.mNode),#[mSettings.mNode,'FKIK'],
                             0,
                             ml_fkMatchers)
        
        mDynSwitch.addSwitch('snapToIK',"{0}.FKIK".format(mSettings.mNode),#[mSettings.mNode,'FKIK'],
                             1,
                             [mMatch_FKtoIK])        
        
    except Exception,err:cgmGEN.cgmException(Exception,err)
    


@cgmGEN.Timer
def rig_cleanUp(self):
    _short = self.d_block['shortName']
    _str_func = 'rig_cleanUp'
    log.debug("|{0}| >>  {1}".format(_str_func,self)+ '-'*80)
    
    mBlock = self.mBlock
    mRigNull = self.mRigNull
    mSettings = mRigNull.settings
    mRoot = mRigNull.rigRoot
    if not mRoot.hasAttr('cgmAlias'):
        mRoot.addAttr('cgmAlias','root')
        
    mRootParent = self.mConstrainNull
    mMasterControl= self.d_module['mMasterControl']
    mMasterDeformGroup= self.d_module['mMasterDeformGroup']    
    mMasterNull = self.d_module['mMasterNull']
    mModuleParent = self.d_module['mModuleParent']
    mPlug_globalScale = self.d_module['mPlug_globalScale']
    
    ml_controlsToSetup = []
    for msgLink in ['rigJoints','controlIK']:
        ml_buffer = mRigNull.msgList_get(msgLink)
        if ml_buffer:
            log.debug("|{0}| >>  Found: {1}".format(_str_func,msgLink))            
            ml_controlsToSetup.extend(ml_buffer)
    
    if not self.mConstrainNull.hasAttr('cgmAlias'):
        self.mConstrainNull.addAttr('cgmAlias','{0}_rootNull'.format(self.d_module['partName']))
        
        
    #>>  DynParentGroups - Register parents for various controls ============================================
    ml_baseDynParents = []
    ml_endDynParents = self.ml_dynParentsAbove + self.ml_dynEndParents# + [mRoot]
    ml_ikDynParents = []
    
    #Lever =================================================================================================
    if self.b_lever:
        log.debug("|{0}| >> Lever Setup...".format(_str_func))
        #mLeverRigJnt = mRigNull.getMessage('leverRig',asMeta=True)[0]
        mLeverFK = mRigNull.leverFK
        mLimbRoot = mRigNull.limbRoot
        
        ml_targetDynParents = [mLeverFK, self.mConstrainNull] + ml_endDynParents
        
        mDynGroup = cgmRigMeta.cgmDynParentGroup(dynChild=mLimbRoot.mNode,dynMode=0)
        
        log.debug("|{0}| >>  Root Targets...".format(_str_func,mLimbRoot))
        pprint.pprint(ml_targetDynParents)
        
        if not mLimbRoot.hasAttr('cgmAlias'):
            mLimbRoot.addAttr('cgmAlias','{0}_limbRoot'.format(self.d_module['partName']))
            
        if not mLeverFK.hasAttr('cgmAlias'):
            mLeverFK.addAttr('cgmAlias','{0}_lever'.format(self.d_module['partName']))
                
        for mTar in ml_targetDynParents:
            mDynGroup.addDynParent(mTar)
        mDynGroup.rebuild()
        #mDynGroup.dynFollow.p_parent = self.mConstrainNull
        
        log.debug(cgmGEN._str_subLine)        
        ml_baseDynParents.append(mLeverFK)
        ml_baseDynParents.append(mLimbRoot)
    else:
        ml_baseDynParents.append(mRoot)
        
    
    #...Root controls ================================================================================
    log.debug("|{0}| >>  Root: {1}".format(_str_func,mRoot))
    
    ml_targetDynParents = [self.mConstrainNull]
    
    if not mRoot.hasAttr('cgmAlias'):
        mRoot.addAttr('cgmAlias','{0}_root'.format(self.d_module['partName']))
        
    ml_targetDynParents.extend(self.ml_dynEndParents)
    mDynGroup = cgmRigMeta.cgmDynParentGroup(dynChild=mRoot.mNode,dynMode=0)

    log.debug("|{0}| >>  Root Targets...".format(_str_func,mRoot))
    pprint.pprint(ml_targetDynParents)
    
    for mTar in ml_targetDynParents:
        mDynGroup.addDynParent(mTar)
    mDynGroup.rebuild()
    #mDynGroup.dynFollow.p_parent = self.mConstrainNull
    
    log.debug(cgmGEN._str_subLine)
    
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
        
        ml_targetDynParents = ml_baseDynParents + [self.mConstrainNull] + ml_endDynParents
        
        ml_targetDynParents.append(self.md_dynTargetsParent['world'])
        ml_targetDynParents.extend(mHandle.msgList_get('spacePivots',asMeta = True))
    
        mDynGroup = cgmRigMeta.cgmDynParentGroup(dynChild=mHandle,dynMode=0)
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
    
        mDynGroup = cgmRigMeta.cgmDynParentGroup(dynChild=mHandle,dynMode=0)
        #mDynGroup.dynMode = 2
    
        for mTar in ml_targetDynParents:
            mDynGroup.addDynParent(mTar)
        mDynGroup.rebuild()
        #mDynGroup.dynFollow.p_parent = self.mConstrainNull
        
        log.debug("|{0}| >>  IK Mid targets...".format(_str_func,mRoot))
        pprint.pprint(ml_targetDynParents)                
        log.debug(cgmGEN._str_subLine)
    
    
    """
    #...rigjoints =================================================================================================
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
        
        mDynGroup = cgmRigMeta.cgmDynParentGroup(dynChild=mObj.mNode)
        mDynGroup.dynMode = 2
        
        for mTar in ml_targetDynParents:
            mDynGroup.addDynParent(mTar)
        
        mDynGroup.rebuild()
        
        mDynGroup.dynFollow.p_parent = mRoot
    """
    
    #...fk controls =================================================================================================
    log.debug("|{0}| >>  FK...".format(_str_func))                
    ml_fkJoints = self.mRigNull.msgList_get('fkJoints')
    
    for i,mObj in enumerate(ml_fkJoints):
        log.debug("|{0}| >>  FK: {1}".format(_str_func,mObj))                        
        ml_targetDynParents = copy.copy(ml_baseDynParents)
        ml_targetDynParents.append(self.mConstrainNull)
        
        mParent = mObj.masterGroup.getParent(asMeta=True)
        if not mParent.hasAttr('cgmAlias'):
            mParent.addAttr('cgmAlias','{0}_base'.format(mObj.p_nameBase))
        
        if i == 0:
            ml_targetDynParents.append(mParent)
            _mode = 2            
        else:
            ml_targetDynParents.insert(0,mParent)
            _mode = 1
            
        
        ml_targetDynParents.extend(ml_endDynParents)
        ml_targetDynParents.extend(mObj.msgList_get('spacePivots',asMeta = True))

        mDynGroup = cgmRigMeta.cgmDynParentGroup(dynChild=mObj.mNode, dynMode=_mode)# dynParents=ml_targetDynParents)
        #mDynGroup.dynMode = 2
    
        for mTar in ml_targetDynParents:
            mDynGroup.addDynParent(mTar)
        mDynGroup.rebuild()
        
        if i == 0:
            mDynGroup.dynFollow.p_parent = mRoot    
        
        log.debug("|{0}| >>  FK targets: {1}...".format(_str_func,mObj))
        pprint.pprint(ml_targetDynParents)                
        log.debug(cgmGEN._str_subLine)    
    
    
    #Lock and hide =================================================================================
    log.debug("|{0}| >> lock and hide..".format(_str_func))
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
            
    #Lock and hide =================================================================================
    log.debug("|{0}| >> lock and hide..".format(_str_func))
    
    
    #Close out ===============================================================================================
    mRigNull.version = self.d_block['buildVersion']
    mBlock.blockState = 'rig'
    
    #cgmGEN.func_snapShot(vars())
    return



    

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
    mSettings = mRigNull.settings
    mPuppetSettings = self.d_module['mMasterControl'].controlSettings
    
    directProxy = mBlock.proxyDirect
    
    _side = BLOCKUTILS.get_side(self.mBlock)
    ml_proxy = []
    
    ml_rigJoints = mRigNull.msgList_get('rigJoints',asMeta = True)
    ml_templateHandles = mBlock.msgList_get('templateHandles',asMeta = True)
    
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
        
    #Figure out our rig joints --------------------------------------------------------
    _str_rigSetup = mBlock.getEnumValueString('rigSetup')
    _str_ikEnd = mBlock.getEnumValueString('ikEnd')
    
    mToe = False
    mBall = False
    int_handleEndIdx = -1
    
    if _str_ikEnd in ['foot']:
        l= []
        
        if mBlock.hasEndJoint:
            mToe = ml_rigJoints.pop(-1)
            log.debug("|{0}| >> mToe: {1}".format(_str_func,mToe))
            int_handleEndIdx -=1
        if mBlock.hasBallJoint:
            mBall = ml_rigJoints.pop(-1)
            log.debug("|{0}| >> mBall: {1}".format(_str_func,mBall))        
            int_handleEndIdx -=1
        
        if mBall or mToe:
            mEnd = ml_rigJoints.pop(-1)
            log.debug("|{0}| >> mEnd: {1}".format(_str_func,mEnd))        
            int_handleEndIdx -=1
    elif _str_rigSetup == 'digit':
        if mBlock.hasEndJoint:
            pass
            #mEnd = ml_rigJoints.pop(-1)
            
    
    log.debug("|{0}| >> Handles Targets: {1}".format(_str_func,ml_rigJoints))            
    log.debug("|{0}| >> End idx: {1} | {2}".format(_str_func,int_handleEndIdx,
                                                   ml_rigJoints[int_handleEndIdx]))                
        
    # Create ---------------------------------------------------------------------------
    ml_segProxy = cgmMeta.validateObjListArg(self.atBuilderUtils('mesh_proxyCreate',
                                                                 ml_rigJoints),
                                             'cgmObject')    
    
    
    #Proxyhelper-----------------------------------------------------------------------------------
    if _str_rigSetup != 'digit':
        log.debug("|{0}| >> proxyHelper... ".format(_str_func))
        mProxyHelper = ml_templateHandles[-1].getMessage('proxyHelper',asMeta=1)
        if mProxyHelper:
            log.debug("|{0}| >> proxyHelper... ".format(_str_func))
            mProxyHelper = mProxyHelper[0]
            mNewShape = mProxyHelper.doDuplicate(po=False)
            mNewShape.parent = False
            ml_segProxy.append(mNewShape)
            ml_rigJoints.append(ml_rigJoints[-1])
            
            
        # Foot --------------------------------------------------------------------------
        elif ml_templateHandles[-1].getMessage('pivotHelper'):
            ml_rigJoints.append(mEnd)#...add this back
            mPivotHelper = ml_templateHandles[-1].pivotHelper
            log.debug("|{0}| >> foot ".format(_str_func))
            
            #make the foot geo....
            l_targets = [ml_templateHandles[-1].loftCurve.mNode]
            
            mBaseCrv = mPivotHelper.doDuplicate(po=False)
            mBaseCrv.parent = False
            mShape2 = False
            
            for mChild in mBaseCrv.getChildren(asMeta=True):
                if mChild.cgmName == 'topLoft':
                    mShape2 = mChild.doDuplicate(po=False)
                    mShape2.parent = False
                    l_targets.append(mShape2.mNode)
                mChild.delete()
                    
            l_targets.append(mBaseCrv.mNode)
            reload(BUILDUTILS)
            _mesh = BUILDUTILS.create_loftMesh(l_targets, name="{0}".format('foot'), divisions=1, degree=1)
            
            _l_combine = []
            for i,crv in enumerate([l_targets[0],l_targets[-1]]):
                _res = mc.planarSrf(crv,po=1,ch=True,d=3,ko=0, tol=.01,rn=0)
                log.info(_res)
                _inputs = mc.listHistory(_res[0],pruneDagObjects=True)
                _tessellate = _inputs[0]        
                _d = {'format':1,#Fit
                      'polygonType':1,#'quads',
                      #'vNumber':1,
                      #'uNumber':1
                      }
                for a,v in _d.iteritems():
                    ATTR.set(_tessellate,a,v)
                _l_combine.append(_res[0])
                _mesh = mc.polyUnite([_mesh,_res[0]],ch=False,mergeUVSets=1,n = "{0}_proxy_geo".format('foot'))[0]
                #_mesh = mc.polyMergeVertex(_res[0], d= .0001, ch = 0, am = 1 )
            
            
            mBaseCrv.delete()
            if mShape2:mShape2.delete()
            
            mMesh = cgmMeta.validateObjArg(_mesh)
            
            #...cut it up
            if mBall:
                _bool_size = 50
                _bool_divs = 80
                #Heel.-----------------------------------------------------------------------------------
                log.debug("|{0}| >> heel... ".format(_str_func))                        
                plane = mc.polyPlane(axis =  MATH.get_obj_vector(mBall.mNode, 'z+'),
                                     width = _bool_size, height = _bool_size,
                                     subdivisionsX=_bool_divs,subdivisionsY=_bool_divs,
                                     ch=0)
                mPlane = cgmMeta.validateObjArg(plane[0])
                mPlane.doSnapTo(mBall.mNode,rotation=False)
                
                mMeshHeel = mMesh.doDuplicate(po=False)
                
                #heel = mc.polyCBoolOp(plane[0], mMeshHeel.mNode, op=3,ch=0, classification = 1)
                heel = mel.eval('polyCBoolOp -op 3-ch 0 -classification 1 {0} {1};'.format(mPlane.mNode, mMeshHeel.mNode))
                
                mMeshHeel = cgmMeta.validateObjArg(heel[0])
                ml_segProxy.append(mMeshHeel)
                

                #toe -----------------------------------------------------------------------------------
                if mToe:
                    #ball -----------------------------------------------------------------------------------
                    log.debug("|{0}| >> ball... ".format(_str_func))            
                    plane = mc.polyPlane(axis =  MATH.get_obj_vector(mBall.mNode, 'z-'),
                                         subdivisionsX=_bool_divs,subdivisionsY=_bool_divs,                                 
                                         width = _bool_size, height = _bool_size, ch=0)
                    mPlane = cgmMeta.validateObjArg(plane[0])
                    mPlane.doSnapTo(mBall.mNode,rotation=False)
                    mMeshBall = mMesh.doDuplicate(po=False)
                
                    #ball = mc.polyCBoolOp(plane[0], mMeshBall.mNode, op=3,ch=0, classification = 1)
                    ball = mel.eval('polyCBoolOp -op 3-ch 0 -classification 1 {0} {1};'.format(mPlane.mNode, mMeshBall.mNode))
                    mMeshBall = cgmMeta.validateObjArg(ball[0])
                    
                    
                    #resplit ball...
                    """
                    log.debug("|{0}| >> ball resplit... ".format(_str_func))            
                    
                    planeToe = mc.polyPlane(axis =  MATH.get_obj_vector(mToe.mNode, 'z-'),
                                            subdivisionsX=_bool_divs,subdivisionsY=_bool_divs,                                 
                                        width = _bool_size, height = _bool_size, ch=0)
                    mPlane = cgmMeta.validateObjArg(planeToe[0])
                    mPlane.doSnapTo(mToe.mNode,rotation=False)
                    mMeshBallDup = mMeshBall.doDuplicate(po=False)
                    #mc.select(cl=1)
                    ball2 = mel.eval('polyCBoolOp -op 3-ch 0 {0} {1};'.format(mPlane.mNode, mMeshBallDup.mNode))
                    mMeshBall.delete()
                    mMeshBall = cgmMeta.validateObjArg(ball2[0])"""
                    
                    
                    log.debug("|{0}| >> toe... ".format(_str_func))
                    planeToe = mc.polyPlane(axis =  MATH.get_obj_vector(mToe.mNode, 'z-'),
                                         subdivisionsX=_bool_divs,subdivisionsY=_bool_divs,                                 
                                         width = _bool_size, height = _bool_size, ch=0)
                    mPlane = cgmMeta.validateObjArg(planeToe[0])
                    mPlane.doSnapTo(mToe.mNode,rotation=False)
                    mMeshToe = mMesh.doDuplicate(po=False)
                
                    #ball = mc.polyCBoolOp(plane[0], mMeshBall.mNode, op=3,ch=0, classification = 1)
                    toe = mel.eval('polyCBoolOp -op 3-ch 0 -classification 1 {0} {1};'.format(mPlane.mNode, mMeshToe.mNode))
                    mMeshToe = cgmMeta.validateObjArg(toe[0])
                    
                    
                    ml_segProxy.append(mMeshBall)
                    ml_rigJoints.append(mBall)
                    ml_segProxy.append(mMeshToe)
                    ml_rigJoints.append(mToe)
                else:
                    #ball -----------------------------------------------------------------------------------
                    log.debug("|{0}| >> ball... ".format(_str_func))            
                    plane = mc.polyPlane(axis =  MATH.get_obj_vector(mBall.mNode, 'z-'),
                                         subdivisionsX=_bool_divs,subdivisionsY=_bool_divs,                                 
                                         width = _bool_size, height = _bool_size, ch=0)
                    mPlane = cgmMeta.validateObjArg(plane[0])
                    mPlane.doSnapTo(mBall.mNode,rotation=False)
                    mMeshBall = mMesh.doDuplicate(po=False)
                
                    #ball = mc.polyCBoolOp(plane[0], mMeshBall.mNode, op=3,ch=0, classification = 1)
                    ball = mel.eval('polyCBoolOp -op 3-ch 0 -classification 1 {0} {1};'.format(mPlane.mNode, mMeshBall.mNode))
                    mMeshBall = cgmMeta.validateObjArg(ball[0])
                    ml_segProxy.append(mMeshBall)
                    ml_rigJoints.append(mBall)                    
                    
                #mMesh.p_parent=False
                mMesh.delete()
                
    if directProxy:
        log.debug("|{0}| >> directProxy... ".format(_str_func))
        _settings = self.mRigNull.settings.mNode
        

    for i,mGeo in enumerate(ml_segProxy):
        log.info("{0} : {1}".format(mGeo, ml_rigJoints[i]))
        mGeo.parent = ml_rigJoints[i]
        #ATTR.copy_to(ml_rigJoints[0].mNode,'cgmName',mGeo.mNode,driven = 'target')
        mGeo.doStore('cgmName',self.d_module['partName'])
        
        mGeo.addAttr('cgmIterator',i+1)
        mGeo.addAttr('cgmType','proxyGeo')
        mGeo.doName()
        
        if directProxy:
            CORERIG.shapeParent_in_place(ml_rigJoints[i].mNode,mGeo.mNode,True,True)
            CORERIG.colorControl(ml_rigJoints[i].mNode,_side,'main',directProxy=True)
            for mShape in ml_rigJoints[i].getShapes(asMeta=True):
                #mShape.overrideEnabled = 0
                mShape.overrideDisplayType = 0
                ATTR.connect("{0}.visDirect".format(_settings), "{0}.overrideVisibility".format(mShape.mNode))    
    for mProxy in ml_segProxy:
        CORERIG.colorControl(mProxy.mNode,_side,'main',transparent=False,proxy=True)
        
        mc.makeIdentity(mProxy.mNode, apply = True, t=1, r=1,s=1,n=0,pn=1)

        #Vis connect -----------------------------------------------------------------------
        mProxy.overrideEnabled = 1
        ATTR.connect("{0}.proxyVis".format(mPuppetSettings.mNode),"{0}.visibility".format(mProxy.mNode) )
        ATTR.connect("{0}.proxyLock".format(mPuppetSettings.mNode),"{0}.overrideDisplayType".format(mProxy.mNode) )
        
        for mShape in mProxy.getShapes(asMeta=1):
            str_shape = mShape.mNode
            mShape.overrideEnabled = 0
            ATTR.connect("{0}.proxyLock".format(mPuppetSettings.mNode),"{0}.overrideDisplayTypes".format(str_shape) )
            
        
    mRigNull.msgList_connect('proxyMesh', ml_segProxy)





















