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
from cgm.core import cgm_Meta as cgmMeta
from cgm.lib import (search,attributes)
from cgm.core import cgm_General as cgmGeneral
from cgm.lib.ml import ml_resetChannels

#Shared Settings
#========================= 
geoTypes = 'nurbsSurface','mesh','poly','subdiv'
_d_KWARG_mPuppet = {'kw':'mPuppet',"default":None,'help':"cgmPuppet mNode or str name","argType":"cgmPuppet"}
_d_KWARG_moduleStateArg = {'kw':'moduleStateArg',"default":0,'help':"What state to check for","argType":"module state"}
_d_KWARG_mirrorSideArg = {'kw':'mirrorSideArg',"default":None,'help':"Which side arg","argType":"string"}
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Puppet Wrapper
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
class PuppetFunc(cgmGeneral.cgmFuncCls):
    def __init__(self,*args,**kws):
	"""
	"""	
	try:
	    try:puppet = kws['mPuppet']
	    except:
		try:puppet = args[0]
		except:raise StandardError,"No kw or arg puppet found'"
	    if puppet.mClass not in ['cgmPuppet','cgmMorpheusPuppet']:
		raise StandardError,"[mPuppet: '%s']{Not a puppet!}"%puppet.mNode
	except Exception,error:raise StandardError,"PuppetFunc failed to initialize | %s"%error
	self._str_funcName= "testPuppetFunc"		
	super(PuppetFunc, self).__init__(*args, **kws)
	self._mi_puppet = puppet	
	self._l_ARGS_KWS_DEFAULTS = [_d_KWARG_mPuppet]	
	#=================================================================
		
def exampleWrap(*args,**kws):
    class clsPuppetFunc(PuppetFunc):
	def __init__(self,*args,**kws):
	    """
	    """	
	    super(clsPuppetFunc, self).__init__(*args,**kws)
	    self._str_funcName = "example('%s')"%self._mi_puppet.cgmName	
	    self.__dataBind__(*args,**kws)
	    #self.l_funcSteps = [{'step':'Get Data','call':self._getData}]
	    
	    #The idea is to register the functions needed to be called
	    #=================================================================
	    
	def __func__(self):
	    """
	    """
	    self.report()
	    
    #We wrap it so that it autoruns and returns
    return clsPuppetFunc(*args,**kws).go()	

