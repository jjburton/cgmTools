import time
import maya.cmds as mc
import copy as copy
import os

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
from cgm.core.cgmPy import validateArgs as cgmValid
from cgm.lib import (search,attributes,lists)
from cgm.core import cgm_General as cgmGeneral
from cgm.lib.ml import ml_resetChannels

#Shared Settings
#========================= 
geoTypes = 'nurbsSurface','mesh','poly','subdiv'
_d_KWARG_mPuppet = {'kw':'mPuppet',"default":None,'help':"cgmPuppet mNode or str name","argType":"cgmPuppet"}
_d_KWARG_moduleStateArg = {'kw':'moduleStateArg',"default":0,'help':"What state to check for","argType":"module state"}
_d_KWARG_mirrorSideArg = {'kw':'mirrorSideArg',"default":None,'help':"Which side arg","argType":"string"}
_d_KWARG_mode = {'kw':'mode',"default":None,'help':"Special mode for this fuction","argType":"varied"}

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
        self._b_ExceptionInterupt = False
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

def get_report(*args,**kws):
    '''
    Puppet reporting tool
    '''
    class fncWrap(PuppetFunc):
        def __init__(self,*args,**kws):
            """
            """	
            super(fncWrap, self).__init__(*args,**kws)
            self._b_reportTimes = True
            self._str_funcName = "puppet.get_report('{0}')".format(self._mi_puppet.cgmName)		    	    	    
            self._l_ARGS_KWS_DEFAULTS = [_d_KWARG_mPuppet,
                                         {'kw':'moduleReport',"default":False,'help':"Whether to get the module report","argType":"bool"},	                                 
                                         {'kw':'rigReport',"default":False,'help':"Whether to include the rig report","argType":"bool"},
                                         ] 
            self.__dataBind__(*args,**kws)   

        def __func__(self):
            try:
                try:
                    mi_puppet = self._mi_puppet
                    self.ml_modules = getModules(self._mi_puppet)
                    int_lenModules = len(self.ml_modules)		    
                except Exception,error: raise Exception,"Link meta fail | error: {0}".format(error)

                _b_rigReport = cgmValid.boolArg(self.d_kws['rigReport'],calledFrom=self._str_reportStart)
                _b_moduleReport = cgmValid.boolArg(self.d_kws['moduleReport'],calledFrom=self._str_reportStart)

                if not _b_rigReport and not _b_moduleReport:
                    self.log_error("Nothing set to find. Check your kws")
                    return self._SuccessReturn_(False)
            except Exception,error: raise Exception,"Inital data fail | error: {0}".format(error)
            try:
                if _b_moduleReport:
                    self.log_info(cgmGeneral._str_headerDiv + "Module Report " + cgmGeneral._str_headerDiv + cgmGeneral._str_subLine)
                    for i,mModule in enumerate(self.ml_modules):
                        try:
                            _str_module = mModule.p_nameShort
                            mi_rigNull = mModule.rigNull
                            mi_templateNull = mModule.templateNull
                            self.progressBar_set(status = "Module Report: '%s' "%(_str_module),progress = i, maxValue = int_lenModules)

                            self.log_info("'{0}' | state: '{1}' | template version: {2} | rig version: {3}".format(mModule.p_nameShort,
                                                                                                                   cgmGeneral._l_moduleStates[mModule.getState()],
                                                                                                                   mi_templateNull.getMayaAttr('version'),
                                                                                                                   mi_rigNull.getMayaAttr('version')))
                        except Exception,error:
                            raise Exception,"Module report fail'{0}' | error: {1}".format(mModule.p_nameShort,error)			    
                for mModule in self.ml_modules:
                    try:
                        if _b_rigReport:
                            mModule._UTILS.rig_getReport(mModule)
                    except Exception,error:
                        raise Exception,"Module '{0}' | error: {1}".format(mModule.p_nameShort,error)		
            except Exception,error:raise Exception,"Report fail | error: {0}".format(error)		
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
            self._str_funcName = "puppet.getUnifiedGeo('%s')"%self._mi_puppet.cgmName	
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
            self._str_funcName = "puppet.getGeo('%s')"%self._mi_puppet.cgmName	
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
            self._str_funcName = "puppet.getModules('%s')"%self._mi_puppet.cgmName
            self._str_funcHelp = "Get the modules of a puppet"	    
            self.__dataBind__(*args,**kws)
            self._b_reportTimes = 1
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
            self._str_funcName = "puppet.gatherModules('%s')"%self._mi_puppet.cgmName	
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
            self._str_funcName = "puppet.getModuleFromDict('%s')"%self._mi_puppet.cgmName	
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
            self._str_funcName = "puppet.getState('%s')"%self._mi_puppet.cgmName	
            self._str_funcHelp = "Get a pupppet's state"	    	    
            self.__dataBind__(*args,**kws)
            self._b_reportTimes = 1
        def __func__(self):
            """
            """
            ml_modules = getModules(self._mi_puppet)
            #ml_modules = self._mi_puppet.moduleChildren
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
            #for p in d_states.iteritems():
                #self.log_info(" '%s' | state : %s"%(p[0],p[1]))
            return min(l_states)
    return fncWrap(*args,**kws).go()

