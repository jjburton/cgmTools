"""
------------------------------------------
cgm.core.mrs.blocks.organic.lowerFace
Author: Josh Burton
email: cgmonks.info@gmail.com

Website : https://github.com/jjburton/cgmTools/wiki
------------------------------------------

================================================================
"""
__MAYALOCAL = 'MUZZLE'

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
log.setLevel(logging.DEBUG)

# From Maya =============================================================
import maya.cmds as mc

# From Red9 =============================================================
#from Red9.core import Red9_Meta as r9Meta
import Red9.core.Red9_AnimationUtils as r9Anim
#r9Meta.cleanCache()#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< TEMP!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


import cgm.core.cgm_General as cgmGEN
#from cgm.core.rigger import ModuleShapeCaster as mShapeCast

#import cgm.core.cgmPy.os_Utils as cgmOS
import cgm.core.cgmPy.path_Utils as cgmPATH
import cgm.core.mrs.assets as MRSASSETS
path_assets = cgmPATH.Path(MRSASSETS.__file__).up().asFriendly()

import cgm.core.mrs.lib.ModuleControlFactory as MODULECONTROL
#reload(MODULECONTROL)
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
import cgm.core.rig.general_utils as RIGGEN
#import cgm.core.lib.constraint_utils as CONSTRAINT
import cgm.core.lib.locator_utils as LOC
#import cgm.core.lib.rayCaster as RAYS
#import cgm.core.lib.shape_utils as SHAPES
import cgm.core.mrs.lib.block_utils as BLOCKUTILS
#import cgm.core.mrs.lib.builder_utils as BUILDERUTILS
#import cgm.core.mrs.lib.shared_dat as BLOCKSHARE
import cgm.core.mrs.lib.blockShapes_utils as BLOCKSHAPES
#import cgm.core.tools.lib.snap_calls as SNAPCALLS
import cgm.core.rig.ik_utils as IK
import cgm.core.cgm_RigMeta as cgmRIGMETA
#import cgm.core.lib.nameTools as NAMETOOLS
import cgm.core.cgmPy.validateArgs as VALID
#import cgm.core.lib.list_utils as LISTS
import cgm.core.rig.ik_utils as IK
#import cgm.core.rig.skin_utils as RIGSKIN
import cgm.core.lib.string_utils as STR
import cgm.core.lib.surface_Utils as SURF

#for m in DIST,POS,MATH,IK,CONSTRAINT,LOC,BLOCKUTILS,BUILDERUTILS,CORERIG,RAYS,JOINT,RIGCONSTRAINT,RIGGEN,BLOCKSHAPES:
#    reload(m)
    
# From cgm ==============================================================
from cgm.core import cgm_Meta as cgmMeta

DGETAVG = DIST.get_average_position
CRVPCT = CURVES.getPercentPointOnCurve
DPCTDIST = DIST.get_pos_by_linearPct

#=============================================================================================================
#>> Block Settings
#=============================================================================================================
__version__ = cgmGEN.__RELEASESTRING
__autoForm__ = False
__menuVisible__ = True
__faceBlock__ = True

#These are our base dimensions. In this case it is for human
__dimensions_by_type = {'box':[22,22,22],
                        'human':[15.2, 23.2, 19.7]}

__l_rigBuildOrder__ = ['rig_dataBuffer',
                       'rig_skeleton',
                       'rig_shapes',
                       'rig_controls',
                       'rig_frame',
                       'rig_lipSegments',
                       'rig_cleanUp']


d_wiring_skeleton = {'msgLinks':[],
                     'msgLists':['moduleJoints','skinJoints']}
d_wiring_prerig = {'msgLinks':['moduleTarget','prerigNull','noTransPrerigNull']}
d_wiring_form = {'msgLinks':['formNull','noTransFormNull'],
                     }
d_wiring_extraDags = {'msgLinks':['bbHelper'],
                      'msgLists':[]}

d_attrStateMask = {'define':[
    'baseSizeX',
    'baseSizeY',
    'baseSizeZ',
    'bridgeSetup',
    'cheekSetup',
    'cheekUprSetup',
    'defineProfile',
    'chinSetup',
    'faceType',
    'jawLwrSetup',
    'jawUprSetup',
    'lipSetup',
     'muzzleSetup',
     'mouthBagSetup',
     'noseSetup',
     'nostrilSetup',
     'numBridgeSplit',
     'smileSetup',
     'sneerSetup',
     'teethLwrSetup',
     'teethUprSetup',
     'tongueSetup',
    ],
                   'form':[ 'numLipOverSplit',
                            'numLipShapersLwr',
                            'numLipShapersUpr',
                            'numLipUnderSplit',
                            'numLoftBag_u',
                            'numLoftBridge_u',
                            'numLoftBridge_v',
                            'numLoftJaw_u',
                            'numLoftJaw_v',
                            'numLoftLipOver_u',
                            'numLoftLipUnder_u',
                            'numLoftLip_u',
                            'numLoftLip_v',
                            'numLoftNose_u',
                            'numLoftNose_v',                            
                       ],
                   'prerig':[ 'jointDepthLip',
                              'numConLips',
                              'paramLwrStart',
                              'paramUprStart',
                              'preLipStartSplit',
                              'controlOffset',
                              'conDirectOffset',

                       ],
                   'skeleton':[
                       'numJointsLipLwr',
                       'numJointsLipUpr',
                       'numJointsNoseTip',
                       'numJointsNostril',
                       'numJointsTongue',
                       ],
                   'rig':[
                       'lipMidFollowSetup',
                       'lipSealCrossBlendMult',
                       
                   ]}




#>>>Profiles ==============================================================================================
d_build_profiles = {}


d_block_profiles = {'default':{},
                    'jaw':{'baseSize':[17.6,7.2,8.4],
                           'faceType':'default',
                           'muzzleSetup':'dag',
                           'noseSetup':'none',
                           'jawLwrSetup':'simple',
                           'lipSetup':'none',
                           'teethSetup':'none',
                           'cheekSetup':'none',
                           'tongueSetup':'none',
                           'uprJaw':False,
                           'chinSetup':'none',
                               },
                    'canine':{'jawLwrSetup':'simple',
                              'lipSetup':'default',
                              'noseSetup':'simple',
                              'chinSetup':'none',
                              'nostrilSetup':'simple'},
                    'human':{'jawLwrSetup':'simple',
                             'lipSetup':'default',
                             'muzzleSetup':'dag',                             
                             'noseSetup':'simple',
                             'chinSetup':'single',
                             'cheekSetup':'single',
                             'sneerSetup':'single',
                             'nostrilSetup':'simple'},
                    'beak':{},
                    }
"""
'eyebrow':{'baseSize':[17.6,7.2,8.4],
           'browType':'full',
           'profileOptions':{},
           'paramStart':.2,
            'paramMid':.5,
            'paramEnd':.7,                               
           },"""
#>>>Attrs =================================================================================================
l_attrsStandard = ['side',
                   'position',
                   'attachPoint',
                   'attachIndex',                   
                   'nameList',
                   #'loftDegree',
                   #'loftSplit',
                   'scaleSetup',
                   'visLabels',
                   'buildSDK',                   
                   'visFormHandles',
                   'controlOffset',
                   'conDirectOffset',
                   'visProximityMode',
                   'ribbonParam',                   
                   'moduleTarget',]

d_attrsToMake = {'faceType':'default:muzzle:beak',
                 'defineProfile':'human:muzzle:beak:muppet',
                 'muzzleSetup':'none:dag:joint',
                 'noseSetup':'none:simple',
                 'jawLwrSetup':'none:simple:slide',
                 'lipSetup':'none:default',
                 'teethUprSetup':'none:simple',
                 'teethLwrSetup':'none:simple',
                 
                 'cheekSetup':'none:single:double',
                 'cheekUprSetup':'none:single:lineSimple',
                 'tongueSetup':'none:single',
                 'sneerSetup':'none:single',
                 'smileSetup':'none:single:lineSimple',
                 'mouthBagSetup':'none:define',
                 
                 #Jaw...
                 'jawUprSetup':'none:simple',
                 'chinSetup':'none:single',
                 
                 #Nose...
                 'nostrilSetup':'none:default',
                 'bridgeSetup':'none:default',
                 'numJointsNostril':'int',
                 'numJointsNoseTip':'int',
                 
                 #Lips...
                 'lipMidFollowSetup':'ribbon:prntConstraint:parent',
                 'lipMidSealSetup':'bool',
                 'lipSealCrossBlendMult':'float',
                 
                 #'lipSealSetup':'none:default',
                 'numConLips':'int',
                 'numLipShapersUpr':'int',
                 'numLipShapersLwr':'int',
                 
                 'numSmile':'int',
                 'numUprCheek':'int',
                 
                 'numJointsLipUpr':'int',
                 'numJointsLipLwr':'int',
                 'paramUprStart':'float',
                 'paramLwrStart':'float',
                 'numLoftJaw_u':'int',
                 'numLoftJaw_v':'int',
                 'numLoftLip_u':'int',
                 'numLoftLipOver_u':'int',                 
                 'numLoftLipUnder_u':'int',
                 
                 'numLoftLip_v':'int',
                 'numLoftNose_u':'int',
                 'numLoftNose_v':'int',
                 'numLoftBridge_u':'int',
                 'numLoftBridge_v':'int',
                 'numLoftBag_u':'int',
                 
                 'numLipOverSplit':'int',
                 'numLipUnderSplit':'int',
                 
                 'numBridgeSplit':'int',
                 
                 #'lipCorners':'bool',
                 #Tongue...
                 'numJointsTongue':'int',
                 'jointDepth':'float',
                 'jointDepthLip':'float',
                 
                 'jointRadius':'float',                 
                 'preLipStartSplit':'float',
                 
                 }

d_defaultSettings = {'version':__version__,
                     'attachPoint':'end',
                     'side':'none',
                     #'loftDegree':'cubic',
                     'lipMidSealSetup':True,
                     'lipSealCrossBlendMult':.8,
                     'numJointsLipUpr':3,
                     'numConLips':3,
                     'numJointsLipLwr':3,
                     'numJointsNoseTip':1,
                     'numJointsNostril':1,
                     'paramUprStart':.15,
                     'paramLwrStart':.15,
                     'numJointsTongue':3,
                     'visLabels':True,
                     'numLoftJaw_u':22,
                     'numLoftJaw_v':6,
                     'numLoftLip_u':9,
                     'numLoftOverUnder_u':6,
                     'numLoftLipUnder_u':3,
                     'ribbonParam':'blend',
                     'numLoftLip_v':13,
                     'numLoftNose_u':10,
                     'numLoftNose_v':10,
                     'numLoftBridge_u':10,
                     'numLoftBridge_v':3,
                     'numLoftBag_u':8,
                     
                     'numLipShapersUpr':6,
                     'numLipShapersLwr':6,
                     'numBridgeSplit':1,
                     'numLipOverSplit':3,
                     'numLipUnderSplit':2,
                     'jointDepth':-.41,
                     'jointDepthLip':-.41,
                     'preLipStartSplit':.05,
                     
                     'controlOffset':1,
                     'conDirectOffset':0,
                     'jointRadius':1.0,
                     'visFormHandles':True,
                     #'baseSize':MATH.get_space_value(__dimensions[1]),
                     }

_d_scaleSpace = {
    'muppet':
                 {'bridge': [6.617444900424222e-24, 0.7119054214044773, 1.3271621184403883],
                  'bridgeOuterLeft': [0.18729736376914286,
                                      0.6654414273750131,
                                      0.9908282807184101],
                  'bridgeOuterRight': [-0.18729736376914283,
                                       0.6654414273750131,
                                       0.9908282807184101],
                  'bridgeRight': [-0.10286757330047164, 0.7009123505204435, 1.3032800012869035],
                  'bulb': [6.617444900424222e-24, 0.39005799548828435, 1.4328131504101937],
                  'bulbRight': [-0.11468922985910648, 0.38223156537965686, 1.391380017814702],
                  'cheekBoneRight': [-0.5848587837359853,
                                     0.2894947782982946,
                                     0.7495439432150794],
                  'cheekRight': [-0.9737103857255595,
                                 -0.07974751909913103,
                                 -0.10215773399907913],
                  'chinRight': [-0.36542079645026765, -0.7497383895643654, 0.9460989438586402],
                  'cornerBackRight': [-0.8384541139408674,
                                      -0.20740679560049458,
                                      0.18170200030231587],
                  'cornerBagRight': [-0.6533842308578784,
                                     -0.28970941424011976,
                                     -0.07351462602931769],
                  'cornerFrontRight': [-0.9150664201749135,
                                       -0.23215147286975757,
                                       0.23476862762587258],
                  'cornerLwrRight': [-0.9196582572635654,
                                     -0.3915755616068193,
                                     0.2600908341184641],
                  'cornerPeakRight': [-0.9529794817408644,
                                      -0.23215147286977533,
                                      0.1804638274446878],
                  'cornerUprRight': [-0.9187639245107152,
                                     -0.04189363402240609,
                                     0.2617995090925054],
                  'jawFrontRight': [-0.36962233968790603,
                                    -0.9240010049543823,
                                    0.936565071483282],
                  'jawNeck': [6.617444900424222e-24, -1.2173357951244217, 0.45931090262267016],
                  'jawNeckRight': [-0.9084376443328624,
                                   -0.6390036604357086,
                                   0.09588862520568858],
                  'jawRight': [-0.9634967059996269, -0.5810373648283846, -0.46021350693906893],
                  'jawTopRight': [-1.002509260463563, 0.4561344761291881, -0.37317360485348805],
                  'lwrBack': [0, -0.3037060733705097, 0.7994843746455893],
                  'lwrBackRight': [-0.5340392236994518, -0.24029295729729228, 0.293704553125681],
                  'lwrFront': [6.617444900424222e-24, -0.30316153816911573, 0.9726691027120613],
                  'lwrFrontRight': [-0.4073950810759738,
                                    -0.29925163551046907,
                                    0.8359528746842595],
                  'lwrGum': [6.617444900424222e-24, -0.611961228542766, 0.69855843482444],
                  'lwrOver': [6.617444900424222e-24, -0.5869600554548917, 0.9939662664626849],
                  'lwrOverRight': [-0.40258166336056317,
                                   -0.5262106964462525,
                                   0.8904778410322158],
                  'lwrPeak': [6.617444900424222e-24, -0.36881209279583693, 1.0177348783071096],
                  'lwrPeakRight': [-0.4316636613601202,
                                   -0.33921160576472786,
                                   0.8625238855989621],
                  'mouthBagBack': [6.617444900424222e-24,
                                   -0.30913356019430793,
                                   -0.5185203517200778],
                  'mouthBagBottom': [6.617444900424222e-24,
                                     -0.7387313209446997,
                                     0.08316614589086718],
                  'mouthBagRight': [-0.6951842247125819,
                                    -0.3357142034735361,
                                    -0.4934290020805305],
                  'mouthBagTop': [6.617444900424222e-24,
                                  0.11855117025756101,
                                  0.13350413315881093],
                  'noseBase': [6.617444900424222e-24, 0.0980172452526702, 1.0802431602787392],
                  'noseBaseRight': [-0.06447592850531289,
                                    0.1312707544658558,
                                    1.0264669005428835],
                  'noseTip': [6.617444900424222e-24, 0.261470920198299, 1.4561538299435526],
                  'noseTipRight': [-0.12175008451239276, 0.2638110760009287, 1.4352360083808022],
                  'noseTop': [6.617444900424222e-24, 0.9976837756942682, 1.002586422922707],
                  'noseTopRight': [-0.09073310410417967, 0.9855281389409907, 0.963336296442221],
                  'noseUnder': [6.617444900424222e-24, 0.15068071834849484, 1.413193899939158],
                  'nostrilBaseRight': [-0.17840265418137208,
                                       0.13183220981177612,
                                       1.0820948312223626],
                  'nostrilLineInnerLeft': [0.05220606107410563,
                                           0.1655798660665475,
                                           1.3228474312211935],
                  'nostrilLineInnerRight': [-0.05220606107410563,
                                            0.1655798660665475,
                                            1.3228474312211935],
                  'nostrilLineOuterRight': [-0.1403097181284395,
                                            0.1927274491792872,
                                            1.258653342471839],
                  'nostrilRight': [-0.23094209451046774,
                                   0.20589739950114172,
                                   0.9975915899024255],
                  'nostrilTopRight': [-0.21194843773659713,
                                      0.3923897628136057,
                                      0.9776489676767361],
                  'orbFrontRight': [-0.5924508681974274, 0.5097291426521302, 0.802984768889557],
                  'orbRight': [-0.8592522662071523, 0.4310727464754862, 0.3720415061915493],
                  'smileRight': [-0.9447446334141945, -0.20253722379706574, 0.10425571338295875],
                  'sneerRight': [-0.1650209689485439, 0.9036412653062555, 0.8603416611983652],
                  'uprBack': [-0.005559025181135858, -0.26621430219109143, 0.8130835245154717],
                  'uprBackRight': [-0.34275257785629065,
                                   -0.24322209321731947,
                                   0.6679266619018258],
                  'uprFront': [6.617444900424222e-24, -0.26339937113841216, 0.9807891218240232],
                  'uprFrontRight': [-0.4073950810759738,
                                    -0.2351521908300267,
                                    0.8079507750711228],
                  'uprGum': [6.617444900424222e-24, 0.10817846136983889, 0.7160626661886829],
                  'uprOver': [6.617444900424222e-24, 0.02648282709150429, 1.0211166964547387],
                  'uprOverRight': [-0.43767073445600774,
                                   0.005788914605096451,
                                   0.8794701445810409],
                  'uprPeak': [6.617444900424222e-24, -0.19691243592580143, 1.0271498010531217],
                  'uprPeakRight': [-0.4465273910651476, -0.1404288489594805, 0.87938720633154]},


                 'canine':
                 {'bridge': [0, 0.7498176416406359, 1.0360182177554098],
                  'bridgeOuterLeft': [0.1957615666726813,
                                      0.5861744098168451,
                                      0.9841679114197788],
                  'bridgeOuterRight': [-0.19576156667268174,
                                       0.5861744098168451,
                                       0.9841679114197788],
                  'bridgeRight': [-0.09935131199319214, 0.7189223703844227, 1.0360182177554107],
                  'bulb': [0, 0.5771649917634214, 1.4865237503303455],
                  'bulbRight': [-0.10000000000000098, 0.559579202989049, 1.486523750330346],
                  'cheekBoneRight': [-0.4548718429906855,
                                     0.3193815118184702,
                                     0.4193117038087638],
                  'cheekRight': [-0.766609681139002, -0.3377810960371548, -0.158567563006563],
                  'cornerBackRight': [-0.37214375696857793,
                                      -0.5474608808125421,
                                      0.30569460998633347],
                  'cornerBagRight': [-0.3309945846495146,
                                     -0.5474608808125438,
                                     0.26342441742485634],
                  'cornerFrontRight': [-0.4088476244546153,
                                       -0.5474608808125421,
                                       0.31501298295863644],
                  'cornerLwrRight': [-0.39308398337602046,
                                     -0.6189502601280825,
                                     0.30429465981816595],
                  'cornerPeakRight': [-0.4524272643516176,
                                      -0.5474608808125652,
                                      0.277378868596756],
                  'cornerUprRight': [-0.4313490937931834,
                                     -0.4130946123885284,
                                     0.35572687429844563],
                  'jawFrontRight': [-0.303667363085141,
                                    -0.8136541251421114,
                                    0.21283793611728252],
                  'jawNeck': [0, -1.0155196870030885, -0.09988547315186386],
                  'jawNeckRight': [-0.5579989616498406,
                                   -0.8301545313225525,
                                   -0.04454479938204825],
                  'jawRight': [-0.8267515799055545, -0.5189037586570784, -0.8910403473217492],
                  'jawTopRight': [-1.0000000000000053, 0.6216915556280753, -0.9999999999999998],
                  'lwrBack': [-8.881784197001252e-16, -0.5918607643873628, 1.2101399766119272],
                  'lwrBackOutLeft': [0.28060741271139555,
                                     -0.5800119857936608,
                                     0.7754055610110713],
                  'lwrBackOutRight': [-0.280607412711396,
                                      -0.5800119857936608,
                                      0.7754055610110713],
                  'lwrBackRight': [-0.18033650066295914,
                                   -0.5918607643873628,
                                   1.1294913439189411],
                  'lwrFront': [0, -0.5918607643873628, 1.2984826494456996],
                  'lwrFrontOutLeft': [0.33951090218515745,
                                      -0.5816402133093899,
                                      0.8160079970770875],
                  'lwrFrontOutRight': [-0.3395109021851579,
                                       -0.5816402133093899,
                                       0.8160079970770875],
                  'lwrFrontRight': [-0.22231060034631822,
                                    -0.5918607643873628,
                                    1.2179583546034918],
                  'lwrGum': [-8.881784197001252e-16, -0.691860764387366, 1.1422086678390535],
                  'lwrGumOutRight': [-0.2436406968926219,
                                     -0.7098406465304699,
                                     0.7567150755165863],
                  'lwrOver': [0, -0.8269212605232905, 1.1305542962469466],
                  'lwrOverOutLeft': [0.2891436087748458,
                                     -0.7672977478568832,
                                     0.7935513492282487],
                  'lwrOverOutRight': [-0.28914360877484624,
                                      -0.7672977478568832,
                                      0.7935513492282487],
                  'lwrOverRight': [-0.1768902633669831,
                                   -0.8045733904124557,
                                   1.0806476321082719],
                  'lwrPeak': [-3.1086244689504383e-15, -0.7140052399719963, 1.2417462320469328],
                  'lwrPeakOutLeft': [0.33661382195627754,
                                     -0.6604659845353336,
                                     0.793977322099741],
                  'lwrPeakOutRight': [-0.336613821956278,
                                      -0.6604659845353336,
                                      0.793977322099741],
                  'lwrPeakRight': [-0.20448822571832803,
                                   -0.7118227410444398,
                                   1.1390415005943137],
                  'noseBase': [0, -0.06898868185345464, 1.604132679267137],
                  'noseBaseRight': [-0.10000000000000098,
                                    -0.006028153579244133,
                                    1.604132679267137],
                  'noseTip': [0, 0.3737935982860847, 1.6879084942027562],
                  'noseTipRight': [-0.1735018630054248, 0.3732671288382967, 1.6059596572032393],
                  'noseTop': [0, 1.0, 0.5],
                  'noseTopRight': [-0.11617618248954154, 0.9550754787151163, 0.500000000000002],
                  'noseUnder': [0, 0.12141895581972761, 1.6669100954216],
                  'nostrilBaseRight': [-0.25242091464837246,
                                       0.1410632843513504,
                                       1.4806614633476713],
                  'nostrilLineInnerLeft': [0.07518023118280803,
                                           0.14445261224951622,
                                           1.6386126003323707],
                  'nostrilLineInnerRight': [-0.07518023118280848,
                                            0.14445261224951622,
                                            1.6386126003323707],
                  'nostrilLineOuterRight': [-0.15748658244389135,
                                            0.19748125577367048,
                                            1.6238699713504006],
                  'nostrilRight': [-0.24404273259852172,
                                   0.40107545329665584,
                                   1.4985048303021897],
                  'nostrilTopRight': [-0.1841356867342694,
                                      0.5068183782140139,
                                      1.4606647904279297],
                  'orbFrontRight': [-0.4301394577464368,
                                    0.5909860773442261,
                                    0.30849262045566506],
                  'orbRight': [-0.6456105096034843, 0.7427437489438979, 0.048974030106921695],
                  'smileRight': [-0.5141412209272933, -0.5437366183790004, 0.24013782225955904],
                  'sneerRight': [-0.22141491559884363, 0.8244026206143751, 0.4450581223588941],
                  'snoutTopRight': [-0.39335312995227945,
                                    0.21876120502259155,
                                    0.9056429069695511],
                  'uprBack': [0, -0.5884473089030458, 1.21955862746079],
                  'uprBackOutLeft': [0.277309719760507, -0.578053836709385, 0.7860807569310277],
                  'uprBackOutRight': [-0.277309719760507,
                                      -0.578053836709385,
                                      0.7860807569310277],
                  'uprBackRight': [-0.17868564856592073,
                                   -0.5884473089030493,
                                   1.1319569647395937],
                  'uprFront': [0, -0.5884473089030404, 1.2953757632288139],
                  'uprFrontOutLeft': [0.33892340015558986,
                                      -0.5884473089030404,
                                      0.8119809244359124],
                  'uprFrontOutRight': [-0.3389234001555903,
                                       -0.5884473089030404,
                                       0.8119809244359124],
                  'uprFrontRight': [-0.22190603872315906,
                                    -0.5884473089030493,
                                    1.2196805068488046],
                  'uprGum': [0, -0.38844730890304113, 1.2453757632288138],
                  'uprGumOutRight': [-0.2636740128954118,
                                     -0.4752923682393497,
                                     0.7628915247068588],
                  'uprOver': [0, -0.21963642489463275, 1.5802602472539617],
                  'uprOverOutLeft': [0.4303941696256979,
                                     -0.2504627316956718,
                                     0.8465348977211804],
                  'uprOverOutRight': [-0.43039416962569854,
                                      -0.2504627316956718,
                                      0.8465348977211804],
                  'uprOverRight': [-0.29563766059242225,
                                   -0.21699739669405993,
                                   1.4311541131749324],
                  'uprPeak': [0, -0.4665727638281254, 1.4295372373948583],
                  'uprPeakOutLeft': [0.3897574118981584,
                                     -0.4636183550215076,
                                     0.8246406265608373],
                  'uprPeakOutRight': [-0.3897574118981586,
                                      -0.4636183550215076,
                                      0.8246406265608373],
                  'uprPeakRight': [-0.2739604280711778,
                                   -0.4849660828778699,
                                   1.3442676225708896]}
                
                 ,
    'human':
    {'bridge': [0, 0.7365867340472114, 1.0030996597926332],
     'bridgeOuterLeft': [0.13949252389112712,
                         0.5837717540493443,
                         0.8367171328970837],
     'bridgeOuterRight': [-0.13949252389112712,
                          0.5837717540493443,
                          0.8367171328970837],
     'bridgeRight': [-0.07520474838168828, 0.7270662266989021, 0.9835762575207574],
     'bulb': [0, 0.5240699068480765, 1.3901734896052207],
     'bulbRight': [-0.11468922985910648, 0.4988461562971267, 1.2372688699933758],
     'cheekBoneRight': [-0.4552455251816405,
                        0.3524273607183872,
                        0.7305402042245492],
     'cheekRight': [-0.7548138362346037, -0.0135475526453952, 0.10398873890517879],
     'chinRight': [-0.1614409523259761, -0.7468972693510736, 0.947632866875574],
     'cornerBackRight': [-0.28625966490909616,
                         -0.23679384075461485,
                         0.6385293062014132],
     'cornerBagRight': [-0.3062596649090961,
                        -0.23679384075461485,
                        0.5885293062014108],
     'cornerFrontRight': [-0.3062596649090961,
                          -0.23679384075461485,
                          0.7385293062014107],
     'cornerLwrRight': [-0.29821787815454764,
                        -0.33065820535748713,
                        0.7786768690864982],
     'cornerPeakRight': [-0.3596721197671391,
                         -0.23679384075463616,
                         0.7230461841801437],
     'cornerUprRight': [-0.30667137028392527,
                        -0.1529287167356017,
                        0.7934864476056909],
     'jawFrontRight': [-0.17999508832537225,
                       -0.9719119178444089,
                       0.7578889161402307],
     'jawNeck': [0, -0.8881111221874534, -0.10000000000000342],
     'jawNeckRight': [-0.539036874461076,
                      -0.6726205915006354,
                      -0.08258840573581838],
     'jawRight': [-0.7651724059447822, -0.3164820148480878, -0.7067427535826039],
     'jawTopRight': [-0.9969301781281826, 0.7911406527910891, -0.8627656184986184],
     'lwrBack': [0, -0.19957702569902835, 0.8578025218313079],
     'lwrBackRight': [-0.09999999999999999,
                      -0.19957702569902835,
                      0.8312374301041356],
     'lwrFront': [0, -0.19957702569902835, 0.9812374301041378],
     'lwrFrontRight': [-0.09999999999999999,
                       -0.19957702569902835,
                       0.9312374301041357],
     'lwrGum': [0, -0.4050106397762363, 0.7101662861302107],
     'lwrOver': [0, -0.43009829085550066, 0.9333321698811523],
     'lwrOverRight': [-0.14114921069235795,
                      -0.40910262091812655,
                      0.9054754675656356],
     'lwrPeak': [0, -0.28145464592647684, 1.0325640693178344],
     'lwrPeakRight': [-0.11879611628814471,
                      -0.2762527299064921,
                      0.9856467769551167],
     'mouthBagBack': [0, -0.1682872287475199, -0.5303918321125718],
     'mouthBagBottom': [0, -0.6273181063579649, -0.07760146037222282],
     'mouthBagRight': [-0.5274779924958036,
                       -0.17152047717288,
                       -0.1334743803977605],
     'mouthBagTop': [0, 0.3950271775166314, -0.06793996224606946],
     'noseBase': [0, 0.15984447456211726, 1.1225285802452465],
     'noseBaseRight': [-0.06447592850531289,
                       0.2013173640764272,
                       1.0687523205093905],
     'noseTip': [0, 0.3805325402582582, 1.4355435576859916],
     'noseTipRight': [-0.12175008451239278,
                      0.34132424799971517,
                      1.2811248605594763],
     'noseTop': [0, 0.9250453592947459, 0.8484752751013809],
     'noseTopRight': [-0.07398231796050096,
                      0.8846985812493671,
                      0.8092251486208948],
     'noseUnder': [0, 0.2255249531889234, 1.2590827521178323],
     'nostrilBaseRight': [-0.17840265418137208,
                          0.20201759620469062,
                          0.9279836834010364],
     'nostrilLineInnerLeft': [0.05220606107410563,
                              0.24410677272582504,
                              1.1687362833998676],
     'nostrilLineInnerRight': [-0.05220606107410563,
                               0.24410677272582504,
                               1.1687362833998676],
     'nostrilLineOuterRight': [-0.1403097181284395,
                               0.277964514108767,
                               1.104542194650513],
     'nostrilRight': [-0.29213419777709765,
                      0.29438972478670067,
                      0.8434804420810997],
     'nostrilTopRight': [-0.21669630246982277,
                         0.41844683344454126,
                         0.8235378198554102],
     'orbFrontRight': [-0.46951524910375025,
                       0.5835603299980932,
                       0.6025409869886382],
     'orbRight': [-0.7916816805290654, 0.7847957495560784, 0.20855368016648068],
     'smileRight': [-0.45059839999917634,
                    -0.23096933114542395,
                    0.6535786299993362],
     'sneerRight': [-0.14101534953672315, 0.7249906642449702, 0.7062305133770392],
     'uprBack': [0, -0.1914104378629098, 0.8619720386817642],
     'uprBackRight': [-0.09999999999999999,
                      -0.1914104378629098,
                      0.816796936835106],
     'uprFront': [0, -0.1914104378629098, 0.9667969368351086],
     'uprFrontRight': [-0.09999999999999999,
                       -0.1914104378629098,
                       0.9167969368351043],
     'uprGum': [0, 0.056504646743022136, 0.7786976244523256],
     'uprOver': [0, 0.014046671071223926, 1.0801305041861746],
     'uprOverRight': [-0.1277698904501184,
                      -0.0017240145500210247,
                      1.0364692906386268],
     'uprPeak': [0, -0.10848970608268971, 1.1026890245980834],
     'uprPeakRight': [-0.1252550253791018,
                      -0.11449613164451478,
                      1.0483478230802286]}
}

#=============================================================================================================
#>> Define
#=============================================================================================================
def mirror_self(self,primeAxis = 'Left'):
    _str_func = 'mirror_self'
    _idx_state = self.getState(False)
    ml_done = []
    log.debug("|{0}| >> define...".format(_str_func)+ '-'*80)
    ml_mirrorDefineHandles = self.msgList_get('defineSubHandles')
    for mObj in ml_mirrorDefineHandles:
        ml_done.append(mObj)
    r9Anim.MirrorHierarchy().makeSymmetrical([mObj.mNode for mObj in ml_mirrorDefineHandles],
                                             mode = '',primeAxis = primeAxis.capitalize() )    
    
    if _idx_state > 0:
        log.debug("|{0}| >> form...".format(_str_func)+ '-'*80)
        ml_mirrorFormHandles = self.msgList_get('formHandles')
        ml_use = []
        for mObj in ml_mirrorFormHandles:
            if mObj not in ml_done:
                ml_use.append(mObj)
            else:
                ml_done.append(mObj)
                
        r9Anim.MirrorHierarchy().makeSymmetrical([mObj.mNode for mObj in ml_use],
                                                     mode = '',primeAxis = primeAxis.capitalize() )
    
    if _idx_state > 1:
        log.debug("|{0}| >> prerig...".format(_str_func)+ '-'*80)        
        ml_mirrorPreHandles = self.msgList_get('prerigHandles') + self.msgList_get('jointHandles')
        
        ml_use = []
        for mObj in ml_mirrorPreHandles:
            if mObj not in ml_done:
                ml_use.append(mObj)
            else:
                ml_done.append(mObj)
                
        r9Anim.MirrorHierarchy().makeSymmetrical([mObj.mNode for mObj in ml_use],
                                                 mode = '',primeAxis = primeAxis.capitalize() )

