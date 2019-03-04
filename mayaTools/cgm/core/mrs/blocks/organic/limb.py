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
log.setLevel(logging.INFO)

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
#reload(MODULECONTROL)
import cgm.core.rig.general_utils as CORERIGGEN
import cgm.core.lib.math_utils as MATH
import cgm.core.lib.transform_utils as TRANS
import cgm.core.lib.distance_utils as DIST
import cgm.core.lib.attribute_utils as ATTR
import cgm.core.tools.lib.snap_calls as SNAPCALLS
import cgm.core.classes.NodeFactory as NODEFACTORY
#reload(NODEFACTORY)
from cgm.core import cgm_RigMeta as cgmRigMeta
import cgm.core.lib.list_utils as LISTS
import cgm.core.lib.nameTools as NAMETOOLS
import cgm.core.lib.locator_utils as LOC
import cgm.core.rig.create_utils as RIGCREATE
#reload(NAMETOOLS)
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
import cgm.core.mrs.lib.shared_dat as BLOCKSHARE
import cgm.core.mrs.lib.builder_utils as BUILDUTILS
import cgm.core.lib.shapeCaster as SHAPECASTER
from cgm.core.cgmPy import validateArgs as VALID

import cgm.core.cgm_RigMeta as cgmRIGMETA
#reload(CURVES)
#reload(BUILDUTILS)
#reload(DIST)
#reload(RIGCONSTRAINT)

# From cgm ==============================================================
from cgm.core import cgm_Meta as cgmMeta

#=============================================================================================================
#>> Block Settings
#=============================================================================================================
__version__ = 'alpha.1.03012019'
__autoTemplate__ = False
__dimensions = [15.2, 23.2, 19.7]#...cm
__menuVisible__ = True
__sizeMode__ = 'castNames'

#__baseSize__ = 1,1,10

__l_rigBuildOrder__ = ['rig_dataBuffer',
                       'rig_skeleton',
                       'rig_shapes',
                       'rig_controls',
                       'rig_frame',
                       'rig_blendFrame',
                       'rig_pivotSetup',
                       'rig_segments',
                       'rig_cleanUp']

d_wiring_skeleton = {'msgLinks':['moduleTarget'],
                     'msgLists':['moduleJoints','skinJoints']}
d_wiring_prerig = {'msgLinks':['prerigNull','noTransPrerigNull'],
                   'msgLists':['prerigHandles']}
d_wiring_template = {'msgLinks':['templateNull','noTransTemplateNull','prerigLoftMesh','orientHelper'],
                     'msgLists':['templateHandles']}
d_wiring_define = {'msgLinks':['defineNull']}

#>>>Profiles =====================================================================================================
d_build_profiles = {
    'unityLow':{'default':{'numRoll':0,},
                'finger':{'numRoll':0},
                'thumb':{'numRoll':0},
                },
    'unityMed':{'default':{'numRoll':1},
               'finger':{'numRoll':0},
               'thumb':{'numRoll':0},
               },
    'unityHigh':{'default':{'numRoll':3},
                'finger':{'numRoll':0},
                'thumb':{'numRoll':0},
                           },
    'feature':{'default':{'numRoll':3,},
               'leg':{'hasBallJoint':True,
                      'hasEndJoint':True,}}}

d_block_profiles = {
'default':{},
'quadRear':{
    'addCog':False,
    'cgmName':'quadRear',
    'loftShape':'circle',
    'loftSetup':'default',
    'settingsPlace':'end',
    'settingsDirection':'down',
    'ikSetup':'rp',
    'ikEnd':'pad',
    'buildLeverEnd':True,
    'numControls':4,
    'numSubShapers':3,
    'ikRPAim':'default',
    'rigSetup':'default',           
    'mainRotAxis':'out',
    'buildBaseLever':False,
    'hasLeverJoint':False,
    'hasBallJoint':False,
    'hasEndJoint':True,
    'nameList':['hip','knee','ankle','ball','toe'],
    'baseAim':[0,-1,0],
    'baseUp':[0,0,1],
    'baseSize':[11.6,8,79],
    'baseDat':{'rp':[0,0,1],'up':[0,0,1],'lever':[1,0,0]},
    },
'quadFront':{
    'addCog':False,
    'attachPoint':'end',
    'cgmName':'quadFront',
    'loftShape':'circle',
    'loftSetup':'default',
    'settingsPlace':'end',
    'settingsDirection':'down',
    'ikSetup':'rp',
    'ikEnd':'pad',
    'buildLeverEnd':True,
    'numControls':4,
    'numSubShapers':3,
    'ikRPAim':'default',
    'rigSetup':'default',           
    'mainRotAxis':'out',
    'buildBaseLever':True,
    'hasLeverJoint':True,
    'hasBallJoint':False,
    'hasEndJoint':True,
    'nameList':['shoulder','knee','wrist','ball','end'],
    'baseAim':[0,-1,0],
    'baseUp':[0,0,1],
    'baseSize':[11.6,8,79],
    'baseDat':{'rp':[0,0,-1],'up':[0,0,1],'lever':[1,0,0]},
    },    

'leg':{
    'numSubShapers':2,
    'addCog':False,
    'cgmName':'leg',
    'loftShape':'circle',
    'loftSetup':'default',
    'settingsPlace':'end',
    'settingsDirection':'down',
    'ikSetup':'rp',
    'ikEnd':'foot',
    'buildLeverEnd':False,           
    'numControls':3,
    'numSubShapers':3,
    'ikRPAim':'default',
    'rigSetup':'default',           
    'mainRotAxis':'out',
    'buildBaseLever':False,
    'hasLeverJoint':False,
    'hasBallJoint':True,
    'hasEndJoint':True,
    'nameList':['hip','knee','ankle','ball','toe'],
    'baseAim':[0,-1,0],
    'baseUp':[0,0,1],
    'baseSize':[11.6,13,70],
    'baseDat':{'rp':[0,0,1],'up':[0,0,1],'lever':[1,0,0]},
    'loftList':['wideNeg','wideDown','circle'],
    'loftShapeEnd':'wideUp',
       },

'crab':{
    'addCog':False,
    'cgmName':'crabLeg',
    'loftShape':'squircleDiamond',
    'loftSetup':'default',
    'settingsPlace':'end',
    'settingsDirection':'down',
    'ikSetup':'rp',
    'buildLeverEnd':True,
    'settingsDirection':'up',
    'ikEnd':'bank',
    'numControls':4,
    'numSubShapers':3,
    'ikRPAim':'default',
    'rigSetup':'default',
    'mainRotAxis':'out',
    'buildBaseLever':False,
    'hasLeverJoint':False,
    'hasBallJoint':False,
    'hasEndJoint':True,
    'nameList':['hip','knee','ankle','ball','toe'],
    'baseAim':[-1,-1,0],
    'baseUp':[0,0,1],
    'baseSize':[11.6,13,70],
    'baseDat':{'rp':[-1,0,0],'up':[-1,0,0],'lever':[1,0,0]},
          },

'arm':{
    'numSubShapers':2,
    'addCog':False,
    'attachPoint':'end',
    'cgmName':'arm',
    'loftShape':'circle',
    'loftSetup':'default',
    'settingsPlace':'end',
    'ikSetup':'rp',
    'ikEnd':'hand',
    'numSubShapers':3,
    'mainRotAxis':'up',
    'numControls':3,
    'ikRPAim':'free',
    'buildLeverBase':True,
    'hasLeverJoint':True,
    'hasBallJoint':False,
    'hasEndJoint':True,
    'rigSetup':'default',
    'nameList':['clav','shoulder','elbow','wrist'],
    'baseAim':[-1,0,0],
    'baseSize':[14,9,76],
    'baseDat':{'lever':[1,0,0],'rp':[0,0,-1],'up':[0,1,0]},
    'loftList':['circle','widePos','squircle'],
       },
'wingBase':{'numSubShapers':2,
            'addCog':False,
            'attachPoint':'end',
            'cgmName':'wing',
            'loftShape':'widePos',
            'loftSetup':'default',
            'settingsPlace':'end',
            'ikSetup':'rp',
            'ikEnd':'none',
            'numSubShapers':3,
            'mainRotAxis':'up',
            'numControls':3,
            'ikRPAim':'free',
            'buildLeverBase':True,
            'hasLeverJoint':True,
            'hasBallJoint':False,
            'hasEndJoint':True,
            'rigSetup':'default',
            'nameList':['clav','shoulder','elbow','wrist'],
            'baseAim':[-1,0,0],
            'baseSize':[14,9,76],
            'baseDat':{'lever':[1,0,0],'rp':[0,0,-1],'up':[0,1,0]},
            },
'finger':{'numSubShapers':2,
          'addCog':False,
          'attachPoint':'end',
          'loftShape':'wideDown',
          'loftSetup':'loftList',
          'loftList':['wideDown','wideDown','wideDown','digit'],                            
          'settingsPlace':'end',
          'ikSetup':'rp',
          'ikEnd':'tipBase',
          'numControls':4,
          'numRoll':0,
          'ikRPAim':'default',              
          'rigSetup':'digit',
          'mainRotAxis':'out',                             
          'offsetMode':'default',
          'buildLeverBase':True,
          'hasLeverJoint':True,
          'hasBallJoint':False,
          'followParentBank':True,              
          'hasEndJoint':True,
          'nameList':['index'],
          'scaleSetup':False,
          'baseAim':[0,0,1],
          'baseUp':[0,1,0],
          'baseSize':[3,2.5,13],
          'baseDat':{'lever':[0,0,-1],'rp':[0,1,0],'up':[0,1,0]},
          },
'toe':{'numSubShapers':1,
       'addCog':False,
       'attachPoint':'end',
       'loftShape':'wideDown',
       'loftSetup':'default',
       'settingsPlace':'end',
       'ikSetup':'rp',
       'ikEnd':'tipBase',
       'numControls':4,
       'numRoll':0,
       'ikRPAim':'default',
       'rigSetup':'digit',
       'mainRotAxis':'out',
       'numSpacePivots':0,
       'offsetMode':'default',
       'followParentBank':True,           
       'buildLeverBase':False,
       'hasLeverJoint':False,
       'hasBallJoint':False,
       'hasEndJoint':True,
       'nameList':['index'],
       'scaleSetup':False,
       'baseAim':[0,0,1],
       'baseUp':[0,1,0],
       'baseSize':[3,2.5,13],
       'baseDat':{'lever':[0,0,-1],'rp':[0,1,0],'up':[0,1,0]},
       },

'thumb':{'numSubShapers':2,
          'addCog':False,
          'attachPoint':'end',
          'loftShape':'wideDown',
          'loftSetup':'loftList',
          'settingsPlace':'end',
          'ikSetup':'rp',
          'ikEnd':'tipBase',
          'numControls':4,
          'numRoll':0,
          'ikRPAim':'default',              
          'rigSetup':'digit',
          'mainRotAxis':'out',
          'followParentBank':True,              
          'offsetMode':'default',
          'buildLeverBase':False,
          'hasLeverJoint':False,
          'hasBallJoint':False,
          'hasEndJoint':True,
          'nameList':['thumb'],
          'scaleSetup':False,
          'baseAim':[1,0,0],
          'baseUp':[0,1,0],
          'baseSize':[3,2.5,13],
          'loftList':['wideNeg','wideDown','wideDown','digit'],              
          'baseDat':{'lever':[0,0,-1],'rp':[0,1,0],'up':[0,1,0]},              
          },    

'nub':{'numSubShapers':2,
       'addCog':False,
       'attachPoint':'end',
       'cgmName':'nub',
       'loftShape':'wideDown',
       'loftSetup':'default',
       'settingsPlace':'end',
       'ikSetup':'rp',
       'ikEnd':'tipEnd',
       'numControls':2,
       'numRoll':0,
       'ikRPAim':'default',
       'rigSetup':'digit',
       'mainRotAxis':'out',
       'hasEndJoint':False,
       'followParentBank':True,           
       'buildLeverBase':False,
       'hasLeverJoint':False,
       'hasLeverJoint':False,
       'hasBallJoint':False,
       'nameList':['nub'],
       'scaleSetup':False,
       'baseAim':[0,0,1],
       'baseUp':[0,1,0],
       'baseSize':[10,10,20],
       'baseDat':{'lever':[0,0,-1],'rp':[0,1,0],'up':[0,1,0]},                               
       },    

   }

#>>>Attrs =====================================================================================================
l_attrsStandard = ['side',
                   'position',
                   #'baseUp',
                   'baseAim',
                   'baseDat',
                   'addCog',
                   'nameList',
                   #'namesHandles',
                   #'namesJoints',
                   'attachPoint',
                   'loftSides',
                   'loftDegree',
                   'loftList',
                   'loftSplit',
                   'loftShape',
                   'loftReverseNormal',
                   'ikSetup',
                   'scaleSetup',
                   'numControls',
                   'numRoll',
                   'offsetMode',
                   'settingsDirection',
                   'numSpacePivots',
                   'ikOrientToWorld',
                   'squashMeasure',
                   'squash',
                   'squashExtraControl',
                   'squashFactorMax',
                   'squashFactorMin',
                   'ribbonAim',
                   'ribbonParam',
                   'visRotatePlane',
                   #'ribbonConnectBy': 'constraint:matrix',
                   'segmentMidIKControl',
                   'spaceSwitch_direct',
                   'proxyGeoRoot',
                   'proxyDirect',
                   'numSubShapers',#...with limb this is the sub shaper count as you must have one per handle
                   #'buildProfile',
                   'moduleTarget']

d_attrsToMake = {'visMeasure':'bool',
                 'followParentBank':'bool',                 
                 'proxyShape':'cube:sphere:cylinder',
                 'mainRotAxis':'up:out',
                 'settingsPlace':'start:end',
                 'ikRPAim':'default:free',
                 'buildLeverEnd':'bool',
                 'blockProfile':'string',#':'.join(d_block_profiles.keys()),
                 'rigSetup':'default:digit',#...this is to account for some different kinds of setup
                 'ikEnd':'default:bank:foot:pad:hand:tipBase:tipEnd:tipMid:tipCombo:proxy',
                 #'ikBase':'none:fkRoot',
                 'hasLeverJoint':'bool',
                 'buildLeverBase':'bool',#...fkRoot is our clav like setup
                 'hasEndJoint':'bool',
                 'hasBallJoint':'bool',
                 #'ikEndIndex':'int',
                 'shapersAim':'toEnd:chain',
                 'loftSetup':'default:loftList',
                 'loftShapeStart':BLOCKSHARE._d_attrsTo_make['loftShape'],
                 'loftShapeEnd':BLOCKSHARE._d_attrsTo_make['loftShape'],
                 
                 #'buildSpacePivots':'bool',
                 #'nameIter':'string',
                 #'numControls':'int',
                 #'numSubShapers':'int',
                 #'numJoints':'int'
                 }

d_defaultSettings = {'version':__version__,
                     #'baseSize':MATH.get_space_value(__dimensions[1]),
                     'numControls': 3,
                     'loftSetup':0,
                     'loftShape':0,
                     'buildLeverEnd':False,
                     'ikOrientToWorld':True,
                     'numSubShapers':3,
                     'followParentBank':True,                     
                     'ikEnd':'tipEnd',
                     'ikRPAim':'default',
                     'settingsDirection':'up',
                     'numSpacePivots':2,
                     'settingsPlace':1,
                     'hasEndJoint':True,
                     'loftList':['square','circle','square'],
                     'loftShapeStart':'squareRoundUp',
                     'loftShapeEnd':'wideUp',
                     'loftReverseNormal':True,
                     'loftSides': 10,
                     'loftSplit':1,
                     'loftDegree':'linear',
                     'numRoll':0,
                     'ribbonParam':'blend',
                     'proxyDirect':True,
                     'nameList':['',''],
                     'blockProfile':'leg',
                     'attachPoint':'base',
                     'proxyGeoRoot':1,
                     'buildSpacePivots':True,
                     'visRotatePlane':True,
                     'squashMeasure':'arcLength',
                     'squash':'both',
                     'squashExtraControl':True,
                     'ribbonAim':'stable',
                     'squashFactorMax':1.0,
                     'squashFactorMin':0.0,
                     'segmentMidIKControl':True,
                     'visRotatePlane':False,
                     }
_l_hiddenAttrs = ['baseAim','baseSize','baseUp']

#d_preferredAngles = {'head':[0,-10, 10]}#In terms of aim up out for orientation relative values, stored left, if right, it will invert
#d_rotationOrders = {'head':'yxz'}