def isTemplated(*args,**kws):
    class fncWrap(PuppetFunc):
        def __init__(self,*args,**kws):
            """
            """	
            super(fncWrap, self).__init__(*args,**kws)
            self._str_funcName = "puppet.isTemplated('%s')"%self._mi_puppet.cgmName	
            self.__dataBind__(*args,**kws)

        def __func__(self):
            """
            """
            ml_modules = getModules(self._mi_puppet)	    
            if not ml_modules:
                self.log_warning("'%s' has no modules"%self.cgmName)
                return False

            for i,mModule in enumerate(ml_modules):
                if not mModule.isTemplated(**kws):
                    return False
            return True
    return fncWrap(*args,**kws).go()

def isSized(*args,**kws):
    class fncWrap(PuppetFunc):
        def __init__(self,*args,**kws):
            """
            """	
            super(fncWrap, self).__init__(*args,**kws)
            self._str_funcName = "puppet.isSized('%s')"%self._mi_puppet.cgmName	
            self.__dataBind__(*args,**kws)

        def __func__(self):
            """
            """
            ml_modules = getModules(self._mi_puppet)	    
            if not ml_modules:
                self.log_warning("'%s' has no modules"%self.cgmName)
                return False

            for i,mModule in enumerate(ml_modules):
                if not mModule.isSized(**kws):
                    return False
            return True
    return fncWrap(*args,**kws).go()

def isSkeletonized(*args,**kws):
    class fncWrap(PuppetFunc):
        def __init__(self,*args,**kws):
            """
            """	
            super(fncWrap, self).__init__(*args,**kws)
            self._str_funcName = "puppet.isSkeletonized('%s')"%self._mi_puppet.cgmName	
            self.__dataBind__(*args,**kws)

        def __func__(self):
            """
            """
            ml_modules = getModules(self._mi_puppet)	    
            if not ml_modules:
                self.log_warning("'%s' has no modules"%self.cgmName)
                return False

            for i,mModule in enumerate(ml_modules):
                if not mModule.isSkeletonized(**kws):
                    return False
            return True
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
            self._str_funcName = "puppet.getOrderedModules('%s')"%self._mi_puppet.cgmName
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
#>>> Template functions
#=====================================================================================================
def templateSettings_do(*args,**kws):
    '''
    Simple factory for template settings functions
    '''
    class fncWrap(PuppetFunc):
        def __init__(self,*args,**kws):
            """
            """	
            super(fncWrap, self).__init__(*args,**kws)
            self._b_reportTimes = True
            self._str_funcName = "puppet.templateSettings_do('{0}')".format(self._mi_puppet.cgmName)		    	    
            self._l_ARGS_KWS_DEFAULTS = [_d_KWARG_mPuppet,
                                         {'kw':'mode',"default":None,'help':"Special mode for this fuction","argType":"varied"}] 
            self.__dataBind__(*args,**kws)
            self._str_funcName = "puppet.templateSettings_do('{0}',mode = {1})".format(self._mi_puppet.cgmName,self.d_kws.get('mode') or None)		    	    
            self.__updateFuncStrings__()

        def __func__(self):
            """
            """
            l_modes = 'reset','store','load'
            str_mode = self.d_kws['mode']
            str_mode = cgmValid.stringArg(str_mode,noneValid=False,calledFrom = self._str_funcName)
            if str_mode not in l_modes:
                raise ValueError,"Mode : {0} not in list: {1}".format(str_mode,l_modes)
            if str_mode is None:
                self.log_error("Mode is None. Don't know what to do with this")
                return False

            ml_modules = getModules(self._mi_puppet)	    
            if not ml_modules:
                self.log_warning("'%s' has no modules"%self.cgmName)
                return False

            int_lenModules = len(ml_modules)
            for i,mModule in enumerate(ml_modules):
                try:
                    _str_module = mModule.p_nameShort
                    d_modesToCalls = {'reset':mModule.poseReset_templateSettings,
                                      'store':mModule.storeTemplatePose,
                                      'load':mModule.loadTemplatePose,
                                      }
                    self.progressBar_set(status = "{0} Module: '{1}' ".format(str_mode,_str_module),progress = i, maxValue = int_lenModules)	    		

                    if not d_modesToCalls[str_mode](**kws):
                        self.log_error("{0} failed".format(mModule.p_nameShort))
                        return False
                except Exception,error:raise Exception,"Module : '{0}' | Mode : {1} | error: {2}".format(mModule.p_nameShort,str_mode,error)
            return True
    return fncWrap(*args,**kws).go()

