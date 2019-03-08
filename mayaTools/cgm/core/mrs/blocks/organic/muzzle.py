"""
------------------------------------------
cgm.core.mrs.blocks.organic.lowerFace
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
import Red9.core.Red9_AnimationUtils as r9Anim
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
import cgm.core.rig.general_utils as RIGGEN
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
import cgm.core.lib.nameTools as NAMETOOLS
import cgm.core.cgmPy.validateArgs as VALID
import cgm.core.lib.list_utils as LISTS
import cgm.core.rig.ik_utils as IK
import cgm.core.rig.skin_utils as RIGSKIN

for m in DIST,POS,MATH,IK,CONSTRAINT,LOC,BLOCKUTILS,BUILDERUTILS,CORERIG,RAYS,JOINT,RIGCONSTRAINT,RIGGEN:
    reload(m)
    
# From cgm ==============================================================
from cgm.core import cgm_Meta as cgmMeta

#=============================================================================================================
#>> Block Settings
#=============================================================================================================
__version__ = 'alpha.10.31.2018'
__autoTemplate__ = False
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
d_wiring_template = {'msgLinks':['templateNull','noTransTemplateNull'],
                     }
d_wiring_extraDags = {'msgLinks':['bbHelper'],
                      'msgLists':[]}
#>>>Profiles ==============================================================================================
d_build_profiles = {}


d_block_profiles = {'default':{},
                    'jaw':{'baseSize':[17.6,7.2,8.4],
                           'faceType':'default',
                           'muzzleSetup':'simple',
                           'noseSetup':'none',
                           'jawSetup':'simple',
                           'lipSetup':'none',
                           'teethSetup':'none',
                           'cheekSetup':'none',
                           'tongueSetup':'none',
                           'uprJaw':False,
                           'chinSetup':'none',
                               },
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
                   'baseAim',
                   'baseDat',
                   'attachPoint',
                   'nameList',
                   'loftDegree',
                   'loftSplit',
                   'scaleSetup',
                   'moduleTarget',]

d_attrsToMake = {'faceType':'default:muzzle:beak',
                 'muzzleSetup':'none:simple',
                 'noseSetup':'none:simple',
                 'jawSetup':'none:simple:slide',
                 'lipSetup':'none:default',
                 'teethSetup':'none:oneJoint:twoJoint',
                 'cheekSetup':'none:single',
                 'tongueSetup':'none:single:ribbon',
                 #Jaw...
                 'uprJawSetup':'none:default',
                 'chinSetup':'none:single',
                 #Nose...
                 'nostrilSetup':'none:default',
                 'bridgeSetup':'none:default',
                 'numJointsNostril':'int',
                 'numJointsNoseTip':'int',
                 #Lips...
                 'lipSealSetup':'none:default',
                 'numLipControls':'int',
                 'numJointsLipUpr':'int',
                 'numJointsLipLwr':'int',
                 'paramUprStart':'float',
                 'paramLwrStart':'float',
                 #'lipCorners':'bool',
                 #Tongue...
                 'numJointsTongue':'int',
                 }

d_defaultSettings = {'version':__version__,
                     'attachPoint':'end',
                     'side':'none',
                     'loftDegree':'cubic',
                     'numJointsLipUpr':3,
                     'numLipControls':3,
                     'numJointsLipLwr':3,
                     'numJointsNoseTip':1,
                     'numJointsNostril':1,
                     'paramUprStart':.15,
                     'paramLwrStart':.15,
                     'numJointsTongue':3,
                     #'baseSize':MATH.get_space_value(__dimensions[1]),
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

@cgmGEN.Timer
def define(self):
    _str_func = 'define'    
    log.debug("|{0}| >>  ".format(_str_func)+ '-'*80)
    log.debug("{0}".format(self))
    
    _short = self.mNode
    
    #Attributes =========================================================
    ATTR.set_alias(_short,'sy','blockScale')    
    self.setAttrFlags(attrs=['sx','sz','sz'])
    self.doConnectOut('sy',['sx','sz'])

    ATTR.set_min(_short, 'loftSplit', 1)
    ATTR.set_min(_short, 'paramUprStart', 0.0)
    ATTR.set_min(_short, 'paramLwrStart', 0.0)
    
    
    #Buffer our values...
    _str_faceType = self.getEnumValueString('faceType')
    _str_muzzleSetup = self.getEnumValueString('muzzleSetup')
    _str_noseSetup = self.getEnumValueString('noseSetup')
    _str_uprJawSetup = self.getEnumValueString('uprJawSetup')    
    _str_lipsSetup = self.getEnumValueString('lipsSetup')
    _str_teethSetup = self.getEnumValueString('teethSetup')
    _str_cheekSetup = self.getEnumValueString('cheekSetup')
    _str_tongueSetup = self.getEnumValueString('tongueSetup')
    

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
    
    mNoTransformNull = self.getMessageAsMeta('noTransDefineNull')
    if mNoTransformNull:
        mNoTransformNull.delete()
    
    #rigBlock Handle ===========================================================
    log.debug("|{0}| >>  RigBlock Handle...".format(_str_func))            
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
    _bb_shape = CURVES.create_controlCurve(self.mNode,'cubeOpen', size = 1.0, sizeMode='fixed')
    mBBShape = cgmMeta.validateObjArg(_bb_shape, 'cgmObject',setClass=True)
    mBBShape.p_parent = mDefineNull    
    mBBShape.tz = -.5
    mBBShape.ty = .5
    
    
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
    
    #Jaw ---------------------------------------------------------------------
    if self.jawSetup:
        log.debug("|{0}| >>  Jaw setup...".format(_str_func))
        _str_jawSetup = self.getEnumValueString('jawSetup')
        
        _d_pairs = {'jawLeft':'jawRight',
                    'jawTopLeft':'jawTopRight',
                    'chinLeft':'chinRight',
                    'cheekBoneLeft':'cheekBoneRight',
                    }
        d_pairs.update(_d_pairs)
    
        _d = {'jawLeft':{'color':'blueBright','tagOnly':True,'arrow':False,'jointLabel':True,
                            'vectorLine':False,'scaleSpace':[.85,-.3,-1]},
              'jawRight':{'color':'redBright','tagOnly':True,'arrow':False,'jointLabel':True,
                             'vectorLine':False,'scaleSpace':[-.85,-.3,-1]},
              'jawTopLeft':{'color':'blueBright','tagOnly':True,'arrow':False,'jointLabel':False,
                            #'defaults':{'tx':-1},
                             'vectorLine':False,'scaleSpace':[1,.5,-1]},
              'jawTopRight':{'color':'redBright','tagOnly':True,'arrow':False,'jointLabel':0,
                             #'defaults':{'tx':1},                             
                              'vectorLine':False,'scaleSpace':[-1,.5,-1]},              
              'chinLeft':{'color':'blueBright','tagOnly':True,'arrow':False,'jointLabel':0,'vectorLine':0,
                          'scaleSpace':[.25,-1,.6]},
              'chinRight':{'color':'redBright','tagOnly':True,'arrow':False,'jointLabel':0,'vectorLine':0,
                          'scaleSpace':[-.25,-1,.6]},
              #'chin':{'color':'yellowBright','tagOnly':True,'arrow':False,'jointLabel':1,
              #              'vectorLine':False,'scaleSpace':[0,-1,1]},
              'cheekBoneLeft':{'color':'blueBright','tagOnly':True,'arrow':False,'jointLabel':0,
                               'vectorLine':False,'scaleSpace':[.7,.4,.3]},
              'cheekBoneRight':{'color':'redBright','tagOnly':True,'arrow':False,'jointLabel':0,
                                'vectorLine':False,'scaleSpace':[-.7,.4,.3]},
              }
        
        d_creation.update(_d)
        l_order.extend(['jawLeft','jawRight','chinLeft','chinRight',
                        'jawTopLeft','jawTopRight','cheekBoneLeft','cheekBoneRight'])
        
        _d_curveCreation = {'jawLine':{'keys':['jawTopLeft','jawLeft','chinLeft',
                                               'chinRight','jawRight','jawTopRight'],
                                       'rebuild':False},
                            'cheekLineLeft':{'keys':['jawTopLeft','cheekBoneLeft'],
                                       'rebuild':False},
                            'cheekLineRight':{'keys':['jawTopRight','cheekBoneRight'],
                                             'rebuild':False},
                            'smileLineLeft':{'keys':['cheekBoneLeft','chinLeft'],
                                             'rebuild':False},
                            'smileLineRight':{'keys':['cheekBoneRight','chinRight'],
                                              'rebuild':False},                            
                            }
        
        if self.noseSetup:
            _d_curveCreation['cheekLineLeft']['keys'].append('sneerLeft')
            _d_curveCreation['cheekLineRight']['keys'].append('sneerRight')
            
        d_curveCreation.update(_d_curveCreation)
        
    if self.chinSetup:
        log.debug("|{0}| >>  Chin setup...".format(_str_func))
        _str_jawSetup = self.getEnumValueString('chinSetup')
        """
        _d_pairs = {'jawLeft':'jawRight',
                    'jawTopLeft':'jawTopRight',
                    'chinLeft':'chinRight',
                    'cheekBoneLeft':'cheekBoneRight',
                    }
        d_pairs.update(_d_pairs)"""
    
        _d = {'chin':{'color':'yellowBright','tagOnly':True,'arrow':False,'jointLabel':True,
                      'vectorLine':False,'scaleSpace':[0,-.8,.8],}}

    
        d_creation.update(_d)
        l_order.extend(['chin'])
        _d_curveCreation = {'chinLeft':{'keys':['chin','chinLeft'],
                                       'rebuild':False},
                            'chinRight':{'keys':['chin','chinRight'],
                                        'rebuild':False},
                            }
   
        d_curveCreation.update(_d_curveCreation)
        
    #lip ---------------------------------------------------------------------
    if self.lipSetup:
        log.debug("|{0}| >>  lip setup...".format(_str_func))
        _str_jawSetup = self.getEnumValueString('lipSetup')
        
        _d_pairs = {'cornerBagLeft':'cornerBagRight',
                    'cornerBackLeft':'cornerBackRight',
                    'cornerFrontLeft':'cornerFrontRight',
                    'cornerPeakLeft':'cornerPeakRight',
                    #'mouthLeft':'mouthRight',
                    #'lipUprLeft':'lipUprRight',
                    #'lipLwrLeft':'lipLwrRight',
                    }
        d_pairs.update(_d_pairs)
        """
        'mouthRight':{'color':'redBright','tagOnly':True,'arrow':False,'jointLabel':True,
                            'vectorLine':1,'scaleSpace':[-.3,-.2,.75],'parentTag':'uprFront',
                            },        
        """
        d_toParent['lwrPeak'] = 'lwrFront'
        d_toParent['lwrBack'] = 'lwrFront'
        d_toParent['lwrGum'] = 'lwrFront'
        d_toParent['uprPeak'] = 'uprFront'
        d_toParent['uprBack'] = 'uprFront'
        d_toParent['uprGum'] = 'uprFront'
        
        d_toParent['cornerBagLeft'] = 'cornerFrontLeft'
        d_toParent['cornerBackLeft'] = 'cornerFrontLeft'
        d_toParent['cornerPeakLeft'] = 'cornerFrontLeft'
        d_toParent['cornerBagRight'] = 'cornerFrontRight'
        d_toParent['cornerBackRight'] = 'cornerFrontRight'
        d_toParent['cornerPeakRight'] = 'cornerFrontRight'
        
        _d = {'cornerFrontLeft':{'color':'blueBright','tagOnly':True,'arrow':False,'jointLabel':True,
                                 'vectorLine':0,'scaleSpace':[.3,-.2,.5],
                                 },
              'cornerBackLeft':{'color':'blueWhite','tagOnly':True,'arrow':False,'jointLabel':0,
                                 'vectorLine':0,'scaleSpace':[.28,-.2,.4],
                                 },
              'cornerBagLeft':{'color':'blueWhite','tagOnly':True,'arrow':False,'jointLabel':0,
                                'vectorLine':0,'scaleSpace':[.3,-.2,.35],
                                },
              'cornerPeakLeft':{'color':'blueWhite','tagOnly':True,'arrow':False,'jointLabel':0,
                               'vectorLine':0,'scaleSpace':[.4,-.2,.5],
                               },
              
              'cornerFrontRight':{'color':'redBright','tagOnly':True,'arrow':False,'jointLabel':True,
                                 'vectorLine':0,'scaleSpace':[-.3,-.2,.5],
                                 },
              'cornerBackRight':{'color':'redWhite','tagOnly':True,'arrow':False,'jointLabel':0,
                                'vectorLine':0,'scaleSpace':[-.28,-.2,.4],
                                },
              'cornerBagRight':{'color':'redWhite','tagOnly':True,'arrow':False,'jointLabel':0,
                               'vectorLine':0,'scaleSpace':[-.3,-.2,.35],
                               },
              'cornerPeakRight':{'color':'redWhite','tagOnly':True,'arrow':False,'jointLabel':0,
                                'vectorLine':0,'scaleSpace':[-.4,-.2,.5],
                                },
              
              
              'uprFront':{'color':'yellowBright','tagOnly':True,'arrow':False,'jointLabel':True,
                        'vectorLine':False,'scaleSpace':[0,-.2,.65],
                        },
              'uprPeak':{'color':'yellowWhite','tagOnly':True,'arrow':False,'jointLabel':0,
                        'vectorLine':False,'scaleSpace':[0,-.1,.7],
                        },
              'uprBack':{'color':'yellowWhite','tagOnly':True,'arrow':False,'jointLabel':0,
                            'vectorLine':False,'scaleSpace':[0,-.2,.5],
                            },
              'uprGum':{'color':'yellowWhite','tagOnly':True,'arrow':False,'jointLabel':0,
                        'vectorLine':False,'scaleSpace':[0,0,.5],
                        },              
              
              'lwrFront':{'color':'greenBright','tagOnly':True,'arrow':False,'jointLabel':True,
                              'vectorLine':False,'scaleSpace':[0,-.3,.65],
                              },
              'lwrPeak':{'color':'greenWhite','tagOnly':True,'arrow':False,'jointLabel':0,
                          'vectorLine':False,'scaleSpace':[0,-.4,.67],
                          },              
              'lwrBack':{'color':'greenWhite','tagOnly':True,'arrow':False,'jointLabel':0,
                          'vectorLine':False,'scaleSpace':[0,-.3,.5],
                          },
              'lwrGum':{'color':'greenWhite','tagOnly':True,'arrow':False,'jointLabel':0,
                         'vectorLine':False,'scaleSpace':[0,-.4,.5],
                         },
              
              
              }
        d_creation.update(_d)
        
        
            
        l_order.extend(['uprFront','uprPeak','uprBack',
                        'lwrFront','lwrPeak','lwrBack',
                        'uprGum','lwrGum',
                        'cornerFrontLeft','cornerPeakLeft','cornerBackLeft','cornerBagLeft',
                        'cornerFrontRight','cornerPeakRight','cornerBackRight','cornerBagRight',
                        #'lipUprLeft','lipUprRight',
                        #'lipLwrLeft','lipLwrRight',
                        ])
        
        """
        'lipUpr':{'keys':['mouthLeft','lipUpr','mouthRight'],
                                      'rebuild':0},
                            'lipLwr':{'keys':['mouthLeft','lipLwr','mouthRight'],
                                      'rebuild':0},
        """
        
        
        _d_curveCreation = {'peakUpr':{'keys':['cornerPeakRight','uprPeak','cornerPeakLeft'],
                                       'rebuild':0},
                            'peakLwr':{'keys':['cornerPeakRight','lwrPeak','cornerPeakLeft'],
                                       'color':'greenWhite',                                       
                                       'rebuild':0},
                            'lipUpr':{'keys':['cornerFrontRight','uprFront','cornerFrontLeft'],
                                       'rebuild':0},
                            'lipLwr':{'keys':['cornerFrontRight','lwrFront','cornerFrontLeft'],
                                       'color':'greenWhite',                                       
                                       'rebuild':0},
                            
                            'lipBackUpr':{'keys':['cornerBackRight','uprBack','cornerBackLeft'],
                                       'rebuild':0},
                            'lipBackLwr':{'keys':['cornerBackRight','lwrBack','cornerBackLeft'],
                                          'color':'greenWhite',                                       
                                          'rebuild':0},                            
                            'lipCrossUpr':{'keys':['uprGum','uprBack','uprFront','uprPeak'],
                                           'rebuild':1},
                            'lipCrossLwr':{'keys':['lwrGum','lwrBack','lwrFront','lwrPeak'],
                                           'color':'greenBright',                                           
                                           'rebuild':1},
                            
                            'lipCornerLeft':{'keys':['cornerBagLeft','cornerBackLeft',
                                                     'cornerFrontLeft','cornerPeakLeft'],
                                           'color':'blueWhite',                                           
                                           'rebuild':0},
                            'lipCornerRight':{'keys':['cornerBagRight','cornerBackRight',
                                                     'cornerFrontRight','cornerPeakRight'],
                                             'color':'redWhite',                                           
                                             'rebuild':0},
                            
                            'lipToChinRight':{'keys':['cornerPeakRight','chinRight'],
                                              'color':'yellowWhite',
                                              'rebuild':0},
                            'lipToChinLeft':{'keys':['cornerPeakLeft','chinLeft'],
                                             'color':'yellowWhite',                                             
                                              'rebuild':0},

                            }
        
        if self.chinSetup:
            _d_curveCreation['lipToChin'] = {'keys':['lwrPeak','chin'],
                                             'color':'yellowWhite',                                             
                                             'rebuild':False}
        if self.noseSetup:
            _d_curveCreation['lipToNoseLeft'] = {'keys':['cornerPeakLeft','noseLeft'],
                                                 'color':'yellowWhite',
                                                 'rebuild':False}
            _d_curveCreation['lipToNoseRight'] = {'keys':['cornerPeakRight','noseRight'],
                                                  'color':'yellowWhite',
                                                 'rebuild':False}
            _d_curveCreation['lipToNoseCenter'] = {'keys':['uprPeak','noseBase'],
                                                  'color':'yellowWhite',
                                                  'rebuild':False}            
        
        d_curveCreation.update(_d_curveCreation)
        
    #Cheek ---------------------------------------------------------------------
    if self.cheekSetup:
        log.debug("|{0}| >>  cheek setup...".format(_str_func))
        _str_jawSetup = self.getEnumValueString('cheekSetup')
        
        """
        _d_pairs = {'cheekLeft':'cheekRight',
                    }
        d_pairs.update(_d_pairs)
    
        _d = {'cheekLeft':{'color':'blueBright','tagOnly':True,'arrow':False,'jointLabel':True,
                            'vectorLine':False,'scaleSpace':[1,-.1,.5]},
              'cheekRight':{'color':'redBright','tagOnly':True,'arrow':False,'jointLabel':True,
                             'vectorLine':False,'scaleSpace':[-1,-.1,.5]},
              }
        d_creation.update(_d)
        l_order.extend(['cheekLeft','cheekRight'])"""


    #nose ---------------------------------------------------------------------
    if self.noseSetup:
        log.debug("|{0}| >>  nose setup...".format(_str_func))
        _str_jawSetup = self.getEnumValueString('noseSetup')
        
        _d_pairs = {'noseLeft':'noseRight',
                    'sneerLeft':'sneerRight',
                    }
        d_pairs.update(_d_pairs)
    
        _d = {'noseTip':{'color':'yellowBright','tagOnly':True,'arrow':False,'jointLabel':False,
                         'vectorLine':False,'scaleSpace':[0,.45,1],},
              'noseBase':{'color':'yellowBright','tagOnly':True,'arrow':False,'jointLabel':False,
                         'vectorLine':False,'scaleSpace':[0,.15,.8],},
              #'bridgeHelp':{'color':'yellowBright','tagOnly':True,'arrow':False,'jointLabel':False,
              #            'vectorLine':False,'scaleSpace':[0,.7,1],
              #            'defaults':{'tz':1}},
              'bridge':{'color':'yellowBright','tagOnly':True,'arrow':False,'jointLabel':0,
                         'vectorLine':False,'scaleSpace':[0,1,.5],},              
              'noseLeft':{'color':'blueBright','tagOnly':True,'arrow':False,'jointLabel':True,
                            'vectorLine':False,'scaleSpace':[.3,.3,.5],},
              'noseRight':{'color':'redBright','tagOnly':True,'arrow':False,'jointLabel':True,
                             'vectorLine':False,'scaleSpace':[-.3,.3,.5],},
              'sneerLeft':{'color':'blueBright','tagOnly':True,'arrow':False,'jointLabel':True,
                          'vectorLine':False,'scaleSpace':[.2,.6,.3],
                          },
              'sneerRight':{'color':'redBright','tagOnly':True,'arrow':False,'jointLabel':True,
                           'vectorLine':False,'scaleSpace':[-.2,.6,.3],
                           },              
              }
        d_creation.update(_d)
        l_order.extend(['noseLeft','noseRight',
                        'sneerLeft','sneerRight',
                        'noseTip','noseBase','bridge'])
        

        _d_curveCreation = {'noseProfile':{'keys':['bridge','noseTip','noseBase'],
                                   'rebuild':False},
                            'noseCross':{'keys':['noseRight','noseTip','noseLeft'],
                                           'rebuild':False},
                            'noseRight':{'keys':['sneerRight','noseRight'],
                                         'rebuild':False},
                            'noseLeft':{'keys':['sneerLeft','noseLeft'],
                                         'rebuild':False},                            
                            'noseUnder':{'keys':['noseRight','noseBase','noseLeft'],
                                           'rebuild':False},
                            'bridgeTop':{'keys':['sneerRight','bridge','sneerLeft'],
                                         'rebuild':False},
                            }
        d_curveCreation.update(_d_curveCreation)        
        
    
    #make em...
    log.debug("|{0}| >>  Make the handles...".format(_str_func))    
    md_res = self.UTILS.create_defineHandles(self, l_order, d_creation, _size / 10, mDefineNull, mBBShape)

    md_handles = md_res['md_handles']
    ml_handles = md_res['ml_handles']
    
    
    for k,p in d_toParent.iteritems():
        md_handles[k].p_parent = md_handles[p]

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
    log.debug("|{0}| >>  Make the curves...".format(_str_func))    
    md_resCurves = self.UTILS.create_defineCurve(self, d_curveCreation, md_handles, mNoTransformNull)
    self.msgList_connect('defineHandles',ml_handles)#Connect    
    self.msgList_connect('defineSubHandles',ml_handles)#Connect
    self.msgList_connect('defineCurves',md_resCurves['ml_curves'])#Connect
    
    return


#=============================================================================================================
#>> Template
#=============================================================================================================
def templateDelete(self):
    _str_func = 'templateDelete'
    log.debug("|{0}| >> ...".format(_str_func)+ '-'*80)
    log.debug("{0}".format(self))
    ml_defSubHandles = self.msgList_get('defineSubHandles')
    for mObj in ml_defSubHandles:
        mObj.template = False    
            
    try:self.defineLoftMesh.template = False
    except:pass
    self.bbHelper.v = True
    
    for mObj in self.msgList_get('defineCurves'):
        mObj.template=0
        mObj.v=1
    
    
@cgmGEN.Timer
def template(self):
    try:    
        _str_func = 'template'
        log.debug("|{0}| >>  ".format(_str_func)+ '-'*80)
        log.debug("{0}".format(self))
        
        _short = self.p_nameShort
        #_baseNameAttrs = ATTR.datList_getAttrs(self.mNode,'nameList')
        
        #Initial checks ===============================================================================
        log.debug("|{0}| >> Initial checks...".format(_str_func)+ '-'*40)    

        #Create temple Null  ==================================================================================
        mTemplateNull = BLOCKUTILS.templateNull_verify(self)
        mNoTransformNull = self.atUtils('noTransformNull_verify','template')
        
        mHandleFactory = self.asHandleFactory()
        
        self.bbHelper.v = False
        _size = MATH.average(self.baseSize[1:])        
        
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
            mObj.template=1
        pprint.pprint(vars())
        
        #
        d_pairs = {}
        d_creation = {}
        l_order = []
        d_curveCreation = {}
        ml_subHandles = []
        md_loftCreation = {}
        
        DGETAVG = DIST.get_average_position
        CRVPCT = CURVES.getPercentPointOnCurve
        
        pSmileR = False
        pSmileL = False
        
        #Main setup -----------------------------------------------------
        if self.jawSetup:
            log.debug("|{0}| >>  Jaw setup...".format(_str_func))
            _str_jawSetup = self.getEnumValueString('jawSetup')
        
            _d_pairs = {'jawLineLeftMid':'jawLineRightMid',
                        'jawEdgeLeftMid':'jawEdgeRightMid',
                        'cheekLineLeftMid':'cheekLineRightMid',
                        'cheekLeft':'cheekRight',
                        }
            
            pMidChinR = DIST.get_average_position([md_handles['jawRight'].p_position,
                                                   md_handles['chinRight'].p_position])
            pMidChinL = DIST.get_average_position([md_handles['jawLeft'].p_position,
                                                   md_handles['chinLeft'].p_position])
            
            pMidJawR = DIST.get_average_position([md_handles['jawRight'].p_position,
                                                   md_handles['jawTopRight'].p_position])
            pMidJawL = DIST.get_average_position([md_handles['jawLeft'].p_position,
                                                   md_handles['jawTopLeft'].p_position])
            
            pMidCheekR = DIST.get_average_position([md_handles['cheekBoneRight'].p_position,
                                                  md_handles['jawTopRight'].p_position])
            pMidCheekL = DIST.get_average_position([md_handles['cheekBoneLeft'].p_position,
                                                  md_handles['jawTopLeft'].p_position])
            
            pNeckBase = DIST.get_average_position([md_handles['jawLeft'].p_position,
                                                      md_handles['jawRight'].p_position])
            
            pChin = DGETAVG([md_handles['chinLeft'].p_position,
                             md_handles['chinRight'].p_position])
            pJawUnder = DIST.get_average_position([pNeckBase,
                                                  pChin])
            
            pCheekL =  DIST.get_average_position([md_handles['cheekBoneLeft'].p_position,
                                                   md_handles['jawLeft'].p_position])
            pCheekR =  DIST.get_average_position([md_handles['cheekBoneRight'].p_position,
                                                  md_handles['jawRight'].p_position])            

            l_order.extend(['jawLineLeftMid','jawLineRightMid',
                            'cheekLineLeftMid','cheekLineRightMid',
                            'jawEdgeLeftMid','jawEdgeRightMid',
                            'cheekLeft','cheekRight',
                            'neckBase','jawUnder','chinBase'])
            
            _d = {'jawLineLeftMid':{'color':'blueSky','tagOnly':True,'arrow':False,'jointLabel':0,
                             'vectorLine':False,'pos':pMidChinL},
                  'jawLineRightMid':{'color':'redWhite','tagOnly':True,'arrow':False,'jointLabel':0,
                              'vectorLine':False,'pos':pMidChinR},
                  'jawEdgeLeftMid':{'color':'blueSky','tagOnly':True,'arrow':False,'jointLabel':0,
                                    'vectorLine':False,'pos':pMidJawL},
                  'jawEdgeRightMid':{'color':'redWhite','tagOnly':True,'arrow':False,'jointLabel':0,
                                     'vectorLine':False,'pos':pMidJawR},
                  'cheekLineLeftMid':{'color':'blueSky','tagOnly':True,'arrow':False,'jointLabel':0,
                                    'vectorLine':False,'pos':pMidCheekL},
                  'cheekLineRightMid':{'color':'redWhite','tagOnly':True,'arrow':False,'jointLabel':0,
                                     'vectorLine':False,'pos':pMidCheekR},
                  'jawUnder':{'color':'yellowBright','tagOnly':True,'arrow':False,'jointLabel':0,
                              'vectorLine':False,'pos':pJawUnder},
                  'neckBase':{'color':'yellowBright','tagOnly':True,'arrow':False,'jointLabel':0,
                              'vectorLine':False,'pos':pNeckBase},
                  'cheekLeft':{'color':'blueSky','tagOnly':True,'arrow':False,'jointLabel':0,
                                      'vectorLine':False,'pos':pCheekL},
                  'cheekRight':{'color':'redWhite','tagOnly':True,'arrow':False,'jointLabel':0,
                                       'vectorLine':False,'pos':pCheekR},                  
                  'chinBase':{'color':'yellowBright','tagOnly':True,'arrow':False,'jointLabel':0,
                          'vectorLine':False,'pos':pChin},                  
                  }
            
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
                _d_pairs['smileLeft']='smileRight'
        
            d_creation.update(_d)
            d_pairs.update(_d_pairs)
            
            _d_curveCreation = {'jawTemplateRight1':{'keys':['jawTopRight','cheekLineRightMid','cheekBoneRight'],
                                                     'rebuild':True},
                                'jawTemplateRight2':{'keys':['jawEdgeRightMid','cheekRight','smileRight'],
                                                     'rebuild':True},
                                'jawTemplateRight3':{'keys':['jawRight','jawLineRightMid','chinRight'],
                                                     'rebuild':True},
                                'jawTemplateCenter':{'keys':['neckBase','jawUnder','chinBase'],
                                                     'rebuild':True},
                                'jawTemplateLeft1':{'keys':['jawTopLeft','cheekLineLeftMid','cheekBoneLeft'],
                                                     'rebuild':True},
                                'jawTemplateLeft2':{'keys':['jawEdgeLeftMid','cheekLeft','smileLeft'],
                                                     'rebuild':True},
                                'jawTemplateLeft3':{'keys':['jawLeft','jawLineLeftMid','chinLeft'],
                                                     'rebuild':True},                               
                                }
            
            #if self.chinSetup:
            #    _d_curveCreation['jawTemplateRight3']['keys'].append('chinFormRight')
            #    _d_curveCreation['jawTemplateCenter']['keys'].append('chin')
            #    _d_curveCreation['jawTemplateLeft3']['keys'].append('chinFormLeft')

            d_curveCreation.update(_d_curveCreation)
            md_loftCreation['jaw'] =  {'keys':['jawTemplateRight1','jawTemplateRight2','jawTemplateRight3',
                                               'jawTemplateCenter',
                                               'jawTemplateLeft3','jawTemplateLeft2','jawTemplateLeft1'],
                                       'rebuild':{'spansU':30,'spansV':5,'degreeU':3},
                                       'kws':{'noRebuild':True}}
            
        if self.noseSetup:
            log.debug("|{0}| >>  nose setup...".format(_str_func))
            _str_noseSetup = self.getEnumValueString('nose')
            _d_pairs = {}
            
            for k in ['edgeOrbTop','smileUpr',
                      'bridgePlane','bridgeBase',
                      'sneerLow','bridgeStartBase','bridgeStartPlane',
                      'nostrilBase','nostrilTop','bulbTopBase','bulbTopPlane',
                      'nostrilFront',
                      'bulbBase','bulbPlane',
                      'bulbUnder',
                      'nostrilUnderEdge','nostrilUnderInner','nostrilUnderFront',
                      ]:
                _d_pairs[k+'Left'] = k+'Right'
                
            l_order.extend(['bulbTopCenter','bridgeStartCenter','bulbUnderCenter'])
            
            _d_pos = {'edgeOrbTopLeft':DGETAVG([md_handles['cheekBoneLeft'].p_position,
                                                   md_handles['sneerLeft'].p_position]),
                      'edgeOrbTopRight':DGETAVG([md_handles['cheekBoneRight'].p_position,
                                                md_handles['sneerRight'].p_position]),
                      'smileUprLeft':DGETAVG([pSmileL,
                                              md_handles['noseLeft'].p_position]),
                      'smileUprRight':DGETAVG([pSmileR,
                                               md_handles['noseRight'].p_position]),
                      
                      'bridgePlaneRight':CRVPCT(md_dCurves['bridgeTop'].mNode,.3),
                      'bridgePlaneLeft':CRVPCT(md_dCurves['bridgeTop'].mNode,.7),
                      'bridgeBaseRight':CRVPCT(md_dCurves['bridgeTop'].mNode,.15),
                      'bridgeBaseLeft':CRVPCT(md_dCurves['bridgeTop'].mNode,.85),
                      
                      'nostrilUnderEdgeRight':CRVPCT(md_dCurves['noseUnder'].mNode,.15),
                      'nostrilUnderEdgeLeft':CRVPCT(md_dCurves['noseUnder'].mNode,.85),
                      'nostrilUnderInnerRight':CRVPCT(md_dCurves['noseUnder'].mNode,.4),
                      'nostrilUnderInnerLeft':CRVPCT(md_dCurves['noseUnder'].mNode,.6),
                      
                      'sneerLowRight':CRVPCT(md_dCurves['noseRight'].mNode,.5),
                      'sneerLowLeft':CRVPCT(md_dCurves['noseLeft'].mNode,.5),
                      
                      
                      'nostrilBaseRight':CRVPCT(md_dCurves['noseRight'].mNode,.8),
                      'nostrilBaseLeft':CRVPCT(md_dCurves['noseLeft'].mNode,.8),
                      
                      'bulbTopCenter':CRVPCT(md_dCurves['noseProfile'].mNode,.35),
                      'bridgeStartCenter':CRVPCT(md_dCurves['noseProfile'].mNode,.2),
                      'bulbUnderCenter':CRVPCT(md_dCurves['noseProfile'].mNode,.8),
                      }
            
            _d = {'bulbTopCenter':{'color':'yellowWhite','tagOnly':True,'arrow':False,'jointLabel':0,
                                   'vectorLine':False,
                                   'pos':_d_pos['bulbTopCenter'],
                                   },
                  'bridgeStartCenter':{'color':'yellowWhite','tagOnly':True,'arrow':False,'jointLabel':0,
                                       'vectorLine':False,
                                       'pos':_d_pos['bridgeStartCenter'],
                                       },
                  'bulbUnderCenter':{'color':'yellowWhite','tagOnly':True,'arrow':False,'jointLabel':0,
                                     'vectorLine':False,
                                     'pos':_d_pos['bulbUnderCenter'],
                                     },
                  }            
            
            #We need to subprocess a few more points of data and push them back to to our _d_pos
            #curve pos points, name of handle, percent on that curve
            _d_split = {'noseBridge':{'l_pos':[_d_pos['sneerLowRight'],
                                               _d_pos['bridgeStartCenter'],
                                               _d_pos['sneerLowLeft'],
                                               ],
                                      'handles':{'bridgeStartBaseRight':.15,
                                                 'bridgeStartPlaneRight':.35,
                                                 'bridgeStartPlaneLeft':.65,
                                                 'bridgeStartBaseLeft':.85}},
                        'noseBulbTop':{'l_pos':[_d_pos['nostrilBaseRight'],
                                               _d_pos['bulbTopCenter'],
                                               _d_pos['nostrilBaseLeft'],
                                               ],
                                      'handles':{'nostrilTopRight':.1,
                                                 'bulbTopBaseRight':.2,
                                                 'bulbTopPlaneRight':.35,
                                                 'bulbTopPlaneLeft':.65,
                                                 'bulbTopBaseLeft':.8,
                                                 'nostrilTopLeft':.9,}},
                        'bulb':{'l_pos':[d_defPos['noseRight'],
                                         d_defPos['noseTip'],
                                         d_defPos['noseLeft'],
                                                ],
                                'handles':{'nostrilFrontRight':.1,
                                           'bulbBaseRight':.2,
                                           'bulbPlaneRight':.35,
                                           'bulbPlaneLeft':.65,
                                           'bulbBaseLeft':.8,
                                           'nostrilFrontLeft':.9}},
                        'bulbUnder':{'l_pos':[_d_pos['nostrilUnderEdgeRight'],
                                              _d_pos['bulbUnderCenter'],
                                              _d_pos['nostrilUnderEdgeLeft'],
                                              ],
                                'handles':{'nostrilUnderFrontRight':.15,
                                           'bulbUnderRight':.3,
                                           'bulbUnderLeft':.7,
                                           'nostrilUnderFrontLeft':.85,}}
                        }
            
            for k,dTmp in _d_split.iteritems():
                #Make our new curve
                _crv = CORERIG.create_at(create='curve',l_pos= dTmp['l_pos'])
                for h,v in dTmp['handles'].iteritems():
                    _d_pos[h] = CRVPCT(_crv,v)
                mc.delete(_crv)

            for k,v in _d_pairs.iteritems():
                l_order.extend([k,v])
                p_k = _d_pos.get(k)
                p_v = _d_pos.get(v)
                
                if p_k:
                    _d[k] = {'color':'blueSky','tagOnly':True,'arrow':False,'jointLabel':0,
                             'vectorLine':False,
                             'pos':p_k}
                if p_v:
                    _d[v] = {'color':'redWhite','tagOnly':True,'arrow':False,'jointLabel':0,
                             'vectorLine':False,
                             'pos':p_v}

            d_creation.update(_d)
            d_pairs.update(_d_pairs)
            
            #Curve declarations.....
            d_curveCreation['bridgeTop'] = {'keys':['sneerRight',
                                                        'bridgeBaseRight',
                                                        'bridgePlaneRight',
                                                        'bridge',
                                                        'bridgePlaneLeft',
                                                        'bridgeBaseLeft',
                                                        'sneerLeft'],
                                                'rebuild':1}
            d_curveCreation['bridgeStart'] = {'keys':['sneerLowRight',
                                                          'bridgeStartBaseRight',
                                                          'bridgeStartPlaneRight',
                                                          'bridgeStartCenter',
                                                          'bridgeStartPlaneLeft',
                                                          'bridgeStartBaseLeft',
                                                          'sneerLowLeft'],
                                                  'rebuild':1}
            d_curveCreation['bulbTop'] = {'keys':['nostrilBaseRight',
                                                  'nostrilTopRight',
                                                  'bulbTopBaseRight',
                                                  'bulbTopPlaneRight',
                                                  'bulbTopCenter',
                                                  'bulbTopPlaneLeft',
                                                  'bulbTopBaseLeft',
                                                  'nostrilTopLeft',
                                                  'nostrilBaseLeft'],
                                          'rebuild':1}
            d_curveCreation['bulb'] = {'keys':['noseRight',
                                               'nostrilFrontRight',
                                               'bulbBaseRight',
                                               'bulbPlaneRight',
                                               'noseTip',
                                               'bulbPlaneLeft',
                                               'bulbBaseLeft',
                                               'nostrilFrontLeft',
                                               'noseLeft'],
                                          'rebuild':1}
            
            d_curveCreation['bulbUnder'] = {'keys':['nostrilUnderEdgeRight',
                                                    'nostrilUnderFrontRight',
                                                    'bulbUnderRight',
                                                    'bulbUnderCenter',
                                                    'bulbUnderLeft',
                                                    'nostrilUnderFrontLeft',
                                                    'nostrilUnderEdgeLeft'],
                                            'rebuild':1}            
            d_curveCreation['noseUnderTrace'] = {'keys':['noseRight',
                                                         'nostrilUnderEdgeRight',
                                                         'nostrilUnderInnerRight',
                                                         'noseBase',
                                                         'nostrilUnderInnerLeft',
                                                         'nostrilUnderEdgeLeft',
                                                         'noseLeft'],
                                                 'rebuild':1}
            d_curveCreation['noseUnderSmallTrace'] = {'keys':['nostrilUnderInnerRight',
                                                              'noseBase',
                                                              'nostrilUnderInnerLeft'],
                                                 'rebuild':1}            
            
            d_curveCreation['noseSideRight'] = {'keys':['sneerRight', 'sneerLowRight',
                                                        'nostrilBaseRight','noseRight'],
                                                'rebuild':1}
            d_curveCreation['eyeOrbRight'] = {'keys':['edgeOrbTopRight', 'smileUprRight'],
                                                'rebuild':1}
            d_curveCreation['eyeCheekMeetRight'] = {'keys':['cheekBoneRight', 'smileRight'],
                                               'rebuild':1}
            d_curveCreation['noseSideLeft'] = {'keys':['sneerLeft', 'sneerLowLeft',
                                                       'nostrilBaseLeft','noseLeft'],
                                                'rebuild':1}
            d_curveCreation['eyeOrbLeft'] = {'keys':['edgeOrbTopLeft', 'smileUprLeft'],
                                              'rebuild':1}
            d_curveCreation['eyeCheekMeetLeft'] = {'keys':['cheekBoneLeft', 'smileLeft'],
                                                    'rebuild':1}
            
            
            #LoftDeclarations....
            md_loftCreation['nose'] =  {'keys':['bridgeTop','bridgeStart',
                                                'bulbTop','bulb','bulbUnder','noseUnderTrace'],
                                        'rebuild':{'spansU':12,'spansV':12,'degreeU':3}}
                                        
            md_loftCreation['noseToCheekRight'] =  {'keys':['noseSideRight','eyeOrbRight','eyeCheekMeetRight'],
                                                    'rebuild':{'spansU':4,'spansV':5,'degreeU':3},
                                                    'kws':{'noRebuild':True}}
            md_loftCreation['noseToCheekLeft'] =  {'keys':['noseSideLeft','eyeOrbLeft','eyeCheekMeetLeft'],
                                                   'rebuild':{'spansU':4,'spansV':5,'degreeU':3},
                                                   'kws':{'noRebuild':False}}
                                                   
            md_loftCreation['nose']['keys'].reverse()
            
            """
            _d_curveCreation = {'jawTemplate1':{'keys':['jawTopLeft','jawEdgeLeftMid','jawLeft','neckBase',
                                                        'jawRight','jawEdgeRightMid','jawTopRight'],
                                                'rebuild':True},
                                'jawTemplate2':{'keys':['cheekLineLeftMid','cheekLeft','jawLineLeftMid',
                                                        'jawUnder',
                                                        'jawLineRightMid','cheekRight','cheekLineRightMid'],
                                                'rebuild':True},
                                'jawTemplate3':{'keys':['cheekBoneLeft','smileLeft','chinLeft','chin',
                                                        'chinRight','smileRight','cheekBoneRight'],
                                                'rebuild':True},
                                }
    
            d_curveCreation.update(_d_curveCreation)
            """            
            
    
    
        
        if self.chinSetup:
            log.debug("|{0}| >>  chin setup...".format(_str_func))
            _str_noseSetup = self.getEnumValueString('chinSetup')
            _d_pairs = {}
        
            for k in ['chinForm',
                      ]:
                _d_pairs[k+'Left'] = k+'Right'
        
        
            #_d_pos = {'lipTopMidCenter':CRVPCT(md_dCurves['lipToNoseCenter'].mNode,.5),
            #          'lipUnderMidCenter':CRVPCT(md_dCurves['lipToChin'].mNode,.4)
  
        
            _d = {}
        
            #We need to subprocess a few more points of data and push them back to to our _d_pos
            #curve pos points, name of handle, percent on that curve
            _d_split = {'chin':{'l_pos':[pSmileR,
                                         d_defPos['chin'],
                                         pSmileL,
                                            ],
                                   'handles':{'chinFormRight':.4,
                                              'chinFormLeft':.6,
                                              }},
                        }
        
            for k,dTmp in _d_split.iteritems():
                #Make our new curve
                _crv = CORERIG.create_at(create='curve',l_pos= dTmp['l_pos'])
                for h,v in dTmp['handles'].iteritems():
                    _d_pos[h] = CRVPCT(_crv,v)
                mc.delete(_crv)
        
            for k,v in _d_pairs.iteritems():
                l_order.extend([k,v])
                p_k = _d_pos.get(k)
                p_v = _d_pos.get(v)
        
                if p_k:
                    _d[k] = {'color':'blueSky','tagOnly':True,'arrow':False,'jointLabel':0,
                             'vectorLine':False,
                             'pos':p_k}
                if p_v:
                    _d[v] = {'color':'redWhite','tagOnly':True,'arrow':False,'jointLabel':0,
                             'vectorLine':False,
                             'pos':p_v}
        
            d_creation.update(_d)
            d_pairs.update(_d_pairs)
        
            #Curve declarations.....
            d_curveCreation['chin'] = {'keys':['smileRight',
                                               'chinFormRight',
                                               'chin',
                                               'chinFormLeft',
                                               'smileLeft',],
                                            'rebuild':1}
            
            d_curveCreation['chinSeal'] = {'keys':['smileRight',
                                                   'chinRight',
                                                   'chinBase',
                                                   'chinLeft',
                                                   'smileLeft',],
                                           'rebuild':1}            
                    


        if self.lipSetup:
            log.debug("|{0}| >>  lip setup...".format(_str_func))
            _str_noseSetup = self.getEnumValueString('nose')
            _d_pairs = {}
            
            for k in ['uprTrace1','uprTrace2','uprTrace3',
                      'lwrTrace1','lwrTrace2','lwrTrace3',
                      'uprFront1','uprFront2',
                      'lwrFront1','lwrFront2',
                      
                      'uprBack1','uprBack2',
                      'lwrBack1','lwrBack2',
                      
                      'uprGum1','uprGum2',
                      'lwrGum1','lwrGum2',
                      
                      'uprLipTop1','uprLipTop2',
                      'lwrLipTop1','lwrLipTop2',                      
                      
                      ]:
                _d_pairs[k+'Left'] = k+'Right'
                
            l_order.extend(['lipTopMidCenter','lipUnderMidCenter'])
            
            _d_pos = {'lipTopMidCenter':CRVPCT(md_dCurves['lipToNoseCenter'].mNode,.5),
                      'lipUnderMidCenter':CRVPCT(md_dCurves['lipToChin'].mNode,.4)
                      #'edgeOrbTopLeft':DGETAVG([md_handles['cheekBoneLeft'].p_position,
                      #                             md_handles['sneerLeft'].p_position]),
                      #'bridgeStartCenter':CRVPCT(md_dCurves['noseProfile'].mNode,.2),
                      #'bulbUnderCenter':CRVPCT(md_dCurves['noseProfile'].mNode,.8),
                      }
            
            _d = {'lipTopMidCenter':{'color':'yellowWhite','tagOnly':True,'arrow':False,'jointLabel':0,
                                       'vectorLine':False,
                                       'pos':_d_pos['lipTopMidCenter'],
                                       },
                  'lipUnderMidCenter':{'color':'yellowWhite','tagOnly':True,'arrow':False,'jointLabel':0,
                                     'vectorLine':False,
                                     'pos':_d_pos['lipUnderMidCenter'],
                                     },
                  
                  #'bridgeStartCenter':{'color':'yellowWhite','tagOnly':True,'arrow':False,'jointLabel':0,
                  #                     'vectorLine':False,
                  #                     'pos':_d_pos['bridgeStartCenter'],
                  #                     },
                  }            
            
            #We need to subprocess a few more points of data and push them back to to our _d_pos
            #curve pos points, name of handle, percent on that curve
            _d_split = {'uprMain':{'l_pos':[d_defPos['cornerPeakRight'],
                                            d_defPos['uprPeak'],
                                            d_defPos['cornerPeakLeft'],
                                            ],
                                      'handles':{'uprTrace1Right':.1,
                                                 'uprTrace2Right':.25,
                                                 'uprTrace3Right':.35,
                                                 'uprTrace3Left':.65,
                                                 'uprTrace2Left':.75,
                                                 'uprTrace1Left':.9,
                                                 }},
                        'lwrMain':{'l_pos':[d_defPos['cornerFrontRight'],
                                            d_defPos['lwrPeak'],
                                            d_defPos['cornerFrontLeft'],
                                            ],
                                      'handles':{'lwrTrace1Right':.1,
                                                 'lwrTrace2Right':.25,
                                                 'lwrTrace3Right':.35,
                                                 'lwrTrace3Left':.65,
                                                 'lwrTrace2Left':.75,
                                                 'lwrTrace1Left':.9,}},
                        
                        'uprFront':{'l_pos':[d_defPos['cornerFrontRight'],
                                            d_defPos['uprFront'],
                                            d_defPos['cornerFrontLeft'],
                                            ],
                                   'handles':{'uprFront1Right':.2,
                                              'uprFront2Right':.35,
                                              'uprFront2Left':.65,
                                              'uprFront1Left':.8,
                                              }},
                        'lwrFront':{'l_pos':[d_defPos['cornerFrontRight'],
                                             d_defPos['lwrFront'],
                                             d_defPos['cornerFrontLeft'],
                                             ],
                                    'handles':{'lwrFront1Right':.2,
                                               'lwrFront2Right':.35,
                                               'lwrFront2Left':.65,
                                               'lwrFront1Left':.8,
                                               }},
                        
                        'uprBack':{'l_pos':[d_defPos['cornerBackRight'],
                                             d_defPos['uprBack'],
                                             d_defPos['cornerBackLeft'],
                                             ],
                                    'handles':{'uprBack1Right':.2,
                                               'uprBack2Right':.35,
                                               'uprBack2Left':.65,
                                               'uprBack1Left':.8,
                                               }},
                        'lwrBack':{'l_pos':[d_defPos['cornerBackRight'],
                                             d_defPos['lwrBack'],
                                             d_defPos['cornerBackLeft'],
                                             ],
                                    'handles':{'lwrBack1Right':.2,
                                               'lwrBack2Right':.35,
                                               'lwrBack2Left':.65,
                                               'lwrBack1Left':.8,
                                               }},
                        
                        'uprGum':{'l_pos':[d_defPos['cornerBagRight'],
                                            d_defPos['uprGum'],
                                            d_defPos['cornerBagLeft'],
                                            ],
                                   'handles':{'uprGum1Right':.2,
                                              'uprGum2Right':.35,
                                              'uprGum2Left':.65,
                                              'uprGum1Left':.8,
                                              }},
                        'lwrGum':{'l_pos':[d_defPos['cornerBagRight'],
                                            d_defPos['lwrGum'],
                                            d_defPos['cornerBagLeft'],
                                            ],
                                   'handles':{'lwrGum1Right':.2,
                                              'lwrGum2Right':.35,
                                              'lwrGum2Left':.65,
                                              'lwrGum1Left':.8,
                                              }},
                        
                        'uprLipTop':{'l_pos':[d_defPos['cornerPeakRight'],
                                           _d_pos['lipTopMidCenter'],
                                           d_defPos['cornerPeakLeft'],
                                           ],
                                  'handles':{'uprLipTop1Right':.2,
                                             'uprLipTop2Right':.35,
                                             'uprLipTop2Left':.65,
                                             'uprLipTop1Left':.8,
                                             }},
                        'lwrLipTop':{'l_pos':[d_defPos['cornerPeakRight'],
                                              _d_pos['lipUnderMidCenter'],
                                              d_defPos['cornerPeakLeft'],
                                              ],
                                     'handles':{'lwrLipTop1Right':.2,
                                                'lwrLipTop2Right':.35,
                                                'lwrLipTop2Left':.65,
                                                'lwrLipTop1Left':.8,
                                                }},
                        
                        }
            
            for k,dTmp in _d_split.iteritems():
                #Make our new curve
                _crv = CORERIG.create_at(create='curve',l_pos= dTmp['l_pos'])
                for h,v in dTmp['handles'].iteritems():
                    _d_pos[h] = CRVPCT(_crv,v)
                mc.delete(_crv)

            for k,v in _d_pairs.iteritems():
                l_order.extend([k,v])
                p_k = _d_pos.get(k)
                p_v = _d_pos.get(v)
                
                if p_k:
                    _d[k] = {'color':'blueSky','tagOnly':True,'arrow':False,'jointLabel':0,
                             'vectorLine':False,
                             'pos':p_k}
                if p_v:
                    _d[v] = {'color':'redWhite','tagOnly':True,'arrow':False,'jointLabel':0,
                             'vectorLine':False,
                             'pos':p_v}

            d_creation.update(_d)
            d_pairs.update(_d_pairs)
            
            #Curve declarations.....
            d_curveCreation['uprLipTop'] = {'keys':['cornerPeakRight',
                                                   'uprLipTop1Right',
                                                   'uprLipTop2Right',
                                                   'lipTopMidCenter',
                                                   'uprLipTop2Left',
                                                   'uprLipTop1Left',
                                                   'cornerPeakLeft'],
                                           'rebuild':1}
            d_curveCreation['lwrLipBottom'] = {'keys':['cornerPeakRight',
                                                    'lwrLipTop1Right',
                                                    'lwrLipTop2Right',
                                                    'lipUnderMidCenter',
                                                    'lwrLipTop2Left',
                                                    'lwrLipTop1Left',
                                                    'cornerPeakLeft'],
                                            'rebuild':1}
            
            
            
            d_curveCreation['uprTrace'] = {'keys':['cornerPeakRight',
                                                  'uprTrace1Right',
                                                  'uprTrace2Right',
                                                  'uprTrace3Right',
                                                  'uprPeak',
                                                  'uprTrace3Left',
                                                  'uprTrace2Left',
                                                  'uprTrace1Left',
                                                  'cornerPeakLeft'],
                                              'rebuild':1}
            d_curveCreation['lwrTrace'] = {'keys':['cornerFrontRight',
                                                  'lwrTrace1Right',
                                                  'lwrTrace2Right',
                                                  'lwrTrace3Right',
                                                  'lwrPeak',
                                                  'lwrTrace3Left',
                                                  'lwrTrace2Left',
                                                  'lwrTrace1Left',
                                                  'cornerFrontLeft'],
                                          'rebuild':1}
            
            d_curveCreation['uprFront'] = {'keys':['cornerFrontRight',
                                                  'uprFront1Right',
                                                  'uprFront2Right',
                                                  'uprFront',
                                                  'uprFront2Left',
                                                  'uprFront1Left',
                                                  'cornerFrontLeft'],
                                          'rebuild':1}
            d_curveCreation['lwrFront'] = {'keys':['cornerBackRight',
                                                   'lwrFront1Right',
                                                   'lwrFront2Right',
                                                   'lwrFront',
                                                   'lwrFront2Left',
                                                   'lwrFront1Left',
                                                   'cornerBackLeft'],
                                           'rebuild':1}
            
            d_curveCreation['uprBack'] = {'keys':['cornerBackRight',
                                                   'uprBack1Right',
                                                   'uprBack2Right',
                                                   'uprBack',
                                                   'uprBack2Left',
                                                   'uprBack1Left',
                                                   'cornerBackLeft'],
                                           'rebuild':1}
            d_curveCreation['lwrBack'] = {'keys':['cornerBackRight',
                                                   'lwrBack1Right',
                                                   'lwrBack2Right',
                                                   'lwrBack',
                                                   'lwrBack2Left',
                                                   'lwrBack1Left',
                                                   'cornerBackLeft'],
                                           'rebuild':1}
            
            d_curveCreation['uprGum'] = {'keys':['cornerBagRight',
                                                  'uprGum1Right',
                                                  'uprGum2Right',
                                                  'uprGum',
                                                  'uprGum2Left',
                                                  'uprGum1Left',
                                                  'cornerBagLeft'],
                                          'rebuild':1}
            d_curveCreation['lwrGum'] = {'keys':['cornerBagRight',
                                                  'lwrGum1Right',
                                                  'lwrGum2Right',
                                                  'lwrGum',
                                                  'lwrGum2Left',
                                                  'lwrGum1Left',
                                                  'cornerBagLeft'],
                                          'rebuild':1}

            d_curveCreation['smileNose'] = {'keys':['smileRight',
                                                    'smileUprRight',
                                                    'noseRight',
                                                    'nostrilUnderEdgeRight',
                                                    'nostrilUnderInnerRight',
                                                    'noseBase',
                                                    'nostrilUnderInnerLeft',
                                                    'nostrilUnderEdgeLeft',
                                                    'noseLeft',
                                                    'smileUprLeft',
                                                    'smileLeft'],
                                                 'rebuild':1}
            
            #LoftDeclarations....
            md_loftCreation['uprLip'] = {'keys':['smileNose','uprLipTop','uprTrace','uprFront','uprBack','uprGum'],
                                         'rebuild':{'spansU':15,'spansV':10},
                                         'kws':{'noRebuild':True}}
            md_loftCreation['lwrLip'] = {'keys':['lwrLipBottom','lwrTrace','lwrFront','lwrBack','lwrGum'],
                                         'rebuild':{'spansU':15,'spansV':10}}
            
            if d_curveCreation.get('chin'):
                md_loftCreation['lwrLip']['keys'].insert(0,'chin')
                md_loftCreation['lwrLip']['keys'].insert(0,'chinSeal')
                

            
        
        md_res = self.UTILS.create_defineHandles(self, l_order, d_creation, _size / 10,
                                                 mTemplateNull)
        ml_subHandles.extend(md_res['ml_handles'])
        md_handles.update(md_res['md_handles'])
    
            
        md_res = self.UTILS.create_defineCurve(self, d_curveCreation, md_handles, mNoTransformNull)
        md_resCurves = md_res['md_curves']
        
        for k,d in md_loftCreation.iteritems():
            ml_curves = [md_resCurves[k2] for k2 in d['keys']]
            for mObj in ml_curves:
                mObj.v=False
            
            
            self.UTILS.create_simpleTemplateLoftMesh(self,
                                                     [mObj.mNode for mObj in ml_curves],
                                                     mTemplateNull,
                                                     polyType = 'faceLoft',
                                                     d_rebuild = d.get('rebuild',{}),
                                                     baseName = k,
                                                     **d.get('kws',{}))
        
        
        
        
        #Mirror indexing -------------------------------------
        log.debug("|{0}| >> Mirror Indexing...".format(_str_func)+'-'*40) 
        
        idx_ctr = 0
        idx_side = 0
        d = {}
        
        for tag,mHandle in md_handles.iteritems():
            if mHandle in ml_defineHandles:
                continue
            
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
            try:
                md_handles[k].mirrorSide = 1
                md_handles[m].mirrorSide = 2
                md_handles[k].mirrorIndex = idx_side
                md_handles[m].mirrorIndex = idx_side
                md_handles[k].doStore('mirrorHandle',md_handles[m])
                md_handles[m].doStore('mirrorHandle',md_handles[k])
                idx_side +=1        
            except Exception,err:
                log.error('Mirror error: {0}'.format(err))
        
        
        
        self.msgList_connect('templateHandles',ml_subHandles)#Connect
        self.msgList_connect('templateCurves',md_res['ml_curves'])#Connect        
        return
        
        
        
            
        #Build our brow loft --------------------------------------------------------------------------
        log.debug("|{0}| >> Loft...".format(_str_func)+'-'*40) 
        self.UTILS.create_simpleTemplateLoftMesh(self,
                                                 [md_loftCurves['browLine'].mNode,
                                                  md_loftCurves['browUpr'].mNode],
                                                 mTemplateNull,
                                                 polyType = 'bezier',
                                                 baseName = 'brow')
        
        #Build our brow loft --------------------------------------------------------------------------
        log.debug("|{0}| >> Visualize brow...".format(_str_func)+'-'*40)
        md_directCurves = {}
        for tag in ['browLeft','browRight']:
            mCrv = md_loftCurves[tag]
            ml_temp = []
            for k in ['start','mid','end']:
                mLoc = cgmMeta.asMeta(self.doCreateAt())
                mJointLabel = mHandleFactory.addJointLabel(mLoc,k)
                
                self.connectChildNode(mLoc, tag+k.capitalize()+'templateHelper','block')
                
                mLoc.rename("{0}_{1}_templateHelper".format(tag,k))
                
                mPointOnCurve = cgmMeta.asMeta(CURVES.create_pointOnInfoNode(mCrv.mNode,
                                                                             turnOnPercentage=True))
                
                mPointOnCurve.doConnectIn('parameter',"{0}.{1}".format(self.mNode,"param{0}".format(k.capitalize())))
            
            
                mPointOnCurve.doConnectOut('position',"{0}.translate".format(mLoc.mNode))
            
                mLoc.p_parent = mNoTransformNull
                ml_temp.append(mLoc)
                #mLoc.v=False
                #mc.pointConstraint(mTrackLoc.mNode,mTrackGroup.mNode)
                
            #Joint curves......
            _crv = mc.curve(d=1,p=[mObj.p_position for mObj in ml_temp])
            
            #CORERIG.create_at(create='curve',l_pos = l_pos)
            mCrv = cgmMeta.validateObjArg(_crv,'cgmObject',setClass=True)
            mCrv.p_parent = mNoTransformNull
            mHandleFactory.color(mCrv.mNode)
            mCrv.rename('{0}_jointCurve'.format(tag))            
            mCrv.v=False
            md_loftCurves[tag] = mCrv
        
            self.connectChildNode(mCrv, tag+'JointCurve','block')
        
            l_clusters = []
            for i,cv in enumerate(mCrv.getComponents('cv')):
                _res = mc.cluster(cv, n = 'test_{0}_{1}_pre_cluster'.format(ml_temp[i].p_nameBase,i))
                TRANS.parent_set( _res[1], ml_temp[i].mNode)
                l_clusters.append(_res)
                ATTR.set(_res[1],'visibility',False)
                
            mc.rebuildCurve(mCrv.mNode, d=3, keepControlPoints=False,ch=1,s=8,
                            n="reparamRebuild")

    except Exception,err:
        cgmGEN.cgmExceptCB(Exception,err)

#=============================================================================================================
#>> Prerig
#=============================================================================================================
def prerigDelete(self):
    self.noTransTemplateNull.v=True
    self.templateNull.template=False
    
    for mObj in self.msgList_get('defineSubHandles') + self.msgList_get('templateHandles'):
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
    mHandle.doStore('cgmType','templateHandle')
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
    def create_handle(mHelper, mSurface, tag, k, side, controlType = 'main',
                      controlShape = 'squareRounded', mClosestSurf = None,
                      aimGroup = 1,nameDict = None,position = [0,0,0], surfaceOffset =1,mode='track',size = 1.0):
        mHandle = cgmMeta.validateObjArg( CURVES.create_fromName(controlShape, size = size), 
                                          'cgmControl',setClass=1)
        mHandle._verifyMirrorable()
    
        mHandle.doSnapTo(self)
        mHandle.p_parent = mStateNull
    
        if nameDict:
            RIGGEN.store_and_name(mHandle,nameDict)
        else:
            mHandle.doStore('cgmName',tag)
            mHandle.doStore('cgmType','prerigHandle')
            mHandle.doName()
    
    
        _key = tag
        if k:
            _key = _key+k.capitalize()
        mMasterGroup = mHandle.doGroup(True,True,
                                       asMeta=True,
                                       typeModifier = 'master',
                                       setClass='cgmObject')
    
        if mode == 'fixed':
            mMasterGroup.p_position = position
        elif mode == 'track':
            if mHelper:
                mc.pointConstraint(mHelper.mNode,mMasterGroup.mNode,maintainOffset=False)
        else:
            if mClosestSurf:
                mSurfTarget = mClosestSurf
            else:mSurfTarget = mSurface
            
            d_res = DIST.get_closest_point_data(mSurfTarget.mNode,mHelper.mNode)
            mMasterGroup.p_position = d_res['position']    
    
        mHandleFactory.color(mHandle.mNode,side = side, controlType=controlType)
        mStateNull.connectChildNode(mHandle, _key+'prerigHelper','block')
    
        _const = mc.normalConstraint(mSurface.mNode, mMasterGroup.mNode,
                                     aimVector = [0,0,1], upVector = [0,1,0],
                                     worldUpObject = self.mNode,
                                     worldUpType = 'objectrotation', 
                                     worldUpVector = [0,1,0])
        mc.delete(_const)
        
    
        if aimGroup:
            mHandle.doGroup(True,True,
                            asMeta=True,
                            typeModifier = 'aim',
                            setClass='cgmObject')
    
    
        mHandle.tz = surfaceOffset
    
        return mHandle
    
    def create_jointHelper(mPos, mSurface, tag, k, side, nameDict=None, aimGroup = 1,size = 1.0, sizeMult=1.0, mode = 'track',surfaceOffset = 1):

        mHandle = cgmMeta.validateObjArg( CURVES.create_fromName('axis3d', size = (size)*sizeMult), 
                                          'cgmControl',setClass=1)
        mHandle._verifyMirrorable()

        mHandle.doSnapTo(self)
        mHandle.p_parent = mStateNull
        if nameDict:
            RIGGEN.store_and_name(mHandle,nameDict)
            _dCopy = copy.copy(nameDict)
            _dCopy.pop('cgmType')
            mJointLabel = mHandleFactory.addJointLabel(mHandle,NAMETOOLS.returnCombinedNameFromDict(_dCopy))

        else:
            mHandle.doStore('cgmName',tag)
            mHandle.doStore('cgmType','jointHelper')
            mHandle.doName()

        _key = tag
        if k:
            _key = "{0}_{1}".format(tag,k)



        mMasterGroup = mHandle.doGroup(True,True,
                                       asMeta=True,
                                       typeModifier = 'master',
                                       setClass='cgmObject')
        
        if mode == 'track':
            if mPos:
                mc.pointConstraint(mPos.mNode,mMasterGroup.mNode,maintainOffset=False)
        else:
            d_res = DIST.get_closest_point_data(mSurface.mNode,mPos.mNode)
            mMasterGroup.p_position = d_res['position']

        #mHandleFactory.color(mHandle.mNode,side = side, controlType='sub')
        mStateNull.connectChildNode(mHandle, _key+'prerigHelper','block')

        if mSurface:
            _const = mc.normalConstraint(mSurface.mNode, mMasterGroup.mNode,
                                         aimVector = [0,0,1], upVector = [0,1,0],
                                         worldUpObject = self.mNode,
                                         worldUpType = 'objectrotation', 
                                         worldUpVector = [0,1,0])
            mc.delete(_const)
            mHandle.tz = -surfaceOffset
            

        if aimGroup:
            mHandle.doGroup(True,True,
                            asMeta=True,
                            typeModifier = 'aim',
                            setClass='cgmObject')


        return mHandle            
    try:
        _str_func = 'prerig'
        log.debug("|{0}| >>  {1}".format(_str_func,self)+ '-'*80)
        self.blockState = 'prerig'
        _side = self.UTILS.get_side(self)
        
        self.atUtils('module_verify')
        mStateNull = self.UTILS.stateNull_verify(self,'prerig')
        mNoTransformNull = self.atUtils('noTransformNull_verify','prerig')
        self.noTransTemplateNull.v=False
        self.templateNull.template=True
        
        _offset = self.atUtils('get_shapeOffset')/4.0
        _size = MATH.average(self.baseSize[1:])
        _size_base = _size * .25
        _size_sub = _size_base * .5
        
        #mRoot = self.getMessageAsMeta('rootHelper')
        mHandleFactory = self.asHandleFactory()
        vec_self = self.getAxisVector('z+')
        vec_selfUp = self.getAxisVector('y+')        
        #---------------------------------------------------------------
        log.debug("|{0}| >> Gather define/template handles/curves in a useful format...".format(_str_func)) 
        d_pairs = {}
        ml_handles = []
        md_handles = {}
        md_dHandles = {}
        md_dCurves = {}
        md_jointHandles = {}
        ml_jointHandles = []
        ml_defineHandles = []
        for mObj in self.msgList_get('defineSubHandles') + self.msgList_get('templateHandles'):
            md_dHandles[mObj.handleTag] = mObj
            mLabel = mObj.getMessageAsMeta('jointLabel')
            if mLabel:
                mLabel.v=0
            ml_defineHandles.append(mObj)

        for mObj in self.msgList_get('defineCurves') + self.msgList_get('templateCurves') :
            md_dCurves[mObj.handleTag] = mObj
            mObj.template=1        
        
        

        
        
        #Main setup -----------------------------------------------------
        if self.lipSetup:
            log.debug("|{0}| >>  lip setup...".format(_str_func)+ '-'*40)
            log.debug("|{0}| >>  mouthMove...".format(_str_func))
            
            #------------------------------------------------------------
            _d = {'cgmName':'mouthMove',
                  'cgmType':'shapeHelper'}
            
            dist_width = DIST.get_distance_between_points(md_dHandles['cornerFrontLeft'].p_position,
                                                          md_dHandles['cornerFrontRight'].p_position)
            
            mShape = cgmMeta.validateObjArg(CURVES.create_fromName(name='dumbell', 
                                                                  size=3.0, 
                                                                  direction='z+'),'cgmObject',setClass=1)
            mHandleFactory.buildBaseShape('dumbell',baseSize = 3.0, shapeDirection = 'z+')
            mShape.p_parent = mStateNull
            mShape.p_position = DIST.get_pos_by_vec_dist(DIST.get_average_position([md_dHandles['uprPeak'].p_position,
                                                                                    md_dHandles['lwrPeak'].p_position]), 
                                                         vec_self,
                                                         _offset)            
            mHandleFactory.color(mShape.mNode)            
            RIGGEN.store_and_name(mShape,_d)
            
            
            """
            mShape = md_dCurves['uprFront'].doDuplicate(po=False,ic=False)            
            DIST.offsetShape_byVector(mShape.mNode,_offset*2,component='ep',vector=[0,0,1],mode='vector')
            mShape.dagLock(False)
            mShape.p_parent = False
            mShape.v=True
            mShape.template = False"""
            
            _d['cgmType'] = 'handleHelper'
            
            mDag = mHandleFactory.buildBaseShape('sphere',baseSize = dist_width, shapeDirection = 'z+')
            #TRANS.scale_to_boundingBox(mDag.mNode, [_muzzleSize,_muzzleSize,_muzzleSize/2.0])
            mDag.p_parent = mStateNull
            mDag.p_position = DIST.get_pos_by_vec_dist(md_dHandles['uprFront'].p_position, 
                                                         vec_self,
                                                         -dist_width/2.0)            
            mHandleFactory.color(mDag.mNode)
            RIGGEN.store_and_name(mDag,_d)
            
            mDag.doStore('shapeHelper',mShape)
            mShape.doStore('dagHelper',mDag)
            mDag.p_parent = mStateNull
            
            mStateNull.connectChildNode(mDag, 'mouthMove'+'Dag','block')
            md_handles['mouthMove'] = mDag
            md_handles['mouthMoveShape'] = mDag
            
            #lips ---------------------------------------------------------------------------
            log.debug("|{0}| >>  lips...".format(_str_func))
            d_pos={}
            #Get our corners
            log.debug("|{0}| >>  lips|corners...".format(_str_func))
            
            for side in 'left','right':
                
                _side = side.capitalize()
                _l_pos = []
                for h in ['cornerBag','cornerBack','cornerFront','cornerPeak']:
                    _l_pos.append(md_dHandles[h+_side].p_position)
                d_pos['corner'+_side] = DIST.get_average_position(_l_pos)
            
            _d = {'cgmName':'lip',
                  'cgmNameModifier':'lip',
                  'cgmType':'handleHelper'}
            
            _d_dat = {'upper':{'centerH':'uprFront',
                               'mSurf':self.uprLipTemplateLoft,
                               'vec':[0,1,0],
                               'mCrv':md_dCurves['uprFront']},
                      'lower':{'centerH':'lwrFront',
                               'mSurf':self.lwrLipTemplateLoft,
                               'vec':[0,-1,-.5],
                               'noReverse':True,
                               'mCrv':md_dCurves['lwrFront']},                      
                               }
            
            _numControls = self.numLipControls + 2#FOR CORNERS. RESOLVE
            _midIdx = MATH.get_midIndex(_numControls)
            _l_rangeLipsIdx = range(_numControls)
            _l_right = _l_rangeLipsIdx[:_midIdx-1]
            _l_left = _l_rangeLipsIdx[_midIdx:]
            _l_left.reverse()
            
            d_indices = {'left':_l_left,
                         'right':_l_right,
                         'center':[_midIdx]}
            
            for d in 'upper','lower':
                log.debug("|{0}| >>  lip {1}...".format(_str_func,d)+ '-'*20)
                d_dir = copy.copy(_d)
                d_dir['cgmPosition'] = d
                d_use = _d_dat.get(d)
                mCrv = d_use['mCrv']
                vec = d_use['vec']
                
                mDup = mCrv.doDuplicate(po=False)
                mDup.dagLock(False)
                mDup.p_parent = False
                mDup.v=True
                
                DIST.offsetShape_byVector(mDup.mNode,_offset,component='ep',vector=vec,mode='vector')
                l_pos = CURVES.getUSplitList(mDup.mNode,5,markPoints=False,rebuild=1)
                l_pos[0] = d_pos['cornerRight']
                l_pos[-1] = d_pos['cornerLeft']
                
                if MATH.is_even(len(l_pos)):
                    raise ValueError,"Must have odd number lip controls now"
                #Factor our lists
                
                
                #Make our new curve...
                _crvNew = CORERIG.create_at(create='curve',l_pos=l_pos)
                mCrv = cgmMeta.asMeta(_crvNew)
                
                mCrvPos = mCrv.doDuplicate(po=False)
                mCrvNeg = mCrv.doDuplicate(po=False)
                
                DIST.offsetShape_byVector(mCrvPos.mNode,_offset,component='ep',vector=vec,mode='vector')
                DIST.offsetShape_byVector(mCrvNeg.mNode,_offset,component='ep',vector=[v * -1 for v in vec],mode='vector')
                
                #Make our surfaces
                surf_kws = d_use.get('d_surf',{})                
                mSurf = self.UTILS.create_simpleTemplateLoftMesh(self,
                                                                 [mObj.mNode for mObj in [mCrvNeg,
                                                                                          mDup,
                                                                                          mCrvPos]],
                                                                 mStateNull,
                                                                 polyType = 'bezier',
                                                                 noReverse = d_use.get('noReverse',False),
                                                                 #d_rebuild = d.get('rebuild',{}),
                                                                 baseName = 'uprPrerig')
                
                
                d_pairTmp = {}
                
                for side in ['right','center','left']:
                    d_dir['cgmDirection'] = side
                    l_idices = d_indices.get(side)
                    key = 'lip'+d.capitalize()+side.capitalize()
                    
                    if side == 'center':
                        d_dir.pop('cgmDirection')
                    else:
                        d_dir['cgmDirection'] = side

                    """
                    if k == 'mid':
                        _control = 'sub'
                    else:
                        _control = 'main'"""
                        
                    _ml = []
                    _ml_jointHandles = []
                    
                    for i,idx in enumerate(l_idices):
                        if d == 'lower' and i == 0 and side !='center':
                            continue
                        
                        if i:
                            _sizeUse = _size_sub/4.0
                        else:
                            _sizeUse = _size_sub/2.0
                        

                        
                        _tag = "{0}_{1}".format(key,i)
                        
                        if side == 'right':
                            _tagCopy = copy.copy(_tag)
                            _tagMirror = _tagCopy.replace('Right','Left')
                            d_pairTmp[_tagMirror] = _tag
                            d_pairTmp[_tagMirror+'Joint'] = _tag + 'Joint'
                        if side != 'center' and i == 0:
                            d_dir['cgmName'] = 'lipCorner'
                        else:
                            d_dir['cgmName'] = 'lip'
                        
                        
                        #LOC.create(position=l_pos[idx])
                        
                        if side == 'center':
                            mHandle = create_handle(md_dHandles[d_use['centerH']],
                                                    mSurf,
                                                    _tag,None,side,
                                                    mode= 'closest',
                                                    mClosestSurf = mDup,
                                                    size=_sizeUse,
                                                    nameDict = d_dir)
                            mHandle.masterGroup.ry = 0
                        else:
                            mHandle = create_handle(md_dHandles[d_use['centerH']],
                                                    mSurf,
                                                    _tag,None,side,
                                                    mode= 'fixed',
                                                    position = l_pos[idx],
                                                    size=_sizeUse,
                                                    nameDict = d_dir)
                        
                        
                        mJointH = create_jointHelper(None,None,_tag,None,
                                                     side,
                                                     #size= _size_sub,
                                                     nameDict=d_dir,
                                                     sizeMult = .5,aimGroup=0)
                        
                        mJointH.doSnapTo(mHandle.masterGroup)
                        mHandle.masterGroup.p_parent = mJointH
                        
                        _ml_jointHandles.append(mJointH)
                        _ml.append(mHandle)
                        md_handles[_tag] = mHandle
                        md_handles[_tag+'Joint'] = mJointH
                        ml_handles.append(mHandle)
                        ml_jointHandles.append(mJointH)
                    
                    mStateNull.msgList_connect('{0}PrerigHandles'.format(key),_ml)
                    mStateNull.msgList_connect('{0}PrerigJointHandles'.format(key),_ml_jointHandles)
                    
                d_pairs.update(d_pairTmp)
                mSurf.delete()
                for mObj in [mCrvNeg,mDup,mCrvPos,mCrv]:
                    mObj.delete() 
            
            
            
            
        """
            #Aim pass ------------------------------------------------------------------------
            for side in ['left','right']:
                #Handles -------
                ml = md_handles['brow'][side]
                for i,mObj in enumerate(ml):
                    mObj.mirrorIndex = idx_side + i
                    mObj.mirrorAxis = "translateX,rotateY,rotateZ"
        
                    if side == 'left':
                        _aim = [-1,0,0]
                        mObj.mirrorSide = 1                    
                    else:
                        _aim = [1,0,0]
                        mObj.mirrorSide = 2
        
                    _up = [0,0,1]
                    _worldUp = [0,0,1]
        
                    if i == 0:
                        mAimGroup = mObj.aimGroup
                        mc.aimConstraint(md_handles['browCenter'][0].masterGroup.mNode,
                                         mAimGroup.mNode,
                                         maintainOffset = False, weight = 1,
                                         aimVector = _aim,
                                         upVector = _up,
                                         worldUpVector = _worldUp,
                                         worldUpObject = mObj.masterGroup.mNode,
                                         worldUpType = 'objectRotation' )                                
                    else:
        
                        mAimGroup = mObj.aimGroup
                        mc.aimConstraint(ml[i-1].masterGroup.mNode,
                                         mAimGroup.mNode,
                                         maintainOffset = False, weight = 1,
                                         aimVector = _aim,
                                         upVector = _up,
                                         worldUpVector = _worldUp,
                                         worldUpObject = mObj.masterGroup.mNode,
                                         worldUpType = 'objectRotation' )
        
                mStateNull.msgList_connect('brow{0}PrerigHandles'.format(side.capitalize()), ml)            
                """
        
        
        if self.muzzleSetup:
            log.debug("|{0}| >>  Muzzle setup...".format(_str_func)+ '-'*40)
            
            _d_name = {'cgmName':'muzzle',
                       'cgmType':'jointHelper'}
            mHandle = create_jointHelper(None,None,'muzzle',None,
                                         'center',
                                         size= _size_sub,
                                         nameDict=_d_name,sizeMult = 1.0,aimGroup=0)
            _muzzleSize = _offset * 2.0
            pMuzzleBase = md_dHandles['bridge'].p_position

            
            pMuzzleBase = DIST.get_pos_by_vec_dist(pMuzzleBase, 
                                                   vec_selfUp,
                                                   _offset*2)

            mHandle.p_position = DIST.get_pos_by_vec_dist(pMuzzleBase, 
                                                                           vec_self,
                                                                           -_offset*4)
            
            mStateNull.connectChildNode(mHandle, 'muzzle'+'JointHelper','block')
            
            mShape = mHandleFactory.buildBaseShape('pyramid',baseSize = _muzzleSize, shapeDirection = 'z+')
            TRANS.scale_to_boundingBox(mShape.mNode, [_muzzleSize,_muzzleSize,_muzzleSize/2.0])
            mShape.p_parent = mStateNull
            mShape.p_position = DIST.get_pos_by_vec_dist(pMuzzleBase, 
                                                         vec_self,
                                                         _offset*2)
            
            _d_name['cgmType'] = 'shapeHelper'
            RIGGEN.store_and_name(mShape,_d_name)
            mHandleFactory.color(mShape.mNode,side = 'center', controlType='main')
            mHandle.doStore('shapeHelper',mShape)
            mShape.doStore('dagHelper',mHandle)            
            
            ml_handles.append(mShape)
            
            md_handles['muzzle'] = mShape
            md_handles['muzzleJoint'] = mHandle              
            ml_jointHandles.append(mHandle)
            
            mShape.p_parent = mHandle
            
            md_jointHandles['muzzle'] = mHandle
            
        if self.jawSetup:
            log.debug("|{0}| >>  Jaw setup...".format(_str_func)+ '-'*40)
        
            _d_name = {'cgmName':'jaw',
                       'cgmType':'jointHelper'}            
            md_jointHandles['jawLower'] = create_jointHelper(None,None,'jawLower',None,
                                                             'center',nameDict=_d_name,
                                                             size= _size_sub,
                                                             sizeMult = 2.0,aimGroup=0)
            md_jointHandles['jawLower'].p_position = DIST.get_average_position([md_dHandles['jawEdgeRightMid'].p_position,
                                                                                md_dHandles['jawEdgeLeftMid'].p_position])
        
        
            l_jaw = ['jawEdgeRightMid', 'jawRight','jawLineRightMid','chinRight','chin',
                     'chinLeft','jawLineLeftMid', 'jawLeft', 'jawEdgeLeftMid']
            
            _crv = CORERIG.create_at(create='curveLinear',l_pos=[md_dHandles[k].p_position for k in l_jaw])
            #md_dCurves['jawLine'].mNode
            _shape = mc.offsetCurve(_crv,rn=0,cb=1,st=1,cl=1,cr=0,ch=0,
                                    d=1,tol=.0001,sd=1,ugn=0,
                                    distance =-_offset)
            mc.delete(_crv)
        
            mShape = cgmMeta.validateObjArg(_shape[0],'cgmControl',setClass=1)
            mShape.p_parent = mStateNull
        
            _d_name['cgmType'] = 'shapeHelper'
            RIGGEN.store_and_name(mShape,_d_name)
            mHandleFactory.color(mShape.mNode,side = 'center', controlType='main')
            md_jointHandles['jawLower'].doStore('shapeHelper',mShape)
            mShape.doStore('dagHelper', md_jointHandles['jawLower'])
        
            mStateNull.connectChildNode(md_jointHandles['jawLower'], 'jaw'+'JointHelper','block')
            mStateNull.connectChildNode(mShape, 'jaw'+'ShapeHelper','block')
            ml_jointHandles.append(md_jointHandles['jawLower'])            
            ml_handles.append(mShape)
        
            md_handles['jaw'] = mShape
            md_handles['jawJoint'] = md_jointHandles['jawLower']            

        
        if self.noseSetup:
            log.debug("|{0}| >>  noseSetup".format(_str_func)+ '-'*40)
            str_noseSetup = self.getEnumValueString('noseSetup')
        
            if str_noseSetup == 'simple':
                log.debug("|{0}| >>  noseSetup: {1}".format(_str_func,str_noseSetup))
        
                mSurf =  self.noseTemplateLoft
        
                _d_name = {'cgmName':'nose',
                           'cgmType':'handleHelper'}
                
                
                #NoseBase ----------------------------------------------------------------------
                log.debug("|{0}| >>  {1}...".format(_str_func,'noseTip'))
                _tag = 'noseBase'
                mDefHandle = md_dHandles['noseTip']
                _dTmp = copy.copy(_d_name)
                _dTmp['cgmName'] = 'noseBase'
                #_dTmp['cgmDirection'] = side
                mHandle = create_handle(mDefHandle,mSurf,_tag,None,None,controlShape = 'loftWideDown',
                                        size= _size_sub*2.0,
                                        controlType = 'main',
                                        nameDict = _d_name,
                                        surfaceOffset=-_offset/2.0, mode = 'closestPoint')
                ml_handles.append(mHandle)
            
                mStateNull.doStore(_tag+'ShapeHelper',mHandle)
                md_handles[_tag] = mHandle
               
            
                #Joint handle
                _dTmp['cgmType'] = 'jointHandle'
                mJointHelper = create_jointHelper(mHandle,mSurf,_tag,None,None,nameDict=_dTmp,mode='closestPoint',surfaceOffset=0)
                mStateNull.doStore(_tag+'JointHelper',mJointHelper)
                
                mJointHelper.masterGroup.p_position = DIST.get_average_position([md_dHandles['nostrilBaseLeft'].p_position,
                                                                            md_dHandles['nostrilBaseRight'].p_position])                
                mHandle.masterGroup.p_position = DIST.get_average_position([md_dHandles['bulbBaseLeft'].p_position,
                                                                                 md_dHandles['bulbBaseRight'].p_position])                 
                md_handles[_tag+'Joint'] = mJointHelper
                ml_jointHandles.append(mJointHelper)
                
                
                
                #NoseTip ----------------------------------------------------------------------
                if self.numJointsNoseTip:
                    log.debug("|{0}| >>  {1}...".format(_str_func,'noseTip'))
                    _tag = 'noseTip'
                    mDefHandle = md_dHandles['noseTip']
                    _dTmp = copy.copy(_d_name)
                    _dTmp['cgmName'] = 'noseTip'
                    #_dTmp['cgmDirection'] = side
                    mHandle = create_handle(mDefHandle,mSurf,_tag,None,None,controlShape = 'semiSphere',
                                            size= _size_sub,
                                            controlType = 'sub',
                                            nameDict = _d_name,
                                            surfaceOffset=_offset/2.0, mode = 'closestPoint')
                    ml_handles.append(mHandle)
                
                    mStateNull.doStore(_tag+'ShapeHelper',mHandle)
                
                    #Joint handle
                    _dTmp['cgmType'] = 'jointHandle'
                    mJointHelper = create_jointHelper(mHandle,mSurf,_tag,None,None,nameDict=_dTmp,mode='closestPoint',surfaceOffset=_offset*2.0)
                    mStateNull.doStore(_tag+'JointHelper',mJointHelper)
                    
                    md_handles[_tag] = mHandle
                    md_handles[_tag+'Joint'] = mJointHelper
                    ml_jointHandles.append(mJointHelper)
                    
                
                #Nostrils -------------------------------------------------------------------
                if self.numJointsNostril:
                    d_pairs['nostrilLeft'] = 'nostrilRight'
                    d_pairs['nostrilLeftJoint'] = 'nostrilRightJoint'
                    for side in ['left','right']:
                        #Get our position
                        _tag = 'nostril'+side.capitalize()
                        log.debug("|{0}| >>  {1}...".format(_str_func,_tag))
            
                        mDefHandle = md_dHandles['nostrilFront'+side.capitalize()]
                        _dTmp = copy.copy(_d_name)
                        _dTmp['cgmName'] = 'nostril'
                        _dTmp['cgmDirection'] = side
                        mHandle = create_handle(mDefHandle,mSurf,_tag,None,side,controlShape = 'semiSphere',
                                                size= _size_sub/2.0,
                                                controlType = 'sub',
                                                nameDict = _d_name,
                                                surfaceOffset=_offset/2.0, mode = 'closestPoint')
                        ml_handles.append(mHandle)
            
                        mStateNull.doStore(_tag+'ShapeHelper',mHandle)
            
                        #Joint handle
                        _dTmp['cgmType'] = 'jointHandle'
                        mJointHelper = create_jointHelper(mHandle,mSurf,_tag,None,side,nameDict=_dTmp,mode='closestPoint',surfaceOffset=_offset)
                        mStateNull.doStore(_tag+'JointHelper',mJointHelper)
                        ml_jointHandles.append(mJointHelper)
                        
                        md_handles[_tag] = mHandle
                        md_handles[_tag+'Joint'] = mJointHelper                        
            else:
                raise ValueError,"Invalid noseSetup: {0}".format(str_noseSetup)
        
        
        if self.cheekSetup:
            log.debug("|{0}| >>  Cheek setup".format(_str_func)+ '-'*40)
            str_cheekSetup = self.getEnumValueString('cheekSetup')
            
            if str_cheekSetup == 'single':
                log.debug("|{0}| >>  cheekSetup: {1}".format(_str_func,str_cheekSetup))
                
                mSurf =  self.jawTemplateLoft
                
                _d_name = {'cgmName':'cheek',
                           'cgmType':'handleHelper'}
                
                d_pairs['cheekLeft'] = 'cheekRight'
                d_pairs['cheekLeftJoint'] = 'cheekRightJoint'                
                
                for side in ['left','right']:
                    #Get our position
                    _tag = 'cheek'+side.capitalize()
                    log.debug("|{0}| >>  {1}...".format(_str_func,_tag))
                    
                    mDefHandle = md_dHandles[_tag]
                    _dTmp = copy.copy(_d_name)
                    _dTmp['cgmDirection'] = side
                    mHandle = create_handle(mDefHandle,mSurf,_tag,None,side,controlShape = 'semiSphere',
                                            size= _size_sub,
                                            controlType = 'sub',nameDict = _d_name,surfaceOffset=_offset, mode = 'closestPoint')
                    ml_handles.append(mHandle)
                    
                    mStateNull.doStore(_tag+'ShapeHelper',mHandle)
                    
                    #Joint handle
                    _dTmp['cgmType'] = 'jointHandle'
                    mJointHelper = create_jointHelper(mHandle,mSurf,_tag,None,
                                                      side,
                                                      size= _size_sub,
                                                      nameDict=_dTmp,mode='closestPoint',surfaceOffset=_offset)
                    mStateNull.doStore(_tag+'JointHelper',mJointHelper)
                    md_handles[_tag] = mHandle
                    md_handles[_tag+'Joint'] = mJointHelper
                    ml_jointHandles.append(mJointHelper)
                    
                    mHandle.p_parent = mJointHelper
                    
            else:
                raise ValueError,"Invalid cheekSetup: {0}".format(str_cheekSetup)
        
        
        if self.chinSetup:
            log.debug("|{0}| >>  Chin setup".format(_str_func)+ '-'*40)
            str_chinSetup = self.getEnumValueString('chinSetup')
            
            if str_cheekSetup == 'single':
                log.debug("|{0}| >>  chin: {1}".format(_str_func,str_chinSetup))
                
                mSurf =  self.lwrLipTemplateLoft
                
                
                _d_name = {'cgmName':'chin',
                           'cgmType':'handleHelper'}
                side = 'center'
                _tag = 'chin'
                mDefHandle = md_dHandles[_tag]
                _dTmp = copy.copy(_d_name)
                mHandle = create_handle(mDefHandle,mSurf,_tag,None,side,controlShape = 'semiSphere',
                                        size= _size_sub,
                                        controlType = 'sub',nameDict = _d_name,surfaceOffset=_offset, mode = 'closestPoint')
                ml_handles.append(mHandle)
            
                mStateNull.doStore(_tag+'ShapeHelper',mHandle)
            
                #Joint handle
                _dTmp['cgmType'] = 'jointHandle'
                mJointHelper = create_jointHelper(mHandle,mSurf,_tag,None,
                                                  side,
                                                  size= _size_sub,
                                                  nameDict=_dTmp,mode='closestPoint',surfaceOffset=_offset)
                mStateNull.doStore(_tag+'JointHelper',mJointHelper)
                md_handles[_tag] = mHandle
                md_handles[_tag+'Joint'] = mJointHelper
                ml_jointHandles.append(mJointHelper)                
                
                
                mHandle.p_parent = mJointHelper
                
            else:
                raise ValueError,"Invalid cheekSetup: {0}".format(str_cheekSetup)
            
            
        
        #Mirror indexing -------------------------------------
        log.debug("|{0}| >> Mirror Indexing...".format(_str_func)+'-'*40) 
    
        idx_ctr = 0
        idx_side = 0
        d = {}
    
        for tag,mHandle in md_handles.iteritems():
            if mHandle in ml_defineHandles:
                continue
            try:mHandle._verifyMirrorable()
            except:
                mHandle = cgmMeta.validateObjArg(mHandle,'cgmControl',setClass=1)
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
            try:
                md_handles[k].mirrorSide = 1
                md_handles[m].mirrorSide = 2
                md_handles[k].mirrorIndex = idx_side
                md_handles[m].mirrorIndex = idx_side
                md_handles[k].doStore('mirrorHandle',md_handles[m])
                md_handles[m].doStore('mirrorHandle',md_handles[k])
                idx_side +=1        
            except Exception,err:
                log.error('Mirror error: {0}'.format(err))        

        self.msgList_connect('prerigHandles', ml_handles)
        self.msgList_connect('jointHandles', ml_jointHandles)
        
        #pprint.pprint(vars())
        return
        
        ml_handles = []
        md_handles = {'brow':{'center':[],
                              'left':[],
                              'right':[]}}
        md_jointHandles = {'brow':{'center':[],
                              'left':[],
                              'right':[]}}

        
        #Get base dat =============================================================================    
        mBBHelper = self.bbHelper
        mBrowLoft = self.getMessageAsMeta('browTemplateLoft')
        
        _size = MATH.average(self.baseSize[1:])
        _size_base = _size * .25
        _size_sub = _size_base * .5
        
        idx_ctr = 0
        idx_side = 0
        
        
        
        #Handles =====================================================================================
        log.debug("|{0}| >> Brow Handles..".format(_str_func)+'-'*40)
        
        _d = {'cgmName':'browCenter',
              'cgmType':'handleHelper'}
        
        mBrowCenterDefine = self.defineBrowcenterHelper
        md_handles['browCenter'] = [create_handle(mBrowCenterDefine,mBrowLoft,
                                                  'browCenter',None,'center',nameDict = _d)]
        md_handles['brow']['center'].append(md_handles['browCenter'])
        md_handles['browCenter'][0].mirrorIndex = idx_ctr
        idx_ctr +=1
        mStateNull.msgList_connect('browCenterPrerigHandles',md_handles['browCenter'])
        
        _d_nameHandleSwap = {'start':'inner',
                             'end':'outer'}
        for tag in ['browLeft','browRight']:
            _d['cgmName'] = tag
        
            for k in ['start','mid','end']:
                _d['cgmNameModifier'] = _d_nameHandleSwap.get(k,k)
                
                if 'Left' in tag:
                    _side = 'left'
                elif 'Right' in tag:
                    _side = 'right'
                else:
                    _side = 'center'
                
                if _side in ['left','right']:
                    _d['cgmDirection'] = _side
                    
                if k == 'mid':
                    _control = 'sub'
                else:
                    _control = 'main'
                    
                mTemplateHelper = self.getMessageAsMeta(tag+k.capitalize()+'templateHelper')
                
                mHandle = create_handle(mTemplateHelper,mBrowLoft,tag,k,_side,controlType = _control,nameDict = _d)
                md_handles['brow'][_side].append(mHandle)
                ml_handles.append(mHandle)                
            mStateNull.msgList_connect('{0}PrerigHandles'.format(tag),md_handles['brow'][_side])


        #Joint helpers ------------------------
        log.debug("|{0}| >> Joint helpers..".format(_str_func)+'-'*40)
        _d = {'cgmName':'brow',
              'cgmDirection':'center',
              'cgmType':'jointHelper'}        
        
        mFullCurve = self.getMessageAsMeta('browLineloftCurve')
        md_jointHandles['browCenter'] = [create_jointHelper(mBrowCenterDefine,mBrowLoft,'center',None,
                                                            'center',nameDict=_d)]
        md_jointHandles['brow']['center'].append(md_jointHandles['browCenter'])
        md_jointHandles['browCenter'][0].mirrorIndex = idx_ctr
        idx_ctr +=1
        mStateNull.msgList_connect('browCenterJointHandles',md_jointHandles['browCenter'])
        

        for tag in ['browLeft','browRight']:
            mCrv = self.getMessageAsMeta("{0}JointCurve".format(tag))
            if 'Left' in tag:
                _side = 'left'
            elif 'Right' in tag:
                _side = 'right'
            else:
                _side = 'center'            
            
            if _side in ['left','right']:
                _d['cgmDirection'] = _side
                
            _factor = 100/(self.numJointsBrow-1)
            
            for i in range(self.numJointsBrow):
                log.debug("|{0}| >>  Joint Handle: {1}|{2}...".format(_str_func,tag,i))            
                _d['cgmIterator'] = i
                
                mLoc = cgmMeta.asMeta(self.doCreateAt())
                mLoc.rename("{0}_{1}_jointTrackHelper".format(tag,i))
            
                #self.connectChildNode(mLoc, tag+k.capitalize()+'templateHelper','block')
                mPointOnCurve = cgmMeta.asMeta(CURVES.create_pointOnInfoNode(mCrv.mNode,
                                                                             turnOnPercentage=True))
            
                mPointOnCurve.parameter = (_factor * i)/100.0
                mPointOnCurve.doConnectOut('position',"{0}.translate".format(mLoc.mNode))
            
                mLoc.p_parent = mNoTransformNull
                
            
                res = DIST.create_closest_point_node(mLoc.mNode,mFullCurve.mNode,True)
                #mLoc = cgmMeta.asMeta(res[0])
                mTrackLoc = cgmMeta.asMeta(res[0])
                mTrackLoc.p_parent = mNoTransformNull
                mTrackLoc.v=False
                
                mHandle = create_jointHelper(mTrackLoc,mBrowLoft,tag,i,_side,nameDict=_d)
                md_jointHandles['brow'][_side].append(mHandle)
                ml_handles.append(mHandle)
                
            
        
        #Aim pass ------------------------------------------------------------------------
        for side in ['left','right']:
            #Handles -------
            ml = md_handles['brow'][side]
            for i,mObj in enumerate(ml):
                mObj.mirrorIndex = idx_side + i
                mObj.mirrorAxis = "translateX,rotateY,rotateZ"
                
                if side == 'left':
                    _aim = [-1,0,0]
                    mObj.mirrorSide = 1                    
                else:
                    _aim = [1,0,0]
                    mObj.mirrorSide = 2
                    
                _up = [0,0,1]
                _worldUp = [0,0,1]
                
                if i == 0:
                    mAimGroup = mObj.aimGroup
                    mc.aimConstraint(md_handles['browCenter'][0].masterGroup.mNode,
                                     mAimGroup.mNode,
                                     maintainOffset = False, weight = 1,
                                     aimVector = _aim,
                                     upVector = _up,
                                     worldUpVector = _worldUp,
                                     worldUpObject = mObj.masterGroup.mNode,
                                     worldUpType = 'objectRotation' )                                
                else:

                    mAimGroup = mObj.aimGroup
                    mc.aimConstraint(ml[i-1].masterGroup.mNode,
                                     mAimGroup.mNode,
                                     maintainOffset = False, weight = 1,
                                     aimVector = _aim,
                                     upVector = _up,
                                     worldUpVector = _worldUp,
                                     worldUpObject = mObj.masterGroup.mNode,
                                     worldUpType = 'objectRotation' )
                    
            mStateNull.msgList_connect('brow{0}PrerigHandles'.format(side.capitalize()), ml)
            
        idx_side = idx_side + i + 1
        log.info(idx_side)
        
        for side in ['left','right']:
            #Joint Helpers ----------------
            ml = md_jointHandles['brow'][side]
            for i,mObj in enumerate(ml):
                if side == 'left':
                    _aim = [1,0,0]
                    mObj.mirrorSide = 1
                else:
                    _aim = [-1,0,0]
                    mObj.mirrorSide = 2
                    
                mObj.mirrorIndex = idx_side + i
                mObj.mirrorAxis = "translateX,rotateY,rotateZ"
                _up = [0,0,1]
                _worldUp = [0,0,1]
                if mObj == ml[-1]:
                    _vAim = [_aim[0]*-1,_aim[1],_aim[2]]
                    mAimGroup = mObj.aimGroup
                    mc.aimConstraint(ml[i-1].masterGroup.mNode,
                                     mAimGroup.mNode,
                                     maintainOffset = False, weight = 1,
                                     aimVector = _vAim,
                                     upVector = _up,
                                     worldUpVector = _worldUp,
                                     worldUpObject = mObj.masterGroup.mNode,
                                     worldUpType = 'objectRotation' )                    
                else:
                    mAimGroup = mObj.aimGroup
                    mc.aimConstraint(ml[i+1].masterGroup.mNode,
                                     mAimGroup.mNode,
                                     maintainOffset = False, weight = 1,
                                     aimVector = _aim,
                                     upVector = _up,
                                     worldUpVector = _worldUp,
                                     worldUpObject = mObj.masterGroup.mNode,
                                     worldUpType = 'objectRotation' )
                    
            mStateNull.msgList_connect('brow{0}JointHandles'.format(side.capitalize()), ml)
        
        #Mirror setup --------------------------------
        """
        for mHandle in ml_handles:
            mHandle._verifyMirrorable()
            _str_handle = mHandle.p_nameBase
            if 'Center' in _str_handle:
                mHandle.mirrorSide = 0
                mHandle.mirrorIndex = idx_ctr
                idx_ctr +=1
            mHandle.mirrorAxis = "translateX,rotateY,rotateZ"
    
        #Self mirror wiring -------------------------------------------------------
        for k,m in _d_pairs.iteritems():
            md_handles[k].mirrorSide = 1
            md_handles[m].mirrorSide = 2
            md_handles[k].mirrorIndex = idx_side
            md_handles[m].mirrorIndex = idx_side
            md_handles[k].doStore('mirrorHandle',md_handles[m].mNode)
            md_handles[m].doStore('mirrorHandle',md_handles[k].mNode)
            idx_side +=1        """
        
        #Close out ======================================================================================
        self.msgList_connect('prerigHandles', ml_handles)
        
        self.blockState = 'prerig'
        return
    
    
    except Exception,err:
        cgmGEN.cgmExceptCB(Exception,err)
        
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
        raise ValueError,"No rigNull connected"
    
    mPrerigNull = self.prerigNull
    if not mPrerigNull:
        raise ValueError,"No prerig null"
    
    mRoot = self.UTILS.skeleton_getAttachJoint(self)
    
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
    


    if self.jawSetup:
        mObj = mPrerigNull.getMessageAsMeta('jaw'+'JointHelper')
        mJaw = create_jointFromHandle(mObj,mRoot)
        mPrerigNull.doStore('jawJoint',mJaw)
        ml_joints.append(mJaw)
        
    if self.lipSetup:
        str_lipSetup = self.getEnumValueString('lipSetup')
        log.debug("|{0}| >>  lipSetup...".format(_str_func)+ '-'*40)
        
        _d_lip = {'cgmName':'lip'}
        
        for d in 'upper','lower':
            log.debug("|{0}| >>  lip {1}...".format(_str_func,d)+ '-'*20)
            d_dir = copy.copy(_d_lip)
            d_dir['cgmPosition'] = d
        
            for side in ['right','center','left']:
                d_dir['cgmDirection'] = side
                key = 'lip'+d.capitalize()+side.capitalize()        
                mHandles = mPrerigNull.msgList_get('{0}PrerigJointHandles'.format(key))
                ml = []
                for mHandle in mHandles:
                    mJnt = create_jointFromHandle(mHandle,mJaw)
                    ml.append(mJnt)
                    
                mPrerigNull.msgList_connect('{0}Joints'.format(key),ml)
                ml_joints.extend(ml)
        
    
    if self.chinSetup:
        log.debug("|{0}| >>  chinSetup...".format(_str_func)+ '-'*40)
        mObj = mPrerigNull.getMessageAsMeta('chin'+'JointHelper')
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
            mNoseBase = create_jointFromHandle(mPrerigNull.getMessageAsMeta('{0}JointHelper'.format(_tag)),
                                               mRoot)
            mPrerigNull.doStore('{0}Joint'.format(_tag),mNoseBase)
            ml_joints.append(mNoseBase)
            
            #NoseTip ----------------------------------------------------------------------
            if self.numJointsNoseTip:
                log.debug("|{0}| >>  {1}...".format(_str_func,'noseTip'))
                _tag = 'noseTip'
                mNoseTip = create_jointFromHandle(mPrerigNull.getMessageAsMeta('{0}JointHelper'.format(_tag)),
                                                  mNoseBase)
                mPrerigNull.doStore('{0}Joint'.format(_tag),mNoseTip)
                ml_joints.append(mNoseTip)

            #Nostrils -------------------------------------------------------------------
            if self.numJointsNostril:
                for side in ['left','right']:
                    _tag = 'nostril'+side.capitalize()
                    log.debug("|{0}| >>  {1}...".format(_str_func,_tag))
                    mJnt = create_jointFromHandle(mPrerigNull.getMessageAsMeta('{0}JointHelper'.format(_tag)),
                                                  mNoseBase)
                    mPrerigNull.doStore('{0}Joint'.format(_tag),mJnt)
                    ml_joints.append(mJnt)
                    
        else:
            raise ValueError,"Invalid noseSetup: {0}".format(str_noseSetup)
        
    if self.cheekSetup:
        log.debug("|{0}| >>  Cheeksetup".format(_str_func)+ '-'*40)
        str_cheekSetup = self.getEnumValueString('cheekSetup')
        if str_cheekSetup == 'single':
            log.debug("|{0}| >>  cheekSetup: {1}".format(_str_func,str_cheekSetup))
            
            for side in ['left','right']:
                _tag = 'cheek'+side.capitalize()
                log.debug("|{0}| >>  {1}...".format(_str_func,_tag))
                mJnt = create_jointFromHandle(mPrerigNull.getMessageAsMeta('{0}JointHelper'.format(_tag)),
                                              mJaw)
                mPrerigNull.doStore('{0}Joint'.format(_tag),mJnt)
                ml_joints.append(mJnt)
                
        else:
            raise ValueError,"Invalid cheekSetup: {0}".format(str_cheekSetup)
                
    #>> ===========================================================================
    mRigNull.msgList_connect('moduleJoints', ml_joints)
    self.msgList_connect('moduleJoints', ml_joints)
    
    pprint.pprint(ml_joints)

    for mJnt in ml_joints:
        mJnt.displayLocalAxis = 1
        mJnt.radius = _radius
    for mJnt in ml_joints:mJnt.rotateOrder = 5
        
    return ml_joints    
    
   
    

    
    
    
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

d_preferredAngles = {}#In terms of aim up out for orientation relative values, stored left, if right, it will invert
d_rotateOrders = {}

#Rig build stuff goes through the rig build factory ------------------------------------------------------
@cgmGEN.Timer
def rig_prechecks(self):
    _str_func = 'rig_prechecks'
    log.debug(cgmGEN.logString_start(_str_func))

    mBlock = self.mBlock
    
    str_faceType = mBlock.getEnumValueString('faceType')
    if str_faceType not in ['default']:
        self.l_precheckErrors.append("faceType setup not completed: {0}".format(str_faceType))

    str_jawSetup = mBlock.getEnumValueString('jawSetup')
    if str_jawSetup not in ['none','simple']:
        self.l_precheckErrors.append("Jaw setup not completed: {0}".format(str_jawSetup))
    
    str_muzzleSetup = mBlock.getEnumValueString('muzzleSetup')
    if str_muzzleSetup not in ['none','simple']:
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
        
    str_lipSetup = mBlock.getEnumValueString('lipSetup')
    if str_lipSetup not in ['none','default']:
        self.l_precheckErrors.append("Lip setup not completed: {0}".format(str_lipSetup))
        
    str_chinSetup = mBlock.getEnumValueString('chinSetup')
    if str_chinSetup not in ['none','single']:
        self.l_precheckErrors.append("Chin setup not completed: {0}".format(str_chinSetup))
                
    if mBlock.scaleSetup:
        self.l_precheckErrors.append("Scale setup not complete")

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
    self.mPrerigNull = mPrerigNull
    ml_handleJoints = mPrerigNull.msgList_get('handleJoints')
    mMasterNull = self.d_module['mMasterNull']

    
    self.b_scaleSetup = mBlock.scaleSetup
    
    
    for k in ['jaw','muzzle','nose','nostril','cheek','bridge','chin',
              'lip','lipSeal','teeth','tongue','uprJaw']:
        _tag = "{0}Setup".format(k)
        self.__dict__['str_{0}'.format(_tag)] = False
        _v = mBlock.getEnumValueString(_tag)
        if _v != 'none':
            self.__dict__['str_{0}'.format(_tag)] = _v
        log.debug("|{0}| >> self.str_{1} = {2}".format(_str_func,_tag,self.__dict__['str_{0}'.format(_tag)]))    
    
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


@cgmGEN.Timer
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
    
    def doSingleJoint(tag,mParent = None):
        log.debug("|{0}| >> gathering {1}...".format(_str_func,tag))            
        mJntSkin = mPrerigNull.getMessageAsMeta('{0}Joint'.format(tag))
    
        mJntRig = mJntSkin.getMessageAsMeta('rigJoint')
        mJntDriver = mJntSkin.getMessageAsMeta('driverJoint')
    
        if mParent is not None:
            mJntDriver.p_parent = mParent
    
        md_skinJoints[t] = mJntSkin
        md_rigJoints[t] = mJntRig
        md_driverJoints[t] = mJntDriver
        md_handleShapes[t] = mPrerigNull.getMessageAsMeta('{0}ShapeHelper'.format(t))
        
    #Jaw ---------------------------------------------------------------
    if self.str_jawSetup:
        log.debug("|{0}| >> jaw...".format(_str_func))
        mJntSkin = mPrerigNull.getMessageAsMeta('jawJoint')
        mJntRig = mJntSkin.getMessageAsMeta('rigJoint')
        mJntDriver = mJntSkin.getMessageAsMeta('driverJoint')
        
        md_skinJoints['jaw'] = mJntSkin
        md_rigJoints['jaw'] = mJntRig
        md_driverJoints['jaw'] = mJntDriver

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
        
        for t in ['noseBase','noseTip','nostrilLeft','nostrilRight']:
            mParent = None
            if t == 'noseBase':
                mParent = False
            doSingleJoint(t,mParent)
            
    if self.str_cheekSetup:
        log.debug("|{0}| >> cheek...".format(_str_func))
        for t in ['cheekLeft','cheekRight']:
            doSingleJoint(t,False)
            

    #Processing  Handles ================================================================================
    log.debug("|{0}| >> Processing...".format(_str_func)+ '-'*40)
    if self.str_lipSetup:
        log.debug("|{0}| >>  lip ".format(_str_func)+ '-'*20)
        
        for d in 'upper','lower':
            log.debug("|{0}| >>  lip {1}...".format(_str_func,d)+ '-'*5)
            _k = 'lip'+d.capitalize()
            for _d in md_skinJoints,md_handles,md_handleShapes,md_rigJoints,md_segJoints:
                if not _d.get(_k):
                    _d[_k] = {}

            for side in ['right','center','left']:
                key = 'lip'+d.capitalize()+side.capitalize()
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
                
                
                mHandles = mPrerigNull.msgList_get('{0}PrerigJointHandles'.format(key))
                mHelpers = mPrerigNull.msgList_get('{0}PrerigHandles'.format(key))
                
                ml = []
                for ii,mHandle in enumerate(mHandles):
                    mJnt = create_jointFromHandle(mHandle,False,'handle')
                    ml.append(mJnt)
                    
                    if d == 'upper' and side in ['right','left'] and ii == 0:
                        log.debug("|{0}| >>  influenceJoints for {1}...".format(_str_func,mHandle))
                        for k in 'upper','lower':
                            mSub = create_jointFromHandle(mHandle,False,'{0}Influence'.format(k))
                            mSub.doStore('mClass','cgmObject')
                            mSub.p_parent = mJnt
                            mJnt.doStore('{0}Influence'.format(k),mSub)
                            ml_jointsToConnect.append(mSub)
                            ml_jointsToHide.append(mSub)
                
                ml_jointsToHide.extend(ml)
                md_handles[_k][side] = ml
                md_handleShapes[_k][side] = mHelpers
            log.debug(cgmGEN._str_subLine)
                

    self.md_rigJoints = md_rigJoints
    self.md_skinJoints = md_skinJoints
    self.md_segJoints = md_segJoints
    self.md_handles = md_handles
    self.md_handleShapes = md_handleShapes
    self.md_driverJoints = md_driverJoints
    
    #...joint hide -----------------------------------------------------------------------------------
    for mJnt in ml_jointsToHide:
        try:mJnt.drawStyle =2
        except:mJnt.radius = .00001
    
    pprint.pprint(vars())
    #...connect... 
    self.fnc_connect_toRigGutsVis( ml_jointsToConnect )        
    return

@cgmGEN.Timer
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
            
        if self.md_rigJoints.get('chin'):
            log.debug("|{0}| >> chin setup...".format(_str_func)+ '-'*40)
            mChin = self.md_driverJoints.get('chin')
            CORERIG.shapeParent_in_place(mChin.mNode, mPrerigNull.getMessageAsMeta('chinShapeHelper').mNode)
            
            mRigNull.doStore('controlChin',mChin)
            log.debug(cgmGEN._str_subLine)
                
        if self.str_muzzleSetup:
            log.debug("|{0}| >> Muzzle setup...".format(_str_func)+ '-'*40)
            mMuzzleDagHelper = mPrerigNull.getMessageAsMeta('muzzleJointHelper')
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
                
        
        if self.str_noseSetup:
            log.debug("|{0}| >> nose setup...".format(_str_func)+ '-'*40)
            
            for k in ['noseBase','noseTip','nostrilLeft','nostrilRight']:
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
            for k in 'lipLower','lipUpper':
                log.debug("|{0}| >> {1}...".format(_str_func,k)+ '-'*40)
                for side,ml in self.md_handles[k].iteritems():
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
        for k,d in self.md_rigJoints.iteritems():
            log.debug("|{0}| >> {1}...".format(_str_func,k)+ '-'*40)
            
            if VALID.isListArg(d):
                for i,mHandle in enumerate(d):
                    log.debug("|{0}| >> {1}...".format(_str_func,mHandle))
                    side = mHandle.getMayaAttr('cgmDirection') or False
                    crv = CURVES.create_fromName(name='cube',
                                                 direction = 'z+',
                                                 size = mHandle.radius)
                    SNAP.go(crv,mHandle.mNode)
                    mHandleFactory.color(crv,side=side,controlType='sub')
                    CORERIG.shapeParent_in_place(mHandle.mNode,
                                                 crv,keepSource=False)                
            elif issubclass(type(d),dict):
                for side,ml in d.iteritems():
                    log.debug("|{0}| >> {1}...".format(_str_func,side)+ '-'*10)
                    for i,mHandle in enumerate(ml):
                        log.debug("|{0}| >> {1}...".format(_str_func,mHandle))
                        crv = CURVES.create_fromName(name='cube',
                                                     direction = 'z+',
                                                     size = mHandle.radius)
                        SNAP.go(crv,mHandle.mNode)
                        mHandleFactory.color(crv,side=side,controlType='sub')
                        CORERIG.shapeParent_in_place(mHandle.mNode,
                                                     crv,keepSource=False)
            else:
                log.debug("|{0}| >> {1}...".format(_str_func,d))
                side = d.getMayaAttr('cgmDirection') or 'center'                
                crv = CURVES.create_fromName(name='cube',
                                             direction = 'z+',
                                             size = d.radius)
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
    except Exception,error:
        cgmGEN.cgmExceptCB(Exception,error,msg=vars())


@cgmGEN.Timer
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
            raise ValueError,"Should have settings"
        
        #mPlug_visSub = self.atBuilderUtils('build_visSub')
        mPlug_visDirect = self.mPlug_visDirect_moduleParent
        mPlug_visSub = self.mPlug_visSub_moduleParent
        
        
        
        def simpleRegister(mObj):
            _d = MODULECONTROL.register(mObj,
                                        mirrorSide= self.d_module['mirrorDirection'],
                                        mirrorAxis="translateX,rotateY,rotateZ",
                                        makeAimable = False)
            ml_controlsAll.append(_d['mObj'])            
            return _d['mObj']
        
        for link in ['controlJaw','controlMuzzle','controlMouth','controlChin']:
            mLink = mRigNull.getMessageAsMeta(link)
            if mLink:
                log.debug("|{0}| >> {1}...".format(_str_func,link))
                
                _d = MODULECONTROL.register(mLink,
                                            mirrorSide= self.d_module['mirrorDirection'],
                                            mirrorAxis="translateX,rotateY,rotateZ",
                                            makeAimable = False)
                
                ml_controlsAll.append(_d['mObj'])        
                #ml_segmentHandles.append(_d['mObj'])
        log.debug(cgmGEN._str_subLine)
        
        if self.str_cheekSetup:
            log.debug("|{0}| >> cheek setup...".format(_str_func)+ '-'*40)
            for k in ['cheekLeft','cheekRight']:
                log.debug("|{0}| >> {1}...".format(_str_func,k))
                simpleRegister(self.md_driverJoints.get(k))


        if self.str_noseSetup:
            log.debug("|{0}| >> nose setup...".format(_str_func)+ '-'*40)
            
            for k in ['noseBase','noseTip','nostrilLeft','nostrilRight']:
                log.debug("|{0}| >> {1}...".format(_str_func,k))
                simpleRegister(self.md_driverJoints.get(k))

        
        #Handles ================================================================================
        log.debug("|{0}| >> Handles...".format(_str_func)+ '-'*80)
        for k,d in self.md_handles.iteritems():
            log.debug("|{0}| >> {1}...".format(_str_func,k)+ '-'*40)
            for side,ml in d.iteritems():
                log.debug("|{0}| >> {1}...".format(_str_func,side)+ '-'*10)
                for i,mHandle in enumerate(ml):
                    log.debug("|{0}| >> {1}...".format(_str_func,mHandle))
                    _d = MODULECONTROL.register(mHandle,
                                                mirrorSide= side,
                                                mirrorAxis="translateX,rotateY,rotateZ",
                                                makeAimable = False)
                    
                    ml_controlsAll.append(_d['mObj'])
                    ml_segmentHandles.append(_d['mObj'])
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
            
        
        """
        for k,d in self.md_rigJoints.iteritems():
            log.debug("|{0}| >> {1}...".format(_str_func,k)+ '-'*40)
            for side,ml in d.iteritems():
                log.debug("|{0}| >> {1}...".format(_str_func,side)+ '-'*10)
                for i,mHandle in enumerate(ml):
                    log.debug("|{0}| >> {1}...".format(_str_func,mHandle))
                    _d = MODULECONTROL.register(mHandle,
                                                typeModifier='direct',
                                                mirrorSide= side,
                                                mirrorAxis="translateX,rotateY,rotateZ",
                                                makeAimable = False)
                    
                    mObj = _d['mObj']
                    
                    ml_controlsAll.append(_d['mObj'])
                    
                    ATTR.set_hidden(mObj.mNode,'radius',True)        
                    if mObj.hasAttr('cgmIterator'):
                        ATTR.set_hidden(mObj.mNode,'cgmIterator',True)        
                
                    for mShape in mObj.getShapes(asMeta=True):
                        ATTR.connect(mPlug_visDirect.p_combinedShortName, "{0}.overrideVisibility".format(mShape.mNode))"""                    
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
        
    except Exception,error:
        cgmGEN.cgmExceptCB(Exception,error,msg=vars())


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
    mDeformNull = self.mDeformNull
    mFollowParent = self.mDeformNull
    mFollowBase = self.mDeformNull
    
    mdD = self.md_driverJoints
    #Process our main controls ==============================================================
    mMuzzle = mRigNull.getMessageAsMeta('controlMuzzle')
    mJaw = mRigNull.getMessageAsMeta('controlJaw')
    _str_rigNull = mRigNull.mNode
    if mMuzzle:
        log.debug("|{0}| >> Muzzle setup...".format(_str_func))
        mMuzzle.masterGroup.p_parent = self.mDeformNull
        mFollowParent = mMuzzle
        mFollowBase = mMuzzle.doCreateAt('null',setClass=True)
        mFollowBase.rename('{0}_followBase'.format(self.d_module['partName']))
        mFollowBase.p_parent = self.mDeformNull
        
    if mJaw:
        log.debug("|{0}| >> Jaw setup...".format(_str_func))
        mJaw.masterGroup.p_parent = mFollowParent
        if not mMuzzle:
            mFollowParent = mJaw
        
    if self.str_lipSetup:
        log.debug("|{0}| >> lip setup...".format(_str_func)+ '-'*40)
        
        log.debug("|{0}| >> mouth move...".format(_str_func))        
        mMouth = mRigNull.getMessageAsMeta('controlMouth')
        log.debug("|{0}| >> mMouth: {1}".format(_str_func,mMouth))
        mMouth.masterGroup.p_parent = mFollowParent
        
        mJawSpaceMouth = mMouth.doCreateAt(setClass=1)
        mJawSpaceMouth.p_parent = mJaw 
        mJawSpaceMouth.rename('{0}_mouthJawSpace'.format(self.d_module['partName']))
        mJawSpaceMouth.doGroup(True,asMeta=True,typeModifier = 'zero')
        _str_mouth = mMouth.mNode
        _str_mouthJawSpace = mJawSpaceMouth.mNode
        
        #Wire our jaw space mouth move
        for a in 'translate','rotate','scale':
            ATTR.connect("{0}.{1}".format(_str_mouth,a), "{0}.{1}".format(_str_mouthJawSpace,a))
            #mMouth.doConnectOut(a,mJawSpaceMouth.mNode)
        
        #Lip handles ------------------------------------------------------
        log.debug("|{0}| >> lip handles...".format(_str_func)+ '-'*20)
        
        log.debug("|{0}| >> sort handles".format(_str_func)+ '-'*20)
        mLeftCorner = self.md_handles['lipUpper']['left'][0]
        mRightCorner = self.md_handles['lipUpper']['right'][0]
        mUprCenter = self.md_handles['lipUpper']['center'][0]
        mLwrCenter = self.md_handles['lipLower']['center'][0]        
        ml_uprLip = self.md_handles['lipUpper']['right'][1:] + self.md_handles['lipUpper']['left'][1:]
        
        ml_lwrLip = self.md_handles['lipLower']['right'] + self.md_handles['lipLower']['left']
        
        ml_uprChain = self.md_handles['lipUpper']['right'][1:] + [mUprCenter] +self.md_handles['lipUpper']['left'][1:]
        ml_lwrChain = self.md_handles['lipLower']['right'] + [mLwrCenter] + self.md_handles['lipLower']['left']

        for mHandle in mLeftCorner,mRightCorner:
            log.debug("|{0}| >> lip handles | {1}".format(_str_func,mHandle))
            
            mHandle.masterGroup.p_parent = mFollowBase
            
            mMainTrack = mHandle.doCreateAt(setClass=1)
            mMainTrack.doStore('cgmName',mHandle)
            mMainTrack.doStore('cgmType','mainTrack')
            mMainTrack.doName()
            mMainTrack.p_parent = mFollowParent
            
            mJawTrack = mHandle.doCreateAt(setClass=1)
            mJawTrack.doStore('cgmName',mHandle)
            mJawTrack.doStore('cgmType','jawTrack')
            mJawTrack.doName()
            mJawTrack.p_parent = mJawSpaceMouth
            
            mc.parentConstraint([mMainTrack.mNode,mJawTrack.mNode],
                                mHandle.masterGroup.mNode,
                                maintainOffset=True)
            
        mUprCenter.masterGroup.p_parent = mMouth
        mLwrCenter.masterGroup.p_parent = mJawSpaceMouth
        
        #side handles ---------------------------
        d_lipSetup = {'upper':{'ml_chain':[mRightCorner] + ml_uprChain + [mLeftCorner],
                               'mInfluences':[mRightCorner.upperInfluence,mUprCenter,mLeftCorner.upperInfluence],
                               'mHandles':ml_uprLip},
                      'lower':{'ml_chain':[mRightCorner] + ml_lwrChain + [mLeftCorner],
                               'mInfluences':[mRightCorner.lowerInfluence,mLwrCenter,mLeftCorner.lowerInfluence],
                               'mHandles':ml_lwrLip}}
        
        for k,d in d_lipSetup.iteritems():
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
            
            """
            #Skin
            max_influences = 2
            mode_tighten = None
            blendLength = len(mInfluences)
            blendMin = 2
            _hardLength = 2
            
            #if extendEnds:
                #blendMin = 4
                #_hardLength = 4
                #mode_tighten = None
        
        
            if len(mInfluences) > 2:
                mode_tighten = None
                #blendLength = int(int_lenInfluences/2)
                max_influences = MATH.Clamp( blendLength, 2, 4)
                blendLength = MATH.Clamp( int(len(mInfluences)/2), 2, 6)
        
            #if len(mInfluences) == dat['int_driven']:
                #_hardLength = 3            
            
            RIGSKIN.surface_tightenEnds(mControlSurface.mNode,
                                        hardLength = 2,
                                        blendLength=2,
                                        mode=None)"""             
            
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
                
        #Lip handles ------------------------------------------------------
        log.debug("|{0}| >> lip corner influences...".format(_str_func)+ '-'*20)
        for i,mHandle in enumerate([mRightCorner,mLeftCorner]):
            mPlug_upper = cgmMeta.cgmAttr(mHandle,'twistUpper',value = 0,
                                          attrType='float',defaultValue = 0.0,keyable = True,hidden = False)
            mPlug_lower = cgmMeta.cgmAttr(mHandle,'twistLower',value = 0,
                                          attrType='float',defaultValue = 0.0,keyable = True,hidden = False)
            
            if not i:# ['right']:# and k not in ['inner','outer']:
                mPlug_upper.doConnectOut("{0}.rz".format(mHandle.upperInfluence.mNode))                 
                mPlug_lower.doConnectOut("{0}.rz".format(mHandle.lowerInfluence.mNode))                 
            else:  
                str_arg1 = "{0}.rz = -{1}".format(mHandle.upperInfluence.mNode,
                                                  mPlug_upper.p_combinedShortName)                
                str_arg2 = "{0}.rz = -{1}".format(mHandle.lowerInfluence.mNode,
                                                 mPlug_lower.p_combinedShortName)
                for a in str_arg1,str_arg2:
                    NODEFACTORY.argsToNodes(a).doBuild()
                

    if self.str_cheekSetup:
        log.debug("|{0}| >> cheek setup...".format(_str_func)+ '-'*40)
        for k in ['cheekLeft','cheekRight']:
            log.debug("|{0}| >> {1}...".format(_str_func,k))
            mdD[k].masterGroup.p_parent = self.mDeformNull
            
            mc.parentConstraint([mFollowParent.mNode, mJaw.mNode],
                                mdD[k].masterGroup.mNode,maintainOffset=True)
            
            mOffsetGroup = mdD[k].doGroup(True,asMeta=True,typeModifier = 'offset')
            
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
                                     driverValue = -20,value = 1)                
    
    if self.str_noseSetup:
        log.debug("|{0}| >> nose setup...".format(_str_func)+ '-'*40)
        mdD['noseBase'].masterGroup.p_parent = mDeformNull
        
        mTrack = mdD['noseBase'].masterGroup.doCreateAt(setClass=1)
        mTrack.p_parent = mFollowParent
        _c = mc.parentConstraint([mFollowBase.mNode, mTrack.mNode],
                            mdD['noseBase'].masterGroup.mNode,maintainOffset=True)[0]
        
        targetWeights = mc.parentConstraint(_c,q=True,
                                            weightAliasList=True,
                                            maintainOffset=True)
        ATTR.set(_c,targetWeights[0],.25)
        ATTR.set(_c,targetWeights[1],.75)
        
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



@cgmGEN.Timer
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
    mLeftCorner = self.md_handles['lipUpper']['left'][0]
    mRightCorner = self.md_handles['lipUpper']['right'][0]
    mUprCenter = self.md_handles['lipUpper']['center'][0]
    mLwrCenter = self.md_handles['lipLower']['center'][0]        
    ml_uprLipInfluences = [mRightCorner.upperInfluence] + self.md_handles['lipUpper']['right'][1:] + self.md_handles['lipUpper']['center']+ self.md_handles['lipUpper']['left'][1:] + [mLeftCorner.upperInfluence]
    ml_lwrLipInfluences = [mRightCorner.lowerInfluence] + self.md_handles['lipLower']['right'] + self.md_handles['lipLower']['center']+ self.md_handles['lipLower']['left'] + [mLeftCorner.lowerInfluence]
    
    log.debug("|{0}| >> sort driven".format(_str_func))
    dUpr =  self.md_rigJoints['lipUpper']
    dLwr =  self.md_rigJoints['lipLower']
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
              'sealSplit':True,
              'specialMode':'endsToInfluences',
              'moduleInstance':mModule,
              'msgDriver':'driverJoint'}    
    
    #pprint.pprint(d_test)
    IK.ribbon_seal(**d_lips)
    
    
    for mObj in ml_uprRig + ml_lwrRig:
        mObj.driverJoint.p_parent = mDeformNull
    
    return 
    """
    driven1 = [u'L_lip_corner_rig',u'L_lip_upr_rig',u'CTR_lip_upr_rig',u'R_lip_upr_rig',u'R_lip_corner_rig']
    driven2 = [u'L_lip_corner_rig',u'L_lip_lwr_rig',u'CTR_lip_lwr_rig',u'R_lip_lwr_rig',u'R_lip_corner_rig']
    
    influences1 =[u'L_lip_corner_anim',u'L_lip_upr_anim',u'CTR_lip_upr_anim',u'R_lip_upr_anim',u'R_lip_corner_anim']
    influences2 =[u'L_lip_corner_anim',u'L_lip_lwr_anim',u'CTR_lip_lwr_anim',u'R_lip_lwr_anim',u'R_lip_corner_anim']
    
    d_test = {'driven1':driven1,
              'driven2':driven2,
              'influences1':influences1,
              'influences2':influences2,
              'baseName':'lipRibbons',
              'baseName1' :"uprLip",
              'baseName2':"lwrLip",
              'extendEnds':True,
              'msgDriver':'driverGroup'}
    reload(MORPHYUTILS)
    MORPHYUTILS.ribbon_seal(**d_test)    """






    
    #Process our main controls ==============================================================
    mMuzzle = mRigNull.getMessageAsMeta('controlMuzzle')
    mJaw = mRigNull.getMessageAsMeta('controlJaw')
    _str_rigNull = mRigNull.mNode
    if mMuzzle:
        log.debug("|{0}| >> Muzzle setup...".format(_str_func))
        mMuzzle.masterGroup.p_parent = self.mDeformNull
        mFollowParent = mMuzzle
        mFollowBase = mMuzzle.doCreateAt('null',setClass=True)
        mFollowBase.rename('{0}_followBase'.format(self.d_module['partName']))
        mFollowBase.p_parent = self.mDeformNull
        
    if mJaw:
        log.debug("|{0}| >> Jaw setup...".format(_str_func))
        mJaw.masterGroup.p_parent = mFollowParent
        if not mMuzzle:
            mFollowParent = mJaw
        
    if self.str_lipSetup:
        log.debug("|{0}| >> lip setup...".format(_str_func)+ '-'*40)
        
        log.debug("|{0}| >> mouth move...".format(_str_func))        
        mMouth = mRigNull.getMessageAsMeta('controlMouth')
        log.debug("|{0}| >> mMouth: {1}".format(_str_func,mMouth))
        mMouth.masterGroup.p_parent = mFollowParent
        
        mJawSpaceMouth = mMouth.doCreateAt(setClass=1)
        mJawSpaceMouth.p_parent = mJaw 
        mJawSpaceMouth.rename('{0}_mouthJawSpace'.format(self.d_module['partName']))
        mJawSpaceMouth.doGroup(True,asMeta=True,typeModifier = 'zero')
        _str_mouth = mMouth.mNode
        _str_mouthJawSpace = mJawSpaceMouth.mNode
        
        #Wire our jaw space mouth move
        for a in 'translate','rotate','scale':
            ATTR.connect("{0}.{1}".format(_str_mouth,a), "{0}.{1}".format(_str_mouthJawSpace,a))
            #mMouth.doConnectOut(a,mJawSpaceMouth.mNode)
        
        #Lip handles ------------------------------------------------------
        log.debug("|{0}| >> lip handles...".format(_str_func)+ '-'*20)
        
        log.debug("|{0}| >> sort handles".format(_str_func)+ '-'*20)
        mLeftCorner = self.md_handles['lipUpper']['left'][0]
        mRightCorner = self.md_handles['lipUpper']['right'][0]
        mUprCenter = self.md_handles['lipUpper']['center'][0]
        mLwrCenter = self.md_handles['lipLower']['center'][0]        
        ml_uprLip = self.md_handles['lipUpper']['right'][1:] + self.md_handles['lipUpper']['left'][1:]
        ml_lwrLip = self.md_handles['lipLower']['right'] + self.md_handles['lipLower']['left']
        
        
        for mHandle in mLeftCorner,mRightCorner:
            log.debug("|{0}| >> lip handles | {1}".format(_str_func,mHandle))
            
            mHandle.masterGroup.p_parent = mFollowBase
            
            mMainTrack = mHandle.doCreateAt(setClass=1)
            mMainTrack.doStore('cgmName',mHandle)
            mMainTrack.doStore('cgmType','mainTrack')
            mMainTrack.doName()
            mMainTrack.p_parent = mFollowBase
            
            mJawTrack = mHandle.doCreateAt(setClass=1)
            mJawTrack.doStore('cgmName',mHandle)
            mJawTrack.doStore('cgmType','jawTrack')
            mJawTrack.doName()
            mJawTrack.p_parent = mJawSpaceMouth
            
            mc.parentConstraint([mMainTrack.mNode,mJawTrack.mNode],
                                mHandle.masterGroup.mNode,
                                maintainOffset=True)
            
        mUprCenter.masterGroup.p_parent = mMouth
        mLwrCenter.masterGroup.p_parent = mJawSpaceMouth
        
        #side handles ---------------------------
        d_lipSetup = {'upper':{'ml_chain':[mRightCorner] + ml_uprLip + [mLeftCorner],
                               'mInfluences':[mRightCorner,mUprCenter,mLeftCorner],
                               'mHandles':ml_uprLip},
                      'lower':{'ml_chain':[mRightCorner] + ml_lwrLip + [mLeftCorner],
                               'mInfluences':[mRightCorner,mLwrCenter,mLeftCorner],
                               'mHandles':ml_lwrLip}                      }
        
        for k,d in d_lipSetup.iteritems():
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
                                                                  tsb=True,
                                                                  maximumInfluences = 2,
                                                                  normalizeWeights = 1,dropoffRate=5.0),
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
        


@cgmGEN.Timer
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
    mBlock.UTILS.set_blockNullTemplateState(mBlock)
    self.UTILS.rigNodes_store(self)


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
    mPuppetSettings = self.d_module['mMasterControl'].controlSettings
    mPrerigNull = mBlock.prerigNull
    
    _side = BLOCKUTILS.get_side(self.mBlock)
    
    ml_rigJoints = mRigNull.msgList_get('rigJoints',asMeta = True)
    if not ml_rigJoints:
        raise ValueError,"No rigJoints connected"
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
    ml_new = []
    #Let's gather our proxy mesh
    for lnk in ['jaw','nose','uprLip','lwrLip','noseToCheekLeft','noseToCheekRight']:
        mBase = mBlock.getMessageAsMeta(lnk+'TemplateLoft')
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
            if lnk in 'uprLip':
                for mObj in ml_use:
                    #if 'LWR_lip' in mObj.mNode:
                    if mObj.getMayaAttr('cgmPosition') == 'lower' and mObj.cgmName == 'lip':
                        log.debug("|{0}| >> removing: {1}".format(_str_func,mObj))
                        ml_remove.append(mObj)
            if lnk in 'lwrLip':
                for mObj in ml_use:
                    #if 'UPR_lip' in mObj.mNode:                    
                    if mObj.getMayaAttr('cgmPosition') == 'upper' and mObj.cgmName == 'lip':
                        ml_remove.append(mObj)
                        log.debug("|{0}| >> removing: {1}".format(_str_func,mObj))
                        
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
            
            
    """
    if ml_new:
        _mesh = mc.polyUnite([mObj.mNode for mObj in ml_new],ch=False)
        _mesh = mc.rename(_mesh,'{0}_proxy_geo'.format(self.d_module['partName']))        
        mNew = cgmMeta.asMeta(_mesh)
        
        ml_proxy.append(mNew)
        
        log.debug("|{0}| >> Skinning surface: {1}".format(_str_func,mNew))
        mSkinCluster = cgmMeta.validateObjArg(mc.skinCluster ([mObj.mNode for mObj in ml_rigJoints],
                                                              mNew.mNode,
                                                              tsb=True,
                                                              maximumInfluences = 4,
                                                              heatmapFalloff = 1.0,
                                                              bindMethod = 2,
                                                              normalizeWeights = 1,dropoffRate=10.0),
                                              'cgmNode',
                                              setClass=True)
    
        mSkinCluster.doStore('cgmName', mNew)
        mSkinCluster.doName()"""
        
    


    for mProxy in ml_proxy:
        CORERIG.colorControl(mProxy.mNode,_side,'main',transparent=False,proxy=True)
        #mc.makeIdentity(mProxy.mNode, apply = True, t=1, r=1,s=1,n=0,pn=1)

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
        raise ValueError,"No rigJoints connected"
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
        mLoftSurface =  mBlock.jawTemplateLoft.doDuplicate(po=False,ic=False)
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
            mLoftSurface =  mBlock.noseTemplateLoft.doDuplicate(po=False,ic=False)
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




