#@cgmGEN.Timer
def define(self):
    _str_func = 'define'    
    log.debug("|{0}| >>  ".format(_str_func)+ '-'*80)
    log.debug("{0}".format(self))
    
    _short = self.mNode
    
    #Attributes =========================================================
    ATTR.set_alias(_short,'sy','blockScale')    
    self.setAttrFlags(attrs=['sx','sz','sz'])
    self.doConnectOut('sy',['sx','sz'])

    #ATTR.set_min(_short, 'loftSplit', 1)
    ATTR.set_min(_short, 'paramUprStart', 0.0)
    ATTR.set_min(_short, 'paramLwrStart', 0.0)
    
    
    #Buffer our values...
    _str_defineProfile= self.getEnumValueString('defineProfile')
    
    _str_muzzleSetup = self.getEnumValueString('muzzleSetup')
    _str_noseSetup = self.getEnumValueString('noseSetup')
    _str_jawLwrSetup = self.getEnumValueString('jawLwrSetup')    
    _str_lipsSetup = self.getEnumValueString('lipsSetup')
    _str_teethSetup = self.getEnumValueString('teethSetup')
    _str_cheekSetup = self.getEnumValueString('cheekSetup')
    _str_tongueSetup = self.getEnumValueString('tongueSetup')
    _str_mouthBagSetup = self.getEnumValueString('mouthBagSetup')
    
    #Cleaning =========================================================        
    _shapes = self.getShapes()
    if _shapes:
        log.debug("|{0}| >>  Removing old shapes...".format(_str_func))        
        mc.delete(_shapes)
        defineNull = self.getMessage('defineNull')
        if defineNull:
            log.debug("|{0}| >>  Removing old defineNull...".format(_str_func))
            mc.delete(defineNull)
    ml_handles = []
    
    
    #rigBlock Handle ===========================================================
    log.debug("|{0}| >>  RigBlock Handle...".format(_str_func))            
    _size = MATH.average(self.baseSize[1:])
    
    if self.jointRadius == 1.0:
        self.jointRadius = _size / 10
    
    _crv = CURVES.create_fromName(name='locatorForm',#'axis3d',#'arrowsAxis', 
                                  direction = 'z+', size = _size/4)
    SNAP.go(_crv,self.mNode,)
    CORERIG.override_color(_crv, 'white')        
    CORERIG.shapeParent_in_place(self.mNode,_crv,False)
    mHandleFactory = self.asHandleFactory()
    self.addAttr('cgmColorLock',True,lock=True, hidden=True)
    mDefineNull = self.atUtils('stateNull_verify','define')
    mNoTransformNull = self.atUtils('noTransformNull_verify','define',forceNew=True,mVisLink=self)
    
    #Bounding sphere ==================================================================
    _bb_shape = CURVES.create_controlCurve(self.mNode,'cubeOpen', size = 1.0, sizeMode='fixed')
    mBBShape = cgmMeta.validateObjArg(_bb_shape, 'cgmObject',setClass=True)
    #mScaleNull = mBBShape.doCreateAt(setClass=True)
    #mScaleNull.rename("scaleRef")
    mBBShape.p_parent = mDefineNull    
    mBBShape.tz = -.5
    mBBShape.ty = .5
    
    #mScaleNull.p_parent = mBBShape
    #mScaleNull.p_position = POS.get(mBBShape.mNode,'bb')
    #mScaleNull.dagLock()
    
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
    _str_pose = _str_defineProfile#self.blockProfile#'human'        
    if not _d_scaleSpace.get(_str_defineProfile):
        log.error(cgmGEN.logString_sub(_str_func,'Unregistered scaleSpace blockProfile: {0}'.format(_str_pose)))        
        return False
    l_mainHandles = []
    
    def get_handleScaleSpaces(d_base,d_scaleSpace,key,plug_left,plug_right):
        for k,d in list(d_base.items()):
            if plug_left in k:
                k_use = str(k).replace(plug_left,plug_right)
                _v = copy.copy(d_scaleSpace[_str_pose].get(k_use))
                if _v:
                    _v[0] = -1 * _v[0]
            else:
                _v = d_scaleSpace[key].get(k)
                
            if _v is not None:
                d_base[k]['scaleSpace'] = _v        
    
    #Jaw ---------------------------------------------------------------------
    if self.jawLwrSetup:
        _str_jawLwrSetup = self.getEnumValueString('jawLwrSetup')
        log.debug(cgmGEN.logString_sub(_str_func,'jawLwrSetup: {0}'.format(_str_jawLwrSetup)))
        
        _d_pairs = {}
        _d = {}
        l_sideKeys = ['jaw','jawTop','jawFront','orbFront','orb','jawNeck','cheek','cheekBone',
                      ]
        
        for k in l_sideKeys:
            _d_pairs[k+'Left'] = k+'Right'
        d_pairs.update(_d_pairs)#push to master list...
        

        l_centerKeys = ['jawNeck']
        for k in l_centerKeys:
            _d[k] = {'color':'yellowWhite','tagOnly':1,'arrow':0,'jointLabel':1,'vectorLine':0}
        
        for k in l_sideKeys:
            _d[k+'Left'] =  {'color':'blueBright','tagOnly':1,'arrow':0,'jointLabel':0,'vectorLine':0}
            _d[k+'Right'] =  {'color':'redBright','tagOnly':1,'arrow':0,'jointLabel':0,'vectorLine':0}
        
        get_handleScaleSpaces(_d,_d_scaleSpace,_str_defineProfile,'Left','Right')
        """
        for k,d in _d.iteritems():
            if 'Left' in k:
                k_use = str(k).replace('Left','Right')
                _v = copy.copy(_d_scaleSpace[_str_pose].get(k_use))
                if _v:
                    _v[0] = -1 * _v[0]
            else:
                _v = _d_scaleSpace[_str_pose].get(k)
                
            if _v is not None:
                _d[k]['scaleSpace'] = _v"""
                
        
        _keys = list(_d.keys())
        _keys.sort()
        l_order.extend(_keys)
        d_creation.update(_d)
        
        
        _d_curveCreation = {'jawLine':{'keys':['jawTopLeft','jawLeft','jawNeckLeft','jawFrontLeft',
                                               'jawFrontRight','jawNeckRight','jawRight','jawTopRight'],
                                       'rebuild':False},
                            'cheekLineLeft':{'keys':['jawTopLeft','orbLeft','orbFrontLeft'],
                                       'rebuild':False},
                            'cheekLineRight':{'keys':['jawTopRight','orbRight','orbFrontRight'],
                                             'rebuild':False},
                            'cheekCurveLeft':{'keys':['orbLeft','cheekLeft','jawNeckLeft'],
                                             'rebuild':False},
                            'cheekCurveRight':{'keys':['orbRight','cheekRight','jawNeckRight'],
                                             'rebuild':False},                            
                            'jawUnder':{'keys':['jawNeckRight','jawNeck','jawNeckLeft'],
                                              'rebuild':False},
                            }
        
        if _str_pose == 'human':
            _d_curveCreation['cheekFrameLeft'] = {'keys':['orbFrontLeft','cheekBoneLeft','jawFrontLeft'],
                             'rebuild':False}
            _d_curveCreation['cheekFrameRight'] = {'keys':['orbFrontRight','cheekBoneRight','jawFrontRight'],
                              'rebuild':False}
        elif _str_pose in ['canine','beak']:
            pass
            #_d_curveCreation['cheekFrameLeft'] = {'keys':['orbFrontLeft','cheekBoneLeft','jawNeckLeft'],
            #                 'rebuild':False}
            #_d_curveCreation['cheekFrameRight'] = {'keys':['orbFrontRight','cheekBoneRight','jawNeckRight'],
            #                  'rebuild':False}           
        
        d_curveCreation.update(_d_curveCreation)

    #lip ---------------------------------------------------------------------
    if self.lipSetup:
        _str_lipSetup = self.getEnumValueString('lipSetup')
        log.debug(cgmGEN.logString_sub(_str_func,'lip setup: {0}'.format(_str_lipSetup)))
        
        #Declarations of keys...---------------------------------------------------------------------
        _d_pairs = {}
        _d = {}
        l_sideKeys = ['cornerBag','cornerBack','cornerFront','cornerPeak',
                      'cornerUpr','cornerLwr',
                      'smile',
                      'uprOver','lwrOver',
                      'uprPeak','uprFront','uprBack',
                      'lwrPeak','lwrFront','lwrBack',
                      ]

        l_centerKeys = ['uprFront','uprPeak','uprBack','uprGum',
                        'uprOver','lwrOver',
                        'lwrFront','lwrPeak','lwrBack','lwrGum']
        
        if _str_pose in ['canine','beak']:
            l_sideKeys.extend(['uprPeakOut','uprFrontOut','uprBackOut','uprGumOut','uprOverOut',
                               'lwrPeakOut','lwrFrontOut','lwrBackOut','lwrGumOut','lwrOverOut'])
        
        for k in l_centerKeys:
            _d[k] = {'color':'yellowWhite','tagOnly':1,'arrow':0,'jointLabel':1,'vectorLine':0}
            
        
        for k in l_sideKeys:
            _d[k+'Left'] =  {'color':'blueBright','tagOnly':1,'arrow':0,'jointLabel':0,'vectorLine':0}
            _d[k+'Right'] =  {'color':'redBright','tagOnly':1,'arrow':0,'jointLabel':0,'vectorLine':0}
        
        #Mirror map left/right----------------------------------------------------------------
        for k in l_sideKeys:
            _d_pairs[k+'Left'] = k+'Right'
        d_pairs.update(_d_pairs)#push to master list...        
        
        #Process scaleSpace------------------------------------------------------------------
        get_handleScaleSpaces(_d,_d_scaleSpace,_str_defineProfile,'Left','Right')

        _keys = list(_d.keys())
        _keys.sort()
        l_order.extend(_keys)
        d_creation.update(_d)
        
        #Heirarchy Mapping -------------------------------------------------------------------
        #d_toParent['lwrPeak'] = 'lwrFront'
        #d_toParent['lwrBack'] = 'lwrFront'
        #d_toParent['lwrGum'] = 'lwrFront'
        #d_toParent['lwrPeakLeft'] = 'lwrFront'
        #d_toParent['lwrPeakRight'] = 'lwrFront'        
        
        if _str_pose in ['canine','beak']:
            for k2 in ['upr','lwr']:
                for side in ['Left','Right','']:
                    for k in ['PeakOut','BackOut','GumOut']:
                        d_toParent[k2+k+side] = k2+'FrontOut'+side
                        
            
        for k2 in ['upr','lwr']:
            for side in ['Left','Right','']:
                for k in ['Peak','Back','Gum']:
                    d_toParent[k2+k+side] = k2+'Front'+side
        
        d_toParent['uprFrontLeft'] = 'uprFront'
        d_toParent['uprFrontRight'] = 'uprFront'
        
        d_toParent['lwrFrontLeft'] = 'lwrFront'
        d_toParent['lwrFrontRight'] = 'lwrFront'        
        
        for s in 'Left','Right':
            for k in ['cornerUpr','cornerLwr','cornerBag',
                      'cornerBack','cornerPeak']:
                d_toParent[k+s] = 'cornerFront'+s
            
        l_mainHandles.extend(['cornerFrontLeft','cornerFrontRight',
                              'lwrFrontLeft','lwrFrontRight',
                              'uprFrontLeft','uprFrontRight',
                             'lwrFront','uprFront'])
        
        if _str_pose in ['canine','beak']:
            l_mainHandles.extend(['uprFrontOutLeft','lwrFrontOutLeft',
                                  'uprFrontOutRight','lwrFrontOutRight'])
        
        
        #Curve Mapping 
        _d_curveCreation = {'uprPeak':{'keys':['cornerFrontRight','uprPeakRight','uprPeak',
                                               'uprPeakLeft','cornerFrontLeft'],
                                       'rebuild':0},
                            'lwrPeak':{'keys':['cornerFrontRight','lwrPeakRight','lwrPeak','lwrPeakLeft','cornerFrontLeft'],
                                       'color':'greenWhite',                                       
                                       'rebuild':0},
                            'uprLip':{'keys':['cornerFrontRight','uprFrontRight','uprFront','uprFrontLeft','cornerFrontLeft'],
                                       'rebuild':0},
                            'lwrLip':{'keys':['cornerFrontRight','lwrFrontRight','lwrFront','lwrFrontLeft','cornerFrontLeft'],
                                       'color':'greenWhite',                                       
                                       'rebuild':0},
                            
                            'uprLipBack':{'keys':['cornerBackRight','uprBackRight','uprBack','uprBackLeft','cornerBackLeft'],
                                       'rebuild':0},
                            'lwrLipBack':{'keys':['cornerBackRight','lwrBackRight','lwrBack',
                                                  'lwrBackLeft','cornerBackLeft'],
                                          'color':'greenWhite',                                       
                                          'rebuild':0},                            
                            'lipCrossUpr':{'keys':['uprGum','uprBack','uprFront','uprPeak'],
                                           'rebuild':0},
                            'lipCrossLwr':{'keys':['lwrGum','lwrBack','lwrFront','lwrPeak'],
                                           'color':'greenBright',                                           
                                           'rebuild':0},
                            
                            
                            'lipCrossLwrLeft':{'keys':['lwrBackLeft','lwrFrontLeft','lwrPeakLeft'],
                                               'color':'greenBright',
                                               'rebuild':0},
                            'lipCrossUprLeft':{'keys':['uprBackLeft','uprFrontLeft','uprPeakLeft'],
                                               'rebuild':0},                            
                            
                            'lipCrossLwrRight':{'keys':['lwrBackRight','lwrFrontRight','lwrPeakRight'],
                                                'color':'greenBright',
                                                'rebuild':0},
                            'lipCrossUprRight':{'keys':['uprBackRight','uprFrontRight','uprPeakRight'],
                                                'rebuild':0},
                            
                            'lipCornerLeft':{'keys':['cornerBagLeft','cornerBackLeft',
                                                     'cornerFrontLeft','cornerPeakLeft'],
                                           'color':'blueWhite',                                           
                                           'rebuild':0},
                            'lipCornerRight':{'keys':['cornerBagRight','cornerBackRight',
                                                     'cornerFrontRight','cornerPeakRight'],
                                             'color':'redWhite',                                           
                                             'rebuild':0},

                            'smileLineLeft':{'keys':['cornerPeakLeft','jawFrontLeft'],
                                             'color':'yellowWhite',                                             
                                              'rebuild':0},
                            'smileLineRight':{'keys':['cornerPeakRight','jawFrontRight'],
                                             'color':'yellowWhite',                                             
                                             'rebuild':0},
                            
                            'smileCrossLeft':{'keys':['cornerPeakLeft','smileLeft'],
                                             'color':'yellowWhite',                                             
                                              'rebuild':0},
                            'smileCrossRight':{'keys':['cornerPeakRight','smileRight'],
                                             'color':'yellowWhite',                                             
                                             'rebuild':0},                            
                            }
        
        _d_curveCreation['lipCrossLwr']['keys'].append('lwrOver')
        _d_curveCreation['lipCrossUpr']['keys'].append('uprOver')
        
        _d_curveCreation['lipCrossUprRight']['keys'].append('uprOverRight')
        _d_curveCreation['lipCrossUprLeft']['keys'].append('uprOverLeft')
        
        _d_curveCreation['lipCrossLwrRight']['keys'].append('lwrOverRight')
        _d_curveCreation['lipCrossLwrLeft']['keys'].append('lwrOverLeft')
        
        if self.noseSetup:
            _d_curveCreation['lipCrossUpr']['keys'].append('noseBase')        
        
        if _str_pose in ['canine','beak','muzzle']:
            _d_curveCreation['lipCrossLwrOutRight'] = {'keys':['lwrGumOutRight','lwrBackOutRight',
                                                               'lwrFrontOutRight','lwrPeakOutRight',
                                                               'lwrOverOutRight'],
                                                       'color':'greenBright',
                                                       'rebuild':0}
            _d_curveCreation['lipCrossLwrOutLeft'] = {'keys':['lwrGumOutLeft','lwrBackOutLeft',
                                                              'lwrFrontOutLeft','lwrPeakOutLeft',
                                                              'lwrOverOutLeft'],
                                                      'color':'greenBright',
                                                      'rebuild':0}
            
            _d_curveCreation['lipCrossUprOutRight'] = {'keys':['uprGumOutRight','uprBackOutRight',
                                                               'uprFrontOutRight','uprPeakOutRight',
                                                               'uprOverOutRight'],
                                                       'color':'greenBright',
                                                       'rebuild':0}
            _d_curveCreation['lipCrossUprOutLeft'] = {'keys':['uprGumOutLeft','uprBackOutLeft',
                                                              'uprFrontOutLeft','uprPeakOutLeft',
                                                              'uprOverOutLeft'],
                                                      'color':'greenBright',
                                                      'rebuild':0}
            
            #Snout...
            _d_curveCreation['snoutLeft'] = {'keys':['nostrilBaseLeft','snoutTopLeft','cheekBoneLeft'],
                                             'color':'blueWhite',
                                             'rebuild':1}
            _d_curveCreation['snoutRight'] = {'keys':['nostrilBaseRight','snoutTopRight','cheekBoneRight'],
                                             'color':'redWhite',
                                             'rebuild':1}
            
            
            _d_curveCreation['uprLipOver'] = {'keys':['cornerPeakRight','cornerUprRight',
                                                      'uprOverOutRight','uprOverRight','uprOver',
                                                      'uprOverLeft','uprOverOutLeft',
                                                      'cornerUprLeft','cornerPeakLeft'],
                                       'rebuild':0}
            _d_curveCreation['lwrLipOver'] = {'keys':['cornerPeakRight','cornerLwrRight',
                                                      'lwrOverOutRight','lwrOverRight','lwrOver',
                                                      'lwrOverLeft','lwrOverOutLeft',
                                                      'cornerLwrLeft','cornerPeakLeft'],
                                       'rebuild':0}
            
            _d_curveCreation['uprPeak']['keys'].insert(1,'uprPeakOutRight')
            _d_curveCreation['uprPeak']['keys'].insert(-1,'uprPeakOutLeft')
            
            _d_curveCreation['uprLipBack']['keys'].insert(1,'uprBackOutRight')
            _d_curveCreation['uprLipBack']['keys'].insert(-1,'uprBackOutLeft')
            
            _d_curveCreation['uprLip']['keys'].insert(1,'uprFrontOutRight')
            _d_curveCreation['uprLip']['keys'].insert(-1,'uprFrontOutLeft')
            
            _d_curveCreation['lwrPeak']['keys'].insert(1,'lwrPeakOutRight')
            _d_curveCreation['lwrPeak']['keys'].insert(-1,'lwrPeakOutLeft')
            
            _d_curveCreation['lwrLipBack']['keys'].insert(1,'lwrBackOutRight')
            _d_curveCreation['lwrLipBack']['keys'].insert(-1,'lwrBackOutLeft')
            
            _d_curveCreation['lwrLip']['keys'].insert(1,'lwrFrontOutRight')
            _d_curveCreation['lwrLip']['keys'].insert(-1,'lwrFrontOutLeft')
            
            if self.noseSetup:
                _d_curveCreation['lipCrossUprOutLeft']['keys'].extend(['snoutTopLeft','bridgeOuterLeft'])
                _d_curveCreation['lipCrossUprOutRight']['keys'].extend(['snoutTopRight','bridgeOuterRight'])

        else:#human
            """
            _d_curveCreation['lipToChinRight'] = {'keys':['cornerPeakRight','jawFrontRight'],
                                                  'color':'yellowWhite',
                                                  'rebuild':0}
            _d_curveCreation['lipToChinLeft'] = {'keys':['cornerPeakLeft','jawFrontLeft'],
                                                 'color':'yellowWhite',
                                                  'rebuild':0}"""
            
            _d_curveCreation['uprLipOver'] = {'keys':['cornerPeakRight','cornerUprRight',
                                                      'uprOverRight','uprOver',
                                                      'uprOverLeft',
                                                      'cornerUprLeft','cornerPeakLeft'],
                                       'rebuild':0}
            _d_curveCreation['lwrLipOver'] = {'keys':['cornerPeakRight','cornerLwrRight',
                                                      'lwrOverRight','lwrOver',
                                                      'lwrOverLeft',
                                                      'cornerLwrLeft','cornerPeakLeft'],
                                       'rebuild':0}                                
            
            _d_curveCreation['smileLineLeft']['keys'].remove('jawFrontLeft')
            _d_curveCreation['smileLineRight']['keys'].remove('jawFrontRight')
            
            
        if self.chinSetup or self.jawLwrSetup:
            _d_curveCreation['lipCrossLwrLeft']['keys'].append('chinLeft')
            _d_curveCreation['lipCrossLwrRight']['keys'].append('chinRight')
            
            _d_curveCreation['lipCrossLwrLeft']['keys'].append('jawFrontLeft')
            _d_curveCreation['lipCrossLwrRight']['keys'].append('jawFrontRight')
            
            
        d_curveCreation.update(_d_curveCreation)

        if self.noseSetup:
            d_curveCreation['cheekLineLeft']['keys'].append('sneerLeft')
            d_curveCreation['cheekLineRight']['keys'].append('sneerRight')
            
            if _str_pose in ['canine','muzzle']:
                d_curveCreation['smileLineLeft']['keys'].insert(0,'sneerLeft')
                d_curveCreation['smileLineRight']['keys'].insert(0,'sneerRight')
                
                d_curveCreation['smileLineLeft']['keys'].insert(1,'cheekBoneLeft')
                d_curveCreation['smileLineRight']['keys'].insert(1,'cheekBoneRight')                
                
                if d_curveCreation.get('lipToChinLeft'):
                    d_curveCreation['lipToChinLeft']['keys'].insert(0,'sneerLeft')
                    d_curveCreation['lipToChinRight']['keys'].insert(0,'sneerRight')                
            else:
                d_curveCreation['smileLineLeft']['keys'].insert(0,'nostrilTopLeft')
                d_curveCreation['smileLineRight']['keys'].insert(0,'nostrilTopRight')
                
                d_curveCreation['smileLineLeft']['keys'].insert(1,'nostrilLeft')
                d_curveCreation['smileLineRight']['keys'].insert(1,'nostrilRight')
            
                if d_curveCreation.get('lipToChinLeft'):
                    d_curveCreation['lipToChinLeft']['keys'].insert(0,'nostrilLeft')
                    d_curveCreation['lipToChinRight']['keys'].insert(0,'nostrilRight')
                
            
            _d_curveCreation['lipCrossUprRight']['keys'].append('noseBaseRight')
            _d_curveCreation['lipCrossUprLeft']['keys'].append('noseBaseLeft')            
            
            """
            d_curveCreation['overLipLeft'] = {'keys':['uprPeakLeft','noseBaseLeft',],
                                                'color':'yellowWhite',
                                                'rebuild':0}
            d_curveCreation['overLipRight'] = {'keys':['uprPeakRight','noseBaseRight',],
                                                'color':'yellowWhite',
                                                'rebuild':0}"""
            
            #d_curveCreation['overLip'] = {'keys':['uprPeak','noseBase',],
                                                #'color':'yellowWhite',
                                                #'rebuild':0}            
        if self.jawLwrSetup:
            #if _str_pose not in ['canine']:
                #d_curveCreation['smileLineLeft']['keys'].insert(0,'cheekBoneLeft')
                #d_curveCreation['smileLineRight']['keys'].insert(0,'cheekBoneRight')            
            
            if d_curveCreation.get('cheekFrameLeft'):
                d_curveCreation['cheekFrameLeft']['keys'][-1]='smileLeft'
                d_curveCreation['cheekFrameRight']['keys'][-1]='smileRight'
            
            
            d_curveCreation['smileCrossLeft']['keys'].append('cheekLeft')
            d_curveCreation['smileCrossRight']['keys'].append('cheekRight')            
        
        if self.chinSetup or self.jawLwrSetup:
            #d_curveCreation['smileLineLeft']['keys'][-1] = 'chinLeft'
            #d_curveCreation['smileLineRight']['keys'][-1] = 'chinRight'
            
            
            if d_curveCreation.get('cheekFrameLeft'):
                d_curveCreation['cheekFrameLeft']['keys'].append('chinLeft')
                d_curveCreation['cheekFrameRight']['keys'].append('chinRight')
                
            
            """
            d_curveCreation['underLipLeft'] = {'keys':['lwrPeakLeft','underLipLeft',],
                                                'color':'yellowWhite',
                                                'rebuild':0}
            d_curveCreation['underLipRight'] = {'keys':['lwrPeakRight','underLipRight',],
                                                'color':'yellowWhite',
                                                'rebuild':0}"""
    #mouthbag ================================================================================
    if self.mouthBagSetup:
        log.debug(cgmGEN.logString_sub(_str_func,'Mouth bag: {0}'.format(_str_lipSetup)))
        
        #Declarations of keys...---------------------------------------------------------------------
        _d_pairs = {}
        _d = {}
        l_sideKeys = ['mouthBag']
   
        l_centerKeys = ['mouthBagTop','mouthBagBottom','mouthBagBack']
        
        for k in l_centerKeys:
            _d[k] = {'color':'yellowWhite','tagOnly':1,'arrow':0,'jointLabel':1,'vectorLine':0}
            
        for k in l_sideKeys:
            _d[k+'Left'] =  {'color':'blueBright','tagOnly':1,'arrow':0,'jointLabel':0,'vectorLine':0}
            _d[k+'Right'] =  {'color':'redBright','tagOnly':1,'arrow':0,'jointLabel':0,'vectorLine':0}
        
        #Mirror map left/right----------------------------------------------------------------
        for k in l_sideKeys:
            _d_pairs[k+'Left'] = k+'Right'
        d_pairs.update(_d_pairs)#push to master list...        
        
        #Process scaleSpace------------------------------------------------------------------
        get_handleScaleSpaces(_d,_d_scaleSpace,_str_defineProfile,'Left','Right')
   
        _keys = list(_d.keys())
        _keys.sort()
        l_order.extend(_keys)
        d_creation.update(_d)
        

        #Curve Mapping 
        _d_curveCreation = {'bagTop':{'keys':['mouthBagLeft','mouthBagTop','mouthBagRight'],
                                       'rebuild':0},
                            'bagBottom':{'keys':['mouthBagLeft','mouthBagBottom','mouthBagRight'],
                                         'rebuild':0},
                            'bagCrossHorizontal':{'keys':['mouthBagLeft','mouthBagBack','mouthBagRight'],
                                                  'rebuild':0},
                            'bagCrossVertical':{'keys':['mouthBagTop','mouthBagBack','mouthBagBottom'],
                                                  'rebuild':0},                            
                            }
        
        d_curveCreation.update(_d_curveCreation)
        
        
        if self.lipSetup:
            d_curveCreation['bagCrossHorizontal']['keys'].insert(0,'cornerBagLeft')
            d_curveCreation['bagCrossHorizontal']['keys'].append('cornerBagRight')

            d_curveCreation['bagCrossVertical']['keys'].insert(0,'uprGum')
            d_curveCreation['bagCrossVertical']['keys'].append('lwrGum')
            
            
    #nose ================================================================================
    if self.noseSetup:
        _str_noseSetup = self.getEnumValueString('noseSetup')
        log.debug(cgmGEN.logString_sub(_str_func,'noseSetup: {0}'.format(_str_noseSetup)))
        
        _d_pairs = {}
        _d = {}
        l_sideKeys = ['sneer','nostrilTop','nostril','bridgeOuter',
                      'noseTop','bridge','bulb','noseTip','nostrilBase','noseBase',
                      'nostrilLineInner','nostrilLineOuter',
                      ]
        
        if _str_pose == 'canine':
            l_sideKeys.append('snoutTop')
        
        l_centerKeys = ['noseBase','noseUnder','noseTip','bulb','bridge','noseTop']
        
        
        for k in l_centerKeys:
            _d[k] = {'color':'yellowWhite','tagOnly':1,'arrow':0,'jointLabel':1,'vectorLine':0}
        
        for k in l_sideKeys:
            _d[k+'Left'] =  {'color':'blueBright','tagOnly':1,'arrow':0,'jointLabel':0,'vectorLine':0}
            _d[k+'Right'] =  {'color':'redBright','tagOnly':1,'arrow':0,'jointLabel':0,'vectorLine':0}
        
        
        #Mirror map left/right
        for k in l_sideKeys:
            _d_pairs[k+'Left'] = k+'Right'
        d_pairs.update(_d_pairs)#push to master list...        
        
        #Process
        get_handleScaleSpaces(_d,_d_scaleSpace,_str_defineProfile,'Left','Right')

        _keys = list(_d.keys())
        _keys.sort()
        l_order.extend(_keys)
        d_creation.update(_d)        
        
        
        _d_curveCreation = {'noseProfile':{'keys':['noseTop','bridge','bulb','noseTip','noseUnder','noseBase'],
                                   'rebuild':False},
                            'noseProfileLeft':{'keys':['noseTopLeft','bridgeLeft','bulbLeft',
                                                       'noseTipLeft','nostrilLineOuterLeft'],
                                               'rebuild':False},
                            'noseProfileRight':{'keys':['noseTopRight','bridgeRight','bulbRight',
                                                       'noseTipRight','nostrilLineOuterRight'],
                                               'rebuild':False},                            
                            
                            'noseCross':{'keys':['nostrilRight','noseTipRight','noseTip',
                                                 'noseTipLeft','nostrilLeft'],
                                           'rebuild':False},
                            'noseRight':{'keys':['sneerRight','bridgeOuterRight','nostrilTopRight','nostrilRight','nostrilBaseRight'],
                                         'rebuild':False},
                            'noseLeft':{'keys':['sneerLeft','bridgeOuterLeft','nostrilTopLeft','nostrilLeft','nostrilBaseLeft'],
                                         'rebuild':False},                            
                            #'noseLeft':{'keys':['sneerLeft','noseLeft'],
                            #             'rebuild':False},                            
                            #'noseUnder':{'keys':['nostrilBaseRight','noseUnder','nostrilBaseLeft'],
                            #               'rebuild':False},
                            'noseBridge':{'keys':['bridgeOuterRight',
                                                  'bridgeRight',
                                                  'bridge',
                                                  'bridgeLeft',
                                                  'bridgeOuterLeft'],
                                          'rebuild':False},
                            
                            'noseBase':{'keys':['nostrilBaseRight','noseBaseRight','noseBase','noseBaseLeft','nostrilBaseLeft'],'rebuild':False},
                            
                            'nostrilRight':{'keys':['nostrilBaseRight','nostrilLineOuterRight',
                                                    'nostrilLineInnerRight','noseBaseRight'],
                                           'rebuild':False},
                            'nostrilLeft':{'keys':['nostrilBaseLeft','nostrilLineOuterLeft',
                                                    'nostrilLineInnerLeft','noseBaseLeft'],
                                           'rebuild':False},
                            
                            'noseTipUnder':{'keys':['nostrilLineInnerRight',
                                                    'noseUnder',
                                                    'nostrilLineInnerLeft',
                                                    ],'rebuild':False},
                            
                            
                            'noseBulb':{'keys':['nostrilTopRight','bulbRight','bulb','bulbLeft','nostrilTopLeft'],
                                           'rebuild':False},
                            'bridgeTop':{'keys':['sneerRight','noseTopRight','noseTop','noseTopLeft','sneerLeft'],
                                         'rebuild':False},
                            }
        d_curveCreation.update(_d_curveCreation)
        
        d_curveCreation['cheekLineLeft']['keys'].append('sneerLeft')
        d_curveCreation['cheekLineRight']['keys'].append('sneerRight')
        
        if self.jawLwrSetup:
            if _str_pose in ['human']:
                d_curveCreation['frontPlaneLeft'] = {'keys':['nostrilTopLeft','cheekBoneLeft'],
                                                     'color':'blueWhite',
                                                     'rebuild':0}
                d_curveCreation['frontPlaneRight'] = {'keys':['nostrilTopRight','cheekBoneRight'],
                                                    'color':'redWhite',
                                                    'rebuild':0}
        
        if _str_pose == 'canine':
            d_curveCreation['noseLeft']['keys'].insert(1,'bridgeOuterLeft')
            d_curveCreation['noseRight']['keys'].insert(1,'bridgeOuterRight')
            
            d_curveCreation['noseBridge']['keys'].append('bridgeOuterLeft')
            d_curveCreation['noseBridge']['keys'].insert(0,'bridgeOuterRight')
            
    
    if self.chinSetup or self.jawLwrSetup:
        _str_chinSetup = self.getEnumValueString('chinSetup')
        log.debug(cgmGEN.logString_sub(_str_func,'chinSetup: {0}'.format(_str_chinSetup)))
        
        _d_pairs = {}
        _d = {}
        l_sideKeys = ['chin',#'underLip',
                      ]        
        #l_centerKeys = ['noseBase','noseUnder','noseTip','bulb','bridge','noseTop']
        #for k in l_centerKeys:
        #    _d[k] = {'color':'yellowWhite','tagOnly':1,'arrow':0,'jointLabel':1,'vectorLine':0}
        
        for k in l_sideKeys:
            _d[k+'Left'] =  {'color':'blueBright','tagOnly':1,'arrow':0,'jointLabel':0,'vectorLine':0}
            _d[k+'Right'] =  {'color':'redBright','tagOnly':1,'arrow':0,'jointLabel':0,'vectorLine':0}
        
        #Mirror map left/right
        for k in l_sideKeys:
            _d_pairs[k+'Left'] = k+'Right'
        d_pairs.update(_d_pairs)#push to master list...        
        
        #Process
        get_handleScaleSpaces(_d,_d_scaleSpace,_str_defineProfile,'Left','Right')

        _keys = list(_d.keys())
        _keys.sort()
        l_order.extend(_keys)
        d_creation.update(_d)
        
        
        _d_curveCreation = {'chinLine':{'keys':['chinRight','chinLeft'],
                                   'rebuild':False},
                            #'underLip':{'keys':['underLipRight','underLipLeft'],
                            #            'rebuild':False},                            
                            }
        d_curveCreation.update(_d_curveCreation)
        
        if self.lipSetup:
            #d_curveCreation['smileLineLeft']['keys'][-1] = 'chinLeft'
            #d_curveCreation['smileLineRight']['keys'][-1] = 'chinRight'
            
            #d_curveCreation['lipToChinLeft']['keys'].insert(-1,'underLipLeft')
            #d_curveCreation['lipToChinRight']['keys'].insert(-1,'underLipRight')
            
            if d_curveCreation.get('lipToChinLeft'):
                d_curveCreation['lipToChinLeft']['keys'].insert(-1,'chinLeft')
                d_curveCreation['lipToChinRight']['keys'].insert(-1,'chinRight')
            
        #if self.jawLwrSetup:
            #d_curveCreation['cheekFrameLeft']['keys'][-1] = 'chinLeft'
            #d_curveCreation['cheekFrameRight']['keys'][-1] = 'chinRight'
            


    #make em... ==============================================================================================
    size_locForm = self.jointRadius
    for tag,d in list(d_creation.items()):
        if tag in l_mainHandles:
            d_creation[tag]['shape'] = 'locatorForm'
            d_creation[tag]['jointScale'] = False
            d_creation[tag]['size'] = size_locForm
            
        else:
            d_creation[tag]['jointScale'] = True
        
    log.debug("|{0}| >>  Make the handles...".format(_str_func))    
    md_res = self.UTILS.create_defineHandles(self, l_order, d_creation,self.jointRadius, mDefineNull, mBBShape,
                                             forceSize=1, )
    
    
    md_handles = md_res['md_handles']
    ml_handles = md_res['ml_handles']
    
    for k,p in list(d_toParent.items()):
        try:md_handles[k].p_parent = md_handles[p]
        except Exception as err:
            log.error(cgmGEN.logString_msg(_str_func,'{0} | {1}'.format(k,err)))
    idx_ctr = 0
    idx_side = 0
    d = {}
    ml_toController = []
    for tag,mHandle in list(md_handles.items()):
        if tag not in l_mainHandles:
            #if cgmGEN.__mayaVersion__ >= 2018:
            #    mController = mHandle.controller_get()
            #    mController.visibilityMode = 2
            ml_toController.append(mHandle)
            
        mHandle._verifyMirrorable()
        _center = True
        for p1,p2 in list(d_pairs.items()):
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
    for k,m in list(d_pairs.items()):
        md_handles[k].mirrorSide = 1
        md_handles[m].mirrorSide = 2
        md_handles[k].mirrorIndex = idx_side
        md_handles[m].mirrorIndex = idx_side
        md_handles[k].doStore('mirrorHandle',md_handles[m])
        md_handles[m].doStore('mirrorHandle',md_handles[k])
        idx_side +=1

    #Curves -------------------------------------------------------------------------
    log.debug("|{0}| >>  Make the curves...".format(_str_func))
    
    for k,d in list(d_curveCreation.items()):
        if "Left" in k:
            d_curveCreation[k]['color'] = 'blueWhite'
        elif "Right" in k:
            d_curveCreation[k]['color'] = 'redWhite'
            
    
    md_resCurves = self.UTILS.create_defineCurve(self, d_curveCreation, md_handles, mNoTransformNull)
    self.msgList_connect('defineHandles',ml_handles)#Connect    
    self.msgList_connect('defineSubHandles',ml_handles)#Connect
    self.msgList_connect('defineCurves',md_resCurves['ml_curves'])#Connect
    
    self.atUtils('controller_wireHandles',ml_toController,'define')
    
    return

#=============================================================================================================
#>> Form
#=============================================================================================================
def formDelete(self):
    _str_func = 'formDelete'
    log.debug("|{0}| >> ...".format(_str_func)+ '-'*80)
    log.debug("{0}".format(self))
    ml_defSubHandles = self.msgList_get('defineSubHandles')
    for mObj in ml_defSubHandles:
        mObj.template = False    
        mObj.v = 1    
            
    try:self.defineLoftMesh.template = False
    except:pass
    self.bbHelper.v = True
    
    for mObj in self.msgList_get('defineCurves'):
        mObj.template=0
        mObj.v=1
    
    
