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
from Red9.core import Red9_CoreUtils as r9Core

# From cgm ==============================================================
from cgm.core import cgm_Meta as cgmMeta
from cgm.core.cgmPy import validateArgs as VALID
from cgm.lib import (search,attributes,lists,cgmMath)
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
        self._l_callSelection = mc.ls(sl=True) or []
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

def state_set(*args,**kws):
    class fncWrap(PuppetFunc):
        def __init__(self,*args,**kws):
            """
            """	
            super(fncWrap, self).__init__(*args,**kws)
            self._b_reportTimes = True
            self._str_funcName = "state_set('%s')"%self._mi_puppet.cgmName
            self._l_ARGS_KWS_DEFAULTS = [_d_KWARG_mPuppet,
                                        {'kw':'stateArg',"default":None,'help':"What state is desired","argType":"int/string"},
                                        {'kw':'rebuildFrom',"default":None,'help':"State to rebuild from","argType":"int/string"}]

            self.__dataBind__(*args,**kws)
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
                    #mModule.stateCheck(self.d_kws['arg'],**kws)
                    mModule.setState(self.d_kws['stateArg'], self.d_kws['rebuildFrom'])
                    self.log_info(mModule)
                except Exception,error: log.error("%s module: %s | %s"%(self._str_reportStart,_str_module,error))
    return fncWrap(*args,**kws).go()


def get_report(self, moduleReport = False, rigReport = False):
    _str_func = 'get_report'
    ml_modules = getModules(self)
    int_lenModules = len(ml_modules)
    
    _b_rigReport = VALID.boolArg(rigReport,calledFrom=_str_func)
    _b_moduleReport = VALID.boolArg(moduleReport,calledFrom=_str_func)   
    
    if not _b_rigReport and not _b_moduleReport:
        log.error("|{0}| >> No options selected".format(_str_func))     
        return False
    
    if _b_moduleReport:
        log.info("|{0}| >> Module Report".format(_str_func) + cgmGeneral._str_hardBreak)     

        for i,mModule in enumerate(ml_modules):
            _str_module = mModule.p_nameShort
            mi_rigNull = mModule.rigNull
            mi_templateNull = mModule.templateNull
            #self.progressBar_set(status = "Module Report: '%s' "%(_str_module),progress = i, maxValue = int_lenModules)

            print("'{0}' | state: '{1}' | template version: {2} | rig version: {3}".format(mModule.p_nameShort,
                                                                                           cgmGeneral._l_moduleStates[mModule.getState()],
                                                                                           mi_templateNull.getMayaAttr('version'),
                                                                                           mi_rigNull.getMayaAttr('version')))
        
    for mModule in ml_modules:
        if _b_rigReport:
            if mModule.isRigged():
                mModule.atFactory('rig_getReport')
            else:
                print("|{0}| >> Module not rigged: {1}".format(_str_func,mModule.p_nameShort))     
                

    
def get_report2(*args,**kws):
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

                _b_rigReport = VALID.boolArg(self.d_kws['rigReport'],calledFrom=self._str_reportStart)
                _b_moduleReport = VALID.boolArg(self.d_kws['moduleReport'],calledFrom=self._str_reportStart)

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

