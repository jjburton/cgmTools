import copy
import re
import time

import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

# From Maya =============================================================
import maya.cmds as mc

# From Red9 =============================================================
from Red9.core import Red9_Meta as r9Meta
from Red9.core import Red9_CoreUtils as r9Core
from Red9.core import Red9_AnimationUtils as r9Anim

# From cgm ==============================================================
from cgm.core import cgm_General as cgmGeneral
from cgm.core import cgm_Meta as cgmMeta
from cgm.core.rigger import TemplateFactory as tFactory
from cgm.core.rigger import JointFactory as jFactory
from cgm.core.rigger import RigFactory as mRig
from cgm.lib import (modules,curves,distance,attributes)
from cgm.lib.ml import ml_resetChannels

from cgm.core.lib import nameTools
from cgm.core.classes import DraggerContextFactory as dragFactory

from cgm.lib.ml import (ml_breakdownDragger,
                        ml_resetChannels)

##>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Shared libraries
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
_l_moduleStates = ['define','size','template','skeleton','rig']
__l_modulesClasses__ = ['cgmModule','cgmLimb','cgmEyeball','cgmEyelids','cgmEyebrow','cgmMouthNose']
__l_faceModules__ = ['eyebrow','eyelids','eyeball','mouthNose']

#KWS ================================================================================================================
_d_KWARG_mModule = {'kw':'mModule',"default":None,'help':"cgmModule mNode or str name","argType":"cgmModule"}
_d_KWARG_force = {'kw':'force',"default":False,'help':"Whether to force the given function or not","argType":"bool"}
_d_KWARG_excludeSelf = {'kw':'excludeSelf',"default":True,'help':"Whether to exclude self in action","argType":"bool"}   
_d_KWARG_dynSwitchArg = {'kw':'dynSwitchArg',"default":None,'help':"Arg to pass to the dynSwitch ","argType":"int"}   

'''
ml_modules = getModules(self.mi_puppet)
int_lenModules = len(ml_modules)  
_str_module = mModule.p_nameShort	 				
self.progressBar_set(status = "Checking Module: '%s' "%(_str_module),progress = i, maxValue = int_lenModules)
	    
'''
class ModuleFunc(cgmGeneral.cgmFuncCls):
    def __init__(self,*args,**kws):
	"""
	"""	
	try:
	    try:mModule = kws['mModule']
	    except:
		try:mModule = args[0]
		except:pass
	    try:
		assert isModule(mModule)
	    except Exception,error:raise StandardError,"[mModule: %s]{Not a module instance : %s}"%(mModule,error)	
	except Exception,error:raise StandardError,"ModuleFunc failed to initialize | %s"%error
	self._str_funcName= "testFModuleFuncunc"		
	super(ModuleFunc, self).__init__(*args, **kws)
	self._mi_module = mModule	
	self._str_moduleName = mModule.p_nameShort	
	self._l_ARGS_KWS_DEFAULTS = [_d_KWARG_mModule]	
	#=================================================================
	
def exampleWrap(*args,**kws):
    class fncWrap(ModuleFunc):
	def __init__(self,*args,**kws):
	    """
	    """
	    super(fncWrap, self).__init__(*args, **kws)
	    self._str_funcName= "exampleWrap('%s')"%self._str_moduleName
	    self._str_funcHelp = "Fill in this help/nNew line!"
	    #self.l_funcSteps = [{'step':'Gather Info','call':self._gatherInfo_},
	    #self._l_ARGS_KWS_DEFAULTS =  [{'kw':'stateArg',"default":None,'help':"What state is desired","argType":"int/string"}]			    
	    self._l_ARGS_KWS_DEFAULTS = [_d_KWARG_mModule,
	                                 {'kw':'stateArg',"default":None,'help':"What state is desired","argType":"int/string"},
	                                 {'kw':'excludeSelf',"default":True,'help':"Whether to exclude self in return","argType":"bool"}]			    

	    self.__dataBind__(*args,**kws)	    
	    #=================================================================
	    
	def __func__(self):
	    try:#Query ========================================================
		mi_module = self._mi_module
		kws = self.d_kws		
	    except Exception,error:raise StandardError,"[Query]{%s}"%error
	    '''
	    int_lenMax = len(LIST)
	    self.progressBar_set(status = "Remaining to process... ", progress = len(LIST) or i, maxValue = int_lenMax)		    				    		    
	    '''
    return fncWrap(*args,**kws).go()
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Modules
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
def isSized(*args,**kws):
    class fncWrap(ModuleFunc):
	def __init__(self,*args,**kws):
	    """
	    """	
	    super(fncWrap, self).__init__(*args,**kws)
	    self._str_funcName = "isSized('%s')"%self._str_moduleName
	    self.__dataBind__(*args,**kws)
	    #=================================================================
	def __func__(self): 
	    mi_module = self._mi_module
	    try:
		if mi_module.moduleType in __l_faceModules__:
		    if mi_module.getMessage('helper'):
			self.log_debug("%s has size helper, good to go."%self._str_reportStart)	    
			return True
		    else:
			self.log_debug("%s No size helper found."%self._str_reportStart)	
	    except Exception,error:raise StandardError,"[Face check]{%s}"%error
	    
	    handles = mi_module.templateNull.handles
	    i_coreNames = mi_module.coreNames
	    if len(i_coreNames.value) < handles:
		self.log_debug("%s Not enough names for handles"%self._str_reportStart)
		return False
	    if len(i_coreNames.value) > handles:
		self.log_debug("%s Not enough handles for names"%self._str_reportStart)	
		return False
	    if mi_module.templateNull.templateStarterData:
		if len(mi_module.templateNull.templateStarterData) == handles:
		    for i,pos in enumerate(mi_module.templateNull.templateStarterData):
			if not pos:
			    self.log_debug("%s [%s] has no data"%(self._str_reportStart,i))			    
			    return False
		    return True
		else:
		    self.log_debug("%s %i is not == %i handles necessary"%(self._str_reportStart,len(mi_module.templateNull.templateStarterData),handles))			    	    
		    return False
	    else:
		pass
		#self.log_debug("%s No template starter data found"%self._str_reportStart)	
	    return False	 
    return fncWrap(*args,**kws).go() 

def deleteSizeInfo(*args,**kws):
    class fncWrap(ModuleFunc):
	def __init__(self,*args,**kws):
	    """
	    """	
	    super(fncWrap, self).__init__(*args,**kws)
	    self._str_funcName = "deleteSizeInfo('%s')"%self._str_moduleName
	    self.__dataBind__(*args,**kws)
	    #=================================================================
	def __func__(self): 
	    mi_module = self._mi_module
	    mi_module.templateNull.__setattr__('templateStarterData','',lock=True)
	    return True
    return fncWrap(*args,**kws).go() 


def doSize(*args,**kws):
    """ 
    Size a module
    1) Determine what points we need to gather
    2) Initiate draggerContextFactory
    3) Prompt user per point
    4) at the end of the day have a pos list the length of the handle list
    
    @ sizeMode
    'all' - pick every handle position
    'normal' - first/last, if child, will use last position of parent as first
    'manual' - provide a pos list to size from
    
    TODO:
    Add option for other modes
    Add geo argument that can be passed for speed
    Add clamp on value
    Add a way to pull size info from a mirror module
    """    
    class fncWrap(ModuleFunc):
	def __init__(self,*args,**kws):
	    """
	    """
	    super(fncWrap, self).__init__(*args, **kws)
	    self._str_funcName= "doSize('%s')"%self._str_moduleName	
	    self._l_ARGS_KWS_DEFAULTS = [_d_KWARG_mModule,
	                                 {'kw':'sizeMode',"default":'normal','help':"What way we're gonna size","argType":"int/string"},
	                                 {'kw':'geo',"default":[],'help':"List of geo to use","argType":"list"},
	                                 {'kw':'posList',"default":[],'help':"Position list for manual mode ","argType":"list"}]		
	    self.__dataBind__(*args,**kws)	    
	    #=================================================================
	    
	def __func__(self,*args,**kws):
	    """
	    """
	    def updateNames():
		if len(i_coreNames.value) == handles:
		    names = i_coreNames.value
		else:
		    self.log_warning("Not enough names. Generating")
		    names = getGeneratedCoreNames(**kws)
		    
	    mi_module = self._mi_module
	    kws = self.d_kws
	    sizeMode = kws['sizeMode']
	    geo = kws['geo']
	    posList = kws['posList']
	    clickMode = {"heel":"surface"}    
	    i_coreNames = mi_module.coreNames
	    
	    #Gather info
	    #==============      
	    handles = mi_module.templateNull.handles
	    if not geo and not mi_module.getMessage('helper'):
		geo = mi_module.modulePuppet.getGeo()	    
	    self.log_debug("Handles: %s"%handles)
	    self.log_debug("Geo: %s"%geo)
	    self.log_debug("sizeMode: %s"%sizeMode)
	    
	    i_module = mi_module #Bridge holder for our module class to go into our sizer class
	    
	    #Variables
	    #============== 
	    if sizeMode == 'manual':#To allow for a pos list to be input
		if not posList:
		    log.error("Must have posList arg with 'manual' sizeMode!")
		    return False
		int_posList = len(posList)
		if int_posList < handles:
		    self.log_warning("Creating curve to get enough points")                
		    curve = curves.curveFromPosList(posList)
		    mc.rebuildCurve (curve, ch=0, rpo=1, rt=0, end=1, kr=0, kcp=0, kep=1, kt=0,s=(handles-1), d=1, tol=0.001)
		    posList = curves.returnCVsPosList(curve)#Get the pos of the cv's
		    mc.delete(curve) 
		elif int_posList > handles:
		    self.log_warning("Not enough handles for positions. Changing to : %s"%int_posList)
		    handles = int_posList
		    mi_module.templateNull.handles = int_posList
		updateNames()
		mi_module.templateNull.__setattr__('templateStarterData',posList,lock=True)
		self.log_debug("'%s' manually sized!"%self._str_moduleName)
		return True
	    
		    
	    elif sizeMode == 'normal':
		updateNames()
		
		if len(names) > 1:
		    namesToCreate = names[0],names[-1]
		else:
		    namesToCreate = names
		self.log_debug("Names: %s"%names)
	    else:
		namesToCreate = names        
		sizeMode = 'all'
		
	    class moduleSizer(dragFactory.clickMesh):
		"""Sublass to get the functs we need in there"""
		def __init__(self,i_module = mi_module,**kws):
		    if kws:log.info("kws: %s"%str(kws))
		    
		    super(moduleSizer, self).__init__(**kws)
		    self._mi_module = i_module
		    self.toCreate = namesToCreate
		    log.info("Please place '%s'"%self.toCreate[0])
		    
		def release(self):
		    if len(self.l_return)< len(self.toCreate)-1:#If we have a prompt left
			log.info("Please place '%s'"%self.toCreate[len(self.l_return)+1])            
		    dragFactory.clickMesh.release(self)
	
		    
		def finalize(self):
		    log.info("returnList: %s"% self.l_return)
		    log.info("createdList: %s"% self.l_created)   
		    buffer = [] #self._mi_module.templateNull.templateStarterData
		    log.info("starting data: %s"% buffer)
		    
		    #Make sure we have enough points
		    #==============  
		    handles = self._mi_module.templateNull.handles
		    if len(self.l_return) < handles:
			self.log_warning("Creating curve to get enough points")                
			curve = curves.curveFromPosList(self.l_return)
			mc.rebuildCurve (curve, ch=0, rpo=1, rt=0, end=1, kr=0, kcp=0, kep=1, kt=0,s=(handles-1), d=1, tol=0.001)
			self.l_return = curves.returnCVsPosList(curve)#Get the pos of the cv's
			mc.delete(curve)
	
		    #Store info
		    #==============                  
		    for i,p in enumerate(self.l_return):
			buffer.append(p)#need to ensure it's storing properly
			#log.info('[%s,%s]'%(buffer[i],p))
			
		    #Store locs
		    #==============  
		    log.info("finish data: %s"% buffer)
		    self._mi_module.templateNull.__setattr__('templateStarterData',buffer,lock=True)
		    #self._mi_module.templateNull.templateStarterData = buffer#store it
		    log.info("'%s' sized!"%self._str_moduleName)
		    dragFactory.clickMesh.finalize(self)
		
	    #Start up our sizer    
	    return moduleSizer(mode = 'midPoint',
	                       mesh = geo,
	                       create = 'locator',
	                       toCreate = namesToCreate)
    return fncWrap(*args,**kws).go() 
    

