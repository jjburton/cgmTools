"""
------------------------------------------
block: cgm.core.mrs.lib
Author: Josh Burton
email: cgmonks.info@gmail.com

Website : https://github.com/jjburton/cgmTools/wiki
------------------------------------------

These are functions with self assumed to be a cgmRigBlock
================================================================
"""
import random
import re
import copy
import time
import os
import pprint
import sys
# From Red9 =============================================================
from Red9.core import Red9_Meta as r9Meta
from Red9.core import Red9_AnimationUtils as r9Anim

#========================================================================
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
#========================================================================

import maya.cmds as mc

# From cgm ==============================================================
from cgm.core import cgm_General as cgmGEN
from cgm.core import cgm_Meta as cgmMeta
from cgm.core import cgm_RigMeta as RIGMETA
import cgm.core.rig.constraint_utils as RIGCONSTRAINT
#reload(RIGCONSTRAINT)
from cgm.core.lib import curve_Utils as CURVES
from cgm.core.lib import attribute_utils as ATTR
from cgm.core.lib import position_utils as POS
from cgm.core.lib import math_utils as MATH
from cgm.core.lib import distance_utils as DIST
from cgm.core.lib import snap_utils as SNAP
from cgm.core.lib import rigging_utils as RIGGING
import cgm.core.classes.NodeFactory as NODEFACTORY
from cgm.core.lib import search_utils as SEARCH
from cgm.core.lib import rayCaster as RAYS
from cgm.core.cgmPy import validateArgs as VALID
from cgm.core.cgmPy import path_Utils as PATH
import cgm.core.rig.general_utils as RIGGEN
import cgm.core.lib.list_utils as LISTS
from cgm.core.classes import GuiFactory as cgmUI
from cgm.core.lib import rigging_utils as CORERIG
import cgm.core.rig.joint_utils as COREJOINTS
import cgm.core.lib.transform_utils as TRANS
import cgm.core.lib.ml_tools.ml_resetChannels as ml_resetChannels
import cgm.core.mrs.lib.shared_dat as BLOCKSHARE
from cgm.core.lib import geo_Utils as COREGEO
from cgm.core.lib import skin_utils as CORESKIN

#reload(BLOCKSHARE)
import cgm.core.mrs.lib.general_utils as BLOCKGEN

#=============================================================================================================
#>> Queries
#=============================================================================================================
@cgmGEN.Timer
def example(self):
    _short = self.p_nameShort
    _str_func = ' example'.format(self)
    log.debug("|{0}| >> ... [{1}]".format(_str_func,self)+ '-'*80)
    

@cgmGEN.Timer
def get_shapeOffset(self):
    """
    Get the shape offset value 
    """
    _str_func = ' get_shapeOffset'.format(self)
    log.debug("|{0}| >> ... [{1}]".format(_str_func,self)+ '-'*80)
    
    if self.getMessage('rigBlock'):
        mRigBlock = self.rigBlock
        l_attrs = ['controlOffset','skinOffset']
        for a in l_attrs:
            if mRigBlock.hasAttr(a):
                v = mRigBlock.getMayaAttr(a)
                log.debug("|{0}| >> {1} attr found on rigBlock: {2}".format(_str_func,a,v))                
                return v            
    
    l_attrs = ['loftOffset','skinOffset']
    for a in l_attrs:
        if self.hasAttr(a):
            v = self.getMayaAttr(a)
            log.debug("|{0}| >> {1} attr found: {2}".format(_str_func,a,v))                
            return v
    
    if self.getMessage('masterControl'):
        log.debug("|{0}| >> Master control found...".format(_str_func))
        _bb = DIST.get_bb_size(self.getMessage('masterControl'))
        return MATH.average(_bb[0],_bb[2])/50
        
    log.debug("|{0}| >> default return".format(_str_func))
    return 1


@cgmGEN.Timer
def modules_getHeirarchal(self,rewire=False):
    _str_func = ' modules_getHeirarchal'.format(self)
    log.debug("|{0}| >> ... [{1}]".format(_str_func,self)+ '-'*80)
    
    if not rewire:
        try:
            _res = self.mModulesAll
            if _res:
                log.debug(cgmGEN.logString_msg(_str_func,'mModulesAll buffer...'))
                return _res
        except Exception as err:
            log.error(err)
    else:
        modules_get(self,True)
            
    
    
    try:ml_initialModules = self.moduleChildren
    except:ml_initialModules = []
    
    if not ml_initialModules:
        return []
    ml_allModules = BLOCKGEN.get_puppet_heirarchy_context(ml_initialModules[0],'root',asList=True,report=False)
                
    if rewire:
        ATTR.set_message(self.mNode, 'mModulesAll', [mObj.mNode for mObj in ml_allModules])
        #self.connectChildren(_res, 'mControlsAll', srcAttr='msg')
                
    return ml_allModules        

@cgmGEN.Timer
def modules_get(self,rewire=False):
    _str_func = ' modules_get'.format(self)
    log.debug("|{0}| >> ... [{1}]".format(_str_func,self)+ '-'*80)
    
    if not rewire:
        try:
            _res = VALID.listArg(self.mModulesAll)
            if _res:
                log.debug(cgmGEN.logString_msg(_str_func,'mModulesAll buffer...'))
                return _res
        except Exception as err:
            log.debug(err)    
    

    
    try:ml_initialModules = self.moduleChildren
    except:ml_initialModules = []
    
    int_lenModules = len(ml_initialModules)  

    ml_allModules = copy.copy(ml_initialModules)
    for i,m in enumerate(ml_initialModules):
        log.debug("|{0}| >> checking: {1}".format(_str_func,m))
        _str_module = m.p_nameShort
        for m in m.get_allModuleChildren():
            if m not in ml_allModules:
                ml_allModules.append(m)
                
    if rewire and ml_allModules:
        ATTR.set_message(self.mNode, 'mModulesAll', [mObj.mNode for mObj in ml_allModules])
        #self.connectChildren(_res, 'mControlsAll', srcAttr='msg')
                
    return ml_allModules

@cgmGEN.Timer
def modules_gather(self,**kws):
    _short = self.p_nameShort
    _str_func = ' modules_gather'.format(self)
    log.debug("|{0}| >> ... [{1}]".format(_str_func,self)+ '-'*80)
    
    ml_modules = modules_get(self)
    int_lenModules = len(ml_modules)

    for i,mModule in enumerate(ml_modules):
        _str_module = mModule.p_nameShort
        module_connect(self,mModule,**kws)
    return ml_modules
    
@cgmGEN.Timer
def module_connect(self,mModule,**kws):
    _short = self.p_nameShort
    _str_func = ' module_connect'.format(self)
    log.debug("|{0}| >> ... [{1}]".format(_str_func,self)+ '-'*80)
    
    ml_buffer = copy.copy(self.getMessage('moduleChildren',asMeta=True)) or []#Buffer till we have have append functionality	
        #self.i_masterNull = self.masterNull
    
    mModule = cgmMeta.validateObjArg(mModule,'cgmRigModule')

    if mModule not in ml_buffer:
        ml_buffer.append(mModule)
        self.__setMessageAttr__('moduleChildren',[mObj.mNode for mObj in ml_buffer]) #Going to manually maintaining these so we can use simpleMessage attr  parents
    
    mModule.modulePuppet = self.mNode

    mModule.parent = self.masterNull.partsGroup.mNode

    if mModule.getMessage('moduleMirror'):
        log.debug("|{0}| >> moduleMirror found. connecting...".format(_str_func))
        #module_connect(self,mModule.moduleMirror)        

    return True        
     

def is_upToDate(self,report = True):
    _res = []
    
    if report:
        _short = self.p_nameBase
        print((cgmGEN._str_hardBreak))        
        print(("|{0}| >> ".format(_short) + cgmGEN._str_subLine))
    
    for mModule in modules_get(self):
        _res.append( mModule.atUtils('is_upToDate',report) )
        
    if report:
        if False in _res:
            print(("|{0}| >> OUT OF DATE ".format(_short)))
        else:
            log.info("|{0}| >> build current. ".format(_short))
        print((cgmGEN._str_hardBreak))
        
    if False in _res:
        return False
    return True
    
