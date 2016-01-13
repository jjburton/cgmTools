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
import cgm_General
import cgm_Meta
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
import lib.shapeCaster

import os
from cgm.core.lib.zoo.path import Path

def _reload():
    '''
    reload carefully and re-register the RED9_META_REGISTRY
    '''
    Red9.core._reload()
    reload(cgm_General)    
    reload(cgm_Meta)
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
    
    
    Red9_Meta.registerMClassNodeMapping(nodeTypes = ['transform','objectSet','clamp','setRange','pointOnCurveInfo','decomposeMatrix','remapValue',
                                                     'ikSplineSolver','blendColors','blendTwoAttr','addDoubleLinear','condition','multiplyDivide','plusMinusAverage'])

    print('CGM Core Reloaded and META REGISTRY updated') 
    print '=============================================================================='  
    Red9_Meta.printSubClassRegistry()  
    print '=============================================================================='    
    
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

def returnPyFilesFromFolder():
        import os
        thisFile = Path( __file__ )
        thisPath = thisFile.up()


        bufferList = find_files(thisPath, '*.py')
        returnList = []
        
        for file in bufferList:
                if '__' not in file:
                        splitBuffer = file.split('.')
                        returnList.append(splitBuffer[0])               
        if returnList:
                return returnList
        else:
                return False
        
def find_files(base, pattern):
        import fnmatch
        import os
        
        '''Return list of files matching pattern in base folder.'''
        """ http://stackoverflow.com/questions/4296138/use-wildcard-with-os-path-isfile"""
        return [n for n in fnmatch.filter(os.listdir(base), pattern) if
                os.path.isfile(os.path.join(base, n))]
        
        
__all__ = returnPyFilesFromFolder()