def doSetParentModule(*args,**kws):
    class fncWrap(ModuleFunc):
	def __init__(self,*args,**kws):
	    """
	    """	
	    super(fncWrap, self).__init__(*args,**kws)
	    self._str_funcName = "doSetParentModule('%s')"%self._str_moduleName
	    self._l_ARGS_KWS_DEFAULTS = [_d_KWARG_mModule,
	                                 {'kw':'moduleParent',"default":None,'help':"Module parent target","argType":"cgmModule"},
	                                 {'kw':'force',"default":False,'help':"Whether to force things","argType":"bool"}] 			    
	    self.__dataBind__(*args,**kws)
	    #=================================================================
	def __func__(self): 
	    mi_module = self._mi_module
	    kws = self.d_kws
	    moduleParent = self.d_kws['moduleParent']
	    try:
		moduleParent.mNode#See if we have an instance
	    except:
		if mc.objExists(moduleParent):
		    moduleParent = r9Meta.MetaClass(moduleParent)#initialize
		else:
		    self.log_warning("'%s' doesn't exist"%moduleParent)#if it doesn't initialize, nothing is there		
		    return False	
	
	    #Logic checks
	    #==============
	    if not moduleParent.hasAttr('mClass'):
		self.log_warning("'%s' lacks an mClass attr"%module.mNode)	    
		return False
	
	    if moduleParent.mClass not in __l_modulesClasses__:
		self.log_warning("'%s' is not a recognized module type"%moduleParent.mClass)
		return False
	
	    if not moduleParent.hasAttr('moduleChildren'):#Quick check
		self.log_warning("'%s'doesn't have 'moduleChildren' attr"%moduleParent.getShortName())#if it doesn't initialize, nothing is there		
		return False	
	    buffer = copy.copy(moduleParent.getMessage('moduleChildren',False)) or []#Buffer till we have have append functionality	
	    ml_moduleChildren = moduleParent.moduleChildren

	    if mi_module in ml_moduleChildren:
		self.log_warning("already connnected to '%s'"%(moduleParent.getShortName()))
		return
	    else:
		try:#Connect ==========================================================================================
		    buffer.append(mi_module.mNode) #Revist when children has proper add/remove handling
		    moduleParent.moduleChildren = buffer
		    mi_module.moduleParent = moduleParent.mNode
		    self.log_info("parent set to: '%s'!"%moduleParent.getShortName())    
		except Exception,error:raise StandardError,"[Connection]{%s}"%(error)	
	    mi_module.parent = moduleParent.parent
	    return True	 
    return fncWrap(*args,**kws).go() 

def getGeneratedCoreNames(*args,**kws):
    class fncWrap(ModuleFunc):
	def __init__(self,*args,**kws):
	    """
	    """	
	    super(fncWrap, self).__init__(*args,**kws)
	    self._str_funcName = "getGeneratedCoreNames('%s')"%self._str_moduleName			    
	    self.__dataBind__(*args,**kws)
	    #=================================================================
	def __func__(self): 
	    mi_module = self._mi_module
	    kws = self.d_kws
	    mi_coreNamesBuffer = mi_module.coreNames
		
	    ### check the settings first ###
	    partType = mi_module.moduleType
	    self.log_debug("%s partType is %s"%(self._str_moduleName,partType))
	    settingsCoreNames = modules.returncgmTemplateCoreNames(partType)
	    int_handles = mi_module.templateNull.handles
	    partName = nameTools.returnRawGeneratedName(mi_module.mNode,ignore=['cgmType','cgmTypeModifier'])
	
	    ### if there are no names settings, genearate them from name of the limb module###
	    l_generatedNames = []
	    if settingsCoreNames == False: 
		if mi_module.moduleType.lower() == 'eyeball':
		    l_generatedNames.append('%s' % (partName))	    
		else:
		    cnt = 1
		    for handle in range(int_handles):
			l_generatedNames.append('%s%s%i' % (partName,'_',cnt))
			cnt+=1
	    elif int(int_handles) > (len(settingsCoreNames)):
		self.log_debug(" We need to make sure that there are enough core names for handles")       
		cntNeeded = int_handles  - len(settingsCoreNames) +1
		nonSplitEnd = settingsCoreNames[len(settingsCoreNames)-2:]
		toIterate = settingsCoreNames[1]
		iterated = []
		for i in range(cntNeeded):
		    iterated.append('%s%s%i' % (toIterate,'_',(i+1)))
		l_generatedNames.append(settingsCoreNames[0])
		for name in iterated:
		    l_generatedNames.append(name)
		for name in nonSplitEnd:
		    l_generatedNames.append(name) 
	    else:
		l_generatedNames = settingsCoreNames[:mi_module.templateNull.handles]
	    
	    #figure out what to do with the names
	    mi_coreNamesBuffer.value = l_generatedNames
	    return l_generatedNames
    return fncWrap(*args,**kws).go() 

#=====================================================================================================
#>>> Rig
#=====================================================================================================
def puppetSettings_setAttr(*args,**kws):
    class fncWrap(ModuleFunc):
	def __init__(self,*args,**kws):
	    """
	    """
	    super(fncWrap, self).__init__(*args, **kws)
	    self._str_funcName= "settings_toggleTemplateVis('%s')"%self._str_moduleName	
	    self._l_ARGS_KWS_DEFAULTS = [_d_KWARG_mModule,
	                                 cgmMeta._d_KWARG_attr,cgmMeta._d_KWARG_value] 			    
	    self.__dataBind__(*args,**kws)	    
	    #=================================================================
	def __func__(self):
	    """
	    """
	    try:#Query ========================================================
		mi_module = self._mi_module
		_str_basePart = mi_module.getPartNameBase()
		kws = self.d_kws
		_value = self.d_kws['value']
		_attr = self.d_kws['attr']
		mi_masterSettings = mi_module.modulePuppet.masterControl.controlSettings		
	    except Exception,error:raise StandardError,"[Query]{%s}"%error
	    
	    try:#Set
		if mi_masterSettings.hasAttr(_attr):    
		    attributes.doSetAttr(mi_masterSettings.mNode,_attr,_value)
		else:
		    self.log_error("[Attr not found on masterSettings | attr: %s| value: %s]"%(_attr,_value))		    
		    return False
	    except Exception,error:
		self.log_error("[Set attr: %s| value: %s]{%s}"%(_attr,_value,error))
		return False
	    return True
	    

    return fncWrap(*args,**kws).go()


#=====================================================================================================
#>>> Rig
#=====================================================================================================
def doRig(*args,**kws):
    class fncWrap(ModuleFunc):
	def __init__(self,*args,**kws):
	    """
	    """
	    super(fncWrap, self).__init__(*args, **kws)
	    self._str_funcName= "doRig('%s')"%self._str_moduleName	
	    self.__dataBind__(*args,**kws)		    
	    #=================================================================
	def __func__(self):
	    """
	    """
	    try:#Query ========================================================
		mi_module = self._mi_module
		kws = self.d_kws		
	    except Exception,error:raise StandardError,"[Query]{%s}"%error
	    
	    if not isSkeletonized(mi_module):
		self.log_warning("Not skeletonized")
		return False      
	    if mi_module.getMessage('moduleParent') and not isRigged(mi_module.moduleParent):
		self.log_warning("Parent module is not rigged: '%s'"%(mi_module.moduleParent.getShortName()))
		return False 
	    
	    #kws.pop('mModule')
	    mRig.go(**kws)      
	    if not isRigged(**kws):
		self.log_warning("Failed To Rig")
		return False
	    rigConnect(**kws)
    return fncWrap(*args,**kws).go()

def isRigged(*args,**kws):
    """
    Return if a module is rigged or not
    """    
    class fncWrap(ModuleFunc):
	def __init__(self,*args,**kws):
	    """
	    """    
	    super(fncWrap, self).__init__(*args, **kws)
	    self._str_funcName= "isRigged('%s')"%self._str_moduleName	
	    self.__dataBind__(*args,**kws)	
	def __func__(self):
	    kws = self.d_kws
	    mi_module = self._mi_module
	    
	    if not isSkeletonized(**kws):
		self.log_debug("%s Not skeletonized"%self._str_reportStart)
		return False   
	    
	    mi_rigNull = mi_module.rigNull
	    str_shortName = self._str_moduleName
	    
	    ml_rigJoints = mi_rigNull.msgList_get('rigJoints',asMeta = True)
	    l_rigJoints = [i_j.p_nameShort for i_j in ml_rigJoints] or []
	    l_skinJoints = rig_getSkinJoints(mi_module,asMeta=False)
	    
	    if not ml_rigJoints:
		mi_rigNull.version = ''#clear the version	
		return False
	    
	    #See if we can find any constraints on the rig Joints
	    if mi_module.moduleType.lower() in __l_faceModules__:
		self.log_warning("Need to find a better face rig joint test rather than constraints")	    
	    else:
		b_foundConstraint = False
		for i,mJoint in enumerate(ml_rigJoints):
		    if mJoint.getConstraintsTo():
			b_foundConstraint = True
		    elif i == (len(ml_rigJoints) - 1) and not b_foundConstraint:
			self.log_warning("No rig joints are constrained")	    
			return False
		
	    if len( l_skinJoints ) < len( ml_rigJoints ):
		self.log_warning(" %s != %s. Not enough rig joints"%(len(l_skinJoints),len(l_rigJoints)))
		mi_rigNull.version = ''#clear the version        
		return False
	    
	    for attr in ['controlsAll']:
		if not mi_rigNull.msgList_get(attr,asMeta = False):
		    self.log_warning("No data found on '%s'"%(attr))
		    mi_rigNull.version = ''#clear the version            
		    return False    
	    return True	     
    return fncWrap(*args,**kws).go()

def rigDelete(*args,**kws):
    """
    Return if a module is rigged or not
    """    
    class fncWrap(ModuleFunc):
	def __init__(self,*args,**kws):
	    """
	    """    
	    super(fncWrap, self).__init__(*args, **kws)
	    self._str_funcName= "rigDelete('%s')"%self._str_moduleName	
	    self.__dataBind__(*args,**kws)	
	    #=================================================================
	    
	def __func__(self):
	    try:#Query ========================================================
		mi_module = self._mi_module
		kws = self.d_kws		
	    except Exception,error:raise StandardError,"[Query]{%s}"%error
	    
	    #if not isRigged(self):
		#raise StandardError,"moduleFactory.rigDelete('%s')>>>> Module not rigged"%(str_shortName)
	    if isRigConnected(**kws):
		rigDisconnect(**kws)#Disconnect
	    """
	    try:
		objList = returnTemplateObjects(self)
		if objList:
		    mc.delete(objList)
		for obj in self.templateNull.getChildren():
		    mc.delete(obj)
		return True
	    except Exception,error:
		self.log_warning(error)"""
	    mi_rigNull = self._mi_module.rigNull
	    l_rigNullStuff = mi_rigNull.getAllChildren()
	    
	    #Build a control master group List
	    l_masterGroups = []
	    for i_obj in mi_rigNull.msgList_get('controlsAll'):
		if i_obj.hasAttr('masterGroup'):
		    l_masterGroups.append(i_obj.getMessage('masterGroup',False)[0])
		    
	    self.log_debug("masterGroups found: %s"%(l_masterGroups))  
	    for obj in l_masterGroups:
		if mc.objExists(obj):
		    mc.delete(obj)
		    
	    if self._mi_module.getMessage('deformNull'):
		mc.delete(self._mi_module.getMessage('deformNull'))
		
	    mc.delete(mi_rigNull.getChildren())
	    mi_rigNull.version = ''#clear the version
	    return True   
    return fncWrap(*args,**kws).go()

