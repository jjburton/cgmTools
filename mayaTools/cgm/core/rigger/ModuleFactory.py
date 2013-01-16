import copy
import re

import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

# From Maya =============================================================
import maya.cmds as mc

# From Red9 =============================================================
from Red9.core import Red9_Meta as r9Meta
from Red9.core import Red9_General as r9General

# From cgm ==============================================================
from cgm.lib import (modules,curves,distance,attributes)
reload(attributes)
from cgm.lib.classes import NameFactory
from cgm.core.classes import DraggerContextFactory as dragFactory
reload(dragFactory)

##>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Modules
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
@r9General.Timer   
def isTemplated(self):
    """
    Return if a module is templated or not
    """
    log.info(">>> isTemplated")
    coreNamesValue = self.coreNames.value
    if not coreNamesValue:
        log.warning("No core names found")
        return False
    if not self.templateNull.getChildren():
        log.warning("No children found in template null")
        return False   
    
    for attr in 'controlObjects','root','curve','orientHelpers','orientRootHelper':
        if not self.templateNull.getMessage(attr):
            log.warning("No data found on '%s'"%attr)
            return False    
        
    if len(coreNamesValue) != len(self.templateNull.getMessage('controlObjects')):
        log.warning("Not enough handles.")
        return False    
        
    for i_obj in self.templateNull.controlObjects:#check for helpers
        if not i_obj.getMessage('helper'):
            log.warning("'%s' missing it's helper"%i_obj.getShortName())
            return False
    
    #self.moduleStates['templateState'] = True #Not working yet
    return True
    
@r9General.Timer   
def isSized(self):
    """
    Return if a moudle is sized or not
    """
    log.info(">>> isSized")    
    handles = self.rigNull.handles
    if len(self.coreNames.value) != handles:
        log.warning("Not enough names for handles")
        return False
    
    if self.templateNull.templateStarterData:
        if len(self.templateNull.templateStarterData) == handles:
            for i,pos in enumerate(self.templateNull.templateStarterData):
                if not pos:
                    log.warning("[%s] has no data"%(i))                    
                    return False
            return True
        else:
            log.warning("%i is not == %i handles necessary"%(len(self.templateNull.templateStarterData),handles))
            return False
    else:
        log.warning("No template starter data found for '%s'"%self.getShortName())  
    return False
    
    
def doSize(self,sizeMode='normal',geo = []):
    """
    Size a module
    1) Determine what points we need to gather
    2) Initiate draggerContextFactory
    3) Prompt user per point
    4) at the end of the day have a pos list the length of the handle list
    
    @ sizeMode
    'all' - pick every handle position
    'normal' - first/last, if child, will use last position of parent as first
    
    TODO:
    Add option for other modes
    Add geo argument that can be passed for speed
    Add clamp on value
    """
    log.info(">>> doSize")    
    
    clickMode = {"heel":"surface"}    
    
    #Gather info
    #==============      
    handles = self.rigNull.handles
    names = self.coreNames.value or getGeneratedCoreNames(self)
    
    if not geo:
        geo = self.modulePuppet.getGeo()
    log.debug("Handles: %s"%handles)
    log.debug("Names: %s"%names)
    log.debug("Puppet: %s"%self.getMessage('modulePuppet'))
    log.debug("Geo: %s"%geo)
    i_module = self #Bridge holder for our module class to go into our sizer class
    
    #Variables
    #==============      
    if sizeMode == 'normal':
        if names > 1:
            namesToCreate = names[0],names[-1]
        else:
            namesToCreate = names
        log.info("Names: %s"%names)
    else:
        namesToCreate = names        
        sizeMode = 'all'
       
    class moduleSizer(dragFactory.clickMesh):
        """Sublass to get the functs we need in there"""
        def __init__(self,i_module = i_module,**kws):
            log.info(">>> moduleSizer.__init__")    
            if kws:log.info("kws: %s"%str(kws))
            
            super(moduleSizer, self).__init__(**kws)
            self.i_module = i_module
            log.info("Please place '%s'"%self.toCreate[0])
            
        def release(self):
            if len(self.returnList)< len(self.toCreate)-1:#If we have a prompt left
                log.info("Please place '%s'"%self.toCreate[len(self.returnList)+1])            
            dragFactory.clickMesh.release(self)

            
        def finalize(self):
            log.debug("returnList: %s"% self.returnList)
            log.debug("createdList: %s"% self.createdList)   
            buffer = [] #self.i_module.templateNull.templateStarterData
            log.debug("starting data: %s"% buffer)
            
            #Make sure we have enough points
            #==============  
            handles = self.i_module.rigNull.handles
            if len(self.returnList) < handles:
                log.warning("Creating curve to get enough points")                
                curve = curves.curveFromPosList(self.returnList)
                mc.rebuildCurve (curve, ch=0, rpo=1, rt=0, end=1, kr=0, kcp=0, kep=1, kt=0,s=(handles-1), d=1, tol=0.001)
                self.returnList = curves.returnCVsPosList('curve1')#Get the pos of the cv's
                mc.delete(curve)

            #Store info
            #==============                  
            for i,p in enumerate(self.returnList):
                buffer.append(p)#need to ensure it's storing properly
                #log.info('[%s,%s]'%(buffer[i],p))
                
            #Store locs
            #==============  
            log.debug("finish data: %s"% buffer)
            self.i_module.templateNull.__setattr__('templateStarterData',buffer,lock=True)
            #self.i_module.templateNull.templateStarterData = buffer#store it
            log.info("'%s' sized!"%self.i_module.getShortName())
            dragFactory.clickMesh.finalize(self)
        
    #Start up our sizer    
    return moduleSizer(mode = 'midPoint',
                       mesh = geo,
                       create = 'locator',
                       toCreate = namesToCreate)
    
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
    log.info(">>> doSetParentModule")
    
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
        #if moduleParent.modulePuppet.mNode:
            #self.__setMessageAttr__('modulePuppet',moduleParent.modulePuppet.mNode)#Connect puppet to 

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
    log.info(">>> getGeneratedCoreNames")    
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
        generatedNames = settingsCoreNames[:self.rigNull.handles]

    #figure out what to do with the names
    self.coreNames.value = generatedNames
    """
    if not self.templateNull.templateStarterData:
        buffer = []
        for n in generatedNames:
            buffer.append([str(n),[]])
        self.templateNull.templateStarterData = buffer
    else:
        for i,pair in enumerate(self.templateNull.templateStarterData):
            pair[0] = generatedNames[i]    
    """
        
    return generatedNames

