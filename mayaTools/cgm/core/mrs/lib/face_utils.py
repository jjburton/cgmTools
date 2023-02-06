"""
------------------------------------------
face_utils: cgm.core.mrs.lib
Author: Josh Burton
Website : https://github.com/jjburton/cgmTools/wiki
------------------------------------------

================================================================
"""
__MAYALOCAL = 'FACEUTILS'

import random
import re
import copy
import time
import os
import pprint

#From Red9 =============================================================
from Red9.core import Red9_Meta as r9Meta

#========================================================================
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
#========================================================================

import maya.cmds as mc

# From cgm ==============================================================
from cgm.core import cgm_General as cgmGEN
from cgm.core.mrs.lib import shared_dat as BLOCKSHARED
from cgm.core import cgm_Meta as cgmMeta
from cgm.core.cgmPy import validateArgs as VALID
from cgm.core.classes import GuiFactory as CGMUI
import cgm.core.lib.string_utils as STR
from cgm.core.lib import attribute_utils as ATTR
from cgm.core.rig import joint_utils as RIGJOINTS
from cgm.core.lib import attribute_utils as ATTR
from cgm.core.lib import search_utils as SEARCH
from cgm.core.classes import NodeFactory as NODEF
import cgm.core.lib.sdk_utils as SDK

def controls_verifyAsControls(nodes= None):
    if not nodes:
        nodes = mc.ls(sl=1)
        
    ml = cgmMeta.validateObjListArg(nodes,'cgmControl',setClass=1)
    for mObj in ml:
        mObj._verifyMirrorable()    
    
def controls_wireRightToLeft(nodes = None):
    if not nodes:
        nodes = mc.ls(sl=1)
    
    ml = cgmMeta.validateObjListArg(nodes,'cgmControl',setClass=1)
    for mObj in ml:
        mObj._verifyMirrorable()
        
    ml[0].connectChildNode(ml[1],'mirrorControl','mirrorControl')
    ml[0].mirrorSide = 'Right'
    ml[1].mirrorSide = 'Left'
    

_d_faceBufferAttributes = {
    'default':{"jaw":{'attrs':['dn','clench','left','right','fwd','back']},
               "eye":{'attrs':['squeeze','blink','upr_up','upr_dn',
                               'ball_left','ball_right','ball_up','ball_dn',
                               ],
                           'sideAttrs':'*'},
               "cheek":{'attrs':['up','dn','blow','suck'],
                        'sideAttrs':'*'},
               
               "brow":{'attrs':['center_up','center_dn',
                                'inr_up','inr_dn','squeeze',
                                'mid_up','mid_dn',
                                'outr_up','outr_dn'],
                       'sideAttrs':[ 'inr_up','inr_dn','squeeze',
                                     'mid_up','mid_dn',
                                     'outr_up','outr_dn']},
               "sneer":{'attrs':['up'],
                        'sideAttrs':'*'},
               
               "nostril":{'attrs':['up','dn','flare','in'],
                        'sideAttrs':'*'},
               
               "mouth":{'attrs':['left','right','up','dn']},
               
               "seal":{'attrs':['left','right','centerOut']},
               
               "lips":{'attrs':['smile','wide','narrow','purse','twistUp','twistDn','out','frown','presser',
                                'funnel','ooo'],
                       'sideAttrs':'*'},
               
               "lipUpr":{'attrs':['up','in','out','fwd'],
                       'sideAttrs':'*'},
               "lipLwr":{'attrs':['up','in','out','fwd'],
                       'sideAttrs':'*'},                           

               "lips":{'attrs':['smile','wide','narrow','purse','twistUp','twistDn','out','frown','dimpler'],
                       'sideAttrs':'*'},
               
               "lipCntr_upr":{'attrs':['fwd','back','up','dn','rollIn','rollOut'],
                       'sideAttrs':['up','dn','rollIn','rollOut']},
               "lipCntr_lwr":{'attrs':['fwd','back','up','dn','rollIn','rollOut'],
                       'sideAttrs':['up','dn','rollIn','rollOut']},            
               },
    
    'FACS_1':{"jaw":{'attrs':['open','left','right','fwd','back']},
            "lips":{'attrs':['smile','dimpler','frown','funnel','uprRollIn','lwrRollIn',
                             'pucker','presser','pullDownWide','pullDown','ooo'],
                    'sideAttrs':['smile','dimpler','frown','presser','pullDownWide','pullDown']},
            "sneer":{'attrs':['up'],
                    'sideAttrs':'*'},
            "mouth":{'attrs':['left','right','up','dn','close','sticky']},
            "eyeLids":{'attrs':['blink','wide','squint','compress',
                                'lookDn','lookUp','lookLeft','lookRight'],
                    'sideAttrs':['blink','wide','squint','compress']},
            "nose":{'attrs':['sneer'],
                    'sideAttrs':'*'},
            "cheek":{'attrs':['raise','puff','suck'],
                    'sideAttrs':'*'},            
            "brow":{'attrs':['innrUp','innrDn','outrUp','outrDn','squeeze'],
                    'sideAttrs':['innrUp','innrDn','outrUp','outrDn']},
            },
    'och':{
        "lid":{'attrs':['upr','lwr'],
               "sideAttrs":'*'},
        "brow":{'attrs':['furrow','up','down'],
                "sideAttrs":'*'},
        "browMid":{'attrs':['up','down','squeeze']},        
        
        "lip":{'attrs':['uprSneer','lwrSneer','sealCenter',
                        'uprUp','uprDown','lwrUp','lwrDown',
                        'seal','smile','frown','wide','narrow'],
               "sideAttrs":['uprSneer','lwrSneer',
                            'uprUp','uprDown','lwrUp','lwrDown',                            
                            'seal','smile','frown','wide','narrow']},
        "ear":{'attrs':['thickBase','cup'],
                "sideAttrs":'*'},
        
        "lipOut":{'attrs':['upr','lwr']},        
        
        "pupil":{'attrs':['horizontal','vertical','angle'],
                 "sideAttrs":'*'},        
        "cheek":{'attrs':['puff','outer'],
                 "sideAttrs":'*'},
        "uprMuzzle":{'attrs':['tweak'],
                 "sideAttrs":'*'},
        "nose":{'attrs':['sniff']},        
        
        "jaw":{'attrs':['open','close','left','right','forward','back'],},
        "mouth":{'attrs':['up','down','left','right'],},
        
        "tongue":{'attrs':['down','left','right','out','hide']},
        
        "teeth":{'attrs':['wide','hideUpr','hideLwr','fangUp', 'close','nice','uprGum','back'],
                 "sideAttrs":['wide','fangUp']},
        
        "hide":{'attrs':['line'],
                 },
    },    
    
    'g1':{
        "eye":{'attrs':['up','dn','left','right']},
        "lid":{'attrs':['uprOpen','lwrOpen','arcUp','arcDn']},
        "orb":{'attrs':['blink','arcUp','arcDn','angry','surprise','arcDn','bottomSqueeze','sad','frustrated']},        
        "mouth":{'attrs':['up','dn','left','right']},
        "brow":{'attrs':['up','dn','thicken','flatten']},                       
        "jaw":{'attrs':['dn','close','fwd','back']},                    
        "lips":{'attrs':['smile','wide','narrow','frown', 'sneer', 'teethLip','close'],
                'sideAttrs':'*'}},    
    
    'w1':{
        "lid":{'attrs':['uprClose','uprFurrow','lwrClose','lwrFurrow','arcUp','arcDn'],
               "sideAttrs":'*'},
        "brow":{'attrs':['arc','dn','up','flatten','furrow'],
                "sideAttrs":'*'},
        "mouth":{'attrs':['up','dn','left','right']},
        "lips":{'attrs':['smile','wide','narrow','frown', 'seal','smirk',
                         'smileBig','frownBig'],
                'sideAttrs':'*'},
        "tongue":{'attrs':['hide']},
        "nose":{'attrs':['flare']},},
    'ren':{
        "eye":{'attrs':['up','dn','left','right'],
               'sideAttrs':'*'},
        "lid":{'attrs':['uprOpen','lwrOpen','arcUp','arcDn'],
               "sideAttrs":'*'},
        "teeth":{'attrs':['arcUp']},

    },
    'ara':{
        "eye":{'attrs':['up','dn','left','right'],
               'sideAttrs':'*'},
        "lid":{'attrs':['arcUprUp','arcLwrUp',
                        'arcUprDn','arcLwrDn',
                        'uprUp','uprDn','lwrUp','lwrDn'],
               "sideAttrs":'*'},
        "brow":{'attrs':['arcUp','arcDn','furrow'],
                "sideAttrs":'*'},
        "pupil":{'attrs':['small'],
                 "sideAttrs":'*'},        
        "cheek":{'attrs':['out'],
                 "sideAttrs":'*'},
        "nose":{'attrs':['flare'],},
        "tongue":{'attrs':['fix']},

    },
    
    'urd':{
        "eye":{'attrs':['up','dn','left','right','hide'],
               'sideAttrs':'*'},
        "lid":{'attrs':['up','dn'],
               "sideAttrs":'*'},
        "brow":{'attrs':['arcUp','arcDn','up','sad','angry'],
                "sideAttrs":'*'},
        
        "lip":{'attrs':['uprSneer','lwrSneer',
                        'up','dn','seal','sealRaw',
                        'smileRaw','frownRaw',
                        'smile','frown','wide','narrow'],
               "sideAttrs":'*'},        
        "pupil":{'attrs':['small','big'],
                 "sideAttrs":'*'},        
        "cheek":{'attrs':['out'],
                 "sideAttrs":'*'},
        
        "jaw":{'attrs':['open','openUse','close',
                        'smileOpen','frownOpen'],
                 "sideAttrs":['smileOpen','frownOpen','open']},        
        "tongue":{'attrs':['hide','teethPose']},

    },
    'cha':{
        "lid":{'attrs':['blink','eyeAngle','arcUp','arcDn'],
               "sideAttrs":'*'},
        "eye":{'attrs':['fix','pupilRound','pupilBottom'],
               "sideAttrs":'*'},
        
        "brow":{'attrs':['arcUp','flat','angry','thick'],
                "sideAttrs":'*'},
        
        "lip":{'attrs':['cat',
                        'seal',
                        'smile','frown','wide','narrow','smilePush'],
               "sideAttrs":'*'},

        "mouth":{'attrs':['out','up']},        
        "jaw":{'attrs':['open']},
        "tongue":{'attrs':['hide']},        
        "teeth":{'attrs':['hide', 'flatUpr','flatLwr', 'closeFlat','closeReg']},

    },
    'pip':{
        "lid":{'attrs':['blink','angry','sad','arcUp','arcDn','squeeze'],
               "sideAttrs":'*'},
        "lip":{'attrs':['seal','ooo',
                        'smile','frown','wide','narrow','pout'],
               "sideAttrs":'*'},
        'cheek':{'attrs':['inflate'],
                 'sideAttrs':'*'},
        'tail':{'attrs':['spread','narrow']},
        "jaw":{'attrs':['open','up','side'],
               "sideAttrs":['side']},
    },       
    'toon':{"nose":{'attrs':['out','in','sneer_up','sneer_dn',
                            'seal_up_cntr','seal_up_outr'],
                   'sideAttrs':'*'},
            
           "cheek":{'attrs':['up','dn','blow','suck'],
                    'sideAttrs':'*'},
           "eyeSqueeze":{'attrs':['up','dn'],
                       'sideAttrs':'*'},                           
           "mouth":{'attrs':['up','dn','left','right','fwd','back','twist'],
                    'sideAttrs':['twist']},
           "brow":{'attrs':['center_up','center_dn',
                            'inr_up','inr_dn','squeeze',
                            'mid_up','mid_dn',
                            'outr_up','outr_dn'],
                   'sideAttrs':[ 'inr_up','inr_dn','squeeze',
                                 'mid_up','mid_dn',
                                 'outr_up','outr_dn']},                       
           "jaw":{'attrs':['dn','clench','left','right','fwd','back']},
           "jawDriven":{'attrs':['dn_tz','dn_rx','left_tx','left_ry','left_rz','right_tx','right_ry','right_rz','fwd_tz','back_tz']},
           "jawBase":{'attrs':['tx','ty','tz','rx','ry','rz']},
           "jawNDV":{'attrs':['tx','ty','tz','rx','ry','rz']},                                                        
           "driver":{'attrs':['jaw_dn_tz','jaw_dn_rx','mouth_twist',
                              'jaw_left_tx','jaw_left_ry','jaw_left_rz',
                              'jaw_right_tx','jaw_right_ry','jaw_right_rz',
                              'jaw_fwd_tz','jaw_back_tz',
                              'smile_dn_pull','frown_dn_pull']},                           
           "lipUpr":{'attrs':['rollOut','rollIn','moreIn','moreOut','up','upSeal_outr','upSeal_cntr',
                              'seal_out_cntr','seal_out_outr',#'seal_out_cntr_diff','seal_out_outr_diff'
                              ],
                   'sideAttrs':'*'},
           "lipLwr":{'attrs':['rollOut','rollIn','moreIn','moreOut','dn','dnSeal_outr','dnSeal_cntr',
                              'seal_out_cntr','seal_out_outr',#'seal_out_cntr_diff','seal_out_outr_diff'
                              ],
                     'sideAttrs':'*'},                           
           "seal":{'attrs':['center','left','right'],
                   'sideAttrs':[]},
           "jDiff":{'attrs':['dn_frown','dn_smile','dn_seal_outr','dn_seal_cntr','fwd_seal_outr','fwd_seal_cntr',
                             'back_seal_outr','back_seal_cntr','left_seal_outr','left_seal_cntr','right_seal_outr','right_seal_cntr'],
                   'sideAttrs':'*'},
           "lips":{'attrs':['smile','wide','narrow','purse','twistUp','twistDn','out','frown'],
                   'sideAttrs':'*'},
           "lipCntr_upr":{'attrs':['fwd','back','up','dn'],
                   'sideAttrs':['up','dn']},
           "lipCntr_lwr":{'attrs':['fwd','back','up','dn'],
                            'sideAttrs':['up','dn']}}}