def isRigConnected(*args,**kws):
    class fncWrap(ModuleFunc):
	def __init__(self,*args,**kws):
	    """
	    """
	    super(fncWrap, self).__init__(*args, **kws)
	    self._str_funcName= "isRigConnected('%s')"%self._str_moduleName	
	    self.__dataBind__(*args,**kws)		    	    
	def __func__(self):
	    try:#Query ========================================================
		mi_module = self._mi_module
		kws = self.d_kws
		mi_rigNull = mi_module.rigNull
		ml_rigJoints = mi_rigNull.msgList_get('rigJoints',asMeta = True)
		ml_skinJoints = rig_getSkinJoints(mi_module,asMeta=True)		
	    except Exception,error:raise StandardError,"[Query]{%s}"%error
	    
	    if not isRigged(**kws):
		self.log_debug("Module not rigged")
		return False

	    for i,i_jnt in enumerate(ml_skinJoints):
		try:
		    if not i_jnt.isConstrainedBy(ml_rigJoints[i].mNode):
			self.log_warning("'%s'>>not constraining>>'%s'"%(ml_rigJoints[i].getShortName(),i_jnt.getShortName()))
			return False
		except Exception,error:
		    log.error(error)
		    raise StandardError,"%s Joint failed: %s"%(self._str_reportStart,i_jnt.getShortName())
	    return True
    return fncWrap(*args,**kws).go()

def rigConnect(*args,**kws):
    class fncWrap(ModuleFunc):
	def __init__(self,*args,**kws):
	    """
	    """
	    super(fncWrap, self).__init__(*args, **kws)
	    self._str_funcName= "rigConnect('%s')"%self._str_moduleName	
	    self._l_ARGS_KWS_DEFAULTS = [_d_KWARG_mModule,
	                                 _d_KWARG_force]
	    self.__dataBind__(*args,**kws)		    
	    #=================================================================
	def __func__(self):
	    """
	    """
	    try:#Query ========================================================
		mi_module = self._mi_module
		kws = self.d_kws
		str_shortName = self._str_moduleName
		b_force = kws['force']
	    except Exception,error:raise StandardError,"[Query]{%s}"%error	    
	    
	    if not isRigged(mi_module) and b_force !=True:
		self.log_error("Module not rigged")
		return False
	    if isRigConnected(mi_module):
		self.log_warning("Module already connected")
		return True
	    
	    try:#Query ========================================================
		mi_rigNull = mi_module.rigNull
		ml_rigJoints = mi_rigNull.msgList_get('rigJoints',asMeta = True)
		ml_skinJoints = rig_getSkinJoints(mi_module,asMeta=True)
	    except Exception,error:raise StandardError,"[Gather joint lists]{%s}"%error	    
	    
	    if mi_module.moduleType in __l_faceModules__:
		_b_faceState = True
		mi_faceDeformNull = mi_module.faceDeformNull
	    else:_b_faceState = False

	    if len(ml_skinJoints)!=len(ml_rigJoints):
		raise StandardError,"Rig/Skin joint chain lengths don't match"
	    
	    l_constraints = []
	    int_lenMax = len(ml_skinJoints)
	    for i,i_jnt in enumerate(ml_skinJoints):
		try:
		    _str_joint = i_jnt.p_nameShort
		    self.progressBar_set(status = "Connecting : %s"%_str_joint, progress = i, maxValue = int_lenMax)
		    self.log_debug("'%s'>>drives>>'%s'"%(ml_rigJoints[i].getShortName(),_str_joint))       
		    if _b_faceState:
			#pntConstBuffer = mc.parentConstraint(ml_rigJoints[i].mNode,i_jnt.mNode,maintainOffset=True,weight=1)  
			pntConstBuffer = mc.pointConstraint(ml_rigJoints[i].mNode,i_jnt.mNode,maintainOffset=True,weight=1)        
			orConstBuffer = mc.orientConstraint(ml_rigJoints[i].mNode,i_jnt.mNode,maintainOffset=True,weight=1) 			
			scConstBuffer = mc.scaleConstraint(ml_rigJoints[i].mNode,i_jnt.mNode,maintainOffset=True,weight=1) 
			for str_a in 'xyz':
			    attributes.doConnectAttr('%s.s%s'%(i_jnt.parent,str_a),'%s.offset%s'%(scConstBuffer[0],str_a.capitalize()))			    
			    #attributes.doConnectAttr('%s.s%s'%(mi_faceDeformNull.mNode,str_a),'%s.offset%s'%(scConstBuffer[0],str_a.capitalize()))
		    else:
			pntConstBuffer = mc.pointConstraint(ml_rigJoints[i].mNode,i_jnt.mNode,maintainOffset=True,weight=1)        
			orConstBuffer = mc.orientConstraint(ml_rigJoints[i].mNode,i_jnt.mNode,maintainOffset=True,weight=1) 			
			attributes.doConnectAttr((ml_rigJoints[i].mNode+'.s'),(i_jnt.mNode+'.s'))
		except Exception,error:
		    raise StandardError,"[Joint failed: %s]{%s}"%(_str_joint,error)
	    return True
    return fncWrap(*args,**kws).go()

def rigDisconnect(*args,**kws):
    class fncWrap(ModuleFunc):
	def __init__(self,*args,**kws):
	    """
	    """
	    super(fncWrap, self).__init__(*args, **kws)
	    self._str_funcName= "rigDisconnect('%s')"%self._str_moduleName	
	    
	    self._l_ARGS_KWS_DEFAULTS = [_d_KWARG_mModule,
	                                 {'kw':'FILLIN',"default":None,'help':"FILLIN","argType":"FILLIN"}] 	
	    self.__dataBind__(*args,**kws)	    
	    #=================================================================
	    
	def __func__(self):
	    try:#Query ========================================================
		mi_module = self._mi_module
		kws = self.d_kws		
	    except Exception,error:raise StandardError,"[Query]{%s}"%error	    
	    """
	    if not isRigged(mi_module):
		raise StandardError,"Module not rigged"
	    if not isRigConnected(mi_module):
		raise StandardError,"Module not connected"
	    """
	    if mi_module.moduleType in __l_faceModules__:_b_faceState = True
	    else:_b_faceState = False
	    
	    mc.select(cl=True)
	    mc.select(mi_module.rigNull.msgList_getMessage('controlsAll'))
	    ml_resetChannels.main(transformsOnly = False)
	    
	    mi_rigNull = mi_module.rigNull
	    ml_rigJoints = mi_rigNull.msgList_get('rigJoints') or False
	    ml_skinJoints = mi_rigNull.msgList_get('skinJoints') or False
	    if not ml_skinJoints:raise Exception,"No skin joints found"	    
	    l_constraints = []
	    int_lenMax = len(ml_skinJoints)
	    for i,i_jnt in enumerate(ml_skinJoints):
		_str_joint = i_jnt.p_nameShort
		self.progressBar_set(status = "Disconnecting : %s"%_str_joint, progress = i, maxValue = int_lenMax)		    				    		    		
		try:
		    l_constraints.extend( i_jnt.getConstraintsTo() )
		    if not _b_faceState:attributes.doBreakConnection("%s.scale"%_str_joint)
		except Exception,error:
		    log.error(error)
		    raise StandardError,"Joint failed: %s"%(_str_joint)
	    self.log_debug("constraints found: %s"%(l_constraints))
	    if l_constraints:mc.delete(l_constraints)
	    return True
    return fncWrap(*args,**kws).go()
 
def rig_getReport(self,*args,**kws):    
    mRig.get_report(self,*args,**kws)      
    return True

def rig_getSkinJoints(*args,**kws):
    class fncWrap(ModuleFunc):
	def __init__(self,*args,**kws):
	    """
	    """
	    super(fncWrap, self).__init__(*args, **kws)
	    self._str_funcName= "rig_getSkinJoints('%s')"%self._str_moduleName
	    self._str_funcHelp = "Get the skin joints of a module"
	    self._l_ARGS_KWS_DEFAULTS = [_d_KWARG_mModule,
	                                 cgmMeta._d_KWARG_asMeta]			    

	    self.__dataBind__(*args,**kws)	    
	    #=================================================================
	    
	def __func__(self):
	    try:#Query ========================================================
		mi_module = self._mi_module
		kws = self.d_kws	
		b_asMeta = self.d_kws['asMeta']
	    except Exception,error:raise StandardError,"[Query]{%s}"%error
	    ml_skinJoints = []
	    ml_moduleJoints = mi_module.rigNull.msgList_get('moduleJoints',asMeta = True, cull = True)
	    int_lenMax = len(ml_moduleJoints)	    
	    for i,i_j in enumerate(ml_moduleJoints):
		ml_skinJoints.append(i_j)
		self.progressBar_set(status = "Remaining to process... ", progress = i, maxValue = int_lenMax)		    				    		    		
		for attr in mRig.__l_moduleJointSingleHooks__:
		    str_attrBuffer = i_j.getMessage(attr)
		    if str_attrBuffer:ml_skinJoints.append( cgmMeta.validateObjArg(str_attrBuffer) )
		for attr in mRig.__l_moduleJointMsgListHooks__:
		    l_buffer = i_j.msgList_get(attr,asMeta = b_asMeta,cull = True)
	    if b_asMeta:return ml_skinJoints
	    if ml_skinJoints:
		return [obj.p_nameShort for obj in ml_skinJoints]	    
    return fncWrap(*args,**kws).go()

def rig_getHandleJoints(*args,**kws):
    class fncWrap(ModuleFunc):
	def __init__(self,*args,**kws):
	    """
	    """
	    super(fncWrap, self).__init__(*args, **kws)
	    self._str_funcName= "rig_getHandleJoints('%s')"%self._str_moduleName
	    self._str_funcHelp = "Get handle joints of a module - ex. shoulder/elbow/wrist - no rolls"
	    self._l_ARGS_KWS_DEFAULTS = [_d_KWARG_mModule,
	                                 cgmMeta._d_KWARG_asMeta]			    

	    self.__dataBind__(*args,**kws)	    
	    #=================================================================
	    
	def __func__(self):
	    try:#Query ========================================================
		mi_module = self._mi_module
		kws = self.d_kws	
		b_asMeta = self.d_kws['asMeta']
	    except Exception,error:raise StandardError,"[Query]{%s}"%error
	    return mi_module.rigNull.msgList_get('handleJoints',asMeta = b_asMeta, cull = True)    
    return fncWrap(*args,**kws).go()

def rig_getRigHandleJoints(*args,**kws):
    class fncWrap(ModuleFunc):
	def __init__(self,*args,**kws):
	    """
	    """
	    super(fncWrap, self).__init__(*args, **kws)
	    self._str_funcName= "rig_getRigHandleJoints('%s')"%self._str_moduleName
	    self._str_funcHelp = "Get rig handle joints of a module - ex. shoulder/elbow/wrist - no rolls"
	    self._l_ARGS_KWS_DEFAULTS = [_d_KWARG_mModule,
	                                 cgmMeta._d_KWARG_asMeta]			    

	    self.__dataBind__(*args,**kws)	    
	    #=================================================================
	    
	def __func__(self):
	    try:#Query ========================================================
		mi_module = self._mi_module
		kws = self.d_kws	
		b_asMeta = self.d_kws['asMeta']
	    except Exception,error:raise StandardError,"[Query]{%s}"%error
	    
	    
	    l_rigHandleJoints = []
	    for i_j in mi_module.rigNull.msgList_get('handleJoints'):
		str_attrBuffer = i_j.getMessage('rigJoint')
		if str_attrBuffer:
		    l_rigHandleJoints.append(str_attrBuffer)
		    
	    if b_asMeta:return cgmMeta.validateObjListArg(l_rigHandleJoints,noneValid=True)	    
	    return l_rigHandleJoints	    	    
    return fncWrap(*args,**kws).go()
    