#=============================================================================================================
#>> Mirror
#=============================================================================================================
@cgmGEN.Timer
def mirror_verify(self,progressBar = None,progressEnd=True):
    """
    Verify the mirror setup of the puppet modules
    """
    _str_func = ' mirror_verify'.format(self)
    log.debug("|{0}| >> ... [{1}]".format(_str_func,self)+ '-'*80)
    
    if self.isReferenced():
        log.debug("|{0}| >> can't process referenced asset | {1}".format(_str_func,self))        
        return 
    
    controls_get(self,True,rewire=True)#Wire pass
    
    md_data = {}
    md_cgmTags = {}
    ml_processed = []
    ml_controlOrphans = []
    
    d_runningSideIdxes = {'Centre':0,
                          'Left':0,
                          'Right':0}
    
    ml_modules = modules_getHeirarchal(self,True)
    md_indicesToControls = {'Centre':{},
                           'Left':{},
                           'Right':{}}
    
    int_lenModules = len(ml_modules)
    
    if progressBar:
        cgmUI.progressBar_start(progressBar)
    else:
        progressBar = cgmUI.doStartMayaProgressBar()
        
    def validate_controls(ml):
        for i,mObj in enumerate(ml):
            log.debug("|{0}| >> Register: {1}".format(_str_func,mObj))
            
            if md_cgmTags.get(mObj):
                continue
            
            if not issubclass(type(mObj), cgmMeta.cgmControl):
                log.debug("|{0}| >> Reclassing: {1}".format(_str_func,mObj))
                mObj = cgmMeta.asMeta(mObj,'cgmControl',setClass = True)#,setClass = True
                ml[i] = mObj#...push back
            md_cgmTags[mObj] = mObj.getCGMNameTags(['cgmDirection'])
            mObj._verifyMirrorable()#...veryify the mirrorsetup    
            ml_controlOrphans.append(mObj)
            mObj.mirrorIndex = 0 
        
    def process_set(ml,d1=None,d2=None):
        md_sideControls = {'Centre':[],
                           'Left':[],
                           'Right':[]}
        d_Indices = {}
        
        for k,v in list(d_runningSideIdxes.items()):
            d_Indices[k] = v
            
        if d_Indices['Right'] != d_Indices['Left']:
            if d_Indices['Left'] > d_Indices['Right']:
                d_Indices['Right'] = d_Indices['Left']
            else:
                d_Indices['Left'] = d_Indices['Right']
            log.info("|{0}| >> Rebasing start side idx: {1}".format(_str_func,d_Indices['Left']))
                
        validate_controls(ml)
        
        #First process our sides ....
        for mObj in ml:
            _side = mObj.getEnumValueString('mirrorSide')
            md_sideControls[_side].append(mObj)
            
        if d1 and d2:
            log.debug("|{0}| >> d1 and d2...".format(_str_func))            
            for key in BLOCKSHARE._l_controlOrder:
                self_keyControls = d1['md_controls'].get(key,[])
                mirr_keyControls = d2['md_controls'].get(key,[])
                
                len_self = len(self_keyControls)
                len_mirr = len(mirr_keyControls)
                
                log.debug(cgmGEN.logString_msg("|{0}| >> Key: {1} | self: {2} | mirror: {3}".format(_str_func,key,len_self,len_mirr)))
                
                ml_primeControls = self_keyControls #...longer list of controls
                ml_secondControls = mirr_keyControls
                
                if len_mirr>len_self:
                    ml_primeControls = mirr_keyControls 
                    ml_secondControls = self_keyControls
                
                ml_cull = copy.copy(ml_secondControls)
                ml_cull_prime = copy.copy(ml_primeControls)
                
                for i,mObj in enumerate(ml_primeControls):
                    log.debug("|{0}| >> Prime: {1}".format(_str_func, mObj))
                    
                    if mObj not in ml_controlOrphans:
                        log.debug("already processed control: {0}".format(mObj))
                        continue
                    if progressBar:
                        cgmUI.progressBar_set(progressBar,
                                              minValue = 0,
                                              maxValue=len(ml_primeControls),
                                              progress=i, vis=True)
                        
                    _side = mObj.getEnumValueString('mirrorSide')
                    _v = d_Indices[_side]+1
                    
                    if  md_indicesToControls[_side].get(_v):
                        log.error('already stored start value: {0}, finding new one'.format(_v))
                        while md_indicesToControls[_side].get(_v):
                            _v +=1
                        log.error('New index: {0}'.format(_v))
                    
                    mObj.mirrorIndex = _v
                    log.debug("|{0}| >> Setting index: [{1}] | {2} | {3}".format(_str_func,_v,_side,mObj))
                    
                    
                    md_indicesToControls[_side][_v] = mObj
                    ml_controlOrphans.remove(mObj)
                    ml_cull_prime.remove(mObj)
                    
                    tags_prime = md_cgmTags[mObj]
                    
                    mMirror = mObj.getMessageAsMeta('mirrorControl')
                    if mMirror:
                        log.debug("|{0}| >> Mirror found: {1}".format(_str_func,mMirror))
                        mMirror.mirrorIndex = _v
                        
                        _sideMirror = mMirror.getEnumValueString('mirrorSide')                
                        
                        d_Indices[_sideMirror] = _v#...push it back                
                        try:ml_cull.remove(mMirror)
                        except:pass
                        md_indicesToControls[_sideMirror][_v] = mMirror
                        try:ml_controlOrphans.remove(mMirror)                        
                        except:pass
                    else:
                        log.debug("Looking for match...")
                        
                        mMatch = False
                        
                        for mCandidate in ml_cull:
                            #First try a simple name match
                            #l_candSplit = mCandidate.p_nameBase.split('_')
                            
                            _match = True
                            tags_second = md_cgmTags.get(mCandidate) or mCandidate.getCGMNameTags(['cgmDirection'])
                            for a,v in list(tags_second.items()):
                                if tags_prime[a] != v:
                                    _match = False
                                    break
                            
                            if _match:
                                mMatch = mCandidate
                                break

                        if not mMatch:
                            log.debug("Trying name match...")
                            _nameBase = mObj.p_nameBase
                            _matchString = None
                            if _nameBase.startswith('L_'):
                                _matchString = 'R_' + _nameBase[2:]
                            elif _nameBase.startswith('R_'):
                                _matchString = 'L_' + _nameBase[2:]
                            
                            if _matchString:
                                log.debug("matchstring: {0}".format(_matchString))
                                for mCandidate in ml_cull:
                                    #First try a simple name match
                                    #l_candSplit = mCandidate.p_nameBase.split('_')
                                    if _matchString == mCandidate.p_nameBase:
                                        mMatch = mCandidate
                                        break
                             
                                
                        if mMatch:
                            log.debug("|{0}| >> Match found: {1} | {2}".format(_str_func,mObj.p_nameShort,mMatch.p_nameShort))
                            
                            mObj.doStore('mirrorControl',mMatch)
                            mMatch.doStore('mirrorControl',mObj)                        
                            
                            mMatch.mirrorIndex = _v
                            
                            _sideMirror = mMatch.getEnumValueString('mirrorSide')                
                            d_Indices[_sideMirror] = _v#...push it back                
                            ml_cull.remove(mMatch)
                            md_indicesToControls[_sideMirror][_v] = mMatch
                            try:ml_controlOrphans.remove(mMatch)
                            except:pass
                            
                    d_Indices[_side] = _v
                    
                for mObj in ml_cull_prime + ml_cull:
                    if mObj not in ml_controlOrphans:
                        log.info("already processed: {0}".format(mObj))
                        continue
                    log.debug("|{0}| >> Setting index of unmatched: [{1}] | {2} | {3}".format(_str_func,_v,_side,mObj))
                    _side = mObj.getEnumValueString('mirrorSide')                
                    _v = d_Indices[_side]+1
                    tags_prime = md_cgmTags[mObj]
                    
                    mObj.mirrorIndex = _v
                    md_indicesToControls[_side][_v] = mObj            
                    
                    d_Indices[_side] = _v
                    ml_controlOrphans.remove(mObj)
                    
            for s in 'Left','Right':
                d_runningSideIdxes[s] = d_Indices[s]+1
                    
            return
        else:
            log.debug("|{0}| >> self match".format(_str_func))                        
            ml_right = md_sideControls.get('Right',[])
            ml_left = md_sideControls.get('Left',[])
            ml_done = []
            if ml_right and ml_left:
                for i,mObj in enumerate(ml_right + ml_left):
                    if progressBar:
                        cgmUI.progressBar_set(progressBar,
                                              minValue = 0,
                                              maxValue=len(ml_right+ml_left),
                                              progress=i, vis=True)                    
                    if mObj in ml_done:
                        continue
                    
                    _side = mObj.getEnumValueString('mirrorSide')
                    _v = d_Indices[_side]+1                    
                    
                    while md_indicesToControls[_side].get(_v):
                        _v +=1
                        
                    log.info("|{0}| >> Setting index: [{1}] | {2} | {3}".format(_str_func,_v,_side,mObj))
                    
                    if  md_indicesToControls[_side].get(_v):
                        log.error('already stored start value')
                        return False
                    
                    md_indicesToControls[_side][_v] = mObj
                    ml_done.append(mObj)
                    ml_controlOrphans.remove(mObj)
                    d_Indices[_side] = _v
                    ATTR.set(mObj.mNode,'mirrorIndex',_v)
                    
                    mMirror = mObj.getMessageAsMeta('mirrorControl')
                    if mMirror:
                        log.info("|{0}| >> Mirror found: {1}".format(_str_func,mMirror))
            
                        _sideMirror = mMirror.getEnumValueString('mirrorSide')                
                        d_Indices[_sideMirror] = _v#...push it back                
                        md_indicesToControls[_sideMirror][_v] = mMirror
                        ml_done.append(mMirror)
                        ml_controlOrphans.remove(mMirror)
                        ATTR.set(mMirror.mNode,'mirrorIndex',_v)

            
            
        #Centers
        #pprint.pprint(md_sideControls)
        #pprint.pprint(md_cgmTags)
        
        _v = None
        int_len = len(md_sideControls['Centre'])
        for i,mObj in enumerate(md_sideControls['Centre']):
            if progressBar:
                cgmUI.progressBar_set(progressBar,
                                      minValue = 0,
                                      maxValue=int_len,
                                      progress=i, vis=True)
                
            _side = mObj.getEnumValueString('mirrorSide')
            _v = d_runningSideIdxes[_side]
            log.debug("|{0}| >> Setting index: [{1}] | {2} | {3}".format(_str_func,_v,_side,mObj))
            ATTR.set(mObj.mNode,'mirrorIndex',_v)
            d_Indices[_side] = _v
            md_indicesToControls[_side][_v] = mObj
            
            d_runningSideIdxes[_side]+=1
            ml_controlOrphans.remove(mObj)
            
            

    
    #Self controls =====================================================
    ml_self = controls_get(self)
    process_set(ml_self)
    
    #>> Process ======================================================================================
    for i,mModule in enumerate(ml_modules):
        if mModule in ml_processed:
            log.info("|{0}| >> Already processed: {1}".format(_str_func,mModule))
            continue
        
        log.info("|{0}| >> Processing: {1}".format(_str_func,mModule))
        
        if progressBar:
            _str = '{0}'.format(mModule.mNode)
            log.info(cgmGEN.logString_sub(_str_func,_str))
            cgmUI.progressBar_set(progressBar,
                                  minValue = 0,
                                  maxValue=int_lenModules+1,
                                  status = _str,
                                  progress=i, vis=True)
            
        d_module = mModule.UTILS.get_mirrorDat(mModule)
        mMirror = d_module.get('mMirror')
        ml_controls = d_module['ml_controls']
        if mMirror:
            log.info("|{0}| >> Block has mirror: {1} | {2}".format(_str_func,mModule.mNode, mMirror.mNode))
            
            d_mirror =  mMirror.UTILS.get_mirrorDat(mMirror)
            ml_controls.extend(d_mirror['ml_controls'])
            
            process_set(ml_controls,d_module,d_mirror)
        else:
            process_set(ml_controls)
            
        ml_processed.append(mModule)
        if mMirror:ml_processed.append(mMirror)


    log.info(cgmGEN.logString_sub(_str_func,'Centre'))
    for k,v in list(md_indicesToControls['Centre'].items()):
        print(("{0} | {1} ".format(k,v.p_nameShort)))
        
    log.info(cgmGEN.logString_sub(_str_func,'Left/Right'))
    for k,v in list(md_indicesToControls['Left'].items()):
        try:print(("{0} | {1} >><< {2}".format(k,v.p_nameShort,md_indicesToControls['Right'][k].p_nameShort)))
        except:
            pass

    if ml_controlOrphans:
        log.error(cgmGEN.logString_sub(_str_func,"Orphans!"))
        pprint.pprint(ml_controlOrphans)

    if progressBar and progressEnd:
        cgmUI.progressBar_end(progressBar)
        
    return