#=============================================================================================================
#>> Define
#=============================================================================================================
def define(self):
    try:
        _str_func = 'define'    
        log.debug("|{0}| >> ...".format(_str_func)+ '-'*80)
        log.debug(self)
        
        _short = self.mNode
        
        for a in _l_hiddenAttrs:
            if ATTR.has_attr(_short,a):
                ATTR.set_hidden(_short,a,True)
        
        ATTR.set_min(_short, 'numControls', 2)
        ATTR.set_min(_short, 'numRoll', 0)
        ATTR.set_min(_short, 'loftSides', 3)
        ATTR.set_min(_short, 'loftSplit', 1)
        ATTR.set_min(_short, 'numSubShapers', 0)
        
        ATTR.set_alias(_short,'sy','blockScale')    
        self.setAttrFlags(attrs=['sx','sz','sz'])
        self.doConnectOut('sy',['sx','sz'])    
        
        _shapes = self.getShapes()
        if _shapes:
            log.debug("|{0}| >>  Removing old shapes...".format(_str_func))        
            mc.delete(_shapes)
            defineNull = self.getMessage('defineNull')
            #noTransform = self.getMessage('noTransDefineNull')
            if defineNull:
                log.debug("|{0}| >>  Removing old defineNull...".format(_str_func))
                mc.delete(defineNull)
            #if noTransform:
            #    log.debug("|{0}| >>  Removing old defineNoTransformNull...".format(_str_func))
            #    mc.delete(noTransform)
            self.verify()
            
                
        _size = self.atUtils('defineSize_get')
            
        #_sizeSub = _size / 2.0
        log.debug("|{0}| >>  Size: {1}".format(_str_func,_size))        
        _crv = CURVES.create_fromName(name='locatorForm',
                                      direction = 'z+', size = _size * 2.0)
        
        SNAP.go(_crv,self.mNode,)
        CORERIG.override_color(_crv, 'white')
        CORERIG.shapeParent_in_place(self.mNode,_crv,False)
        mHandleFactory = self.asHandleFactory()
        self.addAttr('cgmColorLock',True,lock=True,hidden=1)
        mDefineNull = self.atUtils('stateNull_verify','define')
        
        #mNoTransformNull = self.atUtils('noTransformNull_verify','define')
        
        
        """
        #Rotate Group ==================================================================
        mRotateGroup = cgmMeta.validateObjArg(mDefineNull.doGroup(True,False,
                                                                  asMeta=True,
                                                                  typeModifier = 'rotate'),
                                              'cgmObject',
                                              setClass=True)
        mRotateGroup.p_parent = mDefineNull"""
        
        
        #Aim Controls ==================================================================
        _d = {'end':{'color':'white','defaults':{'tz':1}},
              'up':{'color':'greenBright','defaults':{'ty':.5}},
              'rp':{'color':'redBright','defaults':{'tx':.5}},
              'lever':{'color':'orange','defaults':{'tz':-.25}}}
        
        md_handles = {}
        ml_handles = []
        md_vector = {}
        md_jointLabels = {}
        
        _l_order = ['end','up','rp','lever']
        
            
        _resDefine = self.UTILS.create_defineHandles(self, _l_order, _d, _size,
                                                     rotVecControl=True,
                                                     blockUpVector = self.baseDat['up'])
        #_resDefine = self.UTILS.create_defineHandles(self, _l_order, _d, _size)
        self.UTILS.define_set_baseSize(self)
        md_vector = _resDefine['md_vector']
        md_handles = _resDefine['md_handles']
        
        mLeverGroup = mDefineNull.doCreateAt('null',setClass='cgmObject')
        mLeverGroup.p_parent = mDefineNull
        mLeverGroup.rename('lever_null')
        mLeverGroup.doConnectIn('visibility',"{0}.buildLeverBase".format(self.mNode))
        
        md_handles['lever'].p_parent = mLeverGroup
        md_vector['lever'].p_parent = mLeverGroup
        
        #Rotate Plane ======================================================================
        self.UTILS.create_define_rotatePlane(self, md_handles,md_vector)
        _end = md_handles['end'].mNode
        self.doConnectIn('baseSizeX',"{0}.width".format(_end))
        self.doConnectIn('baseSizeY',"{0}.height".format(_end))
        self.doConnectIn('baseSizeZ',"{0}.length".format(_end))
        
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
        
        for k in ['end','rp','up','lever']:
            mHandle = self.getMessageAsMeta("define{0}Helper".format(k.capitalize()))
            if mHandle:
                l_const = mHandle.getConstraintsTo()
                if l_const:
                    log.debug("currentConstraints...")
                    pos = mHandle.p_position
                    
                    for i,c in enumerate(l_const):
                        log.debug("    {0} : {1}".format(i,c))
                    mc.delete(l_const)
                    mHandle.p_position = pos
                    
                mHandle.v = True
                mHandle.template = False
                
                if k == 'end':
                    _end = mHandle.mNode
                    self.doConnectIn('baseSizeX',"{0}.width".format(_end))
                    self.doConnectIn('baseSizeY',"{0}.height".format(_end))
                    self.doConnectIn('baseSizeZ',"{0}.length".format(_end))                  
                
            mHandle = self.getMessageAsMeta("vector{0}Helper".format(k.capitalize()))
            if mHandle:
                mHandle.template=False
                
                 
            
        self.defineLoftMesh.v = True
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err,localDat=vars())        
    
    
def template(self):
    try:
        _str_func = 'template'
        log.debug("|{0}| >> ...".format(_str_func)+ '-'*80)
        log.debug("{0}".format(self))
        
        
        
        ATTR.datList_connect(self.mNode, 'rollCount', [self.numRoll for i in range(self.numControls - 1)])
        l_rollattrs = ATTR.datList_getAttrs(self.mNode,'rollCount')
        for a in l_rollattrs:
            ATTR.set_standardFlags(self.mNode, l_rollattrs, lock=False,visible=True,keyable=True)
        
        #Initial checks =====================================================================================
        log.debug("|{0}| >> Initial checks...".format(_str_func)+ '-'*40)
        _short = self.p_nameShort
        _side = self.UTILS.get_side(self)
            
        _l_basePosRaw = self.datList_get('basePos') or [(0,0,0)]
        _l_basePos = [self.p_position]
        
        
        _ikSetup = self.getEnumValueString('ikSetup')
        _ikEnd = self.getEnumValueString('ikEnd')
        _loftSetup = self.getEnumValueString('loftSetup')
                
        for a in 'XYZ':ATTR.break_connection(self.mNode,'baseSize'+a)
            
        #Get base dat =====================================================================================    
        log.debug("|{0}| >> Base dat...".format(_str_func)+ '-'*40)
        
        #Old method...
        mRootUpHelper = self.vectorUpHelper    
        _mVectorAim = MATH.get_obj_vector(self.vectorEndHelper.mNode,asEuclid=True)
        _mVectorUp = MATH.get_obj_vector(mRootUpHelper.mNode,'y+',asEuclid=True)    
        mDefineEndObj = self.defineEndHelper
        mDefineUpObj = self.defineUpHelper
        
        #Template our vectors
        for k in ['end','rp','up','lever']:
            mHandle = self.getMessageAsMeta("vector{0}Helper".format(k.capitalize()))    
            if k not in ['rp']:
                mHandle.template=True
    
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
        _size_length = DIST.get_distance_between_points(self.p_position, _end)
        _size_handle = _size_width * 1.25
        #self.baseSize = [_size_width,_size_height,_size_length]
        _l_basePos.append(_end)
        log.debug("|{0}| >> baseSize: {1}".format(_str_func, self.baseSize))
        
        #for i,p in enumerate(_l_basePos):
        #    LOC.create(position=p,name="{0}_loc".format(i))
        
        #Hide define stuff ---------------------------------------------
        log.debug("|{0}| >> define stuff...".format(_str_func)+ '-'*40)
        
        mDefineLoftMesh.v = False
        mDefineUpObj.v = False
        mDefineEndObj.v=False
        
        #Create temple Null ==================================================================================
        log.debug("|{0}| >> nulls...".format(_str_func)+ '-'*40)
        
        #mTemplateNull = self.atUtils('templateNull_verify')
        mTemplateNull = self.UTILS.stateNull_verify(self,'template')
        mNoTransformNull = self.atUtils('noTransformNull_verify','template')
        
        #Our main rigBlock shape ...
        mHandleFactory = self.asHandleFactory()
        
        int_handles = self.numControls
        _loftShape = self.getEnumValueString('loftShape')
        if _loftSetup == 'loftList':
            self.UTILS.verify_loftList(self,int_handles)        
        
        _l_loftShapes =  ATTR.datList_get(_short,'loftList',enum=True) or []
        log.debug("|{0}| >> base loftList: {1}".format(_str_func,_l_loftShapes))        
        if _l_loftShapes:
            if len(_l_loftShapes) < int_handles:
                log.warning("|{0}| >> Not enough shapes in loftList. Padding with loftShape".format(_str_func,i,_loftShape))
                while len(_l_loftShapes) < int_handles:
                    _l_loftShapes.append(_loftShape)
        else:
            _l_loftShapes = [_loftShape for i in range(int_handles)]
        
        _l_loftShapes = [('loft' + shape[0].capitalize() + ''.join(shape[1:])) for shape in _l_loftShapes]
                         
        log.debug("|{0}| >> loftShapes: {1}".format(_str_func,_l_loftShapes))
        
        #Lever =============================================================================================
        _b_lever = False
        if self.buildLeverBase:
            _b_lever = True
            log.debug("|{0}| >> Lever base, generating base value".format(_str_func))
            _mBlockParent = self.p_blockParent
    
            mDefineLeverObj = self.defineLeverHelper
            _mVectorLeverUp = MATH.get_obj_vector(mDefineLeverObj.mNode,'y+',asEuclid=True)
            mDefineLeverObj.v=False
            
            pos_lever = mDefineLeverObj.p_position
            
            log.debug("|{0}| >> pos_lever: {1} ".format(_str_func,pos_lever))
            #LOC.create(position=pos_lever, name='lever_pos_loc')
        
        #cgmGEN.func_snapShot(vars())
        #return
        
        #Root handles ===========================================================================================
        log.debug("|{0}| >> root handles...".format(_str_func) + '-'*40) 
        md_handles = {'lever':None}
        ml_handles = []
        md_loftHandles = {}
        ml_loftHandles = []
        

        log.debug("|{0}| >> loft setup...".format(_str_func))
        
        for i,n in enumerate(['start','end']):
            log.debug("|{0}| >> {1}:{2}...".format(_str_func,i,n)) 
            iUse = 0
            if i:iUse = -1
            mHandle = mHandleFactory.buildBaseShape('cubeOpen',baseSize = _size_handle, shapeDirection = 'z+')
            mHandle.p_parent = mTemplateNull
            
            mHandle.resetAttrs()
            
            self.copyAttrTo('cgmName',mHandle.mNode,'cgmName',driven='target')
            mHandle.doStore('cgmType','blockHandle')
            mHandle.doStore('cgmNameModifier',n)
            
            mHandle.doName()
            
            #Convert to loft curve setup ----------------------------------------------------
            mHandleFactory.setHandle(mHandle.mNode)
            #mHandleFactory = self.asHandleFactory(mHandle.mNode)
            
            mLoftCurve = mHandleFactory.rebuildAsLoftTarget(_l_loftShapes[iUse], _size_width, shapeDirection = 'z+',rebuildHandle = False)
            mc.makeIdentity(mHandle.mNode,a=True, s = True)#...must freeze scale once we're back parented and positioned
            
            mHandleFactory.color(mHandle.mNode)            
            mHandle.p_position = _l_basePos[i]
            
            md_handles[n] = mHandle
            ml_handles.append(mHandle)
            
            md_loftHandles[n] = mLoftCurve                
            ml_loftHandles.append(mLoftCurve)
            
            mLoftCurve.p_parent = mTemplateNull
            mTransformedGroup = mLoftCurve.getMessageAsMeta('transformedGroup')
            if not mTransformedGroup:
                mTransformedGroup = mLoftCurve.doGroup(True,True,asMeta=True,typeModifier = 'transformed',setClass='cgmObject')
            mHandle.doConnectOut('scale', "{0}.scale".format(mTransformedGroup.mNode))
            mc.pointConstraint(mHandle.mNode,mTransformedGroup.mNode,maintainOffset=False)
            
            mBaseAttachGroup = mHandle.doGroup(True,True, asMeta=True,typeModifier = 'attach')
            
        #Constrain the define end to the end of the template handles
        mc.pointConstraint(md_handles['end'].mNode,mDefineEndObj.mNode,maintainOffset=False)
        #mc.scaleConstraint(md_handles['end'].mNode,mDefineEndObj.mNode,maintainOffset=True)
        
        
        #>> Base Orient Helper ============================================================================
        log.debug("|{0}| >> Base orient helper...".format(_str_func) + '-'*40) 
        
        mHandleFactory = self.asHandleFactory(md_handles['start'].mNode)
        mBaseOrientCurve = mHandleFactory.addOrientHelper(baseSize = _size_width,
                                                          shapeDirection = 'y+',
                                                          setAttrs = {'ty':_size_width})
    
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
        
        mBaseOrientCurve.setAttrFlags(['ry','rx','translate','scale','v'])
        mHandleFactory.color(mBaseOrientCurve.mNode,controlType='sub')
        mc.select(cl=True)
        

        #Lever Handle ===============================================================================
        log.debug("|{0}| >> Lever handle...".format(_str_func) + '-'*40) 
        
        if _b_lever:
            crv = CURVES.create_fromName('sphere2', _size_handle, direction = 'y+')
            mHandle = cgmMeta.validateObjArg(crv, 'cgmObject', setClass=True)
            md_handles['lever'] = mHandle
            self.copyAttrTo('cgmName',mHandle.mNode,'cgmName',driven='target')
            mHandle.doStore('cgmType','blockHandle')
            mHandle.doStore('cgmNameModifier',"lever".format(i+1))
            mHandle.doName()                
            
            _short = mHandle.mNode
            mHandle.p_parent = mTemplateNull
            mHandle.resetAttrs()
            print md_handles['lever']
            mHandle.p_position = pos_lever
            
            mHandleFactory.setHandle(mHandle.mNode)
            mLeverLoftCurve = mHandleFactory.rebuildAsLoftTarget(self.getEnumValueString('loftShapeStart'),#_loftShape,
                                                                 _size_width,
                                                                 shapeDirection = 'z+',rebuildHandle = False)
            #mc.makeIdentity(mHandle.mNode,a=True, s = True)#...must freeze scale once we're back parented and positioned
            print md_handles['lever']
        
            mGroup = mHandle.doGroup(True,True,asMeta=True,typeModifier = 'master')
            mHandleFactory = self.asHandleFactory(mHandle.mNode)
        
            CORERIG.colorControl(mHandle.mNode,_side,'main',transparent = True)
            
            SNAP.aim(mGroup.mNode, self.mNode,vectorUp=_mVectorLeverUp,mode='vector')
            
            
            mc.parentConstraint(mHandle.mNode, mDefineLeverObj.mNode, maintainOffset = False)
            self.connectChildNode(mHandle.mNode,'templateLeverHandle')      
            
            """
            mc.aimConstraint(md_handles['start'].mNode, mGroup.mNode, maintainOffset = False,
                             aimVector = [0,0,1], upVector = [0,1,0], 
                             worldUpObject = mDefineLeverObj.mNode,
                             worldUpType = 'objectrotation', 
                             worldUpVector = [0,1,0])"""
            print md_handles['lever']            
        
        
        
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
            
            for s in _midTrackResult[1]:
                ATTR.set(s[1],'visibility',False)
        
            #>>> mid main handles =====================================================================
            l_scales = []
            for mHandle in ml_handles:
                l_scales.append(mHandle.scale)
                mHandle.scale = 1,1,1
        
            _l_posMid = CURVES.returnSplitCurveList(mMidTrackCurve.mNode,self.numControls,markPoints = False)
            #_l_pos = [ DIST.get_pos_by_vec_dist(_pos_start, _vec, (_offsetDist * i)) for i in range(self.numControls-1)] + [_pos_end]
        
        
            #Sub handles... -----------------------------------------------------------------------------------
            log.debug("|{0}| >> Mid Handle creation...".format(_str_func))
            ml_aimGroups = []
            ml_midHandles = []
            ml_midLoftHandles = []
            for i,p in enumerate(_l_posMid[1:-1]):
                log.debug("|{0}| >> mid handle cnt: {1} | p: {2}".format(_str_func,i,p))
                crv = CURVES.create_fromName('sphere2', _size_handle, direction = 'y+')
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
                mLoftCurve = mHandleFactory.rebuildAsLoftTarget(_l_loftShapes[i+1],
                                                                _size_width,
                                                                shapeDirection = 'z+',rebuildHandle = False)
                mc.makeIdentity(mHandle.mNode,a=True, s = True)#...must freeze scale once we're back parented and positioned
                ml_midLoftHandles.append(mLoftCurve)
                
                mTransformedGroup = mHandle.getMessageAsMeta('transformedGroup')
                if not mTransformedGroup:
                    mTransformedGroup = mHandle.doGroup(True,True,asMeta=True,typeModifier = 'transformed')
                #mGroup = mHandle.doGroup(True,True,asMeta=True,typeModifier = 'master')
                #mAimGroup = mHandle.doGroup(True,True,asMeta=True,typeModifier = 'aim')
                
                
                _vList = DIST.get_normalizedWeightsByDistance(mTransformedGroup.mNode,
                                                              [ml_handles[0].mNode,ml_handles[-1].mNode])

                #_scale = mc.scaleConstraint([ml_handles[0].mNode,ml_handles[-1].mNode],
                #                            mTransformedGroup.mNode,maintainOffset = False)
        
                _res_attach = RIGCONSTRAINT.attach_toShape(mTransformedGroup.mNode, mMidTrackCurve.mNode, 'conPoint')
                TRANS.parent_set(_res_attach[0], mNoTransformNull.mNode)
                
                mTransformedGroup.resetAttrs('rotate')
                
                
                mLoftCurve.p_parent = mTemplateNull
                mLoftTransformedGroup = mLoftCurve.getMessageAsMeta('transformedGroup')
                if not mLoftTransformedGroup:
                    mLoftTransformedGroup = mLoftCurve.doGroup(True,asMeta=True,typeModifier = 'transformed')
                    
                #mTransformedGroup = mLoftCurve.doGroup(True,True,asMeta=True,typeModifier = 'transformed')
                #mHandle.doConnectOut('scale', "{0}.scale".format(mScaleGroup.mNode))
                mc.scaleConstraint(mHandle.mNode,
                                   mLoftTransformedGroup.mNode,maintainOffset = False)                
                mc.pointConstraint(mHandle.mNode,mLoftTransformedGroup.mNode,maintainOffset=False)
                
                
                #for c in [_scale]:
                    #CONSTRAINT.set_weightsByDistance(c[0],_vList)
        
                mHandleFactory = self.asHandleFactory(mHandle.mNode)
        
                CORERIG.colorControl(mHandle.mNode,_side,'main',transparent = True)
                
            #Push scale back...
            for i,mHandle in enumerate(ml_handles):
                mHandle.scale = l_scales[i]

            
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
            mGroup =  md_handles['start'].doGroup(True,True,asMeta=True,typeModifier = 'aim')            
            _const = mc.aimConstraint(md_handles['end'].mNode, mGroup.mNode,
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
            
            for s in _mainTrackResult[1]:
                ATTR.set(s[1],'visibility',False)            
        else:
            ml_handles_chain = copy.copy(ml_handles)
            
        
        #>>> Aim Main loft curves ================================================================== 
        log.debug("|{0}| >> Aim main loft curves...".format(_str_func)) 
        
        if _b_lever:
            ml_handles_chain.insert(0,md_handles['lever'])
            
        for i,mHandle in enumerate(ml_handles_chain):
            if mHandle in [md_handles['lever']]:#,md_handles['end']
                continue
            
            mLoft = mHandle.loftCurve
            _str_handle = mHandle.mNode
            
            mTransformedGroup = mLoft.getMessageAsMeta('transformedGroup')
            if not mTransformedGroup:
                mTransformedGroup = mLoft.doGroup(True,asMeta=True,typeModifier = 'transformed')
            mLoft.visibility = 1
            #mLoft.setAttrFlags(['translate'])
            
            for mShape in mLoft.getShapes(asMeta=True):
                mShape.overrideDisplayType = 0
            
            _worldUpType = 'objectrotation'
            _worldUpBack = 'objectrotation'
            
            if mHandle == md_handles['lever']:
                _worldUpType = 'vector'
            #elif mHandle == md_handles['start'] and _b_lever:
                #_worldUpBack = 'vector'
                
            _aimBack = None
            _aimForward = None
            _backUpObj = None
            
            if mHandle == ml_handles_chain[0]:
                _aimForward = ml_handles_chain[i+1].mNode
            elif mHandle == ml_handles_chain[-1]:
                if len(ml_handles_chain)>2:
                    _aimBack = ml_handles_chain[-2].mNode#md_handles['start'].mNode#ml_handles_chain[].mNode
                else:
                    _aimBack = md_handles['start'].mNode
            else:
                _aimForward =  ml_handles_chain[i+1].mNode
                _aimBack  =  ml_handles_chain[i-1].mNode
                
            if _aimBack and md_handles.get('lever'):
                if _aimBack == md_handles.get('lever').mNode:
                    _backUpObj = md_handles.get('lever').mNode
                
            if _aimForward and _aimBack is None:
                mc.aimConstraint(_aimForward, mTransformedGroup.mNode, maintainOffset = False,
                                 aimVector = [0,0,1], upVector = [0,1,0], 
                                 worldUpObject = mBaseOrientCurve.mNode,
                                 worldUpType = _worldUpType, 
                                 worldUpVector = [0,1,0])
            elif _aimBack and _aimForward is None:
                mc.aimConstraint(_aimBack, mTransformedGroup.mNode, maintainOffset = False,
                                 aimVector = [0,0,-1], upVector = [0,1,0], 
                                 worldUpObject = mBaseOrientCurve.mNode,
                                 worldUpType = _worldUpBack, 
                                 worldUpVector = [0,1,0])
            else:
                mAimForward = mLoft.doCreateAt()
                mAimForward.p_parent = mLoft.p_parent
                mAimForward.doStore('cgmName',mHandle)                
                mAimForward.doStore('cgmTypeModifier','forward')
                mAimForward.doStore('cgmType','aimer')
                mAimForward.doName()
                
                mAimBack = mLoft.doCreateAt()
                mAimBack.p_parent = mLoft.p_parent
                mAimBack.doStore('cgmName',mHandle)                                
                mAimBack.doStore('cgmTypeModifier','back')
                mAimBack.doStore('cgmType','aimer')
                mAimBack.doName()
                
                mc.aimConstraint(_aimForward, mAimForward.mNode, maintainOffset = False,
                                 aimVector = [0,0,1], upVector = [0,1,0], 
                                 worldUpObject = mBaseOrientCurve.mNode,
                                 worldUpType = _worldUpType, 
                                 worldUpVector = [0,1,0])
                
                if _backUpObj == None:
                    _backUpObj =  mBaseOrientCurve.mNode
                    
                mc.aimConstraint(_aimBack, mAimBack.mNode, maintainOffset = False,
                                 aimVector = [0,0,-1], upVector = [0,1,0], 
                                 worldUpObject = _backUpObj,
                                 worldUpType = _worldUpType, 
                                 worldUpVector = [0,1,0])                
                
                const = mc.orientConstraint([mAimForward.mNode, mAimBack.mNode],
                                            mTransformedGroup.mNode, maintainOffset = False)[0]
                
                ATTR.set(const,'interpType',2)#.shortest...
                
                #...also aim our main handles...
                if mHandle not in [md_handles['end'],md_handles['start']]:
                    mHandleAimGroup = mHandle.getMessageAsMeta('transformedGroup')
                    if not mHandleAimGroup:
                        mHandleAimGroup = mHandle.doGroup(True,asMeta=True,typeModifier = 'transformed')
                        
                    mc.aimConstraint(_aimForward, mHandleAimGroup.mNode, maintainOffset = False,
                                     aimVector = [0,0,1], upVector = [0,1,0], 
                                     worldUpObject = mBaseOrientCurve.mNode,
                                     worldUpType = 'objectrotation', 
                                     worldUpVector = [0,1,0])

            if mHandle == md_handles['lever']:
                pass
                #ATTR.set_standardFlags( mHandle.mNode, ['rotate'])
            elif mHandle in [md_handles['start'],md_handles['end']]:
                _lock = []
                if mHandle == md_handles['start']:
                    _lock.append('rotate')
                    
                #ATTR.set_alias(mHandle.mNode,'sy','handleScale')    
                #ATTR.set_standardFlags( mHandle.mNode, _lock)
                #mHandle.doConnectOut('sy',['sx','sz'])
                ATTR.set_standardFlags( mHandle.mNode, _lock)
                
            else:
                ATTR.set_standardFlags( mHandle.mNode, ['rotate','sz'])
                ATTR.connect('{0}.sy'.format(mHandle.mNode), '{0}.sz'.format(mHandle.mNode))
                
        
        #ml_shapers = copy.copy(ml_handles_chain)
        #>>> shaper handles =======================================================================
        if self.numSubShapers:
            _numSubShapers = self.numSubShapers
            ml_shapers = []
            log.debug("|{0}| >> Sub shaper handles: {1}".format(_str_func,_numSubShapers))
            
            mOrientHelper = mBaseOrientCurve
            
            log.debug("|{0}| >> pairs...".format(_str_func))
            

            ml_handlesToShaper = ml_handles_chain
            ml_shapers = [ml_handlesToShaper[0]]
                
            ml_pairs = LISTS.get_listPairs(ml_handlesToShaper)
            #pprint.pprint(ml_pairs)
            
            
            for i,mPair in enumerate(ml_pairs):
                log.debug(cgmGEN._str_subLine)
                ml_shapersTmp = []
                
                _mStart = mPair[0]
                _mEnd = mPair[1]
                _end = _mEnd.mNode
                log.debug("|{0}| >> pairs: {1} | end: {2}".format(_str_func,i,_end))
                
                _pos_start = _mStart.p_position
                _pos_end = _mEnd.p_position 
                
                _leverLoftAimMode = False
                
                if i == 0 and self.buildLeverBase:
                    _numSubShapers = 1
                    _leverLoftAimMode = True
                else:
                    _numSubShapers = self.numSubShapers

                
                _vec = MATH.get_vector_of_two_points(_pos_start, _pos_end)
                _offsetDist = DIST.get_distance_between_points(_pos_start,_pos_end) / (_numSubShapers+1)
                _l_pos_seg = [ DIST.get_pos_by_vec_dist(_pos_start,
                                                        _vec,
                                                        (_offsetDist * ii)) for ii in range(_numSubShapers+1)] + [_pos_end]
            
                _mVectorAim = MATH.get_vector_of_two_points(_pos_start, _pos_end,asEuclid=True)
                #_mVectorUp = _mVectorAim.up()
                _worldUpVector = [_mVectorUp.x,_mVectorUp.y,_mVectorUp.z]        
                
            
                #Linear track curve ----------------------------------------------------------------------
                _linearCurve = mc.curve(d=1,p=[_pos_start,_pos_end])
                mLinearCurve = cgmMeta.validateObjArg(_linearCurve,'cgmObject')
                
            
                l_clusters = []
                #_l_clusterParents = [mStartHandle,mEndHandle]
                for ii,cv in enumerate(mLinearCurve.getComponents('cv')):
                    _res = mc.cluster(cv, n = 'seg_{0}_{1}_cluster'.format(mPair[0].p_nameBase,ii))
                    TRANS.parent_set(_res[1], mTemplateNull)
                    mc.pointConstraint(mPair[ii].mNode,#getMessage('loftCurve')[0],
                                       _res[1],maintainOffset=True)
                    ATTR.set(_res[1],'v',False)                
                    l_clusters.append(_res)
            
            
                mLinearCurve.parent = mNoTransformNull
                mLinearCurve.rename('seg_{0}_trackCrv'.format(i))
            
                #mLinearCurve.inheritsTransform = False      
            
            
                #Tmp loft mesh -------------------------------------------------------------------
                #...we're going to duplicate our end curve to get a clean end aimer
                mDupLoft = False
                
                if self.buildLeverBase and i == 0:
                    log.debug("|{0}| >> lever loft aim | 0".format(_str_func,i,_end))
                    
                    mDupLoft = mPair[1].loftCurve.doDuplicate(po=False)
                    SNAP.aim_atPoint(mDupLoft.mNode,mPair[0].p_position,
                                     'z-',mode='vector',vectorUp=mPair[0].getAxisVector('y+'))
                    _l_targets = [mPair[0].loftCurve.mNode, mDupLoft.mNode]
                elif self.buildLeverBase and i == 1:
                    log.debug("|{0}| >> lever loft aim | 1".format(_str_func,i,_end))
                    
                    mDupLoft = mPair[0].loftCurve.doDuplicate(po=False)
                    SNAP.aim_atPoint(mDupLoft.mNode,mPair[1].p_position,
                                     'z+',mode='vector',vectorUp=_worldUpVector)                            
                    _l_targets = [mDupLoft.mNode, mPair[1].loftCurve.mNode]
                        
                else:
                    _l_targets = [mObj.loftCurve.mNode for mObj in mPair]
                    
                log.debug(_l_targets)
                _res_body = mc.loft(_l_targets, o = True, d = 3, po = 0 )
                _str_tmpMesh =_res_body[0]
            
                l_scales_seg = []
                
            
                #for mHandle in mPair:
                    #l_scales_seg.append(mHandle.scale)
                    #mHandle.scale = 1,1,1
                
                #Sub handles... --------------------------------------------------------------------------
                for ii,p in enumerate(_l_pos_seg[1:-1]):
                    #mHandle = mHandleFactory.buildBaseShape('circle', _size, shapeDirection = 'y+')
                    mHandle = cgmMeta.cgmObject(name = 'subHandle_{0}_{1}'.format(i,ii))
                    _short = mHandle.mNode
                    ml_handles.append(mHandle)
                    mHandle.p_position = p
                    if _leverLoftAimMode:
                        SNAP.aim_atPoint(_short,_l_pos_seg[ii+2],'z+', 'y+', mode='vector',
                                         vectorUp = _mVectorLeverUp)
                    else:
                        SNAP.aim_atPoint(_short,_l_pos_seg[ii+2],'z+', 'y+', mode='vector', vectorUp = _mVectorUp)
            
                    #...Make our curve
                    _d = RAYS.cast(_str_tmpMesh, _short, 'x+')
                    #pprint.pprint(_d)
                    log.debug("|{0}| >> Casting {1} ...".format(_str_func,_short))
                    #cgmGEN.log_info_dict(_d)
                    _v = _d['uvs'][_str_tmpMesh][0][0]
                    log.debug("|{0}| >> v: {1} ...".format(_str_func,_v))
            
                    #>>For each v value, make a new curve -----------------------------------------------------------------        
                    #duplicateCurve -ch 1 -rn 0 -local 0  "loftedSurface2.u[0.724977270271534]"
                    _crv = mc.duplicateCurve("{0}.u[{1}]".format(_str_tmpMesh,_v), ch = 0, rn = 0, local = 0)
                    log.debug("|{0}| >> created: {1} ...".format(_str_func,_crv))  
            
                    CORERIG.shapeParent_in_place(_short, _crv, False)
            
                    #self.copyAttrTo(_baseNameAttrs[1],mHandle.mNode,'cgmName',driven='target')
                    self.copyAttrTo('cgmName',mHandle.mNode,'cgmName',driven='target')
                    mHandle.doStore('cgmNameModifier','shapeHandle_{0}_{1}'.format(i,ii))
                    mHandle.doStore('cgmType','blockHandle')
                    mHandle.doName()
            
                    mHandle.p_parent = mTemplateNull
            
                    mGroup = mHandle.doGroup(True,True,asMeta=True,typeModifier = 'master')
                    mGroup.p_parent = mTemplateNull
            
                    _vList = DIST.get_normalizedWeightsByDistance(mGroup.mNode,[mPair[0].mNode,mPair[1].mNode])
            
                    _scale = mc.scaleConstraint([mPair[0].mNode,mPair[1].mNode],mGroup.mNode,maintainOffset = False)#Point contraint loc to the object
                    
                    if _leverLoftAimMode:
                        upObj = md_handles['lever'].mNode
                    else:
                        upObj = mBaseOrientCurve.mNode
                    
                    mc.aimConstraint([_end], mGroup.mNode, maintainOffset = False, #skip = 'z',
                                     aimVector = [0,0,1], upVector = [0,1,0],
                                     worldUpObject = upObj,
                                     worldUpType = 'objectrotation', worldUpVector = [0,1,0])                    
            
                    _res_attach = RIGCONSTRAINT.attach_toShape(mGroup.mNode, 
                                                               mLinearCurve.mNode,
                                                               'conPoint')
                    TRANS.parent_set(_res_attach[0], mNoTransformNull.mNode)
            
                    for c in [_scale]:
                        CONSTRAINT.set_weightsByDistance(c[0],_vList)
            
                    #Convert to loft curve setup ----------------------------------------------------
                    mHandleFactory = self.asHandleFactory(mHandle.mNode)
                    #mHandleFactory.rebuildAsLoftTarget('self', None, shapeDirection = 'z+')
                    mHandle.doStore('loftCurve',mHandle)
            
            
                    CORERIG.colorControl(mHandle.mNode,_side,'sub',transparent = True)        
                    #LOC.create(position = p)
                    ml_shapers.append(mHandle)
                    ml_shapersTmp.append(mHandle)
                
                
                ml_shapers.append(mPair[1])
                mc.delete(_res_body)
                
                _mStart.msgList_connect('subShapers',[mObj.mNode for mObj in ml_shapersTmp])                    
                
                if mDupLoft:
                    mDupLoft.delete()
        #>>> Connections ====================================================================================
        self.msgList_connect('templateHandles',[mObj.mNode for mObj in ml_handles_chain])

        #>>Loft Mesh =========================================================================================
        if self.numSubShapers:
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
        
  
        mPivotHelper= False
        #End setup======================================================================================
        if _ikSetup != 'none':
            mEndHandle = ml_handles_chain[-1]
            _shapeEnd = self.getEnumValueString('loftShapeEnd')
            log.debug("|{0}| >> ikSetup. End: {1}".format(_str_func,mEndHandle))
            mHandleFactory.setHandle(mEndHandle.mNode)
            _bankSize = [_size_width,
                         _size_width,
                         _size_width]
            
            if _ikEnd == 'bank':
                log.debug("|{0}| >> Bank setup".format(_str_func)) 
                mFoot,mFootLoftTop = self.UTILS.pivotHelper_get(self,mEndHandle,baseShape = _shapeEnd, baseSize=_size_handle,loft=False)
                mFoot.p_parent = mTemplateNull
                
                #mHandleFactory.addPivotSetupHelper(baseShape = _shapeEnd, baseSize = _bankSize).p_parent = mTemplateNull
            elif _ikEnd in ['foot','pad']:
                log.debug("|{0}| >> foot setup".format(_str_func)) 
                mFoot,mFootLoftTop = self.UTILS.pivotHelper_get(self,mEndHandle,baseShape = _shapeEnd, baseSize=_size_handle)
                #mFoot,mFootLoftTop = mHandleFactory.addFootHelper(baseShape = _shapeEnd, baseSize=_bankSize)
                mFoot.p_parent = mTemplateNull
            elif _ikEnd == 'proxy':
                log.debug("|{0}| >> proxy setup".format(_str_func)) 
                mProxy = mHandleFactory.addProxyHelper(shapeDirection = 'z+',baseSize=_bankSize)
                mProxy.p_parent = mEndHandle
                
                pos_proxy = SNAPCALLS.get_special_pos(mEndHandle.p_nameLong,
                                                     'axisBox','z+',False)
                
                log.debug("|{0}| >> posProxy: {1}".format(_str_func,pos_proxy))
                mProxy.p_position = pos_proxy
                CORERIG.copy_pivot(mProxy.mNode,mEndHandle.mNode)
                
            
            if _ikEnd in ['bank','foot','pad']:
                mPivotHelper = mEndHandle.pivotHelper
                
                if self.blockProfile in ['arm']:
                    mPivotHelper.doSnapTo(mEndHandle,True,True)
                    mGroup = mPivotHelper.doGroup(True,True,asMeta=True,typeModifier = 'track',setClass='cgmObject')
                    mc.parentConstraint([mEndHandle.mNode],mGroup.mNode,)
                    mc.scaleConstraint([mEndHandle.mNode],mGroup.mNode,)
                    mGroup.dagLock()
                elif _ikEnd == 'bank':
                    mGroup = mPivotHelper.doGroup(True,True,asMeta=True,typeModifier = 'track',setClass='cgmObject')
                    mc.parentConstraint([mEndHandle.mNode],mGroup.mNode,)
                    mc.scaleConstraint([mEndHandle.mNode],mGroup.mNode,)
                    mGroup.dagLock()                    
                else:
                    mGroup = mPivotHelper.doGroup(True,True,asMeta=True,typeModifier = 'track',setClass='cgmObject')
                    mc.pointConstraint([mEndHandle.mNode],mGroup.mNode, skip='y')
                    mc.orientConstraint([mEndHandle.mNode],mGroup.mNode, skip=['z','x'])
                    mGroup.dagLock()
                
                    
        #Aim end handle ----------------------------------------------------------------------------------- 
        SNAP.aim_atPoint(md_handles['end'].mNode, position=_l_basePos[0], 
                         aimAxis="z-", mode='vector', vectorUp=_mVectorUp)
        
        if mPivotHelper:
            if self.blockProfile in ['arm']:
                mPivotHelper.doSnapTo(mEndHandle,True,True)
                mPivotHelper.p_position = mEndHandle.getPositionByAxisDistance('y-',_size_height)
            elif _ikEnd in ['foot','pad']:
                mPivotHelper.p_position = mEndHandle.getPositionByAxisDistance('z+',_size_height)
                
            #else:
            #    mPivotHelper.p_position = mEndHandle.getPositionByAxisDistance('y-',_size_height)

                
        self.blockState = 'template'#...buffer
    
    
        return True
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err,localDat=vars())        


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
        self.atUtils('module_verify')
    
        #> Get our stored dat =====================================================================================
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
            baseName = self.cgmName#_l_baseNames[0]
            _l_baseNamesNEW = []
            for i in range(len(ml_templateHandles)):
                _l_baseNamesNEW.append("{0}_{1}".format(baseName,i))
            ATTR.datList_connect(self.mNode,'nameList',_l_baseNamesNEW)
            _l_baseNames = ATTR.datList_get(self.mNode, 'nameList')#...get em back
            
        _baseNameAttrs = ATTR.datList_getAttrs(self.mNode,'nameList')
            
        #Create some nulls Null  =========================================================================
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
        
        _size = MATH.average(POS.get_bb_size(mStartHandle.mNode,True,'maxFill'))#(mHandleFactory.get_axisBox_size(mStartHandle.mNode))
        #DIST.get_bb_size(mStartHandle.loftCurve.mNode,True)[0]    
        _sizeSub = _size * .33    
        _vec_root_up = mOrientHelper.getAxisVector('y+')
        
        
        #Initial logic=========================================================================================
        log.debug("|{0}| >> Initial Logic...".format(_str_func)) 
        
        _pos_start = mStartHandle.p_position
        _pos_end = mEndHandle.p_position 
        _vec = MATH.get_vector_of_two_points(_pos_start, _pos_end)
        
        _mVectorAim = MATH.get_vector_of_two_points(_pos_start, _pos_end,asEuclid=True)
        _mVectorUp = MATH.get_obj_vector(mOrientHelper.mNode,'y+',asEuclid=True)
        
        #_mVectorUp = _mVectorAim.up()
        _worldUpVector = [_mVectorUp.x,_mVectorUp.y,_mVectorUp.z]
        
        #Foot helper ============================================================================
        mFootHelper = False
        if ml_templateHandles[-1].getMessage('pivotHelper'):
            log.debug("|{0}| >> footHelper".format(_str_func))
            mFootHelper = ml_templateHandles[-1].pivotHelper
    
        _ikEnd = self.getEnumValueString('ikEnd')
        ml_noParent = []
        if _ikEnd not in ['pad','bank']:
            if self.hasBallJoint and mFootHelper:
                mHelp = mFootHelper.pivotCenter
                ml_templateHandles.append(mHelp)
                ml_noParent.append(mHelp)
            if self.hasEndJoint and mFootHelper:
                mHelp = mFootHelper.pivotFront            
                ml_templateHandles.append(mHelp)
                ml_noParent.append(mHelp)
            
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
        _nameDict = self.getNameDict(ignore=['cgmName','cgmType'])
        #_nameDict['cgmType'] = 'blockHandle'
        mPivotHelper = ml_templateHandles[-1].getMessageAsMeta('pivotHelper')
        
        mDefineEndObj = self.defineEndHelper    
        _size_width = mDefineEndObj.width#...x width
        _sizeUse1 = _size_width/ 3.0 #self.atUtils('get_shapeOffset')
        _sizeUse2 = self.atUtils('get_shapeOffset') * 2
        _sizeUse = min([_sizeUse1,_sizeUse2])
        mPivotHelper = ml_templateHandles[-1].getMessageAsMeta('pivotHelper')
        for i,mTemplateHandle in enumerate(ml_templateHandles):
            log.debug("|{0}| >> prerig handle cnt: {1} | {2}".format(_str_func,i,mTemplateHandle))
            if mTemplateHandle == mPivotHelper:
                log.debug("|{0}| >> pivotHelper. Skipping".format(_str_func,i))
                continue        
            _HandleSnapTo = mTemplateHandle.mNode
            
            if mTemplateHandle == mEndHandle:
                crv = CURVES.create_fromName('axis3d', size = _sizeUse * 2.0)
                mHandle = cgmMeta.validateObjArg(crv, 'cgmObject', setClass=True)
                mHandle.addAttr('cgmColorLock',True,lock=True,hidden=True)
                
                ml_shapes = mHandle.getShapes(asMeta=1)
                crv2 = CURVES.create_fromName('sphere', size = _sizeUse * 2.5)
                CORERIG.override_color(crv2, 'black')
                SNAP.go(crv2,mHandle.mNode)
                CORERIG.shapeParent_in_place(mHandle.mNode,crv2,False)
                
            else:
                crv = CURVES.create_fromName('axis3d', size = _sizeUse)
                mHandle = cgmMeta.validateObjArg(crv, 'cgmObject', setClass=True)
            _short = mHandle.mNode
            
            #if b_iterNames:
                #ATTR.copy_to(self.mNode,_baseNameAttrs[0],_short, 'cgmName', driven='target')
                #mHandle.doStore('cgmIterator',i)
            #    mHandle.doStore('cgmName',"{0}_{1}".format(_l_baseNames[0],i))
            #else:
            try:ATTR.copy_to(self.mNode,_baseNameAttrs[i],_short, 'cgmName', driven='target')
            except:mHandle.doStore('cgmName','NeedAnotherNameAttr')
            mHandle.doStore('cgmType','preHandle')
            for k,v in _nameDict.iteritems():
                if v:
                    ATTR.copy_to(self.mNode,k,_short, k, driven='target')
            mHandle.doName()
            ml_handles.append(mHandle)
            
            mHandle.doSnapTo(_HandleSnapTo)
            mHandle.p_parent = mPrerigNull
            mGroup = mHandle.doGroup(True,True,asMeta=True,typeModifier = 'master',setClass='cgmObject')
            
            if mTemplateHandle == mEndHandle and _ikEnd in ['foot','pad','bank'] and self.blockProfile not in ['arm']:
                log.debug("|{0}| >> end handle aim: {1}".format(_str_func,mEndHandle))
                
                #_size_width = mDefineEndObj.width#...x width
                SNAP.aim_atPoint(mHandle.mNode, DIST.get_pos_by_vec_dist(mHandle.p_position, _mVectorUp, mDefineEndObj.length), mode='vector',vectorUp=_mVectorUp)
            
            ml_aimGroups.append(mGroup)
            
            if mTemplateHandle not in ml_noParent:
                mc.parentConstraint(_HandleSnapTo, mGroup.mNode, maintainOffset=True)
            elif mFootHelper:
                mc.parentConstraint(mFootHelper.mNode, mGroup.mNode, maintainOffset=True)
                
            mHandleFactory = self.asHandleFactory(mHandle.mNode)
            
            #Convert to loft curve setup ----------------------------------------------------
            ml_jointHandles.append(mHandleFactory.addJointHelper(baseSize = _sizeUse /2.0))
            #CORERIG.colorControl(mHandle.mNode,_side,'sub',transparent = True)
            mHandleFactory.color(mHandle.mNode,controlType='sub')
        
            mTemplateHandle.connectChildNode(mHandle.mNode,'prerigHandle')
            
        self.msgList_connect('prerigHandles', ml_handles)
        
        #ml_handles[0].connectChildNode(mOrientHelper.mNode,'orientHelper')      
        
        #This breaks the naming
        #self.UTILS.prerigHandles_getNameDat(self,True)
                                 
        #Joint placer loft....
        for i,mObj in enumerate(ml_handles[:-1]):
            mLoft = mObj.jointHelper.loftCurve
            mAimGroup = mLoft.doGroup(True,True,asMeta=True)
            mc.aimConstraint(ml_handles[i+1].masterGroup.mNode,
                             mAimGroup.mNode,
                             maintainOffset = True, weight = 1,
                             aimVector = [0,0,1],
                             upVector = [0,1,0],
                             worldUpVector = [0,1,0],
                             worldUpObject = mObj.masterGroup.mNode,
                             worldUpType = 'objectRotation' )          
        targets = [mObj.jointHelper.loftCurve.mNode for mObj in ml_handles]
        jointHelpers = [mObj.jointHelper.mNode for mObj in ml_handles]
        
        #Name Handles...
        for mHandle in ml_handles:
            #Joint Label ---------------------------------------------------------------------------
            mJointLabel = cgmMeta.validateObjArg(mc.joint(),'cgmObject',setClass=True)
            #CORERIG.override_color(mJointLabel.mNode, _dtmp['color'])
        
            mJointLabel.p_parent = mHandle
            mJointLabel.resetAttrs()
        
            mJointLabel.radius = 0
            mJointLabel.side = 0
            mJointLabel.type = 18
            mJointLabel.drawLabel = 1
            mJointLabel.otherType = mHandle.cgmName
        
            mJointLabel.doStore('cgmName',mHandle)
            mJointLabel.doStore('cgmType','jointLabel')
            mJointLabel.doName()            
        
            mJointLabel.dagLock()
        
            mJointLabel.overrideEnabled = 1
            mJointLabel.overrideDisplayType = 2    
        
        self.msgList_connect('jointHelpers',jointHelpers)
        
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
        
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err,localDat=vars())        
    
