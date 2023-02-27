"""
------------------------------------------
cgm.core.mrs.blocks.simple.torso
Author: Josh Burton
email: cgmonks.info@gmail.com

Website : https://github.com/jjburton/cgmTools/wiki
------------------------------------------

================================================================
"""
__MAYALOCAL = 'SEGMENT'

# From Python =============================================================
import copy
import re
import pprint
import time
import os

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
import logging
import importlib
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

log.debug("load...")
# From Maya =============================================================
import maya.cmds as mc

# From Red9 =============================================================
#from Red9.core import Red9_Meta as r9Meta
#r9Meta.cleanCache()#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< TEMP!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

import cgm.core.cgm_General as cgmGEN

#from cgm.core.rigger import ModuleShapeCaster as mShapeCast

#import cgm.core.cgmPy.os_Utils as cgmOS
import cgm.core.cgmPy.path_Utils as cgmPATH
import cgm.core.mrs.assets as MRSASSETS
path_assets = cgmPATH.Path(MRSASSETS.__file__).up().asFriendly()

import cgm.core.mrs.lib.ModuleControlFactory as MODULECONTROL
import cgm.core.lib.math_utils as MATH
import cgm.core.lib.transform_utils as TRANS
import cgm.core.lib.distance_utils as DIST
import cgm.core.lib.attribute_utils as ATTR
import cgm.core.tools.lib.snap_calls as SNAPCALLS
import cgm.core.classes.NodeFactory as NODEFACTORY
from cgm.core import cgm_RigMeta as cgmRigMeta
#import cgm.core.lib.list_utils as LISTS
import cgm.core.lib.nameTools as NAMETOOLS
#import cgm.core.lib.name_utils as CORENAMES
from cgm.core.lib import string_utils as CORESTRING
#import cgm.core.rig.create_utils as RIGCREATE
import cgm.core.mrs.lib.blockShapes_utils as BLOCKSHAPES

#Prerig handle making. refactor to blockUtils
import cgm.core.lib.snap_utils as SNAP
#import cgm.core.lib.rayCaster as RAYS
import cgm.core.lib.rigging_utils as CORERIG
import cgm.core.lib.curve_Utils as CURVES
import cgm.core.rig.constraint_utils as RIGCONSTRAINT
import cgm.core.lib.constraint_utils as CONSTRAINT
import cgm.core.lib.position_utils as POS
import cgm.core.rig.joint_utils as JOINT
import cgm.core.rig.ik_utils as IK
import cgm.core.mrs.lib.block_utils as BLOCKUTILS
import cgm.core.mrs.lib.builder_utils as BUILDUTILS
import cgm.core.cgm_RigMeta as cgmRIGMETA
#import cgm.core.rig.skin_utils as CORESKIN
import cgm.core.mrs.lib.rigShapes_utils as RIGSHAPES
import cgm.core.mrs.lib.rigFrame_utils as RIGFRAME
import cgm.core.mrs.lib.shared_dat as BLOCKSHARE
#from cgm.core.lib import locator_utils as LOC
import cgm.core.mrs.lib.post_utils as MRSPOST
import cgm.core.mrs.lib.blockShapes_utils as BLOCKSHAPES

#for m in RIGSHAPES,CURVES,BUILDUTILS,RIGCONSTRAINT,MODULECONTROL,RIGFRAME:
#    reload(m)
    
# From cgm ==============================================================
from cgm.core import cgm_Meta as cgmMeta

#=============================================================================================================
#>> Block Settings
#=============================================================================================================
__version__ = cgmGEN.__RELEASESTRING
__autoForm__ = False
__dimensions = [15.2, 23.2, 19.7]#...cm
__menuVisible__ = True
__sizeMode__ = 'castNames'

#__baseSize__ = 1,1,10

__l_rigBuildOrder__ = ['rig_dataBuffer',
                       'rig_skeleton',
                       'rig_shapes',
                       'rig_controls',
                       'rig_frame',
                       'rig_segments',
                       'rig_cleanUp']


d_wiring_skeleton = {'msgLists':['moduleJoints','skinJoints']}
d_wiring_prerig = {'msgLinks':['moduleTarget','prerigNull','noTransPrerigNull','prerigStuff'],
                   'msgLists':['prerigHandles'],
                   'optional':['prerigStuff']}
d_wiring_form = {'msgLinks':['formNull','prerigLoftMesh','noTransFormNull','formStuff'],
                 'msgLists':['formHandles'],
                 'optional':['formStuff']}

_d_attrStateOn = {0:[],
                  1:[],
                  2:[],
                  3:[],
                  4:[]}

_d_attrStateOff = {0:[],
                   1:[],
                   2:[],
                   3:[],
                   4:[]}

d_attrStateMask = {'define':['baseSizeX','baseSizeY','baseSizeZ'],
                   'form':['formEndAim','loftShape',
                           'loftShapeEnd','loftShapeStart'],
                   'prerig':[],
                   'skeleton':['numJoints'],
                   'squashStretch':['squashSkipAim','segmentStretchBy'],
                   'space':['ikMidDynParentMode','ikMidDynScaleMode'],
                   'rig':['segmentType','special_swim','ikEndShape','ikSplineAimEnd','ikSplineTwistEndConnect','ikSplineExtendEnd','ikMidSetup','ikMidControlNum','ikSplineTwistAxis',
                          'ribbonExtendEnds','ribbonAttachEndsToInfluence',
                          'ikBaseExtend','ikEndExtend','ikEndLever',]}

l_createUI_attrs = ['attachPoint','attachIndex','nameIter','numControls','numJoints',
                    'addCog','addPivot','numSubShapers','segmentType',
                    'loftSetup','scaleSetup','loftShape',
                    'numControls',
                    'numSubShapers',
                    'ikSetup','segmentStretchBy',
                    'ribbonExtendEnds','ribbonAttachEndsToInfluence',
                    'root_dynParentMode',
                    'root_dynParentScaleMode','squashSkipAim',
                    'dynParentMode','dynParentScaleMode',
                    ]
#>>>Profiles =====================================================================================================
d_build_profiles = {
    'unityLow':{'default':{'numJoints':3,
                           'numControls':3},
                   },
    'unityMed':{'default':{'numJoints':6,
                          'numControls':4},
               'spineUp':{'numJoints':4,
                          'numControls':4},
               'spineFwd':{'numJoints':4,
                          'numControls':4},               
               'earUp':{'numJoints':4,
                        'numControls':4}},
    'unityToon':{'default':{'squashMeasure':'arcLength',
                            'squash':'simple',
                            'scaleSetup':True,
                            'squashSkipAim':False,
                            }},
    'unityHigh':{'default':{'numJoints':4,
                            'numControls':4},
                 'spine':{'numJoints':6,
                          'numControls':4}},
    
    'feature':{'default':{'numJoints':9,
                          'numControls':5}}}

d_block_profiles = {
    'simple':{'numShapers':2,
              'numSubShapers':3,
              'addCog':False,
              'loftSetup':'default',
              'loftShape':'square',
              'ikSetup':'ribbon',
              'ikBase':'cube',
              'ikEnd':'helper',
              'ikEndShape':'cube',
              'cgmName':'simple',
              'nameIter':'seg',
              'numControls':4,
              'numJoints':6,
              'nameList':['start','end'],
              'squash':'both',
              'squashExtraControl':True,
              'squashMeasure':'pointDist',
              'squashFactorMax':1.0,
              'squashFactorMin':0,
              'ribbonAim':'stable',
              #'shapersAim':'toEnd',
              'settingsPlace':'end',
              'baseAim':[0,1,0],
              'shapeDirection':'y+',
              #'baseUp':[0,0,-1],
              'baseDat':{'rp':[0,0,-1],'up':[0,0,-1],'lever':[0,-1,0]},
              'baseSize':[30,15,76]},
    'dangleBit':
    {'addCog': False,
    'addPivot': False,
    'attachIndex': 0,
    'attachPoint': 'closest',
    'castVector': 'up',
    'cgmName': 'dangle',
    'ikBase': 'cube',
    'ikEnd':'helper',    
    'ikEndShape': 'cube',
    'ikOrientToWorld': True,
    'ikSetup': 'ribbon',
    'loftList_0': 'circle',
    'loftList_1': 'circle',
    'loftList_2': 'circle',
    'loftSetup': 'default',
    'loftShape': 'circle',
    'nameList':['dangleStart','dangleEnd'],
    'nameList_0': 'dangleStart',
    'nameList_1': 'dangleEnd',
    'numControls': 3,
    'numJoints': 3,
    'numShapers': 3,
    'numSpacePivots': 2,
    'numSubShapers': 3,
    'numSubShapers_0': 3,
    'numSubShapers_1': 3,
    'parentToDriver': True,
    'proxyDirect': True,
    'proxyGeoRoot': 'loft',
    'ribbonAim': 'stable',
    'ribbonConnectBy': 'constraint',
    'ribbonParam': 'blend',
    'scaleSetup': True,
    'ikMidSetup': 'prntConstraint',
    'segmentType': 'parent',
    'settingsDirection': 'up',
    'settingsPlace': 'end',
    'shapeDirection': 'y+',
    'shapersAim': 'toEnd',
    'spaceSwitch_direct': False,
    'spaceSwitch_fk': False,
    'special_swim': 'none',
    'squash': 'simple',
    'squashExtraControl': True,
    'squashFactorMax': 1.0,
    'squashFactorMin': 0.0,
    'squashMeasure': 'arcLength'},
    'tailFin':
    {'addCog': False,
     'addPivot': False,
     'attachIndex': 0,
     'attachPoint': 'closest',
     'castVector': 'up',
     'cgmName': 'tail_fin',
     'ikBase': 'cube',
     'ikEnd':'helper',     
     'ikEndShape': 'cube',
     'ikOrientToWorld': True,
     'ikSetup': 'spline',
     'loftList_0': 'circle',
     'loftList_1': 'circle',
     'loftList_2': 'circle',
     'loftSetup': 'default',
     'loftShape': 'circle',
     'nameList_0': 'finStart',
     'nameList_1': 'finEnd',
     'numControls': 3,
     'numJoints': 3,
     'numShapers': 3,
     'numSpacePivots': 2,
     'numSubShapers': 3,
     'numSubShapers_0': 3,
     'numSubShapers_1': 3,
     'parentToDriver': True,
     'proxyDirect': True,
     'proxyGeoRoot': 'loft',
     'ribbonAim': 'stable',
     'ribbonConnectBy': 'constraint',
     'ribbonParam': 'blend',
     'scaleSetup': True,
     'ikMidSetup': 'prntConstraint',
     'segmentType': 'parent',
     'settingsDirection': 'up',
     'settingsPlace': 'end',
     'shapeDirection': 'y+',
     'shapersAim': 'toEnd',
     'spaceSwitch_direct': False,
     'spaceSwitch_fk': False,
     'special_swim': 'none',
     'squash': 'simple',
     'squashExtraControl': True,
     'squashFactorMax': 1.0,
     'squashFactorMin': 0.0,
     'squashMeasure': 'arcLength'},
    'whisker':
    {'addCog': False,
     'addPivot': False,
     'attachIndex': 0,
     'attachPoint': 'closest',
     'castVector': 'up',
     'cgmName': 'whisker',
     'ikBase': 'cube',
     'ikEnd': 'tipEnd',
     'ikOrientToWorld': True,
     'ikSetup': 'ribbon',
     'jointRadius': 1.0,
     'loftList_0': 'wideDown',
     'loftList_1': 'squircleDiamond',
     'loftList_2': 'squircleDiamond',
     'loftList_3': 'circle',
     'loftSetup': 'loftList',
     'loftShape': 'wideDown',
     'nameList_0': 'base',
     'nameList_1': 'tip',
     'numControls': 3,
     'numJoints': 3,
     'numShapers': 4,
     'numSpacePivots': 2,
     'numSubShapers': 0,
     'numSubShapers_0': 0,
     'numSubShapers_1': 0,
     'numSubShapers_2': 0,
     'parentToDriver': False,
     'proxyDirect': True,
     'proxyGeoRoot': 'loft',
     'ribbonAim': 'stable',
     'ribbonConnectBy': 'constraint',
     'ribbonParam': 'blend',
     'scaleSetup': True,
     'ikMidSetup': 'prntConstraint',
     'segmentType': 'parent',
     'settingsDirection': 'up',
     'settingsPlace': 'end',
     'shapeDirection': 'z+',
     'shapersAim': 'chain',
     'spaceSwitch_direct': False,
     'spaceSwitch_fk': False,
     'special_swim': 'none',
     'squash': 'none',
     'squashExtraControl': True,
     'squashFactorMax': 1.0,
     'squashFactorMin': 0.25,
     'squashMeasure': 'arcLength'},
    
    'tailCat':
    {'addCog': False,
     'addPivot': False,
     'attachIndex': 0,
     'attachPoint': 'closest',
     'castVector': 'up',
     'cgmName': 'tail',
     'ikBase': 'simple',
     'ikEnd': 'tipEnd',
     'ikOrientToWorld': True,
     'ikSetup': 'spline',
     'loftList_0': 'circle',
     'loftList_1': 'circle',
     'loftList_2': 'circle',
     'loftSetup': 'default',
     'loftShape': 'circle',
     'nameList_0': 'tailBase',
     'nameList_1': 'tailTip',
     'numControls': 5,
     'numJoints': 5,
     'numShapers': 5,
     'numSpacePivots': 2,
     'numSubShapers': 1,
     'numSubShapers_0': 1,
     'numSubShapers_1': 1,
     'numSubShapers_2': 1,
     'numSubShapers_3': 1,
     'numSubShapers_4': 1,
     'numSubShapers_5': 1,
     'parentToDriver': False,
     'proxyDirect': False,
     'proxyGeoRoot': 'loft',
     'ribbonAim': 'stable',
     'ribbonConnectBy': 'constraint',
     'ribbonParam': 'blend',
     'scaleSetup': True,
     'ikMidSetup': 'prntConstraint',
     'segmentType': 'ribbon',
     'settingsDirection': 'up',
     'settingsPlace': 'end',
     'shapeDirection': 'z-',
     'shapersAim': 'chain',
     'spaceSwitch_direct': False,
     'spaceSwitch_fk': False,
     'special_swim': 'none',
     'squash': 'simple',
     'nameList':['tailStart','tailEnd'],     
     'squashExtraControl': True,
     'squashFactorMax': 1.0,
     'squashFactorMin': 1.0,
     'squashMeasure': 'arcLength'},    
    
    'earUp':{'attachPoint':'closest',
             'numShapers':2,
             'numSubShapers':3,
             'addCog':False,
             'side':'right',
             'cgmName':'ear',
             'loftShape':'wideDown',
             'loftSetup':'default',
             'ikSetup':'ribbon',
             'ikBase':'simple',
             'ikEnd':'tipEnd',
             'nameIter':'ear',
             'nameList':['earBase','earTip'],
             'squash':'both',
             'squashExtraControl':True,
             'squashMeasure':'pointDist',
             'squashFactorMax':1.0,
             'squashFactorMin':.25,
             'ribbonAim':'stable',
             'shapersAim':'chain',
             'shapeDirection':'y+',
             'proxyGeoRoot':0,
             'baseAim':[0,1,0],
             'baseUp':[0,1,0],
             'baseDat':{'rp':[0,0,-1],'up':[0,0,-1],'lever':[0,-1,0]},
             'baseSize':[10,10,20],
             },
    'headToon':{'attachPoint':'closest',
             'numShapers':3,
             'numSubShapers':4,
             'addCog':False,
             'cgmName':'head',
             'loftShape':'circle',
             'loftSetup':'default',
             'ikSetup':'ribbon',
             'ikBase':'simple',
             'ikEnd':'tipMid',
             'ikEndExtend':True,
             'nameIter':'head',
             'nameList':['headStart','headEnd'],
             'ikMidSetup':'none',
             'squash':'both',
             'squashExtraControl':True,
             'squashMeasure':'arcLength',
             'squashFactorMax':1.0,
             'squashFactorMin':1.0,
             'ribbonAim':'stable',
             'shapersAim':'chain',
             'shapeDirection':'y+',
             'baseDat':{'rp':[0,0,-1],'up':[0,0,-1],'lever':[0,-1,0]},
             'baseSize':[10,10,20],
             },       
    'earUp':{'attachPoint':'closest',
             'numShapers':2,
             'numSubShapers':3,
             'addCog':False,
             'side':'right',
             'cgmName':'ear',
             'loftShape':'wideDown',
             'loftSetup':'default',
             'ikSetup':'ribbon',
             'ikBase':'simple',
             'ikEnd':'tipEnd',
             'nameIter':'ear',
             'nameList':['earBase','earTip'],
             'squash':'both',
             'squashExtraControl':True,
             'squashMeasure':'pointDist',
             'squashFactorMax':1.0,
             'squashFactorMin':.25,
             'ribbonAim':'stable',
             'shapersAim':'chain',
             'shapeDirection':'y+',
             'proxyGeoRoot':0,
             'baseAim':[0,1,0],
             'baseUp':[0,1,0],
             'baseDat':{'rp':[0,0,-1],'up':[0,0,-1],'lever':[0,-1,0]},
             'baseSize':[10,10,20],
             },    

    'tail':{'attachPoint':'closest',
            'numShapers':5,
            'addCog':False,
            'cgmName':'tail',
            'loftShape':'wideDown',
            'loftSetup':'default',
            'ikSetup':'spline',
            'ikBase':'simple',
            'ikEnd':'tipEnd',            
            'nameIter':'tail',
            'numControls':6,
            'numJoints':8,
            'nameList':['tailBase','tailTip'],
            'squash':'both',
            'squashExtraControl':True,
            'squashMeasure':'pointDist',
            'squashFactorMax':1.0,
            'squashFactorMin':.25,
            'ribbonAim':'stable',
            'shapersAim':'chain',
            'settingsPlace':'end',
            'segmentType':'spline',
            'baseAim':[0,0,-1],
            'baseUp':[0,1,0],
            'shapeDirection':'z-',
            'baseDat':{'rp':[0,1,0],'up':[0,1,0],'lever':[0,0,1]},
            'baseSize':[14,9,76],
            },
    
    'tentacle':{'attachPoint':'closest',
                'numShapers':4,
                'addCog':False,
                'cgmName':'tentacle',
                'loftShape':'wideDown',
                'loftSetup':'loftList',
                'loftList':['wideDown','squircleDiamond','squircleDiamond','circle'],
                'ikSetup':'spline',
                'ikBase':'simple',
                'ikEnd':'tipEnd',            
                'nameIter':'tentacle',
                'numControls':6,
                'numJoints':9,
                'nameList':['base','tip'],
                'squash':'both',
                'squashExtraControl':True,
                'squashMeasure':'pointDist',
                'squashFactorMax':1.0,
                'squashFactorMin':.25,
                'ribbonAim':'stable',
                'shapersAim':'chain',
                'baseAim':[0,0,1],
                'baseUp':[0,1,0],
                'shapeDirection':'z+',                
                'settingsPlace':'end',
                'baseDat':{'rp':[0,1,0],'up':[0,1,0],'lever':[0,0,-1]},
                'baseSize':[14,9,76],
                },
    'spineSwim':{'numShapers':4,
                 'numSubShapers':2,
                 'addCog':True,
                 'loftSetup':'loftList',
                 'loftList':['wideUp','circle','wideDown','wideDown'],             
                 'loftShape':'circle',
                 'ikSetup':'ribbon',
                 'ikBase':'head',
                 'ikEnd':'tipBase',             
                 'cgmName':'spine',
                 'nameIter':'spine',
                 'nameList':['head','tail'],
                 'numControls':4,
                 'squash':'simple',
                 'squashExtraControl':True,
                 'squashMeasure':'arcLength',
                 'squashFactorMax':1.0,
                 'squashFactorMin':1.0,
                 'ribbonAim':'stable',
                 'shapersAim':'toEnd',
                 'segmentType':'ribbon',
                 'settingsPlace':'cog',
                 'shapeDirection':'z-',
                 'special_swim':'wave',
                 'numJoints':8,
                 'baseAim':[0,0,1],
                 #'baseUp':[0,0,-1],
                 'baseDat':{'rp':[0,1,0],'up':[0,1,0],'lever':[0,0,-1]},
                 'baseSize':[30,15,76]},    
    
    'spineFwd':{'numShapers':4,
             'numSubShapers':2,
             'addCog':True,
             'loftSetup':'loftList',
             'loftList':['wideUp','circle','wideDown','wideDown'],             
             'loftShape':'circle',
             'ikSetup':'ribbon',
             'ikBase':'hips',
             'ikEnd':'tipMid',             
             'cgmName':'spine',
             'nameIter':'spine',
             'nameList':['pelvis','chest'],
             'numControls':4,
             'squash':'none',
             'squashExtraControl':True,
             'squashMeasure':'arcLength',
             'squashFactorMax':1.0,
             'squashFactorMin':0,
             'ribbonAim':'stable',
             'shapersAim':'toEnd',
             'settingsPlace':'cog',
             'shapeDirection':'z+',
             'baseAim':[0,0,1],
             #'baseUp':[0,0,-1],
             'baseDat':{'rp':[0,1,0],'up':[0,1,0],'lever':[0,0,-1]},
             'baseSize':[30,15,76]},
    
    'spineUp':{'numShapers':5,
             'numSubShapers':1,
             'addCog':True,
             'loftSetup':'loftList',
             'loftList':['circle','wideUp','circle','wideUp','circle'],
             
             'loftShape':'circle',
             'ikSetup':'ribbon',
             'ikBase':'hips',
             'ikEnd':'tipMid',             
             'cgmName':'spine',
             'nameIter':'spine',
             'nameList':['pelvis','chest'],
             'numControls':4,
             'squash':'none',
             'squashExtraControl':True,
             'squashMeasure':'arcLength',
             'squashFactorMax':1.0,
             'squashFactorMin':0,
             'ribbonAim':'stable',
             'shapersAim':'toEnd',
             'settingsPlace':'cog',
             'shapeDirection':'y+',             
             'baseAim':[0,1,0],
             #'baseUp':[0,0,-1],
             'baseDat':{'rp':[0,0,-1],'up':[0,0,-1],'lever':[0,-1,0]},
             'baseSize':[30,15,76]}}