@cgmGEN.Timer
def mirror_getNextIndex(self,side):
    _str_func = ' mirror_getNextIndex'.format(self)
    log.debug("|{0}| >> ... [{1}]".format(_str_func,self)+ '-'*80)
    
    l_return = []
    ml_modules = modules_get(self)
    int_lenModules = len(ml_modules)
    str_side = cgmGEN.verify_mirrorSideArg(side)
    for i,mModule in enumerate(ml_modules):
        #self.log.info("Checking: '%s'"%mModule.p_nameShort)
        _str_module = mModule.p_nameShort
        if mModule.get_mirrorSideAsString() == str_side :
            #self.progressBar_set(status = "Checking Module: '%s' "%(_str_module),progress = i, maxValue = int_lenModules)		    				    
            try:mi_moduleSet = mModule.rigNull.moduleSet.getMetaList()
            except:mi_moduleSet = []
            for mObj in mi_moduleSet:
                int_side = mObj.getAttr('mirrorSide')
                int_idx = mObj.getAttr('mirrorIndex')
                str_side = mObj.getEnumValueString('mirrorSide')		    
                l_return.append(int_idx)
                l_return.sort()

    if l_return:
        return max(l_return)+1
    else:return 0        
 
    
    
@cgmGEN.Timer
def mirror_getDict(self):
    _str_func = ' mirror_getDict'.format(self)
    log.debug("|{0}| >> ... [{1}]".format(_str_func,self)+ '-'*80)
    
    d_return = {}
    ml_modules = modules_get(self)
    int_lenModules = len(ml_modules)

    for i,mModule in enumerate(ml_modules):
        _str_module = mModule.p_nameShort
        try:mi_moduleSet = mModule.rigNull.moduleSet.getMetaList()
        except:mi_moduleSet = []
        for mObj in mi_moduleSet:

            if mObj.hasAttr('mirrorSide') and mObj.hasAttr('mirrorIndex'):
                int_side = mObj.getAttr('mirrorSide')
                int_idx = mObj.getAttr('mirrorIndex')
                str_side = mObj.getEnumValueString('mirrorSide')

                if not d_return.get(int_side):
                    d_return[int_side] = []

                if int_idx in d_return[int_side]:
                    pass
                    #self.log_debug("%s mModule: %s | side: %s | idx :%s already stored"%(self._str_reportStart,_str_module, str_side,int_idx))
                else:
                    d_return[int_side].append(int_idx)
    return d_return
         
#=============================================================================================================
#>> Anim
#=============================================================================================================
@cgmGEN.Timer
def modules_settings_set(self,**kws):
    _str_func = ' modules_settings_set'.format(self)
    log.debug("|{0}| >> ... [{1}]".format(_str_func,self)+ '-'*80)
    
    for mModule in modules_get(self):
        if mModule.rigNull.getMessage('settings'):
            mSettings = mModule.rigNull.settings
            _short_settings = mSettings.mNode
            for k,v in list(kws.items()):
                try:
                    ATTR.set(_short_settings,k,v)
                except Exception as err:
                    #if mSettings.hasAttr(k):
                    log.debug("|{0}| >>  Failed to set: mModule:{1} | k:{2} | v:{3} | {4}".format(_str_func,mModule.mNode,k,v,err))
        else:
            log.debug("|{0}| >>  Missing settings: {1}".format(_str_func,mModule))
    return True

@cgmGEN.Timer
def anim_reset(self,transformsOnly = True):
    _str_func = ' anim_reset'.format(self)
    log.debug("|{0}| >> ... [{1}]".format(_str_func,self)+ '-'*80)
    _result = False
    _sel = mc.ls(sl=True)
    
    self.puppetSet.select()
    if mc.ls(sl=True):
        RIGGEN.reset_channels(transformsOnly = transformsOnly)
        #ml_resetChannels.main(transformsOnly = transformsOnly)
        _result = True
    if _sel:mc.select(_sel)
    return _result
        
@cgmGEN.Timer
def anim_select(self):
    _str_func = ' anim_select'.format(self)
    log.debug("|{0}| >> ... [{1}]".format(_str_func,self)+ '-'*80)
    self.puppetSet.select()
    return True

@cgmGEN.Timer
def anim_key(self,**kws):
    _str_func = ' anim_key'.format(self)
    log.debug("|{0}| >> ... [{1}]".format(_str_func,self)+ '-'*80)
    _result = False
    _sel = mc.ls(sl=True)
    
    l_objs = self.puppetSet.getList() or []
    
    if l_objs:
        mc.select(l_objs)
        mc.setKeyframe(**kws)
        b_return =  True
        
    if _sel:mc.select(_sel)
    return _result
        
    
@cgmGEN.Timer
def layer_verify(self,**kws):
    _str_func = ' layer_verify'.format(self)
    log.debug("|{0}| >> ... [{1}]".format(_str_func,self)+ '-'*80)
    
    if not self.getMessage('displayLayer'):
        mLayer = cgmMeta.validateObjArg(mc.createDisplayLayer(),'cgmNode',setClass=True)
        
        ATTR.copy_to(self.mNode,'cgmName',mLayer.mNode,driven='target')
        mLayer.doStore('cgmName','main')
        mLayer.doName()
        self.connectChildNode(mLayer.mNode,'displayLayer')
        
    if not self.getMessage('controlLayer'):
        mLayer = cgmMeta.validateObjArg(mc.createDisplayLayer(),'cgmNode',setClass=True)
        
        #ATTR.copy_to(self.mNode,'cgmName',mLayer.mNode,driven='target')
        mLayer.doStore('cgmName','control')
        mLayer.doName()
        self.connectChildNode(mLayer.mNode,'controlLayer')
    
    return self.displayLayer, self.controlLayer
    
    
def armature_verify(self):
    """
    First pass on armature setup
    """
    _str_func = 'verify_armature'
    log.debug("|{0}| >> ...".format(_str_func)+cgmGEN._str_hardBreak)
    log.debug(self)
    
    
    if not self.getMessage('armature'):
        log.debug("|{0}| >> missing plug. Creating armature dag...".format(_str_func))
        mArmature = self.masterNull.doCreateAt(setClass=True)
    else:
        mArmature = self.getMessageAsMeta('armature')
        
    ATTR.copy_to(self.mNode,'cgmName',mArmature.mNode,driven='target')
    mArmature.addAttr('puppet',attrType = 'messageSimple')
    if not mArmature.connectParentNode(self.mNode,'puppet','armature'):
        raise Exception("Failed to connect masterNull to puppet network!")

    mArmature.addAttr('cgmType',initialValue = 'ignore',lock=True)
    mArmature.addAttr('cgmModuleType',value = 'master',lock=True)   
    mArmature.addAttr('geoGroup',attrType = 'messageSimple',lock=True)
    mArmature.addAttr('skeletonGroup',attrType = 'messageSimple',lock=True) 

    #See if it's named properly. Need to loop back after scene stuff is querying properly
    mArmature.doName()
    mArmature.dagLock(True,ignore='v')
    
    mc.editDisplayLayerMembers(self.displayLayer.mNode, mArmature.mNode, noRecurse=True)
    #editDisplayLayerMembers -noRecurse master_displayLayer `ls -selection`;
    
    for attr in 'geo','skeleton':
        _plug = attr+'Group'
        
        if mArmature.getMessage(_plug):
            mGroup = mArmature.getMessageAsMeta(_plug)
            if mGroup.getParent(asMeta=1) != mArmature:
                mGroup.dagLock(False)
                mGroup.p_parent = mArmature
                mGroup.dagLock(True)
            continue
        
        if not self.masterNull.getMessage(_plug):
            log.debug("|{0}| >> missing plug. Creating: {1}".format(_str_func,attr))            
            mGroup = self.masterNull.doCreateAt(setClass=True)    
            self.masterNull.connectChildNode(mGroup,_plug,'module')
        else:
            mGroup = self.masterNull.getMessageAsMeta(_plug)
            mGroup.dagLock(False)        
        
            
        mArmature.connectChildNode(mGroup,_plug)
        mGroup.p_parent = mArmature
        mGroup.dagLock(True)
        mGroup.rename(attr)        

        log.debug("|{0}| >> attr: {1} | mGroup: {2}".format(_str_func, attr, mGroup))    
    return

def armature_remove(self):
    """
    Remove the armature
    """
    _str_func = 'armature_remove'
    log.debug("|{0}| >> ...".format(_str_func)+cgmGEN._str_hardBreak)
    log.debug(self)
    
    
    if not self.getMessage('armature'):
        return log.error("|{0}| >> No armature found.".format(_str_func))
    
    mArmature = self.getMessageAsMeta('armature')
        
    for attr in 'geo','skeleton':
        _plug = attr+'Group'
        
        if mArmature.getMessage(_plug):
            mGroup = mArmature.getMessageAsMeta(_plug)
            log.debug("|{0}| >> attr: {1} | mGroup: {2}".format(_str_func, attr, mGroup))                
            mGroup.dagLock(False)
            if attr == 'geo':
                mGroup.p_parent = self.masterNull.noTransformGroup
            else:
                mGroup.p_parent = self.masterControl
            mGroup.rename("{0}_grp".format(attr))
            mGroup.dagLock(True)
            
        else:
            log.error("|{0}| >> Missing group: {1}.".format(_str_func,attr))
    return