def prerigDelete(self):
    try:
        if self.getMessage('templateLoftMesh'):
            mTemplateLoft = self.getMessage('templateLoftMesh',asMeta=True)[0]
            for s in mTemplateLoft.getShapes(asMeta=True):
                s.overrideDisplayType = 2
            mTemplateLoft.v = True
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err,localDat=vars())        

def skeleton_check(self):
    return True

def skeleton_build(self, forceNew = True):
    try:
        _short = self.mNode
        _str_func = 'skeleton_build'
        log.debug("|{0}| >>  {1}".format(_str_func,self)+ '-'*80)
        
        ml_joints = []
        
        mPrerigNull = self.prerigNull
        self.atUtils('module_verify')
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
            raise ValueError,"No prerig connected"
        
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
        if self.hasLeverJoint and self.buildLeverBase:
            _int_rollStart = 1
        _d_rollCounts = {i+_int_rollStart:v for i,v in enumerate(_rollCounts)}
        
        
        if len(_l_names) < len(ml_jointHelpers):
            log.error("Namelist lengths and handle lengths doesn't match | len {0} != {1}".format(_l_names,len(ml_jointHelpers)))
            return False
    
        
    
        _d_base['cgmType'] = 'skinJoint'
        
        #Build our handle chain ======================================================
        l_pos = []
        
        if self.buildLeverEnd:
            if not self.hasEndJoint and not self.hasBallJoint:
                if len(ml_jointHelpers) > (self.numControls + int(self.hasLeverJoint)):
                    log.debug("|{0}| >> No end joint, culling...".format(_str_func,_rollCounts))
                    ml_jointHelpers = ml_jointHelpers[:-1]
        elif not self.hasEndJoint and not self.hasBallJoint:
            log.debug("|{0}| >> No end joint, culling...".format(_str_func,_rollCounts))
            ml_jointHelpers = ml_jointHelpers[:-1]
        
        for mObj in ml_jointHelpers:
            l_pos.append(mObj.p_position)
                
        mOrientHelper = self.orientHelper
        ml_handleJoints = JOINT.build_chain(l_pos, parent=True,
                                            worldUpAxis= mOrientHelper.getAxisVector('y+'), orient= False)
        
        if _b_lever:
            log.debug("|{0}| >> lever...".format(_str_func))            
            ml_handleJoints[1].p_parent = False
            #Lever...
            mLever = ml_handleJoints[0]
            #_const = mc.aimConstraint(ml_handleJoints[1].mNode, mLever.mNode, maintainOffset = False,
            #                          aimVector = [0,0,1], upVector = [0,1,0], 
            #                          worldUpType = 'Vector', 
            #                          worldUpVector = self.baseUp)
            #mc.delete()
            log.debug("|{0}| >> lever helper: {1}".format(_str_func,ml_jointHelpers[0]))                        
            _vec =  ml_jointHelpers[0].getAxisVector('y+')
            log.debug("|{0}| >> lever vector: {1}".format(_str_func,_vec))            
            
            SNAP.aim(mLever.mNode, ml_handleJoints[1].mNode, 'z+','y+','vector',
                     _vec)
            
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
            #mJnt.rename(NAMETOOLS.returnCombinedNameFromDict(d))
            for t,v in d.iteritems():
                mJnt.doStore(t,v)
            mJnt.doName()
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
        
        _radius = self.atUtils('get_shapeOffset') or DIST.get_distance_between_points(ml_joints[0].p_position, 
                                                                                      ml_joints[-1].p_position)/ 20
        #_radius = DIST.get_distance_between_points(ml_joints[0].p_position, ml_joints[-1].p_position)/ 20
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
                
            elif not self.buildLeverEnd:
                log.debug("|{0}| >> Non quad setup finding end...".format(_str_func))
                _idx = (int(self.hasLeverJoint) + self.numControls) - 1
                log.debug("|{0}| >> non quad end: {1}".format(_str_func,_idx))
                try:mEnd = ml_handleJoints[(int(self.hasLeverJoint) + self.numControls) - 1]
                except:mEnd=False
                
                if mEnd:
                    log.debug("|{0}| >> non quad end: {1}".format(_str_func,mEnd))                    
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
        if not self.hasEndJoint and not self.buildLeverEnd:
            mEnd = ml_joints[-1]        
            log.debug("|{0}| >> Fixing end: {1}".format(_str_func,mEnd))
            
            if self.hasBallJoint:
                mEnd.doSnapTo(ml_prerigHandles[-1])
            else:
                mEnd.doSnapTo(ml_prerigHandles[-2])
            
            """
            SNAP.aim(mEnd.mNode,
                     ml_templateHandles[-1].mNode,
                     'z+','y+','vector',
                     ml_templateHandles[-1].getAxisVector('y+'))"""
            JOINT.freezeOrientation(mEnd.mNode)
            
        for mJnt in ml_joints:mJnt.rotateOrder = 5
        self.blockState = 'skeleton'#...buffer
        
        return ml_joints
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err,localDat=vars())        

#=============================================================================================================
#>> rig
#=============================================================================================================
#NOTE - self here is a rig Factory....

#d_preferredAngles = {'default':[0,-10, 10]}#In terms of aim up out for orientation relative values, stored left, if right, it will invert
#d_preferredAngles = {'out':10}
d_preferredAngles = {}
d_rotateOrders = {'default':'yxz'}

#Rig build stuff goes through the rig build factory ------------------------------------------------------
def rig_prechecks(self):
    try:
        _str_func = 'rig_prechecks'
        log.debug(cgmGEN.logString_start(_str_func))
        
        mBlock = self.mBlock
        
        if not mBlock.ikSetup:
            self.l_precheckErrors.append('Must have ikSetup currently')
            
        if mBlock.buildLeverEnd and mBlock.numControls < 4:
            self.l_precheckErrors.append('Quad Setup needs at least 4 controls')
        
        str_ikEnd = mBlock.getEnumValueString('ikEnd')
        if mBlock.numControls < 3 and str_ikEnd != 'default':
            self.l_precheckWarnings.append('With less than 3 controls, using ikEnd of default')
            mBlock.ikEnd = 'default'
        elif str_ikEnd == 'default':
            if mBlock.hasBallJoint:
                self.l_precheckErrors.append("default ikEnd and hasBallJoint on. | Fix this setting. If you have a ball, you should probably be a pad or foot")
            
        #str_ikEnd = mBlock.getEnumValueString('ikEnd')
        #ml_templateHandles = mBlock.msgList_get('templateHandles')
        #if not mBlock.ikEnd and ml_templateHandles[-1].getMessage('pivotHelper')
            
        
        #if mBlock.getEnumValueString('squashMeasure') == 'pointDist':
        #    self.l_precheckErrors.append('pointDist squashMeasure mode not recommended')
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err,localDat=vars())        

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
        self.b_ikNeedEnd = False
        self.b_pivotSetup = False
        self.mPivotHelper = False
        self.b_leverEnd = mBlock.buildLeverEnd
        log.debug("|{0}| >> Quad | self.b_leverEnd: {1} ".format(_str_func,self.b_leverEnd))
        
        #Initial option checks ============================================================================    
        #if mBlock.scaleSetup:
        #    raise NotImplementedError,"Haven't setup scale yet."
        #if mBlock.ikSetup >=1:
            #raise NotImplementedError,"Haven't setup ik mode: {0}".format(ATTR.get_enumValueString(mBlock.mNode,'ikSetup'))
            
        
        self.str_rigSetup = ATTR.get_enumValueString(mBlock.mNode,'rigSetup')
        
        #Single chain ============================================================================
        self.b_singleChain = False
        ml_joints = self.d_joints['ml_skinJoints']
        len_joints = len(ml_joints)
        len_prerigHandles = len(ml_prerigHandles)
        
        if mBlock.numControls <= 2:
            self.b_singleChain = True
            if len_joints ==1:
                self.b_ikNeedEnd = True
    
            
        log.debug("|{0}| >> Single chain | self.b_singleChain: {1} ".format(_str_func,self.b_singleChain))
        
        #FollowParent ============================================================================
        self.b_followParentBank = False
        self.mPivotResult_moduleParent = False
        if mBlock.followParentBank:
            mModuleParent = self.d_module['mModuleParent']
            if mModuleParent:
                mPivotResult_moduleParent = mModuleParent.rigNull.getMessageAsMeta('pivotResultDriver')
                if mPivotResult_moduleParent:
                    self.mPivotResult_moduleParent = mPivotResult_moduleParent
                    self.b_followParentBank = True
        log.debug("|{0}| >> Follow parentBank | self.b_followParentBank: {1} ".format(_str_func,self.b_followParentBank))
        log.debug("|{0}| >> Follow parentBank | self.mPivotResult_moduleParent: {1} ".format(_str_func,self.mPivotResult_moduleParent))
        log.debug(cgmGEN._str_subLine)    
        
        #Lever ============================================================================    
        _b_lever = False
        self.b_leverJoint = False
        ml_templateHandlesUse = copy.copy(ml_templateHandles)
        ml_fkShapeHandles = copy.copy(ml_prerigHandles)
        if mBlock.buildLeverBase:
            _b_lever = True        
            if mBlock.hasLeverJoint:
                self.b_leverJoint = True
            else:
                log.debug("|{0}| >> Need leverJoint | self.b_leverJoint ".format(_str_func))
            self.mRootTemplateHandle = ml_templateHandles[1]
            ml_templateHandlesUse = ml_templateHandlesUse[1:]
            
            ml_fkShapeHandles = ml_fkShapeHandles[1:]
        self.b_lever = _b_lever
            
        self.ml_fkShapeTargets = ml_fkShapeHandles

        if not self.b_singleChain:
            self.int_templateHandleMidIdx = MATH.get_midIndex(len(ml_templateHandlesUse))
            self.mMidTemplateHandle = ml_templateHandles[self.int_templateHandleMidIdx]
                
            log.debug("|{0}| >> Lever: {1}".format(_str_func,self.b_lever))    
            log.debug("|{0}| >> self.mRootTemplateHandle : {1}".format(_str_func,self.mRootTemplateHandle))
            log.debug("|{0}| >> self.mMidTemplateHandle : {1}".format(_str_func,self.mMidTemplateHandle))    
            log.debug("|{0}| >> Mid self.int_templateHandleMidIdx idx: {1}".format(_str_func,self.int_templateHandleMidIdx))
        
        
            #Pivot checks ============================================================================
            mPivotHolderHandle = ml_templateHandles[-1]
            self.b_pivotSetup = False
            self.mPivotHelper = False
            if mPivotHolderHandle.getMessage('pivotHelper'):
                log.debug("|{0}| >> Pivot setup needed".format(_str_func))
                self.b_pivotSetup = True
                self.mPivotHelper = mPivotHolderHandle.getMessageAsMeta('pivotHelper')
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
        
        #Squash stretch logic  =================================================================================
        log.debug("|{0}| >> Squash stretch..".format(_str_func))
        self.b_scaleSetup = mBlock.scaleSetup
        self.b_squashSetup = False
        
        if not self.md_roll:
            log.debug("|{0}| >> No roll joints found for squash and stretch to happen".format(_str_func))
            
        else:
            
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
            
            #self.d_squashStretch['additiveScaleEnds'] = mBlock.scaleSetup
            self.d_squashStretch['extraSquashControl'] = mBlock.squashExtraControl
            self.d_squashStretch['squashFactorMax'] = mBlock.squashFactorMax
            self.d_squashStretch['squashFactorMin'] = mBlock.squashFactorMin
            
            log.debug("|{0}| >> self.d_squashStretch..".format(_str_func))    
            pprint.pprint(self.d_squashStretch)
            
            #Check for mid control and even handle count to see if w need an extra curve
            if mBlock.segmentMidIKControl:
                if MATH.is_even(mBlock.numControls):
                    self.d_squashStretchIK['sectionSpans'] = 2
                    
            if self.d_squashStretchIK:
                log.debug("|{0}| >> self.d_squashStretchIK..".format(_str_func))    
                pprint.pprint(self.d_squashStretchIK)
            
            
            if not self.b_scaleSetup:
                pass
            
            log.debug("|{0}| >> self.b_scaleSetup: {1}".format(_str_func,self.b_scaleSetup))
            log.debug("|{0}| >> self.b_squashSetup: {1}".format(_str_func,self.b_squashSetup))
            
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
        self.b_cullFKEnd = False
        self.b_ikNeedFullChain = False
        l= []
        
        str_ikEnd = ATTR.get_enumValueString(mBlock.mNode,'ikEnd')
        log.debug("|{0}| >> IK End: {1}".format(_str_func,format(str_ikEnd)))
        
        
        if self.b_leverEnd:
            self.int_handleEndIdx -=1
        else:
            if not mBlock.ikEnd:
                if mBlock.hasEndJoint:
                    self.int_handleEndIdx -=1
                if mBlock.hasBallJoint:
                    self.int_handleEndIdx -=1                
            elif str_ikEnd in ['foot']:
                if mBlock.hasEndJoint:
                    self.mToe = self.ml_handleTargets.pop(-1)
                    log.debug("|{0}| >> mToe: {1}".format(_str_func,self.mToe))
                    self.int_handleEndIdx -=1
                if mBlock.hasBallJoint:
                    self.mBall = self.ml_handleTargets.pop(-1)
                    log.debug("|{0}| >> mBall: {1}".format(_str_func,self.mBall))        
                    self.int_handleEndIdx -=1
                    
            elif str_ikEnd in ['tipEnd','tipBase','tipCombo']:
                log.debug("|{0}| >> tip setup...".format(_str_func))        
                if not mBlock.hasEndJoint:
                    if str_ikEnd == 'tipEnd':
                        self.b_ikNeedEnd = True
                        log.debug("|{0}| >> Need IK end joint".format(_str_func))
                    elif str_ikEnd == 'tipBase':
                        pass
                elif str_ikEnd == 'tipBase':
                    self.int_handleEndIdx -=1
                    self.b_cullFKEnd = True            
            """
            if str_ikEnd in ['foot']:
                if mBlock.hasEndJoint:
                    self.mToe = self.ml_handleTargets.pop(-1)
                    log.debug("|{0}| >> mToe: {1}".format(_str_func,self.mToe))
                    self.int_handleEndIdx -=1
                if mBlock.hasBallJoint:
                    self.mBall = self.ml_handleTargets.pop(-1)
                    log.debug("|{0}| >> mBall: {1}".format(_str_func,self.mBall))        
                    self.int_handleEndIdx -=1
                    
            elif str_ikEnd in ['tipEnd','tipBase','tipCombo']:
                log.debug("|{0}| >> tip setup...".format(_str_func))        
                if not mBlock.hasEndJoint:
                    if str_ikEnd == 'tipEnd':
                        self.b_ikNeedEnd = True
                        log.debug("|{0}| >> Need IK end joint".format(_str_func))
                    elif str_ikEnd == 'tipBase':
                        pass
                elif str_ikEnd == 'tipBase':
                    self.int_handleEndIdx -=1
                    self.b_cullFKEnd = True"""
    
                    
        if str_ikEnd in ['tipCombo'] or self.b_leverEnd:
            log.debug("|{0}| >> Need Full IK chain...".format(_str_func))
            self.b_ikNeedFullChain = True
                
        #elif mBlock.ikEndIndex > 1:
            #log.debug("|{0}| >> Using ikEndIndex...".format(_str_func))        
            #self.int_handleEndIdx = - mBlock.ikEndIndex
        log.debug("|{0}| >> self.b_cullFKEnd: {1}".format(_str_func,
                                                            self.b_cullFKEnd))            
        log.debug("|{0}| >> self.ml_handleTargets: {1} | {2}".format(_str_func,
                                                                         len(self.ml_handleTargets),
                                                                         self.ml_handleTargets))
        
        log.debug("|{0}| >> End self.int_handleEndIdx idx: {1} | {2}".format(_str_func,self.int_handleEndIdx,
                                                                                 ml_handleJoints[self.int_handleEndIdx]))
        if not self.b_singleChain:
            ml_use = ml_handleJoints[:self.int_handleEndIdx]
            if len(ml_use) == 1:
                mid=0
                mMidHandle = ml_use[0]
            else:
                mid = MATH.get_midIndex(len(ml_use))
                mMidHandle = ml_use[mid]
            self.int_handleMidIdx = mid
        
        
        #if self.b_lever:
            #log.debug("|{0}| >> lever pop...".format(_str_func))        
            #self.int_templateHandleMidIdx +=1
        
        
    
            log.debug("|{0}| >> Mid self.int_handleMidIdx idx: {1} | {2}".format(_str_func,self.int_handleMidIdx,
                                                                                 ml_handleJoints[self.int_handleMidIdx]))    
    
        
        
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
        self.v_offset = self.mPuppet.atUtils('get_shapeOffset')
        """
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
        """
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
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err,localDat=vars())        

