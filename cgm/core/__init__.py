'''
------------------------------------------
cgm.core
Author: Josh Burton
email: cgmonks.info@gmail.com

Site : https://github.com/jjburton/cgmTools/wiki
------------------------------------------

Core is the library of Python modules that make the backbone of the cgm.core. 
It is built heavily and modeled on Mark Jackson (Red 9)'s great wwork.
    
===============================================================================
'''

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

from . import cgm_General as cgmGEN
#import os
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
                 #'cgm_PuppetMeta',
                 'mrs.RigBlocks',
                 'cgm_RigMeta',
                 'rig.dynamic_utils',
                 'tools.lightLoomLite',
                 'cgmPy.validateArgs',
                 #'rigger.ModuleFactory',
                 #'rigger.JointFactory',
                 #'rigger.TemplateFactory',
                 #'rigger.PuppetFactory',
                 #'rigger.RigFactory',
                 #'rigger.ModuleShapeCaster',
                 #'rigger.ModuleControlFactory',
                 'classes.DraggerContextFactory',
                 'lib.zoo.baseMelUI',
                 'lib.euclid',
                 'classes.SnapFactory',
                 'lib.rayCaster',
                 'lib.meta_Utils',
                 'lib.shapeCaster']

_l_ignoreTags = ['cgm.core.examples',
                 'cgm.core.lib.wing.wingdbstub',
                 'cgm.lib.gigs',
                 'cgm.lib.zoo',
                 'cgm.projects',
                 'cgm.core.lib.ml_tools',
                 'cgm.lib',
                 'cgm.core.lib.zoo',
                 'cgm.tools',
                 'cgm.core.lib.wing',
                 'cgm.core.mrs.help',
                 #'cgm.core.rigger',
                 'cgmMeta_test']

import cgm
import copy
import maya.cmds as mc
from cgm.core.cgmPy import os_Utils as cgmOS
#reload(cgmOS)
import importlib
import pprint

@cgmGEN.Timer
def _reload(stepConfirm=False):
    """
    import Red9.core
    from Red9.core import (Red9_General,
                           Red9_Meta,
                           Red9_Tools,
                           Red9_CoreUtils,
                           Red9_AnimationUtils,
                           Red9_PoseSaver) 

    """
    _str_func = '_reload'
    
    _d_modules, _l_ordered, _l_pycd = cgmOS.get_module_data(cgm.__path__[0],cleanPyc=True)
    _l_finished = []
    _l_cull = copy.copy(_l_ordered)
    
    import Red9
    import Red9.core
    Red9.setup.addPythonPackages()
    Red9.core._reload()
    cgmGEN._reloadMod(cgmOS)
    _d_failed = {}
    
    def loadLocal(str_module, module):
        _key = module.__dict__.get('__MAYALOCAL')
        if _key:
            try:
                mel.eval('python("import {0} as {1};")'.format(str_module,_key))
                log.info("|{0}| >> ... {1} loaded local as [{2}]".format(_str_func,m,_key))  
            except Exception as err:
                log.error(err)
                
    for m in _l_core_order:
        _k = 'cgm.core.' + m
        
        #log.debug("|{0}| >> Checking for: {1}".format(_str_func,m))
        if _k not in list(_d_modules.keys()):
            log.debug("|{0}| >> Not found in queried sub modules: {1}".format(_str_func,_k))
        else:
            try:
                module = __import__(_k, globals(), locals(), ['*'])
                cgmGEN._reloadMod(module) 
                log.info("|{0}| >> ... {1}".format(_str_func,_k))  
                _l_finished.append(_k)
                _l_cull.remove(_k)
                loadLocal(_k,module)
            except Exception as e:
                #print(m)
                _d_failed[_k] = e.args
                
                """
                for arg in e.args:
                    log.error(arg)"""
                #raise Exception,e
                cgmGEN.cgmExceptCB(Exception,e)
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
    _l_skip = []
    for m in _l_ordered:
        _k = 'cgm.core.' + m
        for t in _l_ignoreTags:
            if t in _k:
                log.debug("|{0}| >> Skipping {1} | contain ignore tag".format(_str_func,m))                
                _l_skip.append(m)        
    
    #for m in _l_pycd:
    for m in _l_ordered:
        if m in _l_skip:
            log.debug("|{0}| >> Skipping {1} | contains skip tag".format(_str_func,m))
            continue
        _k = 'cgm.core.' + m
        
            
        if m not in _l_finished:
            if m not in list(_d_modules.keys()):
                log.debug("|{0}| >> Not found in queried dict: {1}".format(_str_func,m))
            else:
                try:
                    module = __import__(m, globals(), locals(), ['*'],)
                    cgmGEN._reloadMod(module) 
                    log.debug("|{0}| >> ... {1}".format(_str_func,m))  
                    _l_finished.append(m)
                    _l_cull.remove(m)
                    loadLocal(m,module)
                    
                except Exception as e:
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
        log.info(cgmGEN._str_subLine)        
        #log.info("|{0}| >> {1} modules failed to import".format(_str_func,len(_d_failed.keys())))  
        cgmGEN.log_info_dict(_d_failed,"|{0}| >> {1} modules failed to import".format(_str_func,len(list(_d_failed.keys()))))
        
        for k in _d_failed.keys():
            print("import {}".format(k))
    print('CGM Core Reload complete')     

        


#========================================================================
# This HAS to be at the END of this module so that the RED9_META_REGISTRY
# picks up all inherited subclasses when Red9.core is imported
#========================================================================   
#Red9_Meta.registerMClassInheritanceMapping()#Pushes our classes in
#Red9_Meta.registerMClassNodeMapping(nodeTypes = ['network','transform','objectSet'])#What node types to look for