def is_rigged(self):
    _str_func = 'is_rigged'
    log.debug("|{0}| >> ...".format(_str_func)+cgmGEN._str_hardBreak)
    log.debug(self)
    
    if not self.getMessage('masterControl'):
        return False
    
    return True
    
    
def rig_connect(self):
    """
    First pass on armature setup
    """
    _str_func = 'rig_connect'
    log.debug("|{0}| >> ...".format(_str_func)+cgmGEN._str_hardBreak)
    log.debug(self)
    
    if not is_rigged(self) and force !=True:
        log.debug("|{0}| >>  Module not rigged".format(_str_func))
        return False

    if rig_isConnected(self):
        log.debug("|{0}| >>  Master control already connected".format(_str_func))
        return True    
    
    mRootJoint = self.getMessageAsMeta('rootJoint')
    if not mRootJoint:
        log.warning("|{0}| >> No root joint".format(_str_func))        
        return 
    
    mRootMotionHandle =  self.getMessageAsMeta('rootMotionHandle')
    if not mRootJoint:
        log.error("|{0}| >> No root motion handle".format(_str_func))        
        raise Exception("No root motion handle found. ")
    
    RIGCONSTRAINT.driven_connect(mRootJoint,mRootMotionHandle,'noScale')
    
    return True

def rig_getSkinJoints(self,**kws):
    ml = []
    mRootJoint = self.getMessageAsMeta('rootJoint')
    if mRootJoint:
        ml.append(mRootJoint)
    
    mRootMotionHandle =  self.getMessageAsMeta('rootMotionHandle')
    if mRootMotionHandle:
        ml.append(mRootMotionHandle)
        
    return ml
    
    
def rig_disconnect(self):
    """
    First pass on armature setup
    """
    _str_func = 'rig_disconnect'
    log.debug("|{0}| >> ...".format(_str_func)+cgmGEN._str_hardBreak)
    log.debug(self)
    
    if not rig_isConnected(self):
        log.debug("|{0}| >>  Master control not connected".format(_str_func))
        return True
    
    mRootJoint = self.getMessageAsMeta('rootJoint')
    if not mRootJoint:
        log.warning("|{0}| >> No root joint".format(_str_func))        
        return
    
    RIGCONSTRAINT.driven_disconnect(mRootJoint)
    return True
    
    
    
    
def rig_isConnected(self):
    """
    First pass on armature setup
    """
    _str_func = 'rig_isConnected'
    log.debug("|{0}| >> ...".format(_str_func)+cgmGEN._str_hardBreak)
    log.debug(self)
    
    mRootJoint = self.getMessageAsMeta('rootJoint')
    if not mRootJoint:
        return False
    
    if mRootJoint.getConstraintsTo():
        return True
    return False

    
    
def qss_verify(self,puppetSet=True,bakeSet=True,deleteSet=False, exportSet = False):
    """
    First pass on qss verification
    """
    _str_func = 'qss_verify'
    log.debug("|{0}| >> ...".format(_str_func)+cgmGEN._str_hardBreak)
    log.debug(self)
    
    mMasterSet = self.getMessageAsMeta('masterSet')
    if not mMasterSet:
        mMasterSet = cgmMeta.cgmObjectSet(setType='tdSet',qssState=True)
        mMasterSet.connectParentNode(self.mNode,'puppet','masterSet')
        mMasterSet.doStore('cgmName','master')
    mMasterSet.doName()
    
    log.debug("|{0}| >> masterSet: {1}".format(_str_func,mMasterSet))    
    
    
    if puppetSet:
        log.debug("|{0}| >> puppetSet...".format(_str_func)+'-'*40)        
        
        mSet = self.getMessageAsMeta('puppetSet')
        if not mSet:
            mSet = cgmMeta.cgmObjectSet(setType='animSet',qssState=True)
            mSet.connectParentNode(self.mNode,'puppet','puppetSet')
            #ATTR.copy_to(self.mNode,'cgmName',mSet.mNode,'cgmName',driven = 'target')
            mSet.doStore('cgmName','all')
            
        mSet.doName()
        mMasterSet.addObj(mSet.mNode)
        
        log.debug("|{0}| >> puppetSet: {1}".format(_str_func,mSet))
        
    if bakeSet:
        log.debug("|{0}| >> bakeset...".format(_str_func)+'-'*40)        
        
        mSet = self.getMessageAsMeta('bakeSet')
        if not mSet:
            mSet = cgmMeta.cgmObjectSet(setType='tdSet',qssState=True)
            mSet.connectParentNode(self.mNode,'puppet','bakeSet')
            #ATTR.copy_to(self.mNode,'cgmName',mSet.mNode,'cgmName',driven = 'target')
            mSet.doStore('cgmName','bake')
            #mSet.doStore('cgmTypeModifier','bake')
        mSet.doName()
        mSet.purge()
        log.debug("|{0}| >> bakeSet: {1}".format(_str_func,mSet))
        mMasterSet.addObj(mSet.mNode)
        
        ml_joints = get_joints(self,'bind')
        
        for mObj in ml_joints:
            log.debug("|{0}| >>adding : {1}".format(_str_func,mObj))            
            mSet.addObj(mObj.mNode)
        
    if deleteSet:
        log.debug("|{0}| >> deleteSet...".format(_str_func)+'-'*40)        
        
        mSet = self.getMessageAsMeta('deleteSet')
        if not mSet:
            mSet = cgmMeta.cgmObjectSet(setType='tdSet',qssState=True)
            mSet.connectParentNode(self.mNode,'puppet','deleteSet')
            #ATTR.copy_to(self.mNode,'cgmName',mSet.mNode,'cgmName',driven = 'target')
            #mSet.doStore('cgmTypeModifier','bake')
            mSet.doStore('cgmName','delete')
        mSet.doName()
        mSet.purge()
        mMasterSet.addObj(mSet.mNode)

        log.debug("|{0}| >> deleteSet: {1}".format(_str_func,mSet))
        
        for mObj in get_deleteSetDat(self):
            mSet.addObj(mObj.mNode)
    
    if exportSet:
        log.debug("|{0}| >> exportSet...".format(_str_func)+'-'*40)        
        
        mSet = self.getMessageAsMeta('exportSet')
        if not mSet:
            mSet = cgmMeta.cgmObjectSet(setType='tdSet',qssState=True)
            mSet.connectParentNode(self.mNode,'puppet','exportSet')
            #ATTR.copy_to(self.mNode,'cgmName',mSet.mNode,'cgmName',driven = 'target')
            #mSet.doStore('cgmTypeModifier','bake')
            mSet.doStore('cgmName','export')
        mSet.doName()
        mSet.purge()
        mMasterSet.addObj(mSet.mNode)        
        log.debug("|{0}| >> exportSet: {1}".format(_str_func,mSet))
        mMaster = self.masterNull
        mSet.addObj(mMaster.geoGroup.mNode)
        for mGrp in mMaster.skeletonGroup,mMaster.geoGroup:
            for mChild in mGrp.getChildren(asMeta=1):
                mSet.addObj(mChild.mNode)
        #for mObj in get_joints(self,'bind') + get_rigGeo(self):
            #mSet.addObj(mObj.mNode)    
@cgmGEN.Timer
def groups_verify(self):
    _str_func = "groups_verify".format()
    log.debug("|{0}| >> ...".format(_str_func))

    mMasterNull = self.masterNull

    if not mMasterNull:
        raise ValueError("No masterNull")

    for attr in ['rig','deform','noTransform','geo','skeleton',
                 'parts','worldSpaceObjects','puppetSpaceObjects','spacePivots']:
        _link = attr+'Group'
        mGroup = mMasterNull.getMessage(_link,asMeta=True)# Find the group
        if mGroup:mGroup = mGroup[0]

        if not mGroup:
            mGroup = mMasterNull.doCreateAt(setClass=True)
            mGroup.connectParentNode(mMasterNull.mNode,'puppet', attr+'Group')
            
        mGroup.rename(attr)
        log.debug("|{0}| >> attr: {1} | mGroup: {2}".format(_str_func, attr, mGroup))

        # Few Case things
        #----------------------------------------------------
        if attr in ['rig','geo','skeleton']:
            mGroup.p_parent = mMasterNull
        elif attr in ['deform','puppetSpaceObjects'] and self.getMessage('masterControl'):
            mGroup.p_parent = self.getMessage('masterControl')[0]	    
        else:    
            mGroup.p_parent = mMasterNull.rigGroup

        ATTR.set_standardFlags(mGroup.mNode)

        if attr == 'worldSpaceObjects':
            mGroup.addAttr('cgmAlias','world')
        elif attr == 'puppetSpaceObjects':
            mGroup.addAttr('cgmAlias','puppet')
            
        if attr == 'spacePivots':
            mGroup.p_parent = mMasterNull.puppetSpaceObjectsGroup
                