def SDKGroups_pushTo(nodes = [],position=True):
    if nodes:
        ml = cgmMeta.asMeta(nodes)
    else:
        ml = cgmMeta.asMeta(sl=1)
        
    d = {}
    
    for mObj in ml:
        mGrp = mObj.getMessageAsMeta('sdkGroup')
        if not mGrp:
            log.warning("Missing sdkGroup: {0}".format(mGrp))
            continue
        
        d[mObj] = {'t':mObj.translate,
                   'p':mObj.p_position,
                   'o':mObj.p_orient,
                   'r':mObj.rotate,
                   's':mObj.scale,
                   'mGrp':mGrp}
        
    for mObj,_d in d.iteritems():
        mObj.resetAttrs(['t','r','s'])
        
    for i in range(8):
        for mObj,_d in d.iteritems():
            if position:
                _d['mGrp'].p_position = _d['p']
                _d['mGrp'].p_orient = _d['o']
                
            else:
                _d['mGrp'].translate = _d['t']
                _d['mGrp'].rotate = _d['r']
                
            _d['mGrp'].scale = _d['s']
        
    #pprint.pprint(d)

def SDKGroups_select(nodes=[]):
    if nodes:
        ml = cgmMeta.asMeta(nodes)
    else:
        ml = cgmMeta.asMeta(sl=1)
        
    ml_sdks = []
    for mObj in ml:
        try:ml_sdks.append(mObj.getMessage('sdkGroup')[0])
        except:
            log.warning("Missing SDK target: {0}".format(mObj.p_nameShort))
    if ml_sdks:mc.select(ml_sdks)    
    return ml_sdks


def SDKGroups_selectSources(nodes=[]):
    if nodes:
        ml = cgmMeta.asMeta(nodes)
    else:
        ml = cgmMeta.asMeta(sl=1)
        
    _res = []
    for mObj in ml:
        try:_res.append(mObj.getMessage('source')[0])
        except:
            log.warning("Missing SDK source: {0}".format(mObj.p_nameShort))
    if _res:mc.select(_res)    
    return _res    

def SDKGroups_verify(nodes =[]):
    """
    We need joints
    """
    if nodes:
        ml = cgmMeta.asMeta(nodes)
    else:
        ml = cgmMeta.asMeta(sl=1)
        
    ml_sdks = []
    for mObj in ml:
        _create = True
        _cleanOld = False
        mDag = mObj.getMessageAsMeta('sdkGroup')
        if mDag:
            if mDag.getMayaType() != 'joint':
                log.error("Not a joint: {0}".format(mDag))
                _cleanOld = True
            else:
                mSDK = mDag
                _create = False
                
        if _create:
            mSDK = mObj.doCreateAt('joint', connectAs = 'sdkGroup', setClass = 'cgmObject')
            mSDK.p_parent = mObj.p_parent
            
            RIGJOINTS.freezeOrientation(mSDK)
            
            mObj.p_parent = mSDK
            
            if _cleanOld:
                mDag.delete()
            else:
                mSDK.p_parent = mObj.p_parent
                
        mSDK.doStore('cgmName', mObj.p_nameBase)            
        mSDK.doStore('cgmType', 'sdkJoint')
        mSDK.doName()
            

                      
            
        ml_sdks.append(mSDK)
        
    if ml_sdks:
        mc.select([mObj.mNode for mObj in ml_sdks])    
    return ml_sdks    


_d_bufferToAttrs = {
    'FACS_1':{
'Rest':None, 
'brow_innrDn_left':'l_browInnerDn_BLS', 
'brow_innrDn_right':'r_browInnerDn_BLS', 
'brow_innrUp_left':'l_browInnerUp_BLS', 
'brow_innrUp_right':'r_browInnerUp_BLS', 
'brow_outrDn_left':'l_browOuterDn_BLS', 
'brow_outrDn_right':'r_browOuterDn_BLS', 
'brow_outrUp_left':'l_browOuterUp_BLS', 
'brow_outrUp_right':'r_browOuterUp_BLS', 
'brow_squeeze':'m_browSqueeze_BLS', 
'cheek_puff_left':'l_cheekPuff_BLS', 
'cheek_puff_right':'r_cheekPuff_BLS', 
'cheek_raise_left':'l_cheekRaiser_BLS', 
'cheek_raise_right':'r_cheekRaiser_BLS', 
'cheek_suck_left':'l_cheekSuck_BLS', 
'cheek_suck_right':'r_cheekSuck_BLS', 
'eyeLids_blink_left':'l_eyeBlink_BLS', 
'eyeLids_blink_right':'r_eyeBlink_BLS', 
'eyeLids_compress_left':'l_eyeCompress_BLS', 
'eyeLids_compress_right':'r_eyeCompress_BLS', 
'eyeLids_lookDn':'m_eyelidsLookDn_BLS', 
'eyeLids_lookLeft':'m_eyelidsLookLeft_BLS', 
'eyeLids_lookRight':'m_eyelidsLookRight_BLS', 
'eyeLids_lookUp':'m_eyelidsLookUp_BLS', 
'eyeLids_squint_left':'l_eyeSquint_BLS', 
'eyeLids_squint_right':'r_eyeSquint_BLS', 
'eyeLids_wide_left':'l_eyeWide_BLS', 
'eyeLids_wide_right':'r_eyeWide_BLS', 
'jaw_back':'m_jawBackward_BLS', 
'jaw_fwd':'m_jawForward_BLS', 
'jaw_left':'m_jawLeft_BLS', 
'jaw_open':'m_jawOpen_BLS', 
'jaw_right':'m_jawRight_BLS', 
'lips_dimpler_left':'l_dimpler_BLS', 
'lips_dimpler_right':'r_dimpler_BLS', 
'lips_frown_left':'l_frown_BLS', 
'lips_frown_right':'r_frown_BLS', 
'lips_funnel':'m_funnel_BLS', 
'lips_lwrRollIn':'m_lowerLipRollIn_BLS', 
'lips_ooo':'m_lipsOo_BLS', 
'lips_presser_left':'l_presser_BLS', 
'lips_presser_right':'r_presser_BLS', 
'lips_pucker':'m_pucker_BLS', 
'lips_pullDown_left':'l_pullDown_BLS', 
'lips_pullDown_right':'r_pullDown_BLS', 
'lips_pullDownWide_left':'l_pullDownWide_BLS', 
'lips_pullDownWide_right':'r_pullDownWide_BLS', 
'lips_smile_left':'l_smile_BLS', 
'lips_smile_right':'r_smile_BLS', 
'lips_uprRollIn':'m_upperLipRollIn_BLS', 
'mouth_close':'m_mouthClose_BLS', 
'mouth_dn':'m_mouthDn_BLS', 
'mouth_left':'m_mouthLeft_BLS', 
'mouth_right':'m_mouthRight_BLS', 
'mouth_sticky':'m_mouthSticky_BLS', 
'mouth_up':'m_mouthUp_BLS', 
'nose_sneer_left':'l_noseSneer_BLS', 
'nose_sneer_right':'r_noseSneer_BLS', 
'sneer_up_left':'l_sneer_BLS', 
'sneer_up_right':'r_sneer_BLS', 
}}