def getGeo(self,*args,**kws):
    _res = []
    for mObj in self.masterNull.geoGroup.getDescendents(asMeta = True):
        if mObj.getMayaType() in geoTypes:
            _res.append(mObj.p_nameShort)
    return _res

    """
    class fncWrap(PuppetFunc):
        def __init__(self,*args,**kws):	
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
    """

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
                except Exception,error:log.error("[mModule : %s]{%s}"%(_str_module,error))	
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
                self.log_debug("checkDict")                
                checkDict = kws.get('checkDict')
            elif len(args) == 1 and issubclass(type(args[0]),dict):
                self.log_debug("One arg, is dict")
                checkDict = args[0]
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
def templateSettings_call(*args,**kws):
    '''
    Call for doing multiple functions with templateSettings.

    :parameters:
        mode | string
            reset:reset controls
            store:store data to modules
            load:load data from modules
            query:get current data
            export:export to a pose file
            import:import from a  pose file
        filepath | string/None -- if None specified, user will be prompted
    '''
    class fncWrap(PuppetFunc):
        def __init__(self,*args,**kws):
            """
            """	
            super(fncWrap, self).__init__(*args,**kws)
            self._b_reportTimes = True
            self._str_funcName = "puppet.templateSettings_call('{0}')".format(self._mi_puppet.cgmName)		    	    
            self._l_ARGS_KWS_DEFAULTS = [_d_KWARG_mPuppet,
                                         {'kw':'mode',"default":None,'help':"Special mode for this fuction","argType":"varied"},
                                         {'kw':'filepath',"default":None,'help':"File path","argType":"string"}] 
            self.__dataBind__(*args,**kws)
            self._str_funcName = "puppet.templateSettings_call('{0}',mode = {1})".format(self._mi_puppet.cgmName,self.d_kws.get('mode',None))		    	    
            self.__updateFuncStrings__()

        def __func__(self):
            """
            """
            l_modes = 'reset','store','load','query','export','import','update','markStarterData'
            str_mode = self.d_kws['mode']
            str_mode = VALID.stringArg(str_mode,noneValid=False,calledFrom = self._str_funcName)
            
            if str_mode not in l_modes:
                self.log_error("Mode : {0} not in list: {1}".format(str_mode,l_modes))
                return False
            if str_mode is None:
                self.log_error("Mode is None. Don't know what to do with this")
                return False
            
            if str_mode in ['export','import']:
                if str_mode == 'import':
                    fileMode = 1
                else:fileMode = 0
                _filepath = VALID.filepath(self.d_kws.get('filepath'), fileMode = fileMode, fileFilter = 'Template Config file (*.pose)')
                if not _filepath:
                    self.log_error("Invalid filepath")
                    return False
                
                l_nodes = get_controls(self._mi_puppet, mode = 'template',asMeta = False)
                if not l_nodes:
                    raise ValueError,"No controls found"   
                
                if str_mode == 'import':
                    try: r9Anim.r9Pose.PoseData().poseLoad(l_nodes,_filepath,useFilter=False)#this useFilter flag 
                    except Exception,error:"import failure | {0}".format(error)  
                else:
                    try: r9Anim.r9Pose.PoseData().poseSave(l_nodes,_filepath,useFilter=False,storeThumbnail = False)#this useFilter flag 
                    except Exception,error:
                        raise Exception,"export failure | {0}".format(error)            
                return True

            ml_modules = getModules(self._mi_puppet)	    
            if not ml_modules:
                self.log_warning("'%s' has no modules"%self.cgmName)
                return False
            
            int_lenModules = len(ml_modules)
            for i,mModule in enumerate(ml_modules):
                try:
                    _str_module = mModule.p_nameShort
                    self.progressBar_set(status = "{0} Module: '{1}' ".format(str_mode,_str_module),progress = i, maxValue = int_lenModules)	    		
                    if not mModule._UTILS.templateSettings_call(mModule,str_mode):
                        self.log_error("{0} failed".format(mModule.p_nameShort))
                        return False
                except Exception,error:
                    raise Exception,"Module : '{0}' | Mode : {1} | error: {2}".format(mModule.p_nameShort,str_mode,error)
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

            #self._str_funcName = "mirrorSetup_verify('{0}',mode = '{1}')".format(self._mi_puppet.cgmName,self.d_kws.get('mode',None))		    	    
            self.__updateFuncStrings__()

        def _verifyData(self):
            """
            """
            #self.d_kws['str_side'],
            #self.str_side = cgmGeneral.verify_mirrorSideArg(self.d_kws['mirrorSideArg'],**kws)	

            l_modes = ['template','anim']
            str_mode = self.d_kws['mode']
            self.str_mode = VALID.stringArg(str_mode,noneValid=False,calledFrom = self._str_funcName)
            if self.str_mode not in l_modes:
                raise ValueError,"Mode : {0} not in list: {1}".format(str_mode,l_modes)

            self.md_data = {}
            self.ml_modules = getOrderedModules(self._mi_puppet)
            self.ml_noMatch = []
            self.d_runningSideIdxes = {'Centre':[0],
                                       'Left':[0],
                                       'Right':[0]}

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
                    #self.log_infoDict(_d,_str_module)
                #self.log_infoDict(self.d_runningSideIdxes,"Side idxs")
            except Exception,error:raise Exception,"Control Gather fail | error: {0}".format(error)

        def _process(self):
            """
            1) get a module 
            2) get controls
            3) see if has a mirror
            4) register 
            """
            ml_processed = []

            #for our first loop, we're gonna create our cull dict of sides of data to then match 
            for mModule in self.ml_modules:		
                try:#>>>Controls map
                    #self.log_info("On: {0}".format(mModule.p_nameShort))
                    if mModule in ml_processed:
                        #self.log_info("Already processed: {0}".format(mModule.p_nameShort))
                        continue       
                    
                    try:md_buffer = self.md_data[mModule.mNode]#...get the modules dict
                    except Exception,error:raise Exception,"metaDict query | error: {0}".format(error)

                    ml_modulesToDo = [mModule]#...append
                    mi_mirror = md_buffer.get('mi_mirror',False)
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

                    md_culling_controlLists = {'Centre':[],
                                                'Left':[],
                                                'Right':[]}
                    
                    for mi_module in ml_modulesToDo:
                        #self.log_info("Sub on: {0}".format(mi_module.p_nameShort))	
                        try:
                            try:md_buffer = self.md_data[mi_module.mNode]#...get the modules dict	
                            except Exception,error:raise Exception,"metaDict query | error: {0}".format(error)

                            #int_idxStart = max(self.d_runningSideIdxes[str_mirrorSide])
                            #int_idxRunning = int_idxStart + 1
                            #self.log_info("mModule: {0} | starting mirror index: {1}".format(md_buffer['str_name'],int_idxStart))

                            self.progressBar_set(status = "Verifying '{0}' ".format(md_buffer['str_name']),progress = len(ml_processed), maxValue = self.int_lenModules)		    				    
                            #str_mirrorSide = (md_buffer['str_side'])                                    
                            str_mirrorSide = cgmGeneral.verify_mirrorSideArg(mi_module.getMayaAttr('cgmDirection') or 'center')
                            #self.log_info("module: {0} | str_mirrorSide: {1}".format(mi_module.p_nameShort,str_mirrorSide))
                            for i,mObj in enumerate(md_buffer['ml_controls']):
                                try:
                                    #make sure it's a control
                                    #if not mObj.getMayaAttr('mClass') == 'cgmControl':
                                        #self.log_warning("Not a control: '{0}'".format(mObj.p_nameShort))
                                        #continue
                                    if not issubclass(type(mObj), cgmMeta.cgmControl):
                                        mObj = cgmMeta.asMeta(mObj,'cgmControl',setClass = True)#,setClass = True
                                        md_buffer[i] = mObj#...push back
                                    
                                    #before doing anything...see if we have a mirrorSide value on this object already
                                    #str_mirrorSide_obj = False                                    
                                    #if mObj.hasAttr('mirrorSide'):
                                        #str_mirrorSide_obj = mObj.getEnumValueString('mirrorSide')
                                        #if str_mirrorSide_obj != str_mirrorSide:
                                            #self.log_info("{0} has differnt mirrorSide value than module".format(mObj.p_nameShort))
                                        
                                    try:mObj._verifyMirrorable()#...veryify the mirrorsetup
                                    except Exception,error:raise Exception,"_mirrorSetup | {0}".format(error)
                                    
                                    if self.str_mode == 'template':
                                        if mObj.getMayaAttr('cgmType') in ['templateObject','templateOrientHelper','templateOrientRoot']:
                                            mObj.mirrorAxis = 'translateX,translateZ,rotateZ'                                        
                                    
                                    
                                    _mirrorSideFromCGMDirection = cgmGeneral.verify_mirrorSideArg(mObj.getNameDict().get('cgmDirection','centre'))
                                    _mirrorSideCurrent = cgmGeneral.verify_mirrorSideArg(mObj.getEnumValueString('mirrorSide'))
                                    #self.log_info("_mirrorSideFromCGMDirection: {0} ".format(_mirrorSideFromCGMDirection))
                                    #self.log_info("_mirrorSideCurrent: {0}".format(_mirrorSideCurrent))
                                    
                                    _setMirrorSide = False
                                    if _mirrorSideFromCGMDirection:
                                        if _mirrorSideFromCGMDirection != _mirrorSideCurrent:
                                            self.log_info("{0}'s cgmDirection ({1}) is not it's mirror side({2}). Resolving...".format(mObj.p_nameShort,_mirrorSideFromCGMDirection,_mirrorSideCurrent))
                                            _setMirrorSide = _mirrorSideFromCGMDirection                                            
                                    elif not _mirrorSideCurrent:
                                        _setMirrorSide = str_mirrorSide
                                        
                                    if _setMirrorSide:
                                        try:
                                            if not cgmMeta.cgmAttr(mObj,'mirrorSide').getDriver():
                                                mObj.mirrorSide = _setMirrorSide
                                                #self.log_info("{0} mirrorSide set to: {1}".format(mObj.p_nameShort,_setMirrorSide))
                                            else:
                                                pass
                                                #self.log_info("{0} mirrorSide driven".format(mObj.p_nameShort))
                                        except Exception,error:raise Exception,"_setMirrorSide : %s | %s"%(_setMirrorSide,error)
                                       
                                    #append the control to our lists to process                                    
                                    md_culling_controlLists[mObj.getEnumValueString('mirrorSide')].append(mObj)
				
                                except Exception,error:raise Exception,"'{0}' fail | error: {1}".format(mObj.p_nameShort,error)
                                
                        except Exception,error:raise Exception,"{0} fail | error: {1}".format(mi_module.p_nameShort,error)	
                        ml_processed.append(mi_module)#...append
                    
                    self.log_infoDict(md_culling_controlLists, "Culling lists")                        
                    #...Map...
                    _d_mapping = {'Centre':{'ml':md_culling_controlLists['Centre'],
                                            'startIdx':max(self.d_runningSideIdxes['Centre'])+1},
                                  'Sides':{'Left':{'ml':md_culling_controlLists['Left'],
                                                   'startIdx':max(self.d_runningSideIdxes['Left'])+1},
                                           'Right':{'ml':md_culling_controlLists['Right'],
                                                   'startIdx':max(self.d_runningSideIdxes['Right'])+1}}}                                            
                    for key,_d in _d_mapping.iteritems():
                        if key is 'Centre':
                            int_idxRunning = _d['startIdx']
                            _ml = _d['ml']
                            for mObj in _ml:
                                self.log_info("'{0}' idx:{1}".format(mObj.p_nameShort,int_idxRunning))
                                attributes.doSetAttr(mObj.mNode,'mirrorIndex',int_idxRunning)
                                self.d_runningSideIdxes['Centre'].append(int_idxRunning)
                                int_idxRunning+=1
                        else:
                            _ml_left = _d['Left']['ml']
                            _ml_right = _d['Right']['ml']
                            _ml_left_cull = copy.copy(_ml_left)
                            _ml_right_cull = copy.copy(_ml_right)                            
                            int_idxRun_left = _d['Left']['startIdx']
                            int_idxRun_right = _d['Right']['startIdx']
                            _md_tags_l = {}
                            _md_tags_r = {}
                            for mObj in _ml_left:
                                _md_tags_l[mObj] = mObj.getCGMNameTags(['cgmDirection'])
                            for mObj in _ml_right:
                                _md_tags_r[mObj] = mObj.getCGMNameTags(['cgmDirection'])
                                
                            for mObj in _ml_left:
                                #See if we can find a match
                                _match = []
                                l_tags = _md_tags_l[mObj]
                                for mObj2, r_tags in _md_tags_r.iteritems():#first try to match by tags
                                    if l_tags == r_tags:
                                        _match.append(mObj2)
                                        
                                if not _match:
                                    #Match by name
                                    _str_l_nameBase = str(mObj.p_nameBase)
                                    if _str_l_nameBase.startswith('l_'):
                                        _lookfor = 'r_' + ''.join(_str_l_nameBase.split('l_')[1:])
                                        self.log_info("Startwith check. Looking for {0}".format(_lookfor))                                        
                                        for mObj2 in _ml_right:
                                            if str(mObj2.p_nameBase) == _lookfor:
                                                _match.append(mObj2)
                                                self.log_info("Found startswithNameMatch: {0}".format(_lookfor))
                                    elif _str_l_nameBase.count('left'):
                                        _lookfor = _str_l_nameBase.replace('left','right')
                                        self.log_info("Contains 'left' check. Looking for {0}".format(_lookfor))                                                                                                                        
                                        for mObj2 in _ml_right:
                                            if str(mObj2.p_nameBase) == _lookfor:
                                                _match.append(mObj2)
                                                self.log_info("Found contains 'left name match: {0}".format(_lookfor))                                        
                                if len(_match) == 1:
                                    while int_idxRun_left in self.d_runningSideIdxes['Left'] or int_idxRun_right in self.d_runningSideIdxes['Right']:
                                        #self.log_info("Finding available indexes...")
                                        int_idxRun_left+=1
                                        int_idxRun_right+=1
                                        
                                    attributes.doSetAttr(mObj.mNode,'mirrorIndex',int_idxRun_left)
                                    attributes.doSetAttr(_match[0].mNode,'mirrorIndex',int_idxRun_right)                                    
                                    self.d_runningSideIdxes['Left'].append(int_idxRun_left)
                                    self.d_runningSideIdxes['Right'].append(int_idxRun_right)
                                    _ml_left_cull.remove(mObj)
                                    _ml_right_cull.remove(_match[0])
                                    mObj.connectChildNode(_match[0],'cgmMirrorMatch','cgmMirrorMatch')
                                    self.log_info("'{0}' idx:{1} <---Match--> '{2}' idx:{3}".format(mObj.p_nameShort,int_idxRun_left,_match[0].p_nameShort,int_idxRun_right))
                                elif len(_match)>1:
                                    raise ValueError,"Too many matches! mObj:{0} | Matches:{1}".format(mObj.p_nameShort,[mObj2.p_nameShort for mObj2 in _match])
                            for mObj in _ml_left_cull + _ml_right_cull:
                                self.ml_noMatch.append(mObj)
                                #self.log_info("NO MATCH >>>> mObj:'{0}' NO MATCH".format(mObj.p_nameShort))
                    #_l_centre = md_culling_controlLists['Centre']
                    #_l_right = md_culling_controlLists['Left']
                    #_l_left = md_culling_controlLists['Right']
                    #Centre
                    #int_idxStart = max(self.d_runningSideIdxes['Centre'])
                    #int_idxStart = max(self.d_runningSideIdxes[str_mirrorSide])
                    #int_idxRunning = int_idxStart + 1                    
                    
                    #for k in md_culling_controlLists.keys():
                except Exception,error:raise Exception,"'{0}' fail | error: {1}".format(self.md_data[mModule.mNode]['str_name'],error)

            for mObj in self.ml_noMatch:
                self.log_info("NO MATCH >>>> mObj:'{0}' NO MATCH".format(mObj.p_nameBase))
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
                if not mModule.templateSettings_call('store',*kws):
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
            raise DeprecationWarning,"Removing {0}".format(self._str_funcName)                        
            ml_modules = getModules(self._mi_puppet)	    
            if not ml_modules:
                self.log_warning("'%s' has no modules"%self.cgmName)
                return False

            for i,mModule in enumerate(ml_modules):
                if not mModule.templateSettings_call('load'):
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
            raise DeprecationWarning,"Removing {0}".format(self._str_funcName)            
            
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
            raise DeprecationWarning,"Removing {0}".format(self._str_funcName)                        
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
            _result = False
            self._mi_puppet.puppetSet.select()
            try:
                if mc.ls(sl=True):
                    ml_resetChannels.main(transformsOnly = self._d_funcKWs.get('transformsOnly'))		    
                    _result = True
                if self._l_callSelection:mc.select(self._l_callSelection)
                return _result
            except Exception,error:
                self.log_error("Failed to reset | errorInfo: {%s}"%error)
                if self._l_callSelection:mc.select(self._l_callSelection)                
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
                #mc.select(l_controls)
                if self._l_callSelection:mc.select(self._l_callSelection)
                return True
            if self._l_callSelection:mc.select(self._l_callSelection)            
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

                _b_skinJoints = VALID.boolArg(self.d_kws['skinJoints'],calledFrom=self._str_reportStart)
                _b_moduleJoints = VALID.boolArg(self.d_kws['moduleJoints'],calledFrom=self._str_reportStart)                
                _b_rigJoints = VALID.boolArg(self.d_kws['rigJoints'],calledFrom=self._str_reportStart)
                _b_select = VALID.boolArg(self.d_kws['select'],calledFrom=self._str_reportStart)

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

                _str_mode = VALID.stringArg(self.d_kws['mode'],calledFrom=self._str_reportStart)
                _b_select = VALID.boolArg(self.d_kws['select'],calledFrom=self._str_reportStart)

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
            l_return = lists.returnListNoDuplicates(l_return)
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
                                    'noScaleRoots':{},
                                    'bodyNoEyes':{'l_ignore':['eyeball']},
                                    'bodyWithLids':{'l_ignore':['eyeball','mouthNose']},
                                    'eyeballs':{'isModule':'eyeball'},
                                    'eyeballLeft':{'isModule':'eyeball',
                                                   'hasAttrs':{'cgmDirection':'left'}},
                                    'irisLeft':{'isModule':'eyeball',
                                                'hasAttrs':{'cgmName':'iris','cgmDirection':'left'}},  
                                    'pupilLeft':{'isModule':'eyeball',
                                                 'hasAttrs':{'cgmName':'pupil','cgmDirection':'left'}},                                    
                                    'eyeballRight':{'isModule':'eyeball',
                                                   'hasAttrs':{'cgmDirection':'right'}}, 
                                    'irisRight':{'isModule':'eyeball',
                                                 'hasAttrs':{'cgmName':'iris','cgmDirection':'right'}},  
                                    'pupilRight':{'isModule':'eyeball',
                                                  'hasAttrs':{'cgmName':'pupil','cgmDirection':'right'}},                                    
                                    'head':{'indexArgs':[['neckHead',-1]]},
                                    'teethUpr':{'isModule':'mouthNose',
                                                'hasAttrs':{'cgmName':'teeth','cgmPosition':'upper'}},
                                    'jaw':{'isModule':'mouthNose',
                                                'hasAttrs':{'cgmName':'jaw'}},                                    
                                    'teethLwr':{'isModule':'mouthNose',
                                                'hasAttrs':{'cgmName':'teeth','cgmPosition':'lower'}},
                                    'eyeOrbLeft':{'isModule':'eyeball',
                                                 'hasAttrs':{'cgmName':'eyeOrb','cgmDirection':'left'}},
                                    'eyeOrbRight':{'isModule':'eyeball',
                                                   'hasAttrs':{'cgmName':'eyeOrb','cgmDirection':'right'}},                                      
                                    'tongue':{'isModule':'mouthNose',
                                              'hasAttrs':{'cgmName':'tongue'}}}   
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
                            self.log_error("No joints found on {0}".format(mModule.p_nameShort))
                            continue
                        
                        self.log_info("Module : {0} | type: {1} | isFaceModule {2}".format(mModule.p_nameShort,mModule.moduleType, b_isFaceModule)) 			

                        for key in d_bindJointKeys_to_matchData.keys():
                            l_use = copy.copy(l_buffer)
                            self.log_debug("--- Checking {0}...".format(key))
                            if key in l_stopMatch:#...if we already matched this one specifically
                                self.log_debug("--- {0} in stop match".format(key))
                                continue
                            
                            #self.log_info("checking {0}".format(key))
                            d_buffer = d_bindJointKeys_to_matchData[key]
                            for k1 in d_buffer.keys():
                                self.log_debug("--- {0} : {1}".format(k1,d_buffer[k1]))
                            self.log_debug(cgmGeneral._str_subLine)
                            
                            if d_buffer.get('ignoreCheck'):
                                self.log_debug("--- ignoreCheck hit")                                
                                continue

                            l_ignore = d_buffer.get('l_ignore', [])
                            is_module = d_buffer.get('isModule', None)
                            l_indexArgs = d_buffer.get('indexArgs', [])
                            hasAttrs = d_buffer.get('hasAttrs',{})

                            _faceModuleOK = d_buffer.get('faceModuleOK', True)
                            _faceModuleOnly = d_buffer.get('faceModuleOnly', False)                          
                            if _faceModuleOK == False and b_isFaceModule:
                                self.log_debug("--- Face modules not okay. This one is.")				    				
                                continue

                            if _faceModuleOnly and not b_isFaceModule:
                                self.log_debug("--- Not a face module. Face Module only")				    				                                
                                continue

                            if is_module is not None and is_module != str_partType:
                                self.log_debug("--- Wrong module type. isModule check on")
                                continue
                            
                            if l_ignore:
                                if str_partType in l_ignore:
                                    self.log_debug("--- Module type in ignore list.")				    
                                    continue
                                
                            if hasAttrs:
                                l_ = []
                                for mJnt in l_use:
                                    _good = False   
                                    if key == 'noScaleRoots':
                                        if mJnt.hasAttr('scaleJoint'):
                                            continue
                                    for a1 in hasAttrs.keys():
                                        if mJnt.getMayaAttr(a1) == hasAttrs[a1]:
                                            self.log_debug("--- '{0}' hasAttrs match '{1}' == '{2}'".format(mJnt.p_nameShort,a1,hasAttrs[a1]))                                            
                                            _good = True
                                        elif search.findRawTagInfo(mJnt.mNode, a1) == hasAttrs[a1]:
                                            self.log_debug("--- '{0}' tag check hasAttrs match '{1}' == '{2}'".format(mJnt.p_nameShort,a1,hasAttrs[a1]))                                            
                                            _good = True                                            
                                        else:
                                            #self.log_info("--- '{0}' hasAttrs !match! '{1}' != '{2}'".format(mJnt.p_nameShort,a1,hasAttrs[a1]))                                                                                        
                                            _good = False
                                            break
                                    if _good:l_.append(mJnt)
                                l_use = l_
                                
                            if self.d_kws['asMeta']:
                                self._d_return[key].extend(l_use)
                            else:
                                self._d_return[key].extend([mJnt.mNode for mJnt in l_use])

                            for a in l_indexArgs:
                                if str_partType == a[0]:
                                    self._d_return[key] = [(l_use[int(a[1])])]
                                    self.log_debug("--- indexArg match found for {0}".format(key))				    
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
            self._str_funcName = "puppet.mirror_do('{0}')".format(self._mi_puppet.cgmName,self.d_kws.get('mode', None))		    	    
            self.__updateFuncStrings__()
            self.l_funcSteps = [{'step':'Verify','call':self._fncStep_validate_},
                                {'step':'Process','call':self._fncStep_process_}]	

        def _fncStep_validate_(self):
            try:		
                l_modes = ['template','anim']
                str_mode = self.d_kws['mode']
                self.str_mode = VALID.stringArg(str_mode,noneValid=False,calledFrom = self._str_funcName)
                if self.str_mode not in l_modes:
                    raise ValueError,"Mode : '{0}' not in list: {1}".format(str_mode,l_modes)
            except Exception,error: raise Exception,"Mode validate | error: {0}".format(error)

            try:
                l_mirrorModes = ['symLeft','symRight']
                self.str_mirrorMode = VALID.stringArg(self.d_kws['mirrorMode'],noneValid=False,calledFrom = self._str_funcName)
                if self.str_mirrorMode not in l_mirrorModes:
                    raise ValueError,"Mode : '{0}' not in list: {1}".format(self.str_mirrorMode,l_mirrorModes)
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
                            self.log_warning("No controls found on '{0}".format(mModule.p_nameShort))
                        else:
                            ml_controls.extend(ml_moduleControls)
                    except Exception,errors:
                        raise Exception,"Module '{0}' | error: {1}".format(mModule.p_nameShort,error)		
            except Exception,error:raise Exception,"Gather controls | error: {0}".format(error)		

            if ml_controls:
                l_controls = [mObj.mNode for mObj in ml_controls]
                _str_mrrMd = self.str_mirrorMode
                if _str_mrrMd == 'symLeft':
                    r9Anim.MirrorHierarchy().makeSymmetrical(l_controls,mode = '',primeAxis = "Left" )
                elif _str_mrrMd == 'symRight':
                    r9Anim.MirrorHierarchy().makeSymmetrical(l_controls,mode = '',primeAxis = "Right" )
                else:
                    raise StandardError,"Don't know what to do with this mode: {0}".format(self.str_mirrorMode)
                
                if self.str_mode == 'template':#after that pass, we'll do our template xform pass
                    self.log_info("Template mirror mode!")
                    if _str_mrrMd == 'symLeft':
                        _lookingFor = 1
                    else:
                        _lookingFor = 2#right
                    for mObj in ml_controls:
                        if mObj.mirrorSide == _lookingFor:
                            dag_match = mObj.getMessage('cgmMirrorMatch')
                            if not dag_match:
                                self.log_error("Failed to find cgmMirrorMatch for: {0}".format(mObj.p_nameShort))
                                continue
                            _xDat = mc.xform(mObj.mNode,q = True, ws= True, t = True)
                            _xDat = cgmMath.multiplyLists([_xDat,[-1,1,1]])
                            mc.xform(dag_match, ws=True, t = _xDat)

                
                #mc.select(l_controls)
                if self._l_callSelection:mc.select(self._l_callSelection)                
                return True
            
            if self._l_callSelection:mc.select(self._l_callSelection)            
            return False
        
        def templateMirror(self, nodes = None, mode = None, primeAxis = None):
            self.log_info("templateMirror Mode!")
            mi_mirror = r9Anim.MirrorHierarchy()#...get our instantiation
            
            mi_mirror.getMirrorSets(nodes)
                
            if not mi_mirror.indexednodes:
                raise IOError('No nodes mirrorIndexed nodes found from given / selected nodes')
            
            if mode == 'Anim':
                transferCall = mi_mirror.transferCallKeys  # AnimFunctions().copyKeys
                inverseCall = r9Anim.AnimFunctions.inverseAnimChannels
                mi_mirror.mergeLayers=True
            else:
                transferCall = mi_mirror.transferCallAttrs  # AnimFunctions().copyAttributes
                inverseCall = r9Anim.AnimFunctions.inverseAttributes
                mi_mirror.mergeLayers=False
                
            if primeAxis == 'Left':
                masterAxis = 'Left'
                slaveAxis = 'Right'
            else:
                masterAxis = 'Right'
                slaveAxis = 'Left'
                
            with r9Anim.AnimationLayerContext(mi_mirror.indexednodes, mergeLayers=mi_mirror.mergeLayers, restoreOnExit=False):
                for index, masterSide in mi_mirror.mirrorDict[masterAxis].items():
                    log.info("{0} | {1}".format(index, masterSide))
                    if not index in mi_mirror.mirrorDict[slaveAxis].keys():
                        log.warning('No matching Index Key found for %s mirrorIndex : %s >> %s' % \
                                    (masterAxis, index, r9Core.nodeNameStrip(masterSide['node'])))
                    else:
                        slaveData = mi_mirror.mirrorDict[slaveAxis][index]
                        log.debug('SymmetricalPairs : %s >> %s' % (r9Core.nodeNameStrip(masterSide['node']), \
                                             r9Core.nodeNameStrip(slaveData['node'])))
                        transferCall([masterSide['node'], slaveData['node']], **mi_mirror.kws)
                        
                        log.debug('Symmetrical Axis Inversion: %s' % ','.join(slaveData['axis']))
                        if slaveData['axis']:
                            inverseCall(slaveData['node'], slaveData['axis'])
                            
            #For the master side, get the xform translate data, flip it, push it back
            

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
            if self._l_callSelection:mc.select(self._l_callSelection)                
            
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
                if self._l_callSelection:mc.select(self._l_callSelection)                                    
                return True
            except Exception,error:
                self.log_error(error)  
                return False	    	
    return fncWrap(*args,**kws).go()