#@cgmGEN.Timer
def form(self):
    _str_func = 'form'
    log.debug("|{0}| >>  ".format(_str_func)+ '-'*80)
    log.debug("{0}".format(self))
    
    _short = self.p_nameShort
    #_baseNameAttrs = ATTR.datList_getAttrs(self.mNode,'nameList')
    
    #Initial checks ===============================================================================
    log.debug("|{0}| >> Initial checks...".format(_str_func)+ '-'*40)    

    #Create temple Null  ==================================================================================
    mFormNull = BLOCKUTILS.formNull_verify(self)
    mNoTransformNull = self.atUtils('noTransformNull_verify','form')
    
    mHandleFactory = self.asHandleFactory()
    
    self.bbHelper.v = False
    _size = MATH.average(self.baseSize[1:])
    
    _str_pose = self.blockProfile#'human'        
    
    
    #Gather all our define dhandles and curves -----------------------------
    log.debug("|{0}| >> Get our define curves/handles...".format(_str_func)+ '-'*40)    

    md_handles = {}
    md_dCurves = {}
    d_defPos = {}
    
    ml_defineHandles = self.msgList_get('defineSubHandles')
    for mObj in ml_defineHandles:
        md_handles[mObj.handleTag] = mObj
        d_defPos[mObj.handleTag] = mObj.p_position
        
    for mObj in self.msgList_get('defineCurves'):
        md_dCurves[mObj.handleTag] = mObj
        #mObj.template=1
        mObj.v = 0
        
        
    #pprint.pprint(vars())
    
    #
    d_pairs = {}
    d_creation = {}
    l_order = []
    d_curveCreation = {}
    ml_subHandles = []
    md_loftCreation = {}
    

    
    pSmileR = False
    pSmileL = False
    
    d_handlePosDat = {}
    
    
    d_color = {'left':'blueWhite',
               'right':'redWhite',
               'center':'yellowWhite'}
    d_handleBase = {'tagOnly':True,'arrow':False,'jointLabel':0,'vectorLine':False}
    
    
    #Main setup -----------------------------------------------------
    if self.lipSetup:
        log.debug("|{0}| >>  lip setup...".format(_str_func))
        _str_lipSetup = self.getEnumValueString('lipSetup')
        
        #For now we just need to generate some extra data for one of our curves...the others we'll just use the define curves for
        
        #We need to generate a couple of positions
        
        p_lipCornerAdd_l = DGETAVG([d_defPos['cornerFrontLeft'],
                                    d_defPos['cornerBackLeft']])
        p_lipCornerAdd_r = DGETAVG([d_defPos['cornerFrontRight'],
                                    d_defPos['cornerBackRight']])            
        
        
        d_lipDat = {'upr':{'count':self.numLipShapersUpr},
                    'lwr':{'count':self.numLipShapersLwr},
                    }
        
        
        _l_clean = []
        d_uprHandles = {}
        for tag in 'upr','lwr':
            
            #Get our base curves...
            d_baseCurves = {}
            d_handlePosDat_lips = {}
            
            #LipOver
            for t in ['Peak','LipBack']:
                d_baseCurves[t] = md_dCurves[tag+t].mNode
            
            #We need to redfine the lipCurve... ---------------------------------------------
            l_pos = [p_lipCornerAdd_r,
                     #d_defPos['cornerFrontRight'],
                     d_defPos[tag+'FrontRight'],
                     d_defPos[tag+'Front'],
                     d_defPos[tag+'FrontLeft'],
                     #d_defPos['cornerFrontLeft'],
                     p_lipCornerAdd_l,
                     ]
            
            crv_lip = CORERIG.create_at(create='curve',l_pos = l_pos,baseName = tag+'Peak') 
            d_baseCurves['Lip'] = crv_lip
            _l_clean.append(crv_lip)
            
            #Now we need a gum curve ...-----------------------------
            l_pos = [d_defPos['cornerBagRight'],
                     d_defPos[tag+'Gum'],
                     d_defPos['cornerBagLeft'],
                     ]                
            crv_gumLine = CORERIG.create_at(create='curve',l_pos = l_pos,baseName = tag+'Gum') 
            d_baseCurves['Gum'] = crv_gumLine
            _l_clean.append(crv_gumLine)
            
            
            #Now we need an arc curve -----------------------------------------------
            _res_tmp = mc.loft([md_dCurves[tag+'Peak'].mNode,
                                md_dCurves[tag+'Lip'].mNode],
                                           o = True, d = 1, po = 0, c = False,u=False, autoReverse=0,ch=True)                
            str_meshShape = TRANS.shapes_get(_res_tmp[0])[0]
        
            #Get our curves...
            crv_arc = SURF.get_surfaceSplitCurves(str_meshShape,count = 3, mode='u')[0]
            
            _l_clean.extend(_res_tmp+[crv_arc])
            d_baseCurves['Arc'] = crv_arc
            

           
            _count = d_lipDat[tag]['count']
            if MATH.is_even(_count):
                b_even = True
                log.debug("|{0}| >>  lips | Even...".format(_str_func))
            else:
                b_even = False
                log.debug("|{0}| >>  lips | odd...".format(_str_func))
            
            _keyCenter = None
            l_keys_crv = []
            l_curveOrder = ['Peak','Arc','Lip','LipBack','Gum']
            #LipOver
            
            
            if self.mouthBagSetup:
                if tag == 'upr':
                    #Now we need a mouthBagUp
                    l_pos = [d_defPos['mouthBagRight'],
                             d_defPos['mouthBagTop'],
                             d_defPos['mouthBagLeft'],
                             ]                
                    _crv = CORERIG.create_at(create='curve',l_pos = l_pos,baseName = tag+'bagTop') 
                    d_baseCurves['bagTop'] = _crv
                    _l_clean.append(_crv)                    
                    l_curveOrder.append('bagTop')
                    
                    #Now we need a mouthBagBack
                    l_pos = [d_defPos['mouthBagRight'],
                             d_defPos['mouthBagBack'],
                             d_defPos['mouthBagLeft'],
                             ]                
                    _crv = CORERIG.create_at(create='curve',l_pos = l_pos,baseName = tag+'bagBack') 
                    d_baseCurves['bagBack'] = _crv
                    _l_clean.append(_crv)                
                         
                    l_curveOrder.append('bagBack')
                    
                else:
                    #Now we need a mouthBagUp
                    l_pos = [d_defPos['mouthBagRight'],
                             d_defPos['mouthBagBottom'],
                             d_defPos['mouthBagLeft'],
                             ]
                    
                    _crv = CORERIG.create_at(create='curve',l_pos = l_pos,baseName = tag+'bagBottom') 
                    d_baseCurves['bagBottom'] = _crv
                    _l_clean.append(_crv)                    
                    l_curveOrder.append('bagBottom')                    
                
                
            for k in l_curveOrder:
                crv = d_baseCurves[k]
                _l_split =  CURVES.getUSplitList(crv,_count,rebuild=1)
                
                if tag == 'lwr' or k in ['Arc']:#Get rid of the ends because we share...
                    _l_split.pop(0)
                    _l_split.pop(-1)
                    
                if tag == 'upr' and k in ['bagBack']:
                    _l_split.pop(0)
                    _l_split.pop(-1)
                    
                    
                #Now to split the positional data by left right
                _mid = MATH.get_midIndex(len(_l_split))
                
                if b_even:
                    _l_right = _l_split[:_mid]
                    _l_left = _l_split[_mid:]
                    
                else:
                    _midV = _l_split[_mid]
                    _l_right = _l_split[:_mid]
                    _l_left = _l_split[_mid+1:]
                    
                    
                    _keyCenter = "{0}_{1}_center".format(tag,k)
                    d_use = copy.copy(d_handleBase)
                    d_use['color'] = d_color['center']
                    d_use['pos'] = _midV
                    d_defPos[_keyCenter] = _midV
                    
                    d_creation[_keyCenter] = d_use
                    l_order.append(_keyCenter)
                    
                _l_left.reverse()#reverse dat for mirror indexing
                    
                #Now we need to split out our handle create dat
                l_handlesLeft = []
                l_handlesRight = []
                
                for i,p in enumerate(_l_right):
                    _key_l = "{0}_{1}_{2}_left".format(tag,k,i)
                    _key_r = "{0}_{1}_{2}_right".format(tag,k,i)
                    
                    d_pairs[_key_l] = _key_r
                    
                    l_order.extend([_key_l,_key_r])
                    
                    #Right...
                    d_use = copy.copy(d_handleBase)
                    d_use['color'] = d_color['right']
                    d_use['pos'] = p
                    d_creation[_key_r] = d_use
                    l_handlesRight.append(_key_r)
                    d_defPos[_key_r] = p
                    
                    #Left...
                    d_use = copy.copy(d_handleBase)
                    d_use['color'] = d_color['left']
                    d_use['pos'] = _l_left[i]
                    d_creation[_key_l] = d_use
                    d_defPos[_key_l] = _l_left[i]
                    
                    l_handlesLeft.append(_key_l)
                
                #Then curve create dat...
                _keys = copy.copy(l_handlesRight)
                if _keyCenter:
                    _keys.append(_keyCenter)
                l_handlesLeft.reverse()
                _keys.extend(l_handlesLeft)
                
                if tag == 'upr':
                    d_uprHandles[k] = copy.copy(_keys)
                elif k not in ['Arc']:
                    k_use = k
                    if k_use == 'bagBottom':
                        k_use = 'bagTop'
                    _keys.insert(0,d_uprHandles[k_use][0])
                    _keys.append(d_uprHandles[k_use][-1])
                    
                    
                k_crv = "{0}_{1}".format(tag,k)
                l_keys_crv.append(k_crv)
                d_curveCreation[k_crv] = {'keys':_keys,
                                          'rebuild':1}
                
                #Setup base loft list

                #for i,p in enumerate(_l_split):
                    #LOC.create(position=p,name = "{0}_{1}_{2}_loc".format(tag,k,i))
                    
            #Some fixes for arc
            d_curveCreation['{0}_Arc'.format(tag)]['keys'].insert(0, d_curveCreation['upr_Peak']['keys'][0])
            d_curveCreation['{0}_Arc'.format(tag)]['keys'].append(d_curveCreation['upr_Peak']['keys'][-1])
            
            
            if tag == 'lwr':
                l_keys_crv.append('upr_bagBack')
                
            l_keysLip = l_keys_crv[:5]
            l_mouthBagKeys = l_keys_crv[4:]
            
            if tag == 'lwr':
                l_keysLip.reverse()
                
                
            
            md_loftCreation[tag+'Lip'] =  {'keys':l_keysLip,
                                           'rebuild':{'spansU':7,'spansV':7,'degreeU':3},
                                           'uDriver':'{0}.numLoftLip_u'.format(_short),
                                           'vDriver':'{0}.numLoftLip_v'.format(_short),
                                           'kws':{'noRebuild':True}}
            

            if tag == 'lwr':
                l_mouthBagKeys.reverse()
                
            md_loftCreation[tag+'mouthBag'] =  {'keys':l_mouthBagKeys,
                                           'rebuild':{'spansU':7,'spansV':7,'degreeU':3},
                                           'uDriver':'{0}.numLoftBag_u'.format(_short),
                                           'vDriver':'{0}.numLoftLip_v'.format(_short),
                                           'kws':{'noRebuild':True}}
            
            
            
            
            """
            #Let's define our arc data....
            log.debug("|{0}| >>  {1} arc...".format(_str_func,tag))
            
            #Generate a curve...
            l_pos = [p_lipCornerAdd_r,
                     DGETAVG([d_defPos[tag+'front'],d_defPos[tag+'peak']]),
                     p_lipCornerAdd_l
                     ]                                
            crv_arc = CORERIG.create_at(create='curve',l_pos = l_pos,baseName = tag+'Peak') 
            
            _l_split =  CURVES.getUSplitList(crv_arc,5,rebuild=0)
            _l_split = _l_split[1:-1]#cull start end
            
            _key_r = "{0}_arc_right".format(tag)
            _key_l = "{0}_arc_left".format(tag)
            _key_c = "{0}_arc_center".format(tag)
            
            for i,p in enumerate(_l_split):"""
                
            
            
            
            
            
            #Split...
            #Handles...
            #Curves...
            
            


   
        """
        
        _res_tmp = mc.loft(l_bulbCurves,
                           o = True, d = 1, po = 0, c = False,u=False, autoReverse=0,ch=True)
                            
        str_meshShape = TRANS.shapes_get(_res_tmp[0])[0]
        l_knots = SURF.get_dat(str_meshShape, uKnots=True)['uKnots']
        
        pprint.pprint(l_knots)
        
        crv_bulb_2 = mc.duplicateCurve("{0}.u[{1}]".format(str_meshShape,MATH.average(l_knots[:2])),
                                       ch = 0, rn = 0, local = 0)[0]
        
        crv_bulb_4 = mc.duplicateCurve("{0}.u[{1}]".format(str_meshShape,MATH.average(l_knots[1:])),
                                       ch = 0, rn = 0, local = 0)[0]
        """

        mc.delete(_l_clean)        
        #pprint.pprint(d_curveCreation)
        #return        

    if self.noseSetup:
        log.debug("|{0}| >>  nose setup...".format(_str_func))
        _str_noseSetup = self.getEnumValueString('noseSetup')
        _d_pairs = {}

        d_handlePosDat_nose = {}
        
        d_noseCurves = {}
        d_noseHandles = {'bridge':
                        {'center':
                         {0:{},
                          1:{0:'bridge'},
                          2:{},
                          3:{0:'noseTop'}},
                         'left':
                         {0:{},
                          1:{0:'bridgeOuterLeft',
                             2:'bridgeLeft'},
                          2:{},
                          3:{0:'sneerLeft',
                             2:'noseTopLeft'},},
                         'right':
                         {0:{},
                          1:{0:'bridgeOuterRight',
                             2:'bridgeRight'},
                          2:{},
                          3:{0:'sneerRight',
                             2:'noseTopRight'},}},
                        
                        'bulb':
                        {'center':
                         {0:{0:'noseBase'},
                          1:{0:'noseUnder'},
                          2:{},
                          3:{0:'noseTip'},
                          4:{},
                          5:{0:'bulb'}},
                         'left':
                         {0:{0:'nostrilBaseLeft',
                             2:'noseBaseLeft'
                             },
                          1:{0:'nostrilBaseLeft',
                             1:'nostrilLineOuterLeft',
                             2:'nostrilLineInnerLeft'},
                          2:{},
                          3:{0:'nostrilLeft',
                             3:'noseTipLeft'},
                          4:{},
                          5:{0:'nostrilTopLeft',
                             2:'bulbLeft'}},
                         'right':
                         {0:{0:'nostrilBaseRight',
                             2:'noseBaseRight'
                             },
                          1:{0:'nostrilBaseRight',
                             1:'nostrilLineOuterRight',
                             2:'nostrilLineInnerRight'},
                          2:{},
                          3:{0:'nostrilRight',
                             3:'noseTipRight'},
                          4:{},
                          5:{0:'nostrilTopRight',
                             2:'bulbRight'}},
                         }}
        
        #Position gather ---------------------------------------------------------------------
        #We need some base positions....
        #bulb...
        d_handlePosDat_nose['bulb'] = {}
        d_handlePosDat_nose['bulb']['center'] = {}
        d_handlePosDat_nose['bulb']['center'][2] = {}
        
        d_handlePosDat_nose['bulb']['center'][2][0] = DGETAVG([d_defPos['noseUnder'],
                                                          d_defPos['noseTip']])
        
        #d_handlePosDat_nose['bulb']['center'][4] = {}
        """d_handlePosDat_nose['bulb']['center'][0][0] = DGETAVG([d_defPos['noseTip'],
                                                       d_defPos['bulb']])"""
        
        
        #bridge...
        d_handlePosDat_nose['bridge'] = {}
        d_handlePosDat_nose['bridge']['center'] = {}
        
        d_handlePosDat_nose['bridge']['center'][0] = {}
        d_handlePosDat_nose['bridge']['center'][0][0] = DGETAVG([d_defPos['bulb'],
                                                            d_defPos['bridge']])
        
        d_handlePosDat_nose['bridge']['center'][2] = {}
        d_handlePosDat_nose['bridge']['center'][2][0] = DGETAVG([d_defPos['noseTop'],
                                                            d_defPos['bridge']])            
        


        """
        {section: side : curve idx: handle idx}
        
        """
        #Sides...
        _d_pos_bulb = d_handlePosDat_nose['bulb']#...connect
        _d_pos_bridge = d_handlePosDat_nose['bridge']#...connect
        _l_clean = []
        

        
        for side in 'left','right':
            _cap = STR.capFirst(side)
            
            #Bulb...-----------------------------------------------------------------------------
            #_d_pos_bulb[side] = {}#...declare
            _d_tmp = {}
            _d_pos_bulb[side] = _d_tmp#...declare
            
            #Bulb 0...
            _d_tmp[0] = {}
            
            _d_tmp[0][1] = DGETAVG([d_defPos['noseBase'+_cap],
                                    d_defPos['nostrilBase'+_cap]])
            
            #We need some tmp stuff to find some curves
            
            #Bulb 2...after
            
            #Bulb 3...
            _d_tmp[3] = {}
            _d_tmp[3][1] = DPCTDIST(d_defPos['nostril'+_cap],
                                    d_defPos['noseTip'+_cap],
                                    .3)
            _d_tmp[3][2] = DPCTDIST(d_defPos['nostril'+_cap],
                                    d_defPos['noseTip'+_cap],
                                    .6)
            
            _d_tmp[3][4] = DGETAVG([d_defPos['noseTip'+_cap],
                                    d_defPos['noseTip']])
            
            #Bulb 4...after
            
            
            #Bulb 5
            _d_tmp[5] = {}
            
            _d_tmp[5][1] = DGETAVG([d_defPos['nostrilTop'+_cap],
                                    d_defPos['bulb'+_cap]])
            _d_tmp[5][3] = DGETAVG([d_defPos['bulb'],
                                    d_defPos['bulb'+_cap]])                                
            
            
            #Bridge...-----------------------------------------------------------------------------
            _d_tmp = {}
            _d_pos_bridge[side] = _d_tmp#...declare                
            
            #Bridge 0...
            _d_tmp[0] = {}
            
            _d_tmp[0][0] = DGETAVG([d_defPos['bridgeOuter'+_cap],
                                       d_defPos['nostrilTop'+_cap]])
            _d_tmp[0][2] = DGETAVG([d_defPos['bridge'+_cap],
                                       d_defPos['bulb'+_cap]])
            
            _d_tmp[0][1] = DGETAVG([_d_tmp[0][0],
                                   _d_tmp[0][2]])
            
            #Bridge 1...
            _d_tmp[1] = {}
            _d_tmp[1][1] = DGETAVG([d_defPos['bridgeOuter'+_cap],
                                       d_defPos['bridge'+_cap]])

            #Bridge 2...
            _d_tmp[2] = {}
            
            _d_tmp[2][0] = DGETAVG([d_defPos['bridgeOuter'+_cap],
                                       d_defPos['sneer'+_cap]])
            _d_tmp[2][2] = DGETAVG([d_defPos['bridge'+_cap],
                                       d_defPos['noseTop'+_cap]])
            _d_tmp[2][1] = DGETAVG([_d_tmp[2][0],
                                   _d_tmp[2][2]])                
            
            #Bridge 3...
            _d_tmp[3] = {}
            _d_tmp[3][1] = DGETAVG([d_defPos['noseTop'+_cap],
                                    d_defPos['sneer'+_cap]])                
            

        crv_bulbBase = CORERIG.create_at(create='curve',l_pos = [d_defPos['nostrilBaseRight'],
                                                                 d_defPos['nostrilLineOuterRight'],
                                                                 d_defPos['nostrilLineInnerRight'],
                                                                 d_defPos['noseUnder'],
                                                                 d_defPos['nostrilLineInnerLeft'],
                                                                 d_defPos['nostrilLineOuterLeft'],
                                                                 d_defPos['nostrilBaseLeft'],
                                                                 ])                            
        _l_clean.append(crv_bulbBase)
        
        
        #We need a tmp loft for the bulb to get some data...
        l_bulbCurves = [crv_bulbBase,
                        md_dCurves['noseCross'].mNode,
                        md_dCurves['noseBulb'].mNode
                        ]
        
        _res_tmp = mc.loft(l_bulbCurves,
                           o = True, d = 1, po = 0, c = False,u=False, autoReverse=0,ch=True)
                            
        str_meshShape = TRANS.shapes_get(_res_tmp[0])[0]
        l_knots = SURF.get_dat(str_meshShape, uKnots=True)['uKnots']
        
        pprint.pprint(l_knots)
        
        crv_bulb_2 = mc.duplicateCurve("{0}.u[{1}]".format(str_meshShape,MATH.average(l_knots[:2])),
                                       ch = 0, rn = 0, local = 0)[0]
        
        crv_bulb_4 = mc.duplicateCurve("{0}.u[{1}]".format(str_meshShape,MATH.average(l_knots[1:])),
                                       ch = 0, rn = 0, local = 0)[0]
        
        
        
        #_l_pos = CURVES.getUSplitList(_crv,_split,rebuild=1)
        _l_clean.extend([crv_bulb_2,crv_bulb_4] + _res_tmp)
        #Splitting out values for the generated curves
        
        for i,crv in enumerate([crv_bulb_2,crv_bulb_4]):
            if not i:
                _split = 11
                _idx = 2
            else:
                _split = 9
                _idx = 4
            
            _l_split =  CURVES.getUSplitList(crv,_split,rebuild=1)
            
            _mid = MATH.get_midIndex(_split)
            
            _midV = _l_split[_mid]
            
            _l_right = _l_split[:_mid]
            _l_left = _l_split[_mid+1:]
            _l_left.reverse()
            
            _d_pos_bulb['center'][_idx] = {0:_midV}
            _d_pos_bulb['right'][_idx] = {}
            _d_pos_bulb['left'][_idx] = {}
            
            for ii,v in enumerate(_l_right):
                _d_pos_bulb['right'][_idx][ii] = v
                
            for ii,v in enumerate(_l_left):
                _d_pos_bulb['left'][_idx][ii] = v                
            
        for section,d_section in list(d_handlePosDat_nose.items()):
            for side,d_crv in list(d_section.items()):
                for i,d_pos in list(d_crv.items()):
                    for ii,p in list(d_pos.items()):
                        _key = "{0}_{1}_{2}_{3}".format(section,i,ii,side)
                        
                        if side == 'left':d_pairs[_key] =  "{0}_{1}_{2}_{3}".format(section,i,ii,'right')
                        
                        l_order.append(_key)
                        d_defPos[_key] = p
                        d_use = copy.copy(d_handleBase)
                        d_use['color'] = d_color[side]
                        d_use['pos'] = p
                        
                        d_creation[_key] = d_use
                        
                        d_noseHandles[section][side][i][ii] = _key
                        #LOC.create(position=p,name = "{0}_loc".format(_key))
                        
        
        #Loop to gather handles
        for section,d_section in list(d_noseHandles.items()):
            d_noseCurves[section] = {}
            
            #Loop to gather handles
            l_crvIdx = []
            for side,d_crv in list(d_section.items()):
                d_noseCurves[section][side] = {}

                for i,d_handle in list(d_crv.items()):
                    if i not in l_crvIdx:
                        l_crvIdx.append(i)
                    k_crv = "{0}_{1}_{2}".format(section,i,side)
                    d_noseCurves[section][side][i] = {'key':k_crv,
                                                     'handles':[]}
                    #for ii,handle in list(d_handle.items()):
                    #    d_noseCurves[section][side][i]['handles'].append(handle)
                    for ii in sorted(d_handle):
                        d_noseCurves[section][side][i]['handles'].append(d_handle[ii])
            
            #Now we need to sort those handles
            for i in l_crvIdx:
                if not d_noseCurves[section]['right'].get(i):
                    continue
                k_crv = "{0}_{1}".format(section,i)
                
                l_r = d_noseCurves[section]['right'][i]['handles']
                l_c = d_noseCurves[section]['center'][i]['handles']
                l_l = d_noseCurves[section]['left'][i]['handles']
                l_l.reverse()
                
                d_curveCreation[k_crv] = {'keys':l_r + l_c + l_l,
                                          'rebuild':1}
            
        l_noseKeys = ['bulb_0','bulb_1','bulb_2','bulb_3','bulb_4','bulb_5',
                                            'bridge_0','bridge_1','bridge_2','bridge_3']
        l_noseKeys.reverse()
        md_loftCreation['nose'] =  {'keys':l_noseKeys,
                                   'rebuild':{'spansU':30,'spansV':5,'degreeU':3},
                                   'uDriver':'{0}.numLoftNose_u'.format(_short),
                                   'vDriver':'{0}.numLoftNose_v'.format(_short),
                                   'kws':{'noRebuild':True}}
        
        #pprint.pprint(d_noseHandles)
        #pprint.pprint(d_curveCreation)
        mc.delete(_l_clean)
    
    if self.jawLwrSetup:
        log.debug("|{0}| >>  Jaw setup...".format(_str_func))
        _str_jawLwrSetup = self.getEnumValueString('jawLwrSetup')
        
        _d_pairs = {}
        d_handlePosDat_jaw = {}
        
        _d_curveCreateDat = {
            'cheek_0':{'h':{0:'orbFront',2:'orb',4:'jawTop'}},
            
            'cheek_1':{},
            'cheek_2':{},
            'cheek_3':{},
            'chin_0':{},
            'chin_1':{},                
        }
        
        """
        How do I need the data...
        l_order - append handles to make
        d_creation - keyed to order handle
        
        crv_list - by handle key
        surface lists
        """
        
        d_jawCurves = {}
        d_jawHandles = {'cheek':
                        {'left':
                         {0:{0:'orbFrontLeft',
                             2:'orbLeft',
                             4:'jawTopLeft'},
                          1:{0:'cheekBoneLeft'},
                          2:{0:'smileLeft',
                             2:'cheekLeft',
                             4:'jawLeft'},
                          3:{2:'jawNeckLeft'},
                          4:{}},
                        'right':
                         {0:{0:'orbFrontRight',
                             2:'orbRight',
                             4:'jawTopRight'},
                          1:{0:'cheekBoneRight'},
                          2:{0:'smileRight',
                             2:'cheekRight',
                             4:'jawRight'},
                          3:{2:'jawNeckRight'},
                          4:{}}},
                        
                        'chin':
                        {'center':
                         {0:{4:'jawNeck'}},
                          'left':
                          {0:{0:'chinLeft',
                              2:'jawFrontLeft',
                              }},
                          'right':
                          {0:{0:'chinRight',
                              2:'jawFrontRight',
                              }}
                         }}
        #'chin':
        #{'center':{0:{0:{}}}}}
        #pprint.pprint(d_jawHandles)
        #return
        
        
        #Position gather ---------------------------------------------------------------------
        
        #We need some base positions....
        d_handlePosDat_jaw['chin'] = {}
        d_handlePosDat_jaw['chin']['center'] = {}
        d_handlePosDat_jaw['chin']['center'][0] = {}
        
        _d_chin = d_handlePosDat_jaw['chin']['center'][0]
        
        
        _d_chin[0] = DGETAVG([d_defPos['chinLeft'],
                              d_defPos['chinRight']])
        
        _d_chin[2] = DGETAVG([d_defPos['jawFrontLeft'],
                              d_defPos['jawFrontRight']])
        
        _d_chin[1]= DGETAVG([_d_chin[0],
                           _d_chin[2]])
        _d_chin[3] = DGETAVG([d_handlePosDat_jaw['chin']['center'][0][2],
                              d_defPos['jawNeck']])            
        
        
        """
        {section: side : curve idx: handle idx}
        
        """
        #Sides...
        d_handlePosDat_jaw['cheek'] = {}#...declare
        _d_handle_pos = d_handlePosDat_jaw['cheek']#...connect
        
        for side in 'left','right':
            _d_tmp = {}
            _d_handle_pos[side] = _d_tmp
            d_handlePosDat_jaw['chin'][side]= {}#...declare
            _l_clean = []
            
            _cap = STR.capFirst(side)
        
            crv_jawLeft = CORERIG.create_at(create='curve',l_pos = [d_defPos['jawTop'+_cap],
                                                                    d_defPos['jaw'+_cap],
                                                                    d_defPos['jawNeck']
                                                                    ])
            _l_clean.append(crv_jawLeft)
            
            #...cheek 0....
            _d_tmp[0] = {}
            
            _d_tmp[0][1] = DGETAVG([d_defPos['orbFront'+_cap],
                                       d_defPos['orb'+_cap]])
            _d_tmp[0][3] = DGETAVG([d_defPos['orb'+_cap],
                                       d_defPos['jawTop'+_cap]])
            
            #...cheek 1...
            _d_tmp[1] = {}
            
            _d_tmp[1][2] = DGETAVG([d_defPos['orb'+_cap],
                                    d_defPos['cheek'+_cap]])
            
            _d_tmp[1][1] = DGETAVG([_d_tmp[1][2],
                                    d_defPos['cheekBone'+_cap]])
            
            _d_tmp[1][4] = CRVPCT(crv_jawLeft,.2)
            
            _d_tmp[1][3] = DGETAVG([_d_tmp[1][4],
                                    _d_tmp[1][2]])
            
            
            #...cheek 2...
            _d_tmp[2] = {}
            
            #_d_tmp[2][4] = CRVPCT(crv_jawLeft,.4)
            
            _d_tmp[2][1] = DGETAVG([d_defPos['smile'+_cap],
                                       d_defPos['cheek'+_cap]])
            _d_tmp[2][3] = DGETAVG([d_defPos['cheek'+_cap],
                                    d_defPos['jaw'+_cap]])#_d_tmp[2][4]])
            
            #...cheek 3...
            _d_tmp[3] = {}
            
            crv_chinSplit = CORERIG.create_at(create='curveLinear',l_pos = [d_defPos['smile'+_cap],
                                                                    d_defPos['chin'+_cap],
                                                                    d_handlePosDat_jaw['chin']['center'][0][0]
                                                                    ])
            _l_clean.append(crv_chinSplit)
            
            _d_tmp[3][0] = CRVPCT(crv_chinSplit,.3)
            
            crv_cheek3Split = CORERIG.create_at(create='curve',l_pos = [_d_tmp[3][0],
                                                                        d_defPos['jawNeck'+_cap],
                                                                        d_defPos['jaw'+_cap],
                                                                        ])
            _l_clean.append(crv_cheek3Split)
            
            _d_tmp[3][1] = CRVPCT(crv_cheek3Split,.2)
            _d_tmp[3][4] = CRVPCT(crv_jawLeft,.6)
            
            
            #...cheek 4...
            _d_tmp[4] = {}
            
            crv_4Find = CORERIG.create_at(create='curve',l_pos = [d_defPos['cheek'+_cap],
                                                                    d_defPos['jawNeck'+_cap],
                                                                    d_handlePosDat_jaw['chin']['center'][0][3],
                                                                    ])
            _l_clean.append(crv_4Find)
            
            _d_tmp[4][0] = CRVPCT(crv_chinSplit,.5)
            _d_tmp[4][3]  = CRVPCT(crv_jawLeft,.8)
            _d_tmp[4][2]  =  DGETAVG([d_defPos['jawNeck'+_cap],
                                        d_defPos['jawFront'+_cap]])
            _d_tmp[4][1]  = DGETAVG([_d_tmp[4][0] ,
                                     _d_tmp[4][2] ])
            
       
            
            #...chin...
            _d_tmp = d_handlePosDat_jaw['chin'][side]
            _d_tmp[0] = {}
            
            _d_tmp[0][4] = CRVPCT(crv_jawLeft,.9)
            _d_tmp[0][1] = DGETAVG([ d_defPos['chin'+_cap],
                                     d_defPos['jawFront'+_cap]])
            _d_tmp[0][3] = DGETAVG([d_defPos['jawFront'+_cap],
                                    d_handlePosDat_jaw['chin'][side][0][4]])             
            
            
            mc.delete(_l_clean)
            
        for section,d_section in list(d_handlePosDat_jaw.items()):
            for side,d_crv in list(d_section.items()):
                for i,d_pos in list(d_crv.items()):
                    for ii,p in list(d_pos.items()):
                        _key = "{0}_{1}_{2}_{3}".format(section,i,ii,side)
                        
                        if side == 'left':d_pairs[_key] =  "{0}_{1}_{2}_{3}".format(section,i,ii,'right')
                        
                        l_order.append(_key)
                        
                        d_use = copy.copy(d_handleBase)
                        d_use['color'] = d_color[side]
                        d_use['pos'] = p
                        
                        d_creation[_key] = d_use
                        d_defPos[_key] = p
                        
                        d_jawHandles[section][side][i][ii] = _key
                        #LOC.create(position=p,name = "{0}_loc".format(_key))
                        
                    
        for section,d_section in list(d_jawHandles.items()):
            d_jawCurves[section] = {}
            for side,d_crv in list(d_section.items()):
                d_jawCurves[section][side] = {}
                for i,d_handle in list(d_crv.items()):
                    k_crv = "{0}_{1}_{2}".format(section,i,side)
                    d_jawCurves[section][side][i] = {'key':k_crv,
                                                     'handles':[]}
                    
                    #for ii,handle in list(d_handle.items()):
                    #    d_jawCurves[section][side][i]['handles'].append(handle)
                    for ii in sorted(d_handle):
                        d_jawCurves[section][side][i]['handles'].append(d_handle[ii])
                        
                    d_curveCreation[k_crv] = {'keys':d_jawCurves[section][side][i]['handles'],
                                              'rebuild':True}
                        
                        
        
        md_loftCreation['jaw'] =  {'keys':['cheek_0_left','cheek_1_left','cheek_2_left',
                                           'cheek_3_left','cheek_4_left',
                                           'chin_0_left','chin_0_center','chin_0_right',
                                           'cheek_4_right','cheek_3_right','cheek_2_right',
                                           'cheek_1_right','cheek_0_right'],
                                   'rebuild':{'spansU':30,'spansV':5,'degreeU':3},
                                   'uDriver':'{0}.numLoftJaw_u'.format(_short),
                                   'vDriver':'{0}.numLoftJaw_v'.format(_short),
                                   'kws':{'noRebuild':True}}
        
        #pprint.pprint(d_jawHandles)
        #pprint.pprint(d_jawCurves)
    

        
        """
        if self.lipSetup:
            pSmileR = DIST.get_average_position([md_handles['cheekBoneRight'].p_position,
                                                    md_handles['chinRight'].p_position])
            pSmileL = DIST.get_average_position([md_handles['cheekBoneLeft'].p_position,
                                                        md_handles['chinLeft'].p_position])
            _d['smileLeft'] = {'color':'blueSky','tagOnly':True,'arrow':False,'jointLabel':0,
                               'vectorLine':False,'pos':pSmileL}
            _d['smileRight'] = {'color':'redWhite','tagOnly':True,'arrow':False,'jointLabel':0,
                               'vectorLine':False,'pos':pSmileR}
            
            l_order.extend(['smileLeft','smileRight'])
            _d_pairs['smileLeft']='smileRight'"""

    # ==========================================================================================
    # Bridges
    # ==========================================================================================        
    log.debug(cgmGEN.logString_sub(_str_func,'Bridges'))

    d_bridgeDat = {'upr':{},
                   'lwr':{}}
    #for i,l in d_bridgeDat['upr'][side]['handles'].iteritems():
    
    l_overHandles = []
    l_underHandles = []
    r_overHandles = []
    r_underHandles = []
        
    if self.lipSetup:#Bridge Lip setup ----------------------------------------------------------------------
        _count_over = self.numLipOverSplit 
        _count_under = self.numLipUnderSplit
        
        
        
        log.debug(cgmGEN.logString_sub(_str_func,'over lip'))
        #Get our base curves to split our loft
        
        l_curves_baseLoft = []
        _l_clean = []
        
        #Get our base curves...
        d_baseCurves = {}
        d_handlePosDat_lips = {}
        d_overUnderDat = {'over':{},
                          'under':{}}
        
        for t in ['Peak','LipOver']:
            l_curves_baseLoft.append(md_dCurves['upr'+t].mNode)
            
        
        if self.noseSetup:
            #We need a new base curve...
            l_baseTmp = ['cornerPeakRight',
                         'cornerFrontRight',
                         'uprPeakRight',
                         'uprPeak',
                         'uprPeakLeft',
                         'cornerFrontLeft',
                         'cornerPeakLeft']
            crv_base = CORERIG.create_at(create='curve',
                                        l_pos = [d_defPos[k] for k in l_baseTmp],
                                        baseName='base')
            l_curves_baseLoft[0] = crv_base
            _l_clean.append(crv_base)
            
            #End Curve
            l_nose_underTags = ['nostrilRight',
                                'bulb_2_0_right',
                                'nostrilBaseRight',
                                'bulb_0_1_right',
                                'noseBaseRight',
                                'noseBase',
                                'noseBaseLeft',
                                'bulb_0_1_left',
                                'nostrilBaseLeft',
                                'bulb_2_0_left',
                                'nostrilLeft']

            #l_tmpTags = ['smileRight'] + l_nose_underTags + ['smileLeft']
            crv_end = CORERIG.create_at(create='curve',
                                        l_pos = [d_defPos[k] for k in l_nose_underTags],
                                        baseName='end')                 
            _l_clean.append(crv_end)
            l_curves_baseLoft.append(crv_end)
            
            
            l_endKeys = copy.copy(l_nose_underTags)
            d_tmp = {'right':[],'left':[]}
            
            #for side in 'right','left':
                #for i,l in d_bridgeDat['upr'][side]['handles'].iteritems():
                    #d_tmp[side].append(l[-1])
                    
            #l_endKeys = ['cheekBoneRight'] + d_tmp['right'] + l_nose_underTags + d_tmp['left'] + ['cheekBoneLeft']
            d_curveCreation['overEnd'] = {'keys':l_endKeys,
                                          'rebuild':1}
            
            #Make our new over start curve
            l_overStart = ['cornerPeakRight'] + d_curveCreation['upr_Peak']['keys'] + ['cornerPeakLeft']
            d_curveCreation['overStart'] = {'keys':l_overStart,
                                            'rebuild':1}

        else:
            l_nose_underTags = ['nostrilRight',
                                'nostrilBaseRight',
                                'noseBaseRight',
                                'noseBase',
                                'noseBaseLeft',
                                'nostrilBaseLeft',
                                'nostrilLeft']                
            l_endKeys = copy.copy(l_nose_underTags)
            d_tmp = {'right':[],'left':[]}

            d_curveCreation['overEnd'] = {'keys':l_endKeys,
                                          'rebuild':1}
            
            l_overStart = ['cornerPeakRight'] + d_curveCreation['upr_Peak']['keys'] + ['cornerPeakLeft']
            d_curveCreation['overStart'] = {'keys':l_overStart,
                                            'rebuild':1}
            pass
            #raise ValueError,"Finish this"


        #Loft/baseCurves ----------------------------------------------------------------------------------
        _res_tmp = mc.loft(l_curves_baseLoft,
                           o = True, d = 1, po = 0, c = False,u=False, autoReverse=0,ch=True)                
        str_meshShape = TRANS.shapes_get(_res_tmp[0])[0]
        _l_clean.extend(_res_tmp)
    
        #Get our curves...
        l_crvs = SURF.get_surfaceSplitCurves(str_meshShape,count = _count_over+2, mode='u')
        _l_clean.extend(l_crvs)
        
        

        d_uprHandles = {}
        
        #Get our handle values...
        tag = 'overJoin'
        l_keys_crv = []
        for i,crv in enumerate(l_crvs):
            _l_split =  CURVES.getUSplitList(crv,d_lipDat['upr']['count'],rebuild=1)
            l_handlesLeft = []
            l_handlesRight = []
            
            d_overUnderDat['over'][i] = {}
            
            
            #Pop start and end as we'll use the upr handles
            #_l_split.pop(0)
            #_l_split.pop(-1)
                
            #Now to split the positional data by left right
            _mid = MATH.get_midIndex(len(_l_split))
            
            if b_even:
                _l_right = _l_split[:_mid]
                _l_left = _l_split[_mid:]
                
            else:
                _midV = _l_split[_mid]
                _l_right = _l_split[:_mid]
                _l_left = _l_split[_mid+1:]
                
                
                _keyCenter = "{0}_{1}_center".format(tag,i)
                d_use = copy.copy(d_handleBase)
                d_use['color'] = d_color['center']
                d_use['pos'] = _midV
                d_defPos[_keyCenter] = _midV
                
                d_creation[_keyCenter] = d_use
                l_order.append(_keyCenter)
                
            _l_left.reverse()#reverse dat for mirror indexing
                
            #Now we need to split out our handle create dat
            
            
            
            for ii,p in enumerate(_l_right):
                #if crv == l_crvs[-1] and p == _l_right[0]:
                    #l_handlesRight.append('smileRight')
                    #l_handlesLeft.append('smileLeft')
                    #continue
                _key_l = "{0}_{1}_{2}_left".format(tag,i,ii)
                _key_r = "{0}_{1}_{2}_right".format(tag,i,ii)
                
                d_pairs[_key_l] = _key_r
                
                l_order.extend([_key_l,_key_r])
                
                #Right...
                d_use = copy.copy(d_handleBase)
                d_use['color'] = d_color['right']
                d_use['pos'] = p
                d_creation[_key_r] = d_use
                l_handlesRight.append(_key_r)
                d_defPos[_key_r] = p
                
                #Left...
                d_use = copy.copy(d_handleBase)
                d_use['color'] = d_color['left']
                d_use['pos'] = _l_left[ii]
                d_creation[_key_l] = d_use
                d_defPos[_key_l] = _l_left[ii]
                
                l_handlesLeft.append(_key_l)
                
                #LOC.create(position=_l_left[ii],name=_key_l)
                #LOC.create(position=p,name=_key_r)
                
            
            #Then curve create dat...
            _keys = copy.copy(l_handlesRight)
            if _keyCenter:
                _keys.append(_keyCenter)
            l_handlesLeft.reverse()
            _keys.extend(l_handlesLeft)
            
            l_overHandles.append(_keys[-1])
            r_overHandles.append(_keys[0])

            #_keys.insert(0,d_bridgeDat['upr']['right']['handles'][-1])
            #_keys.append(d_bridgeDat['upr']['left']['handles'][-1])
            
            d_uprHandles[i] = copy.copy(_keys)
            
            d_overUnderDat['over'][i]['handles'] = copy.copy(_keys)
            
            k_crv = "{0}_{1}".format(tag,i)
            l_keys_crv.append(k_crv)
            d_curveCreation[k_crv] = {'keys':_keys,
                                      'rebuild':1}                

            #mc.delete(l_crvs + _res_tmp + [crv_start,crv_end])
            #l_keys_crv.insert(0,'lwr_Peak')
            
            
        #l_keys_crv.insert(0,md_loftCreation['uprLip']['keys'][0])
        l_keys_crv.insert(0,'overStart')
        l_keys_crv.append('overEnd')
        
        l_keys_crv.reverse()
        md_loftCreation['overLip'] =  {'keys':l_keys_crv,
                                       'rebuild':{'spansU':30,'spansV':5,'degreeU':3},
                                       'uDriver':'{0}.numLoftLipOver_u'.format(_short),
                                       'vDriver':'{0}.numLoftLip_v'.format(_short),
                                       'kws':{'noRebuild':True}}
            
        mc.delete(_l_clean)
        
        #Underlip ==================================================================================
        log.debug(cgmGEN.logString_sub(_str_func,'under lip'))
        l_curves_baseLoft = []
        _l_clean = []
        
        
        #Start..
        l_baseTmp = ['cornerPeakRight',
                     'cornerFrontRight',
                     'lwrPeakRight',
                     'lwrPeak',
                     'lwrPeakLeft',
                     'cornerFrontLeft',
                     'cornerPeakLeft']
        crv_base = CORERIG.create_at(create='curve',
                                    l_pos = [d_defPos[k] for k in l_baseTmp],
                                    baseName='base')
        l_curves_baseLoft.append( crv_base)
        _l_clean.append(crv_base)

            
        #End...
        l_baseTmp = ['cornerLwrRight', 'lwrOverRight', 'lwrOver', 'lwrOverLeft', 'cornerLwrLeft']
        crv_end = CORERIG.create_at(create='curve',
                                    l_pos = [d_defPos[k] for k in l_baseTmp],
                                    baseName='base')
        l_curves_baseLoft.append( crv_end)
        _l_clean.append(crv_end)
        
        #Make our new over start curve
        l_underStart = ['cornerPeakRight'] + d_curveCreation['lwr_Peak']['keys'] + ['cornerPeakLeft']
        d_curveCreation['underStart'] = {'keys':l_underStart,
                                        'rebuild':1}
            
            
        #Loft/baseCurves ----------------------------------------------------------------------------------
        _res_tmp = mc.loft(l_curves_baseLoft,
                           o = True, d = 1, po = 0, c = False,u=False, autoReverse=0,ch=True)                
        str_meshShape = TRANS.shapes_get(_res_tmp[0])[0]
        _l_clean.extend(_res_tmp)
    
        #Get our curves...
        l_crvs = SURF.get_surfaceSplitCurves(str_meshShape,count = _count_under+2, mode='u',cullStartEnd=False)
        #We need the end curve in this case...
        mc.delete(l_crvs[0])            
        l_crvs.pop(0)
        _l_clean.extend(l_crvs)
        
        tag = 'underJoin'
        l_keys_crv = []
        for i,crv in enumerate(l_crvs):
            _l_split =  CURVES.getUSplitList(crv,d_lipDat['lwr']['count'],rebuild=1)
            l_handlesLeft = []
            l_handlesRight = []
            
            d_overUnderDat['under'][i] = {}
            
            #Pop start and end as we'll use the upr handles
            #_l_split.pop(0)
            #_l_split.pop(-1)
                
            #Now to split the positional data by left right
            _mid = MATH.get_midIndex(len(_l_split))
            
            if b_even:
                _l_right = _l_split[:_mid]
                _l_left = _l_split[_mid:]
                
            else:
                _midV = _l_split[_mid]
                _l_right = _l_split[:_mid]
                _l_left = _l_split[_mid+1:]
                
                
                _keyCenter = "{0}_{1}_center".format(tag,i)
                d_use = copy.copy(d_handleBase)
                d_use['color'] = d_color['center']
                d_use['pos'] = _midV
                d_defPos[_keyCenter] = _midV
                
                d_creation[_keyCenter] = d_use
                l_order.append(_keyCenter)
                
            _l_left.reverse()#reverse dat for mirror indexing
                
            #Now we need to split out our handle create dat
            
            
            
            for ii,p in enumerate(_l_right):
                #if crv == l_crvs[-1] and p == _l_right[0]:
                    #l_handlesRight.append('smileRight')
                    #l_handlesLeft.append('smileLeft')
                    #continue
                _key_l = "{0}_{1}_{2}_left".format(tag,i,ii)
                _key_r = "{0}_{1}_{2}_right".format(tag,i,ii)
                
                d_pairs[_key_l] = _key_r
                
                l_order.extend([_key_l,_key_r])
                
                #Right...
                d_use = copy.copy(d_handleBase)
                d_use['color'] = d_color['right']
                d_use['pos'] = p
                d_creation[_key_r] = d_use
                l_handlesRight.append(_key_r)
                d_defPos[_key_r] = p
                
                #Left...
                d_use = copy.copy(d_handleBase)
                d_use['color'] = d_color['left']
                d_use['pos'] = _l_left[ii]
                d_creation[_key_l] = d_use
                d_defPos[_key_l] = _l_left[ii]
                
                l_handlesLeft.append(_key_l)
                
                #LOC.create(position=_l_left[ii],name=_key_l)
                #LOC.create(position=p,name=_key_r)
                
            
            #Then curve create dat...
            _keys = copy.copy(l_handlesRight)
            if _keyCenter:
                _keys.append(_keyCenter)
            l_handlesLeft.reverse()
            _keys.extend(l_handlesLeft)

            #_keys.insert(0,d_bridgeDat['upr']['right']['handles'][-1])
            #_keys.append(d_bridgeDat['upr']['left']['handles'][-1])
            
            
            d_overUnderDat['under'][i]['handles'] = copy.copy(_keys)
            
            k_crv = "{0}_{1}".format(tag,i)
            l_keys_crv.append(k_crv)
            d_curveCreation[k_crv] = {'keys':_keys,
                                      'rebuild':1}                

            #mc.delete(l_crvs + _res_tmp + [crv_start,crv_end])
            #l_keys_crv.insert(0,'lwr_Peak')
            
            l_underHandles.append(_keys[-1])
            r_underHandles.append(_keys[0])
            
        #l_keys_crv.insert(0,md_loftCreation['uprLip']['keys'][0])
        l_keys_crv.insert(0,'underStart')
        #l_keys_crv.append('overEnd')
        
        md_loftCreation['underLip'] =  {'keys':l_keys_crv,
                                       'rebuild':{'spansU':30,'spansV':5,'degreeU':3},
                                       'uDriver':'{0}.numLoftLipUnder_u'.format(_short),
                                       'vDriver':'{0}.numLoftLip_v'.format(_short),
                                       'kws':{'noRebuild':True}}
            
        mc.delete(_l_clean)            

        
        #We need to generate a surface to flow our -------------------------------------------------
        
        #Need to make lipline curve
        
        l_lipLineUpr = d_curveCreation['overStart']['keys'][:2] + d_curveCreation['upr_Arc']['keys'] + d_curveCreation['overStart']['keys'][-2:]
        
        l_lipLineLwr = d_curveCreation['overStart']['keys'][:2] + d_curveCreation['lwr_Arc']['keys'] + d_curveCreation['overStart']['keys'][-2:]
        
        d_curveCreation['uprLipLine'] = {'keys':l_lipLineUpr,
                                         'rebuild':1}
        d_curveCreation['lwrLipLine'] = {'keys':l_lipLineLwr,
                                         'rebuild':1}            
        
        
        l_lipMask_crvs = md_loftCreation['overLip']['keys'] + ['uprLipLine','lwrLipLine'] + md_loftCreation['underLip']['keys']
        md_loftCreation['attachLips'] = {'keys':l_lipMask_crvs,
                                         'rebuild':{'spansU':12,'spansV':12,'degreeU':3},
                                         #'uDriver':'{0}.numLoftLipUnder_u'.format(_short),
                                         #'vDriver':'{0}.numLoftLip_v'.format(_short),
                                         'kws':{'noRebuild':True}}
        
        
    
    
    
    if self.jawLwrSetup:#Bridge...chin------------------------------------------------------------------
        log.debug(cgmGEN.logString_sub(_str_func,'Bridge | jaw dat'))
        
        
        if self.noseSetup:
            log.debug(cgmGEN.logString_sub(_str_func,'Nose to Jaw Bridge'))
            
            d_bridgeTargets = {'left':{
            'start':['sneerLeft',
                     'bridge_2_0_left',
                     'bridgeOuterLeft',
                     'bridge_0_0_left',
                     'nostrilTopLeft',
                     'bulb_4_0_left',
                     'nostrilLeft'],
            'end':['orbFrontLeft','cheekBoneLeft','smileLeft']},
                               'right':{
            'start':['sneerRight',
                     'bridge_2_0_right',
                     'bridgeOuterRight',
                     'bridge_0_0_right',
                     'nostrilTopRight',
                     'bulb_4_0_right',
                     'nostrilRight',
                     ],
            'end':['orbFrontRight','cheekBoneRight','smileRight']}}
            
            if l_overHandles:#Add in our over split handles if they're there
                l_overHandles.reverse()
                r_overHandles.reverse()

                l_overHandles.append('cornerPeakLeft')
                r_overHandles.append('cornerPeakRight')
                
                d_bridgeTargets['left']['start'].extend(l_overHandles)
                d_bridgeTargets['right']['start'].extend(r_overHandles)                
            
            if self.numBridgeSplit:
                #First get our start curves to split
                log.debug(cgmGEN.logString_msg(_str_func,'Split...'))

                for side,d_side in list(d_bridgeTargets.items()):
                    d_tmpCurves = {}
                    d_dat = d_bridgeDat['upr']
                    d_dat[side] = {'handles':{},
                                   'crvs':[]}
                    _cap = STR.capFirst(side)
 
                    
                    #Declare our start /end
                    k_startCrv = 'uprJoin'+STR.capFirst(side)+'Start'
                    k_endCrv = 'uprJoin'+STR.capFirst(side)+'End'
                    
                    d_curveCreation[k_startCrv] = {'keys':d_bridgeTargets[side]['start'],'rebuild':1}
                    d_curveCreation[k_endCrv] = {'keys':d_bridgeTargets[side]['end'],'rebuild':1}
                    
                    for tag,keys in list(d_side.items()):
                        l_pos = []
                        for k in keys:
                            l_pos.append(d_defPos[k])
                            
                            
                        d_tmpCurves[tag] = CORERIG.create_at(create='curve',l_pos = l_pos)
                        
                    
                    
                    _res_tmp = mc.loft([d_tmpCurves['start'],d_tmpCurves['end']],
                                       o = True, d = 1, po = 0, c = False,u=False, autoReverse=0,ch=True)
                                        
                    str_meshShape = TRANS.shapes_get(_res_tmp[0])[0]
                    
                    #Get our curves...
                    l_crvs = SURF.get_surfaceSplitCurves(str_meshShape,count = self.numBridgeSplit + 2,
                                                         mode='u')
                    
                    #Get our handle values...
                    for i,crv in enumerate(l_crvs):
                        _l_split =  CURVES.getUSplitList(crv,3,rebuild=1)
                        d_dat[side]['handles'][i] = []
                        
                        for ii,p in enumerate(_l_split):
                            _key = "uprJoin_{0}_{1}_{2}".format(i,ii,side)
                            
                            if side == 'left':d_pairs[_key] =  "uprJoin_{0}_{1}_{2}".format(i,ii,'right')
                            
                            l_order.append(_key)
                            d_defPos[_key] = p
                            d_use = copy.copy(d_handleBase)
                            d_use['color'] = d_color[side]
                            d_use['pos'] = p
                            
                            d_creation[_key] = d_use
                            
                            d_dat[side]['handles'][i].append(_key)
                            
                            #LOC.create(position=p,name=_key)
                            
                        k_crv = 'uprJoin_{0}_{1}'.format(i,side)
                        d_dat[side]['crvs'].append(k_crv)
                        
                        d_curveCreation[k_crv] = {'keys':d_dat[side]['handles'][i],
                                                  'rebuild':1}
 
                    mc.delete([d_tmpCurves['start'],d_tmpCurves['end']] + l_crvs + _res_tmp)
                    
                    l_crv_keys = [k_startCrv] + d_dat[side]['crvs'] + [k_endCrv]
                    
                    
                    if side == 'left':
                        l_crv_keys.reverse()
                    md_loftCreation['uprJoin'+_cap] =  {'keys':l_crv_keys,
                                                     'rebuild':{'spansU':30,'spansV':5,'degreeU':3},
                                                     'uDriver':'{0}.numLoftBridge_v'.format(_short),
                                                     'vDriver':'{0}.numLoftBridge_u'.format(_short),
                                                     'kws':{'noRebuild':True}}
                    
                    #pprint.pprint(md_loftCreation['uprJoin'+_cap])
                    

            else:
                log.debug(cgmGEN.logString_sub(_str_func,'simple bridge'))
                
                d_curveCreation['noseToCheekLeftStart'] = {'keys':['sneerLeft',
                                                              'bridge_2_0_left',
                                                              'bridgeOuterLeft',
                                                              'bridge_0_0_left',
                                                              'nostrilTopLeft'],
                                                           'rebuild':1}
                d_curveCreation['noseToCheekRightStart'] = {'keys':['sneerRight',
                                                              'bridge_2_0_right',
                                                              'bridgeOuterRight',
                                                              'bridge_0_0_right',
                                                              'nostrilTopRight'],
                                                           'rebuild':1}
                
                d_curveCreation['noseToCheekLeftEnd'] = {'keys':['orbFrontLeft','cheekBoneLeft'],
                                                         'rebuild':0}
                d_curveCreation['noseToCheekRightEnd'] = {'keys':['orbFrontRight', 'cheekBoneRight'],
                                                           'rebuild':0}
                
                md_loftCreation['noseJoinLeft'] =  {'keys':['noseToCheekLeftStart',
                                                            'noseToCheekLeftEnd'],
                                                 'rebuild':{'spansU':30,'spansV':5,'degreeU':3},
                                                 'uDriver':'{0}.numLoftJaw_u'.format(_short),
                                                 'vDriver':'{0}.numLoftJaw_v'.format(_short),
                                                 'kws':{'noRebuild':True}}
                
                md_loftCreation['noseJoinRight'] =  {'keys':['noseToCheekRightStart',
                                                            'noseToCheekRightEnd'],
                                                 'rebuild':{'spansU':30,'spansV':5,'degreeU':3},
                                                 'uDriver':'{0}.numLoftJaw_u'.format(_short),
                                                 'vDriver':'{0}.numLoftJaw_v'.format(_short),
                                                 'kws':{'noRebuild':True}}
                
        
        
        
        if self.lipSetup:
            log.debug(cgmGEN.logString_sub(_str_func,'Lip to jaw bridge'))
            
            
            d_curveCreation['lipToChinEnd'] = {'keys':['smileRight',
                                                       'cheek_3_0_right',
                                                       'cheek_4_0_right',
                                                       'chinRight',
                                                       'chin_0_0_center',
                                                       'chinLeft',
                                                       'cheek_4_0_left',
                                                       'cheek_3_0_left',
                                                       'smileLeft'],
                                             'rebuild':0}
            
            
            d_bridgeTargets = {'start': ['cornerPeakRight',
                                         'cornerFrontRight',
                                         'lwrPeakRight',
                                         'lwrPeak',
                                         'lwrPeakLeft',
                                         'cornerFrontLeft',
                                         'cornerPeakLeft'],
                               'end':['smileRight',
                                      'cheek_3_0_right',
                                      'cheek_4_0_right',
                                      'chinRight',
                                      'chin_0_0_center',
                                      'chinLeft',
                                      'cheek_4_0_left',
                                      'cheek_3_0_left',
                                      'smileLeft']}
            
            
            l_startKeys = ['cornerPeakRight']
            if r_underHandles:
                #r_underHandles.reverse()
                l_startKeys.extend(r_underHandles)
            l_startKeys.extend(d_curveCreation[md_loftCreation['underLip']['keys'][-1]]['keys'])
            if l_underHandles:
                l_underHandles.reverse()                    
                l_startKeys.extend(l_underHandles)
            l_startKeys.append('cornerPeakLeft')
            
            d_bridgeTargets['start'] = l_startKeys
                           
            d_curveCreation['lipToChinStart'] = {'keys':l_startKeys,
                                               'rebuild':1}                
            

            """
            if l_overHandles:#Add in our over split handles if they're there
                l_overHandles.reverse()
                r_overHandles.reverse()
                
                d_bridgeTargets['left']['start'].extend(l_overHandles)
                d_bridgeTargets['right']['start'].extend(r_overHandles)
                
                l_overHandles.append('cornerPeakLeft')
                r_overHandles.append('cornerPeakRight')"""
                
            
            
            if self.numBridgeSplit:
                #First get our start curves to split
                log.debug(cgmGEN.logString_msg(_str_func,'Split...'))
                
                crv_start = CORERIG.create_at(create='curve',
                                              l_pos = [d_defPos[k] for k in d_bridgeTargets['start']],baseName='start') 
            
                crv_end = CORERIG.create_at(create='curve',
                                            l_pos = [d_defPos[k] for k in d_bridgeTargets['end']],baseName='end') 
            
            
                _res_tmp = mc.loft([crv_start,crv_end],
                               o = True, d = 1, po = 0, c = False,u=False, autoReverse=0,ch=True)                
                
                str_meshShape = TRANS.shapes_get(_res_tmp[0])[0]
                
                #Get our curves...
                l_crvs = SURF.get_surfaceSplitCurves(str_meshShape,count = self.numBridgeSplit + 2,
                                                     mode='u')
                
                tag = 'lwrJoin'
                l_keys_crv = []
                for i,crv in enumerate(l_crvs):
                    _l_split =  CURVES.getUSplitList(crv,d_lipDat['lwr']['count'],rebuild=1)
                    
                    
                    #Pop start and end as we'll use the upr handles
                    if self.noseSetup:
                        _l_split.pop(0)
                        _l_split.pop(-1)
                        
                        
                    #Now to split the positional data by left right
                    _mid = MATH.get_midIndex(len(_l_split))
                    
                    if b_even:
                        _l_right = _l_split[:_mid]
                        _l_left = _l_split[_mid:]
                        
                    else:
                        _midV = _l_split[_mid]
                        _l_right = _l_split[:_mid]
                        _l_left = _l_split[_mid+1:]
                        
                        
                        _keyCenter = "{0}_{1}_center".format(tag,i)
                        d_use = copy.copy(d_handleBase)
                        d_use['color'] = d_color['center']
                        d_use['pos'] = _midV
                        d_defPos[_keyCenter] = _midV
                        
                        d_creation[_keyCenter] = d_use
                        l_order.append(_keyCenter)
                        
                    _l_left.reverse()#reverse dat for mirror indexing
                        
                    #Now we need to split out our handle create dat
                    l_handlesLeft = []
                    l_handlesRight = []
                    
                    for ii,p in enumerate(_l_right):
                        _key_l = "{0}_{1}_{2}_left".format(tag,i,ii)
                        _key_r = "{0}_{1}_{2}_right".format(tag,i,ii)
                        
                        d_pairs[_key_l] = _key_r
                        
                        l_order.extend([_key_l,_key_r])
                        
                        #Right...
                        d_use = copy.copy(d_handleBase)
                        d_use['color'] = d_color['right']
                        d_use['pos'] = p
                        d_creation[_key_r] = d_use
                        l_handlesRight.append(_key_r)
                        d_defPos[_key_r] = p
                        
                        #Left...
                        d_use = copy.copy(d_handleBase)
                        d_use['color'] = d_color['left']
                        d_use['pos'] = _l_left[ii]
                        d_creation[_key_l] = d_use
                        d_defPos[_key_l] = _l_left[ii]
                        
                        l_handlesLeft.append(_key_l)
                        
                        #LOC.create(position=_l_left[ii],name=_key_l)
                        #LOC.create(position=p,name=_key_r)
                        
                    
                    #Then curve create dat...
                    _keys = copy.copy(l_handlesRight)
                    if _keyCenter:
                        _keys.append(_keyCenter)
                    l_handlesLeft.reverse()
                    _keys.extend(l_handlesLeft)
                    
                    
                    if self.noseSetup:
                        _keys.insert(0,d_bridgeDat['upr']['right']['handles'][i][-1])
                        _keys.append(d_bridgeDat['upr']['left']['handles'][i][-1])
                        
                    
                    k_crv = "{0}_{1}".format(tag,i)
                    l_keys_crv.append(k_crv)
                    d_curveCreation[k_crv] = {'keys':_keys,
                                              'rebuild':1}                
                
                
                
                
                
                mc.delete(l_crvs + _res_tmp + [crv_start,crv_end])
                #l_keys_crv.insert(0,md_loftCreation['lwrLip']['keys'][0])
                l_keys_crv.insert(0,'lipToChinStart')
                
                l_keys_crv.append('lipToChinEnd')
                md_loftCreation['lipToChin'] =  {'keys':l_keys_crv,
                                                 'rebuild':{'spansU':30,'spansV':5,'degreeU':3},
                                                 'uDriver':'{0}.numLoftBridge_v'.format(_short),
                                                 'vDriver':'{0}.numLoftBridge_u'.format(_short),
                                                 'kws':{'noRebuild':True}}                
                
            else:
                log.debug(cgmGEN.logString_sub(_str_func,'simple lwr bridge'))

                
                md_loftCreation['lipToChin'] =  {'keys':[md_loftCreation['lwrLip']['keys'][0],
                                                         'lipToChinEnd'],
                                                 'rebuild':{'spansU':30,'spansV':5,'degreeU':3},
                                                 'uDriver':'{0}.numLoftJaw_u'.format(_short),
                                                 'vDriver':'{0}.numLoftJaw_v'.format(_short),
                                                 'kws':{'noRebuild':True}}


     
        #return
    # ==========================================================================================
    # Final bits
    # ==========================================================================================
    #Hiding unused define handles
    l_dTagsUsed = []
    for k,dat in list(d_curveCreation.items()):
        for t in dat['keys']:
            if t not in l_dTagsUsed:
                l_dTagsUsed.append(t)
    
    #l_dTagsUsed.sort()
    #pprint.pprint(l_dTagsUsed)        
    for tag,d in list(d_creation.items()):
        d_creation[tag]['jointScale'] = True
        
    md_res = self.UTILS.create_defineHandles(self, l_order, d_creation, _size / 10,
                                             mFormNull, forceSize=1)
    ml_subHandles.extend(md_res['ml_handles'])
    md_handles.update(md_res['md_handles'])

        
    md_res = self.UTILS.create_defineCurve(self, d_curveCreation, md_handles,
                                           mNoTransformNull,
                                           crvType='formCrv')
    md_resCurves = md_res['md_curves']
    
    for k,d in list(md_loftCreation.items()):
        ml_curves = [md_resCurves.get(k2) for k2 in d['keys']]
        
        ml_curves = [mCurve for mCurve in ml_curves if mCurve]
        for mObj in ml_curves:
            #mObj.template =1
            mObj.v = 0
            
        if len(ml_curves) < 2:
            log.warning("Not enough curves in set: {} | {}".format(k,ml_curves))
            continue
        
        """
            self.UTILS.create_simpleFormLoftMesh(self,
                                                 [mObj.mNode for mObj in ml_curves],
                                                 mFormNull,
                                                 polyType = 'faceLoft',
                                                 d_rebuild = d.get('rebuild',{}),
                                                 baseName = k,
                                                 transparent = False,
                                                 vDriver = "{0}.numLidSplit_v".format(_short),
                                                 uDriver = "{0}.numLidSplit_u".format(_short),
                                                 **d.get('kws',{}))"""
            
            
        mSurf = self.UTILS.create_simpleFormLoftMesh(self,
                                                     [mObj.mNode for mObj in ml_curves],
                                                     mFormNull,
                                                     polyType = 'faceNurbsLoft',
                                                     d_rebuild = d.get('rebuild',{}),
                                                     transparent = False,
                                                     baseName = k,
                                                     vDriver = d.get('vDriver'),#'"{0}.numLidSplit_v".format(_short),
                                                     uDriver = d.get('uDriver'),#"{0}.numLidSplit_u".format(_short),
                                                     **d.get('kws',{}))
        
        if 'attach' in k:
            mSurf.template = 1
    
    
    
    
    #Mirror indexing -------------------------------------
    log.debug("|{0}| >> Mirror Indexing...".format(_str_func)+'-'*40) 
    
    idx_ctr = 0
    idx_side = 0
    d = {}
            
    for tag,mHandle in list(md_handles.items()):
        """
        if cgmGEN.__mayaVersion__ >= 2018:
            mController = mHandle.controller_get()
            mController.visibilityMode = 2"""
            
        if mHandle in ml_defineHandles:
            continue
        
        mHandle._verifyMirrorable()
        _center = True
        for p1,p2 in list(d_pairs.items()):
            if p1 == tag or p2 == tag:
                _center = False
                break
        if _center:
            log.debug("|{0}| >>  Center: {1}".format(_str_func,tag))    
            mHandle.mirrorSide = 0
            mHandle.mirrorIndex = idx_ctr
            idx_ctr +=1
        mHandle.mirrorAxis = "translateX,rotateY,rotateZ"
        
        mHandle.doConnectIn('v', "{0}.visFormHandles".format(_short))
        mHandle.setAttrFlags('v')
        
    l_dTagsUsed.extend(['cornerFrontLeft','cornerFrontRight'])
    for mHandle in ml_defineHandles:
        if mHandle.handleTag not in l_dTagsUsed:
            mHandle.v=False
        else:
            mHandle.v=True
            
    #Self mirror wiring -------------------------------------------------------
    for k,m in list(d_pairs.items()):
        log.debug("{0} -|- {1}".format(k,m))
        try:
            md_handles[k].mirrorSide = 1
            md_handles[m].mirrorSide = 2
            md_handles[k].mirrorIndex = idx_side
            md_handles[m].mirrorIndex = idx_side
            md_handles[k].doStore('mirrorHandle',md_handles[m])
            md_handles[m].doStore('mirrorHandle',md_handles[k])
            idx_side +=1        
        except Exception as err:
            log.error('Mirror error: {0}'.format(err))
    
    self.atUtils('controller_wireHandles',ml_subHandles,'form')
    self.msgList_connect('formHandles',ml_subHandles)#Connect
    self.msgList_connect('formCurves',md_res['ml_curves'])#Connect        
    return



