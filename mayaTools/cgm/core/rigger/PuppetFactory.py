import maya.cmds as mc
import copy as copy

import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

# From Red9 =============================================================
from Red9.core import Red9_Meta as r9Meta
from Red9.core import Red9_General as r9General

# From cgm ==============================================================
from cgm.lib import (search,attributes)

#Shared Settings
#========================= 
geoTypes = 'nurbsSurface','mesh','poly','subdiv'

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Puppet Utilities
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
@r9General.Timer   
def simplePuppetReturn():
    catch = mc.ls(type='network')
    returnList = []
    if catch:
        for o in catch:
            if attributes.doGetAttr(o,'mClass') in ['cgmPuppet','cgmMorpheusPuppet']:
                returnList.append(o)
    return returnList


@r9General.Timer   
def getGeo(self):
    """
    Returns geo in a puppets geo folder, ALL geo to be used by a puppet should be in there
    """    
    geo = []
    for o in self.masterNull.geoGroup.getAllChildren():
        if search.returnObjectType(o) in geoTypes:
            buff = mc.ls(o,long=True)
            geo.append(buff[0])
    return geo

@r9General.Timer   
def getModules(self):
    """
    Get the modules of a puppet in a usable format:
    
    i_modules(dict){indexed to name}
    
    """
    #Get connected Modules
    self.i_modules = self.getChildMetaNodes(mAttrs = ['moduleChildren'])
    return self.i_modules

@r9General.Timer   
def getModuleFromDict(self,checkDict):
    """
    Pass a check dict of attrsibutes and arguments. If that module is found, it returns it.
    
    checkDict = {'moduleType':'torso',etc}
    """
    assert type(checkDict) is dict,"Arg must be dictionary"
    for i_m in self.moduleChildren:
        matchBuffer = 0
        for key in checkDict.keys():
            if i_m.hasAttr(key) and attributes.doGetAttr(i_m.mNode,key) == checkDict.get(key):
                matchBuffer +=1
        if matchBuffer == len(checkDict.keys()):
            log.debug("Found Morpheus Module: '%s'"%i_m.getShortName())
            return i_m
    return False

@r9General.Timer  
def getState(self):
    i_modules = self.moduleChildren
    if not i_modules:
        log.warning("'%s' has no modules"%self.cgmName)
        return False
    
    l_states = []
    for i_m in i_modules:
        l_states.append(i_m.getState())
        
    log.info("'%s' states: %s"%(self.getShortName(),l_states))
    return min(l_states)
    
@r9General.Timer  
def getOrderedModules(self):
    """ 
    Returns ordered modules of a character
    
    Stores:
    self.orderedModules(list)       
    
    Returns:
    self.orderedModules(list)
    
    from cgm.core.rigger import PuppetFactory as pFactory
    reload(pFactory)
    from cgm.core import cgm_PuppetMeta as cgmPM
    p = cgmPM.cgmPuppet(name='Morpheus')
    
    """            
    l_orderedParentModules = []
    moduleRoots = []
       
    #Find the roots 
    for i_m in self.moduleChildren:
        log.debug("%s.moduleParent: %s"%(i_m.getShortName(),i_m.getMessage('moduleParent')))
        log.debug("%s.modulePuppet: %s"%(i_m.getShortName(),i_m.getMessage('modulePuppet')))        
        if i_m.getMessage('modulePuppet') == [self.mNode] and not i_m.getMessage('moduleParent'):
            log.info("Root found: %s"%(i_m.getShortName()))
            moduleRoots.append(i_m) 
            
    l_childrenList = copy.copy(self.moduleChildren)
    
    if not moduleRoots:
        log.critical("No module root found!")
        return False
    
    for i_m in moduleRoots:
        l_childrenList.remove(i_m)
        l_orderedParentModules.append(i_m)
                
    cnt = 0
    #Process the childdren looking for parents as children and so on and so forth, appending them as it finds them
    while len(l_childrenList)>0 and cnt < 100:#While we still have a cull list
        cnt+=1                        
        if cnt == 99:
            log.error('max count')
        for i_Parent in l_orderedParentModules:
            for i_child in l_childrenList:#for each ordered parent module we've found (starting with root)
                log.debug("i_child: %s"%i_Parent.getShortName())
                if i_child.moduleParent == i_Parent:
                    log.debug('Match found!')
                    l_orderedParentModules.append(i_child)
                    l_childrenList.remove(i_child)   
                    
    return l_orderedParentModules