def mirrorSetup_verify(*args,**kws):
    '''
    '''
    class fncWrap(PuppetFunc):
        def __init__(self,*args,**kws):
            """
            """	
            super(fncWrap, self).__init__(*args,**kws)
            self._str_funcName = 'puppetFactory.mirrorSetup_verify'
            self._l_ARGS_KWS_DEFAULTS = [_d_KWARG_mPuppet,
                                         {'kw':'mode',"default":None,'help':"What mode will we be verifying in.","argType":"varied"},
                                         _d_KWARG_mirrorSideArg]
            self.__dataBind__(*args,**kws)
            self._b_ExceptionInterupt = True
            self._b_reportTimes = 1
            self.l_funcSteps = [{'step':'Query','call':self._verifyData},
                                {'step':'Module data','call':self._moduleData_},
                                {'step':'Process','call':self._process}]

            self._str_funcName = "puppet.templateSettings_mirrorVerify('{0}',mode = '{1}')".format(self._mi_puppet.cgmName,self.d_kws.get('mode') or None)		    	    
            self.__updateFuncStrings__()

        def _verifyData(self):
            """
            """
            #self.d_kws['str_side'],
            #self.str_side = cgmGeneral.verify_mirrorSideArg(self.d_kws['mirrorSideArg'],**kws)	

            l_modes = ['template','anim']
            str_mode = self.d_kws['mode']
            self.str_mode = cgmValid.stringArg(str_mode,noneValid=False,calledFrom = self._str_funcName)
            if self.str_mode not in l_modes:
                raise ValueError,"Mode : {0} not in list: {1}".format(str_mode,l_modes)

            self.md_data = {}
            self.ml_modules = getOrderedModules(self._mi_puppet)

            self.d_runningSideIdxes = {}

        def _moduleData_(self):
            ml_modules = self.ml_modules
            self.int_lenModules = len(ml_modules)

            try:#>>>Controls map
                for i,mModule in enumerate(ml_modules):
                    _str_module = mModule.p_nameShort		    
                    self.progressBar_set(status = "Initial gather for: '{0}' ".format(_str_module),progress = i, maxValue = self.int_lenModules)		    				    		    
                    self.md_data[mModule.mNode] = {}#...Initize a dict for this object
                    _d = self.md_data[mModule.mNode]#...link it
                    _d['str_name'] = _str_module
                    _d['ml_controls'] = mModule.get_controls(self.str_mode)
                    _d['mi_mirror'] = mModule.getMirror()
                    _d['str_side'] = cgmGeneral.verify_mirrorSideArg(mModule.getMayaAttr('cgmDirection') or 'center',**kws)

                    if _d['str_side'] not in self.d_runningSideIdxes.keys():
                        self.d_runningSideIdxes[_d['str_side']] = [0]
                    self.log_infoDict(_d,_str_module)
                self.log_infoDict(self.d_runningSideIdxes,"Side idxs")
            except Exception,error:raise Exception,"Control Gather fail | error: {0}".format(error)

        def _process(self):
            """
            1) get a module 
            2) get controls
            3) see if has a mirror
            4) register 
            """
            ml_cull = copy.copy(self.ml_modules)

            while ml_cull:
                for mModule in ml_cull:		
                    try:#>>>Controls map
                        self.log_info("On: {0}".format(mModule.p_nameShort))

                        try:md_buffer = self.md_data[mModule.mNode]#...get the modules dict
                        except Exception,error:raise Exception,"metaDict query | error: {0}".format(error)

                        ml_modulesToDo = [mModule]#...append
                        mi_mirror = md_buffer.get('mi_mirror') or False

                        if mi_mirror:
                            try:
                                try:md_mirror = self.md_data[mi_mirror.mNode]
                                except Exception,error:raise Exception,"Failed to pull mirror from metaDict | {0}".format(error)			    
                                int_controls = len(md_buffer['ml_controls'])
                                int_mirrorControls = len(self.md_data[mi_mirror.mNode]['ml_controls'])
                                if int_controls != int_mirrorControls:
                                    raise ValueError,"Control lengths of mirrors do not match | mModule: {0} | mMirror: {1}".format(md_buffer['str_name'],md_mirror['str_name'])
                                ml_modulesToDo.append(mi_mirror)#...append if we have it

                            except Exception,error:raise Exception,"mirror check fail | error: {0}".format(error)

                        for mi_module in ml_modulesToDo:
                            self.log_debug("Sub on: {0}".format(mi_module.p_nameShort))	

                            try:
                                try:md_buffer = self.md_data[mi_module.mNode]#...get the modules dict	
                                except Exception,error:raise Exception,"metaDict query | error: {0}".format(error)

                                ml_cull.remove(mi_module)#...remove this one as being processed
                                str_mirrorSide = md_buffer['str_side']
                                int_idxStart = max(self.d_runningSideIdxes[str_mirrorSide])
                                int_idxRunning = int_idxStart + 1
                                self.log_info("mModule: {0} | starting mirror index: {1}".format(md_buffer['str_name'],int_idxStart))

                                self.progressBar_set(status = "Verifying '{0}' ".format(md_buffer['str_name']),progress = len(ml_cull), maxValue = self.int_lenModules)		    				    

                                for i,mObj in enumerate(md_buffer['ml_controls']):
                                    try:
                                        mObj = cgmMeta.asMeta(mObj,'cgmControl',setClass = True)
                                        md_buffer[i] = mObj#...push back

                                        try:mObj._verifyMirrorable()
                                        except Exception,error:raise StandardError,"_mirrorSetup | {0}".format(error)

                                        l_enum = cgmMeta.cgmAttr(mObj,'mirrorSide').p_enum
                                        if str_mirrorSide in l_enum:
                                            log.debug("%s >> %s >> found in : %s"%(self._str_funcCombined, "mirrorSetup", l_enum))		
                                            try:
                                                if not cgmMeta.cgmAttr(mObj,'mirrorSide').getDriver():
                                                    mObj.mirrorSide = l_enum.index(str_mirrorSide)
                                                    self.log_debug("mirrorSide set to: %s"%(mObj.mirrorSide))						    
                                            except Exception,error:raise StandardError,"str_mirrorSide : %s | %s"%(str_mirrorSide,error)
                                        if not mObj.getMayaAttr('mirrorAxis'):
                                            mObj.mirrorAxis = 'translateX,rotateZ,rotateY'
                                            #log.debug("str_mirrorAxis set: %s"%(str_mirrorAxis))				    					    
                                        mObj.mirrorIndex = int_idxRunning
                                        #attributes.doSetAttr(mObj.mNode,'mirrorSide',l_enum.index(str_mirrorSide))
                                        attributes.doSetAttr(mObj.mNode,'mirrorIndex',int_idxRunning)
                                        
                                        int_idxRunning += 1
                                        self.d_runningSideIdxes[str_mirrorSide].append(int_idxRunning)					
                                    except Exception,error:raise Exception,"'{0}' fail | error: {1}".format(mObj.p_nameShort,error)
                            except Exception,error:raise Exception,"{0} fail | error: {1}".format(mi_module.p_nameShort,error)	
                    except Exception,error:raise Exception,"'{0}' fail | error: {1}".format(self.md_data[mModule.mNode]['str_name'],error)

            return True
    return fncWrap(*args,**kws).go()

