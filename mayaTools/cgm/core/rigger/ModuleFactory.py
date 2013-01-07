import copy

import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

# From Red9 =============================================================
from Red9.core import Red9_Meta as r9Meta
from Red9.core import Red9_General as r9General

# From cgm ==============================================================
from cgm.lib import modules
from cgm.lib.classes import NameFactory

##>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Modules
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
@r9General.Timer   
def doSetParentModule(self,moduleParent,force = False):
    """
    Set a module parent of a module

    module(string)
    """
    #See if parent exists and is a module, if so...
    #>>>buffer children
    #>>>see if already connected
    #>>Check existance
        #==============	
    #Get our instance
    try:
        moduleParent.mNode#See if we have an instance

    except:
        if mc.objExists(moduleParent):
            moduleParent = r9Meta.MetaClass(moduleParent)#initialize
        else:
            log.warning("'%s' doesn't exist"%moduleParent)#if it doesn't initialize, nothing is there		
            return False	

    #Logic checks
    #==============
    if not moduleParent.hasAttr('mClass'):
        log.warning("'%s' lacks an mClass attr"%module.mNode)	    
        return False

    if moduleParent.mClass not in ['cgmModule']:
        log.warning("'%s' is not a recognized module type"%moduleParent.mClass)
        return False

    if not moduleParent.hasAttr('moduleChildren'):#Quick check
        log.warning("'%s'doesn't have 'moduleChildren' attr"%moduleParent.getShortName())#if it doesn't initialize, nothing is there		
        return False	

    buffer = copy.copy(moduleParent.moduleChildren) or []#Buffer till we have have append functionality	

    if self.mNode in buffer:
        log.warning("'%s' already connnected to '%s'"%(module,moduleParent.getShortName()))
        return False

        #Connect
        #==============	
    else:
        log.info("Current children: %s"%buffer)
        log.info("Adding '%s'!"%self.getShortName())    

        buffer.append(self.mNode) #Revist when children has proper add/remove handling
        del moduleParent.moduleChildren #Revist when children has proper add/remove handling
        moduleParent.connectChildren(buffer,'moduleChildren','moduleParent',force=force)#Connect
        if moduleParent.modulePuppet.mNode:
            self.__setMessageAttr__('modulePuppet',moduleParent.modulePuppet.mNode)#Connect puppet to 

    self.parent = moduleParent.parent
    return True


@r9General.Timer   
def getGeneratedCoreNames(self):
    """ 
    Generate core names for a module and return them

    self MUST be cgmModule

    RETURNS:
    generatedNames(list)
    """
    log.info("Generating core names via ModuleFactory - '%s'"%self.getShortName())

    ### check the settings first ###
    partType = self.moduleType
    log.debug("%s partType is %s"%(self.getShortName(),partType))
    settingsCoreNames = modules.returncgmTemplateCoreNames(partType)
    handles = self.rigNull.handles
    partName = NameFactory.returnRawGeneratedName(self.mNode,ignore=['cgmType','cgmTypeModifier'])

    ### if there are no names settings, genearate them from name of the limb module###
    generatedNames = []
    if settingsCoreNames == False:   
        cnt = 1
        for handle in range(handles):
            generatedNames.append('%s%s%i' % (partName,'_',cnt))
            cnt+=1

    elif int(self.rigNull.handles) > (len(settingsCoreNames)):
        log.info(" We need to make sure that there are enough core names for handles")       
        cntNeeded = self.rigNull.handles  - len(settingsCoreNames) +1
        nonSplitEnd = settingsCoreNames[len(settingsCoreNames)-2:]
        toIterate = settingsCoreNames[1]
        iterated = []
        for i in range(cntNeeded):
            iterated.append('%s%s%i' % (toIterate,'_',(i+1)))
        generatedNames.append(settingsCoreNames[0])
        for name in iterated:
            generatedNames.append(name)
        for name in nonSplitEnd:
            generatedNames.append(name) 

    else:
        return settingsCoreNames[:self.rigNull.handles]

    return generatedNames