#>>>Attrs =====================================================================================================
l_attrsStandard = ['side',
                   'position',
                   'baseUp',
                   'baseAim',
                   'addCog',
                   'addPivot',
                   'castVector',
                   #'hasRootJoint',
                   'nameList',
                   'attachPoint',
                   'attachIndex',
                   'jointRadius',                   
                   'loftSides',
                   'loftDegree',
                   'loftList',
                   'loftSplit',
                   'loftShape',
                   'ikSetup',
                   'nameIter',
                   'numControls',
                   'numShapers',
                   'numJoints',
                   'ikOrientToWorld',
                   #'buildProfile',
                   'blockProfile',
                   'parentToDriver',
                   'numSpacePivots',                   
                   'scaleSetup',
                   'offsetMode',
                   'ribbonParam',
                   'proxyDirect',
                   'proxyGeoRoot',
                   'proxyHardenEdge',
                   'meshBuild',
                   'shapeDirection',
                   #'settingsPlace',
                   'spaceSwitch_direct',
                   'spaceSwitch_fk',
                   'visRotatePlane',
                   'visProximityMode',
                   'visLabels',
                   'visJointHandle',
                   'root_dynParentMode',
                   'root_dynParentScaleMode',
                   'controlOffsetMult',
                   'squashFactorMode',
                   'settingsDirection',
                   'moduleTarget']

d_attrsToMake = {'visMeasure':'bool',
                 'proxyShape':'cube:sphere:cylinder',
                 'numSubShapers':'int',
                 'squashMeasure' : 'none:arcLength:pointDist',
                 'squash' : 'none:simple:single:both',
                 'squashExtraControl' : 'bool',
                 'squashFactorMax':'float',
                 'squashFactorMin':'float',
                 'shapersAim':'toEnd:chain:orientToHandle',
                 'squashSkipAim':'bool',
                 'loftSetup':'default:loftList',
                 'special_swim':'none:wave:sine',
                 'ribbonAim': 'none:stable:stableBlend',
                 'ribbonConnectBy': 'constraint:matrix',
                 'ribbonExtendEnds':'bool',
                 'ribbonAttachEndsToInfluence':'none:start:end:both',
                 'ikMidControlNum':'int',
                 'ikMidSetup':'none:ribbon:prntConstraint:linearTrack:cubicTrack',
                 'ikMidDynParentMode':BLOCKSHARE._d_attrsTo_make['dynParentMode'],
                 'ikMidDynScaleMode':BLOCKSHARE._d_attrsTo_make['dynParentScaleMode'],
                 
                 'segmentType':'ribbon:ribbonLive:spline:curve:linear:parent',
                 'segmentStretchBy':'translate:scale',
                 'ikBase':'none:cube:simple:hips:head',
                 'settingsPlace':'start:end:cog',
                 'blockProfile':'string',#':'.join(d_block_profiles.keys()),
                 #'blockProfile':':'.join(d_block_profiles.keys()),
                 #'ikEnd':'none:cube:bank:foot:hand:tipBase:tipMid:tipEnd:proxy',
                 'ikEnd':'helper:tipBase:tipMid:tipEnd',
                 'ikSplineTwistEndConnect':'bool',
                 'ikSplineExtendEnd':'bool',                 
                 'ikSplineAimEnd':'bool',
                 'ikSplineTwistAxis':'x:y:z',
                 'ikEndShape':'cast:locator:cube',
                 'ikEndLever':'bool',
                 'ikBaseExtend':'bool',
                 'ikEndExtend':'bool',
                 #'nameIter':'string',
                 #'numControls':'int',
                 #'numShapers':'int',
                 #'numJoints':'int'
                 }

d_defaultSettings = {'version':__version__,
                     'baseSize':MATH.get_space_value(__dimensions[1]),
                     'baseAim':[0,1,0],
                     'numControls': 3,
                     'numSubShapers':0,
                     'loftSetup':0,
                     'loftShape':'circle',
                     'numShapers':3,
                     'controlOffsetMult':1.0,                     
                     'castVector':'up',
                     'squashMeasure':'arcLength',
                     'squash':'simple',
                     'squashFactorMax':1.0,
                     'squashFactorMin':0.0,
                     'ikSplineTwistEndConnect':True,
                     'loftList':['square','circle','square'],
                     'visLabels':True,
                     'ikMidSetup':'prntConstraint',
                     'squash':'both',
                     'squashExtraControl':True,
                     'ribbonAim':'stableBlend',
                     'ribbonParam':'blend',
                     'settingsPlace':1,
                     'ikSplineTwistAxis':'z',
                     'loftSides': 10,
                     'loftSplit':1,
                     'loftDegree':'linear',
                     'numSpacePivots':2,
                     'proxyGeoRoot':1,
                     'meshBuild':True,
                     'ikBase':'cube',
                     'ikEnd':'helper',                     
                     'ikOrientToWorld':True,
                     'ikSetup':'ribbon',
                     'numJoints':5,
                     'proxyDirect':True,
                     'spaceSwitch_direct':False,
                     'spaceSwitch_fk':False,
                     'nameList':['',''],
                     'jointRadius':.1,
                     'visJointHandle':1,
                     'shapeDirection':'y+',
                     'ribbonExtendEnds':True,
                     'ribbonAttachEndsToInfluence':'both',
                     'special_swim':'none',
                     'segmentType':'ribbon',
                     #'blockProfile':'spine',
                     'scaleSetup':False,
                     'squashSkipAim':True,
                     'segmentStretchBy':'scale',
                     'attachPoint':'closest',}



#Skeletal stuff ------------------------------------------------------------------------------------------------
d_skeletonSetup = {'mode':'curveCast',
                   'targetsMode':'prerigHandles',
                   'helperUp':'z-',
                   'countAttr':'neckJoints',
                   'targets':'jointHelper'}

#d_preferredAngles = {'head':[0,-10, 10]}#In terms of aim up out for orientation relative values, stored left, if right, it will invert
#d_rotationOrders = {'head':'yxz'}


#=================================================================================================
#>> Define
#================================================================================================
#@cgmGEN.Timer
def define(self):
    #try:
    _str_func = 'define'
    log.debug("|{0}| >>  ".format(_str_func)+ '-'*80)
    log.debug(self)
    
    _short = self.mNode
    
    for a in 'baseAim','baseSize','baseUp':
        ATTR.set_hidden(_short,a,True)
        
    ATTR.set_min(_short, 'numControls', 1)
    ATTR.set_min(_short, 'loftSides', 3)
    ATTR.set_min(_short, 'loftSplit', 1)
    ATTR.set_min(_short, 'numShapers', 2)
    self.doConnectOut('sy',['sx','sz'])    
    ATTR.set_alias(_short,'sy','blockScale')
    self.setAttrFlags(['sx','sz'])
    
    _blockScale = self.blockScale
    
    #Clean and data query ================================================================
    _shapes = self.getShapes()
    if _shapes:
        log.debug("|{0}| >>  Removing old shapes...".format(_str_func))        
        mc.delete(_shapes)
        defineNull = self.getMessage('defineNull')
        if defineNull:
            log.debug("|{0}| >>  Removing old defineNull...".format(_str_func))
            mc.delete(defineNull)
        self.verify()
    
    
    _size = self.atUtils('defineSize_get')
    """
    _crv = CURVES.create_fromName(name='locatorForm',
                                  direction = 'z+', size = _size)

    SNAP.go(_crv,self.mNode,)
    CORERIG.override_color(_crv, 'white')
    CORERIG.shapeParent_in_place(self.mNode,_crv,False)
    self.addAttr('cgmColorLock',True,lock=True,hidden=True)"""
    
    mDefineNull = self.atUtils('stateNull_verify','define')
    mHandleFactory = self.asHandleFactory()
    
    #Joint Label ---------------------------------------------------------------------------
    #mHandleFactory.addJointLabel(self,self.blockProfile)
    
    self.atUtils('shapeDirection_toBaseDat')
    
    
    #Define our controls ===================================================================
    _d = {'start':{'color':'white'},
          'end':{'color':'white','defaults':{'ty':1}},
          'rp':{'color':'redBright','jointLabel':False,'defaults':{'tx':.5}},              
          'up':{'color':'greenBright','jointLabel':False,'defaults':{'tz':-1}}}
    
    for k,d in list(_d.items()):
        d['arrow'] = 1
        d['tagOnly'] = 1
        
        
    md_handles = {}
    ml_handles = []
    md_vector = {}
    md_jointLabels = {}

    _l_order = ['end','up','rp','start']

    _resDefine = self.UTILS.create_defineHandles(self, _l_order, _d, _size,
                                                 rotVecControl=True,
                                                 blockUpVector = self.baseDat['up'],
                                                 startScale=True)
    md_vector = _resDefine['md_vector']
    md_handles = _resDefine['md_handles']        
    self.UTILS.define_set_baseSize(self)
    
    #if self.hasAttr('jointRadius'):
    """
    _crv = CURVES.create_fromName(name='sphere',#'arrowsAxis', 
                                  bakeScale = 1,                                              
                                  direction = 'z+', size = 1.0)

    mJointRadius = cgmMeta.validateObjArg(_crv,'cgmControl',setClass = True)
    mJointRadius.p_parent = mDefineNull
    mJointRadius.doSnapTo(self.mNode)
    CORERIG.override_color(mJointRadius.mNode, 'black')
    
    mJointRadius.rename("jointRadiusVis")
    _base = self.atUtils('get_shapeOffset')*4
    if self.jointRadius < _base:
        self.jointRadius = _base
    self.doConnectOut('jointRadius',"{0}.scale".format(mJointRadius.mNode),pushToChildren=1)    
    mJointRadius.dagLock()
    mJointRadius.connectParentNode(self, 'rigBlock','jointRadiusVisualize') """
        
        
    #Rotate Plane ======================================================================
    self.UTILS.create_define_rotatePlane(self, md_handles,md_vector)
    _end = md_handles['end'].mNode
    #self.doConnectIn('baseSizeX',"{0}.width".format(_end))
    #self.doConnectIn('baseSizeY',"{0}.height".format(_end))
    #self.doConnectIn('baseSizeZ',"{0}.length".format(_end))
    
    self.UTILS.rootShape_update(self)        
    _dat = self.baseDat
    _dat['baseSize'] = self.baseSize
    self.baseDat = _dat
    BLOCKSHAPES.addJointRadiusVisualizer(self, mDefineNull)
    ml_order = [md_handles['end'],
                md_handles['start'],
                md_handles['up'],
                md_handles['rp'],
                self]
    self.UTILS.controller_walkChain(self,ml_order,'define')
    
    return
    #except Exception,err:cgmGEN.cgmExceptCB(Exception,err,localDat=vars())        
    
    
    
    
#================================================================================================
#>> Form
#===============================================================================================
def formDelete(self):
    try:
        _str_func = 'formDelete'
        log.debug("|{0}| >> ...".format(_str_func)+ '-'*80)
        log.debug("{0}".format(self))
        
        for k in ['end','rp','up','lever','aim','start']:
            mHandle = self.getMessageAsMeta("define{0}Helper".format(k.capitalize()))
            if mHandle:
                l_const = mHandle.getConstraintsTo(typeFilter=['point','orient','parent'])
                if l_const:
                    log.debug("currentConstraints...")
                    pos = mHandle.p_position
        
                    for i,c in enumerate(l_const):
                        log.debug("{0} : {1}".format(i,c))
                        if not mc.ls(c,type='aimConstraint'):
                            mc.delete(c)
                    mHandle.p_position = pos
                if k == 'end':
                    _end = mHandle.mNode                    
                    _baseSize = []
                    for a in 'width','height','length':
                        _baseSize.append(ATTR.get(_end,a))
                    self.baseSize = _baseSize
                    _dat = self.baseDat
                    _dat['baseSize'] = self.baseSize
                    self.baseDat = _dat
                    #self.doConnectIn('baseSizeX',"{0}.width".format(_end))
                    #self.doConnectIn('baseSizeY',"{0}.height".format(_end))
                    #self.doConnectIn('baseSizeZ',"{0}.length".format(_end))                    
        
                mHandle.v = True
                mHandle.template = False        
        self.defineLoftMesh.v = True

    except Exception as err:cgmGEN.cgmExceptCB(Exception,err,localDat=vars())        
    
def form(self):
    try:
        _str_func = 'form'
        log.debug("|{0}| >> ...".format(_str_func)+ '-'*80)
        log.debug("{0}".format(self))
        
        
        #LenSub shapers -------------------------------------------------------------------
        _cnt = self.numShapers-1
        _dat = self.datList_get('numSubShapers')
        _diff = _cnt - len(_dat)
        if len(_dat) < _cnt:
            #l_subs = [self.numSubShapers for i in xrange(self.numShapers-1)]
            for i in range(0,_diff):
                self.datList_append('numSubShapers', self.numSubShapers)
        
        
        #Initial checks =====================================================================================
        log.debug("|{0}| >> Initial checks...".format(_str_func)+ '-'*40)
        _short = self.p_nameShort
        _side = self.UTILS.get_side(self)
            
        _l_basePosRaw = self.datList_get('basePos') or [(0,0,0)]
        _l_basePos = [self.p_position]
        
        _ikSetup = self.getEnumValueString('ikSetup')
        _ikEnd = self.getEnumValueString('ikEnd')
        _loftSetup = self.getEnumValueString('loftSetup')
        _shapersAim = self.getEnumValueString('shapersAim')
        
        #Get base dat =======================================================================            
        log.debug("|{0}| Base dat...".format(_str_func)+ '-'*40)
        md_defineHandles,md_vectorHandles = self.UTILS.define_getHandles(self)
        
        mDefineLoftMesh = self.defineLoftMesh
        mRootUpHelper = self.vectorUpHelper    
        _mVectorAim = MATH.get_obj_vector(self.vectorEndHelper.mNode,asEuclid=True)
        _mVectorUp = MATH.get_obj_vector(mRootUpHelper.mNode,'y+',asEuclid=True)    
        mDefineEndObj = self.defineEndHelper
        mDefineUpObj = self.defineUpHelper
        mDefineStartObj = self.defineStartHelper
        
        self.atUtils('jointRadius_guess',mDefineStartObj.mNode)#...size our jointRadius
    
        _v_range = DIST.get_distance_between_points(self.p_position,
                                                    mDefineEndObj.p_position)
        log.debug("|{0}| >> Generating more pos dat | bbHelper: {1} | range: {2}".format(_str_func,
                                                                                         mDefineLoftMesh.p_nameShort,
                                                                                         _v_range))
        _size_width = mDefineEndObj.width#...x width
        _size_height = mDefineEndObj.height#

        _end = DIST.get_pos_by_vec_dist(_l_basePos[0], _mVectorAim, _v_range)
        _size_length = mDefineEndObj.length#DIST.get_distance_between_points(self.p_position, _end)
        _size_handle = _size_width * 1.25
        self.baseSize = [_size_width,_size_height,_size_length]
            
        _size_handle = _size_width * 1.25
        _size_loft = MATH.get_greatest(_size_width,_size_height)
    
        _l_basePos.append(_end)
        log.debug("|{0}| >> baseSize: {1}".format(_str_func, self.baseSize))
    
        
        #Hide define stuff ---------------------------------------------
        log.debug("|{0}| >> hide define stuff...".format(_str_func)+ '-'*40)
        mDefineLoftMesh.v = False
        mDefineUpObj.v = False
        mDefineEndObj.v = False
        mDefineStartObj.v= False
        #Create temple Null ==================================================================================
        log.debug("|{0}| >> nulls...".format(_str_func)+ '-'*40)
        mFormNull = self.UTILS.stateNull_verify(self,'form')
        mNoTransformNull = self.atUtils('noTransformNull_verify','form')
        mHandleFactory = self.asHandleFactory()
        
        int_shapers = self.numShapers
        _loftSetup = self.getEnumValueString('loftSetup')
        if _loftSetup == 'loftList':
            self.UTILS.verify_loftList(self,int_shapers)
                    
        #>>> Connections ====================================================================================
        log.debug("|{0}| >> Shapers ...".format(_str_func)+ '-'*60)
    
        log.debug("vectorAim: {0}".format(_mVectorAim))
    
        pos_self = self.p_position
        pos_aim = DIST.get_pos_by_vec_dist(pos_self, _mVectorAim, 5)        
        mNoTransformNull = BLOCKUTILS.noTransformNull_verify(self,'form')
    
        _shaperAim = self.getEnumValueString('shaperAim')
        
        #Get base dat =============================================================================        
        _b_lever = False
        md_handles = {}
        ml_handles = []
        md_loftHandles = {}
        ml_loftHandles = []
    
        _loftShapeBase = self.getEnumValueString('loftShape')
        _loftShape = 'loft' + _loftShapeBase[0].capitalize() + ''.join(_loftShapeBase[1:])
        _loftSetup = self.getEnumValueString('loftSetup')
    
        #cgmGEN.func_snapShot(vars())
    
    
        #if _loftSetup == 'default':
        md_handles,ml_handles,ml_shapers,ml_handles_chain = self.UTILS.form_segment(
            self,
            aShapers = 'numShapers',aSubShapers = 'numSubShapers',
            loftShape=_loftShape,l_basePos = _l_basePos, baseSize=_size_handle,
            orientHelperPlug='orientHelper',formAim =  self.getEnumValueString('shapersAim'),
            sizeWidth = _size_width, sizeLoft=_size_loft,side = _side,
            mFormNull = mFormNull,mNoTransformNull = mNoTransformNull,
            mDefineEndObj=mDefineEndObj)
    
        mOrientHelper = self.getMessageAsMeta('orientHelper')
        mUpTrans = md_defineHandles['up'].doCreateAt(setClass = True)
        mUpTrans.p_parent = mOrientHelper.mNode                  
    
        #>>> Connections ================================================================================
        self.msgList_connect('formHandles',[mObj.mNode for mObj in ml_handles_chain])
    
        #>>Loft Mesh ==================================================================================
        if self.numShapers:
            targets = [mObj.loftCurve.mNode for mObj in ml_shapers]
            self.msgList_connect('shaperHandles',[mObj.mNode for mObj in ml_shapers])
        else:
            targets = [mObj.loftCurve.mNode for mObj in ml_handles_chain]
    
        mMesh = self.atUtils('create_prerigLoftMesh',
                             targets,
                             mFormNull,
                             'numShapers',                     
                             'loftSplit',
                             polyType='bezier',
                             baseName = self.cgmName )
        mMesh.connectParentNode(self.mNode,'handle','proxyHelper')
        self.msgList_connect('proxyMeshGeo',[mMesh])
    
        mNoTransformNull.v = False
    
        """
        SNAP.aim_atPoint(md_handles['end'].mNode, position=_l_basePos[0], aimAxis="z-", mode='vector', vectorUp=_mVectorUp)
    
        SNAP.aim_atPoint(md_handles['start'].mNode, position=_l_basePos[-1], aimAxis="z+", mode='vector', vectorUp=_mVectorUp)
        """
        #Constrain the define end to the end of the form handles
        #mc.pointConstraint(md_handles['start'].mNode,mDefineEndObj.mNode,maintainOffset=False)
        
        #mc.scaleConstraint([md_handles['end'].mNode,md_handles['start'].mNode],mDefineEndObj.mNode,maintainOffset=True)            
            
            
        #End setup======================================================================================
        if _ikSetup != 'none':
            mEndHandle = ml_handles_chain[-1]
            log.debug("|{0}| >> ikSetup. End: {1}".format(_str_func,mEndHandle))
            mHandleFactory.setHandle(mEndHandle.mNode)
            _bankSize = [_size_width,
                         _size_width,
                         _size_width]
            
            if _ikEnd == 'bank':
                log.debug("|{0}| >> Bank setup".format(_str_func)) 
                mHandleFactory.addPivotSetupHelper(baseSize = _bankSize).p_parent = mFormNull
            elif _ikEnd in ['foot','paw']:
                log.debug("|{0}| >> foot setup".format(_str_func)) 
                mFoot,mFootLoftTop = mHandleFactory.addFootHelper(baseSize=_bankSize)
                mFoot.p_parent = mFormNull
            elif _ikEnd == 'proxy':
                log.debug("|{0}| >> proxy setup".format(_str_func)) 
                mProxy = mHandleFactory.addProxyHelper(shapeDirection = 'z+',baseSize=_bankSize)
                mProxy.p_parent = mEndHandle
                
                pos_proxy = SNAPCALLS.get_special_pos(mEndHandle.p_nameLong,
                                                     'axisBox','z+',False)
                
                log.debug("|{0}| >> posProxy: {1}".format(_str_func,pos_proxy))
                mProxy.p_position = pos_proxy
                CORERIG.copy_pivot(mProxy.mNode,mEndHandle.mNode)
                
        #Aim end handle -----------------------------------------------------------------------------------
        SNAP.aim_atPoint(md_handles['end'].mNode, position=_l_basePos[0], 
                         aimAxis="z-", mode='vector', vectorUp=_mVectorUp)
        
        
        self.UTILS.form_shapeHandlesToDefineMesh(self)
        
        ml_targets = cgmMeta.asMeta(targets,'cgmObject')
        self.UTILS.controller_walkChain(self,ml_targets,'form')
        
        self.blockState = 'form'#...buffer
    
                
    
    except Exception as err:cgmGEN.cgmExceptCB(Exception,err,localDat=vars())        