def collect_worldSpaceObjects(self,progressBar = None):
    _str_func = 'collect_worldSpaceObjects'
    log.debug("|{0}| >> ...".format(_str_func)+cgmGEN._str_hardBreak)
    log.debug(self)    
    ml_objs = []
    mMasterNull = self.masterNull
    mWorldSpaceObjectsGroup = mMasterNull.worldSpaceObjectsGroup
    mPuppetSpaceObjectsGroup = mMasterNull.puppetSpaceObjectsGroup
    

        
    ml_children = self.masterControl.getChildren(asMeta = 1) or []
    if progressBar:
        cgmUI.progressBar_start(progressBar)
        len_children = len(ml_children)
    for i,mObj in enumerate(ml_children):
        if progressBar:
            #mc.progressBar(progressBar,edit = True,
            #               minValue = 0,
            #               maxValue=len_children,step=i, vis=True)
            cgmUI.progressBar_set(progressBar,
                                  minValue = 0,
                                  maxValue=len_children+1,
                                  progress=i, vis=True)
            time.sleep(.01)
        if mObj.getMayaAttr('cgmType') in ['dynDriver','dynFollow']:
            mObj.parent = mPuppetSpaceObjectsGroup
            ml_objs.append(mObj)
            
    ml_children = mObj in mMasterNull.getChildren(asMeta = 1) or []
    if progressBar:
        len_children = len(ml_children)
    for i,mObj in enumerate(ml_children):
        if progressBar:
            cgmUI.progressBar_set(progressBar,
                                  minValue = 0,
                                  maxValue=len_children+1,
                                  progress=i,vis=True)
            time.sleep(.01)
            
        if mObj.getMayaAttr('cgmType') in ['dynDriver','dynFollow']:
            mObj.parent = mWorldSpaceObjectsGroup     
            ml_objs.append(mObj)
            
            
    #World root stuff...
    for mObj in cgmMeta.asMeta(mc.ls('|*', type = 'transform')):
        if mObj.getMayaAttr('cgmType') in ['dynDriver','dynFollow']:
            mObj.parent = mWorldSpaceObjectsGroup     
            ml_objs.append(mObj)
    
    
    
    if progressBar:cgmUI.progressBar_end(progressBar)
    return ml_objs

def get_joints(self,mode='bind'):
    """
    First pass on qss verification
    """
    _str_func = 'get_joints'
    log.debug("|{0}| >> ...".format(_str_func)+cgmGEN._str_hardBreak)
    log.debug(self)
    _mode = mode.lower()
    _res = []
    if _mode in ['bind','skin']:
        mRoot = self.getMessageAsMeta('rootJoint')
        if mRoot:
            _res.append(mRoot)
    for mModule in modules_get(self):
        if _mode in ['bind','skin']:
            ml = mModule.UTILS.rig_getSkinJoints(mModule,asMeta=True)
        elif _mode in ['rig']:
            ml = mModule.rigNull.msgList_get('rigJoints',asMeta = True)
        else:
            raise ValueError("Unknown mode: {0}".format(mode))
        _res.extend(ml)
        
    return _res

#=============================================================================================================
#>> Mirror
#=============================================================================================================
def get_deleteSetDat(self):
    """
    First pass on qss verification
    """
    _str_func = 'get_deleteSetDat'
    log.debug("|{0}| >> ...".format(_str_func)+cgmGEN._str_hardBreak)
    log.debug(self)
    mMasterNull = self.masterNull
    l_compare = [mMasterNull.geoGroup,mMasterNull.skeletonGroup]
    _res = []
    for mChild in mMasterNull.getChildren(asMeta=True):
        if mChild not in l_compare:
            _res.append(mChild)
            
    mSkeletonGroup = mMasterNull.skeletonGroup
    if mSkeletonGroup:
        for mChild in mSkeletonGroup.getAllChildren(asMeta=1):
            if mChild.getMayaAttr('cgmType') in ['dynDriver','attachDriver']:
                _res.append(mChild)
        

    return _res
    
def get_rigGeo(self):
    """
    First pass on qss verification
    """
    _str_func = 'get_rigGeo'
    log.debug("|{0}| >> ...".format(_str_func)+cgmGEN._str_hardBreak)
    log.debug(self)
    mMasterNull = self.masterNull
    
    _res = []
    _l_base = [o for o in mc.ls(type='mesh',visible = True, long=True)]
    _l_dags = [VALID.getTransform(o) for o in _l_base]
    _l_dags = LISTS.get_noDuplicates(_l_dags)
    
    for o in _l_dags:
        mObj = cgmMeta.asMeta(o)
        if mObj.getMayaAttr('mClass') == 'cgmControl':
            log.debug("|{0}| >> Invalid obj: {1}".format(_str_func,o))
            continue
        if mObj.getMayaAttr('cgmType') in ['jointApprox','rotatePlaneVisualize']:
            log.debug("|{0}| >> Invalid obj: {1}".format(_str_func,o))
            continue
        if 'proxy_geo' in o:
            continue
        if 'proxyGeo' in o:
                continue        
        _res.append(mObj)
    
    log.debug("|{0}| >> Visible shapes: {1} | dags: {2} | res: {3} ".format(_str_func,
                                                                            len(_l_base),
                                                                            len(_l_dags),
                                                                            len(_res)))
    

    return _res

def get_exportSetDat(self):
    """
    First pass on qss verification
    """
    _str_func = 'get_exportSetDat'
    log.debug("|{0}| >> ...".format(_str_func)+cgmGEN._str_hardBreak)
    log.debug(self)
    mMasterNull = self.masterNull
    l_compare = [mMasterNull.geoGroup,mMasterNull.skeletonGroup]
    _joints = get_joints(self,'bind')
    _geo = get_rigGeo(self)
    
    log.debug("|{0}| >> Joints: {1} | Geo: {2} ".format(_str_func,len(_joints),len(_geo)))
        
    return _joints + _geo
    
    
@cgmGEN.Timer
def rigNodes_setAttr(self,attr=None,value=None,progressBar = None,progressEnd=True):
    """
    Verify the mirror setup of the puppet modules
    """
    _str_func = ' rigNodes_setAttr'.format(self)
    log.debug("|{0}| >> ... [{1}]".format(_str_func,self)+ '-'*80)
    
    md_data = {}
    ml_modules = modules_get(self)
    
    ml_processed = []
    
    ml_modules = modules_get(self)
    if progressBar:
        int_lenModules = len(ml_modules)
        cgmUI.progressBar_start(progressBar,int_lenModules+1)
        
        
    l_dat = self.getMessage('rigNodes')
    
    for i,mModule in enumerate(ml_modules):
        if progressBar:
            cgmUI.progressBar_set(progressBar,
                                  progress=i, vis=True)
        try:l_dat.extend(mModule.rigNull.getMessage('rigNodes'))
        except Exception as err:
            log.error("{0} | {1}".format(mModule,err))
            
    if attr and value is not None:
        int_lenNodes = len(l_dat)
        if progressBar:
            cgmUI.progressBar_start(progressBar,int_lenNodes+1)
        for i,node in enumerate(l_dat):
            if progressBar:
                cgmUI.progressBar_set(progressBar,
                                      status=node,
                                      progress=i, vis=True)
            try:
                _shapes = TRANS.shapes_get(node)
                if _shapes:
                    for s in _shapes:
                        ATTR.set(node,attr,value)
                ATTR.set(node,attr,value)
            except Exception as err:
                log.error("{0} | {1}".format(node,err))
    
    if progressBar and progressEnd:
        cgmUI.progressBar_end(progressBar)
    
    return l_dat

@cgmGEN.Timer
def rig_connectAll(self, mode = 'connect', progressBar = None,progressEnd=True):
    """
    Connect/disconnect the whole puppet
    """
    _str_func = ' rig_connectAll'.format(self)
    log.debug("|{0}| >> ... [{1}]".format(_str_func,self)+ '-'*80)
    
    ml_modules = modules_get(self)
    
    
    ml_modules = modules_get(self)
    if progressBar:
        int_lenModules = len(ml_modules)
        cgmUI.progressBar_start(progressBar,int_lenModules+2)
        
        
    _d_modeToCall = {'connect':'rig_connect',
                     'disconnect':'rig_disconnect'}
    if not _d_modeToCall.get(mode):
        raise ValueError("Unknown mode: {0}".format(mode))
    for i,mModule in enumerate([self] + ml_modules):
        if progressBar:
            cgmUI.progressBar_set(progressBar,
                                  status = mModule.p_nameShort,
                                  progress=i, vis=True)
            
        try:
            mModule.atUtils(_d_modeToCall.get(mode))
        except Exception as err:
            log.error("{0} | {1}".format(mModule,err))
    
    if progressBar and progressEnd:
        cgmUI.progressBar_end(progressBar)
    
@cgmGEN.Timer
def proxyMesh_verify(self, forceNew = True, puppetMeshMode = False,progressBar = None,progressEnd=True):
    """
    Connect/disconnect the whole puppet
    """
    _str_func = ' rig_connectAll'.format(self)
    log.debug("|{0}| >> ... [{1}]".format(_str_func,self)+ '-'*80)
    
    ml_modules = modules_get(self)

    ml_rigBLocks = []
    
    for i,mModule in enumerate([self] + ml_modules):  
        try:
            ml_rigBLocks.append(mModule.rigBlock)
        except Exception as err:
            log.error("{0} | {1}".format(mModule,err))
            
    if progressBar:
        int_len = len(ml_rigBLocks)
        cgmUI.progressBar_start(progressBar,int_len+1)
        
    for i,mRigBlock in enumerate(ml_rigBLocks):
        if progressBar:
            cgmUI.progressBar_set(progressBar,
                                  status = mRigBlock.p_nameShort,
                                  progress=i, vis=True)
        try:
            mRigBlock.verify_proxyMesh(forceNew=forceNew,puppetMeshMode=puppetMeshMode)
        except Exception as err:
            log.error("{0} | {1}".format(mRigBlock,err))
    
    if progressBar and progressEnd:
        cgmUI.progressBar_end(progressBar)
        
        
#Controls dat ===========================================================================        
l_controlOrder = ['root','settings','motionHandle']
d_controlLinks = {'root':['masterControl'],
                  'motionHandle':['rootMotionHandle'],
                  'pivots':['pivot{0}'.format(n.capitalize()) for n in BLOCKSHARE._l_pivotOrder]}