@cgmGEN.Timer
def rig_skeleton(self):
    try:
        _short = self.d_block['shortName']
        _str_func = 'rig_skeleton'
        log.debug("|{0}| >> ...".format(_str_func)+cgmGEN._str_hardBreak)
        log.debug(self)
        
        mBlock = self.mBlock
        mRigNull = self.mRigNull
        mPrerigNull = mBlock.prerigNull
        ml_jointsToConnect = []
        ml_jointsToHide = []
        ml_blendJoints = []
        ml_joints = mRigNull.msgList_get('moduleJoints')
        ml_handleJoints = mPrerigNull.msgList_get('handleJoints')
        ml_prerigHandles = mBlock.msgList_get('prerigHandles')
        ml_jointHelpers = mBlock.msgList_get('jointHelpers')
        
        self.d_joints['ml_moduleJoints'] = ml_joints
        str_ikBase = ATTR.get_enumValueString(mBlock.mNode,'ikBase')        
        
        reload(BLOCKUTILS)
        BLOCKUTILS.skeleton_pushSettings(ml_joints,self.d_orientation['str'],
                                         self.d_module['mirrorDirection'],
                                         d_rotateOrders)#d_preferredAngles)
        
        
        log.debug("|{0}| >> rig chain...".format(_str_func))              
        ml_rigJoints = BLOCKUTILS.skeleton_buildDuplicateChain(mBlock,
                                                               ml_joints, None ,
                                                               mRigNull,'rigJoints',
                                                               blockNames=False,
                                                               cgmType = 'rigJoint',
                                                               connectToSource = 'rig')
        #pprint.pprint(ml_rigJoints)
        
        
        #...fk chain ----------------------------------------------------------------------------------------------
        log.debug("|{0}| >> fk_chain".format(_str_func))
        #ml_fkJoints = BLOCKUTILS.skeleton_buildHandleChain(mBlock,'fk','fkJoints')
        
        
        ml_fkJoints = BLOCKUTILS.skeleton_buildDuplicateChain(mBlock, ml_handleJoints,
                                                              'fk',mRigNull,'fkJoints',
                                                              blockNames=False,cgmType = 'frame',
                                                              connectToSource='fk')
        ml_jointsToHide.extend(ml_fkJoints)
        
        ml_handleJointsToUse = ml_handleJoints
        
        #if self.int_handleEndIdx < -1:
            #log.debug("|{0}| >> culling extra fk joints...".format(_str_func))
            
        
        ml_fkJointsToUse = ml_fkJoints
        
        
        #...lever -------------------------------------------------------------------------------------------------
        if self.b_lever:
            log.debug("|{0}| >> Lever...".format(_str_func)+'-'*40)          
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
                         mBlock.orientHelper.getAxisVector('y+'))
                reload(JOINT)
                JOINT.freezeOrientation(mLever.mNode)
                mRigNull.connectChildNode(mLever,'leverFK','rigNull')
            
        #Followbase ============================================================
        if self.b_followParentBank:
            log.debug("|{0}| >> followParentBank joints...".format(_str_func)+'-'*40)
            
            mFollowBase = cgmMeta.validateObjArg(mc.joint(),setClass=True)#ml_fkJointsToUse[0].doDuplicate(po=True)
            mFollowBase.p_parent = False
            mFollowBase.p_position = ml_fkJointsToUse[0].p_position
            
            
            mFollowMid = mFollowBase.doDuplicate(po=True)
            if mBlock.hasEndJoint:
                _idxUse = -1
            else:
                _idxUse = -2
                
            #self.int_handleEndIdx
            mFollowMid.p_position = ml_jointHelpers[_idxUse].p_position
            mFollowMid.p_parent = mFollowBase        
            
            mFollowEnd = mFollowBase.doDuplicate(po=True)
            mFollowEnd.p_position = self.ml_templateHandles[-1].p_position
            mFollowEnd.p_parent = mFollowMid
            
            JOINT.orientChain([mFollowBase.mNode, mFollowMid, mFollowEnd.mNode],
                              worldUpAxis=mBlock.orientHelper.getAxisVector('y+'))
            
            l_tags = ['start','mid','end']
            for i,mJnt in enumerate([mFollowBase,mFollowMid,mFollowEnd]):
                mJnt.doStore('cgmName',self.d_module['partName'] + '_followBase')
                mJnt.doStore('cgmType',l_tags[i])
                mJnt.doName()
            
            mFollowEnd.doName()        
            ml_followJoints = [mFollowBase,mFollowMid,mFollowEnd]
            mRigNull.msgList_connect('followParentBankJoints', [mFollowBase,mFollowMid,mFollowEnd])
            ml_jointsToConnect.extend(ml_followJoints)    
        
        
        #...ik joints-------------------------------------------------------------------------------------------
        if mBlock.ikSetup:
            log.debug("|{0}| >> ikSetup on. Building blend and IK chains...".format(_str_func))  
            ml_blendJoints = BLOCKUTILS.skeleton_buildHandleChain(self.mBlock,'blend','blendJoints')
            ml_ikJoints = BLOCKUTILS.skeleton_buildHandleChain(self.mBlock,'ik','ikJoints')
            
            
            if self.b_ikNeedFullChain:
                log.debug("|{0}| >> Creating full IK chain...".format(_str_func))          
                ml_ikFullChain = BLOCKUTILS.skeleton_buildDuplicateChain(mBlock,
                                                                         ml_ikJoints, 'fullChain', 
                                                                         mRigNull,
                                                                         'ikFullChainJoints',
                                                                         connectToSource = 'ikFullChain',
                                                                         cgmType = 'frame')
                
                for mJnt in ml_ikFullChain:
                    mJnt.rotateOrder = 0
                """
                mEndIK = ml_prerigHandles[-1].doCreateAt('joint',setClass=True)
                mEndIK.p_parent = ml_ikFullChain[-1]
                ml_ikFullChain.append(mEndIK)
                mEndIK.rotate = 0,0,0
                
                #mOrientHelper = mBlock.orientHelper
                JOINT.orientChain(ml_ikFullChain[-2:],
                                  relativeOrient=False,
                                  worldUpAxis= ml_prerigHandles[-1].getAxisVector('z+'))
                                  #worldUpAxis= ml_ikFullChain[-2].getAxisVector('z+'))
                """
                mRigNull.msgList_connect('ikFullChainJoints',ml_ikFullChain)
                ml_jointsToConnect.extend(ml_ikFullChain)
                
            if self.b_ikNeedEnd:
                mEndIK = ml_prerigHandles[-1].doCreateAt('joint',setClass=True)
                mEndIK.p_parent = ml_ikJoints[-1]
                ml_ikJoints.append(mEndIK)
                mEndIK.rotate = 0,0,0
                mEndIK.rename("ikEnd_jnt")
                mOrientHelper = mBlock.orientHelper            
                JOINT.orientChain(ml_ikJoints[-1:],
                                 relativeOrient=False,
                                 worldUpAxis= mOrientHelper.getAxisVector('y+'))            
                mRigNull.msgList_connect('ikJoints',ml_ikJoints)
            
                
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
            log.debug("|{0}| >> Handles...".format(_str_func))            
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
            log.debug("|{0}| >> IK Drivers...".format(_str_func))            
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
        md_midHandles = {}
        
        if self.md_roll:#Segment stuff ===================================================================
            log.debug("|{0}| >> Segment...".format(_str_func))
            
            log.debug("|{0}| >> Handle Joints...".format(_str_func))
            log.debug("|{0}| >> Targets: {1} | {2} ".format(_str_func, self.int_handleEndIdx, ml_parentJoints))
            
            if mBlock.buildLeverEnd:
                ml_targets = self.ml_handleTargets
                
            else:
                ml_targets = self.ml_handleTargetsCulled
            
            ml_handleJoints = BLOCKUTILS.skeleton_buildDuplicateChain(mBlock,
                                                                      ml_targets,#ml_parentJoints,#ml_parentJoints[:self.int_handleEndIdx+1],
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
                                                                            connectToSource = 'segHandle_{0}'.format(i),
                                                                            cgmType = 'segHandle')
                log.debug("|{0}| >> created ... {1}".format(_str_func, ml_segmentHandles))#----------------------------
    
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
                        
                log.debug
                if mBlock.segmentMidIKControl:
                    ml_segmentMidHandles = BLOCKUTILS.skeleton_buildDuplicateChain(mBlock,
                                                                                [ml_set[0],ml_set[-1]], None, 
                                                                                mRigNull,
                                                                                'segmentMidHandles_{0}'.format(i),
                                                                                connectToSource = 'segMidHandle_{0}'.format(i),
                                                                                cgmType = 'segHandle')
                    ml_jointsToConnect.extend(ml_segmentMidHandles)
                    
                    for ii,mJnt in enumerate(ml_segmentMidHandles):
                        mJnt.doStore('cgmTypeModifier',"segMid_{0}".format(i))
                        mJnt.doName()
                        mJnt.p_parent = ml_segmentHandles[0].p_parent#...used to be i
                        
                    
                    
                #Seg chain -------------------------------------------------------------------------------------
                log.debug("|{0}| >> SegChain {1} ...".format(_str_func, i))
                ml_segmentChain = BLOCKUTILS.skeleton_buildDuplicateChain(mBlock,
                                                                          ml_set, None, 
                                                                          mRigNull,'segJoints_{0}'.format(i),
                                                                          connectToSource = 'seg_{0}'.format(i),
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
                
                
                if mBlock.segmentMidIKControl:
                    log.debug("|{0}| >> Creating mid control: {1}".format(_str_func,i))  
                    #Lever...
                    mMidIK = ml_set[0].doDuplicate(po=True)
                    mMidIK.cgmName = 'segMid_{0}'.format(i)
                    mMidIK.p_parent = False
                    mMidIK.doName()
                
                    mMidIK.p_position = DIST.get_average_position([ml_set[0].p_position,
                                                                   ml_set[-1].p_position])
                
                    SNAP.aim(mMidIK.mNode, ml_set[-1].mNode, 'z+','y+','vector',
                             mBlock.orientHelper.getAxisVector('y+'))
                    
                    JOINT.freezeOrientation(mMidIK.mNode)
                    
                    mRigNull.connectChildNode(mMidIK,'controlSegMidIK_{0}'.format(i),'rigNull')            
                
                    
        
        """
        if self.b_segmentSetup:
            log.debug("|{0}| >> segment necessary...".format(_str_func))
                
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
            log.debug("|{0}| >> rollSetup joints...".format(_str_func))
            
             
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
                
                if not self.b_leverEnd:
                    if ml_joints[i] == self.mIKEndSkinJnt:#last joint
                        log.debug("|{0}| >> End joint: {1} ".format(_str_func,mJnt))
                        mJnt.p_parent = ml_blendJoints[self.int_handleEndIdx]
                    else:
                        mJnt.p_parent = ml_drivers[-1]
                else:
                    if ml_joints[i] == ml_joints[-1]:#last joint
                        log.debug("|{0}| >> End joint: {1} ".format(_str_func,mJnt))
                        mJnt.p_parent = ml_blendJoints[-1]
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
                    
        #Mirror if side...
        if self.d_module['mirrorDirection'] == 'Left':
            log.debug("|{0}| >> Mirror direction ...".format(_str_func))
            ml_fkAttachJoints = BUILDUTILS.joints_mirrorChainAndConnect(self, ml_fkJoints)
            ml_jointsToConnect.extend(ml_fkAttachJoints)
            
            """
            ml_fkAttachJoints = BLOCKUTILS.skeleton_buildDuplicateChain(mBlock, ml_fkJoints,
                                                                        'fkAttach',mRigNull,'fkAttachJoints',
                                                                        blockNames=False,cgmType = 'frame')
            
            self.atUtils('joints_flipChainForBehavior', ml_fkJoints)
            ml_jointsToConnect.extend(ml_fkAttachJoints)
            for i,mJoint in enumerate(ml_fkAttachJoints):
                log.debug("Mirror connect: %s | %s"%(i,mJoint.p_nameShort))
                ml_fkJoints[i].connectChildNode(ml_fkAttachJoints[i],"fkAttach","rootJoint")
                #attributes.doConnectAttr(("%s.rotateOrder"%mJoint.mNode),("%s.rotateOrder"%ml_fkDriverJoints[i].mNode))
                cgmMeta.cgmAttr(ml_fkJoints[i].mNode,"rotateOrder").doConnectOut("%s.rotateOrder"%ml_fkAttachJoints[i].mNode)
                mJoint.p_parent = ml_fkJoints[i]"""
        
        if self.b_pivotSetup:
            log.debug("|{0}| >> Pivot joints...".format(_str_func))        
            if self.mBall:
                log.debug("|{0}| >> Ball joints...".format(_str_func))
                
                mBallJointPivot = self.mBall.doCreateAt('joint',copyAttrs=True)#dup ball in place
                mBallJointPivot.parent = False
                mBallJointPivot.cgmName = 'ball'
                mBallJointPivot.addAttr('cgmType','pivotJoint')
                mBallJointPivot.doName()
                mRigNull.connectChildNode(mBallJointPivot,"pivot_ballJoint","rigNull")
                ml_jointsToConnect.append(mBallJointPivot)
        
                #Ball wiggle pivot
                mBallWiggleJointPivot = mBallJointPivot.doDuplicate(po = True)#dup ball in place
                mBallWiggleJointPivot.parent = False
                mBallWiggleJointPivot.cgmName = 'ballWiggle'
                mBallWiggleJointPivot.addAttr('cgmType','pivotJoint')            
                mBallWiggleJointPivot.doName()
                mRigNull.connectChildNode(mBallWiggleJointPivot,"pivot_ballWiggle","rigNull") 
                ml_jointsToConnect.append(mBallWiggleJointPivot)
                
                if not self.mToe:
                    log.debug("|{0}| >> Making toe joint...".format(_str_func))
                    mToe = mBallJointPivot.doDuplicate()
                    mToe.doSnapTo(self.mPivotHelper.pivotFront.mNode)
                    mToe.cgmName = 'toe'
                    mToe.addAttr('cgmType','pivotJoint')
                    mToe.doName()
                    mRigNull.connectChildNode(mToe,"toe_helpJoint","rigNull") 
                    mToe.p_parent = ml_ikJoints[-1]
                    ml_jointsToConnect.append(mToe)
                    
    
        
            
        #...joint hide -----------------------------------------------------------------------------------
        for mJnt in ml_jointsToHide:
            try:
                mJnt.drawStyle =2
            except:
                mJnt.radius = .00001
                
        #...connect... 
        self.fnc_connect_toRigGutsVis( ml_jointsToConnect )        
        
        #cgmGEN.func_snapShot(vars())     
        return
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err,localDat=vars())        

@cgmGEN.Timer
def rig_digitShapes(self):
    try:
        _short = self.d_block['shortName']
        _str_func = 'rig_digitShapes'
        log.debug("|{0}| >>  {1}".format(_str_func,self)+ '-'*80)
        
        #_str_func = '[{0}] > rig_shapes'.format(_short)
        log.debug("|{0}| >> ...".format(_str_func))  
        
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
        
        _bbSize = TRANS.bbSize_get(self.mRootTemplateHandle.loftCurve.mNode,shapes=True)
        _size = MATH.average(_bbSize[1:])
        
        
        _offset = self.v_offset / 4.0
        
        d_directions = {'up':'y+','down':'y-','in':'x+','out':'x-'}
        str_settingsDirections = d_directions.get(mBlock.getEnumValueString('settingsDirection'),'y+')
        
        ml_fkCastTargets = self.mRigNull.msgList_get('fkAttachJoints')
        if not ml_fkCastTargets:
            ml_fkCastTargets = copy.copy(ml_fkJoints)

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
                #bb_ik = mHandleFactory.get_axisBox_size(mProxyHelper.mNode)
                bb_ik = POS.get_bb_size(mProxyHelper.mNode,True,'maxFill')
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
                
                if str_ikEnd == 'default':
                    mIKTemplateHandle = ml_templateHandles[-1]
                    #bb_ik = mHandleFactory.get_axisBox_size(mIKTemplateHandle.mNode)
                    bb_ik = POS.get_bb_size(mIKTemplateHandle.mNode,True,mode='maxFill')
                    
                    _ik_shape = CURVES.create_fromName('cube', size = bb_ik)
                    #ATTR.set(_ik_shape,'scale', 1.5)
                    
                    mIKShape = cgmMeta.validateObjArg(_ik_shape, 'cgmObject',setClass=True)
                    mIKShape.doSnapTo(mIKCrv)
                    CORERIG.shapeParent_in_place(mIKCrv.mNode, mIKShape.mNode, False)

                    
                else:
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
            mKnee = ml_fkCastTargets[self.int_templateHandleMidIdx].doCreateAt(setClass=True)
            #size_knee =  POS.get_bb_size(ml_templateHandles[self.int_templateHandleMidIdx].mNode)
            
            crv = CURVES.create_controlCurve(mKnee, shape='sphere',
                                             direction = _jointOrientation[0]+'+',
                                             sizeMode = 'fixed',
                                             size = _size/2)            
            
            
            CORERIG.shapeParent_in_place(mKnee.mNode, crv, False)
            
            mKnee.doSnapTo(ml_ikJoints[1].mNode)
    
            #Get our point for knee...
            #mKnee.p_position = self.UTILS.get_midIK_basePosOrient(self,
            #                                                      self.ml_handleTargetsCulled,False)
    
            mKnee.p_position = self.mBlock.atUtils('prerig_get_rpBasePos',self.ml_handleTargetsCulled,False)
            
            CORERIG.match_orientation(mKnee.mNode, mIKCrv.mNode)
            #mc.makeIdentity(mKnee.mNode, apply = True, t=0, r=0,s=1,n=0,pn=1)
            mHandleFactory.color(mKnee.mNode, controlType = 'sub')
    
            mKnee.doCopyNameTagsFromObject(ml_fkJoints[1].mNode,ignore=['cgmType','cgmTypeModifier'])
            mKnee.doStore('cgmAlias','midIK')            
            mKnee.doName()
    
            self.mRigNull.connectChildNode(mKnee,'controlIKMid','rigNull')#Connect
            
            #Base IK...---------------------------------------------------------------------------------
            log.debug("|{0}| >> baseIK...".format(_str_func))
        
            mIK_templateHandle = self.mRootTemplateHandle
            #bb_ik = POS.get_bb_size(mIK_templateHandle.loftCurve.mNode,True,'maxFill')
            #bb_ik = mHandleFactory.get_axisBox_size(mIK_templateHandle.mNode)
            _ik_shape = CURVES.create_fromName('sphere', size = [_size,_size,_size])
            ATTR.set(_ik_shape,'scale', 1.1)
        
            mIKBaseShape = cgmMeta.validateObjArg(_ik_shape, 'cgmObject',setClass=True)
        
            mIKBaseShape.doSnapTo(mIK_templateHandle)
            #pos_ik = POS.get_bb_center(mProxyHelper.mNode)
            #SNAPCALLS.get_special_pos(mEndHandle.p_nameLong,
            #                                   'axisBox','z+',False)                
        
            #mIKBaseShape.p_position = pos_ik
            mIKBaseCrv = ml_ikJoints[0].doCreateAt()
            mIKBaseCrv.doCopyNameTagsFromObject(ml_fkJoints[0].mNode,ignore=['cgmType'])
            CORERIG.shapeParent_in_place(mIKBaseCrv.mNode, mIKBaseShape.mNode, False)                            
        
            mIKBaseCrv.doStore('cgmTypeModifier','ikBase')
            mIKBaseCrv.doName()
        
            mHandleFactory.color(mIKBaseCrv.mNode, controlType = 'main',transparent=True)
        
        
            #CORERIG.match_transform(mIKBaseCrv.mNode,ml_ikJoints[0].mNode)
            mHandleFactory.color(mIKBaseCrv.mNode, controlType = 'main')        
            self.mRigNull.connectChildNode(mIKBaseCrv,'controlIKBase','rigNull')#Connect       
            
            
        #FollowParent =============================================================================
        if self.b_followParentBank:
            log.debug("|{0}| >> follow parent handle...".format(_str_func))
            ml_followParentBankJoints = mRigNull.msgList_get('followParentBankJoints')
    
            mDag = ml_followParentBankJoints[-1].doCreateAt(setClass=True)
    
            #if not bb_ik:
                #bb_ik = mHandleFactory.get_axisBox_size(ml_templateHandles[-1].mNode)
    
            _ik_shape = CURVES.create_fromName('cube', size =[v*.75 for v in [_size,_size,_size]])            
            SNAP.go(_ik_shape,mDag.mNode)
    
            CORERIG.shapeParent_in_place(mDag.mNode, _ik_shape,False)
    
            mDag.doStore('cgmName',self.d_module['partName'] + '_followBank')
            mDag.doStore('cgmTypeModifier','ik')
            mDag.doName()
            mHandleFactory.color(mDag.mNode, controlType = 'sub')                
    
            self.mRigNull.connectChildNode(mDag,'controlFollowParentBank','rigNull')#            
            log.debug(cgmGEN._str_subLine)
                    
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
            
            mLeverDirect = mRigNull.getMessageAsMeta('leverDirect')
            mLeverFK = mRigNull.getMessageAsMeta('leverFK')
            
            mLeverControlCast = mLeverDirect
            if not mLeverControlCast:
                mLeverControlCast = mLeverFK
                
            log.debug("|{0}| >> mLeverControlCast: {1}".format(_str_func,mLeverControlCast))            
            
    
            dist_lever = DIST.get_distance_between_points(ml_prerigHandles[0].p_position,
                                                          ml_prerigHandles[1].p_position)
            log.debug("|{0}| >> Lever dist: {1}".format(_str_func,dist_lever))
    
            #Dup our rig joint and move it 
            mDup = mLeverControlCast.doDuplicate(po=True)
            mDup.p_parent = mLeverControlCast
            mDup.resetAttrs()
            ATTR.set(mDup.mNode, 't{0}'.format(_jointOrientation[0]), dist_lever * .5)
    
            l_lolis = []
            l_starts = []
            
            size_loli = _size * .3
            offset_loli = _bbSize[1] + (_offset * 1.25)
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
                p_start = mDup.getPositionByAxisDistance(axis, _offset*2.0)
                l_starts.append(p_start)
                line = mc.curve (d=1, ep = [p_start,p_end], os=True)
                l_lolis.extend([ball,line])
        
            CORERIG.shapeParent_in_place(mLeverFK.mNode,l_lolis,False)
            
            ATTR.set(mDup.mNode, 't{0}'.format(_jointOrientation[0]), dist_lever * .8)            
            ml_clavShapes = BUILDUTILS.shapes_fromCast(self, 
                                                       targets= [mLeverControlCast.mNode,
                                                                 #ml_fkJoints[0].mNode],
                                                                  mDup.mNode],
                                                             aimVector= self.d_orientation['vectorOut'],
                                                             connectionPoints = 5,
                                                             f_factor=0,
                                                             offset=_offset,
                                                             mode = 'frameHandle')
            CORERIG.shapeParent_in_place(mLeverFK.mNode,
                                         ml_clavShapes[0].mNode,
                                         False,replaceShapes=False)            
            mHandleFactory.color(mLeverFK.mNode, controlType = 'main')
            mDup.delete()
            for mShape in ml_clavShapes:
                try:mShape.delete()
                except:pass
                
            #limbRoot ------------------------------------------------------------------------------
            log.debug("|{0}| >> Lever -- limbRoot".format(_str_func))
            mLimbRootHandle = ml_prerigHandles[1]
            mLimbRoot = ml_fkCastTargets[1].doCreateAt()
        
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
            ml_targets = ml_fkCastTargets
            
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
        
        
        #FK/Ik =========================================================================================    
        log.debug("|{0}| >> Frame shape cast...".format(_str_func))
        ml_targets = [mObj.mNode for mObj in self.ml_handleTargets]
        if mBlock.hasEndJoint:
            ml_targets.pop(-1)
            
        ml_fkShapes = self.atBuilderUtils('shapes_fromCast',
                                          offset = _offset,
                                          targets = ml_targets,
                                          connectionPoints = 5,
                                          mode = 'frameHandle')#'simpleCast')
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

        
        #Handles =======================================================================================    
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
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err,localDat=vars())        

@cgmGEN.Timer
def rig_shapes(self):
    try:
        _short = self.d_block['shortName']
        _str_func = 'rig_shapes'
        log.debug("|{0}| >> ...".format(_str_func)+cgmGEN._str_hardBreak)
        log.debug(self)        
        #_str_func = '[{0}] > rig_shapes'.format(_short)
        
        mBlock = self.mBlock
        
        _offset = self.v_offset
        str_rigSetup = ATTR.get_enumValueString(_short,'rigSetup')
        
        
        log.debug("|{0}| >> Making fkShapeTargets ".format(_str_func))
        #This is from a bug that Benn reported where a prerig handle we had been using was rotated odd and throwing off the cast
        self.ml_fkShapeTargetDags = []
        for mObj in self.ml_fkShapeTargets:
            mDag = mObj.doCreateAt(setClass='cgmObject')
            self.ml_fkShapeTargetDags.append(mDag)
            
        if len(self.ml_fkShapeTargetDags)>1:
            self.ml_fkShapeTargetDags[-1].p_orient = self.ml_fkShapeTargetDags[-2].p_orient

        
        if str_rigSetup == 'digit':
            str_profile = mBlock.blockProfile#ATTR.get_enumValueString(_short,'blockProfile')
            if str_profile in ['finger','thumb','toe'] and not self.b_singleChain:
                return rig_digitShapes(self)
            _offset = _offset/2.0
        
        mRigNull = self.mRigNull
        
        ml_templateHandles = mBlock.msgList_get('templateHandles')
        ml_prerigHandleTargets = self.mBlock.atBlockUtils('prerig_getHandleTargets')
        ml_ikJoints = mRigNull.msgList_get('ikJoints',asMeta=True)
        ml_blendJoints = self.mRigNull.msgList_get('blendJoints')
        ml_ikFullChain = mRigNull.msgList_get('ikFullChainJoints')
        ml_rigJoints = mRigNull.msgList_get('rigJoints')
        
        ml_fkJoints = self.mRigNull.msgList_get('fkJoints')
        
        ml_fkCastTargets = self.mRigNull.msgList_get('fkAttachJoints')
        if not ml_fkCastTargets:
            ml_fkCastTargets = copy.copy(ml_fkJoints)
            
        #mIKEnd = ml_prerigHandleTargets[-1]
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

        #Pivots =======================================================================================
        mPivotHolderHandle = ml_templateHandles[-1]
        mPivotHelper = mPivotHolderHandle.getMessageAsMeta('pivotHelper')
        if mPivotHelper:
            log.debug("|{0}| >> Pivot shapes...".format(_str_func))            
            mBlock.atBlockUtils('pivots_buildShapes', mPivotHolderHandle.pivotHelper, mRigNull)


        #Lever =============================================================================
        if self.b_lever:
            log.debug("|{0}| >> Lever...".format(_str_func))
            mLeverControlJoint = mRigNull.getMessageAsMeta('leverDirect')
            mLeverControlFK =  mRigNull.getMessageAsMeta('leverFK')
            if not mLeverControlJoint:
                mLeverControlJoint = mLeverControlFK
            else:
                mLeverControlJoint = mLeverControlJoint
            log.debug("|{0}| >> mLeverControlJoint: {1}".format(_str_func,mLeverControlJoint))            
    
            dist_lever = DIST.get_distance_between_points(ml_prerigHandles[0].p_position,
                                                          ml_prerigHandles[1].p_position)
            log.debug("|{0}| >> Lever dist: {1}".format(_str_func,dist_lever))
    
            #Dup our rig joint and move it 
            mDup = mLeverControlJoint.doDuplicate()
            mDup.p_parent = mLeverControlJoint
    
            mDup.resetAttrs()
            ATTR.set(mDup.mNode, 't{0}'.format(_jointOrientation[0]), dist_lever * .8)
    
            mDup2 = mDup.doDuplicate()
            ATTR.set(mDup2.mNode, 't{0}'.format(_jointOrientation[0]), dist_lever * .25)
    
    
            ml_clavShapes = BUILDUTILS.shapes_fromCast(self, targets= [mDup2.mNode,
                                                                       #ml_fkJoints[0].mNode],
                                                                       mDup.mNode],
                                                             aimVector= self.d_orientation['vectorOut'],
                                                             offset=_offset,
                                                             f_factor=0,
                                                             mode = 'frameHandle')
    
            mHandleFactory.color(ml_clavShapes[0].mNode, controlType = 'main')        
            CORERIG.shapeParent_in_place(mLeverControlFK.mNode,ml_clavShapes[0].mNode, True, replaceShapes=True)
            #CORERIG.shapeParent_in_place(mLeverFKJnt.mNode,ml_clavShapes[0].mNode, False, replaceShapes=True)
    
            mc.delete([mShape.mNode for mShape in ml_clavShapes] + [mDup.mNode,mDup2.mNode])
    
            #limbRoot ------------------------------------------------------------------------------
            log.debug("|{0}| >> LimbRoot".format(_str_func))
            idx = 0
            if self.b_lever:
                idx = 1
            mLimbRootHandle = ml_prerigHandles[idx]
            mLimbRoot = ml_fkJoints[0].rigJoint.doCreateAt()
    
            _size_root =  MATH.average(POS.get_bb_size(self.mRootTemplateHandle.mNode))
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
    
            log.debug(cgmGEN._str_subLine)



        
        if self.md_roll:#Segment stuff ===================================================================
            log.debug("|{0}| >> Checking for mid handles...".format(_str_func))
            for i in self.md_roll.keys():
                mControlMid = mRigNull.getMessageAsMeta('controlSegMidIK_{0}'.format(i))
                log.debug("|{0}| >> Found: {1}".format(_str_func,mControlMid))
                
                ml_shapes = self.atBuilderUtils('shapes_fromCast',
                                                targets = mControlMid,
                                                offset = _offset,
                                                mode = 'limbSegmentHandle')#'simpleCast
                CORERIG.shapeParent_in_place(mControlMid.mNode, ml_shapes[0].mNode,False)
            
                mControlMid.doStore('cgmTypeModifier','ik')
                mControlMid.doStore('cgmType','handle')
                mControlMid.doName()            
            
                mHandleFactory.color(mControlMid.mNode, controlType = 'sub')                
            
            log.debug(cgmGEN._str_subLine)
                
            
        
        
        #IK End ================================================================================
        if mBlock.ikSetup:
            log.debug("|{0}| >> ikHandle...".format(_str_func))
            _ikDefault = False
            mShape2 = False
            
            if mPivotHelper:# and str_ikEnd in ['foot']:
                log.debug("|{0}| >> pivot helper...".format(_str_func))
                
                mIKShape = mPivotHelper.doDuplicate(po=False)
                mIKShape.parent = False
                #mc.makeIdentity(mIKShape.mNode,apply=True,translate =False, rotate = False, scale=True)
                for mChild in mIKShape.getChildren(asMeta=True):
                    if mChild.cgmName == 'topLoft':
                        mShape2 = mChild.doDuplicate(po=False)
                        DIST.offsetShape_byVector(mShape2.mNode,_offset,origin=mShape2.p_position,component='cv')
    
                    mChild.delete()
    
                DIST.offsetShape_byVector(mIKShape.mNode,_offset,origin=mIKShape.p_position,component='cv')
                
                if not mShape2:
                    mShape2 = mIKShape.doDuplicate(po=False)
                    mShape2.p_position = mShape2.getPositionByAxisDistance('y+',_offset/2)
                    
                CURVES.join_shapes([mIKShape.mNode,mShape2.mNode])
                #mShape2.delete()
                #CORERIG.shapeParent_in_place(mIKShape.mNode, mShape2.mNode, False)
                
                if mBlock.buildLeverEnd:
                    mIKCrv = ml_prerigHandles[self.int_handleEndIdx + 1].doCreateAt(setClass=True)
                else:
                    mIKCrv = ml_prerigHandles[self.int_handleEndIdx].doCreateAt(setClass=True)
                CORERIG.shapeParent_in_place(mIKCrv.mNode, mIKShape.mNode, False)
                
                
                
                if mBlock.blockProfile in ['arm']:
                    log.debug("|{0}| >> default IK shape...".format(_str_func))                
                    mIKTemplateHandle = ml_templateHandles[-1]
                    #bb_ik = mHandleFactory.get_axisBox_size(mIKTemplateHandle.mNode)
                    bb_ik = POS.get_bb_size(mIKTemplateHandle.mNode,True,mode='maxFill')
                
                    _ik_shape = CURVES.create_fromName('cube', size = bb_ik)
                    SNAP.go(_ik_shape,self.ml_handleTargets[self.int_handleEndIdx].mNode)
                
                    CORERIG.shapeParent_in_place(mIKCrv.mNode, _ik_shape, False)

                
                
                """
                if str_ikEnd in ['foot']:
                    #Make our ikEnd -----------------------------------------------------
                    log.debug("|{0}| >> IK end shape...".format(_str_func))                
                    mIKTemplateHandle = ml_templateHandles[-1]
                    bb_ik = mHandleFactory.get_axisBox_size(mIKTemplateHandle.mNode)
                    _ik_shape = CURVES.create_fromName('cube', size = bb_ik)
                    #ATTR.set(_ik_shape,'scale', 1.5)
                
                    mIKEndCrv = cgmMeta.validateObjArg(_ik_shape, 'cgmObject',setClass=True)
                    mIKEndCrv.doSnapTo(ml_prerigHandles[self.int_handleEndIdx].mNode)
                
                    mHandleFactory.color(mIKEndCrv.mNode, controlType = 'main',transparent=True)
                    mIKEndCrv.doCopyNameTagsFromObject(ml_fkJoints[self.int_handleEndIdx].mNode,
                                                       ignore=['cgmType','cgmTypeModifier'])
                    mIKEndCrv.doStore('cgmTypeModifier','ikEnd')
                    mIKEndCrv.doStore('cgmType','handle')
                    mIKEndCrv.doName()
                
                    self.mRigNull.connectChildNode(mIKEndCrv,'controlIKEnd','rigNull')#Connect                                        
                    """
            elif ml_templateHandles[-1].getMessage('proxyHelper') and str_profile not in ['arm']:
                log.debug("|{0}| >> proxyHelper IK shape...".format(_str_func))
                mProxyHelper = ml_templateHandles[-1].getMessage('proxyHelper',asMeta=True)[0]
                bb_ik = POS.get_bb_size(mProxyHelper.mNode,True,mode='maxFill')#mHandleFactory.get_axisBox_size(mProxyHelper.mNode)
                
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
                
                
                    
                    
            elif str_ikEnd in ['tipCombo']:# and str_ikEnd in ['foot']:
                log.debug("|{0}| >> tipCombo IK shape...".format(_str_func))                
                mIKTemplateHandle = ml_templateHandles[-1]
                #bb_ik = mHandleFactory.get_axisBox_size(mIKTemplateHandle.mNode)
                bb_ik = POS.get_bb_size(mIKTemplateHandle.mNode,True,mode='maxFill')
                
                _ik_shape = CURVES.create_fromName('sphere', size = bb_ik)
                ATTR.set(_ik_shape,'scale', 2.5)
                
                mIKCrv = cgmMeta.validateObjArg(_ik_shape, 'cgmObject',setClass=True)
                mIKCrv.doSnapTo(ml_prerigHandles[-1].mNode)                
                
                
                #Make our ikEnd -----------------------------------------------------
                log.debug("|{0}| >> IK end shape...".format(_str_func))                
                _ik_shape = CURVES.create_fromName('cube', size = bb_ik)
                ATTR.set(_ik_shape,'scale', 2.5)
                """
                mIKEndCrv = cgmMeta.validateObjArg(_ik_shape, 'cgmObject',setClass=True)
                mIKEndCrv.doSnapTo(self.ml_handleTargets[self.int_handleEndIdx].mNode)
            
                mHandleFactory.color(mIKEndCrv.mNode, controlType = 'main',transparent=True)
                mIKEndCrv.doCopyNameTagsFromObject(self.ml_handleTargets[self.int_handleEndIdx].mNode,
                                                   ignore=['cgmType','cgmTypeModifier'])
                """
                mIKEndCrv = cgmMeta.validateObjArg(_ik_shape, 'cgmObject',setClass=True)
                mIKEndCrv.doSnapTo(ml_prerigHandles[-1].mNode)
            
                mHandleFactory.color(mIKEndCrv.mNode, controlType = 'sub')
                mIKEndCrv.doCopyNameTagsFromObject(self.ml_handleTargets[self.int_handleEndIdx].mNode,
                                                   ignore=['cgmType','cgmTypeModifier'])                
                
                mIKEndCrv.doStore('cgmTypeModifier','ikCombo')
                mIKEndCrv.doStore('cgmType','handle')
                mIKEndCrv.doName()
            
                self.mRigNull.connectChildNode(mIKEndCrv,'controlIKEnd','rigNull')#Connect                                        #Connect                        
            else:
                _ikDefault = True
                log.debug("|{0}| >> default IK shape...".format(_str_func))                
                mIKTemplateHandle = ml_templateHandles[-1]
                #bb_ik = mHandleFactory.get_axisBox_size(mIKTemplateHandle.mNode)
                bb_ik = POS.get_bb_size(mIKTemplateHandle.mNode,True,mode='maxFill')
                
                _ik_shape = CURVES.create_fromName('cube', size = bb_ik)
                #ATTR.set(_ik_shape,'scale', 1.5)
                
                mIKCrv = cgmMeta.validateObjArg(_ik_shape, 'cgmObject',setClass=True)
                
                if not self.b_singleChain:
                    if mBlock.buildLeverEnd:
                        mIKCrv.doSnapTo(self.ml_handleTargets[-1].mNode)
                    else:
                        mIKCrv.doSnapTo(self.ml_handleTargets[self.int_handleEndIdx].mNode)
                else:
                    mIKCrv.doSnapTo(ml_prerigHandles[-1].mNode)

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
            log.debug(cgmGEN._str_subLine)
            
            if not self.b_singleChain:
                #Mid IK...---------------------------------------------------------------------------------
                log.debug("|{0}| >> midIK...".format(_str_func))
                size_knee =  MATH.average(POS.get_bb_size(self.mMidTemplateHandle.mNode,True)) * .75
                crv = CURVES.create_fromName('sphere',
                                              direction = 'z+',#_jointOrientation[0]+'+',
                                              size = size_knee)#max(size_knee) * 1.25)            
                
                mKnee = cgmMeta.validateObjArg(crv,setClass=True)
                #Get our point for knee...
                #mKnee.p_position = self.atBuilderUtils('get_midIK_basePosOrient',self.ml_handleTargetsCulled,False)
                mKnee.p_position = self.mBlock.atUtils('prerig_get_rpBasePos',self.ml_handleTargetsCulled,False)
                mHandleFactory.color(mKnee.mNode, controlType = 'main')
        
                mKnee.doCopyNameTagsFromObject(ml_fkJoints[1].mNode,ignore=['cgmType','cgmTypeModifier'])
                mKnee.doStore('cgmAlias','midIK')
                mKnee.doStore('cgmTypeModifier','ikPole')
                
                mKnee.doName()
        
                self.mRigNull.connectChildNode(mKnee,'controlIKMid','rigNull')#Connect
                log.debug(cgmGEN._str_subLine)
            
            #Base IK...---------------------------------------------------------------------------------
            log.debug("|{0}| >> baseIK...".format(_str_func))
            
            mIK_templateHandle = self.mRootTemplateHandle
            #bb_ik = mHandleFactory.get_axisBox_size(mIK_templateHandle.mNode)
            bb_ik = POS.get_bb_size(mIK_templateHandle.loftCurve.mNode,True,mode='maxFill')
            _ik_shape = CURVES.create_fromName('sphere', size = bb_ik)#[v+_offset for v in bb_ik])
            #ATTR.set(_ik_shape,'scale', 1.5)
    
            mIKBaseShape = cgmMeta.validateObjArg(_ik_shape, 'cgmObject',setClass=True)
    
            mIKBaseShape.doSnapTo(mIK_templateHandle)
            #pos_ik = POS.get_bb_center(mProxyHelper.mNode)
            #SNAPCALLS.get_special_pos(mEndHandle.p_nameLong,
            #                                   'axisBox','z+',False)                
    
            #mIKBaseShape.p_position = pos_ik
            mIKBaseCrv = ml_ikJoints[0].doCreateAt()
            mIKBaseCrv.doCopyNameTagsFromObject(ml_fkJoints[0].mNode,ignore=['cgmType'])
            CORERIG.shapeParent_in_place(mIKBaseCrv.mNode, mIKBaseShape.mNode, False)                            
    
            mIKBaseCrv.doStore('cgmTypeModifier','ikBase')
            mIKBaseCrv.doName()

            mHandleFactory.color(mIKBaseCrv.mNode, controlType = 'main',transparent=True)
    
            mHandleFactory.color(mIKBaseCrv.mNode, controlType = 'main')        
            self.mRigNull.connectChildNode(mIKBaseCrv,'controlIKBase','rigNull')#Connect
        #FollowParent =============================================================================
        if self.b_followParentBank:
            log.debug("|{0}| >> follow parent handle...".format(_str_func))
            ml_followParentBankJoints = mRigNull.msgList_get('followParentBankJoints')
    
            mDag = ml_followParentBankJoints[-1].doCreateAt(setClass=True)
    
            if not bb_ik:
                bb_ik = mHandleFactory.get_axisBox_size(ml_templateHandles[-1].mNode)
    
            _ik_shape = CURVES.create_fromName('cube', size = bb_ik)            
            SNAP.go(_ik_shape,mDag.mNode)
    
            CORERIG.shapeParent_in_place(mDag.mNode, _ik_shape,False)
    
            mDag.doStore('cgmName',self.d_module['partName'] + '_followBank')
            mDag.doStore('cgmTypeModifier','ik')
            mDag.doName()
            mHandleFactory.color(mDag.mNode, controlType = 'sub')                
    
            self.mRigNull.connectChildNode(mDag,'controlFollowParentBank','rigNull')#            
            log.debug(cgmGEN._str_subLine)        
        
        #Cog/Settings =============================================================================
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
            
            log.debug(cgmGEN._str_subLine)

        else:#Root =============================================================================
            log.debug("|{0}| >> Root...".format(_str_func))
            
            if self.b_lever:
                mRootHandle = ml_prerigHandles[1]
            else:
                mRootHandle = ml_prerigHandles[0]
            #mRoot = ml_joints[0].doCreateAt()
            
            mRoot = ml_rigJoints[0].doCreateAt()
            
            #mHandleFactory.get_axisBox_size(self.mRootTemplateHandle.mNode)
            _size_root =  MATH.average(POS.get_bb_size(self.mRootTemplateHandle.mNode,True,'maxFill'))
            mRootCrv = cgmMeta.validateObjArg(CURVES.create_fromName('cube', _size_root),'cgmObject',setClass=True)
            mRootCrv.doSnapTo(mRootHandle)
        
            #SNAP.go(mRootCrv.mNode, ml_joints[0].mNode,position=False)
        
            CORERIG.shapeParent_in_place(mRoot.mNode,mRootCrv.mNode, False)
        
            ATTR.copy_to(_short_module,'cgmName',mRoot.mNode,driven='target')
            mRoot.doStore('cgmTypeModifier','root')
            mRoot.doName()
            
            mHandleFactory.color(mRoot.mNode, controlType = 'sub')
            
            self.mRigNull.connectChildNode(mRoot,'rigRoot','rigNull')#Connect
            log.debug(cgmGEN._str_subLine)
        
            
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
                    _mSnapTo = _mTar
                else:
                    _mTar = ml_targets[self.int_handleEndIdx]
                    if self.b_singleChain:
                        _mSnapTo = ml_prerigHandles[-1]
                    else:
                        _mSnapTo = ml_targets[self.int_handleEndIdx]
                        
                    mIKTemplateHandle = ml_templateHandles[-1]
                    bb_ik = TRANS.bbSize_get(mIKTemplateHandle.mNode)#mHandleFactory.get_axisBox_size(mIKTemplateHandle.mNode)
                    _settingsSize = MATH.average(bb_ik) * .75
                    #_settingsSize = MATH.average(TRANS.bbSize_get(ml_templateHandles[-1].mNode,shapes=True))
                    
                mSettingsShape = cgmMeta.validateObjArg(CURVES.create_fromName('gear',_settingsSize * .75,
                                                                               '{0}+'.format(_jointOrientation[2])),'cgmObject',setClass=True)
    
                mSettingsShape.doSnapTo(_mSnapTo.mNode)
                d_directions = {'up':'y+','down':'y-','in':'x+','out':'x-'}
                str_settingsDirections = d_directions.get(mBlock.getEnumValueString('settingsDirection'),'y+')
                
            
                mMesh_tmp =  self.mBlock.atUtils('get_castMesh')
                str_meshShape = mMesh_tmp.getShapes()[0]        
                pos = RAYS.get_cast_pos(_mTar.mNode,str_settingsDirections,shapes = str_meshShape)                
                
                if not pos:
                    log.debug("|{0}| >> Cast pos for setting fail.Using alternate".format(_str_func,_settingsPlace))
                    pos = _mTar.getPositionByAxisDistance(str_settingsDirections,_settingsSize + (_offset * 2))
                else:
                    _vec = MATH.get_vector_of_two_points(_mTar.p_position,pos)
                    pos = DIST.get_pos_by_vec_dist(pos,_vec,_offset*2)
                    
                mSettingsShape.p_position = pos
                
                mMesh_tmp.delete()
                
                #mSettingsShape.p_position = _mSnapTo.getPositionByAxisDistance(str_settingsDirections,
                #                                                               _settingsSize + (_offset * 2))
                
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
            
        
            log.debug(cgmGEN._str_subLine)
         
    
        #Direct Controls =============================================================================
        log.debug("|{0}| >> direct...".format(_str_func))                
        ml_rigJoints = self.mRigNull.msgList_get('rigJoints')
        _size_direct = _offset * 2#DIST.get_distance_between_targets([mObj.mNode for mObj in ml_rigJoints], average=True)        

        d_direct = {'size':_size_direct}
            
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
        log.debug(cgmGEN._str_subLine)

        
        #Handles =======================================================================================    
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
            
            log.debug(cgmGEN._str_subLine)
            
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
        ml_targets = []
        for mObj in self.ml_handleTargets:
            mAttach = mObj.getMessageAsMeta('attachJoint')
            #if mAttach:
            ml_targets.append(mAttach or mObj)
            
        ml_fkShapes = self.atBuilderUtils('shapes_fromCast',
                                          #targets = [mObj.mNode for mObj in self.ml_handleTargets],
                                          targets = [mObj.mNode for mObj in self.ml_fkShapeTargetDags],
                                          #targets = ml_targets,
                                          offset = _offset,
                                          mode = 'frameHandle')#limbHandle
        
        if self.mPivotHelper:
            size_pivotHelper = POS.get_bb_size(self.mPivotHelper.mNode)
        else:
            size_pivotHelper = POS.get_bb_size(ml_templateHandles[-1].mNode)
        
        mBallFK = False
        mToeFK = False
        
        if self.mBall:
            #_size_ball = DIST.get_distance_between_targets([self.mBall.mNode,
                                                            #self.mBall.p_parent])
        
            crv = CURVES.create_controlCurve(self.mBall.mNode, shape='circle',
                                             direction = _jointOrientation[0]+'+',
                                             sizeMode = 'fixed',
                                             size = size_pivotHelper[0])
            mHandleFactory.color(crv, controlType = 'main')                                
            mBallFK = self.mBall.getMessageAsMeta('fkJoint')
            CORERIG.shapeParent_in_place(mBallFK.mNode,crv, True, replaceShapes=True)            
            
            ml_fkShapes.append(cgmMeta.validateObjArg(crv,'cgmObject'))
            
        if self.mToe:
            #_size_ball = DIST.get_distance_between_targets([self.mToe.mNode,
            #                                                self.mToe.p_parent])
    
            crv = CURVES.create_controlCurve(self.mToe.mNode, shape='circle',
                                             direction = _jointOrientation[0]+'+',
                                             sizeMode = 'fixed',
                                             size = size_pivotHelper[0])
            
            mHandleFactory.color(crv, controlType = 'main')                    
            mToeFK = self.mToe.getMessageAsMeta('fkJoint')
            CORERIG.shapeParent_in_place(mToeFK.mNode,crv, True, replaceShapes=True)            
            
            ml_fkShapes.append(cgmMeta.validateObjArg(crv,'cgmObject'))
        
        
        
        log.debug("|{0}| >> FK...".format(_str_func))    
        for i,mShape in enumerate(ml_fkShapes):
            """
            if self.b_lever:
                if i == 0:
                    continue
                i+=1"""
                
            if mShape == ml_fkShapes[-1] and self.b_cullFKEnd:
                log.debug("|{0}| >> Last fk shape and b_cullFKEnd...".format(_str_func))                
                continue
            try:mJnt = ml_fkJoints[i]
            except:continue
            
            if mJnt in [mToeFK,mBallFK]:
                continue


            if mBlock.buildLeverEnd and mJnt == ml_fkJoints[-2]:
                mDag = ml_fkJoints[-1].doCreateAt(setClass=True)
                CORERIG.shapeParent_in_place(mDag.mNode,mShape.mNode, True, replaceShapes=True)            
                
                mDag.p_parent = mIKCrv
                mDag.doStore('cgmName','ballRotationControl')
                mDag.doName()
                mHandleFactory.color(mDag.mNode, controlType = 'sub')
            
                mRigNull.connectChildNode(mDag,'controlBallRotation','rigNull')#Connect

            mHandleFactory.color(mShape.mNode, controlType = 'main')
            #if _ikDefault:
            #    CORERIG.shapeParent_in_place(mIKCrv.mNode,mShape.mNode, True, replaceShapes=True)
            CORERIG.shapeParent_in_place(mJnt.mNode,mShape.mNode, True, replaceShapes=True)
            
        if mBlock.buildLeverEnd and not self.b_cullFKEnd:
            log.debug("|{0}| >> Last fk handle before toes/ball: {1}".format(_str_func,mJnt))
            ml_shapes = self.atBuilderUtils('shapes_fromCast',
                                            targets = ml_fkJoints[-1],
                                            offset = _offset,
                                            mode = 'simpleCast')#'segmentHan
                
            _fk_shape = ml_shapes[0].mNode
            mHandleFactory.color(_fk_shape, controlType = 'main')        
            CORERIG.shapeParent_in_place(ml_fkJoints[-1].mNode,_fk_shape, True, replaceShapes=True)                       

        if str_ikEnd in ['tipCombo']:
            CORERIG.shapeParent_in_place(mIKEndCrv.mNode,ml_fkShapes[-2].mNode, True, replaceShapes=True)
            mHandleFactory.color(mIKEndCrv.mNode, controlType = 'sub')

        for mShape in ml_fkShapes:
            try:mShape.delete()
            except:pass
            
        for mObj in self.ml_fkShapeTargetDags:
            mObj.delete()
            
        log.debug(cgmGEN._str_subLine)

        return
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err,localDat=vars())        
    
@cgmGEN.Timer
def rig_controls(self):
    try:
        _short = self.d_block['shortName']
        _str_func = 'rig_controls'
        log.debug("|{0}| >> ...".format(_str_func)+cgmGEN._str_hardBreak)
        log.debug(self)
        
        mBlock = self.mBlock
        mRigNull = self.mRigNull
        ml_controlsAll = []#we'll append to this list and connect them all at the end
        mRootParent = self.mDeformNull
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
        
        #>> vis Drivers ======================================================================================	
        mPlug_visSub = self.atBuilderUtils('build_visSub')
        
        if not b_cog:
            mPlug_visRoot = cgmMeta.cgmAttr(mSettings,'visRoot', value = True, attrType='bool', defaultValue = False,keyable = False,hidden = False)
        mPlug_visDirect = cgmMeta.cgmAttr(mSettings,'visDirect', value = True, attrType='bool', defaultValue = False,keyable = False,hidden = False)
        
        if self.b_followParentBank:
            mPlug_followParentBankVis = cgmMeta.cgmAttr(mSettings.mNode,'visParentBank',attrType='bool', defaultValue = False,keyable = False,hidden = False)    
        log.debug(cgmGEN._str_subLine)
        
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
        log.debug(cgmGEN._str_subLine)
        
            
        #Settings overall =====================================================================================
        if not b_cog:
            for mShape in mRoot.getShapes(asMeta=True):
                ATTR.connect(mPlug_visRoot.p_combinedShortName, "{0}.overrideVisibility".format(mShape.mNode))
                
            #>> settings -------------------------------------------------------------------------------------
            log.debug("|{0}| >> Settings : {1}".format(_str_func, mSettings))
            MODULECONTROL.register(mSettings,
                                   mirrorSide= self.d_module['mirrorDirection'],
                                   )
            ml_controlsAll.append(mSettings)
            #ml_blendJoints = self.mRigNull.msgList_get('blendJoints')
            #if ml_blendJoints:
            #    mSettings.masterGroup.parent = ml_blendJoints[-1]
            #else:
            #    mSettings.masterGroup.parent = ml_fkJoints[-1]
            log.debug(cgmGEN._str_subLine)
    
    
        #LimbRoot -----------------------------------------------------------------------------------------
        mLimbRoot = mRigNull.getMessageAsMeta('limbRoot')
        if mLimbRoot:
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
            log.debug(cgmGEN._str_subLine)
    
    
    
        #Lever =================================================================================================
        if self.b_lever:
            #Lever ---------------------------------------------------------------------------------------        
            log.debug("|{0}| >> Lever...".format(_str_func))
            #mLeverRigJnt = mRigNull.getMessage('leverRig',asMeta=True)[0]
            mLeverFK = mRigNull.getMessage('leverFK',asMeta=True)[0]
            d_buffer = MODULECONTROL.register(mLeverFK,
                                              typeModifier='FK',
                                              mirrorSide = self.d_module['mirrorDirection'],
                                              mirrorAxis ="translateX,translateY,translateZ",
                                              makeAimable = False)        
            ml_controlsAll.append(mLeverFK)
            log.debug(cgmGEN._str_subLine)
            
            
    
        
        # Pivots ================================================================================================
        #if mMainHandle.getMessage('pivotHelper'):
            #log.debug("|{0}| >> Pivot helper found".format(_str_func))
        for a in 'center','front','back','left','right':#This order matters
            str_a = 'pivot' + a.capitalize()
            if mRigNull.getMessage(str_a):
                log.debug("|{0}| >> Found: {1}".format(_str_func,str_a))
                
                mPivot = mRigNull.getMessage(str_a,asMeta=True)[0]
                
                d_buffer = MODULECONTROL.register(mPivot,
                                                  typeModifier='pivot',
                                                  mirrorSide= self.d_module['mirrorDirection'],
                                                  mirrorAxis="translateX,rotateY,rotateZ",
                                                  makeAimable = False)
                
                mPivot = d_buffer['mObj']
                for mShape in mPivot.getShapes(asMeta=True):
                    ATTR.connect(mPlug_visSub.p_combinedShortName, "{0}.overrideVisibility".format(mShape.mNode))                
                ml_controlsAll.append(mPivot)
            log.debug(cgmGEN._str_subLine)
    
        #FK controls =========================================================================================
        log.debug("|{0}| >> FK Controls...".format(_str_func))
        ml_fkJoints = self.mRigNull.msgList_get('fkJoints')
        
        if str_ikBase == 'hips':
            ml_fkJoints = ml_fkJoints[1:]
        
        ml_fkJoints[0].parent = mRootParent
        ml_controlsAll.extend(ml_fkJoints)
        
        for i,mObj in enumerate(ml_fkJoints):
            d_buffer = MODULECONTROL.register(mObj,
                                              mirrorSide= self.d_module['mirrorDirection'],
                                              mirrorAxis ="translateX,translateY,translateZ",
                                              makeAimable = True)
            
            mObj = d_buffer['mObj']
            if mBlock.ikSetup:
                self.atUtils('get_switchTarget', mObj, mObj.getMessage('blendJoint'))
            
        log.debug(cgmGEN._str_subLine)
    
        
        #ControlIK ========================================================================================
        mControlIK = False
        if mRigNull.getMessage('controlIK'):
            ml_blend = mRigNull.msgList_get('blendJoints')
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
            
            self.atUtils('get_switchTarget', mControlIK,ml_blend[self.int_handleEndIdx])
                    
            log.debug(cgmGEN._str_subLine)
    
            
        mIKControlBase = mRigNull.getMessageAsMeta('controlIKBase')
        if mIKControlBase:
            log.debug("|{0}| >> Found controlBaseIK : {1}".format(_str_func, mIKControlBase))
    
            _d = MODULECONTROL.register(mIKControlBase,
                                        addDynParentGroup = True,
                                        mirrorSide= self.d_module['mirrorDirection'],
                                        mirrorAxis="translateX,rotateY,rotateZ",
                                        makeAimable = True,
                                        **d_controlSpaces)
            
            mIKControlBase = _d['mObj']
            mIKControlBase.masterGroup.parent = mRootParent
            ml_controlsAll.append(mIKControlBase)
            ml_controlsIKRO.append(mIKControlBase)
            
            self.atUtils('get_switchTarget', mIKControlBase,ml_blend[0])
            log.debug(cgmGEN._str_subLine)
    
            
        mIKControlMid = mRigNull.getMessageAsMeta('controlIKMid')
        if mIKControlMid:
            log.debug("|{0}| >> Found controlIKMid : {1}".format(_str_func, mIKControlMid))
    
            _d = MODULECONTROL.register(mIKControlMid,
                                        addDynParentGroup = True,
                                        mirrorSide= self.d_module['mirrorDirection'],
                                        mirrorAxis="translateX,rotateY,rotateZ",
                                        makeAimable = True,
                                        **d_controlSpaces)
            
            mIKControlMid = _d['mObj']
            mIKControlMid.masterGroup.parent = mRootParent
            ml_controlsAll.append(mIKControlMid)
            ml_controlsIKRO.append(mIKControlMid)
            
            self.atUtils('get_switchTarget', mIKControlMid,ml_blend[self.int_handleMidIdx])
            
            log.debug(cgmGEN._str_subLine)
    
        mIKControlEnd = mRigNull.getMessageAsMeta('controlIKEnd')
        if mIKControlEnd:
            log.debug("|{0}| >> Found controlIKEnd : {1}".format(_str_func, mIKControlEnd))
            
            mPlug_visIKEnd = cgmMeta.cgmAttr(mSettings.mNode,'visIKEnd',attrType='bool',lock=False,keyable=False)
            
            _d = MODULECONTROL.register(mIKControlEnd,
                                        addDynParentGroup = False,
                                        mirrorSide= self.d_module['mirrorDirection'],
                                        mirrorAxis="translateX,rotateY,rotateZ",
                                        makeAimable = True,
                                        **d_controlSpaces)
                    
            mIKControlEnd = _d['mObj']
            mIKControlEnd.masterGroup.parent = mRootParent
            ml_controlsAll.append(mIKControlEnd)
            ml_controlsIKRO.append(mIKControlEnd)
            
            self.atUtils('get_switchTarget', mIKControlEnd,ml_blend[self.int_handleEndIdx])
            
            
            ATTR.connect(mPlug_visIKEnd.p_combinedShortName, "{0}.visibility".format(mIKControlEnd.masterGroup.mNode))        
                    
            log.debug(cgmGEN._str_subLine)
            
        
        mIKBallRotationControl = mRigNull.getMessageAsMeta('controlBallRotation')
        if mIKBallRotationControl:
            log.debug("|{0}| >> Found controlBallRotation : {1}".format(_str_func, mIKBallRotationControl))
            
            
            _d = MODULECONTROL.register(mIKBallRotationControl,
                                        addDynParentGroup = False,
                                        mirrorSide= self.d_module['mirrorDirection'],
                                        mirrorAxis="translateX,rotateY,rotateZ",
                                        makeAimable = True)
                    
            mIKControlEnd = _d['mObj']
            ml_controlsAll.append(mIKBallRotationControl)
            
                    
            log.debug(cgmGEN._str_subLine)
            
        #>> handleJoints ==================================================================================
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
                
                ATTR.connect(mPlug_visSub.p_combinedShortName, "{0}.visibility".format(mObj.masterGroup.mNode))
                #for mShape in mObj.getShapes(asMeta=True):
                    #ATTR.connect(mPlug_visSub.p_combinedShortName, "{0}.overrideVisibility".format(mShape.mNode))
                    
            log.debug(cgmGEN._str_subLine)
        
        #Segment stuff ===================================================================
        if self.md_roll:
            log.debug("|{0}| >> Checking for mid handles...".format(_str_func))
        
            for i in self.md_roll.keys():
                mControlMid = mRigNull.getMessageAsMeta('controlSegMidIK_{0}'.format(i))
                log.debug("|{0}| >> found mControlMid {2} : {1}".format(_str_func,mControlMid,i))
                
                
                _d = MODULECONTROL.register(mControlMid,
                                            addDynParentGroup = True, 
                                            mirrorSide= self.d_module['mirrorDirection'],
                                            mirrorAxis="translateX,rotateY,rotateZ",
                                            makeAimable = True,
                                            **d_controlSpaces)
            
            
                mControlMid = _d['mObj']
                mControlMid.masterGroup.parent = ml_blend[i]
                ml_controlsAll.append(mControlMid)
                ATTR.connect(mPlug_visSub.p_combinedShortName, "{0}.visibility".format(mControlMid.masterGroup.mNode))
                
                #for mShape in mControlMid.getShapes(asMeta=True):
                    #ATTR.connect(mPlug_visSub.p_combinedShortName, "{0}.overrideVisibility".format(mShape.mNode))
            
                #Register our snapToTarget -------------------------------------------------------------
                #self.atUtils('get_switchTarget', mControlMid,ml_blend[ MATH.get_midIndex(len(ml_blend))])        
    
            log.debug(cgmGEN._str_subLine)
    
        #>> Direct Controls ====================================================================================
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
        log.debug(cgmGEN._str_subLine)
        
        #controlFollowParentBank -----------------------------------------------------------------------
        mControlFollowParentBank = mRigNull.getMessageAsMeta('controlFollowParentBank')
        if mControlFollowParentBank:
            log.debug("|{0}| >> controlFollowParentBank...".format(_str_func)+'-'*40)
            log.debug("|{0}| >> Found rigRoot : {1}".format(_str_func, mControlFollowParentBank))
        
            _d = MODULECONTROL.register(mControlFollowParentBank,
                                        addDynParentGroup = False,
                                        mirrorSide= self.d_module['mirrorDirection'],
                                        mirrorAxis="translateX,rotateY,rotateZ",
                                        makeAimable = False)
        
            mControlFollowParentBank = _d['mObj']
    
            ml_controlsAll.append(mControlFollowParentBank)
        
        
            for mShape in mControlFollowParentBank.getShapes(asMeta=True):
                ATTR.connect(mPlug_followParentBankVis.p_combinedShortName, "{0}.overrideVisibility".format(mShape.mNode))        
            log.debug(cgmGEN._str_subLine)    
    
        log.debug("|{0}| >> Closeout...".format(_str_func)+'-'*40)
    
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
        
        #ml_controlsAll = self.atBuilderUtils('register_mirrorIndices', ml_controlsAll)
        mRigNull.msgList_connect('controlsAll',ml_controlsAll)
        mRigNull.moduleSet.extend(ml_controlsAll)
        #self.atBuilderUtils('check_nameMatches', ml_controlsAll)
        
        return 
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err,localDat=vars())        


@cgmGEN.Timer
def rig_segments(self):
    try:
        _short = self.d_block['shortName']
        _str_func = 'rig_segments'
        log.debug("|{0}| >> ...".format(_str_func)+cgmGEN._str_hardBreak)
        log.debug(self)
    
        mBlock = self.mBlock
        mRigNull = self.mRigNull
        ml_rigJoints = mRigNull.msgList_get('rigJoints')
        #ml_segJoints = mRigNull.msgList_get('segmentJoints')
        mModule = self.mModule
        mRoot = mRigNull.rigRoot
        mPrerigNull = mBlock.prerigNull
    
        mRootParent = self.mConstrainNull
        ml_handleJoints = mRigNull.msgList_get('handleJoints')
        ml_blendJoints = mRigNull.msgList_get('blendJoints')
        
        ml_prerigHandleJoints = mPrerigNull.msgList_get('handleJoints')
        _jointOrientation = self.d_orientation['str']
        
        
        if not ml_handleJoints and not self.md_roll:
            log.debug("|{0}| >> No segment setup...".format(_str_func))
            
            if mBlock.scaleSetup:
                log.debug("|{0}| >> Scale setup found. Resolving rig joints...".format(_str_func))
                
                for mJnt in ml_rigJoints:
                    mParent = mJnt.masterGroup.getParent(asMeta=True)
                    mScaleParent = mParent.getMessageAsMeta('scaleJoint')
                    if mScaleParent:
                        mJnt.masterGroup.p_parent=mScaleParent            
            return True    
        
        if ml_handleJoints:
            log.debug("|{0}| >> Handle Joints...".format(_str_func))
            
            for i,mHandle in enumerate(ml_handleJoints):
                log.debug("|{0}| >> {1}...".format(_str_func,mHandle))
                
        
        if self.md_roll:
            log.debug("|{0}| >> Segments...".format(_str_func))
            
            
            _settingsControl = None
            if mBlock.squashExtraControl:
                _settingsControl = mRigNull.settings.mNode
    
            _extraSquashControl = mBlock.squashExtraControl
    
            #res_segScale = self.UTILS.get_blockScale(self,'segMeasure')
            #mPlug_masterScale = res_segScale[0]
            #mMasterCurve = res_segScale[1]
    
            _d_ribbonShare = {'connectBy':'constraint',
                              'extendEnds':True,
                              'settingsControl':_settingsControl,
                              'moduleInstance':mModule}
            _d_ribbonShare.update(self.d_squashStretch)
    
            #mMasterCurve.p_parent = mRoot
            
            
            l_rollKeys = self.md_roll.keys()
            l_rollKeys.sort()
            for i in l_rollKeys:
                log.debug("|{0}| >> Segment {1}".format(_str_func,i))
                
                ml_segHandles = mRigNull.msgList_get('segmentHandles_{0}'.format(i))
                ml_segMidHandles = mRigNull.msgList_get('segmentMidHandles_{0}'.format(i))
                mControlMid = mRigNull.getMessageAsMeta('controlSegMidIK_{0}'.format(i))
                
                log.debug("|{0}| >> Segment handles...".format(_str_func,i))
                #pprint.pprint(ml_segHandles)
                
                #Parent these to their handles ------------------------------------------------
                ml_segHandles[0].parent = ml_handleJoints[i]
                ml_segHandles[-1].parent = ml_handleJoints[i+1]
                
                for mJnt in ml_segHandles:
                    mJnt.segmentScaleCompensate = False
                    
                if ml_segMidHandles:
                    for iii,mJnt in enumerate(ml_segMidHandles):
                        mJnt.segmentScaleCompensate = False
                        mJnt.p_parent = ml_segHandles[iii].p_parent
                
                #Setup the aim blends ---------------------------------------------------------
                log.debug("|{0}| >> Aim segmentHandles: {1}".format(_str_func,i))            
                for ii,mSegHandle in enumerate(ml_segHandles):
                    log.debug("|{0}| >> Handle: {1} | {2}".format(_str_func,mSegHandle.p_nameShort, ii))            
                    mParent = mSegHandle.getParent(asMeta=1)
                    idx_parent = ml_handleJoints.index(mParent)
                    #mBlendParent = mParent.masterGroup.getParent(asMeta=True)
                    mBlendParent = ml_blendJoints[idx_parent]
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
                        
                        mLimbRoot = mRigNull.getMessageAsMeta('limbRoot')
                        if mLimbRoot:
                            mStableUp.p_parent = mLimbRoot
                        else:
                            mStableUp.p_parent = mRoot
                        mStableUp.doStore('cgmName',mSegHandle)                
                        mStableUp.doStore('cgmTypeModifier','stable')
                        mStableUp.doStore('cgmType','upObj')
                        mStableUp.doName()
                        
                        #orient contrain one channel
                        mc.orientConstraint(mBlendParent.mNode, mStableUp.mNode,
                                            maintainOffset = True,
                                            skip = [_jointOrientation[0], _jointOrientation[1]])
                        
                        
                        mAimStable = mSegHandle.doCreateAt()
                        mAimStable.p_parent = mBlendParent
                        mAimStable.doStore('cgmName',mSegHandle)                
                        mAimStable.doStore('cgmTypeModifier','stableStart')
                        mAimStable.doStore('cgmType','aimer')
                        mAimStable.doName()
                        
                        mAimFollow = mSegHandle.doCreateAt()
                        mAimFollow.p_parent = mBlendParent
                        mAimFollow.doStore('cgmName',mSegHandle)                
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
                        
                        
                        if ml_segMidHandles:
                            mc.aimConstraint(mControlMid.mNode, ml_segMidHandles[ii].mNode,
                                             maintainOffset = True,#True
                                             aimVector = [0,0,1], upVector = self.v_twistUp,#upVector = [0,1,0], 
                                             worldUpObject = mSegHandle.mNode,
                                             worldUpType = 'objectrotation', 
                                             worldUpVector = [0,1,0])
                        
                        
                    elif mParent == ml_handleJoints[-1]:
                        log.debug("|{0}| >> Last handles...".format(_str_func))
                        _aimBack = ml_handleJoints[idx_parent-1].p_nameShort
                        
                        mBlendParentsParent = ml_blendJoints[idx_parent-1]
                        
                        mFollow = mSegHandle.doCreateAt()
                        mFollow.p_parent = mBlendParent
                        mFollow.doStore('cgmName',mSegHandle)                
                        mFollow.doStore('cgmTypeModifier','follow')
                        mFollow.doStore('cgmType','driver')
                        mFollow.doName()
                    
                        mAimBack = mSegHandle.doCreateAt()
                        mAimBack.p_parent = mBlendParent
                        mAimBack.doStore('cgmName',mSegHandle)                                
                        mAimBack.doStore('cgmTypeModifier','back')
                        mAimBack.doStore('cgmType','aimer')
                        mAimBack.doName()
                        
                        log.debug("|{0}| >> Stable up...".format(_str_func))
                        mStableUp = mBlendParent.doCreateAt()
                        mStableUp.p_parent = mBlendParent.mNode
                        mStableUp.doStore('cgmName',mSegHandle)                
                        mStableUp.doStore('cgmTypeModifier','stableEnd')
                        mStableUp.doStore('cgmType','upObj')
                        mStableUp.rotateOrder = 0#...thing we have to have this to xyz to work right
                        mStableUp.doName()
                        
                        mc.orientConstraint(mBlendParent.mNode, mStableUp.mNode,
                                            maintainOffset = True,
                                            skip = [_jointOrientation[2], _jointOrientation[1]])
                        
                        #mc.pointConstraint(mBlendParent.mNode,mStableUp.mNode)
                        mConstrain = mStableUp.doGroup(True,asMeta=True,typeModifier = 'orient')
                        mc.orientConstraint(mBlendParentsParent.mNode, mConstrain.mNode,
                                            maintainOffset = True)
                        
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
                        
                        
                        if ml_segMidHandles:
                            mc.aimConstraint(mControlMid.mNode, ml_segMidHandles[ii].mNode,
                                             maintainOffset = True,
                                             aimVector = [0,0,-1], upVector = self.v_twistUp,#[-1,0,0], 
                                             worldUpObject = mSegHandle.mNode,
                                             worldUpType = 'objectrotation', 
                                             worldUpVector = self.v_twistUp)#[-1,0,0])
                        
                    else:
                        _aimForward = ml_handleJoints[idx_parent+1].p_nameShort
                        _aimBack = ml_handleJoints[idx_parent-1].p_nameShort
                        
                        log.debug("|{0}| >> Blend handles | forward: {1} | back: {2}".format(_str_func,_aimForward,_aimBack))
                        
                        mAimForward = mSegHandle.doCreateAt()
                        mAimForward.p_parent = mSegHandle.p_parent
                        mAimForward.doStore('cgmName',mSegHandle)                
                        mAimForward.doStore('cgmTypeModifier','forward')
                        mAimForward.doStore('cgmType','aimer')
                        mAimForward.doName()
                    
                        mAimBack = mSegHandle.doCreateAt()
                        mAimBack.p_parent = mSegHandle.p_parent
                        mAimBack.doStore('cgmName',mSegHandle)                                
                        mAimBack.doStore('cgmTypeModifier','back')
                        mAimBack.doStore('cgmType','aimer')
                        mAimBack.doName()
                    
                        mc.aimConstraint(_aimForward, mAimForward.mNode, maintainOffset = False,
                                         aimVector = [0,0,1], upVector = self.v_twistUp,#[0,1,0], 
                                         worldUpObject = mParent.mNode,
                                         worldUpType = 'objectrotation', 
                                         worldUpVector = self.v_twistUp)
                        
                        mc.aimConstraint(_aimBack, mAimBack.mNode, maintainOffset = False,
                                         aimVector = [0,0,-1], upVector = self.v_twistUp,#[0,1,0], 
                                         worldUpObject = mParent.mNode,
                                         worldUpType = 'objectrotation', 
                                         worldUpVector = self.v_twistUp)                
                        
                        if ii == 0:
                            const = mc.orientConstraint([mAimBack.mNode,mAimForward.mNode], mSegHandle.mNode, maintainOffset = False)[0]
                        else:
                            const = mc.orientConstraint([mAimForward.mNode, mAimBack.mNode], mSegHandle.mNode, maintainOffset = False)[0]
                            
                        
                        ATTR.set(const,'interpType',2)
                        
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
                
                        if ml_segMidHandles:
                            #mControlMid = mRigNull.getMessageAsMeta('controlSegMidIK_{0}'.format(i))
                            _d = {'worldUpObject' : mParent.mNode,
                                  'worldUpType' : 'objectrotation',
                                  'upVector':self.v_twistUp,#[0,1,0],
                                  'worldUpVector' : self.v_twistUp}
                            
                            if ii == 0:
                                _d['aimVector'] = [0,0,1]
                            else:
                                _d['aimVector'] = [0,0,-1]
                            
                            mc.aimConstraint(mControlMid.mNode,
                                             ml_segMidHandles[ii].mNode,
                                             maintainOffset = False,**_d)
                
                #Seg handles -------------------------------------------------------------------
                ml_segJoints = mRigNull.msgList_get('segJoints_{0}'.format(i))
                log.debug("|{0}| >> Segment joints...".format(_str_func,i))
                #pprint.pprint(ml_segJoints)
                
                for mJnt in ml_segJoints:
                    mJnt.drawStyle = 2
                    ATTR.set(mJnt.mNode,'radius',0)
                
                ml_influences = []
                if ml_segMidHandles:
                    ml_influences.extend(ml_segMidHandles)
                else:
                    ml_influences.extend(ml_segHandles)
                
                
                #Mid Ik... -----------------------------------------------------------------------------            
                if mControlMid:
                    log.debug("|{0}| >> Mid IK {1} setup...".format(_str_func,i))            
                    
                    mControlMid.masterGroup.parent = mRoot#ml_blendJoints[i]
                        
                    ml_midTrackJoints = copy.copy(ml_segHandles)
                    ml_midTrackJoints.insert(1,mControlMid)
                    
                    d_mid = {'jointList':[mJnt.mNode for mJnt in ml_midTrackJoints],
                             'baseName' :self.d_module['partName'] + '_midRibbon',
                             'driverSetup':None,#Old - stable blend
                             'squashStretch':None,
                             'paramaterization':'floating',          
                             'msgDriver':'masterGroup',
                             'specialMode':'noStartEnd',
                             'connectBy':'constraint',
                             'influences':ml_segHandles,
                             'moduleInstance' : mModule}
                    
                    
                    reload(IK)
                    l_midSurfReturn = IK.ribbon(**d_mid)            
                    ml_influences.append(mControlMid)
                    
                    if self.b_squashSetup:
                        mc.scaleConstraint([mObj.mNode for mObj in ml_segHandles], mControlMid.masterGroup.mNode, maintainOffset=True)
                    
                #Ribbon... --------------------------------------------------------------------------------------------
                log.debug("|{0}| >> Ribbon {1} setup...".format(_str_func,i))
                reload(IK)
                #mSurf = IK.ribbon([mObj.mNode for mObj in ml_rigJoints], baseName = mBlock.cgmName, connectBy='constraint', msgDriver='masterGroup', moduleInstance = mModule)
                
                
                #Trying something new...
                res_segScale = self.UTILS.get_blockScale(self,'segMeasure_{0}'.format(i),ml_segJoints)
                mPlug_masterScale = res_segScale[0]
                mMasterCurve = res_segScale[1]
                self.fnc_connect_toRigGutsVis( mMasterCurve )
    
                mMasterCurve.p_parent = ml_blendJoints[i]#mRoot#ml_blendJoints[i]
                
                _d = {'jointList':[mObj.mNode for mObj in ml_segJoints],
                      'baseName' : "{0}_seg_{1}".format(ml_blendJoints[i].cgmName,i),
                      'masterScalePlug':mPlug_masterScale,
                      'paramaterization':mBlock.getEnumValueString('ribbonParam'),                            
                      'influences':[mHandle.mNode for mHandle in ml_influences],
                      }            
                
                if i == l_rollKeys[0]:
                    _d['squashFactorMode'] = 'blendUpMid'
                elif i == l_rollKeys[-1]:
                    _d['squashFactorMode'] = 'midBlendDown'
                else:
                    _d['squashFactorMode'] = 'max'
                    
                
                
                _d.update(_d_ribbonShare)
                
                IK.ribbon(**_d)
                
                ml_segJoints[0].parent = ml_blendJoints[i]
                    
                if self.b_squashSetup:
                    for mJnt in ml_segJoints:
                        mJnt.segmentScaleCompensate = False
                        if mJnt == ml_segJoints[0]:
                            continue
                        mJnt.p_parent = ml_blendJoints[i]
                
                    for mJnt in ml_handleJoints:
                        mJnt.segmentScaleCompensate = False
                        
                        
                        
                
                """
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
                
                mSkinCluster.doStore('cgmName', mSurf)
                mSkinCluster.doName()    
                """
                #cgmGEN.func_snapShot(vars())
            
                #ml_segJoints[0].parent = mRoot            
                
                
            #segmentHandles_{0}
        
            #
            if self.b_squashSetup:
                log.debug("|{0}| >> Final squash stretch stuff...".format(_str_func))
                
                for mJnt in ml_rigJoints[:self.int_handleEndIdx]:
                    ml_drivers = mJnt.msgList_get('driverJoints')
                    if ml_drivers:
                        log.debug("|{0}| >> Found drivers".format(_str_func))
                        #mJnt.masterGroup.p_parent = mRigNull
                        mc.scaleConstraint([mObj.mNode for mObj in ml_drivers],mJnt.masterGroup.mNode,maintainOffset=True)
                        
                        
            for mHandle in ml_handleJoints:
                mParent = mHandle.masterGroup.getParent(asMeta=True)
                mScaleParent = mParent.getMessageAsMeta('scaleJoint')
                if mScaleParent:
                    mHandle.masterGroup.p_parent=mScaleParent
                    
                        
    
        return
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err,localDat=vars())        

    
    
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
        log.debug("|{0}| >> No segment joints. No segment setup necessary.".format(_str_func))
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

    mSkinCluster.doStore('cgmName', mSurf)
    mSkinCluster.doName()    
    
    cgmGEN.func_snapShot(vars())

    ml_segJoints[0].parent = mRoot

    
@cgmGEN.Timer
def rig_frame(self):
    try:
        _short = self.d_block['shortName']
        _str_func = 'rig_rigFrame'.format(_short)
        log.debug("|{0}| >> ...".format(_str_func)+cgmGEN._str_hardBreak)
        log.debug(self)
        
        if self.b_singleChain:
            return rig_frameSingle(self)
        
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
        ml_ikFullChain = mRigNull.msgList_get('ikFullChainJoints')
        
        
        b_cog = False
        if mBlock.getMessage('cogHelper'):
            b_cog = True
            
        str_ikBase = ATTR.get_enumValueString(mBlock.mNode,'ikBase')
        str_ikEnd = ATTR.get_enumValueString(mBlock.mNode,'ikEnd')        
        str_rigSetup = mBlock.getEnumValueString('rigSetup')

        #Changing targets - these change based on how the setup rolls through
        #mIKHandleDriver = mIKControl#...this will change with pivot
        mIKControl = mRigNull.getMessageAsMeta('controlIK')                
        mIKHandleDriver = mIKControl
        
        mIKControlEnd = mRigNull.getMessageAsMeta('controlIKEnd')
        if mIKControlEnd:
            log.debug("|{0}| >> mIKControlEnd ...".format(_str_func))
            mIKHandleDriver = mIKControlEnd
            mIKControlEnd.masterGroup.p_parent =mIKControl
        mPivotResultDriver = mIKControl
        #Pivot Driver =======================================================================================
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
            
            if mIKControlEnd:
                mIKControlEnd.masterGroup.p_parent = mPivotResultDriver
            
            
            mRigNull.connectChildNode(mPivotResultDriver,'pivotResultDriver','rigNull')#Connect
        
        
        if mBlock.buildLeverEnd:
            log.debug("|{0}| >> Quad setup...".format(_str_func))            
            mIKBallRotationControl = mRigNull.getMessageAsMeta('controlBallRotation')
            mIKHandleDriver = mIKBallRotationControl
            
        #Lever ===========================================================================================
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
                    mUpDecomp.doStore('cgmName',ml_handleParents[i])                
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
            
            mRigNull.connectChildNode(mIKGroup,'ikGroup','rigNull')#Connect
            
            mPlug_IKon.doConnectOut("{0}.visibility".format(mIKGroup.mNode))
            
            mIKGroup.parent = mRoot
            mIKControl.masterGroup.parent = mIKGroup
            
            mIKControlBase = mRigNull.getMessageAsMeta('controlIKBase')
            
            if mIKControlBase:
                log.debug("|{0}| >> Found controlBaseIK : {1}".format(_str_func, mIKControlBase))            
                mIKControlBase.masterGroup.p_parent = mIKGroup
                
            
            """
            mIKControlBase = False
            if mRigNull.getMessage('controlIKBase'):
                mIKControlBase = mRigNull.controlIKBase
                
                if str_ikBase == 'hips':
                    mIKControlBase.masterGroup.parent = mRoot
                else:
                    mIKControlBase.masterGroup.parent = mIKGroup
                    
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
                
                res_ikScale = self.UTILS.get_blockScale(self,
                                                        '{0}_ikMeasure'.format(self.d_module['partName'],),
                                                        self.ml_handleTargetsCulled)
                mPlug_masterScale = res_ikScale[0]
                mMasterCurve = res_ikScale[1]
                mMasterCurve.p_parent = mRoot
                self.fnc_connect_toRigGutsVis( mMasterCurve )
                mMasterCurve.dagLock(True)
                
                #Unparent the children from the end while we set stuff up...
                ml_end_children = mEnd.getChildren(asMeta=True)
                if ml_end_children:
                    for mChild in ml_end_children:
                        mChild.parent = False
                        
                
                #Build the IK ---------------------------------------------------------------------
                reload(IK)
                if mIKControlEnd and str_ikEnd in ['tipCombo']:
                    mMainIKControl = mIKControlEnd
                else:
                    mMainIKControl = mIKControl
                
                _d_ik= {'globalScaleAttr':mPlug_masterScale.p_combinedName,#mPlug_globalScale.p_combinedName,
                        'stretch':'translate',
                        'lockMid':True,
                        'rpHandle':mIKMid.mNode,
                        'nameSuffix':'ik',
                        'baseName':'{0}_ikRP'.format(self.d_module['partName']),
                        'controlObject':mMainIKControl.mNode,
                        'moduleInstance':self.mModule.mNode}
                
                d_ikReturn = IK.handle(_start,_end,**_d_ik)
                mIKHandle = d_ikReturn['mHandle']
                ml_distHandlesNF = d_ikReturn['ml_distHandles']
                mRPHandleNF = d_ikReturn['mRPHandle']
                
                
                #>>>Parent IK handles -----------------------------------------------------------------
                log.debug("|{0}| >> parent ik dat...".format(_str_func))
                
                mIKHandle.parent = mIKHandleDriver.mNode#handle to control	
                for mObj in ml_distHandlesNF[:-1]:
                    mObj.parent = mRoot
                ml_distHandlesNF[-1].parent = mIKHandleDriver.mNode#handle to control
                ml_distHandlesNF[1].parent = mIKMid
                ml_distHandlesNF[1].t = 0,0,0
                ml_distHandlesNF[1].r = 0,0,0
                
                if mIKControlBase:
                    ml_distHandlesNF[0].parent = mIKControlBase
                
                #>>> Fix our ik_handle twist at the end of all of the parenting
                IK.handle_fixTwist(mIKHandle,_jointOrientation[0])#Fix the twist
                
                if mIKControlEnd:
                    mIKEndDriver = mIKControlEnd
                else:
                    mIKEndDriver = mIKControl
                    
                    if ml_end_children:
                        for mChild in ml_end_children:
                            mChild.parent = mEnd                
                    
                    #mc.scaleConstraint([mIKControl.mNode],
                    #                    ml_ikJoints[self.int_handleEndIdx].mNode,
                    #                    maintainOffset = True)                
                    #if mIKControlBase:
                        #ml_ikJoints[0].parent = mRigNull.controlIKBase
                    
                    #if mIKControlBase:
                        #mc.pointConstraint(mIKControlBase.mNode, ml_ikJoints[0].mNode,maintainOffset=True)
                        
                    
                #Make a spin group ===========================================================
                mSpinGroup = mStart.doGroup(False,False,asMeta=True)
                mSpinGroup.doCopyNameTagsFromObject(self.mModule.mNode, ignore = ['cgmName','cgmType'])	
                mSpinGroup.addAttr('cgmName','{0}NoFlipSpin'.format(self.d_module['partName']))
                mSpinGroup.doName()
                ATTR.set(mSpinGroup.mNode, 'rotateOrder', _jointOrientation)
                
                
                mSpinGroup.parent = mIKGroup
                mSpinGroup.doGroup(True,True,typeModifier='zero')
                mSpinGroupAdd = mSpinGroup.doDuplicate()
                
                mSpinGroupAdd.doStore('cgmTypeModifier','addSpin')
                mSpinGroupAdd.doName()
                mSpinGroupAdd.p_parent = mSpinGroup
                
                if mIKControlBase:
                    mc.pointConstraint(mIKControlBase.mNode, mSpinGroup.mNode,maintainOffset=True)
                
                #Setup arg
                #mPlug_spin = cgmMeta.cgmAttr(mIKControl,'spin',attrType='float',keyable=True, defaultValue = 0, hidden = False)
                #mPlug_spin.doConnectOut("%s.r%s"%(mSpinGroup.mNode,_jointOrientation[0]))
 
                mSpinTarget = mIKControl
                    
                if mBlock.ikRPAim:
                    mc.aimConstraint(mSpinTarget.mNode, mSpinGroup.mNode, maintainOffset = False,
                                     aimVector = [0,0,1], upVector = [0,1,0], 
                                     worldUpType = 'none')
                else:
                    mc.aimConstraint(mSpinTarget.mNode, mSpinGroup.mNode, maintainOffset = False,
                                     aimVector = [0,0,1], upVector = [0,1,0], 
                                     worldUpObject = mSpinTarget.mNode,
                                     worldUpType = 'objectrotation', 
                                     worldUpVector = self.v_twistUp)
                
                mPlug_spinMid = cgmMeta.cgmAttr(mSpinTarget,'spinMid',attrType='float',defaultValue = 0,keyable = True,lock=False,hidden=False)	
                
                if self.d_module['direction'].lower() == 'right':
                    str_arg = "{0}.r{1} = -{2}".format(mSpinGroupAdd.mNode,
                                                       _jointOrientation[0].lower(),
                                                       mPlug_spinMid.p_combinedShortName)
                    log.debug("|{0}| >> Right knee spin: {1}".format(_str_func,str_arg))        
                    NODEFACTORY.argsToNodes(str_arg).doBuild()
                else:
                    mPlug_spinMid.doConnectOut("{0}.r{1}".format(mSpinGroupAdd.mNode,_jointOrientation[0]))
                    
                mSpinGroup.dagLock(True)
                mSpinGroupAdd.dagLock(True)
                
                #>>> mBallRotationControl
                mIKBallRotationControl = mRigNull.getMessageAsMeta('controlBallRotation')
                
                if mIKBallRotationControl:# and str_ikEnd not in ['tipCombo']:
                    mBallOrientGroup = cgmMeta.validateObjArg(mIKBallRotationControl.doGroup(True,False,asMeta=True,typeModifier = 'orient'),'cgmObject',setClass=True)
                    ATTR.set(mBallOrientGroup.mNode, 'rotateOrder', _jointOrientation)
                    
                    mLocBase = mIKBallRotationControl.doCreateAt()
                    mLocAim = mIKBallRotationControl.doCreateAt()
                                       
                    mLocAim.doStore('cgmTypeModifier','extendedIK')
                    mLocBase = mIKBallRotationControl.doCreateAt()
                    
                    mLocBase.doName()
                    mLocAim.doName()
                    
                    mLocAim.p_parent = ml_ikFullChain[-1]
                    mLocBase.p_parent = mIKBallRotationControl.masterGroup

                    
                    const = mc.orientConstraint([mLocAim.mNode,mLocBase.mNode],
                                                mBallOrientGroup.mNode, maintainOffset = True)[0]
                                    
                    d_blendReturn = NODEFACTORY.createSingleBlendNetwork([mIKControl.mNode,
                                                                          'extendIK'],
                                                                         [mIKControl.mNode,'resRootFollow'],
                                                                         [mIKControl.mNode,'resFullFollow'],
                                                                         keyable=True)
                
                    targetWeights = mc.orientConstraint(const,q=True,
                                                        weightAliasList=True,
                                                        maintainOffset=True)
                
                    #Connect                                  
                    d_blendReturn['d_result1']['mi_plug'].doConnectOut('%s.%s' % (const,targetWeights[0]))
                    d_blendReturn['d_result2']['mi_plug'].doConnectOut('%s.%s' % (const,targetWeights[1]))
                    d_blendReturn['d_result1']['mi_plug'].p_hidden = True
                    d_blendReturn['d_result2']['mi_plug'].p_hidden = True                    
                    
                    
                    mBallOrientGroup.dagLock(True)
                    mLocAim.dagLock(True)
                    mLocBase.dagLock(True)
                    
                    mIKBallRotationControl.p_parent = mBallOrientGroup                    
                    
                    
                    #Joint constraint -------------------------
                    mIKBallRotationControl.masterGroup.p_parent = mPivotResultDriver
                    mc.orientConstraint([mIKBallRotationControl.mNode],
                                        ml_ikJoints[self.int_handleEndIdx].mNode,
                                        maintainOffset = True)
                    mc.parentConstraint([mPivotResultDriver.mNode],
                                        ml_ikJoints[self.int_handleEndIdx+1].mNode,
                                        maintainOffset = True)
                    
                    ATTR.set_default(mIKControl.mNode, 'extendIK', 1.0)
                    mIKControl.extendIK = 0.0
                    
                    #old...
                    """
                    mBallOrientGroup = cgmMeta.validateObjArg(mIKBallRotationControl.doGroup(True,False,asMeta=True,typeModifier = 'orient'),'cgmObject',setClass=True)
                    ATTR.set(mBallOrientGroup.mNode, 'rotateOrder', _jointOrientation)
                    
                    
                    mLocBase = mIKBallRotationControl.doCreateAt()
                    mLocAim = mIKBallRotationControl.doCreateAt()
                    
                    mLocAim.doStore('cgmTypeModifier','aim')
                    mLocBase = mIKBallRotationControl.doCreateAt()
                    
                    mLocBase.doName()
                    mLocAim.doName()
                    
                    mLocAim.p_parent = mIKBallRotationControl.masterGroup
                    mLocBase.p_parent = mIKBallRotationControl.masterGroup
                    
                    
                    mAimTarget = mIKControlBase
                        
                    
                    if self.d_module['direction'].lower() == 'left':
                        v_aim = [0,0,1]
                    else:
                        v_aim = [0,0,-1]
                        
                        
                    mc.aimConstraint(mAimTarget.mNode, mLocAim.mNode, maintainOffset = True,
                                     aimVector = v_aim, upVector = [0,1,0], 
                                     worldUpObject = mSpinGroupAdd.mNode,
                                     worldUpType = 'objectrotation', 
                                     worldUpVector = self.v_twistUp)
                    

                        
                    
                    const = mc.orientConstraint([mLocAim.mNode,mLocBase.mNode],
                                                mBallOrientGroup.mNode, maintainOffset = True)[0]
                                    
                    d_blendReturn = NODEFACTORY.createSingleBlendNetwork([mIKBallRotationControl.mNode,
                                                                          'aimBack'],
                                                                         [mIKBallRotationControl.mNode,'resRootFollow'],
                                                                         [mIKBallRotationControl.mNode,'resAimFollow'],
                                                                         keyable=True)
                
                    targetWeights = mc.orientConstraint(const,q=True,
                                                        weightAliasList=True,
                                                        maintainOffset=True)
                
                    #Connect                                  
                    d_blendReturn['d_result1']['mi_plug'].doConnectOut('%s.%s' % (const,targetWeights[0]))
                    d_blendReturn['d_result2']['mi_plug'].doConnectOut('%s.%s' % (const,targetWeights[1]))
                    d_blendReturn['d_result1']['mi_plug'].p_hidden = True
                    d_blendReturn['d_result2']['mi_plug'].p_hidden = True                    
                    
                    
                    mBallOrientGroup.dagLock(True)
                    mLocAim.dagLock(True)
                    mLocBase.dagLock(True)
                    
                    mIKBallRotationControl.p_parent = mBallOrientGroup
                    
                    #Joint constraint -------------------------
                    mIKBallRotationControl.masterGroup.p_parent = mPivotResultDriver
                    mc.orientConstraint([mIKBallRotationControl.mNode],
                                        ml_ikJoints[self.int_handleEndIdx].mNode,
                                        maintainOffset = True)
                    mc.parentConstraint([mPivotResultDriver.mNode],
                                        ml_ikJoints[self.int_handleEndIdx+1].mNode,
                                        maintainOffset = True)
                    
                    ATTR.set_default(mIKBallRotationControl.mNode, 'aimBack', 1.0)
                    mIKBallRotationControl.aimBack = 0.0
                    """
                    
                elif str_ikEnd == 'bank':
                    mc.orientConstraint([mPivotResultDriver.mNode],
                                            ml_ikJoints[self.int_handleEndIdx].mNode,
                                            maintainOffset = True)
                elif str_ikEnd == 'pad':
                    mc.orientConstraint([mPivotResultDriver.mNode],
                                        ml_ikJoints[self.int_handleEndIdx].mNode,
                                        maintainOffset = True)                    
                else:
                    mc.orientConstraint([mIKEndDriver.mNode],
                                        ml_ikJoints[self.int_handleEndIdx].mNode,
                                        maintainOffset = True)

                
                #Mid IK driver -----------------------------------------------------------------------
                log.debug("|{0}| >> mid IK driver.".format(_str_func))
                mMidControlDriver = mIKMid.doCreateAt()
                mMidControlDriver.addAttr('cgmName','{0}_midIK'.format(self.d_module['partName']))
                mMidControlDriver.addAttr('cgmType','driver')
                mMidControlDriver.doName()
                mMidControlDriver.addAttr('cgmAlias', 'midDriver')
                
                    
                if mIKControlBase:
                    l_midDrivers = [mIKControlBase.mNode]
                else:
                    l_midDrivers = [mRoot.mNode]
                    
                if str_ikEnd in ['tipCombo'] and mIKControlEnd:
                    log.debug("|{0}| >> mIKControlEnd + tipCombo...".format(_str_func))
                    l_midDrivers.append(mIKControl.mNode)
                else:
                    l_midDrivers.append(mIKHandleDriver.mNode)

                
                mc.pointConstraint(l_midDrivers, mMidControlDriver.mNode)
                mMidControlDriver.parent = mSpinGroupAdd#mIKGroup
                mIKMid.masterGroup.parent = mMidControlDriver
                mMidControlDriver.dagLock(True)
                
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
                
                #Full IK chain -----------------------------------------------------------------------
                if ml_ikFullChain:
                    log.debug("|{0}| >> Full IK Chain...".format(_str_func))
                    
                    _d_ik= {'globalScaleAttr':mPlug_masterScale.p_combinedName,#mPlug_globalScale.p_combinedName,
                            'stretch':'translate',
                            'lockMid':False,
                            'rpHandle':mIKMid.mNode,
                            'baseName':'{0}_ikFullChain'.format(self.d_module['partName']),
                            'nameSuffix':'ikFull',
                            'controlObject':mIKControl.mNode,
                            'moduleInstance':self.mModule.mNode}
                                    
                    d_ikReturn = IK.handle(ml_ikFullChain[0],ml_ikFullChain[-1],**_d_ik)
                    mIKHandle = d_ikReturn['mHandle']
                    ml_distHandlesNF = d_ikReturn['ml_distHandles']
                    mRPHandleNF = d_ikReturn['mRPHandle']
                    
                    mIKHandle.parent = mIKControl.mNode#handle to control	
                    for mObj in ml_distHandlesNF[:-1]:
                        mObj.parent = mRoot
                    ml_distHandlesNF[-1].parent = mIKControl.mNode#handle to control
                    #ml_distHandlesNF[1].parent = mIKMid
                    #ml_distHandlesNF[1].t = 0,0,0
                    #ml_distHandlesNF[1].r = 0,0,0
                    
                    #>>> Fix our ik_handle twist at the end of all of the parenting
                    IK.handle_fixTwist(mIKHandle,_jointOrientation[0])#Fix the twist
                    
                    #mIKControl.masterGroup.p_parent = ml_ikFullChain[-2]
                    
                    
            elif _ikSetup == 'spline':
                log.debug("|{0}| >> spline setup...".format(_str_func))
                ml_ribbonIkHandles = mRigNull.msgList_get('ribbonIKDrivers')
                if not ml_ribbonIkHandles:
                    raise ValueError,"No ribbon IKDriversFound"
            
                log.debug("|{0}| >> ribbon ik handles...".format(_str_func))
                
                if mIKControlBase:
                    ml_ribbonIkHandles[0].parent = mIKControlBase
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
            
                mSkinCluster.doStore('cgmName', mSplineCurve)
                mSkinCluster.doName()    
                cgmGEN.func_snapShot(vars())
                
            elif _ikSetup == 'ribbon':
                log.debug("|{0}| >> ribbon setup...".format(_str_func))
                ml_ribbonIkHandles = mRigNull.msgList_get('ribbonIKDrivers')
                if not ml_ribbonIkHandles:
                    raise ValueError,"No ribbon IKDriversFound"
                
                
                
                log.debug("|{0}| >> ribbon ik handles...".format(_str_func))
                if mIKControlBase:
                    ml_ribbonIkHandles[0].parent = mIKControlBase
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
                                  paramaterization = mBlock.getEnumValueString('ribbonParam'),
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
            
                mSkinCluster.doStore('cgmName', mSurf)
                mSkinCluster.doName()    
                cgmGEN.func_snapShot(vars())
                
                
                
            else:
                raise ValueError,"Not implemented {0} ik setup".format(_ikSetup)
            
            
            
            #Parent --------------------------------------------------
            #Fk...
            #if str_ikBase == 'hips':
            #    mPlug_FKon.doConnectOut("{0}.visibility".format(ml_fkJoints[1].masterGroup.mNode))
            #    ml_fkJoints[0].p_parent = mIKControlBase
            #else:
            mPlug_FKon.doConnectOut("{0}.visibility".format(ml_fkJoints[0].masterGroup.mNode))            
            ml_blendJoints[0].parent = mRoot
            if ml_ikFullChain:
                ml_ikFullChain[0].p_parent = mRoot
                if mIKControlBase:
                    mc.pointConstraint(mIKControlBase.mNode,ml_ikFullChain[0].mNode,maintainOffset=False)
            
            ml_ikJoints[0].parent = mIKGroup            
            if mIKControlBase:
                #ml_ikJoints[0].p_parent = mIKControlBase
                mc.pointConstraint(mIKControlBase.mNode,ml_ikJoints[0].mNode,maintainOffset=False)
            
        #cgmGEN.func_snapShot(vars())
        return    
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err,localDat=vars())        

