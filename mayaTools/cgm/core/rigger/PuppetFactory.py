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
class PuppetFunc(cgmGeneral.cgmFuncCls):
    def __init__(self,*args,**kws):
	"""
	"""	
	try:
	    try:puppet = kws['puppet']
	    except:
		try:puppet = args[0]
		except:raise StandardError,"No kw or arg puppet found'"
	except Exception,error:raise StandardError,"PuppetFunc failed to initialize | %s"%error
	self._str_funcName= "testPuppetFunc"		
	super(PuppetFunc, self).__init__(*args, **kws)
	self.mi_puppet = puppet	
	self._l_ARGS_KWS_DEFAULTS = [{'kw':'puppet',"default":None}]	
	#=================================================================
	
class puppetFactoryWrapperOLD(cgmGeneral.cgmFuncCls):
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
	self.d_kws = {'puppet':puppet}
	self.mi_puppet = puppet
	#self.l_funcSteps = [{'step':'Get Data','call':self._getData}]
	#=================================================================
	
    def __func__(self):
	"""
	"""
	self.report()
	
def exampleWrap(*args,**kws):
    class clsPuppetFunc(PuppetFunc):
	def __init__(self,*args,**kws):
	    """
	    """	
	    super(clsPuppetFunc, self).__init__(*args,**kws)
	    self._str_funcName = 'example(%s)'%self.mi_puppet.p_nameShort	
	    self.__dataBind__()
	    #self.l_funcSteps = [{'step':'Get Data','call':self._getData}]
	    
	    #The idea is to register the functions needed to be called
	    #=================================================================
	    
	def __func__(self):
	    """
	    """
	    self.report()
	    
    #We wrap it so that it autoruns and returns
    return clsPuppetFunc(*args,**kws).go()	

def stateCheck(puppet = None,arg = None,*args,**kws):
    class clsPuppetFunc(puppetFactoryWrapper):
	def __init__(self,puppet = None,arg = None,*args,**kws):
	    """
	    """	
	    super(clsPuppetFunc, self).__init__(puppet,*args,**kws)
	    self._str_funcName = 'stateCheck(%s)'%self.mi_puppet.p_nameShort	
	    self.__dataBind__()
	    self.d_kws['arg'] = arg
	    
	    #self.l_funcSteps = [{'step':'Get Data','call':self._getData}]	    
	    #The idea is to register the functions needed to be called
	    #=================================================================
	    
	def __func__(self):
	    """
	    """
	    ml_orderedModules = getOrderedModules(self.mi_puppet)
	    
	    for mod in ml_orderedModules:
		try:
		    mod.stateCheck(self.d_kws['arg'])
		except Exception,error: log.error("%s module: %s | %s"%(self._str_reportStart,mod.p_nameShort,error))
	    
    #We wrap it so that it autoruns and returns
    return clsPuppetFunc(puppet,arg,*args,**kws).go()	

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Puppet Utilities
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
def simplePuppetReturn():
    try:
	catch = mc.ls(type='network')
	returnList = []
	if catch:
	    for o in catch:
		if attributes.doGetAttr(o,'mClass') in ['cgmPuppet','cgmMorpheusPuppet']:
		    returnList.append(o)
	return returnList
    except Exception,error:raise StandardError,"[func: puppetFactory.simplePuppetReturn]{%s}"%error

def getUnifiedGeo(*args,**kws):
    class fncWrap(PuppetFunc):
	def __init__(self,*args,**kws):
	    """
	    """	
	    super(fncWrap, self).__init__(*args,**kws)
	    self._str_funcName = 'puppetFactory.getUnifiedGeo(%s)'%self.mi_puppet.p_nameShort	
	    self.__dataBind__(*args,**kws)
	def __func__(self):
	    buffer = self.mi_puppet.getMessage('unifiedGeo')
	    if buffer and len(buffer) == 1 and search.returnObjectType(buffer[0]) in geoTypes:
		return buffer[0]
	    return False
    return fncWrap(*args,**kws).go()
    