@r9General.Timer  
def getOrderedParentModules(self):
    """ 
    Returns ordered list of parent modules of a character
    
    Stores:
    self.moduleChildren(dict)
    self.orderedParentModules(list)       
    self.rootModules(list)
    
    Returns:
    self.orderedParentModules(list)
    
    THIS IS STILL NOT DOING ANYTHING NECESSARY
    """    
    d_moduleParents = {}
    l_orderedParentModules = []
    moduleRoots = []
    d_moduleChildren = {}
       
    #Find the roots 
    for i_m in self.moduleChildren:
        log.debug("%s.moduleParent: %s"%(i_m.getShortName(),i_m.getMessage('moduleParent')))
        log.debug("%s.modulePuppet: %s"%(i_m.getShortName(),i_m.getMessage('modulePuppet')))        
        if i_m.getMessage('modulePuppet') and not i_m.getMessage('moduleParent'):
            log.info("Root found: %s"%(i_m.getShortName()))
            moduleRoots.append(i_m)
            l_orderedParentModules.append(i_m)
            
        if i_m.getMessage('moduleChildren'):
            log.info("Parent found: %s"%(i_m.getShortName()))
            d_moduleChildren[i_m] = i_m.moduleChildren
        if i_m.getMessage('moduleParent'):
            d_moduleParents[i_m] = i_m.moduleParent
            
    l_childrenList = copy.copy(self.moduleChildren)
    
    if not moduleRoots:
        log.critical("No module root found!")
        return False
    for i_m in moduleRoots:
        l_childrenList.remove(i_m)
        
    #log.info("d_moduleParents: %s"%d_moduleParents)
    #log.info("d_moduleChildren: %s"%d_moduleChildren)
    #log.info("l_orderedParentModules: %s"%l_orderedParentModules)
    log.info("l_childrenList: %s"%l_childrenList)
        
    cnt = 0
    #Process the childdren looking for parents as children and so on and so forth, appending them as it finds them
    while len(l_childrenList)>0 and cnt < 100:#While we still have a cull list
        if cnt == 99:
            log.error('max count')
        for i_Parent in l_orderedParentModules:
            for i_child in l_childrenList:#for each ordered parent module we've found (starting with root)
                log.debug("i_child: %s"%i_Parent.getShortName())
                cnt+=1
                if i_child.moduleParent == [i_Parent]:
                    log.info('Match found!')
                    l_orderedParentModules.append(i_child)
                    l_childrenList.remove(i_child)            
    
    """
    #Process the childdren looking for parents as children and so on and so forth, appending them as it finds them
    while len(d_moduleChildrenCull)>0 and cnt < 100:#While we still have a cull list
        if cnt == 99:
            log.error('max count')
        for i_Parent in l_orderedParentModules:#for each ordered parent module we've found (starting with root)
            log.debug("i_Parent: %s"%i_Parent.getShortName())
            for i_checkParent in d_moduleChildrenCull.keys():#for each module with children
                log.debug("i_checkParent: %s"%i_Parent.getShortName())                
                cnt +=1
                #if the check parent has a parent and the parent of the check parent is the ordered parent, store it and pop
                log.info("i_Parent: %s"%i_Parent.getShortName())                
                log.info(i_checkParent.moduleParent)
                if i_checkParent in d_moduleParents.keys() and i_checkParent.moduleParent == [i_Parent]:
                    log.info('Match found!')
                    l_orderedParentModules.append(i_checkParent)
                    d_moduleChildrenCull.pop(i_checkParent)
                    """
                    
    return l_orderedParentModules
    """
    while len(moduleChildrenD)>0 and cnt < 100:
    for module in self.orderedParentModules:
        print module
        for child in moduleChildrenD.keys():
            cnt +=1
            if child in moduleParents.keys() and moduleParents[child] == module:
                self.orderedParentModules.append(child)
                moduleChildrenD.pop(child)
    """
 