def rig_frameSingle(self):
    try:
        _short = self.d_block['shortName']
        _str_func = 'rig_frameSingle'.format(_short)
        log.debug("|{0}| >> ...".format(_str_func)+cgmGEN._str_hardBreak)
        log.debug(self)
        
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
        ml_ikFullChain = mRigNull.msgList_get('ikFullChainJoints')
        
        b_cog = False
        if mBlock.getMessage('cogHelper'):
            b_cog = True
            
        str_ikBase = ATTR.get_enumValueString(mBlock.mNode,'ikBase')
        str_ikEnd = ATTR.get_enumValueString(mBlock.mNode,'ikEnd')        
        str_rigSetup = mBlock.getEnumValueString('rigSetup')

        #Changing targets - these change based on how the setup rolls through
        #mIKHandleDriver = mIKControl#...this will change with pivot
        mIKControl = mRigNull.controlIK                
        mIKHandleDriver = mIKControl
        mIKControlEnd = mRigNull.getMessageAsMeta('controlIKEnd')
        
        if mIKControlEnd:
            log.debug("|{0}| >> mIKControlEnd ...".format(_str_func))
            mIKHandleDriver = mIKControlEnd
            
        #Pivot Driver =======================================================================================
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
            
            if mIKControlEnd:
                mIKControlEnd.masterGroup.p_parent = mPivotResultDriver
            
            mRigNull.connectChildNode(mPivotResultDriver,'pivotResultDriver','rigNull')#Connect
        
            
        #Lever ===========================================================================================
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
                    mUpDecomp.doStore('cgmName',ml_handleParents[i])                
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
            
            mRigNull.connectChildNode(mIKGroup,'ikGroup','rigNull')#Connect
        
                        
            
            mPlug_IKon.doConnectOut("{0}.visibility".format(mIKGroup.mNode))
            
            mIKGroup.parent = mRoot
            mIKControl.masterGroup.parent = mIKGroup
            
            mIKControlBase = mRigNull.getMessageAsMeta('controlIKBase')
            
            if mIKControlBase:
                log.debug("|{0}| >> Found controlBaseIK : {1}".format(_str_func, mIKControlBase))            
                mIKControlBase.masterGroup.p_parent = mIKGroup
                
            
            if mIKControlEnd:
                mIKControlEnd.masterGroup.p_parent = mIKGroup
                
           
            if _ikSetup == 'rp':
                log.debug("|{0}| >> rp setup...".format(_str_func,_ikSetup))
                
                """
                #Make a spin group
                log.debug("|{0}| >> spin Group...".format(_str_func,_ikSetup))                
                mSpinGroup = mStart.doGroup(False,False,asMeta=True)
                mSpinGroup.doCopyNameTagsFromObject(self.mModule.mNode, ignore = ['cgmName','cgmType'])	
                mSpinGroup.addAttr('cgmName','{0}NoFlipSpin'.format(self.d_module['partName']))
                mSpinGroup.doName()
                ATTR.set(mSpinGroup.mNode, 'rotateOrder', _jointOrientation)
            
                mSpinGroup.parent = mIKGroup
                mSpinGroup.doGroup(True,True,typeModifier='zero')
                mSpinGroupAdd = mSpinGroup.doDuplicate()
            
                mSpinGroupAdd.doStore('cgmTypeModifier','addSpin')
                mSpinGroupAdd.doName()
                mSpinGroupAdd.p_parent = mSpinGroup

            
                mSpinTarget = mIKControl
            
                if mBlock.ikRPAim:
                    mc.aimConstraint(mSpinTarget.mNode, mSpinGroup.mNode, maintainOffset = False,
                                     aimVector = [0,0,1], upVector = [0,1,0], 
                                     worldUpType = 'none')
                else:
                    mc.aimConstraint(mSpinTarget.mNode, mSpinGroup.mNode, maintainOffset = False,
                                     aimVector = [0,0,1], upVector = [0,1,0], 
                                     worldUpObject = mSpinTarget.mNode,
                                     worldUpType = 'objectrotation', 
                                     worldUpVector = self.v_twistUp)
            
                mPlug_spinMid = cgmMeta.cgmAttr(mSpinTarget,'spinMid',attrType='float',defaultValue = 0,keyable = True,lock=False,hidden=False)	
            
                if self.d_module['mirrorDirection'].lower() == 'right':
                    str_arg = "{0}.r{1} = -{2}".format(mSpinGroupAdd.mNode,
                                                       _jointOrientation[0].lower(),
                                                       mPlug_spinMid.p_combinedShortName)
                    log.debug("|{0}| >> Right knee spin: {1}".format(_str_func,str_arg))        
                    NODEFACTORY.argsToNodes(str_arg).doBuild()
                else:
                    mPlug_spinMid.doConnectOut("{0}.r{1}".format(mSpinGroupAdd.mNode,_jointOrientation[0]))
            
                mSpinGroup.dagLock(True)
                mSpinGroupAdd.dagLock(True)
                """
                
                mc.aimConstraint(mIKControl.mNode, ml_ikJoints[0].mNode, maintainOffset = True,
                                 aimVector = [0,0,1], upVector = [0,1,0], 
                                 worldUpObject = mIKControl.mNode,
                                 worldUpType = 'objectrotation', 
                                 worldUpVector = [0,1,0])                
                
                
                #mIKMid = mRigNull.controlIKMid
                
                #res_ikScale = self.UTILS.get_blockScale(self,
                #                                        '{0}_ikMeasure'.format(self.d_module['partName'],),
                 #                                       self.ml_handleTargetsCulled)
                #mPlug_masterScale = res_ikScale[0]
                #mMasterCurve = res_ikScale[1]
                #mMasterCurve.p_parent = mRoot
                #self.fnc_connect_toRigGutsVis( mMasterCurve )
                #mMasterCurve.dagLock(True)
                
                #Unparent the children from the end while we set stuff up...
                ml_end_children = mEnd.getChildren(asMeta=True)
                if ml_end_children:
                    for mChild in ml_end_children:
                        mChild.parent = False
                        
                
                #Build the IK ---------------------------------------------------------------------
                #if mIKControlEnd and str_ikEnd in ['tipCombo']:
                #    mMainIKControl = mIKControlEnd
                #else:
                mMainIKControl = mIKControl
                


                #IK.handle_fixTwist(mIKHandle,_jointOrientation[0])#Fix the twist
                
                if mIKControlEnd:
                    mIKEndDriver = mIKControlEnd
                else:
                    mIKEndDriver = mIKControl
                    
                mc.orientConstraint([mIKEndDriver.mNode],
                                    ml_ikJoints[self.int_handleEndIdx].mNode,
                                    maintainOffset = True)
                
                if ml_end_children:
                    for mChild in ml_end_children:
                        mChild.parent = mEnd                
                
                #mc.scaleConstraint([mIKControl.mNode],
                #                    ml_ikJoints[self.int_handleEndIdx].mNode,
                #                    maintainOffset = True)                
                #if mIKControlBase:
                    #ml_ikJoints[0].parent = mRigNull.controlIKBase
                
                #if mIKControlBase:
                    #mc.pointConstraint(mIKControlBase.mNode, ml_ikJoints[0].mNode,maintainOffset=True)

        
            else:
                raise ValueError,"Not implemented {0} ik setup".format(_ikSetup)
            
            
            
            #Parent --------------------------------------------------
            #Fk...
            #if str_ikBase == 'hips':
            #    mPlug_FKon.doConnectOut("{0}.visibility".format(ml_fkJoints[1].masterGroup.mNode))
            #    ml_fkJoints[0].p_parent = mIKControlBase
            #else:
            mPlug_FKon.doConnectOut("{0}.visibility".format(ml_fkJoints[0].masterGroup.mNode))            
            ml_blendJoints[0].parent = mRoot
            if ml_ikFullChain:
                ml_ikFullChain[0].p_parent = mRoot
            
            ml_ikJoints[0].parent = mIKGroup            
            if mIKControlBase:
                mc.pointConstraint(mIKControlBase.mNode,ml_ikJoints[0].mNode,maintainOffset=False)
            
        #cgmGEN.func_snapShot(vars())
        return    
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err,localDat=vars())        



