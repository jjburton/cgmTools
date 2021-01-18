"""
------------------------------------------
face_utils: cgm.core.mrs.lib
Author: Josh Burton
Website : http://www.cgmonks.com
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

from cgm.core.lib import attribute_utils as ATTR
from cgm.core.lib import search_utils as SEARCH


_d_faceBufferAttributes = {
    'default':{"jaw":{'attrs':['dn','clench','left','right','fwd','back']},
               "eye":{'attrs':['squeeze','blink','upr_up','upr_dn',
                               'ball_left','ball_right','ball_up','ball_dn'
                               'lwr_up','lwr_dn'],
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
               
               "lips":{'attrs':['smile','wide','narrow','purse','twistUp','twistDn','out','frown'],
                       'sideAttrs':'*'},
               
               "lipUpr":{'attrs':['up','in','out','fwd'],
                       'sideAttrs':'*'},
               "lipLwr":{'attrs':['up','in','out','fwd'],
                       'sideAttrs':'*'},                           

               "lips":{'attrs':['smile','wide','narrow','purse','twistUp','twistDn','out','frown'],
                       'sideAttrs':'*'},
               
               "lipCntr_upr":{'attrs':['fwd','back','up','dn','rollIn','rollOut'],
                       'sideAttrs':['up','dn','rollIn','rollOut']},
               "lipCntr_lwr":{'attrs':['fwd','back','up','dn','rollIn','rollOut'],
                       'sideAttrs':['up','dn','rollIn','rollOut']},            

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


def push_toSDKGroup(nodes = []):
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
        
        d[mObj] = {'t': mObj.translate,
                   'r': mObj.rotate,
                   's':mObj.scale,
                   'mGrp':mGrp}
        
        mObj.resetAttrs(['t','r','s'])
        
    
    for mObj,_d in d.iteritems():
        _d['mGrp'].translate = _d['t']
        _d['mGrp'].rotate = _d['r']
        _d['mGrp'].scale = _d['s']
        
    pprint.pprint(d)

def SDKGroups_select(nodes=[]):
    if nodes:
        ml = cgmMeta.asMeta(nodes)
    else:
        ml = cgmMeta.asMeta(sl=1)
        
    ml_sdks = []
    for mObj in ml:
        ml_sdks.append(mObj.getMessage('sdkGroup')[0])
    mc.select(ml_sdks)    
    return ml_sdks

class poseBuffer():
    attrDat = None
    attrMask = ['cgmName','cgmType','mClass','mNodeID','mClassGrp','mSystemRoot']
    
    def __init__(self,node = None, 
                 name = None,
                 baseName = 'face',
                 faceType = 'default',
                 *args,**kws):
        """ 
        """
        _sel = mc.ls(sl=1)

        self.attrDat = {}
        

        self.attrDat = _d_faceBufferAttributes.get(faceType) or None
       
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
        
    def buffer_verify(self, addNonSplits = True):
        """
        addNonSplits | add a lips_smile for example for splitting to L/R
        """
        _str_func = 'buffer_verify'
        mBuffer = self.mBuffer
        d_buffer = _d_faceBufferAttributes.get(mBuffer.cgmName) or {}
        
        if not d_buffer:
            raise ValueError, "No attrDat"
        
        l_sections = d_buffer.keys()
        l_sections.sort()
        
        mBuffer.addAttr("Rest",attrType = 'float',hidden = False)
        
        for section in l_sections:
            mBuffer.addAttr("XXX_{0}_attrs_XXX".format(section),
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
                    mBuffer.addAttr("_".join(n),attrType = 'float',hidden = False)

        
    def report(self):
        mBuffer = self.mBuffer
        
        for a in mBuffer.getAttrs(ud=True):
            if a in poseBuffer.attrMask:
                continue
            if 'XXX' in a:
                continue
            print a
            
        #pprint.pprint(self.attrDat)
