"""
------------------------------------------
Builder: cgm.core.mrs
Author: Josh Burton
email: jjburton@cgmonks.com

Website : http://www.cgmonks.com
------------------------------------------

================================================================
"""
import random
import re
import copy
import time
import os
# From Red9 =============================================================
from Red9.core import Red9_Meta as r9Meta
from Red9.core import Red9_AnimationUtils as r9Anim

#========================================================================
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
#========================================================================

import maya.cmds as mc


# From cgm ==============================================================
from cgm.core import cgm_General as cgmGEN
from cgm.core import cgm_Meta as cgmMeta
from cgm.core import cgm_RigMeta as RIGMETA
from cgm.core import cgm_PuppetMeta as PUPPETMETA
from cgm.core.classes import GuiFactory as CGMUI
reload(CGMUI)
from cgm.core.lib import curve_Utils as CURVES
from cgm.core.lib import attribute_utils as ATTR
from cgm.core.lib import position_utils as POS
from cgm.core.lib import math_utils as MATH
from cgm.core.lib import distance_utils as DIST
from cgm.core.lib import snap_utils as SNAP
from cgm.core.lib import rigging_utils as RIGGING
from cgm.core.rigger.lib import joint_Utils as JOINTS
from cgm.core.lib import search_utils as SEARCH
from cgm.core.lib import rayCaster as RAYS
from cgm.core.cgmPy import validateArgs as VALID
from cgm.core.classes import NodeFactory as NODEFAC
from cgm.core.cgmPy import path_Utils as PATH
from cgm.core.mrs import RigBlocks as RIGBLOCKS
reload(RIGBLOCKS)
#from cgm.core.mrs.blocks import box
from cgm.core.lib import shared_data as SHARED

_d_blockTypes = {}


