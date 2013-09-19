import time
import maya.cmds as mc
import copy as copy

import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

# From Red9 =============================================================
from Red9.core import Red9_Meta as r9Meta
from Red9.core import Red9_General as r9General
from Red9.core import Red9_AnimationUtils as r9Anim

# From cgm ==============================================================
from cgm.lib import (search,attributes)
from cgm.core import cgm_General as cgmGeneral
from cgm.lib.ml import ml_resetChannels

reload(cgmGeneral)
#Shared Settings
#========================= 
geoTypes = 'nurbsSurface','mesh','poly','subdiv'

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Puppet Wrapper
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
class puppetFactoryWrapper(cgmGeneral.cgmFuncCls):
    def __init__(self,puppet = None,**kws):
	"""
	"""	
	super(puppetFactoryWrapper, self).__init__(self,**kws)
	try:
	    puppet.mNode
	except StandardError,error:
	    raise StandardError,error	
	
	self._str_funcName = 'puppetFactoryWrapper(%s)'%puppet.p_nameShort	
	self.__dataBind__(**kws)
	self.d_kwsDefined = {'puppet':puppet}
	self._mi_puppet = puppet
	#self.l_funcSteps = [{'step':'Get Data','call':self._getData}]
	#=================================================================
	if log.getEffectiveLevel() == 10:self.report()#If debug
	
    def __func__(self):
	"""
	"""
	self.report()
	
def exampleWrap(puppet = None,*args,**kws):
    class clsPuppetFunc(puppetFactoryWrapper):
	def __init__(self,puppet = None,*args,**kws):
	    """
	    """	
	    super(clsPuppetFunc, self).__init__(puppet,*args,**kws)
	    self._str_funcName = 'example(%s)'%self._mi_puppet.p_nameShort	
	    self.__dataBind__()
	    #self.l_funcSteps = [{'step':'Get Data','call':self._getData}]
	    
	    #The idea is to register the functions needed to be called
	    #=================================================================
	    if log.getEffectiveLevel() == 10:self.report()#If debug
	    
	def __func__(self):
	    """
	    """
	    self.report()
	    
    #We wrap it so that it autoruns and returns
    return clsPuppetFunc(puppet).go()	

def stateCheck(puppet = None,arg = None,*args,**kws):
    class clsPuppetFunc(puppetFactoryWrapper):
	def __init__(self,puppet = None,arg = None,*args,**kws):
	    """
	    """	
	    super(clsPuppetFunc, self).__init__(puppet,*args,**kws)
	    self._str_funcName = 'stateCheck(%s)'%self._mi_puppet.p_nameShort	
	    self.__dataBind__()
	    self.d_kwsDefined['arg'] = arg
	    
	    #self.l_funcSteps = [{'step':'Get Data','call':self._getData}]	    
	    #The idea is to register the functions needed to be called
	    #=================================================================
	    if log.getEffectiveLevel() == 10:self.report()#If debug
	    
	def __func__(self):
	    """
	    """
	    ml_orderedModules = getOrderedModules(self._mi_puppet)
	    
	    for mod in ml_orderedModules:
		try:
		    mod.stateCheck(self.d_kwsDefined['arg'])
		except Exception,error: log.error("%s module: %s | %s"%(self._str_reportStart,mod.p_nameShort,error))
	    
    #We wrap it so that it autoruns and returns
    return clsPuppetFunc(puppet,arg,*args,**kws).go()	

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Puppet Utilities
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
def simplePuppetReturn():
    catch = mc.ls(type='network')
    returnList = []
    if catch:
        for o in catch:
            if attributes.doGetAttr(o,'mClass') in ['cgmPuppet','cgmMorpheusPuppet']:
                returnList.append(o)
    return returnList



def getUnifiedGeo(self):
    """
    Returns geo in a puppets geo folder, ALL geo to be used by a puppet should be in there
    """
    buffer = self.getMessage('unifiedGeo')
    if buffer and len(buffer) == 1 and search.returnObjectType(buffer[0]) in geoTypes:
        return buffer[0]
    return False

 
def getGeo(self):
    """
    Returns geo in a puppets geo folder, ALL geo to be used by a puppet should be in there
    """    
    geo = []
    for o in self.masterNull.geoGroup.getAllChildren(True):
        if search.returnObjectType(o) in geoTypes:
            buff = mc.ls(o,long=True)
            geo.append(buff[0])
    return geo

   