class poseBuffer():
    attrDat = None
    attrMask = ['cgmName','cgmType','mClass','mNodeID','mClassGrp','mSystemRoot']
    
    def __init__(self,node = None, 
                 name = None,
                 baseName = 'face',
                 attrDat = None,
                 faceType = 'default',
                 *args,**kws):
        """ 
        """
        _sel = mc.ls(sl=1)

        self.attrDat = {}
        

        self.attrDat = _d_faceBufferAttributes.get(faceType) or None
        if attrDat:
            self.attrDat = attrDat
       
        if kws:log.info("kws: %s"%str(kws))
        if args:log.info("args: %s"%str(args))
        

        if not node:
            mBuffer = cgmMeta.cgmObject()
            mBuffer.doStore('cgmName',faceType)
            mBuffer.doStore('cgmType','faceBuffer')
            mBuffer.doName()
        else:
            mBuffer = cgmMeta.validateObjArg(node)
        
        self.mBuffer = mBuffer
                    
        if _sel:
            mc.select(_sel)
            
            
    def buffer_purge(self):
        mBuffer = self.mBuffer
        _short = mBuffer.mNode
        
        log.warning("Deleting...")
        for a in mBuffer.getAttrs(ud=True):
            if a in poseBuffer.attrMask:
                continue
            
            log.warning(a)
            
            ATTR.delete(_short,a)
        
        
    def buffer_rebuild(self):
        _str_func = 'buffer_rebuild'
        self.buffer_purge()
        self.buffer_verify()
        
    def buffer_verify(self, attrDat = None, addNonSplits = False, maxValue = 1.0, minValue = 0):
        """
        addNonSplits | add a lips_smile for example for splitting to L/R
        """
        _str_func = 'buffer_verify'
        mBuffer = self.mBuffer
        
        if attrDat is None:
            d_buffer = _d_faceBufferAttributes.get(mBuffer.cgmName) or {}
        else:
            d_buffer = attrDat
            self.attrDat = attrDat
            
        if not d_buffer:
            raise ValueError, "No attrDat"
        
        l_sections = d_buffer.keys()
        l_sections.sort()
        
        mBuffer.addAttr("Rest",attrType = 'float',hidden = False)
        
        for section in l_sections:
            mBuffer.addAttr("XXXXXXXXX_{0}_attrs".format(section),
                            attrType = 'int',
                            keyable = False,
                            hidden = False,lock=True) 
            
            _d_section = d_buffer[section]
            l_attrs = _d_section.get('attrs') or []
            l_attrs.sort()
            
            #Build our names
            l_sidesAttrs = _d_section.get('sideAttrs') or []
            if l_sidesAttrs == '*':
                l_sidesAttrs = copy.copy(l_attrs)
                
            for a in l_attrs:
                l_name = [section,a]                    
                l_names = []
                _d = {'left':[],'right':[]}
                if a in l_sidesAttrs:
                    if addNonSplits:l_names.append(l_name)
                    for side in ['left','right']:
                        l_buffer = copy.copy(l_name)
                        l_buffer.append(side)
                        l_names.append(l_buffer)
                        #_d[side].append(l_buffer)
                if not l_names:l_names = [l_name]
                for n in l_names:
                    log.info( cgmGEN.logString_msg(_str_func, n))
                    mBuffer.addAttr("_".join(n),attrType = 'float',hidden = False, maxValue = maxValue, minValue = minValue)
                    
    def connect_to_controls(self,d_type = None):
        _str_func = 'connect_to_controls'
        mBuffer = self.mBuffer
        reload(NODEF)
        
        if not d_type:
            d_type = _d_faceControlsToConnect.get(mBuffer.cgmName)
            
        if not d_type:
            raise ValueError, cgmGEN.logString_msg(_str_func,"Must have wiring dict")
        
        for key,_d_control in d_type.iteritems():
            try:
                control = _d_control['control']
                _d_wiring = _d_control['wiringDict']
                _l_simpleArgs = _d_control.get('simpleArgs') or []
                
                if not mc.objExists(control):
                    raise ValueError,"Control not found: {0}".format(control)
                
                if _d_wiring:
                    try:
                        NODEF.connect_controlWiring(control,mBuffer,
                                                    _d_wiring,
                                                    baseName = key,
                                                    trackAttr = True,
                                                    simpleArgs = _l_simpleArgs )
                    except Exception,error:
                        log.warning(" Wire call fail | error: {0}".format(error)   ) 
                elif _l_simpleArgs:
                        for arg in _l_simpleArgs:
                            log.info( cgmGEN.logString_msg(_str_func,"On arg: {0}".format(arg)))
                            if "{0}" in arg:
                                arg = arg.format(mBuffer.mNode)
                                
                            try:
                                NODEF.argsToNodes(arg).doBuild()			
                            except Exception,error:
                                log.error( cgmGEN.logString_msg(_str_func,"{0} arg failure | error: {1}".format(arg,error)))
                                
                        
                else:
                    log.warning( cgmGEN.logString_msg(_str_func,"No wiring data or simpleArgs for key: {0}".format(key)))
                                        
                #self._d_controls[key] = cgmMeta.cgmObject(control)

            except Exception,error:
                raise Exception,"Control '{0}' fail | error: {1}".format(key,error)
            
    def connect_to_bsNode(self, targetNode = None, d_connect = None):
        _str_func = 'connect_to_blendshapeNode'
        
        if not targetNode:
            raise ValueError, cgmGEN.logString_msg(_str_func,"Must have targetNode")
        
        mTarget = cgmMeta.validateObjArg(targetNode)
            
        mBuffer = self.mBuffer
        
        if not d_connect:
            d_connect = _d_bufferToAttrs.get(mBuffer.cgmName)
            
        l_missingDrivers = []
        l_missingDriven = []
        
        for driver,driven in d_connect.iteritems():
            log.info(cgmGEN.logString_sub(_str_func,"{0} | {1}".format(driver,driven)))
            
            if mBuffer.hasAttr(driver):
                try:
                    mBuffer.doConnectOut(driver,"{0}.{1}".format(mTarget.mNode,driven))
                except Exception,error:
                    log.error("----------------- {0}".format(error))                            
            else:
                log.warning(msg)
                self.log_info("Missing attr: '{0}'".format(a))            
        
        if l_missingDrivers:
            log.info(cgmGEN.logString_sub(_str_func,"Missing attrs {0}".format(len(l_missingDrivers))) )
            for a in l_missingDrivers:
                print a
                                
    def report(self):
        mBuffer = self.mBuffer
        
        for a in mBuffer.getAttrs(ud=True):
            if a in poseBuffer.attrMask:
                continue
            if 'XXX' in a:
                continue
            print a
            
    def log_wireDictTemplate(self):
        mBuffer = self.mBuffer
        
        print "{" +  "'{0}':".format(mBuffer.cgmName) + "{"
        for a in mBuffer.getAttrs(ud=True):
            if a in poseBuffer.attrMask:
                continue
            if 'XXX' in a:
                continue
            print "'{0}':None, ".format(a)        
        print "}}"
        
    def poseDat_get(self):
        mBuffer = self.mBuffer
        
        _res = {}
        _str = mBuffer.mNode
        
        for a in mBuffer.getAttrs(ud=True):
            if a in poseBuffer.attrMask:
                continue
            if 'XXX' in a:
                continue
            
            _res[a] = SDK.walk_sdkInfo("{0}.{1}".format(_str,a),stripObj = False)
        
        return _res
    


