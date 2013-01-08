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
from cgm.core.classes import DraggerContextFactory as dragFactory
reload(dragFactory)

##>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Modules
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
@r9General.Timer   
def isSized(self):
    """
    Return if a moudle is sized or not
    """
    handles = self.rigNull.handles
    if self.templateNull.templateStarterData:
        if len(self.templateNull.templateStarterData) == handles:
            for i in range(handles):
                if not self.templateNull.templateStarterData[i][1]:
                    log.warning("%s has no data"%(self.templateNull.templateStarterData[i]))                    
                    return False
            return True
        else:
            log.warning("%i is not == %i handles necessary"%(len(self.templateNull.templateStarterData),handles))
            return False
    else:
        log.warning("No template starter data found for '%s'"%self.getShortName())        
    return False
    
    
    
def doSize(self,mode='all',geo = []):
    """
    Size a module
    1) Determine what points we need to gather
    2) Initiate draggerContextFactory
    3) Prompt user per point
    4) at the end of the day have a pos list the length of the handle list
    
    TODO:
    Add option for other modes
    Add geo argument that can be passed for speed
    """
    handles = self.rigNull.handles
    names = getGeneratedCoreNames(self)
    geo = self.modulePuppet.getGeo()
    posBuffer = []
    log.info("Handles: %s"%handles)
    log.info("Names: %s"%names)
    log.info("Puppet: %s"%self.getMessage('modulePuppet'))
    log.info("Geo: %s"%geo)
    i_module = self #Bridge holder for our module class to go into our sizer class
    
    class moduleSizer(dragFactory.clickMesh):
        """Sublass to get the functs we need in there"""
        def __init__(self,i_module = i_module,**kws):
            super(moduleSizer, self).__init__(**kws)
            self.i_module = i_module
            
        def finalize(self):
            log.info(self.returnList)
            log.info(self.createdList)   
            log.info(self.i_module.mNode)
            self.i_module.templateNull.templateStarterData = self.returnList#need to ensure it's storing properly
            
            dragFactory.clickMesh.finalize(self)
        
    #Start up our sizer    
    moduleSizer(mode = 'midPoint',
                mesh = geo,
                create = 'locator',
                toCreate = names)
    



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
    
    TODO:
    Where to store names?
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

    #figure out what to do with the names
    if not self.templateNull.templateStarterData:
        buffer = []
        for n in generatedNames:
            buffer.append([str(n),[]])
        self.templateNull.templateStarterData = buffer
    else:
        for i,pair in enumerate(self.templateNull.templateStarterData):
            pair[0] = generatedNames[i]      
        
    return generatedNames