def poseStore_templateSettings(*args,**kws):
    class fncWrap(PuppetFunc):
        def __init__(self,*args,**kws):
            """
            """	
            super(fncWrap, self).__init__(*args,**kws)
            self._str_funcName = "puppet.poseStore_templateSettings('%s')"%self._mi_puppet.cgmName	
            self.__dataBind__(*args,**kws)

        def __func__(self):
            """
            """
            ml_modules = getModules(self._mi_puppet)	    
            if not ml_modules:
                self.log_warning("'%s' has no modules"%self.cgmName)
                return False

            for i,mModule in enumerate(ml_modules):
                if not mModule.storeTemplatePose(**kws):
                    self.log_error("{0} failed".format(mModule.p_nameShort))
                    return False
            self.log_info("Template Pose Saved")
            return True
    return fncWrap(*args,**kws).go()

def poseLoad_templateSettings(*args,**kws):
    class fncWrap(PuppetFunc):
        def __init__(self,*args,**kws):
            """
            """	
            super(fncWrap, self).__init__(*args,**kws)
            self._str_funcName = "puppet.poseLoad_templateSettings('%s')"%self._mi_puppet.cgmName	
            self.__dataBind__(*args,**kws)

        def __func__(self):
            """
            """
            ml_modules = getModules(self._mi_puppet)	    
            if not ml_modules:
                self.log_warning("'%s' has no modules"%self.cgmName)
                return False

            for i,mModule in enumerate(ml_modules):
                if not mModule.loadTemplatePose(**kws):
                    self.log_error("{0} failed".format(mModule.p_nameShort))
                    return False
            self.log_info("Template Pose Loaded")
            return True
    return fncWrap(*args,**kws).go()