#=============================================================================================================
#>> Prerig
#=============================================================================================================
def prerigDelete(self):
    self.noTransFormNull.v=True
    self.formNull.template=False
    
    for mObj in self.msgList_get('defineSubHandles') + self.msgList_get('formHandles'):
        mLabel = mObj.getMessageAsMeta('jointLabel')
        if mLabel:
            mLabel.v=1
    
def create_handle(self,tag,pos,mJointTrack=None,
                  trackAttr=None,visualConnection=True,
                  nameEnd = 'BrowHandle'):
    mHandle = cgmMeta.validateObjArg( CURVES.create_fromName('circle', size = _size_sub), 
                                      'cgmObject',setClass=1)
    mHandle.doSnapTo(self)

    mHandle.p_position = pos

    mHandle.p_parent = mStateNull
    mHandle.doStore('cgmName',tag)
    mHandle.doStore('cgmType','formHandle')
    mHandle.doName()

    mHandleFactory.color(mHandle.mNode,controlType='sub')

    self.connectChildNode(mHandle.mNode,'{0}nameEnd'.format(tag),'block')

    return mHandle

    #joinHandle ------------------------------------------------
    mJointHandle = cgmMeta.validateObjArg( CURVES.create_fromName('jack',
                                                                  size = _size_sub*.75),
                                           'cgmObject',
                                           setClass=1)

    mJointHandle.doStore('cgmName',tag)    
    mJointHandle.doStore('cgmType','jointHelper')
    mJointHandle.doName()                

    mJointHandle.p_position = pos
    mJointHandle.p_parent = mStateNull


    mHandleFactory.color(mJointHandle.mNode,controlType='sub')
    mHandleFactory.addJointLabel(mJointHandle,tag)
    mHandle.connectChildNode(mJointHandle.mNode,'jointHelper','handle')

    mTrackGroup = mJointHandle.doGroup(True,True,
                                       asMeta=True,
                                       typeModifier = 'track',
                                       setClass='cgmObject')

    if trackAttr and mJointTrack:
        mPointOnCurve = cgmMeta.asMeta(CURVES.create_pointOnInfoNode(mJointTrack.mNode,turnOnPercentage=True))

        mPointOnCurve.doConnectIn('parameter',"{0}.{1}".format(self.mNode,trackAttr))

        mTrackLoc = mJointHandle.doLoc()

        mPointOnCurve.doConnectOut('position',"{0}.translate".format(mTrackLoc.mNode))

        mTrackLoc.p_parent = mNoTransformNull
        mTrackLoc.v=False
        mc.pointConstraint(mTrackLoc.mNode,mTrackGroup.mNode)                    


    elif mJointTrack:
        mLoc = mHandle.doLoc()
        mLoc.v=False
        mLoc.p_parent = mNoTransformNull
        mc.pointConstraint(mHandle.mNode,mLoc.mNode)

        res = DIST.create_closest_point_node(mLoc.mNode,mJointTrack.mNode,True)
        #mLoc = cgmMeta.asMeta(res[0])
        mTrackLoc = cgmMeta.asMeta(res[0])
        mTrackLoc.p_parent = mNoTransformNull
        mTrackLoc.v=False
        mc.pointConstraint(mTrackLoc.mNode,mTrackGroup.mNode)


    mAimGroup = mJointHandle.doGroup(True,True,
                                     asMeta=True,
                                     typeModifier = 'aim',
                                     setClass='cgmObject')
    mc.aimConstraint(mLidRoot.mNode,
                     mAimGroup.mNode,
                     maintainOffset = False, weight = 1,
                     aimVector = [0,0,-1],
                     upVector = [0,1,0],
                     worldUpVector = [0,1,0],
                     worldUpObject = self.mNode,
                     worldUpType = 'objectRotation' )                          


    if visualConnection:
        log.debug("|{0}| >> visualConnection ".format(_str_func, tag))
        trackcrv,clusters = CORERIG.create_at([mLidRoot.mNode,
                                               mJointHandle.mNode],#ml_handleJoints[1]],
                                              'linearTrack',
                                              baseName = '{0}_midTrack'.format(tag))

        mTrackCrv = cgmMeta.asMeta(trackcrv)
        mTrackCrv.p_parent = mNoTransformNull
        mHandleFactory.color(mTrackCrv.mNode, controlType = 'sub')

        for s in mTrackCrv.getShapes(asMeta=True):
            s.overrideEnabled = 1
            s.overrideDisplayType = 2

    return mHandle

