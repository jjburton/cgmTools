'''
    ===============================================================================
    Red9 StudioPack:
    email : rednineinfo@gmail.com

    This is the main entry point for initilizing the Red9 StudioPack. 
    Unlike previous releases I've removed the ability to install this via the
    Maya Module systems. Instead I've made it more of a standard Python site-package
    which has many benefits in the way the systems are managed.
    Simply running the following will initialize and install the setups
    
    You need to modify the path to point to the folder containing this file and
    add it to the system path UNLESS the Red9 folder is already on a Maya script path.
    
    import sys
    sys.path.append('P:\Red9_Pipeline\Red9_Release1.28')
    
    import Red9
    Red9.start()
    
    ===============================================================================
'''


#Initialize the RED9_META_REGISTRY which is used by the MetaClass baseclass to 
#know what subclasses there are, and what to consider in it's __new__ statement 
#for initialization. If you're using the MetaClass as a base for your own modules
#you'll probably need to run the Red9.core.Red9_Meta.registerMClassInheritanceMapping()
#to update this dictionary
global RED9_META_REGISTERY
RED9_META_REGISTERY=[]

import startup.setup as setup

def start(Menu=True):
    import maya.cmds as cmds
    #Run the main setups. If you DON'T want the Red9Menu set 'Menu=False'
    cmds.evalDeferred("Red9.setup.start(Menu=%s)" % Menu)
    #Import the core, not this is on LowPriority to make sure it 
    #happens after the main setups have finished above
    cmds.evalDeferred("import Red9.core",lp=True)