def stateCheck(*args,**kws):
    class fncWrap(PuppetFunc):
	def __init__(self,*args,**kws):
	    """
	    """	
	    super(fncWrap, self).__init__(*args,**kws)
	    self._str_funcName = "stateCheck('%s')"%self._mi_puppet.cgmName
	    self._str_funcHelp = "Check to"
	    self._l_ARGS_KWS_DEFAULTS = [_d_KWARG_mPuppet,
	                                 _d_KWARG_moduleStateArg]
	                                 
	    self.__dataBind__(*args,**kws)
	    raise NotImplementedError, "Not sure this is needed"
	    #=================================================================
	    
	def __func__(self):
	    """
	    """
	    ml_orderedModules = getOrderedModules(self._mi_puppet)
	    int_lenModules = len(ml_orderedModules)  
	    for i,mModule in enumerate(ml_orderedModules):
		_str_module = mModule.p_nameShort
		self.progressBar_set(status = "Checking Module: '%s' "%(_str_module),progress = i, maxValue = int_lenModules)	    		
		try:
		    mModule.stateCheck(self.d_kws['arg'],**kws)
		except Exception,error: log.error("%s module: %s | %s"%(self._str_reportStart,_str_module,error))
    return fncWrap(*args,**kws).go()

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
	    self._str_funcName = "puppetFactory.getUnifiedGeo('%s')"%self._mi_puppet.cgmName	
	    self.__dataBind__(*args,**kws)
	def __func__(self):
	    buffer = self._mi_puppet.getMessage('unifiedGeo')
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
	    self._str_funcName = "puppetFactory.getGeo('%s')"%self._mi_puppet.cgmName	
	    self._str_funcHelp = "Get all the geo in our geo groups"	    
	    self.__dataBind__(*args,**kws)
	    #self.l_funcSteps = [{'step':'Get Data','call':self._getData}]
	def __func__(self):
	    geo = []
	    for o in self._mi_puppet.masterNull.geoGroup.getAllChildren(True):
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
	    self._str_funcName = "puppetFactory.getModules('%s')"%self._mi_puppet.cgmName
	    self._str_funcHelp = "Get the modules of a puppet"	    
	    self.__dataBind__(*args,**kws)
	def __func__(self):
	    try:ml_initialModules = self._mi_puppet.moduleChildren
	    except:ml_initialModules = []
	    int_lenModules = len(ml_initialModules)  

	    ml_allModules = copy.copy(ml_initialModules)
	    for i,m in enumerate(ml_initialModules):
		_str_module = m.p_nameShort	 				
		self.progressBar_set(status = "Checking Module: '%s' "%(_str_module),progress = i, maxValue = int_lenModules)
		for m in m.get_allModuleChildren():
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
	    self._str_funcName = "puppetFactory.gatherModules('%s')"%self._mi_puppet.cgmName	
	    self._str_funcHelp = "Collect all modules where they should be in the heirarchy"	    	    
	    self.__dataBind__(*args,**kws)
	def __func__(self):
	    ml_modules = getModules(self._mi_puppet)
	    int_lenModules = len(ml_modules)
	    
	    for i,mModule in enumerate(ml_modules):
		_str_module = mModule.p_nameShort
		self.progressBar_set(status = "Checking Module: '%s' "%(_str_module),progress = i, maxValue = int_lenModules)		    				    				
		try:self._mi_puppet.connectModule(mModule,**kws)
		except Exception,error:raise StandardError,"[mModule : %s]{%s}"%(_str_module,error)	
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
	    self._str_funcName = "puppetFactory.getModuleFromDict('%s')"%self._mi_puppet.cgmName	
	    self._str_funcHelp = "Search the modues of a puppet for a module by attribute/value kws"	    	    
	    self.__dataBind__(*args,**kws)
	def __func__(self):
	    args = self._l_funcArgs
	    kws = copy.copy(self._d_funcKWs)
	    if 'checkDict' in kws.keys():
		checkDict = kws.get('checkDict')
	    else:
		try:
		    '''
		    kws.pop('mPuppet')
		    for s in self._l_ARGS_KWS_DEFAULTS:
			str_key = s['kw']
			if str_key in kws.keys():kws.pop(str_key)
		    checkDict = kws
		    '''
		    checkDict = self.get_cleanKWS()
		except Exception,error:raise StandardError,"[kws cleaning]{%s}"%(error)	
	    assert type(checkDict) is dict,"Arg must be dictionary"
	    for i_m in self._mi_puppet.moduleChildren:
		matchBuffer = 0
		for key in checkDict.keys():
		    if i_m.hasAttr(key) and attributes.doGetAttr(i_m.mNode,key) in checkDict.get(key):
			matchBuffer +=1
			self.log_debug("Match: %s"%i_m.getShortName())
		if matchBuffer == len(checkDict.keys()):
		    self.log_debug("Found Module: '%s'"%i_m.getShortName())
		    return i_m
	    return False
    return fncWrap(*args,**kws).go()