def prerig(self):
    #try:
    _str_func = 'prerig'
    log.debug("|{0}| >>  {1}".format(_str_func,self)+ '-'*80)
    self.blockState = 'prerig'
    _side = self.UTILS.get_side(self)
    
    if MATH.is_even(self.numConLips):
        raise ValueError("numConLips must be odd.")
    
    self.atUtils('module_verify')
    mStateNull = self.UTILS.stateNull_verify(self,'prerig')
    mNoTransformNull = self.atUtils('noTransformNull_verify','prerig')
    #self.noTransFormNull.v=False
    #self.formNull.template=True
    
    _size = self.jointRadius  #MATH.average(self.baseSize[1:])
    _size_base = self.jointRadius 
    _offset = _size_base * 2.0#self.atUtils('get_shapeOffset')/4.0
    
    _size_sub = _size_base * .5
    _size_anchor = _size * 1.5
    _size_anchorLips = _size *1.1
    _size_direct = _size
    _muzzleSize = _size * 3.0
    
    #mRoot = self.getMessageAsMeta('rootHelper')
    mHandleFactory = self.asHandleFactory()
    vec_self = self.getAxisVector('z+')
    vec_selfUp = self.getAxisVector('y+')
    vec_selfBack = self.getAxisVector('z-')
    
    #---------------------------------------------------------------
    log.debug("|{0}| >> Gather define/form handles/curves in a useful format...".format(_str_func))
    _l_clean = []
    d_pairs = {}
    ml_handles = []
    md_handles = {}
    md_dHandles = {}
    md_dCurves = {}
    md_jointHandles = {}
    ml_jointHandles = []
    ml_defineHandles = []
    d_basePosDat = {}
    md_mirrorDat = {'center':[],
                    'left':[],
                    'right':[]}
    
    for mObj in self.msgList_get('defineSubHandles') + self.msgList_get('formHandles'):
        _handleTag = mObj.handleTag
        md_dHandles[_handleTag] = mObj

        ml_defineHandles.append(mObj)
        d_basePosDat[_handleTag] = mObj.p_position

    for mObj in self.msgList_get('defineCurves') + self.msgList_get('formCurves') :
        md_dCurves[mObj.handleTag] = mObj
        mObj.template=1        
    
    d_baseHandeKWS = {'mStateNull' : mStateNull,
                      'mNoTransformNull' : mNoTransformNull,
                      'jointSize': self.jointRadius}
    
    #==================================================================================================
    # Processing 
    #==================================================================================================
    mCrv_lwrBack = self.getMessageAsMeta('lwr_LipBackFormCrv')
    p_lwrLipBack = CRVPCT(mCrv_lwrBack.mNode, .5)
    
    mCrv_lwrGum = self.getMessageAsMeta('lwr_GumFormCrv')
    p_gumLwr = CRVPCT(mCrv_lwrGum.mNode, .5)
    
    mCrv_uprGum = self.getMessageAsMeta('upr_GumFormCrv')
    p_gumUpr = CRVPCT(mCrv_uprGum.mNode, .5)
            
    #p_teethBase = DIST.get_pos_by_vec_dist(p_lwrLipBack,vec_selfBack,_offset)
    
    
    dist_mouthWidth = DIST.get_distance_between_points(md_dHandles['cornerFrontLeft'].p_position,
                                                       md_dHandles['cornerFrontRight'].p_position)        
    
    
    if self.jawUprSetup:#   Jaw setup ============================================================
        log.debug(cgmGEN.logString_sub(_str_func,'jaw upr'))
        
        #Shape...
        
        if self.noseSetup:
            l_jaw = ['cheek_1_4_right',
                     'jawTopRight',
                     'orbFrontRight',
                     'nostrilTopRight',
                     #'overJoin_0_2_right',
                     'bridgeRight',
                     'bridge',
                     'bridgeLeft',
                     'nostrilTopLeft',                                          
                     #'overJoin_0_2_left',
                     'orbFrontLeft',
                     'jawTopLeft',
                     'cheek_1_4_left',
                     ]
        else:
            l_jaw = ['jawTopRight',
                     'orbFrontRight',
                     'upr_Peak_3_right',
                     'upr_Peak_center',
                     'upr_Peak_3_left',
                     'orbFrontLeft',
                     'jawTopLeft']            
 
            
        l_tmp = []
        for k in l_jaw:
            if md_dHandles.get(k):
                l_tmp.append(md_dHandles.get(k).p_position)
                
        _crv = CORERIG.create_at(create='curve',l_pos=l_tmp)
        #md_dCurves['jawLine'].mNode
        
        DIST.offsetShape_byVector(_crv, distance = _offset)
        """
        _shape = mc.offsetCurve(_crv,rn=0,cb=1,st=1,cl=1,cr=0,ch=0,
                                d=1,tol=.0001,sd=1,ugn=0,
                                distance =-_offset*4)
        mc.delete(_crv)
    
        mShape = cgmMeta.validateObjArg(_shape[0],'cgmControl',setClass=1)  """
        mShape = cgmMeta.validateObjArg(_crv,'cgmControl',setClass=1)
        mHandleFactory.color(mShape.mNode,side = 'center', controlType='main')
    
        _d_name = {'cgmName':'jawUpr',
                   'cgmType':'jointHelper'}
        
        _d_kws = copy.copy(d_baseHandeKWS)
        _d_kws['jointSize'] *= 2 
        mShape,mDag = BLOCKSHAPES.create_face_handle(self, None,'jawUpr',None,'center',
                                                     mHandleShape=mShape,
                                                     size = _offset,
                                                     nameDict=_d_name,
                                                     aimGroup=0,
                                                     **_d_kws)            
        
        
        md_jointHandles['jawUpr'] = mDag
        mDag.p_position = DGETAVG([md_dHandles['jawRight'].p_position,
                                                          md_dHandles['jawLeft'].p_position])

        ml_jointHandles.append(mDag)            
        ml_handles.append(mShape)
    
        md_handles['jawUpr'] = mShape
        md_handles['jawUprJoint'] = mDag
        md_mirrorDat['center'].extend([mShape,mDag])
        
        mDag.p_parent = mStateNull        
    

    if self.jawLwrSetup:#   Jaw setup ============================================================
        log.debug(cgmGEN.logString_sub(_str_func,'jaw'))
        
        #Shape...
        l_jaw = [#'jawTopRight',
                 'jawRight',
                 'jawNeckRight',
                 'jawFrontRight',
                 'jawFrontLeft',
                 'jawNeckLeft',
                 'jawLeft',
                 #'jawTopLeft'
                 ]
                            
        _crv = CORERIG.create_at(create='curve',l_pos=[md_dHandles[k].p_position for k in l_jaw])
        #md_dCurves['jawLine'].mNode
        
        DIST.offsetShape_byVector(_crv, distance = _offset)
        """
        _shape = mc.offsetCurve(_crv,rn=0,cb=1,st=1,cl=1,cr=0,ch=0,
                                d=1,tol=.0001,sd=1,ugn=0,
                                distance =-_offset*4)
        mc.delete(_crv)
    
        mShape = cgmMeta.validateObjArg(_shape[0],'cgmControl',setClass=1)  """
        mShape = cgmMeta.validateObjArg(_crv,'cgmControl',setClass=1)
        mHandleFactory.color(mShape.mNode,side = 'center', controlType='main')
    
        _d_name = {'cgmName':'jaw',
                   'cgmType':'jointHelper'}
        
        _d_kws = copy.copy(d_baseHandeKWS)
        _d_kws['jointSize'] *= 2 
        mShape,mDag = BLOCKSHAPES.create_face_handle(self, None,'jaw',None,'center',
                                                     mHandleShape=mShape,
                                                     size = _offset,
                                                     nameDict=_d_name,
                                                     aimGroup=0,
                                                     **_d_kws)            
        
        
        md_jointHandles['jawLwr'] = mDag
        mDag.p_position = DGETAVG([md_dHandles['jawRight'].p_position,
                                                          md_dHandles['jawLeft'].p_position])

        ml_jointHandles.append(mDag)            
        ml_handles.append(mShape)
    
        md_handles['jaw'] = mShape
        md_handles['jawJoint'] = mDag
        md_mirrorDat['center'].extend([mShape,mDag])
        
        mDag.p_parent = mStateNull        
    
     
    
    #Tongue =========================================================================================
    _tongueSetup = self.tongueSetup
    if _tongueSetup:#============================================================
        log.debug(cgmGEN.logString_sub(_str_func,'tongue'))
        
        if _tongueSetup == 1:
            p_base = DGETAVG([p_lwrLipBack,p_gumLwr])
            f_distLipLwr = DIST.get_distance_between_points(p_gumLwr, p_lwrLipBack)
            p_tongue = DIST.get_pos_by_vec_dist(p_base,vec_selfBack,f_distLipLwr)
            
            
            #------------------------------------------------------------

            _d_name = {'cgmName':'tongue',
                       'cgmType':'jointHelper'}
            
            _d_kws = copy.copy(d_baseHandeKWS)
            _d_kws['jointSize'] *= 2 
            
            mShape,mDag = BLOCKSHAPES.create_face_handle(self, p_tongue,'tongue',None,'center',
                                                         mainShape = 'semiSphere',
                                                         size = 1.0,
                                                         nameDict=_d_name,
                                                         aimGroup=0,
                                                         **_d_kws)
            
            TRANS.scale_to_boundingBox(mShape.mNode,
                                       [dist_mouthWidth,f_distLipLwr,f_distLipLwr])

            mShape.p_parent = mStateNull
            mShape.p_position = p_tongue                

            md_handles['tongue'] = mDag
            md_handles['tongue'] = mDag            

            BLOCKSHAPES.create_visualTrack(self, mDag, md_handles['jawJoint'],
                                           'tongue',mNoTransformNull)
            
    
    #Teeth =========================================================================================
    _teethUprSetup = self.teethUprSetup
    _teethLwrSetup = self.teethLwrSetup
    if _teethUprSetup:
        log.debug(cgmGEN.logString_sub(_str_func,'teeth upr: {0}'.format(_teethUprSetup)))
        if _teethUprSetup == 1:
            f_distLip = DIST.get_distance_between_points(p_gumUpr, p_lwrLipBack)
            p_shape = DIST.get_pos_by_vec_dist(DGETAVG([p_lwrLipBack,p_gumUpr]),
                                              vec_self,
                                              0)
            _tag = 'teeth'+'Upr'
            #------------------------------------------------------------
        
            _d_name = {'cgmName':_tag,
                       'cgmType':'jointHelper'}
        
            _d_kws = copy.copy(d_baseHandeKWS)
        
            mShape,mDag = BLOCKSHAPES.create_face_handle(self, p_lwrLipBack,_tag,
                                                         None,'center',
                                                         mainShape = 'loftTriUp',
                                                         size = f_distLip * .75,
                                                         nameDict=_d_name,
                                                         aimGroup=0,
                                                         **_d_kws)            
        
            mShape.p_parent = mStateNull
            mShape.p_position = p_shape                
        
            md_handles[_tag] = mDag
            md_handles[_tag] = mDag
            
    if _teethLwrSetup:
        log.debug(cgmGEN.logString_sub(_str_func,'teeth lwr: {0}'.format(_teethUprSetup)))
        if _teethLwrSetup == 1:
            f_distLip = DIST.get_distance_between_points(p_gumLwr, p_lwrLipBack)
            p_shape = DIST.get_pos_by_vec_dist(DGETAVG([p_lwrLipBack,p_gumLwr]),
                                              vec_self,
                                              0)
            _tag = 'teeth'+'Lwr'
            #------------------------------------------------------------
        
            _d_name = {'cgmName':_tag,
                       'cgmType':'jointHelper'}
        
            _d_kws = copy.copy(d_baseHandeKWS)
        
            mShape,mDag = BLOCKSHAPES.create_face_handle(self, p_lwrLipBack,_tag,
                                                         None,'center',
                                                         mainShape = 'loftTriDown',
                                                         size = f_distLip * .75,
                                                         nameDict=_d_name,
                                                         aimGroup=0,
                                                         **_d_kws)            
        
            mShape.p_parent = mStateNull
            mShape.p_position = p_shape                
        
            md_handles[_tag] = mDag
            md_handles[_tag] = mDag
    
    if self.chinSetup:# chin setup ============================================================
        log.debug(cgmGEN.logString_sub(_str_func,'chin setup'))
        str_chinSetup = self.getEnumValueString('chinSetup')
        
        if str_chinSetup == 'single':
            log.debug(cgmGEN.logString_msg(_str_func, str_chinSetup))
            mSurf =  self.jawFormLoft
            
            _tag = 'chin'                
            _dTmp = {'cgmName':_tag}
            #_dTmp = copy.copy(_d_name)
            #_dTmp['cgmName'] = _tag
            
            p_chinBase = DGETAVG([d_basePosDat['chinLeft'],
                                  d_basePosDat['chinRight']])
            
            d_handleKWS = {
                'mode' : 'handle',
                'mSurface':mSurf,
                'handleShape' :'semiSphere',
                'handleSize' : _size_sub,
                'anchorSize' : _size_anchor,
                'orientToDriver':True,
                'attachToSurf':True,
                'nameDict':_dTmp,
                'md_mirrorDat':md_mirrorDat,
                'ml_handles':ml_handles,
                'md_handles':md_handles,
                'ml_jointHandles':ml_jointHandles,
            }
            d_handleKWS.update(d_baseHandeKWS)
            cgmGEN._reloadMod(BLOCKSHAPES)
            mAnchor,mShape,mDag = BLOCKSHAPES.create_face_anchorHandleCombo(self,
                                                                            p_chinBase,
                                                                            _tag,
                                                                            None,
                                                                            'center',
                                                                            size= _size_anchor,
                                                                            offsetAttr = 'conDirectOffset',
                                                                            **d_handleKWS)
            #ml_handles.extend([mAnchor,mShape,mDag])                
            #md_handles[_tag] = mShape
            #md_handles[_tag+'Joint'] = mDag
            #ml_jointHandles.append(mDag)
            #md_mirrorDat['center'].extend([mAnchor,mShape,mDag])
            BLOCKSHAPES.create_visualTrack(self, mDag, md_handles['jawJoint'],
                                           _tag,mNoTransformNull)
            """
            mShape,mDag = BLOCKSHAPES.create_face_handle(self,
                                                         p_chinBase,
                                                         _tag,
                                                         None,
                                                         'center',
                                                         mSurface=mSurf,
                                                         mainShape='semiSphere',
                                                         size = _size_sub,
                                                         nameDict=_dTmp,
                                                         **d_baseHandeKWS)            
                                                         """
        else:
            raise ValueError("Invalid chinSetup: {0}".format(str_chinSetup))
    
    if self.muzzleSetup:#Muzzle ============================================================
        log.debug(cgmGEN.logString_sub(_str_func,'muzzle'))
        
        _d_name = {'cgmName':'muzzle',
                   'cgmType':'jointHelper'}
        
        
        try:
            pMuzzleBase = md_dHandles['bridge'].p_position
            pMuzzleBase = DIST.get_pos_by_vec_dist(pMuzzleBase, 
                                        vec_selfUp,
                                        _offset*2)
        except:
            # Fallback position if bridge handle not found
            pMuzzleBase = DIST.get_pos_by_vec_dist(self.p_position,
                                                  vec_selfUp,
                                                  _offset*3)
            

        
        p = DIST.get_pos_by_vec_dist(pMuzzleBase, 
                                    vec_self,
                                    -_offset*4)
        
        mShape = cgmMeta.asMeta(CURVES.create_fromName('pyramid',size = _muzzleSize, direction = 'z+'))
        mShape,mDag = BLOCKSHAPES.create_face_handle(self, p,'muzzle',None,'center',
                                                     mHandleShape=mShape,
                                                     size = _muzzleSize,
                                                     nameDict=_d_name,
                                                     aimGroup=0,
                                                     **d_baseHandeKWS)
        BLOCKSHAPES.color(self,mShape)
        
        
        TRANS.scale_to_boundingBox(mShape.mNode, [_muzzleSize,_muzzleSize,_muzzleSize/1.5])
        mShape.p_position = DIST.get_pos_by_vec_dist(pMuzzleBase, 
                                                     vec_self,
                                                     _offset*2)
        
        mShape.p_parent = mStateNull
        mDag.p_parent = mStateNull
        
        ml_handles.append(mShape)
        md_handles['muzzle'] = mShape
        md_handles['muzzleJoint'] = mDag
        ml_jointHandles.append(mDag)
        md_jointHandles['muzzle'] = mDag
        
        md_mirrorDat['center'].extend([mShape,mDag])
        
        

    if self.sneerSetup:# Nose setup ============================================================
        log.debug(cgmGEN.logString_sub(_str_func,'sneer setup'))
        str_sneerSetup = self.getEnumValueString('sneerSetup')
        
        _d_name = {'cgmName':'sneer',
                   'cgmType':'handleHelper'}            
    
        if str_sneerSetup == 'single':
            mSurf =  self.noseFormLoft

            #d_pairs['nostrilLeft'] = 'nostrilRight'
            #d_pairs['nostrilLeftJoint'] = 'nostrilRightJoint'
            
            for side in ['left','right']:
                #Get our position
                _cap = side.capitalize()
                _tag = 'sneer'+_cap
                log.debug(cgmGEN.logString_msg(_str_func, 'sneer | {0}'.format(_tag)))
                mSurf = self.getMessageAsMeta('uprJoin{0}FormLoft'.format(_cap))
                _dTmp = {'cgmName':'sneer',
                         'cgmDirection':side}
                
                d_handleKWS = {
                    'mode' : 'handle',
                    'mSurface':mSurf,
                    'handleShape' :'semiSphere',
                    'handleSize' : _size_sub,
                    'anchorSize' : _size_anchor,
                    'orientToDriver':True,
                    'orientToSurf':False,
                    
                    'attachToSurf':True,
                    'nameDict':_dTmp,
                    'md_mirrorDat':md_mirrorDat,
                    'ml_handles':ml_handles,
                    'md_handles':md_handles,
                    'ml_jointHandles':ml_jointHandles,
                }
                d_handleKWS.update(d_baseHandeKWS)

                mAnchor,mShape,mDag = BLOCKSHAPES.create_face_anchorHandleCombo(self,
                                                                                d_basePosDat['sneer'+_cap],
                                                                                _tag,
                                                                                None,
                                                                                side,
                                                                                size= _size_anchor,
                                                                                offsetAttr = 'conDirectOffset',
                                                                                **d_handleKWS)                        

    if self.noseSetup:# Nose setup ============================================================
        log.debug(cgmGEN.logString_sub(_str_func,'nose setup'))
        str_noseSetup = self.getEnumValueString('noseSetup')
        
        _d_name = {'cgmName':'nose',
                   'cgmType':'handleHelper'}            
    
        if str_noseSetup == 'simple':
            log.debug(cgmGEN.logString_msg(_str_func, str_noseSetup))
            mSurf =  self.noseFormLoft
            
            #NoseBase -------------------------------------------------------------------
            _tag = 'noseBase'                
            _dTmp = copy.copy(_d_name)
            _dTmp['cgmName'] = _tag
            
            p_noseBase = DGETAVG([d_basePosDat['nostrilLeft'],
                                  d_basePosDat['nostrilRight']])
            
            mShape,mDag = BLOCKSHAPES.create_face_handle(self,
                                                         p_noseBase,
                                                         'noseBase',
                                                         None,
                                                         'center',
                                                         mainShape='loftWideDown',
                                                         size = _size * 2.5,
                                                         nameDict=_dTmp,
                                                         **d_baseHandeKWS)
                
            mShape.p_position = DGETAVG([d_basePosDat['noseTipLeft'],
                                         d_basePosDat['noseTipRight']])
            
            ml_handles.append(mShape)                
            md_handles[_tag] = mShape
            md_handles[_tag+'Joint'] = mDag
            ml_jointHandles.append(mDag)
            md_mirrorDat['center'].extend([mShape,mDag])
            
            vec_nose = MATH.get_vector_of_two_points(p_noseBase, d_basePosDat['noseTip'])
            
            if self.numJointsNoseTip:#NoseTip ----------------------------------------------------
                log.debug(cgmGEN.logString_msg(_str_func, 'nosetip...'))
                _tag = 'noseTip'
                _dTmp = copy.copy(_d_name)
                _dTmp['cgmName'] = 'noseTip'

                d_handleKWS = {
                    'mode' : 'handle',
                    'mSurface':mSurf,
                    'handleShape' :'semiSphere',
                    'handleSize' : _size_sub,
                    'anchorSize' : _size_anchor,
                    'orientToDriver':True,
                    'attachToSurf':True,
                    'nameDict':_dTmp,
                    'md_mirrorDat':md_mirrorDat,
                    'ml_handles':ml_handles,
                    'md_handles':md_handles,
                    'ml_jointHandles':ml_jointHandles,
                }
                d_handleKWS.update(d_baseHandeKWS)

                mAnchor,mShape,mDag = BLOCKSHAPES.create_face_anchorHandleCombo(self,
                                                                                d_basePosDat['noseTip'],
                                                                                'noseTip',
                                                                                None,
                                                                                'center',
                                                                                size= _size_direct,
                                                                                **d_handleKWS)

                BLOCKSHAPES.create_visualTrack(self, mDag, md_handles['noseBaseJoint'],_tag,mNoTransformNull)
                
            if self.numJointsNostril:#Nostrils --------------------------------------
                #d_pairs['nostrilLeft'] = 'nostrilRight'
                #d_pairs['nostrilLeftJoint'] = 'nostrilRightJoint'
                
                for side in ['left','right']:
                    #Get our position
                    _tag = 'nostril'+side.capitalize()
                    log.debug(cgmGEN.logString_msg(_str_func, 'nosetip | {0}'.format(_tag)))
                    _dTmp = {'cgmName':'nostril',
                             'cgmDirection':side}
                        
                    d_handleKWS = {
                        'mode' : 'handle',
                        'mSurface':mSurf,
                        'handleShape' :'semiSphere',
                        'handleSize' : _size_sub,
                        'anchorSize' : _size_anchor,
                        'orientToDriver':True,
                        'orientToSurf':True,
                        
                        'attachToSurf':True,
                        'nameDict':_dTmp,
                        'md_mirrorDat':md_mirrorDat,
                        'ml_handles':ml_handles,
                        'md_handles':md_handles,
                        'ml_jointHandles':ml_jointHandles,
                    }
                    d_handleKWS.update(d_baseHandeKWS)
    
                    mAnchor,mShape,mDag = BLOCKSHAPES.create_face_anchorHandleCombo(self,
                                                                                    d_basePosDat['nostril'+side.capitalize()],
                                                                                    _tag,
                                                                                    None,
                                                                                    side,
                                                                                    size= _size_direct,
                                                                                    offsetAttr = 'conDirectOffset',
                                                                                    
                                                                                    **d_handleKWS)
                    
                    BLOCKSHAPES.create_visualTrack(self, mDag, md_handles['noseBaseJoint'],
                                                   _tag,mNoTransformNull)


    
    if self.cheekSetup:# cheek setup ============================================================
        log.debug(cgmGEN.logString_sub(_str_func,'Cheek setup'))
        str_cheekSetup = self.getEnumValueString('cheekSetup')
        
        if str_cheekSetup == 'single':
            log.debug(cgmGEN.logString_msg(_str_func, 'single'))
            
            mSurf =  self.jawFormLoft
            
            _d_name = {'cgmName':'cheek',
                       'cgmType':'handleHelper'}
            
            d_pairs['cheekLeft'] = 'cheekRight'
            d_pairs['cheekLeftJoint'] = 'cheekRightJoint'                
            
            for side in ['left','right']:
                #Get our position
                _tag = 'cheek'+side.capitalize()
                log.debug(cgmGEN.logString_msg(_str_func, 'cheek | {0}'.format(_tag)))
                _dTmp = copy.copy(_d_name)
                _dTmp['cgmDirection'] = side
                
                
                d_handleKWS = {
                    'mode' : 'handle',
                    'mSurface':mSurf,
                    'handleShape' :'semiSphere',
                    'handleSize' : _size_sub,
                    'anchorSize' : _size_anchor,
                    'orientToSurf':True,
                    'orientToDriver':True,
                    'attachToSurf':True,
                    'nameDict':_dTmp,
                    'md_mirrorDat':md_mirrorDat,
                    'ml_handles':ml_handles,
                    'md_handles':md_handles,
                    'ml_jointHandles':ml_jointHandles,
                }
                d_handleKWS.update(d_baseHandeKWS)

                mAnchor,mShape,mDag = BLOCKSHAPES.create_face_anchorHandleCombo(self,
                                                                                d_basePosDat[_tag],
                                                                                _tag,
                                                                                None,
                                                                                side,
                                                                                size= _size_anchor,
                                                                                offsetAttr = 'conDirectOffset',
                                                                                
                                                                                **d_handleKWS)                    

                BLOCKSHAPES.create_visualTrack(self, mDag, md_handles['jawJoint'],
                                               _tag,mNoTransformNull)

        else:
            raise ValueError("Invalid cheekSetup: {0}".format(str_cheekSetup))
        
    if self.cheekUprSetup:# cheek setup ============================================================
        log.debug(cgmGEN.logString_sub(_str_func,'Cheek Upr  setup'))
        str_cheekUprSetup = self.getEnumValueString('cheekUprSetup')
        
        mSurf =  self.jawFormLoft
        _d_name = {'cgmName':'cheekUpr',
                   'cgmType':'handleHelper'}
                    
        
        if str_cheekUprSetup == 'single':
            log.debug(cgmGEN.logString_msg(_str_func, 'single'))
            
            
            d_pairs['cheekUprLeft'] = 'cheekUprRight'
            d_pairs['cheekUprLeftJoint'] = 'cheekUprRightJoint'                
            
            for side in ['left','right']:
                #Get our position
                _tag = 'cheekUpr'+side.capitalize()
                _handleKey = 'cheek_0_1_'+side
                log.debug(cgmGEN.logString_msg(_str_func, 'cheek | {0}'.format(_tag)))
                _dTmp = copy.copy(_d_name)
                _dTmp['cgmDirection'] = side
                
                
                d_handleKWS = {
                    'mode' : 'handle',
                    'mSurface':mSurf,
                    'handleShape' :'semiSphere',
                    'handleSize' : _size_sub,
                    'anchorSize' : _size_anchor,
                    'orientToSurf':True,
                    'orientToDriver':True,
                    'attachToSurf':True,
                    'nameDict':_dTmp,
                    'md_mirrorDat':md_mirrorDat,
                    'ml_handles':ml_handles,
                    'md_handles':md_handles,
                    'ml_jointHandles':ml_jointHandles,
                }
                d_handleKWS.update(d_baseHandeKWS)

                mAnchor,mShape,mDag = BLOCKSHAPES.create_face_anchorHandleCombo(self,
                                                                                d_basePosDat[_handleKey],
                                                                                _tag,
                                                                                None,
                                                                                side,
                                                                                size= _size_anchor,
                                                                                offsetAttr = 'conDirectOffset',
                                                                                
                                                                                **d_handleKWS)                    

                BLOCKSHAPES.create_visualTrack(self, mDag, md_handles['jawJoint'],
                                               _tag,mNoTransformNull)

        elif str_cheekUprSetup == 'lineSimple':
            
            d_sidePos = {}
            for side in ['left','right']:
                #First get our handles to generate a splite list of positions from
                _side = side.capitalize()

                crvTmp = CORERIG.create_at(create='curve',l_pos = [d_basePosDat['orbFront'+_side],
                                                                   d_basePosDat['cheek_0_1_'+side],
                                                                  d_basePosDat['orb'+_side]])
                d_sidePos[side]=CURVES.getUSplitList(crvTmp, self.numUprCheek)
                _l_clean.append(crvTmp)
                
            #Now we can iterate through those
            for i,p1 in enumerate(d_sidePos['right']):
                d_pairs['cheekUprLeft_{0}'.format(i)] = 'cheekUprRight_{0}'.format(i)
                d_pairs['cheekUprLeftJoint_{0}'.format(i)] = 'cheekUprRightJoint_{0}'.format(i)                                    
                p2 = d_sidePos['left'][i]
                
                for side in ['left','right']:
                    #Get our position
                    _tag = 'cheekUpr'+side.capitalize() + '_{0}'.format(i)
                    log.debug(cgmGEN.logString_msg(_str_func, 'cheek | {0}'.format(_tag)))
                    _dTmp = copy.copy(_d_name)
                    _dTmp['cgmDirection'] = side
                    _dTmp['cgmIterator'] = i
                    
                    d_handleKWS = {
                        'mode' : 'handle',
                        'mSurface':mSurf,
                        'handleShape' :'semiSphere',
                        'handleSize' : _size_sub,
                        'anchorSize' : _size_anchor,
                        'orientToSurf':True,
                        'orientToDriver':True,
                        'attachToSurf':True,
                        'nameDict':_dTmp,
                        'md_mirrorDat':md_mirrorDat,
                        'ml_handles':ml_handles,
                        'md_handles':md_handles,
                        'ml_jointHandles':ml_jointHandles,
                    }
                    d_handleKWS.update(d_baseHandeKWS)
    
                    mAnchor,mShape,mDag = BLOCKSHAPES.create_face_anchorHandleCombo(self,
                                                                                    d_sidePos[side][i],
                                                                                    _tag,
                                                                                    None,
                                                                                    side,
                                                                                    size= _size_anchor,
                                                                                    offsetAttr = 'conDirectOffset',
                                                                                    
                                                                                    **d_handleKWS)                    

                    BLOCKSHAPES.create_visualTrack(self, mDag, md_handles['jawJoint'],
                                                   _tag,mNoTransformNull)                    
                
            
            
        else:
            raise ValueError("Invalid cheekSetup: {0}".format(str_cheekUprSetup))
    
    if self.smileSetup:# cheek setup ============================================================
        log.debug(cgmGEN.logString_sub(_str_func,'Smile setup'))
        str_smileSetup = self.getEnumValueString('smileSetup')
        _d_name = {'cgmName':'smile',
                   'cgmType':'handleHelper'}
        
        if str_smileSetup == 'single':
            log.debug(cgmGEN.logString_msg(_str_func, 'single'))
            
            #mSurf =  self.jawFormLoft

            
            d_pairs['smileLeft'] = 'smileRight'
            d_pairs['smileLeftJoint'] = 'smileRightJoint'                
            
            for side in ['left','right']:
                #Get our position
                _tag = 'smile'+side.capitalize()
                mSurf =  self.getMessageAsMeta('uprJoin{0}FormLoft'.format(side.capitalize())) or self.getMessageAsMeta('jawFormLoft')
                
                _handleKey = _tag#'smile'+side
                log.debug(cgmGEN.logString_msg(_str_func, 'smile | {0}'.format(_tag)))
                _dTmp = copy.copy(_d_name)
                _dTmp['cgmDirection'] = side
                
                pprint.pprint(d_handleKWS)
                
                d_handleKWS = {
                    'mode' : 'handle',
                    'mSurface':mSurf,
                    'handleShape' :'semiSphere',
                    'handleSize' : _size_sub,
                    'anchorSize' : _size_anchor,
                    'orientToSurf':True,
                    'orientToDriver':True,
                    'attachToSurf':True,
                    'nameDict':_dTmp,
                    'md_mirrorDat':md_mirrorDat,
                    'ml_handles':ml_handles,
                    'md_handles':md_handles,
                    'ml_jointHandles':ml_jointHandles,
                }
                d_handleKWS.update(d_baseHandeKWS)

                mAnchor,mShape,mDag = BLOCKSHAPES.create_face_anchorHandleCombo(self,
                                                                                d_basePosDat[_handleKey],
                                                                                _tag,
                                                                                None,
                                                                                side,
                                                                                size= _size_anchor,
                                                                                offsetAttr = 'conDirectOffset',
                                                                                
                                                                                **d_handleKWS)                    

                BLOCKSHAPES.create_visualTrack(self, mDag, md_handles['jawJoint'],
                                               _tag,mNoTransformNull)


        elif str_smileSetup == 'lineSimple':
            
            d_sidePos = {}
            for side in ['left','right']:
                #First get our handles to generate a splite list of positions from
                _side = side.capitalize()

                crvTmp = CORERIG.create_at(create='curve',l_pos = [d_basePosDat['uprJoin_0_1_'+side],
                                                                  d_basePosDat['smile'+_side]])
                d_sidePos[side]=CURVES.getUSplitList(crvTmp, self.numSmile)
                #_l_clean.append(crvTmp)
                
            #Now we can iterate through those
            for i,p1 in enumerate(d_sidePos['right']):
                d_pairs['smilLeft_{0}'.format(i)] = 'smileRight_{0}'.format(i)
                d_pairs['smileLeftJoint_{0}'.format(i)] = 'smileRightJoint_{0}'.format(i)                                    
                p2 = d_sidePos['left'][i]
                
                for side in ['left','right']:
                    #Get our position
                    _tag = 'smile'+side.capitalize() + '_{0}'.format(i)
                    log.debug(cgmGEN.logString_msg(_str_func, 'smile | {0}'.format(_tag)))
                    _dTmp = copy.copy(_d_name)
                    _dTmp['cgmDirection'] = side
                    
                    _dTmp['cgmIterator'] = i
                    mSurf =  self.getMessageAsMeta('uprJoin{0}FormLoft'.format(side.capitalize()))
                    
                    d_handleKWS = {
                        'mode' : 'handle',
                        'mSurface':mSurf,
                        'handleShape' :'semiSphere',
                        'handleSize' : _size_sub,
                        'anchorSize' : _size_anchor,
                        'orientToSurf':True,
                        'orientToDriver':True,
                        'attachToSurf':True,
                        'nameDict':_dTmp,
                        'md_mirrorDat':md_mirrorDat,
                        'ml_handles':ml_handles,
                        'md_handles':md_handles,
                        'ml_jointHandles':ml_jointHandles,
                    }
                    d_handleKWS.update(d_baseHandeKWS)
                    
    
                    mAnchor,mShape,mDag = BLOCKSHAPES.create_face_anchorHandleCombo(self,
                                                                                    d_sidePos[side][i],
                                                                                    _tag,
                                                                                    None,
                                                                                    side,
                                                                                    size= _size_anchor,
                                                                                    offsetAttr = 'conDirectOffset',
                                                                                    
                                                                                    **d_handleKWS)                    

                    BLOCKSHAPES.create_visualTrack(self, mDag, md_handles['jawJoint'],
                                                   _tag,mNoTransformNull)       
        else:
            raise ValueError("Invalid cheekSetup: {0}".format(str_smileSetup))        
    
    
    if self.lipSetup:
        log.debug(cgmGEN.logString_sub(_str_func, 'lipSetup'))

        log.debug(cgmGEN.logString_msg(_str_func, 'mouthMove'))
        #------------------------------------------------------------
        _d = {'cgmName':'mouthMove',
              'cgmType':'shapeHelper'}
        
        dist_width = DIST.get_distance_between_points(md_dHandles['cornerFrontLeft'].p_position,
                                                      md_dHandles['cornerFrontRight'].p_position)
        
        mShape = cgmMeta.validateObjArg(CURVES.create_fromName(name='dumbell', 
                                                              size=dist_width * .75, 
                                                              direction='z+'),'cgmObject',setClass=1)
        #mHandleFactory.buildBaseShape('dumbell',baseSize = 3.0, shapeDirection = 'z+')
        mShape.p_parent = mStateNull
        mShape.p_position = DIST.get_pos_by_vec_dist(DIST.get_average_position([md_dHandles['uprPeak'].p_position,
                                                                                md_dHandles['lwrPeak'].p_position]), 
                                                     vec_self,
                                                     _offset)            
        mHandleFactory.color(mShape.mNode)            
        RIGGEN.store_and_name(mShape,_d)

        _d['cgmType'] = 'handleHelper'
        
        mDag = mHandleFactory.buildBaseShape('sphere',baseSize = dist_width, shapeDirection = 'z+')
        #TRANS.scale_to_boundingBox(mDag.mNode, [_muzzleSize,_muzzleSize,_muzzleSize/2.0])
        mDag.p_parent = mStateNull
        mDag.p_position = DIST.get_pos_by_vec_dist(md_dHandles['uprFront'].p_position, 
                                                     vec_self,
                                                     -dist_width/2.0)            
        mHandleFactory.color(mDag.mNode,controlType='sub')
        RIGGEN.store_and_name(mDag,_d)
        
        mDag.doStore('shapeHelper',mShape)
        mShape.doStore('dagHelper',mDag)
        mDag.p_parent = mStateNull
        
        mStateNull.connectChildNode(mDag, 'mouthMove'+'Dag','block')
        md_handles['mouthMove'] = mDag
        md_handles['mouthMoveShape'] = mDag
        
        
        # Lips -------------------------------------------------------------------
        log.debug(cgmGEN.logString_msg(_str_func, 'lips'))
        
        d_anchorDat = {}
        md_anchors = {}
        
        for tag in ['upr','lwr']:
            mCrv = md_dCurves[tag+'_Peak']
            #SURF.get_surfaceSplitCurves()
            _l_split =  CURVES.getUSplitList(mCrv.mNode,self.numConLips + 2,rebuild=1)
            
            d_split = MATH.get_evenSplitDict(_l_split)
            d_anchorDat[tag] = {}
            for t,l in list(d_split.items()):
                d_anchorDat[tag][t] = l
                
                #for i,p in enumerate(l):
                #    LOC.create(position=p,name="{0}_{1}_{2}".format(tag,t,i))
            
        
        #Lip Anchors....
        _d = {'cgmName':'lip',
              'cgmType':'preAnchor'}
        
        mLipLoft = self.attachLipsFormLoft

        for section,sectionDat in list(d_anchorDat.items()):
            md_anchors[section] = {}
            #_d['cgmPosition'] = section
            
            _base = 0
            if section == 'lwr':
                _base = 1
                
            l_tags = ["{0}Lip".format(section)]
            
            for side,sideDat in list(sectionDat.items()):
                if side == 'start':side='right'
                elif side =='end':side = 'left'
                
                md_anchors[section][side] = {}
                md_anchors[section][side]['tags'] = []
                md_anchors[section][side]['ml'] = []
                
                d_tmp = md_anchors[section][side]
                
                b_more = False
                if len(sideDat) > 2:
                    b_more = True
                    
                if side == 'left':
                    sideDat.reverse()
                    
                if section == 'lwr' and len(sideDat)>1:
                    sideDat.pop(0)
                    
                for i,p in enumerate(sideDat):
                    if side == 'center':
                        tag = ''.join(l_tags)
                    else:
                        if not i and section == 'upr':
                           # l_use = copy.copy(l_tags)
                            #l_use.append('Corner')
                            #tag = ''.join(l_use)
                            tag = 'lipCorner'
                        else:
                            l_use = copy.copy(l_tags)
                            if b_more:l_use.append("_{0}".format(i+_base))
                            tag = ''.join(l_use)
                        
                    #LOC.create(position=p,name=tag)
                    
                    
                    
                    _dUse = copy.copy(_d)
                    _dUse['cgmName'] = tag
                    _dUse['cgmDirection'] = side
                    
                    mAnchor = BLOCKSHAPES.create_face_anchor(self,p,
                                                             mLipLoft,
                                                             tag,
                                                             None,
                                                             side,
                                                             nameDict=_dUse,
                                                             mParent=mStateNull,
                                                             size= _size_anchorLips)
                    
                    #mAnchor.rotate = 0,0,0
                    
                    d_tmp['tags'].append(tag)
                    d_tmp['ml'].append(mAnchor)
                    ml_handles.append(mAnchor)
                    md_mirrorDat[side].append(mAnchor)
                    

        
        #...get my anchors in lists...-----------------------------------------------------------------
        ml_uprLeft = copy.copy(md_anchors['upr']['left']['ml'])
        ml_uprLeft.reverse()
        ml_uprRight = md_anchors['upr']['right']['ml']
        
        ml_lwrLeft = copy.copy(md_anchors['lwr']['left']['ml'])
        ml_lwrLeft.reverse()
        
        ml_lwrRight = md_anchors['lwr']['right']['ml']
        
        md_anchorsLists = {}
        
        if md_anchors['upr'].get('center'):
            ml_uprCenter = md_anchors['upr']['center']['ml']
            ml_lwrCenter = md_anchors['lwr']['center']['ml']
            
            md_anchorsLists['upr'] = ml_uprRight + ml_uprCenter + ml_uprLeft
            md_anchorsLists['lwr'] = ml_uprRight[:1] + ml_lwrRight + ml_lwrCenter + ml_lwrLeft + ml_uprLeft[-1:]
                            
        else:
            md_anchorsLists['upr'] = ml_uprRight + ml_uprLeft
            md_anchorsLists['lwr'] = ml_uprRight[:1] + ml_lwrRight + ml_lwrLeft + ml_uprLeft[-1:]
        #pprint.pprint(md_anchors)
        #pprint.pprint(d_anchorDat)
        #pprint.pprint(md_anchorsLists)
        
        
        #...make our driver curves...---------------------------------------------------------------
        log.debug(cgmGEN.logString_msg('driver curves'))
        d_curveCreation = {}
        for section,sectionDat in list(md_anchorsLists.items()):
            #for side,dat in sectionDat.iteritems():
            d_curveCreation[section+'Driver'] = {'ml_handles': sectionDat,
                                                 'rebuild':1}
                
        
        #...anchor | aim ----------------------------------------------------------------------------
        log.debug(cgmGEN.logString_msg('anchor | aim'))
        
        for tag,sectionDat in list(md_anchors.items()):
            for side,sideDat in list(sectionDat.items()):
                if side == 'center':
                    continue
                
                if side == 'left':
                    _aim = [-1,0,0]
                else:
                    _aim = [1,0,0]
                    
                for i,mDriver in enumerate(sideDat['ml']):
                    _mode = None
                    
                    if tag == 'upr' and not i:
                        _mode = 'simple'

                    if _mode == 'simple':
                        loc = LOC.create(position = DGETAVG([md_anchors['upr'][side]['ml'][1].p_position,
                                                             md_anchors['lwr'][side]['ml'][0].p_position]))
                        
                            
                        mc.delete(mc.aimConstraint(loc,
                                                   mDriver.mNode,
                                                   maintainOffset = False, weight = 1,
                                                   aimVector = _aim,
                                                   upVector = [0,1,0],
                                                   worldUpVector = [0,1,0],
                                                   worldUpObject = self.mNode,
                                                   worldUpType = 'objectRotation'))
                        
                        mc.delete(loc)
                    else:
                        try:_tar=sideDat[i+1].mNode
                        except:_tar=md_anchors[tag]['center']['ml'][0].mNode

                        mc.delete(mc.aimConstraint(_tar,
                                         mDriver.mNode,
                                         maintainOffset = False, weight = 1,
                                         aimVector = _aim,
                                         upVector = [0,1,0],
                                         worldUpVector = [0,1,0],
                                         worldUpObject = self.mNode,
                                         worldUpType = 'objectRotation' ))
        
        
    
        #Make our Lip handles...-------------------------------------------------------------------------
        log.debug(cgmGEN.logString_sub('Handles'))
        md_prerigDags = {}
        md_jointHelpers = {}
        
        _d = {'cgmName':''}
        
        #...get our driverSetup
        for section,sectionDat in list(md_anchors.items()):
            log.debug(cgmGEN.logString_msg(section))
            
            #md_handles[section] = {}
            md_prerigDags[section] = {}
            md_jointHelpers[section] = {}
            
            if section == 'upr':
                _mainShape = 'loftCircleHalfUp'
            else:
                _mainShape = 'loftCircleHalfDown'
                
            for side,dat in list(sectionDat.items()):
                log.debug(cgmGEN.logString_msg(side))
                
                #md_handles[section][side] = []
                md_prerigDags[section][side] = []
                md_jointHelpers[side] = []
                
                _ml_shapes = []
                _ml_prerigDags = []
                _ml_jointShapes = []
                _ml_jointHelpers = []
                
                tag = section+'Lip'+STR.capFirst(side)
                _ml_anchors = dat['ml']
                
                
                if side == 'center':
                    mAnchor = _ml_anchors[0]
                    p = mAnchor.p_position
                    d_use = mAnchor.getNameDict(ignore=['cgmType'])
                    
                    mShape, mDag = BLOCKSHAPES.create_face_handle(self,p,
                                                                  tag,
                                                                  None,
                                                                  side,
                                                                  size = _size_anchor,
                                                                  mDriver=mAnchor,
                                                                  mSurface=mLipLoft,
                                                                  mainShape=_mainShape,
                                                                  jointShape='locatorForm',
                                                                  controlType='main',#_controlType,
                                                                  mode='handle',
                                                                  depthAttr = 'jointDepthLip',
                                                                  plugDag= 'preDag',
                                                                  plugShape= 'preShape',
                                                                  attachToSurf=True,
                                                                  orientToDriver = True,
                                                                  nameDict= d_use,**d_baseHandeKWS)
                    _ml_shapes.append(mShape)
                    _ml_prerigDags.append(mDag)                            
                    

                
                else:
                    #mCrv = md_resCurves.get(section+'Driver')
                    #if mCrv:
                    for i,mAnchor in enumerate(_ml_anchors):
                        _shapeUse = _mainShape
                        if section == 'upr' and not i:
                            if side == 'left':
                                _shapeUse = 'widePos'
                            else:
                                _shapeUse = 'wideNeg'
                                
                        p = mAnchor.p_position
                        d_use = mAnchor.getNameDict(ignore=['cgmType'])

                        mShape, mDag = BLOCKSHAPES.create_face_handle(self,p,
                                                                      tag,
                                                                      None,
                                                                      side,
                                                                      size = _size_anchor,
                                                                      mDriver=mAnchor,
                                                                      mSurface=mLipLoft,
                                                                      mainShape=_shapeUse,
                                                                      jointShape='locatorForm',
                                                                      depthAttr = 'jointDepthLip',
                                                                      
                                                                      controlType='main',#_controlType,
                                                                      mode='handle',
                                                                      plugDag= 'preDag',
                                                                      plugShape= 'preShape',
                                                                      attachToSurf=True,
                                                                      orientToDriver = True,
                                                                      nameDict= d_use,**d_baseHandeKWS)
                        

                        _ml_shapes.append(mShape)
                        _ml_prerigDags.append(mDag)                            
                        
                        
                        

                mStateNull.msgList_connect('{0}PrerigShapes'.format(tag),_ml_shapes)
                mStateNull.msgList_connect('{0}PrerigHandles'.format(tag),_ml_prerigDags)
                md_mirrorDat[side].extend(_ml_shapes + _ml_prerigDags)
                md_prerigDags[section][side] = _ml_prerigDags
                ml_handles.extend(_ml_shapes + _ml_prerigDags)
        
        
        #...get control joint handles...-----------------------------------------------------------------
        ml_uprCenter = md_prerigDags['upr']['center']
        ml_uprLeft = copy.copy(md_prerigDags['upr']['left'])
        ml_uprLeft.reverse()
        ml_uprRight = md_prerigDags['upr']['right']
        
        ml_lwrCenter = md_prerigDags['lwr']['center']
        ml_lwrLeft = copy.copy(md_prerigDags['lwr']['left'])
        ml_lwrLeft.reverse()
        
        ml_lwrRight = md_prerigDags['lwr']['right']
        
        md_handleCrvDrivers = {}
        
        md_handleCrvDrivers['upr'] = ml_uprRight + ml_uprCenter + ml_uprLeft
        md_handleCrvDrivers['lwr'] = ml_uprRight[:1] + ml_lwrRight + ml_lwrCenter + ml_lwrLeft + ml_uprLeft[-1:]
        
        #pprint.pprint(md_anchors)
        #pprint.pprint(d_anchorDat)
        #pprint.pprint(md_crvDrivers)

        #...make our driver curves...---------------------------------------------------------------
        log.debug(cgmGEN.logString_msg('driven curves'))
        for section,sectionDat in list(md_handleCrvDrivers.items()):
            d_curveCreation[section+'Driven'] = {'ml_handles': sectionDat,
                                                 'rebuild':1}
                
        md_res = self.UTILS.create_defineCurve(self, d_curveCreation, {}, mNoTransformNull,'preCurve')
        md_resCurves = md_res['md_curves']
        ml_resCurves = md_res['ml_curves']                        
        
        
        #Joint handles =============================================================================
        log.debug(cgmGEN.logString_sub('joints'))
        
        d_lipDrivenDat = {}
        d_lipDriverDat = {}
        md_lipDrivers = {}
        
        #...get our spilt data ---------------------------------------------------------------------
        log.debug(cgmGEN.logString_msg('joints | split data'))
        
        for tag in 'upr','lwr':
            mDriverCrv = md_resCurves[tag+'Driver']
            mDrivenCrv = md_resCurves[tag+'Driven']
            #_crv = CORERIG.create_at(create='curveLinear',
            #                         l_pos=[mObj.p_position for mObj in md_handleCrvDrivers[tag]])
            
            _count = self.getMayaAttr('numJointsLip'+tag.capitalize())
            
            l_driverPos =  CURVES.getUSplitList(mDriverCrv.mNode,_count + 2,rebuild=0,
                                                startSplitFactor=self.preLipStartSplit)
                                                
            l_drivenPos = CURVES.getUSplitList(mDrivenCrv.mNode,_count + 2,rebuild=0,
                                               startSplitFactor=self.preLipStartSplit)
                                               
            
            d_split_driven = MATH.get_evenSplitDict(l_drivenPos)
            d_split_driver = MATH.get_evenSplitDict(l_driverPos)
            
            d_lipDrivenDat[tag] = {}
            d_lipDriverDat[tag] = {}
            
            for t,l in list(d_split_driven.items()):
                d_lipDrivenDat[tag][t] = l
                
                #for i,p in enumerate(l):
                    #LOC.create(position=p,name="{0}_{1}_{2}".format(tag,t,i))                    
            
            for t,l in list(d_split_driver.items()):
                d_lipDriverDat[tag][t] = l
            

        
        _d = {'cgmName':'lip',
              'cgmType':'preAnchor'}
        
        _sizeDirect = _size_sub * .4
        
        md_lipJoints = {}
        for section,sectionDat in list(d_lipDrivenDat.items()):
            mDriverCrv = md_resCurves[section+'Driver']
            mDriverCrv.v = 0
            
            mDrivenCrv = md_resCurves[section+'Driven']
            mDrivenCrv.v = 0
            
            md_lipJoints[section] = {}
            md_lipDrivers[section] = {}
            
            #_d['cgmPosition'] = section
            
            _base = 0
            if section == 'lwr':
                _base = 1
            
            
            for side,sideDat in list(sectionDat.items()):
                driverDat = d_lipDriverDat[section][side]
                
                if side == 'start':side='right'
                elif side =='end':side = 'left'
                
                _ml_jointShapes = []
                _ml_jointHelpers = []
                _ml_lipDrivers = []
                
                md_lipJoints[section][side] = []
                md_lipDrivers[section][side] = []
                
                l_bridge = md_lipJoints[section][side]
                l_tags = ['{0}Lip'.format(section)]
                
                b_more = False
                if len(sideDat) > 2:
                    b_more = True
                    
                if side == 'left':
                    sideDat.reverse()
                    driverDat.reverse()
                    
                if section == 'lwr' and len(sideDat)>1:
                    sideDat.pop(0)
                    driverDat.pop(0)
                    
                for i,p_driven in enumerate(sideDat):
                    p_driver = driverDat[i]
                    _dUse = copy.copy(_d)
                    
                    if side == 'center':
                        tag = ''.join(l_tags)
                    else:
                        if not i and section == 'upr':
                            #l_use = copy.copy(l_tags)
                            #l_use.append('Corner')
                            #tag = ''.join(l_use)
                            tag = 'lipCorner'
                            #_dUse['cgmDirectionModifier'] = 'corner'
                        else:
                            l_use = copy.copy(l_tags)
                            if b_more:l_use.append("_{0}".format(i+_base))
                            tag = ''.join(l_use)
                            #_dUse['cgmIterator'] = i+_base

                    _dUse['cgmName'] = tag#'lip' #+ STR.capFirst(tag)
                    _dUse['cgmDirection'] = side
                    
                    #Driver ...
                    mDriver = self.doCreateAt(setClass=1)#self.doLoc()#
                    mDriver.rename("{0}_{1}_{2}_{3}_driver".format(section, side,_dUse['cgmName'],i))
                    mDriver.p_position = p_driver
                    mDriver.p_parent = mNoTransformNull#mStateNull
                    
                    _res = RIGCONSTRAINT.attach_toShape(mDriver.mNode,mDriverCrv.mNode,'conPoint')
                    TRANS.parent_set(_res[0], mNoTransformNull.mNode)                        
                    
                    
                    mShape, mDag = BLOCKSHAPES.create_face_handle(self,
                                                                  p_driven,tag,None,side,
                                                                  mDriver=mDriver,
                                                                  
                                                                  mSurface = mLipLoft,
                                                                  mAttachCrv = mDrivenCrv,
                                                                  mainShape='semiSphere',
                                                                  #jointShape='sphere',
                                                                  size= _size,#_sizeDirect,
                                                                  mode='joint',
                                                                  controlType='sub',
                                                                  plugDag= 'jointHelper',
                                                                  plugShape= 'directShape',
                                                                  offsetAttr = 'conDirectOffset',
                                                                  
                                                                  attachToSurf=True,
                                                                  orientToDriver=True,
                                                                  nameDict= _dUse,**d_baseHandeKWS)
                    
                    md_mirrorDat[side].append(mShape)
                    md_mirrorDat[side].append(mDag)
                    
                    _ml_jointShapes.append(mShape)
                    _ml_jointHelpers.append(mDag)
                    _ml_lipDrivers.append(mDriver)

                tag = section+'Lip'+STR.capFirst(side)
                mStateNull.msgList_connect('{0}JointHelpers'.format(tag),_ml_jointHelpers)
                mStateNull.msgList_connect('{0}JointShapes'.format(tag),_ml_jointShapes)
                md_jointHelpers[section][side] = _ml_jointHelpers
                ml_handles.extend(_ml_jointShapes)
                ml_handles.extend(_ml_jointHelpers)
                md_mirrorDat[side].extend(_ml_jointShapes + _ml_jointHelpers)
                md_lipDrivers[section][side] = _ml_lipDrivers
                
        
        #Aim our lip drivers...------------------------------------------------------------------
        log.debug(cgmGEN.logString_msg('aim lip drivers'))

            
        for tag,sectionDat in list(md_lipDrivers.items()):
            for side,sideDat in list(sectionDat.items()):
                ml_check = md_anchorsLists[tag]
                l_check = [mObj.mNode for mObj in ml_check]
                
                if side == 'left':
                    _aim = [-1,0,0]
                else:
                    _aim = [1,0,0]
                    
                for i,mDriver in enumerate(sideDat):
                    _mode = None
                    
                    if tag == 'upr' and not i:
                        _mode = 'simple'
                    if side == 'center':
                        _mode = 'simple'
                        
                    _closest = DIST.get_closestTarget(mDriver.mNode,l_check)
                        
                    if _mode == 'simple':
                        mc.orientConstraint(_closest, mDriver.mNode, maintainOffset = False)
                    else:
                        #if mDriver == sideDat[-1]:
                        #    _tar = md_lipDrivers[tag]['center'][0].mNode
                        #else:
                        try:
                            _tar = sideDat[i+1].mNode
                            
                            mc.aimConstraint(_tar,
                                             mDriver.mNode,
                                             maintainOffset = False, weight = 1,
                                             aimVector = _aim,
                                             upVector = [0,0,1],
                                             worldUpVector = [0,0,1],
                                             worldUpObject = _closest,
                                             worldUpType = 'objectRotation' )
                        except:
                            log.error("Unable to find aim dat for: {0} | {1}".format(tag,i))
                    
        
        #Driven Curve

            
        ml_uprLeft = copy.copy(md_jointHelpers['upr']['left'])
        ml_uprLeft.reverse()
        ml_uprRight = md_jointHelpers['upr']['right']
        
        

            
        ml_lwrLeft = copy.copy(md_jointHelpers['lwr']['left'])
        ml_lwrLeft.reverse()
        
        ml_lwrRight = md_jointHelpers['lwr']['right']
        
        md_crvDrivers = {}
        
        #...if we have odd counts we have centers, else not
        if not MATH.is_even(self.numJointsLipUpr):
            ml_uprCenter = md_jointHelpers['upr']['center']
            md_crvDrivers['upr'] = ml_uprRight + ml_uprCenter + ml_uprLeft
        else:
            md_crvDrivers['upr'] = ml_uprRight + ml_uprLeft
            
        if not MATH.is_even(self.numJointsLipLwr):
            ml_lwrCenter = md_jointHelpers['lwr']['center']
            md_crvDrivers['lwr'] = ml_uprRight[:1] + ml_lwrRight + ml_lwrCenter + ml_lwrLeft + ml_uprLeft[-1:]
        else:
            md_crvDrivers['lwr'] = ml_uprRight[:1] + ml_lwrRight + ml_lwrLeft + ml_uprLeft[-1:]
            
        #pprint.pprint(md_anchors)
        #pprint.pprint(d_anchorDat)
        #pprint.pprint(md_crvDrivers)
        
        d_driven = {}
        #...make our driver curves...---------------------------------------------------------------
        log.debug(cgmGEN.logString_msg('driven curves'))
        for section,sectionDat in list(md_crvDrivers.items()):
            #for side,dat in sectionDat.iteritems():
            d_driven[section+'Result'] = {'ml_handles': sectionDat,
                                          'rebuild':1}
            
                
                
        md_res = self.UTILS.create_defineCurve(self, d_driven, {}, mNoTransformNull,'preCurve')
        md_resCurves.update(md_res['md_curves'])
        ml_resCurves.extend(md_res['ml_curves'])
        
    
   

        
    
    #Mirror setup --------------------------------
    log.debug(cgmGEN.logString_sub('mirror'))
    idx_ctr = 0
    idx_side = 0
    
    log.debug(cgmGEN.logString_msg('mirror | center'))
    for mHandle in md_mirrorDat['center']:
        mHandle = cgmMeta.validateObjArg(mHandle,'cgmControl')
        mHandle._verifyMirrorable()
        mHandle.mirrorSide = 0
        mHandle.mirrorIndex = idx_ctr
        idx_ctr +=1
        mHandle.mirrorAxis = "translateX,rotateY,rotateZ"

    log.debug(cgmGEN.logString_msg('mirror | sides'))
        
    for i,mHandle in enumerate(md_mirrorDat['left']):
        mLeft = cgmMeta.validateObjArg(mHandle,'cgmControl') 
        mRight = cgmMeta.validateObjArg(md_mirrorDat['right'][i],'cgmControl')

        for mObj in mLeft,mRight:
            mObj._verifyMirrorable()
            mObj.mirrorAxis = "translateX,rotateY,rotateZ"
            mObj.mirrorIndex = idx_side
        mLeft.mirrorSide = 1
        mRight.mirrorSide = 2
        mLeft.doStore('mirrorHandle',mRight)
        mRight.doStore('mirrorHandle',mLeft)            
        idx_side +=1
        
    
    # Connect -------------------------------------------------
    self.msgList_connect('prerigHandles', ml_handles)
    self.msgList_connect('jointHandles', ml_jointHandles)        

    try:mc.delete(_l_clean)
    except:pass
    
    self.blockState = 'prerig'
    return
    
    
    #except Exception as err:
        #cgmGEN.cgmExceptCB(Exception,err)
        
