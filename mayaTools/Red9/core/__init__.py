'''
------------------------------------------
Red9 Studio Pack: Maya Pipeline Solutions
Author: Mark Jackson
email: rednineinfo@gmail.com

Red9 blog : http://red9-consultancy.blogspot.co.uk/
MarkJ blog: http://markj3d.blogspot.co.uk
------------------------------------------

Core is the library of Python modules that make the backbone of the Red9 Pack
    
:Note that the registerMClassInheritanceMapping() call is after all the imports
so that the global RED9_META_REGISTERY is built up correctly
===============================================================================
'''

import Red9_General 
import Red9_Meta
import Red9_Tools
import Red9_CoreUtils
import Red9_AnimationUtils
import Red9_PoseSaver


def _reload():
    '''
    reload carefully and re-register the RED9_META_REGISTRY
    '''
    reload(Red9_General)
    reload(Red9_Meta)
    reload(Red9_Tools)
    reload(Red9_CoreUtils)
    reload(Red9_AnimationUtils)
    reload(Red9_PoseSaver)
        
    Red9_Meta.registerMClassInheritanceMapping()
    print('Red9 Core Reloaded and META REGISTRY updated') 
    
def _setlogginglevel_debug():
    '''
    Dev wrapper to set the logging level to debug
    '''
    Red9_CoreUtils.log.setLevel(Red9_CoreUtils.logging.DEBUG)
    Red9_AnimationUtils.log.setLevel(Red9_AnimationUtils.logging.DEBUG)
    Red9_General.log.setLevel(Red9_General.logging.DEBUG)
    Red9_Tools.log.setLevel(Red9_Tools.logging.DEBUG)
    Red9_PoseSaver.log.setLevel(Red9_PoseSaver.logging.DEBUG)
    Red9_Meta.log.setLevel(Red9_Meta.logging.DEBUG)
    print('Red9 Core set to DEBUG state')
        
def _setlogginglevel_info():
    '''
    Dev wrapper to set the logging to Info, usual state
    '''
    Red9_CoreUtils.log.setLevel(Red9_CoreUtils.logging.INFO)
    Red9_AnimationUtils.log.setLevel(Red9_AnimationUtils.logging.INFO)
    Red9_General.log.setLevel(Red9_General.logging.INFO)
    Red9_Tools.log.setLevel(Red9_Tools.logging.INFO)
    Red9_PoseSaver.log.setLevel(Red9_PoseSaver.logging.INFO)
    Red9_Meta.log.setLevel(Red9_Meta.logging.INFO)
    print('Red9 Core set to INFO state')


#========================================================================
# This HAS to be at the END of this module so that the RED9_META_REGISTRY
# picks up all inherited subclasses when Red9.core is imported
#========================================================================   
Red9_Meta.registerMClassInheritanceMapping()
Red9_Meta.registerMClassNodeMapping()



