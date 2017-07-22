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
from cgm.core.cgmPy import validateArgs as cgmValid
from cgm.core import cgm_Meta as cgmMeta
from cgm.core.rigger import TemplateFactory as tFactory
from cgm.core.rigger import JointFactory as jFactory
from cgm.core.rigger import RigFactory as mRig
from cgm.lib import (modules,curves,distance,cgmMath,attributes,search,constraints,lists)
from cgm.lib.ml import ml_resetChannels

from cgm.core.lib import (nameTools)
from cgm.core.classes import DraggerContextFactory as dragFactory

from cgm.lib.ml import (ml_breakdownDragger,
                        ml_resetChannels)

##>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Shared libraries
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
_l_moduleStates = cgmGeneral._l_moduleStates
__l_modulesClasses__ = ['cgmModule','cgmLimb','cgmEyeball','cgmEyelids','cgmEyebrow','cgmMouthNose','cgmSimpleBSFace']
__l_faceModules__ = ['eyebrow','eyelids','eyeball','mouthNose','simpleFace']
__l_passThroughModules__ = ['simpleFace']
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
        self._l_callSelection = mc.ls(sl=True) or []
        self._b_ExceptionInterupt = False
        self._l_ARGS_KWS_DEFAULTS = [_d_KWARG_mModule]	
        #=================================================================

def exampleWrap(*args,**kws):
    class fncWrap(ModuleFunc):
        def __init__(self,*args,**kws):
            """
            """
            super(fncWrap, self).__init__(*args, **kws)
            self._str_funcName= "exampleWrap({0})".format(self._str_moduleName)
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
            self._str_funcName = "isSized({0})".format(self._str_moduleName)
            self.__dataBind__(*args,**kws)
            #=================================================================
        def __func__(self): 
            mi_module = self._mi_module
            
            if mi_module.moduleType in __l_passThroughModules__:
                self.log_debug("Pass through module found...")
                return True
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
            self._str_funcName = "deleteSizeInfo({0})".format(self._str_moduleName)
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
            self._str_funcName= "doSize({0})".format(self._str_moduleName)	
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
            self._str_funcName = "doSetParentModule({0})".format(self._str_moduleName)
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
                self.log_warning("'{0}' is not a recognized module type".format(moduleParent.mClass))
                return False

            if not moduleParent.hasAttr('moduleChildren'):#Quick check
                self.log_warning("'{0}'doesn't have 'moduleChildren' attr".format(moduleParent.getShortName()))#if it doesn't initialize, nothing is there		
                return False	
            buffer = copy.copy(moduleParent.getMessage('moduleChildren',False)) or []#Buffer till we have have append functionality	
            ml_moduleChildren = moduleParent.moduleChildren

            if mi_module in ml_moduleChildren:
                self.log_warning("already connnected to '{0}'".format(moduleParent.getShortName()))
                if mi_module.moduleParent is not moduleParent:
                    mi_module.connectParentNode(moduleParent,'moduleParent')
                return
            else:
                try:#Connect ==========================================================================================
                    buffer.append(mi_module.mNode) #Revist when children has proper add/remove handling
                    moduleParent.moduleChildren = buffer
                    mi_module.moduleParent = moduleParent.mNode
                    #self.log_info("parent set to: '%s'!"%moduleParent.getShortName())    
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
            self._str_funcName = "getGeneratedCoreNames({0})".format(self._str_moduleName)			    
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
            partName = nameTools.returnRawGeneratedName(mi_module.mNode,ignore=['cgmType','cgmTypeModifier','cgmDirection'])

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
            self._str_funcName= "settings_toggleTemplateVis({0})".format(self._str_moduleName)	
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
            self._str_funcName= "doRig({0})".format(self._str_moduleName)	
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
            
            try:
                mi_module.modulePuppet.masterControl.controlSettings.__setattr__("{0}_tmpl".format(mi_module.getPartNameBase()),0)
            except Exception,error:
                self.log_error("Failed to turn off template vis attribute | {0}".format(error))
                
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
            self._str_funcName= "isRigged({0})".format(self._str_moduleName)	
            self.__dataBind__(*args,**kws)	
        def __func__(self):
            kws = self.d_kws
            mi_module = self._mi_module
            
            if mi_module.moduleType in __l_passThroughModules__:
                self.log_debug("Pass through module found...")
                return True
            
            mi_rigNull = mi_module.rigNull
            str_shortName = self._str_moduleName
            
            if mi_rigNull.hasAttr('ignoreRigCheck') and mi_rigNull.ignoreRigCheck:
                self.log_info("Ignoring rig check")
                return True

            if not isSkeletonized(**kws):
                self.log_debug("%s Not skeletonized"%self._str_reportStart)
                return False   
            
            #ml_rigJoints = mi_rigNull.msgList_get('rigJoints',asMeta = True)
            l_rigJoints = get_joints(mi_module,rigJoints = True, asMeta=False)            
            #l_rigJoints = [i_j.p_nameShort for i_j in ml_rigJoints] or []
            l_skinJoints = get_joints(mi_module,skinJoints = True, asMeta=False)

            if not l_skinJoints or not l_rigJoints:
                self.log_debug("Necessary chains not found")
                mi_rigNull.version = ''#clear the version	
                return False

            #See if we can find any constraints on the rig Joints
            if mi_module.moduleType.lower() in __l_faceModules__:
                self.log_warning("Need to find a better face rig joint test rather than constraints")	    
            else:
                b_foundConstraint = False
                for i,jnt in enumerate(l_rigJoints):
                    if cgmMeta.cgmObject(jnt).getConstraintsTo():
                        b_foundConstraint = True
                        break
                    elif i == (len(l_rigJoints) - 1) and not b_foundConstraint:
                        self.log_warning("No rig joints are constrained")	    
                        return False

            if len( l_skinJoints ) < len( l_rigJoints ):
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
            self._str_funcName= "rigDelete({0})".format(self._str_moduleName)	
            self.__dataBind__(*args,**kws)	
            #=================================================================

        def __func__(self):
            try:#Query ========================================================
                mi_module = self._mi_module
                kws = self.d_kws		
            except Exception,error:raise StandardError,"[Query]{%s}"%error

            #if not isRigged(self):
                #raise StandardError,"module.rigDelete('%s')>>>> Module not rigged"%(str_shortName)
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
            
            ml_skinJoints = get_joints(self._mi_module,skinJoints = True,asMeta = True)
            for mObj in ml_skinJoints:
                mObj.rotate = [0,0,0]
                mObj.scale = [1,1,1]
            return True   
    return fncWrap(*args,**kws).go()

def isRigConnected(*args,**kws):
    class fncWrap(ModuleFunc):
        def __init__(self,*args,**kws):
            """
            """
            super(fncWrap, self).__init__(*args, **kws)
            self._str_funcName= "isRigConnected({0})".format(self._str_moduleName)	
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
            self._str_funcName= "rigConnect({0})".format(self._str_moduleName)	
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
                        #scConstBuffer = mc.scaleConstraint(ml_rigJoints[i].mNode,i_jnt.mNode,maintainOffset=True,weight=1) 
                        #if 'eyeOrb' not in _str_joint:
                            #for str_a in 'xyz':
                                #attributes.doConnectAttr('%s.s%s'%(i_jnt.parent,str_a),'%s.offset%s'%(scConstBuffer[0],str_a.capitalize()))			    
                                ##attributes.doConnectAttr('%s.s%s'%(mi_faceDeformNull.mNode,str_a),'%s.offset%s'%(scConstBuffer[0],str_a.capitalize()))
                    else:
                        pntConstBuffer = mc.pointConstraint(ml_rigJoints[i].mNode,i_jnt.mNode,maintainOffset=True,weight=1)        
                        orConstBuffer = mc.orientConstraint(ml_rigJoints[i].mNode,i_jnt.mNode,maintainOffset=True,weight=1) 
                        #scConstBuffer = mc.scaleConstraint(ml_rigJoints[i].mNode,i_jnt.mNode,maintainOffset=True,weight=1)                         
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
            self._str_funcName= "rigDisconnect({0})".format(self._str_moduleName)	

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
            mc.select(mi_module.rigNull.msgList_get('controlsAll',asMeta = False))
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
                    #if not _b_faceState:attributes.doBreakConnection("%s.scale"%_str_joint)
                    attributes.doBreakConnection("%s.scale"%_str_joint)
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
            self._b_reportTimes = 1
            self._str_funcName= "rig_getSkinJoints({0})".format(self._str_moduleName)
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
            self._str_funcName= "rig_getHandleJoints({0})".format(self._str_moduleName)
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
            self._str_funcName= "rig_getRigHandleJoints({0})".format(self._str_moduleName)
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
            self._str_funcName= "isTemplated({0})".format(self._str_moduleName)	
            self.__dataBind__(*args,**kws)	
            #=================================================================
        def __func__(self):
            """
            """
            try:#Query ========================================================
                mi_module = self._mi_module
                kws = self.d_kws		
            except Exception,error:raise StandardError,"[Query]{%s}"%error
            if mi_module.moduleType in __l_passThroughModules__:
                self.log_debug("Pass through module found...")
                return True
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
                    if not mi_module.templateNull.msgList_get(attr,asMeta=False):
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
            self._str_funcName= "doTemplate({0})".format(self._str_moduleName)	
            self.__dataBind__(*args,**kws)	
            #=================================================================

        def __func__(self,**kws):
            try:#Query ========================================================
                mi_module = self._mi_module
                kws = self.d_kws		
            except Exception,error:raise StandardError,"[Query]{%s}"%error
            
            if mi_module.getMessage('helper'):
                self.log_info("Have helper object, am templated.")
                return True

            if not isSized(**kws):
                self.log_warning("Not sized")
                return False   
            
            tFactory.go(**kws)     

            try:
                mi_module.modulePuppet.masterControl.controlSettings.__setattr__("{0}_tmpl".format(mi_module.getPartNameBase()),1)
            except Exception,error:
                self.log_error("Failed to turn on template vis attribute | {0}".format(error))
            
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
            self._str_funcName= "deleteTemplate({0})".format(self._str_moduleName)	
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