def getGeo(*args,**kws):
    class fncWrap(PuppetFunc):
	def __init__(self,*args,**kws):
	    """
	    """	
	    super(fncWrap, self).__init__(*args,**kws)
	    self._str_funcName = 'puppetFactory.getGeo(%s)'%self.mi_puppet.p_nameShort	
	    self.__dataBind__(*args,**kws)
	    #self.l_funcSteps = [{'step':'Get Data','call':self._getData}]
	def __func__(self):
	    geo = []
	    for o in self.mi_puppet.masterNull.geoGroup.getAllChildren(True):
		if search.returnObjectType(o) in geoTypes:
		    buff = mc.ls(o,long=True)
		    geo.append(buff[0])
	    return geo
    return fncWrap(*args,**kws).go()

def getModules(*args,**kws):
    class fncWrap(PuppetFunc):
	def __init__(self,*args,**kws):
	    """
	    """	
	    super(fncWrap, self).__init__(*args,**kws)
	    self._str_funcName = 'puppetFactory.getModules(%s)'%self.mi_puppet.p_nameShort	
	    self.__dataBind__(*args,**kws)
	def __func__(self):
	    try:ml_initialModules = self.mi_puppet.moduleChildren
	    except:ml_initialModules = []
	    ml_allModules = copy.copy(ml_initialModules)
	    for m in ml_initialModules:
		for m in m.getAllModuleChildren():
		    if m not in ml_allModules:
			ml_allModules.append(m)
	    #self.i_modules = ml_allModules
	    return ml_allModules
    return fncWrap(*args,**kws).go()

def gatherModules(*args,**kws):
    class fncWrap(PuppetFunc):
	def __init__(self,*args,**kws):
	    """
	    """	
	    super(fncWrap, self).__init__(*args,**kws)
	    self._str_funcName = 'puppetFactory.gatherModules(%s)'%self.mi_puppet.p_nameShort	
	    self.__dataBind__(*args,**kws)
	def __func__(self):
	    for mModule in getModules(self.mi_puppet,**kws):
		try:self.mi_puppet.connectModule(mModule,**kws)
		except Exception,error:raise StandardError,"[mModule : %s]{%s}"%(mModule.p_nameShort,error)	
    return fncWrap(*args,**kws).go()

def getModuleFromDict(*args,**kws):
    """
    Pass a check dict of attrsibutes and arguments. If that module is found, it returns it.
    checkDict = {'moduleType':'torso',etc}
    """    
    class fncWrap(PuppetFunc):
	def __init__(self,*args,**kws):
	    """
	    """	
	    super(fncWrap, self).__init__(*args,**kws)
	    self._str_funcName = 'puppetFactory.getModuleFromDict(%s)'%self.mi_puppet.p_nameShort	
	    self.__dataBind__(*args,**kws)
	def __func__(self):
	    args = self._l_funcArgs
	    kws = copy.copy(self._d_funcKWs)
	    if 'checkDict' in kws.keys():
		checkDict = kws.get('checkDict')
	    else:
		try:
		    '''
		    kws.pop('puppet')
		    for s in self._l_ARGS_KWS_DEFAULTS:
			str_key = s['kw']
			if str_key in kws.keys():kws.pop(str_key)
		    checkDict = kws
		    '''
		    checkDict = self.get_cleanKWS()
		except Exception,error:raise StandardError,"[kws cleaning]{%s}"%(error)	
	    assert type(checkDict) is dict,"Arg must be dictionary"
	    for i_m in self.mi_puppet.moduleChildren:
		matchBuffer = 0
		for key in checkDict.keys():
		    if i_m.hasAttr(key) and attributes.doGetAttr(i_m.mNode,key) in checkDict.get(key):
			matchBuffer +=1
			log.debug("Match: %s"%i_m.getShortName())
		if matchBuffer == len(checkDict.keys()):
		    log.debug("Found Module: '%s'"%i_m.getShortName())
		    return i_m
	    return False
    return fncWrap(*args,**kws).go()





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
    