#=============================================================================================================
#>> Skeleton
#=============================================================================================================
def create_jointFromHandle(mHandle=None,mParent = False,cgmType='skinJoint'):
    mJnt = mHandle.doCreateAt('joint')
    mJnt.doCopyNameTagsFromObject(mHandle.mNode,ignore = ['cgmType'])
    mJnt.doStore('cgmType',cgmType)
    mJnt.doName()
    JOINT.freezeOrientation(mJnt.mNode)

    mJnt.p_parent = mParent
    try:ml_joints.append(mJnt)
    except:pass
    return mJnt
    
def skeleton_check(self):
    return True

def skeleton_build(self, forceNew = True):
    _short = self.mNode
    _str_func = '[{0}] > skeleton_build'.format(_short)
    log.debug("|{0}| >> ...".format(_str_func)) 
    
    _radius = self.atUtils('get_shapeOffset') * .25# or 1
    ml_joints = []
    
    mModule = self.atUtils('module_verify')
    
    mRigNull = mModule.rigNull
    if not mRigNull:
        raise ValueError("No rigNull connected")
    
    mPrerigNull = self.prerigNull
    if not mPrerigNull:
        raise ValueError("No prerig null")
    
    mRoot = self.UTILS.skeleton_getAttachJoint(self)
    mLipRoot = mRoot
    
    #>> If skeletons there, delete -------------------------------------------------------------------------- 
    _bfr = mRigNull.msgList_get('moduleJoints',asMeta=True)
    if _bfr:
        log.debug("|{0}| >> Joints detected...".format(_str_func))            
        if forceNew:
            log.debug("|{0}| >> force new...".format(_str_func))                            
            mc.delete([mObj.mNode for mObj in _bfr])
        else:
            return _bfr
        
    #_baseNameAttrs = ATTR.datList_getAttrs(self.mNode,'nameList')
    #_l_baseNames = ATTR.datList_get(self.mNode, 'nameList')
    
    if self.muzzleSetup == 2:
        log.debug("|{0}| >>  muzzle joint...".format(_str_func)+ '-'*40)
        mObj = mPrerigNull.getMessageAsMeta('muzzle'+'DagHelper')
        mJnt = create_jointFromHandle(mObj,mRoot)
        mPrerigNull.doStore('muzzleJoint',mJnt)
        mJnt.p_parent = mRoot
        ml_joints.append(mJnt)
        
        mLipRoot = mJnt
        
    mJawUpr = False
    if self.jawLwrSetup:
        mObj = mPrerigNull.getMessageAsMeta('jaw'+'DagHelper')
        mJaw = create_jointFromHandle(mObj,mRoot)
        mPrerigNull.doStore('jawJoint',mJaw)
        ml_joints.append(mJaw)
        mJawUpr = mJaw
    else:
        mJaw = mRoot
        mJawUpr = mRoot
        
    if self.jawUprSetup:
        mObj = mPrerigNull.getMessageAsMeta('jawUpr'+'DagHelper')
        mJawUpr = create_jointFromHandle(mObj,mRoot)
        mPrerigNull.doStore('jawUprJoint',mJawUpr)
        ml_joints.append(mJawUpr)
                
    if self.lipSetup:
        log.debug("|{0}| >>  lipSetup...".format(_str_func)+ '-'*40)
        
        _d_lip = {'cgmName':'lip'}
        
        for d in 'upr','lwr':
            log.debug("|{0}| >>  lip {1}...".format(_str_func,d)+ '-'*20)
            d_dir = copy.copy(_d_lip)
            d_dir['cgmPosition'] = d
        
            for side in ['right','center','left']:
                d_dir['cgmDirection'] = side
                key = d+'Lip'+side.capitalize()        
                mHandles = mPrerigNull.msgList_get('{0}JointHelpers'.format(key))
                ml = []
                for mHandle in mHandles:
                    mJnt = create_jointFromHandle(mHandle,mLipRoot)
                    ml.append(mJnt)
                    mShape = mHandle.shapeHelper
                    mShape.connectChildNode(mJnt,'targetJoint')
                    
                    
                mPrerigNull.msgList_connect('{0}Joints'.format(key),ml)
                ml_joints.extend(ml)
        
    
    _tongueSetup = self.tongueSetup
    if _tongueSetup:#============================================================
        log.debug(cgmGEN.logString_sub(_str_func,'tongue'))
        if _tongueSetup == 1:
            mObj = mPrerigNull.getMessageAsMeta('tongue'+'DagHelper')
            mJnt = create_jointFromHandle(mObj,mRoot)
            mPrerigNull.doStore('tongueJoint',mJnt)
            mJnt.p_parent = mJaw
            ml_joints.append(mJnt)
            
            
    if self.teethUprSetup:
        log.debug("|{0}| >>  teethUpr...".format(_str_func)+ '-'*40)
        mObj = mPrerigNull.getMessageAsMeta('teethUpr'+'DagHelper')
        mJnt = create_jointFromHandle(mObj,mRoot)
        mPrerigNull.doStore('teethUprJoint',mJnt)
        mJnt.p_parent = mJawUpr
        ml_joints.append(mJnt)
            
    if self.teethLwrSetup:
        log.debug("|{0}| >>  teethLwr...".format(_str_func)+ '-'*40)
        mObj = mPrerigNull.getMessageAsMeta('teethLwr'+'DagHelper')
        mJnt = create_jointFromHandle(mObj,mRoot)
        mPrerigNull.doStore('teethLwrJoint',mJnt)
        mJnt.p_parent = mJaw
        ml_joints.append(mJnt)
            
            
            
    if self.chinSetup:
        log.debug("|{0}| >>  chinSetup...".format(_str_func)+ '-'*40)
        mObj = mPrerigNull.getMessageAsMeta('chin'+'DagHelper')
        mJnt = create_jointFromHandle(mObj,mRoot)
        mPrerigNull.doStore('chinJoint',mJnt)
        mJnt.p_parent = mJaw
        ml_joints.append(mJnt)
        

    if self.noseSetup:
        log.debug("|{0}| >>  noseSetup".format(_str_func)+ '-'*40)
        str_noseSetup = self.getEnumValueString('noseSetup')
    
        if str_noseSetup == 'simple':
            log.debug("|{0}| >>  noseSetup: {1}".format(_str_func,str_noseSetup))
            
            _tag = 'noseBase'
            mNoseBase = create_jointFromHandle(mPrerigNull.getMessageAsMeta('{0}DagHelper'.format(_tag)),
                                               mRoot)
            mPrerigNull.doStore('{0}Joint'.format(_tag),mNoseBase)
            ml_joints.append(mNoseBase)
            
            #NoseTip ----------------------------------------------------------------------
            if self.numJointsNoseTip:
                log.debug("|{0}| >>  {1}...".format(_str_func,'noseTip'))
                _tag = 'noseTip'
                mNoseTip = create_jointFromHandle(mPrerigNull.getMessageAsMeta('{0}DagHelper'.format(_tag)),
                                                  mNoseBase)
                mPrerigNull.doStore('{0}Joint'.format(_tag),mNoseTip)
                ml_joints.append(mNoseTip)

            #Nostrils -------------------------------------------------------------------
            if self.numJointsNostril:
                for side in ['left','right']:
                    _tag = 'nostril'+side.capitalize()
                    log.debug("|{0}| >>  {1}...".format(_str_func,_tag))
                    mJnt = create_jointFromHandle(mPrerigNull.getMessageAsMeta('{0}DagHelper'.format(_tag)),
                                                  mNoseBase)
                    mPrerigNull.doStore('{0}Joint'.format(_tag),mJnt)
                    ml_joints.append(mJnt)
                    
        else:
            raise ValueError("Invalid noseSetup: {0}".format(str_noseSetup))
        
    if self.cheekSetup:
        log.debug("|{0}| >>  Cheeksetup".format(_str_func)+ '-'*40)
        str_cheekSetup = self.getEnumValueString('cheekSetup')
        if str_cheekSetup == 'single':
            log.debug("|{0}| >>  cheekSetup: {1}".format(_str_func,str_cheekSetup))
            
            for side in ['left','right']:
                _tag = 'cheek'+side.capitalize()
                log.debug("|{0}| >>  {1}...".format(_str_func,_tag))
                mJnt = create_jointFromHandle(mPrerigNull.getMessageAsMeta('{0}DagHelper'.format(_tag)),
                                              mJaw)
                mPrerigNull.doStore('{0}Joint'.format(_tag),mJnt)
                ml_joints.append(mJnt)
                
        else:
            raise ValueError("Invalid cheekSetup: {0}".format(str_cheekSetup))
        
    if self.cheekUprSetup:
        log.debug("|{0}| >>  CheekUpr Setup".format(_str_func)+ '-'*40)
        str_cheekUprSetup = self.getEnumValueString('cheekUprSetup')
        log.debug("|{0}| >>  cheekUprSetup: {1}".format(_str_func,str_cheekUprSetup))
        
        if str_cheekUprSetup == 'single':            
            for side in ['left','right']:
                _tag = 'cheekUpr'+side.capitalize()
                log.debug("|{0}| >>  {1}...".format(_str_func,_tag))
                mJnt = create_jointFromHandle(mPrerigNull.getMessageAsMeta('{0}DagHelper'.format(_tag)),
                                              mJaw)
                mPrerigNull.doStore('{0}Joint'.format(_tag),mJnt)
                ml_joints.append(mJnt)
        
        elif str_cheekUprSetup == 'lineSimple':
            for side in ['left','right']:
                _found = True
                i = 0
                while _found == True:
                    _tag = 'cheekUpr'+side.capitalize()+ "_{0}".format(i)
                    log.debug("|{0}| >>  {1}...".format(_str_func,_tag))
                    mObj = mPrerigNull.getMessageAsMeta('{0}DagHelper'.format(_tag))
                    if not mObj:
                        _found = False
                        break
                    mJnt = create_jointFromHandle(mObj,
                                                  mJaw)
                    mPrerigNull.doStore('{0}Joint'.format(_tag),mJnt)
                    ml_joints.append(mJnt)            
                    i+=1
                
        else:
            raise ValueError("Invalid cheekUprSetup: {0}".format(str_cheekUprSetup))
        
    if self.smileSetup:
        log.debug("|{0}| >>  Smile Setup".format(_str_func)+ '-'*40)
        str_smileSetup = self.getEnumValueString('smileSetup')
        log.debug("|{0}| >>  smileSetup: {1}".format(_str_func,str_smileSetup))
        
        if str_smileSetup == 'single':
            
            for side in ['left','right']:
                _tag = 'smile'+side.capitalize()
                log.debug("|{0}| >>  {1}...".format(_str_func,_tag))
                mJnt = create_jointFromHandle(mPrerigNull.getMessageAsMeta('{0}DagHelper'.format(_tag)),
                                              mJaw)
                mPrerigNull.doStore('{0}Joint'.format(_tag),mJnt)
                ml_joints.append(mJnt)
                
        elif str_cheekUprSetup == 'lineSimple':
            for side in ['left','right']:
                _found = True
                i = 0
                while _found == True:
                    _tag = 'smile'+side.capitalize()+ "_{0}".format(i)
                    log.debug("|{0}| >>  {1}...".format(_str_func,_tag))
                    mObj = mPrerigNull.getMessageAsMeta('{0}DagHelper'.format(_tag))
                    if not mObj:
                        _found = False
                        break
                    mJnt = create_jointFromHandle(mObj,
                                                  mJaw)
                    mPrerigNull.doStore('{0}Joint'.format(_tag),mJnt)
                    ml_joints.append(mJnt)            
                    i+=1
        else:
            raise ValueError("Invalid smileSetup: {0}".format(str_smileSetup))    

    if self.sneerSetup:
        log.debug("|{0}| >>  sneerSetup".format(_str_func)+ '-'*40)
        str_sneerSetup = self.getEnumValueString('sneerSetup')
        if str_sneerSetup == 'single':
            log.debug("|{0}| >>  sneerSetup: {1}".format(_str_func,str_sneerSetup))
            
            for side in ['left','right']:
                _tag = 'sneer'+side.capitalize()
                log.debug("|{0}| >>  {1}...".format(_str_func,_tag))
                mJnt = create_jointFromHandle(mPrerigNull.getMessageAsMeta('{0}DagHelper'.format(_tag)),
                                              mJaw)
                mPrerigNull.doStore('{0}Joint'.format(_tag),mJnt)
                ml_joints.append(mJnt)
                
        else:
            raise ValueError("Invalid cheekSetup: {0}".format(str_sneerSetup))    
                
    #>> ===========================================================================
    mRigNull.msgList_connect('moduleJoints', ml_joints)
    self.msgList_connect('moduleJoints', ml_joints)
    
    #pprint.pprint(ml_joints)

    for mJnt in ml_joints:
        mJnt.displayLocalAxis = 1
        mJnt.radius = _radius
    for mJnt in ml_joints:mJnt.rotateOrder = 5
        
    return ml_joints    
    
   
    

    
    
    
    #>> Head ===================================================================================
    log.debug("|{0}| >> Head...".format(_str_func))
    p = POS.get( ml_prerigHandles[-1].jointHelper.mNode )
    mHeadHelper = ml_formHandles[0].orientHelper
    
    #...create ---------------------------------------------------------------------------
    mHead_jnt = cgmMeta.cgmObject(mc.joint (p=(p[0],p[1],p[2])))
    mHead_jnt.parent = False
    #self.copyAttrTo(_baseNameAttrs[-1],mHead_jnt.mNode,'cgmName',driven='target')
    
    #...orient ----------------------------------------------------------------------------
    #cgmMeta.cgmObject().getAxisVector
    CORERIG.match_orientation(mHead_jnt.mNode, mHeadHelper.mNode)
    JOINT.freezeOrientation(mHead_jnt.mNode)
    
    #...name ----------------------------------------------------------------------------
    #mHead_jnt.doName()
    #mHead_jnt.rename(_l_namesToUse[-1])
    for k,v in list(_l_namesToUse[-1].items()):
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
            for k,v in list(_l_namesToUse[0].items()):
                mNeck_jnt.doStore(k,v)
            mNeck_jnt.doName()
        else:
            log.debug("|{0}| >> Multiple neck joint...".format(_str_func))
            
            _d = self.atBlockUtils('skeleton_getCreateDict', self.neckJoints +1)
            
            mOrientHelper = ml_prerigHandles[0].orientHelper
            
            ml_joints = JOINT.build_chain(_d['positions'][:-1], parent=True, worldUpAxis= mOrientHelper.getAxisVector('z-'))
            
            for i,mJnt in enumerate(ml_joints):
                #mJnt.rename(_l_namesToUse[i])
                for k,v in list(_l_namesToUse[i].items()):
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

d_preferredAngles = {}#In terms of aim up out for orientation relative values, stored left, if right, it will invert
d_rotateOrders = {}

#Rig build stuff goes through the rig build factory ------------------------------------------------------
#@cgmGEN.Timer
def rig_prechecks(self):
    _str_func = 'rig_prechecks'
    log.debug(cgmGEN.logString_start(_str_func))

    mBlock = self.mBlock

    if mBlock.lipMidSealSetup and (mBlock.numJointsLipLwr <= 3 or mBlock.numJointsLipUpr <= 3):
        self.l_precheckErrors.append("Need more than 3 lip joints for midSeal")
    
    str_faceType = mBlock.getEnumValueString('faceType')
    if str_faceType not in ['default']:
        self.l_precheckErrors.append("faceType setup not completed: {0}".format(str_faceType))

    str_jawLwrSetup = mBlock.getEnumValueString('jawLwrSetup')
    if str_jawLwrSetup not in ['none','simple']:
        self.l_precheckErrors.append("Jaw setup not completed: {0}".format(str_jawLwrSetup))
    
    str_muzzleSetup = mBlock.getEnumValueString('muzzleSetup')
    if str_muzzleSetup not in ['none','simple','joint','dag']:
        self.l_precheckErrors.append("Muzzle setup not completed: {0}".format(str_muzzleSetup))
        
    str_noseSetup = mBlock.getEnumValueString('noseSetup')
    if str_noseSetup not in ['none','simple']:
        self.l_precheckErrors.append("Nose setup not completed: {0}".format(str_noseSetup))
        
    str_nostrilSetup = mBlock.getEnumValueString('nostrilSetup')
    if str_nostrilSetup not in ['none','default']:
        self.l_precheckErrors.append("Nostril setup not completed: {0}".format(str_nostrilSetup))
        
    str_cheekSetup = mBlock.getEnumValueString('cheekSetup')
    if str_cheekSetup not in ['none','single']:
        self.l_precheckErrors.append("Cheek setup not completed: {0}".format(str_cheekSetup))
        
    str_cheekUprSetup = mBlock.getEnumValueString('cheekUprSetup')
    if str_cheekUprSetup not in ['none','single','lineSimple']:
        self.l_precheckErrors.append("Cheek upr setup not completed: {0}".format(str_cheekUprSetup)) 
        
    str_smileSetup = mBlock.getEnumValueString('smileSetup')
    if str_smileSetup not in ['none','single','lineSimple']:
        self.l_precheckErrors.append("Smilesetup not completed: {0}".format(str_smileSetup))   
            
    str_lipSetup = mBlock.getEnumValueString('lipSetup')
    if str_lipSetup not in ['none','default']:
        self.l_precheckErrors.append("Lip setup not completed: {0}".format(str_lipSetup))
        
    str_chinSetup = mBlock.getEnumValueString('chinSetup')
    if str_chinSetup not in ['none','single']:
        self.l_precheckErrors.append("Chin setup not completed: {0}".format(str_chinSetup))
                

#@cgmGEN.Timer
def rig_dataBuffer(self):
    _short = self.d_block['shortName']
    _str_func = 'rig_dataBuffer'
    log.debug("|{0}| >>  ".format(_str_func)+ '-'*80)
    log.debug("{0}".format(self))
    
    mBlock = self.mBlock
    mModule = self.mModule
    mRigNull = self.mRigNull
    mPrerigNull = mBlock.prerigNull
    self.mPrerigNull = mPrerigNull
    ml_handleJoints = mPrerigNull.msgList_get('handleJoints')
    mMasterNull = self.d_module['mMasterNull']

    
    self.b_scaleSetup = mBlock.scaleSetup
    
    
    for k in ['muzzle','nose','nostril','cheek','bridge',
              'teethUpr','teethLwr',
              'chin','sneer','cheekUpr','jawLwr','jawUpr',
              'lip','lipSeal','teeth','tongue','smile']:
        _tag = "{0}Setup".format(k)
        self.__dict__['str_{0}'.format(_tag)] = False
        _v = mBlock.getEnumValueString(_tag)
        if _v != 'none':
            self.__dict__['str_{0}'.format(_tag)] = _v
        log.debug("|{0}| >> self.str_{1} = {2}".format(_str_func,_tag,self.__dict__['str_{0}'.format(_tag)]))    
    
    
    for k in ['buildSDK','lipMidFollowSetup']:
        self.__dict__['str_{0}'.format(k)] = ATTR.get_enumValueString(mBlock.mNode,k)    
        self.__dict__['v_{0}'.format(k)] = mBlock.getMayaAttr(k)    
    
    #DynParents =============================================================================
    self.UTILS.get_dynParentTargetsDat(self)
    log.debug(cgmGEN._str_subLine)
    
    #Offset ============================================================================ 
    self.v_offset = self.mPuppet.atUtils('get_shapeOffset')
    log.debug("|{0}| >> self.v_offset: {1}".format(_str_func,self.v_offset))    
    log.debug(cgmGEN._str_subLine)
    
    #Size =======================================================================================
    self.v_baseSize = [mBlock.blockScale * v for v in mBlock.baseSize]
    self.f_sizeAvg = MATH.average(self.v_baseSize)
    
    log.debug("|{0}| >> size | self.v_baseSize: {1} | self.f_sizeAvg: {2}".format(_str_func,
                                                                                  self.v_baseSize,
                                                                                  self.f_sizeAvg ))
    
    #Settings =============================================================================
    mModuleParent =  self.d_module['mModuleParent']
    if mModuleParent:
        mSettings = mModuleParent.rigNull.settings
    else:
        log.debug("|{0}| >>  using puppet...".format(_str_func))
        mSettings = self.d_module['mMasterControl'].controlVis

    log.debug("|{0}| >> mSettings | self.mSettings: {1}".format(_str_func,mSettings))
    self.mSettings = mSettings
    
    log.debug("|{0}| >> self.mPlug_visSub_moduleParent: {1}".format(_str_func,
                                                                    self.mPlug_visSub_moduleParent))
    log.debug("|{0}| >> self.mPlug_visDirect_moduleParent: {1}".format(_str_func,
                                                                       self.mPlug_visDirect_moduleParent))

    #rotateOrder =============================================================================
    _str_orientation = self.d_orientation['str']
    _l_orient = [_str_orientation[0],_str_orientation[1],_str_orientation[2]]
    self.ro_base = "{0}{1}{2}".format(_str_orientation[1],_str_orientation[2],_str_orientation[0])
    """
    self.ro_head = "{2}{0}{1}".format(_str_orientation[0],_str_orientation[1],_str_orientation[2])
    self.ro_headLookAt = "{0}{2}{1}".format(_str_orientation[0],_str_orientation[1],_str_orientation[2])
    log.debug("|{0}| >> rotateOrder | self.ro_base: {1}".format(_str_func,self.ro_base))
    log.debug("|{0}| >> rotateOrder | self.ro_head: {1}".format(_str_func,self.ro_head))
    log.debug("|{0}| >> rotateOrder | self.ro_headLookAt: {1}".format(_str_func,self.ro_headLookAt))"""
    log.debug(cgmGEN._str_subLine)

    return True


#@cgmGEN.Timer
def rig_skeleton(self):
    _short = self.d_block['shortName']
    
    _str_func = 'rig_skeleton'
    log.debug("|{0}| >>  ".format(_str_func)+ '-'*80)
    log.debug("{0}".format(self))
        
    mBlock = self.mBlock
    mRigNull = self.mRigNull
    mPrerigNull = self.mPrerigNull
    
    ml_jointsToConnect = []
    ml_jointsToHide = []
    ml_joints = mRigNull.msgList_get('moduleJoints')
    self.d_joints['ml_moduleJoints'] = ml_joints
    
    #---------------------------------------------

    BLOCKUTILS.skeleton_pushSettings(ml_joints, self.d_orientation['str'],
                                     self.d_module['mirrorDirection'])
                                     #d_rotateOrders, d_preferredAngles)
    
    
    #Rig Joints =================================================================================
    ml_rigJoints = BLOCKUTILS.skeleton_buildDuplicateChain(mBlock,
                                                           ml_joints,
                                                           'rig',
                                                           self.mRigNull,
                                                           'rigJoints',
                                                           'rig',
                                                           cgmType = False,
                                                           blockNames=False)
    ml_driverJoints = BLOCKUTILS.skeleton_buildDuplicateChain(mBlock,
                                                              ml_joints,
                                                              None,
                                                              self.mRigNull,
                                                              'driverJoints',
                                                              'driver',
                                                              cgmType = 'driver',
                                                              blockNames=False)    
    
    for i,mJnt in enumerate(ml_rigJoints):
        mJnt.p_parent = ml_driverJoints[i]
    
    ml_jointsToHide.extend(ml_driverJoints)
    """
    ml_segmentJoints = BLOCKUTILS.skeleton_buildDuplicateChain(mBlock,ml_joints, None,
                                                               mRigNull,'segmentJoints','seg',
                                                               cgmType = 'segJnt')
    ml_jointsToHide.extend(ml_segmentJoints)        """
    
    
    
    
    #Processing  joints ================================================================================
    log.debug("|{0}| >> Processing Joints...".format(_str_func)+ '-'*40)
    
    #Need to sort our joint lists:
    md_skinJoints = {}
    md_rigJoints = {}
    md_segJoints = {}
    md_driverJoints = {}
    md_handles = {}
    md_handleShapes = {}
    md_directShapes = {}
    md_directJoints = {}
    self.md_lines = {
    }
    def doSingleJoint(tag,mParent = None):
        log.debug("|{0}| >> gathering {1}...".format(_str_func,tag))            
        mJntSkin = mPrerigNull.getMessageAsMeta('{0}Joint'.format(tag))
    
        mJntRig = mJntSkin.getMessageAsMeta('rigJoint')
        mJntDriver = mJntSkin.getMessageAsMeta('driverJoint')
    
        if mParent is not None:
            mJntDriver.p_parent = mParent
    
        md_skinJoints[tag] = mJntSkin
        md_rigJoints[tag] = mJntRig
        md_driverJoints[tag] = mJntDriver
        md_handleShapes[tag] = mPrerigNull.getMessageAsMeta('{0}ShapeHelper'.format(tag))
    
    def mirrorConnect(tag1,tag2):
        md_rigJoints[tag1].doStore('mirrorControl',md_rigJoints[tag2])
        md_rigJoints[tag2].doStore('mirrorControl', md_rigJoints[tag1])
        
        md_driverJoints[tag1].doStore('mirrorControl',md_driverJoints[tag2])
        md_driverJoints[tag2].doStore('mirrorControl', md_driverJoints[tag1])
        
        
    if self.str_muzzleSetup == 'joint':
        doSingleJoint('muzzle')
            
            
    #Jaw ---------------------------------------------------------------
    if self.str_jawLwrSetup:
        log.debug("|{0}| >> jaw...".format(_str_func))
        mJntSkin = mPrerigNull.getMessageAsMeta('jawJoint')
        mJntRig = mJntSkin.getMessageAsMeta('rigJoint')
        mJntDriver = mJntSkin.getMessageAsMeta('driverJoint')
        
        md_skinJoints['jaw'] = mJntSkin
        md_rigJoints['jaw'] = mJntRig
        md_driverJoints['jaw'] = mJntDriver
        
    if self.str_jawUprSetup:
        log.debug("|{0}| >> jawUpr...".format(_str_func))
        mJntSkin = mPrerigNull.getMessageAsMeta('jawUprJoint')
        mJntRig = mJntSkin.getMessageAsMeta('rigJoint')
        mJntDriver = mJntSkin.getMessageAsMeta('driverJoint')
        
        md_skinJoints['jawUpr'] = mJntSkin
        md_rigJoints['jawUpr'] = mJntRig
        md_driverJoints['jawUpr'] = mJntDriver

        md_driverJoints['jawUpr'].p_parent = False
    
        
    if self.str_tongueSetup:
        doSingleJoint('tongue')
        
    if self.str_teethUprSetup:
        doSingleJoint('teethUpr')
    if self.str_teethLwrSetup:
        doSingleJoint('teethLwr')


    if self.str_chinSetup:
        log.debug("|{0}| >> chinSetup...".format(_str_func))
        mJntSkin = mPrerigNull.getMessageAsMeta('chinJoint')
        mJntRig = mJntSkin.getMessageAsMeta('rigJoint')
        mJntDriver = mJntSkin.getMessageAsMeta('driverJoint')
        
        md_skinJoints['chin'] = mJntSkin
        md_rigJoints['chin'] = mJntRig
        md_driverJoints['chin'] = mJntDriver
        
    if self.str_noseSetup:
        log.debug("|{0}| >> nose...".format(_str_func)+'-'*40)
        
        _l =  ['noseBase']
        
        if mBlock.numJointsNoseTip:
            _l.append('noseTip')
        
        if mBlock.numJointsNostril:
            _l.extend(['nostrilLeft','nostrilRight'])
            
        for t in _l:
            mParent = None
            if t == 'noseBase':
                mParent = False
            doSingleJoint(t,mParent)
            
        if mBlock.numJointsNostril:
            mirrorConnect('nostrilLeft','nostrilRight')

    if self.str_cheekSetup:
        log.debug("|{0}| >> cheek...".format(_str_func))
        for t in ['cheekLeft','cheekRight']:
            doSingleJoint(t,False)
            
        mirrorConnect('cheekLeft','cheekRight')
    
    if self.str_cheekUprSetup:
        log.debug("|{0}| >> cheekUpr...".format(_str_func))
        
        if self.str_cheekUprSetup == 'single':
            for t in ['cheekUprLeft','cheekUprRight']:
                doSingleJoint(t,False)
            mirrorConnect('cheekUprLeft','cheekUprRight')
            
        elif  self.str_cheekUprSetup == 'lineSimple':
            self.md_lines['cheekUpr'] = {'left':[],
                                      'right':[]}
            _found = True
            i = 0
            while _found == True:
                l_tags = []
                for side in ['left','right']:
                    _tag = 'cheekUpr'+side.capitalize()+ "_{0}".format(i)
                    if mPrerigNull.getMessageAsMeta('{0}Joint'.format(_tag)):
                        l_tags.append(_tag)
                        self.md_lines['cheekUpr'][side].append(_tag)
                        
                if l_tags:
                    doSingleJoint(l_tags[0],False)
                    doSingleJoint(l_tags[1],False)                    
                    mirrorConnect(l_tags[0],l_tags[1])
                else:
                    _found = False                    
                    break
                i+=1
    
    
    if self.str_sneerSetup:
        log.debug("|{0}| >> sneer...".format(_str_func))
        for t in ['sneerLeft','sneerRight']:
            doSingleJoint(t,False)
            
        mirrorConnect('sneerLeft','sneerRight')
        
    if self.str_smileSetup:
        log.debug("|{0}| >> smile...".format(_str_func))
        
        if self.str_cheekUprSetup == 'single':
        
            for t in ['smileLeft','smileRight']:
                doSingleJoint(t,False)
            mirrorConnect('smileLeft','smileRight')  
        
        
        elif  self.str_cheekUprSetup == 'lineSimple':
            self.md_lines['smile'] = {'left':[],
                                      'right':[]}
            _found = True
            i = 0
            while _found == True:
                l_tags = []
                for side in ['left','right']:
                    _tag = 'smile'+side.capitalize()+ "_{0}".format(i)
                    if mPrerigNull.getMessageAsMeta('{0}Joint'.format(_tag)):
                        l_tags.append(_tag)
                        self.md_lines['smile'][side].append(_tag)
                        
                if l_tags:
                    doSingleJoint(l_tags[0],False)
                    doSingleJoint(l_tags[1],False)                    
                    mirrorConnect(l_tags[0],l_tags[1])
                else:
                    _found = False                    
                    break
                i+=1        
                

    #Processing  Handles ================================================================================
    log.debug("|{0}| >> Processing...".format(_str_func)+ '-'*40)
    if self.str_lipSetup:
        log.debug("|{0}| >>  lip ".format(_str_func)+ '-'*20)
        
        for d in 'upr','lwr':
            log.debug("|{0}| >>  lip {1}...".format(_str_func,d)+ '-'*5)
            _k = 'lip'+d.capitalize()
            
            md_directShapes[_k] = {}
            md_directJoints[_k] = {}
            
            for _d in md_skinJoints,md_handles,md_handleShapes,md_rigJoints,md_segJoints:
                if not _d.get(_k):
                    _d[_k] = {}

            for side in ['right','center','left']:
                #key = 'lip'+d.capitalize()+side.capitalize()
                key = d+'Lip'+STR.capFirst(side)
                
                md_directShapes[_k][side] = mPrerigNull.msgList_get('{0}JointShapes'.format(key))
                
                ml_skin = mPrerigNull.msgList_get('{0}Joints'.format(key))
                ml_rig = []
                ml_driver = []
                
                for mJnt in ml_skin:
                    mRigJoint = mJnt.getMessageAsMeta('rigJoint')
                    ml_rig.append(mRigJoint)
                
                    mDriver = mJnt.getMessageAsMeta('driverJoint')
                    ml_driver.append(mDriver)
                    mDriver.p_parent = False
                    mRigJoint.doStore('driverJoint',mDriver)
                    mRigJoint.p_parent = mDriver
                
                md_rigJoints[_k][side] = ml_rig
                md_skinJoints[_k][side] = ml_skin
                md_segJoints[_k][side] = ml_driver
                md_directJoints[_k][side] = ml_rig
                
                mHandles = mPrerigNull.msgList_get('{0}PrerigHandles'.format(key))
                mHelpers = mPrerigNull.msgList_get('{0}PrerigShapes'.format(key))
                
                ml = []
                for ii,mHandle in enumerate(mHandles):
                    mJnt = create_jointFromHandle(mHandle,False,'handle')
                    ml.append(mJnt)
                    
                    if d == 'upr' and side in ['right','left'] and ii == 0:
                        log.debug("|{0}| >>  influenceJoints for {1}...".format(_str_func,mHandle))
                        for k in 'upr','lwr':
                            mSub = create_jointFromHandle(mHandle,False,'{0}Influence'.format(k))
                            mSub.doStore('mClass','cgmObject')
                            mSub.p_parent = mJnt
                            mJnt.doStore('{0}Influence'.format(k),mSub)
                            ml_jointsToConnect.append(mSub)
                            ml_jointsToHide.append(mSub)                
                

                ml_jointsToHide.extend(ml)
                md_handles[_k][side] = ml
                md_handleShapes[_k][side] = mHelpers
                
            for i,mObj in enumerate(md_directJoints[_k]['right']):
                mObj.doStore('mirrorControl',md_directJoints[_k]['left'][i])
                md_directJoints[_k]['left'][i].doStore('mirrorControl', mObj)
            
            for i,mObj in enumerate(md_handles[_k]['right']):
                mObj.doStore('mirrorControl',md_handles[_k]['left'][i])
                md_handles[_k]['left'][i].doStore('mirrorControl', mObj)
            
                
            
            log.debug(cgmGEN._str_subLine)
                

    self.md_rigJoints = md_rigJoints
    self.md_skinJoints = md_skinJoints
    self.md_segJoints = md_segJoints
    self.md_handles = md_handles
    self.md_handleShapes = md_handleShapes
    self.md_driverJoints = md_driverJoints
    self.md_directShapes = md_directShapes
    self.md_directJoints = md_directJoints
    
    #...joint hide -----------------------------------------------------------------------------------
    for mJnt in ml_jointsToHide:
        try:mJnt.drawStyle =2
        except:mJnt.radius = .00001
    
    #pprint.pprint(vars())
    #...connect... 
    self.fnc_connect_toRigGutsVis( ml_jointsToConnect )        
    return