def template_update(*args,**kws):
    class fncWrap(ModuleFunc):
        def __init__(self,*args,**kws):
            """
            """
            super(fncWrap, self).__init__(*args, **kws)
            self._b_ExceptionInterupt = True
            self._str_funcName= "template_update({0})".format(self._str_moduleName)	
            self._l_ARGS_KWS_DEFAULTS =  [_d_KWARG_mModule,
                                          {'kw':'saveTemplatePose',"default":False,'help':"Whether to save the pose before update","argType":"bool"}]		
            self.__dataBind__(*args,**kws)		    	    	    
            #=================================================================

        def __func__(self,**kws):
            try:#Query ========================================================
                mi_module = self._mi_module
                kws = self.d_kws		
            except Exception,error:raise StandardError,"[Query]{%s}"%error

            #if not mi_module.isSized():
                #log.warning("'%s' not sized. Can't update"%mi_module.getShortName())
                #return False

            if not mi_module.isTemplated():
                log.warning("'%s' not templated. Can't update"%mi_module.getShortName())
                return False

            if self.d_kws['saveTemplatePose']:
                mi_module.templateSettings_call('store')#Save our pose before destroying anything

            mi_templateNull = mi_module.templateNull
            corePosList = mi_templateNull.templateStarterData
            i_root = mi_templateNull.root
            ml_controlObjects = mi_templateNull.msgList_get('controlObjects',asMeta = True)

            #if not cgmMath.isVectorEquivalent(i_templateNull.controlObjects[0].translate,[0,0,0]):
                #raise StandardError,"updateTemplate: doesn't currently support having a moved first template object"
                #return False
            try:
                mc.xform(i_root.parent, translation = corePosList[0],worldSpace = True)
                #mc.xform(ml_controlObjects[0].parent, translation = corePosList[0],worldSpace = True)
            except Exception,error:
                try:self.log_error("root.parent : {0}".format(i_root.parent))
                except:pass
                try:self.log_error("ml_controlObjects[0] : {0}".format(ml_controlObjects[0].mNode))
                except:pass			
                try:self.log_error("ml_controlObjects[0].parent : {0}".format(ml_controlObjects[0].parent))
                except:pass	
                try:self.log_error("corePosList[0] : {0}".format(corePosList[0]))
                except:pass			
                raise Exception,"root move fail | {0}".format(error)

            try:
                for i,i_obj in enumerate(ml_controlObjects[1:]):
                    try:
                        self.log_debug("On {0}...".format(i_obj.p_nameShort))
                        try:
                            if i_obj.parent:
                                objConstraints = constraints.returnObjectConstraints(i_obj.parent)
                                if objConstraints:mc.delete(objConstraints) 
                        except Exception,error:raise Exception,"Constraints clear fail | {0}".format(error)
                        '''
			try:
			    buffer = search.returnParentsFromObjectToParent(i_obj.mNode,i_root.mNode)
			    i_obj.parent = False
			    if buffer:mc.delete(buffer)
			except Exception,error:raise Exception,"Parent fail | {0}".format(error)
			'''  
                        try:mc.xform(i_obj.parent, translation = corePosList[1:][i],worldSpace = True)
                        except Exception,error:raise Exception,"final Move fail | {0}".format(error)

                    except Exception,error:
                        self.log_error("current obj : {0}".format(i_obj))
                        self.log_error("current parent : {0}".format(i_obj.parent))			
                        self.log_error("ml_controlObjects: {0}".format(ml_controlObjects))
                        raise Exception,"obj {0} fail | {1}".format(i,error)

            except Exception,error:raise Exception,"objects move fail | {0}".format(error)
            '''
	    try:
		buffer = search.returnParentsFromObjectToParent(ml_controlObjects[0].mNode,i_root.mNode)
		ml_controlObjects[0].parent = False
		if buffer:mc.delete(buffer)
	    except Exception,error:raise Exception,"reparent prep fail | {0}".format(error)
	    '''
            #tFactory.doParentControlObjects(mi_module)
            tFactory.doCastPivots(mi_module)
            #tFactory.store_curveLength(mi_module)#Store our base length before we move stuff around
            return True	    
            mi_module.templateSettings_call('load')#Restore the pose
            return True	    
    return fncWrap(*args,**kws).go()

def returnTemplateObjects(*args,**kws):
    class fncWrap(ModuleFunc):
        def __init__(self,*args,**kws):
            """
            """
            super(fncWrap, self).__init__(*args, **kws)
            self._str_funcName= "returnTemplateObjects({0})".format(self._str_moduleName)	
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
            self._str_funcName= "get_rollJointCountList({0})".format(self._str_moduleName)	
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
            self._str_funcName= "isSkeletonized({0})".format(self._str_moduleName)	
            self.__dataBind__(*args,**kws)		    
            #=================================================================
        def __func__(self,*args,**kws):
            try:#Query ========================================================
                mi_module = self._mi_module
                kws = self.d_kws		
            except Exception,error:raise StandardError,"[Query]{%s}"%error
            if mi_module.moduleType in __l_passThroughModules__:
                self.log_debug("Pass through module found...")
                return True
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
            self._str_funcName= "doSkeletonize({0})".format(self._str_moduleName)	
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
            self._str_funcName= "deleteSkeleton({0})".format(self._str_moduleName)
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
            self._str_funcName= "returnExpectedJointCount({0})".format(self._str_moduleName)	
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

            if mi_module.templateNull.getMayaAttr('rollJoints'):
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
            self._str_funcName = "isModule({0})".format(self._str_moduleName)	
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

def isRootModule(*args,**kws):
    class fncWrap(ModuleFunc):
        def __init__(self,*args,**kws):
            """
            """	
            super(fncWrap, self).__init__(*args,**kws)
            self._str_funcName = "isRootModule({0})".format(self._str_moduleName)
            self.__dataBind__(*args,**kws)
            #=================================================================
        def __func__(self): 
            mi_module = self._mi_module
            if not mi_module.getMessage('moduleParent'):
                self.log_info("No parent")
                if mi_module.getMessage('modulePuppet'):
                    self.log_info("Found puppet")                    
                    return True
            return False	 
    return fncWrap(*args,**kws).go() 

def isFaceModule(*args,**kws):
    class fncWrap(ModuleFunc):
        def __init__(self,*args,**kws):
            """
            """	
            super(fncWrap, self).__init__(*args,**kws)
            self._str_funcName = "isFaceModule({0})".format(self._str_moduleName)
            self.__dataBind__(*args,**kws)
            #=================================================================
        def __func__(self): 
            mi_module = self._mi_module
            if mi_module.moduleType in __l_faceModules__:
                return True
            return False	 
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
            self._str_funcName= "getState({0})".format(self._str_moduleName)	
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
            self._str_funcName= "setState({0})".format(self._str_moduleName)	

            self._l_ARGS_KWS_DEFAULTS = [_d_KWARG_mModule,
                                         {'kw':'stateArg',"default":None,'help':"What state is desired","argType":"int/string"},
                                         {'kw':'rebuildFrom',"default":None,'help':"State to rebuild from","argType":"int/string"}] 		
            self.__dataBind__(*args,**kws)		    
            #=================================================================
        def __func__(self,*args,**kws):
            """
            """
            #self.log_warning("<<<<<<<< This module needs to be updated")
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
            self._str_funcName = "checkState({0})".format(self._str_moduleName)	
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
            self._str_funcName= "changeState({0})".format(self._str_moduleName)	

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