@cgmGEN.Timer
def rig_blendFrame(self):
    try:
        _short = self.d_block['shortName']
        _str_func = 'rig_blendFrame'
        log.debug("|{0}| >> ...".format(_str_func)+cgmGEN._str_hardBreak)
        log.debug(self)
        
        mBlock = self.mBlock
        mRigNull = self.mRigNull
        mRootParent = self.mConstrainNull
        
        ml_rigJoints = mRigNull.msgList_get('rigJoints')
        ml_fkJoints = mRigNull.msgList_get('fkJoints')
        #ml_fkAttachJoints = mRigNull.msgList_get('fkAttachJoints')
        ml_fkAttachJoints = []
        for mObj in ml_fkJoints:
            mAttach = mObj.getMessageAsMeta('fkAttach')
            ml_fkAttachJoints.append(mAttach or mObj)
            
            
        ml_ikJoints = mRigNull.msgList_get('ikJoints')
        if not ml_ikJoints:
            log.debug("|{0}| >> No ik setup...".format(_str_func))        
            return True 
        ml_blendJoints = mRigNull.msgList_get('blendJoints')
        
        mSettings = mRigNull.settings    
        mPlug_FKIK = cgmMeta.cgmAttr(mSettings,'FKIK',attrType='float',lock=False,keyable=True)
        
        ml_scaleJoints = []
        def getScaleJoint(mJnt):
            mDup = mJnt.doDuplicate(po=True,ic=False)
            mDup.p_parent = mJnt
            mDup.rename("{0}_scaled".format(mJnt.p_nameBase))
            mDup.connectParentNode(mJnt,'source','scaleJoint')
            mDup.resetAttrs()
            ml_scaleJoints.append(mDup)
            return mDup
        
        
        if mBlock.getEnumValueString('rigSetup') == 'digit':
            #This was causing issues with toe setup , need to resolve...
            log.debug("|{0}| >> Digit mode. Scale constraining deform null...".format(_str_func))
            #raise ValueError,"This was causing issues with toe setup , need to resolve..."
            self.mDeformNull.p_parent = self.md_dynTargetsParent['attachDriver'].mNode
        
        #Setup blend ----------------------------------------------------------------------------------
        if self.b_scaleSetup:
            """
                mc.scaleConstraint(self.md_dynTargetsParent['attachDriver'].mNode,
                                   self.mDeformNull.mNode,
                                   maintainOffset=True,
                                   scaleCompensate=False)"""        
    
            log.debug("|{0}| >> scale blend chain setup...".format(_str_func))
            
            log.debug("|{0}| >> fk setup...".format(_str_func))
            
            str_aimAxis = self.d_orientation['str'][0]
            """
            #Scale setup for fk joints -------------------------------------------------------------------
            for i,mJnt in enumerate(ml_fkJoints[1:self.int_handleEndIdx+1]):
                mDup = mJnt.doDuplicate(po=True,ic=False)
                mDup.p_parent = ml_fkJoints[i]
                mDup.rename("{0}_scaleHolder".format(mJnt.p_nameBase))
                print mDup
                
                mJnt.masterGroup.p_parent = mDup
                
                mPlug_base = cgmMeta.cgmAttr(mDup.mNode,
                                             "aimBase",
                                             attrType = 'float',
                                             lock=True,
                                             value=ATTR.get(mDup.mNode,"t{0}".format(str_aimAxis)))
                mPlug_inverse = cgmMeta.cgmAttr(mDup.mNode,
                                                "aimInverse",
                                                attrType = 'float',
                                                lock=True)
                
                
                l_argBuild = []
                l_argBuild.append("{0} = 1 / {1}".format(mPlug_inverse.p_combinedShortName,
                                                         "{0}.s{1}".format(ml_fkJoints[i].mNode, str_aimAxis)))
                l_argBuild.append("{0} = {1} * {2}".format("{0}.t{1}".format(mDup.mNode, str_aimAxis),
                                                           mPlug_inverse.p_combinedShortName,
                                                           mPlug_base.p_combinedShortName))
                for arg in l_argBuild:
                    log.debug("|{0}| >> Building arg: {1}".format(_str_func,arg))
                    NODEFACTORY.argsToNodes(arg).doBuild()
            """
            
    
            pprint.pprint(vars())
            
    
            log.debug(cgmGEN._str_subLine)    
    
            log.debug("|{0}| >> ik setup...".format(_str_func))
            
            #Scale setup for ik joints -------------------------------------------------------------------
            ml_ikScaleTargets = []
            ml_ikScaleDrivers = copy.copy(ml_ikJoints)
            
            for i,mJnt in enumerate(ml_ikScaleDrivers[:self.int_handleEndIdx]):
                ml_ikScaleDrivers[i] = getScaleJoint(mJnt)
                
            ml_blendScaleTargets = []
            for i,mJnt in enumerate(ml_blendJoints):
                if mJnt in ml_blendJoints[:self.int_handleEndIdx]:
                    ml_blendScaleTargets.append(getScaleJoint(mJnt))
                else:
                    ml_blendScaleTargets.append(mJnt)
            
            mIKControl = mRigNull.getMessageAsMeta('controlIK')
            mIKControlBase = mRigNull.getMessageAsMeta('controlIKBase')
            mLimbRoot = mRigNull.getMessageAsMeta('limbRoot')
            mIKControlMid = mRigNull.getMessageAsMeta('controlIKMid')
    
            if mIKControlBase:
                log.debug("|{0}| >> Found controlBaseIK : {1}".format(_str_func, mIKControlBase))        
                ml_ikScaleTargets.append(mIKControlBase)
            elif mLimbRoot:
                ml_ikScaleTargets.append(mLimbRoot)
            else:
                ml_ikScaleTargets.append(mRoot)
            
            ml_ikScaleTargets.append(ml_ikJoints[self.int_handleEndIdx])#mIKControl
            log.debug("|{0}| >> Constrain ik 0 to : {1}".format(_str_func, ml_ikScaleTargets[0]))
            mc.scaleConstraint(ml_ikScaleTargets[0].mNode, ml_ikScaleDrivers[0].mNode,
                               maintainOffset=True,
                               scaleCompensate=False)
            
            log.debug("|{0}| >> Constrain ik end to : {1}".format(_str_func,mIKControl))
            mc.scaleConstraint(mIKControl.mNode, ml_ikScaleDrivers[self.int_handleEndIdx].mNode,
                               maintainOffset=True,
                               scaleCompensate=False)
            
            _targets = [mHandle.mNode for mHandle in ml_ikScaleTargets]
        
            #Scale setup for mid set IK
            """
            if mIKControlMid:
                log.debug("|{0}| >> Mid control scale...".format(_str_func))                    
                mMasterGroup = mIKControlMid.masterGroup
                _vList = DIST.get_normalizedWeightsByDistance(mMasterGroup.mNode,_targets)
                _scale = mc.scaleConstraint(_targets,mMasterGroup.mNode,maintainOffset = True)#Point contraint loc to the object
                CONSTRAINT.set_weightsByDistance(_scale[0],_vList)                
                ml_ikScaleTargets.append(mIKControlMid)
                _targets = [mHandle.mNode for mHandle in ml_ikScaleTargets]"""
        
            for mJnt in ml_ikScaleDrivers[1:self.int_handleEndIdx]:
                _vList = DIST.get_normalizedWeightsByDistance(mJnt.mNode,_targets)
                _scale = mc.scaleConstraint(_targets,mJnt.mNode,maintainOffset = True,
                                            scaleCompensate=False)#Point contraint loc to the object
                CONSTRAINT.set_weightsByDistance(_scale[0],_vList)
        
            #for mJnt in ml_ikJoints[1:]:
                #mJnt.p_parent = mIKGroup
                
            for mJnt in ml_ikJoints[self.int_handleEndIdx:]:
                mJnt.segmentScaleCompensate = False
                
            for mJnt in ml_blendJoints:
                mJnt.segmentScaleCompensate = False
                if mJnt == ml_blendJoints[0]:
                    continue
                mJnt.p_parent = ml_blendJoints[0].p_parent
            log.debug(cgmGEN._str_subLine)    
            
            
            RIGCONSTRAINT.blendChainsBy(ml_fkAttachJoints,ml_ikScaleDrivers,ml_blendJoints,
                                        driver = mPlug_FKIK.p_combinedName,
                                        l_constraints=['point','orient'])
            
            RIGCONSTRAINT.blendChainsBy(ml_fkAttachJoints,ml_ikScaleDrivers,ml_blendScaleTargets,
                                        driver = mPlug_FKIK.p_combinedName,
                                        d_scale = {'scaleCompensate':False},
                                        l_constraints=['scale'])        
    
            for mJnt in ml_scaleJoints:
                mJnt.dagLock(True)
        else:
            log.debug("|{0}| >> Normal setup...".format(_str_func))
            RIGCONSTRAINT.blendChainsBy(ml_fkAttachJoints,ml_ikJoints,ml_blendJoints,
                                        driver = mPlug_FKIK,
                                        l_constraints=['point','orient'])
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err,localDat=vars())        
        