def template_saveConfig(*args,**kws):
    '''
    Simple factory for template settings functions
    '''
    class fncWrap(PuppetFunc):
        def __init__(self,*args,**kws):
            """
            """	
            super(fncWrap, self).__init__(*args,**kws)
            self._b_reportTimes = True
            self._str_funcName = "puppet.template_saveConfig('{0}')".format(self._mi_puppet.cgmName)		    	    
            self._l_ARGS_KWS_DEFAULTS = [_d_KWARG_mPuppet,
                                         {'kw':'destination',"default":None,'help':"location to store a file to","argType":"string or None for dialog"}] 
            self.__dataBind__(*args,**kws)	    	    

        def __func__(self):
            """
            """
            str_path = self.d_kws['destination']
            
            if not isinstance(str_path, basestring):
                raise TypeError('path must be string | str_path = {0}'.format(str_path))   
            #str_dir = p1
            #if not os.path.isdir(str_path.split('/')[0]):
                #raise ValueError('path must validate as os.path.isdir | str_path = {0}'.format(str_path))     
            
            self.log_info("File path: {0}".format(str_path))
            
            l_nodes = get_controls(self._mi_puppet, mode = 'template',asMeta = False)
            if not l_nodes:
                raise ValueError,"No controls found"
            
            try: r9Anim.r9Pose.PoseData().poseSave(l_nodes,str_path,useFilter=False)#this useFilter flag 
            except Exception,error:raise Exception,"poseSave | {0}".format(error)                

    return fncWrap(*args,**kws).go()

def template_loadConfig(*args,**kws):
    '''
    Simple factory for template settings functions
    '''
    class fncWrap(PuppetFunc):
        def __init__(self,*args,**kws):
            """
            """	
            super(fncWrap, self).__init__(*args,**kws)
            self._b_reportTimes = True
            self._str_funcName = "puppet.template_loadConfig('{0}')".format(self._mi_puppet.cgmName)		    	    
            self._l_ARGS_KWS_DEFAULTS = [_d_KWARG_mPuppet,
                                         {'kw':'filePath',"default":None,'help':"location to store a file to","argType":"string or None for dialog"}] 
            self.__dataBind__(*args,**kws)	    	    

        def __func__(self):
            """
            """
            str_path = self.d_kws['filePath']
            
            if not isinstance(str_path, basestring):
                raise TypeError('path must be string | str_path = {0}'.format(str_path))   
            #str_dir = p1
            #if not os.path.isdir(str_path.split('/')[0]):
                #raise ValueError('path must validate as os.path.isdir | str_path = {0}'.format(str_path))     
            
            self.log_info("File path: {0}".format(str_path))
            
            l_nodes = get_controls(self._mi_puppet, mode = 'template',asMeta = False)
            if not l_nodes:
                raise ValueError,"No controls found"
            
            try: r9Anim.r9Pose.PoseData().poseLoad(l_nodes,str_path,useFilter=False)#this useFilter flag 
            except Exception,error:"poseLoad | {0}".format(error)                

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
            self._str_funcName = "puppet.getModules('%s')"%self._mi_puppet.cgmName
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
                r9Anim.MirrorHierarchy().mirrorData(l_controls,mode = '')		
                mc.select(l_controls)
                return True	    
            return False
    return fncWrap(*args,**kws).go()