def templateSettings_call(*args,**kws):
    _l_modes = 'reset','store','load','query','update','markStarterData'
    class fncWrap(ModuleFunc):    
        def __init__(self,*args,**kws):
            """
            All encompassing function for dealing with templateSettings
            
            d_pose = {'root':{'test':[0,1,0]},
                        'orientRootHelper':{'test':[0,1,0]},
                        'controlObjects':{0:[1,1,1]},
                        'helperObjects':{0:[]}}  
            modes:
               reset -- reset the controls to base
               store -- store current pose
               load -- load stored pose
               query -- query the pose
               update -- this mode is if the base data has been updated
               markStarterData -- this mode is for testing and will mark the base point data
            """
            super(fncWrap, self).__init__(*args, **kws)
            self._str_funcHelp = "Call to store,reset, upate, load template settings"
            self._str_funcName= "templateSettings_call({0})".format(self._str_moduleName)
            self._l_ARGS_KWS_DEFAULTS = [_d_KWARG_mModule,
                                         {'kw':'mode',"default":None,'help':"What mode this function is in","argType":"string"}]	            
            self.__dataBind__(*args,**kws)	    
            #=================================================================

        def buildDict_AnimAttrsOfObject(self, node,ignore = ['visibility']):
            attrDict = {}
            attrs = r9Anim.getSettableChannels(node,incStatics=True)
            if attrs:
                for attr in attrs:
                    if attr not in ignore:
                        try:attrDict[attr]=mc.getAttr('%s.%s' % (node,attr))
                        except:self.log_debug('%s : attr is invalid in this instance' % attr)
            return attrDict
        
        def _resetTransform_(self,obj,attr):
            try:
                default = mc.attributeQuery(attr, listDefault=True, node=obj)[0]
                mc.setAttr(obj+'.'+attr, default)
            except Exception,error:
                mc.setAttr(obj+'.'+attr, 0)	         
                
        def __func__(self):
            """
            """
            #>> Initial
            mi_module = self._mi_module
            kws = self.d_kws		
            mi_templateNull = mi_module.templateNull 
            
            if not mi_module.isTemplated():
                self.log_info("Not templated. Cannot call.")
                return False
                        
            _mode = kws.get('mode',None)
            if _mode not in _l_modes:
                self.log_error("Mode : {0} not in list: {1}".format(str_mode,_l_modes))
                return False            
            if _mode is None:
                raise ValueError,"{1} Must have a mode | {0}".format(_l_modes,self._str_funcName)
            self.log_debug("mode: '{0}'".format(_mode))
            #---------------------------------------------------------------------------------------    
            if mi_module.getMessage('helper'):
                self.log_debug("Cannot currently store pose with rigBlocks")
                return True               
            #if _mode in ['load','update']:
            try:#>>> We need to setup our value normalizer value
                #self.log_info("Distance between : {0} and {1}".format(ml_controlObjects[0].getParent(asMeta = 1).p_nameShort,ml_controlObjects[-1].getParent(asMeta = 1).p_nameShort))
                #self.f_crvLength_current = distance.returnDistanceBetweenPoints(ml_controlObjects[0].getParent(asMeta = 1).getPosition(),ml_controlObjects[-1].getParent(asMeta = 1).getPosition())		
                #self.f_crvLength_stored =  mi_templateNull.getMayaAttr('moduleBaseLength') or None
                self.f_crvLength_stored =  mi_templateNull.getMayaAttr('curveBaseLength') or None
                self.f_crvLength_current = distance.returnCurveLength(mi_templateNull.getMessage('curve')[0]) 
                #...we'll get the current values after initial reset
            except Exception,error:raise Exception,"[Validate normalize data | {0}]".format(error)                
            
            #Build our pose dict...        
            if _mode in ['query','store']:
                d_pose = self._get_poseDict()
                l_offsets = self._get_offsetData()
                if _mode == 'query':
                    self.log_infoDict(d_pose,"Pose Dict")
                    for i,d in enumerate(l_offsets):
                        self.log_debug("{0} offset: {1}".format(i,d))
                if _mode == 'store':
                    mi_templateNull.controlObjectTemplatePose = d_pose
                    mi_templateNull.doStore('offsetsData',str(l_offsets))
                return d_pose
            elif _mode == 'markStarterData':
                return self._markStarterData()
            
            elif _mode == 'reset':
                return self._resetPose()
            
            elif _mode == 'load':
                return self._loadPose()
            
            elif _mode == 'update':
                return self._updatePose()
            
        def _markStarterData(self):
            try:#Query ========================================================
                mi_module = self._mi_module 
                mi_templateNull = mi_module.templateNull                                   
                ml_controlObjects = mi_templateNull.msgList_get('controlObjects')
                if not ml_controlObjects:
                    log.error("No control objects found")
                    return False
                l_storedPosList = mi_templateNull.templateStarterData

            except Exception,err:raise Exception,"[Query]{0}".format(err)

            _locs = []
            
            for i,mObj in enumerate(ml_controlObjects):
                _locs.append(mc.spaceLocator(p=l_storedPosList[i], n = "{0}_basePos".format(mObj.p_nameBase))[0])

            return _locs  
        
        def _updatePose(self):
            """
            1) Reset roots to start data
            2) Get normalized values from the change
            3) Push back the offsets
            """
            try:#Query ========================================================
                mi_module = self._mi_module
                mi_templateNull = mi_module.templateNull                   
                d_pose = mi_templateNull.controlObjectTemplatePose
                ml_controlObjects = mi_templateNull.msgList_get('controlObjects')
                if not ml_controlObjects:
                    log.error("No control objects found")
                    return False	
                l_storedPosList = mi_templateNull.templateStarterData
                mi_root = mi_templateNull.root

            except Exception,err:raise Exception,"[Query]{0}".format(err)
            
            if self.d_kws.get('saveTemplatePose'):
                d_pose = self._get_poseDict()
                mi_templateNull.controlObjectTemplatePose = d_pose
                
            
            try:#Our first pass of positioning
                mc.xform(mi_root.parent, translation = l_storedPosList[0],worldSpace = True)
                mi_root.resetAttrs()
    
                try:#Initial positioning...
                    for i,i_obj in enumerate(ml_controlObjects):
                        try:
                            #self.log_debug("On {0}...".format(i_obj.p_nameShort))
                            '''try:
                                if i_obj.parent:
                                    objConstraints = constraints.returnObjectConstraints(i_obj.parent)
                                    if objConstraints:mc.delete(objConstraints) 
                            except Exception,error:raise Exception,"Constraints clear fail | {0}".format(error)'''
    
                            try:mc.xform(i_obj.parent, translation = l_storedPosList[i],worldSpace = True)
                            except Exception,err:raise Exception,"final Move fail | {0}".format(err)
                            
                            i_obj.resetAttrs()
    
                        except Exception,err:
                            self.log_error("current obj : {0}".format(i_obj))
                            self.log_error("current parent : {0}".format(i_obj.parent))			
                            self.log_error("ml_controlObjects: {0}".format(ml_controlObjects))
                            raise Exception,"obj {0} fail | {1}".format(i,err)
    
                except Exception,error:raise Exception,"objects move fail | {0}".format(error)
            except Exception,error:raise Exception,"First pass | {0}".format(error)

            self._resetPose()#...reset our pose first of all
            self.f_crvLength_current = distance.returnCurveLength(mi_templateNull.getMessage('curve')[0])              
            
            try:#Get our new starter data
                try:
                    l_newPosList = []
                    l_offsets = mi_templateNull.offsetsData
                    for i,pos in enumerate(l_storedPosList):
                        __normalized = [self.__normalizeValue__(v) for v in l_offsets[i]]
                        l_newPosList.append(cgmMath.list_subtract(pos,__normalized))
                        
                except Exception,err:raise Exception,"Data conversion | {0}".format(err)    
                
                mc.xform(mi_root.parent, translation = l_newPosList[0] ,worldSpace = True)
                
                for i,i_obj in enumerate(ml_controlObjects):
                    try:
                        #self.log_info("On {0}...".format(i_obj.p_nameShort))

                        try:mc.xform(i_obj.parent, translation = l_newPosList[i],worldSpace = True)
                        except Exception,err:raise Exception,"Initial fail | {0}".format(err)
                        
                        i_obj.resetAttrs()
    
                    except Exception,err:
                        raise Exception,"obj {0} fail | {1}".format(i,err)                    
                    
            except Exception,err:raise Exception,"New starter data | {0}".format(err)    
            
            #...this shouldn't happen now tFactory.store_baseLength(mi_module)#Store our base length before we move stuff around
            #self._loadPose()#...this doesn't work because of order of operations

            #>>> Get the root
            l_translates = ['translateX','translateY','translateZ']#Flag our
            for key in ['orientRootHelper']:
                try:
                    if d_pose.get(key):
                        for attr, val in d_pose[key].items():
                            #Don't think we need  to do this anymore...
                            """try:
                                val=eval(val)
                            except Exception,err:
                                self.log_error("{0} failed to eval | {1}".format(val,err))
                                pass """
                            try:
                                if attr not in l_translates:
                                    #mc.setAttr('%s.%s' % (mi_templateNull.getMessage(key)[0],attr), self.__normalizeValue__(val,attr,key))
                                #else:
                                    mc.setAttr('%s.%s' % (mi_templateNull.getMessage(key)[0],attr), val)
                            except Exception,err:
                                self.log_error(err)   
                except Exception,error:raise Exception,"key fail : {0} | {1}".format(key,error)

            for key in d_pose['controlObjects']:
                for attr, val in d_pose['controlObjects'][key].items():
                    try:
                        val=eval(val)
                    except:pass      
                    try:
                        if attr not in l_translates:
                            #mc.setAttr('%s.%s' % (ml_controlObjects[int(key)].mNode, attr), self.__normalizeValue__(val,attr,("obj{0}".format(key))))
                        #else:
                            mc.setAttr('%s.%s' % (ml_controlObjects[int(key)].mNode, attr), val)

                    except Exception,err:
                        self.log_error(err) 

            for key in d_pose['helperObjects']:
                for attr, val in d_pose['helperObjects'][key].items():
                    try:
                        val=eval(val)
                    except:pass      
                    try:
                        if ml_controlObjects[int(key)].getMessage('helper'):
                            mc.setAttr('%s.%s' % (ml_controlObjects[int(key)].getMessage('helper')[0], attr), val)
                    except Exception,err:
                        self.log_error("helperObjects '{0}' | {1}".format(attr,err))     
                        
            tFactory.doCastPivots(mi_module)#...cast our pivots 
            tFactory.store_baseLength(mi_module)#Store our base length before we move stuff around
            return True            
        
        def _loadPose(self):
            try:#Query ========================================================
                mi_module = self._mi_module
                mi_templateNull = mi_module.templateNull                   
                d_pose = mi_templateNull.controlObjectTemplatePose
                ml_controlObjects = mi_templateNull.msgList_get('controlObjects')
                if not ml_controlObjects:
                    log.error("No control objects found")
                    return False	
                l_storedPosList = mi_templateNull.templateStarterData

            except Exception,err:raise Exception,"[Query]{0}".format(err)

            if type(d_pose) is not dict:
                self.log_error("Pose dict is not a dict: {0}".format(d_pose))
                return False
            
            self.f_crvLength_current = distance.returnCurveLength(mi_templateNull.getMessage('curve')[0])           
            self._resetPose()#...reset our pose first of all

            #>>> Get the root
            l_translates = ['translateX','translateY','translateZ']#Flag our
            for key in ['root','orientRootHelper']:
                try:
                    if d_pose[key]:
                        for attr, val in d_pose[key].items():
                            #Don't think we need  to do this anymore...
                            """try:
                                val=eval(val)
                            except Exception,err:
                                self.log_error("{0} failed to eval | {1}".format(val,err))
                                pass """
                            try:
                                if attr in l_translates:
                                    mc.setAttr('%s.%s' % (mi_templateNull.getMessage(key)[0],attr), self.__normalizeValue__(val,attr,key))
                                else:
                                    mc.setAttr('%s.%s' % (mi_templateNull.getMessage(key)[0],attr), val)
                            except Exception,err:
                                self.log_error(err)   
                except Exception,error:raise Exception,"key fail : {0} | {1}".format(key,error)

            for key in d_pose['controlObjects']:
                for attr, val in d_pose['controlObjects'][key].items():
                    try:
                        val=eval(val)
                    except:pass      
                    try:
                        if attr in l_translates:
                            mc.setAttr('%s.%s' % (ml_controlObjects[int(key)].mNode, attr), self.__normalizeValue__(val,attr,("obj{0}".format(key))))
                        else:
                            mc.setAttr('%s.%s' % (ml_controlObjects[int(key)].mNode, attr), val)

                    except Exception,err:
                        self.log_error(err) 

            for key in d_pose['helperObjects']:
                for attr, val in d_pose['helperObjects'][key].items():
                    try:
                        val=eval(val)
                    except:pass      
                    try:
                        if ml_controlObjects[int(key)].getMessage('helper'):
                            mc.setAttr('%s.%s' % (ml_controlObjects[int(key)].getMessage('helper')[0], attr), val)
                    except Exception,err:
                        self.log_error("helperObjects '{0}' | {1}".format(attr,err))     
                        
            return True


        def _get_poseDict(self):
            mi_module = self._mi_module
            kws = self.d_kws		
            mi_templateNull = mi_module.templateNull   
            
            d_pose = {}
            mi_templateNull = mi_module.templateNull
            mi_templateNull.addAttr('controlObjectTemplatePose',attrType = 'string')#make sure attr exists
            #>>> Get the root
            d_pose['root'] = self.buildDict_AnimAttrsOfObject(mi_templateNull.getMessage('root')[0])
            d_pose['orientRootHelper'] = self.buildDict_AnimAttrsOfObject(mi_templateNull.getMessage('orientRootHelper')[0])
            d_pose['controlObjects'] = {}
            d_pose['helperObjects'] = {}

            for i,mi_node in enumerate(mi_templateNull.msgList_get('controlObjects')):
                d_pose['controlObjects'][str(i)] = self.buildDict_AnimAttrsOfObject(mi_node.mNode)
                if mi_node.getMessage('helper'):
                    d_pose['helperObjects'][str(i)] = self.buildDict_AnimAttrsOfObject(mi_node.helper.mNode)

            return d_pose   
        
        def _get_offsetData(self):
            """
            """
            try:#Query ========================================================
                mi_module = self._mi_module
                mi_templateNull = mi_module.templateNull                   
                ml_controlObjects = mi_templateNull.msgList_get('controlObjects')
                if not ml_controlObjects:
                    log.error("No control objects found")
                    return False	
                l_storedPosList = mi_templateNull.templateStarterData

            except Exception,err:raise Exception,"[Query]{0}".format(err)
            
            l_offsets = []

            for i,i_obj in enumerate(ml_controlObjects):
                try:
                    self.log_info("On {0}...".format(i_obj.p_nameShort))
                    try:
                        #mc.xform(i_obj.parent, translation = corePosList[i],worldSpace = True)
                        _data = mc.xform(i_obj.mNode, q = True, translation = True, worldSpace = True)
                        _base = l_storedPosList[i]
                        _offset = cgmMath.list_subtract(_base,_data)
                        l_offsets.append(_offset)
                        self.log_info("{0} | base: {1} - current:{2} = {3}".format(i_obj.p_nameShort,_base,_data,_offset))
                    except Exception,err:raise Exception,"xform query | {0}".format(err)
                    
                except Exception,err:
                    self.log_error("current obj : {0}".format(i_obj))
                    self.log_error("ml_controlObjects: {0}".format(ml_controlObjects))
                    raise Exception,"obj {0} fail | {1}".format(i,err)

            return l_offsets    
        
        def _resetPose(self):
            mi_module = self._mi_module
            mi_templateNull = mi_module.templateNull  
            
            d_pose = self._get_poseDict()
        

            #>>> Get the root
            for key in ['root','orientRootHelper']:
                try:
                    if d_pose.get(key):
                        for attr, val in d_pose[key].items():
                            try:
                                val=eval(val)
                            except:pass 
                            try:
                                self._resetTransform_(mi_templateNull.getMessage(key)[0],attr)
                            except Exception,err:
                                self.log_error(err)   
                    else:
                        self.log_error("Missing data on {0}".format(key))
                except Exception,error:raise Exception,"key fail : {0} | {1}".format(key,error)

            ml_controlObjects = mi_templateNull.msgList_get('controlObjects')
            if not ml_controlObjects:
                log.error("No control objects found")
                return False

            for key in d_pose['controlObjects'].keys():
                for attr, val in d_pose['controlObjects'][key].items():
                    try:
                        val=eval(val)
                    except:pass      

                    try:
                        self._resetTransform_(ml_controlObjects[int(key)].mNode,attr)
                    except Exception,err:
                        self.log_error(err) 

            for key in d_pose['helperObjects']:
                for attr, val in d_pose['helperObjects'][key].items():
                    try:
                        val=eval(val)
                    except:pass      
                    try:
                        if ml_controlObjects[int(key)].getMessage('helper'):
                            self._resetTransform_(ml_controlObjects[int(key)].getMessage('helper')[0],attr)			    
                    except Exception,err:
                        self.log_error("helperObjects '{0}' | {1}".format(attr,err))    
            return True
        
        def __normalizeValue__(self,value,attr = 'no attr name',obj = 'obj'):
                '''
                New concept for normalizing our values to the differential between a stored curve length and a current one
                '''
                try:
                    if self.f_crvLength_stored is not None:
                        #self.log_info("Found stored crv length. Processing...")
                        # base/value | current/x
                        # (value * current)/stored
                        buffer = ((value * self.f_crvLength_current)/self.f_crvLength_stored)
                        #self.log_info("'{0}.{1}' ...".format(obj,attr))
                        #self.log_info("Math : ({0} * {1}) / {2} = {3}".format(value,self.f_crvLength_current,self.f_crvLength_stored,buffer))
                        #self.log_info("Old: {0} | New: {1}".format(value,buffer))		    
                        return buffer
    
                    else:
                        #self.log_info("No stored crv length. Using value: {0}".format(value))
                        return value
    
                except Exception,error:raise Exception,"[__normalizeValue__ | {0}]".format(error)

    return fncWrap(*args,**kws).go()