#=====================================================================================================
#>>> Template
#=====================================================================================================
def isTemplated(*args,**kws):
    """
    Return if a module is templated or not
    """    
    class fncWrap(ModuleFunc):
	def __init__(self,*args,**kws):
	    """
	    """
	    super(fncWrap, self).__init__(*args, **kws)
	    self._str_funcName= "isTemplated('%s')"%self._str_moduleName	
	    self.__dataBind__(*args,**kws)	
	    #=================================================================
	def __func__(self):
	    """
	    """
	    try:#Query ========================================================
		mi_module = self._mi_module
		kws = self.d_kws		
	    except Exception,error:raise StandardError,"[Query]{%s}"%error
	    
	    if mi_module.moduleType in __l_faceModules__:
		if mi_module.getMessage('helper'):
		    self.log_debug("%s has size helper, good to go."%self._str_reportStart)	    
		    return True
		
	    coreNamesValue = mi_module.coreNames.value
	    if not coreNamesValue:
		self.log_debug("No core names found")
		return False
	    if not mi_module.getMessage('templateNull'):
		self.log_debug("No template null")
		return False       
	    if not mi_module.templateNull.getChildren():
		self.log_debug("No children found in template null")
		return False   
	    if not mi_module.getMessage('modulePuppet'):
		self.log_debug("No modulePuppet found")
		return False   	
	    if not mi_module.modulePuppet.getMessage('masterControl'):
		self.log_debug("No masterControl")
		return False
		
	    if mi_module.mClass in ['cgmModule','cgmLimb']:
		#Check our msgList attrs
		#=====================================================================================
		ml_controlObjects = mi_module.templateNull.msgList_get('controlObjects')
		for attr in 'controlObjects','orientHelpers':
		    if not mi_module.templateNull.msgList_getMessage(attr):
			self.log_warning("No data found on '%s'"%attr)
			return False        
		
		#Check the others
		for attr in 'root','curve','orientRootHelper':
		    if not mi_module.templateNull.getMessage(attr):
			if attr == 'orientHelpers' and len(controlObjects)==1:
			    pass
			else:
			    self.log_warning("No data found on '%s'"%attr)
			    return False    
		    
		if len(coreNamesValue) != len(ml_controlObjects):
		    self.log_debug("Not enough handles.")
		    return False    
		    
		if len(ml_controlObjects)>1:
		    for i_obj in ml_controlObjects:#check for helpers
			if not i_obj.getMessage('helper'):
			    self.log_debug("'%s' missing it's helper"%i_obj.getShortName())
			    return False
		return True    
    return fncWrap(*args,**kws).go()

def doTemplate(*args,**kws):
    class fncWrap(ModuleFunc):
	def __init__(self,*args,**kws):
	    """
	    """
	    super(fncWrap, self).__init__(*args, **kws)
	    self._str_funcName= "doTemplate('%s')"%self._str_moduleName	
	    self.__dataBind__(*args,**kws)	
	    #=================================================================
	    
	def __func__(self,**kws):
	    try:#Query ========================================================
		mi_module = self._mi_module
		kws = self.d_kws		
	    except Exception,error:raise StandardError,"[Query]{%s}"%error
	    
	    if isTemplated(**kws):
		return True
	    if not isSized(**kws):
		self.log_warning("Not sized")
		return False    
	    tFactory.go(**kws)      
	    if not isTemplated(**kws):
		self.log_warning("Template failed")
		return False
	    return True  
    return fncWrap(*args,**kws).go()

def deleteTemplate(*args,**kws):
    class fncWrap(ModuleFunc):
	def __init__(self,*args,**kws):
	    """
	    """
	    super(fncWrap, self).__init__(*args, **kws)
	    self._str_funcName= "deleteTemplate('%s')"%self._str_moduleName	
	    self.__dataBind__(*args,**kws)		    
	    #=================================================================
	def __func__(self,**kws):
	    try:#Query ========================================================
		mi_module = self._mi_module
		kws = self.d_kws		
	    except Exception,error:raise StandardError,"[Query]{%s}"%error
	    
	    objList = returnTemplateObjects(**kws)
	    if objList:
		mc.delete(objList)
	    for obj in mi_module.templateNull.getChildren():
		mc.delete(obj)
	    return True	    
    return fncWrap(*args,**kws).go()

def returnTemplateObjects(*args,**kws):
    class fncWrap(ModuleFunc):
	def __init__(self,*args,**kws):
	    """
	    """
	    super(fncWrap, self).__init__(*args, **kws)
	    self._str_funcName= "returnTemplateObjects('%s')"%self._str_moduleName	
	    self.__dataBind__(*args,**kws)		    
	    #=================================================================
	def __func__(self,*args,**kws):
	    try:#Query ========================================================
		mi_module = self._mi_module
	    except Exception,error:raise StandardError,"[Query]{%s}"%error
	    
	    templateNull = mi_module.templateNull.getShortName()
	    returnList = []
	    for obj in mc.ls(type = 'transform'):
		if attributes.doGetAttr(obj,'templateOwner') == templateNull:
		    returnList.append(obj)
	    return returnList
    return fncWrap(*args,**kws).go()
#=====================================================================================================
#>>> Skeleton
#=====================================================================================================
def get_rollJointCountList(*args,**kws):
    class fncWrap(ModuleFunc):
	def __init__(self,*args,**kws):
	    """
	    """
	    super(fncWrap, self).__init__(*args, **kws)
	    self._str_funcName= "get_rollJointCountList('%s')"%self._str_moduleName	
	    self.__dataBind__(*args,**kws)		    
	    #=================================================================
	def __func__(self,*args,**kws):
	    try:#Query ========================================================
		mi_module = self._mi_module
		kws = self.d_kws		
	    except Exception,error:raise StandardError,"[Query]{%s}"%error
	    
	    int_rollJoints = mi_module.templateNull.rollJoints
	    d_rollJointOverride = mi_module.templateNull.rollOverride
	    if type(d_rollJointOverride) is not dict:d_rollJointOverride = {}
	    
	    l_segmentRollCount = [int_rollJoints for i in range(mi_module.templateNull.handles-1)]
		
	    if d_rollJointOverride:
		for k in d_rollJointOverride.keys():
		    try:
			l_segmentRollCount[int(k)]#If the arg passes
			l_segmentRollCount[int(k)] = d_rollJointOverride.get(k)#Override the roll value
		    except:self.log_warning("%s:%s rollOverride arg failed"%(k,d_rollJointOverride.get(k)))
	    self.log_debug("%s"%(l_segmentRollCount))
	    return l_segmentRollCount
    return fncWrap(*args,**kws).go()

def isSkeletonized(*args,**kws):
    """
    Return if a module is skeletonized or not
    """    
    class fncWrap(ModuleFunc):
	def __init__(self,*args,**kws):
	    """
	    """
	    super(fncWrap, self).__init__(*args, **kws)
	    self._str_funcName= "isSkeletonized('%s')"%self._str_moduleName	
	    self.__dataBind__(*args,**kws)		    
	    #=================================================================
	def __func__(self,*args,**kws):
	    try:#Query ========================================================
		mi_module = self._mi_module
		kws = self.d_kws		
	    except Exception,error:raise StandardError,"[Query]{%s}"%error
	    
	    l_moduleJoints = mi_module.rigNull.msgList_get('moduleJoints',asMeta=False)
	    if not l_moduleJoints:
		self.log_debug("No skin joints found")
		return False  
	    
	    #>>> How many joints should we have 
	    goodCount = returnExpectedJointCount(*args,**kws)
	    currentCount = len(l_moduleJoints)
	    if  currentCount < (goodCount-1):
		self.log_warning("Expected at least %s joints. %s found"%(goodCount-1,currentCount))
		return False
	    return True
    return fncWrap(*args,**kws).go()

def doSkeletonize(*args,**kws):
    class fncWrap(ModuleFunc):
	def __init__(self,*args,**kws):
	    """
	    """
	    super(fncWrap, self).__init__(*args, **kws)
	    self._str_funcName= "doSkeletonize('%s')"%self._str_moduleName	
	    self.__dataBind__(*args,**kws)	
	    #=================================================================
	def __func__(self,**kws):
	    try:#Query ========================================================
		mi_module = self._mi_module
		kws = self.d_kws		
	    except Exception,error:raise StandardError,"[Query]{%s}"%error
	    
	    if not isTemplated(**kws):
		self.log_warning("Not templated, can't skeletonize")
		return False      
	    jFactory.go(**kws)      
	    if not isSkeletonized(**kws):
		self.log_warning("Skeleton build failed")
		return False
	    return True
    return fncWrap(*args,**kws).go()

def deleteSkeleton(*args,**kws):
    class fncWrap(ModuleFunc):
	def __init__(self,*args,**kws):
	    """
	    """
	    super(fncWrap, self).__init__(*args, **kws)
	    self._str_funcName= "deleteSkeleton('%s')"%self._str_moduleName
	    self._l_ARGS_KWS_DEFAULTS =  [_d_KWARG_mModule]			    	    
	    self.__dataBind__(*args,**kws)		    
	    #=================================================================
	def __func__(self):
	    try:#Query ========================================================
		mi_module = self._mi_module
		kws = self.d_kws		
	    except Exception,error:raise StandardError,"[Query]{%s}"%error
	    if not isSkeletonized(**kws):
		self.log_warning("Not skeletonized. Cannot delete skeleton")		
		return False
	    jFactory.deleteSkeleton(**kws)
	    return True
    return fncWrap(*args,**kws).go()

def returnExpectedJointCount(*args,**kws):
    """
    Function to figure out how many joints we should have on a module for the purpose of isSkeletonized check
    """    
    class fncWrap(ModuleFunc):
	def __init__(self,*args,**kws):
	    """
	    """
	    super(fncWrap, self).__init__(*args, **kws)
	    self._str_funcName= "returnExpectedJointCount('%s')"%self._str_moduleName	
	    self.__dataBind__(*args,**kws)		    
	    #=================================================================
	def __func__(self,*args,**kws):
	    try:#Query ========================================================
		mi_module = self._mi_module
		kws = self.d_kws		
	    except Exception,error:raise StandardError,"[Query]{%s}"%error
	    
	    handles = mi_module.templateNull.handles
	    if handles == 0:
		self.log_warning("Can't count expected joints. 0 handles: '%s'")
		return False
	    
	    if mi_module.templateNull.getAttr('rollJoints'):
		rollJoints = mi_module.templateNull.rollJoints 
		d_rollJointOverride = mi_module.templateNull.rollOverride 
		
		l_spanDivs = []
		for i in range(0,handles-1):
		    l_spanDivs.append(rollJoints)    
		self.log_debug("l_spanDivs before append: %s"%l_spanDivs)
	    
		if type(d_rollJointOverride) is dict:
		    for k in d_rollJointOverride.keys():
			try:
			    l_spanDivs[int(k)]#If the arg passes
			    l_spanDivs[int(k)] = d_rollJointOverride.get(k)#Override the roll value
			except:self.log_warning("%s:%s rollOverride arg failed"%(k,d_rollJointOverride.get(k)))    
		self.log_debug("l_spanDivs: %s"%l_spanDivs)
		int_count = 0
		for i,n in enumerate(l_spanDivs):
		    int_count +=1
		    int_count +=n
		int_count+=1#add the last handle back
		return int_count
	    else:
		return mi_module.templateNull.handles
    return fncWrap(*args,**kws).go()

#=====================================================================================================
#>>> States
#=====================================================================================================   
def validateStateArg(*args,**kws):
    class fncWrap(cgmGeneral.cgmFuncCls):
	def __init__(self,*args,**kws):
	    """
	    """
	    super(fncWrap, self).__init__(*args, **kws)
	    self._str_funcName= "validateStateArg"	
	    self._l_ARGS_KWS_DEFAULTS = [{'kw':'stateArg',"default":None,'help':"Needs to be a valid cgm module state","argType":"string/int"}] 	
	    self.__dataBind__(*args,**kws)		    
	    #=================================================================
	    
	def __func__(self,*args,**kws):
	    try:#Query ========================================================
		kws = self.d_kws		
	    except Exception,error:raise StandardError,"[Query]{%s}"%error	    
	    stateArg = self.d_kws['stateArg']
	    
	    #>>> Validate argument
	    if type(stateArg) in [str,unicode]:
		stateArg = stateArg.lower()
		if stateArg in _l_moduleStates:
		    stateIndex = _l_moduleStates.index(stateArg)
		    stateName = stateArg
		else:
		    self.log_warning("Bad stateArg: %s"%stateArg)
		    self.log_info("Valid args: %s"%_l_moduleStates)				    
		    return False
	    elif type(stateArg) is int:
		if stateArg<= len(_l_moduleStates)-1:
		    stateIndex = stateArg
		    stateName = _l_moduleStates[stateArg]         
		else:
		    self.log_warning("Bad stateArg: %s"%stateArg)
		    self.log_info("Valid args: %s"%_l_moduleStates)
		    return False        
	    else:
		self.log_warning("Bad stateArg: %s"%stateArg)
		self.log_info("Valid args: %s"%_l_moduleStates)		
		return False
	    return [stateIndex,stateName] 
    return fncWrap(*args,**kws).go()   