d_wireTMP = {
'inner_brow_left':{'control':'l_inner_brow_anim',
                   'wiringDict':{'brow_inr_up_left':{'driverAttr':'ty'},
                                 'brow_inr_dn_left':{'driverAttr':'-ty'},
                                 }},                             
'mid_brow_left':{'control':'l_mid_brow_anim',
                 'wiringDict':{'brow_mid_up_left':{'driverAttr':'ty'},
                               'brow_mid_dn_left':{'driverAttr':'-ty'}}}, 
'outer_brow_left':{'control':'l_outer_brow_anim',
                   'wiringDict':{'brow_outr_up_left':{'driverAttr':'ty'},
                                 'brow_outr_dn_left':{'driverAttr':'-ty'}}},
'inner_brow_right':{'control':'r_inner_brow_anim',
                   'wiringDict':{'brow_inr_up_right':{'driverAttr':'ty'},
                                 'brow_inr_dn_right':{'driverAttr':'-ty'},
                                 }},                             
'mid_brow_right':{'control':'r_mid_brow_anim',
                 'wiringDict':{'brow_mid_up_right':{'driverAttr':'ty'},
                               'brow_mid_dn_right':{'driverAttr':'-ty'}}}, 
'outer_brow_right':{'control':'r_outer_brow_anim',
                   'wiringDict':{'brow_outr_up_right':{'driverAttr':'ty'},
                                 'brow_outr_dn_right':{'driverAttr':'-ty'}}},

'center_brow':{'control':'center_brow_anim',
               'wiringDict':{'brow_squeeze':{'driverAttr':'-ty'},
                             }},

'mouth':{'control':'mouth_anim',
         'wiringDict':{'mouth_up':{'driverAttr':'ty'},
                       'mouth_dn':{'driverAttr':'-ty'},
                       'mouth_left':{'driverAttr':'tx'},
                       'mouth_right':{'driverAttr':'-tx'}}},


'jaw':{'control':'jaw_anim',
       'wiringDict':{'jaw_clench':{'driverAttr':'ty'},
                     'jaw_dn':{'driverAttr':'-ty'},
                     'jaw_left':{'driverAttr':'tx'},
                     'jaw_right':{'driverAttr':'-tx'}}},
'jawFWDBCK':{'control':'jaw_fwdBck_anim',
       'wiringDict':{'jaw_fwd':{'driverAttr':'tx'},
                     'jaw_back':{'driverAttr':'-tx'},
                     }},
"""    
    'eyeSqueeze_left':{'control':'l_eye_squeeze_anim',
                       'wiringDict':{'eyeSqueeze_up_left':{'driverAttr':'ty'},
                                     'eyeSqueeze_dn_left':{'driverAttr':'-ty'}}}, 
    'eyeSqueeze_right':{'control':'r_eye_squeeze_anim',
                       'wiringDict':{'eyeSqueeze_up_right':{'driverAttr':'ty'},
                                     'eyeSqueeze_dn_right':{'driverAttr':'-ty'}}}, 
"""

'cheekUpr_left':{'control':'l_uprCheek_anim',
              'wiringDict':{'cheek_up_left':{'driverAttr':'ty'},}},
'cheekUpr_right':{'control':'r_uprCheek_anim',
              'wiringDict':{'cheek_up_right':{'driverAttr':'ty'}}},   

'cheek_left':{'control':'l_cheek_anim',
              'wiringDict':{'cheek_blow_left':{'driverAttr':'tx'},
                            'cheek_suck_left':{'driverAttr':'-tx'}}},
'cheek_right':{'control':'r_cheek_anim',
              'wiringDict':{'cheek_blow_right':{'driverAttr':'tx'},
                            'cheek_suck_right':{'driverAttr':'-tx'}}},   

'sneer_left':{'control':'l_sneer_anim',
              'wiringDict':{'sneer_up_left':{'driverAttr':'ty'},}},
'sneer_right':{'control':'r_sneer_anim',
              'wiringDict':{'sneer_up_right':{'driverAttr':'ty'}}},   

'l_nostril':{'control':'l_nostril_anim',
             'wiringDict':{'nostril_in_left':{'driverAttr':'tx'},
                           'nostril_flare_left':{'driverAttr':'-tx'},
                           'nostril_up_left':{'driverAttr':'ty'}},
             },
'r_nostril':{'control':'r_nostril_anim',
             'wiringDict':{'nostril_in_right':{'driverAttr':'tx'},
                           'nostril_flare_right':{'driverAttr':'-tx'},
                           'nostril_up_right':{'driverAttr':'ty'}},
             },

'lipCorner_left':{'control':'l_lipCorner_anim',
                  'wiringDict':{#'lips_purse_left':{'driverAttr':'purse'},
                                #'lips_out_left':{'driverAttr':'out'},
                                #'lips_twistUp_left':{'driverAttr':'twist'},
                                #'lips_twistDn_left':{'driverAttr':'-twist'},
                                'lips_smile_left':{'driverAttr':'ty'},
                                'lips_frown_left':{'driverAttr':'-ty'},
                                'lips_narrow_left':{'driverAttr':'-tx'},
                                
                                #'lips_narrow_left':{'driverAttr':'-tx'},
                                #'lips_ooo_left':{'driverAttr':'-tx','driverAttr2':'ty','mode':'cornerBlend'},
                                
                                'lips_wide_left':{'driverAttr':'tx'}}},
'lipCorner_right':{'control':'r_lipCorner_anim',
                  'wiringDict':{#'lips_purse_right':{'driverAttr':'purse'},
                                #'lips_out_right':{'driverAttr':'out'},
                                #'lips_twistUp_right':{'driverAttr':'twist'},
                                #'lips_twistDn_right':{'driverAttr':'-twist'},
                                'lips_smile_right':{'driverAttr':'ty'},
                                'lips_frown_right':{'driverAttr':'-ty'},
                                'lips_narrow_right':{'driverAttr':'-tx'},
                                
                                #'lips_ooo_right':{'driverAttr':'-tx','driverAttr2':'ty','mode':'cornerBlend'},
                                #'lips_narrow_right':{'driverAttr':'-tx'},
                                'lips_wide_right':{'driverAttr':'tx'}}},

'dimpler_left':{'control':'l_dimpler_anim',
              'wiringDict':{'lips_dimpler_left':{'driverAttr':'ty'},}},
'dimpler_right':{'control':'r_dimpler_anim',
              'wiringDict':{'lips_dimpler_right':{'driverAttr':'ty'}}},
'grimace_left':{'control':'l_grimace_anim',
              'wiringDict':{'lips_pull_down_wide_left':{'driverAttr':'ty'},}},
'grimace_right':{'control':'r_grimace_anim',
              'wiringDict':{'lips_pull_down_wide_right':{'driverAttr':'ty'}}},

'lipCenter_upr':{'control':'upper_lipCenter_anim',
                 'wiringDict':{'lipCntr_upr_fwd':{'driverAttr':'fwdBack'},
                               'lipCntr_upr_back':{'driverAttr':'-fwdBack'},
                               'lipCntr_upr_up':{'driverAttr':'ty'},
                               'lipCntr_upr_dn':{'driverAttr':'-ty'},
                               'lipCntr_upr_left':{'driverAttr':'tx'},
                               'lipCntr_upr_right':{'driverAttr':'-tx'},                               
                               }}, 
'lipCenter_lwr':{'control':'lower_lipCenter_anim',
                 'wiringDict':{'lipCntr_lwr_fwd':{'driverAttr':'fwdBack'},
                               'lipCntr_lwr_back':{'driverAttr':'-fwdBack'},
                               'lipCntr_lwr_up':{'driverAttr':'ty'},
                               'lipCntr_lwr_dn':{'driverAttr':'-ty'},
                               'lipCntr_lwr_left':{'driverAttr':'tx'},
                               'lipCntr_lwr_right':{'driverAttr':'-tx'},                                  
                               }}, 

"""
'lipCenter_lwr':{'control':'lower_lipCenter_anim',
                 'wiringDict':{#'lipCntr_upr_fwd':{'driverAttr':'fwdBack'},
                               #'lipCntr_upr_back':{'driverAttr':'-fwdBack'},
                               'lips_funnel_lwr_right':{'driverAttr':'tx','driverAttr2':'ty','mode':'cornerBlend'},
                               'lips_funnel_lwr_left':{'driverAttr':'-tx','driverAttr2':'ty','mode':'cornerBlend'},                                                        
                               }}, """

'uprLip_left':{'control':'l_uprLip_anim',
              'wiringDict':{'lipUpr_rollIn_left':{'driverAttr':'-ty'},
                            'lips_funnel_upr_left':{'driverAttr':'-tx'},
                            'lips_presser_upr_left':{'driverAttr':'tx'},
                            'lipUpr_up_left':{'driverAttr':'ty'},
              }}, 
'uprLip_right':{'control':'r_uprLip_anim',
              'wiringDict':{'lipUpr_rollIn_right':{'driverAttr':'-ty'},
                            'lips_funnel_upr_right':{'driverAttr':'-tx'},
                            'lips_presser_upr_right':{'driverAttr':'tx'},
                            'lipUpr_up_right':{'driverAttr':'ty'},
              }}, 
'lwrLip_left':{'control':'l_lwrLip_anim',
              'wiringDict':{'lipLwr_rollIn_left':{'driverAttr':'-ty'},
                            'lips_funnel_lwr_left':{'driverAttr':'-tx'},
                            'lips_presser_lwr_left':{'driverAttr':'tx'},
                            'lipLwr_dn_left':{'driverAttr':'ty'},
              }}, 
'lwrLip_right':{'control':'r_lwrLip_anim',
              'wiringDict':{'lipLwr_rollIn_right':{'driverAttr':'-ty'},
                            'lips_funnel_lwr_right':{'driverAttr':'-tx'},
                            'lips_presser_lwr_right':{'driverAttr':'tx'},
                            'lipLwr_dn_right':{'driverAttr':'ty'},
              }}, 


'seal_fix':{'control':'r_dimpler_anim',
                 'wiringDict':{},
                 'simpleArgs':['mouthMove_anim.seal_left = l_lipSeal_anim.ty',
                               'mouthMove_anim.seal_right = r_lipSeal_anim.ty',
                               'mouthMove_anim.seal_center = ctr_lipSeal_anim.ty',
                               'mouthMove_anim.sealHeight = sealHeight_anim.ty',
                               ]},   


'lidsWideNarrow_right':{'control':'r_eye_wideNarrow_anim',
                        'wiringDict':{'lids_wide_right':{'driverAttr':'ty'},
                                      'lids_narrow_right':{'driverAttr':'-ty'}}},
'lidsWideNarrow_left':{'control':'l_eye_wideNarrow_anim',
                        'wiringDict':{'lids_wide_left':{'driverAttr':'ty'},
                                      'lids_narrow_left':{'driverAttr':'-ty'}}},

'eye_left':{'control':'l_eye_anim',
              'wiringDict':{'eye_ball_left_left':{'driverAttr':'tx'},
                            'eye_ball_left_right':{'driverAttr':'-tx'},
                            'eye_ball_up_left':{'driverAttr':'ty'},
                            'eye_ball_dn_left':{'driverAttr':'-ty'},
              }}, 
'eye_right':{'control':'r_eye_anim',
              'wiringDict':{'eye_ball_right_left':{'driverAttr':'tx'},
                            'eye_ball_right_right':{'driverAttr':'-tx'},
                            'eye_ball_up_right':{'driverAttr':'ty'},
                            'eye_ball_dn_right':{'driverAttr':'-ty'},
              }}, 

'eye_to_settings':{'control':'r_dimpler_anim',
                 'wiringDict':{},
                 'simpleArgs':['R_eyeOrb_rig_anim.blink = -r_eye_blink_anim.ty',
                               'L_eyeOrb_rig_anim.blink = -l_eye_blink_anim.ty',
                               'R_eyeOrb_rig_anim.blinkHeight = r_lid_sealHeight_anim.ty',
                               'L_eyeOrb_rig_anim.blinkHeight = l_lid_sealHeight_anim.ty',
                               ]},   

}
        


