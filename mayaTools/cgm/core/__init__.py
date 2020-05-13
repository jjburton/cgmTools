'''
------------------------------------------
cgm.core
Author: Josh Burton
email: jjburton@cgmonks.com

Site : http://www.cgmonks.com
------------------------------------------

Core is the library of Python modules that make the backbone of the cgm.core. 
It is built heavily and modeled on Mark Jackson (Red 9)'s great wwork.
    
===============================================================================
'''
import Red9.core
from Red9.core import (Red9_General,
                       Red9_Meta,
                       Red9_Tools,
                       Red9_CoreUtils,
                       Red9_AnimationUtils,
                       Red9_PoseSaver) 
"""import cgm_General
import cgm_Meta
import cgm_Deformers
import cgm_PuppetMeta
import cgm_RigMeta
import cgmPy.validateArgs
import rigger.ModuleFactory
import rigger.TemplateFactory
import rigger.JointFactory
import rigger.PuppetFactory
import rigger.RigFactory
import rigger.ModuleShapeCaster
import rigger.ModuleControlFactory
import classes.DraggerContextFactory
import classes.SnapFactory
import lib.rayCaster
import lib.meta_Utils
import lib.shapeCaster"""

import cgm_General as cgmGen
import os
import maya.mel as mel
#import reloadFactory as RELOAD
#import cgm.core.cgmPy.path_Utils as PATH

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

_l_core_order = ['cgm_General',
                 'cgm_Meta',
                 'cgm_Deformers',
                 'cgm_PuppetMeta',
                 'mrs.RigBlocks',
                 'cgm_RigMeta',
                 'rig.dynamic_utils',
                 'tools.lightLoomLite',
                 'cgmPy.validateArgs',
                 'rigger.ModuleFactory',
                 'rigger.JointFactory',
                 'rigger.TemplateFactory',
                 'rigger.PuppetFactory',
                 'rigger.RigFactory',
                 'rigger.ModuleShapeCaster',
                 'rigger.ModuleControlFactory',
                 'classes.DraggerContextFactory',
                 'lib.zoo.baseMelUI',
                 'lib.euclid',
                 'classes.SnapFactory',
                 'lib.rayCaster',
                 'lib.meta_Utils',
                 'lib.shapeCaster']

_l_ignoreTags = ['cgm.core.examples',
                 'cgm.lib.gigs',
                 #'cgm.lib.zoo',
                 'cgm.projects',
                 'cgm.core.rigger',
                 'cgmMeta_test']

import cgm
import copy
import maya.cmds as mc
from cgm.core.cgmPy import os_Utils as cgmOS
#reload(cgmOS)

@cgmGen.Timer
def _reload(stepConfirm=False):
    
    _str_func = '_reload'
    
    _d_modules, _l_ordered, _l_pycd = cgmOS.get_module_data(cgm.__path__[0],cleanPyc=True)
    _l_finished = []
    _l_cull = copy.copy(_l_ordered)
    
    Red9.core._reload()
    reload(cgmOS)
    
    def loadLocal(str_module, module):
        _key = module.__dict__.get('__MAYALOCAL')
        if _key:
            try:
                mel.eval('python("import {0} as {1};")'.format(str_module,_key))
                log.info("|{0}| >> ... {1} loaded local as [{2}]".format(_str_func,m,_key))  
            except Exception,err:
                log.error(err)
                
    for m in _l_core_order:
        _k = 'cgm.core.' + m
        
        #log.debug("|{0}| >> Checking for: {1}".format(_str_func,m))
        if _k not in _d_modules.keys():
            log.debug("|{0}| >> Not found in queried sub modules: {1}".format(_str_func,_k))
        else:
            try:
                module = __import__(_k, globals(), locals(), ['*'], -1)
                reload(module) 
                log.debug("|{0}| >> ... {1}".format(_str_func,m))  
                _l_finished.append(_k)
                _l_cull.remove(_k)
                loadLocal(_k,module)
            except Exception, e:
                for arg in e.args:
                    log.error(arg)
                cgmGen.cgmExceptCB(Exception,e)
            """log.debug("|{0}| >> Cull: {1} | Ordered: {2}".format(_str_func,
                                                                 len(_l_cull),
                                                                 len(_l_ordered)))"""            

                
    log.debug("|{0}| >> Ordered modules completed...".format(_str_func))
    """
    try:
        import morpheusRig_v2.core.morpheus_meta
        reload(morpheusRig_v2.core.morpheus_meta)
    except Exception,err:
        for arg in err.args:
            log.warning("Morpheus core load: {0}".format(arg))
        log.warning("|{0}| >> Morpheus Rig core not found.".format(_str_func))"""
                
    """
    Red9_Meta.registerMClassNodeMapping(nodeTypes = ['transform','objectSet','clamp','setRange','pointOnCurveInfo','decomposeMatrix','remapValue','ramp',
                                                     'ikSplineSolver','blendColors','blendTwoAttr','addDoubleLinear','condition','multiplyDivide','plusMinusAverage'])

    print('CGM Core Reloaded and META REGISTRY updated')"""
    #return
    _d_failed = {}
    _l_skip = []
    for m in _l_ordered:
        _k = 'cgm.core.' + m
        for t in _l_ignoreTags:
            if t in _k:
                #log.debug("|{0}| >> Skipping {1} | contain ignore tag".format(_str_func,m))                
                _l_skip.append(m)        
    
    for m in _l_pycd:
    #for m in _l_ordered:
        if m in _l_skip:
            log.debug("|{0}| >> Skipping {1} | contains skip tag".format(_str_func,m))
            continue
        _k = 'cgm.core.' + m
        
            
        if m not in _l_finished:
            if m not in _d_modules.keys():
                log.debug("|{0}| >> Not found in queried dict: {1}".format(_str_func,m))
            else:
                try:
                    module = __import__(m, globals(), locals(), ['*'], -1)
                    reload(module) 
                    log.debug("|{0}| >> ... {1}".format(_str_func,m))  
                    _l_finished.append(m)
                    _l_cull.remove(m)
                    loadLocal(m,module)
                    
                except Exception, e:
                    #log.error("|{0}| >> Failed: {1}".format(_str_func,m))  
                    #for arg in e.args:
                        #log.error(arg)
                    _d_failed[m] = e.args
                if stepConfirm:
                    result = mc.confirmDialog(title="Shall we continue",
                                              message= m,
                                              button=['OK', 'Cancel'],
                                              defaultButton='OK',
                                              cancelButton='Cancel',
                                              dismissString='Cancel')
                
                    if result != 'OK':
                        log.error("Cancelled at: {0}".format(m))
                        return False                    
                    
    if _d_failed:   
        log.info(cgmGen._str_subLine)        
        #log.info("|{0}| >> {1} modules failed to import".format(_str_func,len(_d_failed.keys())))  
        cgmGen.log_info_dict(_d_failed,"|{0}| >> {1} modules failed to import".format(_str_func,len(_d_failed.keys())))
        #for k in _d_failed.keys():
            #log.info("|{0}| >> {1}".format(_str_func,m))
    print('CGM Core Reload complete')     

        

        
            