def controls_getDat(self, keys = None, ignore = [], report = False, listOnly = False,rewire=False):
    """
    Function to find all the control data for comparison for mirroing or other reasons
    """
    def addMObj(mObj,mList):
        if mObj not in mList:
            log.debug("|{0}| >> adding: {1}".format(_str_func,mObj))
            mList.append(mObj)            
            """
            if ml_objs is not None:
                if mObj in ml_objs:
                    ml_objs.remove(mObj)
                else:
                    log.warning("|{0}| >> Not in list. Skipped: {1}".format(_str_func,mObj))
                    return
            log.debug("|{0}| >> adding: {1}".format(_str_func,mObj))
            mList.append(mObj)"""


    _str_func = ' controls_getDat'
    log.debug("|{0}| >>  ".format(_str_func)+ '-'*80)
    log.debug("{0}".format(self))
    ignore = VALID.listArg(ignore)
    _isReferenced = self.isReferenced()
    
    ml_objs = []
    #try:ml_objs = self.puppetSet.getMetaList() or []
    #except:pass
    #l_objs = [mObj.mNode for mObj in ml_objs]
    md_controls = {}
    ml_controls = []
    
    if ml_objs:
        for mObj in ml_objs:
            if mObj.getMayaType() == 'objectSet':
                ml_objs.remove(mObj)

    if keys:
        l_useKeys = VALID.listArg(keys)
    else:
        l_useKeys = l_controlOrder

    if ignore:
        log.debug("|{0}| >> Ignore found... ".format(_str_func)+'-'*20)        
        for k in ignore:
            if k in l_useKeys:
                l_useKeys.remove(k)

    for key in l_useKeys:
        l_options = d_controlLinks.get(key,[key])
        log.debug("|{0}| >>  {1}:{2}".format(_str_func,key,l_options))
        md_controls[key] = []
        _ml = md_controls[key]
        for o in l_options:
            mObj = self.getMessageAsMeta(o)
            if mObj:
                log.debug("|{0}| >>  Message found: {1} ".format(_str_func,o))                
                addMObj(mObj,_ml)
            elif self.msgList_exists(o):
                log.debug("|{0}| >>  msgList found: {1} ".format(_str_func,o))                
                _msgList = self.msgList_get(o)
                for mObj in _msgList:
                    addMObj(mObj,_ml)
        ml_controls.extend(_ml)

    if ml_objs:
        ml_dup = copy.copy(ml_objs)
        log.debug("|{0}| >> Second pass {1}... ".format(_str_func,len(ml_objs))+'-'*20)
        for mObj in ml_dup:
            log.debug("|{0}| >> {1} ".format(_str_func,mObj))            
            if mObj.hasAttr('cgmControlDat'):
                _tags = mObj.cgmControlDat.get('tags',[])
                log.debug("|{0}| >> tags: {1} ".format(_str_func,_tags))            
                for t in _tags:
                    _t = str(t)
                    #if keys is not None and _t not in l_useKeys:
                    #    continue
                    if not md_controls.get(_t):
                        md_controls[_t] = []
                    _ml = md_controls[_t] 
                    ml_controls.append(mObj)                    
                    addMObj(mObj,_ml)

    if not keys and 'spacePivots' not in ignore:
        md_controls['spacePivots'] = []
        _ml = md_controls['spacePivots']
        for mObj in ml_controls:
            mBuffer = mObj.msgList_get('spacePivots')
            for mSpace in mBuffer:
                addMObj(mSpace,_ml)
                ml_controls.append(mSpace)
    
    if rewire and not _isReferenced:
        log.warning("|{0}| >> rewire... ".format(_str_func))        
        for mObj in ml_controls:
            if not mObj.getMessageAsMeta('cgmOwner'):
                log.info("|{0}| >> Repair on. Broken rigNull connection on: {1}".format(_str_func,mObj))
                mObj.connectParentNode(self.mNode,'cgmOwner')
                
        ml_core = []
        for k in ['root']:
            ml_core.extend(md_controls[k])
        #self.addAttr('mControlsCore',attrType = 'multimessage')
        #self.mControlsCore = ml_core
        ATTR.set_message(self.mNode, 'mControlsCore', [mObj.mNode for mObj in ml_core],multi=True)                
        
    if report:
        log.info("|{0}| >> Dict... ".format(_str_func))
        pprint.pprint( md_controls)

        log.info("|{0}| >> List... ".format(_str_func))
        pprint.pprint( ml_controls)

    if ml_objs and keys is None and not ignore:        
        log.debug("|{0}| >> remaining... ".format(_str_func))
        #pprint.pprint( ml_objs)
        raise ValueError("|{0}| >> Resolve missing controls!".format(_str_func))
        #return log.error("|{0}| >> Resolve missing controls!".format(_str_func))

    if report:
        return

    if keys or listOnly:
        return ml_controls
    return md_controls,ml_controls

#@cgmGEN.Timer
def controls_checkDups(self):
    _str_func = controls_checkDups
    ml_controls = controls_get(self,True)
    
    l_strings = []
    mObjs = []
    mDups = []
    d_strToObj = {}
    
    for i,mObj in enumerate(ml_controls):
        log.debug("Checking: {0} | Obj: {1}".format(i,mObj))
        
        _str = mObj.p_nameBase
        mOwner = d_strToObj.get(_str)
        if mOwner:
            
            log.warning(cgmGEN._str_subLine)
            _idx = l_strings.index(_str)
            log.warning("key | {0} ".format(_str))
            
            log.warning("Obj: {0}".format(mObj))
            log.warning("mirrorIndex: {1} | Obj Name: {0}".format(mObj.p_nameShort,mObj.mirrorIndex))
            
            log.warning("Owner: {0}".format(mOwner))
            log.warning("mirrorIndex: {1} | Name: {0}".format(mOwner.p_nameShort,mOwner.mirrorIndex))
            mDups.append(mObj)
        else:
            d_strToObj[_str] = mObj
            l_strings.append(_str)
        mObjs.append(mObj)
        
    if not mDups:
        return log.warning("Puppet has no dups: {0}".format(self.mNode))
    
    log.info(cgmGEN.logString_msg(_str_func,'dups:'))
    for mObj in mDups:
        print(("idx: {0} | {1}".format(mObj.mirrorIndex,mObj)))
    return mDups
        


@cgmGEN.Timer
def controls_get(self,walk=False,rewire=False,core=False):
    _str_func = ' controls_get'
    _res = controls_getDat(self,listOnly=True,rewire=rewire)
    if not core and not walk and not rewire:
        return _res
    
    if not rewire and not walk:
        if not core:
            try:
                _res = self.mControlsAll
                if _res:
                    log.info(cgmGEN.logString_msg(_str_func,'mControlsAll buffer...'))
                    return _res
            except Exception as err:
                log.error(err)
        else:
            try:
                _resCore = self.mControlsCoreAll
                if _resCore:
                    log.info(cgmGEN.logString_msg(_str_func,'mControlsCoreAll buffer...'))
                    return _resCore
            except Exception as err:
                log.error(err)
                
    try:
        _resCore = self.mControlsCore
        if _resCore:
            if not walk:
                log.info(cgmGEN.logString_msg(_str_func,'mControlsCore buffer...'))                
                return _resCore
    except Exception as err:
        log.error(err)
        _resCore = copy.copy(_res)
        
    for mModule in modules_get(self):
        _res.extend( mModule.atUtils('controls_get',rewire=rewire))
        _resCore.extend( mModule.atUtils('controls_get',core=True))
        
    if rewire and not self.isReferenced():
        ATTR.set_message(self.mNode, 'mControlsAll', [mObj.mNode for mObj in _res])
        ATTR.set_message(self.mNode, 'mControlsCoreAll', [mObj.mNode for mObj in _resCore])
    if core:
        return _resCore
    return _res
        
    log.error("|{0}| >> No options specified".format(_str_func))
    return False


def get_report(self):
    
    print((cgmGEN._str_hardBreak))
    print(("Puppet: '{0}' | {1}".format(self.cgmName, self.p_nameBase)))
    print((cgmGEN._str_hardBreak))
    
    
    ml_modules = modules_get(self)
    
    md_modules = {}
    int_joints = 0
    int_nodes = 0
    
    d_counts = {}
    
    for i,mModule in enumerate(ml_modules):
        _d = {}
        md_modules[mModule] = _d
        try:mBlock = mModule.rigBlock
        except:
            log.warning("No rigBlock: {0}".format(mModule.p_nameShort))
            continue
        _d['Bind'] = len(mBlock.atUtils('skeleton_getBind',warn=False) or [])
        int_joints += _d['Bind']
        
        
        mRigNull = mModule.getMessageAsMeta('rigNull')
        if mRigNull:
            _bfr = mRigNull.msgList_get('proxyMesh',asMeta=True)
            #Rig nodes....
            
            ml_rigNodes = mRigNull.getMessageAsMeta('rigNodes') or []
            
            for mObj in ml_rigNodes:
                _type = mObj.getMayaType()
                if _type not in _d:
                    _d[_type] = 0
                    
                if _type not in d_counts:
                    d_counts[_type] = 0
                    
                _d[_type] += 1
                d_counts[_type] +=1
                
            int_nodes += len(ml_rigNodes)
            #_d['Nodes'] = len(ml_rigNodes)
        
        
        print((cgmGEN.logString_sub("{0} - '{1}'".format(i,mModule.p_nameShort),
                                   "[{0}] | Type: {1} | Profile: {2}".format(mBlock.p_nameShort, mBlock.blockType, mBlock.blockProfile))))
              
        _keys = list(_d.keys())
        _keys.sort()
        
        for k in _keys:
            print(("   [{0}] : {1}".format(k,_d[k])))
        
        print('\n')
        

    print((cgmGEN.logString_sub("Counts", 'Nodes')))
    _keys = list(d_counts.keys())
    _keys.sort()
    
    for k in _keys:
        print(("   [{0}] : {1}".format(k,d_counts[k])))    
        
        
    print('\n')
    print((cgmGEN._str_subLine))
    
    d_dat = {'Modules': len(ml_modules),
             'Bind Joints':int_joints,
             'Nodes':int_nodes}
    
    for d,v in list(d_dat.items()):
        print(("   [{0}] : {1}".format(d,v)))
        

    print('\n')

    BLOCKGEN.get_rigBlock_heirarchy_context(self.rigBlock,'below',False,True)
    
    print((cgmGEN._str_hardBreak))
    