#=============================================================================================================
#>> Prerig
#=============================================================================================================
def prerig(self):
    _str_func = 'prerig'
    _short = self.p_nameShort
    _side = self.atUtils('get_side')
    log.debug("|{0}| >>  ".format(_str_func)+ '-'*80)
    log.debug(self)
    
    self.atUtils('module_verify')
    
    log.debug("|{0}| >> [{1}] | side: {2}".format(_str_func,_short, _side))   
    
    #Create some nulls Null  =========================================================================
    mPrerigNull = self.atUtils('prerigNull_verify')
    mNoTransformNull = self.UTILS.noTransformNull_verify(self,'prerig')
    

    #> Get our stored dat=============================================================================
    mHandleFactory = self.asHandleFactory()
    
    ml_formHandles = self.msgList_get('formHandles')
    
    mStartHandle = ml_formHandles[0]    
    mEndHandle = ml_formHandles[-1]    
    mOrientHelper = mStartHandle.orientHelper
    
    
    ml_handles = []
    ml_jointHandles = []
    
    _size = MATH.average(mHandleFactory.get_axisBox_size(mStartHandle.mNode))
    #DIST.get_bb_size(mStartHandle.loftCurve.mNode,True)[0]
    _sizeSub = self.atUtils('get_shapeOffset')*2#_size * .33
    _vec_root_up = ml_formHandles[0].orientHelper.getAxisVector('y+')
    
    idx_IK = -1
    
    #Initial logic=========================================================================================
    log.debug("|{0}| >> Initial Logic...".format(_str_func)) 
    
    _pos_start = mStartHandle.p_position
    _pos_end = mEndHandle.p_position 
    _vec = MATH.get_vector_of_two_points(_pos_start, _pos_end)
    _offsetDist = DIST.get_distance_between_points(_pos_start,_pos_end) / (self.numControls - 1)
    
    _mVectorAim = MATH.get_vector_of_two_points(_pos_start, _pos_end,asEuclid=True)
    _mVectorUp = mOrientHelper.getAxisVector('y+',asEuclid=True)#_mVectorAim.up()
    _worldUpVector = [_mVectorUp.x,_mVectorUp.y,_mVectorUp.z]        

    
    #Track curve ============================================================================
    log.debug("|{0}| >> TrackCrv...".format(_str_func)+'-'*40) 
    
    _trackCurve = mc.curve(d=1,p=[mObj.p_position for mObj in ml_formHandles])
    mTrackCurve = cgmMeta.validateObjArg(_trackCurve,'cgmObject')
    mTrackCurve.rename(self.cgmName + 'prerigTrack_crv')
    mTrackCurve.parent = mNoTransformNull
    
            
    l_clusters = []
    #_l_clusterParents = [mStartHandle,mEndHandle]
    for i,cv in enumerate(mTrackCurve.getComponents('cv')):
        _res = mc.cluster(cv, n = 'test_{0}_{1}_pre_cluster'.format(ml_formHandles[i].p_nameBase,i))
        #_res = mc.cluster(cv)
        mCluster = cgmMeta.asMeta(_res[1])
        mCluster.v = 0
        mCluster.p_parent =  ml_formHandles[i].getMessage('loftCurve')[0]
        l_clusters.append(_res)
            
    mc.rebuildCurve(mTrackCurve.mNode, d=3, keepControlPoints=False,ch=1,n="reparamRebuild")
    
    """
    mTrackCurve.parent = mNoTransformNull
    #mLinearCurve.inheritsTransform = False
    ml_trackSkinJoints = []
    for mObj in ml_formHandles:
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
    
    mTrackCluster.doStore('cgmName', mTrackCurve)
    mTrackCluster.doName()    
        
        """
    """
    l_scales = []
    for mHandle in ml_formHandles:
        l_scales.append(mHandle.scale)
        mHandle.scale = 1,1,1"""
        
    _l_pos = CURVES.returnSplitCurveList(mTrackCurve.mNode,self.numControls,markPoints = False)
    
    #_l_pos = [ DIST.get_pos_by_vec_dist(_pos_start, _vec, (_offsetDist * i)) for i in range(self.numControls-1)] + [_pos_end]
        
    #_sizeUse = self.atUtils('get_shapeOffset')
    mDefineEndObj = self.defineEndHelper    
    #_size_width = mDefineEndObj.width#...x width        
    #_sizeUse1 = _size_width/ 3.0 #self.atUtils('get_shapeOffset')
    #_sizeUse2 = self.atUtils('get_shapeOffset') * 2
    #_sizeUse = min([_sizeUse1,_sizeUse2])
    
    
    _sizeUse = self.jointRadius
    
    
    #Sub handles... ------------------------------------------------------------------------------------
    log.debug("|{0}| >> PreRig Handle creation...".format(_str_func))
    ml_aimGroups = []
    for i,p in enumerate(_l_pos):
        log.debug("|{0}| >> handle cnt: {1} | p: {2}".format(_str_func,i,p))
        
        """
        crv = CURVES.create_fromName('axis3d', size = _sizeUse * 2.0)
        mHandle = cgmMeta.validateObjArg(crv, 'cgmObject', setClass=True)
        mHandle.addAttr('cgmColorLock',True,lock=True,hidden=True)
    
        ml_shapes = mHandle.getShapes(asMeta=1)
        crv2 = CURVES.create_fromName('sphere', size = _sizeUse * 2.5)
        CORERIG.override_color(crv2, 'black')
        SNAP.go(crv2,mHandle.mNode)
        CORERIG.shapeParent_in_place(mHandle.mNode,crv2,False)"""
            
        crv = CURVES.create_fromName('cubeOpen', size = _sizeUse)
        mHandle = cgmMeta.validateObjArg(crv, 'cgmObject', setClass=True)
        #mHandle = cgmMeta.cgmObject(crv, name = 'handle_{0}'.format(i))
        _short = mHandle.mNode
        ml_handles.append(mHandle)
        mHandle.p_position = p
        
        if p == _l_pos[-1]:
            SNAP.aim_atPoint(mHandle.mNode,_l_pos[i-1], aimAxis='z-',mode = 'vector',vectorUp=_worldUpVector)
        else:
            SNAP.aim_atPoint(mHandle.mNode,_l_pos[i+1], mode = 'vector',vectorUp=_worldUpVector)
        
        
        """
        if p == _l_pos[-1]:
            SNAP.aim_atPoint(_short,_l_pos[-2],'z-', 'y+', mode='vector', vectorUp = _vec_root_up)
        else:
            SNAP.aim_atPoint(_short,_l_pos[i+1],'z+', 'y+', mode='vector', vectorUp = _vec_root_up)
        """
        mHandle.p_parent = mPrerigNull
        
        mGroup = mHandle.doGroup(True,True,asMeta=True,typeModifier = 'master')
        ml_aimGroups.append(mGroup)
        _vList = DIST.get_normalizedWeightsByDistance(mGroup.mNode,[mStartHandle.mNode,mEndHandle.mNode])

        _res_attach = RIGCONSTRAINT.attach_toShape(mGroup.mNode, mTrackCurve.mNode, 'conPoint')
        TRANS.parent_set(_res_attach[0], mNoTransformNull.mNode)

        mHandleFactory = self.asHandleFactory(mHandle.mNode)
        
        #Convert to loft curve setup ----------------------------------------------------
        #ml_jointHandles.append(mHandleFactory.addJointHelper(baseSize = _sizeUse))

        mHandleFactory.color(mHandle.mNode,controlType='sub')
    
    
    #ml_handles.append(mEndHandle)
    
    ml_handles[0].connectChildNode(mOrientHelper.mNode,'orientHelper')      
    
    #mc.delete(_res_body)
    self.msgList_connect('prerigHandles', ml_handles)                
    self.atUtils('prerigHandles_getNameDat',True)
    for mHandle in ml_handles:
        BLOCKSHAPES.addJointLabel(self,mHandle,mHandle.cgmName)
        
        
    #Driven curve ============================================================================
    log.debug("|{0}| >> TrackCrv...".format(_str_func)+'-'*40) 
    _trackCurve,l_clusters = CORERIG.create_at([mObj.mNode for mObj in ml_handles], 'cubicTrack',
                                               baseName = self.p_nameBase)
    mDrivenCurve = cgmMeta.asMeta(_trackCurve)
    mDrivenCurve.rename(self.cgmName + 'prerigDriven_crv')
    mDrivenCurve.parent = mNoTransformNull

    mc.rebuildCurve(mDrivenCurve.mNode, d=2, keepControlPoints=0,ch=1,n="reparamRebuild")
    mPrerigNull.connectChildNode(mDrivenCurve.mNode,'drivenCurve')
    

    #...pivot -----------------------------------------------------------------------------
    if self.addPivot:
        _size_pivot = _size
        if ml_formHandles:
            _size_pivot = DIST.get_bb_size(ml_formHandles[0].mNode,True,True)

                
        mPivot = BLOCKSHAPES.pivotHelper(self,self,baseShape = 'square', baseSize=_size_pivot,loft=False, mParent = mPrerigNull)
        mPivot.p_parent = mPrerigNull
        mDriverGroup = ml_formHandles[0].doCreateAt(setClass=True)
        mDriverGroup.rename("Pivot_driver_grp")
        mDriverGroup.p_parent = mPrerigNull
        mGroup = mPivot.doGroup(True,True,asMeta=True,typeModifier = 'track',setClass='cgmObject')
        mGroup.p_parent = mDriverGroup
        mc.scaleConstraint([ml_formHandles[0].mNode],mDriverGroup.mNode, maintainOffset = True)

        #mHandleFactory.addPivotSetupHelper()
        self.connectChildNode(mPivot,'pivotHelper')

        #if _shape in ['pyramid','semiSphere','circle','square']:
        #    mPivot.p_position = self.p_position
        #elif b_shapers:mPivot.p_position = pos_shaperBase        

    #Settings =======================================================================================
    mSettings = BLOCKSHAPES.settings(self,mPrerigNull = mPrerigNull)
    self.msgList_connect('prerigHandles', ml_handles)
    
    #Point Contrain the rpHandle -------------------------------------------------------------------------
    mVectorRP = self.getMessageAsMeta('vectorRpHelper')
    str_vectorRP = mVectorRP.mNode
    ATTR.set_lock(str_vectorRP,'translate',False)
    
    mc.pointConstraint([ml_handles[0].mNode], str_vectorRP,maintainOffset=False)
    ATTR.set_lock(str_vectorRP,'translate',True)
    
    #Move start and end... ------------------------------------------------------------------------
    ml_handles[0].p_position = CURVES.getPercentPointOnCurve(mTrackCurve.mNode, .05)
    ml_handles[-1].p_position = CURVES.getPercentPointOnCurve(mTrackCurve.mNode, .95)
    
    self.atUtils('prerig_handlesLayout','even','cubic',2)
    

    self.UTILS.controller_walkChain(self,ml_handles,'prerig')
    
    #IK handles....------------------------------------------------------------------------------
    d_ikHandles = {'start':{'idx':0},
                   'end':{'idx':-1}}
    l_ikHandlesKeys = ['start','end']
    
    str_start = self.getEnumValueString('ikBase')
    if str_start in ['hips','head']:
        d_ikHandles['start']['idx'] = 1
        
    str_end = self.getEnumValueString('ikEnd')
    if str_end == 'tipBase':
        d_ikHandles['end']['idx'] = -2
        
    #num of mid handles...
    _ikMidControlNum = self.ikMidControlNum
    if self.ikMidControlNum:
        if _ikMidControlNum == 1:
            _values = [.5]
        elif _ikMidControlNum == 2:
            _values = [.33,.66]
        else:
            _values = MATH.get_splitValueList(0,1,_ikMidControlNum + 2,True, .2, .8)  
        
        for i,v in enumerate(_values):
            _key = 'mid_{}'.format(i)
            l_ikHandlesKeys.insert(-1,_key)
            d_ikHandles[_key] = {'pos': CURVES.getPercentPointOnCurve(mTrackCurve.mNode, v) }
            
    #cgmGEN.func_snapShot(vars())
    ml_ikHandles = []
    ml_midIKHandles = []
    for key in l_ikHandlesKeys:
        dat = d_ikHandles[key]
        
        if key.startswith('mid'):
            _str = 'ik{0}_Handle'.format(CORESTRING.capFirst(key))                        
            crv = CURVES.create_fromName('locatorForm', size = _sizeUse * 3.0)
            BLOCKSHAPES.color(self,crv,controlType='sub')
        else:
            _str = 'ik{0}Handle'.format(CORESTRING.capFirst(key))            
            crv = CURVES.create_fromName('axis3d', size = _sizeUse * 2.0)
            
        mHandle = cgmMeta.validateObjArg(crv, 'cgmObject', setClass=True)
        mHandle.addAttr('cgmColorLock',True,lock=True,hidden=True)
        self.connectChildNode(mHandle.mNode,_str)
        
        mHandle.rename("{0}_{1}".format(self.cgmName,_str))
        
        if key.startswith('mid'):
            mHandle.doSnapTo(ml_handles[d_ikHandles['start']['idx']])
            mHandle.p_position = dat['pos']
            mHandle.p_parent = mPrerigNull
            ml_midIKHandles.append(mHandle)
    
            #res_attach = RIGCONSTRAINT.attach_toShape(mTrackGroup.mNode,mTrackCurve.mNode,'conPoint')
            #TRANS.parent_set(res_attach[0],mNoTransformNull.mNode)            
            
            
        else:
            mHandle.doSnapTo(ml_handles[dat.get('idx',0)])
            mHandle.p_parent = mPrerigNull# ml_handles[dat.get('idx',0)]
            
        mTrackGroup = mHandle.doGroup(True,True,asMeta=True,typeModifier = 'track',setClass='cgmObject')
        
        #Need to resolve this better
        #self.msgList_append('prerigHandles', mHandle)
        if key == 'start':
            ml_ikHandles.insert(0,mHandle)
        elif key == 'end':
            ml_ikHandles.append(mHandle)
        else:
            ml_ikHandles.insert(1,mHandle)
        
        
    if ml_midIKHandles:
        mPrerigNull.msgList_connect('ikMidHelpers', ml_midIKHandles)
        
    mPrerigNull.msgList_connect('ikHelpers', ml_ikHandles)
    self.UTILS.controller_walkChain(self,ml_ikHandles,'prerig')
        
    
    #...cog -----------------------------------------------------------------------------
    mCog = False
    
    if self.addCog:
        mCog = self.asHandleFactory(ml_formHandles[0]).addCogHelper(baseSize = self.jointRadius * 5, shapeDirection= self.getEnumValueString('shapeDirection'))
        
        mShape = mCog.shapeHelper
        mShape.p_parent = mPrerigNull
        mCog.p_parent = mPrerigNull
        
        for mObj in mCog,mShape:
            mObj.p_position = ml_handles[d_ikHandles['start']['idx']].p_position
        
        self.UTILS.controller_walkChain(self,[mCog,mShape],'prerig')
        
    create_jointHelpers(self,force=True)


    #Close out =======================================================================================
    mNoTransformNull.v = False
    #cgmGEN.func_snapShot(vars())
    
    #if self.getMessage('formLoftMesh'):
        #mFormLoft = self.getMessage('formLoftMesh',asMeta=True)[0]
        #mFormLoft.v = False        
        
    return True


def attachToCurve(mHandle,mCrv,mShape = None,parentTo=None,pct = None, blend = True):
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

