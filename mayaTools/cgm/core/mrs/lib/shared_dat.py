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

_l_blockStates = ['define','template','prerig','rig']
_l_requiredModuleDat = ['__version__',
                        'template','is_template','templateDelete',
                        'prerig','is_prerig','prerigDelete',
                        'rig','is_rig','rigDelete']

#These are our default attrs to make library. To be called via modules
_d_attrsTo_make = {'side':'none:left:right:center',
                   'position':'none:upper:lower:front:back:top:bottom',
                   'baseUp':'float3',
                   'baseAim':'float3',
                   'basePoint':'float3',                   
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
                   'loftShape':'square:circle:squareRounded:triangle',
                   'loftSides':'int',     
                   'loftSplit':'int',
                   'loftDegree':'linear:cubic',
                   'controlType':'main:sub:direct:extra',    
                   'nameList':'stringDatList',
                   'hasRootJoint':'bool',
                   'hasJoint':'bool',
                   'numberControls':'int',
                   'numberJoints':'int',
                   'buildDirect':'bool',
                   'ikSetup':'none:rp:spline:ribbon',
                   'ikBase':'none:simple',
                   'buildAdditiveScale':'bool',                   
                   'customStartOrientation':'bool',
                   'moduleTarget':'messageSimple',
                   'proxyType':'none:castMesh'}

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