def getOrderedModules(*args,**kws):
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
    class fncWrap(PuppetFunc):
	def __init__(self,*args,**kws):
	    """
	    """	
	    super(fncWrap, self).__init__(*args,**kws)
	    self._str_funcName = 'puppetFactory.getOrderedModules(%s)'%self.mi_puppet.p_nameShort
	    self._str_funcHelp = "Returns ordered modules of a character\nBy processing the various modules by parent into a logic list"
	    self.__dataBind__(*args,**kws)
	    #self.l_funcSteps = [{'step':'Gather Info','call':self._gatherInfo_},
	    
	def __func__(self):
	    l_orderedParentModules = []
	    moduleRoots = []
	       
	    try:#Find the roots 
		for i_m in self.mi_puppet.moduleChildren:
		    #log.debug("%s.moduleParent: %s"%(i_m.getShortName(),i_m.getMessage('moduleParent')))
		    #log.debug("%s.modulePuppet: %s"%(i_m.getShortName(),i_m.getMessage('modulePuppet')))        
		    if i_m.getMessage('modulePuppet') == [self.mi_puppet.mNode] and not i_m.getMessage('moduleParent'):
			log.info("Root found: %s"%(i_m.getShortName()))
			moduleRoots.append(i_m) 
	    except Exception,error:raise StandardError,"[Finding roots]{'%s'}"%(error)	

	    l_childrenList = copy.copy(self.mi_puppet.moduleChildren)
	    
	    if not moduleRoots:
		log.critical("No module root found!")
		return False
	    
	    for i_m in moduleRoots:
		l_childrenList.remove(i_m)
		l_orderedParentModules.append(i_m)
			
	    cnt = 0
	    try:#Process the childdren looking for parents as children and so on and so forth, appending them as it finds them
		while len(l_childrenList)>0 and cnt < 100:#While we still have a cull list
		    cnt+=1                        
		    if cnt == 99:
			self.log_error('max count')
		    for i_Parent in l_orderedParentModules:
			for i_child in l_childrenList:#for each ordered parent module we've found (starting with root)
			    try:
				#log.info("checking i_child: %s"%i_Parent.getShortName())
				if i_child.moduleParent == i_Parent:
				    self.log_info("mChild %s | mParent : %s"%(i_child.p_nameShort,i_Parent.p_nameShort))	
				    l_orderedParentModules.append(i_child)
				    l_childrenList.remove(i_child)  
			    except Exception,error:raise StandardError,"[mParent : %s | checking: %s]{%s}"%(i_Parent.p_nameShort,i_child.p_nameShort,error)	
	    except Exception,error:raise StandardError,"[Processing Children]{%s}"%(error)	

	    return l_orderedParentModules	    
	
	    
	    
	    for mModule in getModules(self.mi_puppet,**kws):
		try:self.mi_puppet.connectModule(mModule,**kws)
		except Exception,error:raise StandardError,"[mModule : %s]{%s}"%(mModule.p_nameShort,error)	
    return fncWrap(*args,**kws).go()

'''
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
'''
#=====================================================================================================
#>>> Anim functions functions
#=====================================================================================================
def animReset(*args,**kws):
    class fncWrap(PuppetFunc):
	def __init__(self,*args,**kws):
	    """
	    """	
	    super(fncWrap, self).__init__(*args,**kws)
	    self._str_funcName = 'animReset.getModules(%s)'%self.mi_puppet.p_nameShort	
	    self.l_funcSteps = [{'step':'Process','call':self._process}]	
	    self._l_ARGS_KWS_DEFAULTS = [{'kw':'transformsOnly',"default":True,'help':"Only reset transforms","argType":"bool"}] 
	    self.__dataBind__(*args,**kws)
	    
	def _process(self):
	    """
	    """
	    self.mi_puppet.puppetSet.select()
	    try:
		if mc.ls(sl=True):
		    ml_resetChannels.main(transformsOnly = self._d_funcKWs.get('transformsOnly'))		    
		    return True
		return False  
	    except Exception,error:
		self.log_error("Failed to reset | errorInfo: {%s}"%error)
		return False
    return fncWrap(*args,**kws).go()

class animReset2(cgmGeneral.cgmFuncCls):
    def __init__(self,puppetInstance = None,**kws):
	"""
	"""	
	super(animReset, self).__init__(self,**kws)
	self._str_funcName = 'animReset(%s)'%puppetInstance.p_nameShort	
	self.__dataBind__(**kws)
	self.d_kws = {'puppetInstance':puppetInstance}
	self.l_funcSteps = [{'step':'Process','call':self._process}]	
	#=================================================================

    def _process(self):
	"""
	"""
	puppetInstance = self.d_kws['puppetInstance']
	puppetInstance.puppetSet.select()
	if mc.ls(sl=True):
	    ml_resetChannels.main(transformsOnly = self._d_funcKWs.get('transformsOnly'))
	    return True
	return False  
    