def get_joints(*args,**kws):
    '''
    Factory Rewrite of mirror functions.
    TODO -- replace the many mirror functions here
    '''
    class fncWrap(PuppetFunc):
        def __init__(self,*args,**kws):
            """
            """	
            super(fncWrap, self).__init__(*args,**kws)
            #self._b_reportTimes = True
            self._str_funcName = "puppet.get_joints('{0}')".format(self._mi_puppet.cgmName)		    	    	    
            self._l_ARGS_KWS_DEFAULTS = [_d_KWARG_mPuppet,
                                         {'kw':'skinJoints',"default":False,'help':"Whether to include skin joints or not","argType":"bool"},
                                         {'kw':'moduleJoints',"default":False,'help':"Whether to include module core joints or not","argType":"bool"},                                         
                                         {'kw':'rigJoints',"default":False,'help':"Whether to include rig joints or not","argType":"bool"},
                                         cgmMeta._d_KWARG_asMeta,                                         
                                         cgmMeta._d_KWARG_select] 
            self.__dataBind__(*args,**kws)   

        def __func__(self):
            try:
                try:
                    mi_puppet = self._mi_puppet
                    self.ml_modules = getModules(self._mi_puppet)		    
                except Exception,error: raise Exception,"Link meta fail | error: {0}".format(error)

                _b_skinJoints = cgmValid.boolArg(self.d_kws['skinJoints'],calledFrom=self._str_reportStart)
                _b_moduleJoints = cgmValid.boolArg(self.d_kws['moduleJoints'],calledFrom=self._str_reportStart)                
                _b_rigJoints = cgmValid.boolArg(self.d_kws['rigJoints'],calledFrom=self._str_reportStart)
                _b_select = cgmValid.boolArg(self.d_kws['select'],calledFrom=self._str_reportStart)

                if not _b_skinJoints and not _b_moduleJoints and not _b_rigJoints:
                    self.log_error("Nothing set to find. Check your kws")
                    return self._SuccessReturn_(False)
            except Exception,error: raise Exception,"Inital data fail | error: {0}".format(error)

            try:
                l_return = []
                for mModule in self.ml_modules:
                    try:
                        l_buffer = mModule.get_joints(**kws)
                        if not l_buffer:
                            raise StandardError,"No joints found"
                        l_return.extend(l_buffer)
                    except Exception,error:
                        self.log_error("Module '{0}' | error: {1}".format(mModule.p_nameShort,error))	
            except Exception,error:raise Exception,"Gather joints | error: {0}".format(error)		

            if not l_return:
                self.log_error("More than likely not skeletonized yet")
                return False
            elif _b_select:
                if kws.get('asMeta'):
                    mc.select([mObj.mNode for mObj in l_return])
                else:
                    mc.select(l_return)
            return l_return	    
    return fncWrap(*args,**kws).go()

def get_controls(*args,**kws):
    '''
    '''
    class fncWrap(PuppetFunc):
        def __init__(self,*args,**kws):
            """
            """	
            super(fncWrap, self).__init__(*args,**kws)
            #self._b_reportTimes = True
            self._str_funcName = "puppet.get_controls('{0}')".format(self._mi_puppet.cgmName)		    	    	    
            self._l_ARGS_KWS_DEFAULTS = [_d_KWARG_mPuppet,
                                        {'kw':'mode',"default":'anim','help':"Special mode for this fuction","argType":"varied"},
                                        cgmMeta._d_KWARG_asMeta,                                         
                                        cgmMeta._d_KWARG_select] 
            self.__dataBind__(*args,**kws)   

        def __func__(self):
            try:
                try:
                    mi_puppet = self._mi_puppet
                    self.ml_modules = getModules(self._mi_puppet)
                except Exception,error: raise Exception,"Link meta fail | error: {0}".format(error)

                _str_mode = cgmValid.stringArg(self.d_kws['mode'],calledFrom=self._str_reportStart)
                _b_select = cgmValid.boolArg(self.d_kws['select'],calledFrom=self._str_reportStart)

            except Exception,error: raise Exception,"Inital data fail | error: {0}".format(error)

            try:
                l_return = []
                for mModule in self.ml_modules:
                    try:
                        l_buffer = mModule.get_controls(mode = self.d_kws['mode'],asMeta = self.d_kws['asMeta'])
                        if not l_buffer:
                            raise StandardError,"No controls found"
                        l_return.extend(l_buffer)
                    except Exception,error:
                        self.log_error("Module '{0}' | error: {1}".format(mModule.p_nameShort,error))	
            except Exception,error:raise Exception,"Gather controls | error: {0}".format(error)		

            if not l_return:
                return False
            '''
            elif _b_select:
                if kws.get('asMeta'):
                    mc.select([mObj.mNode for mObj in l_return])
                else:
                    mc.select(l_return)'''
            return l_return	    
    return fncWrap(*args,**kws).go()

