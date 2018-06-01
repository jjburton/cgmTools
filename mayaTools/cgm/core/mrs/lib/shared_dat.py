"""
------------------------------------------
shared_dat: cgm.core.mrs.lib.shared_dat
Author: Josh Burton
email: jjburton@cgmonks.com

Website : http://www.cgmonks.com
------------------------------------------

================================================================
"""
d_defaultAttrs= {'version':'string',#Attributes to be initialzed for any module
                'blockType':'string',
                #'moduleTarget':'messageSimple',
                'baseSize':'float3',
                'cgmName':'string',
                'cgmDirection':'string',
                'cgmPosition':'string',
                'blockState':'string',
                'blockDat':'string',#...for pickle? 
                'blockParent':'messageSimple',
                'blockMirror':'messageSimple'}
d_defaultAttrSettings = {'blockState':'define'}


_l_requiredSkeletonDat = ['__d_controlShapes__','__l_jointAttrs__','__l_buildOrder__']
_l_requiredRigDat = []

_l_blockStates = ['define','template','prerig','skeleton','rig']
_l_requiredModuleDat = ['__version__',
                        'template','is_template','templateDelete',
                        'prerig','is_prerig','prerigDelete',
                        'rig','is_rig','rigDelete']

_l_buildProfiles = 'unityMobile','unityPC','humanIK','feature'

#These are our default attrs to make library. To be called via modules
_d_attrsTo_make = {'side':'none:left:right:center',
                   'position':'none:upper:lower:front:back:top:bottom',
                   'baseUp':'float3',
                   'baseAim':'float3',
                   'basePoint':'float3',
                   'controlOffset':'float',
                   'basicShape':'circle:square:pyramid:semiSphere:sphere:cube',
                   'proxyShape':'cube:sphere:cylinder:cone:torus',
                   'attachPoint':'base:end:closest:surface',
                   'squashStretch':'none:single:double',
                   'addCog':'bool',
                   'addAim':'bool',
                   'addPivot':'bool',
                   'addMotionJoint':'bool',
                   'proxy':'off:lock:on',
                   'addScalePivot':'bool',                   
                   'loftShape':'circle:square:diamond:wideUp:wideDown:widePos:wideNeg',
                   'loftSides':'int',     
                   'loftSplit':'int',
                   'loftDegree':'linear:cubic',
                   'controlType':'main:sub:direct:extra',    
                   'nameList':'stringDatList',
                   'namesHandles':'stringDatList',
                   'namesJoints':'stringDatList',
                   'hasRootJoint':'bool',
                   'hasJoint':'bool',
                   'nameIter':'string',
                   'numControls':'int',
                   'numJoints':'int',
                   'numShapers':'int',
                   'numSpacePivots':'int',
                   'offsetMode':'default:proxyAverage',                   
                   'buildDirect':'bool',
                   'ikSetup':'none:rp:spline:ribbon',
                   'ikBase':'none:cube:simple:hips',
                   'ikEnd':'none:bank:foot:hand:tipBase:tipEnd:tipMid:proxy',                   
                   'buildProfile':'none:unityMobile:unityPC:humanIK:feature',
                   'buildAdditiveScale':'bool',
                   'customStartOrientation':'bool',
                   'offsetMode':'default:proxyAverage',
                   'moduleTarget':'messageSimple',
                   
                   'squashMeasure' : 'none:arcLength:pointDist',
                   'squash' : 'none:simple:single:both',
                   'squashExtraControl' : 'bool',
                   'squashFactorMax':'float',
                   'squashFactorMin':'float',
               
                   'ribbonAim': 'none:stable:stableBlend',
                   #'ribbonConnectBy': 'constraint:matrix',
               
                   'segmentMidIKControl':'bool',
                   
                   
                   'scaleSetup':'bool',
                   'settingsPlace':'start:end',
                   'settingsDirection':'up:down:out:in',
                   'proxyDirect':'bool',
                   'proxyType':'none:castMesh'}

_l_pivotOrder = ['center','back','front','left','right']
_d_pivotBankNames = {'default':{'left':'outer','right':'inner'},
                      'right':{'left':'inner','right':'outer'}}

#>> State Attr Masks =================================================================================
_l_attrMask_all = ['visibility']
_l_attrMask_template = ['baseSize','blockScale']
_l_attrMask_prerig = []
_l_attrMask_rig = []

#>> Modules data =================================================================================
__l_faceModules__ = ['eyebrow','eyelids','eyeball','mouthnose']
__l_moduleJointSingleHooks__ = ['scaleJoint']
__l_moduleJointMsgListHooks__ = ['helperJoints','defHelp_joints']
__l_moduleControlMsgListHooks__ = ['spacePivots']


#>>General ======================================================================================
str_defaultFont = 'arial'