#@cgmGEN.Timer
def rig_shapes(self):
    try:
        _short = self.d_block['shortName']
        _str_func = 'rig_shapes'
        log.debug("|{0}| >>  ".format(_str_func)+ '-'*80)
        log.debug("{0}".format(self))
        
    
        mBlock = self.mBlock
        #_baseNameAttrs = ATTR.datList_getAttrs(mBlock.mNode,'nameList')    
        mHandleFactory = mBlock.asHandleFactory()
        mRigNull = self.mRigNull
        mPrerigNull = self.mPrerigNull
        
        ml_rigJoints = mRigNull.msgList_get('rigJoints')
        
        
        if self.md_rigJoints.get('jaw'):
            log.debug("|{0}| >> Jaw setup...".format(_str_func)+ '-'*40)
            mJaw_fk = self.md_driverJoints.get('jaw')
            CORERIG.shapeParent_in_place(mJaw_fk.mNode, mPrerigNull.getMessageAsMeta('jawShapeHelper').mNode)
            
            mRigNull.doStore('controlJaw',mJaw_fk)
            
            #if not self.mParentSettings:
            #    log.debug("|{0}| >> Jaw settings!...".format(_str_func))                
            mRigNull.doStore('settings',mJaw_fk)
            #else:
            #    mRigNull.doStore('settings',self.mParentSettings)
            log.debug(cgmGEN._str_subLine)
            
        mJawUpr = False
        if self.md_rigJoints.get('jawUpr'):
            log.debug("|{0}| >> Jaw Upr setup...".format(_str_func)+ '-'*40)
            mJawUpr_fk = self.md_driverJoints.get('jawUpr')
            CORERIG.shapeParent_in_place(mJawUpr_fk.mNode, mPrerigNull.getMessageAsMeta('jawUprShapeHelper').mNode)
            
            mRigNull.doStore('controlJawUpr',mJawUpr_fk)
            log.debug(cgmGEN._str_subLine)
                
        for k in 'teethUpr','teethLwr','tongue','chin':
            mDag = self.md_driverJoints.get(k)
            if mDag:
                log.debug("|{0}| >> {1} setup...".format(_str_func,k)+ '-'*40)                
                mShapeHelper = mPrerigNull.getMessageAsMeta('{0}ShapeHelper'.format(k))
                CORERIG.shapeParent_in_place(mDag.mNode, mShapeHelper.mNode)
                
                mRigNull.doStore('control{0}'.format(STR.capFirst(k)),mDag)
                log.debug(cgmGEN._str_subLine)
            
            
        """
        if self.md_rigJoints.get('chin'):
            log.debug("|{0}| >> chin setup...".format(_str_func)+ '-'*40)
            mChin = self.md_driverJoints.get('chin')
            CORERIG.shapeParent_in_place(mChin.mNode, mPrerigNull.getMessageAsMeta('chinShapeHelper').mNode)
            
            mRigNull.doStore('controlChin',mChin)
            log.debug(cgmGEN._str_subLine)"""
                
        if self.str_muzzleSetup:
            log.debug("|{0}| >> Muzzle setup...".format(_str_func)+ '-'*40)
            mMuzzleDagHelper = mPrerigNull.getMessageAsMeta('muzzleDagHelper')
            if self.md_driverJoints.get('muzzle'):
                mMuzzleDag = self.md_driverJoints.get('muzzle')
            
            else:
                mMuzzleDag = mMuzzleDagHelper.doCreateAt()
                mMuzzleDag.doCopyNameTagsFromObject(mMuzzleDagHelper.mNode,'cgmType')
                mMuzzleDag.doName()
            
            CORERIG.shapeParent_in_place(mMuzzleDag.mNode,
                                         mMuzzleDagHelper.getMessageAsMeta('shapeHelper').mNode)
            
            mRigNull.doStore('controlMuzzle',mMuzzleDag)
            log.debug(cgmGEN._str_subLine)
            
        if self.str_cheekSetup:
            log.debug("|{0}| >> cheek setup...".format(_str_func)+ '-'*40)
            for k in ['cheekLeft','cheekRight']:
                mDriver = self.md_driverJoints.get(k)
                CORERIG.shapeParent_in_place(mDriver.mNode, self.md_handleShapes[k].mNode)
            log.debug(cgmGEN._str_subLine)
            
        if self.str_cheekUprSetup:
            log.debug("|{0}| >> cheek upr setup...".format(_str_func)+ '-'*40)
            
            if  self.str_cheekUprSetup == 'single':
            
                for k in ['cheekUprLeft','cheekUprRight']:
                    mDriver = self.md_driverJoints.get(k)
                    CORERIG.shapeParent_in_place(mDriver.mNode, self.md_handleShapes[k].mNode)
            elif  self.str_cheekUprSetup == 'lineSimple':
                for side in 'left','right':
                    for t in self.md_lines['cheekUpr'][side]:
                        mDriver = self.md_driverJoints.get(t)
                        CORERIG.shapeParent_in_place(mDriver.mNode, self.md_handleShapes[t].mNode)                        

                
                
                
            log.debug(cgmGEN._str_subLine)
            
        if self.str_smileSetup:
            log.debug("|{0}| >> smile setup...".format(_str_func)+ '-'*40)
            if  self.str_smileSetup == 'single':
                for k in ['smileLeft','smileRight']:
                    mDriver = self.md_driverJoints.get(k)
                    CORERIG.shapeParent_in_place(mDriver.mNode, self.md_handleShapes[k].mNode)
            elif  self.str_smileSetup == 'lineSimple':
                for side in 'left','right':
                    for t in self.md_lines['smile'][side]:
                        mDriver = self.md_driverJoints.get(t)
                        CORERIG.shapeParent_in_place(mDriver.mNode, self.md_handleShapes[t].mNode)            
                
                
            log.debug(cgmGEN._str_subLine)        
                
        if self.str_sneerSetup:
            log.debug("|{0}| >> sneer setup...".format(_str_func)+ '-'*40)
            for k in ['sneerLeft','sneerRight']:
                mDriver = self.md_driverJoints.get(k)
                CORERIG.shapeParent_in_place(mDriver.mNode, self.md_handleShapes[k].mNode)
            log.debug(cgmGEN._str_subLine)
                
        if self.str_noseSetup:
            log.debug("|{0}| >> nose setup...".format(_str_func)+ '-'*40)
            
            _l = ['noseBase']
            
            if mBlock.numJointsNoseTip:
                _l.append('noseTip')
            if mBlock.numJointsNostril:
                _l.extend(['nostrilLeft','nostrilRight'])

            for k in _l:
                mDriver = self.md_driverJoints.get(k)
                if mDriver:
                    log.debug("|{0}| >> found: {1}".format(_str_func,k))
                    CORERIG.shapeParent_in_place(mDriver.mNode, self.md_handleShapes[k].mNode)
            log.debug(cgmGEN._str_subLine)
                    
        
        if self.str_lipSetup:
            log.debug("|{0}| >> Lip setup...".format(_str_func)+ '-'*40)
            mDagHelper = mPrerigNull.getMessageAsMeta('mouthMoveDag')
            mMouthMove = mDagHelper.doCreateAt()
            mMouthMove.doCopyNameTagsFromObject(mDagHelper.mNode,'cgmType')
            mMouthMove.doName()
        
            CORERIG.shapeParent_in_place(mMouthMove.mNode,
                                         mDagHelper.getMessageAsMeta('shapeHelper').mNode)
        
            mRigNull.doStore('controlMouth',mMouthMove)            
            
            #Handles ================================================================================
            log.debug("|{0}| >> Handles...".format(_str_func)+ '-'*80)
            for k in 'lipLwr','lipUpr':
                log.debug("|{0}| >> {1}...".format(_str_func,k)+ '-'*40)
                for side,ml in list(self.md_handles[k].items()):
                    log.debug("|{0}| >> {1}...".format(_str_func,side)+ '-'*10)
                    for i,mHandle in enumerate(ml):
                        log.debug("|{0}| >> {1}...".format(_str_func,mHandle))
                        CORERIG.shapeParent_in_place(mHandle.mNode,
                                                     self.md_handleShapes[k][side][i].mNode)
        
                        #if side == 'center':
                            #mHandleFactory.color(mHandle.mNode,side='center',controlType='sub')
            log.debug(cgmGEN._str_subLine)
        
        
        #Direct ================================================================================
        log.debug("|{0}| >> Direct...".format(_str_func)+ '-'*80)
        
        #Lip direct shapes
        ml_processed = []
        
        for k,d in list(self.md_directJoints.items()):
            log.debug("|{0}| >> {1}...".format(_str_func,k)+ '-'*40)
            for side,ml in list(d.items()):
                log.debug("|{0}| >> {1}...".format(_str_func,side)+ '-'*10)
                for i,mHandle in enumerate(ml):
                    log.debug("|{0}| >> {1}...".format(_str_func,mHandle))
                    CORERIG.shapeParent_in_place(mHandle.mNode,
                                                 self.md_directShapes[k][side][i].mNode)
                    ml_processed.append(mHandle)
        
        
        
        _radius = mBlock.jointRadius
        for k,d in list(self.md_rigJoints.items()):
            log.debug("|{0}| >> {1}...".format(_str_func,k)+ '-'*40)
            
            if VALID.isListArg(d):
                for i,mHandle in enumerate(d):
                    if mHandle in ml_processed:continue
                    else:ml_processed.append(mHandle)
                    log.debug("|{0}| >> {1}...".format(_str_func,mHandle))
                    side = mHandle.getMayaAttr('cgmDirection') or False
                    crv = CURVES.create_fromName(name='cube',
                                                 direction = 'z+',
                                                 size = _radius)
                    SNAP.go(crv,mHandle.mNode)
                    mHandleFactory.color(crv,side=side,controlType='sub')
                    CORERIG.shapeParent_in_place(mHandle.mNode,
                                                 crv,keepSource=False)                
            elif issubclass(type(d),dict):
                for side,ml in list(d.items()):
                    log.debug("|{0}| >> {1}...".format(_str_func,side)+ '-'*10)
                    for i,mHandle in enumerate(ml):
                        if mHandle in ml_processed:continue
                        else:ml_processed.append(mHandle)                        
                        log.debug("|{0}| >> {1}...".format(_str_func,mHandle))
                        crv = CURVES.create_fromName(name='cube',
                                                     direction = 'z+',
                                                     size = _radius)
                        SNAP.go(crv,mHandle.mNode)
                        mHandleFactory.color(crv,side=side,controlType='sub')
                        CORERIG.shapeParent_in_place(mHandle.mNode,
                                                     crv,keepSource=False)
            else:
                log.debug("|{0}| >> {1}...".format(_str_func,d))
                side = d.getMayaAttr('cgmDirection') or 'center'                
                crv = CURVES.create_fromName(name='cube',
                                             direction = 'z+',
                                             size = _radius)
                SNAP.go(crv,d.mNode)
                mHandleFactory.color(crv,side=side,controlType='sub')
                CORERIG.shapeParent_in_place(d.mNode,
                                             crv,keepSource=False)                
                    
        log.debug(cgmGEN._str_subLine)
                    
        for mJnt in ml_rigJoints:
            try:
                mJnt.drawStyle =2
            except:
                mJnt.radius = .00001                
        return
    except Exception as error:
        cgmGEN.cgmExceptCB(Exception,error,msg=vars())


#@cgmGEN.Timer
def rig_controls(self):
    try:
        _short = self.d_block['shortName']
        _str_func = 'rig_controls'
        log.debug("|{0}| >>  ".format(_str_func)+ '-'*80)
        log.debug("{0}".format(self))
      
        mRigNull = self.mRigNull
        mBlock = self.mBlock
        ml_controlsAll = []#we'll append to this list and connect them all at the end
        mRootParent = self.mDeformNull
        ml_segmentHandles = []
        ml_rigJoints = mRigNull.msgList_get('rigJoints')
        mSettings = self.mSettings
        
        if not mSettings:
            raise ValueError("Should have settings")
        
        #mPlug_visSub = self.atBuilderUtils('build_visSub')
        mPlug_visDirect = self.mPlug_visDirect_moduleParent
        mPlug_visSub = self.mPlug_visSub_moduleParent
        self.atBuilderUtils('build_visModuleProxy')#...proxyVis wiring
        
        self.mDeformNull.overrideEnabled = 1
        ATTR.connect(self.mPlug_visModule.p_combinedShortName,
                     "{0}.overrideVisibility".format(self.mDeformNull.mNode))        
        
        b_sdk=False
        if self.str_buildSDK in ['dag']:
            b_sdk = True        
        
        def simpleRegister(mObj):
            _dir = mObj.getMayaAttr('cgmDirection')
            if not _dir:
                _dir = self.d_module['mirrorDirection']
            else:
                if _dir in ['left','right']:
                    _dir = STR.capFirst(_dir)
                else:
                    _dir = 'Centre'
                
            _d = MODULECONTROL.register(mObj,
                                        addSDKGroup=b_sdk,
                                        mirrorSide= _dir,
                                        mirrorAxis="translateX,rotateY,rotateZ",
                                        makeAimable = False)
            ml_controlsAll.append(_d['mObj'])            
            return _d['mObj']
        
        for k in 'teethUpr','teethLwr','tongue','jaw','jawUpr','muzzle','mouth','chin':
            link = 'control{0}'.format(STR.capFirst(k))
            log.debug("|{0}| >> {1} setup...".format(_str_func,link)+ '-'*40)
            mLink = mRigNull.getMessageAsMeta(link)
            if mLink:
                log.debug("|{0}| >> {1}...".format(_str_func,link))
                
                
                _d = MODULECONTROL.register(mLink,
                                            addSDKGroup=b_sdk,                                    
                                            mirrorSide= self.d_module['mirrorDirection'],
                                            mirrorAxis="translateX,rotateY,rotateZ",
                                            makeAimable = False)
                
                ml_controlsAll.append(_d['mObj'])
                        
                        
            log.debug(cgmGEN._str_subLine)        
        """
        for link in ['controlJaw','controlMuzzle','controlMouth','controlChin']:
            mLink = mRigNull.getMessageAsMeta(link)
            if mLink:
                log.debug("|{0}| >> {1}...".format(_str_func,link))
                
                _d = MODULECONTROL.register(mLink,
                                            mirrorSide= self.d_module['mirrorDirection'],
                                            mirrorAxis="translateX,rotateY,rotateZ",
                                            makeAimable = False)
                
                ml_controlsAll.append(_d['mObj']) """       
                #ml_segmentHandles.append(_d['mObj'])
        log.debug(cgmGEN._str_subLine)
        
        if self.str_cheekSetup:
            log.debug("|{0}| >> cheek setup...".format(_str_func)+ '-'*40)
            for k in ['cheekLeft','cheekRight']:
                log.debug("|{0}| >> {1}...".format(_str_func,k))
                simpleRegister(self.md_driverJoints.get(k))
                
        if self.str_cheekUprSetup:
            log.debug("|{0}| >> cheek upr setup...".format(_str_func)+ '-'*40)
            if  self.str_cheekUprSetup == 'single':
                for k in ['cheekUprLeft','cheekUprRight']:
                    log.debug("|{0}| >> {1}...".format(_str_func,k))
                    simpleRegister(self.md_driverJoints.get(k))
            elif  self.str_cheekUprSetup == 'lineSimple':
                for side in 'left','right':
                    for k in self.md_lines['cheekUpr'][side]:
                        simpleRegister(self.md_driverJoints.get(k))                    
                        
        if self.str_sneerSetup:
            log.debug("|{0}| >> sneer setup...".format(_str_func)+ '-'*40)
            for k in ['sneerLeft','sneerRight']:
                log.debug("|{0}| >> {1}...".format(_str_func,k))
                simpleRegister(self.md_driverJoints.get(k))
                
        if self.str_smileSetup:
            log.debug("|{0}| >> smile setup...".format(_str_func)+ '-'*40)
            if  self.str_smileSetup == 'single':
                for k in ['smileLeft','smileRight']:
                    log.debug("|{0}| >> {1}...".format(_str_func,k))
                    simpleRegister(self.md_driverJoints.get(k))
                
            elif  self.str_smileSetup == 'lineSimple':
                for side in 'left','right':
                    for k in self.md_lines['smile'][side]:
                        simpleRegister(self.md_driverJoints.get(k))

        if self.str_noseSetup:
            log.debug("|{0}| >> nose setup...".format(_str_func)+ '-'*40)
            
            _l = ['noseBase']
            if mBlock.numJointsNoseTip:
                _l.append('noseTip')
            if mBlock.numJointsNostril:
                _l.extend(['nostrilLeft','nostrilRight'])
            
            for k in _l:
                log.debug("|{0}| >> {1}...".format(_str_func,k))
                simpleRegister(self.md_driverJoints.get(k))

        
        #Handles ================================================================================
        log.debug("|{0}| >> Handles...".format(_str_func)+ '-'*80)
        for k,d in list(self.md_handles.items()):
            log.debug("|{0}| >> {1}...".format(_str_func,k)+ '-'*40)
            for side,ml in list(d.items()):
                log.debug("|{0}| >> {1}...".format(_str_func,side)+ '-'*10)
                for i,mHandle in enumerate(ml):
                    log.debug("|{0}| >> {1}...".format(_str_func,mHandle))
                    _d = MODULECONTROL.register(mHandle,
                                                addSDKGroup=b_sdk,
                                                mirrorSide= side,
                                                mirrorAxis="translateX,rotateY,rotateZ",
                                                makeAimable = False)
                    
                    ml_controlsAll.append(_d['mObj'])
                    ml_segmentHandles.append(_d['mObj'])
                    
                    if side == 'right':
                        mTarget = d['left'][i]
                        log.debug("|{0}| >> mirrorControl connect | {1} <<>> {2}".format(_str_func, mHandle.mNode, mTarget.mNode))
                        mHandle.doStore('mirrorControl',mTarget)
                        mTarget.doStore('mirrorControl',mHandle)
                        
                        
        log.debug(cgmGEN._str_subLine)

        #Direct ================================================================================
        log.debug("|{0}| >> Direct...".format(_str_func)+ '-'*80)
        for mHandle in ml_rigJoints:
            log.debug("|{0}| >> {1}...".format(_str_func,mHandle))
            side = mHandle.getMayaAttr('cgmDirection') or 'center'
            
            _d = MODULECONTROL.register(mHandle,
                                        typeModifier='direct',
                                        mirrorSide= side,
                                        mirrorAxis="translateX,rotateY,rotateZ",
                                        makeAimable = False)
        
            mObj = _d['mObj']
        
            ml_controlsAll.append(_d['mObj'])
        
            if mObj.hasAttr('cgmIterator'):
                ATTR.set_hidden(mObj.mNode,'cgmIterator',True)        
            for mShape in mObj.getShapes(asMeta=True):
                ATTR.connect(mPlug_visDirect.p_combinedShortName, "{0}.overrideVisibility".format(mShape.mNode))

        log.debug(cgmGEN._str_subLine)


        #Close out...
        mHandleFactory = mBlock.asHandleFactory()
        for mCtrl in ml_controlsAll:
            ATTR.set(mCtrl.mNode,'rotateOrder',self.ro_base)
            
            if mCtrl.hasAttr('radius'):
                ATTR.set(mCtrl.mNode,'radius',0)        
                ATTR.set_hidden(mCtrl.mNode,'radius',True)        
            
            ml_pivots = mCtrl.msgList_get('spacePivots')
            if ml_pivots:
                log.debug("|{0}| >> Coloring spacePivots for: {1}".format(_str_func,mCtrl))
                for mPivot in ml_pivots:
                    mHandleFactory.color(mPivot.mNode, controlType = 'sub')            
        """
        if mHeadIK:
            ATTR.set(mHeadIK.mNode,'rotateOrder',self.ro_head)
        if mHeadLookAt:
            ATTR.set(mHeadLookAt.mNode,'rotateOrder',self.ro_headLookAt)
            """
        
        mRigNull.msgList_connect('handleJoints',ml_segmentHandles)
        mRigNull.msgList_connect('controlsFace',ml_controlsAll)
        mRigNull.msgList_connect('controlsAll',ml_controlsAll,'rigNull')
        mRigNull.moduleSet.extend(ml_controlsAll)
        mRigNull.faceSet.extend(ml_controlsAll)
        
    except Exception as error:
        cgmGEN.cgmExceptCB(Exception,error,msg=vars())