def poseStore_templateSettings(*args,**kws):
    class fncWrap(ModuleFunc):
        def __init__(self,*args,**kws):
            """
            """
            super(fncWrap, self).__init__(*args, **kws)
            self._str_funcHelp = "Builds a template's data settings for reconstruction./nexampleDict = {'root':{'test':[0,1,0]},/n'controlObjects':{0:[1,1,1]}}"
            self._str_funcName= "poseStore_templateSettings({0})".format(self._str_moduleName)	
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
                        except:self.log_debug('%s : attr is invalid in this instance' % attr)
            return attrDict

        def __func__(self):
            """
            """
            raise DeprecationWarning,"Removing {0}".format(self._str_funcName)
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
                d_pose = {}
                mi_templateNull = mi_module.templateNull
                mi_templateNull.addAttr('controlObjectTemplatePose',attrType = 'string')#make sure attr exists
                #>>> Get the root
                d_pose['root'] = self.buildDict_AnimAttrsOfObject(mi_templateNull.getMessage('root')[0])
                d_pose['orientRootHelper'] = self.buildDict_AnimAttrsOfObject(mi_templateNull.getMessage('orientRootHelper')[0])
                d_pose['controlObjects'] = {}
                d_pose['helperObjects'] = {}

                for i,mi_node in enumerate(mi_templateNull.msgList_get('controlObjects')):
                    d_pose['controlObjects'][str(i)] = self.buildDict_AnimAttrsOfObject(mi_node.mNode)
                    if mi_node.getMessage('helper'):
                        d_pose['helperObjects'][str(i)] = self.buildDict_AnimAttrsOfObject(mi_node.helper.mNode)

                #Store it        
                mi_templateNull.controlObjectTemplatePose = d_pose
                return d_pose
            except Exception,error:
                if not mi_module.isTemplated():
                    raise StandardError,"Not templated"
                raise StandardError,"[Pose store]{%s}"%(error)   

    return fncWrap(*args,**kws).go()