#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Factory
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
class go(object):
    def __init__(self, rigBlock = None, forceNew = True, autoBuild = True, ignoreRigCheck = False,
                 *a,**kws):
        """
        Core rig block builder factory

        :parameters:
            rigBlock(str) | base rigBlock

        :returns
            factory instance
            
            
        """
        _str_func = 'go._init_'
        _start = time.clock()
        
        #>>Initial call ---------------------------------------------------------------------------------
        self._callBlock = None
        self._call_kws = {}
        self._rigBlock = None
        self._d_block = {}
        self._d_module = {}
        self._d_joints = {}
        self._d_orientation = {}         
        self._md_controlShapes = {} 
        
        if a:log.debug("|{0}| >> a: {1}".format(_str_func,a))
        if kws:#...intial population
            self._call_kws = kws
            #log.debug("|{0}| >> kws: {1}".format(_str_func,kws))
        
        self._call_kws['forceNew'] = forceNew
        self._call_kws['rigBlock'] = rigBlock
        self._call_kws['autoBuild'] = autoBuild
        self._call_kws['ignoreRigCheck'] = ignoreRigCheck
        cgmGEN.log_info_dict(self._call_kws,_str_func)
        
        if not self.fnc_check_rigBlock():
            raise RuntimeError,"|{0}| >> RigBlock checks failed. See warnings and errors.".format(_str_func)
        log.debug("|{0}| >> RigBlock check passed".format(_str_func) + cgmGEN._str_subLine)
   
        if not self.fnc_check_module():
            raise RuntimeError,"|{0}| >> Module checks failed. See warnings and errors.".format(_str_func)
        log.debug("|{0}| >> Module check passed...".format(_str_func)+ cgmGEN._str_subLine)
        
        if not self.fnc_rigNeed():
            raise RuntimeError,"|{0}| >> No rig need see errors".format(_str_func)
        log.debug("|{0}| >> Rig needed...".format(_str_func)+ cgmGEN._str_subLine)
        
        if not self.fnc_bufferDat():
            raise RuntimeError,"|{0}| >> Failed to buffer data. See warnings and errors.".format(_str_func)
            
        if not self.fnc_moduleRigChecks():
            raise RuntimeError,"|{0}| >> Failed to process module rig Checks. See warnings and errors.".format(_str_func)
            
        if not self.fnc_deformConstrainNulls():
            raise RuntimeError,"|{0}| >> Failed to process deform/constrain. See warnings and errors.".format(_str_func)
            
        self.fnc_processBuild(**kws)
        
        log.debug("|{0}| >> Time >> = {1} seconds".format(_str_func, "%0.3f"%(time.clock()-_start)))                

        #_verify = kws.get('verify',False)
        #log.debug("|{0}| >> verify: {1}".format(_str_func,_verify))
        
    def __repr__(self):
        try:return "{0}(rigBlock: {1})".format(self.__class__, self._rigBlock)
        except:return self

    def fnc_check_rigBlock(self):
        """
        Check the rig block data 
        """
        _str_func = 'fnc_check_rigBlock' 
        _d = {}
        _res = True
        _start = time.clock()
        
        if not self._call_kws['rigBlock']:
            log.error("|{0}| >> No rigBlock stored in call kws".format(_str_func))
            return False
        
        BlockFactory = RIGBLOCKS.factory(self._call_kws['rigBlock'])
        BlockFactory.verify()
        
        _d['mBlock'] = BlockFactory._mi_root
        self._rigBlock = _d['mBlock']
        _d['mFactory'] = BlockFactory
        _d['shortName'] = BlockFactory._mi_root.getShortName()
        
        _blockType = _d['mBlock'].blockType
        _res = get_block_lib_dat()
        if _res[0].get(_blockType) and _blockType not in _res[2]:
            _buildModule = _res[0].get(_blockType)
            
        if not _buildModule:
            log.error("|{0}| >> No build module found for: {1}".format(_str_func,_d['mBlock'].blockType))        
            return False
        _d['buildModule'] =  _buildModule   #if not is_buildable
        _d['buildVersion'] = _buildModule.__version__
    
        self._d_block = _d    
        cgmGEN.log_info_dict(_d,_str_func + " blockDat")   
        log.debug("|{0}| >> Time >> = {1} seconds".format(_str_func, "%0.3f"%(time.clock()-_start)))                
        
        return True
        
    
    def fnc_check_module(self):
        _str_func = 'fnc_check_module'  
        _res = True
        BlockFactory = self._d_block['mFactory']
        _start = time.clock()
        
        #>>Module -----------------------------------------------------------------------------------  
        _d = {}    
        BlockFactory.module_verify()
        _mModule = BlockFactory._mi_module
        self._mi_module = _mModule
        
        _mRigNull = _mModule.rigNull
        _d['mModule'] = _mModule
        _d['mRigNull'] = _mRigNull
        self._mi_rigNull = _mRigNull
        _d['shortName'] = _mModule.getShortName()
        _d['version'] = _mModule.rigNull.version
        
        _d['mModuleParent'] = False
        if _mModule.getMessage('moduleParent'):
            _d['mModuleParent'] = _mModule.moduleParent
            
            
        if not _mRigNull.getMessage('dynSwitch'):
            _mDynSwitch = RIGMETA.cgmDynamicSwitch(dynOwner=_mRigNull.mNode)
            log.debug("|{0}| >> Created dynSwitch: {1}".format(_str_func,_mDynSwitch))        
        else:
            _mDynSwitch = _mRigNull.dynSwitch  
        _d['mDynSwitch'] = _mDynSwitch
            
        #>>Puppet -----------------------------------------------------------------------------------    
        BlockFactory.puppet_verify()
        _mPuppet = _mModule.modulePuppet
        self._mi_puppet = _mPuppet
        
        _d['mPuppet'] = _mPuppet
        _mPuppet.__verifyGroups__()
        
        if not _mModule.isSkeletonized():
            log.warning("|{0}| >> Module isn't skeletonized. Attempting".format(_str_func))
            
            BlockFactory.skeletonize(True)
            if not _mModule.isSkeletonized():
                log.warning("|{0}| >> Skeletonization failed".format(_str_func))            
                _res = False
        
        self._d_module = _d    
        log.debug("|{0}| >> Time >> = {1} seconds".format(_str_func, "%0.3f"%(time.clock()-_start)))                
        #cgmGEN.log_info_dict(_d,_str_func + " moduleDat")    
        return _res    
    
    
    def fnc_moduleRigChecks(self):
        """
        Verify the module's rig visibility toggles and object set
        """
        _str_func = 'fnc_moduleRigChecks'  
        _res = True
        _start = time.clock()
        
        
        #>>Connect switches ----------------------------------------------------------------------------------- 
        _str_settings = self._d_module['mMasterSettings'].getShortName()
        _str_partBase = self._d_module['partName'] + '_rig'
        _str_moduleRigNull = self._d_module['mRigNull'].getShortName()
        
        _mMasterSettings = self._d_module['mMasterSettings']
        
        _mMasterSettings.addAttr(_str_partBase,enumName = 'off:lock:on', defaultValue = 0, attrType = 'enum',keyable = False,hidden = False)
        
        try:NODEFAC.argsToNodes("{0}.gutsVis = if {1}.{2} > 0".format(_str_moduleRigNull,
                                                                    _str_settings,
                                                                    _str_partBase)).doBuild()
        except Exception,err:
            raise Exception,"|{0}| >> visArg failed [{1}]".format(_str_func,err)
        
        try:NODEFAC.argsToNodes("{0}.gutsLock = if {1}.{2} == 2:0 else 2".format(_str_moduleRigNull,
                                                                              _str_settings,
                                                                              _str_partBase)).doBuild()
        except Exception,err:
            raise Exception,"|{0}| >> lock arg failed [{1}]".format(_str_func,err)
    
        self._d_module['mRigNull'].overrideEnabled = 1		
        cgmMeta.cgmAttr(_str_moduleRigNull,'gutsVis',lock=False).doConnectOut("%s.%s"%(_str_moduleRigNull,'overrideVisibility'))
        cgmMeta.cgmAttr(_str_moduleRigNull,'gutsLock',lock=False).doConnectOut("%s.%s"%(_str_moduleRigNull,'overrideDisplayType'))    
    
        #log.debug("%s >> Time >> = %0.3f seconds " % (_str_funcName,(time.clock()-start)) + "-"*75)   
        
       
        #>>> Object Set -----------------------------------------------------------------------------------
        self._mi_module.__verifyObjectSet__()
        
        log.debug("|{0}| >> Time >> = {1} seconds".format(_str_func, "%0.3f"%(time.clock()-_start)))            
        
        return _res
    
    def fnc_rigNeed(self):
        """
        Function to check if a go instance needs to be rigged
        
        """
        _str_func = 'fnc_rigNeed'  
        
        _mModule = self._d_module['mModule']    
        _mModuleParent = self._d_module['mModuleParent']
        _version = self._d_module['version']
        _buildVersion = self._d_block['buildVersion']
        
        _d_callKWS = self._call_kws
        
        if _mModuleParent:
            _str_moduleParent = _mModuleParent.getShortName()
            if not _mModuleParent.isRigged():
                log.warning("|{0}| >> [{1}] ModuleParent not rigged".format(_str_func,_str_moduleParent))            
                return False
            
        _b_rigged = _mModule.isRigged()
        log.debug("|{0}| >> Rigged: {1}".format(_str_func,_b_rigged))            
        
        if _b_rigged and not _d_callKWS['forceNew'] and _d_callKWS['ignoreRigCheck'] is not True:
            log.warning("|{0}| >> Already rigged and not forceNew".format(_str_func))                    
            return False
                 
        self._b_outOfDate = False
        if _version != _buildVersion:
            self._b_outOfDate = True
            log.warning("|{0}| >> Versions don't match: rigNull: {1} | buildModule: {2}".format(_str_func,_version,_buildVersion))                            
        else:
            if _d_callKWS['forceNew'] and _mModule.isRigged():
                log.warning("|{0}| >> Force new and is rigged. Deleting rig...".format(_str_func))                    
                #_mModule.rigDelete()
            else:
                log.info("|{0}| >> Up to date.".format(_str_func))                    
                return False
        
        return True
        
        
    def fnc_bufferDat(self):
        """
        Function to check if a go instance needs to be rigged
        
        """
        _str_func = 'fnc_bufferDat'  
        
        _mModule = self._d_module['mModule']    
        _mModuleParent = self._d_module['mModuleParent']
        _mPuppet = self._d_module['mPuppet']
        _mRigNull = self._d_module['mRigNull']
        _version = self._d_module['version']
        _buildVersion = self._d_block['buildVersion']
        
        _d_callKWS = self._call_kws
        
        #>>Module dat ------------------------------------------------------------------------------
        _d = {}
        _d['partName'] = _mModule.getPartNameBase()
        _d['partType'] = _mModule.moduleType.lower() or False
        
        _d['l_moduleColors'] = _mModule.getModuleColors() 
        _d['l_coreNames'] = []#...need to do this
        self._mi_templateNull = _mModule.templateNull
        _d['mTemplateNull'] = self._mi_templateNull
        _d['bodyGeo'] = _mPuppet.getGeo() or ['Morphy_Body_GEO']
        _d['direction'] = _mModule.getAttr('cgmDirection')
        
        _d['mirrorDirection'] = _mModule.get_mirrorSideAsString()
        _d['f_skinOffset'] = _mPuppet.getAttr('skinDepth') or 1
        _d['mMasterNull'] = _mPuppet.masterNull
        
        #>MasterControl....
        if not _mPuppet.getMessage('masterControl'):
            log.info("|{0}| >> Creating masterControl...".format(_str_func))                    
            _mPuppet._verifyMasterControl(size = 5)
            
        _d['mMasterControl'] = _mPuppet.masterControl
        _d['mPlug_globalScale'] =  cgmMeta.cgmAttr(_d['mMasterControl'].mNode,'scaleY')	 
        _d['mMasterSettings'] = _d['mMasterControl'].controlSettings
        _d['mMasterDeformGroup'] = _mPuppet.masterNull.deformGroup
        
        _d['mMasterNull'].worldSpaceObjectsGroup.parent = _mPuppet.masterControl
          
        self._d_module.update(_d)
        
        cgmGEN.log_info_dict(self._d_module,_str_func + " moduleDat")      
        log.info(cgmGEN._str_subLine)
        
    
        #>>Joint dat ------------------------------------------------------------------------------
        _d = {}
        
        _d['ml_moduleJoints'] = _mRigNull.msgList_get('moduleJoints',cull=True)
        if not _d['ml_moduleJoints']:
            log.warning("|{0}| >> No module joints found".format(_str_func))                    
            return False
        
        _d['l_moduleJoints'] = []
        
        for mJnt in _d['ml_moduleJoints']:
            _d['l_moduleJoints'].append(mJnt.p_nameShort)
            ATTR.set(mJnt.mNode,'displayLocalAxis',0)
            
        _d['ml_skinJoints'] = _mModule.rig_getSkinJoints()
        if not _d['ml_skinJoints']:
            log.warning("|{0}| >> No skin joints found".format(_str_func))                    
            return False      
        
        
        self._d_joints = _d
        cgmGEN.log_info_dict(self._d_joints,_str_func + " jointsDat")      
        log.info(cgmGEN._str_subLine)    
        
        #>>Orientation dat ------------------------------------------------------------------------------
        _d = {}
        
        _mOrientation = VALID.simpleOrientation('zyx')#cgmValid.simpleOrientation(str(modules.returnSettingsData('jointOrientation')) or 'zyx')
        _d['str'] = _mOrientation.p_string
        _d['vectorAim'] = _mOrientation.p_aim.p_vector
        _d['vectorUp'] = _mOrientation.p_up.p_vector
        _d['vectorOut'] = _mOrientation.p_out.p_vector
        
        _d['vectorAimNeg'] = _mOrientation.p_aimNegative.p_vector
        _d['vectorUpNeg'] = _mOrientation.p_upNegative.p_vector
        _d['vectorOutNeg'] = _mOrientation.p_outNegative.p_vector    
        
        self._d_orientation = _d
        cgmGEN.log_info_dict(self._d_orientation,_str_func + " orientationDat")      
        log.info(cgmGEN._str_subLine)    
        
        return True
        
    
        
    def fnc_deformConstrainNulls(self):
        """
        Verify the module's rig visibility toggles and object set
        """
        _str_func = 'fnc_deformConstrainNulls'  
        _res = True
        _start = time.clock()
        
        
        #>>Connect switches ----------------------------------------------------------------------------------- 
        _str_partType = self._d_module['partType']
        _str_partName= self._d_module['partName']
        
        _mMasterSettings = self._d_module['mMasterSettings']
        _mi_moduleParent = self._d_module['mModuleParent']
        _ml_skinJoints = self._d_joints['ml_skinJoints']
        
        if not self._mi_module.getMessage('deformNull'):
            if _str_partType in ['eyebrow', 'mouthnose']:
                raise ValueError,"not implemented"
                """
                #Make it and link it ------------------------------------------------------
                buffer = rigging.groupMeObject(self.str_faceAttachJoint,False)
                i_grp = cgmMeta.asMeta(buffer,'cgmObject',setClass=True)
                i_grp.addAttr('cgmName',self._partName,lock=True)
                i_grp.addAttr('cgmTypeModifier','deform',lock=True)	 
                i_grp.doName()
                i_grp.parent = self._i_faceDeformNull	
                self._mi_module.connectChildNode(i_grp,'deformNull','module')
                self._mi_module.connectChildNode(i_grp,'constrainNull','module')
                self._i_deformNull = i_grp#link"""
            else:
                #Make it and link it
                if _str_partType in ['eyelids']:
                    buffer =  RIGGING.group_me(_mi_moduleParent.deformNull.mNode,False)			
                else:
                    buffer =  RIGGING.group_me(_ml_skinJoints[0].mNode,False)
    
                i_grp = cgmMeta.asMeta(buffer,'cgmObject',setClass=True)
                i_grp.addAttr('cgmName',_str_partName,lock=True)
                i_grp.addAttr('cgmTypeModifier','deform',lock=True)	 
                i_grp.doName()
                i_grp.parent = self._d_module['mMasterDeformGroup'].mNode
                self._mi_module.connectChildNode(i_grp,'deformNull','module')
                if _str_partType in ['eyeball']:
                    self._mi_module.connectChildNode(i_grp,'constrainNull','module')	
                    i_grp.parent = self._i_faceDeformNull				
        self._mi_deformNull = self._mi_module.deformNull
    
    
        if not self._mi_module.getMessage('constrainNull'):
            #if _str_partType not in __l_faceModules__ or _str_partType in ['eyelids']:
                #Make it and link it
            buffer =  RIGGING.group_me(self._mi_deformNull.mNode,False)
            i_grp = cgmMeta.asMeta(buffer,'cgmObject',setClass=True)
            i_grp.addAttr('cgmName',_str_partName,lock=True)
            i_grp.addAttr('cgmTypeModifier','constrain',lock=True)	 
            i_grp.doName()
            i_grp.parent = self._mi_deformNull.mNode
            self._mi_module.connectChildNode(i_grp,'constrainNull','module')
        self._mi_constrainNull = self._mi_module.constrainNull
        
        #>> Roll joint check...
        self._b_noRollMode = False
        self._b_addMidTwist = True
        if self._rigBlock.hasAttr('rollJoints'):
            if self._rigBlock.rollJoints == 0:
                self._b_noRollMode = True
                self._b_addMidTwist = False
                log.info("|{0}| >> No rollJoint mode...".format(_str_func))                    
            
    
        log.debug("|{0}| >> Time >> = {1} seconds".format(_str_func, "%0.3f"%(time.clock()-_start)))            
        
        return _res
    
    def fnc_processBuild(self,**kws):
        """
        Verify the module's rig visibility toggles and object set
        """
        _str_func = 'fnc_processBuild'  
        _start = time.clock()
    
        if self._b_outOfDate and self._call_kws['autoBuild']:
            self.doBuild(**kws)
        else:log.warning("|{0}| >> No autobuild condition met...".format(_str_func))                    
                 

        log.debug("|{0}| >> Time >> = {1} seconds".format(_str_func, "%0.3f"%(time.clock()-_start)))            
    
    def doBuild(self,buildTo = '',**kws):
        _str_func = 'doBuild'  
        _start = time.clock()        
        
        try:
            _l_buildOrder = self._d_block['buildModule'].__l_buildOrder__
            _len = len(_l_buildOrder)
            
            if not _len:
                log.error("|{0}| >> No steps to build!".format(_str_func))                    
                return False
            #Build our progress Bar
            mayaMainProgressBar = CGMUI.doStartMayaProgressBar(_len)
            
            for i,fnc in enumerate(_l_buildOrder):
                try:	
                    #str_name = d_build[k].get('name','noName')
                    #func_current = d_build[k].get('function')
                    #_str_subFunc = str_name
                    _str_subFunc = fnc.__name__
        
                    mc.progressBar(mayaMainProgressBar, edit=True,
                                   status = "|{0}| >>Rigging>> step: {1}...".format(_str_func,_str_subFunc), progress=i+1)    
                    fnc(self)
        
                    if buildTo is not None:
                        _Break = False
                        if VALID.stringArg(buildTo):
                            if buildTo.lower() == _str_subFunc:
                                _Break = True
                        elif buildTo == i:
                            _Break = True
                                
                        if _Break:
                            log.debug("|{0}| >> Stopped at step: [{1}]".format(_str_func, _str_subFunc))   
                            break
                except Exception,err:
                    raise Exception,"Fail step: {0} | err: [{1}]".format(fnc.__name__,err)  
        
            CGMUI.doEndMayaProgressBar(mayaMainProgressBar)#Close out this progress bar    
        except Exception,err:
            CGMUI.doEndMayaProgressBar(mayaMainProgressBar)#Close out this progress bar    		
            raise Exception,"|{0}| >> err: {1}".format(_str_func,err)        
    
    def build_rigJoints(self):
        _str_func = 'build_rigJoints'  
        _res = True
        _start = time.clock()
        
        _ml_skinJoints = self._d_joints['ml_skinJoints']
        
        #>>Check if exists -----------------------------------------------------------------------------------  
        l_rigJointsExist = self._mi_rigNull.msgList_get('rigJoints',asMeta = False, cull = True)
        if l_rigJointsExist:
            log.warning("|{0}| >> Deleting existing chain!".format(_str_func))                    
            mc.delete(l_rigJointsExist)
            
        #>>Build -----------------------------------------------------------------------------------          
        l_rigJoints = mc.duplicate([i_jnt.mNode for i_jnt in _ml_skinJoints],po=True,ic=True,rc=True)
        ml_rigJoints = [cgmMeta.cgmObject(j) for j in l_rigJoints]

        for i,mJnt in enumerate(ml_rigJoints):
            mJnt.addAttr('cgmTypeModifier','rig',attrType='string',lock=True)
            l_rigJoints[i] = mJnt.mNode
            mJnt.connectChildNode(_ml_skinJoints[i],'skinJoint','rigJoint')#Connect	    
            if mJnt.hasAttr('scaleJoint'):
                if mJnt.scaleJoint in self._ml_skinJoints:
                    int_index = self._ml_skinJoints.index(mJnt.scaleJoint)
                    mJnt.connectChildNode(l_rigJoints[int_index],'scaleJoint','sourceJoint')#Connect
            if mJnt.hasAttr('rigJoint'):mJnt.doRemove('rigJoint')
            mJnt.doName()
            
        ml_rigJoints[0].parent = False
	
        #>>Connect back -----------------------------------------------------------------------------------                  
        self._d_joints['ml_rigJoints'] = ml_rigJoints
        self._d_joints['l_rigJoints'] = [i_jnt.p_nameShort for i_jnt in ml_rigJoints]
        self._mi_rigNull.msgList_connect(ml_rigJoints,'rigJoints','rigNull')#connect	

       
        log.debug("|{0}| >> Time >> = {1} seconds".format(_str_func, "%0.3f"%(time.clock()-_start)))                
        return ml_rigJoints

   
    