def getState(*args,**kws):
    class fncWrap(PuppetFunc):
	def __init__(self,*args,**kws):
	    """
	    """	
	    super(fncWrap, self).__init__(*args,**kws)
	    self._str_funcName = "puppetFactory.getState('%s')"%self._mi_puppet.cgmName	
	    self._str_funcHelp = "Get a pupppet's state"	    	    
	    self.__dataBind__(*args,**kws)
	    
	def __func__(self):
	    """
	    """
	    ml_modules = getModules(self._mi_puppet)
	    int_lenModules = len(ml_modules)  
	    
	    if not ml_modules:
		self.log_warning("'%s' has no modules"%self.cgmName)
		return False
	    
	    l_states = []
	    d_states = {}
	    for i,mModule in enumerate(ml_modules):
		_str_module = mModule.p_nameShort
		self.progressBar_set(status = "Checking Module: '%s' "%(_str_module),progress = i, maxValue = int_lenModules)		
		r_state = mModule.getState(**kws)
		l_states.append(r_state)
		d_states[_str_module] = r_state
	    for p in d_states.iteritems():
		self.log_info(" '%s' | state : %s"%(p[0],p[1]))
	    return min(l_states)
    return fncWrap(*args,**kws).go()

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
	    self._str_funcName = "puppetFactory.getOrderedModules('%s')"%self._mi_puppet.cgmName
	    self._str_funcHelp = "Returns ordered modules of a character\nBy processing the various modules by parent into a logic list"
	    self.__dataBind__(*args,**kws)
	    #self.l_funcSteps = [{'step':'Gather Info','call':self._gatherInfo_},
	    
	def __func__(self):
	    l_orderedParentModules = []
	    moduleRoots = []
	       
	    try:#Find the roots 
		for i_m in self._mi_puppet.moduleChildren:
		    #self.log_debug("%s.moduleParent: %s"%(i_m.getShortName(),i_m.getMessage('moduleParent')))
		    #self.log_debug("%s.modulePuppet: %s"%(i_m.getShortName(),i_m.getMessage('modulePuppet')))        
		    if i_m.getMessage('modulePuppet') == [self._mi_puppet.mNode] and not i_m.getMessage('moduleParent'):
			log.info("Root found: %s"%(i_m.getShortName()))
			moduleRoots.append(i_m) 
	    except Exception,error:raise StandardError,"[Finding roots]{'%s'}"%(error)	

	    l_childrenList = copy.copy(self._mi_puppet.moduleChildren)
	    
	    if not moduleRoots:
		log.critical("No module root found!")
		return False
	    
	    for i_m in moduleRoots:
		l_childrenList.remove(i_m)
		l_orderedParentModules.append(i_m)
			
	    cnt = 0
	    int_lenMax = len(l_childrenList)
	    try:#Process the childdren looking for parents as children and so on and so forth, appending them as it finds them
		while len(l_childrenList)>0 and cnt < 100:#While we still have a cull list
		    self.progressBar_set(status = "Remaining to process... ", progress = len(l_childrenList), maxValue = int_lenMax)		    				    		    
		    cnt+=1                        
		    if cnt == 99:
			self.log_error('max count')
		    for i_Parent in l_orderedParentModules:
			for i_child in l_childrenList:#for each ordered parent module we've found (starting with root)
			    try:
				#log.info("checking i_child: %s"%i_Parent.getShortName())
				if i_child.moduleParent == i_Parent:
				    #self.log_info("mChild %s | mParent : %s"%(i_child.p_nameShort,i_Parent.p_nameShort))	
				    l_orderedParentModules.append(i_child)
				    l_childrenList.remove(i_child)  
			    except Exception,error:raise StandardError,"[mParent : %s | checking: %s]{%s}"%(i_Parent.p_nameShort,i_child.p_nameShort,error)	
	    except Exception,error:raise StandardError,"[Processing Children]{%s}"%(error)	

	    return l_orderedParentModules	    
	
	    for mModule in getModules(self._mi_puppet,**kws):
		try:self._mi_puppet.connectModule(mModule,**kws)
		except Exception,error:raise StandardError,"[mModule : %s]{%s}"%(mModule.p_nameShort,error)	
    return fncWrap(*args,**kws).go()


#=====================================================================================================
#>>> Anim functions functions
#=====================================================================================================
def animReset(*args,**kws):
    class fncWrap(PuppetFunc):
	def __init__(self,*args,**kws):
	    """
	    """	
	    super(fncWrap, self).__init__(*args,**kws)
	    self._str_funcName = "animReset.getModules('%s')"%self._mi_puppet.cgmName
	    self._str_funcHelp = "Reset all the connected controls"	    	    
	    self.l_funcSteps = [{'step':'Process','call':self._process}]	
	    self._l_ARGS_KWS_DEFAULTS = [_d_KWARG_mPuppet,cgmMeta._d_KWARG_transformsOnly] 
	    self.__dataBind__(*args,**kws)
	    
	def _process(self):
	    """
	    """
	    self._mi_puppet.puppetSet.select()
	    try:
		if mc.ls(sl=True):
		    ml_resetChannels.main(transformsOnly = self._d_funcKWs.get('transformsOnly'))		    
		    return True
		return False  
	    except Exception,error:
		self.log_error("Failed to reset | errorInfo: {%s}"%error)
		return False
    return fncWrap(*args,**kws).go()

