"""
------------------------------------------
block: cgm.core.mrs.lib
Author: Josh Burton
email: jjburton@cgmonks.com

Website : http://www.cgmonks.com
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
reload(RIGCONSTRAINT)
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
reload(cgmUI)
import cgm.core.rig.joint_utils as COREJOINTS
import cgm.core.lib.transform_utils as TRANS
import cgm.core.lib.ml_tools.ml_resetChannels as ml_resetChannels
import cgm.core.mrs.lib.shared_dat as BLOCKSHARE

#=============================================================================================================
#>> Queries
#=============================================================================================================
def example(self):
    try:
        _short = self.p_nameShort
        _str_func = ' example'.format(self)
        log.debug("|{0}| >> ... [{1}]".format(_str_func,self)+ '-'*80)
        
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err)
    
def get_shapeOffset(self):
    """
    Get the shape offset value 
    """
    try:
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
        
        
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err)
    
def modules_get(self):
    try:
        _str_func = ' modules_get'.format(self)
        log.debug("|{0}| >> ... [{1}]".format(_str_func,self)+ '-'*80)
        
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
                    
        return ml_allModules        
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err)
    
def modules_gather(self,**kws):
    try:
        _short = self.p_nameShort
        _str_func = ' modules_gather'.format(self)
        log.debug("|{0}| >> ... [{1}]".format(_str_func,self)+ '-'*80)
        
        ml_modules = modules_get(self)
        int_lenModules = len(ml_modules)
    
        for i,mModule in enumerate(ml_modules):
            _str_module = mModule.p_nameShort
            module_connect(self,mModule,**kws)
        return ml_modules
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err)
    
def module_connect(self,mModule,**kws):
    try:
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
       
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err)
    
    
def is_upToDate(self,report = True):
    _res = []
    
    if report:
        _short = self.p_nameBase
        print cgmGEN._str_hardBreak        
        print("|{0}| >> ".format(_short) + cgmGEN._str_subLine)
    
    for mModule in modules_get(self):
        _res.append( mModule.atUtils('is_upToDate',report) )
        
    if report:
        if False in _res:
            print("|{0}| >> OUT OF DATE ".format(_short))
        else:
            log.info("|{0}| >> build current. ".format(_short))
        print cgmGEN._str_hardBreak
        
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
    
    md_data = {}
    ml_modules = modules_get(self)
    
    d_runningSideIdxes = {'Centre':0,
                          'Left':0,
                          'Right':0}
    ml_processed = []
    
    ml_modules = modules_get(self)
    int_lenModules = len(ml_modules)
    
    
    if progressBar:
        cgmUI.progressBar_start(progressBar)
        
    for i,mModule in enumerate(ml_modules):
        if progressBar:
            cgmUI.progressBar_set(progressBar,
                                  minValue = 0,
                                  maxValue=int_lenModules+1,
                                  progress=i, vis=True)
        try:mModule.UTILS.mirror_verifySetup(mModule,d_runningSideIdxes,
                                             ml_processed,
                                             progressBar = progressBar,progressEnd=False)
        except Exception,err:
            log.error("{0} | {1}".format(mModule,err))
    
    if progressBar and progressEnd:
        cgmUI.progressBar_end(progressBar)
    
    return
    
    #>>>Module control maps ===============================================================================
    for i,mModule in enumerate(ml_modules):
        _str_module = mModule.p_nameShort
        md_data[mModule] = {}#...Initize a dict for this object
        _d = md_data[mModule]#...link it
        _d['str_name'] = _str_module
        
        md,ml = mModule.atUtils('controls_getDat')
        _d['md_controls'] = md
        _d['ml_controls'] = ml#mModule.rigNull.moduleSet.getMetaList()
        _d['mi_mirror'] = mModule.atUtils('mirror_get')
        _d['str_side'] = cgmGEN.verify_mirrorSideArg(mModule.getMayaAttr('cgmDirection') or 'center')

        if _d['str_side'] not in d_runningSideIdxes.keys():
            d_runningSideIdxes[_d['str_side']] = [0]
            

            #log.infoDict(_d,_str_module)        
    
    #pprint.pprint(vars())
    #return vars()
    return ml_modules
    #>>>Processing ========================================================================================
    ml_processed = []
    
    #for our first loop, we're gonna create our cull dict of sides of data to then match 
    for mModule in ml_modules:		
        log.info("|{0}| >> On: {1}".format(_str_func,mModule))
        if mModule in ml_processed:
            log.info("|{0}| >> Already processed...".format(_str_func,mModule))
            continue
        
        md_buffer = md_data[mModule.mNode]#...get the modules dict

        ml_modulesToDo = [mModule]#...append
        mi_mirror = md_buffer.get('mi_mirror',False)
        if mi_mirror:
                md_mirror = md_data[mi_mirror.mNode]
                int_controls = len(md_buffer['ml_controls'])
                int_mirrorControls = len(md_data[mi_mirror.mNode]['ml_controls'])
                if int_controls != int_mirrorControls:
                    raise ValueError,"Control lengths of mirrors do not match | mModule: {0} | mMirror: {1}".format(md_buffer['str_name'],md_mirror['str_name'])
                
                ml_modulesToDo.append(mi_mirror)#...append if we have it

        md_culling_controlLists = {'Centre':[],
                                    'Left':[],
                                    'Right':[]}
        
        for mi_module in ml_modulesToDo:
            log.info("|{0}| >> Sub module: {1}".format(_str_func,mi_module))
            md_buffer = md_data[mi_module.mNode]#...get the modules dict	

            str_mirrorSide = cgmGEN.verify_mirrorSideArg(mi_module.getMayaAttr('cgmDirection') or 'center')
            #log.info("module: {0} | str_mirrorSide: {1}".format(mi_module.p_nameShort,str_mirrorSide))
            for i,mObj in enumerate(md_buffer['ml_controls']):
                if not issubclass(type(mObj), cgmMeta.cgmControl):
                    mObj = cgmMeta.asMeta(mObj,'cgmControl',setClass = True)#,setClass = True
                    md_buffer[i] = mObj#...push back

                mObj._verifyMirrorable()#...veryify the mirrorsetup
                
                #if str_mode == 'template':
                #    if mObj.getMayaAttr('cgmType') in ['templateObject','templateOrientHelper','templateOrientRoot']:
                #        mObj.mirrorAxis = 'translateX,translateZ,rotateZ'                                        
                
                
                _mirrorSideFromCGMDirection = cgmGEN.verify_mirrorSideArg(mObj.getNameDict().get('cgmDirection','centre'))
                _mirrorSideCurrent = cgmGEN.verify_mirrorSideArg(mObj.getEnumValueString('mirrorSide'))
                #if not _mirrorSideCurrent:
                    #raise ValueError,"Mirror side is wrong {0} | {1}".format(mObj,ATTR.get(mObj.mNode,'mirrorSide'))
                #log.info("_mirrorSideFromCGMDirection: {0} ".format(_mirrorSideFromCGMDirection))
                #log.info("_mirrorSideCurrent: {0}".format(_mirrorSideCurrent))
                
                _setMirrorSide = False
                if _mirrorSideFromCGMDirection:
                    if _mirrorSideFromCGMDirection != _mirrorSideCurrent:
                        log.info("{0}'s cgmDirection ({1}) is not it's mirror side({2}). Resolving...".format(mObj.p_nameShort,_mirrorSideFromCGMDirection,_mirrorSideCurrent))
                        _setMirrorSide = _mirrorSideFromCGMDirection                                            
                elif not _mirrorSideCurrent:
                    _setMirrorSide = str_mirrorSide
                    
                if _setMirrorSide:
                    if not cgmMeta.cgmAttr(mObj,'mirrorSide').getDriver():
                        mObj.doStore('mirrorSide',_setMirrorSide)
                        
                        #mObj.mirrorSide = _setMirrorSide
                        #log.info("{0} mirrorSide set to: {1}".format(mObj.p_nameShort,_setMirrorSide))
                    else:
                        pass
                        #log.info("{0} mirrorSide driven".format(mObj.p_nameShort))
                   
                #append the control to our lists to process                                    
                md_culling_controlLists[mObj.getEnumValueString('mirrorSide')].append(mObj)

            ml_processed.append(mi_module)#...append
        
        cgmGEN.log_info_dict(md_culling_controlLists, "Culling lists")
        
        #...Map...
        _d_mapping = {'Centre':{'ml':md_culling_controlLists['Centre'],
                                'startIdx':max(d_runningSideIdxes['Centre'])+1},
                      'Sides':{'Left':{'ml':md_culling_controlLists['Left'],
                                       'startIdx':max(d_runningSideIdxes['Left'])+1},
                               'Right':{'ml':md_culling_controlLists['Right'],
                                       'startIdx':max(d_runningSideIdxes['Right'])+1}}}                                            
        
        for key,_d in _d_mapping.iteritems():
            if key is 'Centre':
                int_idxRunning = _d['startIdx']
                _ml = _d['ml']
                for mObj in _ml:
                    log.info("'{0}' idx:{1}".format(mObj.p_nameShort,int_idxRunning))
                    ATTR.set(mObj.mNode,'mirrorIndex',int_idxRunning)
                    d_runningSideIdxes['Centre'].append(int_idxRunning)
                    int_idxRunning+=1
            else:
                _ml_left = _d['Left']['ml']
                _ml_right = _d['Right']['ml']
                _ml_left_cull = copy.copy(_ml_left)
                _ml_right_cull = copy.copy(_ml_right)                            
                int_idxRun_left = _d['Left']['startIdx']
                int_idxRun_right = _d['Right']['startIdx']
                _md_tags_l = {}
                _md_tags_r = {}
                for mObj in _ml_left:
                    _md_tags_l[mObj] = mObj.getCGMNameTags(['cgmDirection'])
                for mObj in _ml_right:
                    _md_tags_r[mObj] = mObj.getCGMNameTags(['cgmDirection'])
                    
                for mObj in _ml_left:
                    #See if we can find a match
                    _match = []
                    l_tags = _md_tags_l[mObj]
                    for mObj2, r_tags in _md_tags_r.iteritems():#first try to match by tags
                        if l_tags == r_tags:
                            _match.append(mObj2)
                            
                    if not _match:
                        #Match by name
                        _str_l_nameBase = str(mObj.p_nameBase)
                        if _str_l_nameBase.startswith('l_'):
                            _lookfor = 'r_' + ''.join(_str_l_nameBase.split('l_')[1:])
                            log.info("Startwith check. Looking for {0}".format(_lookfor))                                        
                            for mObj2 in _ml_right:
                                if str(mObj2.p_nameBase) == _lookfor:
                                    _match.append(mObj2)
                                    log.info("Found startswithNameMatch: {0}".format(_lookfor))
                        elif _str_l_nameBase.count('left'):
                            _lookfor = _str_l_nameBase.replace('left','right')
                            log.info("Contains 'left' check. Looking for {0}".format(_lookfor))                                                                                                                        
                            for mObj2 in _ml_right:
                                if str(mObj2.p_nameBase) == _lookfor:
                                    _match.append(mObj2)
                                    log.info("Found contains 'left name match: {0}".format(_lookfor))                                        
                    if len(_match) == 1:
                        while int_idxRun_left in d_runningSideIdxes['Left'] or int_idxRun_right in d_runningSideIdxes['Right']:
                            #log.info("Finding available indexes...")
                            int_idxRun_left+=1
                            int_idxRun_right+=1
                            
                        ATTR.set(mObj.mNode,'mirrorIndex',int_idxRun_left)
                        ATTR.set(_match[0].mNode,'mirrorIndex',int_idxRun_right)                                    
                        d_runningSideIdxes['Left'].append(int_idxRun_left)
                        d_runningSideIdxes['Right'].append(int_idxRun_right)
                        _ml_left_cull.remove(mObj)
                        _ml_right_cull.remove(_match[0])
                        mObj.connectChildNode(_match[0],'cgmMirrorMatch','cgmMirrorMatch')
                        log.info("'{0}' idx:{1} <---Match--> '{2}' idx:{3}".format(mObj.p_nameShort,int_idxRun_left,_match[0].p_nameShort,int_idxRun_right))
                    elif len(_match)>1:
                        raise ValueError,"Too many matches! mObj:{0} | Matches:{1}".format(mObj.p_nameShort,[mObj2.p_nameShort for mObj2 in _match])
                for mObj in _ml_left_cull + _ml_right_cull:
                    ml_noMatch.append(mObj)
                    #log.info("NO MATCH >>>> mObj:'{0}' NO MATCH".format(mObj.p_nameShort))
        #_l_centre = md_culling_controlLists['Centre']
        #_l_right = md_culling_controlLists['Left']
        #_l_left = md_culling_controlLists['Right']
        #Centre
        #int_idxStart = max(d_runningSideIdxes['Centre'])
        #int_idxStart = max(d_runningSideIdxes[str_mirrorSide])
        #int_idxRunning = int_idxStart + 1                    
        
        #for k in md_culling_controlLists.keys():


    for mObj in ml_noMatch:
        log.info("NO MATCH >>>> mObj:'{0}' NO MATCH".format(mObj.p_nameBase))
    return True
    
    
    

def mirror_getNextIndex(self,side):
    try:
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
     
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err)
    
    
    
def mirror_getDict(self):
    try:
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
     
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err)
    
#=============================================================================================================
#>> Anim
#=============================================================================================================
def modules_settings_set(self,**kws):
    try:
        _str_func = ' modules_settings_set'.format(self)
        log.debug("|{0}| >> ... [{1}]".format(_str_func,self)+ '-'*80)
        
        for mModule in modules_get(self):
            if mModule.rigNull.getMessage('settings'):
                mSettings = mModule.rigNull.settings
                _short_settings = mSettings.mNode
                for k,v in kws.iteritems():
                    try:
                        ATTR.set(_short_settings,k,v)
                    except Exception,err:
                        #if mSettings.hasAttr(k):
                        log.debug("|{0}| >>  Failed to set: mModule:{1} | k:{2} | v:{3} | {4}".format(_str_func,mModule.mNode,k,v,err))
            else:
                log.debug("|{0}| >>  Missing settings: {1}".format(_str_func,mModule))
        return True        
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err)
    
def anim_reset(self,transformsOnly = True):
    try:
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
        
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err)
    
def anim_select(self):
    try:
        _str_func = ' anim_select'.format(self)
        log.debug("|{0}| >> ... [{1}]".format(_str_func,self)+ '-'*80)
        self.puppetSet.select()
        return True        
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err)
    
def anim_key(self,**kws):
    try:
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
        
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err)
    
@cgmGEN.Timer
def layer_verify(self,**kws):
    try:
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
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err)
    
    
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
        raise StandardError,"Failed to connect masterNull to puppet network!"

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
        raise Exception,"No root motion handle found. "
    
    RIGCONSTRAINT.driven_connect(mRootJoint,mRootMotionHandle)
    
    return True
    
    
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
    
    if puppetSet:
        log.debug("|{0}| >> puppetSet...".format(_str_func)+'-'*40)        
        
        mSet = self.getMessageAsMeta('puppetSet')
        if not mSet:
            mSet = cgmMeta.cgmObjectSet(setType='animSet',qssState=True)
            mSet.connectParentNode(self.mNode,'puppet','puppetSet')
            #ATTR.copy_to(self.mNode,'cgmName',mSet.mNode,'cgmName',driven = 'target')
            mSet.doStore('cgmName','all')
            
        mSet.doName()
        
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
        log.debug("|{0}| >> exportSet: {1}".format(_str_func,mSet))
        mMaster = self.masterNull
        for mGrp in mMaster.skeletonGroup,mMaster.geoGroup:
            for mChild in mGrp.getChildren(asMeta=1):
                mSet.addObj(mChild.mNode)
        #for mObj in get_joints(self,'bind') + get_rigGeo(self):
            #mSet.addObj(mObj.mNode)    
        
def groups_verify(self):
    try:
        _str_func = "groups_verify".format()
        log.debug("|{0}| >> ...".format(_str_func))
    
        mMasterNull = self.masterNull
    
        if not mMasterNull:
            raise ValueError, "No masterNull"
    
        for attr in ['rig','deform','noTransform','geo','skeleton',
                     'parts','worldSpaceObjects','puppetSpaceObjects']:
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
                
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err)

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
        if mObj.getMayaAttr('cgmType') in ['dynDriver']:
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
            
        if mObj.getMayaAttr('cgmType') in ['dynDriver']:
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
            raise ValueError,"Unknown mode: {0}".format(mode)
        _res.extend(ml)
        
    return _res
        

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
        except Exception,err:
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
            except Exception,err:
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
        raise ValueError,"Unknown mode: {0}".format(mode)
    for i,mModule in enumerate([self] + ml_modules):
        if progressBar:
            cgmUI.progressBar_set(progressBar,
                                  status = mModule.p_nameShort,
                                  progress=i, vis=True)
            
        try:
            mModule.atUtils(_d_modeToCall.get(mode))
        except Exception,err:
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
        except Exception,err:
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
            mRigBlock.verify_proxyMesh(forceNew,puppetMeshMode)
        except Exception,err:
            log.error("{0} | {1}".format(mRigBlock,err))
    
    if progressBar and progressEnd:
        cgmUI.progressBar_end(progressBar)
        
        
#Controls dat ===========================================================================        
l_controlOrder = ['root','settings','motionHandle']
d_controlLinks = {'root':['masterControl'],
                  'motionHandle':['rootMotionHandle'],
                  'pivots':['pivot{0}'.format(n.capitalize()) for n in BLOCKSHARE._l_pivotOrder]}

def controls_getDat(self, keys = None, ignore = [], report = False, listOnly = False):
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

    if report:
        log.info("|{0}| >> Dict... ".format(_str_func))
        pprint.pprint( md_controls)

        log.info("|{0}| >> List... ".format(_str_func))
        pprint.pprint( ml_controls)

    if ml_objs and keys is None and not ignore:        
        log.debug("|{0}| >> remaining... ".format(_str_func))
        pprint.pprint( ml_objs)
        raise ValueError,("|{0}| >> Resolve missing controls!".format(_str_func))
        #return log.error("|{0}| >> Resolve missing controls!".format(_str_func))

    if report:
        return

    if keys or listOnly:
        return ml_controls
    return md_controls,ml_controls

def controls_get(self,walk=False):
    _str_func = ' controls_get'
    _res = controls_getDat(self,listOnly=True)
    if not walk:
        return _res
    
    for mModule in modules_get(self):
        _res.extend( mModule.atUtils('controls_get'))
    return _res
        
    log.error("|{0}| >> No options specified".format(_str_func))
    return False