def isModule(*args,**kws):
    class fncWrap(cgmGeneral.cgmFuncCls):
	def __init__(self,*args,**kws):
	    super(fncWrap, self).__init__(*args,**kws)
	    self._str_funcHelp = "Simple module check"	
	    self._str_funcName = "isModule"
	    self._l_ARGS_KWS_DEFAULTS = [_d_KWARG_mModule]	    
	    self.__dataBind__(*args,**kws)
	    self.l_funcSteps = [{'step':'Gather Info','call':self._query_},
	                        {'step':'process','call':self._process_}]

	def _query_(self):
	    try:self._str_moduleName = self.d_kws['mModule'].p_nameShort	
	    except:raise StandardError,"[mi_module : %s]{Not an cgmNode, can't be a module!} "%(self.d_kws['mModule'])
	    self._str_funcName = "isModule('%s')"%self._str_moduleName	
	    self.__updateFuncStrings__()
	    
	def _process_(self):
	    mi_module = self.d_kws['mModule']
	    if not mi_module.hasAttr('mClass'):
		self.log_error("Has no 'mClass'")
		return False
	    if mi_module.mClass not in __l_modulesClasses__:
		self.log_error("Class not a known module type: '%s'"%mi_module.mClass)
		return False  
	    return True
    return fncWrap(*args,**kws).go()

def getState(*args,**kws):
    """ 
    Check module state ONLY from the state check attributes
    
    RETURNS:
    state(int) -- indexed to ModuleFactory._l_moduleStates
    
    Possible states:
    define
    sized
    templated
    skeletonized
    rigged
    """    
    class fncWrap(ModuleFunc):
	def __init__(self,*args,**kws):
	    """
	    """
	    super(fncWrap, self).__init__(*args, **kws)
	    self._str_funcName= "getState('%s')"%self._str_moduleName	
	    self.__dataBind__(*args,**kws)		    
	    #=================================================================
	def __func__(self):
	    try:#Query ========================================================
		mi_module = self._mi_module
		kws = self.d_kws		
	    except Exception,error:raise StandardError,"[Query]{%s}"%error
	    d_CheckList = {'size':isSized,
	                   'template':isTemplated,
	                   'skeleton':isSkeletonized,
	                   'rig':isRigged,
	                   }
	    goodState = 0
	    _l_moduleStatesReverse = copy.copy(_l_moduleStates)
	    _l_moduleStatesReverse.reverse()
	    for i,state in enumerate(_l_moduleStatesReverse):
		self.log_debug("Checking: %s"%state)	
		if state in d_CheckList.keys():
		    if d_CheckList[state](**kws):
			self.log_debug("good: %s"%state)
			goodState = _l_moduleStates.index(state)
			break
		else:
		    goodState = 0
	    self.log_debug("'%s' state: %s | '%s'"%(self._str_moduleName,goodState,_l_moduleStates[goodState]))
	    return goodState
    return fncWrap(*args,**kws).go()

def setState(*args,**kws):
    """ 
    Set a module's state
    
    @rebuild -- force it to rebuild each step
    TODO:
    Make template info be stored when leaving
    """    
    class fncWrap(ModuleFunc):
	def __init__(self,*args,**kws):
	    """
	    """
	    super(fncWrap, self).__init__(*args, **kws)
	    self._str_funcName= "setState('%s')"%self._str_moduleName	
	    
	    self._l_ARGS_KWS_DEFAULTS = [_d_KWARG_mModule,
	                                 {'kw':'stateArg',"default":None,'help':"What state is desired","argType":"int/string"},
	                                 {'kw':'rebuildFrom',"default":None,'help':"State to rebuild from","argType":"int/string"}] 		
	    self.__dataBind__(*args,**kws)		    
	    #=================================================================
	def __func__(self,*args,**kws):
	    """
	    """
	    self.log_warning("<<<<<<<< This module needs to be updated")
	    try:#Query ========================================================
		mi_module = self._mi_module
		kws = self.d_kws
		rebuildFrom = kws['rebuildFrom']		
	    except Exception,error:raise StandardError,"[Query]{%s}"%error
	    
	    if rebuildFrom is not None:
		rebuildArgs = validateStateArg(rebuildFrom,**kws)
		if rebuildArgs:
		    self.log_info("'%s' rebuilding from: '%s'"%(self._str_moduleName,rebuildArgs[1]))
		    changeState(self._mi_module,rebuildArgs[1],**kws)
	    changeState(**kws)	
	    return True
    return fncWrap(*args,**kws).go()

def checkState(*args,**kws):
    class fncWrap(ModuleFunc):
	def __init__(self,*args,**kws):
	    """
	    """
	    super(fncWrap, self).__init__(*args, **kws)
	    self._str_funcName = "checkState('%s')"%self._str_moduleName	
	    self._str_funcHelp = "Checks if a module has the arg state.\nIf not, it goes to it. If so, it returns True"		    
	    self._l_ARGS_KWS_DEFAULTS =  [_d_KWARG_mModule,
	                                  {'kw':'stateArg',"default":None,'help':"What state is desired","argType":"int/string"}]		
	    self.__dataBind__(*args,**kws)		    
	    #=================================================================    
	def __func__(self,*args,**kws):
	    """
	    """
	    try:#Query ========================================================
		mi_module = self._mi_module
		kws = self.d_kws		
	    except Exception,error:raise StandardError,"[Query]{%s}"%error
	    stateArg = kws['stateArg']
	    
	    l_stateArg = validateStateArg(stateArg)
	    if not l_stateArg:raise StandardError,"Couldn't find valid state"
	    
	    if getState(*args,**kws) >= l_stateArg[0]:
		self.log_debug("State is good")
		return True
	    
	    self.log_debug("Have to change state")
	    changeState(stateArg,*args,**kws)
	    return False
    return fncWrap(*args,**kws).go()
    
def changeState(*args,**kws):
    """ 
    Changes a module state
    
    TODO:
    Make template info be stored skeleton builds
    Make template builder read and use pose data stored
    """    
    class fncWrap(ModuleFunc):
	def __init__(self,*args,**kws):
	    """
	    """
	    super(fncWrap, self).__init__(*args, **kws)
	    self._str_funcName= "changeState('%s')"%self._str_moduleName	
	    
	    self._l_ARGS_KWS_DEFAULTS = [_d_KWARG_mModule,
	                                 {'kw':'stateArg',"default":None,'help':"What state is desired","argType":"int/string"},
	                                 {'kw':'rebuildFrom',"default":None,'help':"State to rebuild from","argType":"int/string"},
	                                 cgmMeta._d_KWARG_forceNew]		
	    self.__dataBind__(*args,**kws)	    
	    #=================================================================
	    self.log_warning("<<<<<<<< This module needs to be updated")
	    
	def __func__(self,*args,**kws):
	    """
	    """
	    try:#Query ========================================================
		mi_module = self._mi_module
		kws = self.d_kws		
	    except Exception,error:raise StandardError,"[Query]{%s}"%error
	    stateArg = kws['stateArg']
	    rebuildFrom = kws['rebuildFrom']
	    forceNew = kws['forceNew']
    
	    d_upStateFunctions = {'size':doSize,
		                   'template':doTemplate,
		                   'skeleton':doSkeletonize,
		                   'rig':doRig,
		                   }
	    d_downStateFunctions = {'define':deleteSizeInfo,
		                    'size':deleteTemplate,
		                    'template':deleteSkeleton,
		                    'skeleton':rigDelete,
		                    }
	    d_deleteStateFunctions = {'size':deleteSizeInfo,
		                      'template':deleteTemplate,#handle from factory now
		                      'skeleton':deleteSkeleton,
		                      'rig':rigDelete,
		                      }    

	    stateArgs = validateStateArg(stateArg,**kws)
	    if not stateArgs:
		self.log_warning("Bad stateArg from changeState: %s"%stateArg)
		return False
	    
	    stateIndex = stateArgs[0]
	    stateName = stateArgs[1]
	    
	    self.log_debug("stateIndex: %s | stateName: '%s'"%(stateIndex,stateName))
	    
	    #>>> Meat
	    #========================================================================
	    currentState = getState(*args,**kws) 
	    if currentState == stateIndex and rebuildFrom is None and not forceNew:
		if not forceNew:self.log_warning("'%s' already has state: %s"%(self._str_moduleName,stateName))
		return True
	    #If we're here, we're going to move through the set states till we get to our spot
	    self.log_debug("Changing states now...")
	    if stateIndex > currentState:
		startState = currentState+1        
		self.log_debug(' up stating...')        
		self.log_debug("Starting doState: '%s'"%_l_moduleStates[startState])
		doStates = _l_moduleStates[startState:stateIndex+1]
		self.log_debug("doStates: %s"%doStates)        
		for doState in doStates:
		    if doState in d_upStateFunctions.keys():
			if not d_upStateFunctions[doState](self._mi_module,*args,**kws):return False
			else:
			    self.log_debug("'%s' completed: %s"%(self._str_moduleName,doState))
		    else:
			self.log_warning("No up state function for: %s"%doState)
	    elif stateIndex < currentState:#Going down
		self.log_debug('down stating...')        
		l_reverseModuleStates = copy.copy(_l_moduleStates)
		l_reverseModuleStates.reverse()
		startState = currentState      
		#self.log_debug("l_reverseModuleStates: %s"%l_reverseModuleStates)
		self.log_debug("Starting downState: '%s'"%_l_moduleStates[startState])
		rev_start = l_reverseModuleStates.index( _l_moduleStates[startState] )+1
		rev_end = l_reverseModuleStates.index( _l_moduleStates[stateIndex] )+1
		doStates = l_reverseModuleStates[rev_start:rev_end]
		self.log_debug("toDo: %s"%doStates)
		for doState in doStates:
		    self.log_debug("doState: %s"%doState)
		    if doState in d_downStateFunctions.keys():
			if not d_downStateFunctions[doState](self._mi_module,*args,**kws):return False
			else:self.log_debug("'%s': %s"%(self._str_moduleName,doState))
		    else:
			self.log_warning("No down state function for: %s"%doState)  
	    else:
		self.log_debug('Forcing recreate')
		if stateName in d_upStateFunctions.keys():
		    if not d_upStateFunctions[stateName](self._mi_module,*args,**kws):return False
		    return True	    
    return fncWrap(*args,**kws).go()

def storePose_templateSettings(*args,**kws):
    class fncWrap(ModuleFunc):
	def __init__(self,*args,**kws):
	    """
	    """
	    super(fncWrap, self).__init__(*args, **kws)
	    self._str_funcHelp = "Builds a template's data settings for reconstruction./nexampleDict = {'root':{'test':[0,1,0]},/n'controlObjects':{0:[1,1,1]}}"
	    self._str_funcName= "storePose_templateSettings('%s')"%self._str_moduleName	
	    #self.l_funcSteps = [{'step':'Gather Info','call':self._gatherInfo_},	
	    self.__dataBind__(*args,**kws)	    
	    #=================================================================
	def buildDict_AnimAttrsOfObject(self, node,ignore = ['visibility']):
	    attrDict = {}
	    attrs = r9Anim.getSettableChannels(node,incStatics=True)
	    if attrs:
		for attr in attrs:
		    if attr not in ignore:
			try:attrDict[attr]=mc.getAttr('%s.%s' % (node,attr))
			except:mi_module.log_debug('%s : attr is invalid in this instance' % attr)
	    return attrDict
	
	def __func__(self):
	    """
	    """
	    try:#Query ========================================================
		mi_module = self._mi_module
		kws = self.d_kws		
	    except Exception,error:raise StandardError,"[Query]{%s}"%error
	    if mi_module.getMessage('helper'):
		self.log_warning("Cannot currently store pose with rigBlocks")
		return False

	    exampleDict = {'root':{'test':[0,1,0]},
		           'orientRootHelper':{'test':[0,1,0]},
		           'controlObjects':{0:[1,1,1]},
		           'helperObjects':{0:[]}}    
	    try:
		poseDict = {}
		mi_templateNull = mi_module.templateNull
		mi_templateNull.addAttr('controlObjectTemplatePose',attrType = 'string')#make sure attr exists
		#>>> Get the root
		poseDict['root'] = self.buildDict_AnimAttrsOfObject(mi_templateNull.getMessage('root')[0])
		poseDict['orientRootHelper'] = self.buildDict_AnimAttrsOfObject(mi_templateNull.getMessage('orientRootHelper')[0])
		poseDict['controlObjects'] = {}
		poseDict['helperObjects'] = {}
		
		for i,i_node in enumerate(mi_templateNull.controlObjects):
		    poseDict['controlObjects'][str(i)] = self.buildDict_AnimAttrsOfObject(i_node.mNode)
		    if i_node.getMessage('helper'):
			poseDict['helperObjects'][str(i)] = self.buildDict_AnimAttrsOfObject(i_node.helper.mNode)
		
		#Store it        
		mi_templateNull.controlObjectTemplatePose = poseDict
		return poseDict
	    except Exception,error:raise StandardError,"[Posr store]{%s}"%(error)   
	    
    return fncWrap(*args,**kws).go()