@cgmGEN.Timer
def rig_pivotSetup(self):
    try:
        _short = self.d_block['shortName']
        _str_func = 'rig_pivotSetup'.format(_short)
        log.debug("|{0}| >> ...".format(_str_func)+cgmGEN._str_hardBreak)
        log.debug(self)
        
        if not self.b_pivotSetup and not self.b_followParentBank:
            log.debug("|{0}| >> No pivot setup...".format(_str_func))
            return True
        
        mBlock = self.mBlock
        mRigNull = self.mRigNull
        mRootParent = self.mConstrainNull
        mModule = self.mModule
        _jointOrientation = self.d_orientation['str']
        _side = mBlock.atUtils('get_side')
        mRoot = mRigNull.rigRoot
        
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
        mIKControlEnd = mRigNull.getMessageAsMeta('controlIKEnd')
        if mIKControlEnd:
            log.debug("|{0}| >> mIKControlEnd ...".format(_str_func))
            mIKHandleDriver = mIKControlEnd
        else:
            mIKHandleDriver = mIKControl
            
        #Follow parent bank ===============================================================================
        if self.b_followParentBank:
            log.debug("|{0}| >> followParentBank setup ...".format(_str_func)+'-'*40)
            ml_followParentBankJoints = mRigNull.msgList_get('followParentBankJoints')
            mControlFollowParentBank = mRigNull.getMessageAsMeta('controlFollowParentBank')
        
            #ml_followParentBankJoints[0].p_parent = self.mPivotResult_moduleParent
            mLimbRoot = mRigNull.getMessageAsMeta('limbRoot')
            if not mLimbRoot:
                mLimbRoot = mRoot
            ml_followParentBankJoints[0].p_parent = mLimbRoot
            #mc.parentConstraint(mLimbRoot.mNode,
            #                    ml_followParentBankJoints[0].mNode,
            #                    maintainOffset = True)
        
            mControlFollowParentBank.masterGroup.parent = self.d_module['mModuleParent'].rigNull.controlIK
            mIKControlTarget = ml_followParentBankJoints[-1]
            ml_fkAimJoints = ml_followParentBankJoints
        
            if 'yes' == 'yes':
                ml_chain1 = ml_followParentBankJoints[:-1]
                mChain2Base = ml_followParentBankJoints[-2].doDuplicate(po=True)
                mChain2Base.p_parent = ml_followParentBankJoints[-2]
        
                ml_followParentBankJoints[-1].p_parent = mChain2Base
                ml_chain2 = [mChain2Base, ml_followParentBankJoints[-1]]
                pprint.pprint(vars())
        
                #Make our fk chain -----------------------------------------------------
                mFKAim_base = ml_followParentBankJoints[0].doDuplicate(po=True)
                mFKAim_end = ml_followParentBankJoints[-1].doDuplicate(po=True)
                ml_fkAimJoints = [mFKAim_base, mFKAim_end]
                mFKAim_end.p_parent = mFKAim_base
        
                mFKAim_base.p_parent = mLimbRoot
        
                JOINT.orientChain(ml_fkAimJoints,
                                  worldUpAxis=mBlock.orientHelper.getAxisVector('y+'))
        
                for i,mJnt in enumerate(ml_fkAimJoints):
                    mJnt.rename('{0}_bank_fkDriver_{1}'.format(self.d_module['partName'],i))
        
        
        
                #IK follow setup -------------------------------------------------------
                d_chains = {'start':{'start':ml_chain1[0],
                                     'end':ml_chain1[-1],
                                     'baseName':self.d_module['partName'] + 'followParentBankIK1',},
                            'end':{'start':ml_chain2[0],
                                   'end':ml_chain2[-1],
                                   'baseName':self.d_module['partName'] + 'followParentBankIK2'}}
                for t in ['start','end']:
                    d_return = IK.handle(d_chains[t]['start'].mNode,
                                         d_chains[t]['end'].mNode,
                                         solverType='ikSCsolver',
                                         baseName=d_chains[t]['baseName'],
                                         moduleInstance=mModule)
        
                    mIKHandle = d_return['mHandle']
                    mIKHandle.parent = mControlFollowParentBank
        
                mIKControlTarget = ml_chain2[0]
        
                #--------------------------------------------------------------
        
        
            else:
                #Build IK Chain
                log.debug("|{0}| >> followParentBank ik chain ...".format(_str_func)+'-'*40)
        
                d_return = IK.handle(ml_followParentBankJoints[0].mNode,
                                     ml_followParentBankJoints[-1].mNode,
                                     solverType='ikSCsolver',
                                     baseName=self.d_module['partName'] + 'followParentBankIK',
                                     moduleInstance=mModule)
        
                mIKHandle = d_return['mHandle']
                mIKHandle.parent = mControlFollowParentBank
        
            #Connect the parts -------------------------------------------------------------------------
            log.debug("|{0}| >> pivotBank | ik connection setup ...".format(_str_func)+'-'*40)
            
            def create_digitParentBlendDag(mBankDriver,
                                           plugToRigNull,
                                           alias,
                                           mRoot,
                                           mParentSettings,
                                           attrOne,
                                           attrTwo):
            
                #Need to create a dag to blend
                #Create a dag as a solid base
                #Find parent blend attrs            
                mBase = mBankDriver.doDuplicate(po=True)
                mBlend = mBankDriver.doDuplicate(po=True)
                
                for mDag in mBase,mBlend:
                    mDag.p_parent = mRoot
                    
                
                _constraint = mc.parentConstraint([mBase.mNode,mBankDriver.mNode],
                                                  mBlend.mNode,
                                                  maintainOffset=True)[0]
                
                targetWeights = mc.parentConstraint(_constraint,q=True,
                                                    weightAliasList=True,
                                                    maintainOffset=True)
                
                #Connect                                  
                _parentsettings = mParentSettings.mNode
                ATTR.connect("{0}.{1}".format(_parentsettings,attrOne),
                             "{0}.{1}".format(_constraint,targetWeights[0]))
                ATTR.connect("{0}.{1}".format(_parentsettings,attrTwo),
                             "{0}.{1}".format(_constraint,targetWeights[1]))    
                    
                
                
                mBlend.doStore('cgmAlias', alias)                    
                mRigNull.connectChildNode(mBlend,plugToRigNull,'rigNull')#Connect        
                
                return mBlend
            
            mParentSettings = self.d_module['mModuleParent'].rigNull.settings
            
            create_digitParentBlendDag(mIKControlTarget,'bankParentIKDriver',
                                       'followParentBank',mLimbRoot,mParentSettings,
                                       'result_FKon','result_IKon')
            
            #mIKControlTarget.doStore('cgmAlias', 'followParentBank')        
            #mRigNull.connectChildNode(mIKControlTarget,'bankParentIKDriver','rigNull')#Connect        
            
            
            log.debug("|{0}| >> pivotBank | fk connection setup ...".format(_str_func)+'-'*40)
            #mRigNull.connectChildNode(ml_fkAimJoints[0].mNode,'bankParentFKDriver','rigNull')#Connect
            create_digitParentBlendDag(ml_fkAimJoints[0],'bankParentFKDriver',
                                       'followParentBank',mLimbRoot,mParentSettings,
                                       'result_FKon','result_IKon')
        
            #Setup blends to turn off and on
            mFKGroup = self.mRigNull.getMessageAsMeta('fkGroup')
            #mAimGroup = mFKGroup.doGroup(True,True,typeModifier='aim',asMeta=True)
            #mAimDriver = mFKGroup.groupChild.doCreateAt(setClass=True)
        
            #mAimDriver.doStore('cgmName',self.d_module['partName'] + 'bankAimFK')
            #mAimDriver.doStore('cgmType','driver')
            #mAimDriver.doName()
            #mAimDriver.p_parent = ml_followParentBankJoints[0]
        
            #mAimDriver.doStore('cgmAlias', 'followParentBank')
            #mRigNull.connectChildNode(mAimDriver,'bankParentFKDriver','rigNull')#Connect
            
            """
            d_aimFK = IK.handle(ml_fkAimJoints[0].mNode,
                                ml_fkAimJoints[-1].mNode,
                                solverType='ikSCsolver',
                                baseName = self.d_module['partName'] + 'followFKBank',
                                moduleInstance=mModule)
            mHandle = d_aimFK['mHandle']
            mHandle.parent = mControlFollowParentBank.mNode#toeIK to wiggle
            """
        
            
            mc.aimConstraint(mControlFollowParentBank.mNode, ml_fkAimJoints[0].mNode, maintainOffset = True,
                             aimVector = [0,0,1], upVector = [0,1,0], 
                             worldUpObject = mLimbRoot.mNode,
                             worldUpType = 'objectrotation', 
                             worldUpVector = [0,1,0])
            """
                mc.aimConstraint(ml_followParentBankJoints[-1].mNode, mAimGroup.mNode, maintainOffset = True,
                                 aimVector = [0,0,1], upVector = [0,1,0], 
                                 worldUpObject = mFKGroup.mNode,
                                 worldUpType = 'objectrotation', 
                                 worldUpVector = [0,1,0])"""
        
            #mc.parentConstraint(ml_followParentBankJoints[0].mNode, mLimbRoot.mNode, maintainOffset=True)
        
    
            """
                mc.parentConstraint(mIKControlTarget.mNode,
                                    mIKControl.mNode,
                                    maintainOffset=True)"""
        
            return    
        
        
        
        
            
        #Pivot Driver ===============================================================================
        mBallPivotJoint = None
        mBallWiggleJoint = None
        
        if self.b_pivotSetup:
            mPivotResultDriver = mRigNull.getMessage('pivotResultDriver',asMeta=True)[0]
            _pivotSetup = ATTR.get_enumValueString(self.mBlock.mNode,'ikEnd')
            
            if self.b_leverEnd or _pivotSetup in ['pad']:
                _pivotSetup == 'bank'
                
            mToeIK = False
            mBallIK = False
            b_realToe = False
            if _pivotSetup == 'foot':
                log.debug("|{0}| >> foot ...".format(_str_func))
                
                _mode = 'foot'
                
                ml_ikJoints = mRigNull.msgList_get('ikJoints')
                if self.mToe:
                    mToeIK = ml_ikJoints.pop(-1)
                    b_realToe = True
                if self.mBall:
                    mBallIK = ml_ikJoints.pop(-1)
                    
                    if not mToeIK:
                        mToeIK = mRigNull.getMessageAsMeta('toe_helpJoint')
                        
                
                mAnkleIK = ml_ikJoints[-1]
                mBallPivotJoint = mRigNull.getMessageAsMeta('pivot_ballJoint')
                mBallWiggleJoint = mRigNull.getMessageAsMeta('pivot_ballWiggle')
                for mObj in mBallPivotJoint,mBallWiggleJoint:
                    if mObj:
                        mObj.radius = 0
                pprint.pprint(vars())
    
            else:
                _mode = 'default'
                
            
            #pprint.pprint(vars())
             
            mBlock.atBlockUtils('pivots_setup',
                                mControl = mIKControl, 
                                mRigNull = mRigNull, 
                                pivotResult = mPivotResultDriver,
                                mBallJoint= mBallPivotJoint,
                                mBallWiggleJoint = mBallWiggleJoint,
                                mToeJoint = mToeIK,
                                rollSetup = _mode,
                                #mDag = mIKHandleDriver,
                                front = 'front', back = 'back')#front, back to clear the toe, heel defaults
            
            if _mode == 'foot':#and not mBlock.buildLeverEnd and not self.b_quadFront:
                log.debug("|{0}| >> foot ik".format(_str_func))
                
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
        
                if mToeIK and b_realToe:
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
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err,localDat=vars())        

            
#@cgmGEN.Timer
def rig_matchSetup(self):
    try:
        _short = self.d_block['shortName']
        _str_func = 'rig_matchSetup'.format(_short)
        log.debug("|{0}| >> ...".format(_str_func)+cgmGEN._str_hardBreak)
  
        
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
        
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err,localDat=vars())        
    