def _reloadBAK():
    '''
    reload carefully and re-register the RED9_META_REGISTRY
    '''
    Red9.core._reload()
    reload(cgm_General)    
    reload(cgm_Meta)
    reload(cgm_Deformers)
    reload(cgm_PuppetMeta)
    reload(cgm_RigMeta)
    reload(cgmPy.validateArgs)
    reload(rigger.ModuleFactory)
    reload(rigger.JointFactory)
    reload(rigger.TemplateFactory)
    reload(rigger.PuppetFactory)
    reload(rigger.RigFactory)
    reload(rigger.ModuleShapeCaster)
    reload(rigger.ModuleControlFactory)
    
    reload(classes.DraggerContextFactory)
    reload(classes.SnapFactory)
    reload(lib.rayCaster)
    reload(lib.meta_Utils)
    reload(lib.shapeCaster)
    try:reload(morpheusRig_v2.core.morpheus_meta)
    except:print("Morpheus Rig core not found.")
    
    
    Red9_Meta.registerMClassNodeMapping(nodeTypes = ['transform','objectSet','clamp','setRange','pointOnCurveInfo','decomposeMatrix','remapValue','ramp',
                                                     'ikSplineSolver','blendColors','blendTwoAttr','addDoubleLinear','condition','multiplyDivide','plusMinusAverage'])

    print('CGM Core Reloaded and META REGISTRY updated') 
    #print '=' * 100
    #Red9_Meta.printSubClassRegistry()  
    #print '=' * 100    
    
def _setlogginglevel_debug():
    '''
    Dev wrapper to set the logging level to debug
    '''
    Red9.core._setlogginglevel_debug()
    cgm_Meta.log.setLevel(cgm_Meta.logging.DEBUG)
    cgm_PuppetMeta.log.setLevel(cgm_PuppetMeta.logging.DEBUG)
    rigger.ModuleFactory.log.setLevel(rigger.ModuleFactory.logging.DEBUG)
    rigger.JointFactory.log.setLevel(rigger.JointFactory.logging.DEBUG)
    
    print('cgm Core set to DEBUG state')
    
def _setlogginglevel_info():
    '''
    Dev wrapper to set the logging to Info, usual state
    '''
    Red9.core._setlogginglevel_info()
    cgm_Meta.log.setLevel(cgm_Meta.logging.INFO)
    cgm_PuppetMeta.log.setLevel(cgm_PuppetMeta.logging.INFO)
    rigger.ModuleFactory.log.setLevel(rigger.ModuleFactory.logging.INFO)
    rigger.JointFactory.log.setLevel(rigger.JointFactory.logging.INFO)
    
    print('cgm Core set to Info state')



#========================================================================
# This HAS to be at the END of this module so that the RED9_META_REGISTRY
# picks up all inherited subclasses when Red9.core is imported
#========================================================================   
#Red9_Meta.registerMClassInheritanceMapping()#Pushes our classes in
#Red9_Meta.registerMClassNodeMapping(nodeTypes = ['network','transform','objectSet'])#What node types to look for