def create_jointHelpers(self,cnt=None, force = False):
    #>>Joint placers ================================================================================    
    _str_func = 'create_jointHelpers'
    mPrerigNull = self.prerigNull
    
    #Joint placer aim....
    
    #Clean up
    ml_jointHelpers = self.msgList_get('jointHelpers')
    if not force:
        if cnt and len(ml_jointHelpers) == cnt:
            return True
        if not cnt:
            if self.numJoints == len(ml_jointHelpers):
                return True
    
    #If we have existing, we want to save that result so we can try to match those changes 
    _targetCurve = None
    if ml_jointHelpers:
        _targetCurve = CORERIG.create_at(None, 'curveLinear',l_pos = [mObj.p_position for mObj in ml_jointHelpers])
    
    for mJointHelper in ml_jointHelpers:
        bfr = mJointHelper.getMessage('mController')
        if bfr:
            log.warning("Deleting controller: {0}".format(bfr))
            mc.delete(bfr)
        mJointHelper.delete()
            
    for k in ['jointHelpersGroup','jointHelpersNoTransGroup']:
        old = mPrerigNull.getMessage(k)
        if old:
            log.warning("Deleting old: {0}".format(old))
            mc.delete(old)
    
    old_loft = self.getMessage('jointLoftMesh')
    if old_loft:
        mc.delete(old_loft)
        
    if cnt:
        self.numJoints = cnt
    
    #data
    ml_handles = self.msgList_get('prerigHandles')
    mDriven = self.prerigNull.getMessageAsMeta('drivenCurve')
    mNoTrans = self.noTransPrerigNull
    
    ml_formHandles = self.msgList_get('formHandles')
    mStartHandle = ml_formHandles[0]    
    mEndHandle = ml_formHandles[-1]    
    mOrientHelper = mStartHandle.orientHelper
    
    
    l_pcts = [i*(1.0/(self.numJoints-1)) for i in range(self.numJoints-1)] + [1.0]
    
    #pprint.pprint(l_pcts)
    _size = self.jointRadius
    
    mGroupNoTrans = mNoTrans.doCreateAt('null')
    mGroupNoTrans.rename('jointHelpers_noTransGroup')
    mPrerigNull.connectChildNode(mGroupNoTrans.mNode,'jointHelpersNoTransGroup')
    mGroupNoTrans.p_parent = mNoTrans
    
    mGroup = mPrerigNull.doCreateAt('null')
    mGroup.rename('jointHelpersGroup')
    _size = self.jointRadius
    mPrerigNull.connectChildNode(mGroup.mNode,'jointHelpersGroup')
    mGroup.p_parent = mPrerigNull    
    
    
    _l_names = self.atUtils('skeleton_getNameDicts',False,cgmType = 'jointHelper')
    
    #pprint.pprint(_l_names)
    
    ml_jointHelpers = []
    
    
    if self.numJoints == len(ml_handles):
        for mHandle in ml_handles:
            mJointHelper = BLOCKSHAPES.addJointHelper(self,size = _size,
                                                      d_nameTags= mHandle.getNameDict(ignore=['cgmType']))
            mJointHelper.p_parent = mGroup
            
            mTrackGroup = mJointHelper.doGroup(True,True,asMeta=True,typeModifier = 'track',setClass='cgmObject')
            mc.pointConstraint(mHandle.mNode, mTrackGroup.mNode)
            
            mJointHelper.resetAttrs(['tx','ty','tz','rx','ry','rz'])
            
            ml_jointHelpers.append(mJointHelper)
            self.doConnectOut('visJointHandle',"{0}.v".format(mJointHelper.mNode))
            ATTR.set_standardFlags(mJointHelper.mNode,['v'])            
    else:
        for i,pct in enumerate(l_pcts):
            """mLoc = cgmMeta.asMeta(LOC.create(position = CURVES.getPercentPointOnCurve(mDriven.mNode, pct),
                                             name = "pct_{0}_loc".format(i)))"""
            
            
            mJointHelper = BLOCKSHAPES.addJointHelper(self,size = _size, d_nameTags=_l_names[i])
            
    
            mJointHelper.p_position = CURVES.getPercentPointOnCurve(mDriven.mNode, pct)
            mJointHelper.p_parent = mGroup
            mTrackGroup = mJointHelper.doGroup(True,True,asMeta=True,typeModifier = 'track',setClass='cgmObject')
            
            
            attachToCurve(mJointHelper,mDriven,None,mGroupNoTrans,pct,False)
            
            """
            res_attach = RIGCONSTRAINT.attach_toShape(mTrackGroup.mNode,mDriven.mNode,'conPoint')
            TRANS.parent_set(res_attach[0],mGroupNoTrans.mNode)"""
            
            if _targetCurve:
                mJointHelper.p_position = CURVES.getPercentPointOnCurve(_targetCurve, pct)
            
            
            ml_jointHelpers.append(mJointHelper)
            self.doConnectOut('visJointHandle',"{0}.v".format(mJointHelper.mNode))
            ATTR.set_standardFlags(mJointHelper.mNode,['v'])
            
    #mc.rebuildCurve(mDriven.mNode, d=1, keepControlPoints=0,ch=1,n="reparamRebuild")
    #Aim --------------------------------------------------------------------------
    l_targets = []
    for i,mJointHelper in enumerate(ml_jointHelpers):
        mLoftCurve = mJointHelper.loftCurve
        
        if not mLoftCurve.getMessage('aimGroup'):
            mLoftCurve.doGroup(True,asMeta=True,typeModifier = 'aim')
            
        
        mAimGroup = mLoftCurve.getMessage('aimGroup',asMeta=True)[0]
        
        l_targets.append(mLoftCurve.mNode)
        
        mLoftCurve.v = 0
        
        if mJointHelper == ml_jointHelpers[-1]:
            mc.aimConstraint(ml_jointHelpers[-2].mNode, mAimGroup.mNode, maintainOffset = False,
                             aimVector = [0,0,-1], upVector = [0,1,0], worldUpObject = mOrientHelper.mNode, #skip = 'z',
                             worldUpType = 'objectrotation', worldUpVector = [0,1,0])            
        else:
            mc.aimConstraint(ml_jointHelpers[i+1].mNode, mAimGroup.mNode, maintainOffset = False, #skip = 'z',
                             aimVector = [0,0,1], upVector = [0,1,0], worldUpObject = mOrientHelper.mNode,
                             worldUpType = 'objectrotation', worldUpVector = [0,1,0])          

    self.msgList_connect('jointHelpers',ml_jointHelpers)
    self.atUtils('create_jointLoft',
                 l_targets,
                 mPrerigNull,
                 'numJoints',
                 degree = 1,
                 baseName = self.cgmName )
    
    self.UTILS.controller_walkChain(self,ml_jointHelpers,'prerig')
    
    #IKMid Handle ---------------------------------------------------------------------
    _trackCurve,l_clusters = CORERIG.create_at([mObj.mNode for mObj in ml_jointHelpers],'linearTrack',baseName = "{0}_drivenCrv".format(self.p_nameBase))
    mCrv = cgmMeta.asMeta(_trackCurve)
    mShape = cgmMeta.asMeta(mCrv.getShapes()[0])
    _shape = mShape.mNode
    
    """
    _node = mc.rebuildCurve(mCrv.mNode, d=3, keepControlPoints=False,
                            ch=1,s=len(ml_jointHelpers),
                            n="{0}_reparamRebuild".format(mCrv.p_nameBase))
    mc.rename(_node[1],"{0}_reparamRebuild".format(mCrv.p_nameBase))
    """
    mCrv.p_parent = mGroupNoTrans
     
    ml_ikHelpers = mPrerigNull.msgList_get('ikHelpers')
    
    #for k in ['start','end','mid']:
    for mHandle in ml_ikHelpers:
        #_str = 'ik{0}Handle'.format(CORESTRING.capFirst(k))    
        #mHandle = self.getMessageAsMeta(_str)
        attachToCurve(mHandle,mCrv,mShape,mGroupNoTrans)
        
    #Cog
    mHandle = self.getMessageAsMeta('cogHelper')
    if mHandle:
        log.info("cogHelper")    
        attachToCurve(mHandle,mCrv,mShape,mGroupNoTrans)
    
        
    
    if _targetCurve:
        mc.delete(_targetCurve)
    return ml_jointHelpers

    
    
def prerigDelete(self):
    try:
        if self.getMessage('formLoftMesh'):
            mFormLoft = self.getMessage('formLoftMesh',asMeta=True)[0]
            for s in mFormLoft.getShapes(asMeta=True):
                s.overrideDisplayType = 2
            mFormLoft.v = True
            
        #vectorRP ----------------------------------------------
        mVectorRP = self.getMessageAsMeta('vectorRpHelper')
        str_vectorRP = mVectorRP.mNode
        ATTR.set_lock(str_vectorRP,'translate',False)
        mVectorRP.resetAttrs(['tx','ty','tz'])
        ATTR.set_lock(str_vectorRP,'translate',True)        
            
    except Exception as err:cgmGEN.cgmExceptCB(Exception,err,localDat=vars())        


def skeleton_check(self):
    return True

def skeleton_build(self, forceNew = True):
    #try:
    _short = self.mNode
    _str_func = 'skeleton_build'
    log.debug("|{0}| >>  ".format(_str_func)+ '-'*80)
    log.debug("{0}".format(self))
    
    ml_joints = []
    
    mModule = self.atUtils('module_verify')
    
    mRigNull = mModule.rigNull
    if not mRigNull:
        raise ValueError("No rigNull connected")
    
    ml_formHandles = self.msgList_get('formHandles',asMeta = True)
    if not ml_formHandles:
        raise ValueError("No formHandles connected")
    
    ml_jointHelpers = self.msgList_get('jointHelpers',asMeta = True)
    if not ml_jointHelpers:
        raise ValueError("No jointHelpers connected")
    
    #>> If skeletons there, delete ----------------------------------------------------------------------------------- 
    _bfr = mRigNull.msgList_get('moduleJoints',asMeta=True)
    if _bfr:
        log.debug("|{0}| >> Joints detected...".format(_str_func))            
        if forceNew:
            log.debug("|{0}| >> force new...".format(_str_func))                            
            mc.delete([mObj.mNode for mObj in _bfr])
        else:
            return _bfr
    
    
            
    _expected = self.numJoints
    if len(ml_jointHelpers) != _expected:
        return log.error("Joint helper count not found: {0} != expected: {1}. Recreate your joint helpers.".format(len(ml_jointHelpers),_expected))    
    
    
    
    #_baseNameAttrs = ATTR.datList_getAttrs(self.mNode,'baseNames')    

    log.debug("|{0}| >> creating...".format(_str_func))
    
    #_d = self.atBlockUtils('skeleton_getCreateDict', self.numJoints)
    
    
    """
    
    if self.numJoints == self.numControls:
        log.debug("|{0}| >> Control count matches joint ({1})...".format(_str_func,self.numJoints))
        l_pos = []
        for mObj in ml_jointHelpers:
            l_pos.append(mObj.p_position)
    else:
        log.debug("|{0}| >> Generating count ({1})...".format(_str_func,self.numJoints))
        _crv = CURVES.create_fromList(targetList = [mObj.mNode for mObj in ml_jointHelpers])
        l_pos = CURVES.returnSplitCurveList(_crv,self.numJoints)
        mc.delete(_crv)        
        """
    
    mOrientHelper = ml_formHandles[0].orientHelper

    
    #reload(JOINT)
    mVecUp = self.atUtils('prerig_get_upVector')
    
    ml_joints = JOINT.build_chain([mHelper.p_position for mHelper in ml_jointHelpers], parent=True, worldUpAxis= mVecUp)
    

    for i,mJoint in enumerate(ml_joints):
        d = ml_jointHelpers[i].getNameDict(ignore = ['cgmType'])
        d['cgmType'] = 'skinJoint'
        for t,tag in list(d.items()):
            if t and tag:
                mJoint.doStore(t,tag)
        mJoint.doName()
        #mJoint.rename(_l_names[i])
        
    #End Fixing --------------------------------
    #if len(ml_handleJoints) > self.numControls:
        #log.debug("|{0}| >> Extra joints, checking last handle".format(_str_func))

    mEndOrient = self.ikEndHandle
    """Don't do this aim thing, Josh, it breaks ray casting"""
    #mEnd = ml_joints[-1]
    #log.debug("|{0}| >> Fixing end: {1}".format(_str_func,mEnd))
    #mEnd.jointOrient = 0,0,0
    #SNAP.aim_atPoint(mEnd.mNode, DIST.get_pos_by_axis_dist(mEndOrient.mNode,'z+'),mode='vector',
    #                 vectorUp=mEndOrient.getAxisVector('y+'))
    #JOINT.freezeOrientation(mEnd.mNode) 
    #-------------------------------------------------------------------------
        
    ml_joints[0].parent = False
    
    _radius = self.jointRadius #self.atUtils('get_shapeOffset')
    #_radius = DIST.get_distance_between_points(ml_joints[0].p_position, ml_joints[-1].p_position)/ 10
    #MATH.get_space_value(5)

    
    for mJoint in ml_joints:
        mJoint.displayLocalAxis = 1
        mJoint.radius = _radius

    mRigNull.msgList_connect('moduleJoints', ml_joints)
    
    #cgmGEN.func_snapShot(vars())    
    self.atBlockUtils('skeleton_connectToParent')
    for mJnt in ml_joints:mJnt.rotateOrder = 5
    
    if self.scaleSetup:
        for mJnt in ml_joints[1:]:
            mJnt.p_parent = ml_joints[0]
    
    return ml_joints
    #except Exception,err:cgmGEN.cgmExceptCB(Exception,err,localDat=vars())        


#=============================================================================================================
#>> rig
#=============================================================================================================
#NOTE - self here is a rig Factory....

#d_preferredAngles = {'default':[0,-10, 10]}#In terms of aim up out for orientation relative values, stored left, if right, it will invert
#d_preferredAngles = {'out':10}
d_preferredAngles = {}

d_rotateOrders = {'default':'yxz'}

#Rig build stuff goes through the rig build factory --------------------------------------------

#@cgmGEN.Timer
def rig_prechecks(self):
    try:
        _str_func = 'rig_prechecks'
        log.debug(cgmGEN.logString_start(_str_func))
        log.debug(self)
        
        mBlock = self.mBlock    
        
        #Lever ============================================================================    
        log.debug(cgmGEN._str_subLine)
        str_ikSetup = mBlock.getEnumValueString('ikSetup')
        #if mBlock.scaleSetup and str_ikSetup in ['spline']:
        #    self.l_precheckErrors.append('scaleSetup with spline not ready. Use ribbon if you need scale')
            #return False
            
        str_segmentType = mBlock.getEnumValueString('segmentType')
        if str_segmentType == 'parent' and mBlock.numControls != mBlock.numJoints:
            self.l_precheckErrors.append('segmentType parent requires same number of controls as joints')
            
            
        if mBlock.special_swim and str_segmentType != 'ribbon':
            self.l_precheckErrors.append('Special Swim setup requires segmentType of ribbon')
            
        
        str_settingPlace = mBlock.getEnumValueString('settingsPlace')
        if str_settingPlace == 'cog' and not mBlock.addCog:
            self.l_precheckErrors.append('Settings place is cog and addCog off. Please resolve')
        
        if mBlock.numControls > mBlock.numJoints:
            self.l_precheckErrors.append('More controls ({0}) than joints ({1})'.format(mBlock.numControls, mBlock.numJoints))
        
        if mBlock.ikEndLever:
            self.l_precheckErrors.append('End Lever not ready')
            
        for mObj in mBlock.moduleTarget.rigNull.msgList_get('moduleJoints'):
            if not mObj.p_parent:
                self.l_precheckErrors.append("Joint not parented: {0} | Reskeletonize.".format(mObj.mNode))
                
        #ml = mBlock.moduleTarget.rigNull.msgList_get('moduleJoints',cull=True)
        #if len(ml) != mBlock.numJoints:
        #    self.l_precheckErrors.append('Joint len ({0}) != numJoints setting ({1})'.format(len(ml), mBlock.numJoints))
            
        
            #raise NotImplementedError,"scaleSetup not ready."
    except Exception as err:cgmGEN.cgmExceptCB(Exception,err,localDat=vars())        

#@cgmGEN.Timer
def rig_dataBuffer(self):
    try:
        _short = self.d_block['shortName']
        _str_func = 'rig_dataBuffer'
        log.debug("|{0}| >>  ".format(_str_func)+ '-'*80)
        log.debug("{0}".format(self))
        
        mBlock = self.mBlock
        mModule = self.mModule
        mRigNull = self.mRigNull
        mPrerigNull = mBlock.prerigNull
        ml_formHandles = mBlock.msgList_get('formHandles')
        ml_prerigHandles = mBlock.msgList_get('prerigHandles')
        
        self.ml_formHandles = ml_formHandles
        self.ml_prerigHandles = ml_prerigHandles
        self.mHandleFactory = self.mBlock.asHandleFactory()
        
        self.ml_ikMidHelpers = mPrerigNull.msgList_get('ikMidHelpers')
        self.ml_ikMidControls = []
        
        ml_handleJoints = mPrerigNull.msgList_get('handleJoints')
        mMasterNull = self.d_module['mMasterNull']
        
        self.mRootFormHandle = ml_formHandles[0]
        
        if mBlock.numJoints == 4 and mBlock.numControls == 3:
            log.warning("|{0}| >> Mid control unavilable with count: joint: {1} | controls: {2}".format(_str_func,mBlock.numJoints, mBlock.numControls))  
            mBlock.ikMidSetup = 0
            
        for k in ['segmentType','settingsPlace','ikEndShape','ikEnd','ikBase','ikMidSetup','ribbonAttachEndsToInfluence','segmentStretchBy','squashFactorMode']:
            self.__dict__['str_{0}'.format(k)] = ATTR.get_enumValueString(mBlock.mNode,k)
                
        #Vector ====================================================================================
        self.mVec_up = mBlock.atUtils('prerig_get_upVector')
        log.debug("|{0}| >> self.mVec_up: {1} ".format(_str_func,self.mVec_up))
        

        #Initial option checks ============================================================================    
        #if mBlock.scaleSetup:
            #raise NotImplementedError,"Haven't setup scale yet."
        """    
        if mBlock.ikEnd in [2,3,4]:
            raise NotImplementedError,"Haven't setup ik end: {0}".format(ATTR.get_enumValueString(mBlock.mNode,'ikEnd'))"""
        
        #if mBlock.ikSetup > 1:
            #raise NotImplementedError,"Haven't setup ik mode: {0}".format(ATTR.get_enumValueString(mBlock.mNode,'ikSetup'))
        
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
    
        #self.d_squashStretch['additiveScaleEnds'] = mBlock.scaleSetup
        self.d_squashStretch['extraSquashControl'] = mBlock.squashExtraControl
        self.d_squashStretch['squashFactorMax'] = mBlock.squashFactorMax
        self.d_squashStretch['squashFactorMin'] = mBlock.squashFactorMin
        
        log.debug("|{0}| >> self.d_squashStretch..".format(_str_func))    
        #pprint.pprint(self.d_squashStretch)
        
        #Check for mid control and even handle count to see if w need an extra curve
        if mBlock.ikMidSetup:
            #if MATH.is_even(mBlock.numControls):
            self.d_squashStretchIK['sectionSpans'] = 2
                
        if self.d_squashStretchIK:
            log.debug("|{0}| >> self.d_squashStretchIK..".format(_str_func))    
            #pprint.pprint(self.d_squashStretchIK)
        
        
        if not self.b_scaleSetup:
            pass
        
        log.debug("|{0}| >> self.b_scaleSetup: {1}".format(_str_func,self.b_scaleSetup))
        log.debug("|{0}| >> self.b_squashSetup: {1}".format(_str_func,self.b_squashSetup))
        
        log.debug(cgmGEN._str_subLine)
        
        #Frame Handles =============================================================================
        self.mToe = False
        self.mBall = False
        self.int_handleEndIdx = -1
        self.b_ikNeedEnd = False
        l= []
        
        str_ikEnd = ATTR.get_enumValueString(mBlock.mNode,'ikEnd')
        log.debug("|{0}| >> IK End: {1}".format(_str_func,str_ikEnd))
        
        if str_ikEnd in ['foot','hand']:
            raise NotImplemented("not done")
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
            #if not mBlock.hasEndJoint:
                #self.b_ikNeedEnd = True
                #log.debug("|{0}| >> Need IK end joint".format(_str_func))
            #else:
            if str_ikEnd == 'tipBase':
                self.int_handleEndIdx -=1
                
        log.debug("|{0}| >> self.int_handleEndIdx: {1}".format(_str_func,self.int_handleEndIdx))
        
        
        
        str_ikBase = ATTR.get_enumValueString(mBlock.mNode,'ikBase')
        log.debug("|{0}| >> IK Base: {1}".format(_str_func,str_ikBase))    
        self.int_segBaseIdx = 0
        if str_ikBase in ['hips','head']:
            self.int_segBaseIdx = 1
        log.debug("|{0}| >> self.int_segBaseIdx: {1}".format(_str_func,self.int_segBaseIdx))
        
        log.debug(cgmGEN._str_subLine)
        
        
        #Lever ============================================================================    
        _b_lever = False
        self.b_leverJoint = False
        ml_formHandlesUse = copy.copy(ml_formHandles)
        ml_fkShapeHandles = copy.copy(ml_prerigHandles)
        self.mRootFormHandle = ml_formHandles[0]
        """
        if mBlock.buildLeverBase:
            _b_lever = True        
            if mBlock.hasLeverJoint:
                self.b_leverJoint = True
            else:
                log.debug("|{0}| >> Need leverJoint | self.b_leverJoint ".format(_str_func))
            self.mRootFormHandle = ml_formHandles[1]
            ml_formHandlesUse = ml_formHandlesUse[1:]
            
            ml_fkShapeHandles = ml_fkShapeHandles[1:]"""
        self.b_lever = _b_lever
            
        self.ml_fkShapeTargets = ml_fkShapeHandles

        self.int_formHandleMidIdx = MATH.get_midIndex(len(ml_formHandlesUse))
        self.mMidFormHandle = ml_formHandles[self.int_formHandleMidIdx]
            
        log.debug("|{0}| >> Lever: {1}".format(_str_func,self.b_lever))    
        log.debug("|{0}| >> self.mRootFormHandle : {1}".format(_str_func,self.mRootFormHandle))
        log.debug("|{0}| >> self.mMidFormHandle : {1}".format(_str_func,self.mMidFormHandle))    
        log.debug("|{0}| >> Mid self.int_formHandleMidIdx idx: {1}".format(_str_func,self.int_formHandleMidIdx))
        
        
        

        mid = MATH.get_midIndex(mBlock.numControls)
        self.int_handleMidIdx = mid
        
        log.debug("|{0}| >> Mid self.int_handleMidIdx idx: {1}".format(_str_func,
                                                                       self.int_handleMidIdx))        
    
        #Pivot checks ============================================================================
        mPivotHolderHandle = ml_formHandles[-1]
        self.b_pivotSetup = False
        self.mPivotHelper = False
        if mPivotHolderHandle.getMessage('pivotHelper'):
            log.debug("|{0}| >> Pivot setup needed".format(_str_func))
            self.b_pivotSetup = True
            self.mPivotHelper = mPivotHolderHandle.getMessageAsMeta('pivotHelper')
            log.debug(cgmGEN._str_subLine)
            
        
        
        
        #Offset ============================================================================    
        str_offsetMode = ATTR.get_enumValueString(mBlock.mNode,'offsetMode')
        if not mBlock.offsetMode:
            log.debug("|{0}| >> default offsetMode...".format(_str_func))
            self.v_offset = self.mPuppet.atUtils('get_shapeOffset') * mBlock.controlOffsetMult
        else:
            str_offsetMode = ATTR.get_enumValueString(mBlock.mNode,'offsetMode')
            log.debug("|{0}| >> offsetMode: {1}".format(_str_func,str_offsetMode))
            
            l_sizes = []
            for mHandle in ml_formHandles:
                #_size_sub = SNAPCALLS.get_axisBox_size(mHandle)
                #l_sizes.append( MATH.average(_size_sub[1],_size_sub[2]) * .1 )
                _size_sub = POS.get_bb_size(mHandle,True)
                l_sizes.append( MATH.average(_size_sub) * .1 )            
            self.v_offset = MATH.average(l_sizes)
            #_size_midHandle = SNAPCALLS.get_axisBox_size(ml_formHandles[self.int_handleMidIdx])
            #self.v_offset = MATH.average(_size_midHandle[1],_size_midHandle[2]) * .1        
        log.debug("|{0}| >> self.v_offset: {1}".format(_str_func,self.v_offset))    
        
        
        #DynParents =============================================================================
        #reload(self.UTILS)
        self.UTILS.get_dynParentTargetsDat(self)
    
        #rotateOrder =============================================================================
        _str_orientation = self.d_orientation['str']
        #self.rotateOrder = "{0}{1}{2}".format(_str_orientation[1],_str_orientation[2],_str_orientation[0])
        self.rotateOrder_IK = "{}{}{}".format(_str_orientation[0],_str_orientation[2],_str_orientation[1])
        self.rotateOrder_FK = "{}{}{}".format(_str_orientation[1],_str_orientation[2],_str_orientation[0])
        
        log.debug("|{}| >> rotateOrder | fk: {} | ik: {}".format(_str_func,self.rotateOrder_FK, self.rotateOrder_IK))
    
        log.debug(cgmGEN._str_subLine)
        
        #mainRot axis =============================================================================
        """For twist stuff"""
        #_mainAxis = ATTR.get_enumValueString(mBlock.mNode,'mainRotAxis')
        #_axis = ['aim','up','out']
        #if _mainAxis == 'up':
        #    _upAxis = 'out'
        #else:
        #    _upAxis = 'up'
        self.v_twistUp = self.d_orientation.get('vectorOut')
    
        #self.v_twistUp = self.d_orientation.get('vector{0}'.format(_mainAxis.capitalize()))
        log.debug("|{0}| >> twistUp | self.v_twistUp: {1}".format(_str_func,self.v_twistUp))
    
        log.debug(cgmGEN._str_subLine)            
    
        return True
    except Exception as err:cgmGEN.cgmExceptCB(Exception,err,localDat=vars())        