def readPose_templateSettings(*args,**kws):
    class fncWrap(ModuleFunc):
	def __init__(self,*args,**kws):
	    """
	    """
	    super(fncWrap, self).__init__(*args, **kws)
	    self._str_funcHelp = "Reads and applies template settings pose data"
	    self._str_funcName= "readPose_templateSettings('%s')"%self._str_moduleName	
	    #self.l_funcSteps = [{'step':'Gather Info','call':self._gatherInfo_},	
	    self.__dataBind__(*args,**kws)	    
	    #=================================================================
	
	def __func__(self):
	    """
	    """
	    try:#Query ========================================================
		mi_module = self._mi_module
		kws = self.d_kws
		mi_templateNull = mi_module.templateNull   
		d_pose = mi_templateNull.controlObjectTemplatePose
	    except Exception,error:raise StandardError,"[Query]{%s}"%error
	    
	    
	    if type(d_pose) is not dict:
		return False
	    
	    #>>> Get the root
	    for key in ['root','orientRootHelper']:
		if d_pose[key]:
		    for attr, val in d_pose[key].items():
			try:
			    val=eval(val)
			except:pass      
			try:
			    mc.setAttr('%s.%s' % (mi_templateNull.getMessage(key)[0],attr), val)
			except Exception,err:
			    self.log_error(err)   
			    
	    for key in d_pose['controlObjects']:
		for attr, val in d_pose['controlObjects'][key].items():
		    try:
			val=eval(val)
		    except:pass      
		
		    try:
			mc.setAttr('%s.%s' % (mi_templateNull.getMessage('controlObjects')[int(key)], attr), val)
		    except Exception,err:
			self.log_error(err) 
			
	    for key in d_pose['helperObjects']:
		for attr, val in d_pose['helperObjects'][key].items():
		    try:
			val=eval(val)
		    except:pass      
		    try:
			if mi_templateNull.controlObjects[int(key)].getMessage('helper'):
			    mi_module.log_debug(mi_templateNull.controlObjects[int(key)].getMessage('helper')[0])
			    mc.setAttr('%s.%s' % (mi_templateNull.controlObjects[int(key)].getMessage('helper')[0], attr), val)
		    except Exception,err:
			self.log_error(err)    
	    return True
    return fncWrap(*args,**kws).go()
  
    
#=====================================================================================================
#>>> Anim functions functions
#=====================================================================================================
def get_mirror(*args,**kws):
    class fncWrap(ModuleFunc):
	def __init__(self,*args,**kws):
	    """
	    """	
	    super(fncWrap, self).__init__(*args,**kws)
	    self._str_funcName = "get_mirror('%s')"%self._str_moduleName
	    self.__dataBind__(*args,**kws)
	    self.l_funcSteps = [{'step':'Process','call':self.__func__}]
	    #The idea is to register the functions needed to be called
	    #=================================================================
	def __func__(self): 
	    try:#Query ========================================================
		mi_module = self._mi_module
		kws = self.d_kws		
	    except Exception,error:raise StandardError,"[Query]{%s}"%error
	    l_direction = ['left','right']
	    if mi_module.getAttr('cgmDirection') not in l_direction:
		self.log_debug("Module doesn't have direction")
		return False
	    int_direction = l_direction.index(mi_module.cgmDirection)
	    d = {'cgmName':mi_module.cgmName,'moduleType':mi_module.moduleType,'cgmDirection':l_direction[not int_direction]}
	    self.log_debug("checkDict = %s"%d)
	    return mi_module.modulePuppet.getModuleFromDict(checkDict = d,**kws)	 
    return fncWrap(*args,**kws).go()  

def animReset(*args,**kws):
    class fncWrap(ModuleFunc):
	def __init__(self,*args,**kws):
	    """
	    """
	    super(fncWrap, self).__init__(*args, **kws)
	    self._str_funcName= "animReset('%s')"%self._str_moduleName	
	    self._l_ARGS_KWS_DEFAULTS =  [_d_KWARG_mModule,
	                                  {'kw':'transformsOnly',"default":True,'help':"Whether to only reset transforms","argType":"bool"}]			    
	    self.__dataBind__(*args,**kws)	    	    
	def __func__(self):
	    try:#Query ========================================================
		mi_module = self._mi_module
		kws = self.d_kws		
	    except Exception,error:raise StandardError,"[Query]{%s}"%error
	    mi_module.rigNull.moduleSet.select()
	    if mc.ls(sl=True):
		ml_resetChannels.main(transformsOnly = kws['transformsOnly'])
		return True
	    return False	    
    return fncWrap(*args,**kws).go()

def mirrorPush(*args,**kws):
    class fncWrap(ModuleFunc):
	def __init__(self,*args,**kws):
	    """
	    """	
	    super(fncWrap, self).__init__(*args,**kws)
	    self._str_funcName = "mirrorPush('%s')"%self._str_moduleName
	    self._l_ARGS_KWS_DEFAULTS =  [_d_KWARG_mModule]
	    self.l_funcSteps = [{'step':'Process','call':self.__func__}]	    
	    self.__dataBind__(*args,**kws)
	    #=================================================================
	def __func__(self): 
	    try:#Query ========================================================
		mi_module = self._mi_module
		kws = self.d_kws		
	    except Exception,error:raise StandardError,"[Query]{%s}"%error
	    l_buffer = mi_module.rigNull.moduleSet.getList()
	    mi_mirror = get_mirror(**kws)
	    if mi_mirror:
		l_buffer.extend(mi_mirror.rigNull.moduleSet.getList())
	    else:raise StandardError, "Module doesn't have mirror"
	    
	    if l_buffer:
		r9Anim.MirrorHierarchy(l_buffer).makeSymmetrical(mode = '',primeAxis = mi_module.cgmDirection.capitalize() )
		mc.select(l_buffer)
		return True
	    return False	 
	
    return fncWrap(*args,**kws).go()   
        
def mirrorPull(*args,**kws):
    class fncWrap(ModuleFunc):
	def __init__(self,*args,**kws):
	    """
	    """	
	    super(fncWrap, self).__init__(*args,**kws)
	    self._str_funcName = "mirrorPull('%s')"%self._str_moduleName
	    self._l_ARGS_KWS_DEFAULTS =  [_d_KWARG_mModule]
	    self.__dataBind__(*args,**kws)

	def __func__(self): 
	    try:#Query ========================================================
		mi_module = self._mi_module
		kws = self.d_kws		
	    except Exception,error:raise StandardError,"[Query]{%s}"%error
	    
	    l_buffer = mi_module.rigNull.moduleSet.getList()
	    mi_mirror = get_mirror(**kws)
	    if mi_mirror:
		l_buffer.extend(mi_mirror.rigNull.moduleSet.getList())
	    else:raise StandardError, "Module doesn't have mirror"
	    
	    if l_buffer:
		r9Anim.MirrorHierarchy(l_buffer).makeSymmetrical(mode = '',primeAxis = mi_mirror.cgmDirection.capitalize() )
		mc.select(l_buffer)
		return True
	    return False	 
    return fncWrap(*args,**kws).go()
     
def mirrorMe(*args,**kws):
    class fncWrap(ModuleFunc):
	def __init__(self,*args,**kws):
	    """
	    """	
	    super(fncWrap, self).__init__(*args,**kws)
	    self._str_funcName = "mirrorMe('%s')"%self._str_moduleName
	    self.__dataBind__(*args,**kws)
	def __func__(self): 
	    try:#Query ========================================================
		mi_module = self._mi_module
		kws = self.d_kws		
	    except Exception,error:raise StandardError,"[Query]{%s}"%error
	    
	    l_buffer = mi_module.rigNull.moduleSet.getList()
	    try:mi_mirror = get_mirror(**kws)
	    except Exception,error:raise StandardError,"get_mirror | %s"%error
	    if mi_mirror:
		l_buffer.extend(mi_mirror.rigNull.moduleSet.getList())
	    if l_buffer:
		r9Anim.MirrorHierarchy(l_buffer).mirrorData(mode = '')
		mc.select(l_buffer)
		return True
	    return False  
	
    return fncWrap(*args,**kws).go()

def mirrorSymLeft(*args,**kws):
    class fncWrap(ModuleFunc):
	def __init__(self,*args,**kws):
	    """
	    """	
	    super(fncWrap, self).__init__(*args,**kws)
	    self._str_funcName = "mirrorSymLeft('%s')"%self._str_moduleName
	    self.__dataBind__(*args,**kws)
	    #=================================================================
	def __func__(self): 
	    try:#Query ========================================================
		mi_module = self._mi_module
		kws = self.d_kws		
	    except Exception,error:raise StandardError,"[Query]{%s}"%error
	    
	    l_buffer = mi_module.rigNull.moduleSet.getList()
	    try:mi_mirror = get_mirror(**kws)
	    except Exception,error:raise StandardError,"get_mirror | %s"%error
	    if mi_mirror:
		l_buffer.extend(mi_mirror.rigNull.moduleSet.getList())    
	    if l_buffer:
		r9Anim.MirrorHierarchy(l_buffer).makeSymmetrical(mode = '',primeAxis = "Left" )
		mc.select(l_buffer)
		return True
	    return False	 
    return fncWrap(*args,**kws).go() 

def mirrorSymRight(*args,**kws):
    class fncWrap(ModuleFunc):
	def __init__(self,*args,**kws):
	    """
	    """	
	    super(fncWrap, self).__init__(*args,**kws)
	    self._str_funcName = "mirrorSymRight('%s')"%self._str_moduleName
	    self.__dataBind__(*args,**kws)
	    #=================================================================
	def __func__(self): 
	    try:#Query ========================================================
		mi_module = self._mi_module
		kws = self.d_kws		
	    except Exception,error:raise StandardError,"[Query]{%s}"%error
	    
	    l_buffer = mi_module.rigNull.moduleSet.getList()
	    try:mi_mirror = get_mirror(**kws)
	    except Exception,error:raise StandardError,"get_mirror | %s"%error
	    if mi_mirror:
		l_buffer.extend(mi_mirror.rigNull.moduleSet.getList())    	    
	    if l_buffer:
		r9Anim.MirrorHierarchy(l_buffer).makeSymmetrical(mode = '',primeAxis = "Right" )
		mc.select(l_buffer)
		return True
	    return False	 
    return fncWrap(*args,**kws).go() 

#=====================================================================================================
#>>> Sibling functions
#=====================================================================================================  
def mirrorMe_siblings(*args,**kws):
    class fncWrap(ModuleFunc):
	def __init__(self,*args,**kws):
	    """
	    """	
	    super(fncWrap, self).__init__(*args,**kws)
	    self._str_funcName = "mirrorMe_siblings('%s')"%self._str_moduleName
	    self._str_funcHelp = "Basic mirror me function"
	    self._l_ARGS_KWS_DEFAULTS =  [_d_KWARG_mModule,
	                                  _d_KWARG_excludeSelf]
	    self.__dataBind__(*args,**kws)

	def __func__(self): 
	    try:#Query ========================================================
		mi_module = self._mi_module
		kws = self.d_kws		
	    except Exception,error:raise StandardError,"[Query]{%s}"%error
	    
	    mi_moduleParent = mi_module.moduleParent
	    kws_parent = copy.copy(kws)
	    kws['mModule'] = mi_moduleParent
	    mi_parentMirror = get_mirror(**kws_parent)
	    if not mi_moduleParent and mi_parentMirror:
		raise StandardError,"Must have module parent and mirror"
	    ml_buffer = get_allModuleChildren(**kws_parent)
	    ml_buffer.extend(get_allModuleChildren(**kws_parent))
	    
	    int_lenMax = len(ml_buffer)  
	    l_controls = []

	    for i,mModule in enumerate(ml_buffer):
		try:
		    self.progressBar_set( status = "%s >> step:'%s' "%(self._str_reportStart,mModule.p_nameShort), progress = i, maxValue = int_lenMax)		    				    		    		    
		    l_controls.extend(mModule.rigNull.moduleSet.getList())			
		except Exception,error:
		    self.log_error("[child: %s]{%s}"%(mModule.getShortName(),error))
		    
	    if l_controls:
		r9Anim.MirrorHierarchy(l_controls).mirrorData(mode = '')		    
		mc.select(l_controls) 
		return True
	    return False
    return fncWrap(*args,**kws).go()
     