def poseRead_templateSettings(*args,**kws):
    class fncWrap(ModuleFunc):
        def __init__(self,*args,**kws):
            """
            """
            super(fncWrap, self).__init__(*args, **kws)
            self._str_funcHelp = "Reads and applies template settings pose data"
            self._str_funcName= "poseRead_templateSettings({0})".format(self._str_moduleName)	
            #self.l_funcSteps = [{'step':'Gather Info','call':self._gatherInfo_},	
            self.__dataBind__(*args,**kws)	    
            #=================================================================

        def __normalizeValue__(self,value,attr = 'no attr name',obj = 'obj'):
            '''
            New concept for normalizing our values to the differential between a stored curve length and a current one
            '''
            try:
                if self.f_crvLength_stored is not None:
                    self.log_debug("Found stored crv length. Processing...")
                    # base/value | current/x
                    # (value * current)/stored
                    buffer = ((value * self.f_crvLength_current)/self.f_crvLength_stored)
                    self.log_info("'{0}.{1}' ...".format(obj,attr))
                    self.log_info("Math : ({0} * {1}) / {2} = {3}".format(value,self.f_crvLength_current,self.f_crvLength_stored,buffer))
                    self.log_info("Old: {0} | New: {1}".format(value,buffer))		    
                    return buffer

                else:
                    self.log_debug("No stored crv length. Using value: {0}".format(value))
                    return value

            except Exception,error:raise StandardError,"[__normalizeValue__ | {0}]".format(error)

        def __func__(self):
            """
            """
            raise DeprecationWarning,"Removing {0}".format(self._str_funcName)            
            try:#Query ========================================================
                mi_module = self._mi_module
                kws = self.d_kws
                mi_templateNull = mi_module.templateNull   
                d_pose = mi_templateNull.controlObjectTemplatePose
                ml_controlObjects = mi_templateNull.msgList_get('controlObjects')
                if not ml_controlObjects:
                    log.error("No control objects found")
                    return False	
                l_storedPosList = mi_templateNull.templateStarterData

            except Exception,error:raise StandardError,"[Query]{%s}"%error

            if type(d_pose) is not dict:
                self.log_error("Pose dict is not a dict: {0}".format(d_pose))
                return False

            poseReset_templateSettings(mi_module)

            try:#>>> We need to setup our value normalizer value

                ml_controlObjects
                #self.log_info("Distance between : {0} and {1}".format(ml_controlObjects[0].getParent(asMeta = 1).p_nameShort,ml_controlObjects[-1].getParent(asMeta = 1).p_nameShort))
                self.f_crvLength_current = distance.returnDistanceBetweenPoints(ml_controlObjects[0].getParent(asMeta = 1).getPosition(),ml_controlObjects[-1].getParent(asMeta = 1).getPosition())		
                self.f_crvLength_stored =  mi_templateNull.getMayaAttr('moduleBaseLength') or None

            except Exception,error:raise StandardError,"[Validate normalize data | {0}]".format(error)

            #>>> Get the root
            l_translates = ['translateX','translateY','translateZ']#Flag our
            for key in ['root','orientRootHelper']:
                try:
                    if d_pose[key]:
                        for attr, val in d_pose[key].items():
                            try:
                                val=eval(val)
                            except:pass 
                            try:
                                if attr in l_translates:
                                    mc.setAttr('%s.%s' % (mi_templateNull.getMessage(key)[0],attr), self.__normalizeValue__(val,attr,key))
                                else:
                                    mc.setAttr('%s.%s' % (mi_templateNull.getMessage(key)[0],attr), val)
                            except Exception,err:
                                self.log_error(err)   
                except Exception,error:raise Exception,"key fail : {0} | {1}".format(key,error)


            for key in d_pose['controlObjects']:
                for attr, val in d_pose['controlObjects'][key].items():
                    try:
                        val=eval(val)
                    except:pass      

                    try:
                        if attr in l_translates:
                            mc.setAttr('%s.%s' % (ml_controlObjects[int(key)].mNode, attr), self.__normalizeValue__(val,attr,("obj{0}".format(key))))
                        else:
                            mc.setAttr('%s.%s' % (ml_controlObjects[int(key)].mNode, attr), val)

                    except Exception,err:
                        self.log_error(err) 

            for key in d_pose['helperObjects']:
                for attr, val in d_pose['helperObjects'][key].items():
                    try:
                        val=eval(val)
                    except:pass      
                    try:
                        if ml_controlObjects[int(key)].getMessage('helper'):
                            mc.setAttr('%s.%s' % (ml_controlObjects[int(key)].getMessage('helper')[0], attr), val)
                    except Exception,err:
                        self.log_error("helperObjects '{0}' | {1}".format(attr,err))    
            return True
    return fncWrap(*args,**kws).go()

def poseReset_templateSettings(*args,**kws):
    class fncWrap(ModuleFunc):
        def __init__(self,*args,**kws):
            """
            """
            super(fncWrap, self).__init__(*args, **kws)
            self._str_funcName= "poseReset_templateSettings({0})".format(self._str_moduleName)	
            self.__dataBind__(*args,**kws)	    
            #=================================================================

        def _resetTransform_(self,obj,attr):
            try:
                default = mc.attributeQuery(attr, listDefault=True, node=obj)[0]
                mc.setAttr(obj+'.'+attr, default)
            except Exception,error:
                mc.setAttr(obj+'.'+attr, 0)	 

        def __func__(self):
            """
            """
            raise DeprecationWarning,"Removing {0}".format(self._str_funcName)            
            try:#Query ========================================================
                mi_module = self._mi_module
                kws = self.d_kws
                mi_templateNull = mi_module.templateNull   
                d_pose = mi_templateNull.controlObjectTemplatePose
            except Exception,error:raise StandardError,"[Query]{%s}"%error

            if type(d_pose) is not dict:
                self.log_error("Pose dict is not a dict: {0}".format(d_pose))
                return False

            #>>> Get the root
            for key in ['root','orientRootHelper']:
                try:
                    if d_pose[key]:
                        for attr, val in d_pose[key].items():
                            try:
                                val=eval(val)
                            except:pass 
                            try:
                                self._resetTransform_(mi_templateNull.getMessage(key)[0],attr)
                            except Exception,err:
                                self.log_error(err)   
                except Exception,error:raise Exception,"key fail : {0} | {1}".format(key,error)

            ml_controlObjects = mi_templateNull.msgList_get('controlObjects')
            if not ml_controlObjects:
                log.error("No control objects found")
                return False

            for key in d_pose['controlObjects']:
                for attr, val in d_pose['controlObjects'][key].items():
                    try:
                        val=eval(val)
                    except:pass      

                    try:
                        self._resetTransform_(ml_controlObjects[int(key)].mNode,attr)
                    except Exception,err:
                        self.log_error(err) 

            for key in d_pose['helperObjects']:
                for attr, val in d_pose['helperObjects'][key].items():
                    try:
                        val=eval(val)
                    except:pass      
                    try:
                        if ml_controlObjects[int(key)].getMessage('helper'):
                            self._resetTransform_(ml_controlObjects[int(key)].getMessage('helper')[0],attr)			    
                    except Exception,err:
                        self.log_error("helperObjects '{0}' | {1}".format(attr,err))    
            return True
    return fncWrap(*args,**kws).go()