#@cgmGEN.Timer
def rig_skeleton(self):
    try:
        _short = self.d_block['shortName']
        _str_func = 'rig_skeleton'
        log.debug("|{0}| >>  ".format(_str_func)+ '-'*80)
        log.debug(self)    
        
        mBlock = self.mBlock
        mRigNull = self.mRigNull
        ml_jointsToConnect = []
        ml_jointsToHide = []
        ml_blendJoints = []
        ml_joints = mRigNull.msgList_get('moduleJoints')
        self.d_joints['ml_moduleJoints'] = ml_joints
        
        str_ikBase = ATTR.get_enumValueString(mBlock.mNode,'ikBase')        
        str_ikSetup = ATTR.get_enumValueString(mBlock.mNode,'ikSetup')        
        
        #reload(BLOCKUTILS)
        BLOCKUTILS.skeleton_pushSettings(ml_joints,self.d_orientation['str'],
                                         self.d_module['mirrorDirection'],
                                         d_rotateOrders)#, d_preferredAngles)
        
        
        log.debug("|{0}| >> rig chain...".format(_str_func))              
        ml_rigJoints = BLOCKUTILS.skeleton_buildDuplicateChain(mBlock, ml_joints, 'rig', self.mRigNull,'rigJoints',blockNames=True)
        #pprint.pprint(ml_rigJoints)
        
        #...fk chain -------------------------------------------------------------------------------------
        log.debug("|{0}| >> fk_chain".format(_str_func))
        ml_fkJoints = BLOCKUTILS.skeleton_buildHandleChain(mBlock,'fk','fkJoints')
        
        ml_jointsToHide.extend(ml_fkJoints)
    
        
        #...fk chain ------------------------------------------------------------------------------------
        if mBlock.ikSetup:
            log.debug("|{0}| >> ikSetup on. Building blend and IK chains...".format(_str_func))  
            ml_blendJoints = BLOCKUTILS.skeleton_buildHandleChain(self.mBlock,'blend','blendJoints')
            ml_ikJoints = BLOCKUTILS.skeleton_buildHandleChain(self.mBlock,'ik','ikJoints')
            ml_jointsToConnect.extend(ml_ikJoints)
            ml_jointsToHide.extend(ml_blendJoints)
            
            #BLOCKUTILS.skeleton_pushSettings(ml_ikJoints,self.d_orientation['str'],
            #                                 self.d_module['mirrorDirection'],
            #                                 d_rotateOrders, d_preferredAngles)
            
            for i,mJnt in enumerate(ml_ikJoints):
                if mJnt not in [ml_ikJoints[0],ml_ikJoints[-1]]:
                    mJnt.preferredAngle = mJnt.jointOrient
                    
            
            
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
        _ikSetup = mBlock.getEnumValueString('ikSetup')
        
        if mBlock.ikSetup > 1:#...ribbon/spline
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
            
            """
            for i,mObj in enumerate(ml_ribbonIKDrivers):
                if not i:
                    mObj.doSnapTo(mBlock.ikStartHandle)
                else:
                    mObj.doSnapTo(mBlock.ikEndHandle)"""
            
            ml_jointsToConnect.extend(ml_ribbonIKDrivers)
            
            self.ml_ikMidControls = []            
            if self.ml_ikMidHelpers:
                for i,mHelper in enumerate(self.ml_ikMidHelpers):
                    log.debug("|{0}| >> Creating ik mid control...".format(_str_func))  
                    #Lever...
                    mMidIK = mHelper.doCreateAt('joint')#ml_rigJoints[0]
                    _nameSet = NAMETOOLS.combineDict( mBlock.getNameDict(ignore=['cgmType']))                    
                    
                    mMidIK.doStore('cgmName', '{}_midIK_{}'.format(_nameSet,i))
                    mMidIK.p_parent = False
                    mMidIK.doName()
                
                    JOINT.freezeOrientation(mMidIK.mNode)
                    
                    mRigNull.connectChildNode(mMidIK,'controlSegMid_{}_IK'.format(i),'rigNull')
                    
                    self.ml_ikMidControls.append(mMidIK)
            
            """
            #Add base joint for now...
            #if _ikSetup in ['spline','curve']:
            if mBlock.ikBaseExtend:
                log.debug("|{0}| >> Creating controlBaseExtendIK...".format(_str_func))  
                mBaseExtendIK = ml_joints[1].doCreateAt('joint')#ml_rigJoints[0]
                _nameSet = NAMETOOLS.combineDict( mBlock.getNameDict(ignore=['cgmType']))
                
                mBaseExtendIK.doStore('cgmName', '{0}_baseExtend'.format(_nameSet))
                mBaseExtendIK.p_parent = False
                mBaseExtendIK.doName()
                JOINT.freezeOrientation(mBaseExtendIK.mNode)
                
                mRigNull.connectChildNode(mBaseExtendIK,'controlBaseExtendIK','rigNull')
            
            if mBlock.ikEndExtend:
                #Add base joint for now...
                log.debug("|{0}| >> Creating controlEndExtendIK...".format(_str_func))  
                mEndExtendIK = ml_joints[-2].doCreateAt('joint')#ml_rigJoints[0]
                _nameSet = NAMETOOLS.combineDict( mBlock.getNameDict(ignore=['cgmType']))
                
                mEndExtendIK.doStore('cgmName', '{0}_endExtend'.format(_nameSet))
                mEndExtendIK.p_parent = False
                mEndExtendIK.doName()
                
                JOINT.freezeOrientation(mEndExtendIK.mNode)
                
                mRigNull.connectChildNode(mEndExtendIK,'controlEndExtendIK','rigNull')            
            """
            
        
            
        if self.str_segmentType != 'parent':#mBlock.numJoints > mBlock.numControls or self.b_squashSetup:# or str_ikSetup == 'ribbon':
            log.debug("|{0}| >> Handles...".format(_str_func))            
            ml_segmentHandles = BLOCKUTILS.skeleton_buildHandleChain(self.mBlock,'handle','handleJoints',clearType=True)
            if mBlock.ikSetup:
                for i,mJnt in enumerate(ml_segmentHandles):
                    mJnt.parent = ml_blendJoints[i]
            else:
                for i,mJnt in enumerate(ml_segmentHandles):
                    mJnt.parent = ml_fkJoints[i]        
            
            
            log.debug("|{0}| >> segment necessary...".format(_str_func))
                
            ml_segmentChain = BLOCKUTILS.skeleton_buildDuplicateChain(mBlock,ml_joints, None, mRigNull,'segmentJoints', cgmType = 'segJnt',blockNames=True)
            for i,mJnt in enumerate(ml_rigJoints):
                mJnt.parent = ml_segmentChain[i]
                mJnt.connectChildNode(ml_segmentChain[i],'driverJoint','sourceJoint')#Connect
            ml_jointsToHide.extend(ml_segmentChain)
        else:
            log.debug("|{0}| >> Simple setup. Parenting rigJoints to blend...".format(_str_func))
            ml_rigParents = ml_fkJoints
            if ml_blendJoints:
                ml_rigParents = ml_blendJoints
            for i,mJnt in enumerate(ml_rigJoints):
                mJnt.parent = ml_rigParents[i]
                
            if str_ikBase in ['hips','head']:
                log.debug("|{0}| >> Simple setup. Need single handle.".format(_str_func))
                ml_segmentHandles = BLOCKUTILS.skeleton_buildDuplicateChain(mBlock,
                                                                            ml_fkJoints, 
                                                                            'handle', mRigNull,
                                                                            'handleJoints',
                                                                            cgmType = 'handle', indices=[1])
                
            
        #Mirror if side...
        if self.d_module['mirrorDirection'] == 'Left':
            log.debug("|{0}| >> Mirror direction ...".format(_str_func))
            ml_fkAttachJoints = BUILDUTILS.joints_mirrorChainAndConnect(self, ml_fkJoints)
            ml_jointsToHide.extend(ml_fkAttachJoints)
           
        
        #...joint hide -----------------------------------------------------------------------------------
        for mJnt in ml_jointsToHide:
            try:
                mJnt.drawStyle =2
            except:
                mJnt.radius = .00001
                
        #...connect... 
        self.fnc_connect_toRigGutsVis( ml_jointsToConnect )        
        #cgmGEN.func_snapShot(vars())     
        return True
    except Exception as err:cgmGEN.cgmExceptCB(Exception,err,localDat=vars())        

#@cgmGEN.Timer
def rig_shapes(self):
    try:
        _short = self.d_block['shortName']
        _str_func = 'rig_shapes'
        log.debug("|{0}| >>  ".format(_str_func)+ '-'*80)
        log.debug(self)
        
        mBlock = self.mBlock
        mRigNull = self.mRigNull
        
        ml_formHandles = mBlock.msgList_get('formHandles')
        ml_prerigHandleTargets = mBlock.atBlockUtils('prerig_getHandleTargets')
        ml_fkJoints = mRigNull.msgList_get('fkJoints')
        ml_ikJoints = mRigNull.msgList_get('ikJoints',asMeta=True)
        ml_blendJoints = mRigNull.msgList_get('blendJoints')
        ml_rigJoints = self.mRigNull.msgList_get('rigJoints')
        
        mIKEnd = ml_prerigHandleTargets[-1]
        ml_prerigHandles = mBlock.msgList_get('prerigHandles')
        
        _side = mBlock.atUtils('get_side')
        _short_module = self.mModule.mNode
        str_ikBase = self.str_ikBase
        str_ikEnd = self.str_ikEnd
        str_ikEndShape = self.str_ikEndShape
        str_ikSetup = ATTR.get_enumValueString(mBlock.mNode,'ikSetup')        
        
        mHandleFactory = mBlock.asHandleFactory()
        mOrientHelper = ml_prerigHandles[0].orientHelper
        
        #_size = 5
        #_size = MATH.average(mHandleFactory.get_axisBox_size(ml_prerigHandles[0].mNode))
        _jointOrientation = self.d_orientation['str']
        
        ml_joints = self.d_joints['ml_moduleJoints']
        
        #Our base size will be the average of the bounding box sans the largest
        _bbSize = TRANS.bbSize_get(mBlock.getMessage('prerigLoftMesh')[0],shapes=True)
        _bbSize.remove(max(_bbSize))
        _size = MATH.average(_bbSize)        
        _offset = self.v_offset
        mCog = False
        
        #Figure out our handle targets...
        
        ml_handleTargets = ml_fkJoints
        
        ml_fkCastTargets = self.mRigNull.msgList_get('fkAttachJoints')
        if not ml_fkCastTargets:
            ml_fkCastTargets = copy.copy(ml_fkJoints)
            
            
        #...get our aim vector ----------------------------------------------------------------------
        d_orients = self.d_orientation
        _castVector = mBlock.getEnumValueString('castVector')
        _aimVector = d_orients.get('vector{0}'.format(CORESTRING.capFirst(_castVector)))        


        #controlSegMidIK... =============================================================================
        for i,mHelper in enumerate(self.ml_ikMidControls):
            RIGSHAPES.ik_segMid(self,mHelper)
            CORERIG.shapeParent_in_place(mHelper.mNode, self.ml_ikMidHelpers[i].mNode, False)
            
            
        """    
        mControlSegMidIK = mRigNull.getMessageAsMeta('controlSegMidIK')
        if mControlSegMidIK:
            RIGSHAPES.ik_segMid(self,mControlSegMidIK)
            
        
        mControlEndExtendIK = mRigNull.getMessageAsMeta('controlEndExtendIK')
        if mControlEndExtendIK:
            RIGSHAPES.ik_segMid(self,mControlEndExtendIK)
            mControlEndExtendIK.p_parent = False
            
        mControlBaseExtendIK = mRigNull.getMessageAsMeta('controlBaseExtendIK')
        if mControlBaseExtendIK:
            RIGSHAPES.ik_segMid(self,mControlBaseExtendIK)                
            mControlBaseExtendIK.p_parent = False
            """
        #Root...=============================================================================
        mRoot = RIGSHAPES.rootOrCog(self)
        
        
        #Settings...=============================================================================
        if ml_blendJoints:
            ml_targets = ml_blendJoints
        else:
            ml_targets = ml_fkCastTargets
            
        mSettings = RIGSHAPES.settings(self,mBlock.getEnumValueString('settingsPlace'),ml_targets)
        
        
        #Direct Controls...=============================================================
        RIGSHAPES.direct(self,ml_rigJoints)
        
        
        #Handles...=============================================================
        ml_handleJoints = self.mRigNull.msgList_get('handleJoints')
        if ml_handleJoints: RIGSHAPES.segment_handles(self, ml_handleJoints)        
        
        
        #FK Shapes =============================================================================
        ml_fkShapes = self.atBuilderUtils('shapes_fromCast',
                                          targets = ml_fkCastTargets,
                                          offset = _offset,
                                          aimVector = _aimVector,
                                          mode = 'frameHandle')
    
        
        if mBlock.ikSetup:
            #reload(RIGSHAPES)
            #IK Shapes=====================================================================
            #IK End ---------------------------------------------------------------------------------
            d_ikEnd = {}
            if mBlock.ikSetup:
                if str_ikEndShape == 'locator':
                    d_ikEnd = {'shapeArg':'locatorForm'}
                elif str_ikEndShape == 'cast':
                    use_ikEnd = str_ikEnd
                else:
                    d_ikEnd = {'shapeArg':str_ikEndShape}
                    
                #print str_ikEnd
                RIGSHAPES.ik_end(self,str_ikEnd,ml_handleTargets,ml_rigJoints,ml_fkShapes,ml_ikJoints,ml_fkJoints,**d_ikEnd)
        
        
            if mBlock.ikBase:
                RIGSHAPES.ik_base(self,None,ml_fkJoints,ml_fkShapes)
                
            if str_ikSetup == 'rp':
                RIGSHAPES.ik_rp(self,None,ml_ikJoints)            
            
        #FK...=======================================================================
        log.debug("|{0}| >> FK...".format(_str_func))
        #ml_fkShapesSimple = self.atBuilderUtils('shapes_fromCast',
        #                                        ml_fkCastTargets,
        #                                        offset = _offset,
        #                                        mode = 'frameHandle')        
        for i,mCrv in enumerate(ml_fkShapes):
            mJnt = ml_fkJoints[i]
            #CORERIG.match_orientation(mCrv.mNode,mJnt.mNode)
            
            if i == 0 and str_ikBase in ['hips','head']:
                log.debug("|{0}| >> FK hips. no shape on frame...".format(_str_func))
                mCrv.delete()
                continue
            else:
                mHandleFactory.color(mCrv.mNode, controlType = 'main')        
                CORERIG.shapeParent_in_place(mJnt.mNode,mCrv.mNode, False, replaceShapes=True)
                


        for mShape in ml_fkShapes:
            try:mShape.delete()
            except:pass
            
            
        #Pivots =======================================================================================
        if mBlock.getMessage('pivotHelper'):
            RIGSHAPES.pivotShapes(self,mBlock.pivotHelper)        
            
        return        
    except Exception as err:cgmGEN.cgmExceptCB(Exception,err,localDat=vars())        
    