def get_jointsBindDict(*args,**kws):
    d_bindJointKeys_to_matchData = {'all':{},
                                    'body':{'faceModuleOK':False},
                                    'face':{'ignoreCheck':True},
                                    'bodyNoEyes':{'l_ignore':['eyeball']},
                                    'eyeball':{'isModule':'eyeball'},
                                    'head':{'indexArgs':[['neckHead',-1]]},
                                    'tongue':{'isModule':'tongue'}}    
    '''
    'tongue':['tongue','jaw','head'],
    'unified':['bodySansEyes'],
    'uprTeeth':['head','uprTeeth'],
    'lwrTeeth':['lowerTeeth','jaw','head'],
    'eyebrow':['eyebrow','uprHead','head'],
    'earLeft':['earLeft','uprHead','head'],
    'earRight':['earRight','uprHead','head'],
    'eyeLeft':['eyeLeft','uprHead','head'],
    'eyeRight':['eyeRight','uprHead','head'],
    'body':['bodySansEyes'
    '''
    class fncWrap(PuppetFunc):
        def __init__(self,*args,**kws):
            """
            """	
            super(fncWrap, self).__init__(*args,**kws)
            self._b_reportTimes = True
            self._str_funcName = "puppet.get_jointsBindDict('{0}')".format(self._mi_puppet.cgmName)		    	    	    
            self._l_ARGS_KWS_DEFAULTS = [_d_KWARG_mPuppet,
                                         cgmMeta._d_KWARG_asMeta] 
            self.__dataBind__(*args,**kws)   

        def __func__(self):
            try:
                try:
                    mi_puppet = self._mi_puppet
                    self.ml_modules = getModules(self._mi_puppet)		    
                except Exception,error: raise Exception,"Link meta fail | error: {0}".format(error)
                self._d_return = {}

                #Gonna build our list holders
                for key in d_bindJointKeys_to_matchData.keys():
                    self._d_return[key] = []#...initiate the list
            except Exception,error: raise Exception,"Inital data fail | error: {0}".format(error)

            try:
                l_return = []
                l_stopMatch = []
                for mModule in self.ml_modules:
                    try:
                        l_buffer = mModule.get_joints(skinJoints = True, asMeta = self.d_kws['asMeta'])
                        str_partType = mModule.moduleType
                        b_isFaceModule = mModule._UTILS.isFaceModule(mModule)
                        if b_isFaceModule:
                            self._d_return['face'].extend(l_buffer)
                        if not l_buffer:
                            raise StandardError,"No joints found"
                        self.log_info("Module : {0} | type: {1} | isFaceModule {2}".format(mModule.p_nameShort,mModule.moduleType, b_isFaceModule)) 			

                        for key in d_bindJointKeys_to_matchData.keys():
                            if key in l_stopMatch:#...if we already matched this one specifically
                                continue
                            #self.log_info("checking {0}".format(key))
                            d_buffer = d_bindJointKeys_to_matchData[key]
                            if d_buffer.get('ignoreCheck'):
                                continue

                            l_ignore = d_buffer.get('l_ignore') or []
                            is_module = d_buffer.get('isModule') or None
                            l_indexArgs = d_buffer.get('indexArgs') or []

                            _faceModuleOK = d_buffer.get('faceModuleOK') or True
                            _faceModuleOnly = d_buffer.get('faceModuleOnly') or False

                            if not _faceModuleOK and b_isFaceModule:
                                #self.log_info("Face modules not okay. This one is.")				    				
                                continue

                            if _faceModuleOnly and not b_isFaceModule:

                                continue

                            if is_module and is_module != str_partType:
                                #self.log_info("Wrong module type. isModule check on")
                                continue
                            if l_ignore:
                                if str_partType in l_ignore:
                                    #self.log_info("Module type in igore list.")				    
                                    continue

                            self._d_return[key].extend(l_buffer)

                            for a in l_indexArgs:
                                if str_partType == a[0]:
                                    self._d_return[key] = [(l_buffer[int(a[1])])]
                                    self.log_info("indexArg match found for {0}".format(key))				    
                                    l_stopMatch.append(key)
                    except Exception,error:
                        self.log_error("Module '{0}' | error: {1}".format(mModule.p_nameShort,error))	
            except Exception,error:raise Exception,"Gather joints | error: {0}".format(error)		
            self.log_infoDict(self._d_return,"Return Dict")
            return self._d_return	    
    return fncWrap(*args,**kws).go()