#=====================================================================================================
import cgm.core.classes.GuiFactory as cgmUI
mUI = cgmUI.mUI

#>>> Root settings =============================================================
__version__ = 'ALPHA 0.06122017'


class ui(cgmUI.cgmGUI):
    USE_Template = 'cgmUITemplate'
    WINDOW_NAME = 'cgmBuilder_ui'    
    WINDOW_TITLE = 'Builder - {0}'.format(__version__)
    DEFAULT_MENU = None
    RETAIN = True
    MIN_BUTTON = True
    MAX_BUTTON = False
    FORCE_DEFAULT_SIZE = True  #always resets the size of the window when its re-created  
    DEFAULT_SIZE = 500,400
    __modes = 'space','orient','follow'
    
    def insert_init(self,*args,**kws):
            if kws:log.debug("kws: %s"%str(kws))
            if args:log.debug("args: %s"%str(args))
            log.info(self.__call__(q=True, title=True))
    
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
            
            self._blockRoot = None
            self._blockCurrent = None
            self._blockFactory = RIGBLOCKS.factory()
            
            self.create_guiOptionVar('blockAttrsFrameCollapse',defaultValue = 0) 
            self.create_guiOptionVar('blockInfoFrameCollapse',defaultValue = 0) 
            
            
    def build_menus(self):
        self.uiMenu_add = mUI.MelMenu( l='Add', pmc=self.buildMenu_add) 
        #self.uiMenu_switch = mUI.MelMenu( l='Switch', pmc=self.buildMenu_switch) 
        #self.uiMenu_pivot = mUI.MelMenu( l='Pivot', pmc=self.buildMenu_pivot)         
        self.uiMenu_help = mUI.MelMenu( l='Help', pmc=self.buildMenu_help)         
    
    def buildMenu_add( self, *args):
        self.uiMenu_add.clear()   
        
        _d = RIGBLOCKS.get_modules_dat()
            
        for b in _d[1]['blocks']:
            mUI.MelMenuItem(self.uiMenu_add, l=b,
                            c=cgmGEN.Callback(self.uiFunc_block_build,b)) 
                
        for c in _d[1].keys():
            if c == 'blocks':continue

            _sub = mUI.MelMenuItem( self.uiMenu_add, subMenu=True,
                                    l=c)
            for b in _d[1][c]:
                mUI.MelMenuItem(_sub, l=b)
                
    def uiUpdate_building(self):
        _str_func = 'uiUpdate_building'   
        
        self.uiFunc_updateScrollList_blocks()
        
        
            
    def uiFunc_block_build(self, blockType = None):
        _str_func = 'uiFunc_block_build'
        
        _block = self._blockFactory.create_rigBlock(blockType)
        
        log.info("|{0}| >> [{1}] | Created: {2}.".format(_str_func,blockType,self._blockFactory._mi_block))        
        
        self.uiUpdate_building()
        
        self.uiFunc_block_setActive(self._ml_blocks.index(self._blockFactory._mi_block))
        
    def uiFunc_scrollList_block_select(self): 
        _str_func = 'uiFunc_scrollList_block_select'  
        
        if self.uiPopUpMenu_blocks:
            self.uiPopUpMenu_blocks.clear()
            self.uiPopUpMenu_blocks.delete()
            self.uiPopUpMenu_blocks = None        

        _indices = self.uiScrollList_blocks.getSelectedIdxs() or []
        #log.debug("|{0}| >> indices: {1}".format(_str_func, _indices))    
    
        if not _indices:
            return
        
        _ml = RIGBLOCKS.get_from_scene()
        if not _ml:
            self.uiScrollList_blocks.clear()
            self.uiFunc_block_clearActive()
            return
        
        
        _index = _indices[0]
        self._ml_blocks = _ml        
        _mBlock = _ml[_index]
        
    
        self.uiPopUpMenu_blocks = mUI.MelPopupMenu(self.uiScrollList_blocks,button = 3)
        _popUp = self.uiPopUpMenu_blocks  
        
        mUI.MelMenuItem(_popUp,
                        label = "Select",
                        en=True,
                        c=cgmGEN.Callback(_mBlock.select))            
        
        return
    
    
        if len(_indices) == 1:
            _b_single = True
    
            log.debug("|{0}| >> Single pop up mode".format(_str_func))  
            _short = ml_parents[_indices[0]].p_nameShort
            mUI.MelMenuItem(_popUp,
                            label = "Single: {0}".format(_short),
                            en=False)            
        else:
            log.debug("|{0}| >> Multi pop up mode".format(_str_func))  
            mUI.MelMenuItem(_popUp,
                            label = "Mutli",
                            en=False)  
            _b_single = False
    
    
        if _b_single:
            mUI.MelMenuItem(_popUp,
                            label ='Alias',
                            ann = 'Enter value desired in prompt',
                            c = cgmGEN.Callback(self.uiFunc_parentManage_fromScrollList,**{'mode':'alias'}))
            mUI.MelMenuItem(_popUp,
                            label ='Clear Alias',
                            ann = 'Remove any alias',
                            c = cgmGEN.Callback(self.uiFunc_parentManage_fromScrollList,**{'mode':'aliasClear'}))
    
        mUI.MelMenuItem(_popUp,
                        label ='Select',
                        ann = 'Select specified indice parents',
                        c = cgmGEN.Callback(self.uiFunc_parentManage_fromScrollList,**{'mode':'select'}))  
        mUI.MelMenuItem(_popUp,
                        label ='Move Up',
                        ann = 'Move selected up in list',
                        c = cgmGEN.Callback(self.uiFunc_dynParents_reorder,0)) 
        mUI.MelMenuItem(_popUp,
                        label ='Move Down',
                        ann = 'Move selected down in list',
                        c = cgmGEN.Callback(self.uiFunc_dynParents_reorder,1)) 
    
        self._ml_objList = cgmMeta.validateObjListArg( CONTEXT.get_list(getTransform=True) )        
        uiMenu_changeSpace(self,_popUp)
    
        return
    
    def uiFunc_block_clearActive(self):
        self.uiField_inspector(edit=True, label = '')
        self._blockCurrent = None
        self.uiFrame_blockAttrs.clear()
        self.uiFrame_blockInfo.clear()
        
        
    def uiFunc_block_setActive(self, index = None):
        _str_func = 'uiFunc_block_setActive'
        
        _ml = RIGBLOCKS.get_from_scene()
        self._ml_blocks = _ml
        if not _ml:
            self.uiFunc_block_clearActive()
            return
                
        if index:
            if index not in range(len(_ml)):
                log.warning("|{0}| >> Invalid index: {1}".format(_str_func, index))    
                return
        else:
            _indices = self.uiScrollList_blocks.getSelectedIdxs() or []
            #log.debug("|{0}| >> indices: {1}".format(_str_func, _indices))    
        
            if not _indices:
                log.warning("|{0}| >> Nothing selected".format(_str_func))                    
                return
            
            index = _indices[0]
        
        log.info("|{0}| >> To set: {1}".format(_str_func, _ml[index].mNode))
        
        self._blockFactory.set_rigBlock( _ml[index] )
        self._blockCurrent = _ml[index]
        _short = self._blockCurrent.p_nameShort
        
        #>>>Inspector ======================================================================================
        #>>>Report -----------------------------------------------------------------------------------------
        
        _l_report = [self._blockCurrent.blockType, self._blockCurrent.blockState, self._blockCurrent.p_nameBase]
        
        if ATTR.get(_short,'direction'):
            _l_report.append( ATTR.get(_short,'blockState'))
        
        if self._blockCurrent.isReferenced():
            _l_report.insert(0,"Referenced!")
            
        self.uiField_inspector(edit=True, label = '{0}'.format(' | '.join(_l_report)))
        
        #>>>Info ----------------------------------------------------------------------------------------
        self.uiFrame_blockInfo.clear()
        
        for l in self._blockFactory.get_infoBlock_report():
            mUI.MelLabel(self.uiFrame_blockInfo,l=l)
            
        #>>>Attrs ----------------------------------------------------------------------------------------
        self.uiFrame_blockAttrs.clear()
        
        for a in self._blockCurrent.getAttrs(ud=True):
            mUI.MelLabel(self.uiFrame_blockAttrs,l="{0}:{1}".format(a,ATTR.get(_short,a)))
        
        
        
        
        
        
                
                
    def buildMenu_help( self, *args):
        self.uiMenu_help.clear()
    
        mc.menuItem(parent=self.uiMenu_help,
                    l = 'Get Help',
                    c='import webbrowser;webbrowser.open("https://docs.google.com/document/d/1ztN9wZfYunvGlao2iRL5WSc9oJTN021Bk6LNZqhbrL8/edit?usp=sharing");',                        
                    rp = 'N')    
        mUI.MelMenuItem( self.uiMenu_help, l="Log Self",
                         c=lambda *a: cgmUI.log_selfReport(self) )   
        mUI.MelMenuItem( self.uiMenu_help, l="Update Display",
                         c=lambda *a: self.uiUpdate_building() )      
        
 
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
        
    
    def uiFunc_updateScrollList_blocks(self):
        _str_func = 'uiFunc_updateScrollList_blocks'          
        self.uiScrollList_blocks.clear()
        
        _ml = RIGBLOCKS.get_from_scene()
        self._ml_blocks = _ml
        
        _len = len(_ml)
        
        if not _ml:
            log.warning("|{0}| >> No blocks found in scene.".format(_str_func)) 
            self.uiFunc_block_clearActive()
            return False      

        #...menu...
        _progressBar = cgmUI.doStartMayaProgressBar(_len,"Processing...")
        
        try:
            for i,mObj in enumerate(_ml):
                _short = mObj.p_nameShort
                log.info("|{0}| >> scroll list update: {1}".format(_str_func, _short))  
                
                mc.progressBar(_progressBar, edit=True, status = ("{0} Processing Block: {1}".format(_str_func,_short)), step=1)                    
                
                _l_report = [ATTR.get(_short,'blockType')]
                                
                _l_report.append(ATTR.get(_short,'blockState'))
                
                _l_report.append(mObj.p_nameBase)                
                
                if mObj.isReferenced():
                    _l_report.append("Referenced")
                    
                _str = " ~ ".join(_l_report)
                log.debug("|{0}| >> str: {1}".format(_str_func, _str))  
                
                self.uiScrollList_blocks.append(_str)

        except Exception,err:
            try:
                log.error("|{0}| >> err: {1}".format(_str_func, err))  
                cgmUI.doEndMayaProgressBar(_progressBar)
            except:
                raise Exception,err

        cgmUI.doEndMayaProgressBar(_progressBar)    
                    
    def build_layoutWrapper(self,parent):
        _str_func = 'build_layoutWrapper'
    
        _MainForm = mUI.MelFormLayout(self,ut='cgmUISubTemplate')
        
        ui_tabs = mUI.MelTabLayout( _MainForm,w=180 )
        
        uiTab_setup = mUI.MelFormLayout(ui_tabs,ut='cgmUITemplate')#mUI.MelColumnLayout(ui_tabs)
        self.uiTab_setup = uiTab_setup
        
        uiTab_utils = mUI.MelColumnLayout( ui_tabs )
        
        for i,tab in enumerate(['Setup','Utils']):
            ui_tabs.setLabel(i,tab)
            
        self.buildTab_setup(uiTab_setup)
        #self.buildTab_create(uiTab_create)
        #self.buildTab_update(uiTab_update)
    
        _row_cgm = cgmUI.add_cgmFooter(_MainForm)            
        _MainForm(edit = True,
                  af = [(ui_tabs,"top",0),
                        (ui_tabs,"left",0),
                        (ui_tabs,"right",0),                        
                        (_row_cgm,"left",0),
                        (_row_cgm,"right",0),                        
                        (_row_cgm,"bottom",0),
    
                        ],
                  ac = [(ui_tabs,"bottom",0,_row_cgm),
                        ],
                  attachNone = [(_row_cgm,"top")])
        
    def buildTab_setup(self,parent):
        _MainForm = parent
        #_MainForm = mUI.MelScrollLayout(parent)	        
        _row_report = mUI.MelHLayout(_MainForm ,ut='cgmUIInstructionsTemplate',h=20)
        self.uiField_report = mUI.MelLabel(_row_report,
                                           bgc = SHARED._d_gui_state_colors.get('help'),
                                           label = '...',
                                           h=20)
        _row_report.layout()         
        
        
        _LeftColumn = mUI.MelObjectScrollList(_MainForm, ut='cgmUISubTemplate',
                                              allowMultiSelection=False,en=True,
                                              dcc = cgmGEN.Callback(self.uiFunc_block_setActive),
                                              selectCommand = self.uiFunc_scrollList_block_select,
                                              
                                              w = 200)
        #dcc = self.uiFunc_dc_fromList,
        #selectCommand = self.uiFunc_selectParent_inList)
    
                                    #dcc = cgmGEN.Callback(self.uiFunc_attrManage_fromScrollList,**{'mode':'value'}),
        self.uiScrollList_blocks = _LeftColumn
        self._l_toEnable.append(self.uiScrollList_blocks)        
        
        
        _RightColumn = mUI.MelScrollLayout(_MainForm,useTemplate = 'cgmUITemplate')
        
        cgmUI.add_Header('Active',overrideUpper=True) 
        self.uiField_inspector= mUI.MelLabel(_RightColumn,
                                             bgc = SHARED._d_gui_state_colors.get('help'),
                                             label = '...',
                                             h=20) 
        
        
        # ------------------------------------------------------------------------------------
        _frame_info = mUI.MelFrameLayout(_RightColumn,label = 'Info',vis=True,
                                        collapse=self.var_blockInfoFrameCollapse.value,
                                        collapsable=True,
                                        enable=True,
                                        useTemplate = 'cgmUIHeaderTemplate',
                                        expandCommand = lambda:self.var_blockInfoFrameCollapse.setValue(0),
                                        collapseCommand = lambda:self.var_blockInfoFrameCollapse.setValue(1)
                                        )	
        self.uiFrame_blockInfo = _frame_info
        
        _frame_info_inside = mUI.MelColumnLayout(_frame_info,useTemplate = 'cgmUISubTemplate')  
        self.uiFrame_blockInfo = _frame_info_inside        
        
        #Attrs ------------------------------------------------------------------------------------
        _frame_attr = mUI.MelFrameLayout(_RightColumn,label = 'Attrs',vis=True,
                                        collapse=self.var_blockAttrsFrameCollapse.value,
                                        collapsable=True,
                                        enable=True,
                                        useTemplate = 'cgmUIHeaderTemplate',
                                        expandCommand = lambda:self.var_blockAttrsFrameCollapse.setValue(0),
                                        collapseCommand = lambda:self.var_blockAttrsFrameCollapse.setValue(1)
                                        )	
        self.uiFrame_blockAttrs = _frame_attr
        
        _frame_attr_inside = mUI.MelColumnLayout(_frame_attr,useTemplate = 'cgmUISubTemplate')  
        self.uiFrame_blockAttrs = _frame_attr_inside

        #>>> Layout form ---------------------------------------------------------------------------------------
        _MainForm(edit = True,
                  af = [(_row_report,"top",0),
                        (_row_report,"left",0),
                        (_row_report,"right",0),
                        
                        (_LeftColumn,"left",0),
                        (_RightColumn,"right",0),                        
                        (_RightColumn,"bottom",0),
                        (_LeftColumn,"bottom",0),

                        ],
                  ac = [(_LeftColumn,"top",0,_row_report),
                        (_RightColumn,"top",0,_row_report),
                        (_RightColumn,"left",0,_LeftColumn),
                        
                        #(_RightColumn,"bottom",0,_row_cgm),
                        #(_LeftColumn,"bottom",0,_row_cgm),

                        
                       ],
                  attachNone = [])#(_row_cgm,"top")	  
        
        self.uiUpdate_building()        
        
        
        
    def build_layoutWrapperOLD(self,parent):
        _str_func = 'build_layoutWrapper'
        self._d_uiCheckBoxes = {}
        
        _MainForm = mUI.MelFormLayout(parent,ut='cgmUISubTemplate')
        
        #_header_top = cgmUI.add_Header('cgmDynParentGroup',overrideUpper=True)     
        _row_report = mUI.MelHLayout(_MainForm ,ut='cgmUIInstructionsTemplate',h=20)
        self.uiField_report = mUI.MelLabel(_row_report,
                                           bgc = SHARED._d_gui_state_colors.get('help'),
                                           label = '...',
                                           h=20)
        _row_report.layout()         
        
        #_LeftColumn = mUI.MelColumn(_MainForm,ut='cgmUISubTemplate',w=100)
        #cgmUI.add_Header('Blocks',overrideUpper=True)  
        
        _LeftColumn = mUI.MelObjectScrollList(_MainForm, #ut='cgmUISubTemplate',
                                              allowMultiSelection=False,en=True,
                                              dcc = cgmGEN.Callback(self.uiFunc_block_setActive),
                                              selectCommand = self.uiFunc_scrollList_block_select,
                                              w = 200)
        #dcc = self.uiFunc_dc_fromList,
        #selectCommand = self.uiFunc_selectParent_inList)
    
                                    #dcc = cgmGEN.Callback(self.uiFunc_attrManage_fromScrollList,**{'mode':'value'}),
        self.uiScrollList_blocks = _LeftColumn
        self._l_toEnable.append(self.uiScrollList_blocks)        
        
        
        _RightColumn = mUI.MelColumnLayout(_MainForm,useTemplate = 'cgmUITemplate')
        
        cgmUI.add_Header('Inspector',overrideUpper=True) 
        self.uiField_inspector= mUI.MelLabel(_RightColumn,
                                             bgc = SHARED._d_gui_state_colors.get('help'),
                                             label = '...',
                                             h=20) 
        
        
        _frame_attr = mUI.MelFrameLayout(_RightColumn,label = 'Attr',vis=True,
                                        collapse=self.var_attrFrameCollapse.value,
                                        collapsable=True,
                                        enable=True,
                                        useTemplate = 'cgmUIHeaderTemplate',
                                        expandCommand = lambda:self.var_attrFrameCollapse.setValue(0),
                                        collapseCommand = lambda:self.var_attrFrameCollapse.setValue(1)
                                        )	
        _frame_attr_inside = mUI.MelColumnLayout(_frame_attr,useTemplate = 'cgmUISubTemplate')     
        CGMUI.add_Button(_frame_attr_inside)
        
        #>>>CGM Row
        _row_cgm = cgmUI.add_cgmFooter(_MainForm)
        
               
        #>>> Layout form ---------------------------------------------------------------------------------------
        _MainForm(edit = True,
                  af = [(_row_report,"top",0),
                        (_row_report,"left",0),
                        (_row_report,"right",0),
                        
                        (_LeftColumn,"left",0),
                        (_RightColumn,"right",0),                        
                       
                        (_row_cgm,"left",0),
                        (_row_cgm,"right",0),                        
                        (_row_cgm,"bottom",0),

                        ],
                  ac = [(_LeftColumn,"top",0,_row_report),
                        (_RightColumn,"top",0,_row_report),
                        (_RightColumn,"left",0,_LeftColumn),
                        
                        (_RightColumn,"bottom",0,_row_cgm),
                        (_LeftColumn,"bottom",0,_row_cgm),

                        
                       ],
                  attachNone = [(_row_cgm,"top")])	        
        
        self.uiUpdate_building()
        
        #_sel = mc.ls(sl=True)
        #if _sel:
            #self.uiFunc_load_selected()                

        return
 
    #@cgmGEN.Timer
    def uiFunc_selectParent_inList(self): 
        _str_func = 'uiFunc_selectParent_inList'        
        if self.uiPopUpMenu_parent:
            self.uiPopUpMenu_parent.clear()
            self.uiPopUpMenu_parent.delete()
            self.uiPopUpMenu_parent = None        
            
        ml_parents = self._mGroup.msgList_get('dynParents')
        _indices = self.uiScrollList_parents.getSelectedIdxs() or []
        log.debug("|{0}| >> indices: {1}".format(_str_func, _indices))    
        
        if not _indices:
            return
        
        self.uiPopUpMenu_parent = mUI.MelPopupMenu(self.uiScrollList_parents,button = 3)
        _popUp = self.uiPopUpMenu_parent           
                
        if len(_indices) == 1:
            _b_single = True
            
            log.debug("|{0}| >> Single pop up mode".format(_str_func))  
            _short = ml_parents[_indices[0]].p_nameShort
            mUI.MelMenuItem(_popUp,
                            label = "Single: {0}".format(_short),
                            en=False)            
        else:
            log.debug("|{0}| >> Multi pop up mode".format(_str_func))  
            mUI.MelMenuItem(_popUp,
                            label = "Mutli",
                            en=False)  
            _b_single = False
            
        
        if _b_single:
            mUI.MelMenuItem(_popUp,
                            label ='Alias',
                            ann = 'Enter value desired in prompt',
                            c = cgmGEN.Callback(self.uiFunc_parentManage_fromScrollList,**{'mode':'alias'}))
            mUI.MelMenuItem(_popUp,
                            label ='Clear Alias',
                            ann = 'Remove any alias',
                            c = cgmGEN.Callback(self.uiFunc_parentManage_fromScrollList,**{'mode':'aliasClear'}))

        mUI.MelMenuItem(_popUp,
                        label ='Select',
                        ann = 'Select specified indice parents',
                        c = cgmGEN.Callback(self.uiFunc_parentManage_fromScrollList,**{'mode':'select'}))  
        mUI.MelMenuItem(_popUp,
                        label ='Move Up',
                        ann = 'Move selected up in list',
                        c = cgmGEN.Callback(self.uiFunc_dynParents_reorder,0)) 
        mUI.MelMenuItem(_popUp,
                        label ='Move Down',
                        ann = 'Move selected down in list',
                        c = cgmGEN.Callback(self.uiFunc_dynParents_reorder,1)) 
        
        self._ml_objList = cgmMeta.validateObjListArg( CONTEXT.get_list(getTransform=True) )        
        uiMenu_changeSpace(self,_popUp)
        
        return

        
    def uiFunc_dc_fromList(self):
        _str_func = 'uiFunc_dc_fromList'   
    
        if not self._mGroup:
            log.error("|{0}| >> No dynGroup loaded to ui".format(_str_func))                                            
            return False          
    
        ml_parents = self._mGroup.msgList_get('dynParents')
        _indices = self.uiScrollList_parents.getSelectedIdxs() or []
    
        if _indices:
            ml_parents[_indices[0]].select()
                        
    