def getModules(self):
    """
    Get the modules of a puppet in a usable format:
    
    i_modules(dict){indexed to name}
    
    """
    _str_funcName = "getModules"  
    log.debug(">>> %s >>> "%(_str_funcName) + "="*75)  
    ml_modules = False
    #Get connected Modules
    #self.i_modules = self.getChildMetaNodes(mAttrs = ['moduleChildren'])
    try:ml_initialModules = self.moduleChildren
    except:ml_initialModules = []
    ml_allModules = copy.copy(ml_initialModules)
    for m in ml_initialModules:
        for m in m.getAllModuleChildren():
            if m not in ml_allModules:
                ml_allModules.append(m)
    self.i_modules = ml_allModules
    return self.i_modules

def gatherModules(self):
    """
    Connect all children modules
    """
    _str_funcName = "gatherModules"  
    try:
        log.debug(">>> %s >>> "%(_str_funcName) + "="*75)      
        for m in getModules(self):
            self.connectModule(m)
    except Exception,error:
		raise StandardError,"%s >>> error: %s"%(_str_funcName,error)

  
def getModuleFromDict(self,*args,**kws):
    """
    Pass a check dict of attrsibutes and arguments. If that module is found, it returns it.
    
    checkDict = {'moduleType':'torso',etc}
    """
    try:       
        if args:
            checkDict = args[0]
        elif 'checkDict' in kws.keys():
            checkDict = kws.get('checkDict')
        else:
            checkDict = kws
        assert type(checkDict) is dict,"Arg must be dictionary"
        for i_m in self.moduleChildren:
            matchBuffer = 0
            for key in checkDict.keys():
                if i_m.hasAttr(key) and attributes.doGetAttr(i_m.mNode,key) in checkDict.get(key):
                    matchBuffer +=1
                    log.debug("Match: %s"%i_m.getShortName())
            if matchBuffer == len(checkDict.keys()):
                log.debug("Found Morpheus Module: '%s'"%i_m.getShortName())
                return i_m
        return False
    except Exception,error:
        log.error("kws: %s"%kws)
        raise StandardError,"%s.getModuleFromDict>> error: %s"%error
    
 
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

#=====================================================================================================
#>>> Anim functions functions
#=====================================================================================================
class animReset(cgmGeneral.cgmFuncCls):
    def __init__(self,puppetInstance = None,**kws):
	"""
	"""	
	super(animReset, self).__init__(self,**kws)
	self._str_funcName = 'animReset(%s)'%puppetInstance.p_nameShort	
	self.__dataBind__(**kws)
	self.d_kwsDefined = {'puppetInstance':puppetInstance}
	self.l_funcSteps = [{'step':'Process','call':self._process}]	
	#=================================================================
	if log.getEffectiveLevel() == 10:self.report()#If debug

    def _process(self):
	"""
	"""
	puppetInstance = self.d_kwsDefined['puppetInstance']
	puppetInstance.puppetSet.select()
	if mc.ls(sl=True):
	    ml_resetChannels.main(transformsOnly = self._d_funcKWs.get('transformsOnly'))
	    return True
	return False  
    
class mirrorMe(cgmGeneral.cgmFuncCls):
    def __init__(self,puppetInstance = None,**kws):
	"""
	"""	
	super(mirrorMe, self).__init__(self,**kws)
	self._str_funcName = 'mirrorMe(%s)'%puppetInstance.p_nameShort	
	self.__dataBind__(**kws)
	self.d_kwsDefined = {'puppetInstance':puppetInstance}
	self.l_funcSteps = [{'step':'Process','call':self._process}]
	#=================================================================
	if log.getEffectiveLevel() == 10:self.report()#If debug

    def _process(self):
	"""
	"""
	puppetInstance = self.d_kwsDefined['puppetInstance']
	l_controls = puppetInstance.puppetSet.getList()
	if l_controls:
	    r9Anim.MirrorHierarchy(l_controls).mirrorData(mode = '')
	    mc.select(l_controls)
	    return True

'''	
def mirrorMe(self,**kws):
    _str_funcName = "%s.mirrorMe()"%self.p_nameShort  
    log.debug(">>> %s "%(_str_funcName) + "="*75)  	
    try:
	l_controls = self.puppetSet.getList()
	#for mModule in getModules(self):
	"""
	l_controls = []
	for mModule in self.moduleChildren:
	    try:mModule.mirrorMe()
	    except:pass
	"""
	if l_controls:
	    r9Anim.MirrorHierarchy(l_controls).mirrorData(mode = '')
	    mc.select(l_controls)
	    return True
	#return False
    except Exception,error:
	log.error("%s >> error: %s"%(_str_funcName,error))
	return False'''