def mirrorMe(*args,**kws):
    class fncWrap(PuppetFunc):
	def __init__(self,*args,**kws):
	    """
	    """	
	    super(fncWrap, self).__init__(*args,**kws)
	    self._str_funcName = 'mirrorMe.getModules(%s)'%self.mi_puppet.p_nameShort	
	    self.l_funcSteps = [{'step':'Process','call':self._process}]	
	    self.__dataBind__(*args,**kws)
	    
	def _process(self):
	    """
	    """
	    self.mi_puppet.puppetSet.select()
	    l_controls = mc.ls(sl=True)
	    log.info(l_controls)
	    if l_controls:
		r9Anim.MirrorHierarchy(l_controls).mirrorData(mode = '')
		mc.select(l_controls)
		return True	    
	    return False
    return fncWrap(*args,**kws).go()


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


def get_mirrorIndexDict(*args,**kws):
    class fncWrap(PuppetFunc):
	def __init__(self,*args,**kws):
	    """
	    """	
	    super(fncWrap, self).__init__(*args,**kws)
	    self._str_funcName = 'puppetFactory.get_mirrorIndexDict(%s)'%self.mi_puppet.p_nameShort	
	    self.__dataBind__(*args,**kws)	
	    
	def __func__(self):
	    """
	    """
	    d_return = {}
	    for mod in getModules(self.mi_puppet):
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
			    log.debug("%s mod: %s | side: %s | idx :%s already stored"%(self._str_reportStart,mod.p_nameShort, str_side,int_idx))
			else:
			    d_return[int_side].append(int_idx)
	    return d_return
    return fncWrap(*args,**kws).go()
'''
def get_mirrorIndexDictFromSide(*args,**kws):
    class fncWrap(PuppetFunc):
	def __init__(self,*args,**kws):
	    """
	    """	
	    super(fncWrap, self).__init__(*args,**kws)
	    self._str_funcName = 'mirrorMe.getModules(%s)'%self.mi_puppet.p_nameShort	
	    self._l_ARGS_KWS_DEFAULTS.append({'kw':'str_side',"default":None,'help':"Which side arg","argType":"string"}) 
	    self.__dataBind__(*args,**kws)
	    self.l_funcSteps = [{'step':'Query','call':self._verifyData},
	                        {'step':'Process','call':self._process}]	
	    
	def _verifyData(self):
	    """
	    """
	    #self.d_kws['str_side'],
	    self.str_side = cgmGeneral.verify_mirrorSideArg(self.d_kws['str_side'],**kws)	
		
	def _process(self):
	    """
	    """
	    d_return = {}
	    for mod in getModules(self.mi_puppet):
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
			    log.debug("mod: %s | side: %s | idx :%s already stored"%(mod.p_nameShort, str_side,int_idx))
			else:
			    d_return[int_side].append(int_idx)
	    return d_return
    return fncWrap(*args,**kws).go()
'''

def get_nextMirrorIndex(*args,**kws):
    class fncWrap(PuppetFunc):
	def __init__(self,*args,**kws):
	    """
	    """	
	    super(fncWrap, self).__init__(*args,**kws)
	    self._str_funcName = 'puppetFactory.get_nextMirrorIndex(%s)'%self.mi_puppet.p_nameShort	
	    self._l_ARGS_KWS_DEFAULTS.append({'kw':'str_side',"default":None,'help':"Which side arg","argType":"string"}) 
	    self.__dataBind__(*args,**kws)
	    self.l_funcSteps = [{'step':'Query','call':self._verifyData},
	                        {'step':'Process','call':self._process}]	
	    
	def _verifyData(self):
	    """
	    """
	    #self.d_kws['str_side'],
	    self.str_side = cgmGeneral.verify_mirrorSideArg(self.d_kws['str_side'],**kws)	
		
	def _process(self):
	    """
	    """
	    l_return = []
	    for mModule in getModules(self.mi_puppet):
		log.info("Checking: %s"%mModule.p_nameShort)		
		if mModule.get_mirrorSideAsString() == self.str_side :
		    log.info("match Side %s | %s"%(self.str_side,mModule.p_nameShort))		    
		    try:mi_moduleSet = mModule.rigNull.moduleSet.getMetaList()
		    except:mi_moduleSet = []
		    for mObj in mi_moduleSet:
			try:
			    int_side = mObj.getAttr('mirrorSide')
			    int_idx = mObj.getAttr('mirrorIndex')
			    str_side = mObj.getEnumValueString('mirrorSide')		    
			    l_return.append(int_idx)
			    l_return.sort()
			except Exception,error: raise StandardError,"[mObj: '%s' | mModule: '%s']{%s}"%(mObj.p_nameShort,mModule.p_nameShort,error)

	    if l_return:
		return max(l_return)+1
	    else:return 0
    return fncWrap(*args,**kws).go()