def mirrorMe(*args,**kws):
    class fncWrap(PuppetFunc):
	def __init__(self,*args,**kws):
	    """
	    """	
	    super(fncWrap, self).__init__(*args,**kws)
	    self._str_funcName = "puppetFactory.getModules('%s')"%self._mi_puppet.cgmName
	    self._str_funcHelp = "Mirror all puppets modules"	    	    	    
	    self.l_funcSteps = [{'step':'Process','call':self._process}]	
	    self.__dataBind__(*args,**kws)
	    
	def _process(self):
	    """
	    """
	    self._mi_puppet.puppetSet.select()
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
    self.log_debug(">>> %s "%(_str_funcName) + "="*75)  	
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
	    self._str_funcName = "puppetFactory.get_mirrorIndexDict('%s')"%self._mi_puppet.cgmName
	    self._str_funcHelp = "Get the mirror index dict"	    	    	    	    
	    self.__dataBind__(*args,**kws)	
	    
	def __func__(self):
	    """
	    """
	    d_return = {}
	    ml_modules = getModules(self._mi_puppet)
	    int_lenModules = len(ml_modules)
	    
	    for i,mod in enumerate(ml_modules):
		_str_module = mod.p_nameShort
		self.progressBar_set(status = "Checking Module: '%s' "%(_str_module),progress = i, maxValue = int_lenModules)		    				    		
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
			    self.log_debug("%s mod: %s | side: %s | idx :%s already stored"%(self._str_reportStart,_str_module, str_side,int_idx))
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
	    self._str_funcName = "puppetFactory.getModules('%s')"%self._mi_puppet.cgmName	
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
			    self.log_debug("mod: %s | side: %s | idx :%s already stored"%(mod.p_nameShort, str_side,int_idx))
			else:
			    d_return[int_side].append(int_idx)
	    return d_return
    return fncWrap(*args,**kws).go()