@cgmGEN.Timer
def rig_cleanUp(self):
    try:
        _short = self.d_block['shortName']
        _str_func = 'rig_cleanUp'
        log.debug("|{0}| >> ...".format(_str_func)+cgmGEN._str_hardBreak)
        log.debug(self)
        
        mBlock = self.mBlock
        mRigNull = self.mRigNull
        mSettings = mRigNull.settings
        mRoot = mRigNull.rigRoot
        
        if not mRoot.hasAttr('cgmAlias'):
            mRoot.addAttr('cgmAlias','{0}_root'.format(self.d_module['partName']))
            
        #mRootParent = self.mConstrainNull
        mMasterControl= self.d_module['mMasterControl']
        mMasterDeformGroup= self.d_module['mMasterDeformGroup']    
        mMasterNull = self.d_module['mMasterNull']
        mModuleParent = self.d_module['mModuleParent']
        mPlug_globalScale = self.d_module['mPlug_globalScale']
        _baseNameAttrs = ATTR.datList_getAttrs(mBlock.mNode,'nameList')        
        ml_blendJoints = mRigNull.msgList_get('blendJoints')
        ml_ikFullChain = mRigNull.msgList_get('ikFullChainJoints')
        str_blockProfile = mBlock.blockProfile#ATTR.get_enumValueString(_short,'blockProfile')
        
        str_ikEnd = ATTR.get_enumValueString(mBlock.mNode,'ikEnd')        
        str_rigSetup  =  mBlock.getEnumValueString('rigSetup')
       
        b_ikOrientToWorld = mBlock.ikOrientToWorld
    
        #Changing targets - these change based on how the setup rolls through
        mIKControlEnd = mRigNull.getMessageAsMeta('controlIKEnd')
    
        
        ml_controlsToSetup = []
        for msgLink in ['rigJoints','controlIK']:
            ml_buffer = mRigNull.msgList_get(msgLink)
            if ml_buffer:
                log.debug("|{0}| >>  Found: {1}".format(_str_func,msgLink))            
                ml_controlsToSetup.extend(ml_buffer)
    
        #if not self.mConstrainNull.hasAttr('cgmAlias'):
            #self.mConstrainNull.addAttr('cgmAlias','{0}_rootNull'.format(self.d_module['partName']))
        
        mAttachDriver = self.md_dynTargetsParent['attachDriver']
        if not mAttachDriver.hasAttr('cgmAlias'):
            mAttachDriver.addAttr('cgmAlias','{0}_rootDriver'.format(self.d_module['partName']))    
                
            
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
            
            ml_targetDynParents = [mLeverFK]# + self.md_dynTargetsParent['attachDriver']+ ml_endDynParents
            #if str_rigSetup not in ['digit']:
            ml_targetDynParents.append(self.md_dynTargetsParent['attachDriver'])
            ml_targetDynParents.extend(ml_endDynParents)
            
            mDynGroup = cgmRigMeta.cgmDynParentGroup(dynChild=mLimbRoot.mNode,dynMode=0)
            
            log.debug("|{0}| >>  Root Targets...".format(_str_func,mLimbRoot))
            
            if not mLimbRoot.hasAttr('cgmAlias'):
                mLimbRoot.addAttr('cgmAlias','{0}_limbRoot'.format(self.d_module['partName']))
                
            if not mLeverFK.hasAttr('cgmAlias'):
                ATTR.copy_to(mBlock.mNode,_baseNameAttrs[0],mLeverFK.mNode, 'cgmAlias', driven='target')            
                mLeverFK.addAttr('cgmAlias','{0}_lever'.format(self.d_module['partName']))
                    
            for mTar in ml_targetDynParents:
                mDynGroup.addDynParent(mTar)
            mDynGroup.rebuild()
            #mDynGroup.dynFollow.p_parent = self.mConstrainNull
            
            log.debug(cgmGEN._str_subLine)        
            ml_baseDynParents.append(mLimbRoot)
            ml_baseDynParents.append(mLeverFK)
            
            if self.b_singleChain:
                log.debug("|{0}| >>  Single chain and lever...".format(_str_func))
                mDynGroup = cgmRigMeta.cgmDynParentGroup(dynChild=mLeverFK.mNode,dynMode=0)
                for mTar in ml_endDynParents:
                    mDynGroup.addDynParent(mTar)
                mDynGroup.rebuild()
                
                
        else:
            ml_baseDynParents.append(mRoot)
        
        #pprint.pprint(vars())
        
        #...Root controls ================================================================================
        log.debug("|{0}| >>  Root: {1}".format(_str_func,mRoot))
        mDynGroup = cgmRigMeta.cgmDynParentGroup(dynChild=mRoot.mNode,dynMode=0)
        
        ml_targetDynParents = []
        #if str_rigSetup not in ['digit']:
        ml_targetDynParents = [self.md_dynTargetsParent['attachDriver']]
        #else:
        #    ml_targetDynParents = [mDynGroup.p_parent]
            
        if not mRoot.hasAttr('cgmAlias'):
            mRoot.addAttr('cgmAlias','{0}_root'.format(self.d_module['partName']))
        
        #if str_rigSetup not in ['digit']:
        ml_targetDynParents.extend(self.ml_dynEndParents)
    
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
        mControlIK = mRigNull.getMessageAsMeta('controlIK')
        
        if mControlIK:
            mControlIK = mRigNull.controlIK
            ml_ikControls.append(mControlIK)
        if mRigNull.getMessage('controlIKBase'):
            ml_ikControls.append(mRigNull.controlIKBase)
            
        for mHandle in ml_ikControls:
            log.debug("|{0}| >>  IK Handle: {1}".format(_str_func,mHandle))
            
            if b_ikOrientToWorld:
                BUILDUTILS.control_convertToWorldIK(mHandle)
            
            ml_targetDynParents = copy.copy(ml_baseDynParents)
            if mHandle == mControlIK:
                mParentBank = mRigNull.getMessageAsMeta('bankParentIKDriver')
                if mParentBank:
                    log.debug("|{0}| >>  found parent bank".format(_str_func,mHandle))
                    ml_targetDynParents.insert(0,mParentBank)
                    
            #if str_rigSetup not in ['digit']:
            ml_targetDynParents.append(self.md_dynTargetsParent['attachDriver'])
            ml_targetDynParents.extend(ml_endDynParents)
            
            ml_targetDynParents.append(self.md_dynTargetsParent['world'])
            ml_targetDynParents.extend(mHandle.msgList_get('spacePivots',asMeta = True))
        
            mDynGroup = cgmRigMeta.cgmDynParentGroup(dynChild=mHandle,dynMode=0)
            #mDynGroup.dynMode = 2
        
            for mTar in ml_targetDynParents:
                mDynGroup.addDynParent(mTar)
            mDynGroup.rebuild()
            #mDynGroup.dynFollow.p_parent = self.mConstrainNull
            
            if mHandle == mControlIK:
                if str_blockProfile in ['leg'] or str_ikEnd in ['pad','foot']:
                    #_idx = ml_targetDynParents.index( self.dynTargets(puppet))
                    ATTR.set_default(mHandle.mNode,'space','puppet')
            
        log.debug("|{0}| >>  IK targets...".format(_str_func))
        pprint.pprint(ml_targetDynParents)        
        
        log.debug(cgmGEN._str_subLine)
                  
        
        if mRigNull.getMessage('controlIKMid'):
            log.debug("|{0}| >>  IK Mid Handle ... ".format(_str_func))                
            mHandle = mRigNull.controlIKMid
            
            if b_ikOrientToWorld:
                BUILDUTILS.control_convertToWorldIK(mHandle)
            
            mParent = mHandle.masterGroup.getParent(asMeta=True)
            ml_targetDynParents = []
        
            if not mParent.hasAttr('cgmAlias'):
                mParent.addAttr('cgmAlias','midIKBase')
            
            mPivotResultDriver = mRigNull.getMessage('pivotResultDriver',asMeta=True)
            if mPivotResultDriver:
                mPivotResultDriver = mPivotResultDriver[0]
            ml_targetDynParents = [mParent,mPivotResultDriver]
            
            ml_targetDynParents.append(mControlIK)
                
            ml_targetDynParents.extend(ml_baseDynParents)
            #if str_rigSetup not in ['digit']:
            ml_targetDynParents.extend(ml_endDynParents)        
            #ml_targetDynParents.extend(mHandle.msgList_get('spacePivots',asMeta = True))
        
            mDynGroup = cgmRigMeta.cgmDynParentGroup(dynChild=mHandle,dynMode=0)
            #mDynGroup.dynMode = 2
            if b_ikOrientToWorld:
                mDynGroup.dynMode = 3#...point
                
                mHandle.masterGroup.p_parent = mRigNull.getMessage('ikGroup')[0]
        
            for mTar in ml_targetDynParents:
                mDynGroup.addDynParent(mTar)
            mDynGroup.rebuild()
            
            #if b_ikOrientToWorld:
                #mDynGroup.dynFollow.p_parent = self.mConstrainNull
            
            log.debug("|{0}| >>  IK Mid targets...".format(_str_func,mRoot))
            pprint.pprint(ml_targetDynParents)                
            log.debug(cgmGEN._str_subLine)
        
        if mIKControlEnd:
            if str_ikEnd in ['tipCombo']:
                ml_targetDynParents = []
                #ml_baseDynParents + [self.md_dynTargetsParent['attachDriver']] + ml_endDynParents
                       
                ml_targetDynParents.append(self.md_dynTargetsParent['world'])
                ml_targetDynParents.extend(mIKControlEnd.msgList_get('spacePivots',asMeta = True))
                ml_targetDynParents.insert(0,ml_ikFullChain[-2])            
            
                mDynGroup = cgmRigMeta.cgmDynParentGroup(dynChild=mIKControlEnd,dynMode=0)
                #mDynGroup.dynMode = 2
            
                for mTar in ml_targetDynParents:
                    mDynGroup.addDynParent(mTar)
                mDynGroup.rebuild()            
         
                pass
        
        
        #...rigjoints =================================================================================================
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
                
                mDynGroup = cgmRigMeta.cgmDynParentGroup(dynChild=mObj.mNode,dynMode=0)
                
                for mTar in ml_targetDynParents:
                    mDynGroup.addDynParent(mTar)
                
                mDynGroup.rebuild()
                
                #mDynGroup.dynFollow.p_parent = mRoot
        
        
        #...fk controls ============================================================================================
        log.debug("|{0}| >>  FK...".format(_str_func))                
        ml_fkJoints = self.mRigNull.msgList_get('fkJoints')
        
        for i,mObj in enumerate(ml_fkJoints):
            if i:
                break
            log.debug("|{0}| >>  FK: {1}".format(_str_func,mObj))                        
            ml_targetDynParents = copy.copy(ml_baseDynParents)
            ml_targetDynParents.append(self.md_dynTargetsParent['attachDriver'])
            
            mParent = mObj.masterGroup.getParent(asMeta=True)
            if not mParent.hasAttr('cgmAlias'):
                mParent.addAttr('cgmAlias','{0}_base'.format(mObj.p_nameBase))
            
            if i == 0:
                ml_targetDynParents.append(mParent)
                _mode = 2            
            else:
                ml_targetDynParents.insert(0,mParent)
                _mode = 1
                
            mParentBank = False
            if i == 0:
                mParentBank = mRigNull.getMessageAsMeta('bankParentFKDriver')
                if mParentBank:
                    ml_targetDynParents.insert(0,mParentBank)
                
            #if str_rigSetup not in ['digit']:
            ml_targetDynParents.extend(ml_endDynParents)
            ml_targetDynParents.extend(mObj.msgList_get('spacePivots',asMeta = True))
    
            mDynGroup = cgmRigMeta.cgmDynParentGroup(dynChild=mObj.mNode, dynMode=_mode)# dynParents=ml_targetDynParents)
            #mDynGroup.dynMode = 2
        
            for mTar in ml_targetDynParents:
                mDynGroup.addDynParent(mTar)
            mDynGroup.rebuild()
            
            if i == 0:
                mDynGroup.dynFollow.p_parent = mRoot
                if self.b_lever and not mParentBank:
                    #_attachPoint = mBlock.getEnumValueString('attachPoint')
                    #_idx = ml_targetDynParents.index( self.md_dynTargetsParent.get(_attachPoint))
                    ATTR.set_default(mObj.mNode,'orientTo',2)
            
            log.debug("|{0}| >>  FK targets: {1}...".format(_str_func,mObj))
            pprint.pprint(ml_targetDynParents)                
            log.debug(cgmGEN._str_subLine)    
        
    
        
        
        #Lock and hide =================================================================================
        log.debug("|{0}| >> lock and hide..".format(_str_func))
        ml_controls = mRigNull.msgList_get('controlsAll')
        
        BUILDUTILS.controls_lockDown(ml_controls)
        """
        for mCtrl in ml_controls:
            if mCtrl.hasAttr('radius'):
                ATTR.set_hidden(mCtrl.mNode,'radius',True)
            
            for link in 'masterGroup','dynParentGroup','aimGroup','worldOrient':
                if mCtrl.getMessage(link):
                    mCtrl.getMessageAsMeta(link).dagLock(True)"""
        
        if not mBlock.scaleSetup:
            log.debug("|{0}| >> No scale".format(_str_func))
            ml_controlsToLock = copy.copy(ml_controls)
            if self.b_squashSetup:
                ml_handles = self.mRigNull.msgList_get('handleJoints')
                for mHandle in ml_handles:
                    ml_controlsToLock.remove(mHandle)
                for i in self.md_roll.keys():
                    mControlMid = mRigNull.getMessageAsMeta('controlSegMidIK_{0}'.format(i))
                    if mControlMid:
                        ml_controlsToLock.remove(mControlMid)
                    
                    
            for mCtrl in ml_controlsToLock:
                if mCtrl == mSettings:
                    continue
                ATTR.set_standardFlags(mCtrl.mNode, ['scale'])
                
        for mJnt in ml_blendJoints:
            mJnt.dagLock(True)
            
        self.mDeformNull.dagLock(True)
                
        #Defaults/settings =================================================================================
        log.debug("|{0}| >> Settings...".format(_str_func))
        mSettings.visRoot = 0
        mSettings.visDirect = 0
        
        ml_handleJoints = mRigNull.msgList_get('handleJoints')
        if ml_handleJoints:
            ATTR.set_default(ml_handleJoints[0].mNode, 'stable_0', 1.0)
            ml_handleJoints[0].stable_0 = 1.0
            
        if str_blockProfile in ['leg'] or str_ikEnd in ['pad','foot']:
            log.debug("|{0}| >> 'leg' setup...".format(_str_func))
            
            if mSettings.hasAttr('FKIK'):
                ATTR.set_default(mSettings.mNode, 'FKIK', 1.0)
                mSettings.FKIK = 1.0
                
                mControlIK.resetAttrs()
                
        if self.b_lever:
            ml_fkJoints[0].resetAttrs()
            
            
        if mBlock.buildLeverEnd:
            log.debug("|{0}| >> Quad setup...".format(_str_func))            
            mIKBallRotationControl = mRigNull.getMessageAsMeta('controlBallRotation')
            ATTR.set_default(mControlIK.mNode, 'extendIK', 1.0)
            mControlIK.extendIK = 1.0        
           
        #Close out ===============================================================================================
        mRigNull.version = self.d_block['buildVersion']
        mBlock.blockState = 'rig'
        mBlock.UTILS.set_blockNullTemplateState(mBlock)
        self.UTILS.rigNodes_store(self)
        
        #cgmGEN.func_snapShot(vars())
        return
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err,localDat=vars())        

@cgmGEN.Timer
def rigDelete2(self):
    try:
        _str_func = 'rigDelete'    
        self.template = False
        self.noTransTemplateNull.template=True
        
        ml_controls = mRigNull.msgList_get('controlsAll')
        for mCtrl in ml_controls:
            log.debug("|{0}| >> Processing: {1}".format(_str_func,mCtrl))
            mDynGroup = mCtrl.getMessageAsmeta('dynParentGroup')
            if mDynGroup:
                mDynGroup.doPurge()
            
        
                ml_spacePivots = mCtrl.msgList_get('spacePivots')
                if ml_spacePivots:
                    for mObj in ml_spacePivots:
                        log.debug("|{0}| >> SpacePivot: {1}".format(_str_func,mObj)) 
                
        for link in ['constraintGroup','constrainGroup','masterGroup']:
            mGroup = mObj.getMessageAsMeta(link)
            if mGroup:
                mGroup.delete()
                break
                
        
        return True
    except Exception,err:
        raise cgmGEN.cgmExceptCB(Exception,err,msg=vars())

    

def build_proxyMesh(self, forceNew = True, puppetMeshMode = False):
    """
    Build our proxyMesh
    """
    try:
        _short = self.d_block['shortName']
        _str_func = '[{0}] > build_proxyMesh'.format(_short)
        log.debug("|{0}| >> ...".format(_str_func)+cgmGEN._str_hardBreak)
      
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
        
        #>> If proxyMesh there, delete -------------------------------------------------------------------------- 
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
            
        #Figure out our rig joints --------------------------------------------------------
        _str_rigSetup = mBlock.getEnumValueString('rigSetup')
        _str_ikEnd = mBlock.getEnumValueString('ikEnd')
        
        mToe = False
        mBall = False
        int_handleEndIdx = -1
        mEnd = False
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
                mEnd = ml_rigJoints.pop(-1)
        else:
            mEnd = ml_rigJoints[-1]
                
        
        log.debug("|{0}| >> Handles Targets: {1}".format(_str_func,ml_rigJoints))            
        log.debug("|{0}| >> End idx: {1} | {2}".format(_str_func,int_handleEndIdx,
                                                       ml_rigJoints[int_handleEndIdx]))                
            
        # Create ---------------------------------------------------------------------------
        _extendToStart = True
        _blockProfile = mBlock.blockProfile
        _ballBase = False
        _ballMode = False
        if mBlock.proxyGeoRoot:
            _ballMode = mBlock.getEnumValueString('proxyGeoRoot')
            _ballBase=True
            
        if mBlock.buildLeverBase and not mBlock.hasLeverJoint:
            _extendToStart = False
            
        """
        _ballMode = 'sdf'#loft
        _ballBase = True
        if _blockProfile in ['finger','thumb']:
            _ballMode = 'loft'
        if _blockProfile in ['wingBase']:
            _ballBase = False"""
            
        ml_segProxy = cgmMeta.validateObjListArg(self.atBuilderUtils('mesh_proxyCreate',
                                                                     ml_rigJoints,
                                                                     ballBase = _ballBase,
                                                                     ballMode = _ballMode,
                                                                     reverseNormal=mBlock.loftReverseNormal,
                                                                     extendToStart=_extendToStart),
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
            elif ml_templateHandles[-1].getMessage('pivotHelper') and mBlock.blockProfile not in ['arm']:
                if mEnd:ml_rigJoints.append(mEnd)#...add this back
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
                l_targets.reverse()
                
                _mesh = BUILDUTILS.create_loftMesh(l_targets, name="{0}".format('foot'),merge=False,
                                                   degree=1,divisions=3)
                
                _l_combine = []
                """
                for i,crv in enumerate([l_targets[0],l_targets[-1]]):
                    _res = mc.planarSrf(crv,po=1,ch=True,d=3,ko=0, tol=.01,rn=0)
                    log.debug(_res)
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
                """
                
                mBaseCrv.delete()
                if mShape2:mShape2.delete()
                
                mMesh = cgmMeta.validateObjArg(_mesh)
                
                #if self.d_module['direction'].lower() in ['left']:
                    #log.debug("|{0}| >> FLIP... ".format(_str_func))                        
                    #mc.polyNormal(_mesh, normalMode = 0, userNormalMode=1,ch=0)
                    
                    #mc.polyNormal(_mesh,nm=0)
                    #mc.polySetToFaceNormal(_mesh,setUserNormal = True)            
                
                
                #...cut it up
                if mBall:
                    mHeelMesh = mMesh.doDuplicate(po=False)
                    mBallMesh = mMesh.doDuplicate(po=False)
                    
                    mc.polyCut(mBallMesh.getShapes()[0],
                               ch=0, pc=mBall.p_position,
                               ro=mBall.p_orient, deleteFaces=True)
                    mc.polyCloseBorder(mBallMesh.mNode)
                    
                    mBallLoc = mBall.doLoc()
                    mc.rotate(0, 180, 0, mBallLoc.mNode, r=True, os=True, fo=True)
                    mc.polyCut(mHeelMesh.getShapes()[0],
                               ch=0, pc=mBall.p_position,
                               ro=mBallLoc.p_orient, deleteFaces=True)
                    mc.polyCloseBorder(mHeelMesh.mNode)
                    mBallLoc.delete()
    
                    #Add a ankleball ------------------------------------------------------------------------
                    _target = ml_templateHandles[-1].mNode
                    _bb_size = POS.get_bb_size(_target,True,'maxFill')#SNAPCALLS.get_axisBox_size(_target)
                    _size = [_bb_size[0],_bb_size[1],MATH.average(_bb_size)]
                    _size = [v*.8 for v in _size]
                    _sphere = mc.polySphere(axis = [1,0,0], radius = 1, subdivisionsX = 10, subdivisionsY = 10)
                    TRANS.scale_to_boundingBox(_sphere[0], _size)
                
                    SNAP.go(_sphere[0],_target)
                    #TRANS.orient_set(_sphere[0], ml_targets[i].p_orient)
                    #SNAP.go(_sphere[0],ml_targets[i].mNode,False,True)
                    _mesh = mc.polyUnite([mHeelMesh.mNode,_sphere[0]], ch=False )[0]
                    
                    mMeshHeel = cgmMeta.validateObjArg(_mesh)
                    ml_segProxy.append(mMeshHeel)
                    
                    
                    #toe -----------------------------------------------------------------------------------
                    if mToe:
                        mToeMesh = mBallMesh.doDuplicate(po=False)
                        
                        mToeLoc = mToe.doLoc()
                        mc.rotate(0, 180, 0, mToeLoc.mNode, r=True, os=True, fo=True)
                        
                        mc.polyCut(mBallMesh.getShapes()[0],
                                   ch=0, pc=mToe.p_position,
                                   ro=mToeLoc.p_orient, deleteFaces=True)
                        mc.polyCloseBorder(mBallMesh.mNode)
                        
    
                        mc.polyCut(mToeMesh.getShapes()[0],
                                   ch=0, pc=mToe.p_position,
                                   ro=mToe.p_orient, deleteFaces=True)
                        mc.polyCloseBorder(mToeMesh.mNode)                    
                        mToeLoc.delete()
                        
                        
                        ml_segProxy.append(mBallMesh)
                        ml_rigJoints.append(mBall)
                        ml_segProxy.append(mToeMesh)
                        ml_rigJoints.append(mToe)
                    else:
                        #ball -----------------------------------------------------------------------------------
                        log.debug("|{0}| >> ball... ".format(_str_func))            
                        ml_segProxy.append(mBallMesh)
                        ml_rigJoints.append(mBall)                    
                        
                    #mMesh.p_parent=False
                    mMesh.delete()
                else: 
                    _mesh = mc.polyUnite([mMesh.mNode,ml_segProxy[-1].mNode], ch=False )[0]
                    mMesh = cgmMeta.validateObjArg(_mesh)                
                    ml_segProxy[-1] = mMesh
                    
        
        if directProxy:
            log.debug("|{0}| >> directProxy... ".format(_str_func))
            _settings = self.mRigNull.settings.mNode
            
        if puppetMeshMode:
            log.debug("|{0}| >> puppetMesh setup... ".format(_str_func))
            ml_moduleJoints = mRigNull.msgList_get('moduleJoints')
            
            for i,mGeo in enumerate(ml_segProxy):
                log.debug("{0} : {1}".format(mGeo, ml_moduleJoints[i]))
                mGeo.parent = ml_moduleJoints[i]
                mGeo.doStore('cgmName',self.d_module['partName'])
                mGeo.addAttr('cgmIterator',i+1)
                mGeo.addAttr('cgmType','proxyPuppetGeo')
                mGeo.doName()        
            
            mRigNull.msgList_connect('puppetProxyMesh', ml_segProxy)
            return ml_segProxy
    
        for i,mGeo in enumerate(ml_segProxy):
            log.debug("{0} : {1}".format(mGeo, ml_rigJoints[i]))
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
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err,localDat=vars())        


@cgmGEN.Timer
def switchMode(self,mode = 'fkOn'):
    try:
        _str_func = 'switchMode'
        log.debug("|{0}| >> mode: {1} ".format(_str_func,mode)+ '-'*80)
        log.debug("{0}".format(self))
        
        _mode = mode.lower()
        
        if _mode not in ['iksnap','iksnapall']:#If we don't 
            log.debug("|{0}| >> Standard call. Passing back...".format(_str_func))
            return self.atUtils('switchMode',mode,True)
        
        log.debug("|{0}| >> Special call. Processing...".format(_str_func))
        
        mRigNull = self.rigNull
        mSettings = mRigNull.settings
        
        if not mRigNull.getMessage('controlIK'):
            return log.debug("|{0}| >> No IK mode detected ".format(_str_func))
        if MATH.is_float_equivalent(mSettings.FKIK,1.0):
            return log.debug("|{0}| >> Already in IK mode ".format(_str_func))
        
        mControlIK = mRigNull.controlIK
        mControlMid = False
        mControlIKBase = False
        
        ml_ikJoints = mRigNull.msgList_get('ikJoints')
        ml_blendJoints = mRigNull.msgList_get('blendJoints')
        
        #Find our ball and toe ===========================================================
        mBall = False
        mToe = False
        _str_orient = 'zyx'
        
        for mJnt in ml_ikJoints:
            _cgmName = mJnt.getMayaAttr('cgmName') 
            if _cgmName == 'ball':
                mBall = mJnt
                log.debug("|{0}| >> mBall found: {1}".format(_str_func,mBall))
                mBallBlend = mBall.getMessage('blendJoint',asMeta=1)[0]
                log.debug("|{0}| >> mBallBlend found: {1}".format(_str_func,mBallBlend))
                
                d_ball = {'attrs':['x','y','z'],
                          'drivers':['ballLift','ballSide','ballTwist'],
                          'match':[v for v in mBallBlend.rotate]}
                            
            elif _cgmName == 'toe':
                mToe = mJnt
                log.debug("|{0}| >> mToe found: {1}".format(_str_func,mToe))
                mToeBlend = mToe.getMessage('blendJoint',asMeta=1)[0]
                log.debug("|{0}| >> mToeBlend found: {1}".format(_str_func,mToeBlend))
                
                d_toe = {'attrs':['x','y','z'],
                         'drivers':['toeLift','toeSide','toeTwist'],
                         'match':[v for v in mToeBlend.rotate]}            
                
        ml_controls = [mControlIK]
        md_controls = {}        
        md_locs = {}
        if mRigNull.getMessage('controlIKBase'):
            mControlIKBase = mRigNull.controlIKBase
            ml_controls.append(mControlIKBase)
        if mRigNull.getMessage('controlIKMid'):
            mControlMid = mRigNull.controlIKMid
            ml_controls.append(mControlMid)
            #mid_point = IK.get_midIK_basePos(ml_blendJoints,'y+', markPos=True)
    
        md_datPostCompare = {}
        for i,mObj in enumerate (ml_blendJoints):
            md_datPostCompare[i] = {}
            md_datPostCompare[i]['pos'] = mObj.p_position
            md_datPostCompare[i]['orient'] = mObj.p_orient
    
        #IKsnapAll ========================================================================
        if _mode == 'iksnapall':
            log.debug("|{0}| >> ik snap all prep...".format(_str_func))
            mSettings.visDirect=True
            ml_rigLocs = []
            ml_rigJoints = mRigNull.msgList_get('rigJoints')
            for i,mObj in enumerate(ml_rigJoints):
                ml_rigLocs.append( mObj.doLoc(fastMode = True) )
                
            ml_handleLocs = []
            ml_handleJoints = mRigNull.msgList_get('handleJoints')
            for i,mObj in enumerate(ml_handleJoints):
                ml_handleLocs.append( mObj.doLoc(fastMode = True) )        
    
        #Main IK control =====================================================================
    
        #dat we need
        #We need to store the blendjoint target for the ik control or loc it
        for i,mCtrl in enumerate(ml_controls):
            if mCtrl.getMessage('switchTarget'):
                mCtrl.resetAttrs(transformsOnly = True)
                md_locs[i] = mCtrl.switchTarget.doLoc(fastMode=True)
                md_controls[i] = mCtrl
            else:
                raise ValueError,"mCtrl: {0}  missing switchTarget".format(mCtrl)
            
    
        mSettings.FKIK = 1
    
        for i,mLoc in md_locs.iteritems():
            SNAP.go(md_controls[i].mNode,mLoc.mNode)
            mLoc.delete()
            
        #if mControlMid:
            #mControlMid.p_position = mid_point
            
            
        if mBall:
            for i in range(3):
                _a = d_ball['attrs'][i]
                _driver = d_ball['drivers'][i]
                _match = d_ball['match'][i]
                CORERIGGEN.matchValue_iterator(drivenObj = mBallBlend.mNode,
                                               drivenAttr = "r{0}".format(_a),
                                               driverAttr = "{0}.{1}".format(mControlIK.mNode, _driver),
                                               matchValue = _match,
                                               maxIterations=40)
        if mToe:
            for i in range(3):
                _a = d_toe['attrs'][i]
                _driver = d_toe['drivers'][i]
                _match = d_toe['match'][i]
                CORERIGGEN.matchValue_iterator(drivenObj = mToeBlend.mNode,
                                               drivenAttr = "r{0}".format(_a),
                                               driverAttr = "{0}.{1}".format(mControlIK.mNode, _driver),
                                               matchValue = _match,
                                               maxIterations=40)
    
        #IKsnapAll close========================================================================
        if _mode == 'iksnapall':
            log.debug("|{0}| >> ik snap all end...".format(_str_func))
            
            
            for ii in range(2):
                for i,mObj in enumerate(ml_handleJoints):
                    SNAP.go(mObj.mNode,ml_handleLocs[i].mNode)
                    if ii==1:
                        ml_handleLocs[i].delete()
    
            for i,mObj in enumerate(ml_rigJoints):
                SNAP.go(mObj.mNode,ml_rigLocs[i].mNode)
                ml_rigLocs[i].delete()
            log.warning("mode: {0} | Direct controls vis turned on for mode.".format(_mode))
            
        #Pose compare =========================================================================
        for i,v in md_datPostCompare.iteritems():
            mBlend = ml_blendJoints[i]
            dNew = {'pos':mBlend.p_position, 'orient':mBlend.p_orient}
    
            if DIST.get_distance_between_points(md_datPostCompare[i]['pos'], dNew['pos']) > .05:
                log.warning("|{0}| >> [{1}] pos blend dat off... {2}".format(_str_func,i,mBlend))
                log.warning("|{0}| >> base: {1}.".format(_str_func,md_datPostCompare[i]['pos']))
                log.warning("|{0}| >> base: {1}.".format(_str_func,dNew['pos']))
    
            if not MATH.is_vector_equivalent(md_datPostCompare[i]['orient'], dNew['orient'], places=2):
                log.warning("|{0}| >> [{1}] orient blend dat off... {2}".format(_str_func,i,mBlend))
                log.warning("|{0}| >> base: {1}.".format(_str_func,md_datPostCompare[i]['orient']))
                log.warning("|{0}| >> base: {1}.".format(_str_func,dNew['orient']))
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err,localDat=vars())        
    
def snapBall(self,driven = 'L_ball_blend_frame',
             target = 'L_ball_blend_frame_fromTarget_loc',
             handle = 'L_ankle_ik_anim'):
    try:
        _str_func = 'snapBall'
        log.debug("|{0}| >>".format(_str_func)+ '-'*80)
        log.debug("{0}".format(self))
        
        #Get data -----------------------------------------------------------
        mDriven = cgmMeta.validateObjArg(driven)
        mTarget = cgmMeta.validateObjArg(target)
        mHandle = cgmMeta.validateObjArg(handle)
        
        d_targetDat = {'v':[]}
        
        d_drivers = {'x':'ballLift',
                     'y':'ballSide',
                     'z':'ballTwist'}
        
        v_targets = [-34.242,0,0]#...store rotation before we turn off fk
                       
        #for a in 'xyz':
            #d_targetDat['v'].append(MATH.get_obj_vector(target, "{0}+".format(a)))
        
        pprint.pprint(vars())
        
        _d  = {'matchObj' : None,
               'matchAttr' : None,
               'drivenObj' : 'L_ball_blend_frame',
               'drivenAttr' : 'rx',
               'driverAttr' : 'L_ankle_ik_anim.ballLift', 
               'minIn' : -179, 'maxIn' : 179, 'maxIterations' : 40, 'matchValue' : -63.858}
        CORERIGGEN.matchValue_iterator(**_d)    
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err,localDat=vars())        


def get_handleIndices(self):
    try:
        _str_func = 'get_handleIndices'
        log.debug("|{0}| >>  {1}".format(_str_func,self)+ '-'*80)
        
        idx_start = 0
        idx_end = -1
        
        if self.getMessage('templateLeverHandle'):
            log.debug("|{0}| >> lever base".format(_str_func))
            idx_start +=1
    
        str_ikEnd = ATTR.get_enumValueString(self.mNode,'ikEnd')
        log.debug("|{0}| >> IK End: {1}".format(_str_func,format(str_ikEnd)))
        

        if str_ikEnd in ['foot']:
            if self.hasBallJoint:
                idx_end -=1
            if self.hasEndJoint:
                idx_end -=1
        elif str_ikEnd in ['tipEnd','tipBase','tipCombo']:
            log.debug("|{0}| >> tip setup...".format(_str_func))        
            if str_ikEnd == 'tipEnd':
                self.b_ikNeedEnd = True
                log.debug("|{0}| >> Need IK end joint".format(_str_func))
            elif str_ikEnd == 'tipBase':
                idx_end -=1
                
        #if self.buildLeverEnd:
            #idx_end -=1
                
        return idx_start,idx_end
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err,localDat=vars())        