def get_report_asset(self,csv=False):
    _str_func = 'get_report_asset'
    
    _res = []
    _res.append("Puppet: '{0}' | {1}".format(self.cgmName, self.p_nameBase))    
    
    
    _file = os.path.normpath(mc.file(q=True, loc=True))
    _res.append(_file)
    #_file = PATH.Path(mc.file(q=True, loc=True))
    #_res.append(_file._splits)
    
    mExportSet = self.getMessageAsMeta('exportSet')
    for mObj in mExportSet.getMetaList():
        _type = mObj.getMayaType()
        if _type == 'joint':
            print(("joint " + mObj.mNode))
        elif _type in ['mesh']:
            _d = {'mesh':mObj.mNode,
                  'verts':mc.polyEvaluate(mObj.getShapes()[0], vertex=True)}
            _joints = CORESKIN.get_influences_fromSelected(mObj.mNode)
            if _joints:
                _d['joints'] = len(_joints)
            _res.append(_d)
        else:
            log.warning( cgmGEN.logString_msg(_str_func, "Unhandled type: {0} | {1}".format(_type,mObj.mNode)))
    

    pprint.pprint(_res)
    return _res


def get_uiString(self,showSide=True):
    """
    Get a snap shot of all of the controls of a rigBlock
    """
    try:
        _str_func = 'get_uiString'
        log.debug(cgmGEN.logString_start(_str_func))
        str_self = self.mNode
        _d_scrollList_shorts = BLOCKGEN._d_scrollList_shorts
        _l_report = []
        
        #Control sets ===================================================================================
        log.debug(cgmGEN.logString_sub(_str_func, '...'))
        
        if showSide:
            _dir = self.getMayaAttr('cgmDirection')
            if _dir:
                _l_report.append( _d_scrollList_shorts.get(_dir,_dir))
            
        _pos = self.getMayaAttr('cgmPosition')
        if _pos and str(_pos).lower() not in ['none','false']:
            _l_report.append( _d_scrollList_shorts.get(_pos,_pos) )
                
                                    
        l_name = []
        
        #l_name.append( ATTR.get(_short,'blockType').capitalize() )
        _cgmName = self.getMayaAttr('cgmName')
        l_name.append('"{0}"'.format(_cgmName))

        #_l_report.append(STR.camelCase(' '.join(l_name)))
        _l_report.append(' - '.join(l_name))
        
        _l_report.append('[puppet]')
        

        """
        if mObj.hasAttr('baseName'):
            _l_report.append(mObj.baseName)                
        else:
            _l_report.append(mObj.p_nameBase)"""                
    
        if self.isReferenced():
            _l_report.append("[REF]")
            
        _str = " | ".join(_l_report)
            
        return _str
        
    except Exception as err:
        log.debug(cgmGEN.logString_start(_str_func,'ERROR'))
        log.error(err)
        return self.mNode
    
    
    
    
def uiMenu_picker(self,parent = None):
    _short = self.p_nameShort
    ml_done = []
    try:mc.setParent(parent)
    except:pass
    
    md_dat,ml = controls_getDat(self)
    
    for k in l_controlOrder:
        _ml = md_dat.get(k)
        if _ml:
            mc.menuItem(en=True,divider = True, label = k)
            for mControl in _ml:
                _str = mControl.p_nameBase
                d = {'ann':'[{0}] Control: {1} '.format(k,_str),
                     'c':cgmGEN.Callback(mControl.select),
                     'label':"{0}".format(_str)}            
                mc.menuItem(**d)
            
    return

#=============================================================================================================
#>> Mirror
#=============================================================================================================
@cgmGEN.Timer
def controller_verify(self,progressBar = None,progressEnd=True):
    """
    Verify the mirror setup of the puppet modules
    """
    try:
        
        _str_func = ' controller_verify'.format(self)
        log.debug("|{0}| >> ... [{1}]".format(_str_func,self)+ '-'*80)
        
        if self.isReferenced():
            log.debug("|{0}| >> can't process referenced asset | {1}".format(_str_func,self))        
            return 
        
        
        controller_purge(self,progressBar,False)
        
        controls_get(self,True,rewire=False)#Wire pass
        
        md_data = {}
        md_cgmTags = {}
        ml_processed = []
        ml_controlOrphans = []
        md_controls = {}
        
        ml_modules = modules_getHeirarchal(self,True)
        int_lenModules = len(ml_modules)
        
        if progressBar:
            cgmUI.progressBar_start(progressBar)
        else:
            progressBar = cgmUI.doStartMayaProgressBar()
            
        def validate_controls(ml):
            for i,mObj in enumerate(ml):
                log.debug("|{0}| >> First pass: {1}".format(_str_func,mObj))
                if not issubclass(type(mObj), cgmMeta.cgmControl):
                    log.debug("|{0}| >> Reclassing: {1}".format(_str_func,mObj))
                    mObj = cgmMeta.asMeta(mObj,'cgmControl',setClass = True)#,setClass = True
                    ml[i] = mObj#...push back
                md_cgmTags[mObj] = mObj.getCGMNameTags(['cgmName'])
                md_controls[mObj] = mObj.controller_get()
                ml_controlOrphans.append(mObj)
            
    
                
    
        
        #Self controls =====================================================
        #ml_self = controls_get(self)
        #process_set(ml_self)
        
        #mPuppetController = self.controller_get()
        
        #>> Process ======================================================================================
        md_moduleController = {}
        md_moduleInt = {}
        for i,mModule in enumerate(ml_modules):
            md_moduleController[mModule] = mModule.atUtils('get_controllerDat')
            md_moduleInt[i] = md_moduleController[mModule]
            #mModule.atUtils('get_mirrorDat',False)
            
            """
            for mObj in md_moduleMirrorDat[i]['ml_controls']:
                mController = mObj.getMessageAsMeta('mController')
                if mController:
                    mController.purge()"""
    
        
        #pprint.pprint(md_moduleInt)
        #if progressBar and progressEnd:
        #    cgmUI.progressBar_end(progressBar)
            
        
        #pprint.pprint(md_moduleMirrorDat)
        md_tags = {}
        def get_tag(mObj):
            mTag = md_tags.get(mObj)
            if mTag:
                return mTag
            
            mTag = cgmMeta.controller_get(mObj,True)
            mTag.cycleWalkSibling = 1
            mTag.prepopulate = 1
            mTag.parentprepopulate = 1
            md_tags[mObj] = mTag
            return mTag
            
            
        ml_all = []
        md_failsafe = {}
        
        for i,mModule in enumerate(ml_modules):
            _str_module = mModule.p_nameShort
            log.info(cgmGEN.logString_sub(_str_func,"mModule: {0}".format(_str_module)))
            
            if mModule in ml_processed:
                log.debug("|{0}| >> Already processed: {1}".format(_str_func,mModule))
                continue
            
            log.debug("|{0}| >> Processing: {1}".format(_str_func,mModule))
            
            if progressBar:
                _str = '{0}'.format(mModule.mNode)
                log.debug(cgmGEN.logString_sub(_str_func,_str))
                cgmUI.progressBar_set(progressBar,
                                      minValue = 0,
                                      maxValue=int_lenModules+1,
                                      status = _str,
                                      progress=i, vis=True)
            
            
            md_controls = md_moduleController[mModule]
            
            mSettings = md_controls.get('settings') or False
            mSettingsController = False
            if mSettings:
                mSettings = mSettings[0]
                mSettingsController = get_tag(mSettings)
    
            mModParent = mModule.moduleParent
            ml_modSiblings = mModule.atUtils('siblings_get') or []
            ml_modChildren = mModule.moduleChildren or []
            md_tmp = {}
            
            mBlock = mModule.getMessageAsMeta('rigBlock')
            _idx_attach = 0
            _b_face = False
            if mBlock:
                _str_attachPoint = mBlock.getEnumValueString('attachPoint')
                if _str_attachPoint == 'start':
                    _idx_attach = 0
                elif _str_attachPoint == 'end':
                    _idx_attach = -1
                elif _str_attachPoint == 'index':
                    _idx_attach = mBlock.attachIndex
                
                if mBlock.blockType in ['eye','muzzle','brow']:
                    _b_face = True
            
            for tag in ['root','settings','fk','ik','segmentHandles','direct','face']:
                log.debug(cgmGEN.logString_msg(_str_func,"tag: {0}".format(tag)))
                #First validate...
                _l_tag = md_controls.get(tag,[])
                ml = []
                md_tmp[tag] = ml
                pprint.pprint(_l_tag)
                for ii,mObj in enumerate(_l_tag):
                    try:
                        log.info( cgmGEN.logString_sub(_str_func, mObj))
                        mController =  get_tag(mObj)
                        ml.append(mController)
                        ml_children = []
                        
                        if mController in ml_all:
                            continue
                        
                        if tag not in ['root']:
                            if md_tmp.get('root'):
                                md_failsafe[mController] = md_tmp['root'][0]
                                
                        ml_all.append(mController)
                        
                        if not ii:#If our first obj, set to parent of module Parent
                            if mModParent:
                                _buffer = md_moduleController[mModParent].get(tag)
                                if _buffer:
                                    mParentController = get_tag(_buffer[_idx_attach])
                                    mController.parent_set(mParentController)
                                else:
                                    _buffer = md_moduleController[mModParent].get('root')
                                    if _buffer:
                                        print(_buffer)                                    
                                        mParentController = get_tag(_buffer[0])
                                        mController.parent_set(mParentController)                            
                            else:
                                if md_tmp.get('root'):
                                    _buffer = md_tmp.get('root')
                                    if _buffer:
                                        print(_buffer)                                    
                                        mParentController = get_tag(_buffer[0])
                                        mController.parent_set(mParentController)                             
                                    
                        """
                        if _b_face:
                            mMirror = mObj.getMessageAsMeta('mirrorControl')
                            if mMirror:
                                ml_children.append(mMirror)
                                
                            print mObj
                            pprint.pprint(ml_children)
                                """
                        
                        if mObj == _l_tag[-1]:
                            #....Last
                            for modChild in ml_modChildren:
                                _buffer = md_moduleController[modChild].get(tag)
                                if _buffer:
                                    print(_buffer)
                                    ml_children.append(_buffer[0])
                        else:
                            mChild = False
                            
                            try:mChild =_l_tag[ii+1]
                            except:
                                pass
                            
                            if mChild:
                                ml_children = [mChild]
                                
                                mMirror = mChild.getMessageAsMeta('mirrorControl')
                                if mMirror:
                                    ml_children.append(mMirror)
    
                        _msg = False
                        for iii,mChild in enumerate(ml_children):
                            try:
                                
                                if iii or _b_face:
                                    _msg =True
                                mChildController = get_tag(mChild)
                                mChildController.parent_set(mController,msgConnect=_msg)
                            except Exception as err:
                                log.error("Child Err: {0} | {1}".format(mChild,err))
                            
                    except Exception as err:
                        log.error("Err: {0} | {1}".format(mObj,err))
                
                if ml:
                    md_failsafe[ml[-1]] = ml[0]
            
        """
        for mController in ml_all:
            #print mController
            if not mController.children:
                if md_failsafe.get(mController):
                    log.info("|{0}| >>  Failsafe | {1} | parent: {2}".format(_str_func,
                                                                             mController.mNode,
                                                                             md_failsafe.get(mController).mNode))
                    
                    md_failsafe.get(mController).parent_set( mController, msgConnect=True)
        """
    
        if ml_controlOrphans:
            log.error(cgmGEN.logString_sub(_str_func,"Orphans!"))
            pprint.pprint(ml_controlOrphans)
    
        if progressBar and progressEnd:
            cgmUI.progressBar_end(progressBar)
            
        return
    except Exception as err:
        pprint.pprint(vars())
        log.error("controller_verify | {0}".format(err))