def animReset_siblings(*args,**kws):
    class fncWrap(ModuleFunc):
	def __init__(self,*args,**kws):
	    """
	    """	
	    super(fncWrap, self).__init__(*args,**kws)
	    self._str_funcName = "animReset_siblings('%s')"%self._str_moduleName
	    self._l_ARGS_KWS_DEFAULTS = [_d_KWARG_mModule,
	                                 {'kw':'transformsOnly',"default":True,'help':"Whether to only reset transforms","argType":"bool"},
	                                 _d_KWARG_excludeSelf]
	    self.__dataBind__(*args,**kws)    	    
	    
	def __func__(self): 
	    try:#Query ========================================================
		mi_module = self._mi_module
		kws = self.d_kws
		
		ml_buffer = get_moduleSiblings(**kws)
		int_lenMax = len(ml_buffer)		
	    except Exception,error:raise StandardError,"[Query]{%s}"%error	    
	    
	    l_controls = []
	    for i,mModule in enumerate(ml_buffer):
		_str_module = mModule.p_nameShort
		self.progressBar_set(status = "On: %s "%_str_module, progress = i, maxValue = int_lenMax)		    				    		    
		try:
		    l_controls.extend(mModule.rigNull.moduleSet.getList())			
		except Exception,error:
		    self.log_error("child: %s | %s"%(_str_module,error))
		    
	    if l_controls:
		mc.select(l_controls)
		ml_resetChannels.main(transformsOnly = self.d_kws['transformsOnly'])
		return True
	    return False

    #We wrap it so that it autoruns and returns
    return fncWrap(*args,**kws).go()

def animReset_children(*args,**kws):
    class fncWrap(ModuleFunc):
	def __init__(self,*args,**kws):
	    """
	    """	
	    super(fncWrap, self).__init__(*args,**kws)
	    self._str_funcName = "animReset_children('%s')"%self._str_moduleName
	    self._l_ARGS_KWS_DEFAULTS = [_d_KWARG_mModule,
	                                 {'kw':'transformsOnly',"default":True,'help':"Whether to only reset transforms","argType":"bool"},
	                                 {'kw':'excludeSelf',"default":True,'help':"Whether to exclude self in return","argType":"bool"}]
	    self.__dataBind__(*args,**kws)    	    
	    
	def __func__(self): 
	    try:#Query ========================================================
		mi_module = self._mi_module
		kws = self.d_kws
		
		ml_buffer = get_allModuleChildren(**kws)
		int_lenMax = len(ml_buffer)		
	    except Exception,error:raise StandardError,"[Query]{%s}"%error	    
	    
	    l_controls = []
	    for i,mModule in enumerate(ml_buffer):
		_str_module = mModule.p_nameShort
		self.progressBar_set(status = "On: %s "%_str_module, progress = i, maxValue = int_lenMax)		    				    		    
		try:
		    l_controls.extend(mModule.rigNull.moduleSet.getList())			
		except Exception,error:
		    self.log_error("child: %s | %s"%(_str_module,error))
		    
	    if l_controls:
		mc.select(l_controls)
		ml_resetChannels.main(transformsOnly = self.d_kws['transformsOnly'])
		return True
	    return False

    #We wrap it so that it autoruns and returns
    return fncWrap(*args,**kws).go()

def mirrorPush_siblings(*args,**kws):
    class fncWrap(ModuleFunc):
	def __init__(self,*args,**kws):
	    """
	    """	
	    super(fncWrap, self).__init__(*args,**kws)
	    self._str_funcName = "mirrorPush_siblings('%s')"%self._str_moduleName
	    self._l_ARGS_KWS_DEFAULTS = [_d_KWARG_mModule,
	                                 {'kw':'excludeSelf',"default":True,'help':"Whether to exclude self in return","argType":"bool"}]
	    
	    self.__dataBind__(*args,**kws)    	    
	    
	def __func__(self): 
	    try:#Query ========================================================
		mi_module = self._mi_module
		kws = self.d_kws
		ml_buffer = get_moduleSiblings(**kws)
		int_lenMax = len(ml_buffer)		
	    except Exception,error:raise StandardError,"[Query]{%s}"%error	    
	    
	    l_controls = []
	    for i,mModule in enumerate(ml_buffer):
		_str_module = mModule.p_nameShort
		self.progressBar_set(status = "On: %s "%_str_module, progress = i, maxValue = int_lenMax)		    				    		    
		try:
		    l_controls.extend(mModule.rigNull.moduleSet.getList())
		    kws = self.get_cleanKWS()#We use this to get non registered kws -- maya one's more than like
		    kws['mModule'] = i_c
		    mirrorPush(**kws)		    
		except Exception,error:
		    self.log_error("child: %s | %s"%(_str_module,error))
		    
	    if l_controls:
		mc.select(l_controls)
		return True
	    return False

    #We wrap it so that it autoruns and returns
    return fncWrap(*args,**kws).go()

def mirrorPull_siblings(*args,**kws):
    class fncWrap(ModuleFunc):
	def __init__(self,*args,**kws):
	    """
	    """	
	    super(fncWrap, self).__init__(*args,**kws)
	    self._str_funcName = "mirrorPull_siblings('%s')"%self._str_moduleName
	    self._l_ARGS_KWS_DEFAULTS = [_d_KWARG_mModule,
	                                 {'kw':'excludeSelf',"default":True,'help':"Whether to exclude self in return","argType":"bool"}]
	    
	    self.__dataBind__(*args,**kws)    	    
	    
	def __func__(self): 
	    try:#Query ========================================================
		mi_module = self._mi_module
		kws = self.d_kws
		ml_buffer = get_moduleSiblings(**kws)
		int_lenMax = len(ml_buffer)		
	    except Exception,error:raise StandardError,"[Query]{%s}"%error	    
	    
	    l_controls = []
	    for i,mModule in enumerate(ml_buffer):
		_str_module = mModule.p_nameShort
		self.progressBar_set(status = "On: %s "%_str_module, progress = i, maxValue = int_lenMax)		    				    		    
		try:
		    l_controls.extend(mModule.rigNull.moduleSet.getList())
		    kws = self.get_cleanKWS()#We use this to get non registered kws -- maya one's more than like
		    kws['mModule'] = i_c
		    mirrorPull(**kws)		    
		except Exception,error:
		    self.log_error("child: %s | %s"%(_str_module,error))
		    
	    if l_controls:
		mc.select(l_controls)
		return True
	    return False

    #We wrap it so that it autoruns and returns
    return fncWrap(*args,**kws).go()


def get_moduleSiblings(*args,**kws):
    l_sibblingIgnoreCheck = ['finger','thumb']
    class fncWrap(ModuleFunc):
	def __init__(self,*args,**kws):
	    """
	    """	
	    super(fncWrap, self).__init__(*args,**kws)
	    self._str_funcName = "get_moduleSiblings('%s')"%self._str_moduleName
	    self._l_ARGS_KWS_DEFAULTS = [_d_KWARG_mModule,_d_KWARG_excludeSelf]	    
	    self.__dataBind__(*args,**kws)
	    
	def __func__(self):
	    try:#Query ========================================================
		mi_module = self._mi_module
		mi_modParent = self._mi_module.moduleParent
		kws = self.d_kws		
	    except Exception,error:raise StandardError,"[Query]{%s}"%error
	    
	    if not mi_modParent:
		self.log_info("No module parent found. No siblings possible")
		return []
	    
	    ml_buffer = copy.copy(mi_module.moduleParent.moduleChildren)
	    #self.log_debug("Possible siblings: %s"%ml_buffer)
	    
	    ml_return = []
	    int_lenMax = len(ml_buffer)
	    for i,mModule in enumerate(ml_buffer):
		self.progressBar_set(status = "Remaining to process... ", progress = i, maxValue = int_lenMax)	
		if mModule.mNode == mi_module.mNode:
		    self.log_debug("Self Match! | excludeSelf : %s"%kws['excludeSelf'])
		    if kws['excludeSelf'] != True:
			ml_return.append(mi_module)
		elif mi_module.moduleType == mModule.moduleType or mi_module.moduleType in l_sibblingIgnoreCheck:
		    self.log_debug("Type match match : %s"%mModule)		    
		    if mi_module.getAttr('cgmDirection') != mModule.getAttr('cgmDirection') or mi_module.moduleType in l_sibblingIgnoreCheck:
			self.log_debug("Appending: %s"%mModule)
			ml_return.append(mModule)
	    return ml_return

    #We wrap it so that it autoruns and returns
    return fncWrap(*args,**kws).go()

#=====================================================================================================
#>>> Children functions
#=====================================================================================================  
def get_allModuleChildren(*args,**kws):
    class fncWrap(ModuleFunc):
	def __init__(self,*args,**kws):
	    """
	    """	
	    super(fncWrap, self).__init__(*args,**kws)
	    self._str_funcName = "get_allModuleChildren('%s')"%self._str_moduleName
	    self._l_ARGS_KWS_DEFAULTS =  [_d_KWARG_mModule,_d_KWARG_excludeSelf]
	    self.__dataBind__(*args,**kws)
	    
	def __func__(self): 
	    try:#Query ========================================================
		mi_module = self._mi_module
		kws = self.d_kws		
	    except Exception,error:raise StandardError,"[Query]{%s}"%error		

	    ml_children = []
	    ml_childrenCull = copy.copy(mi_module.moduleChildren)
			   
	    cnt = 0
	    #Process the childdren looking for parents as children and so on and so forth, appending them as it finds them
	    while len(ml_childrenCull)>0 and cnt < 100:#While we still have a cull list
		cnt+=1                        
		if cnt == 99:
		    raise StandardError,"Max count reached"
		for i_child in ml_childrenCull:
		    if i_child not in ml_children:
			ml_children.append(i_child)
		    for i_subChild in i_child.moduleChildren:
			ml_childrenCull.append(i_subChild)
		    ml_childrenCull.remove(i_child) 
	    if not self.d_kws['excludeSelf']:
		ml_children.append(self._mi_module)		
	    return ml_children

    #We wrap it so that it autoruns and returns
    return fncWrap(*args,**kws).go()   

def animKey_children(*args,**kws):
    class fncWrap(ModuleFunc):
	def __init__(self,*args,**kws):
	    """
	    """
	    super(fncWrap, self).__init__(*args, **kws)
	    self._str_funcName= "animKey_children('%s')"%self._str_moduleName
	    self._str_funcHelp = "    Key module and all module children controls"			    
	    self.__dataBind__(*args,**kws)	
	    self._l_ARGS_KWS_DEFAULTS = [_d_KWARG_mModule,_d_KWARG_excludeSelf]
	    
	def __func__(self): 
	    try:#Query ========================================================
		mi_module = self._mi_module
		kws = self._d_funcKWs
	    except Exception,error:raise StandardError,"[Query]{%s}"%error
	    
	    ml_buffer = get_allModuleChildren(**kws)
	    int_lenMax = len(ml_buffer)		
	    l_controls = []
	    for i,i_c in enumerate(ml_buffer):
		log.info(i_c.p_nameShort)
		try:
		    self.progressBar_set(status = "Remaining to process... ", progress = i, maxValue = int_lenMax)		    				    		    
		    l_controls.extend(i_c.rigNull.moduleSet.getList())
		except Exception,error:
		    log.error("%s  child: %s | %s"%(self._str_reportStart,i_c.getShortName(),error))
	    if l_controls:
		mc.select(l_controls)
		kws = self.get_cleanKWS()#We use this to get non registered kws -- maya one's more than likely
		mc.setKeyframe(**kws)
		return True
	    return False  
    return fncWrap(*args,**kws).go()