_d_faceControlsToConnect = {
'FACS_1':{
'mouth':{'control':'m_mouth_CTRL',
         'wiringDict':{'mouth_up':{'driverAttr':'ty'},
                       'mouth_dn':{'driverAttr':'-ty'},
                       'mouth_left':{'driverAttr':'tx'},
                       'mouth_right':{'driverAttr':'-tx'}}},
######### JAW SIDE #########################################                       
'jawMain':{'control':'m_jaw_CTRL',
         'wiringDict':{'jaw_open':{'driverAttr':'-ty'},
                       'jaw_right':{'driverAttr':'-tx'},
                       'jaw_left':{'driverAttr':'tx'},
                       'lips_presser_left':{'driverAttr':'ty'},
                       'lips_presser_right':{'driverAttr':'ty'}}},

'jawDepth':{'control':'m_jawForwardBackward_CTRL',
         'wiringDict':{'jaw_back':{'driverAttr':'-ty'},
                       'jaw_fwd':{'driverAttr':'ty'}}},

'mouthClose':{'control':'m_mouthClose_CTRL',
         'wiringDict':{'mouth_close':{'driverAttr':'ty'}}},

'upperLipRollIn':{'control':'m_upperLipRollIn_CTRL',
         'wiringDict':{'lips_uprRollIn':{'driverAttr':'ty'}}},

'lowerLipRollIn':{'control':'m_lowerLipRollIn_CTRL',
         'wiringDict':{'lips_lwrRollIn':{'driverAttr':'ty'}}},

'pucker':{'control':'m_pucker_CTRL',
         'wiringDict':{'lips_pucker':{'driverAttr':'ty'}}},

######### MUZZLE LEFT SIDE ####################################
'Smile_left':{'control':'l_smile_CTRL',
         'wiringDict':{'lips_smile_left':{'driverAttr':'ty'}}},

'Frown_left':{'control':'l_frown_CTRL',
         'wiringDict':{'lips_frown_left':{'driverAttr':'ty'}}},

'Presser_left':{'control':'l_presser_CTRL',
         'wiringDict':{'lips_presser_left':{'driverAttr':'ty'}}},

'Sneer_left':{'control':'l_sneer_CTRL',
         'wiringDict':{'sneer_up_left':{'driverAttr':'ty'}}},
'noseSneer_left' :{'control':'l_noseSneer_CTRL',
         'wiringDict':{'nose_sneer_left':{'driverAttr':'ty'}}},

'CheekRaise_L':{'control':'l_cheekRaiser_CTRL',
         'wiringDict':{'cheek_raise_left':{'driverAttr':'ty'}}},
'CheekPuffSuck_L':{'control':'l_cheekPuffSuck_CTRL',
         'wiringDict':{'cheek_puff_left':{'driverAttr':'-ty'},
                        'cheek_suck_left':{'driverAttr':'ty'}}},

######### MUZZLE RIGHT SIDE ####################################
'Smile_right':{'control':'r_smile_CTRL',
         'wiringDict':{'lips_smile_right':{'driverAttr':'ty'}}},

'Frown_right':{'control':'r_frown_CTRL',
         'wiringDict':{'lips_frown_right':{'driverAttr':'ty'}}},

'Presser_right':{'control':'r_presser_CTRL',
         'wiringDict':{'lips_presser_right':{'driverAttr':'ty'}}},

'Sneer_right':{'control':'r_sneer_CTRL',
         'wiringDict':{'sneer_up_right':{'driverAttr':'ty'}}},
'noseSneer_right':{'control':'r_noseSneer_CTRL',
         'wiringDict':{'nose_sneer_right':{'driverAttr':'ty'}}},

'CheekRaise_R':{'control':'r_cheekRaiser_CTRL',
         'wiringDict':{'cheek_raise_right':{'driverAttr':'ty'}}},

'CheekPuffSuck_R':{'control':'r_cheekPuffSuck_CTRL',
         'wiringDict':{'cheek_puff_right':{'driverAttr':'ty'},
                        'cheek_suck_right':{'driverAttr':'-ty'}}},


######### BROW CENTER SIDE ####################################

'browCenter':{'control':'m_browSqueeze_CTRL',
              'wiringDict':{'brow_squeeze':{'driverAttr':'-ty'},
                            }},

'eyeSqueeze_left':{'control':'l_eyeSqueeze_anim',
                   'wiringDict':{'eyeSqueeze_up_left':{'driverAttr':'ty'},
                                 'eyeSqueeze_dn_left':{'driverAttr':'-ty'}}}, 
'eyeSqueeze_right':{'control':'r_eyeSqueeze_anim',
                   'wiringDict':{'eyeSqueeze_up_right':{'driverAttr':'ty'},
                                 'eyeSqueeze_dn_right':{'driverAttr':'-ty'}}}, 


'cheekUpr_left':{'control':'l_uprCheek_anim',
              'wiringDict':{'cheek_up_left':{'driverAttr':'ty'},}},
'cheekUpr_right':{'control':'r_uprCheek_anim',
              'wiringDict':{'cheek_up_right':{'driverAttr':'ty'}}},   

'cheek_left':{'control':'l_uprCheek_anim',
              'wiringDict':{'cheek_blow_left':{'driverAttr':'tx'},
                            'cheek_suck_left':{'driverAttr':'-tx'}}},
'cheek_right':{'control':'r_uprCheek_anim',
              'wiringDict':{'cheek_blow_right':{'driverAttr':'tx'},
                            'cheek_suck_right':{'driverAttr':'-tx'}}},   

'sneer_left':{'control':'l_sneer_anim',
              'wiringDict':{'sneer_left':{'driverAttr':'ty'},}},
'sneer_right':{'control':'r_sneer_anim',
              'wiringDict':{'sneer_right':{'driverAttr':'ty'}}},   

'l_nostril':{'control':'l_nostril_anim',
             'wiringDict':{'nostril_in_left':{'driverAttr':'-tx'},
                           'nostril_out_left':{'driverAttr':'tx'},
                           'nostril_up_left':{'driverAttr':'ty'},
                           'nose_sneer_dn_left':{'driverAttr':'-ty'}},
             },
'r_nostril':{'control':'r_nostril_anim',
             'wiringDict':{'nostril_in_right':{'driverAttr':'-tx'},
                           'nostril_out_right':{'driverAttr':'tx'},
                           'nostril_up_right':{'driverAttr':'ty'},
                           'nose_sneer_dn_right':{'driverAttr':'-ty'}},
             },

                  },

######### BROW LEFT SIDE ####################################
'browUpDnInner_left':{'control':'l_browUpDnInner_CTRL',
              'wiringDict':{'brow_innrUp_left':{'driverAttr':'ty'},
                            'brow_innrDn_left':{'driverAttr':'-ty'},
                            }},
'browUpDnOuter_left':{'control':'l_browUpDnOuter_CTRL',
              'wiringDict':{'brow_outrUp_left':{'driverAttr':'ty'},
                            'brow_outrDn_left':{'driverAttr':'-ty'},
                            }},

######### BROW RIGHT SIDE ####################################
'browUpDnInner_right':{'control':'r_browUpDnInner_CTRL',
              'wiringDict':{'brow_innrUp_right':{'driverAttr':'ty'},
                            'brow_innrDn_right':{'driverAttr':'-ty'},
                            }},
'browUpDnOuter_right':{'control':'r_browUpDnOuter_CTRL',
              'wiringDict':{'brow_outrUp_right':{'driverAttr':'ty'},
                            'brow_outrDn_right':{'driverAttr':'-ty'},
                            }},

######### EYE LEFT SIDE ####################################
'eyeBlink_left':{'control':'l_eyeBlinkWide_CTRL',
              'wiringDict':{'eyeLids_wide_left':{'driverAttr':'ty'},
                            'eyeLids_blink_left':{'driverAttr':'-ty'},
                            }},

######### EYE RIGHT SIDE ####################################
'eyeBlink_right':{'control':'r_eyeBlinkWide_CTRL',
              'wiringDict':{'eyeLids_wide_right':{'driverAttr':'ty'},
                            'eyeLids_blink_right':{'driverAttr':'-ty'},
                            }},

######### END FACS DICTIONARY #################################
                  
'default':{
'browCenter':{'control':'center_brow_anim',
              'wiringDict':{'brow_center_up':{'driverAttr':'ty'},
                            'brow_center_dn':{'driverAttr':'-ty'}}},
                  
'inner_brow_left':{'control':'l_inner_brow_anim',
                   'wiringDict':{'brow_inr_up_left':{'driverAttr':'ty'},
                                 'brow_inr_dn_left':{'driverAttr':'-ty'},
                                 'brow_squeeze_left':{'driverAttr':'-tx'}}},                             
'mid_brow_left':{'control':'l_mid_brow_anim',
                 'wiringDict':{'brow_mid_up_left':{'driverAttr':'ty'},
                               'brow_mid_dn_left':{'driverAttr':'-ty'}}}, 
'outer_brow_left':{'control':'l_outer_brow_anim',
                   'wiringDict':{'brow_outr_up_left':{'driverAttr':'ty'},
                                 'brow_outr_dn_left':{'driverAttr':'-ty'}}},
'inner_brow_right':{'control':'r_inner_brow_anim',
                   'wiringDict':{'brow_inr_up_right':{'driverAttr':'ty'},
                                 'brow_inr_dn_right':{'driverAttr':'-ty'},
                                 'brow_squeeze_right':{'driverAttr':'-tx'}}},                             
'mid_brow_right':{'control':'r_mid_brow_anim',
                 'wiringDict':{'brow_mid_up_right':{'driverAttr':'ty'},
                               'brow_mid_dn_right':{'driverAttr':'-ty'}}}, 
'outer_brow_right':{'control':'r_outer_brow_anim',
                   'wiringDict':{'brow_outr_up_right':{'driverAttr':'ty'},
                                 'brow_outr_dn_right':{'driverAttr':'-ty'}}}, 

'eyeSqueeze_left':{'control':'l_eyeSqueeze_anim',
                   'wiringDict':{'eyeSqueeze_up_left':{'driverAttr':'ty'},
                                 'eyeSqueeze_dn_left':{'driverAttr':'-ty'}}}, 
'eyeSqueeze_right':{'control':'r_eyeSqueeze_anim',
                   'wiringDict':{'eyeSqueeze_up_right':{'driverAttr':'ty'},
                                 'eyeSqueeze_dn_right':{'driverAttr':'-ty'}}}, 


'cheek_left':{'control':'l_cheek_anim',
              'wiringDict':{'cheek_up_left':{'driverAttr':'ty'},
                            'cheek_dn_left':{'driverAttr':'-ty'},
                            'cheek_blow_left':{'driverAttr':'tx'},
                            'cheek_suck_left':{'driverAttr':'-tx'}}},
'cheek_right':{'control':'r_cheek_anim',
              'wiringDict':{'cheek_up_right':{'driverAttr':'ty'},
                            'cheek_dn_right':{'driverAttr':'-ty'},
                            'cheek_blow_right':{'driverAttr':'tx'},
                            'cheek_suck_right':{'driverAttr':'-tx'}}},   

'nose_left':{'control':'l_nose_anim',
             'wiringDict':{'nose_in_left':{'driverAttr':'-tx'},
                           'nose_out_left':{'driverAttr':'tx'},
                           'nose_sneer_up_left':{'driverAttr':'ty'},
                           'nose_sneer_dn_left':{'driverAttr':'-ty'}},
             'simpleArgs':['{0}.nose_seal_up_cntr_left = {0}.nose_sneer_up_left * {0}.seal_center',
                           '{0}.nose_seal_up_outr_left = {0}.nose_sneer_up_left * {0}.seal_left'
                           ]},
'nose_right':{'control':'r_nose_anim',
             'wiringDict':{'nose_in_right':{'driverAttr':'-tx'},
                           'nose_out_right':{'driverAttr':'tx'},
                           'nose_sneer_up_right':{'driverAttr':'ty'},
                           'nose_sneer_dn_right':{'driverAttr':'-ty'}},
             'simpleArgs':['{0}.nose_seal_up_cntr_right = {0}.nose_sneer_up_right * {0}.seal_center',
                           '{0}.nose_seal_up_outr_right = {0}.nose_sneer_up_right * {0}.seal_right',
                           ]},

'lipCorner_left':{'control':'l_lipCorner_anim',
                  'wiringDict':{'lips_purse_left':{'driverAttr':'purse'},
                                'lips_out_left':{'driverAttr':'out'},
                                'lips_twistUp_left':{'driverAttr':'twist'},
                                'lips_twistDn_left':{'driverAttr':'-twist'},
                                'lips_smile_left':{'driverAttr':'ty'},
                                'lips_frown_left':{'driverAttr':'-ty'},                                                    
                                'lips_narrow_left':{'driverAttr':'-tx'},
                                'lips_wide_left':{'driverAttr':'tx'}}},
'lipCorner_right':{'control':'r_lipCorner_anim',
                  'wiringDict':{'lips_purse_right':{'driverAttr':'purse'},
                                'lips_out_right':{'driverAttr':'out'},
                                'lips_twistUp_right':{'driverAttr':'twist'},
                                'lips_twistDn_right':{'driverAttr':'-twist'},
                                'lips_smile_right':{'driverAttr':'ty'},
                                'lips_frown_right':{'driverAttr':'-ty'},                                                    
                                'lips_narrow_right':{'driverAttr':'-tx'},
                                'lips_wide_right':{'driverAttr':'tx'}}},                            
                  
'lipCenter_upr':{'control':'upper_lipCenter_anim',
                 'wiringDict':{'lipCntr_upr_fwd':{'driverAttr':'fwdBack'},
                               'lipCntr_upr_back':{'driverAttr':'-fwdBack'},
                               'lipCntr_upr_up_left':{'driverAttr':'tx','driverAttr2':'ty','mode':'cornerBlend'},
                               'lipCntr_upr_up_right':{'driverAttr':'-tx','driverAttr2':'ty','mode':'cornerBlend'},
                               'lipCntr_upr_dn_left':{'driverAttr':'tx','driverAttr2':'-ty','mode':'cornerBlend'},
                               'lipCntr_upr_dn_right':{'driverAttr':'-tx','driverAttr2':'-ty','mode':'cornerBlend'},                                                           
                               }},     
'lipCenter_lwr':{'control':'lower_lipCenter_anim',
                 'wiringDict':{'lipCntr_lwr_fwd':{'driverAttr':'fwdBack'},
                               'lipCntr_lwr_back':{'driverAttr':'-fwdBack'},
                               'lipCntr_lwr_up_left':{'driverAttr':'tx','driverAttr2':'ty','mode':'cornerBlend'},
                               'lipCntr_lwr_up_right':{'driverAttr':'-tx','driverAttr2':'ty','mode':'cornerBlend'},
                               'lipCntr_lwr_dn_left':{'driverAttr':'tx','driverAttr2':'-ty','mode':'cornerBlend'},
                               'lipCntr_lwr_dn_right':{'driverAttr':'-tx','driverAttr2':'-ty','mode':'cornerBlend'},                                                           
                               }},                              

'mouth':{'control':'mouth_anim',
         'wiringDict':{'seal_center':{'driverAttr':'seal_center','noTrack':True},
                       'seal_left':{'driverAttr':'seal_left','noTrack':True},
                       'seal_right':{'driverAttr':'seal_right','noTrack':True},
                       'mouth_twist_left':{'driverAttr':'twist'},
                       'mouth_twist_right':{'driverAttr':'-twist'},
                       'mouth_fwd':{'driverAttr':'fwdBack'},
                       'mouth_back':{'driverAttr':'-fwdBack'},
                       'mouth_up':{'driverAttr':'ty'},
                       'mouth_dn':{'driverAttr':'-ty'},
                       'mouth_left':{'driverAttr':'tx'},
                       'mouth_right':{'driverAttr':'-tx'}}},
         #'simpleArgs':['{0}.seal_center = {0}.seal_center * {0}.lipUpr_up_left'.format(__attrHolder)]},

'uprLip_left':{'control':'l_uprLip_anim',
              'wiringDict':{'lipUpr_rollIn_left':{'driverAttr':'tx'},
                            'lipUpr_rollOut_left':{'driverAttr':'-tx','driverAttr2':'{0}.lips_wide_left',
                                                   'mode':'negVNeg'},
                            'lipUpr_up_left':{'driverAttr':'ty'},
                            'lipUpr_moreOut_left':{'driverAttr':'roll'},
                            'lipUpr_moreIn_left':{'driverAttr':'-roll'},
                            },
              'simpleArgs':['{0}.lipUpr_upSeal_outr_left = {0}.seal_left * {0}.lipUpr_up_left',
                            '{0}.lipUpr_upSeal_cntr_left = {0}.seal_center * {0}.lipUpr_up_left',
                            '{0}.lipUpr_seal_out_cntr_left = {0}.seal_left * {0}.lipUpr_rollOut_left',
                            '{0}.lipUpr_seal_out_outr_left = {0}.seal_center * {0}.lipUpr_rollOut_left'
                            ]}, 
'uprLip_right':{'control':'r_uprLip_anim',
               'wiringDict':{'lipUpr_rollIn_right':{'driverAttr':'tx'},
                             'lipUpr_rollOut_right':{'driverAttr':'-tx','driverAttr2':'{0}.lips_wide_right',
                                                     'mode':'negVNeg'},
                             'lipUpr_up_right':{'driverAttr':'ty'},
                             'lipUpr_moreOut_right':{'driverAttr':'roll'},
                             'lipUpr_moreIn_right':{'driverAttr':'-roll'},
                             },
               'simpleArgs':['{0}.lipUpr_upSeal_outr_right = {0}.seal_right * {0}.lipUpr_up_right',
                             '{0}.lipUpr_upSeal_cntr_right = {0}.seal_center * {0}.lipUpr_up_right',
                             '{0}.lipUpr_seal_out_cntr_right = {0}.seal_right * {0}.lipUpr_rollOut_right',
                             '{0}.lipUpr_seal_out_outr_right = {0}.seal_center * {0}.lipUpr_rollOut_right',
                             ]},
'lwrLip_left':{'control':'l_lwrLip_anim',
               'wiringDict':{'lipLwr_rollIn_left':{'driverAttr':'tx'},
                             'lipLwr_rollOut_left':{'driverAttr':'-tx','driverAttr2':'{0}.lips_wide_left',
                                                    'mode':'negVNeg'},
                             'lipLwr_dn_left':{'driverAttr':'ty'},
                             'lipLwr_moreOut_left':{'driverAttr':'roll'},
                             'lipLwr_moreIn_left':{'driverAttr':'-roll'},
                             },
               'simpleArgs':['{0}.lipLwr_dnSeal_outr_left = {0}.seal_left * {0}.lipLwr_dn_left',
                             '{0}.lipLwr_dnSeal_cntr_left = {0}.seal_center * {0}.lipLwr_dn_left',
                             '{0}.lipLwr_seal_out_cntr_left = {0}.seal_left * {0}.lipLwr_rollOut_left',
                             '{0}.lipLwr_seal_out_outr_left = {0}.seal_center * {0}.lipLwr_rollOut_left'
                             ]}, 
'lwrLip_right':{'control':'r_lwrLip_anim',
                'wiringDict':{'lipLwr_rollIn_right':{'driverAttr':'tx'},
                              'lipLwr_rollOut_right':{'driverAttr':'-tx','driverAttr2':'{0}.lips_wide_right','mode':'negVNeg'},
                              'lipLwr_dn_right':{'driverAttr':'ty'},
                              'lipLwr_moreOut_right':{'driverAttr':'roll'},
                              'lipLwr_moreIn_right':{'driverAttr':'-roll'},
                              },
                'simpleArgs':['{0}.lipLwr_dnSeal_outr_right = {0}.seal_right * {0}.lipLwr_dn_right',
                              '{0}.lipLwr_dnSeal_cntr_right = {0}.seal_center * {0}.lipLwr_dn_right',
                              '{0}.lipLwr_seal_out_cntr_right = {0}.seal_right * {0}.lipLwr_rollOut_right',
                              '{0}.lipLwr_seal_out_outr_right = {0}.seal_center * {0}.lipLwr_rollOut_right'
                              ]},                             

'jaw':{'control':'jaw_anim',
       'wiringDict':{'jaw_fwd':{'driverAttr':'fwdBack'},
                     'jaw_back':{'driverAttr':'-fwdBack'},
                     'jaw_clench':{'driverAttr':'ty'},
                     'jaw_dn':{'driverAttr':'-ty'},
                     'jaw_left':{'driverAttr':'tx'},
                     'jaw_right':{'driverAttr':'-tx'},
                     'jDiff_dn_smile_left':{'driverAttr':'{0}.lips_smile_left',
                                            'driverAttr2':'{0}.jaw_dn',
                                            'driverAttr3':'{0}.driver_smile_dn_pull',
                                            'driverAttr4':'{0}.seal_left',
                                            'mode':'multMinusFactoredValue'},
                     'jDiff_dn_smile_right':{'driverAttr':'{0}.lips_smile_right',
                                             'driverAttr2':'{0}.jaw_dn',
                                             'driverAttr3':'{0}.driver_smile_dn_pull',
                                             'driverAttr4':'{0}.seal_right',
                                             'mode':'multMinusFactoredValue'},
                     'jDiff_dn_frown_left':{'driverAttr':'{0}.lips_frown_left',
                                            'driverAttr2':'{0}.jaw_dn',
                                            'driverAttr3':'{0}.driver_frown_dn_pull',
                                            'driverAttr4':'{0}.seal_left',
                                            'mode':'multMinusFactoredValue'},
                     'jDiff_dn_frown_right':{'driverAttr':'{0}.lips_frown_right',
                                             'driverAttr2':'{0}.jaw_dn',
                                             'driverAttr3':'{0}.driver_frown_dn_pull',
                                             'driverAttr4':'{0}.seal_right',
                                             'mode':'multMinusFactoredValue'},                                                  
                     },
       'simpleArgs':['{0}.jDiff_fwd_seal_cntr_left = {0}.seal_center * {0}.jaw_fwd',
                     '{0}.jDiff_fwd_seal_cntr_right = {0}.seal_center * {0}.jaw_fwd',
                     '{0}.jDiff_fwd_seal_outr_left = {0}.seal_left * {0}.jaw_fwd',
                     '{0}.jDiff_fwd_seal_outr_right = {0}.seal_right * {0}.jaw_fwd',
                     '{0}.jDiff_back_seal_cntr_left = {0}.seal_center * {0}.jaw_back',
                     '{0}.jDiff_back_seal_cntr_right = {0}.seal_center * {0}.jaw_back',
                     '{0}.jDiff_back_seal_outr_left = {0}.seal_left * {0}.jaw_back',
                     '{0}.jDiff_back_seal_outr_right = {0}.seal_right * {0}.jaw_back',
                     '{0}.jDiff_dn_seal_cntr_left = {0}.seal_center * {0}.jaw_dn',
                     '{0}.jDiff_dn_seal_cntr_right = {0}.seal_center * {0}.jaw_dn',
                     '{0}.jDiff_dn_seal_outr_left = {0}.seal_left * {0}.jaw_dn',
                     '{0}.jDiff_dn_seal_outr_right = {0}.seal_right * {0}.jaw_dn',
                     '{0}.jDiff_left_seal_cntr_left = {0}.seal_center * {0}.jaw_left',
                     '{0}.jDiff_left_seal_cntr_right = {0}.seal_center * {0}.jaw_left',
                     '{0}.jDiff_left_seal_outr_left = {0}.seal_left * {0}.jaw_left',
                     '{0}.jDiff_left_seal_outr_right = {0}.seal_right * {0}.jaw_left',
                     '{0}.jDiff_right_seal_cntr_left = {0}.seal_center * {0}.jaw_right',
                     '{0}.jDiff_right_seal_cntr_right = {0}.seal_center * {0}.jaw_right',
                     '{0}.jDiff_right_seal_outr_left = {0}.seal_left * {0}.jaw_right',
                     '{0}.jDiff_right_seal_outr_right = {0}.seal_right * {0}.jaw_right',
                     ]},

                  
}}