def mirror_do(*args,**kws):
    '''
    Factory Rewrite of mirror functions.
    TODO -- replace the many mirror functions here
    '''
    class fncWrap(PuppetFunc):
        def __init__(self,*args,**kws):
            """
            """	
            super(fncWrap, self).__init__(*args,**kws)
            #self._b_reportTimes = True
            self._l_ARGS_KWS_DEFAULTS = [_d_KWARG_mPuppet,
                                         {'kw':'mode',"default":'anim','help':"Special mode for this fuction","argType":"string"},
                                         {'kw':'mirrorMode',"default":'symLeft','help':"Special mode for this fuction","argType":"string"}] 
            self.__dataBind__(*args,**kws)
            self._str_funcName = "puppet.mirror_do('{0}')".format(self._mi_puppet.cgmName,self.d_kws.get('mode') or None)		    	    
            self.__updateFuncStrings__()
            self.l_funcSteps = [{'step':'Verify','call':self._fncStep_validate_},
                                {'step':'Process','call':self._fncStep_process_}]	

        def _fncStep_validate_(self):
            try:		
                l_modes = ['template']
                str_mode = self.d_kws['mode']
                self.str_mode = cgmValid.stringArg(str_mode,noneValid=False,calledFrom = self._str_funcName)
                if self.str_mode not in l_modes:
                    raise ValueError,"Mode : {0} not in list: {1}".format(str_mode,l_modes)
            except Exception,error: raise Exception,"Mode validate | error: {0}".format(error)

            try:
                l_mirrorModes = ['symLeft','symRight']
                self.str_mirrorMode = cgmValid.stringArg(self.d_kws['mirrorMode'],noneValid=False,calledFrom = self._str_funcName)
                if self.str_mirrorMode not in l_mirrorModes:
                    raise ValueError,"Mode : {0} not in list: {1}".format(self.str_mirrorMode,l_mirrorModes)
            except Exception,error: raise Exception,"Mirror Mode validate | error: {0}".format(error)	    

            self.ml_modules = getModules(self._mi_puppet)

        def _fncStep_process_(self):
            """
            """

            try:
                ml_controls = []
                for mModule in self.ml_modules:
                    try:
                        ml_moduleControls = mModule.get_controls(mode = self.d_kws['mode'])
                        if not ml_moduleControls:
                            raise StandardError,"No controls found"
                        ml_controls.extend(ml_moduleControls)
                    except Exception,error:
                        raise Exception,"Module '{0}' | error: {1}".format(mModule.p_nameShort,error)		
            except Exception,error:raise Exception,"Gather controls | error: {0}".format(error)		

            if ml_controls:
                l_controls = [mObj.mNode for mObj in ml_controls]
                _str_mrrMd = self.str_mirrorMode
                if _str_mrrMd == 'symLeft':
                    r9Anim.MirrorHierarchy().makeSymmetrical(l_controls,mode = '',primeAxis = "Left" )
                elif _str_mrrMd == 'symRight':
                    r9Anim.MirrorHierarchy().makeSymmetrical(l_controls,mode = '',primeAxis = "Left" )
                else:
                    raise StandardError,"Don't know what to do with this mode: {0}".format(self.str_mirrorMode)
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
            self._str_funcName = "puppet.get_mirrorIndexDict('%s')"%self._mi_puppet.cgmName
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
	    self._str_funcName = "puppet.getModules('%s')"%self._mi_puppet.cgmName	
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