#=====================================================================================================
#>>> Anim functions functions
#=====================================================================================================
def get_controls(*args,**kws):
    '''
    Simple factory for template settings functions
    '''
    class fncWrap(ModuleFunc):
        def __init__(self,*args,**kws):
            """
            """	
            super(fncWrap, self).__init__(*args,**kws)
            #self._b_reportTimes = True
            self._l_ARGS_KWS_DEFAULTS = [_d_KWARG_mModule,
                                         {'kw':'mode',"default":'anim','help':"Special mode for this fuction","argType":"varied"},
                                         cgmMeta._d_KWARG_asMeta] 
            self.__dataBind__(*args,**kws)
            self._b_reportTimes = 1
            self._str_funcName = "module.get_controls('{0}',mode = {1})".format(self._str_moduleName,self.d_kws.get('mode') or None)		    	    
            self.__updateFuncStrings__()

        def __func__(self):
            """
            """
            try:
                try:
                    mi_module = self._mi_module
                    mi_templateNull = mi_module.templateNull   
                except Exception,error: raise Exception,"Link meta fail | error: {0}".format(error)

                l_modes = 'anim','template'
                str_mode = self.d_kws['mode']
                str_mode = cgmValid.stringArg(str_mode,noneValid=False,calledFrom = self._str_funcName)
                if str_mode not in l_modes:
                    raise ValueError,"Mode : {0} not in list: {1}".format(str_mode,l_modes)
                if str_mode is None:
                    self.log_error("Mode is None. Don't know what to do with this")
                    return False

            except Exception,error: raise Exception,"Inital data fail | error: {0}".format(error)

            ml_controlObjects = []
            try:
                if str_mode == 'template':
                    if  mi_module.getMessage('helper'):
                        return mi_module.helper.get_controls(asMeta = self.d_kws['asMeta'])
                    elif mi_module.moduleType not in __l_faceModules__:
                        l_controlAttrs = 'root','orientRootHelper'
                        for str_a in l_controlAttrs:
                            buffer = mi_templateNull.getMessageAsMeta(str_a)
                            if not buffer:
                                raise ValueError,"attr '{0}' failed | buffer: {1}".format(str_a,buffer)
                            if str_a == 'root':
                                ml_controlObjects.append(cgmMeta.asMeta(buffer.parent))
                            ml_controlObjects.append(buffer)
    
                        l_msgLists = 'controlObjects','orientHelpers'
                        for str_a in l_msgLists:
                            buffer = mi_templateNull.msgList_get(str_a)
                            if not buffer:
                                raise ValueError,"attr '{0}' failed | buffer: {1}".format(str_a,buffer)
                            ml_controlObjects.extend(buffer)	

                        #Pivot check
                        try:
                            l_userAttrs = mi_templateNull.getAttrs(userDefined = True)
                            for str_a in l_userAttrs:
                                if 'pivot_' in str_a:
                                    buffer = mi_templateNull.getMessageAsMeta(str_a)
                                    self.log_info("Pivot attr {0}: {1}".format(str_a,buffer))
                                    if not buffer:
                                        raise ValueError,"attr '{0}' failed | buffer: {1}".format(str_a,buffer)
                                    else:ml_controlObjects.append(buffer)
                        except Exception,error: raise Exception,"Pivot check | error: {0}".format(error)
                elif str_mode == 'anim':
                    try:
                        #ml_controlObjects = mi_module.rigNull.moduleSet.getMetaList()
                        ml_controlObjects = mi_module.rigNull.msgList_get('controlsAll')
                    except:
                        self.log_error("No controls found.")
                        self.log_error("Rig Status: {0}".format(mi_module.isRigged()))
                        return False
                else:
                    raise StandardError,"Not done yet"
            except Exception,error: raise Exception,"Mode '{0} fail | error: {1}".format(str_mode,error)
            if not self.d_kws['asMeta']:
                return [mObj.p_nameShort for mObj in ml_controlObjects]
            return ml_controlObjects
    return fncWrap(*args,**kws).go()

def get_joints(*args,**kws):
    '''
    Simple factory for template settings functions
    
    skinJoints
    moduleJoints
    rigJoints
    '''
    class fncWrap(ModuleFunc):
        def __init__(self,*args,**kws):
            """
            """	
            super(fncWrap, self).__init__(*args,**kws)
            self._b_reportTimes = 0
            self._str_funcName = "module.get_joints('{0}')".format(self._str_moduleName)		    	                
            self._l_ARGS_KWS_DEFAULTS = [_d_KWARG_mModule,
                                         {'kw':'skinJoints',"default":False,'help':"Whether to include skin joints or not","argType":"bool"},
                                         {'kw':'moduleJoints',"default":False,'help':"Whether to include module core joints or not","argType":"bool"},                                         
                                         {'kw':'rigJoints',"default":False,'help':"Whether to include rig joints or not","argType":"bool"},
                                         cgmMeta._d_KWARG_asMeta,                                         
                                         cgmMeta._d_KWARG_select] 
            self.__dataBind__(*args,**kws)

        def __func__(self):
            try:
                try:
                    mi_module = self._mi_module
                    mi_templateNull = mi_module.templateNull  
                    mi_rigNull = mi_module.rigNull                    
                except Exception,error: raise Exception,"Link meta fail | error: {0}".format(error)

                _b_skinJoints = cgmValid.boolArg(self.d_kws['skinJoints'],calledFrom=self._str_reportStart)
                _b_moduleJoints = cgmValid.boolArg(self.d_kws['moduleJoints'],calledFrom=self._str_reportStart)                
                _b_rigJoints = cgmValid.boolArg(self.d_kws['rigJoints'],calledFrom=self._str_reportStart)
                _b_select = cgmValid.boolArg(self.d_kws['select'],calledFrom=self._str_reportStart)
                
                if not _b_skinJoints and not _b_moduleJoints and not _b_rigJoints:
                    self.log_error("Nothing set to find. Check your kws")
                    return self._SuccessReturn_(False)
            except Exception,error: raise Exception,"Inital data fail | error: {0}".format(error)
            
            l_return = []
            if _b_moduleJoints or _b_skinJoints:
                try:
                    buffer = mi_rigNull.msgList_get('moduleJoints',asMeta = False)
                except Exception,error:self.log_error("module joints fail | error: {0}".format(error))  
                if _b_skinJoints:
                    try:
                        for obj in buffer:
                            #Need to check for msgLists...
                            l_attrs = mc.listAttr(obj,ud = 1)
                            for a in l_attrs:
                                #self.log_info("Checking: {0}.{1}".format(obj,a))
                                for singleHook in mRig.__l_moduleJointSingleHooks__:
                                    if singleHook in a:
                                        bfr_single =  attributes.returnMessageObject(obj,a)
                                        if bfr_single:
                                            #self.log_info("Found '{0}' on '{1}.{2}'".format(bfr_single,obj,a))
                                            buffer.insert(buffer.index(obj) +1,bfr_single)                                    
                                
                                for msgHook in mRig.__l_moduleJointMsgListHooks__:
                                    if msgHook in a:
                                        bfr_msgHook =  attributes.returnMessageObject(obj,a)
                                        if bfr_msgHook:
                                           #self.log_info("Found '{0}' on '{1}.{2}'".format(bfr_msgHook,obj,a))                                            
                                           buffer.insert(buffer.index(obj) +1, bfr_msgHook)                                        
                    except Exception,error:self.log_error("skin joints fail | error: {0}".format(error))  
                if buffer:l_return.extend(buffer)
            if _b_rigJoints:
                try:
                    buffer = mi_rigNull.msgList_get('rigJoints',asMeta = False)
                    if buffer:l_return.extend(buffer)
                except Exception,error:self.log_error("rig joints fail | error: {0}".format(error)) 
                
            if not l_return:
                return []
            elif _b_select:
                l_return = lists.returnListNoDuplicates(l_return)
                mc.select(l_return)
                
            if kws.get('asMeta'):
                l_return = cgmMeta.validateObjListArg(l_return,cgmMeta.cgmObject)
            return l_return
    return fncWrap(*args,**kws).go()

def get_mirror(*args,**kws):
    class fncWrap(ModuleFunc):
        def __init__(self,*args,**kws):
            """
            """	
            super(fncWrap, self).__init__(*args,**kws)
            self._str_funcName = "get_mirror({0})".format(self._str_moduleName)
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
            if mi_module.getMayaAttr('cgmDirection') not in l_direction:
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
            self._str_funcName= "animReset({0})".format(self._str_moduleName)	
            self._l_ARGS_KWS_DEFAULTS =  [_d_KWARG_mModule,
                                          {'kw':'transformsOnly',"default":True,'help':"Whether to only reset transforms","argType":"bool"}]			    
            self.__dataBind__(*args,**kws)	    	    
        def __func__(self):
            try:#Query ========================================================
                mi_module = self._mi_module
                kws = self.d_kws		
                _result = False
            except Exception,error:raise StandardError,"[Query]{%s}"%error
            mi_module.rigNull.moduleSet.select()
            if mc.ls(sl=True):
                ml_resetChannels.main(transformsOnly = kws['transformsOnly'])
                _result = True
            if self._l_callSelection:mc.select(self._l_callSelection)                        
            return _result	    
    return fncWrap(*args,**kws).go()

def mirrorPush(*args,**kws):
    class fncWrap(ModuleFunc):
        def __init__(self,*args,**kws):
            """
            """	
            super(fncWrap, self).__init__(*args,**kws)
            self._str_funcName = "mirrorPush({0})".format(self._str_moduleName)
            self._l_ARGS_KWS_DEFAULTS =  [_d_KWARG_mModule]
            self.l_funcSteps = [{'step':'Process','call':self.__func__}]	    
            self.__dataBind__(*args,**kws)
            #=================================================================
        def __func__(self): 
            try:#Query ========================================================
                mi_module = self._mi_module
                kws = self.d_kws	
                _result = False
            except Exception,error:raise StandardError,"[Query]{%s}"%error
            l_buffer = mi_module.rigNull.moduleSet.getList()
            mi_mirror = get_mirror(**kws)
            if mi_mirror:
                l_buffer.extend(mi_mirror.rigNull.moduleSet.getList())
            else:raise StandardError, "Module doesn't have mirror"

            if l_buffer:
                r9Anim.MirrorHierarchy().makeSymmetrical(l_buffer,mode = '',primeAxis = mi_module.cgmDirection.capitalize() )
                mc.select(l_buffer)
                _result = True
            if self._l_callSelection:mc.select(self._l_callSelection)                        
            return _result	 

    return fncWrap(*args,**kws).go()   