def animKey_siblings(*args,**kws):
    class fncWrap(ModuleFunc):
	def __init__(self,*args,**kws):
	    """
	    """
	    super(fncWrap, self).__init__(*args, **kws)
	    self._str_funcName= "animSelect_children('%s')"%self._str_moduleName
	    self._str_funcHelp = "Selects controls of a module's children"			    
	    self.__dataBind__(*args,**kws)	
	    self._l_ARGS_KWS_DEFAULTS = [_d_KWARG_mModule,_d_KWARG_excludeSelf]
	
	def __func__(self): 
	    try:#Query ========================================================
		mi_module = self._mi_module
		kws = self._d_funcKWs
		self.log_info(kws)
	    except Exception,error:raise StandardError,"[Query]{%s}"%error
	    
	    ml_buffer = get_moduleSiblings(**kws)
	    int_lenMax = len(ml_buffer)		
	    l_controls = []
	    for i,i_c in enumerate(ml_buffer):
		log.info(i_c.p_nameShort)
		try:
		    self.progressBar_set(status = "Remaining to process... ", progress = i, maxValue = int_lenMax)		    				    		    
		    l_controls.extend(i_c.rigNull.moduleSet.getList())
		except Exception,error:
		    log.error("%s  child: %s | %s"%(self._str_reportStart,i_c.getShortName(),error))
	    if l_controls:
		mc.select(l_controls)
		kws = self.get_cleanKWS()#We use this to get non registered kws -- maya one's more than like
		mc.setKeyframe(**kws)
		return True
	    return False  
    return fncWrap(*args,**kws).go()
    
def animSelect_children(*args,**kws):
    class fncWrap(ModuleFunc):
	def __init__(self,*args,**kws):
	    """
	    """
	    super(fncWrap, self).__init__(*args, **kws)
	    self._str_funcName= "animSelect_children('%s')"%self._str_moduleName
	    self._str_funcHelp = "Selects controls of a module's children"			    
	    self._l_ARGS_KWS_DEFAULTS = [_d_KWARG_mModule,_d_KWARG_excludeSelf]
	    self.__dataBind__(*args,**kws)	    
	    #=================================================================
	    
	def __func__(self):
	    try:#Query ========================================================
		mi_module = self._mi_module
		kws = self.d_kws		
	    except Exception,error:raise StandardError,"[Query]{%s}"%error

	    l_controls = mi_module.rigNull.msgList_getMessage('controlsAll') or []
	    ml_children = get_allModuleChildren(**kws)
	    int_lenMax = len(ml_children)
	    for i,i_c in enumerate(ml_children):
		self.progressBar_set(status = "Remaining to process... ", progress = i, maxValue = int_lenMax)		    				    		    
		buffer = i_c.rigNull.msgList_getMessage('controlsAll')
		if buffer:
		    l_controls.extend(buffer)
		       
	    if l_controls:
		mc.select(l_controls)
		return True
	    return False	    
    return fncWrap(*args,**kws).go()
    
def animSelect_siblings(*args,**kws):
    class fncWrap(ModuleFunc):
	def __init__(self,*args,**kws):
	    """
	    """
	    super(fncWrap, self).__init__(*args, **kws)
	    self._str_funcName= "animSelect_siblings('%s')"%self._str_moduleName
	    self._str_funcHelp = "Selects controls of module siblings"			    
	    self._l_ARGS_KWS_DEFAULTS = [_d_KWARG_mModule,_d_KWARG_excludeSelf]
	    self.__dataBind__(*args,**kws)	    
	    #=================================================================
	    
	def __func__(self):
	    try:#Query ========================================================
		mi_module = self._mi_module
		kws = self.d_kws		
	    except Exception,error:raise StandardError,"[Query]{%s}"%error

	    ml_buffer = get_moduleSiblings(**kws)
	    
	    l_controls = []
	    int_lenMax = len(ml_buffer)
	    for i,mModule in enumerate(ml_buffer):
		try:
		    self.progressBar_set(status = "Remaining to process... ", progress = i, maxValue = int_lenMax)		    				    		    
		    l_controls.extend(mModule.rigNull.moduleSet.getList())
		except Exception,error:
		    self.log_error("%s  Sibbling: %s | %s"%(self._str_reportStart,mModule.getShortName(),error))
	    if l_controls:
		mc.select(l_controls)
		return True	
	    return False  	    
    return fncWrap(*args,**kws).go()
    
def animPushPose_siblings(*args,**kws):
    class fncWrap(ModuleFunc):
	def __init__(self,*args,**kws):
	    """
	    """
	    super(fncWrap, self).__init__(*args, **kws)
	    self._str_funcName = "animPushPose_siblings('%s')"%self._str_moduleName
	    #self._l_ARGS_KWS_DEFAULTS = [_d_KWARG_mModule]	    
	    self.__dataBind__(*args,**kws)
	    
	def __func__(self): 
	    try:#Query ========================================================
		mi_module = self._mi_module
		kws = self.d_kws	
	    except Exception,error:raise StandardError,"[Query]{%s}"%error
	    
	    ml_buffer = get_moduleSiblings(**kws)
	    l_moduleControls = self._mi_module.rigNull.msgList_getMessage('controlsAll')
	    int_lenMax = len(ml_buffer)		
	    l_controls = []
	    for i,i_c in enumerate(ml_buffer):
		try:		    
		    _str_child = i_c.p_nameShort
		    self.progressBar_set(status = "%s >> step:'%s' "%(self._str_reportStart,_str_child), progress = i, maxValue = int_lenMax)		    				    		    			
		    l_siblingControls = i_c.rigNull.msgList_getMessage('controlsAll')
		    for i,c in enumerate(l_siblingControls):
			#log.info("%s %s >> %s"%(self._str_reportStart,l_moduleControls[i],c))
			r9Anim.AnimFunctions().copyAttributes(nodes=[l_moduleControls[i],c])
		    l_controls.extend(l_siblingControls)
		except Exception,error:
		    log.error("%s  child: %s | %s"%(self._str_reportStart,_str_child,error))	    
	    if l_controls:
		mc.select(l_controls)
		    
	    return True  
    return fncWrap(*args,**kws).go()


#Dyn Switch =====================================================================================================
def dynSwitch_children(*args,**kws):
    class fncWrap(ModuleFunc):
	def __init__(self,*args,**kws):
	    """
	    """
	    super(fncWrap, self).__init__(*args, **kws)
	    self._str_funcName= "dynSwitch_children('%s')"%self._str_moduleName
	    self._str_funcHelp = "Activate dynSwtich on children"			    
	    self._l_ARGS_KWS_DEFAULTS = [_d_KWARG_mModule,
	                                 _d_KWARG_dynSwitchArg
	                                 ]
	    self.__dataBind__(*args,**kws)	    
	    #=================================================================
	    
	def __func__(self):
	    try:#Query ========================================================
		mi_module = self._mi_module
		_dynSwitchArg = self.d_kws['dynSwitchArg']
		kws = self.d_kws		
	    except Exception,error:raise StandardError,"[Query]{%s}"%error
	    
	    try:#Process ========================================================	    
		ml_children = get_allModuleChildren(**kws)
		int_lenMax = len(ml_children)
		
		for i,i_c in enumerate(ml_children):
		    try:
			self.progressBar_set(status = "%s step:'%s' "%(self._str_funcName,i_c.p_nameShort), progress = i, maxValue = int_lenMax)		    				    		    
			i_c.rigNull.dynSwitch.go(_dynSwitchArg)
		    except Exception,error:
			self.log_error(" child: %s | %s"%(i_c.getShortName(),error))
		return True
	    except Exception,error:
		self.log_error(error)  
		return False	    
    return fncWrap(*args,**kws).go()

def dynSwitch_siblings(*args,**kws):
    class fncWrap(ModuleFunc):
	def __init__(self,*args,**kws):
	    """
	    """
	    super(fncWrap, self).__init__(*args, **kws)
	    self._str_funcName= "dynSwitch_siblings('%s')"%self._str_moduleName
	    self._str_funcHelp = "Activate dynSwtich on siblings"			    
	    self._l_ARGS_KWS_DEFAULTS = [_d_KWARG_mModule,_d_KWARG_dynSwitchArg,_d_KWARG_excludeSelf]
	    self.__dataBind__(*args,**kws)	    
	    #=================================================================
	    
	def __func__(self):
	    try:#Query ========================================================
		mi_module = self._mi_module
		_dynSwitchArg = self.d_kws['dynSwitchArg']
		kws = self.d_kws		
	    except Exception,error:raise StandardError,"[Query]{%s}"%error
	    
	    try:#Process ========================================================	    
		ml_buffer = get_moduleSiblings(**kws)
		int_lenMax = len(ml_buffer)
		
		for i,i_c in enumerate(ml_buffer):
		    try:
			self.progressBar_set(status = "%s step:'%s' "%(self._str_funcName,i_c.p_nameShort), progress = i, maxValue = int_lenMax)		    				    		    
			i_c.rigNull.dynSwitch.go(_dynSwitchArg)
		    except Exception,error:
			self.log_error(" child: %s | %s"%(i_c.getShortName(),error))
		return True
	    except Exception,error:
		self.log_error(error)  
		return False	    
    return fncWrap(*args,**kws).go()
          
def get_mirrorSideAsString(*args,**kws):
    class fncWrap(ModuleFunc):
	def __init__(self,*args,**kws):
	    """
	    """
	    super(fncWrap, self).__init__(*args, **kws)
	    self._str_funcName= "get_mirrorSideAsString('%s')"%self._str_moduleName
	    self._str_funcHelp = "Returns the mirror side as a string"
	    self.__dataBind__(*args,**kws)	    
	    #=================================================================
	    
	def __func__(self):
	    try:#Query ========================================================
		mi_module = self._mi_module
		kws = self.d_kws		
	    except Exception,error:raise StandardError,"[Query]{%s}"%error
	    _str_direction = mi_module.getAttr('cgmDirection') 
	    if _str_direction is not None and _str_direction.lower() in ['right','left']:
		return _str_direction.capitalize()
	    else:return 'Centre'	    
    return fncWrap(*args,**kws).go()

def toggle_subVis(*args,**kws):
    class fncWrap(ModuleFunc):
	def __init__(self,*args,**kws):
	    """
	    """	
	    super(fncWrap, self).__init__(*args, **kws)
	    self._str_funcName = "toggle_subVis('%s')"%self._str_moduleName
	    self.__dataBind__(*args,**kws)	    
	def __func__(self): 
	    mi_module = self._mi_module
	    try:
		if mi_module.moduleType in __l_faceModules__:
		    mi_module.rigNull.settings.visSubFace = not mi_module.rigNull.settings.visSubFace		    
		else:
		    mi_module.rigNull.settings.visSub = not mi_module.rigNull.settings.visSub
		return True
	    except Exception,error:
		if not mi_module.rigNull.getMessage('settings'):
		    self.log_error("This module lacks a settings control")
		else:self.log_error("%s"%(error))
	    return False  
	
    #We wrap it so that it autoruns and returns
    return fncWrap(*args,**kws).go()

def animSetAttr_children(*args,**kws):
    class fncWrap(ModuleFunc):
	def __init__(self,*args,**kws):
	    """
	    """	
	    super(fncWrap, self).__init__(*args,**kws)
	    self._str_funcHelp = "Function to set an attribute value on all controls of a module's children"
	    self._str_funcName = "animReset_siblings('%s')"%self._str_moduleName
	    self._l_ARGS_KWS_DEFAULTS = [_d_KWARG_mModule, cgmMeta._d_KWARG_attr, cgmMeta._d_KWARG_value,
	                                 {'kw':'settingsOnly',"default":False,'help':"Only check settings controls","argType":"bool"},
	                                 _d_KWARG_excludeSelf]
	    self.__dataBind__(*args,**kws)

	def __func__(self): 
	    try:#Query ========================================================
		mi_module = self._mi_module
		kws = self.d_kws	
		
		ml_buffer = get_allModuleChildren(**kws)
		int_lenMax = len(ml_buffer)		
	    except Exception,error:raise StandardError,"[Query]{%s}"%error
	    
	    for i,mModule in enumerate(ml_buffer):
		try:
		    self.progressBar_set(status = "Step:'%s' "%(self._str_moduleName), progress = i, maxValue = int_lenMax)		    				    		    		    
		    if self.d_kws['settingsOnly']:
			mmi_rigNull = mModule.rigNull
			if mmi_rigNull.getMessage('settings'):
			    mmi_rigNull.settings.__setattr__(self.d_kws['attr'],self.d_kws['value'])
		    else:
			for o in mModule.rigNull.moduleSet.getList():
			    attributes.doSetAttr(o,self.d_kws['attr'],self.d_kws['value'])
		except Exception,error:
		    self.log_error("[child: %s]{%s}"%(self._str_moduleName,error))
	    return False
    #We wrap it so that it autoruns and returns
    return fncWrap(*args,**kws).go()