'''

def get_nextMirrorIndex(*args,**kws):
    '''
    pFactory.get_nextMirrorIndex('Center',puppet = m1.modulePuppet)
    m1.modulePuppet.get_nextMirrorIndex('center',reportTimes = 1)
    '''
    class fncWrap(PuppetFunc):
	def __init__(self,*args,**kws):
	    """
	    """	
	    super(fncWrap, self).__init__(*args,**kws)
	    self._str_funcName = 'puppetFactory.get_nextMirrorIndex'
	    self._str_funcHelp = "Get the next available mirror index by side"	    	    	    	    
	    self._l_ARGS_KWS_DEFAULTS = [_d_KWARG_mPuppet,
	                                 _d_KWARG_mirrorSideArg]
	    self.__dataBind__(*args,**kws)
	    self.l_funcSteps = [{'step':'Query','call':self._verifyData},
	                        {'step':'Process','call':self._process}]	
	def _verifyData(self):
	    """
	    """
	    #self.d_kws['str_side'],
	    self.str_side = cgmGeneral.verify_mirrorSideArg(self.d_kws['mirrorSideArg'],**kws)	
		
	def _process(self):
	    """
	    """
	    l_return = []
	    ml_modules = getModules(self._mi_puppet)
	    int_lenModules = len(ml_modules)
	    for i,mModule in enumerate(ml_modules):
		#self.log_info("Checking: '%s'"%mModule.p_nameShort)
		_str_module = mModule.p_nameShort
		if mModule.get_mirrorSideAsString() == self.str_side :
		    self.progressBar_set(status = "Checking Module: '%s' "%(_str_module),progress = i, maxValue = int_lenModules)		    				    
		    self.log_info("Match Side '%s' >> '%s'"%(self.str_side,_str_module))		    
		    try:mi_moduleSet = mModule.rigNull.moduleSet.getMetaList()
		    except:mi_moduleSet = []
		    for mObj in mi_moduleSet:
			try:
			    int_side = mObj.getAttr('mirrorSide')
			    int_idx = mObj.getAttr('mirrorIndex')
			    str_side = mObj.getEnumValueString('mirrorSide')		    
			    l_return.append(int_idx)
			    l_return.sort()
			except Exception,error:
			    self.log_error("[Object failure. mObj: '%s' | mModule: '%s']{%s}"%(mObj.p_nameShort,_str_module,error))
	    if l_return:
		return max(l_return)+1
	    else:return 0
    return fncWrap(*args,**kws).go()

def animSetAttr(*args,**kws):
    class fncWrap(PuppetFunc):
	def __init__(self,*args,**kws):
	    """
	    """	
	    #attr = None, value = None, settingsOnly = False
	    super(fncWrap, self).__init__(*args,**kws)
	    self._str_funcName = 'puppetFactory.animSetAttr'
	    
	    self._l_ARGS_KWS_DEFAULTS = [_d_KWARG_mPuppet,cgmMeta._d_KWARG_attr,cgmMeta._d_KWARG_value,
	                                 {'kw':'settingsOnly',"default":False,'help':"Only check settings controls","argType":"bool"}]
	    self.__dataBind__(*args,**kws)	    	    
	def __func__(self):
	    """
	    """
	    ml_buffer = self._mi_puppet.moduleChildren
	    log.info("here")
	    int_lenModules = len(ml_buffer)
	    for i,mModule in enumerate(ml_buffer):
		try:
		    _str_module = mModule.p_nameShort
		    self.progressBar_set(status = "module: '%s' "%(_str_module),progress = i, maxValue = int_lenModules)		    
		    if self.d_kws['settingsOnly']:
			mi_rigNull = mModule.rigNull
			if mi_rigNull.getMessage('settings'):
			    mi_rigNull.settings.__setattr__(self.d_kws['attr'],self.d_kws['value'])
		    else:
			for o in mModule.rigNull.moduleSet.getList():
			    attributes.doSetAttr(o,self.d_kws['attr'],self.d_kws['value'])
		except Exception,error:
		   self.log_error("[Module: %s ]{%s}"%(_str_module,error))
    return fncWrap(*args,**kws).go()

def controlSettings_setModuleAttrs(*args,**kws):
    class fncWrap(PuppetFunc):
	def __init__(self,*args,**kws):
	    """
	    """
	    super(fncWrap, self).__init__(*args, **kws)
	    self._str_funcName= "controlSettings_setModuleAttrs('%s')"%self._mi_puppet.cgmName
	    self._str_funcHelp = "Looks for match attributes combining module part names and the arg and pushes values"
	    self._l_ARGS_KWS_DEFAULTS = [_d_KWARG_mPuppet,
	                                 cgmMeta._d_KWARG_attr,
	                                 cgmMeta._d_KWARG_value] 			    
	    self.__dataBind__(*args,**kws)	    
	    #=================================================================
	def __func__(self):
	    """
	    """
	    try:#Query ========================================================
		mi_puppet = self._mi_puppet
		kws = self.d_kws
		_value = self.d_kws['value']
		_attr = self.d_kws['attr']
		mi_masterSettings = mi_puppet.masterControl.controlSettings		
	    except Exception,error:raise StandardError,"[Query]{%s}"%error
	
	    try:#Process ========================================================	    
		ml_modules = getModules(**kws)
		int_lenMax = len(ml_modules)
		
		for i,mModule in enumerate(ml_modules):
		    try:
			self.progressBar_set(status = "%s step:'%s' "%(self._str_funcName,mModule.p_nameShort), progress = i, maxValue = int_lenMax)		    				    		    
			_str_basePart = mModule.getPartNameBase()
			_str_attrToFind = "%s%s"%(_str_basePart,_attr)
			if mi_masterSettings.hasAttr(_str_attrToFind):
			    try:
				attributes.doSetAttr(mi_masterSettings.mNode,_str_attrToFind,_value)
			    except Exception,error:
				self.log_error("[Set attr: '%s'| value: %s]{%s}"%(_str_attrToFind,_value,error))				
			else:
			    self.log_error("[Attr not found on masterSettings | attr: '%s'| value: %s]"%(_str_attrToFind,_value))	
		    except Exception,error:
			self.log_error(" mModule: '%s' | %s"%(mModule.getShortName(),error))
		return True
	    except Exception,error:
		self.log_error(error)  
		return False	    	
    return fncWrap(*args,**kws).go()