__attrHolder = 'cat'
_d_faceControlsToConnectBAK = {
'default':{
'browCenter':{'control':'center_brow_anim',
              'wiringDict':{'brow_center_up':{'driverAttr':'ty'},
                            'brow_center_dn':{'driverAttr':'-ty'}}},
                  
'inner_brow_left':{'control':'l_inner_brow_anim',
                   'wiringDict':{'brow_inr_up_left':{'driverAttr':'ty'},
                                 'brow_inr_dn_left':{'driverAttr':'-ty'},
                                 'brow_squeeze_left':{'driverAttr':'-tx'}}},                             
'mid_brow_left':{'control':'l_mid_brow_anim',
                 'wiringDict':{'brow_mid_up_left':{'driverAttr':'ty'},
                               'brow_mid_dn_left':{'driverAttr':'-ty'}}}, 
'outer_brow_left':{'control':'l_ outer_brow_anim',
                   'wiringDict':{'brow_outr_up_left':{'driverAttr':'ty'},
                                 'brow_outr_dn_left':{'driverAttr':'-ty'}}},
'inner_brow_right':{'control':'r_inner_brow_anim',
                   'wiringDict':{'brow_inr_up_right':{'driverAttr':'ty'},
                                 'brow_inr_dn_right':{'driverAttr':'-ty'},
                                 'brow_squeeze_right':{'driverAttr':'-tx'}}},                             
'mid_brow_right':{'control':'r_mid_brow_anim',
                 'wiringDict':{'brow_mid_up_right':{'driverAttr':'ty'},
                               'brow_mid_dn_right':{'driverAttr':'-ty'}}}, 
'outer_brow_right':{'control':'r_outer_brow_anim',
                   'wiringDict':{'brow_outr_up_right':{'driverAttr':'ty'},
                                 'brow_outr_dn_right':{'driverAttr':'-ty'}}}, 

'eyeSqueeze_left':{'control':'l_eyeSqueeze_anim',
                   'wiringDict':{'eyeSqueeze_up_left':{'driverAttr':'ty'},
                                 'eyeSqueeze_dn_left':{'driverAttr':'-ty'}}}, 
'eyeSqueeze_right':{'control':'r_eyeSqueeze_anim',
                   'wiringDict':{'eyeSqueeze_up_right':{'driverAttr':'ty'},
                                 'eyeSqueeze_dn_right':{'driverAttr':'-ty'}}}, 
                  
'cheek_left':{'control':'l_cheek_anim',
              'wiringDict':{'cheek_up_left':{'driverAttr':'ty'},
                            'cheek_dn_left':{'driverAttr':'-ty'},
                            'cheek_blow_left':{'driverAttr':'tx'},
                            'cheek_suck_left':{'driverAttr':'-tx'}}},
'cheek_right':{'control':'r_cheek_anim',
              'wiringDict':{'cheek_up_right':{'driverAttr':'ty'},
                            'cheek_dn_right':{'driverAttr':'-ty'},
                            'cheek_blow_right':{'driverAttr':'tx'},
                            'cheek_suck_right':{'driverAttr':'-tx'}}},   
                  
'nose_left':{'control':'l_nose_anim',
             'wiringDict':{'nose_in_left':{'driverAttr':'-tx'},
                           'nose_out_left':{'driverAttr':'tx'},
                           'nose_sneer_up_left':{'driverAttr':'ty'},
                           'nose_sneer_dn_left':{'driverAttr':'-ty'}},
             'simpleArgs':['{0}.nose_seal_up_cntr_left = {0}.nose_sneer_up_left * {0}.seal_center'.format(__attrHolder),
                           '{0}.nose_seal_up_outr_left = {0}.nose_sneer_up_left * {0}.seal_left'.format(__attrHolder)
                           ]},
'nose_right':{'control':'r_nose_anim',
             'wiringDict':{'nose_in_right':{'driverAttr':'-tx'},
                           'nose_out_right':{'driverAttr':'tx'},
                           'nose_sneer_up_right':{'driverAttr':'ty'},
                           'nose_sneer_dn_right':{'driverAttr':'-ty'}},
             'simpleArgs':['{0}.nose_seal_up_cntr_right = {0}.nose_sneer_up_right * {0}.seal_center'.format(__attrHolder),
                           '{0}.nose_seal_up_outr_right = {0}.nose_sneer_up_right * {0}.seal_right'.format(__attrHolder)
                           ]},                            
                                           
                  
'lipCorner_left':{'control':'l_lipCorner_anim',
                  'wiringDict':{'lips_purse_left':{'driverAttr':'purse'},
                                'lips_out_left':{'driverAttr':'out'},
                                'lips_twistUp_left':{'driverAttr':'twist'},
                                'lips_twistDn_left':{'driverAttr':'-twist'},
                                'lips_smile_left':{'driverAttr':'ty'},
                                'lips_frown_left':{'driverAttr':'-ty'},                                                    
                                'lips_narrow_left':{'driverAttr':'-tx'},
                                'lips_wide_left':{'driverAttr':'tx'}}},
'lipCorner_right':{'control':'r_lipCorner_anim',
                  'wiringDict':{'lips_purse_right':{'driverAttr':'purse'},
                                'lips_out_right':{'driverAttr':'out'},
                                'lips_twistUp_right':{'driverAttr':'twist'},
                                'lips_twistDn_right':{'driverAttr':'-twist'},
                                'lips_smile_right':{'driverAttr':'ty'},
                                'lips_frown_right':{'driverAttr':'-ty'},                                                    
                                'lips_narrow_right':{'driverAttr':'-tx'},
                                'lips_wide_right':{'driverAttr':'tx'}}},                            
                  
'lipCenter_upr':{'control':'upper_lipCenter_anim',
                 'wiringDict':{'lipCntr_upr_fwd':{'driverAttr':'fwdBack'},
                               'lipCntr_upr_back':{'driverAttr':'-fwdBack'},
                               'lipCntr_upr_up_left':{'driverAttr':'tx','driverAttr2':'ty','mode':'cornerBlend'},
                               'lipCntr_upr_up_right':{'driverAttr':'-tx','driverAttr2':'ty','mode':'cornerBlend'},
                               'lipCntr_upr_dn_left':{'driverAttr':'tx','driverAttr2':'-ty','mode':'cornerBlend'},
                               'lipCntr_upr_dn_right':{'driverAttr':'-tx','driverAttr2':'-ty','mode':'cornerBlend'},                                                           
                               }},     
'lipCenter_lwr':{'control':'lower_lipCenter_anim',
                 'wiringDict':{'lipCntr_lwr_fwd':{'driverAttr':'fwdBack'},
                               'lipCntr_lwr_back':{'driverAttr':'-fwdBack'},
                               'lipCntr_lwr_up_left':{'driverAttr':'tx','driverAttr2':'ty','mode':'cornerBlend'},
                               'lipCntr_lwr_up_right':{'driverAttr':'-tx','driverAttr2':'ty','mode':'cornerBlend'},
                               'lipCntr_lwr_dn_left':{'driverAttr':'tx','driverAttr2':'-ty','mode':'cornerBlend'},
                               'lipCntr_lwr_dn_right':{'driverAttr':'-tx','driverAttr2':'-ty','mode':'cornerBlend'},                                                           
                               }},                              


'mouth':{'control':'mouth_anim',
         'wiringDict':{'seal_center':{'driverAttr':'seal_center','noTrack':True},
                       'seal_left':{'driverAttr':'seal_left','noTrack':True},
                       'seal_right':{'driverAttr':'seal_right','noTrack':True},
                       'mouth_twist_left':{'driverAttr':'twist'},
                       'mouth_twist_right':{'driverAttr':'-twist'},
                       'mouth_fwd':{'driverAttr':'fwdBack'},
                       'mouth_back':{'driverAttr':'-fwdBack'},
                       'mouth_up':{'driverAttr':'ty'},
                       'mouth_dn':{'driverAttr':'-ty'},
                       'mouth_left':{'driverAttr':'tx'},
                       'mouth_right':{'driverAttr':'-tx'}}},
         #'simpleArgs':['{0}.seal_center = {0}.seal_center * {0}.lipUpr_up_left'.format(__attrHolder)]},

'uprLip_left':{'control':'l_uprLip_anim',
              'wiringDict':{'lipUpr_rollIn_left':{'driverAttr':'tx'},
                            'lipUpr_rollOut_left':{'driverAttr':'-tx','driverAttr2':'{0}.lips_wide_left'.format(__attrHolder),'mode':'negVNeg'},
                            'lipUpr_up_left':{'driverAttr':'ty'},
                            'lipUpr_moreOut_left':{'driverAttr':'roll'},
                            'lipUpr_moreIn_left':{'driverAttr':'-roll'},
                            },
              'simpleArgs':['{0}.lipUpr_upSeal_outr_left = {0}.seal_left * {0}.lipUpr_up_left'.format(__attrHolder),
                            '{0}.lipUpr_upSeal_cntr_left = {0}.seal_center * {0}.lipUpr_up_left'.format(__attrHolder),
                            '{0}.lipUpr_seal_out_cntr_left = {0}.seal_left * {0}.lipUpr_rollOut_left'.format(__attrHolder),
                            '{0}.lipUpr_seal_out_outr_left = {0}.seal_center * {0}.lipUpr_rollOut_left'.format(__attrHolder)                                                        
                            ]}, 
'uprLip_right':{'control':'r_uprLip_anim',
               'wiringDict':{'lipUpr_rollIn_right':{'driverAttr':'tx'},
                             'lipUpr_rollOut_right':{'driverAttr':'-tx','driverAttr2':'{0}.lips_wide_right'.format(__attrHolder),'mode':'negVNeg'},
                             'lipUpr_up_right':{'driverAttr':'ty'},
                             'lipUpr_moreOut_right':{'driverAttr':'roll'},
                             'lipUpr_moreIn_right':{'driverAttr':'-roll'},
                             },
               'simpleArgs':['{0}.lipUpr_upSeal_outr_right = {0}.seal_right * {0}.lipUpr_up_right'.format(__attrHolder),
                             '{0}.lipUpr_upSeal_cntr_right = {0}.seal_center * {0}.lipUpr_up_right'.format(__attrHolder),
                             '{0}.lipUpr_seal_out_cntr_right = {0}.seal_right * {0}.lipUpr_rollOut_right'.format(__attrHolder),
                             '{0}.lipUpr_seal_out_outr_right = {0}.seal_center * {0}.lipUpr_rollOut_right'.format(__attrHolder)                                                        
                             ]},
'lwrLip_left':{'control':'l_lwrLip_anim',
               'wiringDict':{'lipLwr_rollIn_left':{'driverAttr':'tx'},
                             'lipLwr_rollOut_left':{'driverAttr':'-tx','driverAttr2':'{0}.lips_wide_left'.format(__attrHolder),'mode':'negVNeg'},
                             'lipLwr_dn_left':{'driverAttr':'ty'},
                             'lipLwr_moreOut_left':{'driverAttr':'roll'},
                             'lipLwr_moreIn_left':{'driverAttr':'-roll'},
                             },
               'simpleArgs':['{0}.lipLwr_dnSeal_outr_left = {0}.seal_left * {0}.lipLwr_dn_left'.format(__attrHolder),
                             '{0}.lipLwr_dnSeal_cntr_left = {0}.seal_center * {0}.lipLwr_dn_left'.format(__attrHolder),
                             '{0}.lipLwr_seal_out_cntr_left = {0}.seal_left * {0}.lipLwr_rollOut_left'.format(__attrHolder),
                             '{0}.lipLwr_seal_out_outr_left = {0}.seal_center * {0}.lipLwr_rollOut_left'.format(__attrHolder)                                                        
                             ]}, 
'lwrLip_right':{'control':'r_lwrLip_anim',
                'wiringDict':{'lipLwr_rollIn_right':{'driverAttr':'tx'},
                              'lipLwr_rollOut_right':{'driverAttr':'-tx','driverAttr2':'{0}.lips_wide_right'.format(__attrHolder),'mode':'negVNeg'},
                              'lipLwr_dn_right':{'driverAttr':'ty'},
                              'lipLwr_moreOut_right':{'driverAttr':'roll'},
                              'lipLwr_moreIn_right':{'driverAttr':'-roll'},
                              },
                'simpleArgs':['{0}.lipLwr_dnSeal_outr_right = {0}.seal_right * {0}.lipLwr_dn_right'.format(__attrHolder),
                              '{0}.lipLwr_dnSeal_cntr_right = {0}.seal_center * {0}.lipLwr_dn_right'.format(__attrHolder),
                              '{0}.lipLwr_seal_out_cntr_right = {0}.seal_right * {0}.lipLwr_rollOut_right'.format(__attrHolder),
                              '{0}.lipLwr_seal_out_outr_right = {0}.seal_center * {0}.lipLwr_rollOut_right'.format(__attrHolder)                                                        
                              ]},                             



'jaw':{'control':'jaw_anim',
       'wiringDict':{'jaw_fwd':{'driverAttr':'fwdBack'},
                     'jaw_back':{'driverAttr':'-fwdBack'},
                     'jaw_clench':{'driverAttr':'ty'},
                     'jaw_dn':{'driverAttr':'-ty'},
                     'jaw_left':{'driverAttr':'tx'},
                     'jaw_right':{'driverAttr':'-tx'},
                     'jDiff_dn_smile_left':{'driverAttr':'{0}.lips_smile_left'.format(__attrHolder),
                                            'driverAttr2':'{0}.jaw_dn'.format(__attrHolder),
                                            'driverAttr3':'{0}.driver_smile_dn_pull'.format(__attrHolder),
                                            'driverAttr4':'{0}.seal_left'.format(__attrHolder),
                                            'mode':'multMinusFactoredValue'},
                     'jDiff_dn_smile_right':{'driverAttr':'{0}.lips_smile_right'.format(__attrHolder),
                                             'driverAttr2':'{0}.jaw_dn'.format(__attrHolder),
                                             'driverAttr3':'{0}.driver_smile_dn_pull'.format(__attrHolder),
                                             'driverAttr4':'{0}.seal_right'.format(__attrHolder),
                                             'mode':'multMinusFactoredValue'},
                     'jDiff_dn_frown_left':{'driverAttr':'{0}.lips_frown_left'.format(__attrHolder),
                                            'driverAttr2':'{0}.jaw_dn'.format(__attrHolder),
                                            'driverAttr3':'{0}.driver_frown_dn_pull'.format(__attrHolder),
                                            'driverAttr4':'{0}.seal_left'.format(__attrHolder),
                                            'mode':'multMinusFactoredValue'},
                     'jDiff_dn_frown_right':{'driverAttr':'{0}.lips_frown_right'.format(__attrHolder),
                                             'driverAttr2':'{0}.jaw_dn'.format(__attrHolder),
                                             'driverAttr3':'{0}.driver_frown_dn_pull'.format(__attrHolder),
                                             'driverAttr4':'{0}.seal_right'.format(__attrHolder),
                                             'mode':'multMinusFactoredValue'},                                                  
                     },
       'simpleArgs':['{0}.jDiff_fwd_seal_cntr_left = {0}.seal_center * {0}.jaw_fwd'.format(__attrHolder),
                     '{0}.jDiff_fwd_seal_cntr_right = {0}.seal_center * {0}.jaw_fwd'.format(__attrHolder),
                     '{0}.jDiff_fwd_seal_outr_left = {0}.seal_left * {0}.jaw_fwd'.format(__attrHolder),
                     '{0}.jDiff_fwd_seal_outr_right = {0}.seal_right * {0}.jaw_fwd'.format(__attrHolder),
                     '{0}.jDiff_back_seal_cntr_left = {0}.seal_center * {0}.jaw_back'.format(__attrHolder),
                     '{0}.jDiff_back_seal_cntr_right = {0}.seal_center * {0}.jaw_back'.format(__attrHolder),
                     '{0}.jDiff_back_seal_outr_left = {0}.seal_left * {0}.jaw_back'.format(__attrHolder),
                     '{0}.jDiff_back_seal_outr_right = {0}.seal_right * {0}.jaw_back'.format(__attrHolder),
                     '{0}.jDiff_dn_seal_cntr_left = {0}.seal_center * {0}.jaw_dn'.format(__attrHolder),
                     '{0}.jDiff_dn_seal_cntr_right = {0}.seal_center * {0}.jaw_dn'.format(__attrHolder),
                     '{0}.jDiff_dn_seal_outr_left = {0}.seal_left * {0}.jaw_dn'.format(__attrHolder),
                     '{0}.jDiff_dn_seal_outr_right = {0}.seal_right * {0}.jaw_dn'.format(__attrHolder),
                     '{0}.jDiff_left_seal_cntr_left = {0}.seal_center * {0}.jaw_left'.format(__attrHolder),
                     '{0}.jDiff_left_seal_cntr_right = {0}.seal_center * {0}.jaw_left'.format(__attrHolder),
                     '{0}.jDiff_left_seal_outr_left = {0}.seal_left * {0}.jaw_left'.format(__attrHolder),
                     '{0}.jDiff_left_seal_outr_right = {0}.seal_right * {0}.jaw_left'.format(__attrHolder),
                     '{0}.jDiff_right_seal_cntr_left = {0}.seal_center * {0}.jaw_right'.format(__attrHolder),
                     '{0}.jDiff_right_seal_cntr_right = {0}.seal_center * {0}.jaw_right'.format(__attrHolder),
                     '{0}.jDiff_right_seal_outr_left = {0}.seal_left * {0}.jaw_right'.format(__attrHolder),
                     '{0}.jDiff_right_seal_outr_right = {0}.seal_right * {0}.jaw_right'.format(__attrHolder),                                                 
                     ]},
'jawNDVSetup':{'control':__attrHolder,
               'wiringDict':{},
               'simpleArgs':['{0}.jawDriven_back_tz = {0}.jaw_back * {0}.driver_jaw_back_tz'.format(__attrHolder),
                             '{0}.jawDriven_fwd_tz = {0}.jaw_fwd * {0}.driver_jaw_fwd_tz'.format(__attrHolder),                                                                                                  
                             '{0}.jawDriven_dn_tz = {0}.jaw_dn * {0}.driver_jaw_dn_tz'.format(__attrHolder),
                             '{0}.jawDriven_dn_rx = {0}.jaw_dn * {0}.driver_jaw_dn_rx'.format(__attrHolder),
                             '{0}.jawDriven_left_tx = {0}.jaw_left * {0}.driver_jaw_left_tx'.format(__attrHolder),
                             '{0}.jawDriven_left_ry = {0}.jaw_left * {0}.driver_jaw_left_ry'.format(__attrHolder),
                             '{0}.jawDriven_left_rz = {0}.jaw_left * {0}.driver_jaw_left_rz'.format(__attrHolder),                                                          
                             '{0}.jawDriven_right_tx = {0}.jaw_right * {0}.driver_jaw_right_tx'.format(__attrHolder),
                             '{0}.jawDriven_right_ry = {0}.jaw_right * {0}.driver_jaw_right_ry'.format(__attrHolder),
                             '{0}.jawDriven_right_rz = {0}.jaw_right * {0}.driver_jaw_right_rz'.format(__attrHolder),#...
                             '{0}.jawNDV_tx = {0}.jawBase_tx + {0}.jawDriven_left_tx + {0}.jawDriven_right_tx'.format(__attrHolder),
                             '{0}.jawNDV_ty = {0}.jawBase_ty'.format(__attrHolder),                                                          
                             '{0}.jawNDV_tz = {0}.jawBase_tz + {0}.jawDriven_back_tz + {0}.jawDriven_fwd_tz + {0}.jawDriven_dn_tz'.format(__attrHolder), 
                             '{0}.jawNDV_rx = {0}.jawBase_rx + {0}.jawDriven_dn_rx'.format(__attrHolder), 
                             '{0}.jawNDV_ry = {0}.jawBase_ry + {0}.jawDriven_left_ry + {0}.jawDriven_right_ry'.format(__attrHolder), 
                             '{0}.jawNDV_rz = {0}.jawBase_rz + {0}.jawDriven_left_rz + {0}.jawDriven_right_rz'.format(__attrHolder), 
                             ]}}}


def getBlendDriverDict(node = 'blendShape1', ignore = ['SHAPES']):
    import cgm.core.lib.attribute_utils as ATTR
    d = {}
    for a in mc.listAttr(node+'.weight',m=1):
        _plug = ATTR.get_driver(node,a) 
        if _plug:
            _check = False
            for check in ignore:
                if check in _plug:
                    _check = True
                    break        
            if not _check:                                       
                d[a] = _plug
    return d


def setBlendDriverDict(node = 'blendShape1', d_wiring = {}):
    import cgm.core.lib.attribute_utils as ATTR
    for t,s in d_wiring.iteritems():
        log.info("Set: {} | {}".format(t,s))
        try:
            ATTR.connect(s,node+'.'+t)
        except Exception,err:
            print err