"""
------------------------------------------
Builder: cgm.core.mrs
Author: Josh Burton
email: cgmonks.info@gmail.com

Website : https://github.com/jjburton/cgmTools/wiki
------------------------------------------

================================================================
"""
__MAYALOCAL = 'BUILDER'

import random
import re
import copy
import time
import pprint
import os
import subprocess, os
import sys

# From Red9 =============================================================
from Red9.core import Red9_Meta as r9Meta
from Red9.core import Red9_AnimationUtils as r9Anim
import Red9.core.Red9_CoreUtils as r9Core

#========================================================================
import logging
import importlib
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
#========================================================================

import maya.cmds as mc


# From cgm ==============================================================
from cgm.core import cgm_General as cgmGEN
import cgm.core.cgmPy.path_Utils as PATHS

from cgm.core import cgm_Meta as cgmMeta
from cgm.core import cgm_RigMeta as RIGMETA
#from cgm.core import cgm_PuppetMeta as PUPPETMETA
import cgm.core.cgm_Dat as CGMDAT
#import cgm.core.mrs.ShapeDat as SHAPEDAT
import cgm.core.mrs.MRSDat as MRSDAT

from cgm.core.classes import GuiFactory as CGMUI
#from cgm.core.lib import curve_Utils as CURVES
from cgm.core.lib import attribute_utils as ATTR
from cgm.core.lib import position_utils as POS
from cgm.core.lib import math_utils as MATH
#from cgm.core.lib import distance_utils as DIST
#from cgm.core.lib import snap_utils as SNAP
#from cgm.core.lib import rigging_utils as RIGGING
#from cgm.core.rigger.lib import joint_Utils as JOINTS
#from cgm.core.lib import search_utils as SEARCH
from cgm.core.lib import rayCaster as RAYS
from cgm.core.cgmPy import validateArgs as VALID
#from cgm.core.classes import NodeFactory as NODEFAC
#from cgm.core.cgmPy import path_Utils as PATH
from cgm.core.mrs import RigBlocks as RIGBLOCKS
from cgm.core.lib import shared_data as SHARED
from cgm.core.mrs.lib import builder_utils as BUILDERUTILS
from cgm.core.mrs.lib import block_utils as BLOCKUTILS
from cgm.core.mrs.lib import blockShapes_utils as BLOCKSHAPES
from cgm.core.mrs.lib import ModuleControlFactory as MODULECONTROLFACTORY
from cgm.core.mrs.lib import ModuleShapeCaster as MODULESHAPECASTER
from cgm.core.rig import ik_utils as IK
import cgm.core.tools.lib.tool_calls as TOOLCALLS

from cgm.core.mrs.lib import rigFrame_utils as RIGFRAME
import cgm.core.lib.string_utils as CORESTRINGS

from cgm.core.mrs.lib import general_utils as BLOCKGEN
from cgm.core.mrs import Helpers as HELPERS
import cgm.core.tools.lib.tool_chunks as UICHUNKS
import cgm.core.tools.toolbox as TOOLBOX
import cgm.core.mrs.lib.shared_dat as BLOCKSHARE
import cgm.core.tools.markingMenus.lib.contextual_utils as CONTEXT
import cgm.core.tools.snapTools as SNAPTOOLS
import cgm.core.lib.list_utils as LISTS
from cgm.core.lib import nameTools as NAMETOOLS
import cgm.core.mrs.lib.rigShapes_utils as RIGSHAPES
import cgm.core.mrs.lib.post_utils as MRSPOST

import cgm.images.icons as cgmIcons
_path_imageFolder = PATHS.Path(cgmIcons.__file__).up().asFriendly()

#for m in BLOCKGEN,BLOCKSHARE,BUILDERUTILS,SHARED,CONTEXT,CGMUI:
    #reload(m)
_d_blockTypes = {}

# Factory 
#=====================================================================================================
import cgm.core.classes.GuiFactory as cgmUI
mUI = cgmUI.mUI

d_state_colors = {'define':[1,.3,.3],
                  'form':[1,.5,0],
                  'prerig':[1,.9,0],
                  'skeleton':[0,.7,.7],
                  'rig':[.310,1,0],
                  'default':[.3,.2,.5],
                  }

d_keyColors = {'profile':'define',
               'basic':'define',
               'name':'define',
               'proxySurface':'form',
               'squashStretch':'rig',
               'space':'rig',
               'post':'rig'}        

d_uiStateSubColors = {}
for k,color in list(d_state_colors.items()):
    d_uiStateSubColors[k] = [v *.95 for v in color ]
    

#Generate our ui colors
d_uiStateUIColors = {}

for k,color in list(d_state_colors.items()):
    _d = {}
    d_uiStateUIColors[k] = _d
    _d['base'] = [v *.95 for v in color ]
    _d['light'] = [ MATH.Clamp(v*2.0,None,1.0) for v in color ]
    _d['bgc'] = [ v * .8 for v in _d['base'] ]
    _d['button'] = [v *.6 for v in _d['bgc'] ]


#>>> Root settings =============================================================
__version__ =  cgmGEN.__RELEASESTRING
_sidePadding = 25



def reloadMRSStuff():
    log.info("reloading...")
    from cgm.core.mrs.lib import module_utils as MODULEUTILS
    from cgm.core.mrs.lib import puppet_utils as PUPPETUTILS
    
    for m in [BUILDERUTILS,BLOCKUTILS,BLOCKSHARE,SHARED,RIGFRAME,cgmGEN,IK,
              BLOCKGEN,CONTEXT,BLOCKSHAPES,NAMETOOLS,CGMUI,RIGSHAPES,MRSPOST,MODULEUTILS,PUPPETUTILS,
              MODULECONTROLFACTORY,MODULESHAPECASTER]:
        print(m)
        cgmGEN._reloadMod(m)
    log.info(cgmGEN._str_subLine)
    

def check_cgm():
    return
    try:
        cgmMeta.cgmNode(nodeType='decomposeMatrix').delete()
    except:
        import cgm
        cgm.core._reload()

"""
import cgm.core.mrs.Builder as BUILDER
reload(BUILDER)
BUILDER.ui_blockEditor('master_masterBlock')
"""
global BLOCKEDITOR
BLOCKEDITOR = None

global UI
UI = None

global BLOCKPICKER
BLOCKPICKER = None

def blockEditor_get(mBlock=None):
    global BLOCKEDITOR
    
    if not mBlock:
        mBlock = BLOCKGEN.block_getFromSelected()
        
    if BLOCKEDITOR:
        log.info('cached...')
        if mBlock:
            BLOCKEDITOR.uiFunc_loadBlock(mBlock)
        try:
            if not BLOCKEDITOR(q=1, visible=True):
                BLOCKEDITOR.show()
            return  BLOCKEDITOR
        except Exception as err:
            log.error(err)
    return ui_blockEditor(mBlock)

def ui_get(create=True):
    global UI
    if UI:
        log.info('cached...')
        UI.show()
        return UI
    if not create:
        return
    return ui()

def blockPicker_get(mBlock=None):
    global BLOCKPICKER
    
    if not mBlock:
        mBlock = BLOCKGEN.block_getFromSelected()
        
    if BLOCKPICKER:
        log.info('cached...')
        if mBlock:
            BLOCKPICKER.uiFunc_loadBlock(mBlock)
        #try:
        if not BLOCKPICKER(q=1, visible=True):
            BLOCKPICKER.show()
        #except Exception,err:
        #    log.error(err)
            
        return  BLOCKPICKER
            
    return ui_blockPicker(mBlock)

class ui_blockPicker(cgmUI.cgmGUI):
    USE_Template = 'cgmUITemplate'
    WINDOW_NAME = 'mrsBlockPicker'    
    WINDOW_TITLE = 'Block Picker | - {0}'.format(__version__)
    DEFAULT_MENU = None
    RETAIN = True
    MIN_BUTTON = False
    MAX_BUTTON = False
    FORCE_DEFAULT_SIZE = True  #always resets the size of the window when its re-created  
    DEFAULT_SIZE = 300,600
    
    _d_ui_annotations = {'select':"Select rigBlocks in maya from ui."}
    
    def __init__(self,mBlock = None, *a,**kws):
        global BLOCKPICKER

        super(ui_blockPicker, self).__init__(*a,**kws)
        
        self.mBlockDict = {}
        self.uiPopUpMenu_children = None
        self.uiPopUpMenu_siblings = None
        #self.uiMenu_load = None 
        self.uiFunc_loadBlock(mBlock)
        BLOCKPICKER = self
        self.mUI_builder = None
        self.uiMenu_snap = None
        
        
    def buildMenu_block(self,*args,**kws):
        self.uiMenu_block.clear()   
        _menu = self.uiMenu_block
        d_s = {'Set Side':{},
               'Set Position':{},
               'Skeleton':{'Joints | get bind':{'ann':self._d_ui_annotations.get('Joints | get bind'),
                               'call':cgmGEN.Callback(self.uiFunc_blockCall,
                                      'atUtils','skeleton_getBind',
                                      **{'select':1,'mode':'noSelect'})},
                           'Joints | tag':{'ann':self._d_ui_annotations.get('Joints | tag'),
                                                          'call':cgmGEN.Callback(self.uiFunc_blockCall,
                                                                 'atUtils','skeleton_getBind',
                                                                 **{'tag':1})}                           
                           },
       
               'Rig':{'Step Build':{'ann':self._d_ui_annotations.get('step build'),
                               'call':cgmGEN.Callback(self.uiFunc_blockCall,
                                                      'stepUI',
                                                      **{'updateUI':0,'mode':'stepBuild'})},
                      'Prechecks':{'ann':'Precheck blocks for problems',
                                   'call':cgmGEN.Callback(self.uiFunc_blockCall,
                                                          'asRigFactory',
                                                          **{'updateUI':0,'mode':'prechecks'})},                      
                      'Proxy | Verify':{'ann':self._d_ui_annotations.get('verify proxy mesh'),
                               'call':cgmGEN.Callback(self.uiFunc_blockCall,
                                      'verify_proxyMesh',
                                      **{'updateUI':0})},
                      'Proxy | Delete':{'ann':self._d_ui_annotations.get('delete proxy mesh'),
                               'call':cgmGEN.Callback(self.uiFunc_blockCall,
                                      'proxyMesh_delete',
                                      **{'updateUI':0})},                      
                      'Rig Connect':{'ann':self._d_ui_annotations.get('connect rig'),
                                        'call':cgmGEN.Callback(self.uiFunc_contextModuleCall,'rig_connect',**{'updateUI':0})},
                      'Rig Disconnect':{'ann':self._d_ui_annotations.get('disconnect rig'),
                                     'call':cgmGEN.Callback(self.uiFunc_contextModuleCall,'rig_disconnect',**{'updateUI':0})},                      
                      'Reset Controls':{'ann':self._d_ui_annotations.get('reset rig controls'),
                               'call':cgmGEN.Callback(self.uiFunc_contextModuleCall,
                                      'rig_reset',
                                      **{'updateUI':0})},
                                       
                      'Query Nodes':{'ann':self._d_ui_annotations.get('query rig nodes'),
                               'call':cgmGEN.Callback(self.uiFunc_blockCall,
                                      'atUtils','rigNodes_get',
                                      **{'updateUI':0,'report':True})},},
               
               
               'Parent':{'To Active':{'ann':'Set parent block to active block',
                                  'call':cgmGEN.Callback(self.uiFunc_blockCall,
                                                         'atUtils','blockParent_set',
                                                         **{'mode':'setParentToActive'})},
                         'To Selected':{'ann':'Set parent block to active block',
                                      'call':cgmGEN.Callback(self.uiFunc_blockCall,
                                                             'atUtils','blockParent_set',
                                                             **{'mode':'setParentToSelected'})},                         
                         'Clear':{'ann':'Clear blockParent',
                                           'call':cgmGEN.Callback(self.uiFunc_blockCall,
                                                                  'atUtils','blockParent_set',
                                                                  **{'parent':False})},},
               'Siblings':{'Form | Push Sub shapers':{'ann':'Push Sub shaper values to siblings',
                                  'call':cgmGEN.Callback(self.uiFunc_blockCall,
                                                         'atUtils','siblings_pushSubShapers',
                                                         **{})},
                           'Form | Push Handles':{'ann':'Push form shaper values to siblings',
                                               'call':cgmGEN.Callback(self.uiFunc_blockCall,
                                                                      'atUtils','siblings_pushFormHandles',
                                                                      **{})},                           
                         'Prerig | Push Handles':{'ann':'Push prerig handle values to siblings',
                                  'call':cgmGEN.Callback(self.uiFunc_blockCall,
                                                         'atUtils','siblings_pushPrerigHandles',
                                                         **{})}},               
               'Form':{'Snap to RP':{'ann':'Snap handles to rp plane',
                                 'call':cgmGEN.Callback(self.uiFunc_blockCall,
                                 'atUtils', 'handles_snapToRotatePlane','form',True,
                                 **{'updateUI':0})},},
               
               'Names':{ 
                   'divTags':['nameList | edit'],
                   'Name | Set tag':{'ann':'Set the name tag of the block and rename dags',
                                     'call':cgmGEN.Callback(self.uiFunc_blockCall,
                                                            'atUtils','set_nameTag', **{})},
                   'Position | Set tag':{'ann':'Set the position tag of the block and rename dags',
                                         'call':cgmGEN.Callback(self.uiFunc_blockCall,
                                                                'atUtils','set_position',
                                                                **{'ui':True})},
                  'nameList | reset':{'ann':'Reset the name list to the profile',
                                 'call':cgmGEN.Callback(self.uiFunc_blockCall,
                                                        'atUtils','nameList_resetToProfile',
                                                        **{})},
                  'nameList | edit':{'ann':'Ui Prompt to edit nameList',
                                      'call':cgmGEN.Callback(self.uiFunc_blockCall,
                                                             'atUtils','nameList_uiPrompt',
                                                             **{})},                  
                   'nameList | iter baseName':{'ann':'Set nameList values from name attribute',
                                 'call':cgmGEN.Callback(self.uiFunc_blockCall,
                                                        'atUtils','set_nameListFromName',
                                                        **{})}},
               
               
               
               'Prerig':{
                   'Visualize | RP Pos':{'ann':'Create locator at the where the system thinks your rp handle will be',
                             'call':cgmGEN.Callback(self.uiFunc_blockCall,
                                'atUtils', 'prerig_get_rpBasePos',
                                **{'markPos':1,'updateUI':0})},
                   'Visualize | Up Vector':{'ann':'Create a curve showing what the assumed rp up vector is',
                                         'call':cgmGEN.Callback(self.uiFunc_blockCall,
                                            'atUtils', 'prerig_get_upVector',
                                            **{'markPos':1,'updateUI':0})},                   
                   'Snap RP to Orient':{'ann':'Snap rp hanlde to orient vector',
                            'call':cgmGEN.Callback(self.uiFunc_blockCall,
                                   'atUtils', 'prerig_snapRPtoOrientHelper',
                                   **{'updateUI':0})},
                   'Snap to RP':{'ann':'Snap handles to rp plane',
                                 'call':cgmGEN.Callback(self.uiFunc_blockCall,
                                 'atUtils', 'handles_snapToRotatePlane','prerig',True,
                                 **{'updateUI':0})},
                   'Handles | Lock':{'ann':'Lock the prerig handles',
                                 'call':cgmGEN.Callback(self.uiFunc_blockCall,
                                 'atUtils', 'prerig_handlesLock',True,
                                 **{'updateUI':0})},
                   'Handles | Unlock':{'ann':'Unlock the prerig handles',
                                   'call':cgmGEN.Callback(self.uiFunc_blockCall,
                                   'atUtils', 'prerig_handlesLock',False,
                                   **{'updateUI':0})},
                   'divTags':['Handles | Lock','Query Indices',
                              'Visualize | RP Pos',
                              ],                   
                   'Arrange | Linear Spaced':{'ann':'Unlock the prerig handles',
                                             'call':cgmGEN.Callback(self.uiFunc_blockCall,
                                             'atUtils', 'prerig_handlesLayout','spaced','linear',
                                             **{'updateUI':0})},
                   'Arrange | Linear Even':{'ann':'Unlock the prerig handles',
                                             'call':cgmGEN.Callback(self.uiFunc_blockCall,
                                             'atUtils', 'prerig_handlesLayout','even','linear',
                                             **{'updateUI':0})},
                   'Arrange | Cubic Even':{'ann':'Unlock the prerig handles',
                                            'call':cgmGEN.Callback(self.uiFunc_blockCall,
                                            'atUtils', 'prerig_handlesLayout','even','cubicRebuild',
                                            **{'updateUI':0})},
                   'Arrange | Cubic Spaced':{'ann':'Unlock the prerig handles',
                                             'call':cgmGEN.Callback(self.uiFunc_blockCall,
                                             'atUtils', 'prerig_handlesLayout','spaced','cubicRebuild',
                                             **{'updateUI':0})},                                      

                   },
               'Geo':{
                   'order':['Block Mesh','Block Loft | Default',
                            'Block Loft | Even',
                            'Puppet Mesh',
                            'Unified','Unified [Skinned]',
                            'Parts Mesh','Parts Mesh [Skinned]',
                            'Proxy Mesh [Parented]','Delete',
                            ],
                   'divTags':['Delete'],
                   'headerTags':['Puppet Mesh'],
                   'Block Mesh':{'ann':'Generate Simple mesh',
                               'call':cgmGEN.CB(self.uiFunc_blockCall,
                                                'atUtils','create_simpleMesh',
                                                **{'connect':False,'updateUI':0,'deleteHistory':1})},
                   'Block Loft | Default':{'ann':'Generate Simple mesh with history to tweak the loft manually',
                               'call':cgmGEN.CB(self.uiFunc_blockCall,
                                                'atUtils','create_simpleMesh',
                                                **{'connect':False,'updateUI':0,'deleteHistory':0})},
                   'Block Loft | Even':{'ann':'Generate Simple mesh with history to tweak the loft manually',
                                 'call':cgmGEN.CB(self.uiFunc_blockCall,
                                                  'atUtils','create_simpleMesh',
                                                  **{'connect':False,'updateUI':0,'deleteHistory':0,
                                                     'loftMode':'evenCubic'})},                   
                   'Unified':{'ann':"Create a unified unskinned puppet mesh from the active block's basis.",
                              'call':cgmGEN.CB(self.uiFunc_blockCall,'atUtils','puppetMesh_create',
                                               **{'unified':True,'skin':False})},
                   'Unified [Skinned]':{
                       'ann':"Create parts skinned puppet mesh from the active block's basis.",
                       'call':cgmGEN.CB(self.uiFunc_blockCall,'atUtils','puppetMesh_create',
                                         **{'unified':True,'skin':True})},
                   'Parts Mesh':{
                       'ann':"Create parts unskinned puppet mesh from the active block's basis.",
                       'call':cgmGEN.CB(self.uiFunc_blockCall,'atUtils','puppetMesh_create',
                                         **{'unified':False,'skin':False})},
                   'Parts Mesh [Skinned]':{
                       'ann':"Create parts skinned puppet mesh from the active block's basis.",
                       'call':cgmGEN.CB(self.uiFunc_blockCall,'atUtils','puppetMesh_create',
                                         **{'unified':False,'skin':True})},
                   'Proxy Mesh [Parented]':{
                       'ann':"Create proxy puppet mesh parented to skin joints from the active block's basis.",
                       'call':cgmGEN.CB(self.uiFunc_blockCall,'atUtils','puppetMesh_create',
                                         **{'proxy':True,'unified':False,'skin':False})},
                   'Unified Proxy [Skinned]':{
                       'ann':"Create proxy puppet mesh skinned and unified to the puppet",
                       'call':cgmGEN.CB(self.uiFunc_blockCall,'atUtils','puppetMesh_create',
                                         **{'proxy':True,'unified':True,'skin':True})},
                   'Unified Proxy':{
                       'ann':"Create unified proxy puppet",
                       'call':cgmGEN.CB(self.uiFunc_blockCall,'atUtils','puppetMesh_create',
                                         **{'proxy':True,'unified':False,'skin':True})},
                   'Delete':{
                       'ann':"Remove skinned or wired puppet mesh",
                       'call':cgmGEN.CB(self.uiFunc_blockCall,'atUtils','puppetMesh_delete')},
                   },
               
               }

        
        """
        for state in ['define','form','prerig']:
            d_s['blockDat']['order'].append('Load {0}'.format(state))
            d_s['blockDat']['Load {0}'.format(state)] = {
                'ann':"Load {0} blockDat in context".format(state),
                'call':cgmGEN.Callback(self.uiFunc_blockCall,
                                       'atUtils','blockDat_load_state',state,
                                       **{})}"""
        
        
        l_keys = sorted(d_s)
        
        l_check = ['Define','Form','Prerig','Skeleton','Rig']
        l_check.reverse()
        for k in l_check:
            if k in l_keys:
                l_keys.remove(k)
                l_keys.insert(0,k)
                
        for s in l_keys:
            d = d_s[s]
            divTags = d.get('divTags',[])
            headerTags = d.get('headerTags',[])
            
            _sub = mUI.MelMenuItem(_menu, subMenu = True,tearOff=True,
                            label = s,
                            en=True,)
            
            if s == 'Set Side':
                for i,side in enumerate(['none','left','right','center']):
                    mUI.MelMenuItem(_sub,
                                    l = side,
                                    ann='Set contextual block side to: {0}'.format(side),
                                    c = cgmGEN.Callback(self.uiFunc_blockCall,
                                                        'atUtils','set_side',side,
                                                        **{}))                
                
            if s == 'Set Position':
                for i,position in enumerate(BLOCKSHARE._l_positions):
                    mUI.MelMenuItem(_sub,
                                    label = position,
                                    ann = 'Specify the position for the current block to : {0}'.format(position),
                                    c = cgmGEN.Callback(self.uiFunc_blockCall,
                                                        'atUtils','set_position',position,
                                                        **{}))             
            
            l_keys2 = d.get('order',False)
            if l_keys2:
                for k in list(d.keys()):
                    if k not in l_keys2:
                        l_keys2.append(k)
            else:
                l_keys2 = sorted(d)
            for l in l_keys2:
                if l in ['divTags','headerTags','order']:
                    continue
                if l in divTags:
                    mUI.MelMenuItemDiv(_sub)                
                if l in headerTags:
                    mUI.MelMenuItem(_sub,divider = True,
                                    label = l,
                                    en=False)
                    """
                    mUI.MelMenuItemDiv(_sub)
                    mUI.MelMenuItem(_sub,
                                    label = "--- {0} ---".format(l.upper()),
                                    en=False)
                    mUI.MelMenuItemDiv(_sub)"""
                    continue
                d2 = d[l]
                mUI.MelMenuItem(_sub,
                                label = l,
                                ann = d2.get('ann',''),
                                c=d2.get('call'))
                
            if s == 'Rig':
                mUI.MelMenuItemDiv(_menu)            



        log.info("Context menu rebuilt")        
        
    def uiFunc_profileSet(self,mode = 'build',**kws):
        _str_func = ''
        _updateUI = kws.pop('updateUI',True)
        _profile = kws.pop('buildProfile',None)
        
        
        _profile = self.__dict__['uiOM_{0}'.format(mode)].getValue()
        
        
        
        #if not _profile:
        #    return log.error("|{0}| >> blockProfile arg".format(_str_func))
        
        log.info("Setting Profile: {0} | {1}".format(mode,_profile))
        
        if mode == 'build':
            uiFunc_blockCall(self,'atUtils','buildProfile_load',_profile)
        elif mode == 'block':
            uiFunc_blockCall(self,'atUtils','blockProfile_load',_profile)
        else:
            return log.error("Unknown Profile mode: {0}".format(mode))

        return

    def buildMenu_snap( self, force=False, *args, **kws):
        #if self.uiMenu_snap and force is not True:
        #    return
        #self.uiMenu_snap.clear()
        
        UICHUNKS.uiSection_snap(self.uiMenu_snap)
        mUI.MelMenuItemDiv(self.uiMenu_snap)
        
        
    def buildMenu_vis(self,*args,**kws):
        self.uiMenu_vis.clear()   
        _menu = self.uiMenu_vis
        
        d_s = {'Focus':{'Clear':{'ann':self._d_ui_annotations.get('focus clear'),
                                 'call':cgmGEN.Callback(self.uiFunc_blockCall,
                                        'focus',False,None,
                                        **{'updateUI':0})},
                        'Vis':{'ann':self._d_ui_annotations.get('focus vis'),
                               'call':cgmGEN.Callback(self.uiFunc_blockCall,
                                      'focus',True,'vis',
                                      **{'updateUI':0})},
                        'Template':{'ann':self._d_ui_annotations.get('focus template'),
                                    'call':cgmGEN.Callback(self.uiFunc_blockCall,
                                           'focus',True,'template',
                                           **{'updateUI':0})},},
                   }


        
        """
        for state in ['define','form','prerig']:
            d_s['blockDat']['order'].append('Load {0}'.format(state))
            d_s['blockDat']['Load {0}'.format(state)] = {
                'ann':"Load {0} blockDat in context".format(state),
                'call':cgmGEN.Callback(self.uiFunc_blockCall,
                                       'atUtils','blockDat_load_state',state,
                                       **{})}"""
        
        
        #l_keys = sorted(d)
                
        for s in sorted(d_s):
            d = d_s[s]
            divTags = d.get('divTags',[])
            headerTags = d.get('headerTags',[])
            
                
            _sub = mUI.MelMenuItem(_menu, subMenu = True,tearOff=True,
                            label = s,
                            en=True,)

            l_keys2 = d.get('order',False)
            if l_keys2:
                for k in list(d.keys()):
                    if k not in l_keys2:
                        l_keys2.append(k)
            else:
                l_keys2 = sorted(d)
            for l in l_keys2:
                if l in ['divTags','headerTags','order']:
                    continue
                if l in divTags:
                    mUI.MelMenuItemDiv(_sub)                
                if l in headerTags:
                    mUI.MelMenuItemDiv(_sub)
                    mUI.MelMenuItem(_sub,
                                    label = "--- {0} ---".format(l.upper()),
                                    en=False)
                    mUI.MelMenuItemDiv(_sub)
                    continue
                d2 = d[l]
                mUI.MelMenuItem(_sub,
                                label = l,
                                ann = d2.get('ann',''),
                                c=d2.get('call'))

        #Vis menu -----------------------------------------------------------------------------
        for a in ['Measure','RotatePlane','Labels','ProximityMode']:
            _sub = mUI.MelMenuItem(_menu, subMenu = True,tearOff=False,
                                   label = a,
                                   en=True,)
            if a == 'ProximityMode':
                _l = ['off','inherit','proximity']
            else:
                _l = ['off','on']
                
            for i,v in enumerate(_l):
                mUI.MelMenuItem(_sub,
                                l = v,
                                ann='Set visibility of: {0} | {1}'.format(a,v),
                                c = cgmGEN.Callback(self.uiFunc_blockCall,
                                            'atUtils', 'blockAttr_set',
                                            **{"vis{0}".format(a):i,'updateUI':0}))
                
                
                
        d_shared = {'formNull':{},
                    'prerigNull':{}}
        
        l_settings = ['visibility']
        l_locks = ['rigBlock','formNull','prerigNull']
        l_enums = []
    
        for n in l_locks:
            _sub = mUI.MelMenuItem(_menu, subMenu = True,tearOff=False,
                                   label = n,
                                   en=True,)
            
    
            if n in l_settings:
                l_options = ['hide','show']
                _mode = 'moduleSettings'
            elif n in l_locks:
                l_options = ['unlock','lock']
                _mode = 'moduleSettings'
                if n != 'rigBlock':
                    _plug = d_shared[n].get('plug',n)
            else:
                l_options = ['off','lock','on']
                _mode = 'puppetSettings'
                
            for v,o in enumerate(l_options):
                if n == 'rigBlock':
                    mUI.MelMenuItem(_sub,
                                    l = o,
                                    ann='Set visibility of: {0} | {1}'.format(a,v),
                                    c = cgmGEN.Callback(self.uiFunc_blockCall,
                                                'atUtils','templateAttrLock',v,**{'updateUI':0}))
                         
  
                else:
                    mUI.MelMenuItem(_sub,
                                    l = o,
                                    ann='Set visibility of: {0} | {1}'.format(a,v),
                                    c = cgmGEN.Callback(self.uiFunc_blockCall,
                                                'atUtils', 'messageConnection_setAttr',
                                                _plug,**{'template':v,'updateUI':0}))                    


        
            for n in l_settings:
                l_options = ['hide','show']
    
                for v,o in enumerate(l_options):
                    mUI.MelMenuItem(_sub,
                                    l = o,
                                    ann='Set visibility of: {0} | {1}'.format(a,v),
                                    c=cgmGEN.Callback(self.uiFunc_blockCall,
                                                'atUtils', 'blockAttr_set',
                                                **{n:v,'updateUI':0}))                    

        log.info("Context menu rebuilt")
        
    @cgmGEN.Timer
    def uiFunc_contextModuleCall(self,*args,**kws):
        try:
            _str_func = ''

            if not self.mBlock:
                return
            mBlock = self.mBlock            
            
            mc.refresh(su=1)

            res = RIGBLOCKS.contextual_module_method_call(mBlock,'self',*args,**kws)
            log.debug("|{0}| >> res: {1}".format(_str_func,res))

        finally:
            mc.refresh(su=0)
            
    def uiFunc_blockCall(self,*args,**kws):
        try:
            if not self.mBlock:
                return
            mBlock = self.mBlock
            
            b_update = kws.pop('updateUI',True)
            
            mc.refresh(su=1)
            _sel = mc.ls(sl=1)
            if _sel:
                mc.select(cl=1)

            _str_func = ''
            log.info(cgmGEN._str_hardBreak)
            
            _mode = kws.get('mode')

            if _mode == 'setParentToSelected':
                mSelectedBlock = BLOCKGEN.block_getFromSelected()
                if not mSelectedBlock:
                    return log.error("|{0}| >> mode: {1} requires selected block".format(_str_func,_mode)) 
                kws['parent'] = mSelectedBlock
                kws.pop('mode')
                    
                
            #elif  _mode == 'clearParentBlock':
            #else:
                #raise ValueError,"Mode not setup: {0}".format(_mode)            
            b_devMode = False
            b_dupMode = False
            b_changeState = False
            b_rootMode = False
            if args[0] == 'changeState':
                kws['forceNew'] = True
                kws['checkDependency'] = True


            if args[0] == 'VISUALIZEHEIRARCHY':
                BLOCKGEN.get_rigBlock_heirarchy_context(mBlock,_contextMode,False,True)
                return True
            elif args[0]== 'focus':
                log.debug("|{0}| >> Focus call".format(_str_func))
                #ml_root = BLOCKGEN.get_rigBlock_heirarchy_context(ml_blocks,'root',True,False)
                #for mBlock in ml_blocks:
                log.info("|{0}| >> Focus call | {1}".format(_str_func,mBlock))                    
                mBlock.UTILS.focus(mBlock,args[1],args[2],ml_focus=[])
                return
            
            #Now parse to sets of data
            if args[0] == 'select':
                #log.info('select...')
                return mc.select(mBlock.mNode)
   
            ml_res = []
            md_dat = {}
            md_datRev = {}
            
            _short = mBlock.p_nameShort
            _call = str(args[0])
            if _call in ['atUtils']:
                _call = str(args[1])
            
            #pprint.pprint(locals())
            res = getattr(mBlock,args[0])(*args[1:],**kws) or None
            
            ml_res.append(res)
            if res:
                if kws.get('mode') not in ['prechecks']:
                    pprint.pprint(res)
                    
            if b_update:
                self.uiFunc_updateStatus()
                
                if self.mUI_builder:
                    self.mUI_builder.uiScrollList_blocks.rebuild()

            if _sel:
                try:mc.select(_sel)
                except:pass
                
        #except Exception,err:
        #    cgmGEN.cgmExceptCB(Exception,err)
        finally:
            mc.refresh(su=0)
            
    def build_menus(self):
        _str_func = 'build_menus[{0}]'.format(self.__class__.TOOLNAME)            
        log.info("|{0}| >>...".format(_str_func))   
        self.uiMenu_load = mUI.MelMenu( l='Load',pmc=self.buildMenu_load,)
        
        self.uiMenu_block = mUI.MelMenu( l='Block', pmc=self.buildMenu_block,pmo=1, tearOff=1)
        self.uiMenu_vis = mUI.MelMenu( l='Vis', tearOff=1)
        
        
        self.buildMenu_vis()
        
        self.uiMenu_OptionsMenu = mUI.MelMenu( l='Options', pmc=self.buildMenu_options)		
        
        self.uiMenu_snap = mUI.MelMenu( l='Snap', pmo=1, tearOff=1)
        self.buildMenu_snap()
        
        self.uiMenu_HelpMenu = mUI.MelMenu( l='Help', pmc=self.buildMenu_help)   

    def uiFunc_toBuilder(self):
        mUI = ui_get()
        
        if self.mBlock:
            mBlock = self.mBlock        
            try:
                mUI.uiScrollList_blocks.selectByObj(self.mBlock)
            except Exception as err:
                log.error(err)
        self.mUI_builder = mUI
        
    def buildMenu_load( self, *args):
        _str_func = 'buildMenu_load'
        
        if self.uiMenu_load:
            log.info(cgmGEN.logString_sub(_str_func,'Clear...'))               
            self.uiMenu_load.clear()
        
        #>>> Reset Options		
        log.info("|{0}| >>...".format(_str_func))   
        
        mUI.MelMenuItem(self.uiMenu_load,
                        l="Selected",
                        c = lambda *a: self.uiFunc_loadBlock(),
                        ann='Load Selected')                
        
        if not self.mBlock:
            mUI.MelMenuItem(self.uiMenu_load,label='None')
            return
        
        mUI.MelMenuItem(self.uiMenu_load,
                        l="To Builder",
                        c = lambda *a: self.uiFunc_toBuilder(),
                        ann='Open Builder')        

        mUI.MelMenuItemDiv( self.uiMenu_load )        
        
        


        mUI.MelMenuItemDiv( self.uiMenu_load )
        
        mParent = self.mParent
        mChildren = self.mChildren
        mSiblings = self.mSiblings
        mMirror = self.mMirror
        
        if mParent:
            log.info(cgmGEN.logString_sub(_str_func,'Parent...'))                           
            _key = mParent.UTILS.get_uiString(mParent)
            #NAMETOOLS.get_combinedNameDict(mParent.mNode,'cgmType')            
            mUI.MelMenuItem(self.uiMenu_load,
                          l="^ {0}".format(_key),
                          c = lambda *a: self.uiFunc_loadBlock(mParent),
                          en=  1 if mParent else 0,
                          ann='Load Parent block')
        else:
            mUI.MelMenuItem(self.uiMenu_load,
                          l='Parent',
                          en= 0,
                          ann='Load Parent block')
            
        if mChildren:
            log.info(cgmGEN.logString_sub(_str_func,'Children...'))               
            _menu =  mUI.MelMenuItem( self.uiMenu_load, l="Children ({0})".format(len(mChildren)),
                                      subMenu=True)        
            
            for i,mObj in enumerate(mChildren):
                _key = self.d_BlockStrings[mObj]
                #NAMETOOLS.get_combinedNameDict(mObj.mNode,'cgmType')
                
                mUI.MelMenuItem( _menu, l = _key,
                                 c = lambda *a:self.uiFunc_loadBlock(mObj))#
                
                
        if mSiblings:
            #mUI.MelLabel(_mRow_load,label = "Sib")
            log.info(cgmGEN.logString_sub(_str_func,'Siblings...'))    
            
            _menu =  mUI.MelMenuItem( self.uiMenu_load, l="Siblings ({0})".format(len(mSiblings)),
                                      subMenu=True)                 

            for i,mObj in enumerate(mSiblings):
                _key = self.d_BlockStrings[mObj]
                
                #_key = NAMETOOLS.get_combinedNameDict(mObj.mNode,'cgmType')
                
                mUI.MelMenuItem( _menu, l = _key,
                                 c = lambda *a:self.uiFunc_loadBlock(mObj))#
                    
        if mMirror:
            mUI.MelMenuItemDiv( self.uiMenu_load )
            
            log.info(cgmGEN.logString_sub(_str_func,'mirror...'))
            _key = mMirror.UTILS.get_uiString(mMirror)
            
            mUI.MelMenuItem(  self.uiMenu_load, l = "Mirror: {0}".format(_key),
                             c = lambda *a:self.uiFunc_loadBlock(mMirror))#
                
        
    def uiFunc_updateStatus(self):
        if not self.mBlock:
            self.uiStatus(edit=1,
                          label='...')
            
            if self.uiMenu_load:self.uiMenu_load.clear()
            
            return log.error("No block loaded")

        self.uiFunc_updateBlock()
        
        #_strBlock = self.mBlock.UTILS.get_uiString(self.mBlock)#p_nameBase
        mBlock = self.mBlock
        """
        l = []

        #...pre
        for a in ['cgmDirection','cgmPosition']:
            _v = mBlock.getMayaAttr(a)
            if _v:
                l.append(_v)
                
        #...base
        l.extend([mBlock.cgmName, mBlock.blockType])
        
        #...post
        for a in ['blockProfile']:
            _v = mBlock.getMayaAttr(a)
            if _v:
                l.append(_v)
                
        _strBlock = ">>> {0} <<<".format(' | '.join(l))"""
        
        _strBlock = self.mBlock.atUtils('get_uiString',skip = ['blockState'])
        _strState = self.mBlock.getEnumValueString('blockState')
        
        self.uiStr_header(edit=1, label = _strBlock,
                          bgc=CGMUI.guiBackgroundColorLight,
                          en=True)
                          #bgc = d_state_colors[_strState])        
        
        
        self.uiStatus(edit=1,
                      bgc = d_state_colors[_strState],
                      label="State: {0}".format(_strState))        
        

    def uiCallback_contextualSetAttrFromField(self, attr, attrType, field):
        _v = field.getValue()
        
        log.info("{0} | {1}".format(attr,_v))

        self.uiFunc_contextBlockCall('atUtils', 'blockAttr_set', **{'updateUI':False, attr:_v})
        
        if attr == 'buildProfile':
            #_strValue = BLOCKSHARE._d_attrsTo_make['buildProfile'].split(':')[_v]
            log.info("Loading buildProfile... {0}".format(_v))
            self.uiFunc_contextBlockCall('atUtils', 'buildProfile_load', _v, **{'updateUI':False})
        
        
        return
        if attrType == 'enum':
            #_strValue = ATTR.get_enumValueString(obj,attr)
            #field.setValue(_strValue)
            
            if attr == 'buildProfile':
                log.info("Loading buildProfile...")
                self._blockCurrent.atUtils('buildProfile_load',_strValue)
            if attr == 'blockProfile':
                log.info("Loading blockProfile...")
                self._blockCurrent.atUtils('blockProfile_load',_strValue)
                
    def uiCallback_setAttrFromField(self, obj, attr, attrType, field):
        _v = field.getValue()
        ATTR.set(obj,attr,_v)
        
        if attrType == 'enum':
            _strValue = ATTR.get_enumValueString(obj,attr)
            field.setValue(_strValue)
            
            if attr == 'buildProfile':
                log.info("Loading buildProfile...")
                self._blockCurrent.atUtils('buildProfile_load',_strValue)
            if attr == 'blockProfile':
                log.info("Loading blockProfile...")
                self._blockCurrent.atUtils('blockProfile_load',_strValue)                
        else:
            field.setValue(ATTR.get(obj,attr))
            
        if attr == 'numRoll':
            log.info("numRoll check...")                            
            if ATTR.datList_exists(obj,'rollCount'):
                log.info("rollCount Found...")                                            
                l = ATTR.datList_getAttrs(obj,'rollCount')
                for a in l:
                    log.info("{0}...".format(a))                                                
                    ATTR.set(obj,a, _v)
                
        if attr in ['numShapers','neckShapers']:
            log.info("loftList verify check...")
            self.mBlock.UTILS.verify_loftList(self.mBlock,_v)
            mc.evalDeferred(self.uiFunc_updateBlock,lp=True)
                #self.uiUpdate_blockDat()
                
        if attr == 'loftShape':
            log.info("loftShape push to list...")            
            for a in ATTR.datList_getAttrs(obj,'loftList'):
                ATTR.set(obj,a,_v)
            mc.evalDeferred(self.uiFunc_updateBlock,lp=True)
        
        if attr in ['numJoints','neckJoints'] or attr.startswith('rollCount'):
            log.info("")            
            try:
                self.mBlock.atBlockModule('create_jointHelpers')
                log.info("Updated jointHelpers")            
                
            except:pass
        
        log.info("Set: {0} | {1} | {2}".format(obj,attr,_v))
    
    def uiCallback_loadChild(self):
        _v = self.uiOM_child.getValue()
        mBlock =  self.mBlockDict.get(_v)
        if not mBlock:
            return
        
        self.uiBlock_content.clear()
        self.uiFunc_loadBlock( mBlock)
        
    def uiCallback_loadSibling(self):
        _v = self.uiOM_sibling.getValue()
        mBlock =  self.mBlockDict.get(_v)
        if not mBlock:
            return
        
        self.uiBlock_content.clear()
        self.uiFunc_loadBlock( mBlock)
        
    def uiPopup_createChildren(self,button):
        if self.uiPopUpMenu_children:
            self.uiPopUpMenu_children.clear()
            self.uiPopUpMenu_children.delete()
            self.uiPopUpMenu_children = None
    
        self.uiPopUpMenu_children = mUI.MelPopupMenu(button,button = 1)
        _popUp = self.uiPopUpMenu_children 
    
        mUI.MelMenuItem(_popUp,
                        label = "Set Children",
                        en=False)     
        mUI.MelMenuItemDiv(_popUp)
        
        _pop = mUI.MelMenuItem(_popUp,subMenu = True,
                               label = "Children",
                               en=True)
        
        for mChild in self.mChildren:
            _label =  mChild.p_nameBase
            mUI.MelMenuItem(_pop,
                            label = _label,
                            ann = "Set the create shape to: {0}".format(_label),
                            c=lambda *a:self.uiFunc_loadBlock(mChild))  
                
                
    def uiFunc_updateBlock(self):
        _str_func = ' uiFunc_updateBlock'
        log.debug("|{0}| >> mBlock: {1}".format(_str_func,self.mBlock))
        
        self.uiBlock_content.clear()
        
        mBlock = self.mBlock
        

        
        mParent = mBlock.p_blockParent
        mChildren = mBlock.getBlockChildren() or []
        mSiblings = mBlock.atUtils('siblings_get') or []
        mMirror = mBlock.getMessageAsMeta('blockMirror')
        
        self.d_BlockStrings = {}
        
        for mList in mChildren,mSiblings:
            mList = LISTS.get_noDuplicates(mList)
            mTmp = {}
            l_keys = []
            for mObj in mList:
                _key = mObj.UTILS.get_uiString(mObj)
                mTmp[_key] = mObj
                l_keys.append(_key)
                self.d_BlockStrings[mObj] = _key 
            
            l_keys.sort()
            mList = [mTmp[k] for k in l_keys]

        self.mParent = mParent
        self.mChildren = mChildren
        self.mSiblings = mSiblings
        self.mMirror = mMirror
        ml_done = []
        
        _short = mBlock.mNode
        
        _keys = ['define','form','prerig']
        
        d_keyColors = {'profile':'define',
                       'basic':'define',
                       'name':'define',
                       'proxySurface':'form',
                       'squashStretch':'rig',
                       'space':'rig',
                       'post':'rig'}
        
        for i,k in enumerate(_keys):
            log.debug(cgmGEN.logString_sub(_str_func,k))                
            
            if mBlock.blockState <= i-1:
                log.debug("|{0}| >> Block not at state: {1}".format(_str_func,i))                
                continue
            
            try:self.__dict__['var_{0}FrameCollapse'.format(k)]
            except:self.create_guiOptionVar('{0}FrameCollapse'.format(k),defaultValue = 0)
            
            mVar_frame = self.__dict__['var_{0}FrameCollapse'.format(k)]
            
            _frame = mUI.MelFrameLayout(self.uiBlock_content,label = CORESTRINGS.capFirst(k),vis=True,
                                        collapse=mVar_frame.value,
                                        collapsable=True,
                                        enable=True,
                                        marginWidth = 5,
                                        useTemplate = 'cgmUIHeaderTemplate',
                                        expandCommand = cgmGEN.Callback(mVar_frame.setValue,0),
                                        collapseCommand =  cgmGEN.Callback(mVar_frame.setValue,1),
                                        statusBarMessage = k,
                                        )	
            _inside = mUI.MelColumnLayout(_frame,
                                          #rowSpacing = 5)
                                          )
            
            
            _sub_bgc = d_keyColors.get(k)
            if _sub_bgc: 
                _d_uiColors = d_uiStateUIColors.get(_sub_bgc)
            else:
                _d_uiColors = d_uiStateUIColors.get(k) or d_uiStateUIColors.get('default')
                
            _clr_header = _d_uiColors['base']
            _clr_bg = _d_uiColors['bgc']
            _clr_light =  _d_uiColors['light']
            _clr_button = _d_uiColors['button']            
            
            
            _frame(edit=1, bgc=_clr_bg)
            _inside(edit=1, bgc=_clr_bg)
                
            
            def buttonIt(**kws):
                mUI.MelButton(_inside,bgc=_clr_button,**kws)
                
            
            if k == 'define':
                #Define .... --------------------------------------------------------
                d_define = []
                for k in ['start','end','rp','up','lever']:
                    mHandle = mBlock.getMessageAsMeta("define{0}Helper".format(k.capitalize()))
                    if mHandle:
                        if mHandle.v:
                            if mHandle in ml_done:continue
                            d = {'ann':'[{0}] Define {1} Helper'.format(_short,k),
                                 'c':cgmGEN.Callback(mHandle.select),
                                 'label':"{0} Helper".format(k)}
                            d_define.append(d)
                            ml_done.append(mHandle)
                            
                ml_define  = mBlock.msgList_get('defineHandles')#    
                for mHandle in ml_define:
                    if mHandle.v:
                        if mHandle in ml_done:continue
                        k = mHandle.getMayaAttr('handleTag') or mHandle.p_nameBase
                        d = {'ann':'[{0}] Define {1} Helper'.format(_short,k),
                             'c':cgmGEN.Callback(mHandle.select),
                             'label':"{0} Helper".format(k)}
                        d_define.append(d)
                        ml_done.append(mHandle)        
                
                if d_define:
                    for d in d_define:
                        buttonIt(**d)
                        
            if k == 'form':
                #Form ------------------------------------------------------------------------------
                def addPivotHelper(mPivotHelper,i,l):
                    _nameBase = mPivotHelper.p_nameBase
                    d_form.append({'ann':' Pivot [{0}] [{1}]'.format(_nameBase,i),
                                  'c':cgmGEN.Callback(mPivotHelper.select),
                                  'label':' '*i + "{0} - [ {1} ]".format(_nameBase,i)})
                    ml_done.append(mPivotHelper)
                    
                    mTopLoft = mPivotHelper.getMessageAsMeta('topLoft')
                    if mTopLoft:
                        d_form.append({'ann':'[{0}] Pivot Top [{1}]'.format(_short,i),
                                      'c':cgmGEN.Callback(mTopLoft.select),
                                      'label':' '*i + "Pivot Top - [ {0} ]".format(i)})            
                    
                d_form = []
                
                for k in ['orientHelper']:
                    mHandle = mBlock.getMessageAsMeta("{0}".format(k))
                    if mHandle:
                        if mHandle in ml_done:continue                
                        d_form.append({'ann':'[{0}] {1}'.format(_short,k),
                                      'c':cgmGEN.Callback(mHandle.select),
                                      'label':"{0}".format(k)})
                        ml_done.append(mHandle)
        
                
                ml_handles = mBlock.msgList_get('formHandles')
                ml_lofts = []
                if ml_handles:
                    for i,mObj in enumerate(ml_handles):
                        if mObj in ml_done:continue                                
                        d_form.append({'ann':'[{0}] Form Handles [{1}]'.format(_short,i),
                                      'c':cgmGEN.Callback(mObj.select),
                                      'label':' '*i + "{0} | {1}".format(i,mObj.p_nameBase)})
                        try:
                            mLoft = mObj.loftCurve
                        except:mLoft = False
                        if mLoft:
                            ml_lofts.append(mLoft)
                            
                        ml_sub = mObj.msgList_get('subShapers')
                        if ml_sub:
                            ml_lofts.extend(ml_sub)
                          
                        mPivotHelper = mObj.getMessageAsMeta('pivotHelper')
                        ml_done.append(mObj)
                        if mPivotHelper:
                            addPivotHelper(mPivotHelper,i,d_form)
                            
                if d_form:
                    buttonIt(**{'ann':'Select mains [{0}]'.format(len(ml_handles)),
                                'label':'Select mains [{0}]'.format(len(ml_handles)),
                                'c':cgmGEN.Callback(mc.select,[mObj.mNode for mObj in ml_handles])})                    
                    for d in d_form:
                        buttonIt(**d)
                        
                        
                if ml_lofts:
                    #mc.setParent(_inside)
                    #cgmUI.add_LineBreak()
                    
                    mUI.MelLabel(_inside,l='Subs',align='center',bgc=_clr_header)                        
                    buttonIt(**{'ann':'Select all [{0}]'.format(len(ml_lofts)),
                                'label':'Select all [{0}]'.format(len(ml_lofts)),
                                'c':cgmGEN.Callback(mc.select,[mObj.mNode for mObj in ml_lofts])})
                    
                    for i,mSub in enumerate(ml_lofts):
                        buttonIt(**{'ann':'[{0}] Loft Handles [{1}]'.format(mSub.mNode,i),
                                    'label':"{0} | {1}".format(i,mSub.p_nameBase),
                                    'c':cgmGEN.Callback(mSub.select)})                
                        
            if k == 'prerig':#prerig------------------------------------------------------------------------------
                d_pre = []

                for k in ['cogHelper','scalePivotHelper']:
                    mHandle = mBlock.getMessageAsMeta("{0}".format(k))
                    if mHandle:
                        if mHandle in ml_done:continue                                                
                        d_pre.append({'ann':'[{0}] {1}'.format(_short,k),
                                          'c':cgmGEN.Callback(mHandle.select),
                                          'label':"{0}".format(k)})
                        ml_done.append(mHandle)
            
            
                ml_preHandles = mBlock.msgList_get('prerigHandles')
                d_names = {}
                if ml_preHandles:
                    for i,mObj in enumerate(ml_preHandles):
                        if mObj in ml_done:continue                                                
                        try:
                            _name = mObj.p_nameBase
                            #d_names[i] = _name
                            #_name = _name + ' ' + mObj.cgmType
                        except:_name = "Pre handle - [ {0} ]".format(i)
                        d_pre.append({'ann':'[{0}] prerig [{1}]'.format(_short,i),
                                          'c':cgmGEN.Callback(mObj.select),
                                          'label':"{0} | {1}".format(i,_name)})
                        ml_done.append(mObj)
                        
                if d_pre:
                    buttonIt(**{'ann':'Select mains [{0}]'.format(len(ml_preHandles)),
                                'label':'Select mains [{0}]'.format(len(ml_preHandles)),
                                'c':cgmGEN.Callback(mc.select,[mObj.mNode for mObj in ml_preHandles])})                    
                    for d in d_pre:
                        buttonIt(**d)
                        
                def doMsgList(arg):
                    ml = mBlock.msgList_get(arg)
                    if not ml:
                        return
                    
                    mUI.MelLabel(_inside,l=arg,align='center',bgc=_clr_header)                        
                    buttonIt(**{'ann':'Select all [{0}]'.format(len(ml)),
                                'label':'Select all [{0}]'.format(len(ml)),
                                'c':cgmGEN.Callback(mc.select,[mObj.mNode for mObj in ml])})

                    for i,mSub in enumerate(ml):
                        buttonIt(**{'ann':'[{0}] {2} [{1}]'.format(mSub.mNode,i, arg),
                                    'label':"{0} | {1}".format(i,mSub.p_nameBase),
                                    'c':cgmGEN.Callback(mSub.select)})
                        
                
                doMsgList('jointHelpers')
            


            
        
        
        return
        
        _d = self.mBlock.atUtils('uiQuery_getStateAttrDict',0,0)
        
        self._d_attrFields = {}
        
        _short = mBlock.mNode
        
        _keys = sorted(_d)
        l_order =['define','profile','basic','name',
                  'form','proxySurface','prerig',
                  'skeleton',
                  'rig','squashStretch']
        l_order.reverse()
        
        for k in l_order:
            if k in _keys:
                _keys.remove(k)
                _keys.insert(0,k)
                
        l_end = ['data','wiring','advanced']
        for k in l_end:
            if k in _keys:
                _keys.remove(k)
                _keys.append(k)        
        
        
        d_keyColors = {'profile':'define',
                       'basic':'define',
                       'name':'define',
                       'proxySurface':'form',
                       'squashStretch':'rig',
                       'post':'rig'}
        
        for k in _keys:
            log.debug(cgmGEN.logString_sub(_str_func,k))                
            
            l = _d.get(k)
            if not l:
                log.debug("|{0}| >> No attrs in : {1}".format(_str_func,k))                
                continue
            
            try:self.__dict__['var_{0}FrameCollapse'.format(k)]
            except:self.create_guiOptionVar('{0}FrameCollapse'.format(k),defaultValue = 0)
            
            mVar_frame = self.__dict__['var_{0}FrameCollapse'.format(k)]
            
            _frame = mUI.MelFrameLayout(self.uiBlock_content,label = CORESTRINGS.capFirst(k),vis=True,
                                        collapse=mVar_frame.value,
                                        collapsable=True,
                                        enable=True,
                                        marginWidth = 5,
                                        useTemplate = 'cgmUIHeaderTemplate',
                                        expandCommand = cgmGEN.Callback(mVar_frame.setValue,0),
                                        collapseCommand =  cgmGEN.Callback(mVar_frame.setValue,1),
                                        statusBarMessage = k,
                                        )	
            _inside = mUI.MelColumnLayout(_frame,
                                          #rowSpacing = 5,
                                          useTemplate = 'cgmUISubTemplate')
            
            _bgc = None
            _sub_bgc = d_keyColors.get(k)
            if _sub_bgc: 
                _bgc = d_uiStateSubColors.get(_sub_bgc)
                _bgc = [v*.7 for v in _bgc]
            else:
                _bgc = d_uiStateSubColors.get(k)
                
            if _bgc:
                _frame(edit=1, bgc=_bgc)
            
            if k == 'name':#Name section....-------------------------------------------------
                log.debug("|{0}| >> Name...".format(_str_func))
                _nameIter = mBlock.hasAttr('nameIter')
                if _nameIter:
                    mUI.MelLabel(_inside,l = "Tag: {0} | Iterator: {1}".format(mBlock.getMayaAttr('cgmName'),
                                                                               mBlock.getMayaAttr('nameIter')),
                                 ut ='cgmUIInstructionsTemplate' ,
                                 )
                else:
                    mUI.MelLabel(_inside,l = "Tag: {0}".format(mBlock.getMayaAttr('cgmName')),
                                 ut ='cgmUIInstructionsTemplate' ,
                                 )                    

                #Base name stuff...
                _mRow = mUI.MelHLayout(_inside,ut='cgmUISubTemplate',padding = 2)
                
                mUI.MelButton(_mRow,
                              label='Tag',ut='cgmUITemplate',
                              c = cgmGEN.Callback(self.uiFunc_blockCall,
                                                  'atUtils','set_nameTag', **{}),
                              ann='Change nameTag')
                if _nameIter:
                    mUI.MelButton(_mRow,
                                  label='NameIter',ut='cgmUITemplate',
                                  c = cgmGEN.Callback(self.uiFunc_blockCall,
                                                      'atUtils','set_nameIter', **{}),
                                  ann='Change iter name')                
                
                _mRow.layout()
                
                
                _nameList = mBlock.datList_get('nameList')
                if _nameList:
                    mc.setParent(_inside)
                    cgmUI.add_LineBreak()
                    cgmUI.add_Header('nameList')
                    
                    #mUI.MelLabel(_inside,l = 'NAMELIST',
                    #             useTemplate = 'cgmUITemplate')
                    
                    mUI.MelLabel(_inside,l = "{0} | {1}".format(len(_nameList),
                                                                [str(n) for n in _nameList]),
                                useTemplate = 'cgmUIInstructionsTemplate',
                                )
                    
                    #Namelist...
                    _mRow = mUI.MelHSingleStretchLayout(_inside,ut='cgmUISubTemplate')
                    mUI.MelSpacer(_mRow,w=_sidePadding)
                    
                    mUI.MelLabel(_mRow,l='NameList:')
                    _mRow.setStretchWidget(mUI.MelSeparator(_mRow,))
                    
                    _d_nameList = {
                                'Reset':{'ann':'Reset the name list to the profile',
                                               'call':cgmGEN.Callback(self.uiFunc_blockCall,
                                                                      'atUtils','nameList_resetToProfile',
                                                                      **{})},
                                'Edit':{'ann':'Ui Prompt to edit nameList',
                                                    'call':cgmGEN.Callback(self.uiFunc_blockCall,
                                                                           'atUtils','nameList_uiPrompt',
                                                                           **{})},                  
                                 'Iter baseName':{'ann':'Set nameList values from name attribute',
                                                  'call':cgmGEN.Callback(self.uiFunc_blockCall,
                                                                         'atUtils','set_nameListFromName',
                                                                         **{})}}
                
                    for k2,d2 in list(_d_nameList.items()):
                        mUI.MelButton(_mRow,
                                     label=k2,ut='cgmUITemplate',
                                     ann = d2.get('ann',''),
                                     c=d2.get('call'))
                        
                    mUI.MelSpacer(_mRow,w=_sidePadding)
                    _mRow.layout()
                
                
            
            if k == 'vis':
                #Lock nulls row ------------------------------------------------------------------------
                _mRow_lockNulls = mUI.MelHSingleStretchLayout(_inside,ut='cgmUISubTemplate',padding = 2)
                mUI.MelSpacer(_mRow_lockNulls,w=_sidePadding)
                
                mUI.MelLabel(_mRow_lockNulls,l='Lock null:')
                _mRow_lockNulls.setStretchWidget(mUI.MelSeparator(_mRow_lockNulls,))
                
                for null in ['formNull','prerigNull']:
                    _str_null = mBlock.getMessage(null)
                    if _str_null:
                        _nullShort = _str_null[0]
                        mUI.MelCheckBox(_mRow_lockNulls, l="- {0}".format(null),
                                        value = ATTR.get(_nullShort,'template'),
                                        onCommand = cgmGEN.Callback(ATTR.set,_nullShort,'template',1),
                                        offCommand = cgmGEN.Callback(ATTR.set,_nullShort,'template',0))                
                    else:
                        mUI.MelCheckBox(_mRow_lockNulls, l="- {0}".format(null),
                                        en=False)
                
                mUI.MelSpacer(_mRow_lockNulls,w=_sidePadding)
                _mRow_lockNulls.layout()                
                
            
            if k == 'profile':
                log.debug("|{0}| >> profile...".format(_str_func))
                
                d_profileDat = {'block':{'options':RIGBLOCKS.get_blockProfile_options(mBlock.blockType),
                                         'current':str(mBlock.getMayaAttr('blockProfile')),
                                         },
                                'build':{'options':BLOCKSHARE._l_buildProfiles,
                                         'current':str(mBlock.getMayaAttr('buildProfile'))}}
                
                
                for k2,d2 in list(d_profileDat.items()):
                    _en = True
                    _defineOff = False
                    if k2 == 'block':
                        if mBlock.blockState != 0:
                            _en = False
                            _defineOff = True
                            
                            
                    _mRow = mUI.MelHSingleStretchLayout(_inside,ut='cgmUISubTemplate',padding = 10)
                    mUI.MelLabel(_mRow,l="  {0} > ".format(CORESTRINGS.capFirst(k2)))
                    
                    
                    _optionMenu = mUI.MelOptionMenu(_mRow,ut = 'cgmUITemplate',h=25,en=_en)
                    
                    _mRow.setStretchWidget(_optionMenu)
                    
                    
                    self.__dict__['uiOM_{0}'.format(k2)] = _optionMenu
                
                    for option in d2.get('options',[]):
                        _optionMenu.append(option)
                        
                    try:_optionMenu.selectByValue(d2['current'])
                    except:pass
                    
                    
                    mUI.MelButton(_mRow,en=_en,
                                  label='Load',ut='cgmUITemplate',
                                  c = cgmGEN.Callback(self.uiFunc_profileSet,
                                                      k2, **{}),
                                  ann='Load {0}Profile'.format(k2))     
                        
                    #mUI.MelSpacer(_mRow,w=_sidePadding)                
                    _mRow.layout()
                    
                    if _defineOff:
                        mUI.MelLabel(_inside, bgc=cgmUI.d_stateColors['warning'],
                                     w=75,al='center',
                                     en=_en,
                                     l = "blockType can only be changed in define state")
                    
                    mc.setParent(_inside)
                    cgmUI.add_LineSubBreak()
                
                    
                continue

                
                for i,item in enumerate(BLOCKSHARE._l_buildProfiles):
                    mUI.MelMenuItem(_Profiles, l=item,
                                    ann = "Load the following profile",
                                    c = cgmGEN.Callback(self.uiFunc_buildProfile_set,**{'buildProfile':item}),
                                    )                       
                
                continue
                _nameIter = mBlock.hasAttr('nameIter')
                
                
                if _nameIter:
                    mUI.MelLabel(_inside,l = "Tag: {0} | Iterator: {1}".format(mBlock.getMayaAttr('cgmName'),
                                                                               mBlock.getMayaAttr('nameIter')),
                                 ut ='cgmUIInstructionsTemplate' ,
                                 )
                else:
                    mUI.MelLabel(_inside,l = "Tag: {0}".format(mBlock.getMayaAttr('cgmName')),
                                 ut ='cgmUIInstructionsTemplate' ,
                                 )                    

                #Base name stuff...
                _mRow = mUI.MelHLayout(_inside,ut='cgmUISubTemplate',padding = 2)
                
                mUI.MelButton(_mRow,
                              label='Tag',ut='cgmUITemplate',
                              c = cgmGEN.Callback(self.uiFunc_blockCall,
                                                  'atUtils','set_nameTag', **{}),
                              ann='Change nameTag')
                if _nameIter:
                    mUI.MelButton(_mRow,
                                  label='NameIter',ut='cgmUITemplate',
                                  c = cgmGEN.Callback(self.uiFunc_blockCall,
                                                      'atUtils','set_nameIter', **{}),
                                  ann='Change iter name')                
                
                _mRow.layout()                
                continue
            
            #Attrs... ------------------------------------------------------------------------
            for a in l:
                try:
                    if a in ['blockState']:
                        continue
                    _type = ATTR.get_type(_short,a)
                    log.debug("|{0}| >> attr: {1} | {2}".format(_str_func, a, _type))
                    
                    if k in ['data','wiring']:
                        
                        mUI.MelLabel(_inside,l = "{0} | {1}".format(a, ATTR.get(_short,a)))
                        continue
                    
                    """
                    _datList = mBlock.datList_get(a)
                    if _datList:
                        mc.setParent(_inside)
                        cgmUI.add_LineBreak()
                        cgmUI.add_Header(a)
                        

                        mUI.MelLabel(_inside,l = "{0} | {1}".format(len(_datList),
                                                                    [str(n) for n in _datList]),
                                    useTemplate = 'cgmUIInstructionsTemplate',
                                    )
                        
                        #Namelist...
                        _mRow = mUI.MelHSingleStretchLayout(_inside,ut='cgmUISubTemplate')
                        mUI.MelSpacer(_mRow,w=_sidePadding)
                        
                        mUI.MelLabel(_mRow,l='NameList:')
                        _mRow.setStretchWidget(mUI.MelSeparator(_mRow,))
                        
                        _d_nameList = {
                                    'Reset':{'ann':'Reset the name list to the profile',
                                                   'call':cgmGEN.Callback(self.uiFunc_blockCall,
                                                                          'atUtils','nameList_resetToProfile',
                                                                          **{})},
                                    'Edit':{'ann':'Ui Prompt to edit nameList',
                                                        'call':cgmGEN.Callback(self.uiFunc_blockCall,
                                                                               'atUtils','nameList_uiPrompt',
                                                                               **{})},                  
                                     'Iter baseName':{'ann':'Set nameList values from name attribute',
                                                      'call':cgmGEN.Callback(self.uiFunc_blockCall,
                                                                             'atUtils','set_nameListFromName',
                                                                             **{})}}
                    
                        for k2,d2 in _d_nameList.iteritems():
                            mUI.MelButton(_mRow,
                                         label=k2,ut='cgmUITemplate',
                                         ann = d2.get('ann',''),
                                         c=d2.get('call'))
                            
                        mUI.MelSpacer(_mRow,w=_sidePadding)
                        _mRow.layout()                    """





                    _hlayout = mUI.MelHSingleStretchLayout(_inside,padding = 10)
                    
                   

                    #if _type not in ['bool']:#Some labels parts of fields
                    mUI.MelLabel(_hlayout,l="  {0} ".format(a))   
        
                    #mUI.MelSpacer(_hlayout,w=_sidePadding)
            
                    _hlayout.setStretchWidget(mUI.MelSeparator(_hlayout,))
                    
                    
                    d_datLists = {'numSubShapers':{'datList':'numSubShapers',
                                           'defaultAttr':'numSubShapers'},
                                  'numRoll':{'datList':'rollCount',
                                             'defaultAttr':'numRoll'},                                  
                          }                    
                    if a in ['numSubShapers','numRoll']:

                        mUI.MelButton(_hlayout,
                                     label='Edit datList',ut='cgmUITemplate',
                                     #ann = d2.get('ann',''),
                                     c=cgmGEN.Callback(self.uiFunc_blockCall,
                                        'atUtils','datList_validate',
                                        **{'datList':d_datLists[a].get('datList'),
                                           'defaultAttr':d_datLists[a].get('defaultAttr'),
                                           'forceEdit':1}))
                    

                    if _type == 'bool':
                        mUI.MelCheckBox(_hlayout, l="",
                                        #annotation = "Copy values",		                           
                                        value = ATTR.get(_short,a),
                                        onCommand = cgmGEN.Callback(ATTR.set,_short,a,1),
                                        offCommand = cgmGEN.Callback(ATTR.set,_short,a,0))
            
                    elif _type in ['double','doubleAngle','doubleLinear','float']:
                        self._d_attrFields[a] = mUI.MelFloatField(_hlayout,w = 50,
                                                                  value = ATTR.get(_short,a),                                                          
                                                                  )
                        self._d_attrFields[a](e=True,
                                              cc  = cgmGEN.Callback(self.uiCallback_setAttrFromField,_short, a, _type,
                                                                    self._d_attrFields[a]),
                                              )
                    elif _type == 'long':
                        self._d_attrFields[a] = mUI.MelIntField(_hlayout,w = 50,
                                                                 value = ATTR.get(_short,a),
                                                                 maxValue=20,
                                                                 minValue=ATTR.get_min(_short,a),
                                                                  )
                        self._d_attrFields[a](e=True,
                                              cc  = cgmGEN.Callback(self.uiCallback_setAttrFromField,_short, a, _type,
                                                                    self._d_attrFields[a]),
                                              )                
                    elif _type == 'string':
                        self._d_attrFields[a] = mUI.MelTextField(_hlayout,w = 75,
                                                                 text = ATTR.get(_short,a),
                                                                  )
                        self._d_attrFields[a](e=True,
                                              cc  = cgmGEN.Callback(self.uiCallback_setAttrFromField,_short, a, _type,
                                                                    self._d_attrFields[a]),
                                              )
                    elif _type == 'enum':
                        _optionMenu = mUI.MelOptionMenu(_hlayout,ut = 'cgmUITemplate')
                        _optionMenu(e=True,
                                    cc = cgmGEN.Callback(self.uiCallback_setAttrFromField,_short, a, _type,
                                                         _optionMenu),) 
                        for option in ATTR.get_enumList(_short,a):
                            _optionMenu.append(option)
                        _optionMenu.setValue(ATTR.get_enumValueString(_short,a))
                    else:
                        mUI.MelLabel(_hlayout,l="{0}({1}):{2}".format(a,_type,ATTR.get(_short,a)))        
                        
                        
                    #mUI.MelSpacer(_hlayout,w=_sidePadding)                
                    _hlayout.layout()
                except Exception as err:
                    log.warning("Attr {0} failed. err: {1}".format(a,err))            

    def uiFunc_loadBlock(self,mBlock = None):
        if mBlock == None:
            mBlock = BLOCKGEN.block_getFromSelected()
        
        
        self.mBlock = cgmMeta.validateObjArg(mBlock,'cgmRigBlock',True)
        self.block = None
        if self.mBlock:
            self.block = self.mBlock.mNode        
        else:
            return log.warning("Invalid block: {0}".format(mBlock))
        

            
        self.uiStr_header(edit=1, label = 'Syncing')
            
        _blockState = self.mBlock.getEnumValueString('blockState')
        
        if not self.block:
            self.uiStatus(edit=True,vis=True,label="Must have something loaded")
            return
        
        self.uiFunc_updateStatus()
        
        
    def build_layoutWrapper(self,parent):
        _str_func = 'build_layoutWrapper[{0}]'.format(self.__class__.TOOLNAME)            
        log.debug("|{0}| >>...".format(_str_func))
        
        _MainForm = mUI.MelFormLayout(parent,ut='cgmUITemplate')#mUI.MelColumnLayout(ui_tabs)
        
       
        _top = mUI.MelColumn(_MainForm)
        #SetHeader = mUI.MelLabel(_inside,label = '', al = 'center', ut = 'cgmUIHeaderTemplate')
        SetHeader = mUI.MelButton(_top,
                                  en=False,
                                  l='...',
                                  c=lambda *a:self.mBlock.select(),
                                  al = 'center', ut = 'cgmUIHeaderTemplate')
        self.uiStr_header = SetHeader
        

        #Inside...
        
        _inside = mUI.MelScrollLayout(_MainForm, ut='cgmUITemplate')

        #mc.setParent(_MainForm)
        _bottom = mUI.MelColumn(_MainForm)
        
        #Push Rows  -------------------------------------------------------------------------------  
        mc.setParent(_bottom)
        CGMUI.add_LineSubBreak()
        cgmUI.add_HeaderBreak()
        _row_push = mUI.MelHLayout(_bottom,ut='cgmUIHeaderTemplate',padding = 2)
        mc.button(l='Define>',
                  bgc = d_state_colors['define'],#SHARED._d_gui_state_colors.get('warning'),
                  height = 20,
                  align='center',
                  c=cgmGEN.Callback(self.uiFunc_blockCall,'changeState','define',**{'forceNew':True}),
                  ann='[Define] - initial block state')
        mc.button(l='<Form>',
                  bgc = d_state_colors['form'],              
                  height = 20,
                  align='center',                  
                  c=cgmGEN.Callback(self.uiFunc_blockCall,'changeState','form',**{'forceNew':True}),
                  ann='[Template] - Shaping the proxy and initial look at settings')
                         
        mc.button(l='<Prerig>',
                  bgc = d_state_colors['prerig'],                  
                  height = 20,
                  align='center',
                  c=cgmGEN.Callback(self.uiFunc_blockCall,'changeState','prerig',**{'forceNew':True}),
                  ann='[Prerig] - More refinded placement and setup before rig process')

        mc.button(l='<Joint>',
                  bgc = d_state_colors['skeleton'],                  
                  height = 20,
                  align='center',                  
                  c=cgmGEN.Callback(self.uiFunc_blockCall,'changeState','skeleton',**{'forceNew':True}),
                  ann='[Joint] - Build skeleton if necessary')

        mc.button(l='<Rig',
                  bgc = d_state_colors['rig'],                  
                  height = 20,
                  align='center',                  
                  c=cgmGEN.Callback(self.uiFunc_blockCall,'changeState','rig',**{'forceNew':True}),
                  ann='[Rig] - Push to a fully rigged state.')
        _row_push.layout()        
        
        
        #---------------------------------------------------------------------------------
        self.uiStatus = mUI.MelButton(_bottom,bgc=SHARED._d_gui_state_colors.get('warning'),
                                      c=lambda *a:self.uiFunc_updateStatus(),
                                      ann="Query the last buffered state and update status",
                                      label='...',
                                      h=20)
        
        #mUI.MelLabel(_MainForm,
        #                             vis=True,
        #                             bgc = SHARED._d_gui_state_colors.get('warning'),
        #                             label = '...',
        #                             h=20)        
        self.uiPB_test=None
        self.uiPB_test = mc.progressBar(vis=False)

        
        #Let's gather our attributes...
        
        self.uiBlock_content = mUI.MelColumn(_inside,
                                             #rowSpacing=2,
                                             #bgc=cgmUI.guiBackgroundColorLight,
                                             useTemplate = 'cgmUITemplate')        
        
        
        #_row_cgm = cgmUI.add_cgmFooter(_MainForm)
        mc.setParent(_MainForm)
 
        
        #_rowProgressBar = mUI.MelRow(_MainForm)

        _MainForm(edit = True,
                  af = [(_top,"top",0),
                        (_top,"left",0),
                        (_top,"right",0),
                        (_inside,"left",0),
                        (_inside,"right",0),                        
                        (_bottom,"left",0),
                        (_bottom,"right",0),
                        #(self.uiPB_test,"left",0),
                        #(self.uiPB_test,"right",0),                        
                        #(_row_cgm,"left",0),
                        #(_row_cgm,"right",0),
                        (_bottom,"bottom",0),
    
                        ],
                  ac = [(_inside,"top",0,_top),
                        (_inside,"bottom",0,_bottom),
                        #(_button,"bottom",0,_row_cgm),
                        #(self.uiPB_test,"bottom",0,_row_cgm),
                        ],
                  attachNone = [(_bottom,"top")])    
        
        
        
        


class ui_blockEditor(cgmUI.cgmGUI):
    USE_Template = 'cgmUITemplate'
    WINDOW_NAME = 'mrsBlockEditor'    
    WINDOW_TITLE = 'Block Edit | - {0}'.format(__version__)
    DEFAULT_MENU = None
    RETAIN = True
    MIN_BUTTON = False
    MAX_BUTTON = False
    FORCE_DEFAULT_SIZE = True  #always resets the size of the window when its re-created  
    DEFAULT_SIZE = 300,600
    
    _d_ui_annotations = {'select':"Select rigBlocks in maya from ui."}
    
    def __init__(self,mBlock = None, *a,**kws):
        global BLOCKEDITOR

        super(ui_blockEditor, self).__init__(*a,**kws)
        
        self.mBlockDict = {}
        self.uiPopUpMenu_children = None
        self.uiPopUpMenu_siblings = None
        #self.uiMenu_load = None 
        self.uiFunc_loadBlock(mBlock)
        BLOCKEDITOR = self
        self.mUI_builder = None
        self.uiMenu_snap = None
        
        
    def buildMenu_block(self,*args,**kws):
        self.uiMenu_block.clear()   
        _menu = self.uiMenu_block
        d_s = {'Set Side':{},
               'Set Position':{},
               'Skeleton':{'Joints | get bind':{'ann':self._d_ui_annotations.get('Joints | get bind'),
                               'call':cgmGEN.Callback(self.uiFunc_blockCall,
                                      'atUtils','skeleton_getBind',
                                      **{'select':1,'mode':'noSelect'})},
                           'Joints | get report':{'ann':self._d_ui_annotations.get('Joints | get report'),
                                                          'call':cgmGEN.Callback(self.uiFunc_blockCall,
                                                                 'atUtils','skeleton_getReport',
                                                                 **{'updateUI':0})},
                           'Joints | tag':{'ann':self._d_ui_annotations.get('Joints | tag'),
                                                          'call':cgmGEN.Callback(self.uiFunc_blockCall,
                                                                 'atUtils','skeleton_getBind',
                                                                 **{'tag':1})}                           
                           },
       
               'Rig':{'Step Build':{'ann':self._d_ui_annotations.get('step build'),
                               'call':cgmGEN.Callback(self.uiFunc_blockCall,
                                                      'stepUI',
                                                      **{'updateUI':0,'mode':'stepBuild'})},
                      'Prechecks':{'ann':'Precheck blocks for problems',
                                   'call':cgmGEN.Callback(self.uiFunc_blockCall,
                                                          'asRigFactory',
                                                          **{'updateUI':0,'mode':'prechecks'})},                      
                      'Proxy | Verify':{'ann':self._d_ui_annotations.get('verify proxy mesh'),
                               'call':cgmGEN.Callback(self.uiFunc_blockCall,
                                      'verify_proxyMesh',
                                      **{'updateUI':0})},
                      'Proxy | Delete':{'ann':self._d_ui_annotations.get('delete proxy mesh'),
                               'call':cgmGEN.Callback(self.uiFunc_blockCall,
                                      'proxyMesh_delete',
                                      **{'updateUI':0})},                      
                      'Rig Connect':{'ann':self._d_ui_annotations.get('connect rig'),
                                        'call':cgmGEN.Callback(self.uiFunc_contextModuleCall,'rig_connect',**{'updateUI':0})},
                      'Rig Disconnect':{'ann':self._d_ui_annotations.get('disconnect rig'),
                                     'call':cgmGEN.Callback(self.uiFunc_contextModuleCall,'rig_disconnect',**{'updateUI':0})},                      
                      'Reset Controls':{'ann':self._d_ui_annotations.get('reset rig controls'),
                               'call':cgmGEN.Callback(self.uiFunc_contextModuleCall,
                                      'rig_reset',
                                      **{'updateUI':0})},
                                       
                      'Query Nodes':{'ann':self._d_ui_annotations.get('query rig nodes'),
                               'call':cgmGEN.Callback(self.uiFunc_blockCall,
                                      'atUtils','rigNodes_get',
                                      **{'updateUI':0,'report':True})},},
               
               
               'Parent':{'To Active':{'ann':'Set parent block to active block',
                                  'call':cgmGEN.Callback(self.uiFunc_blockCall,
                                                         'atUtils','blockParent_set',
                                                         **{'mode':'setParentToActive'})},
                         'To Selected':{'ann':'Set parent block to active block',
                                      'call':cgmGEN.Callback(self.uiFunc_blockCall,
                                                             'atUtils','blockParent_set',
                                                             **{'mode':'setParentToSelected'})},                         
                         'Clear':{'ann':'Clear blockParent',
                                           'call':cgmGEN.Callback(self.uiFunc_blockCall,
                                                                  'atUtils','blockParent_set',
                                                                  **{'parent':False})},},
               'Siblings':{'Form | Push Sub shapers':{'ann':'Push Sub shaper values to siblings',
                                  'call':cgmGEN.Callback(self.uiFunc_blockCall,
                                                         'atUtils','siblings_pushSubShapers',
                                                         **{})},
                           'Form | Push Handles':{'ann':'Push form shaper values to siblings',
                                               'call':cgmGEN.Callback(self.uiFunc_blockCall,
                                                                      'atUtils','siblings_pushFormHandles',
                                                                      **{})},                           
                         'Prerig | Push Handles':{'ann':'Push prerig handle values to siblings',
                                  'call':cgmGEN.Callback(self.uiFunc_blockCall,
                                                         'atUtils','siblings_pushPrerigHandles',
                                                         **{})}},               
               'Form':{'Snap to RP':{'ann':'Snap handles to rp plane',
                                 'call':cgmGEN.Callback(self.uiFunc_blockCall,
                                 'atUtils', 'handles_snapToRotatePlane','form',True,
                                 **{'updateUI':0})},},
               
               'Names':{ 
                   'divTags':['nameList | edit'],
                   'Name | Set tag':{'ann':'Set the name tag of the block and rename dags',
                                     'call':cgmGEN.Callback(self.uiFunc_blockCall,
                                                            'atUtils','set_nameTag', **{})},
                   'Position | Set tag':{'ann':'Set the position tag of the block and rename dags',
                                         'call':cgmGEN.Callback(self.uiFunc_blockCall,
                                                                'atUtils','set_position',
                                                                **{'ui':True})},
                  'nameList | reset':{'ann':'Reset the name list to the profile',
                                 'call':cgmGEN.Callback(self.uiFunc_blockCall,
                                                        'atUtils','nameList_resetToProfile',
                                                        **{})},
                  'nameList | edit':{'ann':'Ui Prompt to edit nameList',
                                      'call':cgmGEN.Callback(self.uiFunc_blockCall,
                                                             'atUtils','nameList_uiPrompt',
                                                             **{})},                  
                   'nameList | iter baseName':{'ann':'Set nameList values from name attribute',
                                 'call':cgmGEN.Callback(self.uiFunc_blockCall,
                                                        'atUtils','set_nameListFromName',
                                                        **{})}},
               
               
               
               'Prerig':{
                   'Visualize | RP Pos':{'ann':'Create locator at the where the system thinks your rp handle will be',
                             'call':cgmGEN.Callback(self.uiFunc_blockCall,
                                'atUtils', 'prerig_get_rpBasePos',
                                **{'markPos':1,'updateUI':0})},
                   'Visualize | Up Vector':{'ann':'Create a curve showing what the assumed rp up vector is',
                                         'call':cgmGEN.Callback(self.uiFunc_blockCall,
                                            'atUtils', 'prerig_get_upVector',
                                            **{'markPos':1,'updateUI':0})},                   
                   'Snap RP to Orient':{'ann':'Snap rp hanlde to orient vector',
                            'call':cgmGEN.Callback(self.uiFunc_blockCall,
                                   'atUtils', 'prerig_snapRPtoOrientHelper',
                                   **{'updateUI':0})},
                   'Snap to RP':{'ann':'Snap handles to rp plane',
                                 'call':cgmGEN.Callback(self.uiFunc_blockCall,
                                 'atUtils', 'handles_snapToRotatePlane','prerig',True,
                                 **{'updateUI':0})},
                   'Handles | Lock':{'ann':'Lock the prerig handles',
                                 'call':cgmGEN.Callback(self.uiFunc_blockCall,
                                 'atUtils', 'prerig_handlesLock',True,
                                 **{'updateUI':0})},
                   'Handles | Unlock':{'ann':'Unlock the prerig handles',
                                   'call':cgmGEN.Callback(self.uiFunc_blockCall,
                                   'atUtils', 'prerig_handlesLock',False,
                                   **{'updateUI':0})},
                   'divTags':['Handles | Lock','Query Indices',
                              'Visualize | RP Pos',
                              ],                   
                   'Arrange | Linear Spaced':{'ann':'Unlock the prerig handles',
                                             'call':cgmGEN.Callback(self.uiFunc_blockCall,
                                             'atUtils', 'prerig_handlesLayout','spaced','linear',
                                             **{'updateUI':0})},
                   'Arrange | Linear Even':{'ann':'Unlock the prerig handles',
                                             'call':cgmGEN.Callback(self.uiFunc_blockCall,
                                             'atUtils', 'prerig_handlesLayout','even','linear',
                                             **{'updateUI':0})},
                   'Arrange | Cubic Even':{'ann':'Unlock the prerig handles',
                                            'call':cgmGEN.Callback(self.uiFunc_blockCall,
                                            'atUtils', 'prerig_handlesLayout','even','cubicRebuild',
                                            **{'updateUI':0})},
                   'Arrange | Cubic Spaced':{'ann':'Unlock the prerig handles',
                                             'call':cgmGEN.Callback(self.uiFunc_blockCall,
                                             'atUtils', 'prerig_handlesLayout','spaced','cubicRebuild',
                                             **{'updateUI':0})},                                      

                   },
               'Geo':{
                   'order':['Block Mesh','Block Loft | Default',
                            'Block Loft | Even',
                            'Puppet Mesh',
                            'Unified','Unified [Skinned]',
                            'Parts Mesh','Parts Mesh [Skinned]',
                            'Proxy Mesh [Parented]','Delete',
                            ],
                   'divTags':['Delete'],
                   'headerTags':['Puppet Mesh'],
                   'Block Mesh':{'ann':'Generate Simple mesh',
                               'call':cgmGEN.CB(self.uiFunc_blockCall,
                                                'atUtils','create_simpleMesh',
                                                **{'connect':False,'updateUI':0,'deleteHistory':1})},
                   'Block Loft | Default':{'ann':'Generate Simple mesh with history to tweak the loft manually',
                               'call':cgmGEN.CB(self.uiFunc_blockCall,
                                                'atUtils','create_simpleMesh',
                                                **{'connect':False,'updateUI':0,'deleteHistory':0})},
                   'Block Loft | Even':{'ann':'Generate Simple mesh with history to tweak the loft manually',
                                 'call':cgmGEN.CB(self.uiFunc_blockCall,
                                                  'atUtils','create_simpleMesh',
                                                  **{'connect':False,'updateUI':0,'deleteHistory':0,
                                                     'loftMode':'evenCubic'})},                   
                   'Unified':{'ann':"Create a unified unskinned puppet mesh from the active block's basis.",
                              'call':cgmGEN.CB(self.uiFunc_blockCall,'atUtils','puppetMesh_create',
                                               **{'unified':True,'skin':False})},
                   'Unified [Skinned]':{
                       'ann':"Create parts skinned puppet mesh from the active block's basis.",
                       'call':cgmGEN.CB(self.uiFunc_blockCall,'atUtils','puppetMesh_create',
                                         **{'unified':True,'skin':True})},
                   'Parts Mesh':{
                       'ann':"Create parts unskinned puppet mesh from the active block's basis.",
                       'call':cgmGEN.CB(self.uiFunc_blockCall,'atUtils','puppetMesh_create',
                                         **{'unified':False,'skin':False})},
                   'Parts Mesh [Skinned]':{
                       'ann':"Create parts skinned puppet mesh from the active block's basis.",
                       'call':cgmGEN.CB(self.uiFunc_blockCall,'atUtils','puppetMesh_create',
                                         **{'unified':False,'skin':True})},
                   'Proxy Mesh [Parented]':{
                       'ann':"Create proxy puppet mesh parented to skin joints from the active block's basis.",
                       'call':cgmGEN.CB(self.uiFunc_blockCall,'atUtils','puppetMesh_create',
                                         **{'proxy':True,'unified':False,'skin':False})},
                   'Delete':{
                       'ann':"Remove skinned or wired puppet mesh",
                       'call':cgmGEN.CB(self.uiFunc_blockCall,'atUtils','puppetMesh_delete')},
                   },
               
               }

        
        """
        for state in ['define','form','prerig']:
            d_s['blockDat']['order'].append('Load {0}'.format(state))
            d_s['blockDat']['Load {0}'.format(state)] = {
                'ann':"Load {0} blockDat in context".format(state),
                'call':cgmGEN.Callback(self.uiFunc_blockCall,
                                       'atUtils','blockDat_load_state',state,
                                       **{})}"""
        
        
        l_keys = sorted(d_s)
        
        l_check = ['Define','Form','Prerig','Skeleton','Rig']
        l_check.reverse()
        for k in l_check:
            if k in l_keys:
                l_keys.remove(k)
                l_keys.insert(0,k)
                
        for s in l_keys:
            d = d_s[s]
            divTags = d.get('divTags',[])
            headerTags = d.get('headerTags',[])
            
            _sub = mUI.MelMenuItem(_menu, subMenu = True,tearOff=True,
                            label = s,
                            en=True,)
            
            if s == 'Set Side':
                for i,side in enumerate(['none','left','right','center']):
                    mUI.MelMenuItem(_sub,
                                    l = side,
                                    ann='Set contextual block side to: {0}'.format(side),
                                    c = cgmGEN.Callback(self.uiFunc_blockCall,
                                                        'atUtils','set_side',side,
                                                        **{}))                
                
            if s == 'Set Position':
                for i,position in enumerate(BLOCKSHARE._l_positions):
                    mUI.MelMenuItem(_sub,
                                    label = position,
                                    ann = 'Specify the position for the current block to : {0}'.format(position),
                                    c = cgmGEN.Callback(self.uiFunc_blockCall,
                                                        'atUtils','set_position',position,
                                                        **{}))             
            
            l_keys2 = d.get('order',False)
            if l_keys2:
                for k in list(d.keys()):
                    if k not in l_keys2:
                        l_keys2.append(k)
            else:
                l_keys2 = list(d.keys())
                l_keys2.sort()
            for l in l_keys2:
                if l in ['divTags','headerTags','order']:
                    continue
                if l in divTags:
                    mUI.MelMenuItemDiv(_sub)                
                if l in headerTags:
                    mUI.MelMenuItem(_sub,divider = True,
                                    label = l,
                                    en=False)
                    """
                    mUI.MelMenuItemDiv(_sub)
                    mUI.MelMenuItem(_sub,
                                    label = "--- {0} ---".format(l.upper()),
                                    en=False)
                    mUI.MelMenuItemDiv(_sub)"""
                    continue
                d2 = d[l]
                mUI.MelMenuItem(_sub,
                                label = l,
                                ann = d2.get('ann',''),
                                c=d2.get('call'))
                
            if s == 'Rig':
                mUI.MelMenuItemDiv(_menu)            



        log.info("Context menu rebuilt")        
        
    def uiFunc_profileSet(self,mode = 'build',**kws):
        _str_func = ''
        _updateUI = kws.pop('updateUI',True)
        _profile = kws.pop('buildProfile',None)
        
        
        _profile = self.__dict__['uiOM_{0}'.format(mode)].getValue()
        
        
        
        #if not _profile:
        #    return log.error("|{0}| >> blockProfile arg".format(_str_func))
        
        log.info("Setting Profile: {0} | {1}".format(mode,_profile))
        
        if mode == 'build':
            uiFunc_blockCall(self,'atUtils','buildProfile_load',_profile)
        elif mode == 'block':
            uiFunc_blockCall(self,'atUtils','blockProfile_load',_profile)
        else:
            return log.error("Unknown Profile mode: {0}".format(mode))

        return

    def buildMenu_snap( self, force=False, *args, **kws):
        #if self.uiMenu_snap and force is not True:
        #    return
        #self.uiMenu_snap.clear()
        
        UICHUNKS.uiSection_snap(self.uiMenu_snap)
        mUI.MelMenuItemDiv(self.uiMenu_snap)
        
        
    def buildMenu_vis(self,*args,**kws):
        self.uiMenu_vis.clear()   
        _menu = self.uiMenu_vis
        
        d_s = {'Focus':{'Clear':{'ann':self._d_ui_annotations.get('focus clear'),
                                 'call':cgmGEN.Callback(self.uiFunc_blockCall,
                                        'focus',False,None,
                                        **{'updateUI':0})},
                        'Vis':{'ann':self._d_ui_annotations.get('focus vis'),
                               'call':cgmGEN.Callback(self.uiFunc_blockCall,
                                      'focus',True,'vis',
                                      **{'updateUI':0})},
                        'Template':{'ann':self._d_ui_annotations.get('focus template'),
                                    'call':cgmGEN.Callback(self.uiFunc_blockCall,
                                           'focus',True,'template',
                                           **{'updateUI':0})},},
                   }


        
        """
        for state in ['define','form','prerig']:
            d_s['blockDat']['order'].append('Load {0}'.format(state))
            d_s['blockDat']['Load {0}'.format(state)] = {
                'ann':"Load {0} blockDat in context".format(state),
                'call':cgmGEN.Callback(self.uiFunc_blockCall,
                                       'atUtils','blockDat_load_state',state,
                                       **{})}"""
        
        
        l_keys = sorted(d_s)
        
                
        for s in l_keys:
            d = d_s[s]
            divTags = d.get('divTags',[])
            headerTags = d.get('headerTags',[])
            
                
            _sub = mUI.MelMenuItem(_menu, subMenu = True,tearOff=True,
                            label = s,
                            en=True,)

            l_keys2 = d.get('order',False)
            if l_keys2:
                for k in list(d.keys()):
                    if k not in l_keys2:
                        l_keys2.append(k)
            else:
                l_keys2 = sorted(d)
                
            for l in l_keys2:
                if l in ['divTags','headerTags','order']:
                    continue
                if l in divTags:
                    mUI.MelMenuItemDiv(_sub)                
                if l in headerTags:
                    mUI.MelMenuItemDiv(_sub)
                    mUI.MelMenuItem(_sub,
                                    label = "--- {0} ---".format(l.upper()),
                                    en=False)
                    mUI.MelMenuItemDiv(_sub)
                    continue
                d2 = d[l]
                mUI.MelMenuItem(_sub,
                                label = l,
                                ann = d2.get('ann',''),
                                c=d2.get('call'))

        #Vis menu -----------------------------------------------------------------------------
        for a in ['Measure','RotatePlane','Labels','ProximityMode']:
            _sub = mUI.MelMenuItem(_menu, subMenu = True,tearOff=False,
                                   label = a,
                                   en=True,)
            if a == 'ProximityMode':
                _l = ['off','inherit','proximity']
            else:
                _l = ['off','on']
                
            for i,v in enumerate(_l):
                mUI.MelMenuItem(_sub,
                                l = v,
                                ann='Set visibility of: {0} | {1}'.format(a,v),
                                c = cgmGEN.Callback(self.uiFunc_blockCall,
                                            'atUtils', 'blockAttr_set',
                                            **{"vis{0}".format(a):i,'updateUI':0}))
                
                
                
        d_shared = {'formNull':{},
                    'prerigNull':{}}
        
        l_settings = ['visibility']
        l_locks = ['rigBlock','formNull','prerigNull']
        l_enums = []
    
        for n in l_locks:
            _sub = mUI.MelMenuItem(_menu, subMenu = True,tearOff=False,
                                   label = n,
                                   en=True,)
            
    
            if n in l_settings:
                l_options = ['hide','show']
                _mode = 'moduleSettings'
            elif n in l_locks:
                l_options = ['unlock','lock']
                _mode = 'moduleSettings'
                if n != 'rigBlock':
                    _plug = d_shared[n].get('plug',n)
            else:
                l_options = ['off','lock','on']
                _mode = 'puppetSettings'
                
            for v,o in enumerate(l_options):
                if n == 'rigBlock':
                    mUI.MelMenuItem(_sub,
                                    l = o,
                                    ann='Set visibility of: {0} | {1}'.format(a,v),
                                    c = cgmGEN.Callback(self.uiFunc_blockCall,
                                                'atUtils','templateAttrLock',v,**{'updateUI':0}))
                         
  
                else:
                    mUI.MelMenuItem(_sub,
                                    l = o,
                                    ann='Set visibility of: {0} | {1}'.format(a,v),
                                    c = cgmGEN.Callback(self.uiFunc_blockCall,
                                                'atUtils', 'messageConnection_setAttr',
                                                _plug,**{'template':v,'updateUI':0}))                    


        
            for n in l_settings:
                l_options = ['hide','show']
    
                for v,o in enumerate(l_options):
                    mUI.MelMenuItem(_sub,
                                    l = o,
                                    ann='Set visibility of: {0} | {1}'.format(a,v),
                                    c=cgmGEN.Callback(self.uiFunc_blockCall,
                                                'atUtils', 'blockAttr_set',
                                                **{n:v,'updateUI':0}))                    

        log.info("Context menu rebuilt")
        
    @cgmGEN.Timer
    def uiFunc_contextModuleCall(self,*args,**kws):
        try:
            _str_func = ''

            if not self.mBlock:
                return
            mBlock = self.mBlock            
            
            mc.refresh(su=1)

            res = RIGBLOCKS.contextual_module_method_call(mBlock,'self',*args,**kws)
            log.debug("|{0}| >> res: {1}".format(_str_func,res))

        finally:
            mc.refresh(su=0)
            
    def uiFunc_blockCall(self,*args,**kws):
        try:
            if not self.mBlock:
                return
            mBlock = self.mBlock
            
            b_update = kws.pop('updateUI',True)
            
            mc.refresh(su=1)
            _sel = mc.ls(sl=1)
            if _sel:
                mc.select(cl=1)

            _str_func = ''
            log.info(cgmGEN._str_hardBreak)
            
            _mode = kws.get('mode')

            if _mode == 'setParentToSelected':
                mSelectedBlock = BLOCKGEN.block_getFromSelected()
                if not mSelectedBlock:
                    return log.error("|{0}| >> mode: {1} requires selected block".format(_str_func,_mode)) 
                kws['parent'] = mSelectedBlock
                kws.pop('mode')
                    
                
            #elif  _mode == 'clearParentBlock':
            #else:
                #raise ValueError,"Mode not setup: {0}".format(_mode)            
            b_devMode = False
            b_dupMode = False
            b_changeState = False
            b_rootMode = False
            if args[0] == 'changeState':
                kws['forceNew'] = True
                kws['checkDependency'] = True


            if args[0] == 'VISUALIZEHEIRARCHY':
                BLOCKGEN.get_rigBlock_heirarchy_context(mBlock,_contextMode,False,True)
                return True
            elif args[0]== 'focus':
                log.debug("|{0}| >> Focus call".format(_str_func))
                #ml_root = BLOCKGEN.get_rigBlock_heirarchy_context(ml_blocks,'root',True,False)
                #for mBlock in ml_blocks:
                log.info("|{0}| >> Focus call | {1}".format(_str_func,mBlock))                    
                mBlock.UTILS.focus(mBlock,args[1],args[2],ml_focus=[])
                return
            
            #Now parse to sets of data
            if args[0] == 'select':
                #log.info('select...')
                return mc.select(mBlock.mNode)
   
            ml_res = []
            md_dat = {}
            md_datRev = {}
            
            _short = mBlock.p_nameShort
            _call = str(args[0])
            if _call in ['atUtils']:
                _call = str(args[1])
            
            #pprint.pprint(locals())
            res = getattr(mBlock,args[0])(*args[1:],**kws) or None
            
            ml_res.append(res)
            if res:
                if kws.get('mode') not in ['prechecks']:
                    pprint.pprint(res)
                    
            if b_update:
                self.uiFunc_updateStatus()
                
                if self.mUI_builder:
                    self.mUI_builder.uiScrollList_blocks.rebuild()

            if _sel:
                try:mc.select(_sel)
                except:pass
                
        #except Exception,err:
        #    cgmGEN.cgmExceptCB(Exception,err)
        finally:
            mc.refresh(su=0)
            
    def build_menus(self):
        _str_func = 'build_menus[{0}]'.format(self.__class__.TOOLNAME)            
        log.info("|{0}| >>...".format(_str_func))   
        self.uiMenu_load = mUI.MelMenu( l='Load',pmc=self.buildMenu_load,)
        
        self.uiMenu_block = mUI.MelMenu( l='Block', pmc=self.buildMenu_block,pmo=1, tearOff=1)
        self.uiMenu_vis = mUI.MelMenu( l='Vis', tearOff=1)
        self.buildMenu_vis()
        
        self.uiMenu_OptionsMenu = mUI.MelMenu( l='Options', pmc=self.buildMenu_options)		
        
        self.uiMenu_snap = mUI.MelMenu( l='Snap', pmo=1, tearOff=1)
        self.buildMenu_snap()
        
        self.uiMenu_HelpMenu = mUI.MelMenu( l='Help', pmc=self.buildMenu_help)   

    def uiFunc_toBuilder(self):
        mUI = ui_get()
        
        if self.mBlock:
            mBlock = self.mBlock        
            try:
                mUI.uiScrollList_blocks.selectByObj(self.mBlock)
            except Exception as err:
                log.error(err)
        self.mUI_builder = mUI
        
    def buildMenu_load( self, *args):
        _str_func = 'buildMenu_load'
        
        if self.uiMenu_load:
            log.info(cgmGEN.logString_sub(_str_func,'Clear...'))               
            self.uiMenu_load.clear()
        
        #>>> Reset Options		
        log.info("|{0}| >>...".format(_str_func))   
        
        mUI.MelMenuItem(self.uiMenu_load,
                        l="Selected",
                        c = lambda *a: self.uiFunc_loadBlock(),
                        ann='Load Selected')                
        
        if not self.mBlock:
            mUI.MelMenuItem(self.uiMenu_load,label='None')
            return
        
        mUI.MelMenuItem(self.uiMenu_load,
                        l="To Builder",
                        c = lambda *a: self.uiFunc_toBuilder(),
                        ann='Open Builder')        

        mUI.MelMenuItemDiv( self.uiMenu_load )        
        
        


        mUI.MelMenuItemDiv( self.uiMenu_load )
        
        mParent = self.mParent
        mChildren = self.mChildren
        mSiblings = self.mSiblings
        mMirror = self.mMirror
        
        if mParent:
            log.info(cgmGEN.logString_sub(_str_func,'Parent...'))                           
            _key = mParent.UTILS.get_uiString(mParent)
            #NAMETOOLS.get_combinedNameDict(mParent.mNode,'cgmType')            
            mUI.MelMenuItem(self.uiMenu_load,
                          l="^ {0}".format(_key),
                          c = lambda *a: self.uiFunc_loadBlock(mParent),
                          en=  1 if mParent else 0,
                          ann='Load Parent block')
        else:
            mUI.MelMenuItem(self.uiMenu_load,
                          l='Parent',
                          en= 0,
                          ann='Load Parent block')
            
        if mChildren:
            log.info(cgmGEN.logString_sub(_str_func,'Children...'))               
            _menu =  mUI.MelMenuItem( self.uiMenu_load, l="Children ({0})".format(len(mChildren)),
                                      subMenu=True)        
            
            for i,mObj in enumerate(mChildren):
                _key = self.d_BlockStrings[mObj]
                #NAMETOOLS.get_combinedNameDict(mObj.mNode,'cgmType')
                
                mUI.MelMenuItem( _menu, l = _key,
                                 c = lambda *a:self.uiFunc_loadBlock(mObj))#
                
                
        if mSiblings:
            #mUI.MelLabel(_mRow_load,label = "Sib")
            log.info(cgmGEN.logString_sub(_str_func,'Siblings...'))    
            
            _menu =  mUI.MelMenuItem( self.uiMenu_load, l="Siblings ({0})".format(len(mSiblings)),
                                      subMenu=True)                 

            for i,mObj in enumerate(mSiblings):
                _key = self.d_BlockStrings[mObj]
                
                #_key = NAMETOOLS.get_combinedNameDict(mObj.mNode,'cgmType')
                
                mUI.MelMenuItem( _menu, l = _key,
                                 c = lambda *a:self.uiFunc_loadBlock(mObj))#
                    
        if mMirror:
            mUI.MelMenuItemDiv( self.uiMenu_load )
            
            log.info(cgmGEN.logString_sub(_str_func,'mirror...'))
            _key = mMirror.UTILS.get_uiString(mMirror)
            
            mUI.MelMenuItem(  self.uiMenu_load, l = "Mirror: {0}".format(_key),
                             c = lambda *a:self.uiFunc_loadBlock(mMirror))#
                
        
    def uiFunc_updateStatus(self):
        if not self.mBlock:
            self.uiStatus(edit=1,
                          label='...')
            
            if self.uiMenu_load:self.uiMenu_load.clear()
            
            return log.error("No block loaded")

        self.uiFunc_updateBlock()
        
        #_strBlock = self.mBlock.UTILS.get_uiString(self.mBlock)#p_nameBase
        mBlock = self.mBlock
        """
        l = []

        #...pre
        for a in ['cgmDirection','cgmPosition']:
            _v = mBlock.getMayaAttr(a)
            if _v:
                l.append(_v)
                
        #...base
        l.extend([mBlock.cgmName, mBlock.blockType])
        
        #...post
        for a in ['blockProfile']:
            _v = mBlock.getMayaAttr(a)
            if _v:
                l.append(_v)
                
        _strBlock = ">>> {0} <<<".format(' | '.join(l))"""
        
        _strBlock = self.mBlock.atUtils('get_uiString',skip = ['blockState'])
        _strState = self.mBlock.getEnumValueString('blockState')
        
        self.uiStr_header(edit=1, label = _strBlock,
                          bgc=CGMUI.guiBackgroundColorLight,
                          en=True)
                          #bgc = d_state_colors[_strState])        
        
        
        self.uiStatus(edit=1,
                      bgc = d_state_colors[_strState],
                      label="State: {0}".format(_strState))        
        

    def uiCallback_contextualSetAttrFromField(self, attr, attrType, field):
        _v = field.getValue()
        
        log.info("{0} | {1}".format(attr,_v))

        self.uiFunc_contextBlockCall('atUtils', 'blockAttr_set', **{'updateUI':False, attr:_v})
        
        if attr == 'buildProfile':
            #_strValue = BLOCKSHARE._d_attrsTo_make['buildProfile'].split(':')[_v]
            log.info("Loading buildProfile... {0}".format(_v))
            self.uiFunc_contextBlockCall('atUtils', 'buildProfile_load', _v, **{'updateUI':False})
        
        
        return
        if attrType == 'enum':
            #_strValue = ATTR.get_enumValueString(obj,attr)
            #field.setValue(_strValue)
            
            if attr == 'buildProfile':
                log.info("Loading buildProfile...")
                self._blockCurrent.atUtils('buildProfile_load',_strValue)
            if attr == 'blockProfile':
                log.info("Loading blockProfile...")
                self._blockCurrent.atUtils('blockProfile_load',_strValue)
                
    def uiCallback_setAttrFromField(self, obj, attr, attrType, field):
        _v = field.getValue()
        ATTR.set(obj,attr,_v)
        
        if attrType == 'enum':
            _strValue = ATTR.get_enumValueString(obj,attr)
            field.setValue(_strValue)
            
            if attr == 'buildProfile':
                log.info("Loading buildProfile...")
                self._blockCurrent.atUtils('buildProfile_load',_strValue)
            if attr == 'blockProfile':
                log.info("Loading blockProfile...")
                self._blockCurrent.atUtils('blockProfile_load',_strValue)                
        else:
            field.setValue(ATTR.get(obj,attr))
            
        if attr == 'numRoll':
            log.info("numRoll check...")                            
            if ATTR.datList_exists(obj,'rollCount'):
                log.info("rollCount Found...")                                            
                l = ATTR.datList_getAttrs(obj,'rollCount')
                for a in l:
                    log.info("{0}...".format(a))                                                
                    ATTR.set(obj,a, _v)
                
        if attr in ['numShapers','neckShapers']:
            log.info("loftList verify check...")
            self.mBlock.UTILS.verify_loftList(self.mBlock,_v)
            mc.evalDeferred(self.uiFunc_updateBlock,lp=True)
                #self.uiUpdate_blockDat()
                
        if attr == 'loftShape':
            log.info("loftShape push to list...")            
            for a in ATTR.datList_getAttrs(obj,'loftList'):
                ATTR.set(obj,a,_v)
            mc.evalDeferred(self.uiFunc_updateBlock,lp=True)
        
        if attr in ['numJoints','neckJoints'] or attr.startswith('rollCount'):
            log.info("")            
            try:
                self.mBlock.atBlockModule('create_jointHelpers')
                log.info("Updated jointHelpers")            
                
            except:pass
        
        log.info("Set: {0} | {1} | {2}".format(obj,attr,_v))
    
    def uiCallback_loadChild(self):
        _v = self.uiOM_child.getValue()
        mBlock =  self.mBlockDict.get(_v)
        if not mBlock:
            return
        
        self.uiBlock_content.clear()
        self.uiFunc_loadBlock( mBlock)
        
    def uiCallback_loadSibling(self):
        _v = self.uiOM_sibling.getValue()
        mBlock =  self.mBlockDict.get(_v)
        if not mBlock:
            return
        
        self.uiBlock_content.clear()
        self.uiFunc_loadBlock( mBlock)
        
    def uiPopup_createChildren(self,button):
        if self.uiPopUpMenu_children:
            self.uiPopUpMenu_children.clear()
            self.uiPopUpMenu_children.delete()
            self.uiPopUpMenu_children = None
    
        self.uiPopUpMenu_children = mUI.MelPopupMenu(button,button = 1)
        _popUp = self.uiPopUpMenu_children 
    
        mUI.MelMenuItem(_popUp,
                        label = "Set Children",
                        en=False)     
        mUI.MelMenuItemDiv(_popUp)
        
        _pop = mUI.MelMenuItem(_popUp,subMenu = True,
                               label = "Children",
                               en=True)
        
        for mChild in self.mChildren:
            _label =  mChild.p_nameBase
            mUI.MelMenuItem(_pop,
                            label = _label,
                            ann = "Set the create shape to: {0}".format(_label),
                            c=lambda *a:self.uiFunc_loadBlock(mChild))  
                
                
    def uiFunc_updateBlock(self):
        _str_func = ' uiFunc_updateBlock'
        log.debug("|{0}| >> mBlock: {1}".format(_str_func,self.mBlock))
        
        self.uiBlock_content.clear()
        
        mBlock = self.mBlock
        

        
        mParent = mBlock.p_blockParent
        mChildren = mBlock.getBlockChildren() or []
        mSiblings = mBlock.atUtils('siblings_get') or []
        mMirror = mBlock.getMessageAsMeta('blockMirror')
        
        self.d_BlockStrings = {}
        
        for mList in mChildren,mSiblings:
            mList = LISTS.get_noDuplicates(mList)
            mTmp = {}
            l_keys = []
            for mObj in mList:
                _key = mObj.UTILS.get_uiString(mObj)
                mTmp[_key] = mObj
                l_keys.append(_key)
                self.d_BlockStrings[mObj] = _key 
            
            l_keys.sort()
            mList = [mTmp[k] for k in l_keys]

        self.mParent = mParent
        self.mChildren = mChildren
        self.mSiblings = mSiblings
        self.mMirror = mMirror
        
                
        
        _d = self.mBlock.atUtils('uiQuery_getStateAttrDict',0,0)
        
        self._d_attrFields = {}
        
        _short = mBlock.mNode
        
        _keys = sorted(_d)
        l_order =['define','profile','basic','name',
                  'form','proxySurface','prerig',
                  'skeleton',
                  'rig','space','squashStretch']
        l_order.reverse()
        
        for k in l_order:
            if k in _keys:
                _keys.remove(k)
                _keys.insert(0,k)
                
        l_end = ['data','wiring','advanced']
        for k in l_end:
            if k in _keys:
                _keys.remove(k)
                _keys.append(k)        
        
        
        d_keyColors = {'profile':'define',
                       'basic':'define',
                       'name':'define',
                       'proxySurface':'form',
                       'squashStretch':'rig',
                       'space':'rig',
                       'post':'rig'}
        
        for k in _keys:
            log.debug(cgmGEN.logString_sub(_str_func,k))                
            
            l = _d.get(k)
            if not l:
                log.debug("|{0}| >> No attrs in : {1}".format(_str_func,k))                
                continue
            
            try:self.__dict__['var_{0}FrameCollapse'.format(k)]
            except:self.create_guiOptionVar('{0}FrameCollapse'.format(k),defaultValue = 0)
            
            mVar_frame = self.__dict__['var_{0}FrameCollapse'.format(k)]
            
            _frame = mUI.MelFrameLayout(self.uiBlock_content,label = CORESTRINGS.capFirst(k),vis=True,
                                        collapse=mVar_frame.value,
                                        collapsable=True,
                                        enable=True,
                                        marginWidth = 5,
                                        useTemplate = 'cgmUIHeaderTemplate',
                                        expandCommand = cgmGEN.Callback(mVar_frame.setValue,0),
                                        collapseCommand =  cgmGEN.Callback(mVar_frame.setValue,1),
                                        statusBarMessage = k,
                                        )	
            _inside = mUI.MelColumnLayout(_frame,
                                          #rowSpacing = 5,
                                          useTemplate = 'cgmUISubTemplate')
            
            _bgc = None
            _sub_bgc = d_keyColors.get(k)
            if _sub_bgc: 
                _bgc = d_uiStateSubColors.get(_sub_bgc)
                _bgc = [v*.7 for v in _bgc]
            else:
                _bgc = d_uiStateSubColors.get(k)
                
            if _bgc:
                _frame(edit=1, bgc=_bgc)
            
            if k == 'name':#Name section....-------------------------------------------------
                log.debug("|{0}| >> Name...".format(_str_func))
                _nameIter = mBlock.hasAttr('nameIter')
                if _nameIter:
                    mUI.MelLabel(_inside,l = "Tag: {0} | Iterator: {1}".format(mBlock.getMayaAttr('cgmName'),
                                                                               mBlock.getMayaAttr('nameIter')),
                                 ut ='cgmUIInstructionsTemplate' ,
                                 )
                else:
                    mUI.MelLabel(_inside,l = "Tag: {0}".format(mBlock.getMayaAttr('cgmName')),
                                 ut ='cgmUIInstructionsTemplate' ,
                                 )                    

                #Base name stuff...
                _mRow = mUI.MelHLayout(_inside,ut='cgmUISubTemplate',padding = 2)
                
                mUI.MelButton(_mRow,
                              label='Tag',ut='cgmUITemplate',
                              c = cgmGEN.Callback(self.uiFunc_blockCall,
                                                  'atUtils','set_nameTag', **{}),
                              ann='Change nameTag')
                if _nameIter:
                    mUI.MelButton(_mRow,
                                  label='NameIter',ut='cgmUITemplate',
                                  c = cgmGEN.Callback(self.uiFunc_blockCall,
                                                      'atUtils','set_nameIter', **{}),
                                  ann='Change iter name')                
                
                _mRow.layout()
                
                
                _nameList = mBlock.datList_get('nameList')
                if _nameList:
                    mc.setParent(_inside)
                    cgmUI.add_LineBreak()
                    cgmUI.add_Header('nameList')
                    
                    #mUI.MelLabel(_inside,l = 'NAMELIST',
                    #             useTemplate = 'cgmUITemplate')
                    
                    mUI.MelLabel(_inside,l = "{0} | {1}".format(len(_nameList),
                                                                [str(n) for n in _nameList]),
                                useTemplate = 'cgmUIInstructionsTemplate',
                                )
                    
                    #Namelist...
                    _mRow = mUI.MelHSingleStretchLayout(_inside,ut='cgmUISubTemplate')
                    mUI.MelSpacer(_mRow,w=_sidePadding)
                    
                    mUI.MelLabel(_mRow,l='NameList:')
                    _mRow.setStretchWidget(mUI.MelSeparator(_mRow,))
                    
                    _d_nameList = {
                                'Reset':{'ann':'Reset the name list to the profile',
                                               'call':cgmGEN.Callback(self.uiFunc_blockCall,
                                                                      'atUtils','nameList_resetToProfile',
                                                                      **{})},
                                'Edit':{'ann':'Ui Prompt to edit nameList',
                                                    'call':cgmGEN.Callback(self.uiFunc_blockCall,
                                                                           'atUtils','nameList_uiPrompt',
                                                                           **{})},                  
                                 'Iter baseName':{'ann':'Set nameList values from name attribute',
                                                  'call':cgmGEN.Callback(self.uiFunc_blockCall,
                                                                         'atUtils','set_nameListFromName',
                                                                         **{})}}
                
                    for k2,d2 in list(_d_nameList.items()):
                        mUI.MelButton(_mRow,
                                     label=k2,ut='cgmUITemplate',
                                     ann = d2.get('ann',''),
                                     c=d2.get('call'))
                        
                    mUI.MelSpacer(_mRow,w=_sidePadding)
                    _mRow.layout()
                
                
            
            if k == 'vis':
                #Lock nulls row ------------------------------------------------------------------------
                _mRow_lockNulls = mUI.MelHSingleStretchLayout(_inside,ut='cgmUISubTemplate',padding = 2)
                mUI.MelSpacer(_mRow_lockNulls,w=_sidePadding)
                
                mUI.MelLabel(_mRow_lockNulls,l='Lock null:')
                _mRow_lockNulls.setStretchWidget(mUI.MelSeparator(_mRow_lockNulls,))
                
                for null in ['formNull','prerigNull']:
                    _str_null = mBlock.getMessage(null)
                    if _str_null:
                        _nullShort = _str_null[0]
                        mUI.MelCheckBox(_mRow_lockNulls, l="- {0}".format(null),
                                        value = ATTR.get(_nullShort,'template'),
                                        onCommand = cgmGEN.Callback(ATTR.set,_nullShort,'template',1),
                                        offCommand = cgmGEN.Callback(ATTR.set,_nullShort,'template',0))                
                    else:
                        mUI.MelCheckBox(_mRow_lockNulls, l="- {0}".format(null),
                                        en=False)
                
                mUI.MelSpacer(_mRow_lockNulls,w=_sidePadding)
                _mRow_lockNulls.layout()                
                
            
            if k == 'profile':
                log.debug("|{0}| >> profile...".format(_str_func))
                
                d_profileDat = {'block':{'options':RIGBLOCKS.get_blockProfile_options(mBlock.blockType),
                                         'current':str(mBlock.getMayaAttr('blockProfile')),
                                         },
                                'build':{'options':BLOCKSHARE._l_buildProfiles,
                                         'current':str(mBlock.getMayaAttr('buildProfile'))}}
                
                
                for k2,d2 in list(d_profileDat.items()):
                    _en = True
                    _defineOff = False
                    if k2 == 'block':
                        if mBlock.blockState != 0:
                            _en = False
                            _defineOff = True
                            
                            
                    _mRow = mUI.MelHSingleStretchLayout(_inside,ut='cgmUISubTemplate',padding = 10)
                    mUI.MelLabel(_mRow,l="  {0} > ".format(CORESTRINGS.capFirst(k2)))
                    #_mRow.setStretchWidget(mUI.MelSeparator(_mRow,))            
                    
                    
                    
                    _optionMenu = mUI.MelOptionMenu(_mRow,ut = 'cgmUITemplate',h=25,en=_en)
                    
                    _mRow.setStretchWidget(_optionMenu)
                    
                    
                    self.__dict__['uiOM_{0}'.format(k2)] = _optionMenu
                
                    for option in d2.get('options',[]):
                        _optionMenu.append(option)
                        
                    try:_optionMenu.selectByValue(d2['current'])
                    except:pass
                    
                    #mUI.MelLabel(_mRow, bgc=cgmUI.guiBackgroundColorLight,w=50,al='center',en=_en,
                    #             l="{0}".format(mBlock.getMayaAttr('{0}Profile'.format(k2))))                    
                    
                    
                    mUI.MelButton(_mRow,en=_en,
                                  label='Load',ut='cgmUITemplate',
                                  c = cgmGEN.Callback(self.uiFunc_profileSet,
                                                      k2, **{}),
                                  ann='Load {0}Profile'.format(k2))     
                        
                    #mUI.MelSpacer(_mRow,w=_sidePadding)                
                    _mRow.layout()
                    
                    if _defineOff:
                        mUI.MelLabel(_inside, bgc=cgmUI.d_stateColors['warning'],
                                     w=75,al='center',
                                     en=_en,
                                     l = "blockType can only be changed in define state")
                    
                    mc.setParent(_inside)
                    cgmUI.add_LineSubBreak()
                
                    
                continue

                
                for i,item in enumerate(BLOCKSHARE._l_buildProfiles):
                    mUI.MelMenuItem(_Profiles, l=item,
                                    ann = "Load the following profile",
                                    c = cgmGEN.Callback(self.uiFunc_buildProfile_set,**{'buildProfile':item}),
                                    )                       
                
                continue
                _nameIter = mBlock.hasAttr('nameIter')
                
                
                if _nameIter:
                    mUI.MelLabel(_inside,l = "Tag: {0} | Iterator: {1}".format(mBlock.getMayaAttr('cgmName'),
                                                                               mBlock.getMayaAttr('nameIter')),
                                 ut ='cgmUIInstructionsTemplate' ,
                                 )
                else:
                    mUI.MelLabel(_inside,l = "Tag: {0}".format(mBlock.getMayaAttr('cgmName')),
                                 ut ='cgmUIInstructionsTemplate' ,
                                 )                    

                #Base name stuff...
                _mRow = mUI.MelHLayout(_inside,ut='cgmUISubTemplate',padding = 2)
                
                mUI.MelButton(_mRow,
                              label='Tag',ut='cgmUITemplate',
                              c = cgmGEN.Callback(self.uiFunc_blockCall,
                                                  'atUtils','set_nameTag', **{}),
                              ann='Change nameTag')
                if _nameIter:
                    mUI.MelButton(_mRow,
                                  label='NameIter',ut='cgmUITemplate',
                                  c = cgmGEN.Callback(self.uiFunc_blockCall,
                                                      'atUtils','set_nameIter', **{}),
                                  ann='Change iter name')                
                
                _mRow.layout()                
                continue
            
            #Attrs... ------------------------------------------------------------------------
            for a in l:
                try:
                    if a in ['blockState']:
                        continue
                    _type = ATTR.get_type(_short,a)
                    log.debug("|{0}| >> attr: {1} | {2}".format(_str_func, a, _type))
                    
                    if k in ['data','wiring']:
                        
                        mUI.MelLabel(_inside,l = "{0} | {1}".format(a, ATTR.get(_short,a)))
                        continue
                    
                    """
                    _datList = mBlock.datList_get(a)
                    if _datList:
                        mc.setParent(_inside)
                        cgmUI.add_LineBreak()
                        cgmUI.add_Header(a)
                        

                        mUI.MelLabel(_inside,l = "{0} | {1}".format(len(_datList),
                                                                    [str(n) for n in _datList]),
                                    useTemplate = 'cgmUIInstructionsTemplate',
                                    )
                        
                        #Namelist...
                        _mRow = mUI.MelHSingleStretchLayout(_inside,ut='cgmUISubTemplate')
                        mUI.MelSpacer(_mRow,w=_sidePadding)
                        
                        mUI.MelLabel(_mRow,l='NameList:')
                        _mRow.setStretchWidget(mUI.MelSeparator(_mRow,))
                        
                        _d_nameList = {
                                    'Reset':{'ann':'Reset the name list to the profile',
                                                   'call':cgmGEN.Callback(self.uiFunc_blockCall,
                                                                          'atUtils','nameList_resetToProfile',
                                                                          **{})},
                                    'Edit':{'ann':'Ui Prompt to edit nameList',
                                                        'call':cgmGEN.Callback(self.uiFunc_blockCall,
                                                                               'atUtils','nameList_uiPrompt',
                                                                               **{})},                  
                                     'Iter baseName':{'ann':'Set nameList values from name attribute',
                                                      'call':cgmGEN.Callback(self.uiFunc_blockCall,
                                                                             'atUtils','set_nameListFromName',
                                                                             **{})}}
                    
                        for k2,d2 in _d_nameList.iteritems():
                            mUI.MelButton(_mRow,
                                         label=k2,ut='cgmUITemplate',
                                         ann = d2.get('ann',''),
                                         c=d2.get('call'))
                            
                        mUI.MelSpacer(_mRow,w=_sidePadding)
                        _mRow.layout()                    """





                    _hlayout = mUI.MelHSingleStretchLayout(_inside,padding = 10)
                    
                   

                    #if _type not in ['bool']:#Some labels parts of fields
                    mUI.MelLabel(_hlayout,l="  {0} ".format(a))   
        
                    #mUI.MelSpacer(_hlayout,w=_sidePadding)
            
                    _hlayout.setStretchWidget(mUI.MelSeparator(_hlayout,))
                    
                    
                    d_datLists = {'numSubShapers':{'datList':'numSubShapers',
                                           'defaultAttr':'numSubShapers'},
                                  'numRoll':{'datList':'rollCount',
                                             'defaultAttr':'numRoll'},                                  
                          }                    
                    if a in ['numSubShapers','numRoll']:

                        mUI.MelButton(_hlayout,
                                     label='Edit datList',ut='cgmUITemplate',
                                     #ann = d2.get('ann',''),
                                     c=cgmGEN.Callback(self.uiFunc_blockCall,
                                        'atUtils','datList_validate',
                                        **{'datList':d_datLists[a].get('datList'),
                                           'defaultAttr':d_datLists[a].get('defaultAttr'),
                                           'forceEdit':1}))
                    

                    if _type == 'bool':
                        mUI.MelCheckBox(_hlayout, l="",
                                        #annotation = "Copy values",		                           
                                        value = ATTR.get(_short,a),
                                        onCommand = cgmGEN.Callback(ATTR.set,_short,a,1),
                                        offCommand = cgmGEN.Callback(ATTR.set,_short,a,0))
            
                    elif _type in ['double','doubleAngle','doubleLinear','float']:
                        self._d_attrFields[a] = mUI.MelFloatField(_hlayout,w = 50,
                                                                  value = ATTR.get(_short,a),                                                          
                                                                  )
                        self._d_attrFields[a](e=True,
                                              cc  = cgmGEN.Callback(self.uiCallback_setAttrFromField,_short, a, _type,
                                                                    self._d_attrFields[a]),
                                              )
                    elif _type == 'long':
                        self._d_attrFields[a] = mUI.MelIntField(_hlayout,w = 50,
                                                                 value = ATTR.get(_short,a),
                                                                 maxValue=20,
                                                                 minValue=ATTR.get_min(_short,a),
                                                                  )
                        self._d_attrFields[a](e=True,
                                              cc  = cgmGEN.Callback(self.uiCallback_setAttrFromField,_short, a, _type,
                                                                    self._d_attrFields[a]),
                                              )                
                    elif _type == 'string':
                        self._d_attrFields[a] = mUI.MelTextField(_hlayout,w = 75,
                                                                 text = ATTR.get(_short,a),
                                                                  )
                        self._d_attrFields[a](e=True,
                                              cc  = cgmGEN.Callback(self.uiCallback_setAttrFromField,_short, a, _type,
                                                                    self._d_attrFields[a]),
                                              )
                    elif _type == 'enum':
                        _optionMenu = mUI.MelOptionMenu(_hlayout,ut = 'cgmUITemplate')
                        _optionMenu(e=True,
                                    cc = cgmGEN.Callback(self.uiCallback_setAttrFromField,_short, a, _type,
                                                         _optionMenu),) 
                        for option in ATTR.get_enumList(_short,a):
                            _optionMenu.append(option)
                        _optionMenu.setValue(ATTR.get_enumValueString(_short,a))
                    else:
                        mUI.MelLabel(_hlayout,l="{0}({1}):{2}".format(a,_type,ATTR.get(_short,a)))        
                        
                        
                    #mUI.MelSpacer(_hlayout,w=_sidePadding)                
                    _hlayout.layout()
                except Exception as err:
                    log.warning("Attr {0} failed. err: {1}".format(a,err))            

    def uiFunc_loadBlock(self,mBlock = None):
        if mBlock == None:
            mBlock = BLOCKGEN.block_getFromSelected()
        
        
        self.mBlock = cgmMeta.validateObjArg(mBlock,'cgmRigBlock',True)
        self.block = None
        if self.mBlock:
            self.block = self.mBlock.mNode        
        else:
            return log.warning("Invalid block: {0}".format(mBlock))
        

            
        self.uiStr_header(edit=1, label = 'Syncing')
            
        _blockState = self.mBlock.getEnumValueString('blockState')
        
        if not self.block:
            self.uiStatus(edit=True,vis=True,label="Must have something loaded")
            return
        
        self.uiFunc_updateStatus()
        
        
    def build_layoutWrapper(self,parent):
        _str_func = 'build_layoutWrapper[{0}]'.format(self.__class__.TOOLNAME)            
        log.debug("|{0}| >>...".format(_str_func))
        
        _MainForm = mUI.MelFormLayout(parent,ut='cgmUITemplate')#mUI.MelColumnLayout(ui_tabs)
        
       
        _top = mUI.MelColumn(_MainForm)
        #SetHeader = mUI.MelLabel(_inside,label = '', al = 'center', ut = 'cgmUIHeaderTemplate')
        SetHeader = mUI.MelButton(_top,
                                  en=False,
                                  c=lambda *a:self.mBlock.select(),
                                  al = 'center', ut = 'cgmUIHeaderTemplate')
        self.uiStr_header = SetHeader
        

        #Inside...
        
        _inside = mUI.MelScrollLayout(_MainForm, ut='cgmUITemplate')

        #mc.setParent(_MainForm)
        _bottom = mUI.MelColumn(_MainForm)
        
        #Push Rows  -------------------------------------------------------------------------------  
        mc.setParent(_bottom)
        CGMUI.add_LineSubBreak()
        cgmUI.add_HeaderBreak()
        _row_push = mUI.MelHLayout(_bottom,ut='cgmUIHeaderTemplate',padding = 2)
        mc.button(l='Define>',
                  bgc = d_state_colors['define'],#SHARED._d_gui_state_colors.get('warning'),
                  height = 20,
                  align='center',
                  c=cgmGEN.Callback(self.uiFunc_blockCall,'changeState','define',**{'forceNew':True}),
                  ann='[Define] - initial block state')
        mc.button(l='<Form>',
                  bgc = d_state_colors['form'],              
                  height = 20,
                  align='center',                  
                  c=cgmGEN.Callback(self.uiFunc_blockCall,'changeState','form',**{'forceNew':True}),
                  ann='[Template] - Shaping the proxy and initial look at settings')
                         
        mc.button(l='<Prerig>',
                  bgc = d_state_colors['prerig'],                  
                  height = 20,
                  align='center',
                  c=cgmGEN.Callback(self.uiFunc_blockCall,'changeState','prerig',**{'forceNew':True}),
                  ann='[Prerig] - More refinded placement and setup before rig process')

        mc.button(l='<Joint>',
                  bgc = d_state_colors['skeleton'],                  
                  height = 20,
                  align='center',                  
                  c=cgmGEN.Callback(self.uiFunc_blockCall,'changeState','skeleton',**{'forceNew':True}),
                  ann='[Joint] - Build skeleton if necessary')

        mc.button(l='<Rig',
                  bgc = d_state_colors['rig'],                  
                  height = 20,
                  align='center',                  
                  c=cgmGEN.Callback(self.uiFunc_blockCall,'changeState','rig',**{'forceNew':True}),
                  ann='[Rig] - Push to a fully rigged state.')
        _row_push.layout()        
        
        
        #---------------------------------------------------------------------------------
        self.uiStatus = mUI.MelButton(_bottom,bgc=SHARED._d_gui_state_colors.get('warning'),
                                      c=lambda *a:self.uiFunc_updateStatus(),
                                      ann="Query the last buffered state and update status",
                                      label='...',
                                      h=20)
        
        #mUI.MelLabel(_MainForm,
        #                             vis=True,
        #                             bgc = SHARED._d_gui_state_colors.get('warning'),
        #                             label = '...',
        #                             h=20)        
        self.uiPB_test=None
        self.uiPB_test = mc.progressBar(vis=False)

        
        #Let's gather our attributes...
        
        self.uiBlock_content = mUI.MelColumn(_inside,
                                             #rowSpacing=2,
                                             #bgc=cgmUI.guiBackgroundColorLight,
                                             useTemplate = 'cgmUITemplate')        
        
        
        #_row_cgm = cgmUI.add_cgmFooter(_MainForm)
        mc.setParent(_MainForm)
 
        
        #_rowProgressBar = mUI.MelRow(_MainForm)

        _MainForm(edit = True,
                  af = [(_top,"top",0),
                        (_top,"left",0),
                        (_top,"right",0),
                        (_inside,"left",0),
                        (_inside,"right",0),                        
                        (_bottom,"left",0),
                        (_bottom,"right",0),
                        #(self.uiPB_test,"left",0),
                        #(self.uiPB_test,"right",0),                        
                        #(_row_cgm,"left",0),
                        #(_row_cgm,"right",0),
                        (_bottom,"bottom",0),
    
                        ],
                  ac = [(_inside,"top",0,_top),
                        (_inside,"bottom",0,_bottom),
                        #(_button,"bottom",0,_row_cgm),
                        #(self.uiPB_test,"bottom",0,_row_cgm),
                        ],
                  attachNone = [(_bottom,"top")])    
        
        
        
        

class ui_stepBuild(cgmUI.cgmGUI):
    USE_Template = 'cgmUITemplate'
    WINDOW_NAME = 'cgmBuilderSteppped'    
    WINDOW_TITLE = 'cgmBuilder | Stepped | - {0}'.format(__version__)
    DEFAULT_MENU = None
    RETAIN = True
    MIN_BUTTON = False
    MAX_BUTTON = False
    FORCE_DEFAULT_SIZE = True  #always resets the size of the window when its re-created  
    DEFAULT_SIZE = 200,275
    
    _d_ui_annotations = {'select':"Select rigBlocks in maya from ui."}
    def __init__(self,mBlock = None, *a,**kws):
        self.mBlock = cgmMeta.validateObjArg(mBlock,'cgmRigBlock',True)
        self.block = None
        if mBlock:
            self.block = self.mBlock.mNode
        super(ui_stepBuild, self).__init__(*a,**kws)
        
    def insert_init(self,*args,**kws):
        _str_func = 'post_win.insert_init'
        #kws = self.kws
        #args = self.args
        if kws:log.debug("kws: %s"%str(kws))
        if args:log.debug("args: %s"%str(args))
        #log.debug(self.__call__(q=True, title=True))
        
        self.__version__ = __version__
        self.__toolName__ = 'Builder'		
        self.WINDOW_TITLE = ui_stepBuild.WINDOW_TITLE
        self.DEFAULT_SIZE = ui_stepBuild.DEFAULT_SIZE
        self.str_lastStep = 'None'
        self.var_buildProfile = cgmMeta.cgmOptionVar('cgmVar_cgmMRSBuildProfile',
                                                    defaultValue = 'unityMed')

    def build_menus(self):pass
    
    @cgmGEN.Timer
    def uiFunc_process(self):
        _str_func = 'uiFunc_process[{0}]'.format(self.__class__.TOOLNAME)
        log.debug("|{0}| >>...".format(_str_func))
        try:
            if not self.mBlock:
                if self.block:
                    self.mBlock = cgmMeta.validateObjArg(self.block,'cgmRigBlock',True)
                    
            if not self.mBlock:
                return log.warning("|Post| >> No Block loaded")

            self.uiStatus(edit=True,vis=True,label = 'Processing...')
            
            """
            l_toDo = []
            l_order = ['Mirror Verify','Gather Space Drivers',
                       'bakeQSS','deleteQSS','exportQSS',
                       'isHistoricallyInteresting','proxyMesh',
                       'connectRig','Delete Blocks']
            d_keyToFunction = {'Mirror Verify':'mirror_verify',
                               'Gather Space Drivers':'collect_worldSpaceObjects',
                               'proxyMesh':'proxyMesh_verify',
                               'connectRig':'rig_connectAll'}
            for k in l_order:
                log.debug("|{0}| >> {1}...".format(_str_func,k)+'-'*20)
                
                if self._dCB_reg[k].getValue():#self.__dict__['cgmVar_mrsPostProcess_{0}'.format(k)].getValue():
                    l_toDo.append(k)
                    
                    
            if not l_toDo:
                return log.warning("|Post| >> No options selected")
            
            for v in ['proxyMesh','connectRig']:
                if v in l_toDo:
                    self.uiStatus(edit=True,vis = True,label='Rig Reset...')
                    cgmUI.progressBar_test(self.uiPB_test,10)                    
                    self.mBlock.atUtils('anim_reset')
                    break
            
            lenDo = len(l_toDo)
            for i,k in enumerate(l_toDo):
                log.debug("|{0}| >> Processing: {1}...".format(_str_func,k)+'-'*30)
                self.uiStatus(edit=True,vis = True, label=" {0} | {1}/{2}".format(k,i+1,lenDo))
                
                if k in ['Gather Space Drivers','Mirror Verify','connectRig','proxyMesh']:
                    self.mBlock.atUtils(d_keyToFunction.get(k),progressBar=self.uiPB_test)
                elif 'QSS' in k:
                    d_qss = {'bakeQSS':{'blockSet':0,'bakeSet':1,'deleteSet':0,'exportSet':0},
                             'deleteQSS':{'blockSet':0,'bakeSet':0,'deleteSet':1,'exportSet':0},
                             'exportQSS':{'blockSet':0,'bakeSet':0,'deleteSet':0,'exportSet':1}}
                    self.mBlock.atUtils('qss_verify',**d_qss.get(k))
                    cgmUI.progressBar_test(self.uiPB_test,100)
                elif k == 'isHistoricallyInteresting':
                    self.mBlock.atUtils('rigNodes_setAttr','ihi',0,self.uiPB_test)
                elif k == 'Delete Blocks':
                    pass
                else:
                    log.warning("Finish {0}".format(k))
                    cgmUI.progressBar_test(self.uiPB_test,100)
            """
                
        finally:
            self.uiStatus(edit=True,vis=False)
            cgmUI.progressBar_end(self.uiPB_test)
            
    @cgmGEN.Timer
    def step(self,fnc=None):
        #mc.progressBar(mayaMainProgressBar, edit=True,
                       #status = "|{0}| >>Rig>> step: {1}...".format(self.d_block['shortName'],fnc), progress=i+1)    

        mc.undoInfo(openChunk=True,chunkName=fnc)
        log.debug(fnc)
        _fncShort = self.d_funcToShort.get(fnc)
        self.uiStatus(edit=True,label="Started: {0}".format(_fncShort))
        err=None
        _short = self.mBlock.mNode
        _fail = True
        if _fncShort not in ['dataBuffer']:
            ATTR.store_info(_short, 'rigStepBuffer',_fncShort )
        try:
            getattr(self.mRigFac.d_block['buildModule'],fnc)(self.mRigFac)
            _fail = False
        except Exception as err:
            log.error(err)
            raise
            #If in a timer, we don't need to pass cgmExceptio handlder
            #cgmGEN.cgmExceptCB(Exception,err,localDat=vars())
        finally:
            mc.undoInfo(closeChunk=True)
            #self.uiStatus(edit=True,vis=True,label="Done: {0}".format(_fncShort))
            if _fail:
                self.uiStatus(edit=True,label="Failed: {0}".format(_fncShort))
            elif fnc == self.l_buildOrder[-1]:
                self.uiStatus(edit=True,label="Done")
                if ATTR.has_attr(_short,'rigStepBuffer'):
                    ATTR.delete(_short,'rigStepBuffer')
            else:
                self.uiFunc_updateStatus()
                

                

    def uiFunc_updateStatus(self):
        if not self.mBlock:
            self.uiStatus(edit=1,
                          label='...')
            return log.error("No block loaded")
        
        _status = self.mBlock.getMayaAttr('rigStepBuffer')
        if _status:
            self.uiStatus(edit=1,
                          label="State: {0}".format(_status))
        else:
            self.uiStatus(edit=1,
                          label=self.str_lastStep)
            
            
    def build_layoutWrapper(self,parent):
        _str_func = 'build_layoutWrapper[{0}]'.format(self.__class__.TOOLNAME)            
        log.debug("|{0}| >>...".format(_str_func))
        log.debug("|{0}| >> mBlock: {1}".format(_str_func,self.mBlock))
        
        _MainForm = mUI.MelFormLayout(parent,ut='cgmUITemplate')#mUI.MelColumnLayout(ui_tabs)
        _inside = mUI.MelColumnLayout(_MainForm)
        if self.mBlock:
            _strBlock = self.mBlock.UTILS.get_uiString(self.mBlock)#p_nameBase
        else:
            _strBlock = self.mBlock
            
        SetHeader = cgmUI.add_Header('{0}'.format(_strBlock))
        
        #mc.setParent(_MainForm)
        self.uiStatus = mUI.MelButton(_MainForm,bgc=SHARED._d_gui_state_colors.get('warning'),
                                      c=lambda *a:self.uiFunc_updateStatus(),
                                      ann="Query the last buffered state and update status",
                                      label='...',
                                      h=20)
        #mUI.MelLabel(_MainForm,
        #                             vis=True,
        #                             bgc = SHARED._d_gui_state_colors.get('warning'),
        #                             label = '...',
        #                             h=20)        
        self.uiPB_test=None
        self.uiPB_test = mc.progressBar(vis=False)
        _blockState = self.mBlock.getEnumValueString('blockState')
        
        if not self.block:
            self.uiStatus(edit=True,vis=True,label="Must have something loaded")
            return
        elif _blockState != 'skeleton':
            self.uiStatus(edit=True,vis=True,label="Block must be skeleton state")            
            return log.error("{0} Block must be skeleton state. Found: {1}".format(self.mBlock.p_nameShort,_blockState))
            pass
        
        mRigFac = self.mBlock.asRigFactory(autoBuild=False)
        self.mRigFac = mRigFac
        mModule = mRigFac.d_block['buildModule']
        
        
        def reloadStuff():
            cgmGEN._reloadMod(mModule)
            cgmGEN._reloadMod(BUILDERUTILS)
            cgmGEN._reloadMod(BLOCKGEN)
            cgmGEN._reloadMod(BLOCKSHARE)
            cgmGEN._reloadMod(BLOCKUTILS)
            cgmGEN._reloadMod(RIGFRAME)
        
        #SingleChecks======================================================================
        mRow_buttons = mUI.MelHLayout(_inside,ut='cgmUISubTemplate',padding = 2)
        CGMUI.add_Button(mRow_buttons, "Reload",
                         cgmGEN.Callback(reloadStuff),
                         "Reload blockModule")
        CGMUI.add_Button(mRow_buttons, "Log Self",
                         cgmGEN.Callback( mRigFac.log_self),
                         "Log Rig Factory")
        mRow_buttons.layout()
        
        #SingleChecks======================================================================
        mRow_buttons2 = mUI.MelHLayout(_inside,ut='cgmUISubTemplate',padding = 2)
        CGMUI.add_Button(mRow_buttons2, "INFO",
                         cgmGEN.Callback(mModule.log.setLevel,mModule.logging.INFO),
                         "Reload blockModule")
        CGMUI.add_Button(mRow_buttons2, "DEBUG",
                         cgmGEN.Callback(mModule.log.setLevel,mModule.logging.DEBUG),
                         "Log Rig Factory")
        mRow_buttons2.layout()        
        
        #Danger!!!!!!======================================================================
        mc.setParent(_inside)
        cgmUI.add_Header('Build Order')
        
        
        _l_buildOrder = mRigFac.d_block['buildModule'].__dict__.get('__l_rigBuildOrder__')
        if not _l_buildOrder:
            raise ValueError("No build order found")
        _len = len(_l_buildOrder)
        self.d_funcToShort = {}
        self.l_buildOrder = _l_buildOrder
        
        for i,fnc in enumerate(_l_buildOrder):
            _short = '_'.join(fnc.split('_')[1:])
            self.d_funcToShort[fnc] = _short

            CGMUI.add_Button(_inside, _short,
                             cgmGEN.Callback(self.step,fnc),
                             "Process: {0}".format(_short))            
        
        
        
        mc.setParent(_inside)
        CGMUI.add_LineBreak()
        self.uiFunc_updateStatus()
        """
        _button = mc.button(parent=_MainForm,
                            l = 'Process',
                            ut = 'cgmUITemplate',
                            #c = cgmGEN.Callback(cgmUI.progressBar_test,self.uiPB_test,10000),
                            c = cgmGEN.Callback(self.uiFunc_process),
                            ann = 'Test progress bar')"""
        
        
        
        #_row_cgm = cgmUI.add_cgmFooter(_MainForm)
        mc.setParent(_MainForm)
 
        
        #_rowProgressBar = mUI.MelRow(_MainForm)

        _MainForm(edit = True,
                  af = [(_inside,"top",0),
                        (_inside,"left",0),
                        (_inside,"right",0),
                        (self.uiStatus,"left",0),
                        (self.uiStatus,"right",0),
                        #(self.uiPB_test,"left",0),
                        #(self.uiPB_test,"right",0),                        
                        #(_row_cgm,"left",0),
                        #(_row_cgm,"right",0),
                        (self.uiStatus,"bottom",0),
    
                        ],
                  ac = [(_inside,"bottom",0,self.uiStatus),
                        #(_button,"bottom",0,_row_cgm),
                        #(self.uiPB_test,"bottom",0,_row_cgm),
                        ],
                  attachNone = [(self.uiStatus,"top")])
        
class ui_post(cgmUI.cgmGUI):
    USE_Template = 'cgmUITemplate'
    WINDOW_NAME = 'cgmBuilderPost'    
    WINDOW_TITLE = 'cgmBuilder | Post | - {0}'.format(__version__)
    DEFAULT_MENU = None
    RETAIN = True
    MIN_BUTTON = False
    MAX_BUTTON = False
    FORCE_DEFAULT_SIZE = True  #always resets the size of the window when its re-created  
    DEFAULT_SIZE = 200,230
    
    _d_ui_annotations = {'select':"Select rigBlocks in maya from ui."}
    def __init__(self,mPuppet = None, *a,**kws):
        self.mPuppet = cgmMeta.validateObjArg(mPuppet,'cgmRigPuppet',True)
        self.puppet = None
        if mPuppet:
            self.puppet = self.mPuppet.mNode
        super(ui_post, self).__init__(*a,**kws)
        
    def insert_init(self,*args,**kws):
        _str_func = 'post_win.insert_init'
        #kws = self.kws
        #args = self.args
        if kws:log.debug("kws: %s"%str(kws))
        if args:log.debug("args: %s"%str(args))
        #log.debug(self.__call__(q=True, title=True))
        
        self.__version__ = __version__
        #self.__toolName__ = 'Builder'		
        self.WINDOW_TITLE = ui_post.WINDOW_TITLE
        self.DEFAULT_SIZE = ui_post.DEFAULT_SIZE

        self.var_buildProfile = cgmMeta.cgmOptionVar('cgmVar_cgmMRSBuildProfile',
                                                    defaultValue = 'unityMed')
        
    def build_menus(self):pass
    
    @cgmGEN.Timer
    def uiFunc_process(self):
        _str_func = 'uiFunc_process[{0}]'.format(self.__class__.TOOLNAME)
        log.debug("|{0}| >>...".format(_str_func))
        try:
            if not self.mPuppet:
                if self.puppet:
                    self.mPuppet = cgmMeta.validateObjArg(self.puppet,'cgmRigPuppet',True)
                    
            if not self.mPuppet:
                return log.warning("|Post| >> No Puppet loaded")

            self.uiStatus(edit=True,vis=True,label = 'Processing...')
            
            
            l_toDo = []
            l_order = ['Mirror Verify','Gather Space Drivers',
                       'bakeQSS','deleteQSS','exportQSS',
                       'isHistoricallyInteresting','proxyMesh',
                       'connectRig','Delete Blocks']
            d_keyToFunction = {'Mirror Verify':'mirror_verify',
                               'Gather Space Drivers':'collect_worldSpaceObjects',
                               'proxyMesh':'proxyMesh_verify',
                               'connectRig':'rig_connectAll'}
            for k in l_order:
                log.debug("|{0}| >> {1}...".format(_str_func,k)+'-'*20)
                
                if self._dCB_reg[k].getValue():#self.__dict__['cgmVar_mrsPostProcess_{0}'.format(k)].getValue():
                    l_toDo.append(k)
                    
                    
            if not l_toDo:
                return log.warning("|Post| >> No options selected")
            
            for v in ['proxyMesh','connectRig']:
                if v in l_toDo:
                    self.uiStatus(edit=True,vis = True,label='Rig Reset...')
                    cgmUI.progressBar_test(self.uiPB_test,10)                    
                    self.mPuppet.atUtils('anim_reset')
                    break
            
            lenDo = len(l_toDo)
            for i,k in enumerate(l_toDo):
                log.debug("|{0}| >> Processing: {1}...".format(_str_func,k)+'-'*30)
                self.uiStatus(edit=True,vis = True, label=" {0} | {1}/{2}".format(k,i+1,lenDo))
                
                if k in ['Gather Space Drivers','Mirror Verify','connectRig','proxyMesh']:
                    self.mPuppet.atUtils(d_keyToFunction.get(k),progressBar=self.uiPB_test)
                elif 'QSS' in k:
                    d_qss = {'bakeQSS':{'puppetSet':0,'bakeSet':1,'deleteSet':0,'exportSet':0},
                             'deleteQSS':{'puppetSet':0,'bakeSet':0,'deleteSet':1,'exportSet':0},
                             'exportQSS':{'puppetSet':0,'bakeSet':0,'deleteSet':0,'exportSet':1}}
                    self.mPuppet.atUtils('qss_verify',**d_qss.get(k))
                    cgmUI.progressBar_test(self.uiPB_test,100)
                elif k == 'isHistoricallyInteresting':
                    self.mPuppet.atUtils('rigNodes_setAttr','ihi',0,self.uiPB_test)
                elif k == 'Delete Blocks':
                    pass
                else:
                    log.warning("Finish {0}".format(k))
                    cgmUI.progressBar_test(self.uiPB_test,100)
                
        finally:
            self.uiStatus(edit=True,vis=False)
            cgmUI.progressBar_end(self.uiPB_test)
        
    
    def build_layoutWrapper(self,parent):
        _str_func = 'build_layoutWrapper[{0}]'.format(self.__class__.TOOLNAME)            
        log.debug("|{0}| >>...".format(_str_func))
        log.debug("|{0}| >> mPuppet: {1}".format(_str_func,self.mPuppet))
        
        _MainForm = mUI.MelFormLayout(parent,ut='cgmUITemplate')#mUI.MelColumnLayout(ui_tabs)
        _inside = mUI.MelColumnLayout(_MainForm)
        if self.mPuppet:
            _strPuppet = self.mPuppet.cgmName
        else:
            _strPuppet = self.mPuppet
            
        SetHeader = cgmUI.add_Header('Puppet: {0}'.format(_strPuppet))
        self.uiStatus = mUI.MelLabel(_inside,
                                     vis=False,
                                     bgc = SHARED._d_gui_state_colors.get('warning'),
                                     label = '...',
                                     h=20)        
        self.uiPB_test=None
        self.uiPB_test = mc.progressBar(vis=False)
        
        """
        mc.button(parent=_inside,
                  l = 'Progress bar',
                  ut = 'cgmUITemplate',
                  c = cgmGEN.Callback(cgmUI.progressBar_test,self.uiPB_test,10000),
                  ann = 'Test progress bar')    """
    
        #add_Button(MainForm,'Reset', lambda *a: resetUI(self))
        #add_Button(MainForm,'Reload', lambda *a: reloadUI(self))
        #add_Button(MainForm,'module Reload', lambda *a: reloadUI(self))
    
        #SingleChecks======================================================================
        _l_order = ['Mirror Verify','Gather Space Drivers','connectRig','proxyMesh','isHistoricallyInteresting']
        _d = {'Gather Space Drivers':'gatherSpaceDrivers',
              'Mirror Verify':'mirrorVerify',
              'isHistoricallyInteresting':'ihi'}
        
        self._dCB_reg = {}
        for k in _l_order:
            _row = mUI.MelHSingleStretchLayout(_inside,ut='cgmUISubTemplate',padding = 5)
            mUI.MelSpacer(_row,w=10)    
            
            mUI.MelLabel(_row, label = '{0}:'.format(k))
            _row.setStretchWidget(mUI.MelSeparator(_row))

            _plug = 'cgmVar_mrsPostProcess_' + _d.get(k,k)
            try:self.__dict__[_plug]
            except:
                log.debug("{0}:{1}".format(_plug,1))
                self.__dict__[_plug] = cgmMeta.cgmOptionVar(_plug, defaultValue = 1)
    
            l = k
            _buffer = _d.get(k)
            if _buffer:l = _buffer
            _cb = mUI.MelCheckBox(_row,
                                  #annotation = 'Create qss set: {0}'.format(k),
                                  value = self.__dict__[_plug].value,
                                  onCommand = cgmGEN.Callback(self.__dict__[_plug].setValue,1),
                                  offCommand = cgmGEN.Callback(self.__dict__[_plug].setValue,0))
            self._dCB_reg[k] = _cb
            mUI.MelSpacer(_row,w=10)    
            
            _row.layout()
        
        #Danger!!!!!!======================================================================
        _l_order = ['Delete Blocks']
        _d = {'Delete Blocks':'deleteBlocks'}
    
        mc.setParent(_inside)
        cgmUI.add_Header('!!!!!DANGER!!!!!!')        
        _row = mUI.MelHLayout(_inside,ut='cgmUISubTemplate',padding = 5)
    
        for k in _l_order:
            _row = mUI.MelHSingleStretchLayout(_inside,ut='cgmUISubTemplate',padding = 5)
            mUI.MelSpacer(_row,w=10)    
    
            mUI.MelLabel(_row, label = '{0}:'.format(k))
            _row.setStretchWidget(mUI.MelSeparator(_row))
    
            _plug = 'cgmVar_mrsPostProcess_' + _d.get(k,k)
            try:self.__dict__[_plug]
            except:
                log.debug("{0}:{1}".format(_plug,1))
                self.__dict__[_plug] = cgmMeta.cgmOptionVar(_plug, defaultValue = 0)
    
            l = k
            _buffer = _d.get(k)
            if _buffer:l = _buffer
            _cb = mUI.MelCheckBox(_row,
                                  #annotation = 'Create qss set: {0}'.format(k),
                                  value = self.__dict__[_plug].value,
                                  en=False,
                                  onCommand = cgmGEN.Callback(self.__dict__[_plug].setValue,1),
                                  offCommand = cgmGEN.Callback(self.__dict__[_plug].setValue,0))
            self._dCB_reg[k] = _cb
            mUI.MelSpacer(_row,w=10)    
    
            _row.layout()                
        
        
        #Qss======================================================================
        mc.setParent(_inside)
        cgmUI.add_Header('qss')        
        _row = mUI.MelHLayout(_inside,ut='cgmUISubTemplate',padding = 5)
        
        _d = {'bake':False,
              'rotation':'rot',
              'rotateAxis':'ra',
              'rotateOrder':'ro',
              'scalePivot':'sp',
              'rotatePivot':'rp'}
        _d_defaults = {'position':1}
        _l_order = ['bake','delete','export']
        for k in _l_order:
            _plug = 'cgmVar_mrsPostProcess_QSS' + k
            try:self.__dict__[_plug]
            except:
                _default = _d_defaults.get(k,1)
                log.debug("{0}:{1}".format(_plug,_default))
                self.__dict__[_plug] = cgmMeta.cgmOptionVar(_plug, defaultValue = _default)
    
            l = k
            _buffer = _d.get(k)
            if _buffer:l = _buffer
            _cb = mUI.MelCheckBox(_row,label=l,
                                  annotation = 'Create qss set: {0}'.format(k),
                                  value = self.__dict__[_plug].value,
                                  onCommand = cgmGEN.Callback(self.__dict__[_plug].setValue,1),
                                  offCommand = cgmGEN.Callback(self.__dict__[_plug].setValue,0))
            self._dCB_reg[k+"QSS"] = _cb
        _row.layout()
        
        
        
        _button = mc.button(parent=_MainForm,
                            l = 'Process',
                            ut = 'cgmUITemplate',
                            #c = cgmGEN.Callback(cgmUI.progressBar_test,self.uiPB_test,10000),
                            c = cgmGEN.Callback(self.uiFunc_process),
                            ann = 'Test progress bar')        
        #_row_cgm = cgmUI.add_cgmFooter(_MainForm)
        mc.setParent(_MainForm)
 
        
        #_rowProgressBar = mUI.MelRow(_MainForm)

        _MainForm(edit = True,
                  af = [(_inside,"top",0),
                        (_inside,"left",0),
                        (_inside,"right",0),
                        (_button,"left",0),
                        (_button,"right",0),
                        #(self.uiPB_test,"left",0),
                        #(self.uiPB_test,"right",0),                        
                        #(_row_cgm,"left",0),
                        #(_row_cgm,"right",0),
                        (_button,"bottom",0),
    
                        ],
                  ac = [(_inside,"bottom",0,_button),
                        #(_button,"bottom",0,_row_cgm),
                        #(self.uiPB_test,"bottom",0,_row_cgm),
                        ],
                  attachNone = [(_button,"top")])
        
        
        
import cgm.core.mrs.lib.batch_utils as MRSBATCH
cgmGEN._reloadMod(MRSBATCH)
_l_post_order = MRSBATCH.l_mrsPost_order


_d_post_order = {'Gather Space Drivers':'gatherSpaceDrivers',
                 'Mirror Verify':'mirrorVerify',
                 'Delete Blocks':'deleteBlocks',
                 'isHistoricallyInteresting':'ihi'}
"""
global UISTANDALONE
UISTANDALONE = None


def uiStandAlone_get():
    global UISTANDALONE
    if UISTANDALONE:
        log.info('cached...')
        #try:
        UISTANDALONE.show()
        return UISTANDALONE
        #except Exception,err:
        #    log.error(err)
    return ui_toStandAlone()
"""



class ui_toStandAlone(cgmUI.cgmGUI):
    USE_Template = 'cgmUITemplate'
    WINDOW_NAME = 'MRSBuildSTANDALONE'    
    WINDOW_TITLE = 'MRS Build | {0}'.format(__version__)
    DEFAULT_MENU = None
    RETAIN = True
    MIN_BUTTON = False
    MAX_BUTTON = False
    FORCE_DEFAULT_SIZE = True  #always resets the size of the window when its re-created  
    DEFAULT_SIZE = 200,300
    
    def insert_init(self,*args,**kws):
        self.l_files = []
        import cgm.core.mrs.lib.batch_utils as MRSBATCH
        cgmGEN._reloadMod(MRSBATCH)        
        #global UISTANDALONE
        #UISTANDALONE = self
        
    """
    def insert_init(self,*args,**kws):
        _str_func = 'post_win.insert_init'
        #kws = self.kws
        #args = self.args
        if kws:log.debug("kws: %s"%str(kws))
        if args:log.debug("args: %s"%str(args))
        #log.debug(self.__call__(q=True, title=True))
        
        self.__version__ = __version__
        self.__toolName__ = 'ui_toStandAlone'		
        self.WINDOW_TITLE = ui_toStandAlone.WINDOW_TITLE
        self.DEFAULT_SIZE = ui_toStandAlone.DEFAULT_SIZE

        self.var_buildProfile = cgmMeta.cgmOptionVar('cgmVar_cgmMRSBuildProfile',
                                                     defaultValue = 'unityMed')
        global UISTANDALONE
        UISTANDALONE = self"""
        
    def build_menus(self):pass
    
    def uiFunc_batch(self):
        ml_masters = r9Meta.getMetaNodes(mTypes = 'cgmRigBlock',
                                         nTypes=['transform','network'],
                                         mAttrs='blockType=master')
        
        l_fails = []
        ml_fails = []
        for mMaster in ml_masters:    
            ml_context = BLOCKGEN.get_rigBlock_heirarchy_context(mMaster,'below',True,False)
    
            for mSubBlock in ml_context:
                l_fails.append(mSubBlock.asRigFactory(**{'mode':'prechecks'}).b_prechecks)
                if not l_fails[-1]: ml_fails.append(mSubBlock)
        
        if False in l_fails:
            #self.uiScrollList_blocks.selectByObj(ml_fails[0])
            result = mc.confirmDialog(title="Prechecks Failed",
                                      message= "{0} Blocks failed prechecks. \n Check scriptEditor".format(len(ml_fails)),
                                      button=['OK'],
                                      defaultButton='OK',
                                      #cancelButton='Cancel',
                                      dismissString='OK')            
            return (log.warning("Prechecks failed. Check script editor!"))
        
        log.info("Batch file creating...")
    
        import cgm.core.mrs.lib.batch_utils as MRSBATCH
        cgmGEN._reloadMod(MRSBATCH)
        MRSBATCH.create_MRS_batchFile(process=True)

    @cgmGEN.Timer
    def uiFunc_process(self, f=None, blocks = [None],
                       process = True,
                       postProcesses = True, deleteAfterProcess = True,
                       gatherOptionVars = True):
        
        _str_func = 'uiFunc_process[{0}]'.format(self.__class__.TOOLNAME)
        log.debug("|{0}| >>...".format(_str_func))
        cgmGEN._reloadMod(MRSBATCH)
                
        ml_masters = r9Meta.getMetaNodes(mTypes = 'cgmRigBlock',
                                         nTypes=['transform','network'],
                                         mAttrs='blockType=master')
        
        l_fails = []
        ml_fails = []
        for mMaster in ml_masters:    
            ml_context = BLOCKGEN.get_rigBlock_heirarchy_context(mMaster,'below',True,False)
    
            for mSubBlock in ml_context:
                l_fails.append(mSubBlock.asRigFactory(**{'mode':'prechecks'}).b_prechecks)
                if not l_fails[-1]: ml_fails.append(mSubBlock)
        
        if False in l_fails:
            #self.uiScrollList_blocks.selectByObj(ml_fails[0])
            result = mc.confirmDialog(title="Prchecks failed. Verify",
                                      message= "{0} Blocks failed prechecks. \n Check scriptEditor".format(len(ml_fails)),
                                      button=['OK'],
                                      defaultButton='OK',
                                      #cancelButton='Cancel',
                                      dismissString='OK')
            
            #if result != 'OK':
            #    log.error("|{0}| >> Cancelled | {1} | {2}.".format(_str_func,_state_target,self))
            #    return False            
            return (log.warning("Prechecks failed. Check script editor!"))
        
        log.info("Batch file creating...")        
        log.debug(self.l_files)
        if not f:
            f = copy.deepcopy(self.l_files)
            self.l_files = []#empty this as we're we don't want it staying stored after we've grabbed it
        
        #try:
        
        
        """
        f=None, blocks = [None], process = False,
                                 postProcesses = True, deleteAfterProcess = False,
                                 gatherOptionVars = True):
                                 """
            
        l_pre = ['import maya',
        'from maya import standalone',
        'standalone.initialize()',
        
        'from maya.api import OpenMaya as om2',
        'om2.MGlobal.displayInfo("Begin")',
        'import maya.cmds as mc',
        'mc.loadPlugin("matrixNodes")',      
        'import cgm.core.mrs.lib.batch_utils as MRSBATCH']
        
        l_post = ['except:',
        '    import msvcrt#...waits for key',
        '    om2.MGlobal.displayInfo("Hit a key to continue")',
        '    msvcrt.getch()',
        'om2.MGlobal.displayInfo("End")',
        'standalone.uninitialize()'    ]
        
        log.debug(cgmGEN.logString_sub(_str_func,"Checks ..."))
        
        l_paths = []
        l_dirs = []
        l_check = VALID.listArg(f)
        l_mFiles = []
        l_batch = []
        if not l_check:
            log.info(cgmGEN.logString_msg(_str_func,"No file passed. Using current"))
            l_check = [mc.file(q=True, sn=True)]
            
        
        _current = os.path.normpath(mc.file(q=True, sn=True))
        
        
        for f in l_check:
            mFile = PATHS.Path(f)
            if not mFile.exists():
                log.error("Invalid file: {0}".format(f))
                continue
            
            if os.path.normpath(f) == _current:
                if VALID.fileDirtyCheck() == False:
                    continue
            
            log.debug(cgmGEN.logString_sub(_str_func))
            
            _path = mFile.asFriendly()
            l_paths.append(_path)
            _name = mFile.name()
            
            _d = mFile.up().asFriendly()
            log.debug(cgmGEN.logString_msg(_str_func,_name))
            _batchPath = os.path.join(_d,_name+'_MRSbatch.py')
            log.debug(cgmGEN.logString_msg(_str_func,"batchPath: "+_batchPath))
            log.debug(cgmGEN.logString_msg(_str_func,"template: "+_path))
            
            
            mTar = PATHS.Path(_batchPath)
            l_join = ["try:MRSBATCH.process_blocks_rig('{0}',**".format(mFile.asString()),'{','})']
            if gatherOptionVars:
                for d,l in list(MRSBATCH.d_mrsPost_calls.items()):
                    for k in l:# _l_post_order:
                        log.debug("|{0}| >> {1}...".format(_str_func,k)+'-'*20)
                        
                        #self._dCB_reg[k].getValue():#self.__dict__['cgmVar_mrsPostProcess_{0}'.format(k)].getValue():
                        l_join.insert(2,"'{0}' : {1} ,".format(k,int(self._dCB_reg[k].getValue())))

                                    
                _l = ''.join(l_join)
           
            else:
                _l = "try:MRSBATCH.process_blocks_rig('{0}',postProcesses = {1})".format(mFile.asString(),postProcesses)
            
            print(_l)
            
            if mTar.getWritable():
                if mTar.exists():
                    os.remove(mTar)
                    
                log.warning("Writing file: {0}".format(_batchPath))
     
                with open( _batchPath, 'a' ) as TMP:
                    for l in l_pre + [_l] + l_post:
                        TMP.write( '{0}\n'.format(l) )
                        
                l_batch.append(mTar)
                        
            else:
                log.warning("Not writable: {0}".format(_batchPath))
        
        self.Close()
        
        if process:
            log.debug(cgmGEN.logString_sub(_str_func,"Processing ..."))        
            for f in l_batch:
                log.warning("Processing file: {0}".format(f.asFriendly()))            
                #subprocess.call([sys.argv[0].replace("maya.exe","mayapy.exe"),f.asFriendly()])
                subprocess.Popen([sys.argv[0].replace("maya.exe",
                                                      "mayapy.exe"),'-i',
                                  f.asFriendly()],
                                 creationflags = subprocess.CREATE_NEW_CONSOLE)# env=my_env
                
                #if deleteAfterProcess:
                #    os.remove(f)

        return
        #finally:
            #self.uiStatus(edit=True,vis=False)
            #cgmUI.progressBar_end(self.uiPB_test)
            #del self
    
    def build_layoutWrapper(self,parent):
        _str_func = 'build_layoutWrapper[{0}]'.format(self.__class__.TOOLNAME)            
        log.debug("|{0}| >>...".format(_str_func))
        
        _MainForm = mUI.MelFormLayout(parent,ut='cgmUITemplate')#mUI.MelColumnLayout(ui_tabs)
        _inside = mUI.MelScrollLayout(_MainForm)

        self.uiStatus = mUI.MelLabel(_inside,
                                     vis=False,
                                     bgc = SHARED._d_gui_state_colors.get('warning'),
                                     label = '...',
                                     h=20)        
        self.uiPB_test=None
        self.uiPB_test = mc.progressBar(vis=False)

    
        #SingleChecks======================================================================

        
        self._dCB_reg = {}
        for d,l in list(MRSBATCH.d_mrsPost_calls.items()):
            mUI.MelLabel(_inside, label = '{0}'.format(d.upper()), h = 13, 
                         ut='cgmUIHeaderTemplate',align = 'center')
            #mc.setParent(_inside)
            #cgmUI.add_Header(d)
            for k in l:
                d_dat = MRSBATCH.d_dat.get(k,{})
                
                _row = mUI.MelHSingleStretchLayout(_inside,ut='cgmUISubTemplate',padding = 5)
                mUI.MelSpacer(_row,w=10)    
                
                mUI.MelLabel(_row, label = '{0}:'.format( d_dat.get('label',k) ))
                _row.setStretchWidget(mUI.MelSeparator(_row))
    
                _plug = 'cgmVar_mrsPostProcess_' + _d_post_order.get(k,k)
                try:self.__dict__[_plug]
                except:
                    log.debug("{0}:{1}".format(_plug,1))
                    self.__dict__[_plug] = cgmMeta.cgmOptionVar(_plug, defaultValue = 1)
        
                l = k
                _buffer = _d_post_order.get(k)
                if _buffer:l = _buffer
                _cb = mUI.MelCheckBox(_row,
                                      annotation = d_dat.get('ann',k),
                                      value = self.__dict__[_plug].value,
                                      onCommand = cgmGEN.Callback(self.__dict__[_plug].setValue,1),
                                      offCommand = cgmGEN.Callback(self.__dict__[_plug].setValue,0))
                self._dCB_reg[k] = _cb
                mUI.MelSpacer(_row,w=10)    
                
                _row.layout()

        
        
        _button = mc.button(parent=_MainForm,
                            l = 'Build',
                            ut = 'cgmUITemplate',
                            #c = cgmGEN.Callback(cgmUI.progressBar_test,self.uiPB_test,10000),
                            c = lambda *a:mc.evalDeferred(self.uiFunc_process),#cgmGEN.Callback(self.uiFunc_process),
                            ann = 'Build with MRS')
        
        mc.setParent(_MainForm)
 
        _MainForm(edit = True,
                  af = [(_inside,"top",0),
                        (_inside,"left",0),
                        (_inside,"right",0),
                        (_button,"left",0),
                        (_button,"right",0),
                        #(self.uiPB_test,"left",0),
                        #(self.uiPB_test,"right",0),                        
                        #(_row_cgm,"left",0),
                        #(_row_cgm,"right",0),
                        (_button,"bottom",0),
    
                        ],
                  ac = [(_inside,"bottom",0,_button),
                        #(_button,"bottom",0,_row_cgm),
                        #(self.uiPB_test,"bottom",0,_row_cgm),
                        ],
                  attachNone = [(_button,"top")])

def uiFunc_blockCall(self,*args,**kws):
    try:
        if not self.mBlock:
            return
        mBlock = self.mBlock
        
        b_update = kws.pop('updateUI',True)
        
        mc.refresh(su=1)
        _sel = mc.ls(sl=1)
        if _sel:
            mc.select(cl=1)

        _str_func = ''
        log.info(cgmGEN._str_hardBreak)
        
        _mode = kws.get('mode')

        if _mode == 'setParentToSelected':
            mSelectedBlock = BLOCKGEN.block_getFromSelected()
            if not mSelectedBlock:
                return log.error("|{0}| >> mode: {1} requires selected block".format(_str_func,_mode)) 
            kws['parent'] = mSelectedBlock
            kws.pop('mode')
                
            
        #elif  _mode == 'clearParentBlock':
        #else:
            #raise ValueError,"Mode not setup: {0}".format(_mode)            
        b_devMode = False
        b_dupMode = False
        b_changeState = False
        b_rootMode = False
        if args[0] == 'changeState':
            kws['forceNew'] = True
            kws['checkDependency'] = True


        if args[0] == 'VISUALIZEHEIRARCHY':
            BLOCKGEN.get_rigBlock_heirarchy_context(mBlock,_contextMode,False,True)
            return True
        elif args[0]== 'focus':
            log.debug("|{0}| >> Focus call".format(_str_func))
            #ml_root = BLOCKGEN.get_rigBlock_heirarchy_context(ml_blocks,'root',True,False)
            #for mBlock in ml_blocks:
            log.info("|{0}| >> Focus call | {1}".format(_str_func,mBlock))                    
            mBlock.UTILS.focus(mBlock,args[1],args[2],ml_focus=[])
            return
        
        #Now parse to sets of data
        if args[0] == 'select':
            #log.info('select...')
            return mc.select(mBlock.mNode)

        ml_res = []
        md_dat = {}
        md_datRev = {}
        
        _short = mBlock.p_nameShort
        _call = str(args[0])
        if _call in ['atUtils']:
            _call = str(args[1])
        
        #pprint.pprint(locals())
        res = getattr(mBlock,args[0])(*args[1:],**kws) or None
        
        ml_res.append(res)
        if res:
            if kws.get('mode') not in ['prechecks']:
                pprint.pprint(res)
                
        if b_update:
            self.uiFunc_updateStatus()
            
            if self.mUI_builder:
                self.mUI_builder.uiScrollList_blocks.rebuild()

        if _sel:
            try:mc.select(_sel)
            except:pass
            
    #except Exception,err:
    #    cgmGEN.cgmExceptCB(Exception,err)
    finally:
        mc.refresh(su=0)
        
class ui(cgmUI.cgmGUI):
    USE_Template = 'cgmUITemplate'
    WINDOW_NAME = 'cgmBuilder_ui'    
    WINDOW_TITLE = 'mrsBuilder - {0}'.format(__version__)
    DEFAULT_MENU = None
    RETAIN = True
    MIN_BUTTON = True
    MAX_BUTTON = False
    FORCE_DEFAULT_SIZE = True  #always resets the size of the window when its re-created  
    DEFAULT_SIZE = 600,400
    __modes = 'space','orient','follow'
    _l_contextModes = ['self','below','root','scene']
    _l_contextStartModes = ['active','selected']
    check_cgm()
    _d_ui_annotations = {'select':"Select rigBlocks in maya from ui.",
                         'step build':"DEV | Generate a step build ui for the block",
                         'rebuild':"Rebuild blocks from define state",
                         'save blockDat':'Save current blockDat to the block',
                         'load blockDat':'Load existing blockDat from the block to current settings',
                         'reset blockDat': 'Reset blockDat to defaults as defined by the module',
                         'copy blockDat': 'Copy the blockDat from one block to another',
                         'load state blockDat': 'Load the blockDat only for this state',
                         
                         'rig connect': 'Connect the bind joints to rig joints',
                         'rig disconnect': 'Disconnect the bind joints from the rig joints',
                         'proxy verify': 'Verify proxy geo per block (if available)',
                         'delete proxy': 'Delete proxy geo if it exists',
                         'reset rig': 'Reset rig controls',
                         'query rig nodes':"Query and display the rig nodes of the block",
                         'verify':"Verify the attributes rigBlocks",
                         'Joints | tag':"Tag joints for maya tools to work better by side and tag",}    
    
    def insert_init(self,*args,**kws):
            if kws:log.debug("kws: %s"%str(kws))
            if args:log.debug("args: %s"%str(args))
            log.debug(self.__call__(q=True, title=True))
            
    
            self.__version__ = __version__
            self.__toolName__ = 'Builder'		
            #self.l_allowedDockAreas = []
            self.WINDOW_TITLE = ui.WINDOW_TITLE
            self.DEFAULT_SIZE = ui.DEFAULT_SIZE

            self.uiPopUpMenu_parent = False
            self._l_toEnable = []
            #self.create_guiOptionVar('dynParentMode',  defaultValue = ui.__modes[0])       
            self.uiScrollList_parents = False
            self.uiPopUpMenu_blocks = None
            self.uiRC_profile = None
            self._blockRoot = None
            self._blockCurrent = None
            self._blockFactory = RIGBLOCKS.factory()
            self.md_BlockPickers = {}
            
            self._d_modules = RIGBLOCKS.get_modules_dat()#...refresh data
            
            self.create_guiOptionVar('blockAttrsFrameCollapse',defaultValue = 0)
            self.create_guiOptionVar('blockSharedFrameCollapse',defaultValue = 0)
            self.create_guiOptionVar('blockInfoFrameCollapse',defaultValue = 0) 
            self.create_guiOptionVar('blockMasterFrameCollapse',defaultValue = 0) 
            self.create_guiOptionVar('blockUtilsFrameCollapse',defaultValue = 0) 
            
            self.create_guiOptionVar('contextMode',defaultValue = 0) 
            self.create_guiOptionVar('contextStartMode',defaultValue = 1) 
            self.create_guiOptionVar('contextForceMode',defaultValue = 1) 
            
            
            self.var_mrsDevMode = cgmMeta.cgmOptionVar('cgmVar_mrsDevMode', defaultValue = 0)
            self.var_buildProfile = cgmMeta.cgmOptionVar('cgmVar_cgmMRSBuildProfile',
                                                        defaultValue = 'unityMed')            
            
            self.var_rigBlockCreateSizeMode = cgmMeta.cgmOptionVar('cgmVar_rigBlockCreateSizeMode', defaultValue = 'selection')
            
            CGMDAT.uiDataSetup(self)
            
            global UI
            UI = self
            
            
    def build_menus(self):
        self.uiMenu_options = mUI.MelMenu( l='Options', pmc=self.buildMenu_options)                        
        self.uiMenu_add = mUI.MelMenu(l='Add', tearOff=1) 
        self.buildMenu_add(False)
        self.uiMenu_select = mUI.MelMenu( l='Select',pmc=self.buildMenu_select, tearOff=1)
        #self.uiMenu_picker = mUI.MelMenu( l='Picker',pmc=self.buildMenu_picker, tearOff=1)
        self.uiMenu_block = mUI.MelMenu( l='Block', pmc=self.buildMenu_block,pmo=1, tearOff=1)
        self.uiMenu_multiset = mUI.MelMenu( l='MultiSet', pmc=self.buildMenu_multiset, tearOff=1)
        
        self.uiMenu_vis = mUI.MelMenu( l='Vis', tearOff=1)
        self.buildMenu_vis()

        self.uiMenu_advanced = mUI.MelMenu( l='Advanced', pmc=self.buildMenu_advanced,pmo=1, tearOff=1)
        self.uiMenu_post = mUI.MelMenu( l='Post', pmc=self.buildMenu_post,pmo=True, tearOff=1)
        self.uiMenu_snap = mUI.MelMenu( l='Snap', pmc=self.buildMenu_snap,pmo=True, tearOff=1)        
        self.uiMenu_help = mUI.MelMenu( l='Help', pmc=self.buildMenu_help,pmo=True)
        
    def uiFunc_buildProfile_set(self,*args,**kws):
        _str_func = ''
        _updateUI = kws.pop('updateUI',True)
        _profile = kws.pop('buildProfile',None)
        

        if not _profile:
            return log.error("|{0}| >> blockProfile arg".format(_str_func))
        
        _current = self.var_buildProfile.value
        if _current != _profile:
            log.debug("|{0}| >> Setting to: {1}".format(_str_func,_profile))
            self.var_buildProfile.setValue(_profile)
            
        if self.uiScrollList_blocks.getSelectedIdxs() or self._blockCurrent:
            self.uiFunc_contextBlockCall('atUtils','buildProfile_load',_profile, **{'contextMode':'root'})

    def uiFunc_toEditor(self):
        mUI = blockEditor_get()
        
        if self.mBlock:
            mBlock = self.mBlock
        self.mUI_builder = mUI
    
    def buildMenu_select(self,*args,**kws):
        self.uiMenu_select.clear()
        _menu = self.uiMenu_select
        
        mUI.MelMenuItem(_menu, l="Roots",
                        ann='Select Roots',
                        c=cgmGEN.Callback(self.uiFunc_contextBlockCall,
                              'select',
                              **{'updateUI':0}))        
        
        mUI.MelMenuItem(_menu, l="Settings",
                        ann='Select Roots',
                        c=cgmGEN.Callback(self.uiFunc_contextBlockCall,
                              'atUtils','get_tagMessage','settingsHelper',
                              **{'selectResult':1,'updateUI':0}))
        
        mUI.MelMenuItemDiv( self.uiMenu_select, label = 'Define')
        mUI.MelMenuItem(_menu, l="Handles",
                        ann='Select  Define Handles',
                        c=cgmGEN.Callback(self.uiFunc_contextBlockCall,
                              'atUtils','get_tagMessage',
                              **{'selectResult':1,'updateUI':0,'msgList':'defineSubHandles'}))
        
        
        mUI.MelMenuItemDiv( self.uiMenu_select, label = 'Form')
        mUI.MelMenuItem(_menu, l="Orient Helper",
                        ann='Select Orient Helper',
                        c=cgmGEN.Callback(self.uiFunc_contextBlockCall,
                              'atUtils','get_tagMessage','orientHelper',
                              **{'selectResult':1,'updateUI':0}))                
        mUI.MelMenuItem(_menu, l="Handles",
                        ann='Select  Form Handles',
                        c=cgmGEN.Callback(self.uiFunc_contextBlockCall,
                              'atUtils','get_tagMessage',
                              **{'selectResult':1,'updateUI':0,'msgList':'formHandles'}))
        
        
        mSub = mUI.MelMenuItem(_menu, l="Indice",tearOff=False,
                               subMenu = True)        
        for idx in [0,-1]:
            mUI.MelMenuItem(mSub, l="{0}".format(idx),
                            ann='Select  Form Handles',
                            c=cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                  'atUtils','get_tagMessage',
                                  **{'selectResult':1,'updateUI':0,'msgList':'formHandles','idx':idx}))
        
        mUI.MelMenuItemDiv( self.uiMenu_select, label = 'Prerig')
        mUI.MelMenuItem(_menu, l="Handles",
                        ann='Select  Prerig Handles',
                        c=cgmGEN.Callback(self.uiFunc_contextBlockCall,
                              'atUtils','get_tagMessage',
                              **{'selectResult':1,'updateUI':0,'msgList':'prerigHandles'}))
        
        mSub = mUI.MelMenuItem(_menu, l="Indice",tearOff=False,
                               subMenu = True)        
        for idx in [0,-1]:
            mUI.MelMenuItem(mSub, l="{0}".format(idx),
                            ann='Select  Prerig Handles',
                            c=cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                  'atUtils','get_tagMessage',
                                  **{'selectResult':1,'updateUI':0,'msgList':'prerigHandles','idx':idx}))        
        
        
        mUI.MelMenuItem(_menu, l="Joint Helpers",
                        ann='Select Joint Handles',
                        c=cgmGEN.Callback(self.uiFunc_contextBlockCall,
                              'atUtils','get_tagMessage',
                              **{'selectResult':1,'updateUI':0,'msgList':'jointHelpers'}))        
        
        
        
        
        return 
        def buildPicker(self,mBlock):
            _key = mBlock.UTILS.get_uiString(mBlock)
            mSub = self.md_BlockPickers.get(_key)
            if mSub:
                try:mSub.delete()
                except:pass
                
            mSub = mUI.MelMenuItem(self.uiMenu_picker, l="{0}".format(_key),tearOff=True,
                                   subMenu = True)
            self.md_BlockPickers[_key] = mSub

            mBlock.atUtils('uiStatePickerMenu',mSub)
            log.info('Built picker: {0}'.format(mBlock))

        mUI.MelMenuItem(_menu, l="Roots",
                        ann='Select Roots',
                        c=cgmGEN.Callback(self.uiFunc_contextBlockCall,
                              'select',
                              **{'updateUI':0}))
        
        return
        try:
            mList = self.uiScrollList_blocks
        except:
            return log.error("No blocklist")
        
        ml_blocks = mList.getSelectedObjs()
        if not ml_blocks:
            mUI.MelMenuItem(_menu, l="None")
            return log.error("Nothing selected")
        
        mUI.MelMenuItemDiv(_menu, l="Build picker")
        for mBlock in ml_blocks:
            mUI.MelMenuItem(_menu, l="{0}".format(mBlock.UTILS.get_uiString(mBlock)),
                            c = cgmGEN.Callback(buildPicker,self,mBlock))            
        return

            
    def buildMenu_picker(self,*args,**kws):
        _menu = self.uiMenu_picker
        print(_menu)

        return
        try:
            mList = self.uiScrollList_blocks
        except:
            return log.error("No blocklist")
        
        ml_blocks = mList.getSelectedObjs()
        if not ml_blocks:
            mUI.MelMenuItem(_menu, l="None")
            return log.error("Nothing selected")
        
        mUI.MelMenuItemDiv(_menu, l="Build picker")
        for mBlock in ml_blocks:
            mUI.MelMenuItem(_menu, l="{0}".format(mBlock.UTILS.get_uiString(mBlock)))            
        return
        
        

        
        

            
        for mBlock in ml_blocks:
            mBlockModule = mBlock.getBlockModule()
            
            _sub = mUI.MelMenuItem(_menu, l="{0}".format(mBlock.UTILS.get_uiString(mBlock)),tearOff=True,
                                   subMenu = True)            
            #if 'uiBuilderMenu' in mBlockModule.__dict__.keys():
            mBlock.atUtils('uiStatePickerMenu',_sub)
        
        
        
    def buildMenu_options(self,*args,**kws):
        self.uiMenu_options.clear()
        #>>> Reset Options
        _menu = self.uiMenu_options
        
        CGMDAT.uiMenu_addDirMode(self,_menu)
        
        mUI.MelMenuItemDiv(_menu, l='UIs')
        
        
        mc.menuItem(parent = _menu,
                    l='BlockConfig',
                    ann = "BlockConfig",
                    c=lambda *a: TOOLCALLS.CONFIGDATui())        
        
        mc.menuItem(parent = _menu,
                    l='BlockDat',
                    ann = "Blockdat",
                    c=lambda *a: TOOLCALLS.BLOCKDATui())
        mc.menuItem(parent = _menu,
                    l='ShapeDat',
                    ann = "ShapeDat",
                    c=lambda *a: TOOLCALLS.SHAPEDATui())
                
        
        mUI.MelMenuItemDiv(_menu, l='Context')
        
        #Context ...---------------------------------------------------------------------------------
        _context = mUI.MelMenuItem(_menu, l="Context",tearOff=True,
                                   subMenu = True)
        
        uiRC = mc.radioMenuItemCollection()
        
        #self._l_contextModes = ['self','below','root','scene']
        _d_ann = {'self':'Context is only of the active/sel block',
                  'below':'Context is active/sel block and below',
                  'root':'Context is active/sel root and below',
                  'scene':'Context is all blocks in the scene. Careful skippy!',}
        
        _on = self.var_contextMode.value
        for i,item in enumerate(self._l_contextModes):
            if i == _on:_rb = True
            else:_rb = False
            mUI.MelMenuItem(_context,label=self._l_contextModes[i],
                            collection = uiRC,
                            rb=_rb,
                            ann = _d_ann[item],
                            c = cgmGEN.Callback(self.uiUpdate_context,
                                                self.var_contextMode,i))        
       
        #=============================================================================
        
        #Begin with ...---------------------------------------------------------------------------------
        _beginWith = mUI.MelMenuItem(_menu, l="Begin With",tearOff=True,
                                   subMenu = True)
        
        uiRC = mc.radioMenuItemCollection()
        
        #self._l_contextStartModes = ['active','selected']
        _d_ann = {'active':'Context begins with active block',
                  'selected':'Context beghins with selected block in the picker on the left',}
        
        _on = self.var_contextStartMode.value
        for i,item in enumerate(self._l_contextStartModes):
            if i == _on:_rb = True
            else:_rb = False
            mUI.MelMenuItem(_beginWith,label=self._l_contextStartModes[i],
                            collection = uiRC,
                            rb=_rb,
                            ann = _d_ann[item],
                            c = cgmGEN.Callback(self.uiUpdate_context,
                                                self.var_contextStartMode,i))
            
        #=============================================================================
        
        #Force ...---------------------------------------------------------------------------------
        uiRC = mc.radioMenuItemCollection()
        
        _contextForce = mUI.MelMenuItem(_menu, l="Force",tearOff=True,
                                   subMenu = True)
        
        _on = self.var_contextForceMode.value
        for i,item in enumerate(['False','True']):        
            if i == _on:_rb = True
            else:_rb = False
            mUI.MelMenuItem(_contextForce,label=item,
                            collection = uiRC,
                            rb=_rb,
                            c = cgmGEN.Callback(self.uiUpdate_context,
                                                self.var_contextForceMode,i))        
        #=============================================================================
        
        
        mUI.MelMenuItemDiv(_menu, l='Other')
        
        
        _Profiles = mUI.MelMenuItem(_menu, l="Profiles",tearOff=True,
                                    subMenu = True)
        for i,item in enumerate(BLOCKSHARE._l_buildProfiles):
            mUI.MelMenuItem(_Profiles, l=item,
                            ann = "Load the following profile",
                            c = cgmGEN.Callback(self.uiFunc_buildProfile_set,**{'buildProfile':item}),
                            )                
        
        uiOptionMenu_devMode(self, self.uiMenu_options)      

        mUI.MelMenuItemDiv( self.uiMenu_options )
        mUI.MelMenuItem( self.uiMenu_options, l="Dock",
                         c = lambda *a:self.do_dock())
        mUI.MelMenuItem( self.uiMenu_options, l="Reload",
                         c = lambda *a:mc.evalDeferred(self.reload,lp=True))
        mUI.MelMenuItem( self.uiMenu_options, l="Reset",
                         c = lambda *a:mc.evalDeferred(self.reload,lp=True))   
            
            
    def buildMenu_profile( self, *args, **kws):
        self.uiMenu_profile.clear()
        _menu = self.uiMenu_profile
        
        for i,item in enumerate(BLOCKSHARE._l_buildProfiles):
            mUI.MelMenuItem(_menu, l=item,
                            ann = "Load the following profile",
                            c = cgmGEN.Callback(self.uiFunc_buildProfile_set,**{'buildProfile':item}),
                            )        
        
        return


    

        
    def buildMenu_post( self, *args, **kws):
        self.uiMenu_post.clear()
        _menu = self.uiMenu_post
        
        #_mPuppet = mUI.MelMenuItem(self.uiMenu_post, l="Puppet",subMenu=True)
        mUI.MelMenuItem( _menu, l="Rig Prep",
                         #c = cgmGEN.Callback(ui)
                         c=cgmGEN.Callback(self.uiFunc_contextPuppetCall,'postUI'))
        mUI.MelMenuItemDiv(_menu)
        mUI.MelMenuItem(_menu, l="Report",
                        ann = "Report rig data",
                        c= cgmGEN.Callback(self.uiFunc_contextPuppetCall,'get_report'),
                        )
        mUI.MelMenuItem(_menu, l="Report | CSV",
                        ann = "Report rig data as csv",
                        c= cgmGEN.Callback(self.uiFunc_contextPuppetCall,'get_report_asset'),
                        )                        
        mUI.MelMenuItem( _menu, l="Gather Blocks",
                         c = self.uiCallback(self,BUILDERUTILS.gather_rigBlocks,self.uiPB_mrs))
                         #c=lambda *a: BUILDERUTILS.gather_rigBlocks(self.uiPB_mrs) )

        mUI.MelMenuItem(_menu, l="Up to date?",
                        ann = "Please don't mess with this if you don't know what you're doing ",
                        c= cgmGEN.Callback(self.uiFunc_contextPuppetCall,'is_upToDate'),
                        )        
        _subCalls = mUI.MelMenuItem( _menu, l="Calls",subMenu=True,tearOff=True)
        
        mUI.MelMenuItem(_subCalls, l="Mirror verify",
                        ann = "Please don't mess with this if you don't know what you're doing ",
                        c = cgmGEN.Callback(self.uiFunc_contextPuppetCall,'mirror_verify'),
                        )
        mUI.MelMenuItem(_subCalls, l="Check dups",
                        ann = "Check puppet for duplicate strings",
                        c = cgmGEN.Callback(self.uiFunc_contextPuppetCall,'controls_checkDups'),
                        )
        mUI.MelMenuItem(_subCalls, l="Gather space drivers",
                                ann = "Gather world and puppet space drivers ",
                                c= cgmGEN.Callback(self.uiFunc_contextPuppetCall,'collect_worldSpaceObjects'),
                                )
        mUI.MelMenuItem(_subCalls, l="Controllers | Verify",
                                ann = "Build controller setup",
                                c= cgmGEN.Callback(self.uiFunc_contextPuppetCall,'controller_verify'),
                                )        
        mUI.MelMenuItem(_subCalls, l="Controllers | Purge",
                                ann = "Purge Controller setup",
                                c= cgmGEN.Callback(self.uiFunc_contextPuppetCall,'controller_purge'),
                                )        
        """
        mUI.MelMenuItem(_menu, l="Armature Verify",
                        ann = "Verify puppet armature ",
                        c= cgmGEN.Callback(self.uiFunc_contextPuppetCall,'armature_verify'),
                        )
        mUI.MelMenuItem(_menu, l="Armature Remove",
                        ann = "Remove puppet armature ",
                        c= cgmGEN.Callback(self.uiFunc_contextPuppetCall,'armature_remove'),
                        )"""
        mUI.MelMenuItem(_subCalls, l="Qss - Bake set",
                        ann = "Add bake set",
                        c= cgmGEN.Callback(self.uiFunc_contextPuppetCall,
                                           'qss_verify',**{'puppetSet':False,
                                                           'bakeSet':True,
                                                           'deleteSet':False,
                                                           'exportSet':False}),)
        mUI.MelMenuItem(_subCalls, l="Qss - Delete set",
                        ann = "Add delete set",
                        c= cgmGEN.Callback(self.uiFunc_contextPuppetCall,
                                           'qss_verify',**{'puppetSet':False,
                                                           'bakeSet':False,
                                                           'deleteSet':True,
                                                           'exportSet':False}),)
        mUI.MelMenuItem(_subCalls, l="Qss - Export set",
                                ann = "Add export set - visible geo and joints",
                                c= cgmGEN.Callback(self.uiFunc_contextPuppetCall,
                                                   'qss_verify',**{'puppetSet':0,
                                                                   'bakeSet':0,
                                                                   'deleteSet':0,
                                                                   'exportSet':1}),)
        
        _mHistorical = mUI.MelMenuItem(_subCalls, l="Is Historically Interesing",
                                         subMenu = True)
        mUI.MelMenuItem(_mHistorical, l="Off",
                        ann = "Turn off every node's isHistoricallyInteresting option",
                        c = cgmGEN.Callback(CONTEXT.set_attrs,None,'ihi',0,'scene',None,'reselect'))
        mUI.MelMenuItem(_mHistorical, l="On",
                        ann = "Turn on every node's isHistoricallyInteresting option",
                        c = cgmGEN.Callback(CONTEXT.set_attrs,None,'ihi',1,'scene',None,'reselect'))
        
        #>>Mesh ---------------------------------------------------------------------
        mUI.MelMenuItemDiv(_menu)        
        _mMesh = mUI.MelMenuItem(_menu, l="Puppet Mesh",tearOff=True,
                                 subMenu = True)
        
        mUI.MelMenuItem(_mMesh, l="Unified",
                        ann = "Create a unified unskinned puppet mesh from the active block's basis.",
                        c = cgmGEN.Callback(self.uiFunc_contextBlockCall,'atUtils','puppetMesh_create',
                                            **{'unified':True,'skin':False}))
        mUI.MelMenuItem(_mMesh, l="Unified [Skinned]",
                        ann = "Create parts skinned puppet mesh from the active block's basis.",
                        c = cgmGEN.Callback(self.uiFunc_contextBlockCall,'atUtils','puppetMesh_create',
                                            **{'unified':True,'skin':True}))
        mUI.MelMenuItem(_mMesh, l="Unified Proxy [Skinned]",
                        ann = "Create proxy skinned puppet mesh.",
                        c = cgmGEN.Callback(self.uiFunc_contextPuppetCall,'puppetMesh_create',
                                            **{'unified':True,'skin':True,'proxy':True}))        
        mUI.MelMenuItem(_mMesh, l="Unified Proxy",
                        ann = "Create proxy puppet mesh",
                        c = cgmGEN.Callback(self.uiFunc_contextBlockCall,'atUtils','puppetMesh_create',
                                            **{'unified':True,'skin':False,'proxy':True}))        
        
        
        mUI.MelMenuItem(_mMesh, l="Parts Mesh",
                        ann = "Create parts unskinned puppet mesh from the active block's basis.",
                        c = cgmGEN.Callback(self.uiFunc_contextBlockCall,'atUtils','puppetMesh_create',
                                            **{'unified':False,'skin':False}))
        mUI.MelMenuItem(_mMesh, l="Parts Mesh [Skinned]",
                        ann = "Create parts skinned puppet mesh from the active block's basis.",
                        c = cgmGEN.Callback(self.uiFunc_contextBlockCall,'atUtils','puppetMesh_create',
                                            **{'unified':False,'skin':True}))
        mUI.MelMenuItem(_mMesh, l="Proxy Mesh [Parented]",
                        ann = "Create proxy puppet mesh parented to skin joints from the active block's basis.",
                        c = cgmGEN.Callback(self.uiFunc_contextBlockCall,'atUtils','puppetMesh_create',
                                            **{'proxy':True,'unified':False,'skin':False}))        
        mUI.MelMenuItem(_mMesh, l="Delete",
                        ann = "Remove skinned or wired puppet mesh",
                        c = cgmGEN.Callback(self.uiFunc_contextBlockCall,'atUtils','puppetMesh_delete'))
            
    def buildMenu_block(self,*args,**kws):
        self.uiMenu_block.clear()   
        _menu = self.uiMenu_block
        d_s = {'Set Side':{},
               'Set Position':{},
               'Skeleton':{'Joints | get bind':{'ann':self._d_ui_annotations.get('Joints | get bind'),
                               'call':cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                      'atUtils','skeleton_getBind',
                                      **{'select':1,'mode':'noSelect'})},
                           'Joints | get report':{'ann':self._d_ui_annotations.get('Joints | get report'),
                                                          'call':cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                                                 'atUtils','skeleton_getReport',
                                                                 **{'updateUI':0})},                           
                           'Joints | tag':{'ann':self._d_ui_annotations.get('Joints | tag'),
                                                          'call':cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                                                 'atUtils','skeleton_getBind',
                                                                 **{'tag':1})}                           
                           },
       
               'Rig':{'Step Build':{'ann':self._d_ui_annotations.get('step build'),
                               'call':cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                                      'stepUI',
                                                      **{'updateUI':0,'mode':'stepBuild'})},
                      'Prechecks':{'ann':'Precheck blocks for problems',
                                   'call':cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                                          'asRigFactory',
                                                          **{'updateUI':0,'mode':'prechecks'})},                      
                      'Proxy | Verify':{'ann':self._d_ui_annotations.get('verify proxy mesh'),
                               'call':cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                      'verify_proxyMesh',
                                      **{'updateUI':0})},
                      'Proxy | Delete':{'ann':self._d_ui_annotations.get('delete proxy mesh'),
                               'call':cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                      'proxyMesh_delete',
                                      **{'updateUI':0})},                      
                      'Rig Connect':{'ann':self._d_ui_annotations.get('connect rig'),
                                        'call':cgmGEN.Callback(self.uiFunc_contextModuleCall,'rig_connect',**{'updateUI':0})},
                      'Rig Disconnect':{'ann':self._d_ui_annotations.get('disconnect rig'),
                                     'call':cgmGEN.Callback(self.uiFunc_contextModuleCall,'rig_disconnect',**{'updateUI':0})},                      
                      'Reset Controls':{'ann':self._d_ui_annotations.get('reset rig controls'),
                               'call':cgmGEN.Callback(self.uiFunc_contextModuleCall,
                                      'rig_reset',
                                      **{'updateUI':0})},
                                       
                      'Query Nodes':{'ann':self._d_ui_annotations.get('query rig nodes'),
                               'call':cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                      'atUtils','rigNodes_get',
                                      **{'updateUI':0,'report':True})},},
               
               
               'Parent':{'To Active':{'ann':'Set parent block to active block',
                                  'call':cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                                         'atUtils','blockParent_set',
                                                         **{'mode':'setParentToActive'})},
                         'To Selected':{'ann':'Set parent block to selected block',
                                      'call':cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                                             'atUtils','blockParent_set',
                                                             **{'mode':'setParentToSelected'})},                         
                         'Clear':{'ann':'Clear blockParent',
                                           'call':cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                                                  'atUtils','blockParent_set',
                                                                  **{'parent':False})},},
               'Siblings':{'Form | Push Sub shapers':{'ann':'Push Sub shaper values to siblings',
                                  'call':cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                                         'atUtils','siblings_pushSubShapers',
                                                         **{})},
                           'Form | Push Handles':{'ann':'Push form shaper values to siblings',
                                               'call':cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                                                      'atUtils','siblings_pushFormHandles',
                                                                      **{})},                           
                         'Prerig | Push Handles':{'ann':'Push prerig handle values to siblings',
                                  'call':cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                                         'atUtils','siblings_pushPrerigHandles',
                                                         **{})}},               
               'Form':{'Snap to RP':{'ann':'Snap handles to rp plane',
                                 'call':cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                 'atUtils', 'handles_snapToRotatePlane','form',True,
                                 **{'updateUI':0})},
                       'Rebuild Block Shape':{'ann':'Rebuild the block shape',
                                              'call':cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                              'atUtils', 'rootShape_update',
                                              **{'updateUI':0})},
                       'Snap Handles to Param Attr':{'ann':'Snap handles to their param values',
                                                     'call':cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                                     'atUtils', 'form_snapHandlesToParam',
                                                     **{'updateUI':0})},                       
                              },
               
               'Names':{ 
                   'divTags':['nameList | edit'],
                   'Name | Set tag':{'ann':'Set the name tag of the block and rename dags',
                                     'call':cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                                            'atUtils','set_nameTag', **{})},
                   'Position | Set tag':{'ann':'Set the position tag of the block and rename dags',
                                         'call':cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                                                'atUtils','set_position',
                                                                **{'ui':True})},
                  'nameList | reset':{'ann':'Reset the name list to the profile',
                                 'call':cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                                        'atUtils','nameList_resetToProfile',
                                                        **{})},
                  'nameList | edit':{'ann':'Ui Prompt to edit nameList',
                                      'call':cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                                             'atUtils','nameList_uiPrompt',
                                                             **{})},                  
                   'nameList | iter baseName':{'ann':'Set nameList values from name attribute',
                                 'call':cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                                        'atUtils','set_nameListFromName',
                                                        **{})}},
               
               
               
               'Prerig':{
                   'Visualize | RP Pos':{'ann':'Create locator at the where the system thinks your rp handle will be',
                             'call':cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                'atUtils', 'prerig_get_rpBasePos',
                                **{'markPos':1,'updateUI':0})},
                   'Visualize | Up Vector':{'ann':'Create a curve showing what the assumed rp up vector is',
                                         'call':cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                            'atUtils', 'prerig_get_upVector',
                                            **{'markPos':1,'updateUI':0})},
                   'Visualize | Fame Shapes':{'ann':'Create frame shapes to test castVectors',
                                         'call':cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                            'atUtils', 'shapes_castTest',
                                            **{'updateUI':0})},  
                   
                   'Snap RP to Orient':{'ann':'Snap rp hanlde to orient vector',
                            'call':cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                   'atUtils', 'prerig_snapRPtoOrientHelper',
                                   **{'updateUI':0})},
                   'Snap to RP':{'ann':'Snap handles to rp plane',
                                 'call':cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                 'atUtils', 'handles_snapToRotatePlane','prerig',True,
                                 **{'updateUI':0})},
                   'Handles | Lock':{'ann':'Lock the prerig handles',
                                 'call':cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                 'atUtils', 'prerig_handlesLock',True,
                                 **{'updateUI':0})},
                   'Handles | Unlock':{'ann':'Unlock the prerig handles',
                                   'call':cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                   'atUtils', 'prerig_handlesLock',False,
                                   **{'updateUI':0})},
                   'divTags':['Handles | Lock','Query Indices',
                              'Visualize | Fame Shapes',
                              ],                   
                   'Arrange | Linear Spaced':{'ann':'Unlock the prerig handles',
                                             'call':cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                             'atUtils', 'prerig_handlesLayout','spaced','linear',
                                             **{'updateUI':0})},
                   'Arrange | Linear Even':{'ann':'Unlock the prerig handles',
                                             'call':cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                             'atUtils', 'prerig_handlesLayout','even','linear',
                                             **{'updateUI':0})},
                   'Arrange | Cubic Even':{'ann':'Unlock the prerig handles',
                                            'call':cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                            'atUtils', 'prerig_handlesLayout','even','cubicRebuild',
                                            **{'updateUI':0})},
                   'Arrange | Cubic Spaced':{'ann':'Unlock the prerig handles',
                                             'call':cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                             'atUtils', 'prerig_handlesLayout','spaced','cubicRebuild',
                                             **{'updateUI':0})},                                      

                   },
               'Geo':{
                   'order':['Block Mesh','Block Loft | Default',
                            'Block Loft | Even',
                            'Puppet Mesh',
                            'Unified','Unified [Skinned]',
                            'Parts Mesh','Parts Mesh [Skinned]',
                            'Proxy Mesh [Parented]','Delete',
                            ],
                   'divTags':['Delete'],
                   'headerTags':['Puppet Mesh'],
                   'Block Mesh':{'ann':'Generate Simple mesh',
                               'call':cgmGEN.CB(self.uiFunc_contextBlockCall,
                                                'atUtils','create_simpleMesh',
                                                **{'connect':False,'updateUI':0,'deleteHistory':1})},
                   'Block Loft | Default':{'ann':'Generate Simple mesh with history to tweak the loft manually',
                               'call':cgmGEN.CB(self.uiFunc_contextBlockCall,
                                                'atUtils','create_simpleMesh',
                                                **{'connect':False,'updateUI':0,'deleteHistory':0})},
                   'Block Loft | Even':{'ann':'Generate Simple mesh with history to tweak the loft manually',
                                 'call':cgmGEN.CB(self.uiFunc_contextBlockCall,
                                                  'atUtils','create_simpleMesh',
                                                  **{'connect':False,'updateUI':0,'deleteHistory':0,
                                                     'loftMode':'evenCubic'})},                   
                   'Unified':{'ann':"Create a unified unskinned puppet mesh from the active block's basis.",
                              'call':cgmGEN.CB(self.uiFunc_contextBlockCall,'atUtils','puppetMesh_create',
                                               **{'unified':True,'skin':False})},
                   'Unified [Skinned]':{
                       'ann':"Create parts skinned puppet mesh from the active block's basis.",
                       'call':cgmGEN.CB(self.uiFunc_contextBlockCall,'atUtils','puppetMesh_create',
                                         **{'unified':True,'skin':True})},
                   'Parts Mesh':{
                       'ann':"Create parts unskinned puppet mesh from the active block's basis.",
                       'call':cgmGEN.CB(self.uiFunc_contextBlockCall,'atUtils','puppetMesh_create',
                                         **{'unified':False,'skin':False})},
                   'Parts Mesh [Skinned]':{
                       'ann':"Create parts skinned puppet mesh from the active block's basis.",
                       'call':cgmGEN.CB(self.uiFunc_contextBlockCall,'atUtils','puppetMesh_create',
                                         **{'unified':False,'skin':True})},
                   'Proxy Mesh [Parented]':{
                       'ann':"Create proxy puppet mesh parented to skin joints from the active block's basis.",
                       'call':cgmGEN.CB(self.uiFunc_contextBlockCall,'atUtils','puppetMesh_create',
                                         **{'proxy':True,'unified':False,'skin':False})},
                   'Delete':{
                       'ann':"Remove skinned or wired puppet mesh",
                       'call':cgmGEN.CB(self.uiFunc_contextBlockCall,'atUtils','puppetMesh_delete')},
                   },
        
               
               
               'Blockdat':{
                   'order':['Save','Load','Load State','Query','Copy','Export','Load Specific',
                            ],
                   'divTags':[],
                   'headerTags':['Load Specific'],
                   'Save':{'ann':self._d_ui_annotations.get('save blockDat'),
                                 'call':cgmGEN.CB(self.uiFunc_contextBlockCall,
                                                  'saveBlockDat',
                                                  **{'updateUI':0})},
                   'Load':{'ann':self._d_ui_annotations.get('load blockDat'),
                                 'call':cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                      'loadBlockDat',
                                      **{})},
                   'Load State':{'ann':self._d_ui_annotations.get('load state blockDat'),
                                 'call': cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                                         'loadBlockDat',
                                                         **{'updateUI':0,'autoPush':False,'currentOnly':True})},
                   'Query':{'ann':self._d_ui_annotations.get('get blockDat'),
                                 'call':cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                      'getBlockDat',
                                      **{'updateUI':0})},
                   'Copy':{'ann':"Copy the active blocks data",
                                 'call':cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                      'atUtils','blockDat_copy',
                                      **{'mode':'blockDatCopyActive'})},
                   'Export':{'ann':"Export blockDat (TESTING)",
                             'call':cgmGEN.Callback(self.uiFunc_contextBlockCall,
                             'exportBlockDat',
                             **{'updateUI':0})}                   
                                  },
               'ShapeDat':{
                   'Save':{'ann':self._d_ui_annotations.get('save blockDat'),
                           'call':cgmGEN.CB(self.uiFunc_contextBlockCall,
                                            'saveShapeDat',
                                            **{'updateUI':0})},                   
               },
               'General':{
                'order':['Select','Verify','Bake Scale','Duplicate','Delete',
                         ],
                'divTags':[],
                'headerTags':[],
                'Select':{'ann':'Select Blocks',
                              'call':cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                      'select',
                                      **{'updateUI':0})},
                'Verify':{'ann':'Verify',
                              'call':cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                      'verify',
                                      **{'updateUI':0})},
                'Bake Scale':{'ann':'Bake the Scale down so the rigBlock is 1.0',
                              'call': cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                      'atUtils','blockScale_bake',
                                      **{'updateUI':0})},
                'Duplicate':{'ann':'Duplicate',
                              'call':cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                      'duplicate',
                                      **{'updateUI':1})},
                'Delete':{'ann':"Delete",
                              'call':cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                      'delete',
                                      **{'updateUI':1})},
                'Outliner Color':{'ann':"Color blocks for the outliner",
                                  'call':cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                         'atUtils','color_outliner')},             
                               },
               'Mirror':{
                'order':['Build','Rebuild','Push','Pull','Form|Push','Form|Pull','Prerig|Push','Prerig|Pull','Self','Left', 'Right',
                         'Settings',' Push',' Pull','SubShapes','   Push', '   Pull'],
                'divTags':[],
                'headerTags':['Self','Settings','SubShapes'],
                'Build':{'ann':'Build Mirror block',
                         'call':cgmGEN.Callback(self.uiFunc_contextBlockCall,
                             'atUtils','blockMirror_create',
                             **{})},
                'Rebuild':{'ann':'Rebuild Mirror block',
                           'call':cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                  'atUtils','blockMirror_create',True,
                                  **{})},
                'Push':{'ann':'Push setup to the mirror',
                        'call': cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                  'atUtils','blockMirror_go',
                                  **{'mode':'push','updateUI':0})},
                'Pull':{'ann':'Pull setup to the mirror',
                        'call': cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                  'atUtils','blockMirror_go',
                                  **{'mode':'pull','updateUI':0})},
                
                'Form|Push':{'ann':'Push form to the mirror',
                        'call': cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                  'atUtils','blockMirror_go',
                                  **{'mode':'push','updateUI':0,'define':False,'prerig':False})},
                'Form|Pull':{'ann':'Pull form to the mirror',
                        'call': cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                  'atUtils','blockMirror_go',
                                  **{'mode':'pull','updateUI':0,'define':False,'prerig':False})},
                'Prerig|Push':{'ann':'Push prerig to the mirror',
                        'call': cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                  'atUtils','blockMirror_go',
                                  **{'mode':'push','updateUI':0,'define':False,'form':False})},
                'Prerig|Pull':{'ann':'Pull prerig to the mirror',
                        'call': cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                  'atUtils','blockMirror_go',
                                  **{'mode':'pull','updateUI':0,'define':False,'form':False})},                
                
                
                'Left':{'ann':'Mirror self - Left Prime Axis',
                        'call': cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                  'atUtils','mirror_self',
                                  **{'primeAxis':'left','updateUI':0})},
                'Right':{'ann':'Mirror self - Right Prime Axis',
                        'call': cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                  'atUtils','mirror_self',
                                  **{'primeAxis':'right','updateUI':0})},
                
                ' Push':{'ann':'Mirror block settings in context | push',
                                   'call': cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                  'atUtils','blockMirror_settings',
                                  **{'updateUI':True,'mode':'push'})},
                ' Pull':{'ann':'Mirror block settings in context | push',
                                   'call': cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                  'atUtils','blockMirror_settings',
                                  **{'updateUI':True,'mode':'pull'})},                   
               '   Push':{'ann':'Mirror block settings in context | push',
                                  'call': cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                 'atUtils','blockMirror_subShapers',
                                 **{'updateUI':True,'mode':'push'})},
               '   Pull':{'ann':'Mirror block settings in context | push',
                                  'call': cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                 'atUtils','blockMirror_subShapers',
                                 **{'updateUI':True,'mode':'pull'})},
               },
               
               }

      
        
        
        
        
        """
        for state in ['define','form','prerig']:
            d_s['blockDat']['order'].append('Load {0}'.format(state))
            d_s['blockDat']['Load {0}'.format(state)] = {
                'ann':"Load {0} blockDat in context".format(state),
                'call':cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                       'atUtils','blockDat_load_state',state,
                                       **{})}"""
           
        
        mUI.MelMenuItem(_menu,
                        label = 'Select',
                        ann = 'Select Blocks',
                        c = cgmGEN.Callback(self.uiFunc_contextBlockCall,
                              'select',
                              **{'updateUI':0}))
        mUI.MelMenuItemDiv(_menu)                
        
        
        l_keys = sorted(d_s)
        
        l_check = ['Define','Form','Prerig','Skeleton','Rig','General','Mirror','Blockdat']
        l_check.reverse()
        for k in l_check:
            if k in l_keys:
                l_keys.remove(k)
                l_keys.insert(0,k)
                
        for s in l_keys:
            d = d_s[s]
            divTags = d.get('divTags',[])
            headerTags = d.get('headerTags',[])
            
            _sub = mUI.MelMenuItem(_menu, subMenu = True,tearOff=True,
                            label = s,
                            en=True,)
            
            if s == 'Set Side':
                for i,side in enumerate(['none','left','right','center']):
                    mUI.MelMenuItem(_sub,
                                    l = side,
                                    ann='Set contextual block side to: {0}'.format(side),
                                    c = cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                                        'atUtils','set_side',side,
                                                        **{}))                
                
            if s == 'Set Position':
                for i,position in enumerate(BLOCKSHARE._l_positions):
                    mUI.MelMenuItem(_sub,
                                    label = position,
                                    ann = 'Specify the position for the current block to : {0}'.format(position),
                                    c = cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                                        'atUtils','set_position',position,
                                                        **{}))             
            
            l_keys2 = d.get('order',False)
            if l_keys2:
                for k in list(d.keys()):
                    if k not in l_keys2:
                        l_keys2.append(k)
            else:
                l_keys2 = sorted(d)
            for l in l_keys2:
                if l in ['divTags','headerTags','order']:
                    continue
                if l in divTags:
                    mUI.MelMenuItemDiv(_sub)                
                if l in headerTags:
                    mUI.MelMenuItem(_sub,divider = True,
                                    label = l,
                                    en=False)
                    """
                    mUI.MelMenuItemDiv(_sub)
                    mUI.MelMenuItem(_sub,
                                    label = "--- {0} ---".format(l.upper()),
                                    en=False)
                    mUI.MelMenuItemDiv(_sub)"""
                    continue
                d2 = d[l]
                mUI.MelMenuItem(_sub,
                                label = l,
                                ann = d2.get('ann',''),
                                c=d2.get('call'))
                
            if s == 'Rig':
                mUI.MelMenuItemDiv(_menu)
                
                
            if s == 'Blockdat':
                for state in ['define','form','prerig','skeleton',]:
                    mUI.MelMenuItem(_sub,
                                    l = state.capitalize(),
                                    ut = 'cgmUITemplate',
                                    c = cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                                        'atUtils','blockDat_load_state',state,
                                                        **{'updateUI':0}),
                                    ann = "Load {0} blockDat in context".format(state))                



        log.info("Context menu rebuilt")        
        
    def buildMenu_multiset(self,force=True, *args,**kws):
        _str_func = 'buildMenu_multiset'
        if self.uiMenu_multiset and force is not True:
            log.debug("No load...")
            return
        
        self.uiMenu_multiset.clear()   
        _menu = self.uiMenu_multiset
        
        self._d_attrFields = {}
        self.d_multiSet_d = {}
        self.d_multiSet_types = {}
        
        _d, _dTypes = BUILDERUTILS.uiQuery_getAttrDict() or False
        if not _d:
            return
        
        self.d_multiSet_d = _d
        self.d_multiSet_types = _dTypes        

        _states = sorted(_d)
        
        for state in _states:
            if state in ['profile', 'advanced', 'data', 'wiring', 'vis']:
                continue
            
            keys = _d[state]
            _sub = mUI.MelMenuItem(_menu, subMenu = True,tearOff=True,
                        label = state, en=True,)
            for k in keys:
                if k in ['baseSizeX','baseSizeY','baseSizeZ','loftList','rollCount']:
                    continue
                
                _type = _dTypes.get(k)
                if issubclass(list,type(_type)):
                    _sub2 = mUI.MelMenuItem(_sub, label = k, en=True,subMenu=True)                    
                    for o in _type:
                        mUI.MelMenuItem(_sub2, label = o, en=True,
                                        command = cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                                                  'multiset',
                                                                  **{'aType':_type,'attr':k, 'value':o}))    
                elif _type == 'bool':
                    _sub2 = mUI.MelMenuItem(_sub, label = k, en=True,subMenu=True)                    
                    for o in [False,True]:
                        mUI.MelMenuItem(_sub2, label = o, en=True,
                                        command = cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                                        'multiset',
                                                        **{'aType':_type,'attr':k, 'value':o}))                    
                else:
                    mUI.MelMenuItem(_sub, label = k, en=True,
                                    command = cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                                    'multiset',
                                                    **{'aType':_type,'attr':k}))
                    
                  
                    
        return       
            
            
    def buildMenu_vis(self,*args,**kws):
        self.uiMenu_vis.clear()   
        _menu = self.uiMenu_vis
        
        d_s = {'Focus':{'Clear':{'ann':self._d_ui_annotations.get('focus clear'),
                                 'call':cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                        'focus',False,None,
                                        **{'updateUI':0})},
                        'Vis':{'ann':self._d_ui_annotations.get('focus vis'),
                               'call':cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                      'focus',True,'vis',
                                      **{'updateUI':0})},
                        'Template':{'ann':self._d_ui_annotations.get('focus template'),
                                    'call':cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                           'focus',True,'template',
                                           **{'updateUI':0})},},
                   }
        
        l_keys = list(d_s.keys())
        l_keys.sort()
                
        for s in l_keys:
            d = d_s[s]
            divTags = d.get('divTags',[])
            headerTags = d.get('headerTags',[])
            
                
            _sub = mUI.MelMenuItem(_menu, subMenu = True,tearOff=True,
                            label = s,
                            en=True,)

            l_keys2 = d.get('order',False)
            if l_keys2:
                for k in list(d.keys()):
                    if k not in l_keys2:
                        l_keys2.append(k)
            else:
                l_keys2 = sorted(d)
                
            for l in l_keys2:
                if l in ['divTags','headerTags','order']:
                    continue
                if l in divTags:
                    mUI.MelMenuItemDiv(_sub)                
                if l in headerTags:
                    mUI.MelMenuItemDiv(_sub)
                    mUI.MelMenuItem(_sub,
                                    label = "--- {0} ---".format(l.upper()),
                                    en=False)
                    mUI.MelMenuItemDiv(_sub)
                    continue
                d2 = d[l]
                mUI.MelMenuItem(_sub,
                                label = l,
                                ann = d2.get('ann',''),
                                c=d2.get('call'))

        #Vis menu -----------------------------------------------------------------------------
        for a in ['Measure','RotatePlane','JointHandle','Labels','ProximityMode','FormMesh','FormHandles']:
            _sub = mUI.MelMenuItem(_menu, subMenu = True,tearOff=False,
                                   label = a,
                                   en=True,)
            if a == 'ProximityMode':
                _l = ['off','inherit','proximity']
            elif a == 'FormMesh':
                _l = ['reg','template']
            else:
                _l = ['off','on']
                
            for i,v in enumerate(_l):
                if a =='FormMesh':
                    mUI.MelMenuItem(_sub,
                                    l = v,
                                    ann='Set visibility of: {0} | {1}'.format(a,v),
                                    c = cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                                'atUtils', 'form_templateMesh',
                                                **{'arg':i}))                    
                else:
                    
                    mUI.MelMenuItem(_sub,
                                    l = v,
                                    ann='Set visibility of: {0} | {1}'.format(a,v),
                                    c = cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                                'atUtils', 'blockAttr_set',
                                                **{"vis{0}".format(a):i}))
                    
                
                
        d_shared = {'formNull':{},
                    'prerigNull':{}}
        
        l_settings = ['visibility']
        l_locks = ['rigBlock','formNull','prerigNull']
        l_enums = []
    
        for n in l_locks:
            _sub = mUI.MelMenuItem(_menu, subMenu = True,tearOff=False,
                                   label = n,
                                   en=True,)
            
    
            if n in l_settings:
                l_options = ['hide','show']
                _mode = 'moduleSettings'
            elif n in l_locks:
                l_options = ['unlock','lock']
                _mode = 'moduleSettings'
                if n != 'rigBlock':
                    _plug = d_shared[n].get('plug',n)
            else:
                l_options = ['off','lock','on']
                _mode = 'puppetSettings'
                
            for v,o in enumerate(l_options):
                if n == 'rigBlock':
                    mUI.MelMenuItem(_sub,
                                    l = o,
                                    ann='Set visibility of: {0} | {1}'.format(a,v),
                                    c = cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                                'atUtils','templateAttrLock',v))
                         
  
                else:
                    mUI.MelMenuItem(_sub,
                                    l = o,
                                    ann='Set visibility of: {0} | {1}'.format(a,v),
                                    c = cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                                'atUtils', 'messageConnection_setAttr',
                                                _plug,**{'template':v}))                    


        
            for n in l_settings:
                l_options = ['hide','show']
    
                for v,o in enumerate(l_options):
                    mUI.MelMenuItem(_sub,
                                    l = o,
                                    ann='Set visibility of: {0} | {1}'.format(a,v),
                                    c=cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                                'atUtils', 'blockAttr_set',
                                                **{n:v}))                    

        log.info("Context menu rebuilt")        
        
    def batch_call(self):
        ml_masters = r9Meta.getMetaNodes(mTypes = 'cgmRigBlock',
                                         nTypes=['transform','network'],
                                         mAttrs='blockType=master')
        
        l_fails = []
        ml_fails = []
        for mMaster in ml_masters:    
            ml_context = BLOCKGEN.get_rigBlock_heirarchy_context(mMaster,'below',True,False)
    
            for mSubBlock in ml_context:
                l_fails.append(mSubBlock.asRigFactory(**{'mode':'prechecks'}).b_prechecks)
                if not l_fails[-1]: ml_fails.append(mSubBlock)
        
        if False in l_fails:
            #self.uiScrollList_blocks.selectByObj(ml_fails[0])
            return (log.warning("Prechecks failed. Check script editor!"))
        
        log.info("Batch file creating...")
    
        import cgm.core.mrs.lib.batch_utils as MRSBATCH
        #cgmGEN._reloadMod(MRSBATCH)
        
        MRSBATCH.create_MRS_batchFile(process=True)
        
    def buildMenu_advanced(self,*args,**kws):
        self.uiMenu_advanced.clear()   
        _menu = self.uiMenu_advanced
        d_s = {'Batch':{'Send File To MayaPy':{'ann':"Process the current file. Will be saved at it's current location as _ BUILD.ext",
                                            'call':cgmGEN.Callback(ui_toStandAlone),},
                        'Old Method':{'ann':"Process the current file. Will be saved at it's current location as _ BUILD.ext",'call':cgmGEN.Callback(self.batch_call),}},
               'Utilities':{
                   'Verify':{'ann':'Check if the block is current (DEV)',
                             'call':cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                                     'verify',
                                                     **{'updateUI':0})},
                   'Root Shape | Update':{'ann':'Update the rootShapes of the blocks in context',
                             'call':cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                                     'atUtils','rootShape_update',
                                                     **{'updateUI':0})},                   
                   'Block Current?':{'ann':'Check if the block is current (DEV)',
                                'call':cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                                       'atUtils','is_current',
                                                       **{'updateUI':0})},
                  'Block Update':{'ann':'[DEV] Update a block. In testing',
                                    'call':cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                                           'atUtils','update',
                                                           **{'updateUI':1,'reverseContext':False})},
                  'Block Rebuild':{'ann':'[DEV] Rebuild a block. In testing',
                                                      'call':cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                                                             'atUtils','rebuild',
                                                                            **{'updateUI':1,'reverseContext':False})},
                  'blockModule | debug':{'ann':'Set the blockModule to debug',
                                  'call':cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                                         'atUtils','blockModule_setLogger',
                                                         **{'updateUI':0,})},
                  'blockModule | info':{'ann':'Set the blockModule to info',
                                  'call':cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                                         'atUtils','blockModule_setLogger','info',
                                                         **{'updateUI':0,})},
                  'blockProfile | update':{'ann':'Check if blockProfile setting is valid, then force update',
                                         'call':cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                                              'atUtils','blockProfile_valid',
                                                              **{'updateUI':0,'update':True})},
                  'Joint Labels | wire':{'ann':'Wire jointLabels to block vis',
                                         'call':cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                                              'atUtils','connect_jointLabels',
                                                              **{'updateUI':0})},                  
                  'Reorder UD':{'ann':'Reorder user defined attrs',
                                'call':cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                                       'atUtils','reorder_udAttrs',
                                                       **{'updateUI':0})}},
               
               'Define':{'Load base size dat':{'ann':'Reset define dat to base',
                                            'call':cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                                                   'atUtils', 'define_set_baseSize',
                                                                   **{'updateUI':0})}},

               'Prerig':{
                   'Query Indices':{'call':cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                                           'atBlockModule', 'get_handleIndices',
                                                           **{'updateUI':0})}},                                      
               
               'blockFrame':{'Align To':{'ann':self._d_ui_annotations.get('blockframealignto'),
                                         'call':cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                                'atUtils','blockFrame_alignTo',False,
                                                **{'updateUI':0})},
                        'Shape To':{'ann':self._d_ui_annotations.get('blockframeshapeto'),
                                    'call':cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                           'atUtils','blockFrame_alignTo',True,
                                           **{'updateUI':0})}},
               
               'Form':{
                   'Resize Handles':{'call':cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                                           'atUtils', 'blockDat_load_state','form',
                                                           **{'updateUI':0,'overrideMode':'useLoft'})}},



               'Queries':{
                   'Visualize':{'ann':'Visualize the block tree in the script editor',
                                'call':cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                                       'VISUALIZEHEIRARCHY',
                                                       **{'updateUI':0})},
                  'Buildable?':{'ann':'Check if the block is buildable (DEV)',
                                'call':cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                                       'getModuleStatus',
                                                       **{'updateUI':0})},
                  'Get Missing Attr Mask':{'ann':'Get missing attrs for the attrMask',
                                               'call':cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                                                    'atUtils','uiQuery_getStateAttrDict',
                                                                    **{'updateUI':0})},
                  'Find orphaned rigModules':{'ann':'Get missing attrs for the attrMask',
                                              'call':cgmGEN.Callback(BLOCKGEN.get_orphanedRigModules,
                                                                    **{'select':1})},                  
                  
                  
                  'blockProfile Valid?':{'ann':'Check if blockProfile setting is valid',
                                               'call':cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                                                    'atUtils','blockProfile_valid',
                                                                    **{'updateUI':0})}},

               'attrMask':{
                   'order':['Define','Form','Prerig','Skeleton','Rig','Clear',
                            ],
                   'divTags':['Clear'],                   
                   'Define':{'ann':'Set attrMask to define',
                            'call':cgmGEN.CB(self.uiFunc_contextBlockCall,
                                             'atUtils','attrMask_set',
                                             **{'mode':0,'updateUI':0})},
                   'Form':{'ann':'Set attrMask to form',
                             'call':cgmGEN.CB(self.uiFunc_contextBlockCall,
                                              'atUtils','attrMask_set',
                                              **{'mode':1,'updateUI':0})},
                   'Prerig':{'ann':'Set attrMask to prerig',
                             'call':cgmGEN.CB(self.uiFunc_contextBlockCall,
                                              'atUtils','attrMask_set',
                                              **{'mode':2,'updateUI':0})},
                   'Skeleton':{'ann':'Set attrMask to skeleton',
                             'call':cgmGEN.CB(self.uiFunc_contextBlockCall,
                                              'atUtils','attrMask_set',
                                              **{'mode':3,'updateUI':0})},
                   'Rig':{'ann':'Set attrMask to rig',
                             'call':cgmGEN.CB(self.uiFunc_contextBlockCall,
                                              'atUtils','attrMask_set',
                                              **{'mode':4,'updateUI':0})},
                   'Clear':{'ann':'Clear the attrMask',
                            'call':cgmGEN.CB(self.uiFunc_contextBlockCall,
                                             'atUtils','attrMask_set',
                                             **{'clear':1,'updateUI':0})}},
               
               'Mirror':{ 
                   'divTags':['Settings | Pull'],
                   'Controls | Push':{'ann':'Mirror block controls in context | push',
                                      'call':cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                                                'atUtils','blockMirror_go',
                                                                **{'updateUI':True,'mode':'push'})},
                  'Controls | Pull':{'ann':'Mirror block controls in context | pull',
                                      'call':cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                                                'atUtils','blockMirror_go',
                                                                **{'updateUI':True,'mode':'pull'})},
                  'Settings | Push':{'ann':'Mirror block controls in context | push',
                                     'call':cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                                               'atUtils','blockMirror_settings',
                                                               **{'updateUI':True,'mode':'push'})},
                 'Settings | Pull':{'ann':'Mirror block controls in context | pull',
                                     'call':cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                                               'atUtils','blockMirror_settings',
                                                               **{'updateUI':True,'mode':'pull'})},                  
                 }}
        
        
        l_keys = sorted(d_s)
        l_check = ['Define','Form','Prerig','Skeleton','Rig']
        l_check.reverse()
        for k in l_check:
            if k in l_keys:
                l_keys.remove(k)
                l_keys.insert(0,k)        
        

        for s in l_keys:
            d = d_s[s]
            divTags = d.get('divTags',[])
            headerTags = d.get('headerTags',[])
            
                
            _sub = mUI.MelMenuItem(_menu, subMenu = True,tearOff=True,
                            label = s,
                            en=True,)
            
            if s == 'Set Side':
                for i,side in enumerate(['none','left','right','center']):
                    mUI.MelMenuItem(_sub,
                                    l = side,
                                    ann='Set contextual block side to: {0}'.format(side),
                                    c = cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                                        'atUtils','set_side',side,
                                                        **{}))                
                
                continue
            
            l_keys2 = d.get('order',False)
            if l_keys2:
                for k in list(d.keys()):
                    if k not in l_keys2:
                        l_keys2.append(k)
            else:
                l_keys2 = sorted(d)
            for l in l_keys2:
                if l in ['divTags','headerTags','order']:
                    continue
                if l in divTags:
                    mUI.MelMenuItemDiv(_sub)                
                if l in headerTags:
                    #mUI.MelMenuItemDiv(_sub)
                    mUI.MelMenuItem(_sub,divider = True,
                                    label = "{0}".format(l.upper()),
                                    en=True)
                    #mUI.MelMenuItemDiv(_sub)
                    continue
                d2 = d[l]
                mUI.MelMenuItem(_sub,
                                label = l,
                                ann = d2.get('ann',''),
                                c=d2.get('call'))

            if s == 'Prerig':
                mUI.MelMenuItemDiv(_menu)                       

    def buildMenu_snap( self, force=False, *args, **kws):
        if self.uiMenu_snap and force is not True:
            return
        self.uiMenu_snap.clear()
        
        UICHUNKS.uiSection_snap(self.uiMenu_snap)
            
        mUI.MelMenuItemDiv(self.uiMenu_snap)
        
        mUI.MelMenuItem(self.uiMenu_snap, l='Rebuild',
                        c=cgmGEN.Callback(self.buildMenu_snap,True))
        log.info("Snap menu rebuilt")
        
    #def buildMenu_help(self):
        #self.uiMenu_Help.clear()
        
        #cgmUI.uiSection_help(self.uiMenu_Help)
        
    class uiCallback(object):
        '''
        By Hamish McKenzie
        stupid little callable object for when you need to "bake" temporary args into a
        callback - useful mainly when creating callbacks for dynamicly generated UI items
        '''
        def __init__( self, ui, func, *a, **kw ):
            self._ui = ui
            self._func = func
            self._args = a
            self._kwargs = kw
        def __call__( self, *args ):
            self._ui.uiRow_progress(edit=1,vis=1)
            cgmUI.progressBar_start(self._ui.uiPB_mrs)
            self._ui.uiProgressText(edit=True,vis=1,
                                    label="{0} ".format(self._func.__name__))

            try:return self._func( *self._args, **self._kwargs )
            except Exception as err:
                try:log.info("Func: {0}".format(self._func.__name__))
                except:log.info("Func: {0}".format(self._func))
                if self._args:
                    log.info("args: {0}".format(self._args))
                if self._kwargs:
                    log.info("kws: {0}".format(self._kwargs))
                for a in err.args:
                    log.info(a)
                    
                cgmGEN.cgmExceptCB(Exception,err)
                raise err 
            finally:
                self._ui.uiRow_progress(edit=1,vis=0)
                self._ui.uiProgressText(edit=True,label='...')
                cgmUI.progressBar_end(self._ui.uiPB_mrs)
                
    def buildMenu_add( self, force=True, *args, **kws):
        if self.uiMenu_add and force is not True:
            log.debug("No load...")
            return
        
        self.uiMenu_add.clear()
        
        mUI.MelMenuItem(self.uiMenu_add, label = 'Create UI', 
                        c = lambda *a:ui_createBlock())
        
        
        mUI.MelMenuItemDiv(self.uiMenu_add, label = 'Old')
        
        if force:
            self._d_modules = RIGBLOCKS.get_modules_dat(True)#...refresh data
        
        _d = copy.copy(self._d_modules)
        for b in _d[1]['blocks']:
            if _d[0][b].__dict__.get('__menuVisible__'):
                mUI.MelMenuItem(self.uiMenu_add, l=b,
                                c=cgmGEN.Callback(self.uiFunc_block_create,b),
                                ann="{0} : {1}".format(b, self.uiFunc_block_create))
                
                l_options = RIGBLOCKS.get_blockProfile_options(b)                
                if l_options:
                    for o in l_options:
                        mUI.MelMenuItem(self.uiMenu_add, l=o,
                                        c=cgmGEN.Callback(self.uiFunc_block_create,b,o),
                                        ann="{0} : {1}".format(b, self.uiFunc_block_create))

        
        for c in list(_d[1].keys()):
            #d_sections[c] = []
            if c == 'blocks':continue
            for b in _d[1][c]:
                if _d[0][b].__dict__.get('__menuVisible__'):
                    #d_sections[c].append( [b,cgmGEN.Callback(self.uiFunc_block_create,b)] )
                    l_options = RIGBLOCKS.get_blockProfile_options(b)
                    if l_options:
                        _sub = mUI.MelMenuItem( self.uiMenu_add, subMenu=True,l=b,tearOff=True)
                        l_options.sort()
                        for o in l_options:
                            _l = "{0}".format(o)
                            _c = cgmGEN.Callback(self.uiFunc_block_create,b,o)
                            mUI.MelMenuItem(_sub, l=_l,
                                            c=_c,
                                            ann="{0} : {1}".format(_l, _c)
                                            )
                    else:
                        mUI.MelMenuItem(self.uiMenu_add, l=b,
                                        c=cgmGEN.Callback(self.uiFunc_block_create,b,'default'),
                                        ann="{0} : {1}".format(b, self.uiFunc_block_create))


        mUI.MelMenuItemDiv(self.uiMenu_add)
        uiOptionMenu_blockSizeMode(self, self.uiMenu_add)        
        mUI.MelMenuItem(self.uiMenu_add, l='Rebuild',
                        c=lambda *a: mc.evalDeferred(self.buildMenu_add,lp=True))
        log.info("Add menu rebuilt")


    def uiFunc_block_create(self, blockType = None, blockProfile = None):
        _str_func = 'uiFunc_block_create'
        
        #index = _indices[0]
        #_mBlock = self._ml_blocks[_index]
        _sel = mc.ls(sl=1) or []
        
        mActiveBlock = None
        side = None
        if blockType in ['limb']:
            side = 'right'
            
        if self._blockCurrent:
            mActiveBlock = self._blockCurrent.mNode
            #side = self._blockCurrent.UTILS.get_side(self._blockCurrent)
        _sizeMode = self.var_rigBlockCreateSizeMode.value
        if _sizeMode == 'selection' and not mc.ls(sl=True):
            #if blockType not in ['master']:
                #log.info("|{0}| >> Must have selection for size mode: {1}.".format(_str_func,_sizeMode))        
                #return False
            _sizeMode = None
        
        _mBlock = cgmMeta.createMetaNode('cgmRigBlock',blockType = blockType, 
                                         size = _sizeMode,
                                         blockParent = mActiveBlock,
                                         side = side,
                                         buildProfile = self.var_buildProfile.value,
                                         blockProfile = blockProfile)
        
        log.info("|{0}| >> [{1}] | Created: {2}.".format(_str_func,blockType,_mBlock.mNode))       
         
        #self.uiUpdate_scrollList_full()
        #self.uiFunc_block_setActive(self._ml_blocks.index(_mBlock))
        
        self.uiScrollList_blocks.rebuild()
        self.uiScrollList_blocks.selectByObj(_mBlock)
        
        #if  not self.var_mrsDevMode.value:
        #    _mBlock.atUtils('attrMask_set',mode=None)        
        
        if _sel:
            mc.select(_sel)
        else:
            _mBlock.select()
        
    def uiFunc_block_mirror_create(self, mBlock = None, forceNew = False):
        _str_func = 'uiFunc_block_mirror_create'
        
        #index = _indices[0]
        #_mBlock = self._ml_blocks[_index]
        mActiveBlock = None
        if self._blockCurrent:
            mActiveBlock = self._blockCurrent.mNode
            

        mMirror = mBlock.atBlockUtils('blockMirror_create',forceNew)
        
        if not mMirror:
            return False
        log.info("|{0}| >> mMirror: {1}.".format(_str_func,mMirror.mNode))        
        
        """
        self.uiUpdate_scrollList_full()
        _idx = self._ml_blocks.index(mMirror)
        
        self.uiFunc_block_setActive(_idx)
        self.uiScrollList_blocks.selectByIdx(_idx)"""
        
    def uiFunc_activeBlockCall(self,func,*args,**kws):          
        _str_func = 'uiFunc_activeBlockCall'
                                         
        if not self._ml_blocks:
            return log.error("|{0}| >> No blocks detected".format(_str_func))

        _mActiveBlock = self._blockCurrent
        _str_activeBlock = False
        if _mActiveBlock:
            _str_activeBlock = _mActiveBlock.mNode
        else:
            return log.error("|{0}| >> No active block detected".format(_str_func))
        return getattr(_mActiveBlock,func)(*args,**kws)
        
    def uiFunc_blockManange_fromScrollList(self,**kws):
        try:
            _str_func = 'uiFunc_blockManange_fromScrollList'
            
            _mode = kws.get('mode',None)
            _fromPrompt = None

            try:_mBlock = self.uiScrollList_blocks.getSelectedObjs()[0]
            except Exception as err:
                print(err)                                                        
                return log.error("|{0}| >> Failed to get _mBlock".format(_str_func))
            log.info(_mBlock)
            
            _mActiveBlock = self._blockCurrent
            _str_activeBlock = False
            if _mActiveBlock:
                _str_activeBlock = _mActiveBlock.mNode    
        
            _done = False    
            if _mode is not None:
                log.debug("|{0}| >> mode: {1}".format(_str_func,_mode)) 
                if _mode == 'setParentToActive':
                    if not _mActiveBlock:
                        log.error("|{0}| >> mode: {1} requires active block".format(_str_func,_mode)) 
                        return
                    _mBlock.p_blockParent = _mActiveBlock
                elif _mode == 'setParentToSelected':
                    mParent = BLOCKGEN.block_getFromSelected()
                    if mParent:
                        _mBlock.p_blockParent = mParent
                    return
                elif  _mode == 'clearParentBlock':
                    _mBlock.p_blockParent = False
                elif _mode == 'toScriptEditor':
                    _mBlock.atUtils('to_scriptEditor')
                elif _mode == 'toScriptEditorRigFactory':
                    _mBlock.atUtils('to_scriptEditor','rigFactory')
                else:
                    raise ValueError("Mode not setup: {0}".format(_mode))
                
            self.uiScrollList_blocks.rebuild()
            #mc.evalDeferred('self.uiScrollList_blocks.rebuild()',lp=True)
        except Exception as err:
            cgmGEN.cgmException(Exception,err)

    #@cgmGEN.Timer
    def uiFunc_contextBlockCall(self,*args,**kws):
        try:
            mc.refresh(su=1)
            _sel = mc.ls(sl=1)
                
            def confirm(title,message,funcString):
                result = mc.confirmDialog(title=title,
                                          message= message,
                                          button=['OK', 'Cancel'],
                                          defaultButton='OK',
                                          cancelButton='Cancel',
                                          dismissString='Cancel')
        
                if result != 'OK':
                    log.error("|{0}| >> Cancelled | {1}.".format(_str_func,funcString))
                    return False
                return True
            
            
            _str_func = ''
            log.info(cgmGEN._str_hardBreak)
            _updateUI = kws.pop('updateUI',True)
            _reverseContext = kws.pop('reverseContext',False)
            _startMode = self.var_contextStartMode.value   
            _contextMode = kws.pop('contextMode', self._l_contextModes[self.var_contextMode.value])
            _b_confirm = False
            _selectRes = kws.pop('selectResult',False)
            
            
            #_contextMode = self._l_contextModes[self.var_contextMode.value]
            log.debug("|{0}| >> Update ui: {1}".format(_str_func,_updateUI))
            _mode = kws.get('mode')
            ml_blocks = []
            _mActiveBlock = self._blockCurrent
            
            
            if _mode == 'setParentToActive':
                if not _mActiveBlock:
                    log.error("|{0}| >> mode: {1} requires active block".format(_str_func,_mode)) 
                    return
                kws['parent'] = _mActiveBlock
                kws.pop('mode')
            elif _mode == 'setParentToSelected':
                mSelectedBlock = BLOCKGEN.block_getFromSelected()
                if not mSelectedBlock:
                    return log.error("|{0}| >> mode: {1} requires selected block".format(_str_func,_mode)) 
                kws['parent'] = mSelectedBlock
                kws.pop('mode')
            elif _mode == 'blockDatCopyActive':
                if not _mActiveBlock:
                    log.error("|{0}| >> mode: {1} requires active block".format(_str_func,_mode)) 
                    return
                kws['sourceBlock'] = _mActiveBlock
                kws.pop('mode')
            elif _mode == 'noSelect':
                mc.select(clear=1)
                kws.pop('mode')
                
                
            if _sel or _selectRes:
                mc.select(cl=1)
                
            #elif  _mode == 'clearParentBlock':
            #else:
                #raise ValueError,"Mode not setup: {0}".format(_mode)            
            b_devMode = False
            b_dupMode = False
            b_changeState = False
            b_rootMode = False
            if args[0] == 'changeState':
                b_changeState = True
                b_devMode = self.var_mrsDevMode.value
                if _contextMode in ['scene']:
                    log.warning("|{0}| >> Change state cannot be run in any mode but self. Changing context.".format(_str_func))
                elif _contextMode == 'root':
                    b_rootMode = True
                
                if _contextMode == 'self':
                    kws['forceNew'] = True
                    kws['checkDependency'] = True
                else:
                    kws['forceNew'] = self.var_contextForceMode.value
            elif args[0] == 'stepUI':
                _contextMode = 'self'
            elif args[0] == 'duplicate':
                if _contextMode in ['below','root','scene']:
                    b_dupMode = True
            
            try:
                if args[1] in ['puppetMesh_create','puppetMesh_delete','skeleton_getReport']:
                    _contextMode = 'self'
                    log.error("|{0}| >> Self context: {}".format(_str_func,args[1] ))
            except:pass
            
            if _contextMode != 'self':
                if b_changeState:
                    _b_confirm = True
                    _funcString = 'changeState'
                    log.debug("|{0}| >> Change state and not self... | {1}".format(_str_func,_contextMode)) 
                    _title = 'Confirm non self state rig change...'
                    _message = '{0} | This is a long process with lots of blocks'.format(_funcString)
                    _text = _contextMode
                    

            if _startMode == 0 :#Active
                log.debug("|{0}| >> Active start".format(_str_func))                
                mBlock = self._blockCurrent
                
                if not mBlock:
                    log.error("|{0}| >> No Active block".format(_str_func))
                    return False
                
                if _b_confirm:
                    if not confirm(_title, _message, _funcString):return False                
                
                if b_rootMode:
                    mRoot = mBlock.getBlockRoot()
                    if mRoot:
                        mBlock = mRoot
                    else:
                        mBlock = mBlock.getBlockRoot()
                    
                ml_blocks = [mBlock]
                #RIGBLOCKS.contextual_rigBlock_method_call(mBlock,_contextMode,*args,**kws)
                
                #if _updateUI:
                    #self.uiUpdate_scrollList_blocks(mBlock)
                    #self.uiUpdate_blockDat()
                
            else:
                log.debug("|{0}| >> start: {1}".format(_str_func,_startMode))
                ml_blocks = self.uiScrollList_blocks.getSelectedObjs()
                if not ml_blocks:
                    #log.error("|{0}| >> Failed to query indices: {1}".format(_str_func))
                    return False
                
            if args[0] == 'VISUALIZEHEIRARCHY':
                BLOCKGEN.get_rigBlock_heirarchy_context(ml_blocks[0],_contextMode,False,True)
                return True
                
            
            try:
                if args[1] == 'skeleton' and _contextMode in ['self']:
                    log.warning(cgmGEN.logString_msg(_str_func,"Changing context to below. Self | Skeleton"))
                    _contextMode = 'below'
            except:pass
                
            ml_context = BLOCKGEN.get_rigBlock_heirarchy_context(ml_blocks,_contextMode,True,False)
            
            _len = len(ml_context)
            if _b_confirm and _len>8:
                _message = "{0} \n Selected: {1}".format(_message,len(ml_context))
                if not confirm(_title, _message, _funcString):return False            
            
            if _reverseContext:
                log.warning(cgmGEN.logString_msg(_str_func,'REVERSE CONTEXT MODE ON'))
                
                ml_context.reverse()
            #Now parse to sets of data
            if args[0] == 'stepUI':
                return ui_stepBuild(ml_blocks[0])
            elif args[0] == 'blockEdit':
                return blockEditor_get(ml_blocks[0])
            elif args[0] == 'blockPicker':
                return blockPicker_get(ml_blocks[0])
            elif args[0] == 'select':
                #log.info('select...')
                return mc.select([mBlock.mNode for mBlock in ml_context])
            elif args[0] == 'saveShapeDat':
                CGMDAT.batch(ml_context, MRSDAT.ShapeDat ).write(startDirMode = self._l_startDirModes[self.var_startDirMode.value])
                return
            elif args[0] == 'exportBlockDat':
                CGMDAT.batch(ml_context, MRSDAT.BlockDat ).write(startDirMode = self._l_startDirModes[self.var_startDirMode.value])
                return            
            elif args[0]== 'focus':
                log.debug("|{0}| >> Focus call | {1}".format(_str_func,_contextMode))
                #ml_root = BLOCKGEN.get_rigBlock_heirarchy_context(ml_blocks,'root',True,False)
                for mBlock in ml_blocks:
                    log.info("|{0}| >> Focus call | {1}".format(_str_func,mBlock))                    
                    mBlock.UTILS.focus(mBlock,args[1],args[2],ml_focus=ml_blocks)
                return
            elif args[0] == 'multiset':
                BUILDERUTILS.multiset( ml_context, **kws)
                return
            
            ml_context = LISTS.get_noDuplicates(ml_context)
            int_len = len(ml_context)
            self.uiRow_progress(edit=1,vis=True,m=True)                
            self.uiProgressText(edit=True,vis=True,label="Processing...")
            mc.progressBar(self.uiPB_mrs,edit=True,vis=True)
            #cgmUI.progressBar_test(self.uiPB_mrs,5,.001)
            
            i_add = 0
            if int_len == 1:
                i_add = 1
                
            ml_res = []
            md_dat = {}
            md_datRev = {}
            
            for i,mBlock in enumerate(ml_context):
                _short = mBlock.p_nameShort
                _call = str(args[0])
                if _call in ['atUtils']:
                    _call = str(args[1])
                    
                self.uiProgressText(edit=True,label="{0}/{1} | {2} | call: {3}".format(i+1,int_len,
                                                                             _short,_call))
                mc.progressBar(self.uiPB_mrs,edit=True,maxValue = int_len,progress = i, vis=1)
                #cgmUI.progressBar_set(self.uiPB_mrs,
                #                      maxValue = int_len+1,
                #                      progress=i+i_add, vis=True)
                log.debug("|{0}| >> Processing: {1}".format(_str_func,mBlock)+'-'*40)
                res = getattr(mBlock,args[0])(*args[1:],**kws) or None
                if VALID.isListArg(res):
                    ml_res.extend(res)
                else:
                    ml_res.append(res)
                    
                if res:
                    if _call == 'rebuild':
                        mBlock = res
                        
                    try:log.debug("[{0}] ...".format(mBlock.p_nameShort,res))
                    except:pass
                    if kws.get('mode') not in ['prechecks']:
                        pprint.pprint(res)
                        
                if b_dupMode:
                    md_dat[res] = mBlock
                    md_datRev[mBlock] = res
                
                #if b_changeState and not b_devMode:
                #    mBlock.atUtils('attrMask_set',mode=None)
                    
            #if _mActiveBlock and b_changeState:
                #self.uiUpdate_blockDat()
            if _selectRes:
                try:mc.select([mObj.mNode for mObj in ml_res])
                except:pass
                
            if b_dupMode and len(ml_res) > 1:
                log.info(cgmGEN.logString_msg(_str_func,"mDup post process..."))
                #pprint.pprint(md_datRev)
                #pprint.pprint(md_dat)
                
                for mDup in ml_res[1:]:
                    log.info(cgmGEN.logString_sub(_str_func,"mDup | {0}".format(mDup)))                    
                    mBlock = md_dat[mDup]
                    mParent = mBlock.p_blockParent
                    if mParent:
                        log.info(cgmGEN.logString_msg(_str_func,"mParent | {0}".format(mParent)))
                        mTargetParent = md_datRev.get(mParent,mParent)
                        mDup.p_blockParent = mTargetParent
                        log.info(cgmGEN.logString_msg(_str_func,"mTargetParent | {0}".format(mTargetParent)))
                        

                
            if _updateUI:
                self.uiScrollList_blocks.rebuild()
                
            if args[0] not in ['delete'] and _startMode != 0:
                #ml_processed.extend(BLOCKGEN.get_rigBlock_heirarchy_context(mBlock,_contextMode,True,False))
                #self.uiScrollList_blocks.selectByIdx(_indices[0])                
                pass
            if _sel and args:
                try:
                    if args[1] not in ['skeleton_getBind'] and _selectRes not in [1,True]:
                        mc.select(_sel)
                except:pass
            return ml_context
                
        #except Exception,err:
        #    cgmGEN.cgmExceptCB(Exception,err)
        finally:
            self.uiRow_progress(edit=1,vis=False)
            self.uiProgressText(edit=True,label='...')
            mc.refresh(su=0)
            
            #cgmUI.progressBar_end(self.uiPB_mrs)
    @cgmGEN.Timer
    def uiFunc_contextModuleCall(self,*args,**kws):
        try:
            _str_func = ''
            _updateUI = kws.pop('updateUI',True)
            _startMode = self.var_contextStartMode.value   
            _contextMode = self._l_contextModes[self.var_contextMode.value]
            ml_blocks = []
            mc.refresh(su=1)
            
            if _startMode == 0 :#Active
                mBlock = self._blockCurrent
                
                if not mBlock:
                    log.error("|{0}| >> No Active block".format(_str_func))
                    return False
                ml_blocks = [mBlock]
                
            else:
                ml_blocks = self.uiScrollList_blocks.getSelectedObjs()
                    
                if not ml_blocks:
                    log.error("|{0}| >> Failed to query indices: {1}".format(_str_func,_indices))
                    return False                
                
            self.uiRow_progress(edit=1,vis=1)
            ml_context = BLOCKGEN.get_rigBlock_heirarchy_context(ml_blocks,_contextMode,True,False)
            #pprint.pprint(ml_context)
            #Now parse to sets of data
            if args[0] == 'select':
                #log.info('select...')
                return mc.select([mBlock.mNode for mBlock in ml_context])
            
            int_len = len(ml_context)
            for i,mBlock in enumerate(ml_context):
                _short = mBlock.p_nameShort
                _call = str(args[0])
                if _call in ['atUtils']:
                    _call = str(args[1])
                self.uiProgressText(edit=True,vis=1,label="{0}/{1} | {2} | call: {3}".format(i,int_len,_short,_contextMode,_call))
                
                cgmUI.progressBar_start(self.uiPB_mrs,int_len)
                cgmUI.progressBar_set(self.uiPB_mrs,
                                      maxValue = int_len,
                                      progress=i, vis=True)
                
                log.debug("|{0}| >> Processing: {1}".format(_str_func,mBlock)+'-'*40)
                res = RIGBLOCKS.contextual_module_method_call(mBlock,'self',*args,**kws)
                log.debug("|{0}| >> res: {1}".format(_str_func,res))

        finally:
            self.uiRow_progress(edit=1,vis=0)
            self.uiProgressText(edit=True,label='...')
            cgmUI.progressBar_end(self.uiPB_mrs)
            mc.refresh(su=0)
            
    def uiFunc_contextPuppetCall(self,*args,**kws):
        _str_func = ''
        _startMode = self.var_contextStartMode.value   
        
        if _startMode == 0 :#Active
            mBlock = self._blockCurrent
            if not mBlock:
                log.error("|{0}| >> No Active block".format(_str_func))
                return False
        else:
            try:mBlock = self.uiScrollList_blocks.getSelectedObjs()[0]
            except:
                log.error("|{0}| >> Failed to query BLock".format(_str_func))                                                        
                return False
            
        mPuppet = mBlock.atUtils('get_puppet')
        if not mPuppet:
            return log.error("|{0}| >> No puppet found.".format(_str_func,_index))
        
        if args[0] == 'postUI':
            return ui_post(mPuppet)
        return mPuppet.atUtils(*args,**kws)
        
            
            
    def uiFunc_block_select_dcc(self,*args,**kws):
        if self._blockCurrent:
            self._blockCurrent.select()
    
    #@cgmGEN.Timer
    def uiScrollList_block_select(self): 
        try:
            _str_func = 'uiScrollList_block_select'  
            log.debug(cgmGEN.logString_start(_str_func))

            if self.uiPopUpMenu_blocks:
                self.uiPopUpMenu_blocks.clear()
                self.uiPopUpMenu_blocks.delete()
                self.uiPopUpMenu_blocks = None
        
            ml_block = self.uiScrollList_blocks.getSelectedObjs()
            if not ml_block:
                log.warning("|{0}| >> Nothing selected".format(_str_func))
                return False
            
            _mBlock = ml_block[0]
            if _mBlock and not _mBlock.mNode:
                log.warning("|{0}| >> Dead block. Rebuilding blockList".format(_str_func))                
                self.uiScrollList_blocks.rebuild()
                return False
            

                
            self.uiScrollList_blocks.setHLC(_mBlock)

            
            _short = _mBlock.p_nameShort

            _mActiveBlock = self._blockCurrent
            _str_activeBlock = False
            if _mActiveBlock:
                _str_activeBlock = _mActiveBlock.mNode
        
            self.uiPopUpMenu_blocks = mUI.MelPopupMenu(self.uiScrollList_blocks,button = 3)
            _popUp = self.uiPopUpMenu_blocks 
            
            _b_active = False
            if _mActiveBlock:
                _b_active = True
                
            if len(ml_block) > 1:
                #print ml_block
                mUI.MelMenuItem(_popUp,
                                ann = 'Select',
                                c = cgmGEN.Callback( self.uiFunc_contextBlockCall, 'select'),
                                label = "Select")
                
                #...side ----------------------------------------------------------------------------------------
                sub_side = mUI.MelMenuItem(_popUp,subMenu=True,
                                           label = 'Set side')
                
                for i,side in enumerate(['None','left','right','center']):
                    mUI.MelMenuItem(sub_side,
                                    label = side,
                                    ann = 'Specify the side for the current block to : {0}'.format(side),
                                    c = uiCallback_withUpdate(self,_mBlock,_mBlock.atBlockUtils,'set_side',side))
                #...position ------------------------------------------------------------------------------
                #none:upper:lower:front:back:top:bottom
                sub_position = mUI.MelMenuItem(_popUp,subMenu=True,
                                               label = 'Set position')
                for i,position in enumerate(BLOCKSHARE._l_positions):
                    mUI.MelMenuItem(sub_position,
                                    label = position,
                                    ann = 'Specify the position for the current block to : {0}'.format(position),
                                    c = uiCallback_withUpdate(self,_mBlock,_mBlock.atBlockUtils,'set_position',position))                
                
                mUI.MelMenuItem(_popUp,
                                label = 'Delete',
                                c = cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                                    'atBlockUtils','delete',
                                                    **{'updateUI':1}))                  
                mUI.MelMenuItemDiv(_popUp)
                mUI.MelMenuItem(_popUp,
                                label = 'Reload Module',
                                ann = 'Reload block module',
                                c =  cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                                     'delete',
                                                     **{'updateUI':1})),              
                
                
                return                
                
                
            #>>>Special menu ---------------------------------------------------------------------------------------
            """
            mUI.MelMenuItem(_popUp,
                            ann = self._d_ui_annotations.get('block edit'),
                            c =cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                               'blockEdit',**{'updateUI':0,'mode':'blockEdit'}),
                            label = "Edit Block UI")"""
            
            mUI.MelMenuItem(_popUp,
                            ann = self._d_ui_annotations.get('block edit'),
                            c =cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                               'blockPicker',**{'updateUI':0,'mode':'blockPicker'}),
                            label = "Picker UI")            
            
            mBlockModule = _mBlock.getBlockModule()
            if 'uiBuilderMenu' in list(mBlockModule.__dict__.keys()):
                mBlockModule.uiBuilderMenu(_mBlock,_popUp)
                #_mBlock.atBlockModule('uiBuilderMenu', _popUp)
                mUI.MelMenuItemDiv(_popUp)
                
            
            
            mUI.MelMenuItem(_popUp,
                            ann = 'Set selected active block',
                            c = cgmGEN.Callback(self.uiFunc_block_setActive),
                            label = "To active")
            
            mUI.MelMenuItem(_popUp,
                            ann = 'Select',
                            c = cgmGEN.Callback( self.uiFunc_contextBlockCall, 'select'),
                            label = "Select")
            
            
            #>>>Heirarchy ------------------------------------------------------------------------------------
            _menu_parent = mUI.MelMenuItem(_popUp,subMenu=True,
                                           label = "Parent")
            
            
            mUI.MelMenuItem(_menu_parent,
                            ann = 'Set parent block to selected block',
                            c= lambda *a:self.uiFunc_blockManange_fromScrollList(**{'mode':'setParentToSelected'}),
                            label = "To Selected")            


            mUI.MelMenuItem(_menu_parent,
                            en = _b_active,
                            ann = 'Set parent block to active block: {0}'.format(_str_activeBlock),
                            #c = cgmGEN.Callback(self.uiFunc_blockManange_fromScrollList,**{'mode':'setParentToActive'}),
                            c= lambda *a:self.uiFunc_blockManange_fromScrollList(**{'mode':'setParentToActive'}),
                            label = "To active")
            mUI.MelMenuItem(_menu_parent,
                            ann = 'Clear parent block',
                            #c = cgmGEN.Callback(self.uiFunc_blockManange_fromScrollList,**{'mode':'clearParentBlock'}),
                            c= lambda *a:self.uiFunc_blockManange_fromScrollList(**{'mode':'clearParentBlock'}),
                            
                            label = "Clear")
            
            #>>Mirror ----------------------------------------------------------------------------------------
            _mirror = mUI.MelMenuItem(_popUp, subMenu = True,
                                      label = "Mirror",
                                      en=True,)   
        
            mUI.MelMenuItem(_mirror,
                            label = 'Verify',
                            ann = '[{0}] Create or load mirror block'.format(_short),
                            c = lambda *a: self.uiFunc_block_mirror_create(_mBlock,False) )    
            mUI.MelMenuItem(_mirror,
                            label = 'Rebuild',
                            ann = '[{0}] Rebuild mirror block from scratch'.format(_short),                                                    
                            #c=lambda *a:self.uiCallback_withUpdate( _mBlock.atBlockUtils, mirrorDat[1], **mirrorDat[2]) )                            
                            c = lambda *a: self.uiFunc_block_mirror_create(_mBlock,True) )  
            
            _l_mirror = [#['Create','blockMirror_create', {}],
                         #['Recreate','blockMirror_create', {'forceNew':True}],
                         ['Push','blockMirror_go', {'mode':'push'}],
                         ['Pull','blockMirror_go', {'mode':'pull'}]]
            for mirrorDat in _l_mirror:
                mUI.MelMenuItem(_mirror,
                                label = mirrorDat[0],
                                ann = '[{0}] {1} block controls'.format(_short,mirrorDat[0]),                                                    
                                #c=lambda *a:self.uiCallback_withUpdate( _mBlock.atBlockUtils, mirrorDat[1], **mirrorDat[2]) )                            
                                c=cgmGEN.Callback( _mBlock.atBlockUtils, mirrorDat[1], **mirrorDat[2]) )
    
            
            #>>Utilities ------------------------------------------------------------------------------------------       
            """
            mUI.MelMenuItem(_popUp,
                            label = "Select",
                            en=True,
                            ann = '[{0}] Select the block'.format(_short),                        
                            c=cgmGEN.Callback(_mBlock.select))
            """
            
            
            _sizeMode = mBlockModule.__dict__.get('__sizeMode__',None)
            if _sizeMode:
                mUI.MelMenuItem(_popUp,
                                label ='Size',
                                ann = 'Size by: {0}'.format(_sizeMode),
                                c=cgmGEN.Callback(_mBlock.atUtils, 'size', _sizeMode))
                
                
            mUI.MelMenuItemDiv(_popUp)
            mUI.MelMenuItem(_popUp,
                            label ='Set Name',
                            ann = 'Specify the name for the current block. Current: {0}'.format(_mBlock.cgmName),
                            c = uiCallback_withUpdate(self,_mBlock,_mBlock.atBlockUtils,'set_nameTag'))
            
            mUI.MelMenuItem(_popUp,
                            label ='Edit NameList',
                            ann = 'Ui Prompt to edit nameList',
                            c = cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                                'atUtils','nameList_uiPrompt',
                                                **{}))
            mUI.MelMenuItem(_popUp,
                            label ='Edit Iter Name',
                            ann = 'Ui Prompt to edit Iter Name',
                            c = cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                                'atUtils','set_nameIter',
                                                **{}))
            
            #...side ----------------------------------------------------------------------------------------
            sub_side = mUI.MelMenuItem(_popUp,subMenu=True,
                                       label = 'Set side')
            
            for i,side in enumerate(['None','left','right','center']):
                mUI.MelMenuItem(sub_side,
                                label = side,
                                ann = 'Specify the side for the current block to : {0}'.format(side),
                                c = uiCallback_withUpdate(self,_mBlock,_mBlock.atBlockUtils,'set_side',side))
            #...position ------------------------------------------------------------------------------
            #none:upper:lower:front:back:top:bottom
            sub_position = mUI.MelMenuItem(_popUp,subMenu=True,
                                           label = 'Set position')
            for i,position in enumerate(BLOCKSHARE._l_positions):
                mUI.MelMenuItem(sub_position,
                                label = position,
                                ann = 'Specify the position for the current block to : {0}'.format(position),
                                c = uiCallback_withUpdate(self,_mBlock,_mBlock.atBlockUtils,'set_position',position))
                
            
            mUI.MelMenuItemDiv(_popUp)
            
            mUI.MelMenuItem(_popUp,
                            label = "Recolor",
                            en=True,
                            ann = '[{0}] Recolor the block'.format(_short),                        
                            c=cgmGEN.Callback(_mBlock.atBlockUtils,'color'))
            
            
            mUI.MelMenuItem(_popUp,
                            label = "Verify",
                            ann = '[{0}] Verify the block'.format(_short),                        
                            en=True,
                            c=uiCallback_withUpdate(self,_mBlock,_mBlock.verify))
            mUI.MelMenuItem(_popUp,
                            label = "Delete",
                            ann = '[{0}] delete the block'.format(_short),                        
                            en=True,
                            c=uiCallback_withUpdate(self,_mBlock,_mBlock.atBlockUtils,'delete'))
            mUI.MelMenuItem(_popUp,
                            label = "Duplicate",
                            ann = '[{0}] Duplicate the block'.format(_short),                        
                            en=True,
                            c=uiCallback_withUpdate(self,_mBlock,_mBlock.atBlockUtils,'duplicate'))
            
            mUI.MelMenuItemDiv(_popUp)
            
            
            mUI.MelMenuItem(_popUp,
                            ann = 'Initialize the block as mBlock in the script editor',
                            c = cgmGEN.Callback(self.uiFunc_blockManange_fromScrollList,**{'mode':'toScriptEditor'}),
                            label = "To ScriptEditor")
            
            mUI.MelMenuItem(_popUp,
                            ann = 'Initialize the block as mBlock in the script editor as a rigFactory',
                            c = cgmGEN.Callback(self.uiFunc_blockManange_fromScrollList,**{'mode':'toScriptEditorRigFactory'}),
                            label = "To ScriptEditor as RigFac")
            """
            mUI.MelMenuItem(_popUp,
                            ann = 'Initialize the block as mBlock in the script editor',
                            c =cgmGEN.Callback(self.uiScrollList_blocks.func_byBlock,
                                               'atUtils','to_scriptEditor',
                                               **{'updateUI':0}),
                            label = "To ScriptEditor")"""
            
            mUI.MelMenuItem(_popUp,
                            ann = self._d_ui_annotations.get('step build'),
                            c =cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                               'stepUI',
                                               **{'updateUI':0,'mode':'stepBuild'}),
                            label = "Step Build")
            
            mUI.MelMenuItemDiv(_popUp)
            mUI.MelMenuItem(_popUp,
                            label = 'Reload Module',
                            ann = 'Reload block module',
                            c = cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                                'getBlockModule',
                                                **{'reloadMod':1}))
            

            return
            
        except Exception as err:cgmGEN.cgmExceptCB(Exception,err)
    def uiFunc_block_clearActive(self):
        #self.uiField_inspector(edit=True, label = '')
        self.uiField_report(edit=True, label = '...', en=False)        
        self._blockCurrent = None
        #self.uiFrame_blockAttrs.clear()
        #self.uiFrame_blockInfo.clear()
        self.uiScrollList_blocks.mActive = None
        self.uiScrollList_blocks.rebuild()
        
        self.mBlock = None
        self.uiBlock_edit.clear()
        
    def get_blockList(self):
        _str_func = 'get_blockList'        
        l = []
        if self._blockCurrent and self._blockCurrent.mNode == None:
            self._blockCurrent = False
            log.debug("|{0}| >> Current no longer exists | {1} ".format(_str_func,self._blockCurrent))
            
        for mBlock in self._ml_blocks:
            if mBlock.mNode is not None:
                l.append(mBlock)
            else:
                log.debug("|{0}| >>Dead node | {1} ".format(_str_func,mBlock))
            
        self._ml_blocks = l
        return self._ml_blocks
                
    def uiFunc_block_setActive(self, index = None, mBlock = None):
        try:
            _str_func = 'uiFunc_block_setActive'
            

            """
            try:_blockCurrent = self._blockCurrent
            except:
                log.debug("|{0}| >> Current no longer exists. Reloading...".format(_str_func))                
                self.uiUpdate_scrollList_blocks()
                return"""
            
            ml_sel = self.uiScrollList_blocks.getSelectedObjs()
            ml_sceneBlocks = self.uiScrollList_blocks._ml_loaded
            mBlockUse = None
            
            if mBlock:
                if mBlock not in ml_sceneBlocks:
                    return log.error(cgmGEN.logString_msg(_str_func, "mBlock not found in scene: {0}".format(mBlock)))
                mBlockUse = mBlock

            
            elif index is not None:
                if index in ml_sceneBlocks:
                    #index = ml_sceneBlocks.index(index)
                    mBlockUse = index
                elif index not in list(range(len(ml_sceneBlocks))):
                    log.warning("|{0}| >> Invalid index: {1}".format(_str_func, index))    
                    return
                else:
                    mBlock = ml_sceneBlocks[index]
            elif ml_sel:
                mBlockUse = ml_sel[0]
            elif self._blockCurrent and self._blockCurrent.mNode and self._blockCurrent in ml_sceneBlocks:
                #_idx_current = _ml.index(self._blockCurrent)
                mBlockUse = self._blockCurrent
                log.debug("|{0}| >> Using Current".format(_str_func))    
                
                    
            if not mBlockUse:
                return log.error(cgmGEN.logString_msg(_str_func, "Found no block to make active".format(mBlock)))
            
            log.info("|{0}| >> To set: {1}".format(_str_func, mBlockUse.mNode))
            self._blockCurrent = mBlockUse
            _short = self._blockCurrent.p_nameShort
            
            #>>>Inspector ===================================================================================
            #>>>Report ---------------------------------------------------------------------------------------
            
            
            _l_report = ["{0}".format(self._blockCurrent.p_nameShort)]
            
            """
            if self._blockCurrent.hasAttr('buildProfile'):
                _l_report.insert(0,str(self._blockCurrent.buildProfile))
            #if ATTR.get(_short,'side'):
                #_l_report.append( ATTR.get_enumValueString(_short,'side'))
            if ATTR.has_attr(_short,'blockProfile'):
                _l_report.append("{0} - {1}".format(self._blockCurrent.blockProfile,
                                                    self._blockCurrent.blockType))
            else:
                _l_report.append("{0}".format(self._blockCurrent.blockType))                
            
            
            if self._blockCurrent.isReferenced():
                _l_report.insert(0,"Referenced!")"""
                
            #self.uiField_inspector(edit=True, label = '{0}'.format(' | '.join(_l_report)))
            self.uiField_report(edit=True, en=True, label = '[ ' + '{0}'.format(' ] [ '.join(_l_report))+ ' ]')
            
            #>>>Settings -------------------------------------------------------------------------------------
            #self.uiUpdate_blockDat()#<<< build our blockDat frame
            
            #>>>Info ----------------------------------------------------------------------------------------
            #self.uiFrame_blockInfo.clear()
            
            #for l in self._blockCurrent.atBlockUtils('get_infoBlock_report'):
                #mUI.MelLabel(self.uiFrame_blockInfo,l=l)
            self.uiScrollList_blocks.mActive = mBlockUse
            self.uiScrollList_blocks.rebuild()
            
            
            self.mBlock = mBlockUse
            uiFunc_updateBlock(self)
            
            
            
            return
           
        except Exception as err:cgmGEN.cgmExceptCB(Exception,err)
             
    def uiCallback_setAttrFromField(self, obj, attr, attrType, field):
        _v = field.getValue()
        ATTR.set(obj,attr,_v)
        
        if attrType == 'enum':
            _strValue = ATTR.get_enumValueString(obj,attr)
            field.setValue(_strValue)
            
            if attr == 'buildProfile':
                log.info("Loading buildProfile...")
                self._blockCurrent.atUtils('buildProfile_load',_strValue)
            if attr == 'blockProfile':
                log.info("Loading blockProfile...")
                self._blockCurrent.atUtils('blockProfile_load',_strValue)                
        else:
            field.setValue(ATTR.get(obj,attr))
            
        if attr == 'numRoll':
            log.info("numRoll check...")                            
            if ATTR.datList_exists(obj,'rollCount'):
                log.info("rollCount Found...")                                            
                l = ATTR.datList_getAttrs(obj,'rollCount')
                for a in l:
                    log.info("{0}...".format(a))                                                
                    ATTR.set(obj,a, _v)
                
                #self.uiUpdate_blockDat()
        
        log.info("Set: {0} | {1} | {2}".format(obj,attr,_v))
            
    def uiCallback_contextualSetAttrFromField(self, attr, attrType, field):
        _v = field.getValue()
        
        log.info("{0} | {1}".format(attr,_v))

        self.uiFunc_contextBlockCall('atUtils', 'blockAttr_set', **{'updateUI':False, attr:_v})
        
        if attr == 'buildProfile':
            #_strValue = BLOCKSHARE._d_attrsTo_make['buildProfile'].split(':')[_v]
            log.info("Loading buildProfile... {0}".format(_v))
            self.uiFunc_contextBlockCall('atUtils', 'buildProfile_load', _v, **{'updateUI':False})
        
        
        return
        if attrType == 'enum':
            #_strValue = ATTR.get_enumValueString(obj,attr)
            #field.setValue(_strValue)
            
            if attr == 'buildProfile':
                log.info("Loading buildProfile...")
                self._blockCurrent.atUtils('buildProfile_load',_strValue)
            if attr == 'blockProfile':
                log.info("Loading blockProfile...")
                self._blockCurrent.atUtils('blockProfile_load',_strValue)                
            
            
    def uiCallback_blockDatButton(self,func,*args,**kws):
        func(*args,**kws)
        #self.uiUpdate_blockDat()
        
    def uiSection_blockDatUtils(self,parent):
        _str_func = 'uiUpdate_blockUtils'
        log.debug("|{0}| >> ...".format(_str_func)+ '-'*80)
        
        #self.uiFrame_blockDatUtils.clear()
        #_column = self.uiFrame_blockDatUtils
        
        _column = parent
        
        #BlcokDat ======================================================
        log.debug(cgmGEN.logString_sub(_str_func,'BlockDat Main'))
        mc.setParent(_column)
        _row = mUI.MelHLayout(_column,ut='cgmUISubTemplate',padding = 2)
        #mUI.MelSpacer(_row,w=1)
        
        mc.button(parent=_row,
                  l = 'Save',
                  ut = 'cgmUITemplate',
                  c = cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                      'saveBlockDat',
                                      **{'updateUI':0}),
                  ann = self._d_ui_annotations.get('save blockDat'))
        mc.button(parent=_row,
                  l = 'Load',
                  ut = 'cgmUITemplate',
                  c = cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                      'loadBlockDat',
                                      **{}),
                  ann = self._d_ui_annotations.get('load blockDat'))
        
        mc.button(parent=_row,
                  l = 'Load State',
                  ut = 'cgmUITemplate',
                  c = cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                      'loadBlockDat',
                                      **{'autoPush':False,'currentOnly':True}),
                  ann = self._d_ui_annotations.get('load state blockDat'))
        
        mc.button(parent=_row,
                  l = 'Query',
                  ut = 'cgmUITemplate',
                  c = cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                      'getBlockDat',
                                      **{'updateUI':0}),
                  ann = self._d_ui_annotations.get('get blockDat'))
        
        mc.button(parent=_row,
                  l = 'Copy',
                  ut = 'cgmUITemplate',
                  c = cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                      'atUtils','blockDat_copy',
                                      **{'mode':'blockDatCopyActive'}),
                  ann = "Copy the active blocks data")
        
        mc.button(parent=_row,
                  l = 'Reset',
                  ut = 'cgmUITemplate',
                  c = cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                      'atUtils','blockDat_reset',
                                      **{'updateUI':0}),
                  ann = self._d_ui_annotations.get('reset blockDat'))        
        
        #mUI.MelSpacer(_row,w=1)
        _row.layout()
        
        #BlcokDat ======================================================
        log.debug(cgmGEN.logString_sub(_str_func,'BlockDat Selective'))
        mc.setParent(_column)
        _row = mUI.MelHSingleStretchLayout(_column,ut='cgmUISubTemplate',padding = 5)
        
        mUI.MelSpacer(_row,w=1)
        mUI.MelLabel(_row,l="Load State data: ")        
        _row.setStretchWidget( mUI.MelSeparator(_row) )
        
        
        for state in ['define','form','prerig','skeleton',]:
            mc.button(parent=_row,
                      l = state.capitalize(),
                      ut = 'cgmUITemplate',
                      c = cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                          'atUtils','blockDat_load_state',state,
                                          **{'updateUI':0}),
                      ann = "Load {0} blockDat in context".format(state))
       
        mUI.MelSpacer(_row,w=1)
        _row.layout()        
        
        
    def uiUpdate_blockUtils(self):
        _str_func = 'uiUpdate_blockUtils'
        log.debug("|{0}| >> ...".format(_str_func)+ '-'*80)
        
        self.uiFrame_blockUtils.clear()
        
        _column = self.uiFrame_blockUtils
                
        
        
        #General ======================================================
        log.debug("|{0}| >> General ...".format(_str_func)+ '-'*40)
        mc.setParent(_column)
        _row = mUI.MelHSingleStretchLayout(_column,ut='cgmUISubTemplate',padding = 5)
        mUI.MelSpacer(_row,w=1)        
        mUI.MelLabel(_row,l="General: ")
        _row.setStretchWidget( mUI.MelSeparator(_row) )
        
        mc.button(parent=_row,
                  l = 'Select',
                  ut = 'cgmUITemplate',                                    
                  c = cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                      'select',
                                      **{'updateUI':0}),
                  ann = 'Select blocks')
        mc.button(parent=_row,
                  l = 'Verify',
                  ut = 'cgmUITemplate',                                    
                  c = cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                      'verify',
                                      **{'updateUI':0}),
                  ann = 'Verify conextual blocks')
        """
        mc.button(parent=_row,
                  l = 'Recolor',
                  ut = 'cgmUITemplate',
                  c = cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                      'atUtils','color',
                                      **{'updateUI':0}),
                  ann = 'Recolor conextual blocks')"""
        
        mc.button(parent=_row,
                  l = 'bakeScale',
                  ut = 'cgmUITemplate',
                  c = cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                      'atUtils','blockScale_bake',
                                      **{'updateUI':0}),
                  ann = 'Bake the Scale down so the rigBlock is 1.0')
        
        mc.button(parent=_row,
                  l = 'Duplicate',
                  ut = 'cgmUITemplate',
                  c = cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                      'duplicate',
                                      **{'updateUI':1}),
                  ann = 'Duplicate conextual blocks')
        
        
        mc.button(parent=_row,
                  l = 'Delete',
                  ut = 'cgmUITemplate',
                  c = cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                      'delete',
                                      **{'updateUI':1}),
                  ann = 'Delete conextual blocks')
        
        mUI.MelSpacer(_row,w=1)
        _row.layout()

        
    @cgmGEN.Timer
    def uiUpdate_blockShared(self):
        _str_func = 'uiUpdate_blockShared'
        self.uiFrame_shared.clear()
        
        _column = self.uiFrame_shared
        
        d_shared = {'formNull':{},
                    'prerigNull':{}}
        
        l_settings = ['visibility']
        l_locks = ['rigBlock','formNull','prerigNull']
        l_enums = []
    
        for n in l_locks:
            _row = mUI.MelHSingleStretchLayout(_column,ut='cgmUISubTemplate',padding = 5)
            
            mUI.MelLabel(_row,l=' {0}:'.format(n))
            _row.setStretchWidget( mUI.MelSeparator(_row) )
    
            if n in l_settings:
                l_options = ['hide','show']
                _mode = 'moduleSettings'
            elif n in l_locks:
                l_options = ['unlock','lock']
                _mode = 'moduleSettings'
                if n != 'rigBlock':
                    _plug = d_shared[n].get('plug',n)
            else:
                l_options = ['off','lock','on']
                _mode = 'puppetSettings'
                
            for v,o in enumerate(l_options):
                if n == 'rigBlock':
                    mc.button(parent = _row,
                              ut = 'cgmUITemplate',
                              l=o,
                              c=cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                                'atUtils','templateAttrLock',v),
                              )                    
                else:
                    mc.button(parent = _row,
                              ut = 'cgmUITemplate',
                              l=o,
                              c=cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                                'atUtils', 'messageConnection_setAttr',
                                                _plug,**{'template':v}),
                              )
            mUI.MelSpacer(_row,w=2)
            _row.layout()
            
        for n in l_settings:
            _row = mUI.MelHSingleStretchLayout(_column,ut='cgmUISubTemplate',padding = 5)
    
            mUI.MelLabel(_row,l=' {0}:'.format(n))
            _row.setStretchWidget( mUI.MelSeparator(_row) )
    
            l_options = ['hide','show']

            for v,o in enumerate(l_options):
                mc.button(parent = _row,
                          ut = 'cgmUITemplate',
                          l=o,
                          c=cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                            'atUtils', 'blockAttr_set',
                                            **{n:v})
                          )
            mUI.MelSpacer(_row,w=2)
            _row.layout()
                        
        
        d_attrDat = copy.copy(BLOCKSHARE._d_attrsTo_make)
        
        for i in range(4):
            d_attrDat['rollCount_{0}'.format(i)] = 'int'
        
        _keys = sorted(d_attrDat)
        
        l_mask = ['baseAim','basePoint','baseUp','controlOffset','moduleTarget','nameIter','nameList',
                  'namesHandles','namesJoints']
        self._d_attrFieldsContextual = {}
        for a in _keys:
            if a in l_mask:
                continue
            try:
                _type = d_attrDat[a]
                log.debug("|{0}| >> attr: {1} | {2}".format(_str_func, a, _type))
                _row = mUI.MelHSingleStretchLayout(_column,padding = 5)
                mUI.MelLabel(_row,l=' {0}:'.format(a))
                mUI.MelSpacer(_row,w=_sidePadding)
                
                if ':' in _type:
                    _enum = _type.split(':')                    
                    _type = 'enum'
        
                _row.setStretchWidget(mUI.MelSeparator(_row,))
        
                if _type == 'bool':
                    l_options = ['off','on']
                    for v,o in enumerate(l_options):
                        mc.button(parent = _row,
                                  ut = 'cgmUITemplate',
                                  l=o,
                                  c=cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                                    'atUtils', 'blockAttr_set',
                                                    **{'updateUI':False,a:v}))
                                  
                elif _type == 'enum':
                    _optionMenu = mUI.MelOptionMenu(_row)
                    _optionMenu(e=True,
                                cc = cgmGEN.Callback(self.uiCallback_contextualSetAttrFromField,
                                                     a,
                                                     _type,
                                                     _optionMenu)) 
                    
                    for option in _enum:
                        _optionMenu.append(option)
                
                elif _type in ['double','doubleAngle','doubleLinear','float']:
                    self._d_attrFieldsContextual[a] = mUI.MelFloatField(_row,w = 50)
                    self._d_attrFieldsContextual[a](e=True,
                                          cc  = cgmGEN.Callback(self.uiCallback_contextualSetAttrFromField, a, _type,
                                                                self._d_attrFieldsContextual[a]))
                elif _type in ['int','long']:
                    self._d_attrFieldsContextual[a] = mUI.MelIntField(_row,w = 50,
                                                              )
                    self._d_attrFieldsContextual[a](e=True,
                                          cc  = cgmGEN.Callback(self.uiCallback_contextualSetAttrFromField, a, _type,
                                                                self._d_attrFieldsContextual[a]),
                                          )                
 
                mUI.MelSpacer(_row,w=_sidePadding)                
                _row.layout()
            except Exception as err:
                log.info("Attr {0} failed. err: {1}".format(a,err))            
            
            
            
        
        
        return
        
        #Lock nulls row ------------------------------------------------------------------------
        _mRow_lockNulls = mUI.MelHSingleStretchLayout(_column,ut='cgmUISubTemplate',padding = 2)
        mUI.MelSpacer(_mRow_lockNulls,w=_sidePadding)
        
        mUI.MelLabel(_mRow_lockNulls,l='Lock null:')
        _mRow_lockNulls.setStretchWidget(mUI.MelSeparator(_mRow_lockNulls,))
        
        for null in ['formNull','prerigNull']:
            #_str_null = mBlock.getMessage(null)
            #_nullShort = _str_null[0]
            mUI.MelCheckBox(_mRow_lockNulls, l="- {0}".format(null),
                            #value = ATTR.get(_nullShort,'template'),
                            #onCommand = cgmGEN.Callback(ATTR.set,_nullShort,'template',1),
                            #offCommand = cgmGEN.Callback(ATTR.set,_nullShort,'template',0))                
                            )
        
        mUI.MelSpacer(_mRow_lockNulls,w=_sidePadding)
        _mRow_lockNulls.layout()        
    
    
    def uiUpdate_blockDat(self):
        _str_func = 'uiUpdate_blockDat'
        log.debug("|{0}| >> ...".format(_str_func)+ '-'*80)
        log.warning("Remove this.")
        return False
        self.uiFrame_blockSettings.clear()
        #_d_ui_annotations = {}
        
        if self._blockCurrent and self._blockCurrent.mNode:
            _short = self._blockCurrent.p_nameShort
            _intState = self._blockCurrent.getState(False)        
        mBlock = self._blockCurrent
        
        if not mBlock:
            return
        
        log.debug("|{0}| >>  Current Block: {1}".format(_str_func,mBlock))
        
        #Save/Load row... ------------------------------------------------------------------------
        _mBlockDat = mUI.MelHLayout(self.uiFrame_blockSettings,ut='cgmUISubTemplate',padding = 2)
        CGMUI.add_Button(_mBlockDat, "Save",
                         cgmGEN.Callback(self._blockCurrent.saveBlockDat),
                         self._d_ui_annotations.get('save blockDat'))       
        CGMUI.add_Button(_mBlockDat, "Load",
                         cgmGEN.Callback(self._blockCurrent.loadBlockDat),
                         self._d_ui_annotations.get('load blockDat') )       
        CGMUI.add_Button(_mBlockDat, "Copy",
                         cgmGEN.Callback(self.uiFunc_contextBlockCall,'loadBlockDat'),
                         self._d_ui_annotations.get('copy blockDat'),                         
                         en=False)         
    
        CGMUI.add_Button(_mBlockDat,'Reset',
                         cgmGEN.Callback(self._blockCurrent.resetBlockDat), 
                         self._d_ui_annotations.get('reset blockDat'))                                
        CGMUI.add_Button(_mBlockDat,'Refresh',
                         cgmGEN.Callback(self.uiUpdate_blockDat),
                         "Resync the ui blockDat with any changes you've made in viewport.")
        _mBlockDat.layout()
        
        #Lock nulls row ------------------------------------------------------------------------
        _mRow_lockNulls = mUI.MelHSingleStretchLayout(self.uiFrame_blockSettings,ut='cgmUISubTemplate',padding = 2)
        mUI.MelSpacer(_mRow_lockNulls,w=_sidePadding)
        
        mUI.MelLabel(_mRow_lockNulls,l='Lock null:')
        _mRow_lockNulls.setStretchWidget(mUI.MelSeparator(_mRow_lockNulls,))
        
        for null in ['formNull','prerigNull']:
            _str_null = mBlock.getMessage(null)
            if _str_null:
                _nullShort = _str_null[0]
                mUI.MelCheckBox(_mRow_lockNulls, l="- {0}".format(null),
                                value = ATTR.get(_nullShort,'template'),
                                onCommand = cgmGEN.Callback(ATTR.set,_nullShort,'template',1),
                                offCommand = cgmGEN.Callback(ATTR.set,_nullShort,'template',0))                
            else:
                mUI.MelCheckBox(_mRow_lockNulls, l="- {0}".format(null),
                                en=False)
        
        mUI.MelSpacer(_mRow_lockNulls,w=_sidePadding)
        _mRow_lockNulls.layout()
        

        #Attrs... ------------------------------------------------------------------------
        _l_attrs = self._blockCurrent.atUtils('get_stateChannelBoxAttrs',_intState)
    
        self._d_attrFields = {}
        _l_attrs.sort()
        for a in _l_attrs:
            try:
                if a in ['blockState']:
                    continue
                _type = ATTR.get_type(_short,a)
                log.debug("|{0}| >> attr: {1} | {2}".format(_str_func, a, _type))
                _hlayout = mUI.MelHSingleStretchLayout(self.uiFrame_blockSettings,padding = 5)
                mUI.MelSpacer(_hlayout,w=_sidePadding)
        
                _hlayout.setStretchWidget(mUI.MelSeparator(_hlayout,))
        
                if _type not in ['bool']:#Some labels parts of fields
                    mUI.MelLabel(_hlayout,l="{0} -".format(a))   
        
                if _type == 'bool':
                    mUI.MelCheckBox(_hlayout, l="- {0}".format(a),
                                    #annotation = "Copy values",		                           
                                    value = ATTR.get(_short,a),
                                    onCommand = cgmGEN.Callback(ATTR.set,_short,a,1),
                                    offCommand = cgmGEN.Callback(ATTR.set,_short,a,0))
        
                elif _type in ['double','doubleAngle','doubleLinear','float']:
                    self._d_attrFields[a] = mUI.MelFloatField(_hlayout,w = 50,
                                                              value = ATTR.get(_short,a),                                                          
                                                              )
                    self._d_attrFields[a](e=True,
                                          cc  = cgmGEN.Callback(self.uiCallback_setAttrFromField,_short, a, _type,
                                                                self._d_attrFields[a]),
                                          )
                elif _type == 'long':
                    self._d_attrFields[a] = mUI.MelIntField(_hlayout,w = 50,
                                                             value = ATTR.get(_short,a),
                                                             maxValue=20,
                                                             minValue=ATTR.get_min(_short,a),
                                                              )
                    self._d_attrFields[a](e=True,
                                          cc  = cgmGEN.Callback(self.uiCallback_setAttrFromField,_short, a, _type,
                                                                self._d_attrFields[a]),
                                          )                
                elif _type == 'string':
                    self._d_attrFields[a] = mUI.MelTextField(_hlayout,w = 75,
                                                             text = ATTR.get(_short,a),
                                                              )
                    self._d_attrFields[a](e=True,
                                          cc  = cgmGEN.Callback(self.uiCallback_setAttrFromField,_short, a, _type,
                                                                self._d_attrFields[a]),
                                          )
                elif _type == 'enum':
                    _optionMenu = mUI.MelOptionMenu(_hlayout)
                    _optionMenu(e=True,
                                cc = cgmGEN.Callback(self.uiCallback_setAttrFromField,_short, a, _type,
                                                     _optionMenu),) 
                    for option in ATTR.get_enumList(_short,a):
                        _optionMenu.append(option)
                    _optionMenu.setValue(ATTR.get_enumValueString(_short,a))
                else:
                    mUI.MelLabel(_hlayout,l="{0}({1}):{2}".format(a,_type,ATTR.get(_short,a)))        
        
                mUI.MelSpacer(_hlayout,w=_sidePadding)                
                _hlayout.layout()
            except Exception as err:
                log.info("Attr {0} failed. err: {1}".format(a,err))
                
    
    def buildMenu_help( self, *args):
        self.uiMenu_help.clear()
        mUI.MelMenuItem( self.uiMenu_help, l="Get Call Size",
                         c=lambda *a: RIGBLOCKS.get_callSize('selection' ) )
        mUI.MelMenuItem( self.uiMenu_help, l="Test Context",
                         c=lambda *a: self.uiFunc_contextBlockCall('VISUALIZEHEIRARCHY') )
        mUI.MelMenuItem( self.uiMenu_help, l="Reverify Scene Blocks",
                         c=lambda *a: BLOCKGEN.verify_sceneBlocks() )
        
        mUI.MelMenuItem( self.uiMenu_help, l="Reload BlocksStuff",
                         c=lambda *a: reloadMRSStuff() )        
        
        
        mUI.MelMenuItem( self.uiMenu_help, l="Thanks!",
                         c=lambda *a: cgmUI.uiWindow_thanks() )
        
        
        mc.menuItem(parent=self.uiMenu_help,
                    l = 'Get Help',
                    c='import webbrowser;webbrowser.open("https://www.cgmonastery.com/teams/mrs-collaborative/");',                        
                    rp = 'N')    
        mUI.MelMenuItem( self.uiMenu_help, l="Log Self",
                         c=lambda *a: cgmUI.log_selfReport(self) )   
        mUI.MelMenuItem( self.uiMenu_help, l="Update Display",
                         c=lambda *a:self.uiScrollList_blocks.rebuild())
        
 
    def uiFunc_clear_loaded(self):
        _str_func = 'uiFunc_clear_loaded'  
        self._mNode = False
        self._mGroup = False
        self._utf_obj(edit=True, l='',en=False)      
        self.uiField_report(edit=True, l='...')
        #self.uiReport_objects()
        self.uiScrollList_parents.clear()
        
        for o in self._l_toEnable:
            o(e=True, en=False)        
    """
    def uiUpdate_sceneBlocks(self):
        _ml,_l_strings = BLOCKGEN.get_uiScollList_dat(showSide=1)
        
        self.__ml_blocks = _ml
        self.__l_strings = _l_strings
        self.__l_itc = []
        
        d_colors = {'left':[.5,.5,1],
                    'right':[.8,.5,.5],
                    'center':[.8,.8,0]}

        for mBlock in _ml:
            _arg = mBlock.getEnumValueString('blockState')#atUtils('get_side')
            _color = d_colors.get(_arg,d_colors['center'])
            self.__l_itc.append(_color)

    def uiUpdate_scrollList_blocks(self, select = None):
        _str_func = 'uiUpdate_scrollList_blocks'
        #if self.uiPopUpMenu_blocks:
        #    self.uiPopUpMenu_blocks.clear()
        #    self.uiPopUpMenu_blocks.delete()
        #    self.uiPopUpMenu_blocks = None
            
        self.uiScrollList_blocks.clear()
        
        
        searchFilter=self.cgmUIField_filterBlocks.getValue()
        #log.info(cgmGEN.logString_msg(_str_func, 'SearchFilter: {0}'.format(searchFilter)))
        
        _ml_use = []
        
        #_ml,_l_strings = BLOCKGEN.get_uiScollList_dat()
        _ml = copy.copy(self.__ml_blocks)
        _l_strings = copy.copy(self.__l_strings)
        
        _len = len(_ml)
        if not _ml:
            log.warning("|{0}| >> No blocks found in scene.".format(_str_func)) 
            self.uiFunc_block_clearActive()
            return False      


        try:
            for i,strEntry in enumerate(r9Core.filterListByString(_l_strings, searchFilter, matchcase=False)):
            #for i,strEntry in enumerate(_l_strings):
                self.uiScrollList_blocks.append(strEntry)
                idx = _l_strings.index(strEntry)
                _ml_use.append(_ml[idx])
                
                #_side = _ml[idx].getEnumValueString('side')#atUtils('get_side')
                #_color = self.__l_itc[idx]
                _color = d_state_colors.get(_ml[idx].getEnumValueString('blockState'))
                try:self.uiScrollList_blocks(e=1, itc = [(i+1,_color[0],_color[1],_color[2])])
                except:pass
                
        except Exception,err:
            try:
                log.error("|{0}| >> err: {1}".format(_str_func, err))  
                for a in err:
                    log.error(a)
                #cgmUI.doEndMayaProgressBar(_progressBar)
            except:
                raise Exception,err
            
        self._ml_blocks = _ml_use

        #cgmUI.doEndMayaProgressBar(_progressBar) 
        return
        if select:
            if select in self._ml_blocks:
                self.uiScrollList_blocks.selectByIdx(self._ml_blocks.index(select))"""
                
    def uiUpdate_context(self,var=None,value=None):
        if var:
            var.setValue(value)
            
        _context = self._l_contextModes[self.var_contextMode.value]
        _contextStart = self._l_contextStartModes[self.var_contextStartMode.value]
        _force = self.var_contextForceMode.value
        
        if _context == 'self':
            log.info("Self mode means force = True")
            _force = 1
        
        _label = "Context: {0} | Begin with: {1} | Force: {2}".format(
        _context,
        _contextStart,
        bool(_force))
        
        self.uiFrame_context(edit=True,label=_label)
        #self.uiField_contextReport(edit=True,label=_label)
        
    def build_layoutWrapper(self,parent):
        _str_func = 'build_layoutWrapper'
    
        _MainForm = mUI.MelFormLayout(self,ut='cgmUITemplate')
        
        ui_tabs = mUI.MelTabLayout( _MainForm,w=180 )
        
        uiTab_setup = mUI.MelFormLayout(ui_tabs,ut='cgmUITemplate')#mUI.MelColumnLayout(ui_tabs)
        self.uiTab_setup = uiTab_setup
        
        uiTab_utils = mUI.MelScrollLayout( ui_tabs,ut='cgmUITemplate' )
        
        for i,tab in enumerate(['Setup','Utils']):
            ui_tabs.setLabel(i,tab)
            
        self.buildTab_setup(uiTab_setup)
        self.buildTab_utilities(uiTab_utils)
        #TOOLBOX.buildTab_td(self,uiTab_utils)

        #self.buildTab_create(uiTab_create)
        #self.buildTab_update(uiTab_update)
    
        self.uiRow_progress = mUI.MelHLayout(_MainForm,vis=False)
        self.uiProgressText = mUI.MelLabel(self.uiRow_progress,
                                           bgc = SHARED._d_gui_state_colors.get('warning'),
                                           label = '...',
                                           h=20)        
        self.uiPB_mrs=None
        mc.setParent(self.uiRow_progress)
        self.uiPB_mrs = mc.progressBar()
        self.uiRow_progress.layout()
        _row_cgm = cgmUI.add_cgmFooter(_MainForm)
        self.uiRow_cgm = _row_cgm
        _MainForm(edit = True,
                  af = [(ui_tabs,"top",0),
                        (ui_tabs,"left",0),
                        (ui_tabs,"right",0),
                        (self.uiRow_progress,"left",0),
                        (self.uiRow_progress,"right",0),                        
                        (_row_cgm,"left",0),
                        (_row_cgm,"right",0),
                        (_row_cgm,"bottom",0),
    
                        ],
                  ac = [(ui_tabs,"bottom",0,self.uiRow_progress),
                        (self.uiRow_progress,"bottom",0,_row_cgm)
                        ],
                  attachNone = [(_row_cgm,"top")])
    
    def buildTab_utilities(self,parent):
        _MainForm = parent
        
        self.uiPopUpMenu_createShape = None
        self.uiPopUpMenu_color = None
        self.uiPopUpMenu_attr = None
        self.uiPopUpMenu_raycastCreate = None
                
        try:self.var_attrCreateType
        except:self.var_attrCreateType = cgmMeta.cgmOptionVar('cgmVar_attrCreateType', defaultValue = 'float')        
        try:self.var_curveCreateType
        except:self.var_curveCreateType = cgmMeta.cgmOptionVar('cgmVar_curveCreateType', defaultValue = 'circle')
        try:self.var_curveCreateType
        except:self.var_curveCreateType = cgmMeta.cgmOptionVar('cgmVar_curveCreateType', defaultValue = 'circle')
        try:self.var_defaultCreateColor
        except:self.var_defaultCreateColor = cgmMeta.cgmOptionVar('cgmVar_defaultCreateColor', defaultValue = 'yellow')
        try:self.var_createAimAxis 
        except:self.var_createAimAxis = cgmMeta.cgmOptionVar('cgmVar_createAimAxis', defaultValue = 2)
        try:self.var_createSizeMode 
        except:self.var_createSizeMode = cgmMeta.cgmOptionVar('cgmVar_createSizeMode', defaultValue=0)
        try:self.var_createSizeValue     
        except:self.var_createSizeValue = cgmMeta.cgmOptionVar('cgmVar_createSizeValue', defaultValue=1.0)
        try:self.var_createSizeMulti     
        except:self.var_createSizeMulti = cgmMeta.cgmOptionVar('cgmVar_createSizeMultiplierValue', defaultValue=1.25)
    
        self.var_createRayCast = cgmMeta.cgmOptionVar('cgmVar_createRayCast', defaultValue = 'locator')        
        self.var_rayCastTargetsBuffer = cgmMeta.cgmOptionVar('cgmVar_rayCastTargetsBuffer',defaultValue = [''])            
        self.var_rayCastMode = cgmMeta.cgmOptionVar('cgmVar_rayCastMode', defaultValue=0)
        self.var_rayCastOffsetMode = cgmMeta.cgmOptionVar('cgmVar_rayCastOffsetMode', defaultValue=0)
        self.var_rayCastOffsetDist = cgmMeta.cgmOptionVar('cgmVar_rayCastOffsetDist', defaultValue=1.0) 
        self.var_rayCastOrientMode = cgmMeta.cgmOptionVar('cgmVar_rayCastOrientMode', defaultValue = 0)
        self.var_rayCastDragInterval = cgmMeta.cgmOptionVar('cgmVar_rayCastDragInterval', defaultValue = .2)
    
        try:
            parent(edit = True,
                   af = [(_MainForm,"top",0),
                         (_MainForm,"left",0),
                         (_MainForm,"right",0),
                         (_MainForm,"bottom",0)])
        except:pass
        #>>>Shape Creation ====================================================================================
        mc.setParent(parent)
        
    
        #>>>Tools -------------------------------------------------------------------------------------  
        #self.buildRow_context(parent)                     
        
        SNAPTOOLS.buildSection_snap(self,parent)
        cgmUI.add_HeaderBreak()        
        
        SNAPTOOLS.buildSection_aim(self,parent)
        cgmUI.add_HeaderBreak()
        
        SNAPTOOLS.buildSection_advancedSnap(self,parent)
        cgmUI.add_HeaderBreak()           
        
        TOOLBOX.buildSection_rigging(self,parent)
        cgmUI.add_SectionBreak()  
        
        TOOLBOX.buildSection_joint(self,parent)
        cgmUI.add_SectionBreak()          
        
        #buildSection_transform(self,parent)
        #cgmUI.add_SectionBreak()  
                
        TOOLBOX.buildSection_shape(self,parent)
        cgmUI.add_SectionBreak()            
        
        TOOLBOX.buildSection_color(self,parent)
        cgmUI.add_SectionBreak()  
        
        TOOLBOX.buildSection_rayCast(self,parent)
        cgmUI.add_SectionBreak()      
        
        TOOLBOX.buildSection_distance(self,parent)        
        
        

        
    def buildTab_setup(self,parent):
        _str_func = 'buildTab_setup'
        _MainForm = parent
        #_MainForm = mUI.MelScrollLayout(parent)	        

        
        #=======================================================================
        #>> Left Column
        #============================================================
        _LeftColumn = mUI.MelFormLayout(_MainForm)
        _header = cgmUI.add_Header('Rigblocks')
        _textField = mUI.MelTextField(_LeftColumn,
                                      ann='Filter blocks',
                                      w=50,
                                      bgc = [.3,.3,.3],
                                      en=True,
                                      text = '')
        self.cgmUIField_filterBlocks = _textField

        
        _scrollList = BlockScrollList(_LeftColumn, ut='cgmUISubTemplate',
                                      allowMultiSelection=True,en=True,
                                      ebg=1,
                                      bgc = [.2,.2,.2],
                                      dcc = cgmGEN.Callback(self.uiFunc_block_setActive),
                                      #cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                            #                'blockEdit',**{'updateUI':0,'mode':'blockEdit'}),#cgmGEN.Callback(self.uiFunc_block_setActive),
                                      w = 50)
        try:_scrollList(edit=True,hlc = [.5,.5,.5])
        except:pass
        
        #_scrollList(e=True,selectCommand = lambda *a:self.uiScrollList_block_select())
        _scrollList.cmd_select = self.uiScrollList_block_select
        
        _scrollList.set_filterObj(self.cgmUIField_filterBlocks)
        self.cgmUIField_filterBlocks(edit=True,
                                     tcc = lambda *a: self.uiScrollList_blocks.update_display())
        
        self.uiScrollList_blocks = _scrollList
        self._l_toEnable.append(self.uiScrollList_blocks)
        
        button_refresh = CGMUI.add_Button(_LeftColumn,'Refresh',
                                          lambda *a:self.uiScrollList_blocks.rebuild(),
                                          'Force the scroll list to update')
        
        _LeftColumn(edit = True,
                    af = [(_header,"top",0),
                          (_header,"left",0),
                          (_header,"right",0),
                          (_textField,"left",0),
                          (_textField,"right",0),                           
                          (_scrollList,"left",0),
                          (_scrollList,"right",0),
                          
                          (button_refresh,"left",0),
                          (button_refresh,"right",0),
                          (button_refresh,"bottom",0),

                          ],
                    ac = [(_textField,"top",0,_header),
                          (_scrollList,"top",0,_textField),
                          (_scrollList,"bottom",0,button_refresh),
                          
                         ],
                    attachNone = [(_textField,'bottom'),
                                  (button_refresh,'top')])#(_row_cgm,"top")	          
  
        
        
        _RightColumn = mUI.MelFormLayout(_MainForm)
        _RightUpperColumn = mUI.MelColumn(_RightColumn)
        _RightScroll = mUI.MelScrollLayout(_RightColumn,useTemplate = 'cgmUITemplate',width=400)
        

        #=============================================================================================
        #>> Top
        #=============================================================================================
        self.uiFrame_context = mUI.MelLabel(_RightUpperColumn,l='',align='center')
        
        self.create_guiOptionVar('contextSettingsFrameCollapse',defaultValue = 0)       
        
        _frame_context = mUI.MelFrameLayout(_RightUpperColumn,label = 'Utilities - Contextual',vis=True,
                                                collapse=self.var_contextSettingsFrameCollapse.value,
                                                collapsable=True,
                                                enable=True,
                                                useTemplate = 'cgmUIHeaderTemplate',
                                                expandCommand = lambda:self.var_contextSettingsFrameCollapse.setValue(0),
                                                collapseCommand = lambda:self.var_contextSettingsFrameCollapse.setValue(1)
                                                )	
        self.uiFrame_context = _frame_context
        _frame_context_inside = mUI.MelColumnLayout(_frame_context,useTemplate = 'cgmUISubTemplate') 

        
        
        
        #mc.setParent(_RightUpperColumn
        
        #Context mode  -------------------------------------------------------------------------------          
        self.create_guiOptionVar('contextMode',defaultValue = 0)       
    
        _rc_contextMode = mUI.MelRadioCollection()
        
        self._l_contextModes = ['self','below','root','scene']
        _d_ann = {'self':'Context is only of the active/sel block',
                  'below':'Context is active/sel block and below',
                  'root':'Context is active/sel root and below',
                  'scene':'Context is all blocks in the scene. Careful skippy!',}
        
        #build our sub section options
        #MelHSingleStretchLayout
        _row_contextModes = mUI.MelHSingleStretchLayout(_frame_context_inside,ut='cgmUISubTemplate',padding = 5)
        mUI.MelSpacer(_row_contextModes,w=1)
        mUI.MelLabel(_row_contextModes,l = 'Context:')
        _row_contextModes.setStretchWidget( mUI.MelSeparator(_row_contextModes) )
        _on = self.var_contextMode.value
        for i,item in enumerate(self._l_contextModes):
            if i == _on:_rb = True
            else:_rb = False
            _rc_contextMode.createButton(_row_contextModes,label=self._l_contextModes[i],sl=_rb,
                                             ann = _d_ann[item],
                                             onCommand = cgmGEN.Callback(self.uiUpdate_context,
                                                                         self.var_contextMode,i))
            mUI.MelSpacer(_row_contextModes,w=2)

        _row_contextModes.layout()         
        """
        #Context Start  -------------------------------------------------------------------------------          
        self.create_guiOptionVar('contextStartMode',defaultValue = 1)       
    
        _rc_contextStartMode = mUI.MelRadioCollection()
    
        self._l_contextStartModes = ['active','selected']
        _d_ann = {'active':'Context begins with active block',
                  'selected':'Context beghins with selected block in the picker on the left',}
    
        #build our sub section options
        #MelHSingleStretchLayout
        _row_contextStartModes = mUI.MelHSingleStretchLayout(_frame_context_inside,ut='cgmUISubTemplate',padding = 5)
        mUI.MelSpacer(_row_contextStartModes,w=1)
        mUI.MelLabel(_row_contextStartModes,l = 'Begin with:')
        
        self.uiOM_beginWith = mUI.MelOptionMenu(_row_contextStartModes,
                                                ut = 'cgmUITemplate', h=25,
                                                cc=lambda *a: self.uiUpdate_context)
        
        _on = self.var_contextStartMode.value
        for i,item in enumerate(self._l_contextStartModes):
            self.uiOM_beginWith.append(item)
            mUI.MelSpacer(_row_contextStartModes,w=2)
            
        _row_contextStartModes.setStretchWidget( mUI.MelSeparator(_row_contextStartModes) )
        
        #..force modes
        self.create_guiOptionVar('contextForceMode',defaultValue = 0)       
    
        _rc_contextForceMode = mUI.MelRadioCollection()
        
        #build our sub section options
        mUI.MelSpacer(_row_contextStartModes,w=1)
        mUI.MelLabel(_row_contextStartModes,l = 'Force:')
        self.uiOM_forceMode = mUI.MelOptionMenu(_row_contextStartModes,
                                                ut = 'cgmUITemplate', h=25,
                                                cc=lambda *a: self.uiUpdate_context)
        
        _on = self.var_contextForceMode.value
        for i,item in enumerate(['False','True']):
            self.uiOM_forceMode.append(item)
            mUI.MelSpacer(_row_contextStartModes,w=2)
            
    
        _row_contextStartModes.layout()       
        
        """
        #Push Rows  -------------------------------------------------------------------------------  
        mc.setParent(_RightUpperColumn)
        CGMUI.add_LineSubBreak()
        _row_push = mUI.MelHLayout(_RightUpperColumn,ut='cgmUISubTemplate',padding = 2)
        mc.button(l='Define>',
                  bgc = d_state_colors['define'],#SHARED._d_gui_state_colors.get('warning'),
                  height = 20,
                  align='center',
                  c=cgmGEN.Callback(self.uiFunc_contextBlockCall,'changeState','define',**{'forceNew':True}),
                  ann='[Define] - initial block state')
        mc.button(l='<Form>',
                  bgc = d_state_colors['form'],              
                  height = 20,
                  align='center',                  
                  c=cgmGEN.Callback(self.uiFunc_contextBlockCall,'changeState','form',**{'forceNew':True}),
                  ann='[Template] - Shaping the proxy and initial look at settings')
                         
        mc.button(l='<Prerig>',
                  bgc = d_state_colors['prerig'],                  
                  height = 20,
                  align='center',
                  c=cgmGEN.Callback(self.uiFunc_contextBlockCall,'changeState','prerig',**{'forceNew':True}),
                  ann='[Prerig] - More refinded placement and setup before rig process')

        mc.button(l='<Joint>',
                  bgc = d_state_colors['skeleton'],                  
                  height = 20,
                  align='center',                  
                  c=cgmGEN.Callback(self.uiFunc_contextBlockCall,'changeState','skeleton',**{'forceNew':True}),
                  ann='[Joint] - Build skeleton if necessary')

        mc.button(l='<Rig',
                  bgc = d_state_colors['rig'],                  
                  height = 20,
                  align='center',                  
                  c=cgmGEN.Callback(self.uiFunc_contextBlockCall,'changeState','rig',**{'forceNew':True}),
                  ann='[Rig] - Push to a fully rigged state.')

        _row_push.layout()
        
        #Active Block Row =================================================================================
        mc.setParent(_RightUpperColumn)
        _header = cgmUI.add_Header('Active Block')
        
        _row_report = mUI.MelHSingleStretchLayout(_RightUpperColumn ,ut='cgmUIInstructionsTemplate',h=20)
        self.uiField_report = mUI.MelButton(_row_report,
                                            bgc = SHARED._d_gui_state_colors.get('help'),
                                            c=lambda *a:self.mBlock.select(),
                                            en= False, 
                                            label = '...',
                                            h=20)
        _row_report.setStretchWidget(self.uiField_report)
        cgmUI.add_Button(_row_report,'<<',
                         cgmGEN.Callback(self.uiFunc_block_setActive),
                         #lambda *a: attrToolsLib.doAddAttributesToSelected(self),
                         "Set the active block.")
        cgmUI.add_Button(_row_report,'Clear',
                         cgmGEN.Callback(self.uiFunc_block_clearActive),
                         #lambda *a: attrToolsLib.doAddAttributesToSelected(self),
                         "Clear the active block.")
        mUI.MelSpacer(_row_report,w=2)
        _row_report.layout()                 
        
        buildFrame_blockEditor(self,_RightScroll)
        
               
        """
        #Utilities Frame =====================================================================================
        log.debug("|{0}| >>  blockUtils...".format(_str_func)+ '-'*40)
        
        self.create_guiOptionVar('blockUtilsFrameCollapse',defaultValue = 0)       
    
        _frame_blockUtils = mUI.MelFrameLayout(_RightScroll,label = 'Utilities',vis=True,
                                                collapse=self.var_blockUtilsFrameCollapse.value,
                                                collapsable=True,
                                                enable=True,
                                                useTemplate = 'cgmUIHeaderTemplate',
                                                expandCommand = lambda:self.var_blockUtilsFrameCollapse.setValue(0),
                                                collapseCommand = lambda:self.var_blockUtilsFrameCollapse.setValue(1)
                                                )	
        self.uiFrameLayout_blockUtils = _frame_blockUtils
    
        _frame_blockUtils_inside = mUI.MelColumnLayout(_frame_blockUtils,useTemplate = 'cgmUISubTemplate')  
        self.uiFrame_blockUtils = _frame_blockUtils_inside
        """
        #self.uiUpdate_blockUtils()
        #buildFrame_mirror(self,_RightScroll)
        #buildFrame_blockDat(self,_RightScroll)
        
        """
        #BlockDat Frame =====================================================================================
        log.debug("|{0}| >>  blockDat...".format(_str_func)+ '-'*40)
        
        self.create_guiOptionVar('blockDatFrameCollapse',defaultValue = 0)       
    
        _frame_blockDat = mUI.MelFrameLayout(_RightScroll,label = 'BlockDat',vis=True,
                                             collapse=self.var_blockUtilsFrameCollapse.value,
                                             collapsable=True,
                                             enable=True,
                                             useTemplate = 'cgmUIHeaderTemplate',
                                             expandCommand = lambda:self.var_blockDatFrameCollapse.setValue(0),
                                             collapseCommand = lambda:self.var_blockDatFrameCollapse.setValue(1)
                                             )	
        self.uiFrameLayout_blockDat = _frame_blockDat
        _frame_blockDat_inside = mUI.MelColumnLayout(_frame_blockDat,useTemplate = 'cgmUISubTemplate')  
        self.uiFrame_blockDat = _frame_blockDat_inside
        self.uiSection_blockDatUtils(_frame_blockDat_inside)"""
        
        
        """
        #Active  Frame ------------------------------------------------------------------------------------
        log.debug("|{0}| >>  Active block frame...".format(_str_func)+ '-'*40)
        
        self.create_guiOptionVar('blockSettingsFrameCollapse',defaultValue = 0)       
    
        _frame_blockSettings = mUI.MelFrameLayout(_RightScroll,label = 'Settings - Active',vis=True,
                                                  collapse=self.var_blockSettingsFrameCollapse.value,
                                                  collapsable=True,
                                                  enable=True,
                                                  useTemplate = 'cgmUIHeaderTemplate',
                                                  expandCommand = lambda:self.var_blockSettingsFrameCollapse.setValue(0),
                                                  collapseCommand = lambda:self.var_blockSettingsFrameCollapse.setValue(1)
                                                  )	
        self.uiFrameLayout_blockSettings = _frame_blockSettings
    
        _frame_settings_inside = mUI.MelColumnLayout(_frame_blockSettings,useTemplate = 'cgmUISubTemplate')  
        self.uiFrame_blockSettings = _frame_settings_inside
        
        #Contextual frame ------------------------------------------------------------------------------------
        log.debug("|{0}| >>  Contextual block frame...".format(_str_func)+ '-'*40)
        
        _frame_shared = mUI.MelFrameLayout(_RightScroll,label = 'Settings - Contextual',vis=True,
                                           collapse=self.var_blockSharedFrameCollapse.value,
                                           collapsable=True,
                                           enable=True,
                                           useTemplate = 'cgmUIHeaderTemplate',
                                           expandCommand = lambda:self.var_blockSharedFrameCollapse.setValue(0),
                                           collapseCommand = lambda:self.var_blockSharedFrameCollapse.setValue(1)
                                           )	
        self.uiFrameLayout_blockShared = _frame_shared
        self.uiFrame_shared = mUI.MelColumnLayout(_frame_shared,useTemplate = 'cgmUISubTemplate')  
        self.uiUpdate_blockShared()
        

        #Info ------------------------------------------------------------------------------------
        _frame_info = mUI.MelFrameLayout(_RightScroll,label = 'Info',vis=True,
                                        collapse=self.var_blockInfoFrameCollapse.value,
                                        collapsable=True,
                                        enable=True,
                                        useTemplate = 'cgmUIHeaderTemplate',
                                        expandCommand = lambda:self.var_blockInfoFrameCollapse.setValue(0),
                                        collapseCommand = lambda:self.var_blockInfoFrameCollapse.setValue(1)
                                        )	
        self.uiFrameLayout_blockInfo = _frame_info
        
        _frame_info_inside = mUI.MelColumnLayout(_frame_info,useTemplate = 'cgmUISubTemplate')  
        self.uiFrame_blockInfo = _frame_info_inside"""
        
        
        
  

        _RightColumn(edit = True,
                     af = [(_RightUpperColumn,"top",0),
                           (_RightUpperColumn,"left",0),
                           (_RightUpperColumn,"right",0),
    
                           (_RightScroll,"left",0),
                           (_RightScroll,"right",0),
                           (_RightScroll,"bottom",0),
    
                           ],
                     ac = [(_RightScroll,"top",0,_RightUpperColumn),
    
                           ],)
                #attachNone = [(button_refresh,'top')])#(_row_cgm,"top")

        self.uiUpdate_context()
        
        #>>> Layout form ---------------------------------------------------------------------------------------
        _MainForm(edit = True,
                  af = [(_LeftColumn,"top",0),
                        (_RightColumn,"top",0),                         
                        (_LeftColumn,"left",0),
                        (_RightColumn,"right",0),                        
                        (_RightColumn,"bottom",0),
                        (_LeftColumn,"bottom",0),

                        ],
                  ac = [(_LeftColumn,"right",0,_RightColumn),
                        #(_RightColumn,"left",0,_LeftColumn),
                        
                        #(_RightColumn,"bottom",0,_row_cgm),
                        #(_LeftColumn,"bottom",0,_row_cgm),

                        
                       ],
                  attachNone = [])#(_row_cgm,"top")	  
        
        self.uiScrollList_blocks.rebuild()        
        
        
    
def uiOptionMenu_blockSizeMode(self, parent, callback = cgmGEN.Callback):
    uiMenu = mc.menuItem( parent = parent, l='Create Mode:', subMenu=True)
    
    try:self.var_rigBlockCreateSizeMode
    except:self.var_rigBlockCreateSizeMode = cgmMeta.cgmOptionVar('cgmVar_rigBlockCreateSizeMode', defaultValue = 'selection')

    try:#>>>
        _str_section = 'Contextual TD mode'
        uiRC = mc.radioMenuItemCollection()
        #self.uiOptions_menuMode = []		
        _v = self.var_rigBlockCreateSizeMode.value

        for i,item in enumerate(['input','selection','default']):
            if item == _v: _rb = True
            else:_rb = False
            mc.menuItem(parent=uiMenu,collection = uiRC,
                        label=item,
                        c = callback(self.var_rigBlockCreateSizeMode.setValue,item),                                  
                        rb = _rb)
    except Exception as err:
        log.error("|{0}| failed to load. err: {1}".format(_str_section,err))
        cgmGEN.cgmExceptCB(Exception,err)

def uiOptionMenu_devMode(self, parent, callback = cgmGEN.Callback):
    uiMenu = mc.menuItem( parent = parent, l='Dev Mode:', subMenu=True)
    
    try:self.var_mrsDevMode
    except:self.var_mrsDevMode = cgmMeta.cgmOptionVar('cgmVar_mrsDevMode', defaultValue = 0)

    try:#>>>
        uiRC = mc.radioMenuItemCollection()
        #self.uiOptions_menuMode = []		
        _v = self.var_mrsDevMode.value

        for i,item in enumerate(['off','on']):
            if i == _v: _rb = True
            else:_rb = False            
            mc.menuItem(parent=uiMenu,collection = uiRC,
                        label=item,
                        c = callback(self.var_mrsDevMode.setValue,i),                                  
                        rb = _rb)
    except Exception as err:
        cgmGEN.cgmExceptCB(Exception,err)
    


class uiCallback_withUpdate(object):
    '''
    '''
    def __init__( self, ui, mBlock, func, *a, **kw ):
        self._func = func
        self._args = a
        self._kwargs = kw
        self._ui = ui
        self._mBlock = mBlock
    def __call__( self, *args ):
        try:self._func( *self._args, **self._kwargs )
        except Exception as err:
            try:log.debug("Func: {0}".format(self._func.__name__))
            except:log.debug("Func: {0}".format(self._func))
            if self._ui:
                log.debug("ui: {0}".format(self._ui))
                
            if self._args:
                log.debug("args: {0}".format(self._args))
            if self._kwargs:
                log.debug("kws: {0}".format(self._kwargs))
            for a in err.args:
                log.debug(a)
            raise err 
        
        #if self._mBlock == self._ui._blockCurrent:
            #log.debug("|{0}| resetting active block".format('uiCallback_withUpdate'))            
            #self._ui.uiFunc_block_setActive()
        self._ui.uiScrollList_blocks.rebuild()

    
class cgmScrollList(mUI.BaseMelWidget):
    '''
    
    You'll want to overload:
    rebuild
    update_display
    
    '''
    WIDGET_CMD = mc.iconTextScrollList
    KWARG_CHANGE_CB_NAME = 'sc'

    ALLOW_MULTI_SELECTION = True
    def __new__( cls, parent, *a, **kw ):
        if 'ams' not in kw and 'allowMultiSelection' not in kw:
            kw[ 'ams' ] = cls.ALLOW_MULTI_SELECTION
        return mUI.BaseMelWidget.__new__( cls, parent, *a, **kw )
    
    def __init__( self, parent, *a, **kw ):
        mUI.BaseMelWidget.__init__( self, parent, *a, **kw )
        self._appendCB = None
        self._items = []
        self._ml_scene = []
        self._ml_loaded = []
        self._l_strings = []
        self._l_itc = []
        self._d_itc =  {}
        self.filterField = None
        self.b_selCommandOn = True
        self.rebuild()
        self.cmd_select = None
        self(e=True, sc = self.selCommand)
        
    def __getitem__( self, idx ):
        return self.getItems()[ idx ]

    def setItems( self, items ):
        self.clear()
        for i in items:
            self.append( i )
    def getItems( self ):
        return self._items
        
    def getSelectedItems( self ):
        return self( q=True, si=True ) or []
    
    def getObjIdx(self,Obj):
        if Obj in self._ml_scene:
            return self._ml_scene.index(Obj)
        return None
        
    def getSelectedIdxs( self ):
        return [ idx-1 for idx in self( q=True, sii=True ) or [] ]
        
    def selectByIdx( self, idx ):
        self( e=True, selectIndexedItem=idx+1 )  #indices are 1-based in mel land - fuuuuuuu alias!!!

    def selectByValue( self, value):
        self( e=True, selectItem=value )
        
    def selectByObj(self,Obj):
        log.debug(cgmGEN.logString_start('selectByObj'))        
        
        ml = VALID.listArg(Obj)
        _cleared = False
        for Obj in ml:
            if Obj in self._ml_loaded:
                if not _cleared:
                    self.clearSelection()
                    _cleared = True
                self.selectByIdx(self._ml_loaded.index(Obj))
                self.setHLC(Obj)
            
    def getSelectedObjs( self):
        log.debug(cgmGEN.logString_start('getSelectedObjs'))                
        _indicesRaw = self.getSelectedIdxs()
        if not _indicesRaw:
            log.debug("Nothing selected")
            return []
        _indices = []
        for i in _indicesRaw:
            _indices.append(int(str(i).split('L')[0]))
        return [self._ml_loaded[i] for i in _indices]

    def append( self, item ):
        self( e=True, append=item )
        self._items.append(item)
        
    def appendItems( self, items ):
        for i in items: self.append( i )
 
    def allowMultiSelect( self, state ):
        self( e=True, ams=state )
    
    def report(self):
        log.debug(cgmGEN.logString_start('report'))                
        log.info("Scene: "+cgmGEN._str_subLine)
        for i,mObj in enumerate(self._ml_scene):
            print(("{0} | {1} | {2}".format(i,self._l_strings[i],mObj)))
            
        log.info("Loaded "+cgmGEN._str_subLine)
        for i,mObj in enumerate(self._ml_loaded):
            print(("{0} | {1}".format(i, mObj)))
            
        pprint.pprint(self._ml_scene)
        
    def set_selCallBack(self,func,*args,**kws):
        log.debug(cgmGEN.logString_start('set_selCallBack'))                
        self.selCommand = func
        self.selArgs = args
        self.selkws = kws
    
    def setHLC(self,mObj=None):
        log.debug(cgmGEN.logString_start('setHLC'))        
        if mObj:
            try:
                _color = self._d_itc[mObj]
                log.debug("{0} | {1}".format(mObj,_color))
                _color = [v*.7 for v in _color]
                self(e =1, hlc = _color)
                return
            except:pass
            try:self(e =1, hlc = [.5,.5,.5])
            except:pass
            
    def selCommand(self):
        log.debug(cgmGEN.logString_start('selCommand'))
        l_indices = self.getSelectedIdxs()
        if self.b_selCommandOn and self.cmd_select:
            if len(l_indices)>=1:
                return self.cmd_select()
        return False
    
    def rebuild( self ):
        pass

    def clear( self ):
        log.debug(cgmGEN.logString_start('clear'))                
        self( e=True, ra=True )
        self._l_str_loaded = []
        self._ml_loaded = []
        
    def clearSelection( self,):
        self( e=True, deselectAll=True )
    def set_filterObj(self,obj=None):
        self.filterField = obj

    def update_display(self,searchFilter='',matchCase = False):
        pass
    
    def func_byObj(self,func,*args,**kws):
        try:
            for mObj in self.getSelectedObjs():
                try:
                    res = func( *args, **kws )
                except Exception as err:
                    try:log.debug("Func: {0}".format(_func.__name__))
                    except:log.debug("Func: {0}".format(_func))
      
                    if args:
                        log.debug("args: {0}".format(args))
                    if kws:
                        log.debug("kws: {0}".format(kws))
                    for a in err.args:
                        log.debug(a)
                    raise err 
        except:pass
        finally:
            self.rebuild()
            
    def selectCallBack(self,func=None,*args,**kws):
        print((self.getSelectedObjs()))


class BlockScrollListBAK(mUI.BaseMelWidget):
    '''
    NOTE: you probably want to use the MelObjectScrollList instead!
    '''
    WIDGET_CMD = mc.iconTextScrollList
    KWARG_CHANGE_CB_NAME = 'sc'

    ALLOW_MULTI_SELECTION = True
    def __new__( cls, parent, *a, **kw ):
        if 'ams' not in kw and 'allowMultiSelection' not in kw:
            kw[ 'ams' ] = cls.ALLOW_MULTI_SELECTION
        return mUI.BaseMelWidget.__new__( cls, parent, *a, **kw )
    
    def __init__( self, parent, *a, **kw ):
        mUI.BaseMelWidget.__init__( self, parent, *a, **kw )
        self._appendCB = None
        self._items = []
        self._ml_scene = []
        self._ml_loaded = []
        self._l_strings = []
        self._l_itc = []
        self._d_itc =  {}
        self.filterField = None
        self.b_selCommandOn = True
        self.rebuild()
        self.cmd_select = None
        self(e=True, sc = self.selCommand)
        
    def __getitem__( self, idx ):
        return self.getItems()[ idx ]

    def setItems( self, items ):
        self.clear()
        for i in items:
            self.append( i )
    def getItems( self ):
        return self._items
        
    def getSelectedItems( self ):
        return self( q=True, si=True ) or []
        
    def getSelectedIdxs( self ):
        return [ idx-1 for idx in self( q=True, sii=True ) or [] ]
        
    def selectByIdx( self, idx ):
        self( e=True, selectIndexedItem=idx+1 )  #indices are 1-based in mel land - fuuuuuuu alias!!!

    def selectByValue( self, value):
        self( e=True, selectItem=value )
        
    def selectByBlock(self,Block):
        log.debug(cgmGEN.logString_start('selectByBlock'))        
        
        ml = VALID.listArg(Block)
        _cleared = False
        for Block in ml:
            if Block in self._ml_loaded:
                if not _cleared:
                    self.clearSelection()
                    _cleared = True
                self.selectByIdx(self._ml_loaded.index(Block))
                self.setHLC(Block)
            
    def getSelectedBlocks( self):
        log.debug(cgmGEN.logString_start('getSelectedBlocks'))                
        _indicesRaw = self.getSelectedIdxs()
        if not _indicesRaw:
            log.debug("Nothing selected")
            return []
        _indices = []
        for i in _indicesRaw:
            _indices.append(int(str(i).split('L')[0]))
        return [self._ml_loaded[i] for i in _indices]

    def append( self, item ):
        self( e=True, append=item )
        self._items.append(item)
        
    def appendItems( self, items ):
        for i in items: self.append( i )
        
    #def removeByIdx( self, idx ):
        #self( e=True, removeIndexedItem=idx+1 )
    #def removeByValue( self, value ):
        #self( e=True, removeItem=value )
    #def removeSelectedItems( self ):
        #for idx in self.getSelectedIdxs():
            #self.removeByIdx( idx )
        
    def allowMultiSelect( self, state ):
        self( e=True, ams=state )
    
    def report(self):
        log.debug(cgmGEN.logString_start('report'))                
        log.info("Scene: "+cgmGEN._str_subLine)
        for i,mObj in enumerate(self._ml_scene):
            print(("{0} | {1} | {2}".format(i,self._l_strings[i],mObj)))
            
        log.info("Loaded "+cgmGEN._str_subLine)
        for i,mObj in enumerate(self._ml_loaded):
            print(("{0} | {1}".format(i, mObj)))
            
        pprint.pprint(self._ml_scene)
        
    def set_selCallBack(self,func,*args,**kws):
        log.debug(cgmGEN.logString_start('set_selCallBack'))                
        self.selCommand = func
        self.selArgs = args
        self.selkws = kws
    
    def setHLC(self,mBlock=None):
        log.debug(cgmGEN.logString_start('setHLC'))        
        if mBlock:
            try:
                _color = self._d_itc[mBlock]
                log.debug("{0} | {1}".format(mBlock,_color))
                _color = [v*.7 for v in _color]
                self(e =1, hlc = _color)
                return
            except:pass
            try:self(e =1, hlc = [.5,.5,.5])
            except:pass
            
    def selCommand(self):
        log.debug(cgmGEN.logString_start('selCommand'))
        l_indices = self.getSelectedIdxs()
        if self.b_selCommandOn and self.cmd_select:
            if len(l_indices)<=1:
                return self.cmd_select()
        return False
    
    def rebuild( self ):
        _str_func = 'rebuild'
        log.debug(cgmGEN.logString_start(_str_func))
        self.b_selCommandOn = False
        ml_sel = self.getSelectedBlocks()
        self( e=True, ra=True )
        
        try:self(e =1, hlc = [.5,.5,.5])
        except:pass        
        
        self._items = []
        self._ml_scene = []
        self._ml_loaded = []
        self._l_strings = []
        self._l_str_loaded = []
        self._l_itc = []
        self._d_itc  = {}
        #...
        _ml,_l_strings = BLOCKGEN.get_uiScollList_dat(showSide=1,presOnly=1)
        
        self._ml_scene = _ml
        self._l_itc = []
        
        d_colors = {'left':[.5,.5,1],
                    'right':[.8,.5,.5],
                    'center':[.8,.8,0]}
        
        def getString(pre,string):
            i = 1
            _check = ''.join([pre,string])
            while _check in self._l_strings and i < 100:
                _check = ''.join([pre,string,' | NAMEMATCH [{0}]'.format(i)])
                i +=1
            return _check
        
        for i,mBlock in enumerate(_ml):
            _arg = mBlock.getEnumValueString('blockState')
            _color = d_state_colors.get(_arg,d_colors['center'])
            self._l_itc.append(_color)            
            self._d_itc[mBlock] = _color
            try:_str_base = mBlock.UTILS.get_uiString(mBlock)
            except:_str_base = 'FAIL | {0}'.format(mBlock.mNode)
            _pre = _l_strings[i]
            self._l_strings.append(getString(_pre,_str_base))
            
        self.update_display()
        
        if ml_sel:
            try:self.selectByBlock(ml_sel)
            except Exception as err:
                print(err)
                
        self.b_selCommandOn = True

    def clear( self ):
        log.debug(cgmGEN.logString_start('clear'))                
        self( e=True, ra=True )
        self._l_str_loaded = []
        self._ml_loaded = []
        
    def clearSelection( self,):
        self( e=True, deselectAll=True )
    def set_filterObj(self,obj=None):
        self.filterField = obj

    def update_display(self,searchFilter='',matchCase = False):
        _str_func = 'update_display'
        log.debug(cgmGEN.logString_start(_str_func))
        
        l_items = self.getSelectedItems()
        
        if self.filterField is not None:
            searchFilter = self.filterField.getValue()
        
        self.clear()
        try:
            for i,strEntry in enumerate(r9Core.filterListByString(self._l_strings,
                                                                  searchFilter,
                                                                  matchcase=matchCase)):
                if strEntry in self._l_str_loaded:
                    log.warning("Duplicate string")
                    continue
                self.append(strEntry)
                self._l_str_loaded.append(strEntry)
                idx = self._l_strings.index(strEntry)
                _mBlock = self._ml_scene[idx]
                self._ml_loaded.append(_mBlock)
                _color = d_state_colors.get(_mBlock.getEnumValueString('blockState'))
                try:self(e=1, itc = [(i+1,_color[0],_color[1],_color[2])])
                except:pass

        except Exception as err:
            log.error("|{0}| >> err: {1}".format(_str_func, err))  
            for a in err:
                log.error(a)
        
        #if l_items:
            #try:self.selectByValue(l_items)
            #except Exception,err:
                #print err
    
    def func_byBlock(self,func,*args,**kws):
        try:
            for mBlock in self.getSelectedBlocks():
                try:
                    res = func( *args, **kws )
                except Exception as err:
                    try:log.debug("Func: {0}".format(_func.__name__))
                    except:log.debug("Func: {0}".format(_func))
      
                    if args:
                        log.debug("args: {0}".format(args))
                    if kws:
                        log.debug("kws: {0}".format(kws))
                    for a in err.args:
                        log.debug(a)
                    raise err 
        except:pass
        finally:
            self.rebuild()
            
    def selectCallBack(self,func=None,*args,**kws):
        print((self.getSelectedBlocks()))
        
        
        
class BlockScrollList(cgmScrollList):
    '''
    NOTE: you probably want to use the MelObjectScrollList instead!
    '''
    WIDGET_CMD = mc.iconTextScrollList
    KWARG_CHANGE_CB_NAME = 'sc'

    ALLOW_MULTI_SELECTION = True
    def __new__( cls, parent, *a, **kw ):
        if 'ams' not in kw and 'allowMultiSelection' not in kw:
            kw[ 'ams' ] = cls.ALLOW_MULTI_SELECTION
        return mUI.BaseMelWidget.__new__( cls, parent, *a, **kw )
    
    def __init__( self, parent, *a, **kw ):
        #cgmScrollList.__init__( self, parent, *a, **kw )
        self.mActive = None
        
        super(BlockScrollList, self).__init__(parent, *a, **kw)
        
        #from cgm import images as cgmImagesFolder
        #_path_imageFolder = CGMPATH.Path(cgmImagesFolder.__file__).up().asFriendly()
        #_path_image = os.path.join(_path_imageFolder,'cgmonastery_uiFooter_gray.png')
        
        #self(e=True, ebg=True, bgc=[.5,.5,.5])

    
    def rebuild( self ):
        _str_func = 'rebuild'
        log.debug(cgmGEN.logString_start(_str_func))
        self.b_selCommandOn = False
        ml_sel = self.getSelectedObjs()
        self( e=True, ra=True )
        
        try:self(e =1, hlc = [.5,.5,.5])
        except:pass        
        
        self._items = []
        self._ml_scene = []
        self._ml_loaded = []
        self._l_strings = []
        self._l_str_loaded = []
        self._l_itc = []
        self._d_itc  = {}
        #...
        _ml,_l_strings = BLOCKGEN.get_uiScollList_dat(showSide=1,presOnly=1)
        
        self._ml_scene = _ml
        self._l_itc = []
        
        d_colors = {'left':[.5,.5,1],
                    'right':[.8,.5,.5],
                    'center':[.8,.8,0]}
        
        def getString(pre,string):
            i = 1
            _check = ''.join([pre,string])
            while _check in self._l_strings and i < 100:
                _check = ''.join([pre,string,' | NAMEMATCH [{0}]'.format(i)])
                i +=1
            return _check
        
        for i,mBlock in enumerate(_ml):
            _arg = mBlock.getEnumValueString('blockState')
            _color = d_state_colors.get(_arg,d_colors['center'])
            self._l_itc.append(_color)            
            self._d_itc[mBlock] = _color
            try:_str_base = mBlock.UTILS.get_uiString(mBlock)
            except:_str_base = 'FAIL | {0}'.format(mBlock.mNode)
            _pre = _l_strings[i]
            if self.mActive == mBlock:
                _pre = _pre + "[A] "
            self._l_strings.append(getString(_pre,_str_base))
            
        self.update_display()
        
        if ml_sel:
            try:self.selectByObj(ml_sel)
            except Exception as err:
                print(err)
                
        self.b_selCommandOn = True
        
    def update_display(self,searchFilter='',matchCase = False):
        _str_func = 'update_display'
        log.debug(cgmGEN.logString_start(_str_func))
        
        l_items = self.getSelectedItems()
        
        if self.filterField is not None:
            searchFilter = self.filterField.getValue()
        
        self.clear()
        try:
            for i,strEntry in enumerate(r9Core.filterListByString(self._l_strings,
                                                                  searchFilter,
                                                                  matchcase=matchCase)):
                if strEntry in self._l_str_loaded:
                    log.warning("Duplicate string")
                    continue
                self.append(strEntry)
                self._l_str_loaded.append(strEntry)
                idx = self._l_strings.index(strEntry)
                _mBlock = self._ml_scene[idx]
                self._ml_loaded.append(_mBlock)
                _color = d_state_colors.get(_mBlock.getEnumValueString('blockState'))
                try:self(e=1, itc = [(i+1,_color[0],_color[1],_color[2])])
                except:pass

        except Exception as err:
            log.error("|{0}| >> err: {1}".format(_str_func, err))  
            for a in err:
                log.error(a)

        
#Frames =====================================================================================
def buildFrame_mirror(self,parent):
    _str_func = 'buildFrame_mirror'
    log.debug(cgmGEN.logString_start(_str_func))
    
    try:self.var_builder_mirrorFrameCollapse
    except:self.create_guiOptionVar('builder_mirrorFrameCollapse',defaultValue = 0)
    mVar_frame = self.var_builder_mirrorFrameCollapse
    
    _frame = mUI.MelFrameLayout(parent,label = 'Mirror',vis=True,
                                collapse=mVar_frame.value,
                                collapsable=True,
                                enable=True,
                                #ann='Contextual MRS functionality',
                                useTemplate = 'cgmUIHeaderTemplate',
                                expandCommand = lambda:mVar_frame.setValue(0),
                                collapseCommand = lambda:mVar_frame.setValue(1)
                                )	
    _inside = mUI.MelColumnLayout(_frame,useTemplate = 'cgmUISubTemplate') 
    
    
    log.debug("|{0}| >> mirror ...".format(_str_func)+ '-'*40)
    mc.setParent(_inside)                
    _row = mUI.MelHSingleStretchLayout(_inside,ut='cgmUISubTemplate',padding = 5)
    mUI.MelSpacer(_row,w=1)
    
    mUI.MelLabel(_row,l="Mirror: ")
    _row.setStretchWidget( mUI.MelSeparator(_row) )
    mc.button(parent=_row,
              l = 'Build',
              ut = 'cgmUITemplate',
              c = cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                  'atUtils','blockMirror_create',
                                  **{}),
              ann = 'Verify block mirrors. WARNING - do not do this with a block and its mirror selected')
    mc.button(parent=_row,
              l = 'Rebuild',
              ut = 'cgmUITemplate',
              c = cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                  'atUtils','blockMirror_create',True,
                                  **{}),
              ann = 'Rebuild mirror block from scratch. WARNING - do not do this with a block and its mirror selected')
    
    
    mc.button(parent=_row,
              l = 'Push',
              ut = 'cgmUITemplate',
              c = cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                  'atUtils','blockMirror_go',
                                  **{'mode':'push','updateUI':0}),
              ann = 'Push setup to the mirror')
    mc.button(parent=_row,
              l = 'Pull',
              ut = 'cgmUITemplate',
              c = cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                  'atUtils','blockMirror_go',
                                  **{'mode':'pull','updateUI':0}),
              ann = 'pull setup to the mirror')
    mUI.MelSpacer(_row,w=5)
    
    mc.button(parent=_row,
              l = 'Self[L]',
              ut = 'cgmUITemplate',
              c = cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                  'atUtils','mirror_self',
                                  **{'primeAxis':'left','updateUI':0}),
              ann = 'Mirror self - Left Prime Axis')
    mc.button(parent=_row,
              l = 'Self[R]',
              ut = 'cgmUITemplate',
              c = cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                  'atUtils','mirror_self',
                                  **{'primeAxis':'right','updateUI':0}),
              ann = 'Mirror self - Righ Prime Axis')        
    mUI.MelSpacer(_row,w=1)
    _row.layout()
    
    #....
    _row = mUI.MelHLayout(_inside,ut='cgmUISubTemplate',padding = 5)
    #mUI.MelSpacer(_row,w=1)
    
    #mUI.MelLabel(_row,l="Settings: ")
    #_row.setStretchWidget( mUI.MelSeparator(_row) )
    mc.button(parent=_row,
              l = 'Settings | Push',
              ut = 'cgmUITemplate',
              c = cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                  'atUtils','blockMirror_settings',
                                  **{'updateUI':True,'mode':'push'}),
              ann = 'Mirror block controls in context | push')
    mc.button(parent=_row,
              l = 'Settings | Pull',
              ut = 'cgmUITemplate',
              c = cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                  'atUtils','blockMirror_settings',
                                  **{'updateUI':True,'mode':'pull'}),
              ann = 'Mirror block controls in context | pull')
    #mUI.MelSpacer(_row,w=1)
    _row.layout()        
    
    
    
    
    
#Frames =====================================================================================
def buildFrame_blockDat(self,parent):
    _str_func = 'buildFrame_blockDat'
    log.debug(cgmGEN.logString_start(_str_func))
    
    try:self.var_builder_blockDatFrameCollapse
    except:self.create_guiOptionVar('builder_blockDatFrameCollapse',defaultValue = 0)
    mVar_frame = self.var_builder_blockDatFrameCollapse
    
    _frame = mUI.MelFrameLayout(parent,label = 'BlockDat',vis=True,
                                collapse=mVar_frame.value,
                                collapsable=True,
                                enable=True,
                                #ann='Contextual MRS functionality',
                                useTemplate = 'cgmUIHeaderTemplate',
                                expandCommand = lambda:mVar_frame.setValue(0),
                                collapseCommand = lambda:mVar_frame.setValue(1)
                                )	
    _inside = mUI.MelColumnLayout(_frame,useTemplate = 'cgmUISubTemplate') 
    
    
    #BlcokDat ======================================================
    log.debug("|{0}| >> Blockdat ...".format(_str_func)+ '-'*40)
    mc.setParent(_inside)
    _row = mUI.MelHSingleStretchLayout(_inside,ut='cgmUISubTemplate',padding = 5)
    
    mUI.MelSpacer(_row,w=1)
    mUI.MelLabel(_row,l="General: ")        
    _row.setStretchWidget( mUI.MelSeparator(_row) )
    
    
    mc.button(parent=_row,
              l = 'Save',
              ut = 'cgmUITemplate',
              c = cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                  'saveBlockDat',
                                  **{'updateUI':0}),
              ann = self._d_ui_annotations.get('save blockDat'))
    mc.button(parent=_row,
              l = 'Load',
              ut = 'cgmUITemplate',
              c = cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                  'loadBlockDat',
                                  **{}),
              ann = self._d_ui_annotations.get('load blockDat'))
    
    mc.button(parent=_row,
              l = 'Load Current',
              ut = 'cgmUITemplate',
              c = cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                  'loadBlockDat',
                                  **{'autoPush':False,'currentOnly':True}),
              ann = self._d_ui_annotations.get('load state blockDat'))
    
    mc.button(parent=_row,
              l = 'Query',
              ut = 'cgmUITemplate',
              c = cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                  'getBlockDat',
                                  **{'updateUI':0}),
              ann = self._d_ui_annotations.get('get blockDat'))
    
    mc.button(parent=_row,
              l = 'Transfer',
              ut = 'cgmUITemplate',
              c = cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                  'atUtils','blockDat_copy',
                                  **{'mode':'blockDatCopyActive'}),
              ann = "Tranfer the active blocks data")
    
    mc.button(parent=_row,
              l = 'Reset',
              ut = 'cgmUITemplate',
              c = cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                  'atUtils','blockDat_reset',
                                  **{'updateUI':0}),
              ann = self._d_ui_annotations.get('reset blockDat'))        
    
    mUI.MelSpacer(_row,w=1)
    _row.layout()
    

    #State Load ======================================================
    log.debug("|{0}| >> Load State ...".format(_str_func)+ '-'*40)
    mc.setParent(_inside)
    _row = mUI.MelHSingleStretchLayout(_inside,ut='cgmUISubTemplate',padding = 5)
    
    mUI.MelSpacer(_row,w=1)
    mUI.MelLabel(_row,l="Load State: ")        
    _row.setStretchWidget( mUI.MelSeparator(_row) )
    
    for state in ['define','form','prerig']:
        mc.button(parent=_row,
                  l = state,
                  ut = 'cgmUITemplate',
                  c = cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                      'atUtils','blockDat_load_state',state,
                                      **{}),
                  ann="Load {0} blockDat in context".format(state),)
 
    mUI.MelSpacer(_row,w=1)
    _row.layout()    

#Frames =====================================================================================
def buildFrame_blockEditor(self,parent):
    _str_func = 'buildFrame_blockEditor'
    log.debug(cgmGEN.logString_start(_str_func))
    
    try:self.var_builder_blockEditorFrameCollapse
    except:self.create_guiOptionVar('builder_blockEditorFrameCollapse',defaultValue = 0)
    mVar_frame = self.var_builder_blockEditorFrameCollapse
    """
    _frame = mUI.MelFrameLayout(parent,label = 'Edit Active',vis=True,
                                collapse=mVar_frame.value,
                                collapsable=True,
                                enable=True,
                                #ann='Contextual MRS functionality',
                                useTemplate = 'cgmUIHeaderTemplate',
                                expandCommand = lambda:mVar_frame.setValue(0),
                                collapseCommand = lambda:mVar_frame.setValue(1)
                                )	"""
    _inside = mUI.MelColumn(parent,useTemplate = 'cgmUITemplate')
    self.uiBlock_edit = _inside
    
def uiFunc_updateBlock(self):
    _str_func = ' uiFunc_updateBlock'
    log.debug("|{0}| >> mBlock: {1}".format(_str_func,self.mBlock))
    
    self.uiBlock_edit.clear()
    
    mBlock = self.mBlock
    
    if not mBlock:
        return log.error("Cannot load block. None wired")
    
    _short = mBlock.mNode

    
    #mParent = mBlock.p_blockParent
    #mChildren = mBlock.getBlockChildren() or []
    #mSiblings = mBlock.atUtils('siblings_get') or []
    #mMirror = mBlock.getMessageAsMeta('blockMirror')
    
    self.d_BlockStrings = {}
    
    """
    for mList in mChildren,mSiblings:
        mList = LISTS.get_noDuplicates(mList)
        mTmp = {}
        l_keys = []
        for mObj in mList:
            _key = mObj.UTILS.get_uiString(mObj)
            mTmp[_key] = mObj
            l_keys.append(_key)
            self.d_BlockStrings[mObj] = _key 
        
        l_keys.sort()
        mList = [mTmp[k] for k in l_keys]
    """
    #self.mParent = mParent
    #self.mChildren = mChildren
    #self.mSiblings = mSiblings
    #self.mMirror = mMirror
    
    _l_report = []
    if self._blockCurrent.hasAttr('buildProfile'):
        _l_report.insert(0,str(self._blockCurrent.buildProfile))
    #if ATTR.get(_short,'side'):
        #_l_report.append( ATTR.get_enumValueString(_short,'side'))
    if ATTR.has_attr(_short,'blockProfile'):
        _l_report.append("{0} - {1}".format(self._blockCurrent.blockProfile,
                                            self._blockCurrent.blockType))
    else:
        _l_report.append("{0}".format(self._blockCurrent.blockType))                
    
    
    if self._blockCurrent.isReferenced():
        _l_report.insert(0,"Referenced!")
    
    mUI.MelLabel(self.uiBlock_edit, l = ' | '.join(_l_report))
    

    
    _d = self.mBlock.atUtils('uiQuery_getStateAttrDict',0,0)
    
    self._d_attrFields = {}
    
    
    _keys = sorted(_d)
    l_order =['define','profile','basic','name',
              'form','proxySurface','prerig',
              'skeleton',
              'rig','space','squashStretch']
    l_order.reverse()
    
    for k in l_order:
        if k in _keys:
            _keys.remove(k)
            _keys.insert(0,k)
            
    l_end = ['data','wiring','advanced']
    for k in l_end:
        if k in _keys:
            _keys.remove(k)
            _keys.append(k)        
    
    
    d_keyColors = {'profile':'define',
                   'basic':'define',
                   'name':'define',
                   'proxySurface':'form',
                   'squashStretch':'rig',
                   'space':'rig',
                   'post':'rig'}
    
    for k in _keys:
        log.debug(cgmGEN.logString_sub(_str_func,k))                
        
        l = _d.get(k)
        if not l:
            log.debug("|{0}| >> No attrs in : {1}".format(_str_func,k))                
            continue
        
        try:self.__dict__['var_{0}FrameCollapse'.format(k)]
        except:self.create_guiOptionVar('{0}FrameCollapse'.format(k),defaultValue = 0)
        
        mVar_frame = self.__dict__['var_{0}FrameCollapse'.format(k)]
        
        _frame = mUI.MelFrameLayout(self.uiBlock_edit,label = CORESTRINGS.capFirst(k),vis=True,
                                    collapse=mVar_frame.value,
                                    collapsable=True,
                                    enable=True,
                                    marginWidth = 5,
                                    useTemplate = 'cgmUIHeaderTemplate',
                                    expandCommand = cgmGEN.Callback(mVar_frame.setValue,0),
                                    collapseCommand =  cgmGEN.Callback(mVar_frame.setValue,1),
                                    statusBarMessage = k,
                                    )	
        _inside = mUI.MelColumnLayout(_frame,
                                      #rowSpacing = 5,
                                      useTemplate = 'cgmUISubTemplate')
        
        
        _sub_bgc = d_keyColors.get(k)
        if _sub_bgc: 
            _d_uiColors = d_uiStateUIColors.get(_sub_bgc)
        else:
            _d_uiColors = d_uiStateUIColors.get(k) or d_uiStateUIColors.get('default')
            
        _clr_header = _d_uiColors['base']
        _clr_bg = _d_uiColors['bgc']
        _clr_light =  _d_uiColors['light']
        _clr_button = _d_uiColors['button']
        
        if _sub_bgc:
            _clr_header = [v*.6 for v in _clr_header]
        """
        _clr_header = [1,1,1]
        _sub_bgc = d_keyColors.get(k)
        if _sub_bgc: 
            _clr_header = d_uiStateSubColors.get(_sub_bgc)
            _clr_header = [v*.6 for v in _clr_header]
        else:
            _clr_header = d_uiStateSubColors.get(k,[.5,.5,.5])
            _clr_header = [v*.8 for v in _clr_header]
            
        if _clr_header:
            _frame(edit=1, bgc=_clr_header)
        
        _clr_bg = [v*.4 for v in _clr_header]
        _clr_light = [v*4.0 for v in _clr_header]
            
        _inside(edit=1, bgc =  [v*.6 for v in _clr_header])

            """
        _frame(edit=1, bgc=_clr_header)
        _inside(edit=1, bgc =  _clr_bg)
        
        
        mUI.MelSpacer(_inside,h=5)

        
        if k == 'name':#Name section....-------------------------------------------------
            log.debug("|{0}| >> Name...".format(_str_func))
            _nameIter = mBlock.hasAttr('nameIter')
            if _nameIter:
                mUI.MelLabel(_inside,l = "Tag: {0} | Iterator: {1}".format(mBlock.getMayaAttr('cgmName'),
                                                                           mBlock.getMayaAttr('nameIter')),
                             bgc = _clr_light,#ut ='cgmUIInstructionsTemplate' ,
                             )
            else:
                mUI.MelLabel(_inside,l = "Tag: {0}".format(mBlock.getMayaAttr('cgmName')),
                             bgc = _clr_light,#ut ='cgmUIInstructionsTemplate' ,
                             )                    

            #Base name stuff...
            _mRow = mUI.MelHLayout(_inside,ut='cgmUISubTemplate',padding = 2)
            
            mUI.MelButton(_mRow,
                          label='Tag',bgc = _clr_button, #ut='cgmUITemplate',
                          c = cgmGEN.Callback(uiFunc_blockCall,self,
                                              'atUtils','set_nameTag', **{}),
                          ann='Change nameTag')
            if _nameIter:
                mUI.MelButton(_mRow,
                              label='NameIter',bgc = _clr_button, #ut='cgmUITemplate',
                              c = cgmGEN.Callback(uiFunc_blockCall,self,
                                                  'atUtils','set_nameIter', **{}),
                              ann='Change iter name')                
            
            _mRow.layout()
            
            
            _nameList = mBlock.datList_get('nameList')
            if _nameList:
                mUI.MelSpacer(_inside,h=5)
                mUI.MelLabel(_inside,l = "{0} | {1}".format(len(_nameList),
                                                            [str(n) for n in _nameList]),
                             bgc = _clr_light,#ut ='cgmUIInstructionsTemplate' ,
                            )
                
                #Namelist...
                mUI.MelSpacer(_inside,h=5)
                
                _mRow = mUI.MelHSingleStretchLayout(_inside)
                mUI.MelSpacer(_mRow,w=_sidePadding)
                
                mUI.MelLabel(_mRow,l='NameList:')
                _mRow.setStretchWidget(mUI.MelSeparator(_mRow,))
                
                _d_nameList = {
                            'Reset':{'ann':'Reset the name list to the profile',
                                           'call':cgmGEN.Callback(uiFunc_blockCall,self,
                                                                  'atUtils','nameList_resetToProfile',
                                                                  **{})},
                            'Edit':{'ann':'Ui Prompt to edit nameList',
                                                'call':cgmGEN.Callback(uiFunc_blockCall,self,
                                                                       'atUtils','nameList_uiPrompt',
                                                                       **{})},                  
                             'Iter baseName':{'ann':'Set nameList values from name attribute',
                                              'call':cgmGEN.Callback(uiFunc_blockCall,self,
                                                                     'atUtils','set_nameListFromName',
                                                                     **{})}}
            
                for k2,d2 in list(_d_nameList.items()):
                    mUI.MelButton(_mRow,
                                 label=k2,bgc = _clr_button,#ut='cgmUITemplate',
                                 ann = d2.get('ann',''),
                                 c=d2.get('call'))
                    
                mUI.MelSpacer(_mRow,w=_sidePadding)
                
                _mRow.layout()
                mUI.MelSpacer(_inside,h=5)

        if k == 'vis':
            #Lock nulls row ------------------------------------------------------------------------
            _mRow_lockNulls = mUI.MelHSingleStretchLayout(_inside,padding = 2)
            mUI.MelSpacer(_mRow_lockNulls,w=_sidePadding)
            
            mUI.MelLabel(_mRow_lockNulls,l='Lock null:')
            _mRow_lockNulls.setStretchWidget(mUI.MelSeparator(_mRow_lockNulls,))
            
            for null in ['formNull','prerigNull']:
                _str_null = mBlock.getMessage(null)
                if _str_null:
                    _nullShort = _str_null[0]
                    mUI.MelCheckBox(_mRow_lockNulls, l="- {0}".format(null),
                                    value = ATTR.get(_nullShort,'template'),
                                    onCommand = cgmGEN.Callback(ATTR.set,_nullShort,'template',1),
                                    offCommand = cgmGEN.Callback(ATTR.set,_nullShort,'template',0))                
                else:
                    mUI.MelCheckBox(_mRow_lockNulls, l="- {0}".format(null),
                                    en=False)
            
            mUI.MelSpacer(_mRow_lockNulls,w=_sidePadding)
            _mRow_lockNulls.layout()                
            
        
        if k == 'profile':
            log.debug("|{0}| >> profile...".format(_str_func))
            
            d_profileDat = {'block':{'options':RIGBLOCKS.get_blockProfile_options(mBlock.blockType),
                                     'current':str(mBlock.getMayaAttr('blockProfile')),
                                     },
                            'build':{'options':BLOCKSHARE._l_buildProfiles,
                                     'current':str(mBlock.getMayaAttr('buildProfile'))}}
            
            
            for k2,d2 in list(d_profileDat.items()):
                _en = True
                _defineOff = False
                if k2 == 'block':
                    if mBlock.blockState != 0:
                        _en = False
                        _defineOff = True
                        
                        
                _mRow = mUI.MelHSingleStretchLayout(_inside,padding = 10)
                mUI.MelLabel(_mRow,l="  {0} > ".format(CORESTRINGS.capFirst(k2)))
                #_mRow.setStretchWidget(mUI.MelSeparator(_mRow,))            

                _optionMenu = mUI.MelOptionMenu(_mRow,bgc = _clr_button,h=25,en=_en)
                
                _mRow.setStretchWidget(_optionMenu)
                
                
                self.__dict__['uiOM_{0}'.format(k2)] = _optionMenu
            
                for option in d2.get('options',[]):
                    _optionMenu.append(option)
                    
                try:_optionMenu.selectByValue(d2['current'])
                except:pass
                
                #mUI.MelLabel(_mRow, bgc=cgmUI.guiBackgroundColorLight,w=50,al='center',en=_en,
                #             l="{0}".format(mBlock.getMayaAttr('{0}Profile'.format(k2))))                    
                
                
                mUI.MelButton(_mRow,en=_en,
                              label='Load',bgc = _clr_button,
                              c = cgmGEN.Callback(uiFunc_profileSet,self,
                                                  k2, **{}),
                              ann='Load {0}Profile'.format(k2))     
                    
                #mUI.MelSpacer(_mRow,w=_sidePadding)                
                _mRow.layout()
                
                if _defineOff:
                    mUI.MelLabel(_inside, bgc=cgmUI.d_stateColors['warning'],
                                 w=75,al='center',
                                 en=_en,
                                 l = "blockType can only be changed in define state")
                
                #mc.setParent(_inside)
                #cgmUI.add_LineSubBreak()
                mUI.MelSpacer(_inside,h=5)
            mUI.MelSpacer(_inside,h=5)
            
                
            continue

            
            for i,item in enumerate(BLOCKSHARE._l_buildProfiles):
                mUI.MelMenuItem(_Profiles, l=item,
                                ann = "Load the following profile",
                                c = cgmGEN.Callback(uiFunc_buildProfile_set,self,**{'buildProfile':item}),
                                )                       
            
            continue
            _nameIter = mBlock.hasAttr('nameIter')
            
            
            if _nameIter:
                mUI.MelLabel(_inside,l = "Tag: {0} | Iterator: {1}".format(mBlock.getMayaAttr('cgmName'),
                                                                           mBlock.getMayaAttr('nameIter')),
                             ut ='cgmUIInstructionsTemplate' ,
                             )
            else:
                mUI.MelLabel(_inside,l = "Tag: {0}".format(mBlock.getMayaAttr('cgmName')),
                             ut ='cgmUIInstructionsTemplate' ,
                             )                    

            #Base name stuff...
            _mRow = mUI.MelHLayout(_inside,ut='cgmUISubTemplate',padding = 2)
            
            mUI.MelButton(_mRow,
                          label='Tag',bgc = _clr_button,#ut='cgmUITemplate',
                          c = cgmGEN.Callback(self.uiFunc_blockCall,
                                              'atUtils','set_nameTag', **{}),
                          ann='Change nameTag')
            if _nameIter:
                mUI.MelButton(_mRow,
                              label='NameIter',bgc = _clr_button, #ut='cgmUITemplate',
                              c = cgmGEN.Callback(self.uiFunc_blockCall,
                                                  'atUtils','set_nameIter', **{}),
                              ann='Change iter name')                
            
            _mRow.layout()                
            continue
        
        #Attrs... ------------------------------------------------------------------------
        for a in l:
            try:
                if a in ['blockState']:
                    continue
                _type = ATTR.get_type(_short,a)
                log.debug("|{0}| >> attr: {1} | {2} | {3}".format(_str_func, k, a, _type))
                
                if k in ['data','wiring']:
                    
                    mUI.MelLabel(_inside,l = "{0} | {1}".format(a, ATTR.get(_short,a)))
                    continue

                _hlayout = mUI.MelHSingleStretchLayout(_inside,padding = 10)
                
               

                #if _type not in ['bool']:#Some labels parts of fields
                mUI.MelLabel(_hlayout,l="  {0} ".format(a))   
    
                #mUI.MelSpacer(_hlayout,w=_sidePadding)
        
                _hlayout.setStretchWidget(mUI.MelSeparator(_hlayout,))
                
                
                d_datLists = {'numSubShapers':{'datList':'numSubShapers',
                                       'defaultAttr':'numSubShapers'},
                              'numRoll':{'datList':'rollCount',
                                         'defaultAttr':'numRoll'},                                  
                      }                    
                if a in ['numSubShapers','numRoll']:

                    mUI.MelButton(_hlayout,
                                 label='Edit datList',bgc = _clr_button,#ut='cgmUITemplate',
                                 #ann = d2.get('ann',''),
                                 c=cgmGEN.Callback(uiFunc_blockCall,self,
                                    'atUtils','datList_validate',
                                    **{'datList':d_datLists[a].get('datList'),
                                       'defaultAttr':d_datLists[a].get('defaultAttr'),
                                       'forceEdit':1}))
                

                if _type == 'bool':
                    mUI.MelCheckBox(_hlayout, l="",
                                    #annotation = "Copy values",		                           
                                    value = ATTR.get(_short,a),
                                    onCommand = cgmGEN.Callback(ATTR.set,_short,a,1),
                                    offCommand = cgmGEN.Callback(ATTR.set,_short,a,0))
        
                elif _type in ['double','doubleAngle','doubleLinear','float']:
                    self._d_attrFields[a] = mUI.MelFloatField(_hlayout,w = 50,
                                                              value = ATTR.get(_short,a),
                                                              )
                    self._d_attrFields[a](e=True,
                                          cc  = cgmGEN.Callback(uiCallback_setAttrFromField,self,_short, a, _type,
                                                                self._d_attrFields[a]),
                                          )
                elif _type == 'long':
                    self._d_attrFields[a] = mUI.MelIntField(_hlayout,w = 50,
                                                             #maxValue=20,
                                                              )
                    self._d_attrFields[a](e=True,value = ATTR.get(_short,a))
                    
                    _min =ATTR.get_min(_short,a) or None
                    if _min is not None:
                        
                        self._d_attrFields[a](e=True,minValue= _min)
                    
                    
                        
                    
                    self._d_attrFields[a](e=True,
                                          cc  = cgmGEN.Callback(uiCallback_setAttrFromField,
                                                                self,_short, a, _type,
                                                                self._d_attrFields[a]),
                                          )                
                elif _type == 'string':
                    self._d_attrFields[a] = mUI.MelTextField(_hlayout,w = 75,
                                                             text = ATTR.get(_short,a),
                                                              )
                    self._d_attrFields[a](e=True,
                                          cc  = cgmGEN.Callback(uiCallback_setAttrFromField,self,_short, a, _type,
                                                                self._d_attrFields[a]),
                                          )
                elif _type == 'enum':
                    _optionMenu = mUI.MelOptionMenu(_hlayout,bgc = _clr_button)#ut = 'cgmUITemplate')
                    _optionMenu(e=True,
                                cc = cgmGEN.Callback(uiCallback_setAttrFromField,self,_short, a, _type,
                                                     _optionMenu),) 
                    for option in ATTR.get_enumList(_short,a):
                        _optionMenu.append(option)
                    _optionMenu.setValue(ATTR.get_enumValueString(_short,a))
                else:
                    mUI.MelLabel(_hlayout,l="{0}({1}):{2}".format(a,_type,ATTR.get(_short,a)))        
                    
                    
                #mUI.MelSpacer(_hlayout,w=_sidePadding)                
                _hlayout.layout()
            except Exception as err:
                log.warning("Attr {0} | {1} | failed. err: {2}".format(a,_type, err))
                
                
def uiCallback_setAttrFromField(self, obj, attr, attrType, field):
    _v = field.getValue()
    ATTR.set(obj,attr,_v)
    
    if attrType == 'enum':
        _strValue = ATTR.get_enumValueString(obj,attr)
        field.setValue(_strValue)
        
        if attr == 'buildProfile':
            log.info("Loading buildProfile...")
            self._blockCurrent.atUtils('buildProfile_load',_strValue)
        if attr == 'blockProfile':
            log.info("Loading blockProfile...")
            self._blockCurrent.atUtils('blockProfile_load',_strValue)                
    else:
        field.setValue(ATTR.get(obj,attr))
        
    if attr == 'numRoll':
        log.info("numRoll check...")                            
        if ATTR.datList_exists(obj,'rollCount'):
            log.info("rollCount Found...")                                            
            l = ATTR.datList_getAttrs(obj,'rollCount')
            for a in l:
                log.info("{0}...".format(a))                                                
                ATTR.set(obj,a, _v)
            
    if attr in ['numShapers','neckShapers']:
        log.info("loftList verify check...")
        self.mBlock.UTILS.verify_loftList(self.mBlock,_v)
        mc.evalDeferred(cgmGEN.Callback(uiFunc_updateBlock,self),lp=True)
            #self.uiUpdate_blockDat()
            
    if attr == 'loftShape':
        log.info("loftShape push to list...")            
        for a in ATTR.datList_getAttrs(obj,'loftList'):
            ATTR.set(obj,a,_v)
        mc.evalDeferred(cgmGEN.Callback(uiFunc_updateBlock,self),lp=True)
    
    if attr in ['numJoints','neckJoints'] or attr.startswith('rollCount'):
        log.info(attr)            
        self.mBlock.atBlockModule('create_jointHelpers',force=True)
        log.info("Updated jointHelpers")            
            
    
    log.info("Set: {0} | {1} | {2}".format(obj,attr,_v))

def uiFunc_profileSet(self,mode = 'build',**kws):
    _str_func = ''
    _updateUI = kws.pop('updateUI',True)
    _profile = kws.pop('buildProfile',None)
    
    _profile = self.__dict__['uiOM_{0}'.format(mode)].getValue()
    
    #if not _profile:
    #    return log.error("|{0}| >> blockProfile arg".format(_str_func))
    
    log.info("Setting Profile: {0} | {1}".format(mode,_profile))
    
    if mode == 'build':
        uiFunc_blockCall(self,'atUtils','buildProfile_load',_profile)
    elif mode == 'block':
        uiFunc_blockCall(self,'atUtils','blockProfile_load',_profile)
    else:
        return log.error("Unknown Profile mode: {0}".format(mode))

    return

def uiFunc_blockCall(self,*args,**kws):
    try:
        if not self.mBlock:
            return
        mBlock = self.mBlock
        
        b_update = kws.pop('updateUI',True)
        
        mc.refresh(su=1)
        _sel = mc.ls(sl=1)
        if _sel:
            mc.select(cl=1)

        _str_func = ''
        log.info(cgmGEN._str_hardBreak)
        
        _mode = kws.get('mode')

        if _mode == 'setParentToSelected':
            mSelectedBlock = BLOCKGEN.block_getFromSelected()
            if not mSelectedBlock:
                return log.error("|{0}| >> mode: {1} requires selected block".format(_str_func,_mode)) 
            kws['parent'] = mSelectedBlock
            kws.pop('mode')
                
            
        #elif  _mode == 'clearParentBlock':
        #else:
            #raise ValueError,"Mode not setup: {0}".format(_mode)            
        b_devMode = False
        b_dupMode = False
        b_changeState = False
        b_rootMode = False
        if args[0] == 'changeState':
            kws['forceNew'] = True
            kws['checkDependency'] = True


        if args[0] == 'VISUALIZEHEIRARCHY':
            BLOCKGEN.get_rigBlock_heirarchy_context(mBlock,_contextMode,False,True)
            return True
        elif args[0]== 'focus':
            log.debug("|{0}| >> Focus call".format(_str_func))
            #ml_root = BLOCKGEN.get_rigBlock_heirarchy_context(ml_blocks,'root',True,False)
            #for mBlock in ml_blocks:
            log.info("|{0}| >> Focus call | {1}".format(_str_func,mBlock))                    
            mBlock.UTILS.focus(mBlock,args[1],args[2],ml_focus=[])
            return
        
        #Now parse to sets of data
        if args[0] == 'select':
            #log.info('select...')
            return mc.select(mBlock.mNode)

        ml_res = []
        md_dat = {}
        md_datRev = {}
        
        _short = mBlock.p_nameShort
        _call = str(args[0])
        if _call in ['atUtils']:
            _call = str(args[1])
        
        #pprint.pprint(locals())
        res = getattr(mBlock,args[0])(*args[1:],**kws) or None
        
        ml_res.append(res)
        if res:
            if kws.get('mode') not in ['prechecks']:
                pprint.pprint(res)
                
        if b_update:
            try:self.uiFunc_updateStatus()
            except:pass
            
            if UI:
                UI.uiScrollList_blocks.rebuild()

        if _sel:
            try:mc.select(_sel)
            except:pass
            
    #except Exception,err:
    #    cgmGEN.cgmExceptCB(Exception,err)
    finally:
        mc.refresh(su=0)
        
        
class ui_createBlock(CGMUI.cgmGUI):
    USE_Template = 'cgmUITemplate'
    WINDOW_NAME = "BlockCreate"
    WINDOW_TITLE = 'BlockCreate | {0}'.format(__version__)
    DEFAULT_MENU = None
    RETAIN = True
    MIN_BUTTON = False
    MAX_BUTTON = False
    #FORCE_DEFAULT_SIZE = True  #always resets the size of the window when its re-created  
    DEFAULT_SIZE = 700,700
    
    def insert_init(self,*args,**kws):
        self.create_guiOptionVar('blockType',defaultValue = '')
        self.create_guiOptionVar('buildProfile',defaultValue = '')
        
        self._d_modules = RIGBLOCKS.get_modules_dat(True)#...refresh data
        self.blockType = None
        self.mDag = False
        self.var_buildProfile = cgmMeta.cgmOptionVar('cgmVar_cgmMRSBuildProfile',
                                                    defaultValue = 'unityMed')
        
    def build_menus(self):
        self.uiMenu_FileMenu = mUI.MelMenu(l='File', pmc = cgmGEN.Callback(self.buildMenu_file))
        self.uiMenu_SetupMenu = mUI.MelMenu(l='Setup', pmc = cgmGEN.Callback(self.buildMenu_setup))
        self.uiMenu_snap = mUI.MelMenu( l='Snap', pmc=self.buildMenu_snap,pmo=True, tearOff=1)                
        self.uiMenu_HelpMenu = mUI.MelMenu(l='Help', pmc = cgmGEN.Callback(self.buildMenu_help))

    def buildMenu_file(self):
        self.uiMenu_FileMenu.clear()                      

        mUI.MelMenuItem( self.uiMenu_FileMenu, l="Save",)
                        # c = lambda *a:mc.evalDeferred(cgmGEN.Callback(uiFunc_save_actions,self)))

        mUI.MelMenuItem( self.uiMenu_FileMenu, l="Save As",)
                        # c = lambda *a:mc.evalDeferred(cgmGEN.Callback(uiFunc_save_as_actions,self)))
        
        mUI.MelMenuItem( self.uiMenu_FileMenu, l="Load",)
                        # c = lambda *a:mc.evalDeferred(cgmGEN.Callback(uiFunc_load_actions,self)))
    def buildMenu_setup(self):pass
    
    def uiFunc_printDat(self,mode='all'):
        _str_func = 'uiFunc_print[{0}]'.format(self.__class__.TOOLNAME)            
        log.debug("|{0}| >>...".format(_str_func))  
        
        if not self.dat:
            return log.error("No dat loaded selected")    
        
        sDat = self.dat
        
        print((log_sub(_str_func,mode)))
        if mode == 'all':
            pprint.pprint(self.dat)
        elif mode == 'settings':
            pprint.pprint(sDat['settings'])
        elif mode == 'base':
            pprint.pprint(sDat['base'])
        elif mode == 'settings':
            pprint.pprint(sDat['settings'])
        elif mode == 'formHandles':
            pprint.pprint(sDat['handles']['form'])        
        elif mode == 'loftHandles':
            pprint.pprint(sDat['handles']['loft'])  
        elif mode == 'sub':
            pprint.pprint(sDat['handles']['sub'])
        elif mode == 'subShapes':
            pprint.pprint(sDat['handles']['subShapes'])
        elif mode == 'subRelative':
            pprint.pprint(sDat['handles']['subRelative'])


        
        
    def uiFunc_create(self, test=False, count = 1):
        _str_func = 'uiFunc_create[{0}]'.format(self.__class__.TOOLNAME)            
        log.info("|{0}| >>...".format(_str_func))
        
        self.ml_blocksMade = []
        import cgm.core.lib.transform_utils as TRANS
        
        #...intitial dict...
        d_create = {'blockType':self.var_blockType.value,
                    'size' : [self.uifloat_baseSizeX.getValue(),
                              self.uifloat_baseSizeY.getValue(),
                              self.uifloat_baseSizeZ.getValue()],
                    'blockProfile':self.uiOM_profile.getValue(),
                    #'buildProfile' : self.var_buildProfile.value,
                    }
        
        _v = self.uiOM_side.getValue()
        if _v != 'none':
            d_create['side'] = _v
        
        _v = self.uiOM_position.getValue()
        if _v != 'none':
            d_create['cgmPosition'] = _v
        
        #...builder data...
        mBuilder = ui_get(False)
        
        if mBuilder:
            if mBuilder._blockCurrent:
                mActiveBlock = mBuilder._blockCurrent.mNode
                d_create['blockParent'] = mActiveBlock
                
                
                
                
                #side = self._blockCurrent.UTILS.get_side(self._blockCurrent)            
        
        _sel = mc.ls(sl=1) or []
        

        #Get Field data
        for a,ui in list(self.d_uiAttrs.items()):
            if not self.d_uiAttrRow[a](q=True,vis=True):
                continue
            
            _v = ui.getValue()
            if _v:
                if a == 'nameList' and ',' in _v:
                    _v = ['{}'.format(v) for v in _v.split(',')]
                d_create[a] = _v
        
        
        #log.info(mBuilder)

        self.d_blockCreate = d_create
        
        if test:return
        
        ml_blocks = []
        
        try:
            ml_helpers = self.ml_helpers
        except:
            ml_helpers = []
            
        for i in range(count):
            mHelper = ml_helpers[i]

            
            if mHelper and mHelper.mNode:
                _orient = mHelper.p_orient
                mHelper.p_orient = 0,0,0
                _size = TRANS.bbSize_get(mHelper.mNode)
                mHelper.p_orient = _orient
                _cast = max(_size) * 1.5
                #d_create['size'] = _size
                _helper = mHelper.mNode
                _shapeDirection = d_create.get('shapeDirection','z+')
                
                _d_shapeToCast = {'y':'xzy',
                                  'x':'yzx',
                                  'z':'xyz'}
                _d_shapeToCast[_shapeDirection[0]][0]
                _castSize = [RAYS.get_dist_from_cast_axis(_helper,_d_shapeToCast[_shapeDirection[0]][0],shapes = _helper, selfCast=True, maxDistance=10000),
                             RAYS.get_dist_from_cast_axis(_helper,_d_shapeToCast[_shapeDirection[0]][1],shapes = _helper, selfCast=True, maxDistance=10000),
                             RAYS.get_dist_from_cast_axis(_helper,_d_shapeToCast[_shapeDirection[0]][2],shapes = _helper, selfCast=True, maxDistance=10000),
                             ]
                d_create['size'] = _castSize
                
                d_create['jointRadius'] = (MATH.average(_castSize[0],_castSize[1])) * .2
                
            pprint.pprint(d_create)
            _mBlock = cgmMeta.createMetaNode('cgmRigBlock',**d_create)

            
            if _sel:
                mc.select(_sel)
            else:
                _mBlock.select()
                
            
            if mBuilder:
                mBuilder.uiScrollList_blocks.rebuild()
                mBuilder.uiScrollList_blocks.selectByObj(_mBlock)
                
                
            
            ml_blocks.append(_mBlock)
            
            
        for mBlock in ml_blocks:
            log.info("|{}| >> [{}] | Created: {}.".format(_str_func,d_create['blockType'],mBlock.mNode))
            if mBlock == ml_blocks[-1]:
                if mBuilder:
                    mBuilder.uiFunc_block_setActive(mBlock=mBlock)
        
        self.ml_blocksMade = ml_blocks
        

        
    def uiFunc_getSize(self, mode = 'selection'):
        _str_func = 'uiFunc_getSize[{0}]'.format(self.__class__.TOOLNAME)            
        log.debug("|{0}| >>...".format(_str_func))
        
        _size = None
        if mode == 'selection':
            _sel = mc.ls(sl=1)
            if not _sel:
                return log.error("Nothing selected")
            _size =  POS.get_bb_size(_sel, False)
        else:
            _size = RIGBLOCKS.get_callSize(blockType = self.var_blockType.getValue(),
                                           blockProfile= self.uiOM_profile.getValue() or None)
        
        if _size:
            self.uifloat_baseSizeX.setValue(_size[0])
            self.uifloat_baseSizeY.setValue(_size[1])
            self.uifloat_baseSizeZ.setValue(_size[2])
            
    def uiFunc_sizeAverage(self, mode = 'selection'):
        _str_func = 'uiFunc_sizeAverage[{0}]'.format(self.__class__.TOOLNAME)            
        log.debug("|{0}| >>...".format(_str_func))
        
        _v = MATH.average(self.uifloat_baseSizeX.getValue(),self.uifloat_baseSizeY.getValue(),
                          self.uifloat_baseSizeZ.getValue())
        
        self.uifloat_baseSizeX.setValue(_v)
        self.uifloat_baseSizeY.setValue(_v)
        self.uifloat_baseSizeZ.setValue(_v)
        
        
    def uiFunc_setBlockType(self, arg):
        _str_func = 'uiFunc_setBlockType[{0}]'.format(self.__class__.TOOLNAME)            
        log.debug("|{0}| >>...".format(_str_func))
        
        
        if arg not in self._d_modules[0]:
            return log.error('Invalid blockType: {}'.format(arg))

        self.uiLabel_blockType(edit=True, label = 'BlockType: {}'.format(arg))
        
        self.var_blockType.setValue(arg)
        self.blockType = arg
        self.uiOM_profile.clear()
        
        try:mBlockModule = self._d_modules[0][self.blockType]
        except:
            log.warning("|{0}| >> No block type stored".format(_str_func))
            return        
        
        l_options = RIGBLOCKS.get_blockProfile_options(arg)
        if l_options:
            for o in l_options:
                self.uiOM_profile.append(o)
                
                
        
        #Get our blockType data to query
        _dAttrDat, _dAttrDefaults = BLOCKUTILS.verify_blockAttrs(None,blockType = arg, mBlockModule = mBlockModule, queryMode=True)
        
                
        #Build ui options ------------------------------------------------------------------------
        self.uiBlock_options.clear()
        self.d_uiAttrs = {}
        self.d_uiAttrRow = {}
        
        #_d,d_defaultSettings = 
        
        
        l_attrs =  ['cgmName','nameIter','nameList','shapeDirection','numShapers','numSubShapers','numRoll','scaleSetup']
        
        if hasattr(mBlockModule,'l_createUI_attrs'):
            l_attrs.extend(getattr(mBlockModule,'l_createUI_attrs'))
            
        l_attrs = LISTS.get_noDuplicates(l_attrs)
            
        d_states = BLOCKUTILS.uiQuery_getStateAttrDictFromModule(mBlockModule)
        #pprint.pprint(d_states)
        l_order,d_sort = BLOCKUTILS.uiQuery_filterListToAttrDict(l_attrs, d_states)
        pprint.pprint(l_order)        
        pprint.pprint(d_sort)
        
        
        """

        
        for k in _keys:
            log.debug(cgmGEN.logString_sub(_str_func,k))                
            
            l = _d.get(k)
            if not l:
                log.debug("|{0}| >> No attrs in : {1}".format(_str_func,k))                
                continue
            
            try:self.__dict__['var_{0}FrameCollapse'.format(k)]
            except:self.create_guiOptionVar('{0}FrameCollapse'.format(k),defaultValue = 0)
            
            mVar_frame = self.__dict__['var_{0}FrameCollapse'.format(k)]
            
            _frame = mUI.MelFrameLayout(self.uiBlock_edit,label = CORESTRINGS.capFirst(k),vis=True,
                                        collapse=mVar_frame.value,
                                        collapsable=True,
                                        enable=True,
                                        marginWidth = 5,
                                        useTemplate = 'cgmUIHeaderTemplate',
                                        expandCommand = cgmGEN.Callback(mVar_frame.setValue,0),
                                        collapseCommand =  cgmGEN.Callback(mVar_frame.setValue,1),
                                        statusBarMessage = k,
                                        )	
            _inside = mUI.MelColumnLayout(_frame,
                                          #rowSpacing = 5,
                                          useTemplate = 'cgmUISubTemplate')
            
            
            _sub_bgc = d_keyColors.get(k)
            if _sub_bgc: 
                _d_uiColors = d_uiStateUIColors.get(_sub_bgc)
            else:
                _d_uiColors = d_uiStateUIColors.get(k) or d_uiStateUIColors.get('default')
                
            _clr_header = _d_uiColors['base']
            _clr_bg = _d_uiColors['bgc']
            _clr_light =  _d_uiColors['light']
            _clr_button = _d_uiColors['button']
            
            if _sub_bgc:
                _clr_header = [v*.6 for v in _clr_header]            
        """
            
       
            
        #log.info(cgmGEN.logString_sub(_str_func, "Profile attrs"))
        #pprint.pprint(l_attrs)
        
        for section in l_order:
            
            _sub_bgc = d_keyColors.get(section)
            if _sub_bgc: 
                _d_uiColors = d_uiStateUIColors.get(_sub_bgc)
            else:
                _d_uiColors = d_uiStateUIColors.get(section) or d_uiStateUIColors.get('default')
                
            _clr_header = _d_uiColors['base']
            _clr_bg = _d_uiColors['bgc']
            _clr_light =  _d_uiColors['light']
            _clr_button = _d_uiColors['button']
            
            if _sub_bgc:
                _clr_header = [v*.6 for v in _clr_header]    
                 
            
            #mc.setParent(self.uiBlock_options)
            #mUI.MelLabel(self.uiBlock_options, bgc= _clr_header, label = section)
            
            l_use = d_sort[section]
            l_use.sort()
            for a in l_use:
                _mRow = mUI.MelHSingleStretchLayout(self.uiBlock_options,ut='cgmUISubTemplate', bgc = _clr_bg)
                mUI.MelSpacer(_mRow,w=_sidePadding)
                
                mUI.MelLabel(_mRow,l="{}".format(a))
                
                a_setup = _dAttrDat.get(a,[])
                
                if a == 'nameList':
                    self.d_uiAttrs[a] = mUI.MelTextField(_mRow)
                    _mRow.setStretchWidget(self.d_uiAttrs[a])
                elif ':' in a_setup:
                    _mRow.setStretchWidget(mUI.MelSeparator(_mRow))                
                    self.d_uiAttrs[a] = mUI.MelOptionMenu(_mRow,ut = 'cgmUITemplate', bgc=_clr_button)
                    for a2 in a_setup.split(':'):
                        self.d_uiAttrs[a].append(a2)
                elif a_setup == 'int':
                    _mRow.setStretchWidget(mUI.MelSeparator(_mRow))
                    self.d_uiAttrs[a] = mUI.MelIntField(_mRow,min=0)
                elif a_setup == 'bool':
                    _mRow.setStretchWidget(mUI.MelSeparator(_mRow))
                    self.d_uiAttrs[a] = mUI.MelCheckBox(_mRow)                
                else:
                    _mRow.setStretchWidget(mUI.MelSeparator(_mRow))
                    self.d_uiAttrs[a] = mUI.MelTextField(_mRow)
    
                mUI.MelSpacer(_mRow,w=_sidePadding)
                _mRow.layout()
                self.d_uiAttrRow[a] = _mRow
        self.uiFunc_setBlockProfile()
        
    def uiFunc_setBlockProfile(self):
        _str_func = 'uiFunc_setBlockProfile[{0}]'.format(self.__class__.TOOLNAME)            
        log.debug("|{0}| >>...".format(_str_func))
        
        _profile = self.uiOM_profile.getValue()
        _build = self.uiOM_build.getValue()
        log.info(_profile)
        
        self.var_buildProfile.setValue(_build)                
        
        try:mBlockModule = self._d_modules[0][self.blockType]
        except:
            log.warning("|{0}| >> No block type stored".format(_str_func))
            return
        
        #try:
            #_d = mBlockModule.d_block_profiles[_profile]
        _d = RIGBLOCKS.get_blockTypeProfile(self.blockType,_profile,buildProfile=_build )[1]
        #except:
            #_d = {'cgmName':self.blockType}
            
        if not _d.get('cgmName'):
            _d['cgmName'] = _profile #self.blockType
        pprint.pprint(_d)
        
        for a in list(self.d_uiAttrs.keys()):
            _v = _d.get(a,None)
            log.debug("Checking: {} | {} | {}".format(a,_v,self.d_uiAttrRow[a]))
            
            if _v is None and a not in ['cgmName']:
                self.d_uiAttrRow[a](edit=True,vis=False)
                continue
                        
            if a == 'cgmName':
                if _v == None:
                    _v = _profile
                    
            _lock = False
            if a in ['numShapers','numRoll','numSubShapers']:
                if _v == None:
                    _v = 1
                    _lock = True
                    
            if issubclass(type(_v),list):
                _v = ','.join(_v)
            
            self.d_uiAttrRow[a](edit=True,vis=True)
            try:
                try:self.d_uiAttrs[a].setValue( _v)
                except Exception as err:
                    self.d_uiAttrs[a].selectByIdx(_v)
            except Exception as err:
                log.error("attr: {} | value: {} | {}".format(a,_v,err))
            if a in ['numShapers']:
                if _lock:
                    self.d_uiAttrs[a](edit=True, en= not _lock)
            
        
    def build_layoutWrapper(self,parent):
        _str_func = 'build_layoutWrapper[{0}]'.format(self.__class__.TOOLNAME)            
        log.debug("|{0}| >>...".format(_str_func))
        
        #Declare form frames...------------------------------------------------------
        _MainForm = mUI.MelFormLayout(parent,)#ut='CGMUITemplate')#mUI.MelColumnLayout(ui_tabs)
        #_inside = mUI.MelColumnLayout(_MainForm, adj=True)#mUI.MelScrollLayout(_MainForm, )#ut='cgmUISubTemplateTemplate')
        #_inside = mUI.MelScrollLayout(_MainForm,childResizable=True)#mUI.MelScrollLayout(_MainForm, )#ut='cgmUISubTemplateTemplate')
        _inside = mUI.MelColumn(_MainForm)
        #SetHeader = CGMUI.add_Header('{0}'.format(_strBlock))
        
        CGMUI.add_Header('Size')
        """
        self.uiStatus_top = mUI.MelButton(_inside,
                                         vis=True,
                                         c = lambda *a:mc.evalDeferred(cgmGEN.Callback(self.uiFunc_dat_get)),
                                         bgc = SHARED._d_gui_state_colors.get('warning'),
                                         label = 'No Data',
                                         h=20)          """      
        
        
        
        #Base size data --------------------------------------------------------------------------
        _row = mUI.MelHSingleStretchLayout(_inside,ut='cgmUISubTemplate',padding = 5)
        mUI.MelSpacer(_row ,w=5)                                              
        mUI.MelLabel(_row ,l='BaseSize')        
        _row.setStretchWidget(mUI.MelSeparator(_row )) 

        for a in list('xyz'):
            mUI.MelLabel(_row ,l=a)
            _field = mUI.MelFloatField(_row , ut='cgmUISubTemplate', w= 60 )
            self.__dict__['uifloat_baseSize{0}'.format(a.capitalize())] = _field
        mUI.MelSpacer(_row ,w=5)
        
        mUI.MelButton(_row, label='//', ann='Average values',
                      c=cgmGEN.Callback(self.uiFunc_sizeAverage),
                      )
        mUI.MelSpacer(_row ,w=5)
        
        _row.layout()
        
        
        #Size Buttons  -------------------------------------------------------------------------------  
        #mc.setParent(_inside)
        #CGMUI.add_LineSubBreak()
        #cgmUI.add_HeaderBreak()
        _row_sizeModes = mUI.MelHLayout(_inside,ut='cgmUIHeaderTemplate',padding = 2)
        
        mc.button(l='Default',
                  height = 20,
                  align='center',
                  c=cgmGEN.Callback(self.uiFunc_getSize,'default'),
                  ann='[Default] - Get the size data from the profile(default)')
        mc.button(l='From Selected',
                  height = 20,
                  align='center',
                  c=cgmGEN.Callback(self.uiFunc_getSize,'selection'),
                  ann='[From Selected] - Use selection to size')
        mc.button(l='Raycast',
                  height = 20,
                  align='center',
                  en=False,
                  #c=cgmGEN.Callback(self.uiFunc_blockCall,'changeState','define',**{'forceNew':True}),
                  ann='[Raycast] - draw/pick size')
        _row_sizeModes.layout()
        
        
        #Helpers Frame -------------------------------------------------------------------------------
        #cgmGEN._reloadMod(HELPERS)
        HELPERS.buildFrame_helpers(self,_inside)
        
        
        #BlockType Buttons --------------------------------------------------------------------------
        self._d_modules = RIGBLOCKS.get_modules_dat(True)#...refresh data
        
        mc.setParent(_inside)
        CGMUI.add_LineSubBreak()
        cgmUI.add_HeaderBreak()        
        self.uiLabel_blockType = mUI.MelLabel(_inside, label = 'Pick Type',  ut = 'cgmUIHeaderTemplate', align = 'center')
        
        
        #_row_blockTypes = mUI.MelHRowLayout(_inside,ut='cgmUIHeaderTemplate')
        #_centerMe = mUI.MelHRowLayout(_inside)
        
        _row_blockTypes = mUI.MelGridLayout(_inside,ut='cgmUIHeaderTemplate',
                                            numberOfColumns=1, cellWidthHeight=(60, 75),
                                            columnsResizable =True,
                                            bgc=cgmUI.guiButtonColor,                                            
                                            #highlightColor=[1,1,1],
                                            )
        mUI.MelSpacer(_row_blockTypes, w=5)
        
        _d = copy.copy(self._d_modules)
        for b in sorted(_d[0]):
            if _d[0][b].__dict__.get('__menuVisible__'):
                
                #mUI.MelIconButton(_row_blockTypes,w=50,
                #                  style = 'iconAndTextVertical', l=b,ann=b)
                _icon = None
                try:
                    _icon = os.path.join(_path_imageFolder,'mrs','{}.png'.format(b))
                except:pass
                #mc.iconTextButton( style='iconAndTextVertical', image1='cube.png', label='cube' )
                #continue
                if _icon:
                    #mUI.MelIconButton
                    mUI.MelIconButton(_row_blockTypes,
                                      ann=b,
                                      style='iconAndTextVertical',
                                      l=b,
                                      image =_icon ,
                                      #ua=True,
                                      #mw=5,
                                      scaleIcon=False,
                                      #olc=[float(v) for v in d_state_colors['form']],
                                      #olb=[float(v) for v in d_state_colors['form']]+[.5],
                                      w=60,h=60,
                                      #bgc = [0,0,0],
                                      c=cgmGEN.Callback(self.uiFunc_setBlockType,b))
                else:
                    mUI.MelButton(_row_blockTypes,l=b,ann=b, bgc=d_state_colors['prerig'],
                                  c=cgmGEN.Callback(self.uiFunc_setBlockType,b))
                
        #_row_blockTypes.layout()
        
        #Option Menus
        mc.setParent(_inside)
        CGMUI.add_LineSubBreak()        
        for i,key in enumerate(['profile','build','side','position']):
            if MATH.is_even(i):
                #_row = mUI.MelHSingleStretchLayout(_inside,ut='cgmUISubTemplate',padding = 5)
                _row = mUI.MelHRowLayout(_inside,ut='cgmUITemplate')
                
            mUI.MelSpacer(_row,w=5)
            mUI.MelLabel(_row,l='{0}: '.format(CORESTRINGS.capFirst(key)))            
            
            _key = 'uiOM_{0}'.format(key)
            self.__dict__[_key] = mUI.MelOptionMenu(_row,ut = 'cgmUITemplate', w=280)
            #_row.setStretchWidget(self.__dict__[_key])
            mUI.MelSpacer(_row,w=5)
            
            _row.layout(expand=True)
        
        for o in BLOCKSHARE._l_buildProfiles:
            self.uiOM_build.append(o)
            
        for o in BLOCKSHARE._l_sides:
            self.uiOM_side.append(o)
            
        for o in BLOCKSHARE._l_positions:
            self.uiOM_position.append(o)                
            
        self.uiOM_build.selectByValue(self.var_buildProfile.getValue())
                        
        self.uiOM_profile(edit=True, cc=lambda *a: self.uiFunc_setBlockProfile())
        self.uiOM_build(edit=True, cc=lambda *a: self.uiFunc_setBlockProfile())
        
        
        #Block settings section ------------------------------------------------------------------
        self.uiBlock_options = mUI.MelScrollLayout(_MainForm,
                                             bgc=cgmUI.guiHeaderColor,
                                             #adj = True,
                                             useTemplate = 'cgmUITemplate')
        
        #....
        mc.setParent(_MainForm)
        self.uiPB_test=None
        self.uiPB_test = mc.progressBar(vis=False)

        #Create buttons...
        _rowCreate = mUI.MelHLayout(_MainForm, h = 25,padding=5,)
                                    #bgc = d_state_colors['define'])
        #self.uiButton_create = 
        mUI.MelButton(_rowCreate, label='Build From Helper', ut='cgmUITemplate', en=True,
                      c = lambda *a:HELPERS.uiFunc_helper_build(self),
                      h=20)
        
        mUI.MelSeparator(_rowCreate,w=10)
        
        mUI.MelButton(_rowCreate,
                      vis=True,
                      c=cgmGEN.Callback(self.uiFunc_create),
                      ut='cgmUITemplate',
                      #bgc = d_state_colors['rig'],
                      label = 'Create Raw',
                      h=20)

        
        _rowCreate.layout()
        
        _row_cgm = CGMUI.add_cgmFooter(_MainForm)            
        
        #Form Layout--------------------------------------------------------------------
        _MainForm(edit = True,
                  af = [(_inside,"top",0),
                        (_inside,"left",0),
                        (_inside,"right",0),
                        #(self.uiBlock_options,"left",0),
                        #(self.uiBlock_options,"right",0),                        
                        (_rowCreate,"left",0),
                        (_rowCreate,"right",0),
                        (self.uiPB_test,"left",0),
                        (self.uiPB_test,"right",0),                            
                        (self.uiBlock_options,"left",0),
                        (self.uiBlock_options,"right",0),                        
                        (_row_cgm,"left",0),
                        (_row_cgm,"right",0),
                        (_row_cgm,"bottom",0),
    
                        ],
                  ac = [
                      #(self.uiBlock_options,"top",0,_inside),                      
                      #(_inside,"bottom",0,self.uiBlock_options),
                      (self.uiBlock_options,"top",0,_inside),                      
                      (self.uiBlock_options,"bottom",0,self.uiPB_test),
                      #(self.uiBlock_options,"bottom",0,self.uiPB_test),
                      (self.uiPB_test,"bottom",0,_rowCreate),
                      (_rowCreate,"bottom",0,_row_cgm),
                      ],
                  attachNone = [(_row_cgm,"top")])    

        if self.var_blockType.getValue():
            self.uiFunc_setBlockType(self.var_blockType.getValue())
            self.uiFunc_getSize('default')
            self.uiFunc_setBlockProfile()
            
        self.mHelper = HELPERS.HelperDag(self)
        self.mDag = self.mHelper.mDag
        self.ml_helpers = VALID.listArg(self.mDag.getMessageAsMeta('helpers'))
            
            
def buildFrame_helpers(self,parent,changeCommand = ''):
    try:self.var_helpersFrameCollapse
    except:self.create_guiOptionVar('helpersFrameCollapse',defaultValue = 0)
    mVar_frame = self.var_helpersFrameCollapse
    
    _frame = mUI.MelFrameLayout(parent,label = 'Helpers',vis=True,
                                collapse=mVar_frame.value,
                                collapsable=True,
                                enable=True,
                                useTemplate = 'cgmUIHeaderTemplate',
                                expandCommand = lambda:mVar_frame.setValue(0),
                                collapseCommand = lambda:mVar_frame.setValue(1)
                                )	
    
    _inside = mUI.MelColumnLayout(_frame,useTemplate = 'cgmUISubTemplate') 
    
    CGMUI.add_Header('Helpers')
    