def mirrorPull(*args,**kws):
    class fncWrap(ModuleFunc):
        def __init__(self,*args,**kws):
            """
            """	
            super(fncWrap, self).__init__(*args,**kws)
            self._str_funcName = "mirrorPull({0})".format(self._str_moduleName)
            self._l_ARGS_KWS_DEFAULTS =  [_d_KWARG_mModule]
            self.__dataBind__(*args,**kws)

        def __func__(self): 
            try:#Query ========================================================
                mi_module = self._mi_module
                kws = self.d_kws
                _result = False
            except Exception,error:raise StandardError,"[Query]{%s}"%error

            l_buffer = mi_module.rigNull.moduleSet.getList()
            mi_mirror = get_mirror(**kws)
            if mi_mirror:
                l_buffer.extend(mi_mirror.rigNull.moduleSet.getList())
            else:raise StandardError, "Module doesn't have mirror"

            if l_buffer:
                r9Anim.MirrorHierarchy().makeSymmetrical(l_buffer,mode = '',primeAxis = mi_mirror.cgmDirection.capitalize() )
                mc.select(l_buffer)
                _result = True
            if self._l_callSelection:mc.select(self._l_callSelection)                        
            return _result	 
    return fncWrap(*args,**kws).go()

def mirrorMe(*args,**kws):
    class fncWrap(ModuleFunc):
        def __init__(self,*args,**kws):
            """
            """	
            super(fncWrap, self).__init__(*args,**kws)
            self._str_funcName = "mirrorMe({0})".format(self._str_moduleName)
            self.__dataBind__(*args,**kws)
        def __func__(self): 
            try:#Query ========================================================
                mi_module = self._mi_module
                kws = self.d_kws	
                _result = False
            except Exception,error:raise StandardError,"[Query]{%s}"%error

            l_buffer = mi_module.rigNull.moduleSet.getList()
            try:mi_mirror = get_mirror(**kws)
            except Exception,error:raise StandardError,"get_mirror | %s"%error
            if mi_mirror:
                l_buffer.extend(mi_mirror.rigNull.moduleSet.getList())
            if l_buffer:
                r9Anim.MirrorHierarchy().mirrorData(l_buffer,mode = '')
                mc.select(l_buffer)
                _result = True
            if self._l_callSelection:mc.select(self._l_callSelection)                        
            return _result

    return fncWrap(*args,**kws).go()

def mirrorSymLeft(*args,**kws):
    class fncWrap(ModuleFunc):
        def __init__(self,*args,**kws):
            """
            """	
            super(fncWrap, self).__init__(*args,**kws)
            self._str_funcName = "mirrorSymLeft({0})".format(self._str_moduleName)
            self.__dataBind__(*args,**kws)
            #=================================================================
        def __func__(self): 
            try:#Query ========================================================
                mi_module = self._mi_module
                kws = self.d_kws	
                _result = False
            except Exception,error:raise StandardError,"[Query]{%s}"%error

            l_buffer = mi_module.rigNull.moduleSet.getList()
            try:mi_mirror = get_mirror(**kws)
            except Exception,error:raise StandardError,"get_mirror | %s"%error
            if mi_mirror:
                l_buffer.extend(mi_mirror.rigNull.moduleSet.getList())    
            if l_buffer:
                r9Anim.MirrorHierarchy().makeSymmetrical(l_buffer,mode = '',primeAxis = "Left" )
                mc.select(l_buffer)
                _result = True
            if self._l_callSelection:mc.select(self._l_callSelection)                        
            return _result	 
    return fncWrap(*args,**kws).go() 

def mirrorSymRight(*args,**kws):
    class fncWrap(ModuleFunc):
        def __init__(self,*args,**kws):
            """
            """	
            super(fncWrap, self).__init__(*args,**kws)
            self._str_funcName = "mirrorSymRight({0})".format(self._str_moduleName)
            self.__dataBind__(*args,**kws)
            #=================================================================
        def __func__(self): 
            try:#Query ========================================================
                mi_module = self._mi_module
                kws = self.d_kws	
                _result = False
            except Exception,error:raise StandardError,"[Query]{%s}"%error

            l_buffer = mi_module.rigNull.moduleSet.getList()
            try:mi_mirror = get_mirror(**kws)
            except Exception,error:raise StandardError,"get_mirror | %s"%error
            if mi_mirror:
                l_buffer.extend(mi_mirror.rigNull.moduleSet.getList())    	    
            if l_buffer:
                r9Anim.MirrorHierarchy().makeSymmetrical(l_buffer,mode = '',primeAxis = "Right" )
                mc.select(l_buffer)
                _result = True
            if self._l_callSelection:mc.select(self._l_callSelection)                        
            return _result 
    return fncWrap(*args,**kws).go() 


def mirror_do(*args,**kws):
    '''
    Factory Rewrite of mirror functions.
    TODO -- replace the many mirror functions here
    '''
    class fncWrap(ModuleFunc):
        def __init__(self,*args,**kws):
            """
            """	
            super(fncWrap, self).__init__(*args,**kws)
            #self._b_reportTimes = True
            self._l_ARGS_KWS_DEFAULTS = [_d_KWARG_mModule,
                                         {'kw':'mode',"default":'anim','help':"Special mode for this fuction","argType":"string"},
                                         {'kw':'mirrorMode',"default":'symLeft','help':"Special mode for this fuction","argType":"string"}] 
            self.__dataBind__(*args,**kws)
            self._str_funcName = "module.get_controls('{0}',mode = {1})".format(self._str_moduleName,self.d_kws.get('mode') or None)		    	    
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

        def _fncStep_process_(self):
            """
            """
            try:
                mi_module = self._mi_module
                mi_templateNull = mi_module.templateNull  
                _result = False
            except Exception,error: raise Exception,"Link meta fail | error: {0}".format(error)

            try:
                ml_controls = get_controls(mi_module,mode = self.d_kws['mode'])
                if not ml_controls:
                    raise StandardError,"No controls found"

                try:mi_mirror = get_mirror(mi_module)
                except Exception,error:raise StandardError,"get_mirror | %s"%error	

                if mi_mirror:
                    ml_controls.extend(get_controls(mi_mirror,mode = self.d_kws['mode']))
            except Exception,error: raise Exception,"Gather controls | error: {0}".format(error)		

            try:
                mi_module = self._mi_module
                mi_templateNull = mi_module.templateNull   
            except Exception,error: raise Exception,"Mirror fail | error: {0}".format(error)

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
                _result = True
            if self._l_callSelection:mc.select(self._l_callSelection)                        
            return _result	    

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
            self._str_funcName = "mirrorMe_siblings({0})".format(self._str_moduleName)
            self._str_funcHelp = "Basic mirror me function"
            self._l_ARGS_KWS_DEFAULTS =  [_d_KWARG_mModule,
                                          _d_KWARG_excludeSelf]
            self.__dataBind__(*args,**kws)

        def __func__(self): 
            try:#Query ========================================================
                mi_module = self._mi_module
                kws = self.d_kws
                _result = False
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
                r9Anim.MirrorHierarchy().mirrorData(l_controls,mode = '')		    
                mc.select(l_controls) 
                _result = True
            if self._l_callSelection:mc.select(self._l_callSelection)                        
            return _result
    return fncWrap(*args,**kws).go()

def animReset_siblings(*args,**kws):
    class fncWrap(ModuleFunc):
        def __init__(self,*args,**kws):
            """
            """	
            super(fncWrap, self).__init__(*args,**kws)
            self._str_funcName = "animReset_siblings({0})".format(self._str_moduleName)
            self._l_ARGS_KWS_DEFAULTS = [_d_KWARG_mModule,
                                         {'kw':'transformsOnly',"default":True,'help':"Whether to only reset transforms","argType":"bool"},
                                         _d_KWARG_excludeSelf]
            self.__dataBind__(*args,**kws)    	    

        def __func__(self): 
            try:#Query ========================================================
                mi_module = self._mi_module
                kws = self.d_kws
                _result = False
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
                _result = True
            if self._l_callSelection:mc.select(self._l_callSelection)                        
            return _result

    #We wrap it so that it autoruns and returns
    return fncWrap(*args,**kws).go()

def animReset_children(*args,**kws):
    class fncWrap(ModuleFunc):
        def __init__(self,*args,**kws):
            """
            """	
            super(fncWrap, self).__init__(*args,**kws)
            self._str_funcName = "animReset_children({0})".format(self._str_moduleName)
            self._l_ARGS_KWS_DEFAULTS = [_d_KWARG_mModule,
                                         {'kw':'transformsOnly',"default":True,'help':"Whether to only reset transforms","argType":"bool"},
                                         {'kw':'excludeSelf',"default":True,'help':"Whether to exclude self in return","argType":"bool"}]
            self.__dataBind__(*args,**kws)    	    

        def __func__(self): 
            try:#Query ========================================================
                mi_module = self._mi_module
                kws = self.d_kws
                _result = False
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
                _result = True
            if self._l_callSelection:mc.select(self._l_callSelection)                        
            return _result

    #We wrap it so that it autoruns and returns
    return fncWrap(*args,**kws).go()

def mirrorPush_siblings(*args,**kws):
    class fncWrap(ModuleFunc):
        def __init__(self,*args,**kws):
            """
            """	
            super(fncWrap, self).__init__(*args,**kws)
            self._str_funcName = "mirrorPush_siblings({0})".format(self._str_moduleName)
            self._l_ARGS_KWS_DEFAULTS = [_d_KWARG_mModule,
                                         {'kw':'excludeSelf',"default":True,'help':"Whether to exclude self in return","argType":"bool"}]

            self.__dataBind__(*args,**kws)    	    

        def __func__(self): 
            try:#Query ========================================================
                mi_module = self._mi_module
                kws = self.d_kws
                _result = False
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
                    kws['mModule'] = mModule
                    mirrorPush(**kws)		    
                except Exception,error:
                    self.log_error("child: %s | %s"%(_str_module,error))

            if l_controls:
                mc.select(l_controls)
                _result = True
            if self._l_callSelection:mc.select(self._l_callSelection)                        
            return _result

    #We wrap it so that it autoruns and returns
    return fncWrap(*args,**kws).go()