#@cgmGEN.Timer
def rig_controls(self):
    try:
        _short = self.d_block['shortName']
        _str_func = 'rig_controls'
        log.debug("|{0}| >>  ".format(_str_func)+ '-'*80)
        log.debug(self)
        
        mBlock = self.mBlock
        mRigNull = self.mRigNull
        ml_controlsAll = []#we'll append to this list and connect them all at the end
        mRootParent = self.mDeformNull
        mSettings = mRigNull.settings
        ml_controlsIKRO = []
        
        b_cog = False
        if mBlock.getMessage('cogHelper'):
            b_cog = True
        str_ikBase = ATTR.get_enumValueString(mBlock.mNode,'ikBase')
        
        d_controlSpaces = self.atBuilderUtils('get_controlSpaceSetupDict')
        
        # Drivers ==============================================================================================
        log.debug("|{0}| >> Attr drivers...".format(_str_func))    
        if mBlock.ikSetup:
            log.debug("|{0}| >> Build IK drivers...".format(_str_func))
            mPlug_FKIK = cgmMeta.cgmAttr(mSettings.mNode,'FKIK',attrType='float',minValue=0,maxValue=1,lock=False,keyable=True)
        
        #>> vis Drivers ====================================================================================
        
        mPlug_visSub = self.atBuilderUtils('build_visModuleMD','visSub')
        mPlug_visDirect = self.atBuilderUtils('build_visModuleMD','visDirect')
        self.atBuilderUtils('build_visModuleProxy')#...proxyVis wiring
        
        mScaleRoot = mRigNull.getMessageAsMeta('scaleRoot')
        if mScaleRoot:
            mPlug_visScaleRoot = self.atBuilderUtils('build_visModuleMD','visScaleRoot',defaultValue=False)
            mPlug_visScaleRoot.p_defaultValue = False
            #mPlug_visScaleRoot.p_value = False

        # Connect to visModule ...
        ATTR.connect(self.mPlug_visModule.p_combinedShortName, 
                     "{0}.visibility".format(self.mDeformNull.mNode))        
        
        
        if not b_cog:
            mPlug_visRoot = self.atBuilderUtils('build_visModuleMD','visRoot',defaultValue=False)
            
        """
            mPlug_visRoot = cgmMeta.cgmAttr(mSettings,'visRoot', value = True,
                                            attrType='bool', defaultValue = False,
                                            keyable = False,hidden = False)
        mPlug_visDirect = cgmMeta.cgmAttr(mSettings,'visDirect', value = True,
                                          attrType='bool', defaultValue = False,
                                          keyable = False,hidden = False)"""
        
        
        #Root ==============================================================================================
        log.debug("|{0}| >> Root...".format(_str_func))
        
        if not mRigNull.getMessage('rigRoot'):
            raise ValueError("No rigRoot found")
        
        mRoot = mRigNull.rigRoot
        log.debug("|{0}| >> Found rigRoot : {1}".format(_str_func, mRoot))
        
        
        _d = MODULECONTROL.register(mRoot,
                                    addDynParentGroup = True,
                                    mirrorSide= self.d_module['mirrorDirection'],
                                    mirrorAxis="translateX,rotateY,rotateZ",
                                    makeAimable = True,
                                    **d_controlSpaces)
        
        mRoot = _d['mObj']
        mRoot.masterGroup.parent = mRootParent
        mRootParent = mRoot#Change parent going forward...
        ml_controlsAll.append(mRoot)
        
        if not b_cog:
            for mShape in mRoot.getShapes(asMeta=True):
                ATTR.connect(mPlug_visRoot.p_combinedShortName, "{0}.overrideVisibility".format(mShape.mNode))
                
                
        #Scale Root --------------------------------------------------------------------------------------
        if mScaleRoot:            
            log.debug("|{0}| >> Scale Root...".format(_str_func))
            _d = MODULECONTROL.register(mScaleRoot,
                                        addDynParentGroup = False,
                                        mirrorSide= self.d_module['mirrorDirection'],
                                        mirrorAxis="translateX,rotateY,rotateZ",
                                        makeAimable = True)
            mScaleRoot = _d['mObj']
            mRootParent = mScaleRoot#Change parent going forward...
            ml_controlsAll.append(mScaleRoot)
            
            for mShape in mScaleRoot.getShapes(asMeta=True):
                ATTR.connect(mPlug_visScaleRoot.p_combinedShortName, "{0}.overrideVisibility".format(mShape.mNode))            
            
                
        #FK controls =============================================================================================
        log.debug("|{0}| >> FK Controls...".format(_str_func))
        ml_fkJoints = self.mRigNull.msgList_get('fkJoints')
        
        if str_ikBase in ['hips','head']:
            p_pelvis = ml_fkJoints[0].p_position
            ml_fkJoints = ml_fkJoints[1:]
        
        ml_fkJoints[0].parent = mRoot
        ml_controlsAll.extend(ml_fkJoints)
        
        if self.d_module['mirrorDirection'] == 'Centre':
            _fkMirrorAxis = 'translateY,translateZ,rotateY,rotateZ'
        else:
            _fkMirrorAxis = "translateX,translateY,translateZ"
    
        
        for i,mObj in enumerate(ml_fkJoints):
            d_buffer = MODULECONTROL.register(mObj,
                                              mirrorSide= self.d_module['mirrorDirection'],
                                              mirrorAxis=_fkMirrorAxis,
                                              makeAimable = True)
    
            mObj = d_buffer['mObj']
            ATTR.set_hidden(mObj.mNode,'radius',True)
            if mBlock.ikSetup:
                self.atUtils('get_switchTarget', mObj, mObj.getMessage('blendJoint'))                
        
        #ControlIK ========================================================================================
        mControlIK = False
        ml_blend = mRigNull.msgList_get('blendJoints')
        ml_controlsIK = []
        
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
            
            #Register our snapToTarget -------------------------------------------------------------
            self.atUtils('get_switchTarget', mControlIK,ml_blend[self.int_handleEndIdx])
            
            ml_controlsIK.append(mControlIK)
            
            
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
            ml_controlsIK.insert(0,mControlBaseIK)
            
            #Register our snapToTarget -------------------------------------------------------------
            self.atUtils('get_switchTarget', mControlBaseIK,ml_blend[0])
            
            if str_ikBase in ['hips','head'] and mBlock.scaleSetup:
                log.info("|{0}| >> Scale Pivot setup...".format(_str_func))
                TRANS.scalePivot_set(mControlBaseIK.mNode, p_pelvis)                
            

            
        #Mid controls ====================
        if self.ml_ikMidControls:
            log.debug("|{0}| >> Found midIKControls".format(_str_func))            
            d_mid = copy.copy(d_controlSpaces)
            if d_mid.get('addSpacePivots'):d_mid.pop('addSpacePivots')
            for mHandle in self.ml_ikMidControls:
                _d = MODULECONTROL.register(mHandle,
                                            addDynParentGroup = True, 
                                            mirrorSide= self.d_module['mirrorDirection'],
                                            mirrorAxis="translateX,rotateY,rotateZ",
                                            makeAimable = True,
                                            **d_mid)
                
                
                mNew = _d['mObj']
                mNew.masterGroup.parent = mRootParent
                ml_controlsAll.append(mNew)            
                ml_controlsIK.insert(-1,mNew)
            
            
        """
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
        
        
        
        
        l_extends = ['controlEndExtendIK','controlBaseExtendIK']
        for k in l_extends:
            mControl = mRigNull.getMessageAsMeta(k)
            if mControl:
                log.debug("|{0}| >> Found : {1}".format(_str_func, k))
        
                _d = MODULECONTROL.register(mControl,
                                            addDynParentGroup = False,
                                            mirrorSide= self.d_module['mirrorDirection'],
                                            mirrorAxis="translateX,rotateY,rotateZ",
                                            makeAimable = True)
                
                mControl = _d['mObj']
                if k == 'controlEndExtendIK':
                    mControl.masterGroup.parent = mControlIK
                else:
                    mControl.masterGroup.parent = mControlBaseIK or mRoot
                    
                ml_controlsAll.append(mControl)
                ml_controlsIKRO.append(mControl)

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
            self.atUtils('get_switchTarget', mControlSegMidIK, ml_blend[ MATH.get_midIndex(len(ml_blend))])"""
    
    
        if mSettings and self.str_settingsPlace != 'cog':#>> settings ==========================================
            log.debug("|{0}| >> Settings : {1}".format(_str_func, mSettings))
            
            MODULECONTROL.register(mSettings,
                                   mirrorSide= self.d_module['mirrorDirection'],
                                   )
        
            #ml_blendJoints = self.mRigNull.msgList_get('blendJoints')
            #if ml_blendJoints:
            #    mSettings.masterGroup.parent = ml_blendJoints[-1]
            #else:
            #    mSettings.masterGroup.parent = ml_fkJoints[-1]
        
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
            
                
        # Pivots =================================================================================================
        if mBlock.getMessage('pivotHelper'):
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
                
        #>> Direct Controls ==================================================================================
        log.debug("|{0}| >> Direct controls...".format(_str_func))
        
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
                    
        
        #self.atBuilderUtils('check_nameMatches', ml_controlsAll)
        
        mHandleFactory = mBlock.asHandleFactory()
        for mCtrl in ml_controlsAll:
            if 'fk' in mCtrl.p_nameBase:
                ATTR.set(mCtrl.mNode,'rotateOrder',self.rotateOrder_FK)
                
            else:
                ATTR.set(mCtrl.mNode,'rotateOrder',self.rotateOrder_IK)
            
            if mCtrl.hasAttr('radius'):
                ATTR.set(mCtrl.mNode,'radius',0)        
            
            ml_pivots = mCtrl.msgList_get('spacePivots')
            if ml_pivots:
                log.debug("|{0}| >> Coloring spacePivots for: {1}".format(_str_func,mCtrl))
                for mPivot in ml_pivots:
                    mHandleFactory.color(mPivot.mNode, controlType = 'sub')        
                    ml_controlsAll.append(mPivot)
                    mPivot.constraintGroup.p_parent = self.d_module['mMasterNull'].spacePivotsGroup
    
        
        #ml_controlsAll = self.atBuilderUtils('register_mirrorIndices', ml_controlsAll)
        mRigNull.msgList_connect('controlsAll',ml_controlsAll)
        mRigNull.moduleSet.extend(ml_controlsAll)
        mRigNull.msgList_connect('controlsIK',ml_controlsIK)
        
        return 
    except Exception as err:cgmGEN.cgmExceptCB(Exception,err,localDat=vars())        


#@cgmGEN.Timer
def rig_segments(self):
    cgmGEN._reloadMod(DIST)
    cgmGEN._reloadMod(IK)
    _short = self.d_block['shortName']
    _str_func = 'rig_segments'
    log.debug("|{0}| >>  ".format(_str_func)+ '-'*80)
    log.debug(self)    

    
    mBlock = self.mBlock
    mRigNull = self.mRigNull
    ml_rigJoints = mRigNull.msgList_get('rigJoints')
    ml_segJoints = mRigNull.msgList_get('segmentJoints')
    mModule = self.mModule
    
    try:mRoot = mRigNull.scaleRoot
    except:mRoot = mRigNull.rigRoot
        
    if len(ml_rigJoints)<2:
        log.debug("|{0}| >> Not enough rig joints for setup".format(_str_func))                      
        return True
    
    
    mRootParent = self.mDeformNull
    if not ml_segJoints:
        log.debug("|{0}| >> No segment joints. No segment setup necessary.".format(_str_func))
        return True
    
    ml_handleJoints = mRigNull.msgList_get('handleJoints')
    
    for mJnt in ml_segJoints:
        mJnt.drawStyle = 2
        ATTR.set(mJnt.mNode,'radius',0)
    
    if self.str_segmentType == 'parent':#len(ml_segJoints) == len(ml_handleJoints):
        for i,mJnt in enumerate(ml_segJoints):
            mJnt.p_parent = ml_handleJoints[i]
            if self.b_squashSetup:
                mJnt.segmentScaleCompensate = False
            
        
    else:
        #>> Ribbon setup ========================================================================================
        log.debug("|{0}| >> Ribbon setup...".format(_str_func))
        
        _settingsControl = mRigNull.settings.mNode
        
        _extraSquashControl = mBlock.squashExtraControl
               
        res_segScale = self.UTILS.get_blockScale(self,'segMeasure')
        mPlug_masterScale = res_segScale[0]
        mMasterCurve = res_segScale[1]
        self.fnc_connect_toRigGutsVis( mMasterCurve )

        
        _d = {'jointList':[mObj.mNode for mObj in ml_segJoints],
              'baseName':'{0}_rigRibbon'.format(self.d_module['partName']),
              'connectBy':'constraint',
              'extendEnds':mBlock.ribbonExtendEnds,#False,#True,
              #'sectionSpans':1,
              'paramaterization':mBlock.getEnumValueString('ribbonParam'),          
              'masterScalePlug':mPlug_masterScale,
              'influences':ml_handleJoints,
              'settingsControl':_settingsControl,
              'attachStartToInfluence':False,
              'attachEndToInfluence':False,#True,#for autoswim
              'parentDeformTo':mRoot,
              'squashFactorMode':self.str_squashFactorMode,
              'driverSetup':mBlock.getEnumValueString('ribbonAim'),
              'skipAim':mBlock.squashSkipAim,
              'moduleInstance':mModule}
        
        
        if self.str_ribbonAttachEndsToInfluence == 'both':
            _d['attachEndsToInfluences'] = True
        elif self.str_ribbonAttachEndsToInfluence == 'start':
            _d['attachStartToInfluence'] = True
        elif self.str_ribbonAttachEndsToInfluence == 'end':
            _d['attachEndToInfluence'] = True
            
        #if mBlock.getEnumValueString('ikBase') in ['hips','head']:
        #    _d['attachStartToInfluence'] = True
            
        if mBlock.special_swim:
            _d['attachStartToInfluence'] = False
            _d['attachEndToInfluence'] = False
            
            
            
        cgmGEN._reloadMod(IK)

        
        _d.update(self.d_squashStretch)
        

        
        if self.str_segmentType in ['ribbon','ribbonLive']:
            if self.str_segmentStretchBy == 'scale':
                _d['setupAimScale'] = True
            else:
                _d['setupAimScale'] = False
                
                
            _d['liveSurface'] = False if self.str_segmentType == 'ribbon' else True
            #log.info(cgmGEN.logString_sub,_str_func,"segment dict...")
            #_d['sectionSpans'] = 6
            pprint.pprint(_d)
            res_ribbon = IK.ribbon(**_d)
            ml_surfaces = res_ribbon['mlSurfaces']
            
        elif self.str_segmentType == 'spline':
            """
            _l_segJoints = _d['jointList']
            _ml_segTmp = cgmMeta.asMeta(_l_segJoints)
            for i,mJnt in enumerate(ml_segJoints[1:]):
                mJnt.p_parent = ml_segJoints[i]
                
            mIKBaseControl = mRigNull.getMessageAsMeta('controlIKBase')
            mIKControl = mRigNull.getMessageAsMeta('controlIK')
            mSettings = mRigNull.getMessageAsMeta('settings')
            
            RIGFRAME.spline(self,_ml_segTmp, None, mIKControl, mIKBaseControl,
                            ml_handleJoints, mPlug_masterScale, 'translate',
                            mBlock.ikSplineTwistEndConnect, mBlock.ikSplineExtendEnd, mBlock.ikSplineAimEnd, mSettings)
            """
            
            
            _l_segJoints = _d['jointList']
            _ml_segTmp = cgmMeta.asMeta(_l_segJoints)
            for i,mJnt in enumerate(ml_segJoints[1:]):
                mJnt.p_parent = ml_segJoints[i]
                
            #mIKBaseControl = mRigNull.getMessageAsMeta('controlIKBase')
            #mIKControl = mRigNull.getMessageAsMeta('controlIK')
            mSettings = mRigNull.getMessageAsMeta('settings')
            

                
            mIKSplineEnd = ml_segJoints[-1].doDuplicate()
            mIKSplineEnd.rename("{}_splineEnd".format(ml_segJoints[-1].p_nameBase))
            
            ml_ikUse = copy.copy(ml_segJoints)
            ml_ikUse[-1] = mIKSplineEnd
            
            mIKSplineEnd.p_parent = ml_segJoints[-1].p_parent
            
            ml_segJoints[-1].p_parent =  ml_handleJoints[-1]#...to get free orient
            
            pprint.pprint(ml_segJoints)
            RIGFRAME.spline(self,ml_ikUse, None, ml_handleJoints[-1], ml_handleJoints[0],
                            ml_handleJoints, mPlug_masterScale, self.str_segmentStretchBy,
                            mBlock.ikSplineTwistEndConnect, mBlock.ikSplineExtendEnd, mBlock.ikSplineAimEnd, mSettings)
            
            if mSettings.hasAttr('twistType'):
                ATTR.set_default(mSettings.mNode,'twistType',1)
                ATTR.set(mSettings.mNode,'twistType',1)
                
                
            mc.pointConstraint([mIKSplineEnd.mNode], ml_segJoints[-1].mNode, maintainOffset = True)
            mIKSplineIKDriver = ml_segJoints[-1].doDuplicate()
            mIKSplineIKDriver.rename("{}_splineControl".format(ml_segJoints[-1].p_nameBase))
            mIKSplineIKDriver.p_parent =  ml_handleJoints[-1]
            mIKSplineEnd.dagLock()

            
            #Add follow setup here 07.10.22
            mPlug_followIK = cgmMeta.cgmAttr(ml_handleJoints[-1].mNode,'followEnd',attrType='float',lock=False,keyable=True,defaultValue=1.0)
            mPlug_followIK.p_value = 1.0
            
            #Setup blend ----------------------------------------------------------------------------------
            RIGCONSTRAINT.blendChainsBy(mIKSplineEnd,mIKSplineIKDriver,ml_segJoints[-1],
                                        driver = mPlug_followIK.p_combinedName,
                                        l_constraints=['orient'])                                
            


            ATTR.set_default(mSettings.mNode,'twistType',1)
            ATTR.set(mSettings.mNode,'twistType',1)
        else:
            _l_segJoints = _d['jointList']
            _ml_segTmp = cgmMeta.asMeta(_l_segJoints)
            _d['setupAim'] = 1                
            if self.str_segmentStretchBy == 'scale':
                _d['setupAimScale'] = True
            #_d['attachEndToInfluence'] = False                
            pprint.pprint(_d)
            IK.curve(**_d)


        
        mMasterCurve.p_parent = mRoot

        #cgmGEN.func_snapShot(vars())
        ml_segJoints[0].parent = mRoot
    
        for mJnt in ml_segJoints:
            if self.b_squashSetup:
                mJnt.segmentScaleCompensate = False
            if mJnt == ml_segJoints[0]:
                continue
            print(mJnt)
            if self.str_segmentType not in ['spline']:
                mJnt.p_parent =ml_segJoints[0].p_parent
        log.debug('ribbon done')
    log.debug("done")

    