def get_mirrorIndexDict(puppet = None):
    class clsPuppetFunc(puppetFactoryWrapper):
	def __init__(self,puppet = None):
	    """
	    """	
	    super(clsPuppetFunc, self).__init__(puppet)
	    self._str_funcName = 'get_MirrorIndexDict(%s)'%self._mi_puppet.p_nameShort	
	    self.__dataBind__()
	    
	    self.l_funcSteps = [{'step':'Process','call':self.__func__}]	    
	    #The idea is to register the functions needed to be called
	    #=================================================================
	    if log.getEffectiveLevel() == 10:self.report()#If debug
	    
	def __func__(self):
	    d_return = {}
	    
	    for mod in getModules(self._mi_puppet):
		try:mi_moduleSet = mod.rigNull.moduleSet.getMetaList()
		except:mi_moduleSet = []
		for mObj in mi_moduleSet:
		    if mObj.hasAttr('mirrorSide') and mObj.hasAttr('mirrorIndex'):
			int_side = mObj.getAttr('mirrorSide')
			int_idx = mObj.getAttr('mirrorIndex')
			str_side = mObj.getEnumValueString('mirrorSide')
			
			if not d_return.get(int_side):
			    d_return[int_side] = []
			    
			if int_idx in d_return[int_side]:
			    log.warning("%s mod: %s | side: %s | idx :%s already stored"%(self._str_reportStart,mod.p_nameShort, str_side,int_idx))
			else:
			    d_return[int_side].append(int_idx)
		    
	    return d_return
   
    #We wrap it so that it autoruns and returns
    return clsPuppetFunc(puppet).go()

def get_mirrorIndexDict(puppet = None,side = None):
    class clsPuppetFunc(puppetFactoryWrapper):
	def __init__(self,puppet = None):
	    """
	    """	
	    super(clsPuppetFunc, self).__init__(puppet)
	    self._str_funcName = 'get_MirrorIndexDict(%s)'%self._mi_puppet.p_nameShort	
	    self.__dataBind__()
	    
	    self.l_funcSteps = [{'step':'Process','call':self.__func__}]	    
	    #The idea is to register the functions needed to be called
	    #=================================================================
	    if log.getEffectiveLevel() == 10:self.report()#If debug
	    
	def __func__(self):
	    d_return = {}
	    
	    for mod in getModules(self._mi_puppet):
		try:mi_moduleSet = mod.rigNull.moduleSet.getMetaList()
		except:mi_moduleSet = []
		for mObj in mi_moduleSet:
		    if mObj.hasAttr('mirrorSide') and mObj.hasAttr('mirrorIndex'):
			int_side = mObj.getAttr('mirrorSide')
			int_idx = mObj.getAttr('mirrorIndex')
			str_side = mObj.getEnumValueString('mirrorSide')
			
			if not d_return.get(int_side):
			    d_return[int_side] = []
			    
			if int_idx in d_return[int_side]:
			    log.warning("%s mod: %s | side: %s | idx :%s already stored"%(self._str_reportStart,mod.p_nameShort, str_side,int_idx))
			else:
			    d_return[int_side].append(int_idx)
		    
	    return d_return
   
    #We wrap it so that it autoruns and returns
    return clsPuppetFunc(puppet,side).go()	

def get_nextMirrorIndex(puppet = None,side = None,*args,**kws):
    class clsPuppetFunc(puppetFactoryWrapper):
	def __init__(self,puppet = None,side = None,*args,**kws):
	    """
	    """	
	    super(clsPuppetFunc, self).__init__(puppet,*args,**kws)
	    self._str_funcName = 'stateCheck(%s)'%self._mi_puppet.p_nameShort	
	    self.__dataBind__()
	    self.d_kwsDefined['side'] = side
	    
	    #self.l_funcSteps = [{'step':'Get Data','call':self._getData}]	    
	    #The idea is to register the functions needed to be called
	    #=================================================================
	    if log.getEffectiveLevel() == 10:self.report()#If debug
	    
	def __func__(self):
	    """
	    """
	    l_return = []
	    
	    for mModule in getModules(self._mi_puppet):
		#log.info("Checking: %s"%mModule.p_nameShort)		
		if mModule.get_mirrorSideAsString() == self.d_kwsDefined['side'].capitalize() :
		    #log.info("match Side %s | %s"%(self.d_kwsDefined['side'],mModule.p_nameShort))		    
		    try:mi_moduleSet = mModule.rigNull.moduleSet.getMetaList()
		    except:mi_moduleSet = []
		    for mObj in mi_moduleSet:
			int_side = mObj.getAttr('mirrorSide')
			int_idx = mObj.getAttr('mirrorIndex')
			str_side = mObj.getEnumValueString('mirrorSide')
						    
			l_return.append(int_idx)
			l_return.sort()
			
	    if l_return:
		return max(l_return)+1
	    else:return 0
	
    #We wrap it so that it autoruns and returns
    return clsPuppetFunc(puppet,side,*args,**kws).go()	