def mirrorPull_siblings(*args,**kws):
    class fncWrap(ModuleFunc):
        def __init__(self,*args,**kws):
            """
            """	
            super(fncWrap, self).__init__(*args,**kws)
            self._str_funcName = "mirrorPull_siblings({0})".format(self._str_moduleName)
            self._l_ARGS_KWS_DEFAULTS = [_d_KWARG_mModule,
                                         {'kw':'excludeSelf',"default":True,'help':"Whether to exclude self in return","argType":"bool"}]

            self.__dataBind__(*args,**kws)    	    

        def __func__(self): 
            try:#Query ========================================================
                mi_module = self._mi_module
                kws = self.d_kws
                ml_buffer = get_moduleSiblings(**kws)
                _result = False
                int_lenMax = len(ml_buffer)		
            except Exception,error:raise StandardError,"[Query]{%s}"%error	    

            l_controls = []
            for i,mModule in enumerate(ml_buffer):
                _str_module = mModule.p_nameShort
                self.progressBar_set(status = "On: %s "%_str_module, progress = i, maxValue = int_lenMax)		    				    		    
                try:
                    l_controls.extend(mModule.rigNull.moduleSet.getList())
                    kws = self.get_cleanKWS()#We use this to get non registered kws -- maya one's more than like
                    kws['mModule'] = mModule
                    mirrorPull(**kws)		    
                except Exception,error:
                    self.log_error("child: %s | %s"%(_str_module,error))

            if l_controls:
                mc.select(l_controls)
                _result = True
            if self._l_callSelection:mc.select(self._l_callSelection)                        
            return _result

    #We wrap it so that it autoruns and returns
    return fncWrap(*args,**kws).go()


def get_moduleSiblings(*args,**kws):
    l_sibblingIgnoreCheck = ['finger','thumb']
    class fncWrap(ModuleFunc):
        def __init__(self,*args,**kws):
            """
            """	
            super(fncWrap, self).__init__(*args,**kws)
            self._str_funcName = "get_moduleSiblings({0})".format(self._str_moduleName)
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
                    if mi_module.getMayaAttr('cgmDirection') != mModule.getMayaAttr('cgmDirection') or mi_module.moduleType in l_sibblingIgnoreCheck:
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
            self._str_funcName = "get_allModuleChildren({0})".format(self._str_moduleName)
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
            self._str_funcName= "animKey_children({0})".format(self._str_moduleName)
            self._str_funcHelp = "    Key module and all module children controls"			    
            self.__dataBind__(*args,**kws)	
            self._l_ARGS_KWS_DEFAULTS = [_d_KWARG_mModule,_d_KWARG_excludeSelf]

        def __func__(self): 
            try:#Query ========================================================
                mi_module = self._mi_module
                kws = self._d_funcKWs
            except Exception,error:raise StandardError,"[Query]{%s}"%error
            _result = False
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
                _result = True
                
            if self._l_callSelection:mc.select(self._l_callSelection)            
            return _result
    return fncWrap(*args,**kws).go()

def animKey_siblings(*args,**kws):
    class fncWrap(ModuleFunc):
        def __init__(self,*args,**kws):
            """
            """
            super(fncWrap, self).__init__(*args, **kws)
            self._str_funcName= "animSelect_children({0})".format(self._str_moduleName)
            self._str_funcHelp = "Selects controls of a module's children"			    
            self.__dataBind__(*args,**kws)	
            self._l_ARGS_KWS_DEFAULTS = [_d_KWARG_mModule,_d_KWARG_excludeSelf]

        def __func__(self): 
            try:#Query ========================================================
                mi_module = self._mi_module
                kws = self._d_funcKWs
                self.log_info(kws)
            except Exception,error:raise StandardError,"[Query]{%s}"%error
            _result = False
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
                _result = True
            if self._l_callSelection:mc.select(self._l_callSelection)            
            return _result
    return fncWrap(*args,**kws).go()

def animSelect_children(*args,**kws):
    class fncWrap(ModuleFunc):
        def __init__(self,*args,**kws):
            """
            """
            super(fncWrap, self).__init__(*args, **kws)
            self._str_funcName= "animSelect_children({0})".format(self._str_moduleName)
            self._str_funcHelp = "Selects controls of a module's children"			    
            self._l_ARGS_KWS_DEFAULTS = [_d_KWARG_mModule,_d_KWARG_excludeSelf]
            self.__dataBind__(*args,**kws)	    
            #=================================================================

        def __func__(self):
            try:#Query ========================================================
                mi_module = self._mi_module
                kws = self.d_kws		
            except Exception,error:raise StandardError,"[Query]{%s}"%error
            
            l_controls = mi_module.rigNull.msgList_get('controlsAll',asMeta = False) or []
            ml_children = get_allModuleChildren(**kws)
            int_lenMax = len(ml_children)
            for i,i_c in enumerate(ml_children):
                self.progressBar_set(status = "Remaining to process... ", progress = i, maxValue = int_lenMax)		    				    		    
                buffer = i_c.rigNull.msgList_get('controlsAll',asMeta = False)
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
            self._str_funcName= "animSelect_siblings({0})".format(self._str_moduleName)
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
            self._str_funcName = "animPushPose_siblings({0})".format(self._str_moduleName)
            #self._l_ARGS_KWS_DEFAULTS = [_d_KWARG_mModule]	    
            self.__dataBind__(*args,**kws)

        def __func__(self): 
            try:#Query ========================================================
                mi_module = self._mi_module
                kws = self.d_kws	
            except Exception,error:raise StandardError,"[Query]{%s}"%error

            ml_buffer = get_moduleSiblings(**kws)
            l_moduleControls = self._mi_module.rigNull.msgList_get('controlsAll',asMeta = False)
            int_lenMax = len(ml_buffer)		
            l_controls = []
            for i,i_c in enumerate(ml_buffer):
                try:		    
                    _str_child = i_c.p_nameShort
                    self.progressBar_set(status = "%s >> step:'%s' "%(self._str_reportStart,_str_child), progress = i, maxValue = int_lenMax)		    				    		    			
                    l_siblingControls = i_c.rigNull.msgList_get('controlsAll',asMeta = False)
                    for i,c in enumerate(l_siblingControls):
                        #log.info("%s %s >> %s"%(self._str_reportStart,l_moduleControls[i],c))
                        r9Anim.AnimFunctions().copyAttributes(nodes=[l_moduleControls[i],c])
                    l_controls.extend(l_siblingControls)
                except Exception,error:
                    log.error("%s  child: %s | %s"%(self._str_reportStart,_str_child,error))	    
            if l_controls:
                mc.select(l_controls)
            if self._l_callSelection:mc.select(self._l_callSelection)            
            return True  
    return fncWrap(*args,**kws).go()


#Dyn Switch =====================================================================================================
def dynSwitch_children(*args,**kws):
    class fncWrap(ModuleFunc):
        def __init__(self,*args,**kws):
            """
            """
            super(fncWrap, self).__init__(*args, **kws)
            self._str_funcName= "dynSwitch_children({0})".format(self._str_moduleName)
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
                if self._l_callSelection:mc.select(self._l_callSelection)                            
                return True
            except Exception,error:
                self.log_error(error)  
                if self._l_callSelection:mc.select(self._l_callSelection)                            
                return False	    
    return fncWrap(*args,**kws).go()

def dynSwitch_siblings(*args,**kws):
    class fncWrap(ModuleFunc):
        def __init__(self,*args,**kws):
            """
            """
            super(fncWrap, self).__init__(*args, **kws)
            self._str_funcName= "dynSwitch_siblings({0})".format(self._str_moduleName)
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
                if self._l_callSelection:mc.select(self._l_callSelection)                        
                return True
            except Exception,error:
                self.log_error(error)
                if self._l_callSelection:mc.select(self._l_callSelection)                            
                return False	    
    return fncWrap(*args,**kws).go()

def get_mirrorSideAsString(*args,**kws):
    class fncWrap(ModuleFunc):
        def __init__(self,*args,**kws):
            """
            """
            super(fncWrap, self).__init__(*args, **kws)
            self._str_funcName= "get_mirrorSideAsString({0})".format(self._str_moduleName)
            self._str_funcHelp = "Returns the mirror side as a string"
            self.__dataBind__(*args,**kws)	    
            #=================================================================

        def __func__(self):
            try:#Query ========================================================
                mi_module = self._mi_module
                kws = self.d_kws		
            except Exception,error:raise StandardError,"[Query]{%s}"%error
            _str_direction = mi_module.getMayaAttr('cgmDirection') 
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
            self._str_funcName = "toggle_subVis({0})".format(self._str_moduleName)
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
            self._str_funcName = "animReset_siblings({0})".format(self._str_moduleName)
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
            if self._l_callSelection:mc.select(self._l_callSelection)                                
            return False
    #We wrap it so that it autoruns and returns
    return fncWrap(*args,**kws).go()