#@cgmGEN.Timer
def rig_frame(self):
    try:
        _short = self.d_block['shortName']
        _str_func = 'rig_rigFrame'.format(_short)
        log.debug("|{0}| >>  ".format(_str_func)+ '-'*80)
        log.debug(self)        
        mBlock = self.mBlock
        mRigNull = self.mRigNull
        mRootParent = self.mDeformNull
        mModule = self.mModule
        cgmGEN._reloadMod(IK)
        ml_rigJoints = mRigNull.msgList_get('rigJoints')
        ml_fkJoints = mRigNull.msgList_get('fkJoints')
        ml_handleJoints = mRigNull.msgList_get('handleJoints')
        ml_baseIKDrivers = mRigNull.msgList_get('baseIKDrivers')
        ml_blendJoints = mRigNull.msgList_get('blendJoints')
        mPlug_globalScale = self.d_module['mPlug_globalScale']
        
        
        try:mRoot = mRigNull.scaleRoot
        except:mRoot = mRigNull.rigRoot
        
        mSettings = mRigNull.settings
        
        b_cog = False
        if mBlock.getMessage('cogHelper'):
            b_cog = True
        str_ikBase = ATTR.get_enumValueString(mBlock.mNode,'ikBase')        
        
        mIKBaseControl = mRigNull.getMessageAsMeta('controlIKBase')
        mIKControl = mRigNull.getMessageAsMeta('controlIK')
            
        mIKHandleDriver = mIKControl
        
        
        log.debug("|{0}| >> segmentScale measure...".format(_str_func))
        res_segScale = self.UTILS.get_blockScale(self,'segMeasure')
        mPlug_masterScale = res_segScale[0]
        mMasterCurve = res_segScale[1]
        mMasterCurve.p_parent = mRoot
        self.fnc_connect_toRigGutsVis( mMasterCurve )
        
        
        if mBlock.parentToDriver:
            log.debug("|{0}| >> Parent to driver".format(_str_func))
            self.mDeformNull.p_parent = self.md_dynTargetsParent['attachDriver'].mNode                
        
        #>> handleJoints =====================================================================================
        if ml_handleJoints:
            log.debug("|{0}| >> Handles setup...".format(_str_func))
            ml_handleParents = ml_fkJoints
            if ml_blendJoints:
                log.debug("|{0}| >> Handles parent: blend".format(_str_func))
                ml_handleParents = ml_blendJoints
            
            RIGFRAME.segment_handles(self,ml_handleJoints,ml_handleParents,
                                     mIKBaseControl,mRoot,str_ikBase)
           
            
       
        #>> Build IK ======================================================================================
        if mBlock.ikSetup:
            _ikSetup = mBlock.getEnumValueString('ikSetup')
            log.debug("|{0}| >> IK Type: {1}".format(_str_func,_ikSetup))    
        
            if not mRigNull.getMessage('rigRoot'):
                raise ValueError("No rigRoot found")
            if not mRigNull.getMessage('controlIK'):
                raise ValueError("No controlIK found")            
            
            ml_ikJoints = mRigNull.msgList_get('ikJoints')
            mPlug_FKIK = cgmMeta.cgmAttr(mSettings.mNode,'FKIK',attrType='float',lock=False,keyable=True)
            _jointOrientation = self.d_orientation['str']
            
            mStart = ml_ikJoints[0]
            mEnd = ml_ikJoints[-1]
            _start = ml_ikJoints[0].mNode
            _end = ml_ikJoints[-1].mNode            
            
            #>>> Setup a vis blend result
            mPlug_FKon = cgmMeta.cgmAttr(mSettings,'result_FKon',attrType='float',defaultValue = 0,keyable = False,lock=True,hidden=True)	
            mPlug_IKon = cgmMeta.cgmAttr(mSettings,'result_IKon',attrType='float',defaultValue = 0,keyable = False,lock=True,hidden=True)	
        
            NODEFACTORY.createSingleBlendNetwork(mPlug_FKIK.p_combinedName,
                                                 mPlug_IKon.p_combinedName,
                                                 mPlug_FKon.p_combinedName)
            
            #IK =====================================================================
            mIKGroup = mRoot.doCreateAt()
            mIKGroup.doStore('cgmTypeModifier','ik')
            mIKGroup.doName()
            
            mPlug_IKon.doConnectOut("{0}.visibility".format(mIKGroup.mNode))
            
            mIKGroup.parent = mRoot
            mIKGroup.dagLock(True)
            mIKControl.masterGroup.parent = mIKGroup
            
            mIKBaseControl = False
            mSpinGroup = False
            def get_spinGroup(self):
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
                return mSpinGroup
                
            if mRigNull.getMessage('controlIKBase'):
                mIKBaseControl = mRigNull.controlIKBase
                
                if str_ikBase in ['hips','head']:
                    mIKBaseControl.masterGroup.parent = mRoot
                else:
                    mIKBaseControl.masterGroup.parent = mIKGroup
                    
                    mBaseOrientGroup = cgmMeta.validateObjArg(mIKBaseControl.doGroup(True,False,asMeta=True,typeModifier = 'aim'),'cgmObject',setClass=True)
                    ATTR.set(mBaseOrientGroup.mNode, 'rotateOrder', _jointOrientation)
                
                    mLocBase = mIKBaseControl.doCreateAt()
                    mLocAim = mIKBaseControl.doCreateAt()
                
                    mLocAim.doStore('cgmType','aimDriver')
                    mLocBase.doStore('cgmType','baseDriver')
                
                
                    for mObj in mLocBase,mLocAim:
                        mObj.doStore('cgmName',mIKBaseControl.mNode)                        
                        mObj.doName()
                        
                                    
                    mLocAim.p_parent = mIKBaseControl.dynParentGroup
                
                    mAimTarget = mIKControl
                    """
                                        _direction = self.d_module['direction'] or 'center'
                                        if _direction.lower() == 'left':
                                            v_aim = [0,0,1]
                                        else:
                                            v_aim = [0,0,-1]"""
                
                    mc.aimConstraint(mAimTarget.mNode, mLocAim.mNode, maintainOffset = True,
                                     aimVector = [0,0,1], upVector = [0,1,0], 
                                     worldUpObject = mIKBaseControl.dynParentGroup.mNode,
                                     worldUpType = 'objectrotation', 
                                     worldUpVector = self.v_twistUp)
                
                
                    mLocBase.p_parent = mIKBaseControl.dynParentGroup
                
                
                    const = mc.orientConstraint([mLocAim.mNode,mLocBase.mNode],
                                                mBaseOrientGroup.mNode, maintainOffset = True)[0]
                
                    d_blendReturn = NODEFACTORY.createSingleBlendNetwork([mIKBaseControl.mNode,
                                                                          'aim'],
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
                    #ATTR.set_default(mIKBaseControl.mNode, 'aim', .5)
                    #mIKBaseControl.extendIK = 0.0
                    mIKBaseControl.p_parent = mBaseOrientGroup                    
                    
                    
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
                
                mSpinGroup.dagLock(True)

            if _ikSetup == 'rp':
                RIGFRAME.ik_rp(self,mStart,mEnd,ml_ikJoints,
                               mIKControl,mIKBaseControl,mIKHandleDriver,
                               mRoot,mIKGroup)                

            elif _ikSetup in ['spline','curve']:# ==============================================================================
                log.debug("|{0}| >> {1} setup...".format(_str_func,_ikSetup))
                
                ml_ribbonIkHandles = mRigNull.msgList_get('ribbonIKDrivers')
                if not ml_ribbonIkHandles:
                    raise ValueError("No ribbon IKDriversFound")
                
                ml_skinDrivers = copy.copy(ml_ribbonIkHandles)
                max_influences = 2
                
                ml_segMidDrivers = copy.copy(ml_ribbonIkHandles)
                    
                #Mid controls ====================
                if self.ml_ikMidControls:
                    RIGFRAME.segment_mid(self,self.ml_ikMidControls,
                                         ml_segMidDrivers,mIKGroup,
                                         mIKBaseControl,mIKControl,ml_ikJoints)
                    ml_skinDrivers = [ml_skinDrivers[0]] + self.ml_ikMidControls + [ml_skinDrivers[-1]]
                    max_influences+=len(self.ml_ikMidControls)                    
                    
                

                if mIKBaseControl:
                    ml_ribbonIkHandles[0].parent = mIKBaseControl
                else:

                    ml_ribbonIkHandles[0].parent = mSpinGroup
                    
                ml_ribbonIkHandles[-1].parent = mIKControl
                
                if _ikSetup == 'spline':
                    '''
                    reload(RIGFRAME)
                    RIGFRAME.spline(self,ml_ikJoints,ml_ribbonIkHandles,mIKControl,mIKBaseControl,
                                    ml_skinDrivers,mPlug_masterScale, 'translate',
                                    mBlock.ikSplineTwistEndConnect, mBlock.ikSplineExtendEnd, mBlock.ikSplineAimEnd,
                                    mSettings)
    
                    ATTR.set_default(mSettings.mNode,'twistType',1)
                    ATTR.set(mSettings.mNode,'twistType',1)'''
                    for i,mJnt in enumerate(ml_ikJoints[1:]):
                        mJnt.p_parent = ml_ikJoints[i]
                        
                    mIKSplineEnd = ml_ikJoints[-1].doDuplicate()
                    mIKSplineEnd.rename("{}_splineEnd".format(ml_ikJoints[-1].p_nameBase))
                    
                    ml_ikUse = copy.copy(ml_ikJoints)
                    ml_ikUse[-1] = mIKSplineEnd
                    
                    mIKSplineEnd.p_parent = ml_ikJoints[-1].p_parent
                    
                    ml_ikJoints[-1].p_parent = mIKControl#...to get free orient
                    
                    #pprint.pprint(ml_ikJoints)
                    RIGFRAME.spline(self,ml_ikUse,
                                    ml_ribbonIkHandles,
                                    mIKControl,mIKBaseControl,
                                    ml_skinDrivers,
                                    mPlug_masterScale,
                                    'translate',
                                    mBlock.ikSplineTwistEndConnect,
                                    mBlock.ikSplineExtendEnd,
                                    mBlock.ikSplineAimEnd,
                                    mSettings = mSettings)
                    
                    if mSettings.hasAttr('twistType'):
                        ATTR.set_default(mSettings.mNode,'twistType',1)
                        ATTR.set(mSettings.mNode,'twistType',1)
                        
                        
                    mc.pointConstraint([mIKSplineEnd.mNode], ml_ikJoints[-1].mNode, maintainOffset = True)
                    mIKSplineIKDriver = ml_ikJoints[-1].doDuplicate()
                    mIKSplineIKDriver.rename("{}_splineControl".format(ml_ikJoints[-1].p_nameBase))
                    mIKSplineIKDriver.p_parent = mIKControl
                    #mIKSplineEnd.dagLock()#....why did I think locking this was a good idea
                    #...this orient here isn't what we want?
                    #mc.orientConstraint([mIKSplineEnd.mNode], ml_ikJoints[-1].mNode, maintainOffset = True)                    
                    
                    #mc.orientConstraint([mIKControl.mNode], ml_ikJoints[-1].mNode, maintainOffset = True)
                    
                    #Add follow setup here 07.10.22
                    mPlug_followIK = cgmMeta.cgmAttr(mIKControl.mNode,'followIK',attrType='float',lock=False,keyable=True,defaultValue=1.0)
                    mPlug_followIK.p_value = 1.0
                    
                    #Setup blend ----------------------------------------------------------------------------------
                    RIGCONSTRAINT.blendChainsBy(mIKSplineEnd,mIKSplineIKDriver,ml_ikJoints[-1],
                                                driver = mPlug_followIK.p_combinedName,
                                                l_constraints=['orient'])                    
                    
                    
                else:
                    _d_ribbonShare = {'connectBy':'constraint',
                                      'extendEnds':True,
                                      'settingsControl':mSettings.mNode,
                                      'moduleInstance':mModule}
                    _d_ribbonShare.update(self.d_squashStretch)                    
                    
                    
                    _d = {'jointList':[mObj.mNode for mObj in ml_ikJoints],
                          'baseName' : "{0}_ikCrv".format(ml_blendJoints[0].cgmName),
                          'masterScalePlug':mPlug_masterScale,
                          'paramaterization':mBlock.getEnumValueString('ribbonParam'),                            
                          'influences':[mHandle.mNode for mHandle in ml_skinDrivers],
                          }            
                    
                    _d.update(_d_ribbonShare)
                    
                    #pprint.pprint(_d)
                    _d['parentDeformTo'] = mIKGroup
                    _d['setupAim'] = 1
                    
                    cgmGEN._reloadMod(IK)
                    #_l_segJoints = _d['jointList']
                    #_ml_segTmp = cgmMeta.asMeta(_l_segJoints)                                    
                    IK.curve(**_d)                                    

                
                
            elif _ikSetup in ['ribbon','ribbonLive']:#===============================================================================
                log.debug("|{0}| >> ribbon setup...".format(_str_func))
                ml_ribbonIkHandles = mRigNull.msgList_get('ribbonIKDrivers')
                if not ml_ribbonIkHandles:
                    raise ValueError("No ribbon IKDriversFound")
                ml_skinDrivers = copy.copy(ml_ribbonIkHandles)
                max_influences = 2
                
                
                #log.debug("|{0}| >> segmentScale measure...".format(_str_func))
                #res_segScale = self.UTILS.get_blockScale(self,'segMeasure')
                #mPlug_masterScale = res_segScale[0]
                #mMasterCurve = res_segScale[1]
                
                ml_segMidDrivers = copy.copy(ml_ribbonIkHandles)
                    
                #Mid controls ====================
                if self.ml_ikMidControls:
                    RIGFRAME.segment_mid(self,self.ml_ikMidControls,
                                         ml_segMidDrivers,mIKGroup,
                                         mIKBaseControl,mIKControl,ml_ikJoints)
                    ml_skinDrivers = [ml_skinDrivers[0]] + self.ml_ikMidControls + [ml_skinDrivers[-1]]
                    max_influences+=len(self.ml_ikMidControls)                              
                
                    
                    
                cgmGEN._reloadMod(IK)
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
                
                
                if not  mRigNull.msgList_get('segmentJoints') and ml_handleJoints:
                    ml_skinDrivers.extend(ml_handleJoints)
                     

                d_ik = {'jointList':[mObj.mNode for mObj in ml_ikJoints],
                        'baseName' : self.d_module['partName'] + '_ikRibbon',
                        'driverSetup':mBlock.getEnumValueString('ribbonAim'),
                        'squashStretch':None,
                        'connectBy':'constraint',
                        'squashStretchMain':'arcLength',
                        'extendEnds':mBlock.ribbonExtendEnds,
                        'paramaterization':mBlock.getEnumValueString('ribbonParam'),
                        #masterScalePlug:mPlug_masterScale,
                        'settingsControl': mSettings.mNode,
                        'extraSquashControl':True,
                        'liveSurface':False if _ikSetup == 'ribbon' else True,
                        'influences':ml_skinDrivers,
                        'moduleInstance' : self.mModule}
                
                if self.str_ribbonAttachEndsToInfluence == 'both':
                    d_ik['attachEndsToInfluences'] = True
                elif self.str_ribbonAttachEndsToInfluence == 'start':
                    d_ik['attachStartToInfluences'] = True
                elif self.str_ribbonAttachEndsToInfluence == 'end':
                    d_ik['attachEndToInfluences'] = True
                    
                
                #if str_ikBase in ['hips','head']:
                #    d_ik['attachEndsToInfluences'] = True
                    
                #if mBlock.numControls == mBlock.numJoints:
                    #d_ik['paramaterization'] = 'fixed'
                    
                
                d_ik.update(self.d_squashStretchIK)
                res_ribbon = IK.ribbon(**d_ik)
                    
                const = ml_ikJoints[-1].getConstraintsTo(asMeta=True)
                for mConst in const:
                    mConst.delete()
                mc.parentConstraint([mIKControl.mNode], ml_ikJoints[-1].mNode, maintainOffset = True)
                
                """
                #...ribbon skinCluster ---------------------------------------------------------------------
                log.debug("|{0}| >> ribbon skinCluster...".format(_str_func))

                
                
                mSkinCluster = cgmMeta.validateObjArg(mc.skinCluster ([mHandle.mNode for mHandle in ml_skinDrivers],
                                                                      mSurf.mNode,
                                                                      tsb=True,
                                                                      maximumInfluences = max_influences,
                                                                      normalizeWeights = 1,dropoffRate=10),
                                                      'cgmNode',
                                                      setClass=True)
            
                mSkinCluster.doStore('cgmName', mSurf)
                mSkinCluster.doName()    
                
                #Tighten the weights...
                #reload(CORESKIN)
                CORESKIN.surface_tightenEnds(mSurf.mNode, ml_ribbonIkHandles[0].mNode,
                                             ml_ribbonIkHandles[-1].mNode, blendLength=5)"""
                
            else:
                raise ValueError("Not implemented {0} ik setup".format(_ikSetup))
            
            
            #Parent --------------------------------------------------
            #Fk...
            if str_ikBase in ['hips','head']:
                mPlug_FKon.doConnectOut("{0}.visibility".format(ml_fkJoints[1].masterGroup.mNode))
                ml_fkJoints[0].p_parent = mIKBaseControl
            else:
                mPlug_FKon.doConnectOut("{0}.visibility".format(ml_fkJoints[0].masterGroup.mNode))            
            
            
            ml_blendJoints[0].parent = mRoot
            if _ikSetup == 'spline':
                ml_ikJoints[0].parent = mIKBaseControl.masterGroup.p_parent
            else:
                ml_ikJoints[0].parent = mIKBaseControl
            
            ml_fkAttachJoints = []
            for mObj in ml_fkJoints:
                mAttach = mObj.getMessageAsMeta('fkAttach')
                ml_fkAttachJoints.append(mAttach or mObj)
                
            #Pivot Setup ========================================================================================
            if mBlock.getMessage('pivotHelper'):
                log.info("|{0}| >> Pivot setup...".format(_str_func))
                
                mPivotResultDriver = ml_ikJoints[0].doCreateAt()
                mPivotResultDriver.addAttr('cgmName','pivotResult')
                mPivotResultDriver.addAttr('cgmType','driver')
                mPivotResultDriver.doName()
                
                mPivotResultDriver.addAttr('cgmAlias', 'PivotResult')
                
                mRigNull.connectChildNode(mPivotResultDriver,'pivotResultDriver','rigNull')#Connect    
         
                mBlock.atBlockUtils('pivots_setup',
                                    mControl = mSettings,
                                    mRigNull = mRigNull,
                                    pivotResult = mPivotResultDriver,
                                    rollSetup = 'default',
                                    front = 'front',
                                    back = 'back')#front, back to clear the toe, heel defaults
                
                
                        
            

            #Setup blend ----------------------------------------------------------------------------------
            if self.b_scaleSetup and _ikSetup in ['ribbon','curve']:
                log.debug("|{0}| >> scale blend chain setup...".format(_str_func))                
                RIGCONSTRAINT.blendChainsBy(ml_fkAttachJoints,ml_ikJoints,ml_blendJoints,
                                            driver = mPlug_FKIK.p_combinedName,
                                            l_constraints=['point','orient','scale'])
                
                
                #Scale setup for ik joints                
                if _ikSetup not in ['curve']:
                    ml_ikScaleTargets = [mIKControl]
    
                    if mIKBaseControl:
                        mc.scaleConstraint(mIKBaseControl.mNode, ml_ikJoints[0].mNode,maintainOffset=True)
                        ml_ikScaleTargets.append(mIKBaseControl)
                    else:
                        mc.scaleConstraint(mRoot.mNode, ml_ikJoints[0].mNode,maintainOffset=True)
                        ml_ikScaleTargets.append(mRoot)
                        
                    mc.scaleConstraint(mIKControl.mNode, ml_ikJoints[-1].mNode,maintainOffset=True)
                    
                    _targets = [mHandle.mNode for mHandle in ml_ikScaleTargets]
                    
                    #Scale setup for mid set IK
                    """
                    if mSegMidIK:
                        mMasterGroup = mSegMidIK.masterGroup
                        _vList = DIST.get_normalizedWeightsByDistance(mMasterGroup.mNode,_targets)
                        _scale = mc.scaleConstraint(_targets,mMasterGroup.mNode,maintainOffset = True)#Point contraint loc to the object
                        CONSTRAINT.set_weightsByDistance(_scale[0],_vList)                
                        ml_ikScaleTargets.append(mSegMidIK)
                        _targets = [mHandle.mNode for mHandle in ml_ikScaleTargets]
                        """
                    for mJnt in ml_ikJoints[1:-1]:
                        _vList = DIST.get_normalizedWeightsByDistance(mJnt.mNode,_targets)
                        _scale = mc.scaleConstraint(_targets,mJnt.mNode,maintainOffset = True)#Point contraint loc to the object
                        CONSTRAINT.set_weightsByDistance(_scale[0],_vList)
                
                for mJnt in ml_ikJoints[1:]:
                    mJnt.p_parent = mIKGroup
                    mJnt.segmentScaleCompensate = False
                    
                for mJnt in ml_blendJoints:
                    mJnt.segmentScaleCompensate = False
                    if mJnt == ml_blendJoints[0]:
                        continue
                    mJnt.p_parent = ml_blendJoints[0].p_parent
                
                
            else:
                RIGCONSTRAINT.blendChainsBy(ml_fkAttachJoints,ml_ikJoints,ml_blendJoints,
                                            driver = mPlug_FKIK.p_combinedName,
                                            l_constraints=['point','orient'])
        

        #cgmGEN.func_snapShot(vars())
        return    
    except Exception as err:cgmGEN.cgmExceptCB(Exception,err,localDat=vars())        

##@cgmGEN.Timer
def rig_matchSetup(self):
    try:
        _short = self.d_block['shortName']
        _str_func = 'rig_matchSetup'.format(_short)
        log.debug("|{0}| >>  ".format(_str_func)+ '-'*80)
        log.debug(self)        
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
            raise ValueError("|{0}| >> All chains must equal length. fk:{1} | ik:{2} | blend:{2}".format(_str_func,len_fk,len_ik,len_blend))
        
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
        
    except Exception as err:cgmGEN.cgmExceptCB(Exception,err,localDat=vars())        
    
def rig_cleanUp(self):
    try:
        _short = self.d_block['shortName']
        _str_func = 'rig_cleanUp'
        log.debug("|{0}| >>  ".format(_str_func)+ '-'*80)
        log.debug(self)
        
         
    
        mRigNull = self.mRigNull
        mSettings = mRigNull.settings
        
        mRoot = mRigNull.rigRoot
        mScaleRoot = mRigNull.getMessageAsMeta('scaleRoot')
        
        mBlock = self.mBlock
        b_ikOrientToWorld = mBlock.ikOrientToWorld
        
        mRootParent = self.mDeformNull
        mMasterControl= self.d_module['mMasterControl']
        mMasterDeformGroup= self.d_module['mMasterDeformGroup']    
        mMasterNull = self.d_module['mMasterNull']
        mModuleParent = self.d_module['mModuleParent']
        mPlug_globalScale = self.d_module['mPlug_globalScale']
        
        #if not self.mConstrainNull.hasAttr('cgmAlias'):
            #self.mConstrainNull.addAttr('cgmAlias','{0}_rootNull'.format(self.d_module['partName']))
        
        mAttachDriver = self.md_dynTargetsParent['attachDriver']
        if mAttachDriver and not mAttachDriver.hasAttr('cgmAlias'):
            mAttachDriver.addAttr('cgmAlias','{0}_rootDriver'.format(self.d_module['partName']))    
        
        #>>  DynParentGroups - Register parents for various controls ============================================
        ml_baseDynParents = []
        ml_endDynParents = self.ml_dynParentsAbove + self.ml_dynEndParents# + [mRoot]
        ml_ikDynParents = []
        
        """
        ml_baseDynParents = []
        ml_endDynParents = [mRoot,mMasterNull.puppetSpaceObjectsGroup, mMasterNull.worldSpaceObjectsGroup]
        
        if mModuleParent:
            mi_parentRigNull = mModuleParent.rigNull
            if mi_parentRigNull.getMessage('rigRoot'):
                ml_baseDynParents.append( mi_parentRigNull.rigRoot )        
            if mi_parentRigNull.getMessage('controlIK'):
                ml_baseDynParents.append( mi_parentRigNull.controlIK )	    
            if mi_parentRigNull.getMessage('controlIKBase'):
                ml_baseDynParents.append( mi_parentRigNull.controlIKBase )
            ml_parentRigJoints =  mi_parentRigNull.msgList_get('rigJoints')
            if ml_parentRigJoints:
                ml_used = []
                for mJnt in ml_parentRigJoints:
                    if mJnt in ml_used:continue
                    if mJnt in [ml_parentRigJoints[0],ml_parentRigJoints[-1]]:
                        ml_baseDynParents.append( mJnt.masterGroup)
                        ml_used.append(mJnt)"""
                        
                        
        #...Root controls ========================================================================================
        log.debug("|{0}| >>  Root: {1}".format(_str_func,mRoot))
        
        if b_ikOrientToWorld:BUILDUTILS.control_convertToWorldIK(mRoot)
        
        ml_targetDynParents = [self.md_dynTargetsParent['attachDriver']]
            
        if not mRoot.hasAttr('cgmAlias'):
            mRoot.addAttr('cgmAlias','{0}_root'.format(self.d_module['partName']))
        
        
        #if mBlock.root_dynParentScaleMode == 2:
        ml_targetDynParents.extend(self.ml_dynParentsAbove)        
        
        ml_targetDynParents.extend(self.ml_dynEndParents)
        mDynGroup = cgmRigMeta.cgmDynParentGroup(dynChild=mRoot.mNode,dynMode=0)
        ml_targetDynParents.extend(mRoot.msgList_get('spacePivots',asMeta = True))
    
        log.debug("|{0}| >>  Root Targets...".format(_str_func,mRoot))
        #pprint.pprint(ml_targetDynParents)
        
        for mTar in ml_targetDynParents:
            mDynGroup.addDynParent(mTar)
        
        mDynGroup.dynMode = mBlock.root_dynParentMode
        mDynGroup.scaleMode = mBlock.root_dynParentScaleMode
            
        mDynGroup.rebuild()
        #mDynGroup.dynFollow.p_parent = self.mConstrainNull
        
        if mBlock.root_dynParentScaleMode == 2:
            mRoot.scaleSpace = 'puppet'
            ATTR.set_default(mRoot.mNode, 'scaleSpace', 'puppet')        
        
        ml_baseDynParents.append(mRoot)
        
        if mScaleRoot:
            mScaleRoot.addAttr('cgmAlias','{0}_scaleRoot'.format(self.d_module['partName']))            
            ml_baseDynParents.insert(0,mScaleRoot)

        mPivotResultDriver = mRigNull.getMessage('pivotResultDriver',asMeta=True)
        
        
        #...ik controls ==================================================================================
        log.debug("|{0}| >>  IK Handles ... ".format(_str_func))                
        
        ml_ikControls = []
        mControlIK = mRigNull.getMessage('controlIK')
        
        if mControlIK:
            ml_ikControls.append(mRigNull.controlIK)
        mControlIKBase = mRigNull.getMessageAsMeta('controlIKBase')
        if mControlIKBase:
            ml_ikControls.append(mControlIKBase)
        
        str_ikBase = mBlock.getEnumValueString('ikBase')
        for mHandle in ml_ikControls:
            log.debug("|{0}| >>  IK Handle: {1}".format(_str_func,mHandle))
            
            
            if b_ikOrientToWorld:
                if mHandle == mControlIKBase and str_ikBase not in ['hips','head']:
                    pass
                else:
                    BUILDUTILS.control_convertToWorldIK(mHandle)
            
            ml_targetDynParents = ml_baseDynParents + [self.md_dynTargetsParent['attachDriver']] + ml_endDynParents
            
            ml_targetDynParents.append(self.md_dynTargetsParent['world'])
            ml_targetDynParents.extend(mHandle.msgList_get('spacePivots',asMeta = True))
            
            if mPivotResultDriver:# and mControlIKBase == mHandle:
                ml_targetDynParents.insert(0, mPivotResultDriver)                        
        
            mDynGroup = cgmRigMeta.cgmDynParentGroup(dynChild=mHandle,dynMode=0)
            if mModuleParent:
                mDynGroup.dynMode = 2
            #mDynGroup.dynMode = 2
        
            for mTar in ml_targetDynParents:
                mDynGroup.addDynParent(mTar)
            mDynGroup.rebuild()
            #mDynGroup.dynFollow.p_parent = self.mConstrainNull
            if mDynGroup.getMessage('dynFollow'):
                mDynGroup.dynFollow.p_parent = self.mConstrainNull
                

                
        log.debug("|{0}| >>  IK targets...".format(_str_func))
        #pprint.pprint(ml_targetDynParents)        
        log.debug(cgmGEN._str_subLine)
                  
                  
        #Mid controls ====================
        if self.ml_ikMidControls:
            log.debug("|{0}| >> Found midIKControls".format(_str_func))       
            for mHandle in self.ml_ikMidControls:
                #if b_ikOrientToWorld:BUILDUTILS.control_convertToWorldIK(mHandle)
            
                #mParent = mHandle.masterGroup.getParent(asMeta=True)
                ml_targetDynParents = []
                mMainDriver = mHandle.getMessageAsMeta('mainDriver')
                if mMainDriver:
                    ml_targetDynParents.append(mMainDriver)
                    mMainDriver.doStore('cgmAlias','midIKBase')
                else:
                    pass
                    #if not mParent.hasAttr('cgmAlias'):
                    #    mParent.doStore('cgmAlias','midIKBase')
                
                mPivotResultDriver = mRigNull.getMessage('pivotResultDriver',asMeta=True)
                if mPivotResultDriver:
                    mPivotResultDriver = mPivotResultDriver[0]
                    
                ml_targetDynParents.extend([mPivotResultDriver] + ml_ikControls)
                
                ml_targetDynParents.extend(ml_baseDynParents + ml_endDynParents)
                #ml_targetDynParents.extend(mHandle.msgList_get('spacePivots',asMeta = True))
                
                mMainDriver = mHandle.getMessageAsMeta('mainDriver')
                if mMainDriver:
                    ml_targetDynParents.insert(0,mMainDriver)
                
                mDynGroup = cgmRigMeta.cgmDynParentGroup(dynChild=mHandle,dynMode=0)
                
                mDynGroup.dynMode = mBlock.ikMidDynParentMode
                mDynGroup.scaleMode = mBlock.ikMidDynScaleMode                
            
                for mTar in ml_targetDynParents:
                    mDynGroup.addDynParent(mTar)
                mDynGroup.rebuild()
                #mDynGroup.dynFollow.p_parent = self.mConstrainNull
                
                log.debug("|{0}| >>  IK Mid targets...".format(_str_func,mRoot))
                #pprint.pprint(ml_targetDynParents)                
                log.debug(cgmGEN._str_subLine)   
                
                self.fnc_connect_toRigGutsVis( [mMainDriver] )        
                
                
        """
        if mRigNull.getMessage('controlSegMidIK'):
            log.debug("|{0}| >>  IK Mid Handle ... ".format(_str_func))                
            mHandle = mRigNull.controlSegMidIK
            if b_ikOrientToWorld:BUILDUTILS.control_convertToWorldIK(mHandle)
            
            mParent = mHandle.masterGroup.getParent(asMeta=True)
            ml_targetDynParents = []
            mMainDriver = mHandle.getMessageAsMeta('mainDriver')
            if mMainDriver:
                ml_targetDynParents.append(mMainDriver)
                mMainDriver.doStore('cgmAlias','midIKBase')
            else:
                if not mParent.hasAttr('cgmAlias'):
                    mParent.doStore('cgmAlias','midIKBase')
            
            mPivotResultDriver = mRigNull.getMessage('pivotResultDriver',asMeta=True)
            if mPivotResultDriver:
                mPivotResultDriver = mPivotResultDriver[0]
            ml_targetDynParents.extend([mPivotResultDriver,mControlIK,mParent])
            
            ml_targetDynParents.extend(ml_baseDynParents + ml_endDynParents)
            #ml_targetDynParents.extend(mHandle.msgList_get('spacePivots',asMeta = True))
            
            mMainDriver = mHandle.getMessageAsMeta('mainDriver')
            if mMainDriver:
                ml_targetDynParents.insert(0,mMainDriver)
            
            mDynGroup = cgmRigMeta.cgmDynParentGroup(dynChild=mHandle,dynMode=0)
            #mDynGroup.dynMode = 2
        
            for mTar in ml_targetDynParents:
                mDynGroup.addDynParent(mTar)
            mDynGroup.rebuild()
            #mDynGroup.dynFollow.p_parent = self.mConstrainNull
            
            log.debug("|{0}| >>  IK Mid targets...".format(_str_func,mRoot))
            #pprint.pprint(ml_targetDynParents)                
            log.debug(cgmGEN._str_subLine)    """

        #...rigjoints ============================================================================================
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
                #mDynGroup.dynMode = 2
                for mTar in ml_targetDynParents:
                    mDynGroup.addDynParent(mTar)
                mDynGroup.rebuild()
                
                #mDynGroup.dynFollow.p_parent = mRoot
        
        #...fk controls ====================================================================================
        log.debug("|{0}| >>  FK...".format(_str_func)+'-'*80)                
        ml_fkJoints = self.mRigNull.msgList_get('fkJoints')
        
        for i,mObj in enumerate(ml_fkJoints):
            if i and not mBlock.spaceSwitch_fk:
                continue
            if not mObj.getMessage('masterGroup'):
                log.debug("|{0}| >>  Lacks masterGroup: {1}".format(_str_func,mObj))            
                continue
            log.debug("|{0}| >>  FK: {1}".format(_str_func,mObj))
            ml_targetDynParents = copy.copy(ml_baseDynParents)
            ml_targetDynParents.append(self.md_dynTargetsParent['attachDriver'])
            
            mParent = mObj.masterGroup.getParent(asMeta=True)
            if not mParent.hasAttr('cgmAlias'):
                mParent.addAttr('cgmAlias','{0}_base'.format(mObj.p_nameBase))
                
            if i == 0:
                ml_targetDynParents.append(mParent)
                _mode = 2
                
                if mPivotResultDriver:
                    ml_targetDynParents.insert(0, mPivotResultDriver)                        
            else:
                ml_targetDynParents.insert(0,mParent)
                _mode = 2
            
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
            #pprint.pprint(ml_targetDynParents)                
            log.debug(cgmGEN._str_subLine)    
        
        
        #Settings =================================================================================
        log.debug("|{0}| >> Settings...".format(_str_func))
        mSettings.visRoot = 0
        mSettings.visDirect = 0
        
        
        ml_handleJoints = mRigNull.msgList_get('handleJoints')
        if ml_handleJoints:
            #ATTR.set_default(ml_handleJoints[-1].mNode, 'followRoot', 1.0)
            #ml_handleJoints[-1].followRoot = 1.0
            for mHandle in ml_handleJoints:
                ATTR.set_default(mHandle.mNode, 'followRoot', 1.0)
                mHandle.followRoot = 1.0
                
            if mBlock.getEnumValueString('ikBase') not in ['hips','head']:
                ATTR.set_default(ml_handleJoints[0].mNode, 'followRoot', 0.0)
                ml_handleJoints[0].followRoot = 0.0
                

        """
        if mSettings.hasAttr('FKIK'):
            if mBlock.blockType in ['tail']:
                _v = 0.0
            else:
                _v = 1.0
            ATTR.set_default(mSettings.mNode, 'FKIK', _v)
            mSettings.FKIK = _v
        """
        
        #Lock and hide =================================================================================
        ml_blendJoints = mRigNull.msgList_get('blendJoints',asMeta=True)
        for mJnt in ml_blendJoints:
            mJnt.dagLock(True)
        
        
        ml_controls = mRigNull.msgList_get('controlsAll')
        self.UTILS.controls_lockDown(ml_controls)
    
        
        if not mBlock.scaleSetup:
            log.debug("|{0}| >> No scale".format(_str_func))
            ml_controlsToLock = copy.copy(ml_controls)
            if self.b_squashSetup:
                ml_handles = self.mRigNull.msgList_get('handleJoints')
                for mHandle in ml_handles:
                    ml_controlsToLock.remove(mHandle)
                    
                """
                if self.md_roll:
                    for i in self.md_roll.keys():
                        mControlMid = mRigNull.getMessageAsMeta('controlSegMidIK_{0}'.format(i))
                        if mControlMid:
                            ml_controlsToLock.remove(mControlMid)"""
        
        
            for mCtrl in ml_controlsToLock:
                ATTR.set_standardFlags(mCtrl.mNode, ['scale'])
        else:
            log.debug("|{0}| >>  scale setup...".format(_str_func))
            
            
        self.mDeformNull.dagLock(True)
    
        #Close out ========================================================================================
        mBlock.blockState = 'rig'
        mRigNull.version = self.d_block['buildVersion']
        
        mBlock.UTILS.set_blockNullFormState(mBlock)
        self.UTILS.rigNodes_store(self)
        
        ml_rigNodes = mBlock.UTILS.rigNodes_get(mBlock)
        for node in ml_rigNodes:
            if mc.ls(node,type=['orientConstraint']):
                log.info("|{0}| >> Orient Node: {1}.".format(_str_func,node))
                ATTR.set(node,'interpType',2)
        
    
        #cgmGEN.func_snapShot(vars())
        return
    except Exception as err:cgmGEN.cgmExceptCB(Exception,err,localDat=vars())        


def build_proxyMesh(self, forceNew = True,  puppetMeshMode = False, skin = False):
    """
    Build our proxyMesh
    """
    _short = self.p_nameShort
    _str_func = '[{0}] > build_proxyMesh'.format(_short)
    log.debug("|{0}| >> ...".format(_str_func)+cgmGEN._str_hardBreak)

    _start = time.time()
    mBlock = self
    
    if not mBlock.meshBuild:
        log.error("|{0}| >> meshBuild off".format(_str_func))                        
        return False
    if skin:
        if not self.atUtils('mesh_skinable'):return False    
    
    
    mModule = self.moduleTarget
    mRigNull = mModule.rigNull
    mSettings = mRigNull.settings
    mPuppet = self.atUtils('get_puppet')
    mMaster = mPuppet.masterControl
    mPuppetSettings = mMaster.controlSettings
    str_partName = mModule.get_partNameBase()
    
    directProxy = mBlock.proxyDirect
    
    _side = BLOCKUTILS.get_side(self)
    
    ml_rigJoints = mRigNull.msgList_get('rigJoints',asMeta = True)
    if not ml_rigJoints:
        raise ValueError("No rigJoints connected")
    
    #>> If proxyMesh there, delete ------------------------------------------------------------------------- 
    if puppetMeshMode:
        _bfr = mRigNull.msgList_get('puppetProxyMesh',asMeta=True)
        ml_proxyExisting = mRigNull.msgList_get('proxyMesh',asMeta=True)        
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

    if not mBlock.meshBuild:
        log.error("|{0}| >> meshBuild off".format(_str_func))                        
        return False        
    # Create ---------------------------------------------------------------------------
    #ml_segProxy = cgmMeta.validateObjListArg(self.atBuilderUtils('mesh_proxyCreate', ml_rigJoints,firstToStart=True),'cgmObject')
    
    # Create ---------------------------------------------------------------------------
    #Mesh build logic...
    _buildMesh = True
    if puppetMeshMode and ml_proxyExisting:
        _buildMesh = False
        ml_segProxy = ml_proxyExisting    
    
    if _buildMesh:
        log.warning("|{0}| >> building mesh...".format(_str_func))            
        
        _extendToStart = True
        _ballBase = False
        _ballMode = False
        if mBlock.proxyGeoRoot:
            _ballMode = mBlock.getEnumValueString('proxyGeoRoot')
            _ballBase=True
            
        """
        _ballMode = 'sdf'#loft
        _ballBase = True
        if _blockProfile in ['finger','thumb']:
            _ballMode = 'loft'
        if _blockProfile in ['wingBase']:
            _ballBase = False"""
            
        ml_segProxy = cgmMeta.validateObjListArg(self.atUtils('mesh_proxyCreate',
                                                              ml_rigJoints,
                                                              firstToStart=True,
                                                              ballBase = _ballBase,
                                                              ballMode = _ballMode,
                                                              hardenEdges = self.proxyHardenEdge,
                                                              extendToStart=_extendToStart),
                                                 'cgmObject')
    
    
    if directProxy:
        _settings = mRigNull.settings.mNode
        log.debug("|{0}| >> directProxy... ".format(_str_func))    
    
    ml_united = []
    if puppetMeshMode:
        log.debug("|{0}| >> puppetMesh setup... ".format(_str_func))
        ml_moduleJoints = mRigNull.msgList_get('moduleJoints')
        
        for i,mGeo in enumerate(ml_segProxy):
            if ml_proxyExisting:
                mGeo = ml_proxyExisting[i].doDuplicate(po=False)
                mGeo.p_parent = False
                ATTR.break_connection(mGeo.mNode,'v')
                mGeo.v = True    
                
            ml_united.append(mGeo)    
            log.debug("{0} : {1}".format(mGeo, ml_moduleJoints[i]))
            if skin:
                MRSPOST.skin_mesh(mGeo,[ml_moduleJoints[i]])                
            else:
                mGeo.p_parent = ml_moduleJoints[i]
                mGeo.doStore('cgmName',str_partName)
                mGeo.addAttr('cgmIterator',i+1)
                mGeo.addAttr('cgmType','proxyPuppetGeo')
                mGeo.doName()
                
            CORERIG.color_mesh(mGeo.mNode,_side,'main',transparent=False,proxy=True)
                
            
        if skin:
            if len(ml_united) > 1:
                _res = mc.polyUniteSkinned([mObj.mNode for mObj in ml_united],ch=False,objectPivot=True)
                _mesh = mc.rename(_res[0],'{0}_UnifiedPuppetProxy_geo'.format(self.p_nameBase))
                mc.rename(_res[1],'{0}_skinCluster'.format(_mesh))
                mMesh = cgmMeta.asMeta(_mesh)
    
                ml_segProxy = [mMesh]
            else:
                ml_segProxy = ml_united            
            
            
        mRigNull.msgList_connect('puppetProxyMesh', ml_segProxy)
        return ml_segProxy
        
    for i,mGeo in enumerate(ml_segProxy):
        mGeo.p_parent = ml_rigJoints[i]
        ATTR.copy_to(ml_rigJoints[0].mNode,'cgmName',mGeo.mNode,driven = 'target')
        mGeo.addAttr('cgmIterator',i+1)
        mGeo.addAttr('cgmType','proxyGeo')
        mGeo.doName()
        
        if directProxy:
            CORERIG.shapeParent_in_place(ml_rigJoints[i].mNode,mGeo.mNode,True,True)
            CORERIG.colorControl(ml_rigJoints[i].mNode,_side,'main',directProxy=True)
            
            for mShape in ml_rigJoints[i].getShapes(asMeta=True):
                ATTR.connect("{0}.visDirect".format(_settings), "{0}.overrideVisibility".format(mShape.mNode))
            
    
    for mProxy in ml_segProxy:
        CORERIG.colorControl(mProxy.mNode,_side,'main',transparent=False,proxy=True)
        mc.makeIdentity(mProxy.mNode, apply = True, t=1, r=1,s=1,n=0,pn=1)

        #Vis connect -----------------------------------------------------------------------
        mProxy.overrideEnabled = 1
        ATTR.connect("{0}.proxyVis_out".format(mRigNull.mNode),"{0}.visibility".format(mProxy.mNode) )
        ATTR.connect("{0}.proxyLock".format(mPuppetSettings.mNode),"{0}.overrideDisplayType".format(mProxy.mNode) )        
        for mShape in mProxy.getShapes(asMeta=1):
            str_shape = mShape.mNode
            mShape.overrideEnabled = 0
            ATTR.connect("{0}.proxyLock".format(mPuppetSettings.mNode),"{0}.overrideDisplayTypes".format(str_shape) )
        
    mRigNull.msgList_connect('proxyMesh', ml_segProxy)
    
    #l_args = [self.d_module['mPuppet'].displayLayer.mNode] + [mObj.mNode for mObj in ml_segProxy]
    #mc.editDisplayLayerMembers(*l_args,
    #                           noRecurse=True)
    
    
def controller_getDat(self):
    _str_func = 'controller_getDat'
    log.debug("|{0}| >>  {1}".format(_str_func,self)+ '-'*80)
    mRigNull = self.rigNull
    
    def checkList(l):
        ml = []
        for o in l:
            if mRigNull.getMessage(o):
                log.debug("|{0}| >>  Message found: {1} ".format(_str_func,o))                
                mObj = mRigNull.getMessage(o,asMeta=True)[0]
                if mObj not in ml:ml.append(mObj)
            elif mRigNull.msgList_exists(o):
                log.debug("|{0}| >>  msgList found: {1} ".format(_str_func,o))                
                _msgList = mRigNull.msgList_get(o)
                for mObj in _msgList:
                    if mObj not in ml:ml.append(mObj)
        return ml
    
    md = {}

    #Root...
    md['root'] =  checkList(['cog','rigRoot','limbRoot'])

    md['settings'] =  checkList(['mSettings','settings'])
    
    #Direct...
    md['direct'] = mRigNull.msgList_get('rigJoints')
    
    md['pivots'] = checkList(['pivot{0}'.format(n.capitalize()) for n in BLOCKSHARE._l_pivotOrder])
    
    #FK...
    md['fk'] = checkList(['leverFK','fkJoints','controlsFK','controlFK'])
    
    md['noHide'] = md['root'] + md['settings']
    
    #IK...
    md['ik'] = checkList(['leverFK','controlsIK',
                          'controlIKBase',
                          'controlIKMid','controlSegMidIK',
                          'controlBallRotation','leverIK',
                          'controlIKBall','controlIKBallHinge','controlIKToe',
                          'controlIKEnd','controlIK'])
    #seg...
    md['segmentHandles'] = mRigNull.msgList_get('handleJoints')
        
        
    return md
    
    
def uiBuilderMenu(self,parent = None):
    #uiMenu = mc.menuItem( parent = parent, l='Head:', subMenu=True)
    _short = self.p_nameShort
    
    mc.menuItem(en=False,
                label = "Segment")    
    mc.menuItem(ann = '[{0}] create joint helpers'.format(_short),
                c = cgmGEN.Callback(create_jointHelpers,self,**{'force':1}),
                label = "Create Joint Helpers")
    
    
    
    
    