def get_nextMirrorIndex2(puppet = None,side = None,*args,**kws):
    class clsPuppetFunc(puppetFactoryWrapper):
	def __init__(self,puppet = None,side = None,*args,**kws):
	    """
	    """	
	    super(clsPuppetFunc, self).__init__(puppet,*args,**kws)
	    self._str_funcName = 'stateCheck(%s)'%self.mi_puppet.p_nameShort	
	    self.__dataBind__()
	    self.d_kws['side'] = side
	    
	    #self.l_funcSteps = [{'step':'Get Data','call':self._getData}]	    
	    #The idea is to register the functions needed to be called
	    #=================================================================
	    
	def __func__(self):
	    """
	    """
	    l_return = []
	    for mModule in getModules(self.mi_puppet):
		log.info("Checking: %s"%mModule.p_nameShort)		
		if mModule.get_mirrorSideAsString() == self.d_kws['side'].capitalize() :
		    log.info("match Side %s | %s"%(self.d_kws['side'],mModule.p_nameShort))		    
		    try:mi_moduleSet = mModule.rigNull.moduleSet.getMetaList()
		    except:mi_moduleSet = []
		    for mObj in mi_moduleSet:
			try:
			    int_side = mObj.getAttr('mirrorSide')
			    int_idx = mObj.getAttr('mirrorIndex')
			    str_side = mObj.getEnumValueString('mirrorSide')		    
			    l_return.append(int_idx)
			    l_return.sort()
			except Exception,error: raise StandardError,"[mObj: %s | mModule: %s]{%s}"%(mModule.p_nameShort,mObj.p_nameShort,error)

	    if l_return:
		return max(l_return)+1
	    else:return 0
	
    #We wrap it so that it autoruns and returns
    return clsPuppetFunc(puppet,side,*args,**kws).go()	

def animSetAttr(puppetInstance = None, attr = None, value = None, settingsOnly = False):
    class clsPuppetFunc(puppetFactoryWrapper):
	def __init__(self,puppetInstance = None, attr = None, value = None, settingsOnly = False):
	    """
	    """	
	    super(clsPuppetFunc, self).__init__(puppetInstance)
	    self._str_funcName = 'animSetAttr(%s)'%self.mi_puppet.p_nameShort
	    self.__dataBind__()
	    self.d_kws['attr'] = attr	  
	    self.d_kws['value'] = value	  
	    self.d_kws['settingsOnly'] = settingsOnly	  
	    self.l_funcSteps = [{'step':'Process','call':self.__func__}]
	    #The idea is to register the functions needed to be called
	    #=================================================================
	    
	def __func__(self): 
	    try:
		ml_buffer = self.mi_puppet.moduleChildren
		mayaMainProgressBar = cgmGeneral.doStartMayaProgressBar(len(ml_buffer))  
		for i,mModule in enumerate(ml_buffer):
		    try:
			mc.progressBar(mayaMainProgressBar, edit=True, status = "%s >> step:'%s' "%(self._str_reportStart,mModule.p_nameShort), progress=i)    				        			
			if self.d_kws['settingsOnly']:
			    mi_rigNull = mModule.rigNull
			    if mi_rigNull.getMessage('settings'):
				mi_rigNull.settings.__setattr__(self.d_kws['attr'],self.d_kws['value'])
			else:
			    for o in mModule.rigNull.moduleSet.getList():
				attributes.doSetAttr(o,self.d_kws['attr'],self.d_kws['value'])
		    except Exception,error:
			log.error("%s  child: %s | %s"%(self._str_reportStart,mModule.p_nameShort,error))
		cgmGeneral.doEndMayaProgressBar(mayaMainProgressBar)#Close out this progress bar 
		return False
	    except Exception,error:
		try:cgmGeneral.doEndMayaProgressBar(mayaMainProgressBar)#Close out this progress bar        	
		except:
		    raise StandardError,error
	    return False  
	
    #We wrap it so that it autoruns and returns
    return clsPuppetFunc(puppetInstance,attr,value,settingsOnly).go()