@cgmGEN.Timer
def controller_purge(self,progressBar = None,progressEnd=True):
    """
    Verify the mirror setup of the puppet modules
    """
    _str_func = ' controller_purge'.format(self)
    log.debug("|{0}| >> ... [{1}]".format(_str_func,self)+ '-'*80)
    
    if self.isReferenced():
        log.debug("|{0}| >> can't process referenced asset | {1}".format(_str_func,self))        
        return 
    
    
    ml_modules = modules_getHeirarchal(self,True)
    int_lenModules = len(ml_modules)
    
    if progressBar:
        cgmUI.progressBar_start(progressBar)
    else:
        progressBar = cgmUI.doStartMayaProgressBar()
        

    #Self controls =====================================================
    #ml_self = controls_get(self)
    #process_set(ml_self)
    
    #mPuppetController = self.controller_get()
    
    #>> Process ======================================================================================
    
    for i,mModule in enumerate(ml_modules):
        if progressBar:
            _str = '{0}'.format(mModule.mNode)
            log.info(cgmGEN.logString_sub(_str_func,_str))
            cgmUI.progressBar_set(progressBar,
                                  minValue = 0,
                                  maxValue=int_lenModules+1,
                                  status = _str,
                                  progress=i, vis=True)
            
        md = mModule.atUtils('get_mirrorDat',False)

        for mObj in md['ml_controls']:
            l_delete = mObj.getMessage('mController')
            if l_delete:
                mc.delete(l_delete)


    if progressBar and progressEnd:
        cgmUI.progressBar_end(progressBar)
        
    return

@cgmGEN.Timer
def puppetMesh_create(self,unified=True,skin=False, proxy = False, forceNew=True):
    _str_func = 'puppetMesh_create'
    log.debug("|{0}| >>  Unified: {1} | Skin: {2} ".format(_str_func,unified,skin)+ '-'*80)
    log.debug("{0}".format(self))
    
    mPuppet = self
    mParent = False
    if skin:
        #mModuleTarget = self.getMessage('moduleTarget',asMeta=True)
        #if not mModuleTarget:
        #    return log.error("|{0}| >> Must have moduleTarget for skining mode".format(_str_func))
        #mModuleTarget = mModuleTarget[0]        
        
        #mPuppet = puppet_get(self,mModuleTarget)
        #if not mPuppet:
        #    return log.error("|{0}| >> Must have puppet for skining mode".format(_str_func))        
        """
        mPuppet = mModuleTarget.getMessageAsMeta('modulePuppet')
        if not mPuppet:
            mRoot = self.p_blockRoot
            if mRoot:
                log.debug("|{0}| >>  Checking root for puppet: {1} ".format(_str_func,mRoot))
                mPuppetTest = mRoot.getMessageAsMeta('moduleTarget')
                log.debug("|{0}| >>  root target: {1} ".format(_str_func,mPuppetTest))
                if mPuppetTest and mPuppetTest.mClass == 'cgmRigPuppet':
                    mPuppet = mPuppetTest
                else:
                    mPuppet = False
            if not mPuppet:
                return log.error("|{0}| >> Must have puppet for skining mode".format(_str_func))"""
            
        mGeoGroup = mPuppet.masterNull.geoGroup
        mParent = mGeoGroup
        log.debug("|{0}| >> mPuppet: {1}".format(_str_func,mPuppet))
        log.debug("|{0}| >> mGeoGroup: {1}".format(_str_func,mGeoGroup))        
        #log.debug("|{0}| >> mModuleTarget: {1}".format(_str_func,mModuleTarget))
    
    
    if proxy:
        if not mPuppet.masterControl.controlSettings.skeleton:
            log.warning("|{0}| >> Skeleton was off. proxy mesh in puppetMeshMode needs a visible skeleton to see. Feel free to turn it back off if you like.".format(_str_func, self.mNode))            
            mPuppet.masterControl.controlSettings.skeleton = 1        
    
    
    #Check for existance of mesh ========================================================================
    if mPuppet:
        bfr = mPuppet.msgList_get('puppetMesh',asMeta=True)
        if skin and bfr:
            log.debug("|{0}| >> puppetMesh detected...".format(_str_func))            
            if forceNew:
                log.debug("|{0}| >> force new...".format(_str_func))                            
                mc.delete([mObj.mNode for mObj in bfr])
            else:
                return bfr
    
    #if proxy:
        #if unified:
        #    log.warning("|{0}| >> Proxy mode detected, unified option overridden".format(_str_func))
        #    unified = False
        #if skin:
        #    log.warning("|{0}| >> Proxy mode detected, skin option overridden".format(_str_func))
        #    skin = False
    
    #Process-------------------------------------------------------------------------------------
    #if self.blockType == 'master':
    #    mRoot = self
    #else:
    #    mRoot = self.getBlockParents()[-1]
    mRoot = self.rigBlock
        
    log.debug("|{0}| >> mRoot: {1}".format(_str_func,mRoot))
    ml_ordered = mRoot.getBlockChildrenAll()
    ml_mesh = []
    subSkin = False
    if skin:
        #if not unified:
        subSkin=True
            
    for mBlock in ml_ordered:
        if mBlock.blockType in ['master', 'eyeMain']:
            log.debug("|{0}| >> unmeshable: {1}".format(_str_func,mBlock))
            continue
        log.debug("|{0}| >> Meshing... {1}".format(_str_func,mBlock))
        
        if proxy and mBlock.blockType not in ['eye']:
            _res = mBlock.verify_proxyMesh(forceNew = True, puppetMeshMode=True,skin=subSkin)
            if _res:ml_mesh.extend(_res)
            
        else:
            _res = mBlock.UTILS.create_simpleMesh(mBlock,skin=subSkin,forceNew=subSkin,deleteHistory=True,)
            if _res:ml_mesh.extend(_res)
        
        """
        if skin:
            mModuleTarget = mBlock.getMessage('moduleTarget',asMeta=True)
            if not mModuleTarget:
                return log.error("|{0}| >> Must have moduleTarget for skining mode".format(_str_func))
            mModuleTarget = mModuleTarget[0]
            mModuleTarget.atUtils('rig_connect')
            ml_joints = mModuleTarget.rigNull.msgList_get('moduleJoints')
            if not ml_joints:
                return log.error("|{0}| >> Must have moduleJoints for skining mode".format(_str_func))
            ml_moduleJoints.extend(ml_joints)"""
        
    if unified:
        if skin:
            #self.msgList_connect('simpleMesh',ml_mesh)
            mMesh = None
            for mObj in ml_mesh:
                TRANS.pivots_zeroTransform(mObj)
                mObj.dagLock(False)
                mObj.p_parent = False
            #Have to dup and copy weights because the geo group isn't always world center
            if len(ml_mesh)>1:
                mMesh = cgmMeta.validateObjListArg(mc.polyUniteSkinned([mObj.mNode for mObj in ml_mesh],ch=0))
                mMesh = mMesh[0]
            elif ml_mesh:
                mMesh = ml_mesh[0]
            
            if mMesh:
                mMesh.dagLock(False)
                
                #mMeshBase = mMeshBase[0]
                #mMesh = mMeshBase.doDuplicate(po=False,ic=False)
                mMesh.rename('{0}_unified_geo'.format(mPuppet.p_nameBase))
                mMesh.p_parent = mParent
                #cgmGEN.func_snapShot(vars())
                
                #now copy weights
                #CORESKIN.transfer_fromTo(mMeshBase.mNode, [mMesh.mNode])
                #mMeshBase.delete()
                
                ml_mesh = [mMesh]
                #ml_mesh[0].p_parent = mGeoGroup
                mMesh.dagLock(True)
            

        else:
            if len(ml_mesh)>1:
                ml_mesh = cgmMeta.validateObjListArg(mc.polyUnite([mObj.mNode for mObj in ml_mesh],ch=False))
        
        if ml_mesh:
            ml_mesh[0].rename('{}_puppetMesh_unified_geo'.format(mRoot.cgmName))
        
    if skin or proxy and ml_mesh:
        mPuppet.msgList_connect('puppetMesh',ml_mesh)
        
    #for mGeo in ml_mesh:
    #    CORERIG.color_mesh(mGeo.mNode,'puppetmesh')
        
    return ml_mesh

    #except Exception as err:cgmGEN.cgmExceptCB(Exception,err,localDat=vars())        
    