#@cgmGEN.Timer
def rig_frame(self):
    try:
            
        _short = self.d_block['shortName']
        _str_func = ' rig_rigFrame'
        
        log.debug("|{0}| >>  ".format(_str_func)+ '-'*80)
        log.debug("{0}".format(self))    
    
        mBlock = self.mBlock
        mRigNull = self.mRigNull
        mRootParent = self.mDeformNull
        mModule = self.mModule
        mDeformNull = self.mDeformNull
        mFollowParent = self.mDeformNull
        mFollowParentUpr = self.mDeformNull
        mJawSpaceMouth = False
        mFollowBase = self.mDeformNull
        
        mdD = self.md_driverJoints
        #Process our main controls ==============================================================
        mMuzzle = mRigNull.getMessageAsMeta('controlMuzzle')
        mJaw = mRigNull.getMessageAsMeta('controlJaw')
        mJawUpr = mRigNull.getMessageAsMeta('controlJawUpr')
        
        _str_rigNull = mRigNull.mNode
        
        
        if mMuzzle:
            log.debug("|{0}| >> Muzzle setup...".format(_str_func))
            mMuzzle.masterGroup.p_parent = self.mDeformNull
            
            mFollowParent = mMuzzle
            mFollowParentUpr = mMuzzle
            mFollowBase = mMuzzle.doCreateAt('null',setClass=True)
            mFollowBase.rename('{0}_followBase'.format(self.d_module['partName']))
            mFollowBase.p_parent = self.mDeformNull
            
        if mJawUpr:
            log.debug("|{0}| >> Jaw upr setup...".format(_str_func))
            mJawUpr.masterGroup.p_parent = mFollowParent
            if not mMuzzle:
                mFollowParentUpr = mJawUpr            
        if mJaw:
            log.debug("|{0}| >> Jaw setup...".format(_str_func))
            mJaw.masterGroup.p_parent = mFollowParent
            if not mMuzzle:
                mFollowParent = mJaw
                
        mUprTeeth = mRigNull.getMessageAsMeta('controlTeethUpr')
        if mUprTeeth:
            log.debug("|{0}| >> uprTeeth setup...".format(_str_func))
            mUprTeeth.masterGroup.p_parent = mFollowParentUpr
        
        mTongue = mRigNull.getMessageAsMeta('controlTongue')
        if mTongue:
            log.debug("|{0}| >> tongue setup...".format(_str_func))
            mTongue.masterGroup.p_parent = mJaw
            

        if self.str_lipSetup:
            log.debug("|{0}| >> lip setup...".format(_str_func)+ '-'*40)
            
            log.debug("|{0}| >> mouth move...".format(_str_func))
            mMouth = mRigNull.getMessageAsMeta('controlMouth')
            log.debug("|{0}| >> mMouth: {1}".format(_str_func,mMouth))
            mMouth.masterGroup.p_parent = mFollowParent
            _str_mouth = mMouth.mNode
            
            if mJaw and not mJawUpr:
                mJawSpaceMouth = mMouth.doCreateAt(setClass=1)
                mJawSpaceMouth.p_parent = mJaw 
                mJawSpaceMouth.rename('{0}_mouthJawSpace'.format(self.d_module['partName']))
                mJawSpaceMouth.doGroup(True,asMeta=True,typeModifier = 'zero')
                _str_mouthJawSpace = mJawSpaceMouth.mNode
                
                #Wire our jaw space mouth move
                for a in 'translate','rotate','scale':
                    ATTR.connect("{0}.{1}".format(_str_mouth,a), "{0}.{1}".format(_str_mouthJawSpace,a))
                    #mMouth.doConnectOut(a,mJawSpaceMouth.mNode)
            
            #Lip handles ------------------------------------------------------
            log.debug("|{0}| >> lip handles...".format(_str_func)+ '-'*20)
            
            log.debug("|{0}| >> sort handles".format(_str_func)+ '-'*20)
            mLeftCorner = self.md_handles['lipUpr']['left'][0]
            mRightCorner = self.md_handles['lipUpr']['right'][0]
            mUprCenter = self.md_handles['lipUpr']['center'][0]
            mLwrCenter = self.md_handles['lipLwr']['center'][0]
            
            ml_uprLeft = self.md_handles['lipUpr']['left'][1:]
            ml_lwrLeft = self.md_handles['lipLwr']['left']
            
            for ml in ml_uprLeft,ml_lwrLeft:
                ml.reverse()
            
            ml_uprLip = self.md_handles['lipUpr']['right'][1:] + ml_uprLeft#self.md_handles['lipUpr']['left'][1:]
            ml_lwrLip = self.md_handles['lipLwr']['right'] + ml_lwrLeft#self.md_handles['lipLwr']['left']
            ml_uprChain = self.md_handles['lipUpr']['right'][1:] + [mUprCenter] + ml_uprLeft#self.md_handles['lipUpr']['left'][1:]
            ml_lwrChain = self.md_handles['lipLwr']['right'] + [mLwrCenter] + ml_lwrLeft#self.md_handles['lipLwr']['left']
            
            
                
            for mHandle in mLeftCorner,mRightCorner:
                log.debug("|{0}| >> lip handles | {1}".format(_str_func,mHandle))
                if mHandle == mLeftCorner:
                    str_side = 'left'
                else:
                    str_side = 'right'
                    
                if mJaw:
                    mHandle.masterGroup.p_parent = mFollowBase
                    
                    mMainTrack = mHandle.doCreateAt(setClass=1)
                    mMainTrack.doStore('cgmName',mHandle)
                    mMainTrack.doStore('cgmType','mainTrack')
                    mMainTrack.doName()
                    mMainTrack.p_parent = mJawUpr or mFollowParent
                    
                    
                    mJawTrack = mHandle.doCreateAt(setClass=1)
                    mJawTrack.doStore('cgmName',mHandle)
                    mJawTrack.doStore('cgmType','jawTrack')
                    mJawTrack.doName()
                    if mJawUpr:
                        mJawTrack.p_parent = mJaw                        
                    else:
                        mJawTrack.p_parent = mJawSpaceMouth
                    
                    const = mc.pointConstraint([mMainTrack.mNode,mJawTrack.mNode],
                                        mHandle.masterGroup.mNode,
                                        maintainOffset=True)[0]


                    #Create Reverse Nodes
                    d_blendReturn = NODEFACTORY.createSingleBlendNetwork([mHandle.mNode,#mJaw.mNode,
                                                                          "cornerPin"],#'cornerPin_{0}'.format(str_side,mHandle)],
                                                                         [mMainTrack.mNode,'cornerPin_Left'],
                                                                         [mMainTrack.mNode,'cornerPin_Right'],
                                                                         keyable=True)

                    targetWeights = mc.pointConstraint(const,q=True,
                                                        weightAliasList=True,
                                                        maintainOffset=True)

                    #Connetct output of switch attribute to input of W1 of pointConstraint
                    d_blendReturn['d_result1']['mi_plug'].doConnectOut('%s.%s' % (const,targetWeights[0]))
                    d_blendReturn['d_result2']['mi_plug'].doConnectOut('%s.%s' % (const,targetWeights[1]))
                    d_blendReturn['d_result1']['mi_plug'].p_hidden = True
                    d_blendReturn['d_result2']['mi_plug'].p_hidden = True

                    #Set a deafult value of 0.5 so that the corners are weighted evenly
                    ATTR.set_default(mHandle.mNode, 'cornerPin', 0.5)

                    mHandle.setMayaAttr('cornerPin', .5)

                    
                else:
                    mHandle.masterGroup.p_parent = mMouth
            
            #Adding an attribute of Open Jaw to the jaw controller.
            #Benn Garnish added for his SDK setup
            #cgmMeta.cgmAttr(mJaw, 'OpenJaw', attrType='float', min = 0, max = 1,defaultValue = 0,keyable = True,lock=False,hidden=False)
                      
                
            
            if mJaw:
                if mJawSpaceMouth:
                    mLwrCenter.masterGroup.p_parent = mJawSpaceMouth
                else:
                    mLwrCenter.masterGroup.p_parent = mJaw
                    
            else:
                mLwrCenter.masterGroup.p_parent = mMouth
            
            if mJawUpr:
                mUprCenter.masterGroup.p_parent = mFollowParentUpr
            else:
                mUprCenter.masterGroup.p_parent = mMouth
                
            
            #side handles ---------------------------
            
            if self.str_lipMidFollowSetup in ['ribbon']:
                #First we're going to attach our handles to a surface to ge general placement. Then we're going to try
                d_lipSetup = {'upr':{'ml_chain':[mRightCorner] + ml_uprChain + [mLeftCorner],
                                       'mInfluences':[mRightCorner.uprInfluence,mUprCenter,mLeftCorner.uprInfluence],
                                       'mHandles':ml_uprLip},
                              'lwr':{'ml_chain':[mRightCorner] + ml_lwrChain + [mLeftCorner],
                                       'mInfluences':[mRightCorner.lwrInfluence,mLwrCenter,mLeftCorner.lwrInfluence],
                                       'mHandles':ml_lwrLip}}
                
                for k,d in list(d_lipSetup.items()):
                    #need our handle chain to make a ribbon
                    ml_chain = d['ml_chain']
                    mInfluences = d['mInfluences']
                    l_surfaceReturn = IK.ribbon_createSurface([mJnt.mNode for mJnt in ml_chain],
                                                    'z+')
                    mControlSurface = cgmMeta.validateObjArg( l_surfaceReturn[0],'cgmObject',setClass = True )
                    mControlSurface.addAttr('cgmName',"{0}HandlesFollow_lip".format(k),attrType='string',lock=True)    
                    mControlSurface.addAttr('cgmType','controlSurface',attrType='string',lock=True)
                    mControlSurface.doName()
                    mControlSurface.p_parent = _str_rigNull
                    
                    
                    log.debug("|{0}| >> Skinning surface: {1}".format(_str_func,mControlSurface))
                    mSkinCluster = cgmMeta.validateObjArg(mc.skinCluster ([mObj.mNode for mObj in mInfluences],
                                                                          mControlSurface.mNode,
                                                                          tsb=True,nurbsSamples=4,
                                                                          maximumInfluences = 3,
                                                                          normalizeWeights = 1,dropoffRate=10.0),
                                                          'cgmNode',
                                                          setClass=True)
                
                    mSkinCluster.doStore('cgmName', mControlSurface)
                    mSkinCluster.doName()
    
                    for mHandle in d['mHandles']:
                        mHandle.masterGroup.p_parent = mFollowParent
                        _resAttach = RIGCONSTRAINT.attach_toShape(mHandle.masterGroup.mNode,
                                                                  mControlSurface.mNode,
                                                                  'conParent')
                        TRANS.parent_set(_resAttach[0],_str_rigNull)
                        
                        
                    
                    for mObj in [mControlSurface]:
                        mObj.overrideEnabled = 1
                        cgmMeta.cgmAttr(_str_rigNull,'gutsVis',lock=False).doConnectOut("%s.%s"%(mObj.mNode,'overrideVisibility'))
                        cgmMeta.cgmAttr(_str_rigNull,'gutsLock',lock=False).doConnectOut("%s.%s"%(mObj.mNode,'overrideDisplayType'))    
                        mObj.parent = mRigNull
            elif self.str_lipMidFollowSetup == 'parent':
                d_lipSetup = {'upr':{'left':self.md_handles['lipUpr']['left'][1:],
                                     'right':self.md_handles['lipUpr']['right'][1:],
                                     'parent':mFollowParentUpr},
                              
                              
                              'lwr':{'left':self.md_handles['lipLwr']['left'],
                                     'right':self.md_handles['lipLwr']['right'],
                                     'parent':mFollowParent}}
                
                for k,d in list(d_lipSetup.items()):
                    #need our handle chain to make a ribbon
                    ml_left = d['left']
                    ml_right = d['right']
                    
                    for mHandle in ml_left:
                        mHandle.masterGroup.p_parent = d['parent']                        
                    for mHandle in ml_right:
                        mHandle.masterGroup.p_parent = d['parent']                        
                
            else:
                #...parentConstraint....
                d_lipSetup = {'upr':{'left':self.md_handles['lipUpr']['left'][1:],
                                     'right':self.md_handles['lipUpr']['right'][1:],
                                    'mInfluences':[mRightCorner.uprInfluence,mUprCenter,mLeftCorner.uprInfluence]},
                              
                              'lwr':{'left':self.md_handles['lipLwr']['left'],
                                     'mInfluences':[mRightCorner.lwrInfluence,mLwrCenter,mLeftCorner.lwrInfluence],                                         
                                     'right':self.md_handles['lipLwr']['right']}}

                for k,d in list(d_lipSetup.items()):
                    #need our handle chain to make a ribbon
                    pprint.pprint(d)
                    ml_left = d['left']
                    ml_right = d['right']
                    mInfluences = d['mInfluences']
                    
                    for mHandle in ml_left:
                        mHandle.masterGroup.p_parent = mFollowParent                        
                        mc.parentConstraint([mObj.mNode for mObj in mInfluences[1:]],
                                            mHandle.masterGroup.mNode,
                                            maintainOffset = True, weight = 1)
                    for mHandle in ml_right:
                        mHandle.masterGroup.p_parent = mFollowParent                        
                        mc.parentConstraint([mObj.mNode for mObj in mInfluences[:2]],
                                            mHandle.masterGroup.mNode,
                                            maintainOffset = True, weight = 1)
                                                
                 
                        
                    

                #Lip Aim setup...
                ml_lwrLeft = self.md_handles['lipLwr']['left']
                ml_lwrRight = self.md_handles['lipLwr']['right']
                d_lipAim = {'upr':{'left':self.md_handles['lipUpr']['left'][1:],
                                   'right':self.md_handles['lipUpr']['right'][1:]},
                            'lwr':{'left':self.md_handles['lipLwr']['left'],
                                   'right':self.md_handles['lipLwr']['right']}}
                
                for tag,sectionDat in list(d_lipAim.items()):
                    for side,sideDat in list(sectionDat.items()):

                        if side == 'left':
                            _aim = [-1,0,0]
                            _corner = mLeftCorner.mNode
                        else:
                            _aim = [1,0,0]
                            _corner = mRightCorner.mNode
                            
                        for i,mJnt in enumerate(sideDat):
                            _mode = None
                            
                            if not i:
                                _tar = _corner
                            else:
                                _tar=sideDat[i-1].mNode
                                
                            mAimGroup = mJnt.doGroup(True,True,
                                                     asMeta=True,
                                                     typeModifier = 'aim',
                                                     setClass='cgmObject')

                            mc.aimConstraint(_tar,
                                             mAimGroup.mNode,
                                             maintainOffset = True, weight = 1,
                                             aimVector = _aim,
                                             upVector = [0,1,0],
                                             worldUpVector = [0,1,0],
                                             worldUpObject = mJnt.masterGroup.mNode,
                                             worldUpType = 'objectRotation' )
                    
            
            
            #Lip Corner influences ------------------------------------------------------
            log.debug("|{0}| >> lip corner influences...".format(_str_func)+ '-'*20)
            for i,mHandle in enumerate([mRightCorner,mLeftCorner]):
                mPlug_upr = cgmMeta.cgmAttr(mHandle,'twistUpper',value = 0,
                                              attrType='float',defaultValue = 0.0,keyable = True,hidden = False)
                mPlug_lwr = cgmMeta.cgmAttr(mHandle,'twistLower',value = 0,
                                              attrType='float',defaultValue = 0.0,keyable = True,hidden = False)
                
                if not i:
                    _aim = [-1,0,0]
                else:
                    _aim = [1,0,0]
                    
                mUprInfluence = mHandle.uprInfluence
                mLwrInfluence = mHandle.lwrInfluence
                
                for ii,mInfl in enumerate([mUprInfluence,mLwrInfluence]):
                    if self.str_lipMidFollowSetup == 'parent':
                        if not ii:
                            if not i:#Right
                                _tar = ml_uprChain[0].mNode
                            else:#Left
                                _tar = ml_uprChain[-1].mNode
                        else:
                            if not i:#Right
                                _tar = ml_lwrChain[0].mNode
                            else:#Left
                                _tar = ml_lwrChain[-1].mNode                        
                    else:
                        if not ii:
                            _tar = mUprCenter.mNode
                        else:
                            _tar = mLwrCenter.mNode            
                        
                    mAimGroup = mInfl.doGroup(True,True,
                                             asMeta=True,
                                             typeModifier = 'aim',
                                             setClass='cgmObject')
                    mc.aimConstraint(_tar,
                                     mAimGroup.mNode,
                                     maintainOffset = True, weight = 1,
                                     aimVector = _aim,
                                     upVector = [0,0,1],
                                     worldUpVector = [0,0,1],
                                     worldUpObject = mHandle.mNode,
                                     worldUpType = 'objectRotation' )                    
                    
                
                
                
                if not i:# ['right']:# and k not in ['inner','outer']:
                    mPlug_upr.doConnectOut("{0}.rz".format(mHandle.uprInfluence.mNode))                 
                    mPlug_lwr.doConnectOut("{0}.rz".format(mHandle.lwrInfluence.mNode))                 
                else:  
                    str_arg1 = "{0}.rz = -{1}".format(mHandle.uprInfluence.mNode,
                                                      mPlug_upr.p_combinedShortName)                
                    str_arg2 = "{0}.rz = -{1}".format(mHandle.lwrInfluence.mNode,
                                                     mPlug_lwr.p_combinedShortName)
                    for a in str_arg1,str_arg2:
                        NODEFACTORY.argsToNodes(a).doBuild()
                    
    
        if self.str_cheekSetup:
            log.debug("|{0}| >> cheek setup...".format(_str_func)+ '-'*40)
            _kws_attr = {'hidden':False, 'lock':False}
            mPlug_jawRXPos = cgmMeta.cgmAttr(mJaw.mNode,
                                             "cheek_rxPos",attrType = 'float',
                                             value = 30,
                                             defaultValue=30,minValue= 0,
                                             **_kws_attr)
            mPlug_jawTYPos = cgmMeta.cgmAttr(mJaw.mNode,
                                             "cheek_tyPos",attrType = 'float',
                                             value = 1.0,
                                             defaultValue=1.0,minValue= 0,
                                             **_kws_attr)
            mPlug_jawTYNeg = cgmMeta.cgmAttr(mJaw.mNode,
                                             "cheek_tyNeg",attrType = 'float',
                                             value = 3.0,
                                             defaultValue=3.0,
                                             **_kws_attr)
            
            
            mRemap_jawRX_pos = cgmMeta.cgmNode(name = "jawRX_pos_remap", nodeType = 'remapValue')
            #mRemap_jawRX_neg = cgmMeta.cgmNode(name = "jawRX_neg_remap", nodeType = 'remapValue')
            
            mRemap_jawTY_pos = cgmMeta.cgmNode(name = "jawTY_pos_remap", nodeType = 'remapValue')
            mRemap_jawTY_neg = cgmMeta.cgmNode(name = "jawTY_neg_remap", nodeType = 'remapValue')            
            
            mRemap_jawRX_pos.doConnectIn('inputValue',"{0}.rx".format(mJaw.mNode))
            #mRemap_jawRX_neg.doConnectIn('inputValue',"{0}.rx".format(mJaw.mNode))
            
            mRemap_jawTY_pos.doConnectIn('inputValue',"{0}.ty".format(mJaw.mNode))
            #mRemap_jawTY_neg.doConnectIn('inputValue',"{0}.ty".format(mJaw.mNode))            
            
            
            mRemap_jawRX_pos.doConnectIn('inputMax',mPlug_jawRXPos.p_combinedShortName)
            
            
            mRemap_jawTY_pos.doConnectIn('inputMax',mPlug_jawTYPos.p_combinedShortName)
            mRemap_jawTY_neg.doConnectIn('inputMax',mPlug_jawTYNeg.p_combinedShortName)
            #mRemap_jawTY_neg.inputMax = 0
            
            #"%s.condResult = if %s.ty == 3:5 else 1
            l_argBuild = []
            mPlug_jawTYNegInv = cgmMeta.cgmAttr(mJaw.mNode,
                                                "jaw_tyNegInverse",attrType = 'float',
                                                **_kws_attr)
            
            l_argBuild.append("{0} = -{1}.ty".format(mPlug_jawTYNegInv.p_combinedName,
                                                     mJaw.mNode))
            
            l_argBuild.append("{0}.inputValue = if {1}.ty < 0:{2} else 0".format(mRemap_jawTY_neg.mNode,
                                                                                 mJaw.mNode,
                                                                                 mPlug_jawTYNegInv.p_combinedName))
            
            

            for arg in l_argBuild:
                log.debug("|{0}| >> Building arg: {1}".format(_str_func,arg))
                NODEFACTORY.argsToNodes(arg).doBuild()              
            
            """
            mRemap_jawRX_neg.inputMin = -180
            mRemap_jawRX_neg.outputMax = -180
            
            mRemap_jawRX_neg.inputMin = -180
            mRemap_jawRX_neg.outputMax = -180"""
            
            
            for k in ['cheekLeft','cheekRight']:
                log.debug("|{0}| >> {1}...".format(_str_func,k))
                mHandle = mdD[k]
                mdD[k].masterGroup.p_parent = self.mDeformNull
                
                mc.parentConstraint([mFollowParent.mNode, mJaw.mNode],
                                    mdD[k].masterGroup.mNode,maintainOffset=True)
                
                mOffsetGroup = mdD[k].doGroup(True,asMeta=True,typeModifier = 'offset')
                
                #offsetAmount, offsetThreshold
                
                
                mHandle.addAttr('offsetOut',value = 1.0, attrType='float',visible=True)
                mHandle.addAttr('offsetIn',value = -.5, attrType='float',visible=True)
                
                l_outDrivers = []
                l_inDrivers = []
                
                for mRemap in mRemap_jawTY_neg,mRemap_jawRX_pos:
                    l_inDrivers.append("{0}.outValue".format(mRemap.mNode))
                    
                for mRemap in [mRemap_jawTY_pos]:
                    l_outDrivers.append("{0}.outValue".format(mRemap.mNode))
                    
                    
                #Make our side rotate push...
                
                
                #Wire up... -------------------------------------------------------------
                
                mPlug_resOut = cgmMeta.cgmAttr(mHandle.mNode,
                                               "res_Out",attrType = 'float',
                                               lock=True)
                mPlug_resIn = cgmMeta.cgmAttr(mHandle.mNode,
                                               "res_In",attrType = 'float',
                                               lock=True)
                mPlug_blendOut = cgmMeta.cgmAttr(mHandle.mNode,
                                                 "blend_Out",attrType = 'float',
                                                 lock=True)
                mPlug_blendIn = cgmMeta.cgmAttr(mHandle.mNode,
                                                 "blend_In",attrType = 'float',
                                                 lock=True)
                mPlug_resBlend = cgmMeta.cgmAttr(mHandle.mNode,
                                                 "res_blend",attrType = 'float',
                                                 lock=True)                
                
                l_argBuild = []
                #distance by master
                
                l_argBuild.append("{0} = {1}".format(mPlug_blendOut.p_combinedName,
                                                     ' + '.join(l_outDrivers)))
                l_argBuild.append("{0} = {1} * {2}".format(mPlug_resOut.p_combinedName,
                                                           mPlug_blendOut.p_combinedName,
                                                           '{0}.offsetOut'.format(mHandle.mNode)))
                
                l_argBuild.append("{0} = {1}".format(mPlug_blendIn.p_combinedName,
                                                     ' + '.join(l_inDrivers)))
                l_argBuild.append("{0} = {1} * {2}".format(mPlug_resIn.p_combinedName,
                                                           mPlug_blendIn.p_combinedName,
                                                           '{0}.offsetIn'.format(mHandle.mNode)))
                
                
                
                l_argBuild.append("{0} = {1} + {2}".format(mPlug_resBlend.p_combinedName,
                                                           mPlug_resOut.p_combinedName,
                                                           mPlug_resIn.p_combinedName))
                
                

                for arg in l_argBuild:
                    log.debug("|{0}| >> Building arg: {1}".format(_str_func,arg))
                    NODEFACTORY.argsToNodes(arg).doBuild()                
                    
                mOffsetGroup.doConnectIn('tz',mPlug_resBlend.p_combinedShortName)

                
                """
                #Offset sdks ------------------------
                inTangent='linear'
                outTangent='linear'
                
                mc.setDrivenKeyframe("{0}.tz".format(mOffsetGroup.mNode),
                                     currentDriver = "{0}.rx".format(mJaw.mNode),
                                     itt=inTangent,ott=outTangent,
                                     driverValue = 0,value = 0.0)
                mc.setDrivenKeyframe("{0}.tz".format(mOffsetGroup.mNode),
                                     currentDriver = "{0}.rz".format(mJaw.mNode),
                                     itt=inTangent,ott=outTangent,
                                     driverValue = 0,value = 0.0)            
                mc.setDrivenKeyframe("{0}.tz".format(mOffsetGroup.mNode),
                                     currentDriver = "{0}.ty".format(mJaw.mNode),
                                     itt=inTangent,ott=outTangent,
                                     driverValue = 0,value = 0.0)
                
                mc.setDrivenKeyframe("{0}.tz".format(mOffsetGroup.mNode),
                                     currentDriver = "{0}.tx".format(mJaw.mNode),
                                     itt=inTangent,ott=outTangent,
                                     driverValue = 0,value = 0.0)            
                
                mc.setDrivenKeyframe("{0}.tz".format(mOffsetGroup.mNode),
                                     currentDriver = "{0}.rx".format(mJaw.mNode),
                                     itt=inTangent,ott=outTangent,
                                     driverValue = 30,value = -1)
                mc.setDrivenKeyframe("{0}.tz".format(mOffsetGroup.mNode),
                                     currentDriver = "{0}.ty".format(mJaw.mNode),
                                     itt=inTangent,ott=outTangent,
                                     driverValue = -4,value = -1)
                mc.setDrivenKeyframe("{0}.tz".format(mOffsetGroup.mNode),
                                     currentDriver = "{0}.ty".format(mJaw.mNode),
                                     itt=inTangent,ott=outTangent,
                                     driverValue = 3,value = 1)
                
                if k == 'cheekLeft':
                    mc.setDrivenKeyframe("{0}.tz".format(mOffsetGroup.mNode),
                                         currentDriver = "{0}.rz".format(mJaw.mNode),
                                         itt=inTangent,ott=outTangent,
                                         driverValue = 20,value = 1)
                else:
                    mc.setDrivenKeyframe("{0}.tz".format(mOffsetGroup.mNode),
                                         currentDriver = "{0}.rz".format(mJaw.mNode),
                                         itt=inTangent,ott=outTangent,
                                         driverValue = -20,value = 1)"""                
        
        if self.str_sneerSetup:
            log.debug("|{0}| >> sneer setup...".format(_str_func)+ '-'*40)
            
            for k in ['sneerLeft','sneerRight']:
                log.debug("|{0}| >> {1}...".format(_str_func,k))
                mdD[k].masterGroup.p_parent = mJawUpr or self.mDeformNull
                
                mTrack = mdD[k].masterGroup.doCreateAt(setClass=1)
                mTrack.p_parent = mFollowParent
                mTrack.rename("{0}_baseTrack".format(mdD[k].p_nameBase))
                _c = mc.parentConstraint([mFollowBase.mNode, mTrack.mNode],
                                    mdD[k].masterGroup.mNode,maintainOffset=True)[0]
                
                targetWeights = mc.parentConstraint(_c,q=True,
                                                    weightAliasList=True,
                                                    maintainOffset=True)
                ATTR.set(_c,targetWeights[0],.8)
                ATTR.set(_c,targetWeights[1],.2)
                
        if self.str_smileSetup:
            log.debug("|{0}| >> smile setup...".format(_str_func)+ '-'*40)
            
            if self.str_smileSetup == 'single':
            
                for s in ['Left','Right']:
                    #k in ['smileLeft','smileRight']:
                    k = 'smile'+s
                    
                    log.debug("|{0}| >> {1}...".format(_str_func,k))
                    mdD[k].masterGroup.p_parent = self.mDeformNull
                    
                    mTrack = mdD[k].masterGroup.doCreateAt(setClass=1)
                    mTrack.p_parent = mFollowParent
                    mTrack.rename("{0}_baseTrack".format(mdD[k].p_nameBase))
                    
                    l_targets = []
                    l_targets.append(self.md_handles['lipUpr'][s.lower()][0].mNode)
                    
                    for k2 in ['nostril','cheek','noseBase','sneer','cheekUpr']:
                        if k2 not in ['noseBase']:
                            _k2 = k2+s
                        else:
                            _k2 = k2
                            
                        if mdD.get(_k2):
                            l_targets.append(mdD.get(_k2).mNode)
                    _c = mc.pointConstraint(l_targets,
                                            mTrack.mNode,maintainOffset=True)[0]
                    
                    targetWeights = mc.pointConstraint(_c,q=True,
                                                        weightAliasList=True,
                                                        maintainOffset=True)
                    ATTR.set(_c,targetWeights[0],1.25)
                    #ATTR.set(_c,targetWeights[1],.9)
                    
                    mc.parentConstraint(mTrack.mNode,
                                       mdD[k].masterGroup.mNode,maintainOffset=True)
                    
            elif self.str_smileSetup == 'lineSimple':
                for side in 'left','right':
                    
                    l_targets = []
                    l_targets.append(self.md_handles['lipUpr'][side][0].mNode)
                    
                    for k2 in ['nostril','cheek','noseBase','sneer']:
                        if k2 not in ['noseBase']:
                            _k2 = k2 + side.capitalize()
                        else:
                            _k2 = k2
                            
                        if mdD.get(_k2):
                            l_targets.append(mdD.get(_k2).mNode)                    
                    
                    for k in self.md_lines['smile'][side]:
                        mdD[k].masterGroup.p_parent = self.mDeformNull
                        
                        #mTrack = mdD[k].masterGroup.doCreateAt(setClass=1)
                        #mTrack.p_parent = mFollowParent
                        #mTrack.rename("{0}_baseTrack".format(mdD[k].p_nameBase))
                        
                        RIGCONSTRAINT.byDistance(mdD[k].masterGroup,l_targets,mc.parentConstraint, maxUse=4, maintainOffset=1)
                
        if self.str_cheekUprSetup:
            log.debug("|{0}| >> cheekUpr setup...".format(_str_func)+ '-'*40)
            
            if self.str_cheekUprSetup == 'single':
                for k in ['cheekUprLeft','cheekUprRight']:
                    log.debug("|{0}| >> {1}...".format(_str_func,k))
                    mdD[k].masterGroup.p_parent = mJawUpr or self.mDeformNull
                    
                    mTrack = mdD[k].masterGroup.doCreateAt(setClass=1)
                    mTrack.p_parent = mFollowParent
                    
                    _c = mc.parentConstraint([mFollowBase.mNode, mTrack.mNode],
                                        mdD[k].masterGroup.mNode,
                                        maintainOffset=True)[0]
                    
                    targetWeights = mc.parentConstraint(_c,q=True,
                                                        weightAliasList=True,
                                                        maintainOffset=True)
                    ATTR.set(_c,targetWeights[0],.9)
                    ATTR.set(_c,targetWeights[1],.1)
                    
            elif self.str_cheekUprSetup == 'lineSimple':
                for side in 'left','right':
                    
                    l_targets = []
                    
                    for k2 in ['cheek','sneer']:
                        if k2 not in ['noseBase']:
                            _k2 = k2 + side.capitalize()
                        else:
                            _k2 = k2
                            
                        if mdD.get(_k2):
                            l_targets.append(mdD.get(_k2).mNode)                      
                    
                    
                    for k in self.md_lines['cheekUpr'][side]:
                        mdD[k].masterGroup.p_parent = self.mDeformNull
                        #mTrack = mdD[k].masterGroup.doCreateAt(setClass=1)
                        #mTrack.p_parent = mFollowParent
                        """
                        _c = mc.parentConstraint([mFollowBase.mNode, mTrack.mNode],
                                                 mdD[k].masterGroup.mNode,
                                                 maintainOffset=True)[0]
                    
                        targetWeights = mc.parentConstraint(_c,q=True,
                                                            weightAliasList=True,
                                                            maintainOffset=True)
                        ATTR.set(_c,targetWeights[0],.9)
                        ATTR.set(_c,targetWeights[1],.1)"""                        
                        
                        #RIGCONSTRAINT.byDistance(mdD[k],[mFollowBase, mTrack],mc.parentConstraint)
                        RIGCONSTRAINT.byDistance(mdD[k].masterGroup,l_targets,mc.parentConstraint, maxUse=4, maintainOffset=1)
                    
                
        if self.str_noseSetup:
            log.debug("|{0}| >> nose setup...".format(_str_func)+ '-'*40)
            mdD['noseBase'].masterGroup.p_parent = mDeformNull
            
            mdD['noseBase'].addAttr('followMuzzle',value = .9, attrType='float',
                                    minValue = 0, maxValue = 1.0, defaultValue = .9,
                                    keyable = False)
            
            mTrack = mdD['noseBase'].masterGroup.doCreateAt(setClass=1)
            mTrack.p_parent = mFollowParentUpr
            #_c = mc.parentConstraint([mFollowBase.mNode, mTrack.mNode],
                                #mdD['noseBase'].masterGroup.mNode,maintainOffset=True)[0]
            
            #targetWeights = mc.parentConstraint(_c,q=True,
            #                                    weightAliasList=True,
            #                                    maintainOffset=True)
            
            RIGCONSTRAINT.blendChainsBy([mFollowBase.mNode],
                                        [mTrack.mNode],[mdD['noseBase'].masterGroup.mNode],
                                        driver = "{0}.followMuzzle".format(mdD['noseBase'].mNode),
                                        l_constraints=['parent'],maintainOffset=True)
            #ATTR.set(_c,targetWeights[0],.25)
            #ATTR.set(_c,targetWeights[1],.75)
            
            """
            mc.pointConstraint([mFollowBase.mNode, mTrack.mNode],
                                mdD['noseBase'].masterGroup.mNode,maintainOffset=True)
            
            mc.aimConstraint(mFollowBase.mNode, mdD['noseBase'].masterGroup.mNode, maintainOffset = True,
                             aimVector = [0,1,0], upVector = [0,0,1], 
                             worldUpObject = mFollowBase.mNode,
                             worldUpType = 'objectrotation', 
                             worldUpVector = [0,0,1])"""
    
            for k in ['noseBase','noseTip','nostrilLeft','nostrilRight']:
                pass
    
        return
    except Exception as error:
        cgmGEN.cgmExceptCB(Exception,error)


#@cgmGEN.Timer
def rig_lipSegments(self):
    _short = self.d_block['shortName']
    _str_func = ' rig_lipSegments'
    
    log.debug("|{0}| >>  ".format(_str_func)+ '-'*80)
    log.debug("{0}".format(self))    

    mBlock = self.mBlock
    mRigNull = self.mRigNull
    mRootParent = self.mDeformNull
    mModule = self.mModule
    mDeformNull = self.mDeformNull
    mFollowParent = self.mDeformNull
    mFollowBase = self.mDeformNull
    mMouth = mRigNull.getMessageAsMeta('controlMouth')
    log.debug("|{0}| >> mMouth: {1}".format(_str_func,mMouth))
    
    mdD = self.md_driverJoints
    
    
    if not self.str_lipSetup:
        log.debug("|{0}| >> No lip setup...".format(_str_func))
        return False
    
    
    log.debug("|{0}| >> sort influences".format(_str_func))
    mLeftCorner = self.md_handles['lipUpr']['left'][0]
    mRightCorner = self.md_handles['lipUpr']['right'][0]
    mUprCenter = self.md_handles['lipUpr']['center'][0]
    mLwrCenter = self.md_handles['lipLwr']['center'][0]        
    ml_uprLipInfluences = [mRightCorner.uprInfluence] + self.md_handles['lipUpr']['right'][1:] + self.md_handles['lipUpr']['center']+ self.md_handles['lipUpr']['left'][1:] + [mLeftCorner.uprInfluence]
    ml_lwrLipInfluences = [mRightCorner.lwrInfluence] + self.md_handles['lipLwr']['right'] + self.md_handles['lipLwr']['center']+ self.md_handles['lipLwr']['left'] + [mLeftCorner.lwrInfluence]
    
    log.debug("|{0}| >> sort driven".format(_str_func))
    dUpr =  self.md_rigJoints['lipUpr']
    dLwr =  self.md_rigJoints['lipLwr']
    _revUprLeft = copy.copy(dUpr['left'])
    _revLwrLeft = copy.copy(dLwr['left'])
    for l in _revLwrLeft,_revUprLeft:
        l.reverse()
    ml_uprRig = dUpr['right'] + dUpr['center']+ _revUprLeft
    ml_lwrRig = dLwr['right'] + dLwr['center']+ _revLwrLeft

    mMidDag = cgmMeta.cgmObject(name='midSealMarker')
    mMidDag.p_position = DIST.get_average_position([mUprCenter.p_position,
                                                    mLwrCenter.p_position])
    mMidDag.p_parent = mDeformNull
    
    

    
    d_lips = {'driven1':ml_uprRig,
              'driven2':ml_lwrRig,
              'influences1':ml_uprLipInfluences,
              'influences2':ml_lwrLipInfluences,
              'baseName':'lipRibbons',
              'settingsControl':mMouth,
              'baseName1' :"uprLip",
              'baseName2':"lwrLip",
              'extendEnds':False,
              'sealDriver1':mLeftCorner,
              'sealDriver2':mRightCorner,
              'sealDriverMid':mMidDag,#mUprCenter
              'sealSplit':mBlock.lipMidSealSetup,
              'specialMode':'noStartEnd',#'endsToInfluences',
              'crossBlendMult':mBlock.lipSealCrossBlendMult,
              'moduleInstance':mModule,
              'paramaterization':mBlock.getEnumValueString('ribbonParam'),
              'msgDriver':'driverJoint'}    
    
    d_lips['liveSurface'] = False
    #pprint.pprint(d_test)
    cgmGEN._reloadMod(IK)
    #pprint.pprint(d_lips)
       
    IK.ribbon_seal(**d_lips)
    
    mc.parentConstraint(mLeftCorner.mNode, ml_uprRig[-1].masterGroup.mNode, maintainOffset = True)
    mc.parentConstraint(mRightCorner.mNode, ml_uprRig[0].masterGroup.mNode, maintainOffset = True)
    
    for mObj in ml_uprRig + ml_lwrRig:
        mObj.driverJoint.p_parent = mDeformNull
    
    #pprint.pprint([mObj.p_nameShort for mObj in ml_uprRig])
    #pprint.pprint([mObj.p_nameShort for mObj in ml_lwrRig])    
    return 



#@cgmGEN.Timer
def rig_cleanUp(self):
    _short = self.d_block['shortName']
    _str_func = 'rig_cleanUp'
    log.debug("|{0}| >>  ".format(_str_func)+ '-'*80)
    log.debug("{0}".format(self))
    
    mBlock = self.mBlock
    mRigNull = self.mRigNull
    
    mMasterControl= self.d_module['mMasterControl']
    mMasterDeformGroup= self.d_module['mMasterDeformGroup']    
    mMasterNull = self.d_module['mMasterNull']
    mModuleParent = self.d_module['mModuleParent']
    mPlug_globalScale = self.d_module['mPlug_globalScale']
    

    #Settings =================================================================================
    #log.debug("|{0}| >> Settings...".format(_str_func))
    #mSettings.visDirect = 0
    
    #mPlug_FKIK = cgmMeta.cgmAttr(mSettings,'FKIK')
    #mPlug_FKIK.p_defaultValue = 1
    #mPlug_FKIK.value = 1
    
    
    mTongue = mRigNull.getMessageAsMeta('controlTongue')
    mUprTeeth = mRigNull.getMessageAsMeta('controlTeethUpr')
    mMuzzle = mRigNull.getMessageAsMeta('controlMuzzle')
    mJaw = mRigNull.getMessageAsMeta('controlJaw')
    
    if mTongue:
        mChild = mTongue
        #Get space stuff
        ml_targetDynParents = []#self.ml_dynParentsAbove + self.ml_dynEndParents
        
        ml_targetDynParents.append(self.md_dynTargetsParent['world'])
        #ml_targetDynParents.extend(mControlIK.msgList_get('spacePivots',asMeta = True))
        
        if mJaw:
            ml_targetDynParents.insert(0,mJaw)
        
        if mUprTeeth:
            ml_targetDynParents.insert(1,mUprTeeth)
        if mMuzzle:
            ml_targetDynParents.insert(1,mMuzzle)
            
    
        mDynGroup = cgmRIGMETA.cgmDynParentGroup(dynChild=mChild,dynMode=0)
    
        for mTar in ml_targetDynParents:
            mDynGroup.addDynParent(mTar)
        mDynGroup.rebuild()
            
        log.debug("|{0}| >>  IK targets...".format(_str_func))
        #pprint.pprint(ml_targetDynParents)        
        
        log.debug(cgmGEN._str_subLine)        
    
    
        
    #Lock and hide =================================================================================
    ml_controls = mRigNull.msgList_get('controlsAll')
    self.UTILS.controls_lockDown(ml_controls)
    
    if not mBlock.scaleSetup:
        log.debug("|{0}| >> No scale".format(_str_func))
        ml_controlsToLock = copy.copy(ml_controls)
        for mCtrl in ml_controlsToLock:
            ATTR.set_standardFlags(mCtrl.mNode, ['scale'])
    else:
        log.debug("|{0}| >>  scale setup...".format(_str_func))
        
        
    self.mDeformNull.dagLock(True)

    #Close out ===============================================================================================
    mRigNull.version = self.d_block['buildVersion']
    mBlock.blockState = 'rig'
    mBlock.UTILS.set_blockNullFormState(mBlock)
    self.UTILS.rigNodes_store(self)


def create_simpleMesh(self,  deleteHistory = True, cap=True, **kws):
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
        raise ValueError("No rigJoints connected")

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

def build_proxyMesh(self, forceNew = True, puppetMeshMode = False, **kws):
    """
    Build our proxyMesh
    """
    
    _str_func = 'build_proxyMesh'
    log.debug("|{0}| >>  ".format(_str_func)+ '-'*80)
    log.debug("{0}".format(self))
    
     
    mBlock = self
    mModule = self.moduleTarget
    mRigNull = mModule.rigNull
    mDeformNull = mModule.deformNull
    #mSettings = mRigNull.settings
    
    mPuppet = self.atUtils('get_puppet')
    mMaster = mPuppet.masterControl    
    mPuppetSettings = mMaster.controlSettings
    str_partName = mModule.get_partNameBase()
    mPrerigNull = mBlock.prerigNull
    
    _side = BLOCKUTILS.get_side(self)
    

    
    ml_rigJoints = mRigNull.msgList_get('rigJoints',asMeta = True)
    if not ml_rigJoints:
        raise ValueError("No rigJoints connected")
    self.v_baseSize = [mBlock.blockScale * v for v in mBlock.baseSize]
    
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
        
    ml_proxy = []
    ml_curves = []
    
    ml_rigJoints = mRigNull.msgList_get('rigJoints')
    ml_use = []
    for mObj in ml_rigJoints:
        if 'teeth' in mObj.mNode:
            pass
        elif 'tongue' in mObj.mNode:
            pass
        else:
            ml_use.append(mObj)
    ml_rigJoints = ml_use
            
    ml_new = []
    mTeethUpr = mPrerigNull.getMessageAsMeta('teethUprJoint')
    mTeethLwr = mPrerigNull.getMessageAsMeta('teethLwrJoint')
    mTongue = mPrerigNull.getMessageAsMeta('tongueJoint')
    
    if mTeethUpr:
        log.debug("|{0}| >> mTeethUpr".format(_str_func)+'-'*40)
        
    
    #Let's gather our proxy mesh
    for lnk in ['jaw','nose','uprLip','lwrLip','overLip','underLip','noseToCheekLeft','noseToCheekRight',
                'lipToChin','uprJoinLeft','uprJoinRight']:
        mBase = mBlock.getMessageAsMeta(lnk+'FormLoft')
        if mBase:
            log.debug("|{0}| >> On: {1}".format(_str_func,lnk)+'-'*40)
            
            mLoftSurface =  mBase.doDuplicate(po=False,ic=False)
            _surf = mc.nurbsToPoly(mLoftSurface.mNode, mnd=1, f=0,
                                   pt = 1,ch=0, pc=200, chr = .9,
                                   ft=.01, mel = .001, d = .1, ut=1, un = 3,
                                   vt=1, vn=3, uch = 0, cht = .01, ntr = 0, mrt = 0, uss = 1 )
            #mLoftSurface.p_parent=False
            mLoftSurface.delete()
            
            mNew = cgmMeta.asMeta(_surf[0])
            
            ml_new.append(mNew)
            mNew.p_parent = False
            mNew.doStore('cgmName',lnk)
            mNew.doName()            
            ml_use = copy.copy(ml_rigJoints)
            ml_remove = []
            if lnk in ['uprLip','overLip']:
                for mObj in ml_use:
                    #if 'LWR_lip' in mObj.mNode:
                    if 'lwrLip' in mObj.mNode:
                        log.debug("|{0}| >> removing: {1}".format(_str_func,mObj))
                        ml_remove.append(mObj)
                    #if mObj.getMayaAttr('cgmPosition') == 'lwr' and mObj.cgmName == 'lip':
                    #    log.debug("|{0}| >> removing: {1}".format(_str_func,mObj))
                    #    ml_remove.append(mObj)
            if lnk in ['lwrLip','underLip']:
                for mObj in ml_use:
                    if 'uprLip' in mObj.mNode:
                        log.debug("|{0}| >> removing: {1}".format(_str_func,mObj))
                        ml_remove.append(mObj)                    
                    #if 'UPR_lip' in mObj.mNode:                    
                    #if mObj.getMayaAttr('cgmPosition') == 'upr' and mObj.cgmName == 'lip':
                        #ml_remove.append(mObj)
                        #log.debug("|{0}| >> removing: {1}".format(_str_func,mObj))
                        
            for mObj in ml_remove:
                ml_use.remove(mObj)
            log.debug("|{0}| >> Skinning surface: {1}".format(_str_func,mNew))
            mSkinCluster = cgmMeta.validateObjArg(mc.skinCluster ([mObj.mNode for mObj in ml_use],
                                                                  mNew.mNode,
                                                                  tsb=True,
                                                                  maximumInfluences = 3,
                                                                  heatmapFalloff = 1.0,
                                                                  bindMethod = 0,
                                                                  normalizeWeights = 1,dropoffRate=10.0),
                                                  'cgmNode',
                                                  setClass=True)
        
            mSkinCluster.doStore('cgmName', mNew)
            mSkinCluster.doName()
            
            ml_proxy.append(mNew)
            

    for mProxy in ml_proxy:
        CORERIG.colorControl(mProxy.mNode,_side,'main',transparent=False,proxy=True)
        #mc.makeIdentity(mProxy.mNode, apply = True, t=1, r=1,s=1,n=0,pn=1)

        #Vis connect -----------------------------------------------------------------------
        mProxy.overrideEnabled = 1
        ATTR.connect("{0}.proxyVis_out".format(mRigNull.mNode),"{0}.visibility".format(mProxy.mNode) )
        ATTR.connect("{0}.proxyLock".format(mPuppetSettings.mNode),"{0}.overrideDisplayType".format(mProxy.mNode) )
        for mShape in mProxy.getShapes(asMeta=1):
            str_shape = mShape.mNode
            mShape.overrideEnabled = 0
            #ATTR.connect("{0}.proxyVis".format(mPuppetSettings.mNode),"{0}.visibility".format(str_shape) )
            ATTR.connect("{0}.proxyLock".format(mPuppetSettings.mNode),"{0}.overrideDisplayTypes".format(str_shape) )
            
    #if directProxy:
    #    for mObj in ml_rigJoints:
    #        for mShape in mObj.getShapes(asMeta=True):
                #mShape.overrideEnabled = 0
    #            mShape.overrideDisplayType = 0
    #            ATTR.connect("{0}.visDirect".format(_settings), "{0}.overrideVisibility".format(mShape.mNode))
        
    
    mRigNull.msgList_connect('proxyMesh', ml_proxy + ml_curves)



def build_proxyMeshBAK(self, forceNew = True, puppetMeshMode = False):
    """
    Build our proxyMesh
    """
    _short = self.d_block['shortName']
    _str_func = 'build_proxyMesh'
    log.debug("|{0}| >>  ".format(_str_func)+ '-'*80)
    log.debug("{0}".format(self))
    
     
    mBlock = self.mBlock
    mRigNull = self.mRigNull
    m#Settings = mRigNull.settings
    mPuppetSettings = self.d_module['mMasterControl'].controlSettings
    mPrerigNull = mBlock.prerigNull
    #directProxy = mBlock.proxyDirect
    
    _side = BLOCKUTILS.get_side(self.mBlock)
    
    ml_rigJoints = mRigNull.msgList_get('rigJoints',asMeta = True)
    if not ml_rigJoints:
        raise ValueError("No rigJoints connected")
    self.v_baseSize = [mBlock.blockScale * v for v in mBlock.baseSize]
    
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
        
    ml_proxy = []
    ml_curves = []
    
    
    #Jaw -------------
    mJaw = mRigNull.getMessageAsMeta('controlJaw')
    if mJaw:
        log.debug("|{0}| >> jaw...".format(_str_func))
        mLoftSurface =  mBlock.jawFormLoft.doDuplicate(po=False,ic=False)
        #nurbsToPoly -mnd 1  -ch 1 -f 1 -pt 1 -pc 200 -chr 0.9 -ft 0.01 -mel 0.001 -d 0.1 -ut 1 -un 3 -vt 1 -vn 3 -uch 0 -ucr 0 -cht 0.01 -es 0 -ntr 0 -mrt 0 -uss 1 "jaw_fk_anim_Transform";
        _surf = mc.nurbsToPoly(mLoftSurface.mNode, mnd=1, f=1, pt = 1,ch=0, pc=200, chr = .9, ft=.01, mel = .001, d = .1, ut=1, un = 3, vt=1, vn=3, uch = 0, cht = .01, ntr = 0, mrt = 0, uss = 1 )
        mDag = mJaw.doCreateAt()
        CORERIG.shapeParent_in_place(mDag.mNode,_surf,False) 
        ml_proxy.append(mDag)
        #mLoftSurface.p_parent = False
        mDag.p_parent = mJaw
        
    
    ml_drivers = mRigNull.msgList_get('driverJoints')
    for mObj in ml_drivers:
        if mObj.getMayaAttr('cgmName')=='noseBase':
            log.debug("|{0}| >> noseBase...".format(_str_func))
            mLoftSurface =  mBlock.noseFormLoft.doDuplicate(po=False,ic=False)
            _surf = mc.nurbsToPoly(mLoftSurface.mNode, mnd=1, f=1, pt = 1,ch=0, pc=200, chr = .9, ft=.01, mel = .001, d = .1, ut=1, un = 3, vt=1, vn=3, uch = 0, cht = .01, ntr = 0, mrt = 0, uss = 1 )
            mDag = mObj.doCreateAt()
            CORERIG.shapeParent_in_place(mDag.mNode,_surf,False) 
            ml_proxy.append(mDag)
            #mLoftSurface.p_parent = False
            mDag.p_parent = mObj            

    for mProxy in ml_proxy:
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
            
    #if directProxy:
    #    for mObj in ml_rigJoints:
    #        for mShape in mObj.getShapes(asMeta=True):
                #mShape.overrideEnabled = 0
    #            mShape.overrideDisplayType = 0
    #            ATTR.connect("{0}.visDirect".format(_settings), "{0}.overrideVisibility".format(mShape.mNode))
        
    
    mRigNull.msgList_connect('proxyMesh', ml_proxy + ml_curves)


#UI ================================================================================================
def uiFunc_getDefineScaleSpace(self):
    ml_handles = self.msgList_get('defineHandles')
    for mObj in ml_handles:
        if 'Left' in mObj.handleTag:
            ml_handles.remove(mObj)
            
    self.atUtils('get_handleScaleSpace',ml_handles)
    
_handleKey = {'define':'defineSubHandles',
              'form':'formHandles',
              'prerig':'prerigHandles'}

def uiFunc_sealFix(self, ml = None, reset = False):
    if not ml:
        ml = cgmMeta.asMeta(mc.ls(sl=1))
    
    if not ml:
        log.warning("Nothing Selected")
        return False
    md = {}
    for mObj in ml:
        mSeal = mObj.getMessageAsMeta('mTrackSeal')
        mBase = mObj.getMessageAsMeta('mTrackBase')
        
        if not mSeal:
            log.warning("Lacks seal: {0}".format(mObj))
            continue
        
        if reset:
            mSeal.p_position = mBase.p_position
            mSeal.p_orient = mBase.p_orient
            mObj.resetAttrs()
            
            continue
        
        #if reset:
        #    pass
        #else:
        #TRANS.relativePos_get(mBase.mNode,mObj.mNode)
        md[mObj] = {'pos':mObj.p_position,
                    'orient':mObj.p_orient,
                    'mSeal':mSeal}
        mObj.resetAttrs()
        
        
    if reset:
        log.warning("LipSeal Reset.")
        return
    
    for mObj in ml:
        if not md.get(mObj):
            continue
        d = md[mObj]
        mSeal = d['mSeal']
        
        mSeal.p_position = d['pos']
        mSeal.p_orient = d['orient']
        
        #LOC.create(position = d['pos'],name="{0}_sealLoc".format(mObj.p_nameShort))
        
    pprint.pprint(md)
    log.warning("LipSeal Set.")
        


def uiFunc_snapStateHandles(self,ml=None):
    if not ml:
        ml = cgmMeta.asMeta(mc.ls(sl=1))
    
    if not ml:
        log.warning("Nothing Selected")
        return False
    
    _state = self.p_blockState    
    ml_handles = self.msgList_get(_handleKey.get(_state))
    
    for mObj in ml_handles:
        try:mObj.p_position = DIST.get_closest_point(mObj.mNode, ml[0].mNode)[0]
        except Exception as err:
            log.warning("Failed to snap: {0} | {1}".format(mObj.mNode,err))
    
def uiBuilderMenu(self,parent = None):
    #uiMenu = mc.menuItem( parent = parent, l='Head:', subMenu=True)
    _short = self.p_nameShort
    
    mc.menuItem(en=False,divider=True,
                label = "|| Muzzle")
    
    mc.menuItem(ann = '[{0}] Get Define scale space values'.format(_short),
                c = cgmGEN.Callback(uiFunc_getDefineScaleSpace,self),
                label = "Get Define Scale Space Dat")
    
    mc.menuItem(ann = '[{0}] Snap state handles'.format(_short),
                c = cgmGEN.Callback(uiFunc_snapStateHandles,self),
                label = "Snap the state handles to selected")
    

    _sub = mc.menuItem(en=True,subMenu = True,tearOff=True,
                       label = "Seal Fix")
    mc.menuItem(ann = '[{0}] Seal Fix Reset'.format(_short),
                c = cgmGEN.Callback(uiFunc_sealFix,self,reset=False),
                label = "Set")    
    mc.menuItem(ann = '[{0}] Seal Fix Reset'.format(_short),
                c = cgmGEN.Callback(uiFunc_sealFix,self,reset=True),
                label = "Reset")
    
    
    """
    mc.menuItem(en=True,divider = True,
                label = "Utilities")
    _sub = mc.menuItem(en=True,subMenu = True,tearOff=True,
                       label = "State Picker")
    """
    #self.atUtils('uiStatePickerMenu',parent)
    
    return
















